"""Library json module."""

import json
import os
from dataclasses import dataclass

from filelock import FileLock

from vidcrawler.youtube_bot import YtVid


@dataclass
class VidEntry:
    """Video entry."""

    url: str
    title: str
    file_path: str

    # needed for set membership
    def __hash__(self):
        return hash(self.url)

    def __eq__(self, other):
        return self.url == other.url

    def __repr__(self) -> str:
        data = self.to_dict()
        return json.dumps(data)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "url": self.url,
            "title": self.title,
            "file_path": self.file_path,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "VidEntry":
        """Create from dictionary."""
        return cls(url=data["url"], title=data["title"], file_path=data["file_path"])

    @classmethod
    def serialize(cls, data: list["VidEntry"]) -> str:
        """Serialize to string."""
        return json.dumps([vid.to_dict() for vid in data])

    @classmethod
    def deserialize(cls, data: str) -> list["VidEntry"]:
        """Deserialize from string."""
        return [cls.from_dict(vid) for vid in json.loads(data)]


def find_missing_downloads(library_json_path: str) -> list[VidEntry]:
    """Find missing downloads."""
    out: list[VidEntry] = []
    lock = library_json_path + ".lock"
    with FileLock(lock):
        data = load_json(library_json_path)
        for vid in data:
            file_path = vid.file_path
            if not os.path.exists(file_path):
                out.append(vid)
    return out


def load_json(file_path: str) -> list[VidEntry]:
    """Load json from file."""
    with open(file_path, encoding="utf-8", mode="r") as filed:
        data = filed.read()
    return VidEntry.deserialize(data)


def save_json(file_path: str, data: list[VidEntry]) -> None:
    """Save json to file."""
    json_out = VidEntry.serialize(data)
    with open(file_path, encoding="utf-8", mode="w") as filed:
        filed.write(json_out)


def merge_into_library(library_json_path: str, vids: list[YtVid]) -> None:
    """Merge the vids into the library."""
    found_entries: list[VidEntry] = []
    for vid in vids:
        title = vid.title
        file_path = os.path.join(f"{title}.mp3")
        found_entries.append(VidEntry(url=vid.url, title=title, file_path=file_path))
    file_lock = library_json_path + ".lock"
    with FileLock(file_lock):
        existing_entries = load_json(library_json_path)
        for found in found_entries:
            if found not in existing_entries:
                existing_entries.append(found)
        save_json(library_json_path, existing_entries)


class LibraryJson:
    """Represents the library"""

    def __init__(self, library_json_path: str) -> None:
        self.library_json_path = library_json_path

    def find_missing_downloads(self) -> list[VidEntry]:
        """Find missing downloads."""
        return find_missing_downloads(self.library_json_path)

    def load(self) -> list[VidEntry]:
        """Load json from file."""
        return load_json(self.library_json_path)

    def save(self, data: list[VidEntry]) -> None:
        """Save json to file."""
        save_json(self.library_json_path, data)

    def merge(self, vids: list[YtVid]) -> None:
        """Merge the vids into the library."""
        merge_into_library(self.library_json_path, vids)
