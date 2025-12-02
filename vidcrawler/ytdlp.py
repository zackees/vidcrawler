import json
import re
import shutil
import subprocess
import warnings
from typing import Any

from vidcrawler.types import ChannelId, VideoId


def _yt_dlp_exe() -> str:
    yt_exe = shutil.which("yt-dlp")
    if yt_exe is None:
        raise FileNotFoundError("yt-dlp not found in PATH")
    return yt_exe


def fetch_channel_info_ytdlp(video_url: str) -> dict[Any, Any]:
    """Fetch the info."""
    # yt-dlp -J "VIDEO_URL" > video_info.json
    yt_exe = _yt_dlp_exe()
    cmd_list = [
        yt_exe,
        "-J",
        video_url,
    ]
    completed_proc = subprocess.run(cmd_list, capture_output=True, text=True, shell=False, check=True)
    if completed_proc.returncode != 0:
        stderr = completed_proc.stderr
        warnings.warn(f"Failed to run yt-dlp with args: {cmd_list}, stderr: {stderr}")
    lines: list[str] = []
    for line in completed_proc.stdout.splitlines():
        if line.startswith("OSError:"):
            continue
        lines.append(line)
    out = "\n".join(lines)
    data = json.loads(out)
    return data


def fetch_video_info(video_url: str) -> dict:
    yt_exe = _yt_dlp_exe()
    cmd_list = [
        yt_exe,
        "-J",
        video_url,
    ]
    # Add browser impersonation for Rumble to avoid HTTP 403 errors
    if "rumble.com" in video_url:
        cmd_list.extend(["--impersonate", "chrome-120"])
    completed_proc = subprocess.run(cmd_list, capture_output=True, text=True, shell=False, check=True)
    if completed_proc.returncode != 0:
        stderr = completed_proc.stderr
        warnings.warn(f"Failed to run yt-dlp with args: {cmd_list}, stderr: {stderr}")
    lines: list[str] = []
    for line in completed_proc.stdout.splitlines():
        if line.startswith("OSError:"):
            continue
        lines.append(line)
    out = "\n".join(lines)
    data = json.loads(out)
    return data


def fetch_channel_url_ytdlp(video_url: str) -> str:
    """Fetch the info."""
    # yt-dlp -J "VIDEO_URL" > video_info.json
    yt_exe = _yt_dlp_exe()
    cmd_list = [
        yt_exe,
        "--print",
        "channel_url",
        video_url,
    ]
    completed_proc = subprocess.run(cmd_list, capture_output=True, text=True, timeout=10, shell=False, check=True)
    if completed_proc.returncode != 0:
        stderr = completed_proc.stderr
        warnings.warn(f"Failed to run yt-dlp with args: {cmd_list}, stderr: {stderr}")
    lines = completed_proc.stdout.splitlines()
    out_lines: list[str] = []
    for line in lines:
        if line.startswith("OSError:"):  # happens on zach's machine
            continue
        out_lines.append(line)
    out = "\n".join(out_lines)
    return out


def fetch_channel_id_ytdlp(video_url: str) -> ChannelId:
    """Fetch the info."""
    url = fetch_channel_url_ytdlp(video_url)
    match = re.search(r"/channel/([^/]+)/?", url)
    if match:
        out: str = str(match.group(1))
        return ChannelId(out)
    raise RuntimeError(f"Could not find channel id in: {video_url} using yt-dlp.")


def fetch_videos_from_channel(channel_url: str) -> list[VideoId]:
    """Fetch the videos from a channel."""
    # yt-dlp -J "CHANNEL_URL" > channel_info.json
    # cmd = f'yt-dlp -i --get-id "https://www.youtube.com/channel/{channel_id}"'
    yt_exe = _yt_dlp_exe()
    cmd_list = [yt_exe, "--print", "id", channel_url]
    # Add browser impersonation for Rumble to avoid HTTP 403 errors
    if "rumble.com" in channel_url:
        cmd_list.extend(["--impersonate", "chrome-120"])
    cms_str = subprocess.list2cmdline(cmd_list)
    print(f"Running: {cms_str}")
    completed_proc = subprocess.run(
        cmd_list,
        capture_output=True,
        text=True,
        shell=False,
        check=False,
    )
    # Check if we got any output before checking return code
    stdout = completed_proc.stdout
    stderr = completed_proc.stderr
    lines = stdout.splitlines()
    out_channel_ids: list[VideoId] = []
    for line in lines:
        if line.startswith("OSError:"):  # happens on zach's machine
            continue
        if line.startswith("WARNING:"):
            warnings.warn(line)
            continue
        if line.startswith("ERROR:"):
            warnings.warn(line)
            continue
        out_channel_ids.append(VideoId(line))

    # If we got video IDs despite warnings, return them
    if out_channel_ids:
        if completed_proc.returncode != 0:
            warnings.warn(f"yt-dlp returned exit code {completed_proc.returncode} but extracted {len(out_channel_ids)} video IDs. Stderr: {stderr}")
        return out_channel_ids

    # If we didn't get any video IDs and there was an error, raise it
    if completed_proc.returncode != 0:
        raise subprocess.CalledProcessError(completed_proc.returncode, cmd_list, output=stdout, stderr=stderr)

    return out_channel_ids


def fetch_videos_from_youtube_channel(channel_id: str) -> list[VideoId]:
    """Fetch the videos from a youtube channel."""
    channel_url = f"https://www.youtube.com/channel/{channel_id}"
    return fetch_videos_from_channel(channel_url)
