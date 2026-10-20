#!/usr/bin/env python3
"""make_score.py under engine release 5.6 — acquired IPR&D one-time value adjustment (Andrew, 2026-10-19).
Run: python _system/tests/test_make_score_iprd.py (or python -m pytest _system/tests). No network.

The engine records come from real offline engine runs on test_engine_iprd's synthetic filer (engine55_harness);
make_score.py runs on them as a subprocess in a temp STOCKS_BASE through test_make_score_55's Run (fail-loud
dcf_engine.py / ttm.py stand-ins, the registry redirected). Each test fails on the 5.5.0 make_score.

1. score.json carries `iprd_adjustment` (charge, per-share figure, periods, IVs and IRR before / after, tier before)
   and the score's own tier / IRR / IV fields are the engine's adjusted ones; key_numbers.md prints one line per
   period, the total and per-share charge, the IVs before → after at 15/20/25% and the weighted IRR before → after.
2. A record without the block — 5.6 output for a filer with no IPR&D expense, or 5.5.0 output rebuilt under the
   5.6.0 code — prints nothing new and gets no key; the 5.5.0 one closes both alert gates ("engine output predates
   release 5.6.0").
3. base_override basis "iprd_amortized": accepted when the engine carried it (treatment amortized_in_base, the
   one-time deduction suppressed), recorded in the registry's base_override event (basis, figures, shares,
   native_base); refused when malformed, when the run did not carry it, when it disagrees with the engine's
   record, and an amortized record without the declaration is refused as out of sync.
4. Review round: the override-impact counterfactuals run the REAL engine offline (BRIDGE stand-ins) — an amortized
   declaration beside a capex_override scores, the TTM-branch replay holds the headline's IPR&D charge
   (DCF_IPRD_HOLD), an amortized base on native_base ttm_json keeps the PR #31 TTM-leg rules; figures follow the
   engine's window (two at a 2-FY filer) and its $1 tolerance.
5. Fixer review round (2026-10-19, [ADDITION — awaiting Andrew's ratification]): judgment.json iprd_cash_flow_check
   (the worker's reading of the 10-K's cash-flow statement for an expense-basis period) is validated and must agree
   with the run; a period still awaiting it is refused; an amortized base on native_base ttm_json is refused once
   ttm.json moved after the run; key_numbers.md says "deducted" only under the one-time treatment; the registry's
   amortized base_override event names the branch its impact is measured on. The records below come from runs that
   declare the check for every expense fact (test_engine_iprd's checks=True); _score / _bridged copy the checks the
   run applied into judgment.json unless a test sets them.
6. Codex review round 2 of PR #47: the amortized base_override event records the measured one-time counterfactual
   (the final run replayed on its native base: weighted IRR, pp change, tier pair, treatment and charge), so a
   successful amortized score spawns that replay — those tests run through the real-engine stand-ins (_bridged).
"""
import copy
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SYS = os.path.dirname(HERE)
for _p in (HERE, SYS):
    if _p not in sys.path:
        sys.path.insert(0, _p)
from test_make_score_55 import Run, _judgment, _stamp  # noqa: E402
import test_engine_iprd as TI  # noqa: E402

E = TI.E
PROBS = [0.1, 0.25, 0.3, 0.25, 0.1]


def _j(**kw):
    return _judgment(None, moat_score=5, probs_used=PROBS, **kw)


def applied_checks(n):
    """The iprd_cash_flow_check entries engine record n applied (what judgment.json must still declare)."""
    blk = n.get("iprd_adjustment") or {}
    return [{"period": p["period"], "window": p["window"], "amount": p["cash_flow_check"]["amount"],
             "presentation": p["cash_flow_check"]["presentation"], "source": p["cash_flow_check"]["source"]}
            for p in blk.get("periods") or [] if isinstance(p.get("cash_flow_check"), dict)]


def _with_applied(n, j):
    j = dict(j)
    if "iprd_cash_flow_check" not in j and applied_checks(n):
        j["iprd_cash_flow_check"] = applied_checks(n)
    return j


def _score(n, j=None, prior_score=None, ttm=None):
    """make_score on a copy of engine record n (ticker rewritten to the Run folder's TST); judgment.json declares
    the cash-flow checks the run applied unless j sets iprd_cash_flow_check itself."""
    m = copy.deepcopy(n)
    m["ticker"] = "TST"
    r = Run(m, _with_applied(n, j if j is not None else _j()), prior_score=prior_score)
    if ttm is not None:
        with open(os.path.join(r.folder, "ttm.json"), "w", encoding="utf-8") as f:
            json.dump(ttm, f)
    r = r.run()
    try:
        r.result = dict(r.state(), score=r.score() if r.rc == 0 else None, key=r.key() if r.rc == 0 else None,
                        entries=r.entries())
    finally:
        r.close()
    return r


def _one_time():
    return TI._cached("ms_one", lambda: TI._ok(TI._run(TI._facts(expense={2025: 20e6}))))


def _amortized():
    def go():
        rec = TI._recurrent()
        d = TI.amortized_decl(rec)
        n = TI._ok(TI._run(TI._facts(expense={2023: 15e6, 2025: 20e6}), extra=["--base-oe-ps", repr(d["value"])],
                           judgment={"base_override": d}))
        return n, d
    return TI._cached("ms_amort", go)


def test_score_and_key_numbers_carry_the_adjustment():
    """Score and key numbers (main-agent addition): score.json iprd_adjustment and key_numbers.md's section for a
    one-time deduction ($20M FY2025 expense on 100M shares = $0.20/share, the cash-flow check says added back and
    paid in investing); tier_by_numbers / implied_irr / iv_at_15 in score.json are the adjusted figures."""
    n = _one_time()
    r = _score(n)
    assert r.rc == 0, r.err
    s, key = r.result["score"], r.result["key"]
    b = s["iprd_adjustment"]
    blk = n["iprd_adjustment"]
    assert b["treatment"] == "one_time_value_deduction" and b["total"] == 20e6 and b["charge_per_share"] == 0.2, b
    assert b["shares_denominator"] == 100e6 and b["shares_source"] == "diluted_latest"
    assert b["iv_before"] == {"15": round(blk["before"]["weighted"]["iv_at_15"], 2), "20": round(blk["before"]["weighted"]["iv_at_20"], 2),
                              "25": round(blk["before"]["weighted"]["iv_at_25"], 2)}, b["iv_before"]
    assert b["iv_after"]["15"] == s["iv_at_15"] == round(n["weighted"]["iv_at_15"], 2)
    assert b["irr_after"] == s["implied_irr"] == round(n["implied_irr_weighted"], 4)
    assert b["irr_before"] == round(blk["before"]["weighted"]["irr"], 4) and b["irr_before"] > b["irr_after"]
    assert s["tier_by_numbers"] == n["tier_by_numbers"] and b["tier_before"] == blk["tier_before"]
    assert [p["deducted"] for p in b["periods"]] == [0.0, 0.0, 20e6] or [p["deducted"] for p in b["periods"]] == [20e6], b["periods"]
    assert "## Acquired IPR&D adjustment" in key, key
    assert ("- FY2025 (2025-12-31): $20,000,000 — expense basis, tag "
            "ResearchAndDevelopmentAssetAcquiredOtherThanThroughBusinessCombinationWrittenOff; deducted $20,000,000; "
            "cash-flow check: added_back_paid_in_investing; "
            "deal and consideration: not identified by the engine — name them in analysis.md") in key, key
    assert [p.get("cash_flow_check") for p in b["periods"] if p["deducted"]] == ["added_back_paid_in_investing"], b["periods"]
    assert "- Total charge: $20,000,000 ÷ 100,000,000 shares (diluted_latest) = $0.20/share" in key, key
    bw = blk["before"]["weighted"]
    assert (f"- Weighted IV before → after: @15% ${bw['iv_at_15']:,.2f} → ${n['weighted']['iv_at_15']:,.2f} · "
            f"@20% ${bw['iv_at_20']:,.2f} → ${n['weighted']['iv_at_20']:,.2f} · "
            f"@25% ${bw['iv_at_25']:,.2f} → ${n['weighted']['iv_at_25']:,.2f}") in key, key
    assert (f"- Weighted IRR before → after: {bw['irr'] * 100:.2f}% → {n['implied_irr_weighted'] * 100:.2f}%") in key, key
    assert not [e for e in r.result["entries"] if "iprd" in json.dumps(e)], r.result["entries"]   # mechanical: no registry event


def test_record_without_the_block_prints_nothing_new():
    """Release handling (main-agent addition): 5.6 output with no IPR&D expense (iprd_adjustment null) gets no score key and no key_numbers section, and
    scores on the current release (gates as before)."""
    n = TI._plain()
    assert n["iprd_adjustment"] is None
    r = _score(n)
    assert r.rc == 0, r.err
    assert "iprd_adjustment" not in r.result["score"] and "Acquired IPR&D" not in r.result["key"]
    assert "predates release" not in json.dumps(r.result["score"])


def test_55_output_rebuilt_under_56_closes_the_gates_and_prints_nothing_new():
    """Release handling (main-agent addition): 5.5.0 output (no block) rebuilt by the 5.6.0 make_score is another release — both
    alert gates closed with "engine output predates release 5.6.0", predates_55 stays False (no ADS correction), no
    iprd key or section."""
    import make_score as M
    n = copy.deepcopy(TI._plain())
    n.pop("iprd_adjustment")
    n["engine_release"] = "5.5.0"
    assert not M.predates_55(n) and not M.predates_55({"engine_release": "5.6.0", "market_cap_basis": {}})
    assert M.release_tuple("5.6.0") == (5, 6, 0) > M.release_tuple("5.5.0")
    assert M.release_mismatch_reason("5.5.0") == "engine output predates release 5.6.0"
    r = _score(n)
    assert r.rc == 0, r.err
    s = r.result["score"]
    assert "iprd_adjustment" not in s and "Acquired IPR&D" not in r.result["key"]
    gate = s.get("alert_suppressed_reason") or s.get("exit_alert_suppressed_reason") or ""
    assert s["alert_eligible"] is False and s["exit_alert_eligible"] is False, s
    assert "engine output predates release 5.6.0" in gate, gate


