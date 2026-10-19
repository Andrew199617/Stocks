#!/usr/bin/env python3
"""Dividends-block tests for fundamentals.py (5.4.1, 5.4.2 / 5.4.3 / 5.4.4 / 5.4.5 review fixes).
Run: python _system/tests/test_fundamentals_dividends.py
(or python -m pytest _system/tests). No network, no company folders: every
test feeds inline fixtures to the module-level pure functions — growth
streak, last cut, frequency inference, payout ratios, TTM sums, CAGR, the
annual-series fallback, split restatement, the unfiled-split guard, the
combined issuance tags, the instant share count — and end-to-end
build_dividends calls on hand-made annual / quarterly tables shaped like the
real names the reviewers used (HBAN, KR, TKO, CCL, ESLT, KVUE, ZS; 5.4.4:
TSCO, NVDA, CTAS, AVGO, LRCX, WMT, CCL again; 5.4.6: ZTS, ATO, IRM, GEHC, HPQ,
FTI, WRB, WCN, FIG, DHI, ROP, LRCX, and the reviewers' S1 / S2 / edge3 fixtures).
2026-10-16 (price-free fundamentals.json): price_dividends — the price leaves
of the block from its own price-free fields — and, over EVERY build_dividends
call the other tests make, build_dividends(price P) == price_dividends(
build_dividends(price Q), P): the block build_site.py reprices at a newer
close is the block this script would write at it.
"""
import copy, json, os, sys, math

HERE = os.path.dirname(os.path.abspath(__file__))
SYS = os.path.dirname(HERE)
sys.path.insert(0, SYS)
import fundamentals as F  # noqa: E402


def close(a, b, rel=1e-9, abs_=1e-12):
    if a is None or b is None:
        return a is None and b is None
    return math.isclose(a, b, rel_tol=rel, abs_tol=abs_)


def _annual(*pairs):
    """[{fy, period_end, dps}] for (fy, dps) pairs — calendar fiscal years ending Dec 31."""
    return [{"fy": str(fy), "period_end": f"{fy}-12-31", "dps": dps} for fy, dps in pairs]


def _q(end, val, fq, fy_start, filed=None):
    return {"val": val, "fq": fq, "fy_start": fy_start, "filed": filed or F._add_days(end, 40)}


# ---------------- growth_years ----------------
def test_growth_years_counts_consecutive_increases_ending_at_latest():
    assert F.growth_years(_annual((2020, 0.5), (2021, 0.6), (2022, 0.7), (2023, 0.8))) == 3
    assert F.growth_years(_annual((2020, 0.5), (2021, 0.6), (2022, 0.6), (2023, 0.8))) == 1, "flat year breaks the streak"
    assert F.growth_years(_annual((2020, 0.5), (2021, 0.6), (2022, 0.7), (2023, 0.7))) == 0, "latest FY flat -> 0"
    assert F.growth_years(_annual((2020, 0.5), (2021, 0.4), (2022, 0.7), (2023, 0.8))) == 2, "a cut earlier does not matter"


def test_growth_years_breaks_on_fy_gap_and_missing_values():
    assert F.growth_years(_annual((2019, 0.3), (2020, 0.5), (2023, 0.8))) == 0, "2020 -> 2023 is not consecutive"
    assert F.growth_years(_annual((2020, 0.5), (2021, None), (2022, 0.7), (2023, 0.8))) == 1, "a None row is skipped, leaving a gap"
    assert F.growth_years([]) == 0 and F.growth_years(_annual((2023, 1.0))) == 0


def test_growth_years_uses_period_end_spacing_not_labels():
    # KR-style 52/53-week years and a KVUE-style fiscal-year-end change: consecutive by spacing
    rows = [{"fy": "2022", "period_end": "2022-01-02", "dps": 0.8}, {"fy": "2023a", "period_end": "2023-01-01", "dps": 0.9},
            {"fy": "2023", "period_end": "2023-12-31", "dps": 1.0}, {"fy": "2024", "period_end": "2024-12-29", "dps": 1.1}]
    assert F.growth_years(rows) == 3 and F.last_cut_fy(rows) is None
    kr = [{"fy": "2024", "period_end": "2024-02-03", "dps": 1.13}, {"fy": "2025", "period_end": "2025-02-01", "dps": 1.25}, {"fy": "2026", "period_end": "2026-01-31", "dps": 1.37}]
    assert F.growth_years(kr) == 2


# ---------------- last_cut_fy ----------------
def test_last_cut_fy_most_recent_decline():
    assert F.last_cut_fy(_annual((2019, 0.5), (2020, 0.1), (2021, 0.2), (2022, 0.3))) == "2020"
    assert F.last_cut_fy(_annual((2019, 0.5), (2020, 0.1), (2021, 0.2), (2022, 0.15))) == "2022"
    assert F.last_cut_fy(_annual((2019, 0.5), (2020, 0.5), (2021, 0.6))) is None, "flat is not a cut"
    assert F.last_cut_fy(_annual((2019, 0.5), (2023, 0.1))) is None, "non-consecutive years never count as a cut"
    assert F.last_cut_fy([]) is None


# ---------------- infer_frequency / frequency_from_spacing ----------------
def test_infer_frequency_counts_and_fy_remainder():
    # n_q_in_fy, fy_dps, sum_q_in_fy, any_quarterly, any_facts
    assert F.infer_frequency(4, 0.62, 0.62, True, True) == "quarterly"
    assert F.infer_frequency(3, 0.62, 0.465, True, True) == "quarterly", "Q4 filed only inside the FY total counts as a fourth payment"
    assert F.infer_frequency(3, 0.465, 0.465, True, True) == "irregular", "three payments and nothing left in the FY total"
    assert F.infer_frequency(2, 1.0, 1.0, True, True) == "semiannual"
    assert F.infer_frequency(1, 1.0, 1.0, True, True) == "annual"
    assert F.infer_frequency(1, None, 1.0, True, True) == "annual", "no FY fact -> plain count"
    assert F.infer_frequency(0, 0.39, None, False, True) is None, "only FY facts filed (20-F): not inferable"
    assert F.infer_frequency(0, None, None, False, False) == "none"
    assert F.infer_frequency(0, None, None, False, False, dividends_paid=True) is None, "cash dividends paid but no per-share tag: null, not 'none'"
    assert F.infer_frequency(0, None, None, True, True) == "irregular", "quarterly facts exist but none in the latest FY (suspended)"


def test_frequency_from_spacing():
    assert F.frequency_from_spacing(["2025-09-30", "2025-12-31", "2026-03-31", "2026-06-30"]) == "quarterly"
    assert F.frequency_from_spacing(["2025-06-30", "2025-09-30", "2026-03-31"]) == "quarterly", "a Q4 missing from the facts: median gap still a quarter"
    assert F.frequency_from_spacing(["2024-06-30", "2024-12-31", "2025-06-30", "2025-12-31"]) == "semiannual"
    assert F.frequency_from_spacing(["2023-06-30", "2024-06-30", "2025-06-30"]) == "annual"
    assert F.frequency_from_spacing(["2026-02-28", "2026-05-31", "2026-08-31"]) == "quarterly", "CCL reinstatement: three facts"
    assert F.frequency_from_spacing(["2026-02-28"]) is None


# ---------------- payout ratios ----------------
def test_payout_ratio_null_on_nonpositive_denominator():
    assert close(F.payout_ratio(1.37, 1.54), 1.37 / 1.54)
    assert F.payout_ratio(1.0, 0) is None
    assert F.payout_ratio(1.0, -0.39) is None, "negative EPS / OE -> null, never a negative payout"
    assert F.payout_ratio(None, 2.0) is None and F.payout_ratio(1.0, None) is None
    assert F.payout_ratio(True, 2.0) is None, "bools are not numbers"


# ---------------- TTM sums ----------------
def test_ttm_sum_needs_exactly_four_numbers():
    assert F.ttm_sum([1, 2, 3, 4]) == 10
    assert F.ttm_sum([1, 2, None, 4]) is None
    assert F.ttm_sum([1, 2, 3]) is None and F.ttm_sum([1, 2, 3, 4, 5]) is None
    assert F.ttm_sum([0, 0, 0, 0]) == 0, "four filed zeros are a real zero"


def test_consecutive_quarters():
    assert F.consecutive_quarters(["2025-03-31", "2025-06-30", "2025-09-30", "2025-12-31"])
    assert F.consecutive_quarters(["2025-05-24", "2025-08-16", "2025-11-08", "2026-01-31"]), "16/12/12/12-week year"
    assert not F.consecutive_quarters(["2025-03-31", "2025-06-30", "2025-09-30", "2026-03-31"]), "Q4 missing"
    assert F.consecutive_quarters(["2025-03-31"]) and not F.consecutive_quarters([])


def test_dps_ttm_from_quarters():
    v, ok = F.dps_ttm_from_quarters([("2026-08-15", 0.39), ("2026-05-23", 0.35), ("2026-01-31", 0.35), ("2025-11-08", 0.35), ("2025-08-16", 0.35)])
    assert ok and close(v, 1.44), "last four facts, newest four only"
    v, ok = F.dps_ttm_from_quarters([("2026-03-31", 0.155), ("2025-09-30", 0.155), ("2025-06-30", 0.155), ("2025-03-31", 0.155)])
    assert not ok and v is None, "Q4 missing -> caller rolls the FY fact forward"
    v, ok = F.dps_ttm_from_quarters([("2026-03-31", 0.155), ("2025-12-31", 0.155), ("2025-09-30", 0.155)])
    assert not ok and v is None, "fewer than four"
    v, ok = F.dps_ttm_from_quarters([("2026-03-31", 0.155), ("2025-12-31", None), ("2025-09-30", 0.155), ("2025-06-30", 0.155)])
    assert not ok, "a None fact is not a fact"


# ---------------- CAGR ----------------
def test_dps_cagr_by_period_end():
    a = _annual((2020, 0.7), (2021, 0.81), (2022, 0.99), (2023, 1.13), (2024, 1.25), (2025, 1.37))
    assert close(F.dps_cagr(a, 3), (1.37 / 0.99) ** (1 / 3) - 1)
    assert close(F.dps_cagr(a, 5), (1.37 / 0.7) ** (1 / 5) - 1)
    assert F.dps_cagr(a, 6) is None, "endpoint missing"
    assert F.dps_cagr(_annual((2020, 0.0), (2023, 1.0)), 3) is None, "zero base"
    assert F.dps_cagr([], 3) is None
    # 5.4.3: the window must be an unbroken run of dividend-paying fiscal years
    v, why = F.dps_cagr_window(_annual((2020, 0.5), (2022, 0.6), (2023, 1.0)), 3)
    assert v is None and "no annual DPS between FY2020" in why and "FY2022" in why, "a year with no DPS row inside the window -> null, gap named"
    v, why = F.dps_cagr_window(_annual((2020, 0.5), (2021, 0.0), (2022, 0.6), (2023, 1.0)), 3)
    assert v is None and "FY2021" in why and "no dividend" in why, "a filed zero inside the window is a suspension"
    assert F.dps_cagr_window(a, 3)[1] is None and F.dps_cagr_window(a, 6)[1].startswith("no annual DPS row 6 years before FY2025")
    # EXPE: FY2020 0.34, nothing filed for FY2021-FY2024, FY2025 1.60 — a reinstatement, not 36%/yr
    expe = _annual((2016, 1.0), (2017, 1.16), (2018, 1.24), (2019, 1.32), (2020, 0.34), (2025, 1.6))
    v, why = F.dps_cagr_window(expe, 5)
    assert v is None and "FY2020→FY2025" in why and "between FY2020 (period ended 2020-12-31) and FY2025" in why
    assert F.dps_cagr(expe, 3) is None
    # CCL: a zero year (FY2009) inside a window that would otherwise compute
    ccl = _annual((2007, 1.375), (2008, 1.6), (2009, 0), (2010, 0.4), (2011, 1.0), (2012, 1.5))
    assert F.dps_cagr(ccl, 5) is None and "FY2009" in F.dps_cagr_window(ccl, 5)[1]
    assert close(F.dps_cagr(ccl, 2), (1.5 / 0.4) ** 0.5 - 1), "FY2010->FY2012 is unbroken"
    kr = [{"fy": str(y), "period_end": e, "dps": d} for y, e, d in ((2021, "2021-01-30", 0.7), (2022, "2022-01-29", 0.81), (2023, "2023-01-28", 0.99),
                                                                     (2024, "2024-02-03", 1.13), (2025, "2025-02-01", 1.25), (2026, "2026-01-31", 1.37))]
    assert close(F.dps_cagr(kr, 5), (1.37 / 0.7) ** 0.2 - 1), "52/53-week drift stays within the ±45-day match"


# ---------------- annual series: period-end keys, unique labels, sum-of-quarters fallback ----------------
def test_annual_dps_rows_prefers_fy_fact_then_sum_of_four_quarters():
    fy_facts = {"2024-12-31": 0.62, "2025-12-31": 0.62}
    qbf = {"2025-01-01": {1: ("2025-03-31", 0.155), 2: ("2025-06-30", 0.155), 3: ("2025-09-30", 0.155), 4: ("2025-12-31", 0.155)},
           "2026-01-01": {1: ("2026-03-31", 0.17), 2: ("2026-06-30", 0.17), 3: ("2026-09-30", 0.17), 4: ("2026-12-31", 0.17)},
           "2027-01-01": {1: ("2027-03-31", 0.18), 2: ("2027-06-30", 0.18)}}
    rows = F.annual_dps_rows(fy_facts, qbf)
    assert [r["fy"] for r in rows] == ["2024", "2025", "2026"], "2027 lacks four quarters -> no row"
    assert rows[1]["dps"] == 0.62 and rows[1]["basis"] == "fy_fact", "the FY fact wins over the quarter sum"
    assert close(rows[2]["dps"], 0.68) and rows[2]["basis"] == "sum_of_quarters" and rows[2]["period_end"] == "2026-12-31"


def test_annual_dps_rows_keeps_both_fiscal_years_that_end_in_the_same_calendar_year():
    # KVUE / TDY: a 52-week year ending 2023-01-01 followed by one ending 2023-12-31
    rows = F.annual_dps_rows({"2022-01-02": 0.8, "2023-01-01": 0.9, "2023-12-31": 1.0, "2024-12-29": 1.1}, {})
    assert [r["period_end"] for r in rows] == ["2022-01-02", "2023-01-01", "2023-12-31", "2024-12-29"], "no fiscal year dropped"
    assert len(set(r["fy"] for r in rows)) == 4, "labels unique"
    assert [r["fy"] for r in rows] == ["2021", "2022", "2023", "2024"], "collision -> the year most of each fiscal year falls in"
    assert F.fy_labels(["2024-02-03", "2025-02-01", "2026-01-31"]) == ["2024", "2025", "2026"], "no collision -> calendar year of the period end (Financials tab convention)"
    assert F.growth_years(rows) == 3 and F.last_cut_fy(rows) is None and close(F.dps_cagr(rows, 2), (1.1 / 0.9) ** 0.5 - 1)


def test_fy_label_puts_a_52_week_year_in_the_year_it_ends():
    assert F._fy_label("2023-01-02") == "2023", "KVUE fiscal 2023 (2023-01-02..2023-12-31)"
    assert F._fy_label("2025-02-02") == "2026", "KR fiscal year ending 2026-01-31"
    assert F._fy_label("2025-01-01") == "2025" and F._fy_label(None) is None


def test_dps_outliers_flags_unit_slips_only():
    assert F.dps_outliers(_annual((2016, 0.05), (2017, 8), (2018, 0.06))) == ["2017"]
    assert F.dps_outliers(_annual((2016, 0.05), (2017, 0.4), (2018, 0.06))) == [], "8x is not flagged"
    assert F.dps_outliers(_annual((2016, 0.05), (2017, 8))) == [], "needs both neighbours"


# ---------------- stock splits (filed ratios) ----------------
def test_split_factor_and_apply_splits_kr_2015():
    # KR companyfacts: FY ending 2013-02-02 = 0.53 in every filing (last 2015-04-01, pre-split);
    # FY ending 2014-02-01 restated to 0.315 in the 10-K filed 2016-03-29; split ratio 2 at 2015-06-25.
    splits = [("2015-06-25", 2)]
    assert F.split_factor("2015-04-01", splits) == 2 and F.split_factor("2016-03-29", splits) == 1 and F.split_factor(None, splits) == 1
    assert F.split_factor("2014-01-01", [("2015-06-25", 2), ("2020-01-01", 3)]) == 6, "ratios compound"
    dps_fy = {"declared": {"2013-02-02": 0.53, "2014-02-01": 0.315, "2015-01-31": 0.35}, "paid": {}}
    fy_filed = {"declared": {"2013-02-02": "2015-04-01", "2014-02-01": "2016-03-29", "2015-01-31": "2017-03-28"}, "paid": {}}
    dps_q = {"declared": {"2013-05-25": _q("2013-05-25", 0.15, 1, "2013-02-03", filed="2015-04-01"),
                          "2014-05-24": _q("2014-05-24", 0.083, 1, "2014-02-02", filed="2016-03-29")}, "paid": {}}
    dps_q, dps_fy, notes = F.apply_splits(dps_q, dps_fy, fy_filed, splits)
    assert close(dps_fy["declared"]["2013-02-02"], 0.265) and dps_fy["declared"]["2014-02-01"] == 0.315 and dps_fy["declared"]["2015-01-31"] == 0.35
    assert close(dps_q["declared"]["2013-05-25"]["val"], 0.075) and dps_q["declared"]["2013-05-25"]["split_factor"] == 2
    assert dps_q["declared"]["2014-05-24"]["val"] == 0.083 and "split_factor" not in dps_q["declared"]["2014-05-24"]
    assert len(notes) == 1 and "2-for-1 split effective 2015-06-25" in notes[0] and "declared" in notes[0]
    rows = F.annual_dps_rows(dps_fy["declared"], {})
    assert F.growth_years(rows) == 2 and F.last_cut_fy(rows) is None, "0.265 -> 0.315 -> 0.35: no phantom 40% cut in FY2014"
    assert F.apply_splits({"declared": {}, "paid": {}}, {"declared": {}, "paid": {}}, {}, [])[2] == []


def test_split_direction_reads_the_filed_share_counts():
    shares = {"2014-02-01": (520e6, "2015-04-01"), "2015-01-31": (990e6, "2016-03-29"), "2016-01-30": (980e6, "2017-03-28")}
    (d, filed, used, ev), = F.split_direction([("2015-06-25", 2)], shares)
    assert d == "2015-06-25" and filed == 2 and used == 2 and "520,000,000" in ev
    # a 1-for-10 reverse split filed as "10": the counts fall ~10x -> the inverse is used
    shares = {"2021-12-31": (100e6, "2022-03-01"), "2022-12-31": (10.2e6, "2023-03-01")}
    (d, filed, used, ev), = F.split_direction([("2022-06-01", 10)], shares)
    assert close(used, 0.1), "reverse split read from the share counts"
    assert F.split_direction([("2022-06-01", 10)], {})[0][2] == 10, "no share evidence -> the ratio as filed"
    assert F.split_direction([("2018-03-31", 0.6667)], {"2017-07-31": (100e6, "2017-10-01"), "2018-07-31": (68e6, "2018-09-13")})[0][2] == 0.6667, "ZS 2-for-3 reverse split filed as new/old"


