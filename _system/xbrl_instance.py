#!/usr/bin/env python3
"""Undimensioned facts from a filing's own XBRL 2.1 instance (engine 5.7 — Andrew's ruling R2, 2026-10-19).

Why: EDGAR companyfacts can lack a filing that EDGAR already holds. RDY's FY2026 Form 20-F (accession
0001575872-26-000381, period 2026-03-31) is in EDGAR with its XBRL, and companyfacts even lists the accession — but
only for the dei cover-page share count; no ifrs-full fact for FY2026 exists there (companyfacts is not ingesting the
ifrs-full 2025 taxonomy). The filing's own instance document carries every fact. This module reads it.

Two callers, both pure readers of bytes this module never fetches on its own except through locate_instance:
- dcf_engine.load_annual_instance (R2b, the annual-from-instance fallback): the annual facts companyfacts lacks
  (annual_facts_after) are merged into companyfacts in companyfacts' own entry shape (to_companyfacts_entries,
  merge_into_companyfacts), so every engine rule (FX, capex assembly, SBC reconciliation, share hygiene, the gates,
  the acquired-IPR&D detection) applies to them unchanged.
- ttm.py --interim (R2a, the declared 6-K interim bridge): the 6-K's interim facts (interim_facts) verify the
  declared legs.

Reuses segments.py's XML primitives (fetch, locate_files, ns_prefix, _split_tag, _parse_context, _parse_unit);
segments.py itself is unchanged. Only an XBRL 2.1 instance (root xbrli:xbrl) is parsed: an inline XBRL .htm is
refused (NotAnInstance) — EDGAR's extracted <base>_htm.xml is the instance. Stdlib only; no I/O at import.

What is kept (parse_undimensioned): us-gaap / ifrs-full numeric facts with a unitRef, not nil, on contexts with no
explicit or typed member and no <segment> / <scenario> at all — the consolidated totals companyfacts carries — plus
the dei cover-page EntityCommonStockSharesOutstanding on such contexts. Values are float(text), int when integral
(companyfacts stores integers). Identical duplicates (same concept, unit, period and value) collapse; two different
values for one (taxonomy, tag, unit, start, end) are a conflict, never guessed: annual_facts_after drops them and
lists them. Known limit: a multi-class filer's dimensioned per-class dei counts are not read (companyfacts keeps
them); the engine then reads the undimensioned count only.
"""
import datetime
import hashlib
import io
import json
import os
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from segments import (fetch, NotFound, locate_files, ns_prefix, _split_tag, _parse_context,  # noqa: E402,F401
                      _parse_unit, XBRLI, XSI)

INSTANCE_MAX_BYTES = 150_000_000          # RDY's FY2026 instance is 27.8 MB; anything larger is refused unread
ANNUAL_DAYS = (330, 380)                  # end - start, the same window as dcf_engine.period_series
INTERIM_START_TOLERANCE_DAYS = 5          # an interim fact's start may sit a few days off the declared period start
TAXONOMIES = ("us-gaap", "ifrs-full")
DEI_SHARES = "EntityCommonStockSharesOutstanding"
DEI_KEYS = ("DocumentType", "DocumentPeriodEndDate", "DocumentFiscalPeriodFocus", "DocumentFiscalYearFocus",
            "EntityCentralIndexKey", "CurrentFiscalYearEndDate")
# a companyfacts entry the engine reads as annual (fp FY on one of these forms) blocks a merged twin
ANNUAL_ENTRY_FORMS = ("10-K", "10-K/A", "20-F", "20-F/A", "40-F", "40-F/A")
SOURCE_TAG = "xbrl_instance"              # the `src` of every merged companyfacts entry


class NotAnInstance(Exception):
    """The document's root is not xbrli:xbrl (an inline XBRL .htm, an HTML index, any other XML)."""


