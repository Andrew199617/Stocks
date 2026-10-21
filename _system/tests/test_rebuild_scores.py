#!/usr/bin/env python3
"""rebuild_scores.py — the make_score-only rebuild (engine 5.7, Andrew's ruling R5 of 2026-10-19; design 05 §6, §9
and the L5 rebase amendments A6, A14, A15). Run: python _system/tests/test_rebuild_scores.py.

Synthetic temp STOCKS_BASEs (test_make_score_55's record builder; fail-loud dcf_engine.py / ttm.py stand-ins in the
base's _system/, the scripts make_score spawns); the dry-run cases run with --allow-drift on a non-git base, the
apply cases on a sweep clone of a local bare origin (preflight exits 0 there). Covered: a dry run writes nothing to
the base; a 5.5.0 folder is changed (release_mismatch) and its open exit gate closes (gate_closed); a 5.5.0 sector
misfit with numbers tier C is listed as a tier change C -> D (notch_applied — runs against the merged L1 notch); a
folder make_score refuses is reported (needs_engine_rerun) and kept; --no-network marks a current-release override
folder needs_network with the stand-in's marker; skipped names; live_paused; apply refuses a report made at another
origin/main sha or with --allow-drift and skips a folder whose inputs changed since the dry run; apply skips a
pr_worktree-locked or in-progress ticker; apply never spawns the engine for stale folders and runs reprice + site
once; a drifted (non-git) base refuses without --allow-drift.
"""
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ops_harness as H  # noqa: E402
import dcf_engine as E  # noqa: E402
import test_make_score_55 as T55  # noqa: E402

CUR = E.ENGINE_RELEASE
OLD = "5.5.0"
FIN_FLAG = "SECTOR_MODEL_MISMATCH: Finance sector — OE/capex DCF fits finance names poorly; grade confidence low"


def _base():
    b = tempfile.mkdtemp(prefix="rebuild_scores_t_")
    os.makedirs(os.path.join(b, "_system"))
    for name in ("dcf_engine.py", "ttm.py"):
        with open(os.path.join(b, "_system", name), "w", encoding="utf-8") as f:
            f.write(T55.FAIL_LOUD)
    with open(os.path.join(b, "_system", "overrides_registry.json"), "w", encoding="utf-8") as f:
        json.dump({"entries": []}, f)
    return b


def _queue(b, entries):
    with open(os.path.join(b, "_system", "queue.json"), "w", encoding="utf-8") as f:
        json.dump({"queue": entries}, f)


def _scored(b, t, n, j=None, mutate=None):
    """A folder scored by this tree's make_score, then (mutate) the prior score.json edited the way an older
    make_score would have left it."""
    H.write_folder(b, t, n, j if j is not None else H.judgment(n), extra={"analysis.md": f"# {t}\nTest.\n"})
    r = H.make_score(b, t)
    assert r.returncode == 0, f"fixture make_score refused {t}: {r.stderr}"
    if mutate:
        p = os.path.join(b, t, "score.json")
        s = json.load(open(p, encoding="utf-8"))
        mutate(s)
        json.dump(s, open(p, "w", encoding="utf-8"), indent=1)


def _old_record(s):
    """What a pre-5.7 make_score wrote: no 5.7 blocks, open gates."""
    for k in ("misfit_notch", "misfit_sector_set_aside", "moat_evidence", "dcf_content_hash", "key_numbers_sha256",
              "declared_facts", "previous_score", "alert_suppressed_reason", "exit_alert_suppressed_reason"):
        s.pop(k, None)
    s["exit_alert_eligible"] = True


def _dry(b, *args):
    out = os.path.join(b, "_report.json")
    r = H.run("rebuild_scores.py", "--allow-drift", "--json", out, *args, base=b)
    rep = json.load(open(out, encoding="utf-8")) if os.path.exists(out) else None
    return r, rep


def _f(rep, t):
    return next(x for x in rep["folders"] if x["ticker"] == t)


