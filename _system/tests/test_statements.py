#!/usr/bin/env python3
"""statements.py tests. Run: python3 _system/tests/test_statements.py
(or python3 -m pytest _system/tests). No network: every EDGAR payload is an
inline fixture, and the build_site pass-through runs on a COPY of the APP
folder in a temporary STOCKS_BASE (nothing in the repo is written).

1. Line assembly from a small companyfacts fixture: two fiscal years, ten
   quarters — direct 3-month income facts, YTD-only cash-flow facts (quarter =
   YTD − prior YTD, flagged), Q4 = FY − 9M, balance-sheet instants (never
   derived, ttm = latest), fiscal Q4 shares = 4×FY − three quarters and Q4
   EPS = Q4 net income ÷ that count (both flagged).
2. Growth arrays: annual vs the prior consecutive FY, quarterly vs the same
   quarter a year earlier, null at the edges and for ratio / pct lines.
3. TTM rule: the sum of the last four consecutive quarters (shares averaged,
   instants = latest); null when the four are not consecutive.
4. Derived lines: ebitda, fcf, owner_earnings, total_debt, net_cash, margins,
   per-share metrics — only from lines present in the same period; a never-
   filed optional component counts as zero, a missing total gives null, and no
   total is synthesised from components.
5. Submissions skip rule: run_one re-fetches only when the newest filing date
   / form moved (or --force), reading the cached payloads.
7-9. Review round 2026-10-15: Q4 legs from the same filing generation (+ the
   basis-break flag), one unit per file and 6-K-only filers, the per-period
   revenue total and the quarters-vs-FY plausibility guard, the bank provision
   components, other non-operating reconciled to pretax income, Kroger's net
   interest / LIFO inventory / total-costs lines, capex read as zero when the
   filing has no such line, combined-total debt tags, split adjustment, the
   day-weighted Q4 share count, and the covered_through skip rule.
10. Review round 3 (2026-10-15): one split however many contexts its ratio
   is tagged in (DXCM) and an unborne ratio not applied (CFG); the newest
   filing of a period with its anomalies dropped — shifted column, power-of-ten
   slip, filed zero (HBAN, HAL, HIG, ECHO, DXCM); one filed fact under two debt tags counted once (GFI); capex
   never read as zero and the REIT capex captions (APP, EXR); no quarter from
   unpaired legs and the catch-all composition check (APP Q4 FY2025); payment
   sign slips (CCI); quarter labels on the annual rule (TDY, KVUE); week-end vs
   month-end dates merged (HSY); face interest line and net interest shown once
   (APP, KR); industry revenue fallbacks (CMG, EQT); continuing-operations EPS
   (HAL); the original filing date; derived lines flagged derived.
11. Review round 4 (2026-10-15): a later 10-K's recast takes the whole period
   and growth is blank across two filing generations (ECHO / HPQ / APP / NVT);
   FCF on one basis — continuing OCF when discontinued investing flows are
   split out, blank when OCF and capex come from two generations (CCI); Q4
   diluted shares only in a loss quarter and Q4 EPS = FY − three quarters
   (DXCM); a spin-off ratio not borne out by the quarterly counts (Q); a
   corroborated 1-for-15 reverse split (DFTX); two splits of one ratio (WRB);
   a gross interest tag carrying the net figure (KR); one capex caption per
   series (EXR).
12. Review round 5 (Codex, PR #2): a cash line filed as the combined cash +
   restricted cash total — the restricted part deducted from net cash, net
   cash per share and the ROIC proxy where it is tagged (NTRS FY2025
   2,521.6M / 13.53 -> 1,990.4M / 10.68), flagged where it is not, the line
   labelled and marked; a separate restricted caption next to a cash-only
   line changes nothing; the --all rebuild rule for files written before;
   statements.json written only when its content (not just as_of) changes.
   Verifier round: growth blank between a period that still counts
   restricted cash and one that deducts it (NTRS 2023-06-30 −12.6% compared
   two definitions), kept next to a caption that does not say (NTRS's
   CashAndDueFromBanks); the same date's cash-only caption from the same
   filing decides the part (ZTS FY2025: 0, not the tagged 2M; another filing
   generation is no evidence); current + noncurrent restricted cash (U);
   the "(some periods incl. restricted cash)" labels.
6. build_site pass-through on a temp site dir with --only APP:
   data/APP.statements.json next to the record, has.statements / has.profile,
   record.profile, prices.intraday / sessions_5d in the record, sessions_5d
   dropped and intraday kept in the attachment, the copy removed when the
   folder's file goes and restored when only the copy is missing, and the
   watchlist in file order with the outside-the-universe list.
"""
import copy
import datetime
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SYS = os.path.dirname(HERE)
BASE = os.path.dirname(SYS)
sys.path.insert(0, SYS)
import statements as S  # noqa: E402
import build_site as B  # noqa: E402

# ---------------------------------------------------------------- fixture
Q_ENDS = {2024: ["2024-03-31", "2024-06-30", "2024-09-30", "2024-12-31"], 2025: ["2025-03-31", "2025-06-30", "2025-09-30", "2025-12-31"],
          2026: ["2026-03-31", "2026-06-30"]}
FILED = {"2024-03-31": "2024-05-01", "2024-06-30": "2024-08-01", "2024-09-30": "2024-11-01", "2024-12-31": "2025-02-20",
         "2025-03-31": "2025-05-01", "2025-06-30": "2025-08-01", "2025-09-30": "2025-11-01", "2025-12-31": "2026-02-19",
         "2026-03-31": "2026-05-01", "2026-06-30": "2026-08-01"}


def _entry(start, end, val, form, fp, fy, unit="USD"):
    return {"start": start, "end": end, "val": val, "fy": fy, "fp": fp, "form": form, "filed": FILED[end], "accn": f"acc-{end}"}


def _flow_entries(per_quarter, mode):
    """per_quarter: {year: [q1, q2, q3, q4]} (2026: two quarters). mode '3m+ytd'
    files the 3-month fact and the YTD fact in each 10-Q and the FY fact in the
    10-K; 'ytd' files YTD legs only (cash-flow style)."""
    out = []
    for year, vals in per_quarter.items():
        start = f"{year}-01-01"
        ytd = 0.0
        for i, v in enumerate(vals):
            end = Q_ENDS[year][i]
            ytd += v
            if i == 3:
                out.append(_entry(start, end, ytd, "10-K", "FY", year))
                continue
            fp = f"Q{i + 1}"
            if mode == "3m+ytd":
                qs = f"{year}-0{3 * i + 1}-01"
                out.append(_entry(qs, end, v, "10-Q", fp, year))
            if i > 0 or mode == "ytd":
                out.append(_entry(start, end, ytd, "10-Q", fp, year))
            elif mode == "3m+ytd":
                pass  # Q1: the 3-month fact IS the YTD fact
    return out


def _instant_entries(values):
    out = []
    for end, v in values.items():
        is_fy = end.endswith("12-31")
        out.append({"end": end, "val": v, "fy": int(end[:4]), "fp": "FY" if is_fy else f"Q{(int(end[5:7]) + 2) // 3}",
                    "form": "10-K" if is_fy else "10-Q", "filed": FILED[end], "accn": f"acc-{end}"})
    return out


def _per_share_entries(per_quarter, unit):
    """EPS / weighted shares: 3-month facts for Q1–Q3, the FY fact in the 10-K (no Q4 fact, like a real filer)."""
    out = []
    for year, vals in per_quarter.items():
        for i, v in enumerate(vals):
            end = Q_ENDS[year][i]
            if i == 3:
                out.append(_entry(f"{year}-01-01", end, v, "10-K", "FY", year, unit))
            else:
                out.append(_entry(f"{year}-0{3 * i + 1}-01", end, v, "10-Q", f"Q{i + 1}", year, unit))
    return out


REV = {2024: [220, 240, 260, 280], 2025: [270, 290, 310, 330], 2026: [350, 370]}
COGS = {2024: [110, 120, 130, 140], 2025: [130, 140, 150, 160], 2026: [170, 180]}
OPI = {2024: [30, 35, 40, 45], 2025: [40, 45, 50, 55], 2026: [60, 65]}
NI = {2024: [20, 25, 25, 30], 2025: [30, 35, 40, 45], 2026: [50, 55]}
OCF = {2024: [30, 35, 40, 45], 2025: [40, 45, 50, 65], 2026: [60, 65]}
CAPEX = {2024: [5, 5, 5, 5], 2025: [6, 6, 6, 6], 2026: [7, 7]}
SBC = {2024: [2, 2, 2, 2], 2025: [3, 3, 3, 3], 2026: [3, 3]}
DA = {2024: [10, 10, 10, 10], 2025: [11, 11, 11, 11], 2026: [12, 12]}
SH = {2024: [100, 100, 100, 100], 2025: [99, 98, 97, 98], 2026: [96, 95]}  # index 3 = the FY weighted average
EPS = {2024: [0.20, 0.25, 0.25, 1.00], 2025: [0.30, 0.36, 0.41, 1.53], 2026: [0.52, 0.58]}
ALL_ENDS = [e for y in (2024, 2025, 2026) for e in Q_ENDS[y]]
ASSETS = {e: 1000 + 40 * i for i, e in enumerate(ALL_ENDS)}
LIAB = {e: 600 + 10 * i for i, e in enumerate(ALL_ENDS)}
EQUITY = {e: ASSETS[e] - LIAB[e] for e in ALL_ENDS}
CASH = {e: 150 + 15 * i for i, e in enumerate(ALL_ENDS)}
CUR_A = {e: 400 + 20 * i for i, e in enumerate(ALL_ENDS)}
CUR_L = {e: 250 + 5 * i for i, e in enumerate(ALL_ENDS)}
LTD = {e: 200 for e in ALL_ENDS}
GOODWILL = {e: 50 for e in ALL_ENDS}
SHARES_OUT = {e: 100 - i for i, e in enumerate(ALL_ENDS)}


def make_facts():
    us = {
        "RevenueFromContractWithCustomerExcludingAssessedTax": _flow_entries(REV, "3m+ytd"),
        "CostOfRevenue": _flow_entries(COGS, "3m+ytd"),
        "OperatingIncomeLoss": _flow_entries(OPI, "3m+ytd"),
        "NetIncomeLoss": _flow_entries(NI, "3m+ytd"),
        "NetCashProvidedByUsedInOperatingActivities": _flow_entries(OCF, "ytd"),
        "PaymentsToAcquirePropertyPlantAndEquipment": _flow_entries(CAPEX, "ytd"),
        "ShareBasedCompensation": _flow_entries(SBC, "ytd"),
        "DepreciationDepletionAndAmortization": _flow_entries(DA, "ytd"),
        "Assets": _instant_entries(ASSETS), "Liabilities": _instant_entries(LIAB), "StockholdersEquity": _instant_entries(EQUITY),
        "CashAndCashEquivalentsAtCarryingValue": _instant_entries(CASH), "AssetsCurrent": _instant_entries(CUR_A),
        "LiabilitiesCurrent": _instant_entries(CUR_L), "LongTermDebtNoncurrent": _instant_entries(LTD), "Goodwill": _instant_entries(GOODWILL),
    }
    facts = {"cik": 999, "entityName": "Fixture Co", "facts": {"us-gaap": {k: {"units": {"USD": v}} for k, v in us.items()}, "dei": {}}}
    facts["facts"]["us-gaap"]["WeightedAverageNumberOfDilutedSharesOutstanding"] = {"units": {"shares": _per_share_entries(SH, "shares")}}
    facts["facts"]["us-gaap"]["WeightedAverageNumberOfSharesOutstandingBasic"] = {"units": {"shares": _per_share_entries(SH, "shares")}}
    facts["facts"]["us-gaap"]["EarningsPerShareDiluted"] = {"units": {"USD/shares": _per_share_entries(EPS, "USD/shares")}}
    facts["facts"]["us-gaap"]["EarningsPerShareBasic"] = {"units": {"USD/shares": _per_share_entries(EPS, "USD/shares")}}
    facts["facts"]["us-gaap"]["CommonStockSharesOutstanding"] = {"units": {"shares": _instant_entries(SHARES_OUT)}}
    return facts


def line(st, stmt, key):
    return next((l for l in st[stmt] if l["key"] == key), None)


def approx(a, b, tol=1e-9):
    return a is not None and b is not None and abs(a - b) <= tol


# ---------------------------------------------------------------- 1. assembly
def test_line_assembly():
    periods, st, currency, warnings = S.build_statements(make_facts(), [])
    # the fixture models no operating-expense lines, so the one warning is the opex-gap note (KR's custom OG&A case)
    assert currency == "USD" and [w for w in warnings if not w.startswith("income statement:")] == [], warnings
    assert len(warnings) == 1 and "explain 580 of the 1,010" in warnings[0], warnings
    assert [p["label"] for p in periods["annual"]] == ["FY2024", "FY2025"]
    assert [p["end"] for p in periods["annual"]] == ["2024-12-31", "2025-12-31"]
    assert [p["filed"] for p in periods["annual"]] == ["2025-02-20", "2026-02-19"]
    assert [p["end"] for p in periods["quarterly"]] == ALL_ENDS
    assert [p["label"] for p in periods["quarterly"]][:5] == ["Q1 FY2024", "Q2 FY2024", "Q3 FY2024", "Q4 FY2024", "Q1 FY2025"]
    assert periods["quarterly"][0]["fy_start"] == "2024-01-01" and periods["quarterly"][0]["filed"] == "2024-05-01"
    assert periods["ttm"] == {"end": "2026-06-30", "quarters": ["2025-09-30", "2025-12-31", "2026-03-31", "2026-06-30"]}
    # every emitted line has the contract shape and arrays of the period lengths
    for stmt, lines in st.items():
        assert stmt in ("income", "balance", "cashflow", "metrics") and lines
        for l in lines:
            for k in ("key", "label", "level", "total", "unit", "annual", "quarterly", "ttm", "growth_annual", "growth_quarterly", "derived_quarterly", "tags"):
                assert k in l, (stmt, l.get("key"), k)
            assert len(l["annual"]) == 2 and len(l["quarterly"]) == 10 and len(l["growth_annual"]) == 2 and len(l["growth_quarterly"]) == 10
            assert len(l["derived_quarterly"]) == 10 and all(isinstance(x, bool) for x in l["derived_quarterly"])
            assert l["unit"] in ("money", "shares", "per_share", "ratio", "pct") and l["level"] in (0, 1, 2) and isinstance(l["total"], bool)
            assert any(S._num(v) for v in l["annual"] + l["quarterly"] + [l["ttm"]]), l["key"]
    # the line order follows the spec, with only the lines that have values
    assert [l["key"] for l in st["income"]][:3] == ["revenue", "cost_of_revenue", "operating_income"]
    assert line(st, "income", "rnd") is None and line(st, "balance", "inventory") is None
    # direct 3-month income facts; Q4 = FY − 9M, flagged
    rev = line(st, "income", "revenue")
    assert rev["annual"] == [1000, 1200] and rev["total"] is True and rev["level"] == 0
    assert rev["quarterly"] == [220, 240, 260, 280, 270, 290, 310, 330, 350, 370]
    assert rev["derived_quarterly"] == [False, False, False, True, False, False, False, True, False, False]
    assert rev["tags"] == ["RevenueFromContractWithCustomerExcludingAssessedTax"]
    # YTD-only cash-flow facts: Q1 is the YTD leg itself (not derived), Q2–Q4 are differences (derived)
    ocf = line(st, "cashflow", "ocf")
    assert ocf["annual"] == [150, 200] and ocf["quarterly"] == [30, 35, 40, 45, 40, 45, 50, 65, 60, 65] and ocf["cf_sign"] == 1
    assert ocf["derived_quarterly"] == [False, True, True, True, False, True, True, True, False, True]
    capex = line(st, "cashflow", "capex")
    assert capex["quarterly"] == [5, 5, 5, 5, 6, 6, 6, 6, 7, 7] and capex["cf_sign"] == -1
    # balance-sheet instants: FY end annual, quarter-end quarterly, never derived, ttm = latest
    ta = line(st, "balance", "total_assets")
    assert ta["annual"] == [ASSETS["2024-12-31"], ASSETS["2025-12-31"]] and ta["quarterly"] == [ASSETS[e] for e in ALL_ENDS]
    assert ta["derived_quarterly"] == [False] * 10 and ta["ttm"] == ASSETS["2026-06-30"]
    # Q4 BASIC weighted shares are DAY-weighted: (D_FY x FY - sum d_i x Q_i) / d_4 with d = 89 / 91 / 92 / 92 days in 2025
    shb = line(st, "income", "shares_basic")
    q4_2025 = (364 * 98 - 89 * 99 - 91 * 98 - 92 * 97) / 92
    assert shb["quarterly"][3] == 100 and approx(shb["quarterly"][7], q4_2025) and 98.0 < q4_2025 < 98.1
    assert shb["derived_quarterly"][3] is True and shb["derived_quarterly"][7] is True and shb["derived_quarterly"][2] is False
    # a DILUTED count has no such identity: a profitable Q4 stays blank (a loss Q4 takes the basic count: test_q4_diluted_and_eps)
    sh = line(st, "income", "shares_diluted")
    assert sh["quarterly"][3] is None and sh["quarterly"][7] is None and sh["annual"] == [100, 98] and sh["unit"] == "shares"
    # Q4 EPS = FY EPS − the three filed quarters (plain arithmetic on filed per-share figures), flagged
    eps = line(st, "income", "eps_diluted")
    assert eps["quarterly"][:3] == [0.20, 0.25, 0.25] and approx(eps["quarterly"][3], 1.00 - 0.70) and eps["derived_quarterly"][3] is True
    assert approx(eps["quarterly"][7], 1.53 - 1.07) and eps["derived_quarterly"][7] is True and eps["annual"] == [1.00, 1.53]
    assert eps["unit"] == "per_share" and approx(eps["ttm"], 0.41 + 0.46 + 0.52 + 0.58)
    # shares outstanding (period end) is a metric instant
    so = line(st, "metrics", "shares_outstanding")
    assert so["quarterly"] == [SHARES_OUT[e] for e in ALL_ENDS] and so["ttm"] == SHARES_OUT["2026-06-30"] and so["unit"] == "shares"


