#!/usr/bin/env python3
"""profile.py tests (v5.4). Run: python3 _system/tests/test_profile.py
(or python3 -m pytest _system/tests). No network, no writes: every case is a
pure function on an inline fixture.

1. Item 1 Business extractor: an inline 10-K HTML fixture with a table of
   contents ("Item 1. Business ... Item 1A." within 300 chars) and the real
   section later; the TOC occurrence is skipped, the prose is kept, the cut
   lands on a sentence boundary at <= 1,500 chars, and a document without the
   section returns None with a note. A short real section followed by Item 1A
   is still the real one. Kroger's "BUSINESS." stray period and Huntington's
   sub-headings (before and after the prose) are dropped. A TOC that labels
   its rows "Item 1(a)" (Halliburton) or indexes Item 1's sub-headings
   ("A. Overview", Carnival) is still the TOC: the real heading later wins.
   The 20-F fallback finds Item 4.B; an integrated-report 20-F (Gold Fields)
   rejects the cross-reference table and uses the bare "Overview" section
   that names the registrant.
2. Employees sentence extractor: positive ("As of December 31, 2025, we had
   approximately 1,900 full-time employees"), a decoy percentage sentence that
   must not win, a non-"we" subject, the year-average FTE form (basis
   "average ..." only with the word average; a point-in-time FTE count reads
   "full-time equivalent as of the stated date"), the multi-year 20-F sentence
   (JD: last number, last year), the integrated-report bullet with the
   prior-year comparative (double-escaped HTML), one-sentence evidence, a
   subsidiary's count losing to the registrant's, a per-country breakdown
   never being the total, a stray proper noun ("Hurricane Milton had 150
   workers") rejected, and negatives (no sentence at all; a number that is not
   a headcount; a bare count without a date) -> None, never a guess.
3. 8-K item mapping: codes -> plain descriptions; 9.01 listed but not
   described unless alone; unknown codes read "Item X.XX"; the filings feed
   keeps only the eight forms, newest first, at most 20, with primary-document
   URLs and amendment labelling.
4. The max-age skip rule: fresh + unchanged newest filing -> skip; a new
   filing, an old file, a missing/malformed file, or --force -> rebuild.
5. Street block assembly from the verified endpoint shapes (history oldest
   first with ISO dates, surprise_pct = (actual - consensus) / |consensus| *
   100 so a beat on a negative consensus is positive, momentum, next earnings
   date, PEG), partial failure (targetprice only), Nasdaq's placeholders (999
   means -> null, 0/0 EPS rows dropped, warnings), and the market block with
   Nasdaq's text dividend dates ("Sep 17, 2026" -> ISO).
6. first_filing: the earliest registration / listing form (APP's real
   sequence D, DRS, DRSLTR, S-1, 424B4 -> the S-1) unless a periodic report
   precedes it (Kroger -> the 1994 10-K405); paginated files fetched oldest
   first with an injected fetcher and stopped once a registration form is
   seen.
7. Helpers: num rejects NaN / Infinity / '1_000'; html_to_text keeps words
   split across inline tags whole; cover_address reads the filed
   dei:EntityAddress* tags and headquarters prefers them over submissions;
   write_atomic refuses NaN without leaving a file or a .tmp behind.
8. Review round: the description is a genuine prose run (M&T's
   cross-reference sheet, MetLife / Prudential / Hartford sub-section indexes,
   forward-looking and read-in-conjunction lead-ins skipped; "Items 1 and 2.
   Business and Properties" and one-line "Part I. Item 1. Business"
   headings; running page headers dropped; a first sentence broken across
   lines; a cross-reference-only 10-K -> None); headcounts are totals only
   (Baidu's total over its R&D subset, "the Company and its subsidiaries had",
   trailing "as of" evidence, Estee Lauder's descending years, breakdowns and
   lone locations -> None with the sentence in notes, PG&E's registrant +
   utility -> None, totals listed with parts kept, more phrasings); foreign
   district cities, all-caps and truncated cover cities; 1990s form
   spellings; build() with the network stubbed publishes
   employees_unresolved.
9. Review round 3: leading definitional / address / "We refer you to Item
   1A" sentences are skipped (Yum! Brands, Arch Capital, Old Dominion on one
   line) and never count toward min_prose (Con Edison's trailing definition;
   sub-headings met before the minimum are dropped); per-type / per-location
   splits with the noun repeated -> None (incl. onsemi's U+2011 hyphens),
   contractors / "worldwide" / "including" / "excluding" totals kept; the
   Human Capital count outranks later-dated counts and "people enrolled" /
   "persons serving as executive officers"; "Sept." dates, impossible dates
   -> None.
"""
import os, sys, json, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
SYS = os.path.dirname(HERE)
sys.path.insert(0, SYS)
import profile as P  # noqa: E402

FAILS = []


def check(cond, msg):
    if not cond:
        FAILS.append(msg)
        print("FAIL:", msg)


# ---------------------------------------------------------------------------
# 1. Item 1 extractor
TENK_HTML = """<html><head><title>10-K</title><style>p{margin:0}</style></head><body>
<div>UNITED STATES SECURITIES AND EXCHANGE COMMISSION</div>
<div><b>TABLE OF CONTENTS</b></div>
<table><tr><td>Part I</td><td></td></tr>
<tr><td>Item 1.</td><td>Business</td><td>2</td></tr>
<tr><td>Item 1A.</td><td>Risk Factors</td><td>8</td></tr>
<tr><td>Item 1B.</td><td>Unresolved Staff Comments</td><td>33</td></tr>
<tr><td>Item 2.</td><td>Properties</td><td>34</td></tr></table>
<p>Forward-looking statements are described in Item 1. Business and Item 1A. Risk Factors of this report.</p>
<p>PART I</p>
<p><b>Item 1. Business</b></p>
<p>2</p>
<p>Our mission is to make widgets that connect businesses to their customers. We sell end&#8209;to&#8211;end widget solutions &amp; services to customers in 40 countries.</p>
<p>""" + " ".join(f"Sentence number {i} describes the widget business in some detail." for i in range(40)) + """</p>
<p>Employees and Human Capital Resources</p>
<p>Our research team is small. As of December 31, 2025, we had approximately 120 employees, or 6% of our total headcount, involved in research and development.</p>
<p>As of December 31, 2025, we had approximately 1,900 full-time employees, of whom 60% were located in the United States.</p>
<p><b>Item 1A. Risk Factors</b></p>
<p>Investing in our stock involves risk.</p>
</body></html>"""


def test_item1():
    text = P.html_to_text(TENK_HTML.encode("utf-8"))
    desc, note = P.extract_item1(text, "10-K")
    check(desc is not None, "item1: section not found")
    check(note == "10-K Item 1 Business", f"item1: note {note!r}")
    check(desc.startswith("Our mission is to make widgets"), f"item1: TOC/cross-reference not skipped: {desc[:80]!r}")
    check("Risk Factors" not in desc[:120] and "Unresolved" not in desc, "item1: TOC rows leaked into the prose")
    # &#8209; (non-breaking hyphen) is normalised to "-" so the employee patterns see "full-time"; &#8211; stays an en dash
    check("end-to–end widget solutions & services" in desc, "item1: entities not unescaped / U+2011 not normalised")
    check(len(desc) <= P.DESCRIPTION_MAX, f"item1: too long ({len(desc)})")
    check(desc.endswith("."), f"item1: not cut at a sentence boundary: {desc[-40:]!r}")
    check("Employees and Human Capital" not in desc, "item1: ran past the 1,500-char limit")
    # without the real section (TOC only) -> None + note
    toc_only = text[: text.index("PART I")]
    d2, n2 = P.extract_item1(toc_only, "10-K")
    check(d2 is None and "no 10-K Item 1 Business" in n2, f"item1: TOC-only should be None, got {d2!r} / {n2!r}")
    check(P.extract_item1("", "10-K") == (None, "empty document"), "item1: empty document")
    # a short real section ends at Item 1A, not at 1,500 chars
    short = "Item 1.\nBusiness\n3\nItem 1A.\nRisk Factors\n9\n\nItem 1. Business\nWe make one thing. It is a good thing and customers like it very much indeed.\nItem 1A. Risk Factors\nRisks follow."
    d3, _ = P.extract_item1(short, "10-K")
    check(d3 == "We make one thing. It is a good thing and customers like it very much indeed.", f"item1: short section {d3!r}")
    # 20-F fallback: Item 4.B Business Overview
    twenty = ("Item 4. Information on the Company\n4\nItem 4.B Business Overview\n5\nItem 5. Operating Results\n6\n"
              "ITEM 4. INFORMATION ON THE COMPANY\nA. History and development\nThe company was incorporated in 1887 in Johannesburg and listed in 1998.\n"
              "B. Business Overview\nWe are a globally diversified gold producer with nine operating mines in Australia, Peru, South Africa and West Africa. "
              "Our attributable annual gold production is approximately 2.2 million ounces.\nC. Organizational structure\nSubsidiaries follow.")
    d4, n4 = P.extract_item1(twenty, "20-F")
    check(d4 is not None and d4.startswith("We are a globally diversified gold producer"), f"20-F: {d4!r} / {n4}")
    check(n4 == "20-F Item 4.B Business Overview", f"20-F note {n4!r}")
    d5, n5 = P.extract_item1("anything", "40-F")
    check(d5 is None and "40-F" in n5, "40-F should be None with a note")
    # Kroger's layout: "ITEM 1.\nBUSINESS.\n" leaves a lone "." under the heading, which must not lead the prose
    kr = ("Item 1\nBusiness\n3\nItem 1A\nRisk Factors\n10\nITEM 1.\nBUSINESS.\nThe Kroger Co. was founded in 1883 and incorporated in 1902. "
          "Our Company is built on the foundation of our retail grocery business, which includes pharmacies and fuel centers.\nITEM 1A.\nRISK FACTORS.\nRisks.")
    d6, _ = P.extract_item1(kr, "10-K")
    check(d6 is not None and d6.startswith("The Kroger Co. was founded"), f"item1: stray heading period not stripped: {d6!r}")
    # Huntington's layout: a sub-heading under the item heading, and another sub-heading after the opening prose
    body = " ".join(f"Sentence {i} about the regional bank and its {i} businesses in several midwestern states." for i in range(8))
    hb = ("Item 1.\nBusiness\n7\nCompetition\n9\nItem 1A.\nRisk Factors\n28\nItem 1: Business\nGeneral Business Description\n" + body
          + "\nAcquisitions and Mergers\nOn October 20, 2025, Huntington completed the acquisition of Veritex Holdings, Inc.\nItem 1A: Risk Factors\nRisks.")
    d7, _ = P.extract_item1(hb, "10-K")
    check(d7 is not None and d7.startswith("Sentence 0 about"), f"item1: leading sub-heading not dropped: {(d7 or '')[:60]!r}")
    check(d7 and "Acquisitions and Mergers" not in d7 and "Veritex" not in d7, f"item1: prose ran into the next sub-heading: {(d7 or '')[-80:]!r}")
    # Halliburton's TOC labels the rows "Item 1(a). Risk Factors": the period after each label is not a sentence end,
    # and the rows run past eight words before "Item 2" — the TOC must still be skipped and the real heading found
    hal = ("Item 1. Business\n3\nItem 1(a). Risk Factors\n9\nItem 1(b). Unresolved Staff Comments\n20\nItem 1(c). Cybersecurity\n21\nItem 2. Properties\n22\n"
           "Item 3. Legal Proceedings\n23\nItem 4. Mine Safety Disclosures\n24\nItem 7. Management's Discussion and Analysis of Financial Condition and Results of Operations\n30\n"
           "PART I\nItem 1. Business.\nGeneral\nHalliburton Company is one of the world's largest providers of products and services to the energy industry. "
           "We help our customers maximize value throughout the lifecycle of the reservoir, from locating hydrocarbons and managing geological data to drilling and formation evaluation.\n"
           "Item 1(a). Risk Factors.\nThe risk factors follow here in detail for the reader.")
    d10, n10 = P.extract_item1(hal, "10-K")
    check(d10 is not None and d10.startswith("Halliburton Company is one of the world's largest providers"), f"item1 HAL-style TOC taken as the section: {(d10 or '')[:80]!r}")
    check(d10 and "Risk Factors" not in d10 and "Properties" not in d10 and d10.endswith("formation evaluation."), f"item1 HAL: section not bounded at Item 1(a): {(d10 or '')[-60:]!r}")
    # Carnival's TOC indexes Item 1's sub-headings ("A. Overview" ... "E. Industry and Market Data") under the row
    para = ("Carnival Corporation was incorporated in Panama in 1972 and Carnival plc was incorporated in England and Wales in 2000. "
            "Together with their consolidated subsidiaries, they are referred to collectively in this 10-K as Carnival Corporation & plc, our, us and we. "
            "We are the largest global cruise company and among the largest leisure travel companies, with a portfolio of world-class cruise lines that serve guests from every region.")
    ccl = ("Item 1. Business\nA. Overview\nB. Global Cruise Industry\nC. Our Global Cruise Business\nD. Website Access to Carnival Corporation & plc SEC Reports\nE. Industry and Market Data\n3\n"
           "Item 1A. Risk Factors\n15\nItem 1B. Unresolved Staff Comments\n25\nItem 2. Properties\n26\n"
           "PART I\nItem 1. Business.\nA. Overview\n" + para + "\nB. Global Cruise Industry\nThe cruise industry is a strong and growing part of the leisure travel market.\nItem 1A. Risk Factors\nRisks.")
    d11, _ = P.extract_item1(ccl, "10-K")
    # the "referred to collectively" sentence does not count toward min_prose, so the walk goes on past "B. Global Cruise
    # Industry" (the sub-heading itself is dropped) into the next paragraph of the same Item 1
    check(d11 == para + " The cruise industry is a strong and growing part of the leisure travel market.",
          f"item1 CCL-style TOC / indexed sub-headings: {(d11 or '')[:80]!r} ... {(d11 or '')[-60:]!r}")
    # integrated-report 20-F (Gold Fields): a cross-reference TABLE mentions "(b) Business overview" with page ranges and no
    # sentences (must be rejected), there is no Item 4 heading, and the business prose sits under a bare "Overview" heading
    gfi = ("Form 20-F Cross Reference Guide\n(a) History and development\nFurther Information—Information on the Company\n28-29\n"
           "(b) Business overview\nGold Fields' Operations\nBack of\ncover\nFurther Information—Information on the Company—Summary\n"
           "Disclosure of Mining Operations Pursuant to Item 1303 of Regulation\nS-K under the Securities Act\n29-38\n"
           "Further Information—Individual Property Disclosure\n39-61\n(c) Organisational structure\n28-29\n"
           "Overview\nGold Fields is a significant producer of gold and a major holder of gold reserves in South Africa, Ghana, Australia, Peru and Chile. "
           "In Peru, Gold Fields also produces copper. Gold Fields is primarily involved in underground and surface gold mining.\n"
           "Operations\nThe Granny Smith mine is a production stage property.")
    d8, n8 = P.extract_item1(gfi, "20-F", entity="GOLD FIELDS LTD")
    check(d8 is not None and d8.startswith("Gold Fields is a significant producer"), f"20-F overview fallback: {d8!r} / {n8}")
    check("Overview section" in n8, f"20-F overview note {n8!r}")
    check("29-38" not in d8 and "Cross Reference" not in d8, "20-F: the cross-reference table leaked into the description")
    d9, n9 = P.extract_item1(gfi, "20-F", entity=None)
    check(d9 is None and "no 20-F" in n9, f"20-F overview fallback needs the registrant's name: {d9!r}")


