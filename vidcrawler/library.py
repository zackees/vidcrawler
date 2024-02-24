"""Library json module."""

import json
import os
import re
from dataclasses import dataclass

from filelock import FileLock

from vidcrawler.downloadmp3 import download_mp3


def clean_filename(filename: str) -> str:
    """
    Cleans a string to make it a valid directory name by removing emojis,
    special characters, and other non-ASCII characters, in addition to the
    previously specified invalid filename characters, while preserving the file extension.

    Args:
    - filename (str): The filename to be cleaned.

    Returns:
    - str: A cleaned-up string suitable for use as a filename.
    """
    # strip out any leading or trailing whitespace
    filename = filename.strip()
    # strip out leading and trailing periods
    filename = filename.strip(".")
    # Split the filename into name and extension
    name_part, _, extension = filename.rpartition(".")

    # Remove emojis and special characters by allowing only a specific set of characters
    # This regex keeps letters, numbers, spaces, underscores, and hyphens.
    # You can adjust the regex as needed to include any additional characters.
    cleaned_name = re.sub(r"[^\w\s\-_]", "", name_part)

    # Replace spaces or consecutive dashes with a single underscore
    cleaned_name = re.sub(r"\s+|-+", "_", cleaned_name)

    # replace commas with underscores
    cleaned_name = cleaned_name.replace(",", "_")

    # Replace multiple underscores with a single underscore
    cleaned_name = re.sub(r"_+", "_", cleaned_name)

    # Replace leading or trailing underscores with an empty string
    cleaned_name = cleaned_name.strip("_")

    # Remove leading or trailing whitespace (after replacing spaces with underscores, this might be redundant)
    cleaned_name = cleaned_name.strip()

    # Optional: Convert to lowercase to avoid issues with case-sensitive file systems
    # cleaned_name = cleaned_name.lower()

    # Optional: Trim the title to a maximum length (e.g., 255 characters)
    max_length = 255
    if len(cleaned_name) > max_length:
        cleaned_name = cleaned_name[:max_length]

    # Reattach the extension only if it was present
    if extension:
        return f"{cleaned_name}.{extension}"
    return cleaned_name


@dataclass
class VidEntry:
    """Video entry."""

    url: str
    title: str
    file_path: str

    def __init__(self, url: str, title: str, file_path: str | None = None) -> None:
        self.url = url
        self.title = title
        if file_path is None:
            self.file_path = clean_filename(f"{title}.mp3")
        else:
            self.file_path = clean_filename(file_path)

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
        filepath = data.get("file_path")
        if filepath is None:
            filepath = clean_filename(data["title"])
        filepath = clean_filename(filepath)
        return cls(url=data["url"], title=data["title"], file_path=filepath)

    @classmethod
    def serialize(cls, data: list["VidEntry"]) -> str:
        """Serialize to string."""
        json_data = [vid.to_dict() for vid in data]
        return json.dumps(json_data, indent=2)

    @classmethod
    def deserialize(cls, data: str) -> list["VidEntry"]:
        """Deserialize from string."""
        # return [cls.from_dict(vid) for vid in json.loads(data)]
        out: list[VidEntry] = []
        try:
            for vid in json.loads(data):
                try:
                    out.append(cls.from_dict(vid))
                except KeyboardInterrupt as e:
                    raise e
                except Exception as e:  # pylint: disable=broad-except
                    print(f"Failed to deserialize {vid}: {e}")
        except Exception as e:  # pylint: disable=broad-except
            print(f"Failed to deserialize {data}: {e}")
        return out


def find_missing_downloads(library_json_path: str) -> list[VidEntry]:
    """Find missing downloads."""
    pardir = os.path.dirname(library_json_path)
    out: list[VidEntry] = []
    lock = library_json_path + ".lock"
    with FileLock(lock):
        data = load_json(library_json_path)
        for vid in data:
            file_path = vid.file_path
            if not os.path.exists(os.path.join(pardir, file_path)):
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
            download_mp3(url=next_url, outmp3=next_mp3_path)
            download_count += 1
