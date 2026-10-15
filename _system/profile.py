#!/usr/bin/env python3
"""Company profile store (v5.4, 2026-10-14) -> <TICKER>/profile.json.

Usage: python3 profile.py <TICKER> [--cik N] [--no-write] [--quiet]
       python3 profile.py --all [--max-age-days 7] [--force] [--quiet]

Schema: SITE_CONTRACT.md, "Decisions (owner, 2026-10-14 evening - layout and
profile)" and the extended `street` block under "Decisions (owner, 2026-10-14
night - Forecast tab)". build_site.py copies the file into the record as
`record.profile`; the app's About / Street / Filings cards render it.

Sources (every figure is a filed value, a Nasdaq-published value or plain
arithmetic on them; nothing is estimated):
  EDGAR submissions  https://data.sec.gov/submissions/CIK##########.json
      sic, sicDescription, stateOfIncorporation, fiscalYearEnd, category,
      exchanges, addresses.business (the fallback address), website, phone and
      the filings.recent arrays. `about.first_sec_filing` (+ `_form`), the
      IPO-date proxy, is the earliest registration / listing form (S-1, F-1,
      S-11, Form 10, 20FR12B, 40FR12B, 8-A12B, 424B4 ...) across `recent` and
      the paginated files (fetched oldest first until one is seen) unless a
      periodic report precedes it (a company public before EDGAR), else the
      earliest filing of any form. A Form D or a DRS draft never wins.
  EDGAR 10-K primary document (the latest 10-K; 20-F for foreign filers)
      `about.headquarters` / `address` = the inline-XBRL cover's filed
      dei:EntityAddress* values (`address.source` "annual filing cover"),
      falling back to the submissions business address ("EDGAR submissions").
      `about.description` = the Item 1 Business (or "Items 1 and 2. Business
      and Properties") opening prose run (<= 1,500 chars, cut at a sentence
      boundary): the TOC occurrence and cross-reference sheets are skipped,
      and so is everything under the heading before the first line that is
      itself prose — sub-headings, a sub-section index with page numbers, a
      forward-looking-statements lead-in, leading definitional / address /
      "We refer you to Item 1A" sentences (which never count toward the
      300-char minimum); page headers / footers never leak; stopped at the
      next sub-heading. For a 20-F the Item 4.B Business
      Overview, else Item 4 Information on the Company, else (integrated
      annual reports such as Gold Fields', which have no Item 4 heading) the
      bare "Overview" section that names the registrant. `description.source`
      says which. `about.employees` = the company's total headcount from the
      Human Capital / Employees passage, with the sentence kept as evidence:
      "As of <date>, we had N employees", "<Name> had N ... as of / during
      <date>", the multi-year sentence (latest year's count), "We ended the
      year 2025 with N", or the integrated-report bullet "N employees (2024:
      N)" dated by the filing's fiscal period end (basis recorded where it is
      not a point-in-time count). A function's or a location's count, a
      per-type split ("N full-time employees and M part-time employees"), the
      registrant's and a subsidiary's counts without a total, or a sentence
      whose date is not a calendar date, is never published: employees is
      null and `about.employees_unresolved` keeps the sentence and the reason;
      null with no such sentence (never guessed). The count under the Human
      Capital / Employees heading outranks a later-dated one elsewhere.
  Nasdaq (User-Agent Mozilla/5.0, Accept application/json)
      company-profile, quote summary, analyst targetprice / ratings /
      earnings-forecast / estimate-momentum / earnings-date / peg-ratio and
      quote eps. Each endpoint fails independently: the affected sub-block is
      null and `warnings` says so; the EDGAR part is always written. `street`
      is null only when every analyst endpoint failed. Nasdaq placeholders are
      not figures: estimate-momentum means of 999 are null and quote/eps rows
      with consensus 0 AND earnings 0 are dropped (both leave a warning).

Refresh policy (--all): a name is skipped when its profile.json is younger
than --max-age-days (default 7) AND the newest EDGAR filing date (from the
small submissions feed, one request) is unchanged; --force rebuilds all.
Rate limits: at most 10 requests/second per host (0.11 s spacing); --all
pauses between names. EDGAR timeout 90 s, Nasdaq 40 s, three attempts with
backoff for both.

Exit status: 0 written (or --all finished), 2 no CIK / usage, 3 the EDGAR
submissions feed could not be read (nothing written), 4 the build itself
raised (a bug, traceback printed; nothing written).
"""
import json, sys, os, re, csv, html, math, time, datetime, traceback, urllib.request
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.environ.get("STOCKS_BASE") or os.path.dirname(HERE)
SYS = f"{BASE}/_system"
EDGAR_UA = {"User-Agent": "Muse research andrewmauro199612@gmail.com"}
NASDAQ_UA = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
EDGAR_TIMEOUT, NASDAQ_TIMEOUT = 90, 40
MIN_INTERVAL_S = 0.11          # <= 10 requests/second per host
ALL_SLEEP_S = 0.5              # pause between names under --all
DEFAULT_MAX_AGE_DAYS = 7
DESCRIPTION_MAX = 1500
FEED_FORMS = ("10-K", "10-Q", "8-K", "20-F", "40-F", "6-K", "S-1", "DEF 14A")
FEED_LIMIT = 20
ANNUAL_FORMS = ("10-K", "20-F", "40-F")

ITEM_DESCRIPTIONS = {
    "1.01": "Material agreement", "1.02": "Termination of agreement", "1.03": "Bankruptcy or receivership",
    "1.05": "Material cybersecurity incident",
    "2.01": "Acquisition/disposition", "2.02": "Results of operations", "2.03": "Debt obligation",
    "2.04": "Triggering event on a debt obligation", "2.05": "Exit costs", "2.06": "Impairment",
    "3.01": "Listing notice", "3.02": "Unregistered sale of equity", "3.03": "Change to security holders' rights",
    "4.01": "Auditor change", "4.02": "Non-reliance on financials",
    "5.01": "Change in control", "5.02": "Officer/director change", "5.03": "Charter or bylaw amendment",
    "5.05": "Code of ethics change", "5.07": "Shareholder vote", "5.08": "Shareholder nominations",
    "7.01": "Reg FD", "8.01": "Other events", "9.01": "Financial statements and exhibits",
}
FORM_DESCRIPTIONS = {
    "10-K": "Annual report", "10-Q": "Quarterly report", "20-F": "Annual report (foreign private issuer)",
    "40-F": "Annual report (Canadian issuer)", "6-K": "Report of a foreign private issuer",
    "S-1": "Registration statement", "DEF 14A": "Proxy statement", "8-K": "Current report",
}
MONTHS = {m: i for i, m in enumerate(("january", "february", "march", "april", "may", "june", "july", "august",
                                      "september", "october", "november", "december"), 1)}
MONTHS.update({k[:3]: v for k, v in list(MONTHS.items())})
MONTHS["sept"] = 9   # "Sept. 30, 2025" (Super Micro)


def et_today():
    return datetime.datetime.now(ZoneInfo("America/New_York")).date()


# ---------------------------------------------------------------------------
# HTTP: per-host throttle, retries with backoff
_last_hit = {}


def _throttle(url):
    host = url.split("/")[2] if "//" in url else url
    wait = _last_hit.get(host, 0) + MIN_INTERVAL_S - time.monotonic()
    if wait > 0:
        time.sleep(wait)
    _last_hit[host] = time.monotonic()


def get_bytes(url, headers, timeout):
    last = None
    for attempt in range(3):
        _throttle(url)
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except Exception as e:
            last = e
            if attempt < 2:
                time.sleep(2 ** attempt)
    raise last


def edgar_json(url):
    return json.loads(get_bytes(url, EDGAR_UA, EDGAR_TIMEOUT))


def nasdaq_json(url):
    d = json.loads(get_bytes(url, NASDAQ_UA, NASDAQ_TIMEOUT))
    if not isinstance(d, dict):
        raise ValueError("non-object response")
    st = d.get("status") or {}
    if isinstance(st, dict) and st.get("rCode") not in (None, 200):
        raise ValueError(f"rCode {st.get('rCode')}: {st.get('bCodeMessage')}")
    return d.get("data")


def jload(p):
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def write_atomic(path, obj):
    """Serialise first (a NaN / Infinity raises before any file exists), then write a temp file next to the target
    and swap it in; the temp file is removed if anything fails, so no profile.json.tmp is left in a company folder."""
    data = json.dumps(obj, indent=1, ensure_ascii=False, allow_nan=False)
    tmp = path + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(data)
        for attempt in range(20):
            try:
                os.replace(tmp, path)
                return
            except PermissionError:
                time.sleep(0.1 * (attempt + 1))
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            try:
                os.remove(tmp)
            except OSError:
                pass


