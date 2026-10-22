#!/usr/bin/env python3
"""pr_audit.py — the done-without-PR audit (engine 5.7, Andrew's ruling R5 of 2026-10-19; design 05 §4, §9 and the
L5 rebase amendment A7). Run: python _system/tests/test_pr_audit.py. Offline: a temp sweep clone of a local bare
origin; gh output from --gh-json / --gh-files-json files or the $STOCKS_GH stub.

The miss it stops: BMRN was done and scored on the sweep tree, differed from main, and no PR carried it. Covered:
in sync is not a finding; done without a PR is missing_pr (exit 1, one MISSING_PR line); an open PR for this
generation is ok; a merged PR followed by a change is merged_then_changed; a PR from before the generation does not
count (missing_pr / stale_open_pr); the grace window; SEC enrichment and caches are ignored; date-suffix branches and
the title shapes (incl. "DCF pass 1 update", #68) match; a bulk rebuild PR covers the files it carries; a done name
with no folder; gh failing exits 3; a CRLF checkout compares by blob; a score that is not its run's
(score_not_from_run, checked first); facts.json and saved runs dcf_numbers_<label>.json are record files; APP outside
the queue is a candidate; --quiet prints one line, and nothing without findings; a finished second pass of the
current generation (done_changed / done_no_change) is a generation of its own — grace to the end of its day, then
missing_pr with the Second pass hint, its Second pass PR open / merged, never merged_then_changed through the pass-1
PR; an older generation's review and an in-progress one do not count; a malformed pass-2 queue exits 3 (review
2026-10-21).
"""
import datetime
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ops_harness as H  # noqa: E402

NOW = datetime.datetime(2026, 10, 21, 12, 0)
OLD_CLAIM = "2026-10-19T14:02:00-04:00"


def _pair(t, tier="B", irr=0.17):
    n = {"ticker": t, "engine_version": 5, "engine_release": "5.5.0", "as_of": "2026-10-18", "tier_by_numbers": tier,
         "implied_irr_weighted": irr, "price": 20.0, "base_oe_per_share": 3.0, "iv_at_15": 25.0}
    s = {"ticker": t, "name": f"{t} Inc", "engine_version": 5, "engine_release": "5.5.0", "analysis_date": "2026-10-18",
         "tier_by_numbers": tier, "tier_final": tier, "implied_irr": irr, "price": 20.0, "base_oe_per_share": 3.0,
         "iv_at_15": 25.0}
    return n, s


def _folder_files(t):
    n, s = _pair(t)
    return {f"{t}/dcf_numbers.json": n, f"{t}/score.json": s, f"{t}/analysis.md": f"# {t}\nAnalysis.\n",
            f"{t}/judgment.json": {"name": f"{t} Inc"}, f"{t}/key_numbers.md": "# key\n",
            f"{t}/statements.json": {"v": 1}}


class Sweep:
    def __init__(self, tickers=("AAA", "BBB"), queue=None, autocrlf=None, extra=None):
        files = {".gitignore": open(os.path.join(H.ROOT, ".gitignore"), encoding="utf-8").read()}
        for t in tickers:
            files.update(_folder_files(t))
        files.update(extra or {})
        self.o = H.make_origin(files)
        self.c = H.clone(self.o, autocrlf=autocrlf)
        self.queue(queue if queue is not None else [{"ticker": t, "status": "done", "completed": "2026-10-19",
                                                      "claimed_at": OLD_CLAIM} for t in tickers])
        self.gh = os.path.join(self.o.root, "gh.json")
        self.files = os.path.join(self.o.root, "gh_files.json")
        self.prs([])
        with open(self.files, "w", encoding="utf-8") as f:
            json.dump({}, f)

    def queue(self, entries):
        p = os.path.join(self.c, "_system", "queue.json")
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            json.dump({"queue": entries}, f)

    def prs(self, prs, files=None):
        with open(self.gh, "w", encoding="utf-8") as f:
            json.dump(prs, f)
        if files is not None:
            with open(self.files, "w", encoding="utf-8") as f:
                json.dump(files, f)

    def edit(self, rel, text="changed\n"):
        p = os.path.join(self.c, *rel.split("/"))
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            f.write(text if isinstance(text, str) else json.dumps(text))

    def audit(self, *args, env=None):
        e = {"STOCKS_NOW": NOW.isoformat()}
        e.update(env or {})
        out = os.path.join(self.o.root, "audit.json")
        r = H.run("pr_audit.py", "--no-fetch", "--gh-json", self.gh, "--gh-files-json", self.files, "--json", out,
                  *args, base=self.c, env=e)
        rep = json.load(open(out, encoding="utf-8")) if os.path.exists(out) and r.returncode in (0, 1) else None
        if os.path.exists(out):
            os.remove(out)
        return r, rep

    def close(self):
        self.o.close()


