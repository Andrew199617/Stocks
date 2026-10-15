#!/usr/bin/env python3
"""Segment / product / geography breakdowns from each filing's own XBRL
instance document (v5.4, 2026-10-14).

Usage:
  python _system/segments.py <TICKER> [--cik N] [--no-write] [--force]
  python _system/segments.py --all [--force]
      every folder with a score.json, sequential, continue on failure; a
      folder whose segments.json already lists the same latest accession
      numbers is skipped unless --force; prints a summary at the end.

Why this exists: the EDGAR companyfacts API drops every dimensioned fact, so
the repo had no segment data (the README notes the same limitation for TKO's
extension tags). The breakdowns live only in each filing's XBRL instance.

Source: EDGAR submissions API -> the latest 10-K (or 20-F / 40-F) and the
latest two 10-Qs -> each filing's extracted XBRL instance
(<primaryDocument basename>_htm.xml, else the instance named in the filing's
index.json) and its label linkbase. Parsed with xml.etree iterparse.

What is kept: facts for the concepts in CONCEPTS (us-gaap plus the obvious
ifrs-full equivalents) in contexts carrying exactly one of
  us-gaap:StatementBusinessSegmentsAxis / ifrs-full:SegmentsAxis   -> business_segments
  srt:ProductOrServiceAxis / ifrs-full:ProductsAndServicesAxis     -> product
  srt:StatementGeographicalAxis / ifrs-full:GeographicalAreasAxis  -> geography
and nothing else (a ConsolidationItemsAxis OperatingSegmentsMember alongside
is tolerated, see below), plus contexts whose ONLY dimension is a
ConsolidationItemsAxis reconciling member (corporate, eliminations), which
become reconciling rows of the business_segments tables. A kept-axis member
combined with a reconciling consolidation member (Huntington's "Capital
Market Fees x Corporate", Expedia's "trivago x Intersegment") is a cell of
the segment-by-reconciliation matrix that is already inside the bare
member's figure, so it is ignored like every other multi-axis combination.
Undimensioned facts are the consolidated totals.

Periods: annual facts (330-380 days) from the 10-K give the FY columns;
three-month facts (77-120 days, so a 16-week first quarter counts) from the
10-Qs give the quarterly columns, with the prior-year comparative quarter the
10-Q carries (that is what growth_yoy needs). Q4 is derived as FY minus the
nine-month leg only when that leg exists for the same member (marked
derived). Latest filing wins per (concept, member, period); within one filing
a bare segment member beats member + OperatingSegmentsMember (Expedia tags
trivago's external revenue bare and its gross-of-intersegment figure under
OperatingSegmentsMember — the bare one ties to the consolidated total).

Rows that would double count are removed, in this order, each with a warning
naming the row: (1) subtotal members — a member that is an ancestor (in the
filing's definition linkbase, domain-member arcs) of another row in the same
table, a member named *Total* / *ReportableSegments* / *IncludingOther*, or a
row whose values equal, in every column, the sum of two or more other rows
(Centene's TotalPremiumAndService = HealthCarePremium + Service; Martin
Marietta's ReportableSegments; nested product subtotals); (2) one member the
filer tagged under two names with identical numbers (Axon's
SoftwareAndSensorsMember / SoftwareAndSensorsSegmentMember); (3) a
reconciling line tagged twice — on the segment axis under the filer's own
member and bare under a standard consolidation member — with identical
numbers is shown once under the filer's member; (4) a reconciling row the
bare segment rows already tie to the consolidated total without (Expedia's
intersegment revenue, +51 in the 10-Q and -205 in the 10-K, which belongs to
the gross OperatingSegments figures, not the bare external ones). When a
consolidated fact exists and the surviving rows still sum more than 2% away
from it the table carries ties_to_total: false and a warning; when they
cover less than half of it (Con Edison: 4 / 0 / -2 against 16,918 because
the real segments sit on an extra LegalEntityAxis) the table is dropped
rather than shown as a breakdown. All-zero rows are dropped. Every number is
a filed value or plain arithmetic on filed values; nothing is estimated.

Labels and the member hierarchy come from the filing's label and definition
linkbases (<basename>_lab.xml / _def.xml, else the *_lab.xml / *_def.xml in
index.json); filers whose linkbases are embedded in the schema (DFIN /
ActiveDisclosure-style: only <basename>.xsd and the instance in the folder)
are read from the .xsd. De-camel-cased names are the last resort.

Output: <TICKER>/segments.json (schema in build_output). A company with no
dimensioned facts gets a file with empty tables and a warning; a filing with
no instance gets a warning; a missing concept never crashes anything. The
payload's `complete` is false when any filing's instance could not be
fetched or parsed; `--all` re-fetches such folders instead of skipping them.
"""
import csv
import datetime
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.environ.get("STOCKS_BASE") or os.path.dirname(HERE)
SYS = f"{BASE}/_system"
UA = {"User-Agent": "Muse research andrewmauro199612@gmail.com", "Accept-Encoding": "identity"}
MIN_INTERVAL = 0.11  # seconds between EDGAR requests: at most 10 requests/second
TIMEOUT = 90
SOURCE = "SEC EDGAR XBRL instance documents"
ARCHIVE = "https://www.sec.gov/Archives/edgar/data"
from zoneinfo import ZoneInfo
TODAY = datetime.datetime.now(ZoneInfo("America/New_York")).date()  # Codex review of PR #2: the VM runs UTC

XBRLI = "http://www.xbrl.org/2003/instance"
XBRLDI = "http://xbrl.org/2006/xbrldi"
LINK = "http://www.xbrl.org/2003/linkbase"
XLINK = "http://www.w3.org/1999/xlink"
XSI = "http://www.w3.org/2001/XMLSchema-instance"
STD_LABEL_ROLE = "http://www.xbrl.org/2003/role/label"

ANNUAL_FORMS = ("10-K", "20-F", "40-F")
QUARTER_FORMS = ("10-Q",)

# canonical concept -> (display label, "duration" | "instant")
CONCEPTS = {
    "Revenues": ("Revenue", "duration"),
    "RevenueFromContractWithCustomerExcludingAssessedTax": ("Revenue from contracts with customers", "duration"),
    "SalesRevenueNet": ("Net sales", "duration"),
    "OperatingIncomeLoss": ("Operating income", "duration"),
    "NetIncomeLoss": ("Net income", "duration"),
    "ProfitLoss": ("Net income incl. noncontrolling interests", "duration"),
    "Assets": ("Total assets", "instant"),
    "InterestIncomeExpenseNet": ("Net interest income", "duration"),
    "NoninterestIncome": ("Noninterest income", "duration"),
    "Deposits": ("Deposits", "instant"),
    "LoansAndLeasesReceivableNetReportedAmount": ("Loans and leases, net", "instant"),
    "DepreciationDepletionAndAmortization": ("Depreciation & amortization", "duration"),
    "PaymentsToAcquirePropertyPlantAndEquipment": ("Capital expenditures", "duration"),
}
# filed QName (canonical prefix) -> canonical concept
TAG_TO_CONCEPT = {f"us-gaap:{c}": c for c in CONCEPTS}
TAG_TO_CONCEPT.update({
    "ifrs-full:Revenue": "Revenues",
    "ifrs-full:RevenueFromContractsWithCustomers": "RevenueFromContractWithCustomerExcludingAssessedTax",
    "ifrs-full:ProfitLossFromOperatingActivities": "OperatingIncomeLoss",
    "ifrs-full:ProfitLoss": "ProfitLoss",
    "ifrs-full:ProfitLossAttributableToOwnersOfParent": "NetIncomeLoss",
    "ifrs-full:Assets": "Assets",
    "ifrs-full:DepreciationAndAmortisationExpense": "DepreciationDepletionAndAmortization",
    "ifrs-full:PurchaseOfPropertyPlantAndEquipmentClassifiedAsInvestingActivities": "PaymentsToAcquirePropertyPlantAndEquipment",
})
# a secondary concept is dropped when its primary already yields a table on the same axis / periodicity
SECONDARY_OF = {"ProfitLoss": "NetIncomeLoss"}
# concepts whose rows partition the consolidated figure (so rows covering under half of it are a leftover, not a
# breakdown); profit concepts are excluded because an untagged corporate loss legitimately flips the sign
PARTITION_CONCEPTS = {c for c in CONCEPTS if c not in ("OperatingIncomeLoss", "NetIncomeLoss", "ProfitLoss")}

