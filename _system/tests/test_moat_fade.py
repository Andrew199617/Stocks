#!/usr/bin/env python3
"""M6 — the moat's DIRECTION sets the growth hold (engine 5.7.0; Andrew, 2026-10-20: "eroding moat should fade faster
and vice versa"; design 10_moat_fade with the decisions 10b and the lane defaults Q4-Q6 of 2026-10-21; lane L3b).
Run: python _system/tests/test_moat_fade.py (or python -m pytest _system/tests). Offline: the engine runs drive
dcf_engine.main() through engine55_harness on the gzip fixtures; the scorecard cases evaluate temp folders.

The decision: the moat's LEVEL still sets CAP = clamp(2 + 1.3 x moat, 2, 15); its DIRECTION sets the growth hold
before the fade — eroding and not rebutted 0 years, stable 2, widening and confirmed 3 — applied only to a scenario
that starts above terminal growth (fade_hold; a start at or below terminal keeps 2, so eroding never raises a value).
The trend reaches the engine as --moat-trend (exit 5 BAD_MOAT_TREND before any fetch); every replay reads the
record's own per-scenario holds (recorded_scenario_holds), never re-derives them.

Engine (dcf_engine):            T1 test_hold_by_trend · T2 test_fade_hold_only_above_terminal · T3 (guard, passes on
  old) test_hold_zero_fades_from_year_one · T4 test_hold_is_monotone_in_direction · T5 test_recorded_hold_years ·
  T6 test_replay_paths_reads_recorded_hold · T6b test_replay_record_wins_over_the_code · T8
  test_engine_moat_trend_eroding · T8w test_engine_moat_trend_widening · T9 test_engine_default_is_stable · T10
  test_engine_bad_moat_trend · T11 test_iprd_composes_with_hold · T12 (guard) test_measure_run_keeps_moat_trend ·
  T27 test_recorded_args_carries_moat_trend.
Scorecard (moat_scorecard):     T13 test_trend_test_mirror · T14 test_fade_trend_cases (T14b PAYX-shaped plain-ROIC
  guard, T14c DD-shaped tangible-only erosion, T14d MOH-shaped ROA guard) · T15 test_widening_from_trough_flag · T15b
  test_commodity_guard_mechanical · T15c test_commodity_guard_reads_no_universe_csv · test_fade_leaves ·
  test_widening_declined_shape · test_fade_sync_record_consistency · test_rebuild_drift_switch (T19b) ·
  test_operating_margin_fallback_moves_the_trend (10b COVERAGE, lane default Q4). Review fixes (2026-10-21; they fail
  on 82ef9b9, r57/L3b/fix3/failing_first.log): test_unused_rebuttal_is_unchecked_on_a_rebuild (T19c in-process) ·
  test_hold_moved_values_and_trace_leaves_of_records.
Reprice (reprice):              T23 test_reprice_hold_zero_record · T23b test_reprice_reads_the_record_not_the_rule.
make_score end to end (T16-T22, T28): test_make_score_57_fade.py; T7 (the repo regression's replay through
recorded_scenario_holds): test_engine_math.py.
Every test except the two marked guards fails on 4f7d6f1 (r57/L3b/failing_first.log).
"""
import builtins
import copy
import csv
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SYS = os.path.dirname(HERE)
ROOT = os.path.dirname(SYS)
for _p in (HERE, SYS):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import engine55_harness as H  # noqa: E402
from test_engine_55 import run, APP_J, recorded_matching_fixture, assert_same_math, LABELS  # noqa: E402

E = H._shared_engine()          # the module make_score / moat_scorecard / reprice import (pure functions)
import moat_scorecard as M  # noqa: E402
import test_moat_scorecard as TM  # noqa: E402  (L3's fixtures: row, rows_of, fact, base_facts, base_scorecard, Case)

GT = 0.025
SPEC_HOLD = {"eroding": 0, "stable": 2, "widening": 3}   # the ruled holds (M6), written here independent of the code
RATES = ((0.10, "iv_at_10"), (0.12, "iv_at_12"), (0.15, "iv_at_15"), (0.20, "iv_at_20"), (0.25, "iv_at_25"))
YEARS = TM.YEARS


def spec_hold(g0, gterm, hold, rule="above_terminal"):
    """The design's per-scenario rule (10 §1.6): the run's hold above terminal, else 2 ("literal": always the run's)."""
    return hold if (rule == "literal" or g0 > gterm) else 2


def hold_record(n, trend, rule="above_terminal", offsets=None, strip_paths=False):
    """A 5.7-shaped copy of engine record n run at the M6 hold for `trend`: every scenario / weighted / headline figure
    the record carries recomputed with the engine's own valuation functions exactly as the 5.7 scenario loop computes
    them (project_path(hold=h), adjusted_value, adjusted_irr), per-scenario hold_years, the top-level and inputs hold
    keys, release 5.7.0 and a re-stamped content_hash. offsets: replace the record's (recomputing g_start too)."""
    m = copy.deepcopy(n)
    inp = m["inputs"]
    if offsets is not None:
        inp["offsets"] = list(offsets)
    hold = SPEC_HOLD[trend]
    gterm = inp.get("g_terminal", GT)
    cap = E.cap_years_for_moat(inp["moat"])
    c = E.iprd_charge_per_share(m)
    price, base = m["price"], m["base_oe_per_share"]
    flows_all = []
    paths, gpaths = {}, {}
    for i, lbl in enumerate(LABELS):
        g0 = max(E.GROWTH_FLOOR_START, min(E.GROWTH_CAP_START, m["g_base"] + inp["offsets"][i]))
        h = spec_hold(g0, gterm, hold, rule)
        flows = E.project_path(base * inp["mults"][i], g0, cap, gterm, hold=h)
        flows_all.append(flows)
        s = m["scenarios"][lbl]
        s["g_start"] = round(g0, 4)
        for r, k in RATES:
            if k in s:
                s[k] = E.adjusted_value(flows, r, gterm, c)
        irr, _cap, floor = E.adjusted_irr(flows, price, gterm, c)
        s["irr"] = irr
        if "irr_at_floor" in s:
            s["irr_at_floor"] = floor
        s["hold_years"] = h
        paths[lbl] = [round(f, 6) for f in flows]
        gpaths[lbl] = [round(g, 6) for g in E.growth_path(g0, cap, gterm, hold=h)]
    w = [sum(inp["probs"][i] * flows_all[i][t] for i in range(5)) for t in range(E.PROJECTION_YEARS)]
    wi = E.adjusted_irr(w, price, gterm, c)
    for r, k in RATES:
        if k in m["weighted"]:
            m["weighted"][k] = E.adjusted_value(w, r, gterm, c)
        if k in m and k != "iv_at_10":
            m[k] = E.adjusted_value(w, r, gterm, c)
    m["weighted"]["irr"] = wi[0]
    if "irr_at_floor" in m["weighted"]:
        m["weighted"]["irr_at_floor"] = wi[2]
    paths["weighted"] = [round(f, 6) for f in w]
    m["implied_irr_weighted"] = wi[0]
    m["implied_irr_base"] = m["scenarios"]["base"]["irr"]
    for k, lbl in (("irr_bear", "bear"), ("irr_bull", "bull")):
        if k in m:
            m[k] = m["scenarios"][lbl]["irr"]
    m["tier_by_numbers"] = E.tier_for_irr(wi[0])
    for k, rate in (("upside_at_15", 0.15), ("upside_at_12", 0.12)):
        if k in m:
            m[k] = E.adjusted_value(w, rate, gterm, c) / price - 1
    if strip_paths:
        m.pop("paths", None)
        m.pop("growth_paths", None)
    else:   # the 6-dp copies a 5.4+ engine stores
        m["paths"], m["growth_paths"] = paths, gpaths
    m["moat_trend"], m["hold_years"] = trend, hold
    inp.update(moat_trend=trend, hold_years=hold, hold_rule=rule)
    m["engine_release"] = "5.7.0"
    m["content_hash"] = E._content_hash(m)
    return m


def app_record():
    with open(os.path.join(ROOT, "APP", "dcf_numbers.json"), encoding="utf-8") as f:
        return json.load(f)


def close(a, b, tol=1e-12):
    return abs(a - b) <= tol * max(1.0, abs(b))


# ===========================================================================
# Engine math and the replay readers
# ===========================================================================
def test_hold_by_trend():
    """T1: the ruled map (Andrew, 2026-10-20) and the one source of truth for it."""
    assert E.HOLD_BY_TREND == {"eroding": 0, "stable": 2, "widening": 3}
    assert E.HOLD_YEARS == 2 and E.MOAT_TRENDS == ("eroding", "stable", "widening")
    for t, h in SPEC_HOLD.items():
        assert E.hold_years_for_trend(t) == h
    for bad in ("x", "Eroding", None, 0):
        try:
            E.hold_years_for_trend(bad)
            raise AssertionError(f"hold_years_for_trend({bad!r}) did not refuse")
        except ValueError:
            pass
    assert E.EXIT_BAD_MOAT_TREND == 5 and E.HOLD_RULE == "above_terminal" and E.HOLD_RULES["above_terminal"] is E.fade_hold


def test_fade_hold_only_above_terminal():
    """T2 (lane default Q6: the design's above-terminal rule): a scenario starting at or below terminal keeps 2."""
    assert E.fade_hold(0.10, GT, 0) == 0 and E.fade_hold(0.10, GT, 3) == 3
    assert E.fade_hold(-0.04, GT, 0) == 2 and E.fade_hold(0.025, GT, 3) == 2 and E.fade_hold(0.025, GT, 0) == 2
    for g in (-0.10, -0.04, 0.0, 0.02, 0.025, 0.0251, 0.08, 0.35, 0.50):
        assert E.fade_hold(g, GT, 2) == 2, g