def test_basis_breaks_guards_an_unfiled_split():
    # WSM-shaped without a ratio fact: DPS halves while diluted shares double -> a basis change, not a cut
    rows = [{"fy": "2021", "period_end": "2021-01-31", "dps": 2.0}, {"fy": "2022", "period_end": "2022-01-30", "dps": 2.6},
            {"fy": "2023", "period_end": "2023-01-29", "dps": 1.56}, {"fy": "2024", "period_end": "2024-01-28", "dps": 1.8}]
    shares = {"2021-01-31": 79e6, "2022-01-30": 76e6, "2023-01-29": 138e6, "2024-01-28": 130e6}
    assert [b[0] for b in F.basis_breaks(rows, shares)] == ["2023-01-29"]
    assert F.basis_breaks(rows, {}) == [], "no share evidence -> no break claimed"
    assert F.basis_breaks(rows, {"2022-01-30": 76e6, "2023-01-29": 80e6}) == [], "shares flat -> a real cut, reported as such"
    # 5.4.3: a split restates the prior year's diluted EPS by the same factor; a real share issuance does not
    eps_split = {"2022-01-30": 14.75, "2023-01-29": 8.1}      # 14.75 / 1.82 = 8.1: restated like the shares
    assert [b[0] for b in F.basis_breaks(rows, shares, eps_split)] == ["2023-01-29"], "EPS corroborates the split"
    rejected = []
    eps_real = {"2022-01-30": 14.75, "2023-01-29": 14.9}      # EPS flat while shares doubled: an issuance plus a real cut
    assert F.basis_breaks(rows, shares, eps_real, rejected) == [] and rejected[0][0] == "2023-01-29" and close(rejected[0][3], 14.9 / 14.75)
    assert [b[0] for b in F.basis_breaks(rows, shares, {"2022-01-30": -1.0, "2023-01-29": 2.0})] == ["2023-01-29"], "no positive EPS pair -> the shares + DPS rule stands alone"


# ---------------- combined issuance tags ----------------
def _facts(entries):
    """companyfacts-shaped dict from [(taxonomy, tag, unit, {start, end, val, form, filed, accn, fp, fy})]."""
    out = {"facts": {}}
    for tax, tag, unit, e in entries:
        out["facts"].setdefault(tax, {}).setdefault(tag, {"units": {}})["units"].setdefault(unit, []).append(e)
    return out


def _e(start, end, val, filed, accn, form="10-Q", fp="Q1", fy=2026):
    return {"start": start, "end": end, "val": val, "filed": filed, "accn": accn, "form": form, "fp": fp, "fy": fy}


def test_combined_duration_facts_sums_distinct_lines_in_one_filing_only():
    g = "us-gaap"
    facts = _facts([
        # ZS-shaped: option exercises + ESPP on two lines of the same 10-Q -> summed
        (g, "ProceedsFromStockOptionsExercised", "USD", _e("2025-08-01", "2026-01-31", 3984000, "2026-02-26", "A")),
        (g, "ProceedsFromIssuanceOfSharesUnderIncentiveAndShareBasedCompensationPlans", "USD", _e("2025-08-01", "2026-01-31", 21506000, "2026-02-26", "A")),
        # the same period re-reported under a renamed tag in a later filing -> the later filing alone, no double count
        (g, "ProceedsFromIssuanceOfSharesUnderIncentiveAndShareBasedCompensationPlansIncludingStockOptions", "USD", _e("2024-01-01", "2024-03-31", 9782000, "2025-05-07", "C")),
        (g, "ProceedsFromStockOptionsExercised", "USD", _e("2024-01-01", "2024-03-31", 9782000, "2024-05-08", "B")),
        # KR-shaped: the cash-flow line plus the ASC 718 note's option-exercise cash in the same 10-K (both 182,000,000) -> the line alone
        (g, "ProceedsFromIssuanceOfCommonStock", "USD", _e("2025-02-02", "2026-01-31", 182000000, "2026-03-31", "D", "10-K", "FY")),
        (g, "ProceedsFromStockOptionsExercised", "USD", _e("2025-02-02", "2026-01-31", 182000000, "2026-03-31", "D", "10-K", "FY")),
        # the aggregate tag beats everything filed beside it
        (g, "ProceedsFromIssuanceOrSaleOfEquity", "USD", _e("2023-01-01", "2023-12-31", 60000000, "2024-02-09", "E", "10-K", "FY")),
        (g, "ProceedsFromStockOptionsExercised", "USD", _e("2023-01-01", "2023-12-31", 60000000, "2024-02-09", "E", "10-K", "FY")),
    ])
    c = F.combined_duration_facts(facts, F.DUR["share_issuance"], F.ISSUANCE_SUPERSETS)
    assert c[("2025-08-01", "2026-01-31")][0] == 25490000 and set(c[("2025-08-01", "2026-01-31")][1].split("+")) == {"ProceedsFromStockOptionsExercised", "ProceedsFromIssuanceOfSharesUnderIncentiveAndShareBasedCompensationPlans"}
    assert c[("2024-01-01", "2024-03-31")][0] == 9782000 and c[("2024-01-01", "2024-03-31")][4] == "C"
    assert c[("2025-02-02", "2026-01-31")][0] == 182000000 and c[("2025-02-02", "2026-01-31")][1] == "ProceedsFromIssuanceOfCommonStock"
    assert c[("2023-01-01", "2023-12-31")][0] == 60000000 and c[("2023-01-01", "2023-12-31")][1] == "ProceedsFromIssuanceOrSaleOfEquity"
    assert F.combined_annual(facts, F.DUR["share_issuance"], F.ISSUANCE_SUPERSETS)[0] == {"2026-01-31": 182000000, "2023-12-31": 60000000}


def test_combined_duration_facts_sums_a_total_tag_smaller_than_its_parts():
    # 5.4.6 review blocker. FIG FY2025 (10-K): ProceedsFromIssuanceOfCommonStock 0 beside ProceedsFromStockOptionsExercised
    # 131,661,000 and ProceedsFromStockPlans 26,382,000 — three statement lines, not a total and two components
    g = "us-gaap"
    facts = _facts([
        (g, "ProceedsFromIssuanceOfCommonStock", "USD", _e("2025-01-01", "2025-12-31", 0, "2026-02-20", "F", "10-K", "FY")),
        (g, "ProceedsFromStockOptionsExercised", "USD", _e("2025-01-01", "2025-12-31", 131661000, "2026-02-20", "F", "10-K", "FY")),
        (g, "ProceedsFromStockPlans", "USD", _e("2025-01-01", "2025-12-31", 26382000, "2026-02-20", "F", "10-K", "FY")),
        # DHI FY2024: the common line 19.7M below the plan line 20.6M -> both
        (g, "ProceedsFromIssuanceOfCommonStock", "USD", _e("2023-10-01", "2024-09-30", 19700000, "2024-11-15", "D", "10-K", "FY")),
        (g, "ProceedsFromStockPlans", "USD", _e("2023-10-01", "2024-09-30", 20600000, "2024-11-15", "D", "10-K", "FY")),
        # ROP FY2025: treasury stock sales 22.4M beside stock-based compensation proceeds 115.0M -> both
        (g, "ProceedsFromSaleOfTreasuryStock", "USD", _e("2024-01-01", "2024-12-31", 22400000, "2025-02-21", "R", "10-K", "FY")),
        (g, "ProceedsFromStockOptionsExercised", "USD", _e("2024-01-01", "2024-12-31", 115000000, "2025-02-21", "R", "10-K", "FY")),
    ])
    c = F.combined_duration_facts(facts, F.DUR["share_issuance"], F.ISSUANCE_SUPERSETS)
    assert c[("2025-01-01", "2025-12-31")][0] == 131661000 + 26382000 and "ProceedsFromStockPlans" in c[("2025-01-01", "2025-12-31")][1]
    assert c[("2023-10-01", "2024-09-30")][0] == 40300000 and c[("2024-01-01", "2024-12-31")][0] == 137400000


def test_quarterly_series_derives_from_a_combined_issuance_series():
    g = "us-gaap"
    facts = _facts([
        (g, "ProceedsFromStockOptionsExercised", "USD", _e("2025-08-01", "2025-10-31", 3984000, "2025-11-25", "Q1")),
        (g, "ProceedsFromStockOptionsExercised", "USD", _e("2025-08-01", "2026-01-31", 3984000, "2026-02-26", "Q2", fp="Q2")),
        (g, "ProceedsFromIssuanceOfSharesUnderIncentiveAndShareBasedCompensationPlans", "USD", _e("2025-08-01", "2026-01-31", 21506000, "2026-02-26", "Q2", fp="Q2")),
        (g, "ProceedsFromStockOptionsExercised", "USD", _e("2025-08-01", "2026-04-30", 3984000, "2026-05-26", "Q3", fp="Q3")),
        (g, "ProceedsFromIssuanceOfSharesUnderIncentiveAndShareBasedCompensationPlans", "USD", _e("2025-08-01", "2026-04-30", 21506000, "2026-05-26", "Q3", fp="Q3")),
        (g, "ProceedsFromStockOptionsExercised", "USD", _e("2025-08-01", "2026-07-31", 3984000, "2026-09-03", "K", "10-K", "FY")),
        (g, "ProceedsFromIssuanceOfSharesUnderIncentiveAndShareBasedCompensationPlans", "USD", _e("2025-08-01", "2026-07-31", 59416000, "2026-09-03", "K", "10-K", "FY")),
    ])
    q = F.quarterly_series(None, None, derive=True, fy_starts={"2025-08-01"}, prebuilt=F.combined_duration_facts(facts, F.DUR["share_issuance"], F.ISSUANCE_SUPERSETS))
    assert [(e, q[e]["val"]) for e in sorted(q)] == [("2025-10-31", 3984000), ("2026-01-31", 21506000), ("2026-04-30", 0), ("2026-07-31", 37910000)]
    assert sum(q[e]["val"] for e in q) == 63400000, "the four quarters add back to the FY sum of both lines"
    assert q["2026-07-31"]["derived"] and q["2026-07-31"]["filed"] == "2026-09-03"


# ---------------- instant share count ----------------
def test_latest_share_count_prefers_the_newest_instant_then_dei():
    facts = _facts([
        ("us-gaap", "WeightedAverageNumberOfDilutedSharesOutstanding", "shares", _e("2026-01-01", "2026-03-31", 1900647000, "2026-04-30", "A")),
        ("us-gaap", "CommonStockSharesOutstanding", "shares", dict(_e(None, "2026-03-31", 2027130587, "2026-04-30", "A"), start=None)),
        ("dei", "EntityCommonStockSharesOutstanding", "shares", dict(_e(None, "2026-03-31", 2027130587, "2026-04-30", "A"), start=None)),
        ("dei", "EntityCommonStockSharesOutstanding", "shares", dict(_e(None, "2026-02-01", 2029792391, "2026-02-13", "K", "10-K", "FY"), start=None)),
    ])
    count, as_of, src = F.latest_share_count(facts)
    assert count == 2027130587 and as_of == "2026-03-31" and src.startswith("dei:EntityCommonStockSharesOutstanding")
    assert F.latest_share_count({"facts": {}}) is None


# ---------------- end-to-end on inline tables ----------------
def _fixture():
    annual = [
        {"fy": "2023", "period_end": "2023-12-31", "eps_diluted": 1.24, "dividends_paid": 900e6, "oe_conservative": 2420e6, "fcf": 2517e6, "shares_diluted": 1468e6},
        {"fy": "2024", "period_end": "2024-12-31", "eps_diluted": 1.22, "dividends_paid": 903e6, "oe_conservative": 1587e6, "fcf": 1693e6, "shares_diluted": 1476e6},
        {"fy": "2025", "period_end": "2025-12-31", "eps_diluted": 1.39, "dividends_paid": 908e6, "oe_conservative": 2102e6, "fcf": 2215e6, "shares_diluted": 1504e6},
    ]
    ends = ["2025-03-31", "2025-06-30", "2025-09-30", "2025-12-31", "2026-03-31"]
    qrows = [{"period_end": e, "shares_diluted": 1900e6 if e == "2026-03-31" else 1480e6,
              "dividends_paid": [226e6, 227e6, 227e6, 228e6, 248e6][i], "buybacks": [0, 0, 0, 0, 150e6][i], "share_issuance": [1e6, 1e6, 1e6, 1e6, 2e6][i]}
             for i, e in enumerate(ends)]
    dps_q = {"declared": {"2025-03-31": _q("2025-03-31", 0.155, 1, "2025-01-01"), "2025-06-30": _q("2025-06-30", 0.155, 2, "2025-01-01"),
                          "2025-09-30": _q("2025-09-30", 0.155, 3, "2025-01-01"), "2026-03-31": _q("2026-03-31", 0.155, 1, "2026-01-01")},
             "paid": {}}
    dps_fy = {"declared": {"2022-12-31": 0.62, "2023-12-31": 0.62, "2024-12-31": 0.62, "2025-12-31": 0.62}, "paid": {}}
    return annual, qrows, dps_q, dps_fy


def _div_flow_facts(qrows, tag):
    """flow_facts with one direct three-month dividends-paid fact per quarterly row (the row's value), filed under `tag`."""
    return {"dividends_paid": {(F._add_days(r["period_end"], -90), r["period_end"]): (r["dividends_paid"], tag, "USD", F._add_days(r["period_end"], 40), "A")
                               for r in qrows if F._num(r.get("dividends_paid"))}, "buybacks": {}, "share_issuance": {}}


def _ctx(**kw):
    ctx = {"filed_any": {"dividends_paid": True, "buybacks": True, "share_issuance": True}, "shares_instant": None, "latest_filed_period": {}, "split_notes": [], "splits": [], "warnings": []}
    ctx.update(kw)
    return ctx


def test_build_dividends_bank_shape():
    annual, qrows, dps_q, dps_fy = _fixture()
    ctx = _ctx(shares_instant=(2027130587, "2026-03-31", "dei:EntityCommonStockSharesOutstanding (10-Q filed 2026-04-30)"),
               latest_filed_period={"10-Q": "2026-06-30", "10-K": "2025-12-31"})
    d = F.build_dividends(annual, qrows, dps_q, dps_fy, 15.10, "2026-10-14", "prices.json stats.last", ctx)
    assert d["dps_basis"] == "declared" and d["frequency"] == "quarterly" and "FY2025" in d["frequency_basis"]
    assert close(d["dps_ttm"], 0.62) and "FY2025 DPS 0.62 + the quarters since (2026-03-31: 0.155)" in d["dps_ttm_basis"], "Q4 only in the FY fact -> FY rolled forward by Q1 2026 minus Q1 2025"
    assert any("not consecutive" in n and "182 days" in n for n in d["notes"])
    assert [r["fy"] for r in d["annual_dps"]] == ["2022", "2023", "2024", "2025"]
    assert close(d["dps_growth_yoy"], 0.0) and close(d["dps_cagr_3y"], 0.0) and d["dps_cagr_5y"] is None
    assert d["growth_years"] == 0 and d["last_cut_fy"] is None
    assert close(d["payout_ratio_eps"], 0.62 / 1.39) and close(d["payout_ratio_oe"], 908e6 / 2102e6) and close(d["payout_ratio_fcf"], 908e6 / 2215e6)
    assert close(d["dividends_paid_ttm"], 930e6) and close(d["buybacks_ttm"], 150e6) and close(d["issuance_ttm"], 5e6)
    assert d["shares_outstanding"] == 2027130587 and d["shares_diluted"] == 1900e6 and close(d["market_cap"], 15.10 * 2027130587), "market cap on the cover-page count, the weighted diluted count kept beside it"
    mc = 15.10 * 2027130587
    assert close(d["dividend_yield"], 0.62 / 15.10)
    assert close(d["buyback_yield"], 150e6 / mc) and close(d["net_buyback_yield"], 145e6 / mc)
    assert close(d["shareholder_yield"], 1075e6 / mc) and d["shareholder_yield_complete"] and "4/4 quarters filed" in d["shareholder_yield_basis"]
    assert [h["period_end"] for h in d["history"]] == ["2026-03-31", "2025-09-30", "2025-06-30", "2025-03-31"], "newest first"
    assert all(h["kind"] == "declared" for h in d["history"])
    assert any("latest 10-Q (period 2026-06-30) is not yet in EDGAR companyfacts" in n for n in d["notes"]) and len(ctx["warnings"]) == 1, "the filing feed is ahead of companyfacts: said in notes and warnings"


def test_build_dividends_no_dividend_payer_counts_buybacks_as_the_whole_return():
    annual, qrows, _, _ = _fixture()
    for r in list(annual) + qrows:
        r["dividends_paid"] = None
    ctx = _ctx(filed_any={"dividends_paid": False, "buybacks": True, "share_issuance": True})
    d = F.build_dividends(annual, qrows, {"declared": {}, "paid": {}}, {"declared": {}, "paid": {}}, 262.19, "2026-10-14", "prices.json stats.last", ctx)
    assert d["frequency"] == "none" and d["dps_ttm"] is None and d["dps_basis"] is None and d["annual_dps"] == [] and d["history"] == []
    assert d["dividends_paid_ttm"] is None, "no dividends paid facts -> the strict TTM stays null"
    assert d["legs"]["dividends_paid"]["value"] == 0.0 and "never filed" in d["legs"]["dividends_paid"]["basis"]
    assert close(d["buybacks_ttm"], 150e6) and d["buyback_yield"] is not None
    assert close(d["shareholder_yield"], d["net_buyback_yield"]) and d["shareholder_yield_complete"], "never-filed dividends are zero by the filer's own statements"
    assert d["payout_ratio_eps"] is None and any("not a dividend payer" in n for n in d["notes"])


def test_build_dividends_partial_legs_are_summed_and_named():
    annual, qrows, dps_q, dps_fy = _fixture()
    for r in qrows[:-1]:
        r["buybacks"] = None          # HBAN: the repurchase line only appears in the Q1 2026 10-Q
    for r in qrows:
        r["share_issuance"] = None    # issuance filed in older years but not in the window
    d = F.build_dividends(annual, qrows, dps_q, dps_fy, 15.10, "2026-10-14", "prices.json stats.last", _ctx())
    mc = 15.10 * 1900e6
    assert d["buybacks_ttm"] is None, "the strict TTM stays null"
    # 5.4.3: every flow yield is built from the filed legs and flagged in yield_basis — no partial numerator without the flag
    yb = d["yield_basis"]
    assert close(d["buyback_yield"], 150e6 / mc) and yb["buyback_yield"]["bound"] == "lower" and yb["buyback_yield"]["partial"] == ["buybacks"] and not yb["buyback_yield"]["complete"]
    assert close(d["net_buyback_yield"], 150e6 / mc) and yb["net_buyback_yield"]["bound"] == "indeterminate", "buybacks a lower bound, issuance unknown -> neither bound"
    assert yb["net_buyback_yield"]["excluded"] == ["share_issuance"] and yb["net_buyback_yield"]["filed"] == ["buybacks"]
    assert close(d["shareholder_yield"], (930e6 + 150e6) / mc) and not d["shareholder_yield_complete"] and yb["shareholder_yield"]["bound"] == "indeterminate"
    assert yb["shareholder_yield"]["filed"] == ["dividends_paid", "buybacks"] and yb["shareholder_yield"]["partial"] == ["buybacks"] and yb["shareholder_yield"]["zero"] == []
    assert "lower bound" in yb["buyback_yield"]["note"] and "neither bound" in yb["shareholder_yield"]["note"]
    assert "buybacks (1/4 quarters filed (2026-03-31) — a lower bound)" in d["shareholder_yield_basis"] and "share_issuance NOT INCLUDED" in d["shareholder_yield_basis"]
    assert d["shares_basis"] == "weighted_average_diluted_fallback" and d["shares_as_of"] == "2026-03-31"
    assert d["shares_source"].startswith("quarter ended 2026-03-31 weighted-average diluted count, fallback: no undimensioned") and d["shares_source"] in d["market_cap_basis"]
    assert any("no undimensioned period-end / cover-page share count" in n for n in d["notes"])
    # neither dividends nor buybacks known -> null, and yield_basis says why
    for r in qrows:
        r["dividends_paid"] = r["buybacks"] = None
    d = F.build_dividends(annual, qrows, dps_q, dps_fy, 15.10, "2026-10-14", "prices.json stats.last", _ctx())
    assert d["shareholder_yield"] is None and d["shareholder_yield_basis"] is None and d["buyback_yield"] is None and d["net_buyback_yield"] is None
    assert d["yield_basis"]["shareholder_yield"]["bound"] is None and "not filed for the window" in d["yield_basis"]["buyback_yield"]["note"]