AXES = {
    "us-gaap:StatementBusinessSegmentsAxis": "business_segments",
    "ifrs-full:SegmentsAxis": "business_segments",
    "srt:ProductOrServiceAxis": "product",
    "ifrs-full:ProductsAndServicesAxis": "product",
    "srt:StatementGeographicalAxis": "geography",
    "ifrs-full:GeographicalAreasAxis": "geography",
}
AXIS_LABEL = {"business_segments": "segment", "product": "product / service", "geography": "geography"}
CONSOLIDATION_AXES = {"srt:ConsolidationItemsAxis", "us-gaap:ConsolidationItemsAxis", "ifrs-full:SegmentConsolidationItemsAxis"}
OPERATING_SEGMENT_MEMBERS = {"us-gaap:OperatingSegmentsMember", "ifrs-full:OperatingSegmentsMember"}
RECONCILING_RE = re.compile(r"Corporate|Eliminat|Reconcil|Unallocated|Intersegment|AllOther|OtherSegment|NonSegment|Other(Member|Domain)$", re.I)
# a member whose name says it is a subtotal of the other members on its axis
SUBTOTAL_RE = re.compile(r"Total|Subtotal|ReportableSegments|ReportingSegments|AllSegments|IncludingOther", re.I)
STANDARD_PREFIXES = ("us-gaap", "ifrs-full", "srt")
DOMAIN_MEMBER_ARCROLE = "http://xbrl.org/int/dim/arcrole/domain-member"
# warnings that mean a filing was not read (transient EDGAR failures included): --all must retry these
FAILURE_RE = re.compile(r"Error\b|unreadable|no XBRL instance document|timed out|Timeout", re.I)
TIE_TOLERANCE = 0.0005  # rows "tie" to the consolidated fact within 0.05% (filed sums tie exactly; this absorbs rounding)
MISMATCH_TOLERANCE = 0.02  # beyond 2% the table is flagged ties_to_total: false
LEFTOVER_COVERAGE = 0.1   # rows covering under a tenth of the consolidated fact are leftovers, not a breakdown

MAX_ROWS = 12
MAX_ANNUAL_COLS = 4
MAX_QUARTER_COLS = 8


# ---------------------------------------------------------------------------
# EDGAR access (rate limited, retried)
# ---------------------------------------------------------------------------
class NotFound(Exception):
    pass


_last_request = [0.0]


def fetch(url, timeout=TIMEOUT):
    """GET url with the project's User-Agent, <= 10 req/s, 3 attempts with backoff. 404 raises NotFound at once."""
    last = None
    for attempt in range(3):
        wait = MIN_INTERVAL - (time.time() - _last_request[0])
        if wait > 0:
            time.sleep(wait)
        _last_request[0] = time.time()
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise NotFound(url)
            last = e
        except Exception as e:  # timeouts, resets
            last = e
        if attempt < 2:
            time.sleep(2 ** attempt)
    raise last


def get_json(url):
    return json.loads(fetch(url))


