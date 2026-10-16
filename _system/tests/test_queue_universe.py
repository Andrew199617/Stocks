#!/usr/bin/env python3
"""build_universe.py queue rebuild tests. Run: python _system/tests/test_queue_universe.py
(or python -m pytest _system/tests). Every test writes a throwaway queue in a
temp folder, never the real _system/queue.json, and makes no network request
(main() runs with fetch() replaced by fixture files).

A rebuild used to keep only ticker, queue_pos and status, dropping
claimed_at (pass 2's scoring generation), completed, note, v5_rerun,
started, blocked_date, last_done, refresh_reason (WORKER_SPEC step 2's
re-score path), refresh_date. Covered: merge_queue keeps every surviving
entry verbatim (field values and key order) apart from queue_pos, gives a new
ticker {ticker, queue_pos, status: "pending"} and drops a departed one;
write_queue does that on disk, starts a fresh queue when there is none,
refuses to rebuild over an unreadable one, leaves no temp file and waits for
queue.py's lock; main() end to end under the locale encoding (-X utf8=0,
cp1252 on Windows) with a non-ASCII company name and the notes' "≈"; and
pass 2 after a real rebuild: done reviews stay done, an in-flight review
passes pass2-check / pass2-done, and a re-score is still a new generation.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
SYS = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, SYS)
import build_universe as BU  # noqa: E402
from _lock import locked  # noqa: E402
from test_queue_pass2 import Base, done, rescore  # noqa: E402

FULL = {"ticker": "KR", "queue_pos": 7, "status": "done", "started": "2026-10-12", "completed": "2026-10-14",
        "v5_rerun": True, "blocked_date": "2026-10-13", "note": "DATA_GAP: capex — fixed by override",
        "claimed_at": "2026-10-14T10:00:00-04:00", "last_done": "2026-10-13",
        "refresh_reason": "NEW_FILING: 10-Q for the period ending 2026-08-15", "refresh_date": "2026-10-14"}


def test_merge_keeps_surviving_entries_verbatim():
    old = [dict(FULL), {"ticker": "LFTO", "queue_pos": 1, "status": "blocked_no_data", "note": "NO_DATA: S-1 only"},
           {"ticker": "GONE", "queue_pos": 2, "status": "done", "claimed_at": "2026-10-13T09:00:00-04:00"}]
    q = BU.merge_queue(old, ["NEW", "KR", "LFTO"])
    assert [e["ticker"] for e in q] == ["NEW", "KR", "LFTO"]
    assert [e["queue_pos"] for e in q] == [1, 2, 3]
    assert q[0] == {"ticker": "NEW", "queue_pos": 1, "status": "pending"}
    assert list(q[0]) == ["ticker", "queue_pos", "status"]
    assert q[1] == dict(FULL, queue_pos=2) and list(q[1]) == list(FULL), "every field kept, key order too"
    assert q[2] == {"ticker": "LFTO", "queue_pos": 3, "status": "blocked_no_data", "note": "NO_DATA: S-1 only"}
    assert old[0] == FULL and old[0]["queue_pos"] == 7, "the old entries are not mutated"
    assert BU.merge_queue([], ["A"]) == [{"ticker": "A", "queue_pos": 1, "status": "pending"}]


def _tmp():
    d = tempfile.mkdtemp(prefix="queue_universe_")
    return d, os.path.join(d, "queue.json")


def test_write_queue_on_disk():
    d, path = _tmp()
    try:
        data = BU.write_queue(path, ["A", "B"], "2026-10-16")
        assert data["universe_size"] == 2 and data["built"] == "2026-10-16" and data["cutoff_market_cap_b"] == 40
        with open(path, encoding="utf-8") as f:
            assert json.load(f)["queue"] == [{"ticker": "A", "queue_pos": 1, "status": "pending"},
                                             {"ticker": "B", "queue_pos": 2, "status": "pending"}]
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"built": "2026-10-12", "cutoff_market_cap_b": 40, "universe_size": 2,
                       "queue": [dict(FULL, queue_pos=1), {"ticker": "B", "queue_pos": 2, "status": "pending"}]}, f)
        BU.write_queue(path, ["B", "C", "KR"], "2026-10-17")
        with open(path, encoding="utf-8") as f:
            q = json.load(f)
        assert q["universe_size"] == 3 and [e["ticker"] for e in q["queue"]] == ["B", "C", "KR"]
        assert q["queue"][2] == dict(FULL, queue_pos=3), q["queue"][2]
        assert not [n for n in os.listdir(d) if ".tmp." in n]
        # An unreadable queue stops the rebuild and is left as it is.
        for bad in ("{", "[1, 2]", '{"built": "x"}'):
            with open(path, "w", encoding="utf-8") as f:
                f.write(bad)
            try:
                BU.write_queue(path, ["A"], "2026-10-18")
                raise AssertionError(f"rebuilt over {bad!r}")
            except SystemExit as e:
                assert "cannot read" in str(e) and "no queue progress is lost" in str(e), e
            with open(path, encoding="utf-8") as f:
                assert f.read() == bad
    finally:
        shutil.rmtree(d, ignore_errors=True)


def test_write_queue_waits_for_the_queue_lock():
    """The rebuild's read-merge-write cannot interleave with a claim or done."""
    d, path = _tmp()
    try:
        BU.write_queue(path, ["A"], "2026-10-16")
        finished = threading.Event()

        def rebuild():
            BU.write_queue(path, ["A", "B"], "2026-10-17")
            finished.set()
        with locked(f"{path}.lock"):
            t = threading.Thread(target=rebuild)
            t.start()
            time.sleep(0.5)
            assert not finished.is_set(), "write_queue must wait for queue.py's lock"
        t.join(30)
        assert finished.is_set()
        with open(path, encoding="utf-8") as f:
            assert json.load(f)["universe_size"] == 2
    finally:
        shutil.rmtree(d, ignore_errors=True)


