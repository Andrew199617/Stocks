#!/usr/bin/env python3
"""Declared share classes (Up-C / multi-class share basis) — engine 5.7, Andrew's ruling R6 (2026-10-19/20: "Fix the
engine so it can use the real total share count for two-class companies like VNOM"). Pure, stdlib only: no I/O at
import, no network; load() is the one file read. Policy-bearing (dcf_engine.py, ttm.py and make_score.py import it).

An Up-C filer (VNOM, OWL, SYM, IBKR ...) consolidates 100% of its operating company's cash flows, but its tagged
diluted share count is the traded class only: the noncontrolling holders' OpCo units — exchangeable into the traded
class and sharing its per-unit distributions — are outside it, so every per-share figure is overstated (VNOM printed a
fake Tier S, 25.05%, on its Class A count). judgment.json `share_classes` declares those units per period, with filing
citations; the engine adds the class-equivalent units to the filed traded-class diluted count of every declared period
before any per-share figure is formed (history, median, CAGRs, the TTM pin — ttm.py applies the same declaration —, the
IPR&D charge per share, the payable / amortized pins, the market cap and the leverage diagnostic).

    "share_classes": {
      "basis": "up_c_exchangeable_units" | "multi_class_common",
      "traded_class": "<the class the filed diluted count counts>",
      "reason": "<why, with a number>",
      ["ack_reason" | "nci_gap_reason" | "cap_gap_reason" | "diluted_gap_reason": "<with a number>"],
      "classes": [{"name", "holder", "exchange_ratio" (filed-count shares per unit), ["ratio_source"],
                   "periods": [{"period_end", "value", "count_basis": period_end | weighted_average,
                                "kind": filing | calc, "accession", "source", "snippet",
                                ["split_basis": pre_split | post_split], ["in_filed_count": true],
                                ["zero_event": not_yet_issued | ended, "event_date"]   (value 0 only),
                                ["calc": {...}]   (kind calc only)}]}]}

Rules (validate; numbers are 08_share_classes.md §2, amended by the rebase map L8.md A-21 and 08b):
 1. basis one of BASES; traded_class / reason non-empty strings, reason carries a digit.
 2. 1-MAX_CLASSES classes; name / holder non-empty; exchange_ratio a finite number > 0 and <= EXCHANGE_RATIO_MAX (the
    filed-count (ordinary) shares one unit equals — never per ADS); ratio_source required when the ratio is not 1.
 3. each period: an ISO period_end unique within its class, an integer-valued value >= 0, count_basis in COUNT_BASES,
    kind in KINDS, an EDGAR accession, non-empty source and snippet; optional split_basis in SPLIT_BASES.
 4. every class lists the same period ends (explicit zeros).
 5. a value of 0 says the class did not exist during the period and when: zero_event in ZERO_EVENTS and an
    event_date written in the entry's own source or snippet (dates_in). The bounds test (ended on or before the
    period start, not_yet_issued after its end) needs the period's start and runs in check_zero_entries, where the
    engine / ttm.py know it: a class that existed for part of a period declares its weighted-average units. Some
    period must carry a value > 0.
 5b. in_filed_count: true (value > 0 only): the filed diluted count of that period already includes the units
    (if-converted) — verified by exchange_test, nothing added.
 6. (engine / make_score) units / filed traded count <= UNITS_MAX_MULT unless ack_reason.
 8. declaration_sha256 over the whole object: any edit is a new declaration (rerun ttm.py and the engine).
 9. the optional reasons (OPTIONAL_REASONS) are non-empty strings carrying a digit when present.
 11. split_basis: only needed when a split is confirmed and the entry's accession is not in the filer's companyfacts.
 A-21 (08b decision 8, the main agent 2026-10-20): kind "calc" is a day-weighted average for a straddle period only
    (count_basis weighted_average; the class was issued or ended inside the period), built from two dated, cited
    counts and the cited event date: calc {method: "day_weighted", event: "ended" | "issued", event_date,
    event_accession, counts: [{value, as_of, accession, snippet}, {...}]}. Its value is re-derived by calc_value on the
    period's own bounds (check_zero_entries) to +-CALC_TOLERANCE units; a calc on a period the event does not
    straddle is refused.
"""
import datetime
import hashlib
import json
import math
import os
import re

BASES = ("up_c_exchangeable_units", "multi_class_common")
COUNT_BASES = ("period_end", "weighted_average")
KINDS = ("filing", "calc")              # A-21: "calc" only for a straddle period's day-weighted average
SPLIT_BASES = ("pre_split", "post_split")
ZERO_EVENTS = ("not_yet_issued", "ended")
CALC_EVENTS = ("ended", "issued")
CALC_METHOD = "day_weighted"
CALC_TOLERANCE = 1.0                    # units: a calc value re-derives to within one unit
MAX_CLASSES = 6
EXCHANGE_RATIO_MAX = 10000              # rule 2
UNITS_MAX_MULT = 20                     # rule 6
EXCHANGE_GAP_FRACTION = 0.5             # exchange_test: (diluted - basic) >= 0.5 x units -> the exchange is in the count
NCI_TOLERANCE_PP = 15                   # the NCI cross-check (engine nci_check)
CAP_GAP_BAND = 0.05                     # the cap cross-check (engine cap_check)
UP_C_NCI_SHARE_MIN = 0.20               # UP_C_SUSPECT threshold (calibrated; 08b decision 1)
UP_C_COUNT_GAP_MIN = 1.05               # count-gap evidence: dei / filed or universe cap / filed cap
UP_C_DILUTION_FRACTION = 0.5            # units_in_diluted: (1 - basic / diluted) >= 0.5 x s
ENV_OFF = "DCF_NO_SHARE_CLASSES"        # make_score's filed-basis replay (engine: only with --measure; ttm.py: only with
                                        # DCF_TTM_NO_WRITE)