def resolve_cik(ticker, nums, argv=None):
    argv = sys.argv if argv is None else argv
    if "--cik" in argv:
        return int(argv[argv.index("--cik") + 1])
    if nums.get("cik"):
        return int(nums["cik"])
    try:
        sec = json.load(open(f"{SYS}/sec_tickers_exchange.json", encoding="utf-8"))
        m = {}
        for rec in sec["data"]:
            m.setdefault(str(rec[2]).upper(), rec[0])
        for cand in (ticker, ticker.replace("/", "-"), ticker.replace("/", ".")):
            if cand in m:
                return int(m[cand])
    except Exception:
        pass
    try:
        with open(f"{SYS}/universe.csv", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row.get("ticker") == ticker and row.get("cik"):
                    return int(row["cik"])
    except Exception:
        pass
    return None


# ---------------------------------------------------------------------------
# Filing selection
# ---------------------------------------------------------------------------
def select_filings(sub):
    """Latest annual report (10-K / 20-F / 40-F) and the latest two 10-Qs from a submissions payload.
    Returns (filings, fiscal_year_end_mmdd). Amendments (/A) are skipped."""
    rec = sub.get("filings", {}).get("recent", {})
    forms, accs, fds, rds, docs = (rec.get(k, []) for k in ("form", "accessionNumber", "filingDate", "reportDate", "primaryDocument"))
    annual, quarters = None, []
    for i, form in enumerate(forms):
        if form in ANNUAL_FORMS and annual is None:
            annual = {"form": form, "accession": accs[i], "filed": fds[i], "period": rds[i], "primary": docs[i]}
        elif form in QUARTER_FORMS and len(quarters) < 2:
            quarters.append({"form": form, "accession": accs[i], "filed": fds[i], "period": rds[i], "primary": docs[i]})
    out = [f for f in [annual] + quarters if f]
    out.sort(key=lambda f: (f["filed"], f["accession"]))  # oldest first: later filings overwrite
    return out, (sub.get("fiscalYearEnd") or None)


def instance_candidates(cik, filing):
    acc = filing["accession"].replace("-", "")
    base = (filing.get("primary") or "").rsplit(".", 1)[0]
    folder = f"{ARCHIVE}/{int(cik)}/{acc}"
    return folder, base


def _is_instance_name(name):
    low = name.lower()
    if not low.endswith(".xml"):
        return False
    return not any(s in low for s in ("_cal", "_def", "_lab", "_pre", "filingsummary"))


def locate_files(cik, filing, index_cache):
    """Return (instance_url, label_url, warnings) for a filing, following the README order:
    <basename>_htm.xml first, then the filing's index.json."""
    folder, base = instance_candidates(cik, filing)
    warnings = []
    inst_url = lab_url = None

    def index_names():
        if folder not in index_cache:
            try:
                j = get_json(f"{folder}/index.json")
                index_cache[folder] = [it.get("name", "") for it in j.get("directory", {}).get("item", [])]
            except Exception as e:
                index_cache[folder] = []
                warnings.append(f"{filing['form']} {filing['accession']}: index.json unreadable ({e})")
        return index_cache[folder]

    if base:
        guess = f"{folder}/{base}_htm.xml"
        try:
            data = fetch(guess)
            return guess, data, base, folder, index_names, warnings
        except NotFound:
            pass
    names = index_names()
    cands = [n for n in names if _is_instance_name(n)]
    cands.sort(key=lambda n: (0 if "_htm" in n.lower() else 1, n))
    for n in cands:
        try:
            data = fetch(f"{folder}/{n}")
            return f"{folder}/{n}", data, base, folder, index_names, warnings
        except NotFound:
            continue
    warnings.append(f"{filing['form']} {filing['accession']} ({filing['period']}): no XBRL instance document found")
    return None, None, base, folder, index_names, warnings


def _linkbase_candidates(base, folder, index_names, suffix):
    """URLs to try for a linkbase: <basename><suffix> first, then every index.json name with that suffix."""
    tried = []
    if base:
        tried.append(f"{folder}/{base}{suffix}")
    for n in index_names():
        if n.lower().endswith(suffix.lower()) and f"{folder}/{n}" not in tried:
            tried.append(f"{folder}/{n}")
    return tried


def _fetch_first(urls, parser, warnings, filing, what):
    """Parse the first URL that exists; None when none does (a parse error warns and counts as found-but-empty)."""
    for url in urls:
        try:
            return parser(io.BytesIO(fetch(url)))
        except NotFound:
            continue
        except Exception as e:
            warnings.append(f"{filing['form']} {filing['accession']}: {what} unreadable ({e})")
            return {}
    return None


def fetch_linkbases(base, folder, index_names, warnings, filing):
    """The filing's standard labels and member hierarchy -> (labels, hierarchy).
    Separate linkbases first (<basename>_lab.xml / _def.xml, else the *_lab.xml / *_def.xml in index.json);
    whatever is still missing is read from the filing's schema (<basename>.xsd, else the *.xsd in index.json),
    where DFIN / ActiveDisclosure-style filings embed every linkbase. Fetched once per filing each."""
    labels = _fetch_first(_linkbase_candidates(base, folder, index_names, "_lab.xml"), parse_labels, warnings, filing, "label linkbase")
    hierarchy = _fetch_first(_linkbase_candidates(base, folder, index_names, "_def.xml"), parse_definitions, warnings, filing, "definition linkbase")
    if labels is None or hierarchy is None:
        xsd = None
        for url in _linkbase_candidates(base, folder, index_names, ".xsd"):
            try:
                xsd = fetch(url)
                break
            except NotFound:
                continue
            except Exception as e:
                warnings.append(f"{filing['form']} {filing['accession']}: schema unreadable ({e})")
                break
        if xsd is not None:
            if labels is None:
                try:
                    labels = parse_labels(io.BytesIO(xsd)) or None
                except Exception as e:
                    warnings.append(f"{filing['form']} {filing['accession']}: labels embedded in the schema unreadable ({e})")
            if hierarchy is None:
                try:
                    hierarchy = parse_definitions(io.BytesIO(xsd))
                except Exception:
                    hierarchy = {}
    if labels is None:
        warnings.append(f"{filing['form']} {filing['accession']}: no label linkbase found; member names de-camel-cased")
        labels = {}
    return labels, hierarchy or {}


# ---------------------------------------------------------------------------
# XML parsing (pure functions; tested on inline fixtures)
# ---------------------------------------------------------------------------
def ns_prefix(uri):
    """Canonical prefix for a namespace URI (taxonomy versions collapse), else None."""
    if re.match(r"https?://fasb\.org/us-gaap/", uri):
        return "us-gaap"
    if re.match(r"https?://fasb\.org/srt/", uri):
        return "srt"
    if re.match(r"https?://xbrl\.sec\.gov/dei/", uri):
        return "dei"
    if re.match(r"https?://xbrl\.sec\.gov/country/", uri):
        return "country"
    if "ifrs.org" in uri and uri.rstrip("/").endswith("ifrs-full"):
        return "ifrs-full"
    return None


def canon_qname(q, nsmap):
    """'pfx:Local' as written in the instance -> canonical 'us-gaap:Local' etc. (filer prefixes stay)."""
    if ":" not in q:
        return q
    pfx, local = q.split(":", 1)
    uri = nsmap.get(pfx)
    if uri:
        canon = ns_prefix(uri)
        if canon:
            return f"{canon}:{local}"
    return f"{pfx}:{local}"


def _split_tag(tag):
    m = re.match(r"\{([^}]*)\}(.+)", tag)
    return (m.group(1), m.group(2)) if m else ("", tag)


def parse_instance(source):
    """Parse an XBRL instance (path, bytes or file object) with iterparse.
    Returns {"contexts": {id: {start, end, instant, dims: {axis: member}, typed: bool}},
             "units": {id: measure}, "facts": [{concept, tag, context, unit, value}], "dei": {...}}.
    QNames are canonicalised (any us-gaap taxonomy year -> 'us-gaap:')."""
    if isinstance(source, (bytes, bytearray)):
        source = io.BytesIO(source)
    elif isinstance(source, str) and not os.path.exists(source):
        source = io.BytesIO(source.encode("utf-8"))
    nsmap = {}
    contexts, units, facts, dei = {}, {}, [], {}
    depth = 0
    for ev, el in ET.iterparse(source, events=("start-ns", "start", "end")):
        if ev == "start-ns":
            nsmap[el[0]] = el[1]
            continue
        if ev == "start":
            depth += 1
            continue
        depth -= 1
        if depth != 1:
            continue
        uri, local = _split_tag(el.tag)
        if uri == XBRLI and local == "context":
            contexts[el.get("id")] = _parse_context(el, nsmap)
        elif uri == XBRLI and local == "unit":
            units[el.get("id")] = _parse_unit(el)
        else:
            pfx = ns_prefix(uri)
            if pfx == "dei" and local in ("DocumentFiscalYearFocus", "DocumentFiscalPeriodFocus", "CurrentFiscalYearEndDate", "DocumentPeriodEndDate", "DocumentType"):
                dei[local] = (el.text or "").strip()
            elif pfx in ("us-gaap", "ifrs-full"):
                tag = f"{pfx}:{local}"
                concept = TAG_TO_CONCEPT.get(tag)
                if concept and el.get(f"{{{XSI}}}nil") != "true" and el.get("contextRef"):
                    try:
                        value = float((el.text or "").strip())
                    except ValueError:
                        value = None
                    if value is not None:
                        facts.append({"concept": concept, "tag": tag, "context": el.get("contextRef"), "unit": el.get("unitRef"), "value": value})
        el.clear()
    return {"contexts": contexts, "units": units, "facts": facts, "dei": dei}


def _parse_context(el, nsmap):
    ctx = {"start": None, "end": None, "instant": None, "dims": {}, "typed": False}
    for node in el.iter():
        uri, local = _split_tag(node.tag)
        if uri == XBRLI and local in ("startDate", "endDate", "instant"):
            ctx[{"startDate": "start", "endDate": "end", "instant": "instant"}[local]] = (node.text or "").strip()
        elif uri == XBRLDI and local == "explicitMember":
            ctx["dims"][canon_qname(node.get("dimension", ""), nsmap)] = canon_qname((node.text or "").strip(), nsmap)
        elif uri == XBRLDI and local == "typedMember":
            ctx["typed"] = True
    return ctx


def _parse_unit(el):
    measures = [(n.text or "").strip() for n in el.iter() if _split_tag(n.tag) == (XBRLI, "measure")]
    return measures[0] if len(measures) == 1 else "/".join(measures)


def parse_labels(source):
    """Label linkbase -> {element id fragment (e.g. 'app_SoftwarePlatformSegmentMember'): standard label}."""
    if isinstance(source, (bytes, bytearray)):
        source = io.BytesIO(source)
    elif isinstance(source, str) and not os.path.exists(source):
        source = io.BytesIO(source.encode("utf-8"))
    locs, labels, arcs = {}, {}, []
    for ev, el in ET.iterparse(source, events=("end",)):
        uri, local = _split_tag(el.tag)
        if uri != LINK:
            continue
        if local == "loc":
            href = el.get(f"{{{XLINK}}}href", "")
            locs[el.get(f"{{{XLINK}}}label")] = href.split("#", 1)[1] if "#" in href else href
        elif local == "label":
            if el.get(f"{{{XLINK}}}role") == STD_LABEL_ROLE:
                labels.setdefault(el.get(f"{{{XLINK}}}label"), (el.text or "").strip())
        elif local == "labelArc":
            arcs.append((el.get(f"{{{XLINK}}}from"), el.get(f"{{{XLINK}}}to")))
        if local in ("loc", "label", "labelArc"):
            el.clear()
    out = {}
    for frm, to in arcs:
        frag, text = locs.get(frm), labels.get(to)
        if frag and text:
            out[frag] = text
    return out


def parse_definitions(source):
    """Definition linkbase (or a schema with one embedded) -> {parent fragment: {child fragments}} from the
    domain-member arcs, i.e. the member hierarchy of every axis (us-gaap_ProductMember -> alny_TTRMember ->
    alny_AmvuttraMember). Locators are resolved per extended link. Works on a bare linkbase and on an .xsd."""
    if isinstance(source, (bytes, bytearray)):
        source = io.BytesIO(source)
    elif isinstance(source, str) and not os.path.exists(source):
        source = io.BytesIO(source.encode("utf-8"))
    out, locs, arcs = {}, {}, []

    def flush():
        for frm, to in arcs:
            a, b = locs.get(frm), locs.get(to)
            if a and b and a != b:
                out.setdefault(a, set()).add(b)
        locs.clear(); arcs.clear()

    for ev, el in ET.iterparse(source, events=("end",)):
        uri, local = _split_tag(el.tag)
        if uri != LINK:
            continue
        if local == "loc":
            href = el.get(f"{{{XLINK}}}href", "")
            locs[el.get(f"{{{XLINK}}}label")] = href.split("#", 1)[1] if "#" in href else href
        elif local == "definitionArc":
            if el.get(f"{{{XLINK}}}arcrole") == DOMAIN_MEMBER_ARCROLE:
                arcs.append((el.get(f"{{{XLINK}}}from"), el.get(f"{{{XLINK}}}to")))
        elif local == "definitionLink":
            flush()
        if local in ("loc", "definitionArc", "definitionLink"):
            el.clear()
    flush()
    return out


def descendants(frag, hierarchy):
    """Every fragment below `frag` in the domain-member hierarchy (transitive, cycle-safe)."""
    seen, stack = set(), list(hierarchy.get(frag, ()))
    while stack:
        f = stack.pop()
        if f in seen:
            continue
        seen.add(f)
        stack.extend(hierarchy.get(f, ()))
    return seen


def fallback_label(qname):
    """'hban:ConsumerAndBusinessBankingMember' -> 'Consumer And Business Banking'."""
    local = qname.split(":", 1)[-1]
    local = re.sub(r"(Member|Domain)$", "", local)
    local = re.sub(r"Segment$", "", local)
    words = re.sub(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])", " ", local).strip()
    return words or qname