def test_iprd_amortized_declaration_is_accepted_and_registered():
    """Amortized path (main-agent addition): the engine's amortized_in_base record with its matching iprd_amortized
    declaration scores: no one-time deduction (charge 0), key_numbers.md prints the amortized construction and
    never says a period was "deducted" ([fixer review round]: each FY charge is "counted in the amortization
    mean"), and the registry base_override event (a judgment call) carries basis, figures, shares, native_base,
    the native -> pinned base and base_used "declared_pin" (a median native base)."""
    n, d = _amortized()
    # [Codex review r2] the event's one-time counterfactual is replayed through the real engine (_bridged)
    r = _bridged(n, _j(base_override=d), TI._facts(expense={2023: 15e6, 2025: 20e6}))
    assert r.rc == 0, r.err
    s = r.result["score"]
    assert s["iprd_adjustment"]["treatment"] == "amortized_in_base" and "iv_before" not in s["iprd_adjustment"]
    assert s["iprd_adjustment"]["amortized"]["figures"] == [15e6, 0.0, 20e6]
    key = r.result["key"]
    assert "- Amortized in the base (iprd_amortized base_override): native base" in key, key
    sec = key[key.index("## Acquired IPR&D adjustment"):]
    assert "deducted $" not in sec and "(deducted, no flag)" not in sec, sec
    assert "- FY2023 (2023-12-31): $15,000,000 — expense basis, tag " in sec and "counted in the amortization mean $15,000,000" in sec, sec
    assert "(treatment amortized_in_base: no one-time deduction)" in sec, sec
    ev = [e for e in r.result["entries"] if e.get("event") == "base_override"]
    assert len(ev) == 1, r.result["entries"]
    ev = ev[0]
    assert (ev["basis"], ev["figures"], ev["shares"], ev["native_base"]) == ("iprd_amortized", [15e6, 0.0, 20e6], 1e8,
                                                                            "median_of_last_3_fy_oe_per_share"), ev
    assert ev["base_oe_with_override"] == round(d["value"], 4) and ev["base_oe_without_override"] == round(
        n["iprd_adjustment"]["amortized"]["native_base_per_share"], 4), ev
    assert ev["base_used"] == "declared_pin", ev


def test_iprd_amortized_declaration_malformed_or_out_of_sync_is_refused():
    """Amortized path (main-agent addition): make_score refuses a malformed iprd_amortized declaration (figures not two or three non-negative numbers, a bad
    native_base, kind estimate, a misspelt basis), one the run did not carry (a one-time run with the declaration
    added afterwards), one that disagrees with the engine's record, and an amortized record whose judgment no
    longer declares it."""
    n, d = _amortized()
    for over, needle in (({"figures": [15e6, 20e6]}, "disagrees with the engine's record"),   # a 2-FY shape, not this run's
                         ({"figures": [15e6, -1.0, 20e6]}, "figures must list the last-3-FY window"),
                         ({"figures": [15e6, 0.0, 20e6, 1.0]}, "figures must list the last-3-FY window"),
                         ({"native_base": "latest_fy"}, "native_base must be one of"),
                         ({"kind": "estimate"}, "must have kind 'filing'"),
                         ({"basis": "iprd_amortised"}, "base_override.basis must be"),
                         ({"shares": 99e6}, "disagrees with the engine's record")):
        bad = dict(d, **over)
        r = _score(n, _j(base_override=bad))
        assert r.rc == 1 and needle in r.err, (over, r.rc, r.err[-500:])
    one = _one_time()
    r = _score(one, _j(base_override=dict(d, value=one["base_oe_per_share"])))
    assert r.rc == 1 and "did not carry it" in r.err, r.err[-500:]
    r = _score(n, _j(base_override={k: v for k, v in d.items() if k not in ("basis", "figures", "shares", "native_base")}))
    assert r.rc == 1 and "out of sync" in r.err, r.err[-500:]


def test_period_awaiting_the_cash_flow_check_is_refused():
    """[fixer review round] A record whose expense-basis period still awaits the cash-flow check
    (ACQUIRED_IPRD_UNCONFIRMED — NBIX's shape, no check declared) is refused: the value is unknown until the worker
    declares what the 10-K's cash-flow statement shows. With the check declared "inside_operating_cash_flow" the
    run scores untouched (no deduction, no flag)."""
    facts = TI._facts(expense={2025: 20e6})
    n = TI._ok(TI._run(facts, checks=False))
    assert n["iprd_adjustment"]["treatment"] == "awaiting_cash_flow_check"
    r = _score(n)
    assert r.rc == 1 and "ACQUIRED_IPRD_UNCONFIRMED" in r.err and "FY2025 $20,000,000" in r.err and "iprd_cash_flow_check" in r.err, r.err[-600:]
    chk = [dict(c, presentation="inside_operating_cash_flow") for c in TI.auto_checks(facts)]
    m = TI._ok(TI._run(facts, judgment={"iprd_cash_flow_check": chk}))
    r = _score(m, _j(iprd_cash_flow_check=chk))
    assert r.rc == 0, r.err[-600:]
    s = r.result["score"]
    assert s["iprd_adjustment"]["periods"][-1]["excluded"] == "paid_in_operating_cash_flow" and s["iprd_adjustment"]["total"] == 0.0
    assert s["implied_irr"] == round(TI._plain()["implied_irr_weighted"], 4)


def test_cash_flow_check_out_of_sync_or_malformed_is_refused():
    """[fixer review round] judgment.json iprd_cash_flow_check must be well formed and agree with the run: a check
    the run applied that judgment.json no longer declares, or declares with another presentation / source, is out of
    sync; a declared amount that is not the filed expense (so the run left the period awaiting or unapplied) is
    refused (named in the refusal); malformed entries (bad presentation, no source, a zero amount, a duplicate period) are refused."""
    n = _one_time()
    good = applied_checks(n)
    assert len(good) == 1
    for j, needle in ((_j(iprd_cash_flow_check=[dict(good[0], presentation="paid_in_shares")]), "now declares differently"),
                      (_j(iprd_cash_flow_check=[dict(good[0], source="another line")]), "now declares differently"),
                      (_j(iprd_cash_flow_check=[dict(good[0], presentation="added_back")]), "is malformed"),
                      (_j(iprd_cash_flow_check=[dict(good[0], source=" ")]), "is malformed"),
                      (_j(iprd_cash_flow_check=[dict(good[0], amount=0)]), "is malformed"),
                      (_j(iprd_cash_flow_check=[good[0], dict(good[0])]), "twice"),
                      (_j(iprd_cash_flow_check=[]), "non-empty list")):
        r = _score(n, j)
        assert r.rc == 1 and needle in r.err, (j.get("iprd_cash_flow_check"), r.err[-500:])
    # the run applied a check judgment.json dropped
    r = _score(n, dict(_j(), iprd_cash_flow_check=[dict(good[0], period="2024-12-31")]))
    assert r.rc == 1 and "no longer declares" in r.err, r.err[-500:]
    # a declared amount that is not the filed expense: the run left the period awaiting
    facts = TI._facts(expense={2025: 20e6})
    bad = [dict(c, amount=19e6) for c in TI.auto_checks(facts)]
    m = TI._ok(TI._run(facts, judgment={"iprd_cash_flow_check": bad}))
    r = _score(m, _j(iprd_cash_flow_check=bad))
    assert r.rc == 1 and "ACQUIRED_IPRD_UNCONFIRMED" in r.err and "FY2025 declared $19,000,000" in r.err, r.err[-500:]


# ===========================================================================
# Review round (2026-10-19): override-impact counterfactuals, the TTM-native amortized base, figure tolerance
# ===========================================================================
# A stand-in pair for the counterfactual runs make_score spawns: dcf_engine.py runs the REAL engine offline on the
# synthetic fixture (engine55_harness, the Run folder's judgment.json / ttm.json); ttm.py answers the no-override
# run with a canned TTM base. Every spawn is logged with its argv, DCF_NO_OVERRIDES and DCF_IPRD_HOLD.
BRIDGE = r'''import json, os, sys
here = os.path.dirname(os.path.abspath(__file__))
cfg = json.load(open(os.path.join(here, "bridge.json"), encoding="utf-8"))
with open(os.path.join(here, "SPAWNED_" + os.path.basename(__file__) + ".txt"), "a", encoding="utf-8") as f:
    f.write(json.dumps({"argv": sys.argv[1:], "no_overrides": os.environ.get("DCF_NO_OVERRIDES"),
                        "hold": os.environ.get("DCF_IPRD_HOLD")}) + "\n")
if os.path.basename(__file__) == "ttm.py":
    if not os.environ.get("DCF_NO_OVERRIDES") or cfg.get("ttm_no_override") is None:
        sys.exit(97)
    print(json.dumps(cfg["ttm_no_override"]))
    sys.exit(0)
sys.path[:0] = cfg["paths"]
import engine55_harness as H
folder = os.path.join(os.path.dirname(here), "TST")
def _load(name):
    try:
        return json.load(open(os.path.join(folder, name), encoding="utf-8"))
    except Exception:
        return None
fx = cfg["fixture"]
base = H.make_base(fx, _load("judgment.json") or {}, _load("ttm.json"), copy_repo_files=False)
out = H.run_engine(fx["ticker"], args=[a for a in sys.argv[2:] if a != "--measure"], base=base, fixture=fx,
                   measure="--measure" in sys.argv)
sys.stdout.write(out["stdout"])
sys.exit(out["exit"] or 0)
'''


def _bridged(n, j, facts, ttm=None, ttm_no_override=None):
    """make_score on engine record n with the real-engine stand-ins; returns the closed Run with its outputs and
    the logged spawns."""
    m = copy.deepcopy(n)
    m["ticker"] = "TST"
    run = Run(m, _with_applied(n, j))
    for name in ("dcf_engine.py", "ttm.py"):
        with open(os.path.join(run.sysdir, name), "w", encoding="utf-8") as f:
            f.write(BRIDGE)
    with open(os.path.join(run.sysdir, "bridge.json"), "w", encoding="utf-8") as f:
        json.dump({"paths": [HERE, SYS], "fixture": TI._syn_fixture(facts, 30.0), "ttm_no_override": ttm_no_override}, f)
    if ttm is not None:
        with open(os.path.join(run.folder, "ttm.json"), "w", encoding="utf-8") as f:
            json.dump(ttm, f)
    try:
        run.run()
        spawns = []
        for name in run.spawned():
            with open(os.path.join(run.sysdir, name), encoding="utf-8") as f:
                spawns += [dict(json.loads(line), script=name) for line in f if line.strip()]
        run.result = dict(run.state(), score=run.score() if run.rc == 0 else None, key=run.key() if run.rc == 0 else None,
                          entries=run.entries(), spawns=spawns)
    finally:
        run.close()
    return run


SBC_SRC = "Last filed SBC: FY2025 ShareBasedCompensation $10,000,000 (Form 10-K FY2025)"


