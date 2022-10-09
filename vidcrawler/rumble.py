"""
Rumble scrapper.
"""

# pylint: disable=line-too-long,missing-function-docstring,consider-using-f-string,too-many-locals,invalid-name,no-else-return,fixme

import json
import sys
import traceback
from typing import Dict, List, Tuple

import isodate  # type: ignore
import requests
from bs4 import BeautifulSoup  # type: ignore

from .date import iso_fmt, now_local
from .fetch_html import fetch_html_using_request_lib as fetch_html
from .video_info import VideoInfo


def parse_rumble_video_object(html_doc: str) -> Dict[str, str]:
    soup_article = BeautifulSoup(html_doc, "html.parser")
    script_dom = soup_article.find("script", {"type": "application/ld+json"})
    json_string = script_dom.contents[0]
    data = json.loads(json_string)  # type: ignore
    return data[0]  # type: ignore


def fetch_rumble(channel: str) -> Tuple[str, str]:
    html_doc: str = ""
    channel_url: str = "https://rumble.com/c/%s" % channel
    url: str = "https://rumble.com/c/%s?date=this-month" % channel
    try:
        sys.stdout.write("Rumble visiting %s (%s)\n" % (channel, url))
        html_doc = fetch_html(url)
    except requests.exceptions.HTTPError:
        channel_url = "https://rumble.com/user/%s" % channel
        url = "https://rumble.com/user/%s" % channel
        sys.stdout.write(f"Rumble alt visiting {channel} ({url})\n")
        html_doc = fetch_html(url)
    return (html_doc, channel_url)


# type: ignore


def fetch_rumble_channel_today(
    channel_name: str, channel: str
) -> List[VideoInfo]:
    # TODO: Fine grained try...catch blocks.
    output: List[VideoInfo] = []
    html_doc: str = ""
    channel_url: str = ""
    html_doc, channel_url = fetch_rumble(channel)
    # print(html_doc)
    soup = BeautifulSoup(html_doc, "html.parser")
    for article in soup.find_all("article", class_="video-item"):
        try:
            article_duration_dom = article.find(class_="video-item--duration")
            duration = (
                ""
                if not article_duration_dom
                else article_duration_dom["data-value"]
            )
            vid_src_suffix = article.find(class_="video-item--a")["href"]
            vid_src = "https://rumble.com%s" % vid_src_suffix
            sys.stdout.write("  visiting video %s (%s)\n" % (channel, vid_src))
            html_doc2 = fetch_html(vid_src)
            video_obj = parse_rumble_video_object(html_doc2)
            title = video_obj["name"]
            iframe_src = video_obj["embedUrl"]
            desc_text = video_obj["description"]
            publish_date = video_obj["uploadDate"]

            if not duration:
                duration_str = video_obj["duration"]
                duration = isodate.parse_duration(duration_str).total_seconds()
            try:
                views = video_obj["interactionStatistic"]["userInteractionCount"]  # type: ignore
            except KeyError:
                views = "?"
            # img_src = video_obj['thumbnailUrl']
            img_src = article.find(class_="video-item--img")["src"]
            now_datestr = iso_fmt(now_local())
            o = VideoInfo(
                channel_name=channel_name,
                source="rumble.com",
                date_published=publish_date,
                date_discovered=now_datestr,
                date_lastupdated=now_datestr,
                url=vid_src,
                channel_url=channel_url,
                title=title,
                duration=duration,
                description=desc_text,
                img_src=img_src,
                iframe_src=iframe_src,
                views=views,
                profile_img_src="",
            )
            output.append(o)
        except BaseException as e:  # pylint: disable=broad-except
            s = "".join(traceback.format_exception(None, e, e.__traceback__))
            sys.stdout.write(
                "Error: %s\nCould not parse\n%s\n\n" % (str(s), str(article))
            )
    return output


def interactive_test() -> None:
    sys.stdout.write("Rumble user: ")
    name: str = input()
    rslt = fetch_rumble_channel_today(channel_name=name, channel=name)
    print(rslt)


if __name__ == "__main__":
    interactive_test()
