#!/usr/bin/env python3
"""queue.py / filing_watch.py file I/O under concurrency, for running the
tools from a Windows PC. Run: python _system/tests/test_queue_io.py (or
python -m pytest _system/tests). Every test works in a throwaway STOCKS_BASE,
never the real queue.

On Windows os.replace raises PermissionError while another process holds the
target open (a reader such as build_site.py, filing_watch.py or a pass-2
command), and a read that lands while another process replaces the file fails
to open with PermissionError. Covered: queue.py's load retries a parse
failure / PermissionError and raises FileNotFoundError at once; claim and
pass2-claim finish once a reader that held queue.json / second_pass_queue.json
open lets go (before, the save crashed on Windows); a writer process
replacing queue.json in a loop while pass2-check and in-process loads read it
and reap writes it: nothing fails; an unreadable second-pass queue stops the
command instead of being saved over as empty; the lock order: the pass-2
commands never take the queue lock, and refresh releases it before it waits
for the second-pass lock; filing_watch reports an unreadable queue.json
instead of "checked 0 done names" and retries a read that lands mid-replace.
"""
import importlib.util
import json
import os
import subprocess
import sys
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
SYS = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, SYS)
from test_queue_pass2 import Base, done  # noqa: E402
from _lock import locked  # noqa: E402

QUEUE = os.path.join(SYS, "queue.py")
FILING_WATCH = os.path.join(SYS, "filing_watch.py")


def _module(name, path):
    """Load a _system script as a module under a private name (queue.py would
    otherwise shadow, or be shadowed by, the stdlib queue module)."""
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


Q = _module("dcf_queue_under_test", QUEUE)
FW = _module("dcf_filing_watch_under_test", FILING_WATCH)


