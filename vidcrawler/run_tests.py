import os;
os.chdir(os.path.dirname(__file__))
os.system("python -m unittest discover tests")