# ---------------------------------------------------------------------------
# 2. Employees extractor
def test_employees():
    text = P.html_to_text(TENK_HTML.encode("utf-8"))
    e = P.extract_employees(text)
    check(e is not None, "employees: nothing found")
    if e:
        check(e["count"] == 1900, f"employees: count {e['count']} (the 120 R&D decoy must lose)")
        check(e["as_of"] == "2025-12-31", f"employees: as_of {e['as_of']!r}")
        check(e["evidence"].startswith("As of December 31, 2025, we had approximately 1,900 full-time employees"), f"employees: evidence {e['evidence']!r}")
        check(e["evidence"].endswith("."), "employees: evidence is not a whole sentence")
    # other phrasings
    variants = {
        "Human Capital\nAt January 31, 2026, Kroger employed approximately 409,000 associates, most of whom are covered by collective bargaining agreements.": (409000, "2026-01-31"),
        "Our People\nAs of July 31, 2026, Zscaler had 8,870 employees worldwide, including 3,100 in research and development.": (8870, "2026-07-31"),
        "Employees\nAs of 12/31/2025, the Company had 20,123 full-time employees.": (20123, "2025-12-31"),
        # Kroger's 10-K phrasing (full- and part-time) and Huntington's (a year-average FTE count, no "as of" date)
        "Human Capital\nAs of January 31, 2026, Kroger employed more than 403,000 full- and part-time employees. Our people are essential.": (403000, "2026-01-31"),
        "Human Capital and Inclusion\nHuntington aspires to be a Category of One. Huntington had 20,424 average full-time equivalent colleagues during 2025, whom we encourage to support a shared purpose.": (20424, "2025"),
    }
    for src, (n, d) in variants.items():
        r = P.extract_employees(src)
        check(r is not None and r["count"] == n and r["as_of"] == d, f"employees variant {src[:30]!r}: {r}")
    r = P.extract_employees("Huntington had 20,424 average full-time equivalent colleagues during 2025.")
    check(r and r.get("basis") == "average full-time equivalent for the period", f"employees FTE basis {r}")
    # a point-in-time FTE count (EQT) is not a year-average: "equivalent" alone must not trigger the average wording
    eqt = "Human Capital\nAs of December 31, 2025, we had 1,523 full-time equivalent employees (i.e., excluding temporary employees and contractors), the majority of whom were in Pennsylvania."
    r = P.extract_employees(eqt, entity="EQT Corp")
    check(r and r["count"] == 1523 and r["as_of"] == "2025-12-31" and r.get("basis") == "full-time equivalent as of the stated date", f"employees point-in-time FTE basis {r}")
    # the multi-year 20-F sentence (JD): the last number belongs to the last year, dated with the stated month/day
    jd = "D. Employees\nAs of December 31, 2023, 2024 and 2025, we had a total of 517,124, 570,895 and 776,682 employees, respectively."
    r = P.extract_employees(jd, entity="JD.com, Inc.")
    check(r and r["count"] == 776682 and r["as_of"] == "2025-12-31" and r["evidence"] == jd.split("\n")[1] and "basis" not in r, f"employees multi-year 20-F sentence {r}")
    r = P.extract_employees("Human Capital\nAs of December 31, 2024 and 2025, the Company had 1,200 and 1,350 employees, respectively.")
    check(r and r["count"] == 1350 and r["as_of"] == "2025-12-31", f"employees two-year sentence {r}")
    # subject ranking: the registrant's own sentence beats a subsidiary's, whichever comes first
    sub = "Human Capital\nAs of December 31, 2025, Acme GmbH had 380 employees. As of December 31, 2025, we had approximately 12,000 employees worldwide."
    r = P.extract_employees(sub, entity="WIDGET CORP")
    check(r and r["count"] == 12000, f"employees subsidiary before registrant: {r}")
    r = P.extract_employees("Human Capital\nAs of December 31, 2025, Acme GmbH had 380 employees.", entity="WIDGET CORP")
    check(r and r["count"] == 380, f"employees: a lone proper-noun 'as of' sentence is still accepted: {r}")
    r = P.extract_employees("Human Capital\nAs of December 31, 2025, Widget Corporation and its subsidiaries had 4,100 employees.", entity="WIDGET CORP")
    check(r and r["count"] == 4100, f"employees registrant 'and its subsidiaries': {r}")
    # a per-country breakdown is never the total; a lone "in <place>" count is one location's headcount, not the total
    # (Vulcan: "we employed 11,172 people in the United States", then 280 in Mexico, 32 in Honduras ...) -> None + a note
    check(P.extract_employees("Human Capital\nAs of December 31, 2025, we had 2,100 employees in the United States and 3,400 employees in India.", entity="WIDGET CORP") is None,
          "employees: per-country breakdown must be None")
    notes = []
    r = P.extract_employees("Human Capital\nAs of December 31, 2025, we had 2,100 employees in Germany.", entity="WIDGET CORP", notes=notes)
    check(r is None and len(notes) == 1 and "location" in notes[0] and "2,100 employees in Germany" in notes[0], f"employees lone geographic count -> None with the sentence as evidence: {r} {notes}")
    r = P.extract_employees("Human Capital\nAs of December 31, 2025, we had 2,100 employees in Germany. We had 5,000 average full-time equivalent colleagues during 2025.", entity="WIDGET CORP")
    check(r and r["count"] == 5000, f"employees: a whole-company average beats a geographic subset: {r}")
    # a stray proper noun with "had N workers in <year>" is not the registrant's headcount
    check(P.extract_employees("Hurricane Milton had 150 workers in 2024 displaced.", entity="WIDGET CORP") is None, "employees: 'Hurricane Milton had 150 workers' must be None")
    # the subject never spans a line: the heading above the sentence is not part of the evidence
    r = P.extract_employees("Human Capital and Inclusion\nHuntington had 20,424 average full-time equivalent colleagues during 2025, whom we encourage.", entity="HUNTINGTON BANCSHARES INC/MD")
    check(r and r["count"] == 20424 and r["evidence"].startswith("Huntington had 20,424"), f"employees heading on the line above: {r}")
    # a number split across inline <span>s (Con Edison's "2</span><span>025") is read whole
    ed = P.html_to_text(b'<div>Human Capital</div><div><span>On December 31, 2</span><span>025, Con Edison and its subsidiaries had 15,407 employees</span><span>.</span></div>')
    r = P.extract_employees(ed, entity="CONSOLIDATED EDISON INC")
    check(r and r["count"] == 15407 and r["as_of"] == "2025-12-31", f"employees split across spans: {r}")
    # an "as of" sentence wins over a year-average one when both exist
    both = "Human Capital\nWe had 20,424 average full-time equivalent colleagues during 2025. As of December 31, 2025, we had 20,800 employees."
    r = P.extract_employees(both)
    check(r and r["count"] == 20800 and "basis" not in r, f"employees as-of beats average {r}")
    # the heading glued to the sentence (APP's layout) is stripped from the evidence
    glued = "Employees and Human Capital Resources As of December 31, 2025, we had a total of 898 employees, comprised of 876 full-time and 22 part-time employees. Our culture is strong."
    r = P.extract_employees(glued)
    check(r is not None and r["count"] == 898 and r["evidence"].startswith("As of December 31, 2025, we had a total of 898 employees"), f"employees glued heading: {r}")
    # the evidence is ONE sentence even when the previous sentence ends in a capitalised word run (HBAN's real text):
    # the proper-noun subject is case-sensitive so it cannot reach back across "performance. "
    hb = ("Human Capital and Inclusion\nHuntington aspires to be a Category of One financial services institution: an organization that "
          "uniquely combines its culture and performance. Huntington had 20,424 average full-time equivalent colleagues during 2025, whom we "
          "encourage to support a shared purpose.")
    r = P.extract_employees(hb)
    check(r and r["count"] == 20424 and r["evidence"].startswith("Huntington had 20,424"), f"employees evidence is one sentence: {r}")
    # form 3: the integrated-report bullet with the prior-year comparative (Gold Fields), double-escaped in the HTML;
    # dated by the filing's fiscal period end, evidence bounded to the bullet
    gfi_html = (b"<p>Our people &amp;#8226; 6,628 employees (2024: 6,560) and 16,607 business partners (2024: 16,330) across six countries "
                b"&amp;#8226; US$13.2m spent on training (2024: US$12.3m) &amp;#8226; US$607m paid in wages</p>")
    r = P.extract_employees(P.html_to_text(gfi_html), period="2025-12-31")
    check(r and r["count"] == 6628 and r["as_of"] == "2025-12-31" and r["evidence"] == "6,628 employees (2024: 6,560) and 16,607 business partners (2024: 16,330) across six countries"
          and "comparative" in r.get("basis", ""), f"employees form 3 bullet: {r}")
    check(P.extract_employees("• 6,628 employees (2024: 6,560) across six countries")["as_of"] == "2025", "employees form 3 without a period dates by the comparative year + 1")
    check(P.extract_employees("6,628 employees and 16,607 business partners across six countries") is None, "employees: a bare count without a date or comparative is not evidence")
    # negatives: never guess
    for src in ("", "We believe our employees are our greatest asset and we had a great year.",
                "As of December 31, 2025, we had 3 reportable segments and 12 offices.",
                "As of December 31, 2025, we had approximately 60% of our employees located outside the U.S.",
                "In 2025 we hired 400 employees across the organization."):
        check(P.extract_employees(src) is None, f"employees negative should be None: {src[:50]!r} -> {P.extract_employees(src)}")