def member_label(qname, labels):
    frag = qname.replace(":", "_", 1)
    text = labels.get(frag)
    if text:
        return re.sub(r"\s*\[(member|domain)\]\s*$", "", text, flags=re.I).strip() or fallback_label(qname)
    return fallback_label(qname)


def classify_context(ctx):
    """-> ("consolidated", None, None, None) | ("row", axis, member, None) | ("ignore", None, None, None).
    A kept-axis member alone (or with the OperatingSegmentsMember on a consolidation axis) is a row. A
    context whose only dimension is a ConsolidationItemsAxis reconciling member (corporate, eliminations)
    becomes a business_segments row keyed by that member; the operating-segments subtotal alone is ignored.
    A kept-axis member plus a reconciling consolidation member is a matrix cell already inside the bare
    member's figure (Huntington's product x Corporate, Expedia's trivago x Intersegment) and is ignored,
    like every other multi-axis context. The fourth slot is kept for compatibility and is always None."""
    if ctx.get("typed"):
        return ("ignore", None, None, None)
    dims = ctx.get("dims") or {}
    if not dims:
        return ("consolidated", None, None, None)
    kept = [(AXES[a], m) for a, m in dims.items() if a in AXES]
    consol = [m for a, m in dims.items() if a in CONSOLIDATION_AXES]
    other = [a for a in dims if a not in AXES and a not in CONSOLIDATION_AXES]
    if other or len(kept) > 1 or len(consol) > 1:
        return ("ignore", None, None, None)
    if len(kept) == 1:
        if consol and consol[0] not in OPERATING_SEGMENT_MEMBERS:
            return ("ignore", None, None, None)
        return ("row", kept[0][0], kept[0][1], None)
    if consol and consol[0] not in OPERATING_SEGMENT_MEMBERS:
        return ("row", "business_segments", consol[0], None)
    return ("ignore", None, None, None)


def is_consolidation_only(ctx):
    """True when the context's only dimension is a consolidation axis (a bare eliminations / corporate row)."""
    dims = ctx.get("dims") or {}
    return bool(dims) and all(a in CONSOLIDATION_AXES for a in dims)


def has_opseg(ctx):
    """True when the context carries the OperatingSegmentsMember on a consolidation axis. Some filers
    (Expedia) tag a segment's revenue twice in one filing: bare member = external revenue, the figure that
    ties to the consolidated total, and member + OperatingSegmentsMember = the segment's gross figure
    before intersegment eliminations. The bare fact wins within a filing."""
    return any(a in CONSOLIDATION_AXES and m in OPERATING_SEGMENT_MEMBERS for a, m in (ctx.get("dims") or {}).items())


def is_reconciling(member, consol_only=False):
    """A corporate / eliminations / reconciling row: any consolidation-axis-only context, or a kept-axis
    member whose name says so (expe:CorporateAndEliminationsMember, gfi:CorporateAndOtherDomain)."""
    local = member.split(":", 1)[-1]
    return bool(consol_only) or bool(RECONCILING_RE.search(local))


def is_standard(member):
    return member.split(":", 1)[0] in STANDARD_PREFIXES


def normalized_name(member):
    """Local name minus the Member / Domain / Segment decorations, lower-cased, for spotting one member
    tagged under two names (axon:SoftwareAndSensorsMember vs axon:SoftwareAndSensorsSegmentMember)."""
    local = member.split(":", 1)[-1]
    local = re.sub(r"(Member|Domain)$", "", local)
    return re.sub(r"Segments?", "", local).lower()


def _d(s):
    return datetime.date.fromisoformat(s)


def period_kind(start, end):
    """Inclusive day count -> 'annual' (330-380), 'quarter' (77-120: 12- or 16-week quarters too),
    '6m' (170-200), '9m' (250-290) or None."""
    try:
        days = (_d(end) - _d(start)).days + 1
    except Exception:
        return None
    if 330 <= days <= 380:
        return "annual"
    if 77 <= days <= 120:
        return "quarter"
    if 170 <= days <= 200:
        return "6m"
    if 250 <= days <= 290:
        return "9m"
    return None


