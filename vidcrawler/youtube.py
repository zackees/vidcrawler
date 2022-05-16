"""
YouTube scraper.
"""

# pylint: disable=invalid-name,consider-using-f-string,fixme,missing-function-docstring,R0801

import datetime
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from typing import Any, List, Optional

import feedparser  # type: ignore
import requests  # type: ignore
from bs4 import BeautifulSoup  # type: ignore
from keyvalue_sqlite import KeyValueSqlite as KeyValueDB  # type: ignore

from .date import iso8601_duration_as_seconds, iso_fmt, now_local
from .error import log_error
from .fetch_html import fetch_html_using_request_lib, fetch_html
from .video_info import VideoInfo

_ENABLE_PROFILE_FETCH = False

HERE = os.path.dirname(__file__)
DB_YOUTUBE_CACHE = os.path.join(HERE, "cache", "youtube_cache.db")
os.makedirs(os.path.dirname(DB_YOUTUBE_CACHE), exist_ok=True)

# Retired. Lots of cost and only 10% of videos have subtitles.
# subtitle_fetcher_cache = YtSubtitleFetcherCache(DB_YOUTUBE_SUBTITLE)


def _get_cache(cache_path: str) -> KeyValueDB:
    return KeyValueDB(cache_path, "cached_youtube_video_attributes")


def _try_get_cached_duration(
    url: str, cache_path: Optional[str]
) -> Optional[int]:
    if cache_path is None:
        return None
    cache = _get_cache(cache_path)
    cached_data = cache.get(url)
    if cached_data:
        duration = cached_data.get("duration_seconds")
        if duration is not None:
            return int(duration)
    return None


def _set_cached_duration(
    url: str, duration_secs: int, cache_path: Optional[str]
) -> None:
    if cache_path is None:
        return
    cache = _get_cache(cache_path)
    cached_data = cache.get(url)
    if not cached_data:
        cached_data = {}
    cached_data.update({"duration_seconds": duration_secs})
    cache[url] = cached_data


def strfdelta(duration_seconds: int) -> str:
    if duration_seconds == 0:
        return "Live"
    td = datetime.timedelta(seconds=duration_seconds)
    hours, rem = divmod(td.seconds, 3600)
    mins, seconds = divmod(rem, 60)
    if hours == 0:
        return "%d:%02d" % (mins, seconds)
    return "%d:%02d:%02d" % (hours, mins, seconds)


def fetch_youtube_duration_str(url: str, cache_path: Optional[str]) -> str:
    sys.stdout.write("  Youtube visiting video %s\n" % url)
    cached_duration = _try_get_cached_duration(url, cache_path)
    if cached_duration:
        if cached_duration > -1:
            return strfdelta(cached_duration)
        return ""  # Gracefully handle error condition.
    try:
        html_doc = fetch_html(url)
        assert html_doc, f"{__file__}: Could not fetch html doc from {url}"
        soup = BeautifulSoup(html_doc, "html.parser")
        dom = soup.find("meta", {"itemprop": "duration"})
        assert dom, f"{__file__}: Could not find duration in html doc in {url}"
        duration_str = dom.attrs["content"]
        duration_seconds = iso8601_duration_as_seconds(duration_str)
        _set_cached_duration(url, duration_seconds, cache_path)
        return strfdelta(duration_seconds)
    except requests.exceptions.HTTPError as e:
        sys.stderr.write(
            f'{__file__} Error while processing {url} for duration because "{str(e)}"\n'
        )
        _set_cached_duration(url, -1, cache_path)
        return ""