def test_yield_basis_is_exact_when_every_leg_is_complete_and_flags_partial_issuance():
    annual, qrows, dps_q, dps_fy = _fixture()
    d = F.build_dividends(annual, qrows, dps_q, dps_fy, 15.10, "2026-10-14", "prices.json stats.last", _ctx())
    yb = d["yield_basis"]
    for k in ("buyback_yield", "net_buyback_yield", "shareholder_yield"):
        assert yb[k]["bound"] == "exact" and yb[k]["complete"] and yb[k]["excluded"] == [] and yb[k]["partial"] == [] and "note" not in yb[k], k
    assert yb["shareholder_yield"]["filed"] == ["dividends_paid", "buybacks", "share_issuance"] and close(yb["shareholder_yield"]["numerator"], 1075e6)
    assert yb["dividend_yield"]["bound"] == "exact" and close(yb["dividend_yield"]["numerator"], 0.62) and "price 15.1" in yb["dividend_yield"]["denominator"]
    # APP-shaped: never-filed dividends (zero), complete buybacks, issuance filed for two of four quarters
    for r in list(annual) + qrows:
        r["dividends_paid"] = None
    qrows[0]["share_issuance"] = qrows[1]["share_issuance"] = None
    ctx = _ctx(filed_any={"dividends_paid": False, "buybacks": True, "share_issuance": True}, shares_instant=(335291000, "2026-06-30", "us-gaap:CommonStockSharesOutstanding (10-Q filed 2026-08-05)"))
    d = F.build_dividends(annual, qrows, {"declared": {}, "paid": {}}, {"declared": {}, "paid": {}}, 262.19, "2026-10-14", "prices.json stats.last", ctx)
    yb = d["yield_basis"]
    mc = 262.19 * 335291000
    assert close(d["buyback_yield"], 150e6 / mc) and yb["buyback_yield"]["bound"] == "exact" and yb["buyback_yield"]["complete"]
    assert close(d["net_buyback_yield"], (150e6 - 4e6) / mc) and yb["net_buyback_yield"]["bound"] == "upper" and yb["net_buyback_yield"]["partial"] == ["share_issuance"]
    assert close(d["shareholder_yield"], d["net_buyback_yield"]) and yb["shareholder_yield"]["bound"] == "upper" and yb["shareholder_yield"]["zero"] == ["dividends_paid"]
    assert yb["shareholder_yield"]["filed"] == ["buybacks", "share_issuance"] and not d["shareholder_yield_complete"] and "upper bound" in yb["shareholder_yield"]["note"]
    assert yb["dividend_yield"]["numerator"] is None and yb["dividend_yield"]["bound"] is None and d["dividend_yield"] is None


def test_build_dividends_degrades_without_quarters_or_price():
    annual, _, _, _ = _fixture()
    dps_fy = {"declared": {"2023-12-31": 0.41, "2024-12-31": 0.39, "2025-12-31": 0.45}, "paid": {}}
    d = F.build_dividends(annual, [], {"declared": {}, "paid": {}}, dps_fy, None, None, None, _ctx(filed_any={"dividends_paid": True, "buybacks": False, "share_issuance": True}))
    assert d["dps_basis"] == "declared" and d["frequency"] is None, "FY-only facts: frequency not inferable"
    assert close(d["dps_ttm"], 0.45) and any("fewer than four" in n for n in d["notes"]) and d["dps_ttm_basis"].startswith("FY2025 DPS")
    assert d["last_cut_fy"] == "2024" and d["growth_years"] == 1
    assert d["dividends_paid_ttm"] is None and d["buybacks_ttm"] is None and d["issuance_ttm"] is None
    assert d["legs"]["dividends_paid"] == {"value": 908e6, "basis": "FY2025 annual fact", "complete": True}, "20-F filer: the latest fiscal year's flows, labelled"
    assert d["legs"]["buybacks"]["value"] == 0.0 and d["legs"]["share_issuance"]["value"] is None
    assert d["price"] is None and d["market_cap"] is None and d["dividend_yield"] is None and d["shareholder_yield"] is None
    assert d["shares_outstanding"] == 1504e6 and d["shares_as_of"] == "2025-12-31" and d["shares_basis"] == "weighted_average_diluted_fallback"
    assert d["shares_source"].startswith("FY2025 (period ended 2025-12-31) weighted-average diluted count, fallback: no undimensioned period-end / cover-page share count")
    assert d["yield_basis"]["shareholder_yield"]["denominator"] is None, "no price -> no market cap, the basis says so"
    assert close(d["payout_ratio_eps"], 0.45 / 1.39)


def test_build_dividends_uses_paid_when_no_declared_facts():
    annual, qrows, _, _ = _fixture()
    dps_q = {"declared": {}, "paid": {"2025-12-31": _q("2025-12-31", 0.3, 4, "2025-01-01"), "2025-06-30": _q("2025-06-30", 0.3, 2, "2025-01-01"),
                                     "2024-12-31": _q("2024-12-31", 0.3, 4, "2024-01-01"), "2024-06-30": _q("2024-06-30", 0.3, 2, "2024-01-01")}}
    d = F.build_dividends(annual, qrows, dps_q, {"declared": {}, "paid": {"2024-12-31": 0.6, "2025-12-31": 0.6}}, 10.0, "2026-10-14", "score.json price", _ctx())
    assert d["dps_basis"] == "paid" and d["frequency"] == "semiannual" and d["frequency_basis"].startswith("spacing")
    assert close(d["dps_ttm"], 0.6) and all(h["kind"] == "paid" for h in d["history"])
    # 2026-10-16: the price note is the volatile `price_note`, never an entry of the committed `notes`
    assert "score.json" in d["price_note"] and not any("score.json" in n for n in d["notes"])


def test_build_dividends_semiannual_with_the_second_payment_only_in_the_fy_total():
    annual, qrows, _, _ = _fixture()
    dps_q = {"declared": {"2024-06-30": _q("2024-06-30", 0.5, 2, "2024-01-01"), "2025-06-30": _q("2025-06-30", 0.5, 2, "2025-01-01")}, "paid": {}}
    d = F.build_dividends(annual, qrows, dps_q, {"declared": {"2024-12-31": 1.0, "2025-12-31": 1.0}, "paid": {}}, 10.0, "2026-10-14", "prices.json stats.last", _ctx())
    assert d["frequency"] == "semiannual" and "carried only in the FY total" in d["frequency_basis"]
    assert close(d["dps_ttm"], 1.0) and "no quarterly DPS fact since" in d["dps_ttm_basis"]


def test_build_dividends_mid_year_initiator_reads_quarterly():
    annual, qrows, _, _ = _fixture()
    qrows = qrows + [{"period_end": "2026-06-30", "shares_diluted": 1900e6, "dividends_paid": 250e6, "buybacks": 0, "share_issuance": 1e6}]
    dps_q = {"declared": {"2025-09-30": _q("2025-09-30", 0.5, 3, "2025-01-01"), "2025-12-31": _q("2025-12-31", 0.5, 4, "2025-01-01"),
                          "2026-03-31": _q("2026-03-31", 0.5, 1, "2026-01-01"), "2026-06-30": _q("2026-06-30", 0.5, 2, "2026-01-01")}, "paid": {}}
    d = F.build_dividends(annual, qrows, dps_q, {"declared": {"2025-12-31": 1.0}, "paid": {}}, 50.0, "2026-10-14", "prices.json stats.last", _ctx())
    assert d["frequency"] == "quarterly" and d["frequency_basis"].startswith("spacing of the latest 4"), "four consecutive quarterly facts, not 'semiannual' from the two inside FY2025"
    assert close(d["dps_ttm"], 2.0) and d["dps_ttm_basis"].startswith("sum of the four quarterly DPS facts")


def test_build_dividends_stale_fy_fact_is_not_a_trailing_dividend():
    # TKO: the only DPS fact is CommonStockDividendsPerShareCashPaid = 3.86 for FY2023; FY2024/FY2025 carry none,
    # while PaymentsOfDividendsCommonStock is filed every quarter (FY2025 = 185,155,000)
    annual = [{"fy": str(y), "period_end": f"{y}-12-31", "eps_diluted": 1.0, "dividends_paid": [None, 185155000][y == 2025], "oe_conservative": 1e9, "fcf": 1e9, "shares_diluted": 76e6} for y in (2023, 2024, 2025)]
    ends = ["2025-09-30", "2025-12-31", "2026-03-31", "2026-06-30"]
    qrows = [{"period_end": e, "shares_diluted": 76e6, "dividends_paid": [62373000, 60647000, 58466000, 58873000][i], "buybacks": None, "share_issuance": None} for i, e in enumerate(ends)]
    ctx = _ctx(flow_facts=_div_flow_facts(qrows, "PaymentsOfDividendsCommonStock"))
    d = F.build_dividends(annual, qrows, {"declared": {}, "paid": {}}, {"declared": {}, "paid": {"2023-12-31": 3.86}}, 172.38, "2026-10-14", "prices.json stats.last", ctx)
    assert d["dps_ttm"] is None and d["dividend_yield"] is None and d["dps_basis"] == "paid"
    # 5.4.5: payer status and frequency come from the cash dividends paid when the per-share facts cannot give them
    assert d["frequency"] == "quarterly" and any("stale" in n and "per-share rate is not tagged" in n for n in d["notes"])
    assert d["frequency_basis"].startswith("cash dividends paid are filed for 4 of the last four quarters (2025-09-30: 62.4M") and "the per-share facts do not give the cadence" in d["frequency_basis"]
    assert d["dps_growth_yoy"] is None and d["dps_cagr_3y"] is None and d["growth_years"] == 0
    assert any("more than 15 months older" in n and "FY2023" in n for n in d["notes"])
    assert close(d["dividends_paid_ttm"], 240359000) and [r["fy"] for r in d["annual_dps"]] == ["2023"], "the FY2023 fact stays in the series, it just is not 'trailing'"


def test_build_dividends_suspended_then_reinstated():
    # CCL: 0.5 quarterly through FY2019, 0.5 then 0/0/0 in FY2020 (3-month facts inside the 10-K), nothing until
    # 0.15 declared for the quarters ended 2026-02-28, 2026-05-31 and 2026-08-31
    annual = [{"fy": str(y), "period_end": f"{y}-11-30", "eps_diluted": 1.0, "dividends_paid": None, "oe_conservative": 1e9, "fcf": 1e9, "shares_diluted": 1.3e9} for y in range(2019, 2026)]
    qrows = [{"period_end": e, "shares_diluted": 1.3e9, "dividends_paid": v, "buybacks": None, "share_issuance": None}
             for e, v in (("2025-11-30", None), ("2026-02-28", 208e6), ("2026-05-31", 206e6), ("2026-08-31", 204e6))]
    dq = {}
    for i, e in enumerate(("2019-02-28", "2019-05-31", "2019-08-31", "2019-11-30")):
        dq[e] = _q(e, 0.5, i + 1, "2018-12-01")
    for i, (e, v) in enumerate((("2020-02-29", 0.5), ("2020-05-31", 0), ("2020-08-31", 0), ("2020-11-30", 0))):
        dq[e] = _q(e, v, i + 1, "2019-12-01")
    for i, e in enumerate(("2026-02-28", "2026-05-31", "2026-08-31")):
        dq[e] = _q(e, 0.15, i + 1, "2025-12-01")
    d = F.build_dividends(annual, qrows, {"declared": dq, "paid": {}}, {"declared": {}, "paid": {}}, 25.97, "2026-10-14", "prices.json stats.last", _ctx())
    assert [(r["fy"], r["dps"]) for r in d["annual_dps"]] == [("2019", 2.0), ("2020", 0.5)], "sum-of-quarters years"
    assert d["dps_ttm"] is None and d["dividend_yield"] is None, "0.15 x 3 is not a trailing twelve months and FY2020 is stale"
    assert any("suspended / reinstated" in n and "do not make a trailing twelve months" in n for n in d["notes"])
    assert d["frequency"] == "quarterly" and "2026-02-28, 2026-05-31, 2026-08-31" in d["frequency_basis"], "the reinstated rate is quarterly, not 'irregular'"
    assert d["last_cut_fy"] == "2020" and d["growth_years"] == 0 and d["dps_growth_yoy"] is None and d["dps_cagr_5y"] is None
    assert d["history"][0] == {"period_end": "2026-08-31", "dps": 0.15, "kind": "declared"}


def test_build_dividends_cash_dividends_without_a_per_share_tag():
    # ESLT: PaymentsOfDividends on the 20-F (111,693,000 for FY2025), no per-share fact, no 10-Qs
    annual = [{"fy": str(y), "period_end": f"{y}-12-31", "eps_diluted": 10.0, "dividends_paid": v, "buybacks": None, "share_issuance": 26000, "oe_conservative": 5e8, "fcf": 6e8, "shares_diluted": 44.7e6}
              for y, v in ((2023, 89248000), (2024, 88958000), (2025, 111693000))]
    d = F.build_dividends(annual, [], {"declared": {}, "paid": {}}, {"declared": {}, "paid": {}}, 701.38, "2026-10-14", "prices.json stats.last",
                          _ctx(filed_any={"dividends_paid": True, "buybacks": True, "share_issuance": True}, shares_instant=(46442352, "2025-12-31", "dei:EntityCommonStockSharesOutstanding (20-F filed 2026-03-17)")))
    assert d["frequency"] is None, "a real payer must not render in the 'No dividend' state"
    assert any("111.7M" in n and "per-share rate not tagged" in n for n in d["notes"])
    assert d["dps_ttm"] is None and d["dividend_yield"] is None
    assert d["legs"]["dividends_paid"]["value"] == 111693000 and "annual" in d["flows_basis"]
    assert close(d["payout_ratio_oe"], 111693000 / 5e8)
    mc = 701.38 * 46442352
    assert close(d["shareholder_yield"], (111693000 - 26000) / mc) and "buybacks NOT INCLUDED" in d["shareholder_yield_basis"] and not d["shareholder_yield_complete"]


def test_build_dividends_unfiled_split_truncates_the_comparable_series():
    # diluted EPS restated by the same factor as the shares (10.4 -> 5.72 across the 1.82x count move): a split
    annual = [{"fy": str(y), "period_end": e, "eps_diluted": eps, "dividends_paid": 3e8, "oe_conservative": 1e9, "fcf": 1e9, "shares_diluted": s}
              for y, e, s, eps in ((2021, "2021-01-31", 79e6, 10.0), (2022, "2022-01-30", 76e6, 10.4), (2023, "2023-01-29", 138e6, 5.72), (2024, "2024-01-28", 130e6, 6.0))]
    dps_fy = {"declared": {"2021-01-31": 2.0, "2022-01-30": 2.6, "2023-01-29": 1.56, "2024-01-28": 1.8}, "paid": {}}
    d = F.build_dividends(annual, [], {"declared": {}, "paid": {}}, dps_fy, 100.0, "2026-10-14", "prices.json stats.last", _ctx())
    assert d["last_cut_fy"] is None and d["growth_years"] == 1 and d["growth_from_fy"] == "2023"
    assert d["basis_breaks"] == [{"period_end": "2023-01-29", "dps_ratio": 1.56 / 2.6, "shares_ratio": 138e6 / 76e6}] and d["basis_breaks_rejected"] == []
    assert any("share-basis change (split)" in n and "not a cut" in n for n in d["notes"])
    assert d["dps_cagr_3y"] is None, "no comparable endpoint three years back"
    # 5.4.3: the same shares + DPS move with EPS NOT restated (an equity raise and a real cut) is reported as a cut
    for r in annual:
        r["eps_diluted"] = 5.0
    d = F.build_dividends(annual, [], {"declared": {}, "paid": {}}, dps_fy, 100.0, "2026-10-14", "prices.json stats.last", _ctx())
    assert d["basis_breaks"] == [] and d["last_cut_fy"] == "2023" and d["growth_from_fy"] == "2021"
    assert d["basis_breaks_rejected"] == [{"period_end": "2023-01-29", "dps_ratio": 1.56 / 2.6, "shares_ratio": 138e6 / 76e6, "eps_ratio": 1.0}]
    assert any("diluted EPS moved ×1.00" in n and "real cut" in n for n in d["notes"])
    assert close(d["dps_cagr_3y"], (1.8 / 2.0) ** (1 / 3) - 1), "the full series is comparable again"


def test_dps_fy_facts_prefers_the_value_most_filings_agree_on_over_a_later_unit_slip():
    # GFI: FY2017 DividendsRecognisedAsDistributionsToOwnersPerShare = 0.08 (20-F/A 2018-04-23, 20-F 2019-03-29) then 8 (20-F 2020-04-06);
    # FY2018 = 0.06 / 6 / 0.06 (restated back); FY2019 = 5 then 0.05 twice
    i = "ifrs-full"
    tag = "DividendsRecognisedAsDistributionsToOwnersPerShare"
    def fy(start, end, val, filed, accn, form="20-F"):
        return (i, tag, "USD/shares", _e(start, end, val, filed, accn, form, "FY", int(end[:4])))
    facts = _facts([
        fy("2016-01-01", "2016-12-31", 0.05, "2018-04-23", "A", "20-F/A"), fy("2016-01-01", "2016-12-31", 0.05, "2019-03-29", "B"),
        fy("2017-01-01", "2017-12-31", 0.08, "2018-04-23", "A", "20-F/A"), fy("2017-01-01", "2017-12-31", 0.08, "2019-03-29", "B"), fy("2017-01-01", "2017-12-31", 8, "2020-04-06", "C"),
        fy("2018-01-01", "2018-12-31", 0.06, "2019-03-29", "B"), fy("2018-01-01", "2018-12-31", 6, "2020-04-06", "C"), fy("2018-01-01", "2018-12-31", 0.06, "2021-03-31", "D"),
        fy("2019-01-01", "2019-12-31", 5, "2020-04-06", "C"), fy("2019-01-01", "2019-12-31", 0.05, "2021-03-31", "D"), fy("2019-01-01", "2019-12-31", 0.05, "2022-03-31", "E"),
        fy("2020-01-01", "2020-12-31", 0.16, "2021-03-31", "D"),
    ])
    vals, tags, filed, notes = F.dps_fy_facts(facts, F.DUR["dps_declared"])
    assert vals == {"2016-12-31": 0.05, "2017-12-31": 0.08, "2018-12-31": 0.06, "2019-12-31": 0.05, "2020-12-31": 0.16}
    assert filed["2017-12-31"] == "2019-03-29", "the filed date is the latest filing of the value used (split restatement keys on it)"
    # 5.4.5: every power-of-ten disagreement is noted, also when the value used is the latest filing's (FY2018, FY2019)
    assert len(notes) == 3 and [n.split(" is filed as ")[0][-10:] for n in notes] == ["2017-12-31", "2018-12-31", "2019-12-31"]
    n17 = notes[0]
    assert "period ended 2017-12-31 is filed as 0.08" in n17 and "8 (20-F filed 2020-04-06)" in n17 and "unit slip" in n17
    assert "0.08 (20-F/A filed 2018-04-23, 20-F filed 2019-03-29)" in n17 and n17.endswith("the value most filings agree on"), \
        "an amended 20-F is a filing of the period, so 0.08 wins 2-1 and the note says so"
    assert "is filed as 0.06" in notes[1] and "6 (20-F filed 2020-04-06)" in notes[1] and "is filed as 0.05" in notes[2]
    assert F.dps_outliers(F.annual_dps_rows(vals, {})) == [], "no 10x outlier is left in the series"
    # a tie (one filing each, 100x apart) goes to the value nearest the tag's other years, and the note says it was a tie
    facts = _facts([fy("2017-01-01", "2017-12-31", 0.08, "2018-04-23", "A"), fy("2017-01-01", "2017-12-31", 8, "2020-04-06", "C"), fy("2018-01-01", "2018-12-31", 0.06, "2019-03-29", "B")])
    vals, _, _, notes = F.dps_fy_facts(facts, F.DUR["dps_declared"])
    assert vals["2017-12-31"] == 0.08 and len(notes) == 1 and notes[0].endswith("the value closest to the tag's other fiscal years (the filings split evenly)")
    # a real restatement (not a power of ten) still takes the latest filing
    facts = _facts([fy("2017-01-01", "2017-12-31", 0.08, "2018-04-23", "A"), fy("2017-01-01", "2017-12-31", 0.09, "2019-03-29", "B")])
    v, _, f, n = F.dps_fy_facts(facts, F.DUR["dps_declared"])
    assert v["2017-12-31"] == 0.09 and f["2017-12-31"] == "2019-03-29" and n == []
    assert F.annual_series(facts, F.DUR["dps_declared"], True)[0] == v, "agrees with annual_series when there is no slip"


