"""
Spotify scraper
"""

# pylint: disable=line-too-long,missing-function-docstring,consider-using-f-string,too-many-locals,invalid-name,no-else-return,fixme

import sys
from datetime import datetime
from typing import List

from bs4 import BeautifulSoup  # type: ignore

from .date import iso_fmt
from .fetch_html import fetch_html_using_request_lib as fetch_html
from .video_info import VideoInfo

_TIMEOUT_EPISODE = 20  # Wow these can take a long time.

# TODO: Allow spotify scraper to access the database and check to see if
# the episode is already there.


def now_local() -> datetime:
    """Patch to allow code to work."""
    return datetime.now()


def fetch_spotify_today(channel_name: str, channel: str) -> List[VideoInfo]:
    output: List[VideoInfo] = []
    now_datestr = iso_fmt(now_local())
    channel_url = f"https://open.spotify.com/show/{channel}"
    sys.stdout.write(
        f"Spotify crawler visiting {channel_name} ({channel_url})\n"
    )
    html_doc = fetch_html(channel_url)
    html_dom = BeautifulSoup(html_doc, "html.parser")
    music_doms = html_dom.findAll("meta", {"name": "music:song"})
    episode_urls = [e.attrs["content"] for e in music_doms]
    for episide_url in episode_urls:
        sys.stdout.write(f"  Spotify crawler visiting episode {episide_url}\n")
        episode_html = fetch_html(episide_url, timeout=_TIMEOUT_EPISODE)
        episode_dom = BeautifulSoup(episode_html, "html.parser")

        def extract_meta_property(name: str) -> str:
            dom = episode_dom.find(  # pylint: disable=cell-var-from-loop
                "meta", {"name": name}
            )
            return str(dom["content"])

        img_url = extract_meta_property("og:image")
        title = extract_meta_property("og:title")
        description = extract_meta_property("og:description")
        release_date = extract_meta_property("music:release_date")
        duration = extract_meta_property("music:duration")
        url = extract_meta_property("og:url")
        # example:
        #   "4rJBoD4BeeYFd8eLhrDRM" is extracted from
        #   "https://open.spotify.com/episode/4rJBoD4BeeYFd8eLhrDRM"
        spotify_id = url.split("episode")[1].replace("/", "")
        title = extract_meta_property("og:title")
        vid_url = f"https://open.spotify.com/episode/{spotify_id}"
        iframe_url = f"https://open.spotify.com/embed/episode/{spotify_id}"
        vid: VideoInfo = VideoInfo(
            channel_name=channel_name,
            source="spotify.com",
            date_published=release_date,
            date_discovered=now_datestr,
            date_lastupdated=now_datestr,
            url=vid_url,
            channel_url=channel_url,
            title=title,
            duration=duration,
            description=description,
            img_src=img_url,
            iframe_src=iframe_url,
            views="?",
            profile_img_src="",
        )
        output.append(vid)
    return output


def unit_test() -> None:
    fetch_spotify_today(
        channel_name="Joe Rogan", channel="4rOoJ6Egrf8K2IrywzwOMk"
    )


if __name__ == "__main__":
    # Unit test
    unit_test()