# ---------------------------------------------------------------------------
# Fiscal calendar (labels only — never a number)
# ---------------------------------------------------------------------------
class FiscalCalendar:
    """FY / quarter labels in the filer's own naming, anchored on a filing's dei facts
    (DocumentFiscalYearFocus + DocumentPeriodEndDate + CurrentFiscalYearEndDate). Without any
    dei anchor the fiscal year is named after the calendar year its period ends in."""

    def __init__(self, fye_mmdd=None, anchor_end=None, anchor_fy=None, anchor_focus=None):
        self.fye = fye_mmdd  # (month, day) or None
        self.anchor_fy_end = None
        self.anchor_fy = None
        if anchor_end and anchor_fy and self.fye:
            end = _d(anchor_end)
            self.anchor_fy_end = self._fye_on_or_after(end) if (anchor_focus or "").upper() != "FY" else end
            self.anchor_fy = int(anchor_fy)

    @classmethod
    def from_filings(cls, parsed_filings, sub_fye=None):
        """Prefer the latest filing with complete dei anchors; fall back to the submissions fiscalYearEnd."""
        fye = None
        for pf in reversed(parsed_filings):
            dei = (pf.get("instance") or {}).get("dei") or {}
            mmdd = cls._mmdd(dei.get("CurrentFiscalYearEndDate")) or cls._mmdd(sub_fye)
            if mmdd and dei.get("DocumentFiscalYearFocus") and dei.get("DocumentPeriodEndDate"):
                try:
                    focus, end = int(dei["DocumentFiscalYearFocus"]), _d(dei["DocumentPeriodEndDate"])
                    # a fiscal year is named after the calendar year it ends or starts in; a filing whose
                    # DocumentFiscalYearFocus is further off (Mettler-Toledo's Q2 2026 10-Q says 2024) is a
                    # filer error and the next filing anchors instead
                    if abs(focus - end.year) <= 1:
                        return cls(mmdd, dei["DocumentPeriodEndDate"], focus, dei.get("DocumentFiscalPeriodFocus"))
                except Exception:
                    pass
            fye = fye or mmdd
        return cls(fye or cls._mmdd(sub_fye))

    @staticmethod
    def _mmdd(s):
        if not s:
            return None
        m = re.search(r"(\d{2})-?(\d{2})$", s.strip())
        if not m:
            return None
        mo, da = int(m.group(1)), int(m.group(2))
        return (mo, da) if 1 <= mo <= 12 and 1 <= da <= 31 else None

    def _nominal(self, year):
        mo, da = self.fye
        while da > 28:
            try:
                return datetime.date(year, mo, da)
            except ValueError:
                da -= 1
        return datetime.date(year, mo, da)

    def _fye_on_or_after(self, d):
        """Nominal fiscal year end on/after d (52/53-week ends drift a few days; a date within 7 days
        after a nominal FYE is treated as that FYE). The previous calendar year's FYE is tested first so
        a December year that drifts into early January (year ended 2024-01-02 on a --12-31 calendar) is
        FY2023, not FY2024."""
        prev = self._nominal(d.year - 1)
        if 0 <= (d - prev).days <= 7:
            return prev
        cand = self._nominal(d.year)
        if cand < d:
            if (d - cand).days <= 7:
                return cand
            cand = self._nominal(d.year + 1)
        return cand

    def fiscal_year(self, end):
        """Fiscal year number of the period ending `end` (ISO)."""
        e = _d(end)
        if self.anchor_fy_end is None or not self.fye:
            return e.year
        fy_end = self._fye_on_or_after(e)
        return self.anchor_fy + round((fy_end - self.anchor_fy_end).days / 365.25)

    def quarter_number(self, end):
        if not self.fye:
            return None
        e = _d(end)
        fy_end = self._fye_on_or_after(e)
        prev = self._nominal(fy_end.year - 1)
        q = round((e - prev).days / 91.3)
        return q if 1 <= q <= 4 else None

    def label(self, kind, end, derived_q4=False):
        fy = self.fiscal_year(end)
        if kind == "annual":
            return f"FY{fy}"
        if derived_q4:
            return f"Q4 FY{fy}"
        q = self.quarter_number(end)
        if kind == "quarter":
            return f"Q{q} FY{fy}" if q else f"3M to {end}"
        if kind == "instant":
            if q == 4 or (self.fye and abs((_d(end) - self._fye_on_or_after(_d(end))).days) <= 7):
                return f"FY{fy} end"
            return f"Q{q} FY{fy}" if q else f"at {end}"
        return end


# ---------------------------------------------------------------------------
# Table assembly (pure; the tests drive it with parsed fixtures)
# ---------------------------------------------------------------------------
def _currency_of(measure):
    if measure and measure.lower().startswith("iso4217:"):
        return measure.split(":", 1)[1].upper()
    return None


def collect_cells(parsed_filings, warnings):
    """Join facts to contexts across filings (oldest first, so the latest filing wins).
    Returns (cells, totals, currency, member_labels, n_dimensioned):
      cells[(concept, axis, row_key)][period_key] = cell  with period_key = ("annual"|"quarter"|"6m"|"9m", start, end)
                                                            or ("instant", None, date)
      totals[concept][period_key] = cell (undimensioned facts)."""
    cells, totals, labels = {}, {}, {}
    currencies = {}
    n_dim = 0
    raw = []
    for idx, pf in enumerate(parsed_filings):
        inst = pf.get("instance")
        if not inst:
            continue
        labels.update(pf.get("labels") or {})
        ctxs, units = inst["contexts"], inst["units"]
        for f in inst["facts"]:
            ctx = ctxs.get(f["context"])
            if not ctx:
                continue
            cur = _currency_of(units.get(f["unit"]))
            if not cur:
                continue
            kind_cls = classify_context(ctx)
            if kind_cls[0] == "ignore":
                continue
            if ctx["instant"]:
                pkey = ("instant", None, ctx["instant"])
                if CONCEPTS[f["concept"]][1] != "instant":
                    continue
            else:
                pk = period_kind(ctx["start"], ctx["end"])
                if not pk or CONCEPTS[f["concept"]][1] != "duration":
                    continue
                pkey = (pk, ctx["start"], ctx["end"])
            raw.append((idx, pf["form"], f, kind_cls, pkey, cur, has_opseg(ctx), is_consolidation_only(ctx)))
            currencies[cur] = currencies.get(cur, 0) + 1
    currency = max(currencies, key=currencies.get) if currencies else None
    dropped = 0

    def put(store, pkey, cell):
        old = store.get(pkey)
        if old is not None:
            cell["forms"] = old["forms"] | cell["forms"]
            if old["filing"] > cell["filing"] or (old["filing"] == cell["filing"] and cell["opseg"] and not old["opseg"]):
                old["forms"] = cell["forms"]
                return  # an earlier filing never overwrites a later one; within a filing the bare member beats OperatingSegmentsMember
        store[pkey] = cell

    for idx, form, f, (cls, axis, member, cm), pkey, cur, opseg, consol_only in raw:
        if cur != currency:
            dropped += 1
            continue
        cell = {"value": f["value"], "tag": f["tag"], "filing": idx, "form": form, "forms": {form}, "derived": False, "opseg": opseg}
        if cls == "consolidated":
            put(totals.setdefault(f["concept"], {}), pkey, cell)
        else:
            n_dim += 1
            cell.update({"member": member, "consol_only": consol_only})
            put(cells.setdefault((f["concept"], axis, member), {}), pkey, cell)
    if dropped:
        warnings.append(f"{dropped} facts in a currency other than {currency} were ignored")
    return cells, totals, currency, labels, n_dim


def derive_q4(cells, totals):
    """Q4 = FY minus the nine-month leg, only when both exist for the same member with the same start."""
    for store in [cells] + [{(c, None, None): p for c, p in totals.items()}]:
        for key, periods in store.items():
            annuals = [pk for pk in periods if pk[0] == "annual"]
            for pk in annuals:
                _, s, e = pk
                for nk in [k for k in periods if k[0] == "9m" and k[1] == s]:
                    gap = (_d(e) - _d(nk[2])).days
                    if not 77 <= gap <= 120:
                        continue
                    q4_end = e
                    q4_start = (_d(nk[2]) + datetime.timedelta(days=1)).isoformat()
                    if any(k[0] == "quarter" and k[2] == q4_end for k in periods):
                        continue
                    fy, nine = periods[pk], periods[nk]
                    periods[("quarter", q4_start, q4_end)] = {
                        "value": fy["value"] - nine["value"], "tag": fy["tag"], "filing": max(fy["filing"], nine["filing"]),
                        "form": fy["form"], "forms": fy["forms"] | nine["forms"], "derived": True, "opseg": fy.get("opseg", False),
                        "member": fy.get("member"), "consol_only": fy.get("consol_only", False)}
    return cells, totals


def _sig(row):
    return tuple(c["value"] if c else None for c in row["_vals"])


def _close(a, b):
    return abs(a - b) <= 1e-6 * max(1.0, abs(a), abs(b))


