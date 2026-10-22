#!/usr/bin/env python3
"""Engine drift guard (engine 5.7, Andrew's ruling R5 of 2026-10-19 — sweep reliability).

Before a worker claims a ticker it checks that its tree runs origin/main's method: every policy-bearing file here
must be the same blob as on origin/main. The miss it stops: after PR #31 merged engine 5.5 the sweep tree kept
running 5.4.0, and MOH (#37) and ESTC (#35) were published as 5.4 scores (Codex r4317729858).

Usage:
  python3 _system/preflight.py [--repo PATH] [--remote origin] [--branch main] [--json] [--no-fetch]
                               [--attempts 3] [--pause 2]
  python3 _system/preflight.py --list-drift      # the paths that differ, one per line (for scripts)
  python3 _system/preflight.py --sync            # the main agent's step after a code PR merges — never a worker

What is guarded (computed from origin/main's tree, so a policy file added on main is checked even by a stale copy
of this script, union the local tree):
  POLICY   (drift -> exit 1): every top-level _system/*.py (not _system/tests/), _system/WORKER_SPEC.md,
           _system/SECOND_PASS.md, _system/PR_PROTOCOL.md, AGENTS.md
  ADVISORY (drift -> a note, exit 0): _system/README.md, _system/SITE_CONTRACT.md, automation/**, _daily/site/**
  DATA     _system/industry_returns.json — the one generated method input make_score reads from _system/ (the moat
           evidence's industry_structure pillar, L3): missing or unreadable here (not a JSON object) while main has
           it -> drift (exit 1; --sync checks main's copy out — make_score would silently score without it);
           a different build -> a note only, never synced over (the daily cron and rebuild_scores.py write the
           sweep tree's own build; pr_worktree prepare scores against it and names both builds in the Mechanics
           block — review 2026-10-21: before, the file was outside the guard and every prepare deadlocked)
  never:   _system/ENGINE_BACKLOG.md (data PRs append to it), every other _system/*.json / *.csv (state and data),
           company folders, tests.
A file's state: same | behind (its content is an older origin/main blob: matched sha, date, commits since) |
diverged (never on origin/main) | missing_here | local_only (a top-level _system/*.py origin/main lacks — advisory).
Content is hashed with `git hash-object` WITH the repo's filters, so a core.autocrlf=true checkout is not drift (and
also as raw bytes: a file committed with CRLF bytes is left as it is by the checkout, _ops.blob_variants).

Exit codes: 0 in sync (advisory notes allowed) · 1 drift in a POLICY path · 2 usage · 3 not a git work tree / no
such remote or branch / git missing · 4 the fetch failed after every attempt (fail closed: the run cannot prove it
is on main's method) · 5 --sync refused (a live claim).
The first line of the text output is the report line a worker quotes (run_health record ... fail --stdin).

--sync (under the queue lock, queue lock first per queue.py's lock order, held for the whole sync so no claim can
start mid-checkout): refuses (exit 5) while queue.json or second_pass_queue.json holds a live in_progress claim
(claimed within queue.py's 90-minute lease), and while either file is malformed or unreadable (queue_rows: missing
means empty; whole-PR review fix, 2026-10-21 — an unreadable state used to read as "no live claim"); otherwise
`git checkout <remote>/<branch> -- <every guarded path that is not same>` (path-limited: no company folder, no
state file; local_only files are never deleted; the DATA file only when it is missing here) and prints the next step, a rebuild_scores.py dry run. Run it on the VM before any engine-5.7 registry event exists there: a
pre-5.7 make_score refuses a registry that holds one.

In-process API (pr_worktree prepare, rebuild_scores): check(base=..., fetch=...) -> report dict with "exit".
"""
import argparse
import datetime
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import _ops  # noqa: E402
from _lock import locked  # noqa: E402