# ---------------------------------------------------------------------------
# 3. 8-K items and the filings feed
SUB = {"name": "Widget Corp", "cik": "123", "sic": "7370", "sicDescription": "Services", "stateOfIncorporation": "DE",
       "fiscalYearEnd": "1231", "category": "Large accelerated filer", "exchanges": ["Nasdaq"], "website": "", "phone": "",
       "addresses": {"business": {"street1": "1 MAIN ST", "street2": None, "city": "PALO ALTO", "stateOrCountry": "CA", "stateOrCountryDescription": "CA", "zipCode": "94304"}},
       "filings": {"recent": {
           "form": ["4", "8-K", "10-Q", "8-K/A", "SC 13G", "10-K", "DEF 14A", "S-1", "6-K", "20-F", "40-F", "8-K"] + ["8-K"] * 12,
           "filingDate": ["2026-08-21", "2026-08-05", "2026-08-04", "2026-07-01", "2026-06-30", "2026-02-19", "2026-04-20", "2018-08-24", "2026-05-01", "2025-04-30", "2025-04-29", "2026-04-07"] + [f"2026-03-{d:02d}" for d in range(12, 0, -1)],
           "reportDate": ["2026-08-20", "2026-08-05", "2026-06-30", "2026-07-01", "", "2025-12-31", "", "", "2026-05-01", "2025-12-31", "2025-12-31", "2026-04-02"] + ["2026-03-01"] * 12,
           "items": ["", "2.02,9.01", "", "4.02", "", "", "", "", "", "", "", "5.02,7.01,9.01"] + ["8.01"] * 12,
           "accessionNumber": [f"0001751008-26-{i:06d}" for i in range(24)],
           "primaryDocument": ["xslF345X06/primarydocument.xml", "app-20260805.htm", "app-20260630.htm", "a8ka.htm", "sc13g.htm", "app-20251231.htm", "def14a.htm", "s1.htm", "6k.htm", "20f.htm", "40f.htm", "app-20260402.htm"] + ["8k.htm"] * 12,
           "primaryDocDescription": [""] * 24}, "files": []}}


def test_items_and_feed():
    check(P.map_items("2.02,9.01") == (["2.02", "9.01"], "Results of operations"), f"items 2.02: {P.map_items('2.02,9.01')}")
    check(P.map_items("5.02,7.01,9.01")[1] == "Officer/director change; Reg FD", "items 5.02/7.01")
    check(P.map_items("9.01") == (["9.01"], "Financial statements and exhibits"), "items 9.01 alone")
    check(P.map_items("3.07") == (["3.07"], "Item 3.07"), "items unknown code")
    check(P.map_items("") == ([], ""), "items empty")
    check(P.map_items(None) == ([], ""), "items None")
    for code, desc in (("1.01", "Material agreement"), ("5.02", "Officer/director change"), ("7.01", "Reg FD"), ("8.01", "Other events"),
                       ("2.01", "Acquisition/disposition"), ("1.02", "Termination of agreement"), ("2.03", "Debt obligation"),
                       ("2.05", "Exit costs"), ("2.06", "Impairment"), ("4.01", "Auditor change"), ("4.02", "Non-reliance on financials")):
        check(P.ITEM_DESCRIPTIONS.get(code) == desc, f"item {code} description")
    feed = P.build_filings(SUB, 1751008)
    check(len(feed) == 20, f"feed length {len(feed)} (latest 20)")
    check(all(f["form"] not in ("4", "SC 13G") for f in feed), "feed: non-feed forms leaked")
    dates = [f["filed"] for f in feed]
    check(dates == sorted(dates, reverse=True), "feed: not newest first")
    check(feed[0]["form"] == "8-K" and feed[0]["items"] == ["2.02", "9.01"] and feed[0]["description"] == "Results of operations", f"feed[0] {feed[0]}")
    check(feed[0]["url"] == "https://www.sec.gov/Archives/edgar/data/1751008/000175100826000001/app-20260805.htm", f"feed url {feed[0]['url']}")
    check(feed[1]["form"] == "10-Q" and feed[1]["description"] == "Quarterly report" and feed[1]["period"] == "2026-06-30", f"feed[1] {feed[1]}")
    amend = [f for f in feed if f["form"] == "8-K/A"]
    check(amend and amend[0]["description"] == "Amendment: Non-reliance on financials", f"feed amendment {amend}")
    check("S-1" not in [f["form"] for f in feed] and "40-F" not in [f["form"] for f in feed], "feed: the 2018 S-1 and the 2025 40-F should fall outside the latest 20")
    check(any(f["form"] == "20-F" and f["description"] == "Annual report (foreign private issuer)" for f in feed), "feed: 20-F described")
    check(P.newest_filing_date(SUB) == "2026-08-21", "newest_filing_date")
    la = P.latest_annual(SUB, 1751008)
    check(la and la["form"] == "10-K" and la["filed"] == "2026-02-19" and la["url"].endswith("app-20251231.htm"), f"latest_annual {la}")
    hq, addr = P.headquarters(SUB)
    check(hq == "Palo Alto, CA" and addr["street"] == "1 MAIN ST" and addr["zip"] == "94304" and addr["source"] == "EDGAR submissions", f"headquarters {hq} {addr}")


# ---------------------------------------------------------------------------
# 4. max-age skip rule
def test_skip_rule():
    today = datetime.date(2026, 10, 14)
    fresh = {"as_of": "2026-10-12", "newest_filing_date": "2026-08-21"}
    check(P.should_skip(fresh, "2026-08-21", 7, today) is True, "skip: fresh + unchanged should skip")
    check(P.should_skip(fresh, "2026-10-13", 7, today) is False, "skip: a newer filing must rebuild")
    check(P.should_skip({"as_of": "2026-10-07", "newest_filing_date": "2026-08-21"}, "2026-08-21", 7, today) is False, "skip: exactly max-age days old must rebuild")
    check(P.should_skip({"as_of": "2026-10-08", "newest_filing_date": "2026-08-21"}, "2026-08-21", 7, today) is True, "skip: 6 days old is fresh")
    check(P.should_skip(None, "2026-08-21", 7, today) is False, "skip: missing file must build")
    check(P.should_skip({"as_of": "garbage"}, "2026-08-21", 7, today) is False, "skip: malformed as_of must build")
    check(P.should_skip(fresh, "2026-08-21", 7, today, force=True) is False, "skip: --force rebuilds")
    check(P.should_skip(fresh, None, 7, today) is True, "skip: unknown newest filing falls back to the age check")
    check(P.should_skip(fresh, "2026-08-21", 1, today) is False, "skip: --max-age-days 1 rebuilds a 2-day-old file")


# ---------------------------------------------------------------------------
# 5. Street block from the verified endpoint shapes
TP = {"symbol": "app", "consensusOverview": {"lowPriceTarget": 325.0, "highPriceTarget": 790.0, "priceTarget": 489.3, "buy": 16, "sell": 0, "hold": 4},
      "historicalConsensus": [{"z": {"buy": 16, "hold": 4, "sell": 0, "date": "10/01/2026", "consensus": "Buy"}, "x": 1790812800, "y": 489.3},
                              {"z": {"buy": 15, "hold": 3, "sell": 0, "date": "10/01/2025", "consensus": "Buy"}, "x": 1759276800, "y": 704.09}]}
RT = {"meanRatingType": "Buy", "ratingsSummary": "Based on 16 analysts offering recommendations for 'APP'.", "upgradesDowngrades": [], "brokerNames": ["CITIGROUP", "UBS"]}
FC = {"quarterlyForecast": {"rows": [{"fiscalEnd": "Sep 2026", "consensusEPSForecast": 3.95, "highEPSForecast": 4.14, "lowEPSForecast": 3.79, "noOfEstimates": 9, "up": 0, "down": 1}]},
      "yearlyForecast": {"rows": [{"fiscalEnd": "Dec 2026", "consensusEPSForecast": 15.68, "highEPSForecast": 16.02, "lowEPSForecast": 14.97, "noOfEstimates": 10, "up": 0, "down": 1}]}}
EPS = {"earningsPerShare": [{"type": "PreviousQuarter", "period": "Jun 2026", "consensus": 3.72, "earnings": 3.76},
                            {"type": "PreviousQuarter", "period": "Sep 2025", "consensus": 2.37, "earnings": 2.45},
                            {"type": "UpcomingQuarter", "period": "Sep 2026", "consensus": 3.95, "earnings": 0.0}]}
MO = {"changeInConsensus": {"monthData": {"qtrMean": 3.95, "yrMean": 15.72}, "weekData": {"qtrMean": 3.95, "yrMean": 15.72}, "currentData": {"qtrMean": 3.95, "yrMean": 15.68},
                            "fiscalYearEndText": "Fiscal Year End Dec 2026", "fiscalQtrEndText": "Fiscal Quarter End Sep 2026"}}
ED = {"reportText": "Applovin Corporation is expected* to report earnings on  11/04/2026 after market close.  The report will be for the fiscal Quarter ending Sep 2026."}
PEG = {"pegr": {"label": "Forecast 12 Month Forward PEG Ratio", "pegValue": 0.55}}
SUMM = {"summaryData": {"Exchange": {"value": "NASDAQ-GS"}, "OneYrTarget": {"value": "$475.00"}, "ShareVolume": {"value": "4,348,338"}, "AverageVolume": {"value": "5,505,072"},
                        "PreviousClose": {"value": "$272.28"}, "FiftTwoWeekHighLow": {"value": "$738.01/$266.84"}, "MarketCap": {"value": "87,742,145,690"},
                        "AnnualizedDividend": {"value": "N/A"}, "Yield": {"value": "N/A"}, "ExDividendDate": {"value": "N/A"}, "DividendPaymentDate": {"value": "N/A"}}}
