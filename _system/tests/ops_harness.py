#!/usr/bin/env python3
"""Offline harness for the sweep-ops tests (engine 5.7, R5): temp git repos with a local bare "origin", a gh stub,
and synthetic company folders. Imported by test_preflight / test_pr_worktree / test_pr_audit / test_rebuild_scores /
test_run_health; never run on its own.

Git runs isolated from the machine's config (GIT_CONFIG_NOSYSTEM, an empty GIT_CONFIG_GLOBAL) with a fixed author,
so the tests behave the same on Windows and on the VM; a test that needs core.autocrlf sets it on its clone.

  make_origin(files, code=False) -> Origin(root, bare, seed): a bare repo seeded with `files` ({rel: text}); code=True
                                    also commits this tree's top-level _system/*.py and .gitignore (pr_worktree's
                                    worktree then runs the real make_score)
  clone(origin, name, autocrlf)  -> a clone of origin (the "sweep tree")
  commit_on_origin(origin, rel, text, msg) -> a commit pushed to origin (main moved)
  fake_gh(dir, responses)        -> path of a gh stub (set $STOCKS_GH to it); it logs argv to <dir>/gh_calls.jsonl
  write_folder(base, ticker, n, j, prior_score=None) -> a synthetic engine folder (test_make_score_55's record
                                    builder, the 5.7 obligations applied, content_hash stamped)
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SYS = os.path.dirname(HERE)
ROOT = os.path.dirname(SYS)
if SYS not in sys.path:
    sys.path.insert(0, SYS)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

_EMPTY_CFG = os.path.join(tempfile.gettempdir(), "ops_harness_empty_gitconfig")
open(_EMPTY_CFG, "a").close()
GIT_ENV = {"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": _EMPTY_CFG, "GIT_AUTHOR_NAME": "Ops Test",
           "GIT_AUTHOR_EMAIL": "ops@test.invalid", "GIT_COMMITTER_NAME": "Ops Test",
           "GIT_COMMITTER_EMAIL": "ops@test.invalid", "GIT_TERMINAL_PROMPT": "0"}
os.environ.update(GIT_ENV)   # inherited by every script a test runs


def git(cwd, *args, check=True):
    r = subprocess.run(["git", "-C", cwd] + list(args), capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=300)
    if check and r.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} failed in {cwd}: {r.stderr.strip()}")
    return r.stdout


class Origin:
    def __init__(self, root, bare, seed):
        self.root, self.bare, self.seed = root, bare, seed

    def head(self):
        return git(self.bare, "rev-parse", "main").strip()

    def close(self):
        shutil.rmtree(self.root, ignore_errors=True)


def _write(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    mode = "wb" if isinstance(data, bytes) else "w"
    with open(path, mode, **({} if isinstance(data, bytes) else {"encoding": "utf-8", "newline": "\n"})) as f:
        f.write(data if isinstance(data, (str, bytes)) else json.dumps(data, indent=1, ensure_ascii=False) + "\n")


def code_files():
    """This tree's top-level _system/*.py and .gitignore ({rel: bytes})."""
    out = {}
    for name in sorted(os.listdir(SYS)):
        p = os.path.join(SYS, name)
        if name.endswith(".py") and os.path.isfile(p):
            with open(p, "rb") as f:
                out[f"_system/{name}"] = f.read().replace(b"\r\n", b"\n")
    with open(os.path.join(ROOT, ".gitignore"), "rb") as f:
        out[".gitignore"] = f.read().replace(b"\r\n", b"\n")
    return out


def make_origin(files=None, code=False, prefix="ops_"):
    root = tempfile.mkdtemp(prefix=prefix)
    seed = os.path.join(root, "seed")
    os.makedirs(seed)
    git(seed, "init", "-q", "-b", "main")
    allf = dict(code_files()) if code else {}
    allf.update(files or {})
    if not allf:
        allf = {"README.md": "seed\n"}
    for rel, data in allf.items():
        _write(os.path.join(seed, *rel.split("/")), data)
    git(seed, "add", "--", ".")
    git(seed, "commit", "-q", "-m", "seed")
    bare = os.path.join(root, "origin.git")
    subprocess.run(["git", "clone", "-q", "--bare", seed, bare], check=True, capture_output=True)
    git(seed, "remote", "add", "origin", bare)
    git(seed, "fetch", "-q", "origin")
    git(seed, "branch", "-q", "--set-upstream-to", "origin/main", "main")
    return Origin(root, bare, seed)


def clone(origin, name="sweep", autocrlf=None):
    path = os.path.join(origin.root, name)
    args = ["git"] + (["-c", f"core.autocrlf={autocrlf}"] if autocrlf is not None else []) + \
        ["clone", "-q", origin.bare, path]
    subprocess.run(args, check=True, capture_output=True)
    if autocrlf is not None:
        git(path, "config", "core.autocrlf", str(autocrlf).lower())
    return path


def commit_on_origin(origin, rel, data, msg="origin change"):
    git(origin.seed, "pull", "-q", "--ff-only", "origin", "main")
    p = os.path.join(origin.seed, *rel.split("/"))
    if data is None:
        git(origin.seed, "rm", "-q", rel)
    else:
        _write(p, data)
        git(origin.seed, "add", rel)
    git(origin.seed, "commit", "-q", "-m", msg)
    git(origin.seed, "push", "-q", "origin", "main")
    return git(origin.seed, "rev-parse", "HEAD").strip()


