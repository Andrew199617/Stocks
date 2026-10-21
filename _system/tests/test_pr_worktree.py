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
"""
import contextlib
import io
import json
import os
import subprocess
import sys
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
        rc, out, err = _inproc(c, ["prepare", T], policy="refuse")
        assert rc == 1, out + err
        assert (f"{T}/dcf_numbers.json is engine release 5.5.0; origin/main is {CUR} — re-run the engine") in err, err
        assert "(MOH #37, ESTC #35)" in err, err
        r = c.ok("prepare", T)   # default STALE_RELEASE_POLICY: lane default Q12 (b)
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
        rc, out, err = _inproc(c, ["prepare", T], policy="refuse")
        assert rc == 0, "kind rebuild prepares a stale-release folder under either policy: " + err
        c.ok("open", T, "--body-file", c.body())
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
        c.ok("prepare", T)
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
        r = c.pw("prepare", T)
        assert r.returncode == 1, r.stdout
        assert "differs from the sweep tree's (tier_final D → B" in r.stderr and "scored on other code" in r.stderr, r.stderr
        assert not c.lock()["prepared"]
    finally:
        c.close()


def test_prepare_runs_check_quotes_on_57_runs():
    c = Case(analysis="# TST\nRevenue grew 37.25% last year.\n")
    try:
        c.acquire()
        r = c.pw("prepare", T)
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
        r = c.pw("prepare", T)
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
        r = c.pw("prepare", T)
        assert r.returncode == 1, r.stdout
        assert f"{T}/second_pass.md is on main but not in the sweep folder" in r.stderr, r.stderr
    finally:
        c.close()


def test_open_refuses_paths_outside_the_company_scope():
    c = Case()
    try:
        c.acquire()
        c.ok("prepare", T)
        with open(os.path.join(c.wt, "_system", "make_score.py"), "a", encoding="utf-8") as f:
            f.write("# edited in the worktree\n")
        r = c.pw("open", T, "--body-file", c.body())
        assert r.returncode == 1, r.stdout
        assert ("refusing to commit — the worktree changes paths a company PR may not carry: _system/make_score.py"
                in r.stderr), r.stderr
        H.git(c.wt, "checkout", "--", "_system/make_score.py")
        with open(os.path.join(c.wt, T, "analysis.md"), "a", encoding="utf-8") as f:
            f.write("A fix made only in the worktree.\n")
        r = c.pw("open", T, "--body-file", c.body())
        assert r.returncode == 1 and "changed since prepare" in r.stderr and "never the worktree" in r.stderr, r.stderr
        assert H.gh_calls(c.gh_dir) == [], "nothing reached gh"
    finally:
        c.close()


def _append(wt, text):
    with open(os.path.join(wt, "_system", "ENGINE_BACKLOG.md"), "a", encoding="utf-8", newline="\n") as f:
        f.write(text)


ENTRY_40 = ("\n### EB-040 — dcf_engine.py:test — a test defect found in review\n- Opened: 2026-10-21, TST PR #101\n"
            "- Status: open\n- Threads: https://github.com/Andrew199617/Stocks/pull/101#discussion_r1 (TST, P3)\n"
            "- Effect: test effect $1.00\n- Fix sketch: test fix\n")


def test_open_backlog_is_append_only():
    c = Case()
    try:
        c.acquire()
        c.ok("prepare", T)
        p = os.path.join(c.wt, "_system", "ENGINE_BACKLOG.md")
        text = open(p, encoding="utf-8").read()
        with open(p, "w", encoding="utf-8", newline="\n") as f:
            f.write(text.replace("- Status: open", "- Status: fixed in PR #101 (2026-10-21)", 1) + ENTRY_40)
        r = c.pw("open", T, "--body-file", c.body())
        assert r.returncode == 1 and "append-only in a data PR: the diff edits or removes 1 existing line" in r.stderr, r.stderr
        with open(p, "w", encoding="utf-8", newline="\n") as f:
            f.write(text + ENTRY_40.replace("EB-040", "EB-039"))
        r = c.pw("open", T, "--body-file", c.body())
        assert r.returncode == 1 and "EB-039 is already used on main" in r.stderr, r.stderr
        with open(p, "w", encoding="utf-8", newline="\n") as f:
            f.write(text + ENTRY_40.replace("- Threads: https://github.com/Andrew199617/Stocks/pull/101#discussion_r1",
                                            "- Threads: none"))
        r = c.pw("open", T, "--body-file", c.body())
        assert r.returncode == 1 and "Threads line holds no PR thread URL" in r.stderr, r.stderr
        with open(p, "w", encoding="utf-8", newline="\n") as f:
            f.write(text + ENTRY_40)
        c.ok("open", T, "--body-file", c.body())
        names = H.git(c.o.bare, "diff", "--name-only", "main", f"dcf/{T}").split()
        assert "_system/ENGINE_BACKLOG.md" in names, names
    finally:
        c.close()


def test_open_stages_only_allowed_paths_and_calls_gh():
    c = Case()
    try:
        c.acquire()
        c.ok("prepare", T)
        r = c.ok("open", T, "--body-file", c.body(), "--trailer", "Co-Authored-By: Test Agent <t@test.invalid>")
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
        r = c.pw("open", T, "--body-file", c.body())
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
        _append(c.wt, ENTRY_40)
        c.ok("prepare", T)
        c.ok("open", T, "--body-file", c.body())
        main_bl = BACKLOG + ENTRY_40.replace("a test defect found in review", "main's own entry")
        H.commit_on_origin(c.o, "_system/ENGINE_BACKLOG.md", main_bl, "main appends EB-040")
        new_oth = dict(OTH_ENTRY, reason="test: re-scored on main (NI_OCF gap 51%)")
        H.commit_on_origin(c.o, "_system/overrides_registry.json", {"entries": [ZZZ_ENTRY, new_oth]}, "OTH re-scored")
        r = c.ok("restack", T)
        assert "backlog ids renumbered EB-040 → EB-041" in r.stdout, r.stdout
        bl = H.git(c.o.bare, "show", f"dcf/{T}:_system/ENGINE_BACKLOG.md").replace("\r\n", "\n")
        assert bl.startswith(main_bl) and "### EB-041 — dcf_engine.py:test — a test defect found in review" in bl, bl[-600:]
        reg = json.loads(H.git(c.o.bare, "show", f"dcf/{T}:_system/overrides_registry.json"))
        assert [e for e in reg["entries"] if e["ticker"] != T] == [ZZZ_ENTRY, new_oth], reg["entries"]
        base = H.git(c.o.bare, "merge-base", "main", f"dcf/{T}").strip()
        assert base == c.o.head(), "the branch sits on the new main"
        assert "Restacked onto origin/main" in H.git(c.o.bare, "log", "-1", "--format=%B", f"dcf/{T}")
    finally:
        c.close()


def test_reap_removes_clean_worktree_of_a_merged_pr():
    c = Case(tickers=(T, "TS2"))
    try:
        c.acquire()
        c.ok("prepare", T)
        c.ok("open", T, "--body-file", c.body())
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
        c.ok("prepare", T)
        c.ok("open", T, "--body-file", c.body())
        c.ok("release", T, "--holder", "agent-1")
        c.gh_responses({"pr list": [{"number": 101, "headRefName": f"dcf/{T}", "state": "OPEN", "url": "u",
                                     "title": f"DCF pass 1: {T} — Test Co — Tier B", "createdAt": "2026-10-21T14:00:00Z"}]})
        r = c.ok("acquire", T, "--holder", "agent-2", "--kind", "review-fix")
        assert f"branch dcf/{T}" in r.stdout and c.lock()["pr_number"] == 101, r.stdout
        with open(os.path.join(c.c, T, "analysis.md"), "a", encoding="utf-8") as f:
            f.write("Review round 1: wording fixed in the sweep tree.\n")
        c.ok("prepare", T)
        c.ok("push", T, "-m", "Review round 1: analysis wording")
        log = H.git(c.o.bare, "log", "--format=%s", f"dcf/{T}", "-2").splitlines()
        assert log[0] == "Review round 1: analysis wording" and log[1].startswith("DCF pass 1:"), log
        r = c.pw("push", T, "-m", "again")
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


def test_backlog_next():
    c = Case()
    try:
        assert c.ok("backlog-next").stdout.strip() == "EB-040"
        H.commit_on_origin(c.o, "_system/ENGINE_BACKLOG.md", BACKLOG + ENTRY_40, "append")
        assert c.ok("backlog-next").stdout.strip() == "EB-041", "read from origin/main after a fetch"
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
