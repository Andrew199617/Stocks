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
- dividends (5.4.1, 5.4.2 review fixes): dividends per share (declared
  preferred, else paid), TTM DPS with its basis (four consecutive quarterly
  facts; else the latest FY fact rolled forward by the quarters since minus
  their prior-year comparatives; a FY fact older than ~15 months is stale and
  gives null — a suspended dividend never yields), payment frequency (the FY
  count rule when the 10-K carries a Q4 the quarters do not, else the spacing
  of the latest quarterly facts), the annual DPS series keyed by period end
  with YoY growth, 3y/5y CAGR, consecutive growth years and the last cut —
  restated for filed stock splits (StockholdersEquityNoteStockSplitConversionRatio1:
  facts last filed before a split are divided by the ratio) and guarded
  against unfiled ones (a DPS move of ~1/k against a share-count move of ~k
  truncates the comparable series instead of reporting a cut) — payout ratios
  vs diluted EPS / owner's earnings / FCF, TTM dividends paid / buybacks /
  share issuance (issuance = the sum of the distinct issuance tags filed in
  the same filing), and the yields on the last close: dividend, buyback (TTM
  buybacks ÷ market cap), net buyback and shareholder yield = dividends +
  buybacks − issuance over the market cap, where a leg that is filed for only
  some of the four quarters is summed as a lower bound and a tag the filer
  never filed in any period counts as zero — `legs`, `shareholder_yield_basis`
  and `shareholder_yield_complete` say exactly which. Market cap = price × the
  latest filed instant share count (cover-page dei count, else the balance
  sheet's), the weighted-average diluted count only as a fallback; both are
  recorded. Quarterly rows carry dividends_paid, buybacks, share_issuance (with
  the contributing tags) and DPS. DPS is a per-share rate: only direct
  quarterly facts are used, never YTD subtraction; the cash flows derive like
  the other cash-flow lines. Price = <T>/prices.json stats.last, else
  score.json price. A filing in the submissions feed that companyfacts has not
  ingested yet is named in `notes` and `warnings`. Anything not computable
  from filed values is null and `notes` says why.
Units are the filer's own (USD for almost every name; `currency` records
anything else). No FX conversion is applied here — the engine handles that
for the valuation; this file is for reading the filings as filed.
"""
import json, sys, os, csv, datetime, time, math, statistics, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
BASE = os.environ.get("STOCKS_BASE") or os.path.dirname(HERE)
SYS = f"{BASE}/_system"
UA = {"User-Agent": "Muse research andrewmauro199612@gmail.com"}
IF = "ifrs-full"
from zoneinfo import ZoneInfo
ET_TODAY = datetime.datetime.now(ZoneInfo("America/New_York")).date()  # Codex review of PR #2: the sweep VM runs UTC; the business date is New York's


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
    # Codex review of PR #2: interest-income tags are NOT revenue candidates — a
    # lender's revenue must be a coherent total on ONE basis for every period
    # (see the bank shape below); mixing contract revenue, interest income and
    # a composite across periods produced RKT's $237M → $35.7M "quarter".
    "revenue": ["RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet", "Revenues", "RevenueFromContractWithCustomerIncludingAssessedTax",
                (IF, "Revenue"), (IF, "RevenueFromContractsWithCustomers")],
    # Banks / lenders: "revenue" is net interest income + noninterest income
    # (or the filer's own Revenues total); RevenueFromContract... is fee income only.
    "nii": ["InterestIncomeExpenseNet", "InterestIncomeExpenseAfterProvisionForLoanLoss"],
    "noninterest_income": ["NoninterestIncome"],
    # A lender's / broker's own top line ("Revenues" or "Revenues, net of
    # interest expense") — used as the company-wide basis when it is filed for
    # the latest year and exceeds the contract-revenue line (Codex review of PR #2:
    # AFRM files Revenues $4.26B vs contract revenue $1.44B; RKT files only
    # RevenuesNetOfInterestExpense).
    "revenues_total": ["Revenues", "RevenuesNetOfInterestExpense"],
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
    # Dividends paid: the common-stock line first (a bank's PaymentsOfDividends
    # includes preferred), then the totals, then the IFRS parent-only / total lines.
    "dividends_paid": ["PaymentsOfDividendsCommonStock", "PaymentsOfDividends", "PaymentsOfOrdinaryDividends",
                       (IF, "DividendsPaidToEquityHoldersOfParentClassifiedAsFinancingActivities"), (IF, "DividendsPaidClassifiedAsFinancingActivities"), (IF, "DividendsPaid")],
    "buybacks": ["PaymentsForRepurchaseOfCommonStock", (IF, "PaymentsToAcquireOrRedeemEntitysShares")],
    "acquisitions": ["PaymentsToAcquireBusinessesNetOfCashAcquired", "PaymentsToAcquireBusinessesGross", (IF, "CashFlowsUsedInObtainingControlOfSubsidiariesOrOtherBusinessesClassifiedAsInvestingActivities")],
    # Dividends per share (USD/shares) and equity issuance (5.4.1).
    "dps_declared": ["CommonStockDividendsPerShareDeclared", (IF, "DividendsRecognisedAsDistributionsToOwnersPerShare")],
    "dps_paid": ["CommonStockDividendsPerShareCashPaid", (IF, "DividendsPaidOrdinarySharesPerShare")],
    # Equity issuance proceeds: filers split the line across several tags
    # (option exercises, ESPP, incentive plans, treasury reissues, offerings),
    # so the series is the SUM of the distinct tags filed in the same filing
    # for a period (combined_duration_facts), not first-tag-wins.
    "share_issuance": ["ProceedsFromIssuanceOrSaleOfEquity", "ProceedsFromIssuanceOfSharesUnderIncentiveAndShareBasedCompensationPlansIncludingStockOptions",
                       "ProceedsFromIssuanceOfCommonStock", "ProceedsFromIssuanceOfSharesUnderIncentiveAndShareBasedCompensationPlans",
                       "ProceedsFromStockOptionsExercised", "ProceedsFromStockPlans", "ProceedsFromSaleOfTreasuryStock",
                       "ProceedsFromIssuanceInitialPublicOffering", "ProceedsFromWarrantExercises",
                       (IF, "ProceedsFromIssuingShares"), (IF, "ProceedsFromExerciseOfOptions")],
    # Stock splits (instant facts, any form): ratio = new shares per old share as filed.
    "split_ratio": ["StockholdersEquityNoteStockSplitConversionRatio1"],
}
# A tag that is by definition the total of other issuance tags: when it is
# filed in the same filing as one of its components, the total alone counts.
ISSUANCE_SUPERSETS = {
    "ProceedsFromIssuanceOrSaleOfEquity": "*",
    "ProceedsFromIssuanceOfSharesUnderIncentiveAndShareBasedCompensationPlansIncludingStockOptions": {
        "ProceedsFromIssuanceOfSharesUnderIncentiveAndShareBasedCompensationPlans", "ProceedsFromStockOptionsExercised", "ProceedsFromStockPlans"},
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
    # Codex review of PR #2: aggregate tag when filed; otherwise the two component
    # groups are ADDITIVE and summed (alternatives within each group).
    "debt_current": ["DebtCurrent", (IF, "CurrentBorrowingsAndCurrentPortionOfNoncurrentBorrowings")],
    "debt_cur_ltd": ["LongTermDebtAndCapitalLeaseObligationsCurrent", "LongTermDebtCurrent", (IF, "CurrentPortionOfLongtermBorrowings")],
    "debt_cur_st": ["ShortTermBorrowings", "CommercialPaper", "NotesPayableCurrent", (IF, "ShorttermBorrowings")],
    "restricted_cash": ["RestrictedCashAndCashEquivalents", "RestrictedCash", "RestrictedCashAndCashEquivalentsAtCarryingValue", "RestrictedCashCurrent", (IF, "RestrictedCashAndCashEquivalents")],
    "debt_lt": ["LongTermDebtNoncurrent", "LongTermDebtAndCapitalLeaseObligations", "LongTermNotesPayable", (IF, "LongtermBorrowings"), (IF, "NoncurrentPortionOfNoncurrentBorrowings")],
    "debt_total": ["LongTermDebt", "DebtLongtermAndShorttermCombinedAmount", "LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities", (IF, "Borrowings")],
    "lease_liab_current": ["OperatingLeaseLiabilityCurrent", (IF, "CurrentLeaseLiabilities")],
    "lease_liab_lt": ["OperatingLeaseLiabilityNoncurrent", (IF, "NoncurrentLeaseLiabilities")],
    "liabilities": ["Liabilities", (IF, "Liabilities")],
    "equity": ["StockholdersEquity", "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest", (IF, "Equity")],
    "retained_earnings": ["RetainedEarningsAccumulatedDeficit", (IF, "RetainedEarnings")],
    "shares_outstanding": ["CommonStockSharesOutstanding", (IF, "NumberOfSharesOutstanding")],
}
# Period-end / cover-page share counts for the market cap (latest instant wins;
# the cover-page dei count first, then the balance-sheet count).
SHARE_COUNT_TAGS = [("dei", "EntityCommonStockSharesOutstanding"), ("us-gaap", "CommonStockSharesOutstanding"), (IF, "NumberOfSharesOutstanding")]
QUARTERLY_FIELDS = ["revenue", "gross_profit", "operating_income", "net_income", "ocf", "capex", "sbc", "da", "eps_diluted", "shares_diluted"]
DIRECT_ONLY = {"eps_diluted", "shares_diluted"}  # ratios / averages: never derived by subtraction
# 5.4.1 capital-return lines on the quarterly rows. The flows derive like the
# other cash-flow lines (YTD minus prior YTD, Q4 = FY minus 9M) but each
# candidate tag is derived on its own and merged per quarter afterwards, so a
# subtraction never mixes two tags (e.g. a total-dividends FY fact minus a
# common-only nine-month leg). DPS is a per-share rate: direct facts only.
QUARTERLY_FLOW_FIELDS = ["dividends_paid", "buybacks", "share_issuance"]
QUARTERLY_DPS_FIELDS = ["dps_declared", "dps_paid"]
DPS_DIRECT_WINDOW = (80, 120)  # a 16-week first quarter (KR) is still that quarter's filed DPS fact
UNIT_PREF = ("USD", "shares", "USD/shares")


def _days(a, b):
    return (datetime.date.fromisoformat(b) - datetime.date.fromisoformat(a)).days


def _pairs(tags):
    return [(t if isinstance(t, tuple) else ("us-gaap", t)) for t in tags]


def _units_pref(units):
    pref = [u for u in UNIT_PREF if u in units]
    return pref + [u for u in units if u not in pref]


def annual_series(facts, tags, duration=True, with_filed=False):
    """{period_end: val}, {period_end: tag}, {period_end: unit} — FY facts on
    annual forms, merged across candidate tags per period, latest filing wins.
    with_filed=True adds a fourth dict {period_end: filed date}."""
    merged, tag_by, unit_by, filed_by = {}, {}, {}, {}
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
                    merged[k], tag_by[k], unit_by[k], filed_by[k] = v["val"], tag, unit_key, v.get("filed")
    if with_filed:
        return merged, tag_by, unit_by, filed_by
    return merged, tag_by, unit_by


DURATION_FORMS = ("10-Q", "10-Q/A", "10-K", "10-K/A", "20-F", "40-F", "6-K")


def duration_facts(facts, tags):
    """{(start, end): (val, tag, unit, filed, accn)} across 10-Q/10-K/20-F/40-F
    forms, merged per period by tag priority (latest filing wins per tag)."""
    out = {}
    for taxonomy, tag in _pairs(tags):
        tf = facts.get("facts", {}).get(taxonomy, {})
        if tag not in tf:
            continue
        units = tf[tag].get("units", {})
        for unit_key in _units_pref(units):
            best = {}
            for e in units[unit_key]:
                if e.get("form", "") not in DURATION_FORMS:
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
                    out[k] = (v["val"], tag, unit_key, v.get("filed"), v.get("accn"))
    return out


def combined_duration_facts(facts, tags, supersets=None):
    """{(start, end): (sum, "tagA+tagB", unit, filed, accn)}: for each period,
    the DISTINCT candidate tags filed in the same filing are summed (a filer
    that books option exercises and ESPP proceeds on two lines). The filing is
    the latest one that reports the period, so a renamed tag in a later 10-K
    never double-counts an older one; a tag that is by definition the total of
    other tags present in the filing (`supersets`) counts alone."""
    supersets = supersets or {}
    per_period = {}
    for taxonomy, tag in _pairs(tags):
        tf = facts.get("facts", {}).get(taxonomy, {})
        if tag not in tf:
            continue
        units = tf[tag].get("units", {})
        for unit_key in _units_pref(units):
            for e in units[unit_key]:
                if e.get("form", "") not in DURATION_FORMS or not e.get("start") or not e.get("end"):
                    continue
                accn = e.get("accn") or e.get("filed")
                slot = per_period.setdefault((e["start"], e["end"]), {}).setdefault(accn, {})
                if tag not in slot:
                    slot[tag] = (e["val"], unit_key, e.get("filed", ""))
    out = {}
    for key, by_accn in per_period.items():
        accn, tagvals = max(by_accn.items(), key=lambda kv: max(v[2] for v in kv[1].values()))
        present = set(tagvals)
        for total, parts in supersets.items():
            if total in present and (present - {total}) and (parts == "*" or (present & set(parts))):
                present = {total} if parts == "*" else present - set(parts)
        unit = next(iter(tagvals.values()))[1]
        keep = sorted(t for t in present if tagvals[t][1] == unit and _num(tagvals[t][0]))
        if not keep:
            continue
        out[key] = (sum(tagvals[t][0] for t in keep), "+".join(keep), unit, max(tagvals[t][2] for t in keep), accn)
    return out


def combined_annual(facts, tags, supersets=None):
    """{period_end: val}, {period_end: tags} for FY-length periods of combined_duration_facts (annual forms only)."""
    vals, tag_by = {}, {}
    for (s, e), (v, tag, unit, filed, accn) in combined_duration_facts(facts, tags, supersets).items():
        if 330 <= _days(s, e) <= 380:
            vals[e], tag_by[e] = v, tag
    return vals, tag_by


def quarterly_series(facts, tags, derive=True, direct_window=(80, 120), fy_starts=None, prebuilt=None):
    """{quarter_end: {val, fq, fy_start, derived, tag}} for the fiscal quarters
    the filer's facts support. Direct 3-month facts win; otherwise (cash-flow
    lines are filed YTD only) quarter = YTD - prior YTD within the same
    fiscal year, Q4 = FY - nine-month YTD.
    `direct_window` (days) says what counts as a direct quarterly fact (80-120: a 16-week first quarter, e.g. KR, is still a filed quarter — Codex review of PR #2);
    `fy_starts` adds known fiscal-year starts (from the core statements) so a
    tag filed year-to-date without its own annual fact can still be derived.
    `prebuilt` is a ready {(start, end): (val, tag, unit, filed, accn)} map
    (combined_duration_facts) used instead of reading `tags`."""
    f = prebuilt if prebuilt is not None else duration_facts(facts, tags)
    if not f:
        return {}
    annual_keys = [(s, e) for (s, e) in f if 330 <= _days(s, e) <= 380]
    fy_starts = set(fy_starts or ()) | {s for s, _ in annual_keys}
    for _, e in annual_keys:  # the fiscal year that follows each filed annual period
        fy_starts.add((datetime.date.fromisoformat(e) + datetime.timedelta(days=1)).isoformat())
    direct = {(s, e): v for (s, e), v in f.items() if direct_window[0] <= _days(s, e) <= direct_window[1]}
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
                out[e] = {"val": dq[0][1][0], "fq": rank, "fy_start": s, "derived": False, "tag": dq[0][1][1], "ytd": v, "filed": dq[0][1][3]}
            elif derive and last_rank == rank - 1:
                out[e] = {"val": v - prev_val, "fq": rank, "fy_start": s, "derived": rank > 1, "tag": f[(s, e)][1], "ytd": v, "filed": f[(s, e)][3]}
            prev_val, last_rank = v, rank
    # direct quarters not attached to a known FY start (fiscal-year start unknown)
    for (s, e), (v, tag, unit, filed, accn) in direct.items():
        if e not in out:
            fs = max((x for x in fy_starts if x <= s and _days(x, s) <= 300), default=None)
            fq = (round(_days(fs, e) / 91.25) if fs else None)
            out[e] = {"val": v, "fq": fq if fq and 1 <= fq <= 4 else None, "fy_start": fs, "derived": False, "tag": tag, "ytd": None, "filed": filed}
    return out


def core_fy_starts(facts):
    """Fiscal-year start dates the core statements establish (annual revenue /
    net income / OCF periods and the year that follows each)."""
    starts = set()
    for k in ("revenue", "net_income", "ocf"):
        for (s, e) in duration_facts(facts, DUR[k]):
            if 330 <= _days(s, e) <= 380:
                starts.add(s)
                starts.add((datetime.date.fromisoformat(e) + datetime.timedelta(days=1)).isoformat())
    return starts


def quarterly_by_tag(facts, tags, derive=True, direct_window=(80, 120), fy_starts=None):
    """quarterly_series run per candidate tag and merged per quarter end in
    tag-priority order — a derived quarter never subtracts one tag's leg from
    another's."""
    out = {}
    for pair in _pairs(tags):
        for e, d in quarterly_series(facts, [pair], derive=derive, direct_window=direct_window, fy_starts=fy_starts).items():
            out.setdefault(e, d)
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
    series["share_issuance"], tags["share_issuance"] = combined_annual(facts, DUR["share_issuance"], ISSUANCE_SUPERSETS)
    periods = sorted(set(series["revenue"]) | set(series["net_income"]) | set(series["ocf"]) | set(series["nii"]))[-10:]
    # Bank shape (NoninterestIncome is a bank-only tag): pick ONE revenue basis
    # for the company — Codex review of PR #2.
    nii_periods = [p for p in periods if series["nii"].get(p) is not None and series["noninterest_income"].get(p) is not None]
    bank_shape = bool(nii_periods)
    bank_basis = None
    if bank_shape:
        bank_basis = ("Revenues (bank total)" if all(series["revenues_total"].get(p) is not None for p in nii_periods)
                      else "InterestIncomeExpenseNet + NoninterestIncome")
    # Lender / broker shape: the filer's own total is filed for the latest
    # fiscal year and exceeds the contract-revenue line by >5% (or there is no
    # contract line at all) — the total is the basis for EVERY period.
    revenue_mode = "bank" if bank_shape else "standard"
    if not bank_shape and periods:
        _lp = periods[-1]
        _tot, _std = series["revenues_total"].get(_lp), series["revenue"].get(_lp)
        if _tot is not None and (_std is None or (_std > 0 and _tot > 1.05 * _std)):
            revenue_mode = "total"
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
        if bank_shape:
            # Codex review of PR #2: one basis for the whole series. Either the
            # filer's own Revenues total (only when it exists for every bank
            # period) or NII + noninterest income (both filed) — a period with
            # neither is null, never contract revenue or interest income alone.
            if bank_basis == "Revenues (bank total)":
                rev = g("revenues_total")
            else:
                rev = (g("nii") + g("noninterest_income")) if (g("nii") is not None and g("noninterest_income") is not None) else None
            rev_basis = bank_basis
        elif revenue_mode == "total":
            rev, rev_basis = g("revenues_total"), (tags["revenues_total"].get(p) or "Revenues (total)") + " (filer total)"
        cogs, gp = g("cogs"), g("gross_profit")
        if gp is None and rev is not None and cogs is not None:
            gp = rev - cogs
        if cogs is None and rev is not None and gp is not None:
            cogs = rev - gp
        sga = g("sga")
        if sga is None and (g("sm") is not None or g("ga") is not None):
            sga = (g("sm") or 0) + (g("ga") or 0)
        if g("debt_current") is not None:
            d_cur = g("debt_current")
        else:
            _parts = [g(k) for k in ("debt_cur_ltd", "debt_cur_st") if g(k) is not None]
            d_cur = sum(_parts) if _parts else None
        d_lt, d_tot = g("debt_lt"), g("debt_total")
        if d_lt is not None:
            total_debt, debt_basis = d_lt + (d_cur or 0), "noncurrent+current"
        elif d_tot is not None:
            total_debt, debt_basis = d_tot, "total tag"
        elif d_cur is not None:
            total_debt, debt_basis = d_cur, "current only"
        else:
            total_debt, debt_basis = None, None
        cash, cash_basis = g("cash"), tags["cash"].get(p)
        if cash is not None and cash_basis == "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents":
            # Codex review of PR #2: never net restricted cash against debt silently
            if g("restricted_cash") is not None:
                cash = cash - g("restricted_cash"); cash_basis = f"{cash_basis} minus restricted cash"
            else:
                cash_basis = f"{cash_basis} (includes restricted cash — no separate tag; net debt understated)"
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
            "cash": cash, "cash_basis": cash_basis, "restricted_cash": g("restricted_cash"),
            "short_term_investments": g("short_term_investments"), "receivables": g("receivables"), "inventory": g("inventory"),
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
            # 5.4.1 capital-return lines (appended so the earlier keys keep their order)
            "dps_declared": g("dps_declared"), "dps_paid": g("dps_paid"), "share_issuance": g("share_issuance"),
            "share_issuance_tags": tags["share_issuance"].get(p),
        })
    # growth columns (vs prior fiscal year in the table)
    for i, r in enumerate(rows):
        prev = rows[i - 1] if i else None
        for k in ("revenue", "gross_profit", "operating_income", "net_income", "eps_diluted", "ocf", "oe_conservative", "fcf", "shares_diluted", "oe_per_share"):
            r[f"{k}_growth"] = _g(r.get(k), prev.get(k)) if prev else None
    core_tags = {k: tags[k] for k in ("revenue", "net_income", "operating_income", "ocf", "capex", "sbc", "da", "shares_diluted", "cash", "debt_lt", "debt_total", "equity", "assets")}
    tag_summary = {k: sorted({v for v in m.values()}) for k, m in core_tags.items()}
    tag_summary["revenue_mode"] = [revenue_mode]
    return rows, tag_summary, sorted(currency)


