#!/usr/bin/env python3
"""queue.py's quote gate on done and pass2-done (engine 5.7; Andrew's ruling R3 of 2026-10-19 — strict quoting;
design 02 §9 / §10 tests 23-26, 07 §1.17, L2 rebase A21).
Run: python _system/tests/test_queue_quote_gate.py (or python -m pytest _system/tests). Every test drives the real
CLI against a throwaway STOCKS_BASE (a folder built by make_score.py through test_make_score_55's Run harness, plus
its own _system/queue.json and second_pass_queue.json); nothing outside temp dirs is written.

Each test fails on the code before the lane (e22e814: queue.py done / pass2-done record any run):
23 done refuses a 5.7 run whose analysis.md quotes a number no generated file holds — rc 1, the analysis.md line
   named, the queue entry still in progress, the lock never held;
24 done passes once the figure is declared in facts.json and make_score.py re-ran;
25 done refuses a key_numbers.md edited by hand (integrity check I2);
26 controls: a pre-5.7 run with an untraced number and a queue entry with no folder are done as before;
27 pass2-done (done_no_change / done_changed) is gated the same way, before its lock; pass2-reset is not.
Review fixes (2026-10-21), each failing on the lane's first build (cc121e2):
r01 judgment.json edited after make_score (probs_used / moat_score holding an analysis figure) never opens the gate;
r07 a saved method run replaced after make_score keeps done refused until make_score re-runs.
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SYS = os.path.dirname(HERE)
for _p in (HERE, SYS):
    if _p not in sys.path:
        sys.path.insert(0, _p)
from test_make_score_55 import Run, _numbers, T  # noqa: E402
import rulings57  # noqa: E402

QUEUE = os.path.join(SYS, "queue.py")
C1 = "2026-10-14T10:00:00-04:00"
GOOD = "Tier B: weighted IRR 17.00% (base case 17.00%), weighted IV $25.00 at 15% against a $20.00 price.\n"
BAD = GOOD + "\nBuybacks ran at $2.19B last year.\n"
FACT = {"id": "F1", "label": "FY2025 share repurchases", "value": 2.19e9, "unit": "USD", "scale": "B", "precision": 2,
        "period": "FY2025", "kind": "filing", "type": "actual",
        "source": {"form": "10-K", "accession": "0000999001-26-000010", "section": "Item 5 — repurchases",
                   "filed": "2026-02-19"},
        "snippet": "we repurchased $2.19 billion of our common stock", "used_for": ["context"]}


class Q:
    """A make_score-built folder TST plus a queue holding TST in progress (and NOFOLDER, a name without a folder)."""

    def __init__(self, release=None, analysis=BAD):
        n = _numbers() if release is None else _numbers(release=release)
        self.r = Run(n).run()
        assert self.r.rc == 0, self.r.err[-800:]
        self.write("analysis.md", analysis)
        self.qpath = os.path.join(self.r.sysdir, "queue.json")
        with open(self.qpath, "w", encoding="utf-8") as f:
            json.dump({"built": "2026-10-12", "queue": [
                {"ticker": T, "queue_pos": 1, "status": "in_progress", "claimed_at": C1},
                {"ticker": "NOFOLDER", "queue_pos": 2, "status": "in_progress", "claimed_at": C1}]}, f, indent=1)

    def write(self, name, text):
        with open(os.path.join(self.r.folder, name), "w", encoding="utf-8") as f:
            f.write(text if isinstance(text, str) else json.dumps(text, indent=1))

    def queue(self, *args):
        env = dict(os.environ, STOCKS_BASE=self.r.base, PYTHONIOENCODING="utf-8")
        return subprocess.run([sys.executable, QUEUE, *args], capture_output=True, text=True, encoding="utf-8",
                              env=env, timeout=120)

    def status(self, t=T):
        with open(self.qpath, encoding="utf-8") as f:
            return next(e for e in json.load(f)["queue"] if e["ticker"] == t)["status"]

    def close(self):
        self.r.close()


def test_done_refuses_a_57_run_that_fails_the_quote_check():
    """02 test 23: rc 1, the untraced token and its analysis.md line named, the entry still in_progress, no lock
    file left behind (the gate runs before with_lock)."""
    q = Q()
    try:
        p = q.queue("done", T)
        assert p.returncode == 1, (p.returncode, p.stdout, p.stderr)
        assert "queue.py: done REFUSED — TST: analysis.md fails the quote check (engine release" in p.stderr, p.stderr
        assert "analysis.md:3 \"$2.19B\"" in p.stderr and "check_quotes.py TST" in p.stderr, p.stderr
        assert q.status() == "in_progress"
        assert not os.path.exists(q.qpath + ".lock") or os.path.getsize(q.qpath + ".lock") == 0
    finally:
        q.close()


def test_done_passes_once_the_fact_is_declared():
    """02 test 24: declare the figure (facts.json F1), re-run make_score.py: done succeeds."""
    q = Q()
    try:
        # [Integrate L3] added to the run's facts.json (which holds the minimal moat scorecard's facts, rulings57), not
        # written over it: the scorecard make_score re-reads cites them
        rulings57.merge_facts(q.r.folder, [FACT], ticker=T)
        assert q.queue("done", T).returncode == 1, "facts.json not yet rendered by make_score: I3 still fails"
        q.r.run()
        assert q.r.rc == 0, q.r.err[-800:]
        p = q.queue("done", T)
        assert p.returncode == 0 and p.stdout.strip() == f"{T} done", (p.stdout, p.stderr)
        assert q.status() == "done"
    finally:
        q.close()


def test_done_refuses_hand_edited_key_numbers():
    """02 test 25: a number appended to key_numbers.md by hand to pass the gate is caught (I2)."""
    q = Q()
    try:
        with open(os.path.join(q.r.folder, "key_numbers.md"), "a", encoding="utf-8") as f:
            f.write("- Buybacks FY2025: $2.19B\n")
        p = q.queue("done", T)
        assert p.returncode == 1 and "I2: key_numbers.md differs from what make_score.py wrote" in p.stderr, p.stderr
        assert q.status() == "in_progress"
    finally:
        q.close()


def test_done_skips_pre57_and_folderless_entries():
    """02 test 26 (controls): a 5.5.0 run with an untraced number and a queue entry with no folder are done as
    before — pre-5.7 analyses are reported by check_quotes.py --all, never gated."""
    q = Q(release="5.5.0")
    try:
        p = q.queue("done", T)
        assert p.returncode == 0 and q.status() == "done", (p.stdout, p.stderr)
        p = q.queue("done", "NOFOLDER")
        assert p.returncode == 0 and q.status("NOFOLDER") == "done", (p.stdout, p.stderr)
    finally:
        q.close()


def test_judgment_edited_after_make_score_never_opens_the_gate():
    """Review r01 (2026-10-21): no integrity check binds judgment.json to the score, so judgment.json is never a
    source — five numbers typed into probs_used (or a moat_score) after make_score leave an untraced analysis figure
    untraced, and done stays refused. The scenario probabilities still trace: the engine records them in
    dcf_numbers.json (make_score refuses a probs_used that differs from them)."""
    q = Q(analysis=GOOD + "\nOperating margin reached 13.7% last year; the base case carries 30%.\n")
    try:
        p = q.queue("done", T)
        assert p.returncode == 1 and 'analysis.md:3 "13.7%"' in p.stderr and '"30%"' not in p.stderr, p.stderr
        assert "1 number traces to no generated file" in p.stderr, p.stderr      # review: the verb agrees
        jp = os.path.join(q.r.folder, "judgment.json")
        with open(jp, encoding="utf-8") as f:
            j = json.load(f)
        j["probs_used"] = [0.137] + list(j["probs_used"])[1:]
        j["moat_score"] = 13.7
        with open(jp, "w", encoding="utf-8") as f:
            json.dump(j, f, indent=1)
        p = q.queue("done", T)
        assert p.returncode == 1 and 'analysis.md:3 "13.7%"' in p.stderr, (p.returncode, p.stdout, p.stderr)
        assert q.status() == "in_progress"
    finally:
        q.close()


def test_saved_run_replaced_after_make_score_keeps_done_refused():
    """Review r07 (2026-10-21): a dcf_numbers_<label>.json replaced after make_score (--save-run ... --replace, or
    another hash-valid record copied over it) is not the run key_numbers.md rendered — done refuses (I4 names it)
    until make_score re-runs; then the new run's figures trace."""
    import check_quotes as CQ
    from test_make_score_55 import _stamp
    q = Q(analysis=GOOD + "\nThe preliminary run gave a weighted IRR of 14.37%.\n")
    try:
        assert CQ.save_run(q.r.folder, "prelim")[0] == 0
        q.r.run()
        assert q.r.rc == 0, q.r.err[-800:]
        assert q.queue("done", T).returncode == 1
        with open(os.path.join(q.r.folder, "dcf_numbers.json"), encoding="utf-8") as f:
            n = json.load(f)
        with open(os.path.join(q.r.folder, "dcf_numbers_prelim.json"), "w", encoding="utf-8") as f:
            json.dump(_stamp(dict(n, implied_irr_weighted=0.1437)), f, indent=1)
        p = q.queue("done", T)
        assert p.returncode == 1 and ("I4: dcf_numbers_prelim.json changed after make_score.py — re-run "
                                      "make_score.py") in p.stderr, (p.returncode, p.stdout, p.stderr)
        assert q.status() == "in_progress"
        q.r.run()
        assert q.r.rc == 0, q.r.err[-800:]
        p = q.queue("done", T)
        assert p.returncode == 0 and q.status() == "done", (p.stdout, p.stderr)
    finally:
        q.close()


