# pylint: disable=all
# flake8: noqa

import unittest

from vidcrawler.youtube_bot import (
    VidEntry,
    fetch_all_sources,
    fetch_all_vids,
    parse_youtube_videos,
)

URL_SILVERGURU = "https://www.youtube.com/@silverguru/videos"


class YouTubeBotTester(unittest.TestCase):
    def test_fetch_sources(self) -> None:
        sources = list(fetch_all_sources(URL_SILVERGURU, limit=1))
        print("sources:")
        # for source in sources:
        #    print(f"  {source}")
        vids: list[VidEntry] = parse_youtube_videos(sources)
        self.assertGreater(len(vids), 0)
        print("vids:")
        for vid in vids:
            print(f"  {vid}")

    def test_fetch_videos(self) -> None:
        # vids = fetch_all_vids(URL_SILVERGURU)
        sources: list[VidEntry] = fetch_all_vids(URL_SILVERGURU, limit=4)
        print("vids:")
        for vid in sources:
            print(f"  {vid}")
        self.assertGreater(len(sources), 0)


if __name__ == "__main__":
    unittest.main()
