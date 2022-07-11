# pylint: disable=missing-module-docstring,missing-class-docstring,missing-function-docstring

import re
import unittest
from typing import List

from vidcrawler.odysee import fetch_odysee_today
from vidcrawler.video_info import VideoInfo


def is_valid_url(url: str) -> bool:
    # Create a regex to match a url
    regex = r"^(?:http(s)?:\/\/)?[\w.-]+(?:\.[\w\.-]+)+[\w\-\._~:/?#[\]@!\$&'\(\)\*\+,;=.]+$"
    return re.match(regex, url) is not None


class OdyseeScraperTester(unittest.TestCase):
    def test_fetch_odysee_today(self):
        # RSS FEED:
        #   https://lbryfeed.melroy.org/channel/odysee/BretWeinstein
        vid_list: List[VideoInfo] = fetch_odysee_today(
            channel_name="BretWeinstein", channel="BretWeinstein"
        )
        self.assertGreater(len(vid_list), 0)

    def test_union_of_the_unwanted(self):
        vid_list: List[VideoInfo] = fetch_odysee_today(
            channel_name="UOTU", channel="uotuw:e"
        )
        self.assertGreater(len(vid_list), 0)

    def test_odysee_bug(self):
        # Test the fix for odysee bug:
        #   https://github.com/zackees/blast.video/issues/1
        vid_list: List[VideoInfo] = fetch_odysee_today(
            channel_name="The Ripple Effect", channel="therippleeffectpodcast"
        )
        self.assertGreater(len(vid_list), 0)
        for vid in vid_list:
            self.assertEqual(vid.channel_name, "The Ripple Effect")
            self.assertTrue(
                is_valid_url(vid.img_src), f'"{vid.img_src}" is not a valid url'
            )


if __name__ == "__main__":
    unittest.main()