POLICY_FILES = ("_system/WORKER_SPEC.md", "_system/SECOND_PASS.md", "_system/PR_PROTOCOL.md", "AGENTS.md")
ADVISORY_FILES = ("_system/README.md", "_system/SITE_CONTRACT.md")
ADVISORY_PREFIXES = ("automation/", "_daily/site/")
NEVER = ("_system/ENGINE_BACKLOG.md",)
# A generated file make_score reads as a method input (L3: moat_scorecard.load_industry, $STOCKS_BASE/_system). Its
# absence is drift (the sweep would score moat evidence without the industry pillar main measures); a different
# build is the sweep tree's own (03b §3.3.3: the daily cron and rebuild_scores.py --write it) and only a note.
DATA_FILES = ("_system/industry_returns.json",)
DATA_NOTE = ("the sweep tree's own build (the daily cron and rebuild_scores.py write it); company PRs are scored "
             "against it and their Mechanics block names both builds")
LEASE_MINUTES = 90   # queue.py LEASE_MINUTES (not imported: queue.py imports the quote gate)
SYNC_NEXT = "next: python3 _system/rebuild_scores.py  (dry run: folders scored on release {old})"
DRIFT_TAIL = ("Do not claim. The main agent syncs the tree (PR_PROTOCOL.md \"Syncing the sweep tree\"); folders "
              "scored meanwhile are rebuilt with rebuild_scores.py.")


def classify(path):
    """'policy' | 'data' | 'advisory' | None for a repo-relative path (forward slashes)."""
    if path in NEVER:
        return None
    if path in DATA_FILES:
        return "data"
    d, _, name = path.rpartition("/")
    if d == "_system" and name.endswith(".py"):
        return "policy"
    if path in POLICY_FILES:
        return "policy"
    if path in ADVISORY_FILES or path.startswith(ADVISORY_PREFIXES):
        return "advisory"
    return None


def _local_candidates(base):
    """Guard-class paths present in the local tree: top-level _system/*.py and the named files (advisory trees are
    taken from origin's list only — a local untracked file under _daily/site/ is a build product, not drift)."""
    out = set()
    sysdir = os.path.join(base, "_system")
    try:
        for name in os.listdir(sysdir):
            if name.endswith(".py") and os.path.isfile(os.path.join(sysdir, name)):
                out.add(f"_system/{name}")
    except OSError:
        pass
    for rel in POLICY_FILES + ADVISORY_FILES + DATA_FILES:
        if os.path.isfile(os.path.join(base, *rel.split("/"))):
            out.add(rel)
    return out


DATA_BROKEN = ("missing_here", "unreadable")


def _readable_json(base, rel):
    try:
        with open(os.path.join(base, *rel.split("/")), encoding="utf-8") as f:
            return isinstance(json.load(f), dict)
    except (OSError, ValueError):
        return False


def _row_class(cls, state):
    """Where a non-same row goes: 'policy' (drift, exit 1) or 'advisory' (a note). A DATA file is drift only when it
    is missing or unreadable here (make_score would score without it); local_only is always advisory."""
    if state == "local_only":
        return "advisory"
    if cls == "data":
        return "policy" if state in DATA_BROKEN else "advisory"
    return cls


def _history(repo, ref, path):
    """[(sha, committer date, blob)] newest first: the blob of `path` after each commit on ref that changed it."""
    rc, out, _ = _ops.git(repo, "log", "--format=@@%H %cI", "--raw", "--no-abbrev", "--no-renames", ref, "--", path,
                          timeout=300)
    rows, cur = [], None
    if rc != 0:
        return rows
    for line in out.splitlines():
        if line.startswith("@@"):
            sha, _, date = line[2:].partition(" ")
            cur = [sha, date, None]
            rows.append(cur)
        elif line.startswith(":") and cur is not None and cur[2] is None:
            parts = line.split("\t", 1)[0].split()
            if len(parts) >= 4:
                cur[2] = parts[3]
    return [tuple(r) for r in rows if r[2]]


