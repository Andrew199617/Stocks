#!/usr/bin/env python3
"""pr_worktree.py — per-company PR worktrees (engine 5.7, Andrew's ruling R5 of 2026-10-19; design 05 §3, §9 and the
L5 rebase amendments A1, A4, A5, A10-A14; lane default Q12 (b)). Run: python _system/tests/test_pr_worktree.py.

Offline: a local bare origin seeded with this tree's real _system/*.py (so the PR worktree runs the real make_score
and check_quotes), a sweep clone holding a synthetic folder TST scored by that make_score (test_make_score_55's
record builder with the 5.7 obligations, no overrides, so nothing is spawned), gh replaced by a stub ($STOCKS_GH),
time by $STOCKS_NOW, PR_ROOT by $STOCKS_PR_ROOT.

The misses it stops: two PR agents in one worktree; hand-constructed registry deltas (#33, #38); stale-release
scores published as current (MOH #37, ESTC #35); review fixes made only in the worktree (HUT #33). Covered: acquire
makes the lock and a sparse worktree (only the top level, _system/ and TST/); a second acquire is refused (exit 4,
holder and expiry named); dcf/T is taken -> dcf/T-<claim date> -> -2; an expired lock is reaped by exactly one of
two racing acquires; an expired lock over a dirty worktree refuses until discard; release by another holder refuses
without --force; a stale-release folder is rebuilt and labelled under Q12 (b) and refused under policy "refuse"
unless kind rebuild; prepare re-derives only TST's registry entries; a sweep score that differs from the rebuild is
refused naming the field; check_quotes gates a 5.7 run and is skipped on a 5.5 run; a lost acquired-IPR&D deferred-
payment record refuses; a record file main has that the sweep folder lost refuses; open refuses paths outside the
company scope and a worktree changed since prepare; the backlog is append-only; open stages only the allowed paths,
pushes and calls gh pr create; the title shapes; restack re-derives the registry and renumbers the backlog block;
reap removes the clean worktree of a merged PR and keeps a dirty one; a review round reuses the branch and pushes;
the bulk set is all-or-nothing and opens one Rebuild PR; backlog-next; PR_PROTOCOL.md names every subcommand; the
real ENGINE_BACKLOG.md parses.
Review fixes (2026-10-21): prepare scores against the sweep tree's _system/industry_returns.json, names
moat_evidence.industry_file when the sweep score used another build, and a company PR never carries the file while
a bulk PR does; prepare / open / push / restack need --holder and refuse an expired holder after a takeover (exit
4), and a takeover during prepare never lets the old holder's lock write land; reaping is serialized by the lease
guard (an interleaved second reaper cannot rename the winner's lock away); reap keeps the worktree of an OPEN PR on
a reused dcf/<T> and one holding unpushed commits.
"""
import contextlib
import datetime
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ops_harness as H  # noqa: E402
import dcf_engine as E  # noqa: E402

CUR = E.ENGINE_RELEASE
T = "TST"
NOW = "2026-10-21T10:00:00"
LATER = "2026-10-21T14:30:00"   # past a 3-hour lease taken at NOW
try:
    BACKLOG = open(os.path.join(H.SYS, "ENGINE_BACKLOG.md"), encoding="utf-8").read().replace("\r\n", "\n")
except OSError:   # a tree without the backlog (the code before R5): every test below fails on its own assertion
    BACKLOG = ""
OTH_ENTRY = {"ticker": "OTH", "event": "tier_override", "date": "2026-10-14", "tier_by_numbers": "A", "tier_final": "B",
             "reason": "test: insurer float, softened one notch (NI_OCF gap 48%)"}
ZZZ_ENTRY = {"ticker": "ZZZ", "event": "tier_override", "date": "2026-10-15", "tier_by_numbers": "B", "tier_final": "C",
             "reason": "test: a second ticker's entry (gap 31%)"}
DEFERRED = {"ticker": T, "event": "iprd_deferred_payment", "date": "2026-10-19", "deal": "Test Bio",
            "first_charged_period": "2023-12-31",
            "contingent_total": {"value": 100e6, "source": "0000999001-26-000090, Note 5 (contingent consideration)"},
            "paid_to_date": 20e6, "periods": [{"period": "2025-12-31", "amount": 20e6}]}


class Case:
    """origin (real code + registry + backlog + another folder OTH), a sweep clone with TST scored there."""

    def __init__(self, release=CUR, analysis="# TST\nTest analysis.\n", registry=None, tickers=(T,),
                 claimed_at="2026-10-19T14:02:00-04:00", on_main=False):
        files = {"_system/overrides_registry.json": registry or {"entries": [OTH_ENTRY, ZZZ_ENTRY]},
                 "_system/ENGINE_BACKLOG.md": BACKLOG,
                 "OTH/score.json": {"ticker": "OTH", "tier_final": "B"}, "OTH/analysis.md": "# OTH\n"}
        self.o = H.make_origin(files, code=True, prefix="prw_")
        self.c = H.clone(self.o)
        self.root = os.path.join(self.o.root, "prroot")
        self.gh_dir = os.path.join(self.o.root, "gh")
        self.stub = H.fake_gh(self.gh_dir, {"pr create": "https://github.com/o/r/pull/101\n", "pr list": []})
        with open(os.path.join(self.c, "_system", "queue.json"), "w", encoding="utf-8") as f:
            json.dump({"queue": [{"ticker": t, "status": "done", "completed": "2026-10-19", "claimed_at": claimed_at}
                                 for t in tickers]}, f)
        for t in tickers:
            n = H.numbers(release=release)
            H.write_folder(self.c, t, n, H.judgment(n), extra={"analysis.md": analysis.replace("TST", t),
                                                                "prices.json": {"close": 20.0}})
            self.score(t)
        if on_main:
            H.commit_in(self.c, [f"{t}/" for t in tickers] + ["_system/overrides_registry.json"], "folders on main")

    def score(self, t=T):
        r = H.make_score(self.c, t, code_dir=os.path.join(self.c, "_system"))
        assert r.returncode == 0, f"make_score on the sweep tree refused {t}: {r.stderr}"

    @property
    def wt(self):
        return os.path.join(self.root, T)

    def env(self, now=NOW, **kw):
        e = {"STOCKS_PR_ROOT": self.root, "STOCKS_NOW": now, "STOCKS_GH": self.stub, "STOCKS_REPO_SLUG": "o/r"}
        e.update(kw)
        return e

    def pw(self, *args, now=NOW, **kw):
        return H.run("pr_worktree.py", *args, base=self.c, env=self.env(now, **kw))

    def ok(self, *args, now=NOW, **kw):
        r = self.pw(*args, now=now, **kw)
        assert r.returncode == 0, f"pr_worktree {args} exited {r.returncode}: {r.stdout} {r.stderr}"
        return r

    def acquire(self, holder="agent-1", kind="pass1", now=NOW):
        return self.ok("acquire", T, "--holder", holder, "--kind", kind, now=now)

    def body(self, text="## Verdict\nTest body.\n"):
        p = os.path.join(self.o.root, "body.md")
        with open(p, "w", encoding="utf-8") as f:
            f.write(text)
        return p

    def lock(self, t=T):
        with open(os.path.join(self.root, ".locks", f"{t}.lock.json"), encoding="utf-8") as f:
            return json.load(f)

    def gh_responses(self, resp):
        with open(os.path.join(self.gh_dir, "gh_responses.json"), "w", encoding="utf-8") as f:
            json.dump(resp, f)

    def close(self):
        H.git(self.c, "worktree", "prune", check=False)
        self.o.close()


