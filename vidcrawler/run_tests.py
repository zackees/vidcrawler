"""
    Trampoline to get tests.
"""

if __name__ == "__main__":
    import os

    os.chdir(os.path.dirname(__file__))
    os.system("pytest testing")