def resolve_cik(ticker, cik_arg=None):
    """--cik > dcf_numbers.json cik (the CIK the engine used) > sec_tickers_exchange.json > universe.csv."""
    if cik_arg:
        return int(cik_arg)
    nums = jload(f"{BASE}/{ticker}/dcf_numbers.json") or {}
    if isinstance(nums, dict) and nums.get("cik"):
        return int(nums["cik"])
    sec = jload(f"{SYS}/sec_tickers_exchange.json")
    if isinstance(sec, dict):
        m = {}
        for rec in sec.get("data") or []:
            try:
                m.setdefault(str(rec[2]).upper(), int(rec[0]))
            except Exception:
                pass
        for cand in (ticker, ticker.replace("/", "-"), ticker.replace("/", "."), ticker.replace(".", "-")):
            if cand in m:
                return m[cand]
    try:
        with open(f"{SYS}/universe.csv", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row.get("ticker") == ticker and row.get("cik"):
                    return int(row["cik"])
    except Exception:
        pass
    return None


# ---------------------------------------------------------------------------
# Numbers and dates
NUM_RE = re.compile(r"[+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?")


def num(v):
    """'$738.01' / '4,348,338' / '1.23%' -> float; 'N/A', '', None, 'NaN', 'Infinity', '1_000' -> None.
    Only a finite decimal literal is a number: NaN / inf would crash intnum or leak invalid JSON."""
    if v is None or isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return float(v) if math.isfinite(v) else None
    s = str(v).strip()
    if not s or s.upper() in ("N/A", "NA", "--", "-"):
        return None
    s = s.replace("$", "").replace(",", "").replace("%", "").strip()
    if not NUM_RE.fullmatch(s):
        return None
    try:
        f = float(s)
    except (ValueError, OverflowError):
        return None
    return f if math.isfinite(f) else None


def intnum(v):
    f = num(v)
    return int(round(f)) if f is not None else None


def iso_from_mdy(s):
    """'10/01/2025' -> '2025-10-01'; anything else -> None."""
    m = re.search(r"(\d{1,2})/(\d{1,2})/(\d{4})", str(s or ""))
    if not m:
        return None
    try:
        return datetime.date(int(m.group(3)), int(m.group(1)), int(m.group(2))).isoformat()
    except ValueError:
        return None


def iso_from_text_date(s):
    """'December 31, 2025' / 'Dec. 31, 2025' / '31 December 2025' -> '2025-12-31'; else None."""
    s = str(s or "")
    m = re.search(r"([A-Za-z]{3,9})\.?\s+(\d{1,2}),?\s+(\d{4})", s)
    if m and m.group(1).lower() in MONTHS:
        try:
            return datetime.date(int(m.group(3)), MONTHS[m.group(1).lower()], int(m.group(2))).isoformat()
        except ValueError:
            return None
    m = re.search(r"(\d{1,2})\s+([A-Za-z]{3,9})\.?,?\s+(\d{4})", s)
    if m and m.group(2).lower() in MONTHS:
        try:
            return datetime.date(int(m.group(3)), MONTHS[m.group(2).lower()], int(m.group(1))).isoformat()
        except ValueError:
            return None
    return iso_from_mdy(s)


def month_key(label):
    """'Sep 2026' -> '2026-09' (sortable); None when unparseable."""
    m = re.search(r"([A-Za-z]{3,9})\.?\s+(\d{4})", str(label or ""))
    if m and m.group(1).lower() in MONTHS:
        return f"{int(m.group(2)):04d}-{MONTHS[m.group(1).lower()]:02d}"
    return None


# ---------------------------------------------------------------------------
# Filing text: strip tags, unescape, collapse whitespace (block tags -> newline)
def _decode(raw):
    if isinstance(raw, bytes):
        try:
            return raw.decode("utf-8")
        except UnicodeDecodeError:
            return raw.decode("cp1252", "replace")
    return raw


def html_to_text(raw):
    s = _decode(raw)
    s = re.sub(r"(?is)<(script|style|head)[^>]*>.*?</\1>", " ", s)
    s = re.sub(r"(?is)<!--.*?-->", " ", s)
    s = re.sub(r"(?is)<(?:br|p|div|tr|li|h[1-6]|table|td|th|section|article)\b[^>]*>", "\n", s)
    # inline tags vanish: EDGAR documents split words across <span>s ("2</span><span>025", "It<span>em 1") and keep
    # their whitespace inside the spans, so a space here would break filed numbers and headings
    s = re.sub(r"(?is)</?(?:span|b|i|u|em|strong|a|font|sup|sub|small|big|ix:[a-z]+)\b[^>]*>", "", s)
    s = re.sub(r"(?is)<[^>]+>", " ", s)
    s = html.unescape(s)
    if re.search(r"&(?:#\d{2,5}|#x[0-9a-f]{2,4}|nbsp|amp|quot|rsquo|ldquo|rdquo);", s, re.I):
        s = html.unescape(s)   # integrated-report 20-Fs double-escape their text ("&amp;#8226;")
    s = s.replace("\xa0", " ").replace("​", "").replace("\xad", "")
    # non-breaking / Unicode hyphens are hyphens ("full‑time" with U+2011 — onsemi), so the patterns see "full-time"
    s = s.replace("‑", "-").replace("‐", "-")
    s = re.sub(r"[ \t\r\f\v]+", " ", s)
    s = re.sub(r" ?\n ?", "\n", s)
    s = re.sub(r"\n{2,}", "\n", s)
    return s.strip()


# abbreviations that end in a period without ending the sentence ("Acme Inc. is ...", "the U.S. market")
NOT_SENTENCE_END = r"(?<!\bInc)(?<!\bCo)(?<!\bCorp)(?<!\bLtd)(?<!\bNo)(?<!\bJr)(?<!\bSr)(?<!\bSt)(?<!\bU\.S)(?<!\bN\.A)(?<!\bS\.A)(?<!\bL\.P)(?<!\bMr)(?<!\bMrs)(?<!\bMs)(?<!\bDr)"


def _cut_at_sentence(prose, limit=DESCRIPTION_MAX, minimum=200):
    prose = re.sub(r"\s+", " ", prose).strip()
    if len(prose) <= limit:
        return prose
    head = prose[:limit]
    ends = [m.end() for m in re.finditer(NOT_SENTENCE_END + r"[.!?][\"'”’)]?(?=\s)", head)]
    ends = [e for e in ends if e >= minimum]
    if ends:
        return head[:ends[-1]].strip()
    sp = head.rfind(" ")
    return (head[:sp] if sp > minimum else head).rstrip() + " …"


SENTENCE_END = r"[.!?][\"'”’)]?(?=\s|$)"
SENTENCE_MIN_WORDS = 12
WORD_RE = r"[A-Za-z][A-Za-z'’\-]*"


def _has_sentence(text, min_words=SENTENCE_MIN_WORDS):
    """True when `text` holds a real sentence: a run of >= `min_words` words closed by a period /
    question mark / exclamation mark ON ONE LINE. Table-of-contents rows ("Item 1(a). Risk Factors",
    "D. Website Access to Carnival Corporation & plc SEC Reports", a page number) never reach that
    length between two sentence ends, index rows on separate lines cannot pool into one "sentence",
    and a run cut off by the end of `text` without its period does not count."""
    for line in text.split("\n"):
        for chunk in re.finditer(r"(.*?)" + SENTENCE_END, line):
            if len(re.findall(WORD_RE, chunk.group(1))) >= min_words:
                return True
    return False


def _is_toc_occurrence(after, toc_followers_re):
    """A heading is the table-of-contents entry when another item label follows it with no sentence
    in between: only page numbers, line breaks, "Item 1(a). Risk Factors"-style labels (Halliburton)
    or an index of the section's sub-headings ("A. Overview", Carnival) — none of them a sentence of
    >= 12 words. A short real section is followed by the next item too, but after a sentence."""
    f = re.search(toc_followers_re, after, re.I | re.M)
    if not f:
        return False
    return not _has_sentence(after[:f.start()])


def _heading_like(line):
    """A short line without sentence punctuation; an index prefix ("A. Overview", "1) General") is allowed."""
    core = re.sub(r"^(?:[A-Za-z]|\d{1,2}|[ivxIVX]{1,4})[.)][ \t]+(?=[A-Za-z])", "", line)
    return len(core) <= 70 and len(core.split()) <= 8 and not re.search(r"[.!?;:,]\s|[.!?]$", core)


def _prose_line(line):
    """A line that is itself running prose: >= 8 words with a sentence end on the line, mostly
    lower-case words (an index row, a cross-reference title or a page header is Title Case or
    has no period) and few digits (a cross-reference table is page numbers and ranges)."""
    words = re.findall(WORD_RE, line)
    if len(words) < 8 or not re.search(SENTENCE_END, line):
        return False
    lower = sum(1 for w in words if w[0].islower())
    digits = sum(c.isdigit() for c in line)
    return lower >= 0.5 * len(words) and digits <= 0.12 * len(line) and \
        len(re.findall(r"\b\d{1,3}\s*[-–]\s*\d{1,3}\b", line)) < 2


# forward-looking-statements / read-in-conjunction boilerplate that some filers put first under Item 1 (WCN, CBOE)
BOILERPLATE = (r"(?i)\bforward[\s\-]looking\s+(?:statements?|information)\b|\bshould\s+be\s+read\s+in\s+conjunction\b"
               r"|\bsafe\s+harbor\b|\bprivate\s+securities\s+litigation\s+reform\s+act\b"
               r"|\bincorporated\s+(?:herein\s+)?by\s+reference\b|\bas\s+to\s+which\s+reference\s+is\s+made\b")
# definitional / navigational lead-in sentences: who "we" are, the address / phone / website, the units amounts are
# stated in, a pointer to another item ("We refer you to Item 1A ..."). Yum! Brands' Item 1 opens with a whole paragraph
# of them and Arch Capital's with three, both directly above a sub-heading; they say nothing about the business, so a
# LEADING run of them is skipped like the forward-looking-statements lead-in (and so never counts toward min_prose).
PREAMBLE = (r"(?i)\breferred\s+to\s+(?:herein|in\s+this|throughout|collectively)\b|\bis\s+referred\s+to\b|\bas\s+used\s+in\s+this\b"
            r"|^\W*unless\s+(?:the\s+context|this\s+(?:form|report|annual)|we\s+state|otherwise|stated|indicated)"
            r"|\b(?:references?|the\s+terms?|we\s+(?:may\s+)?refer|when\s+we\s+refer)\b[^.]{0,250}?"
            r"\b(?:refers?\s+to|referring\s+to|used\s+interchangeably|are\s+(?:also\s+)?used)\b"
            r"|\b(?:throughout|in)\s+this\s+(?:document|report|annual\s+report|form\s+10-k)\b[^.]{0,120}\brefer"
            r"|\bprincipal\s+executive\s+offices?\b|\btelephone\s+number\b|\bwebsite\s+(?:address\s+)?is\b"
            r"|^\W*(?:we\s+refer\s+you\s+to|see|refer\s+to)\s+(?:item|part|note)\b"
            r"|^\W*for\s+(?:more|additional|further)\s+information\b[^.]{0,200}\b(?:see|refer)\b"
            r"|\bamounts\s+(?:in\s+this\s+(?:report|form\s+10-k)\s+)?are\s+(?:stated\s+|presented\s+|expressed\s+|shown\s+)?"
            r"in\s+(?:millions|thousands|billions)\b")


def _sentences(line):
    """`line` split into sentences: a period closing "Inc." / "U.S." / "Ltd." splits only before a capitalised word
    ("... Transmission, Inc. As used in ..." but not "Inc. (CECONY)"), and a fragment of fewer than three words
    ("Yum!" of "Yum! Brands") joins the next sentence."""
    out, carry, pos = [], "", 0
    for m in re.finditer(r"[.!?][\"'”’)]?(?=\s)", line):
        nxt = line[m.end():].lstrip()[:1]
        if re.search(ABBREVIATION_END, line[max(0, m.start() - 6):m.start()]) and not (nxt.isalpha() and nxt.isupper()):
            continue
        piece = carry + line[pos:m.end()]
        pos = m.end()
        if len(re.findall(WORD_RE, piece)) < 3:
            carry = piece
            continue
        out.append(piece.strip())
        carry = ""
    rest = (carry + line[pos:]).strip()
    if rest:
        out.append(rest)
    return out


def _strip_preamble(line):
    """`line` without its leading definitional / navigational sentences (PREAMBLE); "" when that is all it holds."""
    sents = _sentences(line)
    i = 0
    while i < len(sents) and re.search(PREAMBLE, sents[i]):
        i += 1
    return line if i == 0 else " ".join(sents[i:])


def _substance(line):
    """The length of `line` that is not definitional / navigational lead-in: what counts toward min_prose, so a
    trailing "As used in this report, the term ... refers to ..." (Con Edison) does not end the walk early."""
    return sum(len(x) + 1 for x in _sentences(line) if not re.search(PREAMBLE, x))


def _norm_header(line):
    """A page header / footer with its page token removed ("#WORTHREACHINGFOR I 7" -> "#worthreachingfor")."""
    s = re.sub(r"(?i)(?:[\s|·•\-–—]+(?:\d{1,3}|[ivxlc]{1,6}))+$", "", line.strip())
    return re.sub(r"\s+", " ", s).strip().lower()


def _repeated_headers(text, min_count=5):
    """Short lines that recur on page after page (running headers / footers such as "Constellation
    Brands, Inc. FY 2026 Form 10-K" or "#WORTHREACHINGFOR I 12"): the set of normalised lines, only
    for lines that carry a page-ish token (a digit, '#', '|', 'Form 10-K', 'Annual Report') so a
    recurring sub-heading ("Overview") is not mistaken for one."""
    counts = {}
    for line in text.split("\n"):
        if len(line) > 120 or len(line.split()) > 12:
            continue
        k = _norm_header(line)
        if len(k) >= 6:
            counts[k] = counts.get(k, 0) + 1
    return {k for k, n in counts.items()
            if n >= min_count and re.search(r"\d|#|\||form\s+(?:10-k|20-f)|annual\s+report", k)}


ITEM_LINE = r"(?i)^(?:part\s+i\b\W*)?items?\s*\d{1,2}\s*(?:\(?[a-d]\)?)?\s*(?:(?:and|&)\s*\d{1,2})?\s*[.:\-–—]?\s*"


def _running_header(line, headers=()):
    """Page furniture that can sit anywhere in a section: page numbers, "Table of Contents", "PART I",
    "Index" / "Page" column labels, a repeat of the Item 1 heading ("ITEM 1. BUSINESS", "Item 1."),
    and the document's recurring page headers / footers."""
    if re.fullmatch(r"(?i)\d{1,3}|[ivxlc]{1,6}|page\s+\d+|page|index|index\s+to\s+business|table\s+of\s+contents|contents"
                    r"|part\s+[iv]{1,3}\.?|description", line):
        return True
    if re.match(r"(?i)^(?:part\s+i\b\W*)?items?\s*1\s*(?:(?:and|&)\s*2)?\s*[.:\-–—]?\s*(?:business\b(?:\s+and\s+properties)?[\s.:]*(?:\(continued\))?)?$", line):
        return True
    if headers and len(line) <= 120 and _norm_header(line) in headers:
        return True
    return False


def _section_body(body, stop_re=None, headers=(), min_prose=300, max_skip=2500):
    """The prose of a section. Between the item heading and the first line that is itself running
    prose (_prose_line), everything is skipped: sub-headings ("Overview", "General Business
    Description"), a sub-section index with its page numbers (Prudential, MetLife, The Hartford),
    page furniture, a leading forward-looking-statements / read-in-conjunction paragraph (Waste
    Connections, Cboe) and leading definitional / navigational sentences (PREAMBLE: Yum! Brands' "referred
    to herein as ... principal executive offices ... website", Arch Capital's "As used in this report ... We
    refer you to Item 1A"), which also never count toward `min_prose`. If the next item label (`stop_re`) or more than `max_skip` characters come
    before any prose, or the skipped lines carry page ranges ("28-29", "68-77"), this occurrence is not
    the section (a cross-reference sheet: M&T Bank, Gold Fields' 20-F guide) -> None.
    Page furniture is dropped throughout, and the prose stops at the next sub-heading once at least
    `min_prose` characters have been collected."""
    kept, size, skipped, ranges = [], 0, 0, 0
    lines = [re.sub(r"^[\s.:;,\-–—|]+", "", raw.strip()) for raw in body.split("\n")]  # "BUSINESS." leaves a lone "."
    lines = [ln for ln in lines if ln and not _running_header(ln, headers)]
    for i, line in enumerate(lines):
        if not kept:
            if stop_re and re.match(r"(?:" + stop_re + r")", line, re.I):
                return None
            # a leading run of definitional / navigational sentences (Yum! Brands, Arch Capital) is not business prose
            rest = _strip_preamble(line)
            if rest != line:
                skipped += len(line) - len(rest) + 1
                if skipped > max_skip:
                    return None
                if not rest:
                    continue
                lines[i] = line = rest
            # a sentence the document broke across two lines ("... services to the energy\nindustry.") is judged whole
            probe = line if re.search(SENTENCE_END, line) or i + 1 >= len(lines) else line + " " + lines[i + 1]
            if _prose_line(probe) and len(re.findall(WORD_RE, line)) >= 6 and not re.search(BOILERPLATE, probe):
                kept.append(line)
                size += _substance(line)
                continue
            skipped += len(line) + 1
            ranges += len(re.findall(r"\b\d{1,3}\s*[-–]\s*\d{1,3}\b", line))
            if skipped > max_skip or ranges >= 2:
                return None
            continue
        if _heading_like(line):
            if size >= min_prose:
                break
            continue   # a sub-heading between two paragraphs ("Overview of Business", "CECONY") is not prose
        kept.append(line)
        size += _substance(line)
    return "\n".join(kept) or None


def _reads_as_prose(body):
    """A genuine prose run: a sentence of >= 12 words, at least two sentences (unless the section is
    that short), mostly lower-case words and few digits / page ranges in the first 700 characters (a
    cross-reference table, a TOC or an index of sub-headings fails)."""
    if not body:
        return False
    head = body[:700]
    words = re.findall(WORD_RE, head)
    if not words or not _has_sentence(head):
        return False
    sentences = len(re.findall(SENTENCE_END, head))
    lower = sum(1 for w in words if w[0].islower())
    digits = sum(c.isdigit() for c in head)
    return (sentences >= 2 or len(head) < 300) and lower >= 0.5 * len(words) and digits <= 0.1 * len(head) \
        and len(re.findall(r"\b\d{1,3}\s*[-–]\s*\d{1,3}\b", head)) < 3


def _section_prose(text, heading_re, toc_followers_re, lookahead=600, end_re=None, stop_re=None, headers=()):
    """First occurrence of a heading (at line start) that is NOT the table of contents and whose body
    reads as prose. The TOC occurrence is followed within `lookahead` characters by another item label
    with no sentence in between (page numbers, sub-item labels, an index of sub-headings); a
    cross-reference sheet or index reaches the next item label (`stop_re`) before any prose line.
    Returns (prose, heading) with the matched heading text, or (None, None)."""
    for m in re.finditer(r"(?im)^[ \t]*" + heading_re, text):
        after = text[m.end():m.end() + lookahead]
        if _is_toc_occurrence(after, toc_followers_re):
            continue
        body = text[m.end():m.end() + 20000]
        if end_re:
            e = re.search(end_re, body, re.I | re.M)
            if e:
                body = body[:e.start()]
        body = _section_body(body, stop_re=stop_re or toc_followers_re, headers=headers)
        if not _reads_as_prose(body):
            continue
        prose = re.sub(r"\s+", " ", body).strip()
        if len(prose) >= 40:
            return prose, m.group(0)
    return None, None


# "Item 1. Business", "ITEM 1.\nBUSINESS.", "Part I. Item 1. Business" (Expedia, one line), "Part I - Item 1. Business"
# (The Hartford), and the oil & gas layout "Items 1 and 2. Business and Properties" (Devon, Diamondback)
ITEM1_HEADING = (r"(?:part\s+i\b\s*[.:\-–—]?\s*)?items?\s*1\s*(?:(?:and|&)\s*2\s*)?\.?\s*[\-–—:]?\s*\n?\s*"
                 r"business\b(?:\s+and\s+properties\b)?[ \t]*[.:]?")
# "Item 1A", "Item 1(a)" (Halliburton), "Item 2": the labels that follow the Item 1 heading in a table of contents
ITEM1_TOC = r"item\s*1\s*\(?[a-c]\)?(?![a-z0-9])|item\s*2(?![a-z0-9])"
ITEM1_END = r"^[ \t]*item\s*1\s*\(?a\)?\s*\.?\s*[\-–—:]?\s*\n?\s*risk\s+factors\b"
# "Item 4.B Business Overview", "B. Business Overview", "(b) Business overview"
ITEM4B_HEADING = r"(?:item\s*4\s*\.?\s*)?(?:\(?b\)?\s*\.?\s*[\-–—:]?\s*\n?\s*)?business\s+overview\b[ \t]*[.:]?"
ITEM4B_STOP = r"item\s*4\s*\.?\s*c\b|item\s*5\b|\(c\)\s|c\.\s+organi[sz]ational"
ITEM4_HEADING = r"item\s*4\s*\.?\s*[\-–—:]?\s*\n?\s*information\s+on\s+the\s+company\b[ \t]*[.:]?"
ITEM4_TOC = r"item\s*4\s*\.?\s*[a-d]\b|item\s*5\b|^\s*[a-d]\s*\.\s+[a-z]"
ITEM4_STOP = r"item\s*5\b"
# Integrated-report 20-Fs (Gold Fields: the annual report + a Form 20-F cross-reference guide, no
# "Item 4" heading at all) carry the business overview under a bare "Overview" heading.
OVERVIEW_HEADING = r"(?:business\s+|group\s+|company\s+)?overview\s*[.:]?[ \t]*$"


def _overview_prose(text, entity, headers=()):
    """A standalone "Overview" heading whose first 400 characters name the registrant and read as
    a sentence; the first such wins. Returns (prose, kind) like _section_prose."""
    name = re.sub(r"(?i)\b(ltd|limited|plc|inc|corp|corporation|co|company|sa|nv|ag|holdings?)\b\.?", "", str(entity or "")).strip()
    name = re.split(r"[,(]", name)[0].strip()
    if len(name) < 3:
        return None, None
    name_re = re.escape(" ".join(name.split()[:2])).replace(r"\ ", r"\s+")
    for m in re.finditer(r"(?im)^[ \t]*" + OVERVIEW_HEADING, text):
        head = text[m.end():m.end() + 400]
        if re.search(r"(?i)\b" + name_re + r"\b", head) and re.search(r"(?i)\b(?:is|are|was|operates|produces|provides|has)\b", head) \
                and re.search(r"[.!?]\s", head):
            body = _section_body(text[m.end():m.end() + 20000], headers=headers)
            if not _reads_as_prose(body):
                continue
            prose = re.sub(r"\s+", " ", body).strip()
            if len(prose) >= 40:
                return prose, "section"
    return None, None


def extract_item1(text, form="10-K", entity=None):
    """The Item 1 Business opening prose of a 10-K (Item 4.B / Item 4 of a 20-F), <= 1,500 chars
    ending at a sentence boundary. Returns (text | None, note)."""
    if not text:
        return None, "empty document"
    headers = _repeated_headers(text)
    if form == "20-F":
        prose, kind = _section_prose(text, ITEM4B_HEADING, ITEM4B_STOP, lookahead=200, headers=headers)
        label = "20-F Item 4.B Business Overview"
        if not prose:
            prose, kind = _section_prose(text, ITEM4_HEADING, ITEM4_TOC, stop_re=ITEM4_STOP, headers=headers)
            label = "20-F Item 4 Information on the Company"
        if not prose:
            prose, kind = _overview_prose(text, entity, headers=headers)
            label = "20-F Overview section (integrated annual report without an Item 4 heading)"
        if not prose:
            label = "20-F Item 4 Information on the Company / Overview"
    elif form == "40-F":
        return None, "40-F primary document is a wrapper; no Item 1 Business section"
    else:
        prose, kind = _section_prose(text, ITEM1_HEADING, ITEM1_TOC, end_re=ITEM1_END, headers=headers)
        label = "10-K Item 1 Business"
        if prose and re.search(r"(?i)items?\s*1\s*(?:and|&)\s*2", kind or ""):
            label = "10-K Items 1 and 2 Business and Properties"
    if not prose:
        return None, f"no {label} section found outside the table of contents"
    return _cut_at_sentence(prose), label


EMP_NOUN = r"(?:employees|team\s+members|people|persons|associates|staff|workers|colleagues|individuals)"
EMP_DATE = r"(?:[A-Za-z]{3,9}\.?\s+\d{1,2},?\s+\d{4})|(?:\d{1,2}\s+[A-Za-z]{3,9},?\s+\d{4})|(?:\d{1,2}/\d{1,2}/\d{4})"
# the proper-noun subject is case-SENSITIVE ((?-i:...)) so that under the pattern's (?i) flag it cannot
# swallow the tail of the previous sentence ("its culture and performance. Huntington had ...")
# ... and it stays on one line ([ \t]+, never a newline) so a heading above the sentence cannot become its subject.
# The "and its (consolidated) subsidiaries" suffix applies to EVERY subject ("the Company and its subsidiaries had"
# — United Airlines, Yum! Brands; "Con Edison and its subsidiaries had"), so the alternation is wrapped before it.
EMP_SUBJ = (r"(?P<subj>(?:we|the\s+company|the\s+group|the\s+bank|our\s+(?:total\s+|global\s+|worldwide\s+)?(?:workforce|headcount)"
            r"|(?-i:[A-Z][A-Za-z&'\-]*(?:,?[ \t]+[A-Z][A-Za-z&.'\-]*){0,4}(?:[ \t]+team)?))"
            r"(?:,?[ \t]+(?:and|together[ \t]+with)[ \t]+its[ \t]+(?:consolidated[ \t]+)?subsidiaries,?)?)")
# "had", "employed", present tense "employ(s)" with an adverb ("we directly employ" — Coupang), the workforce verbs
# ("our total workforce consisted of" — Teledyne; "The Steel Dynamics team consisted of"), "we have a team of" (Expedia).
# "individuals" counts as the noun only with a form of "employ" ("we employed 8,804 individuals" — W. R. Berkley).
EMP_VERB = (r"(?:(?:directly[ \t]+|collectively[ \t]+)?(?:(?:have|has|had)[ \t]+a[ \t]+(?:global[ \t]+)?(?:team|workforce)[ \t]+of"
            r"|had|employed|employs?|have[ \t]+had|have|has"
            r"|consisted[ \t]+of|consists[ \t]+of|totaled|totalled|comprised|was|were))")
EMP_QUAL = r"(?:a\s+total\s+of\s+|approximately\s+|about\s+|roughly\s+|more\s+than\s+|over\s+|nearly\s+|an\s+aggregate\s+of\s+|an\s+average\s+of\s+)*"
EMP_NUMTOK = r"(?:\d{1,3}(?:,\d{3})+|\d{2,7})"
EMP_NUM = r"(?P<n>" + EMP_NUMTOK + r")\s+"
EMP_ADJ = r"(?:(?:full|part|full-|part-|full-time|part-time|full-\s*and\s+part-time|and|or|time|total|regular|permanent|global|worldwide|average|equivalent|hourly|salaried|active|direct)\s+){0,6}"
EMP_YEAR = r"(?:19|20)\d{2}"
# form 1: "As of December 31, 2025, we had approximately 1,900 full-time employees"
EMP_SENTENCE = (r"(?i)\b(?:as\s+of|at|on)\s+(?P<date>" + EMP_DATE + r")\s*,?\s*" + EMP_SUBJ + r"\s+" + EMP_VERB + r"\s+"
                + EMP_QUAL + EMP_NUM + EMP_ADJ + EMP_NOUN)
# form 2: the date AFTER the count — "Huntington had 20,424 average full-time equivalent colleagues during 2025" (a
# year-average), "Northern Trust employed approximately 23,800 full-time equivalent employees as of December 31, 2025",
# "We had approximately 12,100 employees at December 31, 2025" (EchoStar)
EMP_SENTENCE_2 = (r"(?i)\b" + EMP_SUBJ + r"\s+" + EMP_VERB + r"\s+" + EMP_QUAL + EMP_NUM + EMP_ADJ + EMP_NOUN
                  + r"\s+(?:during|in|for|throughout|at\s+the\s+end\s+of|as\s+of|at|on)\s+(?:fiscal\s+(?:year\s+)?)?(?P<date>(?:" + EMP_DATE + r")|" + EMP_YEAR + r")\b")
# form 3: a headcount bullet with the prior-year comparative, the integrated-report style
# ("• 6,628 employees (2024: 6,560) and 16,607 business partners"); the comparative is what marks
# it as the headcount line rather than a figure in passing
EMP_SENTENCE_3 = (r"(?i)(?<![\d,.$])" + EMP_NUM + EMP_ADJ + EMP_NOUN + r"\s*\(\s*(?:fy\s*)?(?P<date>" + EMP_YEAR + r")\s*:\s*\d{1,3}(?:,\d{3})*\s*\)")
# forms 4 and 5: the multi-year sentence most foreign private issuers use, with the dates first ("As of December 31,
# 2023, 2024 and 2025, we had a total of 517,124, 570,895 and 776,682 employees, respectively" — JD; "As of June 30,
# 2026 and 2025, we had approximately 55,000 and 57,000 employees worldwide, respectively" — Estée Lauder, years in
# DESCENDING order) or last ("We had approximately 39,800, 35,900 and 33,500 full time employees as of December 31,
# 2023, 2024 and 2025, respectively" — Baidu). The years and the counts are paired by position and the LATEST year's
# count is the headcount, whatever the order.
EMP_YEARS = r"(?P<date>" + EMP_DATE + r")(?P<years>(?:\s*,\s*" + EMP_YEAR + r")*\s*,?\s*(?:and|&)\s+" + EMP_YEAR + r")\b"
EMP_NUMS = r"(?P<nums>" + EMP_NUMTOK + r"(?:\s*,\s*" + EMP_NUMTOK + r")*\s*,?\s*(?:and|&)\s+" + EMP_NUMTOK + r")\s+"
EMP_SENTENCE_4 = (r"(?i)\b(?:as\s+of|at|on)\s+" + EMP_YEARS + r"\s*,?\s*" + EMP_SUBJ + r"\s+" + EMP_VERB + r"\s+" + EMP_QUAL
                  + EMP_NUMS + EMP_ADJ + EMP_NOUN)
EMP_SENTENCE_5 = (r"(?i)\b" + EMP_SUBJ + r"\s+" + EMP_VERB + r"\s+" + EMP_QUAL + EMP_NUMS + EMP_ADJ + EMP_NOUN
                  + r"\s+(?:as\s+of|at|on)\s+" + EMP_YEARS)
# form 6: the year-end phrasing "We ended the year 2025 with 1,762 full-time employees" (Diamondback), dated by the
# filing's fiscal period end when it falls in that year, else the bare year
EMP_SENTENCE_6 = (r"(?i)\b" + EMP_SUBJ + r"\s+ended\s+(?:the\s+)?(?:fiscal\s+)?(?:year\s+)?(?P<date>" + EMP_YEAR + r")\s+with\s+"
                  + EMP_QUAL + EMP_NUM + EMP_ADJ + EMP_NOUN)
EMP_QUALIFIER = r"^,?\s*(?:or|representing|which\s+(?:is|was|represents)|who\s+(?:are|were))\b[^.]{0,40}(?:%|percent)|^[^.,;]{0,40}\b(?:involved|engaged)\s+in\b|^[^.,;]{0,40}\bdedicated\s+to\b|^\s+in\s+(?:our|its|the)\s+[a-z ]{0,30}(?:department|team|organization|function|division|segment)"
# what follows the count decides whether it is the total:
# - a total with its parts: "898 employees, comprised of 876 full-time and 22 part-time" (AppLovin), "24,214 active
#   employees, including 11,347 commercial truck drivers ... with 20,471 employees in the U.S." (Waste Connections),
#   "55,000 and 57,000 employees worldwide, respectively, including approximately 35,000 demonstrators" (Estée Lauder)
EMP_TOTAL_MARK = (r"(?i)^\s*(?:worldwide|globally|in\s+total|in\s+the\s+aggregate|around\s+the\s+(?:world|globe))?\s*,?\s*(?:respectively\s*,?\s*)?"
                  r"(?:\(|including\b|of\s+whom\b|of\s+which\b|comprised\s+of\b|consisting\s+of\b|composed\s+of\b|which\s+includes?\b"
                  r"|which\s+included\b|with\b|all\b|excluding\b|which\s+excludes?\b|not\s+including\b)")
# - a subset: the count is followed directly by one function or place — "18,600 employees in research and development,
#   6,400 employees in sales and marketing" (Baidu), "12,000 employees in the United States, 3,000 in Europe" — unless the
#   same clause says it is the whole workforce ("in locations around the world"); "in 38 countries" / "in over 40
#   countries" is the whole workforce's spread, not a subset
EMP_SUBSET_TAIL = (r"(?i)^\s+(?:in|within|outside(?:\s+of)?|based\s+in|located\s+in)\s+"
                   r"(?!(?:more\s+than\s+|over\s+|approximately\s+|about\s+|nearly\s+|roughly\s+)?\d)(?!(?:total|the\s+aggregate|aggregate|all|(?:the\s+)?following|various|multiple|several|many)\b)")
EMP_WHOLE = (r"(?i)\b(?:worldwide|globally|in\s+total|across|around\s+the\s+(?:world|globe)|collectively|combined|in\s+all|internationally|consolidated"
             r"|and\s+abroad|other\s+countries)\b")
# a second count in the same sentence: "N <noun>" or a bare "N in <place>" ("3,000 in Europe and 1,500 in Asia")
EMP_OTHER_COUNT = (r"(?<![\d,.$])" + EMP_NUMTOK + r"\s+(?:(?:[a-z\-]+\s+){0,3}" + EMP_NOUN
                   + r"\b|(?:in|outside|within|based\s+in|located\s+in)\b)")
# a second count of labour that is not employees: "1,233 contract workers", "5,678 independent contractors"
EMP_NON_EMPLOYEE = (r"(?i)" + EMP_NUMTOK + r"\s+(?:[a-z\-]+\s+){0,2}?(?:contract|contracted|contractors?|independent|agency|consultants?"
                    r"|outsourced|third[\s\-]party)\b")
EMP_COMPARATIVE =r"(?i)\b(?:compared|from|versus|vs\.?|up|down|increased?|decreased?|prior|previous|last\s+year|a\s+year\s+ago)\b"
EMP_ANCHOR = r"(?i)human\s+capital|employees\s+and\s+human|our\s+(?:employees|people|workforce|team)\b|^\s*employees\s*$"
# "people" / "persons" / "individuals" / "associates" / "colleagues" / "workers" / "staff" are a workforce only in the
# Human Capital / Employees passage or with a form of "employ" ("employed approximately 49,000 persons" — Yum! Brands);
# elsewhere "we had 850,000 people enrolled in our programs" is a count of customers
EMP_WEAK_NOUN = r"(?i)(?:people|persons|individuals|associates|colleagues|workers|staff)$"
# what follows the noun says it is not the workforce: "people enrolled in", "persons serving as executive officers"
EMP_NOT_WORKFORCE = (r"(?i)^\s*(?:,\s*)?(?:enrolled|using|use|used|served|serving|who\s+(?:use|used|are\s+enrolled|serve|served)"
                     r"|on\s+(?:our|its|the)\s+(?:board|waiting)|holders?\b|of\s+record\b|as\s+(?:customers|members|patients|clients"
                     r"|executive\s+officers|directors|officers)|in\s+(?:our|its)\s+(?:programs?|plans?|networks?|communities|care))")
EMP_FIRST_PERSON = ("we", "the company", "the group", "the bank")


def _entity_words(entity):
    """The distinctive words of the EDGAR registrant name ("HUNTINGTON BANCSHARES INC/MD" -> {huntington, bancshares})."""
    name = re.sub(r"(?i)\b(?:ltd|limited|plc|inc|corp|corporation|co|company|sa|nv|ag|holdings?|group|the|and|of|de|new)\b\.?", " ", str(entity or ""))
    return {w.lower() for w in re.findall(r"[A-Za-z][A-Za-z&'\-]+", name) if len(w) >= 3}


def _subject_rank(subj, entity_words):
    """0 for the registrant itself ("we", "the Company", "our workforce", or a proper noun that shares a word with the
    EDGAR name, with or without "and its subsidiaries"), 1 for any other proper noun (a subsidiary, a hurricane): a
    first-person sentence always wins over it."""
    s = re.sub(r"\s+", " ", str(subj or "")).strip().lower()
    s = re.sub(r",?\s+(?:and|together\s+with)\s+its\s+(?:consolidated\s+)?subsidiaries,?$", "", s).strip()
    if not s or s in EMP_FIRST_PERSON or s.startswith("our "):
        return 0
    words = {w for w in re.findall(r"[a-z][a-z&'\-]+", s) if len(w) >= 3}
    return 0 if entity_words and words & entity_words else 1


def _glued_heading(prefix):
    """A run-on heading in front of the sentence ("Employees and Human Capital Resources As of ..."): short, no
    punctuation, every word capitalised (or a connective)."""
    words = prefix.split()
    return 0 < len(words) <= 8 and len(prefix) <= 80 and not re.search(r"[.!?;:,()]", prefix) and \
        all(w[0].isupper() or w.lower() in ("and", "of", "the", "&", "our", "to", "for", "in", "on") for w in words)


ABBREVIATION_END = r"(?:\bInc|\bCo|\bCorp|\bLtd|\bNo|\bJr|\bSr|\bSt|\bU\.S|\bU\.K|\bN\.A|\bS\.A|\bL\.P|\bi\.e|\be\.g|\bMr|\bMrs|\bMs|\bDr)$"


def _sentence_end(text, end, span=600):
    """Index just past the first sentence end after `end`. A period closing an abbreviation ("U.S.", "Inc.")
    ends the sentence only when the next word is capitalised ("... all located in the U.S. Employee Safety")
    and not when it runs on in lower case ("various U.S. labor organizations"). None when there is none."""
    for m in re.finditer(r"[.!?][\"'”)]?(?:\s|$)|:[ \t]*\n", text[end:end + span]):   # "... in the following locations:\n<table>"
        k = end + m.start()
        if re.search(ABBREVIATION_END, text[max(0, k - 6):k]):
            nxt = text[end + m.end():end + m.end() + 1]
            if nxt and not nxt.isupper():
                continue
        return end + m.end()
    return None


def _sentence_bounds(text, start, end):
    """(left, right) of the sentence holding text[start:end]: from the previous sentence end / line break to the next
    sentence end that is not an abbreviation ("U.S.", "Inc."). A heading glued in front of the match is left out, but
    only text BEFORE the match is ever trimmed, so a sentence whose date sits at its end ("Northern Trust employed
    approximately 23,800 ... as of December 31, 2025.") keeps its subject."""
    left = max(text.rfind(". ", 0, start), text.rfind("\n", 0, start), text.rfind("! ", 0, start), text.rfind("? ", 0, start))
    left = left + 2 if left >= 0 and text[left] != "\n" else (left + 1 if left >= 0 else 0)
    right = _sentence_end(text, end)
    right = right if right is not None else min(len(text), end + 300)
    prefix = re.sub(r"\s+", " ", text[left:start]).strip().rstrip(":").strip()
    if prefix and _glued_heading(prefix):
        left = start
    return left, right


def _sentence_around(text, start, end):
    left, right = _sentence_bounds(text, start, end)
    return re.sub(r"\s+", " ", text[left:right]).strip()


def _bullet_around(text, start, end):
    """The one bullet (or line) holding a form-3 headcount: from the previous bullet mark / line
    break to the next bullet mark / line break / sentence end."""
    marks = ("•", "\n", "·", "▪", "■")
    left = max([text.rfind(mk, 0, start) for mk in marks] + [text.rfind(". ", 0, start) + 1, 0])
    nxt = [text.find(mk, end) for mk in marks]
    m = re.search(r"[.!?][\"'”)]?(?:\s|$)", text[end:end + 400])
    nxt.append(end + m.end() if m else -1)
    nxt = [n for n in nxt if n >= 0]
    right = min(nxt) if nxt else min(len(text), end + 200)
    return re.sub(r"\s+", " ", text[left:right]).strip(" •·▪■\t\n")


def _multi_year(m):
    """(count, as_of) of a form-4/5 match: the counts and the years paired by position, the latest year's count, dated
    with the stated month/day; None when the two lists differ in length or a year repeats."""
    years = [int(re.findall(EMP_YEAR, m.group("date"))[-1])] + [int(y) for y in re.findall(EMP_YEAR, m.group("years"))]
    nums = [int(x.replace(",", "")) for x in re.findall(EMP_NUMTOK, m.group("nums"))]
    if len(years) != len(nums) or len(set(years)) != len(years):
        return None
    i = max(range(len(years)), key=lambda k: years[k])
    iso = iso_from_text_date(m.group("date"))
    if iso is None:
        return nums[i], None   # the stated month/day cannot be read: the caller rejects the sentence
    try:
        return nums[i], datetime.date(years[i], int(iso[5:7]), int(iso[8:10])).isoformat()
    except ValueError:   # "February 29, 2024 and 2025"
        return nums[i], None


def extract_employees(text, period=None, entity=None, notes=None):
    """{count, as_of, evidence[, basis]} from the Human Capital / Employees passage; None when no headcount
    sentence exists (never guessed). Filed forms: (1) "As of <date>, we had N employees"; (2) the date after
    the count ("<Name> had N average full-time equivalent colleagues during 2025", "... N employees as of
    <date>", "... N employees at <date>"); (3) the integrated-report bullet "N employees (2024: N)", dated by
    `period` (the filing's fiscal period end) when given, else by the year after the comparative; (4)/(5) the
    multi-year sentence, dates first or last, paired by position (the latest year's count).
    A count is the total only when nothing in its sentence makes it a part: a count followed directly by one
    function or place ("18,600 employees in research and development", "12,000 employees in the United
    States, 3,000 in Europe") is a subset, and a sentence that gives the registrant's count and another
    entity's ("PG&E Corporation had 10 employees, and the Utility had approximately 29,000") has no filed
    total; both are rejected and, when nothing else is found, described in `notes` (a list) with the
    sentence as evidence. A total listed with its parts ("898 employees, comprised of 876 full-time and 22
    part-time") is the total. Ranking: the registrant ("we", "the Company", its own name — `entity`) beats any
    other proper noun, a dated point-in-time count beats a year-average which beats the bullet, then
    proximity to the Human Capital heading, then the latest date, then position. A per-type split with the
    noun repeated and no total ("N full-time employees and M part-time employees") is a breakdown too;
    "people" / "persons" / "associates" ... count only near the heading or with "employ", never when followed
    by "enrolled" / "serving as ..."; a date that is not a calendar date rejects the sentence. A form-2 sentence whose subject
    is a proper noun other than the registrant is dropped when `entity` is known ("Hurricane Milton had 150
    workers in 2024 displaced")."""
    if not text:
        return None
    anchors = [m.start() for m in re.finditer(EMP_ANCHOR, text, re.M)]
    entity_words = _entity_words(entity)
    best, rejected = None, []
    for form, pattern in ((1, EMP_SENTENCE), (4, EMP_SENTENCE_4), (5, EMP_SENTENCE_5), (6, EMP_SENTENCE_6), (2, EMP_SENTENCE_2), (3, EMP_SENTENCE_3)):
        for m in re.finditer(pattern, text):
            gd = m.groupdict()
            n_start = m.start("n") if gd.get("n") else m.start("nums")
            if form == 3:
                sent, right = _bullet_around(text, m.start(), m.end()), m.end()
            else:
                left, right = _sentence_bounds(text, m.start(), m.end())
                sent = re.sub(r"\s+", " ", text[left:right]).strip()
            after = text[m.end():m.end() + 120]
            before = text[m.start():n_start]
            # a percentage or a department qualifier attached to the number means it is a subset, not the headcount
            if re.search(EMP_QUALIFIER, after, re.I) or "%" in before or re.search(r"(?i)\bpercent\b", before):
                continue
            if form in (4, 5):
                pair = _multi_year(m)
                if pair is None:
                    rejected.append(f"a multi-year headcount sentence whose years and counts do not pair up: \"{sent}\"")
                    continue
                count, as_of = pair
            else:
                count = int(m.group("n").replace(",", ""))
                if form == 3:
                    as_of = period or str(int(m.group("date")) + 1)
                elif form == 6:
                    as_of = period if period and str(period).startswith(m.group("date")) else m.group("date")
                elif re.fullmatch(EMP_YEAR, m.group("date")):
                    as_of = m.group("date")   # form 2 "... during 2025": the year itself
                else:
                    as_of = iso_from_text_date(m.group("date"))
            if as_of is None:
                # "February 30, 2026", an unknown month spelling: the stated date cannot be read, so the count is not
                # published with the raw text as its as-of (the contract wants an ISO date when the sentence has one)
                rejected.append(f"a headcount sentence whose date cannot be read as a calendar date: \"{sent}\"")
                continue
            noun_end = text[m.start():m.end()]
            if count < 10 or (re.search(r"(?i)individuals$", noun_end) and not re.search(r"(?i)\bemploy", noun_end)):
                continue
            if re.match(EMP_NOT_WORKFORCE, text[m.end():m.end() + 80]):
                continue   # "850,000 people enrolled in our programs", "14 persons serving as executive officers"
            near = any(0 <= m.start() - a <= 6000 for a in anchors)
            if form != 3 and re.search(EMP_WEAK_NOUN, noun_end) and not near and not re.search(r"(?i)\bemploy", noun_end):
                continue   # "we had 850,000 people ..." outside the Human Capital passage is not a headcount
            subj_rank = _subject_rank(gd.get("subj"), entity_words) if form != 3 else 0
            if form in (2, 6) and subj_rank and entity_words:
                continue   # "<Other Name> had N workers in 2024" without an as-of date is not the registrant's headcount
            if form != 3:
                tail = text[m.end():max(right, m.end())]
                if not re.match(EMP_TOTAL_MARK, tail):
                    other = re.search(EMP_OTHER_COUNT, tail)
                    comparative = bool(other and re.search(EMP_COMPARATIVE, tail[:other.start()]))
                    # the "whole workforce" words count only before a second count: in "1,100 employees in the United
                    # States and 300 employees internationally" the "internationally" belongs to the second part
                    clause = re.split(r"[,;.(]", tail[:other.start()] if other else tail, maxsplit=1)[0]
                    if re.match(EMP_SUBSET_TAIL, tail) and not re.search(EMP_WHOLE, clause):
                        rejected.append(("a per-function / per-location breakdown with no filed total" if other and not comparative
                                         else "a single function's or location's headcount, not the company total") + f": \"{sent}\"")
                        continue
                    if other and not comparative and re.search(r"(?i)\b(?:had|employed|employs|has|have)\s+" + EMP_QUAL + r"$", tail[:other.start()]):
                        rejected.append(f"separate headcounts for the registrant and another entity with no filed total: \"{sent}\"")
                        continue
                    if other and not comparative and not re.search(EMP_WHOLE, tail[:other.start()]) \
                            and not re.match(EMP_NON_EMPLOYEE, tail[other.start():]):
                        # "17,550 full-time employees and 2,045 part-time employees", "4,000 salaried employees and 6,000
                        # hourly employees", "2,000 employees domestically and 500 employees internationally": the first
                        # part is not the headcount and the filing states no total (summing is not done here). Not a
                        # breakdown: the first count said to be the whole ("130,301 people worldwide and 1,233 contract
                        # workers" — Chipotle) or a second count of non-employee labour (contractors, consultants)
                        rejected.append(f"a per-type / per-location breakdown with no filed total: \"{sent}\"")
                        continue
            window = text[m.start():m.end() + 40]
            average = bool(re.search(r"(?i)\baverage\b", window))
            fte = bool(re.search(r"(?i)full[\-\s]time[\-\s]equivalent|\bFTEs?\b", window))
            if form == 3:
                form_rank = 2
            elif form in (2, 6) and (average or len(as_of) != 10):
                form_rank = 1
            else:
                form_rank = 0
            date_key = -int((as_of if len(as_of) == 10 else str(as_of)[:4] + "-12-31").replace("-", "")) if re.match(r"\d{4}", str(as_of)) else 0
            # proximity to the Human Capital / Employees passage ranks BEFORE the date: a later-dated "we had N ..."
            # elsewhere in the document must not beat the headcount under the heading
            key = (subj_rank, form_rank, 0 if near else 1, date_key, m.start())
            if best is None or key < best[0]:
                rec = {"count": count, "as_of": as_of, "evidence": sent}
                if form == 3:
                    rec["basis"] = "headcount stated with the prior-year comparative; as-of = the filing's fiscal period end"
                elif average:
                    rec["basis"] = "average full-time equivalent for the period" if fte else "average headcount for the period"
                elif fte:
                    rec["basis"] = "full-time equivalent as of the stated date"
                elif form == 6:
                    rec["basis"] = "year-end headcount; as-of = the filing's fiscal period end" if len(as_of) == 10 else "year-end headcount (no day given)"
                elif len(as_of) != 10:
                    rec["basis"] = "headcount stated for the year (no day given)"
                best = (key, rec)
    if best is None and notes is not None:
        notes.extend(dict.fromkeys(rejected))
    return best[1] if best else None


# ---------------------------------------------------------------------------
# EDGAR submissions -> about / filings / first filing
def map_items(items):
    """'2.02,9.01' -> ([codes], 'Results of operations'). 9.01 (exhibits) is listed but not described
    unless it is the only item; unknown codes read 'Item X.XX'."""
    codes = [c.strip() for c in re.split(r"[,\s]+", str(items or "")) if c.strip()]
    described = [ITEM_DESCRIPTIONS.get(c, f"Item {c}") for c in codes if c != "9.01"] or \
                ([ITEM_DESCRIPTIONS["9.01"]] if "9.01" in codes else [])
    return codes, "; ".join(described)


def _recent_rows(sub):
    rec = ((sub or {}).get("filings") or {}).get("recent") or {}
    keys = ("form", "filingDate", "reportDate", "items", "accessionNumber", "primaryDocument", "primaryDocDescription")
    cols = {k: rec.get(k) or [] for k in keys}
    n = len(cols["form"])
    return [{k: (cols[k][i] if i < len(cols[k]) else None) for k in keys} for i in range(n)]


def filing_url(cik, accession, doc):
    acc = str(accession or "").replace("-", "")
    if not acc:
        return None
    if doc:
        return f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc}/{doc}"
    return f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc}/"