def test_fallback_share_count_uses_the_most_inclusive_recent_diluted_count():
    # TKO: no undimensioned instant count; Q2 2026 three-month diluted 75,870,706 (if-converted units excluded that quarter) vs 194,631,394 in Q1 2026 and 194,011,072 for FY2025
    qrows = [{"period_end": e, "shares_diluted": s, "shares_diluted_derived": d} for e, s, d in
             (("2025-09-30", 199061830, False), ("2025-12-31", 196182397, True), ("2026-03-31", 194631394, False), ("2026-06-30", 75870706, False))]
    annual = [{"fy": "2025", "period_end": "2025-12-31", "shares_diluted": 194011072}]
    count, as_of, src = F.fallback_share_count(qrows, annual)
    assert count == 194631394 and as_of == "2026-03-31" and src.startswith("quarter ended 2026-03-31 weighted-average diluted count, fallback: no undimensioned")
    assert "75,870,706" in src and ">20% lower" in src and "if-converted" in src, "the latest quarter's own count is named and the reason given"
    # an ordinary buyback year: the latest quarter is used as filed
    qrows = [{"period_end": e, "shares_diluted": s} for e, s in (("2025-09-30", 100e6), ("2025-12-31", 98e6), ("2026-03-31", 96e6), ("2026-06-30", 94e6))]
    count, as_of, src = F.fallback_share_count(qrows, [{"fy": "2025", "period_end": "2025-12-31", "shares_diluted": 99e6}])
    assert count == 94e6 and as_of == "2026-06-30" and ">20% lower" not in src
    assert F.fallback_share_count([], []) is None
    d = F.build_dividends([{"fy": "2025", "period_end": "2025-12-31", "eps_diluted": 2.26, "dividends_paid": 185155000, "oe_conservative": 1e9, "fcf": 1e9, "shares_diluted": 194011072}],
                          [dict(r, dividends_paid=5e7, buybacks=None, share_issuance=None) for r in
                           ({"period_end": "2025-09-30", "shares_diluted": 199061830}, {"period_end": "2025-12-31", "shares_diluted": 196182397, "shares_diluted_derived": True},
                            {"period_end": "2026-03-31", "shares_diluted": 194631394}, {"period_end": "2026-06-30", "shares_diluted": 75870706})],
                          {"declared": {}, "paid": {}}, {"declared": {}, "paid": {}}, 172.38, "2026-10-14", "prices.json stats.last", _ctx())
    assert d["shares_outstanding"] == 194631394 and d["shares_basis"] == "weighted_average_diluted_fallback" and d["shares_diluted"] == 75870706
    assert close(d["market_cap"], 172.38 * 194631394) and d["shares_source"] in d["market_cap_basis"], "market cap carries the same basis note, never null while a weighted count exists"


def test_build_dividends_names_a_label_collision():
    # KVUE / TDY: the annual table labels both the year ended 2023-01-01 and the year ended 2023-12-31 "2023" (calendar year of the period end)
    annual = [{"fy": e[:4], "period_end": e, "eps_diluted": 2.0, "dividends_paid": 1e8, "oe_conservative": 5e8, "fcf": 5e8, "shares_diluted": 1e8}
              for e in ("2022-01-02", "2023-01-01", "2023-12-31", "2024-12-29")]
    dps_fy = {"declared": {"2022-01-02": 0.8, "2023-01-01": 0.9, "2023-12-31": 1.0, "2024-12-29": 1.1}, "paid": {}}
    d = F.build_dividends(annual, [], {"declared": {}, "paid": {}}, dps_fy, 20.0, "2026-10-14", "prices.json stats.last", _ctx())
    assert [r["fy"] for r in d["annual_dps"]] == ["2021", "2022", "2023", "2024"] and d["fy_label_basis"].startswith("the year most of each fiscal year falls in")
    assert any("FY2022 here (period ended 2023-01-01) is labelled FY2023 in the annual / quarterly tables" in n and "join on period_end" in n for n in d["notes"])
    assert d["growth_years"] == 3 and close(d["dps_cagr_3y"], (1.1 / 0.8) ** (1 / 3) - 1)
    # KR: 52/53-week years, no collision -> the annual table's labels, no note
    annual = [{"fy": e[:4], "period_end": e, "eps_diluted": 2.0, "dividends_paid": 1e8, "oe_conservative": 5e8, "fcf": 5e8, "shares_diluted": 1e8} for e in ("2024-02-03", "2025-02-01", "2026-01-31")]
    d = F.build_dividends(annual, [], {"declared": {}, "paid": {}}, {"declared": {"2024-02-03": 1.13, "2025-02-01": 1.25, "2026-01-31": 1.37}, "paid": {}}, 63.0, "2026-10-14", "prices.json stats.last", _ctx())
    assert [r["fy"] for r in d["annual_dps"]] == ["2024", "2025", "2026"] and d["fy_label_basis"].startswith("calendar year") and not any("labels" in n for n in d["notes"])


# ---------------- 5.4.4 adversarial-review fixes ----------------
def _ratio_fact(end, val, filed, form="10-K", fp="FY"):
    return ("us-gaap", "StockholdersEquityNoteStockSplitConversionRatio1", "pure", {"end": end, "val": val, "filed": filed, "form": form, "fp": fp, "accn": filed})


def _sh(start, end, val, filed, form="10-Q", fp="Q1"):
    return ("us-gaap", "WeightedAverageNumberOfDilutedSharesOutstanding", "shares", _e(start, end, val, filed, filed, form, fp))


def test_split_events_reads_one_split_tagged_at_several_dates():
    # TSCO: the 5-for-1 is tagged at 2024-12-05 (10-K, twice), 2024-12-20 (10-Q) and 2024-12-28 (10-K, CY2024 frame); the 2013 2-for-1 once
    facts = _facts([_ratio_fact("2013-09-28", 2, "2014-02-19"), _ratio_fact("2024-12-05", 5, "2025-02-20"), _ratio_fact("2024-12-05", 5, "2026-02-19"),
                    _ratio_fact("2024-12-20", 5, "2025-08-07", "10-Q", "Q2"), _ratio_fact("2024-12-28", 5, "2025-02-20")])
    dups = []
    assert F.split_events(facts, duplicates=dups) == [("2013-09-28", 2), ("2024-12-05", 5)], "three context dates, one split"
    assert dups == [("2024-12-05", 5, ["2024-12-20", "2024-12-28"])]
    assert F.split_factor("2024-02-23", [("2013-09-28", 2), ("2024-12-05", 5)]) == 5, "a 10-K filed in Feb 2024 is divided by 5, not 125"
    # two real splits of the same ratio more than 180 days apart stay two events and compound
    facts = _facts([_ratio_fact("2020-03-01", 2, "2020-05-01"), _ratio_fact("2021-03-01", 2, "2021-05-01")])
    assert F.split_events(facts) == [("2020-03-01", 2), ("2021-03-01", 2)]
    assert F.split_factor("2019-01-01", [("2020-03-01", 2), ("2021-03-01", 2)]) == 4


def test_split_direction_drops_a_duplicate_ratio_that_overshoots_the_share_counts():
    # NVDA-shaped: the 4-for-1 tagged again 270 days later rests on the same two fiscal-year counts (x4.06) — compounding would read x16
    shares = {"2020-01-26": (620e6, "2020-02-20"), "2021-01-31": (2520e6, "2022-03-18")}
    dropped = []
    kept = F.split_direction([("2021-06-03", 4), ("2022-03-01", 4)], shares, dropped=dropped)
    assert [(d, used) for d, r, used, ev in kept] == [("2021-06-03", 4)] and dropped[0][0] == "2022-03-01" and "×16.00" in dropped[0][2]
    # a genuine second split that the counts confirm (x8 between the two fiscal years) is kept
    shares = {"2020-01-26": (620e6, "2020-02-20"), "2021-01-31": (5000e6, "2022-03-18")}
    assert [used for _, _, used, _ in F.split_direction([("2021-06-03", 4), ("2021-12-01", 2)], shares)] == [4, 2]
    assert len(F.split_direction([("2021-06-03", 4), ("2022-03-01", 4)], {})) == 2, "no share evidence -> nothing is dropped"


def test_split_filing_cutoff_comes_from_the_re_filed_share_counts():
    # CTAS: ratio 4 tagged at 2024-05-02 (board approval); the 10-K filed 2024-07-25 still carries pre-split counts and DPS;
    # the Q1 FY2025 10-Q filed 2024-10-04 re-files the Aug-2023 quarter's count x4 — that is the first filing on the new basis
    facts = _facts([
        _ratio_fact("2024-05-02", 4, "2024-07-25"),
        _sh("2023-06-01", "2023-08-31", 103572000, "2023-10-05"), _sh("2023-06-01", "2023-08-31", 414289000, "2024-10-04"),
        _sh("2023-06-01", "2024-05-31", 103367000, "2024-07-25", "10-K", "FY"), _sh("2023-06-01", "2024-05-31", 413468000, "2025-07-28", "10-K", "FY"),
        _sh("2024-06-01", "2024-08-31", 410496000, "2024-10-04"),
    ])
    ref = F.share_refilings(facts)
    assert [(e, round(k, 2), o, n) for e, k, o, n in ref] == [("2023-08-31", 4.0, "2023-10-05", "2024-10-04"), ("2024-05-31", 4.0, "2024-07-25", "2025-07-28")]
    assert F.split_filing_cutoffs([("2024-05-02", 4)], ref)["2024-05-02"][0] == "2024-10-04"
    assert F.split_filing_cutoffs([("2024-05-02", 4)], []) == {}, "no evidence -> the ratio date stands"
    assert F.split_filing_cutoffs([("2024-05-02", 4)], [("2019-05-31", 4.0, "2019-07-01", "2020-07-01")]) == {}, "a re-filing years away is not this split's"
    splits = [("2024-05-02", 4, "2024-10-04")]
    assert F.split_factor("2024-07-25", splits) == 4 and F.split_factor("2024-10-04", splits) == 1, "filed after the ratio date but before the first post-split filing = pre-split"
    assert F.split_factor("2024-07-25", [("2024-05-02", 4)]) == 1, "two-tuple splits keep the ratio date as the cutoff"
    dps_fy = {"declared": {"2022-05-31": 3.8, "2023-05-31": 1.15}, "paid": {}}
    fy_filed = {"declared": {"2022-05-31": "2024-07-25", "2023-05-31": "2025-07-28"}, "paid": {}}
    _, dps_fy, notes = F.apply_splits({"declared": {}, "paid": {}}, dps_fy, fy_filed, splits)
    assert close(dps_fy["declared"]["2022-05-31"], 0.95) and dps_fy["declared"]["2023-05-31"] == 1.15, "FY2022 3.80 -> 0.95, no phantom 70% cut"
    assert "first filed on the new basis 2024-10-04" in notes[0]
    rows = F.annual_dps_rows(dps_fy["declared"], {})
    assert F.basis_breaks(rows, {"2022-05-31": 103e6, "2023-05-31": 413e6}) == [] and F.last_cut_fy(rows) is None


def test_dps_fy_facts_reads_a_split_restatement_not_a_unit_slip():
    # AVGO: FY2022 CashPaid 16.4 in the 10-Ks filed 2022-12-16 and 2023-12-14, 1.64 in the 10-K filed 2024-12-20 after the July 2024 10-for-1
    tag = "CommonStockDividendsPerShareCashPaid"

    def fy(start, end, val, filed):
        return ("us-gaap", tag, "USD/shares", _e(start, end, val, filed, filed, "10-K", "FY", int(end[:4])))
    facts = _facts([fy("2021-11-01", "2022-10-30", 16.4, "2022-12-16"), fy("2021-11-01", "2022-10-30", 16.4, "2023-12-14"), fy("2021-11-01", "2022-10-30", 1.64, "2024-12-20"),
                    fy("2022-10-31", "2023-10-29", 18.4, "2023-12-14"), fy("2022-10-31", "2023-10-29", 1.84, "2024-12-20"), fy("2022-10-31", "2023-10-29", 1.84, "2025-12-18"),
                    fy("2023-10-30", "2024-11-03", 2.105, "2024-12-20")])
    splits = [("2024-07-12", 10, "2024-09-11")]
    vals, _, filed, notes = F.dps_fy_facts(facts, F.DUR["dps_paid"], splits=splits)
    assert vals == {"2022-10-30": 1.64, "2023-10-29": 1.84, "2024-11-03": 2.105} and filed["2022-10-30"] == "2024-12-20"
    assert len(notes) == 2 and "restated for the 10-for-1 split effective 2024-07-12" in notes[0] and "1.64 used" in notes[0] and "unit slip" not in notes[0]
    assert F.split_factor(filed["2022-10-30"], splits) == 1, "the restated value is already on today's basis and is never divided again"
    # without a ratio fact or share evidence the majority rule stands (GFI: 0.08 twice vs 8 once, shares unchanged)
    vals, _, _, notes = F.dps_fy_facts(facts, F.DUR["dps_paid"])
    assert vals["2022-10-30"] == 16.4 and "unit slip" in notes[0]
    # the re-filed diluted share counts alone are evidence (an unfiled split restated in the same 10-K)
    vals, _, _, notes = F.dps_fy_facts(facts, F.DUR["dps_paid"], refilings=[("2023-10-29", 10.0, "2023-12-14", "2024-12-20")])
    assert vals["2022-10-30"] == 1.64 and "no ratio fact filed" in notes[0]
    # a ratio that does not match the disagreement is not this period's restatement: the 2-1 majority rule decides
    vals, _, _, notes = F.dps_fy_facts(facts, F.DUR["dps_paid"], splits=[("2024-07-12", 4, "2024-09-11")])
    assert vals["2022-10-30"] == 16.4 and "unit slip" in notes[0]


def test_build_dividends_switches_basis_where_the_declared_tag_stops():
    # AVGO-shaped: declared facts end FY2020, CashPaid runs FY2019..FY2025 with quarterly facts to 2026-08-02 -> primary basis = paid
    ends = ["2019-11-03", "2020-11-01", "2021-10-31", "2022-10-30", "2023-10-29", "2024-11-03", "2025-11-02"]
    annual = [{"fy": e[:4], "period_end": e, "eps_diluted": 3.0, "dividends_paid": 1e10, "oe_conservative": 2e10, "fcf": 2e10, "shares_diluted": 4.7e9} for e in ends]
    qends = [("2025-08-03", 3, "2024-11-04"), ("2025-11-02", 4, "2024-11-04"), ("2026-02-01", 1, "2025-11-03"), ("2026-05-03", 2, "2025-11-03"), ("2026-08-02", 3, "2025-11-03")]
    qrows = [{"period_end": e, "fq": fq, "shares_diluted": 4.7e9, "dividends_paid": 2.8e9, "buybacks": 2e9, "share_issuance": 5e7} for e, fq, _ in qends]
    paid_q = {"2025-02-02": _q("2025-02-02", 0.59, 1, "2024-11-04"), "2025-05-04": _q("2025-05-04", 0.59, 2, "2024-11-04"), "2025-08-03": _q("2025-08-03", 0.59, 3, "2024-11-04"),
              "2026-02-01": _q("2026-02-01", 0.65, 1, "2025-11-03"), "2026-05-03": _q("2026-05-03", 0.65, 2, "2025-11-03"), "2026-08-02": _q("2026-08-02", 0.65, 3, "2025-11-03")}
    decl_q = {e: _q(e, 0.325, i + 1, "2019-11-04") for i, e in enumerate(("2020-02-02", "2020-05-03", "2020-08-02", "2020-11-01"))}
    paid_fy = dict(zip(ends, (1.0, 1.265, 1.44, 1.64, 1.84, 2.105, 2.36)))
    dps_fy = {"declared": {"2019-11-03": 1.06, "2020-11-01": 1.3}, "paid": paid_fy}
    d = F.build_dividends(annual, qrows, {"declared": decl_q, "paid": paid_q}, dps_fy, 350.0, "2026-10-14", "prices.json stats.last", _ctx())
    assert d["dps_basis"] == "paid" and "declared facts exist only inside that span and are not used" in d["dps_basis_detail"]
    assert [(r["fy"], r["dps"], r["kind"]) for r in d["annual_dps"]] == [(e[:4], paid_fy[e], "paid") for e in ends], "the whole paid history, nothing from the declared tag"
    assert d["history"][0] == {"period_end": "2026-08-02", "dps": 0.65, "kind": "paid"} and all(h["kind"] == "paid" for h in d["history"])
    assert close(d["dps_ttm"], 2.36 + 3 * 0.65 - 3 * 0.59) and d["frequency"] == "quarterly" and d["growth_years"] == 6 and d["last_cut_fy"] is None
    assert not any("suspended" in n for n in d["notes"]), "an active payer no longer reads as suspended"
    # the reverse switch (paid history, declared facts only in the newest year): mixed, each row keeps its kind, the switch is noted
    dps_fy2 = {"declared": {"2025-11-02": 2.36}, "paid": {e: v for e, v in paid_fy.items() if e < "2025-11-02"}}
    d = F.build_dividends(annual, [], {"declared": {}, "paid": {}}, dps_fy2, 350.0, "2026-10-14", "prices.json stats.last", _ctx())
    assert d["dps_basis"] == "mixed" and [r["kind"] for r in d["annual_dps"]] == ["paid"] * 6 + ["declared"]
    assert "paid facts for the periods the declared tag does not cover" in d["dps_basis_detail"] and any("switches basis" in n for n in d["notes"])
    # 5.4.5: the no-interleave rule is for QUARTERLY facts; a fiscal year with no primary FY fact (and no four primary
    # quarters) takes the other tag's FY fact, with its kind, and the basis reads mixed
    dps_fy3 = {"declared": {"2023-10-29": 1.84, "2025-11-02": 2.36}, "paid": {"2024-11-03": 2.105}}
    d = F.build_dividends(annual, [], {"declared": {}, "paid": {}}, dps_fy3, 350.0, "2026-10-14", "prices.json stats.last", _ctx())
    assert d["dps_basis"] == "mixed" and [(r["period_end"], r["kind"]) for r in d["annual_dps"]] == [("2023-10-29", "declared"), ("2024-11-03", "paid"), ("2025-11-02", "declared")]
    assert "paid FY facts for 1 fiscal year(s) inside that span" in d["dps_basis_detail"] and d["growth_years"] == 2
    # a quarterly paid fact inside the declared span is still never interleaved
    d = F.build_dividends(annual, [], {"declared": {}, "paid": {"2024-08-04": _q("2024-08-04", 0.5, 3, "2023-10-30")}}, {"declared": dps_fy3["declared"], "paid": {}},
                          350.0, "2026-10-14", "prices.json stats.last", _ctx())
    assert d["dps_basis"] == "declared" and d["history"] == [] and [r["period_end"] for r in d["annual_dps"]] == ["2023-10-29", "2025-11-02"]


def _s1_fixture():
    """Reviewer scenario S1: the filer stopped tagging the Q4 DPS fact — the prior year's Q4 fact sits inside a 400-day look-back."""
    def row(end, fy, **kw):
        r = {"period_end": end, "fy": fy, "dividends_paid": 100, "buybacks": 50, "share_issuance": 5, "shares_diluted": 1000, "eps_diluted": 2.0, "oe_conservative": 300, "fcf": 300}
        r.update(kw)
        return r
    annual = [row("2024-12-31", "2024"), row("2025-12-31", "2025")]
    qrows = [row(e, "2025", fq=i + 1) for i, e in enumerate(("2025-03-31", "2025-06-30", "2025-09-30", "2025-12-31"))]
    dps_q = {"declared": {"2024-12-31": _q("2024-12-31", 0.30, 4, "2024-01-01", filed="2025-02-01"),
                          "2025-03-31": _q("2025-03-31", 0.35, 1, "2025-01-01"), "2025-06-30": _q("2025-06-30", 0.35, 2, "2025-01-01"), "2025-09-30": _q("2025-09-30", 0.35, 3, "2025-01-01")}, "paid": {}}
    dps_fy = {"declared": {"2024-12-31": 1.20, "2025-12-31": 1.40}, "paid": {}}
    return annual, qrows, dps_q, dps_fy


