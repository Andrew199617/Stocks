#!/usr/bin/env python3
"""Engine release 5.6 — acquired IPR&D one-time value adjustment (Andrew, 2026-10-19).
Run: python _system/tests/test_engine_iprd.py (or python -m pytest _system/tests). No network.

The decision: OE = OCF - capex - SBC never sees in-process R&D bought in an asset acquisition (ASC 805 expenses it,
the cash-flow statement adds it back in OCF, the payment sits outside every capex tag). The charge is entered ONCE
as a year-0 outflow in every scenario path — IV_adj(r) = IV(r) - charge/share, IRR solved at price + charge/share
— and NEVER deducted from the base. Tiers, the band, hurdle prices and upside follow the adjusted figures.

Every end-to-end case drives dcf_engine.main() offline through engine55_harness (the 5.5 fixture style):
  * a synthetic filer (test_engine_55's _syn_facts: 100M shares, OCF 200M growing 5%/yr, capex 50M, SBC 10M)
    with the IPR&D facts added per case, run both ways (with / without them) so "base bit-identical" and
    "IV lower by exactly charge/shares" are compared on the same run;
  * HALO built from its real companyfacts (fixtures/engine55/HALO.json.gz, trimmed by build_fixtures.py), at its
    scored price and inputs, against the recorded 5.4.0 run's figures frozen below;
  * APP's recorded run (not re-scored) for bit-for-bit identity of a filer with no IPR&D facts.
Then the two other consumers that re-solve values from replayed paths — reprice.reprice (live IRR / IVs, also
across a split since scoring) and build_site's forecast sensitivity / hurdle prices / at-floor flag — must agree
with the engine on an adjusted record, and test_engine_math's replay must reproduce an adjusted record.

Each test names what it covers; all of them fail on the 5.5.0 engine (no detection, no helpers, release 5.5.0).

Fixer review round (2026-10-19, [ADDITION — awaiting Andrew's ratification]): an EXPENSE-basis period (no us-gaap
investing cash tag) is deducted only when judgment.json iprd_cash_flow_check says the 10-K's cash-flow statement
added the charge back in operating activities and paid it in investing (HALO); NBIX pays its upfronts inside
operating cash flow, which OE already carries. The synthetic runs below declare that check for every expense fact
they file (`checks=True`, the HALO shape) unless a test is about the check itself (`checks=False`).
"""
import copy
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SYS = os.path.dirname(HERE)
ROOT = os.path.dirname(SYS)
for _p in (HERE, SYS):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import engine55_harness as H  # noqa: E402
from test_engine_55 import (_syn_facts, _syn_put, _syn_fixture, _ctx, _o, run, args_for, flags, recorded_matching_fixture,  # noqa: E402
                            assert_same_math, APP_J, LABELS)

E = H._engine()

EXPENSE = "ResearchAndDevelopmentAssetAcquiredOtherThanThroughBusinessCombinationWrittenOff"
EXPENSE_OLD = "ResearchAndDevelopmentInProcess"
CASH = "PaymentsToAcquireInProcessResearchAndDevelopment"
IMPAIR = "ImpairmentOfIntangibleAssetsExcludingGoodwill"
INTANG = "PaymentsToAcquireIntangibleAssets"
RATES = (("iv_at_10", 0.10), ("iv_at_12", 0.12), ("iv_at_15", 0.15), ("iv_at_20", 0.20), ("iv_at_25", 0.25))
IV_KEYS = [k for k, _ in RATES]
SHARES = 100e6

# HALO's recorded run (engine 5.4.0, as of 2026-10-18; the 5.5.0 engine reproduces it bit for bit — main agent,
# 2026-10-19), frozen here because the HALO re-score rewrites the folder.
HALO_ARGS = ["--price", "121.84", "--moat", "7", "--probs", "0.1,0.3,0.3,0.2,0.1",
             "--offsets", "-0.12,-0.05,0,0.05,0.12", "--mults", "0.75,0.9,1.0,1.1,1.25", "--ttm"]
HALO_TTM = {"ticker": "HALO", "cik": 1159036, "fy_end": "2025-12-31", "ytd_end": "2026-06-30",
            "inputs": {"ocf": {"fy_period": ["2025-01-01", "2025-12-31"], "ytd_prior_period": ["2025-01-01", "2025-06-30"],
                               "ytd_current_period": ["2026-01-01", "2026-06-30"]}},
            "ttm_ocf": 818595000, "ttm_capex": 12371000, "ttm_sbc": 63066000, "ttm_shares_diluted": 122092000,
            "ttm_oe_total": 743158000, "ttm_oe_per_share": 6.08686891852046, "warnings": [], "overrides_used": []}
HALO_CHARGE = 284887000
# the worker's reading of HALO's FY2025 cash-flow statement (main agent, 2026-10-19: R7.htm of the 10-K)
HALO_J = {"iprd_cash_flow_check": [
    {"period": "2025-12-31", "window": "fy", "amount": HALO_CHARGE, "presentation": "added_back_paid_in_investing",
     "source": "HALO 10-K FY2025 (0001159036-26-000024) cash-flow statement R7.htm: operating activities add back "
               "'Acquired in-process research and development expense 284,887' (thousands); investing activities "
               "'Acquisition of in-process research and development, net of cash acquired (287,771)'"}]}
HALO_BASE = 6.08686891852046
HALO_REC = {
    "weighted": {"iv_at_10": 483.1596992327195, "iv_at_12": 354.5646640597138, "iv_at_15": 243.60641788525,
                 "iv_at_20": 150.1674226190775, "iv_at_25": 103.08955071427161, "irr": 0.22640823015094447},
    "super_bear": {"iv_at_10": 185.50551234270762, "iv_at_12": 139.3563600095508, "iv_at_15": 99.01304980531447,
                   "iv_at_20": 64.2629974328839, "iv_at_25": 46.19151193505563, "irr": 0.1309248480332118},
    "bear": {"iv_at_10": 319.22856636958636, "iv_at_12": 236.80560491188547, "iv_at_15": 165.2529249360693,
             "iv_at_20": 104.35927247631713, "iv_at_25": 73.22088609391074, "irr": 0.1814854213221807},
    "base": {"iv_at_10": 456.73164104907147, "iv_at_12": 336.1365407222625, "iv_at_15": 231.90060505501805,
             "iv_at_20": 143.86094369568926, "iv_at_25": 99.31939051552104, "irr": 0.22104208507515855},
    "bull": {"iv_at_10": 644.2666811279912, "iv_at_12": 470.79787631995447, "iv_at_15": 321.44601996167165,
             "iv_at_20": 196.1583444321635, "iv_at_25": 133.38395644371536, "irr": 0.2634172914607432},
    "super_bull": {"iv_at_10": 1029.677495472532, "iv_at_12": 745.8680910452342, "iv_at_15": 502.69849915058046,
                   "iv_at_20": 300.43389137754514, "iv_at_25": 200.3152524919344, "irr": 0.32799250776641076}}
# the brief's figures from the engine's own math (replay_paths + present_value + solve_irr), 4 dp
HALO_IRR_AFTER = {"weighted": 0.2239, "super_bear": 0.1293, "bear": 0.1793, "base": 0.2185, "bull": 0.2605,
                  "super_bull": 0.3246}

_CACHE = {}


def _cached(key, fn):
    if key not in _CACHE:
        _CACHE[key] = fn()
    return _CACHE[key]


# ---------------------------------------------------------------------------
# Synthetic filers
# ---------------------------------------------------------------------------
def _fy(facts, tag, year, value, filed=None, form="10-K"):
    _syn_put(facts, tag, "USD", _ctx(f"{year}-01-01", f"{year}-12-31", value, form=form, filed=filed or f"{year + 1}-02-20"))


def _ytd(facts, tag, start, end, value, filed, form="10-Q", fp="Q2"):
    _syn_put(facts, tag, "USD", {"start": start, "end": end, "val": value, "form": form, "fp": fp,
                                 "fy": int(end[:4]), "filed": filed, "accn": f"0000999001-{filed}"})


def _facts(expense=None, cash=None, old_expense=None, impairment=None, intangibles=None, capex=None):
    """_syn_facts plus {year: value} maps for the IPR&D expense tag, its pre-2022 name, the cash tag and the
    intangible-impairment tag (intangibles / capex: test_engine_55's own knobs — capex {year: None} = not filed)."""
    facts = _syn_facts(intangibles=intangibles, capex=capex)
    for tag, vals in ((EXPENSE, expense), (EXPENSE_OLD, old_expense), (CASH, cash), (IMPAIR, impairment)):
        for y, v in (vals or {}).items():
            _fy(facts, tag, y, v)
    return facts


def auto_checks(facts):
    """judgment.json iprd_cash_flow_check entries declaring every acquired-IPR&D expense fact in `facts` added back in
    operating activities and paid in investing (the HALO presentation): FY 10-K facts in window "fy", 10-Q
    year-to-date facts in window "ttm_current_ytd" (the latest filing per period; the current tag first)."""
    out = {}
    for tag in (EXPENSE, EXPENSE_OLD):
        for e in sorted(((facts["facts"].get("us-gaap", {}).get(tag) or {}).get("units", {}).get("USD") or []),
                        key=lambda x: x.get("filed", "")):
            if not e.get("val") or e["val"] <= 0:
                continue
            win = "fy" if e.get("form") == "10-K" else "ttm_current_ytd"
            key = (e["end"], win)
            if key in out and out[key]["tag"] != tag:
                continue
            out[key] = {"tag": tag, "period": e["end"], "window": win, "amount": e["val"],
                        "presentation": "added_back_paid_in_investing",
                        "source": f"test: the 10-K / 10-Q cash-flow statement adds the {e['end']} charge back in "
                                  "operating activities and pays it in investing"}
    return [{k: v for k, v in x.items() if k != "tag"} for x in out.values()]


def with_checks(facts, judgment, checks=True):
    j = dict(judgment or {})
    if checks and "iprd_cash_flow_check" not in j:
        c = auto_checks(facts)
        if c:
            j["iprd_cash_flow_check"] = c
    return j


def _run(facts, price=30.0, extra=(), judgment=None, ttm=None, checks=True):
    return run("SYN", args_for(5, extra=list(extra)), judgment=with_checks(facts, judgment, checks), ttm=ttm,
               fixture=_syn_fixture(facts, price))


def _ok(out):
    assert out["exit"] == 0, out["stdout"][-2000:]
    return out["numbers"]


def _plain(price=30.0, intangibles=None):
    return _cached(("plain", price, json.dumps(intangibles, sort_keys=True)),
                   lambda: _ok(_run(_facts(intangibles=intangibles), price)))


def _assert_shifted(n, plain, charge_ps):
    """Every scenario's and the weighted IV at 10/12/15/20/25 is the plain run's IV minus charge_ps (exactly: the
    same present_value less the same float), every IRR is lower and equals solve_irr at price + charge."""
    assert charge_ps > 0
    paths, _ = E.replay_paths(n)
    for lbl in LABELS + ["weighted"]:
        a = n["weighted"] if lbl == "weighted" else n["scenarios"][lbl]
        b = plain["weighted"] if lbl == "weighted" else plain["scenarios"][lbl]
        for k in IV_KEYS:
            assert a[k] == b[k] - charge_ps, (lbl, k, a[k], b[k], charge_ps)
        assert a["irr"] < b["irr"], (lbl, a["irr"], b["irr"])
        assert a["irr"] == E.solve_irr(paths[lbl], n["price"] + charge_ps, n["g_terminal"])[0], lbl
    assert n["implied_irr_weighted"] == n["weighted"]["irr"] < plain["implied_irr_weighted"]
    for k in ("iv_at_10", "iv_at_12", "iv_at_15", "iv_at_20", "iv_at_25"):
        if k in n:
            assert n[k] == n["weighted"][k], k
    assert n["hurdle_prices"] == {"15": n["weighted"]["iv_at_15"], "20": n["weighted"]["iv_at_20"], "25": n["weighted"]["iv_at_25"]}
    assert n["upside_at_15"] == n["weighted"]["iv_at_15"] / n["price"] - 1
    assert n["irr_bear"] == n["scenarios"]["bear"]["irr"] and n["irr_bull"] == n["scenarios"]["bull"]["irr"]
    assert n["irr_low"] == min(n["scenarios"][l]["irr"] for l in LABELS)
    assert n["tier_by_numbers"] == E.tier_for_irr(n["implied_irr_weighted"])
    assert n["tier_bear"] == E.tier_for_irr(n["irr_bear"]) and n["tier_bull"] == E.tier_for_irr(n["irr_bull"])


def _assert_base_untouched(n, plain):
    """The base, its inputs, growth and the projected paths are bit-identical to the run without the charge."""
    for k in ("base_oe_per_share", "base_oe_latest_per_share", "base_oe_normalized_per_share", "base_source",
              "g_blend", "g_base", "paths", "growth_paths", "base_oe_total_latest_fy", "inputs"):
        assert n.get(k) == plain.get(k), (k, n.get(k), plain.get(k))


# ===========================================================================
# 1. Release and the shared helpers
# ===========================================================================
def test_release_is_5_6_0():
    """Release: the acquired-IPR&D rules ship from ENGINE_RELEASE 5.6.0 (engine_version stays 5); a later release
    (5.7.0, the 2026-10-19 rulings — test_rulings57_scaffold pins it) keeps them, so this checks >= 5.6.0."""
    m = re.match(r"(\d+)\.(\d+)\.(\d+)$", E.ENGINE_RELEASE)
    assert m and tuple(int(x) for x in m.groups()) >= (5, 6, 0), E.ENGINE_RELEASE


def test_helpers_are_the_identity_at_zero_and_shift_exactly():
    """Shared helpers (engine, reprice, build_site): a zero charge is bit-identical to present_value / solve_irr; a
    charge c lowers every IV by exactly c and solves the IRR at price + c; iprd_charge_per_share reads only a
    one-time treatment's positive figure (0.0 for a missing block, a pre-5.6 record, the amortized treatment, a
    malformed value)."""
    flows = E.project_path(2.0, 0.12, 9.8, 0.025)
    for r in (0.10, 0.15, 0.25, 0.02):
        assert E.adjusted_value(flows, r, 0.025, 0.0) == E.present_value(flows, r, 0.025)
        assert E.adjusted_value(flows, r, 0.025, 1.5) == E.present_value(flows, r, 0.025) - 1.5
    for px in (10.0, 30.0, 1e9, 0.0001):
        assert E.adjusted_irr(flows, px, 0.025, 0.0) == E.solve_irr(flows, px, 0.025)
        assert E.adjusted_irr(flows, px, 0.025, 2.0) == E.solve_irr(flows, px + 2.0, 0.025)
    assert E.adjusted_irr(flows, 30.0, 0.025, 2.0)[0] < E.solve_irr(flows, 30.0, 0.025)[0]
    one = {"iprd_adjustment": {"treatment": "one_time_value_deduction", "charge_per_share": 2.5}}
    assert E.iprd_charge_per_share(one) == 2.5
    for n in ({}, {"iprd_adjustment": None}, None, {"iprd_adjustment": {"treatment": "amortized_in_base", "charge_per_share": 2.5}},
              {"iprd_adjustment": {"treatment": "no_value_to_adjust", "charge_per_share": 2.5}},
              {"iprd_adjustment": {"treatment": "one_time_value_deduction", "charge_per_share": "2.5"}},
              {"iprd_adjustment": {"treatment": "one_time_value_deduction", "charge_per_share": True}},
              {"iprd_adjustment": {"treatment": "one_time_value_deduction", "charge_per_share": float("nan")}},
              {"iprd_adjustment": {"treatment": "one_time_value_deduction", "charge_per_share": -1.0}}):
        assert E.iprd_charge_per_share(n) == 0.0, n


ADDED_BACK = {"presentation": "added_back_paid_in_investing", "amount": 20e6, "source": "test"}


def test_iprd_period_record_rules():
    """Detection rules per period (unit): cash preferred over the expense when both are filed; an expense-basis
    amount is deducted only beside a cash-flow check saying it was added back and paid in investing (none: excluded
    awaiting_cash_flow_check; paid inside OCF or in shares: excluded); a cash-only period is no record; a $0 expense
    deducts nothing whatever the cash tag says; a negative expense is excluded; [Codex review r8] an expense-basis
    amount is excluded already_in_capex only beside a paid_in_intangible_capex check whose period's capex intangible
    leg covers it (>= 98%; under it the check is not applied) — the leg's size alone is a note, never an exclusion;
    a cash-basis amount is never excluded by it."""
    rec = E.iprd_period_record("2025-12-31", "fy", (EXPENSE, 20e6, "USD", None, "2026-02-20"), (15e6, "USD", None, "2026-02-20"))
    assert (rec["amount"], rec["amount_basis"], rec["tag_used"], rec["deducted"]) == (15e6, "cash_outflow", CASH, 15e6), rec
    rec = E.iprd_period_record("2025-12-31", "fy", (EXPENSE, 20e6, "USD", None, "2026-02-20"), None, check=ADDED_BACK)
    assert (rec["amount"], rec["amount_basis"], rec["tag_used"], rec["deducted"]) == (20e6, "expense", EXPENSE, 20e6), rec
    assert rec["cash_flow_check"]["presentation"] == "added_back_paid_in_investing", rec
    rec = E.iprd_period_record("2025-12-31", "fy", (EXPENSE, 20e6, "USD", None, "2026-02-20"), None)
    assert (rec["amount_basis"], rec["excluded"], rec["deducted"], rec["awaiting"]) == ("expense", "awaiting_cash_flow_check", 0.0, 20e6), rec
    for pres, why in (("inside_operating_cash_flow", "paid_in_operating_cash_flow"), ("paid_in_shares", "paid_in_shares")):
        rec = E.iprd_period_record("2025-12-31", "fy", (EXPENSE, 20e6, "USD", None, "x"), None, check=dict(ADDED_BACK, presentation=pres))
        assert rec["excluded"] == why and rec["deducted"] == 0.0 and "awaiting" not in rec, rec
    assert E.iprd_period_record("2025-12-31", "fy", None, (198e6, "USD", None, "2026-02-20")) is None
    rec = E.iprd_period_record("2025-12-31", "fy", (EXPENSE, 0.0, "USD", None, "x"), (50e6, "USD", None, "x"))
    assert rec["deducted"] == 0.0 and rec["amount"] == 0.0 and rec["excluded"] is None, rec
    rec = E.iprd_period_record("2025-12-31", "fy", (EXPENSE, -5e6, "USD", None, "x"), None)
    assert rec["excluded"] == "negative" and rec["deducted"] == 0.0, rec
    rec = E.iprd_period_record("2025-12-31", "fy", (EXPENSE, 20e6, "USD", None, "x"), None, capex_intang=19.6e6, check=ADDED_BACK)
    assert rec["excluded"] is None and rec["deducted"] == 20e6 and "capex_overlap_note" in rec, rec
    in_capex = dict(ADDED_BACK, presentation="paid_in_intangible_capex")
    rec = E.iprd_period_record("2025-12-31", "fy", (EXPENSE, 20e6, "USD", None, "x"), None, capex_intang=19.6e6, check=in_capex)
    assert rec["excluded"] == "already_in_capex" and rec["deducted"] == 0.0 and "capex_overlap_note" not in rec, rec
    rec = E.iprd_period_record("2025-12-31", "fy", (EXPENSE, 20e6, "USD", None, "x"), None, capex_intang=19.5e6, check=in_capex)
    assert rec["excluded"] == "awaiting_cash_flow_check" and rec["cash_flow_check_mismatch"], rec
    rec = E.iprd_period_record("2025-12-31", "fy", (EXPENSE, 20e6, "USD", None, "x"), None, capex_intang=19.5e6, check=ADDED_BACK)
    assert rec["excluded"] is None and rec["deducted"] == 20e6 and "capex_overlap_note" not in rec, rec
    rec = E.iprd_period_record("2025-12-31", "fy", (EXPENSE, 20e6, "USD", None, "x"), (20e6, "USD", None, "x"), capex_intang=20e6)
    assert rec["excluded"] is None and rec["deducted"] == 20e6 and rec["amount_basis"] == "cash_outflow", rec
    rec = E.iprd_period_record("2025-12-31", "fy", (EXPENSE, None, "EUR", None, "x"), None)
    assert rec["excluded"] == "non_usd_no_rate" and rec["deducted"] == 0.0, rec


def test_negative_cash_fact_falls_back_to_the_expense():
    """[fixer review round] A cash-tag fact filed negative beside a positive expense (a sign error on a payments
    element) never drops the charge: the period takes the expense basis with a cash_sign_note — awaiting the
    cash-flow check without one (so ACQUIRED_IPRD_UNCONFIRMED names it), deducted with one. Before the fix the
    period was excluded "negative" and the $50M charge vanished without a flag."""
    rec = E.iprd_period_record("2025-12-31", "fy", (EXPENSE, 50e6, "USD", None, "x"), (-50e6, "USD", None, "x"))
    assert (rec["amount"], rec["amount_basis"], rec["tag_used"], rec["excluded"]) == (50e6, "expense", EXPENSE, "awaiting_cash_flow_check"), rec
    assert "sign error" in rec["cash_sign_note"], rec
    rec = E.iprd_period_record("2025-12-31", "fy", (EXPENSE, 50e6, "USD", None, "x"), (-50e6, "USD", None, "x"),
                               check=dict(ADDED_BACK, amount=50e6))
    assert rec["deducted"] == 50e6 and rec["excluded"] is None, rec
    n = _ok(_run(_facts(expense={2025: 50e6}, cash={2025: -50e6}), checks=False))
    fl = flags(n, "ACQUIRED_IPRD_UNCONFIRMED")
    assert len(fl) == 1 and "FY2025 $50,000,000" in fl[0], fl
    n = _ok(_run(_facts(expense={2025: 50e6}, cash={2025: -50e6})))
    assert n["iprd_adjustment"]["total"] == 50e6, n["iprd_adjustment"]["periods"]


# ===========================================================================
# 2. Synthetic filer with an IPR&D charge
# ===========================================================================
def test_synthetic_charge_base_identical_iv_lower_by_charge_per_share_irr_lower():
    """Treatment (decision 2): an FY2025 acquired-IPR&D expense of $20M (no cash tag; the cash-flow check says it
    was added back in operating activities and paid in investing) on 100M shares is ONE charge
    of exactly $0.20/share: the base OE, growth and paths are bit-identical to the same filer without the fact;
    every scenario's and the weighted IV at 10/12/15/20/25% is lower by exactly 0.20; every IRR is lower and equals
    solve_irr at price + 0.20; tiers / band / hurdle prices / upside are computed on the adjusted figures; the
    unadjusted figures are kept in iprd_adjustment.before."""
    plain = _plain()
    n = _ok(_run(_facts(expense={2025: 20e6})))
    _assert_base_untouched(n, plain)
    blk = n["iprd_adjustment"]
    assert blk["treatment"] == "one_time_value_deduction" and blk["total"] == 20e6, blk
    assert blk["shares_denominator"] == SHARES and blk["charge_per_share"] == 20e6 / SHARES, blk
    _assert_shifted(n, plain, 20e6 / SHARES)
    for lbl in LABELS + ["weighted"]:
        b = plain["weighted"] if lbl == "weighted" else plain["scenarios"][lbl]
        for k in IV_KEYS + ["irr"]:
            assert blk["before"][lbl][k] == b[k], (lbl, k)
    assert blk["tier_before"] == plain["tier_by_numbers"]
    assert blk["after"]["irr"] == n["implied_irr_weighted"] and blk["after"]["tier"] == n["tier_by_numbers"]
    assert math.isclose(blk["materiality"], (20e6 / SHARES) / n["base_oe_per_share"], rel_tol=1e-12)
    assert blk["materiality"] >= 0.05 and blk["material"] and not blk["recurrent"]
    fl = flags(n, "ACQUIRED_IPRD_CHARGE")
    assert len(fl) == 1 and "FY2025 $20,000,000" in fl[0] and "expense" in fl[0] and "$0.2000/share" in fl[0], fl
    assert not flags(n, "ACQUIRED_IPRD_RECURRENT")
    # the path diagnostics read the unadjusted paths: the scenario spread is the plain run's
    assert n["diagnostics"]["scenario_spread_iv15"] == plain["diagnostics"]["scenario_spread_iv15"]


def test_synthetic_tier_is_decided_on_the_adjusted_irr():
    """Decision 5 (tiers on adjusted figures): at a price where the unadjusted weighted IRR is 15.1% (Tier B), a
    $1.00/share charge takes it below 15% — the record's tier is C, iprd_adjustment.tier_before says B."""
    plain = _plain()
    w, _ = E.replay_paths(plain)
    px = E.present_value(w["weighted"], 0.151, 0.025)
    p2 = _ok(_run(_facts(), price=px))
    n = _ok(_run(_facts(expense={2025: 100e6}), price=px))
    assert p2["tier_by_numbers"] == "B" and n["iprd_adjustment"]["tier_before"] == "B", (p2["implied_irr_weighted"],)
    assert n["implied_irr_weighted"] < 0.15 and n["tier_by_numbers"] == "C", n["implied_irr_weighted"]
    _assert_shifted(n, p2, 1.0)


def test_synthetic_cash_outflow_preferred_over_the_expense():
    """Detection (decision 1): where the expense tag and the investing-outflow tag report the same period, the cash
    figure is the amount (consideration paid in shares is already in the share count): expense $20M, cash $15M ->
    $0.15/share, basis cash_outflow, tag PaymentsToAcquireInProcessResearchAndDevelopment."""
    n = _ok(_run(_facts(expense={2025: 20e6}, cash={2025: 15e6})))
    blk = n["iprd_adjustment"]
    p = [x for x in blk["periods"] if x["period"] == "2025-12-31"][0]
    assert (p["amount_basis"], p["tag_used"], p["deducted"], p["expense"], p["cash"]) == ("cash_outflow", CASH, 15e6, 20e6, 15e6), p
    _assert_shifted(n, _plain(), 15e6 / SHARES)


def test_synthetic_pre_2022_expense_tag_is_read_and_counted_once():
    """Detection: ResearchAndDevelopmentInProcess (the pre-2022 name, in real use at EXEL FY2021-22 and BIIB
    FY2017-22) qualifies; a period filing both names with one value is counted once (the current tag wins)."""
    plain = _plain()
    n = _ok(_run(_facts(old_expense={2024: 10e6})))
    p = [x for x in n["iprd_adjustment"]["periods"] if x["deducted"]][0]
    assert p["tag_used"] == EXPENSE_OLD and p["period"] == "2024-12-31", p
    _assert_shifted(n, plain, 10e6 / SHARES)
    n2 = _ok(_run(_facts(expense={2024: 10e6}, old_expense={2024: 10e6})))
    assert n2["iprd_adjustment"]["total"] == 10e6 and n2["weighted"] == n["weighted"], n2["iprd_adjustment"]["total"]


# ===========================================================================
# 3. Non-goals and untouched filers
# ===========================================================================
def _strip(n):
    return {k: v for k, v in n.items() if k not in ("content_hash",)}


def test_impairment_only_filer_is_untouched():
    """Non-goal 4: an impairment of a previously capitalized intangible (ImpairmentOfIntangibleAssetsExcludingGoodwill
    $48.7M, HALO's FY2025 shape) is never read — the run is identical in every field to the filer without it: no
    iprd_adjustment block, no flag, the same IVs and IRRs."""
    plain = _plain()
    n = _ok(_run(_facts(impairment={2025: 48.7e6, 2024: 10e6})))
    assert n["iprd_adjustment"] is None and not flags(n, "ACQUIRED_IPRD")
    assert _strip(n) == _strip(plain)


def test_cash_tag_only_filer_is_untouched_maa():
    """Detection (main-agent addition): a period with only the cash tag never qualifies — MAA, an apartment REIT, files
    PaymentsToAcquireInProcessResearchAndDevelopment at $198.2M / $313.9M / $272.0M (FY2023-25) for development
    spending with no expense tag. The run is identical to the filer without it."""
    plain = _plain()
    n = _ok(_run(_facts(cash={2023: 198152000, 2024: 313888000, 2025: 272030000})))
    assert n["iprd_adjustment"] is None and not flags(n, "ACQUIRED_IPRD")
    assert _strip(n) == _strip(plain)


def test_expense_only_filer_paying_inside_ocf_is_untouched_nbix():
    """[fixer review round] NBIX's shape: the expense tag only (FY2023-25 $143.9M / $12.5M / $17.4M, no us-gaap
    cash tag) and a 10-K cash-flow statement with no acquired-IPR&D add-back and no investing line (FY2025 10-K
    0000914475-26-000007, R7.htm) — the upfronts were paid inside operating cash flow, so OE already carries them.
    Without a cash-flow check nothing is deducted (every IV and IRR equals the filer without the facts), every period
    is excluded awaiting_cash_flow_check, ACQUIRED_IPRD_UNCONFIRMED names the three periods and no CHARGE flag
    fires; with the check declaring "inside_operating_cash_flow" the run is untouched and raises no CHARGE flag.
    Before the fix the engine deducted $1.74/share and raised CHARGE and RECURRENT. [Codex review r28 of PR #47] The
    three expensed years still count toward ACQUIRED_IPRD_RECURRENT, awaiting the check or paid inside operating
    cash flow: buying R&D every year is the same habit however it is paid (the flag asks the worker to assess it;
    nothing is deducted)."""
    plain = _plain()
    exp = {2023: 143.9e6, 2024: 12.5e6, 2025: 17.4e6}
    n = _ok(_run(_facts(expense=exp), checks=False))
    blk = n["iprd_adjustment"]
    assert blk["total"] == 0.0 and blk["treatment"] == "awaiting_cash_flow_check" and blk["unconfirmed_total"] == sum(exp.values()), blk
    assert [p["excluded"] for p in blk["periods"]] == ["awaiting_cash_flow_check"] * 3, blk["periods"]
    assert n["weighted"] == plain["weighted"] and n["scenarios"] == plain["scenarios"] and E.iprd_charge_per_share(n) == 0.0
    fl = flags(n, "ACQUIRED_IPRD_UNCONFIRMED")
    assert len(fl) == 1 and "FY2023 $143,900,000" in fl[0] and "FY2025 $17,400,000" in fl[0] and "NBIX" in fl[0], fl
    assert not flags(n, "ACQUIRED_IPRD_CHARGE") and blk["recurrent"] and flags(n, "ACQUIRED_IPRD_RECURRENT")
    chk = [dict(c, presentation="inside_operating_cash_flow") for c in auto_checks(_facts(expense=exp))]
    m = _ok(_run(_facts(expense=exp), judgment={"iprd_cash_flow_check": chk}))
    mb = m["iprd_adjustment"]
    assert [p["excluded"] for p in mb["periods"]] == ["paid_in_operating_cash_flow"] * 3 and mb["treatment"] == "none", mb
    assert m["weighted"] == plain["weighted"] and not flags(m, "ACQUIRED_IPRD_CHARGE")
    assert mb["fy_with_charge"] == ["2023-12-31", "2024-12-31", "2025-12-31"] and mb["recurrent"], mb
    assert [f.split(":")[0] for f in flags(m, "ACQUIRED_IPRD")] == ["ACQUIRED_IPRD_RECURRENT"], flags(m, "ACQUIRED_IPRD")
    # the same check with another amount than the filed expense is not applied: the period stays awaiting
    bad = [dict(chk[0], amount=100e6)] + chk[1:]
    b = _ok(_run(_facts(expense=exp), judgment={"iprd_cash_flow_check": bad}))
    p0 = b["iprd_adjustment"]["periods"][0]
    assert p0["excluded"] == "awaiting_cash_flow_check" and p0["cash_flow_check_mismatch"]["declared_amount"] == 100e6, p0
    assert flags(b, "ACQUIRED_IPRD_UNCONFIRMED")


def test_paid_in_shares_check_is_not_deducted():
    """[fixer review round] An expensed charge the 10-K shows paid in shares (a non-cash add-back with no investing
    outflow): the dilution is already in the share count — excluded paid_in_shares, nothing deducted."""
    chk = [dict(c, presentation="paid_in_shares") for c in auto_checks(_facts(expense={2025: 20e6}))]
    n = _ok(_run(_facts(expense={2025: 20e6}), judgment={"iprd_cash_flow_check": chk}))
    p = [x for x in n["iprd_adjustment"]["periods"] if x["period"] == "2025-12-31"][0]
    assert p["excluded"] == "paid_in_shares" and n["weighted"] == _plain()["weighted"], p


def test_deferred_cash_payment_of_an_accrued_charge_is_counted_biib():
    """[fixer review round] BIIB's shape: FY2025 expense $85.0M with $50.0M paid (cash tag, 10-K
    0000875045-26-000013), and the Q1 2026 10-Q files the $35.0M remainder on the cash tag alone. On a TTM base the
    window counts $85M — the YTD cash is a deferred payment bounded by the unpaid remainder — not $50M; it is not a
    new charge (no recurrence from it). Cash beyond the remainder stays ignored (cash_only), and a filer that never
    expenses (MAA) still never qualifies."""
    facts = _facts(expense={2025: 85e6}, cash={2025: 50e6})
    _ytd(facts, CASH, "2026-01-01", "2026-03-31", 35e6, "2026-04-29", fp="Q1")
    ttm = _ttm_doc(2.1, 100e6)
    ttm["inputs"]["ocf"]["ytd_current_period"] = ["2026-01-01", "2026-03-31"]
    n = _ok(_run(facts, extra=["--ttm"], ttm=ttm))
    blk = n["iprd_adjustment"]
    assert blk["total"] == 85e6 and blk["charge_per_share"] == 85e6 / 100e6, blk["periods"]
    d = [p for p in blk["periods"] if p.get("deferred_payment")]
    assert len(d) == 1 and d[0]["window"] == "ttm_current_ytd" and d[0]["deducted"] == 35e6 and d[0]["amount_basis"] == "cash_outflow", d
    assert not blk["ignored_cash_only"], blk["ignored_cash_only"]
    # more cash than the remainder: only the remainder counts
    facts2 = _facts(expense={2025: 85e6}, cash={2025: 50e6})
    _ytd(facts2, CASH, "2026-01-01", "2026-03-31", 60e6, "2026-04-29", fp="Q1")
    b2 = _ok(_run(facts2, extra=["--ttm"], ttm=ttm))["iprd_adjustment"]
    assert b2["total"] == 85e6 and b2["ignored_cash_only"][0]["cash"] == 25e6, b2
    # an FY deferred payment (FY2024 accrued, FY2025 paid with a $0 expense) is not a second year with a charge
    n3 = _ok(_run(_facts(expense={2024: 40e6, 2025: 0.0}, cash={2024: 10e6, 2025: 30e6})))
    b3 = n3["iprd_adjustment"]
    assert b3["total"] == 40e6 and b3["fy_with_charge"] == ["2024-12-31"] and not b3["recurrent"], b3
    # MAA (cash tag only, never expensed): untouched
    assert _ok(_run(_facts(cash={2024: 313888000, 2025: 272030000})))["iprd_adjustment"] is None


def test_overlap_guard_already_in_capex():
    """Overlap guard (main-agent addition; [Codex review r8] declared, never inferred from size): an expense-basis
    charge (no cash tag) whose cash-flow check says it was paid inside the intangible purchases the period's 5.5 capex
    already charged to OE (presentation paid_in_intangible_capex, the leg >= 98% of the expense) is not deducted —
    recorded `excluded: already_in_capex`, the valuation equals the same filer's run without the IPR&D fact; a leg
    under 98% cannot hold it, so the check is not applied and the period stays gated; the added-back-and-paid-in-
    investing check deducts it whatever the leg's size."""
    intang = {2025: 20e6}
    plain = _plain(intangibles=intang)
    n = _ok(_run(_facts(expense={2025: 20e6}, intangibles=intang), judgment={"iprd_cash_flow_check": _intang_check()}))
    blk = n["iprd_adjustment"]
    p = [x for x in blk["periods"] if x["period"] == "2025-12-31"][0]
    assert p["excluded"] == "already_in_capex" and p["deducted"] == 0.0 and blk["total"] == 0.0, p
    assert blk["treatment"] == "none" and blk["charge_per_share"] == 0.0
    assert n["weighted"] == plain["weighted"] and n["scenarios"] == plain["scenarios"] and not flags(n, "ACQUIRED_IPRD")
    n2 = _ok(_run(_facts(expense={2025: 25e6}, intangibles=intang)))
    assert n2["iprd_adjustment"]["total"] == 25e6, n2["iprd_adjustment"]["periods"]
    _assert_shifted(n2, plain, 25e6 / SHARES)
    n3 = _ok(_run(_facts(expense={2025: 25e6}, intangibles=intang),
                  judgment={"iprd_cash_flow_check": _intang_check(amount=25e6)}))
    p3 = [x for x in n3["iprd_adjustment"]["periods"] if x["period"] == "2025-12-31"][0]
    assert p3["excluded"] == "awaiting_cash_flow_check" and p3["cash_flow_check_mismatch"], p3


# ===========================================================================
# 4. Recurrence, materiality and the no-cliff deduction
# ===========================================================================
def test_charges_in_two_of_three_fy_raise_recurrent_and_are_not_amortized():
    """Decision 3: qualifying charges in FY2023 and FY2025 (2 of the last 3) -> ACQUIRED_IPRD_RECURRENT beside
    ACQUIRED_IPRD_CHARGE; the engine does not amortize (the base is unchanged) — both charges are deducted once,
    $0.35/share."""
    plain = _plain()
    n = _ok(_run(_facts(expense={2023: 15e6, 2025: 20e6})))
    blk = n["iprd_adjustment"]
    assert blk["recurrent"] and blk["fy_with_charge"] == ["2023-12-31", "2025-12-31"], blk
    rf = flags(n, "ACQUIRED_IPRD_RECURRENT")
    assert len(rf) == 1 and "FY2023, FY2025 (2 of the last 3" in rf[0] and "iprd_amortized" in rf[0], rf
    assert flags(n, "ACQUIRED_IPRD_CHARGE")
    _assert_base_untouched(n, plain)
    _assert_shifted(n, plain, 35e6 / SHARES)
    # a charge outside the last 3 FY is outside the window
    n3 = _ok(_run(_facts(expense={2022: 15e6, 2025: 20e6})))
    assert n3["iprd_adjustment"]["total"] == 20e6 and not n3["iprd_adjustment"]["recurrent"]


def amortized_decl(n_recurrent, **over):
    """The worker's iprd_amortized base_override for the 2-of-3 synthetic filer, built only from that run's printed
    figures (WORKER_SPEC step 8 (c)): native median base - mean of the three FY charges / the latest diluted count."""
    blk = n_recurrent["iprd_adjustment"]
    figs = [next((p["deducted"] for p in blk["periods"] if p["window"] == "fy" and p["period"] == q), 0.0)
            for q in blk["window"]["fy"]]
    native = n_recurrent["base_oe_normalized_per_share"]
    d = {"basis": "iprd_amortized", "kind": "filing", "native_base": "median_of_last_3_fy_oe_per_share",
         "figures": figs, "shares": SHARES, "value": native - sum(figs) / 3 / SHARES,
         "source": "this run's dcf_numbers.json iprd_adjustment (FY2023 $15,000,000, FY2025 $20,000,000) and the median base",
         "reason": "test: acquisition-led R&D recurs, amortized as a maintenance charge"}
    d.update(over)
    return d


def _recurrent():
    return _cached("recurrent", lambda: _ok(_run(_facts(expense={2023: 15e6, 2025: 20e6}))))


def test_iprd_amortized_declaration_suppresses_the_one_time_deduction():
    """Decision 3, the amortized path (main-agent addition): a --base-oe-ps pin that judgment.json declares as a
    base_override of basis iprd_amortized (figures = this run's three FY charges, shares = the latest diluted count, value = native
    median - mean charge / shares, to the cent) carries the charge in the base: treatment amortized_in_base, NO
    one-time deduction on top — the IVs and IRRs are exactly those of the same pin without any IPR&D fact — and the
    block records the construction."""
    rec = _recurrent()
    d = amortized_decl(rec)
    pin = repr(d["value"])
    n = _ok(_run(_facts(expense={2023: 15e6, 2025: 20e6}), extra=["--base-oe-ps", pin], judgment={"base_override": d}))
    ref = _ok(_run(_facts(), extra=["--base-oe-ps", pin]))
    blk = n["iprd_adjustment"]
    assert blk["treatment"] == "amortized_in_base" and E.iprd_charge_per_share(n) == 0.0, blk["treatment"]
    assert n["base_oe_per_share"] == d["value"] and n["weighted"] == ref["weighted"] and n["scenarios"] == ref["scenarios"]
    am = blk["amortized"]
    assert am["figures"] == [15e6, 0.0, 20e6] and am["shares"] == SHARES and abs(am["expected_value"] - d["value"]) < 1e-12, am
    assert any("amortized_in_base" in f or "iprd_amortized base_override (no one-time" in f for f in flags(n, "ACQUIRED_IPRD_CHARGE"))
    assert "before" not in blk


def test_iprd_amortized_declaration_that_does_not_reproduce_is_refused():
    """Amortized path (main-agent addition): the engine recomputes the amortized base and refuses
    (BAD_BASE_OVERRIDE, exit 3) a declaration whose value
    is off by more than a cent, whose figures are not this run's charges, whose shares are not the native count, or
    that is declared at a filer whose charges are not recurrent."""
    rec = _recurrent()
    facts = _facts(expense={2023: 15e6, 2025: 20e6})
    for over, needle in (({"value": amortized_decl(rec)["value"] - 0.02}, "does not reproduce"),
                         ({"figures": [15e6, 20e6]}, "figures must be"),
                         ({"shares": 99e6}, "shares must be"),
                         ({"native_base": "latest_fy"}, "native_base must be"),
                         ({"kind": "estimate"}, "kind must be 'filing'")):
        d = amortized_decl(rec, **over)
        out = _run(facts, extra=["--base-oe-ps", repr(d["value"])], judgment={"base_override": d})
        assert out["exit"] == 3 and "BAD_BASE_OVERRIDE" in out["stdout"] and needle in out["stdout"], (over, out["stdout"][-600:])
    one = _ok(_run(_facts(expense={2025: 20e6})))
    d = amortized_decl(one)
    out = _run(_facts(expense={2025: 20e6}), extra=["--base-oe-ps", repr(d["value"])], judgment={"base_override": d})
    assert out["exit"] == 3 and "only for recurrent charges" in out["stdout"], out["stdout"][-600:]


def test_below_threshold_charge_is_deducted_without_a_flag():
    """No cliff (main-agent addition): $1M in FY2024 and FY2025 (~1% of the base OE total) — no flag fires (not material, so not
    recurrent either), yet the deduction is applied and reported in iprd_adjustment."""
    plain = _plain()
    n = _ok(_run(_facts(expense={2024: 1e6, 2025: 1e6})))
    blk = n["iprd_adjustment"]
    assert blk["materiality"] < 0.05 and not blk["material"] and not blk["recurrent"], blk
    assert not flags(n, "ACQUIRED_IPRD")
    assert blk["treatment"] == "one_time_value_deduction"
    _assert_shifted(n, plain, 2e6 / SHARES)


def test_charge_beside_a_non_positive_base_is_recorded_and_flagged_not_deducted():
    """Materiality (main-agent addition): a base OE total <= 0 (Tier F, no scenarios): the charge is recorded, ACQUIRED_IPRD_CHARGE fires for any
    charge, and nothing is deducted (treatment no_value_to_adjust, no IV exists)."""
    facts = _facts(expense={2025: 5e6})
    for y in (2019, 2020, 2021, 2022, 2023, 2024, 2025):
        for e in facts["facts"]["us-gaap"]["ShareBasedCompensation"]["units"]["USD"]:
            e["val"] = 400e6
    n = _ok(_run(facts))
    assert n["tier_by_numbers"] == "F", n["tier_by_numbers"]
    blk = n["iprd_adjustment"]
    assert blk["treatment"] == "no_value_to_adjust" and blk["total"] == 5e6 and blk["materiality"] is None, blk
    assert len(flags(n, "ACQUIRED_IPRD_CHARGE")) == 1 and "not deducted" in flags(n, "ACQUIRED_IPRD_CHARGE")[0]
    assert E.iprd_charge_per_share(n) == 0.0


# ===========================================================================
# 5. TTM base: FY and TTM windows count each period once
# ===========================================================================
def _ttm_doc(per_share, shares):
    # v5.7 (07 G16 / 09 rebase A8): a ttm.json as the current ttm.py writes it — stamped with the engine release
    # (rulings57.add_ttm_engine_release), so a current-release run whose basis reads it is a 5.7 run on a 5.7
    # ttm.json (make_score refuse_pre57_ttm_json); the stamp is outside ttm_input_hash
    import rulings57
    return rulings57.add_ttm_engine_release(
        {"fy_end": "2025-12-31", "ytd_end": "2026-06-30", "ttm_oe_per_share": per_share, "ttm_shares_diluted": shares,
         "ttm_oe_total": per_share * shares,
         "inputs": {"ocf": {"fy_period": ["2025-01-01", "2025-12-31"], "ytd_prior_period": ["2025-01-01", "2025-06-30"],
                            "ytd_current_period": ["2026-01-01", "2026-06-30"]}}, "warnings": [], "overrides_used": []})


def test_ttm_window_counts_each_fiscal_period_once():
    """Window (main-agent addition): on a ttm.json pin the window is the last 3 FY plus the current-YTD 10-Q leg after the latest FY end. An
    FY2025 charge of $20M (10-K) that the 2025 H1 10-Q also reports (the prior-YTD leg, inside FY2025) is counted
    once; the 2026 H1 10-Q charge ($5M, re-filed later as a comparative column) is added once: total $25M on
    ttm.json's 98M current-YTD diluted shares."""
    facts = _facts(expense={2025: 20e6})
    _ytd(facts, EXPENSE, "2025-01-01", "2025-06-30", 20e6, "2025-08-05")
    _ytd(facts, EXPENSE, "2026-01-01", "2026-06-30", 5e6, "2026-08-05")
    _ytd(facts, EXPENSE, "2026-01-01", "2026-06-30", 5e6, "2026-11-05", fp="Q3")
    ttm = _ttm_doc(2.1, 98e6)
    plain = _ok(_run(_facts(), extra=["--ttm"], ttm=ttm))
    n = _ok(_run(facts, extra=["--ttm"], ttm=ttm))
    blk = n["iprd_adjustment"]
    assert blk["total"] == 25e6, blk["periods"]
    assert [(p["window"], p["deducted"]) for p in blk["periods"] if p["deducted"]] == [("fy", 20e6), ("ttm_current_ytd", 5e6)]
    assert blk["shares_denominator"] == 98e6 and blk["shares_source"] == "ttm.json ttm_shares_diluted"
    assert blk["window"]["ttm_current_ytd"] == ["2026-01-01", "2026-06-30"]
    assert n["base_oe_per_share"] == plain["base_oe_per_share"] == 2.1
    _assert_shifted(n, plain, 25e6 / 98e6)
    # a median base reads the FY window only (no YTD leg)
    m = _ok(_run(facts))
    assert m["iprd_adjustment"]["total"] == 20e6 and m["iprd_adjustment"]["window"]["ttm_current_ytd"] is None


# ===========================================================================
# 6. Regressions: HALO (the case) and APP (bit for bit)
# ===========================================================================
def _halo(judgment=None):
    def go():
        fx = H.load_fixture("HALO")
        out = run("HALO", HALO_ARGS, judgment=HALO_J if judgment is None else judgment, ttm=HALO_TTM, fixture=fx)
        assert out["exit"] == 0, out["stdout"][-2000:]
        return out["numbers"]
    return _cached(("halo", json.dumps(judgment, sort_keys=True)), go)


def _halo_no_iprd():
    def go():
        fx = copy.deepcopy(H.load_fixture("HALO"))
        for t in (EXPENSE, EXPENSE_OLD, CASH):
            fx["facts"]["facts"]["us-gaap"].pop(t, None)
        out = run("HALO", HALO_ARGS, judgment={}, ttm=HALO_TTM, fixture=fx)
        assert out["exit"] == 0, out["stdout"][-2000:]
        return out["numbers"]
    return _cached("halo0", go)


def test_halo_changes_only_by_the_disclosed_adjustment():
    """HALO regression (the case): from its real companyfacts at the scored price and inputs, the TTM base is
    bit-identical to the recorded run (6.08686891852046); FY2025's $284,887,000 acquired-IPR&D expense (Surf Bio;
    ResearchAndDevelopmentAssetAcquiredOtherThanThroughBusinessCombinationWrittenOff, no us-gaap cash tag — the
    10-K's investing line is a custom extension; judgment.json's iprd_cash_flow_check cites the add-back and the
    investing line) is one charge of 284,887,000 / 122,092,000 ttm.json shares =
    $2.3334/share (38.3% of the $743.2M TTM OE); every IV at 10/12/15/20/25% of every scenario and the weighted
    case is the recorded figure minus exactly that; weighted IRR 22.64% -> 22.39%, still Tier A; ACQUIRED_IPRD_CHARGE
    fires, not RECURRENT (only Surf Bio expensed IPR&D in the window); the $48.7M FY2025 intangible impairment in
    the fixture is not read."""
    n = _halo()
    c = HALO_CHARGE / 122092000
    assert n["base_oe_per_share"] == HALO_BASE and n["g_base"] == 0.35
    blk = n["iprd_adjustment"]
    assert blk["total"] == HALO_CHARGE and blk["charge_per_share"] == c and blk["treatment"] == "one_time_value_deduction"
    assert round(c, 4) == 2.3334 and round(blk["materiality"], 4) == 0.3833 and not blk["recurrent"], blk
    ded = [p for p in blk["periods"] if p["deducted"]]
    assert len(ded) == 1 and ded[0]["period"] == "2025-12-31" and ded[0]["tag_used"] == EXPENSE and ded[0]["amount_basis"] == "expense"
    assert all(p["tag_used"] in (EXPENSE, EXPENSE_OLD, CASH, None) for p in blk["periods"])
    for lbl, rec in HALO_REC.items():
        a = n["weighted"] if lbl == "weighted" else n["scenarios"][lbl]
        for k in IV_KEYS:
            assert a[k] == rec[k] - c, (lbl, k, a[k], rec[k] - c)
            assert blk["before"][lbl][k] == rec[k], (lbl, k)
        assert blk["before"][lbl]["irr"] == rec["irr"], lbl
        assert a["irr"] < rec["irr"] and round(a["irr"], 4) == HALO_IRR_AFTER[lbl], (lbl, a["irr"])
    assert round(n["weighted"]["iv_at_15"], 2) == 241.27
    assert n["tier_by_numbers"] == "A" and blk["tier_before"] == "A"
    assert (n["tier_bear"], n["tier_bull"]) == ("B", "S")
    assert len(flags(n, "ACQUIRED_IPRD_CHARGE")) == 1 and not flags(n, "ACQUIRED_IPRD_RECURRENT")
    assert not flags(n, "ACQUIRED_IPRD_UNCONFIRMED")


def test_halo_without_the_cash_flow_check_is_not_deducted():
    """[fixer review round] HALO from its real companyfacts with no iprd_cash_flow_check: companyfacts alone cannot
    show the add-back, so the FY2025 charge awaits the check — every IV and IRR is the recorded 5.4.0 run's,
    ACQUIRED_IPRD_UNCONFIRMED names FY2025 $284,887,000 and no CHARGE flag fires."""
    n = _halo(judgment={})
    blk = n["iprd_adjustment"]
    assert blk["treatment"] == "awaiting_cash_flow_check" and blk["total"] == 0.0 and blk["unconfirmed_total"] == HALO_CHARGE, blk
    for lbl, rec in HALO_REC.items():
        a = n["weighted"] if lbl == "weighted" else n["scenarios"][lbl]
        assert all(a[k] == rec[k] for k in IV_KEYS) and a["irr"] == rec["irr"], lbl
    fl = flags(n, "ACQUIRED_IPRD_UNCONFIRMED")
    assert len(fl) == 1 and "FY2025 $284,887,000" in fl[0] and round(blk["unconfirmed_materiality"], 4) == 0.3833, (fl, blk)
    assert not flags(n, "ACQUIRED_IPRD_CHARGE")


def test_halo_every_other_field_equals_the_run_without_the_charge():
    """HALO regression, the other half: against the same fixture with the IPR&D tags removed, the only fields that
    differ are the disclosed adjustment and what is computed from it (IVs, IRRs, tiers, band, hurdle prices, upside,
    the flag list's new entry and the TIER_BAND text's adjusted percentages); the CSV rows are identical."""
    n, z = _halo(), _halo_no_iprd()
    assert z["iprd_adjustment"] is None
    moved = {"iprd_adjustment", "scenarios", "weighted", "implied_irr_weighted", "implied_irr_base", "irr_bear", "irr_bull",
             "irr_low", "irr_high", "hurdle_prices", "upside_at_15", "upside_at_12", "iv_at_15", "iv_at_12", "iv_at_20",
             "iv_at_25", "fragility_flags", "content_hash",
             # [Codex review r22] the fixture without the tags declares no cash-flow check: another judgment input
             "iprd_judgment_hash"}
    diff = {k for k in set(n) | set(z) if n.get(k) != z.get(k)}
    assert diff <= moved | {"diagnostics"}, diff - moved
    # [review] the TV share is of the ADJUSTED IV@15 (the same terminal PV over the published IV); the rest is equal
    assert {k: v for k, v in n["diagnostics"].items() if k != "tv_share_at_15"} ==         {k: v for k, v in z["diagnostics"].items() if k != "tv_share_at_15"}
    assert math.isclose(n["diagnostics"]["tv_share_at_15"] * n["weighted"]["iv_at_15"],
                        z["diagnostics"]["tv_share_at_15"] * z["weighted"]["iv_at_15"], rel_tol=1e-12)
    extra = [f for f in n["fragility_flags"] if f not in z["fragility_flags"]]
    gone = [f for f in z["fragility_flags"] if f not in n["fragility_flags"]]
    assert [f.split(":")[0] for f in extra] == ["ACQUIRED_IPRD_CHARGE", "TIER_BAND"], extra
    assert [f.split(":")[0] for f in gone] == ["TIER_BAND"], gone


def test_app_bit_for_bit_with_no_iprd_facts():
    """APP regression: APP's real companyfacts carry no acquired-IPR&D expense or cash tag (verified 2026-10-19 —
    only DeferredTaxAssetsInProcessResearchAndDevelopment, which is not read), so the 5.6 engine reproduces the
    recorded run's valuation bit for bit (assert_same_math, the 5.5 test's comparison) with no iprd_adjustment
    block and no new flag."""
    rec = recorded_matching_fixture("APP")
    out = run("APP", H.recorded_args(rec), judgment=APP_J, ttm={"ttm_oe_per_share": rec["base_oe_per_share"]})
    assert out["exit"] == 0, out["stdout"][-1500:]
    n = out["numbers"]
    assert_same_math(n, rec, "APP (5.6)")
    for lbl in LABELS:
        assert n["scenarios"][lbl]["iv_at_20"] == E.present_value(E.replay_paths(n)[0][lbl], 0.20, n["g_terminal"])
    assert n["iprd_adjustment"] is None and not flags(n, "ACQUIRED_IPRD")
    assert n["engine_release"] == E.ENGINE_RELEASE   # the current release (5.6.0 when written, 5.7.0 since the rulings)


# ===========================================================================
# 7. The other consumers agree with the engine on an adjusted record
# ===========================================================================
def _adjusted():
    return _cached("adj", lambda: _ok(_run(_facts(expense={2023: 15e6, 2025: 20e6}))))


def test_reprice_live_irr_and_ivs_agree_with_the_engine():
    """reprice.py: at the scored price the live weighted and scenario IRRs equal the engine's ADJUSTED ones bit for
    bit (solve_irr at price + charge on the replayed paths); the live IVs are the adjusted ones; at another price
    the live IRR is solve_irr(paths, price + charge); across a 2:1 split since scoring the charge is restated per
    today's share (charge / 2) and the IRR at the halved price equals the scored one."""
    import reprice as R
    n = _adjusted()
    c = E.iprd_charge_per_share(n)
    assert c == 0.35
    lv = R.reprice(n, n["price"])
    assert lv["irr_weighted"] == n["implied_irr_weighted"]
    for lbl in LABELS:
        assert lv["scenarios"][lbl]["irr"] == n["scenarios"][lbl]["irr"], lbl
    for k in ("iv_at_15", "iv_at_12", "iv_at_20", "iv_at_25"):
        assert lv[k] == n["weighted"][k], k
    assert lv["tier_by_numbers"] == n["tier_by_numbers"]
    paths, _ = E.replay_paths(n)
    lv2 = R.reprice(n, 25.0)
    assert lv2["irr_weighted"] == E.solve_irr(paths["weighted"], 25.0 + c, n["g_terminal"])[0]
    # a pre-5.4-shaped copy (no stored weighted IVs): the replay fallback is adjusted too
    m = copy.deepcopy(n)
    for k in ("iv_at_15", "iv_at_12", "iv_at_20", "iv_at_25"):
        m["weighted"].pop(k, None)
        m.pop(k, None)
    lv3 = R.reprice(m, n["price"])
    for k in ("iv_at_15", "iv_at_12", "iv_at_20", "iv_at_25"):
        assert lv3[k] == n["weighted"][k], (k, lv3[k], n["weighted"][k])
    saved = R.check_basis
    R.check_basis = lambda numbers, prices, fund=None: {"status": "split_adjusted", "factor": 2.0, "split": "2:1"}
    try:
        lv4 = R.reprice(n, n["price"] / 2, prices={})
    finally:
        R.check_basis = saved
    assert math.isclose(lv4["irr_weighted"], n["implied_irr_weighted"], rel_tol=0, abs_tol=1e-12), (lv4["irr_weighted"], n["implied_irr_weighted"])
    assert lv4["iprd_charge_per_share"] == c / 2 and lv["iprd_charge_per_share"] == c


def test_reprice_record_without_the_block_is_unchanged():
    """reprice.py on a pre-5.6 record (no iprd_adjustment): the live IRR is solve_irr at the price, exactly as before,
    and live.json says the charge is 0."""
    import reprice as R
    n = _plain()
    paths, _ = E.replay_paths(n)
    lv = R.reprice(n, 25.0)
    assert lv["irr_weighted"] == E.solve_irr(paths["weighted"], 25.0, n["g_terminal"])[0]
    assert lv["iprd_charge_per_share"] == 0.0


def test_build_site_sensitivity_and_hurdles_agree_with_the_engine():
    """build_site.py: the forecast sensitivity table, the hurdle prices and the at-floor flag read the engine's
    adjusted figures; for a record whose stored IVs / hurdle prices / floor flags are missing (the replay fallback)
    they are recomputed through adjusted_value / adjusted_irr and equal the engine's bit for bit."""
    import build_site as B
    n = _adjusted()
    s = {"price": n["price"]}
    paths, _ = E.replay_paths(n)
    sens = B.scenario_sensitivity(n, s, paths, None)
    hp = B.hurdle_prices(n, s, paths)
    m = copy.deepcopy(n)
    m.pop("hurdle_prices")
    for lbl in LABELS:
        for k in IV_KEYS + ["irr_at_floor"]:
            m["scenarios"][lbl].pop(k)
    for k in IV_KEYS + ["irr_at_floor"]:
        m["weighted"].pop(k)
    m["diagnostics"].pop("irr_at_floor")
    sens2 = B.scenario_sensitivity(m, s, paths, None)
    hp2 = B.hurdle_prices(m, s, paths)
    for lbl in LABELS + ["weighted"]:
        a = n["weighted"] if lbl == "weighted" else n["scenarios"][lbl]
        for k, r in RATES:
            rate = str(int(round(r * 100)))
            assert sens[lbl][rate] == a[k] == sens2[lbl][rate], (lbl, rate, sens[lbl][rate], sens2[lbl][rate], a[k])
        assert sens2[lbl]["irr_at_floor"] == a["irr_at_floor"], lbl
    assert hp == hp2 == n["hurdle_prices"], (hp, hp2)
    # at a price where only the ADJUSTED IRR sits at the solver floor, the replayed flag follows the adjustment
    w = paths["weighted"]
    px = E.present_value(w, 0.0305, 0.025)
    x = E.present_value(w, 0.0295, 0.025) - px
    assert B.scored_floor((), w, px, 0.025) is False                     # the old call is unchanged
    assert B.scored_floor((), w, px, 0.025, charge_ps=x) is True
    # a split since scoring restates the charge and the IVs kept beside it per today's share (SPLIT_DIVIDE) and the
    # denominator in today's shares (SPLIT_MULTIPLY), like every other per-share figure of the run
    rec = {"numbers": copy.deepcopy(n), "row": {},
           "score": {"iprd_adjustment": {"charge_per_share": 0.35, "shares_denominator": 1e8,
                                         "iv_before": {"15": 10.0, "20": 8.0, "25": 6.0}, "iv_after": {"15": 9.65, "20": 7.65, "25": 5.65}}}}
    B.restate_split(rec, 2.0, "2:1", {})
    rb = rec["numbers"]["iprd_adjustment"]
    assert rb["charge_per_share"] == 0.175 and rb["shares_denominator"] == 2e8, rb
    assert rb["before"]["weighted"]["iv_at_15"] == n["iprd_adjustment"]["before"]["weighted"]["iv_at_15"] / 2
    assert rb["after"]["weighted"]["iv_at_25"] == n["iprd_adjustment"]["after"]["weighted"]["iv_at_25"] / 2
    sb = rec["score"]["iprd_adjustment"]
    assert (sb["charge_per_share"], sb["shares_denominator"], sb["iv_before"]["15"], sb["iv_after"]["25"]) == (0.175, 2e8, 5.0, 2.825), sb


def test_engine_math_replay_reproduces_an_adjusted_record():
    """test_engine_math's regression (every scored folder replayed bit for bit) applies the same helper: an
    adjusted 5.6 record reproduces, and the unadjusted replay of the same record does not."""
    import test_engine_math as TM
    n = _adjusted()
    TM.replay_record(n, "synthetic adjusted record")
    bad = copy.deepcopy(n)
    bad["iprd_adjustment"] = None
    try:
        TM.replay_record(bad, "synthetic record without the block")
    except AssertionError:
        pass
    else:
        raise AssertionError("an adjusted record replayed without its charge must not reproduce")


# ===========================================================================
# 8. Review round (2026-10-19): the IPR&D basis follows the base; replays hold the charge
# ===========================================================================
def _run_env(facts, extra=(), judgment=None, ttm=None, env=None, measure=False, price=30.0, checks=True):
    """_run with an extra environment (DCF_NO_OVERRIDES / DCF_IPRD_HOLD) and optionally --measure — the shape of
    make_score's override-impact counterfactual."""
    fx = _syn_fixture(facts, price)
    base = H.make_base(fx, with_checks(facts, judgment, checks), ttm, copy_repo_files=False)
    return H.run_engine("SYN", args=args_for(5, extra=list(extra)), base=base, fixture=fx, env=env, measure=measure)


def _ttm_ytd_facts():
    """FY2025 $20M (10-K) plus a 2026 H1 10-Q charge of $30M — the current-YTD leg of a TTM base."""
    facts = _facts(expense={2025: 20e6})
    _ytd(facts, EXPENSE, "2026-01-01", "2026-06-30", 30e6, "2026-08-05")
    return facts


def test_counterfactual_replay_holds_an_amortized_declaration_beside_a_field_override():
    """[review] An iprd_amortized declaration at a filer whose last-3-FY OE rests on a field override (FY2024 capex
    not filed, a capex_override fills it): make_score's counterfactual replays the same pin with DCF_NO_OVERRIDES=1
    and --measure. The replay must not re-validate the declaration against the no-override median (which moved) —
    it exits 0 with the pin held, treatment amortized_in_base and no one-time deduction. Validation is waived only
    in that replay: the same declaration without the override on an ordinary run is still refused."""
    facts = _facts(expense={2023: 15e6, 2025: 20e6}, capex={2024: None})
    J = {"capex_override": _o(80e6)}
    rec = _ok(_run_env(facts, judgment=J))
    assert [o["field"] for o in rec["overrides_applied"]] == ["capex"], rec["overrides_applied"]
    d = amortized_decl(rec)
    J2 = dict(J, base_override=d)
    pin = repr(d["value"])
    fin = _ok(_run_env(facts, ["--base-oe-ps", pin], J2))
    assert fin["iprd_adjustment"]["treatment"] == "amortized_in_base"
    cf = _run_env(facts, ["--base-oe-ps", pin], J2, env={"DCF_NO_OVERRIDES": "1"}, measure=True)
    assert cf["exit"] == 0 and "BAD_BASE_OVERRIDE" not in cf["stdout"], cf["stdout"][-800:]
    c = cf["numbers"]
    assert not c["overrides_applied"] and c["base_oe_per_share"] == d["value"]
    assert c["iprd_adjustment"]["treatment"] == "amortized_in_base" and E.iprd_charge_per_share(c) == 0.0
    assert "counterfactual_replay" in c["iprd_adjustment"]["amortized"], c["iprd_adjustment"]["amortized"]
    bad = _run_env(facts, ["--base-oe-ps", pin], {"base_override": d}, measure=True)
    assert bad["exit"] == 3 and "does not reproduce" in bad["stdout"], bad["stdout"][-800:]


def test_iprd_basis_follows_the_base_not_the_flag():
    """[review] A --base-oe-ps pin equal to ttm.json's ttm_oe_per_share IS the TTM base: it reads the current-YTD
    leg and divides by ttm.json's ttm_shares_diluted exactly like --ttm ($50M / 98M), so both pins value the same;
    a pin that is not ttm.json's figure stays on the FY window and the latest FY count ($20M / 100M)."""
    facts, ttm = _ttm_ytd_facts(), _ttm_doc(2.1, 98e6)
    a = _ok(_run(facts, extra=["--ttm"], ttm=ttm))
    b = _ok(_run(facts, extra=["--base-oe-ps", "2.1"], ttm=ttm))
    ba, bb = a["iprd_adjustment"], b["iprd_adjustment"]
    assert b["inputs"]["base_pin_source"] == "base_oe_ps_arg"
    for k in ("total", "shares_denominator", "shares_source", "charge_per_share", "window", "materiality"):
        assert ba[k] == bb[k], (k, ba[k], bb[k])
    assert ba["charge_per_share"] == 50e6 / 98e6
    assert a["weighted"] == b["weighted"] and a["scenarios"] == b["scenarios"]
    c = _ok(_run(facts, extra=["--base-oe-ps", "2.0"], ttm=ttm))
    bc = c["iprd_adjustment"]
    assert bc["total"] == 20e6 and bc["shares_denominator"] == 100e6 and bc["window"]["ttm_current_ytd"] is None, bc


def test_counterfactual_replay_holds_the_final_runs_charge():
    """[review] make_score's TTM counterfactual replays the no-override TTM base through --base-oe-ps, which would
    read the FY window and the FY count ($0.20/share) instead of the --ttm run's $0.5102/share. With
    DCF_IPRD_HOLD (the final run's treatment and charge) under DCF_NO_OVERRIDES + --measure, every IV is the same
    pin's unadjusted IV less exactly the HELD charge and every IRR is solved at price + the held charge; the
    computed charge is recorded beside it. A malformed hold refuses (exit 3); outside a counterfactual the hold is
    ignored."""
    facts, ttm = _ttm_ytd_facts(), _ttm_doc(2.1, 98e6)
    head = _ok(_run(facts, extra=["--ttm"], ttm=ttm))
    held = E.iprd_charge_per_share(head)
    assert held == 50e6 / 98e6
    hold = json.dumps({"treatment": head["iprd_adjustment"]["treatment"], "charge_per_share": held})
    cf = _run_env(facts, ["--base-oe-ps", "2.0"], ttm=ttm, env={"DCF_NO_OVERRIDES": "1", "DCF_IPRD_HOLD": hold}, measure=True)
    assert cf["exit"] == 0, cf["stdout"][-800:]
    c = cf["numbers"]
    blk = c["iprd_adjustment"]
    assert blk["charge_per_share"] == held and E.iprd_charge_per_share(c) == held
    assert blk["held_from_final_run"]["computed_charge_per_share"] == 20e6 / 100e6, blk["held_from_final_run"]
    ref = _ok(_run(_facts(), extra=["--base-oe-ps", "2.0"]))
    _assert_shifted(c, ref, held)
    bad = _run_env(facts, ["--base-oe-ps", "2.0"], ttm=ttm, env={"DCF_NO_OVERRIDES": "1", "DCF_IPRD_HOLD": "{\"treatment\": 1}"},
                   measure=True)
    assert bad["exit"] == 3 and "BAD_IPRD_HOLD" in bad["stdout"], bad["stdout"][-400:]
    plain = _ok(_run_env(facts, ["--base-oe-ps", "2.0"], ttm=ttm, env={"DCF_IPRD_HOLD": hold}))
    assert plain["iprd_adjustment"]["charge_per_share"] == 0.2 and "held_from_final_run" not in plain["iprd_adjustment"]


def test_counterfactual_holds_a_charge_its_own_window_does_not_see():
    """[review] A held one-time charge is applied even when the replay's window finds no acquired-IPR&D fact (the
    final run's charge sat in the TTM's current-YTD leg only)."""
    facts = _facts()
    _ytd(facts, EXPENSE, "2026-01-01", "2026-06-30", 30e6, "2026-08-05")
    ttm = _ttm_doc(2.1, 98e6)
    head = _ok(_run(facts, extra=["--ttm"], ttm=ttm))
    held = E.iprd_charge_per_share(head)
    assert held == 30e6 / 98e6
    hold = json.dumps({"treatment": "one_time_value_deduction", "charge_per_share": held})
    c = _run_env(facts, ["--base-oe-ps", "2.0"], ttm=ttm, env={"DCF_NO_OVERRIDES": "1", "DCF_IPRD_HOLD": hold}, measure=True)
    assert c["exit"] == 0, c["stdout"][-600:]
    _assert_shifted(c["numbers"], _ok(_run(_facts(), extra=["--base-oe-ps", "2.0"])), held)


def test_amortized_recurrence_is_judged_on_the_native_base():
    """[review] FY2023 and FY2025 charges of $4.2M each (4% of a $2.10 x 100M TTM base) plus $6.3M in the 2026 H1
    10-Q (3%): the --ttm run counts 7% and raises ACQUIRED_IPRD_RECURRENT. The worker's iprd_amortized declaration
    on native_base ttm_json (value 2.10 - $8.4M / 3 / 100M) must be accepted: its run reads the same TTM window and
    ttm.json's count, and judges materiality against the native base, not the lowered pin."""
    facts = _facts(expense={2023: 4.2e6, 2025: 4.2e6})
    _ytd(facts, EXPENSE, "2026-01-01", "2026-06-30", 6.3e6, "2026-08-05")
    ttm = _ttm_doc(2.1, 100e6)
    one = _ok(_run(facts, extra=["--ttm"], ttm=ttm))
    assert one["iprd_adjustment"]["recurrent"] and flags(one, "ACQUIRED_IPRD_RECURRENT")
    figs = [4.2e6, 0.0, 4.2e6]
    val = 2.1 - sum(figs) / 3 / 100e6
    d = {"basis": "iprd_amortized", "kind": "filing", "native_base": "ttm_json", "figures": figs, "shares": 100e6,
         "value": val, "source": "this run's dcf_numbers.json iprd_adjustment and ttm.json", "reason": "test: recurrent"}
    n = _ok(_run(facts, extra=["--base-oe-ps", repr(val)], judgment={"base_override": d}, ttm=ttm))
    blk = n["iprd_adjustment"]
    assert blk["treatment"] == "amortized_in_base" and blk["recurrent"], blk
    assert blk["total"] == one["iprd_adjustment"]["total"] == 14.7e6 and blk["shares_denominator"] == 100e6
    assert blk["materiality"] == blk["charge_per_share"] / 2.1 and blk["materiality_base"] == "native_base_per_share"


def test_amortized_native_base_must_be_the_ttm_base_under_stale_fy():
    """[review] native_base is the base the run would otherwise score, not a free choice: with STALE_FY firing and
    ttm.json carrying a TTM base (WORKER_SPEC step 4: score the TTM base), a median-native iprd_amortized
    declaration is refused (BAD_BASE_OVERRIDE); the ttm_json-native one is accepted."""
    facts = _facts(expense={2023: 15e6, 2025: 20e6})
    ttm = _ttm_doc(2.1, 100e6)
    one = _ok(_run(facts, extra=["--ttm"], ttm=ttm))
    assert flags(one, "STALE_FY") and one["iprd_adjustment"]["recurrent"]
    med = amortized_decl(_recurrent())
    out = _run(facts, extra=["--base-oe-ps", repr(med["value"])], judgment={"base_override": med}, ttm=ttm)
    assert out["exit"] == 3 and "native_base must be 'ttm_json'" in out["stdout"], out["stdout"][-800:]
    figs = [15e6, 0.0, 20e6]
    val = 2.1 - sum(figs) / 3 / 100e6
    d = dict(med, native_base="ttm_json", value=val)
    n = _ok(_run(facts, extra=["--base-oe-ps", repr(val)], judgment={"base_override": d}, ttm=ttm))
    assert n["iprd_adjustment"]["treatment"] == "amortized_in_base"


def test_tv_share_is_measured_on_the_adjusted_iv():
    """[review] HIGH_TV_SHARE / diagnostics.tv_share_at_15 name "IV@15%", and every IV@15 the run publishes is the
    adjusted one: the share is the terminal PV over present_value - charge (terminal_share with charge_ps), so the
    terminal PV it implies is the unadjusted run's exactly; charge 0.0 is the identity."""
    plain = _plain()
    n = _ok(_run(_facts(expense={2025: 20e6})))
    c = E.iprd_charge_per_share(n)
    assert c == 0.2
    t, t0 = n["diagnostics"]["tv_share_at_15"], plain["diagnostics"]["tv_share_at_15"]
    paths, _ = E.replay_paths(n)
    assert math.isclose(t, E.terminal_share(paths["weighted"], 0.15, n["g_terminal"], c), rel_tol=1e-12)
    assert t > t0 and math.isclose(t * n["weighted"]["iv_at_15"], t0 * plain["weighted"]["iv_at_15"], rel_tol=1e-12)
    f = paths["weighted"]
    assert E.terminal_share(f, 0.15, 0.025) == E.terminal_share(f, 0.15, 0.025, 0.0)
    assert E.terminal_share(f, 0.15, 0.025, E.present_value(f, 0.15, 0.025) * 2) is None


def test_split_restates_the_amortized_record():
    """[review] restate_split restates an amortized_in_base record's per-share figures (native and pinned base, the
    expected and declared values) and multiplies its share count, like every other per-share figure of the run."""
    import build_site as B
    n, d = _amortized_record()
    am = n["iprd_adjustment"]["amortized"]
    rec = {"numbers": copy.deepcopy(n), "row": {},
           "score": {"base_oe_per_share": d["value"],
                     "iprd_adjustment": {"amortized": {k: am[k] for k in ("native_base_per_share", "pinned_per_share", "shares",
                                                                            "figures", "mean_annual_charge")}}}}
    B.restate_split(rec, 2.0, "2:1", {})
    ra, sa = rec["numbers"]["iprd_adjustment"]["amortized"], rec["score"]["iprd_adjustment"]["amortized"]
    for k in ("native_base_per_share", "pinned_per_share", "expected_value", "declared_value"):
        assert ra[k] == am[k] / 2, (k, ra[k], am[k])
    assert ra["shares"] == am["shares"] * 2 and ra["figures"] == am["figures"] and ra["mean_annual_charge"] == am["mean_annual_charge"]
    assert (sa["native_base_per_share"], sa["pinned_per_share"], sa["shares"]) == (am["native_base_per_share"] / 2,
                                                                                  am["pinned_per_share"] / 2, am["shares"] * 2)


def _amortized_record():
    def go():
        d = amortized_decl(_recurrent())
        n = _ok(_run(_facts(expense={2023: 15e6, 2025: 20e6}), extra=["--base-oe-ps", repr(d["value"])],
                     judgment={"base_override": d}))
        return n, d
    return _cached("amort_rec", go)

# ===========================================================================
# 7. Deferred payments of an earlier deal (Andrew's 2026-10-20 ruling, delegated to the main agent, who decided)
# ===========================================================================
# A contingent milestone or other deferred payment on an acquired-IPR&D deal already charged in an earlier period
# is the SAME purchase: it is still deducted once when expensed / paid, but its period does not count toward
# ACQUIRED_IPRD_RECURRENT (which catches buying R&D as a habit — distinct deals). The link is declared per period
# in judgment.json iprd_deferred_payment and cited, so a genuine second purchase cannot be relabelled.
DEAL_SRC = ("SYN 10-K FY2023 (0000999001-24-000010) Note 5 'Asset acquisition', p. 71: up to $20.0 million of "
            "contingent development milestones payable to Test Bio's former holders, not recognized at acquisition")


# the deal's contingent consideration (the per-deal cap): generous by default so the window rules are tested apart
CT_SRC = ("SYN 10-K FY2025 (0000999001-26-000004) Note 5 'Commitments', p. 80: $1.0 billion of contingent "
          "development milestones payable to the seller, not recognized")
CT = {"value": 1e9, "source": CT_SRC}


def deferred(period="2025-12-31", amount=20e6, first="2023-12-31", source=DEAL_SRC, window="fy", deal="Test Bio",
             contingent=CT):
    return {"period": period, "window": window, "amount": amount,
            "deferred_payment_of": {"deal": deal, "first_charged_period": first, "source": source,
                                    "contingent_total": contingent}}


def _two_of_three(entries, **kw):
    facts = _facts(expense={2023: 15e6, 2025: 20e6})
    return _run(facts, judgment={"iprd_deferred_payment": entries}, **kw)


def _refused(out, needle):
    assert out["exit"] == 3, (out["exit"], out["stdout"][-1500:])
    assert "BAD_IPRD_DEFERRED_PAYMENT" in out["stdout"] and needle in out["stdout"], out["stdout"][-1500:]


def test_deferred_payment_of_an_earlier_deal_is_deducted_but_not_recurrent():
    """The 2-of-3-FY synthetic filer (FY2023 $15M, FY2025 $20M) whose FY2025 charge is declared, whole, the
    deferred milestone of the FY2023 deal: ACQUIRED_IPRD_RECURRENT does not fire (FY2025 is recorded
    recurrence_excluded: deferred_payment_of), both years are still deducted ($0.35/share, exactly as the
    undeclared run), and the base is untouched. Before the ruling the declaration was ignored and RECURRENT fired."""
    plain = _plain()
    n = _ok(_two_of_three([deferred()]))
    blk = n["iprd_adjustment"]
    assert not blk["recurrent"] and blk["fy_with_charge"] == ["2023-12-31"], blk
    assert not flags(n, "ACQUIRED_IPRD_RECURRENT")
    cf = flags(n, "ACQUIRED_IPRD_CHARGE")
    assert len(cf) == 1 and "deferred payment of Test Bio (first charged 2023-12-31) — not counted toward recurrence" in cf[0], cf
    p25 = next(p for p in blk["periods"] if p["period"] == "2025-12-31")
    assert p25["recurrence_excluded"] == "deferred_payment_of" and p25["deducted"] == 20e6, p25
    assert p25["deferred_payment_of"] == [{"deal": "Test Bio", "first_charged_period": "2023-12-31", "source": DEAL_SRC,
                                           "contingent_total": CT, "amount": 20e6,
                                           "first_charge_evidence": "window_record"}], p25
    assert blk["recurrence_excluded"] == [{"period": "2025-12-31", "window": "fy", "deal": "Test Bio",
                                           "first_charged_period": "2023-12-31", "amount": 20e6}], blk
    assert blk["total"] == 35e6 and blk["charge_per_share"] == 35e6 / SHARES
    _assert_base_untouched(n, plain)
    _assert_shifted(n, plain, 35e6 / SHARES)
    # the deduction is exactly the undeclared run's
    r = _recurrent()
    for lbl in LABELS + ["weighted"]:
        a = n["weighted"] if lbl == "weighted" else n["scenarios"][lbl]
        b = r["weighted"] if lbl == "weighted" else r["scenarios"][lbl]
        assert all(a[k] == b[k] for k in IV_KEYS) and a["irr"] == b["irr"], lbl


def test_partly_deferred_year_still_counts_toward_recurrence():
    """Only $5M of FY2025's $20M charge is declared the FY2023 deal's milestone: the rest is a new purchase, so the
    year still counts — RECURRENT fires, the declaration is recorded (whole: false) without recurrence_excluded."""
    n = _ok(_two_of_three([deferred(amount=5e6)]))
    blk = n["iprd_adjustment"]
    assert blk["recurrent"] and blk["fy_with_charge"] == ["2023-12-31", "2025-12-31"], blk
    assert flags(n, "ACQUIRED_IPRD_RECURRENT")
    p25 = next(p for p in blk["periods"] if p["period"] == "2025-12-31")
    assert [x["amount"] for x in p25["deferred_payment_of"]] == [5e6], p25
    assert "recurrence_excluded" not in p25 and blk["recurrence_excluded"] == [], blk
    assert blk["total"] == 35e6


def test_deferred_declaration_without_a_charge_at_its_first_period_is_refused():
    """first_charged_period inside the engine's window must be a period whose record shows a charge: FY2024 has
    none, and a date inside the window that is no period end (2024-06-30) names no record — both refused (exit 3,
    BAD_IPRD_DEFERRED_PAYMENT), so a second purchase cannot be relabelled as an installment of a deal that never
    charged there. A declaration on a period with no charge, or for more than the period's charge, is refused too."""
    _refused(_two_of_three([deferred(first="2024-12-31")]), "no acquired-IPR&D charge")
    _refused(_two_of_three([deferred(first="2024-06-30")]), "no acquired-IPR&D charge")
    _refused(_two_of_three([deferred(period="2024-12-31", first="2023-12-31")]), "names no acquired-IPR&D charge")
    _refused(_two_of_three([deferred(amount=25e6)]), "more than the period's charge")


def test_deferred_declaration_citing_a_later_or_the_same_period_is_refused():
    """first_charged_period must precede the declared period: FY2023 declared the deferred payment of a deal first
    charged in FY2025 (later), or of FY2023 itself, is refused."""
    _refused(_two_of_three([deferred(period="2023-12-31", amount=15e6, first="2025-12-31")]), "must precede")
    _refused(_two_of_three([deferred(period="2023-12-31", amount=15e6, first="2023-12-31")]), "must precede")


OK_SRC_2021 = "SYN 10-K FY2021 (0000999001-22-000007) Note 4: Test Bio asset acquisition, contingent milestones up to $20.0M"


def _with_2021_charge(entries):
    """The 2-of-3-FY filer plus a FY2021 acquired-IPR&D expense fact ($8M, before the engine's 2023-2025 window)."""
    facts = _facts(expense={2021: 8e6, 2023: 15e6, 2025: 20e6})
    return _run(facts, judgment={"iprd_deferred_payment": entries})


def test_pre_window_first_charge_needs_the_original_acquisition_filing():
    """A first charge before the window (FY2021: the engine has no record of it) must be cited from the original
    acquisition filing — an accession filed from that fiscal year's start through the year after its end. No
    accession at all is malformed; an accession from a later filing (2025) is refused; the FY2021 10-K (filed 2022)
    is accepted (companyfacts carries the FY2021 expense fact) and FY2025 leaves the recurrence count. A malformed
    entry (no deal) and a period declared twice for one deal are refused."""
    _refused(_with_2021_charge([deferred(first="2021-12-31", source="the FY2025 10-K mentions a milestone")]), "malformed")
    _refused(_with_2021_charge([deferred(first="2021-12-31", source="SYN 10-K FY2025 (0000999001-26-000004) Note 5")]),
             "original acquisition filing")
    n = _ok(_with_2021_charge([deferred(first="2021-12-31", source=OK_SRC_2021)]))
    blk = n["iprd_adjustment"]
    assert not blk["recurrent"] and blk["fy_with_charge"] == ["2023-12-31"], blk
    p25 = next(p for p in blk["periods"] if p["period"] == "2025-12-31")
    assert p25["deferred_payment_of"][0]["first_charge_evidence"] == "companyfacts_expense_fact", p25
    assert p25["recurrence_excluded"] == "deferred_payment_of"
    _refused(_two_of_three([deferred(deal=" ")]), "malformed")
    _refused(_two_of_three([deferred(), deferred()]), "twice")


def test_counterfactual_replay_never_refuses_a_deferred_declaration():
    """make_score's override-impact counterfactual (DCF_NO_OVERRIDES=1 --measure) reads another basis; a declaration
    checked on the final run is not refused there (recorded unapplied with its reason), like an iprd_amortized one."""
    facts = _facts(expense={2023: 15e6, 2025: 20e6})
    out = _run_env(facts, judgment={"iprd_deferred_payment": [deferred(first="2024-12-31")]},
                   env={"DCF_NO_OVERRIDES": "1"}, measure=True)
    assert out["exit"] == 0, out["stdout"][-1500:]
    blk = out["numbers"]["iprd_adjustment"]
    assert blk["recurrent"] and blk["deferred_payments_refused"], blk
    assert "no acquired-IPR&D charge" in blk["deferred_payments_refused"][0]["reason"], blk


def test_halo_record_is_unchanged_by_the_deferred_payment_rule():
    """HALO (the motivating case: $100.0M of unrecognized Surf Bio milestones in the FY2025 10-K may arrive as a
    later expensed charge): its judgment.json declares no deferred payment today, and the engine on its real
    companyfacts at the recorded price, inputs, judgment.json and ttm.json reproduces the committed
    dcf_numbers.json field for field (the run date and its month count aside) — no new key in iprd_adjustment."""
    rec = json.load(open(os.path.join(ROOT, "HALO", "dcf_numbers.json"), encoding="utf-8"))
    j = json.load(open(os.path.join(ROOT, "HALO", "judgment.json"), encoding="utf-8"))
    tt = json.load(open(os.path.join(ROOT, "HALO", "ttm.json"), encoding="utf-8"))
    assert "iprd_deferred_payment" not in j
    args = list(HALO_ARGS)
    args[args.index("--price") + 1] = repr(rec["price"])
    out = run("HALO", args, judgment=j, ttm=tt, fixture=H.load_fixture("HALO"))
    assert out["exit"] == 0, out["stdout"][-2000:]
    n = out["numbers"]
    assert n["iprd_adjustment"] == rec["iprd_adjustment"]
    assert "recurrence_excluded" not in n["iprd_adjustment"] and "deferred_payments_refused" not in n["iprd_adjustment"]
    # [Codex review r22] a fresh run also records iprd_judgment_hash, which the committed record predates
    assert "iprd_judgment_hash" not in rec and n["iprd_judgment_hash"] == E.iprd_judgment_hash(j), n.get("iprd_judgment_hash")
    # [Codex review r23] ... and ttm_inputs, what it read from HALO's ttm.json (its 122,092,000-share denominator)
    assert "ttm_inputs" not in rec and n["ttm_inputs"] == E.ttm_inputs_record(tt), n.get("ttm_inputs")
    assert n["ttm_inputs"]["ttm_shares_diluted"] == rec["iprd_adjustment"]["shares_denominator"] == 122092000
    dated = {"as_of", "price_source", "content_hash", "diagnostics", "iprd_judgment_hash", "ttm_inputs"}
    # the committed record is release 5.6.0; a fresh run carries the current release (5.7.0 since the rulings)
    assert rec["engine_release"] == "5.6.0" and n["engine_release"] == E.ENGINE_RELEASE, n["engine_release"]
    dated.add("engine_release")
    # v5.7 (L1, R1): a fresh run also records sector_model, which the committed 5.6.0 record predates — HALO is
    # modeled (Health Care; the offline harness reads no SIC), so nothing else about the run moves
    assert "sector_model" not in rec and n["sector_model"] == E.sector_model_record("Health Care", None, None, None), \
        n.get("sector_model")
    dated.add("sector_model")
    # v5.7 (L3b, M6): a fresh run also records the growth hold it ran — the default stable / 2, top level, in inputs
    # (with hold_rule) and per scenario — which the 5.6.0 record predates; without those keys nothing moves
    assert (n["moat_trend"], n["hold_years"]) == ("stable", 2) and "hold_years" not in rec
    assert [n["scenarios"][s]["hold_years"] for s in LABELS] == [2] * 5
    dated |= {"moat_trend", "hold_years"}
    n = dict(n, inputs={k: v for k, v in n["inputs"].items() if k not in ("moat_trend", "hold_years", "hold_rule")},
             scenarios={s: {k: v for k, v in x.items() if k != "hold_years"} for s, x in n["scenarios"].items()})
    assert [k for k in set(n) | set(rec) if k not in dated and n.get(k) != rec.get(k)] == []
    assert ({k: v for k, v in n["diagnostics"].items() if k != "months_since_fy_end"}
            == {k: v for k, v in rec["diagnostics"].items() if k != "months_since_fy_end"})


# --- Codex review of the deferred-payment rule (fixes amended into the follow-up commit) -------------------------
def _src(yy, what="Note 5: contingent development milestones payable to the seller, not recognized at acquisition"):
    return f"SYN filing (0000999001-{yy:02d}-000010) {what}"


def _three_years(entries):
    """FY2023 $50M, FY2024 $200M, FY2025 $300M — three charges in three years."""
    facts = _facts(expense={2023: 50e6, 2024: 200e6, 2025: 300e6})
    return _run(facts, judgment={"iprd_deferred_payment": entries})


def test_deferred_a_deals_first_charge_cannot_itself_be_declared_an_installment():
    """[Codex review, finding 1] FY2024 declared, whole, deal A's installment (first charged FY2023) AND named as
    deal B's first charge (FY2025 declared B's installment): FY2024 cannot be both, so a genuine second purchase
    would have been relabelled and RECURRENT silenced. Refused (exit 3). The same deal declared first charged on two
    dates (in any letter case) is refused too. The legitimate shape — FY2024 only PARTLY deal A's milestone, the
    rest deal B's purchase, and FY2025 wholly deal B's milestone — is accepted: FY2025 leaves the count, FY2023 and
    FY2024 stay, RECURRENT still fires."""
    a24 = deferred(period="2024-12-31", amount=200e6, first="2023-12-31", deal="Deal A", source=_src(24))
    b25 = deferred(period="2025-12-31", amount=300e6, first="2024-12-31", deal="Deal B", source=_src(25))
    _refused(_three_years([a24, b25]), "would be a second purchase in that period")
    _refused(_three_years([a24, b25]), "names it its first charge")
    a25 = deferred(period="2025-12-31", amount=300e6, first="2024-12-31", deal=" deal  a", source=_src(25))
    _refused(_three_years([a24, a25]), "one deal has one first charge")
    n = _ok(_three_years([dict(a24, amount=50e6), b25]))
    blk = n["iprd_adjustment"]
    assert blk["fy_with_charge"] == ["2023-12-31", "2024-12-31"] and blk["recurrent"], blk
    assert [x["period"] for x in blk["recurrence_excluded"]] == ["2025-12-31"], blk
    assert blk["total"] == 550e6


def test_deferred_source_must_be_the_original_filing_inside_the_window_too():
    """[Codex review, findings 1 and 3] An in-window first charge (FY2023) is also checked against the original
    acquisition filing's years (2023..2024), so an entry accepted today does not start failing once FY2023 rolls out
    of the window: a 2021 accession (before the deal) and a 2026 one (a later 10-K) are refused; 2023 and 2024 pass."""
    for yy in (21, 26):
        _refused(_two_of_three([deferred(source=_src(yy))]), "original acquisition filing")
    for yy in (23, 24):
        _ok(_two_of_three([deferred(source=_src(yy))]))


def test_pre_window_first_charge_must_be_an_expense_fact_in_companyfacts():
    """[Codex review, finding 2] A first charge before the window is checked against companyfacts: FY2019 (the
    synthetic filer's facts start 2019-01-01, so companyfacts covers it) carries no acquired-IPR&D expense fact, so
    citing any 2020 accession does not prove a charge that never happened — refused. A first charge before
    companyfacts starts (FY2017, pre-XBRL in effect) rests on the cited original filing alone and is recorded so
    (first_charge_evidence citation_only_before_companyfacts)."""
    _refused(_two_of_three([deferred(first="2019-12-31", source="9999999999-20-000001 p1")]), "companyfacts covers it")
    n = _ok(_two_of_three([deferred(first="2017-12-31", source=_src(18))]))
    p25 = next(p for p in n["iprd_adjustment"]["periods"] if p["period"] == "2025-12-31")
    assert p25["deferred_payment_of"][0]["first_charge_evidence"] == "citation_only_before_companyfacts", p25
    assert p25["recurrence_excluded"] == "deferred_payment_of"


def _rec(period, amount, window="fy"):
    return {"period": period, "window": window, "amount": amount, "expense": amount, "deducted": amount}


def _fy_fact(start, end, val):
    return {"start": start, "end": end, "val": val, "form": "10-K", "fp": "FY", "filed": end}


def test_original_filing_years_follow_the_fiscal_year_not_the_calendar():
    """[Codex review, findings 3 and 8] A January FY end (2022-01-29): the deal closed and was first expensed in a
    10-Q filed in calendar 2021 — that accession (-21-) is the original filing and is accepted. A June FY (first
    charge FY2024, 2024-06-30): the September 2023 8-K / 10-Q (-23-) is accepted. A -20- accession is still too early
    for the January filer. The flag names the first charge by its date, not a calendar-year 'FY' label."""
    win = ["2023-01-28", "2024-02-03", "2025-02-01"]
    facts = {"facts": {"us-gaap": {EXPENSE: {"units": {"USD": [_fy_fact("2021-01-31", "2022-01-29", 5e6)]}}}}}
    for yy, ok in ((21, True), (22, True), (23, True), (20, False)):
        iprd = {"periods": [_rec("2025-02-01", 20e6)]}
        ref, unused = E.iprd_apply_deferred(iprd, [deferred(period="2025-02-01", first="2022-01-29", source=_src(yy))],
                                            win, facts)
        assert (not ref) == ok and unused == [], (yy, ref)
        assert (iprd["periods"][0].get("recurrence_excluded") == "deferred_payment_of") == ok, (yy, iprd)
    win = ["2025-06-30", "2026-06-30", "2027-06-30"]
    facts = {"facts": {"us-gaap": {EXPENSE: {"units": {"USD": [_fy_fact("2023-07-01", "2024-06-30", 5e6)]}}}}}
    iprd = {"periods": [_rec("2027-06-30", 20e6)]}
    ref, _ = E.iprd_apply_deferred(iprd, [deferred(period="2027-06-30", first="2024-06-30", source=_src(23))], win, facts)
    assert ref == [] and iprd["periods"][0]["recurrence_excluded"] == "deferred_payment_of", ref
    iprd.update(total=20e6, treatment=E.IPRD_TREATMENT_ONE_TIME, charge_per_share=0.2, shares_denominator=100e6,
                shares_source="test", material=True, materiality=0.5, recurrent=False, fy_with_charge=[])
    iprd["periods"][0].update(amount_basis="expense", tag_used=EXPENSE)
    txt = " ".join(E.iprd_flags(iprd))
    assert "first charged 2024-06-30" in txt and "FY2024)" not in txt, txt


def test_ytd_declaration_is_refused_it_never_counts_toward_recurrence():
    """[Codex review, findings 4, 5 and 6] The recurrence count reads FY periods only, so a current-YTD declaration
    could only mislabel a period that never counted ("excluded from" / "still counts toward" the recurrence count)
    and, valid on a --ttm run only, would make every non-TTM run (WORKER_SPEC step 2's preliminary run) exit 3.
    Window "ttm_current_ytd" is malformed: declare the charge once it lands in an FY."""
    assert not E.iprd_deferred_entry_ok(deferred(period="2026-06-30", window="ttm_current_ytd", first="2025-12-31"))
    iprd = {"periods": [_rec("2025-12-31", 20e6), _rec("2026-06-30", 30e6, window="ttm_current_ytd")]}
    ref, _ = E.iprd_apply_deferred(iprd, [deferred(period="2026-06-30", window="ttm_current_ytd", amount=30e6,
                                                   first="2025-12-31", source=_src(26))],
                                   ["2023-12-31", "2024-12-31", "2025-12-31"], None)
    assert len(ref) == 1 and "malformed" in ref[0]["reason"] and "lands in an FY" in ref[0]["reason"], ref
    assert "recurrence_excluded" not in iprd["periods"][1] and "deferred_payment_of" not in iprd["periods"][1]
    out = _run(_ttm_ytd_facts(), extra=["--ttm"], ttm=_ttm_doc(2.1, 98e6),
               judgment={"iprd_deferred_payment": [deferred(period="2026-06-30", window="ttm_current_ytd", amount=30e6,
                                                            first="2025-12-31", source=_src(26))]})
    _refused(out, "lands in an FY")


def test_entry_whose_period_rolled_out_of_the_window_is_kept_not_applied_not_refused():
    """[Codex review, finding 5; Codex review r4, #4322408940] An entry carried over from an earlier scoring whose
    period (FY2022) is now older than the engine's window is neither applied nor refused: the run exits 0 and lists
    it in deferred_payments_rolled_out; it stays in judgment.json (it still counts toward its deal's lifetime
    contingent_total cap). The in-window entry beside it still applies. [Codex review r7] Its first charge (FY2021)
    is an expense fact companyfacts carries: a rolled-out entry passes the same checks as an in-window one."""
    old = deferred(period="2022-12-31", amount=5e6, first="2021-12-31", source=OK_SRC_2021, deal="Old Bio")
    n = _ok(_with_2021_charge([deferred(), old]))
    blk = n["iprd_adjustment"]
    assert blk["deferred_payments_rolled_out"] == [old], blk
    assert "deferred_payments_refused" not in blk and [x["period"] for x in blk["recurrence_excluded"]] == ["2025-12-31"]
    ref, unused = E.iprd_apply_deferred({"periods": [_rec("2025-12-31", 20e6)]}, [old],
                                        ["2023-12-31", "2024-12-31", "2025-12-31"], None)
    assert ref == [] and unused == [old]


def _rolled_only_case():
    """[Codex review r5 of PR #47, #4322641225] The filer expensed Old Bio's first charge in FY2021 and paid a $60.0M
    deferred milestone in FY2022; the FY2023-25 window holds no acquired-IPR&D fact at all. The FY2022 entry has
    rolled out of the window and stays declared (its payment counts toward the deal's $100.0M contingent_total)."""
    cap = {"value": 100e6, "source": CT_SRC}
    old = deferred(period="2022-12-31", amount=60e6, first="2021-12-31", source=OK_SRC_2021, deal="Old Bio",
                   contingent=cap)
    new = deferred(period="2025-12-31", amount=60e6, first="2021-12-31", source=OK_SRC_2021, deal="Old Bio",
                   contingent=cap)
    return _facts(expense={2021: 8e6, 2022: 60e6}), old, new


def test_rolled_out_entry_is_recorded_when_the_window_has_no_iprd_charge():
    """[Codex review r5 of PR #47, #4322641225] iprd_detect finds nothing in the window, so the run had no
    iprd_adjustment block and the rolled-out list was dropped (null block): make_score then refused the kept entry as
    "did not apply", and deleting it — the only way to score — freed the deal's lifetime contingent_total cap. The
    run now records a minimal block (treatment none, total and charge 0, no periods) carrying
    deferred_payments_rolled_out, and nothing else moves: IVs, IRRs, tier and flags equal the undeclared run's, whose
    block stays null. A replay (DCF_NO_OVERRIDES + DCF_IPRD_HOLD) records the list too, held charge or none."""
    facts, old, new = _rolled_only_case()
    plain = _ok(_run(facts))
    assert plain["iprd_adjustment"] is None
    n = _ok(_run(facts, judgment={"iprd_deferred_payment": [old]}))
    blk = n["iprd_adjustment"]
    assert isinstance(blk, dict), blk
    assert blk["deferred_payments_rolled_out"] == [old], blk
    assert (blk["treatment"] == "none" and blk["total"] == 0.0 and blk["charge_per_share"] == 0.0
            and blk["periods"] == [] and blk["ignored_cash_only"] == [] and blk["recurrence_excluded"] == []
            and blk["deferred_payments_only"] is True), blk
    assert E.iprd_charge_per_share(n) == 0.0 and E.iprd_flags(blk) == [] and not flags(n, "ACQUIRED_IPRD")
    # [Codex review r22] the declaration is a judgment input: iprd_judgment_hash differs with it, nothing else
    assert n["iprd_judgment_hash"] != plain["iprd_judgment_hash"]
    assert {k: v for k, v in _strip(n).items() if k not in ("iprd_adjustment", "iprd_judgment_hash")} == \
        {k: v for k, v in _strip(plain).items() if k not in ("iprd_adjustment", "iprd_judgment_hash")}
    # reprice.py and build_site.py read the minimal block as no charge: the same live figures, table and hurdles
    import reprice as R
    import build_site as B
    lv, lp = R.reprice(n, 25.0), R.reprice(plain, 25.0)
    assert lv == lp and lv["iprd_charge_per_share"] == 0.0, (lv, lp)
    paths, _ = E.replay_paths(n)
    s = {"price": n["price"]}
    assert B.scenario_sensitivity(n, s, paths, None) == B.scenario_sensitivity(plain, s, paths, None)
    assert B.hurdle_prices(n, s, paths) == B.hurdle_prices(plain, s, paths) and B.iprd_charge(n) == 0.0
    rec = {"numbers": copy.deepcopy(n), "row": {}, "score": {}}
    B.restate_split(rec, 2.0, "2:1", {})
    assert rec["numbers"]["iprd_adjustment"]["deferred_payments_rolled_out"] == [old], rec["numbers"]["iprd_adjustment"]
    # kept declared, the entry still bounds the deal: a later $60.0M Old Bio milestone takes it past $100.0M
    _refused(_run(_facts(expense={2021: 8e6, 2022: 60e6, 2025: 60e6}), judgment={"iprd_deferred_payment": [new, old]}),
             "contingent_total")
    # the override-impact replay: with no hold, and holding a one-time charge its own window does not see
    for hold in ({"treatment": "none", "charge_per_share": 0.0},
                 {"treatment": "one_time_value_deduction", "charge_per_share": 0.5}):
        c = _run_env(facts, judgment={"iprd_deferred_payment": [old]},
                     env={"DCF_NO_OVERRIDES": "1", "DCF_IPRD_HOLD": json.dumps(hold)}, measure=True)
        assert c["exit"] == 0, c["stdout"][-600:]
        cb = c["numbers"]["iprd_adjustment"]
        assert cb["deferred_payments_rolled_out"] == [old] and cb["recurrence_excluded"] == [], cb
        assert E.iprd_charge_per_share(c["numbers"]) == hold["charge_per_share"], cb


def test_a_period_made_of_two_earlier_deals_milestones_can_be_declared_whole():
    """[Codex review, finding 7] FY2025's $20M = a $12M Test Bio milestone (first charged FY2023, in the window) +
    an $8M Other Bio milestone (first charged FY2021, before it; companyfacts carries the FY2021 charge). Both are
    declared: their sum is the whole charge, so FY2025 leaves the recurrence count and RECURRENT does not fire
    (before the fix the second entry was refused as 'twice'). Declarations summing past the charge are refused, and
    a deal still declares a period once."""
    tb = deferred(amount=12e6)
    ob = deferred(amount=8e6, deal="Other Bio", first="2021-12-31", source=OK_SRC_2021)
    n = _ok(_with_2021_charge([tb, ob]))
    blk = n["iprd_adjustment"]
    assert not blk["recurrent"] and blk["fy_with_charge"] == ["2023-12-31"], blk
    p25 = next(p for p in blk["periods"] if p["period"] == "2025-12-31")
    assert p25["recurrence_excluded"] == "deferred_payment_of"
    assert [(x["deal"], x["amount"], x["first_charge_evidence"]) for x in p25["deferred_payment_of"]] == [
        ("Test Bio", 12e6, "window_record"), ("Other Bio", 8e6, "companyfacts_expense_fact")], p25
    assert [(x["deal"], x["amount"]) for x in blk["recurrence_excluded"]] == [("Test Bio", 12e6), ("Other Bio", 8e6)]
    assert blk["total"] == 35e6
    cf = flags(n, "ACQUIRED_IPRD_CHARGE")
    assert ("deferred payment of Test Bio (first charged 2023-12-31) and Other Bio (first charged 2021-12-31) — not "
            "counted toward recurrence") in cf[0], cf
    # one deal only part of it: the year still counts
    p = _ok(_with_2021_charge([tb]))["iprd_adjustment"]
    assert p["recurrent"] and p["recurrence_excluded"] == [], p
    _refused(_with_2021_charge([tb, dict(ob, amount=9e6)]), "sum to 21,000,000, more than the period's charge")
    _refused(_with_2021_charge([tb, dict(tb, amount=8e6)]), "twice")



# --- the per-deal cap (the main agent's decision on the review's open item, delegated by Andrew 2026-10-20) --------
def _deal_a(period, amount, contingent):
    return deferred(period=period, amount=amount, first="2023-12-31", deal="Deal A", source=_src(24),
                    contingent=contingent)


def test_deferred_declaration_needs_the_deals_contingent_total():
    """Each deferred_payment_of carries contingent_total {value (USD, > 0), source (accession + section showing the
    unrecognized milestones / deferred consideration)}: without it, with a non-positive value or with a source
    carrying no accession, the entry is malformed and refused (exit 3)."""
    d = deferred()
    for bad in (None, {"source": CT_SRC}, {"value": 0, "source": CT_SRC}, {"value": True, "source": CT_SRC},
                {"value": float("nan"), "source": CT_SRC}, {"value": 20e6, "source": "Note 5: $20.0M milestones"},
                {"value": 20e6, "source": "0000999001-26-000004"}, 20e6):
        dd = dict(d["deferred_payment_of"], contingent_total=bad)
        if bad is None:
            del dd["contingent_total"]
        e = dict(d, deferred_payment_of=dd)
        assert not E.iprd_deferred_entry_ok(e), bad
    _refused(_two_of_three([dict(d, deferred_payment_of={k: v for k, v in d["deferred_payment_of"].items()
                                                         if k != "contingent_total"})]), "contingent_total")


def test_deferred_amounts_for_one_deal_are_capped_by_its_contingent_total():
    """One deal's declared deferred amounts, summed across every entry of the run, may not exceed the deal's
    contingent_total: FY2025's $20M declared a Test Bio milestone against a $15M contingent_total is refused; Deal A
    paying $30M (FY2024) + $40M (FY2025) against $60M is refused (both entries), against $70M accepted (the sum
    equals the cap) and the record carries the cap on each item. A rolled-out entry still counts toward its deal's
    sum. The deduction never changes."""
    _refused(_two_of_three([deferred(contingent={"value": 15e6, "source": CT_SRC})]),
             "more than its contingent_total")
    cap60, cap70 = {"value": 60e6, "source": CT_SRC}, {"value": 70e6, "source": CT_SRC}
    out = _three_years([_deal_a("2024-12-31", 30e6, cap60), _deal_a("2025-12-31", 40e6, cap60)])
    _refused(out, "more than its contingent_total")
    assert out["stdout"].count("more than its contingent_total") >= 2, out["stdout"][-1500:]
    n = _ok(_three_years([_deal_a("2024-12-31", 30e6, cap70), _deal_a("2025-12-31", 40e6, cap70)]))
    blk = n["iprd_adjustment"]
    assert blk["total"] == 550e6 and blk["recurrent"], blk
    for p in ("2024-12-31", "2025-12-31"):
        rec = next(x for x in blk["periods"] if x["period"] == p)
        assert [x["contingent_total"] for x in rec["deferred_payment_of"]] == [cap70], rec
    # a rolled-out entry of the same deal is unused, not applied, but its amount still counts toward the cap
    old = deferred(period="2022-12-31", amount=5e6, first="2021-12-31", source=OK_SRC_2021, deal="Old Bio",
                   contingent={"value": 22e6, "source": CT_SRC})
    new = deferred(amount=20e6, first="2021-12-31", source=OK_SRC_2021, deal="old bio",
                   contingent={"value": 22e6, "source": CT_SRC})
    facts = {"facts": {"us-gaap": {EXPENSE: {"units": {"USD": [_fy_fact("2021-01-01", "2021-12-31", 8e6)]}}}}}
    iprd = {"periods": [_rec("2025-12-31", 20e6)]}
    ref, unused = E.iprd_apply_deferred(iprd, [old, new], ["2023-12-31", "2024-12-31", "2025-12-31"], facts)
    assert [r["entry"] for r in ref] == [old, new] and unused == [], (ref, unused)
    assert all("more than its contingent_total" in r["reason"] for r in ref), ref
    assert "deferred_payment_of" not in iprd["periods"][0]
    ref, unused = E.iprd_apply_deferred(iprd, [old, dict(new, amount=17e6)], ["2023-12-31", "2024-12-31", "2025-12-31"],
                                        facts)
    assert ref == [] and unused == [old] and "recurrence_excluded" not in iprd["periods"][0], (ref, iprd)


def test_one_deal_declares_one_contingent_total():
    """A deal's contingent_total is declared once, consistently: two entries for Deal A carrying different values, or
    the same value cited from different sources, are refused (every entry of that deal); identical declarations
    (the source compared without extra spacing) pass."""
    a = {"value": 70e6, "source": CT_SRC}
    for b in ({"value": 80e6, "source": CT_SRC}, {"value": 70e6, "source": _src(26, "Note 9: $70.0M milestones")}):
        out = _three_years([_deal_a("2024-12-31", 30e6, a), _deal_a("2025-12-31", 40e6, b)])
        _refused(out, "one deal has one contingent_total")
    _ok(_three_years([_deal_a("2024-12-31", 30e6, a),
                      _deal_a("2025-12-31", 40e6, {"value": 70e6, "source": "  " + CT_SRC.replace(" ", "  ")})]))



# ===========================================================================
# Codex review round 1 of PR #47 (2026-10-19)
# ===========================================================================
def test_usd_cash_fact_is_the_amount_when_the_expense_has_no_fx_rate():
    """[Codex review r1, #4321488157] The expense tag is the DETECTOR and the cash outflow the AMOUNT (cash
    preferred, README 5.6 entry): an expense filed only in a currency the FX pass holds no rate for (EUR at a USD
    filer: rates_by_ccy is {}) still detects the charge by its native sign, and the USD cash fact for the same period
    is the amount ($200M on 100M shares = $2.00/share). Before the fix the period was excluded non_usd_no_rate before
    the cash fact was read: the real $200M outflow was deducted as $0, with no flag. With no usable cash fact the
    period stays non_usd_no_rate; a native expense <= 0 deducts nothing whatever the cash tag says."""
    fy3 = ["2023-12-31", "2024-12-31", "2025-12-31"]

    def eur_expense(native, cash=200e6):
        f = _syn_facts()
        _syn_put(f, EXPENSE, "EUR", _ctx("2025-01-01", "2025-12-31", native, filed="2026-02-20"))
        if cash is not None:
            _fy(f, CASH, 2025, cash)
        return f

    facts = eur_expense(180e6)
    out = E.iprd_detect(facts, fy3, fx_rates={})
    rec = [p for p in out["periods"] if p["period"] == "2025-12-31"][0]
    assert (rec["excluded"], rec["amount_basis"], rec["tag_used"], rec["amount"], rec["deducted"]) == (
        None, "cash_outflow", CASH, 200e6, 200e6), rec
    assert rec["expense"] is None and rec["expense_unit"] == "EUR" and rec["expense_native"] == 180e6, rec
    assert "no FX rate" in rec["expense_fx_note"], rec
    rec = [p for p in E.iprd_detect(eur_expense(180e6, cash=None), fy3, fx_rates={})["periods"]][0]
    assert rec["excluded"] == "non_usd_no_rate" and rec["deducted"] == 0.0, rec
    for native in (0.0, -5e6):
        rec = [p for p in E.iprd_detect(eur_expense(native), fy3, fx_rates={})["periods"]][0]
        assert rec["deducted"] == 0.0, (native, rec)
    # the record helper keeps its 5-tuple call shape (no native value: non_usd_no_rate, as before)
    rec = E.iprd_period_record("2025-12-31", "fy", (EXPENSE, None, "EUR", None, "x"), (200e6, "USD", None, "x"))
    assert rec["excluded"] == "non_usd_no_rate" and rec["deducted"] == 0.0, rec
    # end to end: the engine deducts the cash outflow, exactly as it does when the expense is filed in USD
    n = _ok(_run(facts, checks=False))
    usd = _facts(expense={2025: 180e6}, cash={2025: 200e6})
    m = _ok(_run(usd, checks=False))
    for x in (n, m):
        b = x["iprd_adjustment"]
        assert b["treatment"] == "one_time_value_deduction" and b["total"] == 200e6 and b["charge_per_share"] == 2.0, b
    assert n["weighted"]["iv_at_15"] == m["weighted"]["iv_at_15"] and n["implied_irr_weighted"] == m["implied_irr_weighted"]


# --- Codex review round 2 of PR #47 -------------------------------------------------------------------------------
def test_pre_2000_original_filing_accession_is_read_in_its_own_century():
    """[Codex review r2, #4321940593] EDGAR accessions carry a two-digit year from 1993: a deal first charged in
    FY1999 (or a June FY ending 2000-06-30, whose first-quarter 10-Q was filed in 1999) cites a -99- accession, which
    the engine read as 2099 and refused (BAD_IPRD_DEFERRED_PAYMENT, so the company could not be scored). The
    original filing's years are 1999..2000 for FY1999 and 1999..2001 for June FY2000: -99- and -00- pass, a -98- or
    a -02- one does not, and FY1998 (only -98- / -99- accessions qualify) is no longer unscoreable.
    [Codex review r18, #4332318439] With no annual context filed for the first charged fiscal year (a pre-XBRL
    charge: companyfacts cannot say when that year started) the start is the end less 380 days, the longest fiscal
    year read, so a 53-week year is never cut short: FY1999 (a December end) then also admits a -98- accession, and
    FY1998 a -97- one; a -97- one for FY1999 or a -96- one for FY1998 is still refused."""
    win = ["2023-12-31", "2024-12-31", "2025-12-31"]
    for first, yy, ok in (("1999-12-31", 99, True), ("1999-12-31", 0, True), ("1999-12-31", 98, True),
                          ("1999-12-31", 97, False), ("1999-12-31", 1, False), ("2000-06-30", 99, True),
                          ("2000-06-30", 1, True), ("2000-06-30", 2, False), ("1998-12-31", 98, True),
                          ("1998-12-31", 99, True), ("1998-12-31", 97, True), ("1998-12-31", 96, False),
                          ("2005-12-31", 6, True), ("2005-12-31", 99, False)):
        iprd = {"periods": [_rec("2025-12-31", 20e6)]}
        ref, unused = E.iprd_apply_deferred(iprd, [deferred(first=first, source=_src(yy))], win, None)
        assert (not ref) == ok and unused == [], (first, yy, ref)
    assert [E.iprd_accession_year(y) for y in (93, 99, 0, 26, 92)] == [1993, 1999, 2000, 2026, 2092]
    # end to end: the synthetic filer's companyfacts start in 2019, so the FY1999 first charge rests on the citation
    n = _ok(_two_of_three([deferred(first="1999-12-31", source=_src(99))]))
    p25 = next(p for p in n["iprd_adjustment"]["periods"] if p["period"] == "2025-12-31")
    assert p25["deferred_payment_of"][0]["first_charge_evidence"] == "citation_only_before_companyfacts", p25
    assert p25["recurrence_excluded"] == "deferred_payment_of"


def _share_count_unverified_record():
    """The adjusted synthetic record relabelled as the engine writes a share-scale rescue with no power-of-ten factor:
    treatment not_applied_share_count_unverified, no denominator, charge 0.0 (nothing deducted)."""
    n = copy.deepcopy(_adjusted())
    blk = n["iprd_adjustment"]
    blk.update(treatment="not_applied_share_count_unverified", shares_denominator=None, shares_source=None,
               charge_per_share=0.0)
    return n


def test_reprice_withholds_a_record_whose_charge_was_deducted_by_hand():
    """[Codex review r2, #4321940598] Treatment not_applied_share_count_unverified publishes only through the main
    agent's tier_override carrying a hand deduction reprice cannot replay: before, reprice solved every live IRR on
    the UNADJUSTED paths (charge 0) and, once the unadjusted numbers tier moved, superseded the override and
    published an unadjusted live tier (A -> S at a lower close). Now the record is skipped like an unverifiable
    per-share basis: Skip with the reason, and reprice_folder removes a stale live.json."""
    import reprice as R
    n = _share_count_unverified_record()
    for fn in (lambda: R.check_eligible(n), lambda: R.reprice(n, 25.0)):
        try:
            fn()
            raise AssertionError("not withheld: an unadjusted live tier would be published")
        except R.Skip as e:
            assert "not_applied_share_count_unverified" in str(e) and "hand" in str(e), str(e)
    # the one-time record still reprices
    assert R.reprice(_adjusted(), 25.0)["iprd_charge_per_share"] == 0.35
    import tempfile
    import shutil
    tmp = tempfile.mkdtemp(prefix="reprice_iprd_")
    saved = R.BASE
    try:
        os.makedirs(os.path.join(tmp, "TST"))
        with open(os.path.join(tmp, "TST", "dcf_numbers.json"), "w", encoding="utf-8") as f:
            json.dump(dict(n, ticker="TST"), f)
        with open(os.path.join(tmp, "TST", "live.json"), "w", encoding="utf-8") as f:
            json.dump({"price": 25.0, "irr_weighted": 0.3}, f)
        R.BASE = tmp
        try:
            R.reprice_folder("TST")
            raise AssertionError("reprice_folder wrote live.json")
        except R.Skip as e:
            assert "not_applied_share_count_unverified" in str(e), str(e)
        assert not os.path.exists(os.path.join(tmp, "TST", "live.json")), "the stale live.json stayed"
    finally:
        R.BASE = saved
        shutil.rmtree(tmp, ignore_errors=True)


def _score_of(n):
    """The identity fields make_score copies from engine record n into score.json (implied_irr to 4 dp, iv_at_15 to
    2 dp) — a score.json built from THIS run (reprice.score_matches_run / build_site.score_from_run). [Codex review
    r13] It carries the run's content_hash as dcf_content_hash, as make_score writes it: a release-5.6.0 score.json
    without it is another run's."""
    return {"ticker": n.get("ticker"), "analysis_date": n.get("as_of"), "tier_by_numbers": n.get("tier_by_numbers"),
            "implied_irr": round(n["implied_irr_weighted"], 4), "price": n.get("price"),
            "base_oe_per_share": n.get("base_oe_per_share"), "iv_at_15": round(n["iv_at_15"], 2),
            "engine_version": n.get("engine_version"), "engine_release": n.get("engine_release"),
            "dcf_content_hash": n.get("content_hash")}


def test_build_site_withholds_live_figures_for_a_hand_deducted_charge():
    """[Codex review r2, #4321940598] build_site: a not_applied_share_count_unverified record never shows live
    figures — a live.json on file (an older reprice) is withheld with reason iprd_share_count_unverified and a note,
    and with no live.json the record still says why it carries none, so the page shows the scored figures (the
    main agent's tier_override) as current; a one-time record's live.json is shown as before."""
    import build_site as B
    import reprice as R
    n = _share_count_unverified_record()
    lv = {"price": 25.0, "irr_weighted": 0.3, "price_date": "2026-10-20", "scored_date": "2026-10-19"}
    sc = {"analysis_date": "2026-10-19"}
    for live in (lv, None):
        shown, w = B.live_shown({"score": sc, "numbers": n, "live": live})
        assert shown is None and w["reason"] == "iprd_share_count_unverified", w
        assert w["scored_date"] == "2026-10-19" and w["price"] == (25.0 if live else None), w
        assert "acquired-IPR&D" in w["note"] and "tier_override" in w["note"], w["note"]
    # a one-time record's live.json beside its own run's score is shown ([Codex review r11] the score must be this run's)
    adj = _adjusted()
    # [Codex review r29 of PR #47] live.json computed against that score (reprice records which one)
    own = R.reprice(adj, 25.0, adj["as_of"], _score_of(adj), today=adj["as_of"])
    assert B.live_shown({"score": _score_of(adj), "numbers": adj, "live": own}) == (own, None)

# --- Codex review round 3 of PR #47 -------------------------------------------------------------------------------
def _eur_expense(native, start="2025-01-01", end="2025-12-31", form="10-K", filed="2026-02-20"):
    f = _syn_facts()
    _syn_put(f, EXPENSE, "EUR", {"start": start, "end": end, "val": native, "form": form, "fp": "FY" if form == "10-K" else "Q2",
                                 "fy": int(end[:4]), "filed": filed, "accn": f"0000999001-{filed}"})
    return f


def test_unconvertible_expense_with_no_usable_cash_is_gated_not_deducted_as_zero():
    """[Codex review r3, #4322176027] A positive acquired-IPR&D expense filed only in a currency the FX pass holds no
    rate for (EUR at a USD filer: rates_by_ccy holds only the core series' currencies and dates), with no usable cash
    fact for the period, was recorded excluded non_usd_no_rate with $0 deducted, treatment "none" and NO flag — the
    unadjusted tier went out and make_score accepted it. The charge is still detected by its native sign, so the run
    now raises ACQUIRED_IPRD_UNCONVERTED (naming the period and the native amount; make_score refuses it,
    NEEDS_MAIN_AGENT: currency) and records treatment non_usd_no_rate when nothing else is deducted — like an expense
    awaiting its cash-flow check. The same for the current-YTD 10-Q leg (the FX pass asks for FY-end rates only). A
    native expense <= 0 expensed nothing: no flag."""
    plain = _plain()
    n = _ok(_run(_eur_expense(300e6), checks=False))
    blk = n["iprd_adjustment"]
    rec = [p for p in blk["periods"] if p["period"] == "2025-12-31"][0]
    assert rec["excluded"] == "non_usd_no_rate" and rec["deducted"] == 0.0 and rec["expense_native"] == 300e6, rec
    assert blk["total"] == 0.0 and blk["treatment"] == "non_usd_no_rate", blk
    fl = flags(n, "ACQUIRED_IPRD_UNCONVERTED")
    assert len(fl) == 1 and "FY2025 300,000,000 EUR" in fl[0] and "NEEDS_MAIN_AGENT: currency" in fl[0], fl
    assert n["weighted"] == plain["weighted"]   # nothing deducted: the gate, not the figures, carries it
    for native in (0.0, -5e6):
        m = _ok(_run(_eur_expense(native), checks=False))
        assert not flags(m, "ACQUIRED_IPRD_UNCONVERTED"), (native, m["iprd_adjustment"])
        assert m["iprd_adjustment"]["treatment"] == "none", m["iprd_adjustment"]
    # the YTD leg: a EUR 10-Q fact with no rate and no cash fact
    f = _eur_expense(150e6, start="2026-01-01", end="2026-06-30", form="10-Q", filed="2026-08-05")
    _fy(f, EXPENSE, 2025, 20e6)
    out = E.iprd_detect(f, ["2023-12-31", "2024-12-31", "2025-12-31"], ytd=("2026-01-01", "2026-06-30"), fx_rates={},
                        checks=auto_checks(f))
    y = [p for p in out["periods"] if p["window"] == "ttm_current_ytd"][0]
    assert y["excluded"] == "non_usd_no_rate" and y["expense_native"] == 150e6, y
    out.update(total=20e6, treatment="one_time_value_deduction", charge_per_share=0.2, shares_denominator=100e6,
               shares_source="ttm.json ttm_shares_diluted", material=True, materiality=0.1, recurrent=False,
               fy_with_charge=["2025-12-31"])
    fl = [x for x in E.iprd_flags(out) if x.startswith("ACQUIRED_IPRD_UNCONVERTED")]
    assert len(fl) == 1 and "YTD 2026-01-01..2026-06-30 150,000,000 EUR" in fl[0], fl


PRE_SRC = ("SYN 10-K FY2022 (0000999001-23-000005) Note 4 'Asset acquisition', p. 64: Old Bio acquired IPR&D $40.0 "
           "million expensed, $10.0 million paid at closing, $30.0 million of deferred consideration payable in 2024")
PRE_CT = {"value": 30e6, "source": "SYN 10-K FY2022 (0000999001-23-000005) Note 4, p. 64: $30.0 million deferred consideration"}


def _pre_window(entries=None, cash24=30e6):
    """FY2022 (before the engine's FY2023-25 window): $40M expensed, $10M paid; the $30M deferred remainder is paid in
    FY2024 on the cash tag alone."""
    facts = _facts(expense={2022: 40e6}, cash={2022: 10e6, 2024: cash24})
    return _run(facts, judgment={"iprd_deferred_payment": entries} if entries is not None else None)


def test_cash_only_payment_of_a_pre_window_charge_is_flagged_then_deducted_when_declared():
    """[Codex review r3, #4322176043] A cash-tag-only payment inside the window that settles an acquired-IPR&D charge
    first expensed BEFORE the window: the window's unpaid remainder is 0 (detection never loaded the earlier expense),
    so the $30M was dropped — the run untouched with no trace (iprd_adjustment None) — and the worker's
    iprd_deferred_payment was refused ("names no acquired-IPR&D charge"), so the tier stayed overstated.
    Now (1) undeclared: the payment is listed in ignored_cash_only with the pre-window charge companyfacts shows and
    ACQUIRED_IPRD_UNMATCHED_PAYMENT names it — nothing is deducted until the worker decides; (2) declared (first charge
    before the window, an expense fact there in companyfacts, the original filing cited, within the deal's
    contingent_total and the payment): the payment is deducted once ($0.30/share), cash basis, recorded
    deferred_payment_of and outside the recurrence count. MAA's shape (cash tag only, never an expense fact) still
    never qualifies: no flag, no block, and a declaration is refused."""
    plain = _plain()
    n = _ok(_pre_window())
    blk = n["iprd_adjustment"]
    assert blk is not None and blk["total"] == 0.0 and blk["periods"] == [], blk
    co = blk["ignored_cash_only"]
    assert (len(co) == 1 and co[0]["period"] == "2024-12-31" and co[0]["cash"] == 30e6
            and co[0]["pre_window_charges"] == ["2022-12-31"]), co
    fl = flags(n, "ACQUIRED_IPRD_UNMATCHED_PAYMENT")
    assert len(fl) == 1 and "FY2024 $30,000,000" in fl[0] and "2022-12-31" in fl[0] and "iprd_deferred_payment" in fl[0], fl
    assert n["weighted"] == plain["weighted"] and n["scenarios"] == plain["scenarios"]
    decl = deferred(period="2024-12-31", amount=30e6, first="2022-12-31", source=PRE_SRC, deal="Old Bio", contingent=PRE_CT)
    m = _ok(_pre_window([decl]))
    mb = m["iprd_adjustment"]
    p24 = [p for p in mb["periods"] if p["period"] == "2024-12-31"]
    assert len(p24) == 1, mb["periods"]
    p24 = p24[0]
    assert (p24["amount_basis"], p24["tag_used"], p24["deducted"], p24["recurrence_excluded"]) == (
        "cash_outflow", CASH, 30e6, "deferred_payment_of"), p24
    assert p24["deferred_payment_of"][0]["first_charge_evidence"] == "companyfacts_expense_fact", p24
    assert mb["total"] == 30e6 and mb["fy_with_charge"] == [] and not mb["recurrent"] and not mb["ignored_cash_only"], mb
    assert not flags(m, "ACQUIRED_IPRD_UNMATCHED_PAYMENT") and flags(m, "ACQUIRED_IPRD_CHARGE")
    _assert_base_untouched(m, plain)
    _assert_shifted(m, plain, 30e6 / SHARES)
    # a declared part of the payment is deducted; the rest stays listed and flagged
    k = _ok(_pre_window([dict(decl, amount=20e6)]))
    kb = k["iprd_adjustment"]
    assert kb["total"] == 20e6 and kb["ignored_cash_only"][0]["cash"] == 10e6, kb
    assert flags(k, "ACQUIRED_IPRD_UNMATCHED_PAYMENT")
    # more than the payment, past the deal's contingent_total, or a first charge companyfacts does not show: refused
    _refused(_pre_window([dict(decl, amount=35e6, deferred_payment_of=dict(decl["deferred_payment_of"],
                                                                            contingent_total=dict(PRE_CT, value=40e6)))]),
             "more than the period's charge")
    _refused(_pre_window([dict(decl, deferred_payment_of=dict(decl["deferred_payment_of"],
                                                               contingent_total=dict(PRE_CT, value=20e6)))]),
             "contingent_total")
    _refused(_pre_window([deferred(period="2024-12-31", amount=30e6, first="2021-12-31",
                                   source="SYN 10-K FY2021 (0000999001-22-000007) Note 4", deal="Old Bio",
                                   contingent=PRE_CT)]),
             "companyfacts covers it")
    # the $0-expense record shape: FY2023 files $0 expensed beside the $30M cash — listed and flagged, not lost
    f0 = _facts(expense={2022: 40e6, 2023: 0.0}, cash={2022: 10e6, 2023: 30e6})
    z = _ok(_run(f0))
    b0 = z["iprd_adjustment"]
    assert [c["period"] for c in b0["ignored_cash_only"]] == ["2023-12-31"] and b0["ignored_cash_only"][0]["cash"] == 30e6, b0
    assert flags(z, "ACQUIRED_IPRD_UNMATCHED_PAYMENT")
    # MAA: cash tag only, never expensed — untouched, and a declaration cannot make it qualify
    maa = _facts(cash={2023: 198152000, 2024: 313888000, 2025: 272030000})
    assert _ok(_run(maa))["iprd_adjustment"] is None
    _refused(_run(maa, judgment={"iprd_deferred_payment": [deferred(period="2024-12-31", amount=30e6, first="2022-12-31",
                                                                     source=PRE_SRC, deal="Old Bio", contingent=PRE_CT)]}),
             "names no acquired-IPR&D charge")


# --- Codex review round 4 of PR #47 -------------------------------------------------------------------------------
def test_rolled_out_entry_stays_declared_and_counts_toward_the_lifetime_cap():
    """[Codex review r4, #4322408940] A deferred-payment entry whose period left the window was listed in
    deferred_payments_unused and make_score refused the score until it was DELETED from judgment.json — yet the
    per-deal cap sums only the entries judgment.json still carries, so after the drop a later declaration could take
    the deal's lifetime payments past its contingent_total ($60M FY2022 rolled out and dropped, then $60M FY2025
    against $100M: $120M accepted). Now a rolled-out entry STAYS in judgment.json: the engine lists it in
    deferred_payments_rolled_out (never applied: it feeds neither the window's deduction nor its recurrence count),
    and it still counts toward the deal's lifetime cap — so a $60M FY2025 declaration beside it is refused, and a
    $40M one (lifetime $100M) is accepted."""
    cap = {"value": 100e6, "source": CT_SRC}
    old = deferred(period="2022-12-31", amount=60e6, first="2021-12-31", source=OK_SRC_2021, deal="Old Bio",
                   contingent=cap)
    new = deferred(amount=20e6, first="2021-12-31", source=OK_SRC_2021, deal="Old Bio", contingent=cap)
    facts = _facts(expense={2021: 8e6, 2023: 15e6, 2025: 20e6})
    n = _ok(_run(facts, judgment={"iprd_deferred_payment": [new, old]}))
    blk = n["iprd_adjustment"]
    assert blk.get("deferred_payments_rolled_out") == [old] and "deferred_payments_unused" not in blk, blk
    assert [x["period"] for x in blk["recurrence_excluded"]] == ["2025-12-31"] and not blk["recurrent"], blk
    assert blk["total"] == 35e6, blk   # the rolled-out entry changes no deduction
    # past the lifetime cap with the rolled-out payment kept: both entries refused
    _refused(_run(_facts(expense={2021: 8e6, 2023: 15e6, 2025: 60e6}),
                  judgment={"iprd_deferred_payment": [dict(new, amount=60e6), old]}),
             "more than its contingent_total")
    fy = ["2023-12-31", "2024-12-31", "2025-12-31"]
    cf = {"facts": {"us-gaap": {EXPENSE: {"units": {"USD": [_fy_fact("2021-01-01", "2021-12-31", 8e6)]}}}}}
    iprd = {"periods": [_rec("2025-12-31", 40e6)]}
    ref, rolled = E.iprd_apply_deferred(iprd, [old, dict(new, amount=40e6)], fy, cf)
    assert ref == [] and rolled == [old] and iprd["periods"][0]["recurrence_excluded"] == "deferred_payment_of", (ref, iprd)


def _biib_eur(native=35e6):
    """BIIB's TTM shape (FY2025 $85M expensed, $50M paid) whose Q1 2026 10-Q files the remainder on the cash tag in
    EUR only (a mixed-unit filer): the FX pass holds FY-end rates only, never the 10-Q's YTD end."""
    facts = _facts(expense={2025: 85e6}, cash={2025: 50e6})
    _syn_put(facts, CASH, "EUR", {"start": "2026-01-01", "end": "2026-03-31", "val": native, "form": "10-Q", "fp": "Q1",
                                  "fy": 2026, "filed": "2026-04-29", "accn": "0000999001-26-000020"})
    ttm = _ttm_doc(2.1, 100e6)
    ttm["inputs"]["ocf"]["ytd_current_period"] = ["2026-01-01", "2026-03-31"]
    return facts, ttm


def _run_fx(facts, rates, extra=(), ttm=None, judgment=None):
    fx = dict(_syn_fixture(facts, 30.0), fx_rates=rates)
    return run("SYN", args_for(5, extra=list(extra)), judgment=with_checks(facts, judgment), ttm=ttm, fixture=fx)


def _eur_cash_ytd(facts, val, accn):
    _syn_put(facts, CASH, "EUR", {"start": "2026-01-01", "end": "2026-03-31", "val": val, "form": "10-Q", "fp": "Q1",
                                  "fy": 2026, "filed": "2026-04-29", "accn": accn})
    return facts


def test_local_currency_cash_settlement_is_converted_at_its_own_date_or_gated():
    """[Codex review r4, #4322408953] A cash-tag-only settlement filed in a currency the FX pass holds no rate for at
    its date (the current-YTD 10-Q end is never in the pass's FY-end table) came back with value None, so it neither
    settled the window's unpaid remainder nor was listed or flagged: BIIB's shape in EUR scored a $50M deduction, not
    $85M, with no trace. Now the engine fetches the period rate for the cash leg (fx_rate, as the 5.5 intangible
    capex leg does): EUR 35M at 1.0 settles the $35M remainder (total $85M, the USD run's figure). With no rate at
    all, the native amount stays on the record (excluded non_usd_no_rate, cash_native) and ACQUIRED_IPRD_UNCONVERTED
    names it (make_score refuses the score) when it could settle the window's remainder or a charge expensed before
    the window; otherwise (nothing it could settle) it is listed in ignored_cash_only with its native amount and
    raises nothing. The FY leg the same: a fetched rate converts, no rate gates."""
    facts, ttm = _biib_eur()
    n = _ok(_run_fx(facts, {"EUR": {"2026-03-31": 1.0}}, extra=["--ttm"], ttm=ttm))
    blk = n["iprd_adjustment"]
    assert blk["total"] == 85e6, blk["periods"]
    y = [p for p in blk["periods"] if p["window"] == "ttm_current_ytd"][0]
    assert y["deducted"] == 35e6 and y.get("deferred_payment") and y["fx_rate"] == 1.0, y
    assert not flags(n, "ACQUIRED_IPRD_UNCONVERTED")
    g = _ok(_run_fx(facts, {}, extra=["--ttm"], ttm=ttm))
    gb = g["iprd_adjustment"]
    y = [p for p in gb["periods"] if p["window"] == "ttm_current_ytd"]
    assert len(y) == 1, gb
    y = y[0]
    assert (y["excluded"] == "non_usd_no_rate" and y.get("cash_native") == 35e6 and y["cash_unit"] == "EUR"
            and y["deducted"] == 0), y
    fl = flags(g, "ACQUIRED_IPRD_UNCONVERTED")
    assert len(fl) == 1 and "YTD 2026-01-01..2026-03-31 35,000,000 EUR" in fl[0], fl
    fy = ["2023-12-31", "2024-12-31", "2025-12-31"]
    # a pre-window charge it may settle (no window remainder): gated too
    pw = _eur_cash_ytd(_facts(expense={2021: 40e6, 2025: 20e6}, cash={2025: 20e6}), 30e6, "0000999001-26-000021")
    out = E.iprd_detect(pw, fy, ytd=("2026-01-01", "2026-03-31"), fx_rates={}, checks=auto_checks(pw))
    assert [p.get("cash_native") for p in out["periods"] if p["window"] == "ttm_current_ytd"] == [30e6], out
    assert [x for x in E.iprd_flags(out) if x.startswith("ACQUIRED_IPRD_UNCONVERTED")], E.iprd_flags(out)
    # nothing it could settle (no remainder, no pre-window charge): listed with its native amount, no gate
    nn = _eur_cash_ytd(_facts(expense={2025: 20e6}, cash={2025: 20e6}), 30e6, "0000999001-26-000022")
    out = E.iprd_detect(nn, fy, ytd=("2026-01-01", "2026-03-31"), fx_rates={}, checks=auto_checks(nn))
    assert not [p for p in out["periods"] if p["window"] == "ttm_current_ytd"], out
    assert [(c.get("cash_native"), c["cash_unit"]) for c in out["ignored_cash_only"]] == [(30e6, "EUR")], out
    assert not [x for x in E.iprd_flags(out) if x.startswith("ACQUIRED_IPRD_UNCONVERTED")]
    # the FY leg: FY2024 $40M expensed, $10M paid; FY2025 pays the rest as EUR 24M (x 1.25) on the cash tag alone
    fyf = _facts(expense={2024: 40e6}, cash={2024: 10e6})
    _syn_put(fyf, CASH, "EUR", _ctx("2025-01-01", "2025-12-31", 24e6, filed="2026-02-20"))
    m = _ok(_run_fx(fyf, {"EUR": {"2025-12-31": 1.25}}))
    mb = m["iprd_adjustment"]
    assert abs(mb["total"] - 40e6) < 1.0 and mb["fy_with_charge"] == ["2024-12-31"], mb
    z = _ok(_run_fx(fyf, {}))
    assert z["iprd_adjustment"]["total"] == 10e6 and flags(z, "ACQUIRED_IPRD_UNCONVERTED"), z["iprd_adjustment"]


# --- Codex review round 6 of PR #47 -------------------------------------------------------------------------------
def _usd_expense_eur_cash(expense, eur_cash, extra_cash=None):
    """A mixed-unit filer: the acquired-IPR&D expense in USD, the same FY2025 payment on the cash tag in EUR only."""
    f = _facts(expense=expense, cash=extra_cash)
    _syn_put(f, CASH, "EUR", _ctx("2025-01-01", "2025-12-31", eur_cash, filed="2026-02-20"))
    return f


def _refused_by(fn, *args):
    try:
        fn(*args)
    except SystemExit as e:
        return e.code
    return None


def test_unconvertible_cash_beside_a_usd_expense_is_gated_not_replaced_by_the_expense():
    """[Codex review r6, #4322859272] The cash outflow is the preferred amount when it is filed. A FY2025 $20M USD
    expense beside a EUR 10M payment on the cash tag deducts $11M at a 1.10 rate (the cash basis); with no rate at
    all (none in the FX pass, none fetched) the record fell back to the $20M EXPENSE, the cash-flow check matched to
    the expense let it be deducted, and no flag was raised: make_score published a $9M over-deduction (and, where the
    payment exceeds the expense, an under-deduction). The unconverted cash leg was gated only for a cash-only or $0
    expense period. Now a positive cash fact the run cannot convert gates its period whatever the expense: excluded
    non_usd_no_rate with cash_native kept, nothing deducted, ACQUIRED_IPRD_UNCONVERTED naming the payment, and
    make_score refuses the score (NEEDS_MAIN_AGENT: currency)."""
    import make_score as M
    f = _usd_expense_eur_cash({2025: 20e6}, 10e6)
    conv = _ok(_run_fx(f, {"EUR": {"2025-12-31": 1.10}}))["iprd_adjustment"]
    assert abs(conv["total"] - 11e6) < 1.0 and conv["periods"][-1]["amount_basis"] == "cash_outflow", conv["periods"]
    g = _ok(_run_fx(_usd_expense_eur_cash({2025: 20e6}, 10e6), {}))
    blk = g["iprd_adjustment"]
    p = [x for x in blk["periods"] if x["period"] == "2025-12-31"][0]
    assert (p["excluded"] == "non_usd_no_rate" and p.get("cash_native") == 10e6 and p["cash_unit"] == "EUR"
            and p["deducted"] == 0 and p["expense"] == 20e6), p
    assert blk["total"] == 0 and blk["treatment"] == "non_usd_no_rate", blk
    fl = flags(g, "ACQUIRED_IPRD_UNCONVERTED")
    assert len(fl) == 1 and "FY2025 10,000,000 EUR" in fl[0] and "20,000,000" in fl[0], fl
    assert _refused_by(M.check_iprd_unconverted, g) == 1, "make_score accepted an unconverted preferred cash leg"
    # the payment exceeds the expense (FY2024 $15M expensed, $5M paid; FY2025 $20M expensed, EUR 30M paid): with no
    # rate the FY2025 period is gated, never the $20M expense standing in for the larger payment
    h = _ok(_run_fx(_usd_expense_eur_cash({2024: 15e6, 2025: 20e6}, 30e6, extra_cash={2024: 5e6}), {}))
    hb = h["iprd_adjustment"]
    q = [x for x in hb["periods"] if x["period"] == "2025-12-31"][0]
    assert q["excluded"] == "non_usd_no_rate" and q.get("cash_native") == 30e6 and q["deducted"] == 0, q
    assert hb["total"] == 5e6 and flags(h, "ACQUIRED_IPRD_UNCONVERTED"), hb
    assert _refused_by(M.check_iprd_unconverted, h) == 1
    # a negative native cash fact beside a positive expense stays the sign error it was: the expense decides
    fy = ["2023-12-31", "2024-12-31", "2025-12-31"]
    neg = _usd_expense_eur_cash({2025: 20e6}, -10e6)
    out = E.iprd_detect(neg, fy, fx_rates={}, checks=auto_checks(neg), fx_fetch=lambda c, d: None)
    r = [x for x in out["periods"] if x["period"] == "2025-12-31"][0]
    assert r["excluded"] is None and r["amount_basis"] == "expense" and r["deducted"] == 20e6, r


def _refused_iprd_records():
    """dcf_numbers.json shapes make_score refuses for an unresolved acquired-IPR&D charge (the new run is left on disk
    beside the score.json of an earlier run): both refused treatments, and a partly deducted one-time run that still
    carries a period awaiting its cash-flow check or one the run cannot convert."""
    base = _adjusted()
    out = []
    for t, per in (("awaiting_cash_flow_check", {"excluded": "awaiting_cash_flow_check", "awaiting": 284.9e6}),
                   ("non_usd_no_rate", {"excluded": "non_usd_no_rate", "expense_native": 250e6, "expense_unit": "EUR"}),
                   ("non_usd_no_rate", {"excluded": "non_usd_no_rate", "cash_native": 10e6, "cash_unit": "EUR"})):
        n = copy.deepcopy(base)
        blk = n["iprd_adjustment"]
        blk["periods"] = [dict(blk["periods"][-1], deducted=0.0, **per)]
        blk.update(treatment=t, total=0.0, charge_per_share=0.0)
        out.append(n)
    for per in ({"excluded": "awaiting_cash_flow_check", "awaiting": 9e6},
                {"excluded": "non_usd_no_rate", "cash_native": 9e6, "cash_unit": "EUR"}):
        n = copy.deepcopy(base)
        n["iprd_adjustment"]["periods"].append({"period": "2026-03-31", "window": "ttm_current_ytd", "deducted": 0.0,
                                                **per})
        assert n["iprd_adjustment"]["treatment"] == "one_time_value_deduction"
        out.append(n)
    return out


def test_reprice_and_build_site_withhold_a_run_make_score_refused():
    """[Codex review r6, #4322859281] make_score refuses a run with an acquired-IPR&D period awaiting its cash-flow
    check or one the engine cannot convert, but the engine has already written dcf_numbers.json and the earlier
    run's score.json stays on disk. The freshness checks did not stop it: reprice.score_matches_run only marked
    score_json_fresh false and dropped the tier override (live.json still written, on the UNADJUSTED paths, charge
    0), build_site.qualifies needs only a score.json, and live_shown withheld only an older live.json or the
    share-count treatment, so the site ranked the name on the refused run's unadjusted live IRR. Now every such run
    is skipped by reprice (no live.json; a stale one removed) and build_site withholds any live.json with reason
    iprd_unresolved (the scored figures stand); a resolved one-time run reprices and shows as before."""
    import reprice as R
    import build_site as B
    import make_score as M
    import shutil
    import tempfile
    lv = {"price": 25.0, "irr_weighted": 0.3, "price_date": "2026-10-21", "scored_date": "2026-10-20"}
    sc = {"analysis_date": "2026-10-19"}
    for n in _refused_iprd_records():
        refused = [_refused_by(M.check_iprd_cash_flow, n, []), _refused_by(M.check_iprd_unconverted, n)]
        assert 1 in refused, ("make_score accepts this shape", n["iprd_adjustment"])
        for fn in (lambda: R.check_eligible(n), lambda: R.reprice(n, 25.0)):
            try:
                fn()
                raise AssertionError("repriced a run make_score refused: " + str(n["iprd_adjustment"]["periods"][-1]))
            except R.Skip as e:
                assert "acquired-IPR&D" in str(e) and "make_score" in str(e), str(e)
        for live in (lv, None):
            shown, w = B.live_shown({"score": sc, "numbers": n, "live": live})
            assert shown is None and w is not None and w["reason"] == "iprd_unresolved", w
            assert w["price"] == (25.0 if live else None) and w["scored_date"] == "2026-10-19", w
            assert "acquired-IPR&D" in w["note"] and "make_score" in w["note"], w["note"]
        tmp = tempfile.mkdtemp(prefix="reprice_iprd_r6_")
        saved = R.BASE
        try:
            os.makedirs(os.path.join(tmp, "TST"))
            with open(os.path.join(tmp, "TST", "dcf_numbers.json"), "w", encoding="utf-8") as f:
                json.dump(dict(n, ticker="TST"), f)
            with open(os.path.join(tmp, "TST", "live.json"), "w", encoding="utf-8") as f:
                json.dump({"price": 25.0, "irr_weighted": 0.3}, f)
            R.BASE = tmp
            try:
                R.reprice_folder("TST")
                raise AssertionError("reprice_folder wrote live.json")
            except R.Skip:
                pass
            assert not os.path.exists(os.path.join(tmp, "TST", "live.json")), "the stale live.json stayed"
        finally:
            R.BASE = saved
            shutil.rmtree(tmp, ignore_errors=True)
    # a resolved one-time run reprices and shows as before
    assert R.reprice(_adjusted(), 25.0)["iprd_charge_per_share"] == 0.35
    adj = _adjusted()
    # [Codex review r29 of PR #47] live.json computed against that score (reprice records which one)
    own = R.reprice(adj, 25.0, adj["as_of"], _score_of(adj), today=adj["as_of"])
    assert B.live_shown({"score": _score_of(adj), "numbers": adj, "live": own}) == (own, None)
    assert E.iprd_unresolved(_adjusted()) is None and E.iprd_unresolved({"iprd_adjustment": None}) is None


# --- Codex review round 7 of PR #47 -------------------------------------------------------------------------------
def test_rolled_out_entry_is_validated_before_it_counts_toward_the_lifetime_cap():
    """[Codex review r7, #4323129476] A rolled-out entry (period older than the window) was moved to
    deferred_payments_rolled_out right after the shape, one-first-charge and cap checks — before any semantic one —
    so a declaration that could never have passed (its first charge after its own period, an accession outside the
    original filing's years, a pre-window first charge companyfacts covers with no acquired-IPR&D expense fact) was
    silently kept, and its amount took the deal's lifetime contingent_total: a valid $60.0M FY2025 Old Bio milestone
    beside a bogus $60.0M FY2022 one ($100.0M cap) was refused as past the cap. Now a rolled-out entry passes the same
    period-independent checks as an in-window one; an invalid one is refused for its own reason (exit 3), never
    listed rolled out and never counted toward the cap. A valid rolled-out entry is still kept and still counts."""
    fy = ["2023-12-31", "2024-12-31", "2025-12-31"]
    cap = {"value": 100e6, "source": CT_SRC}
    # companyfacts reaches back to 2015 (Revenues) and carries the FY2021 Old Bio charge only
    cf = {"facts": {"us-gaap": {
        EXPENSE: {"units": {"USD": [_fy_fact("2021-01-01", "2021-12-31", 8e6)]}},
        "Revenues": {"units": {"USD": [_fy_fact("2015-01-01", "2015-12-31", 1e9)]}}}}}
    new = deferred(amount=60e6, first="2021-12-31", source=OK_SRC_2021, deal="Old Bio", contingent=cap)

    def old(first="2021-12-31", source=OK_SRC_2021, deal="Old Bio", contingent=cap):
        return deferred(period="2022-12-31", amount=60e6, first=first, source=source, deal=deal, contingent=contingent)

    ghost_ct = {"value": 60e6, "source": CT_SRC}
    bad = [(old(first="2023-12-31", source=_src(24), deal="Ghost Bio", contingent=ghost_ct), "must precede"),
           (old(first="2021-12-31", source=_src(26)), "source must cite the original acquisition filing"),
           (old(first="2019-12-31", source=_src(20), deal="Ghost Bio", contingent=ghost_ct),
            "no acquired-IPR&D expense fact"),
           # [Codex review r8] an impossible date is malformed now (iprd_date_ok), refused before any other check
           (old(first="2021-02-30", source=_src(21), deal="Ghost Bio", contingent=ghost_ct), "malformed")]
    for e, needle in bad:
        iprd = {"periods": [_rec("2025-12-31", 60e6)]}
        ref, rolled = E.iprd_apply_deferred(iprd, [e], fy, cf)
        assert rolled == [] and [r["entry"] for r in ref] == [e] and needle in ref[0]["reason"], (needle, ref, rolled)
    # the bogus FY2022 Old Bio entry no longer takes the cap: the valid FY2025 milestone applies, the bogus one is refused
    bogus = bad[1][0]
    iprd = {"periods": [_rec("2025-12-31", 60e6)]}
    ref, rolled = E.iprd_apply_deferred(iprd, [bogus, new], fy, cf)
    assert [r["entry"] for r in ref] == [bogus] and rolled == [], (ref, rolled)
    assert "source must cite the original acquisition filing" in ref[0]["reason"], ref
    assert iprd["periods"][0].get("recurrence_excluded") == "deferred_payment_of", iprd
    # a valid rolled-out entry is still kept and still counts toward the cap
    ref, rolled = E.iprd_apply_deferred({"periods": [_rec("2025-12-31", 60e6)]}, [old(), new], fy, cf)
    assert rolled == [] and len(ref) == 2 and all("more than its contingent_total" in r["reason"] for r in ref), ref
    ref, rolled = E.iprd_apply_deferred({"periods": [_rec("2025-12-31", 40e6)]}, [old(), dict(new, amount=40e6)], fy, cf)
    assert ref == [] and rolled == [old()], (ref, rolled)
    # end to end: the run exits 3 (BAD_IPRD_DEFERRED_PAYMENT) instead of recording the bogus entry rolled out
    out = _run(_facts(expense={2021: 8e6, 2025: 60e6}), judgment={"iprd_deferred_payment": [bogus]})
    _refused(out, "source must cite the original acquisition filing")
    for e, needle in bad[2:3]:
        _refused(_run(_facts(expense={2021: 8e6, 2025: 60e6}), judgment={"iprd_deferred_payment": [e]}), needle)


# --- Codex review round 8 of PR #47 -------------------------------------------------------------------------------
FY3 = ["2023-12-31", "2024-12-31", "2025-12-31"]
R8_CAP = {"value": 100e6, "source": CT_SRC}


def test_deferred_periods_must_be_real_dates():
    """[Codex review r8, #4323410495] A deferred entry's period was checked against \\d{4}-\\d{2}-\\d{2} only, never
    parsed: "2020-99-99" sorts before the window, so it was kept rolled out and counted toward the deal's lifetime
    contingent_total — a valid $60M FY2025 Old Bio milestone beside a bogus $50M "2020-99-99" one against $100M was
    refused. Every period and first_charged_period is now parsed (date.fromisoformat): an impossible date is malformed
    (refused for its own reason, never counted), and the valid entry is applied. The cash-flow check's period too."""
    good = deferred(amount=60e6, first="2021-12-31", source=OK_SRC_2021, deal="Old Bio", contingent=R8_CAP)
    cf = {"facts": {"us-gaap": {EXPENSE: {"units": {"USD": [_fy_fact("2021-01-01", "2021-12-31", 8e6)]}}}}}
    assert E.iprd_deferred_entry_ok(good)
    for bad_p in ("2020-99-99", "2020-02-30", "2020-13-01"):
        bogus = dict(good, period=bad_p, amount=50e6)
        assert not E.iprd_deferred_entry_ok(bogus), bad_p
        iprd = {"periods": [_rec("2025-12-31", 60e6)]}
        ref, rolled = E.iprd_apply_deferred(iprd, [bogus, good], FY3, cf)
        assert [r["entry"] for r in ref] == [bogus] and "malformed" in ref[0]["reason"] and rolled == [], (ref, rolled)
        assert iprd["periods"][0].get("recurrence_excluded") == "deferred_payment_of", iprd
    for bad_f in ("2021-02-30", "2021-00-10"):
        e = dict(good, deferred_payment_of=dict(good["deferred_payment_of"], first_charged_period=bad_f))
        assert not E.iprd_deferred_entry_ok(e), bad_f
    assert not E.iprd_cash_flow_check_entry_ok(dict(ADDED_BACK, period="2025-02-30", window="fy"))
    assert E.iprd_cash_flow_check_entry_ok(dict(ADDED_BACK, period="2025-12-31", window="fy"))
    _refused(_run(_facts(expense={2021: 8e6, 2025: 60e6}),
                  judgment={"iprd_deferred_payment": [dict(good, period="2020-99-99")]}), "malformed")


def _intang_check(presentation="paid_in_intangible_capex", amount=20e6):
    return [{"period": "2025-12-31", "window": "fy", "amount": amount, "presentation": presentation,
             "source": "SYN 10-K FY2025 (0000999001-26-000004) cash-flow statement R7.htm: investing activities "
                       "'Purchases of intangible assets' include the $20.0M acquired IPR&D payment"}]


def test_overlap_with_intangible_capex_is_declared_not_inferred_from_size():
    """[Codex review r8, #4323410514] The overlap guard excluded an expense-basis period as already_in_capex whenever
    the period's capex intangible leg was >= 98% of the charge — a size comparison only, ahead of the cash-flow check:
    a confirmed $20M payment (added back, paid in investing) beside $100M of unrelated patent / software purchases
    deducted $0, with no flag. Now only the worker's iprd_cash_flow_check presentation paid_in_intangible_capex (the
    payment sits inside an intangible-purchase line the engine sums into capex, the line cited) excludes it; the size
    comparison is a non-blocking capex_overlap_note. A paid_in_intangible_capex check where the engine's intangible
    leg does not cover the charge is not applied: the period stays gated (awaiting_cash_flow_check)."""
    intang = {2025: 100e6}
    plain = _plain(intangibles=intang)
    n = _ok(_run(_facts(expense={2025: 20e6}, intangibles=intang)))   # added_back_paid_in_investing
    p = [x for x in n["iprd_adjustment"]["periods"] if x["period"] == "2025-12-31"][0]
    assert p["excluded"] is None and p["deducted"] == 20e6 and "capex_overlap_note" in p, p
    assert n["iprd_adjustment"]["total"] == 20e6
    _assert_shifted(n, plain, 20e6 / SHARES)
    n0 = _ok(_run(_facts(expense={2025: 20e6}, intangibles=intang), checks=False))
    p0 = [x for x in n0["iprd_adjustment"]["periods"] if x["period"] == "2025-12-31"][0]
    assert p0["excluded"] == "awaiting_cash_flow_check" and E.iprd_unresolved(n0), p0
    n1 = _ok(_run(_facts(expense={2025: 20e6}, intangibles=intang), judgment={"iprd_cash_flow_check": _intang_check()}))
    b1 = n1["iprd_adjustment"]
    p1 = [x for x in b1["periods"] if x["period"] == "2025-12-31"][0]
    assert p1["excluded"] == "already_in_capex" and p1["deducted"] == 0.0 and b1["total"] == 0.0, p1
    assert p1["cash_flow_check"]["presentation"] == "paid_in_intangible_capex" and p1["capex_intangibles"] == 100e6, p1
    assert n1["weighted"] == plain["weighted"] and not E.iprd_unresolved(n1)
    n2 = _ok(_run(_facts(expense={2025: 20e6}), judgment={"iprd_cash_flow_check": _intang_check()}))
    p2 = [x for x in n2["iprd_adjustment"]["periods"] if x["period"] == "2025-12-31"][0]
    assert p2["excluded"] == "awaiting_cash_flow_check" and "cash_flow_check_mismatch" in p2, p2
    assert "intangible" in p2["cash_flow_check_mismatch"]["note"] and E.iprd_unresolved(n2), p2


def _eur_expense_usd_cash():
    f = _syn_facts()
    _syn_put(f, EXPENSE, "EUR", _ctx("2024-01-01", "2024-12-31", 85e6, filed="2025-02-20"))
    _fy(f, CASH, 2024, 50e6)
    _fy(f, CASH, 2025, 35e6)
    return f


def test_unconverted_expense_beside_usd_cash_fetches_its_rate_or_gates_later_cash():
    """[Codex review r8, #4323410525] An expense with no FX rate beside a usable USD cash fact deducted that cash but
    left the record's expense None, so no unpaid remainder accrued and a later cash-only settlement went to
    ignored_cash_only with no flag (EUR 85M expensed FY2024, $50M paid FY2024, $35M FY2025: $50M deducted). Now the
    expense period's rate is fetched (the round-4 fx_fetch helper, as for the cash leg): at 1.0 the $35M settles the
    remainder ($85M). With no rate the native expense is kept and later window cash on it is gated
    (non_usd_no_rate, unconverted_remainder_of, ACQUIRED_IPRD_UNCONVERTED) — never silently ignored."""
    out = E.iprd_detect(_eur_expense_usd_cash(), FY3, fx_rates={},
                        fx_fetch=lambda c, d: 1.0 if (c, d) == ("EUR", "2024-12-31") else None)
    recs = {p["period"]: p for p in out["periods"]}
    assert recs["2024-12-31"]["expense"] == 85e6 and recs["2024-12-31"]["deducted"] == 50e6, recs
    assert recs["2025-12-31"]["deducted"] == 35e6 and recs["2025-12-31"].get("deferred_payment"), recs
    assert out["ignored_cash_only"] == [], out["ignored_cash_only"]
    out = E.iprd_detect(_eur_expense_usd_cash(), FY3, fx_rates={}, fx_fetch=lambda c, d: None)
    recs = {p["period"]: p for p in out["periods"]}
    r24, r25 = recs["2024-12-31"], recs["2025-12-31"]
    assert r24["deducted"] == 50e6 and r24["expense"] is None and r24["expense_native"] == 85e6, r24
    assert r25["excluded"] == "non_usd_no_rate" and r25["deducted"] == 0.0, r25
    assert r25["unconverted_remainder_of"] == ["2024-12-31"] and r25["cash"] == 35e6, r25
    assert out["ignored_cash_only"] == [], out["ignored_cash_only"]
    assert E.iprd_unresolved({"iprd_adjustment": out})
    fl = E.iprd_flags(dict(out, total=0.0))
    assert any(f.startswith("ACQUIRED_IPRD_UNCONVERTED") and "FY2024" in f and "FY2025" in f for f in fl), fl
    # end to end: the engine fetches the rate (fixture fx_rates) or gates the later cash
    n = _ok(_run_fx(_eur_expense_usd_cash(), {"EUR": {"2024-12-31": 1.0}}, judgment={}))
    assert n["iprd_adjustment"]["total"] == 85e6, n["iprd_adjustment"]["periods"]
    m = _ok(_run_fx(_eur_expense_usd_cash(), {}, judgment={}))
    assert m["iprd_adjustment"]["total"] == 50e6 and E.iprd_unresolved(m), m["iprd_adjustment"]["periods"]


def test_both_expense_tags_filed_the_positive_one_is_read():
    """[Codex review r8, #4323410542] With both detector tags filed for a period, the loop took the first one filed
    whatever its value: a $0 current tag hid a positive ResearchAndDevelopmentInProcess fact, the period deducted $0
    and the same-period $500M cash went to ignored_cash_only — no deduction, no flag. Now the positive one is read;
    when both are positive and differ by more than $1 both are recorded (expense_tags_conflict) and the current tag is
    used, with a reconcile note."""
    out = E.iprd_detect(_facts(expense={2025: 0.0}, old_expense={2025: 500e6}, cash={2025: 500e6}), FY3)
    r = [p for p in out["periods"] if p["period"] == "2025-12-31"][0]
    assert r["expense_tag"] == EXPENSE_OLD and r["expense"] == 500e6 and r["deducted"] == 500e6, r
    assert out["ignored_cash_only"] == [], out
    out = E.iprd_detect(_facts(expense={2025: 0.0}, old_expense={2025: 500e6}), FY3)
    r = [p for p in out["periods"] if p["period"] == "2025-12-31"][0]
    assert r["expense_tag"] == EXPENSE_OLD and r["excluded"] == "awaiting_cash_flow_check", r
    out = E.iprd_detect(_facts(expense={2025: 20e6}, old_expense={2025: 25e6}), FY3)
    r = [p for p in out["periods"] if p["period"] == "2025-12-31"][0]
    assert r["expense_tag"] == EXPENSE and r["expense"] == 20e6, r
    assert r["expense_tags_conflict"] == {EXPENSE: 20e6, EXPENSE_OLD: 25e6} and "reconcile" in r["expense_tags_note"], r
    out = E.iprd_detect(_facts(expense={2025: 20e6}, old_expense={2025: 20e6}), FY3)
    r = [p for p in out["periods"] if p["period"] == "2025-12-31"][0]
    assert r["expense_tag"] == EXPENSE and "expense_tags_conflict" not in r, r


# --- Codex review round 9 of PR #47 -------------------------------------------------------------------------------
def _calendar_cf(years=range(2019, 2026)):
    """companyfacts of a calendar-year filer: an FY duration fact per year (Revenues), a Q2 fact ending 2022-06-30 and
    the FY2021 Old Bio acquired-IPR&D charge."""
    rev = [_fy_fact(f"{y}-01-01", f"{y}-12-31", 1e9) for y in years]
    rev.append({"start": "2022-01-01", "end": "2022-06-30", "val": 5e8, "form": "10-Q", "fp": "Q2", "filed": "2022-08-01"})
    return {"facts": {"us-gaap": {"Revenues": {"units": {"USD": rev}},
                                  EXPENSE: {"units": {"USD": [_fy_fact("2021-01-01", "2021-12-31", 8e6)]}}}}}


def _r9_old(period):
    return deferred(period=period, amount=60e6, first="2021-12-31", source=OK_SRC_2021, deal="Old Bio", contingent=R8_CAP)


def test_rolled_out_period_must_be_a_fiscal_year_end_of_the_filer():
    """[Codex review r9, #4323764891] A rolled-out entry's period was checked only as a real date: at a calendar-year
    filer, period 2022-06-30 (a quarter end) or 2022-02-14 was kept rolled out and its amount counted toward the deal's
    lifetime contingent_total for good. Now a rolled-out period must be one of the filer's fiscal-year ends: one of
    companyfacts' annual period ends (fp FY, annual form, a 330-380 day duration) or the engine's window, wherever
    those annual periods reach the date (FY ends within a fiscal year of each other on both sides of it); where they
    do not, the month-day of the nearest known FY end (within 7 days: a 52/53-week year). Otherwise refused
    (BAD_IPRD_DEFERRED_PAYMENT), never kept rolled out, never counted. The run records the FY ends it read
    (iprd_adjustment.fy_period_ends) so make_score re-checks every rolled-out entry with the same helper."""
    cf = _calendar_cf()
    for p in ("2022-06-30", "2022-02-14"):
        iprd = {"periods": [_rec("2025-12-31", 60e6)]}
        ref, rolled = E.iprd_apply_deferred(iprd, [_r9_old(p)], FY3, cf)
        assert rolled == [] and len(ref) == 1 and "not a fiscal-year end" in ref[0]["reason"], (p, ref, rolled)
    ref, rolled = E.iprd_apply_deferred({"periods": [_rec("2025-12-31", 60e6)]}, [_r9_old("2022-12-31")], FY3, cf)
    assert ref == [] and rolled == [_r9_old("2022-12-31")], (ref, rolled)
    assert E.iprd_fy_period_ends(cf, FY3) == [f"{y}-12-31" for y in range(2019, 2026)], E.iprd_fy_period_ends(cf, FY3)
    # companyfacts does not reach the date: the nearest FY end's month-day decides, 52/53-week years within 7 days
    assert E.iprd_fy_end_problem("2022-12-31", FY3) is None
    assert "not a fiscal-year end" in (E.iprd_fy_end_problem("2022-06-30", FY3) or "")
    wk = ["2023-09-30", "2024-09-28", "2025-09-27"]
    assert E.iprd_fy_end_problem("2022-10-01", wk) is None and E.iprd_fy_end_problem("2021-09-25", wk) is None
    assert E.iprd_fy_end_problem("2022-12-31", wk) is not None and E.iprd_fy_end_problem("2022-10-15", wk) is not None
    # a gap in companyfacts' annual periods (no FY end within a fiscal year on one side): the month-day again
    assert E.iprd_fy_end_problem("2022-12-31", ["2015-12-31", "2021-12-31"] + FY3) is None
    assert E.iprd_fy_end_problem("2022-06-30", ["2015-12-31", "2021-12-31"] + FY3) is not None
    # end to end: the engine refuses the quarter-end period; the FY end is kept and the record carries the FY ends
    facts = _facts(expense={2021: 8e6, 2025: 60e6})
    _refused(_run(facts, judgment={"iprd_deferred_payment": [_r9_old("2022-06-30")]}), "not a fiscal-year end")
    n = _ok(_run(facts, judgment={"iprd_deferred_payment": [_r9_old("2022-12-31")]}))
    blk = n["iprd_adjustment"]
    assert blk["deferred_payments_rolled_out"] == [_r9_old("2022-12-31")], blk
    assert blk["fy_period_ends"] == [f"{y}-12-31" for y in range(2019, 2026)], blk.get("fy_period_ends")
    # a run without declarations gains no key
    assert "fy_period_ends" not in (_ok(_run(facts))["iprd_adjustment"] or {})


# --- Codex review round 11 of PR #47 ------------------------------------------------------------------------------
def _chk(period, window, amount):
    return {"period": period, "window": window, "amount": amount, "presentation": "added_back_paid_in_investing",
            "source": f"test: the cash-flow statement adds the {period} charge back and pays it in investing"}


Q1, Q2, Q3 = ("2026-01-01", "2026-03-31"), ("2026-04-01", "2026-06-30"), ("2026-07-01", "2026-09-30")
H1 = ("2026-01-01", "2026-06-30")


def _leg(out, window="ttm_current_ytd", period=None):
    recs = [p for p in out["periods"] if p["window"] == window and (period is None or p["period"] == period)]
    assert len(recs) <= 1, recs
    return recs[0] if recs else None


def test_quarter_only_10q_facts_tile_the_current_ytd_leg():
    """[Codex review r11, #4324232838, the main agent's shape] The TTM's current-YTD leg read an acquired-IPR&D fact
    only on exactly the ttm.json ytd_current_period context: a 10-Q filing the charge for its quarters alone (Q1
    $30M and Q2 $70M three-month facts, no January-June context) left the leg empty — "counted as 0" — and the $100M
    paid in 2026 H1 never reached the deduction. Now a leg with no exact-context fact is read from same-tag, same-unit
    facts that tile it exactly (three-month facts, or a year-to-date fact from the leg's first day), for the expense
    and the cash tag alike: the leg deducts $100M (cash basis), records context_basis aggregated_quarters and the
    contexts used, and every IV shifts by the whole $120M window total per share."""
    facts = _facts(expense={2025: 20e6}, cash={2025: 20e6})
    for tag in (EXPENSE, CASH):
        _ytd(facts, tag, Q1[0], Q1[1], 30e6, "2026-05-05", fp="Q1")
        _ytd(facts, tag, Q2[0], Q2[1], 70e6, "2026-08-05", fp="Q2")
    ttm = _ttm_doc(2.1, 98e6)
    plain = _ok(_run(_facts(), extra=["--ttm"], ttm=ttm))
    n = _ok(_run(facts, extra=["--ttm"], ttm=ttm, checks=False))
    blk = n["iprd_adjustment"]
    rec = _leg(blk)
    assert rec is not None, (blk["periods"], blk.get("notes"))
    assert (rec["expense"], rec["cash"], rec["amount_basis"], rec["deducted"]) == (100e6, 100e6, "cash_outflow", 100e6), rec
    q = {"unit": "USD", "contexts": [list(Q1), list(Q2)]}
    assert rec["context_basis"] == "aggregated_quarters" and rec["aggregated_contexts"] == {CASH: q, EXPENSE: q}, rec
    assert blk["total"] == 120e6 and not any("counted as 0" in x for x in blk.get("notes") or []), blk
    assert all("context_basis" not in p for p in blk["periods"] if p["window"] == "fy"), blk["periods"]
    _assert_shifted(n, plain, 120e6 / 98e6)
    _assert_base_untouched(n, plain)


def test_tiling_takes_the_exact_fact_first_never_double_counts_and_records_partial_coverage():
    """[Codex review r11, #4324232838] The tiling rules: an exact-context fact always wins (H1 $90M beside Q1 + Q2
    three-month facts); H1 + Q3 tile a nine-month leg; overlapping facts (Q1, H1, Q2, Q3) are never summed twice
    (the fewest facts: H1 + Q3); a gap (Q1 and Q3, no Q2) or a unit change (Q1 USD, Q2 EUR) tiles nothing — the
    leg is recorded in partial_coverage, its note says so and ACQUIRED_IPRD_PARTIAL_PERIOD names it, never a
    silent $0."""
    def facts_with(*facts_):
        f = _facts(expense={2025: 20e6})
        for (s, e), v, fp, unit in facts_:
            filed = {"Q1": "2026-05-05", "Q2": "2026-08-05", "Q3": "2026-11-05"}[fp]
            _syn_put(f, EXPENSE, unit, {"start": s, "end": e, "val": v, "form": "10-Q", "fp": fp, "fy": 2026,
                                        "filed": filed, "accn": f"0000999001-{filed}"})
        return f

    def detect(f, leg, amount=None):
        checks = [_chk("2025-12-31", "fy", 20e6)] + ([_chk(leg[1], "ttm_current_ytd", amount)] if amount else [])
        return E.iprd_detect(f, FY3, ytd=leg, fx_rates={}, checks=checks)

    nine = (Q1[0], Q3[1])
    out = detect(facts_with((H1, 90e6, "Q2", "USD"), (Q1, 30e6, "Q1", "USD"), (Q2, 70e6, "Q2", "USD")), H1, 90e6)
    rec = _leg(out)
    assert rec["expense"] == 90e6 and rec["deducted"] == 90e6 and "context_basis" not in rec, rec
    out = detect(facts_with((H1, 50e6, "Q2", "USD"), (Q3, 25e6, "Q3", "USD")), nine, 75e6)
    rec = _leg(out)
    assert rec["expense"] == 75e6 and rec["deducted"] == 75e6, rec
    assert rec["aggregated_contexts"] == {EXPENSE: {"unit": "USD", "contexts": [list(H1), list(Q3)]}}, rec
    out = detect(facts_with((Q1, 30e6, "Q1", "USD"), (H1, 100e6, "Q2", "USD"), (Q2, 70e6, "Q2", "USD"),
                            (Q3, 25e6, "Q3", "USD")), nine, 125e6)
    rec = _leg(out)
    assert rec["expense"] == 125e6 and rec["aggregated_contexts"][EXPENSE]["contexts"] == [list(H1), list(Q3)], rec
    for shape in (((Q1, 30e6, "Q1", "USD"), (Q3, 25e6, "Q3", "USD")), ((Q1, 30e6, "Q1", "USD"), (Q2, 70e6, "Q2", "EUR"))):
        leg = nine if shape[-1][0] == Q3 else H1
        out = detect(facts_with(*shape), leg)
        assert _leg(out) is None and sum(p["deducted"] for p in out["periods"]) == 20e6, out["periods"]
        pc = out.get("partial_coverage")
        assert pc and pc[0]["window"] == "ttm_current_ytd" and pc[0]["tag"] == EXPENSE and pc[0]["start"] == leg[0], pc
        assert sorted(c["value"] for u in pc[0]["units"] for c in u["contexts"]) == sorted(x[1] for x in shape), pc
        assert any("cover only part of it" in x for x in out["notes"]), out["notes"]
        fl = [x for x in E.iprd_flags(out) if x.startswith("ACQUIRED_IPRD_PARTIAL_PERIOD: ")]
        assert len(fl) == 1 and "current YTD" in fl[0] and "30,000,000" in fl[0], E.iprd_flags(out)


def test_fy_leg_without_a_10k_fact_is_tiled_from_quarters_or_flagged_partial():
    """[Codex review r11, #4324232838, the main agent's shape: every window leg] An FY leg read only the 10-K's FY
    context: an FY2024 charge filed as four three-month facts (Q1-Q3 in the 10-Qs, Q4 in the 10-K) was missed, and so
    was a cash outflow filed by quarter beside an exact FY expense. Now both tile (FY2024: $40M expense and cash,
    cash basis; FY2025: the $40M expense exact, the cash from its quarters, cash basis). A 10-Q's nine-month fact with
    no FY figure (the SMMT shape: $520.9M January-September 2023, no 10-K fact) covers only part of FY2023: the block
    is kept for it (partial_coverage), ACQUIRED_IPRD_PARTIAL_PERIOD fires and nothing is deducted for it."""
    f = _facts(expense={2025: 40e6})
    quarters = (("01-01", "03-31", "Q1", "10-Q"), ("04-01", "06-30", "Q2", "10-Q"), ("07-01", "09-30", "Q3", "10-Q"),
                ("10-01", "12-31", "FY", "10-K"))
    for y, tags in ((2024, (EXPENSE, CASH)), (2025, (CASH,))):
        for s, e, fp, form in quarters:
            for tag in tags:
                _ytd(f, tag, f"{y}-{s}", f"{y}-{e}", 10e6, f"{y + 1}-02-20" if form == "10-K" else f"{y}-11-05",
                     form=form, fp=fp)
    out = E.iprd_detect(f, FY3, fx_rates={}, checks=[])
    r24, r25 = _leg(out, "fy", "2024-12-31"), _leg(out, "fy", "2025-12-31")
    ctx = lambda y: [[f"{y}-{s}", f"{y}-{e}"] for s, e, _, _ in quarters]
    assert (r24["expense"], r24["cash"], r24["amount_basis"], r24["deducted"]) == (40e6, 40e6, "cash_outflow", 40e6), r24
    assert r24["aggregated_contexts"] == {CASH: {"unit": "USD", "contexts": ctx(2024)},
                                          EXPENSE: {"unit": "USD", "contexts": ctx(2024)}}, r24
    assert (r25["expense"], r25["cash"], r25["amount_basis"], r25["deducted"]) == (40e6, 40e6, "cash_outflow", 40e6), r25
    assert r25["aggregated_contexts"] == {CASH: {"unit": "USD", "contexts": ctx(2025)}}, r25
    assert "partial_coverage" not in out
    # the SMMT shape: a nine-month 10-Q fact, no FY figure
    smmt = _facts()
    _ytd(smmt, EXPENSE, "2023-01-01", "2023-09-30", 520.915e6, "2023-11-06", fp="Q3")
    out = E.iprd_detect(smmt, FY3, fx_rates={}, checks=[])
    assert out is not None and out["periods"] == [] and out["partial_coverage"][0]["period"] == "2023-12-31", out
    plain = _plain()
    n = _ok(_run(smmt))
    blk = n["iprd_adjustment"]
    assert blk["total"] == 0 and blk["charge_per_share"] == 0 and blk["partial_coverage"] == out["partial_coverage"], blk
    fl = flags(n, "ACQUIRED_IPRD_PARTIAL_PERIOD: ")
    assert len(fl) == 1 and "FY2023 (2023-01-01..2023-12-31)" in fl[0] and "520,915,000" in fl[0], n.get("fragility_flags")
    for k in ("implied_irr_weighted", "iv_at_15", "tier_by_numbers", "base_oe_per_share"):
        assert n[k] == plain[k], k


# --- Codex review round 12 of PR #47 ------------------------------------------------------------------------------
def test_a_zero_fact_on_one_detector_tag_never_hides_a_positive_partial_fact_on_the_other():
    """[Codex review r12, #4324802973, the main agent's shape] An exact FY2025 $0 fact on the current detector tag
    counted as having read the leg, so a positive partial-period fact on the pre-2022 tag (a $100M Q4 fact in the
    10-K, no FY context for that tag) was dropped: the period printed $0 with no partial_coverage and no
    ACQUIRED_IPRD_PARTIAL_PERIOD. Now a positive partial detector fact is kept unless a POSITIVE full-leg detector
    fact was read: the $0 period stays (nothing deducted), the $100M Q4 fact is recorded in partial_coverage and the
    flag names it. A positive exact fact on the other tag still decides the leg (the partial fact is not recorded)."""
    def detect(current):
        f = _facts(expense={2025: current})
        _ytd(f, EXPENSE_OLD, "2025-10-01", "2025-12-31", 100e6, "2026-02-20", form="10-K", fp="FY")
        return E.iprd_detect(f, FY3, fx_rates={}, checks=[_chk("2025-12-31", "fy", current)] if current else [])
    out = detect(0.0)
    rec = _leg(out, "fy", "2025-12-31")
    assert rec is not None and rec["expense"] == 0.0 and rec["deducted"] == 0.0, out["periods"]
    pc = out.get("partial_coverage")
    assert pc and len(pc) == 1 and (pc[0]["period"], pc[0]["window"], pc[0]["tag"]) == ("2025-12-31", "fy", EXPENSE_OLD), pc
    assert [(c["start"], c["end"], c["value"]) for u in pc[0]["units"] for c in u["contexts"]] == [
        ("2025-10-01", "2025-12-31", 100e6)], pc
    fl = [x for x in E.iprd_flags(out) if x.startswith("ACQUIRED_IPRD_PARTIAL_PERIOD: ")]
    assert len(fl) == 1 and "FY2025" in fl[0] and "100,000,000" in fl[0] and EXPENSE_OLD in fl[0], E.iprd_flags(out)
    # a positive exact current-tag fact read the leg: the partial legacy fact is not recorded
    out = detect(20e6)
    rec = _leg(out, "fy", "2025-12-31")
    assert rec["expense"] == 20e6 and rec["deducted"] == 20e6 and "partial_coverage" not in out, out


def _shares_check(period, amount):
    return {"period": period, "window": "fy", "amount": amount, "presentation": "paid_in_shares",
            "source": f"test: the {period} 10-K's supplemental non-cash disclosure: the acquired IPR&D was paid in shares"}


def test_share_paid_residual_is_never_accrued_as_an_unpaid_cash_balance():
    """[Codex review r12, #4324802987, the main agent's shape] A $100M FY2024 expense beside a $0 cash fact (cash
    basis: the cash tag is filed) was accrued whole into the window's unpaid remainder, and an iprd_cash_flow_check
    declaring it paid in shares was consumed without effect (the record is cash-basis), so an unrelated $100M FY2025
    cash-only payment was deducted as its deferred payment — the dilution the share count already carries, charged a
    second time. Now a matching check with presentation paid_in_shares applies to a cash-basis record too: it is
    recorded on the period (cash_flow_check, residual_paid_in_shares) and the residual is not accrued, so the FY2025
    cash stays in ignored_cash_only; with $40M paid in cash only the $40M is deducted. The period's own deduction is
    unchanged (its cash). Without any check the residual still accrues and the later payment is still deducted, with
    deferred_payment_assumption naming the period whose remainder it assumed payable in cash."""
    def detect(expense, cash24, cash25, checks):
        f = _facts(expense={2024: expense}, cash={2024: cash24, 2025: cash25})
        return E.iprd_detect(f, FY3, fx_rates={}, checks=checks)
    out = detect(100e6, 0.0, 100e6, [_shares_check("2024-12-31", 100e6)])
    r24 = _leg(out, "fy", "2024-12-31")
    assert r24["amount_basis"] == "cash_outflow" and r24["deducted"] == 0.0 and r24["excluded"] is None, r24
    assert r24["cash_flow_check"]["presentation"] == "paid_in_shares" and r24["residual_paid_in_shares"] == 100e6, r24
    assert _leg(out, "fy", "2025-12-31") is None and not out["cash_flow_checks_unused"], out
    assert [(c["period"], c["cash"]) for c in out["ignored_cash_only"]] == [("2025-12-31", 100e6)], out["ignored_cash_only"]
    out = detect(100e6, 40e6, 60e6, [_shares_check("2024-12-31", 100e6)])
    assert sum(p["deducted"] for p in out["periods"]) == 40e6 and _leg(out, "fy", "2025-12-31") is None, out["periods"]
    assert _leg(out, "fy", "2024-12-31")["residual_paid_in_shares"] == 60e6
    # no check: accrued as before, the automatic match names its assumption
    out = detect(100e6, 0.0, 100e6, [])
    r25 = _leg(out, "fy", "2025-12-31")
    assert r25["deducted"] == 100e6 and r25.get("deferred_payment"), r25
    assert "FY2024" in r25["deferred_payment_assumption"] and "paid_in_shares" in r25["deferred_payment_assumption"], r25
    assert "residual_paid_in_shares" not in _leg(out, "fy", "2024-12-31")
    # end to end: the share-paid run deducts nothing; make_score's sync check sees the applied check
    n = _ok(_run(_facts(expense={2024: 100e6}, cash={2024: 0.0, 2025: 100e6}),
                 judgment={"iprd_cash_flow_check": [_shares_check("2024-12-31", 100e6)]}, checks=False))
    blk = n["iprd_adjustment"]
    assert blk["total"] == 0.0 and blk["charge_per_share"] == 0.0, blk
    assert n["weighted"] == _plain()["weighted"], "a share-paid charge moved the valuation"



# --- Codex review round 13 of PR #47 ------------------------------------------------------------------------------
def test_a_zero_foreign_currency_fact_converts_to_zero_without_a_rate():
    """[Codex review r13, #4325104002, the main agent's shape] A non-USD acquired-IPR&D fact of exactly 0 with no FX
    rate (none in the FX pass, none fetched) was unconvertible (expense None, excluded non_usd_no_rate), though zero is
    zero at every rate: with a $100M FY2024 expense paid $40M in cash, a FY2025 EUR 0 expense beside a $60M USD cash
    fact deducted nothing for FY2025 (the record was excluded, so the deferred-payment branch never ran) and the $60M
    vanished with no flag — $40M deducted instead of $100M. Now a zero native fact converts to 0.0 without a rate:
    FY2025 reads as a $0 expense, the $60M settles the unpaid remainder, exactly as with the same $0 filed in USD."""
    def detect(unit, rates):
        f = _facts(expense={2024: 100e6}, cash={2024: 40e6, 2025: 60e6})
        _syn_put(f, EXPENSE, unit, _ctx("2025-01-01", "2025-12-31", 0.0, form="10-K", filed="2026-02-20"))
        return E.iprd_detect(f, FY3, fx_rates=rates, checks=[], fx_fetch=lambda c, d: None)
    usd = detect("USD", {})
    assert sum(p["deducted"] for p in usd["periods"]) == 100e6, usd["periods"]
    for out in (detect("EUR", {}), detect("EUR", {"EUR": {"2025-12-31": 1.1}})):
        r25 = _leg(out, "fy", "2025-12-31")
        assert r25["expense"] == 0.0 and r25["excluded"] is None and r25["deducted"] == 60e6, r25
        assert r25.get("deferred_payment"), r25
        assert sum(p["deducted"] for p in out["periods"]) == 100e6, out["periods"]
        assert not out["ignored_cash_only"], out["ignored_cash_only"]
        assert E.iprd_unresolved({"iprd_adjustment": {"periods": out["periods"]}}) is None
    # the pick itself: zero needs no rate; a positive native fact with no rate stays unconvertible
    assert E._iprd_pick({"EUR": (0, "2026-02-20")}, {}, "2025-12-31") == (0.0, "EUR", None, "2026-02-20")
    assert E._iprd_pick({"EUR": (5e6, "2026-02-20")}, {}, "2025-12-31") == (None, "EUR", None, "2026-02-20")
    assert E._iprd_pick({"EUR": (0, "2026-02-20"), "GBP": (5e6, "2026-02-21")}, {}, "2025-12-31") == (
        None, "GBP", None, "2026-02-21"), "a zero unit never hides a positive unconvertible one"


# --- Codex review round 14 of PR #47 ------------------------------------------------------------------------------
def test_a_negative_detector_fact_never_hides_a_deferred_payment():
    """[Codex review r14, #4325437571, the main agent's shape] A negative acquired-IPR&D expense (a reversal) is no
    current-period charge, yet only an exact $0 fact let a period's cash settle the window's unpaid remainder: with a
    $100M FY2024 expense paid $40M in cash, a FY2025 -$5M fact beside a $60M cash payment left the period excluded
    "negative", the $60M was neither matched against the $60M remainder nor listed in ignored_cash_only, and the run
    deducted $40M with no warning. Now a negative detector fact is treated like a $0 one: the FY2025 cash settles the
    remainder (deferred_payment; the record no longer reads excluded, its expense_reversal_note says why), cash past
    the remainder is listed in ignored_cash_only, and with no remainder the whole payment is listed (the record stays
    excluded "negative", nothing deducted)."""
    def detect(cash24, cash25):
        f = _facts(expense={2024: 100e6, 2025: -5e6}, cash={2024: cash24, 2025: cash25})
        return E.iprd_detect(f, FY3, fx_rates={}, checks=[])
    out = detect(40e6, 60e6)
    r25 = _leg(out, "fy", "2025-12-31")
    assert r25["expense"] == -5e6 and r25["excluded"] is None and r25["deducted"] == 60e6, r25
    assert r25.get("deferred_payment") and "reversal" in r25.get("expense_reversal_note", ""), r25
    assert sum(p["deducted"] for p in out["periods"]) == 100e6, out["periods"]
    assert not out["ignored_cash_only"], out["ignored_cash_only"]
    # past the remainder: the rest is listed, as beside a $0 expense
    out = detect(40e6, 80e6)
    assert _leg(out, "fy", "2025-12-31")["deducted"] == 60e6, out["periods"]
    assert [(c["period"], c["cash"]) for c in out["ignored_cash_only"]] == [("2025-12-31", 20e6)], out["ignored_cash_only"]
    # no remainder: nothing deducted, the payment is listed, never dropped without a trace
    out = detect(100e6, 30e6)
    r25 = _leg(out, "fy", "2025-12-31")
    assert r25["excluded"] == "negative" and r25["deducted"] == 0.0, r25
    assert [(c["period"], c["cash"]) for c in out["ignored_cash_only"]] == [("2025-12-31", 30e6)], out["ignored_cash_only"]
    # end to end: the engine deducts the full $100M, as with a $0 FY2025 fact
    n = _ok(_run(_facts(expense={2024: 100e6, 2025: -5e6}, cash={2024: 40e6, 2025: 60e6})))
    assert n["iprd_adjustment"]["total"] == 100e6, n["iprd_adjustment"]


# --- Codex review round 15 of PR #47 ------------------------------------------------------------------------------
R15_RATE = {"EUR": {"2025-12-31": 1.1}}


def test_a_positive_fact_in_any_unit_outranks_a_zero_and_unit_conflicts_are_recorded():
    """[Codex review r15, #4325776467, the main agent's shape] One period, one tag, two units: _iprd_pick returned the
    USD fact whenever one was filed, so a USD 0 beside EUR 100M (EUR rate 1.10) read as no charge — expense 0, the
    matching $110M cash-flow check unused, no flag, the tier published unadjusted. Now a positive fact in any unit
    outranks a zero one: it is converted at the FX pass's rate, else the rate fetched for its own date (fx_fetch, as
    the cash leg does), else the period is gated non_usd_no_rate (ACQUIRED_IPRD_UNCONVERTED). Two positive facts in
    different units that disagree after conversion (by more than $1 and 1%) are both recorded (unit_conflict +
    unit_conflict_note) and the USD one is used; facts that agree record nothing."""
    P = "2025-12-31"
    pick = E._iprd_pick({"USD": (0, "2026-02-20"), "EUR": (100e6, "2026-02-21")}, R15_RATE, P)
    assert pick == (100e6 * 1.1, "EUR", 1.1, "2026-02-21"), pick
    assert E._iprd_pick({"USD": (0, "a"), "EUR": (100e6, "b")}, {}, P) == (None, "EUR", None, "b")
    assert E._iprd_pick({"USD": (0, "a"), "EUR": (100e6, "b")}, {}, P, fx_fetch=lambda c, d: 1.2) == (100e6 * 1.2, "EUR", 1.2, "b")
    # one unit, as before
    assert E._iprd_pick({"USD": (0, "a")}, R15_RATE, P) == (0.0, "USD", None, "a")
    assert E._iprd_pick({"USD": (5e6, "a")}, R15_RATE, P) == (5e6, "USD", None, "a")
    uc = {}
    assert E._iprd_pick({"USD": (5e6, "a"), "EUR": (100e6, "b")}, R15_RATE, P, conflict=uc) == (5e6, "USD", None, "a")
    assert uc["units"]["EUR"]["usd"] == 100e6 * 1.1 and uc["units"]["USD"]["usd"] == 5e6 and uc["used"] == "USD", uc
    uc = {}
    E._iprd_pick({"USD": (110e6, "a"), "EUR": (100e6, "b")}, R15_RATE, P, conflict=uc)
    assert uc == {}, uc

    def detect(exp_units, cash_units=None, rates=R15_RATE, checks=None):
        f = _facts()
        for u, v in exp_units.items():
            _syn_put(f, EXPENSE, u, _ctx("2025-01-01", "2025-12-31", v, form="10-K", filed="2026-02-20"))
        for u, v in (cash_units or {}).items():
            _syn_put(f, CASH, u, _ctx("2025-01-01", "2025-12-31", v, form="10-K", filed="2026-02-20"))
        return E.iprd_detect(f, FY3, fx_rates=rates, checks=checks or [], fx_fetch=lambda c, d: None)
    chk = [{"period": P, "window": "fy", "amount": 100e6 * 1.1, "presentation": "added_back_paid_in_investing",
            "source": "test: the FY2025 10-K cash-flow statement adds it back and pays it in investing"}]
    out = detect({"USD": 0.0, "EUR": 100e6}, checks=chk)
    r = _leg(out, "fy", P)
    assert r["expense"] == 100e6 * 1.1 and r["expense_unit"] == "EUR" and r["deducted"] == 100e6 * 1.1, r
    assert r["cash_flow_check"]["presentation"] == "added_back_paid_in_investing" and not out["cash_flow_checks_unused"], out
    assert r["unit_conflict"][EXPENSE]["units"]["USD"]["usd"] == 0.0 and "unit_conflict_note" in r, r
    # no rate (none fetched): gated, never a silent $0
    out = detect({"USD": 0.0, "EUR": 100e6}, rates={})
    r = _leg(out, "fy", P)
    assert r["excluded"] == "non_usd_no_rate" and r["expense_native"] == 100e6 and r["deducted"] == 0.0, r
    assert any(x.startswith("ACQUIRED_IPRD_UNCONVERTED") for x in E.iprd_flags(out)), E.iprd_flags(out)
    # the cash leg: a USD 0 cash fact never hides the converted EUR payment
    out = detect({"USD": 110e6}, {"USD": 0.0, "EUR": 100e6})
    r = _leg(out, "fy", P)
    assert r["amount_basis"] == "cash_outflow" and r["deducted"] == 100e6 * 1.1 and r["cash_unit"] == "EUR", r
    assert r["unit_conflict"][CASH]["used"] == "EUR", r
    # two positive facts that disagree: both recorded, the USD one used
    out = detect({"USD": 5e6, "EUR": 100e6}, checks=[dict(chk[0], amount=5e6)])
    r = _leg(out, "fy", P)
    assert r["expense"] == 5e6 and r["expense_unit"] == "USD" and r["deducted"] == 5e6, r
    assert r["unit_conflict"][EXPENSE]["units"]["EUR"]["native"] == 100e6 and "reconcile" in r["unit_conflict_note"], r


def test_a_cash_basis_check_the_cash_path_cannot_honor_is_recorded_inapplicable():
    """[Codex review r15, #4325776486, the main agent's shape] A cash-basis period (the cash tag filed beside the
    expense) deducts its cash outflow whatever a check says; a matching iprd_cash_flow_check was marked used before
    the record ignored every cash-basis presentation except paid_in_shares, so a check declaring the $100M paid inside
    operating cash flow (inside_operating_cash_flow) or inside the capex intangible leg (paid_in_intangible_capex) left
    no trace — the period deducted $100M, the check was neither applied nor unused, make_score scored. Now such a check
    is recorded on the period as cash_flow_check_inapplicable {presentation, amount, source, note} (make_score refuses
    it, naming the presentation); paid_in_shares stays honored, added_back_paid_in_investing agrees with the cash tag
    and records nothing."""
    f = _facts(expense={2025: 100e6}, cash={2025: 100e6})
    for pres in ("inside_operating_cash_flow", "paid_in_intangible_capex"):
        chk = {"period": "2025-12-31", "window": "fy", "amount": 100e6, "presentation": pres, "source": "test"}
        out = E.iprd_detect(f, FY3, fx_rates={}, checks=[chk])
        r = _leg(out, "fy", "2025-12-31")
        assert r["amount_basis"] == "cash_outflow" and r["deducted"] == 100e6, r
        assert r["cash_flow_check_inapplicable"]["presentation"] == pres and "cash_flow_check" not in r, r
        assert not out["cash_flow_checks_unused"], out
    for pres in ("added_back_paid_in_investing", "paid_in_shares"):
        chk = {"period": "2025-12-31", "window": "fy", "amount": 100e6, "presentation": pres, "source": "test"}
        r = _leg(E.iprd_detect(f, FY3, fx_rates={}, checks=[chk]), "fy", "2025-12-31")
        assert "cash_flow_check_inapplicable" not in r and r["deducted"] == 100e6, r
    assert r["cash_flow_check"]["presentation"] == "paid_in_shares", r


def ttm_window_decl(value, window="ttm", period=("2026-01-01", "2026-06-30")):
    """A plain base_override declaring the window its pin was built on (Codex review r15): basis_window
    {window: "ttm", ytd_current_period} for a pin built from ttm.json's TTM figures, {window: "fy"} otherwise."""
    bw = {"window": window}
    if window == "ttm":
        bw["ytd_current_period"] = list(period)
    return {"value": value, "source": "test: this run's ttm.json ttm_oe_total over the filer's total economic units",
            "reason": "test: an Up-C filer's per-unit TTM base", "basis_window": bw}


R15_PIN = 1.029


def _r15_window_runs():
    facts, ttm = _ttm_ytd_facts(), _ttm_doc(2.1, 98e6)
    go = lambda d: _ok(_run(facts, extra=["--base-oe-ps", repr(R15_PIN)], ttm=ttm, judgment={"base_override": d}))
    return _cached("r15_windows", lambda: {
        "none": go({k: v for k, v in ttm_window_decl(R15_PIN).items() if k != "basis_window"}),
        "ttm": go(ttm_window_decl(R15_PIN)), "fy": go(ttm_window_decl(R15_PIN, "fy"))})


def test_a_declared_ttm_basis_window_reads_the_current_ytd_leg():
    """[Codex review r15, #4325776506, the main agent's shape] A --base-oe-ps pin built from ttm.json's TTM total on
    another denominator (VNOM's agent_supplied_ttm_override: TTM OE over total units) is not ttm.json's per-share
    figure, so the IPR&D window read only the last 3 FY: a $30M charge in the current YTD — whose cash flows are in
    the scored base — counted as $0. A plain base_override may now carry basis_window {window: "ttm",
    ytd_current_period: ttm.json's}: the engine then reads the current-YTD leg ($20M FY + $30M YTD), recording
    inputs.base_basis_window; {window: "fy"} keeps the FY window; a ttm window whose period is not ttm.json's
    ytd_current_period is refused (BAD_BASE_OVERRIDE, exit 3), except in make_score's override-impact replay. The
    share denominator rule is unchanged (the latest FY diluted count for a pin that is not ttm.json's figure)."""
    runs = _r15_window_runs()
    plain, n, fy = runs["none"], runs["ttm"], runs["fy"]
    assert plain["iprd_adjustment"]["total"] == 20e6 and "base_basis_window" not in plain["inputs"], plain["iprd_adjustment"]
    blk = n["iprd_adjustment"]
    assert blk["total"] == 50e6 and blk["window"]["ttm_current_ytd"] == ["2026-01-01", "2026-06-30"], blk
    assert blk["shares_denominator"] == 100e6 and blk["charge_per_share"] == 50e6 / 100e6, blk
    assert n["inputs"]["base_basis_window"] == {"window": "ttm", "ytd_current_period": ["2026-01-01", "2026-06-30"]}
    assert n["base_oe_per_share"] == plain["base_oe_per_share"] == R15_PIN
    assert fy["iprd_adjustment"]["total"] == 20e6 and fy["inputs"]["base_basis_window"] == {"window": "fy"}, fy["inputs"]
    facts, ttm = _ttm_ytd_facts(), _ttm_doc(2.1, 98e6)
    wrong = ttm_window_decl(R15_PIN, period=("2026-01-01", "2026-03-31"))
    bad = _run(facts, extra=["--base-oe-ps", repr(R15_PIN)], ttm=ttm, judgment={"base_override": wrong})
    assert bad["exit"] == 3 and "BAD_BASE_OVERRIDE" in bad["stdout"] and "basis_window" in bad["stdout"], bad["stdout"][-600:]
    cf = _run_env(facts, ["--base-oe-ps", repr(R15_PIN)], ttm=ttm, judgment={"base_override": wrong},
                  env={"DCF_NO_OVERRIDES": "1", "DCF_IPRD_HOLD": json.dumps({"treatment": "one_time_value_deduction",
                                                                             "charge_per_share": 0.5})}, measure=True)
    assert cf["exit"] == 0, cf["stdout"][-600:]


R16_QS = [("2025-01-01", "2025-03-31", "Q1"), ("2025-04-01", "2025-06-30", "Q2"), ("2025-07-01", "2025-09-30", "Q3"),
          ("2025-10-01", "2025-12-31", "Q4")]


def _r16_quarters(f, tag, unit, value, quarters=R16_QS):
    for s, e, fp in quarters:
        _syn_put(f, tag, unit, {"start": s, "end": e, "val": value, "form": "10-K" if fp == "Q4" else "10-Q",
                                "fp": fp, "fy": 2025, "filed": "2026-02-20" if fp == "Q4" else f"2025-{e[5:7]}-28",
                                "accn": f"0000999016-{s}"})


def test_an_exact_fact_in_one_unit_never_stops_another_unit_from_being_tiled():
    """[Codex review r16, #4331515968] An exact-context fact in ANY unit skipped tiling for every unit: a USD 10-K FY
    fact of exactly 0 beside four EUR three-month facts of EUR 25M (rate 1.10) returned the USD 0 alone, so the EUR
    quarters were neither tiled nor recorded as partial coverage — the period read as no charge (no unit_conflict, no
    flag) and the score published without the EUR 100M acquired-IPR&D charge. Now the units with no exact-context
    fact are tiled and merged beside the exact ones before a unit is picked: the positive tiled EUR $110M outranks
    the USD 0 (round 15's rule), the disagreement is recorded (unit_conflict) and the period awaits its cash-flow check
    like any expense-basis charge; a unit that only partly covers the leg is recorded (partial_coverage,
    ACQUIRED_IPRD_PARTIAL_PERIOD). The cash leg reads the same way. An exact fact still wins for its own unit."""
    P = "2025-12-31"

    def detect(f, checks=None):
        return E.iprd_detect(f, FY3, fx_rates=R15_RATE, checks=checks or [], fx_fetch=lambda c, d: 1.1)
    f = _facts()
    _fy(f, EXPENSE, 2025, 0.0)
    _r16_quarters(f, EXPENSE, "EUR", 25e6)
    out = detect(f)
    r = _leg(out, "fy", P)
    assert r is not None and r["expense"] == 100e6 * 1.1 and r["expense_unit"] == "EUR", r
    assert r["excluded"] == "awaiting_cash_flow_check" and r["deducted"] == 0.0, r
    assert r["unit_conflict"][EXPENSE]["used"] == "EUR" and r["unit_conflict"][EXPENSE]["units"]["USD"]["usd"] == 0.0, r
    assert r["context_basis"] == "aggregated_quarters" and r["aggregated_contexts"][EXPENSE]["unit"] == "EUR", r
    assert any(x.startswith("ACQUIRED_IPRD_UNCONFIRMED") for x in E.iprd_flags(out)), E.iprd_flags(out)
    r = _leg(detect(f, checks=[_chk(P, "fy", 100e6 * 1.1)]), "fy", P)
    assert r["deducted"] == 100e6 * 1.1 and r["excluded"] is None, r
    # only part of the year in EUR (Q3 + Q4): recorded, never a silent $0
    f = _facts()
    _fy(f, EXPENSE, 2025, 0.0)
    _r16_quarters(f, EXPENSE, "EUR", 50e6, quarters=R16_QS[2:])
    out = detect(f)
    pc = out.get("partial_coverage") or []
    assert [(x["period"], x["tag"], [u["unit"] for u in x["units"]]) for x in pc] == [(P, EXPENSE, ["EUR"])], pc
    assert any(x.startswith("ACQUIRED_IPRD_PARTIAL_PERIOD") for x in E.iprd_flags(out)), E.iprd_flags(out)
    # the cash leg: a USD 0 cash fact never hides the EUR quarters' payment
    f = _facts()
    _fy(f, EXPENSE, 2025, 110e6)
    _fy(f, CASH, 2025, 0.0)
    _r16_quarters(f, CASH, "EUR", 25e6)
    r = _leg(detect(f), "fy", P)
    assert r["amount_basis"] == "cash_outflow" and r["deducted"] == 100e6 * 1.1 and r["cash_unit"] == "EUR", r
    assert r["unit_conflict"][CASH]["used"] == "EUR", r
    # an exact fact still wins for its own unit (round 11): USD quarters never replace the USD FY fact
    f = _facts()
    _fy(f, EXPENSE, 2025, 20e6)
    _r16_quarters(f, EXPENSE, "USD", 25e6)
    r = _leg(detect(f, checks=[_chk(P, "fy", 20e6)]), "fy", P)
    assert r["expense"] == 20e6 and r["deducted"] == 20e6 and "context_basis" not in r and "unit_conflict" not in r, r


def test_a_unit_conflict_on_a_cash_only_deferred_payment_is_kept():
    """[Codex review r16, #4331515973] The cash tag's unit conflict was attached only to the record
    iprd_period_record built; a cash-only period (no expense fact) gets None there and its record is built later
    (a deferred payment of the window's unpaid remainder), so the conflict was dropped: after FY2023's $100M expense
    with $40M paid ($60M unpaid), FY2024's cash tag filed as USD 5M beside EUR 100M ($110M at 1.10) deducted $5M with
    no unit_conflict. Now every record the period ends with carries the conflict (and its note), and so does a
    cash-only entry the period lists in ignored_cash_only."""
    f = _facts()
    _fy(f, EXPENSE, 2023, 100e6)
    _fy(f, CASH, 2023, 40e6)
    _fy(f, CASH, 2024, 5e6)
    _syn_put(f, CASH, "EUR", _ctx("2024-01-01", "2024-12-31", 100e6, form="10-K", filed="2025-02-20"))
    rates = {"EUR": {"2024-12-31": 1.1}}
    out = E.iprd_detect(f, FY3, fx_rates=rates, checks=[], fx_fetch=lambda c, d: None)
    r = _leg(out, "fy", "2024-12-31")
    assert r["deducted"] == 5e6 and r.get("deferred_payment"), r
    assert r["unit_conflict"][CASH]["used"] == "USD" and r["unit_conflict"][CASH]["units"]["EUR"]["usd"] == 100e6 * 1.1, r
    assert "reconcile" in r["unit_conflict_note"], r
    # beyond the remainder: the rest listed in ignored_cash_only carries it too
    f = _facts()
    _fy(f, EXPENSE, 2023, 100e6)
    _fy(f, CASH, 2023, 40e6)
    _fy(f, CASH, 2024, 70e6)
    _syn_put(f, CASH, "EUR", _ctx("2024-01-01", "2024-12-31", 100e6, form="10-K", filed="2025-02-20"))
    out = E.iprd_detect(f, FY3, fx_rates=rates, checks=[], fx_fetch=lambda c, d: None)
    r = _leg(out, "fy", "2024-12-31")
    assert r["deducted"] == 60e6 and r["unit_conflict"][CASH]["used"] == "USD", r
    co = [x for x in out["ignored_cash_only"] if x["period"] == "2024-12-31"]
    assert len(co) == 1 and co[0]["cash"] == 10e6 and co[0]["unit_conflict"][CASH]["used"] == "USD", co


# --- Codex review round 17 of PR #47 ------------------------------------------------------------------------------
def _r17_pre_window_eur():
    """_pre_window's shape (FY2022 $40M expensed, $10M paid) whose FY2024 cash-tag-only payment is filed as USD 30M
    beside EUR 100M ($110M at 1.10): a unit conflict on a payment only a declaration can deduct."""
    f = _facts(expense={2022: 40e6}, cash={2022: 10e6, 2024: 30e6})
    _syn_put(f, CASH, "EUR", _ctx("2024-01-01", "2024-12-31", 100e6, form="10-K", filed="2025-02-20"))
    return f


def test_a_unit_conflict_on_a_declared_pre_window_payment_is_kept():
    """[Codex review r17, #4332171616] A cash-tag-only payment of a charge expensed BEFORE the window carries its
    period's unit conflict in ignored_cash_only (round 16), but the record iprd_apply_deferred built when a
    declaration promoted it copied only the cash fields and the entry was removed: FY2024 filed USD 30M beside EUR
    100M ($110M) deducted the declared $30M with no unit_conflict and no reconcile note anywhere in the run. Now the
    promoted record carries the entry's unit_conflict and unit_conflict_note (a rest left listed keeps them too)."""
    rates = {"EUR": {"2024-12-31": 1.1}}
    decl = deferred(period="2024-12-31", amount=30e6, first="2022-12-31", source=PRE_SRC, deal="Old Bio", contingent=PRE_CT)
    out = E.iprd_detect(_r17_pre_window_eur(), FY3, fx_rates=rates, checks=[], fx_fetch=lambda c, d: None)
    assert out["periods"] == [] and out["ignored_cash_only"][0]["unit_conflict"][CASH]["used"] == "USD", out
    for amt, rest in ((30e6, None), (20e6, 10e6)):
        iprd = copy.deepcopy(out)
        ref, _ = E.iprd_apply_deferred(iprd, [dict(decl, amount=amt)], FY3, _r17_pre_window_eur())
        assert ref == [], ref
        r = _leg(iprd, "fy", "2024-12-31")
        assert r["deducted"] == amt and r["recurrence_excluded"] == "deferred_payment_of", r
        assert r["unit_conflict"][CASH]["units"]["EUR"]["usd"] == 100e6 * 1.1 and "reconcile" in r["unit_conflict_note"], r
        co = iprd["ignored_cash_only"]
        assert [c["cash"] for c in co] == ([rest] if rest else []) and all("unit_conflict" in c for c in co), co
    n = _ok(_run_fx(_r17_pre_window_eur(), rates, judgment={"iprd_deferred_payment": [decl]}))
    p24 = [p for p in n["iprd_adjustment"]["periods"] if p["period"] == "2024-12-31"]
    assert len(p24) == 1 and p24[0]["deducted"] == 30e6 and p24[0]["unit_conflict"][CASH]["used"] == "USD", p24


def test_a_zero_tiling_never_hides_another_units_positive_partial_facts():
    """[Codex review r17, #4332171623] iprd_tile dropped every unit's partial facts once ANY unit tiled the leg, even
    to $0: four USD three-month facts of 0 beside one EUR Q4 fact of 100M read FY2025 as a $0 charge with no
    partial_coverage and no flag, while an exact USD 0 FY fact beside the same EUR fact was flagged (round 16). Now
    the partial facts are kept whenever no unit tiles the leg to a positive value: the $0 USD tiling is still the
    record, and the EUR fact is recorded (partial_coverage, ACQUIRED_IPRD_PARTIAL_PERIOD). A positive tiling still
    reads the leg (no partial coverage beside it)."""
    P = "2025-12-31"

    def detect(f):
        return E.iprd_detect(f, FY3, fx_rates=R15_RATE, checks=[], fx_fetch=lambda c, d: 1.1)
    for exact_zero in (True, False):
        f = _facts()
        if exact_zero:
            _fy(f, EXPENSE, 2025, 0.0)
        else:
            _r16_quarters(f, EXPENSE, "USD", 0.0)
        _r16_quarters(f, EXPENSE, "EUR", 100e6, quarters=R16_QS[3:])
        out = detect(f)
        pc = (out or {}).get("partial_coverage") or []
        assert [(x["period"], x["tag"], [u["unit"] for u in x["units"]]) for x in pc] == [(P, EXPENSE, ["EUR"])], (exact_zero, out)
        assert any(x.startswith("ACQUIRED_IPRD_PARTIAL_PERIOD") for x in E.iprd_flags(out)), E.iprd_flags(out)
    by_unit, ctx, part = E.iprd_tile(f, EXPENSE, "2025-01-01", P)
    assert by_unit["USD"][0] == 0 and part and [u["unit"] for u in part] == ["EUR"], (by_unit, part)
    # a positive tiling reads the leg: the other unit's partial fact is no missing charge
    f = _facts()
    _r16_quarters(f, EXPENSE, "USD", 5e6)
    _r16_quarters(f, EXPENSE, "EUR", 100e6, quarters=R16_QS[3:])
    by_unit, ctx, part = E.iprd_tile(f, EXPENSE, "2025-01-01", P)
    assert by_unit["USD"][0] == 20e6 and part is None, (by_unit, part)
    assert not (detect(f) or {}).get("partial_coverage"), detect(f)


R17_SRC = ("SYN 10-K FY2022 (0000999001-23-000005) Note 4 'Asset acquisition', p. 64: Old Bio acquired IPR&D $70.0 "
           "million expensed, $10.0 million paid at closing, $60.0 million of deferred consideration payable in 2024")
R17_CT = {"value": 60e6, "source": "SYN 10-K FY2022 (0000999001-23-000005) Note 4, p. 64: $60.0 million deferred consideration"}


def _r17_split(entries=None):
    """FY2022 (before the window): $70M expensed, $10M paid. FY2023: $100M expensed, $60M paid ($40M unpaid). FY2024:
    $100M on the cash tag only — $40M settles the window's remainder automatically, the $60M rest may pay FY2022's
    deal."""
    facts = _facts(expense={2022: 70e6, 2023: 100e6}, cash={2022: 10e6, 2023: 60e6, 2024: 100e6})
    return _run(facts, judgment={"iprd_deferred_payment": entries} if entries is not None else None)


def test_a_declaration_claims_the_residual_beside_an_automatic_settlement():
    """[Codex review r17, #4332171628] A cash-only payment split between the window's unpaid remainder (settled
    automatically) and a rest listed in ignored_cash_only for a pre-window charge: ACQUIRED_IPRD_UNMATCHED_PAYMENT told
    the worker to declare the rest, but iprd_apply_deferred took the automatic settlement as the period's whole
    charge — a $60M declaration was refused ("more than the period's charge 40,000,000") and a $30M one only relabeled
    the automatic $40M (nothing more deducted, the rest still flagged). Now a declaration whose first charge lies
    before the window claims that residual (and only it) on top of the automatic settlement, within the residual and
    the deal's contingent_total: the period deducts both, the automatic part keeps its own record
    (automatic_settlement, its deferred_payment note), the declared part is recorded (declared_residual,
    deferred_payment_of) and any rest stays listed. A declaration first charged inside the window still names the
    automatic settlement, as before."""
    plain = _plain()
    n = _ok(_r17_split())
    b = n["iprd_adjustment"]
    assert b["total"] == 100e6 and [(c["period"], c["cash"]) for c in b["ignored_cash_only"]] == [("2024-12-31", 60e6)], b
    assert flags(n, "ACQUIRED_IPRD_UNMATCHED_PAYMENT")
    decl = deferred(period="2024-12-31", amount=60e6, first="2022-12-31", source=R17_SRC, deal="Old Bio", contingent=R17_CT)
    m = _ok(_r17_split([decl]))
    mb = m["iprd_adjustment"]
    p24 = _leg(mb, "fy", "2024-12-31")
    assert mb["total"] == 160e6 and p24["deducted"] == 100e6 and p24["amount"] == 100e6, p24
    assert p24["automatic_settlement"] == 40e6 and p24["declared_residual"] == 60e6 and p24.get("deferred_payment"), p24
    assert [(x["deal"], x["amount"], x["first_charge_evidence"]) for x in p24["deferred_payment_of"]] == [
        ("Old Bio", 60e6, "companyfacts_expense_fact")], p24
    assert p24["recurrence_excluded"] == "deferred_payment_of" and not mb["ignored_cash_only"], mb
    assert not flags(m, "ACQUIRED_IPRD_UNMATCHED_PAYMENT") and not mb["recurrent"], mb
    _assert_base_untouched(m, plain)
    # part of the residual: deducted on top, the rest stays listed and flagged
    k = _ok(_r17_split([dict(decl, amount=30e6)]))
    kb = k["iprd_adjustment"]
    assert kb["total"] == 130e6 and [c["cash"] for c in kb["ignored_cash_only"]] == [30e6], kb
    assert _leg(kb, "fy", "2024-12-31")["automatic_settlement"] == 40e6 and flags(k, "ACQUIRED_IPRD_UNMATCHED_PAYMENT")
    # more than the residual, or past the deal's contingent_total: refused
    _refused(_r17_split([dict(decl, amount=70e6, deferred_payment_of=dict(decl["deferred_payment_of"],
                                                                           contingent_total=dict(R17_CT, value=80e6)))]),
             "more than the period's")
    _refused(_r17_split([dict(decl, deferred_payment_of=dict(decl["deferred_payment_of"],
                                                              contingent_total=dict(R17_CT, value=50e6)))]),
             "contingent_total")
    # beside an in-window deal naming the automatic settlement: both apply, each against its own amount
    both = _ok(_r17_split([decl, deferred(period="2024-12-31", amount=40e6, deal="Window Bio")]))
    q = _leg(both["iprd_adjustment"], "fy", "2024-12-31")
    assert both["iprd_adjustment"]["total"] == 160e6 and q["deducted"] == 100e6, q
    assert sorted((x["deal"], x["amount"], x["first_charge_evidence"]) for x in q["deferred_payment_of"]) == [
        ("Old Bio", 60e6, "companyfacts_expense_fact"), ("Window Bio", 40e6, "window_record")], q


def test_aggregated_contexts_name_the_unit_the_period_was_read_from():
    """[Codex review r18, #4332318423] When several units tile a leg, aggregated_contexts recorded the USD tiling
    whenever one existed, whatever unit _iprd_pick then used: four USD 0 quarters beside four EUR 25M quarters (rate
    1.10) read expense $110M in EUR (unit_conflict used EUR) while aggregated_contexts named the USD zero facts — the
    provenance pointed at facts that did not produce the charge. Now aggregated_contexts holds the contexts of the
    unit the period's figure was read from, and every other tiled unit is kept under
    aggregated_contexts_other_units {tag: {unit: contexts}}."""
    P = "2025-12-31"
    f = _facts()
    _r16_quarters(f, EXPENSE, "USD", 0.0)
    _r16_quarters(f, EXPENSE, "EUR", 25e6)
    out = E.iprd_detect(f, FY3, fx_rates=R15_RATE, fx_fetch=lambda c, d: 1.1)
    r = _leg(out, "fy", P)
    q = [[s, e] for s, e, _ in R16_QS]
    assert r["expense_unit"] == "EUR" and r["unit_conflict"][EXPENSE]["used"] == "EUR", r
    assert r["context_basis"] == "aggregated_quarters", r
    assert r["aggregated_contexts"] == {EXPENSE: {"unit": "EUR", "contexts": q}}, r
    assert r["aggregated_contexts_other_units"] == {EXPENSE: {"USD": q}}, r
    # one tiled unit only: no other-units key (the round 11 shape is unchanged)
    f = _facts()
    _r16_quarters(f, EXPENSE, "USD", 25e6)
    r = _leg(E.iprd_detect(f, FY3, fx_rates=R15_RATE), "fy", P)
    assert r["aggregated_contexts"] == {EXPENSE: {"unit": "USD", "contexts": q}}, r
    assert "aggregated_contexts_other_units" not in r, r


def test_original_filing_years_reach_a_53_week_years_start():
    """[Codex review r18, #4332318439] The allowed accession years started at (first charged period - 364 days).year:
    a 53-week fiscal year 2019-12-30..2021-01-03 started in 2019, but 2021-01-03 - 364 days is 2020-01-05, so an 8-K
    filed 2019-12-30 (-19-) — the original acquisition filing, inside that fiscal year — was refused
    (BAD_IPRD_DEFERRED_PAYMENT). The start year is now read from the annual context filed for that fiscal year
    (iprd_fy_starts) when companyfacts has one, else from the end less 380 days (the longest fiscal year the engine
    reads)."""
    facts = {"facts": {"us-gaap": {EXPENSE: {"units": {"USD": [_fy_fact("2019-12-30", "2021-01-03", 5e6)]}}}}}
    assert 2019 in E.iprd_original_filing_years("2021-01-03", facts), list(E.iprd_original_filing_years("2021-01-03", facts))
    assert 2019 in E.iprd_original_filing_years("2021-01-03"), list(E.iprd_original_filing_years("2021-01-03"))
    win = ["2023-01-01", "2023-12-31", "2024-12-29"]
    for yy, ok in ((19, True), (20, True), (22, True), (18, False)):
        iprd = {"periods": [_rec("2024-12-29", 20e6)]}
        ref, unused = E.iprd_apply_deferred(iprd, [deferred(period="2024-12-29", first="2021-01-03", source=_src(yy))],
                                            win, facts)
        assert (not ref) == ok and unused == [], (yy, ref)
    # a calendar filer's filed annual context keeps the start year exact (not loosened by the 380-day fallback)
    facts = {"facts": {"us-gaap": {EXPENSE: {"units": {"USD": [_fy_fact("2024-01-01", "2024-12-31", 5e6)]}}}}}
    assert list(E.iprd_original_filing_years("2024-12-31", facts)) == [2024, 2025]



# --- Codex review round 19 of PR #47 ------------------------------------------------------------------------------
def _r19_facts(prior_start, prior_end, window):
    """A filer that expensed $40M of acquired IPR&D in the fiscal year (prior_start, prior_end) before the window and
    paid $10M of it then; the window's FYs (window: [(start, end)], oldest first) carry a $30M payment of the rest in
    the second FY on the cash tag alone ($0 cash in the other FYs) and annual revenue contexts (the filer's FY
    periods)."""
    def c(s, e, v, filed):
        return {"start": s, "end": e, "val": v, "form": "10-K", "fp": "FY", "fy": int(e[:4]), "filed": filed,
                "accn": "0000999001-" + filed[2:4] + "-000005"}
    filed = lambda e: f"{int(e[:4]) + 1}-02-20"
    return {"facts": {"us-gaap": {
        EXPENSE: {"units": {"USD": [c(prior_start, prior_end, 40e6, "2023-03-20")]}},
        CASH: {"units": {"USD": [c(prior_start, prior_end, 10e6, "2023-03-20")]
                         + [c(s, e, 30e6 if i == 1 else 0.0, filed(e)) for i, (s, e) in enumerate(window)]}},
        "Revenues": {"units": {"USD": [c(prior_start, prior_end, 1e9, "2023-03-20")]
                               + [c(s, e, 1e9, filed(e)) for s, e in window]}}}}}


def test_a_charge_in_the_fiscal_year_before_a_short_transition_year_is_before_the_window():
    """[Codex review r19, #4332459839] A first charge counted as before the window only when it ended at least 357 days
    before the oldest window FY end, but the engine reads any 330-380-day annual context as a fiscal year: a filer
    moving its year end from January 31 to December 31 files a 333-day transition year (2023-02-01..2023-12-31),
    so its prior FY end (2023-01-31) lies 334 days before the oldest window FY end and was read as inside the window.
    The $40M FY-Jan-2023 charge was then no pre-window charge: the $30M FY2024 cash-only payment of its rest was
    dropped with no trace (no ignored_cash_only entry, no ACQUIRED_IPRD_UNMATCHED_PAYMENT) and its declaration was
    refused (BAD_IPRD_DEFERRED_PAYMENT, "names no acquired-IPR&D charge in this run's window"). A first charge is now
    before the window when it ends before the oldest window FY STARTS (iprd_window_start: the start of its filed
    annual context, iprd_fy_starts, else the day after the filer's prior fiscal-year end, else its end less 380
    days): the payment is listed and flagged undeclared, and
    deducted once, cash basis, outside the recurrence count, when declared — exactly as for a calendar filer."""
    src = "SYN 10-K (0000999001-23-000005) Note 4 'Asset acquisition', p. 64: Old Bio IPR&D $40.0 million expensed"
    ct = {"value": 30e6, "source": "SYN 10-K (0000999001-23-000005) Note 4, p. 64: $30.0 million deferred consideration"}
    cases = (("2022-01-01", "2022-12-31", [("2023-01-01", "2023-12-31"), ("2024-01-01", "2024-12-31"),
                                           ("2025-01-01", "2025-12-31")]),    # the calendar control
             ("2022-02-01", "2023-01-31", [("2023-02-01", "2023-12-31"), ("2024-01-01", "2024-12-31"),
                                           ("2025-01-01", "2025-12-31")]))    # a 333-day transition year
    for prior_start, prior_end, window in cases:
        facts = _r19_facts(prior_start, prior_end, window)
        fyp = [e for _, e in window]
        assert prior_end in E.iprd_fy_period_ends(facts, fyp), prior_end   # the filer's own prior FY end
        assert E.iprd_pre_window_charges(facts, fyp[0]) == [prior_end], (prior_end, E.iprd_pre_window_charges(facts, fyp[0]))
        iprd = E.iprd_detect(facts, fyp, checks=[])
        co = [x for x in (iprd or {}).get("ignored_cash_only") or [] if x["period"] == "2024-12-31"]
        assert co and co[0]["cash"] == 30e6 and co[0]["pre_window_charges"] == [prior_end], (prior_end, iprd)
        decl = {"period": "2024-12-31", "window": "fy", "amount": 30e6,
                "deferred_payment_of": {"deal": "Old Bio", "first_charged_period": prior_end, "source": src,
                                        "contingent_total": ct}}
        refused, rolled = E.iprd_apply_deferred(iprd, [decl], fyp, facts)
        assert refused == [] and rolled == [], (prior_end, refused)
        rec = [p for p in iprd["periods"] if p["period"] == "2024-12-31"]
        assert (len(rec) == 1 and rec[0]["amount"] == 30e6 and rec[0]["amount_basis"] == "cash_outflow"
                and rec[0]["recurrence_excluded"] == "deferred_payment_of"), (prior_end, rec)
    # a charge inside the transition year itself is still inside the window, and with no fiscal period known around
    # the oldest FY the start falls back to its end less 380 days (the longest fiscal year read)
    assert E.iprd_window_start(_r19_facts(*cases[1]), ["2023-12-31"]) == E.datetime.date(2023, 2, 1)
    assert E.iprd_window_start({"facts": {}}, ["2023-12-31"]) == E.datetime.date(2022, 12, 16)
    # with no annual context for the oldest FY, the day after the filer's prior fiscal-year end (a filed annual one)
    prior_only = {"facts": {"us-gaap": {EXPENSE: {"units": {"USD": [_fy_fact("2021-01-31", "2022-01-29", 5e6)]}}}}}
    assert E.iprd_window_start(prior_only, ["2023-01-28"]) == E.datetime.date(2022, 1, 30)
    assert E.iprd_pre_window_charges(prior_only, "2023-01-28") == ["2022-01-29"]
    assert E.iprd_pre_window_charges({"facts": {"us-gaap": {EXPENSE: {"units": {"USD": [
        _fy_fact("2023-02-01", "2023-06-30", 5e6)]}}}}}, "2023-12-31") == []



# --- Codex review round 20 of PR #47 ------------------------------------------------------------------------------
def _r20_facts(exp24=100e6, exp24_unit="USD", cash24=40e6, cash25=60e6, cash25_unit="USD", neg25=-5e6, prior=None):
    """FY2024 charge (exp24 in exp24_unit, cash24 USD paid); FY2025 a negative detector fact in EUR (no FX rate) beside
    cash25 in cash25_unit; prior: a FY2021 USD expense (a charge before the window)."""
    f = _facts(expense={2021: prior} if prior is not None else None, cash={2024: cash24})
    _syn_put(f, EXPENSE, exp24_unit, _ctx("2024-01-01", "2024-12-31", exp24, form="10-K", filed="2025-02-20"))
    _syn_put(f, EXPENSE, "EUR", _ctx("2025-01-01", "2025-12-31", neg25, form="10-K", filed="2026-02-20"))
    if cash25 is not None:
        _syn_put(f, CASH, cash25_unit, _ctx("2025-01-01", "2025-12-31", cash25, form="10-K", filed="2026-02-20"))
    return f


def test_an_unconvertible_negative_detector_fact_is_a_reversal_not_an_unconverted_charge():
    """[Codex review r20, #4332651259] A detector fact the run cannot convert (no FX rate, even fetched) is classified
    by its native sign before the unconverted gate: exactly 0 converts to 0 (round 13), a positive one gates as
    ACQUIRED_IPRD_UNCONVERTED, and a NEGATIVE one is a reversal — no current-period charge, as a converted negative fact
    is (round 14). Before, a -EUR 5M FY2025 fact read excluded non_usd_no_rate with expense None, which round 14's
    no-charge test (it read only the USD expense) never matched and no gate caught (they key on a POSITIVE native
    figure): a $100M FY2024 charge paid $40M left the FY2025 $60M payment unmatched, unlisted and ungated, and the run
    published a $40M deduction. Now the record reads excluded "negative" (amount 0, its expense_native kept), so the
    cash settles the remainder (deferred_payment, expense_reversal_note naming the native figure: $100M in all), an
    unconvertible payment beside it is gated (cash_native), cash beside it with no remainder is listed (with the
    pre-window charge it may settle), and cash after a charge whose remainder is unknown is gated
    (unconverted_remainder_of) — each exactly as for a USD -5M fact."""
    nofx = lambda c, d: None

    def detect(f, rates=None):
        return E.iprd_detect(f, FY3, fx_rates=rates or {}, checks=[], fx_fetch=nofx)
    # A: the finding — the $60M settles the $60M remainder, as with a USD -5M or a converted EUR -5M fact
    out = detect(_r20_facts())
    r25 = _leg(out, "fy", "2025-12-31")
    assert r25["expense"] is None and r25["expense_native"] == -5e6 and r25["expense_unit"] == "EUR", r25
    assert r25["excluded"] is None and r25["deducted"] == 60e6 and r25.get("deferred_payment"), r25
    assert "reversal" in r25.get("expense_reversal_note", "") and "EUR" in r25["expense_reversal_note"], r25
    assert sum(p["deducted"] for p in out["periods"]) == 100e6 and not out["ignored_cash_only"], out
    assert E.iprd_unresolved({"iprd_adjustment": {"periods": out["periods"]}}) is None
    conv = detect(_r20_facts(), {"EUR": {"2025-12-31": 1.1}})
    assert sum(p["deducted"] for p in conv["periods"]) == 100e6, conv["periods"]
    # with no remainder the record stays excluded "negative" (nothing deducted)
    out = detect(_r20_facts(cash24=100e6, cash25=30e6))
    r25 = _leg(out, "fy", "2025-12-31")
    assert r25["excluded"] == "negative" and r25["deducted"] == 0.0 and r25["amount"] == 0.0, r25
    assert [(c["period"], c["cash"]) for c in out["ignored_cash_only"]] == [("2025-12-31", 30e6)], out
    assert "negative (reversal)" in out["ignored_cash_only"][0]["note"], out["ignored_cash_only"]
    # B: an unconvertible payment beside it, after the $60M remainder: gated with its native amount
    out = detect(_r20_facts(cash25_unit="EUR"))
    r25 = _leg(out, "fy", "2025-12-31")
    assert r25["excluded"] == "non_usd_no_rate" and r25.get("cash_native") == 60e6, r25
    assert "non_usd_no_rate" in (E.iprd_unresolved({"iprd_adjustment": {"periods": out["periods"]}}) or ""), out
    # C: no remainder, a FY2021 charge before the window: the payment is listed with it (UNMATCHED_PAYMENT) ...
    f = _r20_facts(cash24=100e6, cash25=30e6, prior=50e6)
    out = detect(f)
    co = [c for c in out["ignored_cash_only"] if c["period"] == "2025-12-31"]
    assert co and co[0]["cash"] == 30e6 and co[0].get("pre_window_charges") == ["2021-12-31"], out["ignored_cash_only"]
    assert any(x.startswith("ACQUIRED_IPRD_UNMATCHED_PAYMENT") for x in E.iprd_flags(dict(out, total=None))), out
    # ... and a declaration claims it (the record reads the reversal, deducted once)
    decl = {"period": "2025-12-31", "window": "fy", "amount": 30e6,
            "deferred_payment_of": {"deal": "Old Bio", "first_charged_period": "2021-12-31",
                                    "source": "SYN 10-K (0000999001-22-000005) Note 4, p. 64: Old Bio IPR&D expensed",
                                    "contingent_total": {"value": 30e6, "source": "SYN 10-K (0000999001-22-000005) "
                                                         "Note 4, p. 64: $30.0 million deferred consideration"}}}
    refused, rolled = E.iprd_apply_deferred(out, [decl], FY3, f)
    assert refused == [] and rolled == [], refused
    r25 = _leg(out, "fy", "2025-12-31")
    assert r25["deducted"] == 30e6 and r25["excluded"] is None and "reversal" in r25.get("expense_reversal_note", ""), r25
    # D: after a GBP charge the run cannot convert (its remainder unknown): the USD payment is gated
    out = detect(_r20_facts(exp24_unit="GBP"))
    r25 = _leg(out, "fy", "2025-12-31")
    assert r25["excluded"] == "non_usd_no_rate" and r25.get("unconverted_remainder_of") == ["2024-12-31"], r25
    assert E.iprd_unresolved({"iprd_adjustment": {"periods": out["periods"]}}), out["periods"]
    # a positive unconvertible fact still gates; a negative unconvertible CASH fact beside a USD expense is noted
    out = detect(_r20_facts(neg25=5e6, cash25=None))
    assert _leg(out, "fy", "2025-12-31")["excluded"] == "non_usd_no_rate", out["periods"]
    ff = _facts(expense={2025: 100e6})
    _syn_put(ff, CASH, "EUR", _ctx("2025-01-01", "2025-12-31", -90e6, form="10-K", filed="2026-02-20"))
    r25 = _leg(detect(ff), "fy", "2025-12-31")
    assert r25["amount_basis"] == "expense" and "negative" in r25.get("cash_sign_note", ""), r25
    # end to end: the engine deducts the full $100M
    n = _ok(_run_fx(_r20_facts(), {"EUR": {"1999-12-31": 1.0}}))
    assert n["iprd_adjustment"]["total"] == 100e6 and E.iprd_unresolved(n) is None, n["iprd_adjustment"]


# --- Codex review round 21 of PR #47 ------------------------------------------------------------------------------
def _r21_facts():
    """FY2024: a EUR 100M acquired-IPR&D expense with no FX rate (even fetched) beside a $40M USD cash outflow (the
    cash-basis path: the cash is the amount); FY2025: a $25M cash-only fact."""
    f = _facts(cash={2024: 40e6, 2025: 25e6})
    _syn_put(f, EXPENSE, "EUR", _ctx("2024-01-01", "2024-12-31", 100e6, form="10-K", filed="2025-02-20"))
    return f


def _r21_check(amount=100e6, unit="EUR", presentation="paid_in_shares"):
    c = {"period": "2024-12-31", "window": "fy", "amount": amount, "presentation": presentation,
         "source": "SYN 10-K FY2024 (0000999001-25-000003) R7: 'Acquired IPR&D paid in shares' non-cash add-back"}
    if unit is not None:
        c["unit"] = unit
    return c


def test_a_native_paid_in_shares_check_matches_an_unconvertible_expense():
    """[Codex review r21, #4332782414] A cash-basis period whose expense has no FX rate (EUR 100M beside a $40M USD
    cash outflow) matched its iprd_cash_flow_check against the USD expense, which is None there, so every check —
    the correctly declared EUR 100M paid_in_shares one included — was recorded cash_flow_check_mismatch (make_score
    refuses it), the residual stayed unknown in USD and the FY2025 $25M cash-only fact was gated non_usd_no_rate
    against it: no declaration could ever close the period. Now, when the USD expense is None, the check is compared
    with the native detector figure AND its unit (the entry names `unit`, here "EUR"): a matching paid_in_shares check
    is applied (cash_flow_check, with its unit), the residual is recorded paid in shares (unknown in USD:
    residual_paid_in_shares_unknown_usd) and never enters the unknown remainder, so the later cash is listed in
    ignored_cash_only and nothing is unresolved. The $40M cash is still deducted. An amount without the unit, the USD
    cash, or another native figure stays a mismatch whose note names the native figure and unit."""
    nofx = lambda c, d: None

    def detect(checks):
        return E.iprd_detect(_r21_facts(), FY3, fx_rates={}, checks=checks, fx_fetch=nofx)
    out = detect([_r21_check()])
    r24, r25 = _leg(out, "fy", "2024-12-31"), _leg(out, "fy", "2025-12-31")
    assert r24["expense"] is None and r24["expense_native"] == 100e6 and r24["expense_unit"] == "EUR", r24
    assert r24["amount_basis"] == "cash_outflow" and r24["deducted"] == 40e6 and r24["excluded"] is None, r24
    assert "cash_flow_check_mismatch" not in r24, r24
    assert r24["cash_flow_check"] == {"presentation": "paid_in_shares", "amount": 100e6, "unit": "EUR",
                                      "source": _r21_check()["source"]}, r24
    assert r24.get("residual_paid_in_shares_unknown_usd") is True and "EUR" in r24.get("residual_note", ""), r24
    assert r25 is None, r25
    assert [(c["period"], c["cash"]) for c in out["ignored_cash_only"]] == [("2025-12-31", 25e6)], out["ignored_cash_only"]
    assert out["cash_flow_checks_unused"] == [], out["cash_flow_checks_unused"]
    assert E.iprd_unresolved({"iprd_adjustment": {"periods": out["periods"]}}) is None, out["periods"]
    assert sum(p["deducted"] for p in out["periods"]) == 40e6, out["periods"]
    # not matched: the native amount with no unit, the USD cash, another native figure, the wrong unit
    for bad in (_r21_check(unit=None), _r21_check(amount=40e6, unit=None), _r21_check(amount=90e6),
                _r21_check(unit="GBP"), _r21_check(amount=40e6, unit="USD")):
        o = detect([bad])
        p24, p25 = _leg(o, "fy", "2024-12-31"), _leg(o, "fy", "2025-12-31")
        mm = p24.get("cash_flow_check_mismatch")
        assert mm and mm["declared_amount"] == bad["amount"] and p24.get("cash_flow_check") is None, (bad, p24)
        assert "100,000,000 EUR" in mm["note"] and "unit" in mm["note"], (bad, mm)
        assert p25["excluded"] == "non_usd_no_rate" and p25.get("unconverted_remainder_of") == ["2024-12-31"], p25
    # an added_back_paid_in_investing check matched natively says nothing of the residual: still unknown, still gated
    o = detect([_r21_check(presentation="added_back_paid_in_investing")])
    assert "cash_flow_check_mismatch" not in _leg(o, "fy", "2024-12-31"), o["periods"]
    assert _leg(o, "fy", "2025-12-31")["excluded"] == "non_usd_no_rate", o["periods"]
    # a converted expense still matches the USD figure only (a unit, when named, must be USD)
    conv = E.iprd_detect(_r21_facts(), FY3, fx_rates={"EUR": {"2024-12-31": 1.1}}, fx_fetch=nofx,
                         checks=[_r21_check(amount=110e6, unit=None)])
    c24 = _leg(conv, "fy", "2024-12-31")
    assert abs(c24["expense"] - 110e6) < 1 and c24["cash_flow_check"]["presentation"] == "paid_in_shares", c24
    assert abs(c24["residual_paid_in_shares"] - 70e6) < 1, c24
    conv = E.iprd_detect(_r21_facts(), FY3, fx_rates={"EUR": {"2024-12-31": 1.1}}, fx_fetch=nofx,
                         checks=[_r21_check(amount=110e6, unit="EUR")])
    assert _leg(conv, "fy", "2024-12-31").get("cash_flow_check_mismatch"), conv["periods"]
    # the entry's unit, when present, is a non-empty string
    assert E.iprd_cash_flow_check_entry_ok(_r21_check())
    assert not E.iprd_cash_flow_check_entry_ok(_r21_check(unit=""))
    assert not E.iprd_cash_flow_check_entry_ok(dict(_r21_check(), unit=7))



# --- Codex review round 22 of PR #47 ------------------------------------------------------------------------------
def test_the_run_records_a_hash_of_every_iprd_judgment_input_it_read():
    """[Codex review r22] A judgment.json input changed after the run could leave no trace in the record (a
    paid_in_shares check added for a cash-basis period changes the deduction, yet a run without it records nothing
    on the period), so the engine stamps iprd_judgment_hash — a canonical sha256 of every judgment.json input it reads
    for IPR&D: iprd_cash_flow_check, iprd_deferred_payment and the base_override fields (basis, basis_window, and the
    iprd_amortized value / native_base / figures / shares) — inside the content-hashed payload. make_score recomputes
    it with E.iprd_judgment_hash. Canonical: entry order, int vs float, an absent vs a null unit and fields the engine
    never reads do not change it; every field it reads does."""
    chk = _shares_check("2024-12-31", 100e6)
    j = {"iprd_cash_flow_check": [chk]}
    n = _ok(_run(_facts(expense={2024: 100e6}, cash={2024: 40e6, 2025: 60e6}), judgment=j, checks=False))
    assert n["iprd_judgment_hash"] == E.iprd_judgment_hash(j), n.get("iprd_judgment_hash")
    assert E._content_hash(n) == n["content_hash"]
    assert _plain()["iprd_judgment_hash"] == E.iprd_judgment_hash({}) == E.iprd_judgment_hash(None)
    h = E.iprd_judgment_hash
    other = _shares_check("2021-12-31", 50e6)
    ded = {"period": "2025-12-31", "window": "fy", "amount": 6e7,
           "deferred_payment_of": {"deal": "Test Bio", "first_charged_period": "2024-12-31",
                                   "source": "0000999001-25-000001, note 4",
                                   "contingent_total": {"value": 1e8, "source": "0000999001-25-000001, note 4"}}}
    amort = {"basis": "iprd_amortized", "native_base": "ttm_json", "value": 1.5, "figures": [1e6, 0.0, 2e6],
             "shares": 1e7, "kind": "filing", "source": "s", "reason": "r"}
    base = {"iprd_cash_flow_check": [chk, other], "iprd_deferred_payment": [ded], "base_override": amort,
            "moat_score": 5}
    same = [dict(base, iprd_cash_flow_check=[other, chk]),
            dict(base, iprd_cash_flow_check=[dict(chk, amount=100000000), dict(other, unit=None)]),
            dict(base, iprd_cash_flow_check=[dict(chk, note="ignored"), other]),
            dict(base, base_override=dict(amort, source="another", reason="another", kind="estimate")),
            dict(base, moat_score=7, tier_override="B", in_scope_under_40b=False)]
    for v in same:
        assert h(v) == h(base), v
    changed = [dict(base, iprd_cash_flow_check=[chk]),
               dict(base, iprd_cash_flow_check=[dict(chk, presentation="added_back_paid_in_investing"), other]),
               dict(base, iprd_cash_flow_check=[dict(chk, amount=100e6 + 1), other]),
               dict(base, iprd_cash_flow_check=[dict(chk, source="x"), other]),
               dict(base, iprd_cash_flow_check=[dict(chk, unit="USD"), other]),
               dict(base, iprd_cash_flow_check=[dict(chk, window="ttm_current_ytd"), other]),
               dict(base, iprd_deferred_payment=None),
               dict(base, iprd_deferred_payment=[dict(ded, amount=5e7)]),
               dict(base, iprd_deferred_payment=[dict(ded, deferred_payment_of=dict(ded["deferred_payment_of"], deal="B"))]),
               dict(base, base_override=None),
               dict(base, base_override=dict(amort, value=1.6)),
               dict(base, base_override=dict(amort, figures=[2e6, 0.0, 1e6])),
               dict(base, base_override=dict(amort, shares=2e7)),
               dict(base, base_override=dict(amort, native_base="median_of_last_3_fy_oe_per_share")),
               dict(base, base_override={"value": 1.5, "source": "s", "reason": "r", "basis_window": {"window": "fy"}})]
    for v in changed:
        assert h(v) != h(base), v
    plain_pin = {"value": 1.5, "source": "s", "reason": "r"}
    assert h({"base_override": plain_pin}) == h({"base_override": dict(plain_pin, value=1.6)})
    assert h({"base_override": plain_pin}) != h({"base_override": dict(plain_pin, basis_window={"window": "fy"})})


# --- Codex review round 23 of PR #47 ------------------------------------------------------------------------------
def _r23_ttm():
    """test_ttm's ttm.json shape with the legs a real ttm.py writes (inputs legs, capex_components, overrides_used)."""
    t = _ttm_doc(2.1, 100e6)
    t["inputs"]["ocf"].update(ytd_current=50e6, ttm=230e6)
    t["inputs"]["shares_diluted"] = {"ytd_current": 100e6, "ytd_current_period": ["2026-01-01", "2026-06-30"]}
    t.update(ttm_ocf=230e6, ttm_capex=10e6, ttm_sbc=10e6, entity="SYN INC", ticker="SYN", cik=999001,
             capex_components={"ytd_current": {"ppe": 4e6, "intangibles": 1e6, "intangibles_not_added": False,
                                               "intangible_tags": ["PaymentsToAcquireIntangibleAssets"]}},
             overrides_used=[{"field": "sbc", "value": 10e6, "kind": "filing", "source": "10-K note 9",
                              "reason": "the 10-Qs print no SBC line", "legs_filled": ["ytd_current"]}])
    return t


def test_the_run_records_the_ttm_json_inputs_it_read():
    """[Codex review r23] The engine reads ttm.json for a --ttm pin (the base, the Tier F legs) and for any
    --base-oe-ps pin (whether it is ttm.json's figure decides the IPR&D window and share denominator; an
    iprd_amortized ttm_json native base; a basis_window "ttm" period), but recorded none of it, so make_score could
    only compare the base within 0.1%: a ttm.json regenerated after the run with twice the shares (and twice the OE)
    scored the run's $0.50 charge where a rerun deducts $0.25, and a new 10-Q's YTD period scored the stale window.
    The run now records ttm_inputs — ttm_oe_per_share, ttm_shares_diluted, ytd_current_period and ttm_input_hash, a
    canonical sha256 of ttm.json's input legs (inputs, the TTM totals, fy_end / ytd_end, capex_components,
    split_adjustment, overrides_used's field / value / kind / legs_filled) — inside the content-hashed payload; it is
    null for a run with no pin (the median base never reads ttm.json). Canonical: int vs float, warnings, identity
    and override source text do not change the hash; every leg does."""
    facts, ttm = _ttm_ytd_facts(), _r23_ttm()
    n = _ok(_run(facts, extra=["--ttm"], ttm=ttm))
    ti = n.get("ttm_inputs")
    assert isinstance(ti, dict), n.get("ttm_inputs")
    assert ti == E.ttm_inputs_record(ttm), (ti, E.ttm_inputs_record(ttm))
    assert ti["ttm_oe_per_share"] == 2.1 and ti["ttm_shares_diluted"] == 100e6, ti
    assert ti["ytd_current_period"] == ["2026-01-01", "2026-06-30"], ti
    assert isinstance(ti["ttm_input_hash"], str) and len(ti["ttm_input_hash"]) == 64, ti
    assert E._content_hash(n) == n["content_hash"]
    # a --base-oe-ps pin reads ttm.json too (the TTM-basis test); a median run does not
    p = _ok(_run(facts, extra=["--base-oe-ps", "2.1"], ttm=ttm))
    assert p["ttm_inputs"] == ti, p.get("ttm_inputs")
    assert _ok(_run(facts, ttm=ttm))["ttm_inputs"] is None
    # a --base-oe-ps pin beside no ttm.json records that it read none
    q = _ok(_run(facts, extra=["--base-oe-ps", "2.1"]))
    assert q["ttm_inputs"] == E.ttm_inputs_record(None) and q["ttm_inputs"]["ttm_input_hash"] is None, q.get("ttm_inputs")
    h = lambda t: E.ttm_inputs_record(t)["ttm_input_hash"]
    same = [dict(ttm, ttm_shares_diluted=100000000, ttm_ocf=230000000),
            dict(ttm, warnings=["ttm.py: a warning"], entity="Another name"),
            dict(ttm, overrides_used=[dict(ttm["overrides_used"][0], source="another", reason="another")]),
            dict(ttm, sbc_reconciled_legs={"ytd_current": {"note": "provenance only"}})]
    for v in same:
        assert h(v) == h(ttm), v
    cc = ttm["capex_components"]["ytd_current"]
    changed = [dict(ttm, ttm_shares_diluted=200e6, ttm_oe_total=420e6),
               dict(ttm, ttm_oe_per_share=2.1001), dict(ttm, ttm_ocf=231e6), dict(ttm, ttm_capex=11e6),
               dict(ttm, ttm_sbc=9e6), dict(ttm, ytd_end="2026-09-30"),
               dict(ttm, inputs=dict(ttm["inputs"], ocf=dict(ttm["inputs"]["ocf"],
                                                            ytd_current_period=["2026-01-01", "2026-09-30"]))),
               dict(ttm, inputs=dict(ttm["inputs"], ocf=dict(ttm["inputs"]["ocf"], ytd_current=51e6))),
               dict(ttm, capex_components={"ytd_current": dict(cc, intangibles=2e6)}),
               dict(ttm, capex_components={"ytd_current": dict(cc, intangibles_not_added=True)}),
               dict(ttm, capex_components={"ytd_current": dict(cc, intangible_tags=[])}),
               dict(ttm, split_adjustment={"ratio_used": 2.0, "applied": True}),
               dict(ttm, overrides_used=[dict(ttm["overrides_used"][0], value=11e6)]),
               dict(ttm, overrides_used=[])]
    for v in changed:
        assert h(v) != h(ttm), v
    assert E.ttm_inputs_record(dict(ttm, ttm_shares_diluted=200e6))["ttm_shares_diluted"] == 200e6


# --- Codex review round 24 of PR #47 ------------------------------------------------------------------------------
R24_TODAY = "2026-07-15"   # FY2025 end + 6.5 months: STALE_FY does not fire, so a median native base is the run's own


def _r24_run(facts, extra=(), judgment=None, ttm=None):
    """_run on a fresh latest FY (ET_TODAY 2026-07-15)."""
    import datetime

    def patch(M):
        M.ET_TODAY = datetime.date.fromisoformat(R24_TODAY)
    return run("SYN", args_for(5, extra=list(extra)), judgment=with_checks(facts, judgment, True), ttm=ttm,
               fixture=_syn_fixture(facts, 30.0), patch=patch)


def _r24_median_decl(native, figs):
    return {"basis": "iprd_amortized", "kind": "filing", "native_base": "median_of_last_3_fy_oe_per_share",
            "figures": figs, "shares": SHARES, "value": native - sum(figs) / 3 / SHARES,
            "source": "test: this run's dcf_numbers.json iprd_adjustment and the median base",
            "reason": "test: acquisition-led R&D recurs"}


def test_an_amortized_declaration_takes_its_window_and_denominator_from_its_native_base_only():
    """[Codex review r24, #4333432465] An iprd_amortized declaration on native_base median_of_last_3_fy_oe_per_share
    whose pin happens to sit within 0.1% of ttm.json's ttm_oe_per_share was read as a TTM base by the generic numeric
    match: the run added the current-YTD leg and divided by ttm_shares_diluted while the amortization arithmetic used
    the median and the latest FY count. FY2023 / FY2025 $3M each and $6M in the 2026 H1 10-Q on 100M shares is 3.1% of
    the median base (not material, so not recurrent); read on the TTM window ($12M on ttm.json's 50M shares, 12.3%) it
    looked recurrent and the declaration was accepted. The window and denominator now come only from native_base: the
    declaration is refused whatever ttm.json's figure is, and a recurrent one is judged on the FY window and the latest
    FY count. The same holds for a plain base_override declaring basis_window {"window": "fy"}."""
    f = _facts(expense={2023: 3e6, 2025: 3e6})
    _ytd(f, EXPENSE, "2026-01-01", "2026-06-30", 6e6, "2026-08-05")
    n0 = _ok(_r24_run(f))
    assert n0["iprd_adjustment"]["recurrent"] is False and n0["iprd_adjustment"]["total"] == 6e6, n0["iprd_adjustment"]
    d = _r24_median_decl(n0["base_oe_normalized_per_share"], [3e6, 0.0, 3e6])
    for tv in (d["value"], d["value"] * 1.01, None):
        out = _r24_run(f, extra=["--base-oe-ps", repr(d["value"])], judgment={"base_override": d},
                       ttm=_ttm_doc(tv, 50e6) if tv is not None else None)
        assert out["exit"] == 3 and "BAD_BASE_OVERRIDE" in out["stdout"] and "only for recurrent" in out["stdout"], \
            (tv, out["exit"], out["stdout"][-800:])
    # a recurrent declaration whose pin equals ttm.json's figure: the FY window and the latest FY count
    f2 = _facts(expense={2023: 15e6, 2025: 20e6})
    _ytd(f2, EXPENSE, "2026-01-01", "2026-06-30", 30e6, "2026-08-05")
    n1 = _ok(_r24_run(f2))
    d2 = _r24_median_decl(n1["base_oe_normalized_per_share"], [15e6, 0.0, 20e6])
    n = _ok(_r24_run(f2, extra=["--base-oe-ps", repr(d2["value"])], judgment={"base_override": d2},
                     ttm=_ttm_doc(d2["value"], 50e6)))
    blk = n["iprd_adjustment"]
    assert blk["treatment"] == "amortized_in_base" and blk["total"] == 35e6, blk
    assert blk["shares_denominator"] == SHARES and blk["window"]["ttm_current_ytd"] is None, blk
    # a plain pin declaring basis_window fy keeps the FY window and count though ttm.json's figure equals it
    facts, ttm = _ttm_ytd_facts(), _ttm_doc(2.1, 98e6)
    n = _ok(_run(facts, extra=["--base-oe-ps", "2.1"], ttm=ttm, judgment={"base_override": ttm_window_decl(2.1, "fy")}))
    blk = n["iprd_adjustment"]
    assert blk["total"] == 20e6 and blk["shares_denominator"] == SHARES and blk["window"]["ttm_current_ytd"] is None, blk
    assert n["inputs"]["base_basis_window"] == {"window": "fy"}, n["inputs"]
    # undeclared (or declared without basis_window): the numeric match still makes it a TTM base
    bare = {k: v for k, v in ttm_window_decl(2.1).items() if k != "basis_window"}
    n = _ok(_run(facts, extra=["--base-oe-ps", "2.1"], ttm=ttm, judgment={"base_override": bare}))
    blk = n["iprd_adjustment"]
    assert blk["total"] == 50e6 and blk["shares_denominator"] == 98e6, blk


def _r24_unknown_rest(later_unit="EUR", later=60e6):
    """FY2024 EUR 100M expensed (no FX rate) beside $40M USD cash: a cash-basis period whose remainder is unknown in
    USD; FY2025 a cash-only payment of `later` in later_unit."""
    f = _syn_facts()
    _syn_put(f, EXPENSE, "EUR", _ctx("2024-01-01", "2024-12-31", 100e6, filed="2025-02-20"))
    _fy(f, CASH, 2024, 40e6)
    if later is not None:
        _syn_put(f, CASH, later_unit, _ctx("2025-01-01", "2025-12-31", later, filed="2026-02-20"))
    return f


def test_an_unconvertible_cash_only_payment_after_an_unknown_remainder_is_gated():
    """[Codex review r24, #4333432474] The no-FX-rate cash-only branch gated a payment only when the window's unpaid
    remainder was positive or a charge sat before the window. A charge whose USD remainder is unknown (FY2024 EUR 100M
    expensed, no rate, beside $40M USD cash) accrues nothing into the unpaid remainder, so a later EUR 60M cash-only
    payment with no rate went to ignored_cash_only ("nothing in the window it could settle") and the run published
    after deducting $40M. It is now gated like the same payment in USD: excluded non_usd_no_rate, cash_native kept,
    unconverted_remainder_of naming FY2024, ACQUIRED_IPRD_UNCONVERTED — on the FY window, the current-YTD leg, and
    beside a $0 or negative expense alike."""
    nofx = lambda c, d: None
    for unit in ("EUR", "USD"):
        out = E.iprd_detect(_r24_unknown_rest(unit), FY3, fx_rates={}, fx_fetch=nofx)
        r = [p for p in out["periods"] if p["period"] == "2025-12-31"]
        assert len(r) == 1 and r[0]["excluded"] == "non_usd_no_rate" and r[0]["deducted"] == 0.0, (unit, out["periods"])
        assert r[0]["cash_native"] == 60e6 and r[0]["unconverted_remainder_of"] == ["2024-12-31"], r[0]
        assert out["ignored_cash_only"] == [], (unit, out["ignored_cash_only"])
        assert E.iprd_unresolved({"iprd_adjustment": out}), unit
        fl = [x for x in E.iprd_flags(out) if x.startswith("ACQUIRED_IPRD_UNCONVERTED")]
        assert len(fl) == 1 and f"60,000,000 {unit} (after FY2024)" in fl[0], fl
    r = [p for p in E.iprd_detect(_r24_unknown_rest(), FY3, fx_rates={}, fx_fetch=nofx)["periods"]
         if p["period"] == "2025-12-31"][0]
    assert "unknown in USD" in r["cash_fx_note"], r["cash_fx_note"]
    # the current-YTD leg
    f = _r24_unknown_rest(later=None)
    _eur_cash_ytd(f, 60e6, "0000999001-26-000020")
    out = E.iprd_detect(f, FY3, ytd=("2026-01-01", "2026-03-31"), fx_rates={}, fx_fetch=nofx)
    r = [p for p in out["periods"] if p["window"] == "ttm_current_ytd"]
    assert len(r) == 1 and r[0]["excluded"] == "non_usd_no_rate" and r[0]["unconverted_remainder_of"] == ["2024-12-31"], out
    assert out["ignored_cash_only"] == [] and E.iprd_unresolved({"iprd_adjustment": out}), out
    # beside a $0 or a negative (reversal) USD expense
    for v in (0.0, -5e6):
        f = _r24_unknown_rest()
        _fy(f, EXPENSE, 2025, v)
        out = E.iprd_detect(f, FY3, fx_rates={}, fx_fetch=nofx)
        r = [p for p in out["periods"] if p["period"] == "2025-12-31"][0]
        assert r["excluded"] == "non_usd_no_rate" and r["unconverted_remainder_of"] == ["2024-12-31"], (v, r)
        assert out["ignored_cash_only"] == [] and E.iprd_unresolved({"iprd_adjustment": out}), (v, out)
    # end to end: the run is unresolved (make_score refuses it), not a $40M deduction
    m = _run_fx(_r24_unknown_rest(), {}, judgment={})
    assert m["exit"] == 0 and E.iprd_unresolved(m["numbers"]), m["numbers"].get("iprd_adjustment")
    # nothing it could settle: still listed, not gated
    f = _syn_facts()
    _syn_put(f, CASH, "EUR", _ctx("2025-01-01", "2025-12-31", 60e6, filed="2026-02-20"))
    out = E.iprd_detect(f, FY3, fx_rates={}, fx_fetch=nofx)
    assert out is None or (not out["periods"] and len(out["ignored_cash_only"]) == 1), out


def _r24_two_tags(cur, cur_unit, old, old_unit, cash=None, cash_unit="USD"):
    f = _syn_facts()
    _syn_put(f, EXPENSE, cur_unit, _ctx("2025-01-01", "2025-12-31", cur, filed="2026-02-20"))
    _syn_put(f, EXPENSE_OLD, old_unit, _ctx("2025-01-01", "2025-12-31", old, filed="2026-02-20"))
    if cash is not None:
        _syn_put(f, CASH, cash_unit, _ctx("2025-01-01", "2025-12-31", cash, filed="2026-02-20"))
    return f


R24_CHK = [{"period": "2025-12-31", "window": "fy", "amount": 100e6, "presentation": "added_back_paid_in_investing",
            "source": "test"}]


def test_an_unconvertible_parallel_detector_tag_is_a_conflict_that_gates_the_period():
    """[Codex review r24, #4333432477] With both detector tags positive and one of them unconvertible (no FX rate,
    even fetched), the cross-tag conflict test compared the converted tag's USD figure with the other's native one:
    current tag USD 100M beside ResearchAndDevelopmentInProcess EUR 100M recorded no expense_tags_conflict, a USD 100M
    check applied and the run scored though the ignored legacy fact could be a different USD charge (and EUR 50M was
    recorded as if it were USD 50M). A positive unconvertible parallel fact is never equated with a converted one: the
    conflict is recorded with each tag's native figure, unit and USD value (None when unconvertible), no check is
    applied (the entry is listed unused), and the period is gated non_usd_no_rate (ACQUIRED_IPRD_UNCONVERTED, make_score
    refuses it) — expense or cash basis, either tag order. Converted tags compare in USD as before; two unconvertible
    tags in one unit compare their native figures (the unit is recorded)."""
    nofx = lambda c, d: None
    cases = [("expense basis", _r24_two_tags(100e6, "USD", 100e6, "EUR"), R24_CHK),
             ("cash basis", _r24_two_tags(100e6, "USD", 100e6, "EUR", cash=100e6), None),
             ("reverse order", _r24_two_tags(100e6, "EUR", 100e6, "USD", cash=100e6), None),
             ("smaller native", _r24_two_tags(100e6, "USD", 50e6, "EUR"), R24_CHK),
             ("two unconvertible units", _r24_two_tags(100e6, "EUR", 100e6, "GBP", cash=100e6), None)]
    for label, f, checks in cases:
        out = E.iprd_detect(f, FY3, fx_rates={}, fx_fetch=nofx, checks=checks)
        r = [p for p in out["periods"] if p["period"] == "2025-12-31"][0]
        assert r["excluded"] == "non_usd_no_rate" and r["deducted"] == 0.0, (label, r)
        c = r.get("expense_tags_conflict") or {}
        assert set(c) == {EXPENSE, EXPENSE_OLD} and all(isinstance(v, dict) and set(v) == {"native", "unit", "usd"}
                                                        for v in c.values()), (label, c)
        assert any(v["usd"] is None for v in c.values()), (label, c)
        u = r["expense_tag_unconverted"]
        assert u["native"] > 0 and u["unit"] in ("EUR", "GBP") and u["tag"] in (EXPENSE, EXPENSE_OLD), (label, u)
        assert "cash_flow_check" not in r and "cannot be compared" in r["expense_tags_note"], (label, r)
        if checks:
            assert out["cash_flow_checks_unused"] == checks and r["cash_flow_check_not_applied"]["amount"] == 100e6, (label, r)
        assert E.iprd_unresolved({"iprd_adjustment": out}), label
        fl = [x for x in E.iprd_flags(out) if x.startswith("ACQUIRED_IPRD_UNCONVERTED")]
        assert len(fl) == 1 and "cannot be compared" in fl[0], (label, fl)
    c = E.iprd_detect(cases[0][1], FY3, fx_rates={}, fx_fetch=nofx, checks=R24_CHK)["periods"][0]["expense_tags_conflict"]
    assert c == {EXPENSE: {"native": 100e6, "unit": "USD", "usd": 100e6},
                 EXPENSE_OLD: {"native": 100e6, "unit": "EUR", "usd": None}}, c
    # converted: compared in USD as before (no gate)
    out = E.iprd_detect(_r24_two_tags(100e6, "USD", 100e6, "EUR"), FY3, fx_rates={"EUR": {"2025-12-31": 1.3}},
                        checks=R24_CHK)
    r = out["periods"][0]
    assert r["excluded"] is None and r["deducted"] == 100e6, r
    assert r["expense_tags_conflict"] == {EXPENSE: 100e6, EXPENSE_OLD: 130e6}, r
    out = E.iprd_detect(_r24_two_tags(100e6, "USD", 80e6, "EUR"), FY3, fx_rates={"EUR": {"2025-12-31": 1.25}},
                        checks=R24_CHK)
    assert out["periods"][0]["deducted"] == 100e6 and "expense_tags_conflict" not in out["periods"][0], out["periods"][0]
    # two unconvertible facts in one unit: native figures compared; agreeing ones are no conflict
    out = E.iprd_detect(_r24_two_tags(100e6, "EUR", 100e6, "EUR", cash=40e6), FY3, fx_rates={}, fx_fetch=nofx)
    r = out["periods"][0]
    assert r["excluded"] is None and r["deducted"] == 40e6 and "expense_tags_conflict" not in r, r
    out = E.iprd_detect(_r24_two_tags(100e6, "EUR", 120e6, "EUR", cash=40e6), FY3, fx_rates={}, fx_fetch=nofx)
    r = out["periods"][0]
    assert r["excluded"] is None and r["deducted"] == 40e6, r
    assert r["expense_tags_conflict"] == {EXPENSE: {"native": 100e6, "unit": "EUR", "usd": None},
                                          EXPENSE_OLD: {"native": 120e6, "unit": "EUR", "usd": None}}, r
    # end to end: unresolved, so make_score refuses it
    m = _run_fx(_r24_two_tags(100e6, "USD", 100e6, "EUR"), {}, judgment={"iprd_cash_flow_check": R24_CHK})
    assert m["exit"] == 0 and E.iprd_unresolved(m["numbers"]), m["numbers"].get("iprd_adjustment")


# --- Codex review round 25 of PR #47 ------------------------------------------------------------------------------
def _r25_ttm_moved():
    t = _ttm_doc(2.6, 120e6)
    t["inputs"]["ocf"]["ytd_current_period"] = ["2026-01-01", "2026-09-30"]
    t["ytd_end"] = "2026-09-30"
    return t


def _r25_strip(n):
    return {k: v for k, v in n.items() if k not in ("as_of", "price_source", "diagnostics", "content_hash")}


def test_ttm_inputs_are_recorded_only_when_the_runs_basis_reads_ttm_json():
    """[Codex review r25, #4333638581] Round 23 recorded ttm_inputs for every --base-oe-ps pin, deciding before the
    basis was chosen: a plain pin declaring basis_window {"window": "fy"}, or an iprd_amortized pin on the median
    native base, reads nothing from ttm.json (the FY window, the latest FY count, no Tier F legs), yet the whole
    current ttm.json was stamped into its record, so a ttm.json regenerated (or written, or deleted) after the run
    refused an unchanged FY-based run. ttm_inputs is now recorded only when the selected basis reads ttm.json — a
    --ttm pin, a pin no declaration places (ttm.json's figure decides its basis), basis_window "ttm", an amortized
    native_base ttm_json, or a median-native amortized pin under STALE_FY (ttm.json's TTM base decides whether the
    median may be the native base) — and is null otherwise: the FY runs on two ttm.json files and on none are
    identical, ttm_inputs included."""
    facts = _ttm_ytd_facts()
    ta, tb = _ttm_doc(2.1, 98e6), _r25_ttm_moved()
    fy = {"base_override": ttm_window_decl(2.1, "fy")}
    runs = [_ok(_run(facts, extra=["--base-oe-ps", "2.1"], ttm=t, judgment=fy)) for t in (ta, tb, None)]
    for n in runs:
        assert n["ttm_inputs"] is None, n.get("ttm_inputs")
        assert n["inputs"]["base_basis_window"] == {"window": "fy"} and n["iprd_adjustment"]["total"] == 20e6, n["inputs"]
        assert E._content_hash(n) == n["content_hash"]
    assert _r25_strip(runs[0]) == _r25_strip(runs[1]) == _r25_strip(runs[2])
    # a median-native amortized pin on a fresh FY: null whatever ttm.json holds
    f2 = _facts(expense={2023: 15e6, 2025: 20e6})
    _ytd(f2, EXPENSE, "2026-01-01", "2026-06-30", 30e6, "2026-08-05")
    d2 = _r24_median_decl(_ok(_r24_run(f2))["base_oe_normalized_per_share"], [15e6, 0.0, 20e6])
    a2 = ["--base-oe-ps", repr(d2["value"])]
    am = [_ok(_r24_run(f2, extra=a2, judgment={"base_override": d2}, ttm=t))
          for t in (_ttm_doc(d2["value"], 50e6), _ttm_doc(9.0, 70e6))]
    for n in am:
        assert n["iprd_adjustment"]["treatment"] == "amortized_in_base" and n["ttm_inputs"] is None, n.get("ttm_inputs")
    assert _r25_strip(am[0]) == _r25_strip(am[1])
    # ... but under STALE_FY ttm.json's TTM base decides whether the median may be its native base: recorded
    rec = _recurrent()
    d = amortized_decl(rec)
    st = _ok(_run(_facts(expense={2023: 15e6, 2025: 20e6}), extra=["--base-oe-ps", repr(d["value"])],
                  judgment={"base_override": d}))
    assert st["iprd_adjustment"]["treatment"] == "amortized_in_base", st["iprd_adjustment"]["treatment"]
    assert st["ttm_inputs"] == E.ttm_inputs_record(None), st.get("ttm_inputs")
    # a basis_window "ttm" pin reads ttm.json's current-YTD leg: recorded
    w = _ok(_run(facts, extra=["--base-oe-ps", "1.75"], ttm=ta, judgment={"base_override": ttm_window_decl(1.75)}))
    assert w["inputs"]["base_basis_window"]["window"] == "ttm" and w["ttm_inputs"] == E.ttm_inputs_record(ta), w.get("ttm_inputs")


def test_a_zero_pin_matches_a_zero_figure_at_an_absolute_tolerance():
    """[Codex review r25, #4333638587 siblings] Every declared-pin and ttm.json-figure match was 0.1% of the
    reference, which is zero-width at zero, and ttm.json's ttm_oe_per_share of exactly 0 was read as no TTM base:
    an undeclared --base-oe-ps 0.0 beside a ttm.json figure of 0.0 was scored on the FY window and count, and an
    iprd_amortized declaration of $0.003 (inside the engine's own cent check) on a zero pin was not the pin's
    declaration, so the run took the one-time deduction. dcf_engine.pin_matches compares within 0.1% of the
    reference, or within half a cent per share when either side is zero; a non-zero mismatch is still refused."""
    m = E.pin_matches
    assert m(0.0, 0.0) and m(0.004, 0.0) and m(0.0, 0.004) and m(0.0, 2.2e-16) and m(-0.004, 0.0)
    assert not m(0.006, 0.0) and not m(0.0, 0.006) and not m(0.01, 0.0)
    assert m(2.1021, 2.1) and not m(2.103, 2.1) and m(-2.1021, -2.1) and not m(2.1, -2.1)
    assert not m(None, 0.0) and not m(True, 1.0) and not m(float("nan"), 0.0) and not m("0", 0.0)
    facts = _ttm_ytd_facts()
    n = _ok(_run(facts, extra=["--base-oe-ps", "0.0"], ttm=_ttm_doc(0.0, 98e6)))
    blk = n["iprd_adjustment"]
    assert blk["window"]["ttm_current_ytd"] == ["2026-01-01", "2026-06-30"], blk["window"]
    assert blk["total"] == 50e6 and blk["shares_denominator"] == 98e6, blk
    # an amortized declaration of $0.003 on a zero pin: the native median less the mean charge is exactly zero
    N = _recurrent()["base_oe_normalized_per_share"]
    c = 1.5 * N * SHARES
    f0 = _facts(expense={2023: c, 2025: c})
    probe = _ok(_run(f0))
    d = amortized_decl(probe, value=0.003)
    z = _ok(_run(f0, extra=["--base-oe-ps", "0.0"], judgment={"base_override": d}))
    assert z["iprd_adjustment"]["treatment"] == "amortized_in_base" and E.iprd_charge_per_share(z) == 0.0, z["iprd_adjustment"]
    # a declaration a cent off a zero pin is not its declaration
    out = _run(f0, extra=["--base-oe-ps", "0.0"], judgment={"base_override": amortized_decl(probe, value=0.01)})
    assert out["exit"] != 0 or out["numbers"]["iprd_adjustment"]["treatment"] != "amortized_in_base", out["stdout"][-800:]


# --- Codex review round 26 of PR #47 ------------------------------------------------------------------------------
def test_an_undeclared_pin_matches_a_zero_ttm_figure_only_when_exactly_zero():
    """[Codex review r26, #4333889284] Round 25's pin_matches allowed half a cent whenever either side was zero, and
    the engine used it for the numeric TTM match: an undeclared --base-oe-ps 0.004 beside a ttm.json
    ttm_oe_per_share of exactly 0 was taken as ttm.json's $0.00 TTM base (the TTM current-YTD window, ttm.json's
    share denominator), and a plain base_override declaring 0.0 with basis_window {"window": "fy"} placed the 0.004
    pin on the FY basis — a positive base, so Tier D where the declared or TTM base is Tier F. The half-cent band is
    declaration arithmetic only (an iprd_amortized value reproduced from its own figures): an undeclared match and a
    plain value use figure_matches (0.1%, a zero only by an exact zero), and an amortized pin must sit on the same
    side of zero as the value its figures reproduce."""
    f = E.figure_matches
    assert f(0.0, 0.0) and not f(0.004, 0.0) and not f(-0.004, 0.0) and not f(0.0, 0.004) and not f(2.2e-16, 0.0)
    assert f(2.1021, 2.1) and not f(2.103, 2.1) and not f(None, 0.0) and not f(float("nan"), 0.0) and not f(True, 1.0)
    assert E.pin_matches(0.004, 0.0)    # declaration arithmetic keeps its band
    plain0 = ttm_window_decl(0.0, "fy")
    assert E.declared_value_matches({"basis": "iprd_amortized", "value": 0.003}, 0.0)
    assert E.declared_value_matches(plain0, 0.0) and not E.declared_value_matches(plain0, 0.004)
    assert not E.share_scale_pin_rescue("base_oe_ps_arg", 0.004, 30.0, {"value": 0.0, "source": "s", "reason": "r"})[0]
    facts, t0 = _ttm_ytd_facts(), _ttm_doc(0.0, 98e6)
    n = _ok(_run(facts, extra=["--base-oe-ps", "0.004"], ttm=t0))
    blk = n["iprd_adjustment"]
    assert not blk["window"].get("ttm_current_ytd") and blk["shares_denominator"] == SHARES, blk
    assert n["ttm_inputs"] == E.ttm_inputs_record(t0), n.get("ttm_inputs")   # an undeclared pin still records it
    z = _ok(_run(facts, extra=["--base-oe-ps", "0.0"], ttm=t0))   # an exact zero is still ttm.json's TTM base
    assert z["iprd_adjustment"]["window"]["ttm_current_ytd"] == ["2026-01-01", "2026-06-30"], z["iprd_adjustment"]
    # a plain declaration of 0.0 does not place a 0.004 pin on its FY basis_window
    p = _ok(_run(facts, extra=["--base-oe-ps", "0.004"], ttm=_ttm_doc(2.0, 98e6), judgment={"base_override": plain0}))
    assert p["inputs"].get("base_basis_window") is None, p["inputs"]
    # an amortized declaration of $0.00: the zero pin scores, a positive pin half a cent off is refused
    N = _recurrent()["base_oe_normalized_per_share"]
    c = 1.5 * N * SHARES
    f0 = _facts(expense={2023: c, 2025: c})
    d = amortized_decl(_ok(_run(f0)), value=0.0)
    ok = _ok(_run(f0, extra=["--base-oe-ps", "0.0"], judgment={"base_override": d}))
    assert ok["iprd_adjustment"]["treatment"] == "amortized_in_base" and ok["base_oe_per_share"] == 0.0
    out = _run(f0, extra=["--base-oe-ps", "0.004"], judgment={"base_override": d})
    assert out["exit"] != 0 and "opposite sides of zero" in out["stdout"], (out["exit"], out["stdout"][-800:])



# ===========================================================================
# [Codex review r27 of PR #47] The recurrence count reads each FY period's own expense, never its cash timing
# ===========================================================================
def test_recurrence_counts_an_accrued_charge_whatever_its_cash_timing():
    """[Codex review r27 of PR #47] Two distinct deals expensed $100M in FY2023 and $100M in FY2024 with $0 cash in
    either year (the cash tag filed at $0: cash basis, deducted $0, the expense accrued into the window's unpaid
    remainder) and the $200M paid in FY2025 on the cash tag alone. The recurrence list read `deducted > 0`, so both
    charge years dropped out and the FY2025 settlement (a deferred payment) did not count either: fy_with_charge []
    and ACQUIRED_IPRD_RECURRENT silent on a material window, while $1 paid in each charge year flipped it to
    recurrent: cash timing, not the acquisitions, decided the owner's 2-of-3 rule. Now a period counts by its own
    positive expense, paid in the year or accrued: FY2023 and FY2024 count, FY2025 (a settlement with no expense of
    its own) does not. The same holds with a $0 FY2025 expense filed, $1 paid in each charge year, or each charge paid
    in its own year. The deduction is unchanged ($200M once, in FY2025), the iprd_amortized base becomes available
    (its figures are the deducted FY figures, $0 years included), and the TTM path counts an FY charge whose
    remainder the current-YTD 10-Q pays."""
    f = _facts(expense={2023: 100e6, 2024: 100e6}, cash={2023: 0.0, 2024: 0.0, 2025: 200e6})
    n = _ok(_run(f))
    blk = n["iprd_adjustment"]
    assert blk["fy_with_charge"] == ["2023-12-31", "2024-12-31"] and blk["recurrent"] and blk["material"], blk
    rf = flags(n, "ACQUIRED_IPRD_RECURRENT")
    assert len(rf) == 1 and "FY2023, FY2024 (2 of the last 3" in rf[0], rf
    assert blk["total"] == 200e6 and blk["charge_per_share"] == 200e6 / SHARES, blk
    assert [(p["period"], p["deducted"]) for p in blk["periods"]] == [
        ("2023-12-31", 0.0), ("2024-12-31", 0.0), ("2025-12-31", 200e6)], blk["periods"]
    assert next(p for p in blk["periods"] if p["period"] == "2025-12-31").get("deferred_payment"), blk["periods"]
    for exp, cash in (({2023: 100e6, 2024: 100e6, 2025: 0.0}, {2023: 0.0, 2024: 0.0, 2025: 200e6}),
                      ({2023: 100e6, 2024: 100e6}, {2023: 1.0, 2024: 1.0, 2025: 199999998.0}),
                      ({2023: 100e6, 2024: 100e6}, {2023: 100e6, 2024: 100e6})):
        b = _ok(_run(_facts(expense=exp, cash=cash)))["iprd_adjustment"]
        assert b["fy_with_charge"] == ["2023-12-31", "2024-12-31"] and b["recurrent"] and b["total"] == 200e6, (exp, cash, b)
    # the amortized base is no longer refused as "not recurrent": figures [0, 0, 200M], the same mean charge
    d = amortized_decl(n)
    assert d["figures"] == [0.0, 0.0, 200e6], d["figures"]
    am = _ok(_run(f, extra=["--base-oe-ps", repr(d["value"])], judgment={"base_override": d}))
    assert am["iprd_adjustment"]["treatment"] == "amortized_in_base" and am["iprd_adjustment"]["recurrent"], am["iprd_adjustment"]
    # TTM: FY2024 a $100M charge paid in its year, FY2025 a $100M charge with $0 cash paid in the current-YTD 10-Q
    f2 = _facts(expense={2024: 100e6, 2025: 100e6}, cash={2024: 100e6, 2025: 0.0})
    _ytd(f2, CASH, "2026-01-01", "2026-03-31", 100e6, "2026-04-29", fp="Q1")
    ttm = _ttm_doc(2.1, 100e6)
    ttm["inputs"]["ocf"]["ytd_current_period"] = ["2026-01-01", "2026-03-31"]
    b2 = _ok(_run(f2, extra=["--ttm"], ttm=ttm))["iprd_adjustment"]
    assert b2["fy_with_charge"] == ["2024-12-31", "2025-12-31"] and b2["recurrent"] and b2["total"] == 200e6, b2


def test_one_deal_expensed_once_and_paid_in_installments_stays_one_charge_year():
    """[Codex review r27 of PR #47] The other side of the rule: ONE deal expensed $100M in FY2024 and paid over two
    years ($40M then $60M; $0 then $100M; $0 then $100M beside a $0 FY2025 expense) is one charge year. The FY2025
    cash settles the window's unpaid remainder (deferred_payment) and is not a new charge, so
    ACQUIRED_IPRD_RECURRENT stays silent and the $100M is deducted once. [Codex review r28 of PR #47] Two $0-cash
    charges whose residuals are declared paid in shares are still two acquisitions: both years count, recurrent on
    their $200M of expense, though nothing is deducted (round 27 had kept them out of the count)."""
    for exp, cash in (({2024: 100e6}, {2024: 40e6, 2025: 60e6}),
                      ({2024: 100e6}, {2024: 0.0, 2025: 100e6}),
                      ({2024: 100e6, 2025: 0.0}, {2024: 0.0, 2025: 100e6})):
        n = _ok(_run(_facts(expense=exp, cash=cash)))
        b = n["iprd_adjustment"]
        assert b["fy_with_charge"] == ["2024-12-31"] and not b["recurrent"] and b["total"] == 100e6, (exp, cash, b)
        assert not flags(n, "ACQUIRED_IPRD_RECURRENT"), (exp, cash)
    shares = [_shares_check("2023-12-31", 100e6), _shares_check("2024-12-31", 100e6)]
    b = _ok(_run(_facts(expense={2023: 100e6, 2024: 100e6}, cash={2023: 0.0, 2024: 0.0}),
                 judgment={"iprd_cash_flow_check": shares}, checks=False))["iprd_adjustment"]
    assert b["fy_with_charge"] == ["2023-12-31", "2024-12-31"] and b["recurrent"] and b["total"] == 0.0, b
    assert b["recurrence_expense_total"] == 200e6, b


def test_a_declared_installment_year_is_still_excluded_from_the_recurrence_count():
    """[Codex review r27 of PR #47] Andrew's 2026-10-20 rule still holds once the count reads the expense: the FY2023
    deal ($15M, paid in its year) and an FY2025 $20M milestone expensed with $0 cash (accrued). The FY2025 charge now
    counts (RECURRENT on 2 of 3) unless judgment.json declares it, whole and cited, the FY2023 deal's deferred
    payment. The declaration of such an accrued period claims its expense (before, its $0 cash-basis amount left
    nothing to declare: BAD_IPRD_DEFERRED_PAYMENT); declared, the period is recurrence_excluded and RECURRENT does not
    fire. The deduction is unchanged ($15M: FY2025's unpaid $20M is not deducted until paid). The paid installment
    (the expense-basis shape) is still excluded too."""
    f = _facts(expense={2023: 15e6, 2025: 20e6}, cash={2023: 15e6, 2025: 0.0})
    u = _ok(_run(f))["iprd_adjustment"]
    assert u["fy_with_charge"] == ["2023-12-31", "2025-12-31"] and u["recurrent"] and u["total"] == 15e6, u
    n = _ok(_run(f, judgment={"iprd_deferred_payment": [deferred(amount=20e6)]}))
    b = n["iprd_adjustment"]
    assert b["fy_with_charge"] == ["2023-12-31"] and not b["recurrent"] and b["total"] == 15e6, b
    assert not flags(n, "ACQUIRED_IPRD_RECURRENT")
    p25 = next(p for p in b["periods"] if p["period"] == "2025-12-31")
    assert p25["recurrence_excluded"] == "deferred_payment_of" and p25["deducted"] == 0.0, p25
    assert b["recurrence_excluded"] == [{"period": "2025-12-31", "window": "fy", "deal": "Test Bio",
                                         "first_charged_period": "2023-12-31", "amount": 20e6}], b
    # a part of the accrued charge declared: the rest is a new purchase, the year still counts
    part = _ok(_run(f, judgment={"iprd_deferred_payment": [deferred(amount=5e6)]}))["iprd_adjustment"]
    assert part["fy_with_charge"] == ["2023-12-31", "2025-12-31"] and part["recurrent"], part
    # more than the accrued expense: refused
    _refused(_run(f, judgment={"iprd_deferred_payment": [deferred(amount=25e6)]}), "more than the period's")
    # the paid shape is unchanged
    p = _ok(_two_of_three([deferred()]))["iprd_adjustment"]
    assert p["fy_with_charge"] == ["2023-12-31"] and not p["recurrent"], p


# ===========================================================================
# [Codex review r28 of PR #47] A year counts by its own expense whatever its cash presentation, and the recurrence
# gate measures the acquisitions' expense, never the cash the window deducted
# ===========================================================================
def _r28_check(period, amount, presentation):
    return {"period": period, "window": "fy", "amount": amount, "presentation": presentation,
            "source": f"SYN 10-K (0000999001-25-000004) cash-flow statement: the {period} acquired IPR&D ({presentation})"}


def _r28_second_year(presentation=None, intangibles=None):
    """FY2023: a $100M acquisition paid in cash in its year (the cash tag filed: cash basis). FY2024: a separate $100M
    acquisition expensed with no us-gaap cash tag, its iprd_cash_flow_check declaring `presentation` (None: no check,
    so the period awaits it)."""
    f = _facts(expense={2023: 100e6, 2024: 100e6}, cash={2023: 100e6}, intangibles=intangibles)
    j = {"iprd_cash_flow_check": [_r28_check("2024-12-31", 100e6, presentation)]} if presentation else None
    return _ok(_run(f, judgment=j, checks=False))


def _r28_mat(n, expense_total):
    """The recurrence materiality the engine should record: the expense total per share on the run's own denominator
    (x its ADS ratio), against the run's base."""
    b = n["iprd_adjustment"]
    return expense_total / b["shares_denominator"] * b["ads_ratio"] / n["base_oe_per_share"]


def test_a_charge_year_counts_whatever_its_cash_presentation():
    """[Codex review r28 of PR #47, #4334315268] Round 27 counted a year by its own expense whatever its cash timing,
    but still dropped every excluded presentation: a $100M acquisition paid in cash in FY2023 and a SEPARATE $100M one
    in FY2024 paid in shares read one charge year (fy_with_charge [FY2023], recurrent false), so a habit of buying R&D
    escaped ACQUIRED_IPRD_RECURRENT because one deal was paid in stock. The owner's 2-of-3 rule counts acquisitions:
    a year counts by its own positive acquired-IPR&D expense whatever its cash presentation — paid in shares, inside
    operating cash flow, inside intangible capex, awaiting the cash-flow check — and the recurrence gate is measured on
    those expenses ($200M here). The deduction rules are unchanged: those presentations still deduct nothing (OE or
    the share count already carries them), so ACQUIRED_IPRD_CHARGE reads the $100M deducted. Still not counted: a
    negative expense (a reversal), and a year declared, whole, an installment of an earlier deal (Andrew's
    2026-10-20 ruling) — also a $0-cash charge whose residual is declared paid in shares, which a whole declaration
    can now claim by its expense."""
    for pres, intang, why in (("paid_in_shares", None, "paid_in_shares"),
                              ("inside_operating_cash_flow", None, "paid_in_operating_cash_flow"),
                              ("paid_in_intangible_capex", {2024: 100e6}, "already_in_capex"),
                              (None, None, "awaiting_cash_flow_check")):
        n = _r28_second_year(pres, intang)
        b = n["iprd_adjustment"]
        p24 = next(p for p in b["periods"] if p["period"] == "2024-12-31")
        assert p24["excluded"] == why and p24["deducted"] == 0.0, (pres, p24)
        assert b["total"] == 100e6, (pres, b["total"])
        assert b["fy_with_charge"] == ["2023-12-31", "2024-12-31"] and b["recurrent"], (pres, b)
        assert b["recurrence_expense_total"] == 200e6, (pres, b)
        assert abs(b["recurrence_materiality"] - _r28_mat(n, 200e6)) < 1e-12, (pres, b)
        rf = flags(n, "ACQUIRED_IPRD_RECURRENT")
        assert len(rf) == 1 and "FY2023, FY2024 (2 of the last 3" in rf[0], (pres, rf)
    # a reversal is no charge year
    neg = _ok(_run(_facts(expense={2023: 100e6, 2024: -5e6}, cash={2023: 100e6}), checks=False))["iprd_adjustment"]
    assert neg["fy_with_charge"] == ["2023-12-31"] and not neg["recurrent"], neg
    # an expense-basis share-paid year declared, whole, the FY2023 deal's installment still leaves the count
    f = _facts(expense={2023: 15e6, 2025: 20e6}, cash={2023: 15e6})
    j = {"iprd_cash_flow_check": [_r28_check("2025-12-31", 20e6, "paid_in_shares")]}
    u = _ok(_run(f, judgment=j, checks=False))["iprd_adjustment"]
    assert u["fy_with_charge"] == ["2023-12-31", "2025-12-31"] and u["recurrent"], u
    d = _ok(_run(f, judgment=dict(j, iprd_deferred_payment=[deferred(amount=20e6)]), checks=False))["iprd_adjustment"]
    assert d["fy_with_charge"] == ["2023-12-31"] and not d["recurrent"], d
    assert next(p for p in d["periods"] if p["period"] == "2025-12-31")["recurrence_excluded"] == "deferred_payment_of"
    # a $0-cash FY2025 charge whose residual is declared paid in shares: counted, and a whole declaration claims it
    f0 = _facts(expense={2023: 15e6, 2025: 20e6}, cash={2023: 15e6, 2025: 0.0})
    j0 = {"iprd_cash_flow_check": [_shares_check("2025-12-31", 20e6)]}
    u0 = _ok(_run(f0, judgment=j0, checks=False))["iprd_adjustment"]
    p25 = next(p for p in u0["periods"] if p["period"] == "2025-12-31")
    assert p25["residual_paid_in_shares"] == 20e6 and p25["deducted"] == 0.0, p25
    assert u0["fy_with_charge"] == ["2023-12-31", "2025-12-31"] and u0["recurrent"] and u0["total"] == 15e6, u0
    d0 = _ok(_run(f0, judgment=dict(j0, iprd_deferred_payment=[deferred(amount=20e6)]), checks=False))["iprd_adjustment"]
    assert d0["fy_with_charge"] == ["2023-12-31"] and not d0["recurrent"] and d0["total"] == 15e6, d0


def test_recurrence_materiality_reads_the_acquisitions_expense_not_the_cash_deducted():
    """[Codex review r28 of PR #47, #4334315278] Round 27 counted each year by its own expense, but the gate beside
    the count (`material`) still read the cash the window deducted: two $100M acquisitions expensed in FY2023 and
    FY2024 with $1 paid in each year and nothing paid later read fy_with_charge [FY2023, FY2024] yet material false
    ($2 deducted), so ACQUIRED_IPRD_RECURRENT stayed silent; with $0 cash `total > 0` failed outright; paying the
    same expenses in full made it recurrent — cash timing decided again. Recurrence materiality is now its own figure:
    the USD expense of every period counted as a charge (the TTM YTD leg's too on a TTM base), less a declared
    installment part, per share on the run's denominator and ADS ratio against the same base and 5% threshold
    (recorded as recurrence_expense_total / recurrence_materiality when 2 or more FY charge years are counted).
    ACQUIRED_IPRD_CHARGE keeps the deduction's materiality ($2: no CHARGE flag). A cash settlement — a pre-window
    deal's declared installment here — is not a charge of the window, so it never makes tiny in-window charges
    material; and a counted year whose expense has no USD figure (no FX rate) makes the figure unknown, read as
    material (the `materiality is None` convention; that run is gated ACQUIRED_IPRD_UNCONVERTED)."""
    for cash in ({2023: 1.0, 2024: 1.0}, {2023: 0.0, 2024: 0.0}):
        n = _ok(_run(_facts(expense={2023: 100e6, 2024: 100e6}, cash=cash)))
        b = n["iprd_adjustment"]
        assert b["fy_with_charge"] == ["2023-12-31", "2024-12-31"] and b["recurrent"], (cash, b)
        assert b["total"] == sum(cash.values()) and not b["material"], (cash, b)
        assert b["recurrence_expense_total"] == 200e6, (cash, b)
        assert abs(b["recurrence_materiality"] - _r28_mat(n, 200e6)) < 1e-12 and b["recurrence_materiality"] > 1.0, b
        rf = flags(n, "ACQUIRED_IPRD_RECURRENT")
        assert len(rf) == 1 and "FY2023, FY2024 (2 of the last 3" in rf[0] and "$200,000,000" in rf[0], (cash, rf)
        assert not flags(n, "ACQUIRED_IPRD_CHARGE"), cash
    # two tiny in-window charges ($1M each, ~1% of the base) beside a $30M FY2025 cash-only payment declared the
    # deferred consideration of a deal expensed before the window: deducted (CHARGE fires), not recurrent
    f = _facts(expense={2022: 40e6, 2023: 1e6, 2024: 1e6}, cash={2022: 10e6, 2023: 1e6, 2024: 1e6, 2025: 30e6})
    decl = deferred(period="2025-12-31", amount=30e6, first="2022-12-31", source=PRE_SRC, deal="Old Bio", contingent=PRE_CT)
    m = _ok(_run(f, judgment={"iprd_deferred_payment": [decl]}))
    mb = m["iprd_adjustment"]
    assert mb["total"] == 32e6 and mb["material"] and flags(m, "ACQUIRED_IPRD_CHARGE"), mb
    assert mb["fy_with_charge"] == ["2023-12-31", "2024-12-31"] and not mb["recurrent"], mb
    assert mb["recurrence_expense_total"] == 2e6 and mb["recurrence_materiality"] < 0.05, mb
    assert not flags(m, "ACQUIRED_IPRD_RECURRENT")
    # a counted year with no USD figure: FY2023 $1M paid in cash, FY2024 EUR 1M expensed with no FX rate and no cash
    fx = _eur_expense(1e6, start="2024-01-01", end="2024-12-31", filed="2025-02-20")
    _fy(fx, EXPENSE, 2023, 1e6)
    _fy(fx, CASH, 2023, 1e6)
    x = _ok(_run(fx, checks=False))
    xb = x["iprd_adjustment"]
    assert next(p for p in xb["periods"] if p["period"] == "2024-12-31")["excluded"] == "non_usd_no_rate", xb
    assert xb["fy_with_charge"] == ["2023-12-31", "2024-12-31"] and xb["recurrent"], xb
    assert xb["recurrence_materiality"] is None and xb["recurrence_expense_unknown_usd"] == ["FY2024"], xb
    assert flags(x, "ACQUIRED_IPRD_UNCONVERTED") and flags(x, "ACQUIRED_IPRD_RECURRENT")
    # a TTM base: the current-YTD leg's own expense is in the figure; cash settling an FY charge is not added on top
    ttm = _ttm_doc(2.1, 100e6)
    ttm["inputs"]["ocf"]["ytd_current_period"] = ["2026-01-01", "2026-03-31"]
    t = _facts(expense={2024: 3e6, 2025: 3e6}, cash={2024: 3e6, 2025: 3e6})
    _ytd(t, EXPENSE, "2026-01-01", "2026-03-31", 10e6, "2026-04-29", fp="Q1")
    _ytd(t, CASH, "2026-01-01", "2026-03-31", 10e6, "2026-04-29", fp="Q1")
    tb = _ok(_run(t, extra=["--ttm"], ttm=ttm))["iprd_adjustment"]
    assert tb["fy_with_charge"] == ["2024-12-31", "2025-12-31"] and tb["recurrent"], tb
    assert tb["recurrence_expense_total"] == 16e6 and abs(tb["recurrence_materiality"] - 16e6 / 100e6 / 2.1) < 1e-12, tb
    s = _facts(expense={2024: 100e6, 2025: 100e6}, cash={2024: 100e6, 2025: 0.0})
    _ytd(s, CASH, "2026-01-01", "2026-03-31", 100e6, "2026-04-29", fp="Q1")
    sb = _ok(_run(s, extra=["--ttm"], ttm=ttm))["iprd_adjustment"]
    assert sb["total"] == 200e6 and sb["recurrence_expense_total"] == 200e6 and sb["recurrent"], sb
    # one charge year: the gate cannot decide, so no recurrence figure is recorded (HALO's committed block)
    one = _ok(_run(_facts(expense={2025: 20e6})))["iprd_adjustment"]
    assert "recurrence_expense_total" not in one and "recurrence_materiality" not in one, one


# ===========================================================================
# [Codex review r28 of PR #47, re-verification of d7ccc6e] a declared installment is measured against the period's own
# charge, never only its cash; an iprd_amortized base needs a deducted charge to carry
# ===========================================================================
def test_a_partly_declared_installment_comes_first_from_the_cash_beyond_the_periods_own_expense():
    """[Codex review r28 of PR #47, re-verification of d7ccc6e] iprd_recurrence_expense took max(0, expense - declared)
    for a partly declared period, though the declared installment of a deal expensed BEFORE the window sits in the
    period's cash beyond its own expense. Old Bio: $40M expensed in FY2022, $10M paid, $30M deferred. FY2023: a new
    $6M deal, paid. FY2025: another new $6M deal plus Old Bio's $30M, so $6M expensed and $36M paid. Declaring the
    $30M (correctly) an installment of Old Bio left FY2025 counted (30 < 36: partly declared) but subtracted the $30M
    from its $6M expense, so the new deal's own expense dropped out of the figure: $6M = 3.1% of the base, not
    recurrent, while the undeclared run read $12M = 6.1%, recurrent — declaring the installment silenced the flag.
    The declared amount now comes first from the cash beyond the period's own expense and only the rest from the
    expense: FY2025 keeps its $6M, recurrent either way. A declaration reaching into the expense ($33M: $3M of it)
    and an accrued period ($0 cash, $5M of a $20M expense declared) still take that part off."""
    f = lambda: _facts(expense={2022: 40e6, 2023: 6e6, 2025: 6e6}, cash={2022: 10e6, 2023: 6e6, 2025: 36e6})
    ct = {"value": 40e6, "source": PRE_CT["source"]}
    decl = lambda amt: deferred(period="2025-12-31", amount=amt, first="2022-12-31", source=PRE_SRC, deal="Old Bio",
                                contingent=ct)
    for j in (None, {"iprd_deferred_payment": [decl(30e6)]}):
        n = _ok(_run(f(), judgment=j))
        b = n["iprd_adjustment"]
        assert b["total"] == 42e6 and b["fy_with_charge"] == ["2023-12-31", "2025-12-31"], (j, b)
        assert b["recurrence_expense_total"] == 12e6, (j, b)
        assert abs(b["recurrence_materiality"] - _r28_mat(n, 12e6)) < 1e-12 and b["recurrent"], (j, b)
        assert len(flags(n, "ACQUIRED_IPRD_RECURRENT")) == 1, j
    p25 = next(p for p in b["periods"] if p["period"] == "2025-12-31")
    assert p25.get("recurrence_excluded") is None and p25["deferred_payment_of"][0]["amount"] == 30e6, p25
    # $33M declared: $30M is the cash beyond the expense, $3M comes off FY2025's own $6M
    m = _ok(_run(f(), judgment={"iprd_deferred_payment": [decl(33e6)]}))["iprd_adjustment"]
    assert m["fy_with_charge"] == ["2023-12-31", "2025-12-31"] and m["recurrence_expense_total"] == 9e6, m
    # the whole $36M declared: the year leaves the count
    w = _ok(_run(f(), judgment={"iprd_deferred_payment": [decl(36e6)]}))["iprd_adjustment"]
    assert w["fy_with_charge"] == ["2023-12-31"] and not w["recurrent"] and w["total"] == 42e6, w
    # an accrued year (cash $0 <= expense): the declared part comes off the expense, as before
    a = _ok(_run(_facts(expense={2023: 15e6, 2025: 20e6}, cash={2023: 15e6, 2025: 0.0}),
                 judgment={"iprd_deferred_payment": [deferred(amount=5e6)]}))["iprd_adjustment"]
    assert a["fy_with_charge"] == ["2023-12-31", "2025-12-31"] and a["recurrence_expense_total"] == 30e6, a


def test_a_whole_installment_declaration_is_measured_against_the_periods_own_expense_not_its_cash():
    """[Codex review r28 of PR #47, re-verification of d7ccc6e] iprd_apply_deferred measured a declaration against the
    record's amount (its cash) whenever that was positive, and fell back to the expense only at $0 cash. A $100M
    FY2025 acquisition with $1 paid in the year (the rest accrued) beside a FY2023 deal: declaring the $1 an
    installment of the FY2023 deal made the declaration "whole", so FY2025 left the recurrence count and
    ACQUIRED_IPRD_RECURRENT went silent ($20M paid, $20M declared: the same) — though a charge year is its own expense
    whatever its cash timing (rounds 27/28), and Andrew's 2026-10-20 rule takes a year out only when its WHOLE charge
    is declared. A declaration is now measured against the larger of the record's amount and its own USD expense:
    $1 or $20M declared is a part (the year still counts, for its $100M less the declared part), the whole $100M
    leaves the count, more than $100M is refused. The deduction is never touched by a declaration on a charge year."""
    for c25 in (1.0, 20e6):
        f = lambda: _facts(expense={2023: 15e6, 2025: 100e6}, cash={2023: 15e6, 2025: c25})
        u = _ok(_run(f()))["iprd_adjustment"]
        assert u["fy_with_charge"] == ["2023-12-31", "2025-12-31"] and u["recurrent"], (c25, u)
        assert u["total"] == 15e6 + c25 and u["recurrence_expense_total"] == 115e6, (c25, u)
        n = _ok(_run(f(), judgment={"iprd_deferred_payment": [deferred(amount=c25)]}))
        b = n["iprd_adjustment"]
        p25 = next(p for p in b["periods"] if p["period"] == "2025-12-31")
        assert p25.get("recurrence_excluded") is None and p25["deferred_payment_of"][0]["amount"] == c25, (c25, p25)
        assert b["fy_with_charge"] == ["2023-12-31", "2025-12-31"] and b["recurrent"], (c25, b)
        assert b["recurrence_expense_total"] == 115e6 - c25 and b["total"] == u["total"], (c25, b)
        assert flags(n, "ACQUIRED_IPRD_RECURRENT"), c25
        w = _ok(_run(f(), judgment={"iprd_deferred_payment": [deferred(amount=100e6)]}))["iprd_adjustment"]
        assert w["fy_with_charge"] == ["2023-12-31"] and not w["recurrent"] and w["total"] == u["total"], (c25, w)
        assert w["recurrence_excluded"] == [{"period": "2025-12-31", "window": "fy", "deal": "Test Bio",
                                             "first_charged_period": "2023-12-31", "amount": 100e6}], (c25, w)
        _refused(_run(f(), judgment={"iprd_deferred_payment": [deferred(amount=101e6)]}), "more than the period's")
    # cash above the expense: the cash is the period's whole charge, as before ($20M of $25M declared is a part: $5M
    # of it is the cash beyond the $20M expense, $15M comes off the expense, $5M of FY2025's own expense still counts)
    g = _facts(expense={2023: 15e6, 2025: 20e6}, cash={2023: 15e6, 2025: 25e6})
    gp = _ok(_run(g, judgment={"iprd_deferred_payment": [deferred(amount=20e6)]}))["iprd_adjustment"]
    assert gp["fy_with_charge"] == ["2023-12-31", "2025-12-31"] and gp["recurrence_expense_total"] == 20e6, gp
    gw = _ok(_run(g, judgment={"iprd_deferred_payment": [deferred(amount=25e6)]}))["iprd_adjustment"]
    assert gw["fy_with_charge"] == ["2023-12-31"] and not gw["recurrent"], gw


def test_an_iprd_amortized_base_needs_a_deducted_fy_charge_to_carry():
    """[Codex review r28 of PR #47, re-verification of d7ccc6e] Since round 28 ACQUIRED_IPRD_RECURRENT reads the
    acquisitions' expense, so it fires with nothing deducted: two $100M acquisitions expensed with $0 cash. The flag
    told the worker to declare an iprd_amortized base_override, whose figures are the FY charges the window DEDUCTED
    ([0, 0, 0]); the engine accepted that no-op declaration but kept treatment "none" (nothing deducted), and
    make_score then always refused it ("the engine run did not carry it"), so the worker could not get through.
    Nothing deducted in the last 3 FY is nothing to amortize: the engine refuses such a declaration
    (BAD_BASE_OVERRIDE) and the RECURRENT flag no longer asks for one — it says the base has no deducted charge to
    carry and asks for the recurrence assessment. With $1 paid in each year the declaration is accepted, and the flag
    names what the amortized base carries: the deducted FY figures (the cash), not the $200M expense the gate
    measured."""
    f = lambda cash: _facts(expense={2023: 100e6, 2024: 100e6}, cash=cash)
    zero = {2023: 0.0, 2024: 0.0}
    n = _ok(_run(f(zero)))
    b = n["iprd_adjustment"]
    assert b["recurrent"] and b["total"] == 0.0 and b["treatment"] == "none", b
    rf = flags(n, "ACQUIRED_IPRD_RECURRENT")
    assert len(rf) == 1 and "declare an iprd_amortized" not in rf[0] and "nothing to amortize" in rf[0], rf
    d = amortized_decl(n, reason="recurrent")
    assert d["figures"] == [0.0, 0.0, 0.0], d
    out = _run(f(zero), extra=["--base-oe-ps", repr(d["value"])], judgment={"base_override": d})
    assert out["exit"] == 3 and "BAD_BASE_OVERRIDE" in out["stdout"] and "nothing to amortize" in out["stdout"], \
        (out["exit"], out["stdout"][-1500:])
    one = {2023: 1.0, 2024: 1.0}
    m = _ok(_run(f(one)))
    mf = flags(m, "ACQUIRED_IPRD_RECURRENT")
    assert len(mf) == 1 and "declare an iprd_amortized" in mf[0] and "$1 / $1 / $0" in mf[0], mf
    assert "not the expense" in mf[0] and "$200,000,000" in mf[0], mf
    d1 = amortized_decl(m, reason="recurrent")
    a = _ok(_run(f(one), extra=["--base-oe-ps", repr(d1["value"])], judgment={"base_override": d1}))
    assert a["iprd_adjustment"]["treatment"] == "amortized_in_base", a["iprd_adjustment"]
    af = flags(a, "ACQUIRED_IPRD_RECURRENT")
    assert len(af) == 1 and "$1 / $1 / $0" in af[0] and "not the expense" in af[0], af


# ===========================================================================
# [Codex review r29 of PR #47] a deal's first charge is a period with its OWN acquired-IPR&D expense; a year whose
# whole charge is unknown in USD can never be declared whole
# ===========================================================================
GHOST_SRC = "SYN 10-K FY2024 (0000999001-25-000003) Note 5 'Asset acquisition', p. 70: Ghost Bio acquired IPR&D"


def _r29_ghost(amount=50e6):
    return deferred(amount=amount, first="2024-12-31", source=GHOST_SRC, deal="Ghost Bio")


def _r29_settled(exp24=None, cash23=0.0):
    """FY2023: a $100M acquisition expensed with $0 cash (accrued). FY2024: $100M on the cash tag that settles it (no
    expense; `exp24` files one: $0, or a negative reversal). FY2025: a separate $50M acquisition, paid."""
    exp = {2023: 100e6, 2025: 50e6}
    if exp24 is not None:
        exp[2024] = exp24
    return _facts(expense=exp, cash={2023: cash23, 2024: 100e6, 2025: 50e6})


def test_a_first_charge_inside_the_window_must_carry_its_own_acquired_iprd_expense():
    """[Codex review r29 of PR #47, #4335127654] iprd_apply_deferred accepted an in-window first_charged_period whose
    record had amount > 0 or expense > 0, so the automatic settlement of the window's unpaid remainder — cash with no
    expense of its own (deferred_payment) — passed on its cash alone. $100M expensed in FY2023 with $0 cash, its
    $100M cash settlement in FY2024 and a distinct $50M acquisition in FY2025: declaring FY2025 an installment of a
    deal "first charged" in FY2024 was accepted, FY2025 left the recurrence count and ACQUIRED_IPRD_RECURRENT went
    silent. A first charge must now be a period whose record carries its OWN positive acquired-IPR&D expense (the
    iprd_own_charge rule: the detector figure, USD or native, > 0, however it was paid): a cash settlement (no
    expense, a $0 one or a negative reversal) and a $0-expense period are refused (BAD_IPRD_DEFERRED_PAYMENT). A real
    first charge — accrued with $0 cash, paid in shares, or filed only in a currency with no FX rate (which had been
    refused: its record has no USD amount) — is accepted; so is a pre-window first charge (companyfacts' expense
    fact). The deduction is never touched."""
    for exp24 in (None, 0.0, -10e6):
        u = _ok(_run(_r29_settled(exp24)))["iprd_adjustment"]
        p24 = next(p for p in u["periods"] if p["period"] == "2024-12-31")
        assert p24.get("deferred_payment") and p24["deducted"] == 100e6, (exp24, p24)
        assert u["fy_with_charge"] == ["2023-12-31", "2025-12-31"] and u["recurrent"], (exp24, u)
        out = _run(_r29_settled(exp24), judgment={"iprd_deferred_payment": [_r29_ghost()]})
        _refused(out, "first_charged_period 2024-12-31 lies inside the engine's window")
        assert "no acquired-IPR&D charge there" in out["stdout"], out["stdout"][-1500:]
        why = "is negative (-10,000,000, a reversal)" if exp24 else "settles an earlier charge"
        assert why in out["stdout"], (exp24, out["stdout"][-1500:])
    # a $0-expense period whose cash settles nothing (no unpaid remainder): no charge there either
    z = _facts(expense={2024: 0.0, 2025: 50e6}, cash={2024: 30e6, 2025: 50e6})
    _refused(_run(z, judgment={"iprd_deferred_payment": [_r29_ghost()]}), "no acquired-IPR&D charge there")
    # the same filer, the installment declared against the deal that really charged FY2023: accepted (Andrew's rule)
    n = _ok(_run(_r29_settled(), judgment={"iprd_deferred_payment": [deferred(amount=50e6)]}))
    b = n["iprd_adjustment"]
    p25 = next(p for p in b["periods"] if p["period"] == "2025-12-31")
    assert p25["deferred_payment_of"][0]["first_charge_evidence"] == "window_record", p25
    assert b["fy_with_charge"] == ["2023-12-31"] and not b["recurrent"] and b["total"] == 150e6, b
    # a first charge paid in shares (no cash, the expense excluded paid_in_shares): its own expense — accepted
    sh = _facts(expense={2023: 15e6, 2025: 20e6}, cash={2025: 20e6})
    j = {"iprd_cash_flow_check": [_r28_check("2023-12-31", 15e6, "paid_in_shares")] + auto_checks(sh)[1:],
         "iprd_deferred_payment": [deferred()]}
    assert [c["period"] for c in j["iprd_cash_flow_check"]] == ["2023-12-31", "2025-12-31"], j
    s = _ok(_run(sh, judgment=j))["iprd_adjustment"]
    p23 = next(p for p in s["periods"] if p["period"] == "2023-12-31")
    assert p23["excluded"] == "paid_in_shares" and s["fy_with_charge"] == ["2023-12-31"], s
    # a first charge filed only in EUR with no FX rate (excluded non_usd_no_rate, no USD amount): its own expense too
    eur = _facts(expense={2025: 20e6}, cash={2025: 20e6})
    _syn_put(eur, EXPENSE, "EUR", _ctx("2023-01-01", "2023-12-31", 15e6, filed="2024-02-20"))
    m = _ok(_run_fx(eur, {}, judgment={"iprd_deferred_payment": [deferred()]}))
    mb = m["iprd_adjustment"]
    p23 = next(p for p in mb["periods"] if p["period"] == "2023-12-31")
    assert p23["excluded"] == "non_usd_no_rate" and p23.get("amount") is None and p23["expense_native"] == 15e6, p23
    p25 = next(p for p in mb["periods"] if p["period"] == "2025-12-31")
    assert p25["recurrence_excluded"] == "deferred_payment_of", p25
    assert p25["deferred_payment_of"][0]["first_charge_evidence"] == "window_record", p25
    assert E.iprd_unresolved(m), "still gated ACQUIRED_IPRD_UNCONVERTED"
    # before the window: companyfacts' expense fact is the evidence, as before
    w = _ok(_with_2021_charge([deferred(first="2021-12-31", source=OK_SRC_2021)]))["iprd_adjustment"]
    p25 = next(p for p in w["periods"] if p["period"] == "2025-12-31")
    assert p25["deferred_payment_of"][0]["first_charge_evidence"] == "companyfacts_expense_fact", p25


def _r29_eur25(cash25=40e6, eur_cash=False):
    """FY2023: Test Bio's $15M acquired-IPR&D expense, paid. FY2025: a EUR 100M expense with no FX rate (even fetched)
    beside a $40M USD cash outflow (eur_cash: beside EUR 40M of cash with no rate; cash25 None: no cash fact)."""
    f = _facts(expense={2023: 15e6}, cash={2023: 15e6, **({2025: cash25} if (cash25 and not eur_cash) else {})})
    _syn_put(f, EXPENSE, "EUR", _ctx("2025-01-01", "2025-12-31", 100e6, filed="2026-02-20"))
    if eur_cash:
        _syn_put(f, CASH, "EUR", _ctx("2025-01-01", "2025-12-31", cash25, filed="2026-02-20"))
    return f


def _r29_reason(facts, entries, judgment=None):
    """iprd_apply_deferred's refusal reasons for `entries` on the run's own detection (no FX rate for EUR)."""
    fy = ["2023-12-31", "2024-12-31", "2025-12-31"]
    iprd = E.iprd_detect(facts, fy, fx_rates={}, checks=(judgment or {}).get("iprd_cash_flow_check") or auto_checks(facts))
    refused, _ = E.iprd_apply_deferred(iprd, entries, fy, facts)
    return [r["reason"] for r in refused]


def test_a_year_whose_whole_charge_is_unknown_in_usd_can_never_be_declared_whole():
    """[Codex review r29 of PR #47, #4335127660] For a positive foreign-currency expense with no FX rate beside usable
    USD cash, _iprd_claimable_expense returned None, so the period's "whole charge" stayed its cash: EUR 100M expensed
    (USD value unknown) with $40M paid in FY2025 beside Test Bio's FY2023 charge — declaring the $40M an installment
    of Test Bio made the declaration "whole", FY2025 left the recurrence count and ACQUIRED_IPRD_RECURRENT went silent
    (nothing gated the run), though its own expense may be far larger. A charge year's declaration is whole only when
    the year's whole charge (the larger of its cash and its own USD expense) is known in USD. The existing convention
    for counted years with no USD figure (an unconvertible expense with no usable cash, an unconvertible parallel
    detector tag) is a refusal, "names no acquired-IPR&D charge": every declaration on a year whose own expense or
    cash has no USD figure is now refused with that same message (BAD_IPRD_DEFERRED_PAYMENT), whatever its amount, so
    the year stays in the recurrence count — the FX-less cash-basis year, the same with its residual declared paid in
    shares, and a USD expense beside cash with no rate. The deduction is unchanged. With the rate, the expense
    converts and a declaration is measured against it as before ($40M is a part, $100M the whole)."""
    u = _ok(_run(_r29_eur25()))
    b = u["iprd_adjustment"]
    p25 = next(p for p in b["periods"] if p["period"] == "2025-12-31")
    assert p25["expense"] is None and p25["expense_native"] == 100e6 and p25["amount"] == 40e6, p25
    assert p25["excluded"] is None and b["total"] == 55e6, (p25, b)
    assert b["fy_with_charge"] == ["2023-12-31", "2025-12-31"] and b["recurrent"] and E.iprd_unresolved(u) is None, b
    for amt in (40e6, 20e6):
        out = _run(_r29_eur25(), judgment={"iprd_deferred_payment": [deferred(amount=amt)]})
        _refused(out, "FY 2025-12-31 names no acquired-IPR&D charge in this run's window")
        assert "has no USD figure" in out["stdout"] and "stays in the recurrence count" in out["stdout"], \
            out["stdout"][-1500:]
    # the same message as the existing convention: an unconvertible expense with no usable cash (and, below, a USD
    # expense beside cash with no rate; the residual declared paid in shares)
    msg = _r29_reason(_r29_eur25(), [deferred(amount=40e6)])
    assert len(msg) == 1 and "100,000,000 EUR" in msg[0], msg
    assert _r29_reason(_r29_eur25(cash25=None), [deferred(amount=40e6)]) == msg
    sh = {"iprd_cash_flow_check": [dict(_r21_check(), period="2025-12-31")] + auto_checks(_r29_eur25())}
    s = _ok(_run(_r29_eur25(), judgment=sh))["iprd_adjustment"]
    assert next(p for p in s["periods"] if p["period"] == "2025-12-31").get("residual_paid_in_shares_unknown_usd"), s
    assert _r29_reason(_r29_eur25(), [deferred(amount=40e6)], judgment=sh) == msg
    _refused(_run(_r29_eur25(), judgment=dict(sh, iprd_deferred_payment=[deferred(amount=40e6)])), "has no USD figure")
    # a USD expense beside cash with no FX rate: its whole charge (the larger of the two) is unknown in USD as well
    ue = _facts(expense={2023: 15e6, 2025: 100e6}, cash={2023: 15e6})
    _syn_put(ue, CASH, "EUR", _ctx("2025-01-01", "2025-12-31", 40e6, filed="2026-02-20"))
    r = _r29_reason(ue, [deferred(amount=100e6)])
    assert len(r) == 1 and r[0].startswith("FY 2025-12-31 names no acquired-IPR&D charge") and "40,000,000 EUR" in r[0], r
    # with the FX rate the expense converts: $40M is a part (the year still counts), $100M the whole
    rate = {"EUR": {"2025-12-31": 1.0}}
    part = _ok(_run_fx(_r29_eur25(), rate, judgment={"iprd_deferred_payment": [deferred(amount=40e6)]}))["iprd_adjustment"]
    assert part["fy_with_charge"] == ["2023-12-31", "2025-12-31"] and part["recurrent"] and part["total"] == 55e6, part
    whole = _ok(_run_fx(_r29_eur25(), rate, judgment={"iprd_deferred_payment": [deferred(amount=100e6)]}))["iprd_adjustment"]
    assert whole["fy_with_charge"] == ["2023-12-31"] and not whole["recurrent"] and whole["total"] == 55e6, whole


def _r29_unit_conflict(tag):
    """FY2023: Test Bio's $15M acquired-IPR&D expense, paid. FY2025: $40M expensed and $40M paid in USD, and `tag` (the
    expense tag or the cash tag) also filed for FY2025 at EUR 100M with no FX rate (even fetched): the two units
    disagree (unit_conflict, the EUR figure's usd None) and the USD fact is used."""
    f = _facts(expense={2023: 15e6, 2025: 40e6}, cash={2023: 15e6, 2025: 40e6})
    _syn_put(f, tag, "EUR", _ctx("2025-01-01", "2025-12-31", 100e6, filed="2026-02-20"))
    return f


def test_a_unit_with_no_usd_figure_beside_the_usd_fact_used_leaves_the_whole_charge_unknown():
    """[Codex review r29 of PR #47, review note] iprd_whole_charge_unknown read only the record's chosen figures, so a
    year whose expense tag (or cash tag) also carries a positive fact in a unit with no FX rate — EUR 100M beside the
    USD 40M used (unit_conflict, its usd None) — read "whole" at $40M: a $40M declaration took FY2025 out of the
    recurrence count though the EUR filing says the charge may be far larger. Such a year's whole charge is unknown
    in USD too: every declaration on it is refused with the round-29 message (NEEDS_MAIN_AGENT: currency) and the year
    stays counted; the deduction is unchanged. A USD 0 fact beside the EUR one (the EUR figure used: its own expense
    unknown) is refused with the message it had."""
    for tag in (EXPENSE, CASH):
        f = _r29_unit_conflict(tag)
        b = _ok(_run(f))["iprd_adjustment"]
        p25 = next(p for p in b["periods"] if p["period"] == "2025-12-31")
        uc = p25["unit_conflict"][tag]
        assert uc["used"] == "USD" and uc["units"]["EUR"]["usd"] is None and uc["units"]["EUR"]["native"] == 100e6, p25
        assert p25["expense"] == 40e6 and p25["amount"] == 40e6 and p25["excluded"] is None, p25
        assert b["fy_with_charge"] == ["2023-12-31", "2025-12-31"] and b["recurrent"] and b["total"] == 55e6, (tag, b)
        why = E.iprd_whole_charge_unknown(p25)
        assert why and tag in why and "100,000,000 EUR" in why and "USD" in why, (tag, why)
        for amt in (40e6, 20e6):
            r = _r29_reason(f, [deferred(amount=amt)])
            assert len(r) == 1 and r[0].startswith("FY 2025-12-31 names no acquired-IPR&D charge in this run's window"), r
            assert why in r[0] and "stays in the recurrence count (NEEDS_MAIN_AGENT: currency)" in r[0], r
        out = _run(f, judgment={"iprd_deferred_payment": [deferred(amount=40e6)]})
        _refused(out, "names no acquired-IPR&D charge")
        assert "NEEDS_MAIN_AGENT: currency" in out["stdout"], out["stdout"][-1500:]
    # USD 0 beside EUR 100M on the expense tag: the EUR fact is used, its own expense has no USD figure — unchanged
    f = _facts(expense={2023: 15e6, 2025: 0.0}, cash={2023: 15e6, 2025: 40e6})
    _syn_put(f, EXPENSE, "EUR", _ctx("2025-01-01", "2025-12-31", 100e6, filed="2026-02-20"))
    assert _r29_reason(f, [deferred(amount=40e6)]) == [
        "FY 2025-12-31 names no acquired-IPR&D charge in this run's window (2023-12-31, 2024-12-31, 2025-12-31) that a "
        "declaration can be measured against: its own acquired-IPR&D expense (100,000,000 EUR) has no USD figure (no FX "
        "rate, even fetched), so its whole charge (the largest of its own expense and its cash, in every unit filed) is "
        "unknown in USD and no "
        "declaration on it can be whole — none is applied and the year stays in the recurrence count "
        "(NEEDS_MAIN_AGENT: currency)"]


R29_EUR_RATE = {"EUR": {"2025-12-31": 1.08, "2025-12-30": 1.08}}


def test_a_years_own_charge_is_its_largest_figure_in_every_unit_filed():
    """[Codex review r29 of PR #47, polish review] The whole-declaration test and the recurrence materiality read a
    year's own charge from the record's chosen figures only, so a tag filed in two units that disagree — EUR 100M (at
    1.08: $108M) on the expense tag or the cash tag beside the USD 40M expensed and paid (unit_conflict, the USD fact
    used: round 15) — read $40M: a $40M declaration was "whole" and took FY2025 out of the recurrence count, $108M
    was refused as more than the charge, and the materiality read the $40M. One rule now (iprd_own_charge_usd, used
    by both): the year's own charge is the largest positive figure on its acquired-IPR&D expense tags and cash tag in
    every unit filed for the period (each other unit converted at the run's rate), never less than its amount (the
    cash deducted); its own expense the largest on the expense tags. $40M declared is a part (the year stays
    counted), $108M the whole, more than $108M is refused (the cap). The materiality reads that own expense less a
    declared part taken first from the charge beyond it (round 28): $108M with EUR on the expense tag, $40M with EUR on
    the cash tag (cash beyond the expense). When any positive figure on those tags has no USD figure the year's whole
    charge is unknown in USD: no declaration on it is whole (round 29). [Codex review r29 of PR #47, second polish
    review] Its recurrence figure is unknown, read as material, only when the figure with no USD value is on the
    expense side (the own expense is unknown); EUR on the cash tag with no rate leaves the $40M expense read. The
    deduction never changes."""
    for tag, own_exp in ((EXPENSE, 108e6), (CASH, 40e6)):
        u = _ok(_run_fx(_r29_unit_conflict(tag), R29_EUR_RATE))
        b = u["iprd_adjustment"]
        p25 = next(p for p in b["periods"] if p["period"] == "2025-12-31")
        uc = p25["unit_conflict"][tag]
        assert uc["used"] == "USD" and uc["units"]["EUR"]["usd"] == 108e6, (tag, p25)
        assert p25["expense"] == 40e6 and p25["amount"] == 40e6 and p25["excluded"] is None and b["total"] == 55e6, p25
        assert E.iprd_whole_charge_unknown(p25) is None and E.iprd_own_charge_usd(p25) == (108e6, own_exp), (tag, p25)
        assert b["fy_with_charge"] == ["2023-12-31", "2025-12-31"] and b["recurrent"], (tag, b)
        assert b["recurrence_expense_total"] == 15e6 + own_exp, (tag, b)
        assert abs(b["recurrence_materiality"] - _r28_mat(u, 15e6 + own_exp)) < 1e-12, (tag, b)
        # $40M declared: a part of the $108M — the year stays counted, for its own expense less what the charge beyond
        # it cannot hold (EUR on the expense tag: $108M - $40M; on the cash tag the $68M of cash beyond the expense holds it)
        n = _ok(_run_fx(_r29_unit_conflict(tag), R29_EUR_RATE, judgment={"iprd_deferred_payment": [deferred(amount=40e6)]}))
        pb = n["iprd_adjustment"]
        q25 = next(p for p in pb["periods"] if p["period"] == "2025-12-31")
        assert q25.get("recurrence_excluded") is None and q25["deferred_payment_of"][0]["amount"] == 40e6, (tag, q25)
        assert pb["fy_with_charge"] == ["2023-12-31", "2025-12-31"] and pb["recurrent"] and pb["total"] == 55e6, (tag, pb)
        assert pb["recurrence_expense_total"] == 15e6 + (68e6 if tag == EXPENSE else 40e6), (tag, pb)
        assert flags(n, "ACQUIRED_IPRD_RECURRENT"), tag
        # the whole $108M: the year leaves the count; the deduction is unchanged
        w = _ok(_run_fx(_r29_unit_conflict(tag), R29_EUR_RATE,
                        judgment={"iprd_deferred_payment": [deferred(amount=108e6)]}))["iprd_adjustment"]
        assert w["fy_with_charge"] == ["2023-12-31"] and not w["recurrent"] and w["total"] == 55e6, (tag, w)
        assert w["recurrence_excluded"][0]["amount"] == 108e6, (tag, w)
        # more than the whole: refused (the existing cap)
        _refused(_run_fx(_r29_unit_conflict(tag), R29_EUR_RATE, judgment={"iprd_deferred_payment": [deferred(amount=109e6)]}),
                 "FY 2025-12-31's declarations sum to 109,000,000, more than the period's charge 108,000,000")
        # no FX rate for the EUR figure (even fetched): the year's whole charge is unknown in USD (no declaration
        # applies); its recurrence figure is unknown (read as material) only when the EUR figure is on the expense
        # side — on the cash tag the $40M USD expense is known and read (the second polish review's final rule)
        x = _ok(_run(_r29_unit_conflict(tag)))
        xb = x["iprd_adjustment"]
        x25 = next(p for p in xb["periods"] if p["period"] == "2025-12-31")
        assert E.iprd_whole_charge_unknown(x25), (tag, x25)
        assert xb["recurrent"] and xb["total"] == 55e6, (tag, xb)
        rf = flags(x, "ACQUIRED_IPRD_RECURRENT")
        if tag == EXPENSE:
            assert E.iprd_own_charge_usd(x25) == (None, None) and E.iprd_recurrence_expense(x25) is None, x25
            assert xb["recurrence_materiality"] is None and xb["recurrence_expense_unknown_usd"] == ["FY2025"], xb
            assert xb["recurrence_expense_total"] == 15e6, xb
            assert len(rf) == 1 and "FY2025: its acquired-IPR&D expense has no USD figure" in rf[0], rf
        else:
            assert E.iprd_own_charge_usd(x25) == (None, 40e6) and E.iprd_recurrence_expense(x25) == 40e6, x25
            assert xb["recurrence_expense_total"] == 55e6 and "recurrence_expense_unknown_usd" not in xb, xb
            assert abs(xb["recurrence_materiality"] - _r28_mat(x, 55e6)) < 1e-12, xb
            assert len(rf) == 1 and "no USD figure" not in rf[0], rf


def _r29_parallel(case):
    """FY2023: Test Bio's $15M acquired-IPR&D expense, paid. FY2025: $40M expensed on the current detector tag and $40M
    paid, in USD, and the parallel (pre-2022) expense tag ResearchAndDevelopmentInProcess also filed for FY2025, per
    case: A EUR 100M only (at 1.08, $108M: expense_tags_conflict, no unit conflict); B USD 40M + EUR 100M
    (unit_conflict on the parallel tag); C USD 108M only (expense_tags_conflict); D USD 108M + EUR 30M ($32.4M:
    unit_conflict on the parallel tag beside the expense_tags_conflict); E EUR 100M with no FX rate, even fetched
    (expense_tag_unconverted); F USD 108M + EUR 30M with no FX rate (unit_conflict, the EUR unit's usd null); G EUR
    -5M with no FX rate (a negative figure: no USD value, but not positive); H USD 108M + EUR 0 with no FX rate (a
    zero is 0 at every rate: unit_conflict, the EUR unit's usd 0)."""
    f = _facts(expense={2023: 15e6, 2025: 40e6}, cash={2023: 15e6, 2025: 40e6})
    for unit, v in {"A": [("EUR", 100e6)], "B": [("USD", 40e6), ("EUR", 100e6)], "C": [("USD", 108e6)],
                    "D": [("USD", 108e6), ("EUR", 30e6)], "E": [("EUR", 100e6)],
                    "F": [("USD", 108e6), ("EUR", 30e6)], "G": [("EUR", -5e6)],
                    "H": [("USD", 108e6), ("EUR", 0.0)]}[case]:
        _syn_put(f, EXPENSE_OLD, unit, _ctx("2025-01-01", "2025-12-31", v, filed="2026-02-20"))
    return f


def test_a_years_own_expense_is_its_largest_figure_on_every_expense_tag_in_every_unit():
    """[Codex review r29 of PR #47, second polish review] iprd_own_charge_usd read the parallel expense tag's figures
    only when that tag also carried a unit conflict: beside the current tag's USD 40M expensed and paid in FY2025, the
    parallel tag filed at $108M on its own (EUR 100M at 1.08, or USD 108M: expense_tags_conflict, no unit conflict)
    left the year's own expense at $40M, so a $40M declaration was "whole" and took FY2025 out of the recurrence count
    — while the same $108M filed beside a USD 40M fact on that tag (unit_conflict) read $108M. The final rule: a
    year's own expense in USD is the largest positive figure on ANY of its acquired-IPR&D expense tags (the detector
    tag and the parallel one, expense_tags_conflict figures too) in every unit filed for the period, each other unit
    converted at the run's rate — $108M in all four cases; its whole charge is the largest of that, every positive
    cash-tag figure in every unit and the deducted cash. $40M declared is a part (the year stays counted, for $108M
    less the $40M), $108M the whole, more than $108M is refused (the cap). A positive figure on an expense tag with no
    USD value (the parallel tag with no FX rate, alone or beside a USD fact on it) leaves the own expense unknown:
    every declaration is refused (NEEDS_MAIN_AGENT: currency, the message naming the tag and unit) and the recurrence
    figure is unknown, read as material, the RECURRENT flag saying the year's acquired-IPR&D expense has no USD
    figure. The deduction never changes."""
    for case in "ABCD":
        u = _ok(_run_fx(_r29_parallel(case), R29_EUR_RATE))
        b = u["iprd_adjustment"]
        p25 = next(p for p in b["periods"] if p["period"] == "2025-12-31")
        assert p25["expense"] == 40e6 and p25["amount"] == 40e6 and p25["excluded"] is None, (case, p25)
        assert b["total"] == 55e6 and b["fy_with_charge"] == ["2023-12-31", "2025-12-31"] and b["recurrent"], (case, b)
        assert E.iprd_whole_charge_unknown(p25) is None and E.iprd_own_charge_usd(p25) == (108e6, 108e6), (case, p25)
        assert E.iprd_recurrence_expense(p25) == 108e6 and b["recurrence_expense_total"] == 123e6, (case, b)
        assert abs(b["recurrence_materiality"] - _r28_mat(u, 123e6)) < 1e-12, (case, b)
        # $40M declared: a part of the $108M — the year stays counted, for $108M less the $40M
        n = _ok(_run_fx(_r29_parallel(case), R29_EUR_RATE, judgment={"iprd_deferred_payment": [deferred(amount=40e6)]}))
        pb = n["iprd_adjustment"]
        q25 = next(p for p in pb["periods"] if p["period"] == "2025-12-31")
        assert q25.get("recurrence_excluded") is None and q25["deferred_payment_of"][0]["amount"] == 40e6, (case, q25)
        assert pb["fy_with_charge"] == ["2023-12-31", "2025-12-31"] and pb["recurrent"] and pb["total"] == 55e6, (case, pb)
        assert pb["recurrence_expense_total"] == 15e6 + 68e6 and flags(n, "ACQUIRED_IPRD_RECURRENT"), (case, pb)
        # the whole $108M: the year leaves the count; more than the whole is refused (the cap)
        w = _ok(_run_fx(_r29_parallel(case), R29_EUR_RATE,
                        judgment={"iprd_deferred_payment": [deferred(amount=108e6)]}))["iprd_adjustment"]
        assert w["fy_with_charge"] == ["2023-12-31"] and not w["recurrent"] and w["total"] == 55e6, (case, w)
        _refused(_run_fx(_r29_parallel(case), R29_EUR_RATE, judgment={"iprd_deferred_payment": [deferred(amount=109e6)]}),
                 "FY 2025-12-31's declarations sum to 109,000,000, more than the period's charge 108,000,000")
    # a positive parallel-tag figure with no USD value: the own expense (and so the whole charge) is unknown
    for case, needle in (("E", "ResearchAndDevelopmentInProcess (100,000,000 EUR) has no USD figure"),
                         ("F", "acquired-IPR&D expense tag ResearchAndDevelopmentInProcess is also filed at 30,000,000 "
                               "EUR, which has no USD figure")):
        x = _ok(_run(_r29_parallel(case)))
        xb = x["iprd_adjustment"]
        x25 = next(p for p in xb["periods"] if p["period"] == "2025-12-31")
        assert E.iprd_own_charge_usd(x25) == (None, None) and E.iprd_recurrence_expense(x25) is None, (case, x25)
        why = E.iprd_whole_charge_unknown(x25)
        assert why and needle in why, (case, why)
        assert xb["fy_with_charge"] == ["2023-12-31", "2025-12-31"] and xb["recurrent"], (case, xb)
        assert xb["recurrence_materiality"] is None and xb["recurrence_expense_unknown_usd"] == ["FY2025"], (case, xb)
        rf = flags(x, "ACQUIRED_IPRD_RECURRENT")
        assert len(rf) == 1 and "FY2025: its acquired-IPR&D expense has no USD figure" in rf[0], (case, rf)
        r = _r29_reason(_r29_parallel(case), [deferred(amount=40e6)])
        assert len(r) == 1 and r[0].startswith("FY 2025-12-31 names no acquired-IPR&D charge") and why in r[0], (case, r)
        assert "stays in the recurrence count (NEEDS_MAIN_AGENT: currency)" in r[0], (case, r)
    # zero and negative figures never raise the own expense, nor leave it unknown (no FX rate in either case: a
    # negative figure is not a positive one, a zero is 0 at every rate)
    for case, own in (("G", 40e6), ("H", 108e6)):
        x = _ok(_run(_r29_parallel(case)))
        xb = x["iprd_adjustment"]
        x25 = next(p for p in xb["periods"] if p["period"] == "2025-12-31")
        assert x25["expense"] == 40e6 and x25["amount"] == 40e6 and x25["excluded"] is None, (case, x25)
        assert E.iprd_whole_charge_unknown(x25) is None and E.iprd_own_charge_usd(x25) == (own, own), (case, x25)
        assert E.iprd_recurrence_expense(x25) == own and xb["recurrence_expense_total"] == 15e6 + own, (case, xb)
        assert "recurrence_expense_unknown_usd" not in xb and xb["total"] == 55e6, (case, xb)
        assert "no USD figure" not in flags(x, "ACQUIRED_IPRD_RECURRENT")[0], case
        assert _r29_reason(_r29_parallel(case), [deferred(amount=40e6)]) == [], case


def test_the_recurrence_figure_reads_the_expense_side_and_the_whole_charge_adds_the_cash_side():
    """[Codex review r29 of PR #47, second polish review] The round-29 polish made a year's recurrence figure unknown
    whenever its whole charge was, so a known USD expense beside cash with no FX rate — USD 100M expensed, EUR 40M
    paid (no rate, even fetched: gated ACQUIRED_IPRD_UNCONVERTED, no unit conflict) — dropped out of the recurrence
    figure and the RECURRENT flag said FY2025 had "no USD figure", though its expense is $100M in USD. The final rule:
    the recurrence figure reads the expense side — the year's own expense, less only the part of a declaration that
    exceeds the whole charge less that expense — and is unknown only when the own expense is; the whole charge adds
    the cash side (every positive cash-tag figure in every unit, the deducted cash) for the whole-declaration test and
    its cap, unknown when any positive cash-tag figure has no USD value (every declaration then refused, naming the
    cash figure and its unit). USD 100M + EUR 40M cash with no rate reads $100M again (f29b9e9's figure) and its
    declarations stay refused; the cash tag also filed at EUR 100M with no rate beside the USD 40M expensed and paid
    reads the $40M expense; EUR 100M at 1.08 on the cash tag reads a $40M recurrence figure and a $108M whole charge.
    The deduction never changes."""
    ue = _facts(expense={2023: 15e6, 2025: 100e6}, cash={2023: 15e6})
    _syn_put(ue, CASH, "EUR", _ctx("2025-01-01", "2025-12-31", 40e6, filed="2026-02-20"))
    a = _ok(_run(ue))
    ab = a["iprd_adjustment"]
    a25 = next(p for p in ab["periods"] if p["period"] == "2025-12-31")
    assert a25["excluded"] == "non_usd_no_rate" and a25["expense"] == 100e6 and a25["cash_native"] == 40e6, a25
    assert "unit_conflict" not in a25 and "expense_tags_conflict" not in a25, a25
    assert E.iprd_own_charge_usd(a25) == (None, 100e6) and E.iprd_recurrence_expense(a25) == 100e6, a25
    why = E.iprd_whole_charge_unknown(a25)
    assert why == "its cash outflow (40,000,000 EUR) has no USD figure (no FX rate, even fetched)", why
    assert ab["fy_with_charge"] == ["2023-12-31", "2025-12-31"] and ab["recurrent"] and ab["total"] == 15e6, ab
    assert ab["recurrence_expense_total"] == 115e6 and "recurrence_expense_unknown_usd" not in ab, ab
    assert abs(ab["recurrence_materiality"] - _r28_mat(a, 115e6)) < 1e-12, ab
    rf = flags(a, "ACQUIRED_IPRD_RECURRENT")
    assert len(rf) == 1 and "periods $115,000,000 = " in rf[0] and "no USD figure" not in rf[0], rf
    assert flags(a, "ACQUIRED_IPRD_UNCONVERTED") and E.iprd_unresolved(a), "still gated"
    for amt in (100e6, 40e6):
        r = _r29_reason(ue, [deferred(amount=amt)])
        assert len(r) == 1 and r[0].startswith("FY 2025-12-31 names no acquired-IPR&D charge") and why in r[0], r
        assert "stays in the recurrence count (NEEDS_MAIN_AGENT: currency)" in r[0], r
    # the cash tag also filed at EUR 100M with no rate beside the USD 40M expensed and paid (unit_conflict): the
    # expense side is known, so the recurrence figure reads it; the whole charge is not, so no declaration applies
    c = _ok(_run(_r29_unit_conflict(CASH)))
    cb = c["iprd_adjustment"]
    c25 = next(p for p in cb["periods"] if p["period"] == "2025-12-31")
    assert E.iprd_own_charge_usd(c25) == (None, 40e6) and E.iprd_recurrence_expense(c25) == 40e6, c25
    cw = E.iprd_whole_charge_unknown(c25)
    assert cw and "its cash tag PaymentsToAcquireInProcessResearchAndDevelopment is also filed at 100,000,000 EUR" in cw, cw
    assert cb["recurrence_expense_total"] == 55e6 and "recurrence_expense_unknown_usd" not in cb and cb["recurrent"], cb
    r = _r29_reason(_r29_unit_conflict(CASH), [deferred(amount=40e6)])
    assert len(r) == 1 and cw in r[0] and "stays in the recurrence count" in r[0], r
    # with the rate: the expense side and the cash side apart
    for tag, fig in ((EXPENSE, 108e6), (CASH, 40e6)):
        p25 = next(p for p in _ok(_run_fx(_r29_unit_conflict(tag), R29_EUR_RATE))["iprd_adjustment"]["periods"]
                   if p["period"] == "2025-12-31")
        assert E.iprd_own_charge_usd(p25) == (108e6, fig) and E.iprd_recurrence_expense(p25) == fig, (tag, p25)


def test_a_refused_first_charge_names_a_reversal_with_no_fx_rate_in_its_own_currency():
    """[Codex review r29 of PR #47, review note] _iprd_no_own_expense_why printed a reversal filed only in a currency
    with no FX rate as if it were dollars ("negative (-5,000,000, a reversal)" for EUR -5M); it now names the unit and
    the missing rate, as _iprd_reversal_settles does. A USD reversal reads as before."""
    f = _facts(expense={2023: 100e6, 2025: 50e6}, cash={2023: 0.0, 2024: 100e6, 2025: 50e6})
    _syn_put(f, EXPENSE, "EUR", _ctx("2024-01-01", "2024-12-31", -5e6, filed="2025-02-20"))
    r = _r29_reason(f, [_r29_ghost()])
    assert len(r) == 1 and ("its acquired-IPR&D expense is negative (-5,000,000 EUR, no FX rate, a reversal) and its "
                            "cash settles an earlier charge (deferred_payment)") in r[0], r
    u = _r29_reason(_r29_settled(-10e6), [_r29_ghost()])
    assert len(u) == 1 and "is negative (-10,000,000, a reversal) and its cash settles" in u[0], u


def test_the_charge_flag_never_calls_a_cash_settlement_expensed_at_acquisition():
    """[Codex review r29 of PR #47, review note] ACQUIRED_IPRD_CHARGE opened "acquired in-process R&D expensed at
    acquisition in the base window — …" whatever the periods were, so the automatic cash settlement of an earlier
    charge (deferred_payment: cash with no acquired-IPR&D expense of its own) was listed as an acquisition expensed
    that year. A settlement period is named as cash settling an earlier charge, and the opening says so; a window
    with no settlement (HALO) reads exactly as before."""
    n = _ok(_run(_r29_settled()))
    cf = flags(n, "ACQUIRED_IPRD_CHARGE")
    assert len(cf) == 1, cf
    assert cf[0].startswith("ACQUIRED_IPRD_CHARGE: acquired in-process R&D in the base window, expensed at acquisition "
                            "or cash settling an earlier charge — "), cf
    assert ("FY2024 $100,000,000 (cash_outflow, PaymentsToAcquireInProcessResearchAndDevelopment; cash settling an "
            "earlier charge, not an acquisition expensed that year)") in cf[0], cf
    assert "FY2025 $50,000,000 (cash_outflow, PaymentsToAcquireInProcessResearchAndDevelopment);" in cf[0], cf
    assert "expensed at acquisition in the base window" not in cf[0], cf
    # a window whose only deduction is a settlement
    s = _ok(_run(_facts(expense={2023: 100e6}, cash={2023: 0.0, 2024: 100e6})))
    sf = flags(s, "ACQUIRED_IPRD_CHARGE")
    assert len(sf) == 1 and sf[0].startswith("ACQUIRED_IPRD_CHARGE: cash settling an earlier acquired in-process R&D "
                                             "charge in the base window — FY2024 $100,000,000 ("), sf
    assert "expensed at acquisition" not in sf[0] and "cash settling an earlier charge, not an acquisition" in sf[0], sf
    # a pre-window deal's declared installment (cash only, deferred_payment): a settlement too
    f = _facts(expense={2022: 40e6, 2023: 1e6, 2024: 1e6}, cash={2022: 10e6, 2023: 1e6, 2024: 1e6, 2025: 30e6})
    decl = deferred(period="2025-12-31", amount=30e6, first="2022-12-31", source=PRE_SRC, deal="Old Bio", contingent=PRE_CT)
    mf = flags(_ok(_run(f, judgment={"iprd_deferred_payment": [decl]})), "ACQUIRED_IPRD_CHARGE")
    assert len(mf) == 1 and ("FY2025 $30,000,000 (cash_outflow, PaymentsToAcquireInProcessResearchAndDevelopment; cash "
                             "settling an earlier charge, not an acquisition expensed that year; deferred payment of Old "
                             "Bio (first charged 2022-12-31) — not counted toward recurrence)") in mf[0], mf
    # no settlement: exactly the wording before
    p = _ok(_run(_facts(expense={2025: 20e6})))
    pf = flags(p, "ACQUIRED_IPRD_CHARGE")
    assert len(pf) == 1 and pf[0].startswith(
        "ACQUIRED_IPRD_CHARGE: acquired in-process R&D expensed at acquisition in the base window — FY2025 $20,000,000 "
        "(expense, ResearchAndDevelopmentAssetAcquiredOtherThanThroughBusinessCombinationWrittenOff); total "
        "$20,000,000 = 10.2% of the base OE total. Owner's earnings (OCF − capex − SBC) never saw this spend: the "
        "expense is added back in operating cash flow and the payment is not capex. Treatment: "), pf


# --- Codex review round 30 of PR #47 ------------------------------------------------------------------------------
def _r30_two_units(tag, usd_of_eur):
    """FY2023: Test Bio's $15M acquired-IPR&D expense, paid. FY2025: USD 100M expensed and paid, and `tag` (the
    expense tag or the cash tag) also filed for FY2025 in EUR at the figure that converts, at R29_EUR_RATE's 1.08, to
    `usd_of_eur`."""
    f = _facts(expense={2023: 15e6, 2025: 100e6}, cash={2023: 15e6, 2025: 100e6})
    _syn_put(f, tag, "EUR", _ctx("2025-01-01", "2025-12-31", usd_of_eur / 1.08, filed="2026-02-20"))
    return f


def test_a_unit_within_the_unit_agreement_tolerance_is_the_figure_used():
    """[Codex review r30 of PR #47, #4336863087 — behaviour unchanged, the main agent's decision on Andrew's
    delegation] The round-29 rule reads a year's own expense and whole charge as the largest figure "in every unit
    filed". Units that agree within the engine's unit-agreement tolerance (IPRD_UNIT_TOLERANCE: they disagree only
    when, after conversion, they differ by more than max($1, 1% of the larger)) record no unit_conflict: they are one
    charge translated at two rates (the run's period-end rate is not the filer's), so the figure used is the charge.
    USD 100M beside EUR converting to $100.7M (0.7% apart): the whole charge and own expense are $100M, a $100M
    declaration is whole (the year leaves the recurrence count) and $100.7M is more than the charge. Taking the larger
    translation would make that correct declaration a part on FX noise and keep the year counted. Beyond the tolerance
    (EUR converting to $102M, 2% apart) the units disagree: unit_conflict is recorded and the largest converted figure
    is the whole charge ($100M declared is a part, $102M the whole). The same on the expense tag and the cash tag."""
    assert E.IPRD_UNIT_TOLERANCE == 0.01
    for tag in (EXPENSE, CASH):
        # within the tolerance: one charge
        n = _ok(_run_fx(_r30_two_units(tag, 100.7e6), R29_EUR_RATE))
        b = n["iprd_adjustment"]
        p25 = next(p for p in b["periods"] if p["period"] == "2025-12-31")
        assert not p25.get("unit_conflict"), (tag, p25)
        assert E.iprd_own_charge_usd(p25) == (100e6, 100e6) and E.iprd_whole_charge_unknown(p25) is None, (tag, p25)
        assert b["total"] == 115e6 and b["fy_with_charge"] == ["2023-12-31", "2025-12-31"] and b["recurrent"], (tag, b)
        w = _ok(_run_fx(_r30_two_units(tag, 100.7e6), R29_EUR_RATE,
                        judgment={"iprd_deferred_payment": [deferred(amount=100e6)]}))
        wb = w["iprd_adjustment"]
        assert wb["fy_with_charge"] == ["2023-12-31"] and not wb["recurrent"] and wb["total"] == 115e6, (tag, wb)
        assert wb["recurrence_excluded"][0]["amount"] == 100e6 and not flags(w, "ACQUIRED_IPRD_RECURRENT"), (tag, wb)
        _refused(_run_fx(_r30_two_units(tag, 100.7e6), R29_EUR_RATE,
                         judgment={"iprd_deferred_payment": [deferred(amount=100.7e6)]}),
                 "FY 2025-12-31's declarations sum to 100,700,000, more than the period's charge 100,000,000")
        # beyond the tolerance: two figures, the largest converted one is the whole charge
        u = _ok(_run_fx(_r30_two_units(tag, 102e6), R29_EUR_RATE))
        q25 = next(p for p in u["iprd_adjustment"]["periods"] if p["period"] == "2025-12-31")
        uc = q25["unit_conflict"][tag]
        assert uc["used"] == "USD" and abs(uc["units"]["EUR"]["usd"] - 102e6) < 1e-3, (tag, q25)
        charge, own = E.iprd_own_charge_usd(q25)
        assert abs(charge - 102e6) < 1e-3 and abs(own - (102e6 if tag == EXPENSE else 100e6)) < 1e-3, (tag, charge, own)
        part = _ok(_run_fx(_r30_two_units(tag, 102e6), R29_EUR_RATE,
                           judgment={"iprd_deferred_payment": [deferred(amount=100e6)]}))["iprd_adjustment"]
        assert part["fy_with_charge"] == ["2023-12-31", "2025-12-31"] and part["recurrent"], (tag, part)
        whole = _ok(_run_fx(_r30_two_units(tag, 102e6), R29_EUR_RATE,
                            judgment={"iprd_deferred_payment": [deferred(amount=102e6)]}))["iprd_adjustment"]
        assert whole["fy_with_charge"] == ["2023-12-31"] and not whole["recurrent"], (tag, whole)
        assert part["total"] == whole["total"] == b["total"] == 115e6, tag


def test_three_units_within_the_tolerance_of_the_figure_used_but_spread_beyond_it_all_count():
    """[Codex review r30 of PR #47, review of the round's doc fix — behaviour unchanged] The unit-agreement tolerance
    is tested on the SPREAD across every unit a tag is filed in (_iprd_pick: the largest and smallest converted figures
    more than max($1, 1% of the larger) apart), not on each unit against the figure used. USD 100M beside EUR converting
    to $99.2M (-0.8%) and GBP converting to $100.9M (+0.9%): each is within 1% of the USD figure, but the spread is
    $1.7M, so every unit is recorded (unit_conflict) and the largest, $100.9M, is the whole charge — a $100M
    declaration is a part (the year stays counted) and $100.9M is the whole. The same on the expense and cash tags."""
    rates = {"EUR": {"2025-12-31": 1.08, "2025-12-30": 1.08}, "GBP": {"2025-12-31": 1.25, "2025-12-30": 1.25}}

    def three(tag):
        f = _facts(expense={2023: 15e6, 2025: 100e6}, cash={2023: 15e6, 2025: 100e6})
        _syn_put(f, tag, "EUR", _ctx("2025-01-01", "2025-12-31", 99.2e6 / 1.08, filed="2026-02-20"))
        _syn_put(f, tag, "GBP", _ctx("2025-01-01", "2025-12-31", 100.9e6 / 1.25, filed="2026-02-20"))
        return f

    for tag in (EXPENSE, CASH):
        n = _ok(_run_fx(three(tag), rates))
        p25 = next(p for p in n["iprd_adjustment"]["periods"] if p["period"] == "2025-12-31")
        uc = (p25.get("unit_conflict") or {}).get(tag) or {}
        assert set(uc.get("units") or {}) == {"USD", "EUR", "GBP"} and uc.get("used") == "USD", (tag, p25)
        charge, own = E.iprd_own_charge_usd(p25)
        assert abs(charge - 100.9e6) < 1e-3, (tag, charge)
        assert abs(own - (100.9e6 if tag == EXPENSE else 100e6)) < 1e-3, (tag, own)
        part = _ok(_run_fx(three(tag), rates, judgment={"iprd_deferred_payment": [deferred(amount=100e6)]}))
        assert part["iprd_adjustment"]["fy_with_charge"] == ["2023-12-31", "2025-12-31"], (tag, part["iprd_adjustment"])
        assert part["iprd_adjustment"]["recurrent"] and flags(part, "ACQUIRED_IPRD_RECURRENT"), tag
        whole = _ok(_run_fx(three(tag), rates, judgment={"iprd_deferred_payment": [deferred(amount=100.9e6)]}))
        assert whole["iprd_adjustment"]["fy_with_charge"] == ["2023-12-31"], (tag, whole["iprd_adjustment"])


def _r30_ttm(shares="drop"):
    """ttm.json for the synthetic TTM base ($2.10/share): ttm_shares_diluted 50M, else `shares` in its place ("drop":
    the key is absent)."""
    t = _ttm_doc(2.1, 50e6)
    if shares == "drop":
        del t["ttm_shares_diluted"]
    else:
        t["ttm_shares_diluted"] = shares
    return t


R30_BAD_TTM_SHARES = (("missing", "drop"), ("null", None), ("zero", 0), ("negative", -50e6),
                      ("a string", "50000000"), ("a bool", True), ("infinite", float("inf")))


def _r30_refused(out, label):
    assert out["exit"] == 3, (label, out["exit"], out["stdout"][-1500:])
    s = out["stdout"]
    assert "BAD_TTM_SHARES for SYN" in s and "ttm_shares_diluted" in s and "never the latest-FY count" in s, (label, s[-1500:])


def _r30_paid_in_shares(facts):
    return {"iprd_cash_flow_check": [dict(c, presentation="paid_in_shares") for c in auto_checks(facts)]}


def test_a_ttm_base_never_puts_its_iprd_figures_on_the_latest_fy_count():
    """[Codex review r30 of PR #47, #4336863102] On a TTM base the acquired-IPR&D figures are per share on ttm.json's
    current-YTD diluted count (ttm_shares_diluted). When that count was missing or invalid (absent, null, 0, negative,
    a string, a bool, non-finite) the engine silently fell back to the latest-FY count (shares_source diluted_latest),
    exited 0 and make_score published it: $50M on 100M FY shares ($0.50) where the TTM basis is 50M ($1.00). The
    unverified-share-count treatment would not cover it (make_score refuses that one only for a deducted charge, and
    its way through is a hand-deduction tier_override), so the run is refused like any other defective ttm.json
    input (exit 3, BAD_TTM_SHARES: rerun ttm.py) whenever it carries an acquired-IPR&D figure per share — a charge,
    an unconfirmed charge, or two or more charge years (the recurrence figure) — on a --ttm pin and on a --base-oe-ps
    pin equal to ttm.json's figure alike. A TTM run with no such figure is not refused (and records no denominator,
    never the FY count); an FY-median base keeps the latest-FY count whatever ttm.json holds; make_score's
    override-impact replay is never refused (it holds the final run's charge)."""
    import reprice as R
    facts = _ttm_ytd_facts()   # FY2025 $20M + 2026 H1 $30M
    good = _ok(_run(facts, extra=["--ttm"], ttm=_r30_ttm(50e6)))
    gb = good["iprd_adjustment"]
    assert gb["total"] == 50e6 and gb["shares_denominator"] == 50e6, gb
    assert gb["shares_source"] == "ttm.json ttm_shares_diluted" and gb["charge_per_share"] == 1.0, gb
    # reprice / build_site choose no denominator: the live charge is the recorded one, on ttm.json's count
    assert E.iprd_charge_per_share(good) == 1.0 and R.reprice(good, good["price"])["iprd_charge_per_share"] == 1.0
    for label, sh in R30_BAD_TTM_SHARES:
        for extra in (["--ttm"], ["--base-oe-ps", "2.1"]):
            _r30_refused(_run(facts, extra=extra, ttm=_r30_ttm(sh)), (label, extra))
    # the recurrence figure alone: two FY charge years paid in shares, nothing deducted
    f2 = _facts(expense={2024: 15e6, 2025: 20e6})
    j2 = _r30_paid_in_shares(f2)
    r2 = _ok(_run(f2, extra=["--ttm"], ttm=_r30_ttm(50e6), judgment=j2))["iprd_adjustment"]
    assert r2["total"] == 0 and r2["fy_with_charge"] == ["2024-12-31", "2025-12-31"] and r2["recurrent"], r2
    assert r2["recurrence_expense_total"] == 35e6 and r2["shares_denominator"] == 50e6, r2
    _r30_refused(_run(f2, extra=["--ttm"], ttm=_r30_ttm(), judgment=j2), "recurrence only")
    # the unconfirmed figure alone: a charge awaiting its cash-flow check
    f3 = _facts(expense={2025: 20e6})
    r3 = _ok(_run(f3, extra=["--ttm"], ttm=_r30_ttm(50e6), checks=False))["iprd_adjustment"]
    assert r3["total"] == 0 and r3["unconfirmed_total"] == 20e6 and r3["shares_denominator"] == 50e6, r3
    _r30_refused(_run(f3, extra=["--ttm"], ttm=_r30_ttm(0), checks=False), "unconfirmed only")
    # no acquired-IPR&D figure per share: not refused, valued exactly as with the count, no FY denominator recorded
    plain_ok = _ok(_run(_facts(), extra=["--ttm"], ttm=_r30_ttm(50e6)))
    plain = _ok(_run(_facts(), extra=["--ttm"], ttm=_r30_ttm()))
    assert plain["iprd_adjustment"] is None and plain["weighted"] == plain_ok["weighted"], plain["iprd_adjustment"]
    f4 = _facts(expense={2025: 20e6})
    one = _ok(_run(f4, extra=["--ttm"], ttm=_r30_ttm(), judgment=_r30_paid_in_shares(f4)))
    ob = one["iprd_adjustment"]
    assert ob["total"] == 0 and ob["fy_with_charge"] == ["2025-12-31"] and not ob["unconfirmed_total"], ob
    assert ob["shares_denominator"] is None and ob["shares_source"] is None, ob
    assert one["weighted"] == plain["weighted"] and E.iprd_charge_per_share(one) == 0.0
    # an FY-median base: the latest-FY count, whatever ttm.json holds
    m = _ok(_run(facts, ttm=_r30_ttm()))["iprd_adjustment"]
    assert m["total"] == 20e6 and m["shares_denominator"] == SHARES and m["shares_source"] == "diluted_latest", m
    assert m["charge_per_share"] == 20e6 / SHARES and m["window"]["ttm_current_ytd"] is None, m
    # make_score's override-impact replay is never refused: no denominator, the final run's charge held
    hold = json.dumps({"treatment": "one_time_value_deduction", "charge_per_share": 1.0})
    cf = _run_env(facts, ["--ttm"], ttm=_r30_ttm(), env={"DCF_NO_OVERRIDES": "1", "DCF_IPRD_HOLD": hold}, measure=True)
    assert cf["exit"] == 0 and "BAD_TTM_SHARES" not in cf["stdout"], cf["stdout"][-1500:]
    cb = cf["numbers"]["iprd_adjustment"]
    assert cb["shares_denominator"] is None and cb["treatment"] == "one_time_value_deduction", cb
    assert E.iprd_charge_per_share(cf["numbers"]) == 1.0, cb


def test_an_amortized_ttm_native_base_reads_only_a_valid_ttm_share_count():
    """[Codex review r30 of PR #47] An iprd_amortized declaration on native base ttm_json takes its share count from
    ttm.json's ttm_shares_diluted, read unvalidated: a string "50000000" passed the truthiness test and was
    float()-coerced into the declaration's check. Its count is now the same validated figure as the TTM base's
    denominator (dcf_engine.iprd_ttm_share_count), and a run without one is refused BAD_TTM_SHARES like any TTM base
    carrying acquired-IPR&D figures per share."""
    f = _facts(expense={2023: 15e6, 2025: 20e6})
    d = {"basis": "iprd_amortized", "kind": "filing", "native_base": "ttm_json", "figures": [15e6, 0.0, 20e6],
         "shares": 50e6, "value": 2.1 - 35e6 / 3 / 50e6, "source": "test: this run's figures",
         "reason": "test: acquisition-led R&D recurs"}
    ok = _ok(_run(f, extra=["--base-oe-ps", repr(d["value"])], ttm=_r30_ttm(50e6), judgment={"base_override": d}))
    assert ok["iprd_adjustment"]["treatment"] == "amortized_in_base", ok["iprd_adjustment"]["treatment"]
    assert ok["iprd_adjustment"]["amortized"]["shares"] == 50e6, ok["iprd_adjustment"]["amortized"]
    for label, sh in R30_BAD_TTM_SHARES:
        _r30_refused(_run(f, extra=["--base-oe-ps", repr(d["value"])], ttm=_r30_ttm(sh), judgment={"base_override": d}),
                     ("amortized", label))
        assert E.iprd_ttm_share_count(_r30_ttm(sh)) is None, label
    assert E.iprd_ttm_share_count(_r30_ttm(50e6)) == 50e6 and E.iprd_ttm_share_count(_r30_ttm(50_000_000)) == 50e6
    assert E.iprd_ttm_share_count(None) is None and E.iprd_ttm_share_count({}) is None


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
