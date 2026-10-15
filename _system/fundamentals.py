#!/usr/bin/env python3
"""Filing-direct fundamentals store (v5.4, 2026-10-14).

Usage: python3 fundamentals.py <TICKER> [--cik N] [--no-write]

Pulls the SEC EDGAR data a READER of the company page needs but the valuation
engine does not, and writes <TICKER>/fundamentals.json. The company page's
Financials and Data tabs render from it. Nothing here feeds the DCF —
dcf_numbers.json stays the engine's domain and score.json make_score's.

Contents (every figure is a filed value, or arithmetic on filed values —
growth, margins, quarter = YTD minus prior YTD; nothing is estimated):
- profile: SIC, fiscal year end, filer category, exchanges, latest 10-K /
  10-Q filed + period, 8-K count last 12 months (EDGAR submissions API).
- annual: up to 10 fiscal years of income statement, cash flow and balance
  sheet lines (revenue, COGS, gross profit, R&D, SG&A, operating income,
  interest, pretax, tax, net income, EPS, shares, OCF, capex, SBC, D&A,
  dividends, buybacks, acquisitions, cash, debt, leases, assets, equity,
  goodwill, prepaids, deferred revenue) with margins, growth rates, per-share
  figures, ROE and an ROIC proxy, and the tag that supplied each core line.
- quarterly: the last 12 fiscal quarters. Income-statement lines come from the
  filed 3-month facts where present; cash-flow lines (filed year-to-date
  only) are derived as YTD minus the prior YTD in the same fiscal year, and
  Q4 as FY minus the nine-month YTD. `derived` says which.
- ttm: the sum of the last four quarters when all four exist.
Units are the filer's own (USD for almost every name; `currency` records
anything else). No FX conversion is applied here — the engine handles that
for the valuation; this file is for reading the filings as filed.
"""
import json, sys, os, csv, datetime, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
BASE = os.environ.get("STOCKS_BASE") or os.path.dirname(HERE)
SYS = f"{BASE}/_system"
UA = {"User-Agent": "Muse research andrewmauro199612@gmail.com"}
IF = "ifrs-full"
ET_TODAY = datetime.date.today()


def get_json(url, timeout=90):
    last = None
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read())
        except Exception as e:
            last = e
            if attempt < 2:
                time.sleep(2 ** attempt)
    raise last


def resolve_cik(ticker, nums):
    if "--cik" in sys.argv:
        return int(sys.argv[sys.argv.index("--cik") + 1])
    if nums.get("cik"):
        return int(nums["cik"])  # the CIK the engine actually used (covers --cik and the fallback probe)
    try:
        sec = json.load(open(f"{SYS}/sec_tickers_exchange.json"))
        m = {}
        for rec in sec["data"]:
            m.setdefault(rec[2].upper(), rec[0])
        for cand in (ticker, ticker.replace("/", "-"), ticker.replace("/", ".")):
            if cand in m:
                return m[cand]
    except Exception:
        pass
    try:
        with open(f"{SYS}/universe.csv") as f:
            for row in csv.DictReader(f):
                if row["ticker"] == ticker and row.get("cik"):
                    return int(row["cik"])
    except Exception:
        pass
    return None


