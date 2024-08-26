"""
Rumble scrapper.
"""

# pylint: disable=line-too-long,missing-function-docstring,consider-using-f-string,too-many-locals,invalid-name,no-else-return,fixme,too-many-branches,too-many-statements

import sys
import traceback
import warnings
from dataclasses import dataclass
from datetime import datetime
from typing import List

from bs4 import BeautifulSoup  # type: ignore

from .date import iso_fmt, now_local, timestamp_to_iso8601
from .fetch_html import FetchResult
from .fetch_html import fetch_html_using_curl as fetch_html
from .video_info import VideoInfo
from .ytdlp import fetch_video_info


@dataclass
class RumbleResponse:
    html_doc: str
    channel_url: str
    fetch_result: FetchResult


def fetch_rumble_channel_url(channel_url: str) -> RumbleResponse:
    sys.stdout.write(f"Rumble visiting {channel_url}\n")
    # html_doc = fetch_html(channel_url)
    fetch_result: FetchResult = fetch_html(channel_url)
    # return fetch_result
    return RumbleResponse(fetch_result.html, channel_url, fetch_result)


def fetch_rumble(channel: str) -> RumbleResponse:
    html_doc: str = ""
    channel_url: str = "https://rumble.com/c/%s" % channel
    url: str = "https://rumble.com/c/%s?date=this-month" % channel
    try:
        sys.stdout.write("Rumble visiting %s (%s)\n" % (channel, url))
        # html_doc = fetch_rumble_channel_url(url)
        response: RumbleResponse = fetch_rumble_channel_url(url)
        if response.fetch_result.ok:
            html_doc = response.fetch_result.html
        return RumbleResponse(html_doc, channel_url, response.fetch_result)

    except KeyboardInterrupt:
        raise
    except SystemExit:  # pylint: disable=try-except-raise
        raise
    except Exception as err:  # pylint: disable=broad-except
        warnings.warn(f"Error fetching rumble channel {channel}: {err}")
        channel_url = "https://rumble.com/user/%s" % channel
        url = "https://rumble.com/user/%s" % channel
        sys.stdout.write(f"Rumble alt visiting {channel} ({url})\n")
        # html_doc = fetch_html(url)
        fetch_result = fetch_html(url)
        if fetch_result.ok:
            html_doc = fetch_result.html
        else:
            warnings.warn(f"Failed to fetch {url}")
        raise


def rumble_video_id_to_embed_url(video_id: str) -> str:
    return f"https://rumble.com/embed/{video_id}"


@dataclass
class PartialVideo:
    url: str
    title: str
    duration: str
    videoid: str
    channel_url: str
    channel_name: str
    date: datetime

    def to_dict(self) -> dict:
        """Returns a json serializable dictionary."""
        return {
            "url": self.url,
            "duration": self.duration,
            "videoid": self.videoid,
            "channel_url": self.channel_url,
            "channel_name": self.channel_name,
            "date": self.date.isoformat(),
        }


def fetch_rumble_channel_today_legacy(channel_name: str, channel: str) -> List[VideoInfo]:
    # TODO: Fine grained try...catch blocks.
    output: List[VideoInfo] = []
    html_doc: str = ""
    channel_url: str = ""
    # html_doc, channel_url = fetch_rumble(channel)
    fetch_response: RumbleResponse = fetch_rumble(channel)
    html_doc = fetch_response.html_doc
    channel_url = fetch_response.channel_url
    fetch_response = fetch_rumble_channel_url(channel_url)
    if not fetch_response.fetch_result.ok:
        warnings.warn(f"Failed to fetch {channel_url}")
        return []
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
    # html_doc, channel_url = fetch_rumble(channel)
    response: RumbleResponse = fetch_rumble(channel)
    html_doc = response.html_doc
    channel_url = response.channel_url
    fetch_response = fetch_rumble_channel_url(channel_url)
    if not fetch_response.fetch_result.ok:
        warnings.warn(f"Failed to fetch {channel_url}")
        return []

    soup = BeautifulSoup(html_doc, "html.parser")
    for article in soup.find_all("div", class_="videostream thumbnail__grid--item"):
        try:
            article_duration_dom = article.find(class_="videostream__status--duration")
            duration = article_duration_dom.get_text().strip()
            vid_src_suffix = article.find("a", class_="videostream__link link")["href"]
            vid_src = "https://rumble.com%s" % vid_src_suffix
            dom_vid_status = article.find("div", class_="videostream__status")
            if dom_vid_status is not None:
                fuzzy_date = dom_vid_status.get_text().strip()
            else:
                fuzzy_date = ""
            title = parse_title(article)
            date: datetime = parse_fuzzy_date(fuzzy_date)
            partial_video: PartialVideo = PartialVideo(
                url=vid_src,
                title=title,
                duration=duration,
                videoid="",
                channel_url=channel_url,
                channel_name=channel_name,
                date=date,
            )
            out.append(partial_video)
        except BaseException as e:  # pylint: disable=broad-except
            s = "".join(traceback.format_exception(None, e, e.__traceback__))
            sys.stdout.write("Error: %s\nCould not parse\n%s\n\n" % (str(s), str(article)))
    return out