def build_quarterly(facts, max_q=12, warnings=None, revenue_mode=None, annual=None):
    q = {k: quarterly_series(facts, DUR[k], derive=(k not in DIRECT_ONLY)) for k in QUARTERLY_FIELDS}
    # bank presentation: revenue = Revenues total, else NII + noninterest income —
    # on ONE basis for every quarter (Codex review of PR #2); quarters with
    # neither are dropped from the revenue series rather than falling back to
    # contract revenue or interest income alone.
    q_nii, q_nonint, q_revt = (quarterly_series(facts, DUR[k]) for k in ("nii", "noninterest_income", "revenues_total"))
    bank_q = [e for e in q_nii if e in q_nonint and isinstance(q_nii[e].get("val"), (int, float)) and isinstance(q_nonint[e].get("val"), (int, float))]
    if bank_q:
        use_total = all(e in q_revt and isinstance(q_revt[e].get("val"), (int, float)) for e in bank_q)
        rebuilt = {}
        for e in bank_q:
            if use_total:
                rebuilt[e] = dict(q_revt[e], tag="Revenues (bank total)")
            else:
                dn = q_nii[e]
                rebuilt[e] = dict(dn, val=dn["val"] + q_nonint[e]["val"], tag="InterestIncomeExpenseNet + NoninterestIncome",
                                  derived=bool(dn.get("derived") or q_nonint[e].get("derived")))
        q["revenue"] = rebuilt
        if warnings is not None:
            warnings.append(f"bank presentation: quarterly revenue is {'the filed Revenues total' if use_total else 'net interest income + noninterest income'} for every quarter; quarters lacking it are blank")
    elif revenue_mode == "total":
        # lender / broker: the filer's own total on every quarter, same rule as the annual series
        q["revenue"] = {e: dict(d, tag=f"{d.get('tag')} (filer total)") for e, d in quarterly_series(facts, DUR["revenues_total"]).items()}
        if warnings is not None:
            warnings.append("revenue basis: the filer's own total (Revenues / RevenuesNetOfInterestExpense) for every period — it exceeds the contract-revenue line, which is a component for this filer")
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
            fy_label = _fy_label(fs)
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
    # 5.4.1 capital-return lines, appended after the pre-5.4.1 keys
    fy_starts = core_fy_starts(facts)
    extra = {k: quarterly_by_tag(facts, DUR[k], derive=True, fy_starts=fy_starts) for k in QUARTERLY_FLOW_FIELDS if k != "share_issuance"}
    extra["share_issuance"] = quarterly_series(None, None, derive=True, fy_starts=fy_starts,
                                               prebuilt=combined_duration_facts(facts, DUR["share_issuance"], ISSUANCE_SUPERSETS))
    extra.update({k: quarterly_by_tag(facts, DUR[k], derive=False, direct_window=DPS_DIRECT_WINDOW, fy_starts=fy_starts) for k in QUARTERLY_DPS_FIELDS})
    for r in rows:
        for k in QUARTERLY_FLOW_FIELDS + QUARTERLY_DPS_FIELDS:
            d = extra[k].get(r["period_end"])
            r[k] = d["val"] if d else None
            r[f"{k}_derived"] = bool(d["derived"]) if d else None
        d = extra["share_issuance"].get(r["period_end"])
        r["share_issuance_tags"] = d["tag"] if d else None
    # Codex review of PR #2 (TTM share denominator): 10-Ks never file a Q4
    # weighted-average share count on its own, so one quarter per fiscal year
    # is missing. When the other three quarters and the fiscal year's own
    # weighted average are filed, Q4 = 4 × FY − the three quarters — plain
    # arithmetic on filed values, marked derived.
    if annual:
        fy_shares = {a.get("fy"): a.get("shares_diluted") for a in annual if isinstance(a.get("shares_diluted"), (int, float)) and a.get("shares_diluted") > 0}
        by_fy = {}
        for r in rows:
            if r.get("fy"):
                by_fy.setdefault(r["fy"], []).append(r)
        for fy, rs in by_fy.items():
            missing = [r for r in rs if not isinstance(r.get("shares_diluted"), (int, float))]
            present = [r for r in rs if isinstance(r.get("shares_diluted"), (int, float))]
            if len(rs) == 4 and len(missing) == 1 and len(present) == 3 and fy in fy_shares:
                counts = sorted(r["shares_diluted"] for r in present)
                derived = 4 * fy_shares[fy] - sum(counts)
                # Only when the filed quarters are mutually consistent (within
                # 25%) and the result sits near them: a mid-year capital
                # restructuring (RKT's Up-C collapse took the count from ~170M
                # to ~2.8B) makes the FY average irreconcilable with the quarters.
                if derived > 0 and counts[-1] <= 1.25 * counts[0] and 0.75 * counts[1] <= derived <= 1.25 * counts[1]:
                    missing[0]["shares_diluted"] = derived
                    missing[0]["shares_diluted_derived"] = True
    return rows