PIN_SCALE_ENV = "DCF_SC_PIN_SCALE"      # the factor make_score applied to a declared pin in that replay
OPTIONAL_REASONS = ("ack_reason", "nci_gap_reason", "cap_gap_reason", "diluted_gap_reason")
# the basic weighted counts the exchange test reads (the BasicAndDiluted tag is both counts: gap 0)
BASIC_TAGS = (("us-gaap", "WeightedAverageNumberOfSharesOutstandingBasic"),
              ("us-gaap", "WeightedAverageNumberOfShareOutstandingBasicAndDiluted"),
              ("ifrs-full", "WeightedAverageShares"))
DILUTED_TAGS = (("us-gaap", "WeightedAverageNumberOfDilutedSharesOutstanding"),
                ("us-gaap", "WeightedAverageNumberOfSharesOutstandingDiluted"),
                ("ifrs-full", "AdjustedWeightedAverageShares"))
SHARE_FACT_TAGS = DILUTED_TAGS + BASIC_TAGS + (("us-gaap", "CommonStockSharesOutstanding"),
                                               ("ifrs-full", "NumberOfSharesOutstanding"))
OCF_TAGS = (("us-gaap", "NetCashProvidedByUsedInOperatingActivities"),
            ("us-gaap", "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations"),
            ("ifrs-full", "CashFlowsFromUsedInOperatingActivities"))
ANNUAL_FORMS = ("10-K", "10-K/A", "20-F", "20-F/A", "40-F", "40-F/A")
ACCESSION_RE = re.compile(r"^\d{10}-\d{2}-\d{6}$")
_ISO_RE = re.compile(r"(?<!\d)(\d{4})-(\d{2})-(\d{2})(?!\d)")
_MONTHS = {"january": 1, "jan": 1, "february": 2, "feb": 2, "march": 3, "mar": 3, "april": 4, "apr": 4, "may": 5,
           "june": 6, "jun": 6, "july": 7, "jul": 7, "august": 8, "aug": 8, "september": 9, "sept": 9, "sep": 9,
           "october": 10, "oct": 10, "november": 11, "nov": 11, "december": 12, "dec": 12}
_MDY_RE = re.compile(r"\b([A-Za-z]{3,9})\.?\s+(\d{1,2}),?\s+(\d{4})\b")
_DMY_RE = re.compile(r"\b(\d{1,2})\s+([A-Za-z]{3,9})\.?,?\s+(\d{4})\b")


# ---------------------------------------------------------------------------
# small guards
# ---------------------------------------------------------------------------
def _num(v):
    """A finite int / float (never a bool) as a float, else None."""
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        return None
    try:
        f = float(v)
    except (TypeError, ValueError, OverflowError):
        return None
    return f if math.isfinite(f) else None


def _text(v):
    return v.strip() if isinstance(v, str) and v.strip() else None


def _date(s):
    if not isinstance(s, str):
        return None
    try:
        return datetime.date.fromisoformat(s)
    except ValueError:
        return None


def _has_digit(s):
    return isinstance(s, str) and bool(re.search(r"\d", s))


def dates_in(text):
    """The calendar dates written in `text`, as ISO strings: 2024-01-02, January 2, 2024, Jan. 2, 2024, Sept. 30,
    2025, 2 January 2024. Rule 5: a zero entry's (and a calc entry's) event_date must be among its own source /
    snippet dates, so the date is read from the text the worker cites, not typed twice."""
    out = set()
    if not isinstance(text, str):
        return out
    for m in _ISO_RE.finditer(text):
        try:
            out.add(datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3))).isoformat())
        except ValueError:
            pass
    for m in _MDY_RE.finditer(text):
        mo = _MONTHS.get(m.group(1).lower())
        if mo:
            try:
                out.add(datetime.date(int(m.group(3)), mo, int(m.group(2))).isoformat())
            except ValueError:
                pass
    for m in _DMY_RE.finditer(text):
        mo = _MONTHS.get(m.group(2).lower())
        if mo:
            try:
                out.add(datetime.date(int(m.group(3)), mo, int(m.group(1))).isoformat())
            except ValueError:
                pass
    return out


# ---------------------------------------------------------------------------
# validation and the declaration's derived figures
# ---------------------------------------------------------------------------
def _int_valued(v):
    f = _num(v)
    return f is not None and f >= 0 and float(f).is_integer()


