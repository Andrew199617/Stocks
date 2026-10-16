#!/usr/bin/env python3
"""segments.py pure-function tests. Run: python _system/tests/test_segments.py
(or python -m pytest _system/tests). No network: every input is an inline XML
fixture — a toy 10-K instance, a toy Q3 10-Q instance (with the nine-month leg
that lets Q4 be derived) and a toy label linkbase.

Covers: context / unit / fact parsing with QName canonicalisation (a filing that
declares the us-gaap namespace under the prefix "gaap"), dimension
classification (single kept axis, kept axis + consolidation member,
eliminations-only, operating-segments subtotal, two kept axes, typed member),
period classification (12- and 16-week quarters, 52/53-week years, YTD legs),
label linkbase parsing with the standard-label role and the de-camel fallback,
definition-linkbase parsing (member hierarchy, locators resolved per extended
link) from a bare linkbase and from a schema with the linkbases embedded (the
DFIN-style folder, with EDGAR mocked), fiscal-year / quarter naming anchored
on dei facts (Kroger-style January year end; a December year drifting into
early January), and the table assembly: latest filing wins, Q4 derived as FY
minus nine months and flagged, share_of_total on the consolidated fact vs the
sum of rows, growth_yoy against the column one year earlier, row ordering with
reconciling rows last, foreign-currency facts dropped with a warning, the
empty-tables-plus-warning path for a company with no dimensioned facts, and the
double-count rules on real filers' shapes: segment x reconciling matrix cells
ignored (Huntington), Expedia's intersegment revenue rows dropped because the
bare segment rows already tie, subtotal members dropped by name (Martin
Marietta, Centene), by hierarchy (Alnylam) and by value (Cognizant's Europe),
one line under two member names (Axon), leftover tables dropped (Con Edison),
partial breakdowns kept but flagged, and the --all skip predicate that retries
degraded outputs.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SYS = os.path.dirname(HERE)
sys.path.insert(0, SYS)
import segments as S  # noqa: E402

HEAD = """<?xml version="1.0" encoding="utf-8"?>
<xbrl xmlns="http://www.xbrl.org/2003/instance"
  xmlns:gaap="http://fasb.org/us-gaap/2025" xmlns:srt="http://fasb.org/srt/2025"
  xmlns:dei="http://xbrl.sec.gov/dei/2025" xmlns:country="http://xbrl.sec.gov/country/2025"
  xmlns:iso4217="http://www.xbrl.org/2003/iso4217" xmlns:xbrldi="http://xbrl.org/2006/xbrldi"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:toy="http://www.toy.com/20251231">
"""


def ctx(cid, start=None, end=None, instant=None, dims=(), typed=False):
    seg = ""
    if dims or typed:
        seg = "<segment>" + "".join(f'<xbrldi:explicitMember dimension="{a}">{m}</xbrldi:explicitMember>' for a, m in dims)
        if typed:
            seg += '<xbrldi:typedMember dimension="toy:LoanAxis"><toy:LoanId>7</toy:LoanId></xbrldi:typedMember>'
        seg += "</segment>"
    per = f"<instant>{instant}</instant>" if instant else f"<startDate>{start}</startDate><endDate>{end}</endDate>"
    return f'<context id="{cid}"><entity><identifier scheme="http://www.sec.gov/CIK">0000000001</identifier>{seg}</entity><period>{per}</period></context>'


def fact(tag, cid, value, unit="usd", nil=False):
    if nil:
        return f'<{tag} contextRef="{cid}" unitRef="{unit}" xsi:nil="true"/>'
    return f'<{tag} contextRef="{cid}" unitRef="{unit}" decimals="-3">{value}</{tag}>'


UNITS = '<unit id="usd"><measure>iso4217:USD</measure></unit><unit id="eur"><measure>iso4217:EUR</measure></unit><unit id="shares"><measure>shares</measure></unit>'
SEG = "gaap:StatementBusinessSegmentsAxis"
GEO = "srt:StatementGeographicalAxis"
CON = "srt:ConsolidationItemsAxis"
A, B = "toy:AlphaSegmentMember", "toy:BetaSegmentMember"


def tenk_xml():
    cs = [
        ctx("fy25", "2025-01-01", "2025-12-31"), ctx("fy24", "2024-01-01", "2024-12-31"),
        ctx("fy25A", "2025-01-01", "2025-12-31", dims=[(SEG, A), (CON, "gaap:OperatingSegmentsMember")]),
        ctx("fy25B", "2025-01-01", "2025-12-31", dims=[(SEG, B), (CON, "gaap:OperatingSegmentsMember")]),
        ctx("fy24A", "2024-01-01", "2024-12-31", dims=[(SEG, A)]), ctx("fy24B", "2024-01-01", "2024-12-31", dims=[(SEG, B)]),
        ctx("fy25E", "2025-01-01", "2025-12-31", dims=[(CON, "gaap:IntersegmentEliminationMember")]),
        ctx("fy25OS", "2025-01-01", "2025-12-31", dims=[(CON, "gaap:OperatingSegmentsMember")]),
        ctx("fy25AUS", "2025-01-01", "2025-12-31", dims=[(SEG, A), (GEO, "country:US")]),
        ctx("fy25T", "2025-01-01", "2025-12-31", typed=True),
        ctx("fy25US", "2025-01-01", "2025-12-31", dims=[(GEO, "country:US")]), ctx("fy25ROW", "2025-01-01", "2025-12-31", dims=[(GEO, "gaap:NonUsMember")]),
        ctx("i25", instant="2025-12-31"), ctx("i25A", instant="2025-12-31", dims=[(SEG, A)]), ctx("i25B", instant="2025-12-31", dims=[(SEG, B)]),
        ctx("i24A", instant="2024-12-31", dims=[(SEG, A)]), ctx("i24B", instant="2024-12-31", dims=[(SEG, B)]),
    ]
    fs = [
        fact("dei:DocumentFiscalYearFocus", "fy25", "2025"), fact("dei:DocumentFiscalPeriodFocus", "fy25", "FY"),
        fact("dei:CurrentFiscalYearEndDate", "fy25", "--12-31"), fact("dei:DocumentPeriodEndDate", "fy25", "2025-12-31"),
        fact("gaap:Revenues", "fy25", 950), fact("gaap:Revenues", "fy24", 800),
        fact("gaap:Revenues", "fy25A", 600), fact("gaap:Revenues", "fy25B", 400), fact("gaap:Revenues", "fy25E", -50),
        fact("gaap:Revenues", "fy24A", 500), fact("gaap:Revenues", "fy24B", 300),
        fact("gaap:Revenues", "fy25OS", 1000), fact("gaap:Revenues", "fy25AUS", 450), fact("gaap:Revenues", "fy25T", 1),
        fact("gaap:Revenues", "fy25US", 700), fact("gaap:Revenues", "fy25ROW", 250),
        fact("gaap:OperatingIncomeLoss", "fy25A", 120), fact("gaap:OperatingIncomeLoss", "fy25B", 30, nil=True),
        fact("gaap:OperatingIncomeLoss", "fy24A", 100), fact("gaap:OperatingIncomeLoss", "fy24B", 20),
        fact("gaap:Assets", "i25", 5000), fact("gaap:Assets", "i25A", 3000), fact("gaap:Assets", "i25B", 1500),
        fact("gaap:Assets", "i24A", 2500), fact("gaap:Assets", "i24B", 1400),
        fact("gaap:Revenues", "fy25A", 999, unit="eur"),
        fact("gaap:WeightedAverageNumberOfDilutedSharesOutstanding", "fy25", 100, unit="shares"),
    ]
    return HEAD + UNITS + "".join(cs) + "".join(fs) + "</xbrl>"


def tenq_xml(a_q3=180):
    """A Q3 10-Q: three-month Q3 for both years, nine-month legs for both years, Q3 instants."""
    cs = [
        ctx("q3", "2025-07-01", "2025-09-30"), ctx("q3p", "2024-07-01", "2024-09-30"),
        ctx("ytd", "2025-01-01", "2025-09-30"), ctx("ytdp", "2024-01-01", "2024-09-30"),
        ctx("q3A", "2025-07-01", "2025-09-30", dims=[(SEG, A)]), ctx("q3B", "2025-07-01", "2025-09-30", dims=[(SEG, B)]),
        ctx("q3pA", "2024-07-01", "2024-09-30", dims=[(SEG, A)]), ctx("q3pB", "2024-07-01", "2024-09-30", dims=[(SEG, B)]),
        ctx("ytdA", "2025-01-01", "2025-09-30", dims=[(SEG, A)]), ctx("ytdB", "2025-01-01", "2025-09-30", dims=[(SEG, B)]),
        ctx("ytdpA", "2024-01-01", "2024-09-30", dims=[(SEG, A)]), ctx("ytdpB", "2024-01-01", "2024-09-30", dims=[(SEG, B)]),
    ]
    fs = [
        fact("dei:DocumentFiscalYearFocus", "ytd", "2025"), fact("dei:DocumentFiscalPeriodFocus", "ytd", "Q3"),
        fact("dei:CurrentFiscalYearEndDate", "ytd", "--12-31"), fact("dei:DocumentPeriodEndDate", "ytd", "2025-09-30"),
        fact("gaap:Revenues", "q3", 260), fact("gaap:Revenues", "q3p", 210), fact("gaap:Revenues", "ytd", 700), fact("gaap:Revenues", "ytdp", 600),
        fact("gaap:Revenues", "q3A", a_q3), fact("gaap:Revenues", "q3B", 80), fact("gaap:Revenues", "q3pA", 150), fact("gaap:Revenues", "q3pB", 60),
        fact("gaap:Revenues", "ytdA", 450), fact("gaap:Revenues", "ytdB", 250), fact("gaap:Revenues", "ytdpA", 380), fact("gaap:Revenues", "ytdpB", 220),
    ]
    return HEAD + UNITS + "".join(cs) + "".join(fs) + "</xbrl>"


LAB = """<?xml version="1.0" encoding="utf-8"?>
<link:linkbase xmlns:link="http://www.xbrl.org/2003/linkbase" xmlns:xlink="http://www.w3.org/1999/xlink">
 <link:labelLink xlink:type="extended" xlink:role="http://www.xbrl.org/2003/role/link">
  <link:loc xlink:type="locator" xlink:label="loc_toy_AlphaSegmentMember" xlink:href="toy-20251231.xsd#toy_AlphaSegmentMember"/>
  <link:label xlink:type="resource" xlink:label="lab_toy_AlphaSegmentMember" xlink:role="http://www.xbrl.org/2003/role/terseLabel" xml:lang="en-US">Alpha (terse)</link:label>
  <link:label xlink:type="resource" xlink:label="lab_toy_AlphaSegmentMember" xlink:role="http://www.xbrl.org/2003/role/label" xml:lang="en-US">Alpha Platform [Member]</link:label>
  <link:labelArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/concept-label" xlink:from="loc_toy_AlphaSegmentMember" xlink:to="lab_toy_AlphaSegmentMember"/>
  <loc xmlns="http://www.xbrl.org/2003/linkbase" xlink:type="locator" xlink:label="loc_country_US" xlink:href="https://xbrl.sec.gov/country/2025/country-2025.xsd#country_US"/>
  <label xmlns="http://www.xbrl.org/2003/linkbase" xlink:type="resource" xlink:label="lab_country_US" xlink:role="http://www.xbrl.org/2003/role/label" xml:lang="en-US">UNITED STATES</label>
  <labelArc xmlns="http://www.xbrl.org/2003/linkbase" xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/concept-label" xlink:from="loc_country_US" xlink:to="lab_country_US"/>
 </link:labelLink>
