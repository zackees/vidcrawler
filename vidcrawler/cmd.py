"""
Command entry point.
"""

# pylint: disable=consider-using-f-string

import argparse
import json
import os
import time

from vidcrawler.spider import CRAWLER_MAP, crawl_video_sites

CRAWLERS = CRAWLER_MAP.keys()


def main() -> None:
    """Main function."""
    parser = argparse.ArgumentParser("vidcrawler")
    parser.add_argument("--input_crawl_json", type=str)
    parser.add_argument("--output_json", type=str)
    parser.add_argument("--singlethreaded", action="store_true")
    args = parser.parse_args()
    input_crawl_json = args.input_crawl_json or input("input_crawl_json: ")
    assert os.path.exists(input_crawl_json), f"{input_crawl_json} doesn't exist"
    output_json = args.output_json or input("output_json: ")
    with open(input_crawl_json, encoding="utf-8", mode="r") as filed:
        input_crawl_data = json.loads(filed.read())
    # Type check! We expect an array of tuples
    # List[Tuple[str, str, str]]
    tmp = []
    for tup in input_crawl_data:
        assert len(tup) == 3, "expected a List[Tuple[str, str, str]]"
        if tup[1] not in CRAWLERS:
            print(f"Unknown source: {tup[1]} (ignoring)")
            continue
        tmp.append(tup)
    input_crawl_data = tmp
    # Execute the crawl
    time_start = time.time()
    json_str: str = crawl_video_sites(
        input_crawl_data, use_threads=not args.singlethreaded
    )
    time_delta = time.time() - time_start
    print("\nTook %.1f seconds to fetch content\n" % time_delta)
    with open(output_json, encoding="utf-8", mode="w") as filed:
        filed.write(json_str)