DRIVER = r"""
import json, os, sys
sys.path.insert(0, sys.argv[1])
import build_universe as BU
BU.BASE = sys.argv[2]
fixtures = json.load(open(sys.argv[3], encoding="utf-8"))
def fake_fetch(url, out, ua="Mozilla/5.0"):
    name = "nasdaq" if "nasdaq" in url else "sec"
    data = json.dumps(fixtures[name], ensure_ascii=False).encode("utf-8")
    open(out, "wb").write(data)
    return data
BU.fetch = fake_fetch
BU.main()
"""


def test_main_end_to_end_keeps_progress_and_writes_utf8():
    d = tempfile.mkdtemp(prefix="queue_universe_main_")
    try:
        rows = [{"symbol": "KR", "name": "The Kroger Co. Common Stock", "marketCap": "30000000000", "lastsale": "$45.10"},
                {"symbol": "NSRGY", "name": "Nestlé S.A. Ordinary Shares", "marketCap": "35000000000", "lastsale": "$90"},
                {"symbol": "NEWCO", "name": "Société Nouvelle Inc.", "marketCap": "5000000000", "lastsale": "$12"},
                {"symbol": "BIG", "name": "Too Big Corp", "marketCap": "90000000000", "lastsale": "$300"},
                {"symbol": "SPYX", "name": "Some Index ETF", "marketCap": "1000000000", "lastsale": "$10"}]
        sec = {"data": [[56873, "KROGER CO", "KR", "NYSE"], [1234, "NESTLÉ S.A.", "NSRGY", "OTC"]]}
        fx = os.path.join(d, "fixtures.json")
        with open(fx, "w", encoding="utf-8") as f:
            json.dump({"nasdaq": {"data": {"rows": rows}}, "sec": sec}, f, ensure_ascii=False)
        with open(os.path.join(d, "queue.json"), "w", encoding="utf-8") as f:
            json.dump({"built": "2026-10-12", "cutoff_market_cap_b": 40, "universe_size": 2,
                       "queue": [dict(FULL, queue_pos=1), {"ticker": "GONE", "queue_pos": 2, "status": "pending"}]}, f)
        env = dict(os.environ, PYTHONIOENCODING="utf-8")
        env.pop("PYTHONUTF8", None)
        r = subprocess.run([sys.executable, "-X", "utf8=0", "-c", DRIVER, SYS, d, fx], capture_output=True,
                           text=True, encoding="utf-8", env=env, timeout=60)
        assert r.returncode == 0, r.stderr
        with open(os.path.join(d, "queue.json"), encoding="utf-8") as f:
            q = json.load(f)
        by = {e["ticker"]: e for e in q["queue"]}
        assert set(by) == {"KR", "NSRGY", "NEWCO"}, by
        assert by["KR"] == dict(FULL, queue_pos=by["KR"]["queue_pos"]), by["KR"]
        assert by["NEWCO"] == {"ticker": "NEWCO", "queue_pos": by["NEWCO"]["queue_pos"], "status": "pending"}
        assert sorted(e["queue_pos"] for e in q["queue"]) == [1, 2, 3] and q["universe_size"] == 3
        with open(os.path.join(d, "universe.csv"), encoding="utf-8") as f:
            csv_text = f.read()
        assert "Nestlé S.A." in csv_text and "Société Nouvelle Inc." in csv_text, csv_text
        with open(os.path.join(d, "universe_notes.md"), encoding="utf-8") as f:
            notes = f.read()
        assert "≈" in notes and "# Universe — built" in notes, notes
    finally:
        shutil.rmtree(d, ignore_errors=True)