def _inproc(case, argv, policy=None, now=NOW):
    """pr_worktree.main(argv) in this process (to flip the module's STALE_RELEASE_POLICY switch)."""
    import pr_worktree as P
    old_env = {k: os.environ.get(k) for k in ("STOCKS_BASE", "STOCKS_PR_ROOT", "STOCKS_NOW", "STOCKS_GH",
                                              "STOCKS_REPO_SLUG")}
    old_policy = P.STALE_RELEASE_POLICY
    os.environ.update(dict(case.env(now), STOCKS_BASE=case.c))
    if policy:
        P.STALE_RELEASE_POLICY = policy
    out, err = io.StringIO(), io.StringIO()
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = P.main(argv)
    finally:
        P.STALE_RELEASE_POLICY = old_policy
        for k, v in old_env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
    return rc, out.getvalue(), err.getvalue()


def test_acquire_creates_lock_and_sparse_worktree():
    c = Case()
    try:
        r = c.acquire()
        assert f"branch dcf/{T}" in r.stdout, r.stdout
        lk = c.lock()
        assert lk["holder"] == "agent-1" and lk["kind"] == "pass1" and lk["branch"] == f"dcf/{T}", lk
        assert lk["base_sha"] == c.o.head() and os.path.normcase(lk["worktree"]) == os.path.normcase(c.wt), lk
        assert lk["expires_at"] == "2026-10-21T13:00:00-04:00", lk
        top = sorted(os.listdir(c.wt))
        assert "_system" in top and "OTH" not in top, top
        assert os.path.isfile(os.path.join(c.wt, "_system", "make_score.py"))
        assert H.git(c.wt, "rev-parse", "--abbrev-ref", "HEAD").strip() == f"dcf/{T}"
        assert H.git(c.wt, "status", "--porcelain").strip() == "", "a fresh worktree is clean"
    finally:
        c.close()


def test_second_acquire_is_refused_while_held():
    c = Case()
    try:
        c.acquire()
        r = c.pw("acquire", T, "--holder", "agent-2", "--kind", "pass1", now="2026-10-21T11:00:00")
        assert r.returncode == 4, r.stdout + r.stderr
        assert (f"pr_worktree: {T} is held by agent-1 (kind pass1, acquired 10:00 ET, expires 13:00 ET) — another "
                "agent is cutting this PR; do not use its worktree. Finish without touching it.") in r.stderr, r.stderr
        assert c.lock()["holder"] == "agent-1"
    finally:
        c.close()


def test_branch_takes_a_date_suffix_when_dcf_T_exists():
    c = Case()
    try:
        H.git(c.o.seed, "push", "-q", "origin", f"main:refs/heads/dcf/{T}")
        r = c.acquire()
        assert f"branch dcf/{T}-20261019" in r.stdout, r.stdout
        c.ok("release", T, "--holder", "agent-1", "--remove-worktree")
        H.git(c.o.seed, "push", "-q", "origin", f"main:refs/heads/dcf/{T}-20261019")
        H.git(c.c, "branch", "-q", "-D", f"dcf/{T}-20261019")
        r = c.acquire()
        assert f"branch dcf/{T}-20261019-2" in r.stdout, r.stdout
    finally:
        c.close()


def test_expired_lock_is_reaped_once():
    c = Case()
    try:
        c.acquire()
        results = {}

        def go(h):
            results[h] = c.pw("acquire", T, "--holder", h, "--kind", "rescore", now=LATER)
        ts = [threading.Thread(target=go, args=(h,)) for h in ("racer-a", "racer-b")]
        for t in ts:
            t.start()
        for t in ts:
            t.join()
        rcs = sorted(r.returncode for r in results.values())
        assert rcs == [0, 4], {h: (r.returncode, r.stderr[-300:]) for h, r in results.items()}
        winner = next(h for h, r in results.items() if r.returncode == 0)
        assert c.lock()["holder"] == winner
        log = open(os.path.join(c.root, ".locks", "reaped.log"), encoding="utf-8").read()
        assert log.count("reaped TST lock held by agent-1") == 1, log
    finally:
        c.close()


def test_expired_lock_with_dirty_worktree_refuses_until_discard():
    c = Case()
    try:
        c.acquire()
        os.makedirs(os.path.join(c.wt, T), exist_ok=True)   # a new ticker: main has no TST/ yet
        with open(os.path.join(c.wt, T, "scratch.txt"), "w", encoding="utf-8") as f:
            f.write("half-done work\n")
        r = c.pw("acquire", T, "--holder", "agent-2", "--kind", "pass1", now=LATER)
        assert r.returncode == 1 and "uncommitted changes" in r.stderr and "discard" in r.stderr, r.stderr
        assert os.path.exists(os.path.join(c.wt, T, "scratch.txt")), "the expired holder's work is never thrown away"
        r = c.pw("acquire", T, "--holder", "agent-2", "--kind", "pass1", now=LATER)
        assert r.returncode == 1 and "discard" in r.stderr, r.stderr
        assert c.pw("discard", T, now=LATER).returncode == 2, "discard needs --force"
        c.ok("discard", T, "--force", now=LATER)
        assert not os.path.exists(c.wt)
        c.acquire("agent-2", now=LATER)
    finally:
        c.close()


def test_release_by_another_holder_refuses_without_force():
    c = Case()
    try:
        c.acquire()
        r = c.pw("release", T, "--holder", "agent-2")
        assert r.returncode == 1 and "held by agent-1" in r.stderr, r.stderr
        c.ok("release", T, "--holder", "agent-2", "--force")
        assert not os.path.exists(os.path.join(c.root, ".locks", f"{T}.lock.json"))
    finally:
        c.close()