def build_filings(sub, cik, limit=FEED_LIMIT):
    out = []
    rows = _recent_rows(sub)
    rows.sort(key=lambda r: r.get("filingDate") or "", reverse=True)
    for r in rows:
        form = r.get("form") or ""
        base = form[:-2] if form.endswith("/A") else form
        if base not in FEED_FORMS:
            continue
        codes, desc = map_items(r.get("items")) if base == "8-K" else ([], FORM_DESCRIPTIONS.get(base, base))
        if form.endswith("/A"):
            desc = f"Amendment: {desc}" if desc else "Amendment"
        out.append({"form": form, "filed": r.get("filingDate"), "period": r.get("reportDate") or None,
                    "items": codes, "description": desc, "accession": r.get("accessionNumber"),
                    "url": filing_url(cik, r.get("accessionNumber"), r.get("primaryDocument"))})
        if len(out) >= limit:
            break
    return out


def latest_annual(sub, cik):
    """The newest 10-K / 20-F / 40-F row (amendments excluded) as {form, filed, period, accession, url}."""
    best = None
    for r in _recent_rows(sub):
        if r.get("form") in ANNUAL_FORMS and r.get("primaryDocument"):
            if best is None or (r.get("filingDate") or "") > (best.get("filingDate") or ""):
                best = r
    if not best:
        return None
    return {"form": best["form"], "filed": best.get("filingDate"), "period": best.get("reportDate") or None,
            "accession": best.get("accessionNumber"), "url": filing_url(cik, best.get("accessionNumber"), best.get("primaryDocument"))}


