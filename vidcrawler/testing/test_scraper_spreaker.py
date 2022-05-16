# pylint: disable=missing-module-docstring,missing-class-docstring,missing-function-docstring

import unittest

from vidcrawler.spreaker import fetch_spreaker_today


class SpreakerScraperTest(unittest.TestCase):
    def test_fetch_spreaker(self):
        vid_list = fetch_spreaker_today("Sara Carter", "4495281")
        self.assertTrue(vid_list)


if __name__ == "__main__":
    unittest.main()
