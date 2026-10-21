"""Cross-platform exclusive file lock (v5.4).

queue.py and make_score.py used fcntl directly, which does not exist on
Windows — the tooling could not even be imported there, so nothing could be
tested outside the sweep VM. This shim uses fcntl.flock on POSIX and
msvcrt.locking on Windows with identical semantics for our purpose: one
process at a time inside the `with locked(path):` block, blocking until free.
[Codex review r19 of PR #47] on_wait: an optional callable run once, before
blocking, when another process holds the lock (make_score says it waits).
"""
import os, time, contextlib

try:
    import fcntl  # POSIX
except ImportError:  # Windows
    fcntl = None
    import msvcrt


@contextlib.contextmanager
def locked(path, on_wait=None):
    fd = os.open(path, os.O_CREAT | os.O_RDWR)
    try:
        if fcntl is not None:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:   # held by another process
                if on_wait is not None:
                    on_wait()
                fcntl.flock(fd, fcntl.LOCK_EX)
        else:
            try:
                msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
                busy = False
            except OSError:   # held by another process
                busy = True
                if on_wait is not None:
                    on_wait()
            # msvcrt locks a byte range from the current position; LK_LOCK
            # retries ~10x over ~10s then raises — keep waiting like flock.
            while busy:
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
