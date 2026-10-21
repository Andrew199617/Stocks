#!/usr/bin/env python3
"""preflight.py — the engine drift guard (engine 5.7, Andrew's ruling R5 of 2026-10-19; design 05 §2, §9).
Run: python _system/tests/test_preflight.py. Offline: temp git repos with a local bare origin (ops_harness).

The miss it stops: after PR #31 merged engine 5.5 the sweep tree kept running 5.4.0 (MOH #37, ESTC #35 published
5.4 scores). Covered: in sync -> exit 0 / "preflight: OK"; origin moves ENGINE_RELEASE -> exit 1, both releases
named, state behind with the matched sha and commits since; a local edit -> diverged; a policy file added on main
-> missing_here (the guard set comes from origin's tree, not a constant); ENGINE_BACKLOG.md and tests are never
guarded; README drift is advisory (exit 0); a core.autocrlf=true checkout is not drift; a failed fetch retries then
exits 4; a non-git base exits 3; --sync refuses a live claim (exit 5) and otherwise syncs exactly the guarded
files; every local module the scoring chain imports is a POLICY path; _system/industry_returns.json is a DATA input
(review 2026-10-21): missing or unreadable here is drift and --sync brings main's copy, the sweep tree's own build is
a note that --sync never overwrites.
"""
import ast
import datetime
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ops_harness as H  # noqa: E402
import dcf_engine as E  # noqa: E402
try:
    import preflight  # noqa: E402
except ImportError:   # the code before R5 has no preflight.py: each test below fails on its own
    preflight = None

CUR = E.ENGINE_RELEASE


def _origin(extra=None):
    files = {"_system/dcf_engine.py": f'"""engine"""\nENGINE_RELEASE = "{CUR}"\n',
             "_system/make_score.py": "import dcf_engine\nprint('score')\n",
             "_system/WORKER_SPEC.md": "# spec\n1. claim\n",
             "_system/README.md": "# readme\n",
             "_system/ENGINE_BACKLOG.md": "# Engine backlog\n",
             "_system/tests/test_x.py": "print('t')\n",
             "_system/queue.json": '{"queue": []}\n',
             "AGENTS.md": "# agents\n",
             "AAA/score.json": '{"tier_final": "C"}\n'}
    files.update(extra or {})
    return H.make_origin(files)


def _pf(clone, *args):
    return H.run("preflight.py", "--repo", clone, *args, base=clone)


def _json(r):
    return json.loads(r.stdout)


def test_in_sync_exits_0():
    o = _origin()
    try:
        c = H.clone(o)
        r = _pf(c)
        assert r.returncode == 0, r.stdout + r.stderr
        assert r.stdout.splitlines()[0].startswith("preflight: OK — policy files match origin/main "), r.stdout
        assert f"(ENGINE_RELEASE {CUR})" in r.stdout.splitlines()[0]
        d = _json(_pf(c, "--json"))
        assert d["status"] == "in_sync" and d["drift"] == [] and d["fetched"] is True and d["fetch_attempts"] == 1
        assert d["origin_sha"] == o.head()
    finally:
        o.close()


def test_release_drift_exits_1_and_names_both_releases():
    o = _origin()
    try:
        c = H.clone(o)
        new = H.commit_on_origin(o, "_system/dcf_engine.py", '"""engine"""\nENGINE_RELEASE = "5.8.0"\n', "release 5.8")
        r = _pf(c)
        assert r.returncode == 1, r.stdout
        first = r.stdout.splitlines()[0]
        assert first.startswith("preflight: ENGINE DRIFT — this tree does not run origin/main's method"), first
        assert f"ENGINE_RELEASE here {CUR}, origin/main 5.8.0" in first and new[:7] in first, first
        assert "Do not claim." in r.stdout and "rebuild_scores.py" in r.stdout
        d = _json(_pf(c, "--json", "--no-fetch"))
        assert d["engine_release"] == {"here": CUR, "origin": "5.8.0", "same": False}, d["engine_release"]
        row = next(x for x in d["drift"] if x["path"] == "_system/dcf_engine.py")
        assert row["state"] == "behind" and row["class"] == "policy", row
        assert row["matched_origin_sha"] == H.git(c, "rev-parse", "HEAD").strip(), row
        assert row["commits_since"] == 1, row
        assert "behind (matches origin/main at" in r.stdout and "1 commit since)" in r.stdout, r.stdout
    finally:
        o.close()