</link:linkbase>"""


def _table(out, axis, concept, periodicity):
    for t in out["tables"]:
        if (t["axis"], t["concept"], t["periodicity"]) == (axis, concept, periodicity):
            return t
    return None


def _row(t, member):
    return next(r for r in t["rows"] if r["member"] == member)


# ---------------- parsing ----------------
def test_parse_instance_canonicalises_and_filters():
    p = S.parse_instance(tenk_xml())
    assert len(p["contexts"]) == 17 and p["units"]["usd"] == "iso4217:USD" and p["units"]["eur"] == "iso4217:EUR"
    c = p["contexts"]["fy25A"]
    assert c["start"] == "2025-01-01" and c["end"] == "2025-12-31" and c["instant"] is None
    assert c["dims"] == {"us-gaap:StatementBusinessSegmentsAxis": "toy:AlphaSegmentMember", "srt:ConsolidationItemsAxis": "us-gaap:OperatingSegmentsMember"}, c["dims"]
    assert p["contexts"]["fy25T"]["typed"] is True and p["contexts"]["i25"]["instant"] == "2025-12-31"
    tags = {f["tag"] for f in p["facts"]}
    assert tags == {"us-gaap:Revenues", "us-gaap:OperatingIncomeLoss", "us-gaap:Assets"}, tags
    assert not any(f["context"] == "fy25B" and f["concept"] == "OperatingIncomeLoss" for f in p["facts"]), "nil fact must be dropped"
    assert sum(1 for f in p["facts"] if f["context"] == "fy25A" and f["concept"] == "Revenues") == 2, "both USD and EUR facts parsed; currency filtering happens later"
    assert p["dei"] == {"DocumentFiscalYearFocus": "2025", "DocumentFiscalPeriodFocus": "FY", "CurrentFiscalYearEndDate": "--12-31", "DocumentPeriodEndDate": "2025-12-31"}


def test_classify_context():
    p = S.parse_instance(tenk_xml())["contexts"]
    assert S.classify_context(p["fy25"]) == ("consolidated", None, None, None)
    assert S.classify_context(p["fy25A"]) == ("row", "business_segments", A, None), "OperatingSegmentsMember on the consolidation axis is not a reconciling member"
    assert S.classify_context(p["fy24A"]) == ("row", "business_segments", A, None)
    assert S.classify_context(p["fy25E"]) == ("row", "business_segments", "us-gaap:IntersegmentEliminationMember", None)
    assert S.classify_context(p["fy25OS"])[0] == "ignore", "operating-segments subtotal alone is ignored"
    assert S.classify_context(p["fy25AUS"])[0] == "ignore", "two kept axes are ignored"
    assert S.classify_context(p["fy25T"])[0] == "ignore", "typed members are ignored"
    assert S.classify_context(p["fy25US"]) == ("row", "geography", "country:US", None)
    mixed = {"dims": {"us-gaap:StatementBusinessSegmentsAxis": A, "srt:ConsolidationItemsAxis": "us-gaap:IntersegmentEliminationMember"}, "typed": False}
    assert S.classify_context(mixed)[0] == "ignore", "segment x reconciling member is a matrix cell already inside the bare member's figure"
    corp = {"dims": {"srt:ProductOrServiceAxis": "hban:CapitalMarketFeesMember", "srt:ConsolidationItemsAxis": "us-gaap:CorporateNonSegmentMember"}, "typed": False}
    assert S.classify_context(corp)[0] == "ignore", "Huntington's product x Corporate cell is ignored"
    other = {"dims": {"us-gaap:StatementBusinessSegmentsAxis": A, "us-gaap:StatementClassOfStockAxis": "us-gaap:CommonClassAMember"}, "typed": False}
    assert S.classify_context(other)[0] == "ignore"
    assert S.is_reconciling("us-gaap:CorporateNonSegmentMember") and S.is_reconciling(A, consol_only=True)
    assert not S.is_reconciling(A) and S.is_reconciling("gfi:CorporateAndOtherDomain")
    assert S.is_standard("us-gaap:IntersegmentEliminationMember") and S.is_standard("srt:EuropeMember") and not S.is_standard("expe:CorporateAndEliminationsMember")
    assert S.normalized_name("axon:SoftwareAndSensorsSegmentMember") == S.normalized_name("axon:SoftwareAndSensorsMember") == "softwareandsensors"


def test_period_kind():
    assert S.period_kind("2025-01-01", "2025-12-31") == "annual"
    assert S.period_kind("2025-02-02", "2026-01-31") == "annual", "52-week year (364 days)"
    assert S.period_kind("2024-01-28", "2025-02-01") == "annual", "53-week year (371 days)"
    assert S.period_kind("2025-04-01", "2025-06-30") == "quarter", "91 days"
    assert S.period_kind("2026-05-24", "2026-08-15") == "quarter", "12-week quarter (84 days)"
    assert S.period_kind("2026-02-01", "2026-05-23") == "quarter", "16-week first quarter (112 days)"
    assert S.period_kind("2026-02-01", "2026-08-15") == "6m", "28-week year-to-date (196 days)"
    assert S.period_kind("2025-01-01", "2025-09-30") == "9m"
    assert S.period_kind("2025-12-01", "2025-12-31") is None and S.period_kind("x", "y") is None


def test_labels_and_fallback():
    labels = S.parse_labels(LAB)
    assert labels == {"toy_AlphaSegmentMember": "Alpha Platform [Member]", "country_US": "UNITED STATES"}, labels
    assert S.member_label(A, labels) == "Alpha Platform", "standard label wins over terse and [Member] is stripped"
    assert S.member_label("country:US", labels) == "UNITED STATES"
    assert S.member_label(B, labels) == "Beta", "fallback: de-camel-case minus Segment/Member"
    assert S.fallback_label("hban:ConsumerAndBusinessBankingMember") == "Consumer And Business Banking"
    assert S.fallback_label("gfi:CorporateAndOtherDomain") == "Corporate And Other"
    assert S.fallback_label("us-gaap:NonUsMember") == "Non Us"
    assert S.ns_prefix("http://fasb.org/us-gaap/2019") == "us-gaap" and S.ns_prefix("https://xbrl.ifrs.org/taxonomy/2025-03-27/ifrs-full") == "ifrs-full"
    assert S.ns_prefix("http://www.toy.com/20251231") is None


def test_fiscal_calendar():
    kr = S.FiscalCalendar((1, 30), "2026-05-23", 2026, "Q1")  # Kroger: FY ends late January, Q1 FY2026 ended 2026-05-23
    assert kr.fiscal_year("2026-01-31") == 2025 and kr.fiscal_year("2025-02-01") == 2024
    assert kr.label("annual", "2026-01-31") == "FY2025" and kr.label("annual", "2025-02-01") == "FY2024"
    assert kr.label("quarter", "2026-05-23") == "Q1 FY2026" and kr.label("quarter", "2025-05-24") == "Q1 FY2025"
    assert kr.label("quarter", "2026-08-15") == "Q2 FY2026" and kr.label("quarter", "2025-08-16") == "Q2 FY2025"
    cal = S.FiscalCalendar((12, 31), "2026-06-30", 2026, "Q2")  # calendar-year filer anchored on its Q2 10-Q
    assert cal.label("annual", "2025-12-31") == "FY2025" and cal.label("annual", "2023-12-31") == "FY2023"
    assert cal.label("quarter", "2026-06-30") == "Q2 FY2026" and cal.label("quarter", "2025-03-31") == "Q1 FY2025"
    assert cal.label("quarter", "2025-12-31", derived_q4=True) == "Q4 FY2025"
    assert cal.label("instant", "2025-12-31") == "FY2025 end" and cal.label("instant", "2026-06-30") == "Q2 FY2026"
    none = S.FiscalCalendar()  # no dei anchor anywhere: calendar year of the period end
    assert none.label("annual", "2026-01-31") == "FY2026" and none.label("quarter", "2026-05-23") == "3M to 2026-05-23"
    # a "Saturday nearest December 31" filer whose year drifted into January: year ended 2024-01-02 is FY2023
    dec = S.FiscalCalendar((12, 31), "2024-01-02", 2023, "FY")
    assert dec.label("annual", "2024-01-02") == "FY2023" and dec.label("instant", "2024-01-02") == "FY2023 end"
    assert dec.label("quarter", "2024-04-02") == "Q1 FY2024" and dec.label("annual", "2022-12-31") == "FY2022"
    assert dec.label("annual", "2024-12-28") == "FY2024", "a year ending a few days before the nominal FYE"
    q1 = S.FiscalCalendar((12, 31), "2024-04-02", 2024, "Q1")  # the same filer anchored on its Q1 10-Q
    assert q1.label("annual", "2024-01-02") == "FY2023" and q1.label("quarter", "2024-04-02") == "Q1 FY2024" and q1.label("instant", "2024-01-02") == "FY2023 end"
    parsed = [{"form": "10-K", "instance": {"dei": {}}}, {"form": "10-Q", "instance": S.parse_instance(tenq_xml())}]
    assert S.FiscalCalendar.from_filings(parsed).label("annual", "2025-12-31") == "FY2025", "anchor taken from the latest filing that has dei facts"
    # Mettler-Toledo's Q2 2026 10-Q tags DocumentFiscalYearFocus 2024 for a period ending 2026-06-30: a filer error,
    # so the anchor comes from the 10-K instead and 2025-12-31 is FY2025, not FY2023
    bad = {"form": "10-Q", "instance": {"dei": {"CurrentFiscalYearEndDate": "--12-31", "DocumentFiscalYearFocus": "2024", "DocumentPeriodEndDate": "2026-06-30", "DocumentFiscalPeriodFocus": "Q2"}}}
    parsed = [{"form": "10-K", "instance": S.parse_instance(tenk_xml())}, bad]
    mtd = S.FiscalCalendar.from_filings(parsed)
    assert mtd.label("annual", "2025-12-31") == "FY2025" and mtd.label("quarter", "2026-06-30") == "Q2 FY2026", (mtd.anchor_fy, mtd.anchor_fy_end)
    assert S.FiscalCalendar.from_filings([bad]).label("annual", "2025-12-31") == "FY2025", "no usable anchor at all: calendar year of the period end"
    assert S.FiscalCalendar.from_filings([{"form": "10-K", "instance": {"dei": {}}}], "0131").fye == (1, 31), "submissions fiscalYearEnd fallback"


# ---------------- assembly ----------------
def _filings(a_q3_latest=None):
    labels = S.parse_labels(LAB)
    fs = [
        {"form": "10-K", "accession": "0000000001-26-000001", "filed": "2026-02-20", "period": "2025-12-31", "instance_url": "k", "instance": S.parse_instance(tenk_xml()), "labels": labels},
        {"form": "10-Q", "accession": "0000000001-25-000003", "filed": "2025-11-01", "period": "2025-09-30", "instance_url": "q", "instance": S.parse_instance(tenq_xml()), "labels": {}},
    ]
    if a_q3_latest is not None:  # a later 10-Q restating Q3 segment A
        fs.append({"form": "10-Q", "accession": "0000000001-26-000009", "filed": "2026-05-01", "period": "2026-03-31", "instance_url": "q2", "instance": S.parse_instance(tenq_xml(a_q3_latest)), "labels": {}})
    fs.sort(key=lambda f: f["filed"])
    return fs


def test_build_output_annual_tables():
    out = S.build_output("TOY", 1, _filings(), "1231")
    assert out["currency"] == "USD" and out["source"] == S.SOURCE and [f["form"] for f in out["filings"]] == ["10-Q", "10-K"]
    assert any("EUR" not in w and "currency other than USD" in w for w in out["warnings"]), out["warnings"]
    t = _table(out, "business_segments", "Revenues", "annual")
    assert t and t["periods"] == ["2024-12-31", "2025-12-31"] and t["period_labels"] == ["FY2024", "FY2025"] and t["label"] == "Revenue by segment"
    assert [r["member"] for r in t["rows"]] == [A, B, "us-gaap:IntersegmentEliminationMember"], "largest first, eliminations last"
    a = _row(t, A)
    assert a["label"] == "Alpha Platform" and a["values"] == [500, 600] and a["derived"] == [False, False]
    assert a["growth_yoy"] == [None, 0.2] and a["share_of_total"] == [round(500 / 800, 4), round(600 / 950, 4)]
    assert t["total"] == {"values": [800, 950], "basis": "consolidated fact"}, "consolidated Revenues fact, not the 1000 operating-segments subtotal"
    e = _row(t, "us-gaap:IntersegmentEliminationMember")
    assert e["values"] == [None, -50] and e["label"] == "Intersegment Elimination" and e["growth_yoy"] == [None, None]
    oi = _table(out, "business_segments", "OperatingIncomeLoss", "annual")
    assert oi["total"] == {"values": [120, 120], "basis": "sum of rows"} and _row(oi, B)["values"] == [20, None], "nil fact leaves a hole; no consolidated OperatingIncomeLoss -> sum of rows"
    geo = _table(out, "geography", "Revenues", "annual")
    assert [r["label"] for r in geo["rows"]] == ["UNITED STATES", "Non Us"] and geo["total"]["values"] == [950]
    assets = _table(out, "business_segments", "Assets", "annual")
    assert assets["periods"] == ["2024-12-31", "2025-12-31"] and assets["period_labels"] == ["FY2024 end", "FY2025 end"]
    assert _row(assets, A)["share_of_total"] == [round(2500 / 3900, 4), 0.6] and assets["total"]["basis"].startswith("mixed"), "2024 total is the sum of rows (3900), 2025 the consolidated 5000"
    assert assets["total"]["values"] == [3900, 5000]
    assert _table(out, "product", "Revenues", "annual") is None


def test_build_output_quarterly_and_derived_q4():
    out = S.build_output("TOY", 1, _filings(), "1231")
    q = _table(out, "business_segments", "Revenues", "quarterly")
    # the 10-K carries FY2024 too and the Q3 10-Q the 2024 nine-month leg, so Q4 FY2024 is derivable as well
    assert q and q["periods"] == ["2024-09-30", "2024-12-31", "2025-09-30", "2025-12-31"], q["periods"]
    assert q["period_labels"] == ["Q3 FY2024", "Q4 FY2024", "Q3 FY2025", "Q4 FY2025"], q["period_labels"]
    a = _row(q, A)
    assert a["values"] == [150, 120, 180, 150] and a["derived"] == [False, True, False, True], "Q4 FY2025 = FY 600 - nine months 450; Q4 FY2024 = 500 - 380"
    assert a["growth_yoy"] == [None, None, 0.2, 0.25]
    b = _row(q, B)
    assert b["values"] == [60, 80, 80, 150] and b["derived"] == [False, True, False, True], "Q4 = 400 - 250 and 300 - 220"
    assert "us-gaap:IntersegmentEliminationMember" not in [r["member"] for r in q["rows"]], "no nine-month leg for the eliminations row -> no derived Q4 -> no quarterly row"
    assert q["total"]["values"] == [210, 200, 260, 250] and q["total"]["basis"] == "consolidated fact", "derived consolidated Q4s = 800 - 600 and 950 - 700"
    assert a["share_of_total"] == [round(150 / 210, 4), 0.6, round(180 / 260, 4), 0.6]


def test_latest_filing_wins_and_empty_company():
    out = S.build_output("TOY", 1, _filings(a_q3_latest=200), "1231")
    q = _table(out, "business_segments", "Revenues", "quarterly")
    assert _row(q, A)["values"] == [150, 120, 200, 150], "the later 10-Q's restated Q3 FY2025 value (200) replaces the earlier 180"
    bare = HEAD + UNITS + ctx("fy25", "2025-01-01", "2025-12-31") + fact("gaap:Revenues", "fy25", 950) + "</xbrl>"
    empty = S.build_output("BARE", 2, [{"form": "10-K", "accession": "x", "filed": "2026-01-01", "period": "2025-12-31", "instance_url": "u", "instance": S.parse_instance(bare), "labels": {}}])
    assert empty["tables"] == [] and any("no dimensioned facts" in w for w in empty["warnings"]), empty["warnings"]
    none = S.build_output("NONE", 3, [{"form": "20-F", "accession": "y", "filed": "2026-01-01", "period": "2025-12-31", "instance_url": None, "instance": None, "labels": {}}])
    assert none["tables"] == [] and none["currency"] is None
    assert any("no XBRL instance" in w for w in none["warnings"]) and any("20-F filer" in w for w in none["warnings"])
    assert S.build_output("ZERO", 4, [])["tables"] == []


def test_bare_member_beats_operating_segments_member_within_a_filing():
    """Expedia-style double tagging: trivago revenue 145 (bare member, external) and 196 (member +
    OperatingSegmentsMember, gross of intersegment). The bare fact wins whichever comes first in the file;
    a later filing still overwrites both. trivago x IntersegmentElimination (51) is a matrix cell: no row."""
    def inst(bare, gross, bare_first):
        cs = [ctx("q", "2026-04-01", "2026-06-30"), ctx("qA", "2026-04-01", "2026-06-30", dims=[(SEG, A)]),
              ctx("qT", "2026-04-01", "2026-06-30", dims=[(SEG, B)]),
              ctx("qTo", "2026-04-01", "2026-06-30", dims=[(SEG, B), (CON, "gaap:OperatingSegmentsMember")]),
              ctx("qTe", "2026-04-01", "2026-06-30", dims=[(SEG, B), (CON, "gaap:IntersegmentEliminationMember")])]
        fs = [fact("gaap:Revenues", "q", 4315), fact("gaap:Revenues", "qA", 4170), fact("gaap:Revenues", "qTe", 51)]
        pair = [fact("gaap:Revenues", "qT", bare), fact("gaap:Revenues", "qTo", gross)]
        fs += pair if bare_first else pair[::-1]
        return S.parse_instance(HEAD + UNITS + "".join(cs) + "".join(fs) + "</xbrl>")
    for bare_first in (True, False):
        out = S.build_output("TOY", 1, [{"form": "10-Q", "accession": "a", "filed": "2026-08-01", "period": "2026-06-30", "instance_url": "u", "instance": inst(145, 196, bare_first), "labels": {}}], "1231")
        q = _table(out, "business_segments", "Revenues", "quarterly")
        assert _row(q, B)["values"] == [145], (bare_first, _row(q, B)["values"])
        assert [r["member"] for r in q["rows"]] == [A, B] and q["ties_to_total"] is True, q["rows"]
    later = {"form": "10-Q", "accession": "b", "filed": "2026-11-01", "period": "2026-09-30", "instance_url": "u", "instance": inst(150, 200, False), "labels": {}}
    first = {"form": "10-Q", "accession": "a", "filed": "2026-08-01", "period": "2026-06-30", "instance_url": "u", "instance": inst(145, 196, True), "labels": {}}
    out = S.build_output("TOY", 1, [first, later], "1231")
    assert _row(_table(out, "business_segments", "Revenues", "quarterly"), B)["values"] == [150], "later filing wins, then bare beats gross"


def _one_filing(cs, fs, form="10-K", period="2025-12-31", labels=None, hierarchy=None, dei=True):
    if dei:
        fs = [fact("dei:DocumentFiscalYearFocus", "fy", "2025"), fact("dei:DocumentFiscalPeriodFocus", "fy", "FY"),
              fact("dei:CurrentFiscalYearEndDate", "fy", "--12-31"), fact("dei:DocumentPeriodEndDate", "fy", period)] + fs
    inst = S.parse_instance(HEAD + UNITS + "".join(cs) + "".join(fs) + "</xbrl>")
    return {"form": form, "accession": "k", "filed": "2026-02-20", "period": period, "instance_url": "u", "instance": inst, "labels": labels or {}, "hierarchy": hierarchy or {}}


def test_expedia_intersegment_revenue_rows_are_dropped():
    """Expedia's Q2 2026 10-Q (0001324424-26-000053): B2C 2,677 + B2B 1,493 + trivago 145 = 4,315 = the
    consolidated fact; the bare IntersegmentEliminationMember fact is +51 (trivago's intersegment revenue,
    inside the gross 196, not the external 145) and the OperatingSegments subtotal 4,366. The +51 row goes.
    The 10-K (0001324424-26-000008): 9,474 + 4,842 + 417 = 14,733 with a -205 elimination tagged both bare
    and under expe:CorporateAndEliminationsMember on the consolidation axis -> merged, then dropped."""
    PRD = "srt:ProductOrServiceAxis"
    cs = [ctx("fy", "2026-04-01", "2026-06-30"),
          ctx("b2c", "2026-04-01", "2026-06-30", dims=[(SEG, "expe:B2CMember")]), ctx("b2b", "2026-04-01", "2026-06-30", dims=[(SEG, "expe:B2BMember")]),
          ctx("tv", "2026-04-01", "2026-06-30", dims=[(SEG, "expe:TrivagoMember")]),
          ctx("tvo", "2026-04-01", "2026-06-30", dims=[(SEG, "expe:TrivagoMember"), (CON, "gaap:OperatingSegmentsMember")]),
          ctx("tve", "2026-04-01", "2026-06-30", dims=[(SEG, "expe:TrivagoMember"), (CON, "gaap:IntersegmentEliminationMember")]),
          ctx("el", "2026-04-01", "2026-06-30", dims=[(CON, "gaap:IntersegmentEliminationMember")]),
          ctx("os", "2026-04-01", "2026-06-30", dims=[(CON, "gaap:OperatingSegmentsMember")]),
          ctx("lodg", "2026-04-01", "2026-06-30", dims=[(PRD, "expe:LodgingMember")]), ctx("air", "2026-04-01", "2026-06-30", dims=[(PRD, "expe:AirMember")])]
    R = "gaap:RevenueFromContractWithCustomerExcludingAssessedTax"
    fs = [fact(R, "fy", 4315), fact(R, "b2c", 2677), fact(R, "b2b", 1493), fact(R, "tv", 145), fact(R, "tvo", 196), fact(R, "tve", 51),
          fact(R, "el", 51), fact(R, "el", 51), fact(R, "os", 4366), fact(R, "lodg", 3429), fact(R, "air", 886)]
    out = S.build_output("EXPE", 1, [_one_filing(cs, fs, form="10-Q", period="2026-06-30", dei=False)], "1231")
    q = _table(out, "business_segments", "RevenueFromContractWithCustomerExcludingAssessedTax", "quarterly")
    assert [r["member"] for r in q["rows"]] == ["expe:B2CMember", "expe:B2BMember", "expe:TrivagoMember"], [r["member"] for r in q["rows"]]
    assert _row(q, "expe:TrivagoMember")["values"] == [145] and q["total"] == {"values": [4315], "basis": "consolidated fact"} and q["ties_to_total"] is True
    assert abs(sum(r["share_of_total"][0] for r in q["rows"]) - 1) < 1e-3
    assert any("Intersegment" in w and "dropped" in w and "tie" in w for w in out["warnings"]), out["warnings"]
    # the 10-K: elimination tagged twice with identical numbers (-205), both inside the gross figures
    cs = [ctx("fy", "2025-01-01", "2025-12-31"),
          ctx("b2c", "2025-01-01", "2025-12-31", dims=[(SEG, "expe:B2CMember")]), ctx("b2b", "2025-01-01", "2025-12-31", dims=[(SEG, "expe:BusinessToBusinessMember")]),
          ctx("tv", "2025-01-01", "2025-12-31", dims=[(SEG, "expe:TrivagoMember")]),
          ctx("tvo", "2025-01-01", "2025-12-31", dims=[(SEG, "expe:TrivagoMember"), (CON, "gaap:OperatingSegmentsMember")]),
          ctx("corp", "2025-01-01", "2025-12-31", dims=[(CON, "gaap:CorporateNonSegmentMember")]),
          ctx("el", "2025-01-01", "2025-12-31", dims=[(CON, "gaap:IntersegmentEliminationMember")]),
          ctx("ce", "2025-01-01", "2025-12-31", dims=[(CON, "expe:CorporateAndEliminationsMember")])]
    fs = [fact(R, "fy", 14733), fact(R, "b2c", 9474), fact(R, "b2b", 4842), fact(R, "tv", 417), fact(R, "tvo", 622), fact(R, "corp", 0), fact(R, "el", -205), fact(R, "ce", -205)]
    out = S.build_output("EXPE", 1, [_one_filing(cs, fs)], "1231")
    a = _table(out, "business_segments", "RevenueFromContractWithCustomerExcludingAssessedTax", "annual")
    assert [r["values"][0] for r in a["rows"]] == [9474, 4842, 417] and a["total"]["values"] == [14733] and a["ties_to_total"] is True, a["rows"]
    assert any("merged into" in w and "CorporateAndEliminations" in w for w in out["warnings"]), out["warnings"]
    assert any("CorporateAndEliminations" in w and "dropped" in w for w in out["warnings"]), out["warnings"]


def test_matrix_cells_are_ignored_huntington_product_table():
    """HBAN 10-K (0000049196-26-000015) FY2023 Capital Market Fees: 16 (x Consumer & Business Banking,
    OperatingSegments) + 118 (x Commercial Banking, OperatingSegments) - 2 (x CorporateNonSegment) = 132 bare.
    Only the bare 132 is a row; the -2 is a cell of the product-by-segment matrix. A genuine
    consolidation-only row stays and the table ties."""
    PRD = "srt:ProductOrServiceAxis"
    cs = [ctx("fy", "2023-01-01", "2023-12-31"),
          ctx("cm", "2023-01-01", "2023-12-31", dims=[(PRD, "hban:CapitalMarketFeesMember")]),
          ctx("cm1", "2023-01-01", "2023-12-31", dims=[(PRD, "hban:CapitalMarketFeesMember"), (SEG, "hban:ConsumerAndBusinessBankingMember"), (CON, "gaap:OperatingSegmentsMember")]),
          ctx("cm2", "2023-01-01", "2023-12-31", dims=[(PRD, "hban:CapitalMarketFeesMember"), (SEG, "hban:CommercialBankingMember"), (CON, "gaap:OperatingSegmentsMember")]),
          ctx("cmc", "2023-01-01", "2023-12-31", dims=[(PRD, "hban:CapitalMarketFeesMember"), (CON, "gaap:CorporateNonSegmentMember")]),
          ctx("tr", "2023-01-01", "2023-12-31", dims=[(PRD, "hban:TrustAndInvestmentManagementMember")]),
          ctx("trc", "2023-01-01", "2023-12-31", dims=[(PRD, "hban:TrustAndInvestmentManagementMember"), (CON, "gaap:CorporateNonSegmentMember")])]
    R = "gaap:RevenueFromContractWithCustomerExcludingAssessedTax"
    fs = [fact(R, "fy", 300), fact(R, "cm", 132), fact(R, "cm1", 16), fact(R, "cm2", 118), fact(R, "cmc", -2), fact(R, "tr", 168), fact(R, "trc", 3)]
    out = S.build_output("HBAN", 1, [_one_filing(cs, fs, period="2023-12-31")], "1231")
    t = _table(out, "product", "RevenueFromContractWithCustomerExcludingAssessedTax", "annual")
    assert [(r["member"], r["values"][0]) for r in t["rows"]] == [("hban:TrustAndInvestmentManagementMember", 168), ("hban:CapitalMarketFeesMember", 132)], t["rows"]
    assert t["ties_to_total"] is True and sum(r["share_of_total"][0] for r in t["rows"]) == 1.0


def test_subtotal_and_duplicate_rows_are_dropped():
    """Centene (product axis): cnc:TotalPremiumAndServiceMember 44,375 = HealthCarePremium 43,582 + Service 793,
    a sibling in the definition linkbase -> dropped by value (and by name). Alnylam-style nesting from the
    linkbase: ProductMember -> TTR -> Amvuttra / Onpattro, Rare -> Givlaari: every ancestor of a present row
    goes, whatever the numbers. Axon: one segment under two member names with identical numbers -> one row.
    Martin Marietta: mlm:ReportableSegmentsMember by name."""
    PRD = "srt:ProductOrServiceAxis"
    R = "gaap:RevenueFromContractWithCustomerExcludingAssessedTax"
    cs, fs = [ctx("fy", "2025-01-01", "2025-12-31"), ctx("fyp", "2024-01-01", "2024-12-31")], [fact(R, "fy", 44375), fact(R, "fyp", 40000)]
    for cid, m, v, vp in [("tot", "cnc:TotalPremiumAndServiceMember", 44375, 40000), ("hp", "gaap:HealthCarePremiumMember", 43582, 39300), ("sv", "gaap:ServiceMember", 793, 700)]:
        cs += [ctx(cid, "2025-01-01", "2025-12-31", dims=[(PRD, m)]), ctx(cid + "p", "2024-01-01", "2024-12-31", dims=[(PRD, m)])]
        fs += [fact(R, cid, v), fact(R, cid + "p", vp)]
    out = S.build_output("CNC", 1, [_one_filing(cs, fs)], "1231")
    t = _table(out, "product", "RevenueFromContractWithCustomerExcludingAssessedTax", "annual")
    assert [r["member"] for r in t["rows"]] == ["us-gaap:HealthCarePremiumMember", "us-gaap:ServiceMember"] and t["ties_to_total"] is True, t["rows"]
    assert any("TotalPremiumAndService" in w and "dropped" in w for w in out["warnings"]), out["warnings"]
    # the value rule alone (no telltale name, no hierarchy): a row equal to the sum of two others in every column
    cs, fs = [ctx("fy", "2025-01-01", "2025-12-31"), ctx("fyp", "2024-01-01", "2024-12-31")], [fact(R, "fy", 4012), fact(R, "fyp", 3800)]
    for cid, m, v, vp in [("eu", "srt:EuropeMember", 4012, 3800), ("ex", "ctsh:EuropeexcludingUnitedKingdomMember", 2090, 2000), ("gb", "country:GB", 1922, 1800)]:
        cs += [ctx(cid, "2025-01-01", "2025-12-31", dims=[(GEO, m)]), ctx(cid + "p", "2024-01-01", "2024-12-31", dims=[(GEO, m)])]
        fs += [fact(R, cid, v), fact(R, cid + "p", vp)]
    out = S.build_output("CTSH", 1, [_one_filing(cs, fs)], "1231")
    t = _table(out, "geography", "RevenueFromContractWithCustomerExcludingAssessedTax", "annual")
    assert [r["member"] for r in t["rows"]] == ["ctsh:EuropeexcludingUnitedKingdomMember", "country:GB"], t["rows"]
    assert any("srt:EuropeMember" in w and "equal the sum of" in w for w in out["warnings"]), out["warnings"]
    # a single-column coincidence is not enough for the value rule (two non-zero matched columns are required)
    cs, fs = [ctx("fy", "2025-01-01", "2025-12-31")], [fact(R, "fy", 300)]
    for cid, m, v in [("x", "toy:XMember", 100), ("y", "toy:YMember", 60), ("z", "toy:ZMember", 40), ("w", "toy:WMember", 100)]:
        cs.append(ctx(cid, "2025-01-01", "2025-12-31", dims=[(GEO, m)])); fs.append(fact(R, cid, v))
    out = S.build_output("COIN", 1, [_one_filing(cs, fs)], "1231")
    assert len(_table(out, "geography", "RevenueFromContractWithCustomerExcludingAssessedTax", "annual")["rows"]) == 4
    # hierarchy: ancestors of present rows go, nested
    hier = {"us-gaap_ProductMember": {"alny_TTRMember", "alny_RareMember"}, "alny_TTRMember": {"alny_AmvuttraMember", "alny_ONPATTROMember"}, "alny_RareMember": {"alny_GIVLAARIMember"}}
    cs, fs = [ctx("fy", "2025-01-01", "2025-12-31"), ctx("fyp", "2024-01-01", "2024-12-31")], [fact(R, "fy", 3400), fact(R, "fyp", 2500)]
    rows_in = [("pr", "gaap:ProductMember", 2986, 2200), ("ttr", "alny:TTRMember", 2486, 1800), ("am", "alny:AmvuttraMember", 2313, 1500), ("on", "alny:ONPATTROMember", 173, 300),
               ("rare", "alny:RareMember", 500, 400), ("giv", "alny:GIVLAARIMember", 500, 400), ("col", "alny:CollaborationMember", 414, 300)]
    for cid, m, v, vp in rows_in:
        cs += [ctx(cid, "2025-01-01", "2025-12-31", dims=[(PRD, m)]), ctx(cid + "p", "2024-01-01", "2024-12-31", dims=[(PRD, m)])]
        fs += [fact(R, cid, v), fact(R, cid + "p", vp)]
    out = S.build_output("ALNY", 1, [_one_filing(cs, fs, hierarchy=hier)], "1231")
    t = _table(out, "product", "RevenueFromContractWithCustomerExcludingAssessedTax", "annual")
    assert [r["member"] for r in t["rows"]] == ["alny:AmvuttraMember", "alny:GIVLAARIMember", "alny:CollaborationMember", "alny:ONPATTROMember"], [r["member"] for r in t["rows"]]
    assert t["ties_to_total"] is True and any("parent of" in w and "ProductMember" in w for w in out["warnings"]), out["warnings"]
    assert S.descendants("us-gaap_ProductMember", hier) == {"alny_TTRMember", "alny_RareMember", "alny_AmvuttraMember", "alny_ONPATTROMember", "alny_GIVLAARIMember"}
    # Axon: the same segment tagged under two names with identical numbers (a renamed segment, and the standard
    # us-gaap:ServiceMember next to the filer's own member: the filer's member is kept); Martin Marietta's
    # ReportableSegments by name
    cs, fs = [ctx("fy", "2025-01-01", "2025-12-31"), ctx("fyp", "2024-01-01", "2024-12-31")], [fact("gaap:Revenues", "fy", 600), fact("gaap:Revenues", "fyp", 500)]
    for cid, m, v, vp in [("s0", "gaap:ServiceMember", 398, 320), ("s1", "axon:SoftwareAndSensorsSegmentMember", 398, 320), ("s2", "axon:SoftwareAndServicesSegmentMember", 398, 320),
                          ("cd", "axon:ConnectedDevicesMember", 202, 180), ("rs", "mlm:ReportableSegmentsMember", 600, 500)]:
        cs += [ctx(cid, "2025-01-01", "2025-12-31", dims=[(SEG, m)]), ctx(cid + "p", "2024-01-01", "2024-12-31", dims=[(SEG, m)])]
        fs += [fact("gaap:Revenues", cid, v), fact("gaap:Revenues", cid + "p", vp)]
    out = S.build_output("AXON", 1, [_one_filing(cs, fs)], "1231")
    t = _table(out, "business_segments", "Revenues", "annual")
    assert [r["member"] for r in t["rows"]] == ["axon:SoftwareAndSensorsSegmentMember", "axon:ConnectedDevicesMember"] and t["ties_to_total"] is True, t["rows"]
    assert sum(1 for w in out["warnings"] if "same numbers as 'Software And Sensors'" in w) == 2 and any("ReportableSegments" in w and "subtotal" in w for w in out["warnings"]), out["warnings"]
    # two segments whose numbers coincide in a single column are two segments
    cs, fs = [ctx("fy", "2025-01-01", "2025-12-31")], [fact("gaap:Revenues", "fy", 500)]
    for cid, m, v in [("p", "toy:PMember", 250), ("q", "toy:QMember", 250)]:
        cs.append(ctx(cid, "2025-01-01", "2025-12-31", dims=[(SEG, m)])); fs.append(fact("gaap:Revenues", cid, v))
    assert len(_table(S.build_output("TOY", 1, [_one_filing(cs, fs)], "1231"), "business_segments", "Revenues", "annual")["rows"]) == 2


def test_two_classifications_on_one_axis_and_total_members():
    """HP's geography axis (10-K 0000047217-25-000xxx shape): Americas 23,545 + EMEA 18,596 + Asia Pacific
    13,154 = 55,295 = revenue, and US 19,212 + Non-US 36,083 = 55,295 too: two complete splits, 200% stacked.
    The larger split is kept. ResMed's rmd:GlobalMember equals the total in every column next to two regions
    that cover 88%: dropped as a total. A partial split that does not sum exactly is left alone (flagged)."""
    R = "gaap:Revenues"
    cs, fs = [ctx("fy", "2025-01-01", "2025-12-31"), ctx("fyp", "2024-01-01", "2024-12-31")], [fact(R, "fy", 55295), fact(R, "fyp", 53559)]
    rows_in = [("am", "srt:AmericasMember", 23545, 23251), ("em", "gaap:EMEAMember", 18596, 18044), ("ap", "srt:AsiaPacificMember", 13154, 12264),
               ("us", "country:US", 19212, 18790), ("nus", "gaap:NonUsMember", 36083, 34769)]
    for cid, m, v, vp in rows_in:
        cs += [ctx(cid, "2025-01-01", "2025-12-31", dims=[(GEO, m)]), ctx(cid + "p", "2024-01-01", "2024-12-31", dims=[(GEO, m)])]
        fs += [fact(R, cid, v), fact(R, cid + "p", vp)]
    out = S.build_output("HPQ", 1, [_one_filing(cs, fs)], "1231")
    t = _table(out, "geography", "Revenues", "annual")
    assert [r["member"] for r in t["rows"]] == ["srt:AmericasMember", "us-gaap:EMEAMember", "srt:AsiaPacificMember"] and t["ties_to_total"] is True, t["rows"]
    assert sum(1 for w in out["warnings"] if "second classification" in w) == 2, out["warnings"]
    cs, fs = [ctx("fy", "2025-01-01", "2025-12-31"), ctx("fyp", "2024-01-01", "2024-12-31")], [fact(R, "fy", 1431), fact(R, "fyp", 1292)]
    for cid, m, v, vp in [("g", "rmd:GlobalMember", 1431, 1292), ("a", "rmd:UsCanadaAndLatinAmericaMember", 819, 749), ("b", "rmd:CombinedEuropeAsiaAndOtherMarketsMember", 442, 381)]:
        cs += [ctx(cid, "2025-01-01", "2025-12-31", dims=[(GEO, m)]), ctx(cid + "p", "2024-01-01", "2024-12-31", dims=[(GEO, m)])]
        fs += [fact(R, cid, v), fact(R, cid + "p", vp)]
    out = S.build_output("RMD", 1, [_one_filing(cs, fs)], "1231")
    t = _table(out, "geography", "Revenues", "annual")
    assert [r["member"] for r in t["rows"]] == ["rmd:UsCanadaAndLatinAmericaMember", "rmd:CombinedEuropeAsiaAndOtherMarketsMember"] and t["ties_to_total"] is False, t["rows"]
    assert any("GlobalMember" in w and "equal the consolidated total" in w for w in out["warnings"]), out["warnings"]
    # a total that matches in one column only is not a total member; nothing is dropped
    fs = [fact(R, "fy", 1431), fact(R, "fyp", 1300)] + fs[2:]
    out = S.build_output("RMD", 1, [_one_filing(cs, fs)], "1231")
    assert len(_table(out, "geography", "Revenues", "annual")["rows"]) == 3


def test_wide_tables_keep_eleven_rows_plus_an_other_aggregate():
    """Zoetis tags 20+ countries on the geography axis: the 11 largest rows are shown and the rest are summed
    into one 'Other' row (plain arithmetic on filed values), so the shown rows still tie to the total."""
    R = "gaap:Revenues"
    cs, fs = [ctx("fy", "2025-01-01", "2025-12-31"), ctx("fyp", "2024-01-01", "2024-12-31")], []
    n, total = 15, 0
    for k in range(n):
        v = 1000 - 50 * k
        total += v
        cs += [ctx(f"g{k}", "2025-01-01", "2025-12-31", dims=[(GEO, f"toy:Geo{k}Member")]), ctx(f"g{k}p", "2024-01-01", "2024-12-31", dims=[(GEO, f"toy:Geo{k}Member")])]
        fs += [fact(R, f"g{k}", v), fact(R, f"g{k}p", v - 1)]
    fs += [fact(R, "fy", total), fact(R, "fyp", total - n)]
    out = S.build_output("ZTS", 1, [_one_filing(cs, fs)], "1231")
    t = _table(out, "geography", "Revenues", "annual")
    assert len(t["rows"]) == S.MAX_ROWS and t["rows"][-1]["member"] == "_other" and t["rows"][-1]["label"] == "Other (4 smaller rows)", t["rows"][-1]
    assert t["rows"][-1]["values"] == [sum(1000 - 50 * k - 1 for k in range(11, 15)), sum(1000 - 50 * k for k in range(11, 15))]
    assert sum(r["values"][1] for r in t["rows"]) == total and t["ties_to_total"] is True
    assert any("summed into one 'Other' row" in w for w in out["warnings"]), out["warnings"]


def test_leftover_tables_dropped_and_mismatches_flagged():
    """Con Edison style: business_segments/Revenues rows 4 / 0 / -2 against a 16,918 consolidated total (the
    real segments carry an extra LegalEntityAxis and are ignored) -> the table is dropped with a warning.
    Rows summing 10% away from the total stay but carry ties_to_total: false. Profit concepts never drop."""
    cs = [ctx("fy", "2025-01-01", "2025-12-31"), ctx("a", "2025-01-01", "2025-12-31", dims=[(SEG, "ed:CleanEnergyMember")]),
          ctx("b", "2025-01-01", "2025-12-31", dims=[(SEG, "ed:OtherMember")]), ctx("c", "2025-01-01", "2025-12-31", dims=[(SEG, "ed:ParentMember")])]
    fs = [fact("gaap:Revenues", "fy", 16918), fact("gaap:Revenues", "a", 4), fact("gaap:Revenues", "b", 0), fact("gaap:Revenues", "c", -2),
          fact("gaap:OperatingIncomeLoss", "fy", -100), fact("gaap:OperatingIncomeLoss", "a", 300), fact("gaap:OperatingIncomeLoss", "c", 200)]
    out = S.build_output("ED", 1, [_one_filing(cs, fs)], "1231")
    assert _table(out, "business_segments", "Revenues", "annual") is None and any("not a breakdown" in w for w in out["warnings"]), out["warnings"]
    oi = _table(out, "business_segments", "OperatingIncomeLoss", "annual")
    assert oi is not None and oi["ties_to_total"] is False, "profit tables are flagged, never dropped"
    # a small legitimate reconciling row is never dropped by the tie rule: 600 + 300 + 3 = 903 ties exactly, and without
    # the 3 the rows are 0.3% off, which is not a tie
    cs = [ctx("fy", "2025-01-01", "2025-12-31"), ctx("a", "2025-01-01", "2025-12-31", dims=[(SEG, A)]), ctx("b", "2025-01-01", "2025-12-31", dims=[(SEG, B)]),
          ctx("c", "2025-01-01", "2025-12-31", dims=[(CON, "gaap:CorporateNonSegmentMember")])]
    fs = [fact("gaap:Revenues", "fy", 903), fact("gaap:Revenues", "a", 600), fact("gaap:Revenues", "b", 300), fact("gaap:Revenues", "c", 3)]
    t = _table(S.build_output("TOY", 1, [_one_filing(cs, fs)], "1231"), "business_segments", "Revenues", "annual")
    assert len(t["rows"]) == 3 and t["ties_to_total"] is True
    # a partial breakdown (Martin Marietta tags only Aggregates and Service on the product axis, a third of revenue) stays, flagged
    fs = [fact("gaap:Revenues", "fy", 3000), fact("gaap:Revenues", "a", 600), fact("gaap:Revenues", "b", 300)]
    t = _table(S.build_output("TOY", 1, [_one_filing(cs, fs)], "1231"), "business_segments", "Revenues", "annual")
    assert t is not None and t["ties_to_total"] is False and _row(t, A)["share_of_total"] == [0.2]
    cs = [ctx("fy", "2025-01-01", "2025-12-31"), ctx("a", "2025-01-01", "2025-12-31", dims=[(SEG, A)]), ctx("b", "2025-01-01", "2025-12-31", dims=[(SEG, B)])]
    fs = [fact("gaap:Revenues", "fy", 1000), fact("gaap:Revenues", "a", 600), fact("gaap:Revenues", "b", 300)]
    out = S.build_output("TOY", 1, [_one_filing(cs, fs)], "1231")
    t = _table(out, "business_segments", "Revenues", "annual")
    assert t["ties_to_total"] is False and t["total"]["values"] == [1000] and any("90.0%" in w and "ties_to_total: false" in w for w in out["warnings"]), out["warnings"]
    fs = [fact("gaap:Revenues", "a", 600), fact("gaap:Revenues", "b", 300)]
    out = S.build_output("TOY", 1, [_one_filing(cs, fs)], "1231")
    assert _table(out, "business_segments", "Revenues", "annual")["ties_to_total"] is None, "no consolidated fact: nothing to tie to"


def test_instants_belong_to_both_tables_and_zero_rows_drop():
    """The 10-Q restates the FY-end balance sheet: that instant must stay in the annual table (from the
    10-K) and also appear in the quarterly one. Rows that are all zero (or empty) are dropped."""
    k = S.parse_instance(tenk_xml())
    cs = [ctx("i25", instant="2025-12-31"), ctx("i25A", instant="2025-12-31", dims=[(SEG, A)]), ctx("i25B", instant="2025-12-31", dims=[(SEG, B)]),
          ctx("i26", instant="2026-06-30"), ctx("i26A", instant="2026-06-30", dims=[(SEG, A)]), ctx("i26B", instant="2026-06-30", dims=[(SEG, B)]),
          ctx("q", "2026-04-01", "2026-06-30"), ctx("qA", "2026-04-01", "2026-06-30", dims=[(SEG, A)]), ctx("qB", "2026-04-01", "2026-06-30", dims=[(SEG, B)]),
          ctx("qZ", "2026-04-01", "2026-06-30", dims=[(SEG, "toy:ZeroMember")])]
    fs = [fact("dei:DocumentFiscalYearFocus", "q", "2026"), fact("dei:DocumentFiscalPeriodFocus", "q", "Q2"), fact("dei:CurrentFiscalYearEndDate", "q", "--12-31"), fact("dei:DocumentPeriodEndDate", "q", "2026-06-30"),
          fact("gaap:Assets", "i25", 5000), fact("gaap:Assets", "i25A", 3000), fact("gaap:Assets", "i25B", 1500),
          fact("gaap:Assets", "i26", 5600), fact("gaap:Assets", "i26A", 3300), fact("gaap:Assets", "i26B", 1700),
          fact("gaap:Revenues", "q", 300), fact("gaap:Revenues", "qA", 200), fact("gaap:Revenues", "qB", 100), fact("gaap:Revenues", "qZ", 0)]
    q = S.parse_instance(HEAD + UNITS + "".join(cs) + "".join(fs) + "</xbrl>")
    out = S.build_output("TOY", 1, [
        {"form": "10-K", "accession": "k", "filed": "2026-02-20", "period": "2025-12-31", "instance_url": "u", "instance": k, "labels": {}},
        {"form": "10-Q", "accession": "q", "filed": "2026-08-01", "period": "2026-06-30", "instance_url": "u", "instance": q, "labels": {}}], "1231")
    annual = _table(out, "business_segments", "Assets", "annual")
    assert annual["periods"] == ["2024-12-31", "2025-12-31"] and annual["period_labels"] == ["FY2024 end", "FY2025 end"], annual["periods"]
    quarterly = _table(out, "business_segments", "Assets", "quarterly")
    assert quarterly["periods"] == ["2025-12-31", "2026-06-30"] and quarterly["period_labels"] == ["FY2025 end", "Q2 FY2026"], quarterly["period_labels"]
    assert _row(quarterly, A)["values"] == [3000, 3300] and quarterly["total"]["values"] == [5000, 5600]
    rev = _table(out, "business_segments", "Revenues", "quarterly")
    assert [r["member"] for r in rev["rows"]] == [A, B], "the all-zero member is dropped"


def test_duplicate_reconciling_rows_collapse_to_the_filers_member():
    """A reconciling line tagged on the segment axis under the filer's own member AND bare under a standard
    consolidation member with identical numbers is one row, the filer's member. A standard row whose numbers
    coincide with a non-reconciling row, or with another standard row, is never collapsed."""
    cs = [ctx("fy", "2025-01-01", "2025-12-31"), ctx("fyA", "2025-01-01", "2025-12-31", dims=[(SEG, A)]), ctx("fyB", "2025-01-01", "2025-12-31", dims=[(SEG, B)]),
          ctx("fyC", "2025-01-01", "2025-12-31", dims=[(SEG, "toy:CorporateAndEliminationsMember")]),
          ctx("fyE", "2025-01-01", "2025-12-31", dims=[(CON, "gaap:IntersegmentEliminationMember")]),
          ctx("fyO", "2025-01-01", "2025-12-31", dims=[(CON, "gaap:MaterialReconcilingItemsMember")]),
          ctx("fyX", "2025-01-01", "2025-12-31", dims=[(CON, "toy:CorporateAndOtherMember")])]
    fs = [fact("gaap:Revenues", "fy", 943), fact("gaap:Revenues", "fyA", 600), fact("gaap:Revenues", "fyB", 400),
          fact("gaap:Revenues", "fyC", -50), fact("gaap:Revenues", "fyE", -50), fact("gaap:Revenues", "fyO", -7), fact("gaap:Revenues", "fyX", -7)]
    inst = S.parse_instance(HEAD + UNITS + "".join(cs) + "".join(fs) + "</xbrl>")
    out = S.build_output("TOY", 1, [{"form": "10-K", "accession": "k", "filed": "2026-02-20", "period": "2025-12-31", "instance_url": "u", "instance": inst, "labels": {}}], "1231")
    t = _table(out, "business_segments", "Revenues", "annual")
    # reconciling rows come last, ordered by latest value descending (-7 before -50); the bare us-gaap -50 copy is
    # gone (the segment-axis member wins) and so is the us-gaap -7 copy (the filer's own consolidation-axis member wins)
    assert [r["member"] for r in t["rows"]] == [A, B, "toy:CorporateAndOtherMember", "toy:CorporateAndEliminationsMember"], [r["member"] for r in t["rows"]]
    assert t["ties_to_total"] is True and sum(1 for w in out["warnings"] if "merged into" in w) == 2, out["warnings"]
    assert S.is_consolidation_only(inst["contexts"]["fyE"]) and not S.is_consolidation_only(inst["contexts"]["fyC"]) and not S.is_consolidation_only(inst["contexts"]["fy"])
    # two standard reconciling rows with equal values (e.g. intersegment revenue +51 and an elimination -51 do not
    # coincide; but IntersegmentElimination and MaterialReconcilingItems both -7 do) are two lines
    r = lambda v: {"member": v[0], "label": v[0], "_vals": [{"value": v[1]}], "_recon": True, "_consol_only": True}  # noqa: E731
    rows = [r(("us-gaap:IntersegmentEliminationMember", -7)), r(("us-gaap:MaterialReconcilingItemsMember", -7))]
    assert len(S.dedupe_reconciling(rows)) == 2
    seg = {"member": A, "label": "A", "_vals": [{"value": -7}], "_recon": False, "_consol_only": False}
    assert len(S.dedupe_reconciling(rows + [seg])) == 3, "never collapsed into a non-reconciling row"


# ---------------- linkbases (definition + schema-embedded) ----------------
XSD = """<?xml version="1.0" encoding="utf-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:link="http://www.xbrl.org/2003/linkbase" xmlns:xlink="http://www.w3.org/1999/xlink"
  xmlns:xbrli="http://www.xbrl.org/2003/instance" targetNamespace="http://www.toy.com/20251231">
 <xs:annotation><xs:appinfo>
  <link:linkbase>
   <link:labelLink xlink:type="extended" xlink:role="http://www.xbrl.org/2003/role/link">
    <link:loc xlink:type="locator" xlink:label="loc_1" xlink:href="#toy_AlphaSegmentMember"/>
    <link:label xlink:type="resource" xlink:label="lab_1" xlink:role="http://www.xbrl.org/2003/role/label" xml:lang="en-US">Alpha From Schema [Member]</link:label>
    <link:labelArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/concept-label" xlink:from="loc_1" xlink:to="lab_1"/>
   </link:labelLink>
   <link:definitionLink xlink:type="extended" xlink:role="http://www.toy.com/role/Segments">
    <link:loc xlink:type="locator" xlink:label="loc_dom" xlink:href="https://xbrl.fasb.org/us-gaap/2025/elts/us-gaap-2025.xsd#us-gaap_SegmentDomain"/>
    <link:loc xlink:type="locator" xlink:label="loc_a" xlink:href="#toy_AlphaSegmentMember"/>
    <link:loc xlink:type="locator" xlink:label="loc_a1" xlink:href="toy-20251231.xsd#toy_AlphaWestMember"/>
    <link:definitionArc xlink:type="arc" xlink:arcrole="http://xbrl.org/int/dim/arcrole/domain-member" xlink:from="loc_dom" xlink:to="loc_a"/>
    <link:definitionArc xlink:type="arc" xlink:arcrole="http://xbrl.org/int/dim/arcrole/domain-member" xlink:from="loc_a" xlink:to="loc_a1"/>
    <link:definitionArc xlink:type="arc" xlink:arcrole="http://xbrl.org/int/dim/arcrole/hypercube-dimension" xlink:from="loc_dom" xlink:to="loc_a1"/>
   </link:definitionLink>
   <link:definitionLink xlink:type="extended" xlink:role="http://www.toy.com/role/Other">
    <link:loc xlink:type="locator" xlink:label="loc_a" xlink:href="#toy_UnrelatedMember"/>
    <link:loc xlink:type="locator" xlink:label="loc_b" xlink:href="#toy_UnrelatedChildMember"/>
    <link:definitionArc xlink:type="arc" xlink:arcrole="http://xbrl.org/int/dim/arcrole/domain-member" xlink:from="loc_a" xlink:to="loc_b"/>
   </link:definitionLink>
  </link:linkbase>
 </xs:appinfo></xs:annotation>
 <xs:element id="toy_AlphaSegmentMember" name="AlphaSegmentMember" type="xbrli:stringItemType" abstract="true"/>
