"""
Fetcher for html
"""

import subprocess

# pylint: disable=line-too-long,missing-function-docstring,consider-using-f-string,too-many-locals,invalid-name,no-else-return
from typing import Optional

import requests

try:
    subprocess.check_output("curl --version", shell=True)
    USE_CURL = True
except BaseException:  # pylint: disable=broad-except
    USE_CURL = False


def fetch_html_using_request_lib(
    url: str,
    timeout: Optional[int] = None,
    user_agent: Optional[str] = None,
) -> str:
    timeout = timeout or 10
    # Workaround for long request time on windows
    # see https://github.com/psf/requests/issues/4023
    headers = {"Connection": "close"}
    # headers = {"Connection": "close"}
    if user_agent:
        headers["User-Agent"] = user_agent
    resp = requests.get(url, timeout=timeout, params={}, headers=headers)
    resp.raise_for_status()
    return resp.content.decode(resp.apparent_encoding)


def fetch_html_using_curl(url: str, timeout: Optional[int] = None) -> str:
    """Uses the curl library to do a fetch"""
    timeout = int(timeout or 10)
    out: bytes = subprocess.check_output(
        f"curl --max-time {timeout} -s -X GET {url}", shell=True
    )
    return out.decode("utf-8")


def fetch_html(url: str) -> str:
    if USE_CURL:
        return fetch_html_using_curl(url)
    else:
        return fetch_html_using_request_lib(url)
