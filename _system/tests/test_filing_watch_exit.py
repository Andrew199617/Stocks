#!/usr/bin/env python3
"""filing_watch.py exit codes (engine 5.7, Andrew's ruling R5 of 2026-10-19 — job health; design 05 §5).
Run: python _system/tests/test_filing_watch_exit.py.

The miss it stops: filing_watch.py always exited 0, so an EDGAR outage (every submissions fetch failing) read as a
successful run and run_health could never count it. Now: every fetch failing exits 3; a few name-level errors beside
successful checks still exit 0; an empty done list exits 0. Offline: urllib.request.urlopen and time.sleep are
stubbed in-process (no network, no backoff waits) on a temp STOCKS_BASE.
"""
import contextlib
import importlib
import io
import json
import os
import shutil
import sys
import tempfile
import time
import urllib.request

_REAL_SLEEP = time.sleep

HERE = os.path.dirname(os.path.abspath(__file__))
SYS = os.path.dirname(HERE)
sys.path.insert(0, SYS)


class _Resp(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def _run(base, fail_ciks=None, ok_payload=None, dry=True):
    """filing_watch.main() in this process with the network stubbed; returns (exit code, stdout). dry=False runs the
    real queue.py refresh (a subprocess on the temp base)."""
    old_base, old_open, old_argv = os.environ.get("STOCKS_BASE"), urllib.request.urlopen, sys.argv
    os.environ["STOCKS_BASE"] = base
    sys.modules.pop("filing_watch", None)
    fw = importlib.import_module("filing_watch")
    fw.time.sleep = lambda s: None

    def fake(req, timeout=60):
        url = req.full_url if hasattr(req, "full_url") else str(req)
        if fail_ciks is None or any(f"CIK{c:010d}" in url for c in fail_ciks):
            raise OSError("HTTP Error 503: Service Unavailable")
        return _Resp(json.dumps(ok_payload or {"filings": {"recent": {"form": [], "filingDate": [], "reportDate": []}}}).encode())
    urllib.request.urlopen = fake
    sys.argv = ["filing_watch.py", "--quiet"] + (["--dry-run"] if dry else [])
    out = io.StringIO()
    try:
        with contextlib.redirect_stdout(out):
            try:
                fw.main()
                rc = 0
            except SystemExit as e:
                rc = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
    finally:
        urllib.request.urlopen, sys.argv = old_open, old_argv
        time.sleep = _REAL_SLEEP
        if old_base is None:
            os.environ.pop("STOCKS_BASE", None)
        else:
            os.environ["STOCKS_BASE"] = old_base
        sys.modules.pop("filing_watch", None)
    return rc, out.getvalue()


def _base(tickers):
    b = tempfile.mkdtemp(prefix="filing_watch_t_")
    os.makedirs(os.path.join(b, "_system"))
    with open(os.path.join(b, "_system", "queue.json"), "w", encoding="utf-8") as f:
        json.dump({"queue": [{"ticker": t, "status": "done"} for t in tickers]}, f)
    for i, t in enumerate(tickers, 1):
        os.makedirs(os.path.join(b, t))
        with open(os.path.join(b, t, "dcf_numbers.json"), "w", encoding="utf-8") as f:
            json.dump({"cik": i, "latest_period_end": "2025-12-31", "base_source": "median_of_last_3_fy_oe_per_share"}, f)
    return b


def test_all_fetches_failed_exits_3():
    b = _base(["AAA", "BBB", "CCC"])
    try:
        rc, out = _run(b, fail_ciks=None)
        assert rc == 3, (rc, out)
        assert "checked 3 done names — 0 refreshed, 0 unchanged, 3 errors" in out, out
        assert "submissions fetch failed" in out
    finally:
        shutil.rmtree(b, ignore_errors=True)


def test_some_name_errors_still_exit_0():
    b = _base(["AAA", "BBB", "CCC"])
    try:
        rc, out = _run(b, fail_ciks=[2])
        assert rc == 0, (rc, out)
        assert "2 unchanged, 1 errors" in out, out
    finally:
        shutil.rmtree(b, ignore_errors=True)


def test_no_done_names_exits_0():
    b = _base([])
    try:
        rc, out = _run(b)
        assert rc == 0 and "checked 0 done names" in out, (rc, out)
    finally:
        shutil.rmtree(b, ignore_errors=True)


NEWER_10K = {"filings": {"recent": {"form": ["10-K"], "filingDate": ["2027-02-20"], "reportDate": ["2026-12-31"]}}}


def test_every_refresh_failing_exits_3():
    """[whole-PR review fix, 2026-10-21; fails on 6dd4a4a] Three done names with a newer 10-K and a malformed
    second_pass_queue.json (queue.py refresh refuses it): the run counted all three as refreshed before queue.py ran,
    printed "3 refreshed ... 3 errors" and exited 0, so run_health recorded ok while nothing was re-queued. A name is
    refreshed only once queue.py refresh exits 0; every attempted refresh failing is a failed run (exit 3). With a
    well-formed file the same run refreshes the three and exits 0."""
    b = _base(["AAA", "BBB", "CCC"])
    try:
        with open(os.path.join(b, "_system", "second_pass_queue.json"), "w", encoding="utf-8") as f:
            json.dump({"entries": []}, f)
        rc, out = _run(b, fail_ciks=[], ok_payload=NEWER_10K, dry=False)
        assert rc == 3, (rc, out)
        assert "checked 3 done names — 0 refreshed, 0 unchanged, 3 errors (3 queue refreshes failed)" in out, out
        with open(os.path.join(b, "_system", "queue.json"), encoding="utf-8") as f:
            assert all(e["status"] == "done" for e in json.load(f)["queue"])
        with open(os.path.join(b, "_system", "second_pass_queue.json"), "w", encoding="utf-8") as f:
            json.dump({"entries": {}}, f)
        rc, out = _run(b, fail_ciks=[], ok_payload=NEWER_10K, dry=False)
        assert rc == 0 and "3 refreshed, 0 unchanged, 0 errors" in out, (rc, out)
    finally:
        shutil.rmtree(b, ignore_errors=True)


def test_docstring_names_exit_3():
    with open(os.path.join(SYS, "filing_watch.py"), encoding="utf-8") as f:
        assert "Exit 3 when every name's fetch failed" in f.read()


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