def unit_name(measure):
    """An instance unit measure in companyfacts' unit spelling: "iso4217:EUR" -> "EUR", "xbrli:shares" -> "shares",
    "iso4217:USD/xbrli:shares" -> "USD/shares", "xbrli:pure" -> "pure" (the prefix as written is dropped; an iso4217
    code is upper-cased)."""
    parts = []
    for m in str(measure or "").split("/"):
        pfx, _, loc = m.strip().rpartition(":")
        parts.append(loc.upper() if pfx.lower() == "iso4217" else loc)
    return "/".join(parts)


def _value(text):
    try:
        v = float((text or "").strip())
    except ValueError:
        return None
    if v != v or v in (float("inf"), float("-inf")):
        return None
    return int(v) if v.is_integer() else v


def _decimals(raw):
    if raw is None:
        return None
    raw = raw.strip()
    if raw.upper() == "INF":
        return "INF"
    try:
        return int(raw)
    except ValueError:
        return None


def _days(start, end):
    return (datetime.date.fromisoformat(end) - datetime.date.fromisoformat(start)).days


def parse_undimensioned(source):
    """Parse an XBRL 2.1 instance (path, bytes or file object) with iterparse; raises NotAnInstance when the root is
    not xbrli:xbrl, and ET.ParseError on malformed XML. Returns
    {"dei": {DocumentType, DocumentPeriodEndDate, DocumentFiscalPeriodFocus, DocumentFiscalYearFocus,
             EntityCentralIndexKey, CurrentFiscalYearEndDate},
     "facts": [{"taxonomy", "tag", "unit", "start", "end", "instant", "value", "decimals", "context"}]}
    (an instant fact has start None and end == instant). Contexts may follow the facts that cite them: facts are
    resolved after the whole document is read."""
    if isinstance(source, (bytes, bytearray)):
        source = io.BytesIO(source)
    nsmap, contexts, units, raw, dei_raw = {}, {}, {}, [], []
    depth = 0
    for ev, el in ET.iterparse(source, events=("start-ns", "start", "end")):
        if ev == "start-ns":
            nsmap[el[0]] = el[1]
            continue
        if ev == "start":
            if depth == 0 and _split_tag(el.tag) != (XBRLI, "xbrl"):
                raise NotAnInstance(f"the document root is {el.tag!r}, not an XBRL 2.1 instance (xbrli:xbrl) — "
                                    "an inline XBRL document is never parsed here")
            depth += 1
            continue
        depth -= 1
        if depth != 1:
            continue
        uri, local = _split_tag(el.tag)
        if uri == XBRLI and local == "context":
            c = _parse_context(el, nsmap)
            c["segmented"] = any(_split_tag(n.tag) in ((XBRLI, "segment"), (XBRLI, "scenario")) for n in el.iter())
            contexts[el.get("id")] = c
        elif uri == XBRLI and local == "unit":
            units[el.get("id")] = _parse_unit(el)
        else:
            pfx = ns_prefix(uri)
            nil = el.get(f"{{{XSI}}}nil") == "true"
            if pfx == "dei":
                if local in DEI_KEYS:
                    dei_raw.append((local, el.get("contextRef"), (el.text or "").strip()))
                elif local == DEI_SHARES and el.get("unitRef") and not nil:
                    raw.append(("dei", local, el.get("contextRef"), el.get("unitRef"), el.get("decimals"), el.text))
            elif pfx in TAXONOMIES and el.get("contextRef") and el.get("unitRef") and not nil:
                raw.append((pfx, local, el.get("contextRef"), el.get("unitRef"), el.get("decimals"), el.text))
        el.clear()

    def plain(cref):
        c = contexts.get(cref)
        return c if (c and not c["dims"] and not c["typed"] and not c["segmented"]) else None

    dei = {k: None for k in DEI_KEYS}
    for local, cref, text in dei_raw:      # the first value on an undimensioned context wins; else the first at all
        if text and dei[local] is None and plain(cref):
            dei[local] = text
    for local, cref, text in dei_raw:
        if text and dei[local] is None:
            dei[local] = text
    facts, seen = [], set()
    for tax, tag, cref, uref, dec, text in raw:
        c = plain(cref)
        v = _value(text)
        if c is None or v is None:
            continue
        unit = unit_name(units.get(uref, ""))
        if c["instant"]:
            start, end, instant = None, c["instant"], c["instant"]
        elif c["start"] and c["end"]:
            start, end, instant = c["start"], c["end"], None
        else:
            continue
        key = (tax, tag, unit, start, end, v)
        if key in seen:        # an identical duplicate (one line tagged twice in the document) collapses
            continue
        seen.add(key)
        facts.append({"taxonomy": tax, "tag": tag, "unit": unit, "start": start, "end": end, "instant": instant,
                      "value": v, "decimals": _decimals(dec), "context": cref})
    return {"dei": dei, "facts": facts}


