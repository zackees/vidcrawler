# pylint: disable=all

import json
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional

from vidcrawler.models import Video

TABLE_NAME = "videos"

CREATE_STMT: str = "\n".join(
    [
        "PRAGMA journal_mode=wal2;",
        f"CREATE TABLE {TABLE_NAME} (",
        "   url TEXT PRIMARY KEY UNIQUE NOT NULL,",
        "   channel_name TEXT,",
        "   timestamp_published INT,",
        "   data TEXT);",
        f"CREATE INDEX index_channel_name ON {TABLE_NAME}(channel_name);",
        f"CREATE INDEX timestamp_published ON {TABLE_NAME}(channel_name);",
    ]
)

INSERT_STMT = "\n".join(
    [
        f"INSERT OR REPLACE INTO {TABLE_NAME} (",
        "    url,",
        "    channel_name,",
        "    timestamp_published,",
        "    data",
        ") VALUES (?, ?, ?, ?)",
    ]
)


class DbSqliteVideo:
    """SQLite3 context manager"""

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        folder_path = os.path.dirname(self.db_path)
        os.makedirs(folder_path, exist_ok=True)
        if self.db_path == "" or self.db_path == ":memory:":
            raise ValueError("Can not use in memory database for DbSqliteVideo")
        self.create_table()

    def create_table(self) -> None:
        with self.open_db_for_write() as conn:
            # Check to see if it's exists first of all.
            check_table_stmt = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{TABLE_NAME}';"
            cursor = conn.execute(check_table_stmt)
            has_table = cursor.fetchall()
            if has_table:
                return
        with self.open_db_for_write() as conn:
            try:
                conn.executescript(CREATE_STMT)
            except sqlite3.ProgrammingError:
                pass  # Table already created

    def clear(self) -> None:
        with self.open_db_for_write() as conn:
            conn.execute(f"DELETE FROM {TABLE_NAME}")
            conn.commit()

    @contextmanager
    def open_db_for_write(self):
        try:
            conn = sqlite3.connect(
                self.db_path, check_same_thread=False, timeout=10
            )
        except sqlite3.OperationalError as e:
            raise OSError(
                "Error while opening %s\nOriginal Error: %s" % (self.db_path, e)
            )
        try:
            yield conn
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    @contextmanager
    def open_db_for_read(self):
        try:
            conn = sqlite3.connect(
                self.db_path, check_same_thread=False, timeout=10
            )
        except sqlite3.OperationalError as e:
            raise OSError(
                "Error while opening %s\nOriginal Error: %s" % (self.db_path, e)
            )
        try:
            yield conn
        finally:
            conn.close()

    def insert_or_update(self, vids: List[Video]) -> None:
        records = []
        for vid in vids:
            # Convert datetime to unix timestamp
            timestamp_published = int(vid.date_published.timestamp())
            json_data = vid.to_json_str()
            record = (
                vid.url,
                vid.channel_name,
                timestamp_published,
                json_data,
            )
            records.append(record)
        with self.open_db_for_write() as conn:
            conn.executemany(INSERT_STMT, records)
            conn.commit()

    def get_channel_names(self) -> List[str]:
        select_stmt = f"SELECT DISTINCT channel_name FROM {TABLE_NAME}"
        output: List[str] = []
        with self.open_db_for_read() as conn:
            cursor = conn.execute(select_stmt)
            for row in cursor:
                output.append(row[0])
        return output

    def remove_by_channel_name(self, channel_name: str) -> None:
        with self.open_db_for_write() as conn:
            conn.execute(
                f"DELETE FROM {TABLE_NAME} WHERE channel_name=(?)",
                (channel_name,),
            )
            conn.commit()

    def find_videos_by_channel_name(self, channel_name: str) -> List[Video]:
        select_stmt = f"SELECT data FROM {TABLE_NAME} WHERE channel_name=(?)"
        output: List[str] = []
        with self.open_db_for_read() as conn:
            cursor = conn.execute(select_stmt, (channel_name,))
            for row in cursor:
                output.append(row[0])
        return [Video(**json.loads(s)) for s in output]

    def find_videos_by_urls(self, urls: List[str]) -> List[Video]:
        outlist: List[Video] = []
        select_stmt = f"SELECT data FROM {TABLE_NAME} WHERE url=(?)"
        with self.open_db_for_read() as conn:
            for url in urls:
                cursor = conn.execute(select_stmt, (url,))
                for row in cursor:
                    data: Dict = json.loads(row[0])
                    out: Video = Video(**data)
                    outlist.append(out)
                    break
        return outlist

    def find_video_by_url(self, url: str) -> Optional[Video]:
        vids = self.find_videos_by_urls([url])
        return vids[0] if vids else None

    def find_videos(
        self,
        date_start: datetime,
        date_end: datetime,
        channel_name: Optional[str] = None,
        limit_count: Optional[int] = None,
    ) -> List[Video]:
        output: List[Video] = []
        from_time = int(date_start.timestamp())
        to_time = int(date_end.timestamp())
        if limit_count is not None:
            limit_clause = f"LIMIT {limit_count}"
        else:
            limit_clause = ""
        if channel_name is None:
            select_stmt = (
                f"SELECT data FROM {TABLE_NAME} WHERE timestamp_published BETWEEN ? AND ?"
                f" ORDER BY timestamp_published DESC {limit_clause};"
            )
            values = (from_time, to_time)  # type: ignore
        else:
            select_stmt = (
                f"SELECT data FROM {TABLE_NAME} WHERE channel_name=(?) and"
                " timestamp_published BETWEEN ? AND ?"
                f" ORDER BY timestamp_published DESC {limit_clause};"
            )
            values = (channel_name, from_time, to_time)  # type: ignore
        with self.open_db_for_read() as conn:  # TODO: have a read-mode.
            cursor = conn.execute(select_stmt, values)
            all_rows = cursor.fetchall()
        for row in all_rows:
            json_data = row[0]
            data = json.loads(json_data)
            vid = Video(**data)
            output.append(vid)
        return output

    def get_all_videos(self) -> List[Video]:
        select_stmt = f"SELECT data FROM {TABLE_NAME}"
        output: List[str] = []
        with self.open_db_for_read() as conn:
            cursor = conn.execute(select_stmt)
            for row in cursor:
                output.append(row[0])
        return [Video(**json.loads(s)) for s in output]

    def to_data(self) -> List[Any]:
        out = []
        select_stmt = f"SELECT * FROM {TABLE_NAME}"
        with self.open_db_for_read() as conn:
            cursor = conn.execute(select_stmt)
            for row in cursor:
                values = list(row)  # Copy
                out.append(values)
        return out
