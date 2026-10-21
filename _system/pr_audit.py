#!/usr/bin/env python3
"""Done-without-PR audit (engine 5.7, Andrew's ruling R5 of 2026-10-19 — sweep reliability).

The miss it stops: BMRN was done in queue.json and scored on the sweep tree, its folder differed from main, and no
PR carried it. Run daily by the 19:07 dcf-daily-ranking job with `--quiet`: one line (the summary and every finding's
ticker and state) when there are findings, nothing when there are none; that line goes in the message.

Usage:
  python3 _system/pr_audit.py [--json PATH] [--grace-hours 6] [--quiet] [--no-fetch]
                              [--gh-json FILE] [--gh-files-json FILE]      # test doubles for gh output

Candidates: queue.json entries with status done, plus APP (outside the queue) when APP/score.json exists.
Per candidate, in order:
  missing_folder       done in queue.json, no <T>/score.json here                                   (finding)
  score_not_from_run   score.json is not make_score's score of this dcf_numbers.json (build_site.score_from_run):
                       make_score refused the latest engine run or has not run on it — no PR until it scores (finding)
  in_sync              every record file equals origin/main (git hash-object with filters, or of the raw bytes for a
                       file committed with CRLF such as financials_history.csv, vs origin's blob; absent on both sides
                       = equal)
  pr_open              differs; an OPEN PR for T created at/after the scoring generation's start
  merged_then_changed  differs; a MERGED PR for T created at/after the generation start — the sweep folder changed
                       after the merge, or review fixes were made only in the PR worktree                (finding)
  grace                differs; no PR for this generation; the generation started within --grace-hours (6)
  stale_open_pr        differs; the only OPEN PR for T predates this generation                        (finding)
  missing_pr           differs; no OPEN/MERGED PR for T since the generation started (the BMRN case)   (finding)
Record files (the judgment record, not the SEC enrichment the daily job rewrites): analysis.md, dcf_numbers.json,
financials_history.csv, judgment.json, key_numbers.md, score.json, ttm.json, second_pass.md, facts.json,
annual_instance.json and every dcf_numbers_<label>.json (_ops.RECORD_FILES).
A PR belongs to T when its head branch is dcf/<T>, dcf/<T>-<YYYYMMDD> or dcf/<T>-<YYYYMMDD>-<n>; or its title starts
"DCF pass 1: <T> —", "DCF pass 1 update: <T> —", "Re-score: <T> —", "Second pass: <T> —" or "DCF re-run: <T> —"; or
it is a rebuild/* or bulk-* branch whose file list holds <T>/score.json.
Generation start: the done entry's claimed_at, else its completed date at 00:00 ET, else the epoch; APP: its
score.json analysis_date.
Exit: 0 no findings · 1 findings · 2 usage · 3 cannot audit (git, gh or the fetch failed).
What to do with each finding: _system/PR_PROTOCOL.md "pr_audit findings".
"""
import argparse
import datetime
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import _ops  # noqa: E402

FINDINGS = ("missing_folder", "score_not_from_run", "merged_then_changed", "stale_open_pr", "missing_pr")
OK_STATES = ("in_sync", "pr_open", "grace")
STATES = ("in_sync", "pr_open", "grace", "missing_pr", "merged_then_changed", "stale_open_pr", "missing_folder",
          "score_not_from_run")
TITLE_RX = r"^(DCF pass 1( update)?|Re-score|Second pass|DCF re-run): {t} —"
BULK_HEAD = re.compile(r"^(rebuild/|bulk-)")
EPOCH = datetime.datetime(1970, 1, 1, tzinfo=_ops.ET)
HINTS = {"missing_folder": "done in queue.json but no score.json — block or requeue the name",
         "score_not_from_run": "make_score refused this folder's latest engine run or has not run on it — no PR until "
                               "it scores",
         "merged_then_changed": "the folder changed after its PR merged — cut the newer generation's PR, or copy "
                                "main's files back if a review fix was left behind",
         "stale_open_pr": "the open PR predates this generation — push the new generation to it (review-fix) or "
                          "close it and cut a new one",
         "missing_pr": "no PR for this generation — cut it now (PR_PROTOCOL.md)"}


class AuditError(Exception):
    pass


def pr_belongs(pr, t, files_of=None):
    head = pr.get("headRefName") or ""
    if re.match(rf"^dcf/{re.escape(t)}(-\d{{8}}(-\d+)?)?$", head):
        return True
    if re.match(TITLE_RX.format(t=re.escape(t)), pr.get("title") or ""):
        return True
    if BULK_HEAD.match(head) and files_of is not None:
        return f"{t}/score.json" in (files_of(pr) or ())
    return False


def generation_start(entry, base, t):
    if entry is None:   # APP, outside the queue
        s = _ops.load_json(os.path.join(base, t, "score.json"), {}) or {}
        return _ops.parse_ts(s.get("analysis_date")) or EPOCH
    ts = _ops.parse_ts(entry.get("claimed_at"))
    if ts:
        return ts
    c = entry.get("completed")
    if c:
        try:
            return datetime.datetime.fromisoformat(c[:10]).replace(tzinfo=_ops.ET)
        except ValueError:
            pass
    return EPOCH