def _state(repo, ref, path, here, origin_blob):
    """(state, extra) for one guarded path; `here` is the file's (filtered, raw) blob ids (_ops.blob_variants: a
    file committed with CRLF bytes matches on its raw id in a core.autocrlf=true checkout)."""
    present = bool(here) and any(here)
    if _ops.blob_matches(here, origin_blob):
        return "same", {}
    if not present:
        return "missing_here", {}
    if origin_blob is None:
        return "local_only", {}
    hist = _history(repo, ref, path)
    for i, (sha, date, blob) in enumerate(hist):
        if _ops.blob_matches(here, blob):
            return "behind", {"matched_origin_sha": sha, "matched_origin_date": date, "commits_since": i}
    return "diverged", {}


def check(base=None, repo=None, remote="origin", branch="main", fetch=True, attempts=3, pause=2.0):
    """The drift report (see the module docstring). Never raises; report["exit"] is the exit code."""
    base = os.path.abspath(base or _ops.base_dir())
    repo = os.path.abspath(repo or base)
    ref = f"{remote}/{branch}"
    rep = {"status": "error", "exit": 3, "checked_at": _ops.iso(_ops.now_et()), "base": base, "repo": repo,
           "remote_ref": ref, "origin_sha": None, "origin_committed_at": None, "fetched": False, "fetch_attempts": 0,
           "engine_release": {"here": _ops.local_engine_release(base), "origin": None, "same": None},
           "drift": [], "advisory": [], "error": None}
    rc, top, err = _ops.git(repo, "rev-parse", "--show-toplevel")
    if rc != 0 or not top.strip():
        rep["error"] = ("git is not installed" if rc == 127 else f"{repo} is not a git work tree")
        return rep
    rc, _, _ = _ops.git(repo, "remote", "get-url", remote)
    if rc != 0:
        rep["error"] = f"{repo} has no remote named {remote!r}"
        return rep
    if fetch:
        ok, used, last = _ops.fetch_ref(repo, remote, branch, attempts=attempts, pause=pause)
        rep["fetch_attempts"] = used
        if not ok:
            rep["exit"] = 4
            rep["error"] = f"git fetch {remote} {branch} failed {used} time{'s' if used != 1 else ''} ({last})"
            return rep
        rep["fetched"] = True
    sha = _ops.rev(repo, ref)
    if not sha:
        rep["error"] = f"no {ref} in {repo} (fetch it, or check --remote / --branch)"
        return rep
    rep["origin_sha"] = sha
    rep["origin_committed_at"] = _ops.commit_date(repo, sha)
    rep["engine_release"]["origin"] = _ops.engine_release_of(_ops.show(repo, sha, "_system/dcf_engine.py"))
    rel = rep["engine_release"]
    rel["same"] = rel["here"] == rel["origin"]

    origin = _ops.tree_blobs(repo, sha)
    guarded = {p: c for p in origin if (c := classify(p))}
    for p in _local_candidates(base):
        c = classify(p)
        if c:
            guarded.setdefault(p, c)
    here = _ops.blob_variants(repo, base, sorted(guarded))
    for path in sorted(guarded):
        cls = guarded[path]
        st, extra = _state(repo, sha, path, here.get(path), origin.get(path))
        if st == "same":
            continue
        if cls == "data" and origin.get(path) and st not in DATA_BROKEN and not _readable_json(base, path):
            st, extra = "unreadable", {}
        row = dict({"path": path, "class": "advisory" if st == "local_only" else cls, "state": st,
                    "here_blob": (here.get(path) or (None, None))[0], "origin_blob": origin.get(path)}, **extra)
        (rep["drift"] if _row_class(cls, st) == "policy" else rep["advisory"]).append(row)
    rep["status"] = "drift" if rep["drift"] else "in_sync"
    rep["exit"] = 1 if rep["drift"] else 0
    return rep