def test_prepare_stale_release_rebuilds_under_q12b_and_refuses_under_policy_refuse():
    c = Case(release="5.5.0", analysis="# TST\nRevenue grew 37.25% last year.\n")
    try:
        c.acquire()
        rc, out, err = _inproc(c, ["prepare", T, "--holder", "agent-1"], policy="refuse")
        assert rc == 1, out + err
        assert (f"{T}/dcf_numbers.json is engine release 5.5.0; origin/main is {CUR} — re-run the engine") in err, err
        assert "(MOH #37, ESTC #35)" in err, err
        r = c.ok("prepare", T, "--holder", "agent-1")   # default STALE_RELEASE_POLICY: lane default Q12 (b)
        assert f"engine output is release 5.5.0, predating {CUR}" in r.stdout, r.stdout
        assert "check_quotes n/a (pre-5.7 run)" in r.stdout, "a 5.5 run skips the quote gate (37.25% is untraced)"
        prep = c.lock()["prepared"]
        assert prep["tickers"][0]["stale_release"] == {"run": "5.5.0", "main": CUR}, prep
        s = json.load(open(os.path.join(c.wt, T, "score.json"), encoding="utf-8"))
        assert s.get("alert_eligible") is False and s.get("exit_alert_eligible") is False, "stale release: gates closed"
        r = c.pw("release", T, "--holder", "agent-1", "--remove-worktree")
        assert r.returncode == 1 and "uncommitted changes" in r.stderr, "a prepared worktree is never removed silently"
        c.ok("release", T, "--holder", "agent-1")
        c.ok("discard", T, "--force")
        c.acquire(kind="rebuild")
        rc, out, err = _inproc(c, ["prepare", T, "--holder", "agent-1"], policy="refuse")
        assert rc == 0, "kind rebuild prepares a stale-release folder under either policy: " + err
        c.ok("open", T, "--holder", "agent-1", "--body-file", c.body())
        branch = c.lock()["branch"]   # dcf/TST-20261019: the discarded worktree's local dcf/TST branch stays
        msg = H.git(c.o.bare, "log", "-1", "--format=%B", branch)
        assert f"the engine output predates release {CUR}" in msg and "alert gates closed by the stale-release rule" in msg
        assert "lane default Q12 (b)" in msg, msg
    finally:
        c.close()


def test_prepare_rederives_registry_for_the_ticker_only():
    c = Case()
    try:
        c.acquire()
        c.ok("prepare", T, "--holder", "agent-1")
        reg = json.load(open(os.path.join(c.wt, "_system", "overrides_registry.json"), encoding="utf-8"))
        others = [e for e in reg["entries"] if e.get("ticker") != T]
        assert others == [OTH_ENTRY, ZZZ_ENTRY], others
        mine = [e for e in reg["entries"] if e.get("ticker") == T]
        sweep = json.load(open(os.path.join(c.c, "_system", "overrides_registry.json"), encoding="utf-8"))
        assert [e.get("event") for e in mine] == [e.get("event") for e in sweep["entries"] if e.get("ticker") == T]
        prep = c.lock()["prepared"]
        assert prep["registry_entries"] == {"before": 0, "after": len(mine)}, prep["registry_entries"]
        assert prep["origin_sha"] == c.o.head() and prep["engine_release"] == CUR
        assert prep["tickers"][0]["check_quotes"] == "pass" and prep["tickers"][0]["score_from_run"] is True
        changed = sorted(p for _, p in [(None, x[3:]) for x in H.git(c.wt, "status", "--porcelain", "-uall").splitlines()])
        assert all(p.startswith(f"{T}/") or p == "_system/overrides_registry.json" for p in changed), changed
        assert f"{T}/prices.json" not in changed, "a cache is never copied into the PR"
    finally:
        c.close()


def test_prepare_refuses_when_the_rebuilt_score_differs():
    c = Case()
    try:
        p = os.path.join(c.c, T, "score.json")
        s = json.load(open(p, encoding="utf-8"))
        s["tier_final"] = "D"
        json.dump(s, open(p, "w", encoding="utf-8"), indent=1)
        c.acquire()
        r = c.pw("prepare", T, "--holder", "agent-1")
        assert r.returncode == 1, r.stdout
        assert "differs from the sweep tree's (tier_final D → B" in r.stderr and "scored on other code" in r.stderr, r.stderr
        assert not c.lock()["prepared"]
    finally:
        c.close()


def test_prepare_compares_every_57_lanes_score_block():
    """Integrate L5 (07 G13, L5L6 rebase A4 / P2; 08 section 9 item 9; 11 section 7's L5 row): prepare's decision
    fields are make_score.SCORE_DECISION_KEYS plus override_impact.unblocks_tier (PR_PROTOCOL.md section 3), and with
    every lane merged that set holds each 5.7 score block — L1 misfit_notch / misfit_sector_set_aside, L4
    interim_bridge / interim_bridge_declined, R7 base_alternatives, L3 moat_evidence (L3b's fade inside it), L8
    share_classes / up_c_check. No extra path names a judgment field make_score never writes at the top of
    score.json: R7's ttm_rejection_reason / ttm_unavailable_reason live inside base_alternatives and L8's
    up_c_suspect_reason inside up_c_check, so a top-level path for them compared nothing. End to end: a sweep score
    whose R7 or L8 block differs from the rebuild at main's code is refused, naming the block."""
    import make_score as M
    import pr_worktree as P
    blocks = {"misfit_notch", "misfit_sector_set_aside", "interim_bridge", "interim_bridge_declined",
              "base_alternatives", "moat_evidence", "share_classes", "up_c_check"}
    assert blocks <= set(M.SCORE_DECISION_KEYS), sorted(blocks - set(M.SCORE_DECISION_KEYS))
    assert P.EXTRA_DECISION_PATHS == ("override_impact.unblocks_tier",), P.EXTRA_DECISION_PATHS
    c = Case()
    try:
        p = os.path.join(c.c, T, "score.json")
        clean = json.load(open(p, encoding="utf-8"))
        assert not {"base_alternatives", "up_c_check", "ttm_rejection_reason"} & set(clean), sorted(clean)
        c.acquire()
        for key, block in (("base_alternatives", {"schema": 1, "ttm_rejection_reason": "OCF fell $9.99/sh"}),
                           ("up_c_check", {"suspect": True, "s": 0.4, "suppressed_by": "up_c_suspect_reason"})):
            json.dump(dict(clean, **{key: block}), open(p, "w", encoding="utf-8"), indent=1)
            r = c.pw("prepare", T, "--holder", "agent-1")
            assert r.returncode == 1, r.stdout
            assert f"differs from the sweep tree's ({key} {{" in r.stderr and "→ <absent>" in r.stderr, r.stderr
            assert not c.lock()["prepared"]
        json.dump(clean, open(p, "w", encoding="utf-8"), indent=1)
        c.ok("prepare", T, "--holder", "agent-1")
    finally:
        c.close()


def test_prepare_runs_check_quotes_on_57_runs():
    c = Case(analysis="# TST\nRevenue grew 37.25% last year.\n")
    try:
        c.acquire()
        r = c.pw("prepare", T, "--holder", "agent-1")
        assert r.returncode == 1, r.stdout
        assert f"check_quotes.py refused {T}/analysis.md:" in r.stderr and "never in the worktree" in r.stderr, r.stderr
    finally:
        c.close()


def test_prepare_refuses_a_lost_deferred_payment_period():
    c = Case()
    try:
        import make_score as M
        assert M.registry_entry_problem(DEFERRED) is None, M.registry_entry_problem(DEFERRED)
        p = os.path.join(c.c, "_system", "overrides_registry.json")
        reg = json.load(open(p, encoding="utf-8"))
        reg["entries"].append(DEFERRED)   # the sweep tree recorded a deal period an unmerged generation never brought
        json.dump(reg, open(p, "w", encoding="utf-8"), indent=1)
        c.acquire()
        r = c.pw("prepare", T, "--holder", "agent-1")
        assert r.returncode == 1, r.stdout
        assert (f"{T}'s acquired-IPR&D deferred-payment record differs from the sweep tree's (deal Test Bio) — the "
                "lifetime record must reach main unchanged; restack, or ask the main agent") in r.stderr, r.stderr
    finally:
        c.close()


