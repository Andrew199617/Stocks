#!/usr/bin/env python3
"""Shared helpers for the sweep-ops tools (engine 5.7, Andrew's ruling R5 of 2026-10-19 — sweep reliability).

preflight.py, pr_worktree.py, pr_audit.py, run_health.py and rebuild_scores.py import this module; it imports only
the standard library and _lock. Being a top-level _system/*.py it is itself drift-guarded by preflight.

  git(repo, *args)            -> (rc, stdout, stderr); never raises on a git error (rc 127 when git is missing)
  gh_cmd()                    -> the gh command: $STOCKS_GH (a test stub; a .py path runs under this interpreter) or gh
  repo_slug(repo)             -> "owner/name" from `git remote get-url origin` ($STOCKS_REPO_SLUG overrides)
  now_et()                    -> aware America/New_York time; $STOCKS_NOW (ISO, tests only) overrides
  fetch_ref(repo, ...)        -> fetch <remote>/<branch> with retries, serialized across processes by a lock file
  blob_of / blobs_of          -> the blob id git would store for a file in the sweep tree (hash-object WITH filters,
                                 so a core.autocrlf=true Windows checkout equals the committed blob)
  tree_blobs(repo, ref)       -> {path: blob} of every file at a commit (one ls-tree)
  RECORD_FILES, record_files  -> a company folder's judgment record (what a company PR carries; pr_audit compares it)
  engine_release_of(text)     -> ENGINE_RELEASE parsed from dcf_engine.py source
  scored_tickers(base)        -> folders holding score.json (refresh.py's rule)
  parse_backlog(text)         -> ENGINE_BACKLOG.md entries and the format problems (the one parser: pr_worktree, tests)
"""
import datetime
import glob
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
import time
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _lock import locked  # noqa: E402  (cross-platform exclusive file lock)
from _stable import _replace  # noqa: E402  (os.replace, retried on a Windows PermissionError)

ET = ZoneInfo("America/New_York")


def base_dir():
    """$STOCKS_BASE or the parent of _system/ — read at call time, so in-process callers (tests) can move it."""
    return os.environ.get("STOCKS_BASE") or os.path.dirname(HERE)


# --------------------------------------------------------------------------------------------- processes
def git(repo, *args, timeout=120, input=None, env=None):
    """(rc, stdout, stderr) of `git -C repo args…`. rc 127 when git is not installed, 124 on a timeout."""
    cmd = ["git"] + (["-C", repo] if repo else []) + [str(a) for a in args]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace",
                           timeout=timeout, input=input, env=env)
    except FileNotFoundError:
        return 127, "", "git is not installed"
    except subprocess.TimeoutExpired:
        return 124, "", f"git {' '.join(str(a) for a in args[:3])} timed out after {timeout}s"
    return r.returncode, r.stdout, r.stderr


def gh_cmd():
    """The gh command line as a list. $STOCKS_GH replaces it (tests point it at a stub script; a value ending in .py
    runs under this interpreter, so the stub works on Windows too)."""
    v = os.environ.get("STOCKS_GH")
    if not v:
        return ["gh"]
    if v.lower().endswith(".py"):
        return [sys.executable, v]
    return shlex.split(v, posix=(os.name != "nt"))


def gh(*args, timeout=120):
    """(rc, stdout, stderr) of the gh command. rc 127 when gh is missing."""
    try:
        r = subprocess.run(gh_cmd() + [str(a) for a in args], capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=timeout)
    except FileNotFoundError:
        return 127, "", "gh is not installed"
    except subprocess.TimeoutExpired:
        return 124, "", f"gh {' '.join(str(a) for a in args[:3])} timed out after {timeout}s"
    return r.returncode, r.stdout, r.stderr


def repo_slug(repo, remote="origin"):
    """owner/name of the GitHub remote; $STOCKS_REPO_SLUG overrides; None when the URL is not a GitHub one."""
    if os.environ.get("STOCKS_REPO_SLUG"):
        return os.environ["STOCKS_REPO_SLUG"]
    rc, out, _ = git(repo, "remote", "get-url", remote)
    if rc != 0:
        return None
    m = re.search(r"github\.com[:/]+([^/\s]+)/([^/\s]+?)(?:\.git)?/?\s*$", out.strip())
    return f"{m.group(1)}/{m.group(2)}" if m else None