# HBAN's live quote summary: Nasdaq publishes the dividend dates as text ("Sep 17, 2026"), not MM/DD/YYYY
SUMM_DIV = {"summaryData": {"Exchange": {"value": "NASDAQ-GS"}, "Yield": {"value": "4.11%"}, "AnnualizedDividend": {"value": "$0.62"},
                            "ExDividendDate": {"value": "Sep 17, 2026"}, "DividendPaymentDate": {"value": "Oct 1, 2026"}}}


def test_street():
    s = P.build_street("2026-10-14", TP, RT, FC, EPS, MO, ED, PEG, SUMM)
    check(s["consensus"] == "Buy" and s["analysts"] == 16 and (s["buy"], s["hold"], s["sell"]) == (16, 4, 0), f"street counts {s}")
    check((s["target_mean"], s["target_low"], s["target_high"], s["target_1y_nasdaq_summary"]) == (489.3, 325.0, 790.0, 475.0), "street targets")
    check([h["date"] for h in s["history"]] == ["2025-10-01", "2026-10-01"], f"street history oldest first, ISO: {[h['date'] for h in s['history']]}")
    check(s["history"][0]["mean_target"] == 704.09 and s["history"][0]["consensus"] == "Buy" and s["history"][0]["buy"] == 15, "street history row")
    check(s["brokers"] == ["CITIGROUP", "UBS"] and s["upgrades_downgrades"] == [], "street brokers")
    q = s["eps_forecast"]["quarterly"][0]
    check(q["period"] == "Sep 2026" and q["fiscal_end"] == "2026-09" and q["consensus"] == 3.95 and q["low"] == 3.79 and q["high"] == 4.14 and q["estimates"] == 9 and q["revisions_up"] == 0 and q["revisions_down"] == 1, f"eps_forecast quarterly {q}")
    check(s["eps_forecast"]["annual"][0]["consensus"] == 15.68, "eps_forecast annual")
    check([r["period"] for r in s["eps_history"]] == ["Sep 2025", "Jun 2026"], f"eps_history oldest first {s['eps_history']}")
    check(s["eps_history"][1]["actual"] == 3.76 and abs(s["eps_history"][1]["surprise_pct"] - round((3.76 - 3.72) / 3.72 * 100, 2)) < 1e-9, f"surprise_pct {s['eps_history'][1]}")
    check(s["eps_upcoming"] == [{"period": "Sep 2026", "consensus": 3.95}], "eps_upcoming")
    check(s["momentum"]["quarter"] == {"period": "Sep 2026", "current": 3.95, "week_ago": 3.95, "month_ago": 3.95}, f"momentum quarter {s['momentum']}")
    check(s["momentum"]["year"]["period"] == "Dec 2026" and s["momentum"]["year"]["current"] == 15.68 and s["momentum"]["year"]["week_ago"] == 15.72, "momentum year")
    check(s["next_earnings"]["date"] == "2026-11-04" and s["next_earnings"]["timing"] == "after market close" and "expected" in s["next_earnings"]["text"], f"next_earnings {s['next_earnings']}")
    check(s["peg_forward"] == 0.55, "peg")
    # partial failure: only targetprice came back -> the rest null/empty, the block still exists
    s2 = P.build_street("2026-10-14", TP, None, None, None, None, None, None, None)
    check(s2 is not None and s2["target_mean"] == 489.3 and s2["analysts"] == 20 and s2["consensus"] == "Buy" and s2["brokers"] == [] and s2["momentum"] is None and s2["next_earnings"] is None and s2["peg_forward"] is None, f"street partial {s2}")
    check(P.build_street("2026-10-14") is None, "street: all endpoints failed -> None")
    check(P.build_street("2026-10-14", peg={"pegr": 1.2})["peg_forward"] == 1.2, "peg numeric form")
    # Nasdaq placeholders (GFI's real payloads): estimate-momentum 999 = no estimate -> null; quote/eps rows that are
    # consensus 0 AND earnings 0 are not filed zeros -> dropped; both leave a warning
    w = []
    mo999 = {"changeInConsensus": {"monthData": {"qtrMean": 999.0, "yrMean": 4.15}, "weekData": {"qtrMean": 999.0, "yrMean": 4.16}, "currentData": {"qtrMean": 999.0, "yrMean": 4.16},
                                   "fiscalYearEndText": "Fiscal Year End Dec 2026", "fiscalQtrEndText": "Fiscal Quarter End Sep 2026"}}
    eps0 = {"earningsPerShare": [{"type": "PreviousQuarter", "period": "Sep 2025", "consensus": 0.0, "earnings": 0.0},
                                 {"type": "PreviousQuarter", "period": "Dec 2025", "consensus": 0.0, "earnings": 0.0},
                                 {"type": "UpcomingQuarter", "period": "Sep 2026", "consensus": 0.0, "earnings": 0.0},
                                 {"type": "PreviousQuarter", "period": "Mar 2026", "consensus": -0.05, "earnings": -0.01}]}
    s3 = P.build_street("2026-10-14", TP, None, None, eps0, mo999, None, None, None, warnings=w)
    check(s3["momentum"]["quarter"] == {"period": "Sep 2026", "current": None, "week_ago": None, "month_ago": None} and s3["momentum"]["year"]["current"] == 4.16, f"momentum 999 -> null: {s3['momentum']}")
    # a beat on a NEGATIVE consensus (-0.01 actual vs -0.05 consensus) is a positive surprise, as Nasdaq's own
    # earnings-surprise endpoint publishes it (ZS Oct 2025: "80"); (actual / consensus - 1) would flip the sign
    check(s3["eps_history"] == [{"period": "Mar 2026", "consensus": -0.05, "actual": -0.01, "surprise_pct": 80.0}] and s3["eps_upcoming"] == [], f"eps placeholders dropped: {s3['eps_history']} {s3['eps_upcoming']}")
    check(len(w) == 2 and "3 quote/eps row(s)" in w[0] and "999" in w[1], f"placeholder warnings {w}")
    zs = P.build_street("2026-10-14", eps={"earningsPerShare": [
        {"type": "PreviousQuarter", "period": "Oct 2025", "consensus": -0.05, "earnings": -0.01}, {"type": "PreviousQuarter", "period": "Jan 2026", "consensus": -0.05, "earnings": -0.08},
        {"type": "PreviousQuarter", "period": "Apr 2026", "consensus": -0.04, "earnings": -0.03}, {"type": "PreviousQuarter", "period": "Jul 2026", "consensus": 0.06, "earnings": 0.14}]})
    check([r["surprise_pct"] for r in zs["eps_history"]] == [80.0, -60.0, 25.0, 133.33], f"surprise sign on negative consensus (ZS): {[r['surprise_pct'] for r in zs['eps_history']]}")
    # a genuine zero (consensus 0, actual non-zero) is kept
    s4 = P.build_street("2026-10-14", eps={"earningsPerShare": [{"type": "PreviousQuarter", "period": "Jun 2026", "consensus": 0.0, "earnings": 0.02}]})
    check(s4["eps_history"] == [{"period": "Jun 2026", "consensus": 0.0, "actual": 0.02, "surprise_pct": None}], f"genuine zero consensus kept: {s4['eps_history']}")
    m = P.build_market(SUMM)
    check(m == {"exchange": "NASDAQ-GS", "average_volume": 5505072, "volume": 4348338, "market_cap_nasdaq": 87742145690, "high_52w": 738.01, "low_52w": 266.84,
                "previous_close": 272.28, "one_year_target": 475.0, "dividend_yield_nasdaq": None, "annualized_dividend": None, "ex_dividend_date": None, "dividend_pay_date": None}, f"market {m}")
    check(P.build_market(None) is None, "market None")
    md = P.build_market(SUMM_DIV)
    check(md["ex_dividend_date"] == "2026-09-17" and md["dividend_pay_date"] == "2026-10-01" and md["dividend_yield_nasdaq"] == 4.11 and md["annualized_dividend"] == 0.62, f"market text dividend dates {md}")
    check(P.build_market({"summaryData": {"ExDividendDate": {"value": "09/17/2026"}}})["ex_dividend_date"] == "2026-09-17", "market MM/DD/YYYY dividend date still accepted")
    nq = {"CompanyDescription": {"value": "Widgets."}, "Industry": {"value": "Software"}, "Sector": {"value": "Technology"}, "CompanyUrl": {"value": "https://w.com"}}
    a = P.build_about(SUB, 123, nq, SUMM, None, None, ("2021-03-02", "S-1"))
    check(a["description_short"] == "Widgets." and a["industry"] == "Software" and a["exchange"] == "NASDAQ-GS" and a["website"] == "https://w.com" and a["headquarters"] == "Palo Alto, CA"
          and a["first_sec_filing"] == "2021-03-02" and a["first_sec_filing_form"] == "S-1" and a["employees"] is None and a["description"] is None and a["sic"] == "7370" and a["fiscal_year_end_mmdd"] == "1231", f"about {a}")
    check(a["address"]["source"] == "EDGAR submissions", f"about address source without a cover {a['address']}")
    cover = {"street": "120 Holger Way", "city": "San Jose", "state": "California", "zip": "95134", "country": None, "source": "annual filing cover"}
    a2 = P.build_about(SUB, 123, nq, SUMM, None, None, (None, None), cover=cover)
    check(a2["headquarters"] == "San Jose, California" and a2["address"]["zip"] == "95134" and a2["address"]["source"] == "annual filing cover" and a2["first_sec_filing"] is None and a2["first_sec_filing_form"] is None, f"about with a cover address {a2['headquarters']} {a2['address']}")
    # NaN / Infinity from Nasdaq never crash the build or reach the JSON
    check(P.build_market({"summaryData": {"MarketCap": {"value": "NaN"}, "PreviousClose": {"value": "Infinity"}}}) == {"exchange": None, "average_volume": None, "volume": None, "market_cap_nasdaq": None, "high_52w": None, "low_52w": None,
          "previous_close": None, "one_year_target": None, "dividend_yield_nasdaq": None, "annualized_dividend": None, "ex_dividend_date": None, "dividend_pay_date": None}, "market NaN/Infinity -> null")


# ---------------------------------------------------------------------------
# 6. first SEC filing: registration forms first, pagination
def _sub_rows(rows, files=None):
    return {"filings": {"recent": {"form": [r[0] for r in rows], "filingDate": [r[1] for r in rows]}, "files": files or []}}


