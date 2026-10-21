#!/usr/bin/env python3
"""xbrl_instance.py — undimensioned facts from a filing's own XBRL 2.1 instance (engine 5.7, Andrew's ruling R2b,
2026-10-19; design 04 B.1, tests 1-5). Run: python _system/tests/test_xbrl_instance.py (or python -m pytest). Offline:
the hand-written fixtures in fixtures/instance/. Every test fails on the 5.6.0 / L0 code (no module: ImportError).

1. parse_undimensioned keeps only undimensioned numeric us-gaap / ifrs-full facts (and the dei cover-page share
   count): the SegmentsAxis, typed-member and scenario contexts, the nil fact and the text dei facts are not facts;
   identical duplicates collapse; contexts that follow their facts resolve; the dei block is read.
2. unit names match companyfacts' spelling (EUR, shares, EUR/shares, pure).
3. annual_facts_after keeps the annual durations and instants after the date companyfacts already has (the
   comparative FY and its balance sheet are not re-added) and drops a key with two different values, listing it.
4. an inline XBRL document is NotAnInstance.
5. merge_into_companyfacts never replaces or duplicates an annual companyfacts entry (RDY's dei cover fact from the
   same accession stays as companyfacts has it), appends the new keys with src "xbrl_instance" in companyfacts'
   entry shape, never touches its input, and a 10-Q's comparative instant does not block the annual twin.
Also: facts_sha256 moves with any fact value and not with the list being rebuilt; locate_instance returns the
(bytes, url) pair of this lane (the L0 stub's shape).
"""
import copy
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SYS = os.path.dirname(HERE)
sys.path.insert(0, SYS)
import xbrl_instance as X  # noqa: E402

FIX = os.path.join(HERE, "fixtures", "instance")
ANNUAL = os.path.join(FIX, "tiny_annual.xml")
INLINE = os.path.join(FIX, "tiny_inline.htm")


def _parsed():
    return X.parse_undimensioned(ANNUAL)


def _keyed(facts):
    return {(f["taxonomy"], f["tag"], f["unit"], f["start"], f["end"]): f for f in facts}


def test_parse_keeps_only_undimensioned_numeric_facts():
    p = _parsed()
    assert p["dei"] == {"DocumentType": "20-F", "DocumentPeriodEndDate": "2026-03-31", "DocumentFiscalPeriodFocus": "FY",
                        "DocumentFiscalYearFocus": "2026", "EntityCentralIndexKey": "0000999002",
                        "CurrentFiscalYearEndDate": "--03-31"}, p["dei"]
    tags = sorted((f["taxonomy"], f["tag"], f["value"]) for f in p["facts"])
    assert tags == sorted([
        ("ifrs-full", "CashFlowsFromUsedInOperatingActivities", 607000000),   # declared BEFORE its context: resolved
        ("ifrs-full", "CashFlowsFromUsedInOperatingActivities", 590000000),
        ("ifrs-full", "PurchaseOfPropertyPlantAndEquipmentClassifiedAsInvestingActivities", 249000000),   # not the segment's 100M
        ("ifrs-full", "PurchaseOfIntangibleAssetsClassifiedAsInvestingActivities", 161000000),
        ("ifrs-full", "AdjustmentsForSharebasedPayments", 3000000),            # the identical duplicate collapsed
        ("ifrs-full", "AdjustedWeightedAverageShares", 833331689),
        ("ifrs-full", "DilutedEarningsLossPerShare", 0.72),
        ("ifrs-full", "Revenue", 3500000000),                                   # typed (10M) and scenario (5M) dropped
        ("ifrs-full", "ProfitLoss", 600000000), ("ifrs-full", "ProfitLoss", 601000000),   # a conflict: both kept here
        ("ifrs-full", "CashAndCashEquivalents", 400000000), ("ifrs-full", "CashAndCashEquivalents", 350000000),
        ("ifrs-full", "ProportionOfOwnershipInterestInSubsidiary", 0.25),
        ("dei", "EntityCommonStockSharesOutstanding", 834656970)]), tags
    assert not any(f["tag"] == "Equity" for f in p["facts"])                   # nil
    ocf = [f for f in p["facts"] if f["tag"] == "CashFlowsFromUsedInOperatingActivities" and f["value"] == 607000000][0]
    assert ocf == {"taxonomy": "ifrs-full", "tag": "CashFlowsFromUsedInOperatingActivities", "unit": "EUR",
                   "start": "2025-04-01", "end": "2026-03-31", "instant": None, "value": 607000000, "decimals": -6,
                   "context": "FY26"}, ocf
    assert isinstance(ocf["value"], int)                                        # companyfacts stores integers
    cash = [f for f in p["facts"] if f["tag"] == "CashAndCashEquivalents" and f["value"] == 400000000][0]
    assert cash["start"] is None and cash["end"] == cash["instant"] == "2026-03-31", cash
    dei = [f for f in p["facts"] if f["taxonomy"] == "dei"][0]
    assert dei["unit"] == "shares" and dei["decimals"] == "INF" and dei["end"] == "2026-03-31", dei
    # bytes and a file object parse the same
    with open(ANNUAL, "rb") as f:
        data = f.read()
    assert X.parse_undimensioned(data) == p
    import io
    assert X.parse_undimensioned(io.BytesIO(data)) == p


