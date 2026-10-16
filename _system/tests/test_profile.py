#!/usr/bin/env python3
"""profile.py tests (v5.5). Run: python3 _system/tests/test_profile.py
(or python3 -m pytest _system/tests). No network, and nothing written in the
repository: every case is a pure function on an inline fixture, except the
split tests (10), which stub the network and write into a temporary folder.
No test needs a gitignored cache (prices / live / street.json) to exist.

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
4. The refresh policy (split 2026-10-16): profile.json is rebuilt only when
   missing, pre-split (still carries street / market), its
   newest_filing_date (feed forms only; a Form 4 does not count) or its
   feed's accession numbers changed, its last build was degraded (FAILED
   source, unreadable annual document or submissions page; a deterministic
   extraction outcome is not), or --force — never for age; street.json is
   re-fetched when missing, unreadable, --max-age-days or more old,
   degraded (a FAILED endpoint, not a Nasdaq placeholder), or --force.
5. Street block assembly from the verified endpoint shapes (history oldest
   first with ISO dates, surprise_pct = (actual - consensus) / |consensus| *
   100 so a beat on a negative consensus is positive, momentum, next earnings
   date, PEG), partial failure (targetprice only), Nasdaq's placeholders (999
   means -> null, 0/0 EPS rows dropped, warnings), and the market block with
   Nasdaq's text dividend dates ("Sep 17, 2026" -> ISO).
6. first_filing: the earliest registration / listing form (APP's real
   sequence D, DRS, DRSLTR, S-1, 424B4 -> the S-1) unless a periodic report
   precedes it (Kroger -> the 1994 10-K405); paginated files fetched oldest
   first with an injected fetcher and stopped only once the earliest
   registration or periodic report seen predates every unread page (review
   finding 4289642905: a recent resale S-1 must not stop the search before
   the page holding the IPO S-1; overlapping pages and a page without
   filingFrom are read; a pre-EDGAR company with a recent 8-A12B stops
   after its oldest page), and on 3,000 random histories the paginated
   answer equals the answer from every row at once.
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
10. The profile.json / street.json split, with the network stubbed and
   STOCKS_BASE pointed at a temporary folder: profile.json has no street /
   market and is written through _stable (indent 1, raw UTF-8); a second
   run whose only differences are as_of / fetched_at and the volatile quote
   figures (price, volume, market cap, 1y target) leaves it byte-identical
   with the same mtime, while street.json is rewritten in the agreed format;
   a new feed filing rewrites profile.json; a pre-split file is migrated;
   an EDGAR failure still refreshes street.json (exit 3); --all rebuilds
   and re-fetches per the policy with the exact request counts (the quote
   summary read once per name), and --street-only makes no EDGAR request.
   Verifier round: a second feed filing on the same filingDate rebuilds
   profile.json (accession numbers compared); a degraded build (Nasdaq
   About endpoints down, the annual document timing out) is retried by the
   next --all and heals, a persisting failure leaves the file untouched,
   and a degraded street.json is re-fetched; a Windows PermissionError on
   the swap (a real reader holding the file open) is retried, a write that
   still fails costs only that file (exit 5), and an exception in one name
   never aborts --all.
11. Parse error vs unreadable: a timeout, an undecodable body or no body is
   "annual document unreadable" (degraded, retried); an extractor raising
   (cover_address, html_to_text, extract_item1, extract_employees, each
   monkeypatched) is "annual document parse error (TypeError: ...) in
   <extractor>", nulls only that extractor's fields, prints the traceback,
   is not degraded (rebuilt on a feed change or --force only), exits 6 from
   run_one with both files still written, is a failure line in the --all
   summary, and the next --all does not re-download the document.
12. Corrupt files under --all: a profile.json / street.json with fields of
   the wrong type, or a CIK that is not an integer, is one name's failure
   line naming the file; the other file of that name is still refreshed,
   the walk goes on, and a single-name run heals it.
13. --street-only with the transport (urllib) stubbed: zero EDGAR requests
   for --all and for one ticker; the CIK from profile.json first, then
   dcf_numbers.json / fundamentals.json, then the local ticker maps; the
   street.json age / degraded policy with --max-age-days; profile.json
   never written; the same stub sees a full run's EDGAR requests.
14. Every text-mode open() in profile.py names encoding="utf-8" (AST scan).
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
    # the newest filing of a form profile.json reflects: SUB's newest row is a Form 4 (2026-08-21), which changes nothing in
    # the file, so the rebuild key is the 8-K of 2026-08-05 (= the feed's first row)
    check(P.newest_filing_date(SUB) == "2026-08-05" == feed[0]["filed"], f"newest_filing_date ignores the Form 4: {P.newest_filing_date(SUB)}")
    check(P.newest_filing_date(_sub_rows([("4", "2026-09-01"), ("10-Q/A", "2026-08-10"), ("144", "2026-09-02")])) == "2026-08-10", "newest_filing_date counts feed-form amendments")
    check(P.newest_filing_date(_sub_rows([("4", "2026-09-01")])) is None and P.newest_filing_date({}) is None, "newest_filing_date without a feed form -> None")
    la = P.latest_annual(SUB, 1751008)
    check(la and la["form"] == "10-K" and la["filed"] == "2026-02-19" and la["url"].endswith("app-20251231.htm"), f"latest_annual {la}")
    hq, addr = P.headquarters(SUB)
    check(hq == "Palo Alto, CA" and addr["street"] == "1 MAIN ST" and addr["zip"] == "94304" and addr["source"] == "EDGAR submissions", f"headquarters {hq} {addr}")


# ---------------------------------------------------------------------------
# 4. refresh policy: profile.json on a new filing (never for age), street.json on age
def test_skip_rule():
    today = datetime.date(2026, 10, 14)
    prof = {"as_of": "2026-01-02", "newest_filing_date": "2026-08-21", "about": {}}
    R = P.profile_rebuild_reason
    check(R(prof, "2026-08-21") is None, "profile: unchanged newest filing -> left alone, however old its as_of")
    check(R(prof, "2026-10-13") == "new filing 2026-10-13", f"profile: a newer filing rebuilds: {R(prof, '2026-10-13')}")
    check(R(prof, None) is None, "profile: no feed-form filing in the submissions -> left alone")
    check(R(None, "2026-08-21") == "missing" and R({"as_of": "2026-10-12"}, "2026-08-21") == "missing" and R([], "2026-08-21") == "missing",
          "profile: a missing or unreadable file (no about object) is built")
    check(R(dict(prof, street=None, market=None), "2026-08-21") == "legacy file with street / market", "profile: a pre-split file (street / market keys, even null) is rebuilt")
    check(R(dict(prof, market={"volume": 1}), "2026-08-21") is not None, "profile: a pre-split file with market only is rebuilt")
    check(R(prof, "2026-08-21", force=True) == "--force", "profile: --force rebuilds")
    S = P.street_refresh_reason
    check(S({"as_of": "2026-10-12"}, 7, today) is None, "street: 2 days old is fresh")
    check(S({"as_of": "2026-10-08"}, 7, today) is None, "street: 6 days old is fresh")
    check(S({"as_of": "2026-10-07"}, 7, today) == "7 days old", "street: exactly max-age days old is re-fetched")
    check(S({"as_of": "2026-10-12"}, 1, today) == "2 days old", "street: --max-age-days 1 re-fetches a 2-day-old file")
    check(S(None, 7, today) == "missing" and S([1], 7, today) == "missing", "street: missing / malformed file is fetched")
    check(S({"as_of": "garbage"}, 7, today) == "unreadable as_of" and S({}, 7, today) == "unreadable as_of", "street: unreadable as_of is fetched")
    check(S({"as_of": "2026-10-14"}, 7, today, force=True) == "--force", "street: --force re-fetches")

    # verifier round: the feed's accession numbers (a second filing on the same filingDate), degraded builds
    feed = [{"form": "8-K", "filed": "2026-08-21", "accession": "a1"}, {"form": "10-K", "filed": "2026-02-19", "accession": "a0"}]
    fprof = dict(prof, filings=feed)
    same_day = [{"form": "10-Q", "filed": "2026-08-21", "accession": "a2"}] + feed
    check(R(fprof, "2026-08-21", feed=feed) is None, "profile: same feed -> left alone")
    check(R(fprof, "2026-08-21", feed=same_day) == "new filing 10-Q 2026-08-21 (a2)", f"profile: a same-day second filing rebuilds: {R(fprof, '2026-08-21', feed=same_day)}")
    check(R(fprof, "2026-08-21", feed=feed[:1]) == "filing feed changed", "profile: a feed that lost a filing rebuilds")
    check(R(fprof, "2026-08-21") is None, "profile: no feed given -> only newest_filing_date is compared")
    bad_nq = dict(fprof, sources={"edgar_submissions": "u", "nasdaq_company_profile": "FAILED: u", "nasdaq_summary": "FAILED: v"})
    check(R(bad_nq, "2026-08-21", feed=feed) == "last build degraded (nasdaq_company_profile, nasdaq_summary)", f"profile: a Nasdaq failure is retried: {R(bad_nq, '2026-08-21', feed=feed)}")
    bad_doc = dict(fprof, warnings=["annual document unreadable (timed out); description and employees null"])
    check(R(bad_doc, "2026-08-21", feed=feed) == "last build degraded (annual document unreadable)", "profile: an unreadable annual document is retried")
    bad_page = dict(fprof, warnings=["submissions page CIK0000123-submissions-001.json unreadable (HTTP 503); first filing date from the other pages only"])
    check(R(bad_page, "2026-08-21", feed=feed) == "last build degraded (submissions page CIK0000123-submissions-001.json unreadable)", "profile: an unreadable submissions page is retried")
    settled = dict(fprof, warnings=["employees: no headcount sentence found in the 10-K filed 2026-02-19", "description: no 10-K Item 1 Business section found outside the table of contents (10-K filed 2026-02-19)",
                                    "no 10-K / 20-F / 40-F in the recent submissions; description and employees null"])
    check(R(settled, "2026-08-21", feed=feed) is None, "profile: a deterministic extraction outcome is not a failure (no retry)")
    check(S({"as_of": "2026-10-12", "sources": {"nasdaq_ratings": "FAILED: u", "nasdaq_summary": "u"}}, 7, today) == "last pull degraded (nasdaq_ratings)",
          "street: a pull with a failed endpoint is re-fetched on the next run")
    check(S({"as_of": "2026-10-12", "sources": {"nasdaq_ratings": "u"}, "warnings": ["street: estimate-momentum published 999 (no estimate) for some means; those are null"]}, 7, today) is None,
          "street: Nasdaq placeholders are not a failure")


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
    # the oldest page's 10-K405 predates the other page's filingFrom: that settles the answer after one page
    check(P.first_filing(old, fetch=fetch_old) == ("1996-03-01", "10-K405") and calls == ["https://data.sec.gov/submissions/CIK-003.json"], f"first_filing: a periodic report on the oldest page settles it {calls}")
    calls.clear()

    def fetch_undecided(url):
        calls.append(url)
        return {"form": ["SC 13G", "D"], "filingDate": ["1996-03-01", "1996-04-01"]} if url.endswith("003.json") else {"form": ["10-Q"], "filingDate": ["2011-02-01"]}
    check(P.first_filing(old, fetch=fetch_undecided) == ("1996-03-01", "SC 13G") and calls == ["https://data.sec.gov/submissions/CIK-003.json", "https://data.sec.gov/submissions/CIK-001.json"],
          f"first_filing: every page when no registration or periodic report settles it {calls}")

    def boom(url):
        raise OSError("down")
    w = []
    check(P.first_filing(paged, fetch=boom, warnings=w) == ("2009-01-01", None) and len(w) == 2, f"first_filing: unreadable pages fall back to filingFrom with a warning {w}")

    # review finding 4289642905: `recent` already holds a registration (a 2025 resale S-1); the oldest page holds only the
    # Form D and the DRS drafts and the next page the IPO S-1. The search must not stop after the first page because of the
    # recent S-1: it reads on until the earliest registration seen predates every unread page (page C starts 2021-06-01).
    pages = {"CIK-A.json": {"form": ["D", "DRS", "DRSLTR"], "filingDate": ["2018-08-24", "2020-12-07", "2021-01-15"]},
             "CIK-B.json": {"form": ["S-1", "S-1/A", "424B4", "10-Q"], "filingDate": ["2021-03-02", "2021-03-22", "2021-04-15", "2021-05-15"]},
             "CIK-C.json": {"form": ["10-Q", "8-K", "10-K"], "filingDate": ["2021-08-01", "2022-02-01", "2023-02-28"]}}
    calls.clear()

    def fetch_pages(url):
        calls.append(url.rsplit("/", 1)[1])
        return pages[url.rsplit("/", 1)[1]]
    recent_reg = _sub_rows([("10-K", "2026-02-01"), ("S-1", "2025-06-01")], files=[
        {"name": "CIK-C.json", "filingFrom": "2021-06-01", "filingTo": "2024-12-31"},
        {"name": "CIK-A.json", "filingFrom": "2018-08-24", "filingTo": "2021-01-15"},
        {"name": "CIK-B.json", "filingFrom": "2021-03-02", "filingTo": "2021-05-31"}])
    r = P.first_filing(recent_reg, fetch=fetch_pages)
    check(r == ("2021-03-02", "S-1") and calls == ["CIK-A.json", "CIK-B.json"], f"first_filing: a recent registration does not stop the search early: {r} {calls}")
    # a periodic report on the oldest page, older than every unread page, settles the answer (the earliest filing): no
    # later page can hold an earlier registration or an earlier filing, so the search stops after that page
    calls.clear()
    pages["CIK-A.json"] = {"form": ["10-K405", "D"], "filingDate": ["2017-03-01", "2018-08-24"]}
    r = P.first_filing(recent_reg, fetch=fetch_pages)
    check(r == ("2017-03-01", "10-K405") and calls == ["CIK-A.json"], f"first_filing: periodic before the IPO page: {r} {calls}")
    # overlapping pages: a registration on the oldest page does not end the search while a later-listed page starts
    # before it (EDGAR's pages are date ranges, not a strict partition)
    calls.clear()
    pages.update({"CIK-X.json": {"form": ["D", "S-1"], "filingDate": ["2009-01-01", "2010-06-01"]},
                  "CIK-Y.json": {"form": ["F-1", "6-K"], "filingDate": ["2010-02-01", "2010-09-01"]}})
    overlap = _sub_rows([("20-F", "2026-04-01")], files=[{"name": "CIK-Y.json", "filingFrom": "2010-01-01"}, {"name": "CIK-X.json", "filingFrom": "2009-01-01"}])
    r = P.first_filing(overlap, fetch=fetch_pages)
    check(r == ("2010-02-01", "F-1") and calls == ["CIK-X.json", "CIK-Y.json"], f"first_filing: overlapping page read: {r} {calls}")
    # a page without filingFrom has an unknown range: it is read too (last, by the sort)
    calls.clear()
    nofrom = _sub_rows([("10-K", "2026-02-01")], files=[{"name": "CIK-Y.json"}, {"name": "CIK-X.json", "filingFrom": "2009-01-01"}])
    r = P.first_filing(nofrom, fetch=fetch_pages)
    check(r == ("2010-02-01", "F-1") and calls == ["CIK-X.json", "CIK-Y.json"], f"first_filing: page without filingFrom read: {r} {calls}")
    # nothing to read when the registration in hand already predates every page (and the stop is strict: a page that
    # starts ON the registration date is read, it could hold a same-day registration)
    check(P._older_than_unread([("S-1", "2005-01-01")], [{"filingFrom": "2006-01-01"}]) is True, "early stop: registration older than every unread page")
    check(P._older_than_unread([("S-1", "2006-01-01")], [{"filingFrom": "2006-01-01"}]) is False, "early stop is strict")
    check(P._older_than_unread([("10-K", "2005-01-01")], [{"filingFrom": "2006-01-01"}]) is True, "early stop: a periodic report older than every unread page")
    check(P._older_than_unread([("D", "2005-01-01"), ("DRS", "2005-02-01")], [{"filingFrom": "2006-01-01"}]) is False, "early stop needs a registration or a periodic report")
    check(P._older_than_unread([("10-K", "2005-01-01")], [{"filingFrom": "2006-01-01"}, {"name": "x"}]) is False, "early stop: a page without filingFrom is read")
    check(P._older_than_unread([("S-1", "2005-01-01")], []) is True, "early stop: no page left")

    # verifier round: a company public before EDGAR with a recent 8-A12B (an exchange move). The oldest page's 1994 10-K
    # settles the answer; the two later pages are no longer read (the registration-only rule read all three)
    calls.clear()
    pages.update({"CIK-P1.json": {"form": ["10-K", "10-Q"], "filingDate": ["1994-03-01", "1994-05-01"]},
                  "CIK-P2.json": {"form": ["10-Q", "8-K"], "filingDate": ["2001-05-01", "2002-01-01"]},
                  "CIK-P3.json": {"form": ["10-K", "S-3"], "filingDate": ["2010-03-01", "2011-01-01"]}})
    pre = _sub_rows([("10-K", "2026-02-01"), ("8-A12B", "2024-05-01")], files=[
        {"name": "CIK-P3.json", "filingFrom": "2010-03-01"}, {"name": "CIK-P1.json", "filingFrom": "1994-03-01"}, {"name": "CIK-P2.json", "filingFrom": "2001-05-01"}])
    r = P.first_filing(pre, fetch=fetch_pages)
    check(r == ("1994-03-01", "10-K") and calls == ["CIK-P1.json"], f"first_filing: pre-EDGAR company with a recent 8-A12B reads one page: {r} {calls}")

    # exhaustive check of the stop rule: on 3,000 random histories (pages as date ranges, overlapping or not, some without
    # filingFrom; registration / periodic / other forms; registrations among the recent filings) the paginated answer
    # equals the answer computed from every row at once, and no page is read twice
    import random
    rnd = random.Random(4289642905)
    pool = ["S-1", "S-1/A", "424B4", "8-A12B", "F-1", "10-12B", "10-K", "10-Q", "8-K", "10-K405", "6-K", "DEF 14A", "D", "DRS", "SC 13G", "4", "S-8"]
    day0 = datetime.date(1993, 1, 1)
    mism = []
    for case in range(3000):
        def row():
            return (rnd.choice(pool), (day0 + datetime.timedelta(days=rnd.randrange(0, 12000))).isoformat())
        recent = [row() for _ in range(rnd.randrange(0, 6))]
        pg, metas = {}, []
        for k in range(rnd.randrange(0, 5)):
            rows_k = sorted((row() for _ in range(rnd.randrange(1, 6))), key=lambda x: x[1])
            name = f"R{case}-{k}.json"
            pg[name] = {"form": [x[0] for x in rows_k], "filingDate": [x[1] for x in rows_k]}
            meta = {"name": name}
            if rnd.random() > 0.1:
                meta["filingFrom"] = rows_k[0][1]
            metas.append(meta)
        rnd.shuffle(metas)
        read = []

        def fetch_r(url, pg=pg, read=read):
            read.append(url.rsplit("/", 1)[1])
            return pg[url.rsplit("/", 1)[1]]
        got = P.first_filing(_sub_rows(recent, files=metas), fetch=fetch_r)
        # every row, in the order a full read would see them (recent, then the pages oldest first), so that two filings
        # on the same earliest date break the tie the same way
        order = sorted(metas, key=lambda m: m.get("filingFrom") or "9999")
        everything = recent + [(f, d) for m in order for f, d in zip(pg[m["name"]]["form"], pg[m["name"]]["filingDate"])]
        want = P.first_filing(_sub_rows(everything)) if everything else (None, None)
        if got != want or len(read) != len(set(read)):
            mism.append((case, got, want))
    check(not mism, f"first_filing: paginated answer differs from the all-rows answer in {len(mism)} of 3000 random histories: {mism[:3]}")


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
    # profile.json never carries the Street / market blocks (street.json does); the About endpoints' failure is recorded
    check(list(p) == ["ticker", "cik", "as_of", "fetched_at", "newest_filing_date", "sources", "about", "filings", "warnings"], f"build: profile.json keys {list(p)}")
    check(p["sources"].get("nasdaq_company_profile", "").startswith("FAILED: ") and "nasdaq_targetprice" not in p["sources"], f"build: profile sources {p['sources']}")
    check(any(w.startswith("nasdaq company_profile failed (offline test)") for w in p["warnings"]) and not any("street" in w or "market" in w for w in p["warnings"]),
          f"build: profile warnings name the About endpoints only {p['warnings']}")


# ---------------------------------------------------------------------------
# 10. profile.json (committed, rewritten on content change) / street.json (gitignored cache) split
SPLIT_DOC = ('<html><body><div><ix:nonNumeric name="dei:EntityAddressCityOrTown" contextRef="c">Columbus</ix:nonNumeric></div><div>PART I</div><div>Item 1. Business</div><div>Widget Corp makes widgets for industrial customers in many markets, and it sells '
             "them through distributors in the company’s home region. It was founded in 1950 and is headquartered in Ohio.</div><div>Human Capital</div>"
             "<div>As of December 31, 2025, we had approximately 1,900 employees.</div><div>Item 1A. Risk Factors</div></body></html>").encode("utf-8")
NQ_PROFILE = {"CompanyDescription": {"value": "Widgets."}, "Industry": {"value": "Software"}, "Sector": {"value": "Technology"}, "Region": {"value": "North America"}}


def _split_sub(cik, extra_rows=()):
    rows = [("10-K", "2026-02-19", "2025-12-31", "w-20251231.htm"), ("8-K", "2026-08-05", "2026-08-05", "w8k.htm"),
            ("4", "2026-09-30", "", "form4.xml")] + list(extra_rows)
    return dict(SUB, cik=str(cik), filings={"recent": {"form": [r[0] for r in rows], "filingDate": [r[1] for r in rows], "reportDate": [r[2] for r in rows],
                                                       "items": ["2.02" if r[0] == "8-K" else "" for r in rows],
                                                       "accessionNumber": [f"0000{cik}-26-{i:06d}" for i in range(len(rows))],
                                                       "primaryDocument": [r[3] for r in rows], "primaryDocDescription": [""] * len(rows)}, "files": []})


class _Net:
    """The network, stubbed: EDGAR submissions per CIK, the annual document, Nasdaq per endpoint; every request logged."""

    def __init__(self, base):
        self.base, self.subs, self.edgar, self.docs, self.nasdaq = base, {}, [], [], []
        self.summary = json.loads(json.dumps(SUMM))
        self.nasdaq_down, self.edgar_down, self.doc_down = False, False, False

    def edgar_json(self, url):
        self.edgar.append(url)
        if self.edgar_down:
            raise OSError("EDGAR down (test)")
        return self.subs[int(url.split("CIK")[1][:10])]

    def get_bytes(self, url, headers, timeout):
        assert "sec.gov" in url, url
        self.docs.append(url)
        if self.doc_down:
            raise TimeoutError("timed out")
        return SPLIT_DOC

    def nasdaq_json(self, url):
        ticker = url.split("/")[5]
        key = next(k for k, u in P.nasdaq_urls(ticker).items() if u == url)
        self.nasdaq.append(key)
        if self.nasdaq_down:
            raise OSError("Nasdaq down (test)")
        return {"company_profile": NQ_PROFILE, "summary": self.summary, "targetprice": TP, "ratings": RT, "earnings_forecast": FC, "eps": EPS,
                "estimate_momentum": MO, "earnings_date": ED, "peg_ratio": PEG}[key]

    def clear(self):
        self.edgar, self.docs, self.nasdaq = [], [], []

    def __enter__(self):
        self.saved = {k: getattr(P, k) for k in ("BASE", "SYS", "edgar_json", "get_bytes", "nasdaq_json", "ZoneInfo", "ALL_SLEEP_S",
                                                 "write_json_if_changed", "write_atomic", "WRITE_RETRIES")}
        P.BASE, P.SYS, P.ALL_SLEEP_S = self.base, os.path.join(self.base, "_system"), 0
        P.edgar_json, P.get_bytes, P.nasdaq_json = self.edgar_json, self.get_bytes, self.nasdaq_json
        P.ZoneInfo = lambda key: datetime.timezone(datetime.timedelta(hours=-5))   # no tzdata needed (python -I)
        return self

    def __exit__(self, *exc):
        for k, v in self.saved.items():
            setattr(P, k, v)


def _folder(base, ticker, cik):
    os.makedirs(os.path.join(base, ticker), exist_ok=True)
    for name, obj in (("dcf_numbers.json", {"cik": cik}), ("score.json", {"ticker": ticker})):
        with open(os.path.join(base, ticker, name), "w", encoding="utf-8") as f:
            json.dump(obj, f)


def _read(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _quiet(fn, *a, **kw):
    import io, contextlib
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        r = fn(*a, **kw)
    return r, out.getvalue(), err.getvalue()


def test_split_run_one():
    import tempfile
    with tempfile.TemporaryDirectory() as base, _Net(base) as net:
        _folder(base, "WID", 123)
        net.subs[123] = _split_sub(123)
        (res, rc), _, _ = _quiet(P.run_one, "WID", quiet=True)
        pj, sj = os.path.join(base, "WID", "profile.json"), os.path.join(base, "WID", "street.json")
        check(rc == 0 and res["profile_written"] is True and res["street_written"] is True, f"split: first run writes both {rc} {res and (res['profile_written'], res['street_written'])}")
        p, s = _read(pj), _read(sj)
        check("street" not in p and "market" not in p and list(p) == ["ticker", "cik", "as_of", "fetched_at", "newest_filing_date", "sources", "about", "filings", "warnings"],
              f"split: profile.json keys {list(p)}")
        check(set(p["sources"]) == {"edgar_submissions", "edgar_annual_document", "nasdaq_company_profile", "nasdaq_summary"}, f"split: profile sources {p['sources']}")
        check(p["newest_filing_date"] == "2026-08-05" and p["about"]["exchange"] == "NASDAQ-GS" and p["about"]["industry"] == "Software" and p["warnings"] == [],
              f"split: profile content {p['newest_filing_date']} {p['about'].get('exchange')} {p['warnings']}")
        text = open(pj, encoding="utf-8").read()
        check(text.startswith('{\n "ticker": "WID"') and "company’s home region" in text, "split: profile.json keeps write_atomic's format (indent 1, raw UTF-8)")
        today = P.et_today().isoformat()
        check(list(s) == ["ticker", "cik", "as_of", "fetched_at", "source", "street", "market", "sources", "warnings"] and s["ticker"] == "WID" and s["cik"] == 123
              and s["as_of"] == today and s["fetched_at"].startswith(today + "T") and s["fetched_at"].endswith("-05:00")
              and s["source"] == "Nasdaq analyst and quote endpoints", f"split: street.json header {[(k, s[k]) for k in ('ticker', 'cik', 'as_of', 'fetched_at', 'source')]}")
        check(s["street"] == P.build_street(today, TP, RT, FC, EPS, MO, ED, PEG, SUMM) and s["street"]["as_of"] == today and s["market"] == P.build_market(SUMM),
              "split: street.json street / market keep their pre-split shapes")
        check(set(s["sources"]) == {f"nasdaq_{k}" for k in P.NASDAQ_STREET_KEYS} and s["sources"]["nasdaq_summary"].endswith("/summary?assetclass=stocks") and s["warnings"] == [],
              f"split: street.json sources {s['sources']}")
        check(sorted(net.nasdaq) == sorted(["company_profile", "summary", "targetprice", "ratings", "earnings_forecast", "eps", "estimate_momentum", "earnings_date", "peg_ratio"]),
              f"split: one request per Nasdaq endpoint, the summary read once for both files: {net.nasdaq}")

        # the next day: as_of / fetched_at differ and every volatile quote figure moved -> profile.json untouched, street.json rewritten
        old = dict(p, as_of="2026-10-01", fetched_at="2026-10-01T19:07:00-04:00")
        with open(pj, "w", encoding="utf-8") as f:
            json.dump(old, f, indent=1, ensure_ascii=False)
        before_bytes = open(pj, "rb").read()
        past = 1_700_000_000
        os.utime(pj, (past, past))
        with open(sj, "w", encoding="utf-8") as f:
            json.dump(dict(s, as_of="2026-10-01"), f)
        sd = net.summary["summaryData"]
        sd.update({"PreviousClose": {"value": "$250.00"}, "MarketCap": {"value": "80,000,000,000"}, "ShareVolume": {"value": "9,999"},
                   "OneYrTarget": {"value": "$500.00"}, "FiftTwoWeekHighLow": {"value": "$740.00/$240.00"}})
        net.clear()
        (res, rc), _, _ = _quiet(P.run_one, "WID", quiet=True)
        check(rc == 0 and res["profile_written"] is False and open(pj, "rb").read() == before_bytes and os.path.getmtime(pj) == past,
              f"split: an as_of / fetched_at / quote-figure-only change leaves profile.json untouched (written={res and res['profile_written']})")
        s2 = _read(sj)
        check(res["street_written"] is True and s2["as_of"] == today and s2["market"]["previous_close"] == 250.0 and s2["street"]["target_1y_nasdaq_summary"] == 500.0,
              f"split: street.json rewritten with the new figures {s2['as_of']} {s2['market']}")

        # a new feed filing changes the content -> profile.json rewritten, with the new as_of and newest_filing_date
        net.subs[123] = _split_sub(123, [("10-Q", "2026-10-10", "2026-09-30", "w10q.htm")])
        (res, rc), _, _ = _quiet(P.run_one, "WID", quiet=True)
        p3 = _read(pj)
        check(rc == 0 and res["profile_written"] is True and p3["newest_filing_date"] == "2026-10-10" and p3["as_of"] == today and p3["filings"][0]["form"] == "10-Q",
              f"split: a new filing rewrites profile.json {res and res['profile_written']} {p3['newest_filing_date']}")

        # EDGAR down: exit 3, profile.json untouched, street.json still refreshed
        net.edgar_down = True
        snap = open(pj, "rb").read()
        os.remove(sj)
        (res, rc), _, err = _quiet(P.run_one, "WID", quiet=True)
        check(rc == 3 and res["profile"] is None and res["profile_written"] is None and open(pj, "rb").read() == snap and os.path.exists(sj)
              and "profile.json not written" in err, f"split: EDGAR failure -> exit 3, street.json still written: rc={rc} {err!r}")
        net.edgar_down = False

        # --street-only: no EDGAR request at all
        net.clear()
        (res, rc), _, _ = _quiet(P.run_one, "WID", quiet=True, profile=False)
        check(rc == 0 and net.edgar == [] and net.docs == [] and "company_profile" not in net.nasdaq and res["street_written"] is True and res["profile"] is None,
              f"split: street only {net.edgar} {net.nasdaq}")

        # every Nasdaq endpoint down: street.json still written with null blocks and warnings; profile.json's About keeps its
        # EDGAR part (exchange falls back to the submissions list) and is rewritten because its content really changed
        net.nasdaq_down = True
        (res, rc), _, _ = _quiet(P.run_one, "WID", quiet=True)
        s4, p4 = _read(sj), _read(pj)
        check(rc == 0 and s4["street"] is None and s4["market"] is None and all(v.startswith("FAILED: ") for v in s4["sources"].values())
              and any("every Nasdaq analyst endpoint failed" in w for w in s4["warnings"]), f"split: Nasdaq down -> street.json nulls {s4['warnings']}")
        check(p4["about"]["exchange"] == "Nasdaq" and p4["about"]["description"]["text"].startswith("Widget Corp") and p4["sources"]["nasdaq_summary"].startswith("FAILED: "),
              f"split: Nasdaq down -> profile About from EDGAR {p4['about']['exchange']}")
        net.nasdaq_down = False

        # --no-write builds both and writes neither
        snap_p, snap_s = open(pj, "rb").read(), open(sj, "rb").read()
        (res, rc), out, _ = _quiet(P.run_one, "WID", write=False, quiet=False)
        check(rc == 0 and res["profile"] and res["street"] and open(pj, "rb").read() == snap_p and open(sj, "rb").read() == snap_s
              and "profile.json not written" in out and "street.json not written" in out, f"split: --no-write {out!r}")


def test_split_run_all():
    import tempfile
    with tempfile.TemporaryDirectory() as base, _Net(base) as net:
        names = {"AAA": 101, "BBB": 102, "CCC": 103, "DDD": 104, "EEE": 105, "FFF": 106}
        for t, cik in names.items():
            _folder(base, t, cik)
            net.subs[cik] = _split_sub(cik)
        _quiet(P.run_all, 7, force=True, quiet=True)   # build everything once
        today = P.et_today()
        check(all(os.path.exists(os.path.join(base, t, f)) for t in names for f in ("profile.json", "street.json")), "run_all --force builds both files everywhere")

        def edit(t, name, fn):
            path = os.path.join(base, t, name)
            obj = _read(path)
            fn(obj)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(obj, f, indent=1, ensure_ascii=False)
        # AAA: everything fresh -> skipped (one submissions request, nothing else)
        # BBB: a pre-split profile.json (street / market inside) and no street.json -> migrated + fetched
        edit("BBB", "profile.json", lambda o: o.update(street={"consensus": "Buy"}, market={"volume": 1}))
        os.remove(os.path.join(base, "BBB", "street.json"))
        # CCC: street.json 8 days old -> Street only, no EDGAR document read
        edit("CCC", "street.json", lambda o: o.update(as_of=(today - datetime.timedelta(days=8)).isoformat()))
        # DDD: a new 10-Q since the last build -> profile.json rebuilt (and rewritten: the feed changed)
        net.subs[104] = _split_sub(104, [("10-Q", "2026-10-10", "2026-09-30", "d10q.htm")])
        # EEE: only a newer Form 4 -> nothing to do (newest_filing_date counts feed forms only)
        net.subs[105] = _split_sub(105, [("4", "2026-10-12", "", "f4.xml")])
        # FFF: profile.json's as_of is a year old but nothing was filed -> still left alone
        edit("FFF", "profile.json", lambda o: o.update(as_of="2025-10-01"))
        mt = {t: os.path.getmtime(os.path.join(base, t, "profile.json")) for t in names}
        net.clear()
        rc, out, _ = _quiet(P.run_all, 7, quiet=True)
        check(rc == 0 and "profile.json 2 rewritten, 0 rebuilt but unchanged; street.json 2 refreshed; 3 skipped (fresh); 0 failed" in out, f"run_all summary {out!r}")
        check(len(net.edgar) == 6 and sorted(u.rsplit("/", 1)[1] for u in net.docs) == ["w-20251231.htm", "w-20251231.htm"],
              f"run_all: one submissions request per name, the annual document only for the two rebuilds {len(net.edgar)} {net.docs}")
        check(sorted(net.nasdaq) == sorted(["company_profile", "summary"] * 2 + list(P.NASDAQ_STREET_KEYS[1:]) * 2 + ["summary"]),
              f"run_all: Nasdaq requests BBB 9 (summary once), CCC 8, DDD 2: {sorted(net.nasdaq)}")
        b = _read(os.path.join(base, "BBB", "profile.json"))
        check("street" not in b and "market" not in b and _read(os.path.join(base, "BBB", "street.json"))["street"]["consensus"] == "Buy", "run_all: pre-split file migrated")
        check(_read(os.path.join(base, "DDD", "profile.json"))["newest_filing_date"] == "2026-10-10", "run_all: new filing rebuilt")
        check(_read(os.path.join(base, "CCC", "street.json"))["as_of"] == today.isoformat(), "run_all: stale street.json re-fetched")
        check(all(os.path.getmtime(os.path.join(base, t, "profile.json")) == mt[t] for t in ("AAA", "CCC", "EEE", "FFF")), "run_all: untouched profiles keep their mtime")
        # --street-only: no EDGAR request, only stale street files
        edit("AAA", "street.json", lambda o: o.update(as_of="2020-01-01"))
        net.clear()
        rc, out, _ = _quiet(P.run_all, 7, quiet=True, street_only=True)
        check(rc == 0 and net.edgar == [] and net.docs == [] and sorted(net.nasdaq) == sorted(P.NASDAQ_STREET_KEYS) and "street.json 1 refreshed; 5 skipped" in out,
              f"run_all --street-only: {net.edgar} {net.nasdaq} {out!r}")
        # an EDGAR outage: every name fails its profile check, the stale Street files are still refreshed, exit 1
        edit("EEE", "street.json", lambda o: o.update(as_of="2020-01-01"))
        net.edgar_down = True
        net.clear()
        rc, out, _ = _quiet(P.run_all, 7, quiet=True)
        check(rc == 1 and "street.json 1 refreshed" in out and "6 failed" in out and "profile.json not checked" in out, f"run_all EDGAR down: {out!r}")
        net.edgar_down = False
        # a rebuild forced on unchanged content is counted as unchanged, not rewritten
        net.clear()
        rc, out, _ = _quiet(P.run_all, 7, force=True, quiet=True)
        check(rc == 0 and "profile.json 0 rewritten, 6 rebuilt but unchanged; street.json 6 refreshed" in out, f"run_all --force on unchanged content: {out!r}")


def test_split_verifier_round():
    """Verifier round on the split: a second feed filing on the same filingDate rebuilds profile.json; a degraded build
    (Nasdaq About endpoints down, the annual document timing out) is retried by the next --all run and heals, and a
    failure that persists leaves the file untouched; a degraded street.json is re-fetched on the next run; a Windows
    PermissionError on the swap is retried, a write that still fails costs only that file (exit 5), and one name that
    raises never aborts --all."""
    import tempfile, threading
    with tempfile.TemporaryDirectory() as base, _Net(base) as net:
        names = {"AAA": 201, "BBB": 202, "CCC": 203, "DDD": 204}
        for t, cik in names.items():
            _folder(base, t, cik)
            net.subs[cik] = _split_sub(cik)
        net.subs[201] = _split_sub(201, [("8-K", "2026-10-14", "2026-10-14", "a8k.htm")])
        _quiet(P.run_all, 7, force=True, quiet=True)
        pj = {t: os.path.join(base, t, "profile.json") for t in names}
        sj = {t: os.path.join(base, t, "street.json") for t in names}
        check(_read(pj["AAA"])["newest_filing_date"] == "2026-10-14", "verifier: AAA built with the 2026-10-14 8-K")

        # 1. a 10-Q accepted later on the same filingDate: newest_filing_date is unchanged, the feed is not -> rebuilt
        net.subs[201] = _split_sub(201, [("8-K", "2026-10-14", "2026-10-14", "a8k.htm"), ("10-Q", "2026-10-14", "2026-09-30", "a10q.htm")])
        mt = {t: os.path.getmtime(pj[t]) for t in names}
        rc, out, _ = _quiet(P.run_all, 7, quiet=False)
        a = _read(pj["AAA"])
        check(rc == 0 and "AAA: profile.json: new filing 10-Q 2026-10-14 (0000201-26-000004)" in out and "profile.json 1 rewritten" in out
              and sorted(f["form"] for f in a["filings"][:2]) == ["10-Q", "8-K"] and "3 skipped" in out,
              f"verifier: a same-day second filing rebuilds profile.json: {[f['form'] for f in a['filings']]} {out!r}")
        check(all(os.path.getmtime(pj[t]) == mt[t] for t in ("BBB", "CCC", "DDD")), "verifier: the other names are untouched")
        rc, out, _ = _quiet(P.run_all, 7, quiet=True)
        check(rc == 0 and "4 skipped (fresh)" in out, f"verifier: the next run skips AAA again: {out!r}")

        # 2. BBB rebuilt (worker step 9) while Nasdaq is down: About degraded, street.json null; the next --all heals both
        net.nasdaq_down = True
        _quiet(P.run_one, "BBB", quiet=True)
        net.nasdaq_down = False
        b = _read(pj["BBB"])
        check(b["about"]["industry"] is None and b["about"]["exchange"] == "Nasdaq" and b["sources"]["nasdaq_company_profile"].startswith("FAILED: ")
              and _read(sj["BBB"])["street"] is None, "verifier: BBB degraded by the Nasdaq outage")
        net.clear()
        rc, out, _ = _quiet(P.run_all, 7, quiet=False)
        b = _read(pj["BBB"])
        check(rc == 0 and "BBB: profile.json: last build degraded (nasdaq_company_profile, nasdaq_summary); street.json: last pull degraded (" in out
              and b["about"]["industry"] == "Software" and b["about"]["exchange"] == "NASDAQ-GS" and b["about"]["description_short"] == "Widgets."
              and not any(str(v).startswith("FAILED") for v in b["sources"].values()) and b["warnings"] == []
              and _read(sj["BBB"])["street"]["consensus"] == "Buy" and "profile.json 1 rewritten" in out and "street.json 1 refreshed" in out,
              f"verifier: the next --all heals a Nasdaq-degraded build: {b['about'].get('industry')} {out!r}")

        # 3. a new 10-Q for CCC while its 10-K document times out: rewritten with null description / employees (the feed
        # really changed), then retried; a failure that persists leaves the file untouched; recovery heals it
        net.subs[203] = _split_sub(203, [("10-Q", "2026-10-13", "2026-09-30", "c10q.htm")])
        net.doc_down = True
        rc, out, _ = _quiet(P.run_all, 7, quiet=True)
        c = _read(pj["CCC"])
        check(c["about"]["description"] is None and c["about"]["employees"] is None and c["warnings"][0].startswith("annual document unreadable (timed out)")
              and c["filings"][0]["form"] == "10-Q", f"verifier: CCC degraded by the document timeout {c['warnings']}")
        past = 1_700_000_000
        os.utime(pj["CCC"], (past, past))
        net.clear()
        rc, out, _ = _quiet(P.run_all, 7, quiet=True)
        check(rc == 0 and "profile.json 0 rewritten, 1 rebuilt but unchanged" in out and os.path.getmtime(pj["CCC"]) == past and len(net.docs) == 1,
              f"verifier: a persisting failure is retried but leaves the file untouched {out!r} {net.docs}")
        net.doc_down = False
        rc, out, _ = _quiet(P.run_all, 7, quiet=True)
        c = _read(pj["CCC"])
        check(rc == 0 and "profile.json 1 rewritten" in out and c["about"]["description"]["text"].startswith("Widget Corp") and c["about"]["employees"]["count"] == 1900
              and c["warnings"] == [], f"verifier: the document read again heals CCC {c['about'].get('employees')} {out!r}")
        rc, out, _ = _quiet(P.run_all, 7, quiet=True)
        check(rc == 0 and "4 skipped (fresh)" in out, f"verifier: nothing left to retry {out!r}")

        # 4. Windows PermissionError on the swap: retried; a real reader holding the file open for 0.3 s
        real = P.write_json_if_changed
        target = os.path.join(base, "lock.json")
        P.write_profile_json(target, {"a": 1})
        f = open(target, encoding="utf-8")
        threading.Timer(0.3, f.close).start()
        ok = P.write_profile_json(target, {"a": 2})
        check(ok is True and _read(target) == {"a": 2}, "verifier: write_profile_json waits out a reader holding the file open")
        tries = []

        def flaky(path, obj, **kw):
            tries.append(path)
            if len(tries) <= 2:
                raise PermissionError(13, "Access is denied (test)")
            return real(path, obj, **kw)
        P.write_json_if_changed = flaky
        check(P.write_profile_json(target, {"a": 3}) is True and _read(target) == {"a": 3} and len(tries) == 3,
              f"verifier: two PermissionErrors then success {len(tries)}")

        # ... a swap that never succeeds: profile.json is reported (exit 5), street.json is still written, --all goes on
        def locked(path, obj, **kw):
            if os.sep + "AAA" + os.sep in path or "/AAA/" in path:
                raise PermissionError(13, "Access is denied (test)")
            return real(path, obj, **kw)
        P.write_json_if_changed, P.WRITE_RETRIES = locked, 2
        os.remove(sj["AAA"])
        (res, rc), _, err = _quiet(P.run_one, "AAA", quiet=True)
        check(rc == 5 and res["profile_written"] is None and res["street_written"] is True and os.path.exists(sj["AAA"]) and "profile.json not written (PermissionError" in err,
              f"verifier: a locked profile.json -> exit 5, street.json written: rc={rc} {err!r}")
        net.subs[201] = _split_sub(201, [("8-K", "2026-10-14", "2026-10-14", "a8k.htm"), ("10-Q", "2026-10-14", "2026-09-30", "a10q.htm"),
                                         ("8-K", "2026-10-15", "2026-10-15", "b8k.htm")])
        net.subs[204] = _split_sub(204, [("8-K", "2026-10-15", "2026-10-15", "d8k.htm")])
        rc, out, _ = _quiet(P.run_all, 7, quiet=True)
        check(rc == 1 and "AAA: exit 5" in out and "profile.json 1 rewritten" in out and _read(pj["DDD"])["newest_filing_date"] == "2026-10-15",
              f"verifier: a locked file fails its name only; DDD after it is still rebuilt {out!r}")
        P.write_json_if_changed = real

        # ... an exception nobody expected in one name never aborts the walk
        real_atomic = P.write_atomic

        def boom(path, obj):
            if os.sep + "BBB" + os.sep in path or "/BBB/" in path:
                raise ValueError("Out of range float values are not JSON compliant (test)")
            return real_atomic(path, obj)
        P.write_atomic = boom
        for t in ("BBB", "CCC"):
            os.remove(sj[t])
        rc, out, _ = _quiet(P.run_all, 7, quiet=True)
        check(rc == 1 and "BBB: raised ValueError" in out and "street.json 1 refreshed" in out and os.path.exists(sj["CCC"]) and not os.path.exists(sj["BBB"]),
              f"verifier: an exception in BBB is counted and CCC after it is still refreshed {out!r}")
        P.write_atomic = real_atomic


# ---------------------------------------------------------------------------
# 11-14. Follow-up round: parse error vs unreadable, corrupt files under --all, --street-only without EDGAR, encodings
def _main(argv):
    """profile.main(argv) -> (exit code, stdout, stderr)."""
    import io, contextlib
    out, err = io.StringIO(), io.StringIO()
    code = None
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            P.main(argv)
        except SystemExit as e:
            code = e.code
    return code, out.getvalue(), err.getvalue()


def _annual(cik=123):
    return {"form": "10-K", "filed": "2026-02-19", "period": "2025-12-31", "accession": f"0000{cik}-26-000000",
            "url": f"https://www.sec.gov/Archives/edgar/data/{cik}/0000{cik}26000000/w-20251231.htm"}


def test_profile_parse_error_vs_unreadable():
    """An exception from the network / response is "annual document unreadable" (degraded: retried by --all); one raised
    by an extractor on a document that was read is "annual document parse error (<Type>: ...)": on stderr with the
    traceback, exit 6, a failure line in the --all summary, only that extractor's fields null, and NOT degraded, so the
    next --all leaves the name alone (no re-download) until the filing feed changes or --force."""
    import tempfile

    class BadBytes(bytes):
        def decode(self, *a, **k):
            raise UnicodeDecodeError("utf-8", b"\xff", 0, 1, "undecodable (test)")

    with tempfile.TemporaryDirectory() as base, _Net(base) as net:
        sub = _split_sub(123)
        feed, newest = P.build_filings(sub, 123), P.newest_filing_date(sub)

        def build_with(get_bytes):
            P.get_bytes = get_bytes
            try:
                return _quiet(P.build, "WID", 123, quiet=True, sub=sub)
            finally:
                P.get_bytes = net.get_bytes

        # the network / response: unreadable, degraded, retried
        def timeout(url, headers, timeout):
            raise TimeoutError("timed out")
        for label, getter, start in (("timeout", timeout, "annual document unreadable (timed out); description and employees null"),
                                     ("undecodable body", lambda url, h, t: BadBytes(b"<html>"), "annual document unreadable ('utf-8' codec can't decode"),
                                     ("no body", lambda url, h, t: None, "annual document unreadable (response body is NoneType, not bytes)")):
            doc, _, err = build_with(getter)
            w = [x for x in doc["warnings"] if x.startswith("annual document")]
            check(len(w) == 1 and w[0].startswith(start) and P.degraded(doc) == "annual document unreadable" and P.parse_errors(doc) == []
                  and P.profile_rebuild_reason(doc, newest, feed=feed) == "last build degraded (annual document unreadable)" and err == ""
                  and doc["about"]["description"] is None and doc["about"]["employees"] is None,
                  f"parse vs unreadable: {label} is unreadable and retried: {w} {P.degraded(doc)} {err!r}")

        # a healthy build for comparison
        good, _, err = _quiet(P.build, "WID", 123, quiet=True, sub=sub)
        check(good["about"]["description"] and good["about"]["employees"]["count"] == 1900 and good["about"]["address"]["source"] == "annual filing cover"
              and good["warnings"] == [] and err == "", f"parse vs unreadable: the healthy build {good['warnings']} {err!r}")

        # each extractor raising: only its fields are null, the warning names it, stderr has the traceback, not degraded
        class Obj:
            pass
        cases = (("cover_address", "headquarters from the EDGAR submissions address",
                  lambda a: a["address"]["source"] == "EDGAR submissions" and a["description"] and a["employees"]["count"] == 1900),
                 ("html_to_text", "description and employees null",
                  lambda a: a["address"]["source"] == "annual filing cover" and a["description"] is None and a["employees"] is None),
                 ("extract_item1", "description null",
                  lambda a: a["address"]["source"] == "annual filing cover" and a["description"] is None and a["employees"]["count"] == 1900),
                 ("extract_employees", "employees null",
                  lambda a: a["address"]["source"] == "annual filing cover" and a["description"]["text"].startswith("Widget Corp") and a["employees"] is None
                  and a["employees_unresolved"] is None))
        import re
        obj = Obj()
        shown = re.sub(r" at 0x[0-9a-fA-F]+", "", repr(obj))   # "<...Obj object>": the address is dropped
        for step, effect, fields_ok in cases:
            real = getattr(P, step)

            def bug(*a, **k):
                raise TypeError(f"'NoneType' object is not subscriptable, {obj!r}")
            setattr(P, step, bug)
            try:
                doc, _, err = _quiet(P.build, "WID", 123, quiet=True, sub=sub)
            finally:
                setattr(P, step, real)
            pe = P.parse_errors(doc)
            want = (f"annual document parse error (TypeError: 'NoneType' object is not subscriptable, {shown}) in {step} on the 10-K"
                    f" filed 2026-02-19; {effect}")
            check(pe == [want] and "0x" not in pe[0], f"parse error: {step} warning {pe}")
            check(fields_ok(doc["about"]), f"parse error: {step} nulls only its own fields {doc['about'].get('address')} {doc['about'].get('description')} {doc['about'].get('employees')}")
            check(P.degraded(doc) is None and P.profile_rebuild_reason(doc, newest, feed=feed) is None,
                  f"parse error: {step} is not degraded, so --all does not retry it: {P.degraded(doc)}")
            check(P.profile_rebuild_reason(doc, "2026-10-10", feed=feed) == "new filing 2026-10-10" and P.profile_rebuild_reason(doc, newest, force=True, feed=feed) == "--force",
                  f"parse error: {step} is rebuilt on a feed change or --force")
            check(f"profile.py: WID: annual document parse error in {step} (TypeError: " in err and "Traceback (most recent call last)" in err
                  and "Not retried until the filing feed changes (or --force)" in err, f"parse error: {step} on stderr with the traceback {err!r}")

        # run_one: exit 6, profile.json still written (with the warning), street.json written
        _folder(base, "WID", 123)
        net.subs[123] = sub
        real_item1 = P.extract_item1

        def buggy_item1(text, form="10-K", entity=None):
            if "BUGGY" in text:
                raise TypeError("boom (test)")
            return real_item1(text, form, entity=entity)
        P.extract_item1 = buggy_item1
        real_get = net.get_bytes

        def get_doc(url, headers, timeout):   # CIK 402's 10-K trips the bug; every other document is clean
            raw = real_get(url, headers, timeout)
            return raw.replace(b"Human Capital", b"BUGGY Human Capital") if "/data/402/" in url else raw
        net.get_bytes = get_doc
        P.get_bytes = get_doc
        try:
            (res, rc), out, err = _quiet(P.run_one, "WID", quiet=True)
            check(rc == 0 and res["errors"] == [], f"parse error: the clean document exits 0 {rc} {res['errors']}")
            _folder(base, "BUG", 402)
            net.subs[402] = _split_sub(402)
            (res, rc), out, err = _quiet(P.run_one, "BUG", quiet=True)
            pj = os.path.join(base, "BUG", "profile.json")
            p = _read(pj)
            check(rc == 6 and res["profile_written"] is True and res["street_written"] is True and p["about"]["description"] is None
                  and p["about"]["employees"]["count"] == 1900 and P.parse_errors(p) == res["profile"]["warnings"][-1:]
                  and res["errors"] == [(6, P.parse_errors(p)[0])] and "boom (test)" in err and "Traceback" in err,
                  f"parse error: run_one exits 6 and still writes both files: rc={rc} {res['errors']} {p['warnings']}")

            # --all: the build that meets the bug is a failure line; the next run leaves it alone (no re-download)
            os.remove(pj)
            net.clear()
            rc, out, err = _quiet(P.run_all, 7, quiet=True)
            check(rc == 1 and "1 failed" in out and "\n  BUG: exit 6 - annual document parse error (TypeError: boom (test)) in extract_item1 on the 10-K filed 2026-02-19; description null" in out
                  and "profile.json 1 rewritten" in out and "boom (test)" in err and len(net.docs) == 1, f"parse error: --all reports it as a failure {out!r} {net.docs}")
            net.clear()
            rc, out, err = _quiet(P.run_all, 7, quiet=True)
            check(rc == 0 and "2 skipped (fresh); 0 failed" in out and net.docs == [] and err == "",
                  f"parse error: the next --all does not retry it (no document read) {out!r} {net.docs}")
            # a feed change rebuilds it (and reports the bug again); --force does too
            net.subs[402] = _split_sub(402, [("10-Q", "2026-10-10", "2026-09-30", "b10q.htm")])
            net.clear()
            rc, out, err = _quiet(P.run_all, 7, quiet=True)
            check(rc == 1 and "BUG: exit 6 - annual document parse error" in out and len(net.docs) == 1, f"parse error: a new filing rebuilds it {out!r}")
            net.clear()
            rc, out, err = _quiet(P.run_all, 7, force=True, quiet=True)
            check(rc == 1 and "BUG: exit 6 - annual document parse error" in out and len(net.docs) == 2 and "1 failed" in out, f"parse error: --force rebuilds it {out!r}")
            # contrast: an unreadable document IS retried on the next run
            net.doc_down = True
            net.subs[402] = _split_sub(402, [("10-Q", "2026-10-10", "2026-09-30", "b10q.htm"), ("8-K", "2026-10-12", "2026-10-12", "b8k.htm")])
            _quiet(P.run_all, 7, quiet=True)
            net.clear()
            rc, out, _ = _quiet(P.run_all, 7, quiet=True)
            check(len(net.docs) == 1 and "/data/402/" in net.docs[0] and rc == 0, f"parse error: an unreadable document is retried on the next run {net.docs} {out!r}")
            net.doc_down = False
            net.clear()
            rc, out, _ = _quiet(P.run_all, 7, quiet=True)
            check(rc == 1 and len(net.docs) == 1 and "BUG: exit 6 - annual document parse error" in out, f"parse error: the retry that reads it meets the bug once {out!r}")
            net.clear()
            rc, out, _ = _quiet(P.run_all, 7, quiet=True)
            check(rc == 0 and net.docs == [], f"parse error: ... and then stops {out!r}")
        finally:
            P.extract_item1 = real_item1


def test_profile_corrupt_files_in_all():
    """A profile.json / street.json whose fields have the wrong types (or a CIK that is not an integer) never aborts
    --all: that check is a failure line naming the file, the other file of the same name is still checked and
    refreshed, the names after it are processed, and the exit status is 1. A single-name run rewrites the file."""
    import tempfile
    with tempfile.TemporaryDirectory() as base, _Net(base) as net:
        names = {"AAA": 501, "BBB": 502, "CCC": 503, "DDD": 504, "EEE": 505, "FFF": 506}
        for t, cik in names.items():
            _folder(base, t, cik)
            net.subs[cik] = _split_sub(cik)
        _quiet(P.run_all, 7, force=True, quiet=True)
        pj = {t: os.path.join(base, t, "profile.json") for t in names}
        sj = {t: os.path.join(base, t, "street.json") for t in names}

        def edit(path, fn):
            obj = _read(path)
            fn(obj)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(obj, f)
        old = (P.et_today() - datetime.timedelta(days=30)).isoformat()
        # AAA: profile.json warnings is a number (degraded() raises TypeError); its street.json is stale -> still refreshed
        edit(pj["AAA"], lambda o: o.update(warnings=5))
        edit(sj["AAA"], lambda o: o.update(as_of=old))
        # BBB: street.json warnings is a number; a new filing -> profile.json still rebuilt
        edit(sj["BBB"], lambda o: o.update(warnings=5))
        net.subs[502] = _split_sub(502, [("10-Q", "2026-10-10", "2026-09-30", "b10q.htm")])
        # CCC: profile.json filings is a number (the accession comparison raises)
        edit(pj["CCC"], lambda o: o.update(filings=7))
        # DDD: dcf_numbers.json cik is not a number, fundamentals.json has it -> resolved, fresh, skipped
        with open(os.path.join(base, "DDD", "dcf_numbers.json"), "w", encoding="utf-8") as f:
            json.dump({"cik": "abc"}, f)
        with open(os.path.join(base, "DDD", "fundamentals.json"), "w", encoding="utf-8") as f:
            json.dump({"cik": 504}, f)
        # EEE: no usable CIK anywhere (an object, a bool) -> "no CIK"
        with open(os.path.join(base, "EEE", "dcf_numbers.json"), "w", encoding="utf-8") as f:
            json.dump({"cik": {"value": 505}}, f)
        with open(os.path.join(base, "EEE", "fundamentals.json"), "w", encoding="utf-8") as f:
            json.dump({"cik": True}, f)
        # FFF: after all of them, a stale street.json -> refreshed (the walk went on)
        edit(sj["FFF"], lambda o: o.update(as_of=old))
        snap = {t: open(pj[t], "rb").read() for t in ("AAA", "CCC")}
        net.clear()
        rc, out, err = _quiet(P.run_all, 7, quiet=True)
        lines = out.split("\n  ")
        check(rc == 1 and "4 failed" in out and len(lines) == 5, f"corrupt: four names fail, one line each {out!r}")
        check(any(x.startswith("AAA: profile.json unreadable (TypeError: ") and "not rebuilt (profile.py AAA, or --force, rewrites it)" in x for x in lines)
              and any(x.startswith("BBB: street.json unreadable (TypeError: ") and "profile.py BBB --street-only" in x for x in lines)
              and any(x.startswith("CCC: profile.json unreadable (TypeError: ") for x in lines) and any(x.strip() == "EEE: no CIK" for x in lines),
              f"corrupt: each failure line names the file and the reason {lines}")
        check(_read(sj["AAA"])["as_of"] == P.et_today().isoformat() and open(pj["AAA"], "rb").read() == snap["AAA"],
              "corrupt: AAA's stale street.json is refreshed although its profile.json is corrupt (left as it was)")
        check(_read(pj["BBB"])["newest_filing_date"] == "2026-10-10" and _read(sj["BBB"])["warnings"] == 5,
              "corrupt: BBB's profile.json is rebuilt although its street.json is corrupt (left as it was)")
        check(_read(sj["FFF"])["as_of"] == P.et_today().isoformat() and "profile.json 1 rewritten" in out and "street.json 2 refreshed" in out
              and "1 skipped (fresh)" in out, f"corrupt: the walk went on to FFF; DDD resolved through fundamentals.json and skipped {out!r}")
        check(P.resolve_cik("DDD") == 504 and P.resolve_cik("EEE") is None, "corrupt: resolve_cik skips a CIK that is not a positive integer")

        # --street-only meets the corrupt street.json the same way
        net.clear()
        rc, out, _ = _quiet(P.run_all, 7, quiet=True, street_only=True)
        # (EEE resolves here: --street-only reads the CIK from its committed profile.json first)
        check(rc == 1 and "BBB: street.json unreadable (TypeError: " in out and "; 1 failed" in out and "EEE" not in out and net.edgar == [],
              f"corrupt: --street-only {out!r}")

        # an exception nobody expected anywhere in one name's checks (here the CIK lookup itself) is counted, the walk goes on
        real = P.resolve_cik

        def flaky(t, *a, **k):
            if t == "DDD":
                raise RuntimeError("resolver bug (test)")
            return real(t, *a, **k)
        P.resolve_cik = flaky
        try:
            rc, out, err = _quiet(P.run_all, 7, quiet=True)
        finally:
            P.resolve_cik = real
        check(rc == 1 and "DDD: raised RuntimeError: resolver bug (test)" in out and "resolver bug (test)" in err and "5 failed" in out
              and "FFF" not in out.split("failed")[1],
              f"corrupt: an exception in the CIK lookup is one name's failure {out!r}")

        # a single-name run rewrites the corrupt files; --all is clean again (EEE aside)
        for t, extra in (("AAA", []), ("BBB", ["--street-only"]), ("CCC", [])):
            code, _, _ = _main([t, "--quiet"] + extra)
            check(code == 0, f"corrupt: profile.py {t} {extra} heals it ({code})")
        net.clear()
        rc, out, _ = _quiet(P.run_all, 7, quiet=True)
        check(rc == 1 and "1 failed" in out and "EEE: no CIK" in out and "5 skipped (fresh)" in out, f"corrupt: healed {out!r}")


class _Resp:
    def __init__(self, body):
        self.body = body

    def read(self):
        return self.body

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


class _Wire:
    """The transport stubbed (urllib.request.urlopen), so get_bytes / edgar_json / nasdaq_json run for real and every
    request is logged by host: an EDGAR request made by any code path shows up in `sec`."""

    def __init__(self, base, subs):
        self.base, self.subs, self.urls = base, subs, []

    def urlopen(self, req, timeout=None):
        url = req.full_url if hasattr(req, "full_url") else str(req)
        self.urls.append(url)
        host = url.split("/")[2]
        if host == "data.sec.gov":
            return _Resp(json.dumps(self.subs[int(url.split("CIK")[1][:10])]).encode("utf-8"))
        if host == "www.sec.gov":
            return _Resp(SPLIT_DOC)
        assert host == "api.nasdaq.com", url
        ticker = url.split("/")[5]
        key = next(k for k, u in P.nasdaq_urls(ticker).items() if u == url)
        data = {"company_profile": NQ_PROFILE, "summary": SUMM, "targetprice": TP, "ratings": RT, "earnings_forecast": FC, "eps": EPS,
                "estimate_momentum": MO, "earnings_date": ED, "peg_ratio": PEG}[key]
        return _Resp(json.dumps({"data": data, "status": {"rCode": 200}}).encode("utf-8"))

    def sec(self):
        return [u for u in self.urls if "sec.gov" in u.split("/")[2]]

    def nasdaq(self):
        return [u for u in self.urls if u.split("/")[2] == "api.nasdaq.com"]

    def __enter__(self):
        import urllib.request
        self.saved = {k: getattr(P, k) for k in ("BASE", "SYS", "ZoneInfo", "ALL_SLEEP_S", "MIN_INTERVAL_S")}
        self.saved_urlopen = urllib.request.urlopen
        P.BASE, P.SYS, P.ALL_SLEEP_S, P.MIN_INTERVAL_S = self.base, os.path.join(self.base, "_system"), 0, 0
        P.ZoneInfo = lambda key: datetime.timezone(datetime.timedelta(hours=-5))
        urllib.request.urlopen = self.urlopen
        return self

    def __exit__(self, *exc):
        import urllib.request
        urllib.request.urlopen = self.saved_urlopen
        for k, v in self.saved.items():
            setattr(P, k, v)


def test_profile_street_only_no_edgar():
    """--street-only (with --all and with one ticker) makes zero EDGAR requests at the transport level: the CIK comes
    from the committed profile.json, else dcf_numbers.json / fundamentals.json, else the local ticker maps; --all keeps
    the street.json policy (missing, --max-age-days old, degraded, --force); profile.json is never touched. The same
    stub sees the EDGAR requests of a full run, so it would catch one."""
    import tempfile
    with tempfile.TemporaryDirectory() as base:
        os.makedirs(os.path.join(base, "_system"))
        subs = {303: _split_sub(303)}
        with _Wire(base, subs) as wire:
            today = P.et_today()

            def put(t, name, obj):
                os.makedirs(os.path.join(base, t), exist_ok=True)
                with open(os.path.join(base, t, name), "w", encoding="utf-8") as f:
                    json.dump(obj, f)

            def street(as_of, sources=None):
                return {"ticker": "X", "cik": 1, "as_of": as_of, "fetched_at": as_of + "T19:00:00-05:00", "source": P.STREET_SOURCE,
                        "street": None, "market": None, "sources": sources or {}, "warnings": []}
            for t in ("AAA", "BBB", "CCC", "DDD", "EEE", "FFF", "GGG", "HHH", "III", "JJJ", "KKK"):
                put(t, "score.json", {"ticker": t})
            put("AAA", "profile.json", {"ticker": "AAA", "cik": 301, "about": {}})           # profile.json only
            put("BBB", "fundamentals.json", {"ticker": "BBB", "cik": "0000302"})             # fundamentals.json only
            put("CCC", "dcf_numbers.json", {"ticker": "CCC", "cik": 303})                     # dcf_numbers.json only
            with open(os.path.join(base, "_system", "sec_tickers_exchange.json"), "w", encoding="utf-8") as f:   # DDD: the ticker map
                json.dump({"fields": ["cik", "name", "ticker", "exchange"], "data": [[304, "Ddd Inc", "DDD", "NYSE"]]}, f)
            with open(os.path.join(base, "_system", "universe.csv"), "w", encoding="utf-8", newline="") as f:      # EEE: universe.csv
                f.write("queue_pos,ticker,name,cik\n1,EEE,Eee Corp,305\n")
            put("FFF", "profile.json", {"ticker": "FFF", "cik": 306, "about": {}})           # profile.json beats dcf_numbers.json
            put("FFF", "dcf_numbers.json", {"ticker": "FFF", "cik": 999})
            for t, cik in (("GGG", 307), ("HHH", 308), ("III", 309), ("JJJ", 310)):
                put(t, "dcf_numbers.json", {"cik": cik})
            put("GGG", "street.json", street(today.isoformat()))                                                   # fresh
            put("HHH", "street.json", street(today.isoformat(), {"nasdaq_ratings": "FAILED: https://api.nasdaq.com/x"}))  # degraded
            put("III", "street.json", street((today - datetime.timedelta(days=3)).isoformat()))                     # 3 days > 2
            put("JJJ", "street.json", street((today - datetime.timedelta(days=1)).isoformat()))                     # 1 day < 2
            # KKK: no CIK anywhere
            profile_bytes = {t: open(os.path.join(base, t, "profile.json"), "rb").read() for t in ("AAA", "FFF")}

            code, out, err = _main(["--all", "--street-only", "--quiet", "--max-age-days", "2"])
            check(wire.sec() == [], f"street-only --all: zero EDGAR requests {wire.sec()}")
            check(code == 1 and "profile.json 0 rewritten, 0 rebuilt but unchanged (EDGAR not read: --street-only); street.json 8 refreshed; 2 skipped (fresh); 1 failed" in out
                  and "KKK: no CIK" in out, f"street-only --all: summary {code} {out!r} {err!r}")
            got = {t: _read(os.path.join(base, t, "street.json"))["cik"] for t in ("AAA", "BBB", "CCC", "DDD", "EEE", "FFF", "HHH", "III")}
            check(got == {"AAA": 301, "BBB": 302, "CCC": 303, "DDD": 304, "EEE": 305, "FFF": 306, "HHH": 308, "III": 309},
                  f"street-only --all: CIK from profile.json, fundamentals.json, dcf_numbers.json, the ticker map, universe.csv; profile.json first {got}")
            check(_read(os.path.join(base, "GGG", "street.json"))["street"] is None and _read(os.path.join(base, "JJJ", "street.json"))["street"] is None
                  and _read(os.path.join(base, "HHH", "street.json"))["street"]["consensus"] == "Buy",
                  "street-only --all: the fresh files are left alone, the degraded and stale ones re-fetched")
            keys = sorted(u.split("/")[-1].split("?")[0] for u in wire.nasdaq())
            check(len(wire.nasdaq()) == 8 * len(P.NASDAQ_STREET_KEYS) and not any("company-profile" in u for u in wire.nasdaq()),
                  f"street-only --all: only the street.json endpoints, once each per name {len(wire.nasdaq())} {keys[:10]}")
            check(all(open(os.path.join(base, t, "profile.json"), "rb").read() == profile_bytes[t] for t in profile_bytes)
                  and not os.path.exists(os.path.join(base, "CCC", "profile.json")), "street-only --all: profile.json never written")

            # one ticker: re-fetched whatever its age, still no EDGAR request
            wire.urls = []
            code, out, err = _main(["GGG", "--street-only", "--quiet"])
            check(code == 0 and wire.sec() == [] and len(wire.nasdaq()) == len(P.NASDAQ_STREET_KEYS)
                  and _read(os.path.join(base, "GGG", "street.json"))["street"]["consensus"] == "Buy" and not os.path.exists(os.path.join(base, "GGG", "profile.json")),
                  f"street-only <T>: no EDGAR request, street.json re-fetched {code} {wire.sec()} {err!r}")
            wire.urls = []
            code, out, err = _main(["AAA", "--street-only", "--no-write"])
            check(code == 0 and wire.sec() == [] and "profile: AAA cik=301 | street.json not written" in out, f"street-only <T> --no-write {code} {out!r}")
            wire.urls = []
            code, out, err = _main(["KKK", "--street-only", "--quiet"])
            check(code == 2 and wire.urls == [] and "NO_CIK for KKK" in err, f"street-only <T> without a CIK: exit 2, no request {code} {err!r}")
            wire.urls = []
            code, out, err = _main(["--all", "--street-only", "--max-age-days", "two"])
            check(code == 2 and wire.urls == [] and "--max-age-days" in err, f"a bad --max-age-days is a usage error {code} {err!r}")
            code, out, err = _main(["CCC", "--cik", "x1"])
            check(code == 2 and wire.urls == [], f"a bad --cik is a usage error {code} {err!r}")

            # the same stub sees a full run's EDGAR requests (submissions + the 10-K), so the zero above is real
            wire.urls = []
            code, out, err = _main(["CCC", "--quiet"])
            check(code == 0 and len(wire.sec()) == 2 and any("data.sec.gov/submissions/CIK0000000303.json" in u for u in wire.sec())
                  and os.path.exists(os.path.join(base, "CCC", "profile.json")), f"full run: EDGAR requests seen by the stub {wire.sec()} {err!r}")


def test_profile_open_encoding():
    """Every text-mode open() in profile.py names encoding="utf-8" (Windows' default code page would otherwise read
    and write the files differently from the VM)."""
    import ast
    src = open(os.path.join(SYS, "profile.py"), encoding="utf-8").read()
    bad, seen = [], 0
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Call) and ((isinstance(node.func, ast.Name) and node.func.id == "open")
                                           or (isinstance(node.func, ast.Attribute) and node.func.attr in ("open", "fdopen")
                                               and getattr(node.func.value, "id", "") in ("os", "io", "codecs"))):
            seen += 1
            mode = node.args[1] if len(node.args) > 1 else next((k.value for k in node.keywords if k.arg == "mode"), None)
            binary = isinstance(mode, ast.Constant) and "b" in str(mode.value)
            enc = next((k.value for k in node.keywords if k.arg == "encoding"), None)
            if not binary and not (isinstance(enc, ast.Constant) and str(enc.value).lower().replace("-", "") == "utf8"):
                bad.append(node.lineno)
    check(seen >= 3 and bad == [], f"profile.py: text-mode open() without encoding='utf-8' at lines {bad} ({seen} calls)")


if __name__ == "__main__":
    for fn in (test_item1, test_item1_review_round, test_employees, test_employees_review_round, test_items_and_feed, test_skip_rule,
               test_street, test_first_filing, test_helpers, test_hq_and_forms_review_round, test_build_unresolved_employees,
               test_item1_preamble_round, test_employees_breakdown_round, test_split_run_one, test_split_run_all, test_split_verifier_round,
               test_profile_parse_error_vs_unreadable, test_profile_corrupt_files_in_all, test_profile_street_only_no_edgar, test_profile_open_encoding):
        fn()
    if FAILS:
        print(f"{len(FAILS)} failure(s)")
        sys.exit(1)
    print("test_profile: all checks passed")