def _pr(n, head, state="OPEN", created="2026-10-20T10:00:00Z", merged=None, title=None):
    return {"number": n, "headRefName": head, "state": state, "createdAt": created, "mergedAt": merged,
            "title": title or f"DCF pass 1: {head.split('/')[-1]} — x — Tier B", "url": f"https://x/pull/{n}"}


def _state(rep, t):
    for f in rep["findings"]:
        if f["ticker"] == t:
            return f["state"]
    for k, v in rep["ok"].items():
        if t in v:
            return k
    return None


def test_in_sync_is_not_a_finding():
    s = Sweep()
    try:
        r, rep = s.audit()
        assert r.returncode == 0, r.stdout + r.stderr
        assert rep["counts"]["in_sync"] == 2 and rep["findings"] == [], rep
        assert r.stdout.startswith("pr_audit: 2 done names at origin/main ") and "2 in sync" in r.stdout, r.stdout
        q, _ = s.audit("--quiet")
        assert q.returncode == 0 and q.stdout == "", "--quiet prints nothing without findings"
    finally:
        s.close()


def test_done_without_pr_is_missing_pr_exit_1():
    s = Sweep()
    try:
        s.edit("AAA/analysis.md", "# AAA\nNew generation.\n")
        s.prs([_pr(42, "dcf/AAA", "MERGED", created="2026-10-18T10:00:00Z", merged="2026-10-18T12:00:00Z")])
        r, rep = s.audit()
        assert r.returncode == 1, r.stdout
        f = rep["findings"][0]
        assert f["ticker"] == "AAA" and f["state"] == "missing_pr" and f["differs"] == ["analysis.md"], f
        assert "MISSING_PR           AAA   claimed 2026-10-19 14:02 ET, done 2026-10-19  differs: analysis.md" in r.stdout
        assert 'What to do with each: _system/PR_PROTOCOL.md "pr_audit findings".' in r.stdout
        q, _ = s.audit("--quiet")
        assert q.returncode == 1 and len(q.stdout.strip().splitlines()) == 1 and "1 finding" in q.stdout, q.stdout
        assert q.stdout.strip().endswith("(AAA missing_pr)"), q.stdout
    finally:
        s.close()


def test_open_pr_for_this_generation_is_ok():
    s = Sweep()
    try:
        s.edit("AAA/score.json", json.dumps(dict(_pair("AAA")[1], name="AAA renamed")))
        s.prs([_pr(50, "dcf/AAA", "OPEN", created="2026-10-20T09:00:00Z")])
        r, rep = s.audit()
        assert r.returncode == 0, r.stdout
        assert _state(rep, "AAA") == "pr_open" and rep["counts"]["pr_open"] == 1
    finally:
        s.close()


def test_merged_then_changed_is_a_finding():
    s = Sweep()
    try:
        s.edit("AAA/judgment.json", {"name": "AAA Inc", "note": "edited after merge"})
        s.prs([_pr(43, "dcf/AAA", "MERGED", created="2026-10-20T09:00:00Z", merged="2026-10-21T00:20:00Z")])
        r, rep = s.audit()
        assert r.returncode == 1
        assert _state(rep, "AAA") == "merged_then_changed", rep
        assert "MERGED_THEN_CHANGED  AAA   PR #43 merged 2026-10-20 20:20 ET  differs since: judgment.json" in r.stdout, r.stdout
    finally:
        s.close()