def subtotal_parts(row, others):
    """The other rows whose values sum, in every column the row has, to the row's values (at least two parts,
    at least two non-zero matched columns), else None. Subsets are enumerated up to 12 candidates; beyond
    that only "all the other rows" is tested."""
    cols = [i for i, c in enumerate(row["_vals"]) if c is not None]
    if sum(1 for i in cols if row["_vals"][i]["value"] != 0) < 2:
        return None
    cands = [o for o in others if all(o["_vals"][i] is not None for i in cols)]
    if len(cands) < 2:
        return None
    target = [row["_vals"][i]["value"] for i in cols]

    def matches(subset):
        return all(_close(sum(o["_vals"][i]["value"] for o in subset), target[k]) for k, i in enumerate(cols))

    if len(cands) > 12:
        return cands if matches(cands) else None
    n = len(cands)
    for mask in range(1, 1 << n):
        if mask & (mask - 1) == 0:
            continue  # single row
        subset = [cands[j] for j in range(n) if mask >> j & 1]
        if matches(subset):
            return subset
    return None


def drop_subtotal_rows(rows, hierarchy, warnings, name):
    """Rows that double count the others, each dropped with a warning: a member named as a subtotal, an
    ancestor (definition linkbase) of another row, a row equal to the sum of two or more other rows
    (nested subtotals iterate), and one member tagged under two names with identical numbers."""
    def drop(r, why):
        warnings.append(f"{name}: row '{r['label']}' ({r['member']}) dropped: {why}")

    keep = []
    for r in rows:
        if SUBTOTAL_RE.search(r["member"].split(":", 1)[-1]):
            drop(r, "its name marks it as a subtotal of the other rows")
        else:
            keep.append(r)
    rows = keep
    if hierarchy:
        frag_of = {r["member"].replace(":", "_", 1): r for r in rows}
        keep = []
        for r in rows:
            below = descendants(r["member"].replace(":", "_", 1), hierarchy) & set(frag_of)
            if below:
                drop(r, "it is the parent of " + ", ".join(sorted(frag_of[f]["label"] for f in below)) + " in the filing's definition linkbase")
            else:
                keep.append(r)
        rows = keep
    changed = True
    while changed and len(rows) > 2:
        changed = False
        for r in rows:
            parts = subtotal_parts(r, [o for o in rows if o is not r])
            if parts:
                drop(r, "its values equal the sum of " + ", ".join(p["label"] for p in parts))
                rows = [o for o in rows if o is not r]
                changed = True
                break
    # one line tagged under two members with identical numbers (Axon: SoftwareAndSensorsSegment /
    # SoftwareAndServicesSegment, us-gaap Service / SoftwareAndServices): the filer's own member is kept over a
    # standard one, then the member the latest filing carries
    def rank(r):
        return (is_standard(r["member"]), -max(c["filing"] for c in r["_vals"] if c))
    keep = []
    for r in sorted(rows, key=rank):
        dup = next((k for k in keep if same_line(k, r)), None)
        if dup is not None:
            drop(r, f"same numbers as '{dup['label']}' ({dup['member']})")
            continue
        keep.append(r)
    order = {id(r): i for i, r in enumerate(rows)}
    keep.sort(key=lambda r: order[id(r)])
    return keep


def same_line(a, b):
    """Identical numbers in every column, with two or more non-zero columns, or with one and the same
    normalized member name: the same line under two member names, not two lines that coincide."""
    sa, sb = _sig(a), _sig(b)
    if sa != sb:
        return False
    nonzero = sum(1 for v in sa if v)
    return nonzero >= 2 or (nonzero == 1 and normalized_name(a["member"]) == normalized_name(b["member"]))


def dedupe_reconciling(rows, warnings=None, name=""):
    """A reconciling line the filer tagged twice with identical numbers (Expedia: "Corporate & Eliminations"
    on the consolidation axis AND the bare us-gaap IntersegmentEliminationMember) is shown once under the
    filer's own member. Only a standard-taxonomy consolidation-only row is ever collapsed, and only into a
    reconciling row carrying a filer extension member (on the kept axis or the consolidation axis) with
    exactly the same numbers; two rows that merely coincide otherwise both stay."""
    own = {}
    for r in rows:
        if r["_recon"] and not is_standard(r["member"]):
            own.setdefault(_sig(r), r)
    out = []
    for r in rows:
        if r["_recon"] and r["_consol_only"] and is_standard(r["member"]) and _sig(r) in own and own[_sig(r)] is not r:
            if warnings is not None:
                warnings.append(f"{name}: row '{r['label']}' ({r['member']}) merged into '{own[_sig(r)]['label']}' ({own[_sig(r)]['member']}): same numbers")
            continue
        out.append(r)
    return out


def drop_total_rows(rows, cons, warnings, name):
    """A row equal to the consolidated fact in every column that has one (two or more columns) is the total
    under a member name (ResMed's rmd:GlobalMember next to two regions covering 88%), not a breakdown row."""
    cols = [i for i, t in enumerate(cons) if t]
    if len(cols) < 2:
        return rows
    keep = []
    for r in rows:
        cells = [r["_vals"][i] for i in cols]
        if all(c is not None for c in cells) and all(_close(c["value"], cons[i]) for c, i in zip(cells, cols)):
            warnings.append(f"{name}: row '{r['label']}' ({r['member']}) dropped: its values equal the consolidated total")
        else:
            keep.append(r)
    return keep


def keep_one_partition(rows, cons, warnings, name):
    """Filers tag two or more complete classifications on one axis (HP: Americas + EMEA + Asia Pacific and
    US + Non-US both sum to revenue; Take-Two: four product splits, 400% of revenue). When the non-reconciling
    rows do not tie but a subset of them sums exactly to the consolidated fact in every column (two or more
    columns), the table keeps that split, the one with the most rows, and drops every other non-reconciling
    row with a warning. Up to 16 candidate rows are searched; larger tables are left as they are."""
    cols = [i for i, t in enumerate(cons) if t]
    if len(cols) < 2:
        return rows
    plain = [r for r in rows if not r["_recon"]]
    if _ties(plain, cons):
        return rows
    cands = [r for r in plain if all(r["_vals"][i] is not None for i in cols)]
    n = len(cands)
    if n < 2 or n > 16:
        return rows
    best = None
    for mask in range(1, 1 << n):
        subset = [cands[j] for j in range(n) if mask >> j & 1]
        if best is not None and len(subset) <= len(best):
            continue
        if all(_close(sum(r["_vals"][i]["value"] for r in subset), cons[i]) for i in cols):
            best = subset
    if best is None or len(best) == len(plain):
        return rows
    kept = {id(r) for r in best}
    split = ", ".join(r["label"] for r in best)
    out = []
    for r in rows:
        if r["_recon"] or id(r) in kept:
            out.append(r)
        else:
            warnings.append(f"{name}: row '{r['label']}' ({r['member']}) dropped: a second classification on the same axis; the table keeps the split that sums to the consolidated total ({split})")
    return out


def _ties(rows, cons):
    """True when the rows sum to the consolidated fact (within TIE_TOLERANCE) in every column that has one."""
    checked = False
    for i, t in enumerate(cons):
        if not t:
            continue
        vals = [r["_vals"][i]["value"] for r in rows if r["_vals"][i] is not None]
        if not vals:
            continue
        checked = True
        if abs(sum(vals) / t - 1) > TIE_TOLERANCE:
            return False
    return checked


def drop_double_counted_reconciling(rows, cons, warnings, name):
    """A reconciling row the other rows already tie to the consolidated fact without is inside them already
    (Expedia's intersegment revenue next to bare external segment figures) and is dropped with a warning.
    Tried one row at a time, then all reconciling rows together; otherwise the rows are left alone."""
    if not any(cons) or _ties(rows, cons):
        return rows
    recon = [r for r in rows if r["_recon"]]
    for r in recon:
        rest = [o for o in rows if o is not r]
        if _ties(rest, cons):
            warnings.append(f"{name}: reconciling row '{r['label']}' ({r['member']}) dropped: the other rows already tie to the consolidated total without it")
            return rest
    if len(recon) > 1:
        rest = [o for o in rows if not o["_recon"]]
        if _ties(rest, cons):
            for r in recon:
                warnings.append(f"{name}: reconciling row '{r['label']}' ({r['member']}) dropped: the other rows already tie to the consolidated total without it")
            return rest
    return rows


