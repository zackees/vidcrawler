"""
    Stub for error logging.
"""

import sys


def log_error(err_str: str) -> None:  # type: ignore
    """Dummy log error function."""
    sys.stderr.write(f"{err_str}\n")