def test_dry_run_writes_nothing_to_base():
    b = _base()
    try:
        _queue(b, [{"ticker": "AAA", "status": "done"}])
        _scored(b, "AAA", H.numbers(release=OLD), mutate=_old_record)
        before = H.tree_sha(b)
        r, rep = _dry(b, "--json", os.path.join(tempfile.gettempdir(), "rb_t1.json"))
        assert r.returncode == 0, r.stdout + r.stderr
        assert H.tree_sha(b) == before, "a dry run changed the base"
        assert r.stdout.startswith(f"rebuild_scores: DRY RUN at release {CUR} (make_score from THIS tree — drift "
                                   "allowed"), r.stdout
    finally:
        shutil.rmtree(b, ignore_errors=True)


def test_release_mismatch_folder_is_changed_and_gates_close():
    b = _base()
    try:
        _scored(b, "AAA", H.numbers(release=OLD), mutate=_old_record)
        r, rep = _dry(b)
        assert r.returncode == 0, r.stdout + r.stderr
        f = _f(rep, "AAA")
        assert f["state"] == "changed" and f["engine_release_run"] == OLD, f
        assert "release_mismatch" in f["reasons"] and "gate_closed" in f["reasons"], f["reasons"]
        assert f["exit_alert_eligible"] == {"before": True, "after": False}, f["exit_alert_eligible"]
        assert rep["counts"]["exit_gate_closed"] == 1 and rep["counts"]["changed"] == 1
        assert rep["drift_allowed"] is True and rep["origin_sha"] is None and f["main_sync"] == "unknown"
        assert set(f["input_hashes"]) == {"dcf_numbers.json", "judgment.json", "score.json"}
        assert "Alert gates closed by the stale-release rule: 0 entry, 1 exit" in r.stdout, r.stdout
    finally:
        shutil.rmtree(b, ignore_errors=True)


def test_misfit_notch_tier_change_is_listed():
    b = _base()
    try:
        n = H.numbers(release=OLD, tier_by_numbers="C", implied_irr_weighted=0.12, implied_irr_base=0.12,
                      fragility_flags=[FIN_FLAG])

        def legacy(s):
            _old_record(s)
            s["tier_final"] = "C"   # before 5.7 a misfit published its numbers tier
        _scored(b, "FIN", n, H.judgment(n, sector="Finance"), mutate=legacy)
        _scored(b, "AAA", H.numbers(release=OLD), mutate=_old_record)
        r, rep = _dry(b)
        assert r.returncode == 0, r.stdout + r.stderr
        f = _f(rep, "FIN")
        assert f["tier_final"] == {"before": "C", "after": "D"} and "notch_applied" in f["reasons"], f
        assert f["misfit_notch"]["after"]["applies"] is True and f["misfit_notch"]["after"]["tier_by_numbers"] == "C"
        assert rep["counts"]["tier_changes"] == 1 and rep["counts"]["notch_applied"] == 1, rep["counts"]
        assert "Tier changes (tier_final would publish differently): 1" in r.stdout, r.stdout
        line = next(x for x in r.stdout.splitlines() if x.startswith("  FIN"))
        assert "C → D  misfit notch (C by numbers)" in line and f"engine {OLD}" in line, line
    finally:
        shutil.rmtree(b, ignore_errors=True)


def test_refusal_is_reported_and_folder_kept():
    b = _base()
    try:
        _scored(b, "AAA", H.numbers(release=OLD), mutate=_old_record)
        p = os.path.join(b, "AAA", "dcf_numbers.json")
        n = json.load(open(p, encoding="utf-8"))
        n.pop("content_hash")
        json.dump(n, open(p, "w", encoding="utf-8"), indent=1)
        before = H.tree_sha(os.path.join(b, "AAA"))
        r, rep = _dry(b)
        f = _f(rep, "AAA")
        assert f["state"] == "refused" and f["refusal_kind"] == "needs_engine_rerun", f
        assert "has no content_hash" in f["refusal"], f["refusal"]
        assert rep["counts"]["refused"] == 1 and rep["counts"]["needs_engine_rerun"] == 1
        assert H.tree_sha(os.path.join(b, "AAA")) == before
        assert "1 refuse (keep their current score.json; 1 need an engine re-run)" in r.stdout, r.stdout
    finally:
        shutil.rmtree(b, ignore_errors=True)


