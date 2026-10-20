#!/usr/bin/env python3
"""Filing-direct fundamentals store (v5.4, 2026-10-14).

Usage: python3 fundamentals.py <TICKER> [--cik N] [--no-write]

Pulls the SEC EDGAR data a READER of the company page needs but the valuation
engine does not, and writes <TICKER>/fundamentals.json — a committed file,
rewritten only when its content apart from `as_of` changed
(_stable.write_json_if_changed; the printed summary's `fundamentals_json` says
"written" or "unchanged"). The file is a snapshot as of its `as_of`: the 8-K
count is the 12 months to that date, and a run whose only other difference is
8-Ks ageing out of a later window leaves it alone (write_fundamentals). The
company page's Financials and Data tabs render from it. Nothing here feeds the DCF —
dcf_numbers.json stays the engine's domain and score.json make_score's.

Contents (every figure is a filed value, or arithmetic on filed values —
growth, margins, quarter = YTD minus prior YTD; nothing is estimated):
- profile: SIC, fiscal year end, filer category, exchanges, latest 10-K /
  10-Q filed + period, 8-K count in the 12 months to `as_of` (EDGAR
  submissions API).
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
  and `shareholder_yield_complete` say exactly which. 5.4.3 (re-verification
  fixes): every flow yield (buyback, net buyback, shareholder) is built the
  same way from the filed legs and `yield_basis` states per yield which legs
  went in, which were taken as zero (never-filed line), which were left out,
  and whether the figure is exact, a lower bound, an upper bound or neither —
  no headline carries a partial numerator without that flag; a DPS CAGR
  window that contains a year with no dividend (no annual row, or a filed
  zero — a suspension) is null and `notes` names the gap; an FY DPS fact two
  filings agree on beats a later filing's power-of-ten unit slip
  (dps_fy_facts); the unfiled-split guard requires the diluted EPS to have
  restated by the same factor (a real share issuance with a coincident cut
  stays a cut, `basis_breaks_rejected`); a label collision between two fiscal
  years ending in one calendar year is named (`fy_label_basis`, join on
  period_end). Market cap = price × the latest filed instant share count
  (cover-page dei count, else the balance sheet's) — unless that count is
  stale (dated more than dcf_engine.DEI_MAX_AGE_DAYS before the newest fiscal
  year end, ruling-sheet Q8 bug 2: TLK's 1995 count), and a dei count that is
  one class of a multi-class filer gives way to the same filing's all-class
  count (class_count_check, GGB); when no usable instant count exists (a
  dual-class filer's counts are class-dimensioned and dropped by the API —
  TKO — or the only one is stale) the most inclusive recent filed diluted
  weighted-average count is used and `shares_source` / `shares_basis` /
  `market_cap_basis` say so and why (fallback_share_count); a fallback that
  replaces a stale count outside SHARE_SCALE_BAND of the engine's validated
  count prices nothing (PAC), and one more than 20% from it that no other
  recent filed count corroborates gives way to the latest filed diluted
  count within 20% of it (SHARE_ANCHOR_TOL, ECHO; SF's split level stands). Quarterly rows carry dividends_paid, buybacks, share_issuance (with
  the contributing tags) and DPS. DPS is a per-share rate: only direct
  quarterly facts are used, never YTD subtraction; the cash flows derive like
  the other cash-flow lines. Price = <T>/prices.json stats.last; without
  prices.json (a fresh clone: the file is a gitignored cache) the close this
  file already used, carried with its date and source, unless score.json's
  analysis price is newer; else score.json price. Price-free file (2026-10-16):
  every leaf that depends on the price (price / price_date / price_source /
  price_note, market_cap and its basis, the four yields,
  yield_basis.*.denominator, yields_display.*.value / label — PRICE_LEAVES)
  is set by price_dividends() from the block's own price-free fields and is
  volatile for the file comparison, so a new close alone never rewrites the
  committed file; build_site.py reprices the block at the newer prices.json
  close with the same function. The price note ("from score.json", "no
  price") is `price_note`, not an entry of `notes`. A filing in the submissions feed that companyfacts has not
  ingested yet is named in `notes` and `warnings`. Anything not computable
  from filed values is null and `notes` says why. 5.4.5 (re-verification
  fixes): a dividends / buyback / issuance value filed below zero is a sign
  error read as its absolute amount (`legs[*].sign_corrected`,
  `yield_basis[*].sign_corrected`); the primary DPS basis is chosen by coverage
  of the last eight quarters; a fiscal year the primary tag never filed takes
  the other tag's FY fact; an FY DPS fact below its own quarters is not used;
  a power-of-ten disagreement prefers the value consistent with the year's
  quarters and neighbouring years; a cash payer whose per-share tags lapsed
  reads its frequency from dividends paid, not "suspended"; a split evidenced
  only by re-filed DPS and share counts restates the quarterly facts too.
  5.4.6 (second re-verification): the primary DPS basis is a stopped tag's
  other tag, else the tag with quarterly facts, else declared — the same at
  every filing date (choose_dps_basis); an FY DPS fact below its own quarters
  is set aside only when the other tag files a full-year total that replaces
  it, else kept with a note; a quarterly DPS fact re-filed later at another
  value is read from the filing that first reported it; the FY-count
  frequency rule needs the FY total and the quarters from the same tag and a
  remainder of at least half a quarterly payment; payer status / cadence from
  cash only off a common-stock dividends tag and never over filed zero DPS;
  issuance below zero is kept as filed unless its own fiscal year carries the
  opposite sign (`legs[*].kept_as_filed`), a quarter whose year-to-date facts
  decrease is left out as such (`legs[*].left_out`); an issuance "total" tag
  smaller than its components is summed with them; a split read from
  re-filed values takes a whole-number ratio, and the unfiled-split guard
  reads split-adjusted share counts.
Units are the filer's own (USD for almost every name; `currency` records
anything else). No FX conversion is applied here — the engine handles that
for the valuation; this file is for reading the filings as filed.
Ruling-sheet Q8 bugs 2-3 (Andrew, 2026-10-19; enrichment only, no engine
release): ONE money unit per file (money_unit — the currency the newest
annual filing files its core FY facts in, the all-filing count breaking a
tie; convenience translations and a former presentation currency are never
read, RDY, RTO);
a non-USD file's yields are null (its DPS and flows are not in the USD
price's currency; the block carries `currency`); an instant share count more
than 18 months before the newest fiscal year end is stale (TLK's 1995
count) and a cover-page dei count that is one class of a multi-class filer
gives way to the same filing's all-class count (class_count_check, GGB);
derived fcf / oe_conservative subtract the engine 5.5 intangible-capex leg
too (ENGINE_INTANGIBLE_TAGS via dcf_engine.capex_for_period; GGB, GMED).
"""
import json, sys, os, csv, datetime, time, math, statistics, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _stable import write_json_if_changed, same_content  # noqa: E402  (committed SEC file: no run-date-only rewrites)
import dcf_engine as _engine  # noqa: E402  (ruling-sheet Q8: the engine's intangible-capex leg and dei staleness rule; no I/O at import)
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
        with open(f"{SYS}/sec_tickers_exchange.json", encoding="utf-8") as f:
            sec = json.load(f)
        m = {}
        for rec in sec["data"]:
            m.setdefault(rec[2].upper(), rec[0])
        for cand in (ticker, ticker.replace("/", "-"), ticker.replace("/", ".")):
            if cand in m:
                return m[cand]
    except Exception:
        pass
    try:
        with open(f"{SYS}/universe.csv", encoding="utf-8", newline="") as f:
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
# ProceedsFromStockOptionsExercised doubles as the ASC 718 note disclosure
# ("cash received from option exercises"), the same cash a filer's statement
# line already carries as issuance of common stock / sale of treasury stock
# (KR, ESLT) — so those lines rank above it; a filer whose statement has an
# option line AND an ESPP line (ZS) still gets both summed.
_PLAN_TAGS = {"ProceedsFromIssuanceOfSharesUnderIncentiveAndShareBasedCompensationPlans", "ProceedsFromStockOptionsExercised", "ProceedsFromStockPlans"}
ISSUANCE_SUPERSETS = {
    "ProceedsFromIssuanceOrSaleOfEquity": "*",
    "ProceedsFromIssuanceOfCommonStock": _PLAN_TAGS | {"ProceedsFromIssuanceOfSharesUnderIncentiveAndShareBasedCompensationPlansIncludingStockOptions"},
    "ProceedsFromIssuanceOfSharesUnderIncentiveAndShareBasedCompensationPlansIncludingStockOptions": _PLAN_TAGS,
    "ProceedsFromSaleOfTreasuryStock": {"ProceedsFromStockOptionsExercised"},
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


def _units_pref(units, money=None):
    """The units of a tag in reading order (USD first). money= (the file's one
    money unit, money_unit) keeps only units that are not ANOTHER currency:
    the money unit itself, its per-share unit and the non-money units (shares,
    pure) — a convenience translation never enters a series (ruling-sheet Q8
    bug 3: RDY's FY2018 USD revenue beside its INR history)."""
    pref = [u for u in UNIT_PREF if u in units]
    order = pref + [u for u in units if u not in pref]
    if money is None:
        return order
    return [u for u in order if _unit_currency(u) in (None, money)]


def _unit_currency(unit_key):
    """The ISO currency a unit is denominated in ('INR' for INR and INR/shares), None for shares / pure."""
    base = str(unit_key).split("/")[0]
    return base if (len(base) == 3 and base.isalpha() and base.isupper()) else None


MONEY_UNIT_FORMS = ("10-K", "10-K/A", "20-F", "20-F/A", "40-F", "40-F/A")


def money_entries(facts):
    """[(unit, filed, accn)] — one per core FY fact (revenue, net income, OCF, assets) on an annual form, money units only."""
    out = []
    for key, duration in (("revenue", True), ("net_income", True), ("ocf", True), ("assets", False)):
        for taxonomy, tag in _pairs(DUR[key] if duration else INST[key]):
            for unit_key, es in ((facts.get("facts", {}).get(taxonomy, {}).get(tag) or {}).get("units") or {}).items():
                if "/" in unit_key or _unit_currency(unit_key) is None:
                    continue
                for e in es:
                    if e.get("fp") != "FY" or e.get("form", "") not in MONEY_UNIT_FORMS or not e.get("end"):
                        continue
                    if duration and not (e.get("start") and 330 <= _days(e["start"], e["end"]) <= 380):
                        continue
                    out.append((unit_key, e.get("filed") or "", e.get("accn")))
    return out


def money_counts(facts):
    """{unit: number of core FY facts (revenue, net income, OCF, assets) filed in it} — money units only."""
    counts = {}
    for u, _, _ in money_entries(facts):
        counts[u] = counts.get(u, 0) + 1
    return counts


def pick_money_unit(entries):
    """Ruling-sheet Q8 bug 3 (Andrew, 2026-10-19) — the one money unit of a
    file from its core FY facts `entries` [(unit, filed, accn)]: the currency
    the NEWEST annual filing (latest filed date) files most of its core facts
    in; the count over every filing breaks a tie, then USD. A filer that
    changed its presentation currency (RTO: GBP through the 20-F filed
    2025-03-26, USD from the one filed 2026-03-25, which restates FY2023-24)
    is read in the new one at once — an all-time majority would keep the old
    currency and drop the newest year until the new one outnumbered the
    history. Returns {"unit", "counts", "newest_filed", "translations"
    (other currencies the newest filing also files — convenience
    translations), "earlier" (other currencies only earlier filings file),
    split into "former" (the majority currency of at least one earlier
    filing — a former presentation currency: RTO's GBP, FMS's USD) and
    "earlier_translations" (a minority in every filing — convenience
    translations older filings carried: VOD's USD)}."""
    counts, by_filing = {}, {}
    latest = max((f for _, f, _ in entries), default="")
    for u, f, _ in entries:
        counts[u] = counts.get(u, 0) + 1
        by_filing.setdefault(f, {})
        by_filing[f][u] = by_filing[f].get(u, 0) + 1
    if not counts:
        return {"unit": "USD", "counts": {}, "translations": [], "earlier": [], "former": [], "earlier_translations": [], "newest_filed": None}
    newest = by_filing.get(latest, {})
    order = _units_pref(list(counts))
    unit = max(order, key=lambda u: (newest.get(u, 0), counts[u], -order.index(u)))
    earlier = sorted(u for u in counts if u != unit and u not in newest)
    led = {max(fc, key=lambda u: (fc[u], -order.index(u))) for fc in by_filing.values()}
    return {"unit": unit, "counts": counts, "newest_filed": latest or None,
            "translations": sorted(u for u in newest if u != unit), "earlier": earlier,
            "former": [u for u in earlier if u in led], "earlier_translations": [u for u in earlier if u not in led]}


def money_unit(facts):
    """Ruling-sheet Q8 bug 3 (Andrew, 2026-10-19): the ONE money unit of
    fundamentals.json — the currency the newest annual filing files most of
    its core FY facts (revenue, net income, OCF, assets) in, the all-filing
    count then USD breaking a tie (pick_money_unit); statements.money_unit
    applies the same rule to statements.json. Every money series, per-share
    series and flow leg is read in it (_units_pref(money=...)); facts the filer
    also files in another currency (convenience translations, or a former
    presentation currency) are not read."""
    return pick_money_unit(money_entries(facts))["unit"]


def money_unit_warning(pick):
    """The file warning that names the money unit and every currency left unread (pick_money_unit's result)."""
    unit, tr = pick["unit"], pick["translations"]
    fo, et = pick.get("former", []), pick.get("earlier_translations", [])
    left = []
    if tr:
        left.append(f"the filer's {', '.join(tr)} convenience translations are not read")
    if fo:
        left.append(f"the {', '.join(fo)} facts of filings before the newest annual report (filed {pick['newest_filed']}) are a former "
                    f"presentation currency and are not read")
    if et:
        left.append(f"the {', '.join(et)} convenience translations of earlier filings are not read")
    if unit != "USD":
        return (f"core facts filed in {unit} — figures are shown as filed (no FX conversion here; the engine converts for the valuation)"
                + "".join(f"; {x}" for x in left) + f"; the price is USD, so the price-based yields are not computed")
    if left:
        return "the filer also files core facts in another currency — only the USD facts are read: " + "; ".join(left)
    return None


def annual_series(facts, tags, duration=True, with_filed=False, unit=None, money=None):
    """{period_end: val}, {period_end: tag}, {period_end: unit} — FY facts on
    annual forms, merged across candidate tags per period, latest filing wins.
    with_filed=True adds a fourth dict {period_end: filed date}. unit= reads
    only that unit (the same line in another line's currency); money= reads
    no currency other than that one (_units_pref)."""
    merged, tag_by, unit_by, filed_by = {}, {}, {}, {}
    for taxonomy, tag in _pairs(tags):
        tf = facts.get("facts", {}).get(taxonomy, {})
        if tag not in tf:
            continue
        units = tf[tag].get("units", {})
        for unit_key in _units_pref(units, money):
            if unit is not None and unit_key != unit:
                continue
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


def duration_facts(facts, tags, money=None):
    """{(start, end): (val, tag, unit, filed, accn)} across 10-Q/10-K/20-F/40-F
    forms, merged per period by tag priority (latest filing wins per tag).
    money=: no currency other than that one (_units_pref)."""
    out = {}
    for taxonomy, tag in _pairs(tags):
        tf = facts.get("facts", {}).get(taxonomy, {})
        if tag not in tf:
            continue
        units = tf[tag].get("units", {})
        for unit_key in _units_pref(units, money):
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


def combined_duration_facts(facts, tags, supersets=None, money=None):
    """{(start, end): (sum, "tagA+tagB", unit, filed, accn)}: for each period,
    the DISTINCT candidate tags filed in the same filing are summed (a filer
    that books option exercises and ESPP proceeds on two lines). The filing is
    the latest one that reports the period, so a renamed tag in a later 10-K
    never double-counts an older one; a tag that is by definition the total of
    other tags present in the filing (`supersets`) counts alone.
    5.4.6 review blocker (FIG FY2025: ProceedsFromIssuanceOfCommonStock 0
    beside ProceedsFromStockOptionsExercised 131.7M and ProceedsFromStockPlans
    26.4M; DHI FY2025 common 0 beside its plan line 18.5M): a "total" is only a
    total when it is at least the sum of the present parts it would drop
    (within 0.5% rounding) — a smaller one is a separate statement line, and
    every line is summed."""
    supersets = supersets or {}
    per_period = {}
    for taxonomy, tag in _pairs(tags):
        tf = facts.get("facts", {}).get(taxonomy, {})
        if tag not in tf:
            continue
        units = tf[tag].get("units", {})
        for unit_key in _units_pref(units, money):
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
                drop = (present - {total}) if parts == "*" else (present & set(parts))
                tv = tagvals[total][0]
                dv = sum(tagvals[t][0] for t in drop if _num(tagvals[t][0]))
                if _num(tv) and tv >= dv - max(1.0, 0.005 * abs(dv)):
                    present = present - drop
        unit = next(iter(tagvals.values()))[1]
        keep = sorted(t for t in present if tagvals[t][1] == unit and _num(tagvals[t][0]))
        if not keep:
            continue
        out[key] = (sum(tagvals[t][0] for t in keep), "+".join(keep), unit, max(tagvals[t][2] for t in keep), accn)
    return out


def combined_annual(facts, tags, supersets=None, money=None):
    """{period_end: val}, {period_end: tags} for FY-length periods of combined_duration_facts (annual forms only)."""
    vals, tag_by = {}, {}
    for (s, e), (v, tag, unit, filed, accn) in combined_duration_facts(facts, tags, supersets, money=money).items():
        if 330 <= _days(s, e) <= 380:
            vals[e], tag_by[e] = v, tag
    return vals, tag_by


def quarterly_series(facts, tags, derive=True, direct_window=(80, 120), fy_starts=None, prebuilt=None, money=None):
    """{quarter_end: {val, fq, fy_start, derived, tag}} for the fiscal quarters
    the filer's facts support. Direct 3-month facts win; otherwise (cash-flow
    lines are filed YTD only) quarter = YTD - prior YTD within the same
    fiscal year, Q4 = FY - nine-month YTD.
    `direct_window` (days) says what counts as a direct quarterly fact (80-120: a 16-week first quarter, e.g. KR, is still a filed quarter — Codex review of PR #2);
    `fy_starts` adds known fiscal-year starts (from the core statements) so a
    tag filed year-to-date without its own annual fact can still be derived.
    `prebuilt` is a ready {(start, end): (val, tag, unit, filed, accn)} map
    (combined_duration_facts) used instead of reading `tags`."""
    f = prebuilt if prebuilt is not None else duration_facts(facts, tags, money=money)
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


def core_fy_periods(facts, money=None):
    """The (start, end) fiscal-year periods the core statements file (annual
    revenue / net income / OCF contexts of 330-380 days) — the years that have
    an annual row."""
    out = set()
    for k in ("revenue", "net_income", "ocf"):
        for (s, e) in duration_facts(facts, DUR[k], money=money):
            if 330 <= _days(s, e) <= 380:
                out.add((s, e))
    return out


def core_fy_starts(facts, money=None):
    """Fiscal-year start dates the core statements establish (annual revenue /
    net income / OCF periods and the year that follows each)."""
    starts = set()
    for (s, e) in core_fy_periods(facts, money=money):
        starts.add(s)
        starts.add((datetime.date.fromisoformat(e) + datetime.timedelta(days=1)).isoformat())
    return starts


def quarterly_by_tag(facts, tags, derive=True, direct_window=(80, 120), fy_starts=None, money=None):
    """quarterly_series run per candidate tag and merged per quarter end in
    tag-priority order — a derived quarter never subtracts one tag's leg from
    another's."""
    out = {}
    for pair in _pairs(tags):
        for e, d in quarterly_series(facts, [pair], derive=derive, direct_window=direct_window, fy_starts=fy_starts, money=money).items():
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


# Codex review of PR #2 (HBAN FY2025: 17.221B here vs 18.482B in statements.json):
# the debt_total tags are of two kinds. A LONG-TERM total (LongTermDebt,
# LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities) carries the
# current maturities of long-term debt but not the short-term borrowings a
# filer reports on their own line (ShortTermBorrowings / CommercialPaper /
# NotesPayableCurrent / IFRS ShorttermBorrowings = debt_cur_st), so those are
# added — never the current maturities (debt_cur_ltd), which are inside it.
# An aggregate of long- AND short-term debt (DebtLongtermAndShorttermCombinedAmount,
# IFRS Borrowings) already holds them and stands alone.
LT_DEBT_TOTAL_TAGS = frozenset({"LongTermDebt", "LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities"})


def debt_from_total_tag(tot, tot_tag, st=None, st_tag=None, cur_agg=None, unit_mismatch=None):
    """(total debt, basis) for a period whose only long-term figure is a
    debt_total tag. tot_tag / st_tag are bare element names; st = the
    short-term-borrowings component (debt_cur_st) in the same unit as tot;
    cur_agg = an aggregate current-debt fact (DebtCurrent), used only to say
    that short-term borrowings inside it could not be separated;
    unit_mismatch = the unit short-term borrowings were filed in when it is
    not tot's (they are then left out, never added across currencies)."""
    if tot_tag not in LT_DEBT_TOTAL_TAGS:
        return tot, f"total tag ({tot_tag}, includes short-term debt)"
    if st is not None:
        return tot + st, f"total tag ({tot_tag}, long-term incl. current maturities) + short-term borrowings ({st_tag})"
    if unit_mismatch:
        return tot, f"total tag ({tot_tag}, long-term incl. current maturities); short-term borrowings filed only in {unit_mismatch} — not added"
    if cur_agg is not None:
        return tot, f"total tag ({tot_tag}, long-term incl. current maturities); DebtCurrent has no separately filed short-term part — none added"
    return tot, f"total tag ({tot_tag}, long-term incl. current maturities; no short-term borrowings filed)"


# Ruling-sheet Q8 (Andrew, 2026-10-19), GGB / GMED: the enrichment's derived
# fcf / oe_conservative are on the engine's capex definition (engine 5.5:
# capex = the PP&E leg + intangible purchases, dcf_engine.capex_for_period).
# The intangible leg is the engine's own: its tag list, its rules (a negative
# fact dropped, a $0 fact ignored, one cash-flow line tagged twice counted
# once, a value the same tag also files on a multi-year context dropped as a
# cumulative total — ECHO), so it never drifts from the scored CSV. The
# capex_intangibles display field keeps its own wider list (it also shows
# capitalized software, PaymentsToDevelopSoftware, which is not capex until
# the Q6 / engine 5.7 follow-on) and is not what is deducted.
ENGINE_INTANGIBLE_TAGS = _engine.CAPEX_INTANGIBLE_TAGS


def intangible_capex_annual(facts, money, ppe):
    """{period_end: intangible purchases the engine adds on top of the PP&E leg}
    for FY periods, read in `money`. ppe: {period_end: (tag, value)} — the PP&E
    leg capex_for_period checks the combined-tag rule against."""
    cumulative = _engine.cumulative_context_values(facts, ENGINE_INTANGIBLE_TAGS, units=(money,))
    per_tag = []
    for t in ENGINE_INTANGIBLE_TAGS:
        vals, _, units, filed = annual_series(facts, [t], True, with_filed=True, money=money)
        per_tag.append((t[1] if isinstance(t, tuple) else t, vals, units, filed))
    out = {}
    for pe in sorted({pe for _, vals, _, _ in per_tag for pe in vals}):
        legs = [(name, vals[pe], units[pe], filed.get(pe)) for name, vals, units, filed in per_tag if pe in vals]
        roll = [(ppe[pe][0], ppe[pe][1], money, None)] if pe in ppe else []
        res = _engine.capex_for_period(roll, [], legs, cumulative=cumulative)
        if res["intangible_tags"]:
            out[pe] = _whole(res["intangibles"])
    return out


def _whole(v):
    """A sum of filed whole amounts kept an int (the file's numbers keep their JSON type)."""
    return int(v) if isinstance(v, float) and v.is_integer() else v


def _ytd_rank(start, end):
    """1..4 for a ~1/2/3/4-quarter year-to-date context (±35 days, quarterly_series' rule), else None."""
    d = _days(start, end)
    rank = round(d / 91.25)
    return rank if (1 <= rank <= 4 and abs(d - rank * 91.25) <= 35 and d <= 380) else None


def intangible_capex_periods(facts, money):
    """{(start, end): intangible purchases} per exact duration context (up to
    380 days) — each period through the engine's capex_for_period (its tags,
    negative / $0 / same-line-twice / cumulative-duplicate rules, the PP&E
    leg's combined-tag rule against the period's own capex tag). A fiscal-year
    period carries the annual figure (intangible_capex_annual), so the quarters
    and the TTM can never disagree with the annual row for the same window."""
    cumulative = _engine.cumulative_context_values(facts, ENGINE_INTANGIBLE_TAGS, units=(money,))
    per_tag = []
    for t in ENGINE_INTANGIBLE_TAGS:
        taxonomy, name = t if isinstance(t, tuple) else ("us-gaap", t)
        units = ((facts.get("facts", {}).get(taxonomy, {}).get(name) or {}).get("units") or {})
        keep = {u: [e for e in es if not ((name, u, e.get("val")) in cumulative and e.get("start") and e.get("end")
                                          and _days(e["start"], e["end"]) <= _engine.CUMULATIVE_CONTEXT_DAYS)]
                for u, es in units.items()}
        per_tag.append((name, duration_facts({"facts": {taxonomy: {name: {"units": keep}}}}, [(taxonomy, name)], money=money)))
    ppe = duration_facts(facts, DUR["capex"], money=money)
    pv, pt, _ = annual_series(facts, DUR["capex"], True, money=money)
    annual = intangible_capex_annual(facts, money, {pe: (pt.get(pe), v) for pe, v in pv.items()})
    out = {}
    for per in sorted({k for _, m in per_tag for k in m}):
        if _days(per[0], per[1]) > _engine.CUMULATIVE_CONTEXT_DAYS:
            continue
        if 330 <= _days(per[0], per[1]) <= 380:
            if per[1] in annual:
                out[per] = annual[per[1]]
            continue
        legs = [(name, m[per][0], m[per][2], m[per][3]) for name, m in per_tag if per in m]
        roll = [(ppe[per][1], ppe[per][0], money, None)] if per in ppe else []
        res = _engine.capex_for_period(roll, [], legs, cumulative=cumulative)
        if res["intangible_tags"]:
            out[per] = _whole(res["intangibles"])
    return out


def _intangible_fy_starts(periods, fy_starts):
    """Known fiscal-year starts: the core statements' plus each FY intangible period's start and the day after its end."""
    fy = [(s, e) for (s, e) in periods if 330 <= _days(s, e) <= 380]
    return set(fy_starts or ()) | {s for s, _ in fy} | {(datetime.date.fromisoformat(e) + datetime.timedelta(days=1)).isoformat() for _, e in fy}


def intangible_capex_quarterly(facts, money, fy_starts=None, periods=None, fy_periods=None):
    """{quarter_end: intangible purchases} (verifier round 1: IREN, PFGC, RMD).
    Within a fiscal year each tagged year-to-date leg less the latest tagged
    shorter one (0 when none — a line first tagged in the six-month 10-Q is
    all Q2's: IREN's 107,573,000), Q4 = FY less the latest tagged YTD, so the
    quarters of a year always sum to its FY figure; a quarter can be negative
    (RMD's Q2 FY2026: a YTD restated down) — only the TTM total is floored
    (intangible_capex_ttm). Direct three-month facts count only in a fiscal
    year with no year-to-date leg. A completed fiscal year (its annual row is
    filed — fy_periods, core_fy_periods) with no FY intangible figure (the
    10-K leaves the line untagged, or re-files it as $0, which the engine
    ignores) deducts nothing in any quarter, as its annual row and the engine
    deduct nothing (verifier round 2: RMD FY2024 YTD 10.8M / 12.0M / 14.0M,
    then the FY re-filed as 0; BAX FY2025)."""
    per = periods if periods is not None else intangible_capex_periods(facts, money)
    starts = _intangible_fy_starts(per, fy_starts)
    if fy_periods is None:
        fy_periods = core_fy_periods(facts, money=money) if facts is not None else set()
    filed_years = {s for s, e in fy_periods if 330 <= _days(s, e) <= 380}
    fy_years = {s for (s, e) in per if 330 <= _days(s, e) <= 380}
    unreconciled = filed_years - fy_years  # completed years with no FY intangible figure
    out, ytd_years = {}, set()
    for s in sorted(starts):
        if s in unreconciled:
            ytd_years.add(s)  # no direct three-month fallback either
            continue
        by_rank = {}
        for (s2, e) in sorted(per):
            r = _ytd_rank(s2, e) if s2 == s else None
            if r is not None and r not in by_rank:
                by_rank[r] = (e, per[(s2, e)])
        if by_rank:
            ytd_years.add(s)
        prev = 0
        for r in (1, 2, 3, 4):
            if r in by_rank:
                e, v = by_rank[r]
                out[e] = _whole(v - prev)
                prev = v
    for (s, e), v in sorted(per.items()):
        if 80 <= _days(s, e) <= 120 and e not in out:
            fs = max((x for x in starts if x <= s and _days(x, s) <= 300), default=None)
            if fs not in ytd_years:
                out[e] = v
    return out


def intangible_capex_ttm(facts, money, qrows, fy_starts=None, periods=None):
    """The TTM intangible leg the engine's way (ttm.py add_intangibles; verifier
    round 1): FY − the prior year's same-length YTD + the current YTD at the
    last quarter's end (the FY figure alone when that end is a fiscal year
    end), an untagged leg 0; a prior-YTD amount with no FY amount or above it
    leaves the FY remainder unknown and neither leg counts (R4-INTANG); the
    total is never negative. None without four quarter rows or a known fiscal
    year start for the last one (build_ttm then sums the quarters)."""
    if not qrows or len(qrows) < 4:
        return None
    per = periods if periods is not None else intangible_capex_periods(facts, money)
    starts = _intangible_fy_starts(per, fy_starts)
    end = qrows[-1]["period_end"]
    fs = max((x for x in starts if x <= end and _ytd_rank(x, end) is not None), default=None)
    if fs is None:
        return None
    rank = _ytd_rank(fs, end)
    cur = per.get((fs, end), 0)
    if rank == 4:
        return _whole(max(0, cur))
    prev_end = (datetime.date.fromisoformat(fs) - datetime.timedelta(days=1)).isoformat()
    prev_fs = max((x for x in starts if x < fs and 330 <= _days(x, prev_end) <= 380), default=None)
    fy = per.get((prev_fs, prev_end)) if prev_fs else None
    prior = next((v for (s2, e), v in sorted(per.items()) if s2 == prev_fs and e < fs and _ytd_rank(s2, e) == rank), 0) if prev_fs else 0
    if prior > 0 and (fy is None or fy < prior):
        fy, prior = 0, 0
    return _whole(max(0, (fy or 0) - prior + cur))


def build_annual(facts, money=None):
    """(rows, tag_summary, [currency] — empty for USD). Every money / per-share
    line is read in the file's one money unit (money_unit; ruling-sheet Q8 bug 3)."""
    money = money or money_unit(facts)
    series, tags, units = {}, {}, {}
    for k, t in DUR.items():
        series[k], tags[k], units[k] = annual_series(facts, t, True, money=money)
    for k, t in INST.items():
        series[k], tags[k], units[k] = annual_series(facts, t, False, money=money)
    series["share_issuance"], tags["share_issuance"] = combined_annual(facts, DUR["share_issuance"], ISSUANCE_SUPERSETS, money=money)
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
    currency = {money} if money != "USD" else set()
    st_same_unit = {}  # {unit: annual_series of debt_cur_st read in that unit only; "_any": read in every unit}
    intang_by_end = intangible_capex_annual(facts, money, {pe: (tags["capex"].get(pe), v) for pe, v in series["capex"].items()})  # Q8: the engine's intangible leg
    for p in periods:
        g = lambda k: series[k].get(p)
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
            st, st_tag, st_unit_other = g("debt_cur_st"), tags["debt_cur_st"].get(p), None
            tot_unit = units["debt_total"].get(p)
            if st is None:
                # the money-unit series leaves another currency's short-term line out (Q8 bug 3); still name it
                if "_any" not in st_same_unit:
                    st_same_unit["_any"] = annual_series(facts, INST["debt_cur_st"], False)
                _u = st_same_unit["_any"][2].get(p)
                st_unit_other = _u if (_u and _u != tot_unit) else None
            if st is not None and units["debt_cur_st"].get(p) != tot_unit:
                # never add across currencies (JD files ShortTermBorrowings in USD
                # convenience translation and LongTermDebt in RMB): read the line
                # in the total's own unit, else leave it out and say so
                st_unit_other = units["debt_cur_st"].get(p)
                if tot_unit not in st_same_unit:
                    st_same_unit[tot_unit] = annual_series(facts, INST["debt_cur_st"], False, unit=tot_unit)
                st, st_tag = st_same_unit[tot_unit][0].get(p), st_same_unit[tot_unit][1].get(p)
            total_debt, debt_basis = debt_from_total_tag(d_tot, tags["debt_total"].get(p), st, st_tag, cur_agg=g("debt_current"),
                                                         unit_mismatch=(st_unit_other if st is None else None))
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
        intang = intang_by_end.get(p)  # the engine's intangible leg, added on top of the PP&E leg
        fcf = (ocf - capex - (intang or 0)) if (ocf is not None and capex is not None) else None
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


def build_quarterly(facts, max_q=12, warnings=None, revenue_mode=None, annual=None, money=None):
    money = money or money_unit(facts)
    q = {k: quarterly_series(facts, DUR[k], derive=(k not in DIRECT_ONLY), money=money) for k in QUARTERLY_FIELDS}
    # bank presentation: revenue = Revenues total, else NII + noninterest income —
    # on ONE basis for every quarter (Codex review of PR #2); quarters with
    # neither are dropped from the revenue series rather than falling back to
    # contract revenue or interest income alone.
    q_nii, q_nonint, q_revt = (quarterly_series(facts, DUR[k], money=money) for k in ("nii", "noninterest_income", "revenues_total"))
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
        q["revenue"] = {e: dict(d, tag=f"{d.get('tag')} (filer total)") for e, d in quarterly_series(facts, DUR["revenues_total"], money=money).items()}
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
    q_intang = intangible_capex_quarterly(facts, money, fy_starts=core_fy_starts(facts, money=money))  # Q8: the engine's intangible leg
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
        row["fcf"] = (ocf - capex - q_intang.get(e, 0)) if (ocf is not None and capex is not None) else None
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
    fy_starts = core_fy_starts(facts, money=money)
    extra = {k: quarterly_by_tag(facts, DUR[k], derive=True, fy_starts=fy_starts, money=money) for k in QUARTERLY_FLOW_FIELDS if k != "share_issuance"}
    extra["share_issuance"] = quarterly_series(None, None, derive=True, fy_starts=fy_starts,
                                               prebuilt=combined_duration_facts(facts, DUR["share_issuance"], ISSUANCE_SUPERSETS, money=money))
    extra.update({k: quarterly_by_tag(facts, DUR[k], derive=False, direct_window=DPS_DIRECT_WINDOW, fy_starts=fy_starts, money=money) for k in QUARTERLY_DPS_FIELDS})
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
# Dividends block (5.4.1; 5.4.2 / 5.4.3 / 5.4.4 / 5.4.5 review fixes). Pure functions first — tested
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
    g = statistics.median_low([_days(a, b) for a, b in zip(ends, ends[1:])])  # low median: a run with one hole still reads as its usual gap
    if g <= 130:
        return "quarterly"
    if g <= 240:
        return "semiannual"
    if g <= 400:
        return "annual"
    return "irregular"


def fy_remainder_is_a_payment(fy_dps, sum_quarterly_in_fy, min_quarterly=None):
    """True when the FY DPS total exceeds the sum of the quarterly facts inside
    that fiscal year by enough to be a payment the quarterly facts do not carry.
    5.4.6 review fix (IRM: quarterly facts 0.785 ×3 + 0.864 = 3.219 against the
    rounded FY fact 3.22 — the 0.001 is rounding, not a fifth payment): the
    remainder must be at least half the smallest positive quarterly fact of the
    year (any positive remainder when no quarterly fact is given)."""
    if not (_num(fy_dps) and _num(sum_quarterly_in_fy)):
        return False
    rem = fy_dps - sum_quarterly_in_fy
    floor = 0.5 * min_quarterly if _num(min_quarterly) and min_quarterly > 0 else 0.0
    return rem > 1e-9 and rem >= floor


def infer_frequency(n_quarterly_in_fy, fy_dps, sum_quarterly_in_fy, any_quarterly_facts, any_facts, dividends_paid=False, min_quarterly=None):
    """Payment frequency from how many DPS facts fall inside the latest
    fiscal year (the fallback when the FY total carries a payment the
    quarterly facts do not — the 10-K files the year, not the Q4). None (not
    inferable) when the filer files only full-year DPS facts (20-F). A filer
    with no per-share facts at all is "none" only when it also pays no cash
    dividends; with `dividends_paid` the rate is simply not tagged → None.
    `min_quarterly` (the smallest positive quarterly fact of the year) sets the
    rounding floor of fy_remainder_is_a_payment."""
    if not any_facts:
        return None if dividends_paid else "none"
    if not any_quarterly_facts:
        return None
    n = n_quarterly_in_fy
    if fy_remainder_is_a_payment(fy_dps, sum_quarterly_in_fy, min_quarterly):
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


def dps_cagr_window(annual, years):
    """(cagr, reason). CAGR of annual DPS between the latest row and the row
    whose period end is `years` years earlier (±45 days, so 52/53-week drift
    is fine). The window must be an unbroken run of consecutive fiscal years
    (one fiscal year apart by period end) each with a DPS > 0: a year with no
    annual DPS row (dividend suspended, or simply not filed) or a filed zero
    inside the window makes the figure null and `reason` names the gap —
    EXPE's FY2020 0.34 → FY2025 1.60 is a suspension and a reinstatement, not
    36%/yr of growth (5.4.3 review fix). reason is None when the CAGR is
    computed, and names the missing endpoint otherwise."""
    rows = _dps_rows(annual)
    if len(rows) < 2:
        return None, "fewer than two annual DPS rows"
    last = rows[-1]
    target = datetime.date.fromisoformat(last["period_end"]) - datetime.timedelta(days=round(years * 365.25))
    base = min(rows[:-1], key=lambda r: abs((datetime.date.fromisoformat(r["period_end"]) - target).days))
    if abs((datetime.date.fromisoformat(base["period_end"]) - target).days) > 45:
        return None, f"no annual DPS row {years} years before FY{last['fy']} (period ended {last['period_end']})"
    window = [r for r in rows if base["period_end"] <= r["period_end"] <= last["period_end"]]
    label = f"the {years}-year window FY{base['fy']}→FY{last['fy']}"
    for prev, cur in zip(window, window[1:]):
        if not fy_consecutive(prev["period_end"], cur["period_end"]):
            return None, (f"{label} has no annual DPS between FY{prev['fy']} (period ended {prev['period_end']}) and FY{cur['fy']} "
                          f"(period ended {cur['period_end']}) — a dividend suspension or unfiled years, not a growth path")
    zeros = [r for r in window if not r["dps"] > 0]
    if zeros:
        return None, f"{label} contains a fiscal year with no dividend ({', '.join('FY' + r['fy'] for r in zeros)}: DPS {zeros[0]['dps']:g}) — a suspension, not a growth path"
    a, b = base["dps"], last["dps"]
    return (b / a) ** (1.0 / years) - 1, None


def dps_cagr(annual, years):
    """CAGR of annual DPS over an unbroken `years`-year window (see dps_cagr_window); None otherwise."""
    return dps_cagr_window(annual, years)[0]


def dps_outliers(annual):
    """Labels of rows whose annual DPS is more than 10x both neighbours (a unit
    slip in the filed XBRL, e.g. cents tagged as dollars). Reported, never altered.
    5.4.5 review fix (CCI FY2014 1870 against FY2015 3.35, FY2016 3.61): the
    first and the last positive rows are compared with their single neighbour
    when that neighbour is itself corroborated by the next row (within 3x), at
    EDGE_OUTLIER_FACTOR (100x: a cents / thousands slip) — one-sided, a real
    cut can be 10x-plus (HBAN FY2008 0.6625 → FY2009 0.04 is 16.6x). With only
    two rows there is no telling which one is off."""
    rows = [r for r in annual if _num(r.get("dps")) and r["dps"] > 0]
    out = []
    for i in range(len(rows)):
        b = rows[i]["dps"]
        if 0 < i < len(rows) - 1:
            if b > 10 * rows[i - 1]["dps"] and b > 10 * rows[i + 1]["dps"]:
                out.append(rows[i]["fy"])
        elif len(rows) >= 3:
            n1, n2 = (rows[1]["dps"], rows[2]["dps"]) if i == 0 else (rows[-2]["dps"], rows[-3]["dps"])
            if b > EDGE_OUTLIER_FACTOR * n1 and max(n1, n2) <= 3 * min(n1, n2):
                out.append(rows[i]["fy"])
    return out


EDGE_OUTLIER_FACTOR = 100


def basis_breaks(annual, shares_by_end, eps_by_end=None, rejected=None):
    """Fiscal years where annual DPS moved ~1/k while the diluted share count
    moved ~k (k ≥ 1.4): a share-basis change (an unfiled split) — never a
    cut. Returns [(period_end, dps_ratio, share_ratio)] ascending.
    5.4.3 review fix (false positives on real share moves): a split restates
    the prior year's diluted EPS by the same factor, a share issuance with a
    coincident dividend cut does not — so when both years' diluted EPS are
    filed and positive, the EPS move must also be ~1/k (EPS ratio × share
    ratio within 0.6–1.6; earnings move year to year, hence the wider band).
    A candidate the EPS contradicts is appended to `rejected` as
    (period_end, dps_ratio, share_ratio, eps_ratio) and stays a cut."""
    rows = _dps_rows(annual)
    eps_by_end = eps_by_end or {}
    out = []
    for prev, cur in zip(rows, rows[1:]):
        if not fy_consecutive(prev["period_end"], cur["period_end"]):
            continue
        s0, s1 = shares_by_end.get(prev["period_end"]), shares_by_end.get(cur["period_end"])
        if not (_num(s0) and _num(s1) and s0 > 0 and s1 > 0 and prev["dps"] > 0 and cur["dps"] > 0):
            continue
        rs, rd = s1 / s0, cur["dps"] / prev["dps"]
        if (rs >= 1.4 or rs <= 1 / 1.4) and 0.8 <= rs * rd <= 1.25:
            e0, e1 = eps_by_end.get(prev["period_end"]), eps_by_end.get(cur["period_end"])
            if _num(e0) and _num(e1) and e0 > 0 and e1 > 0:
                re = e1 / e0
                if not 0.6 <= rs * re <= 1.6:
                    if rejected is not None:
                        rejected.append((cur["period_end"], rd, rs, re))
                    continue
            out.append((cur["period_end"], rd, rs))
    return out


def payout_ratio(numerator, denominator):
    """numerator / denominator, None unless both are numbers, the denominator is
    > 0 and the numerator is ≥ 0 (a payment filed below zero is a sign error the
    caller corrects first — never a negative payout)."""
    if not _num(numerator) or not _num(denominator) or denominator <= 0 or numerator < 0:
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
SPLIT_DUPLICATE_DAYS = 180   # one split is tagged at several context dates (approval, record date, distribution, fiscal year end)
SPLIT_RATIO_TOL = 1.1        # a re-filed value within 10% of the ratio is the split's restatement
SHARE_REFILE_MIN = 1.4       # a diluted share count re-filed ≥1.4x apart is a basis change, not rounding
SHARE_SCALE_BAND = 10        # Q8: a fallback count more than 10x from the engine's validated diluted count is a scale break
SHARE_ANCHOR_TOL = 1.2       # Q8 round 2: a fallback count more than 20% from the engine's validated count gives way to a filed count within 20% of it (ECHO)


def split_events(facts, duplicates=None):
    """[(effective_date, ratio)] from StockholdersEquityNoteStockSplitConversionRatio1
    facts on any form; ratio = new shares per old share as filed (2 for a
    2-for-1 split, 0.6667 for a 2-for-3 reverse split). A filer tags ONE split
    at several context dates — the board approval, the record date, the
    distribution, the fiscal year end (TSCO's 5-for-1 sits at 2024-12-05,
    2024-12-20 and 2024-12-28; NVDA's 4-for-1 at 2021-06-03 and 2021-07-19,
    its 10-for-1 at 2024-05-31 and 2024-06-30) — so facts with the same ratio
    within SPLIT_DUPLICATE_DAYS of the event's first date are ONE event at
    that first date (5.4.4 blocker fix: before this each date compounded and
    TSCO's pre-split DPS was divided by 125 instead of 5). `duplicates`
    (optional list) receives (date, ratio, [folded dates])."""
    seen = {}
    for taxonomy, tag in _pairs(DUR["split_ratio"]):
        tf = facts.get("facts", {}).get(taxonomy, {}).get(tag)
        if not tf:
            continue
        for unit_key, es in tf.get("units", {}).items():
            for e in es:
                d, v = e.get("end"), e.get("val")
                if d and _num(v) and v > 0 and v != 1 and d not in seen:
                    seen[d] = v
    groups = []
    for d, v in sorted(seen.items()):
        if groups and groups[-1][1] == v and _days(groups[-1][0], d) <= SPLIT_DUPLICATE_DAYS:
            groups[-1][2].append(d)
            continue
        groups.append([d, v, []])
    if duplicates is not None:
        duplicates.extend((d, v, folded) for d, v, folded in groups if folded)
    return [(d, v) for d, v, _ in groups]


def split_direction(splits, shares_with_filed, dropped=None):
    """Check each filed ratio against the filed diluted share counts: the
    last fiscal year filed BEFORE the split vs the first filed AFTER it. The
    us-gaap element does not fix which way the ratio reads, so when the counts
    move by ~1/ratio instead of ~ratio (a 1-for-10 reverse split filed as 10)
    the inverse is used. Returns [(date, ratio_filed, ratio_used, evidence)].
    5.4.4: two events that rest on the SAME pair of filed counts are one split
    when their compounded ratio overshoots the observed move by more than
    1.5x — the later one is a duplicate ratio fact (tagged again months later),
    not a second split; it is left out and `dropped` (optional list) receives
    (date, ratio, evidence)."""
    out = []
    for d, r in splits:
        pre = [(e, v) for e, (v, f) in shares_with_filed.items() if f and f < d and _num(v) and v > 0]
        post = [(e, v) for e, (v, f) in shares_with_filed.items() if f and f >= d and _num(v) and v > 0]
        used, ev, obs, pair = r, None, None, None
        if pre:
            post = [(e, v) for e, v in post if e > max(pre)[0]]
        if pre and post:
            e0, s0 = max(pre)
            e1, s1 = min(post)
            obs, pair = s1 / s0, (e0, e1)
            ev = f"diluted shares {s0:,.0f} (FY ending {e0}) → {s1:,.0f} (FY ending {e1}), ×{obs:.2f}"
            # 5.4.6: one of the two counts filed in thousands, the other in
            # shares (WRB 2019: 193,527 vs 129,017,613) — the move is read
            # after taking out the factor of 1,000
            k3 = round(-math.log10(obs) / 3) if obs > 0 else 0
            if k3 and abs(math.log10(obs)) >= 2.5:
                obs = obs * 1000.0 ** k3
                ev += f" — one count is filed in thousands, ×{obs:.2f} once the factor of 1,000 is taken out"
            if abs(math.log(obs)) > math.log(1.25) and abs(math.log(obs) - math.log(1 / r)) < abs(math.log(obs) - math.log(r)):
                used = 1 / r
                sn = snap_ratio(used, tol=0.001)  # a ratio filed rounded (0.6667) inverts to 1.49993: the split is 3-for-2
                used = sn[0] if sn else used
        out.append((d, r, used, ev, obs, pair))
    kept, product = [], {}
    for d, r, used, ev, obs, pair in out:
        if pair is not None and abs(math.log(obs)) > math.log(1.25):
            prod = product.get(pair, 1.0) * used
            if abs(math.log(prod)) > abs(math.log(obs)) + math.log(1.5):
                if dropped is not None:
                    dropped.append((d, r, f"{ev}; compounding it with the split already read from the same counts would give ×{prod:.2f}"))
                continue
            product[pair] = prod
        kept.append((d, r, used, ev))
    return kept


def share_refilings(facts):
    """Periods whose diluted weighted-average share count was re-filed at a
    different value — the comparatives a filer restates after a split:
    [(period_end, k, last_filed_old, first_filed_new)] ascending by the
    re-filing date, k = new / old (|log k| ≥ log 1.4). Every filing of every
    period on 10-Q / 10-K forms is read, not just the latest."""
    by_period = {}
    for taxonomy, tag in _pairs(DUR["shares_diluted"]):
        tf = facts.get("facts", {}).get(taxonomy, {}).get(tag)
        if not tf:
            continue
        for unit_key, es in tf.get("units", {}).items():
            if unit_key != "shares":
                continue
            for e in es:
                if e.get("form", "") not in DURATION_FORMS or not e.get("start") or not e.get("end") or not e.get("filed"):
                    continue
                if not _num(e.get("val")) or e["val"] <= 0:
                    continue
                by_period.setdefault((e["start"], e["end"]), []).append((e["filed"], e["val"]))
    out = []
    for (s, e), fv in by_period.items():
        fv.sort()
        old_filed, old_val = fv[0]
        for filed, val in fv[1:]:
            k = val / old_val
            if abs(math.log(k)) >= math.log(SHARE_REFILE_MIN):
                out.append((e, k, old_filed, filed))
            old_filed, old_val = filed, val
    return sorted(out, key=lambda x: (x[3], x[0]))


def split_filing_cutoffs(splits, refilings):
    """{split_date: (first_post_split_filing, evidence)}. A ratio fact's
    context date is the approval / record date, not the day the filer's
    numbers changed basis: CTAS tagged 4 at 2024-05-02 and its 10-K filed
    2024-07-25 still carried pre-split comparatives; KR tagged 2 at 2015-06-25
    and the 10-Q filed 2015-06-30 was pre-split. The filings themselves say
    when the basis changed — the first filing that re-files a period's diluted
    share count ×≈ratio (share_refilings) within −200..+400 days of the ratio
    date. splits: [(date, ratio_used)]."""
    out = {}
    for d, used in splits:
        cands = []
        for e, k, old_filed, new_filed in refilings:
            if abs(math.log(k) - math.log(used)) <= math.log(SPLIT_RATIO_TOL) and -200 <= _days(d, new_filed) <= 400:
                cands.append((new_filed, e, k, old_filed))
        if cands:
            new_filed, e, k, old_filed = min(cands)
            out[d] = (new_filed, f"the diluted share count for the period ended {e} was re-filed ×{k:.2f} on {new_filed} (last filed on the old basis {old_filed})")
    return out


def _split_cutoff(s):
    """(date, ratio, cutoff) for a split tuple of two or three elements — the
    cutoff is the first filing on the post-split basis, the date itself when
    the filings gave no evidence."""
    d, r = s[0], s[1]
    return d, r, (s[2] if len(s) > 2 and s[2] else d)


def split_factor(filed, splits):
    """Product of the ratios of every split whose first post-split filing
    (the split's date when the filings carry no evidence) is after `filed`,
    the date the fact was last filed. A fact filed before that is on the
    pre-split share basis; dividing its per-share value by this factor
    restates it to today's basis — plain arithmetic on two filed values.
    splits: [(date, ratio)] or [(date, ratio, first_post_split_filing)]."""
    f = 1.0
    for s in splits:
        d, r, cutoff = _split_cutoff(s)
        if filed and filed < cutoff:
            f *= r
    return f


def snap_ratio(x, tol=0.01, max_n=10):
    """(p/q, (p, q)) — the simplest ratio of two whole numbers ≤ max_n within
    `tol` (1%) of x, else None. A split is p-for-q in whole shares; a ratio read
    off two rounded per-share values (WRB: 0.89 / 0.59 = 1.50847) is that split
    plus rounding (5.4.6 review fix)."""
    if not _num(x) or x <= 0:
        return None
    for q in range(1, max_n + 1):
        p = round(x * q)
        if 1 <= p <= max_n and abs(p / q / x - 1) <= tol:
            return p / q, (p, q)
    return None


def _split_desc(d, r, cutoff=None):
    desc = f"{r:g}-for-1 split effective {d}" if r >= 1 else f"1-for-{1 / r:g} reverse split effective {d}"
    return desc + (f" (first filed on the new basis {cutoff})" if cutoff and cutoff != d else "")


def apply_splits(dps_q, dps_fy, fy_filed, splits):
    """Restate every DPS fact whose latest filing precedes a split's first
    post-split filing. dps_q: {basis: {end: {val, filed, ...}}} (quarterly
    dicts get 'split_factor'); dps_fy: {basis: {end: dps}}; fy_filed: {basis:
    {end: filed}}; splits: [(date, ratio[, first_post_split_filing])].
    Returns (dps_q, dps_fy, notes)."""
    notes = []
    splits = [s for s in (splits or []) if _num(s[1]) and s[1] > 0 and s[1] != 1]
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
    desc = "; ".join(_split_desc(*_split_cutoff(s)) + (" (no ratio fact: the factor the filer re-filed its FY DPS and diluted share counts by)" if len(s) > 3 and s[3] == "re_filed_counts" else "")
                     for s in splits)
    src = ("the filed ratio (StockholdersEquityNoteStockSplitConversionRatio1)" if all(not (len(s) > 3 and s[3] == "re_filed_counts") for s in splits)
           else "the split ratio (filed, or evidenced by the re-filed values)")
    for basis, ends in touched.items():
        ends = sorted(set(ends))
        notes.append(f"split adjustment ({basis} DPS): {len(ends)} facts for periods ending {ends[0]}..{ends[-1]} were last filed before the {desc} and are divided by {src} to today's share basis")
    return dps_q, dps_fy, notes


# Ruling-sheet Q8 bug 2 (Andrew, 2026-10-19), multi-class filers: companyfacts
# keeps a cover-page dei count only when it is undimensioned, which at a filer
# with two listed classes can be ONE class (GGB: 717,782,619 common shares)
# while the same 20-F files the all-class count (IFRS
# NumberOfSharesIssuedAndFullyPaid 2,000,879,949). Per-share figures divided by
# the one class overstated book value per share ~2.8x and understated the
# market cap ~2.8x. The all-class counts read: an outstanding count, or an
# IFRS issued count, each less the treasury shares the same filing files at
# that date — EG tags its ISSUED count (74.5M) as CommonStockSharesOutstanding
# beside 35.8M treasury shares and a 38.3M cover count, which is therefore not
# a class count (us-gaap issued counts are not read: a treasury-heavy US
# filer's issued count is far above its outstanding shares — IBM ~2.4x).
ALL_CLASS_OUTSTANDING_TAGS = [("us-gaap", "CommonStockSharesOutstanding"), (IF, "NumberOfSharesOutstanding")]
ALL_CLASS_ISSUED_TAGS = [(IF, "NumberOfSharesIssuedAndFullyPaid"), (IF, "NumberOfSharesIssued")]
TREASURY_SHARE_TAGS = [(IF, "SharesInEntityHeldByEntityOrByItsSubsidiariesOrAssociates"), ("us-gaap", "TreasuryStockShares"),
                       ("us-gaap", "TreasuryStockCommonShares")]


def _instant_share_facts(facts, pairs, accn):
    """[(end, val, tag)] — undimensioned instant share facts of `pairs` filed in the filing `accn`."""
    out = []
    for taxonomy, tag in pairs:
        for e in ((facts.get("facts", {}).get(taxonomy, {}).get(tag) or {}).get("units") or {}).get("shares", []):
            if e.get("accn") != accn or not e.get("end") or (e.get("start") and e["start"] != e["end"]):
                continue
            if _num(e.get("val")) and e["val"] > 0:
                out.append((e["end"], e["val"], f"{taxonomy}:{tag}"))
    return out


def all_class_count(facts, accn):
    """(count, end, source) — the largest all-class period-end share count the
    filing `accn` files at its latest balance-sheet date (ALL_CLASS_OUTSTANDING_TAGS
    or ALL_CLASS_ISSUED_TAGS, less that filing's treasury shares at the same
    date when it files them), else None."""
    if not accn:
        return None
    outs = _instant_share_facts(facts, ALL_CLASS_OUTSTANDING_TAGS, accn)
    issued = _instant_share_facts(facts, ALL_CLASS_ISSUED_TAGS, accn)
    if not outs and not issued:
        return None
    end = max(x[0] for x in outs + issued)
    treasury = {x[0]: x[1] for x in _instant_share_facts(facts, TREASURY_SHARE_TAGS, accn)}
    cands = [(v - treasury.get(end, 0), src + (f" less {treasury[end]:,.0f} treasury shares" if end in treasury else "")) for e, v, src in outs + issued if e == end]
    cands = [c for c in cands if c[0] > 0]
    if not cands:
        return None
    v, src = max(cands, key=lambda c: c[0])
    return v, end, src


def class_count_check(count, facts, accn):
    """When a cover-page dei count is below 1/SHARE_REFILE_MIN (1/1.4) of the
    same filing's all-class count it is one class of a multi-class filer:
    (all-class count, end, source, note); else None."""
    ac = all_class_count(facts, accn)
    if ac is None or not _num(count) or count <= 0 or ac[0] < SHARE_REFILE_MIN * count:
        return None
    note = (f"the cover-page dei:EntityCommonStockSharesOutstanding count {count:,.0f} does not cover the filing's share base — the same filing's "
            f"all-class count {ac[0]:,.0f} ({ac[2]}, {ac[1]}) is {ac[0] / count:.2f}x it (one class of a multi-class filer, or a stale cover "
            f"figure) — so the all-class count is used")
    return ac[0], ac[1], ac[2], note


def latest_share_count(facts):
    """(count, as_of, source) — the latest filed instant share count: the
    cover-page dei:EntityCommonStockSharesOutstanding, else the balance
    sheet's CommonStockSharesOutstanding / IFRS NumberOfSharesOutstanding.
    The latest date wins; on the same date the dei count, then the latest filing.
    A dei count that is one class of a multi-class filer (class_count_check)
    gives way to the same filing's all-class count, named in the source."""
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
    if src == "dei:EntityCommonStockSharesOutstanding":
        chk = class_count_check(e["val"], facts, e.get("accn"))
        if chk is not None:
            return chk[0], chk[1], f"{chk[2]} ({e.get('form')} filed {e.get('filed')}; {chk[3]})"
    return e["val"], e["end"], f"{src} ({e.get('form')} filed {e.get('filed')})"


PRICES_JSON_SOURCE = "prices.json stats.last"  # dividends.price_source of a close read from prices.json (build_site.py reprices with it too)


def _read_price(folder, prev_dividends=None):
    """(price, date, source) from prices.json stats.last; else the close the
    committed fundamentals.json already used (prev_dividends = its dividends
    block), carried with its own date and source, unless score.json's
    analysis price is dated later; else score.json price.

    prices.json is a gitignored cache that a fresh clone does not have, and
    refresh.py --sec runs this script before prices.py: falling straight back
    to score.json's analysis-time price there replaced a newer close and
    rewrote every priced name's committed file (verifier, PR #2 repair round:
    Q 121.62 'prices.json stats.last' -> 121.8685 'score.json price'). A price
    that came from score.json is never carried; score.json is read afresh.
    A split since the scored run (live.json split_factor != 1, from
    reprice.py) puts prices.json's close in post-split units while the filed
    DPS and share counts stay pre-split until the company files again; that
    close is then skipped (build_site does not reprice across a split
    either), so the yields are never doubled or halved by mixed units.
    """
    try:
        with open(f"{folder}/live.json", encoding="utf-8") as f:
            sf = json.load(f).get("split_factor")
        split_since_scoring = bool(_num(sf) and sf > 0 and abs(sf - 1.0) > 1e-9)
    except Exception:
        split_since_scoring = False
    try:
        if split_since_scoring:
            raise ValueError("split since scoring: prices.json is in post-split units")
        with open(f"{folder}/prices.json", encoding="utf-8") as f:
            p = json.load(f)
        st = p.get("stats") or {}
        if _num(st.get("last")):
            return st["last"], st.get("last_date"), PRICES_JSON_SOURCE
    except Exception:
        pass
    score = None
    try:
        with open(f"{folder}/score.json", encoding="utf-8") as f:
            s = json.load(f)
        if _num(s.get("price")):
            score = (s["price"], s.get("analysis_date"), "score.json price")
    except Exception:
        pass
    pv = prev_dividends if isinstance(prev_dividends, dict) else {}
    carried = None
    if (_num(pv.get("price")) and pv["price"] > 0 and isinstance(pv.get("price_date"), str) and pv.get("price_date")
            and isinstance(pv.get("price_source"), str) and "score.json" not in pv["price_source"]):
        carried = (pv["price"], pv["price_date"], pv["price_source"])
    if carried and not (score and isinstance(score[1], str) and score[1] > carried[1]):
        return carried
    return score or (None, None, None)


def _fmt_big(v):
    if not _num(v):
        return "—"
    a = abs(v)
    if a >= 1e9:
        return f"{v / 1e9:.2f}B"
    if a >= 1e6:
        return f"{v / 1e6:.1f}M"
    return f"{v:,.0f}"


def ytd_cover(last4, flow_facts):
    """(value, [covered quarter ends], description) — the longest filed
    year-to-date fact that spans whole quarters INSIDE the four-quarter
    window: its end is a window quarter's end, its length is that quarter's
    fiscal rank (fq 2 → a six-month fact, fq 3 → nine months, fq 4 → the
    fiscal year), and the quarters it spans (the fiscal year's first through
    that quarter) are all window rows. flow_facts: duration_facts output
    {(start, end): (val, tag, unit, filed, accn)}. None when no such fact
    exists (a one-quarter fact adds nothing the row does not carry).
    5.4.5: a fourth element is the fact's (start, end) key, so the caller can
    tell whether the fact it used was filed with a flipped sign."""
    if not last4 or not flow_facts:
        return None
    best = None
    for i, row in enumerate(last4):
        n = row.get("fq")
        if not _num(n) or n < 2 or i - n + 1 < 0:
            continue
        span = last4[i - n + 1:i + 1]
        if any(_num(r.get("fq")) and r["fq"] != j + 1 for j, r in enumerate(span)):
            continue
        for (s, e), fact in flow_facts.items():
            if e != row["period_end"] or not _num(fact[0]):
                continue
            d = _days(s, e)
            if round(d / 91.25) != n or abs(d - n * 91.25) > 35:
                continue
            if best is None or n > best[0]:
                label = {2: "six-month", 3: "nine-month", 4: "full-year"}[n]
                best = (n, fact[0], [r["period_end"] for r in span],
                        f"the {label} year-to-date fact {s}..{e} = {_fmt_big(fact[0])} ({fact[1]}, filed {fact[3]})", (s, e))
    return best[1:] if best else None


# ---- 5.4.5 / 5.4.6 review fixes: primary DPS basis, flow-leg signs, cash payer status
BASIS_WINDOW_QUARTERS = 8   # "files quarterly facts" = a quarterly fact in the latest eight quarters (ending at the newest fact of either tag)
BASIS_STOP_DAYS = 330       # a tag whose newest fact is this much older than the other tag's newest has stopped (≈ four quarters)


def choose_dps_basis(dps_q, dps_fy):
    """(basis, rule) — the PRIMARY per-share basis. 5.4.6 review fix: the 5.4.5
    rule (coverage of the last eight quarter slots, an FY fact covering every
    slot of its year) was seasonal for a tag that files only full-year facts —
    each 10-K gave that tag four new slots and each later 10-Q took them away
    (ZTS: CashPaid FY-only, Declared Q1-Q3; ATO), and one newer fact could move
    the slot difference by two (the window slides). The rule now reads only
    things that do not change between a 10-K and the next 10-Q:
    1. a tag whose newest fact is ≥ BASIS_STOP_DAYS older than the other tag's
       newest has stopped — the other tag is primary (AVGO: declared ends FY2020);
    2. otherwise a tag with quarterly facts in the latest eight quarters beats
       a tag with only full-year facts there (the quarterly tag gives the TTM and
       the cadence; ZTS → declared, a CashPaid Q1-Q3 + FY filer with a
       declared FY-only tag → paid);
    3. otherwise declared.
    Once a filer's tagging pattern is set, the answer is the same at every
    filing date. rule is None when only one tag (or none) is filed."""
    ends = {b: ([e for e, d in (dps_q.get(b) or {}).items() if _num(d.get("val"))],
                [p for p, v in (dps_fy.get(b) or {}).items() if _num(v)]) for b in ("declared", "paid")}
    has = {b: bool(ends[b][0] or ends[b][1]) for b in ends}
    if not (has["declared"] and has["paid"]):
        return ("declared" if has["declared"] else ("paid" if has["paid"] else None)), None
    newest = {b: max(ends[b][0] + ends[b][1]) for b in ends}
    anchor = max(newest.values())
    floor = _add_days(anchor, -round(BASIS_WINDOW_QUARTERS * 91.31))
    quarterly = {b: any(e > floor for e in ends[b][0]) for b in ends}
    lag = _days(newest["declared"], newest["paid"])  # > 0: declared's newest fact is older
    n = BASIS_WINDOW_QUARTERS
    if lag >= BASIS_STOP_DAYS:
        return "paid", (f"the declared tag stopped: its newest fact ({newest['declared']}) is {lag} days older than the paid tag's ({newest['paid']}) — paid is primary")
    if -lag >= BASIS_STOP_DAYS:
        return "declared", (f"the paid tag stopped: its newest fact ({newest['paid']}) is {-lag} days older than the declared tag's ({newest['declared']}) — declared is primary")
    if quarterly["declared"] != quarterly["paid"]:
        b = "declared" if quarterly["declared"] else "paid"
        o = "paid" if b == "declared" else "declared"
        return b, (f"the {b} tag files quarterly facts in the last {n} quarters ending {anchor}, the {o} tag only full-year facts — the quarterly tag is primary "
                   f"(the {o} tag's full-year facts fill only fiscal years the {b} tag does not cover)")
    kind = "quarterly" if quarterly["declared"] else "only full-year"
    return "declared", (f"both tags file {kind} facts in the last {n} quarters ending {anchor} and neither has stopped — declared is primary "
                        f"(paid becomes primary only when the declared tag has had no fact for {BASIS_STOP_DAYS} days while paid continues)")


def _flow_quarter_from_facts(end, ff):
    """(value, used) — one fiscal quarter of a flow line rebuilt from the filed
    facts ending at `end`, every fact taken as an absolute amount: a direct
    three-month fact, else the year-to-date fact minus the one a quarter shorter
    with the same start. used: [(start, end, value as filed)]; (None, []) when
    the facts do not support the quarter."""
    direct = [k for k in ff if k[1] == end and DPS_DIRECT_WINDOW[0] <= _days(k[0], k[1]) <= DPS_DIRECT_WINDOW[1] and _num(ff[k][0])]
    if direct:
        k = max(direct, key=lambda x: ff[x][3] or "")
        return abs(ff[k][0]), [(k[0], k[1], ff[k][0])]
    for (s, e), fact in sorted(ff.items()):
        if e != end or not _num(fact[0]):
            continue
        d = _days(s, e)
        n = round(d / 91.25)
        if not 2 <= n <= 4 or abs(d - n * 91.25) > 35:
            continue
        for (s2, e2), f2 in sorted(ff.items()):
            d2 = _days(s2, e2)
            if s2 == s and _num(f2[0]) and round(d2 / 91.25) == n - 1 and abs(d2 - (n - 1) * 91.25) <= 35:
                return abs(fact[0]) - abs(f2[0]), [(s, e, fact[0]), (s2, e2, f2[0])]
    return None, []


COMMON_DIVIDEND_TAGS = {"PaymentsOfDividendsCommonStock", "PaymentsOfOrdinaryDividends", "DividendsPaidToEquityHoldersOfParentClassifiedAsFinancingActivities"}
# the kinds of a flow-leg sign entry (sign_fixed_flows): only SIGN_ABS changes a
# filed sign; SIGN_KEPT is a negative issuance line kept as filed; the
# SIGN_LEFT_OUT kinds are quarters no consistent figure exists for
SIGN_ABS, SIGN_KEPT, SIGN_LEFT_OUT_SIGN, SIGN_LEFT_OUT_DECREASE = "abs", "kept", "left_out_sign", "left_out_decrease"


def _sign_error(k, key, ff):
    """Is the fact `key` of flow `k`, filed below zero, a sign-convention error?
    Dividends paid and repurchases are payments — always. Issuance proceeds can
    be a net line (net of offering costs, or stock-award proceeds net of the tax
    withheld — IRM's ProceedsFromStockPlans −4.8M / −8.8M, LRCX's −43,000), so
    for share_issuance only when the same fiscal year's other filed facts (the
    same start date) carry the opposite sign — CCI's pattern of an FY fact below
    zero beside positive year-to-date facts (5.4.6 review fix)."""
    if k != "share_issuance":
        return True
    s = key[0]
    return any(k2 != key and k2[0] == s and _num(f2[0]) and f2[0] > 0 for k2, f2 in (ff or {}).items())


def signed_flow_facts(k, ff):
    """(facts, flipped keys): the flow facts with every sign-convention error
    (_sign_error) read as its absolute amount; a consistently negative
    issuance fact stays as filed."""
    out, flipped = {}, []
    for key, f in (ff or {}).items():
        if _num(f[0]) and f[0] < 0 and _sign_error(k, key, ff):
            out[key] = (abs(f[0]),) + tuple(f[1:])
            flipped.append(key)
        else:
            out[key] = f
    return out, flipped


_NET_LINE = ("issuance proceeds can be a net line (net of offering costs, or stock-award proceeds net of the tax withheld) "
             "and no other fact of that fiscal year carries the opposite sign")


def sign_fixed_flows(annual, qrows, flow_facts=None):
    """Dividends paid and repurchases are cash payments, non-negative by
    definition; a value filed below zero is a sign-convention error in the
    filing, not a negative payment (5.4.5 review blocker: CCI's FY2025 10-K tags
    PaymentsOfDividendsCommonStock −2,080,000,000 and
    PaymentsForRepurchaseOfCommonStock −23,000,000 while every 10-Q year-to-date
    fact is positive, so the quarterly table's Q4 = FY − nine months read
    −3,695,000,000 and −46,000,000). Issuance proceeds below zero are a sign
    error only when the same fiscal year's other facts carry the opposite sign
    (_sign_error); otherwise a net issuance line is kept as filed (5.4.6).
    Returns (qv, av, fixes):
    qv {flow: {quarter end: value}} — the row value, or, when the row is below
    zero or was built from a fact that is a sign error, the quarter rebuilt from
    the facts read as absolute amounts (|FY| − |nine months| = 2,080M − 1,615M =
    465M); None when no consistent figure exists (left out, a missing quarter);
    av {flow: {FY period end: value}} — the annual value, sign errors absolute;
    fixes {flow: [(key, text, kind)]} — key is the quarter end, or "FY:<period
    end>" for an annual row; kind SIGN_ABS (read as the absolute amount),
    SIGN_KEPT (a negative issuance line kept as filed), SIGN_LEFT_OUT_SIGN
    (facts of opposite signs, no consistent figure) or SIGN_LEFT_OUT_DECREASE
    (every fact positive but the year-to-date total decreases: no quarter can
    be derived — 5.4.6 review fix, DHI / CMPS: this is not a sign error)."""
    flow_facts = flow_facts or {}
    qv, av, fixes = {k: {} for k in FLOW_KEYS}, {k: {} for k in FLOW_KEYS}, {k: [] for k in FLOW_KEYS}
    for r in annual or []:
        pe = r.get("period_end")
        for k in FLOW_KEYS:
            v = r.get(k)
            if not (_num(v) and v < 0):
                av[k][pe] = v
                continue
            ff = flow_facts.get(k) or {}
            fy_key = next((key for key in ff if key[1] == pe and 330 <= _days(key[0], key[1]) <= 380), None)
            if k != "share_issuance" or (fy_key and _sign_error(k, fy_key, ff)):
                av[k][pe] = -v
                why = " while the same fiscal year's year-to-date facts are positive" if k == "share_issuance" else ""
                fixes[k].append(("FY:" + str(pe), f"FY{r.get('fy')} (period ended {pe}) filed as {_fmt_big(v)}, read as {_fmt_big(-v)}{why}", SIGN_ABS))
            else:
                av[k][pe] = v
                fixes[k].append(("FY:" + str(pe), f"FY{r.get('fy')} (period ended {pe}) filed as {_fmt_big(v)} and kept as filed — {_NET_LINE}", SIGN_KEPT))
    for r in qrows or []:
        e = r.get("period_end")
        for k in FLOW_KEYS:
            v = r.get(k)
            ff = flow_facts.get(k) or {}
            val, used = _flow_quarter_from_facts(e, ff) if ff else (None, [])
            neg = [x for x in used if _num(x[2]) and x[2] < 0]
            row_txt = f"the quarterly row read {_fmt_big(v)}" if _num(v) else "the quarterly row was empty"
            if not neg and not (_num(v) and v < 0):
                qv[k][e] = v
                continue
            facts_txt = " and ".join(f"{s}..{en} = {x:,.0f}" for s, en, x in used)
            if neg:
                if not any(_sign_error(k, (x[0], x[1]), ff) for x in neg):
                    raw = used[0][2] - (used[1][2] if len(used) == 2 else 0.0)
                    qv[k][e] = raw
                    fixes[k].append((e, f"quarter ended {e}: {facts_txt} filed below zero and kept as filed ({_fmt_big(raw)}) — {_NET_LINE}", SIGN_KEPT))
                elif _num(val) and val >= 0:
                    qv[k][e] = val
                    arith = (f"|{used[0][2]:,.0f}| − |{used[1][2]:,.0f}| = {val:,.0f}" if len(used) == 2 else f"|{used[0][2]:,.0f}| = {val:,.0f}")
                    fixes[k].append((e, f"quarter ended {e}: the filed facts {facts_txt} carry a sign below zero — {arith} used ({row_txt})", SIGN_ABS))
                else:
                    qv[k][e] = None
                    fixes[k].append((e, f"quarter ended {e}: {row_txt} from facts filed with opposite signs ({facts_txt}) and no consistent figure can be rebuilt — left out (a missing quarter)",
                                     SIGN_LEFT_OUT_SIGN))
            elif len(used) == 2:
                # every fact positive, the year-to-date total smaller than the one before it: no quarter, and no sign error either
                (s1, e1, x1), (s2, e2, x2) = used
                qv[k][e] = None
                fixes[k].append((e, f"quarter ended {e}: the year-to-date facts decrease ({s2}..{e2} = {x2:,.0f} > {s1}..{e1} = {x1:,.0f}) — no quarter can be derived from them "
                                    f"({row_txt}; typically a line tagged in one filing and not in the next); left out (a missing quarter)", SIGN_LEFT_OUT_DECREASE))
            elif not used and not r.get(f"{k}_derived"):
                if k == "share_issuance":
                    qv[k][e] = v
                    fixes[k].append((e, f"quarter ended {e}: filed as {_fmt_big(v)} and kept as filed — issuance proceeds can be a net line (net of offering costs or of the tax withheld on stock awards)", SIGN_KEPT))
                else:
                    qv[k][e] = -v
                    fixes[k].append((e, f"quarter ended {e}: filed as {_fmt_big(v)}, read as {_fmt_big(-v)}", SIGN_ABS))
            else:
                qv[k][e] = None
                fixes[k].append((e, f"quarter ended {e}: {row_txt}, derived from year-to-date facts that are not available to check — left out (a missing quarter)", SIGN_LEFT_OUT_SIGN))
    return qv, av, fixes


def build_dividends(annual, qrows, dps_q, dps_fy, price, price_date, price_source, ctx=None):
    """The `dividends` block. annual / qrows: build_annual / build_quarterly
    output; dps_q: {"declared": {end: {val, fq, fy_start, filed, ...}}, "paid":
    {...}} quarterly DPS facts (split-adjusted by dividends_inputs); dps_fy:
    {"declared": {period_end: dps}, "paid": {...}} FY-duration DPS facts.
    ctx (optional): filed_any {flow: bool — any fact in any period},
    flow_facts {flow: duration_facts output — the filed year-to-date legs},
    shares_instant (count, as_of, source), latest_filed_period {form: period}
    from the submissions feed, split_notes, splits, warnings (list to append
    to). Every figure is a filed value or arithmetic on filed values; anything
    else is None and `notes` says why. price / price_date / price_source go
    only to the closing price_dividends call, which sets every price leaf
    (PRICE_LEAVES) — the rest of the block is price-free."""
    ctx = ctx or {}
    notes = list(ctx.get("split_notes") or [])
    filed_any = ctx.get("filed_any") or {}
    # 5.4.4 blocker fix (AVGO): the basis is no longer one tag for the whole
    # history. The PRIMARY basis is the tag with the newest fact (declared on
    # a tie); the other tag extends the series only OUTSIDE the primary's
    # span — before its oldest or after its newest fact — never interleaved
    # inside it (a declared Q4 and a paid Q1 can be the same dividend). AVGO's
    # declared facts end FY2020 while CommonStockDividendsPerShareCashPaid runs
    # FY2016..FY2025 with quarters to 2026-08-02: primary = paid. Every history
    # row and annual row carries its `kind`.
    # 5.4.5 review fixes: (a) the primary basis is chosen by coverage of the
    # last eight quarters (choose_dps_basis), not by the single newest fact;
    # (b) the no-interleave rule applies to QUARTERLY facts only — a fiscal year
    # with no primary FY fact and no four primary quarterly facts takes the other
    # tag's FY fact (NVDA: declared FY facts skip FY2017-FY2021, CashPaid files
    # every one of them); (c) an FY fact below the sum of its own tag's quarterly
    # facts inside that fiscal year is impossible as a total and is not used
    # (NVDA's FY2016 declared fact is one quarter's rate tagged with the FY context).
    # 5.4.6 review fixes: (a) choose_dps_basis no longer slides with each filing
    # (stopped tag → the other; quarterly beats full-year-only; else declared);
    # (c) is narrowed — the quarterly facts can be the faulty ones (FTI's 10-K
    # re-tags Q1 2019 at 0.52, HPQ tags YTD values as quarters), so an FY fact
    # below its own quarters is set aside ONLY when the other tag files a
    # full-year total for that year that is consistent with those quarters
    # (NVDA FY2016: declared 0.115, CashPaid 0.395); otherwise it is kept as
    # filed and the note names the disagreement.
    def _ends(b):
        return [e for e, d in (dps_q.get(b) or {}).items() if _num(d.get("val"))] + [p for p, v in (dps_fy.get(b) or {}).items() if _num(v)]

    has = {b: bool(_ends(b)) for b in ("declared", "paid")}
    basis, basis_rule = choose_dps_basis(dps_q, dps_fy)
    secondary = {"declared": "paid", "paid": "declared"}.get(basis)
    q = {e: dict(d, kind=basis) for e, d in (dps_q.get(basis) or {}).items() if _num(d.get("val"))} if basis else {}
    fy_facts = {p: v for p, v in (dps_fy.get(basis) or {}).items() if _num(v)} if basis else {}
    fy_kind = {p: basis for p in fy_facts}

    def _fy_below_quarters(p, v, kind_):
        """(quarters, sum, confirmed) when the FY fact `v` (period ended p) is
        below 90% of the same tag's positive quarterly facts inside that fiscal
        year, else None; confirmed: every positive quarter is borne out by the
        tag's year-to-date facts (original_quarterly_dps' ytd_confirmed)."""
        qd = {e: d for e, d in (dps_q.get(kind_) or {}).items() if _num(d.get("val")) and 0 <= _days(e, p) < 350}
        qs = sorted((e, d["val"]) for e, d in qd.items())
        if any(_days(a[0], b[0]) < 45 for a, b in zip(qs, qs[1:])):
            return None  # two fiscal calendars inside one year (YUM: 2016-03-19 and 2016-03-31 quarters) — the sum double-counts, no comparison
        tot = sum(x for _, x in qs)
        positive = [x for _, x in qs if x > 0]
        confirmed = all(qd[e].get("ytd_confirmed") for e, x in qs if x > 0)
        # IBKR tags the quarterly rate in every context (quarters, 6M, 9M, FY all
        # 0.025): an FY fact equal to each of two or more positive quarterly facts
        # is one quarter's rate, not a total
        # — and only when at least two of those quarters were filed in their own
        # quarter's report (FTI's Q2 / Q3 2020 at 0.13, equal to its FY 0.13, exist
        # only as comparatives filed a year later: there the FY total is right)
        rate = (len(positive) >= 2 and all(abs(x - v) <= 1e-9 * max(1.0, abs(v)) for x in positive)
                and sum(1 for e, x in qs if x > 0 and _days(e, qd[e].get("first_filed") or qd[e].get("filed") or "9999-12-31") <= 150) >= 2)
        return (qs, tot, confirmed or rate) if tot > 0 and v < 0.9 * tot else None

    for p in sorted(fy_facts):
        bad = _fy_below_quarters(p, fy_facts[p], basis)
        if not bad:
            continue
        qtxt = f"{bad[1]:g}: {', '.join(f'{e}: {x:g}' for e, x in bad[0])}"
        other = next(((p2, v2) for p2, v2 in sorted((dps_fy.get(secondary) or {}).items()) if _num(v2) and abs(_days(p, p2)) <= 7), None) if secondary else None
        if other and other[1] >= 0.9 * bad[1]:
            notes.append(f"annual_dps: the {basis} FY DPS fact for the period ended {p} ({fy_facts[p]:g}) is below the sum of the same tag's quarterly facts inside that fiscal year "
                         f"({qtxt}) while the {secondary} tag's full-year fact for that year ({other[1]:g}) is consistent with them — a full-year total cannot be smaller than "
                         f"its quarters, so the {secondary} fact is used for that year")
            del fy_facts[p], fy_kind[p]
        elif bad[2]:
            # one quarter's rate tagged with the full-year context (IBKR), the quarters borne out by the 6M / 9M facts or equal to the FY value
            notes.append(f"annual_dps: the {basis} FY DPS fact for the period ended {p} ({fy_facts[p]:g}) is below the sum of the same tag's quarterly facts inside that fiscal year "
                         f"({qtxt}), and those quarters are borne out by the tag's year-to-date facts or each equal the FY value (one quarter's rate tagged with the full-year "
                         "context) — the full-year fact is not a total and is not used (the year has an annual row only if its four quarterly facts are filed)")
            del fy_facts[p], fy_kind[p]
        else:
            notes.append(f"annual_dps: the {basis} FY DPS fact for the period ended {p} ({fy_facts[p]:g}) is below the sum of the same tag's quarterly facts inside that fiscal year "
                         f"({qtxt}) — the quarters are not borne out by year-to-date facts (one of those filings is mis-tagged) and no other filed full-year total replaces it, "
                         "so the FY fact is kept as filed")
    extended, filled = [], []
    if basis and has.get(secondary):
        span = _ends(basis)
        lo, hi = min(span), max(span)
        for e, d in (dps_q.get(secondary) or {}).items():
            if _num(d.get("val")) and (e < lo or e > hi) and e not in q:
                q[e] = dict(d, kind=secondary)
                extended.append(e)
        primary_years = {}
        for e, d in q.items():
            if d["kind"] == basis and d.get("fy_start") and d.get("fq"):
                primary_years.setdefault(d["fy_start"], {})[d["fq"]] = e
        qsum_ends = [max(qs.values()) for qs in primary_years.values() if all(fq in qs for fq in (1, 2, 3, 4))]
        for p, v in sorted((dps_fy.get(secondary) or {}).items()):
            if not _num(v) or any(abs(_days(p, x)) <= 7 for x in list(fy_facts) + qsum_ends):
                continue
            bad = _fy_below_quarters(p, v, secondary)
            if bad and bad[2]:
                notes.append(f"annual_dps: the {secondary} FY DPS fact for the period ended {p} ({v:g}) is below the sum of the same tag's quarterly facts inside that fiscal year ({bad[1]:g}), "
                             "which the tag's year-to-date facts bear out or which each equal it (one quarter's rate tagged with the full-year context) — not used")
                continue
            if bad:
                notes.append(f"annual_dps: the {secondary} FY DPS fact for the period ended {p} ({v:g}) is below the sum of the same tag's quarterly facts inside that fiscal year ({bad[1]:g}) "
                             "— the quarters are not borne out by year-to-date facts and no other filed full-year total replaces it, so the FY fact is kept as filed")
            fy_facts[p], fy_kind[p] = v, secondary
            (extended if (p < lo or p > hi) else filled).append(p)
    dps_basis_detail = None
    if basis:
        dps_basis_detail = f"{basis} facts for periods ending {min(_ends(basis))}..{max(_ends(basis))}"
        if extended:
            extended = sorted(set(extended))
            dps_basis_detail += f"; {secondary} facts for the periods the {basis} tag does not cover ({extended[0]}..{extended[-1]}, {len(extended)} facts)"
        if filled:
            dps_basis_detail += (f"; {secondary} FY facts for {len(filled)} fiscal year(s) inside that span that carry no {basis} FY fact and no four {basis} quarterly facts "
                                 f"({', '.join(filled)})")
        if extended or filled:
            notes.append(f"dps_basis: {dps_basis_detail} — the series switches basis where one tag stops; the switch year can double-count or skip one payment (a dividend declared in one quarter and paid in the next)")
        elif has["declared"] and has["paid"]:
            dps_basis_detail += f"; {secondary} facts exist only inside that span and are not used"
        if basis_rule:
            dps_basis_detail += f"; {basis_rule}"
    any_facts = bool(q or fy_facts)
    latest_fy_row = annual[-1] if annual else None
    latest_end = latest_fy_row["period_end"] if latest_fy_row else None
    payout_fy = latest_fy_row["fy"] if latest_fy_row else None
    last_q_end = qrows[-1]["period_end"] if qrows else None
    reference = max(x for x in (latest_end, last_q_end) if x) if (latest_end or last_q_end) else None

    def stale(e):
        return reference is not None and _days(e, reference) > STALE_DAYS

    # flow legs with the filing's sign errors corrected (sign_fixed_flows); every
    # use of dividends paid / buybacks / issuance below reads these, not the rows
    flow_facts = ctx.get("flow_facts") or {}
    q_flow, a_flow, sign_fixes = sign_fixed_flows(annual, qrows, flow_facts)
    for k in FLOW_KEYS:
        by_kind = {}
        for _, t, kind in sign_fixes[k]:
            by_kind.setdefault(kind, []).append(t)
        if by_kind.get(SIGN_ABS):
            what = ("a payment line is non-negative by definition" if k != "share_issuance"
                    else "issuance proceeds filed below zero beside positive facts of the same fiscal year")
            notes.append(f"sign convention ({k}): {what}, so the value filed below zero is a sign-convention error in the filing — " + "; ".join(by_kind[SIGN_ABS]))
        if by_kind.get(SIGN_KEPT):
            notes.append(f"{k}: filed below zero and kept as filed (a net line, not a sign error) — " + "; ".join(by_kind[SIGN_KEPT]))
        if by_kind.get(SIGN_LEFT_OUT_SIGN):
            notes.append(f"{k}: quarters left out — " + "; ".join(by_kind[SIGN_LEFT_OUT_SIGN]))
        if by_kind.get(SIGN_LEFT_OUT_DECREASE):
            notes.append(f"{k}: quarters left out (not a sign error) — " + "; ".join(by_kind[SIGN_LEFT_OUT_DECREASE]))
    paid_rows = [{"period_end": r["period_end"], "dividends_paid": a_flow["dividends_paid"].get(r["period_end"])} for r in annual
                 if _num(a_flow["dividends_paid"].get(r.get("period_end"))) and a_flow["dividends_paid"][r["period_end"]] > 0]
    paid_rows += [{"period_end": r["period_end"], "dividends_paid": q_flow["dividends_paid"].get(r["period_end"])} for r in qrows
                  if _num(q_flow["dividends_paid"].get(r.get("period_end"))) and q_flow["dividends_paid"][r["period_end"]] > 0]
    paid_any = bool(paid_rows)
    last4 = qrows[-4:] if len(qrows) >= 4 and consecutive_quarters([r["period_end"] for r in qrows[-4:]]) else []

    # 5.4.5 review fix (HSY: per-share tags stopped in 2010, $1.1B of cash
    # dividends a year since): payer status and, when the per-share facts cannot
    # give it, the frequency come from the filed dividends paid. cash_recent:
    # (frequency or None, description) when the latest four consecutive quarters
    # (else, for a filer without 10-Qs, the latest fiscal year) carry a positive
    # dividends-paid figure; None otherwise.
    cash_recent = None
    if last4 and not stale(last4[-1]["period_end"]):
        cq = [(r["period_end"], q_flow["dividends_paid"].get(r["period_end"])) for r in last4]
        posq = [i for i, (_, v) in enumerate(cq) if _num(v) and v > 0]
        if posq:
            cfreq = None
            if all(_num(v) for _, v in cq):
                if len(posq) == 4:
                    cfreq = "quarterly"
                elif len(posq) == 2 and posq[1] - posq[0] == 2:
                    cfreq = "semiannual"
                elif len(posq) == 1:
                    cfreq = "annual"
            cash_recent = (cfreq, f"cash dividends paid are filed for {len(posq)} of the last four quarters ("
                           + ", ".join(f"{cq[i][0]}: {_fmt_big(cq[i][1])}" for i in posq) + ")", {cq[i][0] for i in posq})
    elif not qrows and latest_fy_row and not stale(latest_end):
        v = a_flow["dividends_paid"].get(latest_end)
        if _num(v) and v > 0:
            cash_recent = (None, f"cash dividends paid are filed for FY{payout_fy} ({_fmt_big(v)})", {latest_end})
    # 5.4.6 review fix (reviewer S1 / S2: a suspended common dividend beside
    # preferred dividends): cash establishes payer status only when the leg is
    # the COMMON dividends line (PaymentsOfDividendsCommonStock, ordinary / parent
    # dividends) — PaymentsOfDividends and the IFRS totals include preferred and
    # noncontrolling-interest dividends — and never over per-share facts filed as
    # ZERO (an explicit suspension; zero_since below)
    cash_tags = sorted({f[1] for (s_, e_), f in (flow_facts.get("dividends_paid") or {}).items() if cash_recent and e_ in cash_recent[2] and _num(f[0])})
    cash_common = bool(cash_recent and cash_tags and set(cash_tags) <= COMMON_DIVIDEND_TAGS)
    cash_desc = cash_recent[1] if cash_recent else None  # without the total-line caveat
    if cash_recent and not cash_common:
        cash_recent = (cash_recent[0], cash_recent[1] + (f" on the total dividends line ({', '.join(cash_tags)}) — it can include preferred / noncontrolling-interest dividends"
                                                         if cash_tags else " (the dividends tag is not known — it can be a total that includes preferred dividends)"), cash_recent[2])
    q_pos = sorted(e for e, d in q.items() if d["val"] > 0)
    # (zeros after the last positive fact, while that fact is itself stale — a
    # declarer that files Q2-Q4 as zero after a Q1 declaration (WMT) is not suspended)
    zero_since = [e for e in sorted(q) if q[e]["val"] == 0 and (not q_pos or (e > q_pos[-1] and stale(q_pos[-1]))) and not stale(e)]
    cash_payer = bool(cash_recent and cash_common and not zero_since)

    def cash_every_year_since(end):
        """True when common cash dividends are paid now and every fiscal year in the annual table after `end` files a positive dividends-paid figure."""
        later = [r for r in annual if r.get("period_end") and r["period_end"] > end]
        return cash_payer and all(_num(a_flow["dividends_paid"].get(r["period_end"])) and a_flow["dividends_paid"][r["period_end"]] > 0 for r in later)

    # annual series (FY facts, else the sum of a fiscal year's four quarterly facts)
    quarters_by_fy = {}
    for e, d in q.items():
        if d.get("fy_start") and d.get("fq"):
            quarters_by_fy.setdefault(d["fy_start"], {})[d["fq"]] = (e, d["val"])
    annual_dps = annual_dps_rows(fy_facts, quarters_by_fy)
    if any(r["basis"] == "sum_of_quarters" for r in annual_dps):
        notes.append("annual_dps: " + ", ".join(f"FY{r['fy']}" for r in annual_dps if r["basis"] == "sum_of_quarters") + " = sum of the four filed quarterly DPS facts (no FY fact)")
    annual_out = [{"fy": r["fy"], "period_end": r["period_end"], "dps": r["dps"],
                   "kind": fy_kind.get(r["period_end"]) or next((q[e]["kind"] for e in sorted(q, reverse=True) if e <= r["period_end"]), basis)} for r in annual_dps]
    by_end = {r["period_end"]: r["dps"] for r in annual_dps}
    by_label = {r["fy"]: r["dps"] for r in annual_dps}
    pos_labels = [r["fy"] for r in annual_dps if _num(r.get("dps")) and r["dps"] > 0]
    for fy in dps_outliers(annual_dps):
        where = (f"more than {EDGE_OUTLIER_FACTOR}x the adjacent fiscal year (the {'first' if fy == pos_labels[0] else 'latest'} dividend year, compared with its one neighbour)"
                 if fy in (pos_labels[0], pos_labels[-1]) else "more than 10x both neighbouring years")
        notes.append(f"annual_dps: FY{fy} DPS {by_label[fy]} is {where} — shown as filed; check the filing's XBRL unit before relying on it")
    latest_dps_row = annual_dps[-1] if annual_dps else None
    dps_stale = bool(latest_dps_row and stale(latest_dps_row["period_end"]))
    if latest_dps_row and latest_dps_row["dps"] == 0 and not dps_stale and (not q_pos or q_pos[-1] <= latest_dps_row["period_end"]):
        zero_since = sorted(set(zero_since) | {latest_dps_row["period_end"]})  # a full-year DPS filed as zero is an explicit suspension too
        cash_payer = False

    # labels: the Financials tab's convention (calendar year of the period end)
    # unless two fiscal years end in one calendar year; then the annual /
    # quarterly tables repeat a label and this series does not — say so, the
    # join key is period_end (5.4.3 review: 53-week / FYE-change filers)
    fy_label_basis = "calendar year of the fiscal period end (the annual table's convention)"
    table_labels = {r["period_end"]: r.get("fy") for r in annual if r.get("period_end")}
    relabelled = [(r["fy"], r["period_end"], table_labels[r["period_end"]]) for r in annual_dps
                  if r["period_end"] in table_labels and table_labels[r["period_end"]] and r["fy"] != str(table_labels[r["period_end"]])]
    if relabelled:
        fy_label_basis = "the year most of each fiscal year falls in — two fiscal years end in the same calendar year; join on period_end, not the label"
        notes.append("annual_dps labels: " + "; ".join(f"FY{lab} here (period ended {end}) is labelled FY{tl} in the annual / quarterly tables" for lab, end, tl in relabelled)
                     + " — two fiscal years end in the same calendar year (a 53-week year or a fiscal-year-end change); join on period_end")

    # share-basis breaks the filed split ratios did not cover (unfiled split):
    # growth statistics only over the consistently-based years after the break
    # (5.4.6: ctx shares_by_end — dividends_inputs' split-adjusted diluted
    # counts — replace the table's as-filed counts for the fiscal years the
    # table carries; no years are added, so the guard sees the same years)
    shares_by_end = {r["period_end"]: r.get("shares_diluted") for r in annual}
    adj_shares = ctx.get("shares_by_end") or {}
    for e in shares_by_end:
        if _num(adj_shares.get(e)):
            shares_by_end[e] = adj_shares[e]
    eps_by_end = ctx.get("eps_by_end") or {r["period_end"]: r.get("eps_diluted") for r in annual}
    rejected = []
    breaks = basis_breaks(annual_dps, shares_by_end, eps_by_end, rejected)
    comparable = annual_dps
    if breaks:
        cut_end, rd, rs = breaks[-1]
        cut_label = next(r["fy"] for r in annual_dps if r["period_end"] == cut_end)
        comparable = [r for r in annual_dps if r["period_end"] >= cut_end]
        notes.append(f"annual_dps: FY{cut_label} DPS moved ×{rd:.2f} while diluted shares moved ×{rs:.2f} — a share-basis change (split) with no StockholdersEquityNoteStockSplitConversionRatio1 fact filed, not a cut; growth years, last cut, YoY and CAGR are computed from FY{cut_label} on")
    for cut_end, rd, rs, re in rejected:
        cut_label = next(r["fy"] for r in annual_dps if r["period_end"] == cut_end)
        notes.append(f"annual_dps: FY{cut_label} DPS moved ×{rd:.2f} while diluted shares moved ×{rs:.2f}, but diluted EPS moved ×{re:.2f} — not the restatement a split would show, so the share move is read as a real issuance / reduction and the DPS move as a real cut; check the filing")

    # TTM DPS
    qf = sorted((e, d["val"]) for e, d in q.items())
    dps_ttm, ok = dps_ttm_from_quarters(qf)
    dps_ttm_basis = None
    latest_kind = annual_out[-1]["kind"] if annual_out else basis
    # 5.4.4 review fix: four consecutive quarterly facts that END before the
    # latest FY fact (a filer that stopped tagging the Q4 fact: prior Q4 +
    # Q1..Q3) are older than the fiscal year itself — the FY fact is rolled
    # forward instead of summing the four
    fy_newer = bool(ok and latest_dps_row and latest_dps_row["basis"] == "fy_fact" and not dps_stale and latest_dps_row["period_end"] > qf[-1][0])
    since_txt = qf[-1][0] if qf else (latest_dps_row["period_end"] if latest_dps_row else "the filed history")
    if zero_since:
        untagged = None
    elif cash_payer:
        untagged = f"the per-share rate is not tagged since {since_txt} although {cash_recent[1]} — not a suspension"
    elif cash_recent:
        untagged = f"the per-share rate is not tagged since {since_txt}; {cash_recent[1]} — whether the common dividend continues is not filed"
    else:
        untagged = None
    if ok and not fy_newer:
        last4q = qf[-4:]
        if stale(last4q[-1][0]):
            dps_ttm = None
            if untagged:
                notes.append(f"dps_ttm: the latest quarterly DPS fact ({last4q[-1][0]}) is more than 15 months older than the newest filed period ({reference}) — {untagged}; dps_ttm and dividend_yield null")
            else:
                notes.append(f"dps_ttm: the latest quarterly DPS fact ({last4q[-1][0]}) is more than 15 months older than the newest filed period ({reference}) — dividend suspended or no longer tagged; dps_ttm and dividend_yield null")
        else:
            dps_ttm_basis = f"sum of the four quarterly DPS facts {last4q[0][0]}..{last4q[-1][0]}"
    elif any_facts:
        if fy_newer:
            why = f"the FY DPS fact (period ended {latest_dps_row['period_end']}) is newer than the latest quarterly DPS fact ({qf[-1][0]}) — the four-quarter sum would stop a quarter short"
        else:
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
                # 5.4.6 review fix (ZTS: a CashPaid FY total plus Declared
                # quarters): the roll-forward adds the change between the
                # quarters since and the same quarters a year earlier, which must
                # be one tag; when that tag is not the full-year total's, the
                # basis names the mix (ATO / ED file both tags per quarter, so the
                # change is the same either way)
                q_kinds = {q[e]["kind"] for e, _ in after} | {q[m[0]]["kind"] for m in matched if m}
                if all(m is not None for m in matched) and len(q_kinds) == 1:
                    dps_ttm = latest_dps_row["dps"] + sum(v for _, v in after) - sum(v for _, v in matched)
                    dps_ttm_basis = (f"FY{fy_lab} DPS {latest_dps_row['dps']:g} + the quarters since ({', '.join(f'{e}: {v:g}' for e, v in after)})"
                                     f" − the same quarters a year earlier ({', '.join(f'{e}: {v:g}' for e, v in matched)})")
                    qk = next(iter(q_kinds))
                    if qk != latest_kind:
                        dps_ttm_basis += (f" — mixed basis: the full-year total is a {latest_kind} fact and the quarters are {qk} facts, so the year-over-year change in the "
                                          f"{qk} quarterly rate is applied to the {latest_kind} total (a payment declared in one quarter and paid in the next can shift by a quarter)")
                elif len(q_kinds) > 1:
                    dps_ttm = latest_dps_row["dps"]
                    dps_ttm_basis = (f"FY{fy_lab} DPS ({latest_kind}, {latest_dps_row['basis']}, period ended {fy_end}) — the quarterly facts since and a year earlier are on different "
                                     f"tags ({'/'.join(sorted(q_kinds))}), so the year is not rolled forward")
                else:
                    dps_ttm = latest_dps_row["dps"]
                    dps_ttm_basis = f"FY{fy_lab} DPS ({latest_dps_row['basis']}, period ended {fy_end}) — the {len(after)} quarterly fact(s) since have no prior-year comparative facts, so the year is not rolled forward"
            notes.append(f"dps_ttm: {why} — {dps_ttm_basis}")
        elif latest_dps_row:
            after = [e for e, _ in qf if e > latest_dps_row["period_end"]]
            head = f"dps_ttm: {why}; the latest full-year DPS (FY{latest_dps_row['fy']}, period ended {latest_dps_row['period_end']}) is more than 15 months older than the newest filed period ({reference})"
            tail = (f"; the {len(after)} quarterly fact(s) since ({', '.join(after)}) do not make a trailing twelve months" if after else "") + "; dps_ttm and dividend_yield null"
            if cash_payer and cash_every_year_since(latest_dps_row["period_end"]):
                # 5.4.5 review fix (STAG: Q1-Q3 per-share facts every year, no Q4 / FY fact since FY2019, cash dividends every quarter)
                notes.append(head + f" — no full-year / fourth-quarter per-share fact is tagged since, although cash dividends are paid in every fiscal year since and {cash_recent[1]}"
                             + " — the per-share rate is tagged for some quarters only, not a suspension" + tail)
            elif untagged and (not after or (not cash_payer and stale(after[-1]))):  # per-share facts stopped (none recent); a recent run is a reinstatement
                notes.append(head + f" — {untagged}" + tail)
            else:
                notes.append(head + " — a suspended / reinstated dividend" + tail)
        elif untagged and (not qf or stale(qf[-1][0])):
            notes.append(f"dps_ttm: {untagged}; dps_ttm and dividend_yield null")
        else:
            notes.append(f"dps_ttm: {why} and no FY DPS fact — dps_ttm null")
    if not any_facts:
        if paid_any:
            r = paid_rows[-1]
            notes.append(f"no dividends-per-share facts filed (CommonStockDividendsPerShareDeclared / CashPaid or IFRS equivalents) although cash dividends paid are filed ({_fmt_big(r['dividends_paid'])} for the period ended {r['period_end']}) — per-share rate not tagged; "
                         + ("dps_ttm and dividend_yield null, frequency from the quarters with cash dividends paid" if cash_payer and cash_recent[0] else "dps_ttm, dividend_yield and frequency null"))
        else:
            notes.append("no dividends-per-share facts filed (CommonStockDividendsPerShareDeclared / CashPaid or IFRS equivalents) and no dividends paid — not a dividend payer")

    # frequency: the FY-count rule when the FY total carries a payment the
    # quarterly facts do not (the 10-K files the year, not the Q4), else the
    # spacing of the latest quarterly facts (a mid-year initiator reads quarterly)
    frequency, frequency_basis = None, None
    cash_cadence_pending = False
    pos = q_pos
    zeros = sorted(e for e, d in q.items() if d["val"] == 0)
    # 5.4.4 review fix (WMT): staleness applies to the LATEST positive fact
    # only; the spacing is read from the trailing run of positive facts (gaps
    # ≤400 days — a suspension ends the run) whatever their own age, so an
    # annual declarer whose previous fact is 457 days old still reads "annual"
    recent = []
    if pos and not stale(pos[-1]):
        recent = [pos[-1]]
        for e in reversed(pos[:-1]):
            if _days(e, recent[0]) > FY_SPACING[1]:
                break
            recent.insert(0, e)

    def _cash_frequency(lead):
        """Frequency from the quarters with common cash dividends paid (cash_recent), with its basis; the note when it cannot be read."""
        if not cash_payer:
            if cash_recent:
                notes.append(f"frequency: {lead}; {cash_recent[1]} — not the common-stock dividend line, so it does not give the common dividend's cadence; frequency null")
            return None, None
        f, desc = cash_recent[0], cash_recent[1]
        # 4 of 4 quarters reads quarterly on its own; fewer only for an established
        # payer (cash dividends in every fiscal year of the last three) — one paid
        # quarter of a reinstated payer is not an "annual" cadence
        if f and (f == "quarterly" or (reference and cash_every_year_since(_add_days(reference, -3 * 365)))):
            return f, f"{desc} — {lead}; the per-share facts do not give the cadence, so this is the cadence of the filed cash dividends (a payment cadence inside a quarter is not filed)"
        if last4:
            notes.append(f"frequency: {lead}; {desc} — the four quarters do not show an established cadence, frequency null")
        return None, None

    if not any_facts:
        frequency = infer_frequency(0, None, None, False, False, dividends_paid=paid_any)
        if cash_recent:
            frequency, frequency_basis = _cash_frequency("no dividends-per-share facts filed")
    elif not q:
        if dps_stale:
            notes.append(f"frequency: the only DPS facts are full-year facts up to FY{latest_dps_row['fy']} (period ended {latest_dps_row['period_end']}), stale against the newest filed period ({reference})"
                         + (f"; cash dividends paid are filed ({_fmt_big(paid_rows[-1]['dividends_paid'])} for the period ended {paid_rows[-1]['period_end']}) but the per-share rate is not tagged" if paid_any else "")
                         + (" — frequency from the quarters with cash dividends paid" if cash_payer and cash_recent[0] else " — payment frequency not inferable"))
            if cash_recent:
                frequency, frequency_basis = _cash_frequency(f"no per-share fact since FY{latest_dps_row['fy']}")
        else:
            notes.append("frequency: only full-year DPS facts are filed (no quarterly / interim facts) — payment count not inferable")
    elif not recent:
        last_pos = pos[-1] if pos else "the filed history"
        if zero_since:
            # 5.4.6 review fix (reviewer S1): per-share facts filed as ZERO are an explicit suspension — cash paid does not override them
            frequency = "irregular"
            notes.append(f"frequency: no positive quarterly DPS fact since {last_pos} and the per-share dividend is filed as zero since ({', '.join(zero_since[-6:])}) — dividend suspended; shown as irregular"
                         + (f" ({cash_recent[1]} — not a common dividend rate the filer tags: preferred / noncontrolling-interest dividends or the last payment of the suspended dividend)" if cash_recent else ""))
        elif cash_payer:
            notes.append(f"frequency: no positive quarterly DPS fact since {last_pos} (newest filed period {reference}), but {cash_recent[1]} — "
                         "the per-share rate is no longer tagged, not a suspension")
            frequency, frequency_basis = _cash_frequency(f"no per-share fact since {last_pos}")
        elif cash_recent:
            notes.append(f"frequency: no positive quarterly DPS fact since {last_pos} (newest filed period {reference}); {cash_recent[1]} — whether the common dividend continues "
                         "is not filed, so it is neither read as suspended nor as paid; frequency null")
        else:
            frequency = "irregular"
            notes.append(f"frequency: no positive quarterly DPS fact since {last_pos} (newest filed period {reference}) and no cash dividends paid filed for the latest quarters — dividend suspended; shown as irregular")
    else:
        fy_rule, fy_rule_basis = None, None
        if latest_dps_row and latest_dps_row["basis"] == "fy_fact" and not dps_stale:
            fy_end = latest_dps_row["period_end"]
            # 5.4.4 review fix: the fiscal year is bounded by the previous
            # fiscal year's period end (annual table, else annual_dps), not a
            # 400-day look-back that pulled the prior year's Q4 fact in
            prev_ends = [r["period_end"] for r in list(annual) + annual_dps if r.get("period_end") and r["period_end"] < fy_end and fy_consecutive(r["period_end"], fy_end)]
            fy_floor = max(prev_ends) if prev_ends else _add_days(fy_end, -400)
            in_fy_e = sorted(e for e, d in q.items() if fy_floor < e <= fy_end and d["val"] > 0)
            in_fy = [q[e]["val"] for e in in_fy_e]
            # 5.4.6 review fixes: the FY total and the quarters must be the same
            # tag (ZTS: a CashPaid FY 2.03 against Declared quarters 0.5, 0.5, 0);
            # a remainder below half a quarterly payment is rounding (IRM 3.22 vs 3.219)
            mixed_kinds = sorted({q[e]["kind"] for e in in_fy_e} - {latest_kind})
            if in_fy and mixed_kinds:
                notes.append(f"frequency: the FY{latest_dps_row['fy']} total is a {latest_kind} fact and the quarterly facts inside that year are {'/'.join(mixed_kinds)} facts — "
                             "the payment count needs both from one tag, so the cadence is read from the spacing of the quarterly facts")
            elif in_fy and fy_remainder_is_a_payment(latest_dps_row["dps"], sum(in_fy), min(in_fy)):
                fy_rule = infer_frequency(len(in_fy), latest_dps_row["dps"], sum(in_fy), True, True, min_quarterly=min(in_fy))
                fy_rule_basis = f"{len(in_fy)} quarterly DPS facts inside FY{latest_dps_row['fy']} ({_add_days(fy_floor, 1)}..{fy_end}) plus one payment carried only in the FY total"
        used = recent[-4:]
        spacing = frequency_from_spacing(used) if len(recent) >= 2 else None
        spacing_basis = None
        if spacing:
            spacing_basis = f"spacing of the latest {len(used)} positive quarterly DPS facts ({', '.join(used)})"
            zero_in = [z for z in zeros if z > used[0]]
            if zero_in:
                spacing_basis += f"; quarters filed as zero: {', '.join(zero_in)}"
        # an FY count that reads "irregular" does not override a regular spacing (5.4.6: GEHC declares two dividends in one quarter)
        if fy_rule and not (fy_rule == "irregular" and spacing and spacing != "irregular"):
            frequency, frequency_basis = fy_rule, fy_rule_basis
        elif spacing:
            frequency, frequency_basis = spacing, spacing_basis
            if fy_rule:
                frequency_basis += f" (the FY count — {fy_rule_basis} — reads irregular)"
        elif fy_rule:
            frequency, frequency_basis = fy_rule, fy_rule_basis
        elif cash_payer and cash_recent[0] and reference and cash_every_year_since(_add_days(reference, -3 * 365)):
            # an established payer whose per-share quarters are mostly untagged (STAG): the cash cadence, labelled
            frequency, frequency_basis = _cash_frequency(f"only one recent quarterly per-share fact ({recent[-1]}) is tagged")
        else:
            notes.append(f"frequency: a single quarterly DPS fact so far ({recent[-1]}) — payment frequency not inferable yet")
        # 5.4.6: a per-share reading other than quarterly while cash dividends are
        # paid in each of the last four quarters is checked against the cash
        # below, once dps_ttm, the cash TTM and the diluted count are known
        cash_cadence_pending = bool(frequency in ("irregular", "semiannual", "annual") and cash_recent and cash_recent[0] == "quarterly" and not zero_since)
        if frequency == "quarterly" and frequency_basis and not frequency_basis.startswith("cash dividends"):
            # 5.4.5 review (MAIN, STAG pay monthly): the per-share facts are quarterly totals
            frequency_basis += "; the per-share facts are filed per quarter — a payment cadence inside the quarter (a monthly payer) is not tagged"

    # growth (on the comparable series; null when the latest annual row is stale)
    dps_growth_yoy = None
    if not dps_stale and len(comparable) >= 2 and fy_consecutive(comparable[-2]["period_end"], comparable[-1]["period_end"]):
        dps_growth_yoy = _g(comparable[-1]["dps"], comparable[-2]["dps"])
    cagr3 = cagr5 = None
    if not dps_stale:
        for years, key in ((3, "dps_cagr_3y"), (5, "dps_cagr_5y")):
            value, why = dps_cagr_window(comparable, years)
            if years == 3:
                cagr3 = value
            else:
                cagr5 = value
            if why and len(comparable) >= 2 and not why.startswith("no annual DPS row"):
                notes.append(f"{key}: null — {why}")
    gyears = growth_years(comparable) if not dps_stale else 0
    cut = last_cut_fy(comparable)
    if dps_stale:
        notes.append(f"growth: the latest annual DPS row (FY{latest_dps_row['fy']}, period ended {latest_dps_row['period_end']}) is more than 15 months older than the newest filed period ({reference}) — YoY growth, CAGR and growth years null")

    # payout ratios on the latest fiscal year in the annual table (dividends
    # paid sign-corrected: CCI's FY2025 10-K files −2.08B)
    pr_eps = pr_oe = pr_fcf = None
    if latest_fy_row:
        d_fy = by_end.get(latest_end)
        div_fy = a_flow["dividends_paid"].get(latest_end)
        pr_eps = payout_ratio(d_fy, latest_fy_row.get("eps_diluted"))
        pr_oe = payout_ratio(div_fy, latest_fy_row.get("oe_conservative"))
        pr_fcf = payout_ratio(div_fy, latest_fy_row.get("fcf"))
        if d_fy is None and any_facts:
            notes.append(f"payout_ratio_eps: no DPS fact for FY{payout_fy} (latest fiscal year in the annual table)")
        if latest_fy_row.get("dividends_paid") is None and any_facts:
            notes.append(f"payout_ratio_oe / payout_ratio_fcf: dividends paid not filed for FY{payout_fy}")

    # flows: the last four quarterly rows when they are consecutive quarters;
    # a filer without 10-Qs (20-F/40-F) falls back to the latest fiscal year's
    # annual flows, labelled as such. Each leg records how complete it is, and
    # `sign_corrected` names any value the filing carried below zero and read
    # as its absolute amount, `kept_as_filed` a negative issuance line kept,
    # `left_out` the quarters no consistent figure exists for (5.4.6).
    flows = {k: ttm_sum(q_flow[k].get(r["period_end"]) for r in last4) if last4 else None for k in FLOW_KEYS}
    legs, flows_basis, flows_end = {}, None, None

    def never_filed(k):
        return filed_any.get(k) is False

    def _attach(leg_, entries):
        """5.4.6: a leg's sign entries by kind — sign_corrected (a filed sign
        read as its absolute amount), kept_as_filed (a negative issuance line
        kept), left_out (quarters no consistent figure exists for)."""
        for field, kinds in (("sign_corrected", (SIGN_ABS,)), ("kept_as_filed", (SIGN_KEPT,)), ("left_out", (SIGN_LEFT_OUT_SIGN, SIGN_LEFT_OUT_DECREASE))):
            got = [t for t, kind in entries if kind in kinds]
            if got:
                leg_[field] = got

    if last4:
        flows_basis = f"sum of the four quarterly rows {last4[0]['period_end']}..{last4[-1]['period_end']}"
        flows_end = last4[-1]["period_end"]
        win = {r["period_end"] for r in last4}
        for k in FLOW_KEYS:
            fixed_here = [(t, kind) for e, t, kind in sign_fixes[k] if e in win]
            if flows[k] is not None:
                legs[k] = {"value": flows[k], "basis": "4/4 quarters filed", "complete": True}
                _attach(legs[k], fixed_here)
                continue
            filed = [(r["period_end"], q_flow[k].get(r["period_end"])) for r in last4 if _num(q_flow[k].get(r["period_end"]))]
            missing = [r["period_end"] for r in last4 if not _num(q_flow[k].get(r["period_end"]))]
            # 5.4.4 review fix (CCL): a filed year-to-date fact that spans
            # window quarters the rows could not derive (Q1 untagged → Q2 = 6M
            # − Q1 impossible) is a filed value covering them — the leg is the
            # YTD plus the filed quarters outside its span, and only quarters
            # no filed fact covers are missing (5.4.5: sign errors as absolute
            # amounts; 5.4.6: a consistently negative issuance fact as filed)
            ff = flow_facts.get(k) or {}
            ff_signed, flipped = signed_flow_facts(k, ff)
            ytd = ytd_cover(last4, ff_signed) if ff_signed else None
            if ytd:
                y_val, y_ends, y_desc, y_key = ytd
                if y_key in flipped:
                    fixed_here.append((f"the year-to-date fact {y_key[0]}..{y_key[1]} filed as {_fmt_big(ff[y_key][0])}, read as {_fmt_big(y_val)}", SIGN_ABS))
                    notes.append(f"sign convention ({k}): the year-to-date fact {y_key[0]}..{y_key[1]} is filed as {_fmt_big(ff[y_key][0])} — a sign-convention error, read as {_fmt_big(y_val)}")
                outside = [(e, v) for e, v in filed if e not in y_ends]
                covered = set(y_ends) | {e for e, _ in outside}
                missing = [r["period_end"] for r in last4 if r["period_end"] not in covered]
                value = y_val + sum(v for _, v in outside)
                desc = y_desc + (f" + the filed quarters {', '.join(e for e, _ in outside)}" if outside else "")
                if not missing:
                    legs[k] = {"value": value, "basis": f"4/4 quarters covered: {desc}", "complete": True}
                    _attach(legs[k], fixed_here)
                    flows[k] = value
                    notes.append(f"{k}_ttm: {desc} — the four quarters are covered by filed facts although not every quarter is filed on its own")
                    continue
                legs[k] = {"value": value, "basis": f"{4 - len(missing)}/4 quarters covered ({desc}) — a lower bound", "complete": False}
            elif filed:
                legs[k] = {"value": sum(v for _, v in filed), "basis": f"{len(filed)}/4 quarters filed ({', '.join(e for e, _ in filed)}) — a lower bound", "complete": False}
            elif never_filed(k):
                legs[k] = {"value": 0.0, "basis": "never filed in any period — zero by the filer's own statements", "complete": True}
            else:
                legs[k] = {"value": None, "basis": "not filed for any of the four quarters", "complete": False}
            _attach(legs[k], fixed_here)
            notes.append(f"{k}_ttm: not all of the last four quarters have a filed {k} figure (missing {', '.join(missing)})"
                         + (f" — {ytd[2]} covers {len(ytd[1])} of them" if ytd else "")
                         + ("" if (filed or ytd) else (" — the tag was never filed in any period, so the leg counts as zero" if never_filed(k) else "")))
    elif not qrows and latest_fy_row:
        flows_basis = f"FY{payout_fy} annual flows (period ended {latest_end}) — no quarterly filings (20-F/40-F filer)"
        flows_end = latest_end
        for k in FLOW_KEYS:
            v = a_flow[k].get(latest_end)
            if _num(v):
                legs[k] = {"value": v, "basis": f"FY{payout_fy} annual fact", "complete": True}
                _attach(legs[k], [(t, kind) for e, t, kind in sign_fixes[k] if e == f"FY:{latest_end}"])
            elif never_filed(k):
                legs[k] = {"value": 0.0, "basis": "never filed in any period — zero by the filer's own statements", "complete": True}
            else:
                legs[k] = {"value": None, "basis": f"not filed for FY{payout_fy}", "complete": False}
        notes.append("quarterly flows: no quarterly facts (20-F/40-F filer without 10-Qs) — dividends_paid_ttm / buybacks_ttm / issuance_ttm null; the buyback and shareholder yields use the latest fiscal year's annual flows")
    else:
        for k in FLOW_KEYS:
            legs[k] = {"value": None, "basis": "fewer than four consecutive quarterly rows", "complete": False}
        notes.append("quarterly flows: fewer than four consecutive quarterly rows — dividends_paid_ttm / buybacks_ttm / issuance_ttm null")

    # shares (the price, the market cap and every yield on them are set by
    # price_dividends below, so build_site.py can reprice the block at a newer
    # close with the very same code)
    diluted = next((r["shares_diluted"] for r in reversed(qrows) if _num(r.get("shares_diluted"))), None)
    diluted_src = "latest quarterly weighted-average diluted" if diluted is not None else None
    if diluted is None and annual:
        diluted = next((r["shares_diluted"] for r in reversed(annual) if _num(r.get("shares_diluted"))), None)
        diluted_src = "latest annual weighted-average diluted" if diluted is not None else None
    inst = ctx.get("shares_instant")
    # ruling-sheet Q8 bug 2 (Andrew, 2026-10-19), recency: an instant count dated more than 18 months
    # (dcf_engine.DEI_MAX_AGE_DAYS) before the newest fiscal year end is not today's share count — TLK's only
    # undimensioned instant count is a 1995-11-13 fact (8.4B shares) that divided 2024 flows into a 123.36% yield
    newest_fy = max((r.get("period_end") for r in (annual or []) if r.get("period_end")), default=None)
    stale_inst, shares_scale_break = None, False
    if inst and _num(inst[0]) and inst[0] > 0 and newest_fy and inst[1] and _days(inst[1], newest_fy) > _engine.DEI_MAX_AGE_DAYS:
        stale_inst = inst
        notes.append(f"shares: the latest filed instant share count ({inst[0]:,.0f}, {inst[2]}, as of {inst[1]}) is stale — more than "
                     f"{_engine.DEI_MAX_AGE_DAYS} days before the newest fiscal year end ({newest_fy}) — so it is not the market-cap denominator")
        inst = None
    if inst and _num(inst[0]) and inst[0] > 0:
        shares, shares_as_of, shares_src, shares_basis = inst[0], inst[1], inst[2], "instant"
    else:
        # 5.4.3 review fix (TKO): a dual-class filer's instant counts are
        # class-dimensioned and absent from companyfacts — fall back to a filed
        # diluted weighted-average count, say so in shares_source, and never
        # leave the market cap null while a weighted count exists.
        # verifier round 1 (COKE, WMG, VOD, TLK): the fallback's source names WHY it is used — the stale count, not the
        # dual-class explanation, when an undimensioned instant count was filed but is stale
        fb = fallback_share_count(qrows, annual, reason=(
            f"weighted-average diluted count, fallback: the latest undimensioned instant share count ({stale_inst[0]:,.0f}, {stale_inst[2]}, "
            f"as of {stale_inst[1]}) is stale — more than {_engine.DEI_MAX_AGE_DAYS} days before the newest fiscal year end ({newest_fy})")
            if stale_inst else None, anchor=ctx.get("engine_shares") if stale_inst else None)
        eng = ctx.get("engine_shares")
        if fb and stale_inst and _num(eng) and eng > 0 and not (1 / SHARE_SCALE_BAND <= fb[0] / eng <= SHARE_SCALE_BAND):
            # ruling-sheet Q8 bug 2: the fallback that replaces a stale count is checked against the engine's validated
            # diluted count (dcf_numbers.json shares_diluted_latest) — PAC's filed weighted-average facts are 1,000x its
            # 505,277,464 shares, so neither count prices the cap; null, never a $10T market cap
            notes.append(f"shares: the diluted fallback count ({fb[0]:,.0f}, {fb[2]}) is {fb[0] / eng:,.1f}x the engine's validated diluted count "
                         f"({eng:,.0f}, dcf_numbers.json shares_diluted_latest) — a scale break in the filed counts, so the market cap and yields are null")
            fb = None
            shares_scale_break = True
        shares, shares_as_of, shares_src = fb if fb else (None, None, None)
        shares_basis = "weighted_average_diluted_fallback" if fb else None
        if shares is not None:
            notes.append(f"shares: market cap uses the {shares_src}")
    if shares is None and not shares_scale_break:
        notes.append("shares: no current share count filed (the latest instant count is stale and no diluted count is filed) — market cap and yields null"
                     if stale_inst else "shares: no share count filed — market cap and yields null")

    # 5.4.6 review fix (HPQ declares two quarters at once, GEHC two in Q3 and
    # none in Q2, KVUE / WRB at some run dates): per-share facts filed on a
    # declaration cadence read "semiannual" / "irregular" (ZTS at some run dates:
    # "annual" — Q1 and Q2 positive, Q3 filed as zero, no Q4) for a company whose
    # common cash dividend is paid in each of the last four quarters. The cash
    # line counts as the common dividend when it is the common-stock tag, or —
    # on the total PaymentsOfDividends line — when the four quarters' cash
    # (dividends_paid_ttm) is within 0.85–1.15x of dps_ttm × the latest diluted
    # count, i.e. there is no material preferred / NCI dividend inside it
    if cash_cadence_pending:
        cash_ttm = flows.get("dividends_paid")
        implied = dps_ttm * diluted if _num(dps_ttm) and _num(diluted) else None
        corroborated = cash_payer or bool(_num(cash_ttm) and _num(implied) and implied > 0 and 0.85 <= cash_ttm / implied <= 1.15)
        if corroborated:
            check = "" if cash_payer else (f" ({', '.join(cash_tags) or 'the dividends line'} is not the common-stock tag, but its four quarters, {_fmt_big(cash_ttm)}, match dps_ttm "
                                           f"{dps_ttm:g} × {diluted:,.0f} diluted shares = {_fmt_big(implied)}, so it carries the common dividend)")
            frequency_basis = (f"{cash_desc}{check} — the cash dividend is paid every quarter; the per-share facts read {frequency} "
                               f"({frequency_basis}) because they are filed on a declaration cadence, not a payment cadence")
            frequency = "quarterly"
        else:
            notes.append(f"frequency: the per-share facts read {frequency} ({frequency_basis}); {cash_recent[1]} — not shown to be the common dividend alone, so the per-share reading stands")

    # yields
    def leg(k):
        return legs.get(k, {}).get("value")

    div_leg, bb_leg, iss_leg = leg("dividends_paid"), leg("buybacks"), leg("share_issuance")
    # 5.4.3 review fix: every flow yield is built the same way — from the legs
    # that ARE filed (complete, or filed for only some of the four quarters and
    # summed as a bound), a never-filed line as zero, a leg not filed in the
    # window left out — and `yield_basis` says, per yield, which legs went in,
    # which were taken as zero, which were left out, and whether the figure is
    # exact, a lower bound, an upper bound or neither. A yield is null only when
    # its own leg is unknown (buybacks for the buyback yields; both dividends
    # and buybacks for the shareholder yield), when the block's currency is not
    # the price's (price_dividends, ruling-sheet Q8 bug 3) or when the market
    # cap is null (no current share count / a SHARE_SCALE_BAND scale break, Q8
    # bug 2). No headline carries a partial numerator without this flag.
    # The market cap (the denominator) and the bound note that goes with it are
    # set by price_dividends (YIELD_LEGS / YIELD_REQUIRES are module constants):
    # everything here is price-free.

    def yield_parts(name):
        """(numerator, basis dict) for one flow yield."""
        spec = YIELD_LEGS[name]
        known = {k for k, _ in spec if _num(leg(k))}
        req = YIELD_REQUIRES[name]
        if not any(k in known for k in req):
            return None, {"legs": {k: legs.get(k, {}).get("basis") for k, _ in spec}, "filed": [], "zero": [], "excluded": [k for k, _ in spec],
                          "partial": [], "bound": None, "complete": False, "numerator": None, "denominator": None,
                          "note": f"{' / '.join(req)} not filed for the window — null"}
        total, filed, zero, excluded, partial, lower, upper = 0.0, [], [], [], [], False, False
        for k, sign in spec:
            info = legs.get(k) or {}
            v = info.get("value")
            if not _num(v):
                excluded.append(k)
                # an unknown positive leg means the true figure is at least this one; an unknown negative leg, at most
                lower, upper = lower or sign > 0, upper or sign < 0
                continue
            total += sign * v
            if "never filed" in str(info.get("basis")):
                zero.append(k)
            else:
                filed.append(k)
            if not info.get("complete"):
                partial.append(k)
                lower, upper = lower or sign > 0, upper or sign < 0
        bound = "exact" if not (lower or upper) else ("lower" if lower and not upper else ("upper" if upper and not lower else "indeterminate"))
        return total, {"legs": {k: legs.get(k, {}).get("basis") for k, _ in spec}, "filed": filed, "zero": zero, "excluded": excluded,
                       "partial": partial, "bound": bound, "complete": False, "numerator": total, "denominator": None}

    yield_basis = {}
    for name in YIELD_LEGS:
        total, yb = yield_parts(name)
        yb["complete"] = bool(yb["bound"] == "exact" and not yb["excluded"])
        # 5.4.5 review blocker (CCI): a leg the filing carried below zero is read
        # as its absolute amount, and the yield's basis says which legs and why
        # (5.4.6: only the entries that were read as absolute amounts; a kept
        # negative issuance line and left-out quarters are named as such)
        fixed = {k: legs[k]["sign_corrected"] for k, _ in YIELD_LEGS[name] if legs.get(k, {}).get("sign_corrected")}
        if fixed:
            yb["sign_corrected"] = {k: "; ".join(v) + " — the filed sign is a sign-convention error, the absolute amount is used"
                                    for k, v in fixed.items()}
        kept = {k: legs[k]["kept_as_filed"] for k, _ in YIELD_LEGS[name] if legs.get(k, {}).get("kept_as_filed")}
        if kept:
            yb["kept_as_filed"] = {k: "; ".join(v) for k, v in kept.items()}
        left = {k: legs[k]["left_out"] for k, _ in YIELD_LEGS[name] if legs.get(k, {}).get("left_out")}
        if left:
            yb["left_out"] = {k: "; ".join(v) for k, v in left.items()}
        yield_basis[name] = yb
    yield_basis["dividend_yield"] = {"numerator": dps_ttm, "basis": dps_ttm_basis, "bound": "exact" if dps_ttm is not None else None,
                                     "complete": dps_ttm is not None, "denominator": None}
    sh_total = yield_basis["shareholder_yield"]["numerator"]
    parts = []
    for k, sign in (("dividends_paid", "+"), ("buybacks", "+"), ("share_issuance", "−")):
        if k not in legs:
            continue
        parts.append((f"{sign} " if parts else "") + (f"{k} ({legs[k]['basis']})" if _num(legs[k]["value"]) else f"{k} NOT INCLUDED ({legs[k]['basis']})"))
    sh_basis = " ".join(parts) + (f"; {flows_basis}" if flows_basis else "")
    history = [dict({"period_end": e, "dps": q[e]["val"], "kind": q[e]["kind"]}, **({"split_factor": q[e]["split_factor"]} if q[e].get("split_factor") else {})) for e in sorted(q, reverse=True)[:20]]
    # the filing feed is ahead of companyfacts: say so
    lfp = ctx.get("latest_filed_period") or {}
    newest = max(((p, f) for f, p in lfp.items() if p), default=None)
    if newest and reference and newest[0] > reference:
        msg = f"latest {newest[1]} (period {newest[0]}) is not yet in EDGAR companyfacts — annual / quarterly rows, TTM flows and this dividends block stop at {reference}"
        notes.append(msg)
        if isinstance(ctx.get("warnings"), list):
            ctx["warnings"].append(msg)

    block = {
        "dps_ttm": dps_ttm, "dps_ttm_basis": dps_ttm_basis, "dps_basis": basis if not (extended or filled) else "mixed", "dps_basis_detail": dps_basis_detail,
        "frequency": frequency, "frequency_basis": frequency_basis,
        "annual_dps": annual_out,
        "dps_growth_yoy": dps_growth_yoy, "dps_cagr_3y": cagr3, "dps_cagr_5y": cagr5,
        "growth_years": gyears, "last_cut_fy": cut,
        "growth_from_fy": comparable[0]["fy"] if comparable else None,
        "fy_label_basis": fy_label_basis,
        "basis_breaks": [{"period_end": e, "dps_ratio": rd, "shares_ratio": rs} for e, rd, rs in breaks],
        "basis_breaks_rejected": [{"period_end": e, "dps_ratio": rd, "shares_ratio": rs, "eps_ratio": re} for e, rd, rs, re in rejected],
        "split_adjustments": [{"effective": _split_cutoff(s)[0], "ratio": _split_cutoff(s)[1], "first_post_split_filing": _split_cutoff(s)[2],
                               "source": s[3] if len(s) > 3 and s[3] else "ratio_fact"} for s in (ctx.get("splits") or [])],
        "payout_ratio_eps": pr_eps, "payout_ratio_oe": pr_oe, "payout_ratio_fcf": pr_fcf,
        "payout_fy": payout_fy,
        "dividends_paid_ttm": flows["dividends_paid"], "buybacks_ttm": flows["buybacks"], "issuance_ttm": flows["share_issuance"],
        "ttm_period_end": last4[-1]["period_end"] if last4 else None,
        "flows_basis": flows_basis, "flows_period_end": flows_end, "legs": legs,
        # the price leaves (PRICE_LEAVES) are placeholders here, set by price_dividends
        "price": None, "price_date": None, "price_source": None, "price_note": None,
        "shares_outstanding": shares, "shares_as_of": shares_as_of, "shares_source": shares_src, "shares_basis": shares_basis,
        "shares_diluted": diluted, "shares_diluted_source": diluted_src,
        "ads_ratio": ctx.get("ads_ratio"),
        "market_cap": None, "market_cap_basis": None,
        "dividend_yield": None,
        "buyback_yield": None,
        "net_buyback_yield": None,
        "shareholder_yield": None,
        "shareholder_yield_basis": sh_basis if sh_total is not None else None,
        "shareholder_yield_complete": yield_basis["shareholder_yield"]["complete"],
        "yield_basis": yield_basis,
        "yields_display": None,
        "history": history,
        "notes": notes,
    }
    cur = ctx.get("currency")
    if cur and cur != PRICE_CURRENCY:
        # ruling-sheet Q8 bug 3: DPS and the flow legs are in the file's money unit, the price in USD — no yield across
        # two currencies (RDY: Rs40 DPS / $12.87 = "310.80%"; SKM: KRW 3,540 / $31.96 = "11,076%"). Only non-USD blocks
        # carry the key, so a USD block is written exactly as before.
        block["currency"] = cur
        notes.append(f"yields: dividends per share and the cash-flow legs are filed in {cur} and the price is in {PRICE_CURRENCY} — this file applies "
                     f"no FX conversion, so the dividend, buyback and shareholder yields are not computed (the market cap is the {PRICE_CURRENCY} price × shares)")
    return price_dividends(block, price, price_date, price_source)


# ---------------------------------------------------------------------------
# The price-dependent part of the dividends block (2026-10-16 data policy).
# fundamentals.json is committed and rewritten only when its content changes;
# the close moves every day. Every leaf that depends on the price is set by
# price_dividends from the block's own price-free fields (dps_ttm, the share
# count, the yield_basis numerators and bounds, the legs) and listed in
# PRICE_LEAVES, which write_fundamentals treats as volatile: a new close alone
# never rewrites the file. build_site.py calls the same function with a newer
# prices.json close, so the page shows the yields at the latest close, equal
# to what this script would write at that price.
# ---------------------------------------------------------------------------
YIELD_LEGS = {"buyback_yield": (("buybacks", 1),), "net_buyback_yield": (("buybacks", 1), ("share_issuance", -1)),
              "shareholder_yield": (("dividends_paid", 1), ("buybacks", 1), ("share_issuance", -1))}
YIELD_REQUIRES = {"buyback_yield": ("buybacks",), "net_buyback_yield": ("buybacks",), "shareholder_yield": ("dividends_paid", "buybacks")}
YIELD_BOUND_NOTES = {"lower": "a lower bound — a positive leg is filed for only some quarters or not at all",
                     "upper": "an upper bound — the issuance leg is filed for only some quarters or not at all",
                     "indeterminate": "neither bound — a positive leg and the issuance leg are both incomplete"}
YIELD_KEYS = ("dividend_yield", "buyback_yield", "net_buyback_yield", "shareholder_yield")
# dotted paths in fundamentals.json (_stable.py: `*` = every key at that level)
PRICE_LEAVES = ("dividends.price", "dividends.price_date", "dividends.price_source", "dividends.price_note",
                "dividends.market_cap", "dividends.market_cap_basis",
                "dividends.dividend_yield", "dividends.buyback_yield", "dividends.net_buyback_yield", "dividends.shareholder_yield",
                "dividends.yield_basis.*.denominator",
                "dividends.yields_display.*.value", "dividends.yields_display.*.label")
FUNDAMENTALS_VOLATILE = ("as_of",) + PRICE_LEAVES
LEGACY_PRICE_NOTE = "price: "  # a block written before 2026-10-16 carried its price note in `notes`


def _with_note_after_denominator(yb, note):
    """yb with `note` set (None: removed) right after `denominator`, the key
    order the block has always been written in."""
    out = {}
    for k, v in yb.items():
        if k == "note":
            continue
        out[k] = v
        if k == "denominator" and note is not None:
            out["note"] = note
    if note is not None and "note" not in out:
        out["note"] = note
    return out


PRICE_CURRENCY = "USD"  # prices.json (Nasdaq) and score.json closes


def price_dividends(div, price, price_date, price_source, currency=None, unit_unrecorded=None):
    """The dividends block `div` priced at `price` (pure: `div` is not
    modified). Every price-dependent leaf — price / price_date / price_source
    / price_note, market_cap and its basis, the four yields,
    yield_basis.*.denominator (and the bound note that goes with a market
    cap), yields_display — is recomputed from the block's own price-free
    fields: dps_ttm and its basis, shares_outstanding / shares_source /
    shares_as_of, the yield_basis numerators, bounds and legs, `notes`.
    build_dividends ends with this call, so a block repriced here at P equals
    the block fundamentals.py writes at P. A price note in `notes` from a
    block written before 2026-10-16 is dropped (it is `price_note` now).
    Ruling-sheet Q8 bug 3: the yields are computed only when the block's
    numerators are in the price's currency (USD) — `currency` (build_site.py
    passes fundamentals.json's own) else the block's `currency` key (written
    only on a non-USD block) else USD; otherwise every yield is null and
    yields_display says why. The market cap is unaffected.
    `unit_unrecorded` (build_site.py, verifier round 2): the file's currency
    when it is not USD and the block was written before the one-currency rule
    (no `currency` key) — its legs and DPS were read USD-first, so their unit
    is not recorded; the yields are null and the note says so instead of
    naming the file's currency as the numerator's."""
    if not isinstance(div, dict):
        return div
    d = dict(div)
    num_cur = currency or d.get("currency") or PRICE_CURRENCY
    notes = [n for n in (d.get("notes") if isinstance(d.get("notes"), list) else [])
             if not (isinstance(n, str) and n.startswith(LEGACY_PRICE_NOTE))]
    if price is None:
        price_note = "price: neither prices.json nor score.json carries a price — yields null"
    elif price_source and "score.json" in price_source:
        price_note = f"price: {price} from score.json ({price_date}); prices.json absent"
    else:
        price_note = None
    shares, shares_src, shares_as_of = d.get("shares_outstanding"), d.get("shares_source"), d.get("shares_as_of")
    # ADS filers: shares_outstanding is the ordinary share count while the
    # price is per ADS, so the yield denominator divides by the ads_ratio the
    # engine recorded in dcf_numbers.json (carried in the block at build time)
    # — the traded cap, on the same basis as dcf_engine.market_cap_est
    # (2026-10-18 ADS fix). No ratio recorded: the plain product, unchanged.
    ads_ratio = d.get("ads_ratio")
    ads_ratio = ads_ratio if (_num(ads_ratio) and ads_ratio > 0) else None
    market_cap = price * shares / ads_ratio if (_num(price) and _num(shares) and ads_ratio) else (price * shares if (_num(price) and _num(shares)) else None)
    market_cap_basis = f"{price} × {shares:,.0f} shares ({shares_src}" + (f" ÷ ADS ratio {ads_ratio}" if ads_ratio else "") + (f", as of {shares_as_of})" if shares_as_of else ")") if market_cap is not None else None
    legs = d.get("legs") if isinstance(d.get("legs"), dict) else {}
    yield_basis = dict(d.get("yield_basis")) if isinstance(d.get("yield_basis"), dict) else {}
    values = {}
    cross = num_cur != PRICE_CURRENCY or bool(unit_unrecorded)
    cross_note = ((f"not computed: this block was written before the one-currency rule (2026-10-19) and does not record the currency of its "
                   f"DPS and flows — they may be {PRICE_CURRENCY} or {unit_unrecorded}, the currency this file reports in — so no yield is "
                   f"computed until the file's next refresh") if unit_unrecorded and not currency and not d.get("currency") else
                  f"not computed: the numerator is filed in {num_cur} and the price is in {PRICE_CURRENCY} (no FX conversion in this file)" if cross else None)
    for name in YIELD_LEGS:
        yb = yield_basis.get(name)
        if not isinstance(yb, dict):
            values[name] = None
            continue
        total = yb.get("numerator")
        values[name] = _ratio(total, market_cap) if (market_cap and total is not None and not cross) else None
        yb = dict(yb, denominator=market_cap_basis)
        if total is not None:  # a filed numerator: its bound is stated only next to a market cap
            yb = _with_note_after_denominator(yb, YIELD_BOUND_NOTES[yb["bound"]] if (market_cap and yb.get("bound") in YIELD_BOUND_NOTES) else None)
        yield_basis[name] = yb
    dps_ttm, dps_ttm_basis = d.get("dps_ttm"), d.get("dps_ttm_basis")
    # dps_ttm is filed per ordinary share; against a per-ADS price the
    # numerator scales by the same ratio (per-ADS DPS = per-share DPS x
    # ordinary shares per ADS), else the yield is off by exactly the ratio
    # (LTM at 2000: shown 0.0010% for a true 2.04%).
    dps_yield_num = dps_ttm * ads_ratio if (ads_ratio and _num(dps_ttm)) else dps_ttm
    values["dividend_yield"] = _ratio(dps_yield_num, price) if (_num(price) and price > 0 and not cross) else None
    if isinstance(yield_basis.get("dividend_yield"), dict):
        denom = f"price {price} ({price_source})" if _num(price) else None
        if denom is not None and ads_ratio:
            denom += f"; DPS × ADS ratio {ads_ratio} (per-ADS basis)"
        yield_basis["dividend_yield"] = dict(yield_basis["dividend_yield"], denominator=denom)
    # 5.4.4 review fix: a display-ready figure per yield so no consumer (the
    # Dividends tab, the ranking row) can print a partial numerator bare —
    # the bound is in the label ("≥ 2.66%", "≤ 6.1%", "≈ 4.4% (incomplete)")
    yields_display = {}
    for name in YIELD_KEYS:
        value = values[name]
        yb = yield_basis.get(name) if isinstance(yield_basis.get(name), dict) else {}
        bound = yb.get("bound") if value is not None else None
        prefix = {"exact": "", "lower": "≥", "upper": "≤", "indeterminate": "≈"}.get(bound, "")
        if value is None:
            label = "—"
            if cross:
                yields_display[name] = {"value": None, "bound": None, "prefix": "", "label": label, "note": cross_note}
                continue
        else:
            label = (f"{prefix} " if prefix else "") + f"{value * 100:.2f}%" + (" (incomplete)" if bound == "indeterminate" else "")
        if name == "dividend_yield":
            note = dps_ttm_basis if value is not None else next(
                (n for n in notes if isinstance(n, str) and (n.startswith("dps_ttm") or n.startswith("no dividends-per-share"))), None)
        else:
            # 5.4.5 review (APP '≤ 2.78%' over an issuance leg described as "a
            # lower bound"): each leg's basis is phrased by what it does to THIS yield
            sign_of = dict(YIELD_LEGS[name])
            parts_n = []
            for k in (yb.get("partial") or []) + (yb.get("excluded") or []):
                if not isinstance(legs.get(k), dict):
                    continue
                b = str(legs[k].get("basis"))
                b = b[:-len(" — a lower bound")] if b.endswith(" — a lower bound") else b
                if k in (yb.get("excluded") or []):
                    eff = "left out, so this yield is a lower bound" if sign_of.get(k, 1) > 0 else "no deduction made, so this yield is an upper bound"
                else:
                    eff = "understated, so this yield is a lower bound" if sign_of.get(k, 1) > 0 else "the deduction is understated, so this yield is an upper bound"
                parts_n.append(f"{k}: {b} — {eff}" if value is not None else f"{k}: {legs[k].get('basis')}")
            parts_n += [f"{k}: filed below zero, read as the absolute amount" for k in (yb.get("sign_corrected") or {})]
            parts_n += [f"{k}: filed below zero as a net line, kept as filed" for k in (yb.get("kept_as_filed") or {})]
            note = "; ".join(parts_n) or (yb.get("note") if value is None else None)
        yields_display[name] = {"value": value, "bound": bound, "prefix": prefix, "label": label, "note": note or None}
    d.update({"price": price, "price_date": price_date, "price_source": price_source, "price_note": price_note,
              "market_cap": market_cap, "market_cap_basis": market_cap_basis,
              "dividend_yield": values["dividend_yield"], "buyback_yield": values["buyback_yield"],
              "net_buyback_yield": values["net_buyback_yield"], "shareholder_yield": values["shareholder_yield"],
              "yield_basis": yield_basis, "yields_display": yields_display, "notes": notes})
    return d


def repriceable(div):
    """Whether a dividends block carries what price_dividends reads (a block
    written from 5.4.4 on: yield_basis for every yield and yields_display).
    An older block is shown as written."""
    return (isinstance(div, dict) and isinstance(div.get("yield_basis"), dict) and isinstance(div.get("yields_display"), dict)
            and all(isinstance(div["yield_basis"].get(k), dict) for k in YIELD_KEYS))


UNIT_SLIP_FACTOR = 10  # two filings of the same period's DPS that disagree by ≥10x disagree on the unit, not the dividend
DPS_FY_FORMS = ("10-K", "10-K/A", "20-F", "20-F/A", "40-F", "40-F/A")  # annual reports and their amendments carry the FY DPS fact


def _near_power_of_ten(ratio):
    return ratio >= UNIT_SLIP_FACTOR and abs(math.log10(ratio) - round(math.log10(ratio))) < 0.01


def split_restatement(hi_es, lo_es, splits=None, refilings=None):
    """Is a two-valued filing history of one period's DPS a split restatement?
    hi_es / lo_es: the facts carrying the larger / smaller value. A forward
    split of ratio r re-files the period at value/r in every filing after the
    split (the smaller value is the newer basis); a reverse split the other
    way. Evidence, either: a filed ratio ≈ hi/lo (split events, direction-
    checked) dated before the newer group's first filing and within 800 days
    of it; or the filer's diluted share count re-filed ×≈hi/lo between the two
    groups (share_refilings). Returns (post_is_lo, description, evidence) or
    None; the older-basis filings must all precede the newer-basis ones.
    evidence (5.4.5): ("ratio_fact", date, ratio) or ("re_filed_counts",
    period_end, ratio, first_filing_on_the_new_basis) — ratio = new shares per
    old share. 5.4.6 review fix (WRB's June 2024 3-for-2 read as 1.50847 =
    0.89 / 0.59, two rounded DPS values): the ratio is the simplest whole-number
    ratio p/q (p, q ≤ 10) within 1% of the DPS ratio, else of the re-filed
    share-count factor, else the share-count factor itself — never the quotient
    of two rounded per-share values."""
    ratio = max(e["val"] for e in hi_es) / min(e["val"] for e in lo_es)
    f_hi, f_lo = [e.get("filed", "") for e in hi_es], [e.get("filed", "") for e in lo_es]
    for post_is_lo, old, new in ((True, f_hi, f_lo), (False, f_lo, f_hi)):
        if max(old) >= min(new):
            continue
        target = ratio if post_is_lo else 1 / ratio
        for s in splits or []:
            d, r, cutoff = _split_cutoff(s)
            if abs(math.log(r) - math.log(target)) <= math.log(SPLIT_RATIO_TOL) and d < min(new) and _days(d, min(new)) <= 800:
                return post_is_lo, f"restated for the {_split_desc(d, r, cutoff)}", ("ratio_fact", d, r)
        for e, k, old_filed, new_filed in refilings or []:
            if abs(math.log(k) - math.log(target)) <= math.log(SPLIT_RATIO_TOL) and max(old) < new_filed <= min(new):
                snapped = snap_ratio(target) or snap_ratio(k)
                used = snapped[0] if snapped else k
                how = (f"{snapped[1][0]}-for-{snapped[1][1]} (the per-share values move ×{target:.4f}, the share count ×{k:.4f})" if snapped
                       else f"×{k:.4f} as the share count was re-filed (the per-share values move ×{target:.4f})")
                return post_is_lo, (f"restated for a share-basis change with no ratio fact filed — the diluted share count for the period ended {e} was re-filed ×{k:.2f} on {new_filed}; "
                                    f"read as {how}"), ("re_filed_counts", e, used, new_filed)
    return None


def dps_fy_facts(facts, tags, splits=None, refilings=None, restated=None, money=None):
    """FY-duration DPS facts on annual forms: ({period_end: dps}, {period_end:
    tag}, {period_end: filed}, notes). Like annual_series (tag priority per
    period, the latest filing wins) EXCEPT for a unit slip: when the filings
    that report one period disagree by a power of ten (GFI's FY2017 is 0.08
    in two 20-Fs and 8 in a third — cents tagged as dollars, never restated),
    the value most filings agree on wins, a tie going to the value closest in
    log terms to the tag's other fiscal years; the note names both and says
    which rule decided. Amended annual reports (10-K/A, 20-F/A, 40-F/A) count
    as filings of their period — GFI's 0.08 is in a 20-F/A and a 20-F, the 8
    in one 20-F. 5.4.3 review fix: before this the later filing's slip won
    the annual series. 5.4.4 review fix: a disagreement that IS a split
    restatement (split_restatement: a filed ratio ≈ the disagreement, or the
    diluted share count re-filed by it, between the two groups of filings —
    AVGO's FY2022 16.4 → 1.64 across the July 2024 10-for-1, NVDA's FY2023
    0.16 → 0.016, LRCX's FY2023 6.9 → 0.69) takes the latest filing on the
    new basis and says so; the majority rule applies only when no such
    share-basis evidence exists (GFI: shares unchanged). `splits`:
    [(date, ratio[, first_post_split_filing])]; `refilings`: share_refilings.
    5.4.5 review fix (CCI's FY2014 is 1.87 in the 10-K filed 2015-02-19 and
    1870 in the 10-Ks filed 2016-02-22 and 2017-02-22 — a 1000x slip the filer
    carried into two later comparatives, so it wins the count): before the
    majority rule, each power-of-ten group is checked against that year's own
    quarterly facts (the same tag's three-month facts inside the fiscal year,
    summed) and the tag's other fiscal years (log median); when exactly one group
    is within 3x of every reference and every other group is ≥10x from all of
    them, that group wins whatever the count, and the note says so. A note is
    written for EVERY power-of-ten disagreement, also when the value used is the
    latest filing's. `restated` (optional list) receives (period_end, evidence)
    for each split restatement read here (split_restatement's evidence)."""
    vals, tag_by, filed_by, notes = {}, {}, {}, []
    restated_out = restated
    for taxonomy, tag in _pairs(tags):
        tf = facts.get("facts", {}).get(taxonomy, {})
        if tag not in tf:
            continue
        units = tf[tag].get("units", {})
        for unit_key in _units_pref(units, money):
            by_end = {}
            for e in units[unit_key]:
                if e.get("fp") != "FY" or e.get("form", "") not in DPS_FY_FORMS:
                    continue
                end, start = e.get("end"), e.get("start")
                if not end or not start or not (330 <= _days(start, end) <= 380) or not _num(e.get("val")):
                    continue
                by_end.setdefault(end, []).append(e)
            latest_by_end = {end: max(es, key=lambda e: e.get("filed", "")) for end, es in by_end.items()}
            three_month = {}
            for e in units[unit_key]:
                if e.get("start") and e.get("end") and _num(e.get("val")) and DPS_DIRECT_WINDOW[0] <= _days(e["start"], e["end"]) <= DPS_DIRECT_WINDOW[1]:
                    prev = three_month.get((e["start"], e["end"]))
                    if prev is None or e.get("filed", "") > prev.get("filed", ""):
                        three_month[(e["start"], e["end"])] = e
            for end, es in by_end.items():
                if end in vals:
                    continue
                chosen = latest_by_end[end]
                positive = [e for e in es if e["val"] > 0]
                if len({round(e["val"], 9) for e in positive}) > 1:
                    hi, lo = max(e["val"] for e in positive), min(e["val"] for e in positive)
                    hi_es = [e for e in positive if round(e["val"], 9) == round(hi, 9)]
                    lo_es = [e for e in positive if round(e["val"], 9) == round(lo, 9)]
                    restated = split_restatement(hi_es, lo_es, splits, refilings) if len({round(e["val"], 9) for e in positive}) == 2 else None
                    if restated:
                        post_is_lo, why, evidence = restated
                        if restated_out is not None:
                            restated_out.append((end, evidence))
                        post, pre = (lo_es, hi_es) if post_is_lo else (hi_es, lo_es)
                        chosen = max(post, key=lambda e: e.get("filed", ""))

                        def _desc2(g):
                            return ", ".join(f"{e.get('form')} filed {e.get('filed')}" for e in sorted(g, key=lambda e: e.get("filed", "")))
                        notes.append(f"annual_dps: FY DPS for the period ended {end} is filed as {pre[0]['val']:g} ({_desc2(pre)}) and as {chosen['val']:g} ({_desc2(post)}) — "
                                     f"{why}; {chosen['val']:g} used (the latest filing on the new share basis, {tag})")
                    elif _near_power_of_ten(hi / lo):
                        groups = {}
                        for e in positive:
                            groups.setdefault(round(e["val"], 9), []).append(e)
                        others = [latest_by_end[x]["val"] for x in latest_by_end if x != end and latest_by_end[x]["val"] > 0]
                        centre = statistics.median(math.log10(v) for v in others) if others else None
                        best = max(groups.items(), key=lambda kv: (len(kv[1]), -(abs(math.log10(kv[0]) - centre) if centre is not None else 0), max(e.get("filed", "") for e in kv[1])))
                        majority = all(len(best[1]) > len(g) for k, g in groups.items() if k != best[0])
                        rule = ("the value most filings agree on" if majority else
                                ("the value closest to the tag's other fiscal years (the filings split evenly)" if centre is not None else
                                 "the value in the latest filing among an even split"))
                        # 5.4.5: the year's own quarterly facts and the tag's other fiscal years as references
                        start = es[0].get("start")
                        qy = sorted((k2, e2["val"]) for k2, e2 in three_month.items() if start <= k2[0] and k2[1] <= end and e2["val"] > 0)
                        refs = []
                        if len(qy) >= 2:
                            refs.append((f"that year's {len(qy)} quarterly facts (sum {sum(v for _, v in qy):g})", sum(v for _, v in qy)))
                        if centre is not None:
                            refs.append((f"the tag's other fiscal years (median {10 ** centre:.4g})", 10 ** centre))
                        near = [k for k in groups if refs and all(abs(math.log10(k) - math.log10(r)) < math.log10(3) for _, r in refs)]
                        if len(near) == 1 and near[0] != best[0] and all(all(abs(math.log10(k) - math.log10(r)) >= 1 for _, r in refs) for k in groups if k != near[0]):
                            repeated = any(len(g) > 1 for k, g in groups.items() if k != near[0])
                            best = (near[0], groups[near[0]])
                            rule = (f"the value consistent with {' and '.join(t for t, _ in refs)} — the other value is a unit slip"
                                    + (" the filer repeated in later comparatives, so it wins the count but not the arithmetic" if repeated else ""))
                        chosen = max(best[1], key=lambda e: e.get("filed", ""))

                        def _desc(g):
                            return ", ".join(f"{e.get('form')} filed {e.get('filed')}" for e in sorted(g, key=lambda e: e.get("filed", "")))
                        notes.append(f"annual_dps: FY DPS for the period ended {end} is filed as {chosen['val']:g} ({_desc(best[1])}) and as "
                                     + "; ".join(f"{k:g} ({_desc(g)})" for k, g in groups.items() if k != best[0])
                                     + f" — the filings disagree by a power of ten (a unit slip, {tag}); {chosen['val']:g} used, {rule}")
                vals[end], tag_by[end], filed_by[end] = chosen["val"], tag, chosen.get("filed")
    return vals, tag_by, filed_by, notes


def fallback_share_count(qrows, annual, reason=None, anchor=None):
    """(count, as_of, source) — the share count for the market cap when no
    undimensioned instant count exists in companyfacts (a dual-class filer's
    cover-page and balance-sheet counts are class-dimensioned and dropped by
    the API — TKO). The latest filed (non-derived) quarterly diluted
    weighted-average count is used, unless another recent filed diluted count
    (the latest four quarterly rows or the latest fiscal year) exceeds it by
    more than 20%: a diluted count excludes antidilutive / if-converted
    shares period by period (TKO's Q2 2026 count is 75.9M against 194.6M the
    quarter before), so the count that covers the shares the dividends and
    buybacks are paid on is the LATEST filed count that is within 20% of the
    largest recent one (TKO: Q1 2026's 194.6M, not Q3 2025's 199.1M — a
    buyback year's newest consistent count, not its oldest). Every candidate
    is named in `source`. None when no diluted count exists. `reason`
    replaces the default why-text (build_dividends passes the stale instant
    count it rejected — that filer DID file an undimensioned count).
    `anchor` (build_dividends passes the engine's validated diluted count,
    dcf_numbers.json shares_diluted_latest, when the fallback replaces a stale
    instant count): a pick more than 20% from it (SHARE_ANCHOR_TOL) that no
    other recent filed count (another period) corroborates within 20% is a
    one-period outlier and gives way to the latest candidate within 20% of
    the anchor, and `source` names both — ECHO's Q2 2026 diluted count,
    351,622,000, carries the if-converted shares of a one-time-gain quarter
    against Q1 2026's 289,014,000 and the engine's 287,589,000 (verifier
    round 2). A corroborated pick stands: SF's two 2026 quarters (163.4M,
    161.6M) are a level the engine's pre-split FY2025 count (110.05M) has
    not caught up with. With no candidate within 20% of the anchor the pick
    stands too (the scale-band check in build_dividends still applies)."""
    cands = []
    for r in (qrows or [])[-4:]:
        if _num(r.get("shares_diluted")) and r["shares_diluted"] > 0 and not r.get("shares_diluted_derived"):
            cands.append((r["shares_diluted"], r["period_end"], f"quarter ended {r['period_end']}"))
    for r in (annual or [])[-1:]:
        if _num(r.get("shares_diluted")) and r["shares_diluted"] > 0:
            cands.append((r["shares_diluted"], r["period_end"], f"FY{r.get('fy')} (period ended {r['period_end']})"))
    if not cands:
        return None
    latest = max(cands, key=lambda c: c[1])
    biggest = max(cands, key=lambda c: c[0])
    why = reason or ("weighted-average diluted count, fallback: no undimensioned period-end / cover-page share count in EDGAR companyfacts "
                     "(a dual-class filer's cover-page and balance-sheet counts are class-dimensioned and dropped by the API)")
    if biggest[0] > 1.2 * latest[0]:
        # the newest count that is not an exclusion anomaly: latest by date among those within 20% of the largest
        consistent = max((c for c in cands if 1.2 * c[0] >= biggest[0]), key=lambda c: c[1])
        pick = (consistent[0], consistent[1], (f"{consistent[2]} {why}; the latest quarter's own diluted count ({latest[0]:,.0f}, {latest[2]}) is >20% lower — "
                                               f"a diluted count excludes antidilutive / if-converted shares period by period, so the latest recent filed count "
                                               f"consistent with the most inclusive one ({biggest[0]:,.0f}, {biggest[2]}) is used"))
    else:
        pick = (latest[0], latest[1], f"{latest[2]} {why}")
    if _num(anchor) and anchor > 0 and not (1 / SHARE_ANCHOR_TOL <= pick[0] / anchor <= SHARE_ANCHOR_TOL):
        near = [c for c in cands if 1 / SHARE_ANCHOR_TOL <= c[0] / anchor <= SHARE_ANCHOR_TOL]
        corroborated = any(c[1] != pick[1] and 1 / SHARE_ANCHOR_TOL <= c[0] / pick[0] <= SHARE_ANCHOR_TOL for c in cands)
        if near and not corroborated:
            c = max(near, key=lambda c: c[1])
            return c[0], c[1], (f"{c[2]} {why}; the count otherwise picked ({pick[0]:,.0f}, as of {pick[1]}) is {pick[0] / anchor:,.2f}x the engine's "
                                f"validated diluted count ({anchor:,.0f}, dcf_numbers.json shares_diluted_latest) — more than 20% from it, so the latest "
                                f"recent filed diluted count within 20% of the engine's is used")
    return pick


def dividends_inputs(facts, money=None):
    """The filed DPS series the dividends block reads — quarterly direct facts
    (declared / paid) and FY-duration facts (declared / paid, unit-slip and
    split-restatement aware: dps_fy_facts) — restated for filed stock splits
    (one event per split however many context dates it is tagged at; the
    basis changes at the first filing that re-files the diluted share count,
    not at the ratio fact's date: apply_splits). Returns (dps_q, dps_fy, meta)
    with meta = {splits: [(date, ratio, first_post_split_filing)], split_notes: [...]}.
    money= (money_unit): DPS facts in that currency's per-share unit only."""
    fy_starts = core_fy_starts(facts, money=money)
    dps_q = {"declared": quarterly_by_tag(facts, DUR["dps_declared"], derive=False, direct_window=DPS_DIRECT_WINDOW, fy_starts=fy_starts, money=money),
             "paid": quarterly_by_tag(facts, DUR["dps_paid"], derive=False, direct_window=DPS_DIRECT_WINDOW, fy_starts=fy_starts, money=money)}
    notes, splits, dups, dropped = [], [], [], []
    events = split_events(facts, duplicates=dups)
    for d, r, folded in dups:
        notes.append(f"split ratio {r:g} is tagged at {len(folded) + 1} context dates ({', '.join([d] + folded)}) — one split, read once at {d}")
    refilings = share_refilings(facts)
    directed = split_direction(events, _shares_with_filed(facts), dropped=dropped)
    for d, r, ev in dropped:
        notes.append(f"split ratio {r:g} tagged at {d} is left out — {ev}; it is the same split as the one already read, not a second one")
    cutoffs = split_filing_cutoffs([(d, used) for d, r, used, ev in directed], refilings)
    # 5.4.6: the same ratio tagged again within 400 days, further apart than
    # split_events folds (WCN: 1.5 at 2017-04-26 and again at 2018-03-31), is a
    # second split only when some filing re-files a value that was ALREADY on
    # the first split's basis by the ratio again; otherwise it is the first
    # split tagged twice, and compounding it would divide every older DPS fact
    # by 2.25 instead of 1.5
    deduped = []
    for d, r, used, ev in directed:
        prev = deduped[-1] if deduped else None
        if prev and abs(math.log(prev[2]) - math.log(used)) <= math.log(SPLIT_RATIO_TOL) and 0 < _days(prev[0], d) <= 400:
            c1 = cutoffs.get(prev[0], (prev[0], None))[0]
            if not any(abs(math.log(k) - math.log(used)) <= math.log(SPLIT_RATIO_TOL) and old_filed >= c1 and -200 <= _days(d, new_filed) <= 400
                       for e, k, old_filed, new_filed in refilings):
                notes.append(f"split ratio {r:g} tagged at {d} is left out — the same ratio as the split tagged at {prev[0]} ({_days(prev[0], d)} days earlier), and no filing "
                             f"re-files a value already on that split's basis (first filed {c1}) by it again: one split tagged twice, not two")
                continue
        deduped.append((d, r, used, ev))
    directed = deduped
    # 5.4.6: a ratio fact the filed share counts do not bear out is not a split
    # (CFG tags 6 at 2021-12-31 and its diluted count moves ×0.95; DXCM tags its
    # June 2022 4-for-1 at 2019-12-31 and 2020-12-31 too): across the first
    # filing on the new basis (else the ratio fact's date) the diluted count
    # must move closer to the ratio than to no change. Codex review of PR #2:
    # the counts are the fiscal-year AND quarterly ones (the same evidence
    # statements.py's split_borne_out reads) — Q tags the 0.5 spin-off
    # distribution ratio (one Qnity share per two DuPont shares) on its Q1 2026
    # 10-Q; no fiscal year has been filed since, so the annual counts alone
    # said nothing and the FY2025 DPS of $0.14 was doubled to $0.28, while the
    # quarterly count went 209.8M (FY2025) -> 210.3M (Q1 2026): no split
    counts = diluted_counts_with_filed(facts) if directed else {}
    supported = []
    for d, r, used, ev in directed:
        cut = cutoffs.get(d, (None, None))[0] or d
        mv = share_count_move(counts, cut)
        if mv and abs(math.log(used)) >= math.log(SHARE_REFILE_MIN) and abs(math.log(mv[0])) < abs(math.log(mv[0]) - math.log(used)):
            notes.append(f"split ratio {r:g} tagged at {d} is left out — {mv[1]}: the share counts do not move by the ratio, so it is not a split of the common shares "
                         "(an exchange or conversion ratio, or a split tagged at an earlier context date)")
            continue
        supported.append((d, r, used, ev))
    directed = supported
    for d, r, used, ev in directed:
        cutoff, cev = cutoffs.get(d, (None, None))
        splits.append((d, used, cutoff))
        if used != r:
            notes.append(f"split ratio {r:g} filed for {d} read as {used:g} new shares per old share — {ev}")
        if cutoff and cutoff != d:
            notes.append(f"split {used:g} tagged at {d}: facts filed before {cutoff} are on the pre-split basis — {cev}")
    restated = []
    fy = {b: dps_fy_facts(facts, DUR[f"dps_{b}"], splits=splits, refilings=refilings, restated=restated, money=money) for b in ("declared", "paid")}
    dps_fy = {b: fy[b][0] for b in fy}
    fy_filed = {b: fy[b][2] for b in fy}
    for b in fy:
        notes.extend(fy[b][3])
    # 5.4.5 review fix (EXPE's December 2011 1-for-2 reverse split has no ratio
    # fact): when a period's FY DPS AND the filer's diluted share count were both
    # re-filed by the same factor between two groups of filings, that is a split
    # the filings themselves evidence — it is applied like a filed ratio (every
    # per-share fact last filed before the first filing on the new basis is
    # restated, quarterly facts included) and listed in split_adjustments with
    # source "re_filed_counts". Before this only the FY fact was restated and the
    # quarterly history mixed bases (2010 quarters 0.07 beside 2011's 0.14).
    for end, ev in sorted(restated, key=lambda x: x[1][-1] if x[1][0] == "re_filed_counts" else ""):
        if ev[0] != "re_filed_counts":
            continue
        _, e, k, new_filed = ev
        if any(abs(math.log(_split_cutoff(s)[1]) - math.log(k)) <= math.log(SPLIT_RATIO_TOL) and abs(_days(_split_cutoff(s)[2], new_filed)) <= 800 for s in splits):
            continue
        splits.append((new_filed, k, new_filed, "re_filed_counts"))
        notes.append(f"share-basis change with no ratio fact filed: the FY DPS for the period ended {end} and the diluted share count for the period ended {e} were both re-filed by the same factor "
                     f"(first on {new_filed}) — read as a {_split_desc(new_filed, k)}; every per-share fact last filed before {new_filed} is restated by it")
    notes.extend(original_quarterly_dps(facts, dps_q, splits, money=money))
    dps_q, dps_fy, adj_notes = apply_splits(dps_q, dps_fy, fy_filed, splits)
    # 5.4.6 review fix (WRB): the annual diluted counts on today's share basis
    # (a count last filed before a split's first post-split filing × the
    # ratio), so the unfiled-split guard (basis_breaks) never reads a known
    # split as a share move — WRB's FY2021 count (filed before the 2024 3-for-2)
    # against FY2022's (filed after it) is ×1.5 for that reason alone
    shares_by_end = {e: v * split_factor(f, splits) for e, (v, f) in _shares_with_filed(facts).items() if _num(v)}
    return dps_q, dps_fy, {"splits": splits, "split_notes": notes + adj_notes, "shares_by_end": shares_by_end}


def original_quarterly_dps(facts, dps_q, splits, money=None):
    """5.4.6 review blocker (FTI's 10-K filed 2021-03-05 re-tags Q1 2019 at
    0.52, the year-to-date total, in a three-month context; HPQ's 10-K filed
    2019-12-12 tags 0.53 and 0.64 YTD values as quarters; WRB's 10-Q filed
    2021-08-02 re-files Q2 2020 at the six-month 0.23): when the filings of
    one quarter's DPS disagree — different filed values that also differ on
    today's share basis (split_factor; values within rounding are one value) —
    the value is chosen by the filer's own arithmetic: the one equal to the
    same tag's year-to-date fact minus the year-to-date fact a quarter shorter
    (for a first quarter: the six-month fact minus the second quarter). WRB's
    Q2 2021 shows why the first filing is not always right: its 10-Q tagged
    0.12 while the later six-month 0.75 − Q1 0.12 gives the 0.63 a later
    comparative carries. When the year-to-date facts decide nothing (none
    filed, or both values fit), the filing that first reported the quarter is
    used — later 10-Ks and comparatives are where the mis-tags are.
    Every quarter whose value the year-to-date arithmetic confirms gets
    `ytd_confirmed` (the facts used) — build_dividends uses it to tell a
    full-year fact below its quarters (IBKR files one quarter's 0.025 with the
    FY context; its quarters are confirmed by the 6M / 9M facts) from mis-tagged
    quarters (FTI). Mutates dps_q (val, filed, ytd_confirmed); returns notes."""
    notes = []

    def adj(x):
        return x["val"] / split_factor(x["filed"], splits)

    by_tag = {}
    for b in ("declared", "paid"):
        for taxonomy, tag in _pairs(DUR[f"dps_{b}"]):
            for unit_key, es in (facts.get("facts", {}).get(taxonomy, {}).get(tag, {}).get("units") or {}).items():
                if money is not None and _unit_currency(unit_key) not in (None, money):
                    continue
                for x in es:
                    if (x.get("start") and x.get("end") and x.get("filed") and _num(x.get("val")) and x.get("form", "") in DURATION_FORMS
                            and DPS_DIRECT_WINDOW[0] <= _days(x["start"], x["end"]) <= 380):
                        by_tag.setdefault(tag, []).append(x)
    by_tag_end = {tag: {} for tag in by_tag}
    for tag, xs in by_tag.items():
        for x in xs:
            by_tag_end[tag].setdefault(x["end"], []).append(x)

    for b in ("declared", "paid"):
        changed = []
        for e, d in (dps_q.get(b) or {}).items():
            if not _num(d.get("val")) or not d.get("tag") or not d.get("filed") or d["tag"] not in by_tag:
                continue
            ends = by_tag_end[d["tag"]]
            three = [x for x in ends.get(e, []) if _days(x["start"], e) <= DPS_DIRECT_WINDOW[1]]
            if not three:
                continue
            tol = 0.0051 / max(1.0, min(split_factor(x["filed"], splits) for x in three))

            def corroborated(c):
                for A in ends.get(e, []):
                    if _days(A["start"], e) > DPS_DIRECT_WINDOW[1]:
                        for B in by_tag[d["tag"]]:
                            if B["start"] == A["start"] and DPS_DIRECT_WINDOW[0] <= _days(B["end"], e) <= DPS_DIRECT_WINDOW[1] and abs(adj(A) - adj(B) - c) <= tol:
                                return f"{A['start']}..{e} − {B['start']}..{B['end']}"
                for x in three:  # a first quarter: the six-month fact minus the second quarter
                    for A in by_tag[d["tag"]]:
                        if A["start"] == x["start"] and DPS_DIRECT_WINDOW[0] <= _days(e, A["end"]) <= DPS_DIRECT_WINDOW[1]:
                            for N in ends.get(A["end"], []):
                                if N["start"] > e and _days(N["start"], N["end"]) <= DPS_DIRECT_WINDOW[1] and abs(adj(A) - adj(N) - c) <= tol:
                                    return f"{A['start']}..{A['end']} − {N['start']}..{N['end']}"
                return None

            groups = []  # [(adjusted value, [facts])], values within rounding merged
            for x in sorted(three, key=lambda x: x["filed"]):
                g = next((g for g in groups if abs(g[0] - adj(x)) <= tol), None)
                if g:
                    g[1].append(x)
                else:
                    groups.append((adj(x), [x]))
            raw_same = len({round(x["val"], 9) for x in three}) == 1  # one filed value: a split that did not restate it is no disagreement
            if len(groups) >= 2 and not raw_same:
                fits = [(g, corroborated(g[0])) for g in groups]
                fits = [(g, why) for g, why in fits if why]
                if len(fits) == 1:
                    pick, rule = fits[0][0], f"the value the year-to-date facts give ({fits[0][1]})"
                else:
                    pick, rule = groups[0], "the filing that first reported the quarter (the year-to-date facts do not decide)"
                if not any(x["filed"] == d["filed"] and x["val"] == d["val"] for x in pick[1]):
                    fact = max(pick[1], key=lambda x: x["filed"])
                    changed.append((e, fact["val"], fact["filed"], d["val"], d["filed"], rule))
                    d["val"], d["filed"] = fact["val"], fact["filed"]
            cur = d["val"] / split_factor(d["filed"], splits)
            d["ytd_confirmed"] = corroborated(cur)
            d["first_filed"] = min((x["filed"] for x in three if abs(adj(x) - cur) <= tol), default=d["filed"])
        if changed:
            changed.sort()
            ex = "; ".join(f"{e}: {v0:g} (filed {fd0}) used, not {v1:g} (filed {fd1}) — {rule}" for e, v0, fd0, v1, fd1, rule in changed[:6])
            notes.append(f"quarterly DPS ({b}): {len(changed)} quarter(s) filed at different values on the same share basis ({ex}{'; …' if len(changed) > 6 else ''}) — "
                         "later 10-Ks and comparatives sometimes tag a year-to-date or annual value with a three-month context")
    return notes


def share_count_move(shares_with_filed, date):
    """(observed move, evidence) of the diluted count across `date`: the last
    period whose count was last filed before it vs the first later period
    filed on or after it (as split_direction reads it; a count filed in
    thousands against one in shares is normalised). Keys are fiscal-year ends
    ({end: (val, filed)}, _shares_with_filed) or (start, end) periods
    ({(start, end): (val, filed)}, diluted_counts_with_filed: fiscal years and
    quarters); where several periods end on one date the shortest is read
    (the quarter, not the year-to-date or the year around it). None without both."""
    def _end(k):
        return k[1] if isinstance(k, tuple) else k

    def _span(k):
        return _days(k[0], k[1]) if isinstance(k, tuple) else 365

    def _label(k):
        sp = _span(k)
        return "FY" if sp >= 330 else ("quarter" if sp <= 120 else "year-to-date period")

    pre = [(_end(k), _span(k), k, v) for k, (v, f) in shares_with_filed.items() if f and f < date and _num(v) and v > 0]
    post = [(_end(k), _span(k), k, v) for k, (v, f) in shares_with_filed.items() if f and f >= date and _num(v) and v > 0]
    if not pre:
        return None
    last_end = max(x[0] for x in pre)
    post = [x for x in post if x[0] > last_end]
    if not post:
        return None
    first_end = min(x[0] for x in post)
    e0, _, k0, s0 = min((x for x in pre if x[0] == last_end), key=lambda x: (x[1], str(x[2])))
    e1, _, k1, s1 = min((x for x in post if x[0] == first_end), key=lambda x: (x[1], str(x[2])))
    obs = s1 / s0
    k3 = round(-math.log10(obs) / 3)
    if k3 and abs(math.log10(obs)) >= 2.5:
        obs *= 1000.0 ** k3
    return obs, f"diluted shares {s0:,.0f} ({_label(k0)} ending {e0}, last filed before {date}) → {s1:,.0f} ({_label(k1)} ending {e1}), ×{obs:.2f}"


def diluted_counts_with_filed(facts):
    """{(start, end): (diluted weighted shares, filed)} — every fiscal-year AND
    quarter count (3-month or year-to-date) filed in shares, each period's
    newest filing (the evidence statements.py's split_borne_out reads)."""
    out = {}
    for (s, e), (v, tag, unit, filed, accn) in duration_facts(facts, DUR["shares_diluted"]).items():
        if unit == "shares" and filed and _num(v) and v > 0 and 60 <= _days(s, e) <= 380:
            out[(s, e)] = (v, filed)
    return out


def _shares_with_filed(facts):
    """{period_end: (diluted shares, filed)} for the annual diluted share count."""
    vals, _, _, filed = annual_series(facts, DUR["shares_diluted"], True, with_filed=True)
    return {e: (v, filed.get(e)) for e, v in vals.items()}


def build_ttm(qrows, intang_ttm=None):
    """The trailing four quarters. intang_ttm (intangible_capex_ttm): the TTM
    intangible-capex leg the engine's way — fcf / oe_conservative are then
    OCF − PP&E capex − it [− SBC] over the four quarters rather than the sum of
    the quarterly rows (whose legs are not floored); None keeps the sum."""
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
    if _num(intang_ttm) and out["fcf"] is not None and out["ocf"] is not None and out["capex"] is not None:
        out["fcf"] = _whole(out["ocf"] - out["capex"] - intang_ttm)
        out["oe_conservative"] = _whole(out["fcf"] - out["sbc"]) if out["sbc"] is not None else None
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


def eight_k_count(dates, as_of):
    """8-K filings dated in the 365 days to `as_of` (a date), both ends included."""
    lo, hi = (as_of - datetime.timedelta(days=365)).isoformat(), as_of.isoformat()
    return sum(1 for d in dates if isinstance(d, str) and lo <= d <= hi)


def build_profile(cik, facts, eight_k_dates=None):
    """The EDGAR submissions profile. eight_k_count_12m is counted to ET_TODAY;
    a list passed as eight_k_dates receives every 8-K filing date in the feed
    so write_fundamentals can recount the window to an earlier as_of."""
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
    dates8k = []
    for i, form in enumerate(forms):
        fd = fds[i] if i < len(fds) else ""
        if form in ("10-K", "10-K/A", "20-F", "40-F", "10-Q", "10-Q/A") and form.replace("/A", "") not in latest:
            acc = accs[i].replace("-", "") if i < len(accs) else ""
            doc = docs[i] if i < len(docs) else ""
            latest[form.replace("/A", "")] = {"filed": fd, "period": rds[i] if i < len(rds) else "",
                                              "url": f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc}/{doc}" if acc and doc else None}
        if form == "8-K" and fd:
            dates8k.append(fd)
    prof["latest_filings"] = latest
    prof["eight_k_count_12m"] = eight_k_count(dates8k, ET_TODAY)
    if eight_k_dates is not None:
        eight_k_dates.extend(dates8k)
    prof["edgar_url"] = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik:010d}&type=10-K&dateb=&owner=include&count=40"
    return prof


