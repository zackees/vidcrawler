"""
Command entry point.
"""

# pylint: disable=consider-using-f-string

import argparse
import json
import os

from vidcrawler.youtube_bot import YtVid, fetch_all_vids


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser("youtube-pull")
    parser.add_argument(
        "channel_url",
        type=str,
        help="URL of the channel, example: https://www.youtube.com/@silverguru/videos",
    )
    parser.add_argument("output_dir", type=str)
    return parser.parse_args()


def main() -> None:
    """Main function."""
    args = parse_args()
    channel_url = args.channel_url
    output_dir = args.output_dir
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    vids: list[YtVid] = fetch_all_vids(channel_url)
    data = [vid.to_dict() for vid in vids]
    out_str = json.dumps(data, indent=2)
    output_json = os.path.join(output_dir, "vids.json")
    with open(output_json, encoding="utf-8", mode="w") as filed:
        filed.write(out_str)
    print(f"Output written to {output_json}")


if __name__ == "__main__":
    import sys

    sys.argv.append("https://www.youtube.com/@silverguru/videos")
    sys.argv.append("tmp")
    main()