def test_no_network_marks_a_current_release_override_folder():
    b = _base()
    try:
        n = T55._numbers(release=CUR, data_gap=["sbc"], data_gap_uncovered=[],
                         overrides_applied=[{"field": "sbc", "value": 1e6, "kind": "filing",
                                             "source": "Form 10-K FY2025 cash-flow statement", "reason": "untagged",
                                             "periods_filled": ["2025-12-31"]}])
        j = T55._judgment(n, sbc_override={"value": 1e6, "kind": "filing", "source": "Form 10-K FY2025 cash-flow statement",
                                           "reason": "SBC printed on the cash-flow statement, untagged in companyfacts"})
        H.write_folder(b, "OVR", n, j, prior_score={"ticker": "OVR", "tier_final": "B"},
                       extra={"analysis.md": "# OVR\n"})
        r, rep = _dry(b, "--no-network")
        f = _f(rep, "OVR")
        assert f["state"] == "needs_network", f
        assert f["spawned"] == ["SPAWNED_dcf_engine.py_OVR"], f
        assert rep["counts"]["needs_network"] == 1
        assert not any(x.startswith("SPAWNED") for x in os.listdir(os.path.join(b, "_system"))), \
            "the stand-ins live in the work copy, never in the base"
    finally:
        shutil.rmtree(b, ignore_errors=True)


def test_skipped_names_and_live_paused():
    b = _base()
    try:
        _queue(b, [{"ticker": "AAA", "status": "done"}, {"ticker": "PEN", "status": "pending"}])
        _scored(b, "AAA", H.numbers(release=OLD), mutate=_old_record)
        _scored(b, "PEN", H.numbers(release=OLD), mutate=_old_record)
        s = json.load(open(os.path.join(b, "AAA", "score.json"), encoding="utf-8"))
        live = {"score_json_fresh": True, "scored": {"tier_final": s["tier_final"], "tier_override_reason": None,
                                                     "dcf_content_hash": None}}
        json.dump(live, open(os.path.join(b, "AAA", "live.json"), "w", encoding="utf-8"))
        r, rep = _dry(b)
        assert _f(rep, "PEN")["state"] == "skipped" and "pending" in _f(rep, "PEN")["refusal"]
        f = _f(rep, "AAA")
        assert f["live"] == {"bound_before": True, "bound_after": False, "has_live": True,
                             "problem_after": f["live"]["problem_after"]} and f["live"]["problem_after"], f["live"]
        assert rep["counts"]["live_paused"] == 1 and rep["counts"]["live_paused_by_rebuild"] == 1, rep["counts"]
        assert "identity_stamped" in f["reasons"], f["reasons"]
        assert "Live figures paused until reprice.py --all: 1" in r.stdout, r.stdout
    finally:
        shutil.rmtree(b, ignore_errors=True)


class Sweep:
    """A sweep clone in sync with a local bare origin: _system/ holds the fail-loud stand-ins (committed, so
    preflight is in sync), the folders are committed on origin."""

    def __init__(self, tickers=("AAA", "BBB")):
        self.o = H.make_origin({"_system/dcf_engine.py": T55.FAIL_LOUD, "_system/ttm.py": T55.FAIL_LOUD,
                                "_system/overrides_registry.json": {"entries": []},
                                ".gitignore": open(os.path.join(H.ROOT, ".gitignore"), encoding="utf-8").read()})
        self.c = H.clone(self.o)
        self.root = os.path.join(self.o.root, "prroot")
        for t in tickers:
            _scored(self.c, t, H.numbers(release=OLD), mutate=_old_record)
        H.commit_in(self.c, [f"{t}/" for t in tickers] + ["_system/overrides_registry.json"], "folders")
        _queue(self.c, [{"ticker": t, "status": "done"} for t in tickers])
        self.report = os.path.join(self.o.root, "rb.json")

    def run(self, *args):
        return H.run("rebuild_scores.py", *args, base=self.c, env={"STOCKS_PR_ROOT": self.root})

    def dry(self):
        r = self.run("--json", self.report)
        assert r.returncode == 0, r.stdout + r.stderr
        return json.load(open(self.report, encoding="utf-8"))

    def apply(self, *args):
        r = self.run("--apply", "--from-report", self.report, *args)
        p = self.report + ".applied.json"
        return r, (json.load(open(p, encoding="utf-8")) if os.path.exists(p) else None)

    def close(self):
        self.o.close()