def _fetch_youtube_channel_via_rss(
    channel_name: str, channel_id: str
) -> List[VideoInfo]:
    url = "https://www.youtube.com/feeds/videos.xml?channel_id=" + channel_id
    sys.stdout.write(f"Youtube visiting {channel_name} ({url})\n")
    content = fetch_html(url)
    if "was not found on this server" in content:  # TODO: Make less hacky.
        raise OSError(f"Could not fetch {url}")
    feed = feedparser.parse(content)
    output: List[VideoInfo] = []
    profile_picture = None
    for entry in feed.entries:
        views = entry.media_statistics["views"]
        if views == "0":  # Skip views with 0 as they have not be released yet.
            continue
        # Disable profile picture for now.
        if _ENABLE_PROFILE_FETCH and profile_picture is None:
            sys.stdout.write(
                f"  Youtube visiting {entry.link} to fetch profile picture.\n"
            )
            vid_html = fetch_html(entry.link)
            if vid_html is None:
                sys.stdout.write(
                    f"    Error - vid_html from {entry.link} was None"
                )
            else:
                try:
                    vid_info = parse_youtube_video(vid_html)
                    profile_picture = vid_info.get("profile_thumbnail", None)
                except AttributeError as err:
                    sys.stdout.write(
                        f"Failed to get photo from {entry.link} because {err}.\n"
                    )
        now_datestr = iso_fmt(now_local())
        o = VideoInfo(
            channel_name=channel_name,
            title=entry.title,
            date_published=entry.published,
            date_discovered=now_datestr,
            date_lastupdated=now_datestr,
            channel_url=entry.author_detail.href,
            source="youtube.com",
            url=entry.link,
            duration="?",
            description=entry.summary,
            img_src=entry.media_thumbnail[0]["url"],
            iframe_src="https://youtube.com/embed/" + entry.yt_videoid,
            views=views,
            profile_img_src=profile_picture or "",
        )
        output.append(o)
    return output


def _fetch_youtube_channel_via_html(
    channel_name: str,
    channel_id: str,
    limit: int = -1,
) -> List[Any]:
    """SLOW! Also, Experimental - use if the videos.xml api is disabled"""

    # Step 1: using the channel_id fetch the channel_name.
    # TODO: this should be cached to avoid a fetch.
    url = f"https://www.youtube.com/channel/{channel_id}"
    sys.stdout.write(f"Youtube visiting {channel_name} ({url})\n")
    html_doc = fetch_html(url)
    pat = r'\"canonicalBaseUrl\":\"/c/([^\"]+)"'
    canonical_name = re.findall(pat, html_doc)[0]
    # Now the fetch the videos list from the channels canonical name
    # url.
    url = f"https://youtube.com/c/{canonical_name}/videos"
    chan_html_doc = fetch_html_using_request_lib(url)
    # Inside a json file there is a bunch of videos that can be found
    # using the following regex.
    pat = r"{\"videoId\":\"([^\"]+)\","
    vid_ids = list(set(re.findall(pat, chan_html_doc)))
    vid_urls = [f"https://youtube.com/watch?v={id}" for id in vid_ids]
    output = []
    # Iterate through all videos and use the youtube-dl python command to
    # get a json dump of the file. Unfortunately this does not include the
    # very import publishing date time stamp. Another note is that with a
    # little bit of research it's not clear that there are alternative ways
    # to get exact timestamps from Youtube other than by videos.xml api, or
    # the youtube api which requires an audit of the app. Work arounds include
    # cross referencing the videos with those scraped from social blade or using
    # a paid service to get these videos.
    for i, vid_url in enumerate(vid_urls):
        if limit != -1 and i >= limit:
            break
        stdout = subprocess.check_output(
            f"youtube-dl {vid_url} -j", shell=True
        ).decode("utf-8")
        data = json.loads(stdout)
        # Future:
        #  title = data['title']
        #  view_count = data['view_count']
        output.append(data)
    return output


def fetch_youtube_today(
    channel_name: str,
    channel_id: str,
    cache_path: Optional[str] = DB_YOUTUBE_CACHE,
    limit: int = -1,
) -> List[VideoInfo]:
    start_time = time.time()
    video_list = _fetch_youtube_channel_via_rss(channel_name, channel_id)
    if limit != -1:
        video_list = video_list[0:limit]
    vid: VideoInfo
    for vid in video_list:
        # Add in duration with per-video fetch
        duration_time = fetch_youtube_duration_str(vid.url, cache_path)
        vid.duration = duration_time
    delta_time = start_time - time.time()
    if delta_time > 15:
        sys.stdout.write(
            f"WARNING, youtube scraper took {int(delta_time)} seconds to complete\n"
        )
    return video_list


def _test_fetch_youtube_video_info(url: str) -> None:
    sys.stdout.write("Youtube visiting video %s\n" % url)
    html_doc = fetch_html(url)
    premiered_ago_matches = re.findall(r'\"Premiered (.{1,15}) ago"}', html_doc)
    premiered_in_progress = re.findall(
        r'\"Premiere in progress\. Started (.{1,15}) ago"}', html_doc
    )
    started_streaming_matches = re.findall(
        r"\"Started streaming (.{1,15}) ago\"", html_doc
    )
    video_is_private = '{"simpleText":"Private video"}' in html_doc
    unplayable = '"status":"UNPLAYABLE"' in html_doc
    # has_set_reminder = re.findall(r'\"simpleText\":\"Set reminder\"', html_doc)
    # has_set_reminder = '{"simpleText":"Set reminder"}' in html_doc

    stream_offline = '"status":"LIVE_STREAM_OFFLINE"' in html_doc

    print("  Testing %s" % url)
    print("    Premiered ago: %s" % premiered_ago_matches)
    print("    Premiered in progress started: %s" % premiered_in_progress)
    print("    Started streaming ago: %s" % started_streaming_matches)
    print("    Has stream_offline: %s" % stream_offline)
    print("    Is unplayable: %s" % unplayable)
    print("    Video is private: %s" % video_is_private)


