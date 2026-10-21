#!/usr/bin/env python3
"""The declared 6-K interim bridge — rules and arithmetic (engine 5.7, Andrew's ruling R2a, 2026-10-19).

R2 (Andrew, 2026-10-19: "do what we gotta to get good foreign companies working"): a 20-F / 40-F filer's trailing
twelve months, bridged from its 6-K interim report — latest FY − prior-year interim + current interim, per leg —
MAY be the scored base, but only when DECLARED leg by leg in judgment.json `interim_bridge`, following the override
pattern ({value, source, reason, kind} with the 6-K accession / document / page or section and a short verbatim
snippet), converted to USD per period at that period's own rate, and bounded by like-for-like rules (equal-length
periods, the same months a year apart, the prior interim the first part of the latest FY; a restatement, demerger or
material disposal / acquisition only when declared and resolved). Missing legs (condensed statements often omit SBC
or split capex) are declared kind "estimate" with a stated method, or the bridge refuses.

This module is pure — no network, no file reads; every function takes plain dicts — and is shared by ttm.py
--interim (which builds ttm.json from the declaration and the engine's own FY leg) and make_score.py (which
re-verifies the record), so the two never drift. Snippets are judged by quote_tokens.snippet_shows_value with the
presentation-scale rule (a statement table "in millions": "539" shows 539,000,000), the one snippet rule of R3
(SNIPPET_MAX_WORDS = 24, "under 25 words").

Refusal codes (each message starts with its code; ttm.py exits 3 on any):
- IB-SHAPE  the declaration's shape (validate_shape)
- IB-P0..P6 periods (check_periods): the FY is the engine's latest FY; the prior interim starts within 5 days of the
  FY start; the current interim starts 1-10 days after the FY end; both 80-300 days long and within 7 days of each
  other; the prior interim ends the same month-day a year before the current one (±6 days); the current interim
  ends after the FY end, not after today, at the report's period (±3 days); no period starts after its end
- IB-LFL1..5 like-for-like (check_like_for_like)
- IB-EST1..4 estimates (check_estimates); IB-DEF1..2 capex / SBC definitions (check_definitions)
- IB-SNIP   a filing leg's snippet is over 24 words or does not show its value (snippet_problems)
- ttm.py adds IB-ENG / IB-FORM / IB-UNIT / IB-FX1..3 / IB-SRC1..2 / IB-XBRL1..2 / IB-IPRD / IB-ADS / IB-SH1.
"""
import datetime
import hashlib
import json
import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import quote_tokens as _qt  # noqa: E402  (the one snippet rule, R3 / 07 §1.7)

BASIS = "fy_minus_prior_interim_plus_current_interim"
RECORD_BASIS = "declared_interim"               # ttm.json `basis` of a declared bridge (absent on the 10-Q path)
FLOW_FIELDS = ("ocf", "capex_ppe", "capex_intangibles", "sbc")
SHARES_FIELD = "shares_diluted"
LEG_NAMES = ("prior_interim", "current_interim")
ESTIMATE_METHODS = {"fy_prorated": ("capex_intangibles", "sbc"),
                    "comparative_carried": ("capex_intangibles", "sbc"),
                    "combined_in_ppe": ("capex_intangibles",),
                    "fy_diluted_count": ("shares_diluted",),
                    "other": ("capex_intangibles", "sbc")}
