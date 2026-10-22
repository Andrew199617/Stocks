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


def _patched_edgar(answers):
    """Patch segments.fetch / get_json (what locate_instance reads through) with {url suffix: bytes | dict |
    exception}; returns (calls, restore)."""
    import segments as S
    calls = []

    def answer(url):
        calls.append(url)
        for suffix, a in answers.items():
            if url.endswith(suffix):
                if isinstance(a, Exception):
                    raise a
                return a
        raise S.NotFound(url)
    saved = S.fetch, S.get_json
    S.fetch = lambda url, timeout=None: answer(url)
    S.get_json = lambda url: answer(url)

    def restore():
        S.fetch, S.get_json = saved
    return calls, restore


def test_locate_instance_returns_the_bytes_url_pair():
    folder = "https://www.sec.gov/Archives/edgar/data/999002/000999900226000381"
    calls, restore = _patched_edgar({"/a_htm.xml": b"<xbrl/>"})
    try:
        assert X.locate_instance(999002, "0009999002-26-000381", "a.htm", "20-F", "2026-03-31") == (
            b"<xbrl/>", f"{folder}/a_htm.xml")
        assert calls == [f"{folder}/a_htm.xml"], calls
    finally:
        restore()
    # the guess absent, the index lists the instance under another name
    calls, restore = _patched_edgar({"/index.json": {"directory": {"item": [{"name": "a.htm"}, {"name": "b_lab.xml"},
                                                                             {"name": "b.xml"}]}},
                                     "/b.xml": b"<xbrl/>"})
    try:
        assert X.locate_instance(999002, "0009999002-26-000381", "a.htm") == (b"<xbrl/>", f"{folder}/b.xml")
    finally:
        restore()
    # no instance: the guess and every listed candidate 404, or index.json itself 404s
    for answers in ({"/index.json": {"directory": {"item": [{"name": "a.htm"}]}}}, {}):
        calls, restore = _patched_edgar(answers)
        try:
            assert X.locate_instance(999002, "0009999002-26-000381", "a.htm") == (None, None)
        finally:
            restore()


def test_locate_instance_raises_on_a_transient_index_failure():
    """[whole-PR review fix, 2026-10-21; fails on 6dd4a4a] segments.locate_files turns a failed index.json into an
    empty listing, so a 503 after the <base>_htm.xml guess 404s came back as (None, None) — "no instance", which the
    engine recorded as the permanent "inline document only". locate_instance's promise is that a fetch failure other
    than a 404 raises; it now does, for index.json and for a listed candidate alike."""
    import urllib.error
    err = urllib.error.HTTPError("https://www.sec.gov/x/index.json", 503, "Service Unavailable", {}, None)
    for answers in ({"/index.json": err},
                    {"/index.json": {"directory": {"item": [{"name": "b.xml"}]}}, "/b.xml": TimeoutError("timed out")}):
        calls, restore = _patched_edgar(answers)
        try:
            try:
                X.locate_instance(1009001, "0001193125-26-116229", "ccj-20251231.htm", "40-F", "2025-12-31")
                raise AssertionError(f"no exception after {calls}")
            except (urllib.error.HTTPError, TimeoutError):
                pass
        finally:
            restore()


def test_consistent_duplicates_keep_the_precise_fact():
    """[whole-PR review fix, 2026-10-21; fails on 6dd4a4a] One line tagged twice at two precisions is not a conflict
    (XBRL consistency: equal once rounded to the smaller decimals): CCJ's FY2025 OCF 1,408,432,000 (decimals 0) beside
    1,408,000,000 (decimals -6) keeps the precise fact — the fallback had refused the year ("no undimensioned annual
    operating cash flow") — and its capex 333,025,000 beside 333,000,000 merges (the year had merged with capex 0 and
    a DATA_GAP:capex). Inconsistent values (1,408,432,000 beside 1,409,000,000 at -6), a missing decimals and two
    different exact (INF) values stay conflicts."""
    def f(v, d, tag="CashFlowsFromUsedInOperatingActivities"):
        return {"taxonomy": "ifrs-full", "tag": tag, "unit": "CAD", "start": "2025-01-01", "end": "2025-12-31",
                "instant": None, "value": v, "decimals": d, "context": "c"}
    entries, conflicts = X.annual_facts_after({"facts": [f(1408432000, 0), f(1408000000, -6)]}, "2024-12-31")
    assert conflicts == [] and [(e["val"], e["decimals"]) for e in entries] == [(1408432000, 0)], (entries, conflicts)
    entries, conflicts = X.annual_facts_after({"facts": [f(333000000, -6, "P"), f(333025000, -3, "P")]}, None)
    assert conflicts == [] and [(e["val"], e["decimals"]) for e in entries] == [(333025000, -3)], (entries, conflicts)
    entries, _ = X.annual_facts_after({"facts": [f(0.72, 2, "EPS"), f(0.725, "INF", "EPS")]}, None)
    assert [(e["val"], e["decimals"]) for e in entries] == [(0.725, "INF")], entries
    # pair by pair: 0.7249 (decimals 4) is consistent with 0.72 (2) but not with the exact 0.725
    for pair in ((f(1408432000, 0), f(1409000000, -6)), (f(1408432000, None), f(1408000000, -6)),
                 (f(5, "INF"), f(6, "INF")), (f(0.7249, 4, "EPS"), f(0.72, 2, "EPS"), f(0.725, "INF", "EPS"))):
        entries, conflicts = X.annual_facts_after({"facts": list(pair)}, None)
        assert entries == [] and len(conflicts) == 1, (pair, entries, conflicts)


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
