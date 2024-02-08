# flake8: noqa=W293
# pylint: disable=line-too-long,missing-class-docstring,missing-function-docstring,consider-using-f-string,too-many-locals,invalid-name

"""
Test script for opening a youtube channel and getting the latest videos.
"""

import json
import os
import time
import traceback
import warnings
from dataclasses import dataclass

from bs4 import BeautifulSoup  # type: ignore
from open_webdriver import open_webdriver  # type: ignore

# from be

IS_GITHUB_RUNNER = os.environ.get("GITHUB_ACTIONS") == "true"
HEADLESS = IS_GITHUB_RUNNER

URL = "https://www.youtube.com/@silverguru/videos"

JS_SCROLL_TO_BOTTOM = (
    "window.scrollTo(0, document.documentElement.scrollHeight);"
)
JS_SCROLL_TO_BOTTOM_WAIT = 1
URL_BASE = "https://www.youtube.com"


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
        data = {"url": self.url, "title": self.title}
        return json.dumps(data)


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


def fetch_all_sources(yt_channel_url: str, limit: int = -1) -> list[str]:
    max_index = limit if limit > 0 else 1000
    sources: list[str] = []
    with open_webdriver(headless=HEADLESS) as driver:

        def get_contents() -> list[str]:
            out: list[str] = []
            vids = driver.find_elements_by_tag_name("ytd-rich-item-renderer")
            for vid in vids:
                content = vid.get_attribute("outerHTML")
                out.append(content)
            return out

        # All Chromium / web driver dependencies are now installed.
        driver.get(yt_channel_url)
        time.sleep(JS_SCROLL_TO_BOTTOM_WAIT)
        contents = get_contents()
        sources.extend(contents)
        last_scroll_height = 0
        for index in range(max_index):
            driver.execute_script(JS_SCROLL_TO_BOTTOM)
            time.sleep(JS_SCROLL_TO_BOTTOM_WAIT)
            contents = get_contents()
            sources.extend(contents)
            scroll_height = driver.execute_script(
                "return document.documentElement.scrollHeight"
            )
            print(f"scroll_height: {scroll_height}")
            scroll_diff = abs(scroll_height - last_scroll_height)
            if scroll_diff < 100:
                break
            last_scroll_height = scroll_height
        if index == max_index - 1 and limit <= 0:
            warnings.warn("Reached max scroll limit.")
    return sources


def fetch_all_vids(yt_channel_url: str) -> list[YtVid]:
    """Open a web driver and navigate to Google. yt_channel_url should be of the form https://www.youtube.com/@silverguru/videos"""
    sources: list[str] = fetch_all_sources(yt_channel_url)
    # vidlist = YtVid.reduce(parse_youtube_videos(sources))
    allvids = parse_youtube_videos(sources)
    unique_vids: list[YtVid] = []
    for vid in allvids:  # keep unique vids in order
        if vid not in unique_vids:
            unique_vids.append(vid)
    return unique_vids


def main() -> int:
    vidlist = fetch_all_vids(URL)
    print(f"Found {len(vidlist)} videos.")
    for vid in vidlist:
        print(f"  {vid.url}")
    return 0


if __name__ == "__main__":
    main()