def test_a_pr_before_the_generation_does_not_count():
    s = Sweep()
    try:
        s.edit("AAA/analysis.md", "# new\n")
        s.edit("BBB/analysis.md", "# new\n")
        s.prs([_pr(9, "dcf/AAA", "MERGED", created="2026-10-19T05:10:00Z", merged="2026-10-19T06:00:00Z"),
               _pr(10, "dcf/BBB", "OPEN", created="2026-10-19T05:10:00Z")])
        r, rep = s.audit()
        assert r.returncode == 1
        assert _state(rep, "AAA") == "missing_pr" and _state(rep, "BBB") == "stale_open_pr", rep
        assert "STALE_OPEN_PR        BBB   PR #10 opened 2026-10-19 01:10 ET predates the claim at 2026-10-19 14:02 ET" \
            in r.stdout, r.stdout
    finally:
        s.close()


def test_grace_window():
    s = Sweep(queue=[{"ticker": "AAA", "status": "done", "completed": "2026-10-21", "claimed_at": "2026-10-21T09:30:00-04:00"},
                     {"ticker": "BBB", "status": "done", "completed": "2026-10-19", "claimed_at": OLD_CLAIM}])
    try:
        s.edit("AAA/analysis.md", "# new\n")
        r, rep = s.audit()
        assert r.returncode == 0 and _state(rep, "AAA") == "grace", rep
        r, rep = s.audit("--grace-hours", "1")
        assert r.returncode == 1 and _state(rep, "AAA") == "missing_pr", rep
    finally:
        s.close()


def test_sec_enrichment_and_caches_are_ignored():
    s = Sweep()
    try:
        s.edit("AAA/statements.json", '{"v": 2}')
        s.edit("AAA/prices.json", '{"close": 1}')
        s.edit("AAA/live.json", '{"tier": "A"}')
        s.edit("AAA/fundamentals.json", '{"v": 9}')
        r, rep = s.audit()
        assert r.returncode == 0 and _state(rep, "AAA") == "in_sync", rep
    finally:
        s.close()


def test_suffix_branch_and_title_match():
    s = Sweep(tickers=("AAA", "BBB", "CCC"))
    try:
        for t in ("AAA", "BBB", "CCC"):
            s.edit(f"{t}/analysis.md", "# new\n")
        s.prs([_pr(60, "dcf/AAA-20261020", "OPEN"),
               _pr(61, "fix-bbb", "OPEN", title="Re-score: BBB — B Inc — Tier C"),
               _pr(62, "other", "OPEN", title="DCF pass 1 update: CCC — C Inc — Tier D"),
               _pr(63, "dcf/AAAB", "OPEN"), _pr(64, "dcf/AAA/x", "OPEN")])
        r, rep = s.audit()
        assert r.returncode == 0, r.stdout
        assert all(_state(rep, t) == "pr_open" for t in ("AAA", "BBB", "CCC")), rep
        import pr_audit
        assert not pr_audit.pr_belongs({"headRefName": "dcf/AAAB", "title": ""}, "AAA")
        assert pr_audit.pr_belongs({"headRefName": "dcf/AAA-20261020-2", "title": ""}, "AAA")
        assert pr_audit.pr_belongs({"headRefName": "z", "title": "DCF re-run: AAA — x"}, "AAA")
        assert pr_audit.pr_belongs({"headRefName": "z", "title": "Second pass: AAA — x"}, "AAA")
    finally:
        s.close()


def test_bulk_rebuild_pr_covers_its_files():
    s = Sweep()
    try:
        s.edit("AAA/score.json", json.dumps(dict(_pair("AAA")[1], name="AAA rebuilt")))
        s.edit("BBB/score.json", json.dumps(dict(_pair("BBB")[1], name="BBB rebuilt")))
        s.prs([_pr(70, "rebuild/5.7.0-20261021", "OPEN", title="Rebuild: make_score at release 5.7.0 over 1 folders")],
              files={"70": ["AAA/score.json", "AAA/key_numbers.md", "_system/overrides_registry.json"]})
        r, rep = s.audit()
        assert _state(rep, "AAA") == "pr_open" and _state(rep, "BBB") == "missing_pr", rep
    finally:
        s.close()


