"""
Tests for Playwright.
"""

import os
import unittest

from playwright.sync_api import sync_playwright

IS_GITHUB_RUNNER = os.environ.get("GITHUB_ACTIONS") == "true"


class PlaywrightTester(unittest.TestCase):
    """Tests basic functionality of Playwright."""

    @classmethod
    def setUpClass(cls):
        rtn = os.system("playwright install")
        if rtn != 0:
            raise OSError("Failed to install Playwright.")
        cls.playwright = sync_playwright().start()
        # Launch a headed browser by setting headless to False
        cls.browser = cls.playwright.chromium.launch(headless=IS_GITHUB_RUNNER)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()

    def setUp(self):
        self.page = self.browser.new_page()

    def tearDown(self):
        self.page.close()

    def test_has_title(self):
        """Simple test to verify the title of a page."""
        # Go to page google.com
        self.page.goto("https://www.google.com")
        # Get page title
        title = self.page.title()
        # Verify the title
        self.assertEqual(title, "Google")


if __name__ == "__main__":
    unittest.main()