def test_pass2_done_is_gated_and_reset_is_not():
    """07 §1.17 (rebase A21): pass2-done done_no_change / done_changed run the same gate before the second-pass lock
    — a failing 5.7 analysis records nothing; once it passes the review is recorded; pass2-reset (status pending) is
    the unchecked escape hatch."""
    q = Q()
    try:
        with open(q.qpath, encoding="utf-8") as f:
            data = json.load(f)
        data["queue"][0].update(status="done", completed="2026-10-14")
        with open(q.qpath, "w", encoding="utf-8") as f:
            json.dump(data, f)
        p2 = os.path.join(q.r.sysdir, "second_pass_queue.json")
        ent = {"status": "in_progress", "date": "2026-10-15", "claimed_at": "2026-10-15T09:00:00-04:00", "generation": C1}
        with open(p2, "w", encoding="utf-8") as f:
            json.dump({"entries": {T: ent}}, f)
        for status in ("done_no_change", "done_changed"):
            p = q.queue("pass2-done", T, status)
            assert p.returncode == 1 and "queue.py: pass2-done REFUSED — TST: analysis.md fails the quote check" in p.stderr, p.stderr
            assert json.load(open(p2, encoding="utf-8"))["entries"][T] == ent
        q.write("analysis.md", GOOD)
        p = q.queue("pass2-done", T, "done_no_change")
        assert p.returncode == 0, p.stderr
        assert json.load(open(p2, encoding="utf-8"))["entries"][T]["status"] == "done_no_change"
        q.write("analysis.md", BAD)
        p = q.queue("pass2-reset", T)
        assert p.returncode == 0 and json.load(open(p2, encoding="utf-8"))["entries"][T]["status"] == "pending", p.stderr
    finally:
        q.close()


if __name__ == "__main__":
    fails = 0
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"PASS {name}")
            except AssertionError as e:
                fails += 1
                print(f"FAIL {name}: {str(e)[:1500]}")
            except Exception as e:
                fails += 1
                print(f"ERROR {name}: {type(e).__name__}: {e}")
    sys.exit(1 if fails else 0)
