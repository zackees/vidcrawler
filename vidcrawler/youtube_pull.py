"""
Command entry point.
"""

# pylint: disable=consider-using-f-string

import argparse
import os
import subprocess
import warnings

from static_ffmpeg import add_paths

from vidcrawler.library_json import LibraryJson
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

    for _ in range(3):
        try:
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
            return
        except subprocess.CalledProcessError as cpe:
            print(f"Failed to download {url} as mp3: {cpe}")
            continue
    warnings.warn(f"Failed all attempts to download {url} as mp3.")


def main() -> None:
    """Main function."""
    args = parse_args()
    channel_url = to_channel_url(args.channel)
    output_dir = os.path.join(args.basedir, args.channel, "youtube")
    limit_scroll_pages = args.limit_scroll_pages
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    library_json = os.path.join(output_dir, "library.json")
    library = LibraryJson(library_json)
    if not args.skip_scan:
        vids: list[YtVid] = fetch_all_vids(channel_url, limit=limit_scroll_pages)
        library.merge(vids)
        print(f"Updated {library_json}")
    else:
        if not os.path.exists(library_json):
            raise FileNotFoundError(f"{library_json} does not exist. Cannot skip scan.")
    if args.download:
        print("Warning: The --download option is deprecated is now implied. Use --skip-download to avoid downloading")
    if not args.skip_download:
        download_count = 0
        while True:
            if args.download_limit != -1 and download_count >= args.download_limit:
                break
            missing_downloads = library.find_missing_downloads()
            # make full paths
            for vid in missing_downloads:
                vid.file_path = os.path.join(output_dir, vid.file_path)
            if not missing_downloads:
                break
            vid = missing_downloads[0]
            next_url = vid.url
            next_mp3_path = vid.file_path
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
