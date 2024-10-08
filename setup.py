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
REQUIRES_PYTHON = ">=3.6.0"
VERSION = None

# The text of the README file
with open(os.path.join(HERE, "README.md"), encoding="utf-8", mode="rt") as fd:
    LONG_DESCRIPTION = fd.read()


def get_version() -> str:
    version_file = os.path.join(HERE, NAME, "version.py")
    with open(version_file, encoding="utf-8", mode="rt") as fd:
        for line in fd.readlines():
            if line.startswith("VERSION"):
                VERSION = line.split("=")[1].strip().strip('"')
                return VERSION
    raise RuntimeError("Could not find version")


VERSION = get_version()


class UploadCommand(Command):
    """Support setup.py upload."""

    description = "Build and publish the package."
    user_options = []

    @staticmethod
    def status(s):
        pass

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status("Removing previous builds…")
            rmtree(os.path.join(HERE, "dist"))
        except OSError:
            pass

        self.status("Building Source and Wheel (universal) distribution…")

        def exe(cmd: str) -> None:
            print(f"Executing:\n  {cmd}\n")
            return os.system(cmd)

        exe(f'"{sys.executable}" setup.py sdist bdist_wheel --universal')

        self.status("Uploading the package to PyPI via Twine…")
        if 0 != exe("twine upload dist/*"):
            raise RuntimeError("Upload failed")

        self.status("Pushing git tags…")
        exe(f"git tag v{VERSION} && git push --tags")

        sys.exit()


setup(
    python_requires=REQUIRES_PYTHON,
    version=VERSION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
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
    cmdclass={
        "upload": UploadCommand,
    },
)