def test_prepare_refuses_a_record_file_main_has_and_the_sweep_lost():
    c = Case(on_main=True)
    try:
        H.commit_on_origin(c.o, f"{T}/second_pass.md", "# second pass\n", "pass 2 on main")
        H.git(c.c, "pull", "-q", "--ff-only")
        os.remove(os.path.join(c.c, T, "second_pass.md"))
        c.acquire(kind="rescore")
        r = c.pw("prepare", T, "--holder", "agent-1")
        assert r.returncode == 1, r.stdout
        assert f"{T}/second_pass.md is on main but not in the sweep folder" in r.stderr, r.stderr
    finally:
        c.close()


def test_open_refuses_paths_outside_the_company_scope():
    c = Case()
    try:
        c.acquire()
        c.ok("prepare", T, "--holder", "agent-1")
        with open(os.path.join(c.wt, "_system", "make_score.py"), "a", encoding="utf-8") as f:
            f.write("# edited in the worktree\n")
        r = c.pw("open", T, "--holder", "agent-1", "--body-file", c.body())
        assert r.returncode == 1, r.stdout
        assert ("refusing to commit — the worktree changes paths a company PR may not carry: _system/make_score.py"
                in r.stderr), r.stderr
        H.git(c.wt, "checkout", "--", "_system/make_score.py")
        with open(os.path.join(c.wt, T, "analysis.md"), "a", encoding="utf-8") as f:
            f.write("A fix made only in the worktree.\n")
        r = c.pw("open", T, "--holder", "agent-1", "--body-file", c.body())
        assert r.returncode == 1 and "changed since prepare" in r.stderr and "never the worktree" in r.stderr, r.stderr
        assert H.gh_calls(c.gh_dir) == [], "nothing reached gh"
    finally:
        c.close()


def _append(wt, text):
    with open(os.path.join(wt, "_system", "ENGINE_BACKLOG.md"), "a", encoding="utf-8", newline="\n") as f:
        f.write(text)


# The ids are read from this tree's ENGINE_BACKLOG.md, never hard-coded: the file is append-only and grows with every
# code PR's deferred defects and every data PR's didnt-fix entry (Integrate L5: R7's follow-up EB-040 made a fixed
# "EB-040" the id of a real entry, and the first data-PR append on main would have done the same).
_BL_IDS = [int(x) for x in re.findall(r"^### EB-(\d{3,}) — ", BACKLOG, re.M)]
NEXT_ID = (max(_BL_IDS) + 1) if _BL_IDS else 1   # what `pr_worktree.py backlog-next` prints for this tree
NEW_EB, AFTER_EB, LAST_EB = (f"EB-{k:03d}" for k in (NEXT_ID, NEXT_ID + 1, NEXT_ID - 1))
ENTRY_NEW = (f"\n### {NEW_EB} — dcf_engine.py:test — a test defect found in review\n- Opened: 2026-10-21, TST PR #101\n"
             "- Status: open\n- Threads: https://github.com/Andrew199617/Stocks/pull/101#discussion_r1 (TST, P3)\n"
             "- Effect: test effect $1.00\n- Fix sketch: test fix\n")


def test_open_backlog_is_append_only():
    c = Case()
    try:
        c.acquire()
        c.ok("prepare", T, "--holder", "agent-1")
        p = os.path.join(c.wt, "_system", "ENGINE_BACKLOG.md")
        text = open(p, encoding="utf-8").read()
        with open(p, "w", encoding="utf-8", newline="\n") as f:
            f.write(text.replace("- Status: open", "- Status: fixed in PR #101 (2026-10-21)", 1) + ENTRY_NEW)
        r = c.pw("open", T, "--holder", "agent-1", "--body-file", c.body())
        assert r.returncode == 1 and "append-only in a data PR: the diff edits or removes 1 existing line" in r.stderr, r.stderr
        with open(p, "w", encoding="utf-8", newline="\n") as f:
            f.write(text + ENTRY_NEW.replace(NEW_EB, LAST_EB))
        r = c.pw("open", T, "--holder", "agent-1", "--body-file", c.body())
        assert r.returncode == 1 and f"{LAST_EB} is already used on main" in r.stderr, r.stderr
        with open(p, "w", encoding="utf-8", newline="\n") as f:
            f.write(text + ENTRY_NEW.replace("- Threads: https://github.com/Andrew199617/Stocks/pull/101#discussion_r1",
                                             "- Threads: none"))
        r = c.pw("open", T, "--holder", "agent-1", "--body-file", c.body())
        assert r.returncode == 1 and "Threads line holds no PR thread URL" in r.stderr, r.stderr
        with open(p, "w", encoding="utf-8", newline="\n") as f:
            f.write(text + ENTRY_NEW)
        c.ok("open", T, "--holder", "agent-1", "--body-file", c.body())
        names = H.git(c.o.bare, "diff", "--name-only", "main", f"dcf/{T}").split()
        assert "_system/ENGINE_BACKLOG.md" in names, names
    finally:
        c.close()


def test_open_stages_only_allowed_paths_and_calls_gh():
    c = Case()
    try:
        c.acquire()
        c.ok("prepare", T, "--holder", "agent-1")
        r = c.ok("open", T, "--holder", "agent-1", "--body-file", c.body(), "--trailer", "Co-Authored-By: Test Agent <t@test.invalid>")
        assert r.stdout.strip() == "https://github.com/o/r/pull/101", r.stdout
        names = sorted(H.git(c.o.bare, "diff", "--name-only", "main", f"dcf/{T}").split())
        assert names and all(n.startswith(f"{T}/") or n == "_system/overrides_registry.json" for n in names), names
        assert f"{T}/prices.json" not in names and f"{T}/score.json" in names, names
        call = H.gh_calls(c.gh_dir)[-1]
        assert call[:9] == ["pr", "create", "--repo", "o/r", "--base", "main", "--head", f"dcf/{T}", "--title"], call
        assert call[9] == f"DCF pass 1: {T} — Test Co — Tier B, weighted IRR 17.00%", call[9]
        msg = H.git(c.o.bare, "log", "-1", "--format=%B", f"dcf/{T}")
        assert msg.startswith(call[9]) and "## Mechanics" in msg and msg.rstrip().endswith(
            "Co-Authored-By: Test Agent <t@test.invalid>"), msg
        assert f"- Score rebuilt by make_score.py at origin/main {c.o.head()[:12]}, engine release {CUR}" in msg, msg
        assert "score built from this run: yes" in msg and "- check_quotes.py: pass" in msg, msg
        lk = c.lock()
        assert lk["pr_number"] == 101 and lk["pr_url"] == "https://github.com/o/r/pull/101", lk
        r = c.pw("open", T, "--holder", "agent-1", "--body-file", c.body())
        assert r.returncode == 1 and "already open" in r.stderr, r.stderr
    finally:
        c.close()