def test_apply_requires_the_report_sha_and_skips_changed_inputs():
    s = Sweep()
    try:
        rep = s.dry()
        assert rep["drift_allowed"] is False and rep["origin_sha"] == s.o.head(), rep["origin_sha"]
        assert {f["ticker"]: f["main_sync"] for f in rep["folders"]} == {"AAA": "in_sync", "BBB": "in_sync"}
        H.commit_on_origin(s.o, "README.md", "main moved\n")
        r, _ = s.apply()
        assert r.returncode == 3 and "dry-run again" in r.stdout, r.stdout
        H.git(s.c, "pull", "-q", "--ff-only")
        rep = s.dry()
        p = os.path.join(s.c, "BBB", "judgment.json")
        j = json.load(open(p, encoding="utf-8"))
        j["one_liner"] = "edited after the dry run"
        json.dump(j, open(p, "w", encoding="utf-8"), indent=1)
        r, ap = s.apply()
        assert r.returncode == 1, r.stdout + r.stderr
        st = {f["ticker"]: (f["state"], f.get("refusal")) for f in ap["folders"]}
        assert st["AAA"][0] == "rebuilt" and st["BBB"] == ("skipped", "changed since the dry run"), st
        bad = dict(json.load(open(s.report, encoding="utf-8")), drift_allowed=True)
        json.dump(bad, open(s.report, "w", encoding="utf-8"))
        r, _ = s.apply()
        assert r.returncode == 3 and "--allow-drift" in r.stdout, r.stdout
    finally:
        s.close()


def test_apply_skips_a_locked_or_in_progress_ticker():
    s = Sweep(tickers=("AAA", "BBB", "CCC"))
    try:
        s.dry()
        os.makedirs(os.path.join(s.root, ".locks"), exist_ok=True)
        json.dump({"ticker": "AAA", "holder": "agent-7", "kind": "pass1", "acquired_at": "2026-10-21T09:00:00-04:00",
                   "expires_at": "2099-01-01T00:00:00-05:00"}, open(os.path.join(s.root, ".locks", "AAA.lock.json"), "w"))
        _queue(s.c, [{"ticker": "AAA", "status": "done"}, {"ticker": "BBB", "status": "in_progress"},
                     {"ticker": "CCC", "status": "done"}])
        r, ap = s.apply()
        assert r.returncode == 1
        st = {f["ticker"]: (f["state"], f.get("refusal") or "") for f in ap["folders"]}
        assert st["AAA"][0] == "skipped" and "held by agent-7" in st["AAA"][1], st
        assert st["BBB"] == ("skipped", "queue.json status in_progress") and st["CCC"][0] == "rebuilt", st
        assert not os.path.exists(os.path.join(s.root, ".locks", "CCC.lock.json")), "apply releases its lock"
        assert os.path.exists(os.path.join(s.root, ".locks", "AAA.lock.json")), "another holder's lock is left alone"
    finally:
        s.close()


def test_apply_never_spawns_the_engine_for_stale_folders():
    s = Sweep()
    try:
        s.dry()
        r, ap = s.apply()
        assert r.returncode == 0, r.stdout + r.stderr
        assert all(f["state"] == "rebuilt" for f in ap["folders"]), ap["folders"]
        assert not [x for x in os.listdir(os.path.join(s.c, "_system")) if x.startswith("SPAWNED_")]
        assert [x["step"] for x in ap["steps"]] == ["reprice", "site"], ap["steps"]
        sc = json.load(open(os.path.join(s.c, "AAA", "score.json"), encoding="utf-8"))
        assert sc.get("dcf_content_hash") and sc["exit_alert_eligible"] is False
        assert ap["mode"] == "apply" and r.stdout.startswith(f"rebuild_scores: APPLIED at release {CUR}"), r.stdout
    finally:
        s.close()


def test_drift_refuses_without_allow_drift():
    b = _base()
    try:
        _scored(b, "AAA", H.numbers(release=OLD), mutate=_old_record)
        r = H.run("rebuild_scores.py", base=b)
        assert r.returncode == 3, r.stdout
        assert r.stdout.startswith("preflight: CANNOT VERIFY") and "--allow-drift is for development only" in r.stdout
        assert H.run("rebuild_scores.py", "--apply", base=b).returncode == 2
    finally:
        shutil.rmtree(b, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(H.run_tests(globals()))
