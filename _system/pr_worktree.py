#!/usr/bin/env python3
"""Per-company PR worktrees (engine 5.7, Andrew's ruling R5 of 2026-10-19 — sweep reliability; _system/PR_PROTOCOL.md).

The misses it stops: two PR agents shared one worktree; registry deltas were hand-"constructed" (PR #33, #38);
company PRs published a score made on a stale engine (MOH #37, ESTC #35); a review fix lived only in the worktree.
Every company PR is cut through this script: a per-ticker lease lock, a deterministic sparse worktree on a new branch
from origin/main, make_score.py re-run there at origin/main's code, check_quotes.py on a 5.7 run, a decision-field
comparison with the sweep tree's score, and staging limited to <T>/, the ticker's own registry entries and appended
ENGINE_BACKLOG.md lines.

Usage:
  pr_worktree.py acquire <T> --holder ID --kind pass1|rescore|pass2|review-fix|rebuild [--ttl-hours 3]
  pr_worktree.py acquire --bulk REPORT.json --holder ID [--ttl-hours 6]  # every rebuilt in-sync ticker of a report
  pr_worktree.py renew <T> --holder ID [--ttl-hours 3]
  pr_worktree.py prepare <T>|--bulk BRANCH [--holder ID] [--no-fetch]
  pr_worktree.py open <T>|--bulk BRANCH --body-file PATH [--holder ID] [--trailer LINE]...
  pr_worktree.py push <T> -m MSG [--holder ID] [--trailer LINE]...   # review rounds
  pr_worktree.py restack <T> [--holder ID] [--trailer LINE]...
  pr_worktree.py release <T> --holder ID [--force] [--remove-worktree]
  pr_worktree.py status [--json]
  pr_worktree.py reap [--json]
  pr_worktree.py discard <T> --force
  pr_worktree.py backlog-next [--no-fetch]

Paths: PR_ROOT = $STOCKS_PR_ROOT or <parent of the sweep tree>/stocks-pr (outside the repo); worktree <PR_ROOT>/<T>
(bulk: <PR_ROOT>/_bulk/<branch, / -> _>); lock <PR_ROOT>/.locks/<T>.lock.json, created with O_CREAT|O_EXCL. The
worktree is sparse: the top-level files, _system/ and <T>/ only.
Locks: a lease (expires_at), never a process lock — an agent's work spans many processes. A stale lock is reaped
race-safely (os.rename to <lock>.stale.<pid>.<ns>: one reaper wins); a stale lock whose worktree holds uncommitted
changes is reaped but acquire refuses until `discard <T> --force` or the changes are committed. release by another
holder refuses without --force. Time: $STOCKS_NOW (tests); gh: $STOCKS_GH (tests: a stub).
Stale engine release (lane default Q12 (b), 2026-10-21, pending Andrew; the one switch STALE_RELEASE_POLICY):
prepare rebuilds a folder whose dcf_numbers.json is from another release with make_score at origin/main's code and
publishes it with the alert gates the stale-release rule closes; the Mechanics block says the engine output predates
the release. "refuse" is design 05's (a): re-run the engine first (MOH #37 / ESTC #35).
Exit: 0 ok · 1 refused (a check) · 2 usage · 3 environment (git / gh missing, the sweep tree not a git checkout,
PR_ROOT unwritable, a fetch that failed) · 4 held by another holder.
An owner-directed acceptance re-score (AGENTS.md "What is in a PR") rides with its code PR and never goes through
this script.
"""
import argparse
import datetime
import hashlib
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import _ops  # noqa: E402
import preflight  # noqa: E402

# Lane default Q12 (b) (main agent, 2026-10-21, pending Andrew's ratification): "rebuild" = make_score at main's
# release, alert gates closed by the stale-release rule, the PR says the engine output predates it. "refuse" = 05 (a).
STALE_RELEASE_POLICY = "rebuild"
KINDS = ("pass1", "rescore", "pass2", "review-fix", "rebuild")
TITLE_PREFIX = {"pass1": "DCF pass 1", "rescore": "Re-score", "pass2": "Second pass", "rebuild": "Rebuild"}
DEFAULT_TTL_HOURS, BULK_TTL_HOURS = 3.0, 6.0
MAKE_SCORE_TIMEOUT = 3600   # make_score's own replays may take 600 s each (L5L6 rebase A3)
CHECK_QUOTES_TIMEOUT = 600
REGISTRY_REL = "_system/overrides_registry.json"
BACKLOG_REL = _ops.BACKLOG_REL
# Decision fields beyond make_score.SCORE_DECISION_KEYS (absent == absent): A4's override_impact.unblocks_tier, and the
# lanes merged after this one append theirs to SCORE_DECISION_KEYS (R7 ttm_rejection_reason / base_alternatives, L8
# share_classes) — listed here too so the comparison holds whichever lands first.
EXTRA_DECISION_PATHS = ("override_impact.unblocks_tier", "ttm_rejection_reason", "base_alternatives", "share_classes")
IPRD_DEFERRED_EVENT = "iprd_deferred_payment"
TICKER_RX = re.compile(r"^[A-Z0-9][A-Z0-9.\-]{0,11}$")
MECHANICS_HEADING = "## Mechanics"


class Stop(Exception):
    """A refusal with its exit code (1 refused, 2 usage, 3 environment, 4 held)."""

    def __init__(self, msg, code=1):
        super().__init__(msg)
        self.code = code


def refuse(msg):
    raise Stop(f"pr_worktree: {msg}", 1)


def env_fail(msg):
    raise Stop(f"pr_worktree: {msg}", 3)


# --------------------------------------------------------------------------------------------- paths and locks
def base():
    return os.path.abspath(_ops.base_dir())


def pr_root():
    return os.path.abspath(os.environ.get("STOCKS_PR_ROOT") or os.path.join(os.path.dirname(base()), "stocks-pr"))


def lock_dir():
    return os.path.join(pr_root(), ".locks")


def lock_path(t):
    return os.path.join(lock_dir(), f"{t}.lock.json")


def bulk_manifest(branch):
    return os.path.join(lock_dir(), "_bulk", branch.replace("/", "_") + ".json")


def wt_path(t):
    return os.path.join(pr_root(), t)


def bulk_wt_path(branch):
    return os.path.join(pr_root(), "_bulk", branch.replace("/", "_"))


def norm_ticker(t):
    t = (t or "").strip().upper()
    if not TICKER_RX.match(t):
        raise Stop(f"pr_worktree: {t!r} is not a ticker", 2)
    return t


def read_lock(t):
    return _ops.load_json(lock_path(t))


def write_lock(t, d):
    _ops.write_json_atomic(lock_path(t), d)


def is_live(lock, now):
    exp = _ops.parse_ts((lock or {}).get("expires_at"))
    return exp is not None and exp >= now


def held_msg(t, lock):
    a, e = _ops.parse_ts(lock.get("acquired_at")), _ops.parse_ts(lock.get("expires_at"))
    return (f"pr_worktree: {t} is held by {lock.get('holder')} (kind {lock.get('kind')}, acquired {_ops.et_hm(a, ref=a)}, "
            f"expires {_ops.et_hm(e, ref=a)}) — another agent is cutting this PR; do not use its worktree. Finish "
            "without touching it.")


def _log(msg):
    try:
        os.makedirs(lock_dir(), exist_ok=True)
        with open(os.path.join(lock_dir(), "reaped.log"), "a", encoding="utf-8") as f:
            f.write(f"{_ops.iso(_ops.now_et())} {msg}\n")
    except OSError:
        pass


def reap_lock(t, lock):
    """Race-safe removal of an expired lock: only one reaper's rename succeeds. True when this process reaped it."""
    p = lock_path(t)
    stale = f"{p}.stale.{os.getpid()}.{time.time_ns()}"
    try:
        os.rename(p, stale)
    except OSError:
        return False
    _log(f"reaped {t} lock held by {lock.get('holder')} (kind {lock.get('kind')}, expired {lock.get('expires_at')})")
    try:
        os.remove(stale)
    except OSError:
        pass
    return True


