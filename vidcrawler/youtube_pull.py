"""
Command entry point.
"""

# pylint: disable=consider-using-f-string

import argparse
import json
import os
import subprocess

from filelock import FileLock
from static_ffmpeg import add_paths

from vidcrawler.youtube_bot import YtVid, fetch_all_vids


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser("youtube-pull")
    parser.add_argument(
        "channel",
        type=str,
        # help="URL of the channel, example: https://www.youtube.com/@silverguru/videos",
        help="URL slug of the channel, example: @silverguru",
    )
    parser.add_argument("basedir", type=str)
    parser.add_argument(
        "--limit-scroll-pages",
        type=int,
        default=1000,
        help="Limit the number of the number of pages to scroll down",
    )
    parser.add_argument(
        "--download",
        action="store_true",
        help="Deprecated: This option does nothing.",
    )
    parser.add_argument(
        "--skip-download",
        action="store_true",
        help="Skip the download of the videos.",
    )
    parser.add_argument(
        "--download-limit",
        type=int,
        default=-1,
        help="Limit the number of videos to download",
    )
    parser.add_argument(
        "--skip-scan",
        action="store_true",
        help="Skip the update of the library.json file",
    )
    return parser.parse_args()


def load_json(file_path: str) -> list[dict]:
    """Load json from file if it exists."""
    if not os.path.exists(file_path):
        return []
    with open(file_path, encoding="utf-8", mode="r") as filed:
        # data = json.load(filed)
        # return data
        json_str = filed.read()
    json_obj = json.loads(json_str)
    return json_obj


def save_json(file_path: str, data: list[dict]) -> None:
    """Save json to file."""
    out_str = json.dumps(data, indent=2)
    with open(file_path, encoding="utf-8", mode="w") as filed:
        filed.write(out_str)


def to_channel_url(channel: str) -> str:
    """Convert channel name to channel URL."""
    out = f"https://www.youtube.com/{channel}/videos"
    return out


def yt_dlp_download_mp3(url: str, outmp3: str) -> None:
    """Download the youtube video as an mp3."""
    add_paths()
    par_dir = os.path.dirname(outmp3)
    if par_dir:
        os.makedirs(par_dir, exist_ok=True)
    cmd_list: list[str] = [
        "yt-dlp",
        url,
        "--extract-audio",
        "--audio-format",
        "mp3",
        "--output",
        outmp3,
    ]
    subprocess.run(cmd_list, check=True)


def find_missing_downloads(library_json_path: str) -> list[dict]:
    """Find missing downloads."""
    out: list[dict] = []
    with open(library_json_path, encoding="utf-8", mode="r") as filed:
        data = json.load(filed)
    for vid in data:
        title = vid["title"]
        file_path = os.path.join(os.path.dirname(library_json_path), f"{title}.mp3")
        if not os.path.exists(file_path):
            vid["file_path"] = file_path
            out.append(vid)
    return out


def main() -> None:
    """Main function."""
    args = parse_args()
    channel_url = to_channel_url(args.channel)
    output_dir = os.path.join(args.basedir, args.channel, "youtube")
    limit_scroll_pages = args.limit_scroll_pages
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    library_json = os.path.join(output_dir, "library.json")
    # load the json data if it already exists
    file_lock = library_json + ".lock"
    if not args.skip_scan:
        with FileLock(file_lock):
            loaded_data = load_json(library_json)
            vids: list[YtVid] = fetch_all_vids(channel_url, limit=limit_scroll_pages)
            fetched_data = [vid.to_dict() for vid in vids]
            new_data = list(loaded_data)
            for vid in fetched_data:
                if vid not in loaded_data:
                    new_data.append(vid)
            save_json(library_json, new_data)
        print(f"Updated {library_json}")

    if not os.path.exists(library_json):
        raise FileNotFoundError(f"{library_json} does not exist. Cannot skip scan.")
    if args.download:
        print("Warning: The --download option is deprecated is now implied. Use --skip-download to avoid downloading")
    if not args.skip_download:
        download_count = 0
        while True:
            if args.download_limit != -1 and download_count >= args.download_limit:
                break
            missing_downloads = find_missing_downloads(library_json)
            if not missing_downloads:
                break
            vid = missing_downloads[0]
            next_url = vid["url"]
            next_mp3_path = vid["file_path"]
            print(f"\n#######################\n# Downloading missing file {next_url}: {next_mp3_path}\n" "###################")
            yt_dlp_download_mp3(url=next_url, outmp3=next_mp3_path)
            download_count += 1


if __name__ == "__main__":
    import sys

    sys.argv.append("@silverguru")
    sys.argv.append("tmp")
    sys.argv.append("--limit-scroll-pages")
    sys.argv.append("1")
    main()
