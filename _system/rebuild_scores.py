#!/usr/bin/env python3
"""make_score-only rebuild for Muse (engine 5.7, Andrew's ruling R5 of 2026-10-19 — sweep reliability).

A tool to rebuild score.json across the scored folders whose engine output is from an older release or whose
misfit notch is not yet applied — make_score only, never the engine — dry run by default, printing exactly which
folders change tier. It runs on the VM after a code PR merges and preflight.py --sync; the rebuilt folders reach
main as one company data PR (pr_worktree.py acquire --bulk), never inside a code PR.

Usage:
  python3 _system/rebuild_scores.py [--only T,T] [--work-dir DIR] [--json PATH] [--keep-work] [--no-network]
                                    [--allow-drift] [--no-fetch]
  python3 _system/rebuild_scores.py --apply --from-report PATH [--only T,T] [--holder ID] [--no-fetch]

Dry run (writes nothing in the sweep tree): preflight must exit 0 (the rebuild must be origin/main's make_score),
else exit 3 — unless --allow-drift (dev and tests: the report then says drift_allowed and --apply refuses it). Every
folder holding score.json (∩ --only) is copied, with _system/'s top-level files (not *.lock / *.tmp*), into a work
directory, and make_score.py from THIS tree runs there (STOCKS_BASE = the work copy, the registry the work copy's).
Before the first make_score, `industry_returns.py --json <work>/_system/industry_returns.json` builds the
same-ladder SIC-group medians (the moat evidence's industry_structure input, L3) from the sweep tree's scored
folders into the work copy — the stable write leaves the sweep tree's copy as it is when nothing but `built` would
change — so the dry run scores against exactly the file the apply step writes (review 2026-10-21: before, the tool
never wrote it, a first 5.7 rebuild ran without it, and every bulk PR deadlocked on moat_evidence). The report's
industry_file names the build (built, sha256) and whether it differs from the sweep tree's copy.
make_score imports the engine in-process but spawns <work>/_system/dcf_engine.py / ttm.py for a current-release
override replay; --no-network puts fail-loud stand-ins there (a folder that reaches one is `needs_network`).
Skipped: a name queued pending / in_progress (a re-score is coming), a live pr_worktree lock, a live pass-2 claim.
Per folder: state changed | unchanged | refused | needs_network | skipped, the score.json fields that change, the
tier before / after, the misfit_notch block, the alert gates, key_numbers.md / judgment.json / registry changes, the
input hashes the apply step re-checks, and main_sync (the record set vs origin/main: in_sync | differs — a bulk PR
carries only in_sync folders; a `differs` folder is rebuilt inside its own company PR).
reasons: release_mismatch (dcf_numbers engine_release != ENGINE_RELEASE), notch_applied (the misfit_notch block is
new or differs, an applied or a not-applied one), gate_closed (an alert gate true -> false), identity_stamped
(score.json gains dcf_content_hash), other_fields. A refusal is `needs_engine_rerun` when only an engine run can fix
it (no / mismatched content_hash, judgment.json or ttm.json changed after the run, a pre-5.7 ttm.json, an uncovered
data gap, no tier) — make_score will never accept that folder as it is — else `refused` (transient).
counts.live_paused: rebuilt folders whose live.json no longer binds to the new score (build_site's
live_score_problem / live_score_identity_missing: the site withholds it until reprice.py --all rewrites it).

Apply: refuses (exit 3) unless the report's origin_sha is origin/main now, drift_allowed is false and preflight
exits 0. Then `industry_returns.py --write` on the sweep tree (exit 3 when it fails); a build that differs from the
dry run's (a member folder changed meanwhile) is named, not refused — the applied table is the actual result. For
each `changed` folder of the report (∩ --only): skipped when its input hashes changed since the dry
run, it is queued pending / in_progress, or its pr_worktree lock is held; else the ticker's lock is taken (kind
rebuild), make_score.py runs on the sweep tree, the lock is released. Then ONE `reprice.py --all --quiet` and ONE
`build_site.py --quiet` (failures named, non-blocking); live_paused is measured before and after the reprice. The
bulk PR (pr_worktree.py --bulk) carries the sweep tree's industry_returns.json with the rebuilt folders.
Writes <report>.applied.json. Exit: 0 every listed folder rebuilt · 1 any refusal or skip · 2 usage · 3 precondition.
"""
import argparse
import datetime
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import _ops  # noqa: E402
import preflight  # noqa: E402