def _yoy_prior(end, ends):
    """The column ending ~one year before `end` (350-380 days)."""
    e = _d(end)
    for cand in ends:
        gap = (e - _d(cand)).days
        if 350 <= gap <= 380:
            return cand
    return None


def _fmt(v):
    if v is None:
        return None
    return int(v) if float(v).is_integer() and abs(v) < 1e15 else round(v, 6)


def build_tables(cells, totals, labels, calendar, warnings, hierarchy=None):
    """Group cells into tables per (axis, concept, periodicity); rows sorted by latest value, reconciling rows last.
    `hierarchy` is the merged definition-linkbase member tree ({parent fragment: {child fragments}})."""
    groups = {}
    for (concept, axis, row_key), periods in cells.items():
        for pk, cell in periods.items():
            kind = pk[0]
            if kind == "annual":
                pers = ["annual"]
            elif kind == "quarter":
                pers = ["quarterly"]
            elif kind == "instant":  # a balance-sheet date belongs to every table whose filings carry it
                pers = [p for p, forms in (("annual", ANNUAL_FORMS), ("quarterly", QUARTER_FORMS)) if cell["forms"] & set(forms)]
            else:
                continue
            for periodicity in pers:
                groups.setdefault((axis, concept, periodicity), {}).setdefault(row_key, {})[pk] = cell
    tables = []
    emitted = set()
    order = {"business_segments": 0, "product": 1, "geography": 2}
    concept_order = {c: i for i, c in enumerate(CONCEPTS)}
    for (axis, concept, periodicity) in sorted(groups, key=lambda k: (order[k[0]], concept_order[k[1]], k[2])):
        rows_src = groups[(axis, concept, periodicity)]
        primary = SECONDARY_OF.get(concept)
        if primary and (axis, primary, periodicity) in emitted:
            continue
        # columns: distinct end dates (latest filing wins on a clash)
        col_cells = {}
        for row_key, periods in rows_src.items():
            for pk, cell in periods.items():
                end = pk[2]
                prev = col_cells.get(end)
                if prev is None or cell["filing"] >= prev[1]:
                    col_cells[end] = (pk, cell["filing"])
        ends = sorted(col_cells)
        limit = MAX_ANNUAL_COLS if periodicity == "annual" else MAX_QUARTER_COLS
        if len(ends) > limit:
            ends = ends[-limit:]
        pkeys = {end: col_cells[end][0] for end in ends}
        name = f"{axis}/{concept}/{periodicity}"
        rows = []
        for row_key, periods in rows_src.items():
            vals = [periods.get(pkeys[end]) for end in ends]
            if all(v is None or v["value"] == 0 for v in vals):
                continue  # nothing filed, or an all-zero placeholder row
            any_cell = next(v for v in vals if v is not None)
            member, consol_only = any_cell["member"], bool(any_cell.get("consol_only"))
            rows.append({"member": row_key, "label": member_label(member, labels), "_vals": vals,
                         "_recon": is_reconciling(member, consol_only), "_consol_only": consol_only})
        # consolidated fact per column (None where the filing has none)
        cons = [(totals.get(concept, {}).get(pkeys[end]) or {}).get("value") for end in ends]
        rows = drop_subtotal_rows(rows, hierarchy or {}, warnings, name)
        rows = drop_total_rows(rows, cons, warnings, name)
        rows = keep_one_partition(rows, cons, warnings, name)
        rows = dedupe_reconciling(rows, warnings, name)
        rows = drop_double_counted_reconciling(rows, cons, warnings, name)
        if len(rows) < 2:
            continue
        # totals: consolidated fact for that period when it exists, else the sum of rows
        total_vals, basis = [], []
        for i, end in enumerate(ends):
            if cons[i] is not None:
                total_vals.append(cons[i]); basis.append("consolidated fact")
            else:
                s = [r["_vals"][i]["value"] for r in rows if r["_vals"][i] is not None]
                total_vals.append(sum(s) if s else None); basis.append("sum of rows")
        # does the breakdown tie to the consolidated fact? (latest column that has one)
        ties = None
        for i in range(len(ends) - 1, -1, -1):
            if cons[i]:
                s = [r["_vals"][i]["value"] for r in rows if r["_vals"][i] is not None]
                ratio = sum(s) / cons[i]
                if concept in PARTITION_CONCEPTS and abs(ratio) < LEFTOVER_COVERAGE:
                    ties = "leftover"
                else:
                    ties = abs(ratio - 1) <= MISMATCH_TOLERANCE
                if ties != "leftover" and not ties:
                    warnings.append(f"{name}: rows sum to {ratio:.1%} of the consolidated total for {end} (ties_to_total: false)")
                break
        if ties == "leftover":
            warnings.append(f"{name}: table dropped: its {len(rows)} rows cover {ratio:.1%} of the consolidated total for {end}, not a breakdown of it")
            continue
        rows.sort(key=lambda r: (r["_recon"], -(r["_vals"][-1]["value"] if r["_vals"][-1] is not None else float("-inf"))))
        if len(rows) > MAX_ROWS:
            # the largest MAX_ROWS - 1 rows plus one aggregate of the rest (a plain sum of filed values), so the
            # table shown still ties to the total; the app itself caps a table at MAX_ROWS rows
            rest = rows[MAX_ROWS - 1:]
            agg_vals = []
            for i in range(len(ends)):
                cells = [r["_vals"][i] for r in rest if r["_vals"][i] is not None]
                agg_vals.append({"value": sum(c["value"] for c in cells), "tag": cells[0]["tag"], "filing": max(c["filing"] for c in cells),
                                 "derived": any(c["derived"] for c in cells), "member": "_other"} if cells else None)
            warnings.append(f"{name}: {len(rows)} rows; the {len(rest)} smallest ({', '.join(r['label'] for r in rest)}) are summed into one 'Other' row")
            rows = rows[:MAX_ROWS - 1] + [{"member": "_other", "label": f"Other ({len(rest)} smaller rows)", "_vals": agg_vals, "_recon": True, "_consol_only": False}]
        out_rows = []
        for r in rows:
            values = [c["value"] if c else None for c in r["_vals"]]
            derived = [bool(c and c["derived"]) for c in r["_vals"]]
            share, growth = [], []
            for i, end in enumerate(ends):
                v, t = values[i], total_vals[i]
                share.append(round(v / t, 4) if (v is not None and t) else None)
                prior = _yoy_prior(end, ends[:i])
                pv = values[ends.index(prior)] if prior else None
                growth.append(round(v / pv - 1, 4) if (v is not None and pv is not None and pv > 0) else None)
            out_rows.append({"member": r["member"], "label": r["label"], "values": [_fmt(v) for v in values],
                             "derived": derived, "share_of_total": share, "growth_yoy": growth})
        kind_for_label = "instant" if pkeys[ends[-1]][0] == "instant" else ("annual" if periodicity == "annual" else "quarter")
        period_labels = []
        for end in ends:
            pk = pkeys[end]
            dq4 = pk[0] == "quarter" and all(bool(r["_vals"][ends.index(end)] and r["_vals"][ends.index(end)]["derived"]) for r in rows if r["_vals"][ends.index(end)])
            period_labels.append(calendar.label(kind_for_label, end, derived_q4=dq4))
        tag = next(c["tag"] for r in rows for c in r["_vals"] if c)
        tables.append({
            "axis": axis, "concept": concept, "tag": tag,
            "label": f"{CONCEPTS[concept][0]} by {AXIS_LABEL[axis]}",
            "periodicity": periodicity, "periods": ends, "period_labels": period_labels,
            "rows": out_rows,
            "total": {"values": [_fmt(v) for v in total_vals], "basis": "consolidated fact" if all(b == "consolidated fact" for b in basis) else ("sum of rows" if all(b == "sum of rows" for b in basis) else "mixed: " + ", ".join(basis))},
            "ties_to_total": ties,
        })
        emitted.add((axis, concept, periodicity))
    return tables


