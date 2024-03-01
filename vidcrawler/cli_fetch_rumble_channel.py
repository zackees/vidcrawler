"""
Command line interface for fetching rumble channel
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from vidcrawler.date import parse_datetime
from vidcrawler.rumble import PartialVideo, fetch_rumble_channel_all_partial_result


def main() -> int:
    """Command line interface for fetching rumble channel."""
    parser = argparse.ArgumentParser(description="Fetch rumble channel.")
    parser.add_argument("--channel", help="Channel ID.", required=True)
    # add after date
    parser.add_argument("--after-date", help="Fetch videos after this date.", default=None)
    # add --output-json
    parser.add_argument("--output-json", help="Output to this file.", default=None)
    args = parser.parse_args()
    after_date: datetime | None = None
    if args.after_date:
        after_date = parse_datetime(args.after_date)
    vid_list: list[PartialVideo] = fetch_rumble_channel_all_partial_result(
        channel_name=args.channel,
        channel=args.channel,
        after=after_date,
    )
    vid_dict_list = [vid.to_dict() for vid in vid_list]
    json_data = json.dumps(vid_dict_list, indent=2)
    if args.output_json:
        # convert to json dict
        output_json = Path(args.output_json)
        output_json.write_text(json_data, encoding="utf-8")
    else:
        print(json_data)
    return 0


if __name__ == "__main__":
    sys.argv.append("--channel")
    sys.argv.append("PlandemicSeriesOfficial")
    sys.exit(main())
