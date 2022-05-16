"""
Tests bitchute scraper.
"""

# pylint: disable=missing-class-docstring,missing-function-docstring


import unittest

from vidcrawler.bitchute import (
    fetch_bitchute_today,
    fetch_rss_url,
    parse_rss_feed,
)
from vidcrawler.fetcher import fetch_html


class BitchuteScraperTester(unittest.TestCase):
    """Tester for bitchute."""

    def test_fetch_rss_video(self):
        rss_url = fetch_rss_url(
            channel_name="Infowars", channel_id="9c7qJvwx7YQT"
        )
        self.assertIsNotNone(rss_url)
        self.assertEqual(
            "https://www.bitchute.com/feeds/rss/channel/banned-dot-video/",
            rss_url,
        )
        content: str = fetch_html(rss_url)  # type: ignore
        feed = parse_rss_feed(content)
        self.assertIsNotNone(feed)

    def test_fetch_bitchute_today(self):
        vid_list = fetch_bitchute_today(
            channel_name="Infowars", channel_id="9c7qJvwx7YQT"
        )
        self.assertIsNotNone(vid_list)

    def test_fetch_bitchute_amazing_polly(self):
        vid_list = fetch_bitchute_today(
            channel_name="Amazing Polly", channel_id="ZofFQQoDoqYT"
        )
        self.assertTrue(vid_list)
        vid = vid_list[0]
        self.assertEqual("Amazing Polly", vid.channel_name)


if __name__ == "__main__":
    unittest.main()