</xs:schema>"""


def test_parse_definitions_and_schema_embedded_linkbases():
    h = S.parse_definitions(XSD)
    assert h == {"us-gaap_SegmentDomain": {"toy_AlphaSegmentMember"}, "toy_AlphaSegmentMember": {"toy_AlphaWestMember"}, "toy_UnrelatedMember": {"toy_UnrelatedChildMember"}}, h
    assert S.descendants("us-gaap_SegmentDomain", h) == {"toy_AlphaSegmentMember", "toy_AlphaWestMember"}, "locators resolve per extended link (loc_a means different things in each)"
    assert S.parse_labels(XSD) == {"toy_AlphaSegmentMember": "Alpha From Schema [Member]"}
    assert S.parse_definitions(LAB) == {} and S.parse_definitions(tenk_xml()) == {}
    # a DFIN-style folder: only the schema and the instance exist; labels and hierarchy come from the .xsd
    folder, base = "https://www.sec.gov/Archives/edgar/data/1/000000000126000001", "toy-20251231"
    served = {f"{folder}/{base}.xsd": XSD.encode()}
    calls = []
    real = S.fetch

    def fake(url, timeout=S.TIMEOUT):
        calls.append(url)
        if url in served:
            return served[url]
        raise S.NotFound(url)
    S.fetch = fake
    try:
        w = []
        filing = {"form": "10-Q", "accession": "0000000001-26-000001"}
        labels, hier = S.fetch_linkbases(base, folder, lambda: ["FilingSummary.xml", f"{base}.xsd", f"{base}_htm.xml"], w, filing)
        assert labels == {"toy_AlphaSegmentMember": "Alpha From Schema [Member]"} and hier["toy_AlphaSegmentMember"] == {"toy_AlphaWestMember"} and w == [], (labels, w)
        assert calls == [f"{folder}/{base}_lab.xml", f"{folder}/{base}_def.xml", f"{folder}/{base}.xsd"], calls
        # separate linkbases win when they exist; the schema is not fetched
        served[f"{folder}/{base}_lab.xml"] = LAB.encode(); served[f"{folder}/{base}_def.xml"] = XSD.encode(); calls.clear()
        labels, hier = S.fetch_linkbases(base, folder, lambda: [f"{base}_lab.xml", f"{base}_def.xml", f"{base}.xsd"], w, filing)
        assert labels["toy_AlphaSegmentMember"] == "Alpha Platform [Member]" and hier and not any(c.endswith(".xsd") for c in calls)
        # nothing at all: the de-camel warning stays
        served.clear(); w.clear()
        assert S.fetch_linkbases(base, folder, lambda: [], w, filing) == ({}, {}) and any("no label linkbase found" in x for x in w), w
    finally:
        S.fetch = real


def test_all_skip_predicate_retries_degraded_outputs():
    """--all skips a folder only when its segments.json lists EDGAR's latest filings AND read them all."""
    sub = {"fiscalYearEnd": "1231", "filings": {"recent": {"form": ["10-Q", "10-K"], "accessionNumber": ["a2", "a1"], "filingDate": ["2026-08-01", "2026-02-20"],
                                                           "reportDate": ["2026-06-30", "2025-12-31"], "primaryDocument": ["q.htm", "k.htm"]}}}
    good = {"filings": [{"accession": "a1", "instance_url": "u"}, {"accession": "a2", "instance_url": "u"}], "warnings": ["10-K a1: no label linkbase found; member names de-camel-cased"]}
    assert S.up_to_date(good, sub) and S.is_complete(good)
    assert not S.up_to_date({"filings": [{"accession": "a1", "instance_url": "u"}], "warnings": []}, sub), "a new filing appeared"
    timeout = {"filings": [{"accession": "a1", "instance_url": None}, {"accession": "a2", "instance_url": None}], "warnings": ["10-K a1: TimeoutError: timed out"]}
    assert not S.is_complete(timeout) and not S.up_to_date(timeout, sub)
    http = {"filings": [{"accession": "a1", "instance_url": "u"}, {"accession": "a2", "instance_url": "u"}], "warnings": ["10-Q a2: index.json unreadable (HTTP Error 503)"]}
    assert not S.up_to_date(http, sub)
    noinst = {"filings": [{"accession": "a1", "instance_url": "u"}, {"accession": "a2", "instance_url": None}], "warnings": ["10-Q a2 (2026-06-30): no XBRL instance document found"]}
    assert not S.up_to_date(noinst, sub)
    assert S.up_to_date({"complete": True, "filings": [{"accession": "a1"}, {"accession": "a2"}], "warnings": ["10-K a1: TimeoutError"]}, sub), "an explicit complete flag is authoritative"
    assert not S.up_to_date({"complete": False, "filings": [{"accession": "a1", "instance_url": "u"}, {"accession": "a2", "instance_url": "u"}], "warnings": []}, sub)
    assert not S.up_to_date({"filings": "garbage"}, sub)
    # build_output records the flag: a filing without an instance, or an exception warning, makes the payload incomplete
    out = S.build_output("TOY", 1, _filings(), "1231")
    assert out["complete"] is True
    out = S.build_output("NONE", 3, [{"form": "10-K", "accession": "y", "filed": "2026-01-01", "period": "2025-12-31", "instance_url": None, "instance": None, "labels": {}}])
    assert out["complete"] is False
    out = S.build_output("TOY", 1, _filings(), "1231", warnings=["10-Q x: URLError: <urlopen error timed out>"])
    assert out["complete"] is False


