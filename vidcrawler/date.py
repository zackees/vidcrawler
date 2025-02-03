"""
Date utility functions.
"""

# pylint: disable=invalid-name

from datetime import datetime
from re import findall
from typing import Optional, Union

import pytz
from dateutil.parser import parse

CURRENT_TIME_ZONE_STR = "America/Los_Angeles"


def now_local(tz_str: Optional[str] = None) -> datetime:
    """Returns timezone aware now, which allows subtractions"""
    tz_str = tz_str or CURRENT_TIME_ZONE_STR
    tz = pytz.timezone(tz_str)
    ts = datetime.now().astimezone(tz)
    return ts


def _my_date_parse(date_string: str | datetime) -> datetime:
    if isinstance(date_string, datetime):
        return date_string
    try:
        return datetime.fromisoformat(date_string)
    except Exception as verr:  # pylint: disable=broad-except
        if "Invalid isoformat" in str(verr):
            return parse(date_string, fuzzy=True)
        raise


def parse_datetime(s, tzinfo=None) -> datetime:  # type: ignore
    """Parses a datetime string"""
    date: datetime = _my_date_parse(s)
    if tzinfo:
        if isinstance(tzinfo, str):
            tzinfo = pytz.timezone(tzinfo)
        if date.tzinfo is None:
            date = date.replace(tzinfo=tzinfo)
        else:
            date = date.astimezone(tzinfo)
    return date


def iso_fmt(date_obj: Union[datetime, str]) -> str:
    """Outputs the ogbject as an iso formatted string"""
    if isinstance(date_obj, datetime):
        return date_obj.isoformat()
    if isinstance(date_obj, str):
        return parse_datetime(date_obj).isoformat()
    raise ValueError(f"{__file__} Unexpected type: {type(date_obj)}")


def iso8601_duration_as_seconds(d: str) -> int:
    """assert iso8601_duration_as_seconds('PT25M0S') == 1500"""
    if d[0] != "P":
        raise ValueError("Not an ISO 8601 Duration string")
    seconds = 0
    # split by the 'T'
    for i, item in enumerate(d.split("T")):
        for number, unit in findall(r"(?P<number>\d+)(?P<period>S|M|H|D|W|Y)", item):
            # print '%s -> %s %s' % (d, number, unit )
            number = int(number)
            this = 0
            if unit == "Y":
                this = number * 31557600  # 365.25
            elif unit == "W":
                this = number * 604800
            elif unit == "D":
                this = number * 86400
            elif unit == "H":
                this = number * 3600
            elif unit == "M":
                # ambiguity ellivated with index i
                if i == 0:
                    this = number * 2678400  # assume 30 days
                    # print "MONTH!"
                else:
                    this = number * 60
            elif unit == "S":
                this = number
            seconds = seconds + this
    return seconds


def timestamp_to_iso8601(timestamp: float) -> str:
    """Converts a timestamp to an iso8601 string"""
    return datetime.utcfromtimestamp(timestamp).isoformat() + "Z"