# ---------------------------------------------------------------------------
# Tag maps (us-gaap candidates first, then ifrs-full pairs) — display breadth,
# wider than the engine's valuation set.
# ---------------------------------------------------------------------------
DUR = {
    "revenue": ["RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet", "Revenues", "RevenueFromContractWithCustomerIncludingAssessedTax",
                "InterestAndDividendIncomeOperating", "InterestIncomeExpenseNet", (IF, "Revenue"), (IF, "RevenueFromContractsWithCustomers")],
    # Banks / lenders: "revenue" is net interest income + noninterest income
    # (or the filer's own Revenues total); RevenueFromContract... is fee income only.
    "nii": ["InterestIncomeExpenseNet", "InterestIncomeExpenseAfterProvisionForLoanLoss"],
    "noninterest_income": ["NoninterestIncome"],
    "revenues_total": ["Revenues"],
    "cogs": ["CostOfRevenue", "CostOfGoodsAndServicesSold", "CostOfGoodsSold", "CostOfServices", (IF, "CostOfSales")],
    "gross_profit": ["GrossProfit", (IF, "GrossProfit")],
    "rnd": ["ResearchAndDevelopmentExpense", "ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost", (IF, "ResearchAndDevelopmentExpense")],
    "sga": ["SellingGeneralAndAdministrativeExpense", (IF, "SellingGeneralAndAdministrativeExpense")],
    "sm": ["SellingAndMarketingExpense", "SalesAndMarketingExpense"],
    "ga": ["GeneralAndAdministrativeExpense"],
    "operating_income": ["OperatingIncomeLoss", (IF, "ProfitLossFromOperatingActivities")],
    "interest_expense": ["InterestExpense", "InterestExpenseNonoperating", "InterestExpenseDebt", "InterestAndDebtExpense", (IF, "InterestExpense")],
    "pretax_income": ["IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest",
                      "IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments", (IF, "ProfitLossBeforeTax")],
    "tax": ["IncomeTaxExpenseBenefit", (IF, "IncomeTaxExpenseContinuingOperations"), (IF, "IncomeTaxExpense")],
    "net_income": ["NetIncomeLoss", "ProfitLoss", (IF, "ProfitLoss")],
    "disc_ops": ["IncomeLossFromDiscontinuedOperationsNetOfTax", "DiscontinuedOperationsIncomeLossNetOfTax"],
    "nonop": ["NonoperatingIncomeExpense", "OtherNonoperatingIncomeExpense"],
    "eps_diluted": ["EarningsPerShareDiluted", (IF, "DilutedEarningsLossPerShare")],
    "eps_basic": ["EarningsPerShareBasic", (IF, "BasicEarningsLossPerShare")],
    "shares_diluted": ["WeightedAverageNumberOfDilutedSharesOutstanding", "WeightedAverageNumberOfSharesOutstandingDiluted", (IF, "AdjustedWeightedAverageShares")],
    "shares_basic": ["WeightedAverageNumberOfSharesOutstandingBasic", (IF, "WeightedAverageShares")],
    "ocf": ["NetCashProvidedByUsedInOperatingActivities", "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations",
            (IF, "CashFlowsFromUsedInOperatingActivities"), (IF, "CashFlowsFromUsedInOperatingActivitiesContinuingOperations")],
    "icf": ["NetCashProvidedByUsedInInvestingActivities", (IF, "CashFlowsFromUsedInInvestingActivities")],
    "fincf": ["NetCashProvidedByUsedInFinancingActivities", (IF, "CashFlowsFromUsedInFinancingActivities")],
    "capex": ["PaymentsToAcquirePropertyPlantAndEquipment", "PaymentsForConstructionInProcess", "PaymentsToAcquireOtherPropertyPlantAndEquipment",
              "PaymentsToAcquireProductiveAssets", "PaymentsToAcquireOtherProductiveAssets",
              (IF, "PurchaseOfPropertyPlantAndEquipmentClassifiedAsInvestingActivities"), (IF, "PurchaseOfPropertyPlantAndEquipment")],
    "capex_intangibles": ["PaymentsToAcquireIntangibleAssets", "PaymentsToDevelopSoftware", (IF, "PurchaseOfIntangibleAssetsClassifiedAsInvestingActivities")],
    "da": ["DepreciationDepletionAndAmortization", "DepreciationAmortizationAndAccretionNet", "DepreciationAndAmortization", "Depreciation",
           (IF, "AdjustmentsForDepreciationAndAmortisationExpense"), (IF, "DepreciationAndAmortisationExpense")],
    "sbc": ["ShareBasedCompensation", "AllocatedShareBasedCompensationExpense", (IF, "AdjustmentsForSharebasedPayments")],
    "dividends_paid": ["PaymentsOfDividends", "PaymentsOfDividendsCommonStock", "PaymentsOfOrdinaryDividends", (IF, "DividendsPaidClassifiedAsFinancingActivities")],
    "buybacks": ["PaymentsForRepurchaseOfCommonStock", (IF, "PaymentsToAcquireOrRedeemEntitysShares")],
    "acquisitions": ["PaymentsToAcquireBusinessesNetOfCashAcquired", "PaymentsToAcquireBusinessesGross", (IF, "CashFlowsUsedInObtainingControlOfSubsidiariesOrOtherBusinessesClassifiedAsInvestingActivities")],
}
INST = {
    "cash": ["CashAndCashEquivalentsAtCarryingValue", "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents", (IF, "CashAndCashEquivalents")],
    "short_term_investments": ["ShortTermInvestments", "MarketableSecuritiesCurrent", "AvailableForSaleSecuritiesDebtSecuritiesCurrent"],
    "receivables": ["AccountsReceivableNetCurrent", (IF, "TradeAndOtherCurrentReceivables")],
    "inventory": ["InventoryNet", (IF, "Inventories")],
    "prepaids": ["PrepaidExpenseAndOtherAssetsCurrent", "PrepaidExpenseCurrent"],
    "assets_current": ["AssetsCurrent", (IF, "CurrentAssets")],
    "ppe_net": ["PropertyPlantAndEquipmentNet", (IF, "PropertyPlantAndEquipment")],
    "goodwill": ["Goodwill", (IF, "Goodwill")],
    "intangibles": ["IntangibleAssetsNetExcludingGoodwill", (IF, "IntangibleAssetsOtherThanGoodwill")],
    "assets": ["Assets", (IF, "Assets")],
    "liab_current": ["LiabilitiesCurrent", (IF, "CurrentLiabilities")],
    "deferred_revenue": ["ContractWithCustomerLiabilityCurrent", "DeferredRevenueCurrent"],
    "debt_current": ["DebtCurrent", "LongTermDebtCurrent", "LongTermDebtAndCapitalLeaseObligationsCurrent", "ShortTermBorrowings", "CommercialPaper", "NotesPayableCurrent",
                     (IF, "CurrentPortionOfLongtermBorrowings"), (IF, "CurrentBorrowingsAndCurrentPortionOfNoncurrentBorrowings"), (IF, "ShorttermBorrowings")],
    "debt_lt": ["LongTermDebtNoncurrent", "LongTermDebtAndCapitalLeaseObligations", "LongTermNotesPayable", (IF, "LongtermBorrowings"), (IF, "NoncurrentPortionOfNoncurrentBorrowings")],
    "debt_total": ["LongTermDebt", "DebtLongtermAndShorttermCombinedAmount", "LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities", (IF, "Borrowings")],
    "lease_liab_current": ["OperatingLeaseLiabilityCurrent", (IF, "CurrentLeaseLiabilities")],
    "lease_liab_lt": ["OperatingLeaseLiabilityNoncurrent", (IF, "NoncurrentLeaseLiabilities")],
    "liabilities": ["Liabilities", (IF, "Liabilities")],
    "equity": ["StockholdersEquity", "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest", (IF, "Equity")],
    "retained_earnings": ["RetainedEarningsAccumulatedDeficit", (IF, "RetainedEarnings")],
    "shares_outstanding": ["CommonStockSharesOutstanding", (IF, "NumberOfSharesOutstanding")],
}
QUARTERLY_FIELDS = ["revenue", "gross_profit", "operating_income", "net_income", "ocf", "capex", "sbc", "da", "eps_diluted", "shares_diluted"]
DIRECT_ONLY = {"eps_diluted", "shares_diluted"}  # ratios / averages: never derived by subtraction
UNIT_PREF = ("USD", "shares", "USD/shares")