def test_build_dividends_frequency_window_is_the_fiscal_year_and_the_newer_fy_fact_wins():
    annual, qrows, dps_q, dps_fy = _s1_fixture()
    d = F.build_dividends(annual, qrows, dps_q, dps_fy, 50.0, "2026-10-14", "prices.json stats.last", _ctx(shares_instant=(1000, "2025-12-31", "dei")))
    assert d["frequency"] == "quarterly" and d["frequency_basis"].startswith("3 quarterly DPS facts inside FY2025 (2025-01-01..2025-12-31)"), "the prior year's Q4 fact is outside FY2025"
    assert close(d["dps_ttm"], 1.40) and d["dps_ttm_basis"].startswith("FY2025 DPS (fy_fact, period ended 2025-12-31)"), "the FY fact is newer than the four consecutive quarterly facts"
    assert any("newer than the latest quarterly DPS fact (2025-09-30)" in n for n in d["notes"])
    assert close(d["dividend_yield"], 1.40 / 50.0)
    # control (S2): without the prior-year Q4 fact the result is the same
    dps_q2 = {"declared": {e: v for e, v in dps_q["declared"].items() if e != "2024-12-31"}, "paid": {}}
    d2 = F.build_dividends(annual, qrows, dps_q2, dps_fy, 50.0, "2026-10-14", "prices.json stats.last", _ctx(shares_instant=(1000, "2025-12-31", "dei")))
    assert d2["frequency"] == "quarterly" and close(d2["dps_ttm"], 1.40)
    # four consecutive quarterly facts that run PAST the FY fact still sum (the mid-year initiator test keeps the other direction)
    dps_q3 = {"declared": dict(dps_q2["declared"], **{"2025-12-31": _q("2025-12-31", 0.35, 4, "2025-01-01")}), "paid": {}}
    d3 = F.build_dividends(annual, qrows, dps_q3, dps_fy, 50.0, "2026-10-14", "prices.json stats.last", _ctx(shares_instant=(1000, "2025-12-31", "dei")))
    assert close(d3["dps_ttm"], 1.40) and d3["dps_ttm_basis"].startswith("sum of the four quarterly DPS facts 2025-03-31..2025-12-31")


def test_build_dividends_frequency_spacing_ignores_the_age_of_older_facts():
    # WMT: the full year's dividend is declared in Q1 (0.94 for FY2026, 0.99 for FY2027) with zeros in the other quarters;
    # 2025-04-30 -> 2026-07-31 is 457 days, one over STALE_DAYS, so the old rule saw a single fact and gave frequency null
    annual = [{"fy": e[:4], "period_end": e, "eps_diluted": 2.5, "dividends_paid": 6.7e9, "oe_conservative": 2e10, "fcf": 2e10, "shares_diluted": 8e9} for e in ("2024-01-31", "2025-01-31", "2026-01-31")]
    qrows = [{"period_end": e, "fq": fq, "shares_diluted": 8e9, "dividends_paid": 1.7e9, "buybacks": 1e9, "share_issuance": None}
             for e, fq in (("2025-10-31", 3), ("2026-01-31", 4), ("2026-04-30", 1), ("2026-07-31", 2))]
    q = {}
    for fy_start, pay, ends in (("2023-02-01", 0.76, ("2023-04-30", "2023-07-31", "2023-10-31")), ("2024-02-01", 0.83, ("2024-04-30", "2024-07-31", "2024-10-31")),
                                ("2025-02-01", 0.94, ("2025-04-30", "2025-07-31")), ("2026-02-01", 0.99, ("2026-04-30", "2026-07-31"))):
        for i, e in enumerate(ends):
            q[e] = _q(e, pay if i == 0 else 0, i + 1, fy_start)
    dps_fy = {"declared": {"2024-01-31": 0.76, "2025-01-31": 0.83, "2026-01-31": 0.94}, "paid": {}}
    no_cash = [dict(r, dividends_paid=None) for r in qrows]
    d = F.build_dividends(annual, no_cash, {"declared": q, "paid": {}}, dps_fy, 100.0, "2026-10-14", "prices.json stats.last", _ctx(shares_instant=(8e9, "2026-07-31", "dei")))
    assert d["frequency"] == "annual", "what the per-share facts say: one positive fact a year"
    assert d["frequency_basis"].startswith("spacing of the latest 4 positive quarterly DPS facts (2023-04-30, 2024-04-30, 2025-04-30, 2026-04-30)")
    assert d["frequency_basis"].endswith("quarters filed as zero: 2023-07-31, 2023-10-31, 2024-07-31, 2024-10-31, 2025-07-31, 2026-07-31")
    assert close(d["dps_ttm"], 0.99) and not any("single quarterly DPS fact" in n for n in d["notes"])
    # 5.4.6: with the common cash dividend filed in each of the last four quarters, that is the payment cadence (WMT declares
    # once a year and pays quarterly); the per-share reading is kept in the basis and the zeros are not a suspension
    d = F.build_dividends(annual, qrows, {"declared": q, "paid": {}}, dps_fy, 100.0, "2026-10-14", "prices.json stats.last",
                          _ctx(shares_instant=(8e9, "2026-07-31", "dei"), flow_facts=_div_flow_facts(qrows, "PaymentsOfDividendsCommonStock")))
    assert d["frequency"] == "quarterly" and d["frequency_basis"].startswith("cash dividends paid are filed for 4 of the last four quarters")
    assert "the per-share facts read annual (spacing of the latest 4 positive quarterly DPS facts" in d["frequency_basis"] and "declaration cadence" in d["frequency_basis"]
    assert not any("suspended" in n for n in d["notes"])
    # a reinstated payer with ONE fact after a long gap: the run stops at the suspension, the single new fact is not inferable yet
    q2 = {e: _q(e, 0.5, i + 1, "2018-12-01") for i, e in enumerate(("2019-02-28", "2019-05-31", "2019-08-31", "2019-11-30"))}
    q2["2026-08-31"] = _q("2026-08-31", 0.15, 3, "2025-12-01")
    annual2 = [{"fy": str(y), "period_end": f"{y}-11-30", "eps_diluted": 1.0, "dividends_paid": None, "oe_conservative": 1e9, "fcf": 1e9, "shares_diluted": 1.3e9} for y in range(2019, 2026)]
    qrows2 = [{"period_end": e, "shares_diluted": 1.3e9, "dividends_paid": None, "buybacks": None, "share_issuance": None} for e in ("2025-11-30", "2026-02-28", "2026-05-31", "2026-08-31")]
    d = F.build_dividends(annual2, qrows2, {"declared": q2, "paid": {}}, {"declared": {}, "paid": {}}, 25.0, "2026-10-14", "prices.json stats.last", _ctx())
    assert d["frequency"] is None and any("a single quarterly DPS fact so far (2026-08-31)" in n for n in d["notes"])
    # the latest positive fact itself stale -> still "suspended / irregular"
    q3 = {e: _q(e, 0.5, i + 1, "2018-12-01") for i, e in enumerate(("2019-02-28", "2019-05-31", "2019-08-31", "2019-11-30"))}
    d = F.build_dividends(annual2, qrows2, {"declared": q3, "paid": {}}, {"declared": {}, "paid": {}}, 25.0, "2026-10-14", "prices.json stats.last", _ctx())
    assert d["frequency"] == "irregular" and any("dividend suspended; shown as irregular" in n for n in d["notes"])


def test_build_dividends_partial_leg_uses_the_filed_year_to_date_fact():
    # CCL: Q1 FY2026 repurchases untagged (so Q2 = 6M - Q1 cannot be derived), Q3 derived = 548M; the six-month (381M) and
    # nine-month (929M, 10-Q filed 2026-09-29) YTD facts are filed; Q4 FY2025 has no fact at all
    annual = [{"fy": str(y), "period_end": f"{y}-11-30", "eps_diluted": 1.0, "dividends_paid": None, "buybacks": None, "oe_conservative": 1e9, "fcf": 1e9, "shares_diluted": 1.3e9} for y in (2024, 2025)]
    qrows = [{"period_end": e, "fq": fq, "shares_diluted": 1.3e9, "dividends_paid": dv, "buybacks": bb, "share_issuance": None}
             for e, fq, dv, bb in (("2025-11-30", 4, None, None), ("2026-02-28", 1, 208e6, None), ("2026-05-31", 2, 206e6, None), ("2026-08-31", 3, 204e6, 548e6))]
    bb_tag, dv_tag = "PaymentsForRepurchaseOfCommonStock", "PaymentsOfDividends"
    flow_facts = {"buybacks": {("2024-12-01", "2025-08-31"): (0, bb_tag, "USD", "2026-09-29", "B"), ("2025-12-01", "2026-05-31"): (381e6, bb_tag, "USD", "2026-06-26", "A"),
                               ("2025-12-01", "2026-08-31"): (929e6, bb_tag, "USD", "2026-09-29", "B")},
                  "dividends_paid": {("2025-12-01", "2026-08-31"): (618e6, dv_tag, "USD", "2026-09-29", "B")}, "share_issuance": {}}
    ctx = _ctx(flow_facts=flow_facts, shares_instant=(1344610129, "2026-08-31", "dei:EntityCommonStockSharesOutstanding (10-Q filed 2026-09-29)"))
    d = F.build_dividends(annual, qrows, {"declared": {}, "paid": {}}, {"declared": {}, "paid": {}}, 25.97, "2026-10-14", "prices.json stats.last", ctx)
    mc = 25.97 * 1344610129
    assert d["legs"]["buybacks"]["value"] == 929e6 and not d["legs"]["buybacks"]["complete"] and d["buybacks_ttm"] is None
    assert d["legs"]["buybacks"]["basis"].startswith("3/4 quarters covered (the nine-month year-to-date fact 2025-12-01..2026-08-31 = 929.0M (PaymentsForRepurchaseOfCommonStock, filed 2026-09-29)) — a lower bound")
    assert close(d["buyback_yield"], 929e6 / mc) and d["yield_basis"]["buyback_yield"]["bound"] == "lower", "2.66%, not 1.57% from the single derived quarter"
    assert any(n.startswith("buybacks_ttm: not all of the last four quarters have a filed buybacks figure (missing 2025-11-30)") and "covers 3 of them" in n for n in d["notes"])
    assert d["legs"]["dividends_paid"]["value"] == 618e6 and d["legs"]["dividends_paid"]["basis"].startswith("3/4 quarters covered")
    assert close(d["shareholder_yield"], (618e6 + 929e6) / mc) and d["yield_basis"]["shareholder_yield"]["bound"] == "indeterminate"
    assert d["yields_display"]["buyback_yield"]["label"] == "≥ 2.66%" and d["yields_display"]["buyback_yield"]["note"].startswith("buybacks: 3/4 quarters covered")
    # a full-year fact plus the first quarter's row covers all four window quarters of one fiscal year: exact, and the strict TTM is filled
    qrows = [{"period_end": e, "fq": i + 1, "shares_diluted": 1e9, "dividends_paid": 1e8, "buybacks": [100e6, None, None, None][i], "share_issuance": 0}
             for i, e in enumerate(("2025-03-31", "2025-06-30", "2025-09-30", "2025-12-31"))]
    ff = {"buybacks": {("2025-01-01", "2025-12-31"): (1000e6, bb_tag, "USD", "2026-02-20", "K")}, "dividends_paid": {}, "share_issuance": {}}
    d = F.build_dividends([{"fy": "2025", "period_end": "2025-12-31", "eps_diluted": 1.0, "dividends_paid": 4e8, "oe_conservative": 1e9, "fcf": 1e9, "shares_diluted": 1e9}],
                          qrows, {"declared": {}, "paid": {}}, {"declared": {}, "paid": {}}, 10.0, "2026-10-14", "prices.json stats.last", _ctx(flow_facts=ff, shares_instant=(1e9, "2025-12-31", "dei")))
    assert d["buybacks_ttm"] == 1000e6 and d["legs"]["buybacks"] == {"value": 1000e6, "basis": "4/4 quarters covered: the full-year year-to-date fact 2025-01-01..2025-12-31 = 1.00B (PaymentsForRepurchaseOfCommonStock, filed 2026-02-20)", "complete": True}
    assert d["yield_basis"]["buyback_yield"]["bound"] == "exact" and close(d["buyback_yield"], 0.1)
    # a year-to-date fact that starts before the window (the prior fiscal year's nine months) covers nothing: ytd_cover is None
    last4 = [{"period_end": e, "fq": fq} for e, fq in (("2025-09-30", 3), ("2025-12-31", 4), ("2026-03-31", 1), ("2026-06-30", 2))]
    assert F.ytd_cover(last4, {("2025-01-01", "2025-09-30"): (5e8, bb_tag, "USD", "2025-10-30", "Q")}) is None
    assert F.ytd_cover(last4, {("2026-01-01", "2026-06-30"): (3e8, bb_tag, "USD", "2026-07-30", "Q")})[:2] == (3e8, ["2026-03-31", "2026-06-30"])
    assert F.ytd_cover(last4, {("2026-04-01", "2026-06-30"): (1e8, bb_tag, "USD", "2026-07-30", "Q")}) is None, "a single quarter adds nothing the row does not carry"


def test_yields_display_carries_the_bound():
    annual, qrows, dps_q, dps_fy = _fixture()
    d = F.build_dividends(annual, qrows, dps_q, dps_fy, 15.10, "2026-10-14", "prices.json stats.last", _ctx())
    yd = d["yields_display"]
    assert yd["buyback_yield"]["bound"] == "exact" and yd["buyback_yield"]["prefix"] == "" and yd["buyback_yield"]["label"] == f"{d['buyback_yield'] * 100:.2f}%" and yd["buyback_yield"]["note"] is None
    assert yd["dividend_yield"]["label"] == f"{0.62 / 15.10 * 100:.2f}%" and yd["dividend_yield"]["note"] == d["dps_ttm_basis"]
    for r in qrows[:-1]:
        r["buybacks"] = None
    for r in qrows:
        r["share_issuance"] = None
    d = F.build_dividends(annual, qrows, dps_q, dps_fy, 15.10, "2026-10-14", "prices.json stats.last", _ctx())
    yd = d["yields_display"]
    assert yd["buyback_yield"]["prefix"] == "≥" and yd["buyback_yield"]["label"] == f"≥ {d['buyback_yield'] * 100:.2f}%" and yd["buyback_yield"]["note"].startswith("buybacks: 1/4 quarters filed (2026-03-31)")
    assert yd["net_buyback_yield"]["label"].startswith("≈ ") and yd["net_buyback_yield"]["label"].endswith("% (incomplete)") and "share_issuance: not filed for any of the four quarters" in yd["net_buyback_yield"]["note"]
    assert yd["shareholder_yield"]["bound"] == "indeterminate" and yd["shareholder_yield"]["label"].startswith("≈ ")
    d = F.build_dividends(annual, qrows, dps_q, dps_fy, None, None, None, _ctx())
    assert all(v["label"] == "—" and v["value"] is None and v["bound"] is None for v in d["yields_display"].values())
    assert "not filed for the window" not in (d["yields_display"]["buyback_yield"]["note"] or ""), "no price -> no market cap; the leg itself is filed"


# ---------------- 5.4.5 re-verification fixes ----------------
def _cci_fixture():
    """CCI: the FY2025 10-K (filed 2026-02-23) tags PaymentsOfDividendsCommonStock −2,080,000,000 and
    PaymentsForRepurchaseOfCommonStock −23,000,000; every 10-Q year-to-date fact is positive (9M 1,615M / 23M)."""
    dv, bb = "PaymentsOfDividendsCommonStock", "PaymentsForRepurchaseOfCommonStock"
    annual = [{"fy": "2025", "period_end": "2025-12-31", "eps_diluted": 1.01, "dividends_paid": -2080e6, "buybacks": -23e6, "share_issuance": None,
               "oe_conservative": 2802e6, "fcf": 2875e6, "shares_diluted": 435e6}]
    qrows = [{"period_end": e, "fq": fq, "shares_diluted": 435e6, "dividends_paid": d, "dividends_paid_derived": der, "buybacks": b, "share_issuance": None}
             for e, fq, d, der, b in (("2025-09-30", 3, 462e6, True, 0), ("2025-12-31", 4, -3695e6, True, -46e6),
                                      ("2026-03-31", 1, 473e6, False, 25e6), ("2026-06-30", 2, 459e6, True, 992e6))]

    def ff(tag, vals):
        return {k: (v, tag, "USD", f, "A") for k, (v, f) in vals.items()}
    flow_facts = {"dividends_paid": ff(dv, {("2025-01-01", "2025-06-30"): (1153e6, "2025-08-06"), ("2025-01-01", "2025-09-30"): (1615e6, "2025-11-06"),
                                            ("2025-01-01", "2025-12-31"): (-2080e6, "2026-02-23"), ("2026-01-01", "2026-03-31"): (473e6, "2026-05-07"),
                                            ("2026-01-01", "2026-06-30"): (932e6, "2026-08-05")}),
                  "buybacks": ff(bb, {("2025-01-01", "2025-06-30"): (23e6, "2025-08-06"), ("2025-01-01", "2025-09-30"): (23e6, "2025-11-06"),
                                      ("2025-01-01", "2025-12-31"): (-23e6, "2026-02-23"), ("2026-01-01", "2026-03-31"): (25e6, "2026-05-07"),
                                      ("2026-01-01", "2026-06-30"): (1017e6, "2026-08-05")}),
                  "share_issuance": {}}
    return annual, qrows, flow_facts


def test_build_dividends_negative_flow_leg_is_a_sign_error_not_a_negative_payment():
    annual, qrows, flow_facts = _cci_fixture()
    ctx = _ctx(flow_facts=flow_facts, shares_instant=(435.5e6, "2026-06-30", "dei"))
    d = F.build_dividends(annual, qrows, {"declared": {}, "paid": {}}, {"declared": {"2024-12-31": 6.26, "2025-12-31": 4.75}, "paid": {}}, 85.0, "2026-10-14", "prices.json stats.last", ctx)
    # Q4 2025 = |−2,080M| − 1,615M = 465M (the row read −3,695M); buybacks Q4 = |−23M| − 23M = 0
    assert close(d["dividends_paid_ttm"], 462e6 + 465e6 + 473e6 + 459e6) and close(d["buybacks_ttm"], 0 + 0 + 25e6 + 992e6)
    assert d["legs"]["dividends_paid"]["complete"] and "2025-12-31" in d["legs"]["dividends_paid"]["sign_corrected"][0] and "|-2,080,000,000| − |1,615,000,000| = 465,000,000 used" in d["legs"]["dividends_paid"]["sign_corrected"][0]
    mc = 85.0 * 435.5e6
    assert close(d["shareholder_yield"], (1859e6 + 1017e6) / mc) and d["shareholder_yield"] > 0
    yb = d["yield_basis"]["shareholder_yield"]
    assert set(yb["sign_corrected"]) == {"dividends_paid", "buybacks"} and "sign-convention error" in yb["sign_corrected"]["dividends_paid"]
    assert "filed below zero" in d["yields_display"]["shareholder_yield"]["note"]
    assert close(d["payout_ratio_oe"], 2080e6 / 2802e6) and close(d["payout_ratio_fcf"], 2080e6 / 2875e6), "the FY fact read as its absolute amount, never a negative payout"
    assert any(n.startswith("sign convention (dividends_paid)") and "FY2025 (period ended 2025-12-31) filed as -2.08B, read as 2.08B" in n for n in d["notes"])
    # the pure helpers: a negative numerator is never a payout; a direct row below zero is read as its absolute amount,
    # a derived row with no facts to rebuild it from is left out (a missing quarter, not a guess)
    assert F.payout_ratio(-1.0, 2.0) is None
    qv, av, fixes = F.sign_fixed_flows([], [{"period_end": "2026-03-31", "dividends_paid": -5e6}, {"period_end": "2026-06-30", "dividends_paid": -9e6, "dividends_paid_derived": True}])
    assert qv["dividends_paid"] == {"2026-03-31": 5e6, "2026-06-30": None} and len(fixes["dividends_paid"]) == 2


