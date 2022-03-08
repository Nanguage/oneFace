import sys

def pytest_sessionstart(session):
    sys.path.insert(0, "./")
