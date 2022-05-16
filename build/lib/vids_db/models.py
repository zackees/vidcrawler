# disable pylint for the entire file
# pylint: disable=all

from __future__ import annotations

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union

from pydantic import (
    AnyUrl,
    BaseModel,
    NonNegativeFloat,
    NonNegativeInt,
    constr,
    validator,
)

from vidcrawler.date import iso_fmt, parse_datetime


def parse_duration(duration: str) -> float:
    """
    Checks that the duration is in the format HH:MM:SS.
    Other acceptable formats include SS.
    Ok:
      ""
      "?"
      06
      6
      60
      61
      23:24
      23:24:01.34
    Not Ok:
      -7
      61  # above 60 seconds
      61:01 # above 60 minutes
      25:24:01.34 # above 24 hours
    """

    def _raise() -> None:
        raise ValueError(f"Invalid duration: {duration}")

    def _is_non_neg_int(s: str) -> bool:
        try:
            return int(s) >= 0
        except ValueError:
            return False

    def _is_non_neg_float(s: str) -> bool:
        try:
            return float(s) >= 0.0
        except ValueError:
            return False

    try:
        valf = float(duration)
        if valf >= 0.0:
            return valf
        else:
            _raise()
    except ValueError:
        pass

    if "" == duration or "?" == duration or "Live" == duration:
        return 0
    # Simple case
    if ":" not in duration and "." not in duration:
        try:
            tmp = float(duration)
            if tmp < 0:
                _raise()
            return tmp
        except ValueError:
            _raise()
    new_duration = duration
    units = new_duration.split(":")
    if len(units) > 3 or len(units) < 1:
        _raise()
    units.reverse()
    total: float = 0.0
    limit_multiplier = [
        (60, 1),
        (60, 60),
        (24, 60 * 24),
    ]
    for i, unit in enumerate(units):
        if i == 0:
            is_valid_number = _is_non_neg_float(unit)
        else:
            is_valid_number = _is_non_neg_int(unit)
        if not is_valid_number:
            _raise()
        limit, multipler = limit_multiplier[i]
        val = float(unit)
        if val >= limit:
            _raise()
        total += val * multipler
    return total


class Video(BaseModel):
    """Represents a video object."""

    channel_name: constr(min_length=2)  # type: ignore
    title: constr(min_length=2)  # type: ignore
    date_published: datetime  # from the scraped website
    date_lastupdated: datetime
    channel_url: AnyUrl
    source: constr(min_length=4)  # type: ignore
    url: AnyUrl
    duration: NonNegativeFloat
    description: str
    img_src: AnyUrl
    iframe_src: str
    views: NonNegativeInt
    # rank: Optional[float] = None  # optional stdev rank.

    @validator("duration", pre=True)
    def check_duration(cls, v):
        return parse_duration(v)

    @validator("date_published", pre=True)
    def check_date_published(cls, v):
        return iso_fmt(v)

    @validator("date_lastupdated", pre=True)
    def check_date_lastupdated(cls, v):
        return iso_fmt(v)

    @validator("views", pre=True)
    def check_views(cls, v):
        if v == "" or v == "?":
            return 0
        try:
            return int(v)
        except ValueError:
            return 0

    @classmethod
    def from_list_of_dicts(cls, data: List[Dict]) -> List[Video]:
        out: List[Video] = []
        for datum in data:
            vid = Video(**datum)
            out.append(vid)
        return out

    @classmethod
    def to_plain_list(cls, data: List[Video]) -> List[Dict]:
        out = []
        vid: Video
        for vid in data:
            out.append(vid.dict())
        return out

    @classmethod
    def parse_json(cls, data: Union[str, dict]) -> List[dict]:
        """
        Parses a string or json dict and returns a json dict representation
        that can be used in a network request.
        """
        out: List[dict] = []
        if isinstance(data, str):
            json_data = json.loads(data)
        else:
            json_data = data
        if "content" in json_data:  # This is the publishing format.
            json_data = json_data["content"]
        for json_video in json_data:
            try:
                vid = Video(**json_video)
                out.append(vid.to_json())
            except Exception as err:
                print(
                    f"{__file__}: Skipping {json_video.get('url')} because {err}"
                )
        return out

    def video_age_seconds(self, now_time: Optional[datetime] = None) -> float:
        """
        Returns the date published as a datetime object.
        """
        now_time = now_time or datetime.now()
        diff: timedelta = now_time - parse_datetime(self.date_published)
        return diff.total_seconds()

    def to_json(self) -> dict:
        """
        Returns a json representation of the video object.
        """
        data = self.dict()
        data["date_published"] = self.date_published.isoformat()
        data["date_lastupdated"] = self.date_lastupdated.isoformat()
        return data

    def to_json_str(self) -> str:
        """
        Returns a json string representation of the video object.
        """
        return json.dumps(self.to_json(), ensure_ascii=False)