def test_build_dividends_takes_the_other_tags_fy_fact_where_the_primary_has_none():
    # NVDA-shaped: declared FY facts for FY2015, FY2016 (one quarter's rate tagged FY: below its own quarters) and FY2021-FY2022;
    # CashPaid FY facts for every year FY2015-FY2021
    annual = [{"fy": str(y), "period_end": f"{y}-12-31", "eps_diluted": 2.0, "dividends_paid": 4e8, "oe_conservative": 2e9, "fcf": 2e9, "shares_diluted": 6e8} for y in range(2015, 2023)]
    decl_q = {e: _q(e, v, fq, fs) for e, v, fq, fs in (("2016-03-31", 0.1, 1, "2016-01-01"), ("2016-06-30", 0.1, 2, "2016-01-01"), ("2016-09-30", 0.1, 3, "2016-01-01"),
                                                        ("2022-03-31", 0.16, 1, "2022-01-01"), ("2022-06-30", 0.16, 2, "2022-01-01"), ("2022-09-30", 0.16, 3, "2022-01-01"))}
    dps_fy = {"declared": {"2015-12-31": 0.38, "2016-12-31": 0.1, "2021-12-31": 0.64, "2022-12-31": 0.64},
              "paid": {"2015-12-31": 0.37, "2016-12-31": 0.395, "2017-12-31": 0.485, "2018-12-31": 0.57, "2019-12-31": 0.61, "2020-12-31": 0.64, "2021-12-31": 0.64}}
    d = F.build_dividends(annual, [], {"declared": decl_q, "paid": {}}, dps_fy, 100.0, "2026-10-14", "prices.json stats.last", _ctx())
    rows = [(r["fy"], r["dps"], r["kind"]) for r in d["annual_dps"]]
    assert rows == [("2015", 0.38, "declared"), ("2016", 0.395, "paid"), ("2017", 0.485, "paid"), ("2018", 0.57, "paid"), ("2019", 0.61, "paid"),
                    ("2020", 0.64, "paid"), ("2021", 0.64, "declared"), ("2022", 0.64, "declared")]
    assert d["dps_basis"] == "mixed" and "paid FY facts for 5 fiscal year(s) inside that span" in d["dps_basis_detail"]
    assert any("FY DPS fact for the period ended 2016-12-31 (0.1) is below the sum of the same tag's quarterly facts" in n for n in d["notes"])
    assert close(d["dps_cagr_5y"], (0.64 / 0.485) ** 0.2 - 1) and d["last_cut_fy"] is None, "no five-year hole, no phantom FY2016 cut"


def test_dps_fy_facts_prefers_the_value_consistent_with_the_years_quarters_over_a_repeated_slip():
    # CCI: FY2014 CommonStockDividendsPerShareDeclared 1.87 (10-K 2015-02-19), 1870 (10-Ks 2016-02-22 and 2017-02-22);
    # the 2014 10-Qs file 0.35 for each of Q1-Q3; FY2015 3.35, FY2016 3.61
    tag = "CommonStockDividendsPerShareDeclared"

    def f(start, end, val, filed, form="10-K", fp="FY"):
        return ("us-gaap", tag, "USD/shares", _e(start, end, val, filed, filed, form, fp, int(end[:4])))
    base = [f("2014-01-01", "2014-12-31", 1.87, "2015-02-19"), f("2014-01-01", "2014-12-31", 1870, "2016-02-22"), f("2014-01-01", "2014-12-31", 1870, "2017-02-22"),
            f("2015-01-01", "2015-12-31", 3.35, "2016-02-22"), f("2016-01-01", "2016-12-31", 3.61, "2017-02-22")]
    quarters = [f("2014-01-01", "2014-03-31", 0.35, "2014-05-06", "10-Q", "Q1"), f("2014-04-01", "2014-06-30", 0.35, "2014-08-08", "10-Q", "Q2"),
                f("2014-07-01", "2014-09-30", 0.35, "2014-11-07", "10-Q", "Q3")]
    vals, _, filed, notes = F.dps_fy_facts(_facts(base + quarters), F.DUR["dps_declared"])
    assert vals["2014-12-31"] == 1.87 and filed["2014-12-31"] == "2015-02-19"
    assert len(notes) == 1 and "that year's 3 quarterly facts (sum 1.05)" in notes[0] and "repeated in later comparatives" in notes[0]
    vals, _, _, notes = F.dps_fy_facts(_facts(base), F.DUR["dps_declared"])
    assert vals["2014-12-31"] == 1.87 and "the tag's other fiscal years" in notes[0], "the neighbouring years alone decide the same way"
    # the series edge: a first / last dividend year ≥100x its corroborated neighbour is flagged; a real 16x cut is not
    assert F.dps_outliers(_annual((2014, 1870), (2015, 3.35), (2016, 3.61))) == ["2014"]
    assert F.dps_outliers(_annual((2008, 0.6625), (2009, 0.04), (2010, 0.04))) == [], "HBAN's FY2008 → FY2009 cut is real"


def test_build_dividends_cash_payer_without_per_share_tags_is_not_suspended():
    # HSY: CommonStockDividendsPerShareCashPaid only for 2008-06-29..2010-04-04, PaymentsOfDividendsCommonStock every quarter since
    annual = [{"fy": str(y), "period_end": f"{y}-12-31", "eps_diluted": 5.0, "dividends_paid": 1.0e9 + y, "oe_conservative": 2e9, "fcf": 2e9, "shares_diluted": 2e8} for y in range(2020, 2026)]
    qrows = [{"period_end": e, "shares_diluted": 2e8, "dividends_paid": v, "buybacks": 1e8, "share_issuance": 1e7}
             for e, v in (("2025-09-28", 271130000), ("2025-12-31", 271341000), ("2026-03-29", 287997000), ("2026-06-28", 286395000))]
    dq = {e: _q(e, v, fq, fs) for e, v, fq, fs in (("2009-07-05", 0.2975, 2, "2009-01-01"), ("2009-10-04", 0.2975, 3, "2009-01-01"), ("2010-04-04", 0.32, 1, "2010-01-01"))}
    ctx = _ctx(flow_facts=_div_flow_facts(qrows, "PaymentsOfDividendsCommonStock"))
    d = F.build_dividends(annual, qrows, {"declared": {}, "paid": dq}, {"declared": {}, "paid": {}}, 200.0, "2026-10-14", "prices.json stats.last", ctx)
    assert d["frequency"] == "quarterly" and d["frequency_basis"].startswith("cash dividends paid are filed for 4 of the last four quarters (2025-09-28: 271.1M")
    assert not any("suspended" in n for n in d["notes"]) and any("not tagged since 2010-04-04" in n and "not a suspension" in n for n in d["notes"])
    assert d["dps_ttm"] is None and close(d["dividends_paid_ttm"], 1116863000)
    # STAG-shaped: Q1-Q3 per-share facts every year, no Q4 / FY fact since FY2019, cash dividends every year -> not "suspended / reinstated"
    dq2 = {f"{y}-{md}": _q(f"{y}-{md}", 0.36, i + 1, f"{y}-01-01") for y in range(2020, 2026) for i, md in enumerate(("03-31", "06-30", "09-30"))}
    d = F.build_dividends(annual, qrows, {"declared": dq2, "paid": {}}, {"declared": {"2019-12-31": 1.43}, "paid": {}}, 35.0, "2026-10-14", "prices.json stats.last", ctx)
    assert d["dps_ttm"] is None and not any("suspended" in n for n in d["notes"])
    assert any("tagged for some quarters only, not a suspension" in n for n in d["notes"]) and d["frequency"] == "quarterly"


def test_primary_dps_basis_does_not_flip_on_one_extra_paid_fact():
    # reviewer scenario S-A: both tags quarterly through Q3 2025 and FY facts for 2023/2024 (declared 1.6/1.8, paid 1.5/1.9)
    annual = [{"fy": str(y), "period_end": f"{y}-12-31", "eps_diluted": 3.0, "dividends_paid": 1e8, "oe_conservative": 5e8, "fcf": 5e8, "shares_diluted": 1e8} for y in (2023, 2024)]
    q3 = {e: _q(e, 0.5, i + 1, "2025-01-01") for i, e in enumerate(("2025-03-31", "2025-06-30", "2025-09-30"))}
    paid_q = dict(q3, **{"2024-12-31": _q("2024-12-31", 0.5, 4, "2024-01-01")})
    dps_fy = {"declared": {"2023-12-31": 1.6, "2024-12-31": 1.8}, "paid": {"2023-12-31": 1.5, "2024-12-31": 1.9}}
    out = []
    for extra in (False, True):
        pq = dict(paid_q, **({"2025-12-31": _q("2025-12-31", 0.5, 4, "2025-01-01")} if extra else {}))
        d = F.build_dividends(annual, [], {"declared": dict(q3), "paid": pq}, dps_fy, 40.0, "2026-10-14", "prices.json stats.last", _ctx())
        out.append(d)
        assert d["dps_basis_detail"].startswith("declared facts") and "both tags file quarterly facts in the last 8 quarters" in d["dps_basis_detail"]
        assert [(r["fy"], r["dps"]) for r in d["annual_dps"]][:2] == [("2023", 1.6), ("2024", 1.8)], "the history keeps its basis"
    assert out[0]["dps_basis"] == "declared" and out[1]["dps_basis"] == "mixed", "the extra paid quarter only extends the series past the declared span"
    # AVGO-shaped (declared stopped years ago) still reads paid
    assert F.choose_dps_basis({"declared": {}, "paid": paid_q}, {"declared": {"2019-11-03": 1.06}, "paid": {"2024-12-31": 1.9}})[0] == "paid"
    assert F.choose_dps_basis({"declared": q3, "paid": {}}, {"declared": {}, "paid": {}}) == ("declared", None)
    # the per-share facts are quarterly totals: a quarterly result says it is the filing cadence, not a monthly payer's payment cadence
    annual2, qrows2, dps_q2, dps_fy2 = _fixture()
    d = F.build_dividends(annual2, qrows2, dps_q2, dps_fy2, 15.10, "2026-10-14", "prices.json stats.last", _ctx())
    assert d["frequency"] == "quarterly" and d["frequency_basis"].endswith("a payment cadence inside the quarter (a monthly payer) is not tagged")


def test_yields_display_note_says_what_each_leg_does_to_the_yield():
    annual, qrows, _, _ = _fixture()
    for r in list(annual) + qrows:
        r["dividends_paid"] = None
    qrows[0]["share_issuance"] = qrows[1]["share_issuance"] = None
    ctx = _ctx(filed_any={"dividends_paid": False, "buybacks": True, "share_issuance": True}, shares_instant=(335291000, "2026-06-30", "us-gaap"))
    d = F.build_dividends(annual, qrows, {"declared": {}, "paid": {}}, {"declared": {}, "paid": {}}, 262.19, "2026-10-14", "prices.json stats.last", ctx)
    yd = d["yields_display"]["net_buyback_yield"]
    assert yd["label"].startswith("≤ ") and "the deduction is understated, so this yield is an upper bound" in yd["note"] and "a lower bound" not in yd["note"]
    for r in qrows[:-1]:
        r["buybacks"] = None
    d = F.build_dividends(annual, qrows, {"declared": {}, "paid": {}}, {"declared": {}, "paid": {}}, 262.19, "2026-10-14", "prices.json stats.last", ctx)
    assert "buybacks: 1/4 quarters filed (2026-03-31) — understated, so this yield is a lower bound" in d["yields_display"]["buyback_yield"]["note"]


def test_dividends_inputs_applies_a_split_evidenced_only_by_re_filed_values_to_the_quarters():
    # EXPE: the December 2011 1-for-2 reverse split has no ratio fact; the 10-K filed 2012-02-10 re-files FY2010 DPS 0.28 -> 0.56
    # and FY2009's diluted count 290M -> 145M; the 2010 quarterly facts were last filed in 2010/2011 at 0.07
    g, dps = "us-gaap", "CommonStockDividendsPerShareDeclared"

    def f(start, end, val, filed, form="10-Q", fp="Q1"):
        return (g, dps, "USD/shares", _e(start, end, val, filed, filed, form, fp, int(end[:4])))
    facts = _facts([
        f("2010-01-01", "2010-03-31", 0.07, "2010-04-30"), f("2010-04-01", "2010-06-30", 0.07, "2010-07-30", fp="Q2"),
        f("2010-01-01", "2010-12-31", 0.28, "2011-02-11", "10-K", "FY"), f("2010-01-01", "2010-12-31", 0.56, "2012-02-10", "10-K", "FY"),
        f("2011-01-01", "2011-03-31", 0.14, "2012-04-27"), f("2011-01-01", "2011-12-31", 0.56, "2012-02-10", "10-K", "FY"),
        (g, "WeightedAverageNumberOfDilutedSharesOutstanding", "shares", _e("2009-01-01", "2009-12-31", 290e6, "2010-02-12", "a", "10-K", "FY")),
        (g, "WeightedAverageNumberOfDilutedSharesOutstanding", "shares", _e("2009-01-01", "2009-12-31", 145e6, "2012-02-10", "b", "10-K", "FY")),
    ])
    dps_q, dps_fy, meta = F.dividends_inputs(facts)
    assert len(meta["splits"]) == 1 and meta["splits"][0][0] == "2012-02-10" and close(meta["splits"][0][1], 0.5) and meta["splits"][0][3] == "re_filed_counts"
    assert close(dps_q["declared"]["2010-03-31"]["val"], 0.14) and close(dps_q["declared"]["2010-06-30"]["val"], 0.14), "the 2010 quarters join the post-split basis"
    assert dps_q["declared"]["2011-03-31"]["val"] == 0.14 and dps_fy["declared"] == {"2010-12-31": 0.56, "2011-12-31": 0.56}
    assert any("no ratio fact filed" in n and "1-for-2 reverse split" in n for n in meta["split_notes"])
    d = F.build_dividends([], [], dps_q, dps_fy, 100.0, "2026-10-14", "prices.json stats.last", _ctx(splits=meta["splits"]))
    assert d["split_adjustments"][0]["source"] == "re_filed_counts" and d["split_adjustments"][0]["first_post_split_filing"] == "2012-02-10"


# ---------------- 5.4.6 second re-verification fixes ----------------
def _asof(dps_q, dps_fy, asof):
    """The DPS inputs as a run on `asof` sees them: facts for periods ending on or before it."""
    return ({b: {e: d for e, d in v.items() if e <= asof} for b, v in dps_q.items()},
            {b: {e: x for e, x in v.items() if e <= asof} for b, v in dps_fy.items()})


def test_primary_dps_basis_is_the_same_at_every_filing_date():
    runs = ("2025-12-31", "2026-03-31", "2026-06-30", "2026-09-30")
    annual = [{"fy": str(y), "period_end": f"{y}-12-31", "eps_diluted": 3.0, "dividends_paid": 1e8, "oe_conservative": 5e8, "fcf": 5e8, "shares_diluted": 1e8} for y in (2022, 2023, 2024, 2025)]
    # ZTS: Declared filed for Q1-Q3 only (10-Qs), CashPaid only as FY facts (10-K) — the 5.4.5 coverage rule read
    # declared at 2025-12-15, paid at 2026-03-15 and declared again at 2026-06-15
    rate = {2022: 0.325, 2023: 0.375, 2024: 0.432, 2025: 0.5, 2026: 0.53}
    decl = {f"{y}-{md}": _q(f"{y}-{md}", rate[y] if md != "09-30" else 0.0, i + 1, f"{y}-01-01") for y in rate for i, md in enumerate(("03-31", "06-30", "09-30"))}
    paid_fy = {"2022-12-31": 1.3, "2023-12-31": 1.5, "2024-12-31": 1.796, "2025-12-31": 2.03}
    seen = set()
    for asof in runs:
        dq, dfy = _asof({"declared": decl, "paid": {}}, {"declared": {}, "paid": paid_fy}, asof)
        b, rule = F.choose_dps_basis(dq, dfy)
        d = F.build_dividends(annual, [], dq, dfy, 75.0, "2026-10-14", "prices.json stats.last", _ctx())
        seen.add((b, tuple((r["fy"], r["dps"], r["kind"]) for r in d["annual_dps"] if r["period_end"] <= "2024-12-31")))
        assert b == "declared" and "the declared tag files quarterly facts" in rule
    assert len(seen) == 1, "one basis and one history at every run date"
    # the mirror image (reviewer rv/flip.py): Declared FY-only, CashPaid Q1-Q3 + FY — paid at every run date, annual series unchanged
    dfy_all = {"2022-12-31": 1.6, "2023-12-31": 1.8, "2024-12-31": 2.0, "2025-12-31": 2.2}
    pfy_all = {"2022-12-31": 1.55, "2023-12-31": 1.75, "2024-12-31": 1.95, "2025-12-31": 2.15}
    prate = {2022: 0.4, 2023: 0.45, 2024: 0.5, 2025: 0.55, 2026: 0.6}
    pq = {f"{y}-{md}": _q(f"{y}-{md}", prate[y], i + 1, f"{y}-01-01") for y in prate for i, md in enumerate(("03-31", "06-30", "09-30"))}
    out = set()
    for asof in runs:
        dq, dfy = _asof({"declared": {}, "paid": pq}, {"declared": dfy_all, "paid": pfy_all}, asof)
        d = F.build_dividends(annual, [], dq, dfy, 40.0, "2026-10-14", "prices.json stats.last", _ctx())
        out.add((d["dps_basis"], tuple((r["fy"], r["dps"]) for r in d["annual_dps"]), round(d["dps_cagr_3y"], 12)))
    assert out == {("paid", (("2022", 1.55), ("2023", 1.75), ("2024", 1.95), ("2025", 2.15)), round((2.15 / 1.55) ** (1 / 3) - 1, 12))}
    # ATO: both tags quarterly (CashPaid until early 2025, Declared since) — declared at every run once both exist
    both_q = {"declared": {e: _q(e, 1.0, fq, fs) for e, fq, fs in (("2025-03-31", 2, "2024-10-01"), ("2025-06-30", 3, "2024-10-01"), ("2025-12-31", 1, "2025-10-01"),
                                                                    ("2026-03-31", 2, "2025-10-01"), ("2026-06-30", 3, "2025-10-01"))},
              "paid": {e: _q(e, 0.87, fq, fs) for e, fq, fs in (("2024-03-31", 2, "2023-10-01"), ("2024-06-30", 3, "2023-10-01"), ("2024-12-31", 1, "2024-10-01"))}}
    fy = {"declared": {}, "paid": {"2024-09-30": 3.22, "2025-09-30": 3.48}}
    assert {F.choose_dps_basis(*_asof(both_q, fy, a))[0] for a in ("2025-06-30", "2025-09-30", "2025-12-31", "2026-03-31", "2026-06-30")} == {"declared"}
    # reviewer edge3: declared covers 2023-12-31..2025-06-30, paid 2024-03-31..2025-09-30; one more paid fact does not flip the basis
    dq3 = {e: _q(e, 0.5, 1, e[:4] + "-01-01") for e in ("2023-12-31", "2024-03-31", "2024-06-30", "2024-09-30", "2024-12-31", "2025-03-31", "2025-06-30")}
    pq3 = {e: _q(e, 0.5, 1, e[:4] + "-01-01") for e in ("2024-03-31", "2024-06-30", "2024-09-30", "2024-12-31", "2025-03-31", "2025-06-30", "2025-09-30")}
    for extra in ({}, {"2025-12-31": _q("2025-12-31", 0.5, 4, "2025-01-01")}):
        assert F.choose_dps_basis({"declared": dq3, "paid": dict(pq3, **extra)}, {"declared": {}, "paid": {}})[0] == "declared"
    # AVGO: the declared tag stopped years ago -> paid
    assert F.choose_dps_basis({"declared": {"2020-08-02": _q("2020-08-02", 3.25, 3, "2019-11-04")}, "paid": pq3}, {"declared": {}, "paid": {}})[0] == "paid"


