# pylint: disable=missing-module-docstring,missing-class-docstring,missing-function-docstring
import unittest
from datetime import datetime
from typing import Optional

from vidcrawler.date import now_local, parse_datetime
from vidcrawler.rumble import fetch_rumble, fetch_rumble_channel_today
from vidcrawler.video_info import VideoInfo


class RumbleScraperTester(unittest.TestCase):
    def test_fetch_rumble(self):
        vid_list = fetch_rumble(channel="DiamondandSilk")
        self.assertTrue(vid_list)

    def test_fetch_alt_channel_url(self):
        vid_list = fetch_rumble(channel="MaryamXHenein")
        self.assertTrue(vid_list)

    def test_fetch_bannon(self) -> None:
        max_days = 4
        vid_list = fetch_rumble_channel_today(
            channel="BannonsWarRoom", channel_name="BannonsWarRoom"
        )
        most_recent_date: Optional[datetime] = None
        vid: VideoInfo
        for vid in vid_list:
            if most_recent_date is None:
                most_recent_date = parse_datetime(vid.date_published)
                continue
            new_datetime = parse_datetime(vid.date_published)
            if new_datetime > most_recent_date:
                most_recent_date = new_datetime
        # get time delta between most recent date and now in days
        bannons_last_show_in_days: float = 9999
        if most_recent_date is not None:
            bannons_last_show_in_days = (
                now_local() - most_recent_date
            ).total_seconds() / (3600 * 24)

        self.assertLess(
            bannons_last_show_in_days,
            max_days,
            f"Bannon's last show was {bannons_last_show_in_days} days ago.",
        )


if __name__ == "__main__":
    unittest.main()
