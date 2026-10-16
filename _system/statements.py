#!/usr/bin/env python3
"""Full financial statements from EDGAR companyfacts (v6, 2026-10-14; review
round 2026-10-15) — the Financials tab's income statement, balance sheet,
cash-flow statement and derived metrics, stockanalysis-style, over the
company's WHOLE filing history.

Usage: python3 statements.py <TICKER> [--cik N] [--no-write] [--force]
       python3 statements.py --all [--force]          every folder with score.json
       (--cache DIR reads/writes the raw EDGAR JSON there instead of fetching
        when a cached copy exists — tests and offline verification)

Writes <TICKER>/statements.json; build_site.py copies it to
_daily/site/data/<T>.statements.json, which the app loads on demand when the
Financials tab opens (it is never embedded in the chat attachment).

Every figure is a filed value or plain arithmetic on filed values; nothing is
estimated. The tag lists are fundamentals.py's (DUR / INST) plus display-only
extras; the fiscal-period bookkeeping (_days, _g, _ratio, fy_labels,
core_fy_starts, the split machinery, resolve_cik, get_json) is imported. The
fact READERS are local because they need what fundamentals.py's collapse: the
whole filing history of every fact (which 10-K / 10-Q filed it, in which unit),
for the rules below.
- every period's value is the NEWEST filing's (a restatement re-files every
  year it covers, so a restated year and its neighbours share one basis),
  once three anomalies are dropped (warned): a filed 0 against non-zero
  filings of the period, a power-of-ten slip of another filing's value (10^3,
  10^6; the value consistent with the tag's other periods is kept), and a
  column shifted onto the adjacent period's value (HBAN's 2015 10-K);
- a cell's provenance is every accession that filed its value: annual growth
  is blank where the two years' values share no filing although some filing
  reported both years (two filing generations — the earlier year as
  originally reported, the later one restated), and FCF / owner's earnings /
  margins are blank where their inputs share no filing although a filing
  carries both (warned);
- one period, one date: a fiscal week-end and the calendar month-end a later
  comparative used (1-3 days apart) are merged onto the original filing's date;
- annual columns = every fiscal year the filer's FY-duration facts support
  (10-K / 20-F / 40-F) in ONE money unit per file (the unit
  most of the core FY facts are filed in, USD preferred on ties; convenience
  translations in another currency are ignored);
- quarterly columns = every derivable fiscal quarter: direct 3-month facts
  where filed, else year-to-date minus the prior year-to-date leg in the same
  fiscal year (flagged derived_quarterly), Q4 = FY minus the nine-month leg —
  only when every leg exists in the SAME tag (else the quarter is blank and
  flagged basis_break_quarterly), with BOTH legs taken from the same filing
  generation (the longer leg's fact
  from the first annual / quarterly filing on or after the shorter leg's last
  filing, so a fiscal year restated years later is never netted against a
  nine-month leg that was not) and in the same unit; per-share and
  weighted-average share lines are never derived by subtraction (a ratio has
  no YTD identity) except a fiscal Q4 BASIC share count, day-weighted from
  the FY average and the three filed quarters when they are mutually
  consistent; the Q4 DILUTED count only in a loss quarter (= that basic
  count: every potential share is antidilutive), else blank; Q4 EPS = FY EPS
  − the three filed quarters (not when the year's net-income quarters and
  the year are on different bases) — all marked derived;
- per-share and share-count lines are split-adjusted to today's share basis
  with the filed split ratios — ONE event per split however many comparative
  contexts its ratio is tagged in, a second same-ratio split a few years on
  kept separate (split_events_dedup), applied only when the share counts
  (fiscal years and quarters) bear it out, plus splits read from re-filed
  counts (a non-simple ratio — DFTX 1-for-15 — when a split-shares instant
  corroborates it) — and split_factor, the way the dividends block restates
  DPS;
- capex keeps one caption per series (the previous years' tag while the
  filer still files it), growth blank across a caption change;
- balance-sheet lines are instants: FY end, quarter end, and "ttm" = the
  latest quarter-end value (the app labels that column "Current");
- flow lines' ttm = the sum of the last four consecutive quarters when all
  four exist (shares: their duration-weighted average);
- growth_annual = YoY vs the prior consecutive fiscal year, growth_quarterly =
  YoY vs the quarter ending one year earlier; null when either side is
  missing or the base is not positive (ratio / pct lines carry no growth),
  and an annual cell is null across two filing generations (see above);
- a fiscal year whose four quarters do not sum to the fiscal-year figure
  (|sum − FY| > 1%: a restatement, reclassification or discontinued
  operations between filings) is flagged `basis_break_quarterly` on those
  quarters and the growth cells that straddle it are blanked;
- derived lines (ebitda, fcf, owner_earnings and every metric) are computed
  only from lines present in the SAME period; a component line the filer has
  never filed in any period (no short-term investments, no debt, no goodwill)
  counts as zero where the definition allows it, a component filed in other
  periods but not this one gives null — except SBC, which counts as zero for
  a period whose cash-flow statement (the filing that supplied the period's
  OCF) has no SBC line and no SBC-like caption at all. Capex is NEVER read as
  zero: no filed capex, no FCF and no owner's earnings. In a period whose
  cash-flow statement reports discontinued investing flows on their own
  line, FCF / owner's earnings use continuing OCF (capex is continuing-only
  there) and net margin continuing net income. Two lines that resolve
  to the same filed fact (same value, date and filing) are counted once.
  Totals are never synthesised from components.
- restricted cash (Codex review of PR #2): a balance-sheet cash cell filed
  only as the combined cash + restricted cash total
  (CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents) is shown
  as filed. Its restricted part is the difference from the same date's
  cash-only caption (CashAndCashEquivalentsAtCarryingValue) where a filing
  reports both with that total, or 0 where the two are equal (ZTS FY2025:
  the 2026 10-Qs file 2,450M of both, so 0 — both columns then agree), else
  a restricted-cash total filed for the date, else the current and
  noncurrent restricted captions summed. A positive part is shown on the
  "Restricted cash (included in cash above)" line in those cells only, and
  net cash, net cash per share and the ROIC proxy's invested capital use
  cash minus it — NTRS FY2025: 5,873.1M − 531.2M restricted, net cash
  2,521.6M → 1,990.4M, 13.53 → 10.68 per share. A combined cell nothing
  separates stays in those metrics, flagged `incl_restricted_*`, the line
  labelled "(some periods incl. restricted cash)", warned, and the growth
  cells across a change between the two bases blank (NTRS 2023-06-30 vs
  2022-06-30: −12.6% compared 1,584.7M without restricted cash to 1,814.0M
  with it).
Cash-flow lines are as filed: capex, buybacks, dividends, repayments,
acquisitions and investment purchases are POSITIVE amounts paid (a payment a
filing tagged negative is the filer's sign slip and is read as the absolute
amount, warned); each
cash-flow LINE carries `cf_sign` (+1 adds to cash, -1 reduces it) so the app
can present outflows as negatives.

--all cost rule: the small submissions API is read first and the name is
SKIPPED without touching the multi-megabyte companyfacts file when the
existing statements.json already records the newest 10-K / 10-Q / 20-F / 40-F
filing (`latest_filed`) AND its period is covered by the columns written
(`covered_through`), unless --force. EDGAR rules: the Muse User-Agent,
<= 10 requests/second, 3 attempts with backoff, 90 s timeout.

statements.json is committed: it is written through _stable.write_json_if_changed,
so a rebuild whose content differs from the file only in `as_of` leaves the file
untouched (`as_of` = the day the content was produced); --all reports written /
unchanged / skipped.
"""
import argparse
import bisect
import datetime
import glob
import json
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from fundamentals import (DUR, INST, DURATION_FORMS, core_fy_starts, _days, _g, _ratio, _num, fy_labels,  # noqa: E402
                          resolve_cik, get_json, split_direction, share_refilings, split_filing_cutoffs,
                          split_factor, _split_desc, _split_cutoff, _shares_with_filed, _units_pref)
from _stable import write_json_if_changed  # noqa: E402  (committed SEC file: no run-date-only rewrites)

BASE = os.environ.get("STOCKS_BASE") or os.path.dirname(HERE)
IF = "ifrs-full"
SOURCE = "SEC EDGAR companyfacts (filing-direct)"
# 3 (2026-10-15 review round 4): newest filing wins (anomalies dropped), growth / FCF never across filing generations, Q4
# diluted / EPS rules, splits — --all rebuilds older files once. The restricted-cash split (round 5) only ADDS fields and
# changes only files whose cash line uses the combined cash + restricted tag, so it is not a version bump: can_skip
# rebuilds exactly those files once (restricted_cash_pending) and leaves the rest untouched.
SCHEMA_VERSION = 3
FILING_FORMS = ("10-K", "10-K/A", "10-Q", "10-Q/A", "20-F", "20-F/A", "40-F", "40-F/A")
INSTANT_FORMS = ("10-Q", "10-Q/A", "10-K", "10-K/A", "20-F", "20-F/A", "40-F", "40-F/A")
ANNUAL_FORMS = ("10-K", "10-K/A", "20-F", "40-F")
QUARTERLY_FORMS = ("10-Q", "10-Q/A")
MIN_INTERVAL = 0.11  # seconds between EDGAR requests (<= 10/s)
RESTATE_TOL = 0.005  # a re-filed value within 0.5% is the same figure (rounding), beyond it a restatement
BASIS_BREAK_TOL = 0.01  # |sum of four quarters − FY| above 1% of FY = the quarters and the year are on different bases
SCALE_SLIP_LOG10 = 0.02  # two filings of one period whose values differ by 10^k (k ≥ 3) within this log10 distance = a scale slip
SHIFT_DAYS = (300, 400)  # a shifted column lands on the comparative one year away (10-K years, a 10-Q's year-ago quarter)
DATE_MERGE_DAYS = 3      # period ends (or starts) this close are the same period: a fiscal week-end vs the calendar month-end
_last_request = [0.0]
# per-build log of what the readers resolved (reset by build_statements; read for the warnings)
_LOG = {"scale": {}, "sign": {}, "zero": {}, "shift": {}}


def _et_today():
    from zoneinfo import ZoneInfo
    return datetime.datetime.now(ZoneInfo("America/New_York")).date()


def fetch(url, cache=None, name=None):
    """get_json (3 attempts, backoff, 90 s) behind a 10 requests/second
    throttle; with `cache` the file <cache>/<name> is read when present and
    written after a fetch."""
    if cache and name:
        p = os.path.join(cache, name)
        if os.path.exists(p):
            with open(p, encoding="utf-8") as f:
                return json.load(f)
    wait = MIN_INTERVAL - (time.monotonic() - _last_request[0])
    if wait > 0:
        time.sleep(wait)
    _last_request[0] = time.monotonic()
    data = get_json(url)
    if cache and name:
        os.makedirs(cache, exist_ok=True)
        with open(os.path.join(cache, name), "w", encoding="utf-8") as f:
            json.dump(data, f)
    return data


# ---------------------------------------------------------------------------
# Line specifications. Each line: key, label, level (indent), total (bold),
# unit, and either `tags` (us-gaap names, or (taxonomy, name)) or `derived`.
# kind: flow (duration, derivable), direct (duration, never derived), instant.
# bank: True = only for the bank shape, False = only for non-banks, None = both.
# negate: tags whose filed sign is the opposite of the line's (a net-interest
#   INCOME tag on the interest-EXPENSE line). combo: [(sign, tag), ...] — a
#   fallback for periods the tags leave empty: plain arithmetic on the legs,
#   all of them required in the same period. only_if_absent: the line is
#   emitted only when that other line carries no value at all.
# ---------------------------------------------------------------------------
def L(key, label, tags=None, level=1, total=False, unit="money", kind="flow", bank=None, derived=None, cf_sign=None, nonneg=False,
      negate=None, combo=None, only_if_absent=None, net_label=None):
    return {"key": key, "label": label, "tags": tags or [], "level": level, "total": total, "unit": unit, "kind": kind,
            "bank": bank, "derived": derived, "cf_sign": cf_sign, "nonneg": nonneg, "negate": set(negate or ()), "combo": combo,
            "only_if_absent": only_if_absent, "net_label": net_label}


REVENUE_TAGS = list(DUR["revenue"]) + ["SalesRevenueGoodsNet", "SalesRevenueServicesNet"]
REVENUE_TOTAL_TAGS = list(DUR["revenues_total"])
# Industry top-line elements filers used before the 2018 contract-revenue taxonomy (ATO, CMG, EXR, WEC, CCL, ALNY,
# GFI's US-GAAP years). They are components for some other filers (EQT's OilAndGasRevenue is one segment), so each
# fills only periods the tags above leave empty, and only when it never disagrees with the chosen revenue in a year
# where both are filed in the same taxonomy (revenue_fallbacks).
REVENUE_FALLBACK_TAGS = ["RegulatedAndUnregulatedOperatingRevenue", "SalesRevenueEnergyServices", "FoodAndBeverageRevenue", "RealEstateRevenueNet",
                         "GoldProductsAndServicesRevenue", "SalesRevenueServicesGross", "SalesRevenueGoodsGross", "LicenseAndServicesRevenue",
                         "OilAndGasRevenue", "UtilitiesOperatingRevenue", "ElectricUtilityRevenue"]
FALLBACK_AGREE_TOL = 0.01
FALLBACK_FAR_TOL = 0.10
NII_TAGS = ["InterestIncomeExpenseNet"]
NONINT_INCOME_TAGS = list(DUR["noninterest_income"])
NET_INCOME_TAGS = ["NetIncomeLoss", "ProfitLoss", (IF, "ProfitLossAttributableToOwnersOfParent"), (IF, "ProfitLoss")]
DA_TAGS = list(DUR["da"])
SBC_TAGS = list(DUR["sbc"])
OCF_TAGS = list(DUR["ocf"])
# capex: fundamentals' PP&E tags first, then the captions REITs / banks / insurers use for their capital spending
# (EXR's real-estate development and acquisitions, CFG / MTB's net premises-and-equipment line). One tag per period,
# never a sum; the line's `tags` names what was used.
CAPEX_TAGS = list(DUR["capex"]) + ["PaymentsForCapitalImprovements", "PaymentsToDevelopRealEstateAssets", "PaymentsToAcquireAndDevelopRealEstate",
                                   "PaymentsToAcquireRealEstate", "PaymentsForProceedsFromProductiveAssets"]
NET_PAYMENT_TAGS = ("PaymentsForProceedsFromProductiveAssets",)  # payments NET of proceeds: a negative value is a real net inflow
OI_TAGS = list(DUR["operating_income"])
SHARES_OUT_TAGS = list(INST["shares_outstanding"])
DEI_SHARES = ("dei", "EntityCommonStockSharesOutstanding")
NET_INTEREST_TAGS = ["InterestIncomeExpenseNonoperatingNet", "InterestIncomeExpenseNet"]  # income − expense as filed → negated on the expense line
# the face "interest expense" before the debt-only note component (APP's 10-K face is InterestAndDebtExpense 207,016K;
# InterestExpenseDebt 200,615K is the note figure)
INTEREST_EXPENSE_TAGS = ["InterestExpense", "InterestExpenseNonoperating", "InterestAndDebtExpense", "InterestExpenseDebt"]
# current-debt tags that are by definition the whole current borrowings (short-term + current maturities)
DEBT_CURRENT_AGG_TAGS = ("DebtCurrent", "CurrentBorrowingsAndCurrentPortionOfNoncurrentBorrowings")
# continuing-operations EPS: a fallback for periods with no EPS tag and no discontinued operations (HAL FY2022-FY2025)
EPS_CONTINUING = {"eps_diluted": "IncomeLossFromContinuingOperationsPerDilutedShare", "eps_basic": "IncomeLossFromContinuingOperationsPerBasicShare"}
# cash-flow lines whose filed amount is a payment (non-negative by definition): a negative filed value is the filer's
# sign slip — read as its absolute value, warned
PAYMENT_LINES = ("capex", "capex_intangibles", "buybacks", "dividends_paid", "purchases_investments", "debt_repaid")
# the cash-flow statement's cash total (cash + equivalents + RESTRICTED cash): the cash line's second tag, used for a date
# with no CashAndCashEquivalentsAtCarryingValue (fundamentals.py / dcf_engine.py read the same tag and treat it the same
# way). The restricted part is not cash the company can use, so the figures below that treat cash as available deduct it
# (Codex review of PR #2).
CASH_WITH_RESTRICTED_TAGS = ("CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents",)
# the balance-sheet cash caption WITHOUT restricted cash: where one filing reports it next to the combined total for the
# same date (a later 10-Q's comparative of a year end the 10-K tagged only with the total), the difference is exactly
# the restricted part (_cash_only_part)
CASH_ONLY_TAG = "CashAndCashEquivalentsAtCarryingValue"
# the restricted part of a combined total: a restricted-cash TOTAL for the date (fundamentals' INST["restricted_cash"]
# order, its current-only tag excepted), else the current and the noncurrent captions filed for the date summed (the
# cash-flow total includes both — U files RestrictedCashNoncurrent only). Listed here, not imported, so the split does
# not move when fundamentals' own list changes.
RESTRICTED_TOTAL_TAGS = ["RestrictedCashAndCashEquivalents", "RestrictedCash", "RestrictedCashAndCashEquivalentsAtCarryingValue", (IF, "RestrictedCashAndCashEquivalents")]
RESTRICTED_PART_TAGS = (["RestrictedCashCurrent"], ["RestrictedCashNoncurrent", "RestrictedCashAndCashEquivalentsNoncurrent"])
RESTRICTED_CASH_DERIVED = ("net_cash", "net_cash_per_share", "roic_proxy")
CASH_WITH_RESTRICTED_LABEL = "Cash, equivalents & restricted cash"
# visible on the statements table (the per-cell incl_restricted_* marks are JSON only): a line where SOME valued cells
# still count restricted cash as cash says so in its label; every cell → the ALL suffix (the cash line: the label above)
RESTRICTED_SOME_SUFFIX = " (some periods incl. restricted cash)"
RESTRICTED_ALL_SUFFIX = " (incl. restricted cash)"
DEBT_TOTAL_TAGS = ("LongTermDebt", "LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities", "DebtLongtermAndShorttermCombinedAmount", "Borrowings",
                   "SeniorNotes", "ConvertibleNotesPayable")  # totals that include current maturities: never added to the current-debt lines