def commit_in(repo, rels, msg="commit", push=True):
    git(repo, "add", "--", *rels)
    git(repo, "commit", "-q", "-m", msg)
    if push:
        git(repo, "push", "-q", "origin", "HEAD:main")


GH_STUB = r'''import json, os, sys
here = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(here, "gh_calls.jsonl"), "a", encoding="utf-8") as f:
    f.write(json.dumps(sys.argv[1:]) + "\n")
with open(os.path.join(here, "gh_responses.json"), encoding="utf-8") as f:
    resp = json.load(f)
args = sys.argv[1:]
key = " ".join(args[:2])
r = resp.get(key)
if r is None:
    sys.stderr.write("gh stub: no response for " + key + "\n")
    sys.exit(1)
if isinstance(r, dict) and "rc" in r:
    sys.stderr.write(r.get("stderr", ""))
    sys.stdout.write(r.get("stdout", ""))
    sys.exit(r["rc"])
if key == "pr view":
    n = args[2]
    r = r.get(n, {"files": []})
sys.stdout.write(r if isinstance(r, str) else json.dumps(r))
'''


def fake_gh(folder, responses):
    """A gh stub at <folder>/gh_stub.py answering by the first two argv words ('pr list', 'pr create', 'pr view' —
    the last keyed by PR number); {"rc": n, "stderr": …} fails. Logs every argv to <folder>/gh_calls.jsonl."""
    os.makedirs(folder, exist_ok=True)
    stub = os.path.join(folder, "gh_stub.py")
    with open(stub, "w", encoding="utf-8") as f:
        f.write(GH_STUB)
    with open(os.path.join(folder, "gh_responses.json"), "w", encoding="utf-8") as f:
        json.dump(responses, f)
    return stub


def gh_calls(folder):
    try:
        with open(os.path.join(folder, "gh_calls.jsonl"), encoding="utf-8") as f:
            return [json.loads(x) for x in f if x.strip()]
    except OSError:
        return []


def run(script, *args, base=None, env=None, stdin=None, timeout=900):
    """Run a real _system script as a subprocess (its own interpreter; STOCKS_BASE=base)."""
    e = dict(os.environ, PYTHONIOENCODING="utf-8")
    if base:
        e["STOCKS_BASE"] = base
    e.update(env or {})
    r = subprocess.run([sys.executable, os.path.join(SYS, script)] + [str(a) for a in args], capture_output=True,
                       text=True, encoding="utf-8", errors="replace", env=e, input=stdin, timeout=timeout)
    return r


# ------------------------------------------------------------------ synthetic company folders
def _ms55():
    import test_make_score_55 as T55
    return T55


def numbers(**kw):
    return _ms55()._numbers(**kw)


def judgment(n=None, **kw):
    return _ms55()._judgment(n, **kw)


def write_folder(base, ticker, n, j, prior_score=None, extra=None):
    """A synthetic engine folder under base (the record test_make_score_55.Run writes): rulings57's 5.7 obligations
    applied to a current-release record, dcf_numbers.json stamped with its content_hash. Returns the folder."""
    import rulings57
    T55 = _ms55()
    folder = os.path.join(base, ticker)
    os.makedirs(folder, exist_ok=True)
    n = dict(n, ticker=ticker)
    n, j = rulings57.apply(n, j, folder=folder)
    with open(os.path.join(folder, "dcf_numbers.json"), "w", encoding="utf-8") as f:
        json.dump(T55._stamp(n), f, indent=1, ensure_ascii=False)
    with open(os.path.join(folder, "judgment.json"), "w", encoding="utf-8") as f:
        f.write(json.dumps(j, indent=1, ensure_ascii=False) + "\n")
    if prior_score is not None:
        with open(os.path.join(folder, "score.json"), "w", encoding="utf-8") as f:
            json.dump(prior_score, f, indent=1)
    for name, data in (extra or {}).items():
        _write(os.path.join(folder, name), data)
    return folder


def make_score(base, ticker, code_dir=SYS, registry=None):
    """make_score.py <ticker> from code_dir with STOCKS_BASE=base (the registry at base/_system unless given)."""
    e = dict(os.environ, STOCKS_BASE=base, PYTHONIOENCODING="utf-8",
             MAKE_SCORE_REGISTRY=registry or os.path.join(base, "_system", "overrides_registry.json"))
    return subprocess.run([sys.executable, os.path.join(code_dir, "make_score.py"), ticker], capture_output=True,
                          text=True, encoding="utf-8", errors="replace", env=e, timeout=600)


def tree_sha(path):
    """{relpath: sha256} of every file under path (a dry run must leave all of them as they were)."""
    import hashlib
    out = {}
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d != ".git"]
        for name in files:
            if name.endswith(".lock"):   # lock files are ignored by *.lock; taking a lock is not a write
                continue
            p = os.path.join(root, name)
            with open(p, "rb") as f:
                out[os.path.relpath(p, path)] = hashlib.sha256(f.read()).hexdigest()
    return out


def run_tests(glb):
    fails = 0
    for name, fn in list(glb.items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"PASS {name}")
            except AssertionError as e:
                fails += 1
                print(f"FAIL {name}: {e}")
            except Exception as e:   # noqa: BLE001
                fails += 1
                import traceback
                print(f"ERROR {name}: {type(e).__name__}: {e}")
                traceback.print_exc()
    return 1 if fails else 0