def create_lock(t, payload):
    """O_CREAT|O_EXCL: atomic on POSIX and NTFS. False when the file exists."""
    os.makedirs(lock_dir(), exist_ok=True)
    try:
        fd = os.open(lock_path(t), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        return False
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=1)
        f.write("\n")
    return True


def require_lock(t, holder=None):
    lock = read_lock(t)
    now = _ops.now_et()
    if not lock:
        refuse(f"{t} is not acquired — run `pr_worktree.py acquire {t} --holder <id> --kind <kind>` first")
    if holder and lock.get("holder") != holder:
        raise Stop(held_msg(t, lock), 4)
    if not is_live(lock, now):
        refuse(f"{t}'s lock expired at {lock.get('expires_at')} — `pr_worktree.py renew {t} --holder "
               f"{lock.get('holder')}` (or acquire again)")
    return lock


# --------------------------------------------------------------------------------------------- git helpers
def git_ok(repo, *args, timeout=300, what=None):
    rc, out, err = _ops.git(repo, *args, timeout=timeout)
    if rc != 0:
        env_fail(f"{what or 'git ' + ' '.join(str(a) for a in args[:3])} failed: "
                 f"{(err or out).strip().splitlines()[-1] if (err or out).strip() else 'exit ' + str(rc)}")
    return out


def porcelain(wt):
    rc, out, err = _ops.git(wt, "status", "--porcelain", "-uall", "--no-renames")
    if rc != 0:
        env_fail(f"git status in {wt} failed: {err.strip()}")
    paths = []
    for line in out.splitlines():
        if len(line) > 3:
            p = line[3:]
            if p.startswith('"'):
                try:
                    p = json.loads(p)
                except ValueError:
                    pass
            paths.append((line[:2], p))
    return paths


def is_dirty(wt):
    return bool(os.path.isdir(wt) and _ops.toplevel(wt) and porcelain(wt))


def repo_of_base():
    b = base()
    if not _ops.same_dir(_ops.toplevel(b), b):
        env_fail(f"the sweep tree {b} is not a git checkout (its top level) — company PRs are cut from it")
    return b


def fetch_main(repo, no_fetch=False):
    if not no_fetch:
        ok, used, last = _ops.fetch_ref(repo, "origin", "main")
        if not ok:
            env_fail(f"git fetch origin main failed {used} times ({last})")
    sha = _ops.rev(repo, "origin/main")
    if not sha:
        env_fail("no origin/main in the sweep tree")
    return sha


def remote_branch_exists(repo, branch):
    rc, out, _ = _ops.git(repo, "ls-remote", "--heads", "origin", f"refs/heads/{branch}", timeout=120)
    if rc != 0:
        env_fail(f"git ls-remote origin failed for {branch}")
    return bool(out.strip())


def local_branch_exists(repo, branch):
    return _ops.rev(repo, f"refs/heads/{branch}") is not None


def generation_date(t):
    q = _ops.load_json(os.path.join(base(), "_system", "queue.json"), {}) or {}
    for e in q.get("queue") or []:
        if isinstance(e, dict) and e.get("ticker") == t:
            d = _ops.parse_ts(e.get("claimed_at"))
            if d:
                return d.astimezone(_ops.ET).strftime("%Y%m%d")
    return _ops.now_et().strftime("%Y%m%d")


def choose_branch(repo, t):
    """dcf/<T> when neither origin nor the local repo has it; else dcf/<T>-<YYYYMMDD> (the ET date of the scoring
    generation's claim), then -2, -3, … (dcf/<T>/… is impossible: it collides with the ref dcf/<T>)."""
    def taken(b):
        return local_branch_exists(repo, b) or remote_branch_exists(repo, b)
    first = f"dcf/{t}"
    if not taken(first):
        return first
    stem = f"dcf/{t}-{generation_date(t)}"
    if not taken(stem):
        return stem
    for i in range(2, 100):
        b = f"{stem}-{i}"
        if not taken(b):
            return b
    refuse(f"no free branch name for {t} ({stem}-2 … -99 all exist)")


def sparse_patterns(tickers):
    return ["/*", "!/*/", "/_system/"] + [f"/{t}/" for t in tickers]


def unpushed(wt):
    """Commits on the worktree's branch that no remote branch holds (a worktree that is clean may still own them)."""
    rc, out, _ = _ops.git(wt, "rev-list", "--count", "HEAD", "--not", "--remotes=origin")
    try:
        return int(out.strip()) if rc == 0 else 0
    except ValueError:
        return 0


def make_worktree(repo, path, branch, start, tickers, new_branch=True):
    if os.path.exists(path):
        if _ops.same_dir(_ops.toplevel(path), path):
            if is_dirty(path):
                refuse(f"{path} holds uncommitted changes — commit them in that worktree or `pr_worktree.py discard "
                       f"{tickers[0]} --force`")
            if unpushed(path):
                refuse(f"{path} has commits that were never pushed — push them or `pr_worktree.py discard "
                       f"{tickers[0]} --force`")
            git_ok(repo, "worktree", "remove", path, what="git worktree remove")
        else:
            refuse(f"{path} exists and is not a worktree of {repo} — remove it, then acquire again")
    _ops.git(repo, "worktree", "prune")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if new_branch:
        git_ok(repo, "worktree", "add", "--no-checkout", "--no-track", "-b", branch, path, start, what="git worktree add")
    else:
        git_ok(repo, "worktree", "add", "--no-checkout", path, branch, what="git worktree add")
    git_ok(path, "sparse-checkout", "set", "--no-cone", *sparse_patterns(tickers), what="git sparse-checkout set")
    git_ok(path, "checkout", "--quiet", what="git checkout")


# --------------------------------------------------------------------------------------------- acquire / renew / release
def _new_lock(t, holder, kind, ttl, now, bulk=None):
    return {"ticker": t, "holder": holder, "kind": kind, "acquired_at": _ops.iso(now),
            "expires_at": _ops.iso(now + datetime.timedelta(hours=ttl)), "renewed_at": None,
            "host": socket.gethostname(), "pid": os.getpid(), "worktree": None, "branch": None, "base_sha": None,
            "bulk": bulk, "pr_number": None, "pr_url": None, "prepared": None}


def _take(t, holder, kind, ttl, now, bulk=None):
    """Create t's lock (reaping an expired one). Raises Stop(4) while another holder's lease is live, Stop(1) when
    the expired holder left uncommitted work in the worktree."""
    for _ in range(3):
        cur = read_lock(t)
        if cur:
            if is_live(cur, now):
                raise Stop(held_msg(t, cur), 4)
            reap_lock(t, cur)
            wt = cur.get("worktree")
            if wt and is_dirty(wt):
                refuse(f"{t}'s lock expired ({cur.get('holder')}, {cur.get('expires_at')}) and was reaped, but its "
                       f"worktree {wt} holds uncommitted changes — the expired holder's work is never thrown away: "
                       f"commit it there, or `pr_worktree.py discard {t} --force`, then acquire again")
        if create_lock(t, _new_lock(t, holder, kind, ttl, now, bulk)):
            return
    cur = read_lock(t) or {}
    raise Stop(held_msg(t, cur) if cur else f"pr_worktree: could not take {t}'s lock (a race) — try again", 4)


def _open_pr_for(repo, t):
    import pr_audit
    slug = _ops.repo_slug(repo)
    args = ["pr", "list", "--state", "open", "--limit", "200", "--json", "number,headRefName,title,url,state,createdAt"]
    if slug:
        args[2:2] = ["--repo", slug]
    rc, out, err = _ops.gh(*args)
    if rc != 0:
        env_fail(f"gh pr list failed ({(err or out).strip()[:200]})")
    try:
        prs = json.loads(out)
    except ValueError:
        env_fail("gh pr list printed no JSON")
    mine = [p for p in prs if pr_audit.pr_belongs(p, t) and str(p.get("headRefName", "")).startswith("dcf/")]
    return mine[0] if mine else None