def _ttm_with_sbc_legs(per_share, shares):
    """ttm.json whose YTD SBC legs only an sbc_override estimate fills (APA's shape, test_make_score_55)."""
    t = TI._ttm_doc(per_share, shares)
    t["overrides_used"] = [{"field": "sbc", "value": 10e6, "kind": "estimate", "source": SBC_SRC,
                            "legs_filled": {"ytd_prior": {"period": ["2025-01-01", "2025-06-30"], "amount": 5e6},
                                            "ytd_current": {"period": ["2026-01-01", "2026-06-30"], "amount": 5e6}}}]
    return t


SBC_OVERRIDE = {"value": 10e6, "kind": "estimate", "source": SBC_SRC, "reason": "test: the 10-Qs print no SBC line"}


def test_amortized_declaration_beside_a_capex_override_scores_end_to_end():
    """[review] An iprd_amortized declaration (median native base) at a filer whose FY2024 capex only a
    capex_override fills: make_score's declared-pin counterfactual replays the pin with the overrides off and must
    score (before the fix the engine re-validated the declaration against the moved no-override median, exited 3,
    and make_score refused "counterfactual engine --measure run failed"); the replay carries DCF_IPRD_HOLD with the
    final run's treatment (amortized_in_base, charge 0)."""
    facts = TI._facts(expense={2023: 15e6, 2025: 20e6}, capex={2024: None})
    J = {"capex_override": TI._o(80e6)}
    rec = TI._ok(TI._run_env(facts, judgment=J))
    d = TI.amortized_decl(rec)
    n = TI._ok(TI._run_env(facts, ["--base-oe-ps", repr(d["value"])], dict(J, base_override=d)))
    assert n["iprd_adjustment"]["treatment"] == "amortized_in_base"
    r = _bridged(n, _j(base_override=d, capex_override=J["capex_override"]), facts)
    assert r.rc == 0, r.err[-800:]
    oi = r.result["score"]["override_impact"]
    assert oi["base_used"] == "declared_pin" and isinstance(oi["weighted_irr_without_override"], float), oi
    cf = [s for s in r.result["spawns"] if s["script"].endswith("dcf_engine.py.txt") and s["no_overrides"]]
    assert len(cf) == 1 and json.loads(cf[0]["hold"]) == {"treatment": "amortized_in_base", "charge_per_share": 0.0}, cf


def test_ttm_counterfactual_holds_the_headline_charge():
    """[review] A --ttm run (FY2025 $20M + 2026 H1 $30M on ttm.json's 98M shares = $0.5102/share) whose TTM SBC legs
    an override fills: the TTM-branch counterfactual replays the no-override TTM base ($2.00) through --base-oe-ps
    and must carry the headline's charge (DCF_IPRD_HOLD) — its IRR is the engine's with the held charge, not the
    $0.20/share an FY-window replay would deduct, so weighted_irr_impact_pp measures the override alone."""
    facts = TI._ttm_ytd_facts()
    ttm = _ttm_with_sbc_legs(2.1, 98e6)
    J = {"sbc_override": SBC_OVERRIDE}
    n = TI._ok(TI._run_env(facts, ["--ttm"], J, ttm=ttm))
    c = E.iprd_charge_per_share(n)
    assert c == 50e6 / 98e6
    r = _bridged(n, _j(sbc_override=SBC_OVERRIDE), facts, ttm=ttm,
                 ttm_no_override={"ttm_oe_per_share": 2.0, "ttm_oe_total": 196e6, "ttm_shares_diluted": 98e6})
    assert r.rc == 0, r.err[-800:]
    oi = r.result["score"]["override_impact"]
    hold = json.dumps({"treatment": "one_time_value_deduction", "charge_per_share": c})
    held = TI._run_env(facts, ["--base-oe-ps", "2.0"], J, ttm=ttm, env={"DCF_NO_OVERRIDES": "1", "DCF_IPRD_HOLD": hold},
                       measure=True)["numbers"]
    unheld = TI._run_env(facts, ["--base-oe-ps", "2.0"], J, ttm=ttm, env={"DCF_NO_OVERRIDES": "1"}, measure=True)["numbers"]
    assert oi["base_used"] == "ttm" and oi["base_oe_without_override"] == 2.0, oi
    assert oi["weighted_irr_without_override"] == round(held["implied_irr_weighted"], 4), (oi, held["implied_irr_weighted"])
    assert round(unheld["implied_irr_weighted"], 4) != oi["weighted_irr_without_override"]
    cf = [s for s in r.result["spawns"] if s["script"].endswith("dcf_engine.py.txt") and s["no_overrides"]]
    assert len(cf) == 1 and json.loads(cf[0]["hold"]) == json.loads(hold), cf


def test_amortized_ttm_native_base_keeps_the_ttm_leg_rules():
    """[review] An iprd_amortized base on native_base ttm_json IS ttm.json's TTM base less the amortization, so the
    PR #31 TTM-leg rules hold: the sbc_override that fills ttm.py's YTD legs is reported (scope ttm_legs), measured
    on the TTM branch (the no-override TTM base $2.00 less the same $0.1167 amortization, replayed with the amortized
    treatment held), and a ttm.json override judgment.json no longer declares refuses. Before the fix the pin was
    compared with ttm.json's figure, nothing was reported and the stale ttm.json was accepted."""
    facts = TI._facts(expense={2023: 15e6, 2025: 20e6})
    ttm = _ttm_with_sbc_legs(2.1, 100e6)
    figs = [15e6, 0.0, 20e6]
    val = 2.1 - sum(figs) / 3 / 100e6
    d = {"basis": "iprd_amortized", "kind": "filing", "native_base": "ttm_json", "figures": figs, "shares": 100e6,
         "value": val, "source": "this run's dcf_numbers.json iprd_adjustment and ttm.json", "reason": "test: recurrent"}
    J = {"sbc_override": SBC_OVERRIDE, "base_override": d}
    n = TI._ok(TI._run_env(facts, ["--base-oe-ps", repr(val)], J, ttm=ttm))
    assert n["iprd_adjustment"]["treatment"] == "amortized_in_base"
    no_ovr = {"ttm_oe_per_share": 2.0, "ttm_oe_total": 200e6, "ttm_shares_diluted": 100e6}
    r = _bridged(n, _j(**J), facts, ttm=ttm, ttm_no_override=no_ovr)
    assert r.rc == 0, r.err[-800:]
    s = r.result["score"]
    assert [(o["field"], o.get("scope")) for o in s.get("overrides") or []] == [("sbc", "ttm_legs")], s.get("overrides")
    oi = s["override_impact"]
    assert oi["base_used"] == "ttm" and oi["base_oe_without_override"] == round(2.0 - (2.1 - val), 4), oi
    cf = [x for x in r.result["spawns"] if x["script"].endswith("dcf_engine.py.txt") and x["no_overrides"]]
    assert len(cf) == 1 and json.loads(cf[0]["hold"]) == {"treatment": "amortized_in_base", "charge_per_share": 0.0}, cf
    # [fixer review round] the registry event names the branch the impact is measured on (the field override's too)
    ev = [e for e in r.result["entries"] if e.get("event") == "base_override"]
    assert len(ev) == 1 and ev[0]["base_used"] == "ttm" == oi["base_used"], ev
    r = _bridged(n, _j(base_override=d), facts, ttm=ttm, ttm_no_override=no_ovr)
    assert r.rc == 1 and "no longer declares one" in r.err, r.err[-600:]
    # [fixer review round] ttm.py re-saved after the run (a new 10-Q): the stale amortized base is refused, with or
    # without the TTM-leg override (before the fix both scored the old base and silently dropped the override)
    for t2 in (TI._ttm_doc(7.0, 100e6), _ttm_with_sbc_legs(7.0, 100e6), _ttm_with_sbc_legs(2.1, 101e6)):
        r = _bridged(n, _j(**J), facts, ttm=t2, ttm_no_override=no_ovr)
        assert r.rc == 1 and "ttm.json changed after the engine run" in r.err, (t2["ttm_oe_per_share"], r.err[-600:])


def test_iprd_amortized_figures_follow_the_engine_window_and_tolerance():
    """[review] make_score agrees with the engine on what a valid declaration is: a filer with only two FY has a
    two-figure window (two figures pass validate_base_override; one or four do not), and figures are compared
    with the engine's own $1 tolerance (an FX-converted charge such as 12,345,678.912345 declared as 12,345,679 is
    the engine-accepted declaration), not float equality."""
    import make_score as M

    def refused(fn, *a):
        try:
            fn(*a)
        except SystemExit as e:
            return e.code == 1
        return False
    base = {"basis": "iprd_amortized", "kind": "filing", "native_base": "median_of_last_3_fy_oe_per_share",
            "shares": 1e8, "value": 1.5, "source": "s", "reason": "r"}
    assert M.validate_base_override({"base_override": dict(base, figures=[1e7, 2e7])})["figures"] == [1e7, 2e7]
    assert M.validate_base_override({"base_override": dict(base, figures=[1e7, 0, 2e7])})
    for figs in ([1e7], [1e7, 0, 2e7, 3e7]):
        assert refused(M.validate_base_override, {"base_override": dict(base, figures=figs)}), figs
    rec = [12345678.912345, 0.0, 5000000.5]
    n = {"inputs": {"base_oe_ps_arg": 1.5, "base_pin_source": "base_oe_ps_arg"},
         "iprd_adjustment": {"treatment": "amortized_in_base",
                             "amortized": {"expected_value": 1.5, "figures": rec, "shares": 1e8,
                                           "native_base": "median_of_last_3_fy_oe_per_share"}}}
    assert M.check_iprd_amortized(n, dict(base, figures=[12345679, 0, 5000000])) is None
    assert refused(M.check_iprd_amortized, n, dict(base, figures=[12345681, 0, 5000000]))
    assert refused(M.check_iprd_amortized, n, dict(base, figures=[12345679, 0]))

# ===========================================================================
# Deferred payments of an earlier deal (Andrew's 2026-10-20 ruling, delegated to the main agent, who decided)
# ===========================================================================
def _deferred_run(key, entries):
    facts = TI._facts(expense={2023: 15e6, 2025: 20e6})
    return TI._cached(key, lambda: TI._ok(TI._run(facts, judgment={"iprd_deferred_payment": entries})))