# ---------------------------------------------------------------------------
# Dividends block (5.4.1; 5.4.2 review fixes). Pure functions first — tested
# in tests/test_fundamentals_dividends.py against inline fixtures — then the
# assembly that reads the filed series and the price files.
# ---------------------------------------------------------------------------
STALE_DAYS = 456          # ~15 months: a DPS fact older than this vs the newest filed period is not "trailing"
FY_SPACING = (300, 400)   # consecutive fiscal years (52/53-week years, a fiscal-year-end change)
FLOW_KEYS = ("dividends_paid", "buybacks", "share_issuance")


def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _add_days(d, n):
    return (datetime.date.fromisoformat(d) + datetime.timedelta(days=n)).isoformat()


def ttm_sum(vals):
    """Sum of exactly four quarterly values; None unless all four are numbers."""
    vals = list(vals)
    if len(vals) != 4 or not all(_num(v) for v in vals):
        return None
    return sum(vals)


def consecutive_quarters(ends):
    """True when the period ends are ascending and ~one quarter apart (60–130 days, as build_ttm)."""
    ends = list(ends)
    if len(ends) < 2:
        return len(ends) == 1
    return all(60 <= _days(a, b) <= 130 for a, b in zip(ends, ends[1:]))


def fy_consecutive(prev_end, cur_end):
    """True when two fiscal-year period ends are one fiscal year apart (300–400 days)."""
    return FY_SPACING[0] <= _days(prev_end, cur_end) <= FY_SPACING[1]