def _days(a, b):
    return (datetime.date.fromisoformat(b) - datetime.date.fromisoformat(a)).days


def _pairs(tags):
    return [(t if isinstance(t, tuple) else ("us-gaap", t)) for t in tags]


def _units_pref(units):
    pref = [u for u in UNIT_PREF if u in units]
    return pref + [u for u in units if u not in pref]


def annual_series(facts, tags, duration=True):
    """{period_end: val}, {period_end: tag}, {period_end: unit} — FY facts on
    annual forms, merged across candidate tags per period, latest filing wins."""
    merged, tag_by, unit_by = {}, {}, {}
    for taxonomy, tag in _pairs(tags):
        tf = facts.get("facts", {}).get(taxonomy, {})
        if tag not in tf:
            continue
        units = tf[tag].get("units", {})
        for unit_key in _units_pref(units):
            best = {}
            for e in units[unit_key]:
                if e.get("fp") != "FY" or e.get("form", "") not in ("10-K", "10-K/A", "20-F", "40-F"):
                    continue
                end, start = e.get("end"), e.get("start")
                if not end:
                    continue
                if duration:
                    if not start or not (330 <= _days(start, end) <= 380):
                        continue
                elif start and start != end:
                    continue
                prev = best.get(end)
                if prev is None or e.get("filed", "") > prev.get("filed", ""):
                    best[end] = e
            for k, v in best.items():
                if k not in merged:
                    merged[k], tag_by[k], unit_by[k] = v["val"], tag, unit_key
    return merged, tag_by, unit_by


