# pylint: disable=missing-module-docstring,missing-class-docstring,missing-function-docstring

import unittest
from typing import List

from vidcrawler.gabtv import fetch_gabtv_today, fetch_views
from vidcrawler.video_info import VideoInfo


class GabTvTester(unittest.TestCase):
    def test_fetch_gabtv_views(self):
        """Tests that we can fetch views."""
        views = fetch_views(channel="LadyBee")
        self.assertGreater(len(views), 0)

    def test_fetch_gabtv_today(self):
        vid_list: List[VideoInfo] = fetch_gabtv_today(
            channel_name="Maryam Henein", channel_id="LadyBee"
        )
        self.assertGreater(len(vid_list), 0)


if __name__ == "__main__":
    unittest.main()
