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
from test_make_score_55 import Run, _judgment  # noqa: E402
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
    r = _score(n, _j(base_override=d))
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
        run.result = dict(run.state(), score=run.score() if run.rc == 0 else None, entries=run.entries(), spawns=spawns)
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