def test_deferred_payment_scores_and_shows_the_excluded_period():
    """judgment.json iprd_deferred_payment declaring FY2025's whole $20M charge the FY2023 deal's milestone: the
    record scores; score.json iprd_adjustment carries recurrence_excluded (the excluded period, its deal and first
    charge) and the period's deferred_payment_of; key_numbers.md says on the period line and on its own line that
    FY2025 is excluded from the recurrence count but still deducted; recurrent is false; [Codex review r8] the
    registry gains one iprd_deferred_payment event for the deal (its lifetime record) and nothing else IPR&D."""
    d = TI.deferred()
    n = _deferred_run("ms_def_whole", [d])
    r = _score(n, _j(iprd_deferred_payment=[d]))
    assert r.rc == 0, r.err[-800:]
    b = r.result["score"]["iprd_adjustment"]
    assert b["recurrent"] is False and b["total"] == 35e6, b
    assert b["recurrence_excluded"] == [{"period": "2025-12-31", "window": "fy", "deal": "Test Bio",
                                         "first_charged_period": "2023-12-31", "amount": 20e6}], b
    p25 = [p for p in b["periods"] if p["period"] == "2025-12-31"][0]
    assert p25["recurrence_excluded"] == "deferred_payment_of" and p25["deducted"] == 20e6, p25
    assert p25["deferred_payment_of"] == [{"deal": "Test Bio", "first_charged_period": "2023-12-31", "amount": 20e6}], p25
    key = r.result["key"]
    assert ("; deducted $20,000,000; cash-flow check: added_back_paid_in_investing; deferred payment of Test Bio "
            "($20,000,000, first charged 2023-12-31): excluded from the recurrence count") in key, key
    assert ("- Excluded from the recurrence count (judgment.json iprd_deferred_payment — a deferred payment of a deal "
            "first charged earlier; still deducted): FY2025 $20,000,000 — Test Bio, first charged 2023-12-31") in key, key
    assert "recurrent (ACQUIRED_IPRD_RECURRENT)" not in key
    iprd_entries = [e for e in r.result["entries"] if "iprd" in json.dumps(e)]
    assert [(e.get("event"), e.get("deal"), e.get("paid_to_date"), e.get("periods")) for e in iprd_entries] == [
        ("iprd_deferred_payment", "Test Bio", 20e6, [{"period": "2025-12-31", "amount": 20e6}])], iprd_entries


def test_partly_deferred_period_is_shown_and_still_counts():
    """A partly deferred FY2025 ($5M of $20M): key_numbers.md says it still counts toward recurrence, score.json
    records the declaration (whole: false) and an empty recurrence_excluded list; recurrent stays true."""
    d = TI.deferred(amount=5e6)
    n = _deferred_run("ms_def_part", [d])
    r = _score(n, _j(iprd_deferred_payment=[d]))
    assert r.rc == 0, r.err[-800:]
    b = r.result["score"]["iprd_adjustment"]
    assert b["recurrent"] is True and b["recurrence_excluded"] == [], b
    p25 = [p for p in b["periods"] if p["period"] == "2025-12-31"][0]
    assert [x["amount"] for x in p25["deferred_payment_of"]] == [5e6] and "recurrence_excluded" not in p25, p25
    assert ("partly a deferred payment of Test Bio ($5,000,000, first charged 2023-12-31) — $5,000,000 of "
            "$20,000,000: still counts toward recurrence") in r.result["key"], r.result["key"]


def test_deferred_declaration_malformed_or_out_of_sync_is_refused():
    """make_score refuses a malformed iprd_deferred_payment (no deal, no accession in the source, an empty list, a
    period declared twice), a declaration the run did not apply (judgment.json changed after the run — the run
    then still counts the period), one now declared differently, and an applied one judgment.json dropped."""
    d = TI.deferred()
    n = _deferred_run("ms_def_whole", [d])
    bad_deal = dict(d, deferred_payment_of=dict(d["deferred_payment_of"], deal=""))
    bad_src = dict(d, deferred_payment_of=dict(d["deferred_payment_of"], source="Note 5"))
    for entries, needle in (([bad_deal], "is malformed"), ([bad_src], "is malformed"), ([], "non-empty list"),
                            ([d, dict(d)], "twice"),
                            ([dict(d, amount=19e6)], "now declares differently"),
                            ([dict(d, deferred_payment_of=dict(d["deferred_payment_of"], first_charged_period="2022-12-31"))],
                             "now declares differently"),
                            ([dict(d, deferred_payment_of=dict(d["deferred_payment_of"], deal="Other Bio"))],
                             "no longer declares")):
        r = _score(n, _j(iprd_deferred_payment=entries))
        assert r.rc == 1 and needle in r.err, (entries, r.err[-600:])
    r = _score(n, _j())
    assert r.rc == 1 and "no longer declares" in r.err, r.err[-600:]
    r = _score(TI._recurrent(), _j(iprd_deferred_payment=[d]))
    assert r.rc == 1 and "did not apply" in r.err, r.err[-600:]


def test_halo_score_and_key_numbers_are_unchanged():
    """HALO's committed record (no deferred payment declared): validate / check accept its judgment.json, and the
    score.json block and the key_numbers.md section make_score builds from its dcf_numbers.json are the committed
    ones, unchanged by the deferred-payment rule."""
    import make_score as M
    root = os.path.dirname(SYS)
    rd = lambda f: open(os.path.join(root, "HALO", f), encoding="utf-8").read()
    rec, j, score = json.loads(rd("dcf_numbers.json")), json.loads(rd("judgment.json")), json.loads(rd("score.json"))
    assert M.validate_iprd_deferred_payment(j) is None
    assert M.check_iprd_deferred_payment(rec, None) is None
    assert M.iprd_score_block(rec) == score["iprd_adjustment"]
    lines = M.iprd_lines(rec)
    key = rd("key_numbers.md").splitlines()
    start = key.index(lines[1])
    assert key[start - 1:start - 1 + len(lines)] == lines, (lines, key[start - 1:start - 1 + len(lines)])
    assert not any("recurrence" in x for x in lines), lines


# --- Codex review of the deferred-payment rule (fixes amended into the follow-up commit) -------------------------
def test_two_deal_period_scores_and_prints_both_deals():
    """[Codex review, finding 7] FY2025's $20M declared as a $12M Test Bio milestone (first charged FY2023) plus an
    $8M Other Bio milestone (first charged FY2021): make_score accepts two entries for one period with distinct
    deals, score.json lists both (period and block), key_numbers.md prints both on the period line and in the
    excluded-periods line, by first-charge date (not a calendar-year FY label), and recurrent is false."""
    tb = TI.deferred(amount=12e6)
    ob = TI.deferred(amount=8e6, deal="Other Bio", first="2021-12-31", source=TI.OK_SRC_2021)
    facts = TI._facts(expense={2021: 8e6, 2023: 15e6, 2025: 20e6})
    n = TI._cached("ms_def_two", lambda: TI._ok(TI._run(facts, judgment={"iprd_deferred_payment": [tb, ob]})))
    r = _score(n, _j(iprd_deferred_payment=[tb, ob]))
    assert r.rc == 0, r.err[-800:]
    b = r.result["score"]["iprd_adjustment"]
    assert b["recurrent"] is False, b
    assert [(x["deal"], x["amount"]) for x in b["recurrence_excluded"]] == [("Test Bio", 12e6), ("Other Bio", 8e6)], b
    p25 = [p for p in b["periods"] if p["period"] == "2025-12-31"][0]
    assert p25["deferred_payment_of"] == [{"deal": "Test Bio", "first_charged_period": "2023-12-31", "amount": 12e6},
                                          {"deal": "Other Bio", "first_charged_period": "2021-12-31", "amount": 8e6}], p25
    key = r.result["key"]
    assert ("deferred payment of Test Bio ($12,000,000, first charged 2023-12-31) and Other Bio ($8,000,000, first "
            "charged 2021-12-31): excluded from the recurrence count") in key, key
    assert ("FY2025 $12,000,000 — Test Bio, first charged 2023-12-31; FY2025 $8,000,000 — Other Bio, first charged "
            "2021-12-31") in key, key
    # judgment.json now declaring only one of the two is out of sync
    r = _score(n, _j(iprd_deferred_payment=[tb]))
    assert r.rc == 1 and "no longer declares" in r.err, r.err[-600:]


def test_validate_deferred_refuses_a_ytd_window_and_one_deal_twice_in_a_period():
    """[Codex review, findings 4, 6 and 7] make_score's shape check matches the engine's: window ttm_current_ytd is
    malformed (the recurrence count is FY-only); two entries for one period with distinct deals pass; the same deal
    twice in one period (in any letter case) is refused."""
    import make_score as M
    d = TI.deferred()
    for bad, needle in (([dict(d, window="ttm_current_ytd", period="2026-06-30")], "is malformed"),
                        ([d, dict(d, amount=1e6, deferred_payment_of=dict(d["deferred_payment_of"], deal=" test BIO"))],
                         "twice")):
        try:
            M.validate_iprd_deferred_payment({"iprd_deferred_payment": bad})
        except SystemExit:
            continue
        raise AssertionError(f"accepted {bad!r} ({needle})")
    two = [d, dict(d, amount=1e6, deferred_payment_of=dict(d["deferred_payment_of"], deal="Other Bio"))]
    assert M.validate_iprd_deferred_payment({"iprd_deferred_payment": two}) == two


def test_rolled_out_declaration_stays_declared_and_scores():
    """[Codex review r4, #4322408940] (was: test_rolled_out_declaration_is_asked_to_be_dropped) The engine lists an
    entry whose period is older than its window in deferred_payments_rolled_out (exit 0). make_score used to refuse
    the score until the entry was DELETED — the deletion that let a later declaration take the deal past its
    contingent_total. The entry now stays declared: make_score scores with judgment.json carrying it. Out of sync
    either way is refused: a rolled-out entry the run did not list (judgment.json changed after the run), or one the
    run listed that judgment.json dropped (it counts toward the deal's lifetime cap: never delete it). [Codex review
    r7] The filer carries Old Bio's FY2021 first charge in companyfacts: a rolled-out entry is validated like any."""
    old = TI.deferred(period="2022-12-31", amount=5e6, first="2021-12-31", source=TI.OK_SRC_2021, deal="Old Bio")
    d = TI.deferred()
    n = TI._cached("ms_def_old", lambda: TI._ok(TI._run(TI._facts(expense={2021: 8e6, 2023: 15e6, 2025: 20e6}),
                                                         judgment={"iprd_deferred_payment": [d, old]})))
    r = _score(n, _j(iprd_deferred_payment=[d, old]))
    assert r.rc == 0, r.err[-800:]
    # [Codex review r5 of PR #47] key_numbers.md shows the rolled-out entry beside the window's charge
    assert "Rolled out of the window" in r.result["key"] and "Old Bio" in r.result["key"], r.result["key"][-1500:]
    r = _score(n, _j(iprd_deferred_payment=[d]))
    assert r.rc == 1 and "rolled-out" in r.err and "contingent_total" in r.err, r.err[-600:]
    other = TI.deferred(period="2021-12-31", amount=1e6, first="2020-12-31", source=TI.OK_SRC_2021, deal="Other Bio")
    r = _score(n, _j(iprd_deferred_payment=[d, old, other]))
    assert r.rc == 1 and "did not apply" in r.err, r.err[-600:]



