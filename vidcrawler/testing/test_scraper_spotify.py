# pylint: disable=missing-module-docstring,missing-class-docstring,missing-function-docstring

import os
import unittest

from vidcrawler.spotify import fetch_spotify_today

RUN_ALL_TESTS = os.environ.get("RUN_ALL_TESTS", None) is not None


class SpotifyScraperTest(unittest.TestCase):
    @unittest.skipUnless(RUN_ALL_TESTS, "Spotify is not working")
    def test_joe_rogan(self):
        vid_list = fetch_spotify_today(channel_name="Joe Rogan", channel="4rOoJ6Egrf8K2IrywzwOMk")
        self.assertTrue(vid_list)


if __name__ == "__main__":
    unittest.main()