def test_local_edit_is_diverged():
    o = _origin()
    try:
        c = H.clone(o)
        with open(os.path.join(c, "_system", "make_score.py"), "a", encoding="utf-8") as f:
            f.write("# a local edit\n")
        r = _pf(c, "--json")
        assert r.returncode == 1
        row = next(x for x in _json(r)["drift"] if x["path"] == "_system/make_score.py")
        assert row["state"] == "diverged", row
        t = _pf(c, "--no-fetch")
        assert "_system/make_score.py  diverged (never on origin/main)" in t.stdout, t.stdout
    finally:
        o.close()


def test_policy_file_added_on_main_is_missing_here():
    o = _origin()
    try:
        c = H.clone(o)
        H.commit_on_origin(o, "_system/check_quotes.py", "print('gate')\n", "add a gate")
        r = _pf(c, "--json")
        assert r.returncode == 1
        row = next(x for x in _json(r)["drift"] if x["path"] == "_system/check_quotes.py")
        assert row["state"] == "missing_here" and row["class"] == "policy", row
        assert "_system/check_quotes.py  missing here" in _pf(c, "--no-fetch").stdout
    finally:
        o.close()


def test_backlog_and_tests_are_not_guarded():
    o = _origin()
    try:
        c = H.clone(o)
        H.commit_on_origin(o, "_system/ENGINE_BACKLOG.md", "# Engine backlog\n\n### EB-001 — x\n", "append")
        H.commit_on_origin(o, "_system/tests/test_x.py", "print('t2')\n", "test edit")
        H.commit_on_origin(o, "_system/queue.json", '{"queue": [1]}\n', "state")
        H.commit_on_origin(o, "AAA/score.json", '{"tier_final": "D"}\n', "data")
        r = _pf(c, "--json")
        assert r.returncode == 0, r.stdout
        d = _json(r)
        assert d["drift"] == [] and d["advisory"] == [], d
    finally:
        o.close()


def test_advisory_drift_is_a_note():
    o = _origin()
    try:
        c = H.clone(o)
        H.commit_on_origin(o, "_system/README.md", "# readme v2\n", "docs")
        r = _pf(c, "--json")
        assert r.returncode == 0, r.stdout
        d = _json(r)
        assert d["drift"] == [] and [x["path"] for x in d["advisory"]] == ["_system/README.md"], d
        t = _pf(c, "--no-fetch")
        assert t.stdout.startswith("preflight: OK") and "advisory: _system/README.md  behind" in t.stdout, t.stdout
    finally:
        o.close()


def test_crlf_checkout_is_not_drift():
    o = _origin({".gitattributes": "* text=auto\n"})
    try:
        c = H.clone(o, autocrlf=True)
        with open(os.path.join(c, "_system", "make_score.py"), "rb") as f:
            assert b"\r\n" in f.read(), "the autocrlf clone holds CRLF bytes (the case under test)"
        r = _pf(c, "--json")
        assert r.returncode == 0, r.stdout
        assert _json(r)["drift"] == []
    finally:
        o.close()


def test_crlf_committed_file_is_not_drift():
    """A file committed WITH CRLF bytes: an autocrlf=true checkout leaves it as it is, hash-object with filters
    converts it anyway (it does not read the index), so only the raw bytes equal the blob — still in sync."""
    o = _origin({"_system/make_score.py": b"import dcf_engine\r\nprint('score')\r\n"})
    try:
        c = H.clone(o, autocrlf=True)
        r = _pf(c, "--json")
        assert r.returncode == 0, r.stdout
        assert _json(r)["drift"] == []
        with open(os.path.join(c, "_system", "make_score.py"), "ab") as f:
            f.write(b"# edited\r\n")
        assert _pf(c, "--no-fetch").returncode == 1, "a real edit of that file is still drift"
    finally:
        o.close()


