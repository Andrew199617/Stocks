#!/usr/bin/env python3
"""Number tokens in quoted text — the one tokenizer of the R3 quote rule (engine 5.7, Andrew's ruling R3 of
2026-10-19; 02 §6.3-§6.5, 07 §1.7-§1.8). Pure: stdlib only, no I/O.

R3 (strict quoting): every number in a 5.7 run's analysis.md must trace to a generated file; the reasons that
influence a score (tier_override_reason, misfit_notch_reason, a plain base_override, the moat and share-class reasons,
ttm_rejection_reason) must trace too; and a non-folder declared fact carries the source's own words, under 25 words
(SNIPPET_MAX_WORDS = 24), that contain the number. check_quotes.py (the analysis.md gate), facts.py (snippets,
influence) and make_score.py (the reason fields) all read numbers through this module, so "a number", "an ignored
number" and "the quoted precision" have one definition. interim_bridge.py (lane L4) and the share-class lane (L8)
call snippet_shows_value.

What a token is (tokenize):
- A number with an optional approximation mark (~ ≈ < > ≤ ≥ ±), sign (unicode minus / dashes too), currency
  ($, US$, C$, R$, €, £, ¥, ₹, ₩, CHF, ISO codes such as EUR / RMB / BRL ...), thousands separators, decimals, scale
  word (trillion / billion / million / thousand / tn / bn / mn / mm / T / B / M / K / k / m / b) and unit (% /
  percent -> pct, pp / pps -> pp, bp / bps -> bps, x / × -> mult). Currency or scale -> money (a per-share
  "$5.09/share" is money); otherwise plain. Value = number × scale; the quoted precision is the number of decimals
  as written ("$1.52B" is ±$5M; "18.43%" is ±0.005 points; approximate tokens get twice that).
- Markdown emphasis and backticks are removed first (columns stay those of the original text); URLs, HTML comments
  and the reference spans below are blanked, so they never produce a token.
- Ranges and lists inherit right to left: "$3.18–3.22B" is two money tokens, "0.1 / 4.1 / 8.1 / 11.1 / 14.1%" five
  percents, "−12/−5/0/+5/+12pp" five pp (never from a year, never through "and"); "$a – b" passes a's currency to
  b; an arithmetic chain "$1,075.6 − $282.6 = $801.9M" inherits the scale written once at the end; a slash list of
  exactly five plain numbers summing to 100 ± 1 is five percents (probabilities "15/30/30/17/8").
- Not quantities: a number glued to a word by a hyphen (CFM56-7B, MV-75, COVID-19), "200mm" without a currency (a
  length).

Ignore rules (02 §6.4, amended by the L2 rebase A12 and A19):
- Blanked before tokenizing: accession numbers, ISO dates / timestamps, YYYY-MM, year ranges (FY2024–25, 2023/24,
  FY23–25), release references ("5.4 final run", "new in 5.5", "pre-5.5"), SEC form names, statement pages (F-8),
  dates with month names, references (Item 7, Note 34, step 8 (c), § 8.6, PR #31, rule 3, tier 1-3 ...), versions
  (v5.1, 5.5.0, "release 5.7", "python 3.13"), SIC / CIK / CUSIP codes, IV@15 / @12%, period labels (Q2 2026, H1
  2026, FY 2025, FY26, 9M, YTD), times, "top / first / last / next / past N", ordinals, integer durations (3-yr,
  15-year, 90 days, 4 quarters — integers only, so "21.6 months" stays a number), share-scale constants (1/100,
  100×, and a power-of-ten divisor or multiplier: "/ 1000", "÷ 1,000", "× 1,000,000"), "x10.0", accounting-standard
  references (ASC 805-50, ASU 2016-13, IFRS 15, IAS 36, Topic 842), XBRL viewer pages (R4.htm), index and proper
  names (S&P 500, Russell 2000, Nasdaq-100, FTSE 100, Phillips 66 ...) and a folder's facts.json not_quantities.
- Classified as ignored after tokenizing: a bare integer 1900-2100 (a year), a bare integer ≤ 20 with no currency,
  unit, decimals or comma (a small count: "5 of the last 5", "moat 6/10"), a zero.
- Ignored only when UNMATCHED (fallbacks, so an engine figure equal to one still matches; the caller decides):
  method constants, each with its own context within 45 characters (METHOD_CONSTANTS: the 10/12/15/20/25% hurdles,
  2.5% terminal growth, the 35% cap blend, the 40% NI/OCF divergence, the 60% basis break, 50% capex coverage, the
  200% IRR cap, the $40B scope line, the 0.1x-10x band, 20x, 3x, 0.5x-2x, the 1.3 CAP slope, the default multiples /
  offsets / probabilities, and the IPR&D 5% materiality threshold), and release numbers (a plain one-decimal 4.0,
  5.0-5.7: "What 5.5 changed").
"""
import bisect
import re

