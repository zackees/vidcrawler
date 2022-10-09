"""
Scraper for spreaker.com
"""

# pylint: disable=line-too-long,missing-function-docstring,consider-using-f-string,too-many-locals,invalid-name,no-else-return,R0801

import sys
from typing import List

import feedparser  # type: ignore

from vidcrawler.date import iso_fmt, now_local

from .fetch_html import fetch_html_using_request_lib as fetch_html
from .video_info import VideoInfo

# EXPERIMENTAL - parses sara carter from spreaker.


def rss_element_to_video_info(
    channel_name: str, rss_element: dict
) -> VideoInfo:
    thumbnail_img = rss_element["image"]["href"]
    link = rss_element["link"]
    published = rss_element["published"]
    title = rss_element["title"]
    description = rss_element.get("subtitle") or rss_element.get("summary", "")
    # summary = entry['summary']
    duration = rss_element["itunes_duration"]
    now_str = iso_fmt(now_local())
    o = VideoInfo(
        channel_name=channel_name,
        title=title,
        date_published=published,
        date_discovered=now_str,
        date_lastupdated=now_str,
        source="spreaker.com",
        url=link,
        duration=duration,
        description=f"{description}",
        img_src=thumbnail_img,
        iframe_src="",
        views="?",
        profile_img_src=thumbnail_img,
    )
    return o


def fetch_spreaker_today(channel_name: str, channel: str) -> List[VideoInfo]:
    url = f"https://www.spreaker.com/show/{channel}/episodes/feed"
    sys.stdout.write("Spreaker visiting %s (%s)\n" % (channel, url))
    content = fetch_html(url)
    feed = feedparser.parse(content)
    output: List[VideoInfo] = []
    for entry in feed.entries:
        try:
            vid = rss_element_to_video_info(
                channel_name=channel_name, rss_element=entry
            )
            output.append(vid)
        except BaseException as err:  # pylint: disable=broad-except
            sys.stderr.write(
                f"{__file__}: Error while parsing {channel_name} entry:\n {str(entry['title'])}:\n because of {err}"
            )
    return output


if __name__ == "__main__":
    print(fetch_spreaker_today("Sara Carter", "4495281"))
