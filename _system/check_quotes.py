#!/usr/bin/env python3
"""The R3 quote gate: every number in analysis.md traces to a generated file (engine 5.7; Andrew's ruling R3 of
2026-10-19 — strict quoting; design 02 §6, L2 rebase A5, A7, A11, A12, A19, A22).

Usage:
  python3 _system/check_quotes.py <T> [<T> ...] [--json] [--strict]
  python3 _system/check_quotes.py --all [--release-min 5.7.0] [--json PATH] [--quiet]
  python3 _system/check_quotes.py --save-run <T> <label> [--replace]

Per ticker: exit 0 when the run passes, or when it is a pre-5.7 (legacy) run — its report is printed with status
"legacy" and nothing is gated; exit 1 when a GATED run (dcf_numbers.json engine_release >= 5.7.0) fails — a number
traces to no generated file, or an integrity check fails — and, with --strict, when any run has an untraced number;
exit 2 on a usage error or an unreadable folder (no analysis.md, no dcf_numbers.json, unparseable JSON).
--all: every folder with analysis.md + dcf_numbers.json, one line each (ticker, status, release, checked, untraced,
stale) and a summary (counts by status; min / p25 / median / p75 / p90 / max untraced; the ten worst). Exit 1 only
when a gated run fails: the corpus mode runs green on legacy output and goes red the day a 5.7 run regresses.
--save-run: byte-copies <T>/dcf_numbers.json to <T>/dcf_numbers_<label>.json after verifying its content_hash
(label ^[a-z][a-z0-9_]{0,31}$; an existing label only with --replace). A preliminary or exploratory engine run
quoted in analysis.md (a method range) must be saved this way, never retyped. Exit 0 / 1 (hash) / 2 (usage).

What traces (02 §6.6): key_numbers.md, every section, with worker text removed (every judgment.json string of 12+
characters and every facts.json label / snippet / section / publisher where it occurs, the acquired-IPR&D deal names,
the worker text the engine record itself carries — below), everything inside “…” — make_score's echo of worker text
— and the pre-5.7 echo patterns); dcf_numbers.json's numeric leaves and the numbers inside its engine strings (never
under content_hash, cik, paths, growth_paths, source, reason, ack_reason, deal, iprd_judgment_hash, ttm_input_hash,
accession, url, at any depth); ttm.json the same way; the saved method runs dcf_numbers_<label>.json (hash-verified
and, on a gated run, the very runs score.json method_runs recorded — I4); the exact values behind key_numbers.md's
filed history and return / margin series; and the declared facts' exact values — only after integrity check I3
holds, so they are exactly what key_numbers.md rendered. Worker text the engine copies into its record (any
string under source / reason / ack_reason / deal — ads_ratio.source, an override's source, a share-class source)
and echoes into its flag strings (ADS_RATIO_APPLIED, OVERRIDE_APPLIED, the share-class DATA_GAP) is blanked
wherever the record's strings or key_numbers.md repeat it, at any length — through the record's own copy, which I1
binds. judgment.json is never a source (review r01, 2026-10-21: nothing binds it to the score, so a number typed
into probs_used or moat_score after make_score would pass; the engine's own scenario probabilities and moat are in
dcf_numbers.json, and make_score refuses a judgment that differs from them). Tokens are read by quote_tokens (the
tokenizer, ignore rules and tolerance at the quoted precision); a method constant or release number in its context
is ignored only when it matches nothing.

Integrity (gated runs; each failure fails the run): I1 score.json was built from this dcf_numbers.json (its
dcf_content_hash is the run's content_hash, valid over the record — reprice.run_hash_problem's rule); I2
key_numbers.md is what make_score.py wrote (sha256, CRLF normalized to LF, equals score.json key_numbers_sha256: a
number added to key_numbers.md by hand never passes, and a make_score run that stopped between score.json and
key_numbers.md fails safe); I3 facts.json is the declaration make_score rendered (facts_sha256); I4 every saved run
verifies, names this ticker and is the run score.json method_runs recorded under its label (same content_hash: a
saved run replaced after make_score — --save-run ... --replace — fails until make_score re-runs and renders it);
I5 analysis.md is not empty.

Imports facts and quote_tokens only (never make_score: make_score imports this module); no network; writes nothing
except --save-run.
"""
import csv
import glob
import hashlib
import json
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import facts as _facts  # noqa: E402
import quote_tokens as _qt  # noqa: E402

BASE = os.environ.get("STOCKS_BASE") or os.path.dirname(HERE)
LABEL_RE = re.compile(r"^[a-z][a-z0-9_]{0,31}$")
SAVED_RUN_GLOB = "dcf_numbers_*.json"
WORKER_TEXT_MIN = 12          # 02 §6.6: a judgment.json string this long is blanked wherever key_numbers.md echoes it
SKIP_KEYS = frozenset({"content_hash", "cik", "paths", "growth_paths", "source", "reason", "ack_reason", "deal",
                       "iprd_judgment_hash", "ttm_input_hash", "accession", "instance_url", "url"})   # rebase A11
