"""Library json module."""

import json
import os
import subprocess
import warnings
from dataclasses import dataclass

from filelock import FileLock
from static_ffmpeg import add_paths


@dataclass
class VidEntry:
    """Video entry."""

    url: str
    title: str
    file_path: str

    def __init__(self, url: str, title: str, file_path: str | None = None) -> None:
        self.url = url
        self.title = title
        self.file_path = file_path or f"{title}.mp3"

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
        json_data = [vid.to_dict() for vid in data]
        return json.dumps(json_data, indent=2)

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


def yt_dlp_download_mp3(url: str, outmp3: str) -> None:
    """Download the youtube video as an mp3."""
    add_paths()
    par_dir = os.path.dirname(outmp3)
    if par_dir:
        os.makedirs(par_dir, exist_ok=True)

    for _ in range(3):
        try:
            cmd_list: list[str] = [
                "yt-dlp",
                url,
                "--extract-audio",
                "--audio-format",
                "mp3",
                "--output",
                outmp3,
            ]
            subprocess.run(cmd_list, check=True)
            return
        except subprocess.CalledProcessError as cpe:
            print(f"Failed to download {url} as mp3: {cpe}")
            continue
    warnings.warn(f"Failed all attempts to download {url} as mp3.")


def merge_into_library(library_json_path: str, vids: list[VidEntry]) -> None:
    """Merge the vids into the library."""
    found_entries: list[VidEntry] = []
    for vid in vids:
        title = vid.title
        file_path = vid.file_path
        found_entries.append(VidEntry(url=vid.url, title=title, file_path=file_path))
    file_lock = library_json_path + ".lock"
    with FileLock(file_lock):
        existing_entries = load_json(library_json_path)
        for found in found_entries:
            if found not in existing_entries:
                existing_entries.append(found)
        save_json(library_json_path, existing_entries)


class Library:
    """Represents the library"""

    def __init__(self, library_json_path: str) -> None:
        self.library_json_path = library_json_path
        self.base_dir = os.path.dirname(library_json_path)
        pardir = os.path.dirname(library_json_path)
        if not os.path.exists(pardir):
            os.makedirs(pardir)
        if not os.path.exists(library_json_path):
            with open(library_json_path, encoding="utf-8", mode="w") as filed:
                filed.write("[]")

    def find_missing_downloads(self) -> list[VidEntry]:
        """Find missing downloads."""
        return find_missing_downloads(self.library_json_path)

    def load(self) -> list[VidEntry]:
        """Load json from file."""
        return load_json(self.library_json_path)

    def save(self, data: list[VidEntry]) -> None:
        """Save json to file."""
        save_json(self.library_json_path, data)

    def merge(self, vids: list[VidEntry]) -> None:
        """Merge the vids into the library."""
        merge_into_library(self.library_json_path, vids)

    def download_missing(self, download_limit: int = -1) -> None:
        """Download the missing files."""
        download_count = 0
        while True:
            if download_limit != -1 and download_count >= download_limit:
                break
            missing_downloads = self.find_missing_downloads()
            # make full paths
            if not missing_downloads:
                break
            vid = missing_downloads[0]
            next_url = vid.url
            next_mp3_path = os.path.join(self.base_dir, vid.file_path)
            print(f"\n#######################\n# Downloading missing file {next_url}: {next_mp3_path}\n" "###################")
            yt_dlp_download_mp3(url=next_url, outmp3=next_mp3_path)
            download_count += 1
