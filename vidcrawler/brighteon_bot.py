# pylint: disable=too-many-locals

"""
Scrapes the brighteon website for video urls and downloads them.
"""

import argparse
import os
import sys
import warnings

from playwright.sync_api import Page

from vidcrawler.library import Library, VidEntry
from vidcrawler.playwright_launcher import launch_playwright, set_headless

BASE_URL = "https://www.brighteon.com"

INSTALLED = False


def _fetch_vid_infos(page: Page, channel_url: str, page_num: int) -> list[VidEntry]:
    """Get the urls from a channel page. Throws exception when page not found."""
    # From: https://www.brighteon.com/channels/hrreport
    # To: https://www.brighteon.com/channels/hrreport/videos?page=1
    url = f"{channel_url}/videos?page={page_num}"
    print(f"Fetching video list from {url}")
    response = page.goto(url)
    assert response
    if response.status != 200:
        raise ValueError(f"Failed to fetch {url}, status: {response.status}")
    # get all div class="post" objects
    posts = page.query_selector_all("div.post")
    # get the first one
    vids: list[VidEntry] = []
    for post in posts:
        try:
            link = post.query_selector("a")
            assert link
            href = link.get_attribute("href")
            assert href
            title = post.query_selector("div.title")
            assert title
            title_text = title.inner_text().strip()
            href = BASE_URL + href
            vids.append(VidEntry(title=title_text, url=href))
        except Exception as e:  # pylint: disable=broad-except
            warnings.warn(f"Failed to get url: {e}")
    print(f"Found {len(vids)} videos.")
    return vids


def _update_library(outdir: str, channel_name: str, full_scan: bool, limit: int = -1) -> Library:
    """Simple test to verify the title of a page."""
    channel_url = f"https://www.brighteon.com/channels/{channel_name}"
    library_json = os.path.join(outdir, "library.json")
    library = Library(library_json)
    count = 0
    stored_vids: list[VidEntry] = library.load()
    with launch_playwright() as (page, _):
        # Determine whether to run headless based on the environment variable
        urls: list[VidEntry] = []
        page_num = 0
        while True:
            if limit > -1:
                if count >= limit:
                    break
            count += 1
            try:
                new_urls: list[VidEntry] = _fetch_vid_infos(page, channel_url, page_num)
                set_new_urls = set(new_urls)
                set_stored_vids = set(stored_vids)
                # if the new urls are fully contained in the stored vids, then we are done
                if not full_scan and (set_new_urls <= set_stored_vids):
                    warnings.warn("All the new videos are already in the library... halting scan.")
                    break
                page_num += 1
                urls += new_urls
            except Exception as e:  # pylint: disable=broad-except
                warnings.warn(f"Failed to get urls: {e}")
                break
    print(f"Got {len(urls)} urls.")
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
    parser.add_argument(
        "--limit-downloads",
        type=int,
        default=-1,
    )
    parser.add_argument(
        "--skip-download",
        action="store_true",
    )
    parser.add_argument(
        "--yt-dlp-uses-docker",
        action="store_true",
        help="Use docker to run yt-dlp",
    )
    set_headless(True)
    # full-scan
    parser.add_argument("--full-scan", action="store_true", help="Scan the entire channel, not just the new videos.")
    args = parser.parse_args()
    if args.yt_dlp_uses_docker:
        os.environ["USE_DOCKER_YT_DLP"] = "1"
    outdir = args.output
    channel = args.channel_name
    download_limit = args.limit_downloads
    skip_download = args.skip_download
    full_scan = args.full_scan

    library = _update_library(outdir, channel, full_scan=full_scan, limit=download_limit)
    if not skip_download:
        library.download_missing(download_limit)
    return 0


def unit_test(limit=-1) -> int:
    """Run the tests."""
    sys.argv.append("--channel-name")
    sys.argv.append("hrreport")
    sys.argv.append("--output")
    sys.argv.append("tmp2")
    sys.argv.append("--yt-dlp-uses-docker")
    sys.argv.append("--limit-downloads")
    sys.argv.append(str(limit))
    main()
    return 0


if __name__ == "__main__":
    sys.exit(unit_test(1))