CACHE_FILES = frozenset({"prices.json", "live.json", "street.json"})   # per-folder gitignored caches
INPUT_FILES = ("dcf_numbers.json", "judgment.json", "score.json")
STALE_TIMEOUT, REPLAY_TIMEOUT = 900, 3600
NEEDS_ENGINE = ("has no content_hash", "content_hash MISMATCH", "judgment.json changed after the engine run",
                "ttm.json changed after the engine run", "ttm.json predates engine 5.7", "uncovered data_gap",
                "has no tier_by_numbers")
STAND_IN = r'''import os, sys
# rebuild_scores --no-network stand-in: make_score.py tried to spawn this script (a current-release override replay).
here = os.path.dirname(os.path.abspath(__file__))
tick = next((a for a in sys.argv[1:] if not a.startswith("-")), "UNKNOWN")
with open(os.path.join(here, "SPAWNED_" + os.path.basename(__file__) + "_" + tick), "a", encoding="utf-8") as f:
    f.write(" ".join(sys.argv) + "\n")
sys.stderr.write("rebuild_scores stand-in: " + os.path.basename(__file__) + " was spawned (needs network)\n")
sys.exit(97)
'''


def base():
    return os.path.abspath(_ops.base_dir())


def sha256(path):
    try:
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except OSError:
        return None


def current_release():
    return _ops.local_engine_release(os.path.dirname(HERE))   # this tree's ENGINE_RELEASE (make_score runs from HERE)


INDUSTRY_SCRIPT = os.path.join(HERE, "industry_returns.py")
INDUSTRY_REL = "_system/industry_returns.json"


def industry_doc(path):
    """{built, sha256} of an industry_returns.json (sha256 of the bytes, as make_score records it), or None."""
    try:
        with open(path, "rb") as f:
            raw = f.read()
        built = json.loads(raw.decode("utf-8")).get("built")
    except (OSError, ValueError, UnicodeDecodeError, AttributeError):
        return None
    return {"built": built, "sha256": hashlib.sha256(raw).hexdigest()}