def test_select_filings_and_instance_naming():
    sub = {"fiscalYearEnd": "0131", "filings": {"recent": {
        "form": ["8-K", "10-Q", "10-Q/A", "10-Q", "10-K/A", "10-K", "10-Q", "10-K"],
        "accessionNumber": ["a0", "a1", "a2", "a3", "a4", "a5", "a6", "a7"],
        "filingDate": ["2026-09-20", "2026-09-18", "2026-07-01", "2026-06-26", "2026-04-02", "2026-03-31", "2025-12-12", "2025-04-01"],
        "reportDate": ["2026-09-20", "2026-08-15", "2026-05-23", "2026-05-23", "2026-01-31", "2026-01-31", "2025-11-08", "2025-02-01"],
        "primaryDocument": ["x.htm", "kr-20260815x10q.htm", "a.htm", "kr-20260523x10q.htm", "b.htm", "kr-20260131x10k.htm", "c.htm", "d.htm"]}}}
    filings, fye = select_filings_wrapper(sub)
    assert fye == "0131" and [f["accession"] for f in filings] == ["a5", "a3", "a1"], "latest 10-K + latest two 10-Qs, amendments skipped, oldest first"
    folder, base = S.instance_candidates(56873, filings[0])
    assert folder == "https://www.sec.gov/Archives/edgar/data/56873/a5" and base == "kr-20260131x10k"
    assert S._is_instance_name("kr-20260131x10k_htm.xml") and not S._is_instance_name("kr-20260131_lab.xml") and not S._is_instance_name("FilingSummary.xml")
    assert S.latest_accessions(sub) == ["a1", "a3", "a5"]


def select_filings_wrapper(sub):
    return S.select_filings(sub)


if __name__ == "__main__":
    fails = 0
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn(); print(f"PASS {name}")
            except AssertionError as e:
                fails += 1; print(f"FAIL {name}: {e}")
            except Exception as e:
                fails += 1; print(f"ERROR {name}: {type(e).__name__}: {e}")
    sys.exit(1 if fails else 0)