def _popen(b, *args):
    env = dict(os.environ, STOCKS_BASE=b.dir, PYTHONIOENCODING="utf-8")
    return subprocess.Popen([sys.executable, QUEUE, *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            text=True, encoding="utf-8", env=env)


def _late_fix(path, text, delay=0.3):
    def fix():
        time.sleep(delay)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
    t = threading.Thread(target=fix)
    t.start()
    return t


def test_load_retries_a_parse_failure_and_not_a_missing_file():
    b = Base([done("KR")])
    try:
        with open(b.qpath, "w", encoding="utf-8") as f:
            f.write('{"queue": [')  # unparseable, as a torn read would be
        t = _late_fix(b.qpath, json.dumps({"queue": [done("KR")]}))
        assert Q.load(b.qpath)["queue"][0]["ticker"] == "KR"
        t.join()
        with open(b.qpath, "w", encoding="utf-8") as f:
            f.write("{")
        try:
            Q.load(b.qpath, attempts=3, pause=0.01)
            raise AssertionError("a file that never parses must raise")
        except ValueError:
            pass
        missing = os.path.join(b.dir, "_system", "nope.json")
        t0 = time.time()
        try:
            Q.load(missing)
            raise AssertionError("missing file must raise")
        except FileNotFoundError:
            assert time.time() - t0 < 0.5, "a missing file is not retried"
    finally:
        b.close()


def _held_open_then_released(b, path, args, hold=1.0):
    """Run a queue.py command while this process holds path open, then let go."""
    with open(path, "rb"):
        p = _popen(b, *args)
        time.sleep(hold)
        if os.name == "nt":
            # The save is waiting on the handle we hold; before the retry it had
            # already crashed with PermissionError.
            assert p.poll() is None, ("the save should still be retrying", p.communicate())
    out, err = p.communicate(timeout=60)
    assert p.returncode == 0, (args, out, err)
    assert "PermissionError" not in err and "Traceback" not in err, err
    leftovers = [n for n in os.listdir(os.path.dirname(path)) if ".tmp." in n]
    assert not leftovers, leftovers
    return out


def test_writes_wait_for_a_reader_holding_the_file():
    b = Base([done("KR", pos=1), {"ticker": "ZS", "queue_pos": 2, "status": "pending"}], folders=["KR"])
    try:
        assert _held_open_then_released(b, b.qpath, ("claim",)).strip() == "ZS"
        assert b.queue("ZS")["status"] == "in_progress" and b.queue("ZS")["claimed_at"]
        b.set_entry("KR", {"status": "pending", "date": "2026-10-15"})
        assert _held_open_then_released(b, b.ppath, ("pass2-claim",)).strip() == "KR"
        assert b.entry("KR")["status"] == "in_progress"
    finally:
        b.close()


WRITER = r"""
import importlib.util, json, sys, time
spec = importlib.util.spec_from_file_location("dcf_queue_writer", sys.argv[1])
Q = importlib.util.module_from_spec(spec); spec.loader.exec_module(Q)
path, seconds = sys.argv[2], float(sys.argv[3])
n, end = 0, time.time() + seconds
while time.time() < end:
    data = Q.load(path)
    Q.save(path, data)
    n += 1
print(n)
"""


def test_reads_and_writes_survive_a_concurrent_writer():
    """A second process replaces queue.json in a loop (as pass 1 does on a
    busy PC) while pass2-check reads it, this process reads it, and reap
    rewrites it under the lock: every command and read succeeds."""
    padding = [{"ticker": f"P{i:04d}", "queue_pos": i + 2, "status": "pending", "note": "x" * 40}
               for i in range(1500)]  # a queue.json about the real one's size
    b = Base([done("KR")] + padding, folders=["KR"])
    try:
        assert b.run("pass2-claim").stdout.strip() == "KR"
        env = dict(os.environ, PYTHONIOENCODING="utf-8")
        w = subprocess.Popen([sys.executable, "-c", WRITER, QUEUE, b.qpath, "4"], stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, text=True, env=env)
        reads, procs = 0, []
        end = time.time() + 3.5
        while time.time() < end:
            if len(procs) < 12:
                procs.append(_popen(b, "pass2-check", "KR"))
                procs.append(_popen(b, "reap"))
            assert Q.load(b.qpath)["queue"][0]["ticker"] == "KR"
            reads += 1
            time.sleep(0.01)  # a reader holds the file for a moment, not continuously
        for p in procs:
            out, err = p.communicate(timeout=60)
            assert p.returncode == 0 and "Traceback" not in err, (p.args, out, err)
        out, err = w.communicate(timeout=60)
        assert w.returncode == 0 and "Traceback" not in err, err
        assert int(out) > 0 and reads > 0
        assert b.queue("KR")["status"] == "done" and len(Q.load(b.qpath)["queue"]) == 1501
    finally:
        b.close()


def test_unreadable_second_pass_queue_is_never_saved_over():
    """It used to read as empty, and the next pass2-claim saved a one-entry
    queue over every recorded review."""
    b = Base([done("KR")], pass2={}, folders=["KR"])
    try:
        with open(b.ppath, "w", encoding="utf-8") as f:
            f.write('{"entries": {"ZS": {"status": "done_no_change"')
        with open(b.ppath, "rb") as f:
            before = f.read()
        for args in (("pass2-claim",), ("pass2-reset", "KR")):
            r = b.run(*args)
            assert r.returncode == 1 and "cannot read" in r.stderr and "Traceback" not in r.stderr, (args, r.stderr)
            with open(b.ppath, "rb") as f:
                assert f.read() == before, args
    finally:
        b.close()


def test_pass2_commands_never_take_the_queue_lock():
    """Lock order: with the queue lock held elsewhere, every pass-2 command
    still finishes (it reads queue.json without that lock), so no pass-2 path
    can wait on the queue lock while holding the second-pass lock."""
    b = Base([done("KR")], folders=["KR"])
    try:
        with locked(f"{b.qpath}.lock"):
            for args in (("pass2-claim",), ("pass2-check", "KR"), ("pass2-done", "KR", "done_no_change"),
                         ("pass2-reset", "KR")):
                r = b.run(*args)
                assert r.returncode == 0, (args, r.stderr)
    finally:
        b.close()


def test_refresh_releases_the_queue_lock_before_the_second_pass_lock():
    """refresh writes queue.json, lets go of its lock, then waits for the
    second-pass lock: while it waits, a pass-1 claim still gets through."""
    b = Base([done("KR", pos=1), {"ticker": "ZS", "queue_pos": 2, "status": "pending"}],
             pass2={"KR": {"status": "done_no_change", "date": "2026-10-14", "generation": done("KR")["claimed_at"]}},
             folders=["KR"])
    try:
        with locked(f"{b.ppath}.lock"):
            env = dict(os.environ, STOCKS_BASE=b.dir, PYTHONIOENCODING="utf-8")
            p = subprocess.Popen([sys.executable, QUEUE, "refresh", "KR", "--stdin"], stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", env=env)
            p.stdin.write("NEW_FILING: 10-Q")
            p.stdin.close()
            deadline = time.time() + 30
            while Q.load(b.qpath)["queue"][0]["status"] != "pending":  # Q.load: refresh may be mid-replace
                assert time.time() < deadline, "refresh never updated queue.json"
                time.sleep(0.05)
            r = b.run("claim")
            assert r.returncode == 0 and r.stdout.strip() == "KR", ("queue lock still held", r.stderr)
            assert p.poll() is None, "refresh should be waiting for the second-pass lock"
        out, err = p.communicate(timeout=60)
        assert p.returncode == 0 and "KR second pass: done_no_change -> pending" in out, (out, err)
        assert b.entry("KR")["status"] == "pending"
    finally:
        b.close()


def test_filing_watch_queue_read():
    b = Base([{"ticker": "ZS", "queue_pos": 1, "status": "pending"}])
    try:
        env = dict(os.environ, STOCKS_BASE=b.dir, PYTHONIOENCODING="utf-8")
        r = subprocess.run([sys.executable, FILING_WATCH, "--dry-run"], capture_output=True, text=True,
                           encoding="utf-8", env=env, timeout=60)
        assert r.returncode == 0 and "checked 0 done names" in r.stdout, (r.stdout, r.stderr)
        with open(b.qpath, "w", encoding="utf-8") as f:
            f.write("{")
        r = subprocess.run([sys.executable, FILING_WATCH, "--dry-run"], capture_output=True, text=True,
                           encoding="utf-8", env=env, timeout=60)
        assert r.returncode == 1 and "cannot read" in r.stderr and "checked" not in r.stdout, (r.stdout, r.stderr)
        os.remove(b.qpath)
        r = subprocess.run([sys.executable, FILING_WATCH, "--dry-run"], capture_output=True, text=True,
                           encoding="utf-8", env=env, timeout=60)
        assert r.returncode == 1 and "cannot read" in r.stderr, (r.stdout, r.stderr)
        with open(b.qpath, "w", encoding="utf-8") as f:
            f.write('{"queue": [')
        t = _late_fix(b.qpath, json.dumps({"queue": [done("KR")]}))
        assert FW.load_queue(b.qpath)["queue"][0]["ticker"] == "KR", "a read that lands mid-replace is retried"
        t.join()
    finally:
        b.close()


if __name__ == "__main__":
    fails = 0
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn(); print(f"PASS {name}")
            except AssertionError as e:
                fails += 1; print(f"FAIL {name}: {e}")
            except Exception as e:
                fails += 1; print(f"ERROR {name}: {type(e).__name__}: {e}")
    sys.exit(1 if fails else 0)
