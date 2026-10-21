#!/usr/bin/env python3
"""Declared facts (facts.json) and the engine 5.7 rulings-release predicate — stdlib only, no I/O at import.

Engine 5.7 (Andrew's rulings of 2026-10-19, R1-R9; integration plan 07 §1.1, §1.6). SKELETON placed by the scaffold
lane L0: the release predicate every 5.7 module shares, the facts.json schema constants, the period helpers and the
small pure readers. The facts lane (L2, ruling R3) adds validation, folder verification, duplicate detection, calc
facts, the influence trace and rendering on top of these names without changing their signatures.

One predicate, one place (07 §1.1): `RULINGS_RELEASE = (5, 7, 0)` is fixed for good — the 5.7 worker obligations
(misfit_notch_reason, facts.json + the quote gate, moat_scorecard, the interim-bridge rules, share_classes,
ttm_rejection_reason) start at 5.7.0 and do not move with later release bumps. make_score (RELEASE_57 / is_57_run),
check_quotes, queue.py, moat_scorecard, interim_bridge and build_site import it from here; none imports make_score.

facts.json (D2; schema owned by L2, consumed by the moat lane L3 / L3b, the interim lane L4, the share-class lane L8
and R7): `{"schema": 1, "ticker": "TST", "facts": [{"id": "F1", "label", "value", "unit", "scale", "precision",
"period", "kind", "type", "metric"?, "source", "snippet"?, "used_for": [...], "calc"?}], "not_quantities"?: [...]}`.
Ids are "F1", "F2", ...; a reason cites them as [F1] or [F1, F3] (parse_refs).
"""
import hashlib
import json
import os
import re
import calendar as _calendar
import csv as _csv
import datetime as _dt

# ---------------------------------------------------------------------------
# The rulings release (07 §1.1)
# ---------------------------------------------------------------------------
RULINGS_RELEASE = (5, 7, 0)


def release_tuple(s):
    """'5.7.0' -> (5, 7, 0); '5.7' -> (5, 7, 0); None / unparseable -> None (the same parse as
    make_score.release_tuple)."""
    m = re.match(r"\s*(\d+)\.(\d+)(?:\.(\d+))?", s) if isinstance(s, str) else None
    if not m:
        return None
    return tuple(int(x or 0) for x in m.groups())


def release_at_least(rel, t=RULINGS_RELEASE):
    """True when release string rel parses and is >= t (a tuple, or a release string such as "5.7.0")."""
    if isinstance(t, str):
        t = release_tuple(t)
    r = release_tuple(rel)
    return r is not None and t is not None and r >= tuple(t)


def is_rulings_run(n):
    """A 5.7 run: dcf_numbers.json (dict n) from engine release 5.7.0 or later — the 5.7 worker obligations bind it.
    Output from an older release (or with no engine_release) is not one: make_score rebuilds it unchanged."""
    return isinstance(n, dict) and release_at_least(n.get("engine_release"))


# ---------------------------------------------------------------------------
# facts.json schema constants (02 §3, amended by 07 §1.6 and the lane rebases)
# ---------------------------------------------------------------------------
SCHEMA = 1
ID_RE = re.compile(r"^F[1-9]\d*$")
KINDS = ("folder", "filing", "release", "third_party")
# 07 §1.6: `event` — a dated occurrence or term carrying a number (contract length, price increase, patent-expiry
# count); a `metric` fact always sits in a series (R4), an `event` fact may stand alone where the moat lane allows it
TYPES = ("actual", "guidance", "estimate", "metric", "event")
UNIT_RE = re.compile(r"^(?:[A-Z]{3}(?:/(?:share|ADS))?|pct|pp|bps|x|count)$")   # pct / pp / bps are fractions
SCALES = ("", "K", "M", "B", "T")
PERIOD_RE = re.compile(r"^(?:FY\d{4}|CY\d{4}|Q[1-4] FY\d{4}|H[12] FY\d{4}|9M FY\d{4}|TTM \d{4}-\d{2}-\d{2}"
                       r"|\d{4}-\d{2}-\d{2})$")
METRIC_RE = re.compile(r"^[a-z][a-z0-9_]{1,40}$")
SNIPPET_KINDS = ("filing", "release", "third_party")   # non-folder kinds carry a verbatim snippet (R3)

# used_for tags. Each influence field's tag is reserved here for its lane (INFLUENCE_TAGS); `moat:<name>` is a
# pattern (MOAT_TAG_NAMES), checked by used_for_problem.
USED_FOR = ("context", "scenarios", "guidance_check", "flag_resolution",
            "tier_override",            # L2 (02 §5): tier_override_reason
            "misfit_notch",             # L1 (R1): misfit_notch_reason
            "base_override",            # L2: a plain base_override pin's reason / source
            "moat_divergence",          # L3 (R4): moat_scorecard.moat_divergence_reason
            "low_roic",                 # L3 (07 §1.6): moat_scorecard.low_roic_reason
            "high_return_low_moat",     # L3 (03b): moat_scorecard.high_return_low_moat_reason
            "erosion_rebuttal",         # L3 / L3b (03b, 10): moat_scorecard.erosion_rebuttal
            "business_type_reason",     # L3 / L3b (03b, 10): moat_scorecard.business_type_reason
            "interim_bridge",           # L4 (R2a)
            "share_classes",            # L8 (R6): share_classes reasons and up_c_suspect_reason
            "ttm_rejection")            # R7: ttm_rejection_reason