SNIPPET_MAX_WORDS = 24   # R3 "under 25 words" (07 §1.7: one constant everywhere)

# ---------------------------------------------------------------------------
# The L0 slots (rebase A12), kept by name: L4's snippet check and the ignore rules share them
# ---------------------------------------------------------------------------
ACCOUNTING_STANDARD_RE = re.compile(r"(?<![A-Za-z])(?:ASC|ASU|SFAS|FAS|IFRS|IAS|IFRIC|SIC-)\s?\d+(?:[-–]\d+)*")
TOPIC_RE = re.compile(r"\bTopic \d{3}\b")
XBRL_VIEWER_PAGE_RE = re.compile(r"\bR\d+\.htm\b")
FORM_NAME_RE = re.compile(r"(?<![A-Za-z0-9])(?:10-K|10-Q|20-F|40-F|6-K|8-K|10-KT)(?:/A)?(?![A-Za-z0-9])")
IGNORE_PATTERNS = (ACCOUNTING_STANDARD_RE, TOPIC_RE, XBRL_VIEWER_PAGE_RE, FORM_NAME_RE)

SCALE_WORDS = {"trillion": 1e12, "tn": 1e12, "t": 1e12, "billion": 1e9, "bn": 1e9, "b": 1e9,
               "million": 1e6, "mn": 1e6, "mm": 1e6, "m": 1e6, "thousand": 1e3, "k": 1e3}
PRESENTATION_SCALES = (3, 6, 9)   # a statement table printed in thousands / millions / billions

# ---------------------------------------------------------------------------
# The token pattern (02 §6.3, ported from the tuned prototype cq_proto.TOKEN)
# ---------------------------------------------------------------------------
_MINUS = "−–—‒\\-"
_CUR = (r"US\$|C\$|CA\$|A\$|AU\$|R\$|HK\$|NT\$|S\$|MX\$|NZ\$|\$|€|£|¥|₹|₩|₪|₺|CHF\s?|"
        r"(?:RMB|EUR|GBP|JPY|CNY|INR|BRL|CAD|AUD|SEK|NOK|DKK|MXN|KRW|TWD|HKD|ZAR|ILS|CLP|COP|PEN|ARS|IDR|TRY|EGP|RUB|"
        r"PLN|SGD|NZD|USD)\s?")
SCALES = {"trillion": 1e12, "tn": 1e12, "T": 1e12, "billion": 1e9, "bn": 1e9, "B": 1e9, "b": 1e9,
          "million": 1e6, "mn": 1e6, "mm": 1e6, "M": 1e6, "m": 1e6, "thousand": 1e3, "K": 1e3, "k": 1e3}
# "/" is NOT in the look-behind: slash lists ("15/30/30/17/8", "−12/−5/0/+5/+12pp") are tokenized element by element
# and grouped afterwards; "1/100" and year ranges are blanked before.
TOKEN = re.compile(
    r"(?<![A-Za-z0-9_.,@#\\])"
    r"(?P<approx>~|≈|<|>|≤|≥|\+/-|±)?\s?"
    r"(?P<sign>[" + _MINUS + r"+])?"
    r"(?:(?P<cur>" + _CUR + r")\(?)?"
    r"(?P<num>\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?)"
    r"(?:(?<=\d)\)(?=\s?(?:trillion|billion|million|thousand|tn|bn|mn|mm|B|M|K|k|m|b|T)(?![A-Za-z0-9])))?"  # $(72,178) thousand
    r"(?P<scale>\s?(?:trillion|billion|million|thousand|tn|bn|mn|mm|B|M|K|k|m|b|T)(?![A-Za-z0-9]))?"
    r"(?P<unit>\s?%|\s?pps?(?![A-Za-z])|\s?bps?(?![A-Za-z])|x(?![A-Za-z0-9])|×|\s?percent(?![A-Za-z]))?"
    r"(?![A-Za-z0-9_])")