def test_fetch_failure_retries_then_exits_4():
    o = _origin()
    try:
        c = H.clone(o)
        H.git(c, "remote", "set-url", "origin", os.path.join(o.root, "no_such_repo.git"))
        r = _pf(c, "--json", "--attempts", "2", "--pause", "0")
        assert r.returncode == 4, r.stdout + r.stderr
        d = _json(r)
        assert d["fetch_attempts"] == 2 and d["status"] == "error", d
        t = _pf(c, "--attempts", "2", "--pause", "0")
        assert t.stdout.startswith("preflight: CANNOT VERIFY — git fetch origin main failed 2 times"), t.stdout
    finally:
        o.close()


def test_not_a_git_checkout_exits_3():
    import tempfile
    d = tempfile.mkdtemp(prefix="pf_nogit_")
    try:
        os.makedirs(os.path.join(d, "_system"))
        r = H.run("preflight.py", "--repo", d, base=d)
        assert r.returncode == 3, r.stdout
        assert r.stdout.startswith("preflight: CANNOT VERIFY — ") and "not a git work tree" in r.stdout, r.stdout
        bad = H.run("preflight.py", "--attempts", "0", base=d)
        assert bad.returncode == 2
    finally:
        shutil.rmtree(d, ignore_errors=True)


def test_sync_refuses_a_live_claim_then_syncs():
    o = _origin()
    try:
        c = H.clone(o)
        H.commit_on_origin(o, "_system/dcf_engine.py", '"""engine"""\nENGINE_RELEASE = "5.8.0"\n', "release")
        H.commit_on_origin(o, "_system/check_quotes.py", "print('gate')\n", "new gate")
        H.commit_on_origin(o, "_system/README.md", "# readme v2\n", "docs")
        H.commit_on_origin(o, "AAA/score.json", '{"tier_final": "D"}\n', "data on main")
        with open(os.path.join(c, "_system", "scratch_tool.py"), "w", encoding="utf-8") as f:
            f.write("print('local only')\n")
        now = datetime.datetime(2026, 10, 19, 15, 0)
        claim = {"queue": [{"ticker": "AAA", "status": "in_progress",
                            "claimed_at": (now - datetime.timedelta(minutes=10)).isoformat() + "-04:00"}]}
        with open(os.path.join(c, "_system", "queue.json"), "w", encoding="utf-8") as f:
            json.dump(claim, f)
        before = H.tree_sha(c)
        env = {"STOCKS_NOW": now.isoformat()}
        r = H.run("preflight.py", "--sync", base=c, env=env)
        assert r.returncode == 5, r.stdout + r.stderr
        assert r.stdout.startswith("preflight: SYNC REFUSED — AAA is being scored"), r.stdout
        assert H.tree_sha(c) == before, "a refused sync changed files"
        claim["queue"][0]["claimed_at"] = (now - datetime.timedelta(hours=2)).isoformat() + "-04:00"
        with open(os.path.join(c, "_system", "queue.json"), "w", encoding="utf-8") as f:
            json.dump(claim, f)
        r = H.run("preflight.py", "--sync", base=c, env=env)
        assert r.returncode == 0, r.stdout + r.stderr
        assert "next: python3 _system/rebuild_scores.py" in r.stdout and f"folders scored on release {CUR}" in r.stdout
        for rel in ("_system/dcf_engine.py", "_system/check_quotes.py", "_system/README.md"):
            assert H.git(c, "hash-object", rel).strip() == H.git(c, "rev-parse", f"origin/main:{rel}").strip(), rel
        with open(os.path.join(c, "AAA", "score.json"), encoding="utf-8") as f:
            assert json.load(f)["tier_final"] == "C", "a sync never touches a company folder"
        assert os.path.exists(os.path.join(c, "_system", "scratch_tool.py")), "local_only files are never deleted"
        again = _pf(c, "--no-fetch")
        assert again.returncode == 0, again.stdout
    finally:
        o.close()