def build_industry(b, args):
    """Run THIS tree's industry_returns.py over the sweep tree's folders (STOCKS_BASE = b) with `args`
    (['--json', <work copy>] in the dry run, ['--write'] in apply). (ok, last line). Skipped (ok) when the script
    does not exist (a tree before L3)."""
    if not os.path.isfile(INDUSTRY_SCRIPT):
        return True, "industry_returns.py not in this tree"
    env = dict(os.environ, STOCKS_BASE=b, PYTHONIOENCODING="utf-8")
    try:
        r = subprocess.run([sys.executable, INDUSTRY_SCRIPT] + args, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", env=env, cwd=b, timeout=1800)
    except subprocess.TimeoutExpired:
        return False, "industry_returns.py timed out"
    lines = [x for x in ((r.stdout or "") + "\n" + (r.stderr or "")).splitlines() if x.strip()]
    return r.returncode == 0, (lines[-1] if r.returncode else (lines[0] if lines else "")).strip()[:300]


def _skip_name(name):
    return name.endswith(".lock") or name.endswith(".tmp") or ".tmp." in name or name == "__pycache__"


def queue_states(b):
    q = _ops.load_json(os.path.join(b, "_system", "queue.json"), {}) or {}
    return {e.get("ticker"): e.get("status") for e in q.get("queue") or [] if isinstance(e, dict)}


def pass2_live(b):
    p = os.path.join(b, "_system", "second_pass_queue.json")
    return {t for t, _ in preflight._live_claims(p)}


def pr_lock_live(t):
    import pr_worktree
    lk = pr_worktree.read_lock(t)
    return bool(lk) and pr_worktree.is_live(lk, _ops.now_et()), lk


def skip_reason(t, qs, p2):
    st = qs.get(t)
    if st in ("pending", "in_progress"):
        return f"queue.json status {st} (a re-score is coming)"
    live, lk = pr_lock_live(t)
    if live:
        return f"pr_worktree lock held by {lk.get('holder')} (kind {lk.get('kind')})"
    if t in p2:
        return "a live pass-2 claim"
    return None


def registry_entries(path, t):
    reg = _ops.load_json(path, {}) or {}
    return [e for e in reg.get("entries") or [] if isinstance(e, dict) and e.get("ticker") == t]


def text_of(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read().replace("\r\n", "\n")
    except OSError:
        return None


def refusal_line(text):
    lines = [x.strip() for x in (text or "").splitlines() if x.strip()]
    hit = [x for x in lines if "REFUSED" in x]
    return (hit[0] if hit else (lines[-1] if lines else ""))[:400]


def live_problem(folder, score, numbers):
    """Why the folder's live.json does not bind to `score` (None when it binds; 'no live.json' when absent)."""
    import build_site
    lv = _ops.load_json(os.path.join(folder, "live.json"))
    if lv is None:
        return "no live.json"
    return build_site.live_score_problem(lv, score, numbers) or build_site.live_score_identity_missing(lv, score)


def classify(t, old, new, n, rel, kn_changed, j_changed, reg_changed):
    changed = sorted(k for k in set(old) | set(new) if old.get(k, "<absent>") != new.get(k, "<absent>"))
    reasons = []
    if n.get("engine_release") != rel:
        reasons.append("release_mismatch")
    mb, ma = old.get("misfit_notch"), new.get("misfit_notch")
    if isinstance(ma, dict) and ma != mb:
        reasons.append("notch_applied")
    if (old.get("alert_eligible") is True and new.get("alert_eligible") is False) or \
            (old.get("exit_alert_eligible") is True and new.get("exit_alert_eligible") is False):
        reasons.append("gate_closed")
    if "dcf_content_hash" in new and "dcf_content_hash" not in old:
        reasons.append("identity_stamped")
    accounted = {"misfit_notch", "alert_eligible", "exit_alert_eligible", "dcf_content_hash"}
    if set(changed) - accounted or kn_changed or j_changed or reg_changed:
        reasons.append("other_fields")
    return changed, reasons


def dry_run(only=None, work_dir=None, json_path=None, keep_work=False, no_network=False, allow_drift=False,
            fetch=True):
    b = base()
    rel = current_release()
    rep = preflight.check(base=b, fetch=fetch)
    if rep["exit"] != 0 and not allow_drift:
        print(preflight.first_line(rep))
        print("rebuild_scores: refusing — the rebuild must run origin/main's make_score (sync the tree first: "
              "PR_PROTOCOL.md \"Syncing the sweep tree\"); --allow-drift is for development only")
        return 3, None
    origin_sha = rep.get("origin_sha")
    names = _ops.scored_tickers(b)
    if only:
        names = [t for t in names if t in only]
    qs, p2 = queue_states(b), pass2_live(b)
    work = os.path.abspath(work_dir) if work_dir else tempfile.mkdtemp(prefix="rebuild_scores_")
    wsys = os.path.join(work, "_system")
    os.makedirs(wsys, exist_ok=True)
    for name in os.listdir(os.path.join(b, "_system")):
        src = os.path.join(b, "_system", name)
        if os.path.isfile(src) and not _skip_name(name):
            shutil.copyfile(src, os.path.join(wsys, name))
    if no_network:
        for script in ("dcf_engine.py", "ttm.py"):
            with open(os.path.join(wsys, script), "w", encoding="utf-8") as f:
                f.write(STAND_IN)
    sweep_ind = industry_doc(os.path.join(b, *INDUSTRY_REL.split("/")))
    ok, msg = build_industry(b, ["--json", os.path.join(wsys, "industry_returns.json")])
    if not ok:
        if not keep_work and not work_dir:
            shutil.rmtree(work, ignore_errors=True)
        print(f"rebuild_scores: refusing — industry_returns.py failed ({msg}); the moat evidence of every rebuilt "
              "folder reads that file")
        return 3, None
    work_ind = industry_doc(os.path.join(wsys, "industry_returns.json"))
    industry = {"path": INDUSTRY_REL, "built": (work_ind or {}).get("built"), "sha256": (work_ind or {}).get("sha256"),
                "sweep_sha256": (sweep_ind or {}).get("sha256"), "sweep_built": (sweep_ind or {}).get("built"),
                "differs_from_sweep": (work_ind or {}).get("sha256") != (sweep_ind or {}).get("sha256"),
                "note": msg}
    wreg = os.path.join(wsys, "overrides_registry.json")
    env = dict(os.environ, STOCKS_BASE=work, MAKE_SCORE_REGISTRY=wreg, PYTHONIOENCODING="utf-8")
    folders, origin_blobs, repo_ok = [], None, bool(origin_sha) and _ops.same_dir(_ops.toplevel(b), b)
    if repo_ok:
        origin_blobs = _ops.tree_blobs(b, origin_sha)
    for t in names:
        rec = {"ticker": t, "state": None, "engine_release_run": None, "reasons": [], "tier_final": None,
               "tier_by_numbers": None, "misfit_notch": None, "alert_eligible": None, "exit_alert_eligible": None,
               "changed_fields": [], "key_numbers_changed": False, "judgment_changed": False,
               "registry_changed": False, "refusal": None, "refusal_kind": None,
               "input_hashes": {f: sha256(os.path.join(b, t, f)) for f in INPUT_FILES}, "main_sync": None,
               "live": None}
        why = skip_reason(t, qs, p2)
        if why:
            rec.update(state="skipped", refusal=why)
            folders.append(rec)
            continue
        src, dst = os.path.join(b, t), os.path.join(work, t)
        if os.path.isdir(dst):
            shutil.rmtree(dst)
        os.makedirs(dst)
        for name in os.listdir(src):
            p = os.path.join(src, name)
            if os.path.isfile(p) and name not in CACHE_FILES and not _skip_name(name):
                shutil.copyfile(p, os.path.join(dst, name))
        n = _ops.load_json(os.path.join(src, "dcf_numbers.json"), {}) or {}
        rec["engine_release_run"] = n.get("engine_release")
        stale = n.get("engine_release") != rel
        before = set(x for x in os.listdir(wsys) if x.startswith("SPAWNED_"))
        try:
            r = subprocess.run([sys.executable, os.path.join(HERE, "make_score.py"), t], capture_output=True,
                               text=True, encoding="utf-8", errors="replace", env=env,
                               timeout=STALE_TIMEOUT if (stale or no_network) else REPLAY_TIMEOUT)
            rc, err = r.returncode, (r.stderr or r.stdout)
        except subprocess.TimeoutExpired:
            rc, err = 124, "make_score.py timed out"
        spawned = sorted(x for x in os.listdir(wsys) if x.startswith("SPAWNED_") and x not in before
                         and x.endswith("_" + t))
        old = _ops.load_json(os.path.join(src, "score.json"), {}) or {}
        if spawned:
            rec.update(state="needs_network", refusal=refusal_line(err) if rc else None, spawned=spawned)
        elif rc != 0:
            line = refusal_line(err)
            rec.update(state="refused", refusal=line,
                       refusal_kind="needs_engine_rerun" if any(s in line for s in NEEDS_ENGINE) else "refused")
        else:
            new = _ops.load_json(os.path.join(dst, "score.json"), {}) or {}
            kn = text_of(os.path.join(src, "key_numbers.md")) != text_of(os.path.join(dst, "key_numbers.md"))
            jc = text_of(os.path.join(src, "judgment.json")) != text_of(os.path.join(dst, "judgment.json"))
            rg = registry_entries(os.path.join(b, "_system", "overrides_registry.json"), t) != registry_entries(wreg, t)
            changed, reasons = classify(t, old, new, n, rel, kn, jc, rg)
            rec.update(state="changed" if (changed or kn or jc or rg) else "unchanged", reasons=reasons,
                       changed_fields=changed, key_numbers_changed=kn, judgment_changed=jc, registry_changed=rg,
                       tier_final={"before": old.get("tier_final"), "after": new.get("tier_final")},
                       tier_by_numbers=new.get("tier_by_numbers"),
                       misfit_notch={"before": old.get("misfit_notch"), "after": new.get("misfit_notch")},
                       alert_eligible={"before": old.get("alert_eligible"), "after": new.get("alert_eligible")},
                       exit_alert_eligible={"before": old.get("exit_alert_eligible"),
                                            "after": new.get("exit_alert_eligible")})
            if rec["state"] == "changed":
                was = live_problem(src, old, n)
                now = live_problem(src, new, n)
                rec["live"] = {"bound_before": was is None, "bound_after": now is None,
                               "problem_after": None if now in (None, "no live.json") else now,
                               "has_live": was != "no live.json"}
        folders.append(rec)
    if repo_ok:
        import pr_audit
        diff = pr_audit.differs(b, b, [f["ticker"] for f in folders], origin_blobs)
        for f in folders:
            f["main_sync"] = "in_sync" if not diff.get(f["ticker"]) else "differs"
    else:
        for f in folders:
            f["main_sync"] = "unknown"
    now = _ops.now_et()
    report = {"tool": "rebuild_scores", "mode": "dry_run", "engine_release": rel, "origin_sha": origin_sha,
              "drift_allowed": bool(allow_drift), "preflight": preflight.first_line(rep), "base": b,
              "made_at": _ops.iso(now), "no_network": bool(no_network), "industry_file": industry,
              "counts": counts_of(folders), "folders": folders}
    path = json_path or os.path.join(tempfile.gettempdir(), f"rebuild_scores-{rel}-{now.strftime('%Y%m%d-%H%M')}.json")
    _ops.write_json_atomic(path, report)
    if not keep_work and not work_dir:
        shutil.rmtree(work, ignore_errors=True)
    print(summary(report, path))
    return 0, report


def counts_of(folders):
    c = {k: 0 for k in ("selected", "changed", "unchanged", "refused", "needs_network", "skipped", "tier_changes",
                        "entry_gate_closed", "exit_gate_closed", "needs_engine_rerun", "identity_stamped",
                        "notch_applied", "live_paused", "live_paused_by_rebuild")}
    c["selected"] = len(folders)
    for f in folders:
        st = f["state"]
        if st in c:
            c[st] += 1
        if st == "refused" and f.get("refusal_kind") == "needs_engine_rerun":
            c["needs_engine_rerun"] += 1
        if st != "changed":
            continue
        tf = f.get("tier_final") or {}
        if tf.get("before") != tf.get("after"):
            c["tier_changes"] += 1
        if (f.get("alert_eligible") or {}).get("before") is True and (f.get("alert_eligible") or {}).get("after") is False:
            c["entry_gate_closed"] += 1
        ex = f.get("exit_alert_eligible") or {}
        if ex.get("before") is True and ex.get("after") is False:
            c["exit_gate_closed"] += 1
        for r in ("identity_stamped", "notch_applied"):
            if r in (f.get("reasons") or []):
                c[r] += 1
        lv = f.get("live") or {}
        if lv.get("has_live") and not lv.get("bound_after"):
            c["live_paused"] += 1
            if lv.get("bound_before"):
                c["live_paused_by_rebuild"] += 1
    return c


def _tier_why(f):
    a = ((f.get("misfit_notch") or {}).get("after")) or {}
    tf = f.get("tier_final") or {}
    if isinstance(a, dict) and a.get("applies") and a.get("tier_after_notch") == tf.get("after"):
        return f"misfit notch ({a.get('tier_by_numbers')} by numbers)"
    b = ((f.get("misfit_notch") or {}).get("before")) or {}
    if isinstance(b, dict) and b.get("applies") and not (isinstance(a, dict) and a.get("applies")):
        return "misfit notch no longer applies"
    return "other: " + ", ".join(x for x in f.get("changed_fields") or [] if x.startswith("tier"))[:60]


def summary(rep, path):
    c = rep["counts"]
    mode = "DRY RUN" if rep["mode"] == "dry_run" else "APPLIED"
    src = (f"make_score from origin/main {(rep.get('origin_sha') or '')[:7]}" if not rep.get("drift_allowed")
           else "make_score from THIS tree — drift allowed (--allow-drift), not a report --apply accepts")
    verb = "would change" if rep["mode"] == "dry_run" else "rebuilt"
    n_changed = c["changed"] if rep["mode"] == "dry_run" else c.get("rebuilt", 0)
    lines = [f"rebuild_scores: {mode} at release {rep['engine_release']} ({src}) over {c['selected']} scored folders —",
             f"  {n_changed} {verb}, {c['unchanged']} unchanged, {c['refused']} refuse (keep their current score.json"
             f"{'; ' + str(c['needs_engine_rerun']) + ' need an engine re-run' if c['needs_engine_rerun'] else ''}), "
             f"{c['needs_network']} need network, {c['skipped']} skipped"]
    ind = rep.get("industry_file")
    if ind and ind.get("sha256"):
        what = f"industry_returns.json built {ind.get('built')} (sha256 {str(ind['sha256'])[:12]})"
        if rep["mode"] == "dry_run":
            lines.append(f"{what}: " + ("a new build from the scored folders (the sweep tree's: "
                                        + (f"built {ind.get('sweep_built')}" if ind.get("sweep_sha256") else "none")
                                        + ") — --apply writes it before rebuilding; the bulk PR carries it"
                                        if ind.get("differs_from_sweep") else "the sweep tree's copy is current"))
        else:
            lines.append(f"{what}: written to the sweep tree before rebuilding"
                         + ("; it CHANGED since the dry run (a member folder changed): the table below is the actual "
                            "result" if ind.get("changed_since_dry_run") else "; the same build as the dry run's"))
    moved = [f for f in rep["folders"] if f["state"] in ("changed", "rebuilt")
             and (f.get("tier_final") or {}).get("before") != (f.get("tier_final") or {}).get("after")]
    lines.append(f"Tier changes (tier_final would publish differently): {len(moved)}")
    for f in moved:
        tf = f["tier_final"]
        lines.append(f"  {f['ticker']:<6}{tf.get('before')} → {tf.get('after')}  {_tier_why(f):<38} engine "
                     f"{f.get('engine_release_run') or 'unstamped'}  main: {str(f.get('main_sync')).replace('_', ' ')}")
    lines.append(f"Alert gates closed by the stale-release rule: {c['entry_gate_closed']} entry, {c['exit_gate_closed']} "
                 f"exit — re-run the engine at {rep['engine_release']} to reopen them")
    if c.get("live_paused"):
        lines.append(f"Live figures paused until reprice.py --all: {c['live_paused']} (of which "
                     f"{c['live_paused_by_rebuild']} were bound to the old score)"
                     + (f"; after the reprice: {c['live_paused_after']}" if "live_paused_after" in c else ""))
    for f in rep["folders"]:
        if f["state"] in ("refused", "needs_network"):
            lines.append(f"Refusal:  {f['ticker']:<6}{f.get('refusal') or 'spawned ' + ', '.join(f.get('spawned') or [])}"
                         + ("  (needs an engine re-run)" if f.get("refusal_kind") == "needs_engine_rerun" else ""))
    for f in rep["folders"]:
        if f["state"] == "skipped":
            lines.append(f"Skipped:  {f['ticker']:<6}{f.get('refusal')}")
    other = {}
    for f in rep["folders"]:
        for k in f.get("changed_fields") or []:
            other[k] = other.get(k, 0) + 1
    if other:
        lines.append("Changed fields: " + ", ".join(f"{k} {v}" for k, v in sorted(other.items(), key=lambda kv: -kv[1])[:12]))
    lines.append(f"Report: {path}")
    if rep["mode"] == "dry_run":
        lines.append(f"Apply: python3 _system/rebuild_scores.py --apply --from-report {path}")
    return "\n".join(lines)


def apply(report_path, only=None, holder=None, fetch=True):
    import pr_worktree
    rep = _ops.load_json(report_path)
    if not isinstance(rep, dict) or rep.get("tool") != "rebuild_scores" or rep.get("mode") != "dry_run":
        print(f"rebuild_scores: {report_path} is not a rebuild_scores dry-run report", file=sys.stderr)
        return 2
    if rep.get("drift_allowed"):
        print("rebuild_scores: refusing — the report was made with --allow-drift; dry-run again on a synced tree")
        return 3
    b = base()
    pf = preflight.check(base=b, fetch=fetch)
    if pf["exit"] != 0:
        print(preflight.first_line(pf))
        print("rebuild_scores: refusing — the apply step must run origin/main's make_score")
        return 3
    if pf["origin_sha"] != rep.get("origin_sha"):
        print(f"rebuild_scores: refusing — the report was made at {str(rep.get('origin_sha'))[:7]}; main is now "
              f"{pf['origin_sha'][:7]} — dry-run again")
        return 3
    holder = holder or "rebuild_scores"
    ok, msg = build_industry(b, ["--write"])
    if not ok:
        print(f"rebuild_scores: refusing — industry_returns.py --write failed ({msg}); nothing was rebuilt")
        return 3
    now_ind = industry_doc(os.path.join(b, *INDUSTRY_REL.split("/")))
    dry_ind = rep.get("industry_file") or {}
    industry = {"path": INDUSTRY_REL, "built": (now_ind or {}).get("built"), "sha256": (now_ind or {}).get("sha256"),
                "dry_run_sha256": dry_ind.get("sha256"), "note": msg,
                "changed_since_dry_run": bool(dry_ind) and (now_ind or {}).get("sha256") != dry_ind.get("sha256")}
    qs = queue_states(b)
    env = dict(os.environ, STOCKS_BASE=b, PYTHONIOENCODING="utf-8")
    env.pop("MAKE_SCORE_REGISTRY", None)
    out = []
    for f in rep["folders"]:
        if f.get("state") != "changed" or (only and f["ticker"] not in only):
            continue
        t = f["ticker"]
        rec = dict(f, state=None, refusal=None)
        now_hashes = {k: sha256(os.path.join(b, t, k)) for k in INPUT_FILES}
        if now_hashes != f.get("input_hashes"):
            rec.update(state="skipped", refusal="changed since the dry run")
        elif qs.get(t) in ("pending", "in_progress"):
            rec.update(state="skipped", refusal=f"queue.json status {qs.get(t)}")
        else:
            try:
                lease = pr_worktree._take(t, holder, "rebuild", 1.0, _ops.now_et())
            except pr_worktree.Stop as e:
                rec.update(state="skipped", refusal=str(e).replace("pr_worktree: ", "")[:200])
            else:
                try:
                    r = subprocess.run([sys.executable, os.path.join(HERE, "make_score.py"), t], capture_output=True,
                                       text=True, encoding="utf-8", errors="replace", env=env,
                                       timeout=STALE_TIMEOUT if f.get("engine_release_run") != rep["engine_release"]
                                       else REPLAY_TIMEOUT)
                    if r.returncode == 0:
                        rec["state"] = "rebuilt"
                        new = _ops.load_json(os.path.join(b, t, "score.json"), {}) or {}
                        rec["tier_final"] = dict(f.get("tier_final") or {}, after=new.get("tier_final"))
                    else:
                        line = refusal_line(r.stderr or r.stdout)
                        rec.update(state="refused", refusal=line,
                                   refusal_kind="needs_engine_rerun" if any(s in line for s in NEEDS_ENGINE) else "refused")
                except subprocess.TimeoutExpired:
                    rec.update(state="refused", refusal="make_score.py timed out", refusal_kind="refused")
                finally:
                    pr_worktree.drop_lock(t, lease)   # only this lease, never another holder's
        out.append(rec)

    def paused():
        k = 0
        for x in out:
            if x["state"] != "rebuilt":
                continue
            folder = os.path.join(b, x["ticker"])
            s = _ops.load_json(os.path.join(folder, "score.json"), {}) or {}
            n = _ops.load_json(os.path.join(folder, "dcf_numbers.json"), {}) or {}
            p = live_problem(folder, s, n)
            if p not in (None, "no live.json"):
                k += 1
        return k
    paused_before = paused()
    steps = []
    for label, args in (("reprice", ["reprice.py", "--all", "--quiet"]), ("site", ["build_site.py", "--quiet"])):
        try:
            rc = subprocess.run([sys.executable, os.path.join(HERE, args[0])] + args[1:], env=env, cwd=b,
                                capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=3600).returncode
        except subprocess.TimeoutExpired:
            rc = 124
        steps.append({"step": label, "rc": rc})
    paused_after = paused()
    c = counts_of([dict(x, state="changed" if x["state"] == "rebuilt" else x["state"]) for x in out])
    c["rebuilt"] = sum(1 for x in out if x["state"] == "rebuilt")
    c["live_paused"], c["live_paused_after"] = paused_before, paused_after
    applied = dict(rep, mode="apply", applied_at=_ops.iso(_ops.now_et()), counts=c, folders=out, steps=steps,
                   from_report=report_path, industry_file=industry)
    apath = report_path + ".applied.json"
    _ops.write_json_atomic(apath, applied)
    print(summary(applied, apath))
    for s in steps:
        if s["rc"] != 0:
            print(f"rebuild_scores: {s['step']} exited {s['rc']} (non-blocking: rerun it)")
    return 0 if all(x["state"] == "rebuilt" for x in out) else 1


def main(argv=None):
    ap = argparse.ArgumentParser(prog="rebuild_scores.py", description="make_score-only rebuild (R5).")
    ap.add_argument("--only")
    ap.add_argument("--work-dir")
    ap.add_argument("--json")
    ap.add_argument("--keep-work", action="store_true")
    ap.add_argument("--no-network", action="store_true")
    ap.add_argument("--allow-drift", action="store_true")
    ap.add_argument("--no-fetch", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--from-report")
    ap.add_argument("--holder")
    try:
        a = ap.parse_args(argv)
    except SystemExit as e:
        return 2 if e.code else 0
    only = {x.strip().upper() for x in a.only.split(",") if x.strip()} if a.only else None
    if a.apply:
        if not a.from_report or a.allow_drift or a.work_dir or a.no_network:
            print("rebuild_scores: --apply needs --from-report PATH (and takes no --allow-drift / --work-dir / "
                  "--no-network)", file=sys.stderr)
            return 2
        return apply(a.from_report, only, a.holder, fetch=not a.no_fetch)
    if a.from_report or a.holder:
        print("rebuild_scores: --from-report / --holder go with --apply", file=sys.stderr)
        return 2
    rc, _ = dry_run(only, a.work_dir, a.json, a.keep_work, a.no_network, a.allow_drift, fetch=not a.no_fetch)
    return rc


if __name__ == "__main__":
    sys.exit(main())