def test_rolled_out_entry_scores_when_the_window_has_no_iprd_charge():
    """[Codex review r5 of PR #47, #4322641225] A window with no acquired-IPR&D charge used to drop the rolled-out
    list (null block), so make_score refused the kept entry ("did not apply") and scored only once it was deleted —
    freeing the deal's lifetime contingent_total cap. Now the run records the entry and scores with it kept; deleting
    it is refused. score.json gains no iprd_adjustment (no charge, nothing to show on the site); key_numbers.md lists
    the rolled-out entry and no charge line."""
    facts, old, _ = TI._rolled_only_case()
    n = TI._cached("ms_def_rolled_only", lambda: TI._ok(TI._run(facts, judgment={"iprd_deferred_payment": [old]})))
    r = _score(n, _j(iprd_deferred_payment=[old]))
    assert r.rc == 0, r.err[-800:]
    assert "iprd_adjustment" not in r.result["score"], r.result["score"].get("iprd_adjustment")
    key = r.result["key"]
    assert "Acquired IPR&D" in key and "Rolled out of the window" in key and "Old Bio" in key, key[-1500:]
    assert "Total charge" not in key and "Treatment:" not in key, key[-1500:]
    r = _score(n, _j())
    assert r.rc == 1 and "rolled-out" in r.err and "contingent_total" in r.err, r.err[-600:]


# --- the per-deal cap (the main agent's decision on the review's open item, delegated by Andrew 2026-10-20) --------
def test_validate_deferred_refuses_a_missing_or_inconsistent_contingent_total_or_amounts_past_it():
    """make_score's shape check matches the engine's cap: an entry without contingent_total is malformed; one deal
    declaring two contingent_total values, or amounts summing past its contingent_total across the entries, is
    refused; a record whose applied contingent_total differs from judgment.json's is out of sync."""
    import make_score as M
    d = TI.deferred()
    dd = d["deferred_payment_of"]
    no_cap = dict(d, deferred_payment_of={k: v for k, v in dd.items() if k != "contingent_total"})
    other = dict(d, period="2024-12-31", amount=1e6,
                 deferred_payment_of=dict(dd, contingent_total={"value": 2e9, "source": TI.CT_SRC}))
    small = {"value": 15e6, "source": TI.CT_SRC}
    over = [dict(d, amount=10e6, deferred_payment_of=dict(dd, contingent_total=small)),
            dict(d, period="2024-12-31", amount=6e6, deferred_payment_of=dict(dd, contingent_total=small))]
    for bad, needle in (([no_cap], "is malformed"), ([d, other], "one deal has one contingent_total"),
                        (over, "more than its contingent_total")):
        try:
            M.validate_iprd_deferred_payment({"iprd_deferred_payment": bad})
        except SystemExit:
            continue
        raise AssertionError(f"accepted {bad!r} ({needle})")
    n = _deferred_run("ms_def_whole", [d])
    r = _score(n, _j(iprd_deferred_payment=[no_cap]))
    assert r.rc == 1 and "is malformed" in r.err and "contingent_total" in r.err, r.err[-600:]
    recap = dict(d, deferred_payment_of=dict(dd, contingent_total={"value": 2e9, "source": TI.CT_SRC}))
    r = _score(n, _j(iprd_deferred_payment=[recap]))
    assert r.rc == 1 and "now declares differently" in r.err, r.err[-600:]
    r = _score(n, _j(iprd_deferred_payment=[d]))
    assert r.rc == 0, r.err[-800:]


# ===========================================================================
# Codex review round 1 of PR #47 (2026-10-19)
# ===========================================================================
def _share_count_unverified():
    """test_engine_55's R3-CAP shape (FY2023-24 diluted counts filed in thousands, no power-of-ten factor found)
    rescued by a declared base_override pin, plus a $40M FY2025 acquired-IPR&D charge (cash-flow check declared): the
    engine has no verified denominator, so it records treatment not_applied_share_count_unverified and deducts $0."""
    import test_engine_55 as T55

    def go():
        pin = (200e6 * 1.05 ** 4 - 60e6) / 100e6
        facts = T55._syn_facts(shares={2023: 100e3, 2024: 100e3})
        TI._fy(facts, TI.EXPENSE, 2025, 40e6)
        bo = T55._bo(pin)
        n = TI._ok(TI._run(facts, extra=["--base-oe-ps", repr(pin)], judgment={"base_override": bo}))
        return n, bo
    return TI._cached("ms_unverified", go)


def test_unverified_share_count_charge_needs_a_quantified_tier_override():
    """[Codex review r1, #4321488151] Treatment not_applied_share_count_unverified: a $40M charge the engine could
    not put on a verified share count, so the tier is the UNADJUSTED one. WORKER_SPEC step 4 / AGENTS check 8: the
    worker blocks NEEDS_MAIN_AGENT: shares and only a main-agent tier_override whose reason quantifies the hand
    deduction publishes it. make_score refuses the score without a tier_override, and with one whose reason gives no
    figure; it scores with a quantified one. Before the fix make_score published the unadjusted tier silently."""
    n, bo = _share_count_unverified()
    blk = n["iprd_adjustment"]
    assert blk["treatment"] == "not_applied_share_count_unverified" and blk["total"] == 40e6, blk
    assert blk["charge_per_share"] == 0.0 and blk["shares_denominator"] is None, blk
    r = _score(n, _j(base_override=bo))
    assert r.rc == 1 and "NEEDS_MAIN_AGENT: shares" in r.err and "$40,000,000" in r.err, (r.rc, r.err[-800:])
    r = _score(n, _j(base_override=bo, tier_override=n["tier_by_numbers"],
                     tier_override_reason="main agent: the charge is small against the base"))
    assert r.rc == 1 and "NEEDS_MAIN_AGENT: shares" in r.err, (r.rc, r.err[-800:])
    why = ("main agent: $40,000,000 / 100,000,000 verified diluted shares (FY2025 10-K cover) = $0.40/share deducted "
           "by hand; adjusted weighted IRR 9.6%, same band")
    r = _score(n, _j(base_override=bo, tier_override=n["tier_by_numbers"], tier_override_reason=why))
    assert r.rc == 0, r.err[-800:]
    s = r.result["score"]
    assert s["tier_final"] == n["tier_by_numbers"] and s["tier_override_reason"] == why, s


def test_median_counterfactual_holds_the_headline_charge():
    """[Codex review r1, summary P2] A median-base score whose shares_override fills the latest FY diluted count
    (125M; the filer left it out, so the no-override world falls back to the 100M cover-page count) beside a $300M
    FY2025 charge: the median override-impact replay must hold the final run's IPR&D charge ($300M / 125M =
    $2.40/share, DCF_IPRD_HOLD) like the declared-pin and TTM replays, so the measured IRR impact is the override's
    effect on the base and growth alone, not that plus a $3.00 vs $2.40 swing in a mechanical charge. Before the fix the median replay carried no
    hold and re-detected the charge on its own denominator."""
    import test_engine_55 as T55
    facts = T55._syn_facts(shares={2025: None})
    TI._fy(facts, TI.EXPENSE, 2025, 300e6)
    so = TI._o(125e6)
    J = {"shares_override": so}
    n = TI._ok(TI._run_env(facts, judgment=J))
    c = E.iprd_charge_per_share(n)
    assert n["iprd_adjustment"]["shares_denominator"] == 125e6 and c == 300e6 / 125e6, n["iprd_adjustment"]
    r = _bridged(n, _j(shares_override=so), facts)
    assert r.rc == 0, r.err[-800:]
    oi = r.result["score"]["override_impact"]
    hold = json.dumps({"treatment": "one_time_value_deduction", "charge_per_share": c})
    held = TI._run_env(facts, judgment=J, env={"DCF_NO_OVERRIDES": "1", "DCF_IPRD_HOLD": hold}, measure=True)["numbers"]
    unheld = TI._run_env(facts, judgment=J, env={"DCF_NO_OVERRIDES": "1"}, measure=True)["numbers"]
    assert unheld["iprd_adjustment"]["charge_per_share"] == 3.0   # the replay's own denominator: 100M
    assert oi["base_used"] == "median_3y", oi
    assert oi["weighted_irr_without_override"] == round(held["implied_irr_weighted"], 4), (oi, held["implied_irr_weighted"])
    assert round(unheld["implied_irr_weighted"], 4) != oi["weighted_irr_without_override"]
    cf = [x for x in r.result["spawns"] if x["script"].endswith("dcf_engine.py.txt") and x["no_overrides"]]
    assert len(cf) == 1 and json.loads(cf[0]["hold"]) == json.loads(hold), cf


def test_payable_counterfactual_holds_the_headline_charge():
    """[Codex review r1, summary P2 — the same rule on the last branch] The payable-earnings pin's replay also
    carries DCF_IPRD_HOLD, so every override-impact counterfactual holds the final run's IPR&D treatment and charge
    (AGENTS check 8). Checked in-process: the replay's environment, captured from make_score's own _run_json."""
    import make_score as M
    import test_make_score_55 as T55M
    n, _ = T55M._payable(T55M.CUR)
    n = dict(n, iprd_adjustment={"treatment": "one_time_value_deduction", "charge_per_share": 0.5, "total": 23.2415e6})
    seen = []

    def fake(cmd, env_extra=None, timeout=600):
        seen.append(dict(env_extra or {}))
        return {"implied_irr_weighted": 0.11, "base_oe_per_share": n["base_oe_per_share"], "data_gap": []}
    orig = M._run_json
    M._run_json = fake
    try:
        oi = M.compute_override_impact("TST", n)
    finally:
        M._run_json = orig
    assert oi["base_used"] == "payable_5y", oi
    assert len(seen) == 1 and seen[0].get("DCF_NO_OVERRIDES") == "1", seen
    assert json.loads(seen[0].get("DCF_IPRD_HOLD") or "null") == {"treatment": "one_time_value_deduction",
                                                                   "charge_per_share": 0.5}, seen