PERIMETER_KINDS = ("acquisition", "disposal", "demerger", "discontinued_operation", "other")
RESOLUTIONS = ("immaterial", "comparatives_re_presented", "same_business_perimeter", "outside_window")
FX_BASES = ("ecb_period_end", "none", "issuer_convenience_translation")
IMMATERIAL_REVENUE_SHARE = 0.05
FX_TOLERANCE = 0.005          # a declared interim rate vs the fetched ECB rate
ESTIMATE_TOLERANCE = 0.01     # fy_prorated reproduces within 1% (or one currency unit)
SNIPPET_MAX_WORDS = _qt.SNIPPET_MAX_WORDS
REPORT_FORMS = ("6-K", "6-K/A")
ACCESSION_RE = re.compile(r"^\d{10}-\d{2}-\d{6}$")
CURRENCY_RE = re.compile(r"^[A-Z]{3}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
FIELD_LABELS = {"ocf": "Operating cash flow", "capex_ppe": "Capex — PP&E", "capex_intangibles": "Capex — intangibles",
                "sbc": "SBC", "shares_diluted": "Shares diluted"}
P1_DAYS, P2_DAYS, P3_DELTA, P3_RANGE, P4_DAYS, P5_DAYS = 5, (1, 10), 7, (80, 300), 6, 3


# ---------------------------------------------------------------------------
# small helpers
# ---------------------------------------------------------------------------
def _d(s):
    return datetime.date.fromisoformat(s)


def days(a, b):
    """INCLUSIVE day count of a..b (ttm.py's rule: a calendar year is 365 days)."""
    return (_d(b) - _d(a)).days + 1


def shift_year(dstr, delta):
    d = _d(dstr)
    try:
        return d.replace(year=d.year + delta).isoformat()
    except ValueError:     # Feb 29
        return d.replace(year=d.year + delta, day=28).isoformat()


def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def _str(v):
    return isinstance(v, str) and bool(v.strip())


def _is_date(v):
    if not (isinstance(v, str) and DATE_RE.match(v)):
        return False
    try:
        _d(v)
        return True
    except ValueError:
        return False


def _period(v):
    return isinstance(v, list) and len(v) == 2 and all(_is_date(x) for x in v)


def leg(decl, field, name):
    """The declared leg dict (None when absent)."""
    f = ((decl or {}).get("legs") or {}).get(field)
    x = f.get(name) if isinstance(f, dict) else None
    return x if isinstance(x, dict) else None


def periods_of(decl):
    """{"fy": [s, e], "prior_interim": [s, e], "current_interim": [s, e]} as declared."""
    return {"fy": list(decl["fy_period"]), "prior_interim": list(decl["prior_interim"]["period"]),
            "current_interim": list(decl["current_interim"]["period"])}


def declaration_hash(decl):
    """sha256 of the declaration as canonical JSON (sorted keys, no whitespace, UTF-8): key order and layout do not
    change it, any value does. ttm.json records it; make_score refuses a declaration edited after ttm.py ran."""
    canon = json.dumps(decl, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()


def snippet_shows_value(snippet, value):
    """True when the snippet carries `value` at some presentation scale (units, thousands, millions, billions) at the
    snippet's own precision, signs ignored ("(182)" shows 182,000,000) — quote_tokens' rule."""
    return _qt.snippet_shows_value(snippet, value, presentation_scale=True)


def snippet_words(snippet):
    return _qt.snippet_words(snippet)


# ---------------------------------------------------------------------------
# shape
# ---------------------------------------------------------------------------
def _source_problems(src, path):
    out = []
    if not isinstance(src, dict):
        return [f"[IB-SHAPE] interim_bridge.{path}: must be an object {{accession, document, page, section}}"]
    if not (isinstance(src.get("accession"), str) and ACCESSION_RE.match(src["accession"])):
        out.append(f"[IB-SHAPE] interim_bridge.{path}.accession: must be an EDGAR accession NNNNNNNNNN-YY-NNNNNN "
                   f"(got {src.get('accession')!r})")
    if not _str(src.get("document")):
        out.append(f"[IB-SHAPE] interim_bridge.{path}.document: the file name in the filing is required")
    page = src.get("page")
    if page is not None and not (isinstance(page, int) and not isinstance(page, bool)) and not _str(page):
        out.append(f"[IB-SHAPE] interim_bridge.{path}.page: an integer, a page label or null")
    if page is None and not _str(src.get("section")):
        out.append(f"[IB-SHAPE] interim_bridge.{path}: page null needs a non-empty section (the statement / note title)")
    if src.get("section") is not None and not isinstance(src.get("section"), str):
        out.append(f"[IB-SHAPE] interim_bridge.{path}.section: must be a string")
    return out


def _leg_problems(x, field, name):
    path = f"legs.{field}.{name}"
    if not isinstance(x, dict):
        return [f"[IB-SHAPE] interim_bridge.{path}: must be an object {{value, kind, source, snippet, reason}}"]
    out = []
    v = x.get("value")
    if not _num(v) or v < 0:
        out.append(f"[IB-SHAPE] interim_bridge.{path}.value: a finite number >= 0 in full units of `currency` "
                   f"(got {v!r})")
    elif field == SHARES_FIELD and v <= 0:
        out.append(f"[IB-SHAPE] interim_bridge.{path}.value: a share count must be > 0 (got {v!r})")
    kind = x.get("kind")
    if kind not in ("filing", "estimate"):
        out.append(f"[IB-SHAPE] interim_bridge.{path}.kind: \"filing\" or \"estimate\" (got {kind!r})")
    if not _str(x.get("reason")):
        out.append(f"[IB-SHAPE] interim_bridge.{path}.reason: required")
    if kind == "filing":
        out += _source_problems(x.get("source"), f"{path}.source")
        if not _str(x.get("snippet")):
            out.append(f"[IB-SHAPE] interim_bridge.{path}.snippet: the report's own words showing the value are required")
    elif kind == "estimate":
        m = x.get("method")
        if m not in ESTIMATE_METHODS:
            out.append(f"[IB-SHAPE] interim_bridge.{path}.method: one of {sorted(ESTIMATE_METHODS)} (got {m!r})")
        if m == "other" and not _str(x.get("method_detail")):
            out.append(f"[IB-SHAPE] interim_bridge.{path}.method_detail: required for method \"other\"")
    if field == SHARES_FIELD and x.get("share_basis") is not None and not _str(x.get("share_basis")):
        out.append(f"[IB-SHAPE] interim_bridge.{path}.share_basis: a string when present (the share-class lane's basis)")
    return out


def validate_shape(decl):
    """Every shape error of a judgment.json interim_bridge declaration, each "[IB-SHAPE] interim_bridge.<path>: ...".
    [] when the shape is valid. Legs missing entirely are check_estimates' (IB-EST4), not shape errors."""
    if not isinstance(decl, dict):
        return ["[IB-SHAPE] interim_bridge: must be an object (see _system/examples/interim_bridge.example.json)"]
    out = []
    known = {"basis", "currency", "fy_period", "prior_interim", "current_interim", "report", "legs", "like_for_like",
             "fx", "reason"}
    for k in decl:
        if k not in known and not str(k).startswith("_"):
            out.append(f"[IB-SHAPE] interim_bridge.{k}: unknown key")
    if decl.get("basis") != BASIS:
        out.append(f"[IB-SHAPE] interim_bridge.basis: must be {BASIS!r} (got {decl.get('basis')!r})")
    ccy = decl.get("currency")
    if not (isinstance(ccy, str) and CURRENCY_RE.match(ccy)):
        out.append(f"[IB-SHAPE] interim_bridge.currency: an ISO 4217 code in upper case (got {ccy!r})")
    if not _period(decl.get("fy_period")):
        out.append("[IB-SHAPE] interim_bridge.fy_period: [start, end] ISO dates")
    for name in LEG_NAMES:
        p = decl.get(name)
        if not (isinstance(p, dict) and _period(p.get("period"))):
            out.append(f"[IB-SHAPE] interim_bridge.{name}.period: [start, end] ISO dates")
    rep = decl.get("report")
    if not isinstance(rep, dict):
        out.append("[IB-SHAPE] interim_bridge.report: must be an object {form, accession, document, filed, title}")
    else:
        if not _str(rep.get("form")):
            out.append("[IB-SHAPE] interim_bridge.report.form: required (6-K)")
        if not (isinstance(rep.get("accession"), str) and ACCESSION_RE.match(rep["accession"])):
            out.append(f"[IB-SHAPE] interim_bridge.report.accession: an EDGAR accession (got {rep.get('accession')!r})")
        if not _str(rep.get("document")):
            out.append("[IB-SHAPE] interim_bridge.report.document: required")
        if rep.get("filed") is not None and not _is_date(rep.get("filed")):
            out.append("[IB-SHAPE] interim_bridge.report.filed: an ISO date when present")
    legs = decl.get("legs")
    if not isinstance(legs, dict):
        out.append("[IB-SHAPE] interim_bridge.legs: must be an object {ocf, capex_ppe, capex_intangibles, sbc, "
                   "shares_diluted}")
    else:
        for f, legs_f in legs.items():
            if f not in FLOW_FIELDS + (SHARES_FIELD,):
                out.append(f"[IB-SHAPE] interim_bridge.legs.{f}: unknown field (allowed: "
                           f"{', '.join(FLOW_FIELDS + (SHARES_FIELD,))})")
                continue
            if not isinstance(legs_f, dict):
                out.append(f"[IB-SHAPE] interim_bridge.legs.{f}: must be an object of legs")
                continue
            allowed = ("current_interim",) if f == SHARES_FIELD else LEG_NAMES
            for name, x in legs_f.items():
                if name not in allowed:
                    out.append(f"[IB-SHAPE] interim_bridge.legs.{f}.{name}: unknown leg (allowed: {', '.join(allowed)})")
                    continue
                out += _leg_problems(x, f, name)
    lfl = decl.get("like_for_like")
    if not isinstance(lfl, dict):
        out.append("[IB-SHAPE] interim_bridge.like_for_like: must be an object {comparative_restated, perimeter_changes, ...}")
    else:
        rs = lfl.get("comparative_restated")
        if not isinstance(rs, bool):
            out.append("[IB-SHAPE] interim_bridge.like_for_like.comparative_restated: true or false (required)")
        if rs is True:
            if not _str(lfl.get("comparative_note")):
                out.append("[IB-SHAPE] interim_bridge.like_for_like.comparative_note: required when the comparative was restated")
            out += _source_problems(lfl.get("comparative_source"), "like_for_like.comparative_source")
            if not _str(lfl.get("comparative_snippet")):
                out.append("[IB-SHAPE] interim_bridge.like_for_like.comparative_snippet: required when the comparative was restated")
            r = lfl.get("restatement")
            if not isinstance(r, dict):
                out.append("[IB-SHAPE] interim_bridge.like_for_like.restatement: {description, fy_leg_consistent, source, "
                           "snippet} required when the comparative was restated")
            else:
                if not _str(r.get("description")):
                    out.append("[IB-SHAPE] interim_bridge.like_for_like.restatement.description: required")
                if not isinstance(r.get("fy_leg_consistent"), bool):
                    out.append("[IB-SHAPE] interim_bridge.like_for_like.restatement.fy_leg_consistent: true or false")
                out += _source_problems(r.get("source"), "like_for_like.restatement.source")
                if not _str(r.get("snippet")):
                    out.append("[IB-SHAPE] interim_bridge.like_for_like.restatement.snippet: required")
        pcs = lfl.get("perimeter_changes")
        if not isinstance(pcs, list):
            out.append("[IB-SHAPE] interim_bridge.like_for_like.perimeter_changes: a list (required; [] when none)")
        else:
            for i, pc in enumerate(pcs):
                path = f"like_for_like.perimeter_changes[{i}]"
                if not isinstance(pc, dict):
                    out.append(f"[IB-SHAPE] interim_bridge.{path}: must be an object")
                    continue
                if pc.get("kind") not in PERIMETER_KINDS:
                    out.append(f"[IB-SHAPE] interim_bridge.{path}.kind: one of {', '.join(PERIMETER_KINDS)}")
                if not _is_date(pc.get("effective_date")):
                    out.append(f"[IB-SHAPE] interim_bridge.{path}.effective_date: an ISO date")
                if not isinstance(pc.get("material"), bool):
                    out.append(f"[IB-SHAPE] interim_bridge.{path}.material: true or false")
                if pc.get("resolution") not in RESOLUTIONS:
                    out.append(f"[IB-SHAPE] interim_bridge.{path}.resolution: one of {', '.join(RESOLUTIONS)}")
                rsh = pc.get("revenue_share")
                if rsh is not None and not (_num(rsh) and 0 <= rsh <= 1):
                    out.append(f"[IB-SHAPE] interim_bridge.{path}.revenue_share: a fraction 0..1 (0.023 = 2.3%)")
                for k in ("description", "reason"):
                    if not _str(pc.get(k)):
                        out.append(f"[IB-SHAPE] interim_bridge.{path}.{k}: required")
                out += _source_problems(pc.get("source"), f"{path}.source")
                if not _str(pc.get("snippet")):
                    out.append(f"[IB-SHAPE] interim_bridge.{path}.snippet: required")
    fx = decl.get("fx")
    if not isinstance(fx, dict):
        out.append("[IB-SHAPE] interim_bridge.fx: must be an object {basis, source, fy, prior_interim, current_interim}")
    else:
        basis = fx.get("basis")
        if basis not in FX_BASES:
            out.append(f"[IB-SHAPE] interim_bridge.fx.basis: one of {', '.join(FX_BASES)} (got {basis!r})")
        elif isinstance(ccy, str) and ccy != "USD" and basis != "ecb_period_end":
            out.append(f"[IB-SHAPE] interim_bridge.fx.basis: legs declared in {ccy} convert at ecb_period_end rates")
        elif ccy == "USD" and basis == "ecb_period_end":
            out.append("[IB-SHAPE] interim_bridge.fx.basis: USD legs take basis none or issuer_convenience_translation")
        if not _str(fx.get("source")):
            out.append("[IB-SHAPE] interim_bridge.fx.source: required")
        if basis == "ecb_period_end" or basis == "issuer_convenience_translation":
            names = ("fy",) + LEG_NAMES if basis == "ecb_period_end" else LEG_NAMES
            per_end = {"fy": (decl.get("fy_period") or [None, None])[-1] if _period(decl.get("fy_period")) else None}
            for name in LEG_NAMES:
                p = (decl.get(name) or {}).get("period") if isinstance(decl.get(name), dict) else None
                per_end[name] = p[1] if _period(p) else None
            for name in names:
                r = fx.get(name)
                if not (isinstance(r, dict) and _is_date(r.get("date")) and _num(r.get("rate")) and r["rate"] > 0):
                    out.append(f"[IB-SHAPE] interim_bridge.fx.{name}: {{date, rate > 0}} required")
                    continue
                if per_end.get(name) and r["date"] != per_end[name]:
                    out.append(f"[IB-SHAPE] interim_bridge.fx.{name}.date: {r['date']} is not the period end "
                               f"{per_end[name]} — each leg converts at its own period-end rate (R2)")
                if basis == "issuer_convenience_translation" and not _str(r.get("snippet")):
                    out.append(f"[IB-SHAPE] interim_bridge.fx.{name}.snippet: the report's own rate sentence is required")
    if not _str(decl.get("reason")):
        out.append("[IB-SHAPE] interim_bridge.reason: why the bridge is the right base (required)")
    return out


# ---------------------------------------------------------------------------
# periods
# ---------------------------------------------------------------------------
def check_periods(decl, fy_period, today, report_date=None):
    """IB-P0..IB-P6 against the engine's latest FY `fy_period` ([start, end]; None skips P0 / P1 / P2 / P5's FY test),
    `today` (an ISO date or date) and the report's period `report_date` (EDGAR reportDate; None skips that test)."""
    out = []
    per = periods_of(decl)
    for name in ("fy", "prior_interim", "current_interim"):
        s, e = per[name]
        if s > e:
            out.append(f"[IB-P6] a period's start is after its end: {name} {s}..{e}")
    if out:
        return out
    fy, pr, cu = per["fy"], per["prior_interim"], per["current_interim"]
    if fy_period is not None and list(fy_period) != fy:
        out.append(f"[IB-P0] interim_bridge.fy_period {fy[0]}..{fy[1]} is not the engine's latest fiscal year "
                   f"{fy_period[0]}..{fy_period[1]} (dcf_numbers.json latest_period_end) — the bridge must start from the "
                   "FY the engine scored")
    fs, fe = (fy_period or fy)[0], (fy_period or fy)[1]
    d1 = (_d(pr[0]) - _d(fs)).days
    if abs(d1) > P1_DAYS:
        out.append(f"[IB-P1] prior interim starts {pr[0]}, {d1} days from the FY start {fs} — the prior interim must be "
                   "the first part of the latest FY")
    d2 = (_d(cu[0]) - _d(fe)).days
    if not (P2_DAYS[0] <= d2 <= P2_DAYS[1]):
        out.append(f"[IB-P2] current interim starts {cu[0]}, {d2} days after the FY end {fe} (must be "
                   f"{P2_DAYS[0]}-{P2_DAYS[1]})")
    a, b = days(*pr), days(*cu)
    if abs(a - b) > P3_DELTA or not all(P3_RANGE[0] <= x <= P3_RANGE[1] for x in (a, b)):
        out.append(f"[IB-P3] interim lengths differ: prior {a} days, current {b} days (|Δ| ≤ {P3_DELTA}; each "
                   f"{P3_RANGE[0]}-{P3_RANGE[1]})")
    target = shift_year(cu[1], -1)
    if abs((_d(pr[1]) - _d(target)).days) > P4_DAYS:
        out.append(f"[IB-P4] prior interim ends {pr[1]}, not the same months as the current interim end {cu[1]} one "
                   f"year earlier (±{P4_DAYS} days)")
    today_s = today.isoformat() if isinstance(today, datetime.date) else str(today)
    why = []
    if cu[1] <= fe:
        why.append(f"not after the FY end {fe}")
    if cu[1] > today_s:
        why.append(f"after today {today_s}")
    if report_date and abs((_d(cu[1]) - _d(report_date)).days) > P5_DAYS:
        why.append(f"not the report's period {report_date} (±{P5_DAYS} days)")
    if why:
        out.append(f"[IB-P5] current interim ends {cu[1]}: " + "; ".join(why))
    return out


# ---------------------------------------------------------------------------
# like-for-like
# ---------------------------------------------------------------------------
def check_like_for_like(decl):
    """IB-LFL1..IB-LFL5 (window = [prior interim start, current interim end])."""
    out = []
    lfl = decl.get("like_for_like") or {}
    per = periods_of(decl)
    a, b = per["prior_interim"][0], per["current_interim"][1]
    restated = lfl.get("comparative_restated") is True
    consistent = restated and (lfl.get("restatement") or {}).get("fy_leg_consistent") is True
    if restated and not consistent:
        out.append("[IB-LFL1] the comparative was restated (comparative_restated true) but restatement.fy_leg_consistent "
                   "is not true — FY (from the 20-F) minus a restated prior interim mixes bases; wait for the next annual "
                   "report or block NEEDS_MAIN_AGENT: base")
    for pc in lfl.get("perimeter_changes") or []:
        kind, date, res = pc.get("kind"), pc.get("effective_date"), pc.get("resolution")
        inside = a <= date <= b
        if res == "outside_window" and inside:
            out.append(f"[IB-LFL4] resolution outside_window but {date} is inside {a}..{b}")
            continue
        if res == "immaterial":
            rs = pc.get("revenue_share")
            if pc.get("material") is True or not (_num(rs) and rs < IMMATERIAL_REVENUE_SHARE) or not pc.get("source"):
                out.append(f"[IB-LFL3] {kind} on {date} declared immaterial without revenue_share below "
                           f"{IMMATERIAL_REVENUE_SHARE:.0%} (got {rs}) and its source"
                           + (" — and it is declared material" if pc.get("material") is True else ""))
            continue
        if not (inside and pc.get("material") is True):
            continue
        if kind == "discontinued_operation" and res != "comparatives_re_presented":
            out.append(f"[IB-LFL5] a material discontinued_operation inside the window ({date}) is resolved only by "
                       "comparatives_re_presented")
            continue
        ok = ((res == "comparatives_re_presented" and consistent)
              or (res == "same_business_perimeter" and kind == "demerger"))
        if not ok:
            out.append(f"[IB-LFL2] perimeter change {kind} on {date} lies inside the bridge window {a}..{b}, is material, "
                       f"and its resolution {res} does not resolve it — material changes need comparatives_re_presented "
                       "(with comparative_restated and fy_leg_consistent true) or, for a demerger only, "
                       "same_business_perimeter")
    return out


# ---------------------------------------------------------------------------
# estimates and definitions
# ---------------------------------------------------------------------------
def estimate_value(decl, field, name, fy_local, fy_shares=None):
    """What the leg's declared method gives (None for comparative_carried / other: no value of its own)."""
    x = leg(decl, field, name) or {}
    m = x.get("method")
    per = periods_of(decl)
    if m == "fy_prorated" and _num((fy_local or {}).get(field)):
        return fy_local[field] * days(*per[name]) / days(*per["fy"])
    if m == "combined_in_ppe":
        return 0.0
    if m == "fy_diluted_count":
        return fy_shares
    if m == "comparative_carried":
        p = leg(decl, field, "prior_interim") or {}
        return p.get("value")
    return None


def check_estimates(decl, fy_local, fy_period=None, fy_shares=None):
    """IB-EST1..IB-EST4. fy_local: {field: FY value in `currency`} (the engine's FY leg); fy_shares: the CSV FY diluted
    count (the fy_diluted_count method). fy_period is accepted for the design's signature; the declared fy_period is
    the one IB-P0 binds."""
    out = []
    for f in FLOW_FIELDS:
        for name in LEG_NAMES:
            if leg(decl, f, name) is None:
                out.append(f"[IB-EST4] {f}.{name} is missing — condensed statements often omit SBC or intangibles; "
                           "declare it kind filing from the report or kind estimate with a method (R2), or the bridge "
                           "refuses")
    if leg(decl, SHARES_FIELD, "current_interim") is None:
        out.append(f"[IB-EST4] {SHARES_FIELD}.current_interim is missing — the TTM denominator is the current interim's "
                   "weighted average diluted count (kind filing; kind estimate fy_diluted_count when the report prints none)")
    for f in FLOW_FIELDS + (SHARES_FIELD,):
        for name in (("current_interim",) if f == SHARES_FIELD else LEG_NAMES):
            x = leg(decl, f, name)
            if x is None or x.get("kind") != "estimate":
                continue
            m = x.get("method")
            if f in ("ocf", "capex_ppe"):
                out.append(f"[IB-EST1] {f}.{name} must be kind filing — the condensed cash-flow statement prints both")
                continue
            if f not in ESTIMATE_METHODS.get(m, ()):
                out.append(f"[IB-EST3] method {m} is not allowed for {f}")
                continue
            v = x.get("value")
            if m == "comparative_carried":
                p = leg(decl, f, "prior_interim") or {}
                if name != "current_interim" or p.get("kind") != "filing" or p.get("value") != v:
                    out.append(f"[IB-EST2] {f}.{name} (comparative_carried) declares {v}; the method gives "
                               f"{p.get('value') if name == 'current_interim' else 'nothing for the prior leg'} (the current "
                               "leg carries the filed prior leg)")
                continue
            if m == "combined_in_ppe":
                ppe = leg(decl, "capex_ppe", name) or {}
                txt = " ".join(str(t or "") for t in (ppe.get("reason"), ppe.get("snippet"),
                                                     (ppe.get("source") or {}).get("section"))).lower()
                if v != 0 or "intangible" not in txt:
                    out.append(f"[IB-EST2] {f}.{name} (combined_in_ppe) declares {v}; the method gives 0, and the capex_ppe "
                               f"{name} leg must name the combined PP&E + intangibles line (its reason, snippet or section)")
                continue
            if m == "fy_diluted_count":
                if fy_shares is None or v != fy_shares:
                    out.append(f"[IB-EST2] {f}.{name} (fy_diluted_count) declares {v}; the method gives {fy_shares}")
                continue
            if m == "fy_prorated":
                want = estimate_value(decl, f, name, fy_local)
                if want is None or abs(v - want) > max(1.0, ESTIMATE_TOLERANCE * abs(want)):
                    out.append(f"[IB-EST2] {f}.{name} (fy_prorated) declares {v}; the method gives "
                               f"{'n/a' if want is None else f'{want:,.0f}'}")
    return out


def check_definitions(decl, fy_usd):
    """IB-DEF1 / IB-DEF2 (and IB-EST4 for an absent intangible leg beside FY intangibles): the TTM never mixes capex or
    SBC definitions. fy_usd: {field: the engine's FY value}."""
    out = []
    fi = (fy_usd or {}).get("capex_intangibles") or 0
    fs = (fy_usd or {}).get("sbc") or 0
    for name in LEG_NAMES:
        x = leg(decl, "capex_intangibles", name)
        if fi > 0 and x is None:
            out.append(f"[IB-EST4] capex_intangibles.{name} is missing while the engine's FY capex includes intangible "
                       f"purchases ({fi:,.0f}) — declare it (kind filing, or an estimate method), or the TTM mixes capex "
                       "definitions")
        if fi == 0 and x is not None and _num(x.get("value")) and x["value"] > 0:
            out.append(f"[IB-DEF1] the engine's FY capex has no intangible purchases (capex_provenance) but {name} declares "
                       f"{x['value']:,.0f} — the TTM would mix capex definitions")
        s = leg(decl, "sbc", name)
        if fs == 0 and s is not None and _num(s.get("value")) and s["value"] > 0:
            out.append(f"[IB-DEF2] the engine's FY SBC is 0 but sbc.{name} declares {s['value']:,.0f} — the TTM would mix "
                       "SBC definitions")
    return out


def snippet_problems(decl):
    """IB-SNIP: every filing leg's snippet is at most SNIPPET_MAX_WORDS words and shows its value at a presentation
    scale; the like-for-like snippets keep the word limit."""
    out = []
    for f in FLOW_FIELDS + (SHARES_FIELD,):
        for name in (("current_interim",) if f == SHARES_FIELD else LEG_NAMES):
            x = leg(decl, f, name)
            if not x or x.get("kind") != "filing":
                continue
            sn = x.get("snippet")
            if snippet_words(sn) > SNIPPET_MAX_WORDS:
                out.append(f"[IB-SNIP] {f}.{name} snippet is {snippet_words(sn)} words (at most {SNIPPET_MAX_WORDS}, R3)")
            elif not snippet_shows_value(sn, x.get("value")):
                out.append(f"[IB-SNIP] {f}.{name} snippet does not show {x.get('value'):,} at any presentation scale")
    lfl = decl.get("like_for_like") or {}
    sns = [("like_for_like.comparative_snippet", lfl.get("comparative_snippet")),
           ("like_for_like.restatement.snippet", (lfl.get("restatement") or {}).get("snippet"))]
    sns += [(f"like_for_like.perimeter_changes[{i}].snippet", pc.get("snippet"))
            for i, pc in enumerate(lfl.get("perimeter_changes") or []) if isinstance(pc, dict)]
    for path, sn in sns:
        if sn and snippet_words(sn) > SNIPPET_MAX_WORDS:
            out.append(f"[IB-SNIP] {path} is {snippet_words(sn)} words (at most {SNIPPET_MAX_WORDS}, R3)")
    return out


def leg_lists(decl):
    """(estimate_legs, unverified_legs) as "field.leg" strings, in declaration order (method "other" is unverified)."""
    est, unv = [], []
    for f in FLOW_FIELDS + (SHARES_FIELD,):
        for name in (("current_interim",) if f == SHARES_FIELD else LEG_NAMES):
            x = leg(decl, f, name)
            if x and x.get("kind") == "estimate":
                est.append(f"{f}.{name}")
                if x.get("method") == "other":
                    unv.append(f"{f}.{name}")
    return est, unv


# ---------------------------------------------------------------------------
# arithmetic
# ---------------------------------------------------------------------------
def _arith(fy, prior, cur, rates, shares, ads):
    """fy: {field: {"local", "usd"}}; prior / cur: {field: local value}; rates: {"prior_interim", "current_interim"}."""
    legs = {}
    for f in FLOW_FIELDS:
        p, c = float(prior[f]), float(cur[f])
        legs[f] = {"fy": {"local": fy[f]["local"], "usd": fy[f]["usd"]},
                   "prior_interim": {"local": p, "usd": p * rates["prior_interim"]},
                   "current_interim": {"local": c, "usd": c * rates["current_interim"]},
                   "ttm_local": fy[f]["local"] - p + c,
                   "ttm_usd": fy[f]["usd"] - p * rates["prior_interim"] + c * rates["current_interim"]}
    capex_usd = legs["capex_ppe"]["ttm_usd"] + legs["capex_intangibles"]["ttm_usd"]
    capex_local = legs["capex_ppe"]["ttm_local"] + legs["capex_intangibles"]["ttm_local"]
    oe = legs["ocf"]["ttm_usd"] - capex_usd - legs["sbc"]["ttm_usd"]
    oe_local = legs["ocf"]["ttm_local"] - capex_local - legs["sbc"]["ttm_local"]
    per_ord = oe / shares if shares else None
    return {"legs": legs, "ttm_ocf": legs["ocf"]["ttm_usd"], "ttm_capex": capex_usd, "ttm_capex_local": capex_local,
            "ttm_sbc": legs["sbc"]["ttm_usd"], "ttm_shares_diluted": shares, "ttm_oe_total": oe,
            "ttm_oe_total_local": oe_local, "ttm_oe_per_ordinary_share": per_ord,
            "ttm_oe_per_share": per_ord * ads if per_ord is not None else None, "ads_ratio": ads}


def compute(decl, fy_leg, rates, ads_ratio):
    """The bridge's arithmetic (no checks): per flow field TTM_local = FY_local − prior + current and TTM_usd = FY_usd −
    prior × r_prior + current × r_current (each interim leg at its own period-end rate, R2; the FY leg is the engine's
    own USD figure); capex = PP&E + intangibles; OE = OCF − capex − SBC; the denominator is the current interim's
    weighted average diluted count; ttm_oe_per_share = OE ÷ shares × ADS ratio (per ADS, like the price).
    fy_leg: {field: {"local", "usd"}}; rates: {"fy", "prior_interim", "current_interim"} (1.0 for USD legs)."""
    prior = {f: leg(decl, f, "prior_interim")["value"] for f in FLOW_FIELDS}
    cur = {f: leg(decl, f, "current_interim")["value"] for f in FLOW_FIELDS}
    shares = float(leg(decl, SHARES_FIELD, "current_interim")["value"])
    return _arith(fy_leg, prior, cur, rates, shares, float(ads_ratio))


def recompute_from_record(ttm):
    """make_score's re-derivation from a declared-interim ttm.json alone: the record's FY USD legs, its interim local
    legs, its rates_used and ADS ratio give every TTM figure again (None when the record is not a declared bridge or
    is malformed)."""
    try:
        legs = ttm["legs"]
        fy = {f: {"local": float(legs[f]["fy"]["local"]), "usd": float(legs[f]["fy"]["usd"])} for f in FLOW_FIELDS}
        prior = {f: float(legs[f]["prior_interim"]["local"]) for f in FLOW_FIELDS}
        cur = {f: float(legs[f]["current_interim"]["local"]) for f in FLOW_FIELDS}
        ru = ttm["fx"]["rates_used"]
        rates = {k: float(ru[k]) for k in ("prior_interim", "current_interim")}
        shares = float(ttm["shares"]["current_interim"]["value"])
        return _arith(fy, prior, cur, rates, shares, float(ttm["ads_ratio"]))
    except (KeyError, TypeError, ValueError):
        return None
