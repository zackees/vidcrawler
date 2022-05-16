"""
Testing cmd
"""


# pylint: disable=line-too-long,missing-function-docstring,missing-class-docstring,super-with-arguments,invalid-name,R0801

import os
import subprocess
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
FETCH_LIST = os.path.join(HERE, "fetch_list.json")
OUT_LIST = os.path.join(HERE, "out_list.json")


class IoTester(unittest.TestCase):
    def test_cmd(self):  # pylint: disable=no-self-use
        subprocess.check_call(
            "vidcrawler --help",
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    def test_process_test(self):  # pylint: disable=no-self-use
        subprocess.check_call(
            f'vidcrawler --input_crawl_json "{FETCH_LIST}" --output_json "{OUT_LIST}"',
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )


if __name__ == "__main__":
    unittest.main()