# ---------------------------------------------------------------- 2. growth
def test_growth_arrays():
    periods, st, _, _ = S.build_statements(make_facts(), [])
    rev = line(st, "income", "revenue")
    assert rev["growth_annual"][0] is None and approx(rev["growth_annual"][1], 0.2)
    assert rev["growth_quarterly"][:4] == [None] * 4
    assert approx(rev["growth_quarterly"][4], 270 / 220 - 1) and approx(rev["growth_quarterly"][9], 370 / 290 - 1)
    ni = line(st, "income", "net_income")
    assert approx(ni["growth_annual"][1], 0.5) and approx(ni["growth_quarterly"][7], 45 / 30 - 1)
    # ratio / pct lines carry no growth
    for key in ("operating_margin", "current_ratio", "roe"):
        m = line(st, "metrics", key)
        assert m is not None and m["growth_annual"] == [None, None] and m["growth_quarterly"] == [None] * 10, key
    # a non-positive base gives null; a missing side gives null; non-consecutive fiscal years give null
    g = S.growth_arrays([-5, 10, 12], ["2023-12-31", "2024-12-31", "2025-12-31"], True)
    assert g[:2] == [None, None] and approx(g[2], 0.2)
    assert S.growth_arrays([10, None, 12], ["2023-12-31", "2024-12-31", "2025-12-31"], True) == [None, None, None]
    assert S.growth_arrays([10, 12], ["2022-12-31", "2025-12-31"], True) == [None, None]
    g = S.growth_arrays([10, 11, 12], ["2024-06-30", "2024-09-30", "2025-06-30"], False)
    assert g[:2] == [None, None] and approx(g[2], 0.2)


# ---------------------------------------------------------------- 3. TTM
def test_ttm_rule():
    periods, st, _, _ = S.build_statements(make_facts(), [])
    assert line(st, "income", "revenue")["ttm"] == 310 + 330 + 350 + 370
    assert line(st, "cashflow", "ocf")["ttm"] == 50 + 65 + 60 + 65
    assert line(st, "cashflow", "capex")["ttm"] == 26 and line(st, "cashflow", "sbc")["ttm"] == 12
    assert line(st, "balance", "cash")["ttm"] == CASH["2026-06-30"]
    sh = line(st, "income", "shares_basic")  # basic: its Q4 is derived (a diluted Q4 only in a loss quarter)
    assert 95 < sh["ttm"] < 98  # duration-weighted average of 97, 98, 96, 95
    # the unit function: null unless all four are present and consecutive
    ends = ["2025-03-31", "2025-06-30", "2025-09-30", "2025-12-31"]
    assert S.ttm_of([1, 2, 3, 4], ends, "money", "flow", ends) == 10
    assert S.ttm_of([1, None, 3, 4], ends, "money", "flow", ends) is None
    assert S.ttm_of([1, 2, 3, 4], ends, "money", "flow", None) is None
    assert S.ttm_of([1, 2, 3, 4], ends, "money", "instant", ends) == 4
    assert S.quarters_consecutive(ends) and not S.quarters_consecutive(["2025-03-31", "2025-06-30", "2025-12-31", "2026-03-31"])
    # a gap in the quarters (no Q3 FY2025 facts at all) → Q4 FY2025 is not derivable either (no 9M leg; only the
    # balance-sheet instant carries that date, and one core line is not a period) → the last four quarters are
    # Q1'25, Q2'25, Q1'26, Q2'26: not consecutive → no TTM for flows; the balance-sheet 'ttm' (latest instant) stays
    facts = make_facts()
    for tag, d in facts["facts"]["us-gaap"].items():
        for unit, es in d["units"].items():
            d["units"][unit] = [e for e in es if e["end"] != "2025-09-30"]
    periods2, st2, _, warn2 = S.build_statements(facts, [])
    assert periods2["ttm"] is None and any(w.startswith("ttm:") for w in warn2), warn2
    qe = [p["end"] for p in periods2["quarterly"]]
    assert "2025-09-30" not in qe and "2025-12-31" not in qe and qe[-2:] == ["2026-03-31", "2026-06-30"]
    rev2 = line(st2, "income", "revenue")
    assert rev2["ttm"] is None and rev2["annual"] == [1000, 1200]  # the annual column is untouched
    assert line(st2, "balance", "total_assets")["ttm"] == ASSETS["2026-06-30"]
    assert line(st2, "cashflow", "fcf")["ttm"] is None and line(st2, "cashflow", "ocf")["ttm"] is None


# ---------------------------------------------------------------- 4. derived lines
def test_derived_lines():
    periods, st, _, _ = S.build_statements(make_facts(), [])
    ebitda = line(st, "income", "ebitda")
    assert ebitda["annual"] == [150 + 40, 190 + 44] and ebitda["quarterly"][9] == 65 + 12 and ebitda["ttm"] == (50 + 55 + 60 + 65) + (11 + 11 + 12 + 12)
    # a derived line's quarter is derived when an input quarter is (D&A is YTD-only in the fixture: Q2-Q4 are differences)
    assert ebitda["derived_quarterly"] == line(st, "cashflow", "da")["derived_quarterly"] == [False, True, True, True, False, True, True, True, False, True]
    assert ebitda["tags"] == [] and ebitda["total"] is True
    assert line(st, "cashflow", "fcf")["derived_quarterly"] == line(st, "cashflow", "ocf")["derived_quarterly"]
    assert line(st, "metrics", "operating_margin")["derived_quarterly"] == line(st, "income", "revenue")["derived_quarterly"]  # Q4s
    fcf = line(st, "cashflow", "fcf")
    assert fcf["annual"] == [150 - 20, 200 - 24] and fcf["ttm"] == 240 - 26 and fcf["cf_sign"] == 1
    oe = line(st, "cashflow", "owner_earnings")
    assert oe["annual"] == [150 - 20 - 8, 200 - 24 - 12] and oe["ttm"] == 240 - 26 - 12
    gp = line(st, "income", "gross_profit")
    assert gp is None  # never synthesised from revenue − cost of revenue
    assert line(st, "income", "total_opex") is None and line(st, "balance", "total_liabilities_and_equity") is None
    # metrics: total_debt from the one debt line (no current debt filed → 0 added), net cash = cash + 0 (no ST investments ever filed) − debt
    td = line(st, "metrics", "total_debt")
    assert td["annual"] == [200, 200] and td["ttm"] == 200
    nc = line(st, "metrics", "net_cash")
    assert nc["annual"] == [CASH["2024-12-31"] - 200, CASH["2025-12-31"] - 200] and nc["ttm"] == CASH["2026-06-30"] - 200
    wc = line(st, "metrics", "working_capital")
    assert wc["ttm"] == CUR_A["2026-06-30"] - CUR_L["2026-06-30"]
    bvps = line(st, "metrics", "book_value_per_share")
    assert approx(bvps["ttm"], EQUITY["2026-06-30"] / SHARES_OUT["2026-06-30"]) and bvps["unit"] == "per_share"
    tbv = line(st, "metrics", "tangible_book_value")
    assert tbv["ttm"] == EQUITY["2026-06-30"] - 50  # goodwill filed, intangibles never filed → 0
    gm = line(st, "metrics", "gross_margin")
    assert gm is None  # no gross profit line → no margin (not revenue − cogs)
    om = line(st, "metrics", "operating_margin")
    assert approx(om["annual"][1], 190 / 1200) and approx(om["ttm"], 230 / 1360) and om["unit"] == "pct"
    fm = line(st, "metrics", "fcf_margin")
    assert approx(fm["annual"][0], 130 / 1000)
    fps = line(st, "metrics", "fcf_per_share")
    assert approx(fps["annual"][1], 176 / 98)
    roe = line(st, "metrics", "roe")
    assert approx(roe["annual"][1], 150 / EQUITY["2025-12-31"])
    assert roe["quarterly"][:3] == [None] * 3 and approx(roe["quarterly"][3], 100 / EQUITY["2024-12-31"])  # trailing-four NI on quarterly columns
    assert approx(roe["ttm"], 190 / EQUITY["2026-06-30"])
    cr = line(st, "metrics", "current_ratio")
    assert approx(cr["ttm"], CUR_A["2026-06-30"] / CUR_L["2026-06-30"]) and cr["unit"] == "ratio"
    de = line(st, "metrics", "debt_to_equity")
    assert approx(de["ttm"], 200 / EQUITY["2026-06-30"])
    # a derived line is computed only from lines present in the same period: drop FY2024's D&A → ebitda FY2024 null, FY2025 intact
    facts = make_facts()
    d = facts["facts"]["us-gaap"]["DepreciationDepletionAndAmortization"]["units"]["USD"]
    facts["facts"]["us-gaap"]["DepreciationDepletionAndAmortization"]["units"]["USD"] = [e for e in d if not e["end"].startswith("2024")]
    _, st3, _, _ = S.build_statements(facts, [])
    e3 = line(st3, "income", "ebitda")
    assert e3["annual"] == [None, 234] and e3["quarterly"][:4] == [None] * 4 and e3["quarterly"][9] == 77
    # a filed component missing in ONE period gives null there (goodwill filed elsewhere but not at 2026-06-30)
    facts = make_facts()
    g = facts["facts"]["us-gaap"]["Goodwill"]["units"]["USD"]
    facts["facts"]["us-gaap"]["Goodwill"]["units"]["USD"] = [e for e in g if e["end"] != "2026-06-30"]
    _, st4, _, _ = S.build_statements(facts, [])
    assert line(st4, "metrics", "tangible_book_value")["ttm"] is None and line(st4, "metrics", "tangible_book_value")["annual"][1] == EQUITY["2025-12-31"] - 50
    # derive_value directly: the total_debt rule with an aggregate current-debt tag, and DebtCurrent never double counted
    vals = {"long_term_debt": 100, "short_term_debt": 10, "current_lt_debt": 5, "debt_current_agg": None, "debt_total_agg": None}
    assert S.derive_value("total_debt", vals.get, lambda k: True) == 115
    vals["debt_current_agg"] = 12
    assert S.derive_value("total_debt", vals.get, lambda k: True) == 112
    assert S.derive_value("total_debt", {"debt_total_agg": 130, "short_term_debt": 10}.get, lambda k: True, tag_of=lambda k: "DebtCurrent") == 130
    assert S.derive_value("total_debt", {"debt_total_agg": 130, "short_term_debt": 10}.get, lambda k: True, tag_of=lambda k: "CommercialPaper") == 140
    assert S.derive_value("fcf", {"ocf": 10}.get, lambda k: True) is None
    assert S.derive_value("net_cash", {"cash": 10, "total_debt": 4}.get, lambda k: k != "short_term_investments") == 6
    assert S.derive_value("net_cash", {"cash": 10, "total_debt": 4}.get, lambda k: True) is None


# ---------------------------------------------------------------- 5. skip rule (cached payloads, no network)
def test_submissions_skip_rule():
    sub = {"cik": "999", "fiscalYearEnd": "1231", "filings": {"recent": {
        "form": ["8-K", "10-Q", "10-K", "10-Q"], "filingDate": ["2026-09-01", "2026-08-01", "2026-02-19", "2026-05-01"],
        "reportDate": ["2026-08-30", "2026-06-30", "2025-12-31", "2026-03-31"]}}}
    assert S.latest_filing(sub) == {"form": "10-Q", "filed": "2026-08-01", "period": "2026-06-30"}
    assert S.latest_filing({"filings": {"recent": {"form": ["8-K"], "filingDate": ["2026-09-01"], "reportDate": ["x"]}}}) is None
    tmp = tempfile.mkdtemp(prefix="statements_test_")
    old_base = S.BASE
    try:
        cache = os.path.join(tmp, "cache")
        os.makedirs(cache)
        os.makedirs(os.path.join(tmp, "FIX"))
        with open(os.path.join(cache, "FIX.sub.json"), "w", encoding="utf-8") as f:
            json.dump(sub, f)
        with open(os.path.join(cache, "FIX.facts.json"), "w", encoding="utf-8") as f:
            json.dump(make_facts(), f)
        S.BASE = tmp
        s1, sk1 = S.run_one("FIX", cik=999, write=True, cache=cache)
        assert sk1 is False and s1["annual_years"] == 2 and s1["quarters"] == 10 and s1["first_fy"] == "FY2024"
        out = json.load(open(os.path.join(tmp, "FIX", "statements.json"), encoding="utf-8"))
        for k in ("ticker", "cik", "as_of", "currency", "fiscal_year_end_mmdd", "source", "periods", "statements", "warnings", "latest_filed", "schema_version"):
            assert k in out, k
        assert out["source"] == "SEC EDGAR companyfacts (filing-direct)" and out["cik"] == 999 and out["fiscal_year_end_mmdd"] == "1231"
        assert out["latest_filed"] == {"form": "10-Q", "filed": "2026-08-01", "period": "2026-06-30"} and out["covered_through"] == "2026-06-30"
        assert [w for w in out["warnings"] if not w.startswith("income statement:")] == [] and datetime.date.fromisoformat(out["as_of"])
        json.dumps(out, allow_nan=False)
        # same newest filing → skipped without touching the facts (remove the cached facts to prove it)
        os.remove(os.path.join(cache, "FIX.facts.json"))
        s2, sk2 = S.run_one("FIX", cik=999, write=True, cache=cache)
        assert sk2 is True and s2["skipped"] is True
        # --force re-reads the facts; a newer filing re-reads too
        with open(os.path.join(cache, "FIX.facts.json"), "w", encoding="utf-8") as f:
            json.dump(make_facts(), f)
        assert S.run_one("FIX", cik=999, write=False, cache=cache, force=True)[1] is False
        sub2 = copy.deepcopy(sub)
        sub2["filings"]["recent"]["form"].append("10-Q")
        sub2["filings"]["recent"]["filingDate"].append("2026-11-01")
        sub2["filings"]["recent"]["reportDate"].append("2026-09-30")
        with open(os.path.join(cache, "FIX.sub.json"), "w", encoding="utf-8") as f:
            json.dump(sub2, f)
        s3, sk3 = S.run_one("FIX", cik=999, write=False, cache=cache)
        assert sk3 is False and any("not yet in EDGAR companyfacts" in w for w in s3["warnings"]), s3["warnings"]
    finally:
        S.BASE = old_base
        shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------------- 6. build_site pass-through