def dps_ttm_from_quarters(qfacts):
    """(dps_ttm, ok). qfacts: [(period_end, dps)] in any order. ok is False
    when fewer than four facts exist or the latest four are not consecutive
    quarters (a Q4 DPS that was only filed inside the FY total, or a gap in
    the payments) — the caller then rolls the FY fact forward or reports null."""
    facts = sorted((e, v) for e, v in qfacts if _num(v))
    if len(facts) < 4:
        return None, False
    last4 = facts[-4:]
    if not consecutive_quarters([e for e, _ in last4]):
        return None, False
    return sum(v for _, v in last4), True


def _gap_text(qfacts):
    """Names the first non-quarterly gap in a run of DPS fact period ends."""
    ends = [e for e, _ in sorted(qfacts)]
    for a, b in zip(ends, ends[1:]):
        if not 60 <= _days(a, b) <= 130:
            return f"{_days(a, b)} days between {a} and {b}"
    return "not consecutive"


def frequency_from_spacing(ends):
    """Payment frequency from the spacing of the latest (up to four) DPS
    facts: median gap ≤130 days quarterly, ≤240 semiannual, ≤400 annual,
    else irregular; None with fewer than two facts."""
    ends = sorted(ends)[-4:]
    if len(ends) < 2:
        return None
    g = statistics.median(_days(a, b) for a, b in zip(ends, ends[1:]))
    if g <= 130:
        return "quarterly"
    if g <= 240:
        return "semiannual"
    if g <= 400:
        return "annual"
    return "irregular"


def infer_frequency(n_quarterly_in_fy, fy_dps, sum_quarterly_in_fy, any_quarterly_facts, any_facts, dividends_paid=False):
    """Payment frequency from how many DPS facts fall inside the latest
    fiscal year (the fallback when the FY total carries a payment the
    quarterly facts do not — the 10-K files the year, not the Q4). None (not
    inferable) when the filer files only full-year DPS facts (20-F). A filer
    with no per-share facts at all is "none" only when it also pays no cash
    dividends; with `dividends_paid` the rate is simply not tagged → None."""
    if not any_facts:
        return None if dividends_paid else "none"
    if not any_quarterly_facts:
        return None
    n = n_quarterly_in_fy
    if _num(fy_dps) and _num(sum_quarterly_in_fy) and fy_dps > sum_quarterly_in_fy + 1e-9:
        n += 1
    return {4: "quarterly", 2: "semiannual", 1: "annual"}.get(n, "irregular")


def _dps_rows(annual):
    return [r for r in annual if _num(r.get("dps")) and r.get("period_end")]


def growth_years(annual):
    """Consecutive fiscal years of strictly increasing annual DPS ending at the
    latest row. annual: [{fy, period_end, dps}] ascending; rows are compared
    by period-end spacing (one fiscal year apart), so a missing year or a
    missing dps ends the streak."""
    rows = _dps_rows(annual)
    n = 0
    for cur, prev in zip(reversed(rows), reversed(rows[:-1])):
        if not fy_consecutive(prev["period_end"], cur["period_end"]) or not cur["dps"] > prev["dps"]:
            break
        n += 1
    return n


def last_cut_fy(annual):
    """Label of the most recent fiscal year whose annual DPS fell below the prior (consecutive) fiscal year, else None."""
    rows = _dps_rows(annual)
    for cur, prev in zip(reversed(rows), reversed(rows[:-1])):
        if fy_consecutive(prev["period_end"], cur["period_end"]) and cur["dps"] < prev["dps"]:
            return cur["fy"]
    return None


def dps_cagr(annual, years):
    """CAGR of annual DPS between the latest row and the row whose period end
    is `years` years earlier (±45 days, so 52/53-week drift is fine; a
    missing endpoint is None, a missing year in between does not matter)."""
    rows = _dps_rows(annual)
    if len(rows) < 2:
        return None
    last = rows[-1]
    target = datetime.date.fromisoformat(last["period_end"]) - datetime.timedelta(days=round(years * 365.25))
    base = min(rows[:-1], key=lambda r: abs((datetime.date.fromisoformat(r["period_end"]) - target).days))
    if abs((datetime.date.fromisoformat(base["period_end"]) - target).days) > 45:
        return None
    a, b = base["dps"], last["dps"]
    if a <= 0 or b <= 0:
        return None
    return (b / a) ** (1.0 / years) - 1


def dps_outliers(annual):
    """Labels of rows whose annual DPS is more than 10x both neighbours (a unit
    slip in the filed XBRL, e.g. cents tagged as dollars). Reported, never altered."""
    rows = [r for r in annual if _num(r.get("dps")) and r["dps"] > 0]
    out = []
    for i in range(1, len(rows) - 1):
        a, b, c = rows[i - 1]["dps"], rows[i]["dps"], rows[i + 1]["dps"]
        if b > 10 * a and b > 10 * c:
            out.append(rows[i]["fy"])
    return out