def _group(facts):
    """{(taxonomy, tag, unit, start, end): [facts]} in document order."""
    out = {}
    for f in facts:
        out.setdefault((f["taxonomy"], f["tag"], f["unit"], f["start"], f["end"]), []).append(f)
    return out


def _split_conflicts(groups):
    """(entries, conflicts): one entry per key with a single value; a key with two or more different values is a
    conflict, dropped and listed."""
    entries, conflicts = [], []
    for (tax, tag, unit, start, end), fs in groups.items():
        vals = []
        for f in fs:
            if f["value"] not in vals:
                vals.append(f["value"])
        if len(vals) > 1:
            conflicts.append({"taxonomy": tax, "tag": tag, "unit": unit, "start": start, "end": end, "values": vals})
            continue
        entries.append({"taxonomy": tax, "tag": tag, "unit": unit, "start": start, "end": end, "val": vals[0],
                        "decimals": fs[0]["decimals"]})
    key = lambda e: (e["taxonomy"], e["tag"], e["unit"], e["start"] or "", e["end"])  # noqa: E731
    return sorted(entries, key=key), sorted(conflicts, key=key)


def annual_facts_after(parsed, after_end):
    """(entries, conflicts) for the periods companyfacts lacks: annual durations (330-380 days, end - start) and
    instants whose end is after `after_end` (an ISO date; None = every period), the dei cover-page share count
    included on the same rule. entries: [{"taxonomy", "tag", "unit", "start" (None for an instant), "end", "val",
    "decimals"}] sorted; conflicts: [{"taxonomy", "tag", "unit", "start", "end", "values"}] — a key carrying two
    different values is dropped, never guessed."""
    after = after_end or ""
    keep = []
    for f in parsed.get("facts") or []:
        if f["end"] <= after:
            continue
        if f["instant"] is None:
            try:
                d = _days(f["start"], f["end"])
            except ValueError:
                continue
            if not (ANNUAL_DAYS[0] <= d <= ANNUAL_DAYS[1]):
                continue
        keep.append(f)
    return _split_conflicts(_group(keep))


def interim_facts(parsed, periods):
    """({(start, end): [entries]}, conflicts) for ttm.py --interim: per requested period (a (start, end) pair), the
    undimensioned DURATION facts with the same end and a start within INTERIM_START_TOLERANCE_DAYS, conflicts
    dropped as in annual_facts_after. Each entry also carries its own `start` (the filed one)."""
    out, conflicts = {}, []
    for per in periods:
        s0, e0 = per
        hits = []
        for f in parsed.get("facts") or []:
            if f["instant"] is not None or f["end"] != e0:
                continue
            try:
                off = abs((datetime.date.fromisoformat(f["start"]) - datetime.date.fromisoformat(s0)).days)
            except ValueError:
                continue
            if off <= INTERIM_START_TOLERANCE_DAYS:
                hits.append(f)
        entries, conf = _split_conflicts(_group(hits))
        out[(s0, e0)] = entries
        conflicts += conf
    return out, conflicts