def test_build_site_passthrough():
    tmp = tempfile.mkdtemp(prefix="statements_site_")
    try:
        os.makedirs(os.path.join(tmp, "_system"))
        shutil.copytree(os.path.join(BASE, "APP"), os.path.join(tmp, "APP"))
        # the gitignored caches (Nasdaq prices / Street / live returns) are absent from a fresh clone: never read them —
        # the copy drops whatever this checkout has and the test writes its own prices.json below
        for f in ("prices.json", "live.json", "street.json"):
            if os.path.exists(os.path.join(tmp, "APP", f)):
                os.remove(os.path.join(tmp, "APP", f))
        for f in ("queue.json", "overrides_registry.json"):
            shutil.copy(os.path.join(SYS, f), os.path.join(tmp, "_system", f))
        with open(os.path.join(tmp, "_system", "watchlist.json"), "w", encoding="utf-8") as f:
            json.dump({"tickers": [{"ticker": "zs", "in_universe": True, "name": "Zscaler"}, {"ticker": "META", "in_universe": False, "name": None},
                                   "APP", {"ticker": "ZS"}, {"ticker": " "}, 5]}, f)
        periods, st, currency, warnings = S.build_statements(make_facts(), [])
        stmts = {"ticker": "APP", "cik": 1751008, "as_of": "2026-10-15", "currency": currency, "fiscal_year_end_mmdd": "1231", "source": S.SOURCE,
                 "schema_version": S.SCHEMA_VERSION, "latest_filed": {"form": "10-Q", "filed": "2026-08-05", "period": "2026-06-30"},
                 "periods": periods, "statements": st, "warnings": warnings}
        folder = os.path.join(tmp, "APP")
        with open(os.path.join(folder, "statements.json"), "w", encoding="utf-8") as f:
            json.dump(stmts, f)
        # profile.json as profile.py writes it since 2026-10-16: SEC-derived About / filings only (the Street block and
        # market data live in the gitignored street.json, absent here)
        profile = {"ticker": "APP", "as_of": "2026-10-15", "about": {"description": "Fixture about text.", "website": "https://example.com"}, "filings": []}
        with open(os.path.join(folder, "profile.json"), "w", encoding="utf-8") as f:
            json.dump(profile, f)
        pr = {"ticker": "APP", "source": "fixture", "as_of": "2026-10-14", "currency": "USD", "stats": {}, "weekly": [], "daily_1y": []}
        pr["intraday"] = {"session_date": "2026-10-14", "prev_close": 272.28, "last": 257.14, "bars": [[240, 271.9], [570, 270.1], [1195, 257.14]]}
        pr["sessions_5d"] = [{"session_date": "2026-10-13", "prev_close": 270.0, "bars": [[570, 271.0]]}, {"session_date": "2026-10-14", "prev_close": 272.28, "bars": [[570, 270.1]]}]
        pr["warnings"] = []
        with open(os.path.join(folder, "prices.json"), "w", encoding="utf-8") as f:
            json.dump(pr, f)
        site = os.path.join(tmp, "_daily", "site")
        res = B.build(base=tmp, site_dir=site, only=["APP"], quiet=True)
        assert res["written"] == ["APP"] and res["statements_written"] == ["APP"] and res["statements_removed"] == []
        copy_path = os.path.join(site, "data", "APP.statements.json")
        assert os.path.exists(copy_path)
        with open(copy_path, encoding="utf-8") as f:
            served = json.load(f)
        assert served == json.loads(json.dumps(stmts))  # verbatim copy
        rec = B.jload(os.path.join(site, "data", "APP.json"))
        assert "statements" not in rec and rec["row"]["has"]["statements"] is True and rec["row"]["has"]["profile"] is True
        # every profile.json key verbatim; no street.json → the Street / market keys build_site adds (if any) are null
        assert all(rec["profile"].get(k) == v for k, v in profile.items()), rec["profile"]
        assert rec["profile"].get("street") is None and rec["profile"].get("market") is None
        assert rec["prices"]["intraday"] == pr["intraday"] and rec["prices"]["sessions_5d"] == pr["sessions_5d"] and rec["prices"]["warnings"] == []
        index = B.jload(os.path.join(site, "index.json"))
        row = next(r for r in index if r["ticker"] == "APP")
        assert row["has"]["statements"] is True and row["has"]["profile"] is True and row["watchlist"] is True
        meta = B.jload(os.path.join(site, "meta.json"))
        assert meta["watchlist"] == ["ZS", "META", "APP"] and meta["watchlist_outside"] == ["META"]  # file order, deduped, blanks dropped
        assert meta["watchlist_entries"][0] == {"ticker": "ZS", "in_universe": True, "name": "Zscaler"}
        assert meta["counts"]["statements"] == 1 and meta["counts"]["profiles"] == 1 and meta["counts"]["watchlist"] == 1
        assert any(n.startswith("statements:") for n in meta["notes"])
        # the attachment: sessions_5d dropped, intraday + profile kept, no statements anywhere in the records
        att = B.build(base=tmp, site_dir=site, only=["APP"], quiet=True, attachment=True, top=5)
        with open(att["attachment"][0], encoding="utf-8") as f:
            doc = f.read()
        start = doc.index("<script>window.SITE_DATA=") + len("<script>window.SITE_DATA=")
        data = json.loads(doc[start:doc.index(";</script>", start)])
        arec = data["records"]["APP"]
        assert "sessions_5d" not in arec["prices"] and "daily_1y" not in arec["prices"] and arec["prices"]["intraday"] == pr["intraday"]
        assert arec["profile"] == rec["profile"] and "statements" not in arec and data["meta"]["watchlist_outside"] == ["META"]
        # unchanged folder → the record is skipped and the copy stays
        res2 = B.build(base=tmp, site_dir=site, only=["APP"], quiet=True)
        assert res2["written"] == [] and res2["skipped"] == ["APP"] and res2["statements_written"] == [] and os.path.exists(copy_path)
        # only the copy missing → restored without rebuilding the record
        os.remove(copy_path)
        res3 = B.build(base=tmp, site_dir=site, only=["APP"], quiet=True)
        assert res3["written"] == [] and res3["statements_written"] == ["APP"] and os.path.exists(copy_path)
        # the folder's statements.json removed → the record rebuilds (file list changed), the copy goes, has.statements false
        os.remove(os.path.join(folder, "statements.json"))
        res4 = B.build(base=tmp, site_dir=site, only=["APP"], quiet=True)
        assert res4["written"] == ["APP"] and res4["statements_removed"] == ["APP"] and not os.path.exists(copy_path)
        assert B.jload(os.path.join(site, "data", "APP.json"))["row"]["has"]["statements"] is False
        # a malformed statements.json renders as absent; a NaN inside a valid one becomes null in the copy
        with open(os.path.join(folder, "statements.json"), "w", encoding="utf-8") as f:
            f.write("[1, 2]")
        res5 = B.build(base=tmp, site_dir=site, only=["APP"], quiet=True)
        assert res5["written"] == ["APP"] and not os.path.exists(copy_path) and B.jload(os.path.join(site, "data", "APP.json"))["row"]["has"]["statements"] is False
        bad = json.loads(json.dumps(stmts))
        bad["statements"]["income"][0]["annual"][0] = float("nan")
        with open(os.path.join(folder, "statements.json"), "w", encoding="utf-8") as f:
            json.dump(bad, f)
        B.build(base=tmp, site_dir=site, only=["APP"], quiet=True)
        with open(copy_path, encoding="utf-8") as f:
            text = f.read()
        assert "NaN" not in text and json.loads(text)["statements"]["income"][0]["annual"][0] is None
        # the folder no longer qualifies → record AND copy removed; an orphan copy is removed too
        with open(os.path.join(site, "data", "ORPHAN.statements.json"), "w", encoding="utf-8") as f:
            f.write("{}")
        os.remove(os.path.join(folder, "score.json"))
        res6 = B.build(base=tmp, site_dir=site, only=["APP"], quiet=True)
        assert res6["removed"] == ["APP"] and sorted(res6["statements_removed"]) == ["APP", "ORPHAN"]
        assert not os.path.exists(copy_path) and not os.path.exists(os.path.join(site, "data", "ORPHAN.statements.json"))
        # no watchlist file → the universe.csv column (nothing outside)
        os.remove(os.path.join(tmp, "_system", "watchlist.json"))
        wl, outside, entries = B.load_watchlist(tmp)
        assert wl == [] and outside == [] and entries == []  # no universe.csv in the temp base either
        shutil.copy(os.path.join(SYS, "universe.csv"), os.path.join(tmp, "_system", "universe.csv"))
        wl, outside, entries = B.load_watchlist(tmp)
        assert wl and outside == [] and all(e["in_universe"] for e in entries) and wl == [e["ticker"] for e in entries]
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------------- 7. review round 2026-10-15: filing generations, units, 6-K filers
def _fact(start, end, val, form, fp, fy, filed, accn, unit=None):
    return {"start": start, "end": end, "val": val, "fy": fy, "fp": fp, "form": form, "filed": filed, "accn": accn}


def test_q4_from_same_filing_generation():
    """APP's case: FY2024 operating income restated in the FY2025 10-K (filed 2026-02-19) while the nine-month 2024 leg was
    last re-filed UNCHANGED in the Q3 2025 10-Q — Q4 FY2024 must be the original pair (150 − 105 = 45), never 180 − 105."""
    facts = make_facts()
    es = facts["facts"]["us-gaap"]["OperatingIncomeLoss"]["units"]["USD"]
    es.append(_fact("2024-01-01", "2024-12-31", 180, "10-K", "FY", 2025, "2026-02-19", "acc-2025-12-31"))   # restated comparative
    es.append(_fact("2024-01-01", "2024-09-30", 105, "10-Q", "Q3", 2025, "2025-11-01", "acc-2025-09-30"))  # 9M re-filed unchanged
    _, st, _, warnings = S.build_statements(facts, [])
    oi = line(st, "income", "operating_income")
    assert oi["annual"] == [180, 190], oi["annual"]  # the annual column is the latest filing (restated), as the contract says
    assert oi["quarterly"][:4] == [30, 35, 40, 45] and oi["derived_quarterly"][3] is True, oi["quarterly"]
    # the four quarters (150) no longer sum to the restated year (180): flagged, growth across the break blanked
    assert oi["basis_break_quarterly"] == [True] * 4 + [False] * 6
    assert oi["growth_quarterly"][4:8] == [None] * 4 and S._num(oi["growth_quarterly"][8]), oi["growth_quarterly"]
    assert any(w.startswith("basis break") and "operating_income" in w and "2024-12-31" in w for w in warnings), warnings
    assert "basis_break_quarterly" not in line(st, "income", "revenue"), "an unaffected line carries no flag array"
    # when the nine-month comparative was ALSO restated the new pair is consistent: Q4 = 180 − 120 = 60
    facts2 = make_facts()
    es2 = facts2["facts"]["us-gaap"]["OperatingIncomeLoss"]["units"]["USD"]
    es2.append(_fact("2024-01-01", "2024-12-31", 180, "10-K", "FY", 2025, "2026-02-19", "acc-2025-12-31"))
    es2.append(_fact("2024-01-01", "2024-09-30", 120, "10-Q", "Q3", 2025, "2025-11-01", "acc-2025-09-30"))
    _, st2, _, _ = S.build_statements(facts2, [])
    assert line(st2, "income", "operating_income")["quarterly"][3] == 60
    # pair_generations directly: the longer leg is the first filing on or after the shorter leg's last filing
    lg, sh = S.pair_generations([("2025-02-20", 150, "a", "10-K"), ("2026-02-19", 180, "b", "10-K")], [("2024-11-01", 105, "c", "10-Q")])
    assert lg[1] == 150 and sh[1] == 105
    lg, sh = S.pair_generations([("2025-02-20", 150, "a", "10-K")], [("2024-11-01", 105, "c", "10-Q"), ("2025-11-01", 105, "d", "10-Q")])
    assert lg[1] == 150  # no filing after the re-filed leg yet: the last one before it


def test_units_never_mixed():
    """JD's case: a fiscal-year leg in USD (20-F convenience translation) must never meet a nine-month leg in CNY."""
    facts = make_facts()
    us = facts["facts"]["us-gaap"]["NetCashProvidedByUsedInOperatingActivities"]["units"]
    us["USD"] = [e for e in us["USD"] if not (e["end"] == "2025-09-30")]
    us["CNY"] = [_fact("2025-01-01", "2025-09-30", 1000, "10-Q", "Q3", 2025, "2025-11-01", "acc-2025-09-30"),
                 _fact("2025-01-01", "2025-12-31", 1400, "10-K", "FY", 2025, "2026-02-19", "acc-2025-12-31")]  # a convenience translation
    _, st, currency, warnings = S.build_statements(facts, [])
    ocf = line(st, "cashflow", "ocf")
    assert currency == "USD" and ocf["quarterly"][6] is None and ocf["quarterly"][7] is None, ocf["quarterly"]  # no Q3, no Q4 = FY − CNY
    assert ocf["quarterly"][:6] == [30, 35, 40, 45, 40, 45]
    assert any("also files core facts in CNY" in w for w in warnings), warnings
    # the file's money unit is the majority unit of the core FY facts: all-CNY facts → CNY, shown as filed
    facts2 = make_facts()
    for tag, d in facts2["facts"]["us-gaap"].items():
        if "USD" in d["units"]:
            d["units"]["CNY"] = d["units"].pop("USD")
    _, st2, currency2, warnings2 = S.build_statements(facts2, [])
    assert currency2 == "CNY" and line(st2, "income", "revenue")["annual"] == [1000, 1200] and any("filed in CNY" in w for w in warnings2)


def test_six_k_only_filer_needs_full_fiscal_years():
    facts = make_facts()
    for d in facts["facts"]["us-gaap"].values():
        for es in d["units"].values():
            for e in es:
                if e["form"] == "10-Q":
                    e["form"] = "6-K"
    periods, st, _, warnings = S.build_statements(facts, [])
    assert [p["end"] for p in periods["quarterly"]] == ALL_ENDS[:8], periods["quarterly"]  # the two 2026 quarters have no full year
    assert any("6-K only" in w and "2 quarter(s)" in w for w in warnings), warnings


# ---------------------------------------------------------------- 8. revenue per period, bank provision, other non-operating, KR lines
def test_revenue_total_per_period_and_plausibility():
    facts = make_facts()
    us = facts["facts"]["us-gaap"]
    # IRM's case: the filer's own Revenues total exceeds the contract line by >5% for FY2024 only
    us["Revenues"] = {"units": {"USD": [_fact("2024-01-01", "2024-12-31", 1300, "10-K", "FY", 2024, "2025-02-20", "acc-2024-12-31")]}}
    _, st, _, warnings = S.build_statements(facts, [])
    rev = line(st, "income", "revenue")
    assert rev["annual"] == [1300, 1200] and sorted(rev["tags"]) == ["RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues"]
    assert any(w.startswith("revenue basis") and "2024-12-31" in w and "1 period(s)" in w for w in warnings), warnings
    assert rev["basis_break_quarterly"][:4] == [True] * 4  # the quarters stayed on the contract basis: visible, not silent
    # HSY's case: the first-choice tag's FY fact disagrees with the four filed quarters while another tag agrees
    facts = make_facts()
    us = facts["facts"]["us-gaap"]
    for e in us["RevenueFromContractWithCustomerExcludingAssessedTax"]["units"]["USD"]:
        if e["fp"] == "FY" and e["end"] == "2025-12-31":
            e["val"] = 300  # a rounded note-level fact on the primary tag
    us["SalesRevenueNet"] = {"units": {"USD": [_fact("2025-01-01", "2025-12-31", 1200, "10-K", "FY", 2025, "2026-02-19", "acc-2025-12-31")]}}
    _, st, _, warnings = S.build_statements(facts, [])
    rev = line(st, "income", "revenue")
    assert rev["annual"] == [1000, 1200] and "SalesRevenueNet" in rev["tags"], (rev["annual"], rev["tags"])
    assert rev["quarterly"][7] is None  # the Q4 derived from the bogus year went negative and stays blank (SalesRevenueNet has no 9M leg)
    assert any("disagrees with the filed quarters" in w and "300" in w for w in warnings), warnings
    # the HSY shape itself: the rounded fact sits on a tag with NO quarters, the real series (year + quarters) on another
    facts = make_facts()
    us = facts["facts"]["us-gaap"]
    us["RevenueFromContractWithCustomerIncludingAssessedTax"] = us.pop("RevenueFromContractWithCustomerExcludingAssessedTax")
    us["SalesRevenueNet"] = {"units": {"USD": [_fact("2025-01-01", "2025-12-31", 300, "10-K", "FY", 2025, "2026-02-19", "acc-2025-12-31")]}}
    _, st, _, warnings = S.build_statements(facts, [])
    rev = line(st, "income", "revenue")
    assert rev["annual"] == [1000, 1200] and rev["quarterly"][4:8] == [270, 290, 310, 330] and rev["tags"] == ["RevenueFromContractWithCustomerIncludingAssessedTax"]
    # the tag order itself: SalesRevenueNet ranks ahead of Revenues (fundamentals.DUR is the source)
    assert S.REVENUE_TAGS.index("SalesRevenueNet") < S.REVENUE_TAGS.index("Revenues")


def _bank_facts():
    facts = make_facts()
    us = facts["facts"]["us-gaap"]
    NII = {2024: [50, 50, 50, 50], 2025: [55, 55, 55, 55], 2026: [60, 60]}
    NON = {2024: [20, 20, 20, 20], 2025: [22, 22, 22, 22], 2026: [24, 24]}
    LOANS = {2024: [10, 10, 10, 10], 2025: [12, 12, 12, 12], 2026: [14, 14]}
    OBS = {2024: [-2, 1, 0, 1], 2025: [0, 0, 0, 0], 2026: [-3, 1]}
    us["InterestIncomeExpenseNet"] = {"units": {"USD": _flow_entries(NII, "3m+ytd")}}
    us["NoninterestIncome"] = {"units": {"USD": _flow_entries(NON, "3m+ytd")}}
    us["FinancingReceivableExcludingAccruedInterestCreditLossExpenseReversal"] = {"units": {"USD": _flow_entries(LOANS, "ytd")}}
    us["OffBalanceSheetCreditLossLiabilityCreditLossExpenseReversal"] = {"units": {"USD": _flow_entries(OBS, "ytd")}}
    return facts


def test_bank_provision_components():
    """HBAN's case: no income-statement total is tagged — the loans component alone (250) is never shown; the two
    components are summed when both are filed (158), blank otherwise."""
    facts = _bank_facts()
    _, st, _, warnings = S.build_statements(facts, [])
    prov = line(st, "income", "provision_credit_losses")
    assert prov["annual"] == [40, 48] and prov["quarterly"][:4] == [8, 11, 10, 11] and prov["quarterly"][8] == 11 and prov["quarterly"][9] == 15
    assert prov["tags"] == ["FinancingReceivableExcludingAccruedInterestCreditLossExpenseReversal+OffBalanceSheetCreditLossLiabilityCreditLossExpenseReversal"]
    assert prov["derived_quarterly"][1] is True and any("provision for credit losses" in w for w in warnings), warnings
    rev = line(st, "income", "revenue")
    assert rev["annual"] == [280, 308] and rev["tags"] == ["InterestIncomeExpenseNet+NoninterestIncome"]
    assert line(st, "income", "interest_expense") is None  # bank shape
    # a filed total wins; a period with only the loans component is blank
    facts2 = _bank_facts()
    us = facts2["facts"]["us-gaap"]
    us["ProvisionForCreditLosses"] = {"units": {"USD": [_fact("2025-01-01", "2025-12-31", 47, "10-K", "FY", 2025, "2026-02-19", "acc-2025-12-31")]}}
    us["OffBalanceSheetCreditLossLiabilityCreditLossExpenseReversal"]["units"]["USD"] = [e for e in us["OffBalanceSheetCreditLossLiabilityCreditLossExpenseReversal"]["units"]["USD"] if e["end"] != "2024-12-31"]
    _, st2, _, _ = S.build_statements(facts2, [])
    prov2 = line(st2, "income", "provision_credit_losses")
    assert prov2["annual"] == [None, 47], prov2["annual"]


def test_other_nonoperating_reconciles_to_pretax():
    """APP's case: NonoperatingIncomeExpense is the whole non-operating section (interest inside) — shown as that total
    + interest expense − interest income when OI + total = pretax; kept when it is the face line; blank otherwise."""
    facts = make_facts()
    us = facts["facts"]["us-gaap"]
    # FY2024: OI 150, interest expense 25, nonop −20 (= −25 + 5), pretax 130 → the tag is the total → other = 5
    # FY2025: OI 190, interest expense 30, nonop 7 (the face "other"), pretax 167 → kept
    us["InterestExpense"] = {"units": {"USD": [_fact("2024-01-01", "2024-12-31", 25, "10-K", "FY", 2024, "2025-02-20", "acc-2024-12-31"),
                                               _fact("2025-01-01", "2025-12-31", 30, "10-K", "FY", 2025, "2026-02-19", "acc-2025-12-31")]}}
    us["NonoperatingIncomeExpense"] = {"units": {"USD": [_fact("2024-01-01", "2024-12-31", -20, "10-K", "FY", 2024, "2025-02-20", "acc-2024-12-31"),
                                                          _fact("2025-01-01", "2025-12-31", 7, "10-K", "FY", 2025, "2026-02-19", "acc-2025-12-31")]}}
    us["IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest"] = {"units": {"USD": [
        _fact("2024-01-01", "2024-12-31", 130, "10-K", "FY", 2024, "2025-02-20", "acc-2024-12-31"),
        _fact("2025-01-01", "2025-12-31", 167, "10-K", "FY", 2025, "2026-02-19", "acc-2025-12-31")]}}
    _, st, _, warnings = S.build_statements(facts, [])
    on = line(st, "income", "other_nonoperating")
    assert on["annual"] == [5, 7], on["annual"]
    assert "NonoperatingIncomeExpense+InterestExpense-InterestIncome" in on["tags"] and any(w.startswith("other non-operating") for w in warnings), warnings
    # neither reading reconciles → blank
    us["IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest"]["units"]["USD"][1]["val"] = 100
    _, st2, _, _ = S.build_statements(facts, [])
    assert line(st2, "income", "other_nonoperating")["annual"] == [5, None]
    # OtherNonoperatingIncomeExpense (the face line) ranks first and is never touched
    us["OtherNonoperatingIncomeExpense"] = {"units": {"USD": [_fact("2025-01-01", "2025-12-31", 9, "10-K", "FY", 2025, "2026-02-19", "acc-2025-12-31")]}}
    _, st3, _, _ = S.build_statements(facts, [])
    assert line(st3, "income", "other_nonoperating")["annual"] == [5, 9]