PR_LIST_LIMIT = 100000   # gh pr list --limit: gh pages to it (100 a request); $STOCKS_GH_LIST_LIMIT overrides (tests)


def list_prs(repo, state="all"):
    """[whole-PR review fix, 2026-10-21] (prs, error) — EVERY pull request in `state` ("open" | "all"), newest first,
    as gh pr list prints them {number, headRefName, headRefOid, state OPEN | MERGED | CLOSED, createdAt, mergedAt,
    title, url}. The fixed `--limit 1000` / `--limit 200` silently dropped the older PRs once the repo had more
    (pr_audit read an open PR's folder as missing_pr — "cut it now", a duplicate PR; a review-fix acquire refused "no
    open PR"). gh pages to PR_LIST_LIMIT itself, and an answer that reaches the limit is truncated — an error, never
    "no PR". error is None on success, else the reason (gh failed, no JSON, truncated)."""
    try:
        limit = int(os.environ.get("STOCKS_GH_LIST_LIMIT") or PR_LIST_LIMIT)
    except ValueError:
        limit = PR_LIST_LIMIT
    slug = repo_slug(repo)
    rc, out, err = gh("pr", "list", *(["--repo", slug] if slug else []), "--state", state, "--limit", str(limit),
                      "--json", "number,headRefName,headRefOid,state,createdAt,mergedAt,title,url", timeout=900)
    if rc != 0:
        return [], f"gh pr list failed ({(err or out).strip()[:200]})"
    try:
        prs = json.loads(out)
    except ValueError:
        return [], "gh pr list printed no JSON"
    if not isinstance(prs, list):
        return [], "gh pr list printed no JSON list"
    if len(prs) >= limit:
        return [], (f"gh pr list returned {len(prs)} PRs, its --limit: the list is truncated, so a PR missing from it "
                    "may exist")
    return prs, None


# --------------------------------------------------------------------------------------------- time
def now_et():
    """Aware New York time; $STOCKS_NOW (an ISO timestamp, tests only) overrides — naive means ET."""
    v = os.environ.get("STOCKS_NOW")
    if v:
        d = datetime.datetime.fromisoformat(v.replace("Z", "+00:00"))
        return d.replace(tzinfo=ET) if d.tzinfo is None else d.astimezone(ET)
    return datetime.datetime.now(ET)


def parse_ts(s):
    """An aware datetime from an ISO string (naive = ET; 'Z' accepted), else None."""
    if not isinstance(s, str) or not s:
        return None
    try:
        d = datetime.datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        try:
            d = datetime.datetime.fromisoformat(s[:10])
        except ValueError:
            return None
    return d.replace(tzinfo=ET) if d.tzinfo is None else d


def iso(d):
    return d.isoformat(timespec="seconds") if d else None


def et_hm(d, ref=None):
    """'14:15 ET' when d is on ref's ET date, else '2026-10-19 14:15 ET'."""
    if d is None:
        return "?"
    d = d.astimezone(ET)
    if ref is not None and ref.astimezone(ET).date() == d.date():
        return d.strftime("%H:%M ET")
    return d.strftime("%Y-%m-%d %H:%M ET")


# --------------------------------------------------------------------------------------------- files
def load_json(path, default=None):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def write_json_atomic(path, obj, indent=1):
    """temp file in the same folder + os.replace (retried on Windows): a reader never sees half a file."""
    folder = os.path.dirname(os.path.abspath(path))
    os.makedirs(folder, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix="." + os.path.basename(path) + ".", suffix=".tmp", dir=folder)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(obj, f, indent=indent, ensure_ascii=False)
            f.write("\n")
        _replace(tmp, path)
    except BaseException:
        try:
            os.remove(tmp)
        except OSError:
            pass
        raise


def scored_tickers(base=None):
    """Folders (not starting with . or _) holding score.json — refresh.py's rule."""
    base = base or base_dir()
    try:
        names = os.listdir(base)
    except OSError:
        return []
    return sorted(d for d in names if not d.startswith((".", "_")) and os.path.isfile(os.path.join(base, d, "score.json")))