# ===========================================================================
# Codex review round 2 of PR #47
# ===========================================================================
def test_amortized_base_override_event_records_the_one_time_counterfactual():
    """[Codex review r2, #4321940606] The registry's iprd_amortized base_override event recorded the native and
    pinned bases but only the IRR WITH the override. Without it the run takes the one-time value deduction on the
    native base, so make_score replays exactly that (the final run's inputs and field overrides, no pin — the
    median native base) and records both IRRs, the change in pp and the tier pair, as payable_pin_impact does for
    the payable pin. The replay is the preliminary one-time run itself (TI._recurrent: same IRR, same tier)."""
    facts = TI._facts(expense={2023: 15e6, 2025: 20e6})
    n, d = _amortized()
    one = TI._recurrent()
    assert one["iprd_adjustment"]["treatment"] == "one_time_value_deduction"
    r = _bridged(n, _j(base_override=d), facts)
    assert r.rc == 0, r.err[-800:]
    ev = [e for e in r.result["entries"] if e.get("event") == "base_override"]
    assert len(ev) == 1, r.result["entries"]
    ev = ev[0]
    assert ev["weighted_irr_without_override"] == round(one["implied_irr_weighted"], 4), (ev, one["implied_irr_weighted"])
    assert ev["weighted_irr_with_override"] == round(n["implied_irr_weighted"], 4), ev
    assert ev["weighted_irr_impact_pp"] == round((n["implied_irr_weighted"] - one["implied_irr_weighted"]) * 100, 3), ev
    assert (ev["tier_by_numbers_without_override"], ev["tier_by_numbers_with_override"]) == (
        one["tier_by_numbers"], n["tier_by_numbers"]), ev
    assert ev["iprd_charge_per_share_without_override"] == round(E.iprd_charge_per_share(one), 4), ev
    assert ev["base_oe_without_override"] == round(one["base_oe_per_share"], 4), ev
    cf = [s for s in r.result["spawns"] if s["script"].endswith("dcf_engine.py.txt")]
    assert len(cf) == 1 and not cf[0]["no_overrides"] and cf[0]["hold"] is None, cf
    assert "--base-oe-ps" not in cf[0]["argv"] and "--ttm" not in cf[0]["argv"], cf

def test_unconvertible_iprd_expense_is_refused_needs_main_agent():
    """[Codex review r3, #4322176027] A positive acquired-IPR&D expense filed only in a currency with no FX rate and
    no usable cash fact (EUR 300M at the synthetic USD filer): the engine deducts nothing and records excluded
    non_usd_no_rate, so the tier is the UNADJUSTED one. make_score accepted it silently; it now refuses the score
    (ACQUIRED_IPRD_UNCONVERTED, NEEDS_MAIN_AGENT: currency) whatever judgment.json says, like a period still awaiting
    its cash-flow check. A native expense of 0 records no charge and scores."""
    n = TI._ok(TI._run(TI._eur_expense(300e6), checks=False))
    assert n["iprd_adjustment"]["treatment"] == "non_usd_no_rate"
    r = _score(n)
    assert r.rc == 1 and "ACQUIRED_IPRD_UNCONVERTED" in r.err and "NEEDS_MAIN_AGENT: currency" in r.err, (r.rc, r.err[-800:])
    assert "FY2025 300,000,000 EUR" in r.err, r.err[-800:]
    r = _score(n, _j(tier_override=n["tier_by_numbers"], tier_override_reason="main agent: $3.30/share, IRR 9.9%"))
    assert r.rc == 1 and "ACQUIRED_IPRD_UNCONVERTED" in r.err, (r.rc, r.err[-800:])
    z = TI._ok(TI._run(TI._eur_expense(0.0), checks=False))
    r = _score(z)
    assert r.rc == 0, r.err[-800:]


# --- Codex review round 4 of PR #47 -------------------------------------------------------------------------------
def test_unconvertible_cash_settlement_is_refused_needs_main_agent():
    """[Codex review r4, #4322408953] A cash-tag-only payment that could settle the window's unpaid remainder but is
    filed in a currency with no FX rate (FY2024 $40M expensed, $10M paid; FY2025 EUR 24M, no rate) was dropped, and
    make_score scored the $10M deduction. The engine now records the native amount (cash_native) and raises
    ACQUIRED_IPRD_UNCONVERTED; make_score refuses the score (NEEDS_MAIN_AGENT: currency), naming the payment."""
    fyf = TI._facts(expense={2024: 40e6}, cash={2024: 10e6})
    TI._syn_put(fyf, TI.CASH, "EUR", TI._ctx("2025-01-01", "2025-12-31", 24e6, filed="2026-02-20"))
    n = TI._ok(TI._run_fx(fyf, {}))
    r = _score(n)
    assert r.rc == 1 and "ACQUIRED_IPRD_UNCONVERTED" in r.err and "NEEDS_MAIN_AGENT: currency" in r.err, (r.rc, r.err[-800:])
    assert "FY2025 24,000,000 EUR" in r.err, r.err[-800:]
    m = TI._ok(TI._run_fx(fyf, {"EUR": {"2025-12-31": 1.25}}))
    r = _score(m)
    assert r.rc == 0, r.err[-800:]


def test_iprd_equations_carry_the_ads_ratio():
    """[Codex review r4, #4322408961] At an ADS filer the engine's charge per share is total ÷ shares × ads_ratio and
    the amortized base native − mean ÷ shares × ads_ratio, but key_numbers.md printed both equations without the ratio
    ($100M ÷ 100M shares = $2.00/share at 2 ordinary per ADS): the quotable lines did not reproduce the record. Both
    now print '× ADS ratio r' and a per-ADS result when the applied ratio is not 1; at ratio 1 they are unchanged."""
    import make_score as M
    ratio, total, denom = 2.0, 100e6, 100e6
    figs, shares, native = [100e6, 100e6, 100e6], 100e6, 10.0
    pinned = E.iprd_amortized_value(native, figs, shares, {"ratio": ratio})
    blk = {"treatment": "amortized_in_base", "total": total, "shares_denominator": denom, "shares_source": "diluted_latest",
           "ads_ratio": ratio, "charge_per_share": total / denom * ratio, "materiality": 0.2, "material": True,
           "recurrent": True, "periods": [],
           "amortized": {"native_base": "median_of_last_3_fy_oe_per_share", "native_base_per_share": native,
                         "figures": figs, "mean_annual_charge": sum(figs) / 3, "shares": shares, "ads_ratio": ratio,
                         "pinned_per_share": pinned}}
    L = M.iprd_lines({"iprd_adjustment": blk})
    tot = [x for x in L if x.startswith("- Total charge")][0]
    assert "$100,000,000 ÷ 100,000,000 shares (diluted_latest) × ADS ratio 2 = $2.00/ADS" in tot, tot
    am = [x for x in L if x.startswith("- Amortized in the base")][0]
    assert "÷ 100,000,000 shares × ADS ratio 2 = pinned base $8.00" in am, am
    one = dict(blk, treatment="one_time_value_deduction", ads_ratio=1.0, charge_per_share=1.0, amortized=None)
    tot1 = [x for x in M.iprd_lines({"iprd_adjustment": one}) if x.startswith("- Total charge")][0]
    assert tot1 == "- Total charge: $100,000,000 ÷ 100,000,000 shares (diluted_latest) = $1.00/share", tot1


# --- Codex review round 8 of PR #47 -------------------------------------------------------------------------------
def _score_reg(n, j, registry_entries=None):
    """_score with the registry seeded first (registry_entries: what an earlier make_score run left there)."""
    m = copy.deepcopy(n)
    m["ticker"] = "TST"
    r = Run(m, _with_applied(n, j))
    if registry_entries is not None:
        with open(r.registry, "w", encoding="utf-8") as f:
            json.dump({"entries": registry_entries}, f)
    r = r.run()
    try:
        r.result = dict(r.state(), score=r.score() if r.rc == 0 else None, entries=r.entries())
    finally:
        r.close()
    return r


def _r8_cases():
    def go():
        cap = {"value": 100e6, "source": TI.CT_SRC}
        old = TI.deferred(period="2022-12-31", amount=60e6, first="2021-12-31", source=TI.OK_SRC_2021, deal="Old Bio",
                          contingent=cap)
        new = TI.deferred(amount=60e6, first="2021-12-31", source=TI.OK_SRC_2021, deal="Old Bio", contingent=cap)
        facts = TI._facts(expense={2021: 8e6, 2023: 15e6, 2025: 60e6})
        runs = {"old": [old], "new": [new], "none": None, "both": [old, dict(new, amount=40e6)]}
        out = {}
        for k, entries in runs.items():
            out[k] = TI._ok(TI._run(facts, judgment={"iprd_deferred_payment": entries} if entries else None))
        return cap, old, new, out
    return TI._cached("ms_r8_lifetime", go)


def test_deferred_payments_are_recorded_and_deleting_one_cannot_reopen_the_cap():
    """[Codex review r8, #4323410481] The lifetime contingent_total cap summed only what judgment.json declared NOW:
    with a rolled-out $60M FY2022 Old Bio milestone deleted and the engine rerun, nothing remembered it, and a later
    $60M FY2025 Old Bio declaration against a $100M contingent_total scored ($120M in all, FY2025 kept out of the
    recurrence count). make_score now records each deal's cumulative declared deferred amount as a registry event
    (iprd_deferred_payment: deal, contingent_total, paid_to_date, first_charged_period, periods) carried across runs,
    refuses a run whose declarations for a deal sum to less than the recorded paid_to_date (a deleted or shrunk
    entry), and caps max(declared on recorded periods, paid_to_date) + new periods' amounts at the contingent_total."""
    cap, old, new, n = _r8_cases()
    assert n["new"]["iprd_adjustment"]["recurrence_excluded"], n["new"]["iprd_adjustment"]   # the engine alone accepts it
    r = _score_reg(n["old"], _j(iprd_deferred_payment=[old]))
    assert r.rc == 0, r.err[-800:]
    ev = [e for e in r.result["entries"] if e.get("event") == "iprd_deferred_payment"]
    assert len(ev) == 1, r.result["entries"]
    assert (ev[0]["deal"], ev[0]["first_charged_period"], ev[0]["contingent_total"], ev[0]["paid_to_date"],
            ev[0]["periods"]) == ("Old Bio", "2021-12-31", cap, 60e6, [{"period": "2022-12-31", "amount": 60e6}]), ev
    reg = r.result["entries"]
    # unchanged rerun: the event is carried as it was (its first date kept)
    r2 = _score_reg(n["old"], _j(iprd_deferred_payment=[old]), reg)
    assert r2.rc == 0 and [e for e in r2.result["entries"] if e.get("event") == "iprd_deferred_payment"] == ev, r2.err[-600:]
    # deleted, engine rerun: refused (the registry still holds the paid amount)
    r3 = _score_reg(n["none"], _j(), reg)
    assert r3.rc == 1 and "paid_to_date" in r3.err and "Old Bio" in r3.err, r3.err[-800:]
    assert r3.result["entries"] == reg, "a refusal rewrote the registry"
    # deleted and replaced by a new $60M declaration: past the lifetime cap ($60M recorded + $60M > $100M) — since
    # Codex review r10 refused first as a deleted recorded period, the message naming it and the cap
    r4 = _score_reg(n["new"], _j(iprd_deferred_payment=[new]), reg)
    assert (r4.rc == 1 and "contingent_total" in r4.err and "Old Bio" in r4.err and "2022-12-31" in r4.err
            and "immutable" in r4.err), r4.err[-800:]
    # kept, plus $40M in the window: the lifetime $100M is within the cap and recorded
    r5 = _score_reg(n["both"], _j(iprd_deferred_payment=[old, dict(new, amount=40e6)]), reg)
    assert r5.rc == 0, r5.err[-800:]
    ev5 = [e for e in r5.result["entries"] if e.get("event") == "iprd_deferred_payment"]
    assert ev5[0]["paid_to_date"] == 100e6 and ev5[0]["periods"] == [{"period": "2022-12-31", "amount": 60e6},
                                                                     {"period": "2025-12-31", "amount": 40e6}], ev5
    # a shrunk entry: the declarations sum below the recorded paid_to_date
    r6 = _score_reg(n["old"], _j(iprd_deferred_payment=[old]), ev5)
    assert r6.rc == 1 and "paid_to_date" in r6.err, r6.err[-800:]