LIMIT_STUB = r'''import json, os, sys
here = os.path.dirname(os.path.abspath(__file__))
args = sys.argv[1:]
with open(os.path.join(here, "calls.jsonl"), "a", encoding="utf-8") as f:
    f.write(json.dumps(args) + "\n")
cfg = json.load(open(os.path.join(here, "cfg.json"), encoding="utf-8"))
if args[:2] == ["pr", "list"]:   # honours --state / --limit, newest first, as gh does
    state = args[args.index("--state") + 1] if "--state" in args else "open"
    limit = int(args[args.index("--limit") + 1]) if "--limit" in args else 30
    sys.stdout.write(json.dumps([p for p in cfg["prs"] if state == "all" or p["state"] == state.upper()][:limit]))
    sys.exit(0)
if args[:2] == ["pr", "view"]:   # gh's files(first: 100), unpaginated
    sys.stdout.write(json.dumps({"files": [{"path": p} for p in cfg["files"][:100]]}))
    sys.exit(0)
if args[:2] == ["api", "--paginate"]:   # the REST file list, paged to the end
    sys.stdout.write("".join(p + "\n" for p in cfg["files"]))
    sys.exit(0)
sys.exit(1)
'''


def _limit_stub(folder, prs, files=()):
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, "stub.py"), "w", encoding="utf-8") as f:
        f.write(LIMIT_STUB)
    with open(os.path.join(folder, "cfg.json"), "w", encoding="utf-8") as f:
        json.dump({"prs": prs, "files": list(files)}, f)
    return os.path.join(folder, "stub.py")


def test_pr_list_is_never_silently_truncated():
    """[whole-PR review fix, 2026-10-21; fails on 6dd4a4a] `gh pr list --state all --limit 1000` returned the newest
    1000 PRs and said nothing about the rest: AAA's OPEN PR #60, the 1001st newest, was invisible and AAA read
    MISSING_PR ("cut it now": a duplicate PR). Every PR is listed now (_ops.list_prs: gh pages to PR_LIST_LIMIT), and a
    list that reaches the limit is truncated — exit 3, never "no PR"."""
    s = Sweep(tickers=("AAA",))
    try:
        s.edit("AAA/analysis.md", "# AAA\nNew generation.\n")
        prs = [_pr(2000 - i, f"dcf/Z{i:04d}", "MERGED", merged="2026-10-20T12:00:00Z") for i in range(1000)]
        prs.append(_pr(60, "dcf/AAA", "OPEN"))
        stub = _limit_stub(os.path.join(s.o.root, "lim"), prs)
        out = os.path.join(s.o.root, "audit.json")
        r = H.run("pr_audit.py", "--no-fetch", "--json", out, base=s.c, env={"STOCKS_NOW": NOW.isoformat(),
                                                                             "STOCKS_GH": stub})
        assert r.returncode == 0, r.stdout + r.stderr
        assert _state(json.load(open(out, encoding="utf-8")), "AAA") == "pr_open"
        r = H.run("pr_audit.py", "--no-fetch", base=s.c, env={"STOCKS_NOW": NOW.isoformat(), "STOCKS_GH": stub,
                                                              "STOCKS_GH_LIST_LIMIT": "1001"})
        assert r.returncode == 3 and "the list is truncated" in r.stdout, r.stdout + r.stderr
    finally:
        s.close()