def newest_filing_date(sub):
    dates = [r.get("filingDate") for r in _recent_rows(sub) if r.get("filingDate")]
    return max(dates) if dates else None


# the forms that register or list a company's shares: their earliest filing is the IPO-date proxy. A private
# placement (Form D) or a confidential draft (DRS) comes earlier but is not a public registration.
REGISTRATION_FORMS = ("S-1", "F-1", "S-11", "10-12B", "10-12G", "20FR12B", "40FR12B", "8-A12B", "8-A12G", "424B1", "424B4")
# a company that filed periodic reports BEFORE its earliest registration form was already public (EDGAR starts in
# the 1990s, long after the IPO of a Kroger or a Huntington): its overall earliest filing is the better proxy
PERIODIC_FORMS = ("10-K", "10-K405", "10-KSB", "10-KSB405", "10-KT", "10-Q", "10-QSB", "10-QT", "8-K", "20-F", "40-F", "6-K", "DEF 14A")


def _base_form(form):
    f = str(form or "").strip().upper()
    return f[:-2] if f.endswith("/A") else f


def _form_key(form):
    """The base form with hyphens and spaces removed, so EDGAR's 1990s spellings match ("10QSB" == "10-QSB",
    "10KSB" == "10-KSB", "10-KT"); an amendment carries its base form."""
    return re.sub(r"[\s\-]", "", _base_form(form))