def test_first_filing():
    # SUB's recent rows hold an S-1 (2018-08-24) and nothing periodic before it -> the S-1
    check(P.first_filing(SUB) == ("2018-08-24", "S-1"), f"first_filing SUB {P.first_filing(SUB)}")
    check(P.earliest_filing_date(SUB) == "2018-08-24", "earliest_filing_date is the date half")
    # APP's real sequence: a Form D (2018) and a DRS draft (2020) precede the S-1 (2021-03-02) and the 424B4 (2021-04-15, the IPO)
    app = _sub_rows([("10-Q", "2021-05-15"), ("424B4", "2021-04-15"), ("S-1/A", "2021-03-22"), ("S-1", "2021-03-02"), ("DRSLTR", "2021-01-15"), ("DRS", "2020-12-07"), ("D", "2018-08-24")])
    check(P.first_filing(app) == ("2021-03-02", "S-1"), f"first_filing APP sequence {P.first_filing(app)}")
    zs = _sub_rows([("424B4", "2018-03-16"), ("S-1", "2018-02-16"), ("DRS", "2017-08-25")])
    check(P.first_filing(zs) == ("2018-02-16", "S-1"), f"first_filing ZS sequence {P.first_filing(zs)}")
    # a company public before EDGAR (Kroger): periodic reports precede its first S-1 -> the overall earliest filing
    kr = _sub_rows([("10-Q", "1996-08-01"), ("S-1", "1996-05-05"), ("8-K", "1995-03-01"), ("10-K405", "1994-01-07")])
    check(P.first_filing(kr) == ("1994-01-07", "10-K405"), f"first_filing pre-EDGAR company {P.first_filing(kr)}")
    # foreign and spin-off forms count as registrations; an amendment carries its base form
    check(P.first_filing(_sub_rows([("20-F", "2004-06-30"), ("F-1/A", "2003-10-02"), ("D", "2001-01-01")])) == ("2003-10-02", "F-1/A"), "first_filing F-1/A")
    check(P.first_filing(_sub_rows([("10-Q", "2022-05-01"), ("10-12B", "2021-11-01")])) == ("2021-11-01", "10-12B"), "first_filing Form 10 spin-off")
    check(P.first_filing(_sub_rows([("D", "2019-01-01"), ("DRS", "2020-01-01")])) == ("2019-01-01", "D"), "first_filing: no registration form at all -> the earliest filing")
    check(P.first_filing({"filings": {}}) == (None, None), "first_filing empty")
    # pagination: pages are fetched oldest first and stop once a registration form has been seen
    calls = []

    def fetch(url):
        calls.append(url)
        if url.endswith("CIK-002.json"):
            return {"form": ["D", "S-1", "10-Q"], "filingDate": ["2009-01-01", "2010-06-01", "2010-08-01"]}
        return {"form": ["10-Q", "8-K"], "filingDate": ["2012-01-01", "2012-02-01"]}
    paged = _sub_rows([("10-K", "2026-02-01")], files=[{"name": "CIK-001.json", "filingFrom": "2011-01-01", "filingTo": "2019-06-02"}, {"name": "CIK-002.json", "filingFrom": "2009-01-01", "filingTo": "2010-12-15"}])
    check(P.first_filing(paged, fetch=fetch) == ("2010-06-01", "S-1") and calls == ["https://data.sec.gov/submissions/CIK-002.json"], f"first_filing paged: {calls}")
    calls.clear()
    old = _sub_rows([("10-K", "2026-02-01")], files=[{"name": "CIK-001.json", "filingFrom": "2011-01-01"}, {"name": "CIK-003.json", "filingFrom": "1996-01-01"}])

    def fetch_old(url):
        calls.append(url)
        return {"form": ["10-K405"], "filingDate": ["1996-03-01"]} if url.endswith("003.json") else {"form": ["10-Q"], "filingDate": ["2011-02-01"]}
    check(P.first_filing(old, fetch=fetch_old) == ("1996-03-01", "10-K405") and calls == ["https://data.sec.gov/submissions/CIK-003.json", "https://data.sec.gov/submissions/CIK-001.json"], f"first_filing: every page when no registration form exists {calls}")

    def boom(url):
        raise OSError("down")
    w = []
    check(P.first_filing(paged, fetch=boom, warnings=w) == ("2009-01-01", None) and len(w) == 2, f"first_filing: unreadable pages fall back to filingFrom with a warning {w}")


# ---------------------------------------------------------------------------
def test_helpers():
    check(P.num("$738.01") == 738.01 and P.num("4,348,338") == 4348338 and P.num("N/A") is None and P.num("1.23%") == 1.23 and P.num(None) is None, "num")
    check(P.num("-1.5") == -1.5 and P.num("1e3") == 1000.0 and P.num(7) == 7.0 and P.num(True) is None, "num forms")
    # NaN / Infinity / '1_000' are not numbers: a NaN would crash intnum and an inf is invalid JSON for the browser
    check(all(P.num(v) is None for v in ("NaN", "nan", "Infinity", "-inf", "1_000", "1 000", "abc", float("nan"), float("inf"))), "num rejects NaN / inf / underscores")
    check(P.intnum("NaN") is None and P.intnum("4,348,338") == 4348338, "intnum")
    try:
        import tempfile
        tmp = os.path.join(tempfile.gettempdir(), "profile_test_nan.json")
        P.write_atomic(tmp, {"x": float("nan")})
        check(False, "write_atomic must refuse NaN")
    except ValueError:
        pass
    check(not os.path.exists(tmp) and not os.path.exists(tmp + ".tmp"), "write_atomic leaves no file (and no .tmp) behind when it refuses")
    # inline tags vanish (words split across <span>s stay whole); block tags still break lines
    check(P.html_to_text(b"<div>It<span>em 1. B</span>USINESS</div><p>As of December 31, 2<span>025</span>, we had <b>15,407</b> employees.</p>") == "Item 1. BUSINESS\nAs of December 31, 2025, we had 15,407 employees.",
          f"html_to_text inline tags: {P.html_to_text(b'<div>It<span>em 1. B</span>USINESS</div>')!r}")
    check(P.html_to_text(b'<ix:nonNumeric name="dei:X">Zscaler</ix:nonNumeric>, Inc.<td>next') == "Zscaler, Inc.\nnext", "html_to_text ix tags vanish")
    # the inline-XBRL cover address (ZS's 10-K: San Jose, where the submissions address says Santa Clara)
    cov = (b'<html><body><div><ix:nonNumeric contextRef="c1" name="dei:EntityAddressAddressLine1" id="x">120 Holger Way</ix:nonNumeric></div>'
           b'<div><ix:nonNumeric name="dei:EntityAddressCityOrTown" contextRef="c1">San Jose</ix:nonNumeric>, <ix:nonNumeric name="dei:EntityAddressStateOrProvince" contextRef="c1">California</ix:nonNumeric> '
           b'<ix:nonNumeric name="dei:EntityAddressPostalZipCode" contextRef="c1">95134</ix:nonNumeric></div></body></html>')
    check(P.cover_address(cov) == {"street": "120 Holger Way", "city": "San Jose", "state": "California", "zip": "95134", "country": None, "source": "annual filing cover"}, f"cover_address {P.cover_address(cov)}")
    hq, addr = P.headquarters(SUB, P.cover_address(cov))
    check(hq == "San Jose, California" and addr["source"] == "annual filing cover", f"headquarters prefers the cover {hq} {addr}")
    # HBAN's cover: two address lines, the city tag reads "Columbus," inside a span
    cov2 = (b'<ix:nonNumeric name="dei:EntityAddressAddressLine1" contextRef="c">Huntington Center</ix:nonNumeric> <ix:nonNumeric name="dei:EntityAddressAddressLine2" contextRef="c">41 South High Street</ix:nonNumeric> '
            b'<ix:nonNumeric name="dei:EntityAddressCityOrTown" contextRef="c"><span>Columbus,</span></ix:nonNumeric> <ix:nonNumeric name="dei:EntityAddressStateOrProvince" contextRef="c">Ohio</ix:nonNumeric>')
    c2 = P.cover_address(cov2)
    check(c2 and c2["street"] == "Huntington Center 41 South High Street" and c2["city"] == "Columbus" and c2["state"] == "Ohio" and c2["zip"] is None, f"cover_address HBAN-style {c2}")
    check(P.cover_address(b"<html><body>no cover tags</body></html>") is None and P.headquarters(SUB, None)[0] == "Palo Alto, CA", "cover_address absent -> submissions")
    # CCL's cover tags TWO registrants under their own contextRefs; every field comes from the first city's context
    # (Carnival Corporation, Miami), never the plc's "United Kingdom"
    cov3 = (b'<ix:nonNumeric name="dei:EntityAddressAddressLine1" contextRef="corp">3655 N.W. 87th Avenue</ix:nonNumeric> <ix:nonNumeric name="dei:EntityAddressCityOrTown" contextRef="corp">Miami</ix:nonNumeric>, '
            b'<ix:nonNumeric name="dei:EntityAddressStateOrProvince" contextRef="corp">Florida</ix:nonNumeric> <ix:nonNumeric name="dei:EntityAddressPostalZipCode" contextRef="corp">33178-2428</ix:nonNumeric>'
            b'<ix:nonNumeric name="dei:EntityAddressAddressLine1" contextRef="plc">Carnival House, 100 Harbour Parade</ix:nonNumeric> <ix:nonNumeric name="dei:EntityAddressCityOrTown" contextRef="plc">Southampton</ix:nonNumeric> '
            b'<ix:nonNumeric name="dei:EntityAddressCountry" contextRef="plc">United Kingdom</ix:nonNumeric> <ix:nonNumeric name="dei:EntityAddressPostalZipCode" contextRef="plc">SO15 1ST</ix:nonNumeric>')
    c3 = P.cover_address(cov3)
    check(c3 == {"street": "3655 N.W. 87th Avenue", "city": "Miami", "state": "Florida", "zip": "33178-2428", "country": None, "source": "annual filing cover"}, f"cover_address two registrants {c3}")
    # a street tagged in another context before the first city does not leak either
    c4 = P.cover_address(b'<ix:nonNumeric name="dei:EntityAddressAddressLine1" contextRef="old">1 Old Road</ix:nonNumeric><ix:nonNumeric name="dei:EntityAddressCityOrTown" contextRef="new">Austin</ix:nonNumeric>')
    check(c4 and c4["city"] == "Austin" and c4["street"] is None, f"cover_address street from another context {c4}")
    check(P.iso_from_mdy("10/01/2025") == "2025-10-01" and P.iso_from_mdy("x") is None, "iso_from_mdy")
    check(P.iso_from_text_date("December 31, 2025") == "2025-12-31" and P.iso_from_text_date("31 December 2025") == "2025-12-31" and P.iso_from_text_date("Dec. 31, 2025") == "2025-12-31", "iso_from_text_date")
    check(P.month_key("Sep 2026") == "2026-09" and P.month_key("September 2026") == "2026-09" and P.month_key("") is None, "month_key")
    t = P.html_to_text(b"<p>A&nbsp;&amp;\xa0B</p><script>x<y</script><table><tr><td>c</td></tr></table>")
    check(t == "A & B\nc", f"html_to_text {t!r}")
    t2 = P.html_to_text(b"Risk \x97 Factors")  # cp1252 em dash, invalid as UTF-8
    check(t2 == "Risk — Factors", f"html_to_text cp1252 fallback {t2!r}")


# ---------------------------------------------------------------------------
# 8. Review round (2026-10-15 reverify): description = a genuine prose run; heading layouts; headcount forms
LOREM = " ".join(f"Sentence {i} explains how the company serves its customers and grows its business over time." for i in range(6))


