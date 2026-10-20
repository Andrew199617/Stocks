#!/usr/bin/env python3
"""Fixture builder for _system/tests/test_engine_55.py (engine release 5.5).

Run MANUALLY, with network: python _system/tests/fixtures/engine55/build_fixtures.py [TICKER ...]
The tests themselves never fetch anything. `TICKER=PATH` builds from a companyfacts file already on disk (the
engine 5.6 HALO fixture: python build_fixtures.py HALO=<scratch>/halo_facts.json) instead of fetching it.

For each ticker it writes <TICKER>.json.gz beside this file:
  {"ticker", "cik", "entityName", "price", "price_source", "filer_annual_form",
   "fx_rates": {ccy: {date: rate}},         # from the folder's dcf_numbers.json fx_conversion (if any)
   "universe_row": {...},                   # the _system/universe.csv row
   "facts": {"cik", "entityName", "facts": {taxonomy: {tag: {"units": {unit: [entries]}}}}}}
The facts are EDGAR companyfacts trimmed to the tags dcf_engine.py / ttm.py read (plus the 5.5 additions,
dei and the split-ratio tags) and to entries from the last ~12 fiscal years (all forms kept so ttm.py's 10-Q
legs are present), so an offline engine run reproduces the folder's recorded numbers.
"""
import csv, gzip, json, os, sys, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.environ.get("STOCKS_BASE") or os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
UA = {"User-Agent": "Muse research andrewmauro199612@gmail.com"}
YEARS_KEPT = 12

US = ["RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet", "Revenues", "RevenueFromContractWithCustomerIncludingAssessedTax",
      "NetIncomeLoss", "ProfitLoss", "OperatingIncomeLoss",
      "NetCashProvidedByUsedInOperatingActivities", "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations",
      "PaymentsToAcquirePropertyPlantAndEquipment", "PaymentsForConstructionInProcess", "PaymentsToAcquireOtherPropertyPlantAndEquipment",
      "PaymentsToAcquireProductiveAssets", "PaymentsToAcquireOtherProductiveAssets", "PaymentsForCapitalImprovements",
      "PaymentsToExploreAndDevelopOilAndGasProperties", "PaymentsToAcquireOilAndGasProperty",
      "PaymentsToAcquireIntangibleAssets", "PaymentsToAcquireOtherIntangibleAssets",
      "DepreciationDepletionAndAmortization", "DepreciationAmortizationAndAccretionNet", "DepreciationAndAmortization", "Depreciation",
      "ShareBasedCompensation", "AllocatedShareBasedCompensationExpense", "IncomeTaxExpenseBenefit",
      "WeightedAverageNumberOfDilutedSharesOutstanding", "WeightedAverageNumberOfSharesOutstandingDiluted", "WeightedAverageNumberOfSharesOutstandingBasic",
      "CashAndCashEquivalentsAtCarryingValue", "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents",
      "RestrictedCashAndCashEquivalents", "RestrictedCash", "RestrictedCashAndCashEquivalentsAtCarryingValue", "RestrictedCashCurrent",
      "AssetsCurrent", "LiabilitiesCurrent", "DebtCurrent", "LongTermDebtAndCapitalLeaseObligationsCurrent", "LongTermDebtCurrent",
      "ShortTermBorrowings", "CommercialPaper", "NotesPayableCurrent", "LongTermDebtNoncurrent", "LongTermDebtAndCapitalLeaseObligations",
      "LongTermNotesPayable", "LongTermDebt", "DebtLongtermAndShorttermCombinedAmount", "LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities",
      "OperatingLeaseLiabilityCurrent", "OperatingLeaseLiabilityNoncurrent", "Assets", "Liabilities", "PropertyPlantAndEquipmentNet",
      "StockholdersEquity", "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest", "CommonStockSharesOutstanding",
      "StockholdersEquityNoteStockSplitConversionRatio1", "StockholdersEquityNoteStockSplitConversionRatio",
      # engine 5.6 (acquired IPR&D, Andrew 2026-10-19): the two expense tags the detector reads, the cash tag it
      # prefers, and the intangible-impairment tag it must NOT read (kept so a fixture proves the non-goal)
      "ResearchAndDevelopmentAssetAcquiredOtherThanThroughBusinessCombinationWrittenOff", "ResearchAndDevelopmentInProcess",
      "PaymentsToAcquireInProcessResearchAndDevelopment", "ImpairmentOfIntangibleAssetsExcludingGoodwill"]