def test_hold_zero_fades_from_year_one():
    """T3 (a guard — the hold parameter predates M6, so this passes on old code too): hold 0 fades from year 1, hold
    3 holds three years."""
    p0 = E.growth_path(0.30, 5, GT, hold=0)
    assert p0[0] == 0.30 - (0.30 - GT) / 5 * 1
    p3 = E.growth_path(0.30, 5, GT, hold=3)
    assert p3[:3] == [0.30, 0.30, 0.30] and p3[3] < 0.30


def test_hold_is_monotone_in_direction():
    """T4: under the per-scenario rule the value moves only in the ruled direction — PV at 15% of
    project_path(..., hold=fade_hold(g0, gterm, h)) satisfies h=0 <= h=2 <= h=3 for every start and CAP."""
    for g0 in (-0.10, 0.0, 0.025, 0.08, 0.35):
        for cap in (2, 8.5, 15):
            pv = {h: E.present_value(E.project_path(10.0, g0, cap, GT, hold=E.fade_hold(g0, GT, h)), 0.15, GT)
                  for h in (0, 2, 3)}
            assert pv[0] <= pv[2] <= pv[3], (g0, cap, pv)
            if g0 <= GT:
                assert pv[0] == pv[2] == pv[3], (g0, cap, pv)


def test_recorded_hold_years():
    """T5: the readers. Absent -> 2 (every pre-5.7 record); malformed -> None (not replayable); a record's
    per-scenario holds are returned as written; partial or impossible holds refuse."""
    assert E.recorded_hold_years({}) == 2 and E.recorded_hold_years({"inputs": {}}) == 2
    assert E.recorded_hold_years("x") == 2 and E.recorded_hold_years({"inputs": "x"}) == 2
    for h in (0, 3, 15):
        assert E.recorded_hold_years({"inputs": {"hold_years": h}}) == h
    for bad in (True, 2.0, "3", -1, 16, None):
        assert E.recorded_hold_years({"inputs": {"hold_years": bad}}) is None, bad
    g0s = [-0.04, 0.03, 0.08, 0.13, 0.20]
    legacy = {"inputs": {}, "scenarios": {k: {} for k in LABELS}}
    assert E.recorded_scenario_holds(legacy, g0s, GT) == [2] * 5
    run0 = {"inputs": {"hold_years": 0}, "scenarios": {k: {} for k in LABELS}}
    assert E.recorded_scenario_holds(run0, g0s, GT) == [2, 0, 0, 0, 0], "no per-scenario keys: fade_hold of the run hold"
    rec = {"inputs": {"hold_years": 0}, "scenarios": {k: {"hold_years": h} for k, h in zip(LABELS, (0, 0, 2, 0, 0))}}
    assert E.recorded_scenario_holds(rec, g0s, GT) == [0, 0, 2, 0, 0], "as written, even where fade_hold says otherwise"
    part = copy.deepcopy(rec)
    del part["scenarios"]["bull"]["hold_years"]
    assert E.recorded_scenario_holds(part, g0s, GT) is None
    for bad in (True, 2.0, 7, 3, -1):
        r = copy.deepcopy(rec)
        r["scenarios"]["base"]["hold_years"] = bad
        assert E.recorded_scenario_holds(r, g0s, GT) is None, bad
    assert E.recorded_scenario_holds({"inputs": {"hold_years": "x"}, "scenarios": {}}, g0s, GT) is None
    assert E.counterfactual_scenario_holds({"inputs": {}}, g0s, GT, 0) == [2, 0, 0, 0, 0]
    assert E.counterfactual_scenario_holds({"inputs": {"hold_rule": "above_terminal"}}, g0s, GT, 3) == [2, 3, 3, 3, 3]
    assert E.counterfactual_scenario_holds({"inputs": {"hold_rule": "nonsense"}}, g0s, GT, 0) is None
    assert E.counterfactual_scenario_holds({"inputs": {}}, g0s, GT, 2.0) is None


def test_replay_paths_reads_recorded_hold():
    """T6: an APP-shaped record run at hold 0 (per-scenario holds as the engine writes them, stored paths removed)
    replays to project_path(..., hold=scenarios[k].hold_years) exactly; the same record without the keys replays
    bit-identical to today's; replay_paths(n, hold=3) is a counterfactual that never returns the stored paths."""
    n = app_record()
    m = hold_record(n, "eroding", strip_paths=True)
    assert [m["scenarios"][k]["hold_years"] for k in LABELS] == [0] * 5   # APP's starts are all above terminal
    paths, gpaths = E.replay_paths(m)
    cap = E.cap_years_for_moat(m["inputs"]["moat"])
    for i, k in enumerate(LABELS):
        g0 = max(E.GROWTH_FLOOR_START, min(E.GROWTH_CAP_START, m["g_base"] + m["inputs"]["offsets"][i]))
        assert paths[k] == E.project_path(m["base_oe_per_share"] * m["inputs"]["mults"][i], g0, cap, GT, hold=0), k
        assert gpaths[k] == E.growth_path(g0, cap, GT, hold=0), k
    w = E.adjusted_irr(paths["weighted"], m["price"], GT, 0.0)[0]
    assert w == m["implied_irr_weighted"], (w, m["implied_irr_weighted"])
    p_old, g_old = E.replay_paths(n)
    for i, k in enumerate(LABELS):
        g0 = max(E.GROWTH_FLOOR_START, min(E.GROWTH_CAP_START, n["g_base"] + n["inputs"]["offsets"][i]))
        assert p_old[k] == E.project_path(n["base_oe_per_share"] * n["inputs"]["mults"][i], g0, cap, GT), k
    stored = hold_record(n, "eroding")
    assert stored["paths"] and E.replay_paths(stored)[0]["base"] == paths["base"], "the record replays, not the copy"
    p3, _ = E.replay_paths(stored, hold=3)
    g0b = max(E.GROWTH_FLOOR_START, min(E.GROWTH_CAP_START, stored["g_base"] + stored["inputs"]["offsets"][2]))
    assert p3 is not stored["paths"] and p3["base"] == E.project_path(stored["base_oe_per_share"], g0b, cap, GT, hold=3)
    drift = copy.deepcopy(stored)
    drift["paths"] = {k: [x * 2 for x in v] for k, v in drift["paths"].items()}
    assert E.replay_paths(drift)[0] is drift["paths"], "a drifted replay still yields to the stored record"
    assert E.replay_paths(drift, hold=3)[0] is not drift["paths"], "...but a counterfactual never returns it"
    assert E.replay_paths(dict(stored, inputs=dict(stored["inputs"], offsets=[0.0])), hold=3) == (None, None)
    assert E.replay_paths(dict(stored, inputs=dict(stored["inputs"], hold_rule="nonsense")), hold=3) == (None, None)
    bad = copy.deepcopy(m)
    bad["scenarios"]["bear"]["hold_years"] = 7
    assert E.replay_paths(bad) == (None, None), "a record whose holds disagree with its own trend is not replayable"


def test_replay_record_wins_over_the_code():
    """T6b: a hold-0 record written by a 'literal' engine (every scenario at the run's hold, inputs.hold_rule literal)
    whose below-terminal super_bear records hold_years 0 — today's fade_hold would give 2 — replays super_bear at hold
    0 and reproduces the weighted IRR bit for bit; swapping fade_hold for the literal rule changes nothing in that
    replay (the record is the source of truth)."""
    n = app_record()
    m = hold_record(n, "eroding", rule="literal", offsets=[-0.40, -0.13, -0.05, 0.03, 0.10], strip_paths=True)
    sb = m["scenarios"]["super_bear"]
    assert sb["g_start"] <= GT and sb["hold_years"] == 0 and E.fade_hold(sb["g_start"], GT, 0) == 2
    paths, _ = E.replay_paths(m)
    assert E.adjusted_irr(paths["weighted"], m["price"], GT, 0.0)[0] == m["implied_irr_weighted"]
    assert E.adjusted_irr(paths["super_bear"], m["price"], GT, 0.0)[0] == sb["irr"]
    saved = E.HOLD_RULES["above_terminal"]
    try:
        E.HOLD_RULES["above_terminal"] = lambda g0, gterm, h: h
        p2, _ = E.replay_paths(m)
        assert p2 == paths
    finally:
        E.HOLD_RULES["above_terminal"] = saved


# ===========================================================================
# Engine runs (engine55_harness, offline fixtures)
# ===========================================================================
_RUNS = {}


def _app_run(extra=()):
    key = tuple(extra)
    if key not in _RUNS:
        rec = recorded_matching_fixture("APP")
        out = run("APP", H.recorded_args(rec) + list(extra), judgment=APP_J,
                  ttm={"ttm_oe_per_share": rec["base_oe_per_share"]})
        assert out["exit"] == 0, out["stdout"][-1500:]
        _RUNS[key] = out["numbers"]
    return _RUNS[key]


def _flags(n, prefix):
    return [f for f in n.get("fragility_flags") or [] if str(f).startswith(prefix)]