def _score_from_run(base, t):
    """(matches, first mismatch) — build_site.score_from_run, imported lazily (the site's own binding rule)."""
    import build_site
    s = _ops.load_json(os.path.join(base, t, "score.json"))
    n = _ops.load_json(os.path.join(base, t, "dcf_numbers.json"))
    if n is None:
        return False, "dcf_numbers.json missing or unreadable"
    ok, mm = build_site.score_from_run(s, n)
    return ok, (mm[0] if mm else None)


def differs(repo, base, tickers, origin):
    """{T: [record files that differ from origin/main]} for every ticker (one hash-object batch)."""
    by_t, rels = {}, []
    origin_paths = list(origin)
    for t in tickers:
        names = _ops.record_files(base, t, [p for p in origin_paths if p.startswith(t + "/")])
        by_t[t] = names
        rels += [f"{t}/{n}" for n in names]
    here = _ops.blob_variants(repo, base, rels)   # filtered and raw ids: a CRLF-committed CSV matches on its raw id
    out = {}
    for t, names in by_t.items():
        out[t] = [n for n in names if not _ops.blob_matches(here.get(f"{t}/{n}"), origin.get(f"{t}/{n}"))]
    return out


def load_prs(repo, gh_json=None):
    if gh_json:
        d = _ops.load_json(gh_json)
        if not isinstance(d, list):
            raise AuditError(f"--gh-json {gh_json} is not a JSON list")
        return d
    slug = _ops.repo_slug(repo)
    args = ["pr", "list", "--state", "all", "--limit", "1000", "--json",
            "number,headRefName,state,createdAt,mergedAt,title,url"]
    if slug:
        args[2:2] = ["--repo", slug]
    rc, out, err = _ops.gh(*args)
    if rc != 0:
        raise AuditError(f"gh pr list failed ({(err or out).strip()[:200]})")
    try:
        d = json.loads(out)
    except ValueError:
        raise AuditError("gh pr list printed no JSON")
    if not isinstance(d, list):
        raise AuditError("gh pr list printed no JSON list")
    return d


def files_loader(repo, gh_files_json=None):
    cache = {}
    canned = _ops.load_json(gh_files_json) if gh_files_json else None

    def files_of(pr):
        n = pr.get("number")
        if n in cache:
            return cache[n]
        if canned is not None:
            v = canned.get(str(n)) or []
        else:
            slug = _ops.repo_slug(repo)
            args = ["pr", "view", str(n), "--json", "files"] + (["--repo", slug] if slug else [])
            rc, out, err = _ops.gh(*args)
            if rc != 0:
                raise AuditError(f"gh pr view {n} failed ({(err or out).strip()[:200]})")
            try:
                v = [f.get("path") for f in json.loads(out).get("files") or []]
            except (ValueError, AttributeError):
                raise AuditError(f"gh pr view {n} printed no JSON")
        cache[n] = [x if isinstance(x, str) else (x or {}).get("path") for x in v]
        return cache[n]
    return files_of


def audit(base=None, repo=None, grace_hours=6.0, fetch=True, gh_json=None, gh_files_json=None, remote="origin",
          branch="main"):
    base = os.path.abspath(base or _ops.base_dir())
    repo = os.path.abspath(repo or base)
    if _ops.toplevel(repo) is None:
        raise AuditError(f"{repo} is not a git work tree")
    if fetch:
        ok, used, last = _ops.fetch_ref(repo, remote, branch)
        if not ok:
            raise AuditError(f"git fetch {remote} {branch} failed {used} times ({last})")
    ref = f"{remote}/{branch}"
    sha = _ops.rev(repo, ref)
    if not sha:
        raise AuditError(f"no {ref} in {repo}")
    now = _ops.now_et()
    q = _ops.load_json(os.path.join(base, "_system", "queue.json"))
    if not isinstance(q, dict) or not isinstance(q.get("queue"), list):
        raise AuditError(f"{base}/_system/queue.json is missing or unreadable")
    cands = [(e["ticker"], e) for e in q["queue"] if isinstance(e, dict) and e.get("status") == "done" and e.get("ticker")]
    if "APP" not in {t for t, _ in cands} and os.path.isfile(os.path.join(base, "APP", "score.json")):
        cands.append(("APP", None))
    prs = load_prs(repo, gh_json)
    files_of = files_loader(repo, gh_files_json)
    origin = _ops.tree_blobs(repo, sha)
    present = [t for t, _ in cands if os.path.isfile(os.path.join(base, t, "score.json"))]
    diff = differs(repo, base, present, origin)
    findings, ok = [], {k: [] for k in OK_STATES}
    counts = {k: 0 for k in STATES}
    for t, entry in cands:
        start = generation_start(entry, base, t)
        rec = {"ticker": t, "generation_start": _ops.iso(start),
               "completed": (entry or {}).get("completed"), "differs": [], "prs": []}
        if t not in diff:
            state = "missing_folder"
        else:
            rec["differs"] = diff[t]
            match, why = _score_from_run(base, t)
            mine = [p for p in prs if pr_belongs(p, t, files_of)]
            rec["prs"] = [{k: p.get(k) for k in ("number", "state", "headRefName", "createdAt", "mergedAt", "url")}
                          for p in mine]
            new = [p for p in mine if (_ops.parse_ts(p.get("createdAt")) or EPOCH) >= start]
            if not match:
                state = "score_not_from_run"
                rec["mismatch"] = why
            elif not diff[t]:
                state = "in_sync"
            elif any(p.get("state") == "OPEN" for p in new):
                state = "pr_open"
            elif any(p.get("state") == "MERGED" for p in new):
                state = "merged_then_changed"
            elif now - start <= datetime.timedelta(hours=grace_hours):
                state = "grace"
            elif any(p.get("state") == "OPEN" for p in mine):
                state = "stale_open_pr"
            else:
                state = "missing_pr"
        counts[state] += 1
        if state in FINDINGS:
            rec["state"] = state
            rec["hint"] = HINTS[state]
            findings.append(rec)
        else:
            ok[state].append(t)
    return {"checked_at": _ops.iso(now), "origin_sha": sha, "candidates": len(cands), "counts": counts,
            "findings": findings, "ok": ok}


