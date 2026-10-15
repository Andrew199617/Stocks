"""Cross-platform exclusive file lock (v5.4).

queue.py and make_score.py used fcntl directly, which does not exist on
Windows — the tooling could not even be imported there, so nothing could be
tested outside the sweep VM. This shim uses fcntl.flock on POSIX and
msvcrt.locking on Windows with identical semantics for our purpose: one
process at a time inside the `with locked(path):` block, blocking until free.
"""
import os, time, contextlib

try:
    import fcntl  # POSIX
except ImportError:  # Windows
    fcntl = None
    import msvcrt


@contextlib.contextmanager
def locked(path):
    fd = os.open(path, os.O_CREAT | os.O_RDWR)
    try:
        if fcntl is not None:
            fcntl.flock(fd, fcntl.LOCK_EX)
        else:
            # msvcrt locks a byte range from the current position; LK_LOCK
            # retries ~10x over ~10s then raises — keep waiting like flock.
            while True:
                try:
                    msvcrt.locking(fd, msvcrt.LK_LOCK, 1)
                    break
                except OSError:
                    time.sleep(0.2)
        yield fd
    finally:
        try:
            if fcntl is not None:
                fcntl.flock(fd, fcntl.LOCK_UN)
            else:
                msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
        except OSError:
            pass
        os.close(fd)