def test_engine_moat_trend_eroding():
    """T8 (APP fixture): --moat-trend eroding records moat_trend / hold_years 0 at the top level and in inputs (with
    hold_rule), every scenario's hold (fade_hold of 0), paths equal to project_path at those holds, the MOAT_TREND_HOLD
    flag, a content_hash that recomputes, and a weighted IRR below the stable run's."""
    n, s = _app_run(["--moat-trend", "eroding"]), _app_run()
    assert n["moat_trend"] == "eroding" and n["hold_years"] == 0
    assert n["inputs"]["moat_trend"] == "eroding" and n["inputs"]["hold_years"] == 0
    assert n["inputs"]["hold_rule"] == "above_terminal"
    cap = E.cap_years_for_moat(n["inputs"]["moat"])
    for i, k in enumerate(LABELS):
        g0 = max(E.GROWTH_FLOOR_START, min(E.GROWTH_CAP_START, n["g_base"] + n["inputs"]["offsets"][i]))
        assert n["scenarios"][k]["hold_years"] == spec_hold(g0, GT, 0)
        flows = E.project_path(n["base_oe_per_share"] * n["inputs"]["mults"][i], g0, cap, GT,
                               hold=n["scenarios"][k]["hold_years"])
        assert n["paths"][k] == [round(f, 6) for f in flows], k
        assert n["scenarios"][k]["irr"] == E.adjusted_irr(flows, n["price"], GT, E.iprd_charge_per_share(n))[0]
    fl = _flags(n, "MOAT_TREND_HOLD")
    assert fl == ["MOAT_TREND_HOLD: moat eroding — growth hold 0 years (default 2): the fade starts in year 1 for every "
                  "scenario that starts above terminal growth (make_score's trend test; an erosion_rebuttal restores 2)"], fl
    assert E._content_hash(n) == n["content_hash"]
    assert n["implied_irr_weighted"] < s["implied_irr_weighted"] and n["base_oe_per_share"] == s["base_oe_per_share"]
    assert n["g_base"] == s["g_base"] and n["cap_years"] == s["cap_years"]


def test_engine_moat_trend_widening():
    """T8w: --moat-trend widening holds 3 years on every scenario above terminal, raises the IRR, and says in its flag
    that a cyclical upswing looks like widening."""
    n, s = _app_run(["--moat-trend", "widening"]), _app_run()
    assert n["moat_trend"] == "widening" and n["hold_years"] == 3 and n["inputs"]["hold_years"] == 3
    assert [n["scenarios"][k]["hold_years"] for k in LABELS] == [3] * 5
    assert n["implied_irr_weighted"] > s["implied_irr_weighted"]
    fl = _flags(n, "MOAT_TREND_HOLD")
    assert len(fl) == 1 and "growth hold 3 years (default 2)" in fl[0] and "cyclical upswing" in fl[0], fl


def test_engine_default_is_stable():
    """T9: no flag = stable / hold 2: the new keys only — the valuation is APP's recorded run bit for bit, every
    scenario records hold 2, no MOAT_TREND_HOLD flag — and an explicit --moat-trend stable writes the same record."""
    n = _app_run()
    rec = recorded_matching_fixture("APP")
    assert n["moat_trend"] == "stable" and n["hold_years"] == 2
    assert {k: n["inputs"][k] for k in ("moat_trend", "hold_years", "hold_rule")} == {
        "moat_trend": "stable", "hold_years": 2, "hold_rule": "above_terminal"}
    assert [n["scenarios"][k]["hold_years"] for k in LABELS] == [2] * 5
    assert_same_math(n, rec, "APP default stable")
    assert not _flags(n, "MOAT_TREND_HOLD")
    for k in rec["inputs"]:
        assert n["inputs"][k] == rec["inputs"][k], k
    assert _app_run(["--moat-trend", "stable"])["content_hash"] == n["content_hash"]


def test_engine_bad_moat_trend():
    """T10: --moat-trend falling exits 5 (BAD_MOAT_TREND), checked before any fetch (the companyfacts stub records zero
    calls); a valid value with an unknown ticker still exits 2 (NO_CIK) — the two codes stay distinct."""
    calls = []

    def patch(Eng):
        real = Eng.get_json

        def counting(url, *a, **k):
            calls.append(url)
            return real(url, *a, **k)
        Eng.get_json = counting
    out = run("APP", ["--moat", "6", "--moat-trend", "falling"], judgment=APP_J, patch=patch)
    assert out["exit"] == 5 and out["stdout"].startswith("BAD_MOAT_TREND"), (out["exit"], out["stdout"][:300])
    assert "eroding, stable, widening" in out["stdout"] and "moat_scorecard.py" in out["stdout"]
    assert calls == [] and out["numbers"] is None
    fx = H.load_fixture("APP")
    out2 = run("NOPE", ["--moat", "6", "--moat-trend", "stable"], judgment={}, fixture=fx)
    assert out2["exit"] == 2 and "NO_CIK" in out2["stdout"], (out2["exit"], out2["stdout"][:300])


def test_iprd_composes_with_hold():
    """T11 (HALO fixture with test_engine_iprd's inputs — the TTM base, its ttm.json share count, the cash-flow check):
    the one-time IPR&D charge acts after the flows, so on an eroding run every scenario IV is present_value(flows at
    hold 0) - charge and every IRR solve_irr(flows, price + charge); iprd_adjustment.before is the unadjusted value on
    the same hold-0 flows; the base, g_base, the charge, its share denominator and its periods equal the stable run's."""
    import test_engine_iprd as TI
    fx = H.load_fixture("HALO")
    e = run("HALO", TI.HALO_ARGS + ["--moat-trend", "eroding"], judgment=TI.HALO_J, ttm=TI.HALO_TTM, fixture=fx)
    s = run("HALO", TI.HALO_ARGS, judgment=TI.HALO_J, ttm=TI.HALO_TTM, fixture=fx)
    assert e["exit"] == 0 and s["exit"] == 0, (e["stdout"][-800:], s["stdout"][-800:])
    n, st = e["numbers"], s["numbers"]
    for k in ("base_oe_per_share", "g_base", "cap_years"):
        assert n[k] == st[k], k
    for k in ("charge_per_share", "shares_denominator", "periods", "treatment"):
        assert n["iprd_adjustment"][k] == st["iprd_adjustment"][k], k
    c = n["iprd_adjustment"]["charge_per_share"]
    assert c > 0 and E.iprd_charge_per_share(n) == c
    cap = E.cap_years_for_moat(n["inputs"]["moat"])
    all_f = []
    for i, k in enumerate(LABELS):
        g0 = max(E.GROWTH_FLOOR_START, min(E.GROWTH_CAP_START, n["g_base"] + n["inputs"]["offsets"][i]))
        h = n["scenarios"][k]["hold_years"]
        assert h == spec_hold(g0, GT, 0)
        flows = E.project_path(n["base_oe_per_share"] * n["inputs"]["mults"][i], g0, cap, GT, hold=h)
        all_f.append(flows)
        for r, key in RATES:
            assert n["scenarios"][k][key] == E.present_value(flows, r, GT) - c, (k, key)
            assert n["iprd_adjustment"]["before"][k][key] == E.present_value(flows, r, GT), (k, key)
        assert n["scenarios"][k]["irr"] == E.solve_irr(flows, n["price"] + c, GT)[0], k
    w = [sum(n["inputs"]["probs"][i] * all_f[i][t] for i in range(5)) for t in range(15)]
    assert n["implied_irr_weighted"] == E.solve_irr(w, n["price"] + c, GT)[0]
    assert n["implied_irr_weighted"] < st["implied_irr_weighted"]
    print(f"   HALO weighted IRR: hold 0 {n['implied_irr_weighted'] * 100:.2f}% (tier {n['tier_by_numbers']}) vs hold 2 "
          f"{st['implied_irr_weighted'] * 100:.2f}% (tier {st['tier_by_numbers']})")


def test_measure_run_keeps_moat_trend():
    """T12 (a guard — _measure_run already passed argv through): the override-impact replay keeps --moat-trend."""
    Eng = H._engine()
    seen = {}

    class Out:
        stdout = '{"base_oe_per_share": 1.0, "implied_irr_weighted": 0.1}'

    def fake_run(args, **k):
        seen["args"] = args
        return Out()
    saved_argv, saved_run = sys.argv, subprocess.run
    sys.argv = ["dcf_engine.py", "APP", "--moat", "5", "--moat-trend", "eroding", "--ttm"]
    Eng.subprocess.run = fake_run
    try:
        assert Eng._measure_run("APP", 10.0, True) == (1.0, 0.1)
    finally:
        sys.argv = saved_argv
        Eng.subprocess.run = saved_run
    a = seen["args"]
    i = a.index("--moat-trend")
    assert a[i + 1] == "eroding" and "--ttm" not in a and "--measure" in a, a


def test_recorded_args_carries_moat_trend():
    """T27: engine55_harness.recorded_args replays a 5.7 record's inputs.moat_trend right after the --gterm pair, so a
    hold-0 fixture replays at hold 0 (a legacy record: no flag, the engine default); the replay on the APP fixture
    reproduces the record's hold_years and per-scenario holds."""
    n = _app_run(["--moat-trend", "eroding"])
    args = H.recorded_args(n)
    g = args.index("--gterm")
    assert args[g + 2:g + 4] == ["--moat-trend", "eroding"], args
    assert "--moat-trend" not in H.recorded_args(recorded_matching_fixture("APP"))
    rec = recorded_matching_fixture("APP")
    out = run("APP", args, judgment=APP_J, ttm={"ttm_oe_per_share": rec["base_oe_per_share"]})
    assert out["exit"] == 0
    m = out["numbers"]
    assert m["hold_years"] == 0 and [m["scenarios"][k]["hold_years"] for k in LABELS] == [
        n["scenarios"][k]["hold_years"] for k in LABELS]
    assert m["implied_irr_weighted"] == n["implied_irr_weighted"]


# ===========================================================================
# The trend test, the guards and the fade block (moat_scorecard)
# ===========================================================================
def _rows(g, gm, measure="roic"):
    """Bare per-year rows for trend_test: the governing value and the gross margin."""
    return [{"fy": str(y), measure: v, "gross_margin": m} for y, v, m in zip(YEARS[-len(g):], g, gm)]