def _fmt_t(s):
    d = _ops.parse_ts(s)
    return d.astimezone(_ops.ET).strftime("%Y-%m-%d %H:%M ET") if d else "?"


def finding_line(f):
    t, st = f["ticker"], f["state"]
    dif = f.get("differs") or []
    dif_s = ", ".join(dif[:3]) + (f" (+{len(dif) - 3})" if len(dif) > 3 else "")
    prs = f.get("prs") or []
    if st == "missing_pr":
        return (f"  MISSING_PR           {t:<5} claimed {_fmt_t(f['generation_start'])}, done {f.get('completed') or '?'}"
                f"  differs: {dif_s}  no PR for {t} since the claim")
    if st == "merged_then_changed":
        m = next((p for p in prs if p.get("state") == "MERGED"), {})
        return (f"  MERGED_THEN_CHANGED  {t:<5} PR #{m.get('number')} merged {_fmt_t(m.get('mergedAt'))}  differs since: "
                f"{dif_s}")
    if st == "stale_open_pr":
        o = next((p for p in prs if p.get("state") == "OPEN"), {})
        return (f"  STALE_OPEN_PR        {t:<5} PR #{o.get('number')} opened {_fmt_t(o.get('createdAt'))} predates the "
                f"claim at {_fmt_t(f['generation_start'])}")
    if st == "score_not_from_run":
        return f"  SCORE_NOT_FROM_RUN   {t:<5} {f.get('mismatch') or ''} — {HINTS[st]}"
    return f"  MISSING_FOLDER       {t:<5} {HINTS[st]}"


def summary_line(rep):
    c = rep["counts"]
    n = len(rep["findings"])
    return (f"pr_audit: {rep['candidates']} done names at origin/main {rep['origin_sha'][:7]} — {c['in_sync']} in sync, "
            f"{c['pr_open']} PR open, {c['grace']} in grace, {n} finding{'s' if n != 1 else ''}")


def main(argv=None):
    ap = argparse.ArgumentParser(prog="pr_audit.py", description="Done-without-PR audit (R5).")
    ap.add_argument("--json")
    ap.add_argument("--grace-hours", type=float, default=6.0)
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--no-fetch", action="store_true")
    ap.add_argument("--gh-json")
    ap.add_argument("--gh-files-json")
    try:
        a = ap.parse_args(argv)
    except SystemExit as e:
        return 2 if e.code else 0
    if a.grace_hours < 0:
        print("pr_audit: --grace-hours must be >= 0", file=sys.stderr)
        return 2
    try:
        rep = audit(grace_hours=a.grace_hours, fetch=not a.no_fetch, gh_json=a.gh_json, gh_files_json=a.gh_files_json)
    except AuditError as e:
        print(f"pr_audit: CANNOT AUDIT — {e}")
        return 3
    if a.json:
        _ops.write_json_atomic(a.json, rep)
    if a.quiet:   # one line for the 19:07 message (nothing when there are no findings)
        if rep["findings"]:
            print(summary_line(rep) + " (" + ", ".join(f"{f['ticker']} {f['state']}" for f in rep["findings"][:20])
                  + (", …" if len(rep["findings"]) > 20 else "") + ")")
    else:
        print(summary_line(rep))
        for f in rep["findings"]:
            print(finding_line(f))
        if rep["findings"]:
            print('What to do with each: _system/PR_PROTOCOL.md "pr_audit findings".')
    return 1 if rep["findings"] else 0


if __name__ == "__main__":
    sys.exit(main())