INCOME = [
    L("revenue", "Revenue", REVENUE_TAGS, 0, True, nonneg=True),
    # bank shape (NoninterestIncome filed): the interest block replaces interest expense / income
    L("interest_income_total", "Total interest income", ["InterestAndDividendIncomeOperating", "InterestIncomeOperating"], 1, bank=True, nonneg=True),
    L("interest_expense_total", "Total interest expense", ["InterestExpense", "InterestExpenseOperating"], 1, bank=True, nonneg=True),
    L("net_interest_income", "Net interest income", NII_TAGS, 0, True, bank=True),
    # the income-statement TOTAL first; the loans-only allowance component is never shown alone (HBAN's 250 vs the filed
    # 158) — when no total tag exists the loans + off-balance-sheet components are summed, both required
    L("provision_credit_losses", "Provision for credit losses", ["ProvisionForCreditLosses", "ProvisionForLoanLeaseAndOtherLosses", "ProvisionForLoanAndLeaseLosses",
                                                                 "ProvisionForLoanLossesExpensed", "ProvisionForOtherCreditLosses"], 1, bank=True,
      combo=[(1, "FinancingReceivableExcludingAccruedInterestCreditLossExpenseReversal"), (1, "OffBalanceSheetCreditLossLiabilityCreditLossExpenseReversal")]),
    L("noninterest_income", "Noninterest income", NONINT_INCOME_TAGS, 0, True, bank=True),
    L("noninterest_expense", "Noninterest expense", ["NoninterestExpense"], 0, True, bank=True, nonneg=True),
    L("cost_of_revenue", "Cost of revenue", list(DUR["cogs"]) + ["CostOfGoodsAndServiceExcludingDepreciationDepletionAndAmortization",
                                                                  "CostOfGoodsSoldExcludingDepreciationDepletionAndAmortization"], 1, nonneg=True),
    L("gross_profit", "Gross profit", list(DUR["gross_profit"]), 0, True),
    L("rnd", "Research & development", list(DUR["rnd"]), 1, nonneg=True),
    L("sga", "Selling, general & administrative", list(DUR["sga"]), 1, nonneg=True),
    L("selling_marketing", "Selling & marketing", list(DUR["sm"]) + ["MarketingAndAdvertisingExpense"], 2, nonneg=True),
    L("general_admin", "General & administrative", list(DUR["ga"]), 2, nonneg=True),
    L("other_opex", "Other operating expenses", ["OtherCostAndExpenseOperating", "RestructuringCharges"], 1),
    L("total_opex", "Operating expenses", ["OperatingExpenses"], 0, True, nonneg=True),
    # last resort for filers that tag only the all-in total (cost of sales included): its own line, never mixed into the one above
    L("total_costs", "Total costs & expenses", ["CostsAndExpenses", "OperatingCostsAndExpenses"], 0, True, nonneg=True, only_if_absent="total_opex"),
    L("operating_income", "Operating income", OI_TAGS, 0, True),
    # IFRS: FinanceCosts is the face "finance expense"; ifrs InterestExpense is the gross note figure (GFI 130.4M vs 50.4M)
    L("interest_expense", "Interest expense", INTEREST_EXPENSE_TAGS + [(IF, "FinanceCosts"), (IF, "InterestExpense")] + NET_INTEREST_TAGS, 1, bank=False,
      negate=NET_INTEREST_TAGS, net_label="Interest expense, net"),
    L("interest_income", "Interest & investment income", ["InvestmentIncomeInterest", "InvestmentIncomeInterestAndDividend", "InterestAndOtherIncome",
                                                          (IF, "FinanceIncome"), (IF, "InvestmentIncome"), (IF, "InterestIncomeOnCashAndCashEquivalents")], 1, bank=False),
    # OtherNonoperatingIncomeExpense is the face "other" line; NonoperatingIncomeExpense is the whole non-operating section
    # for many filers (interest included) — reconciled against pretax income per period in reconcile_nonoperating
    L("other_nonoperating", "Other non-operating income (expense)", ["OtherNonoperatingIncomeExpense", "NonoperatingIncomeExpense"], 1),
    L("pretax_income", "Pretax income", list(DUR["pretax_income"]), 0, True),
    L("income_tax", "Income tax", list(DUR["tax"]), 1),
    L("net_income_continuing", "Net income from continuing operations", ["IncomeLossFromContinuingOperations", "IncomeLossFromContinuingOperationsIncludingPortionAttributableToNoncontrollingInterest",
                                                                           (IF, "ProfitLossFromContinuingOperations")], 1),
    L("discontinued_ops", "Discontinued operations", list(DUR["disc_ops"]) + ["IncomeLossFromDiscontinuedOperationsNetOfTaxAttributableToReportingEntity",
                                                                              (IF, "ProfitLossFromDiscontinuedOperations")], 1),
    L("net_income", "Net income", NET_INCOME_TAGS, 0, True),
    L("net_income_to_common", "Net income to common", ["NetIncomeLossAvailableToCommonStockholdersBasic", (IF, "ProfitLossAttributableToOrdinaryEquityHoldersOfParentEntity")], 1),
    L("eps_basic", "EPS (basic)", list(DUR["eps_basic"])[:1] + ["EarningsPerShareBasicAndDiluted", (IF, "BasicEarningsLossPerShare")], 0, False, "per_share", "direct"),
    L("eps_diluted", "EPS (diluted)", list(DUR["eps_diluted"])[:1] + ["EarningsPerShareBasicAndDiluted", (IF, "DilutedEarningsLossPerShare")], 0, True, "per_share", "direct"),
    L("shares_basic", "Shares outstanding (basic, weighted)", list(DUR["shares_basic"])[:1] + ["WeightedAverageNumberOfShareOutstandingBasicAndDiluted", (IF, "WeightedAverageShares")], 0, False, "shares", "direct"),
    L("shares_diluted", "Shares outstanding (diluted, weighted)", list(DUR["shares_diluted"])[:2] + ["WeightedAverageNumberOfShareOutstandingBasicAndDiluted", (IF, "AdjustedWeightedAverageShares")], 0, True, "shares", "direct"),
    L("da", "Depreciation & amortization", DA_TAGS, 1, nonneg=True),
    L("sbc", "Stock-based compensation", SBC_TAGS, 1, nonneg=True),
    L("ebitda", "EBITDA", level=0, total=True, derived="ebitda"),
    L("dps", "Dividends per share", list(DUR["dps_declared"]) + list(DUR["dps_paid"]), 0, False, "per_share", "direct"),
]
BALANCE = [
    L("cash", "Cash & equivalents", list(INST["cash"]) + ["CashAndDueFromBanks", "Cash"], 1, kind="instant"),
    # the restricted part of a cash cell filed only as the combined cash + restricted cash total (NTRS FY2025: 531.2M of
    # the 5,873.1M); filled ONLY in those cells by restricted_cash_split (from CASH_ONLY_TAG / RESTRICTED_TOTAL_TAGS /
    # RESTRICTED_PART_TAGS, so no tags here) — a separate restricted-cash caption next to a cash-only line is not part of
    # the line above and is not shown
    L("restricted_cash", "Restricted cash (included in cash above)", [], 2, kind="instant"),
    L("short_term_investments", "Short-term investments", list(INST["short_term_investments"]) + ["DebtSecuritiesAvailableForSaleExcludingAccruedInterestCurrent", "AvailableForSaleSecuritiesCurrent",
                                                                                                  (IF, "CurrentInvestments")], 1, kind="instant"),
    # banks: AFS and HTM are separate captions on the face; a total only when the filer tags one
    L("investment_securities", "Investment securities", ["MarketableSecurities", "AvailableForSaleSecuritiesAndHeldToMaturitySecurities", "InvestmentsDebtAndEquitySecurities"], 1, kind="instant", bank=True),
    L("securities_afs", "Securities available for sale", ["DebtSecuritiesAvailableForSaleExcludingAccruedInterest", "AvailableForSaleSecuritiesDebtSecurities", "AvailableForSaleSecurities"], 2, kind="instant", bank=True),
    L("securities_htm", "Securities held to maturity", ["DebtSecuritiesHeldToMaturityExcludingAccruedInterestAfterAllowanceForCreditLoss", "DebtSecuritiesHeldToMaturityAmortizedCostAfterAllowanceForCreditLoss",
                                                        "DebtSecuritiesHeldToMaturity", "HeldToMaturitySecurities"], 2, kind="instant", bank=True),
    L("loans_net", "Loans, net", ["LoansAndLeasesReceivableNetReportedAmount", "FinancingReceivableExcludingAccruedInterestAfterAllowanceForCreditLoss",
                                 "NotesReceivableNet", "LoansAndLeasesReceivableNetOfDeferredIncome"], 1, kind="instant", bank=True),
    L("allowance_credit_losses", "Allowance for credit losses", ["FinancingReceivableAllowanceForCreditLossExcludingAccruedInterest", "FinancingReceivableAllowanceForCreditLosses",
                                                                 "LoansAndLeasesReceivableAllowance", "AllowanceForLoanAndLeaseLosses"], 2, kind="instant", bank=True),
    L("receivables", "Receivables", list(INST["receivables"])[:1] + ["ReceivablesNetCurrent", (IF, "TradeAndOtherCurrentReceivables")], 1, kind="instant"),
    # LIFO filers (KR) file FIFO inventory and the LIFO reserve, not the net: the difference is the balance-sheet figure
    L("inventory", "Inventory", ["InventoryNet", "InventoryFinishedGoodsNetOfReserves", "InventoryGross", (IF, "Inventories")], 1, kind="instant",
      combo=[(1, "FIFOInventoryAmount"), (-1, "InventoryLIFOReserve")]),
    L("prepaids_other_current", "Prepaids & other current assets", list(INST["prepaids"]) + ["OtherAssetsCurrent"], 1, kind="instant"),
    L("total_current_assets", "Total current assets", list(INST["assets_current"]) + [(IF, "CurrentAssetsOtherThanAssetsOrDisposalGroupsClassifiedAsHeldForSaleOrAsHeldForDistributionToOwners")], 0, True, kind="instant"),
    L("ppe_net", "Property, plant & equipment, net", ["PropertyPlantAndEquipmentNet", "PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization",
                                                      (IF, "PropertyPlantAndEquipment"), (IF, "PropertyPlantAndEquipmentIncludingRightofuseAssets")], 1, kind="instant"),
    L("operating_lease_rou", "Operating lease right-of-use assets", ["OperatingLeaseRightOfUseAsset", (IF, "RightofuseAssets")], 1, kind="instant"),
    L("goodwill", "Goodwill", list(INST["goodwill"]), 1, kind="instant"),
    L("intangibles", "Intangible assets", ["IntangibleAssetsNetExcludingGoodwill", "FiniteLivedIntangibleAssetsNet", (IF, "IntangibleAssetsOtherThanGoodwill")], 1, kind="instant"),
    L("long_term_investments", "Long-term investments", ["LongTermInvestments", "MarketableSecuritiesNoncurrent", "AvailableForSaleSecuritiesDebtSecuritiesNoncurrent",
                                                        (IF, "NoncurrentInvestmentsOtherThanInvestmentsAccountedForUsingEquityMethod")], 1, kind="instant"),
    L("deferred_tax_assets", "Deferred tax assets", ["DeferredIncomeTaxAssetsNet", "DeferredTaxAssetsNetNoncurrent", "DeferredTaxAssetsNet", (IF, "DeferredTaxAssets")], 1, kind="instant"),
    L("other_lt_assets", "Other long-term assets", ["OtherAssetsNoncurrent", "OtherAssets", (IF, "OtherNoncurrentAssets")], 1, kind="instant"),
    L("total_assets", "Total assets", list(INST["assets"]), 0, True, kind="instant"),
    L("accounts_payable", "Accounts payable", ["AccountsPayableCurrent", "AccountsPayableTradeCurrent", "AccountsPayableAndAccruedLiabilitiesCurrent", (IF, "TradeAndOtherCurrentPayables")], 1, kind="instant"),
    L("accrued", "Accrued liabilities", ["AccruedLiabilitiesCurrent", (IF, "Accruals")], 1, kind="instant"),
    L("short_term_debt", "Short-term debt", list(INST["debt_cur_st"])[:3] + ["DebtCurrent", (IF, "ShorttermBorrowings")], 1, kind="instant"),
    L("current_lt_debt", "Current portion of long-term debt", ["LongTermDebtCurrent", "LongTermDebtAndCapitalLeaseObligationsCurrent", (IF, "CurrentPortionOfLongtermBorrowings"),
                                                              (IF, "CurrentBorrowingsAndCurrentPortionOfNoncurrentBorrowings")], 1, kind="instant"),
    L("current_lease", "Current lease liabilities", list(INST["lease_liab_current"]), 1, kind="instant"),
    L("deferred_revenue_current", "Deferred revenue (current)", list(INST["deferred_revenue"]), 1, kind="instant"),
    L("income_tax_payable", "Income taxes payable", ["AccruedIncomeTaxesCurrent", "TaxesPayableCurrent", (IF, "CurrentTaxLiabilities")], 1, kind="instant"),
    L("other_current_liab", "Other current liabilities", ["OtherLiabilitiesCurrent", (IF, "OtherCurrentLiabilities")], 1, kind="instant"),
    L("total_current_liabilities", "Total current liabilities", list(INST["liab_current"]), 0, True, kind="instant"),
    L("deposits", "Deposits", ["Deposits", (IF, "DepositsFromCustomers")], 1, kind="instant", bank=True),
    # per-period fallbacks for unclassified balance sheets (banks: LongTermDebt, which includes current maturities — the
    # total_debt rule knows) and for notes / convertibles tagged on their own
    L("long_term_debt", "Long-term debt", list(INST["debt_lt"]) + ["LongTermDebt", "LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities", "ConvertibleNotesPayableNoncurrent",
                                                                  "ConvertibleLongTermNotesPayable", "ConvertibleDebtNoncurrent", "SeniorLongTermNotes", "SeniorNotes", "ConvertibleNotesPayable"], 1, kind="instant"),
    L("long_term_lease", "Long-term lease liabilities", list(INST["lease_liab_lt"]), 1, kind="instant"),
    L("deferred_revenue_lt", "Deferred revenue (long-term)", ["ContractWithCustomerLiabilityNoncurrent", "DeferredRevenueNoncurrent"], 1, kind="instant"),
    L("deferred_tax_liab", "Deferred tax liabilities", ["DeferredIncomeTaxLiabilitiesNet", "DeferredTaxLiabilitiesNoncurrent", "DeferredIncomeTaxLiabilities", (IF, "DeferredTaxLiabilities")], 1, kind="instant"),
    L("other_lt_liab", "Other long-term liabilities", ["OtherLiabilitiesNoncurrent", "OtherLiabilities", (IF, "OtherNoncurrentLiabilities")], 1, kind="instant"),
    L("total_liabilities", "Total liabilities", list(INST["liabilities"]), 0, True, kind="instant"),
    L("common_stock", "Common stock", ["CommonStockValue", "CommonStockValueOutstanding", "CommonStocksIncludingAdditionalPaidInCapital", (IF, "IssuedCapital")], 1, kind="instant"),
    L("apic", "Additional paid-in capital", ["AdditionalPaidInCapital", "AdditionalPaidInCapitalCommonStock", (IF, "SharePremium")], 1, kind="instant"),
    L("retained_earnings", "Retained earnings", list(INST["retained_earnings"]), 1, kind="instant"),
    L("treasury_stock", "Treasury stock", ["TreasuryStockValue", "TreasuryStockCommonValue", (IF, "TreasuryShares")], 1, kind="instant"),
    L("aoci", "Accumulated other comprehensive income", ["AccumulatedOtherComprehensiveIncomeLossNetOfTax", (IF, "AccumulatedOtherComprehensiveIncome")], 1, kind="instant"),
    L("total_common_equity", "Shareholders' equity", ["StockholdersEquity", (IF, "EquityAttributableToOwnersOfParent")], 0, True, kind="instant"),
    L("minority_interest", "Minority interest", ["MinorityInterest", (IF, "NoncontrollingInterests")], 1, kind="instant"),
    L("total_equity", "Total equity", ["StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest", "StockholdersEquity", (IF, "Equity")], 0, True, kind="instant"),
    L("total_liabilities_and_equity", "Total liabilities & equity", ["LiabilitiesAndStockholdersEquity", (IF, "EquityAndLiabilities")], 0, True, kind="instant"),
]
CASHFLOW = [
    L("net_income", "Net income", NET_INCOME_TAGS, 0, True, cf_sign=1),
    L("da", "Depreciation & amortization", DA_TAGS, 1, cf_sign=1, nonneg=True),
    L("sbc", "Stock-based compensation", SBC_TAGS, 1, cf_sign=1, nonneg=True),
    L("deferred_taxes", "Deferred income taxes", ["DeferredIncomeTaxExpenseBenefit", "DeferredIncomeTaxesAndTaxCredits", (IF, "AdjustmentsForDeferredTaxExpense")], 1, cf_sign=1),
    L("other_noncash", "Other non-cash items", ["OtherNoncashIncomeExpense", "OtherOperatingActivitiesCashFlowStatement"], 1, cf_sign=1),
    L("change_receivables", "Change in receivables", ["IncreaseDecreaseInAccountsReceivable", "IncreaseDecreaseInReceivables"], 1, cf_sign=-1),
    L("change_inventory", "Change in inventory", ["IncreaseDecreaseInInventories", "IncreaseDecreaseInRetailRelatedInventories"], 1, cf_sign=-1),
    L("change_payables", "Change in accounts payable", ["IncreaseDecreaseInAccountsPayable", "IncreaseDecreaseInAccountsPayableTrade", "IncreaseDecreaseInAccountsPayableAndAccruedLiabilities"], 1, cf_sign=1),
    L("change_deferred_revenue", "Change in deferred revenue", ["IncreaseDecreaseInContractWithCustomerLiability", "IncreaseDecreaseInDeferredRevenue"], 1, cf_sign=1),
    L("change_working_capital", "Change in working capital", ["IncreaseDecreaseInOperatingCapital"], 1, cf_sign=-1),
    L("ocf", "Operating cash flow", OCF_TAGS, 0, True, cf_sign=1),
    L("capex", "Capital expenditures", CAPEX_TAGS, 1, cf_sign=-1, nonneg=True),
    L("capex_intangibles", "Purchases of intangibles / software", list(DUR["capex_intangibles"]), 1, cf_sign=-1, nonneg=True),
    L("acquisitions", "Acquisitions", list(DUR["acquisitions"]), 1, cf_sign=-1),
    L("purchases_investments", "Purchases of investments", ["PaymentsToAcquireInvestments", "PaymentsToAcquireAvailableForSaleSecuritiesDebt", "PaymentsToAcquireMarketableSecurities",
                                                           "PaymentsToAcquireAvailableForSaleSecurities", "PaymentsToAcquireShortTermInvestments", "PaymentsToAcquireOtherInvestments",
                                                           (IF, "PurchaseOfInvestmentsOtherThanInvestmentsAccountedForUsingEquityMethod")], 1, cf_sign=-1, nonneg=True),
    L("sales_investments", "Sales / maturities of investments", ["ProceedsFromSaleMaturityAndCollectionsOfInvestments", "ProceedsFromSaleAndMaturityOfMarketableSecurities",
                                                                "ProceedsFromMaturitiesPrepaymentsAndCallsOfAvailableForSaleSecurities", "ProceedsFromSaleOfAvailableForSaleSecuritiesDebt",
                                                                "ProceedsFromSaleOfAvailableForSaleSecurities", "ProceedsFromSaleMaturityAndCollectionOfShortTermInvestments",
                                                                (IF, "ProceedsFromSalesOfInvestmentsOtherThanInvestmentsAccountedForUsingEquityMethod")], 1, cf_sign=1, nonneg=True),
    L("other_investing", "Other investing activities", ["PaymentsForProceedsFromOtherInvestingActivities"], 1, cf_sign=-1),
    L("icf", "Investing cash flow", list(DUR["icf"])[:1] + ["NetCashProvidedByUsedInInvestingActivitiesContinuingOperations", (IF, "CashFlowsFromUsedInInvestingActivities")], 0, True, cf_sign=1),
    L("debt_issued", "Debt issued", ["ProceedsFromIssuanceOfLongTermDebt", "ProceedsFromIssuanceOfDebt", "ProceedsFromDebtNetOfIssuanceCosts", "ProceedsFromIssuanceOfSeniorLongTermDebt",
                                    "ProceedsFromLinesOfCredit", (IF, "ProceedsFromBorrowingsClassifiedAsFinancingActivities")], 1, cf_sign=1, nonneg=True),
    L("debt_repaid", "Debt repaid", ["RepaymentsOfLongTermDebt", "RepaymentsOfDebt", "RepaymentsOfLongTermDebtAndCapitalSecurities", "RepaymentsOfSeniorDebt", "RepaymentsOfLinesOfCredit",
                                    (IF, "RepaymentsOfBorrowingsClassifiedAsFinancingActivities")], 1, cf_sign=-1, nonneg=True),
    L("buybacks", "Share repurchases", list(DUR["buybacks"]), 1, cf_sign=-1, nonneg=True),
    L("dividends_paid", "Dividends paid", list(DUR["dividends_paid"]), 1, cf_sign=-1, nonneg=True),
    L("stock_issued", "Stock issued", ["ProceedsFromIssuanceOfCommonStock", "ProceedsFromIssuanceOrSaleOfEquity", "ProceedsFromIssuanceOfSharesUnderIncentiveAndShareBasedCompensationPlansIncludingStockOptions",
                                      "ProceedsFromIssuanceOfSharesUnderIncentiveAndShareBasedCompensationPlans", "ProceedsFromStockOptionsExercised", "ProceedsFromIssuanceInitialPublicOffering",
                                      (IF, "ProceedsFromIssuingShares")], 1, cf_sign=1, nonneg=True),
    L("other_financing", "Other financing activities", ["ProceedsFromPaymentsForOtherFinancingActivities"], 1, cf_sign=1),
    L("fincf", "Financing cash flow", list(DUR["fincf"])[:1] + ["NetCashProvidedByUsedInFinancingActivitiesContinuingOperations", (IF, "CashFlowsFromUsedInFinancingActivities")], 0, True, cf_sign=1),
    L("fx_effect", "Effect of exchange rates", ["EffectOfExchangeRateOnCashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents", "EffectOfExchangeRateOnCashAndCashEquivalents", "EffectOfExchangeRateOnCash",
                                               (IF, "EffectOfExchangeRateChangesOnCashAndCashEquivalents")], 1, cf_sign=1),
    L("net_change_cash", "Net change in cash", ["CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsPeriodIncreaseDecreaseIncludingExchangeRateEffect", "CashAndCashEquivalentsPeriodIncreaseDecrease",
                                               "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsPeriodIncreaseDecreaseExcludingExchangeRateEffect",
                                               (IF, "IncreaseDecreaseInCashAndCashEquivalents")], 0, True, cf_sign=1),
    L("fcf", "Free cash flow", level=0, total=True, derived="fcf", cf_sign=1),
    L("owner_earnings", "Owner's earnings", level=0, total=True, derived="owner_earnings", cf_sign=1),
]
METRICS = [
    L("total_debt", "Total debt", level=0, total=True, derived="total_debt"),
    L("net_cash", "Net cash (debt)", level=0, total=True, derived="net_cash"),
    L("net_cash_per_share", "Net cash per share", level=1, unit="per_share", derived="net_cash_per_share"),
    L("working_capital", "Working capital", level=0, derived="working_capital"),
    L("book_value_per_share", "Book value per share", level=0, unit="per_share", derived="book_value_per_share"),
    L("tangible_book_value", "Tangible book value", level=0, derived="tangible_book_value"),
    L("tangible_book_value_per_share", "Tangible book value per share", level=1, unit="per_share", derived="tangible_book_value_per_share"),
    L("shares_outstanding", "Shares outstanding (period end)", SHARES_OUT_TAGS, 0, False, "shares", "instant"),
    L("fcf_per_share", "Free cash flow per share", level=0, unit="per_share", derived="fcf_per_share"),
    L("owner_earnings_per_share", "Owner's earnings per share", level=0, unit="per_share", derived="owner_earnings_per_share"),
    L("gross_margin", "Gross margin", level=0, unit="pct", derived="gross_margin"),
    L("operating_margin", "Operating margin", level=0, unit="pct", derived="operating_margin"),
    L("net_margin", "Net margin", level=0, unit="pct", derived="net_margin"),
    L("fcf_margin", "Free cash flow margin", level=0, unit="pct", derived="fcf_margin"),
    L("roe", "Return on equity", level=0, unit="pct", derived="roe"),
    L("roa", "Return on assets", level=0, unit="pct", derived="roa"),
    L("roic_proxy", "Return on invested capital (proxy)", level=0, unit="pct", derived="roic_proxy"),
    L("debt_to_equity", "Debt / equity", level=0, unit="ratio", derived="debt_to_equity"),
    L("current_ratio", "Current ratio", level=0, unit="ratio", derived="current_ratio"),
]
# hidden instant helpers the total_debt rule needs (never emitted as lines)
HIDDEN = [
    L("debt_current_agg", "", ["DebtCurrent"], kind="instant"),  # (the IFRS aggregate is a display line: current_lt_debt)
    L("debt_total_agg", "", list(INST["debt_total"]), kind="instant"),
    # discontinued operations in the cash-flow statement (CCI FY2023-FY2025: total-company OCF 3,057M includes 1,185M of
    # discontinued operations while capex 182M is continuing only, the discontinued investing flows on their own line):
    # free cash flow is then continuing OCF - capex, never total OCF - continuing capex
    L("ocf_continuing", "", ["NetCashProvidedByUsedInOperatingActivitiesContinuingOperations"],
      combo=[(1, "NetCashProvidedByUsedInOperatingActivities"), (-1, "CashProvidedByUsedInOperatingActivitiesDiscontinuedOperations")]),
    L("icf_discontinued", "", ["CashProvidedByUsedInInvestingActivitiesDiscontinuedOperations"]),
]
STATEMENTS = (("income", INCOME), ("balance", BALANCE), ("cashflow", CASHFLOW), ("metrics", METRICS))
TTM_SUM_UNITS = ("money", "per_share")  # flows summed over four quarters; shares averaged
DPS_WINDOW = (80, 120)
# SBC counts as 0 for a period whose cash-flow statement has no share-based-compensation line at all (and no unlisted
# SBC-like tag either). Capex NEVER reads as zero: a period without a filed capex figure has no FCF / owner's earnings.
ZERO_WHEN_UNFILED = ("sbc",)
# lines whose four quarters should sum to the fiscal year (the basis-break check); flows only — EPS and share
# averages never sum, instants never do
BASIS_CHECK_UNITS = ("money",)


# ---------------------------------------------------------------------------
# Fact readers — the whole filing history of every fact, one unit at a time
# ---------------------------------------------------------------------------
def _pairs(tags):
    return [(t if isinstance(t, tuple) else ("us-gaap", t)) for t in tags]


def _tag_facts(facts, pair):
    tf = facts.get("facts", {}).get(pair[0], {}).get(pair[1])
    return (tf or {}).get("units", {}) if tf else {}


def _unit_ok(unit_key, unit):
    """`unit` is a money unit ("USD"), "shares", or a per-share unit ("USD/shares")."""
    if unit is None:
        return True
    if unit_key == unit:
        return True
    return unit.endswith("/shares") and unit_key.replace("/share", "/shares").replace("/shares/shares", "/shares") == unit


def _sign_fix(pair, key, e, absneg):
    """The filed value, or its absolute value for a payment tag filed negative (logged)."""
    v = e["val"]
    if absneg and v < 0 and pair[1] not in NET_PAYMENT_TAGS:
        per = f"{e['start']}..{e['end']}" if e.get("start") and e["start"] != e.get("end") else e.get("end")
        _LOG["sign"].setdefault(pair[1], set()).add((per, e.get("form", ""), e.get("filed", ""), e.get("accn")))
        return -v
    return v


def _value_groups(entries):
    """[[value, [entries]]] — entries whose values agree within RESTATE_TOL share a group (first-filed order)."""
    groups = []
    for x in entries:
        for g in groups:
            if _close(x[1], g[0]):
                g[1].append(x)
                break
        else:
            groups.append([x[1], [x]])
    return groups


def pick(entries):
    """(chosen entry, its value group) for one period's filings (sorted by
    filing date) once the anomalies are gone (drop_anomalies): the NEWEST
    filing wins — a restatement (discontinued operations, an accounting
    change, a recast) re-files every year it covers, so the restated year and
    its neighbours share one basis; the group is every filing of that value
    (within 0.5%), whose accessions are the cell's provenance."""
    last = entries[-1]
    return last, [x for x in entries if _close(x[1], last[1])]


def _scale_slip(a, b):
    """True when two non-zero values differ by a factor of 10^k, k ≥ 3 (a thousands / millions slip)."""
    if not a or not b:
        return False
    r = abs(math.log10(abs(a)) - math.log10(abs(b)))
    return r >= 2.5 and abs(r - round(r)) <= SCALE_SLIP_LOG10


def drop_zero_slips(hist, tag):
    """A filed 0 for a period another filing reports as non-zero is a slip
    (DXCM's FY2014 10-K tagged EPS 0 for every 2013 quarter the 10-Qs filed
    as −0.14 / −0.08 / …): dropped before anything is chosen, logged."""
    out = None
    for k, es in hist.items():
        if es and es[-1][1] == 0 and any(x[1] != 0 for x in es):  # only a NEWEST zero matters (an older one never wins)
            out = out if out is not None else dict(hist)
            out[k] = [x for x in es if x[1] != 0]
            kname = k if isinstance(k, str) else f"{k[0]}..{k[1]}"
            _LOG["zero"][(tag, kname)] = (out[k][-1][1], [(x[3], x[0]) for x in es if x[1] == 0])
    return out if out is not None else hist


def _period_len(k):
    return 0 if isinstance(k, str) else _days(k[0], k[1])


def _period_end(k):
    return k if isinstance(k, str) else k[1]


SHIFT_MIN_DIGITS = 3


def _sig_digits(v):
    """Significant digits of a filed value (1,115,968,000 → 7; 43,000,000 → 2; 0.885 → 3; 0 → 0)."""
    t = f"{abs(v):.12g}".split("e")[0].replace(".", "").lstrip("0").rstrip("0")
    return len(t)