def test_trend_test_mirror():
    """T13: one test, two directions (10 §1.1): returns +4pp and +25% with gross margin +2.5pp -> widening; the exact
    negation -> eroding (03b's erosion); returns up / margin down -> contradicting; returns up only -> flat; 3 margin
    years -> not measured (no_margin); the last year unbounded -> not measured (governing_not_finite); a change of
    exactly +3.00pp and exactly +2.00pp passes although the float sums land a hair below."""
    roc = {"metric": "roic"}
    src = "fundamentals.json"
    up = M.trend_test(roc, _rows([0.16, 0.16, 0.18, 0.20, 0.20], [0.40, 0.40, 0.41, 0.425, 0.425]), src)
    assert up["status"] == "measured" and up["direction"] == "widening" and up["returns_up"] and up["margin_up"]
    assert up["governing_change_pp"] == 4.0 and up["margin_change_pp"] == 2.5 and up["margin_basis"] == "gross"
    dn = M.trend_test(roc, _rows([0.20, 0.20, 0.18, 0.16, 0.16], [0.425, 0.425, 0.41, 0.40, 0.40]), src)
    assert dn["direction"] == "eroding" and M.erosion_view(dn)["fired"] is True, dn
    assert M.trend_test(roc, _rows([0.16, 0.16, 0.18, 0.20, 0.20], [0.425, 0.425, 0.41, 0.40, 0.40]), src)["direction"] == "contradicting"
    assert M.trend_test(roc, _rows([0.20, 0.20, 0.18, 0.16, 0.16], [0.40, 0.40, 0.41, 0.425, 0.425]), src)["direction"] == "contradicting"
    assert M.trend_test(roc, _rows([0.16, 0.16, 0.18, 0.20, 0.20], [0.40] * 5), src)["direction"] == "flat"
    nm = M.trend_test(roc, _rows([0.16, 0.16, 0.18, 0.20, 0.20], [None, None, 0.41, 0.42, 0.43]), src)
    assert nm["status"] == "not_measured" and nm["reason"] == "no_margin" and nm["direction"] is None
    inf = _rows([0.16, 0.16, 0.18, 0.20, None], [0.40] * 5)
    inf[-1]["roic_note"] = "unbounded_high"
    assert M.trend_test(roc, inf, src)["reason"] == "governing_not_finite"
    assert M.trend_test(roc, _rows([0.16, 0.16, 0.18, 0.20, 0.20], [0.40] * 5), "financials_history.csv")["reason"] == "csv_only"
    # exactly the thresholds: (0.142 + 0.142) / 2 - (0.112 + 0.112) / 2 is 0.02999999999999998 in floats, and
    # 0.42 - 0.40 is 0.01999999999999996 — inclusive bounds still pass them
    a, b = 0.112, 0.142
    assert (b + b) / 2 - (a + a) / 2 < 0.03 and (0.42 + 0.42) / 2 - (0.40 + 0.40) / 2 < 0.02, "fixture lands below"
    ex = M.trend_test(roc, _rows([a, a, 0.127, b, b], [0.40, 0.40, 0.41, 0.42, 0.42]), src)
    assert ex["returns_up"] and ex["margin_up"] and ex["direction"] == "widening", ex
    # the erosion view keeps 03b's shape and adds the direction
    v = M.erosion_view(up)
    assert list(v) == ["status", "fired", "governing_change_pp", "margin_change_pp", "margin_basis", "slope_governing",
                       "slope_margin", "reason", "governing_first2", "governing_last2", "direction"], list(v)
    assert v["direction"] == "widening" and v["fired"] is False


UPV = [0.15, 0.16, 0.20, 0.24, 0.26]           # roic +9.5pp, median 20% (+2 on the default ladder)
UPGM = [0.40, 0.41, 0.42, 0.43, 0.44]           # gross margin +3pp
DNV = [0.30, 0.29, 0.26, 0.22, 0.20]            # L3's DOWN: -8.5pp
DNGM = [0.45, 0.44, 0.42, 0.41, 0.40]           # -4pp


def _scn():
    return {k: {"prob": 0.2, "g_start": 0.08} for k in LABELS}


def _case_fade(rows, sc="base", sic="3561", moat=6, extra_facts=(), n_extra=None, is_57=True, sync=False, mut=None):
    c = TM.Case(rows=rows, sic=sic, moat=moat, facts=TM.base_facts() + list(extra_facts),
                n_extra=dict({"scenarios": _scn()}, **(n_extra or {})), sc=sc)
    try:
        if mut:
            mut(c)
        return M.evaluate(c.folder, c.n, c.j, facts={f["id"]: f for f in c.facts}, is_57=is_57, sic=c.sic, sync=sync)
    finally:
        c.close()


def _gm_rows(vals, gms, **kw):
    return [TM.row(y, v, gross_margin=g, **kw) for y, v, g in zip(YEARS, vals, gms)]


def test_fade_trend_cases():
    """T14: 10 §1.2 row by row on a 5.7 record with scenarios (sync off: the rule, not the engine record, is tested
    here) — eroding -> eroding_not_rebutted hold 0; rebutted -> 2; widening with every guard -> widening_confirmed hold
    3; declined -> 2; a guard failing alone -> widening_guard_failed hold 2 with the guard named; flat -> no_trend;
    contradicting; not measured; an unused rebuttal / decline is flagged; a pre-5.7 record is report_only (the
    counterfactual flagged report_only); a Tier F record is no_projection."""
    f = _case_fade(_gm_rows(DNV, DNGM))["fade"]
    assert (f["direction"], f["rule"], f["trend"], f["hold_years"]) == ("eroding", "eroding_not_rebutted", "eroding", 0)
    sc = TM.base_scorecard()
    sc["erosion_rebuttal"] = "a price cycle: price realization 4.5% [F3]"
    f = _case_fade(_gm_rows(DNV, DNGM), sc=sc)["fade"]
    assert (f["rule"], f["trend"], f["hold_years"], f["rebuttal_declared"], f["rebuttal_unused"]) == (
        "eroding_rebutted", "stable", 2, True, False)
    ev = _case_fade(_gm_rows(UPV, UPGM))
    f = ev["fade"]
    assert (f["direction"], f["rule"], f["trend"], f["hold_years"]) == ("widening", "widening_confirmed", "widening", 3), f
    g = f["guards"]
    assert g["applies"] and g["fact_backed_source"] is True and g["source"] == "switching_costs/embedded_component"
    assert g["returns_on_capital"] == 2 and g["plain_roic_agrees"] is None and g["roa_agrees"] is None and g["failed"] == []
    assert g["commodity_sic"]["passes"] and g["commodity_sic"]["basis"] is None and g["commodity_sic"]["sic"] == "3561"
    assert ev["flags"][0] == "MOAT_WIDENING" and "MOAT_EROSION" not in ev["flags"]
    sc = TM.base_scorecard()
    sc["widening_declined"] = "a recovery from the 2021 trough, not a wider moat"
    f = _case_fade(_gm_rows(UPV, UPGM), sc=sc)["fade"]
    assert (f["rule"], f["trend"], f["hold_years"], f["decline_declared"], f["decline_unused"]) == (
        "widening_declined", "stable", 2, True, False)
    # each guard failing alone
    sc = TM.base_scorecard()                                              # guard 1: no fact-backed source
    sc["sources"] = [TM.src("switching_costs", "embedded_component", facts=(), metrics=("returns_on_capital",))]
    try:
        _case_fade(_gm_rows(UPV, UPGM), sc=sc)
        raise AssertionError("W8 (a) should refuse a returns_on_capital source with no fact")
    except M.MoatRefusal:
        pass
    sc["sources"] = [TM.src("switching_costs", "embedded_component", facts=(), metrics=("scale_economics",))]
    f = _case_fade(_gm_rows(UPV, UPGM), sc=sc)["fade"]
    assert f["rule"] == "widening_guard_failed" and f["hold_years"] == 2 and f["guards"]["fact_backed_source"] is False
    assert f["guards"]["failed"][0].startswith("no fact-backed source"), f["guards"]["failed"]
    low = [0.08, 0.085, 0.12, 0.13, 0.14]                                  # guard 2: returns_on_capital 0 (median 12%)
    f = _case_fade(_gm_rows(low, UPGM), moat=5)["fade"]
    assert f["direction"] == "widening" and f["rule"] == "widening_guard_failed"
    assert f["guards"]["failed"] == ["returns_on_capital +0 < +1"], f["guards"]["failed"]
    f = _case_fade(_gm_rows(UPV, UPGM), sic="1040")["fade"]               # guard 4: commodity SIC
    assert f["rule"] == "widening_guard_failed" and f["guards"]["commodity_sic"]["basis"] == "sic"
    assert f["guards"]["failed"][0].startswith("commodity SIC 1040, declared industrial — a commodity price upcycle")
    f = _case_fade(_gm_rows(UPV, [0.40] * 5))["fade"]
    assert (f["direction"], f["rule"], f["trend"], f["hold_years"]) == ("flat", "no_trend", "stable", 2)
    f = _case_fade(_gm_rows(UPV, [0.44, 0.43, 0.42, 0.41, 0.40]))["fade"]
    assert (f["direction"], f["rule"], f["hold_years"]) == ("contradicting", "contradicting", 2)
    f = _case_fade(_gm_rows(UPV, [None] * 5, operating_income=None, pretax_income=None))["fade"]
    assert f["status"] == "not_measured" and f["rule"] == "not_measured" and f["hold_years"] == 2
    sc = TM.base_scorecard()
    sc["erosion_rebuttal"], sc["widening_declined"] = "cycle 4.5% [F3]", "a recovery"
    f = _case_fade(_gm_rows(UPV, [0.40] * 5), sc=sc)["fade"]
    assert f["rebuttal_unused"] is True and f["decline_unused"] is True and f["rule"] == "no_trend"
    # pre-5.7 record (report_only): the would-be hold's counterfactual is flagged report_only (no inputs: not replayable)
    f = _case_fade(_gm_rows(DNV, DNGM), sc=None, is_57=False)["fade"]
    assert (f["rule"], f["trend"], f["hold_years"], f["in_sync"]) == ("report_only", None, None, None)
    assert f["counterfactual"][0]["hold_years"] == 0 and f["counterfactual"][0]["report_only"] is True
    # a Tier F record (no scenarios): no projection, no counterfactual
    f = _case_fade(_gm_rows(UPV, UPGM), n_extra={"scenarios": {}})["fade"]
    assert (f["rule"], f["trend"], f["hold_years"], f["counterfactual"]) == ("no_projection", None, None, [])