def test_item1_review_round():
    toc = "Item 1. Business\n3\nItem 1A. Risk Factors\n20\nItem 2. Properties\n30\n"
    # M&T Bank: the first non-TOC occurrence is a Regulation S-K subpart 1400 cross-reference SHEET (index rows, page
    # ranges, no sentence of its own); the real "Item 1. Business." heading follows and must win
    mtb = (toc + "CROSS-REFERENCE SHEET\nForm 10-K\nPage\nPART I\nItem 1.\nBusiness\n3\nDisclosure pursuant to subpart 1400 of Regulation S-K\nI.\n"
           "Distribution of assets, liabilities and shareholders’ equity; interest rates and interest differential\nA.Average balance sheets\n56\n"
           "B.Interest income/expense and resulting yield or rate on average\ninterest-earning assets and interest‑bearing liabilities\n56\n"
           "IV.\nAllowance for credit losses\nA.Credit ratios\n69, 74, 77\nFactors driving material changes in credit ratios or related\ncomponents\n68-77, 129-141\n"
           "Item 1A.\nRisk Factors\n20\nPART I\nItem 1. Business.\nM&T is a New York business corporation that has elected to be treated as a financial holding company. "
           "M&T was incorporated in November 1969 and its banks offer a wide range of retail and commercial banking services.\nItem 1A. Risk Factors\nRisks.")
    d, n = P.extract_item1(mtb, "10-K")
    check(d is not None and d.startswith("M&T is a New York business corporation"), f"item1 MTB cross-reference sheet: {(d or '')[:90]!r} / {n}")
    # MetLife / Prudential / The Hartford: a sub-section INDEX (rows + page numbers) directly under the real heading, then
    # the prose; Hartford's heading is "Part I - Item 1. Business" on one line followed by "Item 1.\nBusiness" again
    met = (toc + "PART I\nItem 1. Business\nIndex to Business\nPage\nBusiness Overview & Strategy\n5\nPolicyholder Liabilities\n10\nUnderwriting and Pricing\n11\n"
           "Human Capital Resources\n24\nAvailable Information\n26\n4\nTable of Contents\nBusiness Overview & Strategy\n"
           "As used in this Form 10-K, “MetLife,” the “Company,” “we,” “our” and “us” refer to MetLife, Inc., a Delaware corporation incorporated in 1999. "
           "MetLife is one of the world’s leading financial services companies, providing insurance, annuities, employee benefits and asset management.\n" + LOREM)
    d, _ = P.extract_item1(met, "10-K")
    # the leading "As used in this Form 10-K ... refer to" definition is dropped (PREAMBLE)
    check(d is not None and d.startswith("MetLife is one of the world’s leading") and "Policyholder" not in d and "Table of Contents" not in d, f"item1 MET index: {(d or '')[:90]!r}")
    pru = (toc + "PART I\nITEM 1. BUSINESS\nTable of Contents\nPage\nOverview\n2\nPGIM\n3\nRetirement Strategies\n4\nGroup Insurance\n6\nRegulation\n13\nHuman Capital Resources\n18\n1\n"
           "Table of Contents\nOverview\nPrudential Financial, Inc., a global financial services leader and premier active global investment manager, has operations in "
           "the United States, Asia, Europe and Latin America. Through our subsidiaries and affiliates we offer a wide array of financial products and services.\n" + LOREM)
    d, _ = P.extract_item1(pru, "10-K")
    check(d is not None and d.startswith("Prudential Financial, Inc., a global financial services leader") and "PGIM" not in d, f"item1 PRU index: {(d or '')[:90]!r}")
    hig = (toc + "Index to Business\nPart I - Item 1. Business\nItem 1.\nBusiness\n(Dollar amounts in millions, except for per share data, unless otherwise stated)\nIndex\nDescription\nPage\n"
           "General\n6\nOrganization\n6\nReserves\n15\nHuman Capital Resources\n18\nGeneral\nThe Hartford Insurance Group, Inc. is a holding company for a group of subsidiaries "
           "that provide property and casualty insurance, employee group benefits and mutual funds to individual and business customers.\n" + LOREM)
    d, _ = P.extract_item1(hig, "10-K")
    check(d is not None and d.startswith("The Hartford Insurance Group, Inc. is a holding company"), f"item1 HIG 'Part I - Item 1' + index: {(d or '')[:90]!r}")
    # "Items 1 and 2. Business and Properties" (Devon, Diamondback) and "Part I. Item 1. Business" on one line (Expedia)
    dvn = ("PART I\n7\nItems 1 and 2. Business and Properties\n7\nItem 1A. Risk Factors\n16\nItem 3. Legal Proceedings\n28\n"
           "PART I\nItems 1 and 2. Business and Properties\nGeneral\nFounded in 1971 and publicly held since 1988, Devon is an independent energy company engaged primarily "
           "in the exploration, development and production of oil, natural gas and NGLs. Our operations are concentrated in five core areas.\nItem 1A. Risk Factors\nRisks.")
    d, n = P.extract_item1(dvn, "10-K")
    check(d is not None and d.startswith("Founded in 1971 and publicly held since 1988, Devon") and n == "10-K Items 1 and 2 Business and Properties", f"item1 'Items 1 and 2': {(d or '')[:80]!r} / {n}")
    fang = (toc.replace("Item 1. Business", "Items 1 and 2. Business and Properties") + "ITEMS 1 and 2. BUSINESS AND PROPERTIES\nOverview\nWe are an independent oil and natural gas "
            "company focused on the acquisition, development, exploration and exploitation of unconventional, onshore oil and natural gas reserves in the Permian Basin. "
            "Our activities are primarily directed at the horizontal development of the Midland and Delaware Basins.\nItem 1A. Risk Factors\nRisks.")
    d, _ = P.extract_item1(fang, "10-K")
    check(d is not None and d.startswith("We are an independent oil and natural gas company"), f"item1 'ITEMS 1 and 2' upper case: {(d or '')[:80]!r}")
    expe = (toc + "as “Expedia Group,” the “Company,” “us,” “we” and “our” in this Annual Report on Form 10-K.\nPart I. Item 1. Business\nOverview\nExpedia Group, Inc. is the global "
            "travel marketplace with one purpose: to help travelers explore the world, one journey at a time. We connect travelers, partners, and advertisers through our trusted brands.\n"
            "Item 1A. Risk Factors\nRisks.")
    d, _ = P.extract_item1(expe, "10-K")
    check(d is not None and d.startswith("Expedia Group, Inc. is the global travel marketplace"), f"item1 'Part I. Item 1. Business' one line: {(d or '')[:80]!r}")
    # forward-looking-statements / read-in-conjunction boilerplate opening Item 1 is skipped (Waste Connections, Cboe)
    wcn = (toc + "PART I\nITEM 1. BUSINESS\nThis Annual Report on Form 10-K contains forward-looking statements based on expectations, estimates, and projections as of the date "
           "of this filing. Actual results may differ materially from those expressed in forward-looking statements.\nOur Company\nWaste Connections, Inc. is the third largest "
           "solid waste services company in North America, providing non-hazardous waste collection, transfer and disposal services. Our senior management team has extensive experience.\n"
           "Item 1A. Risk Factors\nRisks.")
    d, _ = P.extract_item1(wcn, "10-K")
    check(d is not None and d.startswith("Waste Connections, Inc. is the third largest") and "forward-looking" not in d, f"item1 FLS boilerplate skipped: {(d or '')[:80]!r}")
    cboe = (toc + "PART I\nItem 1. Business\nThe following description of the business should be read in conjunction with the information included elsewhere in this Annual "
            "Report on Form 10-K. This description contains forward-looking statements that involve risks and uncertainties.\nOverview\nCboe Global Markets, Inc., the world's "
            "leading derivatives and securities exchange network, delivers trading, clearing, and investment solutions to people around the world. Cboe provides trading solutions.\n"
            "Item 1A. Risk Factors\nRisks.")
    d, _ = P.extract_item1(cboe, "10-K")
    check(d is not None and d.startswith("Cboe Global Markets, Inc., the world's leading"), f"item1 read-in-conjunction lead-in skipped: {(d or '')[:80]!r}")
    # running page headers never leak: Constellation's repeated "ITEM 1. BUSINESS / Table of Contents / PART I" and its
    # page footer (recurring through the document), Baidu's "Table of Contents" mid-paragraph
    footer = "Constellation Brands, Inc. FY 2026 Form 10-K\n#WORTHREACHINGFOR I {p}\n"
    stz = (toc + "".join(footer.format(p=p) + "Other page text that is long enough to be a line of its own here.\n" for p in ("i", "ii", "iii", "iv"))
           + "PART I\nITEM 1. BUSINESS\nTable of Contents\nPART I\nITEM 1. BUSINESS\nINTRODUCTION\nWe are an international producer and marketer of beer, wine, and spirits "
           "with operations in the U.S., Mexico, New Zealand, and Italy.\n" + footer.format(p=1) + "PART I\nITEM 1. BUSINESS\nTable of Contents\n"
           "In our beer business, we focus on upholding our leadership position in the U.S. beer market and continuing to grow our imported brands.\nItem 1A. Risk Factors\nRisks.")
    d, _ = P.extract_item1(stz, "10-K")
    check(d == "We are an international producer and marketer of beer, wine, and spirits with operations in the U.S., Mexico, New Zealand, and Italy. "
               "In our beer business, we focus on upholding our leadership position in the U.S. beer market and continuing to grow our imported brands.", f"item1 STZ running headers: {d!r}")
    bidu = ("Item 4. Information on the Company\n40\nItem 4.B Business Overview\n45\nItem 5. Operating Results\n60\nB. Business Overview\n"
            "Our mission is to make the complicated world simpler through technology.\nTable of Contents\nWe are a leading AI company with a strong internet foundation. "
            "We have been consistently investing in AI since 2010 to advance our technological capabilities.\nC. Organizational Structure\nSubsidiaries.")
    d, _ = P.extract_item1(bidu, "20-F")
    check(d is not None and d.startswith("Our mission is to make the complicated world simpler through technology. We are a leading AI company"), f"item1 BIDU mid-text TOC header: {(d or '')[:120]!r}")
    # a sentence the document broke across two lines is still the first prose line (Halliburton, Gold Fields)
    hal = (toc + "PART I\nItem 1. Business.\nGeneral\nHalliburton Company is one of the world's largest providers of products and services to the energy\n"
           "industry. Its predecessor was established in 1919 and incorporated under the laws of the State of Delaware in 1924.\nItem 1A. Risk Factors\nRisks.")
    d, _ = P.extract_item1(hal, "10-K")
    check(d is not None and d.startswith("Halliburton Company is one of the world's largest providers of products and services to the energy industry."), f"item1 broken first line: {(d or '')[:100]!r}")
    # a 10-K that only cross-references Item 1 (Synchrony style): no prose anywhere under the heading -> None, never the table
    syf = (toc + "Form 10-K Cross-Reference Index\nItem 1. Business\n3-25, 30-35, 40-44\nItem 1A. Risk Factors\n50-70\nItem 2. Properties\n71\nPART I\nItem 1A. Risk Factors\nRisks.")
    d, n = P.extract_item1(syf, "10-K")
    check(d is None and "no 10-K Item 1 Business" in n, f"item1 cross-reference-only 10-K: {d!r}")
    # the description cut never ends on an abbreviation ("... Acme Inc." is not a sentence end)
    cut = P._cut_at_sentence("A" * 300 + " first sentence ends here. " + "b " * 560 + "We are Acme Inc. the leader in widgets and more text follows here")
    check(cut.endswith("first sentence ends here."), f"cut at an abbreviation: {cut[-40:]!r}")


