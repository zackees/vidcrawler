# pylint: disable=missing-module-docstring,missing-class-docstring,missing-function-docstring

import unittest

from vidcrawler.brighteon import fetch_brighteon_today


class BrighteonScraperTester(unittest.TestCase):
    def test_fetch_brighteon_today(self):
        vid_list = fetch_brighteon_today(channel_name="hrreport", channel="hrreport")
        self.assertIsNotNone(vid_list)
        self.assertGreater(len(vid_list), 0)

        for vid in vid_list:
            self.assertIsNotNone(vid)
            # assert that the title and other elements are valid
            self.assertGreater(len(vid.title), 0)
            self.assertGreater(len(vid.url), 0)
            self.assertGreater(len(vid.img_src), 0)
            self.assertGreater(len(vid.iframe_src), 0)
            self.assertGreater(len(vid.description), 0)
            # duration should not be ?
            self.assertNotEqual(vid.duration, "?")
            self.assertGreater(len(vid.duration), 0)
            self.assertGreater(len(vid.date_published), 0)
            self.assertGreater(len(vid.date_discovered), 0)
            self.assertGreater(len(vid.date_lastupdated), 0)
            self.assertGreater(len(vid.channel_name), 0)
            self.assertGreater(len(vid.source), 0)
            self.assertGreater(len(vid.channel_url), 0)


if __name__ == "__main__":
    unittest.main()
