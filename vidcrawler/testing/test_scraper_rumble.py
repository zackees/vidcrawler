# pylint: disable=missing-module-docstring,missing-class-docstring,missing-function-docstring
import unittest

from vidcrawler.rumble import fetch_rumble


class RumbleScraperTester(unittest.TestCase):
    def test_fetch_rumble(self):
        vid_list = fetch_rumble(channel="DiamondandSilk")
        self.assertTrue(vid_list)

    def test_fetch_alt_channel_url(self):
        vid_list = fetch_rumble(channel="MaryamXHenein")
        self.assertTrue(vid_list)


if __name__ == "__main__":
    unittest.main()
