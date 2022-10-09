# pylint: disable=all
import os
import tempfile
import unittest
from typing import List

import requests
from vidcrawler.fetch_html import fetch_html
from vidcrawler.video_info import VideoInfo
from vidcrawler.youtube import fetch_youtube_today, parse_youtube_video


class YouTubeScraperTester(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cleanup = []

    def tearDown(self):
        for cleanup in self.cleanup:
            try:
                cleanup()
            except BaseException as be:  # pylint: disable=broad-except
                print(str(be))
        self.cleanup = []

    def create_tempfile_path(self) -> str:
        tmp_file = tempfile.NamedTemporaryFile(suffix=".sqlite3", delete=False)
        tmp_file.close()
        self.cleanup.append(lambda: os.remove(tmp_file.name))
        return os.path.abspath(tmp_file.name)

    def test_fetch_video_info(self):
        url: str = "https://www.youtube.com/watch?v=5nBqIK0mrFI"
        content: str = fetch_html(url)
        d = parse_youtube_video(content)
        self.assertEqual("False", d["is_live"])
        self.assertEqual(
            "https://yt3.ggpht.com/ytc/AMLnZu8YcoqIA7-FfOC0tEwMjTDflDpiMjnJT6GvCXjunw=s176-c-k-c0x00ffffff-no-rj",
            d["profile_thumbnail"],
        )

    def test_bad_content(self):
        """Stephan Molynuex is banned. This should produce an error."""
        try:
            fetch_youtube_today(
                channel_name="Stefan Molynuex",
                channel_id="UCC3L8QaxqEGUiBC252GHy3w",
                cache_path=None,
            )
        except OSError:
            return  # expected result.
        self.fail("Expected bad channel to raise exception.")

    def test_maryam_henein(self):
        out: List[VideoInfo] = fetch_youtube_today(
            channel_name="Maryam Henein",
            channel_id="UCkw3pE7PwWfQCFFP2YgKVIQ",
            cache_path=None,
            limit=1,
        )
        self.assertEqual(len(out), 1)

    def test_lex_freemond(self):
        out: List[VideoInfo] = fetch_youtube_today(
            channel_name="Lex Fridman",
            channel_id="UCSHZKyawb77ixDdsGog4iWA",
            cache_path=None,
            limit=1,
        )
        self.assertEqual(len(out), 1)

    def test_fetch_channel_via_html(self):
        out = fetch_youtube_today(
            channel_name="Maryam Henein",
            channel_id="UCkw3pE7PwWfQCFFP2YgKVIQ",
            cache_path=None,
            limit=1,
        )
        self.assertEqual(len(out), 1)

    def test_video_xml_api(self):
        """Tests a major entry point used by the scraper to get YT vids."""
        # Links to tim pool channel.
        url = "https://www.youtube.com/feeds/videos.xml?channel_id=UCG749Dj4V2fKa143f8sE60Q"
        response = requests.get(url)
        # Raise error if 404 or other error condition.
        response.raise_for_status()


if __name__ == "__main__":
    unittest.main()
