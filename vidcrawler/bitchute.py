"""
    Scraper for bitchute
"""

# pylint: disable=line-too-long,missing-function-docstring,consider-using-f-string,too-many-locals,invalid-name

import html
import re
import sys
from typing import List, Optional

import feedparser  # type: ignore
from bs4 import BeautifulSoup  # type: ignore

from .date import iso_fmt, now_local
from .error import log_error

# bitchute is bombing out on CURL so switch to the request-lib get version.
from .fetch_html import fetch_html_using_request_lib
from .video_info import VideoInfo

_EMBED_BITCHUTE_PATT = r"/video/(.+)/"
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"


def fetch_html(url: str) -> str:
    return fetch_html_using_request_lib(url, user_agent=USER_AGENT)


def parse_rss_url(html_doc: str) -> Optional[str]:
    top_dom = BeautifulSoup(html_doc, "html.parser")
    details_dom = top_dom.find("div", class_="details")
    if not details_dom:
        return None
    inner_dom = details_dom.find("p", class_="name")
    if not inner_dom:
        return None
    attrs = inner_dom.find("a")
    suffix = attrs["href"]
    rss_url: str = "https://www.bitchute.com/feeds/rss" + suffix
    return rss_url


def fetch_rss_url(
    channel_name: str, channel_id: str  # pylint: disable=unused-argument
) -> Optional[str]:
    channel_url = "https://www.bitchute.com/channel/%s/" % channel_id
    html_doc = fetch_html(channel_url)
    return parse_rss_url(html_doc)


def parse_rss_feed(content: str) -> List[dict]:
    feed = feedparser.parse(content)
    channel_url = feed["feed"]["link"]
    # from pprint import pprint
    output: List[dict] = []
    for entry in feed.entries:
        date_published = entry["published"]
        summary = entry["summary"]
        title = entry["title"]
        id = entry["id"]  # pylint: disable=redefined-builtin
        try:
            type_ = entry["title_detail"]["type"]
            if type_ == "text/html":
                title = html.unescape(title)
        except BaseException as err:  # pylint: disable=broad-except
            log_error(f"Error while parsing because of {str(err)}")
        links = entry["links"]
        embed_link = links[0]["href"]
        img_link = links[1]["href"]
        id = re.findall(r".*/embed/([^\/]+)/", entry["link"])[0]
        obj = dict(
            title=title,
            date_published=date_published,
            alt_channel_url=channel_url,
            description=summary,
            img_src=img_link,
            iframe_src=embed_link,
            url="https://www.bitchute.com/video/%s" % id,
        )
        output.append(obj)
    return output


# type: ignore


def fetch_bitchute_today(channel_name: str, channel_id: str) -> List[VideoInfo]:
    output: List[VideoInfo] = []
    channel_url = "https://www.bitchute.com/channel/%s/" % channel_id
    sys.stdout.write(
        "Bitchute visiting %s (%s)\n" % (channel_name, channel_url)
    )
    html_doc = fetch_html(channel_url)
    rss_url = parse_rss_url(html_doc)
    date_published_map = {}
    if rss_url is None:
        sys.stderr.write(
            "---- ERROR ---- Failed to parse rss_channel for %s\n" % channel_url
        )
    else:
        rss_content = fetch_html(rss_url)
        # These objects contain the video publishing date.
        rss_objects: List[dict] = parse_rss_feed(rss_content)
        rss_obj: dict
        for rss_obj in rss_objects:
            key = rss_obj["url"]
            date_published_map[key] = iso_fmt(rss_obj["date_published"])
    soup = BeautifulSoup(html_doc, "html.parser")
    vid_divs = soup.find_all(class_="channel-videos-container")
    skipped_vid_urls: List[str] = []
    for vd in vid_divs:
        title_dom = vd.find(class_="channel-videos-title")
        spa_dom = title_dom.find(class_="spa")
        title_text = spa_dom.text
        views_text = vd.find(class_="video-views").text.strip()
        video_src = spa_dom["href"]
        vid_id = re.findall(_EMBED_BITCHUTE_PATT, video_src)[0]
        iframe_src = "https://www.bitchute.com/embed/%s" % vid_id
        url = "https://www.bitchute.com/video/%s" % vid_id
        duration = vd.find(class_="video-duration").text  # type: ignore
        # poster_dom = plyr__poster
        poster_dom = vd.find(class_="channel-videos-image")
        img_src = poster_dom.find("img")["data-src"]
        now_datestr = now_local().isoformat()
        date_published = date_published_map.get(url)
        if date_published is None:
            skipped_vid_urls.append(url)
            continue
        o = VideoInfo(
            channel_name=channel_name,
            source="bitchute.com",
            date_published=date_published,
            date_discovered=now_datestr,
            date_lastupdated=now_datestr,
            url=url,
            channel_url=channel_url,
            title=title_text,
            duration=duration,
            description="TODO",
            img_src=img_src,
            iframe_src=iframe_src,
            views=views_text,
            profile_img_src="",
        )
        output.append(o)
    if skipped_vid_urls:
        sys.stdout.write(
            f"{__file__}: Skipping {len(skipped_vid_urls)} videos from {channel_name} because no data from rss.\n"
        )
    return output