def locate_instance(cik, accession, primary, form=None, period=None):
    """(instance bytes, instance URL) for a filing, or (None, None) when its folder holds no XBRL instance — through
    segments.locate_files (<primary basename>_htm.xml first, then the filing index's .xml documents). A fetch
    failure other than a 404 raises (the caller decides: the engine records it, ttm.py --interim exits 4).
    [v5.7 L4 note] the pair is (bytes, url) everywhere in this lane (dcf_engine.fetch_instance, the harness patch,
    ttm.fetch_report_instance), so no caller swaps them."""
    filing = {"accession": accession, "primary": primary or "", "form": form or "?", "period": period or "?"}
    url, data, *_ = locate_files(cik, filing, {})
    if not url or data is None:
        return None, None
    return data, url


def to_companyfacts_entries(entries, filing, fiscal_year):
    """[(taxonomy, tag, unit, entry)] in companyfacts' entry shape: {"start" (durations), "end", "val", "accn", "fy",
    "fp": "FY", "form", "filed", "src": "xbrl_instance"} — the form is the ORIGINAL annual form (never "/A"), so the
    engine's annual readers (period_series, the acquired-IPR&D detector) take them like any 10-K / 20-F / 40-F fact."""
    form = str(filing.get("form") or "").replace("/A", "")
    out = []
    for e in entries:
        ent = {"end": e["end"], "val": e["val"], "accn": filing.get("accession"), "fy": fiscal_year, "fp": "FY",
               "form": form, "filed": filing.get("filed"), "src": SOURCE_TAG}
        if e.get("start"):
            ent = {"start": e["start"], **ent}
        out.append((e["taxonomy"], e["tag"], e["unit"], ent))
    return out


def _is_annual_entry(e):
    return e.get("fp") == "FY" and e.get("form") in ANNUAL_ENTRY_FORMS


def merge_into_companyfacts(facts, cf_entries):
    """(merged companyfacts, number of entries added). `facts` is never modified: the taxonomies, tags and unit
    lists touched are copied. An entry is appended only when companyfacts holds no ANNUAL entry (fp FY, a 10-K /
    20-F / 40-F form or its amendment) with the same (taxonomy, tag, unit, start, end) — a companyfacts entry is never
    replaced (RDY's dei cover fact from the same accession stays as companyfacts has it); a 10-Q's comparative
    balance-sheet instant at the same date does not block the annual one (the engine reads only annual entries)."""
    merged = dict(facts or {})
    merged["facts"] = dict((facts or {}).get("facts") or {})
    copied_tax, copied_tag, n = set(), set(), 0
    for tax, tag, unit, ent in cf_entries:
        if tax not in copied_tax:
            merged["facts"][tax] = dict(merged["facts"].get(tax) or {})
            copied_tax.add(tax)
        if (tax, tag) not in copied_tag:
            old = merged["facts"][tax].get(tag)
            if old is None:
                merged["facts"][tax][tag] = {"label": None, "description": None, "units": {}}
            else:
                merged["facts"][tax][tag] = dict(old, units={u: list(arr) for u, arr in (old.get("units") or {}).items()})
            copied_tag.add((tax, tag))
        arr = merged["facts"][tax][tag]["units"].setdefault(unit, [])
        key = (ent.get("start"), ent["end"])
        if any(_is_annual_entry(e) and (e.get("start"), e.get("end")) == key for e in arr):
            continue
        arr.append(ent)
        n += 1
    return merged, n


def _canon(v):
    """Numbers as floats, null dict members dropped (the dcf_engine._iprd_canon convention)."""
    if isinstance(v, bool) or v is None or isinstance(v, str):
        return v
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, dict):
        return {str(k): _canon(x) for k, x in v.items() if x is not None}
    if isinstance(v, (list, tuple)):
        return [_canon(x) for x in v]
    return repr(v)


def facts_sha256(facts, conflicts):
    """sha256 of the canonical (facts, conflicts) lists of annual_instance.json — dcf_numbers.json
    annual_from_instance.facts_sha256 binds the committed file to the run that read it (make_score
    annual_instance_check refuses a file whose facts no longer hash to the run's)."""
    canon = json.dumps({"facts": _canon(list(facts or [])), "conflicts": _canon(list(conflicts or []))},
                       sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()