REGISTRATION_KEYS = {_form_key(f) for f in REGISTRATION_FORMS}
PERIODIC_KEYS = {_form_key(f) for f in PERIODIC_FORMS}


def first_filing(sub, fetch=edgar_json, warnings=None):
    """(date, form) of the company's first SEC filing: the earliest registration / listing form
    (REGISTRATION_FORMS) unless a periodic report precedes it, else the earliest filing of any form.
    Rows come from filings.recent plus the paginated files, fetched oldest first and stopped as soon
    as a registration form has been seen (one request for most names, none when `files` is empty)."""
    rows = [(r.get("form"), r.get("filingDate")) for r in _recent_rows(sub) if r.get("filingDate")]
    files = ((sub or {}).get("filings") or {}).get("files") or []
    files = sorted((f for f in files if isinstance(f, dict) and f.get("name")), key=lambda f: f.get("filingFrom") or "9999")
    for page_meta in files:
        try:
            page = fetch(f"https://data.sec.gov/submissions/{page_meta['name']}") or {}
            forms, dates = page.get("form") or [], page.get("filingDate") or []
            rows += [(forms[i] if i < len(forms) else None, d) for i, d in enumerate(dates) if d]
        except Exception as e:
            if warnings is not None:
                warnings.append(f"submissions page {page_meta['name']} unreadable ({e}); first filing date from the other pages only")
            if page_meta.get("filingFrom"):
                rows.append((None, page_meta["filingFrom"]))
        if any(_form_key(f) in REGISTRATION_KEYS for f, _ in rows):
            break
    if not rows:
        return None, None
    reg = [r for r in rows if _form_key(r[0]) in REGISTRATION_KEYS]
    if reg:
        first_reg = min(reg, key=lambda r: r[1])
        if not any(_form_key(f) in PERIODIC_KEYS and d < first_reg[1] for f, d in rows):
            return first_reg[1], first_reg[0]
    earliest = min(rows, key=lambda r: r[1])
    return earliest[1], earliest[0]


