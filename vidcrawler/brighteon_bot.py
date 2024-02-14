"""
Scrapes the brighteon website for video urls and downloads them.
"""

import os
import sys
import warnings
from contextlib import contextmanager
from typing import Generator

from playwright.sync_api import Browser, Page, sync_playwright


def install_playwright() -> None:
    """Install Playwright."""
    rtn = os.system("playwright install")
    if rtn != 0:
        raise OSError("Failed to install Playwright.")


@contextmanager
def launch_playwright() -> Generator[tuple[Page, Browser], None, None]:
    """Playwright context manager."""
    with sync_playwright() as context:
        is_github_runner = os.environ.get("GITHUB_ACTIONS") == "true"
        browser = context.chromium.launch(headless=is_github_runner)
        page = browser.new_page()
        try:
            yield (page, browser)
        finally:
            page.close()
            browser.close()


def get_urls(page: Page, channel_url: str, page_num: int) -> list[str]:
    """Get the urls from a channel page. Throws exception when page not found."""
    # From: https://www.brighteon.com/channels/hrreport
    # To: https://www.brighteon.com/channels/hrreport/videos?page=1
    url = f"{channel_url}/videos?page={page_num}"
    page.goto(url)
    # get all div class="post" objects
    posts = page.query_selector_all("div.post")
    # get the first one
    urls: list[str] = []
    for post in posts:
        try:
            link = post.query_selector("a")
            assert link
            href = link.get_attribute("href")
            assert href
            urls.append(href)
        except Exception as e:  # pylint: disable=broad-except
            warnings.warn(f"Failed to get url: {e}")
    return urls


def unit_test() -> None:
    """Simple test to verify the title of a page."""
    chanel_url = "https://www.brighteon.com/channels/hrreport"
    with launch_playwright() as (page, _):
        # Determine whether to run headless based on the environment variable
        urls: list[str] = []
        page_num = 0
        while True:
            try:
                new_urls: list[str] = get_urls(page, chanel_url, page_num)
                page_num += 1
                urls += new_urls
            except Exception as e:  # pylint: disable=broad-except
                warnings.warn(f"Failed to get urls: {e}")
                break
        print(f"Got {len(urls)} urls.")


def main() -> int:
    """Run the tests."""
    install_playwright()
    unit_test()
    return 0


if __name__ == "__main__":
    sys.exit(main())