ENGINE_RELEASE_RE = re.compile(r'^ENGINE_RELEASE\s*=\s*"([^"]+)"', re.M)


def engine_release_of(text):
    m = ENGINE_RELEASE_RE.search(text or "")
    return m.group(1) if m else None


def local_engine_release(base=None):
    try:
        with open(os.path.join(base or base_dir(), "_system", "dcf_engine.py"), encoding="utf-8") as f:
            return engine_release_of(f.read())
    except OSError:
        return None


# --------------------------------------------------------------------------------------------- git objects
def toplevel(repo):
    rc, out, _ = git(repo, "rev-parse", "--show-toplevel")
    return os.path.normcase(os.path.abspath(out.strip())) if rc == 0 and out.strip() else None


def same_dir(a, b):
    return bool(a and b) and os.path.normcase(os.path.abspath(a)) == os.path.normcase(os.path.abspath(b))


def rev(repo, ref):
    rc, out, _ = git(repo, "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}")
    return out.strip() if rc == 0 and out.strip() else None


def commit_date(repo, ref):
    rc, out, _ = git(repo, "show", "-s", "--format=%cI", ref)
    return out.strip() if rc == 0 else None


def show(repo, ref, rel):
    """Text of <ref>:<rel>, None when absent."""
    rc, out, _ = git(repo, "show", f"{ref}:{rel}")
    return out if rc == 0 else None


def tree_blobs(repo, ref, prefix=None):
    """{path: blob id} of every file at ref (one `git ls-tree -r`), optionally under prefix/."""
    args = ["ls-tree", "-r", "--full-tree", ref]
    if prefix:
        args += ["--", prefix.rstrip("/") + "/"]
    rc, out, _ = git(repo, *args, timeout=300)
    blobs = {}
    if rc != 0:
        return blobs
    for line in out.splitlines():
        meta, _, path = line.partition("\t")
        parts = meta.split()
        if len(parts) == 3 and parts[1] == "blob":
            if path.startswith('"'):
                try:
                    path = json.loads(path)
                except ValueError:
                    pass
            blobs[path] = parts[2]
    return blobs


def origin_blob(repo, ref, rel):
    rc, out, _ = git(repo, "rev-parse", "--verify", "--quiet", f"{ref}:{rel}")
    return out.strip() if rc == 0 and out.strip() else None


def blob_of(repo, base, rel):
    """The blob id of <base>/<rel> as git would store it at <rel> in repo (hash-object WITH the repo's filters:
    on a core.autocrlf=true checkout this equals the committed blob; --no-filters would hash the CRLF bytes)."""
    p = os.path.join(base, *rel.split("/"))
    if not os.path.isfile(p):
        return None
    rc, out, _ = git(repo, "hash-object", f"--path={rel}", "--", p)
    return out.strip() if rc == 0 else None


def blobs_of(repo, base, rels, chunk=400, raw=False):
    """{rel: blob id or None} for many files: one `hash-object --stdin-paths` per chunk when base is the repo's own
    work tree (filters and attributes then come from the path itself), else one call per file (--path). raw=True
    hashes the bytes as they are (--no-filters) — see blob_variants."""
    rels = list(rels)
    out = {r: None for r in rels}
    present = [r for r in rels if os.path.isfile(os.path.join(base, *r.split("/")))]
    if not present:
        return out
    flag = ["--no-filters"] if raw else []
    if same_dir(toplevel(repo), base):
        for i in range(0, len(present), chunk):
            part = present[i:i + chunk]
            rc, so, _ = git(repo, "hash-object", *flag, "--stdin-paths", input="\n".join(part) + "\n", timeout=600)
            ids = so.split()
            if rc == 0 and len(ids) == len(part):
                out.update(zip(part, ids))
            else:   # fall back one by one (a path git refuses in the batch)
                for r in part:
                    out[r] = _blob_one(repo, base, r, raw)
        return out
    for r in present:
        out[r] = _blob_one(repo, base, r, raw)
    return out