def earliest_filing_date(sub, fetch=edgar_json, warnings=None):
    """The date half of first_filing (kept for callers of the older name)."""
    return first_filing(sub, fetch=fetch, warnings=warnings)[0]


COVER_TAGS = (("EntityAddressAddressLine1", "line1"), ("EntityAddressAddressLine2", "line2"), ("EntityAddressAddressLine3", "line3"),
              ("EntityAddressCityOrTown", "city"), ("EntityAddressStateOrProvince", "state"), ("EntityAddressCountry", "country"),
              ("EntityAddressPostalZipCode", "zip"))


def cover_address(raw):
    """The principal executive office from the inline-XBRL cover of the annual document (the filed
    dei:EntityAddress* values). A filing with two registrants (Carnival Corporation in Miami and
    Carnival plc in Southampton) tags each under its own contextRef: the first city's context is
    the address and every field comes from that context only. Tags are stripped and a trailing
    comma dropped ("Columbus,"). None when the document carries no tagged city."""
    s = _decode(raw)
    keys = {tag: key for tag, key in COVER_TAGS}
    by_ctx, order = {}, []
    for m in re.finditer(r"(?is)<ix:nonnumeric\b([^>]*)>(.*?)</ix:nonnumeric\s*>", s):
        attrs, inner = m.group(1), m.group(2)
        name = re.search(r"\bname\s*=\s*[\"']dei:(EntityAddress[A-Za-z0-9]+)[\"']", attrs)
        if not name or name.group(1) not in keys:
            continue
        ctx = re.search(r"\bcontextRef\s*=\s*[\"']([^\"']*)[\"']", attrs, re.I)
        ctx = ctx.group(1) if ctx else ""
        v = html.unescape(re.sub(r"(?s)<[^>]+>", "", inner)).replace("\xa0", " ")
        v = re.sub(r"[,;:\s]+$", "", re.sub(r"\s+", " ", v).strip())
        if not v:
            continue
        if ctx not in by_ctx:
            by_ctx[ctx], order = {}, order + [ctx]
        by_ctx[ctx].setdefault(keys[name.group(1)], v)
    vals = next((by_ctx[c] for c in order if by_ctx[c].get("city")), None)
    if not vals:
        return None
    street = " ".join(vals[k] for k in ("line1", "line2", "line3") if vals.get(k)) or None
    return {"street": street, "city": vals["city"], "state": vals.get("state"), "zip": vals.get("zip"),
            "country": vals.get("country"), "source": "annual filing cover"}


def _title_city(city):
    """An all-caps city in readable case ("GOODLETTSVILLE" -> "Goodlettsville", "MCLEAN" -> "McLean",
    "ST. LOUIS" -> "St. Louis"); a city already in mixed case is left exactly as filed."""
    c = re.sub(r"\s+", " ", str(city or "")).strip()
    if not c or not c.isupper():
        return c
    t = c.title()
    t = re.sub(r"\bMc([a-z])", lambda m: "Mc" + m.group(1).upper(), t)
    return re.sub(r"(?<=[a-z])'S\b", "'s", t)