def test_title_from_score():
    import pr_worktree as P
    s = {"name": "Acme", "tier_final": "B", "tier_by_numbers": "B", "implied_irr": 0.1734}
    assert P.title_for("pass1", "ACME", s) == "DCF pass 1: ACME — Acme — Tier B, weighted IRR 17.34%"
    s = {"name": "Acme", "tier_final": "D", "tier_by_numbers": "C", "implied_irr": 0.10206}
    assert P.title_for("pass1", "ACME", s) == "DCF pass 1: ACME — Acme — Tier D (C by numbers, 10.21%), weighted IRR 10.21%"
    s = {"name": "Acme", "tier_final": "F", "tier_by_numbers": "F", "implied_irr": None}
    assert P.title_for("rescore", "ACME", s) == "Re-score: ACME — Acme — Tier F (no cash generation)"
    assert P.title_for("pass2", "ACME", {"tier_final": "C", "tier_by_numbers": "C", "implied_irr": 0.12}, {"name": "J"}) \
        == "Second pass: ACME — J — Tier C, weighted IRR 12.00%"


def test_restack_rederives_registry_and_renumbers_backlog():
    c = Case()
    try:
        c.acquire()
        _append(c.wt, ENTRY_NEW)
        c.ok("prepare", T, "--holder", "agent-1")
        c.ok("open", T, "--holder", "agent-1", "--body-file", c.body())
        main_bl = BACKLOG + ENTRY_NEW.replace("a test defect found in review", "main's own entry")
        H.commit_on_origin(c.o, "_system/ENGINE_BACKLOG.md", main_bl, f"main appends {NEW_EB}")
        new_oth = dict(OTH_ENTRY, reason="test: re-scored on main (NI_OCF gap 51%)")
        H.commit_on_origin(c.o, "_system/overrides_registry.json", {"entries": [ZZZ_ENTRY, new_oth]}, "OTH re-scored")
        r = c.ok("restack", T, "--holder", "agent-1")
        assert f"backlog ids renumbered {NEW_EB} → {AFTER_EB}" in r.stdout, r.stdout
        bl = H.git(c.o.bare, "show", f"dcf/{T}:_system/ENGINE_BACKLOG.md").replace("\r\n", "\n")
        assert bl.startswith(main_bl) and f"### {AFTER_EB} — dcf_engine.py:test — a test defect found in review" in bl, \
            bl[-600:]
        reg = json.loads(H.git(c.o.bare, "show", f"dcf/{T}:_system/overrides_registry.json"))
        assert [e for e in reg["entries"] if e["ticker"] != T] == [ZZZ_ENTRY, new_oth], reg["entries"]
        base = H.git(c.o.bare, "merge-base", "main", f"dcf/{T}").strip()
        assert base == c.o.head(), "the branch sits on the new main"
        assert "Restacked onto origin/main" in H.git(c.o.bare, "log", "-1", "--format=%B", f"dcf/{T}")
    finally:
        c.close()


def test_restack_after_a_review_fix_acquire_keeps_the_backlog_entry():
    """[whole-PR review fix, 2026-10-21; fails on 6dd4a4a] PR_PROTOCOL 4 then 5: agent-1 cuts the PR with a didnt-fix
    backlog entry and releases; main merges its own entry under the same id; agent-2 acquires --kind review-fix (its
    lock's base_sha is the NEW origin/main) and restacks. The block was measured from that base_sha, came back empty,
    and the force-push dropped the PR's entry with a success line. It is measured from the branch's own merge-base
    now: the entry is kept and renumbered. A worktree backlog that does not start with that base's text is refused,
    never read as "nothing appended"."""
    c = Case()
    try:
        c.acquire("agent-1")
        _append(c.wt, ENTRY_NEW)
        c.ok("prepare", T, "--holder", "agent-1")
        c.ok("open", T, "--holder", "agent-1", "--body-file", c.body())
        c.ok("release", T, "--holder", "agent-1")
        main_bl = BACKLOG + ENTRY_NEW.replace("a test defect found in review", "main's own entry")
        H.commit_on_origin(c.o, "_system/ENGINE_BACKLOG.md", main_bl, f"main appends {NEW_EB}")
        c.gh_responses({"pr list": [{"number": 101, "headRefName": f"dcf/{T}", "state": "OPEN", "url": "u",
                                     "title": f"DCF pass 1: {T} — Test Co — Tier B", "createdAt": "2026-10-21T14:00:00Z"}]})
        c.ok("acquire", T, "--holder", "agent-2", "--kind", "review-fix")
        assert c.lock()["base_sha"] == c.o.head()
        r = c.ok("restack", T, "--holder", "agent-2")
        assert f"backlog ids renumbered {NEW_EB} → {AFTER_EB}" in r.stdout, r.stdout
        bl = H.git(c.o.bare, "show", f"dcf/{T}:_system/ENGINE_BACKLOG.md").replace("\r\n", "\n")
        assert bl.startswith(main_bl) and f"### {AFTER_EB} — dcf_engine.py:test — a test defect found in review" in bl, \
            bl[-600:]
        # the worktree file edited above its base: refused, nothing pushed
        p = os.path.join(c.wt, "_system", "ENGINE_BACKLOG.md")
        with open(p, encoding="utf-8") as f:
            text = f.read()
        with open(p, "w", encoding="utf-8", newline="\n") as f:
            f.write(text.replace("# ", "#  ", 1))
        before = H.git(c.o.bare, "rev-parse", f"dcf/{T}").strip()
        r = c.pw("restack", T, "--holder", "agent-2")
        assert r.returncode == 1 and "does not start with its base's text" in (r.stdout + r.stderr), (r.stdout, r.stderr)
        assert H.git(c.o.bare, "rev-parse", f"dcf/{T}").strip() == before
    finally:
        c.close()


def test_reap_removes_clean_worktree_of_a_merged_pr():
    c = Case(tickers=(T, "TS2"))
    try:
        c.acquire()
        c.ok("prepare", T, "--holder", "agent-1")
        c.ok("open", T, "--holder", "agent-1", "--body-file", c.body())
        c.ok("release", T, "--holder", "agent-1")
        c.ok("acquire", "TS2", "--holder", "agent-1", "--kind", "pass1")
        c.ok("release", "TS2", "--holder", "agent-1")
        os.makedirs(os.path.join(c.root, "TS2", "TS2"), exist_ok=True)
        with open(os.path.join(c.root, "TS2", "TS2", "junk.txt"), "w", encoding="utf-8") as f:
            f.write("dirty\n")
        c.gh_responses({"pr list": [{"number": 101, "headRefName": f"dcf/{T}", "state": "MERGED", "url": "u1"},
                                    {"number": 102, "headRefName": "dcf/TS2", "state": "CLOSED", "url": "u2"}]})
        r = c.ok("reap", "--json")
        res = json.loads(r.stdout)
        assert [x["branch"] for x in res["removed_worktrees"]] == [f"dcf/{T}"], res
        assert [x["branch"] for x in res["kept_worktrees"]] == ["dcf/TS2"], res
        assert not os.path.exists(c.wt) and os.path.exists(os.path.join(c.root, "TS2"))
    finally:
        c.close()