# [review r02, 2026-10-21] the keys under which an engine record carries worker text it copied from judgment.json
# (and may echo into a flag string): every string below them is blanked from the record's other strings
WORKER_TEXT_KEYS = frozenset({"source", "reason", "ack_reason", "deal"})
FILED_HISTORY_YEARS = 10
RETURN_SERIES_YEARS = 6
# 07 §1.9 item 4: the return / margin series key_numbers.md prints — the set 02 §1.1 measured (OCF margin and revenue
# growth included), minus the ROIC proxy series, which the moat lane's Moat scorecard prints once
RETURN_SERIES = (("gross_margin", "Gross margin"), ("operating_margin", "Operating margin"), ("net_margin", "Net margin"),
                 ("roe", "ROE"), ("fcf_margin", "FCF margin"), ("ocf_margin", "OCF margin"),
                 ("revenue_growth", "Revenue growth"), ("sbc_pct_rev", "SBC % of revenue"),
                 ("capex_pct_rev", "Capex % of revenue"))
# 02 §7.2's table plus the columns 02 §1.1 measured (FCF, the capex legs, equity, tax)
FILED_COLUMNS = (("revenue", "Revenue"), ("net_income", "Net income"), ("operating_income", "Operating income"),
                 ("ocf", "OCF"), ("capex", "Capex"), ("capex_ppe", "Capex PP&E"),
                 ("capex_intangibles", "Capex intangibles"), ("sbc", "SBC"), ("da", "D&A"), ("fcf", "FCF"),
                 ("oe_conservative", "OE (conservative)"), ("oe_per_share", "OE/share"),
                 ("oe_maintenance", "OE (maintenance)"), ("delta_nwc", "ΔNWC"), ("shares_diluted", "Diluted shares"),
                 ("cash", "Cash"), ("debt_total", "Total debt"), ("equity", "Equity"), ("tax", "Tax"))
YOY_COLUMNS = (("revenue", "Revenue"), ("ocf", "OCF"), ("net_income", "Net income"), ("oe_conservative", "OE"))
PRELIM_HINT = re.compile(r"(?i)preliminary|method range|exploratory|\brun\b")
# pre-5.7 key_numbers.md echoes of worker text (02 §6.6 legacy fallback patterns)
LEGACY_ECHO = (re.compile(r"\(agent override of [A-F]: .*\)(?= · confidence)"),
               re.compile(r"^- (?:capex|sbc|shares) reason: .*$", re.M),
               re.compile(r"^- Source: .*$", re.M))
DATE_RX = (re.compile(r"\b\d{4}-\d{2}-\d{2}\b"),
           re.compile(r"(?i)\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+\d{1,2}(?:,\s*\d{4})?\b"))


tokenize = _qt.tokenize   # 02 §6.7's API name (the tokenizer lives in quote_tokens, 07 §1.8)


def gated(n):
    """A 5.7 run (facts.is_rulings_run): its analysis.md must pass."""
    return _facts.is_rulings_run(n)


def _load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _try_load(path):
    try:
        return _load(path)
    except (OSError, ValueError):
        return None


def _f(s):
    try:
        v = float(s) if s not in (None, "") else None
    except (TypeError, ValueError):
        return None
    return v if v is not None and v == v and abs(v) != float("inf") else None


# ---------------------------------------------------------------------------
# What make_score renders as engine lines (one definition: make_score's renderer and these sources read it)
# ---------------------------------------------------------------------------
def _csv_rows(folder):
    try:
        with open(os.path.join(folder, "financials_history.csv"), encoding="utf-8", newline="") as f:
            return sorted((r for r in csv.DictReader(f) if r.get("period_end")), key=lambda r: r["period_end"])
    except (OSError, ValueError, csv.Error, UnicodeDecodeError):
        return []


def _ads_ratio(n):
    a = n.get("ads_ratio") if isinstance(n, dict) else None
    r = a.get("ratio") if isinstance(a, dict) else None
    return float(r) if isinstance(r, (int, float)) and not isinstance(r, bool) and r > 0 else None


def filed_history(folder, n):
    """The filed-history table key_numbers.md prints (02 §7.2 with the columns 02 §1.1 measured; rebase A1 / A9 /
    A10): the last 10 FY rows of financials_history.csv (FILED_COLUMNS, full dollars, USD — the engine's
    FX-converted figures), total debt = debt_total, else
    debt_current + debt_lt; OE/share = oe_per_share, else oe_conservative / shares_diluted — × the ADS ratio when the
    run applied one — shown only when the latest row reproduces the engine's base_oe_latest_per_share (1e-6
    relative), else withheld. Returns {"rows": [{fy, period_end, <column>: value | None}], "per_share": bool,
    "yoy": [(label, [(fy, growth)])]}; rows [] without a CSV."""
    rows = _csv_rows(folder)[-FILED_HISTORY_YEARS:]
    out = []
    for r in rows:
        rec = {"fy": f"FY{r.get('fy_label') or r['period_end'][:4]}", "period_end": r["period_end"]}
        for col, _ in FILED_COLUMNS:
            rec[col] = _f(r.get(col))
        if rec["debt_total"] is None and (_f(r.get("debt_current")) is not None or _f(r.get("debt_lt")) is not None):
            rec["debt_total"] = (_f(r.get("debt_current")) or 0.0) + (_f(r.get("debt_lt")) or 0.0)
        if rec["oe_per_share"] is None and rec["oe_conservative"] is not None and rec["shares_diluted"]:
            rec["oe_per_share"] = rec["oe_conservative"] / rec["shares_diluted"]
        out.append(rec)
    per_share = False
    eng = (n or {}).get("base_oe_latest_per_share") if isinstance(n, dict) else None
    if out and isinstance(eng, (int, float)) and not isinstance(eng, bool) and out[-1]["oe_per_share"] is not None:
        ratio = _ads_ratio(n)
        for factor in ([1.0, ratio] if ratio else [1.0]):
            if abs(out[-1]["oe_per_share"] * factor - eng) <= 1e-6 * max(1.0, abs(eng)):
                per_share = True
                for rec in out:
                    if rec["oe_per_share"] is not None:
                        rec["oe_per_share"] *= factor
                break
    if not per_share:
        for rec in out:
            rec["oe_per_share"] = None
    yoy = []
    for col, name in YOY_COLUMNS:
        pts = []
        for a, b in zip(out, out[1:]):
            x, y = a.get(col), b.get(col)
            if x and y is not None and x > 0:
                pts.append((b["fy"], y / x - 1.0))
        if pts:
            yoy.append((name, pts))
    return {"rows": out, "per_share": per_share, "yoy": yoy}