def duration_facts(facts, tags):
    """{(start, end): (val, tag, unit)} across 10-Q/10-K/20-F/40-F forms, merged per period by tag priority."""
    out = {}
    for taxonomy, tag in _pairs(tags):
        tf = facts.get("facts", {}).get(taxonomy, {})
        if tag not in tf:
            continue
        units = tf[tag].get("units", {})
        for unit_key in _units_pref(units):
            best = {}
            for e in units[unit_key]:
                if e.get("form", "") not in ("10-Q", "10-Q/A", "10-K", "10-K/A", "20-F", "40-F", "6-K"):
                    continue
                s, en = e.get("start"), e.get("end")
                if not s or not en:
                    continue
                key = (s, en)
                prev = best.get(key)
                if prev is None or e.get("filed", "") > prev.get("filed", ""):
                    best[key] = e
            for k, v in best.items():
                if k not in out:
                    out[k] = (v["val"], tag, unit_key)
    return out


def quarterly_series(facts, tags, derive=True):
    """{quarter_end: {val, fq, fy_start, derived, tag}} for the fiscal quarters
    the filer's facts support. Direct 3-month facts win; otherwise (cash-flow
    lines are filed YTD only) quarter = YTD - prior YTD within the same
    fiscal year, Q4 = FY - nine-month YTD."""
    f = duration_facts(facts, tags)
    if not f:
        return {}
    annual_keys = [(s, e) for (s, e) in f if 330 <= _days(s, e) <= 380]
    fy_starts = {s for s, _ in annual_keys}
    for _, e in annual_keys:  # the fiscal year that follows each filed annual period
        fy_starts.add((datetime.date.fromisoformat(e) + datetime.timedelta(days=1)).isoformat())
    direct = {(s, e): v for (s, e), v in f.items() if 80 <= _days(s, e) <= 100}
    out = {}
    for s in sorted(fy_starts):
        # Rank each YTD leg by its length: ~1, 2, 3 or 4 quarters (±35 days
        # tolerates 52/53-week years and 16-week first quarters). A quarter
        # is derived ONLY from the leg one rank shorter — a missing leg
        # (e.g. capex filed on the 10-K alone) must never make the annual
        # total masquerade as a quarter.
        by_rank = {}
        for (s2, e) in f:
            if s2 != s:
                continue
            d = _days(s, e)
            if d > 380:
                continue
            rank = round(d / 91.25)
            if 1 <= rank <= 4 and abs(d - rank * 91.25) <= 35 and rank not in by_rank:
                by_rank[rank] = e
        prev_val, last_rank = 0.0, 0
        for rank in (1, 2, 3, 4):
            e = by_rank.get(rank)
            if e is None:
                continue
            v = f[(s, e)][0]
            dq = [(k, dv) for k, dv in direct.items() if k[1] == e]
            if dq:
                out[e] = {"val": dq[0][1][0], "fq": rank, "fy_start": s, "derived": False, "tag": dq[0][1][1], "ytd": v}
            elif derive and last_rank == rank - 1:
                out[e] = {"val": v - prev_val, "fq": rank, "fy_start": s, "derived": rank > 1, "tag": f[(s, e)][1], "ytd": v}
            prev_val, last_rank = v, rank
    # direct quarters not attached to a known FY start (fiscal-year start unknown)
    for (s, e), (v, tag, unit) in direct.items():
        if e not in out:
            fs = max((x for x in fy_starts if x <= s and _days(x, s) <= 300), default=None)
            fq = (round(_days(fs, e) / 91.25) if fs else None)
            out[e] = {"val": v, "fq": fq if fq and 1 <= fq <= 4 else None, "fy_start": fs, "derived": False, "tag": tag, "ytd": None}
    return out


