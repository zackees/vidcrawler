# pylint: disable=all

import unittest
from typing import List

from vidcrawler.date import now_local
from vidcrawler.video_info import VideoInfo


class VideoInfoTester(unittest.TestCase):
    def test_one(self) -> None:
        now_str = str(now_local().isoformat())
        vid_list = []
        vi = VideoInfo()
        vi.title = "test_channel"
        vi.img_src = "https://example.com/img_src.png"
        vi.description = "My video description"
        vi.iframe_src = "https://example/123/player.html"
        vi.duration = "1:03:53"
        vi.views = "1000"
        vi.date_published = "2021-12-21T03:30:19+00:00"
        vi.channel_url = "https://rumble.com/c/PeteSantilliInterviews"
        vi.channel_name = "Pete Santilli Interviews"
        vi.date_published = now_str
        vi.date_discovered = now_str
        vi.date_lastupdated = now_str
        vid_list.append(vi)
        data: List[List] = VideoInfo.to_compact_csv(vid_list)
        vid_list2: List[VideoInfo] = VideoInfo.from_compact_csv(data)
        vi2: VideoInfo = vid_list2[0]
        self.assertEqual(vi, vi2)


if __name__ == "__main__":
    unittest.main()