def return_series(folder):
    """[(label, field, [(FY label, value)])] — fundamentals.json's return / margin series over the last 6 FY that
    key_numbers.md's Growth & moat block prints (fractions; printed at 1 dp)."""
    fu = _try_load(os.path.join(folder, "fundamentals.json"))
    rows = [r for r in (fu.get("annual") or []) if isinstance(r, dict)] if isinstance(fu, dict) else []
    rows = sorted(rows, key=lambda r: str(r.get("period_end") or ""))[-RETURN_SERIES_YEARS:]
    out = []
    for field, label in RETURN_SERIES:
        pts = [(f"FY{r.get('fy') or str(r.get('period_end'))[:4]}", float(r[field])) for r in rows
               if isinstance(r.get(field), (int, float)) and not isinstance(r.get(field), bool)
               and r[field] == r[field]]
        if pts:
            out.append((label, field, pts))
    return out


def derived_values(n):
    """The figures L2's engine lines derive (02 §7.2): price ÷ IV@15% and its premium / discount, price ÷ base
    OE/share, and the probability weights (bear-or-worse, base, bull-or-better)."""
    out = []
    p, iv = n.get("price"), n.get("iv_at_15")
    if isinstance(p, (int, float)) and isinstance(iv, (int, float)) and iv:
        out += [p / iv, p / iv - 1.0]
    b = n.get("base_oe_per_share")
    if isinstance(p, (int, float)) and isinstance(b, (int, float)) and b > 0:
        out.append(p / b)
    sc = n.get("scenarios") or {}
    pr = [(sc.get(k) or {}).get("prob") for k in ("super_bear", "bear", "base", "bull", "super_bull")]
    if all(isinstance(x, (int, float)) for x in pr):
        out += [pr[0] + pr[1], pr[2], pr[3] + pr[4]]
    return out