_MONTHS = (r"jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|june?|july?|aug(?:ust)?|sep(?:t(?:ember)?)?|"
           r"oct(?:ober)?|nov(?:ember)?|dec(?:ember)?")
INDEX_NAMES_RE = re.compile(
    r"S&P\s?(?:500|400|600|100)\b|\bRussell\s(?:1000|2000|3000)\b|\bNasdaq[- ]100\b|\bFTSE\s(?:100|250)\b|"
    r"\bFortune\s(?:500|100|1000)\b|\bEuro\sStoxx\s50\b|\bStoxx\s600\b|\bNikkei\s225\b|\bDAX\s40\b|\bCAC\s40\b|"
    r"\bIBEX\s35\b|\bASX\s200\b|\bTSX\s60\b|\bPhillips\s66\b")

# Reference spans: blanked in every mode (analysis.md, reasons, snippets) — identifiers, dates, references
_REFERENCE_STRIP = [re.compile(p) for p in (
    r"(?s)<!--.*?-->",                                                   # HTML comments
    r"https?://\S+",                                                     # URLs
    r"(?i)\bsha-?256\s*[:=]?\s*[0-9a-f]{6,64}\b|\b[0-9a-f]{32,64}\b",    # digests (sha256 1a2b3c4d5e6f, hashes)
    r"\b\d{10}-\d{2}-\d{6}\b",                                           # accession numbers
    r"\b\d{4}-\d{2}-\d{2}(?:T[\d:+\-.Z]+)?\b",                           # ISO dates / timestamps
    r"\b\d{4}-\d{2}\b(?!\d)",                                            # 2025-12
    r"\b(?:FY|CY)?(?:19|20)\d{2}\s?[–\-/]\s?(?:FY)?\d{2}\b(?![\d.%]|,\d)",  # year ranges FY2024–26, 2023/24
    r"\b(?:FY|CY)\d{2}\s?[–\-/]\s?(?:FY)?\d{2}\b(?![\d.%]|,\d)",           # FY23–25
    r"(?i)\b[45]\.\d(?:\.\d)?\b(?=\s+(?:final\s+|preliminary\s+)?(?:runs?|re-?scores?|rules?|engine|outputs?|method|"
    r"pass|records?|fields?|flags?|additions?|changes?|changed|checks?|fix(?:es)?|basis|release|scores?)\b)",
    r"(?i)\b(?:in|since|before|after|under|pre|post)[\s-]+[45]\.\d(?:\.\d)?\b(?![\d%x×])",   # 'new in 5.5', 'pre-5.5'
    r"(?<![A-Za-z0-9])(?:ASC|ASU|SFAS|FAS|IFRS|IAS|IFRIC|SIC-)\s?\d+(?:[-–]\d+)*",            # A12 standards
    r"\bTopic \d{3}\b",
    r"\bR\d+\.htm\b",
    r"\b(?:10-K|10-Q|20-F|40-F|6-K|8-K|10-KT|S-1|S-3|S-4|F-1|F-3|F-4|11-K|DEF\s?14A|13D|13G|13F|424B\d|N-CSR)"
    r"(?:/A|405)?\b",
    r"\bF-\d+\b",                                                        # financial-statement pages (p. F-8)
    r"(?i)\b(?:" + _MONTHS + r")\.?\s+\d{1,2}(?:st|nd|rd|th)?(?:,\s*\d{4})?\b",
    r"(?i)\b\d{1,2}(?:st|nd|rd|th)?\s+(?:" + _MONTHS + r")\b\.?(?:\s+\d{4})?",
    r"(?i)\b(?:items?|steps?|sections?|§|rulings?|decisions?|rounds?|phase|clauses?|rules?|notes?|part|schedule|"
    r"exhibits?|ex\.|pages?|pp\.|p\.|chapter|article|art\.|tier\s+[1-3]|level\s+[1-3]|stage)\s*#?\d+(?:\.\d+)*[a-z]?"
    r"(?:\s*\([a-z]\))?(?:\s?[–-]\s?\d+)?",                             # "pp. 51–52", "Notes 4-5"
    r"§\s?\d+(?:\.\d+)*",
    r"#\d+",                                                             # PR numbers, rankings (#2 spine)
    r"\bv\d+(?:\.\d+)*\b",                                               # v5, v5.1
    r"\b\d+\.\d+\.\d+\b",                                                # 5.5.0
    r"(?i)\b(?:release|engine|make_score(?:\.py)?|version|spec|pass|python)\s+\d+(?:\.\d+)*\b",
    r"(?i)\bSIC(?:\s+codes?)?\s*\d{4}(?:\s*(?:/|,|and|or|–|-)\s*\d{4})*",
    r"(?i)\bCIK\s*0*\d+",
    r"(?i)\bCUSIP\s*[0-9A-Z]{9}",
    r"\b(?:Q[1-4]|H[12]|9M|6M|3M)\s+FY\s?\d{2,4}\b",                    # Q2 FY2026, 9M FY2026
    r"\b(?:Q[1-4]|H[12]|FY|CY|9M|6M|3M|YTD)\s?'?\d{2,4}\b",             # Q2 2026, FY 2025, FY26
    r"\b(?:9M|6M|3M)(?=\s+(?:YTD|ended|period|results)\b)",             # "9M YTD", "the 9M ended"
    r"\b\d{1,2}:\d{2}(?::\d{2})?\b",                                     # times
    INDEX_NAMES_RE.pattern,
)]
# Quantity-like spans that are method / reading conventions: blanked for analysis.md and reasons, NOT for snippets
# (a snippet "a 3-year agreement" shows the number 3)
_CONVENTION_STRIP = [re.compile(p) for p in (
    r"@\s?\d+(?:\.\d+)?%?",                                              # IV@15, @12%
    r"(?i)\b(?:top|first|last|next|past)\s+\d+\b",                       # top 10, last 3
    r"\b\d+(?:st|nd|rd|th)\b",                                           # ordinals
    r"(?i)(?<![\d.,])\b\d+\s*(?:-|–)?\s*(?:yr|year|month|day|week|quarter)s?\b(?!\s+(?:revenue|cagr))",  # 3-yr, 90 days
    r"\b1/100\b|\b100×|\b100x\b",                                        # share-scale constants
    r"(?:[/÷×]|\bx(?=\s))\s?(?:1,?000|10,?000|1,?000,?000)\b(?![.,]\d)",   # "/ 1000", "÷ 1,000", "× 1,000"
    r"\bx\d+(?:\.\d+)?\b",                                               # scaled x10.0
)]
EMPH = re.compile(r"\*\*|__|(?<![A-Za-z0-9])\*(?=\S)|(?<=\S)\*(?![A-Za-z0-9])|`")
APPROX_WORDS = re.compile(r"(?i)(?:~|≈|about|approximately|approx\.|roughly|around|nearly|almost|some|over|under|"
                          r"more than|less than|up to|at least|at most|close to|c\.)\s*$")