def test_kroger_lines():
    """Net interest expense tagged as income − expense is shown negated as 'Interest expense, net'; LIFO inventory =
    FIFO − reserve; a total-costs line only when no operating-expenses total exists."""
    facts = make_facts()
    us = facts["facts"]["us-gaap"]
    us["InterestIncomeExpenseNonoperatingNet"] = {"units": {"USD": [_fact("2024-01-01", "2024-12-31", -12, "10-K", "FY", 2024, "2025-02-20", "acc-2024-12-31"),
                                                                     _fact("2025-01-01", "2025-12-31", -14, "10-K", "FY", 2025, "2026-02-19", "acc-2025-12-31")]}}
    us["FIFOInventoryAmount"] = {"units": {"USD": _instant_entries({e: 90 for e in ALL_ENDS})}}
    us["InventoryLIFOReserve"] = {"units": {"USD": _instant_entries({e: 25 for e in ALL_ENDS})}}
    us["CostsAndExpenses"] = {"units": {"USD": _flow_entries({2024: [190, 205, 220, 235], 2025: [230, 245, 260, 275], 2026: [290, 305]}, "3m+ytd")}}
    _, st, _, warnings = S.build_statements(facts, [])
    ie = line(st, "income", "interest_expense")
    assert ie["annual"] == [12, 14] and ie["label"] == "Interest expense, net" and ie["tags"] == ["InterestIncomeExpenseNonoperatingNet"]
    inv = line(st, "balance", "inventory")
    assert inv["annual"] == [65, 65] and inv["ttm"] == 65 and inv["tags"] == ["FIFOInventoryAmount-InventoryLIFOReserve"]
    tc = line(st, "income", "total_costs")
    assert tc is not None and tc["annual"] == [850, 1010] and line(st, "income", "total_opex") is None
    assert not any(w.startswith("income statement:") for w in warnings), warnings  # the total-costs line explains the gap
    us["OperatingExpenses"] = {"units": {"USD": _flow_entries({2024: [80, 85, 90, 95], 2025: [100, 105, 110, 115], 2026: [120, 125]}, "3m+ytd")}}
    _, st2, _, _ = S.build_statements(facts, [])
    assert line(st2, "income", "total_costs") is None and line(st2, "income", "total_opex")["annual"] == [350, 430]
    # a filed InventoryNet ranks first; the difference fills only the periods it leaves empty
    us["InventoryNet"] = {"units": {"USD": _instant_entries({"2026-06-30": 70})}}
    _, st3, _, _ = S.build_statements(facts, [])
    assert line(st3, "balance", "inventory")["ttm"] == 70 and line(st3, "balance", "inventory")["annual"] == [65, 65]


# ---------------------------------------------------------------- 9. capex scoped per filing, long-term debt totals, splits, Q4 shares, skip rule
def test_capex_never_read_as_zero():
    """APP / EXR / CFG: a period whose filings carry no capex figure has NO free cash flow and NO owner's earnings —
    never FCF = OCF. The capex candidates cover the REIT / bank captions."""
    facts = make_facts()
    cap = facts["facts"]["us-gaap"]["PaymentsToAcquirePropertyPlantAndEquipment"]["units"]["USD"]
    facts["facts"]["us-gaap"]["PaymentsToAcquirePropertyPlantAndEquipment"]["units"]["USD"] = [e for e in cap if e["end"] < "2025-01-01"]
    _, st, _, warnings = S.build_statements(facts, [])
    capex, fcf, oe = line(st, "cashflow", "capex"), line(st, "cashflow", "fcf"), line(st, "cashflow", "owner_earnings")
    assert capex["annual"] == [20, None] and capex["quarterly"][4:] == [None] * 6 and capex["ttm"] is None
    assert fcf["annual"] == [130, None] and fcf["quarterly"][4:] == [None] * 6 and fcf["ttm"] is None, fcf
    assert oe["annual"] == [122, None] and line(st, "metrics", "fcf_margin")["annual"][1] is None
    assert any(w.startswith("capex: no capital-expenditure figure is filed for 6 period(s)") and "never read as zero" in w for w in warnings), warnings
    # EXR's case: the filer's capital spending is a real-estate development caption — it is the capex line
    facts = make_facts()
    us = facts["facts"]["us-gaap"]
    us["PaymentsToDevelopRealEstateAssets"] = us.pop("PaymentsToAcquirePropertyPlantAndEquipment")
    _, st, _, _ = S.build_statements(facts, [])
    assert line(st, "cashflow", "capex")["annual"] == [20, 24] and line(st, "cashflow", "capex")["tags"] == ["PaymentsToDevelopRealEstateAssets"]
    assert line(st, "cashflow", "fcf")["annual"] == [130, 176]
    for tag in ("PaymentsToAcquireRealEstate", "PaymentsForCapitalImprovements", "PaymentsToAcquireProductiveAssets", "PaymentsForProceedsFromProductiveAssets"):
        assert tag in [p[1] for p in S._pairs(S.CAPEX_TAGS)], tag
    # SBC is still read as 0 for a period whose cash-flow statement has no SBC line at all ...
    facts = make_facts()
    sbc = facts["facts"]["us-gaap"]["ShareBasedCompensation"]["units"]["USD"]
    facts["facts"]["us-gaap"]["ShareBasedCompensation"]["units"]["USD"] = [e for e in sbc if e["end"] < "2025-01-01"]
    _, st, _, warnings = S.build_statements(facts, [])
    assert line(st, "cashflow", "owner_earnings")["annual"] == [122, 176] and line(st, "cashflow", "sbc")["annual"] == [8, None]
    # ... but not when the filing carries an unlisted share-based-compensation caption (the figure is unknown, not zero)
    facts["facts"]["us-gaap"]["ShareBasedCompensationExpenseNetOfTax"] = {"units": {"USD": [
        _fact("2025-01-01", "2025-12-31", 9, "10-K", "FY", 2025, "2026-02-19", "acc-2025-12-31")]}}
    _, st, _, warnings = S.build_statements(facts, [])
    assert line(st, "cashflow", "owner_earnings")["annual"] == [122, None]
    assert any(w.startswith("sbc: some periods' filings carry no listed SBC tag") and "ShareBasedCompensationExpenseNetOfTax" in w for w in warnings), warnings


def test_no_quarter_from_unpaired_legs():
    """APP Q4 FY2025: the 10-K breaks out 'purchase of intangibles' (FY) that the 10-Qs folded into 'other investing'.
    The line's Q4 is never 'FY minus 0'; the catch-all's Q4 (FY other − 9M other, a number no filing contains) is blanked;
    both cells are flagged basis_break_quarterly."""
    facts = make_facts()
    us = facts["facts"]["us-gaap"]
    # 'other investing': 9M 2025 = 27.9 in the Q3 10-Q (intangibles inside); FY 2025 = 0.4 in the 10-K (intangibles broken out)
    us["PaymentsForProceedsFromOtherInvestingActivities"] = {"units": {"USD": [
        _fact("2025-01-01", "2025-03-31", 4, "10-Q", "Q1", 2025, "2025-05-01", "acc-2025-03-31"),
        _fact("2025-01-01", "2025-06-30", 27.1, "10-Q", "Q2", 2025, "2025-08-01", "acc-2025-06-30"),
        _fact("2025-01-01", "2025-09-30", 27.9, "10-Q", "Q3", 2025, "2025-11-01", "acc-2025-09-30"),
        _fact("2025-01-01", "2025-12-31", 0.4, "10-K", "FY", 2025, "2026-02-19", "acc-2025-12-31")]}}
    us["PaymentsToAcquireIntangibleAssets"] = {"units": {"USD": [_fact("2025-01-01", "2025-12-31", 28.3, "10-K", "FY", 2025, "2026-02-19", "acc-2025-12-31")]}}
    _, st, _, warnings = S.build_statements(facts, [])
    ci, oi = line(st, "cashflow", "capex_intangibles"), line(st, "cashflow", "other_investing")
    assert ci["annual"] == [None, 28.3] and ci["quarterly"][7] is None and ci["basis_break_quarterly"][7] is True, ci
    assert oi["quarterly"][4] == 4 and approx(oi["quarterly"][5], 23.1) and approx(oi["quarterly"][6], 0.8), oi["quarterly"]
    assert oi["quarterly"][7] is None and oi["basis_break_quarterly"][7] is True, oi["quarterly"]
    assert any(w.startswith("quarters not derived") and "capex_intangibles 2025-12-31" in w for w in warnings), warnings
    assert any(w.startswith("catch-all cash-flow quarters blanked") and "other_investing 2025-12-31" in w and "capex_intangibles" in w for w in warnings), warnings
    # the same composition with a catch-all that kept growing through the year is a genuine fourth quarter and stays
    us["PaymentsForProceedsFromOtherInvestingActivities"]["units"]["USD"][-1]["val"] = 31.0
    _, st, _, _ = S.build_statements(facts, [])
    assert approx(line(st, "cashflow", "other_investing")["quarterly"][7], 3.1)


def test_payment_sign_slip():
    """CCI's case: dividends / buybacks / capex are payments; a filing that tags one NEGATIVE is the filer's sign slip —
    the absolute amount paid is read (annual cells and the legs of derived quarters), with a warning naming the filing."""
    facts = make_facts()
    us = facts["facts"]["us-gaap"]
    us["PaymentsOfDividendsCommonStock"] = {"units": {"USD": _flow_entries({2024: [10, 10, 10, 10], 2025: [11, 11, 11, 11], 2026: [12, 12]}, "ytd")}}
    for e in us["PaymentsOfDividendsCommonStock"]["units"]["USD"]:
        if e["end"].startswith("2025"):
            e["val"] = -e["val"]  # every 2025 filing tags the outflow negative
    _, st, _, warnings = S.build_statements(facts, [])
    dv = line(st, "cashflow", "dividends_paid")
    assert dv["annual"] == [40, 44] and dv["quarterly"][4:8] == [11, 11, 11, 11] and dv["cf_sign"] == -1, (dv["annual"], dv["quarterly"])
    assert any(w.startswith("sign:") and "PaymentsOfDividendsCommonStock for 4 period(s)" in w and "10-K filed 2026-02-19" in w for w in warnings), warnings
    # a NET payments tag (payments net of proceeds) keeps its filed sign
    assert "PaymentsForProceedsFromProductiveAssets" in S.NET_PAYMENT_TAGS


def test_long_term_debt_total_tags():
    """HBAN's case: LongTermDebt (includes current maturities) on an unclassified balance sheet is the long-term-debt
    line and the total_debt rule never adds the current maturities to it again."""
    vals = {"long_term_debt": 100, "short_term_debt": 10, "current_lt_debt": 5, "debt_current_agg": None, "debt_total_agg": None}
    assert S.derive_value("total_debt", vals.get, lambda k: True, tag_of=lambda k: {"long_term_debt": "LongTermDebt", "short_term_debt": "ShortTermBorrowings"}.get(k)) == 110
    assert S.derive_value("total_debt", vals.get, lambda k: True, tag_of=lambda k: {"long_term_debt": "LongTermDebtNoncurrent", "short_term_debt": "ShortTermBorrowings"}.get(k)) == 115
    assert S.derive_value("total_debt", vals.get, lambda k: True, tag_of=lambda k: {"long_term_debt": "LongTermDebt", "short_term_debt": "DebtCurrent"}.get(k)) == 100
    facts = make_facts()
    us = facts["facts"]["us-gaap"]
    us["LongTermDebt"] = {"units": {"USD": _instant_entries({e: 300 for e in ALL_ENDS})}}
    us["LongTermDebtNoncurrent"]["units"]["USD"] = [e for e in us["LongTermDebtNoncurrent"]["units"]["USD"] if e["end"] < "2026-01-01"]
    us["LongTermDebtCurrent"] = {"units": {"USD": _instant_entries({e: 40 for e in ALL_ENDS})}}
    _, st, _, _ = S.build_statements(facts, [])
    ltd = line(st, "balance", "long_term_debt")
    assert ltd["quarterly"][7] == 200 and ltd["quarterly"][8] == 300 and sorted(ltd["tags"]) == ["LongTermDebt", "LongTermDebtNoncurrent"]
    td = line(st, "metrics", "total_debt")
    assert td["quarterly"][7] == 240 and td["quarterly"][8] == 300 and td["ttm"] == 300  # noncurrent + current; the total as is
    # bank securities: AFS and HTM are separate lines
    assert [s["key"] for s in S.BALANCE if s["key"].startswith("securities_")] == ["securities_afs", "securities_htm"]


def test_split_adjustment():
    """ACGL's case: a 3-for-1 split — per-share and share-count facts last filed before the first post-split filing are
    restated to today's basis (per share ÷ 3, shares × 3), so FY and quarters sit on one basis."""
    facts = make_facts()
    us = facts["facts"]["us-gaap"]
    # the split: ratio fact at 2025-07-01; the Q2 2025 10-Q (filed 2025-08-01) is the first post-split filing and re-files Q1 2025 ×3
    us["StockholdersEquityNoteStockSplitConversionRatio1"] = {"units": {"pure": [{"end": "2025-07-01", "val": 3, "fy": 2025, "fp": "Q2", "form": "10-Q", "filed": "2025-08-01", "accn": "acc-2025-06-30"}]}}
    for tag in ("WeightedAverageNumberOfDilutedSharesOutstanding", "WeightedAverageNumberOfSharesOutstandingBasic"):
        es = us[tag]["units"]["shares"]
        for e in es:
            if e["filed"] >= "2025-08-01":
                e["val"] *= 3
        es.append(_fact("2025-01-01", "2025-03-31", 99 * 3, "10-Q", "Q1", 2025, "2025-08-01", "acc-2025-06-30"))
        es.append(_fact("2024-01-01", "2024-12-31", 100 * 3, "10-K", "FY", 2025, "2026-02-19", "acc-2025-12-31"))  # the FY2025 10-K restates FY2024
    for tag in ("EarningsPerShareDiluted", "EarningsPerShareBasic"):
        for e in us[tag]["units"]["USD/shares"]:
            if e["filed"] >= "2025-08-01":
                e["val"] = round(e["val"] / 3, 2)
    for e in us["CommonStockSharesOutstanding"]["units"]["shares"]:
        if e["filed"] >= "2025-08-01":
            e["val"] *= 3
    _, st, _, warnings = S.build_statements(facts, [])
    sh = line(st, "income", "shares_basic")  # basic: its Q4 is derived (a diluted Q4 only in a loss quarter)
    assert sh["annual"] == [300, 294] and sh["quarterly"][:5] == [300, 300, 300, 300, 297], (sh["annual"], sh["quarterly"])
    assert 290 < sh["quarterly"][7] < 300 and sh["derived_quarterly"][7] is True  # Q4 derived on the adjusted basis
    eps = line(st, "income", "eps_diluted")
    assert approx(eps["annual"][0], 1.00 / 3) and approx(eps["quarterly"][0], 0.20 / 3) and approx(eps["quarterly"][4], 0.30 / 3)
    assert eps["quarterly"][5] == 0.12  # filed post-split, untouched
    so = line(st, "metrics", "shares_outstanding")
    assert so["quarterly"][0] == 300 and so["quarterly"][9] == 91 * 3  # filed post-split, untouched
    assert any(w.startswith("split adjustment") and "3-for-1 split" in w and "eps_diluted" in w for w in warnings), warnings
    assert S.split_schedule(facts) == [("2025-07-01", 3, "2025-08-01")]
    assert S.split_schedule(make_facts()) == [] and not any(w.startswith("split") for w in S.build_statements(make_facts(), [])[3])


def test_q4_shares_day_weighted():
    """KR's 16-week first quarter: Q4 = (D_FY × FY − Σ d_i × Q_i) / d_4, not 4 × FY − Q1 − Q2 − Q3."""
    ends = ["2025-05-24", "2025-08-16", "2025-11-08", "2026-01-31"]
    qmeta = {e: {"fq": i + 1, "fy_start": "2025-02-02"} for i, e in enumerate(ends)}
    ln = {"quarterly": [664e6, 665e6, 655e6, None], "derived_quarterly": [False] * 4}
    S.derive_q4_shares(ln, [655e6], ["2026-01-31"], ends, qmeta)
    assert ln["quarterly"][3] == 633107000 and ln["derived_quarterly"][3] is True, ln  # 4 × FY − ΣQ would give 636,000,000
    # the consistency gate still applies
    ln = {"quarterly": [664e6, 665e6, 300e6, None], "derived_quarterly": [False] * 4}
    S.derive_q4_shares(ln, [655e6], ["2026-01-31"], ends, qmeta)
    assert ln["quarterly"][3] is None