def test_build_dividends_frequency_needs_the_fy_total_and_the_quarters_from_one_tag():
    # ZTS: Declared Q1 0.5, Q2 0.5, Q3 filed as 0 (no Q4); CashPaid FY2025 2.03. The FY-count rule compared the paid total with
    # the declared quarters and read "irregular"; the spacing reads quarterly, and the TTM roll-forward names the mixed basis
    annual = [{"fy": str(y), "period_end": f"{y}-12-31", "eps_diluted": 5.0, "dividends_paid": 9e8, "oe_conservative": 2e9, "fcf": 2e9, "shares_diluted": 4.4e8} for y in (2024, 2025)]
    decl = {e: _q(e, v, fq, e[:4] + "-01-01") for e, v, fq in (("2024-03-31", 0.432, 1), ("2024-06-30", 0.432, 2), ("2024-09-30", 0, 3), ("2025-03-31", 0.5, 1),
                                                               ("2025-06-30", 0.5, 2), ("2025-09-30", 0, 3), ("2026-03-31", 0.53, 1), ("2026-06-30", 0.53, 2))}
    d = F.build_dividends(annual, [], {"declared": decl, "paid": {}}, {"declared": {}, "paid": {"2024-12-31": 1.796, "2025-12-31": 2.03}}, 75.0, "2026-10-14", "prices.json stats.last", _ctx())
    assert d["dps_basis"] == "mixed" and [(r["fy"], r["kind"]) for r in d["annual_dps"]] == [("2024", "paid"), ("2025", "paid")]
    assert d["frequency"] == "quarterly" and d["frequency_basis"].startswith("spacing of the latest 4 positive quarterly DPS facts")
    assert any("the FY2025 total is a paid fact and the quarterly facts inside that year are declared facts" in n for n in d["notes"])
    assert close(d["dps_ttm"], 2.03 + 1.06 - 1.0) and "mixed basis: the full-year total is a paid fact and the quarters are declared facts" in d["dps_ttm_basis"]
    # IRM: four quarterly facts 0.785 x3 + 0.864 = 3.219 against the rounded FY fact 3.22 — rounding, not a fifth payment
    assert F.infer_frequency(4, 3.22, 3.219, True, True, min_quarterly=0.785) == "quarterly"
    assert not F.fy_remainder_is_a_payment(3.22, 3.219, 0.785) and F.fy_remainder_is_a_payment(0.62, 0.465, 0.155)
    irm = {e: _q(e, v, fq, "2025-01-01") for e, v, fq in (("2025-03-31", 0.785, 1), ("2025-06-30", 0.785, 2), ("2025-09-30", 0.785, 3), ("2025-12-31", 0.864, 4))}
    irm["2026-03-31"] = _q("2026-03-31", 0.864, 1, "2026-01-01")
    d = F.build_dividends(annual, [], {"declared": irm, "paid": {}}, {"declared": {"2025-12-31": 3.22}, "paid": {}}, 100.0, "2026-10-14", "prices.json stats.last", _ctx())
    assert d["frequency"] == "quarterly" and d["frequency_basis"].startswith("spacing")


def _cash_rows(vals, ends=("2025-09-30", "2025-12-31", "2026-03-31", "2026-06-30")):
    return [{"period_end": e, "fq": None, "shares_diluted": 4.57e8, "dividends_paid": v, "buybacks": 0, "share_issuance": 0} for e, v in zip(ends, vals)]


def test_build_dividends_quarterly_cash_payer_with_a_declaration_cadence():
    # GEHC: 0.035 declared in Q1, none in Q2, two (0.07) in Q3; FY2025 0.14 — the FY count read "irregular", the spacing "semiannual"
    annual = [{"fy": str(y), "period_end": f"{y}-12-31", "eps_diluted": 4.0, "dividends_paid": 6.4e7, "oe_conservative": 2e9, "fcf": 2e9, "shares_diluted": 4.57e8} for y in (2024, 2025)]
    q = {e: _q(e, v, fq, e[:4] + "-01-01") for e, v, fq in (("2024-09-30", 0.06, 3), ("2025-03-31", 0.035, 1), ("2025-09-30", 0.07, 3), ("2026-03-31", 0.035, 1))}
    dps_fy = {"declared": {"2024-12-31": 0.125, "2025-12-31": 0.14}, "paid": {}}
    rows = _cash_rows([16e6] * 4)
    d = F.build_dividends(annual, rows, {"declared": q, "paid": {}}, dps_fy, 80.0, "2026-10-14", "prices.json stats.last", _ctx())
    assert d["frequency"] == "quarterly", "the total dividends line matches dps_ttm × diluted shares (64.0M), so it is the common dividend"
    assert "its four quarters, 64.0M, match dps_ttm 0.14" in d["frequency_basis"] and "declaration cadence" in d["frequency_basis"]
    d = F.build_dividends(annual, rows, {"declared": q, "paid": {}}, dps_fy, 80.0, "2026-10-14", "prices.json stats.last", _ctx(flow_facts=_div_flow_facts(rows, "PaymentsOfDividendsCommonStock")))
    assert d["frequency"] == "quarterly" and d["frequency_basis"].startswith("cash dividends paid are filed for 4 of the last four quarters (2025-09-30: 16.0M")
    # a total line twice the common dividend (preferred inside) proves nothing: the per-share reading stands, with a note
    rows2 = _cash_rows([32e6] * 4)
    d = F.build_dividends(annual, rows2, {"declared": q, "paid": {}}, dps_fy, 80.0, "2026-10-14", "prices.json stats.last", _ctx(flow_facts=_div_flow_facts(rows2, "PaymentsOfDividends")))
    assert d["frequency"] != "quarterly" and any("not shown to be the common dividend alone" in n for n in d["notes"])


def test_build_dividends_filed_zero_dps_is_a_suspension_whatever_the_total_cash_line_says():
    # reviewer S1: DPS 1.0 a quarter to 2024-06-30, filed as 0 every quarter since and FY2025 = 0; PaymentsOfDividends 10M a quarter (preferred)
    annual = [{"fy": str(y), "period_end": f"{y}-12-31", "eps_diluted": -1.0, "dividends_paid": 4e7, "oe_conservative": 1e9, "fcf": 1e9, "shares_diluted": 1e8} for y in range(2021, 2026)]
    ends = ["2024-03-31", "2024-06-30", "2024-09-30", "2024-12-31", "2025-03-31", "2025-06-30", "2025-09-30", "2025-12-31", "2026-03-31", "2026-06-30"]
    qrows = [{"period_end": e, "fq": (i % 4) + 1, "shares_diluted": 1e8, "dividends_paid": 1e7, "buybacks": None, "share_issuance": None} for i, e in enumerate(ends)]
    dq = {e: _q(e, 1.0 if e < "2024-07-01" else 0.0, (i % 4) + 1, e[:4] + "-01-01") for i, e in enumerate(ends)}
    dfy = {"declared": {"2023-12-31": 4.0, "2024-12-31": 2.0, "2025-12-31": 0.0}, "paid": {}}
    for tag in ("PaymentsOfDividends", "PaymentsOfDividendsCommonStock"):
        d = F.build_dividends(annual, qrows, {"declared": dq, "paid": {}}, dfy, 50.0, "2026-10-14", "prices.json stats.last", _ctx(flow_facts=_div_flow_facts(qrows, tag)))
        assert d["frequency"] == "irregular" and any("filed as zero since" in n and "dividend suspended" in n for n in d["notes"]), tag
        assert not any("not a suspension" in n for n in d["notes"]), tag
    # reviewer S2: the per-share tag simply stops (no zeros) and only the TOTAL line is paid: neither suspended nor a payer — null
    dq2 = {e: v for e, v in dq.items() if v["val"] > 0}
    d = F.build_dividends(annual, qrows, {"declared": dq2, "paid": {}}, {"declared": {"2023-12-31": 4.0}, "paid": {}}, 50.0, "2026-10-14", "prices.json stats.last",
                          _ctx(flow_facts=_div_flow_facts(qrows, "PaymentsOfDividends")))
    assert d["frequency"] is None and any("whether the common dividend continues is not filed" in n for n in d["notes"])
    assert not any("not a suspension" in n or "dividend suspended" in n for n in d["notes"])


def test_build_dividends_keeps_an_fy_fact_below_mis_tagged_quarters():
    # FTI: the 10-K filed 2021-03-05 re-tags Q1 2019 at 0.52 (the year's total); FY2019 0.52 = 0.13 x 4 must survive, and so must
    # FY2020 0.13 (the cut and suspension) although later comparatives file Q2 / Q3 2020 at 0.13 too
    annual = [{"fy": str(y), "period_end": f"{y}-12-31", "eps_diluted": 1.0, "dividends_paid": 6e7, "oe_conservative": 5e8, "fcf": 5e8, "shares_diluted": 4.5e8} for y in range(2018, 2021)]
    q = {e: _q(e, v, fq, e[:4] + "-01-01") for e, v, fq in (("2018-03-31", 0.13, 1), ("2018-06-30", 0.13, 2), ("2018-09-30", 0.13, 3), ("2019-03-31", 0.52, 1),
                                                           ("2019-06-30", 0.13, 2), ("2019-09-30", 0.13, 3), ("2020-03-31", 0.13, 1))}
    q["2020-06-30"] = _q("2020-06-30", 0.13, 2, "2020-01-01", filed="2021-07-29")  # comparatives first filed a year later
    q["2020-09-30"] = _q("2020-09-30", 0.13, 3, "2020-01-01", filed="2021-10-27")
    d = F.build_dividends(annual, [], {"declared": q, "paid": {}}, {"declared": {"2018-12-31": 0.52, "2019-12-31": 0.52, "2020-12-31": 0.13}, "paid": {}}, 25.0, "2026-10-14",
                          "prices.json stats.last", _ctx())
    assert [(r["fy"], r["dps"]) for r in d["annual_dps"]] == [("2018", 0.52), ("2019", 0.52), ("2020", 0.13)] and d["last_cut_fy"] == "2020"
    assert any("2019-12-31 (0.52) is below the sum" in n and "kept as filed" in n for n in d["notes"])
    # HPQ: FY2019 0.64 beside 10-K-tagged quarters 0.53 / 0.64 -> kept, the growth streak unbroken
    hq = {e: _q(e, v, fq, fs) for e, v, fq, fs in (("2019-01-31", 0.53, 1, "2018-11-01"), ("2019-04-30", 0, 2, "2018-11-01"), ("2019-07-31", 0.64, 3, "2018-11-01"))}
    # (IBKR, by contrast, files the quarterly rate in every context — each quarter in its own 10-Q equal to the FY fact: that FY fact is not a total)
    iq = {e: _q(e, 0.025, fq, "2023-01-01") for e, fq in (("2023-03-31", 1), ("2023-06-30", 2), ("2023-09-30", 3))}
    d = F.build_dividends(annual, [], {"declared": {}, "paid": iq}, {"declared": {}, "paid": {"2023-12-31": 0.025}}, 60.0, "2026-10-14", "prices.json stats.last", _ctx())
    assert d["annual_dps"] == [] and any("one quarter's rate tagged with the full-year context" in n for n in d["notes"])
    ha = [{"fy": str(y), "period_end": f"{y}-10-31", "eps_diluted": 3.0, "dividends_paid": 1e9, "oe_conservative": 4e9, "fcf": 4e9, "shares_diluted": 1.5e9} for y in (2018, 2019, 2020)]
    d = F.build_dividends(ha, [], {"declared": hq, "paid": {}}, {"declared": {"2018-10-31": 0.56, "2019-10-31": 0.64, "2020-10-31": 0.7}, "paid": {}}, 25.0, "2026-10-14", "prices.json stats.last", _ctx())
    assert [r["dps"] for r in d["annual_dps"]] == [0.56, 0.64, 0.7] and d["growth_years"] == 2


def test_original_quarterly_dps_takes_the_value_the_year_to_date_facts_give():
    g, tag = "us-gaap", "CommonStockDividendsPerShareDeclared"

    def f(start, end, val, filed, form="10-Q", fp="Q1"):
        return (g, tag, "USD/shares", _e(start, end, val, filed, filed, form, fp, int(end[:4])))
    # FTI: Q1 2019 0.13 in its 10-Q, 0.52 in the 10-K filed 2021-03-05; six months 0.26 − Q2 0.13 = 0.13
    facts = _facts([f("2019-01-01", "2019-03-31", 0.13, "2019-05-09"), f("2019-01-01", "2019-03-31", 0.52, "2021-03-05", "10-K", "FY"),
                    f("2019-04-01", "2019-06-30", 0.13, "2019-08-08", fp="Q2"), f("2019-01-01", "2019-06-30", 0.26, "2019-08-08", fp="Q2")])
    dps_q, _, meta = F.dividends_inputs(facts)
    assert dps_q["declared"]["2019-03-31"]["val"] == 0.13 and any("2019-03-31: 0.13 (filed 2019-05-09) used, not 0.52" in n for n in meta["split_notes"])
    # WRB Q2 2021: the 10-Q tagged 0.12, but the later six-month 0.75 − Q1 0.12 = 0.63, the later comparative's value
    paid = "CommonStockDividendsPerShareCashPaid"
    facts = _facts([
        ("us-gaap", paid, "USD/shares", _e("2021-01-01", "2021-03-31", 0.12, "2021-05-05", "a", "10-Q", "Q1", 2021)),
        ("us-gaap", paid, "USD/shares", _e("2021-04-01", "2021-06-30", 0.12, "2021-08-02", "b", "10-Q", "Q2", 2021)),
        ("us-gaap", paid, "USD/shares", _e("2021-04-01", "2021-06-30", 0.63, "2022-08-02", "c", "10-Q", "Q2", 2022)),
        ("us-gaap", paid, "USD/shares", _e("2021-01-01", "2021-06-30", 0.75, "2022-08-02", "c", "10-Q", "Q2", 2022)),
    ])
    dps_q, _, meta = F.dividends_inputs(facts)
    assert dps_q["paid"]["2021-06-30"]["val"] == 0.63 and not meta["split_notes"], "the latest filing is the one the arithmetic supports: nothing to change"
    # with no year-to-date facts at all, the first filing wins
    facts = _facts([f("2019-01-01", "2019-03-31", 0.13, "2019-05-09"), f("2019-01-01", "2019-03-31", 0.52, "2021-03-05", "10-K", "FY")])
    assert F.dividends_inputs(facts)[0]["declared"]["2019-03-31"]["val"] == 0.13


def test_split_ratio_read_from_re_filed_values_is_a_whole_number_ratio():
    assert F.snap_ratio(0.89 / 0.59) == (1.5, (3, 2)) and F.snap_ratio(0.5) == (0.5, (1, 2)) and F.snap_ratio(1 / 0.6667, tol=0.001)[0] == 1.5
    assert F.snap_ratio(1.37) is None and F.snap_ratio(10.0) == (10.0, (10, 1))
    # WRB's June 2024 3-for-2 (no ratio fact): FY2022 CashPaid 0.89 (10-Ks 2023 / 2024) and 0.59 (10-K 2025); a diluted count re-filed ×1.5 on 2024-08-02
    hi = [{"val": 0.89, "filed": "2023-02-24"}, {"val": 0.89, "filed": "2024-02-23"}]
    lo = [{"val": 0.59, "filed": "2025-02-24"}]
    post_is_lo, why, ev = F.split_restatement(hi, lo, [], [("2023-06-30", 1.5, "2023-08-03", "2024-08-02")])
    assert post_is_lo and ev == ("re_filed_counts", "2023-06-30", 1.5, "2024-08-02") and "read as 3-for-2" in why
    # a split ratio filed rounded and the wrong way round (WRB 2019: 0.6667), share counts filed in thousands vs units
    shares = {"2016-12-31": (128552838, "2017-02-24"), "2017-12-31": (193527, "2020-02-21")}
    assert F.split_direction([("2019-04-02", 0.6667)], shares)[0][2] == 1.5


def test_basis_breaks_reads_split_adjusted_share_counts():
    # WRB: FY2021 0.8933 -> FY2022 0.59 is a real decline (special dividends); the FY2021 diluted count was last filed before the
    # 2024 3-for-2 and FY2022's after it, so the as-filed counts move ×1.5 and the guard read an "unfiled split"
    annual = [{"fy": str(y), "period_end": f"{y}-12-31", "eps_diluted": e, "dividends_paid": 3e8, "oe_conservative": 1e9, "fcf": 1e9, "shares_diluted": s}
              for y, e, s in ((2021, 4.5, 2.66e8), (2022, 3.5, 3.99e8), (2023, 3.5, 3.95e8))]
    dps_fy = {"declared": {}, "paid": {"2021-12-31": 0.8933, "2022-12-31": 0.59, "2023-12-31": 1.29}}
    d = F.build_dividends(annual, [], {"declared": {}, "paid": {}}, dps_fy, 70.0, "2026-10-14", "prices.json stats.last", _ctx())
    assert d["basis_breaks"] and d["last_cut_fy"] is None, "as filed: the guard misreads the split"
    adj = {"2021-12-31": 2.66e8 * 1.5, "2022-12-31": 3.99e8, "2023-12-31": 3.95e8}
    d = F.build_dividends(annual, [], {"declared": {}, "paid": {}}, dps_fy, 70.0, "2026-10-14", "prices.json stats.last", _ctx(shares_by_end=adj))
    assert d["basis_breaks"] == [] and d["last_cut_fy"] == "2022" and d["growth_years"] == 1


def test_dividends_inputs_reads_one_split_tagged_twice_a_year_apart():
    # WCN: 1.5 tagged at 2017-04-26 and again at 2018-03-31; the only re-filings are of values last filed before the first split
    g = "us-gaap"
    sh = "WeightedAverageNumberOfDilutedSharesOutstanding"
    facts = _facts([
        (g, "StockholdersEquityNoteStockSplitConversionRatio1", "pure", _e("2017-04-26", "2017-04-26", 1.5, "2017-07-26", "a", "10-Q", "Q2", 2017)),
        (g, "StockholdersEquityNoteStockSplitConversionRatio1", "pure", _e("2018-03-31", "2018-03-31", 1.5, "2018-04-26", "b", "10-Q", "Q1", 2018)),
        (g, sh, "shares", _e("2016-04-01", "2016-06-30", 1.76e8, "2016-08-05", "c", "10-Q", "Q2", 2016)),
        (g, sh, "shares", _e("2016-04-01", "2016-06-30", 2.64e8, "2017-07-26", "a", "10-Q", "Q2", 2017)),
        (g, sh, "shares", _e("2016-07-01", "2016-09-30", 1.76e8, "2016-10-31", "d", "10-Q", "Q3", 2016)),
        (g, sh, "shares", _e("2016-07-01", "2016-09-30", 2.64e8, "2017-10-26", "e", "10-Q", "Q3", 2017)),
        (g, "CommonStockDividendsPerShareCashPaid", "USD/shares", _e("2016-07-01", "2016-09-30", 0.145, "2016-10-31", "d", "10-Q", "Q3", 2016)),
    ])
    dps_q, _, meta = F.dividends_inputs(facts)
    assert [s[:2] for s in meta["splits"]] == [("2017-04-26", 1.5)] and any("one split tagged twice" in n for n in meta["split_notes"])
    assert close(dps_q["paid"]["2016-09-30"]["val"], 0.145 / 1.5), "divided by 1.5, not 2.25"