def _describe(row):
    st = row["state"]
    if st == "behind":
        d = (row.get("matched_origin_date") or "")[:10]
        n = row.get("commits_since", 0)
        text = (f"behind (matches {row.get('remote_ref', 'origin/main')} at {row['matched_origin_sha'][:7]} {d}, {n} "
                f"commit{'s' if n != 1 else ''} since)")
    else:
        text = {"diverged": "diverged (never on origin/main)", "missing_here": "missing here",
                "unreadable": "unreadable here (not a JSON object: make_score would score without it)",
                "local_only": "local only (not on origin/main)"}.get(st, st)
    if row.get("class") == "data" and st not in DATA_BROKEN:
        text += f" — {DATA_NOTE}"
    return text


def sync_paths(rep):
    """The paths --sync checks out (and --list-drift prints): every drift / advisory row except local_only files
    (never deleted) and a DATA file that exists here and reads (the sweep tree's own build is never overwritten)."""
    return [r["path"] for r in rep["drift"] + rep["advisory"]
            if r["state"] != "local_only" and not (r.get("class") == "data" and r["state"] not in DATA_BROKEN)]


def first_line(rep):
    """The report line a worker quotes."""
    ref = rep.get("remote_ref", "origin/main")
    sha = (rep.get("origin_sha") or "")[:7]
    rel = rep.get("engine_release") or {}
    if rep["exit"] == 0:
        return f"preflight: OK — policy files match {ref} {sha} (ENGINE_RELEASE {rel.get('origin')})"
    if rep["exit"] == 1:
        return (f"preflight: ENGINE DRIFT — this tree does not run {ref}'s method ({ref} {sha}; ENGINE_RELEASE here "
                f"{rel.get('here')}, {ref} {rel.get('origin')})")
    return f"preflight: CANNOT VERIFY — {rep.get('error')}"


def text_report(rep):
    lines = [first_line(rep)]
    for row in rep.get("drift", []):
        lines.append(f"  {row['path']}  {_describe(dict(row, remote_ref=rep.get('remote_ref')))}")
    if rep.get("drift"):
        lines.append(DRIFT_TAIL)
    for row in rep.get("advisory", []):
        lines.append(f"  advisory: {row['path']}  {_describe(dict(row, remote_ref=rep.get('remote_ref')))}")
    return "\n".join(lines)


# --------------------------------------------------------------------------------------------- --sync
def queue_rows(path):
    """[whole-PR review fix, 2026-10-21] (rows, problem) of queue.json ({"queue": [<entry>, ...]}) or
    second_pass_queue.json ({"entries": {<ticker>: <entry>}}, each row with its ticker): a missing file is ([], None);
    one that cannot be read, does not parse or has another shape is ([], "<why>") — the strict reading queue.py's own
    loaders apply (queue._pass2_load), never "no claims"."""
    if not os.path.exists(path):
        return [], None
    try:
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
    except (OSError, ValueError) as e:
        return [], f"unreadable ({type(e).__name__}: {str(e)[:120]})"
    second = os.path.basename(path) == "second_pass_queue.json"
    if not isinstance(d, dict):
        return [], "not a JSON object"
    if second:
        ents = d.get("entries")
        if not isinstance(ents, dict):
            return [], f"'entries' is {type(ents).__name__}, not an object" if "entries" in d else "no 'entries' key"
        bad = next((t for t, v in ents.items() if not isinstance(v, dict)), None)
        if bad is not None:
            return [], f"entry {bad!r} is not an object"
        return [dict(v, ticker=k) for k, v in ents.items()], None
    q = d.get("queue")
    if not isinstance(q, list):
        return [], f"'queue' is {type(q).__name__}, not a list" if "queue" in d else "no 'queue' key"
    if any(not isinstance(e, dict) for e in q):
        return [], "a queue entry is not an object"
    return q, None


def live_claims(path):
    """([(ticker, claimed_at)] of in_progress entries with a live lease, problem) — queue_rows' strict reading."""
    rows, problem = queue_rows(path)
    return _live(rows), problem


