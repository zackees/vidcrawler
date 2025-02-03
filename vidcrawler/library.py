# pylint: disable=too-many-arguments

"""Library json module."""

import json
import os
import re
import traceback
import warnings
from dataclasses import dataclass
from datetime import datetime

from appdirs import user_data_dir
from filelock import FileLock

from vidcrawler.downloadmp3 import download_mp3


def _get_library_json_lock_path() -> str:
    """Get the library json path."""
    return os.path.join(user_data_dir("vidcrawler"), "library.json.lock")


_FILE_LOCK = FileLock(_get_library_json_lock_path())


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
    # strip out multiple periods
    filename = re.sub(r"\.{2,}", ".", filename)
    # Split the filename into name and extension
    name_part, _, extension = filename.rpartition(".")

    # Remove emojis and special characters by allowing only a specific set of characters
    # This regex keeps letters, numbers, spaces, underscores, and hyphens.
    # You can adjust the regex as needed to include any additional characters.
    cleaned_name = re.sub(r"[^\w\s\-_]", "", name_part)

    # Replace spaces or consecutive dashes with a single underscore
    cleaned_name = re.sub(r"\s+|-+", "_", cleaned_name)

    # Replace multiple underscores with a single underscore
    cleaned_name = re.sub(r"_+", "_", cleaned_name)

    # replace commas with underscores
    cleaned_name = cleaned_name.replace(",", "_")

    # remove single quotes
    cleaned_name = cleaned_name.replace("'", "")

    cleaned_name = cleaned_name.replace(":", "_")

    # final problematic characters

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
    date: datetime | None
    error: bool = False

    def __init__(self, url: str, title: str, file_path: str | None = None, date: datetime | None = None, error=False) -> None:
        self.url = url
        self.title = title
        self.date = date
        if file_path is None:
            self.file_path = clean_filename(f"{title}.mp3")
        else:
            self.file_path = clean_filename(file_path)
        self.error = error

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
            "date": self.date.isoformat() if self.date else None,
            "file_path": self.file_path,
            "error": self.error,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "VidEntry":
        """Create from dictionary."""
        filepath = data.get("file_path")
        if filepath is None:
            filepath = clean_filename(data["title"])
        filepath = clean_filename(filepath)
        date = datetime.fromisoformat(data["date"]) if data.get("date") else None
        error = data.get("error", False)
        return VidEntry(url=data["url"], title=data["title"], date=date, file_path=filepath, error=error)

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
                # if error
                if not vid.error:
                    out.append(vid)
                else:
                    warnings.warn(f"Skipping {vid.url} because it is marked as an error.")
    all_have_a_date = all(vid.date for vid in out)
    if all_have_a_date:
        # sort oldest first
        out.sort(key=lambda vid: vid.date)  # type: ignore
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
        found_entries.append(VidEntry(url=vid.url, title=title, file_path=file_path, date=vid.date))
    with _FILE_LOCK:
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
        if pardir and not os.path.exists(pardir):
            os.makedirs(pardir, exist_ok=True)
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
            try:
                download_mp3(url=next_url, outmp3=next_mp3_path)
            except Exception as e:  # pylint: disable=broad-except
                stacktrace_str = traceback.format_exc()
                print(f"Error downloading {next_url}: {e}")
                print(stacktrace_str)
                self.mark_error(vid)
            download_count += 1

    def mark_error(self, vid: VidEntry) -> None:
        """Mark the vid as an error."""
        vid.error = True
        self.merge([vid])
        print(f"Marked {vid.url} as an error.")

    def date_range(self) -> tuple[datetime, datetime] | None:
        """Get the date range."""
        vids = self.load()
        dates = [vid.date for vid in vids if vid.date]
        if not dates:
            return None
        return min(dates), max(dates)