def basis_breaks(annual, shares_by_end):
    """Fiscal years where annual DPS moved ~1/k while the diluted share count
    moved ~k (k ≥ 1.4): a share-basis change (an unfiled split) — never a
    cut. Returns [(period_end, dps_ratio, share_ratio)] ascending."""
    rows = _dps_rows(annual)
    out = []
    for prev, cur in zip(rows, rows[1:]):
        if not fy_consecutive(prev["period_end"], cur["period_end"]):
            continue
        s0, s1 = shares_by_end.get(prev["period_end"]), shares_by_end.get(cur["period_end"])
        if not (_num(s0) and _num(s1) and s0 > 0 and s1 > 0 and prev["dps"] > 0 and cur["dps"] > 0):
            continue
        rs, rd = s1 / s0, cur["dps"] / prev["dps"]
        if (rs >= 1.4 or rs <= 1 / 1.4) and 0.8 <= rs * rd <= 1.25:
            out.append((cur["period_end"], rd, rs))
    return out


def payout_ratio(numerator, denominator):
    """numerator / denominator, None unless both are numbers and the denominator is > 0."""
    if not _num(numerator) or not _num(denominator) or denominator <= 0:
        return None
    return numerator / denominator


def fy_labels(period_ends):
    """Display labels for fiscal-year period ends: the calendar year of the
    period end (the Financials tab's convention) unless two collide (a fiscal
    year ending in early January followed by one ending that December — a
    fiscal-year-end change), then the year most of each fiscal year falls in
    (period end − 182 days), then the period end itself."""
    ends = list(period_ends)
    for fn in (lambda e: e[:4], lambda e: _add_days(e, -182)[:4], lambda e: e):
        labels = [fn(e) for e in ends]
        if len(set(labels)) == len(labels):
            return labels
    return ends


def annual_dps_rows(fy_facts, quarters_by_fy):
    """[{fy, period_end, dps, basis}] ascending, keyed by period end.
    fy_facts: {period_end: dps} from FY-duration facts; quarters_by_fy:
    {fy_start: {fq: (period_end, dps)}} fallback — a fiscal year with all four
    quarterly facts and no FY fact gets their sum. Labels come from fy_labels
    (unique even when two fiscal years end in the same calendar year)."""
    rows = {}
    for p, v in fy_facts.items():
        if _num(v):
            rows[p] = {"period_end": p, "dps": v, "basis": "fy_fact"}
    for fs, qs in (quarters_by_fy or {}).items():
        if not qs or not all(fq in qs and _num(qs[fq][1]) for fq in (1, 2, 3, 4)):
            continue
        end = max(qs[fq][0] for fq in (1, 2, 3, 4))
        if any(abs(_days(end, p)) <= 7 for p in rows):
            continue  # the FY fact covers this fiscal year
        rows[end] = {"period_end": end, "dps": sum(qs[fq][1] for fq in (1, 2, 3, 4)), "basis": "sum_of_quarters"}
    out = [rows[k] for k in sorted(rows)]
    for r, label in zip(out, fy_labels([r["period_end"] for r in out])):
        r["fy"] = label
    return out


def _fy_label(fy_start):
    """Calendar year of the fiscal year's end for a fiscal year starting
    `fy_start` (start + 363 days: a 52-week year ending 2023-12-31 starts
    2023-01-02; 364 put it in the next year)."""
    if not fy_start:
        return None
    return str((datetime.date.fromisoformat(fy_start) + datetime.timedelta(days=363)).year)


# ---- stock splits (filed ratios) ------------------------------------------
def split_events(facts):
    """[(effective_date, ratio)] from StockholdersEquityNoteStockSplitConversionRatio1
    facts on any form, one entry per date; ratio = new shares per old share
    as filed (2 for a 2-for-1 split, 0.6667 for a 2-for-3 reverse split)."""
    out = {}
    for taxonomy, tag in _pairs(DUR["split_ratio"]):
        tf = facts.get("facts", {}).get(taxonomy, {}).get(tag)
        if not tf:
            continue
        for unit_key, es in tf.get("units", {}).items():
            for e in es:
                d, v = e.get("end"), e.get("val")
                if d and _num(v) and v > 0 and v != 1 and d not in out:
                    out[d] = v
    return sorted(out.items())


def split_direction(splits, shares_with_filed):
    """Check each filed ratio against the filed diluted share counts: the
    last fiscal year filed BEFORE the split vs the first filed AFTER it. The
    us-gaap element does not fix which way the ratio reads, so when the counts
    move by ~1/ratio instead of ~ratio (a 1-for-10 reverse split filed as 10)
    the inverse is used. Returns [(date, ratio_filed, ratio_used, evidence)]."""
    out = []
    for d, r in splits:
        pre = [(e, v) for e, (v, f) in shares_with_filed.items() if f and f < d and _num(v) and v > 0]
        post = [(e, v) for e, (v, f) in shares_with_filed.items() if f and f >= d and _num(v) and v > 0]
        used, ev = r, None
        if pre:
            post = [(e, v) for e, v in post if e > max(pre)[0]]
        if pre and post:
            e0, s0 = max(pre)
            e1, s1 = min(post)
            obs = s1 / s0
            ev = f"diluted shares {s0:,.0f} (FY ending {e0}) → {s1:,.0f} (FY ending {e1}), ×{obs:.2f}"
            if abs(math.log(obs)) > math.log(1.25) and abs(math.log(obs) - math.log(1 / r)) < abs(math.log(obs) - math.log(r)):
                used = 1 / r
        out.append((d, r, used, ev))
    return out


def split_factor(filed, splits):
    """Product of the ratios of every split effected after `filed` (the date
    the fact was last filed). A fact filed before a split is on the pre-split
    share basis; dividing its per-share value by this factor restates it to
    today's basis — plain arithmetic on two filed values."""
    f = 1.0
    for d, r in splits:
        if filed and filed < d:
            f *= r
    return f


def apply_splits(dps_q, dps_fy, fy_filed, splits):
    """Restate every DPS fact whose latest filing precedes a split. dps_q:
    {basis: {end: {val, filed, ...}}} (quarterly dicts get 'split_factor');
    dps_fy: {basis: {end: dps}}; fy_filed: {basis: {end: filed}}; splits:
    [(date, ratio)]. Returns (dps_q, dps_fy, notes)."""
    notes = []
    splits = [(d, r) for d, r in (splits or []) if _num(r) and r > 0 and r != 1]
    if not splits:
        return dps_q, dps_fy, notes
    touched = {}
    for basis in ("declared", "paid"):
        for e, d in (dps_q.get(basis) or {}).items():
            f = split_factor(d.get("filed"), splits)
            if f != 1 and _num(d.get("val")):
                d["val"] = d["val"] / f
                d["split_factor"] = f
                touched.setdefault(basis, []).append(e)
        for e, v in list((dps_fy.get(basis) or {}).items()):
            f = split_factor((fy_filed.get(basis) or {}).get(e), splits)
            if f != 1 and _num(v):
                dps_fy[basis][e] = v / f
                touched.setdefault(basis, []).append(e)
    desc = "; ".join(f"{r:g}-for-1 split effective {d}" if r >= 1 else f"1-for-{1 / r:g} reverse split effective {d}" for d, r in splits)
    for basis, ends in touched.items():
        ends = sorted(set(ends))
        notes.append(f"split adjustment ({basis} DPS): {len(ends)} facts for periods ending {ends[0]}..{ends[-1]} were last filed before the {desc} and are divided by the filed ratio (StockholdersEquityNoteStockSplitConversionRatio1) to today's share basis")
    return dps_q, dps_fy, notes


def latest_share_count(facts):
    """(count, as_of, source) — the latest filed instant share count: the
    cover-page dei:EntityCommonStockSharesOutstanding, else the balance
    sheet's CommonStockSharesOutstanding / IFRS NumberOfSharesOutstanding.
    The latest date wins; on the same date the dei count, then the latest filing."""
    best = None
    for prio, (taxonomy, tag) in enumerate(SHARE_COUNT_TAGS):
        tf = facts.get("facts", {}).get(taxonomy, {}).get(tag)
        if not tf:
            continue
        for unit_key, es in tf.get("units", {}).items():
            if unit_key != "shares":
                continue
            for e in es:
                if (e.get("start") and e["start"] != e.get("end")) or not e.get("end"):
                    continue
                if not _num(e.get("val")) or e["val"] <= 0:
                    continue
                key = (e["end"], -prio, e.get("filed", ""))
                if best is None or key > best[0]:
                    best = (key, e, f"{taxonomy}:{tag}")
    if best is None:
        return None
    _, e, src = best
    return e["val"], e["end"], f"{src} ({e.get('form')} filed {e.get('filed')})"


