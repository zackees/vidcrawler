"""
Testing for io
"""


# pylint: disable=line-too-long,missing-function-docstring,missing-class-docstring,super-with-arguments,invalid-name,R0801

import gzip
import os
import shutil
import tempfile
import unittest

from vidcrawler.io import write_json


class IoTester(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cleanup = []

    def tearDown(self):
        for cleanup in self.cleanup:
            try:
                cleanup()
            except BaseException as be:  # pylint: disable=broad-except
                print(str(be))
        self.cleanup = []

    def create_tmp_dir(self) -> str:
        tmp_dir = os.path.join(
            tempfile.gettempdir(),
            "blast.video",
            "test",
            "io",
            os.urandom(24).hex(),
        )
        os.makedirs(tmp_dir, exist_ok=True)
        self.cleanup.append(lambda: shutil.rmtree(tmp_dir, ignore_errors=True))
        return tmp_dir

    def test_make_zip(self):
        tmp_dir = self.create_tmp_dir()
        json_content = {"key": "value"}
        json_path = os.path.join(tmp_dir, "my.json")
        write_json(json_path, content=json_content, also_gzip=True, minify=True)
        self.assertTrue(os.path.isfile(json_path), json_path)
        # Expect that zip file exists.
        zip_path = json_path + ".gz"
        self.assertTrue(os.path.isfile(zip_path), f"Path: {zip_path}")
        with gzip.open(zip_path, "rb") as f:
            data_reread = f.read().decode("utf-8")
        self.assertEqual(data_reread, '{"key": "value"}')


if __name__ == "__main__":
    unittest.main()
