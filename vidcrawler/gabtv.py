"""
    Scraper for gabtv.com
"""

# pylint: disable=line-too-long,missing-function-docstring,consider-using-f-string,too-many-locals,invalid-name,no-else-return,redefined-builtin,W0511

import json
import re
import subprocess
import sys
from typing import Dict, List

from bs4 import BeautifulSoup  # type: ignore

from .date import iso_fmt, now_local
from .error import log_error
from .video_info import VideoInfo

_PATTERN_DATA_EPISODE_ID = re.compile('data-episode-id="([^"]*)"')


def _fetch_html_using_curl(url: str) -> str:
    out: bytes = subprocess.check_output(
        "curl --max-time 10 -s -X GET " + url, shell=True
    )
    return out.decode("utf-8")


def fetch_views(channel: str) -> Dict[str, str]:
    out: Dict[str, str] = {}
    html_url: str = f"https://tv.gab.com/channel/{channel}"
    html_doc: str = _fetch_html_using_curl(html_url)
    soup = BeautifulSoup(html_doc, "html.parser")
    top_dom = soup.find("div", {"class": "tv-channel-episode-list"})
    dom_episodes = top_dom.findAll("div")
    for i, dom_episode in enumerate(dom_episodes):
        str_episode = str(dom_episode)
        if "data-episode-id" not in str_episode:
            continue
        try:
            id = _PATTERN_DATA_EPISODE_ID.findall(str_episode)[0]
        except IndexError as e:
            raise IndexError(f"idx: {i}, url: {html_url}") from e
        dom_published = dom_episode.find("div", {"class": "studio-episode-published"})
        dom_spans = dom_published.findAll("span")
        views = dom_spans[0].text
        out[id] = views
    return out


def fetch_gabtv_today(channel_name: str, channel_id: str) -> List[VideoInfo]:
    now_datestr = iso_fmt(now_local())
    # GabTV does not PUBLISH VIEWS IN IT'S FEED, so scrape them from the html
    # here.
    out: List[VideoInfo] = []
    view_data = fetch_views(channel_id)
    channel_url = f"https://tv.gab.com/channel/{channel_id}"
    json_feed_url: str = f"https://tv.gab.com/channel/{channel_id}/feed/json"
    # Note: Gab.TV currently returns 403 when using the request lib. The
    # work-around (for now) is to use the curl alternative. Gab should be
    # notified of this limitation and if possible, we should go back to using
    # the request lib to fetch this data.
    json_str = _fetch_html_using_curl(json_feed_url)
    data = json.loads(json_str)
    for item in data["items"]:
        try:
            url: str = item["url"]
            id: str = item["id"]
            title: str = item["title"]
            # Summary is sometimes empty.
            summary: str = item.get("summary", "")
            image: str = item["image"]
            published_date: str = item["date_modified"]
        except KeyError as ke:
            log_error(err_str=f"Error while parsing {channel_id} because of {ke}\n")
            continue

        # GabTV does not PUBLISH VIEWS IN IT'S FEED.
        # print(url)
        views = view_data.get(id)
        if views is None:
            sys.stderr.write(f"{__file__}: Warning, views for {url} is None\n")
            views = "?"
        vi = VideoInfo(
            channel_name=channel_name,
            title=title,
            date_published=published_date,
            date_discovered=now_datestr,
            date_lastupdated=now_datestr,
            channel_url=channel_url,
            source="tv.gab.com",
            url=url,
            duration="?",  # TODO: get this
            description=summary,
            img_src=image,
            iframe_src="",  # No iframe source yet
            views=views,
            profile_img_src="",
        )
        out.append(vi)
    return out


def test() -> None:
    from pprint import pprint  # pylint: disable=import-outside-toplevel

    channel_id: str = input("Enter Channel ID: ")
    channel_name: str = input("Enter Channel Name: ")
    vids: List[VideoInfo] = fetch_gabtv_today(
        channel_name=channel_name, channel_id=channel_id
    )
    print("First two videos:")
    vids = vids[0:2]
    for v in vids:
        pprint(v.to_dict())


if __name__ == "__main__":
    test()
