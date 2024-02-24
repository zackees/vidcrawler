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


def yt_dlp_download_mp3(url: str, outmp3: str) -> None:
    """Download the youtube video as an mp3."""
    add_paths()
    par_dir = os.path.dirname(outmp3)
    if par_dir:
        os.makedirs(par_dir, exist_ok=True)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file = os.path.join(temp_dir, "temp.mp3")
        for _ in range(3):
            try:
                cmd_list: list[str] = [
                    "yt-dlp",
                    url,
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
        cmd_args = [url, "--extract-audio", "--audio-format", "mp3", "--output", "/host_dir/temp.mp3", "--update", "--no-geo-bypass"]
        docker_run(name="yt-dlp", dockerfile_or_url=dockerfile, cwd=temp_dir, cmd_list=cmd_args)
        shutil.copy(os.path.join(temp_dir, "temp.mp3"), outmp3)


def download_mp3(url: str, outmp3: str) -> None:
    """Download the youtube video as an mp3."""
    docker_yt_dlp = os.environ.get("USE_DOCKER_YT_DLP", "0") == "1"
    if docker_yt_dlp:
        return docker_yt_dlp_download_mp3(url, outmp3)
    return yt_dlp_download_mp3(url, outmp3)
