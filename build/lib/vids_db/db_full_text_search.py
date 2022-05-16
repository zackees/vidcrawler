"""
    Implements a full text search engine.
"""

import os
from datetime import datetime
from typing import List

import pytz  # type: ignore
from whoosh import fields  # type: ignore
from whoosh.analysis import FancyAnalyzer  # type: ignore
from whoosh.compat import u  # type: ignore
from whoosh.filedb.filestore import FileStorage  # type: ignore
from whoosh.qparser import QueryParser  # type: ignore
from whoosh.qparser.dateparse import DateParserPlugin  # type: ignore

from vidcrawler.models import Video

SCHEMA = fields.Schema(
    url=fields.ID(stored=True, unique=True, sortable=True),
    channel_name=fields.TEXT(
        stored=True, chars=True, vector=True, analyzer=FancyAnalyzer()
    ),
    date=fields.DATETIME(stored=True, sortable=True),
    # title=fields.TEXT(
    #    stored=True, chars=True, vector=True, analyzer=FancyAnalyzer()
    # ),
    title=fields.NGRAMWORDS(stored=True, minsize=3),
    views=fields.NUMERIC(stored=True, sortable=True, bits=64),
)


def _filter_out_duplicate_videos(videos: List[Video]) -> List[Video]:
    found_urls = set()
    filtered_videos = []
    for video in videos:
        if video.url in found_urls:
            continue
        found_urls.add(video.url)
        filtered_videos.append(video)
    if len(filtered_videos) != len(videos):
        print(
            f"Filtered out {len(videos) - len(filtered_videos)} duplicate videos."
        )
    return filtered_videos


class DbFullTextSearch:
    """Impelmentation of a full text search database."""

    def __init__(self, index_path) -> None:
        """Initialize the database."""
        self.storage = FileStorage(index_path)
        if self.storage.index_exists():
            self.index = self.storage.open_index()
        else:
            os.makedirs(index_path, exist_ok=True)
            self.index = self.storage.create_index(SCHEMA)

    def clear(self) -> None:  # pylint: disable=no-self-use
        """Clear the database."""
        # TODO: Implement this.  # pylint: disable=W0511
        return

    def add_videos(self, videos: List[Video]) -> None:
        """Add videos to the database."""
        videos = _filter_out_duplicate_videos(videos)
        with self.index.writer() as writer:
            with writer.group():
                for vid in videos:
                    published: datetime = vid.date_published
                    # Change published datetime to utc timezone.
                    published_utc = published.astimezone(pytz.utc)
                    writer.update_document(
                        url=vid.url,
                        channel_name=u(vid.channel_name),
                        date=published_utc,
                        title=u(vid.title),
                        views=vid.views,
                    )

    def _field_search(
        self, field_name: str, query_string: str, limit: int = 40
    ) -> List[dict]:
        """Searcher for videos by one of the fields."""
        qparser = QueryParser(field_name, schema=SCHEMA)
        qparser.add_plugin(DateParserPlugin(free=False))
        qry = qparser.parse(query_string)
        with self.index.searcher() as searcher:
            # matcher = query.matcher(searcher)  # useful for debugging
            results = searcher.search(qry, mask=None, limit=limit, terms=True)
            # Convert the results to dicts.
            results_dicts = []
            for result in results:
                results_dicts.append(
                    {
                        "url": result["url"],
                        "channel_name": result["channel_name"],
                        "date": result["date"],
                        "title": result["title"],
                        "views": result["views"],
                    }
                )
            return results_dicts

    def title_search(self, query_string: str, limit: int = 40) -> List[dict]:
        """Searcher for videos by title."""
        return self._field_search("title", query_string, limit)

    def channel_search(self, query_string: str, limit: int = 40) -> List[dict]:
        """Searcher for videos by title."""
        return self._field_search("channel_name", query_string, limit)