def test_skip_rule_retries_until_companyfacts_covers_the_filing():
    sub = {"cik": "999", "fiscalYearEnd": "1231", "filings": {"recent": {"form": ["10-Q"], "filingDate": ["2026-11-01"], "reportDate": ["2026-09-30"]}}}
    tmp = tempfile.mkdtemp(prefix="statements_skip_")
    old_base = S.BASE
    try:
        cache = os.path.join(tmp, "cache")
        os.makedirs(cache)
        os.makedirs(os.path.join(tmp, "FIX"))
        with open(os.path.join(cache, "FIX.sub.json"), "w", encoding="utf-8") as f:
            json.dump(sub, f)
        with open(os.path.join(cache, "FIX.facts.json"), "w", encoding="utf-8") as f:
            json.dump(make_facts(), f)  # facts end 2026-06-30: companyfacts lags the Q3 10-Q
        S.BASE = tmp
        s1, sk1 = S.run_one("FIX", cik=999, write=True, cache=cache)
        assert sk1 is False and s1["covered_through"] == "2026-06-30" and any("not yet in EDGAR companyfacts" in w for w in s1["warnings"])
        s2, sk2 = S.run_one("FIX", cik=999, write=True, cache=cache)
        assert sk2 is False, "the same newest filing is NOT a reason to skip while its period is not covered"
        existing = S.read_existing(os.path.join(tmp, "FIX"))
        assert S.can_skip(existing, S.latest_filing(sub)) is False
        existing["covered_through"] = "2026-09-30"
        assert S.can_skip(existing, S.latest_filing(sub)) is True
        assert S.can_skip(dict(existing, schema_version=0), S.latest_filing(sub)) is False
        assert S.can_skip({k: v for k, v in existing.items() if k != "covered_through"}, S.latest_filing(sub)) is False  # a pre-rule file is rebuilt once
    finally:
        S.BASE = old_base
        shutil.rmtree(tmp, ignore_errors=True)


def test_split_inferred_from_refiled_counts():
    """CTSH's case: no split-ratio fact at all, but the diluted counts of several periods were re-filed at exactly x2 —
    the filings say the basis changed on the first such re-filing."""
    facts = make_facts()
    us = facts["facts"]["us-gaap"]
    for tag in ("WeightedAverageNumberOfDilutedSharesOutstanding", "WeightedAverageNumberOfSharesOutstandingBasic"):
        es = us[tag]["units"]["shares"]
        for e in es:
            if e["filed"] >= "2025-11-01":
                e["val"] *= 2
        es.append(_fact("2025-01-01", "2025-03-31", 99 * 2, "10-Q", "Q1", 2025, "2025-11-01", "acc-2025-09-30"))
        es.append(_fact("2025-04-01", "2025-06-30", 98 * 2, "10-Q", "Q2", 2025, "2025-11-01", "acc-2025-09-30"))
        es.append(_fact("2024-01-01", "2024-12-31", 100 * 2, "10-K", "FY", 2025, "2026-02-19", "acc-2025-12-31"))
    for tag in ("EarningsPerShareDiluted", "EarningsPerShareBasic"):
        for e in us[tag]["units"]["USD/shares"]:
            if e["filed"] >= "2025-11-01":
                e["val"] = round(e["val"] / 2, 3)
    _, st, _, warnings = S.build_statements(facts, [])
    assert S.split_schedule(facts) == [("2025-11-01", 2.0, "2025-11-01")]
    sh = line(st, "income", "shares_basic")  # basic: its Q4 is derived (a diluted Q4 only in a loss quarter)
    assert sh["annual"] == [200, 196] and sh["quarterly"][:6] == [200, 200, 200, 200, 198, 196], (sh["annual"], sh["quarterly"])
    eps = line(st, "income", "eps_diluted")
    assert approx(eps["annual"][0], 0.5) and approx(eps["quarterly"][4], 0.15) and approx(eps["quarterly"][6], 0.205)
    assert any(w.startswith("split inferred from the filings") and "3 period(s)" in w and "2-for-1" in w for w in warnings), warnings
    # a single re-filed period is not a split; a tagged split with the same ratio nearby is not inferred twice
    assert S.inferred_splits([("2025-03-31", 2.0, "2025-05-01", "2025-11-01")], []) == []
    assert S.inferred_splits([("2025-03-31", 2.0, "2025-05-01", "2025-11-01"), ("2025-06-30", 2.0, "2025-08-01", "2025-11-01")], [("2025-07-01", 2, "2025-11-01")]) == []
    assert S.inferred_splits([("2025-03-31", 0.5, "2025-05-01", "2025-11-01"), ("2025-06-30", 0.5, "2025-08-01", "2026-02-19")], []) == [("2025-11-01", 0.5, "2025-11-01", 2)]


# ---------------------------------------------------------------- 10-11. review rounds 3-4 (2026-10-15): splits, newest filing + anomalies, same fact, labels, dates
def test_split_tagged_in_many_contexts_is_one_split():
    """DXCM's case: ONE 4-for-1 split (2022-06-10) whose ratio fact is tagged against FY2019, FY2020, 6M / 9M / FY2021
    comparative contexts AND the 2022-06-10 instant — one event, not four (which multiplied old counts up to 256x)."""
    facts = make_facts()
    us = facts["facts"]["us-gaap"]
    ctx = [("2019-01-01", "2019-12-31"), ("2020-01-01", "2020-12-31"), ("2021-01-01", "2021-06-30"), ("2021-01-01", "2021-09-30"), ("2021-01-01", "2021-12-31")]
    ratio = [dict(_fact(s0, e0, 4, "10-K", "FY", 2025, "2025-08-01", "acc-2025-06-30")) for s0, e0 in ctx]
    ratio += [{"end": "2025-06-10", "val": 4, "fy": 2025, "fp": "Q2", "form": "10-Q", "filed": f, "accn": a}
              for f, a in (("2025-08-01", "acc-2025-06-30"), ("2025-11-01", "acc-2025-09-30"), ("2026-02-19", "acc-2025-12-31"))]
    us["StockholdersEquityNoteStockSplitConversionRatio1"] = {"units": {"pure": ratio}}
    for tag in ("WeightedAverageNumberOfDilutedSharesOutstanding", "WeightedAverageNumberOfSharesOutstandingBasic"):
        es = us[tag]["units"]["shares"]
        for e in es:
            if e["filed"] >= "2025-08-01":
                e["val"] *= 4
        es.append(_fact("2025-01-01", "2025-03-31", 99 * 4, "10-Q", "Q1", 2025, "2025-08-01", "acc-2025-06-30"))
        es.append(_fact("2024-01-01", "2024-12-31", 100 * 4, "10-K", "FY", 2025, "2026-02-19", "acc-2025-12-31"))
    assert S.split_events_dedup(facts) == [("2025-06-10", 4)]
    assert S.split_schedule(facts) == [("2025-06-10", 4, "2025-08-01")]
    _, st, _, warnings = S.build_statements(facts, [])
    sh = line(st, "income", "shares_basic")  # basic: its Q4 is derived (a diluted Q4 only in a loss quarter)
    assert sh["annual"] == [400, 392] and sh["quarterly"][:5] == [400, 400, 400, 400, 396], (sh["annual"], sh["quarterly"])
    assert approx(line(st, "income", "eps_diluted")["annual"][0], 1.00 / 4)
    assert sum(1 for w in warnings if "4-for-1 split effective" in w) == 1 and not any("2019-12-31" in w and "split" in w for w in warnings)
    # CFG's case: a ratio tagged only against a fiscal-year context, with flat share counts on both sides — the filings
    # never changed share basis, so nothing is restated
    facts = make_facts()
    facts["facts"]["us-gaap"]["StockholdersEquityNoteStockSplitConversionRatio1"] = {"units": {"pure": [
        _fact("2025-01-01", "2025-12-31", 6, "10-K", "FY", 2025, "2026-02-19", "acc-2025-12-31")]}}
    notes = []
    assert S.split_schedule(facts, notes) == [] and any(n.startswith("split ratio not applied") for n in notes), notes
    _, st, _, _ = S.build_statements(facts, [])
    assert line(st, "income", "shares_diluted")["annual"] == [100, 98]


def test_newest_filing_and_anomalies():
    """The newest filing of a period wins (a restatement re-files every year it covers), except for three anomalies:
    HBAN's shifted column (only the newest filing carries the adjacent year's exact value), HAL's power-of-ten slips
    (the value consistent with the tag's other periods is kept) and DXCM's filed zeros (a 0 against non-zero filings)."""
    facts = make_facts()
    us = facts["facts"]["us-gaap"]
    cash = us["CashAndCashEquivalentsAtCarryingValue"]["units"]["USD"]
    # the FY2024 balance re-filed as a comparative by three 2025 10-Qs (same value), then once shifted in a 2026 10-Q
    for f, a in (("2025-05-01", "acc-2025-03-31"), ("2025-08-01", "acc-2025-06-30"), ("2025-11-01", "acc-2025-09-30")):
        cash.append({"end": "2024-12-31", "val": CASH["2024-12-31"], "fy": 2025, "fp": "Q1", "form": "10-Q", "filed": f, "accn": a})
    cash.append({"end": "2024-12-31", "val": CASH["2025-12-31"], "fy": 2026, "fp": "Q1", "form": "10-Q", "filed": "2026-05-01", "accn": "acc-2026-03-31"})
    eps = us["EarningsPerShareDiluted"]["units"]["USD/shares"]
    eps.append(_fact("2024-01-01", "2024-12-31", 1000000.0, "10-K", "FY", 2025, "2026-02-19", "acc-2025-12-31"))   # x1e6 slip ...
    eps.append(_fact("2024-01-01", "2024-12-31", 1000000.0, "10-K/A", "FY", 2025, "2026-03-01", "acc-amend"))       # ... filed twice
    eps.append(_fact("2025-04-01", "2025-06-30", 360000.0, "10-Q", "Q2", 2026, "2026-08-01", "acc-2026-06-30"))
    eps.append(_fact("2025-07-01", "2025-09-30", 0, "10-Q", "Q3", 2026, "2026-11-01", "acc-2026-09-30"))            # DXCM: a filed 0
    _, st, _, warnings = S.build_statements(facts, [])
    assert line(st, "balance", "cash")["annual"][0] == CASH["2024-12-31"]
    e = line(st, "income", "eps_diluted")
    assert e["annual"][0] == 1.00 and e["quarterly"][5] == 0.36 and e["quarterly"][6] == 0.41, (e["annual"], e["quarterly"])
    assert any(w.startswith("power-of-ten disagreement") and "EarningsPerShareDiluted 2024-01-01..2024-12-31: kept 1" in w for w in warnings), warnings
    assert any(w.startswith("shifted column") and "CashAndCashEquivalentsAtCarryingValue 2024-12-31: kept 195" in w for w in warnings), warnings
    assert any(w.startswith("filed zero") and "EarningsPerShareDiluted 2025-07-01..2025-09-30: kept 0.41" in w for w in warnings), warnings
    # the rule itself: the newest filing wins whatever the count of older ones
    es = [("2024-02-01", 5, "a", "10-K"), ("2025-02-01", 5, "b", "10-K"), ("2026-02-01", 7, "c", "10-K")]
    assert S.pick(es)[0][1] == 7 and [x[2] for x in S.pick(es)[1]] == ["c"] and S.pick(es[:2])[0][1] == 5
    assert S._scale_slip(-1.91, -1910000) and S._scale_slip(1236.5, 1.2365) and not S._scale_slip(1.0, 10.0)  # a 10-for-1 split is no slip
    # a restated balance that equals the next year's because it did not move (goodwill 45 both years in the restating
    # filing) is a restatement, not a shifted column
    hist = {"2024-12-31": [("2025-02-20", 50, "k24", "10-K"), ("2026-02-19", 45, "k25", "10-K")], "2025-12-31": [("2026-02-19", 45, "k25", "10-K")]}
    assert S.drop_shifted(hist, "Goodwill") is hist
    # a genuine restatement (no anomaly) of a balance wins: the newest filing
    facts = make_facts()
    facts["facts"]["us-gaap"]["Goodwill"]["units"]["USD"].append({"end": "2024-12-31", "val": 40, "fy": 2025, "fp": "FY", "form": "10-K",
                                                                  "filed": "2026-02-19", "accn": "acc-2025-12-31"})
    _, st, _, _ = S.build_statements(facts, [])
    assert line(st, "balance", "goodwill")["annual"] == [40, 50]
    # the last-resort cell check: a share count 1/1000 of the line's other cells is blanked (ECHO's 307,410 "shares")
    facts = make_facts()
    sh = facts["facts"]["us-gaap"]["WeightedAverageNumberOfDilutedSharesOutstanding"]["units"]["shares"]
    for x in sh:
        if x["end"] == "2025-06-30":
            x["val"] = 0.098
    _, st, _, warnings = S.build_statements(facts, [])
    assert line(st, "income", "shares_diluted")["quarterly"][5] is None and any(w.startswith("implausible per-share") for w in warnings)
    # an EPS whose filings disagree and whose newest figure has the opposite sign to net income is blanked
    facts = make_facts()
    facts["facts"]["us-gaap"]["EarningsPerShareDiluted"]["units"]["USD/shares"].append(
        _fact("2025-04-01", "2025-06-30", -0.36, "10-Q", "Q2", 2026, "2026-08-01", "acc-2026-06-30"))
    _, st, _, warnings = S.build_statements(facts, [])
    assert line(st, "income", "eps_diluted")["quarterly"][5] is None and any(w.startswith("EPS blanked") and "eps_diluted 2025-06-30 -0.36" in w for w in warnings), warnings


def _restating_facts():
    """FY2023 / FY2024 / FY2025; the FY2025 10-K (acc-2025-12-31, filed 2026-02-19) restates FY2024 for discontinued
    operations — revenue 1000 → 700, net income → 70, assets → 1,100 — while FY2023 (only in the FY2024 10-K) stays as
    originally reported (900)."""
    facts = make_facts()
    us = facts["facts"]["us-gaap"]
    f24, a24, f25, a25 = "2025-02-20", "acc-2024-12-31", "2026-02-19", "acc-2025-12-31"
    us["RevenueFromContractWithCustomerExcludingAssessedTax"]["units"]["USD"] += [
        _fact("2023-01-01", "2023-12-31", 900, "10-K", "FY", 2024, f24, a24), _fact("2024-01-01", "2024-12-31", 700, "10-K", "FY", 2025, f25, a25)]
    us["NetIncomeLoss"]["units"]["USD"] += [
        _fact("2023-01-01", "2023-12-31", 90, "10-K", "FY", 2024, f24, a24), _fact("2024-01-01", "2024-12-31", 70, "10-K", "FY", 2025, f25, a25)]
    us["Assets"]["units"]["USD"] += [{"end": "2023-12-31", "val": 1500, "fy": 2024, "fp": "FY", "form": "10-K", "filed": f24, "accn": a24},
                                     {"end": "2024-12-31", "val": 1100, "fy": 2025, "fp": "FY", "form": "10-K", "filed": f25, "accn": a25}]
    return facts


def test_restatement_takes_the_period_and_growth_never_spans_generations():
    """ECHO / HPQ / APP / NVT: a later 10-K that recasts a prior year (revenue, net income AND the balance sheet) is that
    year's value for every line — never the original balance sheet next to the recast income statement — and the growth
    from the year before it, which no filing reports on the restated basis, is blank rather than mixing bases."""
    _, st, _, warnings = S.build_statements(_restating_facts(), [])
    rev, ni, ta = line(st, "income", "revenue"), line(st, "income", "net_income"), line(st, "balance", "total_assets")
    assert rev["annual"] == [900, 700, 1200] and ni["annual"][1] == 70 and ta["annual"][1] == 1100, (rev["annual"], ta["annual"])
    # FY2024 (restated, FY2025 10-K) vs FY2023 (original, FY2024 10-K): the FY2024 10-K reported both years, so the two
    # chosen values are from two generations — growth blank; FY2025 vs FY2024 come from the same 10-K — growth shown
    assert rev["growth_annual"][1] is None and approx(rev["growth_annual"][2], 1200 / 700 - 1), rev["growth_annual"]
    assert ta["growth_annual"][1] is None and ni["growth_annual"][1] is None
    assert any(w.startswith("growth across filing generations") and "revenue (2024-12-31)" in w for w in warnings), warnings
    nm = line(st, "metrics", "net_margin")
    assert approx(nm["annual"][1], 70 / 700)  # restated net income over restated revenue
    # a fixture whose filings carry no comparatives at all: no filing reports both years, so no evidence of two bases
    _, st, _, _ = S.build_statements(make_facts(), [])
    assert approx(line(st, "income", "revenue")["growth_annual"][1], 0.2)


def test_fcf_on_one_basis():
    """CCI's case: the FY2025 10-K re-files total-company OCF unchanged (it includes discontinued operations) while capex is
    restated to continuing operations, the discontinued investing flows on their own line. FCF = continuing OCF (OCF −
    discontinued OCF, same filing) − continuing capex — never total OCF − continuing capex; and FCF is blank when OCF and
    capex were taken from two different filing generations."""
    facts = make_facts()
    us = facts["facts"]["us-gaap"]
    f25, a25 = "2026-02-19", "acc-2025-12-31"
    us["NetCashProvidedByUsedInOperatingActivities"]["units"]["USD"].append(_fact("2024-01-01", "2024-12-31", 150, "10-K", "FY", 2025, f25, a25))
    us["PaymentsToAcquirePropertyPlantAndEquipment"]["units"]["USD"].append(_fact("2024-01-01", "2024-12-31", 12, "10-K", "FY", 2025, f25, a25))
    us["CashProvidedByUsedInOperatingActivitiesDiscontinuedOperations"] = {"units": {"USD": [
        _fact("2024-01-01", "2024-12-31", 50, "10-K", "FY", 2025, f25, a25), _fact("2025-01-01", "2025-12-31", 60, "10-K", "FY", 2025, f25, a25)]}}
    us["CashProvidedByUsedInInvestingActivitiesDiscontinuedOperations"] = {"units": {"USD": [
        _fact("2024-01-01", "2024-12-31", -30, "10-K", "FY", 2025, f25, a25), _fact("2025-01-01", "2025-12-31", -35, "10-K", "FY", 2025, f25, a25)]}}
    _, st, _, warnings = S.build_statements(facts, [])
    ocf, capex, fcf = line(st, "cashflow", "ocf"), line(st, "cashflow", "capex"), line(st, "cashflow", "fcf")
    assert ocf["annual"] == [150, 200] and capex["annual"] == [12, 24], (ocf["annual"], capex["annual"])
    assert fcf["annual"] == [150 - 50 - 12, 200 - 60 - 24], fcf["annual"]  # not 150 − 12 = 138
    assert line(st, "cashflow", "owner_earnings")["annual"] == [150 - 50 - 12 - 8, 200 - 60 - 24 - 12]
    # capex restated by the FY2025 10-K but OCF not re-filed there: the two values share no filing although the FY2024 10-K
    # reported both — FCF (and owner's earnings, FCF margin) blank, warned
    facts = make_facts()
    facts["facts"]["us-gaap"]["PaymentsToAcquirePropertyPlantAndEquipment"]["units"]["USD"].append(_fact("2024-01-01", "2024-12-31", 12, "10-K", "FY", 2025, f25, a25))
    _, st, _, warnings = S.build_statements(facts, [])
    assert line(st, "cashflow", "fcf")["annual"] == [None, 176] and line(st, "cashflow", "owner_earnings")["annual"][0] is None
    assert line(st, "metrics", "fcf_margin")["annual"][0] is None
    assert any(w.startswith("same filing:") and "fcf 2024-12-31" in w for w in warnings), warnings


