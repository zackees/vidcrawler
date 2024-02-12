# flake8: noqa=W293
# pylint: disable=line-too-long,missing-class-docstring,missing-function-docstring,consider-using-f-string,too-many-locals,invalid-name

"""
Test script for opening a youtube channel and getting the latest videos.
"""

import concurrent.futures
import json
import os
import time
import traceback
import unicodedata
import warnings
from dataclasses import dataclass
from typing import Any, Callable, Generator

import requests
from bs4 import BeautifulSoup  # type: ignore
from open_webdriver import open_webdriver  # type: ignore
from selenium.common.exceptions import (
    StaleElementReferenceException as StaleElementException,
)

IS_GITHUB_RUNNER = os.environ.get("GITHUB_ACTIONS") == "true"
# Always headless now.
HEADLESS = IS_GITHUB_RUNNER or True

URL = "https://www.youtube.com/@silverguru/videos"

JS_SCROLL_TO_BOTTOM = "window.scrollTo(0, document.documentElement.scrollHeight);"
JS_SCROLL_TO_BOTTOM_WAIT = 1
URL_BASE = "https://www.youtube.com"

CACHE_OUTER_HTML: dict[str, str] = {}


@dataclass
class YtVid:
    url: str
    title: str

    # needed for set membership
    def __hash__(self):
        return hash(self.url)

    def __eq__(self, other):
        return self.url == other.url

    def __repr__(self) -> str:
        data = self.to_dict()
        return json.dumps(data)

    def to_dict(self) -> dict:
        return {"url": self.url, "title": self.title}


def sanitize_filepath(path: str, replacement_char: str = "_") -> str:
    """
    Sanitize a file path to make it safe for use in file systems.

    :param path: The file path to be sanitized.
    :param replacement_char: The character to use for replacing invalid characters.
    :return: A sanitized version of the file path.
    """
    # Normalize unicode characters
    path = unicodedata.normalize("NFKD", path).encode("ascii", "ignore").decode("ascii")

    # Replace invalid file path characters
    invalid_chars = r'<>:"/\\|?*'
    for char in invalid_chars:
        path = path.replace(char, replacement_char)

    # Replace leading/trailing periods and spaces
    path = path.strip(". ")

    # Avoid reserved names in Windows like CON, PRN, AUX, NUL, etc.
    reserved_names = ["CON", "PRN", "AUX", "NUL"] + [f"{name}{i}" for name in ["COM", "LPT"] for i in range(1, 10)]
    basename = path.split("/")[-1]
    if basename.upper() in reserved_names:
        path = path.replace(basename, replacement_char + basename)

    # Truncate long paths
    max_length = 255
    if len(path) > max_length:
        extension = "." + path.split(".")[-1] if "." in path else ""
        path = path[: max_length - len(extension)] + extension
    path = path.replace("'", "_")

    return path


def parse_youtube_videos(div_strs: list[str]) -> list[YtVid]:
    """Div containing the youtube video, which has a title and an href."""
    out: list[YtVid] = []
    for div_str in div_strs:
        soup = BeautifulSoup(div_str, "html.parser")
        title_link = soup.find("a", id="video-title-link")
        try:
            title = title_link.get("title")
            href = title_link.get("href")
            assert title is not None
            assert href is not None
            assert href.startswith("/")
            href = URL_BASE + href
            title = sanitize_filepath(title.strip())
        except KeyboardInterrupt:
            return out
        except SystemExit:
            return out
        except Exception as err:  # pylint: disable=broad-except
            stack_trace = traceback.format_exc()
            warnings.warn(f"Error, could not scrape video: {err} {stack_trace}")
            continue
        out.append(YtVid(title=title, url=href))
    return out


def fetch_source_cached(unique_id: str, value_cb: Callable[[], str]) -> str:
    if unique_id in CACHE_OUTER_HTML:
        return CACHE_OUTER_HTML[unique_id]
    value = value_cb()
    CACHE_OUTER_HTML[unique_id] = value
    return value


def fetch_all_sources(yt_channel_url: str, limit: int = -1) -> Generator[str, None, None]:
    max_index = limit if limit > 0 else 1000
    with open_webdriver(headless=HEADLESS) as driver:

        def get_vid_attribute(vid: Any) -> str:
            try:
                try:
                    unique_id = getattr(vid, "id")
                    html = fetch_source_cached(unique_id, lambda: str(vid.get_attribute("outerHTML")))
                    return html
                except AttributeError:
                    pass
                return str(vid.get_attribute("outerHTML"))
            except StaleElementException:
                warnings.warn("skipping stale element")
                return ""

        def get_contents() -> list[str]:
            vids = driver.find_elements_by_tag_name("ytd-rich-item-renderer")
            with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
                futures: list = []
                for vid in vids:
                    future = executor.submit(get_vid_attribute, vid)
                    futures.append(future.result)
                out = [future() for future in futures]
                # filter out empty strings
                out = [x for x in out if x]
            return out

        # All Chromium / web driver dependencies are now installed.
        driver.get(yt_channel_url)
        time.sleep(JS_SCROLL_TO_BOTTOM_WAIT)
        for item in get_contents():
            yield item
        last_scroll_height = 0
        for index in range(max_index + 1):
            driver.execute_script(JS_SCROLL_TO_BOTTOM)
            time.sleep(JS_SCROLL_TO_BOTTOM_WAIT)
            # yield get_contents()
            for item in get_contents():
                yield item
            scroll_height = driver.execute_script("return document.documentElement.scrollHeight")
            print(f"#### {index}: scrolling for new content ####")
            scroll_diff = abs(scroll_height - last_scroll_height)
            if scroll_diff < 100:
                break
            last_scroll_height = scroll_height
        if index == max_index and limit <= 0:
            warnings.warn("Reached max scroll limit.")


def test_channel_url(channel_url: str) -> bool:
    """Test if the channel url is valid."""
    response = requests.get(channel_url, timeout=10)
    return response.status_code == 200


def fetch_all_vids(yt_channel_url: str, limit: int = -1) -> list[YtVid]:
    """
    Open a web driver and navigate to Google. yt_channel_url should be
    of the form https://www.youtube.com/@silverguru/videos
    """
    if not test_channel_url(yt_channel_url):
        raise ValueError(f"Invalid channel url: {yt_channel_url}")
    pending_fetches = fetch_all_sources(yt_channel_url=yt_channel_url, limit=limit)
    list_vids: list[list[YtVid]] = []
    num_workers = max(1, os.cpu_count() or 0)
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        future_to_vid = {}
        for sources in pending_fetches:
            future = executor.submit(parse_youtube_videos, [sources])
            future_to_vid[future] = sources
        for future in concurrent.futures.as_completed(future_to_vid):
            vids = future.result()
            list_vids.append(vids)
    unique_vids: set[YtVid] = set()
    out_vids: list[YtVid] = []
    for vids in list_vids:
        for vid in vids:
            if vid not in unique_vids:
                unique_vids.add(vid)
                out_vids.append(vid)
    return out_vids


def main() -> int:
    vidlist = fetch_all_vids(URL, limit=1)
    print(f"Found {len(vidlist)} videos.")
    for vid in vidlist:
        print(f"  {vid.url}")
    return 0


if __name__ == "__main__":
    main()