def test_bulk_pr_file_list_past_100_files():
    """[whole-PR review fix, 2026-10-21; fails on 6dd4a4a] `gh pr view --json files` lists 100 files (gh's
    files(first: 100)): an OPEN rebuild PR over 60 folders (122 files) covered only the first 50, and the other 10
    folders read MERGED_THEN_CHANGED with "copy main's files back" — reverting the rebuild. With a GitHub slug the REST
    file list is paged to the end (every folder pr_open); a list at gh pr view's 100 is truncated — exit 3."""
    tickers = [f"T{i:02d}" for i in range(60)]
    s = Sweep(tickers=tickers)
    try:
        for t in tickers:
            s.edit(f"{t}/score.json", json.dumps(dict(_pair(t)[1], misfit_notch={"applies": False})))
        prs = [_pr(500, "rebuild/5.7.0-20261021", "OPEN", created="2026-10-21T10:00:00Z",
                   title="Rebuild: make_score at release 5.7.0 over 60 folders")]
        prs += [_pr(100 + i, f"dcf/{t}", "MERGED", created="2026-10-20T09:00:00Z", merged="2026-10-20T12:00:00Z")
                for i, t in enumerate(tickers)]
        files = sorted([f"{t}/{n}" for t in tickers for n in ("key_numbers.md", "score.json")]
                       + ["_system/industry_returns.json", "_system/overrides_registry.json"])
        stub = _limit_stub(os.path.join(s.o.root, "bulk"), prs, files)
        out = os.path.join(s.o.root, "audit.json")
        env = {"STOCKS_NOW": NOW.isoformat(), "STOCKS_GH": stub, "STOCKS_REPO_SLUG": "o/r"}
        r = H.run("pr_audit.py", "--no-fetch", "--json", out, base=s.c, env=env)
        assert r.returncode == 0, r.stdout + r.stderr
        rep = json.load(open(out, encoding="utf-8"))
        assert sorted(rep["ok"]["pr_open"]) == tickers and rep["findings"] == [], rep["findings"][:3]
        r = H.run("pr_audit.py", "--no-fetch", base=s.c, env={"STOCKS_NOW": NOW.isoformat(), "STOCKS_GH": stub})
        assert r.returncode == 3 and "the file list is truncated at 100" in r.stdout, r.stdout + r.stderr
    finally:
        s.close()


def test_missing_folder():
    s = Sweep(queue=[{"ticker": "AAA", "status": "done", "completed": "2026-10-19", "claimed_at": OLD_CLAIM},
                     {"ticker": "ZZZ", "status": "done", "completed": "2026-10-19"}])
    try:
        r, rep = s.audit()
        assert r.returncode == 1 and _state(rep, "ZZZ") == "missing_folder", rep
        assert "MISSING_FOLDER       ZZZ" in r.stdout
    finally:
        s.close()


def test_gh_failure_exits_3():
    s = Sweep()
    try:
        stub = H.fake_gh(os.path.join(s.o.root, "gh"), {"pr list": {"rc": 1, "stderr": "HTTP 502"}})
        r = H.run("pr_audit.py", "--no-fetch", base=s.c, env={"STOCKS_GH": stub, "STOCKS_REPO_SLUG": "o/r"})
        assert r.returncode == 3 and r.stdout.startswith("pr_audit: CANNOT AUDIT — gh pr list failed"), r.stdout
        ok = H.fake_gh(os.path.join(s.o.root, "gh2"), {"pr list": []})
        r = H.run("pr_audit.py", "--no-fetch", base=s.c, env={"STOCKS_GH": ok, "STOCKS_REPO_SLUG": "o/r"})
        assert r.returncode == 0, r.stdout + r.stderr
        call = H.gh_calls(os.path.join(s.o.root, "gh2"))[0]
        assert call[:4] == ["pr", "list", "--repo", "o/r"] and "--state" in call and "all" in call, call
        H.git(s.c, "remote", "set-url", "origin", os.path.join(s.o.root, "nope.git"))
        fetch_fail = H.run("pr_audit.py", "--gh-json", s.gh, base=s.c)
        assert fetch_fail.returncode == 3 and "fetch" in fetch_fail.stdout, fetch_fail.stdout
    finally:
        s.close()


def test_crlf_blob_compare():
    s = Sweep(autocrlf=True, extra={".gitattributes": "* text=auto\n"})
    try:
        with open(os.path.join(s.c, "AAA", "analysis.md"), "rb") as f:
            assert b"\r\n" in f.read()
        r, rep = s.audit()
        assert r.returncode == 0 and rep["counts"]["in_sync"] == 2, rep
    finally:
        s.close()


