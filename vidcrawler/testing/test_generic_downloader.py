# pylint: disable=missing-class-docstring,missing-function-docstring,missing-module-docstring

"""
Testing generic downloader
"""

import unittest

from vidcrawler.generic_downloader import fetch_all_videos_in_channel
from vidcrawler.types import ChannelId


class GenericDownloadTester(unittest.TestCase):
    def test_env(self):  # pylint: disable
        vidlist = fetch_all_videos_in_channel("youtube", ChannelId("UCiuTGTCkYrjVknhvMAICFjA"))
        self.assertGreater(len(vidlist), 0)


if __name__ == "__main__":
    unittest.main()