# ---------------------------------------------------------------------------
# Sources (02 §6.6)
# ---------------------------------------------------------------------------
def _leaves_into(vs, obj, blank=(), skip_paths=(), path=""):
    """Numeric leaves of a JSON object (and the numbers inside its strings: engine flag texts) into ValueSet vs,
    never under SKIP_KEYS (any depth) or a dotted path in skip_paths; worker text in `blank` is removed from
    strings first."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = f"{path}.{k}" if path else str(k)
            if k in SKIP_KEYS or p in skip_paths:
                continue
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                vs.add(v, key=str(k))
            else:
                _leaves_into(vs, v, blank, skip_paths, p)
    elif isinstance(obj, list):
        for v in obj:
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                vs.add(v)
            else:
                _leaves_into(vs, v, blank, skip_paths, path)
    elif isinstance(obj, str) and len(obj) < 4000 and re.search(r"\d", obj):
        s = _qt.blank_quoted(_qt.blank_literals(obj, blank))
        s = re.sub(r"\((?:estimate|filing): [^)]*\)", " ", s)
        vs.add_tokens(_qt.numbers(s))


def record_worker_strings(rec):
    """[review r02, 2026-10-21] The worker text an engine record (dcf_numbers.json, a saved run, ttm.json) carries:
    every string with a digit at any depth under a WORKER_TEXT_KEYS key — ads_ratio.source, an override's source and
    reason, a share-class source, an acquired-IPR&D deal name — at any length. The engine echoes some of it into its
    flag strings (ADS_RATIO_APPLIED "(<source>)", OVERRIDE_APPLIED "(<kind>: <source>)", the share-class DATA_GAP),
    so a number inside it would otherwise read as an engine figure; the record's own copy is what the echo repeats,
    whatever judgment.json says now (the record is hash-bound, judgment.json is not)."""
    out = []

    def strings(o):
        if isinstance(o, str):
            if re.search(r"\d", o) and o.strip():
                out.append(o)
        elif isinstance(o, dict):
            for v in o.values():
                strings(v)
        elif isinstance(o, list):
            for v in o:
                strings(v)

    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k in WORKER_TEXT_KEYS:
                    strings(v)
                else:
                    walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(rec)
    return out


def judgment_strings(j):
    """The worker text judgment.json carries: every string leaf of 12+ characters, and the acquired-IPR&D deal
    names of any length (rebase A11)."""
    out = []

    def walk(o, key=None):
        if isinstance(o, dict):
            for k, v in o.items():
                walk(v, k)
        elif isinstance(o, list):
            for v in o:
                walk(v, key)
        elif isinstance(o, str) and (len(o) >= WORKER_TEXT_MIN or (key == "deal" and o.strip())):
            out.append(o)
    walk(j if isinstance(j, dict) else {})
    return out


def facts_strings(doc):
    out = []
    for f in (doc.get("facts") or []) if isinstance(doc, dict) else []:
        if not isinstance(f, dict):
            continue
        for k in ("label", "snippet"):
            if isinstance(f.get(k), str):
                out.append(f[k])
        src = f.get("source") if isinstance(f.get("source"), dict) else {}
        for k in ("section", "publisher", "exhibit"):
            if isinstance(src.get(k), str) and len(src[k]) >= 3:
                out.append(src[k])
    for e in (doc.get("not_quantities") or []) if isinstance(doc, dict) else []:
        if isinstance(e, dict) and isinstance(e.get("reason"), str):
            out.append(e["reason"])
    return out


def key_numbers_source_text(text, blank):
    """key_numbers.md with worker text removed: the literal strings in `blank`, every “…” span, and the pre-5.7
    echo patterns (the tier line's "(agent override of X: …)", "- <field> reason:", the payable "- Source:" line,
    the Overrides table's Source column, "(estimate: …)" / "(filing: …)" in flag and note lines)."""
    t = _qt.blank_quoted(_qt.blank_literals(text, blank))
    for rx in LEGACY_ECHO:
        t = rx.sub(lambda m: " " * len(m.group(0)), t)
    lines = []
    for line in t.split("\n"):
        if line.startswith(("| capex |", "| sbc |", "| shares |")):
            cells = line.split("|")
            if len(cells) > 5:
                cells[4] = " " * len(cells[4])
                line = "|".join(cells)
        if line.startswith(("- OVERRIDE_APPLIED", "- Note:", "- ADS_RATIO_APPLIED")):
            line = re.sub(r"\((?:estimate|filing): .*?\)", lambda m: " " * len(m.group(0)), line)
        lines.append(line)
    return "\n".join(lines)


def saved_runs(folder):
    """[(label, path, record or None)] — every dcf_numbers_<label>.json in the folder, sorted by label."""
    out = []
    for p in sorted(glob.glob(os.path.join(folder, SAVED_RUN_GLOB))):
        name = os.path.basename(p)
        out.append((name[len("dcf_numbers_"):-len(".json")], p, _try_load(p)))
    return out


def saved_run_problem(label, rec, ticker):
    """None when a saved run is verbatim engine output for this ticker, else why not."""
    name = f"dcf_numbers_{label}.json"
    if not isinstance(rec, dict) or not _facts.run_hash_ok(rec):
        return (f"{name}: content_hash missing or MISMATCH — a saved method run must be verbatim engine output "
                "(check_quotes.py --save-run)")
    if str(rec.get("ticker") or "").upper() != str(ticker).upper():
        return f"{name}: ticker {rec.get('ticker')} is not {str(ticker).upper()}"
    return None


def path_value(obj, path):
    """The value at dotted path `path` of a JSON object, or None."""
    cur = obj
    for k in str(path).split("."):
        if not isinstance(cur, dict) or k not in cur:
            return None
        cur = cur[k]
    return cur


def bound_saved_run(label, rec, ticker, runs=None):
    """True when saved run `label` counts as a source: verbatim engine output for this ticker and, when `runs`
    ({label: content_hash}, score.json method_runs) is given, the very run make_score recorded under that label
    (review r07, 2026-10-21: I4 binds by content_hash, not by label alone)."""
    if saved_run_problem(label, rec, ticker) is not None:
        return False
    return runs is None or (label in runs and runs[label] == rec.get("content_hash"))


def method_runs_bound(score):
    """{label: content_hash} of score.json method_runs (the saved runs make_score rendered), or {} without any."""
    return {r.get("label"): r.get("content_hash") for r in (score or {}).get("method_runs") or [] if isinstance(r, dict)}


def engine_sources(folder, n, ttm=None, exclude_paths=(), blank=(), runs=None):
    """The engine sources a reason (make_score.check_influence) or analysis.md traces to, as a ValueSet:
    dcf_numbers.json (n) leaves and engine-string numbers, ttm.json, the verified saved runs (only those in `runs`,
    {label: content_hash}, when given — I4's binding), and the filed history / return series / derived values
    key_numbers.md prints. Strings lose the worker text in `blank` and, record by record, the worker text the record
    itself carries (record_worker_strings: an echo of ads_ratio.source in ADS_RATIO_APPLIED is the worker's, not an
    engine figure). exclude_paths: dotted dcf_numbers.json paths kept out (10 §(l) trace_only). judgment.json is
    never read (review r01, 2026-10-21: it is not bound to the score; its probs_used and moat_score must equal the
    engine's, which are here already)."""
    vs = _qt.ValueSet()
    ticker = (n or {}).get("ticker") or os.path.basename(os.path.normpath(folder))
    blank = list(blank or ())
    paths = set(exclude_paths or ())
    _leaves_into(vs, n or {}, blank + record_worker_strings(n or {}), paths)
    tt = ttm if ttm is not None else _try_load(os.path.join(folder, "ttm.json"))
    if isinstance(tt, dict):
        _leaves_into(vs, tt, blank + record_worker_strings(tt))
    for label, _, rec in saved_runs(folder):
        if bound_saved_run(label, rec, ticker, runs):
            # an excluded path stays out of a saved run too wherever the saved run repeats the scored run's figure
            # there — a saved copy of a pinned run repeats the pin (review r05, 2026-10-21)
            same = {p for p in paths if path_value(rec, p) is not None and path_value(rec, p) == path_value(n, p)}
            _leaves_into(vs, rec, blank + record_worker_strings(rec), same)
    fh = filed_history(folder, n or {})
    for rec in fh["rows"]:
        for col, _ in FILED_COLUMNS:
            if rec.get(col) is not None:
                vs.add(rec[col])
    for _, pts in fh["yoy"]:
        for _, g in pts:
            vs.add(g)
    for _, _, pts in return_series(folder):
        for _, v in pts:
            vs.add(v)
    for v in derived_values(n or {}):
        vs.add(v)
    return vs


def worker_blank(j=None, facts_doc=None, n=None):
    """The worker text blanked wherever key_numbers.md or an engine string repeats it (02 §6.6 item 1): judgment.json's
    strings (12+ characters, and the deal names), the declaration's labels / snippets / sections / publishers /
    not_quantities reasons, and the worker text engine record n carries (record_worker_strings, any length). One
    list for check_folder and make_score.check_influence."""
    return (judgment_strings(j if isinstance(j, dict) else {}) + facts_strings(facts_doc)
            + (record_worker_strings(n) if isinstance(n, dict) else []))


def influence_sources(folder, n, judgment=None, facts_doc=None, exclude_paths=()):
    """The engine set a 5.7 reason traces to (make_score.check_influence; 02 §5): engine_sources with check_folder's
    worker text blanked — the judgment's (judgment.json read from the folder when not given) and the declaration's
    (facts.json likewise) — so a number the worker typed into ads_ratio.source, an override's source or another
    echoed string never supports the worker's own reason (review r02, 2026-10-21). Every saved run that verifies
    counts (make_score's load_method_runs already refused a tampered one)."""
    j = judgment if isinstance(judgment, dict) else (_try_load(os.path.join(folder, "judgment.json")) or {})
    doc = facts_doc if isinstance(facts_doc, dict) else _facts.load(folder)[0]
    return engine_sources(folder, n, exclude_paths=exclude_paths, blank=worker_blank(j, doc if isinstance(doc, dict)
                                                                                    else None))


class Sources:
    """Everything an analysis.md number may trace to (02 §6.6), built for one folder."""

    def __init__(self, values):
        self.values = values

    def match(self, tok):
        return self.values.match(tok)

    @classmethod
    def for_folder(cls, folder, n=None, facts_doc=None, include_key_numbers=True, include_facts=True, judgment=None,
                   runs=None):
        """runs: {label: content_hash} — only those saved runs count (a gated run's I4 binding); None: every saved
        run that verifies. judgment.json supplies worker text to blank, never a number."""
        n = n if n is not None else _try_load(os.path.join(folder, "dcf_numbers.json")) or {}
        j = judgment if judgment is not None else _try_load(os.path.join(folder, "judgment.json")) or {}
        blank = worker_blank(j, facts_doc, n)
        vs = engine_sources(folder, n, blank=blank, runs=runs)
        if include_key_numbers:
            try:
                with open(os.path.join(folder, "key_numbers.md"), encoding="utf-8") as f:
                    kn = f.read()
                vs.add_tokens(_qt.numbers(key_numbers_source_text(kn, blank)))
            except OSError:
                pass
        if include_facts and isinstance(facts_doc, dict):
            for fact in facts_doc.get("facts") or []:
                if isinstance(fact, dict):
                    for v in (fact.get("value") if isinstance(fact.get("value"), list) else [fact.get("value")]):
                        vs.add(v)
        return cls(vs)


def trace_text(text, sources, not_quantities=()):
    """(untraced tokens, ignored counts) for a text against sources."""
    ignored = {"year": 0, "date": 0, "small": 0, "const": 0, "release": 0, "zero": 0, "not_quantity": 0}
    untraced, matched, checked = [], 0, 0
    for nq in not_quantities:
        ignored["not_quantity"] += text.count(nq) if nq else 0
    for rx in DATE_RX:
        ignored["date"] += len(rx.findall(text))
    for t in _qt.tokenize(text, not_quantities):
        if t.cls:
            ignored[t.cls] += 1
            continue
        if sources.match(t):
            checked += 1
            matched += 1
            continue
        if t.release_like:
            ignored["release"] += 1
            continue
        if _qt.is_method_constant(t, text):
            ignored["const"] += 1
            continue
        checked += 1
        untraced.append(t)
    return untraced, ignored, checked, matched


# ---------------------------------------------------------------------------
# One folder (02 §6.1-§6.2)
# ---------------------------------------------------------------------------
def _sha_text_lf(path):
    with open(path, encoding="utf-8", newline="") as f:
        t = f.read()
    return hashlib.sha256(t.replace("\r\n", "\n").encode("utf-8")).hexdigest()


def check_folder(folder, strict=False):
    """The report for one folder (02 §6.1 JSON shape). status: pass | fail | legacy | error."""
    ticker = os.path.basename(os.path.normpath(folder)).upper()
    rep = {"ticker": ticker, "status": "error", "gated": False, "engine_release": None, "checked": 0, "matched": 0,
           "ignored": {}, "untraced": [], "integrity": [], "warnings": [], "analysis_sha256": None,
           "facts_sha256": None, "key_numbers_sha256": None,
           "sources": {"key_numbers": False, "dcf_numbers": False, "ttm": False, "facts": 0, "method_runs": []}}
    try:
        n = _load(os.path.join(folder, "dcf_numbers.json"))
    except OSError:
        rep["integrity"].append("no dcf_numbers.json — nothing to check")
        return rep
    except ValueError as e:
        rep["integrity"].append(f"dcf_numbers.json is not valid JSON ({e})")
        return rep
    try:
        with open(os.path.join(folder, "analysis.md"), encoding="utf-8") as f:
            text = f.read()
    except OSError:
        rep["integrity"].append("no analysis.md — nothing to check")
        return rep
    rep["engine_release"] = n.get("engine_release") if isinstance(n, dict) else None
    rep["gated"] = gate = gated(n)
    rep["sources"]["dcf_numbers"] = True
    rep["analysis_sha256"] = hashlib.sha256(text.replace("\r\n", "\n").encode("utf-8")).hexdigest()
    score = _try_load(os.path.join(folder, "score.json"))
    score = score if isinstance(score, dict) else None
    kn_path = os.path.join(folder, "key_numbers.md")
    rep["sources"]["key_numbers"] = os.path.exists(kn_path)
    rep["sources"]["ttm"] = os.path.exists(os.path.join(folder, "ttm.json"))
    if rep["sources"]["key_numbers"]:
        rep["key_numbers_sha256"] = _sha_text_lf(kn_path)
    doc, ferr = _facts.load(folder)
    facts_ok = False
    if ferr:
        if gate:
            rep["integrity"].append(ferr)
    elif doc is not None:
        rep["facts_sha256"] = _facts.canonical_sha256(doc)
    declared = (score or {}).get("declared_facts") if isinstance((score or {}).get("declared_facts"), dict) else None
    if gate:
        # I1 (A7: reprice.run_hash_problem's rule) — score.json is this run's
        if score is None or score.get("dcf_content_hash") != n.get("content_hash") or not _facts.run_hash_ok(n):
            rep["integrity"].append("I1: score.json is not built from this dcf_numbers.json — run make_score.py")
        # I2 — key_numbers.md is make_score's
        if not rep["sources"]["key_numbers"]:
            rep["integrity"].append("I2: key_numbers.md is missing — re-run make_score.py")
        elif score is not None and rep["key_numbers_sha256"] != score.get("key_numbers_sha256"):
            rep["integrity"].append("I2: key_numbers.md differs from what make_score.py wrote — never edit it; re-run "
                                    "make_score.py (a make_score run that stopped before writing key_numbers.md "
                                    "leaves the same state)")
        # I3 — facts.json is the declaration make_score rendered
        if not ferr and rep["facts_sha256"] != (declared or {}).get("facts_sha256"):
            rep["integrity"].append("I3: facts.json changed after make_score.py — re-run make_score.py so "
                                    "key_numbers.md renders it")
        # I4 — every saved run verifies and is the run score.json method_runs recorded under its label (review r07,
        # 2026-10-21: by content_hash — a run replaced after make_score is not the one key_numbers.md rendered)
        listed = method_runs_bound(score)
        for label, _, rec in saved_runs(folder):
            why = saved_run_problem(label, rec, ticker)
            if why:
                rep["integrity"].append(f"I4: {why}")
            elif label not in listed:
                rep["integrity"].append(f"I4: dcf_numbers_{label}.json is not listed in score.json method_runs — "
                                        "re-run make_score.py")
            elif listed[label] != rec.get("content_hash"):
                rep["integrity"].append(f"I4: dcf_numbers_{label}.json changed after make_score.py — re-run "
                                        "make_score.py")
        # I5
        if not text.strip():
            rep["integrity"].append("I5: analysis.md is empty")
    facts_ok = doc is not None and not ferr and rep["facts_sha256"] == (declared or {}).get("facts_sha256")
    rep["sources"]["facts"] = len(doc.get("facts") or []) if facts_ok and isinstance(doc, dict) else 0
    # a gated run's saved runs trace only once I4 holds for them (the same rule as the declared values and I3); a
    # legacy report keeps every saved run that verifies (pre-5.7 scores record no method_runs)
    runs = method_runs_bound(score) if gate else None
    rep["sources"]["method_runs"] = [label for label, _, rec in saved_runs(folder)
                                     if bound_saved_run(label, rec, ticker, runs)]
    nq = [e.get("text") for e in (doc.get("not_quantities") or []) if isinstance(e, dict)
          and isinstance(e.get("text"), str)] if isinstance(doc, dict) and not ferr else []
    # the declared values trace only once I3 holds (they are then exactly what key_numbers.md rendered); the labels
    # and snippets are worker text either way, never a source
    src = Sources.for_folder(folder, n=n, facts_doc=doc if isinstance(doc, dict) else None, include_facts=facts_ok,
                             runs=runs)
    untraced, ignored, checked, matched = trace_text(text, src, nq)
    rep["checked"], rep["matched"], rep["ignored"] = checked, matched, ignored
    for t in untraced:
        line, col = _qt.line_col(text, t.start)
        rep["untraced"].append({"line": line, "col": col, "raw": t.raw, "kind": t.kind,
                                "value": t.val if t.kind in ("money", "plain", "mult") else t.v,
                                "tolerance": _qt.tolerance(t)})
    for s in (declared or {}).get("stale") or []:
        if isinstance(s, dict):
            rep["warnings"].append(f"{s.get('id')} is STALE (as of {s.get('as_of')}): {s.get('why')}")
    for d in (declared or {}).get("drift") or []:
        if isinstance(d, dict):
            rep["warnings"].append(f"{d.get('id')} DRIFTED ({d.get('status')}): {d.get('path')} now reads "
                                   f"{d.get('file_value')} (declared {d.get('declared')}) — re-score at the next filing")
    if not gate:
        rep["status"] = "legacy"
    else:
        rep["status"] = "pass" if not untraced and not rep["integrity"] else "fail"
    return rep


def refusal_text(rep, limit=10):
    """The done / pass2-done refusal for a failing report (02 §9)."""
    if rep.get("integrity"):
        return (f"analysis.md fails the quote check (engine release {rep.get('engine_release')}): "
                + "; ".join(rep["integrity"]) + f". Run python3 _system/check_quotes.py {rep['ticker']} for the report")
    un = rep.get("untraced") or []
    shown = ", ".join(f"analysis.md:{u['line']} \"{u['raw']}\"" for u in un[:limit]) + (" …" if len(un) > limit else "")
    verb = "numbers trace" if len(un) != 1 else "number traces"     # review r08: "1 number traces"
    return (f"analysis.md fails the quote check (engine release {rep.get('engine_release')}): {len(un)} {verb} to no "
            f"generated file — {shown}. Run python3 _system/check_quotes.py "
            f"{rep['ticker']} for the report; quote key_numbers.md, declare research figures in facts.json and re-run "
            "make_score.py, save preliminary runs with --save-run")


def human_report(rep, folder=None):
    """The stdout report (02 §6.1)."""
    st = {"pass": "PASS", "fail": "FAIL", "legacy": "legacy (pre-5.7 run, not gated)", "error": "ERROR"}[rep["status"]]
    rel = rep.get("engine_release") or "pre-5.4"
    L = [f"check_quotes.py: {rep['ticker']} — {st} (engine {rel} run; {rep['checked']} numbers checked, "
         f"{len(rep['untraced'])} untraced, {sum((rep.get('ignored') or {}).values())} ignored)"]
    for msg in rep.get("integrity") or []:
        L.append(f"  integrity: {msg}")
    lines = []
    if folder and rep.get("untraced"):
        try:
            with open(os.path.join(folder, "analysis.md"), encoding="utf-8") as f:
                lines = f.read().split("\n")
        except OSError:
            lines = []
    for u in rep.get("untraced") or []:
        ctx = lines[u["line"] - 1] if 0 < u["line"] <= len(lines) else ""
        hint = (f" — a preliminary run? save it: check_quotes.py --save-run {rep['ticker']} prelim"
                if PRELIM_HINT.search(ctx) else
                " — quote key_numbers.md, or declare it in facts.json (kind folder when a folder file has it) and "
                "re-run make_score.py")
        L.append(f"  analysis.md:{u['line']}:{u['col']}  \"{u['raw']}\"  {u['kind']:6} traces to no generated file{hint}")
    ig = rep.get("ignored") or {}
    if ig:
        L.append(f"  ignored: {ig.get('year', 0) + ig.get('date', 0)} years/dates, {ig.get('small', 0)} small counts, "
                 f"{ig.get('const', 0)} method constants, {ig.get('release', 0)} release numbers, {ig.get('zero', 0)} "
                 f"zeros, {ig.get('not_quantity', 0)} not_quantities")
    for w in rep.get("warnings") or []:
        L.append(f"  warning: {w}")
    return "\n".join(L)


# ---------------------------------------------------------------------------
# --save-run (02 §6.1; rebase A7)
# ---------------------------------------------------------------------------
def save_run(folder, label, replace=False):
    """(exit code, message): byte-copy <folder>/dcf_numbers.json to dcf_numbers_<label>.json after verifying its
    content_hash; 2 on a bad label / missing file, 1 on a hash mismatch or an existing label without replace."""
    if not LABEL_RE.match(label or ""):
        return 2, f"check_quotes.py: --save-run label {label!r} must match ^[a-z][a-z0-9_]{{0,31}}$"
    src = os.path.join(folder, "dcf_numbers.json")
    try:
        n = _load(src)
    except OSError:
        return 2, f"check_quotes.py: no dcf_numbers.json in {folder}"
    except ValueError as e:
        return 2, f"check_quotes.py: dcf_numbers.json is not valid JSON ({e})"
    if not _facts.run_hash_ok(n):
        return 1, ("check_quotes.py: --save-run REFUSED — dcf_numbers.json content_hash missing or MISMATCH (not "
                   "verbatim engine output); re-run dcf_engine.py and save that run")
    dst = os.path.join(folder, f"dcf_numbers_{label}.json")
    if os.path.exists(dst) and not replace:
        return 1, (f"check_quotes.py: --save-run REFUSED — {os.path.basename(dst)} exists; pass --replace to overwrite "
                   "it, or choose another label")
    tmp = f"{dst}.tmp.{os.getpid()}"
    shutil.copyfile(src, tmp)
    os.replace(tmp, dst)
    return 0, f"check_quotes.py: saved {dst}"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def _quantile(xs, q):
    return xs[min(len(xs) - 1, int(q * len(xs)))] if xs else None


def _all(args):
    rel_min, jpath, quiet = None, None, "--quiet" in args
    if "--release-min" in args:
        i = args.index("--release-min")
        if i + 1 >= len(args):
            print("check_quotes.py: --release-min needs a release (e.g. 5.7.0)", file=sys.stderr)
            return 2
        rel_min = args[i + 1]
    if "--json" in args:
        i = args.index("--json")
        if i + 1 >= len(args):
            print("check_quotes.py: --all --json needs a path", file=sys.stderr)
            return 2
        jpath = args[i + 1]
    folders = sorted(d for d in glob.glob(os.path.join(BASE, "*")) if os.path.isdir(d)
                     and os.path.exists(os.path.join(d, "analysis.md")) and os.path.exists(os.path.join(d, "dcf_numbers.json")))
    reports, rc = [], 0
    for d in folders:
        try:
            rep = check_folder(d)
        except Exception as e:  # a checker defect on one folder is reported, never fatal to the corpus run
            rep = {"ticker": os.path.basename(d), "status": "error", "gated": False, "engine_release": None,
                   "checked": 0, "untraced": [], "integrity": [f"exception: {type(e).__name__}: {e}"], "warnings": []}
        if rel_min and not _facts.release_at_least(rep.get("engine_release"), rel_min):
            continue
        reports.append(rep)
        if rep.get("gated") and rep["status"] != "pass":
            rc = 1
        if not quiet:
            stale = sum(1 for w in rep.get("warnings") or [] if "STALE" in w)
            print(f"{rep['ticker']} {rep['status']} {rep.get('engine_release') or '-'} {rep.get('checked', 0)} "
                  f"{len(rep.get('untraced') or [])} {stale}")
    counts = {}
    for r in reports:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    un = sorted(len(r.get("untraced") or []) for r in reports)
    worst = sorted(reports, key=lambda r: -len(r.get("untraced") or []))[:10]
    print(f"check_quotes.py --all: {len(reports)} folders — " + ", ".join(f"{k} {v}" for k, v in sorted(counts.items()))
          + f"; gated {sum(1 for r in reports if r.get('gated'))}")
    if un:
        print(f"untraced per folder: min {un[0]} p25 {_quantile(un, .25)} median {_quantile(un, .5)} "
              f"p75 {_quantile(un, .75)} p90 {_quantile(un, .9)} max {un[-1]}")
        print("worst: " + ", ".join(f"{r['ticker']} {len(r.get('untraced') or [])}" for r in worst))
    if jpath:
        with open(jpath, "w", encoding="utf-8") as f:
            json.dump(reports, f, indent=1, ensure_ascii=False)
    return rc


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    if not args or args[0] in ("-h", "--help"):
        print(__doc__.split("\n\n")[1] if __doc__ else "usage: check_quotes.py <T> | --all | --save-run <T> <label>")
        return 2 if not args else 0
    if args[0] == "--all":
        return _all(args[1:])
    if args[0] == "--save-run":
        rest = [a for a in args[1:] if a != "--replace"]
        if len(rest) != 2:
            print("check_quotes.py: usage --save-run <TICKER> <label> [--replace]", file=sys.stderr)
            return 2
        rc, msg = save_run(os.path.join(BASE, rest[0].upper()), rest[1], replace="--replace" in args)
        print(msg, file=sys.stderr if rc else sys.stdout)
        return rc
    as_json, strict = "--json" in args, "--strict" in args
    tickers = [a for a in args if not a.startswith("--")]
    if not tickers or any(a.startswith("--") and a not in ("--json", "--strict") for a in args):
        print("check_quotes.py: usage <TICKER> [...] [--json] [--strict] | --all | --save-run <T> <label>", file=sys.stderr)
        return 2
    rc, out = 0, []
    for t in tickers:
        folder = os.path.join(BASE, t.upper())
        rep = check_folder(folder, strict=strict)
        out.append(rep)
        if not as_json:
            print(human_report(rep, folder))
        if rep["status"] == "error":
            rc = max(rc, 2)
        elif rep["status"] == "fail" or (strict and (rep["untraced"] or rep["integrity"])):
            rc = max(rc, 1)
    if as_json:
        print(json.dumps(out if len(out) > 1 else out[0], indent=1, ensure_ascii=False))
    return rc


if __name__ == "__main__":
    sys.exit(main())