def _validate_calc(c, where, errs):
    if not isinstance(c, dict):
        errs.append(f"{where}.calc must be an object {{method, event, event_date, event_accession, counts}} (kind calc)")
        return
    if c.get("method") != CALC_METHOD:
        errs.append(f"{where}.calc.method must be {CALC_METHOD!r}")
    if c.get("event") not in CALC_EVENTS:
        errs.append(f"{where}.calc.event must be one of {', '.join(CALC_EVENTS)} (the class ended or was issued inside "
                    "the period)")
    if _date(c.get("event_date")) is None:
        errs.append(f"{where}.calc.event_date must be an ISO date YYYY-MM-DD")
    if not (isinstance(c.get("event_accession"), str) and ACCESSION_RE.match(c["event_accession"])):
        errs.append(f"{where}.calc.event_accession must be an EDGAR accession NNNNNNNNNN-YY-NNNNNN")
    cs = c.get("counts")
    if not (isinstance(cs, list) and len(cs) == 2 and all(isinstance(x, dict) for x in cs)):
        errs.append(f"{where}.calc.counts must list exactly two dated, cited counts {{value, as_of, accession, snippet}}")
        return
    for i, x in enumerate(cs):
        w = f"{where}.calc.counts[{i}]"
        if not _int_valued(x.get("value")):
            errs.append(f"{w}.value must be an integer-valued number >= 0")
        if _date(x.get("as_of")) is None:
            errs.append(f"{w}.as_of must be an ISO date YYYY-MM-DD")
        if not (isinstance(x.get("accession"), str) and ACCESSION_RE.match(x["accession"])):
            errs.append(f"{w}.accession must be an EDGAR accession NNNNNNNNNN-YY-NNNNNN")
        if not _text(x.get("snippet")):
            errs.append(f"{w}.snippet must be a non-empty string (the filing's words showing the count)")
    d0, d1 = _date(cs[0].get("as_of")), _date(cs[1].get("as_of"))
    if d0 and d1 and d0 > d1:
        errs.append(f"{where}.calc.counts must be in date order (as_of {cs[0]['as_of']} after {cs[1]['as_of']})")


def validate(decl):
    """(normalized declaration | None, [errors]) — rules 1-5b, 7, 9, 11 and A-21's shape (see the module docstring).
    The normalized copy has float exchange ratios and values; the raw object is what declaration_sha256 hashes."""
    errs = []
    if not isinstance(decl, dict):
        return None, [f"share_classes must be an object {{basis, traded_class, reason, classes}} (got {type(decl).__name__})"]
    if decl.get("basis") not in BASES:
        errs.append(f"basis must be one of {', '.join(BASES)} (got {decl.get('basis')!r})")
    if not _text(decl.get("traded_class")):
        errs.append("traded_class must be a non-empty string (the class the filed diluted count counts)")
    if not _text(decl.get("reason")):
        errs.append("reason must be a non-empty string")
    elif not _has_digit(decl["reason"]):
        errs.append("reason must carry a number (the figure the declaration rests on)")
    for k in OPTIONAL_REASONS:
        if k in decl and decl[k] is not None:
            if not _text(decl[k]):
                errs.append(f"{k} must be a non-empty string when present")
            elif not _has_digit(decl[k]):
                errs.append(f"{k} must carry a number")
    classes = decl.get("classes")
    if not (isinstance(classes, list) and 1 <= len(classes) <= MAX_CLASSES and all(isinstance(c, dict) for c in classes)):
        errs.append(f"classes must list 1-{MAX_CLASSES} class objects")
        return None, errs
    norm_classes, period_sets, any_positive = [], [], False
    for ci, c in enumerate(classes):
        where = f"classes[{ci}]"
        if not _text(c.get("name")):
            errs.append(f"{where}.name must be a non-empty string")
        if not _text(c.get("holder")):
            errs.append(f"{where}.holder must be a non-empty string")
        r = _num(c.get("exchange_ratio"))
        if r is None or r <= 0 or r > EXCHANGE_RATIO_MAX:
            errs.append(f"{where}.exchange_ratio must be a finite number > 0 and <= {EXCHANGE_RATIO_MAX} (filed-count "
                        "shares per unit of the class)")
            r = None
        elif r != 1 and not _text(c.get("ratio_source")):
            errs.append(f"{where}.ratio_source is required when exchange_ratio is not 1 (the filing that states it)")
        periods = c.get("periods")
        if not (isinstance(periods, list) and periods and all(isinstance(p, dict) for p in periods)):
            errs.append(f"{where}.periods must list at least one period object")
            period_sets.append(None)
            continue
        seen, nps = set(), []
        for pi, p in enumerate(periods):
            w = f"{where}.periods[{pi}]"
            pe = p.get("period_end")
            if _date(pe) is None:
                errs.append(f"{w}.period_end must be an ISO date YYYY-MM-DD")
            elif pe in seen:
                errs.append(f"{w}.period_end {pe} is listed twice in {where}")
            else:
                seen.add(pe)
            if not _int_valued(p.get("value")):
                errs.append(f"{w}.value must be an integer-valued number >= 0 (a filed count)")
            val = _num(p.get("value"))
            if p.get("count_basis") not in COUNT_BASES:
                errs.append(f"{w}.count_basis must be one of {', '.join(COUNT_BASES)}")
            if p.get("kind") not in KINDS:
                errs.append(f"{w}.kind must be \"filing\" (a filed count; an estimate is refused) or \"calc\" (a "
                            "straddle year's day-weighted average, rule A-21)")
            if not (isinstance(p.get("accession"), str) and ACCESSION_RE.match(p["accession"])):
                errs.append(f"{w}.accession must be an EDGAR accession NNNNNNNNNN-YY-NNNNNN")
            if not _text(p.get("source")):
                errs.append(f"{w}.source must be a non-empty string")
            if not _text(p.get("snippet")):
                errs.append(f"{w}.snippet must be a non-empty string")
            if p.get("split_basis") is not None and p.get("split_basis") not in SPLIT_BASES:
                errs.append(f"{w}.split_basis must be one of {', '.join(SPLIT_BASES)} when present")
            ifc = p.get("in_filed_count")
            if ifc is not None and ifc is not True and ifc is not False:
                errs.append(f"{w}.in_filed_count must be true when present")
            texts = " ".join(str(p.get(k) or "") for k in ("source", "snippet"))
            if val is not None and val == 0:
                if ifc is True:
                    errs.append(f"{w}.in_filed_count needs a value > 0 (the class's units the filed count includes)")
                if p.get("zero_event") not in ZERO_EVENTS:
                    errs.append(f"{w} declares 0: zero_event must say why the class did not exist during the period "
                                f"({' / '.join(ZERO_EVENTS)}) with its event_date")
                ed = p.get("event_date")
                if _date(ed) is None:
                    errs.append(f"{w} declares 0: event_date must be an ISO date YYYY-MM-DD")
                elif ed not in dates_in(texts):
                    errs.append(f"{w} declares 0 with event_date {ed}, but that date is not written in its own source "
                                "or snippet (rule 5: the date is read from the cited text)")
                if p.get("kind") == "calc":
                    errs.append(f"{w}: a calc entry is a straddle year's weighted average (> 0); a class absent all "
                                "period is declared 0 with kind filing")
            elif val is not None:
                if val > 0:
                    any_positive = True
                if p.get("zero_event") is not None or p.get("event_date") is not None:
                    errs.append(f"{w}: zero_event / event_date belong to a 0 entry only (a class that existed for part "
                                "of the period declares its weighted-average units)")
            if p.get("kind") == "calc":
                if p.get("count_basis") != "weighted_average":
                    errs.append(f"{w}: kind calc is a weighted average — count_basis must be weighted_average")
                _validate_calc(p.get("calc"), w, errs)
                ced = (p.get("calc") or {}).get("event_date") if isinstance(p.get("calc"), dict) else None
                if _date(ced) is not None and ced not in dates_in(texts):
                    errs.append(f"{w}.calc.event_date {ced} is not written in the entry's own source or snippet")
            elif p.get("calc") is not None:
                errs.append(f"{w}.calc belongs to a kind calc entry only")
            nps.append({"period_end": pe, "value": val, "count_basis": p.get("count_basis"), "kind": p.get("kind"),
                        "accession": p.get("accession"), "source": p.get("source"), "snippet": p.get("snippet"),
                        "split_basis": p.get("split_basis"), "in_filed_count": ifc is True,
                        "zero_event": p.get("zero_event"), "event_date": p.get("event_date"),
                        "calc": p.get("calc") if p.get("kind") == "calc" else None})
        period_sets.append(seen)
        norm_classes.append({"name": c.get("name"), "holder": c.get("holder"), "exchange_ratio": r,
                             "ratio_source": c.get("ratio_source"), "periods": nps})
    sets = [s for s in period_sets if s is not None]
    if sets and any(s != sets[0] for s in sets):
        allp = sorted(set().union(*sets))
        for ci, s in enumerate(period_sets):
            if s is not None and s != set(allp):
                errs.append(f"classes[{ci}] does not list {', '.join(sorted(set(allp) - s))} — every class lists the same "
                            "period ends (an explicit 0, dated, for a class that did not exist)")
    if not any_positive and not errs:
        errs.append("every declared count is 0 — some period must carry units > 0 (otherwise there is nothing to declare)")
    if errs:
        return None, errs
    norm = {"basis": decl["basis"], "traded_class": decl["traded_class"], "reason": decl["reason"],
            "classes": norm_classes}
    for k in OPTIONAL_REASONS:
        if _text(decl.get(k)):
            norm[k] = decl[k]
    return norm, []