def test_q4_diluted_and_eps():
    """DXCM: a diluted weighted count has no day-weighted identity, so Q4 diluted is never derived from the year — except
    in a loss quarter, where every potential share is antidilutive and diluted = the derived basic count. Q4 EPS = FY EPS −
    the three filed quarters (FY 0.82 − 0.23 − 0.12 − 0.24 = 0.23), not net income ÷ a derived count."""
    ends = ["2022-03-31", "2022-06-30", "2022-09-30", "2022-12-31"]
    qmeta = {e: {"fq": i + 1, "fy_start": "2022-01-01"} for i, e in enumerate(ends)}

    def ln(q, a=None):
        return {"quarterly": list(q), "annual": list(a or [None]), "derived_quarterly": [False] * 4, "_atags": {}, "_qtags": {}}
    lines = {"shares_basic": ln([390, 391, 392, None], [391]), "shares_diluted": ln([430, 431, 432, None], [431]),
             "net_income": ln([90, 50, 100, 92], [332]), "eps_diluted": ln([0.23, 0.12, 0.24, None], [0.82]), "eps_basic": ln([0.23, 0.13, 0.26, None], [0.85])}
    S.derive_q4_shares(lines["shares_basic"], [391], ["2022-12-31"], ends, qmeta)
    S.derive_q4_diluted_shares(lines, ends, qmeta)
    S.derive_q4_eps(lines, ["2022-12-31"], ends, qmeta)
    assert S._num(lines["shares_basic"]["quarterly"][3]) and lines["shares_diluted"]["quarterly"][3] is None  # profitable Q4: blank
    assert approx(lines["eps_diluted"]["quarterly"][3], 0.23) and lines["eps_diluted"]["derived_quarterly"][3] is True
    assert approx(lines["eps_basic"]["quarterly"][3], 0.23)
    # a loss Q4: diluted = the derived basic count (never below it)
    lines["net_income"]["quarterly"][3] = -5
    lines["net_income"]["annual"] = [235]
    lines["eps_diluted"] = ln([0.23, 0.12, 0.24, None], [0.58])
    S.derive_q4_diluted_shares(lines, ends, qmeta)
    assert lines["shares_diluted"]["quarterly"][3] == lines["shares_basic"]["quarterly"][3] and lines["shares_diluted"]["derived_quarterly"][3] is True
    S.derive_q4_eps(lines, ["2022-12-31"], ends, qmeta)
    assert approx(lines["eps_diluted"]["quarterly"][3], -0.01)
    # the year's quarters and the year on different bases (net income quarters 289 vs FY 400): no Q4 EPS
    lines["net_income"]["annual"] = [400]
    lines["eps_diluted"] = ln([0.23, 0.12, 0.24, None], [1.05])
    warnings = []
    S.derive_q4_eps(lines, ["2022-12-31"], ends, qmeta, warnings)
    assert lines["eps_diluted"]["quarterly"][3] is None and any(w.startswith("Q4 EPS not derived") for w in warnings)


def test_split_ratio_not_borne_out_by_quarterly_counts():
    """Q (Qnity): 0.5 tagged on 2026 duration contexts is the spin-off distribution ratio (one Qnity share per two DuPont
    shares), not a reverse split — the quarterly diluted count filed after it (210.3M) follows the last one before it
    (209.8M), so nothing is restated. No fiscal-year count filed since is no longer a reason to apply it."""
    facts = make_facts()
    facts["facts"]["us-gaap"]["StockholdersEquityNoteStockSplitConversionRatio1"] = {"units": {"pure": [
        _fact("2026-01-01", "2026-03-31", 0.5, "10-Q", "Q1", 2026, "2026-05-01", "acc-2026-03-31"),
        _fact("2026-01-01", "2026-06-30", 0.5, "10-Q", "Q2", 2026, "2026-08-01", "acc-2026-06-30")]}}
    notes = []
    assert S.split_schedule(facts, notes) == [] and any(n.startswith("split ratio not applied") and "1-for-2 reverse split" in n for n in notes), notes
    _, st, _, warnings = S.build_statements(facts, [])
    assert line(st, "income", "eps_diluted")["annual"] == [1.00, 1.53] and line(st, "income", "shares_diluted")["annual"] == [100, 98]
    # the rule: quarterly counts count; a duration-only ratio with nothing filed since is not applied, an instant one is
    counts = {("2025-01-01", "2025-12-31"): (209.8, "2026-02-26"), ("2026-01-01", "2026-03-31"): (210.3, "2026-05-12")}
    assert S.split_borne_out("2026-03-31", 0.5, counts) is False
    assert S.split_borne_out("2026-03-31", 0.5, {("2026-01-01", "2026-03-31"): (105.1, "2026-05-12"), **{k: v for k, v in counts.items() if k[1] < "2026"}}) is True
    only_pre = {("2025-01-01", "2025-12-31"): (209.8, "2026-02-26")}
    assert S.split_borne_out("2026-03-31", 0.5, only_pre, instant=False) is False and S.split_borne_out("2026-03-31", 0.5, only_pre, instant=True) is True


def test_reverse_split_corroborated_by_split_shares_fact():
    """DFTX: a 1-for-15 reverse split with NO ratio fact; one period's diluted count re-filed ×1/15 and a
    StockIssuedDuringPeriodSharesReverseStockSplits instant at the effective date (2022-08-26). Any whole ratio is accepted
    when corroborated, from one period, and values last filed before the effective date are restated."""
    refil = [("2022-06-30", 1 / 15, "2022-08-11", "2023-08-03")]
    assert S.inferred_splits(refil, []) == []  # 15 is no simple ratio and one period is no evidence on its own
    assert S.inferred_splits(refil, [], ["2022-08-26"]) == [("2022-08-26", 1 / 15, "2022-08-26", 1)]
    assert S.inferred_splits(refil, [], ["2021-01-15"]) == []  # a split-shares date far before the old-basis filing corroborates nothing
    facts = make_facts()
    us = facts["facts"]["us-gaap"]
    for tag in ("WeightedAverageNumberOfDilutedSharesOutstanding", "WeightedAverageNumberOfSharesOutstandingBasic"):
        es = us[tag]["units"]["shares"]
        for e in es:
            if e["filed"] >= "2025-08-01":
                e["val"] = round(e["val"] / 15, 4)
        es.append(_fact("2025-01-01", "2025-03-31", round(99 / 15, 4), "10-Q", "Q1", 2025, "2026-05-01", "acc-2026-03-31"))
    for tag in ("EarningsPerShareDiluted", "EarningsPerShareBasic"):
        for e in us[tag]["units"]["USD/shares"]:
            if e["filed"] >= "2025-08-01":
                e["val"] = round(e["val"] * 15, 2)
    us["StockIssuedDuringPeriodSharesReverseStockSplits"] = {"units": {"shares": [
        {"end": "2025-07-15", "val": 1, "fy": 2025, "fp": "Q2", "form": "10-Q", "filed": "2025-08-01", "accn": "acc-2025-06-30"}]}}
    notes = []
    sched = S.split_schedule(facts, notes)
    assert len(sched) == 1 and sched[0][0] == "2025-07-15" and approx(sched[0][1], 1 / 15) and sched[0][2] == "2025-07-15", sched
    _, st, _, _ = S.build_statements(facts, [])
    eps = line(st, "income", "eps_diluted")
    assert approx(eps["annual"][0], 1.00 * 15) and approx(eps["quarterly"][0], 0.20 * 15) and approx(eps["quarterly"][5], 0.36 * 15)


def test_two_splits_of_the_same_ratio():
    """WRB did 3-for-2 in 2019, 2022 and 2024: a second same-ratio split tagged only on duration contexts, filed more than
    SPLIT_CHAIN_DAYS after the first event's own filings, is a second event — never absorbed into the first."""
    def inst(d, filed):
        return {"end": d, "val": 1.5, "form": "10-Q", "filed": filed, "accn": "i-" + filed}
    facts = {"facts": {"us-gaap": {"StockholdersEquityNoteStockSplitConversionRatio1": {"units": {"pure": [
        inst("2022-03-23", "2022-05-03"),
        _fact("2024-01-01", "2024-06-30", 1.5, "10-Q", "Q2", 2024, "2024-08-02", "d1"),
        _fact("2024-01-01", "2024-09-30", 1.5, "10-Q", "Q3", 2024, "2024-11-04", "d2"),
        _fact("2024-01-01", "2024-12-31", 1.5, "10-K", "FY", 2024, "2025-02-20", "d3")]}}}}}
    assert S.split_events_dedup(facts) == [("2022-03-23", 1.5), ("2024-06-30", 1.5)]
    facts2 = {"facts": {"us-gaap": {"StockholdersEquityNoteStockSplitConversionRatio1": {"units": {"pure": [
        {"end": "2021-06-01", "val": 2, "form": "10-Q", "filed": "2021-08-01", "accn": "i"},
        _fact("2023-01-01", "2023-03-31", 2, "10-Q", "Q1", 2023, "2023-05-01", "d1"),
        _fact("2023-01-01", "2023-06-30", 2, "10-Q", "Q2", 2023, "2023-08-01", "d2")]}}}}}
    assert S.split_events_dedup(facts2) == [("2021-06-01", 2), ("2023-03-31", 2)]
    # comparatives re-tagged within the event's own chain of filings stay one event (DXCM: test_split_tagged_in_many_contexts_is_one_split)
    facts3 = {"facts": {"us-gaap": {"StockholdersEquityNoteStockSplitConversionRatio1": {"units": {"pure": [
        {"end": "2022-06-10", "val": 4, "form": "10-Q", "filed": "2022-07-28", "accn": "i"},
        _fact("2020-01-01", "2020-12-31", 4, "10-K", "FY", 2022, "2023-02-10", "k"),
        _fact("2021-01-01", "2021-12-31", 4, "10-Q", "Q3", 2023, "2023-10-26", "q")]}}}}}
    assert S.split_events_dedup(facts3) == [("2022-06-10", 4)]


def test_gross_interest_tag_carrying_the_net_figure():
    """KR's FY2023 / FY2024 10-Ks tag the face 'Interest expense' 441M under InterestExpense while
    InterestIncomeExpenseNonoperatingNet carries −441M for the same year: the figure is NET (the 118M of interest income is
    inside it), so interest income is blank there; a row mixing gross and net years keeps the generic label."""
    facts = make_facts()
    us = facts["facts"]["us-gaap"]
    us["InterestExpense"] = {"units": {"USD": [_fact("2024-01-01", "2024-12-31", 30, "10-K", "FY", 2024, "2025-02-20", "acc-2024-12-31"),
                                               _fact("2025-01-01", "2025-12-31", 41, "10-K", "FY", 2025, "2026-02-19", "acc-2025-12-31")]}}
    us["InterestIncomeExpenseNonoperatingNet"] = {"units": {"USD": [_fact("2025-01-01", "2025-12-31", -41, "10-K", "FY", 2026, "2026-08-01", "acc-x")]}}
    us["InvestmentIncomeInterest"] = {"units": {"USD": [_fact("2024-01-01", "2024-12-31", 3, "10-K", "FY", 2024, "2025-02-20", "acc-2024-12-31"),
                                                        _fact("2025-01-01", "2025-12-31", 11, "10-K", "FY", 2025, "2026-02-19", "acc-2025-12-31")]}}
    _, st, _, warnings = S.build_statements(facts, [])
    ie, ii = line(st, "income", "interest_expense"), line(st, "income", "interest_income")
    assert ie["annual"] == [30, 41] and ii["annual"] == [3, None], (ie["annual"], ii["annual"])
    assert ie["label"] == "Interest expense"
    assert any(w.startswith("interest expense: the row mixes gross and NET") and "1 filed under the gross tag" in w for w in warnings), warnings
    # every figure net → the net label
    us["InterestIncomeExpenseNonoperatingNet"]["units"]["USD"].append(_fact("2024-01-01", "2024-12-31", -30, "10-K", "FY", 2025, "2026-02-19", "acc-2025-12-31"))
    _, st, _, _ = S.build_statements(facts, [])
    assert line(st, "income", "interest_expense")["label"] == "Interest expense, net" and line(st, "income", "interest_income") is None


def test_capex_keeps_one_caption():
    """EXR: development spending (PaymentsToDevelopRealEstateAssets) is filed every year; a higher-priority
    PaymentsToAcquireProductiveAssets appears from FY2025 — the series keeps the caption the earlier years used while it is
    still filed, instead of jumping on a change of definition."""
    facts = make_facts()
    us = facts["facts"]["us-gaap"]
    us["PaymentsToDevelopRealEstateAssets"] = us.pop("PaymentsToAcquirePropertyPlantAndEquipment")
    us["PaymentsToAcquireProductiveAssets"] = {"units": {"USD": [_fact("2025-01-01", "2025-12-31", 900, "10-K", "FY", 2025, "2026-02-19", "acc-2025-12-31")]}}
    _, st, _, warnings = S.build_statements(facts, [])
    capex = line(st, "cashflow", "capex")
    assert capex["annual"] == [20, 24] and capex["tags"] == ["PaymentsToDevelopRealEstateAssets"] and approx(capex["growth_annual"][1], 0.2)
    assert any(w.startswith("capex: one caption per series") for w in warnings), warnings
    # a caption change that cannot be avoided (the old caption is no longer filed) blanks the growth across it
    us["PaymentsToDevelopRealEstateAssets"]["units"]["USD"] = [e for e in us["PaymentsToDevelopRealEstateAssets"]["units"]["USD"] if e["end"] < "2025-01-01"]
    _, st, _, warnings = S.build_statements(facts, [])
    capex = line(st, "cashflow", "capex")
    assert capex["annual"] == [20, 900] and capex["growth_annual"][1] is None
    assert any(w.startswith("capex: the filed caption changes") for w in warnings), warnings


def test_same_filed_fact_counted_once():
    """GFI's case: the one face line 'Current portion of borrowings' 719.1 is tagged ShorttermBorrowings AND
    CurrentBorrowingsAndCurrentPortionOfNoncurrentBorrowings in the same 20-F — total debt = 1,776.5 + 719.1, not + 2 x 719.1."""
    facts = make_facts()
    us = facts["facts"]["us-gaap"]
    us["ShortTermBorrowings"] = {"units": {"USD": _instant_entries({e: 70 for e in ALL_ENDS})}}
    us["LongTermDebtCurrent"] = {"units": {"USD": _instant_entries({e: 70 for e in ALL_ENDS})}}
    us["LongTermDebtCurrent"]["units"]["USD"][0]["val"] = 30  # a different figure in one period: both lines count there
    _, st, _, warnings = S.build_statements(facts, [])
    cur = line(st, "balance", "current_lt_debt")
    assert cur["quarterly"][0] == 30 and cur["quarterly"][1:] == [None] * 9 and line(st, "balance", "short_term_debt")["ttm"] == 70
    td = line(st, "metrics", "total_debt")
    assert td["quarterly"][0] == 200 + 70 + 30 and td["ttm"] == 270 and td["annual"] == [270, 270]
    assert any(w.startswith("debt:") and "same filed fact" in w for w in warnings), warnings
    # the IFRS aggregate is the whole current debt when it is the only current line
    vals = {"long_term_debt": 1776.5, "current_lt_debt": 719.1, "short_term_debt": 719.1, "debt_current_agg": None, "debt_total_agg": None}
    tags = {"long_term_debt": "LongtermBorrowings", "current_lt_debt": "CurrentBorrowingsAndCurrentPortionOfNoncurrentBorrowings", "short_term_debt": "ShorttermBorrowings"}
    assert approx(S.derive_value("total_debt", vals.get, lambda k: True, tag_of=tags.get), 1776.5 + 719.1)


def _fy_facts(fys, quarters, filed_lag=40):
    """A minimal filer: fys = [(start, end)], quarters = [(start, end)]; revenue / net income as 3-month 10-Q facts
    plus FY 10-K facts, assets at every end."""
    def f(e):
        return (datetime.date.fromisoformat(e) + datetime.timedelta(days=filed_lag)).isoformat()
    rev, ni, assets = [], [], []
    for s0, e0 in quarters:
        rev.append(_fact(s0, e0, 100, "10-Q", "Q1", 2000, f(e0), "q-" + e0))
        ni.append(_fact(s0, e0, 10, "10-Q", "Q1", 2000, f(e0), "q-" + e0))
        assets.append({"end": e0, "val": 1000, "fp": "Q1", "form": "10-Q", "filed": f(e0), "accn": "q-" + e0})
    for s0, e0 in fys:
        rev.append(_fact(s0, e0, 400, "10-K", "FY", 2000, f(e0), "k-" + e0))
        ni.append(_fact(s0, e0, 40, "10-K", "FY", 2000, f(e0), "k-" + e0))
        assets.append({"end": e0, "val": 1000, "fp": "FY", "form": "10-K", "filed": f(e0), "accn": "k-" + e0})
    return {"cik": 1, "entityName": "X", "facts": {"us-gaap": {"Revenues": {"units": {"USD": rev}}, "NetIncomeLoss": {"units": {"USD": ni}},
                                                                "Assets": {"units": {"USD": assets}}}}}


