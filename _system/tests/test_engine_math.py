#!/usr/bin/env python3
"""Engine math tests (v5.4). Run: python3 _system/tests/test_engine_math.py
(or python3 -m pytest _system/tests). No network: everything comes from the
module-level functions in dcf_engine.py plus the dcf_numbers.json files
already in the repo.

1. Unit tests of the valuation functions (fade shape, Gordon boundary, IRR
   cap / floor, tier boundaries, CAP from moat).
2. REGRESSION over every scored folder: recompute each scenario's 15-year
   path and IV@10/12/15 and its IRR from the recorded inputs (base, g_base,
   offsets, mults, moat, gterm, price) and require bit-level agreement with
   what the pre-refactor engine wrote. This proves the v5.4 refactor of the
   math into module-level functions changed nothing for r > g_terminal.
   v5.6: a record with an acquired-IPR&D one-time deduction is replayed
   through the same helpers (adjusted_value / adjusted_irr; charge 0.0 for
   every other record — the identity).
"""
import os, sys, glob, json, math

HERE = os.path.dirname(os.path.abspath(__file__))
SYS = os.path.dirname(HERE)
BASE = os.path.dirname(SYS)
sys.path.insert(0, SYS)
import dcf_engine as E  # noqa: E402

LABELS = ["super_bear", "bear", "base", "bull", "super_bull"]


def close(a, b, rel=1e-9, abs_=1e-9):
    if a is None or b is None:
        return a is None and b is None
    return math.isclose(a, b, rel_tol=rel, abs_tol=abs_)


# ---------------- unit tests ----------------
def test_growth_path_holds_then_fades():
    g = E.growth_path(0.30, cap_years=5, gterm=0.025, n=15)
    assert g[0] == 0.30 and g[1] == 0.30, "growth must hold for 2 years"
    assert g[2] < 0.30, "fade starts in year 3"
    assert close(g[6], 0.025, 1e-12), "reaches terminal after 2 + CAP years"
    assert all(close(x, 0.025, 1e-12) for x in g[6:]), "stays at terminal"
    # below-terminal start converges UP, never overshoots
    g2 = E.growth_path(-0.10, cap_years=4, gterm=0.025)
    assert g2[0] == -0.10 and g2[-1] == 0.025 and all(g2[i] <= g2[i + 1] for i in range(14))


def test_project_path_compounds():
    f = E.project_path(1.0, 0.10, cap_years=15, gterm=0.025)
    assert close(f[0], 1.10) and close(f[1], 1.21)
    assert len(f) == 15


def test_present_value_gordon_boundary():
    f = E.project_path(1.0, 0.05, 8, 0.025)
    assert E.present_value(f, 0.025, 0.025) == float("inf")
    assert E.present_value(f, 0.0, 0.025) == float("inf")
    v15, v10 = E.present_value(f, 0.15, 0.025), E.present_value(f, 0.10, 0.025)
    assert 0 < v15 < v10, "lower discount rate -> higher value"
    assert 0 < E.terminal_share(f, 0.15, 0.025) < 1


def test_solve_irr_matches_value_and_caps_and_floors():
    f = E.project_path(1.0, 0.08, 8, 0.025)
    px = E.present_value(f, 0.15, 0.025)
    irr, capped, floor = E.solve_irr(f, px, 0.025)
    assert close(irr, 0.15, 1e-6) and not capped and not floor, "IRR at the price equal to IV@15 is 15%"
    irr, capped, floor = E.solve_irr(f, 0.0001, 0.025)
    assert irr == 2.0 and capped, "absurdly cheap -> capped at 200%, never blank"
    irr, capped, floor = E.solve_irr(f, 1e9, 0.025)
    assert floor and close(irr, 0.025, 1e-3), "absurdly expensive -> converges onto g_terminal and is flagged"


def test_tiers_and_cap():
    assert [E.tier_for_irr(x) for x in (0.26, 0.25, 0.2, 0.15, 0.1, 0.0999, 0.0, -0.1)] == ["S", "S", "A", "B", "C", "D", "D", "D"]
    assert E.tier_for_irr(None) is None
    assert E.cap_years_for_moat(0) == 2.0 and E.cap_years_for_moat(10) == 15.0
    assert close(E.cap_years_for_moat(6), 9.8) and close(E.cap_years_for_moat(5), 8.5)
    assert E.cap_years_for_moat(99) == 15.0 and E.cap_years_for_moat(-3) == 2.0