def drop_shifted(hist, tag):
    """A value only the NEWEST filing(s) of a period carry that is exactly the
    value the same tag carries for the ADJACENT comparative column (same
    length, ends one year apart: SHIFT_DAYS) while earlier filings of this
    period say otherwise, and the late filing does not itself report that
    neighbour at the same value (a balance that did not move), is a
    shifted column, not a restatement (HBAN's 2015 10-K tagged its 2010 cash
    with 2011's 1,115,968K and its 2011 cash with 2012's 1,262,806K): those
    filings are dropped for this period, logged."""
    keys = list(hist)
    out = None
    for k in keys:
        es = hist[k]
        if len(es) < 2:
            continue
        last = es[-1]
        late = [x for x in es if _close(x[1], last[1])]
        early = [x for x in es if not _close(x[1], last[1])]
        if not early or min(x[0] for x in late) <= max(x[0] for x in early) or _sig_digits(last[1]) < SHIFT_MIN_DIGITS:
            continue  # (a figure rounded to one or two digits — 43,000,000 — matches a neighbour by coincidence too often)
        n, e = _period_len(k), _period_end(k)
        late_acc = {x[2] for x in late}
        same = lambda v: abs(v - last[1]) <= 1e-9 * max(abs(last[1]), 1.0)  # noqa: E731
        for k2 in keys:
            if k2 == k or abs(_period_len(k2) - n) > 20 or not (SHIFT_DAYS[0] <= abs(_days(_period_end(k2), e)) <= SHIFT_DAYS[1]):
                continue
            # the late filing reports the adjacent period at that same value too: a balance that did not move (a restated
            # goodwill, a fixed note), not a shifted column
            if any(x[2] in late_acc and same(x[1]) for x in hist[k2]):
                continue
            # the neighbour's value as filed BEFORE the late filing (a later mis-dated filing of the neighbour proves nothing)
            if any(x[2] not in late_acc and x[0] < min(y[0] for y in late) and same(x[1]) for x in hist[k2]):
                out = out if out is not None else dict(hist)
                out[k] = early
                kname = k if isinstance(k, str) else f"{k[0]}..{k[1]}"
                _LOG["shift"][(tag, kname)] = (early[-1][1], last[1], _period_end(k2), [(x[3], x[0]) for x in late])
                break
    return out if out is not None else hist


def drop_anomalies(hist, tag, per_share=False):
    """The anomaly detectors that may overrule the newest filing of a period:
    a filed 0 against non-zero filings, a power-of-ten slip, a column shifted
    to the adjacent period's value. Everything else is a restatement and the
    newest filing wins (pick)."""
    hist = drop_scale_slips(hist, tag, per_share=per_share)
    hist = drop_zero_slips(hist, tag)
    return drop_shifted(hist, tag)


