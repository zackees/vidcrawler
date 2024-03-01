# pylint: disable=R0801

import argparse
import os
import sys

from vidcrawler.library import Library, VidEntry
from vidcrawler.rumble import PartialVideo, fetch_rumble_channel_all_partial_result


def _update_library(outdir: str, channel_name: str) -> Library:
    # channel_url = f"https://www.brighteon.com/channels/{channel_name}"
    library_json = os.path.join(outdir, "library.json")
    videos: list[PartialVideo] = fetch_rumble_channel_all_partial_result(
        channel_name=channel_name,
        channel=channel_name,
        after=None,
    )
    urls: list[VidEntry] = [VidEntry(url=vid.url, title=vid.title, date=vid.date) for vid in videos]
    library = Library(library_json)
    library.merge(urls)
    return library


def main() -> int:
    """Main function."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--channel-name",
        type=str,
        help="URL slug of the channel, example: hrreport",
        required=True,
    )
    parser.add_argument("--output", type=str, help="Output directory", required=True)
    # full-scan
    parser.add_argument("--skip-download", action="store_true", help="Skip downloading")
    args = parser.parse_args()
    outdir = args.output
    channel = args.channel_name

    library = _update_library(outdir, channel)
    print(f"Updated library {library.library_json_path}")
    if not args.skip_download:
        library.download_missing()
    return 0


def unit_test() -> int:
    """Run the tests."""
    sys.argv.append("--channel-name")
    sys.argv.append("PlandemicSeriesOfficial")
    sys.argv.append("--output")
    sys.argv.append("tmp3")
    sys.argv.append("--skip-download")
    main()
    return 0


if __name__ == "__main__":
    sys.exit(unit_test())