def test_industry_file_is_a_data_input():
    """Review 2026-10-21 (P1): _system/industry_returns.json is a make_score input (moat_evidence) that was outside
    the guard and outside --sync, so a first 5.7 deploy scored every folder without it while preflight said OK.
    Missing here is drift (--sync brings main's copy); the sweep tree's own build is a note, never overwritten."""
    main = '{"schema": 1, "built": "2026-10-20"}\n'
    o = _origin({"_system/industry_returns.json": main})
    try:
        c = H.clone(o)
        p = os.path.join(c, "_system", "industry_returns.json")
        assert preflight.classify("_system/industry_returns.json") == "data"
        assert _pf(c).returncode == 0
        with open(p, "w", encoding="utf-8", newline="\n") as f:
            f.write('{"schema": 1, "built": "2026-10-22"}\n')   # the daily cron's rewrite
        r = _pf(c, "--json")
        assert r.returncode == 0, r.stdout
        d = _json(r)
        row = next(x for x in d["advisory"] if x["path"] == "_system/industry_returns.json")
        assert row["class"] == "data" and row["state"] == "diverged" and d["drift"] == [], d
        t = _pf(c, "--no-fetch")
        assert "advisory: _system/industry_returns.json  diverged (never on origin/main) — the sweep tree's own build" \
            in t.stdout, t.stdout
        assert _pf(c, "--list-drift", "--no-fetch").stdout.strip() == "", "--list-drift prints what --sync checks out"
        r = H.run("preflight.py", "--sync", base=c)
        assert r.returncode == 0 and "nothing to sync" in r.stdout, r.stdout
        assert "2026-10-22" in open(p, encoding="utf-8").read(), "the sweep tree's own build is never overwritten"
        os.remove(p)   # the first 5.7 deploy: main has the file, the sweep tree never had it
        r = _pf(c, "--json")
        assert r.returncode == 1, r.stdout
        row = next(x for x in _json(r)["drift"] if x["path"] == "_system/industry_returns.json")
        assert row["state"] == "missing_here" and row["class"] == "data", row
        assert _pf(c, "--list-drift", "--no-fetch").stdout.split() == ["_system/industry_returns.json"]
        r = H.run("preflight.py", "--sync", base=c)
        assert r.returncode == 0 and "_system/industry_returns.json" in r.stdout, r.stdout
        assert open(p, encoding="utf-8").read().replace("\r\n", "\n") == main
        assert _pf(c, "--no-fetch").returncode == 0
        open(p, "w").close()   # an empty (unreadable) file: make_score would score without it, like a missing one
        r = _pf(c, "--json", "--no-fetch")
        assert r.returncode == 1, r.stdout
        row = next(x for x in _json(r)["drift"] if x["path"] == "_system/industry_returns.json")
        assert row["state"] == "unreadable", row
        assert H.run("preflight.py", "--sync", base=c).returncode == 0
        assert open(p, encoding="utf-8").read().replace("\r\n", "\n") == main
    finally:
        o.close()


def test_guard_covers_every_module_the_chain_imports():
    chain = ("dcf_engine.py", "make_score.py", "ttm.py", "queue.py", "check_quotes.py")
    local = {n[:-3] for n in os.listdir(H.SYS) if n.endswith(".py")}
    seen = set()
    for name in chain:
        with open(os.path.join(H.SYS, name), encoding="utf-8") as f:
            tree = ast.parse(f.read())
        for node in ast.walk(tree):
            mods = []
            if isinstance(node, ast.Import):
                mods = [a.name.split(".")[0] for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                mods = [node.module.split(".")[0]]
            seen.update(m for m in mods if m in local)
    assert {"_lock", "facts", "check_quotes", "dcf_engine"} <= seen, seen
    for m in sorted(seen) + [c[:-3] for c in chain]:
        assert preflight.classify(f"_system/{m}.py") == "policy", m
    assert preflight.classify("_system/tests/test_x.py") is None
    assert preflight.classify("_system/ENGINE_BACKLOG.md") is None
    assert preflight.classify("_system/overrides_registry.json") is None
    assert preflight.classify("_system/PR_PROTOCOL.md") == "policy"
    assert preflight.classify("automation/crons/minutely/x.md") == "advisory"


if __name__ == "__main__":
    sys.exit(H.run_tests(globals()))
