#!/usr/bin/env python3
"""queue.py second-pass generation tests. Run: python _system/tests/test_queue_pass2.py
(or python -m pytest _system/tests). Every test drives the real CLI against a
throwaway STOCKS_BASE (a temp folder with its own _system/queue.json,
_system/second_pass_queue.json and <T>/score.json), never the real queue.

Covers the Codex finding on PR #2 ("refresh second-pass eligibility for each
new scoring generation"): a refreshed and re-scored name is reviewed again;
the claim records the generation it reviews; a done review of an older
generation is eligible again even without the refresh reset; refresh puts a
done review back to pending and leaves live claims, pending entries and
absent entries alone; pass2-done refuses an obsolete worker while the name
awaits its re-score and after the re-score; a live claim is not re-issued
early, an expired one is; entries written before generations existed follow
the documented legacy rules; APP outside the queue; pass2-reset and status
validation unchanged; queue order unchanged. Repair round: a universe
rebuild by the old build_universe.py (which dropped claimed_at) neither
reopens done reviews nor refuses an in-flight one; pass2-check refuses an
obsolete claim before the worker writes and records nothing; a missing queue.json is a plain exit 1; --file moves the
second-pass queue with the primary one. Round 3: both refusals name their
case and what is true in it (pending / being re-scored / blocked: the
re-score rewrites judgment.json, dcf_numbers.json and score.json; re-scored:
nothing will, delete your second_pass.md and leave judgment.json /
score.json); SECOND_PASS.md and both second-pass cron bodies put pass2-check
before every write of the review and say what to do after each refusal.
"""
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
SYS = os.path.dirname(HERE)
QUEUE = os.path.join(SYS, "queue.py")
ET = ZoneInfo("America/New_York")

C1 = "2026-10-14T10:00:00-04:00"  # the first pass-1 claim of a scored name