MOAT_TAG_PREFIX = "moat:"
# 03b §10.1: the 11 core pillars, the 4 supporting factors and the sources block
MOAT_CORE_PILLARS = ("returns_on_capital", "industry_structure", "capital_intensity", "scale_economics",
                     "pricing_power", "retention", "reach_and_growth", "switching_costs", "concentration",
                     "erosion_risks", "customer_regard")
MOAT_SUPPORTING_FACTORS = ("product_quality", "market_share", "execution", "management")
MOAT_TAG_NAMES = MOAT_CORE_PILLARS + MOAT_SUPPORTING_FACTORS + ("sources",)
# retired by the M1b amendment (03b) -> where the evidence goes now
RETIRED_MOAT_TAGS = {"market_position": "supporting.market_share",
                     "reinvestment_discipline": "supporting.management",
                     "capital_allocation": "supporting.management",
                     "durability_risks": "pillars.erosion_risks"}
# a third-party fact never supports these alone (R3); L2 enforces it
THIRD_PARTY_NOT_SOLE_SUPPORT = ("tier_override", "misfit_notch", "base_override", "ttm_rejection")

# Influence fields (judgment.json path -> the used_for tag a fact it cites must list). One table for every lane's
# reason fields so L2's rule "a cited fact lists the field's tag" has one source; each lane checks its own fields
# through make_score.check_influence on 5.7 runs.
INFLUENCE_TAGS = {
    "tier_override_reason": "tier_override",                                    # L2
    "misfit_notch_reason": "misfit_notch",                                      # L1 (R1)
    "base_override": "base_override",                                           # L2 (.reason / .source, plain pin)
    "moat_scorecard.moat_divergence_reason": "moat_divergence",                 # L3 (R4)
    "moat_scorecard.low_roic_reason": "low_roic",                               # L3
    "moat_scorecard.high_return_low_moat_reason": "high_return_low_moat",       # L3
    "moat_scorecard.erosion_rebuttal": "erosion_rebuttal",                      # L3 / L3b
    "moat_scorecard.business_type_reason": "business_type_reason",              # L3 / L3b
    "share_classes.reason": "share_classes",                                    # L8 (R6)
    "share_classes.ack_reason": "share_classes",
    "share_classes.nci_gap_reason": "share_classes",
    "share_classes.cap_gap_reason": "share_classes",
    "share_classes.diluted_gap_reason": "share_classes",
    "up_c_suspect_reason": "share_classes",
    "ttm_rejection_reason": "ttm_rejection",                                    # R7
}


def used_for_problem(tag):
    """None when tag is a valid facts.json used_for entry, else why not: a fixed USED_FOR tag, or `moat:<name>` with
    a core pillar, a supporting factor or `sources`; a retired moat name names where it went (M1b)."""
    if not isinstance(tag, str) or not tag:
        return f"used_for entry {tag!r} is not a non-empty string"
    if tag in USED_FOR:
        return None
    if tag.startswith(MOAT_TAG_PREFIX):
        name = tag[len(MOAT_TAG_PREFIX):]
        if name in MOAT_TAG_NAMES:
            return None
        if name in RETIRED_MOAT_TAGS:
            return (f"used_for {tag!r}: {name} is not a moat pillar since the M1b amendment — cite the evidence under "
                    f"{RETIRED_MOAT_TAGS[name]}")
        return f"used_for {tag!r}: {name!r} is not a moat pillar, supporting factor or 'sources'"
    return f"used_for {tag!r} is not one of {', '.join(USED_FOR)} or moat:<pillar>"


# ---------------------------------------------------------------------------
# Pure readers
# ---------------------------------------------------------------------------
REF_RE = re.compile(r"\[(F[1-9]\d*(?:\s*,\s*F[1-9]\d*)*)\]")


def parse_refs(text):
    """The fact ids a reason cites, in first-mention order without repeats: "[F1]" / "[F1, F3]" (02 §5)."""
    out = []
    for m in REF_RE.finditer(text if isinstance(text, str) else ""):
        for fid in re.split(r"\s*,\s*", m.group(1)):
            if fid not in out:
                out.append(fid)
    return out


def by_id(doc):
    """{id: fact} for every fact object in facts.json doc with a string id (the first one wins; validation, L2,
    reports a duplicate)."""
    out = {}
    facts = doc.get("facts") if isinstance(doc, dict) else None
    for f in facts if isinstance(facts, list) else []:
        if isinstance(f, dict) and isinstance(f.get("id"), str) and f["id"] not in out:
            out[f["id"]] = f
    return out