def test_unit_names_match_companyfacts():
    assert X.unit_name("iso4217:EUR") == "EUR"
    assert X.unit_name("iso4217:usd") == "USD"
    assert X.unit_name("xbrli:shares") == "shares"
    assert X.unit_name("iso4217:USD/xbrli:shares") == "USD/shares"
    assert X.unit_name("xbrli:pure") == "pure"
    units = {f["tag"]: f["unit"] for f in _parsed()["facts"]}
    assert units["DilutedEarningsLossPerShare"] == "EUR/shares"
    assert units["AdjustedWeightedAverageShares"] == "shares"
    assert units["ProportionOfOwnershipInterestInSubsidiary"] == "pure"
    assert units["Revenue"] == "EUR"


def test_annual_facts_after_skips_known_periods_and_drops_conflicts():
    entries, conflicts = X.annual_facts_after(_parsed(), "2025-03-31")
    k = _keyed(entries)
    assert ("ifrs-full", "CashFlowsFromUsedInOperatingActivities", "EUR", "2025-04-01", "2026-03-31") in k
    assert ("ifrs-full", "CashFlowsFromUsedInOperatingActivities", "EUR", "2024-04-01", "2025-03-31") not in k  # comparative
    assert ("ifrs-full", "CashAndCashEquivalents", "EUR", None, "2026-03-31") in k
    assert ("ifrs-full", "CashAndCashEquivalents", "EUR", None, "2025-03-31") not in k                           # comparative
    assert ("dei", "EntityCommonStockSharesOutstanding", "shares", None, "2026-03-31") in k
    assert not any(e["tag"] == "ProfitLoss" for e in entries), "a conflicting key must be dropped"
    assert conflicts == [{"taxonomy": "ifrs-full", "tag": "ProfitLoss", "unit": "EUR", "start": "2025-04-01",
                          "end": "2026-03-31", "values": [600000000, 601000000]}], conflicts
    e = k[("ifrs-full", "AdjustmentsForSharebasedPayments", "EUR", "2025-04-01", "2026-03-31")]
    assert e == {"taxonomy": "ifrs-full", "tag": "AdjustmentsForSharebasedPayments", "unit": "EUR",
                 "start": "2025-04-01", "end": "2026-03-31", "val": 3000000, "decimals": -6}, e
    assert len(entries) == 10, [(x["tag"], x["end"]) for x in entries]   # 8 FY durations (one conflict out) + 2 instants
    # a later after_end keeps nothing; None keeps the comparative too (conflict still dropped)
    assert X.annual_facts_after(_parsed(), "2026-03-31") == ([], [])
    allp, _ = X.annual_facts_after(_parsed(), None)
    assert len(allp) == 12
    # a non-annual duration (a half year) is never an annual fact
    half = {"facts": [{"taxonomy": "ifrs-full", "tag": "Revenue", "unit": "EUR", "start": "2025-10-01",
                       "end": "2026-03-31", "instant": None, "value": 1, "decimals": 0, "context": "H2"}], "dei": {}}
    assert X.annual_facts_after(half, "2025-03-31") == ([], [])


def test_inline_document_is_not_an_instance():
    try:
        X.parse_undimensioned(INLINE)
    except X.NotAnInstance as e:
        assert "not an XBRL 2.1 instance" in str(e), e
    else:
        raise AssertionError("an inline XBRL document must be refused")


def _cf_rdy_shape():
    """companyfacts in RDY's shape: FY2025 annual facts, and from the FY2026 accession ONLY the dei cover fact."""
    return {"cik": 999002, "entityName": "TINY", "facts": {
        "dei": {"EntityCommonStockSharesOutstanding": {"label": "x", "description": "y", "units": {"shares": [
            {"end": "2026-03-31", "val": 834656970, "accn": "0009999002-26-000381", "fy": 2026, "fp": "FY",
             "form": "20-F", "filed": "2026-05-29"}]}}},
        "ifrs-full": {
            "CashFlowsFromUsedInOperatingActivities": {"label": "OCF", "description": "d", "units": {"EUR": [
                {"start": "2024-04-01", "end": "2025-03-31", "val": 590000000, "accn": "0009999002-25-000100",
                 "fy": 2025, "fp": "FY", "form": "20-F", "filed": "2025-06-01"}]}},
            "CashAndCashEquivalents": {"label": "Cash", "description": "d", "units": {"EUR": [
                {"end": "2026-03-31", "val": 1, "accn": "0009999002-26-000010", "fy": 2026, "fp": "Q3",
                 "form": "6-K", "filed": "2026-04-30"}]}}}}}