# a cover "city" that is a district / ward of a larger city (Baidu "Haidian District", JD "Daxing District", Nomura
# "Chuo-ku"): the submissions business city names the city proper
CITY_DISTRICT = r"(?i)\bdistrict\b|-ku$|\bku\b|\bward\b|\bborough\b|\bprefecture\b|\barrondissement\b|-gu$"


def headquarters(sub, cover=None):
    """(text, address): the annual filing's cover address when `cover` (cover_address) is given, else
    the EDGAR submissions business address; `address.source` says which. On the cover path:
    - an all-caps city is put in readable case (the filed spelling otherwise kept);
    - a city tag the filer cut short ("St. John'" — Fortis tags only part of "St. John's") or shorter than
      3 characters is replaced by the submissions business city (`address.city_source` says so);
    - a foreign cover (no state) whose city is a district ("Haidian District") or a part of the submissions
      city ("DAXING DISTRICT, BEIJING") also names the city proper from the submissions address, in
      `address.metro` (`address.metro_source` "EDGAR submissions"): "Haidian District, Beijing, The People's
      Republic of China"."""
    biz = ((sub or {}).get("addresses") or {}).get("business") or {}
    biz = biz if isinstance(biz, dict) else {}
    sub_city = _title_city(biz.get("city"))
    if isinstance(cover, dict) and cover.get("city"):
        address = dict(cover)
        city = _title_city(cover["city"])
        if (re.search(r"['’]$", city) or len(city) < 3) and sub_city:
            city, address["city_source"] = sub_city, "EDGAR submissions (the cover city tag is incomplete)"
        address["city"] = city
        parts = [city]
        if not cover.get("state") and sub_city and sub_city.lower() != city.lower():
            if re.search(CITY_DISTRICT, city) or city.lower() in sub_city.lower():
                metro = re.sub(r"(?i)" + re.escape(city), "", sub_city).strip(" ,;-")
                if len(metro) >= 3 and metro.lower() not in city.lower():
                    address["metro"], address["metro_source"] = metro, "EDGAR submissions"
                    parts.append(metro)
        parts.append(cover.get("state") or cover.get("country"))
        return ", ".join(x for x in parts if x), address
    if not (biz.get("city") or biz.get("street1")):
        return None, None
    city = sub_city
    state = str(biz.get("stateOrCountryDescription") or biz.get("stateOrCountry") or "").strip()
    text = ", ".join(x for x in (city, state) if x) or None
    return text, {"street": " ".join(str(biz.get(k) or "").strip() for k in ("street1", "street2")).strip() or None,
                  "city": city or None, "state": state or None, "zip": biz.get("zipCode") or None,
                  "country": None, "source": "EDGAR submissions"}


def build_about(sub, cik, nasdaq_profile, summary, description, employees, first_filing, cover=None, employees_unresolved=None):
    prof = nasdaq_profile if isinstance(nasdaq_profile, dict) else {}
    sdata = (summary or {}).get("summaryData") if isinstance(summary, dict) else None
    sdata = sdata if isinstance(sdata, dict) else {}

    def pv(d, k):
        v = d.get(k)
        v = v.get("value") if isinstance(v, dict) else v
        return (str(v).strip() or None) if v is not None else None

    hq_text, address = headquarters(sub, cover)
    first_date, first_form = first_filing if isinstance(first_filing, (tuple, list)) else (first_filing, None)
    exchanges = sub.get("exchanges") or []
    return {
        "entity": sub.get("name"), "cik": cik,
        "description": description,
        "description_short": pv(prof, "CompanyDescription"),
        "industry": pv(prof, "Industry") or pv(sdata, "Industry"),
        "sector": pv(prof, "Sector") or pv(sdata, "Sector"),
        "region": pv(prof, "Region"),
        "sic": sub.get("sic") or None, "sic_description": sub.get("sicDescription") or None,
        "state_of_incorporation": sub.get("stateOfIncorporation") or None,
        "fiscal_year_end_mmdd": sub.get("fiscalYearEnd") or None,
        "filer_category": sub.get("category") or None,
        "exchange": pv(sdata, "Exchange") or (exchanges[0] if exchanges else None),
        "exchanges": exchanges,
        "website": (sub.get("website") or "").strip() or pv(prof, "CompanyUrl"),
        "headquarters": hq_text, "address": address,
        "phone": (sub.get("phone") or "").strip() or pv(prof, "Phone"),
        "employees": employees,
        "employees_unresolved": employees_unresolved,
        "first_sec_filing": first_date, "first_sec_filing_form": first_form,
        "former_names": [f.get("name") for f in (sub.get("formerNames") or []) if isinstance(f, dict) and f.get("name")][:5],
        "edgar_url": f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={int(cik):010d}&type=10-K&dateb=&owner=include&count=40",
    }


def build_market(summary):
    sdata = (summary or {}).get("summaryData") if isinstance(summary, dict) else None
    if not isinstance(sdata, dict):
        return None

    def pv(k):
        v = sdata.get(k)
        return v.get("value") if isinstance(v, dict) else v

    hl = str(pv("FiftTwoWeekHighLow") or "")
    parts = [num(x) for x in hl.split("/")] if "/" in hl else [None, None]
    return {"exchange": pv("Exchange") or None, "average_volume": intnum(pv("AverageVolume")), "volume": intnum(pv("ShareVolume")),
            "market_cap_nasdaq": intnum(pv("MarketCap")), "high_52w": parts[0], "low_52w": parts[1] if len(parts) > 1 else None,
            "previous_close": num(pv("PreviousClose")), "one_year_target": num(pv("OneYrTarget")),
            "dividend_yield_nasdaq": num(pv("Yield")), "annualized_dividend": num(pv("AnnualizedDividend")),
            "ex_dividend_date": iso_from_text_date(pv("ExDividendDate")), "dividend_pay_date": iso_from_text_date(pv("DividendPaymentDate"))}


# ---------------------------------------------------------------------------
# Nasdaq analyst endpoints -> street
def _forecast_rows(block):
    rows = (block or {}).get("rows") if isinstance(block, dict) else None
    out = []
    for r in rows or []:
        if not isinstance(r, dict):
            continue
        out.append({"period": r.get("fiscalEnd"), "fiscal_end": month_key(r.get("fiscalEnd")),
                    "consensus": num(r.get("consensusEPSForecast")), "low": num(r.get("lowEPSForecast")),
                    "high": num(r.get("highEPSForecast")), "estimates": intnum(r.get("noOfEstimates")),
                    "revisions_up": intnum(r.get("up")), "revisions_down": intnum(r.get("down"))})
    return out


def _earnings_date(d):
    text = (d or {}).get("reportText") if isinstance(d, dict) else None
    if not text:
        return None
    text = re.sub(r"\s+", " ", str(text)).strip()
    date = iso_from_mdy(text)
    m = re.search(r"(?i)\b(before market open|after market close|during market hours|pre-?market|after[- ]hours)\b", text)
    return {"date": date, "text": text, "timing": m.group(1).lower() if m else None}


NASDAQ_NO_DATA = 999.0   # estimate-momentum publishes qtrMean/yrMean = 999 when Zacks has no estimate


def _mean(v):
    """A consensus mean from estimate-momentum; Nasdaq's 999 placeholder reads as null."""
    f = num(v)
    return None if f is not None and abs(f) == NASDAQ_NO_DATA else f


def build_street(as_of, targetprice=None, ratings=None, forecast=None, eps=None, momentum=None, earnings_date=None, peg=None, summary=None, warnings=None):
    """The extended `street` block. Every argument is one endpoint's `data` (None when it failed).
    Nasdaq placeholders are not figures: quote/eps rows with consensus = 0 AND earnings = 0 (every
    row for a name Zacks does not cover, e.g. GFI) are dropped, estimate-momentum's 999 means are
    null; `warnings` (a list, optional) records each such case."""
    if not any(x is not None for x in (targetprice, ratings, forecast, eps, momentum, earnings_date, peg)):
        return None
    tp = targetprice if isinstance(targetprice, dict) else {}
    co = tp.get("consensusOverview") if isinstance(tp.get("consensusOverview"), dict) else {}
    rt = ratings if isinstance(ratings, dict) else {}
    history = []
    for h in tp.get("historicalConsensus") or []:
        if not isinstance(h, dict):
            continue
        z = h.get("z") if isinstance(h.get("z"), dict) else {}
        date = iso_from_mdy(z.get("date"))
        if not date and isinstance(h.get("x"), (int, float)):
            date = datetime.datetime.fromtimestamp(h["x"], datetime.timezone.utc).date().isoformat()
        history.append({"date": date, "mean_target": num(h.get("y")), "buy": intnum(z.get("buy")), "hold": intnum(z.get("hold")),
                        "sell": intnum(z.get("sell")), "consensus": z.get("consensus")})
    history.sort(key=lambda r: r["date"] or "")
    analysts = None
    m = re.search(r"(\d+)\s+analysts?", str(rt.get("ratingsSummary") or ""))
    if m:
        analysts = int(m.group(1))
    buy, hold, sell = intnum(co.get("buy")), intnum(co.get("hold")), intnum(co.get("sell"))
    if analysts is None and any(x is not None for x in (buy, hold, sell)):
        analysts = (buy or 0) + (hold or 0) + (sell or 0)
    fc = forecast if isinstance(forecast, dict) else {}
    rows = (eps or {}).get("earningsPerShare") if isinstance(eps, dict) else None
    eps_history, eps_upcoming, placeholders = [], [], 0
    for r in rows or []:
        if not isinstance(r, dict):
            continue
        c, a = num(r.get("consensus")), num(r.get("earnings"))
        if c == 0 and a == 0:
            placeholders += 1   # Nasdaq's "no estimate" row, not a filed zero
            continue
        if r.get("type") == "PreviousQuarter":
            eps_history.append({"period": r.get("period"), "consensus": c, "actual": a,
                                "surprise_pct": round((a - c) / abs(c) * 100, 2) if c not in (None, 0) and a is not None else None})
        elif r.get("type") == "UpcomingQuarter":
            eps_upcoming.append({"period": r.get("period"), "consensus": c})
    if placeholders and warnings is not None:
        warnings.append(f"street: {placeholders} quote/eps row(s) with consensus = 0 and earnings = 0 are Nasdaq placeholders; dropped")
    eps_history.sort(key=lambda r: month_key(r["period"]) or "")
    eps_upcoming.sort(key=lambda r: month_key(r["period"]) or "")
    mo = (momentum or {}).get("changeInConsensus") if isinstance(momentum, dict) else None
    mom = None
    if isinstance(mo, dict):
        cur, wk, mn = (mo.get(k) if isinstance(mo.get(k), dict) else {} for k in ("currentData", "weekData", "monthData"))
        mom = {"quarter": {"period": re.sub(r"(?i)^fiscal quarter end\s*", "", str(mo.get("fiscalQtrEndText") or "")).strip() or None,
                           "current": _mean(cur.get("qtrMean")), "week_ago": _mean(wk.get("qtrMean")), "month_ago": _mean(mn.get("qtrMean"))},
               "year": {"period": re.sub(r"(?i)^fiscal year end\s*", "", str(mo.get("fiscalYearEndText") or "")).strip() or None,
                        "current": _mean(cur.get("yrMean")), "week_ago": _mean(wk.get("yrMean")), "month_ago": _mean(mn.get("yrMean"))}}
        if warnings is not None and any(abs(num(d.get(k)) or 0) == NASDAQ_NO_DATA for d in (cur, wk, mn) for k in ("qtrMean", "yrMean")):
            warnings.append("street: estimate-momentum published 999 (no estimate) for some means; those are null")
    pegv = None
    if isinstance(peg, dict):
        p = peg.get("pegr")
        pegv = num(p.get("pegValue")) if isinstance(p, dict) else num(p)
    sdata = (summary or {}).get("summaryData") if isinstance(summary, dict) else None
    t1y = sdata.get("OneYrTarget") if isinstance(sdata, dict) else None
    return {"source": "Nasdaq analyst endpoints", "as_of": as_of,
            "consensus": rt.get("meanRatingType") or (history[-1]["consensus"] if history else None),
            "analysts": analysts, "buy": buy, "hold": hold, "sell": sell,
            "target_mean": num(co.get("priceTarget")), "target_low": num(co.get("lowPriceTarget")), "target_high": num(co.get("highPriceTarget")),
            "target_1y_nasdaq_summary": num(t1y.get("value") if isinstance(t1y, dict) else t1y),
            "history": history, "brokers": [b for b in (rt.get("brokerNames") or []) if isinstance(b, str)],
            "upgrades_downgrades": [u for u in (rt.get("upgradesDowngrades") or []) if u is not None],
            "eps_forecast": {"quarterly": _forecast_rows(fc.get("quarterlyForecast")), "annual": _forecast_rows(fc.get("yearlyForecast"))},
            "eps_history": eps_history, "eps_upcoming": eps_upcoming, "momentum": mom,
            "next_earnings": _earnings_date(earnings_date), "peg_forward": pegv}


