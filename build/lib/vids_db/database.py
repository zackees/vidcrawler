# pylint: disable=all
import os
from datetime import datetime
from typing import List, Optional

from vidcrawler.db_full_text_search import DbFullTextSearch
from vidcrawler.db_sqlite_video import DbSqliteVideo  # type: ignore
from vidcrawler.models import Video

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(HERE)
DB_PATH_DIR = os.path.join(PROJECT_ROOT, "data")

FULL_TEXT_SEARCH_ENABLED = (
    os.environ.get("FULL_TEXT_SEARCH_ENABLED", "0") == "1"
)


class Database:
    def __init__(self, db_path: Optional[str] = None) -> None:
        db_path = db_path or DB_PATH_DIR
        os.makedirs(db_path, exist_ok=True)
        self.db_path = db_path
        db_path_sqlite = os.path.join(db_path, "videos.sqlite")
        self.db_full_text_search = None
        full_text_enabled = (
            os.environ.get("FULL_TEXT_SEARCH_ENABLED", "0") == "1"
        )
        if full_text_enabled:
            db_path_fts = os.path.join(db_path, "full_text_seach")
            self.db_full_text_search = DbFullTextSearch(db_path_fts)
        self.db_sqlite = DbSqliteVideo(db_path_sqlite)

    def clear(self) -> None:
        self.db_sqlite.clear()
        if self.db_full_text_search:
            self.db_full_text_search.clear()

    def update_many(self, vids: List[Video]) -> None:  # type: ignore
        self.db_sqlite.insert_or_update(vids)
        if self.db_full_text_search:
            self.db_full_text_search.add_videos(vids)

    def update(self, vid: Video) -> None:
        self.update_many([vid])

    def get_channel_names(self) -> List[str]:
        return self.db_sqlite.get_channel_names()

    def remove_by_channel_name(self, channel_name: str) -> None:
        self.db_sqlite.remove_by_channel_name(channel_name)

    def get_video_list(
        self,
        date_start: datetime,
        date_end: datetime,
        channel_name: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Video]:
        vid_list: List[Video] = self.db_sqlite.find_videos(
            date_start, date_end, channel_name=channel_name, limit_count=limit
        )
        return vid_list

    def query_video_list(
        self,
        query_string: str,
        limit: Optional[int] = None,
    ) -> List[Video]:
        if not self.db_full_text_search:
            return []
        options = {}
        if limit is not None:
            options["limit"] = limit
        vids0: List[dict] = self.db_full_text_search.channel_search(
            query_string, **options
        )
        vids1: List[dict] = self.db_full_text_search.title_search(
            query_string, **options
        )
        vid_list = vids0 + vids1
        found_urls = set()
        filtered_vids = []
        for vid in vid_list:
            if vid["url"] in found_urls:
                continue
            found_urls.add(vid["url"])
            filtered_vids.append(vid)
        if limit is not None:
            filtered_vids = filtered_vids[:limit]

        urls = [v["url"] for v in filtered_vids]
        vids = self.db_sqlite.find_videos_by_urls(urls)
        return vids