def test_quarter_labels_follow_the_annual_rule():
    """TDY / KVUE: 52/53-week years ending 2012-01-01 and 2012-12-30 are FY2011 and FY2012; their quarters carry the SAME
    fiscal-year labels (they were labelled a year late and collided: two 'Q1 FY2012')."""
    fys = [("2011-01-03", "2012-01-01"), ("2012-01-02", "2012-12-30")]
    qs = [("2011-01-03", "2011-04-03"), ("2011-04-04", "2011-07-03"), ("2011-07-04", "2011-10-02"), ("2011-10-03", "2012-01-01"),
          ("2012-01-02", "2012-04-01"), ("2012-04-02", "2012-07-01"), ("2012-07-02", "2012-09-30"), ("2012-10-01", "2012-12-30"),
          ("2012-12-31", "2013-03-31")]
    periods, _, _, warnings = S.build_statements(_fy_facts(fys, qs), [])
    assert [p["label"] for p in periods["annual"]] == ["FY2011", "FY2012"]
    labels = [p["label"] for p in periods["quarterly"]]
    assert labels == ["Q1 FY2011", "Q2 FY2011", "Q3 FY2011", "Q4 FY2011", "Q1 FY2012", "Q2 FY2012", "Q3 FY2012", "Q4 FY2012", "Q1 FY2013"], labels
    assert not any(w.startswith("quarter labels") for w in warnings)


def test_week_end_and_month_end_are_one_period():
    """HSY: the 10-Q dated Q1 2012 at the fiscal week-end 2012-04-01, the next year's comparative at 2012-03-31 — one
    column, dated as the original filing dated it, both filings voting."""
    fys = [("2012-01-01", "2012-12-31")]
    qs = [("2012-01-01", "2012-04-01"), ("2012-04-02", "2012-07-01"), ("2012-07-02", "2012-09-30"), ("2012-10-01", "2012-12-31"), ("2013-01-01", "2013-03-31")]
    facts = _fy_facts(fys, qs)
    us = facts["facts"]["us-gaap"]
    us["Revenues"]["units"]["USD"].append(_fact("2012-01-01", "2012-03-31", 100, "10-Q", "Q1", 2013, "2013-05-08", "q-2013-03-31"))
    us["NetIncomeLoss"]["units"]["USD"].append(_fact("2012-01-01", "2012-03-31", 10, "10-Q", "Q1", 2013, "2013-05-08", "q-2013-03-31"))
    us["Assets"]["units"]["USD"].append({"end": "2012-03-31", "val": 1000, "fp": "Q1", "form": "10-Q", "filed": "2013-05-08", "accn": "q-2013-03-31"})
    periods, st, _, warnings = S.build_statements(facts, [])
    ends = [p["end"] for p in periods["quarterly"]]
    assert ends == ["2012-04-01", "2012-07-01", "2012-09-30", "2012-12-31", "2013-03-31"], ends
    assert any(w.startswith("period dates merged") and "2012-03-31 -> 2012-04-01" in w for w in warnings), warnings
    assert line(st, "income", "revenue")["quarterly"][0] == 100 and line(st, "balance", "total_assets")["quarterly"][0] == 1000


def test_interest_lines():
    """APP: the face 'interest expense and loss on settlement of debt' (InterestAndDebtExpense) ranks above the debt-only note
    figure; KR: when the expense line is the NET figure, interest income is not shown again for that period."""
    assert S.INTEREST_EXPENSE_TAGS.index("InterestAndDebtExpense") < S.INTEREST_EXPENSE_TAGS.index("InterestExpenseDebt")
    facts = make_facts()
    us = facts["facts"]["us-gaap"]
    us["InterestExpenseDebt"] = {"units": {"USD": [_fact("2025-01-01", "2025-12-31", 20, "10-K", "FY", 2025, "2026-02-19", "acc-2025-12-31")]}}
    us["InterestAndDebtExpense"] = {"units": {"USD": [_fact("2025-01-01", "2025-12-31", 21, "10-K", "FY", 2025, "2026-02-19", "acc-2025-12-31")]}}
    us["InvestmentIncomeInterest"] = {"units": {"USD": [_fact("2024-01-01", "2024-12-31", 3, "10-K", "FY", 2024, "2025-02-20", "acc-2024-12-31"),
                                                        _fact("2025-01-01", "2025-12-31", 4, "10-K", "FY", 2025, "2026-02-19", "acc-2025-12-31")]}}
    us["InterestIncomeExpenseNonoperatingNet"] = {"units": {"USD": [_fact("2024-01-01", "2024-12-31", -12, "10-K", "FY", 2024, "2025-02-20", "acc-2024-12-31")]}}
    _, st, _, warnings = S.build_statements(facts, [])
    ie, ii = line(st, "income", "interest_expense"), line(st, "income", "interest_income")
    # the label follows the newest fiscal year's presentation (FY2025: the gross face line); KR's all-net case is test_kroger_lines
    assert ie["annual"] == [12, 21] and ie["label"] == "Interest expense" and "InterestIncomeExpenseNonoperatingNet" in ie["tags"], ie
    assert ii["annual"] == [None, 4], ii["annual"]  # FY2024's expense line is the net figure: income already inside it
    assert any(w.startswith("interest income: blank for 1 period(s)") for w in warnings), warnings


def test_revenue_industry_fallback():
    """CMG / ATO / EXR / GFI: years before the contract-revenue taxonomy carry the filer's industry top line — used for the
    years the standard tags leave empty when it agrees with the standard revenue where both are filed; EQT's
    OilAndGasRevenue (a component that disagrees) is never used."""
    facts = make_facts()
    us = facts["facts"]["us-gaap"]
    for e in us["RevenueFromContractWithCustomerExcludingAssessedTax"]["units"]["USD"]:
        if e["end"] < "2025-01-01":
            e["val"] = None  # the standard tag is not filed for 2024
    us["RevenueFromContractWithCustomerExcludingAssessedTax"]["units"]["USD"] = [e for e in us["RevenueFromContractWithCustomerExcludingAssessedTax"]["units"]["USD"] if e["val"] is not None]
    us["FoodAndBeverageRevenue"] = {"units": {"USD": _flow_entries({2024: [220, 240, 260, 280], 2025: [270, 290, 310, 330]}, "3m+ytd")}}
    _, st, _, warnings = S.build_statements(facts, [])
    rev = line(st, "income", "revenue")
    assert rev["annual"] == [1000, 1200] and rev["quarterly"][:4] == [220, 240, 260, 280] and "FoodAndBeverageRevenue" in rev["tags"]
    assert any(w.startswith("revenue: periods the standard revenue tags leave empty") and "FoodAndBeverageRevenue for 1 fiscal year(s)" in w for w in warnings), warnings
    us.pop("FoodAndBeverageRevenue")
    us["OilAndGasRevenue"] = {"units": {"USD": _flow_entries({2024: [220, 240, 260, 280], 2025: [100, 100, 100, 100]}, "3m+ytd")}}
    _, st, _, warnings = S.build_statements(facts, [])
    assert line(st, "income", "revenue")["annual"] == [None, 1200]
    assert any(w.startswith("revenue: blank where no standard tag is filed") and "OilAndGasRevenue" in w for w in warnings), warnings


def test_continuing_eps_and_original_filing_date():
    """HAL FY2022-FY2025 tags only continuing-operations EPS (no discontinued operations): it is the EPS. periods.annual[].filed
    is the ORIGINAL annual report's date (submissions feed first, then the first annual filing of ANY fact for that year)."""
    facts = make_facts()
    us = facts["facts"]["us-gaap"]
    us["EarningsPerShareDiluted"]["units"]["USD/shares"] = [e for e in us["EarningsPerShareDiluted"]["units"]["USD/shares"] if e["end"] != "2025-12-31"]
    us["IncomeLossFromContinuingOperationsPerDilutedShare"] = {"units": {"USD/shares": [_fact("2025-01-01", "2025-12-31", 1.53, "10-K", "FY", 2025, "2026-02-19", "acc-2025-12-31")]}}
    sub = {"filings": {"recent": {"form": ["10-K", "10-Q"], "filingDate": ["2025-02-18", "2025-05-01"], "reportDate": ["2024-12-31", "2025-03-31"]}}}
    periods, st, _, warnings = S.build_statements(facts, [], sub=sub)
    assert line(st, "income", "eps_diluted")["annual"] == [1.00, 1.53] and "IncomeLossFromContinuingOperationsPerDilutedShare" in line(st, "income", "eps_diluted")["tags"]
    assert [p["filed"] for p in periods["annual"]] == ["2025-02-18", "2026-02-19"]  # FY2024 from the feed, FY2025 from the facts
    # with discontinued operations in the period the continuing figure is NOT the EPS
    us["IncomeLossFromDiscontinuedOperationsNetOfTax"] = {"units": {"USD": [_fact("2025-01-01", "2025-12-31", 5, "10-K", "FY", 2025, "2026-02-19", "acc-2025-12-31")]}}
    _, st, _, _ = S.build_statements(facts, [])
    assert line(st, "income", "eps_diluted")["annual"] == [1.00, None]


# ---------------------------------------------------------------- 12. review round 5: restricted cash, stable write
COMB = "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents"


def _restricted_facts():
    """NTRS-shaped: every cash cell is the combined cash + restricted total (no CashAndCashEquivalentsAtCarryingValue),
    RestrictedCash tagged from 2025 only; FY2025 = NTRS's 10-K: cash and due from banks 5,873.1M of which 531.2M
    restricted, statements.py's total debt 3,351.5M, 186,337,588 shares outstanding."""
    facts = make_facts()
    us = facts["facts"]["us-gaap"]
    del us["CashAndCashEquivalentsAtCarryingValue"]
    cash = {e: 4_000_000_000 + 100_000_000 * i for i, e in enumerate(ALL_ENDS)}
    cash["2025-12-31"] = 5_873_100_000
    rc = {e: 500_000_000 + 1_000_000 * i for i, e in enumerate(ALL_ENDS) if e >= "2025-01-01"}
    rc["2025-12-31"] = 531_200_000
    us[COMB] = {"units": {"USD": _instant_entries(cash)}}
    us["RestrictedCash"] = {"units": {"USD": _instant_entries(rc)}}
    us["LongTermDebtNoncurrent"] = {"units": {"USD": _instant_entries({e: 3_351_500_000 for e in ALL_ENDS})}}
    us["CommonStockSharesOutstanding"] = {"units": {"shares": _instant_entries({e: 186_337_588 for e in ALL_ENDS})}}
    return facts, cash, rc


def test_restricted_cash_deducted_from_net_cash():
    """Codex review of PR #2 (statements.py:2411): the cash line accepts the combined cash + restricted cash tag, and net
    cash netted the whole amount — NTRS FY2025 2,521.6M / 13.53 per share. The restricted part is deducted where it is
    tagged (1,990.4M / 10.68), flagged where it is not, and the cash line itself says what it holds."""
    facts, cash, rc = _restricted_facts()
    periods, st, _, warnings = S.build_statements(facts, [])
    debt = 3_351_500_000
    # the balance-sheet line stays as filed, labelled and marked as including restricted cash
    c = line(st, "balance", "cash")
    assert c["annual"] == [cash["2024-12-31"], 5_873_100_000] and c["quarterly"] == [cash[e] for e in ALL_ENDS] and c["tags"] == [COMB]
    assert c["label"] == "Cash, equivalents & restricted cash"
    assert c["incl_restricted_annual"] == [True, True] and c["incl_restricted_quarterly"] == [True] * 10 and c["incl_restricted_ttm"] is True
    # the restricted part on its own line, right under cash, only where it is tagged
    keys = [l["key"] for l in st["balance"]]
    assert keys[keys.index("cash") + 1] == "restricted_cash"
    r = line(st, "balance", "restricted_cash")
    assert r["label"] == "Restricted cash (included in cash above)" and r["level"] == 2 and r["tags"] == ["RestrictedCash"]
    assert r["annual"] == [None, 531_200_000] and r["quarterly"] == [None] * 4 + [rc[e] for e in ALL_ENDS[4:]] and r["ttm"] == rc["2026-06-30"]
    # net cash: FY2025 2,521.6M -> 1,990.4M; FY2024 (no restricted-cash tag) stays the combined figure, flagged
    nc = line(st, "metrics", "net_cash")
    assert nc["annual"][1] == 5_873_100_000 - 531_200_000 - debt == 1_990_400_000
    assert nc["annual"][0] == cash["2024-12-31"] - debt and nc["incl_restricted_annual"] == [True, False]
    assert nc["quarterly"] == [cash[e] - debt for e in ALL_ENDS[:4]] + [cash[e] - rc[e] - debt for e in ALL_ENDS[4:]]
    assert nc["incl_restricted_quarterly"] == [True] * 4 + [False] * 6 and nc["incl_restricted_ttm"] is False
    assert nc["ttm"] == cash["2026-06-30"] - rc["2026-06-30"] - debt
    # net cash per share: 13.53 -> 10.68
    ncps = line(st, "metrics", "net_cash_per_share")
    assert round(ncps["annual"][1], 2) == 10.68 and round((5_873_100_000 - debt) / 186_337_588, 2) == 13.53
    assert ncps["incl_restricted_annual"] == [True, False] and ncps["incl_restricted_quarterly"] == nc["incl_restricted_quarterly"]
    # the marks are JSON only (the app shows labels): the labels say some periods still count restricted cash as cash
    assert nc["label"] == "Net cash (debt) (some periods incl. restricted cash)" and ncps["label"] == "Net cash per share (some periods incl. restricted cash)"
    # growth never compares a cell that still counts restricted cash (2024, nothing separates it) with one that deducts it
    # (2025): FY2025 and the four 2025 quarters are blank on both lines; 2026 vs 2025 (both deducted) stays
    assert nc["growth_annual"] == [None, None] and ncps["growth_annual"] == [None, None]
    assert nc["growth_quarterly"][4:8] == [None] * 4 and ncps["growth_quarterly"][4:8] == [None] * 4
    for i in (8, 9):
        j = i - 4
        assert approx(nc["growth_quarterly"][i], nc["quarterly"][i] / nc["quarterly"][j] - 1), (i, nc["growth_quarterly"])
        assert ncps["growth_quarterly"][i] is not None
    # (the fixture files no income tax, so there is no ROIC proxy line to flag: its deduction is checked on derive_value below)
    assert line(st, "metrics", "roic_proxy") is None
    # lines that do not treat cash as available carry no flag, keep their label and their growth
    wc = line(st, "metrics", "working_capital")
    assert "incl_restricted_annual" not in wc and "incl_restricted_annual" not in line(st, "metrics", "total_debt") and wc["label"] == "Working capital"
    assert wc["growth_annual"][1] is not None
    w = [x for x in warnings if x.startswith("restricted cash:")]
    assert len(w) == 2 and "in 10 period(s), 2024-03-31..2026-06-30 the cash line is the filed cash + restricted cash total" in w[0], w
    assert "in 6 period(s), 2025-03-31..2026-06-30 the restricted part is the restricted-cash figure filed for the same date (RestrictedCash)" in w[0], w
    assert "in 4 period(s), 2024-03-31..2024-12-31 no figure separates the restricted part" in w[0], w
    assert w[1].startswith("restricted cash: 10 growth cell(s) are blank because one of the two periods deducts restricted cash"), w
    assert "net_cash (FY ending 2025-12-31; quarters 2025-03-31, 2025-06-30, 2025-09-30, 2025-12-31)" in w[1], w
    json.dumps(st, allow_nan=False)
    # derive_value directly with NTRS's FY2025 cells (the tag decides; no tag_of = a cash-only line, nothing deducted)
    vals = {"cash": 5_873_100_000, "restricted_cash": 531_200_000, "total_debt": debt}
    no_sti = lambda k: k != "short_term_investments"  # noqa: E731
    assert S.derive_value("net_cash", vals.get, no_sti, lambda k: COMB if k == "cash" else None) == 1_990_400_000
    assert S.derive_value("net_cash", vals.get, no_sti) == 2_521_600_000
    assert S.derive_value("net_cash", vals.get, no_sti, lambda k: "CashAndCashEquivalentsAtCarryingValue" if k == "cash" else None) == 2_521_600_000
    roic = {"operating_income": 100, "income_tax": 21, "pretax_income": 100, "total_common_equity": 500, "total_debt": 300, "cash": 200, "restricted_cash": 50}
    assert approx(S.derive_value("roic_proxy", roic.get, lambda k: True, lambda k: COMB if k == "cash" else None), 79 / (500 + 300 - 150))
    assert approx(S.derive_value("roic_proxy", roic.get, lambda k: True), 79 / (500 + 300 - 200))


def test_restricted_cash_only_where_the_cash_line_is_the_combined_total():
    """A separate restricted-cash caption next to a cash-only line is not part of that line: no deduction, no line, no
    flag — the output is identical to the same filer without the caption. Where the combined total takes over (2026
    here) the restricted part is deducted; a restricted figure above the cash figure is not, and is warned."""
    base = S.build_statements(make_facts(), [])
    facts = make_facts()
    facts["facts"]["us-gaap"]["RestrictedCash"] = {"units": {"USD": _instant_entries({e: 30 for e in ALL_ENDS})}}
    with_caption = S.build_statements(facts, [])
    assert with_caption[1] == base[1] and with_caption[3] == base[3]
    assert line(base[1], "balance", "restricted_cash") is None
    assert not any(k.startswith("incl_restricted") for lines in base[1].values() for l in lines for k in l)
    # the combined total only for the 2026 quarter ends; RestrictedCash for every date, 500 > the 420 of cash at 2026-06-30
    us = facts["facts"]["us-gaap"]
    us["CashAndCashEquivalentsAtCarryingValue"]["units"]["USD"] = [e for e in us["CashAndCashEquivalentsAtCarryingValue"]["units"]["USD"] if not e["end"].startswith("2026")]
    us[COMB] = {"units": {"USD": _instant_entries({"2026-03-31": 400, "2026-06-30": 420})}}
    us["RestrictedCash"] = {"units": {"USD": _instant_entries(dict({e: 30 for e in ALL_ENDS}, **{"2026-06-30": 500}))}}
    _, st, _, warnings = S.build_statements(facts, [])
    c = line(st, "balance", "cash")
    assert c["label"] == "Cash & equivalents (some periods incl. restricted cash)" and c["quarterly"] == [CASH[e] for e in ALL_ENDS[:8]] + [400, 420]
    assert c["incl_restricted_annual"] == [False, False] and c["incl_restricted_quarterly"] == [False] * 8 + [True, True] and c["incl_restricted_ttm"] is True
    r = line(st, "balance", "restricted_cash")
    assert r["annual"] == [None, None] and r["quarterly"] == [None] * 8 + [30, None] and r["ttm"] is None
    nc = line(st, "metrics", "net_cash")
    assert nc["annual"] == [CASH["2024-12-31"] - 200, CASH["2025-12-31"] - 200]  # cash-only cells: unchanged
    assert nc["quarterly"][:8] == [CASH[e] - 200 for e in ALL_ENDS[:8]] and nc["quarterly"][8] == 400 - 30 - 200 and nc["quarterly"][9] == 420 - 200
    assert nc["incl_restricted_quarterly"] == [False] * 9 + [True] and nc["incl_restricted_annual"] == [False, False]
    assert nc["ttm"] == 220 and nc["incl_restricted_ttm"] is True
    # growth: 2026-03-31 (restricted deducted) vs 2025-03-31 (the cash-only caption) is one basis — kept; 2026-06-30
    # (restricted cash still in) vs 2025-06-30 (cash-only) is not — blank
    assert approx(nc["growth_quarterly"][8], 170 / (CASH["2025-03-31"] - 200) - 1) and nc["growth_quarterly"][9] is None
    w = [x for x in warnings if x.startswith("restricted cash:")]
    assert len(w) == 2 and "outside 0..cash was not deducted: 2026-06-30 (500 of RestrictedCash vs cash 420)" in w[0], w
    assert "net_cash (quarters 2026-06-30)" in w[1], w


