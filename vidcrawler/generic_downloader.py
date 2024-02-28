# flake8: noqa=W293
# pylint: disable=line-too-long,missing-class-docstring,missing-function-docstring,consider-using-f-string,too-many-locals,invalid-name,redefined-builtin

"""
Test script for opening a youtube channel and getting the latest videos.
"""


from vidcrawler.types import ChannelId, ChannelUrl, VideoId
from vidcrawler.ytdlp import fetch_videos_from_channel


def to_rumble_channel_url(id: ChannelId) -> ChannelUrl:
    url: str = f"https://rumble.com/c/{id}/videos"
    return ChannelUrl(url)


def to_youtube_channel_url(id: ChannelId) -> ChannelUrl:
    url: str = f"https://www.youtube.com/channel/{id}"
    return ChannelUrl(url)


def fetch_all_videos_in_rumble_channel(channel_id: ChannelId) -> list[VideoId]:
    url: ChannelUrl = to_rumble_channel_url(channel_id)
    vids: list[VideoId] = fetch_videos_from_channel(url)
    return vids


def fetch_all_videos_in_youtube_channel(channel_id: ChannelId) -> list[VideoId]:
    url: ChannelUrl = to_youtube_channel_url(channel_id)
    vids: list[VideoId] = fetch_videos_from_channel(url)
    return vids


def fetch_all_videos_in_channel(channel_type: str, channel_id: ChannelId) -> list[VideoId]:
    if channel_type == "youtube":
        fetcher = fetch_all_videos_in_youtube_channel
    elif channel_type == "rumble":
        fetcher = fetch_all_videos_in_rumble_channel
    else:
        raise ValueError(f"Unknown channel_type: {channel_type}")
    out: list[VideoId] = fetcher(channel_id)
    return out


def unit_test() -> int:
    channel_id = ChannelId("UCiuTGTCkYrjVknhvMAICFjA")
    vidlist = fetch_all_videos_in_channel("youtube", channel_id)
    print(f"Found {len(vidlist)} videos.")
    for vid in vidlist:
        print(f"  {vid}")
    return 0


def main() -> int:
    return unit_test()


if __name__ == "__main__":
    main()
