"""
Command entry point.
"""

# pylint: disable=consider-using-f-string

import argparse
import os

from vidcrawler.library import Library, VidEntry
from vidcrawler.youtube_bot import fetch_all_vids


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser("youtube-pull")
    parser.add_argument(
        "--channel-name",
        type=str,
        # help="URL of the channel, example: https://www.youtube.com/@silverguru/videos",
        help="URL slug of the channel, example: @silverguru",
        required=True,
    )
    parser.add_argument("--output", type=str, help="Output directory", required=True)
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
    parser.add_argument(
        "--yt-dlp-uses-docker",
        action="store_true",
        help="Use docker to run yt-dlp",
    )
    return parser.parse_args()


def to_channel_url(channel: str) -> str:
    """Convert channel name to channel URL."""
    out = f"https://www.youtube.com/{channel}/videos"
    return out


def main() -> None:
    """Main function."""
    args = parse_args()
    if args.yt_dlp_uses_docker:
        os.environ["USE_DOCKER_YT_DLP"] = "1"
    channel_url = to_channel_url(args.channel_name)
    # base_dir = Path(args.basedir)
    # output_dir = str(base_dir / args.channel / "youtube")
    output_dir = args.output
    limit_scroll_pages = args.limit_scroll_pages
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    library_json = os.path.join(output_dir, "library.json")
    library = Library(library_json)
    if not args.skip_scan:
        vids: list[VidEntry] = fetch_all_vids(channel_url, limit=limit_scroll_pages)
        library.merge(vids)
        print(f"Updated {library_json}")
    else:
        if not os.path.exists(library_json):
            raise FileNotFoundError(f"{library_json} does not exist. Cannot skip scan.")
    if args.download:
        print("Warning: The --download option is deprecated is now implied. Use --skip-download to avoid downloading")
    if not args.skip_download:
        library.download_missing(args.download_limit)


if __name__ == "__main__":
    import sys

    sys.argv.append("--channel-name")
    sys.argv.append("@silverguru")
    sys.argv.append("--output")
    sys.argv.append(os.path.join(os.getcwd(), "tmp", "@silverguru", "youtube"))
    sys.argv.append("--limit-scroll-pages")
    sys.argv.append("1")
    sys.argv.append("--download-limit")
    sys.argv.append("1")
    main()