def cmd_acquire(t, holder, kind, ttl):
    t = norm_ticker(t)
    if kind not in KINDS:
        raise Stop(f"pr_worktree: --kind must be one of {', '.join(KINDS)}", 2)
    repo = repo_of_base()
    now = _ops.now_et()
    path = wt_path(t)
    if not read_lock(t) and is_dirty(path):
        refuse(f"{path} holds uncommitted changes and no live lock — `pr_worktree.py discard {t} --force` first")
    _take(t, holder, kind, ttl, now)
    try:
        sha = fetch_main(repo)
        pr = None
        if kind == "review-fix":
            pr = _open_pr_for(repo, t)
            if not pr:
                refuse(f"no open PR for {t} — a review round needs one (cut it with --kind pass1|rescore|pass2)")
            branch = pr["headRefName"]
            git_ok(repo, "fetch", "--quiet", "--no-tags", "origin", f"+refs/heads/{branch}:refs/remotes/origin/{branch}",
                   what=f"git fetch origin {branch}")
            on = _ops.toplevel(path) and _ops.same_dir(_ops.toplevel(path), path)
            cur = None
            if on:
                rc, o, _ = _ops.git(path, "rev-parse", "--abbrev-ref", "HEAD")
                cur = o.strip()
            if not (on and cur == branch):
                if local_branch_exists(repo, branch):
                    make_worktree(repo, path, branch, None, [t], new_branch=False)
                else:
                    make_worktree(repo, path, branch, f"origin/{branch}", [t])
                    git_ok(path, "branch", "--set-upstream-to", f"origin/{branch}", what="git branch --set-upstream-to")
            rc, _, _ = _ops.git(path, "merge", "--ff-only", "--quiet", f"origin/{branch}")
        else:
            branch = choose_branch(repo, t)
            make_worktree(repo, path, branch, "origin/main", [t])
        lock = read_lock(t)
        lock.update(worktree=path, branch=branch, base_sha=sha,
                    pr_number=(pr or {}).get("number"), pr_url=(pr or {}).get("url"))
        write_lock(t, lock)
    except BaseException:
        try:
            os.remove(lock_path(t))
        except OSError:
            pass
        raise
    print(f"pr_worktree: {t} acquired by {holder} (kind {kind}) — worktree {path}, branch {branch}, origin/main "
          f"{sha[:7]}, expires {lock['expires_at']}")
    return 0


def cmd_acquire_bulk(report_path, holder, ttl):
    rep = _ops.load_json(report_path)
    if not isinstance(rep, dict) or rep.get("tool") != "rebuild_scores":
        raise Stop(f"pr_worktree: {report_path} is not a rebuild_scores report", 2)
    if rep.get("drift_allowed"):
        refuse(f"{report_path} was made with --allow-drift — a bulk PR needs a report made at origin/main's code")
    want_state = "rebuilt" if rep.get("mode") == "apply" else "changed"
    tickers = sorted(f["ticker"] for f in rep.get("folders") or []
                     if f.get("state") == want_state and f.get("main_sync") == "in_sync")
    if not tickers:
        refuse(f"{report_path} lists no {want_state} folder that is in sync with main")
    repo = repo_of_base()
    now = _ops.now_et()
    rel = rep.get("engine_release") or "?"
    branch = f"rebuild/{rel}-{now.strftime('%Y%m%d')}"
    i = 2
    while local_branch_exists(repo, branch) or remote_branch_exists(repo, branch):
        branch = f"rebuild/{rel}-{now.strftime('%Y%m%d')}-{i}"
        i += 1
    taken = []
    try:
        for t in tickers:
            _take(t, holder, "rebuild", ttl, now, bulk=branch)
            taken.append(t)
        sha = fetch_main(repo)
        path = bulk_wt_path(branch)
        make_worktree(repo, path, branch, "origin/main", tickers)
        for t in tickers:
            lock = read_lock(t)
            lock.update(worktree=path, branch=branch, base_sha=sha)
            write_lock(t, lock)
        _ops.write_json_atomic(bulk_manifest(branch), {"branch": branch, "holder": holder, "tickers": tickers,
                                                        "worktree": path, "base_sha": sha, "report": report_path,
                                                        "engine_release": rel, "prepared": None, "pr_number": None,
                                                        "pr_url": None, "acquired_at": _ops.iso(now)})
    except BaseException:
        for t in taken:   # all-or-nothing
            try:
                os.remove(lock_path(t))
            except OSError:
                pass
        raise
    print(f"pr_worktree: bulk {branch} acquired by {holder} — {len(tickers)} tickers, worktree {path}")
    return 0


def cmd_renew(t, holder, ttl):
    t = norm_ticker(t)
    lock = read_lock(t)
    if not lock:
        refuse(f"{t} is not acquired")
    if lock.get("holder") != holder:
        raise Stop(held_msg(t, lock), 4)
    now = _ops.now_et()
    lock.update(expires_at=_ops.iso(now + datetime.timedelta(hours=ttl)), renewed_at=_ops.iso(now))
    write_lock(t, lock)
    print(f"pr_worktree: {t} renewed until {lock['expires_at']}")
    return 0


def cmd_release(t, holder, force, remove_worktree):
    t = norm_ticker(t)
    lock = read_lock(t)
    if not lock:
        print(f"pr_worktree: {t} holds no lock")
        return 0
    if lock.get("holder") != holder and not force:
        refuse(f"{t} is held by {lock.get('holder')}, not {holder} — release refuses without --force")
    wt = lock.get("worktree")
    if remove_worktree and wt and os.path.isdir(wt) and not lock.get("bulk"):
        if is_dirty(wt):
            refuse(f"{wt} holds uncommitted changes — --remove-worktree refuses (commit them or discard --force)")
        git_ok(repo_of_base(), "worktree", "remove", wt, what="git worktree remove")
    os.remove(lock_path(t))
    print(f"pr_worktree: {t} released" + (f" (worktree {wt} stays until its PR is merged or closed; reap removes it)"
                                         if wt and os.path.isdir(wt) else ""))
    return 0


# --------------------------------------------------------------------------------------------- prepare
def _score_keys_and_registry_problems(wt, registries):
    """(SCORE_DECISION_KEYS, {label: [problems]}) read through the WORKTREE's make_score (origin/main's code)."""
    code = ("import json, sys\n"
            "sys.path.insert(0, sys.argv[1])\n"
            "import make_score as M\n"
            "out = {'keys': list(M.SCORE_DECISION_KEYS), 'problems': {}}\n"
            "for label, p in json.loads(sys.argv[2]).items():\n"
            "    probs = []\n"
            "    try:\n"
            "        d = json.load(open(p, encoding='utf-8'))\n"
            "    except FileNotFoundError:\n"
            "        d = {'entries': []}\n"
            "    except ValueError as e:\n"
            "        probs.append('unreadable: %s' % e); d = None\n"
            "    if d is not None:\n"
            "        ents = d.get('entries') if isinstance(d, dict) else None\n"
            "        if not isinstance(ents, list):\n"
            "            probs.append('no entries list')\n"
            "        else:\n"
            "            for i, e in enumerate(ents):\n"
            "                bad = M.registry_entry_problem(e) if isinstance(e, dict) else ('entry', 'is not an object')\n"
            "                if bad is not None:\n"
            "                    probs.append('entry %d (ticker %r, event %r): field %r %s' % (i, e.get('ticker') if isinstance(e, dict) else None, e.get('event') if isinstance(e, dict) else None, bad[0], bad[1]))\n"
            "    out['problems'][label] = probs\n"
            "print(json.dumps(out))\n")
    env = dict(os.environ, STOCKS_BASE=wt, PYTHONIOENCODING="utf-8",
               MAKE_SCORE_REGISTRY=os.path.join(wt, *REGISTRY_REL.split("/")))
    r = subprocess.run([sys.executable, "-c", code, os.path.join(wt, "_system"), json.dumps(registries)],
                       capture_output=True, text=True, encoding="utf-8", errors="replace", env=env, timeout=300)
    if r.returncode != 0:
        env_fail(f"reading make_score's decision fields in {wt} failed: {(r.stderr or '').strip()[-300:]}")
    d = json.loads(r.stdout.strip().splitlines()[-1])
    return tuple(d["keys"]), d["problems"]