def _g(cur, prev):
    """Growth rate, None when undefined (sign change through zero, missing)."""
    if cur is None or prev is None or prev == 0 or (prev < 0) != (cur < 0) and prev < 0:
        return None
    if prev < 0:
        return None
    return cur / prev - 1


def _ratio(a, b):
    return (a / b) if (a is not None and b not in (None, 0)) else None


def build_annual(facts):
    series, tags, units = {}, {}, {}
    for k, t in DUR.items():
        series[k], tags[k], units[k] = annual_series(facts, t, True)
    for k, t in INST.items():
        series[k], tags[k], units[k] = annual_series(facts, t, False)
    periods = sorted(set(series["revenue"]) | set(series["net_income"]) | set(series["ocf"]))[-10:]
    rows = []
    currency = set()
    for p in periods:
        g = lambda k: series[k].get(p)
        for k in ("revenue", "net_income", "ocf"):
            u = units[k].get(p)
            if u and u not in UNIT_PREF:
                currency.add(u)
        rev, ni, oi, ocf, capex, sbc, da = g("revenue"), g("net_income"), g("operating_income"), g("ocf"), g("capex"), g("sbc"), g("da")
        rev_basis = tags["revenue"].get(p)
        if g("noninterest_income") is not None and g("nii") is not None and g("nii") > 0:
            # bank presentation (NoninterestIncome is a bank-only tag)
            if g("revenues_total") is not None:
                rev, rev_basis = g("revenues_total"), "Revenues (bank total)"
            else:
                rev, rev_basis = g("nii") + g("noninterest_income"), "InterestIncomeExpenseNet + NoninterestIncome"
        cogs, gp = g("cogs"), g("gross_profit")
        if gp is None and rev is not None and cogs is not None:
            gp = rev - cogs
        if cogs is None and rev is not None and gp is not None:
            cogs = rev - gp
        sga = g("sga")
        if sga is None and (g("sm") is not None or g("ga") is not None):
            sga = (g("sm") or 0) + (g("ga") or 0)
        d_cur, d_lt, d_tot = g("debt_current"), g("debt_lt"), g("debt_total")
        if d_lt is not None:
            total_debt, debt_basis = d_lt + (d_cur or 0), "noncurrent+current"
        elif d_tot is not None:
            total_debt, debt_basis = d_tot, "total tag"
        elif d_cur is not None:
            total_debt, debt_basis = d_cur, "current only"
        else:
            total_debt, debt_basis = None, None
        cash = g("cash")
        net_debt = (total_debt - (cash or 0)) if total_debt is not None else None
        lease = None
        if g("lease_liab_lt") is not None or g("lease_liab_current") is not None:
            lease = (g("lease_liab_lt") or 0) + (g("lease_liab_current") or 0)
        fcf = (ocf - capex) if (ocf is not None and capex is not None) else None
        oe = (fcf - sbc) if (fcf is not None and sbc is not None) else None
        sh = g("shares_diluted")
        sh_src = tags["shares_diluted"].get(p)
        if sh is None and g("shares_basic") is not None:
            sh, sh_src = g("shares_basic"), f"BASIC:{tags['shares_basic'].get(p)}"
        eq = g("equity")
        pretax, tax = g("pretax_income"), g("tax")
        tax_rate = _ratio(tax, pretax) if (pretax and pretax > 0 and tax is not None and 0 <= tax / pretax <= 0.5) else 0.21
        invested = (eq + (total_debt or 0) - (cash or 0)) if eq is not None else None
        rows.append({
            "period_end": p, "fy": p[:4],
            "revenue": rev, "revenue_basis": rev_basis, "cogs": cogs, "gross_profit": gp, "gross_margin": _ratio(gp, rev),
            "rnd": g("rnd"), "sga": sga, "rnd_pct_rev": _ratio(g("rnd"), rev), "sga_pct_rev": _ratio(sga, rev),
            "operating_income": oi, "operating_margin": _ratio(oi, rev),
            "interest_expense": g("interest_expense"), "pretax_income": pretax, "tax": tax,
            "net_income": ni, "net_margin": _ratio(ni, rev), "disc_ops": g("disc_ops"), "nonop": g("nonop"),
            "eps_diluted": g("eps_diluted"), "eps_basic": g("eps_basic"),
            "shares_diluted": sh, "shares_tag": sh_src, "shares_outstanding": g("shares_outstanding"),
            "ocf": ocf, "icf": g("icf"), "fincf": g("fincf"), "capex": capex, "capex_intangibles": g("capex_intangibles"),
            "sbc": sbc, "da": da, "fcf": fcf, "oe_conservative": oe,
            "ocf_margin": _ratio(ocf, rev), "oe_margin": _ratio(oe, rev), "fcf_margin": _ratio(fcf, rev),
            "capex_pct_rev": _ratio(capex, rev), "sbc_pct_rev": _ratio(sbc, rev), "sbc_pct_ocf": _ratio(sbc, ocf),
            "dividends_paid": g("dividends_paid"), "buybacks": g("buybacks"), "acquisitions": g("acquisitions"),
            "shareholder_yield_paid": ((g("dividends_paid") or 0) + (g("buybacks") or 0)) if (g("dividends_paid") is not None or g("buybacks") is not None) else None,
            "cash": cash, "short_term_investments": g("short_term_investments"), "receivables": g("receivables"), "inventory": g("inventory"),
            "prepaids": g("prepaids"), "assets_current": g("assets_current"), "ppe_net": g("ppe_net"),
            "goodwill": g("goodwill"), "intangibles": g("intangibles"), "assets": g("assets"),
            "liab_current": g("liab_current"), "deferred_revenue": g("deferred_revenue"),
            "debt_current": d_cur, "debt_lt": d_lt, "total_debt": total_debt, "debt_basis": debt_basis, "net_debt": net_debt,
            "lease_liabilities": lease, "liabilities": g("liabilities"), "equity": eq, "retained_earnings": g("retained_earnings"),
            "oe_per_share": _ratio(oe, sh), "fcf_per_share": _ratio(fcf, sh), "ocf_per_share": _ratio(ocf, sh),
            "revenue_per_share": _ratio(rev, sh), "book_value_per_share": _ratio(eq, sh),
            "roe": _ratio(ni, eq), "roa": _ratio(ni, g("assets")),
            "roic_proxy": (_ratio(oi * (1 - tax_rate), invested) if (oi is not None and invested) else None),
            "net_debt_to_oe": _ratio(net_debt, oe) if (oe and oe > 0) else None,
            "goodwill_pct_assets": _ratio(g("goodwill"), g("assets")),
            "prepaids_pct_assets": _ratio(g("prepaids"), g("assets")),
            "current_ratio": _ratio(g("assets_current"), g("liab_current")),
        })
    # growth columns (vs prior fiscal year in the table)
    for i, r in enumerate(rows):
        prev = rows[i - 1] if i else None
        for k in ("revenue", "gross_profit", "operating_income", "net_income", "eps_diluted", "ocf", "oe_conservative", "fcf", "shares_diluted", "oe_per_share"):
            r[f"{k}_growth"] = _g(r.get(k), prev.get(k)) if prev else None
    core_tags = {k: tags[k] for k in ("revenue", "net_income", "operating_income", "ocf", "capex", "sbc", "da", "shares_diluted", "cash", "debt_lt", "debt_total", "equity", "assets")}
    tag_summary = {k: sorted({v for v in m.values()}) for k, m in core_tags.items()}
    return rows, tag_summary, sorted(currency)


