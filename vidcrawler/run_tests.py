"""
    Trampoline to get tests.
"""


if __name__ == "__main__":
    import os
    import sys

    os.chdir(os.path.dirname(__file__))
    sys.exit(os.system("pytest testing"))