def _read_price(folder):
    """(price, date, source) from prices.json stats.last, else score.json price."""
    try:
        p = json.load(open(f"{folder}/prices.json", encoding="utf-8"))
        st = p.get("stats") or {}
        if _num(st.get("last")):
            return st["last"], st.get("last_date"), "prices.json stats.last"
    except Exception:
        pass
    try:
        s = json.load(open(f"{folder}/score.json", encoding="utf-8"))
        if _num(s.get("price")):
            return s["price"], s.get("analysis_date"), "score.json price"
    except Exception:
        pass
    return None, None, None


def _fmt_big(v):
    if not _num(v):
        return "—"
    a = abs(v)
    if a >= 1e9:
        return f"{v / 1e9:.2f}B"
    if a >= 1e6:
        return f"{v / 1e6:.1f}M"
    return f"{v:,.0f}"


def build_dividends(annual, qrows, dps_q, dps_fy, price, price_date, price_source, ctx=None):
    """The `dividends` block. annual / qrows: build_annual / build_quarterly
    output; dps_q: {"declared": {end: {val, fq, fy_start, filed, ...}}, "paid":
    {...}} quarterly DPS facts (split-adjusted by dividends_inputs); dps_fy:
    {"declared": {period_end: dps}, "paid": {...}} FY-duration DPS facts.
    ctx (optional): filed_any {flow: bool — any fact in any period},
    shares_instant (count, as_of, source), latest_filed_period {form: period}
    from the submissions feed, split_notes, splits, warnings (list to append
    to). Every figure is a filed value or arithmetic on filed values; anything
    else is None and `notes` says why."""
    ctx = ctx or {}
    notes = list(ctx.get("split_notes") or [])
    filed_any = ctx.get("filed_any") or {}
    has = {b: bool(dps_q.get(b)) or bool(dps_fy.get(b)) for b in ("declared", "paid")}
    basis = "declared" if has["declared"] else ("paid" if has["paid"] else None)
    q = {e: d for e, d in (dps_q.get(basis) or {}).items() if _num(d.get("val"))} if basis else {}
    fy_facts = {p: v for p, v in (dps_fy.get(basis) or {}).items() if _num(v)} if basis else {}
    any_facts = bool(q or fy_facts)
    latest_fy_row = annual[-1] if annual else None
    latest_end = latest_fy_row["period_end"] if latest_fy_row else None
    payout_fy = latest_fy_row["fy"] if latest_fy_row else None
    last_q_end = qrows[-1]["period_end"] if qrows else None
    reference = max(x for x in (latest_end, last_q_end) if x) if (latest_end or last_q_end) else None

    def stale(e):
        return reference is not None and _days(e, reference) > STALE_DAYS

    paid_rows = [r for r in list(annual) + list(qrows) if _num(r.get("dividends_paid")) and r["dividends_paid"] > 0]
    paid_any = bool(paid_rows)

    # annual series (FY facts, else the sum of a fiscal year's four quarterly facts)
    quarters_by_fy = {}
    for e, d in q.items():
        if d.get("fy_start") and d.get("fq"):
            quarters_by_fy.setdefault(d["fy_start"], {})[d["fq"]] = (e, d["val"])
    annual_dps = annual_dps_rows(fy_facts, quarters_by_fy)
    if any(r["basis"] == "sum_of_quarters" for r in annual_dps):
        notes.append("annual_dps: " + ", ".join(f"FY{r['fy']}" for r in annual_dps if r["basis"] == "sum_of_quarters") + " = sum of the four filed quarterly DPS facts (no FY fact)")
    annual_out = [{"fy": r["fy"], "period_end": r["period_end"], "dps": r["dps"]} for r in annual_dps]
    by_end = {r["period_end"]: r["dps"] for r in annual_dps}
    by_label = {r["fy"]: r["dps"] for r in annual_dps}
    for fy in dps_outliers(annual_dps):
        notes.append(f"annual_dps: FY{fy} DPS {by_label[fy]} is more than 10x both neighbouring years — shown as filed; check the filing's XBRL unit before relying on it")
    latest_dps_row = annual_dps[-1] if annual_dps else None
    dps_stale = bool(latest_dps_row and stale(latest_dps_row["period_end"]))

    # share-basis breaks the filed split ratios did not cover (unfiled split):
    # growth statistics only over the consistently-based years after the break
    shares_by_end = ctx.get("shares_by_end") or {r["period_end"]: r.get("shares_diluted") for r in annual}
    breaks = basis_breaks(annual_dps, shares_by_end)
    comparable = annual_dps
    if breaks:
        cut_end, rd, rs = breaks[-1]
        cut_label = next(r["fy"] for r in annual_dps if r["period_end"] == cut_end)
        comparable = [r for r in annual_dps if r["period_end"] >= cut_end]
        notes.append(f"annual_dps: FY{cut_label} DPS moved ×{rd:.2f} while diluted shares moved ×{rs:.2f} — a share-basis change (split) with no StockholdersEquityNoteStockSplitConversionRatio1 fact filed, not a cut; growth years, last cut, YoY and CAGR are computed from FY{cut_label} on")

    # TTM DPS
    qf = sorted((e, d["val"]) for e, d in q.items())
    dps_ttm, ok = dps_ttm_from_quarters(qf)
    dps_ttm_basis = None
    if ok:
        last4 = qf[-4:]
        if stale(last4[-1][0]):
            dps_ttm = None
            notes.append(f"dps_ttm: the latest quarterly DPS fact ({last4[-1][0]}) is more than 15 months older than the newest filed period ({reference}) — dividend suspended or no longer tagged; dps_ttm and dividend_yield null")
        else:
            dps_ttm_basis = f"sum of the four quarterly DPS facts {last4[0][0]}..{last4[-1][0]}"
    elif any_facts:
        why = "fewer than four quarterly DPS facts" if len(qf) < 4 else f"the latest four quarterly DPS facts are not consecutive quarters ({_gap_text(qf[-4:])})"
        if latest_dps_row and not dps_stale:
            fy_end, fy_lab = latest_dps_row["period_end"], latest_dps_row["fy"]
            after = [(e, v) for e, v in qf if e > fy_end]
            if not after:
                dps_ttm = latest_dps_row["dps"]
                dps_ttm_basis = f"FY{fy_lab} DPS ({latest_dps_row['basis']}, period ended {fy_end}) — no quarterly DPS fact since"
            else:
                matched = []
                for e, v in after:
                    tgt = _add_days(e, -364)
                    matched.append(next(((e2, v2) for e2, v2 in qf if abs(_days(tgt, e2)) <= 14), None))
                if all(m is not None for m in matched):
                    dps_ttm = latest_dps_row["dps"] + sum(v for _, v in after) - sum(v for _, v in matched)
                    dps_ttm_basis = (f"FY{fy_lab} DPS {latest_dps_row['dps']:g} + the quarters since ({', '.join(f'{e}: {v:g}' for e, v in after)})"
                                     f" − the same quarters a year earlier ({', '.join(f'{e}: {v:g}' for e, v in matched)})")
                else:
                    dps_ttm = latest_dps_row["dps"]
                    dps_ttm_basis = f"FY{fy_lab} DPS ({latest_dps_row['basis']}, period ended {fy_end}) — the {len(after)} quarterly fact(s) since have no prior-year comparative facts, so the year is not rolled forward"
            notes.append(f"dps_ttm: {why} — {dps_ttm_basis}")
        elif latest_dps_row:
            after = [e for e, _ in qf if e > latest_dps_row["period_end"]]
            notes.append(f"dps_ttm: {why}; the latest full-year DPS (FY{latest_dps_row['fy']}, period ended {latest_dps_row['period_end']}) is more than 15 months older than the newest filed period ({reference}) — a suspended / reinstated dividend"
                         + (f"; the {len(after)} quarterly fact(s) since ({', '.join(after)}) do not make a trailing twelve months" if after else "")
                         + "; dps_ttm and dividend_yield null")
        else:
            notes.append(f"dps_ttm: {why} and no FY DPS fact — dps_ttm null")
    if not any_facts:
        if paid_any:
            r = paid_rows[-1]
            notes.append(f"no dividends-per-share facts filed (CommonStockDividendsPerShareDeclared / CashPaid or IFRS equivalents) although cash dividends paid are filed ({_fmt_big(r['dividends_paid'])} for the period ended {r['period_end']}) — per-share rate not tagged; dps_ttm, dividend_yield and frequency null")
        else:
            notes.append("no dividends-per-share facts filed (CommonStockDividendsPerShareDeclared / CashPaid or IFRS equivalents) and no dividends paid — not a dividend payer")

    # frequency: the FY-count rule when the FY total carries a payment the
    # quarterly facts do not (the 10-K files the year, not the Q4), else the
    # spacing of the latest quarterly facts (a mid-year initiator reads quarterly)
    frequency, frequency_basis = None, None
    pos = sorted(e for e, d in q.items() if d["val"] > 0)
    recent = [e for e in pos if not stale(e)]
    if not any_facts:
        frequency = infer_frequency(0, None, None, False, False, dividends_paid=paid_any)
    elif not q:
        notes.append("frequency: only full-year DPS facts are filed (no quarterly / interim facts) — payment count not inferable")
    elif not recent:
        frequency = "irregular"
        notes.append(f"frequency: no positive quarterly DPS fact since {pos[-1] if pos else 'the filed history'} (newest filed period {reference}) — dividend suspended; shown as irregular")
    else:
        if latest_dps_row and latest_dps_row["basis"] == "fy_fact" and not dps_stale:
            fy_end = latest_dps_row["period_end"]
            in_fy = [d["val"] for e, d in q.items() if _add_days(fy_end, -400) < e <= fy_end and d["val"] > 0]
            if in_fy and latest_dps_row["dps"] > sum(in_fy) + 1e-9:
                frequency = infer_frequency(len(in_fy), latest_dps_row["dps"], sum(in_fy), True, True)
                frequency_basis = f"{len(in_fy)} quarterly DPS facts inside FY{latest_dps_row['fy']} plus one payment carried only in the FY total"
        if frequency is None:
            if len(recent) >= 2:
                frequency = frequency_from_spacing(recent)
                frequency_basis = f"spacing of the latest {min(4, len(recent))} quarterly DPS facts ({', '.join(recent[-4:])})"
            else:
                notes.append(f"frequency: a single quarterly DPS fact so far ({recent[-1]}) — payment frequency not inferable yet")

    # growth (on the comparable series; null when the latest annual row is stale)
    dps_growth_yoy = None
    if not dps_stale and len(comparable) >= 2 and fy_consecutive(comparable[-2]["period_end"], comparable[-1]["period_end"]):
        dps_growth_yoy = _g(comparable[-1]["dps"], comparable[-2]["dps"])
    cagr3 = dps_cagr(comparable, 3) if not dps_stale else None
    cagr5 = dps_cagr(comparable, 5) if not dps_stale else None
    gyears = growth_years(comparable) if not dps_stale else 0
    cut = last_cut_fy(comparable)
    if dps_stale:
        notes.append(f"growth: the latest annual DPS row (FY{latest_dps_row['fy']}, period ended {latest_dps_row['period_end']}) is more than 15 months older than the newest filed period ({reference}) — YoY growth, CAGR and growth years null")

    # payout ratios on the latest fiscal year in the annual table
    pr_eps = pr_oe = pr_fcf = None
    if latest_fy_row:
        d_fy = by_end.get(latest_end)
        pr_eps = payout_ratio(d_fy, latest_fy_row.get("eps_diluted"))
        pr_oe = payout_ratio(latest_fy_row.get("dividends_paid"), latest_fy_row.get("oe_conservative"))
        pr_fcf = payout_ratio(latest_fy_row.get("dividends_paid"), latest_fy_row.get("fcf"))
        if d_fy is None and any_facts:
            notes.append(f"payout_ratio_eps: no DPS fact for FY{payout_fy} (latest fiscal year in the annual table)")
        if latest_fy_row.get("dividends_paid") is None and any_facts:
            notes.append(f"payout_ratio_oe / payout_ratio_fcf: dividends paid not filed for FY{payout_fy}")

    # flows: the last four quarterly rows when they are consecutive quarters;
    # a filer without 10-Qs (20-F/40-F) falls back to the latest fiscal year's
    # annual flows, labelled as such. Each leg records how complete it is.
    last4 = qrows[-4:] if len(qrows) >= 4 and consecutive_quarters([r["period_end"] for r in qrows[-4:]]) else []
    flows = {k: ttm_sum(r.get(k) for r in last4) if last4 else None for k in FLOW_KEYS}
    legs, flows_basis, flows_end = {}, None, None

    def never_filed(k):
        return filed_any.get(k) is False

    if last4:
        flows_basis = f"sum of the four quarterly rows {last4[0]['period_end']}..{last4[-1]['period_end']}"
        flows_end = last4[-1]["period_end"]
        for k in FLOW_KEYS:
            if flows[k] is not None:
                legs[k] = {"value": flows[k], "basis": "4/4 quarters filed", "complete": True}
                continue
            filed = [(r["period_end"], r[k]) for r in last4 if _num(r.get(k))]
            missing = [r["period_end"] for r in last4 if not _num(r.get(k))]
            if filed:
                legs[k] = {"value": sum(v for _, v in filed), "basis": f"{len(filed)}/4 quarters filed ({', '.join(e for e, _ in filed)}) — a lower bound", "complete": False}
            elif never_filed(k):
                legs[k] = {"value": 0.0, "basis": "never filed in any period — zero by the filer's own statements", "complete": True}
            else:
                legs[k] = {"value": None, "basis": "not filed for any of the four quarters", "complete": False}
            notes.append(f"{k}_ttm: not all of the last four quarters have a filed {k} figure (missing {', '.join(missing)})" + ("" if filed else (" — the tag was never filed in any period, so the leg counts as zero" if never_filed(k) else "")))
    elif not qrows and latest_fy_row:
        flows_basis = f"FY{payout_fy} annual flows (period ended {latest_end}) — no quarterly filings (20-F/40-F filer)"
        flows_end = latest_end
        for k in FLOW_KEYS:
            v = latest_fy_row.get(k)
            if _num(v):
                legs[k] = {"value": v, "basis": f"FY{payout_fy} annual fact", "complete": True}
            elif never_filed(k):
                legs[k] = {"value": 0.0, "basis": "never filed in any period — zero by the filer's own statements", "complete": True}
            else:
                legs[k] = {"value": None, "basis": f"not filed for FY{payout_fy}", "complete": False}
        notes.append("quarterly flows: no quarterly facts (20-F/40-F filer without 10-Qs) — dividends_paid_ttm / buybacks_ttm / issuance_ttm null; the buyback and shareholder yields use the latest fiscal year's annual flows")
    else:
        for k in FLOW_KEYS:
            legs[k] = {"value": None, "basis": "fewer than four consecutive quarterly rows", "complete": False}
        notes.append("quarterly flows: fewer than four consecutive quarterly rows — dividends_paid_ttm / buybacks_ttm / issuance_ttm null")

    # price, shares, market cap
    diluted = next((r["shares_diluted"] for r in reversed(qrows) if _num(r.get("shares_diluted"))), None)
    diluted_src = "latest quarterly weighted-average diluted" if diluted is not None else None
    if diluted is None and annual:
        diluted = next((r["shares_diluted"] for r in reversed(annual) if _num(r.get("shares_diluted"))), None)
        diluted_src = "latest annual weighted-average diluted" if diluted is not None else None
    inst = ctx.get("shares_instant")
    if inst and _num(inst[0]) and inst[0] > 0:
        shares, shares_as_of, shares_src = inst[0], inst[1], inst[2]
    else:
        shares, shares_as_of, shares_src = diluted, None, diluted_src
        if shares is not None:
            notes.append(f"shares: no period-end / cover-page share count filed — market cap uses the {diluted_src} count")
    if price is None:
        notes.append("price: neither prices.json nor score.json carries a price — yields null")
    elif price_source and "score.json" in price_source:
        notes.append(f"price: {price} from score.json ({price_date}); prices.json absent")
    market_cap = price * shares if (_num(price) and _num(shares)) else None
    market_cap_basis = f"{price} × {shares:,.0f} shares ({shares_src}" + (f", as of {shares_as_of})" if shares_as_of else ")") if market_cap is not None else None
    if market_cap is None and shares is None:
        notes.append("shares: no share count filed — market cap and yields null")

    # yields
    def leg(k):
        return legs.get(k, {}).get("value")

    div_leg, bb_leg, iss_leg = leg("dividends_paid"), leg("buybacks"), leg("share_issuance")
    bb_complete = legs.get("buybacks", {}).get("complete") and _num(bb_leg)
    net_bb = (bb_leg - iss_leg) if (_num(bb_leg) and _num(iss_leg)) else None
    sh_total = (div_leg + bb_leg - iss_leg) if (_num(div_leg) and _num(bb_leg) and _num(iss_leg)) else None
    sh_basis = " + ".join(f"{k} ({legs[k]['basis']})" for k in ("dividends_paid", "buybacks") if k in legs) + (f" − share_issuance ({legs['share_issuance']['basis']})" if "share_issuance" in legs else "")
    if flows_basis:
        sh_basis = f"{sh_basis}; {flows_basis}"
    history = [dict({"period_end": e, "dps": q[e]["val"], "kind": basis}, **({"split_factor": q[e]["split_factor"]} if q[e].get("split_factor") else {})) for e in sorted(q, reverse=True)[:20]]

    # the filing feed is ahead of companyfacts: say so
    lfp = ctx.get("latest_filed_period") or {}
    newest = max(((p, f) for f, p in lfp.items() if p), default=None)
    if newest and reference and newest[0] > reference:
        msg = f"latest {newest[1]} (period {newest[0]}) is not yet in EDGAR companyfacts — annual / quarterly rows, TTM flows and this dividends block stop at {reference}"
        notes.append(msg)
        if isinstance(ctx.get("warnings"), list):
            ctx["warnings"].append(msg)

    return {
        "dps_ttm": dps_ttm, "dps_ttm_basis": dps_ttm_basis, "dps_basis": basis,
        "frequency": frequency, "frequency_basis": frequency_basis,
        "annual_dps": annual_out,
        "dps_growth_yoy": dps_growth_yoy, "dps_cagr_3y": cagr3, "dps_cagr_5y": cagr5,
        "growth_years": gyears, "last_cut_fy": cut,
        "growth_from_fy": comparable[0]["fy"] if comparable else None,
        "basis_breaks": [{"period_end": e, "dps_ratio": rd, "shares_ratio": rs} for e, rd, rs in breaks],
        "split_adjustments": [{"effective": d, "ratio": r} for d, r in (ctx.get("splits") or [])],
        "payout_ratio_eps": pr_eps, "payout_ratio_oe": pr_oe, "payout_ratio_fcf": pr_fcf,
        "payout_fy": payout_fy,
        "dividends_paid_ttm": flows["dividends_paid"], "buybacks_ttm": flows["buybacks"], "issuance_ttm": flows["share_issuance"],
        "ttm_period_end": last4[-1]["period_end"] if last4 else None,
        "flows_basis": flows_basis, "flows_period_end": flows_end, "legs": legs,
        "price": price, "price_date": price_date, "price_source": price_source,
        "shares_outstanding": shares, "shares_as_of": shares_as_of, "shares_source": shares_src,
        "shares_diluted": diluted, "shares_diluted_source": diluted_src,
        "market_cap": market_cap, "market_cap_basis": market_cap_basis,
        "dividend_yield": _ratio(dps_ttm, price) if _num(price) and price > 0 else None,
        "buyback_yield": _ratio(bb_leg, market_cap) if (market_cap and bb_complete) else None,
        "net_buyback_yield": _ratio(net_bb, market_cap) if (market_cap and net_bb is not None) else None,
        "shareholder_yield": _ratio(sh_total, market_cap) if (market_cap and sh_total is not None) else None,
        "shareholder_yield_basis": sh_basis if sh_total is not None else None,
        "shareholder_yield_complete": bool(sh_total is not None and all(legs[k].get("complete") for k in FLOW_KEYS if k in legs)),
        "history": history,
        "notes": notes,
    }