def drop_scale_slips(hist, tag, per_share=False):
    """Remove the filings of a period whose value is a power-of-ten slip of
    another filing's value (HAL re-filed its 2020-2024 EPS ×1,000,000, twice
    for some years — more filings carry the slip than the original). The value
    kept is the one closest (log scale) to the tag's other periods (their
    newest values); with no other period, the smaller one for per-share facts, else
    the original filing's. Every drop lands in _LOG['scale']."""
    conflicted, ref_vals = {}, []
    for k, es in hist.items():
        gs = _value_groups(es)
        if any(_scale_slip(a[0], b[0]) for i, a in enumerate(gs) for b in gs[i + 1:]):
            conflicted[k] = gs
        elif es:
            v = abs(pick(es)[0][1])
            if v:
                ref_vals.append(v)
    if not conflicted:
        return hist
    ref_vals.sort()
    ref = ref_vals[len(ref_vals) // 2] if ref_vals else None
    out = dict(hist)
    for k, gs in conflicted.items():
        nz = [g for g in gs if g[0]]
        if ref:
            keep = min(nz, key=lambda g: abs(math.log10(abs(g[0])) - math.log10(ref)))
        elif per_share:
            keep = min(nz, key=lambda g: abs(g[0]))
        else:
            keep = min(nz, key=lambda g: min(x[0] for x in g[1]))
        dropped = [g for g in gs if g is not keep and _scale_slip(g[0], keep[0])]
        if not dropped:
            continue
        drop_ids = {id(x) for g in dropped for x in g[1]}
        out[k] = [x for x in hist[k] if id(x) not in drop_ids]
        kname = k if isinstance(k, str) else f"{k[0]}..{k[1]}"
        _LOG["scale"][(tag, kname)] = (keep[0], [(x[1], x[3], x[0], x[2]) for g in dropped for x in g[1]])
    return out


def duration_history(facts, pair, unit=None, forms=DURATION_FORMS, absneg=False):
    """{(start, end): [(filed, val, accn, form), ...] sorted by filing date} —
    EVERY filing of every duration period of one tag, in `unit`, power-of-ten
    slips removed (drop_scale_slips); `absneg` reads a negative payment as its
    absolute value (the filer's sign slip)."""
    out = {}
    for unit_key, es in _tag_facts(facts, pair).items():
        if not _unit_ok(unit_key, unit):
            continue
        for e in es:
            if e.get("form", "") not in forms or not e.get("start") or not e.get("end") or not _num(e.get("val")):
                continue
            key = (e["start"], e["end"])
            out.setdefault(key, []).append((e.get("filed", ""), _sign_fix(pair, key, e, absneg), e.get("accn"), e.get("form", "")))
    for v in out.values():
        v.sort(key=lambda x: x[0])
    return drop_anomalies(out, pair[1], per_share=bool(unit and unit.endswith("/shares")))


def instant_history(facts, pair, unit=None, forms=INSTANT_FORMS):
    """{end: [(filed, val, accn, form, fp)] sorted by filing date} — every filing of every instant of one tag
    (power-of-ten slips removed)."""
    out = {}
    for unit_key, es in _tag_facts(facts, pair).items():
        if not _unit_ok(unit_key, unit):
            continue
        for e in es:
            if e.get("form", "") not in forms or not e.get("end") or not _num(e.get("val")):
                continue
            if e.get("start") and e["start"] != e["end"]:
                continue
            out.setdefault(e["end"], []).append((e.get("filed", ""), e["val"], e.get("accn"), e.get("form", ""), e.get("fp")))
    for v in out.values():
        v.sort(key=lambda x: x[0])
    return drop_anomalies(out, pair[1], per_share=bool(unit and unit.endswith("/shares")))


def is_fy(s, e):
    return 330 <= _days(s, e) <= 380


def _rec(entry, group, tag, es=None, key=None):
    """(val, tag, filed, accn, accns, all_accns) — the chosen filing of a period, every accession that filed that
    value (the cell's provenance) and every accession that filed the period at all (whatever value)."""
    return (entry[1], tag, entry[0], entry[2], sorted({x[2] for x in group if x[2]}), sorted({x[2] for x in (es or group) if x[2]}),
            bool(es) and len(group) < len(es))


def annual_values(facts, tags, unit, duration=True, absneg=False):
    """({end: (val, tag, filed, accn, accns)}, {end: [(tag, val, filed, accn)]})
    — FY facts (fp FY on 10-K / 20-F / 40-F) in `unit`, tag priority first;
    per tag the NEWEST filing's value of the period (pick) once the anomalies
    are dropped (drop_anomalies: a filed 0 against non-zero filings, a
    power-of-ten slip, a shifted column). The second dict lists every
    candidate tag's value per period (the plausibility checks read it)."""
    vals, cands = {}, {}
    for pair in _pairs(tags):
        hist = {}
        for unit_key, es in _tag_facts(facts, pair).items():
            if not _unit_ok(unit_key, unit):
                continue
            for e in es:
                if e.get("fp") != "FY" or e.get("form", "") not in ANNUAL_FORMS or not e.get("end") or not _num(e.get("val")):
                    continue
                end, start = e["end"], e.get("start")
                if duration:
                    if not start or not is_fy(start, end):
                        continue
                elif start and start != end:
                    continue
                hist.setdefault(end, []).append((e.get("filed", ""), _sign_fix(pair, end, e, absneg), e.get("accn"), e.get("form", "")))
        for v in hist.values():
            v.sort(key=lambda x: x[0])
        hist = drop_anomalies(hist, pair[1], per_share=bool(unit and unit.endswith("/shares")))
        for k, es in hist.items():
            if not es:
                continue
            entry, group = pick(es)
            cands.setdefault(k, []).append((pair[1], entry[1], entry[0], entry[2]))
            if k not in vals:
                vals[k] = _rec(entry, group, pair[1], es, k)
    return vals, cands


def instant_values(facts, tags, unit):
    """{end: (val, tag, filed, accn, accns)} — balance-sheet instants on ANY
    10-Q / 10-K / 20-F / 40-F form in `unit`, tag priority first, the
    newest filing per tag once the anomalies are dropped (HBAN's 2010 cash:
    847,888K, not the 2015 10-K's shifted 1,115,968K — 2011's value)."""
    out = {}
    for pair in _pairs(tags):
        for end, es in instant_history(facts, pair, unit).items():
            if end not in out and es:
                entry, group = pick(es)
                out[end] = _rec(entry, group, pair[1], es, end)
    return out


def annual_instant_values(facts, tags, unit):
    """{end: (val, tag, filed, accn, accns)} for fiscal-year-end balances: the
    tag is the first (priority order) that an annual report (fp FY) filed for
    that date; its value is the newest filing of that tag at that date
    (annual and quarterly forms; anomalies dropped)."""
    out = {}
    for pair in _pairs(tags):
        for end, es in instant_history(facts, pair, unit).items():
            if end in out or not es or not any(x[3] in ANNUAL_FORMS and x[4] == "FY" for x in es):
                continue
            entry, group = pick(es)
            out[end] = _rec(entry, group, pair[1], es, end)
    return out


# ---------------------------------------------------------------------------
# One period, one date: a fiscal week-end and the calendar month-end the later
# comparatives used (HSY's 2012-04-01 10-Q vs 2012-03-31 in the 2013 10-K)
# ---------------------------------------------------------------------------
def _date_clusters(dated):
    """dated: {date: earliest filed} → {date: representative} for chains of
    dates DATE_MERGE_DAYS apart or less; the representative is the date the
    earliest filing used (the 10-Q's own period end)."""
    ds = sorted(dated)
    out, cur = {}, []

    def flush():
        if len(cur) > 1:
            rep = min(cur, key=lambda d: (dated[d], d))
            for d in cur:
                out[d] = rep
    for d in ds:
        if cur and _days(cur[-1], d) > DATE_MERGE_DAYS:
            flush()
            cur = []
        cur.append(d)
    flush()
    return out


def canonical_dates(facts):
    """facts with every context start / end mapped onto one date per period
    (the date the earliest filing used), so the two filings of one quarter —
    one at the fiscal week-end, one at the calendar month-end — are one column
    and vote together. The clusters come from the core lines' periods; any
    other fact dated within DATE_MERGE_DAYS of a merged date follows it.
    Returns (facts, {old: new}) — the input is not modified."""
    ends, starts = {}, {}
    core = REVENUE_TAGS + REVENUE_TOTAL_TAGS + NET_INCOME_TAGS + OCF_TAGS + OI_TAGS + list(INST["assets"])
    for pair in _pairs(core):
        for es in _tag_facts(facts, pair).values():
            for e in es:
                f = e.get("filed") or "9999"
                if e.get("end"):
                    ends[e["end"]] = min(ends.get(e["end"], f), f)
                if e.get("start") and e["start"] != e.get("end"):
                    starts[e["start"]] = min(starts.get(e["start"], f), f)
    emap, smap = _date_clusters(ends), _date_clusters(starts)
    if not emap and not smap:
        return facts, {}

    def near(m):
        keys = sorted(m)

        def f(d):
            if not d or d in m:
                return m.get(d, d)
            i = bisect.bisect_left(keys, d)
            for j in (i - 1, i):
                if 0 <= j < len(keys) and abs(_days(keys[j], d)) <= DATE_MERGE_DAYS:
                    return m[keys[j]]
            return d
        return f
    fe, fs = near(emap), near(smap)
    out = dict(facts)
    out["facts"] = {}
    for tax, tags in (facts.get("facts") or {}).items():
        nt = {}
        for name, d in tags.items():
            units = {}
            for u, es in (d.get("units") or {}).items():
                ne = []
                for e in es:
                    end, start = e.get("end"), e.get("start")
                    if start and start == end:
                        n_end = n_start = fe(end)
                    else:
                        n_end, n_start = fe(end), fs(start)
                    if n_end != end or n_start != start:
                        e = dict(e, end=n_end)
                        if start:
                            e["start"] = n_start
                    ne.append(e)
                units[u] = ne
            nt[name] = dict(d, units=units)
        out["facts"][tax] = nt
    return out, {k: v for k, v in emap.items() if k != v}


def dei_shares_by_period(facts, period_ends, window=75):
    """{period_end: (count, filed, cover_date)} from the cover-page
    dei:EntityCommonStockSharesOutstanding dated within `window` days AFTER
    the period end (the earliest such cover date), for periods that have no
    balance-sheet share count."""
    tf = facts.get("facts", {}).get(DEI_SHARES[0], {}).get(DEI_SHARES[1])
    if not tf:
        return {}
    pts = sorted((e["end"], e.get("filed", ""), e["val"]) for e in tf.get("units", {}).get("shares", [])
                 if e.get("end") and _num(e.get("val")) and e["val"] > 0 and not (e.get("start") and e["start"] != e["end"]))
    out = {}
    for p in period_ends:
        for end, filed, val in pts:
            d = _days(p, end)
            if 0 <= d <= window:
                out[p] = (val, filed, end)
                break
    return out


def accns_with(facts, tags):
    """Every accession number that files any of `tags` (any period, unit, form)."""
    out = set()
    for pair in _pairs(tags):
        for es in _tag_facts(facts, pair).values():
            for e in es:
                if e.get("accn") and _num(e.get("val")):
                    out.add(e["accn"])
    return out


def has_quarterly_forms(facts, tags):
    for pair in _pairs(tags):
        for es in _tag_facts(facts, pair).values():
            if any(e.get("form") in QUARTERLY_FORMS for e in es):
                return True
    return False


def money_unit(facts, warnings):
    """The ONE money unit of the file: the unit most of the core FY facts
    (revenue, net income, OCF, assets) are filed in, USD preferred on ties.
    Facts in any other currency (convenience translations) are ignored."""
    counts = {}
    for tags, duration in ((REVENUE_TAGS, True), (NET_INCOME_TAGS, True), (OCF_TAGS, True), (INST["assets"], False)):
        for pair in _pairs(tags):
            for unit_key, es in _tag_facts(facts, pair).items():
                if "/" in unit_key or unit_key in ("shares", "pure"):
                    continue
                for e in es:
                    if e.get("fp") != "FY" or e.get("form", "") not in ANNUAL_FORMS or not e.get("end"):
                        continue
                    if duration and not (e.get("start") and is_fy(e["start"], e["end"])):
                        continue
                    counts[unit_key] = counts.get(unit_key, 0) + 1
    if not counts:
        return "USD"
    order = _units_pref(list(counts))
    unit = max(order, key=lambda u: (counts[u], -order.index(u)))
    others = sorted(u for u in counts if u != unit)
    if unit != "USD":
        warnings.append(f"core facts filed in {unit} — figures are shown as filed (no FX conversion)" + (f"; the filer's {', '.join(others)} convenience translations are ignored" if others else ""))
    elif others:
        warnings.append(f"the filer also files core facts in {', '.join(others)} — only the USD facts are read; a quarter is never derived from legs in different currencies")
    return unit


def unit_for(spec, money):
    return {"money": money, "per_share": f"{money}/shares", "shares": "shares"}.get(spec["unit"], money)


# ---------------------------------------------------------------------------
# Quarterly machinery — fundamentals.quarterly_series with the legs paired by
# filing generation and restricted to one unit
# ---------------------------------------------------------------------------
def _close(a, b, tol=RESTATE_TOL):
    return abs(a - b) <= tol * max(abs(a), abs(b), 1e-9)


def pair_generations(long_hist, short_hist):
    """The two legs of a derived quarter from the same filing generation.
    long_hist / short_hist: [(filed, val, accn, form)] sorted by filing date
    (the longer and the shorter year-to-date leg). The shorter leg is its
    latest filing (filed F); the longer leg is the first filing on or after F
    (the original 10-K after the original Q3 10-Q; the next year's 10-K after
    the next year's Q3 comparative), else the last one before F. When the
    longer leg was restated AFTER the shorter leg's last filing (the value
    changed vs the longer leg's filing before F while the shorter leg was
    re-filed unchanged) the pair before F is used, so a nine-month leg never
    meets a fiscal year on another basis. Returns (long, short) entries."""
    short = short_hist[-1]
    f_short = short[0]
    after = [x for x in long_hist if x[0] >= f_short]
    before = [x for x in long_hist if x[0] < f_short]
    cand = after[0] if after else before[-1]
    if after and before and len(short_hist) >= 2 and _close(short[1], short_hist[-2][1]) and not _close(cand[1], before[-1][1]):
        cand = before[-1]
    return cand, short


def quarterly_series_gen(hist, derive=True, direct_window=(80, 120), fy_starts=None, tag=None):
    """{quarter_end: {val, fq, fy_start, derived, tag, ytd, filed, accns}} for
    the fiscal quarters one tag's history supports. Direct 3-month facts win
    (latest filing); otherwise quarter = YTD − prior YTD within the same
    fiscal year, Q4 = FY − nine-month YTD, both legs from one filing
    generation (pair_generations). `hist` = duration_history in ONE unit. A
    period read as itself (a direct quarter, a first-quarter YTD) takes its
    newest filing (anomalies dropped)."""
    f = {k: pick(v)[0] for k, v in hist.items() if v}
    dis = {k: len(pick(v)[1]) < len(v) for k, v in hist.items() if v}
    if not f:
        return {}
    annual_keys = [(s, e) for (s, e) in f if is_fy(s, e)]
    fy_starts = set(fy_starts or ()) | {s for s, _ in annual_keys}
    for _, e in annual_keys:  # the fiscal year that follows each filed annual period
        fy_starts.add((datetime.date.fromisoformat(e) + datetime.timedelta(days=1)).isoformat())
    direct = {(s, e): v for (s, e), v in f.items() if direct_window[0] <= _days(s, e) <= direct_window[1]}
    out = {}
    for s in sorted(fy_starts):
        # Rank each YTD leg by its length: ~1, 2, 3 or 4 quarters (±35 days tolerates 52/53-week years and 16-week
        # first quarters). A quarter is derived ONLY from the leg one rank shorter — a missing leg (e.g. capex filed
        # on the 10-K alone) must never make the annual total masquerade as a quarter.
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
        prev_e, last_rank = None, 0
        for rank in (1, 2, 3, 4):
            e = by_rank.get(rank)
            if e is None:
                continue
            filed, v, accn, form = f[(s, e)]
            dq = [(k, dv) for k, dv in direct.items() if k[1] == e]
            if dq:
                dfiled, dval, daccn, dform = dq[0][1]
                out[e] = {"val": dval, "fq": rank, "fy_start": s, "derived": False, "tag": tag, "ytd": v, "filed": dfiled, "accns": [daccn], "disagree": dis[dq[0][0]]}
            elif derive and last_rank == rank - 1:
                if rank == 1:
                    out[e] = {"val": v, "fq": 1, "fy_start": s, "derived": False, "tag": tag, "ytd": v, "filed": filed, "accns": [accn], "disagree": dis[(s, e)]}
                else:
                    lg, sh = pair_generations(hist[(s, e)], hist[(s, prev_e)])
                    out[e] = {"val": lg[1] - sh[1], "fq": rank, "fy_start": s, "derived": True, "tag": tag, "ytd": v, "filed": lg[0], "accns": [lg[2], sh[2]]}
            prev_e, last_rank = e, rank
    # direct quarters not attached to a known FY start (fiscal-year start unknown)
    for (s, e), (filed, v, accn, form) in direct.items():
        if e not in out:
            fs = max((x for x in fy_starts if x <= s and _days(x, s) <= 300), default=None)
            fq = (round(_days(fs, e) / 91.25) if fs else None)
            out[e] = {"val": v, "fq": fq if fq and 1 <= fq <= 4 else None, "fy_start": fs, "derived": False, "tag": tag, "ytd": None, "filed": filed, "accns": [accn],
                      "disagree": dis[(s, e)]}
    return out


def quarterly_values(facts, tags, unit, derive=True, direct_window=(80, 120), fy_starts=None, absneg=False):
    """quarterly_series_gen per candidate tag, merged per quarter end in
    tag-priority order — a derived quarter never subtracts one tag's leg from
    another's, nor a leg in another unit."""
    out = {}
    for pair in _pairs(tags):
        hist = duration_history(facts, pair, unit, absneg=absneg)
        if not hist:
            continue
        for e, d in quarterly_series_gen(hist, derive=derive, direct_window=direct_window, fy_starts=fy_starts, tag=pair[1]).items():
            out.setdefault(e, d)
    return out


# ---------------------------------------------------------------------------
# Series per line
# ---------------------------------------------------------------------------
def _apply_sign(spec, a, q):
    for e, v in list(a.items()):
        if v[1] in spec["negate"]:
            a[e] = (-v[0],) + tuple(v[1:])
    for e, d in q.items():
        if d.get("tag") in spec["negate"] and _num(d.get("val")):
            d["val"] = -d["val"]


def _combo(spec, facts, unit, fy_starts, a, q):
    """Fill periods the tags left empty with the combo's arithmetic (every leg
    required in the same period, and from one filing generation: legs whose
    values share no filing although a filing reports them all are not
    combined)."""
    legs = spec["combo"]
    label = "".join(("+" if sgn > 0 else "-") + t for sgn, t in legs).lstrip("+")

    def joined(series, e):
        p = _prov_join([(set(s[e][4]), set(s[e][5] if len(s[e]) > 5 else s[e][4])) for _, s in series])
        return None if _prov_conflict(p) else p

    if spec["kind"] == "instant":
        series = [(sgn, instant_values(facts, [t], unit)) for sgn, t in legs]
        for e in set.intersection(*(set(s) for _, s in series)) if series else set():
            p = joined(series, e)
            if p is None:
                continue
            val, filed, accn = sum(sgn * s[e][0] for sgn, s in series), max(s[e][2] or "" for _, s in series), series[0][1][e][3]
            accns = sorted(p[0])
            if e not in a:
                a[e] = (val, label, filed, accn, accns, sorted(p[1]))
            if e not in q:
                q[e] = {"val": val, "derived": False, "tag": label, "filed": filed, "accns": accns}
        return
    ann = [(sgn, annual_values(facts, [t], unit)[0]) for sgn, t in legs]
    for e in set.intersection(*(set(s) for _, s in ann)) if ann else set():
        p = joined(ann, e)
        if e not in a and p is not None:
            a[e] = (sum(sgn * s[e][0] for sgn, s in ann), label, max(s[e][2] or "" for _, s in ann), ann[0][1][e][3], sorted(p[0]), sorted(p[1]))
    qs = [(sgn, quarterly_values(facts, [t], unit, derive=True, fy_starts=fy_starts)) for sgn, t in legs]
    for e in set.intersection(*(set(s) for _, s in qs)) if qs else set():
        if e not in q:
            base = qs[0][1][e]
            q[e] = dict(base, val=sum(sgn * s[e]["val"] for sgn, s in qs), tag=label, derived=any(s[e].get("derived") for _, s in qs),
                        accns=sorted({x for _, s in qs for x in s[e].get("accns", [])}))


def _series_for(spec, facts, fy_starts, money):
    """(annual {end: (val, tag, filed, accn, accns)}, quarterly {end: {val, fq, fy_start, derived, tag, filed, accns}})."""
    unit = unit_for(spec, money)
    kind, tags = spec["kind"], spec["tags"]
    absneg = spec["key"] in PAYMENT_LINES
    if kind == "instant":
        # every filing of a balance-sheet date votes (the 10-K and the next 10-Qs' comparatives); the annual column's
        # tag is decided among the tags the annual reports used for that date (a bank's 10-K cash caption, not a
        # 10-Q's narrower one)
        inst = instant_values(facts, tags, unit)
        a = annual_instant_values(facts, tags, unit)
        for e, v in inst.items():  # a FY-end balance no annual report tagged but a later 10-Q re-filed as its comparative
            a.setdefault(e, v)
        q = {e: {"val": v[0], "derived": False, "tag": v[1], "filed": v[2], "accns": list(v[4])} for e, v in inst.items()}
    else:
        a, _ = annual_values(facts, tags, unit, duration=True, absneg=absneg)
        if kind == "direct":
            window = DPS_WINDOW if spec["key"] == "dps" else (80, 120)
            q = quarterly_values(facts, tags, unit, derive=False, direct_window=window, fy_starts=fy_starts, absneg=absneg)
        else:
            q = quarterly_values(facts, tags, unit, derive=True, fy_starts=fy_starts, absneg=absneg)
    if spec["combo"]:
        _combo(spec, facts, unit, fy_starts, a, q)
    if spec["negate"]:
        _apply_sign(spec, a, q)
    return a, q


def _combine_q(q1, q2, tag):
    """Quarterly NII + noninterest income (bank revenue) — both legs needed."""
    out = {}
    for e, d in q1.items():
        o = q2.get(e)
        if o and _num(d.get("val")) and _num(o.get("val")):
            out[e] = dict(d, val=d["val"] + o["val"], tag=tag, derived=bool(d.get("derived") or o.get("derived")),
                          accns=sorted(set(d.get("accns", [])) | set(o.get("accns", []))))
    return out


def fy_consecutive(prev_end, cur_end):
    return 300 <= _days(prev_end, cur_end) <= 400


def quarters_consecutive(ends):
    ends = list(ends)
    return len(ends) >= 1 and all(60 <= _days(a, b) <= 130 for a, b in zip(ends, ends[1:]))


def bank_shape(facts):
    """True when the filer files NoninterestIncome (a bank-only tag) and net interest income."""
    return bool(duration_history(facts, ("us-gaap", "NoninterestIncome"))) and bool(duration_history(facts, ("us-gaap", "InterestIncomeExpenseNet")))


def _q_by_fy(q):
    """{fy_start: {fq: (val, end)}} for fiscal years with all four quarters present in a quarterly map."""
    by = {}
    for e, d in q.items():
        if d.get("fq") and d.get("fy_start") and _num(d.get("val")):
            by.setdefault(d["fy_start"], {})[d["fq"]] = (d["val"], e)
    return {s: qs for s, qs in by.items() if set(qs) == {1, 2, 3, 4}}


def revenue_series(facts, fy_starts, bank, money, warnings):
    """(annual {end: (val, tag, filed, accn)}, quarterly). Banks: the filer's
    own Revenues total when it is filed for every NII period, else NII +
    noninterest income (both legs filed; the sum is marked derived when either
    leg is). Non-banks: PER PERIOD, the filer's own Revenues /
    RevenuesNetOfInterestExpense total replaces the contract-revenue line when
    it exceeds it by >5% (the contract line is a component for lenders,
    brokers and filers that tagged a service component with the contract
    tag — IRM 2018-2019), and a fiscal year whose chosen value disagrees with
    its four quarters while another candidate tag agrees takes that candidate."""
    unit = money
    a, cands = annual_values(facts, REVENUE_TAGS, unit, True)
    q = quarterly_values(facts, REVENUE_TAGS, unit, derive=True, fy_starts=fy_starts)
    ta, _ = annual_values(facts, REVENUE_TOTAL_TAGS, unit, True)
    if bank:
        na, _ = annual_values(facts, NII_TAGS, unit, True)
        oa, _ = annual_values(facts, NONINT_INCOME_TAGS, unit, True)
        nq = quarterly_values(facts, NII_TAGS, unit, derive=True, fy_starts=fy_starts)
        oq = quarterly_values(facts, NONINT_INCOME_TAGS, unit, derive=True, fy_starts=fy_starts)
        both = [e for e in na if e in oa]
        if both and all(e in ta for e in both):
            warnings.append("bank presentation: revenue is the filer's own Revenues total for every period")
            return ta, quarterly_values(facts, REVENUE_TOTAL_TAGS, unit, derive=True, fy_starts=fy_starts)
        tag = "InterestIncomeExpenseNet+NoninterestIncome"
        ann = {e: (na[e][0] + oa[e][0], tag, max(na[e][2] or "", oa[e][2] or ""), na[e][3], sorted(set(na[e][4]) | set(oa[e][4]))) for e in both}
        warnings.append("bank presentation: revenue = net interest income + noninterest income for every period; periods lacking either leg are blank")
        return ann, _combine_q(nq, oq, tag)
    # plausibility first: a fiscal year that disagrees with its own four quarters while another candidate tag agrees
    # (HSY's rounded note-level Revenues facts); a fiscal year BELOW its own nine months (the derived Q4 negative) is
    # impossible for revenue — another candidate at or above the nine months, with a Q4 no larger than twice the
    # biggest filed quarter, is the figure
    fixed = []
    for s, qs in _q_by_fy(q).items():
        fy_end = qs[4][1]
        cur = a.get(fy_end)
        if cur is None:
            continue
        s3, q4, top = sum(qs[k][0] for k in (1, 2, 3)), qs[4][0], max(qs[k][0] for k in (1, 2, 3))
        if s3 <= 0:
            continue
        tot = s3 + q4
        if q4 >= 0 and abs(cur[0] - tot) <= 0.05 * tot:
            continue
        for tag, val, filed, accn in cands.get(fy_end, []):
            if tag == cur[1]:
                continue
            if (q4 >= 0 and abs(val - tot) <= 0.02 * tot) or (q4 < 0 and s3 <= val <= s3 + 2 * top):
                a[fy_end] = (val, tag, filed, accn, [accn] if accn else [])
                alt_q = quarterly_values(facts, [tag], unit, derive=True, fy_starts=fy_starts).get(fy_end)
                if alt_q and _num(alt_q.get("val")) and alt_q["val"] >= 0:
                    q[fy_end] = alt_q
                fixed.append(f"{fy_end} {cur[1]} {cur[0]:,.0f} → {tag} {val:,.0f}")
                break
    if fixed:
        warnings.append(f"revenue: {len(fixed)} fiscal year(s) where the first-choice tag disagrees with the filed quarters (sum of four >5% apart, or a year below its own nine months) while another filed tag agrees — that tag is used ({'; '.join(fixed)})")
    # then the per-period total rule (a lender's quarters switch with its years; a year switched on its own is caught
    # by the basis-break check downstream)
    switched = []
    if ta:
        tq = quarterly_values(facts, REVENUE_TOTAL_TAGS, unit, derive=True, fy_starts=fy_starts)
        for e, tv in ta.items():
            sv = a.get(e)
            if tv[1] != (sv[1] if sv else None) and (sv is None or (sv[0] > 0 and tv[0] > 1.05 * sv[0])):
                a[e] = tv
                switched.append(e)
        for e, td in tq.items():
            sd = q.get(e)
            if _num(td.get("val")) and (sd is None or not _num(sd.get("val")) or (sd["val"] > 0 and td["val"] > 1.05 * sd["val"])):
                q[e] = td
                if sd is not None:
                    switched.append(e)
        if switched:
            warnings.append(f"revenue basis: the filer's own total (Revenues / RevenuesNetOfInterestExpense) is used for {len(switched)} period(s) ({', '.join(sorted(switched))}) where it exceeds the contract-revenue line by >5% — the contract line is a component there")
    revenue_fallbacks(facts, a, q, fy_starts, unit, warnings)
    return a, q


def revenue_fallbacks(facts, a, q, fy_starts, unit, warnings):
    """Fill revenue periods the standard tags leave empty with an industry
    top-line element (REVENUE_FALLBACK_TAGS, in order) — only when that
    element agrees (within 1%) with the chosen revenue in at least as many
    fiscal years as it disagrees, and never by more than 10%, where both are
    filed in the same taxonomy (a component — EQT's OilAndGasRevenue —
    disagrees and is never used; CCL's gross service revenue agrees for
    FY2014-FY2015 and is 2% off two reclassified 2008-2009 comparatives); with no such year (GFI's
    US-GAAP years before its IFRS switch) the element is the filer's only
    revenue figure for those years and is used. Mutates a / q."""
    used, rejected = [], []
    for tag in REVENUE_FALLBACK_TAGS:
        fa, _ = annual_values(facts, [tag], unit, True)
        if not fa:
            continue
        same_tax = {p[1] for p in _pairs(REVENUE_TAGS + REVENUE_TOTAL_TAGS) if p[0] == "us-gaap"}
        overlap = [e for e in fa if e in a and a[e][1] in same_tax]
        agree = sum(1 for e in overlap if _close(fa[e][0], a[e][0], FALLBACK_AGREE_TOL))
        if agree < len(overlap) - agree or any(not _close(fa[e][0], a[e][0], FALLBACK_FAR_TOL) for e in overlap):
            # a component (or another basis): it disagrees with the filer's revenue more often than not, or by >10%
            gaps = [e for e in fa if e not in a]
            if gaps:
                rejected.append(f"{tag} ({len(gaps)} fiscal year(s) {min(gaps)}..{max(gaps)}; agrees in {agree} of {len(overlap)} overlapping year(s))")
            continue
        filled_a = [e for e in fa if e not in a and _num(fa[e][0]) and fa[e][0] >= 0]
        for e in filled_a:
            a[e] = fa[e]
        fq = quarterly_values(facts, [tag], unit, derive=True, fy_starts=fy_starts)
        filled_q = [e for e, d in fq.items() if (e not in q or not _num(q[e].get("val"))) and _num(d.get("val")) and d["val"] >= 0]
        for e in filled_q:
            q[e] = fq[e]
        if filled_a or filled_q:
            span = f" ({min(filled_a)}..{max(filled_a)})" if filled_a else ""
            used.append(f"{tag} for {len(filled_a)} fiscal year(s){span} and {len(filled_q)} quarter(s)"
                        + (f" (agrees with the standard revenue tags in all {len(overlap)} overlapping year(s))" if overlap else " (no overlapping year with the standard tags)"))
    if used:
        warnings.append("revenue: periods the standard revenue tags leave empty are filled from the filer's industry top-line element — " + "; ".join(used))
    if rejected:
        warnings.append("revenue: blank where no standard tag is filed; an industry element that could fill those years is NOT used because it is a component "
                        "(it disagrees with the filer's revenue where both are filed): " + "; ".join(rejected))


def build_periods(core, facts, warnings):
    """core: {key: (annual, quarterly)} for the period-defining lines.
    Returns (annual_ends, quarterly_ends, qmeta) where qmeta[end] = {fq,
    fy_start, filed, accns}. A fiscal year / quarter counts when at least two
    core lines carry it (one line alone for annual-only filers with a single
    core line). A filer with no 10-Q at all (20-F / 40-F with 6-K interims)
    keeps only fiscal years whose four quarters all exist."""
    acount, qcount = {}, {}
    for key, (a, q) in core.items():
        for e, v in a.items():
            if _num(v[0]):
                acount[e] = acount.get(e, 0) + 1
        for e, d in q.items():
            if _num(d.get("val")):
                qcount[e] = qcount.get(e, 0) + 1
    annual_ends = sorted(e for e, n in acount.items() if n >= 2) or sorted(acount)
    quarterly_ends = sorted(e for e, n in qcount.items() if n >= 2)
    qmeta = {}
    for e in quarterly_ends:
        fq = fy_start = None
        filed, accns = None, set()
        for key in ("revenue", "net_income", "ocf", "operating_income"):
            d = core.get(key, (None, {}))[1].get(e)
            if not d:
                continue
            if fq is None and d.get("fq") and d.get("fy_start"):
                fq, fy_start = d["fq"], d["fy_start"]
            f = d.get("filed")
            if f and (filed is None or f < filed):
                filed = f
            accns |= set(d.get("accns") or [])
        qmeta[e] = {"fq": fq, "fy_start": fy_start, "filed": filed, "accns": sorted(a for a in accns if a)}
    if quarterly_ends and not has_quarterly_forms(facts, REVENUE_TAGS + NET_INCOME_TAGS + OCF_TAGS):
        by_fy = {}
        for e in quarterly_ends:
            m = qmeta[e]
            if m["fy_start"] and m["fq"]:
                by_fy.setdefault(m["fy_start"], set()).add(m["fq"])
        keep = [e for e in quarterly_ends if qmeta[e]["fy_start"] and by_fy.get(qmeta[e]["fy_start"]) == {1, 2, 3, 4}]
        if len(keep) != len(quarterly_ends):
            warnings.append(f"quarterly columns: the filer reports interim periods on 6-K only (no 10-Q) — {len(quarterly_ends) - len(keep)} quarter(s) of fiscal years without all four quarters are not shown")
            quarterly_ends = keep
            qmeta = {e: qmeta[e] for e in keep}
    return annual_ends, quarterly_ends, qmeta


def yoy_index(ends):
    """[index of the period ending ~one year earlier or None] per period."""
    out = []
    for i, e in enumerate(ends):
        j = None
        for k in range(i - 1, -1, -1):
            d = _days(ends[k], e)
            if abs(d - 365) <= 20:
                j = k
                break
            if d > 400:
                break
        out.append(j)
    return out


def growth_arrays(values, ends, annual):
    """YoY growth per period: annual vs the prior CONSECUTIVE fiscal year,
    quarterly vs the quarter ending one year earlier (±20 days)."""
    if annual:
        return [(_g(values[i], values[i - 1]) if i and _num(values[i]) and _num(values[i - 1]) and fy_consecutive(ends[i - 1], ends[i]) else None)
                for i in range(len(values))]
    idx = yoy_index(ends)
    return [(_g(values[i], values[j]) if j is not None and _num(values[i]) and _num(values[j]) else None) for i, j in enumerate(idx)]


def ttm_of(values, ends, unit, kind, ttm_quarters):
    """Flow lines: the sum over the four TTM quarters (shares: duration-
    weighted average); instants: the latest quarter's value; None unless every
    quarter carries a value."""
    if not values:
        return None
    if kind == "instant":
        return values[-1] if _num(values[-1]) else None
    if not ttm_quarters:
        return None
    pos = {e: i for i, e in enumerate(ends)}
    vals = [values[pos[e]] if e in pos else None for e in ttm_quarters]
    if len(vals) != 4 or not all(_num(v) for v in vals):
        return None
    if unit == "shares":
        gaps = [_days(ttm_quarters[i - 1], ttm_quarters[i]) for i in range(1, 4)]
        w = [gaps[0]] + gaps
        return sum(v * d for v, d in zip(vals, w)) / sum(w)
    return sum(vals)


def derive_q4_shares(line, annual_vals, annual_ends, q_ends, qmeta):
    """BASIC shares only (a diluted count has no such identity:
    derive_q4_diluted_shares). A 10-K never files a Q4 weighted-average share
    count on its own. When
    the three other quarters of that fiscal year and the FY count are filed
    and mutually consistent (quarters within 25% of each other, the result
    within 25% of the middle one), the Q4 average follows from the DAY-
    WEIGHTED identity of a weighted average: Q4 = (D_FY × FY − Σ d_i × Q_i) /
    d_4 with d_i the quarters' lengths from the fiscal-year start (a 16-week
    first quarter weighs 112 days, not a quarter of the year) — plain
    arithmetic on filed values, rounded to the nearest thousand shares and
    marked derived. Mutates line['quarterly'] / ['derived_quarterly'] in place."""
    fy_by_end = {}
    for i, e in enumerate(annual_ends):
        if _num(annual_vals[i]) and annual_vals[i] > 0:
            fy_by_end[e] = annual_vals[i]
    by_fy = {}
    for i, e in enumerate(q_ends):
        m = qmeta.get(e) or {}
        if m.get("fy_start") and m.get("fq"):
            by_fy.setdefault(m["fy_start"], {})[m["fq"]] = i
    for fs, qs in by_fy.items():
        if set(qs) != {1, 2, 3, 4}:
            continue
        fy_end = q_ends[qs[4]]
        fy_val = fy_by_end.get(fy_end)
        vals = {fq: line["quarterly"][i] for fq, i in qs.items()}
        if fy_val is None or _num(vals[4]) or not all(_num(vals[fq]) and vals[fq] > 0 for fq in (1, 2, 3)):
            continue
        ends = [q_ends[qs[fq]] for fq in (1, 2, 3, 4)]
        d = [_days(fs, ends[0])] + [_days(ends[k - 1], ends[k]) for k in (1, 2, 3)]
        if min(d) <= 0:
            continue
        counts = sorted(vals[fq] for fq in (1, 2, 3))
        derived = (sum(d) * fy_val - sum(d[k] * vals[k + 1] for k in range(3))) / d[3]
        derived = round(derived / 1000.0) * 1000.0 if derived > 1e6 else derived
        if derived > 0 and counts[-1] <= 1.25 * counts[0] and 0.75 * counts[1] <= derived <= 1.25 * counts[1]:
            line["quarterly"][qs[4]] = derived
            line["derived_quarterly"][qs[4]] = True


def _fy_quarter_index(q_ends, qmeta):
    """{fy_start: {fq: index}} for fiscal years with all four quarters among the columns."""
    by_fy = {}
    for i, e in enumerate(q_ends):
        m = qmeta.get(e) or {}
        if m.get("fy_start") and m.get("fq"):
            by_fy.setdefault(m["fy_start"], {})[m["fq"]] = i
    return {fs: qs for fs, qs in by_fy.items() if set(qs) == {1, 2, 3, 4}}


def _ni_common(lines, col, i):
    """Net income to common for a cell, else net income (None when neither is filed)."""
    for k in ("net_income_to_common", "net_income"):
        ln = lines.get(k)
        if ln is not None and _num(ln[col][i]):
            return ln[col][i]
    return None


def derive_q4_diluted_shares(lines, q_ends, qmeta):
    """A diluted weighted-average count has no day-weighted identity
    (antidilution makes it equal the basic count in a loss period; the
    treasury-stock and if-converted results differ by period), so the fiscal
    Q4 diluted count is never derived from the year. In a LOSS fourth quarter
    (Q4 net income to common, else net income, below zero) every potential
    share is antidilutive and the diluted count IS the basic count: the
    derived basic Q4 count is used, marked derived; otherwise Q4 stays blank.
    Mutates the shares_diluted line in place."""
    dil, bas = lines.get("shares_diluted"), lines.get("shares_basic")
    if dil is None or bas is None:
        return
    for i, e in enumerate(q_ends):
        if (qmeta.get(e) or {}).get("fq") != 4 or _num(dil["quarterly"][i]):
            continue
        n = _ni_common(lines, "quarterly", i)
        b = bas["quarterly"][i]
        if _num(n) and n < 0 and _num(b) and b > 0:
            dil["quarterly"][i] = b
            dil["derived_quarterly"][i] = True


def derive_q4_eps(lines, annual_ends, q_ends, qmeta, warnings=None):
    """A 10-K files no fourth-quarter EPS. When the fiscal-year EPS and the
    three FILED quarters' EPS exist (all on today's share basis), Q4 EPS = FY
    EPS − Q1 − Q2 − Q3 — plain arithmetic on filed per-share figures, marked
    derived — so the TTM EPS can be summed. Not derived when the year's four
    net-income quarters do not sum to its net income (>1%: the quarters and
    the year were filed on different bases) or when the result's sign is
    opposite to the Q4 net income (to common) by more than a cent. A filed Q4
    EPS is never replaced. Mutates the eps lines in place."""
    apos = {e: i for i, e in enumerate(annual_ends)}
    ni = lines.get("net_income")
    skipped = []
    for key in ("eps_basic", "eps_diluted"):
        eps = lines.get(key)
        if eps is None:
            continue
        for fs, qs in _fy_quarter_index(q_ends, qmeta).items():
            i4 = qs[4]
            fy_end = q_ends[i4]
            ai = apos.get(fy_end)
            if ai is None or _num(eps["quarterly"][i4]) or not _num(eps["annual"][ai]):
                continue
            three = [eps["quarterly"][qs[k]] for k in (1, 2, 3)]
            if not all(_num(v) for v in three) or any(eps["derived_quarterly"][qs[k]] for k in (1, 2, 3)):
                continue
            if ni is not None and _num(ni["annual"][ai]):
                nq = [ni["quarterly"][qs[k]] for k in (1, 2, 3, 4)]
                if all(_num(v) for v in nq) and abs(sum(nq) - ni["annual"][ai]) > BASIS_BREAK_TOL * max(abs(ni["annual"][ai]), 1e-9):
                    skipped.append(f"{key} {fy_end}")
                    continue
            v = round(eps["annual"][ai] - sum(three), 6)
            n4 = _ni_common(lines, "quarterly", i4)
            if _num(n4) and n4 != 0 and v != 0 and (v > 0) != (n4 > 0) and abs(v) > 0.01:
                skipped.append(f"{key} {fy_end}")
                continue
            eps["quarterly"][i4] = v
            eps["derived_quarterly"][i4] = True
    if skipped and warnings is not None:
        warnings.append(f"Q4 EPS not derived (FY EPS − three filed quarters) where the year's quarters and the year were filed on different bases or the result's "
                        f"sign contradicts the Q4 net income: {', '.join(sorted(set(skipped))[:8])}{'...' if len(set(skipped)) > 8 else ''}")


def eps_sign_check(lines, annual_ends, q_ends, warnings):
    """Per-cell sanity on EPS where the period's filings DISAGREE (a period
    every filing agrees on is kept as filed): an EPS whose sign is opposite to
    net income to common (else net income), or an EPS of 0, while that income
    ÷ the period's share count is at least a cent, is a filing slip — blanked,
    warned."""
    out = []
    for key, sh_key in (("eps_basic", "shares_basic"), ("eps_diluted", "shares_diluted")):
        ln, sh = lines.get(key), lines.get(sh_key)
        if ln is None or sh is None:
            continue
        for col, ends, tmap, dis in (("annual", annual_ends, "_atags", "_adis"), ("quarterly", q_ends, "_qtags", "_qdis")):
            for i, v in enumerate(ln[col]):
                if not _num(v) or not (ln.get(dis) or {}).get(ends[i]):
                    continue
                n, c = _ni_common(lines, col, i), sh[col][i]
                if not (_num(n) and _num(c) and c > 0) or abs(n / c) < 0.01:
                    continue
                if v == 0 or (v > 0) != (n > 0):
                    out.append(f"{key} {ends[i]} {v:g} (income {n:,.0f})")
                    ln[col][i] = None
                    ln[tmap].pop(ends[i], None)
                    if col == "quarterly":
                        ln["derived_quarterly"][i] = False
        _retag(ln)
    if out:
        warnings.append(f"EPS blanked where the period's filings disagree and the shown figure contradicts the period's net income (opposite sign, or 0 against "
                        f"at least a cent a share): {'; '.join(out[:8])}{'; ...' if len(out) > 8 else ''}")


# ---------------------------------------------------------------------------
# Stock splits (per-share and share-count lines to today's share basis)
# ---------------------------------------------------------------------------
SIMPLE_RATIOS = (2.0, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0, 1.5)
REFILE_RATIO_TOL = 1.03   # a re-filed count within 3% of a simple ratio is that ratio
INFER_CLUSTER_DAYS = 400  # re-filings of several periods on the new basis spread over the following year's comparatives


SPLIT_SHARE_TAGS = ("StockIssuedDuringPeriodSharesReverseStockSplits", "StockIssuedDuringPeriodSharesStockSplits")
CORROBORATE_SLACK = 120  # a split-shares instant may be dated up to ~4 months before the last filing on the old basis (approval vs effect)


def split_share_dates(facts):
    """Instant dates of the filer's split-shares facts (StockIssuedDuringPeriodSharesReverseStockSplits /
    ...StockSplits): the effective date of a split it never tagged a ratio for (DFTX 2022-08-26)."""
    out = set()
    for tag in SPLIT_SHARE_TAGS:
        for es in _tag_facts(facts, ("us-gaap", tag)).values():
            for e in es:
                if e.get("end") and not (e.get("start") and e["start"] != e["end"]):
                    out.add(e["end"])
    return sorted(out)


def _snap_whole(k, tol=REFILE_RATIO_TOL, max_n=100):
    """k as n or 1/n (n whole, 2..max_n) within `tol`, else None."""
    if k <= 0:
        return None
    n = round(k) if k >= 1 else round(1.0 / k)
    if n < 2 or n > max_n:
        return None
    r = float(n) if k >= 1 else 1.0 / n
    return r if abs(math.log(k) - math.log(r)) <= math.log(tol) else None


def inferred_splits(refilings, tagged, corroborations=()):
    """Splits the filer never tagged with a ratio fact (CTSH's 2-for-1 of
    2014, ACGL's 3-for-1 of 2011, DFTX's 1-for-15 of 2022) read from the
    filings themselves. Uncorroborated: the diluted share count of at least
    TWO periods re-filed at one simple ratio (×2, ×3 … or the inverse), the
    earliest such re-filing being the first filing on the new basis.
    Corroborated by a split-shares instant (`corroborations`, dated between
    the last old-basis filing − 120 days and the re-filing): ANY whole ratio
    (n or 1/n, n ≤ 100) from even one period, dated and cut off at that
    instant — the filings after the split's effective date are on the new
    basis. A tagged split with the same ratio within 400 days already covers
    it. refilings: share_refilings(); tagged: [(date, ratio, cutoff)].
    Returns [(cutoff, ratio, cutoff, n_periods)]."""
    by_ratio, corro = {}, {}
    for e, k, old_filed, new_filed in refilings:
        if not new_filed or k <= 0:
            continue
        c = next((d for d in corroborations if old_filed and -CORROBORATE_SLACK <= _days(old_filed, d) and d <= new_filed), None)
        if c is not None:
            r = _snap_whole(k)
            if r is not None:
                corro.setdefault((r, c), set()).add(e)
                continue
        for r in SIMPLE_RATIOS + tuple(1.0 / x for x in SIMPLE_RATIOS):
            if abs(math.log(k) - math.log(r)) <= math.log(REFILE_RATIO_TOL):
                by_ratio.setdefault(r, []).append((new_filed, e))
                break

    def covered(r, when):
        return any(abs(math.log(used) - math.log(r)) <= math.log(1.1) and -INFER_CLUSTER_DAYS <= _days(tc or d, when) <= INFER_CLUSTER_DAYS
                   for d, used, tc in tagged)
    out = []
    for (r, c), periods in corro.items():
        if not covered(r, c):
            out.append((c, r, c, len(periods)))
    for r, items in by_ratio.items():
        items.sort()
        clusters, cur = [], []
        for nf, e in items:
            if cur and _days(cur[0][0], nf) > INFER_CLUSTER_DAYS:
                clusters.append(cur)
                cur = []
            cur.append((nf, e))
        if cur:
            clusters.append(cur)
        for cl in clusters:
            periods = {e for _, e in cl}
            if len(periods) < 2:
                continue
            cutoff = cl[0][0]
            if not covered(r, cutoff) and not any(abs(math.log(rr) - math.log(r)) <= math.log(1.1) and abs(_days(c, cutoff)) <= INFER_CLUSTER_DAYS for c, rr, _, _ in out):
                out.append((cutoff, r, cutoff, len(periods)))
    return sorted(out)


SPLIT_ANCHOR_AHEAD = 200     # a filing can disclose a split that takes effect up to ~6 months after it is filed
SPLIT_COMPARATIVE_DAYS = 1300  # a split's ratio is re-tagged in comparative contexts for ~3 years of later filings
SPLIT_CHAIN_DAYS = 400       # filings of one un-anchored ratio less than ~a year apart describe the same split


def split_events_dedup(facts, kinds=None):
    """[(effective_date, ratio)] — ONE event per stock split, however many
    contexts its ratio fact is tagged in. A ratio fact on a DURATION context
    (DXCM tags its 4-for-1 of 2022-06-10 against FY2019, FY2020, 6M/9M/FY2021
    as restated comparatives) says nothing about when the split happened; only
    an instant context does. So: instant dates are the events (dates of one
    ratio within SPLIT_DUPLICATE_DAYS — approval, record, distribution — are
    one event at the first); a duration fact (in filing-date order) belongs to
    the latest same-ratio event dated no later than SPLIT_ANCHOR_AHEAD days
    after its filing and no more than SPLIT_COMPARATIVE_DAYS before it, whose
    OWN chain of filings (the instant facts' and the durations already
    attached, gaps ≤ SPLIT_CHAIN_DAYS) reaches the fact's filing, and whose
    date is not a year before the context starts (a period wholly after the
    split describes another one) — so a second split of the same ratio a few
    years on (WRB's 3-for-2 of 2019, 2022 and 2024) is never absorbed into the
    first. Duration facts with no such event are chained by filing date
    (gaps ≤ SPLIT_CHAIN_DAYS) into one event each, dated by the latest context
    end of the chain's first filing (capped at that filing date). `kinds`
    (optional dict) receives {date: "instant" | "duration"}."""
    from fundamentals import SPLIT_DUPLICATE_DAYS
    inst, dur, raw = {}, [], {}
    for taxonomy, tag in _pairs(DUR["split_ratio"]):
        for es in _tag_facts(facts, (taxonomy, tag)).values():
            for e in es:
                d, v = e.get("end"), e.get("val")
                if not d or not _num(v) or v <= 0 or v == 1:
                    continue
                r = f"{float(v):.4g}"  # 0.3775 and 0.377501 are one ratio (keyed by 4 significant digits, the first filed value kept)
                raw.setdefault(r, float(v))
                if e.get("start") and e["start"] != d:
                    dur.append((e.get("filed") or d, d, r, e["start"]))
                else:
                    f = e.get("filed") or d
                    inst.setdefault(r, {})
                    inst[r][d] = max(inst[r].get(d, f), f)
    events, last_filed = [], {}
    for r, ds in inst.items():
        for d in sorted(ds):
            if events and events[-1][1] == r and _days(events[-1][0], d) <= SPLIT_DUPLICATE_DAYS:
                key = events[-1]
                last_filed[key] = max(last_filed[key], ds[d])
                continue
            events.append((d, r))
            last_filed[(d, r)] = ds[d]
    loose = {}
    for filed, end, r, start in sorted(dur):
        anchors = [ev for ev in events if ev[1] == r and -SPLIT_COMPARATIVE_DAYS <= _days(filed, ev[0]) <= SPLIT_ANCHOR_AHEAD
                   and _days(last_filed[ev], filed) <= SPLIT_CHAIN_DAYS and _days(ev[0], start) <= SPLIT_CHAIN_DAYS]
        if anchors:
            ev = max(anchors)
            last_filed[ev] = max(last_filed[ev], filed)
        else:
            loose.setdefault(r, []).append((filed, end))
    out_kind = {d: "instant" for d, _ in events}
    for r, items in loose.items():
        chains, cur = [], []
        for filed, end in items:
            if cur and _days(cur[-1][0], filed) > SPLIT_CHAIN_DAYS:
                chains.append(cur)
                cur = []
            cur.append((filed, end))
        if cur:
            chains.append(cur)
        for ch in chains:
            first = ch[0][0]
            d = min(max(end for filed, end in ch if filed == first), first)
            events.append((d, r))
            out_kind.setdefault(d, "duration")
    events.sort()
    out = []
    for d, r in events:  # an un-anchored chain that lands next to an instant event of the same ratio is that event
        if any(rr == r and abs(_days(dd, d)) <= SPLIT_DUPLICATE_DAYS for dd, rr in out):
            continue
        out.append((d, r))
    if kinds is not None:
        kinds.update({d: out_kind.get(d, "duration") for d, _ in out})
    return [(d, raw[r]) for d, r in out]


def diluted_counts_with_filed(facts):
    """{(start, end): (diluted weighted shares, filed)} — every fiscal-year AND quarter count (3-month or year-to-date),
    each period's newest filing (anomalies dropped)."""
    out = {}
    for pair in _pairs(DUR["shares_diluted"]):
        for k, es in duration_history(facts, pair, "shares").items():
            if es and k not in out and (60 <= _days(*k) <= 380):
                out[k] = (es[-1][1], es[-1][0])
    return out


def split_borne_out(d, ratio, counts, instant=True):
    """A tagged split with no re-filed share count to date it is applied only
    when the filings bear it out: nothing was filed before it (a pre-IPO
    split — nothing to restate), or the last diluted count (fiscal year OR
    quarter) filed before it and the first count for a later period filed
    after it move by that ratio (within 25%). A flat count is no split (Q's
    0.5 of 2026 is the spin-off distribution ratio — one Qnity share per two
    DuPont shares — and its Q1 2026 count of 210.3M follows FY2025's 209.8M;
    CFG's ratio 6 tagged against FY2021, counts flat). With no count filed
    since, an instant-dated split is applied; a ratio tagged only on duration
    contexts is not (nothing moves by it). counts: {(start, end): (val, filed)}
    or {end: (val, filed)}."""
    def end_of(k):
        return k[1] if isinstance(k, tuple) else k
    pre = [(end_of(k), v) for k, (v, f) in counts.items() if f and f < d and _num(v) and v > 0]
    if not pre:
        return True
    last_end = max(e for e, _ in pre)
    last = [v for e, v in pre if e == last_end][-1]
    post = sorted((end_of(k), f, v) for k, (v, f) in counts.items() if f and f >= d and _num(v) and v > 0 and end_of(k) > last_end)
    if not post:
        return instant
    obs = post[0][2] / last
    return abs(math.log(obs) - math.log(ratio)) <= math.log(1.25)


def split_schedule(facts, notes=None):
    """[(date, ratio_used, first_post_split_filing)] — fundamentals' split
    machinery on de-duplicated events (split_events_dedup: one event per
    split, however many comparative contexts its ratio is tagged in),
    direction checked against the diluted counts, the basis change dated by
    the first filing that re-filed a share count on the new basis, plus the
    splits inferred from re-filed share counts alone (inferred_splits; `notes`
    receives one line per inferred event)."""
    refilings = share_refilings(facts)
    kinds = {}
    events = split_events_dedup(facts, kinds)
    tagged = []
    if events:
        shares = _shares_with_filed(facts)
        counts = diluted_counts_with_filed(facts)
        directed = split_direction(events, shares)
        cutoffs = split_filing_cutoffs([(d, used) for d, r, used, ev in directed], refilings)
        for d, r, used, ev in directed:
            cutoff = cutoffs.get(d, (None, None))[0]
            if cutoff is None and not split_borne_out(d, used, counts or shares, instant=kinds.get(d) == "instant"):
                if notes is not None:
                    notes.append(f"split ratio not applied: a {_split_desc(d, used)} is tagged, but no share count was re-filed on a new basis and the "
                                 f"diluted counts filed before and after it (fiscal years and quarters) do not move by that ratio — the filings never "
                                 f"changed share basis (a spin-off distribution ratio or a mis-tagged fact)")
                continue
            tagged.append((d, used, cutoff))
    inferred = inferred_splits(refilings, tagged, split_share_dates(facts))
    for cutoff, r, _, n in inferred:
        if notes is not None:
            notes.append(f"split inferred from the filings: the diluted share count of {n} period(s) was re-filed ×{r:.4g} with no split-ratio fact tagged — read as a "
                         f"{_split_desc(cutoff, r)}; values last filed before {cutoff} are restated")
    return sorted(tagged + [(c, r, c) for c, r, _, n in inferred])


def _scaled(v, k):
    """v × k, the binary-float noise of a split ratio (÷ 1/15 → −1.9500000000000002) trimmed to 12 significant digits."""
    return v if k == 1.0 else float(f"{v * k:.12g}")


def _split_scale(unit, filed, splits):
    """Multiplier that restates a value last filed on `filed` to today's share
    basis: shares × factor, per-share ÷ factor; 1 when nothing applies."""
    if not splits or not filed:
        return 1.0
    f = split_factor(filed, splits)
    if f == 1:
        return 1.0
    return f if unit == "shares" else 1.0 / f


# ---------------------------------------------------------------------------
# Assembly
# ---------------------------------------------------------------------------
def assemble_lines(facts, bank, annual_ends, q_ends, qmeta, fy_starts, money, splits, warnings, revenue=None):
    """Every filed (non-derived) line of every statement as
    {key: line-dict-without-growth}, plus the hidden helpers. Derived lines
    are added by add_derived. `revenue` = the (annual, quarterly) revenue
    series chosen by revenue_series."""
    lines = {}
    split_touched = {}
    for stmt, specs in STATEMENTS + (("hidden", HIDDEN),):
        for spec in specs:
            if spec["derived"] or (spec["bank"] is not None and spec["bank"] != bank):
                continue
            if spec["key"] in lines and stmt != "hidden":
                continue
            if spec["key"] == "revenue" and revenue is not None:
                a, q = revenue
            else:
                a, q = _series_for(spec, facts, fy_starts, money)
            if spec["key"] in STICKY_TAG_LINES:
                sticky_tags(spec, facts, a, q, fy_starts, money, warnings)
            scale = spec["unit"] in ("shares", "per_share")
            annual, quarterly, dq, atags, qtags, aaccn, qaccn, aall, adis, qdis = [], [], [], {}, {}, {}, {}, {}, {}, {}
            for e in annual_ends:
                v = a.get(e)
                if v is None:
                    annual.append(None)
                    continue
                k = _split_scale(spec["unit"], v[2], splits) if scale else 1.0
                if k != 1.0:
                    split_touched.setdefault(spec["key"], []).append(e)
                annual.append(_scaled(v[0], k))
                atags[e], aaccn[e] = v[1], (list(v[4]) if len(v) > 4 and v[4] else ([v[3]] if v[3] else []))
                aall[e] = list(v[5]) if len(v) > 5 and v[5] else list(aaccn[e])
                adis[e] = bool(v[6]) if len(v) > 6 else False
            for e in q_ends:
                d = q.get(e)
                if d is None or not _num(d.get("val")):
                    quarterly.append(None)
                    dq.append(False)
                    continue
                k = _split_scale(spec["unit"], d.get("filed"), splits) if scale else 1.0
                if k != 1.0:
                    split_touched.setdefault(spec["key"], []).append(e)
                quarterly.append(_scaled(d["val"], k))
                dq.append(bool(d.get("derived")))
                qtags[e], qaccn[e] = d.get("tag"), [x for x in (d.get("accns") or []) if x]
                qdis[e] = bool(d.get("disagree"))
            if spec["nonneg"]:
                bad = [i for i, v in enumerate(quarterly) if dq[i] and _num(v) and v < 0]
                if bad:
                    warnings.append(f"{spec['key']}: {len(bad)} derived quarter(s) ({', '.join(q_ends[i] for i in bad)}) came out negative — the fiscal-year (or year-to-date) figure and the leg subtracted from it are on different bases (a restatement, reclassification or discontinued operations); not shown")
                    for i in bad:
                        quarterly[i], dq[i] = None, False
                        qtags.pop(q_ends[i], None)
            tags = sorted({t for t in atags.values() if t} | {t for t in qtags.values() if t})
            label = spec["label"]  # (the net label, when every figure is net, is set by net_interest_dedupe)
            line = {"key": spec["key"], "label": label, "level": spec["level"], "total": bool(spec["total"]), "unit": spec["unit"],
                    "annual": annual, "quarterly": quarterly, "ttm": None, "derived_quarterly": dq, "tags": tags, "_kind": spec["kind"], "_stmt": stmt,
                    "_atags": atags, "_qtags": qtags, "_aaccn": aaccn, "_qaccn": qaccn, "_aall": aall, "_adis": adis, "_qdis": qdis, "_spec": spec}
            if spec["cf_sign"] is not None:
                line["cf_sign"] = spec["cf_sign"]
            lines[spec["key"]] = line
    # lines that exist only as a last resort
    for key, line in list(lines.items()):
        other = line["_spec"]["only_if_absent"]
        if other and other in lines and any(_num(v) for v in lines[other]["annual"] + lines[other]["quarterly"]):
            del lines[key]
    # period-end shares: the balance-sheet count first, the cover-page dei count within 75 days as the fallback
    so = lines.get("shares_outstanding")
    if so is not None:
        dei_a = dei_shares_by_period(facts, [e for i, e in enumerate(annual_ends) if not _num(so["annual"][i])])
        dei_q = dei_shares_by_period(facts, [e for i, e in enumerate(q_ends) if not _num(so["quarterly"][i])])
        for i, e in enumerate(annual_ends):
            if e in dei_a:
                k = _split_scale("shares", dei_a[e][1], splits)
                so["annual"][i] = _scaled(dei_a[e][0], k)
                if k != 1.0:
                    split_touched.setdefault("shares_outstanding", []).append(e)
        for i, e in enumerate(q_ends):
            if e in dei_q:
                k = _split_scale("shares", dei_q[e][1], splits)
                so["quarterly"][i] = _scaled(dei_q[e][0], k)
                if k != 1.0:
                    split_touched.setdefault("shares_outstanding", []).append(e)
        if dei_a or dei_q:
            so["tags"] = sorted(set(so["tags"]) | {"dei:EntityCommonStockSharesOutstanding"})
    if split_touched:
        desc = "; ".join(_split_desc(*_split_cutoff(s)) for s in splits)
        parts = ", ".join(f"{k} ({len(set(v))})" for k, v in sorted(split_touched.items()))
        warnings.append(f"split adjustment: per-share and share-count cells last filed before the {desc} are restated to today's share basis with the filed ratio (per share ÷ ratio, shares × ratio): {parts}")
    continuing_eps_fallback(facts, lines, annual_ends, q_ends, fy_starts, money, splits, warnings)
    implausible_cells(lines, annual_ends, q_ends, warnings)
    eps_sign_check(lines, annual_ends, q_ends, warnings)
    if "shares_basic" in lines:
        derive_q4_shares(lines["shares_basic"], lines["shares_basic"]["annual"], annual_ends, q_ends, qmeta)
    derive_q4_diluted_shares(lines, q_ends, qmeta)
    derive_q4_eps(lines, annual_ends, q_ends, qmeta, warnings)
    dedupe_same_fact(lines, annual_ends, q_ends, warnings)
    net_interest_dedupe(facts, lines, annual_ends, q_ends, fy_starts, money, warnings)
    reconcile_nonoperating(lines, annual_ends, q_ends, warnings)
    unpaired_quarters(facts, lines, q_ends, qmeta, money, warnings)
    zero_unfiled_components(facts, lines, annual_ends, q_ends, qmeta, money, warnings)
    capex_gap_warning(facts, lines, annual_ends, q_ends, warnings)
    opex_gap_warning(lines, annual_ends, warnings)
    restricted_cash_split(facts, lines, annual_ends, q_ends, money, warnings)
    return lines


STICKY_TAG_LINES = ("capex",)


def sticky_tags(spec, facts, a, q, fy_starts, money, warnings):
    """One definition per series: walking the periods in order, a period
    whose priority tag differs from the previous period's keeps the PREVIOUS
    tag while the filer still files it for that period (EXR files
    PaymentsToDevelopRealEstateAssets every year — 62.0M / 100.2M / 128.6M /
    143.0M for FY2022-FY2025 — while a higher-priority
    PaymentsToAcquireProductiveAssets, 1,193.3M / 135.6M / …, appears from
    FY2022: the series stays on development spending instead of jumping on a
    change of definition). A tag change that remains is warned and blanks the
    growth across it (annual_generation_breaks). Mutates a / q."""
    unit = unit_for(spec, money)
    absneg = spec["key"] in PAYMENT_LINES
    cache_a, cache_q = {}, {}

    def ann(tag):
        if tag not in cache_a:
            cache_a[tag] = annual_values(facts, [tag], unit, duration=True, absneg=absneg)[0]
        return cache_a[tag]

    def qtr(tag):
        if tag not in cache_q:
            cache_q[tag] = quarterly_values(facts, [tag], unit, derive=True, fy_starts=fy_starts, absneg=absneg)
        return cache_q[tag]
    kept, changes = [], []
    prev = None
    for e in sorted(a):
        t = a[e][1]
        if prev and t != prev and "+" not in prev:
            alt = ann(prev).get(e)
            if alt is not None and _num(alt[0]):
                a[e] = alt
                kept.append(e)
                continue
        if prev and t != prev:
            changes.append(f"{e} {prev} → {t}")
        prev = t
    prev = None
    for e in sorted(q):
        t = q[e].get("tag")
        if prev and t != prev and "+" not in prev:
            alt = qtr(prev).get(e)
            if alt is not None and _num(alt.get("val")):
                q[e] = alt
                continue
        prev = t
    if kept:
        warnings.append(f"{spec['key']}: one caption per series — {len(kept)} fiscal year(s) ({kept[0]}..{kept[-1]}) keep the tag the earlier years used, "
                        f"which the filer still files, instead of a higher-priority caption that appeared later (a change of definition, not of business)")
    if changes:
        warnings.append(f"{spec['key']}: the filed caption changes ({'; '.join(changes[:4])}) — growth across a change is blank")


def _retag(line):
    line["tags"] = sorted({t for t in line["_atags"].values() if t} | {t for t in line["_qtags"].values() if t})


def continuing_eps_fallback(facts, lines, annual_ends, q_ends, fy_starts, money, splits, warnings):
    """A filer that tags only continuing-operations EPS (HAL FY2022-FY2025:
    IncomeLossFromContinuingOperationsPerDilutedShare 1.73 / 2.92 / 2.83 /
    1.50 and no EarningsPerShareDiluted) has the same figure as its EPS when it
    reports no discontinued operations in that period — used for empty EPS
    cells only where the discontinued-operations line is blank or zero."""
    disc = lines.get("discontinued_ops")
    unit = f"{money}/shares"
    for key, tag in EPS_CONTINUING.items():
        ln = lines.get(key)
        if ln is None:
            continue
        a, _ = annual_values(facts, [tag], unit)
        q = quarterly_values(facts, [tag], unit, derive=False, fy_starts=fy_starts)
        if not a and not q:
            continue
        filled = []
        for col, ends, src, tmap in (("annual", annual_ends, a, ln["_atags"]), ("quarterly", q_ends, q, ln["_qtags"])):
            for i, e in enumerate(ends):
                if _num(ln[col][i]) or e not in src:
                    continue
                if disc is not None and _num(disc[col][i]) and disc[col][i] != 0:
                    continue
                v, filed = (src[e][0], src[e][2]) if col == "annual" else (src[e].get("val"), src[e].get("filed"))
                if not _num(v):
                    continue
                ln[col][i] = _scaled(v, _split_scale("per_share", filed, splits))
                tmap[e] = tag
                filled.append(e)
        if filled:
            _retag(ln)
            warnings.append(f"{key}: {len(filled)} period(s) ({min(filled)}..{max(filled)}) carry no EPS tag — the filed continuing-operations EPS ({tag}) is shown, "
                            f"only where the period reports no discontinued operations")


def implausible_cells(lines, annual_ends, q_ends, warnings):
    """Last-resort per-cell sanity on the per-share and share-count lines
    after the anomaly rules: an EPS / DPS cell above 1,000 in
    absolute value AND 100× the line's median, or a share count below 1/100 or
    above 100× the line's median (ECHO's 2023 quarters re-filed as 307,410
    "shares" against ~300M), is a filing slip — blanked, warned."""
    out = []
    for key in ("eps_basic", "eps_diluted", "dps", "shares_basic", "shares_diluted", "shares_outstanding"):
        ln = lines.get(key)
        if ln is None:
            continue
        vals = sorted(abs(v) for v in ln["annual"] + ln["quarterly"] if _num(v) and v)
        if len(vals) < 3:
            continue
        med = vals[len(vals) // 2]
        for col, ends, tmap in (("annual", annual_ends, ln["_atags"]), ("quarterly", q_ends, ln["_qtags"])):
            for i, v in enumerate(ln[col]):
                if not _num(v) or not v:
                    continue
                if ln["unit"] == "per_share":
                    bad = abs(v) > 1000 and abs(v) > 100 * med
                else:
                    bad = abs(v) < med / 100 or abs(v) > med * 100
                if bad:
                    out.append(f"{key} {ends[i]} {v:,.4g}")
                    ln[col][i] = None
                    tmap.pop(ends[i], None)
                    if col == "quarterly":
                        ln["derived_quarterly"][i] = False
        _retag(ln)
    if out:
        warnings.append(f"implausible per-share / share-count cells blanked (more than 100× off the line's median — a filing's scale slip): {'; '.join(out)}")


SAME_FACT_PAIRS = (("short_term_debt", "current_lt_debt"), ("long_term_debt", "current_lt_debt"), ("long_term_debt", "short_term_debt"))


def dedupe_same_fact(lines, annual_ends, q_ends, warnings):
    """Two debt lines that resolve to the SAME filed fact in a period — the
    same value for the same date in the same filing, tagged under two
    elements (GFI's one face line "Current portion of borrowings" 719.1M is
    tagged ShorttermBorrowings AND CurrentBorrowingsAndCurrentPortionOf-
    NoncurrentBorrowings) — are one figure: the later line's cell is blanked,
    so neither the statement nor total debt counts it twice."""
    hits = []
    for k1, k2 in SAME_FACT_PAIRS:
        a, b = lines.get(k1), lines.get(k2)
        if a is None or b is None:
            continue
        for col, ends, amap, tmap in (("annual", annual_ends, "_aaccn", "_atags"), ("quarterly", q_ends, "_qaccn", "_qtags")):
            for i, e in enumerate(ends):
                va, vb = a[col][i], b[col][i]
                if not (_num(va) and _num(vb)) or not va or not _close(va, vb, 1e-9):
                    continue
                if set(a[amap].get(e) or []) & set(b[amap].get(e) or []):
                    b[col][i] = None
                    ta, tb = a[tmap].get(e), b[tmap].pop(e, None)
                    hits.append((e, k1, ta, k2, tb, va))
        _retag(b)
    if hits:
        ex = hits[-1]
        warnings.append(f"debt: {len(hits)} cell(s) where two debt lines are the same filed fact (same value, date and filing under two tags) are counted once — "
                        f"e.g. {ex[0]} {ex[1]} ({ex[2]}) = {ex[3]} ({ex[4]}) = {ex[5]:,.0f}; the {ex[3]} cell is blank")


def net_interest_dedupe(facts, lines, annual_ends, q_ends, fy_starts, money, warnings):
    """A period's interest-expense figure is the NET one (interest income
    already inside it) when it came from a net tag (KR FY2026's
    InterestIncomeExpenseNonoperatingNet, negated: 639M) OR when a gross tag's
    value equals minus a net tag's value for the same period in any filing
    (within 0.5%: KR's FY2023 / FY2024 10-Ks tagged the face "Interest
    expense" 535M / 441M under InterestExpense while InterestIncomeExpense-
    NonoperatingNet carries −441M for FY2024 — the same net figure, with the
    118M of interest income a Note 5 component of it). For those periods the
    separate interest-income line is blanked so the statement never shows it
    twice. The line is labelled "Interest expense, net" only when every
    figure it shows is net; a row mixing gross and net periods keeps the
    generic "Interest expense" and the warning names the net periods."""
    ie, ii = lines.get("interest_expense"), lines.get("interest_income")
    if ie is None:
        return
    neg = ie["_spec"]["negate"]
    pairs = _pairs(NET_INTEREST_TAGS)
    hists = [duration_history(facts, pr, money) for pr in pairs]
    netq = quarterly_values(facts, NET_INTEREST_TAGS, money, derive=True, fy_starts=fy_starts)

    def filed_net(col, e, v):
        if col == "annual":
            cands = [x[1] for h in hists for (s0, e0), es in h.items() if e0 == e and is_fy(s0, e0) for x in es]
        else:
            cands = [x[1] for h in hists for (s0, e0), es in h.items() if e0 == e and 80 <= _days(s0, e0) <= 120 for x in es]
            d = netq.get(e)
            if d and _num(d.get("val")):
                cands.append(d["val"])
        return any(_close(-c, v) for c in cands if _num(c))

    net_cells, gross_cells, blanked = [], 0, []
    for col, ends, emap, imap in (("annual", annual_ends, ie["_atags"], ii["_atags"] if ii else {}), ("quarterly", q_ends, ie["_qtags"], ii["_qtags"] if ii else {})):
        for i, e in enumerate(ends):
            v = ie[col][i]
            if not _num(v):
                continue
            is_net = emap.get(e) in neg or (v != 0 and filed_net(col, e, v))
            if not is_net:
                gross_cells += 1
                continue
            net_cells.append((col, e, emap.get(e) in neg))
            if ii is not None and _num(ii[col][i]):
                ii[col][i] = None
                imap.pop(e, None)
                if col == "quarterly":
                    ii["derived_quarterly"][i] = False
                blanked.append(e)
    if net_cells and not gross_cells:
        ie["label"] = ie["_spec"]["net_label"] or ie["label"]
    else:
        ie["label"] = ie["_spec"]["label"]
    if blanked:
        _retag(ii)
        warnings.append(f"interest income: blank for {len(blanked)} period(s) where the interest-expense figure is the filer's NET interest (income already inside it)")
    via_gross = sorted({e for col, e, by_tag in net_cells if not by_tag})
    if net_cells and gross_cells:
        nets = sorted({e for _, e, _ in net_cells})
        warnings.append(f"interest expense: the row mixes gross and NET figures, so it keeps the label \"Interest expense\"; net (income inside) for {len(nets)} "
                        f"period(s) {nets[0]}..{nets[-1]}" + (f" — including {len(via_gross)} filed under the gross tag whose value equals minus the filer's net "
                                                               f"interest tag for that period" if via_gross else ""))
    elif via_gross:
        warnings.append(f"interest expense: {len(via_gross)} period(s) filed under the gross tag carry the same figure as minus the filer's net interest tag — read as net")


def reconcile_nonoperating(lines, annual_ends, q_ends, warnings):
    """`NonoperatingIncomeExpense` is the whole non-operating section for many
    filers (interest expense inside it) and the face "other" line for others.
    Per period, when it supplied the value and an interest line exists, the
    two readings are tested against pretax income: OI + nonop = pretax means it
    is the total — the other line becomes nonop + interest expense − interest
    income (plain arithmetic, tag recorded); OI − interest + income + nonop =
    pretax means it is the face line (kept); neither → blank."""
    on, oi, pre = lines.get("other_nonoperating"), lines.get("operating_income"), lines.get("pretax_income")
    ie, ii = lines.get("interest_expense"), lines.get("interest_income")
    if on is None:
        return
    derived, blanked = [], []
    for col, ends, tagmap in (("annual", annual_ends, on["_atags"]), ("quarterly", q_ends, on["_qtags"])):
        for i, e in enumerate(ends):
            if tagmap.get(e) != "NonoperatingIncomeExpense" or not _num(on[col][i]):
                continue
            x = lambda ln: (ln[col][i] if (ln is not None and _num(ln[col][i])) else None)  # noqa: E731
            exp, inc = x(ie), x(ii)
            if exp is None and inc is None:
                continue  # no interest line this period: the tag is the only non-operating figure there is
            exp, inc = exp or 0.0, inc or 0.0
            o, p, n = x(oi), x(pre), on[col][i]
            tol = max(abs(p or 0.0) * 0.01, 1.0)
            if o is not None and p is not None:
                if abs(o + n - p) <= tol and abs(o - exp + inc + n - p) > tol:
                    on[col][i] = n + exp - inc
                    tagmap[e] = "NonoperatingIncomeExpense+InterestExpense-InterestIncome"
                    derived.append(e)
                    continue
                if abs(o - exp + inc + n - p) <= tol:
                    continue
            on[col][i] = None
            tagmap.pop(e, None)
            if col == "quarterly":
                on["derived_quarterly"][i] = False
            blanked.append(e)
    if derived or blanked:
        on["tags"] = sorted({t for t in on["_atags"].values() if t} | {t for t in on["_qtags"].values() if t})
        msg = "other non-operating: NonoperatingIncomeExpense is the filer's whole non-operating section (interest included) for some periods"
        if derived:
            msg += f"; shown as that total + interest expense − interest income (plain arithmetic, reconciles to pretax income) for {len(derived)} period(s)"
        if blanked:
            msg += f"; blank for {len(blanked)} period(s) ({', '.join(sorted(blanked)[:6])}{'…' if len(blanked) > 6 else ''}) where neither reading reconciles to pretax income"
        warnings.append(msg)


CF_SECTIONS = {
    "operating": ("net_income", "da", "sbc", "deferred_taxes", "other_noncash", "change_receivables", "change_inventory", "change_payables",
                  "change_deferred_revenue", "change_working_capital"),
    "investing": ("capex", "capex_intangibles", "acquisitions", "purchases_investments", "sales_investments", "other_investing"),
    "financing": ("debt_issued", "debt_repaid", "buybacks", "dividends_paid", "stock_issued", "other_financing"),
}
CATCH_ALL = {"other_noncash": "operating", "other_investing": "investing", "other_financing": "financing"}
SBC_LIKE = ("ShareBased", "StockBased", "StockOption", "RestrictedStock", "SharebasedPayment")
CAPEX_LIKE = ("PropertyPlantAndEquipment", "ProductiveAssets", "RealEstate", "CapitalImprovements", "ConstructionInProcess", "Premises", "Equipment", "Software")


def _section_tags(section):
    specs = {sp["key"]: sp for sp in CASHFLOW}
    return {p[1] for k in CF_SECTIONS[section] if k in specs for p in _pairs(specs[k]["tags"])}


def _accn_index(facts, names):
    """{accession: {(tag, start, end)}} for duration facts of the named tags with a non-zero value."""
    idx = {}
    for tags in (facts.get("facts") or {}).values():
        for name in names:
            d = tags.get(name)
            if not d:
                continue
            for es in d.get("units", {}).values():
                for e in es:
                    if e.get("accn") and e.get("start") and _num(e.get("val")) and e["val"] != 0:
                        idx.setdefault(e["accn"], set()).add((name, e["start"], e["end"]))
    return idx


def unpaired_quarters(facts, lines, q_ends, qmeta, money, warnings):
    """A quarter is derived only from two legs of the SAME tag. (a) A flow
    line whose year-to-date / fiscal-year fact of a tag exists for a quarter
    while the shorter leg of that tag does not (the 10-K breaks out a line the
    10-Qs folded into another caption: APP's FY2025 purchases of intangibles,
    28,318K, sat inside "other investing" in the 10-Qs) stays blank there and
    the cell is flagged basis_break_quarterly. (b) The section's catch-all
    line (other investing / financing / non-cash) derived across two filings
    that present the section differently (the longer leg's filing carries a
    line of that section the shorter leg's filing does not) while the
    catch-all's year-to-date figure shrank through the year (APP Q4 FY2025
    other investing 373K - 27,863K = -27,490K, a number no filing contains) is
    blanked and flagged. The flags land in line['_bb_extra']."""
    unpaired, broken = [], []
    for key, line in lines.items():
        spec = line.get("_spec")
        if spec is None or line["_kind"] != "flow" or line["unit"] != "money" or not spec["tags"]:
            continue
        hists = [duration_history(facts, p, money) for p in _pairs(spec["tags"])]
        for i, e in enumerate(q_ends):
            m = qmeta.get(e) or {}
            s0, fq = m.get("fy_start"), m.get("fq")
            if _num(line["quarterly"][i]) or not s0 or not fq or fq < 2:
                continue
            for h in hists:
                if (s0, e) in h and not any(ss == s0 and x < e and 60 <= _days(x, e) <= 120 for (ss, x) in h):
                    line.setdefault("_bb_extra", set()).add(i)
                    unpaired.append(f"{key} {e}")
                    break
    idx, line_of = None, {}
    for key, section in CATCH_ALL.items():
        line = lines.get(key)
        if line is None:
            continue
        for i, e in enumerate(q_ends):
            qv = line["quarterly"][i]
            acc = line["_qaccn"].get(e) or []
            if not line["derived_quarterly"][i] or not _num(qv) or len(acc) != 2:
                continue
            s0 = (qmeta.get(e) or {}).get("fy_start")
            pair = next((p for p in _pairs(line["_spec"]["tags"]) if p[1] == line["_qtags"].get(e)), None)
            if not s0 or pair is None:
                continue
            h = duration_history(facts, pair, money)
            lv = next((x[1] for x in h.get((s0, e), []) if x[2] == acc[0]), None)
            short = [(x2, z[1]) for (ss, x2), es in h.items() if ss == s0 and x2 < e for z in es if z[2] == acc[1]]
            if lv is None or not short:
                continue
            short_end, sv = max(short)
            if idx is None:
                idx = {sec: _accn_index(facts, _section_tags(sec)) for sec in CF_SECTIONS}
                specs = {sp["key"]: sp for sp in CASHFLOW}
                line_of = {p[1]: k for sec in CF_SECTIONS for k in CF_SECTIONS[sec] if k in specs for p in _pairs(specs[k]["tags"])}
            # compare the section's LINES (a tag swap between the 10-Q and the 10-K within one line is no new caption)
            long_lines = {line_of[t] for (t, ss, ee) in idx[section].get(acc[0], ()) if ss == s0 and ee == e}
            short_lines = {line_of[t] for (t, ss, ee) in idx[section].get(acc[1], ()) if ss == s0 and ee == short_end}
            new = sorted(long_lines - short_lines - {key})
            shrank = abs(qv) > abs(lv) or (lv != 0 and qv != 0 and (qv > 0) != (lv > 0))
            if new and shrank:
                line["quarterly"][i] = None
                line["derived_quarterly"][i] = False
                line["_qtags"].pop(e, None)
                line.setdefault("_bb_extra", set()).add(i)
                broken.append(f"{key} {e} ({lv:,.0f} - {sv:,.0f}; the longer leg's filing adds {', '.join(new)})")
        _retag(line)
    if unpaired:
        more = "..." if len(unpaired) > 12 else ""
        warnings.append(f"quarters not derived (the year-to-date fact's tag has no shorter leg in the same tag: the 10-Qs carried the figure in another caption; flagged basis_break_quarterly): {', '.join(unpaired[:12])}{more}")
    if broken:
        warnings.append(f"catch-all cash-flow quarters blanked (the two legs' filings present the section differently, so their difference is no filed figure; flagged basis_break_quarterly): {'; '.join(broken)}")


def _accns_with_like(facts, words, exclude):
    """{accession: {tag names}} of duration facts whose tag name contains one of `words` (an unlisted caption of
    the same kind), excluding `exclude`."""
    out = {}
    for tax, tags in (facts.get("facts") or {}).items():
        if tax not in ("us-gaap", IF):
            continue
        for name, d in tags.items():
            if name in exclude or not any(w.lower() in name.lower() for w in words):
                continue
            for unit_key, es in d.get("units", {}).items():
                if "/" in unit_key or unit_key in ("shares", "pure"):
                    continue  # money facts only (a per-share grant-date fair value is not a cash-flow caption)
                for e in es:
                    if e.get("accn") and e.get("start") and _num(e.get("val")) and e["val"] != 0:
                        out.setdefault(e["accn"], set()).add(name)
    return out


def zero_unfiled_components(facts, lines, annual_ends, q_ends, qmeta, money, warnings):
    """SBC counts as ZERO for a period whose cash-flow statement (the
    filing(s) that supplied the period's operating cash flow) carries no SBC
    line at all AND no unlisted share-based-compensation-like tag (that would
    be the filer's own SBC caption: the figure is unknown, not zero). The line
    itself stays blank; owner's earnings reads the zero (`_zero_annual` /
    `_zero_quarterly`). Capex is never read as zero: a period without a filed
    capex figure has no FCF and no owner's earnings (capex_gap_warning)."""
    ocf = lines.get("ocf")
    if ocf is None:
        return
    for key in ZERO_WHEN_UNFILED:
        line = lines.get(key)
        if line is None:
            continue
        have = accns_with(facts, line["_spec"]["tags"])
        if not have:
            continue  # never filed at all: the derived lines already treat a never-filed component as zero where allowed
        like = _accns_with_like(facts, SBC_LIKE, {p[1] for p in _pairs(line["_spec"]["tags"])})
        za, zq, unknown = set(), set(), set()
        for col, ends, accmap, zs in (("annual", annual_ends, ocf["_aaccn"], za), ("quarterly", q_ends, ocf["_qaccn"], zq)):
            for i, e in enumerate(ends):
                acc = accmap.get(e) or []
                if _num(line[col][i]) or not _num(ocf[col][i]) or not acc or (set(acc) & have):
                    continue
                other = sorted({t for a in acc for t in like.get(a, ())})
                if other:
                    unknown.update(other)
                    continue
                zs.add(i)
        if za or zq:
            line["_zero_annual"], line["_zero_quarterly"] = za, zq
            periods = sorted([annual_ends[i] for i in za] + [q_ends[i] for i in zq])
            warnings.append(f"{key}: the filing(s) for {len(periods)} period(s) ({periods[0]}..{periods[-1]}) carry no such cash-flow line; read as 0 in owner's earnings, the line itself stays blank there")
        if unknown:
            warnings.append(f"{key}: some periods' filings carry no listed SBC tag but do carry {', '.join(sorted(unknown)[:4])}; owner's earnings stays blank there (the figure is unknown, not zero)")


def capex_gap_warning(facts, lines, annual_ends, q_ends, warnings):
    """Name the periods with operating cash flow but no filed capex (free cash
    flow and owner's earnings blank there), and any unlisted capex-like tag
    those periods' filings carry."""
    ocf, capex = lines.get("ocf"), lines.get("capex")
    if ocf is None:
        return
    gaps, accs = [], set()
    for col, ends, accmap in (("annual", annual_ends, ocf["_aaccn"]), ("quarterly", q_ends, ocf["_qaccn"])):
        for i, e in enumerate(ends):
            if _num(ocf[col][i]) and (capex is None or not _num(capex[col][i])):
                gaps.append(e)
                accs.update(accmap.get(e) or [])
    if not gaps:
        return
    like = _accns_with_like(facts, CAPEX_LIKE, {p[1] for p in _pairs(CAPEX_TAGS)} | {p[1] for p in _pairs(DUR["capex_intangibles"])})
    other = sorted({t for a in accs for t in like.get(a, ()) if t.startswith(("Payments", "PurchaseOf"))})
    uniq = sorted(set(gaps))
    warnings.append(f"capex: no capital-expenditure figure is filed for {len(uniq)} period(s) with operating cash flow ({uniq[0]}..{uniq[-1]}); free cash flow and owner's earnings are blank there (capex is never read as zero)"
                    + (f"; those filings carry unlisted tags {', '.join(other[:5])}" if other else ""))


def opex_gap_warning(lines, annual_ends, warnings):
    """Custom-tagged operating lines (Kroger's OG&A and Rent) never reach
    companyfacts: when the operating lines shown explain less than 90% of the
    latest fiscal year's revenue − operating income, say so."""
    rev, oi = lines.get("revenue"), lines.get("operating_income")
    if rev is None or oi is None or not annual_ends:
        return
    i = len(annual_ends) - 1
    while i >= 0 and not (_num(rev["annual"][i]) and _num(oi["annual"][i])):
        i -= 1
    if i < 0 or rev["annual"][i] <= 0:
        return
    gap = rev["annual"][i] - oi["annual"][i]
    if gap <= 0:
        return
    shown = 0.0
    for key in ("cost_of_revenue", "total_opex", "total_costs"):
        ln = lines.get(key)
        if ln is not None and _num(ln["annual"][i]):
            shown += ln["annual"][i]
    if lines.get("total_opex") is None and lines.get("total_costs") is None:
        for key in ("rnd", "sga", "selling_marketing", "general_admin", "other_opex", "da"):
            ln = lines.get(key)
            if ln is not None and _num(ln["annual"][i]) and not (key in ("selling_marketing", "general_admin") and lines.get("sga") is not None and _num(lines["sga"]["annual"][i])):
                shown += ln["annual"][i]
    if shown < 0.9 * gap:
        warnings.append(f"income statement: the operating lines shown for FY ending {annual_ends[i]} explain {shown:,.0f} of the {gap:,.0f} between revenue and operating income — the filer tags its other operating lines with custom elements that EDGAR companyfacts does not carry")


def _span(ends):
    ends = sorted(set(ends))
    return f"{len(ends)} period(s), {ends[0]}..{ends[-1]}" if len(ends) > 1 else f"1 period, {ends[0]}"


def _cash_only_part(e, v, cash_only, h_c0, h_comb):
    """(part, accns, all_accns) from the same date's cash-only caption (CASH_ONLY_TAG), or None:
    - a filing that reports BOTH for date e with this combined value (within RESTATE_TOL): part = its total − its
      cash-only figure (the newest such filing; its accessions are the provenance);
    - else, when the newest cash-only figure equals the combined value exactly (APP / RBLX 2019-12-31, ARES
      2017-12-31: a 10-Q comparative and the 10-K's total, the same dollars): part 0.
    A cash-only figure from another filing generation is no evidence (ZTS 2024-12-31: the 2025 10-Qs' 1,987M of both
    against the 2026 10-Qs' restated 2,114M total — 127M of reclassified cash, not restricted cash)."""
    c0s, combs = h_c0.get(e) or [], h_comb.get(e) or []
    c0_by = {x[2]: x[1] for x in c0s if x[2]}
    pairs = sorted(((x[0], x[2], c0_by[x[2]], x[1]) for x in combs if x[2] in c0_by and _close(x[1], v)), reverse=True)
    if pairs:
        _, _, c0, tot = pairs[0]
        if 0 <= c0 <= tot:
            return tot - c0, sorted({p[1] for p in pairs if (p[2], p[3]) == (c0, tot)}), sorted({p[1] for p in pairs})
    rec = cash_only.get(e)
    if rec is not None and rec[0] == v:
        return 0.0, list(rec[4]), list(rec[5] or rec[4])
    return None


def _restricted_part(e, v, cash_only, totals, parts, h_c0=None, h_comb=None):
    """(part, tag, accns, all_accns, how) — the restricted cash inside a combined cash + restricted cash cell of value v
    at date e:
    - how "cash_only": the same date's CASH_ONLY_TAG caption separates it (_cash_only_part — ZTS FY2025: the 2026
      10-Qs file 2,450M of both, so 0, where RestrictedCashCurrent says 2M; the quarterly column at that date reads the
      cash-only figure itself, so both columns now agree);
    - how "tagged": a RESTRICTED_TOTAL_TAGS figure for the date, else the RESTRICTED_PART_TAGS captions filed for it
      summed (current + noncurrent: U's RestrictedCashNoncurrent), 0 <= part <= v;
    - how "odd": that figure is outside 0..v (not deducted); None: nothing separates it."""
    cp = _cash_only_part(e, v, cash_only, h_c0 or {}, h_comb or {})
    if cp is not None:
        return cp[0], f"{CASH_WITH_RESTRICTED_TAGS[0]}-{CASH_ONLY_TAG}", cp[1], cp[2], "cash_only"
    got = [totals[e]] if e in totals else [p[e] for p in parts if e in p]
    if not got:
        return None, None, [], [], None
    val = sum(g[0] for g in got)
    acc = set.intersection(*(set(g[4]) for g in got))
    al = set.intersection(*(set(g[5] or g[4]) for g in got))
    return val, "+".join(g[1] for g in got), sorted(acc), sorted(al), ("tagged" if 0 <= val <= v else "odd")


def restricted_cash_split(facts, lines, annual_ends, q_ends, money, warnings):
    """The cash line where its cell is the combined cash + restricted cash
    total (CASH_WITH_RESTRICTED_TAGS — the line's tag for a date the annual
    report filed no CashAndCashEquivalentsAtCarryingValue for; NTRS's FY2025
    5,873.1M includes 531.2M of restricted cash):
    - the cell stays as filed; `_incl_restricted` (→ incl_restricted_annual /
      _quarterly / _ttm, emitted whenever the line has a combined cell) is True
      where it holds restricted cash: a positive part, or an unknown one. A
      part of 0 (the same date's cash-only figure equals the total) is not;
    - the restricted part (_restricted_part) is shown on the restricted_cash
      line in exactly the cells where it is positive and inside the total — the
      line is built here, never from a restricted-cash caption next to a
      cash-only cell (a separate caption, not part of the line above);
    - `_unsplit` marks the combined cells no figure separates: the derived
      figures that treat cash as available (RESTRICTED_CASH_DERIVED) deduct the
      part where it is shown and are flagged where it is not (add_derived),
      their growth blank across a change between the two (finish_lines);
    - the label says so: every valued cell holding restricted cash ->
      CASH_WITH_RESTRICTED_LABEL, some -> RESTRICTED_SOME_SUFFIX. Warned."""
    cash, rc = lines.get("cash"), lines.get("restricted_cash")
    if rc is None:
        spec = next(s for s in BALANCE if s["key"] == "restricted_cash")
        rc = lines["restricted_cash"] = {"key": "restricted_cash", "label": spec["label"], "level": spec["level"], "total": False, "unit": "money",
                                         "ttm": None, "tags": [], "_kind": "instant", "_stmt": "balance", "_spec": spec}
    # built from scratch: only the parts of combined cells
    rc["annual"], rc["quarterly"], rc["derived_quarterly"] = [None] * len(annual_ends), [None] * len(q_ends), [False] * len(q_ends)
    for m in ("_atags", "_qtags", "_aaccn", "_qaccn", "_aall", "_adis", "_qdis"):
        rc[m] = {}
    rc["tags"] = []
    if cash is None:
        return
    cash_only = instant_values(facts, [CASH_ONLY_TAG], money)
    h_c0 = instant_history(facts, ("us-gaap", CASH_ONLY_TAG), money)
    h_comb = instant_history(facts, ("us-gaap", CASH_WITH_RESTRICTED_TAGS[0]), money)
    totals = instant_values(facts, RESTRICTED_TOTAL_TAGS, money)
    parts = [instant_values(facts, tags, money) for tags in RESTRICTED_PART_TAGS]
    combined, by_c0, by_tag, zero, unsplit, odd, rtags = [], [], [], [], [], [], set()
    flags, loose, basis = {}, {}, {}
    for col, ends, tmap in (("annual", annual_ends, "_atags"), ("quarterly", q_ends, "_qtags")):
        fl, un, bs = [], [], []
        for i, e in enumerate(ends):
            v = cash[col][i]
            comb = bool(_num(v) and cash[tmap].get(e) in CASH_WITH_RESTRICTED_TAGS)
            part, tag, acc, al, how = _restricted_part(e, v, cash_only, totals, parts, h_c0, h_comb) if comb else (None, None, [], [], None)
            known = how in ("cash_only", "tagged")
            fl.append(bool(comb and not (known and part == 0)))
            un.append(bool(comb and not known))
            # what the derived figures' cash means here: "incl" restricted cash, "ex" (deducted, or the cash-only caption),
            # None when the caption does not say (CashAndDueFromBanks, Cash: NTRS's equals its combined total)
            bs.append(("ex" if known else "incl") if comb else ("ex" if (_num(v) and cash[tmap].get(e) == CASH_ONLY_TAG) else None))
            if not comb:
                continue
            combined.append(e)
            if known and part == 0:
                zero.append(e)
            elif known:
                (by_c0 if how == "cash_only" else by_tag).append(e)
                rc[col][i] = part
                rc[tmap][e] = tag
                if how == "tagged":
                    rtags.add(tag)
                if col == "annual":
                    rc["_aaccn"][e], rc["_aall"][e] = acc, al
                else:
                    rc["_qaccn"][e] = acc
            else:
                unsplit.append(e)
                if how == "odd":
                    odd.append(f"{e} ({part:,.0f} of {tag} vs cash {v:,.0f})")
        flags[col], loose[col], basis[col] = fl, un, bs
    _retag(rc)
    if not combined:
        return
    flags["ttm"] = bool(flags["quarterly"] and flags["quarterly"][-1])  # an instant's ttm is the latest quarter's cell
    loose["ttm"] = bool(loose["quarterly"] and loose["quarterly"][-1])
    cash["_incl_restricted"] = flags  # emitted even when all False: the file records that the split was applied (restricted_cash_pending)
    cash["_unsplit"] = loose
    cash["_rbasis"] = basis
    valued = sum(1 for v in cash["annual"] + cash["quarterly"] if _num(v))
    held = sum(flags["annual"]) + sum(flags["quarterly"])
    if held and held == valued:
        cash["label"] = CASH_WITH_RESTRICTED_LABEL
    elif held:
        cash["label"] = cash["label"] + RESTRICTED_SOME_SUFFIX
    msg = (f"restricted cash: in {_span(combined)} the cash line is the filed cash + restricted cash total ({CASH_WITH_RESTRICTED_TAGS[0]}, "
           f"the cash-flow statement's total, read where the annual report filed no {CASH_ONLY_TAG} for the date)")
    if by_c0:
        msg += f"; in {_span(by_c0)} a filing reports the same date's {CASH_ONLY_TAG} next to that total, so the restricted part is the difference"
    if by_tag:
        msg += f"; in {_span(by_tag)} the restricted part is the restricted-cash figure filed for the same date ({', '.join(sorted(rtags))})"
    if by_c0 or by_tag:
        msg += ("; that part is shown on the 'Restricted cash (included in cash above)' line and deducted from cash wherever net cash, net cash per "
                "share and the ROIC proxy's invested capital are computed")
    if zero:
        msg += (f"; in {_span(zero)} it holds no restricted cash (the same date's {CASH_ONLY_TAG} equals the total, or the restricted-cash "
                f"figure is 0): nothing deducted, not marked")
    if unsplit:
        msg += (f"; in {_span(unsplit)} no figure separates the restricted part, so where those metrics are computed they still count restricted cash "
                f"as cash (net cash overstated, net debt understated by the restricted amount; flagged incl_restricted_* and labelled "
                f"'{RESTRICTED_SOME_SUFFIX.strip()[1:-1]}' on the metric; growth across a change between the two bases is blank)")
    if odd:
        msg += f"; a restricted-cash figure outside 0..cash was not deducted: {'; '.join(odd[:4])}{'; ...' if len(odd) > 4 else ''}"
    warnings.append(msg)


def _derived_restricted_flags(cash, annual, quarterly, ttm):
    """incl_restricted_* for a derived figure that treats cash as available: True where its value exists and the
    period's cash is the combined total with no restricted figure to deduct (restricted_cash_split's `_unsplit`)."""
    u = (cash or {}).get("_unsplit")
    if not u:
        return None
    a = [bool(_num(v) and i < len(u["annual"]) and u["annual"][i]) for i, v in enumerate(annual)]
    q = [bool(_num(v) and i < len(u["quarterly"]) and u["quarterly"][i]) for i, v in enumerate(quarterly)]
    t = bool(_num(ttm) and u["quarterly"] and u["quarterly"][-1])
    return {"annual": a, "quarterly": q, "ttm": t} if (any(a) or any(q) or t) else None


# ---- derived lines ----------------------------------------------------------
def _opt(get, present, key):
    """A component that may legitimately not exist: its value when filed for
    the period, 0.0 when the filer never files the line at all, None when the
    line exists in other periods but not this one."""
    v = get(key)
    if _num(v):
        return v
    return None if present(key) else 0.0


def _tax_rate(get):
    pre, tax = get("pretax_income"), get("income_tax")
    if _num(pre) and pre > 0 and _num(tax) and 0 <= tax / pre <= 0.5:
        return tax / pre
    return None


def _ocf_key(get):
    """The OCF the free-cash-flow figures subtract capex from: continuing-operations OCF in a period whose cash-flow
    statement reports discontinued investing flows on their own line (capex is then continuing only), else OCF."""
    d = get("icf_discontinued")
    return "ocf_continuing" if (_num(d) and d != 0) else "ocf"


def _ni_key(get):
    """Net margin's numerator: continuing net income in a period with discontinued operations (revenue is then
    continuing only), else net income."""
    d = get("discontinued_ops")
    return "net_income_continuing" if (_num(d) and d != 0 and _num(get("net_income_continuing"))) else "net_income"


def derived_input_keys(name, get):
    """The lines whose values a derived figure's cell combines (its provenance = the filings they share)."""
    return {"ebitda": ["operating_income", "da"], "fcf": [_ocf_key(get), "capex"], "owner_earnings": [_ocf_key(get), "capex", "sbc"],
            "gross_margin": ["gross_profit", "revenue"], "operating_margin": ["operating_income", "revenue"], "net_margin": [_ni_key(get), "revenue"],
            "fcf_margin": ["fcf", "revenue"], "total_debt": ["long_term_debt", "short_term_debt", "current_lt_debt", "debt_current_agg", "debt_total_agg"],
            "net_cash": ["cash", "restricted_cash", "short_term_investments", "total_debt"], "working_capital": ["total_current_assets", "total_current_liabilities"],
            "tangible_book_value": ["total_common_equity", "goodwill", "intangibles"], "net_cash_per_share": ["net_cash", "shares_outstanding"],
            "book_value_per_share": ["total_common_equity", "shares_outstanding"], "tangible_book_value_per_share": ["tangible_book_value", "shares_outstanding"],
            "fcf_per_share": ["fcf", "shares_diluted"], "owner_earnings_per_share": ["owner_earnings", "shares_diluted"]}.get(name, [])


# derived figures blanked when their inputs' values share no filing although one filing carries them all
SAME_FILING_DERIVED = ("ebitda", "fcf", "owner_earnings", "gross_margin", "operating_margin", "net_margin", "fcf_margin")


def _prov(line, e):
    """(accessions that filed the annual cell's value, accessions that filed the period at all) or None (unknown)."""
    if line is None:
        return None
    acc, al = (line.get("_aaccn") or {}).get(e), (line.get("_aall") or {}).get(e)
    if not acc and not al:
        return None
    return set(acc or ()), set(al or acc or ())


def _prov_join(provs):
    provs = [p for p in provs if p is not None]
    if not provs:
        return None
    return set.intersection(*(p[0] for p in provs)), set.intersection(*(p[1] for p in provs))


def _prov_conflict(p):
    """The values share no filing although some filing reported all of them: two filing generations."""
    return p is not None and not p[0] and bool(p[1])


def _available_cash(cash, get, tag_of):
    """The period's cash a derived figure may treat as available: the cash cell minus its restricted part when the cell
    is the combined cash + restricted total (CASH_WITH_RESTRICTED_TAGS) and the period's restricted figure is shown
    (restricted_cash_split keeps it only there); otherwise the cash cell itself."""
    if _num(cash) and tag_of is not None and tag_of("cash") in CASH_WITH_RESTRICTED_TAGS:
        r = get("restricted_cash")
        if _num(r):
            return cash - r
    return cash


def derive_value(name, get, present, tag_of=None, ni_ttm=None, oi_ttm=None, tax_ttm=None):
    """One derived figure for one period. get(key) -> the period's value of a
    line (None when absent), present(key) -> the line carries a value in SOME
    period; tag_of(key) -> the tag that supplied the period's value;
    ni_ttm / oi_ttm / tax_ttm -> trailing-four-quarter numerators for the
    return metrics on quarterly columns (None on annual columns)."""
    req = lambda *ks: all(_num(get(k)) for k in ks)  # noqa: E731
    if name == "ebitda":
        return get("operating_income") + get("da") if req("operating_income", "da") else None
    if name == "fcf":
        ok = _ocf_key(get)
        return get(ok) - get("capex") if req(ok, "capex") else None
    if name == "owner_earnings":
        ok = _ocf_key(get)
        return get(ok) - get("capex") - get("sbc") if req(ok, "capex", "sbc") else None
    if name == "total_debt":
        lt, agg_cur, agg_tot = get("long_term_debt"), get("debt_current_agg"), get("debt_total_agg")
        st, cur_ltd = get("short_term_debt"), get("current_lt_debt")
        st_is_agg = bool(tag_of and tag_of("short_term_debt") in DEBT_CURRENT_AGG_TAGS)
        cur_is_agg = bool(tag_of and tag_of("current_lt_debt") in DEBT_CURRENT_AGG_TAGS)
        lt_is_total = bool(tag_of and tag_of("long_term_debt") in DEBT_TOTAL_TAGS)
        if _num(agg_cur):
            cur = agg_cur
        elif cur_is_agg and _num(cur_ltd):  # IFRS current borrowings incl. the current portion: the whole current debt
            cur = cur_ltd
        elif _num(st) or _num(cur_ltd):
            cur = (st if _num(st) else 0.0) + (cur_ltd if (_num(cur_ltd) and not st_is_agg) else 0.0)
        else:
            cur = None
        if _num(lt) and lt_is_total:  # the long-term-debt line is the filer's combined total (current maturities inside)
            agg_tot = lt
        elif _num(lt):
            return lt + (cur or 0.0)
        if _num(agg_tot):  # the filer's combined long-term debt (includes current maturities) + any short-term borrowings
            return agg_tot + (st if (_num(st) and not st_is_agg) else 0.0)
        return cur
    if name == "net_cash":
        cash = _available_cash(get("cash"), get, tag_of)
        sti, debt = _opt(get, present, "short_term_investments"), _opt(get, present, "total_debt")
        return cash + sti - debt if (_num(cash) and sti is not None and debt is not None) else None
    if name == "working_capital":
        return get("total_current_assets") - get("total_current_liabilities") if req("total_current_assets", "total_current_liabilities") else None
    if name == "tangible_book_value":
        eq = get("total_common_equity")
        gw, it = _opt(get, present, "goodwill"), _opt(get, present, "intangibles")
        return eq - gw - it if (_num(eq) and gw is not None and it is not None) else None
    if name in ("net_cash_per_share", "book_value_per_share", "tangible_book_value_per_share"):
        num = {"net_cash_per_share": "net_cash", "book_value_per_share": "total_common_equity", "tangible_book_value_per_share": "tangible_book_value"}[name]
        sh = get("shares_outstanding") if _num(get("shares_outstanding")) else get("shares_diluted")
        return _ratio(get(num), sh) if (_num(sh) and sh > 0) else None
    if name in ("fcf_per_share", "owner_earnings_per_share"):
        sh = get("shares_diluted")
        return _ratio(get(name[:-10]), sh) if (_num(sh) and sh > 0) else None
    if name in ("gross_margin", "operating_margin", "net_margin", "fcf_margin"):
        num = {"gross_margin": "gross_profit", "operating_margin": "operating_income", "net_margin": _ni_key(get), "fcf_margin": "fcf"}[name]
        rev = get("revenue")
        return _ratio(get(num), rev) if (_num(rev) and rev > 0) else None
    if name in ("roe", "roa"):
        ni = ni_ttm if ni_ttm is not None else get("net_income")
        den = get("total_common_equity") if name == "roe" else get("total_assets")
        return _ratio(ni, den) if (_num(ni) and _num(den) and den > 0) else None
    if name == "roic_proxy":
        oi = oi_ttm if oi_ttm is not None else get("operating_income")
        t = tax_ttm if tax_ttm is not None else _tax_rate(get)
        eq = get("total_common_equity")
        debt, cash = _opt(get, present, "total_debt"), _available_cash(_opt(get, present, "cash"), get, tag_of)
        if not (_num(oi) and t is not None and _num(eq) and debt is not None and cash is not None):
            return None
        invested = eq + debt - cash
        return _ratio(oi * (1 - t), invested) if invested > 0 else None
    if name == "debt_to_equity":
        eq = get("total_common_equity")
        return _ratio(get("total_debt"), eq) if (_num(eq) and eq > 0) else None
    if name == "current_ratio":
        cl = get("total_current_liabilities")
        return _ratio(get("total_current_assets"), cl) if (_num(cl) and cl > 0) else None
    return None


def _trailing4(line, ends, i):
    """Sum of a flow line over quarters i-3..i when they are consecutive and all filed."""
    if line is None or i < 3:
        return None
    sub = ends[i - 3:i + 1]
    if not quarters_consecutive(sub):
        return None
    vals = line["quarterly"][i - 3:i + 1]
    return sum(vals) if all(_num(v) for v in vals) else None


def _eff(line, col, i):
    """A line's value for a derived computation: the filed value, else 0 when
    the period's filing has no such line (zero_unfiled_components)."""
    v = line[col][i]
    if _num(v):
        return v
    return 0.0 if i in line.get(f"_zero_{col}", ()) else None


# the lines each derived figure reads (a derived line's quarter is marked derived when any input quarter is)
DERIVED_INPUTS = {
    "ebitda": ("operating_income", "da"), "fcf": ("ocf", "capex"), "owner_earnings": ("ocf", "capex", "sbc"),
    "fcf_per_share": ("fcf", "shares_diluted"), "owner_earnings_per_share": ("owner_earnings", "shares_diluted"),
    "net_cash_per_share": ("net_cash", "shares_outstanding"), "book_value_per_share": ("shares_outstanding",),
    "tangible_book_value_per_share": ("shares_outstanding",),
    "gross_margin": ("gross_profit", "revenue"), "operating_margin": ("operating_income", "revenue"), "net_margin": ("net_income", "revenue"),
    "fcf_margin": ("fcf", "revenue"), "roe": ("net_income",), "roa": ("net_income",), "roic_proxy": ("operating_income", "income_tax", "pretax_income"),
}


def add_derived(lines, annual_ends, q_ends, ttm_quarters, warnings=None):
    """Compute every derived line over annual / quarterly / ttm columns, in
    spec order (a derived line may use an earlier derived line: fcf ->
    fcf_per_share, total_debt -> net_cash)."""
    present = lambda k: k in lines and any(_num(v) for v in lines[k]["annual"] + lines[k]["quarterly"] + [lines[k]["ttm"]])  # noqa: E731
    mixed = []
    ni, oi, tax, pre = lines.get("net_income"), lines.get("operating_income"), lines.get("income_tax"), lines.get("pretax_income")
    for stmt, specs in STATEMENTS:
        for spec in specs:
            if not spec["derived"]:
                continue
            name = spec["derived"]
            annual, aacc, aall = [], {}, {}
            for i in range(len(annual_ends)):
                get = lambda k, i=i: (_eff(lines[k], "annual", i) if k in lines and i < len(lines[k]["annual"]) else None)  # noqa: E731
                tag_of = lambda k, i=i: (lines[k].get("_atags", {}).get(annual_ends[i]) if k in lines else None)  # noqa: E731
                v = derive_value(name, get, present, tag_of)
                e = annual_ends[i]
                p = _prov_join([_prov(lines.get(k), e) for k in derived_input_keys(name, get) if k in lines and _num(lines[k]["annual"][i])])
                if _num(v) and name in SAME_FILING_DERIVED and _prov_conflict(p):
                    mixed.append(f"{spec['key']} {e}")
                    v = None
                if _num(v) and p is not None:
                    aacc[e], aall[e] = sorted(p[0]), sorted(p[1])
                annual.append(v)
            quarterly = []
            for i in range(len(q_ends)):
                get = lambda k, i=i: (_eff(lines[k], "quarterly", i) if k in lines and i < len(lines[k]["quarterly"]) else None)  # noqa: E731
                tag_of = lambda k, i=i: (lines[k].get("_qtags", {}).get(q_ends[i]) if k in lines else None)  # noqa: E731
                kw = {}
                if name in ("roe", "roa", "roic_proxy"):
                    kw["ni_ttm"] = _trailing4(ni, q_ends, i)
                    kw["oi_ttm"] = _trailing4(oi, q_ends, i)
                    t4, p4 = _trailing4(tax, q_ends, i), _trailing4(pre, q_ends, i)
                    kw["tax_ttm"] = (t4 / p4) if (_num(t4) and _num(p4) and p4 > 0 and 0 <= t4 / p4 <= 0.5) else None
                    if name in ("roe", "roa") and kw["ni_ttm"] is None:
                        quarterly.append(None)
                        continue
                    if name == "roic_proxy" and (kw["oi_ttm"] is None or kw["tax_ttm"] is None):
                        quarterly.append(None)
                        continue
                quarterly.append(derive_value(name, get, present, tag_of, **kw))
            get = lambda k: (lines[k]["ttm"] if k in lines else None)  # noqa: E731
            tag_of = lambda k: (lines[k].get("_qtags", {}).get(q_ends[-1]) if (k in lines and q_ends) else None)  # noqa: E731
            kw = {}
            if name in ("roe", "roa", "roic_proxy"):
                kw = {"ni_ttm": get("net_income"), "oi_ttm": get("operating_income"),
                      "tax_ttm": (get("income_tax") / get("pretax_income")) if (_num(get("income_tax")) and _num(get("pretax_income")) and get("pretax_income") > 0 and 0 <= get("income_tax") / get("pretax_income") <= 0.5) else None}
                ttm = None if ((name != "roic_proxy" and kw["ni_ttm"] is None) or (name == "roic_proxy" and (kw["oi_ttm"] is None or kw["tax_ttm"] is None))) else derive_value(name, get, present, tag_of, **kw)
            else:
                ttm = derive_value(name, get, present, tag_of)
            inputs = [lines[k] for k in DERIVED_INPUTS.get(name, ()) if k in lines]
            dq = [bool(_num(quarterly[i]) and any(ln["derived_quarterly"][i] for ln in inputs if i < len(ln.get("derived_quarterly") or []))) for i in range(len(q_ends))]
            lines[spec["key"]] = {"key": spec["key"], "label": spec["label"], "level": spec["level"], "total": bool(spec["total"]), "unit": spec["unit"],
                                  "annual": annual, "quarterly": quarterly, "ttm": ttm, "derived_quarterly": dq, "tags": [], "_aaccn": aacc, "_aall": aall,
                                  "_kind": "derived", "_stmt": stmt, **({"cf_sign": spec["cf_sign"]} if spec["cf_sign"] is not None else {})}
            if name in RESTRICTED_CASH_DERIVED:
                fl = _derived_restricted_flags(lines.get("cash"), annual, quarterly, ttm)
                if fl:
                    lines[spec["key"]]["_incl_restricted"] = fl
                    lines[spec["key"]]["_rbasis"] = lines["cash"]["_rbasis"]  # growth never across "incl" vs "ex" (finish_lines)
                    # the per-cell marks are JSON only: the label tells the reader of the table
                    held = sum(fl["annual"]) + sum(fl["quarterly"]) + int(fl["ttm"])
                    valued = sum(1 for v in annual + quarterly + [ttm] if _num(v))
                    lines[spec["key"]]["label"] = spec["label"] + (RESTRICTED_ALL_SUFFIX if held == valued else RESTRICTED_SOME_SUFFIX)
    icf = lines.get("icf_discontinued")
    if icf is not None and warnings is not None:
        per = [e for col, ends in (("annual", annual_ends), ("quarterly", q_ends)) for i, e in enumerate(ends) if _num(icf[col][i]) and icf[col][i] != 0]
        if per:
            per = sorted(set(per))
            warnings.append(f"free cash flow: {len(per)} period(s) ({per[0]}..{per[-1]}) report discontinued operations' investing cash flows on their own line, so "
                            f"capex is continuing-only there — FCF and owner's earnings use continuing OCF (NetCashProvidedByUsedInOperatingActivitiesContinuing"
                            f"Operations, else OCF − CashProvidedByUsedInOperatingActivitiesDiscontinuedOperations from the same filing), blank where neither is filed; "
                            f"the OCF line itself stays the filed total")
    dn = lines.get("discontinued_ops")
    if dn is not None and "net_income_continuing" in lines and warnings is not None:
        per = [e for col, ends in (("annual", annual_ends), ("quarterly", q_ends)) for i, e in enumerate(ends)
               if _num(dn[col][i]) and dn[col][i] != 0 and _num(lines["net_income_continuing"][col][i])]
        if per:
            per = sorted(set(per))
            warnings.append(f"net margin: continuing net income ÷ revenue for {len(per)} period(s) with discontinued operations ({per[0]}..{per[-1]}) — revenue is continuing-only there")
    if mixed and warnings is not None:
        warnings.append(f"same filing: {len(mixed)} fiscal-year cell(s) of a derived figure are blank because its inputs' values come from different filing "
                        f"generations (one restated by a later filing, the other as originally filed) although one filing reports them all: {', '.join(mixed[:10])}"
                        + ("..." if len(mixed) > 10 else ""))
    return lines


def _ttm_with_zeros(line, q_ends, ttm_quarters):
    """TTM of a filed flow line; a quarter the filing reads as zero
    (zero_unfiled_components) counts as 0 so the derived TTM (fcf) exists —
    the line's own ttm stays None when any quarter is genuinely missing."""
    zq = line.get("_zero_quarterly")
    if not zq or not ttm_quarters:
        return None
    pos = {e: i for i, e in enumerate(q_ends)}
    vals = []
    for e in ttm_quarters:
        i = pos.get(e)
        if i is None:
            return None
        v = line["quarterly"][i]
        vals.append(v if _num(v) else (0.0 if i in zq else None))
    return sum(vals) if all(_num(v) for v in vals) else None


def basis_breaks(lines, annual_ends, q_ends, qmeta, warnings):
    """Flag the four quarters of a fiscal year whose sum differs from the
    fiscal-year figure by more than 1% of it (restatement, reclassification
    or discontinued operations between filings — APP's FY2024 revenue, AEE's
    FY2011): `basis_break_quarterly[i]` True on those quarters, growth cells
    that straddle them blanked (finish_lines), a warning per line naming the
    years."""
    by_fy = {}
    for i, e in enumerate(q_ends):
        m = qmeta.get(e) or {}
        if m.get("fy_start") and m.get("fq"):
            by_fy.setdefault(m["fy_start"], {})[m["fq"]] = i
    apos = {e: i for i, e in enumerate(annual_ends)}
    found = []
    for key, line in lines.items():
        extra = line.get("_bb_extra") or set()
        if extra:
            line["basis_break_quarterly"] = [i in extra for i in range(len(q_ends))]
        if line["_kind"] != "flow" or line["unit"] not in BASIS_CHECK_UNITS:
            continue
        flags = [i in extra for i in range(len(q_ends))]
        years = []
        for fs, qs in sorted(by_fy.items()):
            if set(qs) != {1, 2, 3, 4}:
                continue
            fy_end = q_ends[qs[4]]
            ai = apos.get(fy_end)
            if ai is None or not _num(line["annual"][ai]):
                continue
            vals = [line["quarterly"][qs[k]] for k in (1, 2, 3, 4)]
            if not all(_num(v) for v in vals):
                continue
            fy, s = line["annual"][ai], sum(vals)
            if abs(s - fy) > BASIS_BREAK_TOL * max(abs(fy), 1e-9):
                for k in (1, 2, 3, 4):
                    flags[qs[k]] = True
                years.append(f"{fy_end} ({s:,.0f} vs {fy:,.0f})")
        if years:
            line["basis_break_quarterly"] = flags
            found.append(f"{key}: {', '.join(years)}")
    if found:
        warnings.append("basis break (four quarters vs the fiscal year, >1% apart — the quarters and the year were filed on different bases: restatement, reclassification or "
                        "discontinued operations; those quarters carry basis_break_quarterly and the growth cells across them are blank): " + "; ".join(found))


def finish_lines(lines, annual_ends, q_ends, qmeta, ttm_quarters, warnings):
    """TTM for the filed lines, then the derived lines, the basis-break flags,
    then growth arrays for every line, then the statements dict (lines with
    at least one value, in spec order)."""
    for key, line in lines.items():
        if line["_kind"] != "derived":
            line["ttm"] = ttm_of(line["quarterly"], q_ends, line["unit"], line["_kind"], ttm_quarters)
            if line["ttm"] is None and line.get("_zero_quarterly"):
                line["_ttm_eff"] = _ttm_with_zeros(line, q_ends, ttm_quarters)
    # the hidden discontinued-investing line only switches FCF to continuing OCF: any non-zero quarter in the TTM window
    # does (its partial sum is never shown)
    icf = lines.get("icf_discontinued")
    if icf is not None and icf["ttm"] is None and ttm_quarters:
        pos = {e: i for i, e in enumerate(q_ends)}
        vals = [icf["quarterly"][pos[e]] for e in ttm_quarters if e in pos and _num(icf["quarterly"][pos[e]])]
        if any(v != 0 for v in vals):
            icf["ttm"] = sum(vals)
    # the derived TTM reads the zero-filled TTM of the unfiled components
    for key in ZERO_WHEN_UNFILED:
        if key in lines and lines[key].get("_ttm_eff") is not None:
            lines[key]["ttm"] = lines[key]["_ttm_eff"]
    add_derived(lines, annual_ends, q_ends, ttm_quarters, warnings)
    for key in ZERO_WHEN_UNFILED:
        if key in lines and lines[key].get("_ttm_eff") is not None:
            lines[key]["ttm"] = None
    basis_breaks(lines, annual_ends, q_ends, qmeta, warnings)
    yoy = yoy_index(q_ends)
    gen_breaks, rc_breaks = {}, {}
    out = {}
    for stmt, specs in STATEMENTS:
        out[stmt] = []
        for spec in specs:
            line = lines.get(spec["key"])
            if line is None or (line["_kind"] == "derived" and line["_stmt"] != stmt):
                continue
            # a filed line listed by two statements (net income, D&A, SBC: income statement AND cash-flow
            # statement) is assembled once and emitted in both, with each statement's own label / indent /
            # total flag and cf_sign — the values are the same filed facts
            if not any(_num(v) for v in line["annual"] + line["quarterly"] + [line["ttm"]]):
                continue
            no_growth = line["unit"] in ("ratio", "pct")
            gq = [None] * len(q_ends) if no_growth else growth_arrays(line["quarterly"], q_ends, False)
            flags = line.get("basis_break_quarterly")
            if flags:
                gq = [None if (flags[i] or (yoy[i] is not None and flags[yoy[i]])) else g for i, g in enumerate(gq)]
            ga = [None] * len(annual_ends) if no_growth else growth_arrays(line["annual"], annual_ends, True)
            for i in annual_generation_breaks(line, annual_ends, ga):
                ga[i] = None
                gen_breaks.setdefault(spec["key"], set()).add(annual_ends[i])
            if spec["key"] == line["key"] and line["key"] in RESTRICTED_CASH_DERIVED:
                for cell in restricted_basis_breaks(line, annual_ends, q_ends, yoy, ga, gq):
                    rc_breaks.setdefault(spec["key"], []).append(cell)
            rec = {"key": spec["key"], "label": line["label"] if spec["key"] == line["key"] and line["_stmt"] == stmt else spec["label"],
                   "level": spec["level"], "total": bool(spec["total"]), "unit": line["unit"],
                   "annual": line["annual"], "quarterly": line["quarterly"], "ttm": line["ttm"],
                   "growth_annual": ga,
                   "growth_quarterly": gq, "derived_quarterly": line["derived_quarterly"], "tags": line["tags"]}
            if flags:
                rec["basis_break_quarterly"] = flags
            ir = line.get("_incl_restricted") if line["key"] == spec["key"] else None
            if ir:  # the cell counts restricted cash as cash (restricted_cash_split / _derived_restricted_flags)
                rec["incl_restricted_annual"], rec["incl_restricted_quarterly"], rec["incl_restricted_ttm"] = ir["annual"], ir["quarterly"], ir["ttm"]
            if spec["cf_sign"] is not None:
                rec["cf_sign"] = spec["cf_sign"]
            out[stmt].append(rec)
    if gen_breaks:
        parts = [f"{k} ({', '.join(sorted(v)[:4])}{'…' if len(v) > 4 else ''})" for k, v in sorted(gen_breaks.items())]
        warnings.append(f"growth across filing generations: {sum(len(v) for v in gen_breaks.values())} annual growth cell(s) are blank because the year and "
                        f"the year before come from different filings that disagree (one restated by a later filing — discontinued operations, an "
                        f"accounting change, a recast — the other as originally filed; or a capex caption change): " + "; ".join(parts[:12]) + ("; ..." if len(parts) > 12 else ""))
    if rc_breaks:
        parts = []
        for k, cells in sorted(rc_breaks.items()):
            a, q = [e for c, e in cells if c == "annual"], [e for c, e in cells if c == "quarterly"]
            parts.append(f"{k} (" + "; ".join(x for x in ((f"FY ending {', '.join(a)}" if a else ""), (f"quarters {', '.join(q[:6])}{'…' if len(q) > 6 else ''}" if q else "")) if x) + ")")
        warnings.append(f"restricted cash: {sum(len(v) for v in rc_breaks.values())} growth cell(s) are blank because one of the two periods deducts "
                        f"restricted cash and the other still counts it as cash (no figure separates it there; flagged incl_restricted_*): " + "; ".join(parts))
    return out


def restricted_basis_breaks(line, annual_ends, q_ends, yoy, ga, gq):
    """Blank (in place) the growth cells of a figure that treats cash as available (RESTRICTED_CASH_DERIVED) where one
    period counts restricted cash as cash (a combined cash cell no figure separates: `_rbasis` "incl") and the other does
    not ("ex": its restricted part deducted, or the cash-only caption CASH_ONLY_TAG). NTRS net cash 2023-06-30 vs
    2022-06-30: 1,584.7M after deducting 583.5M vs 1,814.0M still including it — −12.6%, a change of definition, not of
    the business. A caption that does not say (NTRS's CashAndDueFromBanks before 2016, which equals its combined total
    wherever both are filed) is no break. Returns the cells blanked as (column, period end)."""
    b = line.get("_rbasis") if line.get("_incl_restricted") else None
    if not b:
        return []
    out = []
    a, q = b["annual"], b["quarterly"]
    for i in range(1, len(ga)):
        if ga[i] is not None and i < len(a) and {a[i], a[i - 1]} == {"incl", "ex"}:
            ga[i] = None
            out.append(("annual", annual_ends[i]))
    for i, g in enumerate(gq):
        j = yoy[i] if i < len(yoy) else None
        if g is not None and j is not None and i < len(q) and {q[i], q[j]} == {"incl", "ex"}:
            gq[i] = None
            out.append(("quarterly", q_ends[i]))
    return out


# lines whose growth is also blank across a change of the filed tag (a different definition, not a different business)
TAG_CHANGE_BREAK = ("capex",)


def annual_generation_breaks(line, annual_ends, growth):
    """Indices of annual growth cells to blank: the two years' values share no
    filing although some filing reported both years (each value's provenance
    is every accession that filed it — a restated year next to one as
    originally reported), or, for TAG_CHANGE_BREAK lines, the two years were
    read from different tags."""
    out = []
    for i, g in enumerate(growth):
        if g is None or i == 0:
            continue
        e0, e1 = annual_ends[i - 1], annual_ends[i]
        if _prov_conflict(_prov_join([_prov(line, e0), _prov(line, e1)])) and _prov(line, e0) is not None and _prov(line, e1) is not None:
            out.append(i)
            continue
        if line.get("key") in TAG_CHANGE_BREAK:
            t0, t1 = (line.get("_atags") or {}).get(e0), (line.get("_atags") or {}).get(e1)
            if t0 and t1 and t0 != t1:
                out.append(i)
    return out


def period_labels(annual_ends, q_ends, qmeta):
    """(annual labels, {fy_start: label}) from ONE rule: fy_labels over the
    fiscal-year ends of the annual columns plus the (estimated) ends of
    fiscal years that only have quarters, so a quarter carries exactly the
    label its fiscal year's annual column carries (TDY's 52/53-week years
    ending 2012-01-01 and 2012-12-30 are FY2011 and FY2012 in both)."""
    fy_end_of, est = {}, []
    for e in q_ends:
        s0 = (qmeta.get(e) or {}).get("fy_start")
        if not s0 or s0 in fy_end_of:
            continue
        hit = [ae for ae in annual_ends if is_fy(s0, ae)]
        if hit:
            fy_end_of[s0] = min(hit, key=lambda ae: abs(_days(s0, ae) - 364))
            continue
        q4 = [x for x in q_ends if (qmeta.get(x) or {}).get("fy_start") == s0 and (qmeta.get(x) or {}).get("fq") == 4]
        ee = q4[0] if q4 else (datetime.date.fromisoformat(s0) + datetime.timedelta(days=364)).isoformat()
        near = [ae for ae in annual_ends if abs(_days(ae, ee)) <= 20]
        fy_end_of[s0] = near[0] if near else ee
        if not near:
            est.append(ee)
    all_ends = sorted(set(annual_ends) | set(est))
    lab = dict(zip(all_ends, fy_labels(all_ends)))
    return [lab[e] for e in annual_ends], {s0: lab[fe] for s0, fe in fy_end_of.items()}


def original_filing_dates(facts, ends, sub=None):
    """{fiscal-year end: the ORIGINAL annual report's filing date}: the 10-K /
    20-F / 40-F whose report date is that end in the submissions feed, else
    the earliest annual-form filing (fp FY, filed within 400 days of the end)
    that reported ANY fact for that end, whatever tags it used (GFI's FY2016
    20-F tagged revenue with an element the line lists do not carry); a year
    that never had its own annual report (KVUE's pre-IPO FY2022) gets the
    first annual report that carried it as a comparative."""
    out = {}
    rec = ((sub or {}).get("filings") or {}).get("recent") or {}
    for form, fd, rd in zip(rec.get("form", []), rec.get("filingDate", []), rec.get("reportDate", [])):
        if form not in ("10-K", "20-F", "40-F", "10-K/A", "20-F/A", "40-F/A") or not rd or not fd:
            continue
        for e in ends:
            if abs(_days(rd, e)) <= DATE_MERGE_DAYS and (e not in out or fd < out[e]):
                out[e] = fd
    want = {e for e in ends if e not in out}
    late = {}
    if want:
        for tags in (facts.get("facts") or {}).values():
            for d in tags.values():
                for es in (d.get("units") or {}).values():
                    for x in es:
                        e, f = x.get("end"), x.get("filed")
                        if e in want and f and x.get("fp") == "FY" and x.get("form", "") in FILING_FORMS and 0 < _days(e, f):
                            k = (_days(e, f) > 400, f)  # the year's own report first; a later comparative only when there is none
                            if e not in late or k < late[e]:
                                late[e] = k
        for e, (_, f) in late.items():
            out[e] = f
    return out


def _log_warnings(warnings, merged, q_ends, annual_ends):
    if _LOG["scale"]:
        uniq = {}
        for (tag, per), v in sorted(_LOG["scale"].items()):  # one entry per tag and period end (an FY fact is read as a duration and as an annual value)
            uniq.setdefault((tag, per.split("..")[-1]), ((tag, per), v))
        items = sorted(uniq.values())
        ex = []
        for (tag, per), (kept, dropped) in items[:6]:
            d = dropped[0]
            ex.append(f"{tag} {per}: kept {kept:,.6g}, ignored {d[0]:,.6g} ({d[1]} filed {d[2]})")
        more = "; ..." if len(items) > 6 else ""
        warnings.append(f"power-of-ten disagreement between filings of the same period: {len(items)} tag-period(s) where one filing's value is 10^k x another's (a scale slip); "
                        f"the value consistent with the tag's other periods is kept: {'; '.join(ex)}{more}")
    if _LOG["zero"]:
        items = sorted(_LOG["zero"].items())
        ex = [f"{tag} {per}: kept {kept:,.6g}, ignored 0 ({z[0][0]} filed {z[0][1]})" for (tag, per), (kept, z) in items[:6]]
        warnings.append(f"filed zero against non-zero filings of the same period: {len(items)} tag-period(s) where one filing tagged 0 while another filed a "
                        f"figure (a slip, not a restatement); the 0 is ignored: {'; '.join(ex)}{'; ...' if len(items) > 6 else ''}")
    if _LOG["shift"]:
        items = sorted(_LOG["shift"].items())
        ex = [f"{tag} {per}: kept {kept:,.6g}, ignored {late:,.6g} = the {adj} value ({z[0][0]} filed {z[0][1]})" for (tag, per), (kept, late, adj, z) in items[:6]]
        warnings.append(f"shifted column: {len(items)} tag-period(s) where only the newest filing(s) carry the adjacent period's exact value (a mis-dated context, "
                        f"not a restatement); the earlier filings' value is kept: {'; '.join(ex)}{'; ...' if len(items) > 6 else ''}")
    if _LOG["sign"]:
        parts = []
        for tag, rows in sorted(_LOG["sign"].items()):
            rows = sorted(rows)
            filings = sorted({f"{r[1]} filed {r[2]}" for r in rows})
            more = "..." if len(filings) > 4 else ""
            span = rows[0][0] if len(rows) == 1 else f"{rows[0][0]} to {rows[-1][0]}"
            parts.append(f"{tag} for {len(rows)} period(s) ({span}) in {', '.join(filings[:4])}{more}")
        warnings.append("sign: a payment the cash-flow statement shows as an outflow was filed NEGATIVE (the filer's sign slip); read as the absolute amount paid: " + "; ".join(parts))
    used = set(q_ends) | set(annual_ends)
    shown = sorted((a, b) for a, b in merged.items() if b in used)
    if shown:
        more = "..." if len(shown) > 8 else ""
        warnings.append("period dates merged (a fiscal week-end and the calendar month-end later comparatives used are one period, dated as the original filing dated it): "
                        + ", ".join(f"{a} -> {b}" for a, b in shown[:8]) + more)


def build_statements(facts, warnings=None, sub=None):
    """facts (companyfacts JSON) -> (periods, statements, currency, warnings).
    `sub` (the submissions feed, optional) dates each fiscal year's original
    annual report."""
    warnings = warnings if warnings is not None else []
    for k in _LOG:
        _LOG[k] = {}
    facts, merged = canonical_dates(facts)
    bank = bank_shape(facts)
    fy_starts = core_fy_starts(facts)
    money = money_unit(facts, warnings)
    rev = revenue_series(facts, fy_starts, bank, money, warnings)
    core = {"revenue": rev}
    for key, spec in (("net_income", L("net_income", "", NET_INCOME_TAGS)), ("ocf", L("ocf", "", OCF_TAGS)),
                      ("operating_income", L("operating_income", "", OI_TAGS)),
                      ("total_assets", L("total_assets", "", list(INST["assets"]), kind="instant"))):
        core[key] = _series_for(spec, facts, fy_starts, money)
    annual_ends, q_ends, qmeta = build_periods(core, facts, warnings)
    splits = split_schedule(facts, warnings)
    lines = assemble_lines(facts, bank, annual_ends, q_ends, qmeta, fy_starts, money, splits, warnings, revenue=rev)
    ttm = None
    if len(q_ends) >= 4 and quarters_consecutive(q_ends[-4:]):
        ttm = {"end": q_ends[-1], "quarters": q_ends[-4:]}
    elif q_ends:
        warnings.append(f"ttm: the last four quarters ({', '.join(q_ends[-4:])}) are not four consecutive fiscal quarters — flow lines carry no TTM")
    statements = finish_lines(lines, annual_ends, q_ends, qmeta, (ttm or {}).get("quarters"), warnings)
    labels, fy_lab = period_labels(annual_ends, q_ends, qmeta)
    orig = original_filing_dates(facts, annual_ends, sub)
    qlabels = [(f"Q{qmeta[e]['fq']} FY{fy_lab[qmeta[e]['fy_start']]}" if qmeta[e].get("fq") and qmeta[e].get("fy_start") in fy_lab else e) for e in q_ends]
    dup = sorted({x for x in qlabels if qlabels.count(x) > 1})
    if dup:  # a fiscal-calendar change (YUM 2016: 12-week quarters to calendar quarters) gives two genuine "Q1 FY2016" periods
        warnings.append(f"quarter labels: {len(dup)} label(s) would name two columns ({', '.join(dup[:6])}) after a fiscal-calendar change; those labels carry the period end")
        qlabels = [f"{lab} ({e})" if lab in dup else lab for lab, e in zip(qlabels, q_ends)]
    periods = {"annual": [{"end": e, "label": f"FY{lab}", "filed": orig.get(e)} for e, lab in zip(annual_ends, labels)],
               "quarterly": [{"end": e, "label": lab, "fy_start": qmeta[e].get("fy_start"), "filed": qmeta[e].get("filed")} for e, lab in zip(q_ends, qlabels)],
               "ttm": ttm, "current": ({"end": q_ends[-1]} if q_ends else None)}
    _log_warnings(warnings, merged, q_ends, annual_ends)
    if not q_ends:
        warnings.append("no quarterly facts could be assembled (filer may report on 20-F/40-F without 10-Qs)")
    if bank:
        warnings.append("bank shape: interest income / expense, provision, noninterest lines, deposits and loans are shown; the non-bank interest lines are not")
        prov = lines.get("provision_credit_losses")
        if prov is not None and any("+" in t for t in prov["tags"]):
            warnings.append("provision for credit losses: the filer tags no income-statement total — periods without one show the loans component + the off-balance-sheet component (both filed in that period; blank where either is absent), which can differ from the face line by other components (securities)")
    return periods, statements, money, warnings


# ---------------------------------------------------------------------------
# Submissions (small): newest financial filing, fiscal year end
# ---------------------------------------------------------------------------
def latest_filing(sub):
    """{form, filed, period} of the newest 10-K / 10-Q / 20-F / 40-F (or amendment) in the submissions feed."""
    rec = (sub.get("filings") or {}).get("recent") or {}
    forms, fds, rds = rec.get("form", []), rec.get("filingDate", []), rec.get("reportDate", [])
    best = None
    for i, form in enumerate(forms):
        if form not in FILING_FORMS:
            continue
        fd = fds[i] if i < len(fds) else ""
        if best is None or fd > best["filed"]:
            best = {"form": form, "filed": fd, "period": rds[i] if i < len(rds) else None}
    return best


def read_existing(folder):
    try:
        with open(os.path.join(folder, "statements.json"), encoding="utf-8") as f:
            d = json.load(f)
        return d if isinstance(d, dict) else None
    except Exception:
        return None


def can_skip(existing, latest):
    """The --all cost rule: skip the companyfacts download when the existing
    file records the same newest filing (form + date), the same schema, AND
    its columns already cover that filing's period (`covered_through`) — a
    file written while EDGAR's companyfacts lagged the filing is retried on
    every run until the data arrives; a file written before the restricted-cash
    split whose cash line used the combined tag is rebuilt once
    (restricted_cash_pending)."""
    if not existing or not latest or not isinstance(existing.get("latest_filed"), dict):
        return False
    lf = existing["latest_filed"]
    if lf.get("filed") != latest.get("filed") or lf.get("form") != latest.get("form") or existing.get("schema_version") != SCHEMA_VERSION:
        return False
    covered = existing.get("covered_through")
    if latest.get("period") and (not covered or latest["period"] > covered):
        return False
    if restricted_cash_pending(existing):
        return False
    return True


def restricted_cash_pending(existing):
    """A file written before the restricted-cash split whose cash line uses the combined cash + restricted cash tag: its
    net cash counted restricted cash as cash, so --all rebuilds it once (the rebuilt file carries incl_restricted_* on
    that line — all False where no combined cell holds any). A file whose cash line never used the combined tag is
    unaffected and stays skipped."""
    st = existing.get("statements")
    bal = st.get("balance") if isinstance(st, dict) else None
    for ln in bal if isinstance(bal, list) else []:
        if isinstance(ln, dict) and ln.get("key") == "cash":
            tags = ln.get("tags") if isinstance(ln.get("tags"), list) else []
            return any(t in CASH_WITH_RESTRICTED_TAGS for t in tags) and "incl_restricted_annual" not in ln
    return False


def run_one(ticker, cik=None, write=True, cache=None, force=False, existing=None):
    """Build and (optionally) write <ticker>/statements.json. Returns
    (summary dict, skipped bool)."""
    folder = os.path.join(BASE, ticker)
    nums = {}
    try:
        with open(os.path.join(folder, "dcf_numbers.json"), encoding="utf-8") as f:
            nums = json.load(f)
    except Exception:
        pass
    if cik is None:
        cik = resolve_cik(ticker, nums if isinstance(nums, dict) else {})
    if cik is None:
        raise RuntimeError(f"NO_CIK for {ticker}")
    cik = int(cik)
    sub = fetch(f"https://data.sec.gov/submissions/CIK{cik:010d}.json", cache, f"{ticker}.sub.json")
    latest = latest_filing(sub)
    existing = existing if existing is not None else read_existing(folder)
    if not force and can_skip(existing, latest):
        return {"ticker": ticker, "cik": cik, "skipped": True, "latest_filed": latest}, True
    facts = fetch(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json", cache, f"{ticker}.facts.json")
    warnings = []
    periods, statements, currency, warnings = build_statements(facts, warnings, sub=sub)
    newest_period = max([p["end"] for p in periods["annual"]] + [p["end"] for p in periods["quarterly"]], default=None)
    if latest and latest.get("period") and newest_period and latest["period"] > newest_period:
        warnings.append(f"latest {latest['form']} (period {latest['period']}, filed {latest['filed']}) is not yet in EDGAR companyfacts — columns stop at {newest_period}")
    out = {"ticker": ticker, "cik": cik, "entity": facts.get("entityName"), "as_of": _et_today().isoformat(), "currency": currency,
           "fiscal_year_end_mmdd": sub.get("fiscalYearEnd"), "source": SOURCE, "schema_version": SCHEMA_VERSION,
           "latest_filed": latest, "covered_through": newest_period, "periods": periods, "statements": statements, "warnings": warnings}
    written = None  # --no-write
    if write:
        # committed file: rewritten (atomically) only when something besides the run date `as_of` changed (_stable.py)
        written = write_json_if_changed(os.path.join(folder, "statements.json"), out, volatile=("as_of",),
                                        ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    summary = {"ticker": ticker, "cik": cik, "skipped": False, "written": written, "currency": currency, "fiscal_year_end_mmdd": sub.get("fiscalYearEnd"),
               "annual_years": len(periods["annual"]), "first_fy": periods["annual"][0]["label"] if periods["annual"] else None,
               "last_fy": periods["annual"][-1]["label"] if periods["annual"] else None,
               "quarters": len(periods["quarterly"]), "first_quarter": periods["quarterly"][0]["end"] if periods["quarterly"] else None,
               "ttm": periods["ttm"], "covered_through": newest_period, "lines": {k: len(v) for k, v in statements.items()}, "latest_filed": latest, "warnings": warnings}
    return summary, False


def main(argv=None):
    ap = argparse.ArgumentParser(description="Full statements from EDGAR companyfacts -> <T>/statements.json")
    ap.add_argument("ticker", nargs="?")
    ap.add_argument("--cik", type=int)
    ap.add_argument("--no-write", action="store_true")
    ap.add_argument("--force", action="store_true", help="rebuild even when the newest filing is already recorded")
    ap.add_argument("--all", action="store_true", help="every folder with score.json; skips names whose statements.json already records the newest filing")
    ap.add_argument("--cache", help="directory of cached EDGAR JSON (read when present, written after a fetch)")
    a = ap.parse_args(argv)
    if a.all:
        folders = sorted(os.path.basename(os.path.dirname(p)) for p in glob.glob(os.path.join(BASE, "*", "score.json")))
        folders = [f for f in folders if not f.startswith(("_", "."))]
        written, unchanged, skipped, failed = [], [], [], []
        for t in folders:
            try:
                s, sk = run_one(t, write=not a.no_write, cache=a.cache, force=a.force)
            except Exception as e:  # noqa: BLE001 — one name never stops the refresh
                failed.append(t)
                print(f"statements.py: FAILED {t}: {type(e).__name__}: {e}", file=sys.stderr)
                continue
            if sk:
                skipped.append(t)
                continue
            same = s.get("written") is False
            (unchanged if same else written).append(t)
            print(f"{t}: FY{s['first_fy'][2:] if s['first_fy'] else '?'}..{s['last_fy'][2:] if s['last_fy'] else '?'} ({s['annual_years']} FY, {s['quarters']} quarters, ttm {(s['ttm'] or {}).get('end')})"
                  + (f" | {len(s['warnings'])} warning(s)" if s["warnings"] else "") + (" | content unchanged, file left as is" if same else ""))
        print(f"statements.py --all: {len(written)} {'built (--no-write)' if a.no_write else 'written'}, {len(unchanged)} unchanged (rebuilt; same content apart from as_of - file left as is), "
              f"{len(skipped)} skipped (newest filing already recorded and covered - companyfacts not downloaded), {len(failed)} failed"
              + (f" [{', '.join(failed)}]" if failed else ""))
        return 1 if failed and not written and not unchanged and not skipped else 0
    if not a.ticker:
        ap.print_help()
        return 2
    s, _ = run_one(a.ticker.upper(), cik=a.cik, write=not a.no_write, cache=a.cache, force=True)
    print(json.dumps(s, indent=1, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