def get_path(d, path):
    cur = d
    for k in path.split("."):
        if not isinstance(cur, dict) or k not in cur:
            return "<absent>"
        cur = cur[k]
    return cur


def _short(v):
    s = json.dumps(v, sort_keys=True, default=str) if not isinstance(v, str) else v
    return s if len(s) <= 40 else s[:37] + "…"


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _ignored(wt, rels):
    if not rels:
        return set()
    rc, out, _ = _ops.git(wt, "check-ignore", "--stdin", input="\n".join(rels) + "\n")
    return set(x.strip() for x in out.splitlines() if x.strip()) if rc in (0, 1) else set()


def copy_folder(wt, t, origin_sha):
    """Step 3: the sweep folder's committed files -> the worktree (refusing a record file main has and the sweep
    folder lost). Returns the copied repo-relative paths."""
    src = os.path.join(base(), t)
    if not os.path.isdir(src):
        refuse(f"the sweep tree has no {t}/ folder")
    rels = []
    for root, dirs, files in os.walk(src):
        dirs[:] = [d for d in dirs if d not in ("__pycache__",)]
        for name in files:
            full = os.path.join(root, name)
            if os.path.isfile(full) and not os.path.islink(full):
                rels.append(os.path.relpath(full, base()).replace(os.sep, "/"))
    ign = _ignored(wt, rels)
    keep = sorted(r for r in rels if r not in ign)
    on_main = _ops.tree_blobs(wt, origin_sha, prefix=t)
    lost = sorted(p for p in on_main if p not in set(keep))
    if lost:
        refuse(f"{lost[0]} is on main but not in the sweep folder — a company PR does not delete record files; "
               "restore it or ask the main agent")
    dst_root = os.path.join(wt, t)
    for r in keep:
        dst = os.path.join(wt, *r.split("/"))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(os.path.join(base(), *r.split("/")), dst)
    # files an earlier prepare copied that the sweep folder no longer holds (never on main: checked above)
    keep_set, extra = set(keep), []
    for root, dirs, files in os.walk(dst_root):
        for name in files:
            r = os.path.relpath(os.path.join(root, name), wt).replace(os.sep, "/")
            if r not in keep_set:
                extra.append(r)
    ign_extra = _ignored(wt, extra)
    for r in extra:
        if r not in ign_extra:
            os.remove(os.path.join(wt, *r.split("/")))
    return keep


def _ms_env(wt):
    return dict(os.environ, STOCKS_BASE=wt, PYTHONIOENCODING="utf-8",
                MAKE_SCORE_REGISTRY=os.path.join(wt, *REGISTRY_REL.split("/")))


def _last_line(text, prefer="REFUSED"):
    lines = [x.strip() for x in (text or "").splitlines() if x.strip()]
    hit = [x for x in lines if prefer in x]
    return (hit[0] if hit else lines[-1]) if lines else ""


def _facts():
    import facts
    return facts