SMALL_INT = 20
QUOTED_SPAN = re.compile(r"“[^”]*”")   # 07 §1.10: worker text echoed by make_score — never a source, never checked

# Method constants (02 §6.4): (kind, values, context) — ignored only when unmatched AND the context is within 45 chars
METHOD_CTX_CHARS = 45
METHOD_CONSTANTS = (
    ("pct", (10.0, 12.0, 15.0, 20.0, 25.0), r"hurdle|clear|IV@|discount|tier|margin of safety"),
    ("pct", (2.5,), r"terminal|g_?term|converge"),
    ("pct", (35.0,), r"\bcap\b|CAP|blend"),
    ("pct", (40.0,), r"NI_OCF|net income and operating cash flow|differ"),
    ("pct", (60.0,), r"BASIS_BREAK|revenue (?:jump|drop|move)"),
    ("pct", (50.0,), r"CAPEX_COVERAGE|of D&A"),
    ("pct", (200.0,), r"solver|IRR cap|IRR_CAPPED"),
    ("pct", (5.0,), r"threshold|material|ACQUIRED_IPRD"),           # engine 5.6: the IPR&D materiality line
    ("money", (40e9,), r"scope|cap line|market cap|under|universe"),
    ("mult", (0.1, 10.0), r"band|0\.1\s?[x×]"),
    ("mult", (20.0,), r"the price|20\s?[x×] limit"),
    ("mult", (3.0,), r"spans|OE_VOLATILE|move by"),
    ("mult", (0.5, 2.0), r"0\.5\s?[x×]\s?[–-]\s?2\s?[x×]"),
    ("plain", (1.3,), r"CAP|clamp|2 \+ 1\.3"),
    ("plain", (0.75, 0.9, 1.0, 1.1, 1.25), r"default|mult"),
    ("pp", (12.0, 5.0, 0.0), r"default|offset"),
    ("pct", (10.0, 25.0, 30.0), r"default|probs?\b|probabilit"),   # the default probabilities 10/25/30/25/10
)
_CONST_RX = [(k, vals, re.compile(rx, re.I)) for k, vals, rx in METHOD_CONSTANTS]
RELEASE_NUMBERS = (4.0, 5.0, 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7)   # A19: the release-number fallback set