class Base:
    """A temp STOCKS_BASE with a queue, a second-pass queue and score folders."""

    def __init__(self, queue, pass2=None, folders=()):
        self.dir = tempfile.mkdtemp(prefix="queue_pass2_")
        os.makedirs(os.path.join(self.dir, "_system"))
        self.qpath = os.path.join(self.dir, "_system", "queue.json")
        self.ppath = os.path.join(self.dir, "_system", "second_pass_queue.json")
        self._dump(self.qpath, {"built": "2026-10-12", "queue": queue})
        if pass2 is not None:
            self._dump(self.ppath, {"entries": pass2})
        for t in folders:
            os.makedirs(os.path.join(self.dir, t))
            self._dump(os.path.join(self.dir, t, "score.json"), {"ticker": t, "tier_final": "B"})

    @staticmethod
    def _dump(path, obj):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(obj, f, indent=1)

    def run(self, *args, stdin=None):
        env = dict(os.environ, STOCKS_BASE=self.dir, PYTHONIOENCODING="utf-8")
        return subprocess.run([sys.executable, QUEUE, *args], input=stdin, capture_output=True,
                              text=True, encoding="utf-8", env=env, timeout=60)

    def queue(self, t):
        with open(self.qpath, encoding="utf-8") as f:
            return next(e for e in json.load(f)["queue"] if e["ticker"] == t)

    def entry(self, t):
        try:
            with open(self.ppath, encoding="utf-8") as f:
                return json.load(f)["entries"].get(t)
        except FileNotFoundError:
            return None

    def set_entry(self, t, ent):
        try:
            with open(self.ppath, encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            data = {"entries": {}}
        data["entries"][t] = ent
        self._dump(self.ppath, data)

    def close(self):
        shutil.rmtree(self.dir, ignore_errors=True)


def done(t, pos=1, claimed_at=C1, completed="2026-10-14"):
    e = {"ticker": t, "queue_pos": pos, "status": "done", "completed": completed}
    if claimed_at:
        e["claimed_at"] = claimed_at
    return e


def ago(minutes):
    return (datetime.datetime.now(ET) - datetime.timedelta(minutes=minutes)).isoformat(timespec="seconds")


def rescore(b, t):
    """Pass 1 re-scores a refreshed name: claim, then done."""
    r = b.run("claim")
    assert r.returncode == 0 and r.stdout.strip() == t, f"primary claim: {r.stdout!r} {r.stderr!r}"
    r = b.run("done", t)
    assert r.returncode == 0, r.stderr
    return b.queue(t)["claimed_at"]


def test_refresh_then_rescore_is_reviewed_again():
    """The reviewer's scenario: done review, refresh, re-score -> claimable again."""
    b = Base([done("KR")], folders=["KR"])
    try:
        r = b.run("pass2-claim")
        assert r.returncode == 0 and r.stdout.strip() == "KR", r.stderr
        assert b.entry("KR")["generation"] == C1, b.entry("KR")
        r = b.run("pass2-done", "KR", "done_no_change")
        assert r.returncode == 0, r.stderr
        assert b.entry("KR")["status"] == "done_no_change" and b.entry("KR")["generation"] == C1
        assert b.run("pass2-claim").returncode == 1, "a reviewed generation is not claimable"
        r = b.run("refresh", "KR", "--stdin", stdin="NEW_FILING: 10-Q for the period ending 2026-08-15")
        assert r.returncode == 0, r.stderr
        assert "KR second pass: done_no_change -> pending" in r.stdout, r.stdout
        ent = b.entry("KR")
        assert ent["status"] == "pending" and ent["last_status"] == "done_no_change" and ent["reset_by"] == "refresh", ent
        assert ent["refresh_reason"].startswith("NEW_FILING"), ent
        r = b.run("pass2-claim")
        assert r.returncode == 1, "nothing to review while the name awaits its re-score"
        c2 = rescore(b, "KR")
        assert c2 != C1
        r = b.run("pass2-claim")
        assert r.returncode == 0 and r.stdout.strip() == "KR", f"re-scored name must be reviewed again: {r.stderr!r}"
        assert b.entry("KR")["generation"] == c2, b.entry("KR")
        r = b.run("pass2-done", "KR", "done_changed")
        assert r.returncode == 0, r.stderr
        assert b.entry("KR") == {"status": "done_changed", "date": b.entry("KR")["date"], "generation": c2}
    finally:
        b.close()


def test_older_generation_review_is_eligible_without_the_reset():
    """Versioning holds even if the refresh reset never ran (a crash between
    the two locks, or a refresh made by the old code)."""
    c2 = "2026-10-16T07:05:00-04:00"
    b = Base([done("KR", claimed_at=c2, completed="2026-10-16")],
             pass2={"KR": {"status": "done_no_change", "date": "2026-10-15", "generation": C1}}, folders=["KR"])
    try:
        r = b.run("pass2-claim")
        assert r.returncode == 0 and r.stdout.strip() == "KR", r.stderr
        assert b.entry("KR")["generation"] == c2
    finally:
        b.close()
    b = Base([done("KR")], pass2={"KR": {"status": "done_changed", "date": "2026-10-15", "generation": C1}},
             folders=["KR"])
    try:
        assert b.run("pass2-claim").returncode == 1, "same generation already reviewed"
    finally:
        b.close()


def test_obsolete_worker_cannot_finish():
    b = Base([done("KR")], folders=["KR"])
    try:
        assert b.run("pass2-claim").stdout.strip() == "KR"
        r = b.run("refresh", "KR", "--stdin", stdin="NEW_FILING: 10-K")
        assert r.returncode == 0 and "second pass" not in r.stdout, r.stdout
        assert b.entry("KR")["status"] == "in_progress" and b.entry("KR")["generation"] == C1, \
            "refresh leaves a live claim alone"
        r = b.run("pass2-done", "KR", "done_no_change")
        assert r.returncode == 1 and "REFUSED" in r.stderr and "pending in queue.json" in r.stderr, r.stderr
        assert_done_refused(r.stderr, PENDING_CASE)
        assert b.entry("KR")["status"] == "in_progress", "a refused done records nothing"
        c2 = rescore(b, "KR")
        r = b.run("pass2-done", "KR", "done_changed")
        assert r.returncode == 1 and "re-scored after this claim" in r.stderr and c2 in r.stderr, r.stderr
        assert_done_refused(r.stderr, RESCORED_CASE)
        assert b.entry("KR")["status"] == "in_progress" and b.entry("KR")["generation"] == C1
        assert b.run("pass2-claim").returncode == 1, "a live claim is not re-issued early"
        ent = b.entry("KR")
        ent["claimed_at"] = ago(120)  # the obsolete worker's lease expired (cron timeout 60 min < lease 90)
        b.set_entry("KR", ent)
        r = b.run("pass2-claim")
        assert r.returncode == 0 and r.stdout.strip() == "KR", r.stderr
        assert b.entry("KR")["generation"] == c2
        assert b.run("pass2-done", "KR", "done_no_change").returncode == 0
        assert b.entry("KR")["generation"] == c2
    finally:
        b.close()


def test_expired_claim_same_generation_reclaimable_live_one_not():
    b = Base([done("KR")], pass2={"KR": {"status": "in_progress", "date": "2026-10-15",
                                         "claimed_at": ago(10), "generation": C1}}, folders=["KR"])
    try:
        assert b.run("pass2-claim").returncode == 1, "live lease"
        b.set_entry("KR", {"status": "in_progress", "date": "2026-10-15", "claimed_at": ago(91), "generation": C1})
        r = b.run("pass2-claim")
        assert r.returncode == 0 and r.stdout.strip() == "KR", r.stderr
    finally:
        b.close()


def test_legacy_done_entries():
    """Done before generations existed: counts for the current generation
    unless the score was completed on the review date or later."""
    b = Base([done("KR", completed="2026-10-13")],
             pass2={"KR": {"status": "done_no_change", "date": "2026-10-14"}}, folders=["KR"])
    try:
        assert b.run("pass2-claim").returncode == 1, "score completed before the review day: reviewed"
    finally:
        b.close()
    # The verifier's sequence: review 03:00, old-code refresh 06:30, re-score
    # 07:00, all on 2026-10-14. A date cannot order them, so it is reviewed again.
    b = Base([done("KR", claimed_at="2026-10-14T07:00:00-04:00", completed="2026-10-14")],
             pass2={"KR": {"status": "done_no_change", "date": "2026-10-14"}}, folders=["KR"])
    try:
        r = b.run("pass2-claim")
        assert r.returncode == 0 and r.stdout.strip() == "KR", "same-day completion: eligible again"
    finally:
        b.close()
    b = Base([done("KR", claimed_at="2026-10-15T07:00:00-04:00", completed="2026-10-15")],
             pass2={"KR": {"status": "done_no_change", "date": "2026-10-14"}}, folders=["KR"])
    try:
        r = b.run("pass2-claim")
        assert r.returncode == 0 and r.stdout.strip() == "KR", "score completed after the review: eligible"
    finally:
        b.close()
    # A done queue entry with no claimed_at falls back to its completed date.
    b = Base([done("KR", claimed_at=None, completed="2026-10-13")], folders=["KR"])
    try:
        assert b.run("pass2-claim").stdout.strip() == "KR"
        assert b.entry("KR")["generation"] == "completed 2026-10-13", b.entry("KR")
    finally:
        b.close()


def test_legacy_in_progress_claims():
    """Claimed before generations existed: refused only when the score's
    generation stamp is later than the claim."""
    claim = "2026-10-14T12:00:00-04:00"
    b = Base([done("KR", claimed_at="2026-10-14T09:00:00-04:00")],
             pass2={"KR": {"status": "in_progress", "date": "2026-10-14", "claimed_at": claim}}, folders=["KR"])
    try:
        r = b.run("pass2-done", "KR", "done_no_change")
        assert r.returncode == 0, r.stderr
        assert b.entry("KR")["generation"] == "2026-10-14T09:00:00-04:00"
    finally:
        b.close()
    b = Base([done("KR", claimed_at="2026-10-14T13:00:00-04:00")],
             pass2={"KR": {"status": "in_progress", "date": "2026-10-14", "claimed_at": claim}}, folders=["KR"])
    try:
        r = b.run("pass2-done", "KR", "done_no_change")
        assert r.returncode == 1 and "re-scored after this claim" in r.stderr, r.stderr
        assert_done_refused(r.stderr, RESCORED_CASE)
    finally:
        b.close()


def test_refresh_leaves_pending_and_absent_entries():
    b = Base([done("KR", pos=1), done("ZS", pos=2)], pass2={"KR": {"status": "pending", "date": "2026-10-14"}},
             folders=["KR", "ZS"])
    try:
        for t in ("KR", "ZS"):
            r = b.run("refresh", t, "--stdin", stdin="NEW_FILING: 10-K")
            assert r.returncode == 0 and "second pass" not in r.stdout, r.stdout
        assert b.entry("KR") == {"status": "pending", "date": "2026-10-14"}
        assert b.entry("ZS") is None, "refresh never creates a second-pass entry"
    finally:
        b.close()


def test_app_outside_the_queue():
    b = Base([], folders=["APP"])
    try:
        r = b.run("pass2-claim")
        assert r.returncode == 0 and r.stdout.strip() == "APP", r.stderr
        assert b.entry("APP")["generation"] == "unqueued"
        assert b.run("pass2-done", "APP", "done_no_change").returncode == 0
        assert b.run("pass2-claim").returncode == 1
    finally:
        b.close()
    b = Base([], pass2={"APP": {"status": "done_changed", "date": "2026-10-14"}}, folders=["APP"])
    try:
        assert b.run("pass2-claim").returncode == 1, "a legacy APP review stays done"
    finally:
        b.close()


def test_queue_order_reset_and_validation_unchanged():
    b = Base([done("KR", pos=1), done("ZS", pos=2), done("NOSCORE", pos=3)], folders=["KR", "ZS"])
    try:
        assert b.run("pass2-claim").stdout.strip() == "KR"
        assert b.run("pass2-claim").stdout.strip() == "ZS"
        assert b.run("pass2-claim").returncode == 1, "a done name without score.json is skipped"
        r = b.run("pass2-done", "KR", "bogus")
        assert r.returncode == 2, r.stderr
        r = b.run("pass2-reset", "KR")
        assert r.returncode == 0 and b.entry("KR")["status"] == "pending"
        assert b.run("pass2-claim").stdout.strip() == "KR"
        # pass2-reset is the unchecked escape hatch: it works while the name is being re-scored.
        b.run("pass2-done", "ZS", "done_no_change")
        assert b.run("refresh", "ZS", "--stdin", stdin="NEW_FILING: 10-K").returncode == 0
        assert b.run("pass2-reset", "ZS").returncode == 0
    finally:
        b.close()


def rebuild_universe(b):
    """Rewrite queue.json the way build_universe.py did until 2026-10-16:
    it kept only ticker, queue_pos and status from the old entries. Queue
    files rebuilt then still lack the stamps; the current rebuild keeps every
    entry verbatim (test_queue_universe.py)."""
    with open(b.qpath, encoding="utf-8") as f:
        old = json.load(f)
    q = [{"ticker": e["ticker"], "queue_pos": e["queue_pos"], "status": e.get("status", "pending")}
         for e in old["queue"]]
    b._dump(b.qpath, {"built": "2026-10-16", "cutoff_market_cap_b": 40, "universe_size": len(q), "queue": q})


def test_universe_rebuild_is_not_a_new_generation():
    """The old rebuild dropped claimed_at and completed; no score changed, so
    no done review reopens and no in-flight review is refused."""
    names = ["KR", "ZS", "EXPE"]
    b = Base([done(t, pos=i + 1, claimed_at=f"2026-10-14T1{i}:00:00-04:00") for i, t in enumerate(names)],
             folders=names)
    try:
        for t in names:
            assert b.run("pass2-claim").stdout.strip() == t
            assert b.run("pass2-done", t, "done_no_change").returncode == 0
        assert b.run("pass2-claim").returncode == 1
        rebuild_universe(b)
        r = b.run("pass2-claim")
        assert r.returncode == 1, f"a rebuild re-scores nothing, yet {r.stdout.strip()!r} was re-claimed"
        assert all(b.entry(t)["status"] == "done_no_change" for t in names)
        # A real re-score after the rebuild stamps the entry again and is reviewed.
        assert b.run("refresh", "ZS", "--stdin", stdin="NEW_FILING: 10-Q").returncode == 0
        c2 = rescore(b, "ZS")
        r = b.run("pass2-claim")
        assert r.returncode == 0 and r.stdout.strip() == "ZS" and b.entry("ZS")["generation"] == c2, r.stderr
    finally:
        b.close()
    b = Base([done("KR")], folders=["KR"])
    try:
        assert b.run("pass2-claim").stdout.strip() == "KR"
        rebuild_universe(b)
        assert b.run("pass2-check", "KR").returncode == 0
        r = b.run("pass2-done", "KR", "done_changed")
        assert r.returncode == 0, r.stderr
        assert b.entry("KR")["generation"] == C1, "the claim's generation is kept, not the bare 'done'"
        assert b.run("pass2-claim").returncode == 1
    finally:
        b.close()


def test_pass2_check_before_writes():
    """pass2-check is pass2-done's supersession test with nothing recorded."""
    b = Base([done("KR")], folders=["KR"])
    try:
        assert b.run("pass2-claim").stdout.strip() == "KR"
        with open(b.ppath, "rb") as f:
            before = f.read()
        r = b.run("pass2-check", "KR")
        assert r.returncode == 0 and "KR claim current" in r.stdout, (r.stdout, r.stderr)
        assert b.run("refresh", "KR", "--stdin", stdin="NEW_FILING: 10-Q").returncode == 0
        r = b.run("pass2-check", "KR")
        assert r.returncode == 1 and "REFUSED" in r.stderr and "pending in queue.json" in r.stderr, r.stderr
        assert "its re-score has not started" in r.stderr, r.stderr
        assert_check_refused(r.stderr, PENDING_CASE)
        assert b.run("claim").stdout.strip() == "KR"
        r = b.run("pass2-check", "KR")
        assert r.returncode == 1 and "in_progress in queue.json (being re-scored)" in r.stderr, r.stderr
        assert_check_refused(r.stderr, PENDING_CASE)
        assert b.run("done", "KR").returncode == 0
        r = b.run("pass2-check", "KR")
        assert r.returncode == 1 and "re-scored after this claim" in r.stderr, r.stderr
        assert_check_refused(r.stderr, RESCORED_CASE)
        with open(b.ppath, "rb") as f:
            assert f.read() == before, "pass2-check records nothing"
    finally:
        b.close()


# The two refusal cases (queue.py PENDING / RESCORED) and what each must say.
PENDING_CASE = ("the re-score this name awaits rewrites judgment.json, dcf_numbers.json and score.json",)
RESCORED_CASE = ("newer generation",)


def assert_check_refused(err, case):
    """pass2-check refused: the worker has written nothing and writes nothing."""
    assert "pass2-check REFUSED" in err, err
    assert "Write nothing for this review (no second_pass.md, analysis.md addendum, judgment.json" in err, err
    assert "Delete" not in err, "after a pass2-check refusal there is nothing to delete: " + err
    for phrase in case:
        assert phrase in err, (phrase, err)
    if case is RESCORED_CASE:
        assert "rewrites" not in err, "nothing rewrites the folder after a newer generation: " + err


def assert_done_refused(err, case):
    """pass2-done refused: delete this run's second_pass.md, leave the rest,
    and the message says whether anything will rewrite the folder."""
    assert "pass2-done REFUSED" in err and "Nothing was recorded in the second-pass queue" in err, err
    assert "elete the second_pass.md and any analysis.md '## Second pass' addendum you wrote in this run" in err, err
    if case is PENDING_CASE:
        assert "rewrites judgment.json, dcf_numbers.json and score.json" in err, err
        assert "nothing will rewrite" not in err, err
    else:
        assert "nothing will rewrite what this run wrote" in err, err
        assert "leave judgment.json and score.json as the newer generation left them" in err, err
        assert "the re-score this name awaits" not in err, err
    assert "report nothing" in err.lower(), err


def test_refusals_for_a_blocked_rescore():
    """A re-score that ended blocked is the pending case: the name is not
    done, and whichever run re-scores it rewrites the folder."""
    b = Base([done("KR")], folders=["KR"])
    try:
        assert b.run("pass2-claim").stdout.strip() == "KR"
        assert b.run("refresh", "KR", "--stdin", stdin="NEW_FILING: 10-K").returncode == 0
        assert b.run("claim").stdout.strip() == "KR"
        assert b.run("block", "KR", "--stdin", stdin="DATA_GAP: capex missing for FY2026").returncode == 0
        for args, check in ((("pass2-check", "KR"), assert_check_refused),
                            (("pass2-done", "KR", "done_no_change"), assert_done_refused)):
            r = b.run(*args)
            assert r.returncode == 1, (args, r.stderr)
            assert "blocked_data_gap in queue.json (its re-score is blocked until it is requeued)" in r.stderr, r.stderr
            check(r.stderr, PENDING_CASE)
        assert b.entry("KR")["status"] == "in_progress"
    finally:
        b.close()


def _section(text, heading):
    start = text.index(heading)
    nxt = text.find("\n## ", start + len(heading))
    return text[start:] if nxt < 0 else text[start:nxt]


def test_second_pass_docs_check_before_any_write():
    """SECOND_PASS.md: pass2-check runs before the first write of the review
    (second_pass.md included), the freshness TTM run does not save ttm.json,
    and each refusal says what to do; both cron bodies agree."""
    with open(os.path.join(SYS, "SECOND_PASS.md"), encoding="utf-8") as f:
        doc = f.read()
    steps = " ".join(_section(doc, "## Worker steps").split())  # independent of line wrapping
    check = steps.index("python3 _system/queue.py pass2-check <T>")
    writes = [m.start() for m in re.finditer(r"\bwrite (second_pass\.md|the new judgment\.json)|"
                                             r"append a dated|add `second_pass|rerun the engine", steps)]
    assert len(writes) >= 5 and all(check < w for w in writes), (check, writes)
    assert "paste the output into second_pass.md" not in steps, "step 3 must not write second_pass.md"
    for needle in ("write nothing, report nothing", "Delete the second_pass.md you wrote in this run",
                   "addendum you appended to analysis.md in step 7",
                   "rewrites judgment.json, dcf_numbers.json and score.json",
                   "nothing will rewrite what you wrote",
                   "leave judgment.json and score.json as the new generation left them"):
        assert needle in steps, needle
    fresh = " ".join(_section(doc, "## Filing freshness").split())
    assert "DCF_TTM_NO_WRITE=1 python3 _system/ttm.py" in fresh, "the pre-check TTM run must not save ttm.json"
    for name in ("dcf-second-pass__interval@30m.md", "dcf-second-pass-parallel__interval@15m.md"):
        with open(os.path.join(os.path.dirname(SYS), "automation", "crons", "minutely", name), encoding="utf-8") as f:
            body = f.read().split("\n---\n", 1)[1]
        assert "`queue.py pass2-check <T>` before you write anything for the review (second_pass.md" in body, name
        assert "if it refuses, write nothing" in body, name
        assert "delete the second_pass.md and the analysis.md addendum you wrote in this run" in body, name
        assert "before you touch judgment.json" not in body, name


def test_filing_watch_docstring_names_every_write():
    with open(os.path.join(SYS, "filing_watch.py"), encoding="utf-8") as f:
        src = f.read()
    assert "nothing is written except the queue entries" not in src
    assert "second_pass_queue.json" in src and "back to pending" in src


def test_missing_queue_file_is_a_clean_exit():
    b = Base([], pass2={"APP": {"status": "in_progress", "date": "2026-10-15", "claimed_at": ago(5),
                                "generation": "unqueued"}}, folders=["APP"])
    try:
        os.remove(b.qpath)
        for args in (("pass2-claim",), ("pass2-check", "APP"), ("pass2-done", "APP", "done_no_change")):
            r = b.run(*args)
            assert r.returncode == 1 and "no queue file" in r.stderr and "Traceback" not in r.stderr, (args, r.stderr)
        assert b.entry("APP")["status"] == "in_progress"
        assert b.run("pass2-reset", "APP").returncode == 0, "pass2-reset never reads queue.json"
    finally:
        b.close()


def test_file_flag_moves_the_second_pass_queue():
    """refresh with --file resets the second-pass entry beside that queue file."""
    b = Base([done("KR")], pass2={"KR": {"status": "done_no_change", "date": "2026-10-14", "generation": C1}},
             folders=["KR"])
    alt = tempfile.mkdtemp(prefix="queue_pass2_alt_")
    try:
        aq = os.path.join(alt, "queue.json")
        ap = os.path.join(alt, "second_pass_queue.json")
        Base._dump(aq, {"built": "2026-10-12", "queue": [done("KR")]})
        Base._dump(ap, {"entries": {"KR": {"status": "done_changed", "date": "2026-10-14", "generation": C1}}})
        r = b.run("--file", aq, "refresh", "KR", "--stdin", stdin="NEW_FILING: 10-Q")
        assert r.returncode == 0 and "KR second pass: done_changed -> pending" in r.stdout, r.stdout
        with open(ap, encoding="utf-8") as f:
            assert json.load(f)["entries"]["KR"]["status"] == "pending"
        assert b.entry("KR") == {"status": "done_no_change", "date": "2026-10-14", "generation": C1}, \
            "STOCKS_BASE's second-pass queue is untouched"
        assert b.queue("KR")["status"] == "done"
    finally:
        b.close()
        shutil.rmtree(alt, ignore_errors=True)


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