def test_validate_deferred_refuses_an_impossible_date():
    """[Codex review r8, #4323410495] make_score's shape check parses each period and first_charged_period: an
    impossible date ("2020-99-99", "2021-02-30") is malformed."""
    import make_score as M
    d = TI.deferred()
    for bad in (dict(d, period="2020-99-99"),
                dict(d, deferred_payment_of=dict(d["deferred_payment_of"], first_charged_period="2021-02-30"))):
        try:
            M.validate_iprd_deferred_payment({"iprd_deferred_payment": [bad]})
        except SystemExit:
            continue
        raise AssertionError(f"accepted {bad!r}")


# --- Codex review round 9 of PR #47 -------------------------------------------------------------------------------
R9_CT = {"value": 100e6, "source": TI.CT_SRC}


def _refusal(fn, *a):
    """make_score's refusal text when fn(*a) refuses (SystemExit), else None."""
    import contextlib
    import io
    buf = io.StringIO()
    try:
        with contextlib.redirect_stderr(buf):
            fn(*a)
    except SystemExit:
        return buf.getvalue()
    return None


def _r9(deal="Surf Bio", period="2024-12-31", amount=60e6, first="2021-12-31", source=TI.OK_SRC_2021, contingent=R9_CT):
    return TI.deferred(period=period, amount=amount, first=first, source=source, deal=deal, contingent=contingent)


def _lifetime(entries, prior):
    import make_score as M
    return M.iprd_deferred_lifetime("TST", M.validate_iprd_deferred_payment({"iprd_deferred_payment": entries}), prior)


def test_a_recorded_deals_contingent_total_and_first_charge_cannot_change():
    """[Codex review r9, #4323764885] The lifetime check read the cap from the current declaration only: with Surf
    Bio's $60M FY2024 milestone recorded against a $100M contingent_total, raising the cap to $200M on every entry and
    adding an $80M FY2025 milestone passed, and the registry event was rewritten with cap $200M and $140M paid. A
    recorded deal's contingent_total (value and source) is now immutable: a declaration whose cap differs from the
    recorded one by more than $1, or whose source differs beyond whitespace, is refused, and the event keeps the
    recorded cap. A changed first_charged_period on a recorded deal is refused too."""
    ev1 = _lifetime([_r9()], [])
    assert ev1[0]["contingent_total"] == R9_CT and ev1[0]["paid_to_date"] == 60e6, ev1
    # control: the recorded cap holds a second $80M milestone off
    assert "more than its contingent_total" in (_refusal(_lifetime, [_r9(), _r9(period="2025-12-31", amount=80e6)], ev1)
                                                or "")
    other_src = TI.CT_SRC.replace("0000999001-26-000004", "0000999001-26-000009")
    for ct in ({"value": 200e6, "source": TI.CT_SRC}, {"value": 200e6, "source": other_src},
               {"value": 100e6, "source": other_src}, {"value": 90e6, "source": TI.CT_SRC}):
        msg = _refusal(_lifetime, [_r9(contingent=ct), _r9(period="2025-12-31", amount=30e6, contingent=ct)], ev1)
        assert msg and "contingent_total" in msg and "recorded" in msg and "Surf Bio" in msg, (ct, msg)
    # within $1 and only whitespace apart: accepted, the event keeps the recorded cap exactly
    ws = {"value": 100e6 + 0.5, "source": "  " + TI.CT_SRC.replace(" ", "  ") + " "}
    ev2 = _lifetime([_r9(contingent=ws), _r9(period="2025-12-31", amount=40e6, contingent=ws)], ev1)
    assert ev2[0]["contingent_total"] == R9_CT and ev2[0]["paid_to_date"] == 100e6, ev2
    # the deal's first charge moved
    msg = _refusal(_lifetime, [_r9(first="2020-12-31")], ev1)
    assert msg and "first_charged_period" in msg and "recorded" in msg, msg


def test_a_renamed_copy_of_a_recorded_deal_is_refused():
    """[Codex review r9, #4323764895] Every cap check keyed a deal on its name: with "Surf Bio" recorded ($60M of a
    $100M contingent_total), a second $60M declared as "Surf Bio acquisition" (the same first charge, the same
    contingent_total filing) got its own copy of the cap — $120M paid against $100M. Deal identity is now the
    evidence: a new deal key whose first_charged_period and contingent_total source accession match a recorded event
    (or another deal declared beside it) under a different name is refused as a renamed copy, naming the recorded
    deal. A distinct deal (another first charge, or a cap disclosed in another filing) is accepted."""
    ev1 = _lifetime([_r9()], [])
    dup = _r9(deal="Surf Bio acquisition", period="2025-12-31")
    msg = _refusal(_lifetime, [_r9(), dup], ev1)
    assert msg and "renamed copy" in msg and "'Surf Bio'" in msg and "Surf Bio acquisition" in msg, msg
    # the same two names in one declaration, nothing recorded yet
    msg = _refusal(_lifetime, [_r9(), dup], [])
    assert msg and "renamed copy" in msg, msg
    # distinct deals: another first charge, or a cap disclosed in another filing
    other_first = _r9(deal="Other Bio", period="2025-12-31", first="2022-12-31", source=TI._src(23))
    other_cap = _r9(deal="Other Bio", period="2025-12-31",
                    contingent={"value": 80e6, "source": "SYN 10-K FY2024 (0000999001-25-000003) Note 6, p. 77: $80.0 "
                                                         "million of Other Bio milestones, not recognized"})
    for o in (other_first, other_cap):
        ev = _lifetime([_r9(), o], ev1)
        assert sorted(e["deal"] for e in ev) == ["Other Bio", "Surf Bio"], ev


def test_record_check_refuses_a_rolled_out_period_that_is_not_a_fiscal_year_end():
    """[Codex review r9, #4323764891] make_score re-checks every rolled-out entry with the engine's helper against the
    FY ends the run recorded (iprd_adjustment.fy_period_ends): a non-FY-end period is refused, and a record carrying
    rolled-out entries without fy_period_ends (an engine run that predates the rule) is refused — rerun the engine."""
    import make_score as M
    old = _r9(deal="Old Bio", period="2022-12-31")
    blk = {"periods": [], "deferred_payments_rolled_out": [old],
           "fy_period_ends": [f"{y}-12-31" for y in range(2019, 2026)]}
    assert M.check_iprd_deferred_payment({"iprd_adjustment": blk}, [old]) is None
    bad = dict(old, period="2022-06-30")
    msg = _refusal(M.check_iprd_deferred_payment, {"iprd_adjustment": dict(blk, deferred_payments_rolled_out=[bad])},
                   [bad])
    assert msg and "not a fiscal-year end" in msg, msg
    msg = _refusal(M.check_iprd_deferred_payment,
                   {"iprd_adjustment": {k: v for k, v in blk.items() if k != "fy_period_ends"}}, [old])
    assert msg and "fy_period_ends" in msg, msg



# --- Codex review round 10 of PR #47 ------------------------------------------------------------------------------
def test_a_recorded_periods_amount_cannot_change():
    """[Codex review r10] The registry refused only a deal whose declarations summed below its recorded paid_to_date,
    then overwrote the recorded per-period amounts with the new declarations: with Surf Bio's FY2022 $60M and FY2023
    $20M recorded ($80M paid of $100M), swapping them to $20M / $60M passed and the event was rewritten — which can
    make FY2023 wholly deferred and drop it from the ACQUIRED_IPRD_RECURRENT count with the cap still satisfied —
    and deleting FY2022 while declaring FY2023 $80M passed too and wrote periods summing to $140M against an $80M
    paid_to_date (the next unchanged run was refused). Every recorded period is now immutable: make_score refuses a
    declaration whose amount for a recorded period is missing or more than $1 apart from the recorded one (shrunk or
    grown), naming the period; new periods merge as before and the event keeps the recorded amounts exactly."""
    two = [_r9(period="2022-12-31", amount=60e6), _r9(period="2023-12-31", amount=20e6)]
    ev1 = _lifetime(two, [])
    assert ev1[0]["paid_to_date"] == 80e6 and ev1[0]["periods"] == [{"period": "2022-12-31", "amount": 60e6},
                                                                    {"period": "2023-12-31", "amount": 20e6}], ev1
    # control: the same declarations pass and the event is unchanged
    assert _lifetime(two, ev1) == ev1
    cases = {
        "swapped": ([_r9(period="2022-12-31", amount=20e6), _r9(period="2023-12-31", amount=60e6)], "2022-12-31"),
        "grown": ([_r9(period="2022-12-31", amount=60e6), _r9(period="2023-12-31", amount=30e6)], "2023-12-31"),
        "deleted and moved": ([_r9(period="2023-12-31", amount=80e6)], "2022-12-31"),
        "shrunk": ([_r9(period="2022-12-31", amount=20e6), _r9(period="2023-12-31", amount=20e6)], "2022-12-31"),
    }
    for label, (entries, period) in cases.items():
        msg = _refusal(_lifetime, entries, ev1)
        assert msg and "Surf Bio" in msg and period in msg and "immutable" in msg and "recorded" in msg, (label, msg)
    # within $1, plus a new period: accepted; the recorded amounts are kept exactly and the new one merged
    ev2 = _lifetime([_r9(period="2022-12-31", amount=60e6 + 0.5), _r9(period="2023-12-31", amount=20e6 - 0.5),
                     _r9(period="2025-12-31", amount=15e6)], ev1)
    assert ev2[0]["periods"] == [{"period": "2022-12-31", "amount": 60e6}, {"period": "2023-12-31", "amount": 20e6},
                                 {"period": "2025-12-31", "amount": 15e6}], ev2
    assert ev2[0]["paid_to_date"] == 95e6, ev2