def test_review_round_reuses_the_branch_and_pushes():
    c = Case()
    try:
        c.acquire()
        c.ok("prepare", T, "--holder", "agent-1")
        c.ok("open", T, "--holder", "agent-1", "--body-file", c.body())
        c.ok("release", T, "--holder", "agent-1")
        c.gh_responses({"pr list": [{"number": 101, "headRefName": f"dcf/{T}", "state": "OPEN", "url": "u",
                                     "title": f"DCF pass 1: {T} — Test Co — Tier B", "createdAt": "2026-10-21T14:00:00Z"}]})
        r = c.ok("acquire", T, "--holder", "agent-2", "--kind", "review-fix")
        assert f"branch dcf/{T}" in r.stdout and c.lock()["pr_number"] == 101, r.stdout
        with open(os.path.join(c.c, T, "analysis.md"), "a", encoding="utf-8") as f:
            f.write("Review round 1: wording fixed in the sweep tree.\n")
        r = c.pw("prepare", T, "--holder", "agent-1")
        assert r.returncode == 4 and f"{T} is held by agent-2" in r.stderr, "the earlier holder is refused: " + r.stderr
        c.ok("prepare", T, "--holder", "agent-2")
        c.ok("push", T, "--holder", "agent-2", "-m", "Review round 1: analysis wording")
        log = H.git(c.o.bare, "log", "--format=%s", f"dcf/{T}", "-2").splitlines()
        assert log[0] == "Review round 1: analysis wording" and log[1].startswith("DCF pass 1:"), log
        r = c.pw("push", T, "--holder", "agent-2", "-m", "again")
        assert r.returncode == 1 and "nothing to push" in r.stderr, r.stderr
    finally:
        c.close()


def test_bulk_set_is_all_or_nothing_and_opens_one_rebuild_pr():
    c = Case(tickers=(T, "TS2"))
    try:
        rep = os.path.join(c.o.root, "rebuild.json.applied.json")
        json.dump({"tool": "rebuild_scores", "mode": "apply", "engine_release": CUR, "drift_allowed": False,
                   "folders": [{"ticker": T, "state": "rebuilt", "main_sync": "in_sync"},
                               {"ticker": "TS2", "state": "rebuilt", "main_sync": "in_sync"},
                               {"ticker": "OTH", "state": "rebuilt", "main_sync": "differs"}]}, open(rep, "w"))
        c.ok("acquire", "TS2", "--holder", "agent-9", "--kind", "pass1")
        r = c.pw("acquire", "--bulk", rep, "--holder", "muse-main")
        assert r.returncode == 4 and "TS2 is held by agent-9" in r.stderr, r.stderr
        assert not os.path.exists(os.path.join(c.root, ".locks", f"{T}.lock.json")), "all-or-nothing"
        c.ok("release", "TS2", "--holder", "agent-9", "--remove-worktree")
        r = c.ok("acquire", "--bulk", rep, "--holder", "muse-main")
        branch = f"rebuild/{CUR}-20261021"
        assert f"bulk {branch} acquired" in r.stdout and "2 tickers" in r.stdout, r.stdout
        c.ok("prepare", "--bulk", branch, "--holder", "muse-main")
        c.ok("open", "--bulk", branch, "--body-file", c.body(), "--holder", "muse-main")
        call = H.gh_calls(c.gh_dir)[-1]
        assert call[call.index("--title") + 1] == f"Rebuild: make_score at release {CUR} over 2 folders", call
        names = H.git(c.o.bare, "diff", "--name-only", "main", branch).split()
        assert {n.split("/")[0] for n in names} == {T, "TS2", "_system"}, names
    finally:
        c.close()


def test_bulk_refusal_names_the_folder_and_the_set_can_drop_it():
    """[whole-PR review fix, 2026-10-21; fails on 6dd4a4a] One folder refused in prepare --bulk (its sweep score no
    longer its rebuild) blocked the whole set: the refusal did not name it (with ~488 folders the main agent cannot
    tell which), and nothing could drop it (acquire / prepare --bulk had no ticker filter). The refusal now starts with
    the ticker and names `prepare --bulk <branch> --exclude <T>`, which drops it (lock released, worktree reset) so the
    rest is prepared and opened; --exclude is refused for a ticker outside the set and once nothing would be left."""
    c = Case(tickers=(T, "TS2"))
    try:
        rep = os.path.join(c.o.root, "rebuild.json.applied.json")
        json.dump({"tool": "rebuild_scores", "mode": "apply", "engine_release": CUR, "drift_allowed": False,
                   "folders": [{"ticker": T, "state": "rebuilt", "main_sync": "in_sync"},
                               {"ticker": "TS2", "state": "rebuilt", "main_sync": "in_sync"}]}, open(rep, "w"))
        c.ok("acquire", "--bulk", rep, "--holder", "muse-main")
        branch = f"rebuild/{CUR}-20261021"
        p = os.path.join(c.c, "TS2", "score.json")
        s = json.load(open(p, encoding="utf-8"))
        s["tier_final"] = "D" if s.get("tier_final") != "D" else "C"
        json.dump(s, open(p, "w", encoding="utf-8"), indent=1)
        r = c.pw("prepare", "--bulk", branch, "--holder", "muse-main")
        assert r.returncode == 1 and "pr_worktree: TS2: the score rebuilt at origin/main" in r.stderr, r.stderr
        assert f"prepare --bulk {branch} --exclude TS2" in r.stderr, r.stderr
        r = c.pw("prepare", "--bulk", branch, "--holder", "muse-main", "--exclude", "OTH")
        assert r.returncode == 1 and "not in bulk set" in r.stderr, r.stderr
        r = c.pw("prepare", "--bulk", branch, "--holder", "muse-main", "--exclude", f"{T},TS2")
        assert r.returncode == 1 and "would leave bulk set" in r.stderr, r.stderr
        r = c.ok("prepare", "--bulk", branch, "--holder", "muse-main", "--exclude", "TS2")
        assert "excluded TS2 (locks released); 1 tickers left" in r.stdout, r.stdout
        assert not os.path.exists(os.path.join(c.root, ".locks", "TS2.lock.json")), "TS2's lock is released"
        c.ok("open", "--bulk", branch, "--body-file", c.body(), "--holder", "muse-main")
        names = H.git(c.o.bare, "diff", "--name-only", "main", branch).split()
        assert {n.split("/")[0] for n in names} == {T, "_system"}, names
    finally:
        c.close()


def test_bulk_mechanics_names_each_stale_folder_and_its_hash():
    """[whole-PR review fix, 2026-10-21; fails on 6dd4a4a] AGENTS.md check 6: a stale-release score presented as current
    (no "the engine output predates release <rel>" line) is P1, and a rebuild/* PR is the same case for many folders;
    the Mechanics block names score.dcf_content_hash and "score built from this run". The bulk block printed only the
    set of releases: every rebuild PR drew the P1. It now carries, per folder, the hash, the from-run answer and — for
    a folder whose run predates main's release — the exact line."""
    import pr_worktree as P

    def row(t, h, stale=True):
        return {"ticker": t, "engine_release_run": "5.4.0" if stale else CUR, "dcf_content_hash": h,
                "stale_release": {"run": "5.4.0", "main": CUR} if stale else None, "check_quotes": "pass",
                "other_changed_fields": [], "score_from_run": True, "score_mismatch": None}
    prep = {"origin_sha": "a" * 40, "engine_release": CUR, "files": ["CNA/score.json", "GLPI/score.json"],
            "tickers": [row("GLPI", "1234567890abcdef"), row("CNA", "fedcba0987654321", stale=False)],
            "registry_entries": {}}
    text = P.mechanics(prep, ["GLPI", "CNA"], None)
    assert (f"- GLPI: score.dcf_content_hash 1234567890ab · score built from this run: yes · the engine output "
            f"predates release {CUR} (run 5.4.0)") in text, text
    assert "- CNA: score.dcf_content_hash fedcba098765 · score built from this run: yes\n" in text, text


