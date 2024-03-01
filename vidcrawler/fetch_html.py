# pylint: disable=line-too-long,missing-function-docstring,consider-using-f-string,too-many-locals,invalid-name,no-else-return
"""
Fetcher for html
"""

import subprocess
import tempfile
from dataclasses import dataclass
from typing import Optional

import requests

try:
    subprocess.check_output("curl --version", shell=True)
    USE_CURL = True
except BaseException:  # pylint: disable=broad-except
    USE_CURL = False


@dataclass
class FetchResult:
    html: str
    status_code: int
    ok = property(lambda self: 200 <= self.status_code < 300)


def fetch_html_using_request_lib(
    url: str,
    timeout: Optional[int] = None,
    user_agent: Optional[str] = None,
) -> FetchResult:
    timeout = timeout or 10
    # Workaround for long request time on windows
    # see https://github.com/psf/requests/issues/4023
    headers = {"Connection": "close"}
    # headers = {"Connection": "close"}
    if user_agent:
        headers["User-Agent"] = user_agent
    resp = requests.get(url, timeout=timeout, params={}, headers=headers)
    resp.raise_for_status()
    return FetchResult(html=resp.text, status_code=resp.status_code)


def fetch_html_using_curl(url: str, timeout: Optional[int] = None) -> FetchResult:
    """Uses the curl library to fetch HTML and return HTML content and status code."""
    timeout = int(timeout or 10)
    # Create a temporary directory to store the response and the status code
    with tempfile.TemporaryDirectory() as temp_dir:
        # Define file paths within the temporary directory
        body_file_path = f"{temp_dir}/response_body.txt"
        status_code_file_path = f"{temp_dir}/status_code.txt"

        # Construct curl command to write body to a file and status code to another file
        command = f"curl --max-time {timeout} -s -o {body_file_path} -w '%{{http_code}}' -X GET {url} > {status_code_file_path}"
        subprocess.check_output(command, shell=True)

        # Read the status code from its file
        with open(status_code_file_path, encoding="utf-8", mode="r") as file:
            status_code = int(file.read().strip().replace("'", ""))

        # Read the response body from its file
        with open(body_file_path, encoding="utf-8", mode="r") as file:
            body = file.read()

    return FetchResult(html=body, status_code=status_code)


def fetch_html(url: str) -> FetchResult:
    if USE_CURL:
        return fetch_html_using_curl(url)
    else:
        return fetch_html_using_request_lib(url)
