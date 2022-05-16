"""Spider which crawls all the channels"""

# pylint: disable=line-too-long,missing-function-docstring,consider-using-f-string,too-many-locals,invalid-name,no-else-return

import json
import queue
import random
import signal
import sys
import threading
import time
import traceback
from typing import Any, Dict, List, Tuple

from .bitchute import fetch_bitchute_today
from .brighteon import fetch_brighteon_today
from .gabtv import fetch_gabtv_today
from .odysee import fetch_odysee_today
from .rumble import fetch_rumble_channel_today
from .spotify import fetch_spotify_today
from .spreaker import fetch_spreaker_today
from .video_info import VideoInfo
from .youtube import fetch_youtube_today

BRIGHTEON = "brighteon"
YOUTUBE = "youtube"
RUMBLE = "rumble"
BITCHUTE = "bitchute"
SPREAKER = "spreaker"
ODYSEE = "odysee"
GAB = "gab"
SPOTIFY = "spotify"

CRAWLER_MAP = {
    RUMBLE: fetch_rumble_channel_today,
    BITCHUTE: fetch_bitchute_today,
    BRIGHTEON: fetch_brighteon_today,
    YOUTUBE: fetch_youtube_today,
    SPREAKER: fetch_spreaker_today,
    ODYSEE: fetch_odysee_today,
    GAB: fetch_gabtv_today,
    SPOTIFY: fetch_spotify_today,
}

_SCRAPE_RANDOMIZE_ORDER = True
_YT_SCRAPER_ENABLE_THREADS = True
_YT_SCRAPER_ENABLE_THREADS = False

# type: ignore


def _fetch_all(
    source_name: str,
    fetch_list: List[Tuple[str, str]],
    out_queue: queue.Queue,
    bad_channels: queue.Queue,
) -> None:
    callback = CRAWLER_MAP[source_name]
    if _SCRAPE_RANDOMIZE_ORDER:
        random.shuffle(fetch_list)

    def do_fetch(fetch_list: List, callback: Any) -> None:
        for (channel_name, channel_id) in fetch_list:
            try:
                videos = callback(channel_name, channel_id)  # type: ignore
                for vid in videos:
                    out_queue.put(vid)
            except KeyboardInterrupt:
                sys.exit(1)
            except BaseException as e:
                traceback.print_exc()
                entry = (channel_name, str(e))
                bad_channels.put(entry)
                continue

    if source_name != YOUTUBE:
        do_fetch(fetch_list, callback)
        return
    if not _YT_SCRAPER_ENABLE_THREADS:
        do_fetch(fetch_list, callback)
        return
    # YouTube and threads enabled.
    num_workers = 4
    thread_data = [[] for _ in range(num_workers)]  # type: ignore
    for i, data in enumerate(fetch_list):
        idx = i % num_workers
        thread_data[idx].append(data)
    threads = []
    for tdata in thread_data:
        thread = threading.Thread(target=do_fetch, args=(tdata, callback))
        thread.daemon = True
        thread.start()
        threads.append(thread)
    for t in threads:
        t.join()


def _yield_thread_for_keyboard_interrupt() -> None:
    if sys.platform == "win32":
        time.sleep(0.1)
    else:
        try:
            # might be missing on some platforms.
            signal.pause()  # pylint: disable-all
        except BaseException:
            time.sleep(0.1)


def _threaded_fetch_channels(
    channels: List[Tuple[str, str, str]],
    out_videos: List[VideoInfo],
    out_bad_channels: List[Tuple[str, str]],
) -> None:
    # Partition the list by source type (bitchute, youtube, ...)
    # for each source fetch all videos.
    partitioned: Dict[str, Any] = {}
    for (channel_name, source, channel_id) in channels:
        partitioned.setdefault(source, [])
        partitioned[source].append((channel_name, channel_id))
    queue_out: queue.Queue = queue.Queue()
    queue_bad_channels: queue.Queue = queue.Queue()
    # Launch threads but also makes the main thread responsive to the keyboard interrupt.
    threads = []
    for source, array_data in partitioned.items():
        thread = threading.Thread(
            target=_fetch_all,
            args=(source, array_data, queue_out, queue_bad_channels),
        )
        thread.daemon = True
        thread.start()
        threads.append(thread)
    while True:  # Weird loop allows KeyboardInterrupt
        finish_cnt = 0
        for t in threads:
            if t.is_alive():
                finish_cnt += 1
        if finish_cnt == len(threads):
            break
        _yield_thread_for_keyboard_interrupt()
    # Busy loop here allows keyboard interrupts to filter through to the
    # top and halt the execution of the program right away.
    while len(threads):
        for i, thread in enumerate(threads):
            if not thread.is_alive():
                thread.join()
                threads.pop(i)
                break  # Start the outer loop again
        time.sleep(0.1)
    while not queue_out.empty():
        out_videos.append(queue_out.get_nowait())
    for c in list(queue_bad_channels.queue):
        out_bad_channels.append(c)


def _singlethreaded_fetch(
    channels: List[Tuple[str, str, str]],
    out_videos: List[VideoInfo],
    out_bad_channels: List[Tuple[str, str]],
) -> None:
    partitioned: Dict[str, Any] = {}
    for (channel_name, source, channel_id) in channels:
        partitioned.setdefault(source, [])
        partitioned[source].append((channel_name, channel_id))
    queue_out: queue.Queue = queue.Queue()
    queue_bad_channels: queue.Queue = queue.Queue()
    for source, array_data in partitioned.items():
        _fetch_all(source, array_data, queue_out, queue_bad_channels)
    while not queue_out.empty():
        out_videos.append(queue_out.get_nowait())
    for c in list(queue_bad_channels.queue):
        out_bad_channels.append(c)


def crawl_video_sites(channels: List[Tuple[str, str, str]], use_threads: bool = True) -> str:  # type: ignore
    vid_infos: List[VideoInfo] = []
    bad_channels: List[Tuple[str, str]] = []
    if use_threads:
        _threaded_fetch_channels(channels, vid_infos, bad_channels)
    else:
        _singlethreaded_fetch(channels, vid_infos, bad_channels)
    # apply_fetch_images(vid_infos)
    out_data: List[Dict] = VideoInfo.to_plain_list(vid_infos)  # type: ignore
    json_str = json.dumps(
        out_data, indent=2, sort_keys=True, ensure_ascii=False
    )
    bad_channels.sort()
    if bad_channels:
        print("#############")
        print("# Bad channels:")
        for name, err in bad_channels:
            print(f"#  {name}: {err}")
        print("#############")
    else:
        print("No bad channels detected!")
    return json_str