def test_issuance_below_zero_is_kept_unless_its_own_year_says_otherwise():
    iss = "ProceedsFromStockPlans"
    # IRM: a net stock-plan line filed −4.8M for FY2022 and consistently below zero: a net outflow, kept as filed
    ff = {"share_issuance": {("2022-01-01", "2022-12-31"): (-4849000, iss, "USD", "2023-02-23", "K"), ("2022-01-01", "2022-09-30"): (-3000000, iss, "USD", "2022-11-03", "Q")}}
    qv, av, fixes = F.sign_fixed_flows([{"fy": "2022", "period_end": "2022-12-31", "share_issuance": -4849000}], [], ff)
    assert av["share_issuance"]["2022-12-31"] == -4849000 and fixes["share_issuance"][0][2] == F.SIGN_KEPT and "kept as filed" in fixes["share_issuance"][0][1]
    # LRCX: a direct three-month fact −43,000 with a six-month −237,000: kept
    ff = {"share_issuance": {("2024-07-01", "2024-09-29"): (-43000, "ProceedsFromIssuanceOfCommonStock", "USD", "2024-10-28", "Q")}}
    qv, _, fixes = F.sign_fixed_flows([], [{"period_end": "2024-09-29", "share_issuance": -43000}], ff)
    assert qv["share_issuance"]["2024-09-29"] == -43000 and fixes["share_issuance"][0][2] == F.SIGN_KEPT
    # CCI-shaped issuance: FY filed below zero beside positive year-to-date facts -> a sign error, rebuilt from absolute values
    ff = {"share_issuance": {("2025-01-01", "2025-09-30"): (30e6, iss, "USD", "2025-11-06", "Q"), ("2025-01-01", "2025-12-31"): (-40e6, iss, "USD", "2026-02-23", "K")}}
    qv, av, fixes = F.sign_fixed_flows([{"fy": "2025", "period_end": "2025-12-31", "share_issuance": -40e6}],
                                       [{"period_end": "2025-12-31", "share_issuance": -70e6, "share_issuance_derived": True}], ff)
    assert av["share_issuance"]["2025-12-31"] == 40e6 and qv["share_issuance"]["2025-12-31"] == 10e6 and {x[2] for x in fixes["share_issuance"]} == {F.SIGN_ABS}


def test_build_dividends_a_decreasing_year_to_date_is_left_out_not_a_sign_error():
    # DHI: share_issuance facts all positive or zero (9M 8.5M, FY 0 from a filing that tags only the common line): Q4 = 0 − 8.5M
    tag = "ProceedsFromIssuanceOfCommonStock"
    qrows = [{"period_end": e, "fq": fq, "shares_diluted": 3e8, "dividends_paid": 1.2e8, "buybacks": 7e8, "share_issuance": v, "share_issuance_derived": fq > 1}
             for e, fq, v in (("2025-06-30", 3, 2e6), ("2025-09-30", 4, -8.5e6), ("2025-12-31", 1, 3e6), ("2026-03-31", 2, 2e6))]
    ff = {"share_issuance": {("2024-10-01", "2025-06-30"): (8.5e6, tag, "USD", "2025-07-25", "Q"), ("2024-10-01", "2025-09-30"): (0, tag, "USD", "2025-11-14", "K"),
                             ("2025-10-01", "2025-12-31"): (3e6, tag, "USD", "2026-01-30", "Q"), ("2025-10-01", "2026-03-31"): (5e6, tag, "USD", "2026-04-28", "Q")},
          "dividends_paid": {}, "buybacks": {}}
    d = F.build_dividends([], qrows, {"declared": {}, "paid": {}}, {"declared": {}, "paid": {}}, 150.0, "2026-10-14", "prices.json stats.last",
                          _ctx(flow_facts=ff, shares_instant=(2.9e8, "2026-03-31", "dei")))
    leg = d["legs"]["share_issuance"]
    assert "sign_corrected" not in leg and leg["left_out"] and "the year-to-date facts decrease (2024-10-01..2025-06-30 = 8,500,000 > 2024-10-01..2025-09-30 = 0)" in leg["left_out"][0]
    assert not any(n.startswith("sign convention") for n in d["notes"]) and any("quarters left out (not a sign error)" in n for n in d["notes"])
    assert "filed below zero" not in (d["yields_display"]["net_buyback_yield"]["note"] or "") and "sign_corrected" not in d["yield_basis"]["net_buyback_yield"]


# ---------------- Codex review of PR #2: quarterly share evidence for a split ----------------
def _q_facts(q1_count=210.3e6, q2_count=210.2e6):
    """Q (Qnity): the 0.5 spin-off distribution ratio (one Qnity share per two DuPont shares) tagged on the duration contexts of
    its Q1 and Q2 2026 10-Qs; diluted counts FY2023-FY2025 from the 10-K filed 2026-02-26, then the 2026 quarters; FY2025
    declared DPS 0.14 and Q2 2026 0.08. No fiscal year has been filed since the ratio, so only the quarters can speak."""
    def ratio(start, end, filed, fp):
        return ("us-gaap", "StockholdersEquityNoteStockSplitConversionRatio1", "pure", _e(start, end, 0.5, filed, filed, "10-Q", fp))

    def dps(start, end, val, filed, form="10-Q", fp="Q2"):
        return ("us-gaap", "CommonStockDividendsPerShareDeclared", "USD/shares", _e(start, end, val, filed, filed, form, fp, int(end[:4])))
    return _facts([
        ratio("2026-01-01", "2026-03-31", "2026-05-12", "Q1"), ratio("2026-01-01", "2026-06-30", "2026-08-04", "Q2"),
        _sh("2023-01-01", "2023-12-31", 209.4e6, "2026-02-26", "10-K", "FY"), _sh("2024-01-01", "2024-12-31", 209.4e6, "2026-02-26", "10-K", "FY"),
        _sh("2025-07-01", "2025-09-30", 209.0e6, "2025-11-18", "10-Q", "Q3"), _sh("2025-01-01", "2025-12-31", 209.8e6, "2026-02-26", "10-K", "FY"),
        _sh("2026-01-01", "2026-03-31", q1_count, "2026-05-12"), _sh("2026-04-01", "2026-06-30", q2_count, "2026-08-04", fp="Q2"),
        dps("2025-01-01", "2025-12-31", 0.14, "2026-02-26", "10-K", "FY"), dps("2026-04-01", "2026-06-30", 0.08, "2026-08-04"),
    ])


def test_dividends_inputs_rejects_a_ratio_the_quarterly_counts_do_not_bear_out():
    # Before: the annual counts alone (none filed after the ratio) said nothing, the 0.5 was applied and the FY2025 DPS of 0.14
    # became 0.28 — yield 0.2302% and EPS payout 8.4848% at $121.62 instead of 0.1151% / 4.2424%
    dps_q, dps_fy, meta = F.dividends_inputs(_q_facts())
    assert meta["splits"] == [], meta["splits"]
    assert dps_fy["declared"]["2025-12-31"] == 0.14 and dps_q["declared"]["2026-06-30"]["val"] == 0.08
    note = next(n for n in meta["split_notes"] if "is left out" in n and "0.5" in n)
    assert "209,800,000 (FY ending 2025-12-31" in note and "210,300,000 (quarter ending 2026-03-31)" in note and "×1.00" in note
    annual = [{"fy": "2025", "period_end": "2025-12-31", "eps_diluted": 3.30, "dividends_paid": None, "oe_conservative": None, "fcf": None, "shares_diluted": 209.8e6}]
    d = F.build_dividends(annual, [], dps_q, dps_fy, 121.62, "2026-10-14", "prices.json stats.last", _ctx(splits=meta["splits"]))
    assert d["split_adjustments"] == [] and close(d["dps_ttm"], 0.14)
    assert [r["dps"] for r in d["annual_dps"]] == [0.14]
    assert round(d["dividend_yield"] * 100, 4) == 0.1151 and round(d["payout_ratio_eps"] * 100, 4) == 4.2424


def test_dividends_inputs_keeps_a_split_the_quarterly_counts_bear_out():
    # the same facts with the Q1 2026 count halved: a genuine 1-for-2 reverse split evidenced by the quarters is still applied
    dps_q, dps_fy, meta = F.dividends_inputs(_q_facts(q1_count=105.2e6, q2_count=105.1e6))
    assert [(d, r) for d, r, *_ in meta["splits"]] == [("2026-03-31", 0.5)]
    assert close(dps_fy["declared"]["2025-12-31"], 0.28), "the FY2025 DPS filed before the reverse split is restated to the new basis"


def test_share_count_move_reads_fiscal_years_and_quarters():
    counts = {("2025-01-01", "2025-12-31"): (209.8e6, "2026-02-26"), ("2025-10-01", "2025-12-31"): (209.9e6, "2026-02-26"),
              ("2026-01-01", "2026-03-31"): (210.3e6, "2026-05-12"), ("2026-01-01", "2026-06-30"): (210.3e6, "2026-08-04"),
              ("2026-04-01", "2026-06-30"): (210.2e6, "2026-08-04")}
    obs, ev = F.share_count_move(counts, "2026-03-31")
    assert close(obs, 210.3e6 / 209.9e6) and "(quarter ending 2025-12-31" in ev, "the shortest period at the last end before the date (Q4, not FY)"
    assert F.share_count_move(counts, "2027-01-01") is None and F.share_count_move(counts, "2025-01-01") is None
    # the annual {end: (val, filed)} shape still reads as before
    obs, ev = F.share_count_move({"2024-12-31": (100e6, "2025-02-01"), "2025-12-31": (200e6, "2026-02-01")}, "2025-06-01")
    assert close(obs, 2.0) and "(FY ending 2024-12-31" in ev and "(FY ending 2025-12-31)" in ev
    # a count filed in thousands against one in shares is normalised
    assert close(F.share_count_move({"2024-12-31": (100e3, "2025-02-01"), "2025-12-31": (101e6, "2026-02-01")}, "2025-06-01")[0], 1.01)


def test_diluted_counts_with_filed_reads_quarters_and_years_newest_filing():
    facts = _facts([_sh("2025-01-01", "2025-12-31", 209.8e6, "2026-02-26", "10-K", "FY"), _sh("2025-01-01", "2025-12-31", 209.7e6, "2027-02-26", "10-K", "FY"),
                    _sh("2026-01-01", "2026-03-31", 210.3e6, "2026-05-12"), _sh("2026-01-01", "2026-01-20", 1e6, "2026-05-12")])
    c = F.diluted_counts_with_filed(facts)
    assert c == {("2025-01-01", "2025-12-31"): (209.7e6, "2027-02-26"), ("2026-01-01", "2026-03-31"): (210.3e6, "2026-05-12")}, "newest filing; a 19-day stub is no period"


# ---------------- 2026-10-16: the price leaves (price_dividends) ----------------
def _jd(o):
    return json.dumps(o, ensure_ascii=False)  # key order included: the file is written in this order


def test_price_dividends_ads_ratio_divides_market_cap():
    """ADS filers (2026-10-18): shares_outstanding is the ordinary count and
    the price is per ADS, so the block's yield denominator is the traded cap
    — price x shares / ads_ratio, the engine's market_cap_est basis. Ratio
    0.5 (the FMS shape): the traded cap is 2x the naive product and the
    yields halve. The ratio rides in the block from dcf_numbers.json, so
    build_site's repricing divides too."""
    annual, qrows, dps_q, dps_fy = _fixture()
    ctx = _ctx(shares_instant=(2027130587, "2026-03-31", "dei:EntityCommonStockSharesOutstanding (10-Q filed 2026-04-30)"), ads_ratio=0.5)
    d = F.build_dividends(annual, qrows, dps_q, dps_fy, 15.10, "2026-10-14", "prices.json stats.last", ctx)
    assert close(d["market_cap"], 15.10 * 2027130587 / 0.5), "build prices the block on the ADS basis"
    assert "ADS ratio 0.5" in d["market_cap_basis"], "the printed basis names the division"
    r = F.price_dividends(d, 20.0, "2026-10-20", "prices.json stats.last")
    assert close(r["market_cap"], 20.0 * 2027130587 / 0.5)
    for k in ("buyback_yield", "net_buyback_yield", "shareholder_yield"):
        assert close(r[k], d["yield_basis"][k]["numerator"] / r["market_cap"]), k


def test_price_dividends_recomputes_every_price_leaf_from_the_block():
    annual, qrows, dps_q, dps_fy = _fixture()
    ctx = _ctx(shares_instant=(2027130587, "2026-03-31", "dei:EntityCommonStockSharesOutstanding (10-Q filed 2026-04-30)"))
    d = F.build_dividends(annual, qrows, dps_q, dps_fy, 15.10, "2026-10-14", "prices.json stats.last", copy.deepcopy(ctx))
    before = _jd(d)
    r = F.price_dividends(d, 20.0, "2026-10-20", "prices.json stats.last")
    assert _jd(d) == before, "the input block is not modified"
    assert (r["price"], r["price_date"], r["price_source"], r["price_note"]) == (20.0, "2026-10-20", "prices.json stats.last", None)
    assert close(r["market_cap"], 20.0 * 2027130587) and r["market_cap_basis"].startswith("20.0 × 2,027,130,587 shares (dei:")
    assert close(r["dividend_yield"], d["dps_ttm"] / 20.0) and close(r["dividend_yield"], d["dividend_yield"] * 15.10 / 20.0)
    for k in ("buyback_yield", "net_buyback_yield", "shareholder_yield"):
        assert close(r[k], d["yield_basis"][k]["numerator"] / r["market_cap"]), k
        assert r["yield_basis"][k]["denominator"] == r["market_cap_basis"] and r["yields_display"][k]["value"] == r[k]
        assert r["yields_display"][k]["label"].endswith(f"{r[k] * 100:.2f}%") or "(incomplete)" in r["yields_display"][k]["label"]
    assert r["yield_basis"]["dividend_yield"]["denominator"] == "price 20.0 (prices.json stats.last)"
    # everything else is the block as built
    strip = lambda b: {k: v for k, v in b.items() if k not in ("price", "price_date", "price_source", "price_note", "market_cap", "market_cap_basis",
                                                                "dividend_yield", "buyback_yield", "net_buyback_yield", "shareholder_yield",
                                                                "yield_basis", "yields_display")}
    assert _jd(strip(r)) == _jd(strip(d))
    # back at the original price: the original block, key order included
    assert _jd(F.price_dividends(r, 15.10, "2026-10-14", "prices.json stats.last")) == before
    # no price: every yield null, the note says why (price_note, never `notes`), the bound notes go with the market cap
    n = F.price_dividends(d, None, None, None)
    assert n["market_cap"] is None and all(n[k] is None for k in F.YIELD_KEYS) and all(v["label"] == "—" for v in n["yields_display"].values())
    assert n["price_note"] == "price: neither prices.json nor score.json carries a price — yields null" and not any(x.startswith("price:") for x in n["notes"])
    s = F.price_dividends(d, 14.0, "2026-10-14", "score.json price")
    assert s["price_note"] == "price: 14.0 from score.json (2026-10-14); prices.json absent" and s["notes"] == d["notes"]
    # a bound note follows the market cap, placed right after the denominator (the order the file has always had)
    for r_ in qrows[:-1]:
        r_["buybacks"] = None
    p = F.build_dividends(annual, qrows, dps_q, dps_fy, 15.10, "2026-10-14", "prices.json stats.last", copy.deepcopy(ctx))
    yb = p["yield_basis"]["buyback_yield"]
    assert yb["bound"] == "lower" and yb["note"] == F.YIELD_BOUND_NOTES["lower"] and list(yb).index("note") == list(yb).index("denominator") + 1
    q = F.price_dividends(p, None, None, None)
    assert "note" not in q["yield_basis"]["buyback_yield"] and q["yields_display"]["buyback_yield"]["note"].startswith("buybacks: ")
    assert _jd(F.price_dividends(q, 15.10, "2026-10-14", "prices.json stats.last")) == _jd(p)
    # a block written before 2026-10-16 carried the price note in `notes`: dropped, the note is price_note now
    legacy = dict(n, notes=["price: neither prices.json nor score.json carries a price — yields null"] + n["notes"])
    legacy.pop("price_note")
    assert F.price_dividends(legacy, 20.0, "2026-10-20", "prices.json stats.last")["notes"] == d["notes"]
    assert F.price_dividends(None, 1.0, None, None) is None and F.price_dividends([1], 1.0, None, None) == [1]
    assert F.repriceable(d) and not F.repriceable({k: v for k, v in d.items() if k != "yields_display"}) and not F.repriceable(None)


def test_build_dividends_at_any_price_is_price_dividends_of_the_block():
    """Every build_dividends call the other tests in this module make (the shapes of HBAN, KR, TKO, CCL,
    CCI, AVGO, ZTS, ...) is replayed at a second price P: build_dividends(P) must equal
    price_dividends(build_dividends(Q), P) byte for byte (key order included), and at the same price the
    two blocks must differ only in the volatile price leaves (fundamentals.PRICE_LEAVES)."""
    import _stable
    orig, seen = F.build_dividends, []

    def check(*a, **k):
        snap = copy.deepcopy((list(a), k))  # the inputs as passed (the call itself appends to ctx["warnings"])
        out = orig(*a, **k)
        price = snap[0][4]
        for p2, d2, s2 in (((price * 1.37 if F._num(price) and price > 0 else 42.0), "2026-11-02", "prices.json stats.last"),
                           (9.5, "2026-11-03", "score.json price"), (None, None, None)):
            b, kb = copy.deepcopy(snap)
            b[4:7] = [p2, d2, s2]
            want = orig(*b, **kb)
            got = F.price_dividends(out, p2, d2, s2)
            assert _jd(got) == _jd(want), (snap[0][4:7], p2)
            if F._num(price) and price > 0 and p2 is not None:  # a close moved, nothing filed: only the volatile leaves differ
                assert _stable.canonical({"dividends": want}, F.PRICE_LEAVES) == _stable.canonical({"dividends": out}, F.PRICE_LEAVES)
        assert _jd(F.price_dividends(out, *snap[0][4:7])) == _jd(out), "idempotent at its own price"
        seen.append(1)
        return out

    F.build_dividends = check
    try:
        for name, fn in list(globals().items()):
            if name.startswith("test_") and callable(fn) and name != "test_build_dividends_at_any_price_is_price_dividends_of_the_block":
                fn()
    finally:
        F.build_dividends = orig
    assert len(seen) >= 60, len(seen)



def test_read_price_skips_a_post_split_close():
    """A split since the scored run (live.json split_factor 2.0) leaves prices.json's close in post-split units while the
    filed DPS / share counts are pre-split: _read_price falls back to the carried close (or score.json), never pairing them."""
    import tempfile, shutil
    d = tempfile.mkdtemp(prefix="fund_split_")
    try:
        with open(os.path.join(d, "prices.json"), "w", encoding="utf-8") as f:
            json.dump({"stats": {"last": 50.0, "last_date": "2026-10-20"}}, f)
        with open(os.path.join(d, "score.json"), "w", encoding="utf-8") as f:
            json.dump({"price": 101.0, "analysis_date": "2026-10-01"}, f)
        assert F._read_price(d)[:2] == (50.0, "2026-10-20")
        with open(os.path.join(d, "live.json"), "w", encoding="utf-8") as f:
            json.dump({"split_factor": 1.0}, f)
        assert F._read_price(d)[:2] == (50.0, "2026-10-20")
        with open(os.path.join(d, "live.json"), "w", encoding="utf-8") as f:
            json.dump({"split_factor": 2.0}, f)
        assert F._read_price(d) == (101.0, "2026-10-01", "score.json price"), F._read_price(d)
        prev = {"price": 100.0, "price_date": "2026-10-10", "price_source": "prices.json stats.last"}
        assert F._read_price(d, prev) == (100.0, "2026-10-10", "prices.json stats.last"), F._read_price(d, prev)
    finally:
        shutil.rmtree(d, ignore_errors=True)

if __name__ == "__main__":
    fails = 0
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn(); print(f"PASS {name}")
            except AssertionError as e:
                fails += 1; print(f"FAIL {name}: {e}")
            except Exception as e:  # a crash is a failure too
                fails += 1; print(f"ERROR {name}: {type(e).__name__}: {e}")
    sys.exit(1 if fails else 0)