def dividends_inputs(facts):
    """The filed DPS series the dividends block reads — quarterly direct facts
    (declared / paid) and FY-duration facts (declared / paid) — restated for
    filed stock splits (apply_splits). Returns (dps_q, dps_fy, meta) with
    meta = {splits: [(date, ratio)], split_notes: [...]}."""
    fy_starts = core_fy_starts(facts)
    dps_q = {"declared": quarterly_by_tag(facts, DUR["dps_declared"], derive=False, direct_window=DPS_DIRECT_WINDOW, fy_starts=fy_starts),
             "paid": quarterly_by_tag(facts, DUR["dps_paid"], derive=False, direct_window=DPS_DIRECT_WINDOW, fy_starts=fy_starts)}
    fy = {b: annual_series(facts, DUR[f"dps_{b}"], True, with_filed=True) for b in ("declared", "paid")}
    dps_fy = {b: fy[b][0] for b in fy}
    fy_filed = {b: fy[b][3] for b in fy}
    notes, splits = [], []
    for d, r, used, ev in split_direction(split_events(facts), _shares_with_filed(facts)):
        splits.append((d, used))
        if used != r:
            notes.append(f"split ratio {r:g} filed for {d} read as {used:g} new shares per old share — {ev}")
    dps_q, dps_fy, adj_notes = apply_splits(dps_q, dps_fy, fy_filed, splits)
    return dps_q, dps_fy, {"splits": splits, "split_notes": notes + adj_notes}


