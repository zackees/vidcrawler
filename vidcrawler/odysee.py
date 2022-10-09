"""
Odysee scrapper.
"""

# pylint: disable=invalid-name

from typing import List

import feedparser  # type: ignore
import requests  # type: ignore

from .date import iso_fmt, now_local
from .video_info import VideoInfo

_TIMEOUT = 10


def _parse_rss_entry(entry: feedparser.util.FeedParserDict) -> VideoInfo:
    """Parses an rss entry and outputs a VideoInfo object."""
    title = entry.title
    link = entry.link
    links = entry.links
    published = entry.published
    thumbnail_img = ""
    for lnk in links:
        if lnk.type.lower().startswith("image/"):
            thumbnail_img = lnk.href
            break
    description = getattr(entry, "description", "")
    o = VideoInfo(
        channel_name="",
        title=title,
        date_published=published,
        date_discovered="",
        date_lastupdated="",
        source="odysee.com",
        url=link,
        duration="?",  # No duration, suprisingly.
        description=description,
        img_src=thumbnail_img,
        iframe_src="",
        views="?",
        profile_img_src=thumbnail_img,
    )
    return o


def fetch_odysee_today(channel_name: str, channel: str) -> List[VideoInfo]:
    """Fetches the latest videos from odysee.com."""
    url: str = f"https://lbryfeed.melroy.org/channel/odysee/{channel}"
    channel_url: str = f"https://odysee.com/@{channel}"
    resp = requests.get(url, timeout=_TIMEOUT)
    now_str: str = iso_fmt(now_local())
    resp.raise_for_status()
    feed = feedparser.parse(resp.text)
    out: List[VideoInfo] = []
    for entry in feed.entries:
        vo = _parse_rss_entry(entry)
        vo.channel_name = channel_name
        vo.channel_url = channel_url
        vo.date_discovered = now_str
        vo.date_lastupdated = now_str
        if vo:
            out.append(vo)
    return out
