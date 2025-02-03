# pylint: disable=missing-function-docstring
# pylint: disable=consider-using-f-string
# pylint: disable=missing-module-docstring

import os
import sys
from shutil import rmtree

from setuptools import Command, find_packages, setup

# The directory containing this file
HERE = os.path.dirname(__file__)
NAME = "vidcrawler"
URL = "https://github.com/zackees/vidcrawler"
EMAIL = "dont@email.me"
AUTHOR = "Zach Vorhies"

setup(
    url=URL,
    author="Zach Vorhies",
    author_email="dont@email.me",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.9",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Operating System :: MacOS :: MacOS X",
        "Environment :: Console",
    ],
    packages=find_packages(
        exclude=["tests", "*.tests", "*.tests.*", "tests.*"]
    ),
    package_data={},
    include_package_data=True,
)