def parse_duration(article_soup: BeautifulSoup) -> str:
    dom_duration = article_soup.find("div", class_="videostream__status--duration")
    if dom_duration is not None:
        duration = dom_duration.get_text().strip()
        return duration
    dom_live = article_soup.find("a", class_="videostream__status--live")
    if dom_live is not None:
        if dom_live.get_text().strip().upper() == "LIVE":
            return "LIVE"
    dom_dvr = article_soup.find("a", class_="videostream__status--dvr")
    if dom_dvr is not None:
        if dom_dvr.get_text().strip().upper() == "DVR":
            return "DVR"
    raise ValueError("Could not find duration")


def parse_title(article_soup: BeautifulSoup) -> str:
    class_name = "thumbnail__title"
    dom_title = article_soup.find(class_=class_name)
    if dom_title is not None:
        title = dom_title.get_text().strip()
        return title
    raise ValueError(f"Could not find title with class {class_name}")


def parse_date(article_soup: BeautifulSoup) -> str:
    # videostream__data--item videostream__date
    dom_date = article_soup.find(class_="videostream__data--item videostream__date")
    if dom_date is not None:
        # does text attribute exist?
        if hasattr(dom_date, "title"):
            date = dom_date["title"]
            if date:
                return date
        return dom_date.get_text().strip()
    warnings.warn("Could not find date")
    return ""


def get_channel_url(channel: str, page_num: int, is_user_channel: bool) -> str:
    # only return a page if the page number is greater than 1
    # if page_num > 1:
    #    if is_user_channel:
    #        return f"https://rumble.com/user/{channel}?page={page_num}"
    #    return f"https://rumble.com/c/{channel}?page={page_num}"
    # if is_user_channel:
    #    return f"https://rumble.com/user/{channel}"
    # return f"https://rumble.com/c/{channel}"
    # let's simplify this
    if is_user_channel:
        base_url = f"https://rumble.com/user/{channel}"
    else:
        base_url = f"https://rumble.com/c/{channel}"
    if page_num > 1:
        return f"{base_url}?page={page_num}"
    return base_url


def parse_fuzzy_date(datestr: str) -> datetime:
    """Parses strings like 'November 6, 2023' into datetime objects."""
    return datetime.strptime(datestr, "%B %d, %Y")


def fetch_rumble_channel_all_partial_result(channel_name: str, channel: str, after: datetime | None = None) -> list[PartialVideo]:
    out: List[PartialVideo] = []
    page = 1
    is_user_channel = False
    test_url = get_channel_url(channel, page, is_user_channel)
    fetch_response = fetch_html(test_url)
    if not fetch_response.ok:
        is_user_channel = True
        # now assert they can be reached
        test_url = get_channel_url(channel, page, is_user_channel)
        fetch_response = fetch_html(test_url)
        if not fetch_response.ok:
            raise ValueError(f"Could not find channel or user {channel}")
    while True:
        try:
            curr_page = page
            page += 1
            html_doc: str = ""
            current_channel_url = get_channel_url(channel, curr_page, is_user_channel)
            # html_doc = fetch_rumble_channel_url(current_channel_url)
            fetch_result: FetchResult = fetch_html(current_channel_url)
            if fetch_result.ok:
                html_doc = fetch_result.html
            else:
                status_code = fetch_result.status_code
                if status_code == 404:
                    break  # expected result when we've reached the end of the channel.
                warnings.warn(f"Failed to fetch {current_channel_url}")
                break
            soup = BeautifulSoup(html_doc, "html.parser")
            for article in soup.find_all("div", class_="videostream thumbnail__grid--item"):
                try:
                    duration = parse_duration(article)
                    vid_src_suffix = article.find("a", class_="videostream__link link")["href"]
                    vid_src = f"https://rumble.com{vid_src_suffix}"
                    fuzzy_date = parse_date(article)
                    date = parse_fuzzy_date(fuzzy_date)
                    title = parse_title(article)
                    if after is not None and date < after:
                        continue
                    videoid = vid_src.split("/")[-1]
                    videoid = videoid.split("-")[0]
                    partial_video: PartialVideo = PartialVideo(
                        url=vid_src,
                        title=title,
                        duration=duration,
                        videoid=videoid,
                        channel_url=current_channel_url,
                        channel_name=channel_name,
                        date=date,
                    )
                    out.append(partial_video)
                except BaseException as e:  # pylint: disable=broad-except
                    s = "".join(traceback.format_exception(None, e, e.__traceback__))
                    sys.stdout.write("Error: %s\nCould not parse\n%s\n\n" % (str(s), str(article)))
        except KeyboardInterrupt:
            raise
        except SystemExit:  # pylint: disable=try-except-raise
            raise
        except Exception as err:  # pylint: disable=broad-except
            warnings.warn(f"Error fetching rumble channel {channel}: {err}")
    return out


def resolve(rumble_partial: PartialVideo) -> VideoInfo:
    vid_src = rumble_partial.url
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
