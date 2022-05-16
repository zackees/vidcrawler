"""
    Scraper for Brighteon.com
"""

# pylint: disable=line-too-long,missing-function-docstring,consider-using-f-string,too-many-locals,invalid-name,no-else-return


import json
import sys
from typing import List

from bs4 import BeautifulSoup  # type: ignore

from .date import iso_fmt, now_local
from .fetch_html import fetch_html_using_request_lib as fetch_html
from .video_info import VideoInfo


def fetch_brighteon_today(channel_name: str, channel: str) -> List[VideoInfo]:
    output: List[VideoInfo] = []
    url = "https://www.brighteon.com/channels/%s" % channel
    sys.stdout.write("Brighteon visiting %s (%s)\n" % (channel, url))
    html_doc = fetch_html(url)
    soup = BeautifulSoup(html_doc, "html.parser")
    json_data = soup.find("script", id="__NEXT_DATA__").string
    data = json.loads(json_data)
    channel_data = data["props"]["initialProps"]["pageProps"]["data"]
    videos = channel_data["videos"]
    for vid in videos:
        created_time = vid["createdAt"]
        id = vid["id"]  # pylint: disable=redefined-builtin
        iframe_url = "https://www.brighteon.com/embed%s" % id
        video_url = "https://www.brighteon.com/%s" % id
        title = vid["name"]
        image_src = vid["thumbnail"]
        view_count = vid["analytics"]["videoView"]
        duration = vid["duration"]
        now_datestr = iso_fmt(now_local())
        o = VideoInfo(
            channel_name=channel_name,
            source="brighteon.com",
            date_published=created_time,
            date_discovered=now_datestr,
            date_lastupdated=now_datestr,
            url=video_url,
            channel_url=url,
            title=title,
            duration=duration,
            description="TODO",
            img_src=image_src,
            iframe_src=iframe_url,
            views=view_count,
            profile_img_src="",
        )
        output.append(o)
    return output