# --- Codex review round 11 of PR #47 ------------------------------------------------------------------------------
def _r11_deferred_runs():
    def go():
        decl = TI.deferred(period="2024-12-31", amount=30e6, first="2022-12-31", source=TI.PRE_SRC, deal="Old Bio",
                           contingent=TI.PRE_CT)
        return decl, TI._ok(TI._pre_window([decl])), TI._ok(TI._pre_window())
    return TI._cached("ms_r11_deferred", go)


def test_no_live_figures_unless_the_score_is_from_this_run():
    """[Codex review r11, #4324232845, the main agent's general rule] A recorded pre-window deferred payment ($30M Old
    Bio, FY2024) deleted from judgment.json and the engine rerun: the new run deducts $0, make_score refuses it against
    the durable registry and the declared run's score.json stays on disk — but iprd_unresolved does not see a
    registry refusal, so reprice published live IRRs from paths that omit the recorded payment (score_json_fresh
    false only dropped the override) and build_site showed them. Now no live figures exist for ANY run its score.json
    was not built from, whatever the reason make_score refused (or has not run yet): reprice raises Skip (no
    live.json, a stale one removed) and build_site withholds any live.json with reason score_not_from_this_run. The
    score's own run reprices and shows as before."""
    import reprice as R
    import build_site as B
    import shutil
    import tempfile
    decl, n_decl, n_del = _r11_deferred_runs()
    r1 = _score_reg(n_decl, _j(iprd_deferred_payment=[decl]))
    assert r1.rc == 0, r1.err[-800:]
    s = r1.result["score"]
    r2 = _score_reg(n_del, _j(), r1.result["entries"])
    assert r2.rc != 0 and "no longer declared" in r2.err, r2.err[-800:]
    assert n_del["iprd_adjustment"]["charge_per_share"] == 0 and E.iprd_unresolved(n_del) is None
    # the runs as on disk: engine-stamped (round 12 binds the score to the run's content_hash)
    m_del, m_decl = _stamp(dict(copy.deepcopy(n_del), ticker="TST")), _stamp(dict(copy.deepcopy(n_decl), ticker="TST"))
    day = m_del["as_of"]
    try:
        R.reprice(m_del, 18.75, day, s, today=day)
        raise AssertionError("repriced a run its score.json was not built from")
    except R.Skip as e:
        assert "score.json is not from this engine run" in str(e) and "make_score" in str(e), str(e)
    live = R.reprice(m_decl, 18.75, day, s, today=day)
    assert live["score_json_fresh"] is True and live["score_mismatch"] is None, live
    assert live["iprd_charge_per_share"] == n_decl["iprd_adjustment"]["charge_per_share"] > 0, live
    shown, w = B.live_shown({"numbers": m_del, "score": s, "live": live})
    assert shown is None and w["reason"] == "score_not_from_this_run" and w["price"] == 18.75, w
    assert "make_score" in w["note"] and w["scored_date"] == s["analysis_date"], w
    assert B.live_shown({"numbers": m_decl, "score": s, "live": live}) == (live, None)
    ok, mm = B.score_from_run(s, m_del)
    assert not ok and mm == R.score_matches_run(s, m_del)[1], (mm, R.score_matches_run(s, m_del))
    assert B.score_from_run(s, m_decl) == R.score_matches_run(s, m_decl) == (True, [])
    tmp = tempfile.mkdtemp(prefix="reprice_r11_")
    saved = R.BASE
    try:
        d = os.path.join(tmp, "TST")
        os.makedirs(d)
        for fn, obj in (("dcf_numbers.json", m_del), ("score.json", s), ("live.json", live)):
            with open(os.path.join(d, fn), "w", encoding="utf-8") as f:
                json.dump(obj, f)
        R.BASE = tmp
        try:
            R.reprice_folder("TST")
            raise AssertionError("reprice_folder wrote live.json")
        except R.Skip as e:
            assert "score.json is not from this engine run" in str(e), str(e)
        assert not os.path.exists(os.path.join(d, "live.json")), "the stale live.json stayed"
    finally:
        R.BASE = saved
        shutil.rmtree(tmp, ignore_errors=True)


def test_a_release_mismatch_rebuild_of_the_same_run_still_reprices():
    """[Codex review r11, the main agent's shape] make_score rebuilding a 5.5.0 run's score.json under 5.6.0 code
    copies the run's engine_release and figures, so the score is from that run: reprice writes live figures and
    build_site shows them (the general live-figure rule never pauses a release-mismatch rebuild)."""
    import reprice as R
    import build_site as B
    n = copy.deepcopy(TI._plain())
    n["engine_release"] = "5.5.0"
    n.pop("iprd_adjustment", None)
    r = _score(n)
    assert r.rc == 0, r.err[-800:]
    s = r.result["score"]
    assert s["engine_release"] == "5.5.0" != E.ENGINE_RELEASE, s.get("engine_release")
    m = _stamp(dict(n, ticker="TST"))   # the run as on disk (round 12: the score carries its content_hash)
    live = R.reprice(m, 25.0, m["as_of"], s, today=m["as_of"])
    assert live["score_json_fresh"] is True and live["engine_release_of_run"] == "5.5.0", live
    assert B.score_from_run(s, m) == (True, []) and B.live_shown({"numbers": m, "score": s, "live": live}) == (live, None)


# --- Codex review round 12 of PR #47 ------------------------------------------------------------------------------
def test_live_figures_are_bound_to_the_runs_content_hash():
    """[Codex review r12, summary-5584834562, the main agent's shape] score_matches_run / score_from_run took rounded
    headline figures as proof that score.json came from the run: a second same-day run (or an edited one) that moved
    scenario paths or the acquired-IPR&D record while keeping the tier, base, price, 4-dp IRR and 2-dp IV still
    passed, so live figures were written for a run make_score refused or never scored. Now make_score copies the
    run's content_hash into score.json (dcf_content_hash) and both checks require it to equal the dcf_numbers.json
    content_hash, which must itself match the record's content (the integrity check make_score applies): another
    run with the same headline (re-stamped) or the same run edited after stamping (stale hash) gets no live figures.
    A score.json without the field (every score built before this round) keeps the headline comparison."""
    import reprice as R
    import build_site as B
    n = _one_time()
    r = _score(n)
    assert r.rc == 0, r.err[-800:]
    s = r.result["score"]
    own = _stamp(dict(copy.deepcopy(n), ticker="TST"))
    assert s.get("dcf_content_hash") == own["content_hash"], (s.get("dcf_content_hash"), own["content_hash"])
    assert R.score_matches_run(s, own) == B.score_from_run(s, own) == (True, [])
    day = own["as_of"]
    live = R.reprice(own, 25.0, day, s, today=day)
    assert live["score_json_fresh"] is True and B.live_shown({"numbers": own, "score": s, "live": live}) == (live, None)
    edited = copy.deepcopy(own)
    edited["iprd_adjustment"]["deferred_payments_rolled_out"] = [{"period": "2021-12-31", "amount": 5e6}]
    for other, why in ((_stamp(edited), "dcf_content_hash"), (edited, "content_hash")):
        ok, mm = R.score_matches_run(s, other)
        assert not ok and any(why in x for x in mm), mm
        assert B.score_from_run(s, other) == (ok, mm), (B.score_from_run(s, other), mm)
        try:
            R.reprice(other, 25.0, day, s, today=day)
            raise AssertionError("repriced a run its score.json was not built from")
        except R.Skip as e:
            assert "score.json is not from this engine run" in str(e), str(e)
        shown, w = B.live_shown({"numbers": other, "score": s, "live": live})
        assert shown is None and w["reason"] == "score_not_from_this_run", w
    # a pre-round-12 score.json (no dcf_content_hash): the headline comparison, as before
    old = {k: v for k, v in s.items() if k != "dcf_content_hash"}
    assert R.score_matches_run(old, _stamp(edited)) == B.score_from_run(old, _stamp(edited)) == (True, [])


def test_a_share_paid_residual_check_on_a_cash_basis_period_is_scored_and_kept_in_sync():
    """[Codex review r12, #4324802987] The paid_in_shares check applied to a cash-basis period ($100M FY2024 expense,
    $0 cash fact) is what keeps the unrelated FY2025 cash-only payment out of the deduction, so make_score holds it
    like any applied check: score.json names it on the period, key_numbers.md says the residual was paid in shares,
    and a judgment.json that now declares it differently is refused as out of sync with the run. Without the check the
    automatic deferred match prints its assumption."""
    chk = TI._shares_check("2024-12-31", 100e6)
    facts = lambda: TI._facts(expense={2024: 100e6}, cash={2024: 0.0, 2025: 100e6})
    n = TI._cached("ms_r12_shares", lambda: TI._ok(TI._run(facts(), judgment={"iprd_cash_flow_check": [chk]},
                                                          checks=False)))
    r = _score(n, _j(iprd_cash_flow_check=[chk]))
    assert r.rc == 0, r.err[-800:]
    p24 = [p for p in r.result["score"]["iprd_adjustment"]["periods"] if p["period"] == "2024-12-31"][0]
    assert p24["cash_flow_check"] == "paid_in_shares" and p24["deducted"] == 0.0, p24
    assert "residual $100,000,000 paid in shares" in r.result["key"], r.result["key"]
    r2 = _score(n, _j(iprd_cash_flow_check=[dict(chk, presentation="added_back_paid_in_investing")]))
    assert r2.rc != 0 and "now declares differently" in r2.err, r2.err[-800:]
    m = TI._cached("ms_r12_assumed", lambda: TI._ok(TI._run(facts(), checks=False)))
    assert m["iprd_adjustment"]["total"] == 100e6, m["iprd_adjustment"]
    r3 = _score(m, _j())
    assert r3.rc == 0, r3.err[-800:]
    assert "assumes the earlier remainder was payable in cash" in r3.result["key"], r3.result["key"]


if __name__ == "__main__":
    fails = 0
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn) and fn.__module__ == __name__:
            try:
                fn()
                print(f"PASS {name}")
            except AssertionError as e:
                fails += 1
                print(f"FAIL {name}: {e}")
            except Exception as e:
                fails += 1
                print(f"ERROR {name}: {type(e).__name__}: {e}")
    sys.exit(1 if fails else 0)