def series(doc, metric, calendar=None, latest_period_end=None):
    """The facts of doc whose `metric` is metric — a SERIES (R4: every metric is several periods). Sorted by
    period_end (with the folder's fiscal calendar when given) and then id; facts whose period cannot be placed keep
    their declaration order after the placed ones."""
    facts = doc.get("facts") if isinstance(doc, dict) else None
    hits = [f for f in (facts if isinstance(facts, list) else []) if isinstance(f, dict) and f.get("metric") == metric]
    keyed = [(period_end(f, calendar, latest_period_end), i, f) for i, f in enumerate(hits)]
    placed = sorted((k for k in keyed if k[0] is not None), key=lambda k: (k[0], k[1]))
    return [f for _, _, f in placed] + [f for pe, _, f in keyed if pe is None]


def _read_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def fiscal_calendar(folder):
    """{period label: "YYYY-MM-DD" period end} from the folder's own files (07 §1.6, L2 rebase A9): every
    financials_history.csv row (its bare `fy_label` "2025" read as "FY2025"), then statements.json
    periods.annual[] / periods.quarterly[] labels ("FY2025", "Q2 FY2026"). Missing or unreadable files add nothing."""
    cal = {}
    try:
        with open(os.path.join(folder, "financials_history.csv"), encoding="utf-8", newline="") as f:
            for row in _csv.DictReader(f):
                lab, end = str(row.get("fy_label") or "").strip(), str(row.get("period_end") or "").strip()
                if re.fullmatch(r"\d{4}", lab) and _iso(end):
                    cal.setdefault(f"FY{lab}", end)
    except (OSError, ValueError, _csv.Error):
        pass
    st = _read_json(os.path.join(folder, "statements.json"))
    periods = st.get("periods") if isinstance(st, dict) else None
    for key in ("annual", "quarterly"):
        for p in (periods.get(key) if isinstance(periods, dict) and isinstance(periods.get(key), list) else []):
            if isinstance(p, dict) and isinstance(p.get("label"), str) and _iso(p.get("end")):
                cal.setdefault(p["label"], p["end"])
    return cal


def _iso(s):
    """s when it is a real YYYY-MM-DD date, else None."""
    if not (isinstance(s, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", s)):
        return None
    try:
        _dt.date.fromisoformat(s)
    except ValueError:
        return None
    return s


def _month_end(year, month):
    return _dt.date(year, month, _calendar.monthrange(year, month)[1])


_SUB_MONTHS = {"Q1": 3, "Q2": 6, "Q3": 9, "Q4": 12, "H1": 6, "H2": 12, "9M": 9}


def period_end(fact, calendar=None, latest_period_end=None):
    """The "YYYY-MM-DD" end of a fact's `period` (a fact dict or the period string), else None (07 §1.6):
    an instant date and "TTM <date>" parse directly; "CY<yyyy>" is <yyyy>-12-31; "FY<yyyy>", "Q<n> FY<yyyy>",
    "H<n> FY<yyyy>", "9M FY<yyyy>" come from the fiscal calendar when it holds the label, else from the FY end
    month-day of latest_period_end applied to the label year (the fiscal-year label is the calendar year of the FY's
    end), the sub-period ending that many months after the FY start (month ends: a 52/53-week year is approximate)."""
    p = fact.get("period") if isinstance(fact, dict) else fact
    if not isinstance(p, str) or not PERIOD_RE.match(p):
        return None
    if _iso(p):
        return p
    if p.startswith("TTM "):
        return _iso(p[4:])
    if p.startswith("CY"):
        return f"{p[2:]}-12-31"
    if isinstance(calendar, dict) and _iso(calendar.get(p)):
        return calendar[p]
    anchor = _iso(latest_period_end)
    if anchor is None:
        return None
    a = _dt.date.fromisoformat(anchor)
    sub, _, fy = p.partition(" ") if " " in p else ("", "", p)
    year = int(fy[2:])
    try:
        fy_end = _dt.date(year, a.month, a.day)
    except ValueError:                       # Feb 29 anchor in a non-leap label year
        fy_end = _month_end(year, a.month)
    if not sub:
        return fy_end.isoformat()
    # the FY starts the day after the prior FY end; a sub-period ends k months later, at a month end
    start_month = fy_end.month % 12 + 1
    start_year = fy_end.year - (1 if fy_end.month != 12 else 0)
    k = _SUB_MONTHS[sub]
    m0 = start_month - 1 + k - 1          # 0-based month index of the sub-period's last month
    return _month_end(start_year + m0 // 12, m0 % 12 + 1).isoformat()


def run_hash_ok(n):
    """True when dcf_numbers.json object n carries a content_hash equal to the sha256 of its canonical payload (every
    other key, sort_keys, compact separators, default=str) — the engine's _content_hash and make_score's content-hash
    check. check_quotes' integrity check I1 and --save-run use it (they import facts only, never the engine)."""
    if not isinstance(n, dict) or not isinstance(n.get("content_hash"), str):
        return False
    canon = json.dumps({k: v for k, v in n.items() if k != "content_hash"},
                       sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(canon.encode()).hexdigest() == n["content_hash"]
