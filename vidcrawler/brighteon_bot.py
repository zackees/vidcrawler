"""
Scrapes the brighteon website for video urls and downloads them.
"""

import argparse
import os
import sys
import warnings
from contextlib import contextmanager
from typing import Generator

from filelock import FileLock
from playwright.sync_api import Browser, Page, sync_playwright

from vidcrawler.library import Library, VidEntry

BASE_URL = "https://www.brighteon.com"

INSTALLED = False


def install_playwright() -> None:
    """Install Playwright."""
    install_lock = os.path.join(os.getcwd(), "playwright.lock")
    with FileLock(install_lock):
        global INSTALLED  # pylint: disable=global-statement
        if INSTALLED:
            return
        rtn = os.system("playwright install")
        if rtn != 0:
            raise OSError("Failed to install Playwright.")
        INSTALLED = True


@contextmanager
def launch_playwright() -> Generator[tuple[Page, Browser], None, None]:
    """Playwright context manager."""
    install_playwright()
    with sync_playwright() as context:
        is_github_runner = os.environ.get("GITHUB_ACTIONS") == "true"
        browser = context.chromium.launch(headless=is_github_runner)
        page = browser.new_page()
        try:
            yield (page, browser)
        finally:
            page.close()
            browser.close()


def get_vids(page: Page, channel_url: str, page_num: int) -> list[VidEntry]:
    """Get the urls from a channel page. Throws exception when page not found."""
    # From: https://www.brighteon.com/channels/hrreport
    # To: https://www.brighteon.com/channels/hrreport/videos?page=1
    url = f"{channel_url}/videos?page={page_num}"
    page.goto(url)
    # get all div class="post" objects
    posts = page.query_selector_all("div.post")
    # get the first one
    urls: list[VidEntry] = []
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
            urls.append(VidEntry(title=title_text, url=href))
        except Exception as e:  # pylint: disable=broad-except
            warnings.warn(f"Failed to get url: {e}")
    return urls


def update_library(outdir: str, channel_name: str, limit: int = -1) -> Library:
    """Simple test to verify the title of a page."""
    channel_url = f"https://www.brighteon.com/channels/{channel_name}"
    library_json = os.path.join(outdir, channel_name, "brighteon", "library.json")
    library = Library(library_json)
    count = 0
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
                new_urls: list[VidEntry] = get_vids(page, channel_url, page_num)
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
    parser = argparse.ArgumentParser("brighteon-pull")
    parser.add_argument(
        "channel",
        type=str,
        help="URL slug of the channel, example: hrreport",
    )
    parser.add_argument("basedir", type=str, help="Base directory", default=".")
    parser.add_argument(
        "--limit-downloads",
        type=int,
        default=-1,
    )
    parser.add_argument(
        "--skip-download",
        action="store_true",
    )
    args = parser.parse_args()
    basedir = args.basedir
    channel = args.channel
    download_limit = args.limit_downloads
    skip_download = args.skip_download

    library = update_library(basedir, channel, limit=-1)
    if not skip_download:
        library.download_missing(download_limit)
    return 0


def unit_test(limit=-1) -> int:
    """Run the tests."""
    sys.argv.append("hrreport")
    sys.argv.append("tmp")
    sys.argv.append("--limit-downloads")
    sys.argv.append(str(limit))
    main()
    return 0


if __name__ == "__main__":
    sys.exit(unit_test(1))
