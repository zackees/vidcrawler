"""
Download a youtube video as an mp3.
"""

import os
import shutil
import subprocess
import tempfile
import warnings

from docker_run_cmd.api import docker_run
from static_ffmpeg import add_paths

FFMPEG_PATH_ADDED = False


def yt_dlp_download_mp3(url: str, outmp3: str) -> None:
    """Download the youtube video as an mp3."""
    global FFMPEG_PATH_ADDED  # pylint: disable=global-statement
    if not FFMPEG_PATH_ADDED:
        add_paths()
        FFMPEG_PATH_ADDED = True
    par_dir = os.path.dirname(outmp3)
    if par_dir:
        os.makedirs(par_dir, exist_ok=True)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file = os.path.join(temp_dir, "temp.mp3")
        for _ in range(3):
            try:
                cmd_list: list[str] = []
                cmd_list += ["yt-dlp", url]
                is_youtube = "youtube.com" in url or "youtu.be" in url
                if is_youtube:
                    cmd_list += [
                        "-f",
                        "bestaudio",
                    ]
                cmd_list += [
                    "--extract-audio",
                    "--audio-format",
                    "mp3",
                    "--output",
                    temp_file,
                ]
                subprocess.run(cmd_list, check=True)
                shutil.copy(temp_file, outmp3)
                return
            except subprocess.CalledProcessError as cpe:
                print(f"Failed to download {url} as mp3: {cpe}")
                continue
        warnings.warn(f"Failed all attempts to download {url} as mp3.")


def docker_yt_dlp_download_mp3(url: str, outmp3: str) -> None:
    """Download the youtube video as an mp3."""
    here = os.path.abspath(os.path.dirname(__file__))
    dockerfile = os.path.join(here, "Dockerfile")
    dockerfile = os.path.abspath(dockerfile)
    assert os.path.exists(dockerfile), f"dockerfile {dockerfile} does not exist"
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp_dir:
        cmd_args = [url, "-f", "bestaudio", "--extract-audio", "--audio-format", "mp3", "--output", "/host_dir/temp.mp3", "--update", "--no-geo-bypass"]
        docker_run(name="yt-dlp", dockerfile_or_url=dockerfile, cwd=temp_dir, cmd_list=cmd_args)
        shutil.copy(os.path.join(temp_dir, "temp.mp3"), outmp3)


def download_mp3(url: str, outmp3: str) -> None:
    """Download the youtube video as an mp3."""
    docker_yt_dlp = os.environ.get("USE_DOCKER_YT_DLP", "0") == "1"
    if docker_yt_dlp:
        return docker_yt_dlp_download_mp3(url, outmp3)
    return yt_dlp_download_mp3(url, outmp3)


def update_yt_dlp() -> None:
    docker_yt_dlp = os.environ.get("USE_DOCKER_YT_DLP", "0") == "1"
    if not docker_yt_dlp:
        return
    cmd_list = ["yt-dlp", "--update"]
    subprocess.run(cmd_list, check=True)


def unit_test() -> None:
    """Run the tests."""
    url = "https://www.youtube.com/watch?v=3Zl9puhwiyw"
    outmp3 = "tmp.mp3"
    download_mp3(url, outmp3)
    print(f"Downloaded {url} as {outmp3}")
    os.remove(outmp3)


if __name__ == "__main__":
    unit_test()
