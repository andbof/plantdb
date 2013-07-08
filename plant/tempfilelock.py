from fcntl import flock, LOCK_EX, LOCK_UN
from tempfile import TemporaryFile

class TempfileLock:

    def __init__(self):
        self.handle   = TemporaryFile()

    def lock(self):
        flock(self.handle, LOCK_EX)

    def unlock(self):
        flock(self.handle, LOCK_UN)

    def __del__(self):
        self.handle.close()