def _shares_with_filed(facts):
    """{period_end: (diluted shares, filed)} for the annual diluted share count."""
    vals, _, _, filed = annual_series(facts, DUR["shares_diluted"], True, with_filed=True)
    return {e: (v, filed.get(e)) for e, v in vals.items()}


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
    # Codex review of PR #2: the TTM numerator sums four quarters, so the
    # denominator is the duration-weighted average of the four quarterly
    # diluted weighted-average counts — the latest quarter alone mismatches
    # during buybacks or dilution.
    _sh = [r.get("shares_diluted") for r in last4]
    if all(isinstance(v, (int, float)) and v > 0 for v in _sh):
        _ends = [r["period_end"] for r in last4]
        _gaps = [_days(_ends[i - 1], _ends[i]) for i in range(1, 4)]
        _w = [_gaps[0]] + _gaps  # the first quarter's length ≈ the following gap
        out["shares_diluted"] = sum(v * d for v, d in zip(_sh, _w)) / sum(_w)
        out["shares_basis"] = "duration-weighted average of the four quarterly diluted weighted-average counts" + \
            (" (a fiscal-Q4 count derived as 4 x FY - the other three quarters)" if any(r.get("shares_diluted_derived") for r in last4) else "")
    else:
        out["shares_diluted"] = last4[-1].get("shares_diluted")
        out["shares_basis"] = "latest quarter's diluted weighted-average count (not all four quarters filed)"
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
    quarterly = build_quarterly(facts, warnings=warnings, revenue_mode=(tag_summary.get("revenue_mode") or ["standard"])[0], annual=annual)
    ttm = build_ttm(quarterly)
    profile = build_profile(cik, facts)
    dps_q, dps_fy, dmeta = dividends_inputs(facts)
    price, price_date, price_source = _read_price(folder)
    filed_any = {"dividends_paid": bool(duration_facts(facts, DUR["dividends_paid"])),
                 "buybacks": bool(duration_facts(facts, DUR["buybacks"])),
                 "share_issuance": bool(combined_duration_facts(facts, DUR["share_issuance"], ISSUANCE_SUPERSETS))}
    ctx = {"filed_any": filed_any, "shares_instant": latest_share_count(facts),
           "latest_filed_period": {f: v.get("period") for f, v in (profile.get("latest_filings") or {}).items() if isinstance(v, dict)},
           "split_notes": dmeta["split_notes"], "splits": dmeta["splits"], "warnings": warnings}
    dividends = build_dividends(annual, quarterly, dps_q, dps_fy, price, price_date, price_source, ctx)
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
           "profile": profile, "annual": annual, "quarterly": quarterly, "ttm": ttm, "dividends": dividends,
           "tags_used": tag_summary, "warnings": warnings}
    if "--no-write" not in sys.argv:
        os.makedirs(folder, exist_ok=True)
        with open(f"{folder}/fundamentals.json", "w", encoding="utf-8") as f:
            json.dump(out, f, indent=1)
    summary = {"ticker": ticker, "cik": cik, "annual_years": len(annual), "quarters": len(quarterly),
               "ttm_period": (ttm or {}).get("period_end"), "latest_filings": profile.get("latest_filings"), "warnings": warnings,
               "dividends": {k: dividends.get(k) for k in ("dps_ttm", "dps_ttm_basis", "dps_basis", "frequency", "frequency_basis", "dividend_yield",
                                                           "growth_years", "last_cut_fy", "dps_cagr_5y", "dividends_paid_ttm", "buybacks_ttm", "issuance_ttm",
                                                           "buyback_yield", "net_buyback_yield", "shareholder_yield", "shareholder_yield_basis", "shareholder_yield_complete",
                                                           "shares_outstanding", "shares_source", "market_cap", "price", "price_date", "notes")}}
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
