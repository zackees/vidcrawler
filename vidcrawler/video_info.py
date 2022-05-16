"""
VideoInfo object used to store information about a video.
"""

# pylint: disable=line-too-long,missing-function-docstring,consider-using-f-string,too-many-locals,invalid-name,no-else-return,too-many-instance-attributes

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set

from .date import iso_fmt, now_local, parse_datetime


@dataclass
class VideoInfo:
    """Object used to hold information about a video."""

    channel_name: str = ""
    title: str = ""
    date_published: str = ""  # from the scraped website
    date_discovered: str = ""  # generated during scrape
    date_lastupdated: str = ""
    channel_url: str = ""
    source: str = ""
    url: str = ""
    duration: str = ""  # units = seconds.
    description: str = ""
    img_src: str = ""
    img_status: int = -1
    img_width: int = -1
    img_height: int = -1
    iframe_src: str = ""
    views: str = ""
    profile_img_src: str = ""
    subtitles_url: str = ""
    rank: Optional[float] = None  # optional stdev rank.

    def to_dict(self) -> Dict:
        """Generates a dictionary representing this class instance."""
        out = {
            "channel_name": self.channel_name,
            "title": self.title,
            "date_published": self.date_published,
            "date_discovered": self.date_discovered,
            "date_lastupdated": self.date_lastupdated,
            "channel_url": self.channel_url,
            "source": self.source,
            "url": self.url,
            "duration": self.duration,
            "description": self.description,
            "img_src": self.img_src,
            "img_status": self.img_status,
            "img_width": self.img_width,
            "img_height": self.img_height,
            "iframe_src": self.iframe_src,
            "views": self.views,
            "profile_img_src": self.profile_img_src,
            "subtitles_url": self.subtitles_url,
        }
        if self.rank is not None:
            # parse float to two decimal places
            out["rank"] = round(self.rank, 2)
        return out

    @classmethod
    def from_json_str(cls, data: str) -> VideoInfo:
        """Deserializes from dictionary json str back to VideoInfo"""
        d = json.loads(data)
        return VideoInfo.from_dict(d)

    @classmethod
    def from_dict(cls, data: Dict) -> VideoInfo:
        """Deserializes from dictionary back to VideoInfo"""
        views = _parse_views(data["views"])
        return VideoInfo(
            channel_name=data["channel_name"],
            title=data["title"],
            date_published=iso_fmt(data["date_published"]),
            date_discovered=iso_fmt(data["date_discovered"]),
            date_lastupdated=iso_fmt(data["date_lastupdated"]),
            channel_url=data["channel_url"],
            source=data["source"],
            url=data["url"],
            duration=data["duration"],
            description=data["description"],
            img_src=data["img_src"],
            # img_width, img_height, status were added recently, and therefore are optional.
            img_status=data.get("img_status", -1),
            img_width=data.get("img_width", -1),
            img_height=data.get("img_height", -1),
            iframe_src=data["iframe_src"],
            views=views,
            profile_img_src=data["profile_img_src"],
            subtitles_url=data.get("subtitles_url", ""),
            rank=data.get("rank", None),
        )

    @classmethod
    def from_list_of_dicts(cls, data: List[Dict]) -> List[VideoInfo]:
        out: List[VideoInfo] = []
        for datum in data:
            vi = VideoInfo.from_dict(datum)
            out.append(vi)
        return out

    @classmethod
    def to_plain_list(cls, data: List[VideoInfo]) -> List[Dict]:
        out = []
        vid_info: VideoInfo
        for vid_info in data:
            d = vid_info.to_dict()
            out.append(d)
        return out

    @classmethod
    def to_compact_csv(
        cls,
        vid_list: List[VideoInfo],
        exclude_columns: Optional[Set[str]] = None,
    ) -> List[List]:
        """
        Generates a compact csv form of the data. The csv form consists of a header list, followed by N data
        lists. This has the advantage of eliminating the redundant keys in the dictionary form, which helps
        reduce the size of the file over the wire.
        """
        columns_set: Set[str] = set({})
        for vid in vid_list:
            vid_dict = vid.to_dict()
            for key in vid_dict.keys():
                columns_set.add(key)
        if exclude_columns:
            columns_set = columns_set - exclude_columns
        exclude_columns = exclude_columns or set({})
        columns = sorted(list(columns_set))
        out: List[Any] = []
        # Create the header for the csv
        out.append(columns)
        for vid in vid_list:
            vid_dict = vid.to_dict()
            row = []
            for col in columns:
                val = vid_dict.get(col, "")
                row.append(val)
            out.append(row)
        return out

    @classmethod
    def from_compact_csv(cls, csv_list: List[List]) -> List[VideoInfo]:
        """
        Generates a compact csv form of the data. The csv form consists of a header list, followed by N data
        lists. This has the advantage of eliminating the redundant keys in the dictionary form, which helps
        reduce the size of the file over the wire.
        """
        if len(csv_list) == 0:
            return []
        # Header line is the key list
        key_list: List = [e.strip() for e in csv_list[0]]
        out: List[VideoInfo] = []
        # Go through the rest of the list and and construct the data, using the key_list
        # as the schema to build out the output list of VideoInfo.
        for datum in csv_list[1:]:
            vi: VideoInfo = VideoInfo()
            d = vi.to_dict()
            for i, key in enumerate(key_list):
                d[key] = datum[i]
            out.append(VideoInfo.from_dict(d))
        return out

    def video_age_seconds(self, now_time: Optional[datetime] = None) -> float:
        """
        Returns the date published as a datetime object.
        """
        now_time = now_time or now_local()
        diff: timedelta = now_time - parse_datetime(self.date_published)
        return diff.total_seconds()

    # Set operations like intersection, union, etc are nice to have.
    # This needs hash, eq, and ne.
    def __hash__(self):
        return hash(self.channel_name + self.title)

    def __eq__(self, other):
        return (self.channel_name, self.title) == (
            other.channel_name,
            other.title,
        )

    def __ne__(self, other):
        # Not strictly necessary, but to avoid having both x==y and x!=y
        # True at the same time
        return not (self == other)  # pylint: disable=superfluous-parens


def _parse_views(view_str: str) -> str:
    try:
        if view_str == "?":
            return view_str
        if view_str == "":
            return "0"
        multiplier = 1
        view_str = str(view_str).upper().replace(",", "")
        if "K" in view_str:
            view_str = view_str.replace("K", "")
            multiplier = 1000
        elif "M" in view_str:
            view_str = view_str.replace("M", "")
            multiplier = 1000 * 1000
    except BaseException as e:  # pylint: disable=broad-except
        print(e)
    return str(int(float(view_str) * multiplier))


def test() -> None:
    url: str = "2021-03-29 01:13:15+00:00"
    d: Any = parse_datetime(url)
    print(f'"{d.isoformat()}"')


if __name__ == "__main__":
    test()
