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
    """Release: ENGINE_RELEASE 5.6.0 (engine_version stays 5)."""
    assert E.ENGINE_RELEASE == "5.6.0", E.ENGINE_RELEASE


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
    deducts nothing whatever the cash tag says; a negative expense is excluded; the overlap guard excludes an
    expense-basis amount the capex intangible leg already covers (>= 98%), not a cash-basis one."""
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
    assert rec["excluded"] == "already_in_capex" and rec["deducted"] == 0.0, rec
    rec = E.iprd_period_record("2025-12-31", "fy", (EXPENSE, 20e6, "USD", None, "x"), None, capex_intang=19.5e6, check=ADDED_BACK)
    assert rec["excluded"] is None and rec["deducted"] == 20e6, rec
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
    is excluded awaiting_cash_flow_check, ACQUIRED_IPRD_UNCONFIRMED names the three periods and no CHARGE /
    RECURRENT flag fires; with the check declaring "inside_operating_cash_flow" the run is untouched and raises no
    IPR&D flag at all. Before the fix the engine deducted $1.74/share and raised CHARGE and RECURRENT."""
    plain = _plain()
    exp = {2023: 143.9e6, 2024: 12.5e6, 2025: 17.4e6}
    n = _ok(_run(_facts(expense=exp), checks=False))
    blk = n["iprd_adjustment"]
    assert blk["total"] == 0.0 and blk["treatment"] == "awaiting_cash_flow_check" and blk["unconfirmed_total"] == sum(exp.values()), blk
    assert [p["excluded"] for p in blk["periods"]] == ["awaiting_cash_flow_check"] * 3, blk["periods"]
    assert n["weighted"] == plain["weighted"] and n["scenarios"] == plain["scenarios"] and E.iprd_charge_per_share(n) == 0.0
    fl = flags(n, "ACQUIRED_IPRD_UNCONFIRMED")
    assert len(fl) == 1 and "FY2023 $143,900,000" in fl[0] and "FY2025 $17,400,000" in fl[0] and "NBIX" in fl[0], fl
    assert not flags(n, "ACQUIRED_IPRD_CHARGE") and not flags(n, "ACQUIRED_IPRD_RECURRENT")
    chk = [dict(c, presentation="inside_operating_cash_flow") for c in auto_checks(_facts(expense=exp))]
    m = _ok(_run(_facts(expense=exp), judgment={"iprd_cash_flow_check": chk}))
    mb = m["iprd_adjustment"]
    assert [p["excluded"] for p in mb["periods"]] == ["paid_in_operating_cash_flow"] * 3 and mb["treatment"] == "none", mb
    assert m["weighted"] == plain["weighted"] and not flags(m, "ACQUIRED_IPRD")
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
    """Overlap guard (main-agent addition): an expense-basis charge (no cash tag) that the period's 5.5 capex already
    charged to OE through intangible purchases (>= 98% of the expense) is not deducted — recorded
    `excluded: already_in_capex`, the valuation equals the same filer's run without the IPR&D fact; below 98% it is
    deducted."""
    intang = {2025: 20e6}
    plain = _plain(intangibles=intang)
    n = _ok(_run(_facts(expense={2025: 20e6}, intangibles=intang)))
    blk = n["iprd_adjustment"]
    p = [x for x in blk["periods"] if x["period"] == "2025-12-31"][0]
    assert p["excluded"] == "already_in_capex" and p["deducted"] == 0.0 and blk["total"] == 0.0, p
    assert blk["treatment"] == "none" and blk["charge_per_share"] == 0.0
    assert n["weighted"] == plain["weighted"] and n["scenarios"] == plain["scenarios"] and not flags(n, "ACQUIRED_IPRD")
    n2 = _ok(_run(_facts(expense={2025: 25e6}, intangibles=intang)))
    assert n2["iprd_adjustment"]["total"] == 25e6, n2["iprd_adjustment"]["periods"]
    _assert_shifted(n2, plain, 25e6 / SHARES)


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
    return {"fy_end": "2025-12-31", "ytd_end": "2026-06-30", "ttm_oe_per_share": per_share, "ttm_shares_diluted": shares,
            "ttm_oe_total": per_share * shares,
            "inputs": {"ocf": {"fy_period": ["2025-01-01", "2025-12-31"], "ytd_prior_period": ["2025-01-01", "2025-06-30"],
                               "ytd_current_period": ["2026-01-01", "2026-06-30"]}}, "warnings": [], "overrides_used": []}


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
             "iv_at_25", "fragility_flags", "content_hash"}
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
    assert n["engine_release"] == "5.6.0"


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
    dated = {"as_of", "price_source", "content_hash", "diagnostics"}
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


def test_entry_whose_period_rolled_out_of_the_window_is_unused_not_refused():
    """[Codex review, finding 5] An entry carried over from an earlier scoring whose period (FY2022) is now older
    than the engine's window is neither applied nor refused: the run exits 0 and lists it in
    deferred_payments_unused (like cash_flow_checks_unused); make_score then asks for it to be dropped. The
    in-window entry beside it still applies."""
    old = deferred(period="2022-12-31", amount=5e6, first="2021-12-31", source=OK_SRC_2021, deal="Old Bio")
    n = _ok(_two_of_three([deferred(), old]))
    blk = n["iprd_adjustment"]
    assert blk["deferred_payments_unused"] == [old], blk
    assert "deferred_payments_refused" not in blk and [x["period"] for x in blk["recurrence_excluded"]] == ["2025-12-31"]
    ref, unused = E.iprd_apply_deferred({"periods": [_rec("2025-12-31", 20e6)]}, [old],
                                        ["2023-12-31", "2024-12-31", "2025-12-31"], None)
    assert ref == [] and unused == [old]


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