def _tangible_rows(plain, gw, gms, equity=1000.0):
    """Rows whose plain ROIC is plain[i] (operating income = plain x equity, tax 0, IC = equity) and whose goodwill is
    gw[i] — tangible ROIC = operating income / (equity - goodwill)."""
    return [TM.row(y, p, goodwill=g, gross_margin=m, equity=equity) for y, p, g, m in zip(YEARS, plain, gw, gms)]


def test_fade_trend_tangible_and_roe_guards():
    """T14b (PAYX-shaped): tangible ROIC governs and rises while plain ROIC falls 45% -> 24.5% (goodwill from a
    debt-funded acquisition shrinks the tangible base) -> guard 3 fails, hold 2, the plain-ROIC text named; plain ROIC
    up 20% -> 30% -> widening_confirmed; a HALO-shaped plain +1.32pp fails. T14c (DD-shaped): a tangible-only erosion
    (plain -2.73pp, under 3pp) is NOT exempted — eroding_not_rebutted, hold 0 — and its plain-ROIC figures are rebuttal
    anchors (fade_anchor_leaves), never numeric_leaves. T14d (MOH-shaped, ROE governs at SIC 6324): ROE +8pp on a
    shrinking equity base while ROA falls 5.91% -> 5.29% -> guard 3b fails; ROA 4.0% -> 7.5% -> confirmed; ROA not
    measured fails; a ROIC-governed widening reads roa_agrees None."""
    gm = [0.40, 0.40, 0.41, 0.422, 0.422]
    payx = _tangible_rows([0.45, 0.45, 0.35, 0.245, 0.245], [400, 400, 750, 900, 900], gm)
    ev = _case_fade(payx)
    f = ev["fade"]
    assert f["measure"] == "roic_tangible" and f["direction"] == "widening", (f["measure"], f["direction"])
    assert f["plain_roic"]["status"] == "measured" and f["plain_roic"]["change_pp"] == -20.5 and f["plain_roic"]["down"]
    assert f["guards"]["plain_roic_agrees"] is False and f["rule"] == "widening_guard_failed" and f["hold_years"] == 2
    assert f["guards"]["failed"] == [
        f"plain roic -20.50pp (FY2021-22 avg 45.00% -> FY2024-25 avg 24.50%) does not pass the widening thresholds while "
        f"tangible roic governs ({f['governing_change_pp']:+.2f}pp) — widening on tangible returns alone can be "
        "acquisition goodwill shrinking the tangible base (03c decision 2)"], f["guards"]["failed"]
    good = _tangible_rows([0.20, 0.20, 0.25, 0.30, 0.30], [400] * 5, gm)
    f = _case_fade(good)["fade"]
    assert f["measure"] == "roic_tangible" and f["guards"]["plain_roic_agrees"] is True
    assert (f["rule"], f["hold_years"]) == ("widening_confirmed", 3), (f["rule"], f["guards"]["failed"])
    halo = _tangible_rows([0.1895, 0.1895, 0.195, 0.2027, 0.2027], [400, 400, 500, 600, 600], gm)
    f = _case_fade(halo)["fade"]
    assert f["plain_roic"]["change_pp"] == 1.32 and f["guards"]["plain_roic_agrees"] is False
    assert f["rule"] == "widening_guard_failed"
    # T14c: DD-shaped tangible-only erosion
    dd = _tangible_rows([0.0463, 0.0463, 0.035, 0.019, 0.019], [500] * 5, [0.40, 0.40, 0.39, 0.3776, 0.3776])
    ev = _case_fade(dd)
    f = ev["fade"]
    assert f["measure"] == "roic_tangible" and f["direction"] == "eroding", (f["measure"], f["direction"])
    assert (f["rule"], f["hold_years"]) == ("eroding_not_rebutted", 0)
    assert f["plain_roic"]["change_pp"] == -2.73 and not f["plain_roic"]["down"]
    anchors = M.fade_anchor_leaves(ev)
    assert -2.73 in anchors and -0.0273 in anchors and 0.0463 in anchors, anchors
    assert -2.73 not in M.numeric_leaves(ev) and -0.0273 not in M.numeric_leaves(ev), "fade figures never numeric_leaves"
    assert -2.73 not in M.fade_trace_leaves(ev)["values"], "in the anchor case the plain figures anchor, not trace"
    roic_eroding = _case_fade(_gm_rows(DNV, DNGM))
    assert M.fade_anchor_leaves(roic_eroding) == [], "a roic-governed erosion has no anchor leaves"
    # T14d: ROE governs (SIC 6324 is locked to financial_balance_sheet)
    sc = TM.base_scorecard()
    sc["business_type"] = "financial_balance_sheet"
    sc["business_type_reason"] = "Managed care: 100% of revenue is premiums (segments.json)."

    def roe_rows(ni, eq, assets, gms):
        return [TM.row(y, 0.10, net_income=n_, equity=e_, assets=a_, liabilities=(a_ - e_) if a_ else None, gross_margin=m_)
                for y, n_, e_, a_, m_ in zip(YEARS, ni, eq, assets, gms)]
    gm2 = [0.15, 0.15, 0.16, 0.171, 0.171]
    moh = roe_rows([320] * 5, [1000, 1000, 889, 800, 800], [5414.55, 5414.55, 5700, 6049.15, 6049.15], gm2)
    f = _case_fade(moh, sc=sc, sic="6324")["fade"]
    assert f["measure"] == "roe" and f["direction"] == "widening", (f["measure"], f["direction"], f["governing_change_pp"])
    assert f["roa"]["status"] == "measured" and f["roa"]["change_pp"] == -0.62, f["roa"]
    assert f["guards"]["roa_agrees"] is False and f["rule"] == "widening_guard_failed" and f["hold_years"] == 2
    assert any(x.startswith("roa -0.62pp (FY2021-22 avg 5.91% -> FY2024-25 avg 5.29%) does not pass the widening "
                            "thresholds while roe governs (+8.00pp) — ROE rising on a shrinking equity base can be "
                            "buybacks, not a widening moat") for x in f["guards"]["failed"]), f["guards"]["failed"]
    ok = roe_rows([320] * 5, [1000, 1000, 889, 800, 800], [8000, 8000, 6000, 4266.67, 4266.67], gm2)
    f = _case_fade(ok, sc=sc, sic="6324")["fade"]
    assert f["guards"]["roa_agrees"] is True and f["rule"] == "widening_confirmed", f["guards"]["failed"]
    nm = roe_rows([320] * 5, [1000, 1000, 889, 800, 800], [None, None, 6000, 4266.67, 4266.67], gm2)
    f = _case_fade(nm, sc=sc, sic="6324")["fade"]
    assert f["roa"]["status"] == "not_measured" and f["guards"]["roa_agrees"] is False
    assert f["rule"] == "widening_guard_failed"
    f = _case_fade(_gm_rows(UPV, UPGM))["fade"]
    assert f["guards"]["roa_agrees"] is None and f["roa"] is None and f["plain_roic"] is None


def test_widening_from_trough_flag():
    """T15: a widening whose first-two-year governing average sits below the cost-of-capital line (10% default ladder)
    is flagged WIDENING_FROM_TROUGH (moat_evidence.flags, after MOAT_WIDENING, and fade.flags); it never changes the
    hold — a confirmed widening from a trough still holds 3."""
    ev = _case_fade(_gm_rows([0.08, 0.08, 0.20, 0.30, 0.30], UPGM))
    f = ev["fade"]
    assert f["flags"] == ["WIDENING_FROM_TROUGH"] and f["trough"] == {"governing_first2": 0.08, "line": 0.10}
    assert ev["flags"][:2] == ["MOAT_WIDENING", "WIDENING_FROM_TROUGH"] and f["rule"] == "widening_confirmed"
    assert f["hold_years"] == 3
    f = _case_fade(_gm_rows([0.12, 0.12, 0.20, 0.30, 0.30], UPGM))["fade"]
    assert f["flags"] == [] and f["trough"] is None and f["rule"] == "widening_confirmed"
    kn = "\n".join(M.key_numbers_lines(ev))
    assert "- Flags: MOAT_WIDENING, WIDENING_FROM_TROUGH (first-two-year governing average 8.00% < 10.00%)" in kn, kn