class Token:
    """One number token. raw: the text as written; kind: money | pct | pp | bps | mult | plain; v: the number as
    written (unscaled, unsigned); val: v × scale (money / plain / mult; pct / pp / bps carry v in points);
    dec: decimals as written; cur / scale / unit: as written; approx: ~ ≈ or an approximation word before it;
    start / end: offsets in the ORIGINAL text; cls: None (a quantity) or year / small / zero (ignored);
    const_ctx: True when it is a method-constant candidate with its context near (ignored only when unmatched)."""
    __slots__ = ("raw", "kind", "v", "val", "dec", "cur", "scale", "unit", "approx", "start", "end", "comma",
                 "sign", "cls", "const_ctx", "release_like", "_s", "_e", "ranged")

    def __init__(self, **kw):
        for k in self.__slots__:
            setattr(self, k, kw.get(k))

    def as_dict(self):
        return {"raw": self.raw, "kind": self.kind, "value": self.val if self.kind in ("money", "plain", "mult")
                else self.v, "decimals": self.dec, "approx": bool(self.approx), "cls": self.cls}

    def __repr__(self):
        return f"Token({self.raw!r}, {self.kind}, {self.val if self.kind in ('money', 'plain', 'mult') else self.v})"


def _remove_emphasis(text):
    """(text without markdown emphasis / backticks, map from new offsets to original offsets)."""
    out, idx, last = [], [], 0
    for m in EMPH.finditer(text):
        seg = text[last:m.start()]
        out.append(seg)
        idx.extend(range(last, m.start()))
        last = m.end()
    out.append(text[last:])
    idx.extend(range(last, len(text)))
    idx.append(len(text))
    return "".join(out), idx


def _blank(text, rx):
    return rx.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), text)


def blank_literals(text, strings):
    """text with every occurrence of each literal string (worker text, not_quantities) replaced by spaces of the same
    length (newlines kept), so offsets stay true."""
    for s in sorted({s for s in strings if isinstance(s, str) and s}, key=len, reverse=True):
        if s in text:
            text = text.replace(s, re.sub(r"[^\n]", " ", s))
    return text


def blank_quoted(text):
    """text with every “…” span blanked (07 §1.10: make_score's echo of worker text)."""
    return _blank(text, QUOTED_SPAN)


def strip_text(text, snippet=False, not_quantities=()):
    """(stripped text, offset map): emphasis removed, then not_quantities, the reference spans and (unless snippet)
    the convention spans blanked with spaces."""
    t, idx = _remove_emphasis(text if isinstance(text, str) else "")
    t = blank_literals(t, not_quantities)
    for rx in _REFERENCE_STRIP + ([] if snippet else _CONVENTION_STRIP):
        t = _blank(t, rx)
    return t, idx