def test_backlog_next():
    c = Case()
    try:
        assert NEXT_ID > 40, NEXT_ID   # 39 seeded entries + R7's follow-up EB-040 (Integrate L5)
        assert c.ok("backlog-next").stdout.strip() == NEW_EB
        H.commit_on_origin(c.o, "_system/ENGINE_BACKLOG.md", BACKLOG + ENTRY_NEW, "append")
        assert c.ok("backlog-next").stdout.strip() == AFTER_EB, "read from origin/main after a fetch"
    finally:
        c.close()


def test_pr_protocol_names_every_pr_worktree_command():
    import pr_worktree as P
    ap = P.build_parser()
    sub = next(a for a in ap._actions if a.__class__.__name__ == "_SubParsersAction")
    names = sorted(sub.choices)
    assert names == sorted(P.SUBCOMMANDS), names
    proto = open(os.path.join(H.SYS, "PR_PROTOCOL.md"), encoding="utf-8").read()
    for n in names:
        assert f"pr_worktree.py {n}" in proto or f"`{n} " in proto or f"`{n}`" in proto, n


# ------------------------------------------------------------------ review fixes (2026-10-21)
INDUSTRY = "_system/industry_returns.json"


def _industry_src():
    with open(os.path.join(H.SYS, "industry_returns.json"), encoding="utf-8") as f:
        return f.read()


def _rewrite_industry(sweep, built):
    """What the daily cron's industry_returns.py --write leaves when a member changed: a new build."""
    p = os.path.join(sweep, *INDUSTRY.split("/"))
    doc = json.load(open(p, encoding="utf-8"))
    doc["built"] = built
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, indent=1)


def _industry_on_main(c):
    H.commit_on_origin(c.o, INDUSTRY, _industry_src(), "industry_returns.json initial build")
    H.git(c.c, "pull", "-q", "--ff-only", "origin", "main")


def test_prepare_scores_against_the_sweep_trees_industry_file():
    """P1: _system/industry_returns.json feeds moat_evidence (a decision field). Before the fix prepare scored
    against main's copy and refused every folder whose sweep tree held another build — the daily cron's rewrite, or
    the first 5.7 deploy — with advice that could not clear it. Now: the refusal names moat_evidence.industry_file
    when the sweep score is older than the sweep's file, re-running make_score clears it, prepare scores against the
    sweep tree's build, and the company PR never carries the file."""
    c = Case()
    try:
        _industry_on_main(c)   # TST was scored before the file existed: its moat_evidence has no industry file
        c.acquire()
        r = c.pw("prepare", T, "--holder", "agent-1")
        assert r.returncode == 1, r.stdout
        assert "differs from the sweep tree's (moat_evidence.industry_file null → {" in r.stderr, r.stderr
        assert "another build of _system/industry_returns.json" in r.stderr, r.stderr
        assert H.git(c.wt, "status", "--porcelain", "--", INDUSTRY).strip() == "", "a refused prepare restores main's"
        _rewrite_industry(c.c, "2026-10-22")   # the daily cron rewrites the sweep tree's build
        c.score()                              # the worker re-runs make_score on the sweep tree (the advice)
        s = json.load(open(os.path.join(c.c, T, "score.json"), encoding="utf-8"))
        assert s["moat_evidence"]["industry_file"]["built"] == "2026-10-22", s["moat_evidence"]["industry_file"]
        r = c.ok("prepare", T, "--holder", "agent-1")
        assert "industry_returns.json: scored against the sweep tree's built 2026-10-22" in r.stdout, r.stdout
        main_built = json.loads(_industry_src())["built"]
        assert f"main's is built {main_built}" in r.stdout, r.stdout
        assert H.git(c.wt, "status", "--porcelain", "--", INDUSTRY).strip() == "", "main's copy is back"
        prep = c.lock()["prepared"]
        assert prep["industry_file"]["sweep"]["built"] == "2026-10-22" and prep["industry_file"]["carried"] is False
        assert INDUSTRY not in prep["files"], prep["files"]
        c.ok("open", T, "--holder", "agent-1", "--body-file", c.body())
        names = H.git(c.o.bare, "diff", "--name-only", "main", f"dcf/{T}").split()
        assert INDUSTRY not in names and f"{T}/score.json" in names, names
        msg = H.git(c.o.bare, "log", "-1", "--format=%B", f"dcf/{T}")
        assert "- industry_returns.json: scored against the sweep tree's built 2026-10-22" in msg, msg
    finally:
        c.close()


def test_bulk_pr_carries_the_sweep_trees_industry_file():
    """03b §3.3.3: a rebuild data PR scores against a current build and carries it."""
    c = Case(tickers=(T, "TS2"))
    try:
        _industry_on_main(c)
        _rewrite_industry(c.c, "2026-10-22")
        for t in (T, "TS2"):
            c.score(t)
        rep = os.path.join(c.o.root, "rebuild.json.applied.json")
        json.dump({"tool": "rebuild_scores", "mode": "apply", "engine_release": CUR, "drift_allowed": False,
                   "folders": [{"ticker": t, "state": "rebuilt", "main_sync": "in_sync"} for t in (T, "TS2")]},
                  open(rep, "w"))
        c.ok("acquire", "--bulk", rep, "--holder", "muse-main")
        branch = f"rebuild/{CUR}-20261021"
        r = c.ok("prepare", "--bulk", branch)   # the bulk forms default to the bulk set's holder
        assert "industry_returns.json: the sweep tree's built 2026-10-22" in r.stdout and "carried" in r.stdout, r.stdout
        c.ok("open", "--bulk", branch, "--body-file", c.body())
        names = H.git(c.o.bare, "diff", "--name-only", "main", branch).split()
        assert INDUSTRY in names and f"{T}/score.json" in names, names
        assert json.loads(H.git(c.o.bare, "show", f"{branch}:{INDUSTRY}"))["built"] == "2026-10-22"
    finally:
        c.close()


def test_an_expired_holder_is_refused_after_a_takeover():
    """P2: agent-1's lease expired, agent-2 acquired TST; agent-1's next step as PR_PROTOCOL wrote it (no --holder)
    used to prepare and open a PR in agent-2's worktree."""
    c = Case()
    try:
        c.acquire()                                         # agent-1, 10:00, a 3-hour lease
        c.acquire("agent-2", kind="rescore", now=LATER)     # 14:30: reaped and taken over
        body = c.body()
        for args in (("prepare", T), ("open", T, "--body-file", body), ("push", T, "-m", "x"), ("restack", T)):
            r = c.pw(*args, now=LATER)
            assert r.returncode == 2, f"{args} without --holder: {r.returncode} {r.stdout} {r.stderr}"
            r = c.pw(*args, "--holder", "agent-1", now=LATER)
            assert r.returncode == 4 and f"{T} is held by agent-2" in r.stderr, f"{args}: {r.returncode} {r.stderr}"
        lk = c.lock()
        assert lk["holder"] == "agent-2" and lk["pr_url"] is None and lk["prepared"] is None, lk
        assert H.gh_calls(c.gh_dir) == [], "nothing reached gh"
    finally:
        c.close()