def test_pass2_after_a_real_rebuild():
    """The stamps survive a rebuild now: nothing reopens, nothing in flight is
    refused, and a later re-score is still a new generation."""
    names = ["KR", "ZS", "EXPE"]
    b = Base([done(t, pos=i + 1, claimed_at=f"2026-10-14T1{i}:00:00-04:00") for i, t in enumerate(names)] +
             [{"ticker": "LFTO", "queue_pos": 4, "status": "pending"}], folders=names)
    try:
        for t in names[:2]:
            assert b.run("pass2-claim").stdout.strip() == t
            assert b.run("pass2-done", t, "done_no_change").returncode == 0
        assert b.run("pass2-claim").stdout.strip() == "EXPE"  # in flight across the rebuild
        before = {t: b.queue(t) for t in names}
        BU.write_queue(b.qpath, ["LFTO", "EXPE", "ZS", "KR", "NEW"], "2026-10-16")
        for t in names:
            assert b.queue(t) == dict(before[t], queue_pos=b.queue(t)["queue_pos"]), t
        assert b.run("pass2-claim").returncode == 1, "a rebuild re-scores nothing"
        assert b.run("pass2-check", "EXPE").returncode == 0
        assert b.run("pass2-done", "EXPE", "done_changed").returncode == 0
        assert b.entry("EXPE")["generation"] == before["EXPE"]["claimed_at"]
        # The refresh reason survives a rebuild (WORKER_SPEC step 2 reads it)...
        assert b.run("refresh", "ZS", "--stdin", stdin="NEW_FILING: 10-Q for the period ending 2026-08-31").returncode == 0
        BU.write_queue(b.qpath, ["ZS", "LFTO", "EXPE", "KR", "NEW"], "2026-10-17")
        assert b.queue("ZS")["refresh_reason"].startswith("NEW_FILING: 10-Q") and b.queue("ZS")["status"] == "pending"
        # ...and the re-score is reviewed again.
        c2 = rescore(b, "ZS")
        r = b.run("pass2-claim")
        assert r.returncode == 0 and r.stdout.strip() == "ZS" and b.entry("ZS")["generation"] == c2, r.stderr
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