# Still experimental
def parse_youtube_video(html_doc: str) -> dict:
    out: dict = {
        "date_published": "?",
        "views": "?",
        "profile_thumbnail": "?",
        "is_live": "?",
    }
    if '"isLiveNow":true' in html_doc:
        out["is_live"] = "True"
    else:
        out["is_live"] = "False"
    top_dom = BeautifulSoup(html_doc, "html.parser")  # type: ignore
    try:
        dom = top_dom.find("meta", {"itemprop": "startDate"})  # type: ignore
        out["date_published"] = str(dom.attrs["content"])
    except KeyError as err:
        log_error(str(err))
    except AttributeError as err:
        text = "NO STATUS"
        try:
            text = top_dom.text
        except Exception as err2:  # pylint: disable=broad-except
            print(f"{__file__}: Error: {err2}")
        sys.stdout.write(
            f"{__file__}: \ntop_dom.text: {text}\n\nError: {err}\n"
        )
        raise
    try:
        dom = top_dom.find("meta", {"itemprop": "interactionCount"})  # type: ignore
        out["views"] = str(dom.attrs["content"])
    except KeyError as ke:
        log_error(str(ke))
    all_scripts = top_dom.find_all("script")
    needle_initial_data = "var ytInitialData = "
    # Needed for commented out code, below.
    # needle_player_response = "var ytInitialPlayerResponse = "
    for script in all_scripts:
        if not script.string:
            continue
        try:
            if script.string.startswith(needle_initial_data):
                img_urls = re.findall(
                    r"\"(https://yt\d[^\"]+)\"", script.string
                )
                for img_url in img_urls:
                    if (
                        "s176" in img_url
                    ):  # For some reason this appears only in the thumbnail image.
                        out["profile_thumbnail"] = img_url
                        break
            # Video Details contains a lot of gems, but is disabled for now.
            # if script.string.startswith(needle_player_response):
            #     last_semi: int = script.string.rfind(";")
            #     json_str = script.string[
            #         len(needle_player_response) : last_semi
            #     ]
            #     json_data = json.loads(json_str)
            #     video_details = json_data["videoDetails"]
        except BaseException as be:  # pylint: disable=broad-except
            log_error("Error: " + str(be) + " for " + str(out))
    return out


def test_fetch_duration():
    url = "https://www.youtube.com/watch?v=UywxSWjzGaU"
    try:
        cache_path_file = (
            tempfile.NamedTemporaryFile(  # pylint: disable=consider-using-with
                suffix=".db", delete=False
            )
        )
        cache_path = cache_path_file.name
        cache_path_file.close()
        duration_str = fetch_youtube_duration_str(url, cache_path=cache_path)
        print("Discovered that the video at %s is %s" % (url, duration_str))
        duration_str = fetch_youtube_duration_str(url, cache_path=cache_path)
        print("Discovered that the video at %s is %s" % (url, duration_str))
    finally:
        os.remove(cache_path)


if __name__ == "__main__":
    # test_fetch_duration()
    _test_fetch_youtube_video_info(
        "https://www.youtube.com/watch?v=5nBqIK0mrFI"
    )
    _test_fetch_youtube_video_info(
        "https://www.youtube.com/watch?v=r5VjrVqgEU8"
    )
    _test_fetch_youtube_video_info(
        "https://www.youtube.com/watch?v=xfJsiDkbjg0"
    )
    # Project veritas should not return anything
    _test_fetch_youtube_video_info(
        "https://www.youtube.com/watch?v=F7y19uNaYfE"
    )
    # Upcoming film
    _test_fetch_youtube_video_info(
        "https://www.youtube.com/watch?v=yv7NFn95R0s"
    )
    _test_fetch_youtube_video_info(
        "https://www.youtube.com/watch?v=egRMAnwUQDQ"
    )