def tokenize(text, not_quantities=(), snippet=False):
    """Every number token of text (ignored ones too: their cls says why), in order. snippet=True keeps the
    convention spans (durations, ordinals, "@" ...) and classifies nothing as a small count — a snippet's numbers
    are all candidates for the fact's value; years stay ignored."""
    t, idx = strip_text(text, snippet=snippet, not_quantities=not_quantities)
    toks = []
    for m in TOKEN.finditer(t):
        st = m.start()
        pre = t[max(0, st - 12):st]
        sign = m.group("sign") or ""
        if sign == "-" and re.search(r"[A-Za-z][A-Za-z0-9]*$", pre):
            continue                       # MV-75 written as sign + number
        if re.search(r"[A-Za-z][A-Za-z0-9]*-$", pre) or re.search(r"[A-Za-z][A-Za-z0-9]*-$",
                                                                    t[max(0, m.start("num") - 12):m.start("num")]):
            continue                       # identifier: CFM56-7B, COVID-19, MV-75
        if sign == "-" and m.start("sign") > 0 and t[m.start("sign") - 1].isalnum():
            continue
        if (m.group("scale") or "").strip() == "mm" and not m.group("cur"):
            continue                       # 200mm: a length
        num = m.group("num")
        unit = (m.group("unit") or "").strip()
        unit = {"percent": "%", "×": "x", "pps": "pp", "bp": "bps"}.get(unit, unit)
        s0 = st
        while s0 < m.end() and t[s0].isspace():
            s0 += 1
        a0, a1 = idx[s0], idx[m.end() - 1] + 1          # offsets in the original text (markup outside the token)
        toks.append(Token(raw=text[a0:a1], v=float(num.replace(",", "")),
                          dec=len(num.split(".")[1]) if "." in num else 0, cur=(m.group("cur") or "").strip(),
                          scale=(m.group("scale") or "").strip(), unit=unit,
                          approx=bool(m.group("approx")) or bool(APPROX_WORDS.search(t[max(0, st - 20):st])),
                          start=a0, end=a1, comma="," in num, sign=sign,
                          _s=m.start(), _e=m.end(), ranged=False))
    _join_lists(t, toks)
    for k in toks:
        _classify(k, snippet)
    return toks


def _join_lists(t, toks):
    """Ranges, slash lists and arithmetic chains (02 §6.3), right to left over adjacent tokens."""
    # slash lists of exactly five plain numbers summing to 100 ± 1: probabilities
    i = 0
    while i < len(toks):
        j = i
        while j + 1 < len(toks) and re.fullmatch(r"\s*/\s*", t[toks[j]._e:toks[j + 1]._s]):
            j += 1
        run = toks[i:j + 1]
        if len(run) == 5 and all(not k.cur and not k.scale and (not k.unit or (k is run[-1] and k.unit == "%"))
                                 for k in run) and abs(sum(k.v for k in run) - 100) <= 1:
            for k in run:
                k.unit = "%"
                k.ranged = True
        i = j + 1
    for a, b in reversed(list(zip(toks, toks[1:]))):
        gap_raw = t[a._e:b._s]
        gap = gap_raw + (b.sign if b.sign and b.sign in "−–-" else "")
        joined = bool(re.fullmatch(r"\s*(?:/|to)\s*", gap_raw)) or bool(re.fullmatch(r"\s*(?:[–\-−]|to|/)\s*", gap))
        yearish = not a.comma and a.dec == 0 and 1900 <= a.v <= 2100
        if not yearish and joined and not a.scale and not a.unit and not (a.cur and not b.cur and b.unit):
            if b.scale or b.unit:
                a.scale, a.unit = b.scale, b.unit
                a.cur = a.cur or b.cur
                a.ranged = True
        arith = (re.fullmatch(r"\s*[+=×÷−\-–]\s*", gap_raw) or (not gap_raw.strip() and b.sign in ("+", "−", "-")))
        if arith and a.cur and b.cur and not a.scale and not a.unit and b.scale and not b.unit:
            a.scale = b.scale
        if re.fullmatch(r"\s*(?:[–\-−]|to)\s*", gap) and a.cur and not b.cur:
            b.cur = a.cur