def declaration_sha256(decl):
    """Rule 8: sha256 of the whole judgment.json share_classes object (sources and snippets included)."""
    return hashlib.sha256(json.dumps(decl, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
                          .encode("utf-8")).hexdigest()


def _entries(norm, period_end):
    for c in (norm or {}).get("classes") or []:
        for p in c["periods"]:
            if p["period_end"] == period_end:
                yield c, p


def units_by_period(norm):
    """{period_end: units_equivalent >= 0}: sum of value x exchange_ratio over the period's entries WITHOUT
    in_filed_count (rule 5), in filed-count (ordinary-share) units."""
    out = {}
    for c in (norm or {}).get("classes") or []:
        for p in c["periods"]:
            out.setdefault(p["period_end"], 0.0)
            if not p["in_filed_count"]:
                out[p["period_end"]] += p["value"] * c["exchange_ratio"]
    return out


def included_units(norm, period_end):
    """Rule 5b: sum of value x exchange_ratio over the period's in_filed_count entries (units the filed diluted count
    already carries)."""
    return sum(p["value"] * c["exchange_ratio"] for c, p in _entries(norm, period_end) if p["in_filed_count"])


def period_detail(norm, period_end):
    """Per class for one period: name, value, exchange_ratio, units, count_basis, kind, accession (+ split_basis,
    in_filed_count, zero_event / event_date when set)."""
    out = []
    for c, p in _entries(norm, period_end):
        d = {"name": c["name"], "value": p["value"], "exchange_ratio": c["exchange_ratio"],
             "units": p["value"] * c["exchange_ratio"], "count_basis": p["count_basis"], "kind": p["kind"],
             "accession": p["accession"]}
        for k in ("split_basis", "zero_event", "event_date"):
            if p.get(k) is not None:
                d[k] = p[k]
        if p["in_filed_count"]:
            d["in_filed_count"] = True
        out.append(d)
    return out


def count_bases(norm, period_end):
    """The distinct count_basis values of a period's entries with units (value > 0)."""
    return sorted({p["count_basis"] for _, p in _entries(norm, period_end) if p["value"] > 0})


def zero_source(norm, period_end):
    """The dated sources of a zero period's 0 entries (rule 5)."""
    return "; ".join(f"{c['name']}: {p['zero_event']} {p['event_date']} — {p['source']}"
                     for c, p in _entries(norm, period_end) if p["value"] == 0)


def calc_value(calc, start, end):
    """A-21: the day-weighted mean of a class over the period start..end (inclusive dates): the class exists on
    [start, event_date - 1 day] when it ENDED at event_date, on [event_date, end] when it was ISSUED then; the first
    count holds from the existence start until the day before the second count's as_of date, the second from its
    as_of to the existence end; sum of count x days / days in the period. None on a malformed calc."""
    try:
        s, e, ev = _date(start), _date(end), _date(calc["event_date"])
        cs = sorted(calc["counts"], key=lambda x: x["as_of"])
        if None in (s, e, ev):
            return None
        if calc["event"] == "ended":
            a, b = s, ev - datetime.timedelta(days=1)
        else:
            a, b = ev, e
        total = (e - s).days + 1
        if total <= 0 or b < a:
            return 0.0
        acc = 0.0
        for i, x in enumerate(cs):
            seg_a = a if i == 0 else max(a, _date(x["as_of"]))
            seg_b = (_date(cs[i + 1]["as_of"]) - datetime.timedelta(days=1)) if i + 1 < len(cs) else b
            seg_b = min(seg_b, b)
            days = (seg_b - seg_a).days + 1
            if days > 0:
                acc += float(x["value"]) * days
        return acc / total
    except (KeyError, TypeError, ValueError, AttributeError):
        return None


def check_zero_entries(norm, period_end, start):
    """Rule 5 (and A-21) on one period's own bounds start..period_end: each 0 entry's event must lie outside the
    period — `ended` on or before its start, `not_yet_issued` after its end — else the class existed for part of the
    period and its 0 is refused; each calc entry's event must straddle the period (start < event_date <= end), its
    counts must be dated inside the class's existence, and its value must re-derive (calc_value) to +-CALC_TOLERANCE.
    Returns [errors]."""
    errs = []
    s, e = _date(start), _date(period_end)
    for c, p in _entries(norm, period_end):
        if p["value"] == 0:
            ev = _date(p.get("event_date"))
            if ev is None or s is None or e is None:
                continue
            inside = (p["zero_event"] == "ended" and ev > s) or (p["zero_event"] == "not_yet_issued" and ev <= e)
            if inside:
                errs.append(f"{c['name']} is declared 0 for the period ending {period_end}, but the class existed for "
                            f"part of this period ({p['zero_event']} {p['event_date']} inside {start}..{period_end}): "
                            "declare its weighted-average units for the period (count_basis weighted_average, from the "
                            "EPS note's antidilutive or exchangeable count, or a kind calc day-weighted average)")
        if p["kind"] == "calc":
            cal = p.get("calc") or {}
            ev = _date(cal.get("event_date"))
            if ev is None or s is None or e is None:
                continue
            if not (s < ev <= e):
                errs.append(f"{c['name']} {period_end}: a kind calc count is for a period its class starts or ends in, "
                            f"but {cal.get('event')} {cal.get('event_date')} does not fall inside {start}..{period_end} — "
                            "declare the filed count (kind filing)")
                continue
            a = s if cal.get("event") == "ended" else ev
            b = (ev - datetime.timedelta(days=1)) if cal.get("event") == "ended" else e
            for x in cal.get("counts") or []:
                d = _date(x.get("as_of"))
                if d is None or not (a - datetime.timedelta(days=1) <= d <= b + datetime.timedelta(days=1)):
                    errs.append(f"{c['name']} {period_end}: calc count as_of {x.get('as_of')} is outside the class's "
                                f"existence in the period ({a.isoformat()}..{b.isoformat()})")
            v = calc_value(cal, start, period_end)
            if v is None or abs(v - p["value"]) > CALC_TOLERANCE:
                errs.append(f"{c['name']} {period_end}: the declared value {p['value']:,.0f} does not reproduce the "
                            f"day-weighted average of its counts ({'n/a' if v is None else f'{v:,.2f}'}) over "
                            f"{start}..{period_end}")
    return errs


def calc_records(norm, period_end, start):
    """The re-derived arithmetic of the period's calc entries (recorded by the engine, re-checked by make_score)."""
    out = []
    for c, p in _entries(norm, period_end):
        if p["kind"] == "calc":
            out.append({"name": c["name"], "value": p["value"], "period_start": start, "period_end": period_end,
                        "rederived": calc_value(p.get("calc") or {}, start, period_end)})
    return out


def exchange_test(filed, basic, units, included, norm):
    """(refusal | None, record): one rule for every leg (engine FY row, ttm.py YTD, the interim leg); never called on
    an OVERRIDE leg. No basic count -> no test: refused unless diluted_gap_reason (in_filed_count units always need
    one); in_filed_count units must be in the count ((filed - basic) >= 0.5 x included, rule 5b); the remaining gap
    (filed - basic - included) >= 0.5 x units means the count already carries the exchange: refused unless
    diluted_gap_reason."""
    reason = (norm or {}).get("diluted_gap_reason")
    filed_f, b = _num(filed), _num(basic)
    rec = {"basic": b, "gap": None, "threshold": EXCHANGE_GAP_FRACTION * units, "included_units": included}
    if b is None:
        if included:
            return ("the filed diluted count's period has no basic weighted count, so the units marked in_filed_count "
                    "cannot be verified — remove in_filed_count (the units are then added) or cite a filing with the "
                    "basic count"), dict(rec, test="not_possible")
        if reason:
            return None, dict(rec, test="not_possible_reason_given")
        return ("no basic weighted count is filed for this period, so the engine cannot tell whether the diluted count "
                "already includes the exchange — state why it excludes the units in share_classes.diluted_gap_reason "
                "(with the figure)"), dict(rec, test="not_possible")
    gap = (filed_f or 0.0) - b
    rec["gap"] = gap
    if included and gap < EXCHANGE_GAP_FRACTION * included:
        return (f"the filed diluted count does not carry the exchange (diluted - basic {gap:,.0f} < half the units marked "
                f"in_filed_count {included:,.0f}) — remove in_filed_count and the units are added"), \
            dict(rec, test="in_filed_count_not_carried")
    rest = gap - included
    if units and rest >= EXCHANGE_GAP_FRACTION * units:
        if reason:
            return None, dict(rec, test="gap_reason_given")
        return (f"the filed diluted count already includes the exchange (diluted - basic {rest:,.0f} >= half the "
                f"declared units {units:,.0f}): mark the units in_filed_count when the EPS note says the count is "
                "if-converted, or explain the gap in share_classes.diluted_gap_reason (with the figure)"), \
            dict(rec, test="exchange_in_count")
    return None, dict(rec, test="passed")


def ttm_on_declaration(ttm_doc, decl):
    """(True, None) when ttm.json (object ttm_doc) is on this share_classes declaration (decl: judgment.json's raw
    share_classes object, or None): no share_classes block and nothing declared, or a block whose declaration_sha256
    equals declaration_sha256(decl); else (False, why). The §5.3 table as one function — the engine's
    check_ttm_share_basis (the --ttm read), make_score R-6 and R7's base_alternatives (every ttm.json alternative)."""
    blk = ttm_doc.get("share_classes") if isinstance(ttm_doc, dict) else None
    if decl is None:
        if isinstance(blk, dict):
            return False, "ttm.json is on total units but judgment.json declares no share_classes — re-run ttm.py"
        return True, None
    if not isinstance(ttm_doc, dict):
        return False, "no ttm.json to check against the share_classes declaration — run ttm.py"
    if not isinstance(blk, dict):
        return False, "ttm.json was built before the share_classes declaration — re-run ttm.py"
    if blk.get("declaration_sha256") != declaration_sha256(decl):
        return False, "ttm.json was built on another share_classes declaration — re-run ttm.py"
    return True, None


# ---------------------------------------------------------------------------
# reading companyfacts (the document already in memory)
# ---------------------------------------------------------------------------
def _facts_of(facts, tax, tag):
    body = ((facts or {}).get("facts") or {}).get(tax) if isinstance(facts, dict) else None
    body = body.get(tag) if isinstance(body, dict) else None
    units = body.get("units") if isinstance(body, dict) else None
    return units if isinstance(units, dict) else {}


def share_period_ends(facts):
    """Every `end` of the filer's companyfacts share facts (diluted / basic weighted tags, CommonStockSharesOutstanding
    and their ifrs twins) — the period ends a declared period may be."""
    out = set()
    for tax, tag in SHARE_FACT_TAGS:
        for es in _facts_of(facts, tax, tag).values():
            for e in es if isinstance(es, list) else []:
                if isinstance(e, dict) and _date(e.get("end")):
                    out.add(e["end"])
    return out


def filed_dates_by_accession(facts):
    """{accession: earliest `filed`} over every fact of the companyfacts document."""
    out = {}
    for tags in (((facts or {}).get("facts") or {}).values() if isinstance(facts, dict) else []):
        if not isinstance(tags, dict):
            continue
        for body in tags.values():
            units = body.get("units") if isinstance(body, dict) else None
            for es in (units.values() if isinstance(units, dict) else []):
                for e in es if isinstance(es, list) else []:
                    if isinstance(e, dict) and isinstance(e.get("accn"), str) and isinstance(e.get("filed"), str):
                        if e["accn"] not in out or e["filed"] < out[e["accn"]]:
                            out[e["accn"]] = e["filed"]
    return out


def _days(s, e):
    a, b = _date(s), _date(e)
    return (b - a).days if (a and b) else None


def period_bounds(facts, period_end):
    """(start, end) of a fiscal-year period: the start of the filer's 330-380-day duration share / OCF fact ending on
    period_end (the latest filed), else period_end - 1 year + 1 day."""
    best = None
    for tax, tag in DILUTED_TAGS + BASIC_TAGS + OCF_TAGS:
        for es in _facts_of(facts, tax, tag).values():
            for e in es if isinstance(es, list) else []:
                if not isinstance(e, dict) or e.get("end") != period_end or not e.get("start"):
                    continue
                d = _days(e["start"], e["end"])
                if d is None or not (329 <= d <= 380):
                    continue
                if best is None or str(e.get("filed") or "") > str(best.get("filed") or ""):
                    best = e
    if best is not None:
        return best["start"], period_end
    e = _date(period_end)
    if e is None:
        return None, period_end
    try:
        s = e.replace(year=e.year - 1) + datetime.timedelta(days=1)
    except ValueError:
        s = e.replace(year=e.year - 1, day=28) + datetime.timedelta(days=1)
    return s.isoformat(), period_end


def _annual_value(facts, tags, period_end, units=("shares",), prefer_filed=None):
    """The annual (330-380-day) value ending at period_end, filed on an annual form (ANNUAL_FORMS, as the engine's
    period_series reads), for the first tag (in order) that files one, in one of `units`: the fact filed on
    prefer_filed when there is one, else the latest filed. None when none."""
    for tax, tag in tags:
        u_all = _facts_of(facts, tax, tag)
        for unit in units:
            cands = []
            for e in u_all.get(unit) or []:
                if not isinstance(e, dict) or e.get("end") != period_end or not e.get("start"):
                    continue
                if e.get("form") is not None and e.get("form") not in ANNUAL_FORMS:
                    continue
                d = _days(e["start"], e["end"])
                v = _num(e.get("val"))
                if d is None or not (329 <= d <= 380) or v is None:
                    continue
                cands.append(e)
            if cands:
                same = [e for e in cands if prefer_filed and e.get("filed") == prefer_filed]
                pick = max(same or cands, key=lambda e: str(e.get("filed") or ""))
                return float(pick["val"])
    return None


def basic_by_period(facts, periods, prefer_filed=None):
    """{period_end: the FY basic weighted count} (BASIC_TAGS — the BasicAndDiluted tag counts as basic): the filing
    that supplied the diluted count when it carries one (prefer_filed: {period_end: filed date}), else the latest
    filed. Periods with none are absent."""
    out = {}
    for p in periods or []:
        v = _annual_value(facts, BASIC_TAGS, p, prefer_filed=(prefer_filed or {}).get(p))
        if v is not None:
            out[p] = v
    return out


def units_split_scale(norm, period_end, accn_filed, ev_date, ratio_used, included=False):
    """(factor, basis): the split basis of the period's units (rule 11) — each class entry on the basis of the filing
    that printed it. Without a confirmed split: (1.0, "no_split"). Else per entry with value > 0 (its applied
    entries, or its in_filed_count ones with included=True): the accession's companyfacts `filed` date before the
    event -> x ratio_used ("pre_split_rescaled"), on or after it -> 1.0 ("post_split"); an accession absent from
    companyfacts takes its declared split_basis, and without one raises ValueError (refused). The factor is
    units-weighted across classes; basis "mixed" when they differ."""
    if not ev_date:
        return 1.0, "no_split"
    num = den = 0.0
    bases = set()
    for c, p in _entries(norm, period_end):
        if p["in_filed_count"] != bool(included) or not p["value"]:
            continue
        u = p["value"] * c["exchange_ratio"]
        f = (accn_filed or {}).get(p["accession"])
        if f is not None:
            pre = f < ev_date
        elif p.get("split_basis") in SPLIT_BASES:
            pre = p["split_basis"] == "pre_split"
        else:
            raise ValueError(f"{c['name']} {period_end}: accession {p['accession']} is not in the filer's companyfacts and "
                             f"a split is confirmed ({ev_date}, ratio {ratio_used:g}) — state the units' split_basis "
                             "(pre_split / post_split) for that period")
        fac = float(ratio_used) if pre else 1.0
        bases.add("pre_split_rescaled" if pre else "post_split")
        num += u * fac
        den += u
    if not den:
        return 1.0, "no_units"
    return num / den, (bases.pop() if len(bases) == 1 else "mixed")


def load(base, ticker):
    """judgment.json's share_classes value (None when absent or null, or when judgment.json is unreadable); never
    raises. Any other value is returned as found — validate() refuses a non-object."""
    try:
        with open(os.path.join(base, ticker, "judgment.json"), encoding="utf-8") as f:
            j = json.load(f)
    except Exception:
        return None
    return j.get("share_classes") if isinstance(j, dict) else None


# ---------------------------------------------------------------------------
# UP_C_SUSPECT — the detector (08 §6; universe.csv's own price, never the run price)
# ---------------------------------------------------------------------------
_NCI_NI_TAGS = (("us-gaap", "NetIncomeLossAttributableToNoncontrollingInterest"),
                ("ifrs-full", "ProfitLossAttributableToNoncontrollingInterests"))
_CONS_NI_TAGS = (("us-gaap", "ProfitLoss"), ("ifrs-full", "ProfitLoss"))
_PARENT_NI_TAGS = (("us-gaap", "NetIncomeLoss"), ("ifrs-full", "ProfitLossAttributableToOwnersOfParent"))
_NCI_EQ_TAGS = (("us-gaap", "MinorityInterest"), ("us-gaap", "NonredeemableNoncontrollingInterest"),
                ("ifrs-full", "NoncontrollingInterests"))
_TOTAL_EQ_TAGS = (("us-gaap", "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"),
                  ("ifrs-full", "Equity"))
_PARENT_EQ_TAGS = (("us-gaap", "StockholdersEquity"), ("ifrs-full", "EquityAttributableToOwnersOfParent"))


def _instant_value(facts, tags, date, units=("USD",)):
    for tax, tag in tags:
        u_all = _facts_of(facts, tax, tag)
        for unit in units:
            cands = [e for e in u_all.get(unit) or [] if isinstance(e, dict) and e.get("end") == date
                     and not e.get("start") and _num(e.get("val")) is not None
                     and (e.get("form") is None or e.get("form") in ANNUAL_FORMS)]
            if cands:
                return float(max(cands, key=lambda e: str(e.get("filed") or ""))["val"])
    return None


def up_c_signals(facts, window, latest_fy_end, shares_latest, dei_count, universe_price, universe_cap, ads_ratio,
                 annual_form):
    """The UP_C_SUSPECT detector's record (dcf_numbers.json up_c_check; the flag fires when `suspect` and nothing
    suppresses it). s = max(NCI share of consolidated net income over the base window (sum of |NCI| / sum of
    |consolidated|, >= 2 FY), NCI share of equity at the latest FY end (total and parent equity both positive));
    units_in_diluted = (1 - basic / diluted) >= UP_C_DILUTION_FRACTION x s at the latest FY; count-gap evidence = no
    undimensioned cover-page count (cover by class), or dei / filed >= UP_C_COUNT_GAP_MIN, or universe.csv's cap /
    (universe.csv's price x filed / ads) >= UP_C_COUNT_GAP_MIN. suspect = a domestic form, s >= UP_C_NCI_SHARE_MIN,
    the units not in the diluted count, and count-gap evidence. USD (money) and shares facts only; every value
    type-guarded (the caller still wraps the call)."""
    years = []
    for p in window or []:
        nci = _annual_value(facts, _NCI_NI_TAGS, p, units=("USD",))
        cons = _annual_value(facts, _CONS_NI_TAGS, p, units=("USD",))
        if nci is None and cons is not None:
            par = _annual_value(facts, _PARENT_NI_TAGS, p, units=("USD",))
            nci = (cons - par) if par is not None else None
        if cons is None and nci is not None:
            par = _annual_value(facts, _PARENT_NI_TAGS, p, units=("USD",))
            cons = (par + nci) if par is not None else None
        if nci is not None and cons is not None:
            years.append([p, nci, cons])
    ni_share = None
    if len(years) >= 2:
        den = sum(abs(c) for _, _, c in years)
        if den > 0:
            ni_share = max(0.0, min(1.0, sum(abs(x) for _, x, _ in years) / den))
    eq_share = None
    tot = _instant_value(facts, _TOTAL_EQ_TAGS, latest_fy_end)
    par = _instant_value(facts, _PARENT_EQ_TAGS, latest_fy_end)
    if tot is not None and par is not None and tot > 0 and par > 0:
        nci_eq = _instant_value(facts, _NCI_EQ_TAGS, latest_fy_end)
        if nci_eq is None:
            nci_eq = tot - par
        eq_share = max(0.0, min(1.0, nci_eq / tot))
    shares = [v for v in (ni_share, eq_share) if v is not None]
    s = max(shares) if shares else None
    dil = _annual_value(facts, DILUTED_TAGS, latest_fy_end)
    bas = _annual_value(facts, BASIC_TAGS[:1] + BASIC_TAGS[2:], latest_fy_end)
    d2b = (dil / bas) if (dil and bas and bas > 0) else None
    units_in = bool(dil and bas and dil > 0 and s is not None and (1 - bas / dil) >= UP_C_DILUTION_FRACTION * s)
    filed = _num(shares_latest)
    dei = _num(dei_count)
    cover_by_class = dei is None
    dei_to = (dei / filed) if (dei and filed) else None
    up, uc = _num(universe_price), _num(universe_cap)
    r = _num(ads_ratio.get("ratio") if isinstance(ads_ratio, dict) else ads_ratio)
    r = r if (r is not None and r > 0) else 1.0
    cap_ratio = (uc / (up * filed / r)) if (up and uc and filed and up > 0 and filed > 0) else None
    gap = bool(cover_by_class or (dei_to is not None and dei_to >= UP_C_COUNT_GAP_MIN)
               or (cap_ratio is not None and cap_ratio >= UP_C_COUNT_GAP_MIN))
    domestic = annual_form not in ("20-F", "40-F")
    suspect = bool(domestic and s is not None and s >= UP_C_NCI_SHARE_MIN and not units_in and gap)
    return {"nci_share_of_net_income_3fy": ni_share, "nci_years": years, "nci_share_of_equity": eq_share, "s": s,
            "diluted_to_basic": d2b, "units_in_diluted": units_in, "cover_by_class": cover_by_class,
            "dei_to_diluted": dei_to, "universe_price": up, "universe_cap_to_filed_cap": cap_ratio,
            "count_gap": gap, "domestic": domestic, "threshold": UP_C_NCI_SHARE_MIN, "suspect": suspect,
            "suppressed_by": None}


def nci_check(up_c, declared_share):
    """The up_c_exchangeable_units cross-check: the declared share of total units at the latest FY against the
    detector's NCI shares (equity, net income); agrees = the nearer within NCI_TOLERANCE_PP, None when neither
    exists."""
    eq = (up_c or {}).get("nci_share_of_equity") if isinstance(up_c, dict) else None
    ni = (up_c or {}).get("nci_share_of_net_income_3fy") if isinstance(up_c, dict) else None
    gaps = [abs(declared_share - x) for x in (eq, ni) if isinstance(x, (int, float)) and declared_share is not None]
    g = min(gaps) if gaps else None
    return {"nci_share_of_equity": eq, "nci_share_of_net_income_3fy": ni, "declared_share_of_total": declared_share,
            "gap_pp": round(g * 100, 2) if g is not None else None, "tolerance_pp": NCI_TOLERANCE_PP,
            "agrees": (g * 100 <= NCI_TOLERANCE_PP + 1e-9) if g is not None else None}


def cap_check(up_c, total_latest, filed_latest):
    """Every basis: the screener's cap against price x the filed count (universe.csv's own price) — gap when the
    screener prices exactly the filed count (|ratio - 1| <= CAP_GAP_BAND) while the declaration adds more than
    CAP_GAP_BAND of it. None-valued when universe.csv has no price or cap."""
    cr = (up_c or {}).get("universe_cap_to_filed_cap") if isinstance(up_c, dict) else None
    upr = (up_c or {}).get("universe_price") if isinstance(up_c, dict) else None
    uplift = (total_latest / filed_latest - 1) if (total_latest and filed_latest) else None
    eps = 1e-9   # the band edges are inclusive / exclusive exactly as stated, never by float noise (105 / 100 - 1)
    gap = (abs(cr - 1) <= CAP_GAP_BAND + eps and uplift is not None and uplift > CAP_GAP_BAND + eps) \
        if cr is not None else None
    return {"cap_ratio": round(cr, 4) if cr is not None else None, "universe_price": upr,
            "declared_uplift": round(uplift, 4) if uplift is not None else None, "band": CAP_GAP_BAND, "gap": gap}
