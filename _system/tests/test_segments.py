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
fiscal-year / quarter naming anchored on dei facts (Kroger-style January year
end), and the table assembly: latest filing wins, Q4 derived as FY minus nine
months and flagged, share_of_total on the consolidated fact vs the sum of rows,
growth_yoy against the column one year earlier, row ordering with reconciling
rows last, foreign-currency facts dropped with a warning, and the
empty-tables-plus-warning path for a company with no dimensioned facts.
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
    assert S.classify_context(mixed) == ("row", "business_segments", A, "us-gaap:IntersegmentEliminationMember")
    other = {"dims": {"us-gaap:StatementBusinessSegmentsAxis": A, "us-gaap:StatementClassOfStockAxis": "us-gaap:CommonClassAMember"}, "typed": False}
    assert S.classify_context(other)[0] == "ignore"
    assert S.is_reconciling("us-gaap:CorporateNonSegmentMember", None) and S.is_reconciling(A, "us-gaap:IntersegmentEliminationMember")
    assert not S.is_reconciling(A, None) and S.is_reconciling("gfi:CorporateAndOtherDomain", None)


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
    parsed = [{"form": "10-K", "instance": {"dei": {}}}, {"form": "10-Q", "instance": S.parse_instance(tenq_xml())}]
    assert S.FiscalCalendar.from_filings(parsed).label("annual", "2025-12-31") == "FY2025", "anchor taken from the latest filing that has dei facts"
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
    a later filing still overwrites both."""
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
        assert _row(q, f"{B}|us-gaap:IntersegmentEliminationMember")["label"] == "Beta — Intersegment Elimination"
    later = {"form": "10-Q", "accession": "b", "filed": "2026-11-01", "period": "2026-09-30", "instance_url": "u", "instance": inst(150, 200, False), "labels": {}}
    first = {"form": "10-Q", "accession": "a", "filed": "2026-08-01", "period": "2026-06-30", "instance_url": "u", "instance": inst(145, 196, True), "labels": {}}
    out = S.build_output("TOY", 1, [first, later], "1231")
    assert _row(_table(out, "business_segments", "Revenues", "quarterly"), B)["values"] == [150], "later filing wins, then bare beats gross"


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
    """Expedia tags "Corporate & Eliminations" on the segment axis AND the bare IntersegmentEliminationMember
    with identical numbers; one row, the filer's own member, survives. Different numbers stay separate."""
    cs = [ctx("fy", "2025-01-01", "2025-12-31"), ctx("fyA", "2025-01-01", "2025-12-31", dims=[(SEG, A)]), ctx("fyB", "2025-01-01", "2025-12-31", dims=[(SEG, B)]),
          ctx("fyC", "2025-01-01", "2025-12-31", dims=[(SEG, "toy:CorporateAndEliminationsMember")]),
          ctx("fyE", "2025-01-01", "2025-12-31", dims=[(CON, "gaap:IntersegmentEliminationMember")]),
          ctx("fyO", "2025-01-01", "2025-12-31", dims=[(CON, "gaap:MaterialReconcilingItemsMember")]),
          ctx("fyX", "2025-01-01", "2025-12-31", dims=[(CON, "toy:CorporateAndOtherMember")])]
    fs = [fact("gaap:Revenues", "fy", 950), fact("gaap:Revenues", "fyA", 600), fact("gaap:Revenues", "fyB", 400),
          fact("gaap:Revenues", "fyC", -50), fact("gaap:Revenues", "fyE", -50), fact("gaap:Revenues", "fyO", -7), fact("gaap:Revenues", "fyX", -7)]
    inst = S.parse_instance(HEAD + UNITS + "".join(cs) + "".join(fs) + "</xbrl>")
    out = S.build_output("TOY", 1, [{"form": "10-K", "accession": "k", "filed": "2026-02-20", "period": "2025-12-31", "instance_url": "u", "instance": inst, "labels": {}}], "1231")
    t = _table(out, "business_segments", "Revenues", "annual")
    # reconciling rows come last, ordered by latest value descending (-7 before -50); the bare us-gaap -50 copy is
    # gone (the segment-axis member wins) and so is the us-gaap -7 copy (the filer's own consolidation-axis member wins)
    assert [r["member"] for r in t["rows"]] == [A, B, "toy:CorporateAndOtherMember", "toy:CorporateAndEliminationsMember"], [r["member"] for r in t["rows"]]
    assert S.is_consolidation_only(inst["contexts"]["fyE"]) and not S.is_consolidation_only(inst["contexts"]["fyC"]) and not S.is_consolidation_only(inst["contexts"]["fy"])


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