def test_employees_review_round():
    # Baidu: the multi-year total with the dates LAST, then a per-function breakdown (R&D first): the total wins
    bidu = ("Employees\nWe had approximately 39,800, 35,900 and 33,500 full time employees as of December 31, 2023, 2024 and 2025, respectively. As of December 31, 2025, "
            "we had approximately 18,600 employees in research and development, 6,400 employees in sales and marketing, 5,600 employees in operation and service, and 2,900 "
            "employees in management and administration.")
    r = P.extract_employees(bidu, entity="Baidu, Inc.")
    check(r and r["count"] == 33500 and r["as_of"] == "2025-12-31" and r["evidence"].startswith("We had approximately 39,800, 35,900 and 33,500"), f"employees BIDU total over the R&D subset: {r}")
    notes = []
    r = P.extract_employees(bidu.split(". ", 1)[1], entity="Baidu, Inc.", notes=notes)
    check(r is None and notes and "breakdown" in notes[0] and "18,600 employees in research and development" in notes[0], f"employees BIDU breakdown alone -> None with evidence: {r} {notes}")
    # "the Company and its subsidiaries had / employed N" (United Airlines, Yum! Brands)
    ual = "Human Capital\nAs of December 31, 2025, the Company and its subsidiaries had approximately 113,200 employees, of whom approximately 83% were represented by various U.S. labor organizations."
    r = P.extract_employees(ual, entity="United Airlines Holdings, Inc.")
    check(r and r["count"] == 113200 and r["as_of"] == "2025-12-31" and r["evidence"].endswith("various U.S. labor organizations."), f"employees UAL 'the Company and its subsidiaries had': {r}")
    yum = "Employees\nAs of December 31, 2025, the Company and its subsidiaries employed approximately 49,000 persons (collectively referred to as “our employees”), including approximately 28,000 employees in the U.S."
    r = P.extract_employees(yum, entity="YUM BRANDS INC")
    check(r and r["count"] == 49000, f"employees YUM 'the Company and its subsidiaries employed': {r}")
    # a trailing "as of <date>" keeps the whole sentence as evidence and the right basis (Northern Trust, The Hartford)
    ntrs = "Human Capital\nNorthern Trust employed approximately 23,800 full-time equivalent employees as of December 31, 2025."
    r = P.extract_employees(ntrs, entity="NORTHERN TRUST CORP")
    check(r and r["count"] == 23800 and r["as_of"] == "2025-12-31" and r["evidence"] == ntrs.split("\n")[1] and r.get("basis") == "full-time equivalent as of the stated date", f"employees NTRS trailing as-of: {r}")
    hig = "Human Capital Resources\nThe Hartford has approximately 19,200 employees as of December 31, 2025. Our people are key."
    r = P.extract_employees(hig, entity="HARTFORD INSURANCE GROUP, INC.")
    check(r and r["count"] == 19200 and r["evidence"] == "The Hartford has approximately 19,200 employees as of December 31, 2025." and "basis" not in r, f"employees HIG trailing as-of: {r}")
    # multi-year sentence in DESCENDING order (Estée Lauder): the current year's count, not the prior year's
    el = ("Employees\nAs of June 30, 2026 and 2025, we had approximately 55,000 and 57,000 employees worldwide, respectively, including approximately 35,000 demonstrators "
          "at points of sale who are employed by us as of June 30, 2026 and 2025.")
    r = P.extract_employees(el, entity="ESTEE LAUDER COMPANIES INC")
    check(r and r["count"] == 55000 and r["as_of"] == "2026-06-30", f"employees EL descending years: {r}")
    # a per-location breakdown whose later counts omit the noun is not the total
    notes = []
    r = P.extract_employees("Human Capital\nAs of December 31, 2025, we had 12,000 employees in the United States, 3,000 in Europe and 1,500 in Asia.", entity="WIDGET CORP", notes=notes)
    check(r is None and notes and "breakdown" in notes[0], f"employees breakdown without repeated noun: {r} {notes}")
    # the registrant's count and a subsidiary's in one sentence, no total (PG&E) -> None with the sentence
    notes = []
    r = P.extract_employees("Human Capital\nAs of December 31, 2025, PG&E Corporation had 10 employees, and the Utility had approximately 29,000 regular employees.", entity="PG&E Corp", notes=notes)
    check(r is None and notes and "separate headcounts" in notes[0], f"employees PCG registrant + utility: {r} {notes}")
    # totals listed with their parts stay the total (Waste Connections, Kroger-style consolidated, Cboe's table lead-in)
    wcn = ("Human Capital\nAs of December 31, 2025, Waste Connections employed approximately 24,214 active employees, including 11,347 commercial truck drivers and 2,020 mechanics, "
           "with 20,471 employees in the U.S. and 3,743 in Canada.")
    check((P.extract_employees(wcn, entity="WASTE CONNECTIONS, INC.") or {}).get("count") == 24214, "employees WCN total with its parts")
    kmb = "Employees\nAs of December 31, 2025, we had approximately 36,000 employees in our consolidated operations, including employees of our IFP Business."
    check((P.extract_employees(kmb) or {}).get("count") == 36000, "employees 'in our consolidated operations' is the whole workforce")
    cboe = "Human Capital\nAs of December 31, 2025, we employed 1,661 individuals in the following locations:\nLocation\nNumber of Employees\nUnited States\n1,102"
    r = P.extract_employees(cboe)
    check(r and r["count"] == 1661 and r["evidence"] == "As of December 31, 2025, we employed 1,661 individuals in the following locations:", f"employees CBOE table lead-in: {r}")
    r = P.extract_employees("Human Capital\nAs of December 31, 2025, we had 46,000 employees, compared with 45,000 employees at December 31, 2024.")
    check(r and r["count"] == 46000, f"employees prior-year comparison is not a breakdown: {r}")
    # more phrasings: "N employees at <date>" (EchoStar), "we directly employ" (Coupang), "our total workforce consisted of"
    # (Teledyne), "we have a team of" (Expedia), "<Name> team consisted of ... team members at" (Steel Dynamics),
    # "We ended the year 2025 with N" (Diamondback, dated by the fiscal period end), "employed N individuals" (W. R. Berkley)
    for src, n, d in (("We had approximately 12,100 employees at December 31, 2025, the majority of whom were located in the United States.", 12100, "2025-12-31"),
                      ("As of December 31, 2025, we directly employ approximately 108,000 employees, the majority of which are located in Korea.", 108000, "2025-12-31"),
                      ("At December 28, 2025, our total workforce consisted of approximately 15,800 employees in 38 countries.", 15800, "2025-12-28"),
                      ("As of December 31, 2025, we have a team of approximately 16,000 employees across nearly 50 countries.", 16000, "2025-12-31"),
                      ("The Steel Dynamics team consisted of approximately 14,400 full-time team members at December 31, 2025.", 14400, "2025-12-31"),
                      ("As of January 15, 2026, we employed 8,804 individuals.", 8804, "2026-01-15")):
        r = P.extract_employees("Human Capital\n" + src, entity="STEEL DYNAMICS INC" if "Steel" in src else "WIDGET CORP")
        check(r and r["count"] == n and r["as_of"] == d and r["evidence"] == src, f"employees phrasing {src[:45]!r}: {r}")
    r = P.extract_employees("Human Capital\nWe ended the year 2025 with 1,762 full-time employees.", period="2025-12-31", entity="Diamondback Energy, Inc.")
    check(r and r["count"] == 1762 and r["as_of"] == "2025-12-31" and "year-end" in r.get("basis", ""), f"employees 'ended the year 2025 with': {r}")
    check(P.extract_employees("As of December 31, 2025, we had 50,000 individuals using our platform.") is None, "employees: 'individuals' without 'employ' is not a headcount")
    # the latest date wins over an earlier-positioned prior-year sentence
    r = P.extract_employees("Human Capital\nAs of December 31, 2024, we had 900 employees. As of December 31, 2025, we had 1,100 employees.")
    check(r and r["count"] == 1100 and r["as_of"] == "2025-12-31", f"employees latest date wins: {r}")
    # the evidence ends at the real sentence end after "U.S." ("... outside of the U.S. None of our ...")
    alny = "Human Capital\nAs of December 31, 2025, we employed approximately 2,500 full-time employees, of whom approximately 1,945 were employed in the U.S. None of our employees are unionized."
    r = P.extract_employees(alny)
    check(r and r["evidence"].endswith("were employed in the U.S."), f"employees evidence stops after 'U.S.' + capital: {r}")


def test_item1_preamble_round():
    # Yum! Brands: a whole paragraph of definitions / address / phone / website above "Overview of Business"; the
    # description is the business prose under that sub-heading, not the preamble ("Yum!" must not split a sentence)
    yum_pre = ("Yum! Brands, Inc. (referred to herein as “YUM”, the “Registrant” or the “Company”), was incorporated under the laws of the state of North Carolina in 1997. "
               "The principal executive offices of YUM are located at 1441 Gardiner Lane, Louisville, Kentucky 40213, and the telephone number at that location is (502) 874-8300. "
               "Our website address is https://www.yum.com. YUM, together with its subsidiaries, is referred to in this Form 10-K annual report (“Form 10-K”) as the Company. "
               "The terms “we,” “us” and “our” are also used in the Form 10-K to refer to the Company. Throughout this Form 10-K, the terms “restaurants,” “stores” and “units” "
               "are used interchangeably. While YUM does not directly own or operate any restaurants, throughout this document we may refer to restaurants that are owned or "
               "operated by our subsidiaries as being Company-owned.")
    yum_body = ("YUM has over 63,000 restaurants in 155 countries and territories primarily operating under the four concepts of KFC, Taco Bell, Pizza Hut and Habit Burger & Grill. "
                "The Company’s KFC, Taco Bell and Pizza Hut brands are global leaders of the chicken, Mexican-inspired food and pizza categories, respectively.")
    d, n = P.extract_item1("PART I\nItem 1. Business.\n" + yum_pre + "\nOverview of Business\n" + yum_body + "\nItem 1A. Risk Factors\nRisks.", "10-K")
    check(d == yum_body and n == "10-K Item 1 Business", f"item1 YUM preamble skipped: {(d or '')[:90]!r} / {n}")
    # Arch Capital: definitions + "All amounts are in millions" + "We refer you to Item 1A" above "OUR COMPANY / General"
    acgl_pre = ("As used in this report, references to “we,” “us,” “our,” “Arch” or the “Company” refer to the consolidated operations of Arch Capital Group Ltd. "
                "(“Arch Capital”) and its subsidiaries. All amounts are in millions, except per share amounts, unless otherwise noted. We refer you to Item 1A “Risk Factors” "
                "for a discussion of risk factors relating to our business.")
    acgl_body = ("Arch Capital is a publicly listed Bermuda exempted company with approximately $26.9 billion in capital at December 31, 2025 and is part of the S&P 500 index. "
                 "Arch provides insurance, reinsurance and mortgage insurance on a worldwide basis through its wholly owned subsidiaries.")
    d, _ = P.extract_item1("Item 1. Business\n" + acgl_pre + "\nOUR COMPANY\nGeneral\n" + acgl_body + "\nItem 1A. Risk Factors\nRisks.", "10-K")
    check(d == acgl_body, f"item1 ACGL preamble skipped: {(d or '')[:90]!r}")
    # the definitions sentence and the prose on ONE line (Old Dominion): only the leading sentence goes; "Inc. We" splits
    odfl = ("Unless the context requires otherwise, references in this report to “Old Dominion,” the “Company,” “we,” “us” and “our” refer to Old Dominion Freight Line, Inc. "
            "We are one of the largest North American less-than-truckload motor carriers. We provide regional, inter-regional and national LTL services through a single "
            "integrated, union-free organization.")
    d, _ = P.extract_item1("Item 1. Business\n" + odfl + "\nItem 1A. Risk Factors\nRisks.", "10-K")
    check(d is not None and d.startswith("We are one of the largest North American") and d.endswith("union-free organization."), f"item1 ODFL same-line preamble: {(d or '')[:90]!r}")
    # Con Edison: the business sentence first ("Inc. (CECONY)" does not split it), a trailing definition that does not
    # count toward min_prose, then sub-headings (dropped) and the rest of the opening prose
    ed1 = ("Consolidated Edison, Inc. (Con Edison), incorporated in New York State in 1997, is a holding company that owns all of the outstanding common stock of "
           "Consolidated Edison Company of New York, Inc. (CECONY) and Orange and Rockland Utilities, Inc. (O&R). As used in this report, the term the “Utilities” refers to CECONY and O&R.")
    ed2 = "Con Edison’s principal business operations are those of CECONY, O&R and Con Edison Transmission. CECONY’s principal business operations are its regulated delivery businesses."
    d, _ = P.extract_item1("Item 1: Business\nOverview\n" + ed1 + "\nCon Edison\nCECONY\n" + ed2 + "\nItem 1A: Risk Factors\nRisks.", "10-K")
    check(d == ed1 + " " + ed2, f"item1 ED trailing definition + sub-headings: {(d or '')[-120:]!r}")
    # "Inc. (Acme)" and "U.S. market" do not split; "Inc. Was" does, and the two-word fragment "Acme Inc." joins the next
    sents = P._sentences("Acme Inc. (Acme) makes widgets in the U.S. market today. Acme Inc. Was founded in 1990.")
    check(sents == ["Acme Inc. (Acme) makes widgets in the U.S. market today.", "Acme Inc. Was founded in 1990."], f"item1 _sentences abbreviations: {sents}")
    # only preamble under the heading, then the next item: no description (never the preamble itself)
    d, n = P.extract_item1("Item 1. Business\n" + acgl_pre + "\nItem 1A. Risk Factors\nRisks.", "10-K")
    check(d is None, f"item1 preamble-only section -> None: {d!r}")