def _prev_file(path):
    """The fundamentals.json already on disk (dict), else None."""
    try:
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        return d if isinstance(d, dict) else None
    except (OSError, ValueError):
        return None


def write_fundamentals(path, out, eight_k_dates=None, prev=None):
    """Write `out` to path (json.dump indent=1, atomically) unless the file
    already holds the same content apart from `as_of`. Returns True when written.

    The committed file is a snapshot as of its own `as_of`. Its one rolling
    figure, profile.eight_k_count_12m (8-Ks in the 365 days to the run date),
    changes when an old 8-K ages out of the window with no filing at all
    (verifier, PR #2 repair round: Q 13 -> 12 and HBAN 31 -> 29 between
    2026-10-15 and 2026-10-20 on the same companyfacts and submissions, so
    both files were rewritten). So the count is first compared as of the
    file's own as_of: when that is the only other difference the file stays —
    as_of and its 8-K count still agree — and a file rewritten for any other
    reason carries the count to the run date. An 8-K filed after the file's
    as_of is therefore picked up with the next content change, not on its own."""
    prev = prev if prev is not None else _prev_file(path)
    prof = out.get("profile")
    try:
        then = datetime.date.fromisoformat(str((prev or {}).get("as_of")))
    except ValueError:
        then = None
    if (then is not None and eight_k_dates is not None and isinstance(prof, dict) and "eight_k_count_12m" in prof
            and then.isoformat() != out.get("as_of") and then <= ET_TODAY):
        as_then = dict(out, as_of=then.isoformat(), profile=dict(prof, eight_k_count_12m=eight_k_count(eight_k_dates, then)))
        if same_content(path, as_then, volatile=FUNDAMENTALS_VOLATILE):
            return False
    return write_json_if_changed(path, out, volatile=FUNDAMENTALS_VOLATILE, indent=1)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__); sys.exit(2)
    ticker = args[0].upper()
    folder = f"{BASE}/{ticker}"
    nums = {}
    try:
        with open(f"{folder}/dcf_numbers.json", encoding="utf-8") as f:
            nums = json.load(f)
    except Exception:
        pass
    cik = resolve_cik(ticker, nums)
    if cik is None:
        print(f"fundamentals.py: NO_CIK for {ticker}", file=sys.stderr); sys.exit(2)
    facts = get_json(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json")
    warnings = []
    money = money_unit(facts)  # ruling-sheet Q8 bug 3: one money unit for every series, leg and per-share figure in the file
    annual, tag_summary, currency = build_annual(facts, money=money)
    quarterly = build_quarterly(facts, warnings=warnings, revenue_mode=(tag_summary.get("revenue_mode") or ["standard"])[0], annual=annual, money=money)
    ttm = build_ttm(quarterly, intang_ttm=intangible_capex_ttm(facts, money, quarterly, fy_starts=core_fy_starts(facts, money=money)))
    eight_k_dates = []
    profile = build_profile(cik, facts, eight_k_dates=eight_k_dates)
    dps_q, dps_fy, dmeta = dividends_inputs(facts, money=money)
    path = f"{folder}/fundamentals.json"
    prev = _prev_file(path)
    price, price_date, price_source = _read_price(folder, (prev or {}).get("dividends"))
    flow_facts = {"dividends_paid": duration_facts(facts, DUR["dividends_paid"], money=money),
                  "buybacks": duration_facts(facts, DUR["buybacks"], money=money),
                  "share_issuance": combined_duration_facts(facts, DUR["share_issuance"], ISSUANCE_SUPERSETS, money=money)}
    filed_any = {k: bool(v) for k, v in flow_facts.items()}
    _ads = nums.get("ads_ratio")
    ctx = {"filed_any": filed_any, "flow_facts": flow_facts, "shares_instant": latest_share_count(facts),
           "ads_ratio": _ads.get("ratio") if isinstance(_ads, dict) else None,
           "latest_filed_period": {f: v.get("period") for f, v in (profile.get("latest_filings") or {}).items() if isinstance(v, dict)},
           "split_notes": dmeta["split_notes"], "splits": dmeta["splits"], "shares_by_end": dmeta.get("shares_by_end"), "warnings": warnings,
           "currency": money, "engine_shares": nums.get("shares_diluted_latest")}
    dividends = build_dividends(annual, quarterly, dps_q, dps_fy, price, price_date, price_source, ctx)
    _mw = money_unit_warning(pick_money_unit(money_entries(facts)))
    if _mw:
        warnings.append(_mw)
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
    file_status = "not written (--no-write)"
    if "--no-write" not in sys.argv:
        # committed file: rewritten only when something besides the run date
        # changed (_stable.py), so `as_of` = the day this content was produced
        file_status = "written" if write_fundamentals(path, out, eight_k_dates, prev) else "unchanged"
    summary = {"ticker": ticker, "cik": cik, "fundamentals_json": file_status, "annual_years": len(annual), "quarters": len(quarterly),
               "ttm_period": (ttm or {}).get("period_end"), "latest_filings": profile.get("latest_filings"), "warnings": warnings,
               "dividends": {k: dividends.get(k) for k in ("dps_ttm", "dps_ttm_basis", "dps_basis", "frequency", "frequency_basis", "dividend_yield",
                                                           "growth_years", "last_cut_fy", "dps_cagr_5y", "dividends_paid_ttm", "buybacks_ttm", "issuance_ttm",
                                                           "buyback_yield", "net_buyback_yield", "shareholder_yield", "shareholder_yield_basis", "shareholder_yield_complete",
                                                           "shares_outstanding", "shares_source", "market_cap", "price", "price_date", "price_note", "notes")}}
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