def _classify(k, snippet):
    sf = SCALES.get(k.scale, 1.0)
    if k.unit == "%":
        k.kind = "pct"
    elif k.unit == "pp":
        k.kind = "pp"
    elif k.unit == "bps":
        k.kind = "bps"
    elif k.unit == "x":
        k.kind = "mult"
    elif k.cur or k.scale:
        k.kind = "money"
    else:
        k.kind = "plain"
    k.val = k.v * sf if k.kind in ("money", "plain", "mult") else k.v
    k.cls = None
    if k.kind == "plain" and k.dec == 0 and not k.comma:
        if 1900 <= k.v <= 2100:
            k.cls = "year"
        elif k.v <= SMALL_INT and not snippet:
            k.cls = "small"
    if k.cls is None and k.v == 0 and not snippet:
        k.cls = "zero"
    k.release_like = k.kind == "plain" and k.dec == 1 and not k.cur and round(k.v, 1) in RELEASE_NUMBERS


def numbers(text, not_quantities=()):
    """The tokens of text that are quantities (cls None) — the numbers a checker traces."""
    return [k for k in tokenize(text, not_quantities) if k.cls is None]


def is_method_constant(tok, text):
    """True when tok is one of METHOD_CONSTANTS and its own context is within 45 characters of it in text (the
    caller ignores it only when it is also unmatched)."""
    val = tok.val if tok.kind == "money" else tok.v
    lo, hi = max(0, tok.start - METHOD_CTX_CHARS), tok.end + METHOD_CTX_CHARS
    for kind, vals, rx in _CONST_RX:
        if kind == tok.kind and any(abs(val - c) <= 1e-9 * max(1.0, abs(c)) for c in vals):
            if rx.search(text[lo:hi]):
                return True
    return False


def carries_number(text, not_quantities=()):
    """R3 / 02 §5 "the reason carries a number": at least one token survives the ignore rules — not a year, small
    count, zero, a method constant in its context or a release number. (R7's ttm_rejection_reason uses the same
    definition.)"""
    s = text if isinstance(text, str) else ""
    return any(not (k.release_like or is_method_constant(k, s)) for k in numbers(s, not_quantities))


def tolerance(tok, approx_widen=2.0):
    """Half a unit of the token's last written digit, in the token's own measure (dollars for money, percent points
    for pct / pp, bps for bps); approximate tokens (~, "about", <, ...) get approx_widen times that."""
    sf = SCALES.get(tok.scale, 1.0) if tok.kind in ("money", "plain", "mult") else 1.0
    tol = 0.5 * 10 ** (-tok.dec) * sf
    return tol * (approx_widen if tok.approx else 1.0)


def line_col(text, pos):
    """(1-based line, 1-based column) of offset pos in text."""
    line = text.count("\n", 0, pos) + 1
    return line, pos - (text.rfind("\n", 0, pos) + 1) + 1