def _live(rows):
    cutoff = _ops.now_et() - datetime.timedelta(minutes=LEASE_MINUTES)
    live = []
    for e in rows:
        if not isinstance(e, dict) or e.get("status") != "in_progress":
            continue
        ts = _ops.parse_ts(e.get("claimed_at"))
        if ts is not None and ts >= cutoff:
            live.append((e.get("ticker"), e.get("claimed_at")))
    return live


def sync(base=None, repo=None, remote="origin", branch="main", fetch=True, attempts=3, pause=2.0):
    """(exit code, text) of --sync."""
    base = os.path.abspath(base or _ops.base_dir())
    repo = os.path.abspath(repo or base)
    if not _ops.same_dir(_ops.toplevel(repo), base):
        return 2, (f"preflight: SYNC REFUSED — {base} is not the work tree of {repo}; --sync checks files out in the "
                   "repo itself (run it in the sweep tree)")
    qpath = os.path.join(base, "_system", "queue.json")
    with locked(f"{qpath}.lock"):
        live = []
        for p in (qpath, os.path.join(base, "_system", "second_pass_queue.json")):
            got, problem = live_claims(p)
            if problem:   # [whole-PR review fix] the one safety check never passes on a state it cannot read
                return 5, (f"preflight: SYNC REFUSED — {os.path.basename(p)} is malformed or unreadable ({problem}), so "
                           "whether a run holds a live claim cannot be read; restore it from git, then sync")
            live += got
        if live:
            t, ts = live[0]
            return 5, f"preflight: SYNC REFUSED — {t} is being scored (claimed {ts}); sync after its run ends"
        rep = check(base=base, repo=repo, remote=remote, branch=branch, fetch=fetch, attempts=attempts, pause=pause)
        if rep["exit"] not in (0, 1):
            return rep["exit"], first_line(rep)
        paths = sync_paths(rep)
        old = (rep.get("engine_release") or {}).get("here")
        if not paths:
            return 0, first_line(rep) + "\npreflight: nothing to sync"
        rc, _, err = _ops.git(repo, "checkout", rep["origin_sha"], "--", *paths, timeout=600)
        if rc != 0:
            return 3, f"preflight: SYNC FAILED — git checkout {rep['remote_ref']} -- … ({(err or '').strip()[:300]})"
    lines = [f"preflight: SYNCED {len(paths)} file{'s' if len(paths) != 1 else ''} to {rep['remote_ref']} "
             f"{rep['origin_sha'][:7]} (ENGINE_RELEASE {old} -> {(rep.get('engine_release') or {}).get('origin')})"]
    lines += [f"  {p}" for p in paths]
    lines.append(SYNC_NEXT.format(old=old))
    return 0, "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="preflight.py", description="Engine drift guard (R5).")
    ap.add_argument("--repo")
    ap.add_argument("--remote", default="origin")
    ap.add_argument("--branch", default="main")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-fetch", action="store_true")
    ap.add_argument("--attempts", type=int, default=3)
    ap.add_argument("--pause", type=float, default=2.0)
    ap.add_argument("--list-drift", action="store_true")
    ap.add_argument("--sync", action="store_true")
    try:
        a = ap.parse_args(argv)
    except SystemExit as e:
        return 2 if e.code else 0
    if a.attempts < 1 or a.pause < 0 or (a.sync and a.list_drift):
        print("preflight: usage — --attempts >= 1, --pause >= 0, --sync and --list-drift exclude each other",
              file=sys.stderr)
        return 2
    kw = dict(base=_ops.base_dir(), repo=a.repo, remote=a.remote, branch=a.branch, fetch=not a.no_fetch,
              attempts=a.attempts, pause=a.pause)
    if a.sync:
        rc, text = sync(**kw)
        print(text)
        return rc
    rep = check(**kw)
    if a.list_drift:
        for path in sync_paths(rep):
            print(path)
        if rep["exit"] not in (0, 1):
            print(first_line(rep), file=sys.stderr)
        return rep["exit"]
    if a.json:
        print(json.dumps(rep, indent=1))
    else:
        print(text_report(rep))
    return rep["exit"]


if __name__ == "__main__":
    sys.exit(main())