def test_commodity_guard_mechanical():
    """T15b (guard 4 on committed SEC data; 10b OQ10): SIC 1040 or 1400 declared industrial fails (basis sic); SIC 6199
    with ASC 606 contract revenue fails (the 6199 operating lock, IREN-shaped) while 6199 with `Revenues` passes
    (CHYM-shaped); no SIC fails closed; declared commodity_producer fails at any SIC. The one exemption: a
    business_type_reason quoting a cited, non-third-party COST-POSITION fact tagged business_type_reason (cash cost
    per unit vs peers); a revenue-share number, a reason with no number, the trend's own figure or a third-party
    cost fact does not lift it."""
    G = M.commodity_guard
    for sic in ("1040", "1400", 2911, "4412"):
        g = G("industrial", sic, {"revenue_basis": "Revenues"}, "x", {})
        assert g["basis"] == "sic" and g["passes"] is False, (sic, g)
    g = G("industrial", "1040", None, None, {})
    assert g["detail"] == ("commodity SIC 1040, declared industrial — a commodity price upcycle is not a widening moat; "
                           "business_type_reason must carry a cost-position number (cost-curve position or cash cost per "
                           "unit vs peers) from a cited non-third-party fact tagged business_type_reason to lift this guard")
    iren = {"fy": "2025", "revenue_basis": "RevenueFromContractWithCustomerExcludingAssessedTax"}
    g = G("financial_balance_sheet", "6199", iren, None, {})
    assert g["basis"] == "sic_6199_operating" and not g["passes"] and g["revenue_basis"] == iren["revenue_basis"]
    assert g["detail"].startswith("SIC 6199 with contract revenue (RevenueFromContractWithCustomerExcludingAssessedTax, "
                                  "FY2025): an operating business filed under finance services")
    g = G("financial_balance_sheet", "6199", {"revenue_basis": "Revenues"}, None, {})
    assert g["passes"] and g["basis"] is None
    g = G("industrial", None, None, None, {})
    assert g["basis"] == "sic_unknown" and not g["passes"] and "fails closed" in g["detail"]
    g = G("commodity_producer", "7372", None, "cash cost $412/t [F2]", {})
    assert g["basis"] == "declared" and not g["passes"]
    assert G("enterprise_recurring", "7372", None, None, {})["passes"]
    cost = TM.fact("F2", "cash_cost_per_unit", "FY2025", 412, unit="USD", type="actual", used=("business_type_reason",))
    share = TM.fact("F2", "branded_revenue_share", "FY2025", 0.96, unit="pct", type="actual", used=("business_type_reason",))
    tp = dict(cost, kind="third_party", source={"url": "https://example.com/x", "publisher": "X", "published": "2026-01-05"})
    untagged = dict(cost, used_for=["context"])
    ok = G("consumer_brands_retail", "2060", None, "cash cost $412 per tonne vs a peer median of $530 [F2]", {"F2": cost})
    assert ok["passes"] and ok["exempted_by_reason"] and ok["exempt_fact"] == "F2" and ok["basis"] == "sic"
    for reason, facts in (("branded confectionery 96% of net sales FY2025 [F2]", {"F2": share}),
                          ("a branded franchise [F2]", {"F2": cost}),
                          ("returns rose 9.50pp", {}),
                          ("cash cost $412 per tonne [F2]", {"F2": tp}),
                          ("cash cost $412 per tonne [F2]", {"F2": untagged}),
                          ("cash cost $400 per tonne [F2]", {"F2": cost})):
        g = G("consumer_brands_retail", "2060", None, reason, facts)
        assert not g["passes"] and not g["exempted_by_reason"], (reason, g)
    # through evaluate: a widening at SIC 1040 declared industrial fails guard 4 alone; a cost-position fact lifts it
    f = _case_fade(_gm_rows(UPV, UPGM), sic="1040")["fade"]
    assert f["rule"] == "widening_guard_failed" and len(f["guards"]["failed"]) == 1
    sc = TM.base_scorecard()
    sc["business_type_reason"] = "First-quartile cost: cash cost $412 per tonne [F30] (industrial service revenue 70%)"
    f30 = TM.fact("F30", "cash_cost_per_unit", "FY2025", 412, unit="USD", type="actual", used=("business_type_reason",))
    f = _case_fade(_gm_rows(UPV, UPGM), sic="1040", sc=sc, extra_facts=[f30])["fade"]
    assert f["rule"] == "widening_confirmed" and f["guards"]["commodity_sic"]["exempted_by_reason"], f["guards"]


def test_commodity_guard_reads_no_universe_csv():
    """T15c: the guard never opens _system/universe.csv (Nasdaq's sector is rewritten on every universe rebuild): with
    no universe.csv, with one whose row says Energy, and with one lacking the ticker, the fade block is byte-identical;
    an open() of any universe.csv path would raise; the dry run completes in a base without the file."""
    real_open = builtins.open
    opened = []

    def guarded(path, *a, **k):
        if str(path).replace("\\", "/").endswith("universe.csv"):
            opened.append(path)
            raise AssertionError(f"universe.csv opened: {path}")
        return real_open(path, *a, **k)
    blocks = []
    builtins.open = guarded
    try:
        for sic in ("7372", "1040"):
            for uni in (None, "TST,Energy\n", "ZZZ,Technology\n"):
                def mut(c, uni=uni):
                    if uni is not None:
                        sysd = os.path.join(c.tmp, "_system")
                        os.makedirs(sysd, exist_ok=True)
                        with real_open(os.path.join(sysd, "universe.csv"), "w", encoding="utf-8") as fh:
                            fh.write("ticker,sector\n" + uni)
                blocks.append((sic, json.dumps(_case_fade(_gm_rows(UPV, UPGM), sic=sic, mut=mut)["fade"], sort_keys=True)))
    finally:
        builtins.open = real_open
    assert opened == []
    for sic in ("7372", "1040"):
        bs = {b for s, b in blocks if s == sic}
        assert len(bs) == 1, f"SIC {sic}: the fade block moved with universe.csv"
    by = {s: json.loads(b) for s, b in blocks}
    assert by["7372"]["guards"]["commodity_sic"]["passes"] and not by["1040"]["guards"]["commodity_sic"]["passes"]
    assert by["1040"]["guards"]["commodity_sic"]["basis"] == "sic"
    # the dry run in a STOCKS_BASE with no _system/universe.csv
    base = tempfile.mkdtemp(prefix="fade_dry_")
    try:
        d = os.path.join(base, "TST")
        os.makedirs(d)
        json.dump({"cik": 1, "currency": "USD", "profile": {"sic": "3561"}, "annual": _gm_rows(UPV, UPGM)},
                  open(os.path.join(d, "fundamentals.json"), "w", encoding="utf-8"))
        json.dump({"schema": 1, "ticker": "TST", "facts": TM.base_facts()}, open(os.path.join(d, "facts.json"), "w", encoding="utf-8"))
        json.dump({"moat_score": 6, "moat_justification": "t", "moat_scorecard": TM.base_scorecard()},
                  open(os.path.join(d, "judgment.json"), "w", encoding="utf-8"))
        json.dump({"ticker": "TST", "engine_release": "5.7.0", "latest_period_end": "2025-12-31", "cik": 1,
                   "scenarios": _scn(), "fragility_flags": []}, open(os.path.join(d, "dcf_numbers.json"), "w", encoding="utf-8"))
        env = dict(os.environ, STOCKS_BASE=base, PYTHONIOENCODING="utf-8")
        r = subprocess.run([sys.executable, os.path.join(SYS, "moat_scorecard.py"), "TST"], capture_output=True, text=True,
                           encoding="utf-8", env=env, timeout=120)
        assert r.returncode == 0, r.stdout + r.stderr
        assert "fade: widening (widening_confirmed) -> pass --moat-trend widening (growth hold 3 years)" in r.stdout, r.stdout
    finally:
        shutil.rmtree(base, ignore_errors=True)


def test_fade_leaves():
    """10 §1.4: numeric_leaves keeps 03b's set (every moat_evidence number outside `fade`); fade_trace_leaves carries
    the trend block's figures (as numbers and as fractions, so '-8.50pp' matches), the thresholds, the holds and the
    counterfactual, plus the record's hold-moved paths; fade_extra_leaves drops the trend block from the anchors."""
    ev = _case_fade(_gm_rows(DNV, DNGM), sync=False)
    f = ev["fade"]
    leaves = M.numeric_leaves(ev)
    assert -8.5 in leaves and f["governing_first2"] in leaves, "erosion_test stays in 03b's set"
    no_fade = {k: v for k, v in ev.items() if k != "fade"}
    assert sorted(M.numeric_leaves(ev)) == sorted(M.numeric_leaves(no_fade, exclude=()))
    tr = M.fade_trace_leaves(ev)
    for v in (-8.5, -0.085, -4.0, -0.04, f["governing_first2"], f["governing_last2"], 0.03, 0.2, 0.02, 0, 2, 3):
        assert v in tr["values"], v
    assert "implied_irr_weighted" in tr["paths"] and "scenarios.base.irr" in tr["paths"] and "hold_years" in tr["paths"]
    assert "inputs.hold_years" in tr["paths"] and "weighted" in tr["paths"] and "iprd_adjustment.before" in tr["paths"]
    ex = M.fade_extra_leaves(ev)
    assert -8.5 not in ex and f["governing_first2"] not in ex and ev["core_evidence_score"] in ex


def test_widening_declined_shape():
    """10 §6.2: widening_declined is a non-empty string or null on any release (it is no influence field: declining
    only lowers the value)."""
    for bad in ("", "   ", 3, ["x"], True):
        sc = TM.base_scorecard()
        sc["widening_declined"] = bad
        try:
            _case_fade(_gm_rows(UPV, UPGM), sc=sc, is_57=False)
            raise AssertionError(f"widening_declined {bad!r} was accepted")
        except M.MoatRefusal as e:
            assert str(e).startswith("moat_scorecard.widening_declined must be a non-empty string"), str(e)
    sc = TM.base_scorecard()
    sc["widening_declined"] = None
    assert _case_fade(_gm_rows(UPV, UPGM), sc=sc)["fade"]["decline_declared"] is False
    assert "widening_declined" in M.SCORECARD_KEYS


def _rec(trend=None, hold=None, holds=None):
    n = {"inputs": {"moat": 6, "offsets": [-0.12, -0.05, 0, 0.05, 0.12], "g_terminal": GT}, "g_base": 0.08,
         "scenarios": {k: {"prob": 0.2} for k in LABELS}}
    if trend is not None:
        n["inputs"]["moat_trend"] = trend
        n["moat_trend"] = trend
    if hold is not None:
        n["inputs"]["hold_years"] = hold
    for k, h in zip(LABELS, holds or ()):
        n["scenarios"][k]["hold_years"] = h
    return n