def prepare_one(wt, t, kind, origin_sha, keys):
    """Steps 3-7 for one ticker; returns its record for the lock's `prepared`."""
    files = copy_folder(wt, t, origin_sha)
    folder = os.path.join(wt, t)
    n = _ops.load_json(os.path.join(folder, "dcf_numbers.json"))
    if not isinstance(n, dict):
        refuse(f"{t}/dcf_numbers.json is missing or unreadable in the sweep folder")
    main_rel = _ops.local_engine_release(wt)
    run_rel = n.get("engine_release")
    stale = None
    if run_rel != main_rel:
        if kind != "rebuild" and STALE_RELEASE_POLICY == "refuse":
            refuse(f"{t}/dcf_numbers.json is engine release {run_rel}; origin/main is {main_rel} — re-run the engine on "
                   "a synced sweep tree (preflight exit 0) and make_score, then prepare again. A company PR never "
                   "publishes a stale-release score (MOH #37, ESTC #35).")
        stale = {"run": run_rel, "main": main_rel}
    r = subprocess.run([sys.executable, os.path.join(wt, "_system", "make_score.py"), t], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", env=_ms_env(wt), timeout=MAKE_SCORE_TIMEOUT)
    if r.returncode != 0:
        refuse(f"make_score.py refused {t} at origin/main {origin_sha[:7]}: {_last_line(r.stderr or r.stdout)}")
    if _facts().is_rulings_run(n):
        q = subprocess.run([sys.executable, os.path.join(wt, "_system", "check_quotes.py"), t], capture_output=True,
                           text=True, encoding="utf-8", errors="replace", env=_ms_env(wt), timeout=CHECK_QUOTES_TIMEOUT)
        if q.returncode != 0:
            first = " / ".join([x for x in (q.stdout + "\n" + q.stderr).splitlines() if x.strip()][:3])
            refuse(f"check_quotes.py refused {t}/analysis.md: {first} — fix analysis.md (or facts.json) in the sweep "
                   "tree, never in the worktree, then prepare again.")
        cq = "pass"
    else:
        cq = "n/a (pre-5.7 run)"
    new = _ops.load_json(os.path.join(folder, "score.json")) or {}
    old = _ops.load_json(os.path.join(base(), t, "score.json")) or {}
    paths = list(dict.fromkeys(list(keys) + list(EXTRA_DECISION_PATHS)))
    diffs = [(p, get_path(old, p), get_path(new, p)) for p in paths if get_path(old, p) != get_path(new, p)]
    if diffs:
        shown = "; ".join(f"{p} {_short(a)} → {_short(b)}" for p, a, b in diffs[:4])
        refuse(f"the score rebuilt at origin/main {origin_sha[:7]} differs from the sweep tree's ({shown}) — the sweep "
               "tree scored on other code. Run preflight.py, re-run make_score.py on the sweep tree, then prepare "
               "again.")
    other = sorted(k for k in set(old) | set(new) if old.get(k, "<absent>") != new.get(k, "<absent>"))
    import build_site
    built, mm = build_site.score_from_run(new, n)
    return {"ticker": t, "engine_release_run": run_rel, "stale_release": stale, "check_quotes": cq,
            "other_changed_fields": other, "dcf_content_hash": new.get("dcf_content_hash"),
            "score_from_run": bool(built), "score_mismatch": (mm[0] if mm else None),
            "tier_final": new.get("tier_final"), "tier_by_numbers": new.get("tier_by_numbers")}


def _entries(reg):
    return (reg or {}).get("entries") if isinstance((reg or {}).get("entries"), list) else []


def registry_check(wt, tickers, origin_sha, problems):
    """Step 8: both registries readable by make_score; every other ticker's entries identical and in the same
    relative order; each ticker's acquired-IPR&D deferred-payment record equal to the sweep tree's."""
    for label in ("origin", "worktree"):
        if problems.get(label):
            refuse(f"{label} overrides_registry.json would be refused by make_score ({problems[label][0]}) — a PR never "
                   "pushes a registry main's make_score refuses; restack, or ask the main agent")
    main_text = _ops.show(wt, origin_sha, REGISTRY_REL)
    main_reg = json.loads(main_text) if main_text else {"entries": []}
    wt_reg = _ops.load_json(os.path.join(wt, *REGISTRY_REL.split("/"))) or {"entries": []}
    ts = set(tickers)
    a = [e for e in _entries(main_reg) if e.get("ticker") not in ts]
    b = [e for e in _entries(wt_reg) if e.get("ticker") not in ts]
    if a != b:
        changed = sorted({e.get("ticker") for e in a if e not in b} | {e.get("ticker") for e in b if e not in a}) or \
            ["(order)"]
        refuse(f"the worktree's registry changes entries of other tickers: {', '.join(str(x) for x in changed[:8])} — "
               "restack")
    sweep_reg = _ops.load_json(os.path.join(base(), *REGISTRY_REL.split("/"))) or {"entries": []}

    def deferred(reg, t):
        return sorted((json.dumps({k: v for k, v in e.items() if k != "date"}, sort_keys=True)
                       for e in _entries(reg) if e.get("ticker") == t and e.get("event") == IPRD_DEFERRED_EVENT))
    counts = {}
    for t in tickers:
        dw, ds = deferred(wt_reg, t), deferred(sweep_reg, t)
        if dw != ds:
            deal = next((json.loads(x).get("deal") for x in (set(dw) ^ set(ds))), "?")
            refuse(f"{t}'s acquired-IPR&D deferred-payment record differs from the sweep tree's (deal {deal}) — the "
                   "lifetime record must reach main unchanged; restack, or ask the main agent")
        counts[t] = {"before": sum(1 for e in _entries(main_reg) if e.get("ticker") == t),
                     "after": sum(1 for e in _entries(wt_reg) if e.get("ticker") == t)}
    return counts


def _staged_sha(wt, rels):
    out = {}
    for r in rels:
        p = os.path.join(wt, *r.split("/"))
        if os.path.isfile(p):
            out[r] = _sha256(p)
    return out


def _check_code_is_main(wt, origin_sha):
    """The worktree must run origin/main's code (main may have moved since acquire)."""
    rep = preflight.check(base=wt, repo=wt, fetch=False)
    if rep["exit"] == 1:
        refuse(f"the PR worktree runs older code than origin/main {origin_sha[:7]} "
               f"({', '.join(r['path'] for r in rep['drift'][:3])}) — run `pr_worktree.py restack <T>`")
    if rep["exit"] != 0:
        env_fail(preflight.first_line(rep))


def do_prepare(tickers, kind, wt, no_fetch=False):
    rep = preflight.check(base=base(), fetch=not no_fetch)
    if rep["exit"] == 1:
        refuse(f"{preflight.first_line(rep)} — the sweep tree must run origin/main's method before a PR is cut")
    if rep["exit"] != 0:
        env_fail(preflight.first_line(rep))
    origin_sha = rep["origin_sha"]
    _check_code_is_main(wt, origin_sha)
    tmp = tempfile.mkdtemp(prefix="pr_worktree_reg_")
    try:
        mtxt = _ops.show(wt, origin_sha, REGISTRY_REL)
        mpath = os.path.join(tmp, "origin_registry.json")
        with open(mpath, "w", encoding="utf-8") as f:
            f.write(mtxt if mtxt is not None else '{"entries": []}')
        keys, _ = _score_keys_and_registry_problems(wt, {})
        per = [prepare_one(wt, t, kind, origin_sha, keys) for t in tickers]
        _, problems = _score_keys_and_registry_problems(
            wt, {"origin": mpath, "worktree": os.path.join(wt, *REGISTRY_REL.split("/"))})
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    counts = registry_check(wt, tickers, origin_sha, problems)
    staged = [p for _, p in porcelain(wt)]
    main_rel = _ops.local_engine_release(wt)
    return {"at": _ops.iso(_ops.now_et()), "origin_sha": origin_sha, "engine_release": main_rel, "make_score_rc": 0,
            "tickers": per, "check_quotes": per[0]["check_quotes"] if len(per) == 1 else
            sorted({p["check_quotes"] for p in per}), "registry_entries": counts if len(tickers) > 1 else counts[tickers[0]],
            "files": sorted(staged), "files_sha256": _staged_sha(wt, staged)}


def cmd_prepare(t=None, bulk=None, holder=None, no_fetch=False, quiet=False):
    if bulk:
        man = _ops.load_json(bulk_manifest(bulk))
        if not man:
            refuse(f"no bulk set {bulk} — acquire --bulk first")
        for x in man["tickers"]:
            require_lock(x, holder or man.get("holder"))
        prepared = do_prepare(man["tickers"], "rebuild", man["worktree"], no_fetch)
        man["prepared"] = prepared
        _ops.write_json_atomic(bulk_manifest(bulk), man)
        print(f"pr_worktree: bulk {bulk} prepared at origin/main {prepared['origin_sha'][:7]} — {len(man['tickers'])} "
              f"folders, {len(prepared['files'])} files")
        return 0
    t = norm_ticker(t)
    lock = require_lock(t, holder)
    if lock.get("bulk"):
        refuse(f"{t} is part of bulk set {lock['bulk']} — prepare --bulk {lock['bulk']}")
    prepared = do_prepare([t], lock.get("kind"), lock["worktree"], no_fetch)
    lock = read_lock(t)
    lock["prepared"] = prepared
    write_lock(t, lock)
    one = prepared["tickers"][0]
    if not quiet:
        print(f"pr_worktree: {t} prepared at origin/main {prepared['origin_sha'][:7]} (engine {prepared['engine_release']}"
              f"; run {one['engine_release_run']}) — tier {one['tier_final']} (numbers {one['tier_by_numbers']}), "
              f"check_quotes {one['check_quotes']}, registry {prepared['registry_entries']['before']} → "
              f"{prepared['registry_entries']['after']} entries, {len(prepared['files'])} files")
        if one["stale_release"]:
            print(f"  engine output is release {one['stale_release']['run']}, predating {one['stale_release']['main']}: "
                  "rebuilt by make_score, alert gates closed by the stale-release rule (lane default Q12 (b))")
        if one["other_changed_fields"]:
            print(f"  fields make_score re-derived (not decisions): {', '.join(one['other_changed_fields'])}")
    return 0


# --------------------------------------------------------------------------------------------- title, body, staging
def _pct(x):
    try:
        return f"{float(x) * 100:.2f}%"
    except (TypeError, ValueError):
        return None


def title_for(kind, t, s, j=None):
    name = s.get("name") or (j or {}).get("name") or t
    tf, tb, irr = s.get("tier_final"), s.get("tier_by_numbers"), _pct(s.get("implied_irr"))
    prefix = TITLE_PREFIX.get(kind, "DCF pass 1")
    if tf == "F" and irr is None:
        tier = "Tier F (no cash generation)"
    else:
        tier = f"Tier {tf}"
        if tb and tb != tf:
            tier += f" ({tb} by numbers{', ' + irr if irr else ''})"
        if irr:
            tier += f", weighted IRR {irr}"
    return f"{prefix}: {t} — {name} — {tier}"


def mechanics(prepared, tickers, wt):
    rows = prepared["tickers"]
    lines = [MECHANICS_HEADING, "(generated by pr_worktree.py — do not edit)",
             f"- Score rebuilt by make_score.py at origin/main {prepared['origin_sha'][:12]}, engine release "
             f"{prepared['engine_release']}"]
    if len(rows) == 1:
        r = rows[0]
        s = r["stale_release"]
        lines.append(f"- dcf_numbers.json engine release: {r['engine_release_run']}"
                     + (f" — the engine output predates release {s['main']}: rebuilt by make_score at {s['main']} (the "
                        "misfit notch applies mechanically), alert gates closed by the stale-release rule; no engine "
                        "re-run (lane default Q12 (b), 2026-10-21, pending Andrew)" if s else ""))
        lines.append(f"- score.dcf_content_hash: {(r['dcf_content_hash'] or 'none')[:12]} · score built from this run: "
                     + ("yes" if r["score_from_run"] else f"no — {r['score_mismatch']}"))
        lines.append(f"- check_quotes.py: {r['check_quotes']}")
        reg = prepared["registry_entries"]
        lines.append(f"- Registry: {tickers[0]} entries {reg['before']} → {reg['after']}; every other ticker's entries "
                     "unchanged")
        lines.append("- Fields make_score re-derived (not decisions): " + (", ".join(r["other_changed_fields"]) or "none"))
    else:
        stale = sorted({r["engine_release_run"] or "none" for r in rows})
        lines.append(f"- Folders: {len(rows)} ({', '.join(r['ticker'] for r in rows)})")
        lines.append(f"- dcf_numbers.json engine releases: {', '.join(stale)} (alert gates closed by the stale-release "
                     "rule where they predate the release)")
        lines.append("- score built from its run: " + ("every folder" if all(r["score_from_run"] for r in rows) else
                                                       ", ".join(r["ticker"] for r in rows if not r["score_from_run"])
                                                       + " NOT"))
        lines.append("- Registry: only these tickers' entries change")
    lines.append("- Files: " + ", ".join(prepared["files"]))
    return "\n".join(lines) + "\n"


def allowed_path(p, tickers):
    return p in (REGISTRY_REL, BACKLOG_REL) or any(p.startswith(f"{t}/") for t in tickers)


def check_backlog_append(wt, origin_sha):
    """ENGINE_BACKLOG.md is append-only in a data PR: no removed or edited line, every added line after main's last
    line, new ids absent on main, every new entry parses, no `#<this>` placeholder."""
    p = os.path.join(wt, *BACKLOG_REL.split("/"))
    main_text = _ops.show(wt, origin_sha, BACKLOG_REL) or ""
    if not os.path.isfile(p):
        if main_text:
            refuse(f"{BACKLOG_REL} is append-only in a data PR: the worktree deletes it")
        return []
    with open(p, encoding="utf-8") as f:
        text = f.read().replace("\r\n", "\n")
    main_norm = main_text.replace("\r\n", "\n")
    if text == main_norm:
        return []
    if not text.startswith(main_norm):
        old, new = main_norm.splitlines(), text.splitlines()
        edited = sum(1 for i, line in enumerate(old) if i >= len(new) or new[i] != line)
        refuse(f"{BACKLOG_REL} is append-only in a data PR: the diff edits or removes {edited} existing line"
               f"{'s' if edited != 1 else ''} — only lines after main's last line may be added")
    if main_norm and not main_norm.endswith("\n"):
        refuse(f"{BACKLOG_REL} on main does not end with a newline — ask the main agent (an append would edit its last line)")
    added = text[len(main_norm):]
    if "#<this>" in added:
        refuse(f"{BACKLOG_REL}: a data PR never writes the `fixed in PR #<this>` placeholder")
    main_ids = _ops.backlog_ids(main_norm)
    new_entries, _ = _ops.parse_backlog(added)
    for e in new_entries:
        if not e["seen_again"] and e["id"] in main_ids:
            refuse(f"{BACKLOG_REL}: EB-{e['id']:03d} is already used on main — `pr_worktree.py backlog-next` names the "
                   "next free id (restack renumbers)")
    _, problems = _ops.parse_backlog(text)
    if problems:
        refuse(f"{BACKLOG_REL}: {problems[0]}")
    return [f"EB-{e['id']:03d}{' seen again' if e['seen_again'] else ''}" for e in new_entries]


def stage(wt, tickers, prepared, origin_sha):
    changes = porcelain(wt)
    bad = sorted({p for _, p in changes if not allowed_path(p, tickers)})
    if bad:
        refuse(f"refusing to commit — the worktree changes paths a company PR may not carry: {', '.join(bad[:6])}. A "
               "company PR carries <T>/, _system/overrides_registry.json (<T>'s entries only) and appended lines in "
               "_system/ENGINE_BACKLOG.md.")
    deleted = sorted(p for st, p in changes if "D" in st and p != BACKLOG_REL)
    if deleted:
        refuse(f"refusing to commit — the worktree deletes {deleted[0]}; a company PR does not delete record files")
    # every file prepare copied or make_score wrote must be as prepare left it (ENGINE_BACKLOG.md is the one file a
    # PR agent edits in the worktree: its append-only rule is checked below instead)
    was = {p: h for p, h in (prepared.get("files_sha256") or {}).items() if p != BACKLOG_REL}
    now_sha = _staged_sha(wt, sorted(({p for _, p in changes} | set(was)) - {BACKLOG_REL}))
    moved = sorted(p for p in set(now_sha) | set(was) if now_sha.get(p) != was.get(p))
    if moved:
        refuse(f"the worktree changed since prepare ({', '.join(moved[:4])}) — fix the sweep tree, never the worktree, "
               "then prepare again")
    new_ids = check_backlog_append(wt, origin_sha)
    paths = [f"{t}/" for t in tickers] + [REGISTRY_REL] + ([BACKLOG_REL] if any(p == BACKLOG_REL for _, p in changes) else [])
    git_ok(wt, "add", "--", *paths, what="git add")
    return new_ids


def trailers(extra):
    out = list(extra or [])
    env = os.environ.get("STOCKS_COMMIT_TRAILER")
    if env and env not in out:
        out.append(env)
    return out


def commit(wt, subject, body, extra_trailers):
    msg = subject + "\n\n" + body.rstrip() + "\n"
    tr = trailers(extra_trailers)
    if tr:
        msg += "\n" + "\n".join(tr) + "\n"
    fd, tmp = tempfile.mkstemp(prefix="pr_worktree_msg_", suffix=".txt")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(msg)
    try:
        rc, out, err = _ops.git(wt, "commit", "--quiet", "-F", tmp)
        if rc != 0:
            env_fail(f"git commit failed: {(err or out).strip()[-300:]}")
    finally:
        os.remove(tmp)


def _context(t=None, bulk=None, holder=None):
    """(lock-like record, tickers, worktree, kind, writer) for a single ticker or a bulk set."""
    if bulk:
        man = _ops.load_json(bulk_manifest(bulk))
        if not man:
            refuse(f"no bulk set {bulk}")
        for x in man["tickers"]:
            require_lock(x, holder or man.get("holder"))

        def save(d):
            _ops.write_json_atomic(bulk_manifest(bulk), d)
        return man, man["tickers"], man["worktree"], "rebuild", save
    t = norm_ticker(t)
    lock = require_lock(t, holder)
    if lock.get("bulk"):
        refuse(f"{t} is part of bulk set {lock['bulk']} — use --bulk {lock['bulk']}")
    return lock, [t], lock["worktree"], lock.get("kind"), (lambda d: write_lock(t, d))


def cmd_open(t, bulk, body_file, holder, extra_trailers):
    rec, tickers, wt, kind, save = _context(t, bulk, holder)
    if not rec.get("prepared"):
        refuse("not prepared — run `pr_worktree.py prepare` first")
    if rec.get("pr_number"):
        refuse(f"PR #{rec['pr_number']} is already open for this worktree — review rounds use `push`")
    try:
        with open(body_file, encoding="utf-8") as f:
            body = f.read()
    except OSError as e:
        raise Stop(f"pr_worktree: cannot read --body-file {body_file} ({e})", 2)
    prepared = rec["prepared"]
    stage(wt, tickers, prepared, prepared["origin_sha"])
    if bulk:
        title = f"Rebuild: make_score at release {prepared['engine_release']} over {len(tickers)} folders"
    else:
        s = _ops.load_json(os.path.join(wt, tickers[0], "score.json")) or {}
        j = _ops.load_json(os.path.join(wt, tickers[0], "judgment.json")) or {}
        title = title_for(kind, tickers[0], s, j)
    mech = mechanics(prepared, tickers, wt)
    rc, _, _ = _ops.git(wt, "diff", "--cached", "--quiet")
    head = _ops.rev(wt, "HEAD")
    if rc != 0:
        commit(wt, title, mech, extra_trailers)
    elif head == rec.get("base_sha"):
        refuse("nothing to commit — the prepared worktree equals origin/main (did prepare copy the folder?)")
    # else: an earlier open committed (and maybe pushed) but gh failed — push and open the PR now
    branch = rec["branch"]
    git_ok(wt, "push", "--quiet", "-u", "origin", branch, what=f"git push origin {branch}")
    full = body.rstrip() + "\n\n" + mech
    fd, tmp = tempfile.mkstemp(prefix="pr_worktree_body_", suffix=".md")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(full)
    try:
        slug = _ops.repo_slug(wt)
        args = ["pr", "create"] + (["--repo", slug] if slug else []) + ["--base", "main", "--head", branch, "--title",
                                                                        title, "--body-file", tmp]
        rc, out, err = _ops.gh(*args)
    finally:
        os.remove(tmp)
    if rc != 0:
        env_fail(f"gh pr create failed ({(err or out).strip()[:300]}) — the branch {branch} is pushed; open the PR "
                 "with gh and record nothing by hand")
    m = re.search(r"https?://\S+/pull/(\d+)", out)
    rec = dict(rec, pr_number=int(m.group(1)) if m else None, pr_url=m.group(0) if m else out.strip())
    save(rec)
    print(rec["pr_url"])
    return 0


def cmd_push(t, msg, holder, extra_trailers):
    rec, tickers, wt, kind, save = _context(t, None, holder)
    if not rec.get("prepared"):
        refuse("not prepared — run `pr_worktree.py prepare` again after the sweep-tree fix")
    prepared = rec["prepared"]
    stage(wt, tickers, prepared, prepared["origin_sha"])
    rc, out, _ = _ops.git(wt, "diff", "--cached", "--quiet")
    if rc == 0:
        refuse("nothing to push — the prepared worktree equals the branch (did the sweep-tree fix and prepare run?)")
    commit(wt, msg, mechanics(prepared, tickers, wt), extra_trailers)
    git_ok(wt, "push", "--quiet", "origin", rec["branch"], what=f"git push origin {rec['branch']}")
    print(f"pr_worktree: pushed {rec['branch']}" + (f" (PR #{rec['pr_number']})" if rec.get("pr_number") else ""))
    return 0


# --------------------------------------------------------------------------------------------- restack
def _appended_block(old_text, cur_text):
    old_n, cur = (old_text or "").replace("\r\n", "\n"), (cur_text or "").replace("\r\n", "\n")
    return cur[len(old_n):] if cur.startswith(old_n) else None


def renumber_block(block, taken):
    """Renumber the block's new EB ids that `taken` (main's ids) already uses to the next free ids, rewriting the
    block's own 'seen again' headers that point at a renumbered id. Returns (block, {old: new})."""
    entries, _ = _ops.parse_backlog(block)
    nxt = max(taken | {e["id"] for e in entries} | {0}) + 1
    mapping = {}
    for e in entries:
        if not e["seen_again"] and e["id"] in taken and e["id"] not in mapping:
            mapping[e["id"]] = nxt
            nxt += 1
    if not mapping:
        return block, {}

    def sub(m):
        old = int(m.group(1))
        return f"### EB-{mapping[old]:03d}{m.group(2) or ''} — " if old in mapping else m.group(0)
    out = re.sub(r"^### EB-(\d{3,})( seen again)? — ", sub, block, flags=re.M)
    return out, mapping


def cmd_restack(t, holder, extra_trailers):
    rec, tickers, wt, kind, save = _context(t, None, holder)
    repo = repo_of_base()
    old_base = rec.get("base_sha")
    sha = fetch_main(repo)
    branch = rec["branch"]
    bl = os.path.join(wt, *BACKLOG_REL.split("/"))
    cur_text = open(bl, encoding="utf-8").read() if os.path.isfile(bl) else ""
    block = _appended_block(_ops.show(wt, old_base, BACKLOG_REL) if old_base else "", cur_text) or ""
    rc, remote_sha, _ = _ops.git(wt, "rev-parse", "--verify", "--quiet", f"refs/remotes/origin/{branch}")
    git_ok(wt, "reset", "--quiet", "--hard", sha, what="git reset --hard origin/main")
    mapping = {}
    if block.strip():
        main_text = _ops.show(wt, sha, BACKLOG_REL) or ""
        block, mapping = renumber_block(block, _ops.backlog_ids(main_text))
        with open(bl, "w", encoding="utf-8", newline="\n") as f:
            f.write(main_text.replace("\r\n", "\n") + block)
    prepared = do_prepare(tickers, kind, wt)
    rec = dict(rec, base_sha=sha, prepared=prepared)
    save(rec)
    stage(wt, tickers, prepared, prepared["origin_sha"])
    s = _ops.load_json(os.path.join(wt, tickers[0], "score.json")) or {}
    commit(wt, title_for(kind, tickers[0], s), mechanics(prepared, tickers, wt) + f"\nRestacked onto origin/main "
           f"{sha[:12]}.\n", extra_trailers)
    lease = f"--force-with-lease={branch}:{remote_sha.strip()}" if rc == 0 and remote_sha.strip() else "--force-with-lease"
    git_ok(wt, "push", "--quiet", lease, "origin", branch, what=f"git push --force-with-lease origin {branch}")
    print(f"pr_worktree: {tickers[0]} restacked onto origin/main {sha[:7]} and pushed"
          + ("; backlog ids renumbered " + ", ".join(f"EB-{a:03d} → EB-{b:03d}" for a, b in mapping.items())
             if mapping else ""))
    return 0


# --------------------------------------------------------------------------------------------- status / reap / discard
def _locks():
    out = []
    try:
        names = os.listdir(lock_dir())
    except OSError:
        return out
    for n in sorted(names):
        if n.endswith(".lock.json"):
            d = _ops.load_json(os.path.join(lock_dir(), n))
            if isinstance(d, dict):
                out.append(d)
    return out


def _worktrees():
    root = pr_root()
    out = []
    for parent in (root, os.path.join(root, "_bulk")):
        try:
            names = os.listdir(parent)
        except OSError:
            continue
        for n in sorted(names):
            p = os.path.join(parent, n)
            if n.startswith((".", "_")) and parent == root:
                continue
            if os.path.isdir(p):
                out.append(p)
    return out


def cmd_status(as_json):
    now = _ops.now_et()
    locks = [dict(lk, live=is_live(lk, now)) for lk in _locks()]
    wts = []
    for p in _worktrees():
        top = _ops.toplevel(p)
        br = None
        if top and _ops.same_dir(top, p):
            rc, o, _ = _ops.git(p, "rev-parse", "--abbrev-ref", "HEAD")
            br = o.strip()
        wts.append({"path": p, "branch": br, "dirty": is_dirty(p) if br else None})
    if as_json:
        print(json.dumps({"pr_root": pr_root(), "locks": locks, "worktrees": wts}, indent=1))
        return 0
    print(f"pr_worktree: PR_ROOT {pr_root()} — {sum(1 for x in locks if x['live'])} live lock(s), {len(wts)} worktree(s)")
    for lk in locks:
        print(f"  {lk.get('ticker'):<6} {('live' if lk['live'] else 'EXPIRED'):<7} {lk.get('holder')} kind "
              f"{lk.get('kind')} expires {lk.get('expires_at')} branch {lk.get('branch')}"
              + (f" PR #{lk['pr_number']}" if lk.get("pr_number") else "")
              + (" prepared" if lk.get("prepared") else ""))
    for w in wts:
        print(f"  worktree {w['path']} on {w['branch']}{' (dirty)' if w['dirty'] else ''}")
    return 0


def cmd_reap(as_json):
    now = _ops.now_et()
    repo = repo_of_base()
    reaped, removed, kept = [], [], []
    for lk in _locks():
        if not is_live(lk, now) and reap_lock(lk.get("ticker"), lk):
            reaped.append(lk.get("ticker"))
    live_wts = {os.path.normcase(os.path.abspath(lk.get("worktree") or "")) for lk in _locks() if is_live(lk, now)}
    slug = _ops.repo_slug(repo)
    args = ["pr", "list", "--state", "all", "--limit", "1000", "--json", "number,headRefName,state,url"]
    if slug:
        args[2:2] = ["--repo", slug]
    rc, out, err = _ops.gh(*args)
    if rc != 0:
        env_fail(f"gh pr list failed ({(err or out).strip()[:200]})")
    try:
        prs = {p.get("headRefName"): p for p in json.loads(out)}
    except (ValueError, AttributeError):
        env_fail("gh pr list printed no JSON")
    for p in _worktrees():
        if os.path.normcase(os.path.abspath(p)) in live_wts:
            continue
        top = _ops.toplevel(p)
        if not (top and _ops.same_dir(top, p)):
            continue
        rc, o, _ = _ops.git(p, "rev-parse", "--abbrev-ref", "HEAD")
        br = o.strip()
        pr = prs.get(br)
        if not pr or pr.get("state") not in ("MERGED", "CLOSED"):
            continue
        if is_dirty(p):
            kept.append({"path": p, "branch": br, "pr": pr.get("number"), "why": "uncommitted changes"})
            continue
        rc, _, e = _ops.git(repo, "worktree", "remove", p)
        if rc != 0:
            kept.append({"path": p, "branch": br, "pr": pr.get("number"), "why": e.strip()[:200]})
            continue
        _ops.git(repo, "branch", "-D", br)
        removed.append({"path": p, "branch": br, "pr": pr.get("number"), "state": pr.get("state")})
    _ops.git(repo, "worktree", "prune")
    res = {"reaped_locks": reaped, "removed_worktrees": removed, "kept_worktrees": kept}
    if as_json:
        print(json.dumps(res, indent=1))
    else:
        print(f"pr_worktree: reaped {len(reaped)} stale lock(s), removed {len(removed)} worktree(s), kept {len(kept)}")
        for k in kept:
            print(f"  kept {k['path']} ({k['branch']}, PR #{k['pr']}): {k['why']}")
    return 0


def cmd_discard(t, force):
    t = norm_ticker(t)
    if not force:
        raise Stop("pr_worktree: discard removes uncommitted work — pass --force", 2)
    lock = read_lock(t)
    now = _ops.now_et()
    if lock and is_live(lock, now):
        raise Stop(held_msg(t, lock), 4)
    if lock:
        reap_lock(t, lock)
    repo = repo_of_base()
    path = wt_path(t)
    if os.path.isdir(path):
        rc, _, err = _ops.git(repo, "worktree", "remove", "--force", path)
        if rc != 0 and os.path.isdir(path):
            shutil.rmtree(path, ignore_errors=True)
    _ops.git(repo, "worktree", "prune")
    print(f"pr_worktree: {t} discarded ({path})")
    return 0


def cmd_backlog_next(no_fetch):
    repo = repo_of_base()
    sha = fetch_main(repo, no_fetch)
    ids = _ops.backlog_ids(_ops.show(repo, sha, BACKLOG_REL) or "")
    print(f"EB-{(max(ids) + 1) if ids else 1:03d}")
    return 0


# --------------------------------------------------------------------------------------------- CLI
def build_parser():
    ap = argparse.ArgumentParser(prog="pr_worktree.py", description="Per-company PR worktrees (R5).")
    sub = ap.add_subparsers(dest="cmd")
    a = sub.add_parser("acquire")
    a.add_argument("ticker", nargs="?")
    a.add_argument("--bulk")
    a.add_argument("--holder", required=True)
    a.add_argument("--kind", choices=KINDS)
    a.add_argument("--ttl-hours", type=float)
    r = sub.add_parser("renew")
    r.add_argument("ticker")
    r.add_argument("--holder", required=True)
    r.add_argument("--ttl-hours", type=float, default=DEFAULT_TTL_HOURS)
    p = sub.add_parser("prepare")
    p.add_argument("ticker", nargs="?")
    p.add_argument("--bulk")
    p.add_argument("--holder")
    p.add_argument("--no-fetch", action="store_true")
    o = sub.add_parser("open")
    o.add_argument("ticker", nargs="?")
    o.add_argument("--bulk")
    o.add_argument("--body-file", required=True)
    o.add_argument("--holder")
    o.add_argument("--trailer", action="append")
    pu = sub.add_parser("push")
    pu.add_argument("ticker")
    pu.add_argument("-m", dest="message", required=True)
    pu.add_argument("--holder")
    pu.add_argument("--trailer", action="append")
    rs = sub.add_parser("restack")
    rs.add_argument("ticker")
    rs.add_argument("--holder")
    rs.add_argument("--trailer", action="append")
    rl = sub.add_parser("release")
    rl.add_argument("ticker")
    rl.add_argument("--holder", required=True)
    rl.add_argument("--force", action="store_true")
    rl.add_argument("--remove-worktree", action="store_true")
    s = sub.add_parser("status")
    s.add_argument("--json", action="store_true")
    rp = sub.add_parser("reap")
    rp.add_argument("--json", action="store_true")
    d = sub.add_parser("discard")
    d.add_argument("ticker")
    d.add_argument("--force", action="store_true")
    b = sub.add_parser("backlog-next")
    b.add_argument("--no-fetch", action="store_true")
    return ap


SUBCOMMANDS = ("acquire", "renew", "prepare", "open", "push", "restack", "release", "status", "reap", "discard",
               "backlog-next")


def main(argv=None):
    ap = build_parser()
    try:
        a = ap.parse_args(argv)
    except SystemExit as e:
        return 2 if e.code else 0
    if not a.cmd:
        print(__doc__, file=sys.stderr)
        return 2
    try:
        if a.cmd == "acquire":
            if a.bulk:
                if a.ticker:
                    raise Stop("pr_worktree: acquire takes <T> or --bulk REPORT, not both", 2)
                return cmd_acquire_bulk(a.bulk, a.holder, a.ttl_hours or BULK_TTL_HOURS)
            if not a.ticker or not a.kind:
                raise Stop("pr_worktree: acquire <T> needs --kind", 2)
            return cmd_acquire(a.ticker, a.holder, a.kind, a.ttl_hours or DEFAULT_TTL_HOURS)
        if a.cmd == "renew":
            return cmd_renew(a.ticker, a.holder, a.ttl_hours)
        if a.cmd in ("prepare", "open"):
            if bool(a.ticker) == bool(a.bulk):
                raise Stop(f"pr_worktree: {a.cmd} takes <T> or --bulk BRANCH", 2)
            if a.cmd == "prepare":
                return cmd_prepare(a.ticker, a.bulk, a.holder, a.no_fetch)
            return cmd_open(a.ticker, a.bulk, a.body_file, a.holder, a.trailer)
        if a.cmd == "push":
            return cmd_push(a.ticker, a.message, a.holder, a.trailer)
        if a.cmd == "restack":
            return cmd_restack(a.ticker, a.holder, a.trailer)
        if a.cmd == "release":
            return cmd_release(a.ticker, a.holder, a.force, a.remove_worktree)
        if a.cmd == "status":
            return cmd_status(a.json)
        if a.cmd == "reap":
            return cmd_reap(a.json)
        if a.cmd == "discard":
            return cmd_discard(a.ticker, a.force)
        if a.cmd == "backlog-next":
            return cmd_backlog_next(a.no_fetch)
    except Stop as e:
        print(str(e), file=sys.stderr)
        return e.code
    except subprocess.TimeoutExpired as e:
        print(f"pr_worktree: {e.cmd[1] if isinstance(e.cmd, list) and len(e.cmd) > 1 else 'a step'} timed out after "
              f"{e.timeout}s", file=sys.stderr)
        return 3
    return 2


if __name__ == "__main__":
    sys.exit(main())
