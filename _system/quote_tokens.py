#!/usr/bin/env python3
"""Number tokens in quoted text — the one place the snippet rule lives (engine 5.7, Andrew's ruling R3; 07 §1.7-§1.8).

SKELETON placed by the scaffold lane L0. The quote lane (L2) ports check_quotes' full tokenizer here (`Token`,
`tokenize`, the strip / ignore rules, `tolerance`) and re-implements snippet_shows_value on it WITHOUT changing its
signature; facts.py, check_quotes.py, interim_bridge.py (L4) and the share-class lane (L8) all call this module, so
there is one definition of "the snippet shows the number". Pure: stdlib only, no I/O.

R3: a non-folder fact (and a declared interim-bridge leg, a share-class count) carries the source's own words, under
25 words (SNIPPET_MAX_WORDS = 24), and the words must contain the number.
"""
import re

SNIPPET_MAX_WORDS = 24   # R3 "under 25 words" (07 §1.7: one constant everywhere)

# Ignore-rule slots (L2 rebase A12) blanked before numbers are read: accounting-standard references (HALO's
# "ASC 805-50"), codification topics and XBRL viewer pages are references, not quantities. L2's port of the full
# ignore rules (02 §6.4) extends IGNORE_PATTERNS; L4's snippet check shares them through snippet_shows_value.
ACCOUNTING_STANDARD_RE = re.compile(r"(?<![A-Za-z])(?:ASC|ASU|SFAS|FAS|IFRS|IAS|IFRIC|SIC-)\s?\d+(?:[-–]\d+)*")
TOPIC_RE = re.compile(r"\bTopic \d{3}\b")
XBRL_VIEWER_PAGE_RE = re.compile(r"\bR\d+\.htm\b")
FORM_NAME_RE = re.compile(r"(?<![A-Za-z0-9])(?:10-K|10-Q|20-F|40-F|6-K|8-K|10-KT)(?:/A)?(?![A-Za-z0-9])")
IGNORE_PATTERNS = (ACCOUNTING_STANDARD_RE, TOPIC_RE, XBRL_VIEWER_PAGE_RE, FORM_NAME_RE)

SCALE_WORDS = {"trillion": 1e12, "tn": 1e12, "t": 1e12, "billion": 1e9, "bn": 1e9, "b": 1e9,
               "million": 1e6, "mn": 1e6, "mm": 1e6, "m": 1e6, "thousand": 1e3, "k": 1e3}
PRESENTATION_SCALES = (3, 6, 9)   # a statement table printed in thousands / millions / billions

# A number with an optional currency mark, parentheses (a cash outflow), sign, thousands separators, decimals, an
# optional scale word and an optional percent / bps / pp unit. Not glued to letters or another number ("FY2026",
# "Q2", "10-K" stay out).
_NUM = re.compile(
    r"(?<![A-Za-z0-9_.,])(?:US\$|C\$|A\$|\$|€|£|¥|(?:USD|EUR|GBP|JPY|CNY|RMB|INR|CAD|AUD|CHF)\s?)?\(?[-−–+]?"
    r"(?P<num>\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?)\)?"
    r"(?:\s?(?P<scale>trillion|billion|million|thousand|tn|bn|mn|mm|T|B|M|K|k|m|b)(?![A-Za-z0-9]))?"
    r"(?:\s?(?P<unit>%|percent(?![A-Za-z])|bps?(?![A-Za-z])|pps?(?![A-Za-z])))?"
    r"(?![A-Za-z0-9_])")


def snippet_words(snippet):
    """The snippet's word count (R3's limit is SNIPPET_MAX_WORDS)."""
    return len(str(snippet or "").split())


def _numbers(snippet):
    """[(number, decimals, scale multiplier or None, unit or None)] in snippet, references blanked first."""
    text = str(snippet or "")
    for pat in IGNORE_PATTERNS:
        text = pat.sub(lambda m: " " * len(m.group(0)), text)
    out = []
    for m in _NUM.finditer(text):
        raw = m.group("num").replace(",", "")
        dec = len(raw.split(".")[1]) if "." in raw else 0
        sc = m.group("scale")
        unit = (m.group("unit") or "").strip().lower() or None
        if unit == "percent":
            unit = "%"
        elif unit in ("bp", "bps"):
            unit = "bps"
        elif unit in ("pp", "pps"):
            unit = "pp"
        out.append((float(raw), dec, SCALE_WORDS[sc.lower()] if sc else None, unit))
    return out


def _close(x, n, dec):
    return abs(x - n) <= 0.5 * 10 ** (-dec) + 1e-9 * max(1.0, abs(n))


def snippet_shows_value(snippet, value, unit=None, presentation_scale=False):
    """True when the snippet carries a number that is `value` at the snippet's own precision (signs ignored:
    outflows print in parentheses). unit "pct" / "pp" (fractions, 0.126 = 12.6%) matches a percent token;
    "bps" (a fraction, 0.0042 = 42 bps) a bps token; any other unit (money, counts, per-share, x) a token with no
    percent unit — "$1.92 billion" proves 1,923,686,000 at 2 decimals. presentation_scale (a statement table "in
    millions": declared interim legs, filing / release facts, share-class counts) lets a bare token (no scale word)
    also match value / 10^k for k in 3, 6, 9 ("Revenue 1,923.7" proves 1,923,686,000; "539" proves 539,000,000 and
    not 538,000,000). A zero matches only a zero."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    v = abs(float(value))
    for n, dec, mult, tok_unit in _numbers(snippet):
        if (n == 0) != (v == 0):
            continue
        if unit in ("pct", "pp"):
            if tok_unit in ("%", "pp") and _close(v * 100.0, n, dec):
                return True
            continue
        if unit == "bps":
            if tok_unit == "bps" and _close(v * 1e4, n, dec):
                return True
            continue
        if tok_unit is not None:
            continue
        if mult is not None:
            if _close(v / mult, n, dec):
                return True
            continue
        if _close(v, n, dec):
            return True
        if presentation_scale and any(_close(v / 10 ** k, n, dec) for k in PRESENTATION_SCALES):
            return True
    return False
