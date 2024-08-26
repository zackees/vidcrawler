"""
    Scraper for Brighteon.com
"""

import re

# pylint: disable=line-too-long,missing-function-docstring,consider-using-f-string,too-many-locals,invalid-name,no-else-return
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import partial
from typing import List

import requests
from bs4 import BeautifulSoup  # type: ignore
from feedparser import FeedParserDict, parse
from PIL import Image  # type: ignore

from .date import iso_fmt, now_local

# from .fetch_html import fetch_html_using_request_lib as fetch_html
from .video_info import VideoInfo

# https://www.brighteon.com/api-v3/channels/hrreport/rss/rss.xml


def get_rss_url(channel: str) -> str:
    return f"https://www.brighteon.com/api-v3/channels/{channel}/rss/rss.xml"


def parse_thumbnail_url(soup: BeautifulSoup) -> str:
    img = soup.find("img")
    if img:
        if "thumbnail" in img["src"]:
            return img["src"]
    raise ValueError("Could not find thumbnail image")


def parse_entry(url: str, channel_name: str, entry: FeedParserDict) -> VideoInfo:
    created_time = entry.published
    iframe_url = "https://www.brighteon.com/embed%s" % entry.id
    video_url = entry.link
    title = entry.title
    summary_html = entry.summary
    summary_soup = BeautifulSoup(summary_html, "html.parser")
    image_src = parse_thumbnail_url(summary_soup)
    # print(summary_html)
    # image_src = entry.media_thumbnail[0]["url"]
    view_count = "?"
    duration = "?"
    now_datestr = iso_fmt(now_local())
    vid = VideoInfo(
        channel_name=channel_name,
        source="brighteon.com",
        date_published=created_time,
        date_discovered=now_datestr,
        date_lastupdated=now_datestr,
        url=video_url,
        channel_url=url,
        title=title,
        duration=duration,
        description=summary_html,
        img_src=image_src,
        iframe_src=iframe_url,
        views=view_count,
        profile_img_src="",
    )
    return vid


def fetch_image_size(vid: VideoInfo) -> None:
    """fetches the height and width by downloading the image"""
    try:
        url: str = vid.img_src
        response = requests.get(url, stream=True, timeout=10)
        response.raw.decode_content = True
        img = Image.open(response.raw)
        vid.img_width = img.width
        vid.img_height = img.height
        vid.img_status = 200
    except Exception as verr:  # pylint: disable=broad-except
        sys.stderr.write(f"Error fetching image size: {verr} during {url}\n")


def fetch_views_and_duration(vid: VideoInfo) -> None:
    url = vid.url
    response = requests.get(url, timeout=10)
    text = response.text
    # pattern is like "3798 views"

    pattern = re.compile(r"(\d+) views")
    match = pattern.search(text)
    if match:
        out = str(match.group(1))
        vid.views = out
    else:
        vid.views = "?"

    # "duration":"22:27"
    # also "duration":"02:34:18"
    pattern = re.compile(r'"duration":"(\d+:\d+:\d+|\d+:\d+)"')
    match = pattern.search(text)
    if match:
        out = str(match.group(1))
        vid.duration = out
    else:
        vid.duration = "?"


def fetch_brighteon_today(channel_name: str, channel: str) -> List[VideoInfo]:
    # switching to rss feed style
    output: List[VideoInfo] = []
    url = get_rss_url(channel)
    sys.stdout.write("Brighteon visiting %s (%s)\n" % (channel, url))
    feed = parse(url)
    entry: FeedParserDict
    for entry in feed.entries:
        try:
            vid = parse_entry(url, channel_name, entry)
            output.append(vid)
        except Exception as verr:  # pylint: disable=broad-except
            sys.stderr.write(f"Error parsing entry: {verr} during {entry}\n")

    with ThreadPoolExecutor(max_workers=8) as executor:
        fetch_size = partial(fetch_image_size)
        futures = [executor.submit(fetch_size, vid) for vid in output]
        for future in as_completed(futures):
            future.result()  # This will raise any exceptions that occurred during execution

    # now bulk fetch the views
    with ThreadPoolExecutor(max_workers=8) as executor:
        fetch_views_partial = partial(fetch_views_and_duration)
        futures = [executor.submit(fetch_views_partial, vid) for vid in output]
        for future in as_completed(futures):
            future.result()  # This will raise any exceptions that occurred during execution

    return output