def test_merge_never_replaces_a_companyfacts_entry():
    cf = _cf_rdy_shape()
    before = copy.deepcopy(cf)
    entries, _ = X.annual_facts_after(_parsed(), "2025-03-31")
    filing = {"form": "20-F", "accession": "0009999002-26-000381", "filed": "2026-05-29", "period": "2026-03-31"}
    cfe = X.to_companyfacts_entries(entries, filing, 2026)
    merged, n = X.merge_into_companyfacts(cf, cfe)
    assert cf == before, "merge_into_companyfacts modified its input"
    assert n == len(entries) - 1, (n, len(entries))         # every new key but the dei fact companyfacts already holds
    dei = merged["facts"]["dei"]["EntityCommonStockSharesOutstanding"]["units"]["shares"]
    assert dei == before["facts"]["dei"]["EntityCommonStockSharesOutstanding"]["units"]["shares"], dei   # not duplicated
    ocf = merged["facts"]["ifrs-full"]["CashFlowsFromUsedInOperatingActivities"]
    assert ocf["label"] == "OCF" and ocf["units"]["EUR"][0] == before["facts"]["ifrs-full"][
        "CashFlowsFromUsedInOperatingActivities"]["units"]["EUR"][0]
    assert ocf["units"]["EUR"][1] == {"start": "2025-04-01", "end": "2026-03-31", "val": 607000000,
                                      "accn": "0009999002-26-000381", "fy": 2026, "fp": "FY", "form": "20-F",
                                      "filed": "2026-05-29", "src": "xbrl_instance"}, ocf["units"]["EUR"][1]
    # a 6-K / 10-Q comparative instant at the same date is not an annual entry: the annual twin is appended
    cash = merged["facts"]["ifrs-full"]["CashAndCashEquivalents"]["units"]["EUR"]
    assert [e["val"] for e in cash] == [1, 400000000], cash
    new_tag = merged["facts"]["ifrs-full"]["PurchaseOfIntangibleAssetsClassifiedAsInvestingActivities"]
    assert new_tag["units"]["EUR"][0]["src"] == "xbrl_instance" and new_tag["label"] is None
    # merging twice adds nothing; an amendment form on the filing is written as the original annual form
    again, n2 = X.merge_into_companyfacts(merged, cfe)
    assert n2 == 0 and again == merged
    amend = X.to_companyfacts_entries(entries[:1], dict(filing, form="20-F/A"), 2026)
    assert amend[0][3]["form"] == "20-F", amend


def test_facts_sha256_moves_with_a_value():
    entries, conflicts = X.annual_facts_after(_parsed(), "2025-03-31")
    h = X.facts_sha256(entries, conflicts)
    assert h == X.facts_sha256(json.loads(json.dumps(entries)), json.loads(json.dumps(conflicts)))
    edited = copy.deepcopy(entries)
    edited[0]["val"] = edited[0]["val"] + 1
    assert X.facts_sha256(edited, conflicts) != h
    assert X.facts_sha256(entries, []) != h
    # 3000000 and 3000000.0 are the same figure (the engine's float canon)
    floats = copy.deepcopy(entries)
    floats[0]["val"] = float(floats[0]["val"])
    assert X.facts_sha256(floats, conflicts) == h


def test_locate_instance_returns_the_bytes_url_pair():
    calls = []

    def fake_locate(cik, filing, cache):
        calls.append((cik, dict(filing)))
        return "https://www.sec.gov/Archives/x/a_htm.xml", b"<xbrl/>", "a", "folder", (lambda: []), []
    saved = X.locate_files
    X.locate_files = fake_locate
    try:
        assert X.locate_instance(999002, "0009999002-26-000381", "a.htm", "20-F", "2026-03-31") == (
            b"<xbrl/>", "https://www.sec.gov/Archives/x/a_htm.xml")
        assert calls[0][1] == {"accession": "0009999002-26-000381", "primary": "a.htm", "form": "20-F",
                               "period": "2026-03-31"}
        X.locate_files = lambda cik, filing, cache: (None, None, "a", "folder", (lambda: []), ["none"])
        assert X.locate_instance(999002, "0009999002-26-000381", "a.htm") == (None, None)
    finally:
        X.locate_files = saved


if __name__ == "__main__":
    import inspect
    fns = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_") and inspect.isfunction(f)]
    failed = 0
    for name, fn in fns:
        try:
            fn()
            print(f"PASS {name}")
        except Exception as e:  # noqa: BLE001
            failed += 1
            print(f"FAIL {name}: {type(e).__name__}: {e}")
    print(f"{len(fns) - failed}/{len(fns)} passed")
    sys.exit(1 if failed else 0)
