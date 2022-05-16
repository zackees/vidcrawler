"""
Utilities for reading and writing files.
"""

# pylint: disable=missing-function-docstring,too-many-arguments,too-many-locals,too-many-statements,line-too-long,invalid-name

import gzip
import json
import os
import sys
from datetime import datetime
from typing import Any, Dict, List

from .date import iso_fmt
from .video_info import VideoInfo


def write_gzip(out_path: str, content: bytes) -> None:
    assert out_path.endswith(".gz")
    with gzip.open(out_path, "wb") as f:
        f.write(content)


def write_utf8(out_path: str, content: str) -> None:
    out_path = os.path.normpath(out_path)
    dir_path: str = os.path.dirname(out_path)
    os.makedirs(dir_path, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as fd:
        fd.write(content)


def make_export_json(
    now: datetime, content: List[Any], network_name: str, telegram: str
) -> Dict[str, Any]:
    # Type check, do we have a list of VideoInfo objects? If so convert to a list of dicts.
    if len(content) > 0:
        first = content[0]
        if isinstance(first, VideoInfo):
            content = VideoInfo.to_plain_list(content)
    return {
        "network_name": network_name,
        "__update_time": iso_fmt(now),
        "telegram": telegram,
        "content": content,
    }


def write_json(out_path: str, content: Any, also_gzip: bool = False, minify: bool = False, **kwargs) -> None:  # type: ignore
    """
    If zip is True, then the same json file will ALSO be written out
    with the extension *.zip and a single file inside labeled data.json.
    """
    assert "gzip" not in kwargs
    if not minify:
        kwargs["indent"] = 2
    out_utf8 = json.dumps(content, ensure_ascii=False, **kwargs)
    write_utf8(out_path, out_utf8)
    if also_gzip:
        if "indent" in kwargs:
            del kwargs["indent"]
        out_utf8 = json.dumps(content, ensure_ascii=False, **kwargs)
        write_gzip(out_path + ".gz", out_utf8.encode("utf-8"))


def read_utf8(in_path: str) -> str:
    in_path = os.path.normpath(in_path)
    with open(in_path, "r", encoding="utf-8") as fd:
        return fd.read()


def trap_win32_keyboard_interrupt_here() -> None:
    if sys.platform == "win32":  # Play better with ctrl-c
        import signal  # pylint: disable=import-outside-toplevel

        def raise_exc(a: Any, b: Any) -> None:
            raise KeyboardInterrupt("ctrl-c")

        signal.signal(signal.SIGINT, raise_exc)