def _blob_one(repo, base, rel, raw):
    if not raw:
        return blob_of(repo, base, rel)
    p = os.path.join(base, *rel.split("/"))
    rc, out, _ = git(repo, "hash-object", "--no-filters", "--", p)
    return out.strip() if rc == 0 else None


def blob_variants(repo, base, rels):
    """{rel: (filtered blob, raw blob)} — the two ids a sweep-tree file can legitimately have in the repo. With
    core.autocrlf=true, hash-object WITH filters equals the committed blob of a file committed with LF (the checkout
    holds CRLF); a file committed WITH CRLF bytes (the csv module writes \\r\\n: every financials_history.csv) is
    left as it is by git — but hash-object, which does not read the index, still converts it, so only the raw bytes
    (--no-filters) equal that blob. A file is unchanged when either id is the committed one (blob_matches)."""
    rels = list(rels)
    f = blobs_of(repo, base, rels)
    r = blobs_of(repo, base, rels, raw=True)
    return {x: (f.get(x), r.get(x)) for x in rels}


def blob_matches(variants, blob):
    """Whether a file whose (filtered, raw) ids are `variants` is the blob `blob` (None = absent on both sides)."""
    filt, raw = variants if variants else (None, None)
    if filt is None and raw is None:
        return blob is None
    return blob is not None and blob in (filt, raw)


def common_dir(repo):
    rc, out, _ = git(repo, "rev-parse", "--git-common-dir")
    if rc != 0 or not out.strip():
        return None
    p = out.strip()
    if not os.path.isabs(p):
        p = os.path.join(repo, p)
    return os.path.abspath(p)


FETCH_WAIT = "preflight: waiting for another preflight's fetch"


def fetch_ref(repo, remote="origin", branch="main", attempts=3, pause=2.0, timeout=90):
    """Fetch <remote>/<branch> into refs/remotes/<remote>/<branch>. Retries `attempts` times with pauses of
    pause × attempt seconds; serialized across parallel workers by <git-common-dir>/stocks-preflight.lock (two
    concurrent fetches can fail on the ref lock). Returns (ok, attempts_used, last_error_line)."""
    lock = os.path.join(common_dir(repo) or repo, "stocks-preflight.lock")
    last = ""
    used = 0
    with locked(lock, on_wait=lambda: print(FETCH_WAIT, file=sys.stderr)):
        for i in range(1, max(1, attempts) + 1):
            used = i
            rc, _, err = git(repo, "fetch", "--quiet", "--no-tags", remote,
                             f"+refs/heads/{branch}:refs/remotes/{remote}/{branch}", timeout=timeout)
            if rc == 0:
                return True, used, ""
            lines = [x.strip() for x in (err or "").splitlines() if x.strip()]
            last = lines[-1] if lines else f"exit {rc}"
            if i < attempts and pause:
                time.sleep(pause * i)
    return False, used, last


# --------------------------------------------------------------------------------------------- the record set
# A company folder's judgment record — what a company PR carries and pr_audit compares with origin/main (the SEC
# enrichment files the daily job rewrites and the gitignored caches are not in it). Engine 5.7 adds facts.json (R3),
# annual_instance.json (R2b) and the saved method runs dcf_numbers_<label>.json (R3).
RECORD_FILES = ("analysis.md", "dcf_numbers.json", "financials_history.csv", "judgment.json", "key_numbers.md",
                "score.json", "ttm.json", "second_pass.md", "facts.json", "annual_instance.json")
RECORD_GLOBS = ("dcf_numbers_*.json",)


def record_files(base, ticker, origin_paths=()):
    """The record files of <base>/<ticker> (and of the same folder on origin: origin_paths, repo-relative) — names
    only, sorted: the fixed list plus every dcf_numbers_<label>.json on either side."""
    names = set(RECORD_FILES)
    folder = os.path.join(base, ticker)
    for pat in RECORD_GLOBS:
        names.update(os.path.basename(p) for p in glob.glob(os.path.join(folder, pat)))
        rx = re.compile("^" + re.escape(ticker + "/") + pat.replace(".", r"\.").replace("*", r"[^/]*") + "$")
        names.update(p.split("/", 1)[1] for p in origin_paths if rx.match(p))
    return sorted(names)