def test_employees_breakdown_round():
    W = dict(period="2025-12-31", entity="WIDGET CORP")
    # a per-type / per-location split with the noun repeated and no total: never the first part
    for s in ("As of December 31, 2025, we had 17,550 full-time employees and 2,045 part-time employees.",
              "As of December 31, 2025, we had approximately 4,000 salaried employees and 6,000 hourly employees.",
              "As of December 31, 2025, we employed 9,800 full-time employees and 1,400 part-time employees.",
              "As of December 31, 2025, we had 2,000 employees domestically and 500 employees internationally.",
              "As of December 31, 2025, we had approximately 1,100 employees in the United States and approximately 300 employees internationally.",
              "As of December 31, 2025, we had approximately 1,100 employees in the United States and approximately 300 employees outside the United States.",
              "As of December 31, 2025, we had 17,550 full-time and 2,045 part-time employees."):
        notes = []
        r = P.extract_employees("Human Capital\n" + s, notes=notes, **W)
        check(r is None and (notes and "breakdown" in notes[0] or "full-time and" in s), f"employees breakdown -> None: {s[45:110]!r}: {r} {notes}")
    # onsemi writes "full‑time" with U+2011: html_to_text makes it a hyphen, and the split is still a breakdown
    on = P.html_to_text("<p>Human Capital</p><p>As of December 31, 2025, we had approximately 22,600 regular full&#8209;time employees and about 70 part&#8209;time or temporary employees across 33 countries.</p>")
    check("full-time" in on, "html_to_text: U+2011 -> '-'")
    notes = []
    r = P.extract_employees(on, notes=notes, **W)
    check(r is None and notes and "breakdown" in notes[0], f"employees onsemi U+2011 breakdown: {r} {notes}")
    # still the total: contractors are not employees; a first count said to be the whole; a total with "including" /
    # "excluding"; a prior-year comparison
    for s, n in (("As of December 31, 2025, we had 1,234 employees and 5,678 independent contractors.", 1234),
                 ("As of December 31, 2025, Widget employed 130,301 people worldwide and 1,233 contract workers.", 130301),
                 ("As of December 31, 2025, we have approximately 11,100 employees around the globe, including 11,000 full-time employees.", 11100),
                 ("As of December 31, 2025, we had 52,000 employees, excluding the 8,000 employees of our joint ventures.", 52000),
                 ("As of December 31, 2025, we had approximately 900 employees, compared to approximately 1,100 employees as of December 31, 2024.", 900)):
        r = P.extract_employees("Human Capital\n" + s, **W)
        check(r and r["count"] == n, f"employees total kept: {s[45:110]!r}: {r}")
    # a later-dated count of people elsewhere in the 10-K never beats the headcount under Human Capital
    hc = "Human Capital\nAs of December 31, 2025, we had approximately 4,200 employees."
    for lead in ("As of February 15, 2026, we had approximately 850,000 people enrolled in our weight-management programs.",
                 "As of February 15, 2026, we had approximately 850,000 people.",
                 "As of February 15, 2026, we had 14 persons serving as executive officers."):
        r = P.extract_employees("Item 1. Business\nOverview\n" + lead + "\n" + hc, entity="ACME CORP")
        check(r and r["count"] == 4200 and r["as_of"] == "2025-12-31", f"employees not a headcount ({lead[33:80]!r}): {r}")
    check(P.extract_employees("Human Capital\nAs of December 31, 2025, we had 14 persons serving as executive officers.", **W) is None,
          "employees: persons serving as executive officers")
    # ranking: proximity to the Human Capital passage comes before the date
    r = P.extract_employees("Item 7. Management's Discussion\nAs of March 1, 2026, we had approximately 5,000 employees.\n" + hc, entity="ACME CORP")
    check(r and r["count"] == 4200, f"employees: the Human Capital count outranks a later-dated count elsewhere: {r}")
    # "Sept." is September; an impossible date is never published as a raw as-of
    r = P.extract_employees("Human Capital\nAs of Sept. 30, 2025, we had approximately 3,000 employees.", **W)
    check(r and r["as_of"] == "2025-09-30" and "basis" not in r, f"employees 'Sept.' date: {r}")
    check(P.iso_from_text_date("Sept. 30, 2025") == "2025-09-30" and P.iso_from_text_date("30 Sept 2025") == "2025-09-30", "iso_from_text_date Sept")
    notes = []
    r = P.extract_employees("Human Capital\nOn February 30, 2026, we had 3,000 employees.", notes=notes, **W)
    check(r is None and notes and "cannot be read" in notes[0], f"employees impossible date -> None: {r} {notes}")
    r = P.extract_employees("Human Capital\nAs of Sept 30, 2025 and 2024, we had 3,000 and 2,900 employees, respectively.", **W)
    check(r and r["count"] == 3000 and r["as_of"] == "2025-09-30", f"employees multi-year 'Sept': {r}")
    notes = []
    r = P.extract_employees("Human Capital\nAs of February 29, 2024 and 2025, we had 3,000 and 2,900 employees, respectively.", notes=notes, **W)
    check(r is None and notes and "cannot be read" in notes[0], f"employees multi-year Feb 29 in a non-leap latest year: {r} {notes}")


def test_hq_and_forms_review_round():
    def sub(city):
        return {"addresses": {"business": {"city": city, "stateOrCountryDescription": "F4"}}}

    def cov(city, state=None, country=None):
        return {"street": None, "city": city, "state": state, "zip": None, "country": country, "source": "annual filing cover"}
    hq, addr = P.headquarters(sub("BEIJING"), cov("Haidian District", country="The People's Republic of China"))
    check(hq == "Haidian District, Beijing, The People's Republic of China" and addr["city"] == "Haidian District" and addr["metro"] == "Beijing"
          and addr["metro_source"] == "EDGAR submissions", f"hq foreign district (Baidu): {hq} {addr}")
    check(P.headquarters(sub("DAXING DISTRICT, BEIJING"), cov("Daxing District", country="People's Republic of China"))[0] == "Daxing District, Beijing, People's Republic of China", "hq JD")
    check(P.headquarters(sub("TOKYO"), cov("Chuo-ku", country="Japan"))[0] == "Chuo-ku, Tokyo, Japan", "hq Nomura")
    check(P.headquarters(sub("SANDTON"), cov("Sandton", country="South Africa"))[0] == "Sandton, South Africa", "hq same city adds nothing")
    check(P.headquarters(sub("SANTA CLARA"), cov("San Jose", state="California"))[0] == "San Jose, California", "hq domestic cover never borrows the submissions city")
    hq, addr = P.headquarters(sub("ST. JOHN'S"), cov("St. John'", state="Newfoundland and Labrador"))
    check(hq == "St. John's, Newfoundland and Labrador" and "incomplete" in addr.get("city_source", ""), f"hq truncated cover city tag (Fortis): {hq} {addr}")
    check(P.headquarters(sub("GOODLETTSVILLE"), cov("GOODLETTSVILLE", state="TN"))[0] == "Goodlettsville, TN", "hq all-caps cover city")
    check(P.headquarters(sub("MCLEAN"))[0] == "McLean, F4" and P.headquarters(sub("ST. LOUIS"))[0] == "St. Louis, F4", "hq submissions title case")
    # EDGAR's 1990s spellings: "10QSB" is the periodic 10-QSB (Take-Two's earliest row), so a later 8-A is not the proxy
    rows = {"filings": {"recent": {"form": ["8-A12B", "10QSB"], "filingDate": ["1998-01-01", "1997-06-16"]}, "files": []}}
    check(P.first_filing(rows) == ("1997-06-16", "10QSB"), f"first_filing 10QSB spelling {P.first_filing(rows)}")
    for f in ("10KSB", "10-KT", "10-QT", "10-KSB405", "10-QSB/A"):
        check(P._form_key(f) in P.PERIODIC_KEYS, f"periodic form spelling {f}")


def test_build_unresolved_employees():
    """build() with the network stubbed: only a per-location headcount is filed -> about.employees null, the sentence kept
    in about.employees_unresolved and in a warning; every Nasdaq endpoint failing leaves street / market null."""
    doc = (b"<html><body><div>PART I</div><div>Item 1. Business</div><div>Widget Corp makes widgets for industrial customers in many markets, and it sells them "
           b"through distributors. It was founded in 1950 and is headquartered in Ohio.</div><div>Human Capital</div><div>As of December 31, 2025, we employed "
           b"11,172 people in the United States.</div><div>Item 1A. Risk Factors</div></body></html>")
    sub = dict(SUB, filings={"recent": {"form": ["10-K"], "filingDate": ["2026-02-19"], "reportDate": ["2025-12-31"], "items": [""],
                                        "accessionNumber": ["0000000001-26-000001"], "primaryDocument": ["w-20251231.htm"], "primaryDocDescription": [""]}, "files": []})
    saved = (P.get_bytes, P.nasdaq_json, P.ZoneInfo)

    def fake_get(url, headers, timeout):
        assert "sec.gov" in url, url
        return doc

    def no_nasdaq(url):
        raise OSError("offline test")
    try:
        # a fixed UTC-5 zone: the test needs no tzdata (python -I has no site-packages)
        P.get_bytes, P.nasdaq_json, P.ZoneInfo = fake_get, no_nasdaq, (lambda key: datetime.timezone(datetime.timedelta(hours=-5)))
        p = P.build("WID", 123, quiet=True, sub=sub)
    finally:
        P.get_bytes, P.nasdaq_json, P.ZoneInfo = saved
    a = p["about"]
    check(a["employees"] is None, f"build: employees must be null, got {a['employees']}")
    u = a.get("employees_unresolved") or {}
    check(u.get("count") is None and u.get("evidence") == "As of December 31, 2025, we employed 11,172 people in the United States." and "location" in u.get("reason", "")
          and u.get("form") == "10-K", f"build: employees_unresolved {u}")
    check(any(w.startswith("employees: null - ") and "11,172 people in the United States" in w for w in p["warnings"]), f"build: warning {p['warnings']}")
    check(a["description"] and a["description"]["text"].startswith("Widget Corp makes widgets"), f"build: description {a['description']}")
    check(p["street"] is None and p["market"] is None, "build: Nasdaq offline -> street / market null")


if __name__ == "__main__":
    for fn in (test_item1, test_item1_review_round, test_employees, test_employees_review_round, test_items_and_feed, test_skip_rule,
               test_street, test_first_filing, test_helpers, test_hq_and_forms_review_round, test_build_unresolved_employees,
               test_item1_preamble_round, test_employees_breakdown_round):
        fn()
    if FAILS:
        print(f"{len(FAILS)} failure(s)")
        sys.exit(1)
    print("test_profile: all checks passed")