def test_a_takeover_during_prepare_never_overwrites_the_new_lease():
    """The lock update at the end of a long prepare checks the lease is still the caller's (exit 4 otherwise):
    before, write_lock put the old holder's record over the new holder's lock."""
    import pr_worktree as P
    c = Case()
    try:
        c.acquire()
        real = P.do_prepare

        def slow_prepare(tickers, kind, wt, no_fetch=False, bulk=False):
            # the make_score run outlives the lease and agent-2 takes TST meanwhile (its worktree is clean)
            later = dict(os.environ, STOCKS_NOW=LATER)
            r = subprocess.run([sys.executable, os.path.join(H.SYS, "pr_worktree.py"), "acquire", T, "--holder",
                                "agent-2", "--kind", "rescore"], capture_output=True, text=True, encoding="utf-8",
                               env=later, timeout=600)
            assert r.returncode == 0, r.stderr
            return {"origin_sha": "x", "tickers": [{}], "files": []}
        P.do_prepare = slow_prepare
        try:
            rc, out, err = _inproc(c, ["prepare", T, "--holder", "agent-1"])
        finally:
            P.do_prepare = real
        assert rc == 4 and f"{T} is held by agent-2" in err, (rc, out, err)
        lk = c.lock()
        assert lk["holder"] == "agent-2" and lk["prepared"] is None, lk
    finally:
        c.close()


def test_reaping_is_serialized_by_the_lease_guard():
    """P2: B read the expired lock, A reaped it and created its own, then B's rename took A's live lock away and both
    acquires succeeded. Replayed in-process: A's whole _take is injected right after B's read. With the guard A
    waits for B and is refused (exit 4); exactly one reap is logged."""
    import _ops
    import pr_worktree as P
    root = tempfile.mkdtemp(prefix="prw_race_")
    old = {k: os.environ.get(k) for k in ("STOCKS_PR_ROOT", "STOCKS_NOW")}
    os.environ.update(STOCKS_PR_ROOT=root, STOCKS_NOW=LATER)
    real_read = P.read_lock
    try:
        now = _ops.now_et()
        assert P.create_lock(T, P._new_lock(T, "agent-1", "pass1", 3.0, now - datetime.timedelta(hours=5)))
        res, threads, calls = {}, [], {"n": 0}

        def take(h):
            try:
                P._take(T, h, "rescore", 3.0, now)
                res[h] = 0
            except P.Stop as e:
                res[h] = e.code

        def read_then_let_a_run(t):
            cur = real_read(t)
            if calls["n"] == 0:   # B's read of the expired lock: A runs its whole acquire now
                calls["n"] += 1
                th = threading.Thread(target=take, args=("racer-a",))
                th.start()
                th.join(timeout=2.0)   # without the guard A finishes here; with it, A waits for B
                threads.append(th)
            return cur
        P.read_lock = read_then_let_a_run
        take("racer-b")
        P.read_lock = real_read
        for th in threads:
            th.join(timeout=60)
        assert sorted(res.values()) == [0, 4], res
        winner = next(h for h, rc in res.items() if rc == 0)
        assert real_read(T)["holder"] == winner, real_read(T)
        log = open(os.path.join(root, ".locks", "reaped.log"), encoding="utf-8").read()
        assert log.count(f"reaped {T} lock held by agent-1") == 1, log
    finally:
        P.read_lock = real_read
        for k, v in old.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        shutil.rmtree(root, ignore_errors=True)


def test_reap_keeps_an_open_pr_on_a_reused_branch_and_unpushed_commits():
    """P3: dcf/<T> is handed out again once an earlier PR's branch was deleted after its merge; reap read the OLDEST
    PR of that head name and removed the worktree (and the local branch) of an OPEN PR."""
    c = Case()
    try:
        c.acquire()
        c.ok("prepare", T, "--holder", "agent-1")
        c.ok("open", T, "--holder", "agent-1", "--body-file", c.body())
        c.ok("release", T, "--holder", "agent-1")
        head = H.git(c.wt, "rev-parse", "HEAD").strip()
        c.gh_responses({"pr list": [
            {"number": 101, "headRefName": f"dcf/{T}", "state": "OPEN", "createdAt": "2026-10-21T14:00:00Z",
             "headRefOid": head, "url": "u101"},
            {"number": 5, "headRefName": f"dcf/{T}", "state": "MERGED", "createdAt": "2026-10-19T22:00:00Z",
             "headRefOid": "0" * 40, "url": "u5"}]})
        res = json.loads(c.ok("reap", "--json").stdout)
        assert res["removed_worktrees"] == [], res
        assert os.path.isdir(c.wt) and H.git(c.c, "branch", "--list", f"dcf/{T}").strip(), "the open PR's worktree stays"
        # #101 merged (the newest decides), then a local commit nobody pushed: kept
        with open(os.path.join(c.wt, T, "analysis.md"), "a", encoding="utf-8") as f:
            f.write("A local commit.\n")
        H.git(c.wt, "commit", "-q", "-am", "local only")
        c.gh_responses({"pr list": [
            {"number": 101, "headRefName": f"dcf/{T}", "state": "MERGED", "createdAt": "2026-10-21T14:00:00Z",
             "headRefOid": head, "url": "u101"},
            {"number": 5, "headRefName": f"dcf/{T}", "state": "MERGED", "createdAt": "2026-10-19T22:00:00Z",
             "url": "u5"}]})
        res = json.loads(c.ok("reap", "--json").stdout)
        assert res["removed_worktrees"] == [] and [k["pr"] for k in res["kept_worktrees"]] == [101], res
        assert "neither PR #101's head nor pushed" in res["kept_worktrees"][0]["why"], res
        H.git(c.wt, "reset", "-q", "--hard", head)   # back to the merged PR's head: removed
        res = json.loads(c.ok("reap", "--json").stdout)
        assert [x["pr"] for x in res["removed_worktrees"]] == [101], res
        assert not os.path.exists(c.wt)
    finally:
        c.close()


def test_engine_backlog_parses():
    import _ops
    entries, problems = _ops.parse_backlog(BACKLOG)
    assert problems == [], problems
    ids = [e["id"] for e in entries if not e["seen_again"]]
    assert ids == list(range(1, len(ids) + 1)) and len(ids) >= 28, ids
    assert all("- Threads: " in e["fields"]["Threads"] for e in entries)
    status = {e["id"]: e["fields"]["Status"] for e in entries}
    assert status[5] == "- Status: fixed in PR #53 (2026-10-20)" and status[28].startswith("- Status: fixed in PR #")
    assert status[10].startswith("- Status: fixed in PR #") and status[24] == "- Status: needs-decision (Andrew)"


if __name__ == "__main__":
    sys.exit(H.run_tests(globals()))