# --------------------------------------------------------------------------------------------- ENGINE_BACKLOG.md
BACKLOG_REL = "_system/ENGINE_BACKLOG.md"
THREAD_URL = r"https://github\.com/Andrew199617/Stocks/pull/\d+#(?:discussion_r\d+|issuecomment-\d+)"
BL_HEADER = re.compile(r"^### EB-(\d{3,})( seen again)? — (.+)$")
BL_STATUS = re.compile(r"^- Status: (open|needs-decision \(Andrew\)|deferred \(.+\)"
                       r"|fixed in PR #(?:\d+|<this>) \(\d{4}-\d{2}-\d{2}\))$")
BL_OPENED = re.compile(r"^- Opened: (\d{4}-\d{2}-\d{2}), (.+)$")
BL_THREADS = re.compile(r"^- Threads: (.+)$")
BL_NO_THREAD = re.compile(r"^\(design \d{4}-\d{2}-\d{2}, no PR thread\)$")
BL_FIELDS = ("Opened", "Status", "Threads", "Effect", "Fix sketch")


def parse_backlog(text):
    """(entries, problems) for ENGINE_BACKLOG.md. Entries: [{id, seen_again, title, line, fields: {name: text}}].
    A full entry carries the five fields in order (Opened, Status, Threads, Effect, Fix sketch); a 'seen again' entry
    Threads and Effect, and its id must name an earlier full entry. Every Threads line holds at least one PR thread
    URL, or — only for an entry opened by a design — the literal '(design <date>, no PR thread)'. Full-entry ids are
    unique. The '    ### EB-<NNN> …' template lines (indented) are not entries."""
    entries, problems = [], []
    cur = None
    for i, raw in enumerate((text or "").splitlines(), 1):
        line = raw.rstrip()
        if line.startswith("### "):
            m = BL_HEADER.match(line)
            if not m:
                problems.append(f"line {i}: heading does not match '### EB-<NNN> — <file>:<area> — <defect>': {line[:80]}")
                cur = None
                continue
            cur = {"id": int(m.group(1)), "seen_again": bool(m.group(2)), "title": m.group(3), "line": i, "fields": {},
                   "order": []}
            entries.append(cur)
            continue
        if cur is None or not line.startswith("- "):
            if line.startswith("## "):
                cur = None
            continue
        name = line[2:].split(":", 1)[0]
        if name in BL_FIELDS:
            cur["fields"][name] = line
            cur["order"].append(name)
    full_ids = set()
    for e in entries:
        tag = f"EB-{e['id']:03d}{' seen again' if e['seen_again'] else ''} (line {e['line']})"
        want = ["Threads", "Effect"] if e["seen_again"] else list(BL_FIELDS)
        if e["order"] != want:
            problems.append(f"{tag}: fields {e['order']} — expected {want} in that order")
        if e["seen_again"]:
            if e["id"] not in full_ids:
                problems.append(f"{tag}: names no earlier entry")
        else:
            if e["id"] in full_ids:
                problems.append(f"{tag}: id used twice")
            full_ids.add(e["id"])
            st = e["fields"].get("Status", "")
            if st and not BL_STATUS.match(st):
                problems.append(f"{tag}: Status line does not match the format: {st}")
            op = e["fields"].get("Opened", "")
            if op and not BL_OPENED.match(op):
                problems.append(f"{tag}: Opened line does not match '- Opened: <YYYY-MM-DD>, <ticker> PR #<n>': {op}")
        th = e["fields"].get("Threads", "")
        if th:
            body = BL_THREADS.match(th).group(1)
            design = BL_OPENED.match(e["fields"].get("Opened", "")) if not e["seen_again"] else None
            if BL_NO_THREAD.match(body):
                if not (design and design.group(2).startswith("design")):
                    problems.append(f"{tag}: '(design …, no PR thread)' is allowed only for an entry opened by a design")
            elif not re.search(THREAD_URL, body):
                problems.append(f"{tag}: Threads line holds no PR thread URL")
        for k in ("order",):
            e.pop(k, None)
    return entries, problems


def backlog_ids(text):
    return {e["id"] for e in parse_backlog(text)[0] if not e["seen_again"]}