def test_crlf_committed_csv_is_in_sync():
    """Every financials_history.csv is committed with CRLF bytes (the csv module writes \\r\\n). In a
    core.autocrlf=true checkout git leaves such a file as it is, but hash-object WITH filters (it does not read the
    index) still converts it — the filtered id differs from the committed blob. Measured on the real tree: all 524
    scored done names read "differs: financials_history.csv" until the raw id was compared too."""
    csv = b"period_end,fy_label,revenue\r\n2024-12-31,FY2024,100\r\n2025-12-31,FY2025,110\r\n"
    s = Sweep(autocrlf=True, extra={"AAA/financials_history.csv": csv, "BBB/financials_history.csv": csv})
    try:
        with open(os.path.join(s.c, "AAA", "financials_history.csv"), "rb") as f:
            assert f.read() == csv, "the checkout keeps the committed CRLF bytes"
        filt = H.git(s.c, "hash-object", "--path=AAA/financials_history.csv", "AAA/financials_history.csv").strip()
        assert filt != H.git(s.c, "rev-parse", "HEAD:AAA/financials_history.csv").strip(), "the case under test"
        r, rep = s.audit()
        assert r.returncode == 0 and rep["counts"]["in_sync"] == 2, rep
        with open(os.path.join(s.c, "AAA", "financials_history.csv"), "ab") as f:
            f.write(b"2026-12-31,FY2026,120\r\n")
        r, rep = s.audit()
        f = next(x for x in rep["findings"] if x["ticker"] == "AAA")
        assert f["differs"] == ["financials_history.csv"], f
    finally:
        s.close()


def test_score_not_from_run_is_checked_first():
    s = Sweep()
    try:
        n, sc = _pair("AAA")
        s.edit("AAA/dcf_numbers.json", json.dumps(dict(n, implied_irr_weighted=0.12, tier_by_numbers="C")))
        s.prs([_pr(80, "dcf/AAA", "OPEN", created="2026-10-20T09:00:00Z")])
        r, rep = s.audit()
        assert r.returncode == 1 and _state(rep, "AAA") == "score_not_from_run", rep
        f = rep["findings"][0]
        assert "make_score refused" in f["hint"] and f.get("mismatch"), f
        assert "SCORE_NOT_FROM_RUN   AAA" in r.stdout
    finally:
        s.close()


def test_facts_and_saved_runs_are_record_files():
    s = Sweep(extra={"AAA/dcf_numbers_prelim.json": {"run": 1}})
    try:
        s.edit("AAA/facts.json", {"schema": 1, "facts": []})
        s.edit("AAA/dcf_numbers_prelim.json", {"run": 2})
        s.edit("AAA/annual_instance.json", {"x": 1})
        r, rep = s.audit()
        f = next(x for x in rep["findings"] if x["ticker"] == "AAA")
        assert f["differs"] == ["annual_instance.json", "dcf_numbers_prelim.json", "facts.json"], f
        os.remove(os.path.join(s.c, "AAA", "dcf_numbers_prelim.json"))
        os.remove(os.path.join(s.c, "AAA", "facts.json"))
        os.remove(os.path.join(s.c, "AAA", "annual_instance.json"))
        r, rep = s.audit()
        f = next(x for x in rep["findings"] if x["ticker"] == "AAA")
        assert f["differs"] == ["dcf_numbers_prelim.json"], "a saved run on main that the sweep folder lost differs"
    finally:
        s.close()


def _pass2(s, entries):
    with open(os.path.join(s.c, "_system", "second_pass_queue.json"), "w", encoding="utf-8") as f:
        json.dump({"entries": entries}, f)