def _inst(end, val, form, filed, accn):
    """One balance-sheet fact as a specific filing reported it (a 10-K for its own year end, or any later comparative)."""
    return {"end": end, "val": val, "fy": int(filed[:4]), "fp": "FY" if form == "10-K" else "Q1", "form": form, "filed": filed, "accn": accn}


def _drop(us, tag, ends):
    us[tag]["units"]["USD"] = [x for x in us[tag]["units"]["USD"] if x["end"] not in ends]


def test_restricted_cash_same_date_cash_only_caption():
    """Verifier round on the Codex fix: a combined year-end cell whose date also carries the cash-only caption.
    ZTS FY2025: the 10-K tags only the combined total; the 2026 10-Qs file 2,450M of BOTH for 2025-12-31 (so nothing
    restricted is inside), yet RestrictedCashCurrent says 2M — the fix deducted it, so the FY2025 column read 2M less net
    cash than the 2025-12-31 quarter column (cash-only caption). Now the filing that reports both decides: part 0, the
    two columns agree, nothing is marked. A cash-only figure from another filing generation is no evidence (ZTS
    2024-12-31: the 2025 10-Qs' 1,987M of both vs the 2026 10-Qs' restated 2,114M total) — the tagged restricted figure
    is used there."""
    facts = make_facts()
    us = facts["facts"]["us-gaap"]
    c0 = "CashAndCashEquivalentsAtCarryingValue"
    _drop(us, c0, ("2024-12-31", "2025-12-31"))
    us[c0]["units"]["USD"] += [_inst("2024-12-31", 1987, "10-Q", f, a) for f, a in (("2025-05-01", "acc-2025-03-31"), ("2025-08-01", "acc-2025-06-30"))]
    us[c0]["units"]["USD"] += [_inst("2025-12-31", 2450, "10-Q", f, a) for f, a in (("2026-05-01", "acc-2026-03-31"), ("2026-08-01", "acc-2026-06-30"))]
    us[COMB] = {"units": {"USD": [_inst("2024-12-31", 1987, "10-K", "2025-02-20", "acc-2024-12-31"),
                                  _inst("2024-12-31", 1987, "10-Q", "2025-05-01", "acc-2025-03-31"), _inst("2024-12-31", 1987, "10-Q", "2025-08-01", "acc-2025-06-30"),
                                  _inst("2024-12-31", 2114, "10-Q", "2026-05-01", "acc-2026-03-31"), _inst("2024-12-31", 2114, "10-Q", "2026-08-01", "acc-2026-06-30"),
                                  _inst("2025-12-31", 2312, "10-K", "2026-02-19", "acc-2025-12-31"),
                                  _inst("2025-12-31", 2450, "10-Q", "2026-05-01", "acc-2026-03-31"), _inst("2025-12-31", 2450, "10-Q", "2026-08-01", "acc-2026-06-30")]}}
    us["RestrictedCashCurrent"] = {"units": {"USD": [_inst("2024-12-31", 2, "10-K", "2025-02-20", "acc-2024-12-31"),
                                                     _inst("2025-12-31", 2, "10-K", "2026-02-19", "acc-2025-12-31"),
                                                     _inst("2025-12-31", 2, "10-Q", "2026-08-01", "acc-2026-06-30")]}}
    _, st, _, warnings = S.build_statements(facts, [])
    c, nc = line(st, "balance", "cash"), line(st, "metrics", "net_cash")
    # the annual cells read the combined tag (no 10-K filed the cash-only caption for its year end), newest value
    assert c["annual"] == [2114, 2450] and c["quarterly"][3] == 1987 and c["quarterly"][7] == 2450
    # FY2025: 2,450 − 0 → net cash 2,250 in both columns (the fix gave 2,248 in the annual one); not marked
    assert nc["annual"][1] == 2450 - 200 == nc["quarterly"][7]
    assert c["incl_restricted_annual"] == [True, False] and c["incl_restricted_quarterly"] == [False] * 10
    # FY2024: the 1,987 pair is another generation than the 2,114 total — the tagged 2 is the restricted part
    r = line(st, "balance", "restricted_cash")
    assert r["annual"] == [2, None] and r["quarterly"] == [None] * 10 and r["tags"] == ["RestrictedCashCurrent"]
    assert nc["annual"][0] == 2114 - 2 - 200 and "incl_restricted_annual" not in nc and nc["label"] == "Net cash (debt)"
    assert approx(nc["growth_annual"][1], 2250 / 1912 - 1)
    w = [x for x in warnings if x.startswith("restricted cash:")]
    assert len(w) == 1 and "in 1 period, 2025-12-31 it holds no restricted cash" in w[0] and "in 1 period, 2024-12-31 the restricted part is the restricted-cash figure" in w[0], w

    # YUM FY2016: the 10-K's 831M total, a 10-Q's 725M cash-only caption for the same date, no filing with both and no
    # restricted tag — nothing separates the part: flagged, and the growth into the next (cash-only) year is blank.
    # APP / RBLX 2019-12-31: the cash-only caption equals the total to the dollar (different filings) — part 0.
    facts = make_facts()
    us = facts["facts"]["us-gaap"]
    _drop(us, c0, ("2024-12-31", "2025-12-31"))
    us[c0]["units"]["USD"] += [_inst("2024-12-31", 725, "10-Q", "2025-05-01", "acc-2025-03-31"), _inst("2025-12-31", 700, "10-Q", "2026-05-01", "acc-2026-03-31")]
    us[COMB] = {"units": {"USD": [_inst("2024-12-31", 831, "10-K", "2025-02-20", "acc-2024-12-31"), _inst("2025-12-31", 700, "10-K", "2026-02-19", "acc-2025-12-31")]}}
    _, st, _, warnings = S.build_statements(facts, [])
    c, nc = line(st, "balance", "cash"), line(st, "metrics", "net_cash")
    assert c["annual"] == [831, 700] and c["incl_restricted_annual"] == [True, False] and line(st, "balance", "restricted_cash") is None
    assert nc["annual"] == [631, 500] and nc["incl_restricted_annual"] == [True, False] and nc["growth_annual"] == [None, None]
    assert c["label"] == "Cash & equivalents (some periods incl. restricted cash)" and nc["label"] == "Net cash (debt) (some periods incl. restricted cash)"
    w = [x for x in warnings if x.startswith("restricted cash:")]
    assert "in 1 period, 2024-12-31 no figure separates the restricted part" in w[0] and "in 1 period, 2025-12-31 it holds no restricted cash" in w[0], w
    assert "net_cash (FY ending 2025-12-31)" in w[1], w


def test_restricted_cash_noncurrent_and_parts():
    """Verifier round: the restricted part of a combined total is current AND noncurrent restricted cash. U files only
    RestrictedCashNoncurrent (14.6M at 2019-09-30) — before, its cells said 'no restricted-cash figure separates it';
    a filer with both captions had only the current one deducted. A restricted TOTAL wins over its parts (U 2022-03-31:
    RestrictedCashAndCashEquivalents and RestrictedCashNoncurrent both 10,678K — counted once)."""
    facts, cash, _ = _restricted_facts()
    us = facts["facts"]["us-gaap"]
    del us["RestrictedCash"]
    us["RestrictedCashCurrent"] = {"units": {"USD": _instant_entries({e: 30_000_000 for e in ALL_ENDS[:4]})}}
    us["RestrictedCashNoncurrent"] = {"units": {"USD": _instant_entries(dict({e: 50_000_000 for e in ALL_ENDS[:8]}, **{e: 70_000_000 for e in ALL_ENDS[8:]}))}}
    us["RestrictedCashAndCashEquivalents"] = {"units": {"USD": _instant_entries({e: 70_000_000 for e in ALL_ENDS[8:]})}}
    _, st, _, warnings = S.build_statements(facts, [])
    r = line(st, "balance", "restricted_cash")
    assert r["quarterly"] == [80_000_000] * 4 + [50_000_000] * 4 + [70_000_000] * 2, r["quarterly"]
    assert r["annual"] == [80_000_000, 50_000_000]
    assert r["tags"] == ["RestrictedCashAndCashEquivalents", "RestrictedCashCurrent+RestrictedCashNoncurrent", "RestrictedCashNoncurrent"], r["tags"]
    nc = line(st, "metrics", "net_cash")
    assert nc["quarterly"] == [cash[e] - r["quarterly"][i] - 3_351_500_000 for i, e in enumerate(ALL_ENDS)]
    assert "incl_restricted_annual" not in nc and nc["label"] == "Net cash (debt)"  # every cell separated: nothing flagged
    c = line(st, "balance", "cash")
    assert c["label"] == "Cash, equivalents & restricted cash" and c["incl_restricted_quarterly"] == [True] * 10
    assert all(g is not None for g in nc["growth_quarterly"][4:])  # one basis throughout: growth kept
    w = [x for x in warnings if x.startswith("restricted cash:")]
    assert len(w) == 1 and "(RestrictedCashAndCashEquivalents, RestrictedCashCurrent+RestrictedCashNoncurrent, RestrictedCashNoncurrent)" in w[0], w


def test_restricted_cash_growth_kept_where_the_caption_does_not_say():
    """Growth is blanked only between a period that still counts restricted cash (combined, unseparated) and one that
    does not (deducted, or the cash-only caption). A caption that does not say — NTRS's CashAndDueFromBanks before
    2016, equal to its combined total wherever both are filed — is no break: NTRS FY2016 vs FY2015 keeps its −22.1%."""
    facts, cash, rc = _restricted_facts()
    us = facts["facts"]["us-gaap"]
    _drop(us, COMB, ALL_ENDS[:4])
    us["CashAndDueFromBanks"] = {"units": {"USD": _instant_entries({e: cash[e] for e in ALL_ENDS[:4]})}}
    # restricted cash tagged only from 2026: 2024 = the bank caption, 2025 = combined, not separated, 2026 = deducted
    us["RestrictedCash"] = {"units": {"USD": _instant_entries({e: rc[e] for e in ALL_ENDS[8:]})}}
    _, st, _, warnings = S.build_statements(facts, [])
    nc = line(st, "metrics", "net_cash")
    assert nc["incl_restricted_quarterly"] == [False] * 4 + [True] * 4 + [False] * 2 and nc["incl_restricted_annual"] == [False, True]
    assert nc["growth_annual"][1] is not None and all(g is not None for g in nc["growth_quarterly"][4:8])  # caption vs combined: kept
    assert nc["growth_quarterly"][8:] == [None, None]  # deducted vs not separated: blank
    w = [x for x in warnings if x.startswith("restricted cash:")]
    assert "net_cash (quarters 2026-03-31, 2026-06-30)" in w[1], w


def test_restricted_cash_rebuild_rule():
    """--all rebuilds a file written before the split only when its cash line used the combined tag; others stay skipped."""
    latest = {"form": "10-Q", "filed": "2026-08-01", "period": "2026-06-30"}
    current = {"latest_filed": dict(latest), "schema_version": S.SCHEMA_VERSION, "covered_through": "2026-06-30",
               "statements": {"balance": [{"key": "cash", "tags": ["CashAndCashEquivalentsAtCarryingValue"]}]}}
    assert S.can_skip(current, latest) and not S.restricted_cash_pending(current)
    old = copy.deepcopy(current)
    old["statements"]["balance"][0]["tags"].append(COMB)
    assert S.restricted_cash_pending(old) and not S.can_skip(old, latest)
    new = copy.deepcopy(old)
    new["statements"]["balance"][0].update(incl_restricted_annual=[True], incl_restricted_quarterly=[True], incl_restricted_ttm=True)
    assert S.can_skip(new, latest)
    # a rebuilt file whose combined cells all hold no restricted cash (ZTS: the cash-only caption equals each total)
    # still records the split — all-False marks on the cash line — so --all does not re-download it every run
    facts = make_facts()
    us = facts["facts"]["us-gaap"]
    _drop(us, "CashAndCashEquivalentsAtCarryingValue", ("2025-12-31",))
    us["CashAndCashEquivalentsAtCarryingValue"]["units"]["USD"].append(_inst("2025-12-31", 700, "10-Q", "2026-05-01", "acc-2026-03-31"))
    us[COMB] = {"units": {"USD": [_inst("2025-12-31", 700, "10-K", "2026-02-19", "acc-2025-12-31"), _inst("2025-12-31", 700, "10-Q", "2026-05-01", "acc-2026-03-31")]}}
    _, st, _, _ = S.build_statements(facts, [])
    c = line(st, "balance", "cash")
    assert COMB in c["tags"] and c["incl_restricted_annual"] == [False, False] and c["incl_restricted_quarterly"] == [False] * 10 and c["label"] == "Cash & equivalents"
    built = dict(current, statements=st)
    assert not S.restricted_cash_pending(built) and S.can_skip(built, latest)
    for bad in ({"statements": None}, {"statements": {"balance": "x"}}, {"statements": {"balance": [{"key": "cash", "tags": None}]}}):
        assert S.restricted_cash_pending(bad) is False


def test_stable_write_only_when_content_changes():
    """statements.json is committed: a rebuild that changes nothing but as_of leaves the file byte-for-byte alone (and
    --all reports it as unchanged); a real change rewrites it with today's as_of."""
    import contextlib
    import io
    sub = {"cik": "999", "fiscalYearEnd": "1231", "filings": {"recent": {"form": ["10-Q"], "filingDate": ["2026-08-01"], "reportDate": ["2026-06-30"]}}}
    tmp = tempfile.mkdtemp(prefix="statements_stable_")
    old_base = S.BASE
    try:
        cache, folder = os.path.join(tmp, "cache"), os.path.join(tmp, "FIX")
        os.makedirs(cache)
        os.makedirs(folder)
        for name, obj in (("FIX.sub.json", sub), ("FIX.facts.json", make_facts())):
            with open(os.path.join(cache, name), "w", encoding="utf-8") as f:
                json.dump(obj, f)
        S.BASE = tmp
        path = os.path.join(folder, "statements.json")
        s1, _ = S.run_one("FIX", cik=999, write=True, cache=cache, force=True)
        assert s1["written"] is True
        with open(path, encoding="utf-8") as f:
            text = f.read()
        assert text.startswith('{"ticker":"FIX","cik":999,') and "NaN" not in text and "\n" not in text  # the same compact dump as before
        # an older as_of on disk: the rebuild has the same content, so the file (and its as_of) is left exactly as it was
        doc = json.loads(text)
        doc["as_of"] = "2000-01-01"
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(doc, f, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
        with open(path, "rb") as f:
            before = f.read()
        s2, _ = S.run_one("FIX", cik=999, write=True, cache=cache, force=True)
        with open(path, "rb") as f:
            assert s2["written"] is False and f.read() == before
        assert S.run_one("FIX", cik=999, write=False, cache=cache, force=True)[0]["written"] is None
        # --all: forced rebuild with nothing new -> unchanged; without --force -> skipped (companyfacts not read)
        with open(os.path.join(folder, "score.json"), "w", encoding="utf-8") as f:
            json.dump({"ticker": "FIX"}, f)
        with open(os.path.join(folder, "dcf_numbers.json"), "w", encoding="utf-8") as f:
            json.dump({"cik": 999}, f)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            assert S.main(["--all", "--force", "--cache", cache]) == 0
        assert "content unchanged, file left as is" in out.getvalue() and "--all: 0 written, 1 unchanged" in out.getvalue(), out.getvalue()
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            assert S.main(["--all", "--cache", cache]) == 0
        assert "--all: 0 written, 0 unchanged" in out.getvalue() and "1 skipped" in out.getvalue(), out.getvalue()
        # a real change (a restated cash figure) -> written, with today's as_of
        facts = make_facts()
        facts["facts"]["us-gaap"]["CashAndCashEquivalentsAtCarryingValue"]["units"]["USD"][-1]["val"] += 1
        with open(os.path.join(cache, "FIX.facts.json"), "w", encoding="utf-8") as f:
            json.dump(facts, f)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            assert S.main(["--all", "--force", "--cache", cache]) == 0
        assert "--all: 1 written, 0 unchanged" in out.getvalue(), out.getvalue()
        with open(path, encoding="utf-8") as f:
            doc = json.load(f)
        assert doc["as_of"] == S._et_today().isoformat() and line(doc["statements"], "balance", "cash")["ttm"] == CASH["2026-06-30"] + 1
        assert not [p for p in os.listdir(folder) if p.endswith(".tmp")]  # the atomic write leaves no temp file
    finally:
        S.BASE = old_base
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    failed = 0
    for name, fn in sorted((k, v) for k, v in globals().items() if k.startswith("test_") and callable(v)):
        try:
            fn()
            print(f"PASS {name}")
        except Exception as e:  # noqa: BLE001
            failed += 1
            import traceback
            traceback.print_exc()
            print(f"FAIL {name}: {e}")
    sys.exit(1 if failed else 0)