def test_fade_sync_record_consistency():
    """10 §5.2: fade_sync — in sync when the engine recorded the trend and hold the trend test gives (absent = stable
    / 2); the mismatch texts; a record inconsistent with itself (eroding with hold 2, a per-scenario hold that is
    neither the run's nor 2) is malformed and refused everywhere."""
    want0 = {"trend": "eroding", "hold_years": 0, "rule": "eroding_not_rebutted", "status": "measured", "measure": "roic",
             "years": ["2021", "2022", "2023", "2024", "2025"], "governing_change_pp": -6.4, "margin_basis": "gross",
             "margin_change_pp": -3.1}
    assert M.fade_sync(want0, _rec("eroding", 0, [2, 0, 0, 0, 0]))[0] is True
    ok, detail, bad = M.fade_sync(want0, _rec())
    assert not ok and not bad and detail == (
        "moat fade: make_score's trend test says eroding (governing roic -6.40pp FY2021-22 -> FY2024-25, gross margin "
        "-3.10pp; no erosion_rebuttal) -> --moat-trend eroding (growth hold 0 years), but the engine ran --moat-trend "
        "stable (hold 2) — rerun the final pass with --moat-trend eroding, or declare moat_scorecard.erosion_rebuttal "
        "carrying a traced number"), detail
    stable = {"trend": "stable", "hold_years": 2, "rule": "no_trend", "status": "measured", "measure": "roic",
              "years": ["2021", "2022", "2023", "2024", "2025"], "governing_change_pp": -2.1, "margin_basis": "gross",
              "margin_change_pp": -1.4}
    assert M.fade_sync(stable, _rec())[0] is True and M.fade_sync(stable, _rec("stable", 2, [2] * 5))[0] is True
    ok, detail, bad = M.fade_sync(stable, _rec("widening", 3, [2, 3, 3, 3, 3]))
    assert not ok and not bad and "says stable (no trend: governing roic -2.10pp" in detail and \
        "but the engine ran --moat-trend widening (hold 3) — rerun the final pass with --moat-trend stable" in detail
    ok, detail, bad = M.fade_sync(stable, _rec("eroding", 2, [2] * 5))
    assert bad and detail == "dcf_numbers.json records moat_trend eroding with hold_years 2 — the engine pairs eroding with 0; rerun the engine"
    ok, detail, bad = M.fade_sync(want0, _rec("eroding", 0, [7, 0, 0, 0, 0]))
    assert bad and detail == ("dcf_numbers.json scenarios.super_bear.hold_years 7 is neither the run's hold 0 nor the "
                              "default 2 — rerun the engine"), detail
    ok, detail, bad = M.fade_sync(want0, _rec("falling", 0))
    assert bad and "moat_trend 'falling'" in detail


def test_rebuild_drift_switch():
    """T19b (lane default Q5): on a rebuild a fade mismatch caused by moved data is gate drift (recorded, never
    refused); FADE_DRIFT_ON_REBUILD = False refuses it on rebuilds too (M6's letter)."""
    c = TM.Case(rows=_gm_rows(DNV, DNGM), sic="3561", n_extra={"scenarios": _scn(), "moat_trend": "eroding",
                                                               "inputs": {"moat_trend": "eroding", "hold_years": 0},
                                                               "hold_years": 0})
    for k in LABELS:
        c.n["scenarios"][k]["hold_years"] = 0
    try:
        facts = {f["id"]: f for f in c.facts}
        first = M.evaluate(c.folder, c.n, c.j, facts=facts, is_57=True, sic=c.sic)
        assert first["fade"]["in_sync"] is True and first["fade"]["rule"] == "eroding_not_rebutted"
        prior = {"moat_evidence": first, "dcf_content_hash": c.n["content_hash"]}
        # the data moves: flat rows now (fundamentals.json refreshed), same engine run, same declaration and facts
        json.dump({"cik": 1, "currency": "USD", "annual": _gm_rows([0.20] * 5, [0.40] * 5)},
                  open(os.path.join(c.folder, "fundamentals.json"), "w", encoding="utf-8"))
        ev = M.evaluate(c.folder, c.n, c.j, facts=facts, is_57=True, sic=c.sic, prior=prior)
        f = ev["fade"]
        assert f["in_sync"] is False and f["rule"] == "no_trend" and f["trend"] == "stable"
        dr = [d for d in ev["gate_drift"] if d["gate"] == "fade_sync"]
        assert len(dr) == 1 and dr[0]["detail"].startswith("engine ran eroding (hold 0); the trend computed now is stable "
                                                           "(no_trend: governing roic +0.00pp"), dr
        assert "data moved since the engine run; the next engine run passes --moat-trend stable" in dr[0]["detail"]
        try:
            M.evaluate(c.folder, c.n, c.j, facts=facts, is_57=True, sic=c.sic)   # an authoring run refuses it
            raise AssertionError("authoring run accepted a stale trend")
        except M.MoatRefusal as e:
            assert "says stable" in str(e) and "engine ran --moat-trend eroding (hold 0)" in str(e)
        saved = M.FADE_DRIFT_ON_REBUILD
        M.FADE_DRIFT_ON_REBUILD = False
        try:
            M.evaluate(c.folder, c.n, c.j, facts=facts, is_57=True, sic=c.sic, prior=prior)
            raise AssertionError("FADE_DRIFT_ON_REBUILD = False still drifted")
        except M.MoatRefusal as e:
            assert "rerun the final pass with --moat-trend stable" in str(e)
        finally:
            M.FADE_DRIFT_ON_REBUILD = saved
    finally:
        c.close()


def test_unused_rebuttal_is_unchecked_on_a_rebuild():
    """T19c in-process, review 2026-10-21: a rebuttal unused when authored (flat data) that meets a measured erosion on
    a REBUILD restores no hold — fade_trend(rebuttal_checked=False): rule eroding_not_rebutted with rebuttal_declared
    (rebuttal_unchecked), the fade_sync drift text says why; an identical rerun stays so; a prior that ran the rebuttal
    as the hold-restoring field (rule eroding_rebutted) keeps it; an authoring run (no prior) and the dry run give
    eroding_rebutted (make_score then checks it); FADE_DRIFT_ON_REBUILD = False refuses with the unchecked text."""
    sc = TM.base_scorecard()
    sc["erosion_rebuttal"] = "n/a"
    c = TM.Case(rows=_gm_rows([0.20] * 5, [0.40] * 5), sic="3561", sc=sc,
                n_extra={"scenarios": _scn(), "moat_trend": "stable", "hold_years": 2,
                         "inputs": {"moat_trend": "stable", "hold_years": 2}})
    for k in LABELS:
        c.n["scenarios"][k]["hold_years"] = 2
    try:
        facts = {f["id"]: f for f in c.facts}
        ev0 = lambda prior=None, **kw: M.evaluate(c.folder, c.n, c.j, facts=facts, is_57=True, sic=c.sic,  # noqa: E731
                                                  prior=prior, **kw)
        first = ev0()
        assert first["fade"]["rule"] == "no_trend" and first["fade"]["rebuttal_unused"] is True
        prior = {"moat_evidence": first, "dcf_content_hash": c.n["content_hash"]}
        json.dump({"cik": 1, "currency": "USD", "annual": _gm_rows(DNV, DNGM)},
                  open(os.path.join(c.folder, "fundamentals.json"), "w", encoding="utf-8"))
        ev = ev0(prior)
        f = ev["fade"]
        assert (f["rule"], f["trend"], f["hold_years"], f["in_sync"]) == ("eroding_not_rebutted", "eroding", 0, False), f
        assert f["rebuttal_declared"] and not f["rebuttal_unused"] and M.rebuttal_unchecked(f)
        assert {k: v for k, v in f.items() if k not in ("rule", "trend", "hold_years", "in_sync", "counterfactual")} == {
            k: v for k, v in ev0(prior=None, sync=False)["fade"].items()
            if k not in ("rule", "trend", "hold_years", "in_sync", "counterfactual")}, "only the rule and hold differ"
        dr = [d for d in ev["gate_drift"] if d["gate"] == "fade_sync"]
        assert len(dr) == 1 and dr[0]["detail"] == (
            "engine ran stable (hold 2); the trend computed now is eroding (eroding_not_rebutted: governing roic -8.50pp "
            "FY2021-22 -> FY2024-25, gross margin -4.00pp) — data moved since the engine run; the erosion_rebuttal, "
            "declared while no erosion was measured, has never been checked (a rebuild skips the influence checks), so "
            "it restores no hold here — the next authoring run checks it (a traced number anchored outside the trend "
            "test keeps --moat-trend stable) or passes --moat-trend eroding"), dr
        assert any(x.startswith(f"- Fade direction: {M.UNCHECKED_TEXT} -> growth hold 0 yrs") for x in M.fade_lines(f))
        assert ev0({"moat_evidence": ev, "dcf_content_hash": c.n["content_hash"]}) == ev, "an identical rerun differs"
        checked = dict(first, fade=dict(first["fade"], rule="eroding_rebutted"))
        kept = ev0({"moat_evidence": checked, "dcf_content_hash": c.n["content_hash"]})["fade"]
        assert (kept["rule"], kept["in_sync"]) == ("eroding_rebutted", True) and not M.rebuttal_unchecked(kept)
        assert ev0()["fade"]["rule"] == "eroding_rebutted"
        assert ev0(prior, dry_run=True)["fade"]["rule"] == "eroding_rebutted"
        saved = M.FADE_DRIFT_ON_REBUILD
        M.FADE_DRIFT_ON_REBUILD = False
        try:
            ev0(prior)
            raise AssertionError("FADE_DRIFT_ON_REBUILD = False still drifted")
        except M.MoatRefusal as e:
            assert str(e) == (
                "moat fade: make_score's trend test says eroding (governing roic -8.50pp FY2021-22 -> FY2024-25, gross "
                "margin -4.00pp; the erosion_rebuttal was declared while no erosion was measured and no run has checked "
                "it) -> --moat-trend eroding (growth hold 0 years), but the engine ran --moat-trend stable (hold 2) — "
                "rerun the final pass: an authoring run checks moat_scorecard.erosion_rebuttal (a traced number anchored "
                "outside the trend test), or remove it and run --moat-trend eroding"), str(e)
        finally:
            M.FADE_DRIFT_ON_REBUILD = saved
    finally:
        c.close()