def is_complete(payload):
    """True when every filing's instance was read and no warning records a fetch / parse failure."""
    if "complete" in payload:
        return bool(payload["complete"])
    filings = payload.get("filings") or []
    return all(f.get("instance_url") for f in filings) and not any(FAILURE_RE.search(w or "") for w in payload.get("warnings") or [])


def build_output(ticker, cik, parsed_filings, sub_fye=None, warnings=None):
    """parsed_filings: [{"form","accession","filed","period","instance_url","instance": parse_instance(...) or None,
    "labels": parse_labels(...) or {}, "hierarchy": parse_definitions(...) or {}}] oldest first.
    Returns the segments.json payload."""
    warnings = list(warnings or [])
    calendar = FiscalCalendar.from_filings(parsed_filings, sub_fye)
    cells, totals, currency, labels, n_dim = collect_cells(parsed_filings, warnings)
    derive_q4(cells, totals)
    hierarchy = {}
    for pf in parsed_filings:
        for parent, kids in (pf.get("hierarchy") or {}).items():
            hierarchy.setdefault(parent, set()).update(kids)
    tables = build_tables(cells, totals, labels, calendar, warnings, hierarchy)
    if not any(pf.get("instance") for pf in parsed_filings):
        warnings.append("no XBRL instance document could be read for any filing")
    elif n_dim == 0:
        warnings.append("no dimensioned facts for the tracked concepts on the segment / product / geography axes")
    elif not tables:
        warnings.append("dimensioned facts exist but no axis has two members with values for the same concept")
    annual = [pf for pf in parsed_filings if pf["form"] in ANNUAL_FORMS]
    if annual and annual[-1]["form"] != "10-K":
        warnings.append(f"{annual[-1]['form']} filer: no 10-Qs, so quarterly tables are not available")
    return {
        "ticker": ticker, "cik": cik, "as_of": TODAY.isoformat(), "source": SOURCE,
        "filings": [{"form": pf["form"], "accession": pf["accession"], "filed": pf["filed"], "period": pf["period"], "instance_url": pf.get("instance_url")} for pf in parsed_filings],
        "currency": currency,
        "tables": tables,
        "warnings": warnings,
        "complete": all(pf.get("instance") is not None for pf in parsed_filings) and not any(FAILURE_RE.search(w) for w in warnings),
    }


# ---------------------------------------------------------------------------
# Per-company driver
# ---------------------------------------------------------------------------
def latest_accessions(sub):
    filings, _ = select_filings(sub)
    return sorted(f["accession"] for f in filings)


def up_to_date(prev, sub):
    """--all skip predicate: the previous segments.json lists exactly EDGAR's latest filings AND read all of
    them (a file written after a timeout / 503 / unreadable index is re-fetched, never frozen)."""
    try:
        return is_complete(prev) and sorted(f["accession"] for f in prev.get("filings", [])) == latest_accessions(sub)
    except Exception:
        return False


def run_ticker(ticker, cik, write=True, sub=None):
    sub = sub or get_json(f"https://data.sec.gov/submissions/CIK{cik:010d}.json")
    filings, sub_fye = select_filings(sub)
    warnings = []
    if not filings:
        warnings.append("no 10-K / 20-F / 40-F / 10-Q filings listed in EDGAR submissions")
    parsed = []
    index_cache = {}
    for filing in filings:
        rec = dict(filing)
        try:
            inst_url, data, base, folder, index_names, w = locate_files(cik, filing, index_cache)
            warnings.extend(w)
            rec["instance_url"] = inst_url
            if data is not None:
                rec["instance"] = parse_instance(data)
                rec["labels"], rec["hierarchy"] = fetch_linkbases(base, folder, index_names, warnings, filing)
            else:
                rec["instance"], rec["labels"], rec["hierarchy"] = None, {}, {}
        except Exception as e:
            warnings.append(f"{filing['form']} {filing['accession']}: {type(e).__name__}: {e}")
            rec.setdefault("instance_url", None); rec["instance"], rec["labels"], rec["hierarchy"] = None, {}, {}
        parsed.append(rec)
    out = build_output(ticker, cik, parsed, sub_fye, warnings)
    if write:
        folder = f"{BASE}/{ticker}"
        os.makedirs(folder, exist_ok=True)
        with open(f"{folder}/segments.json", "w", encoding="utf-8") as f:
            json.dump(out, f, indent=1)
    return out


def summarize(out):
    return {"ticker": out["ticker"], "cik": out["cik"], "currency": out["currency"], "complete": out.get("complete"),
            "filings": [f"{f['form']} {f['period']}" + ("" if f.get("instance_url") else " (no instance)") for f in out["filings"]],
            "tables": [f"{t['axis']}/{t['concept']}/{t['periodicity']}: {len(t['rows'])} rows x {len(t['periods'])} cols"
                       + ("" if t.get("ties_to_total") in (True, None) else " (does not tie)") for t in out["tables"]],
            "warnings": out["warnings"]}


def main(argv=None):
    argv = sys.argv if argv is None else argv
    args = [a for i, a in enumerate(argv[1:], 1) if not a.startswith("--") and argv[i - 1] != "--cik"]
    force, write = "--force" in argv, "--no-write" not in argv
    if "--all" in argv:
        folders = sorted(d for d in os.listdir(BASE) if os.path.isfile(f"{BASE}/{d}/score.json") and not d.startswith("_"))
        done, skipped, failed = [], [], []
        for t in folders:
            try:
                nums = {}
                try:
                    nums = json.load(open(f"{BASE}/{t}/dcf_numbers.json", encoding="utf-8"))
                except Exception:
                    pass
                cik = resolve_cik(t, nums, argv=[a for a in argv if a != "--cik"])
                if cik is None:
                    failed.append(f"{t}: NO_CIK"); continue
                sub = get_json(f"https://data.sec.gov/submissions/CIK{cik:010d}.json")
                if not force and os.path.isfile(f"{BASE}/{t}/segments.json"):
                    try:
                        prev = json.load(open(f"{BASE}/{t}/segments.json", encoding="utf-8"))
                    except Exception:
                        prev = None
                    if prev is not None and up_to_date(prev, sub):
                        skipped.append(t); continue
                out = run_ticker(t, cik, write=write, sub=sub)
                done.append(f"{t}: {len(out['tables'])} tables" + (f", {len(out['warnings'])} warnings" if out["warnings"] else ""))
                print(f"{t}: {len(out['tables'])} tables; warnings: {out['warnings'] or 'none'}", flush=True)
            except Exception as e:
                failed.append(f"{t}: {type(e).__name__}: {e}")
                print(f"{t}: FAILED {type(e).__name__}: {e}", file=sys.stderr, flush=True)
        print(json.dumps({"processed": len(done), "skipped_up_to_date": len(skipped), "failed": failed, "done": done, "skipped": skipped}, indent=1))
        return 0
    if not args:
        print(__doc__); return 2
    ticker = args[0].upper()
    nums = {}
    try:
        nums = json.load(open(f"{BASE}/{ticker}/dcf_numbers.json", encoding="utf-8"))
    except Exception:
        pass
    cik = resolve_cik(ticker, nums, argv=argv)
    if cik is None:
        print(f"segments.py: NO_CIK for {ticker}", file=sys.stderr); return 2
    out = run_ticker(ticker, cik, write=write)
    print(json.dumps(summarize(out), indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
