#!/usr/bin/env python3
"""Declared facts (facts.json) and the engine 5.7 rulings-release predicate — stdlib only, no I/O at import.

Engine 5.7 (Andrew's rulings of 2026-10-19, R1-R9; integration plan 07 §1.1, §1.6). The scaffold lane L0 placed the
release predicate every 5.7 module shares, the facts.json schema constants, the period helpers and the small pure
readers; the facts lane (L2, Andrew's ruling R3 — strict quoting, 2026-10-19) adds, on top of those names and
without changing their signatures (design 02 §3-§5, §7.4, §8.4; L2 rebase A7-A9):
- validate(doc, ticker): the facts.json schema, every rule a make_score refusal (02 §8.2 texts);
- the folder path grammar `<file>:<selector>` (resolve): financials_history.csv `<column>[FY2025 | period_end]`,
  statements.json `<section>.<row>.<annual|quarterly|growth_annual|growth_quarterly>[<label | end>]` and
  `<section>.<row>.ttm@<end>`, fundamentals.json `annual[..].<field>` / `quarterly[..].<field>` /
  `ttm.<field>@<end>` / `dividends.<field>` / `profile.<field>`, segments.json
  `tables[<axis>/<concept>/<periodicity>].rows[<member | label>].<values|share_of_total|growth_yoy>[<period>]` and
  `tables[..].total.values[<period>]`, profile.json / ttm.json dotted paths, dcf_numbers.json dotted paths as calc
  operands only; integer indexes are refused (they shift when a year is added), a ttm selector names its end;
- check(...): a folder fact VERIFIED against the named file (unit and value at the declared precision), a calc fact
  reproduced from its operands (kind = its weakest operand's), a snippet that shows the number (quote_tokens'
  snippet_shows_value; under 25 words), a filing / release / third-party fact that repeats a folder figure refused
  (same metric and period, or any same-period leaf at >= 4 significant digits; fewer is a warning), guidance /
  estimate facts older than the latest filing the engine used marked STALE (never a refusal), and drift on a
  rebuild (facts.json unchanged since the last score, a folder file changed) recorded instead of refused;
- influence_support(...): the influence trace make_score.check_influence runs on a 5.7 run's reasons (02 §5,
  10 §(l)): every number traces to an engine source or a cited fact, a reason never rests on third-party facts
  alone, and a cited fact lists the field's used_for tag;
- fmt_value / key_numbers_lines: the "Declared facts (not engine output)" section, worker text in “…”.
The module reads folder files only through check() / resolve() (callers pass the folder); nothing is written.

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
import glob as _glob
import math as _math
import sys as _sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)
import quote_tokens as _qt  # noqa: E402  (L2: the one tokenizer — snippets and the influence trace)

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


# ===========================================================================
# L2 (R3 strict quoting, Andrew 2026-10-19): validation, the folder path grammar, verification, calc facts,
# duplicates, staleness, the influence trace and rendering (02 §3-§5, §7.4, §8.4; rebase A7-A9, A14)
# ===========================================================================
ACCESSION_RE = re.compile(r"^\d{10}-\d{2}-\d{6}$")
FILING_FORMS = ("10-K", "10-Q", "20-F", "40-F", "6-K", "8-K", "10-KT", "20-F/A", "10-K/A", "40-F/A", "10-Q/A",
                "S-1", "F-1", "DEF 14A")                                   # and 424B<n>
RELEASE_FORMS = ("8-K", "6-K")                                             # R3: "8-K/6-K exhibit"
SCALE_MULT = {"": 1.0, "K": 1e3, "M": 1e6, "B": 1e9, "T": 1e12}
KIND_RANK = {"third_party": 0, "release": 1, "filing": 1, "folder": 2}    # a calc fact's kind is its weakest operand's
CALC_OPS = ("growth", "ratio", "diff", "sum", "mid", "cagr")
CALC_MAX_OPERANDS = 6
LABEL_LEN = (3, 80)
NOT_QUANTITIES_MAX = 20
NOT_QUANTITY_LEN = (3, 60)
GUIDANCE_TYPES = ("guidance", "estimate")                                  # STALE when older than the engine's filing
DUP_MIN_SIGNIFICANT = 4                       # 02 §4.5: a same-period folder leaf equal at >= 4 significant digits
FOLDER_FILES = ("financials_history.csv", "statements.json", "fundamentals.json", "segments.json", "profile.json",
                "ttm.json")
CALC_ONLY_FILES = ("dcf_numbers.json",)       # engine figures are quotable directly: a path into it is a calc operand
NUMBER_OPTIONAL_FIELDS = ("base_override",)   # rebase I13: a plain pin's reason / source need not carry a number
ANNUAL_FILED_FORMS = ("10-K", "10-Q", "20-F", "40-F", "6-K", "10-KT")
_FU_PCT_SUFFIX = ("_margin", "_growth", "_yoy", "_pct", "_pct_rev", "_pct_ocf", "_pct_assets", "_yield", "_cagr_3y",
                  "_cagr_5y")
# 02 §4.5 metric-keyed duplicate lookup: metric -> (financials_history.csv column, statements.json row key,
# fundamentals.json field); None where the file has no such figure
CANONICAL_METRICS = {
    "revenue": ("revenue", "revenue", "revenue"), "net_income": ("net_income", "net_income", "net_income"),
    "operating_income": ("operating_income", "operating_income", "operating_income"), "ocf": ("ocf", "ocf", "ocf"),
    "capex": ("capex", "capex", "capex"), "sbc": ("sbc", "sbc", "sbc"), "da": ("da", "da", "da"),
    "fcf": ("fcf", "fcf", "fcf"), "eps_diluted": (None, "eps_diluted", "eps_diluted"),
    "eps_basic": (None, "eps_basic", "eps_basic"), "shares_diluted": ("shares_diluted", "shares_diluted", "shares_diluted"),
    "buybacks": (None, "buybacks", "buybacks"), "dividends_paid": (None, "dividends_paid", "dividends_paid"),
    "dps_paid": (None, None, "dps_paid"), "gross_margin": (None, "gross_margin", "gross_margin"),
    "operating_margin": (None, "operating_margin", "operating_margin"), "net_margin": (None, "net_margin", "net_margin"),
    "roic_proxy": (None, "roic_proxy", "roic_proxy"), "roe": (None, "roe", "roe"), "cash": ("cash", "cash", "cash"),
    "total_debt": (None, "total_debt", "total_debt"), "net_debt": (None, "net_debt", "net_debt"),
    "equity": ("equity", "equity", "equity"), "goodwill": (None, "goodwill", "goodwill"),
    "employees": (None, None, None),        # profile.json about.employees.count
}


class FactsRefusal(Exception):
    """A facts.json declaration make_score refuses (the message is the 02 §8.2 text, without make_score's prefix)."""


def canonical_sha256(doc):
    """facts_sha256 (02 §8.3): sha256 of the canonical JSON (sort_keys, compact, raw UTF-8) — reformatting facts.json
    does not change it."""
    return hashlib.sha256(json.dumps(doc, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=False).encode("utf-8")).hexdigest()


def _isnum(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and _math.isfinite(float(v))


def _values(v):
    """[v] for a number, [low, high] for a range."""
    return list(v) if isinstance(v, list) else [v]


def _value_ok(v):
    if _isnum(v):
        return True
    return (isinstance(v, list) and len(v) == 2 and all(_isnum(x) for x in v) and float(v[0]) <= float(v[1]))


def unit_family(u):
    """money (an ISO code), per_share (<CCY>/share, /ADS), count, fraction (pct / pp / bps) or x."""
    if u in ("pct", "pp", "bps"):
        return "fraction"
    if u in ("count", "x"):
        return u
    if isinstance(u, str) and "/" in u:
        return "per_share"
    return "money"


def value_tolerance(f, ref=0.0):
    """02 §4.3: half a unit of the declared precision at the display scale — money / count / per-share at
    1, 1e3, 1e6, 1e9, 1e12; pct / pp in percent points (0.01); bps at 1e-4; x at 1 — plus 1e-9 relative."""
    unit, p = f.get("unit"), int(f.get("precision") or 0)
    s = 0.01 if unit in ("pct", "pp") else 1e-4 if unit == "bps" else 1.0 if unit == "x" \
        else SCALE_MULT.get(f.get("scale") or "", 1.0)
    return 0.5 * 10 ** (-p) * s + 1e-9 * max(1.0, abs(float(ref or 0.0)))


def _equal(f, declared, other):
    """declared equals other at f's precision, signs agreeing (02 §4.3)."""
    d, o = float(declared), float(other)
    if d != 0 and o != 0 and (d > 0) != (o > 0):
        return False
    return abs(d - o) <= value_tolerance(f, o)


def significant_digits(f, v=None):
    """Significant digits of the value as declared (at its display scale and precision): $1,923,686,000 at scale ""
    has 10, $1.9B at precision 1 has 2."""
    v = abs(float(f.get("value") if v is None else v))
    unit = f.get("unit")
    s = 0.01 if unit in ("pct", "pp") else 1e-4 if unit == "bps" else 1.0 if unit == "x" \
        else SCALE_MULT.get(f.get("scale") or "", 1.0)
    p = int(f.get("precision") or 0)
    digits = f"{v / s:.{p}f}".replace(".", "").lstrip("0")
    return len(digits)


# ---------------------------------------------------------------------------
# Value formatting (02 §7.4)
# ---------------------------------------------------------------------------
CCY_SYMBOL = {"USD": "$", "EUR": "€", "GBP": "£", "JPY": "¥", "CNY": "RMB "}


def _fmt_one(v, unit, scale="", precision=0, unit_label=None):
    p = int(precision or 0)
    v = float(v)
    if unit == "pct":
        return f"{v * 100:.{p}f}%"
    if unit == "pp":
        return f"{v * 100:+.{p}f}pp"
    if unit == "bps":
        return f"{v * 1e4:.{p}f} bps"
    if unit == "x":
        return f"{v:.{p}f}x"
    s = SCALE_MULT.get(scale or "", 1.0)
    body = f"{abs(v) / s:,.{p}f}{scale or ''}"
    neg = "-" if v < 0 else ""
    if unit == "count":
        return f"{neg}{body}" + (f" {unit_label}" if unit_label else "")
    ccy, _, per = str(unit).partition("/")
    sym = CCY_SYMBOL.get(ccy, f"{ccy} ")
    return f"{neg}{sym}{body}" + (f"/{per}" if per else "")


def fmt_value(f, value=None):
    """A fact's value as key_numbers.md prints it: "$1.92B", "$2,191,944,000", "$4.10/share", "126%", "+1.2pp",
    "42 bps", "2.5x", "898 employees", "$3.18B–$3.22B" (scale on both ends)."""
    v = f.get("value") if value is None else value
    args = (f.get("unit"), f.get("scale") or "", f.get("precision") or 0, f.get("unit_label"))
    if isinstance(v, list):
        return "–".join(_fmt_one(x, *args) for x in v)
    return _fmt_one(v, *args) if _isnum(v) else str(v)


def fmt_exact(f, value):
    """A file figure printed in the fact's unit at full precision (no display scale): "$1,923,686,000",
    "52.8246%", "$4.1035/share"."""
    unit = f.get("unit")
    if unit in ("pct", "pp"):
        p = int(f.get("precision") or 0) + 3
    elif unit == "bps" or unit == "x":
        p = int(f.get("precision") or 0) + 2
    elif unit_family(unit) == "per_share":
        p = 4
    else:
        p = 0 if abs(float(value)) >= 1000 else 4
    return _fmt_one(value, unit, "", p, f.get("unit_label"))


def _fmt_tol(f, tol):
    unit = f.get("unit")
    if unit in ("pct", "pp"):
        return f"{tol * 100:.{int(f.get('precision') or 0) + 2}f} points"
    if unit == "bps":
        return f"{tol * 1e4:g} bps"
    return f"{tol:,.6g}"


def quoted(text):
    """07 §1.10's echo convention (make_score.quoted's twin): worker text in curly quotes, its own curly quotes
    straightened — check_quotes never reads a number inside “…”."""
    s = "" if text is None else str(text)
    return "“" + s.replace("“", '"').replace("”", '"') + "”"


# ---------------------------------------------------------------------------
# Validation (02 §3, §8.2)
# ---------------------------------------------------------------------------
def _snippet_unit(unit):
    return unit if unit in ("pct", "pp", "bps", "x") else None


def _source_problem(f, p):
    kind, src = f.get("kind"), f.get("source")
    s = src if isinstance(src, dict) else {}
    if kind == "folder":
        if not (isinstance(s.get("path"), str) and s["path"].strip()):
            return f"{p} (folder): source needs a path — <file>:<selector>, e.g. fundamentals.json:annual[FY2025].buybacks"
        return None
    if kind == "filing":
        form = s.get("form")
        ok = (isinstance(form, str) and (form in FILING_FORMS or re.fullmatch(r"424B\d", form))
              and isinstance(s.get("accession"), str) and ACCESSION_RE.match(s["accession"])
              and isinstance(s.get("section"), str) and s["section"].strip() and _iso(s.get("filed")))
        return None if ok else (f"{p} (filing): source needs form, accession (##########-##-######), section and "
                                "filed (YYYY-MM-DD)")
    if kind == "release":
        ok = (s.get("form") in RELEASE_FORMS and isinstance(s.get("accession"), str) and ACCESSION_RE.match(s["accession"])
              and isinstance(s.get("exhibit"), str) and s["exhibit"].strip() and _iso(s.get("filed")))
        return None if ok else f"{p} (release): source needs form 8-K or 6-K, accession, exhibit and filed"
    ok = (isinstance(s.get("url"), str) and s["url"].startswith("https://") and len(s["url"]) > len("https://")
          and isinstance(s.get("publisher"), str) and s["publisher"].strip() and _iso(s.get("published")))
    return None if ok else f"{p} (third_party): source needs url (https://…), publisher and published (YYYY-MM-DD)"


def _calc_shape_problem(f, p):
    c = f.get("calc")
    if not isinstance(c, dict):
        return f"{p}: calc must be an object {{op, of, years?}}"
    op, of = c.get("op"), c.get("of")
    if op not in CALC_OPS:
        return f"{p}: calc op must be one of {', '.join(CALC_OPS)} (got {op!r})"
    if not (isinstance(of, list) and 1 <= len(of) <= CALC_MAX_OPERANDS and all(isinstance(o, str) and o.strip() for o in of)):
        return f"{p}: calc of must list 1–{CALC_MAX_OPERANDS} operands (fact ids or folder paths)"
    need = {"growth": (2,), "ratio": (2,), "diff": (2,), "cagr": (2,), "mid": (1, 2), "sum": tuple(range(2, 7))}[op]
    if len(of) not in need:
        return f"{p}: calc {op} takes {' or '.join(str(x) for x in need[:2])}{'+' if op == 'sum' else ''} operands (got {len(of)})"
    if op == "cagr":
        y = c.get("years")
        if not (isinstance(y, int) and not isinstance(y, bool) and 1 <= y <= 30):
            return f"{p}: calc cagr needs years, an integer 1–30"
    if isinstance(f.get("value"), list):
        return f"{p}: a calc fact's value is one number (the computed result)"
    return None


def fact_problem(f):
    """The first schema problem of one fact object (02 §8.2 texts), else None."""
    fid = f["id"]
    p = f"facts.json {fid}"
    kind = f.get("kind")
    if kind not in KINDS:
        return f"{p}: kind must be one of {', '.join(KINDS)} (got {kind!r})"
    if f.get("type") not in TYPES:
        return f"{p}: type must be one of {', '.join(TYPES)}"
    lab = f.get("label")
    if not (isinstance(lab, str) and LABEL_LEN[0] <= len(lab.strip()) <= LABEL_LEN[1]):
        return f"{p}: label must be {LABEL_LEN[0]}–{LABEL_LEN[1]} characters (what the number is)"
    if not _value_ok(f.get("value")):
        return f"{p}: value must be a number or a [low, high] pair of numbers (low ≤ high)"
    unit = f.get("unit")
    if not (isinstance(unit, str) and UNIT_RE.match(unit)):
        return f"{p}: unit must be an ISO currency code, '<CCY>/share', 'pct', 'pp', 'bps', 'x' or 'count' (got {unit!r})"
    if "unit_label" in f and not (isinstance(f["unit_label"], str) and 0 < len(f["unit_label"]) <= 30):
        return f"{p}: unit_label must be a short noun (stores, MW) — display only"
    if f.get("scale", "") not in SCALES:
        return f'{p}: scale must be one of "", K, M, B, T'
    prec = f.get("precision")
    if not (isinstance(prec, int) and not isinstance(prec, bool) and 0 <= prec <= 6):
        return f"{p}: precision must be an integer 0–6"
    per = f.get("period")
    if not (isinstance(per, str) and PERIOD_RE.match(per)) or (per[:4].isdigit() and not _iso(per)) \
            or (per.startswith("TTM ") and not _iso(per[4:])):
        return (f"{p}: period {per!r} is not recognised — use FY2025, Q2 FY2026, H1 FY2026, 9M FY2026, TTM 2026-06-30, "
                "CY2026 or a YYYY-MM-DD instant")
    m = f.get("metric")
    if m is not None and not (isinstance(m, str) and METRIC_RE.match(m)):
        return f"{p}: metric must be a snake_case series name ([a-z][a-z0-9_], 2–41 characters)"
    uf = f.get("used_for")
    if not (isinstance(uf, list) and uf):
        return f"{p}: used_for must be a non-empty list (context, scenarios, guidance_check, flag_resolution, a reason tag or moat:<pillar>)"
    for tag in uf:
        why = used_for_problem(tag)
        if why:
            return f"{p}: {why}"
        if kind == "third_party" and tag in THIRD_PARTY_NOT_SOLE_SUPPORT:
            return (f"{p}: used_for {tag} is not allowed for a third_party fact — third-party facts calibrate scenarios "
                    "and give context only (R3)")
    if "calc" in f:
        return _calc_shape_problem(f, p)
    why = _source_problem(f, p)
    if why:
        return why
    if kind == "folder":
        if isinstance(f.get("value"), list):
            return f"{p} (folder): a [low, high] range cannot be a folder fact — a folder file holds one figure"
        return None
    sn = f.get("snippet")
    if not (isinstance(sn, str) and sn.strip()):
        return f"{p}: a {kind} fact needs a snippet — the source's own words, under 25 words, containing the number"
    w = _qt.snippet_words(sn)
    if w > _qt.SNIPPET_MAX_WORDS:
        return f"{p}: snippet has {w} words — keep it under 25 (R3)"
    ps = kind in ("filing", "release")          # 07 §1.7: a filing table snippet prints in thousands / millions
    for v in _values(f["value"]):
        if not _qt.snippet_shows_value(sn, v, unit=_snippet_unit(unit), presentation_scale=ps):
            return f"{p}: snippet does not contain the declared value {fmt_value(f)} at the snippet's own precision"
    return None


def validate(doc, ticker):
    """None when facts.json document doc is well-formed for folder ticker, else the first refusal text (02 §8.2)."""
    if not isinstance(doc, dict):
        return "facts.json: must be a JSON object {schema, ticker, facts}"
    if doc.get("schema") != SCHEMA or isinstance(doc.get("schema"), bool):
        return "facts.json: schema must be 1"
    t = str(ticker).upper()
    if doc.get("ticker") != t:
        return f"facts.json: ticker {doc.get('ticker')} is not this folder's {t}"
    facts = doc.get("facts")
    if not (isinstance(facts, list) and all(isinstance(f, dict) for f in facts)):
        return 'facts.json: "facts" must be a list of objects'
    seen = set()
    for i, f in enumerate(facts, 1):
        fid = f.get("id")
        if fid is None or fid == "":
            return f"facts.json: fact #{i} has no id"
        if not (isinstance(fid, str) and ID_RE.match(fid)):
            return f"facts.json: id {fid} is not of the form F<n>"
        if fid in seen:
            return f"facts.json: duplicate fact id {fid}"
        seen.add(fid)
    for f in facts:
        why = fact_problem(f)
        if why:
            return why
    nq = doc.get("not_quantities")
    if nq is not None:
        if not (isinstance(nq, list) and len(nq) <= NOT_QUANTITIES_MAX and all(
                isinstance(e, dict) and isinstance(e.get("text"), str) and isinstance(e.get("reason"), str)
                and e["reason"].strip() for e in nq)):
            return f"facts.json: not_quantities must be a list of at most {NOT_QUANTITIES_MAX} {{text, reason}} entries"
        for e in nq:
            t_ = e["text"]
            if not (NOT_QUANTITY_LEN[0] <= len(t_) <= NOT_QUANTITY_LEN[1] and re.search(r"\d", t_)):
                return (f"facts.json: not_quantities entry '{t_}' must be {NOT_QUANTITY_LEN[0]}–{NOT_QUANTITY_LEN[1]} "
                        "characters and contain a digit")
            hits = [k for k in _qt.tokenize(t_) if k.kind in ("money", "pct", "pp", "bps", "mult")]
            if hits:
                return f"facts.json: not_quantities entry '{t_}' is a quantity ({hits[0].kind}) — declare it as a fact or reword it"
    return None


# ---------------------------------------------------------------------------
# The folder path grammar (02 §4.1; rebase A9, D1-D2)
# ---------------------------------------------------------------------------
class PathError(ValueError):
    """A folder path that does not resolve; status unresolved / file_missing / period_moved (02 §4.7)."""

    def __init__(self, why, status="unresolved"):
        super().__init__(why)
        self.why, self.status = why, status


class Resolved:
    """A resolved folder figure: value, unit (the file's currency, <ccy>/share, pct, count or x), period_end, filed
    (that period's filed date when the folder files know it), file, path."""
    __slots__ = ("value", "unit", "period_end", "filed", "file", "path")

    def __init__(self, **kw):
        for k in self.__slots__:
            setattr(self, k, kw.get(k))


class Folder:
    """The folder files of one company, parsed once (read only)."""

    def __init__(self, path):
        self.path = path
        self._json, self._rows, self._cal = {}, None, None

    def json(self, name):
        """The parsed file; None when it does not exist, False when it is unreadable."""
        if name not in self._json:
            p = os.path.join(self.path, name)
            if not os.path.exists(p):
                self._json[name] = None
            else:
                try:
                    with open(p, encoding="utf-8") as fh:
                        self._json[name] = json.load(fh)
                except (OSError, ValueError):
                    self._json[name] = False
        return self._json[name]

    def rows(self):
        """financials_history.csv rows (oldest first), None when the file does not exist."""
        if self._rows is None:
            p = os.path.join(self.path, "financials_history.csv")
            if not os.path.exists(p):
                return None
            try:
                with open(p, encoding="utf-8", newline="") as fh:
                    self._rows = sorted((r for r in _csv.DictReader(fh) if r.get("period_end")),
                                        key=lambda r: r["period_end"])
            except (OSError, ValueError, _csv.Error):
                self._rows = []
        return self._rows

    def calendar(self):
        if self._cal is None:
            self._cal = fiscal_calendar(self.path)
        return self._cal


def _num_s(s):
    if _isnum(s):
        return float(s)
    try:
        v = float(s) if isinstance(s, str) and s.strip() else None
    except ValueError:
        return None
    return v if v is not None and _math.isfinite(v) else None


def filed_for(fol, period_end):
    """The filed date of a period: statements.json periods.annual / quarterly, else profile.json filings (the
    earliest annual / quarterly report for that period), else None."""
    st = fol.json("statements.json")
    if isinstance(st, dict):
        for key in ("annual", "quarterly"):
            for p in ((st.get("periods") or {}).get(key) or []):
                if isinstance(p, dict) and p.get("end") == period_end and _iso(p.get("filed")):
                    return p["filed"]
    pr = fol.json("profile.json")
    if isinstance(pr, dict):
        cands = [x.get("filed") for x in pr.get("filings") or [] if isinstance(x, dict) and x.get("period") == period_end
                 and x.get("form") in ANNUAL_FILED_FORMS and _iso(x.get("filed"))]
        if cands:
            return min(cands)
    return None


def _fund_unit(field, ccy):
    f = field.lower()
    if f in ("roa", "roe", "roic_proxy") or f.endswith(_FU_PCT_SUFFIX) or f.startswith("payout_ratio") or "yield" in f:
        return "pct"
    if f in ("current_ratio", "debt_to_equity", "net_debt_to_oe", "ads_ratio") or f.endswith("_ratio") or "_to_" in f:
        return "x"
    if f.startswith(("eps", "dps")) or f.endswith("per_share") or f == "price":
        return f"{ccy}/share"
    if f.startswith("shares") or f in ("growth_years", "employees", "quarters"):
        return "count"
    return ccy


def _dcf_unit(path):
    k = path.split(".")[-1].lower()
    if "irr" in k or k.startswith(("upside", "g_", "prob", "share_cagr", "materiality")) or k.endswith(("_pct", "yield")):
        return "pct"
    if "shares" in k:
        return "count"
    if k == "price" or k.startswith(("iv_", "hurdle")) or "per_share" in k:
        return "USD/share"
    return "USD"


def _bad(sel_help):
    return PathError(f"bad selector — {sel_help}")


_PATH_RE = re.compile(r"^(?P<file>[A-Za-z_]+\.(?:json|csv)):(?P<sel>.+)$")
_ST_RE = re.compile(r"(?P<sec>income|balance|cashflow|metrics)\.(?P<key>[A-Za-z0-9_]+)\.(?:(?P<ser>annual|quarterly|"
                    r"growth_annual|growth_quarterly)\[(?P<per>[^\]]+)\]|ttm(?:@(?P<end>\S+))?)")
_FU_RE = re.compile(r"(?:annual\[(?P<ap>[^\]]+)\]\.(?P<af>\w+)|quarterly\[(?P<qp>[^\]]+)\]\.(?P<qf>\w+)|"
                    r"ttm\.(?P<tf>\w+)(?:@(?P<te>\S+))?|dividends\.(?P<df>\w+)|profile\.(?P<pf>\w+))")
_SEG_RE = re.compile(r"tables\[(?P<axis>[^/\]]+)/(?P<concept>[^/\]]+)/(?P<per>[^/\]]+)\]\.(?:rows\[(?P<row>[^\]]+)\]\."
                     r"(?P<ser>values|share_of_total|growth_yoy)|total\.values)\[(?P<p>[^\]]+)\]")
_DOT_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*")


def _leaf(v, what="value"):
    if v is None:
        raise PathError(f"{what} is null")
    if not _isnum(v):
        raise PathError(f"{what} is not a number")
    return float(v)


def resolve(path, fol, calc_operand=False):
    """Resolve a folder path `<file>:<selector>` against Folder fol -> Resolved; raises PathError (02 §4.1)."""
    m = _PATH_RE.match(path.strip()) if isinstance(path, str) else None
    if not m:
        raise PathError("unknown file — a folder path is <file>:<selector>")
    fname, sel = m.group("file"), m.group("sel").strip()
    if fname in CALC_ONLY_FILES and not calc_operand:
        raise PathError(f"{fname} figures are quotable directly — a path into it is allowed only as a calc operand")
    if fname not in FOLDER_FILES + CALC_ONLY_FILES:
        raise PathError(f"unknown file {fname} (one of {', '.join(FOLDER_FILES)})")
    if re.search(r"\[\s*[-+]?\d+\s*\]", sel):
        raise _bad("integer indexes are not accepted (they shift when a year is added); select by period label or end date")
    if fname == "financials_history.csv":
        return _res_csv(fol, sel, path)
    doc = fol.json(fname)
    if doc is None:
        raise PathError(f"{fname} is not in the folder", "file_missing")
    if not isinstance(doc, dict):
        raise PathError(f"{fname} is not readable JSON", "file_missing")
    if fname == "statements.json":
        return _res_statements(doc, sel, fol, path)
    if fname == "fundamentals.json":
        return _res_fundamentals(doc, sel, fol, path)
    if fname == "segments.json":
        return _res_segments(doc, sel, fol, path)
    if not _DOT_RE.fullmatch(sel):
        raise _bad(f"{fname}:<dotted.path> (keys only)")
    cur = doc
    for k in sel.split("."):
        if not isinstance(cur, dict) or k not in cur:
            raise PathError(f"{k} is not in {fname} (at {sel})")
        cur = cur[k]
    v = _leaf(cur)
    if fname == "profile.json":
        emp = ((doc.get("about") or {}).get("employees") or {}) if isinstance(doc.get("about"), dict) else {}
        pe = emp.get("as_of") if sel.startswith("about.employees") and _iso(emp.get("as_of")) else str(doc.get("as_of") or "")[:10]
        return Resolved(value=v, unit="count", period_end=_iso(pe), filed=None, file=fname, path=path)
    if fname == "ttm.json":
        k = sel.split(".")[-1]
        unit = "USD/share" if "per_share" in k else "count" if "shares" in sel else "USD"
        pe = doc.get("ytd_end")
        return Resolved(value=v, unit=unit, period_end=_iso(pe), filed=filed_for(fol, pe), file=fname, path=path)
    pe = str(doc.get("as_of") or "")[:10]
    return Resolved(value=v, unit=_dcf_unit(sel), period_end=_iso(pe), filed=None, file=fname, path=path)


def _res_csv(fol, sel, path):
    rows = fol.rows()
    if rows is None:
        raise PathError("financials_history.csv is not in the folder", "file_missing")
    m = re.fullmatch(r"([a-z][a-z0-9_]*)\[([^\]]+)\]", sel)
    if not m:
        raise _bad("financials_history.csv:<column>[<FY label or period end>]")
    col, per = m.group(1), m.group(2).strip()
    fy = per[2:] if re.fullmatch(r"FY\d{4}", per) else None
    row = next((r for r in rows if (fy and str(r.get("fy_label") or "").strip() == fy) or r.get("period_end") == per), None)
    if row is None:
        raise PathError(f"period {per} not in financials_history.csv")
    if col not in row:
        raise PathError(f"column {col} not in financials_history.csv")
    raw = row.get(col)
    v = _num_s(raw)
    if v is None:
        raise PathError("value is null" if raw in (None, "") else "value is not a number")
    unit = "count" if col.startswith("shares") else ("USD/share" if col.endswith("per_share") else "USD")
    pe = row["period_end"]
    return Resolved(value=v, unit=unit, period_end=pe, filed=filed_for(fol, pe), file="financials_history.csv", path=path)


def _period_index(plist, per):
    for i, p in enumerate(plist):
        if isinstance(p, dict) and (p.get("label") == per or p.get("end") == per):
            return i
    return None


def _res_statements(doc, sel, fol, path):
    m = _ST_RE.fullmatch(sel)
    if not m:
        raise _bad("statements.json:<section>.<row key>.<annual|quarterly|growth_annual|growth_quarterly>[<period>] "
                   "or <section>.<row key>.ttm@<end>")
    rows = (doc.get("statements") or {}).get(m.group("sec")) or []
    row = next((r for r in rows if isinstance(r, dict) and r.get("key") == m.group("key")), None)
    if row is None:
        raise PathError(f"row {m.group('sec')}.{m.group('key')} is not in statements.json")
    ccy = doc.get("currency") or "USD"
    unit = {"money": ccy, "per_share": f"{ccy}/share", "shares": "count", "pct": "pct", "ratio": "x"}.get(row.get("unit"), ccy)
    periods = doc.get("periods") or {}
    if m.group("ser"):
        ser, per = m.group("ser"), m.group("per").strip()
        plist = periods.get("annual" if "annual" in ser else "quarterly") or []
        i = _period_index(plist, per)
        if i is None:
            raise PathError(f"period {per} is not in statements.json")
        series = row.get(ser)
        v = _leaf(series[i] if isinstance(series, list) and i < len(series) else None)
        if ser.startswith("growth"):
            unit = "pct"
        return Resolved(value=v, unit=unit, period_end=plist[i].get("end"),
                        filed=plist[i].get("filed") if _iso(plist[i].get("filed")) else filed_for(fol, plist[i].get("end")),
                        file="statements.json", path=path)
    end = m.group("end")
    if not end or not _iso(end):
        raise _bad("a ttm selector must carry @<end> (the TTM's end date, YYYY-MM-DD)")
    now = (periods.get("ttm") or {}).get("end")
    if now != end:
        raise PathError(f"TTM in statements.json now ends {now}", "period_moved")
    return Resolved(value=_leaf(row.get("ttm")), unit=unit, period_end=end, filed=filed_for(fol, end),
                    file="statements.json", path=path)


def _res_fundamentals(doc, sel, fol, path):
    m = _FU_RE.fullmatch(sel)
    if not m:
        raise _bad("fundamentals.json:annual[<FY|end>].<field>, quarterly[<label|end>].<field>, ttm.<field>@<end>, "
                   "dividends.<field> or profile.<field>")
    ccy = doc.get("currency") or "USD"
    if m.group("ap"):
        per, field = m.group("ap").strip(), m.group("af")
        fy = per[2:] if re.fullmatch(r"FY\d{4}", per) else None
        row = next((r for r in doc.get("annual") or [] if isinstance(r, dict)
                    and ((fy and str(r.get("fy")) == fy) or r.get("period_end") == per)), None)
        if row is None:
            raise PathError(f"period {per} is not in fundamentals.json annual")
    elif m.group("qp"):
        per, field = m.group("qp").strip(), m.group("qf")
        row = next((r for r in doc.get("quarterly") or [] if isinstance(r, dict)
                    and (r.get("label") == per or r.get("period_end") == per)), None)
        if row is None:
            raise PathError(f"period {per} is not in fundamentals.json quarterly")
    elif m.group("tf"):
        field, end = m.group("tf"), m.group("te")
        if not end or not _iso(end):
            raise _bad("a ttm selector must carry @<end> (the TTM's end date, YYYY-MM-DD)")
        row = doc.get("ttm") if isinstance(doc.get("ttm"), dict) else {}
        if row.get("period_end") != end:
            raise PathError(f"TTM in fundamentals.json now ends {row.get('period_end')}", "period_moved")
    else:
        key = "dividends" if m.group("df") else "profile"
        field = m.group("df") or m.group("pf")
        row = doc.get(key) if isinstance(doc.get(key), dict) else {}
        if field not in row:
            raise PathError(f"{key}.{field} is not in fundamentals.json")
        pe = row.get("ttm_period_end") if key == "dividends" else None
        return Resolved(value=_leaf(row.get(field)), unit=_fund_unit(field, ccy), period_end=_iso(pe),
                        filed=None, file="fundamentals.json", path=path)
    if field not in row:
        raise PathError(f"field {field} is not in that fundamentals.json row")
    pe = row.get("period_end")
    return Resolved(value=_leaf(row.get(field)), unit=_fund_unit(field, ccy), period_end=pe,
                    filed=filed_for(fol, pe), file="fundamentals.json", path=path)


def _res_segments(doc, sel, fol, path):
    m = _SEG_RE.fullmatch(sel)
    if not m:
        raise _bad("segments.json:tables[<axis>/<concept>/<periodicity>].rows[<member|label>]."
                   "<values|share_of_total|growth_yoy>[<period>] or tables[...].total.values[<period>]")
    tab = next((t for t in doc.get("tables") or [] if isinstance(t, dict) and t.get("axis") == m.group("axis")
                and t.get("concept") == m.group("concept") and t.get("periodicity") == m.group("per")), None)
    if tab is None:
        raise PathError(f"table {m.group('axis')}/{m.group('concept')}/{m.group('per')} is not in segments.json")
    per = m.group("p").strip()
    labels, ends = tab.get("period_labels") or [], tab.get("periods") or []
    i = labels.index(per) if per in labels else (ends.index(per) if per in ends else None)
    if i is None:
        raise PathError(f"period {per} is not in that segments.json table")
    ccy = doc.get("currency") or "USD"
    if m.group("row"):
        rk = m.group("row").strip()
        row = next((r for r in tab.get("rows") or [] if isinstance(r, dict) and rk in (r.get("member"), r.get("label"))), None)
        if row is None:
            raise PathError(f"row {rk} is not in that segments.json table")
        ser = row.get(m.group("ser"))
        unit = ccy if m.group("ser") == "values" else "pct"
    else:
        ser = (tab.get("total") or {}).get("values")
        unit = ccy
    v = _leaf(ser[i] if isinstance(ser, list) and i < len(ser) else None)
    pe = ends[i] if i < len(ends) else None
    return Resolved(value=v, unit=unit, period_end=pe, filed=filed_for(fol, pe), file="segments.json", path=path)


# ---------------------------------------------------------------------------
# Same-period folder leaves (02 §4.5 duplicate detection)
# ---------------------------------------------------------------------------
def _fy_of(period):
    return period[2:] if re.fullmatch(r"FY\d{4}", period or "") else None


def canonical_paths(metric, period, pe):
    """The folder paths of a canonical metric for one period (02 §4.5 detector 1), most authoritative first."""
    spec = CANONICAL_METRICS.get(metric)
    if spec is None:
        return []
    col, key, fld = spec
    if metric == "employees":
        return ["profile.json:about.employees.count"]
    out = []
    if period.startswith("FY"):
        if col:
            out.append(f"financials_history.csv:{col}[{period}]")
        out += [f"statements.json:{sec}.{key}.annual[{period}]" for sec in ("income", "cashflow", "balance", "metrics")] if key else []
        out += [f"fundamentals.json:annual[{period}].{fld}"] if fld else []
    elif re.match(r"Q[1-4] FY", period):
        out += [f"statements.json:{sec}.{key}.quarterly[{period}]" for sec in ("income", "cashflow", "balance", "metrics")] if key else []
        out += [f"fundamentals.json:quarterly[{period}].{fld}"] if fld else []
    elif period.startswith("TTM ") and pe:
        out += [f"statements.json:{sec}.{key}.ttm@{pe}" for sec in ("income", "cashflow", "balance", "metrics")] if key else []
        out += [f"fundamentals.json:ttm.{fld}@{pe}"] if fld else []
    elif _iso(period):
        if col:
            out.append(f"financials_history.csv:{col}[{period}]")
        out += [f"statements.json:{sec}.{key}.{s}[{period}]" for s in ("annual", "quarterly")
                for sec in ("income", "cashflow", "balance", "metrics")] if key else []
        out += [f"fundamentals.json:{s}[{period}].{fld}" for s in ("annual", "quarterly")] if fld else []
    return out


def period_leaves(fol, period, pe):
    """[(path, value, unit)] — every numeric folder-file leaf that carries the fact's period (02 §4.5 detector 2):
    statements series by period label / end, fundamentals rows by period_end, segments by period label / end, the
    CSV row of that FY / period end."""
    out = []
    is_fy, is_q, is_ttm = period.startswith("FY"), bool(re.match(r"(?:Q[1-4]|H[12]|9M) FY", period)), period.startswith("TTM ")
    inst = _iso(period)
    st = fol.json("statements.json")
    if isinstance(st, dict):
        ccy = st.get("currency") or "USD"
        periods = st.get("periods") or {}
        idx = []
        for key, ser in (("annual", "annual"), ("quarterly", "quarterly")):
            for i, p in enumerate(periods.get(key) or []):
                if not isinstance(p, dict):
                    continue
                if (p.get("label") == period and ((is_fy and key == "annual") or (is_q and key == "quarterly"))) \
                        or (inst and p.get("end") == inst):
                    idx.append((ser, i, p.get("label") or p.get("end")))
        ttm_ok = is_ttm and (periods.get("ttm") or {}).get("end") == period[4:]
        for sec, rows in (st.get("statements") or {}).items():
            for r in rows if isinstance(rows, list) else []:
                if not isinstance(r, dict):
                    continue
                unit = {"money": ccy, "per_share": f"{ccy}/share", "shares": "count", "pct": "pct",
                        "ratio": "x"}.get(r.get("unit"), ccy)
                for ser, i, lab in idx:
                    for s2, u2 in ((ser, unit), (f"growth_{ser}", "pct")):
                        vals = r.get(s2)
                        if isinstance(vals, list) and i < len(vals) and _isnum(vals[i]):
                            out.append((f"statements.json:{sec}.{r.get('key')}.{s2}[{lab}]", float(vals[i]), u2))
                if ttm_ok and _isnum(r.get("ttm")):
                    out.append((f"statements.json:{sec}.{r.get('key')}.ttm@{period[4:]}", float(r["ttm"]), unit))
    fu = fol.json("fundamentals.json")
    if isinstance(fu, dict) and pe:
        ccy = fu.get("currency") or "USD"
        groups = []
        if is_fy or inst:
            groups += [("annual", r) for r in fu.get("annual") or [] if isinstance(r, dict) and r.get("period_end") == (inst or pe)]
        if is_q or inst:
            groups += [("quarterly", r) for r in fu.get("quarterly") or [] if isinstance(r, dict) and r.get("period_end") == (inst or pe)]
        if is_ttm and isinstance(fu.get("ttm"), dict) and fu["ttm"].get("period_end") == period[4:]:
            groups.append(("ttm", fu["ttm"]))
        for g, r in groups:
            for k, v in r.items():
                if _isnum(v):
                    sel = (f"annual[FY{r.get('fy')}].{k}" if g == "annual" else
                           f"quarterly[{r.get('label') or r.get('period_end')}].{k}" if g == "quarterly" else f"ttm.{k}@{period[4:]}")
                    out.append((f"fundamentals.json:{sel}", float(v), _fund_unit(k, ccy)))
    sg = fol.json("segments.json")
    if isinstance(sg, dict):
        ccy = sg.get("currency") or "USD"
        for t in sg.get("tables") or []:
            if not isinstance(t, dict):
                continue
            labels, ends = t.get("period_labels") or [], t.get("periods") or []
            i = labels.index(period) if period in labels else (ends.index(inst) if inst and inst in ends else None)
            if i is None:
                continue
            tsel = f"tables[{t.get('axis')}/{t.get('concept')}/{t.get('periodicity')}]"
            lab = labels[i] if i < len(labels) else ends[i]
            for r in t.get("rows") or []:
                if not isinstance(r, dict):
                    continue
                for ser, u in (("values", ccy), ("share_of_total", "pct"), ("growth_yoy", "pct")):
                    vals = r.get(ser)
                    if isinstance(vals, list) and i < len(vals) and _isnum(vals[i]):
                        out.append((f"segments.json:{tsel}.rows[{r.get('member') or r.get('label')}].{ser}[{lab}]",
                                    float(vals[i]), u))
            tv = (t.get("total") or {}).get("values")
            if isinstance(tv, list) and i < len(tv) and _isnum(tv[i]):
                out.append((f"segments.json:{tsel}.total.values[{lab}]", float(tv[i]), ccy))
    rows = fol.rows() or []
    fy = _fy_of(period)
    for r in rows:
        if (fy and str(r.get("fy_label") or "").strip() == fy) or (inst and r.get("period_end") == inst):
            for k, raw in r.items():
                v = _num_s(raw)
                if v is not None and k not in ("period_end", "fy_label"):
                    unit = "count" if k.startswith("shares") else ("USD/share" if k.endswith("per_share") else "USD")
                    out.append((f"financials_history.csv:{k}[FY{r.get('fy_label')}]" if r.get("fy_label")
                                else f"financials_history.csv:{k}[{r['period_end']}]", v, unit))
    return out


# ---------------------------------------------------------------------------
# Staleness (02 §8.4; rebase A8, 07 G7 / 1.20)
# ---------------------------------------------------------------------------
def latest_filing_used(folder, n, fol=None):
    """{period_end, filed, form, basis}: the latest filing the engine run used. (1) the annual-from-instance record
    (L4, R2b) when applied; (2) the run's latest period P = max(latest_period_end, the TTM's current-YTD end —
    ttm_inputs.ytd_current_period on records that carry it, else ttm.json ytd_end when the base is TTM-pinned);
    (3) P's filed date from statements.json periods, then its latest_filed, then profile.json filings; else the
    period end itself (basis "period_end")."""
    fol = fol or Folder(folder)
    n = n if isinstance(n, dict) else {}
    afi = n.get("annual_from_instance")
    if isinstance(afi, dict) and afi.get("applied") and _iso(afi.get("filed")):
        return {"period_end": _iso(afi.get("period")) or n.get("latest_period_end"), "filed": afi["filed"],
                "form": afi.get("form"), "basis": "annual_from_instance"}
    p = _iso(n.get("latest_period_end"))
    ti = n.get("ttm_inputs")
    if isinstance(ti, dict):
        ycp = ti.get("ytd_current_period")
        if isinstance(ycp, list) and len(ycp) == 2 and _iso(ycp[1]):
            p = max(p, ycp[1]) if p else ycp[1]
    elif "ttm_inputs" not in n:
        inp = n.get("inputs") or {}
        if inp.get("base_pin_source") == "ttm_json" or "ttm" in str(n.get("base_source") or "").lower():
            tt = fol.json("ttm.json")
            ye = _iso(tt.get("ytd_end")) if isinstance(tt, dict) else None
            if ye:
                p = max(p, ye) if p else ye
    if not p:
        return {"period_end": None, "filed": None, "form": None, "basis": "unknown"}
    st = fol.json("statements.json")
    if isinstance(st, dict):
        for key, form in (("quarterly", None), ("annual", None)):
            for q in ((st.get("periods") or {}).get(key) or []):
                if isinstance(q, dict) and q.get("end") == p and _iso(q.get("filed")):
                    lf = st.get("latest_filed") if isinstance(st.get("latest_filed"), dict) else {}
                    return {"period_end": p, "filed": q["filed"],
                            "form": lf.get("form") if lf.get("period") == p else form, "basis": "statements.json"}
        lf = st.get("latest_filed")
        if isinstance(lf, dict) and lf.get("period") == p and _iso(lf.get("filed")):
            return {"period_end": p, "filed": lf["filed"], "form": lf.get("form"), "basis": "statements.json latest_filed"}
    pr = fol.json("profile.json")
    if isinstance(pr, dict):
        cands = sorted((x.get("filed"), x.get("form")) for x in pr.get("filings") or [] if isinstance(x, dict)
                       and x.get("period") == p and x.get("form") in ANNUAL_FILED_FORMS and _iso(x.get("filed")))
        if cands:
            return {"period_end": p, "filed": cands[0][0], "form": cands[0][1], "basis": "profile.json"}
    return {"period_end": p, "filed": None, "form": None, "basis": "period_end"}


# ---------------------------------------------------------------------------
# The check make_score runs (02 §4, §4.7): validation, verification, calc, duplicates, staleness
# ---------------------------------------------------------------------------
class FactsCheck:
    """The verified declaration — what make_score stamps (summary), renders (key_numbers_lines) and traces against
    (values, kinds). authoring: facts.json is new or edited since the prior score (any non-verified status refused);
    otherwise a rebuild (drift recorded)."""

    def __init__(self, doc, folder, ticker):
        self.doc, self.folder, self.ticker = doc, folder, ticker
        self.sha = canonical_sha256(doc)
        self.facts = [f for f in doc.get("facts") or []]
        self.by_id = by_id(doc)
        self.values, self.status, self.as_of, self.paths_shown = {}, {}, {}, {}
        self.drift, self.stale, self.counterparts, self.possible_dups = [], [], [], []
        self.latest = None
        self.influence = {}
        self.authoring = True

    def not_quantities(self):
        return [e["text"] for e in self.doc.get("not_quantities") or [] if isinstance(e, dict) and isinstance(e.get("text"), str)]

    def worker_strings(self):
        """Every worker-authored string the declaration carries (labels, snippets, sections, publishers, reasons) —
        blanked wherever key_numbers.md echoes them."""
        out = []
        for f in self.facts:
            for k in ("label", "snippet"):
                if isinstance(f.get(k), str):
                    out.append(f[k])
            src = f.get("source") if isinstance(f.get("source"), dict) else {}
            for k in ("section", "publisher", "exhibit"):
                if isinstance(src.get(k), str):
                    out.append(src[k])
        out += [e.get("reason") for e in self.doc.get("not_quantities") or [] if isinstance(e, dict)
                and isinstance(e.get("reason"), str)]
        return out

    def value_set(self, ids=None):
        vs = _qt.ValueSet()
        for fid, vals in self.values.items():
            if ids is None or fid in ids:
                for v in vals:
                    vs.add(v)
        return vs

    def cited_records(self, ids):
        """The registry's `facts` citation list (02 §5): [{id, kind, value, unit, period, source}] for cited ids."""
        out = []
        for fid in ids:
            f = self.by_id.get(fid)
            if f is None:
                continue
            out.append({"id": fid, "kind": f.get("kind"), "value": f.get("value"), "unit": f.get("unit"),
                        "period": f.get("period"),
                        "source": f.get("source") if "calc" not in f else {"calc": f.get("calc")}})
        return out

    def summary(self):
        """score.json declared_facts (02 §8.3)."""
        by_kind = {k: 0 for k in KINDS}
        by_type = {t: 0 for t in TYPES}
        for f in self.facts:
            by_kind[f.get("kind")] = by_kind.get(f.get("kind"), 0) + 1
            by_type[f.get("type")] = by_type.get(f.get("type"), 0) + 1
        return {"schema": SCHEMA, "facts_sha256": self.sha, "count": len(self.facts), "by_kind": by_kind,
                "by_type": by_type,
                "facts": [{"id": f["id"], "kind": f.get("kind"), "type": f.get("type"), "metric": f.get("metric"),
                           "period": f.get("period"), "as_of": self.as_of.get(f["id"]),
                           "status": self.status.get(f["id"], "declared")} for f in self.facts],
                "verified": [f["id"] for f in self.facts if self.status.get(f["id"]) == "verified"],
                "drift": list(self.drift), "stale": list(self.stale),
                "folder_counterparts": list(self.counterparts),
                "possible_folder_duplicates": list(self.possible_dups),
                "latest_filing_used": self.latest,
                "influence": dict(self.influence)}


def _weakest(kinds):
    r = min(KIND_RANK[k] for k in kinds)
    return r, {0: "third_party", 1: "filing or release", 2: "folder"}[r]


def check(doc, folder, ticker, n=None, prior_sha=None):
    """Validate, verify and annotate facts.json document doc for folder (02 §4) -> FactsCheck; raises FactsRefusal.
    prior_sha: the prior score.json's declared_facts.facts_sha256 — equal to this document's means a rebuild (the
    declaration is unchanged and only folder files moved): mismatches are recorded as drift, never refused."""
    why = validate(doc, ticker)
    if why:
        raise FactsRefusal(why)
    fc = FactsCheck(doc, folder, ticker)
    fc.authoring = prior_sha != fc.sha
    fol = Folder(folder)
    if isinstance(n, dict):
        fol._json["dcf_numbers.json"] = n          # a calc operand into dcf_numbers.json reads this run's record
    cal = fol.calendar()
    lpe = (n or {}).get("latest_period_end") if isinstance(n, dict) else None

    def refuse_or_drift(fid, msg, status, path, declared, file_value):
        if fc.authoring:
            raise FactsRefusal(msg)
        fc.drift.append({"id": fid, "status": status, "path": path, "declared": declared, "file_value": file_value})
        fc.status[fid] = "drifted"

    # 1. folder facts: resolve, unit, value (02 §4.1-§4.3)
    for f in fc.facts:
        fid = f["id"]
        if f.get("kind") != "folder" or "calc" in f:
            continue
        path = f["source"]["path"].strip()
        fc.values[fid] = [float(f["value"])]
        fc.paths_shown[fid] = path
        try:
            r = resolve(path, fol)
        except PathError as e:
            refuse_or_drift(fid, f"facts.json {fid} (folder): path {path} does not resolve — {e.why}", e.status, path,
                            f["value"], None)
            continue
        fc.as_of[fid] = r.filed or r.period_end
        if f["unit"] != r.unit:
            refuse_or_drift(fid, f"facts.json {fid} (folder): unit {f['unit']} does not match {r.file}'s {r.unit}",
                            "mismatch", path, f["value"], r.value)
            continue
        if not _equal(f, f["value"], r.value):
            refuse_or_drift(fid, f"facts.json {fid} (folder): value {fmt_value(f)} does not equal {path} = "
                                 f"{fmt_exact(f, r.value)} at the declared precision "
                                 f"(± {_fmt_tol(f, value_tolerance(f, r.value))})",
                            "mismatch", path, f["value"], r.value)
            continue
        fc.status[fid] = "verified"
    # 2. non-folder, non-calc facts: the date is the source's (02 §3 "every fact carries a date")
    for f in fc.facts:
        if f.get("kind") != "folder" and "calc" not in f:
            fc.values[f["id"]] = [float(x) for x in _values(f["value"])]
            src = f["source"]
            fc.as_of[f["id"]] = src.get("published") if f["kind"] == "third_party" else src.get("filed")
            fc.status[f["id"]] = "declared"
    # 3. calc facts (02 §4.6): operands are fact ids or paths (dcf_numbers.json / ttm.json too); no cycles
    done = {}

    def calc_value(fid, stack):
        if fid in done:
            return done[fid]
        if fid in stack:
            raise FactsRefusal(f"facts.json {fid}: calc operands form a cycle ({' → '.join(stack + [fid])})")
        f = fc.by_id[fid]
        c = f["calc"]
        ops, kinds, dates, units = [], [], [], []
        for o in c["of"]:
            o = o.strip()
            if ID_RE.match(o):
                of = fc.by_id.get(o)
                if of is None:
                    raise FactsRefusal(f"facts.json {fid}: calc operand {o} does not resolve — facts.json declares no {o}")
                if "calc" in of:
                    val = calc_value(o, stack + [fid])
                    vals = [val] if val is not None else None
                else:
                    vals = [float(x) for x in _values(of["value"])]
                if vals is None:
                    return None
                ops.append(vals)
                kinds.append(of["kind"])
                dates.append(fc.as_of.get(o))
                units.append(of["unit"])
            else:
                try:
                    r = resolve(o, fol, calc_operand=True)
                except PathError as e:
                    refuse_or_drift(fid, f"facts.json {fid}: calc operand {o} does not resolve — {e.why}", e.status, o,
                                    f["value"], None)
                    done[fid] = None
                    return None
                ops.append([r.value])
                kinds.append("folder")
                dates.append(r.filed or r.period_end)
                units.append(r.unit)
        op = c["op"]
        rank, name = _weakest(kinds)
        if KIND_RANK[f["kind"]] != rank:
            raise FactsRefusal(f"facts.json {fid}: calc kind must be {name} (its weakest operand)")
        if op in ("growth", "cagr", "diff", "sum", "mid") and len({unit_family(u) for u in units}) > 1:
            raise FactsRefusal(f"facts.json {fid}: calc {op} operands must share a unit family (got {', '.join(units)})")
        if any(len(v) != 1 for v in ops) and not (op == "mid" and len(ops) == 1 and len(ops[0]) == 2):
            raise FactsRefusal(f"facts.json {fid}: calc {op} takes single numbers (a [low, high] range only as the one "
                               "operand of mid)")
        try:
            if op == "mid":
                a = ops[0] if len(ops) == 1 else [ops[0][0], ops[1][0]]
                val = (a[0] + a[1]) / 2.0
            elif op == "sum":
                val = sum(v[0] for v in ops)
            elif op == "diff":
                val = ops[0][0] - ops[1][0]
            elif op == "ratio":
                val = ops[0][0] / ops[1][0]
            elif op == "growth":
                val = ops[0][0] / ops[1][0] - 1.0
            else:
                q = ops[0][0] / ops[1][0]
                if q <= 0:
                    raise FactsRefusal(f"facts.json {fid}: calc cagr needs operands of the same sign (ratio {q:g})")
                val = q ** (1.0 / int(c["years"])) - 1.0
        except ZeroDivisionError:
            raise FactsRefusal(f"facts.json {fid}: calc {op} divides by zero")
        fc.as_of[fid] = max((d for d in dates if d), default=None)
        if not _equal(f, f["value"], val):
            refuse_or_drift(fid, f"facts.json {fid}: calc {op} does not reproduce: computed {fmt_value(f, val)}, "
                                 f"declared {fmt_value(f)} (± {_fmt_tol(f, value_tolerance(f, val))})",
                            "mismatch", f"calc {op}", f["value"], val)
        elif fc.status.get(fid) != "drifted":
            fc.status[fid] = "verified"
        done[fid] = val
        return val

    for f in fc.facts:
        if "calc" in f:
            v = calc_value(f["id"], [])
            fc.values[f["id"]] = [float(f["value"])] + ([v] if v is not None else [])
    # 4. a filing / release / third-party fact that repeats a folder figure (02 §4.5)
    for f in fc.facts:
        if f.get("kind") == "folder" or "calc" in f or isinstance(f.get("value"), list):
            continue
        fid, kind = f["id"], f["kind"]
        pe = period_end(f, cal, lpe)
        fam = unit_family(f["unit"])
        hit = None
        found = []
        for path in canonical_paths(f.get("metric"), f["period"], pe) if f.get("metric") else []:
            try:
                r = resolve(path, fol)
            except PathError:
                continue
            if unit_family(r.unit) == fam:
                found.append((path, r))
        hit = next(((p_, r.value) for p_, r in found if _equal(f, f["value"], r.value)), None)
        if hit is None and found:
            # the folder's figure for the same metric and period differs (a non-GAAP / adjusted figure, another
            # currency basis): recorded and printed beside the fact — the same unit first (the CSV is USD-converted)
            p_, r = next(((p_, r) for p_, r in found if r.unit == f["unit"]), found[0])
            fc.counterparts.append({"id": fid, "path": p_, "file_value": r.value})
        if hit is None:
            for path, v, u in period_leaves(fol, f["period"], pe):
                if unit_family(u) == fam and _equal(f, f["value"], v):
                    if significant_digits(f) >= DUP_MIN_SIGNIFICANT:
                        hit = (path, v)
                        break
                    if not any(d["id"] == fid and d["path"] == path for d in fc.possible_dups):
                        fc.possible_dups.append({"id": fid, "path": path, "file_value": v})
        if hit:
            msg = (f"facts.json {fid} ({kind}): the value equals {hit[0]} = {fmt_exact(f, hit[1])} for the same period "
                   "— a number available in a folder file must be declared kind \"folder\" with that path (R3)")
            if fc.authoring:
                raise FactsRefusal(msg)
            fc.possible_dups.append({"id": fid, "path": hit[0], "file_value": hit[1]})
    # 5. STALE guidance / estimates (02 §8.4; never a refusal)
    fc.latest = latest_filing_used(folder, n, fol)
    p, filed = fc.latest.get("period_end"), fc.latest.get("filed")
    cutoff = filed or p
    for f in fc.facts:
        if f.get("type") not in GUIDANCE_TYPES:
            continue
        a = fc.as_of.get(f["id"])
        tpe = period_end(f, cal, lpe)
        why = None
        if tpe and p and tpe <= p:          # the more telling of the two when both hold
            why = f"superseded by reported actuals (the period ended {tpe}; the engine used figures through {p})"
        elif a and cutoff and a < cutoff:
            why = (f"older than the {fc.latest.get('form') or 'filing'} filed {filed} the engine used" if filed
                   else f"older than the period ended {p} the engine used")
        if why:
            fc.stale.append({"id": f["id"], "as_of": a, "cutoff": cutoff, "why": why})
    return fc


def load(folder):
    """(doc, None) for <folder>/facts.json, (None, None) when absent, (None, refusal) when it is not valid JSON."""
    p = os.path.join(folder, "facts.json")
    if not os.path.exists(p):
        return None, None
    try:
        with open(p, encoding="utf-8") as fh:
            return json.load(fh), None
    except (OSError, ValueError) as e:
        return None, f"facts.json: not valid JSON ({e})"


# ---------------------------------------------------------------------------
# The influence trace (02 §5; 10 §(l): trace_only / require_anchor)
# ---------------------------------------------------------------------------
class Influence:
    """What influence_support found in one reason: untraced tokens, matched numbers, the facts they matched, whether
    the reason rests only on third-party facts, which cited facts lack the field's tag, and whether it is
    anchored (require_anchor)."""

    def __init__(self):
        self.untraced, self.numbers, self.engine_numbers = [], 0, 0
        self.facts_matched, self.missing_tag, self.unknown = [], [], []
        self.third_party_only, self.anchored, self.carries_number = False, False, False


def influence_support(text, fact_ids, fc, engine, tag, extra=None, trace_only=None, not_quantities=()):
    """02 §5's algorithm over one reason text: (1) cited ids facts.json does not declare (unknown); (2) each number
    must match an engine source (`engine`, a quote_tokens.ValueSet: dcf_numbers / ttm / filed history / saved runs /
    judgment probs), the `extra` values, the `trace_only` values (10 §(l): accepted, never counted as an engine
    match) or a CITED fact's value(s), else it is untraced (a method constant or release number in its context is
    ignored when unmatched); (3) third_party_only = at least one number, none matched an engine source and every
    cited fact that matched is third_party; (4) cited facts whose used_for lacks `tag`; anchored = a number matched
    an engine source (not trace_only), `extra`, or a cited non-third-party fact listing `tag`."""
    res = Influence()
    s = text if isinstance(text, str) else ""
    by = fc.by_id if fc is not None else {}
    ids = list(dict.fromkeys(fact_ids or []))
    res.unknown = [i for i in ids if i not in by]
    cited = [i for i in ids if i in by]
    res.missing_tag = [i for i in cited if tag not in (by[i].get("used_for") or [])]
    sets = {i: fc.value_set([i]) for i in cited} if fc is not None else {}
    res.carries_number = _qt.carries_number(s, not_quantities)
    for t in _qt.numbers(s, not_quantities):
        e = engine.match(t) if engine is not None else False
        x = extra.match(t) if extra is not None else False
        tr = trace_only.match(t) if trace_only is not None else False
        fm = [i for i in cited if sets[i].match(t)]
        if not (e or x or tr or fm):
            if t.release_like or _qt.is_method_constant(t, s):
                continue
            res.untraced.append(t)
            continue
        res.numbers += 1
        if e or x:
            res.engine_numbers += 1
        for i in fm:
            if i not in res.facts_matched:
                res.facts_matched.append(i)
        if e or x or any(by[i].get("kind") != "third_party" and tag in (by[i].get("used_for") or []) for i in fm):
            res.anchored = True
    res.third_party_only = bool(res.numbers and not res.engine_numbers and res.facts_matched
                                and all(by[i].get("kind") == "third_party" for i in res.facts_matched))
    return res


# ---------------------------------------------------------------------------
# key_numbers.md "Declared facts (not engine output)" (02 §7.4; D7: always last)
# ---------------------------------------------------------------------------
DECLARED_HEADING = "## Declared facts (not engine output)"


def _source_text(f, q):
    src = f.get("source") if isinstance(f.get("source"), dict) else {}
    k = f.get("kind")
    if "calc" in f:
        c = f["calc"]
        return f"calc {c.get('op')}({', '.join(c.get('of') or [])})" + (f", {c['years']} years" if c.get("years") else "")
    if k == "folder":
        return f"folder {src.get('path')}"
    if k == "filing":
        return f"filing {src.get('form')} {src.get('accession')} {q(src.get('section'))}, filed {src.get('filed')}"
    if k == "release":
        return f"release {src.get('form')} {src.get('accession')} Ex. {src.get('exhibit')}, filed {src.get('filed')}"
    return f"third-party {q(src.get('publisher'))}, {src.get('published')}"


def key_numbers_lines(fc, quote=None):
    """The last key_numbers.md section — every declared fact with its value as rendered (quotable), its period,
    type, source and status; worker text (labels, snippets, sections, publishers) in “…”."""
    if fc is None:
        return []
    q = quote or quoted
    kinds = {k: 0 for k in KINDS}
    for f in fc.facts:
        kinds[f.get("kind")] = kinds.get(f.get("kind"), 0) + 1
    tally = " · ".join(f"{c} {k.replace('_', '-')}" for k, c in kinds.items() if c)
    nfac = len(fc.facts)
    L = ["", DECLARED_HEADING,
         f"Declared by the worker in facts.json ({nfac} fact{'s' if nfac != 1 else ''}"
         + (f": {tally}" if tally else "") + f"; sha256 {fc.sha[:12]}).",
         "Folder facts were checked by make_score.py against the named file; filing, release and third-party facts "
         "carry the source's own words and are not verified here. Third-party facts calibrate scenarios and give "
         "context only."]
    drift = {d["id"]: d for d in fc.drift}
    stale = {s["id"]: s for s in fc.stale}
    counter = {}
    for c in fc.counterparts:
        counter.setdefault(c["id"], []).append(c)
    dups = {}
    for d in fc.possible_dups:
        dups.setdefault(d["id"], []).append(d)
    for f in fc.facts:
        fid = f["id"]
        typ = f.get("type")
        if f.get("metric"):
            typ += f" (series {f['metric']})"
        line = f"- {fid} · {fmt_value(f)} — {q(f.get('label'))} · {f.get('period')} · {typ} · {_source_text(f, q)}"
        st = fc.status.get(fid)
        if fid in drift:
            d = drift[fid]
            fv = fmt_exact(f, d["file_value"]) if _isnum(d.get("file_value")) else d.get("status")
            line += f" — DRIFTED: {d.get('path')} now reads {fv}"
        elif st == "verified":
            a = fc.as_of.get(fid)
            line += " — verified" + (f" (as filed {a})" if a and f.get("kind") == "folder" else "")
        if f.get("kind") != "folder" or "calc" in f:
            line += f" · used for: {', '.join(f.get('used_for') or [])}"
        if fid in stale:
            line += f" · STALE: {stale[fid]['why']}"
        L.append(line)
        if isinstance(f.get("snippet"), str) and f.get("kind") != "folder" and "calc" not in f:
            L.append(f"  - source words: {q(f['snippet'])}")
        for c in counter.get(fid, []):
            L.append(f"  - folder figure for the same period: {c['path']} = {fmt_exact(f, c['file_value'])}")
        for d in dups.get(fid, []):
            L.append(f"  - possible folder duplicate: {d['path']} = {fmt_exact(f, d['file_value'])}")
    return L
