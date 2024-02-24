"""
Testing for io
"""

# pylint: disable=line-too-long,missing-function-docstring,missing-class-docstring,super-with-arguments,invalid-name,R0801

import os
import pathlib
import shutil
import tempfile
import traceback
import unittest
import warnings

from vidcrawler.library import Library

HERE = pathlib.Path(__file__).parent.absolute()
BAD_LIBRARY_JSON_PATH = os.path.join(HERE, "bad_library.json")
assert os.path.exists(BAD_LIBRARY_JSON_PATH), f"bad_library.json {BAD_LIBRARY_JSON_PATH} does not exist"


class BadVideoMp3DownloadTester(unittest.TestCase):

    def test_create_tmp_dir(self) -> None:
        prev_dir = os.getcwd()
        temp_dir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
        try:
            os.chdir(temp_dir.name)
            basename = os.path.basename(BAD_LIBRARY_JSON_PATH)
            shutil.copy(BAD_LIBRARY_JSON_PATH, ".")
            library = Library(basename)
            library.download_missing()
        except Exception as e:  # pylint: disable=broad-except
            traceback.print_exc()
            self.fail(f"Failed to download missing videos: {e}")
        finally:
            try:
                os.chdir(prev_dir)
                temp_dir.cleanup()
            except Exception as e:  # pylint: disable=broad-except
                warnings.warn(f"Failed to cleanup temp_dir: {e}")


if __name__ == "__main__":
    unittest.main()