def build_quarterly(facts, max_q=12, warnings=None):
    q = {k: quarterly_series(facts, DUR[k], derive=(k not in DIRECT_ONLY)) for k in QUARTERLY_FIELDS}
    # bank presentation: revenue = Revenues total, else NII + noninterest income
    q_nii, q_nonint, q_revt = (quarterly_series(facts, DUR[k]) for k in ("nii", "noninterest_income", "revenues_total"))
    for e, dn in q_nii.items():
        if e in q_nonint and isinstance(dn.get("val"), (int, float)) and dn["val"] > 0:
            if e in q_revt:
                q["revenue"][e] = dict(q_revt[e], tag="Revenues (bank total)")
            elif isinstance(q_nonint[e].get("val"), (int, float)):
                q["revenue"][e] = dict(dn, val=dn["val"] + q_nonint[e]["val"], tag="InterestIncomeExpenseNet + NoninterestIncome",
                                       derived=bool(dn.get("derived") or q_nonint[e].get("derived")))
    ends = sorted(set(q["revenue"]) | set(q["net_income"]) | set(q["ocf"]))
    # keep ends that at least two core lines agree on, last max_q
    ends = [e for e in ends if sum(1 for k in ("revenue", "net_income", "ocf") if e in q[k]) >= 2][-max_q:]
    # A derived revenue / gross profit below zero means the annual figure was
    # restated (discontinued operations) while the year-to-date legs were not —
    # a basis break, not a quarter. Null it and say so.
    for k in ("revenue", "gross_profit"):
        for e in list(q[k]):
            d = q[k][e]
            if d.get("derived") and isinstance(d.get("val"), (int, float)) and d["val"] < 0:
                if warnings is not None:
                    warnings.append(f"{k} for the quarter ending {e}: FY minus year-to-date is negative — the annual figure was restated on a different basis (discontinued operations); quarter not shown")
                del q[k][e]
    rows = []
    for e in ends:
        meta = next((q[k][e] for k in ("revenue", "net_income", "ocf") if e in q[k]), {})
        fs = meta.get("fy_start")
        fy_label = None
        if fs:
            fy_end = datetime.date.fromisoformat(fs) + datetime.timedelta(days=364)
            fy_label = str(fy_end.year)
        row = {"period_end": e, "fq": meta.get("fq"), "fy": fy_label,
               "label": (f"Q{meta['fq']} FY{fy_label}" if meta.get("fq") and fy_label else e)}
        for k in QUARTERLY_FIELDS:
            d = q[k].get(e)
            row[k] = d["val"] if d else None
            row[f"{k}_derived"] = bool(d["derived"]) if d else None
        rev, ni, oi, ocf, capex, sbc, gp = row["revenue"], row["net_income"], row["operating_income"], row["ocf"], row["capex"], row["sbc"], row["gross_profit"]
        row["gross_margin"] = _ratio(gp, rev)
        row["operating_margin"] = _ratio(oi, rev)
        row["net_margin"] = _ratio(ni, rev)
        row["fcf"] = (ocf - capex) if (ocf is not None and capex is not None) else None
        row["oe_conservative"] = (row["fcf"] - sbc) if (row["fcf"] is not None and sbc is not None) else None
        rows.append(row)
    # YoY vs the quarter ending ~one year earlier
    by_end = {r["period_end"]: r for r in rows}
    for r in rows:
        tgt = datetime.date.fromisoformat(r["period_end"]) - datetime.timedelta(days=365)
        prev = next((by_end[e] for e in by_end if abs((datetime.date.fromisoformat(e) - tgt).days) <= 10), None)
        for k in ("revenue", "net_income", "operating_income", "ocf", "oe_conservative", "eps_diluted"):
            r[f"{k}_yoy"] = _g(r.get(k), prev.get(k)) if prev else None
    return rows