def test_hold_moved_values_and_trace_leaves_of_records():
    """Review 2026-10-21: hold_moved_values reads the derived price / IV@15 figures and the numbers inside the
    hold-moved flags (TIER_BAND, WIDE_SCENARIO_SPREAD, HIGH_TV_SHARE) and nothing else; fade_trace_leaves(ev, n,
    saved) adds the record's figures at FADE_TRACE_PATHS (not the per-year FADE_SERIES_PATHS, never an engine source)
    and a saved run's wherever they differ from the record's; fade_extra_leaves drops a moat-evidence number equal to
    any of them."""
    n = {"price": 20.0, "iv_at_15": 25.0, "implied_irr_weighted": 0.1712, "scenarios": {"bear": {"irr": 0.1234}},
         "growth_paths": {"base": [0.0661, 0.0662]}, "base_oe_per_share": 3.0,
         "fragility_flags": ["TIER_BAND: bear-case tier C (12.3%) vs bull-case tier A (27.1%) — the verdict spans tiers",
                             "WIDE_SCENARIO_SPREAD: super-bull IV is 6.1x super-bear IV — uncertainty is huge",
                             "HIGH_TV_SHARE: terminal value is 82% of IV@15% — result is mostly a terminal assumption",
                             "LOW_OE_YIELD: base OE yield 1.9% — valuation rests almost entirely on growth"]}
    hm = M.hold_moved_values(n)
    for v in (0.8, -0.2, 0.123, 0.271, 6.1, 0.82):
        assert any(abs(v - w) < 1e-9 for w in hm), (v, hm)
    assert not any(abs(w - 0.019) < 1e-9 or abs(w - 0.15) < 1e-9 for w in hm), hm
    vals = M.fade_trace_leaves({}, n=n)["values"]
    assert 0.1712 in vals and 0.1234 in vals and 0.0661 not in vals and 0.82 in vals
    s0 = dict(n, implied_irr_weighted=0.1555, growth_paths={"base": [0.0612, 0.0571]}, iv_at_15=23.0)
    vals = M.fade_trace_leaves({}, n=n, saved=[s0, n])["values"]
    assert 0.1555 in vals and 0.0612 not in vals and 0.0571 not in vals and 0.0661 not in vals
    assert any(abs(w - (20.0 / 23.0 - 1)) < 1e-12 for w in vals)
    me = {"core_evidence_score": 0.1712, "supporting_adjustment": 0.5}
    assert M.fade_extra_leaves(me, M.fade_trace_leaves({}, n=n)["values"]) == [0.5]


def test_operating_margin_fallback_moves_the_trend():
    """10b COVERAGE (lane default Q4): with no gross-margin line the margin leg is the filed operating margin (same
    thresholds, margin_basis operating), so an operating-margin decline erodes; a filer with neither stays unmeasured;
    a CSV-only folder is never measured."""
    rows = [TM.row(y, v, gross_margin=None, operating_income=1000.0 * v, revenue=r)
            for y, v, r in zip(YEARS, DNV, (2000.0, 2050.0, 2100.0, 2200.0, 2300.0))]
    f = _case_fade(rows)["fade"]
    assert f["margin_basis"] == "operating" and f["direction"] == "eroding" and f["hold_years"] == 0, f
    kn = "\n".join(M.fade_lines(f))
    assert "· operating margin " in kn and "-> eroding (MOAT_EROSION)" in kn, kn
    # no gross margin and no operating-income line (ROIC on the pretax rung): the governing return is measured, the
    # margin leg is not — the pretax EBIT fallback is never trended
    rows = [TM.row(y, v, gross_margin=None, operating_income=None, pretax_income=1000.0 * v) for y, v in zip(YEARS, DNV)]
    f = _case_fade(rows)["fade"]
    assert f["status"] == "not_measured" and f["reason"] == "no_margin", (f["status"], f["reason"])


def test_fade_key_numbers_lines():
    """10 §5.7: the Trend test line replaces 03b's Erosion test line, the Fade direction line follows; every number
    generated, no worker text."""
    ev = _case_fade(_gm_rows(DNV, DNGM), n_extra={"inputs": {"moat_trend": "eroding", "hold_years": 0}}, sync=True,
                    mut=lambda c: [c.n["scenarios"][k].__setitem__("hold_years", 0) for k in LABELS])
    L = M.key_numbers_lines(ev)
    t = [x for x in L if x.startswith("- Trend test")]
    assert t == ["- Trend test (last 5 FY, governing roic): FY2021-22 avg 29.50% -> FY2024-25 avg 21.00% (-8.50pp, slope "
                 f"{ev['fade']['slope_governing']:+.4f}/yr) · gross margin -4.00pp (slope {ev['fade']['slope_margin']:+.4f}/yr) "
                 "-> eroding (MOAT_EROSION)"], t
    fd = [x for x in L if x.startswith("- Fade direction")]
    assert fd[0].startswith("- Fade direction: eroding, erosion_rebuttal not declared -> growth hold 0 yrs · engine ran "
                            "--moat-trend eroding (hold 0): in sync"), fd
    assert not any(x.startswith("- Erosion test") for x in L)
    sc = TM.base_scorecard()
    sc["erosion_rebuttal"] = "SECRET worker text 4.5% [F3]"
    ev = _case_fade(_gm_rows(DNV, DNGM), sc=sc)
    assert "SECRET" not in "\n".join(M.key_numbers_lines(ev))
    legacy = _case_fade(_gm_rows(UPV, UPGM), sc=None, is_57=False)
    fd = [x for x in M.key_numbers_lines(legacy) if x.startswith("- Fade direction")]
    assert fd[0].startswith("- Fade direction (report only, pre-5.7 record): widening -> a 5.7 run holds 3 yrs only with "
                            "a fact-backed source"), fd


# ===========================================================================
# reprice: a 5.7 hold-0 record reprices on its own holds
# ===========================================================================
def test_reprice_hold_zero_record():
    """T23 (A13): APP's record turned 5.7 hold 0 (scenarios recomputed with the engine at hold 0, stored paths stripped,
    content_hash re-stamped) reprices at the scored price to the scored weighted and scenario IRRs bit for bit
    (reprice, scored=None); reprice_folder with a score.json make_score would write for it (dcf_content_hash and the
    headline figures) writes live figures on the hold-0 flows."""
    import reprice as R
    import test_reprice as TR
    m = hold_record(app_record(), "eroding", strip_paths=True)
    live = R.reprice(m, m["price"])
    assert live["irr_weighted"] == m["implied_irr_weighted"], (live["irr_weighted"], m["implied_irr_weighted"])
    for k in LABELS:
        assert live["scenarios"][k]["irr"] == m["scenarios"][k]["irr"], k
    tmp = tempfile.mkdtemp(prefix="fade_reprice_")
    old = R.BASE
    try:
        R.BASE = tmp
        d = os.path.join(tmp, "APP")
        os.makedirs(d)
        score = {"ticker": "APP", "dcf_content_hash": m["content_hash"], "implied_irr": round(m["implied_irr_weighted"], 4),
                 "iv_at_15": round(m["iv_at_15"], 2), "analysis_date": m["as_of"], "tier_by_numbers": m["tier_by_numbers"],
                 "tier_final": m["tier_by_numbers"], "base_oe_per_share": m["base_oe_per_share"], "price": m["price"],
                 "engine_release": m["engine_release"], "engine_version": m.get("engine_version")}
        for name, obj in (("dcf_numbers.json", m), ("score.json", score), ("prices.json", TR._prices())):
            with open(os.path.join(d, name), "w", encoding="utf-8") as f:
                json.dump(obj, f)
        live = R.reprice_folder("APP")
        paths, _ = E.replay_paths(m)
        exp = E.adjusted_irr(paths["weighted"], live["price"], GT, 0.0)[0]
        assert live["irr_weighted"] == exp and live["score_json_fresh"] is True, (live["irr_weighted"], exp)
    finally:
        R.BASE = old
        shutil.rmtree(tmp, ignore_errors=True)


def test_reprice_reads_the_record_not_the_rule():
    """T23b: the T6b record (a per-scenario hold today's fade_hold would not give: a below-terminal super_bear at hold
    0, written by a 'literal' engine) reprices to its scored IRRs bit for bit."""
    import reprice as R
    m = hold_record(app_record(), "eroding", rule="literal", offsets=[-0.40, -0.13, -0.05, 0.03, 0.10], strip_paths=True)
    assert m["scenarios"]["super_bear"]["g_start"] <= GT and m["scenarios"]["super_bear"]["hold_years"] == 0
    live = R.reprice(m, m["price"])
    assert live["irr_weighted"] == m["implied_irr_weighted"]
    assert live["scenarios"]["super_bear"]["irr"] == m["scenarios"]["super_bear"]["irr"]


if __name__ == "__main__":
    fails = 0
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"PASS {name}")
            except Exception as e:  # noqa: BLE001
                fails += 1
                import traceback
                traceback.print_exc()
                print(f"FAIL {name}: {type(e).__name__}: {e}")
    sys.exit(1 if fails else 0)
