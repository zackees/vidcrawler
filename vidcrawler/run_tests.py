"""
    Trampoline to get tests.
"""


def main() -> None:
    import os  # pylint: disable=import-outside-toplevel
    import sys  # pylint: disable=import-outside-toplevel

    os.chdir(os.path.dirname(__file__))
    sys.exit(os.system("pytest testing"))


if __name__ == "__main__":
    main()
