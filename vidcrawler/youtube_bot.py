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

    # class static
    @staticmethod
    def merge(vids: list[list["YtVid"]]) -> list["YtVid"]:
        """Merge lists of videos."""
        # Flatten the list of lists
        flattened_vids = [vid for sublist in vids for vid in sublist]
        # Convert the flattened list into a set to remove duplicates, then back to a list
        out = list(set(flattened_vids))
        return out


def parse_youtube_videos(content: str) -> list[YtVid]:
    out: list[YtVid] = []
    soup = BeautifulSoup(content, "html.parser")
    # search for div with id="contents"
    try:
        div = soup.find(id="contents")
        vid_rows = div.find_all("ytd-rich-grid-row", recursive=False)
        vid_divs: list = []
        for row in vid_rows:
            # vids = parse_youtube_videos_from_row(row)
            # "ytd-rich-item-renderer"
            vids = row.find_all("ytd-rich-item-renderer")
            vid_divs.extend(vids)
            # out.extend(vids)
    #  vid_divs = div.find_all("ytd-rich-item-renderer")
    except Exception as err:  # pylint: disable=broad-except
        stack_trace = traceback.format_exc()
        warnings.warn(f"Error could not scrape channel: {err} {stack_trace}")
        return
    # find each element "ytd-rich-item-renderer"
    for item in vid_divs:
        # print(item)
        # find #video-title-link
        title_link = item.find("a", id="video-title-link")
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
            content_div = driver.find_element_by_id("contents")
            content = content_div.get_attribute("outerHTML")
            return [content]

        # All Chromium / web driver dependencies are now installed.
        driver.get(yt_channel_url)
        time.sleep(JS_SCROLL_TO_BOTTOM_WAIT)
        # driver.find_element_by_id("search").send_keys("seleniumhq" + Keys.RETURN)
        # assert "No results found." not in driver.page_source
        contents = get_contents()
        # content = driver.page_source
        sources.extend(contents)
        last_scroll_height = 0
        for index in range(max_index):
            driver.execute_script(JS_SCROLL_TO_BOTTOM)
            # driver.implicitly_wait(JS_SCROLL_TO_BOTTOM_WAIT)
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
    vidlist = YtVid.merge([parse_youtube_videos(source) for source in sources])
    return vidlist


def main() -> int:
    vidlist = fetch_all_vids(URL)
    print(f"Found {len(vidlist)} videos.")
    for vid in vidlist:
        print(f"  {vid.url}")
    return 0


if __name__ == "__main__":
    main()