# ---------------------------------------------------------------------------
# Refresh policy
def should_skip(existing, newest_filing, max_age_days, today=None, force=False):
    """True when profile.json is younger than max_age_days AND the newest EDGAR filing date is unchanged."""
    if force or not isinstance(existing, dict):
        return False
    try:
        as_of = datetime.date.fromisoformat(str(existing.get("as_of")))
    except Exception:
        return False
    today = today or et_today()
    if (today - as_of).days >= max_age_days:
        return False
    if newest_filing and existing.get("newest_filing_date") != newest_filing:
        return False
    return True


# ---------------------------------------------------------------------------
def build(ticker, cik, quiet=False, sub=None):
    warnings, sources = [], {}
    as_of = et_today().isoformat()
    sub_url = f"https://data.sec.gov/submissions/CIK{int(cik):010d}.json"
    if sub is None:
        sub = edgar_json(sub_url)
    sources["edgar_submissions"] = sub_url
    annual = latest_annual(sub, cik)
    description, employees, cover, emp_unresolved = None, None, None, None
    if annual and annual.get("url"):
        sources["edgar_annual_document"] = annual["url"]
        try:
            raw = get_bytes(annual["url"], EDGAR_UA, EDGAR_TIMEOUT)
            cover = cover_address(raw)
            if cover:
                cover.update({"form": annual["form"], "filed": annual["filed"]})
            else:
                warnings.append(f"headquarters: no dei:EntityAddress cover tags in the {annual['form']} filed {annual['filed']}; EDGAR submissions address used")
            text = html_to_text(raw)
            desc_text, note = extract_item1(text, annual["form"], entity=sub.get("name"))
            if desc_text:
                description = {"text": desc_text, "source": note, "form": annual["form"], "filed": annual["filed"],
                               "period": annual["period"], "accession": annual["accession"], "url": annual["url"]}
            else:
                warnings.append(f"description: {note} ({annual['form']} filed {annual['filed']})")
            emp_notes = []
            employees = extract_employees(text, period=annual.get("period"), entity=sub.get("name"), notes=emp_notes)
            if employees:
                employees.update({"form": annual["form"], "filed": annual["filed"], "url": annual["url"]})
            elif emp_notes:
                # only a part of the workforce is filed (one function / location, a per-type split, or the registrant and a
                # subsidiary separately) or the stated date is unreadable: employees stays null and the sentence is the evidence
                reason, _, evidence = emp_notes[0].partition(": ")
                emp_unresolved = {"count": None, "reason": reason, "evidence": evidence.strip('"'),
                                  "form": annual["form"], "filed": annual["filed"], "url": annual["url"]}
                warnings.append(f"employees: null - {reason} in the {annual['form']} filed {annual['filed']}: {evidence}")
            else:
                warnings.append(f"employees: no headcount sentence found in the {annual['form']} filed {annual['filed']}")
        except Exception as e:
            warnings.append(f"annual document unreadable ({e}); description and employees null")
    else:
        warnings.append("no 10-K / 20-F / 40-F in the recent submissions; description and employees null")
    first = first_filing(sub, warnings=warnings)

    nq = {}
    endpoints = {"company_profile": f"https://api.nasdaq.com/api/company/{ticker}/company-profile",
                 "summary": f"https://api.nasdaq.com/api/quote/{ticker}/summary?assetclass=stocks",
                 "targetprice": f"https://api.nasdaq.com/api/analyst/{ticker}/targetprice",
                 "ratings": f"https://api.nasdaq.com/api/analyst/{ticker}/ratings",
                 "earnings_forecast": f"https://api.nasdaq.com/api/analyst/{ticker}/earnings-forecast",
                 "eps": f"https://api.nasdaq.com/api/quote/{ticker}/eps",
                 "estimate_momentum": f"https://api.nasdaq.com/api/analyst/{ticker}/estimate-momentum",
                 "earnings_date": f"https://api.nasdaq.com/api/analyst/{ticker}/earnings-date",
                 "peg_ratio": f"https://api.nasdaq.com/api/analyst/{ticker}/peg-ratio"}
    for key, url in endpoints.items():
        try:
            nq[key] = nasdaq_json(url)
            sources[f"nasdaq_{key}"] = url
        except Exception as e:
            nq[key] = None
            warnings.append(f"nasdaq {key} failed ({e}); that block is null")
            sources[f"nasdaq_{key}"] = f"FAILED: {url}"

    about = build_about(sub, cik, nq.get("company_profile"), nq.get("summary"), description, employees, first, cover=cover,
                        employees_unresolved=emp_unresolved)
    street = build_street(as_of, nq.get("targetprice"), nq.get("ratings"), nq.get("earnings_forecast"), nq.get("eps"),
                          nq.get("estimate_momentum"), nq.get("earnings_date"), nq.get("peg_ratio"), nq.get("summary"), warnings=warnings)
    if street is None:
        warnings.append("street: every Nasdaq analyst endpoint failed; block is null")
    market = build_market(nq.get("summary"))
    if market is None:
        warnings.append("market: Nasdaq summary unavailable; block is null")
    return {"ticker": ticker, "cik": int(cik), "as_of": as_of,
            "fetched_at": datetime.datetime.now(ZoneInfo("America/New_York")).isoformat(timespec="seconds"),
            "newest_filing_date": newest_filing_date(sub), "sources": sources,
            "about": about, "street": street, "filings": build_filings(sub, cik), "market": market, "warnings": warnings}


def summary_line(p):
    a, s = p.get("about") or {}, p.get("street") or {}
    d = a.get("description") or {}
    e = a.get("employees") or {}
    return (f"profile: {p['ticker']} cik={p['cik']} description={'yes (' + str(d.get('source')) + ')' if d else 'null'}"
            f" employees={e.get('count') if e else 'null'} first_filing={a.get('first_sec_filing')}"
            f" street={'consensus ' + str(s.get('consensus')) + ' n=' + str(s.get('analysts')) + ' target ' + str(s.get('target_mean')) if s else 'null'}"
            f" filings={len(p.get('filings') or [])} warnings={len(p.get('warnings') or [])}")


def run_one(ticker, cik_arg=None, write=True, quiet=False, sub=None):
    cik = resolve_cik(ticker, cik_arg)
    if cik is None:
        print(f"profile.py: NO_CIK for {ticker}", file=sys.stderr)
        return None, 2
    if sub is None:
        try:
            sub = edgar_json(f"https://data.sec.gov/submissions/CIK{int(cik):010d}.json")
        except Exception as e:
            print(f"profile.py: {ticker}: EDGAR submissions unreadable ({e}); nothing written", file=sys.stderr)
            return None, 3
    try:
        p = build(ticker, cik, quiet=quiet, sub=sub)
    except Exception as e:
        # a bug in the build is not a network failure: say so, with the traceback
        print(f"profile.py: {ticker}: build failed ({type(e).__name__}: {e}); nothing written", file=sys.stderr)
        traceback.print_exc()
        return None, 4
    if write:
        folder = f"{BASE}/{ticker}"
        os.makedirs(folder, exist_ok=True)
        write_atomic(f"{folder}/profile.json", p)
    if not quiet:
        print(summary_line(p))
        for w in p["warnings"]:
            print(f"  warning: {w}")
    return p, 0


def run_all(max_age_days, force=False, quiet=False):
    names = sorted(d for d in os.listdir(BASE) if not d.startswith((".", "_")) and os.path.isdir(f"{BASE}/{d}")
                   and os.path.exists(f"{BASE}/{d}/score.json"))
    written, skipped, failed = [], [], []
    for t in names:
        cik = resolve_cik(t)
        if cik is None:
            failed.append(f"{t}: no CIK"); continue
        try:
            sub = edgar_json(f"https://data.sec.gov/submissions/CIK{int(cik):010d}.json")
        except Exception as e:
            failed.append(f"{t}: submissions fetch failed ({e})"); continue
        existing = jload(f"{BASE}/{t}/profile.json")
        if should_skip(existing, newest_filing_date(sub), max_age_days, force=force):
            skipped.append(t)
            continue
        p, rc = run_one(t, write=True, quiet=quiet, sub=sub)
        if rc == 0:
            written.append(t)
        else:
            failed.append(f"{t}: exit {rc}")
        time.sleep(ALL_SLEEP_S)
    print(f"profile --all: {len(names)} names - {len(written)} written, {len(skipped)} skipped (fresh), {len(failed)} failed"
          + ("\n  " + "\n  ".join(failed) if failed else ""))
    return 1 if failed else 0


def main():
    argv = sys.argv[1:]
    if not argv or "-h" in argv or "--help" in argv:
        print(__doc__); sys.exit(2)

    def opt(name, default=None):
        return argv[argv.index(name) + 1] if name in argv and argv.index(name) + 1 < len(argv) else default

    quiet = "--quiet" in argv
    if "--all" in argv:
        sys.exit(run_all(int(opt("--max-age-days", DEFAULT_MAX_AGE_DAYS)), force="--force" in argv, quiet=quiet))
    pos = [a for i, a in enumerate(argv) if not a.startswith("--") and (i == 0 or argv[i - 1] not in ("--cik", "--max-age-days"))]
    if not pos:
        print(__doc__); sys.exit(2)
    ticker = pos[0].upper()
    _, rc = run_one(ticker, cik_arg=opt("--cik"), write="--no-write" not in argv, quiet=quiet)
    sys.exit(rc)


if __name__ == "__main__":
    main()