def build_ttm(qrows):
    if len(qrows) < 4:
        return None
    last4 = qrows[-4:]
    # consecutive quarters: ends ~91 days apart
    for a, b in zip(last4, last4[1:]):
        if not (60 <= _days(a["period_end"], b["period_end"]) <= 130):
            return None
    out = {"period_end": last4[-1]["period_end"], "quarters": [r["period_end"] for r in last4]}
    for k in ("revenue", "gross_profit", "operating_income", "net_income", "ocf", "capex", "sbc", "da", "fcf", "oe_conservative", "eps_diluted"):
        vals = [r.get(k) for r in last4]
        out[k] = sum(vals) if all(isinstance(v, (int, float)) for v in vals) else None
    out["shares_diluted"] = last4[-1].get("shares_diluted")
    out["gross_margin"], out["operating_margin"], out["net_margin"] = _ratio(out["gross_profit"], out["revenue"]), _ratio(out["operating_income"], out["revenue"]), _ratio(out["net_income"], out["revenue"])
    out["oe_margin"] = _ratio(out["oe_conservative"], out["revenue"])
    out["oe_per_share"] = _ratio(out["oe_conservative"], out["shares_diluted"])
    out["fcf_per_share"] = _ratio(out["fcf"], out["shares_diluted"])
    # YoY of the TTM vs the TTM one year earlier (needs 8 quarters)
    if len(qrows) >= 8:
        prev4 = qrows[-8:-4]
        for k in ("revenue", "net_income", "ocf", "oe_conservative"):
            pv = [r.get(k) for r in prev4]
            if all(isinstance(v, (int, float)) for v in pv) and out.get(k) is not None:
                out[f"{k}_yoy"] = _g(out[k], sum(pv))
    return out