IFRS = ["Revenue", "RevenueFromContractsWithCustomers", "ProfitLoss", "ProfitLossFromOperatingActivities",
        "CashFlowsFromUsedInOperatingActivities", "CashFlowsFromUsedInOperatingActivitiesContinuingOperations",
        "PurchaseOfPropertyPlantAndEquipmentClassifiedAsInvestingActivities", "PurchaseOfPropertyPlantAndEquipment",
        "PurchaseOfPropertyPlantAndEquipmentIntangibleAssetsOtherThanGoodwillInvestmentPropertyAndOtherNoncurrentAssets",
        "PurchaseOfIntangibleAssetsClassifiedAsInvestingActivities",
        "AdjustmentsForDepreciationAndAmortisationExpense", "DepreciationAndAmortisationExpense",
        "AdjustmentsForSharebasedPayments", "ExpenseFromSharebasedPaymentTransactionsWithEmployees",
        "IncomeTaxExpenseContinuingOperations", "IncomeTaxExpense", "AdjustedWeightedAverageShares", "WeightedAverageShares",
        "CashAndCashEquivalents", "RestrictedCashAndCashEquivalents", "CurrentAssets", "CurrentLiabilities",
        "CurrentBorrowingsAndCurrentPortionOfNoncurrentBorrowings", "CurrentPortionOfLongtermBorrowings", "ShorttermBorrowings",
        "LongtermBorrowings", "NoncurrentPortionOfNoncurrentBorrowings", "Borrowings", "CurrentLeaseLiabilities", "NoncurrentLeaseLiabilities",
        "Assets", "Liabilities", "PropertyPlantAndEquipment", "Equity", "NumberOfSharesOutstanding"]
DEI = ["EntityCommonStockSharesOutstanding"]
KEEP = {"us-gaap": set(US), "ifrs-full": set(IFRS), "dei": set(DEI)}


def fetch(url):
    last = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r:
                return json.loads(r.read())
        except Exception as e:
            last = e
            time.sleep(2 ** attempt)
    raise last


def trim(facts):
    ends = [e.get("end") for tax in facts.get("facts", {}).values() for body in tax.values()
            for es in body.get("units", {}).values() for e in es if e.get("end") and e.get("fp") == "FY"]
    cutoff = f"{int(max(ends)[:4]) - YEARS_KEPT}-01-01" if ends else "0000"
    out = {}
    for tax, tags in facts.get("facts", {}).items():
        for tag, body in tags.items():
            if tag not in KEEP.get(tax, ()):
                continue
            units = {}
            for unit, es in body.get("units", {}).items():
                kept = [e for e in es if (e.get("end") or "") >= cutoff]
                if kept:
                    units[unit] = kept
            if units:
                out.setdefault(tax, {})[tag] = {"units": units}
    return {"cik": facts.get("cik"), "entityName": facts.get("entityName"), "facts": out}


def build(ticker, facts_path=None):
    folder = f"{BASE}/{ticker}"
    n = json.load(open(f"{folder}/dcf_numbers.json", encoding="utf-8"))
    cik = int(n["cik"])
    if facts_path:
        facts = json.load(open(facts_path, encoding="utf-8"))
        assert int(facts.get("cik") or 0) == cik, f"{facts_path}: CIK {facts.get('cik')} is not {ticker}'s {cik}"
    else:
        facts = fetch(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json")
    uni = None
    with open(f"{BASE}/_system/universe.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["ticker"] == ticker:
                uni = row
                break
    fxc = n.get("fx_conversion") or {}
    # pre-5.3.1 runs recorded only the primary currency's rates (no rates_by_currency)
    fx = fxc.get("rates_by_currency") or ({fxc["from_currency"]: fxc["rates"]} if fxc.get("from_currency") and fxc.get("rates") else {})
    fixture = {"ticker": ticker, "cik": cik, "entityName": facts.get("entityName"),
               "price": n.get("price"), "price_source": n.get("price_source"),
               "filer_annual_form": n.get("filer_annual_form"), "fx_rates": fx,
               "recorded_as_of": n.get("as_of"), "recorded_engine_release": n.get("engine_release"),
               "universe_row": uni, "facts": trim(facts)}
    path = os.path.join(HERE, f"{ticker}.json.gz")
    with gzip.open(path, "wt", encoding="utf-8") as f:
        json.dump(fixture, f, separators=(",", ":"))
    print(f"{ticker}: {os.path.getsize(path) / 1024:.0f} KB")
    if not facts_path:
        time.sleep(0.3)


DEFAULT = ["AR", "APA", "ELS", "JLL", "DD", "NTNX", "TEM", "VIV", "TLK", "PUK", "CX", "CCJ", "STZ", "APP",
           "BNT", "IESC", "WF", "VOD", "ATO", "RBC", "FER", "PR"]

if __name__ == "__main__":
    for t in sys.argv[1:] or DEFAULT:
        tk, _, fp = t.partition("=")
        build(tk.upper(), fp or None)