class ValueSet:
    """A set of source values a token is matched against (02 §6.5): value only (currency is not part of the match),
    signs ignored, at the token's quoted precision (tolerance(); approximate tokens twice that; plus 1e-9 relative).
    A pct / pp token matches 100 × v for every value |v| <= 100 (fractions: 0.1843 is "18.43%"), every percent
    print added with add_points (key_numbers.md's "18.43%"), and a value whose key ends _pct / _pp as it stands; a
    bps token matches 1e4 × v for |v| <= 1; money / plain / mult tokens match the values themselves. Sorted arrays
    and bisect: a folder checks in milliseconds."""

    def __init__(self):
        self._raw, self._pct, self._bps = [], [], []
        self._frozen = True

    def add(self, v, key=None):
        if isinstance(v, bool) or not isinstance(v, (int, float)) or v != v or v in (float("inf"), float("-inf")):
            return
        a = abs(float(v))
        self._raw.append(a)
        if a <= 100:
            self._pct.append(a * 100.0)
        if a <= 1:
            self._bps.append(a * 1e4)
        if isinstance(key, str) and key.endswith(("_pct", "_pp")):
            self._pct.append(a)
        self._frozen = False

    def add_points(self, v):
        """A figure printed as a percent (its number in points)."""
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            self._pct.append(abs(float(v)))
            self._frozen = False

    def add_tokens(self, toks):
        """The numbers printed in a text (key_numbers.md, an engine flag string): percents as points, the rest as
        values."""
        for k in toks:
            if k.kind in ("pct", "pp"):
                self.add_points(k.v)
            elif k.kind == "bps":
                self._bps.append(abs(k.v))
            else:
                self._raw.append(abs(k.val))
        self._frozen = False

    def merge(self, other):
        self._raw += other._raw
        self._pct += other._pct
        self._bps += other._bps
        self._frozen = False
        return self

    def _freeze(self):
        if not self._frozen:
            self._raw.sort()
            self._pct.sort()
            self._bps.sort()
            self._frozen = True

    @staticmethod
    def _hit(arr, v, tol):
        slack = tol + 1e-9 * max(1.0, abs(v))
        i = bisect.bisect_left(arr, v - slack)
        return i < len(arr) and arr[i] <= v + slack

    def match(self, tok, approx_widen=2.0):
        self._freeze()
        tol = tolerance(tok, approx_widen)
        if tok.kind in ("pct", "pp"):
            return self._hit(self._pct, abs(tok.v), tol)
        if tok.kind == "bps":
            return self._hit(self._bps, abs(tok.v), tol)
        return self._hit(self._raw, abs(tok.val), tol)

    def __len__(self):
        return len(self._raw) + len(self._pct) + len(self._bps)


# ---------------------------------------------------------------------------
# The snippet rule (07 §1.7) — one definition for facts.py, interim_bridge.py (L4) and the share-class lane (L8)
# ---------------------------------------------------------------------------
def snippet_words(snippet):
    """The snippet's word count (R3's limit is SNIPPET_MAX_WORDS)."""
    return len(str(snippet or "").split())


def _close(x, n, dec):
    return abs(x - n) <= 0.5 * 10 ** (-dec) + 1e-9 * max(1.0, abs(n))


def snippet_shows_value(snippet, value, unit=None, presentation_scale=False):
    """True when the snippet carries a number that is `value` at the snippet's own precision (signs ignored:
    outflows print in parentheses). unit "pct" / "pp" (fractions, 0.126 = 12.6%) matches a percent or pp token;
    "bps" (a fraction, 0.0042 = 42 bps) a bps token; "x" a multiple ("2.5x") or a bare number; any other unit
    (money, counts, per-share) a token with no percent / bps / multiple unit — "$1.92 billion" proves 1,923,686,000
    at 2 decimals. presentation_scale (a statement table "in millions": declared interim legs, filing / release
    facts, share-class counts) lets a bare token (no scale word) also match value / 10^k for k in 3, 6, 9
    ("Revenue 1,923.7" proves 1,923,686,000; "539" proves 539,000,000 and not 538,000,000). A zero matches only a
    zero. The snippet is read by the check_quotes tokenizer in snippet mode: references, dates, form names and
    accounting-standard numbers are not numbers; durations and small counts are."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    v = abs(float(value))
    for k in tokenize(snippet, snippet=True):
        if k.cls == "year":
            continue
        if (k.v == 0) != (v == 0):
            continue
        if unit in ("pct", "pp"):
            if k.kind in ("pct", "pp") and _close(v * 100.0, k.v, k.dec):
                return True
            continue
        if unit == "bps":
            if k.kind == "bps" and _close(v * 1e4, k.v, k.dec):
                return True
            continue
        if k.kind in ("pct", "pp", "bps") or (k.kind == "mult" and unit != "x"):
            continue
        mult = SCALES.get(k.scale) if k.scale else None
        if mult is not None:
            if _close(v / mult, k.v, k.dec):
                return True
            continue
        if _close(v, k.v, k.dec):
            return True
        if presentation_scale and k.kind != "mult" and any(_close(v / 10 ** e, k.v, k.dec) for e in PRESENTATION_SCALES):
            return True
    return False
