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
DESCRIPTION = "Video Crawler"
URL = "https://github.com/zackees/vidcrawler"
EMAIL = "dont@email.me"
AUTHOR = "Zach Vorhies"
REQUIRES_PYTHON = ">=3.6.0"
VERSION = None

# The text of the README file
with open(os.path.join(HERE, "README.md"), encoding="utf-8", mode="rt") as fd:
    LONG_DESCRIPTION = fd.read()

with open(
    os.path.join(HERE, "requirements.txt"), encoding="utf-8", mode="rt"
) as fd:
    REQUIREMENTS = [line.strip() for line in fd.readlines() if line.strip()]


def get_requirements():
    with open(
        os.path.join(HERE, "requirements.txt"), encoding="utf-8", mode="rt"
    ) as f:
        packages = []
        for line in f:
            line = line.strip()
            # let's also ignore empty lines and comments
            if not line or line.startswith("#"):
                continue
            if "https://" in line:
                tail = line.rsplit("/", 1)[1]
                tail = tail.split("#")[0]
                line = tail.replace("@", "==").replace(".git", "")
            packages.append(line)
    return packages


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
    name=NAME,
    python_requires=REQUIRES_PYTHON,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url=URL,
    author="Zach Vorhies",
    author_email="dont@email.me",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.9",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Operating System :: MacOS :: MacOS X",
        "Environment :: Console",
    ],
    install_requires=REQUIREMENTS,
    packages=find_packages(
        exclude=["tests", "*.tests", "*.tests.*", "tests.*"]
    ),
    package_data={},
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "vidcrawler = vidcrawler.cmd:main",
            "vidcrawler_test = vidcrawler.run_tests:main",
        ],
    },
    cmdclass={
        "upload": UploadCommand,
    },
)
