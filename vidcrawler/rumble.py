"""
Rumble scrapper.
"""

# pylint: disable=line-too-long,missing-function-docstring,consider-using-f-string,too-many-locals,invalid-name,no-else-return,fixme

import sys
import traceback
import warnings
from typing import List, Tuple

from bs4 import BeautifulSoup  # type: ignore

from .date import iso_fmt, now_local, timestamp_to_iso8601
from .fetch_html import fetch_html_using_curl as fetch_html
from .video_info import VideoInfo
from .ytdlp import fetch_video_info


def fetch_rumble(channel: str) -> Tuple[str, str]:
    html_doc: str = ""
    channel_url: str = "https://rumble.com/c/%s" % channel
    url: str = "https://rumble.com/c/%s?date=this-month" % channel
    try:
        sys.stdout.write("Rumble visiting %s (%s)\n" % (channel, url))
        html_doc = fetch_html(url)
    except KeyboardInterrupt:
        raise
    except SystemExit:  # pylint: disable=try-except-raise
        raise
    except Exception as err:  # pylint: disable=broad-except
        warnings.warn(f"Error fetching rumble channel {channel}: {err}")
        channel_url = "https://rumble.com/user/%s" % channel
        url = "https://rumble.com/user/%s" % channel
        sys.stdout.write(f"Rumble alt visiting {channel} ({url})\n")
        html_doc = fetch_html(url)
    return (html_doc, channel_url)


def rumble_video_id_to_embed_url(video_id: str) -> str:
    return f"https://rumble.com/embed/{video_id}"

from dataclasses import dataclass


@dataclass
class PartialVideo:
    vid_src: str
    duration: str
    videoid: str
    channel_url: str
    channel_name: str
    


def fetch_rumble_channel_today_legacy(channel_name: str, channel: str) -> List[VideoInfo]:
    # TODO: Fine grained try...catch blocks.
    output: List[VideoInfo] = []
    html_doc: str = ""
    channel_url: str = ""
    html_doc, channel_url = fetch_rumble(channel)
    soup = BeautifulSoup(html_doc, "html.parser")
    for article in soup.find_all("div", class_="videostream thumbnail__grid--item"):
        try:
            article_duration_dom = article.find(class_="videostream__status--duration")
            duration = article_duration_dom.get_text().strip()
            vid_src_suffix = article.find("a", class_="videostream__link link")["href"]
            vid_src = "https://rumble.com%s" % vid_src_suffix
            sys.stdout.write("  visiting video %s (%s)\n" % (channel, vid_src))
            video_obj = fetch_video_info(vid_src)
            video_id = video_obj["id"]
            title = video_obj["fulltitle"]
            iframe_src = rumble_video_id_to_embed_url(video_id)
            desc_text = video_obj["description"]
            publish_timestamp = float(video_obj["timestamp"])
            publish_date = timestamp_to_iso8601(publish_timestamp)
            views = str(video_obj["view_count"])
            thumbnails: list[dict[str, str]] = video_obj["thumbnails"]
            img_src = thumbnails[0]["url"]
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
            sys.stdout.write("Error: %s\nCould not parse\n%s\n\n" % (str(s), str(article)))
    return output

def fetch_rumble_channel_today_partial_result(channel_name: str, channel: str) -> list[PartialVideo]:
    out: List[PartialVideo] = []
    html_doc: str = ""
    channel_url: str = ""
    html_doc, channel_url = fetch_rumble(channel)
    soup = BeautifulSoup(html_doc, "html.parser")
    for article in soup.find_all("div", class_="videostream thumbnail__grid--item"):
        try:
            article_duration_dom = article.find(class_="videostream__status--duration")
            duration = article_duration_dom.get_text().strip()
            vid_src_suffix = article.find("a", class_="videostream__link link")["href"]
            vid_src = "https://rumble.com%s" % vid_src_suffix
            partial_video: PartialVideo = PartialVideo(
                vid_src=vid_src,
                duration=duration,
                videoid="",
                channel_url=channel_url,
                channel_name=channel_name,
            )
            out.append(partial_video)
        except BaseException as e:  # pylint: disable=broad-except
            s = "".join(traceback.format_exception(None, e, e.__traceback__))
            sys.stdout.write("Error: %s\nCould not parse\n%s\n\n" % (str(s), str(article)))
    return out

def resolve(rumble_partial: PartialVideo) -> VideoInfo:
    vid_src = rumble_partial.vid_src
    sys.stdout.write("  visiting video %s (%s)\n" % (rumble_partial.channel_name, vid_src))
    video_obj = fetch_video_info(vid_src)
    video_id = video_obj["id"]
    title = video_obj["fulltitle"]
    iframe_src = rumble_video_id_to_embed_url(video_id)
    try:
        desc_text = video_obj["description"]
    except KeyError:
        warnings.warn(f"Could not find description for {vid_src}")
        desc_text = ""
    try:
        publish_timestamp = float(video_obj["timestamp"])
    except KeyError:
        warnings.warn(f"Could not find timestamp for {vid_src}")
        publish_timestamp = 0
    publish_date = timestamp_to_iso8601(publish_timestamp)
    views = str(video_obj["view_count"])
    thumbnails: list[dict[str, str]] = video_obj["thumbnails"]
    img_src = thumbnails[0]["url"]
    now_datestr = iso_fmt(now_local())
    o = VideoInfo(
        channel_name=rumble_partial.channel_name,
        source="rumble.com",
        date_published=publish_date,
        date_discovered=now_datestr,
        date_lastupdated=now_datestr,
        url=vid_src,
        channel_url=rumble_partial.channel_url,
        title=title,
        duration=rumble_partial.duration,
        description=desc_text,
        img_src=img_src,
        iframe_src=iframe_src,
        views=views,
        profile_img_src="",
    )
    return o


def fetch_rumble_channel_today(channel_name: str, channel: str) -> List[VideoInfo]:
    # use the partial result, then full resolve
    partial_result = fetch_rumble_channel_today_partial_result(channel_name, channel)
    output: List[VideoInfo] = []
    for partial in partial_result:
        vinfo = resolve(partial)
        output.append(vinfo)
    return output

def interactive_test() -> None:
    sys.stdout.write("Rumble user: ")
    name: str = input()
    rslt = fetch_rumble_channel_today(channel_name=name, channel=name)
    print(rslt)


if __name__ == "__main__":
    interactive_test()
