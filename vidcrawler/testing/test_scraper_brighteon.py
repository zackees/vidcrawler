# pylint: disable=missing-module-docstring,missing-class-docstring,missing-function-docstring

import unittest

from vidcrawler.brighteon import fetch_brighteon_today


class BrighteonScraperTester(unittest.TestCase):
    def test_fetch_brighteon_today(self):
        vid_list = fetch_brighteon_today(
            channel_name="brendon", channel="brendon"
        )
        self.assertIsNotNone(vid_list)


if __name__ == "__main__":
    unittest.main()