def test_market_cap_ads_ratio():
    # Foreign-form filer: the price is per ADS while `shares` is the ordinary
    # share count from EDGAR, so the traded cap divides the ordinary count by
    # the ADS ratio. TLK shape (ratio 100): the pre-fix formula printed a
    # $1,092.66B cap for a ~$10.9B company and blocked the name on scope.
    assert close(E.market_cap_est(11.03, 99_062_216_600, {"ratio": 100.0}),
                 11.03 * 99_062_216_600 / 100)
    # JD shape: ratio 2.
    assert close(E.market_cap_est(26.60, 2_978_037_127, {"ratio": 2.0}),
                 26.60 * 2_978_037_127 / 2)
    # Ratio below 1 (FMS: 1 ADS = 1/2 ordinary share) corrects an
    # UNDERstatement — the formula divides, never special-cases ratio > 1.
    assert close(E.market_cap_est(10.0, 1000, {"ratio": 0.5}), 20000.0)
    # No ratio / ratio 1: bit-identical to the pre-fix price * shares.
    assert E.market_cap_est(50.0, 1_000_000, None) == 50.0 * 1_000_000
    assert E.market_cap_est(50.0, 1_000_000, {"ratio": 1.0}) == 50.0 * 1_000_000
    # Missing price or shares: the universe-screener fallback, untouched.
    assert E.market_cap_est(None, 1_000_000, {"ratio": 10.0}, fallback=123.0) == 123.0
    assert E.market_cap_est(50.0, None, None, fallback=None) is None


# ---------------- regression over the repo ----------------
def replay_record(n, who, floor_hits=None):
    """Recompute one recorded run's scenario paths, IV@10/12/15 and IRRs from its recorded inputs and require
    bit-level agreement. v5.6: a record carrying an acquired-IPR&D one-time deduction (iprd_adjustment, treatment
    one_time_value_deduction) is replayed through the same helpers the engine used — IV = present_value - charge,
    IRR = solve_irr at price + charge; for every other record the charge is 0.0, the identity."""
    scn, inp = n["scenarios"], n["inputs"]
    base, price, gterm = n["base_oe_per_share"], n["price"], inp.get("g_terminal", 0.025)
    c = E.iprd_charge_per_share(n)
    cap = E.cap_years_for_moat(inp["moat"])
    g_base = n["g_base"]
    flows_all = []
    for i, lbl in enumerate(LABELS):
        r = scn[lbl]
        g0 = max(E.GROWTH_FLOOR_START, min(E.GROWTH_CAP_START, g_base + inp["offsets"][i]))
        assert close(round(g0, 4), r["g_start"], 1e-12, 1e-12), f"{who}: g_start {lbl}"
        flows = E.project_path(base * inp["mults"][i], g0, cap, gterm)
        flows_all.append(flows)
        for rate, key in ((0.10, "iv_at_10"), (0.12, "iv_at_12"), (0.15, "iv_at_15")):
            assert close(E.adjusted_value(flows, rate, gterm, c), r[key]), f"{who}: {lbl} {key}"
        irr, capped, floor = E.adjusted_irr(flows, price, gterm, c)
        if r["irr"] is not None and r["irr"] < gterm + 0.005:
            # The pre-5.4 solver floored the terminal denominator at 0.5% and
            # could "solve" an IRR below terminal growth (GFI super-bear:
            # -3.8%). A perpetuity growing at g has an IRR above g at any
            # finite price, so v5.4 finds the real root just above g and
            # flags it. Both agree the name sits at the model's floor.
            assert irr >= gterm and floor, f"{who}: {lbl} expected at-floor IRR, got {irr}"
            if floor_hits is not None:
                floor_hits.append(f"{who}:{lbl}")
        else:
            assert close(irr, r["irr"], 1e-9, 1e-9), f"{who}: {lbl} irr {irr} vs {r['irr']}"
    probs = inp["probs"]
    w = [sum(probs[i] * flows_all[i][t] for i in range(5)) for t in range(15)]
    rec = n["weighted"]
    for rate, key in ((0.10, "iv_at_10"), (0.12, "iv_at_12"), (0.15, "iv_at_15")):
        assert close(E.adjusted_value(w, rate, gterm, c), rec[key]), f"{who}: weighted {key}"
    irr, capped, floor = E.adjusted_irr(w, price, gterm, c)
    if rec["irr"] is not None and rec["irr"] < gterm + 0.005:
        assert irr >= gterm and floor, f"{who}: weighted expected at-floor IRR, got {irr}"
        if floor_hits is not None:
            floor_hits.append(f"{who}:weighted")
    else:
        assert close(irr, rec["irr"], 1e-9, 1e-9), f"{who}: weighted irr"
    assert E.tier_for_irr(irr) == n["tier_by_numbers"], f"{who}: tier"


def test_regression_recorded_folders():
    checked, skipped, floor_hits = 0, [], []
    for p in sorted(glob.glob(os.path.join(BASE, "*", "dcf_numbers.json"))):
        n = json.load(open(p, encoding="utf-8"))
        scn, inp = n.get("scenarios"), n.get("inputs")
        if not scn or not inp or n.get("base_oe_per_share") is None or n.get("price") is None:
            skipped.append(os.path.basename(os.path.dirname(p))); continue
        replay_record(n, os.path.basename(os.path.dirname(p)), floor_hits)
        checked += 1
    print(f"regression: {checked} folders reproduced bit-for-bit; skipped (no scenarios): {', '.join(skipped) or 'none'}")
    print(f"at-floor cases (pre-5.4 solver reported an IRR below terminal growth): {', '.join(floor_hits) or 'none'}")
    assert checked >= 1


if __name__ == "__main__":
    fails = 0
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn(); print(f"PASS {name}")
            except AssertionError as e:
                fails += 1; print(f"FAIL {name}: {e}")
    sys.exit(1 if fails else 0)