def build_profile(cik, facts):
    prof = {"cik": cik, "entity": facts.get("entityName")}
    try:
        sub = get_json(f"https://data.sec.gov/submissions/CIK{cik:010d}.json")
    except Exception as e:
        prof["submissions_error"] = str(e)
        return prof
    prof.update({"sic": sub.get("sic"), "sic_description": sub.get("sicDescription"),
                 "fiscal_year_end_mmdd": sub.get("fiscalYearEnd"), "state_of_incorporation": sub.get("stateOfIncorporation"),
                 "exchanges": sub.get("exchanges"), "tickers": sub.get("tickers"), "filer_category": sub.get("category"),
                 "website": sub.get("website") or None, "former_names": [f.get("name") for f in (sub.get("formerNames") or [])][:5]})
    rec = (sub.get("filings") or {}).get("recent") or {}
    forms, fds, rds, accs, docs = rec.get("form", []), rec.get("filingDate", []), rec.get("reportDate", []), rec.get("accessionNumber", []), rec.get("primaryDocument", [])
    latest = {}
    n8k = 0
    cutoff = (ET_TODAY - datetime.timedelta(days=365)).isoformat()
    for i, form in enumerate(forms):
        fd = fds[i] if i < len(fds) else ""
        if form in ("10-K", "10-K/A", "20-F", "40-F", "10-Q", "10-Q/A") and form.replace("/A", "") not in latest:
            acc = accs[i].replace("-", "") if i < len(accs) else ""
            doc = docs[i] if i < len(docs) else ""
            latest[form.replace("/A", "")] = {"filed": fd, "period": rds[i] if i < len(rds) else "",
                                              "url": f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc}/{doc}" if acc and doc else None}
        if form == "8-K" and fd >= cutoff:
            n8k += 1
    prof["latest_filings"] = latest
    prof["eight_k_count_12m"] = n8k
    prof["edgar_url"] = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik:010d}&type=10-K&dateb=&owner=include&count=40"
    return prof


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__); sys.exit(2)
    ticker = args[0].upper()
    folder = f"{BASE}/{ticker}"
    nums = {}
    try:
        nums = json.load(open(f"{folder}/dcf_numbers.json", encoding="utf-8"))
    except Exception:
        pass
    cik = resolve_cik(ticker, nums)
    if cik is None:
        print(f"fundamentals.py: NO_CIK for {ticker}", file=sys.stderr); sys.exit(2)
    facts = get_json(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json")
    warnings = []
    annual, tag_summary, currency = build_annual(facts)
    quarterly = build_quarterly(facts, warnings=warnings)
    ttm = build_ttm(quarterly)
    profile = build_profile(cik, facts)
    if currency:
        warnings.append(f"core facts filed in {', '.join(currency)} — figures are shown as filed (no FX conversion here; the engine converts for the valuation)")
    if not quarterly:
        warnings.append("no quarterly facts could be assembled (filer may report on 20-F/40-F without 10-Qs)")
    nd_src = [r for r in annual if r.get("shares_tag") and str(r["shares_tag"]).startswith("BASIC")]
    if nd_src:
        warnings.append(f"diluted share count not filed for {', '.join(r['fy'] for r in nd_src)} — basic count shown")
    out = {"ticker": ticker, "cik": cik, "entity": facts.get("entityName"), "as_of": ET_TODAY.isoformat(),
           "source": "SEC EDGAR companyfacts + submissions APIs (filing-direct)",
           "currency": currency[0] if currency else "USD",
           "profile": profile, "annual": annual, "quarterly": quarterly, "ttm": ttm,
           "tags_used": tag_summary, "warnings": warnings}
    if "--no-write" not in sys.argv:
        os.makedirs(folder, exist_ok=True)
        with open(f"{folder}/fundamentals.json", "w", encoding="utf-8") as f:
            json.dump(out, f, indent=1)
    summary = {"ticker": ticker, "cik": cik, "annual_years": len(annual), "quarters": len(quarterly),
               "ttm_period": (ttm or {}).get("period_end"), "latest_filings": profile.get("latest_filings"), "warnings": warnings}
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
