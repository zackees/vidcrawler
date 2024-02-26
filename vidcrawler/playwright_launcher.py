"""
Launches playwright and sets up all the defaults.
"""

import os
from contextlib import contextmanager
from typing import Generator

from filelock import FileLock
from playwright.sync_api import Browser, Page, sync_playwright

INSTALLED = False
HEADLESS = True


def set_headless(headless: bool) -> None:
    """Set headless."""
    global HEADLESS  # pylint: disable=global-statement
    HEADLESS = headless


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
def launch_playwright(timeout_seconds: float = 300) -> Generator[tuple[Page, Browser], None, None]:
    """
    Launches a playwright browser. Each browser is only safe to use in a single thread.
    """
    install_playwright()
    with sync_playwright() as context:
        # add timeout to context
        headless = HEADLESS or os.environ.get("GITHUB_ACTIONS") == "true"
        browser = context.chromium.launch(headless=headless, timeout=timeout_seconds * 1000)
        page = browser.new_page()
        try:
            yield (page, browser)
        finally:
            page.close()
            browser.close()