def test_a_second_pass_after_the_pass1_merge_is_its_own_generation():
    """Review 2026-10-21 (P3): a pass-2 change after the pass-1 PR merged was MERGED_THEN_CHANGED at once, with a
    hint to copy main's files back — which would erase the review. second_pass_queue.json was never read."""
    s = Sweep(tickers=("AAA",))
    try:
        p1 = _pr(5, "dcf/AAA", "MERGED", created="2026-10-19T22:00:00Z", merged="2026-10-20T01:00:00Z")
        s.prs([p1])
        r, rep = s.audit()
        assert _state(rep, "AAA") == "in_sync", rep
        s.edit("AAA/second_pass.md", "# AAA second pass (2026-10-21)\nVerdict: changed.\n")
        _pass2(s, {"AAA": {"status": "done_changed", "date": "2026-10-21", "generation": OLD_CLAIM}})
        r, rep = s.audit()   # 12:00 ET on the review's day
        assert r.returncode == 0 and _state(rep, "AAA") == "grace", rep
        r, rep = s.audit(env={"STOCKS_NOW": "2026-10-22T05:00:00"})   # the review's day + 5 h: still grace
        assert _state(rep, "AAA") == "grace", rep
        r, rep = s.audit(env={"STOCKS_NOW": "2026-10-22T07:00:00"})
        assert r.returncode == 1 and _state(rep, "AAA") == "missing_pr", rep
        f = rep["findings"][0]
        assert f["generation"] == "pass2" and f["pass2"] == {"status": "done_changed", "date": "2026-10-21"}, f
        assert "cut the Second pass PR" in f["hint"] and "copy main" not in f["hint"], f["hint"]
        assert "acquire AAA --kind pass2" in f["hint"], f["hint"]
        assert "MISSING_PR           AAA   second pass done_changed 2026-10-21  differs: second_pass.md" in r.stdout, \
            r.stdout
        p2 = _pr(6, "dcf/AAA-20261019", "OPEN", created="2026-10-21T18:00:00Z", title="Second pass: AAA — A — Tier B")
        s.prs([p2, p1])
        r, rep = s.audit(env={"STOCKS_NOW": "2026-10-22T07:00:00"})
        assert r.returncode == 0 and _state(rep, "AAA") == "pr_open", rep
        s.prs([dict(p2, state="MERGED", mergedAt="2026-10-21T22:00:00Z"), p1])
        r, rep = s.audit(env={"STOCKS_NOW": "2026-10-22T07:00:00"})   # merged, and the folder still differs
        assert _state(rep, "AAA") == "merged_then_changed", rep
        assert "PR #6 merged 2026-10-21 18:00 ET" in r.stdout, r.stdout
        # a no-change review writes second_pass.md too: the same generation rule
        s.prs([p1])
        _pass2(s, {"AAA": {"status": "done_no_change", "date": "2026-10-21", "generation": OLD_CLAIM}})
        r, rep = s.audit(env={"STOCKS_NOW": "2026-10-22T07:00:00"})
        assert _state(rep, "AAA") == "missing_pr" and rep["findings"][0]["generation"] == "pass2", rep
        # a review of an OLDER scoring generation does not apply: the folder change is pass 1's
        _pass2(s, {"AAA": {"status": "done_changed", "date": "2026-10-18", "generation": "2026-10-17T09:00:00-04:00"}})
        r, rep = s.audit(env={"STOCKS_NOW": "2026-10-22T07:00:00"})
        assert _state(rep, "AAA") == "merged_then_changed" and "generation" not in rep["findings"][0], rep
        # an in-progress review is not a finished one
        _pass2(s, {"AAA": {"status": "in_progress", "date": "2026-10-21", "generation": OLD_CLAIM,
                           "claimed_at": "2026-10-21T11:00:00-04:00"}})
        r, rep = s.audit(env={"STOCKS_NOW": "2026-10-22T07:00:00"})
        assert _state(rep, "AAA") == "merged_then_changed", rep
        with open(os.path.join(s.c, "_system", "second_pass_queue.json"), "w", encoding="utf-8") as fh:
            json.dump({"entries": []}, fh)
        r, _ = s.audit()
        assert r.returncode == 3 and "second_pass_queue.json is malformed" in r.stdout, r.stdout
    finally:
        s.close()


def test_app_outside_the_queue_is_a_candidate():
    s = Sweep(tickers=("AAA", "APP"), queue=[{"ticker": "AAA", "status": "done", "completed": "2026-10-19",
                                               "claimed_at": OLD_CLAIM}])
    try:
        r, rep = s.audit()
        assert rep["candidates"] == 2 and _state(rep, "APP") == "in_sync", rep
        s.edit("APP/analysis.md", "# new\n")
        r, rep = s.audit()
        f = next(x for x in rep["findings"] if x["ticker"] == "APP")
        assert f["state"] == "missing_pr" and f["generation_start"].startswith("2026-10-18"), f
    finally:
        s.close()


if __name__ == "__main__":
    sys.exit(H.run_tests(globals()))
