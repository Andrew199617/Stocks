#!/usr/bin/env python3
"""Site data layer (v6 presentation, 2026-10-14) — see _system/SITE_CONTRACT.md.

Usage: python3 build_site.py [--only T,T] [--force] [--attachment] [--top N]
                             [--site-dir PATH] [--quiet] [--no-prerender]

Reads every <TICKER>/ folder (the files Muse's scripts write) and derives the
JSON the static app renders:

  <site>/meta.json          build stamp, sweep progress, counts, hurdles, stale list
  <site>/index.json         one row per CURRENT company, ranked by irr_live else irr
  <site>/data/<TICKER>.json everything the company page renders
  <site>/state.json         builder bookkeeping (built_from_mtime per record)

<site> defaults to <base>/_daily/site. Incremental: a record is rebuilt only
when a file in its folder is newer than the record, the folder's file list
changed (a deleted live.json counts), or this script is newer than the record
(--force rebuilds everything). Records whose folder no longer qualifies
(score.json gone, pre-v5 numbers, an uncovered data gap) are removed.

Missing outputs (2026-10-16): everything under <site> except the app shell is
a gitignored cache, so a fresh clone has no data/ at all and a machine may
have lost it. A record whose data/<T>.json is missing is always built — even
outside --only, so the index never silently loses a company — whatever
state.json or index.json still claim; state.json entries for tickers that
are no longer current are dropped; meta.json and index.json are written on
every run (an unreadable state.json / index.json / queue.json / registry
counts as absent).

Keys: every company is served under score.json's `ticker` (upper-cased; the
folder name when absent) — data/<ticker>.json, the index row, the attachment
and state.json all agree; the folder stays in record.folder. Two folders
claiming one ticker: the first in sorted order is served, the other reported.

Robustness: a malformed folder (non-object JSON, lists where objects belong,
NaN/inf in a verbatim file or CSV) never aborts the run — nested shapes are
coerced, non-finite floats become null, and a folder whose record still fails
to build is logged to stderr (`build_site: FAILED <T>: ...`), keeps its
previous row/record if any, and is listed in meta.failed / meta.notes.

Watchlist: _system/watchlist.json tickers are listed in meta.watchlist (file
order) with the names outside the universe (over $40B, no page) repeated in
meta.watchlist_outside, and flagged as `watchlist: bool` on every index row
and meta.stale entry; the flag is re-derived on every run from the current
list (not part of the skip check), so the index is authoritative over a
skipped record's `row`. Without the file the universe.csv watchlist column
is the list.

Statements / profile / intraday (2026-10-15): <T>/statements.json
(statements.py) is copied to <site>/data/<T>.statements.json next to the
record — never inside it, never in the attachment — under the same
incremental rule, removed with the record; the row carries has.statements.
<T>/profile.json (profile.py) is embedded as record.profile (kept in the
attachment) with has.profile on the row. record.prices carries
prices.intraday / sessions_5d / warnings verbatim; the attachment drops
sessions_5d (and daily_1y) and keeps intraday.

Street (2026-10-16): profile.py writes the Nasdaq Street block and market
data to <T>/street.json (a gitignored cache, rewritten on every pull) and
keeps profile.json for the SEC-derived About / filings (committed, rewritten
only when its content changes). The builder puts street.json's `street` and
`market` back at record.profile.street / record.profile.market and its
fetched_at at record.profile.street_fetched_at, so the app reads the same
paths; without street.json the legacy street / market keys of an older
profile.json are used, else null. record.profile (whenever either file
exists) always carries the key street_fetched_at: null without street.json
and without a legacy block (the app reads the key's presence as "the Street
pull has not run yet" rather than "a record built before the split").
street.json is an ordinary folder file, so a new pull rebuilds the record
like any other changed file.

--attachment inlines <site>/index.html + app.css + app.js (or a placeholder
shell when the app is not there yet) with window.SITE_DATA = {meta, index,
records of the top N rows (default 150), trimmed} into
<base>/_daily/ranking-<America/New_York date>.html and <base>/_daily/latest.html
(gitignored), and writes the compact committed snapshot
<base>/_daily/history/ranking-<same date>.csv: one row per ranked company,
the columns the daily chat message quotes (HISTORY_COLUMNS), ordered by live
IRR desc, then scored IRR desc, then ticker. A --site-dir build writes both
next to that directory instead (its parent), never into the real _daily/.

Pre-rendered attachment (2026-10-16): --attachment also runs the app's own
renderers in Node (_system/prerender.js) over the exact SITE_DATA payload
and inlines the finished HTML as a static layer inside #app — the ranking
with a CSS-radio tier filter, one :target section per company with every
tab pane stacked visible, charts as inline SVG — because the iOS chat
attachment viewer never runs the app's script and the file otherwise sits
on "Loading the ranking…". A one-line cleanup script removes the layer
during parsing when JavaScript does run, so the interactive app boots into
the pristine shell; app.js and SITE_DATA are inlined unchanged either way.
Node missing or the pre-render failing aborts the build BEFORE the previous
attachment is overwritten (an unrendered file must never ship silently);
--no-prerender is the emergency opt-out. Data-layer builds (no --attachment)
never invoke Node.

Dividends at the last close (2026-10-16): fundamentals.json is committed and
no longer rewritten for a new close alone — its price leaves are volatile
(fundamentals.PRICE_LEAVES). When <T>/prices.json's close is not older than
the dividends block's price_date (and differs from it), the block is
repriced with fundamentals.price_dividends — the function fundamentals.py
writes the block with — at stats.last / last_date ("prices.json
stats.last"), so the Dividends tab and the row's dividend_yield /
shareholder_yield / shareholder_yield_label / shareholder_yield_bound read
the latest close and equal what fundamentals.py would write at that price.
Without prices.json (a fresh clone) or with an older close, for a block
written before 5.4.4, or across a split since scoring (below: the block's
filed DPS and share count would meet a post-split close), the block is
shown as written.

Live older than the score (2026-10-16): Nasdaq posts a session's close hours
after it ends, so a live.json repriced on scoring day can carry the close
BEFORE the scored session (reprice's basis_check.method
"no_close_since_scoring") — older than the verdict's own price. Such a
live.json (price_date earlier than score.json analysis_date / the run's
as_of) is not shown as current: record.live is null, record.live_withheld =
{reason, note, price, price_date, scored_date, method}, the row's live
fields stay null with row.live_withheld = true, so the ranking sorts on the
scored IRR and the page shows the scored figures until a close after the
scored session arrives.

Splits since scoring (2026-10-16): reprice.py restates live.json in today's
share units and records split_factor (new shares per scored-run share). The
record's run figures (score.json, dcf_numbers.json, the run's history CSV
and ttm.json, the replayed forecast and the index row) are in the scored
run's units; when the live.json shown carries split_factor != 1 every
per-share run figure (SPLIT_DIVIDE: prices, IVs, hurdle prices, OE per
share, the forecast paths and sensitivity IVs) is divided by it and the
run's share counts (SPLIT_MULTIPLY) multiplied by it, so the page compares
like with like against today's close; IRRs, tiers, upside and market caps
do not change. record.split_restated = {factor, split, scored_date,
price_date, fields, as_scored, note}, row.split_restated = {factor, split}
(null otherwise).

Every number comes from a file; the only computation here is the forecast
replay through the engine's own functions (dcf_engine.replay_paths,
present_value, solve_irr, tier_for_irr) when a pre-5.4 run lacks the stored
values — including solve_irr's at-floor flag for a scored scenario IRR the run
did not flag itself (the recorded IRR is never replaced) — plus the display
arithmetic (upside = IV / price − 1) the v2 pages did, the dividends
repricing above (fundamentals.price_dividends) and the split restatement
(division by the factor reprice.py found). Stdlib only. The loaders and
derivations were copied from build_daily_html.py (v2, being retired) —
nothing is imported from it.
"""
import argparse
import csv
import datetime
import glob
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
try:
    import dcf_engine as ENGINE
except Exception:  # the data layer still builds without the forecast replay
    ENGINE = None
try:  # price_dividends: the dividends block at a newer close, with the code fundamentals.py writes it with
    import fundamentals as FUND
except Exception:  # the data layer still builds; dividends blocks are then shown as written
    FUND = None

DATA_VERSION = 1
HURDLES = {"S": 0.25, "A": 0.20, "B": 0.15, "C": 0.10}
LABELS = ["super_bear", "bear", "base", "bull", "super_bull"]
RATES = (10, 12, 15, 20, 25)
TABS = ["overview", "financials", "dividends", "segments", "forecast", "analysis", "data"]
NY = ZoneInfo("America/New_York")
COMPANY_FILES = ("score.json", "dcf_numbers.json", "financials_history.csv", "fundamentals.json", "prices.json",
                 "live.json", "segments.json", "ttm.json", "judgment.json", "analysis.md", "second_pass.md",
                 "profile.json", "statements.json", "street.json")
STATEMENTS_SUFFIX = ".statements.json"  # data/<T>.statements.json — served next to the record, loaded on demand
DEFAULT_GTERM = getattr(ENGINE, "DEFAULT_GTERM", 0.025)
# _daily/history/ranking-<date>.csv (committed): what the daily chat message quotes, one row per ranked company
HISTORY_COLUMNS = ("rank", "ticker", "name", "sector_misfit", "tier_scored", "irr_scored", "tier_live", "irr_live",
                   "band_low_tier", "band_high_tier", "price", "price_date", "iv15", "upside15_pct",
                   "analysis_date", "engine_release", "alert_eligible", "watchlist")
# Split restatement (see the module docstring): dotted paths in the record, `*` = every key / item at that level.
# SPLIT_DIVIDE holds every per-share figure of the scored run the page shows; SPLIT_MULTIPLY its share counts.
_IV_KEYS = tuple(f"iv_at_{r}" for r in RATES)
SPLIT_DIVIDE = (tuple(f"score.{k}" for k in ("price", "base_oe_per_share") + _IV_KEYS)
                + tuple(f"score.scenarios.*.{k}" for k in _IV_KEYS)
                + ("score.override_impact.base_oe_without_override", "score.override_impact.base_oe_with_override",
                   "score.second_pass.prior_iv_at_15")
                + tuple(f"numbers.{k}" for k in ("price", "base_oe_per_share", "base_oe_latest_per_share", "base_oe_normalized_per_share") + _IV_KEYS)
                + tuple(f"numbers.scenarios.*.{k}" for k in _IV_KEYS) + tuple(f"numbers.weighted.{k}" for k in _IV_KEYS)
                + ("numbers.hurdle_prices.*", "numbers.inputs.base_oe_ps_arg",
                   "numbers.override_impact.base_oe_per_share_zero_fill", "numbers.override_impact.base_oe_per_share_final")
                + ("forecast.paths.*.*", "forecast.hurdle_prices.*", "forecast.inputs.base_oe_ps_arg")
                + tuple(f"forecast.sensitivity.*.{r}" for r in RATES)
                + tuple(f"row.{k}" for k in ("price", "iv15", "iv12", "iv20", "iv25"))
                + ("ttm.ttm_oe_per_share",))
SPLIT_MULTIPLY = ("numbers.shares_diluted_latest", "history.*.shares_diluted", "ttm.ttm_shares_diluted")
_NUM_RX = re.compile(r"-?\d+(\.\d+)?([eE][-+]?\d+)?")
_INT_RX = re.compile(r"-?\d+")


# ---------------------------------------------------------------- helpers (copied from build_daily_html.py)
def num(v):
    try:
        if v is None or v == "" or isinstance(v, bool):
            return None
        f = float(v)
        return f if f == f and f not in (float("inf"), float("-inf")) else None
    except Exception:
        return None


def jload(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _d(v):
    """A nested field that must be an object: the dict itself, else {} (a list,
    string or number where an object belongs renders as absent, never crashes)."""
    return v if isinstance(v, dict) else {}


def _l(v):
    return v if isinstance(v, list) else []


def finite(o):
    """Deep copy with every non-finite float (NaN / ±inf — Python's json.dump
    writes them, json.load reads them back) replaced by None, so dump()'s
    allow_nan=False never trips and the app sees null."""
    if isinstance(o, float):
        return o if math.isfinite(o) else None
    if isinstance(o, dict):
        return {k: finite(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [finite(v) for v in o]
    return o


def tread(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except Exception:
        return None


def is_current(numbers):
    numbers = _d(numbers)
    ev = numbers.get("engine_version")
    return isinstance(ev, (int, float)) and not isinstance(ev, bool) and ev >= 5 and "data_gap" in numbers


def tier_for_irr(irr):
    if irr is None:
        return None
    if ENGINE is not None:
        return ENGINE.tier_for_irr(irr)
    return "S" if irr >= 0.25 else "A" if irr >= 0.20 else "B" if irr >= 0.15 else "C" if irr >= 0.10 else "D"


def coerce_cell(v):
    """financials_history.csv cell → number / bool / None / string."""
    if v is None:
        return None
    s = str(v).strip()
    if s == "":
        return None
    if s in ("True", "False"):
        return s == "True"
    if _INT_RX.fullmatch(s):
        try:
            return int(s)
        except ValueError:
            return s
    if _NUM_RX.fullmatch(s):
        f = float(s)
        return f if math.isfinite(f) else None  # 1e400 parses as inf
    return s


def read_history(path):
    try:
        with open(path, encoding="utf-8", newline="") as f:
            return [{k: coerce_cell(v) for k, v in r.items() if k is not None} for r in csv.DictReader(f)]
    except Exception:
        return []


def folder_files(folder):
    try:
        return sorted(f for f in os.listdir(folder) if not f.startswith(".") and os.path.isfile(os.path.join(folder, f)))
    except Exception:
        return []


def newest_mtime(folder, files=None):
    m = 0.0
    for f in (folder_files(folder) if files is None else files):
        try:
            m = max(m, os.path.getmtime(os.path.join(folder, f)))
        except OSError:
            pass
    return m


def universe_tickers(base):
    """Upper-cased tickers of _system/universe.csv, and the rows flagged in its
    watchlist column (queue order). Both empty when the file is unreadable."""
    allt, wl = [], []
    try:
        with open(os.path.join(base, "_system", "universe.csv"), encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                t = (r.get("ticker") or "").strip().upper()
                if not t:
                    continue
                allt.append(t)
                if (r.get("watchlist") or "").strip().lower() in ("yes", "y", "true", "1"):
                    wl.append(t)
    except Exception:
        return [], []
    return allt, wl


def load_watchlist(base):
    """_system/watchlist.json → (tickers, outside, entries). `tickers` keeps
    the FILE ORDER (upper-cased, trimmed, duplicates / blanks / non-strings
    dropped; entries may be {ticker, in_universe, name} objects or bare
    strings). `outside` = the tickers not in the universe (over $40B, no page):
    an entry's own in_universe flag when it carries one, else the universe.csv
    membership test when that file is readable. `entries` = [{ticker,
    in_universe, name}] in the same order. Without the file (or with a
    malformed one) the universe.csv watchlist column is the list, in queue
    order, and nothing is outside."""
    raw = _d(jload(os.path.join(base, "_system", "watchlist.json"))).get("tickers")
    uni, uni_wl = universe_tickers(base)
    uni_set = set(uni)
    tickers, outside, entries, seen = [], [], [], set()
    if not isinstance(raw, list):
        for t in uni_wl:
            if t not in seen:
                seen.add(t)
                tickers.append(t)
                entries.append({"ticker": t, "in_universe": True, "name": None})
        return tickers, outside, entries
    for e in raw:
        t = e.get("ticker") if isinstance(e, dict) else e
        if not isinstance(t, str) or not t.strip():
            continue
        t = t.strip().upper()
        if t in seen:
            continue
        seen.add(t)
        iu = e.get("in_universe") if isinstance(e, dict) else None
        if not isinstance(iu, bool):
            iu = (t in uni_set) if uni_set else True
        name = e.get("name") if isinstance(e, dict) and isinstance(e.get("name"), str) else None
        tickers.append(t)
        entries.append({"ticker": t, "in_universe": iu, "name": name})
        if not iu:
            outside.append(t)
    return tickers, outside, entries


# ---------------------------------------------------------------- loading
def load_light(folder):
    """score.json + dcf_numbers.json only — enough to classify a folder.
    Either file that is not a JSON object counts as absent ({})."""
    return {"folder": os.path.basename(folder), "path": folder,
            "score": _d(jload(os.path.join(folder, "score.json"))),
            "numbers": _d(jload(os.path.join(folder, "dcf_numbers.json")))}


def ticker_key(c):
    """The key a company is served under: score.json's `ticker` (upper-cased,
    trimmed), else the folder name. data/<key>.json, index rows and the
    attachment all agree on it; the folder stays in record.folder."""
    t = c["score"].get("ticker")
    t = t.strip().upper() if isinstance(t, str) else ""
    # Re-verification finding: the served key becomes a file name under data/
    # and a hash token — it must be a plain ticker (letters, digits, '.', '-'),
    # never an arbitrary string from a JSON file. Anything else falls back to
    # the folder name (already a ticker directory), reported on stderr.
    if t and not re.fullmatch(r"[A-Z0-9][A-Z0-9.\-]{0,11}", t):
        print(f"build_site: score.json ticker {t!r} in {c['folder']} is not a plain ticker — serving under the folder name", file=sys.stderr)
        t = ""
    return t or c["folder"]


def load_company(folder):
    c = load_light(folder)
    c["history"] = read_history(os.path.join(folder, "financials_history.csv"))
    c["fund"] = jload(os.path.join(folder, "fundamentals.json"))
    c["prices"] = jload(os.path.join(folder, "prices.json"))
    c["ttm"] = jload(os.path.join(folder, "ttm.json"))
    c["live"] = jload(os.path.join(folder, "live.json"))
    c["segments"] = jload(os.path.join(folder, "segments.json"))
    c["judgment"] = jload(os.path.join(folder, "judgment.json"))
    c["profile"] = jload(os.path.join(folder, "profile.json"))
    c["street"] = jload(os.path.join(folder, "street.json"))  # merged into record.profile (profile_with_street)
    c["statements"] = jload(os.path.join(folder, "statements.json"))  # copied next to the record, never embedded
    c["analysis_md"] = tread(os.path.join(folder, "analysis.md"))
    c["second_pass_md"] = tread(os.path.join(folder, "second_pass.md"))
    c["files"] = folder_files(folder)
    for k in ("fund", "prices", "ttm", "live", "segments", "judgment", "profile", "street", "statements"):
        if c[k] is not None and not isinstance(c[k], dict):
            c[k] = None  # a malformed file renders as absent
    return c


def qualifies(c):
    """A CURRENT company: scored, engine v5+, no uncovered data gap."""
    return bool(c["score"]) and is_current(c["numbers"]) and not c["numbers"].get("data_gap_uncovered")


def flags_of(s, n):
    return [str(f) for f in (_l(s.get("fragility_flags")) or _l(n.get("fragility_flags")))]


def model_fit(c):
    s = c["score"]
    if isinstance(s.get("model_fit"), str) and s.get("model_fit"):
        return s["model_fit"]
    return "misfit" if any(f.startswith("SECTOR_MODEL_MISMATCH") for f in flags_of(s, c["numbers"])) else "modeled"


def live_ok(lv):
    return isinstance(lv, dict) and num(lv.get("price")) is not None and num(lv.get("irr_weighted")) is not None


def _date10(v):
    return v[:10] if isinstance(v, str) and len(v) >= 10 else None


def live_shown(c):
    """(live, withheld): the live.json the page shows as current, else None,
    and why it was withheld (None when it was not). A live.json whose close
    (price_date) is older than the scored analysis — score.json
    analysis_date or the run's as_of (live.scored_date), whichever is later —
    reprices the scored paths at a price older than the verdict's own: Nasdaq
    had not posted the scored session yet (reprice's basis_check.method
    "no_close_since_scoring"). A live.json whose run (scored_date) predates
    score.json's analysis_date belongs to an earlier run of a re-scored name
    and is withheld too. The scored figures are then the latest available
    (Andrew's ruling, 2026-10-20: never described as "pending")."""
    lv = c.get("live")
    if not live_ok(lv):
        return None, None
    pd = _date10(lv.get("price_date"))
    sa, ls = _date10(_d(c.get("score")).get("analysis_date")), _date10(lv.get("scored_date"))
    if sa and ls and ls < sa:
        # live.json left over from an earlier run (the name was re-scored and
        # reprice.py has not run since): its paths are not the verdict's
        return None, {"reason": "live_from_earlier_run", "price": num(lv.get("price")), "price_date": pd, "scored_date": sa,
                      "method": None,
                      "note": (f"The live repricing on file is from the {ls} run, before the current score ({sa}); "
                               "the scored figures are the latest available.")}
    scored = [d for d in (sa, ls) if d]
    sd = max(scored) if scored else None
    if pd is None or sd is None or pd >= sd:
        return lv, None
    method = _d(lv.get("basis_check")).get("method")
    return None, {"reason": "live_older_than_score", "price": num(lv.get("price")), "price_date": pd, "scored_date": sd,
                  "method": method if isinstance(method, str) else None,
                  "note": (f"The last close on file ({pd}) predates the scored analysis ({sd}) — no close after the analysis "
                           "is on file, so the scored figures are the latest available, as of the {pd} close.")}


def live_split(lv):
    """(factor, label) of a split since the scored run that reprice.py
    restated live.json for (live.split_factor, else basis_check.factor; the
    label from basis_check.split), else (None, None)."""
    if not isinstance(lv, dict):
        return None, None
    bc = _d(lv.get("basis_check"))
    f = num(lv.get("split_factor"))
    if f is None:
        f = num(bc.get("factor"))
    if f is None or f <= 0 or abs(f - 1.0) < 1e-9:
        return None, None
    label = bc.get("split") if isinstance(bc.get("split"), str) and bc.get("split") else f"{f:g}x"
    return f, label


def _scale_path(obj, parts, factor):
    """Multiply every number at the dotted path `parts` inside obj by factor,
    in place (`*` = every key of an object / item of a list). Returns how
    many numbers were scaled."""
    if not parts:
        return 0
    key, rest, n = parts[0], parts[1:], 0
    if isinstance(obj, dict):
        keys = list(obj) if key == "*" else ([key] if key in obj else [])
        for k in keys:
            if rest:
                n += _scale_path(obj[k], rest, factor)
            elif num(obj[k]) is not None:
                obj[k] = num(obj[k]) * factor
                n += 1
    elif isinstance(obj, list) and key == "*":
        for i, v in enumerate(obj):
            if rest:
                n += _scale_path(v, rest, factor)
            elif num(v) is not None:
                obj[i] = num(v) * factor
                n += 1
    return n


def restate_split(rec, factor, label, lv):
    """Restate the record's scored-run figures in today's share units (in
    place; rec is build_record's own deep copy): SPLIT_DIVIDE / factor,
    SPLIT_MULTIPLY × factor. Sets record.split_restated and
    row.split_restated."""
    s = _d(rec.get("score"))
    as_scored = {k: num(s.get(k)) for k in ("price", "iv_at_15", "base_oe_per_share")}
    fields = []
    for path in SPLIT_DIVIDE:
        if _scale_path(rec, path.split("."), 1.0 / factor):
            fields.append(path)
    for path in SPLIT_MULTIPLY:
        if _scale_path(rec, path.split("."), factor):
            fields.append(path)
    scored_date = lv.get("scored_date") if isinstance(lv.get("scored_date"), str) else s.get("analysis_date")
    rec["split_restated"] = {
        "factor": factor, "split": label, "scored_date": scored_date,
        "price_date": lv.get("price_date") if isinstance(lv.get("price_date"), str) else None,
        "fields": fields, "as_scored": as_scored,
        "note": (f"A {label} split since the scored run ({scored_date}): every per-share figure of the run (prices, intrinsic "
                 f"values, hurdle prices, owner's earnings per share, the forecast paths) is divided by {factor:g} and its share "
                 f"counts multiplied by {factor:g}, so they read in today's share units next to the last close. IRRs, tiers, "
                 "upside and market cap do not change.")}
    if isinstance(rec.get("row"), dict):
        rec["row"]["split_restated"] = {"factor": factor, "split": label}


def _fund_currency(fund):
    """fundamentals.json's own currency when it is not USD, else None."""
    cur = fund.get("currency") if isinstance(fund, dict) else None
    return cur if isinstance(cur, str) and cur != "USD" else None


def dividends_unit(fund):
    """price_dividends' unit keywords for this file's dividends block (ruling-sheet Q8 bug 3, verifier round 2): {} for a
    USD file; {"currency": X} for a block that records its unit (`dividends.currency`, written only on a non-USD block
    under the one-currency rule); {"unit_unrecorded": X} for a non-USD file whose block has no key — written before
    2026-10-19, when the readers took a filed USD fact first (TLK's dividends paid is the USD 1,099,000,000 fact, CX's
    $90M, RDY's shareholder-yield leg), so the file's `currency` X is NOT the legs' unit and the yield note must not say
    it is. Either non-USD case prices no yield."""
    cur = _fund_currency(fund)
    if cur is None:
        return {}
    div = fund.get("dividends") if isinstance(fund.get("dividends"), dict) else {}
    own = div.get("currency")
    if isinstance(own, str) and own:
        return {} if own == "USD" else {"currency": own}
    return {"unit_unrecorded": cur}


def cross_currency_safe(fund):
    """Ruling-sheet Q8 bug 3: a non-USD block written before the currency rule
    still carries yields whose numerators' unit it does not record (read
    USD-first, so some are cross-currency: RDY's 310.80%, SKM's 11,076%) —
    re-price it at its OWN close with dividends_unit's keywords
    (price_dividends(unit_unrecorded=...); a block that records a non-USD
    unit: currency=...), which nulls only the yields (market cap, shares and
    the per-share basis are the block's own). Every other block is returned
    as is. build_record applies it
    when it serves a block as written (a split since scoring — verifier
    round 1: SKM's 11,076% had survived that path); priced_fundamentals when
    there is no newer close."""
    if FUND is None or _fund_currency(fund) is None or not FUND.repriceable(fund.get("dividends")):
        return fund
    unit = dividends_unit(fund)
    div = fund["dividends"]
    if not unit or not any(num(div.get(k)) is not None for k in FUND.YIELD_KEYS):
        return fund
    return dict(fund, dividends=FUND.price_dividends(div, div.get("price"), div.get("price_date"), div.get("price_source"), **unit))


def priced_fundamentals(fund, prices, ads_ratio=None):
    """fundamentals.json as the page shows it: the dividends block repriced
    with fundamentals.price_dividends at prices.json stats.last / last_date
    when that close is not older than the block's own price_date and differs
    from the block's price (a same-day close supersedes a score.json
    analysis-time quote). A shallow copy with a new `dividends`; the input is
    not modified. Shown as written without prices.json, with an older close,
    for a block written before 5.4.4 (fundamentals.repriceable), or without
    fundamentals.py. The close is passed as filed (a JSON number, as
    fundamentals._read_price reads it), never a coerced string. `ads_ratio`
    (the run's recorded ratio, from dcf_numbers.json) backfills a dividends
    block written before blocks carried it, so a legacy ADS block reprices
    on the traded-cap basis instead of price x ordinary shares.
    Ruling-sheet Q8 bug 3 (Andrew, 2026-10-19): the block is priced in its
    own unit (dividends_unit) — a non-USD block's yields are null (its DPS
    and flows are not in the price's currency); a non-USD file's block
    written before that rule records no unit, so its yields are null too and
    the note says the unit is unrecorded (verifier round 2: the file's
    `currency` is not its legs' unit — CX's $90M is a USD fact); such a block
    that still shows a yield is re-priced at its own close, so the page never
    shows a cross-currency yield while the file awaits a refresh."""
    if FUND is None or not isinstance(fund, dict) or not FUND.repriceable(fund.get("dividends")):
        return fund
    unit = dividends_unit(fund)
    div = fund["dividends"]
    if not isinstance(div.get("ads_ratio"), (int, float)) and isinstance(ads_ratio, (int, float)) \
            and not isinstance(ads_ratio, bool) and ads_ratio > 0:
        div = dict(div, ads_ratio=ads_ratio)
    st = _d(_d(prices).get("stats"))
    last, last_date = st.get("last"), _date10(st.get("last_date"))
    if not isinstance(last, (int, float)) or isinstance(last, bool) or not math.isfinite(last) or last <= 0 or last_date is None:
        return cross_currency_safe(fund)
    pd = _date10(div.get("price_date"))
    if pd is not None and (last_date < pd or (last_date == pd and num(div.get("price")) == last
                                              and div.get("price_source") == FUND.PRICES_JSON_SOURCE)):
        return cross_currency_safe(fund)
    return dict(fund, dividends=FUND.price_dividends(div, st.get("last"), st.get("last_date"), FUND.PRICES_JSON_SOURCE, **unit))


def profile_with_street(profile, street):
    """record.profile: profile.json (SEC-derived About / filings, committed)
    with the Street block and market data put back where the app reads them
    — profile.street, profile.market, profile.street_fetched_at. Since
    2026-10-16 profile.py writes those to street.json (a gitignored cache):
    when street.json carries a key its value wins (null included: a newer
    pull with no coverage is not overridden by an older profile.json);
    otherwise the legacy key of an older profile.json is used, else null.
    street_fetched_at is street.json's fetched_at, or the legacy
    profile.json's fetched_at when the legacy block is the one shown. None
    when neither file is a usable object."""
    prof = profile if isinstance(profile, dict) else None
    st = street if isinstance(street, dict) else None
    if prof is None and st is None:
        return None
    out = dict(prof or {})
    from_street = from_legacy = False
    for key in ("street", "market"):
        if st is not None and key in st:
            out[key] = _d(st.get(key)) or None
            from_street = True
        else:
            out[key] = _d(out.get(key)) or None
            from_legacy = from_legacy or out[key] is not None
    fa = st.get("fetched_at") if from_street else (out.get("fetched_at") if from_legacy else None)
    out["street_fetched_at"] = fa if isinstance(fa, str) else None
    return out


# ---------------------------------------------------------------- forecast replay (engine functions)
def forecast_paths(n):
    """(paths, growth_paths, replayed). Stored paths when the run carries them
    (5.4+), else the engine's own replay from the recorded inputs."""
    if _d(n.get("paths")) and _d(n.get("growth_paths")):
        return n["paths"], n["growth_paths"], False
    if ENGINE is None:
        return None, None, False
    if hasattr(ENGINE, "replay_paths"):
        try:
            paths, gpaths = ENGINE.replay_paths(n)
        except Exception:
            return None, None, False
        return paths, gpaths, bool(paths)
    # local copy of build_daily_html.forecast_paths
    inp, scn = _d(n.get("inputs")), _d(n.get("scenarios"))
    base, gb = num(n.get("base_oe_per_share")), num(n.get("g_base"))
    if not inp or base is None or gb is None or not scn:
        return None, None, False
    gterm = _gterm(n)
    cap = ENGINE.cap_years_for_moat(inp.get("moat", 5))
    paths, gpaths = {}, {}
    try:
        for i, k in enumerate(LABELS):
            g0 = max(ENGINE.GROWTH_FLOOR_START, min(ENGINE.GROWTH_CAP_START, gb + inp["offsets"][i]))
            paths[k] = ENGINE.project_path(base * inp["mults"][i], g0, cap, gterm)
            gpaths[k] = ENGINE.growth_path(g0, cap, gterm)
        probs = inp["probs"]
        paths["weighted"] = [sum(probs[i] * paths[LABELS[i]][t] for i in range(5)) for t in range(len(paths["base"]))]
    except Exception:
        return None, None, False
    return paths, gpaths, True


def _gterm(n):
    """The run's terminal growth: inputs.g_terminal, else the top-level copy,
    else the engine default. Tested for None, never truthiness — a recorded
    0.0 is a valid assumption (review finding: `or` replaced it with 2.5%)."""
    for v in (_d(n.get("inputs")).get("g_terminal"), n.get("g_terminal")):
        g = num(v)
        if g is not None:
            return g
    return DEFAULT_GTERM


def _scored_price(n, s):
    """The price the scored IRRs were solved at: score.json's copy, else the run's own."""
    return num(s.get("price")) or num(n.get("price"))


def scored_floor(recorded, flows, px, g):
    """Whether a SCORED IRR sits at the solver's floor. The first boolean in
    `recorded` (the run's own flags — engine 5.4 writes them per scenario and
    for the weighted case) wins. A pre-5.4 run recorded none, so the flag is
    inferred through the engine: solve_irr's at_floor on the replayed flows at
    the scored price. Only the flag is taken from the replay — the recorded
    (historical) IRR is never replaced. None when there is neither a flag nor
    anything to replay."""
    for v in recorded:
        if isinstance(v, bool):
            return v
    flows = _l(flows)
    if not flows or px is None or px <= 0 or ENGINE is None or not hasattr(ENGINE, "solve_irr"):
        return None
    try:
        return bool(ENGINE.solve_irr(flows, px, g)[2])
    except Exception:
        return None


def _weighted_floor_recorded(n, s):
    """The run's own flags for the weighted IRR, in precedence order."""
    return (s.get("irr_at_floor"), _d(n.get("diagnostics")).get("irr_at_floor"), _d(n.get("weighted")).get("irr_at_floor"))


def hurdle_prices(n, s, paths):
    """Weighted IV at 15 / 20 / 25% — stored by engine 5.4 (numbers.hurdle_prices
    or score.iv_at_20/25); replayed through present_value otherwise."""
    if _d(n.get("hurdle_prices")):
        return {str(k): num(v) for k, v in n["hurdle_prices"].items()}
    stored = {"15": num(s.get("iv_at_15")), "20": num(s.get("iv_at_20")), "25": num(s.get("iv_at_25"))}
    if all(v is not None for v in stored.values()):
        return stored
    if not paths or ENGINE is None or not paths.get("weighted"):
        return {"15": num(s.get("iv_at_15")) if s.get("iv_at_15") is not None else num(n.get("iv_at_15")), "20": None, "25": None} if (s.get("iv_at_15") is not None or n.get("iv_at_15") is not None) else None
    g, w = _gterm(n), paths["weighted"]
    return {"15": ENGINE.present_value(w, 0.15, g), "20": ENGINE.present_value(w, 0.20, g), "25": ENGINE.present_value(w, 0.25, g)}


def scenario_sensitivity(n, s, paths, lv):
    """{label: {"10".."25": iv, irr, irr_at_floor, irr_live, irr_live_at_floor}}
    from stored values (5.4) or present_value on the replayed paths; irr_live
    from live.json. irr_at_floor marks the SCORED IRR: the run's own flag when
    recorded, else solve_irr's flag on the replayed flows at the scored price
    (scored_floor); null when there is no scored IRR or nothing to decide it."""
    scn = _d(n.get("scenarios")) or _d(s.get("scenarios"))
    if not scn:
        return None
    g = _gterm(n)
    px = _scored_price(n, s)
    live = lv if live_ok(lv) else None
    paths = _d(paths)
    out = {}
    for k in LABELS + ["weighted"]:
        r = _d(scn.get(k)) if k != "weighted" else _d(n.get("weighted"))
        row = {}
        for rate in RATES:
            v = r.get(f"iv_at_{rate}")
            if v is None and k == "weighted" and rate in (15, 12) and s.get(f"iv_at_{rate}") is not None:
                v = s.get(f"iv_at_{rate}")
            if v is None and ENGINE is not None and _l(paths.get(k)):
                try:
                    v = ENGINE.present_value(paths[k], rate / 100, g)
                except Exception:
                    v = None
            row[str(rate)] = num(v)
        row["irr"] = num(r.get("irr")) if k != "weighted" else (num(r.get("irr")) if r.get("irr") is not None else num(n.get("implied_irr_weighted") if n.get("implied_irr_weighted") is not None else s.get("implied_irr")))
        recorded = (r.get("irr_at_floor"),) if k != "weighted" else _weighted_floor_recorded(n, s)
        row["irr_at_floor"] = scored_floor(recorded, paths.get(k), px, g) if row["irr"] is not None else None
        if live:
            lscn = _d(_d(live.get("scenarios")).get(k))
            lr = live.get("irr_weighted") if k == "weighted" else lscn.get("irr")
            lf = live.get("irr_at_floor") if k == "weighted" else lscn.get("irr_at_floor")
            row["irr_live"], row["irr_live_at_floor"] = num(lr), (bool(lf) if lf is not None else None)
        else:
            row["irr_live"], row["irr_live_at_floor"] = None, None
        out[k] = row
    return out


def forecast_block(c, paths, gpaths, replayed, sens, hp):
    n, s = c["numbers"], c["score"]
    inp = _d(n.get("inputs"))
    return {"paths": paths, "growth_paths": gpaths, "sensitivity": sens, "hurdle_prices": hp, "inputs": inp or None,
            "g_base": num(n.get("g_base")), "g_blend": num(n.get("g_blend")), "g_terminal": _gterm(n),
            "cap_years": num(n.get("cap_years")) if n.get("cap_years") is not None else num(s.get("cap_years")),
            "growth_components": _d(n.get("growth_components")), "growth_components_adjusted": _d(n.get("growth_components_adjusted")) or None,
            "share_cagr": num(n.get("share_cagr")), "share_count_adj": num(n.get("share_count_adj")), "share_adj_basis": n.get("share_adj_basis"),
            "replayed": bool(replayed)}


def irr_at_floor_flag(c, paths):
    """score.irr_at_floor (5.4) → diagnostics.irr_at_floor → weighted.irr_at_floor
    → for an older run, solve_irr's at-floor flag on the replayed weighted path
    at the scored price (scored_floor; the same answer as
    forecast.sensitivity.weighted.irr_at_floor). False when undecidable."""
    s, n = c["score"], c["numbers"]
    return bool(scored_floor(_weighted_floor_recorded(n, s), _d(paths).get("weighted"), _scored_price(n, s), _gterm(n)))


# ---------------------------------------------------------------- index row
def _tier(v):
    return v if isinstance(v, str) and v in ("S", "A", "B", "C", "D", "F") else None


def registry_entries(registry, c, ticker):
    return [e for e in (_l(registry.get(ticker)) or _l(registry.get(c["folder"])) or _l(registry.get(c["score"].get("ticker")))) if isinstance(e, dict)]


def index_row(c, registry, paths, hp, watchlist=()):
    s, n = c["score"], c["numbers"]
    lv = c.get("live") if live_ok(c.get("live")) else None
    scn = _d(n.get("scenarios")) or _d(s.get("scenarios"))
    diag = _d(n.get("diagnostics"))
    tier_by_numbers = _tier(s.get("tier_by_numbers")) or _tier(n.get("tier_by_numbers"))
    tier = _tier(s.get("tier_final")) or tier_by_numbers or "?"
    irr = num(s.get("implied_irr")) if s.get("implied_irr") is not None else num(n.get("implied_irr_weighted"))
    irr_bear = num(s.get("irr_bear")) if s.get("irr_bear") is not None else num(_d(scn.get("bear")).get("irr"))
    irr_bull = num(s.get("irr_bull")) if s.get("irr_bull") is not None else num(_d(scn.get("bull")).get("irr"))
    price = num(s.get("price")) if s.get("price") is not None else num(n.get("price"))
    st = _d(_d(c.get("prices")).get("stats"))
    div = _d(c.get("fund")).get("dividends")
    div = div if isinstance(div, dict) else None
    ticker = c.get("ticker") or ticker_key(c)
    entries = registry_entries(registry, c, ticker)
    imp = _d(s.get("override_impact"))
    sp = s.get("second_pass") if isinstance(s.get("second_pass"), dict) else None
    hp = _d(hp)
    row = {
        "ticker": ticker, "name": s.get("name") if isinstance(s.get("name"), str) else (n.get("name") if isinstance(n.get("name"), str) else None),
        "sector": s.get("sector") if isinstance(s.get("sector"), str) else None,
        "fit": model_fit(c), "watchlist": ticker in watchlist,
        "tier": tier, "tier_by_numbers": tier_by_numbers, "tier_override": bool(tier_by_numbers and tier != tier_by_numbers),
        "tier_live": None, "tier_bear": _tier(s.get("tier_bear")) or tier_for_irr(irr_bear), "tier_bull": _tier(s.get("tier_bull")) or tier_for_irr(irr_bull),
        "irr": irr, "irr_live": None, "irr_bear": irr_bear, "irr_bull": irr_bull,
        "irr_at_floor": irr_at_floor_flag(c, paths), "irr_capped": bool(s.get("irr_capped") or diag.get("irr_capped")),
        "live_withheld": False, "split_restated": None,  # set by build_record (live_shown / restate_split)
        "f_subtype": s.get("f_subtype") or n.get("f_subtype"),
        "price": price, "price_live": None, "price_date": None, "ret_1y_pct": num(st.get("ret_1y_pct")),
        "iv15": num(s.get("iv_at_15")) if s.get("iv_at_15") is not None else num(n.get("iv_at_15")),
        "iv12": num(s.get("iv_at_12")) if s.get("iv_at_12") is not None else num(n.get("iv_at_12")),
        "iv20": num(hp.get("20")), "iv25": num(hp.get("25")),
        "upside15": num(s.get("upside_at_15_pct")), "upside15_live": None,
        "market_cap_b": num(s.get("market_cap_b")), "market_cap_b_live": None,
        "moat": num(s.get("moat_score")), "cap_years": num(s.get("cap_years")), "confidence": s.get("confidence"),
        "confidence_capped": bool(s.get("confidence_capped")),
        "one_liner": s.get("one_liner"), "analysis_date": s.get("analysis_date"), "engine_release": s.get("engine_release") or n.get("engine_release"),
        "flags": flags_of(s, n),
        "overrides": [{"field": o.get("field"), "kind": o.get("kind")} for o in _l(s.get("overrides")) if isinstance(o, dict) and o.get("field")],
        "override_unblocks_tier": bool(imp.get("unblocks_tier")) or any(bool(e.get("unblocks_tier")) for e in entries),
        "second_pass": {"date": sp.get("date"), "verdict": sp.get("verdict"), "prior_tier": sp.get("prior_tier")} if sp else None,
        "alert_eligible": bool(s.get("alert_eligible")),
        "dividend_yield": num(div.get("dividend_yield")) if div else None, "shareholder_yield": num(div.get("shareholder_yield")) if div else None,
        # The fundamentals block marks partial yields (≥ lower bound, ≤ upper bound,
        # ≈ incomplete): the row carries the label so the ranking never prints a
        # bounded figure as if it were exact (review finding, dividends round 2).
        "shareholder_yield_label": (_d(_d(div.get("yields_display")).get("shareholder_yield")).get("label") if div else None),
        "shareholder_yield_bound": (_d(_d(div.get("yields_display")).get("shareholder_yield")).get("bound") if div else None),
        "has": {"prices": isinstance(c.get("prices"), dict), "fundamentals": isinstance(c.get("fund"), dict), "dividends": div is not None,
                "segments": isinstance(c.get("segments"), dict), "live": lv is not None, "analysis": c.get("analysis_md") is not None,
                "second_pass": c.get("second_pass_md") is not None,
                "statements": isinstance(c.get("statements"), dict), "profile": isinstance(c.get("profile"), dict)},
    }
    if lv:
        p = num(lv.get("price"))
        iv15 = num(lv.get("iv_at_15"))
        up = (iv15 / p - 1) * 100 if (iv15 is not None and p and p > 0) else (num(lv.get("upside_at_15")) * 100 if num(lv.get("upside_at_15")) is not None else None)
        cap = num(lv.get("market_cap_est"))
        pd = lv.get("price_date") or lv.get("as_of")
        row.update({"tier_live": _tier(lv.get("tier")) or tier, "irr_live": num(lv.get("irr_weighted")), "price_live": p,
                    "price_date": pd if isinstance(pd, str) else None, "upside15_live": up,
                    "market_cap_b_live": cap / 1e9 if cap is not None else None,
                    "irr_bear_live": num(lv.get("irr_bear")), "irr_bull_live": num(lv.get("irr_bull")),
                    "tier_bear_live": _tier(lv.get("tier_bear")), "tier_bull_live": _tier(lv.get("tier_bull")),
                    "irr_at_floor_live": bool(lv.get("irr_at_floor"))})
        # live.json's IVs are in today's share units; the row's run figures are in the scored run's until
        # restate_split, so a fallback is put back in run units first (× the split factor, 1 without a split)
        sf = live_split(lv)[0] or 1.0
        if row["iv20"] is None and num(lv.get("iv_at_20")) is not None:
            row["iv20"] = num(lv.get("iv_at_20")) * sf
        if row["iv25"] is None and num(lv.get("iv_at_25")) is not None:
            row["iv25"] = num(lv.get("iv_at_25")) * sf
    return row


def rank_key(row):
    v = row.get("irr_live") if row.get("irr_live") is not None else row.get("irr")
    return (0, -v, row.get("ticker") or "") if v is not None else (1, 0.0, row.get("ticker") or "")


# ---------------------------------------------------------------- record
def build_record(c, registry, built_at, built_from_mtime, watchlist=()):
    # the live.json shown as current (not one older than the score) and the
    # dividends block at the latest close; every derivation below reads these.
    # Across a split since scoring the block is shown as written: its filed DPS
    # and share count are in the units of the filings it was built from, and a
    # post-split close would mix the two (a 2:1 split doubles every yield).
    live, withheld = live_shown(c)
    factor, label = live_split(live)
    _ads = c["numbers"].get("ads_ratio") if isinstance(c.get("numbers"), dict) else None
    _ratio = _ads.get("ratio") if isinstance(_ads, dict) else None
    # across a split since scoring the block is served as written (never repriced) — but never with a cross-currency yield (Q8 bug 3)
    c = dict(c, live=live, fund=cross_currency_safe(c.get("fund")) if factor else priced_fundamentals(c.get("fund"), c.get("prices"), _ratio))
    s, n = c["score"], c["numbers"]
    has_scn = bool(_d(n.get("scenarios")))
    paths, gpaths, replayed = forecast_paths(n) if has_scn else (None, None, False)
    paths, gpaths = (_d(paths) or None), (_d(gpaths) or None)
    hp = hurdle_prices(n, s, paths) if has_scn else None
    sens = scenario_sensitivity(n, s, paths, live)
    row = index_row(c, registry, paths, hp, watchlist)
    row["live_withheld"] = withheld is not None
    numbers = {k: v for k, v in n.items() if k not in ("paths", "growth_paths")}
    pr = c.get("prices")
    prices = ({"source": pr.get("source"), "as_of": pr.get("as_of"), "currency": pr.get("currency"), "stats": _d(pr.get("stats")),
               "weekly": _l(pr.get("weekly")), "daily_1y": _l(pr.get("daily_1y")),
               # prices.py intraday capture (SITE_CONTRACT "prices.py intraday capture"): verbatim pass-through
               "intraday": _d(pr.get("intraday")) or None, "sessions_5d": [x for x in _l(pr.get("sessions_5d")) if isinstance(x, dict)],
               "warnings": [str(w) for w in _l(pr.get("warnings"))]} if isinstance(pr, dict) else None)
    rec = {"ticker": row["ticker"], "name": row["name"], "sector": row["sector"], "folder": c["folder"],
           "built_at": built_at, "built_from_mtime": built_from_mtime, "data_version": DATA_VERSION,
           "row": row, "score": s, "numbers": numbers,
           "forecast": forecast_block(c, paths, gpaths, replayed, sens, hp),
           "live": live, "live_withheld": withheld, "split_restated": None,
           "history": c.get("history") or [],
           "fundamentals": c.get("fund"), "prices": prices, "segments": c.get("segments"), "ttm": c.get("ttm"),
           "judgment": c.get("judgment"),
           "profile": profile_with_street(c.get("profile"), c.get("street")),
           "registry": registry_entries(registry, c, row["ticker"]),
           "analysis_md": c.get("analysis_md"), "second_pass_md": c.get("second_pass_md"),
           "files": c.get("files") or []}
    rec = finite(rec)  # NaN / inf anywhere in a verbatim file -> null; also the deep copy restate_split edits
    if factor:
        restate_split(rec, factor, label, live)
    return rec


# numbers keys the attachment copy drops: per-tag / per-period engine provenance
# the page does not render (engine 5.5 adds the capex, SBC and share-basis
# records, stripped like used_tags so the embedded record size stays flat).
TRIM_NUMBERS_KEYS = ("used_tags", "capex_provenance", "sbc_provenance", "share_basis")


def trim_record(rec):
    """The attachment copy: no judgment / ttm / prices.daily_1y /
    prices.sessions_5d / numbers.used_tags, numbers.capex_provenance,
    numbers.sbc_provenance, numbers.share_basis (prices.intraday and profile
    are kept; the statements never live in a record, so nothing to drop there)."""
    out = {k: v for k, v in rec.items() if k not in ("judgment", "ttm", "statements")}
    if isinstance(out.get("prices"), dict):
        out["prices"] = {k: v for k, v in out["prices"].items() if k not in ("daily_1y", "sessions_5d")}
    if isinstance(out.get("numbers"), dict):
        out["numbers"] = {k: v for k, v in out["numbers"].items() if k not in TRIM_NUMBERS_KEYS}
    return out


# ---------------------------------------------------------------- IO
def dump(obj, compact=True):
    return json.dumps(obj, ensure_ascii=False, separators=((",", ":") if compact else (",", ": ")), indent=(None if compact else 1), allow_nan=False)


def write_atomic(path, text, retries=20):
    """Write then os.replace. On Windows a reader (the browser, another agent,
    an antivirus scan) holding the target open makes the replace fail with
    PermissionError for a moment; retry briefly before giving up."""
    import time
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    tmp = f"{path}.tmp{os.getpid()}"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    for attempt in range(retries + 1):
        try:
            os.replace(tmp, path)
            break
        except PermissionError:
            if attempt == retries:
                try:
                    os.remove(tmp)
                except OSError:
                    pass
                raise
            time.sleep(0.05 * (attempt + 1))
    return len(text.encode("utf-8"))


def script_json(obj):
    """JSON safe inside <script>: '</' → '<\\/', '<!--' → '<\\u0021--', U+2028/9 escaped."""
    return (dump(obj).replace("</", "<\\/").replace("<!--", "<\\u0021--")
            .replace("\u2028", "\\u2028").replace("\u2029", "\\u2029"))


def load_registry(base):
    reg = {}
    for e in _l(_d(jload(os.path.join(base, "_system", "overrides_registry.json"))).get("entries")):
        if isinstance(e, dict) and isinstance(e.get("ticker"), str):
            reg.setdefault(e.get("ticker"), []).append(e)
    return reg


def sweep_counts(base):
    qd = _d(jload(os.path.join(base, "_system", "queue.json")))
    q = [e for e in _l(qd.get("queue")) if isinstance(e, dict)]
    cnt = lambda st: sum(1 for e in q if e.get("status") == st)
    total = qd.get("universe_size") if isinstance(qd.get("universe_size"), int) else len(q)
    return {"done": cnt("done"), "total": total, "pending": cnt("pending"), "blocked_data_gap": cnt("blocked_data_gap"),
            "blocked_no_data": cnt("blocked_no_data"), "in_progress": cnt("in_progress")}


# ---------------------------------------------------------------- attachment
PLACEHOLDER = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>DCF Ranking (data only)</title>
<style>:root{color-scheme:dark;--bg:#0C0E12;--fg:#ECEEF2;--mut:#9AA3B2;--card:#151922;--line:#232935;--acc:#7AA2FF}
body{margin:0;padding:16px;background:var(--bg);color:var(--fg);font:15px/1.5 "IBM Plex Sans",system-ui,sans-serif}
h1{font-size:20px;margin:0 0 4px}.note{color:var(--mut);font-size:13px}table{border-collapse:collapse;width:100%;margin-top:12px;font-variant-numeric:tabular-nums}
th,td{padding:6px 8px;border-bottom:1px solid var(--line);text-align:left}td.n,th.n{text-align:right}code{font-family:"IBM Plex Mono",monospace}</style></head>
<body><h1>Owner's-Earnings DCF Ranking — data only</h1><p class="note" id="m"></p>
<p class="note">The app shell (_daily/site/index.html + app.css + app.js) was not present when this file was built; this placeholder lists the index so the data layer can be checked on its own.</p>
<table><thead><tr><th>#</th><th>Ticker</th><th>Name</th><th>Tier</th><th class="n">IRR</th><th class="n">Live IRR</th><th class="n">Price</th><th>Embedded</th></tr></thead><tbody id="t"></tbody></table>
<!--SITE_DATA--><script>(function(){var D=window.SITE_DATA||{},m=D.meta||{},rows=D.index||[],R=D.records||{};var pct=function(v){return v==null?"\u2014":(v*100).toFixed(1)+"%"};
document.getElementById("m").textContent=(m.date||"")+" \u00b7 "+rows.length+" companies \u00b7 sweep "+((m.sweep||{}).done||0)+" / "+((m.sweep||{}).total||0)+" \u00b7 "+Object.keys(R).length+" records embedded";
var tb=document.getElementById("t");rows.forEach(function(r,i){var tr=document.createElement("tr");[i+1,r.ticker,r.name||"",r.tier,pct(r.irr),pct(r.irr_live),r.price==null?"\u2014":"$"+r.price.toFixed(2),R[r.ticker]?"yes":"no"].forEach(function(v,j){var td=document.createElement("td");if(j>=4&&j<=6)td.className="n";td.textContent=v;tr.appendChild(td)});tb.appendChild(tr)})})();</script></body></html>"""


def inline_shell(site_dir, data_js):
    """index.html with app.css / app.js inlined and the SITE_DATA script in front
    of the app script; the placeholder shell when the app files are absent."""
    html_src = tread(os.path.join(site_dir, "index.html"))
    if html_src is None:
        return PLACEHOLDER.replace("<!--SITE_DATA-->", data_js)
    css = tread(os.path.join(site_dir, "app.css"))
    js = tread(os.path.join(site_dir, "app.js"))
    out = html_src
    if css is not None:
        css_tag = re.compile(r"<link\b[^>]*\bhref=[\"'](?:\./)?app\.css[\"'][^>]*>", re.I)
        style = "<style>" + css.replace("</style", "<\\/style") + "</style>"
        out, k = css_tag.subn(lambda m: style, out, count=1)
        if not k:
            out = out.replace("</head>", style + "</head>", 1) if "</head>" in out else style + out
    js_tag = re.compile(r"<script\b[^>]*\bsrc=[\"'](?:\./)?app\.js[\"'][^>]*>\s*</script>", re.I)
    script = (data_js + "<script>" + js.replace("</script", "<\\/script") + "</script>") if js is not None else data_js
    out, k = js_tag.subn(lambda m: script, out, count=1)
    if not k:
        out = out.replace("</body>", script + "</body>", 1) if "</body>" in out else out + script
    return out


def attachment_dir(base, site_dir):
    """Where the attachment and the history CSV go: <base>/_daily for the
    default site, the parent of --site-dir otherwise (a temp-dir test build
    must never overwrite the real ranking file — review finding)."""
    default_site = os.path.normcase(os.path.abspath(os.path.join(base, "_daily", "site")))
    if os.path.normcase(os.path.abspath(site_dir)) == default_site:
        return os.path.join(base, "_daily")
    return os.path.dirname(os.path.abspath(site_dir))


def _csv_num(v, digits):
    """Fixed-point text with no thousands separators ('' for null); never '-0.00'."""
    v = num(v)
    if v is None:
        return ""
    s = f"{v:.{digits}f}"
    return s[1:] if s.startswith("-") and float(s) == 0 else s


def _csv_str(v):
    return v if isinstance(v, str) else ""


def _csv_bool(v):
    return "true" if v is True else "false"


def history_key(r):
    """Live IRR desc, then scored IRR desc, then ticker (nulls after values)."""
    lv, sc = num(r.get("irr_live")), num(r.get("irr"))
    return (lv is None, -lv if lv is not None else 0.0, sc is None, -sc if sc is not None else 0.0, str(r.get("ticker") or ""))


def history_rows(index):
    """index.json rows -> HISTORY_COLUMNS value lists, in history_key order.
    Live figures where the row has live.json, else the scored ones: price and
    price_date (the scored price's date is the analysis date), upside at 15%,
    and the bear -> bull band tiers; tier_live / irr_live stay blank without
    live data."""
    out = []
    for i, r in enumerate(sorted(index, key=history_key), 1):
        live = num(r.get("price_live")) is not None and num(r.get("irr_live")) is not None
        lo, hi = (_tier(r.get("tier_bear_live")), _tier(r.get("tier_bull_live"))) if live else (None, None)
        if lo is None or hi is None:
            lo, hi = _tier(r.get("tier_bear")), _tier(r.get("tier_bull"))
        out.append([str(i), _csv_str(r.get("ticker")), _csv_str(r.get("name")), _csv_bool(r.get("fit") == "misfit"),
                    _csv_str(_tier(r.get("tier")) or r.get("tier")), _csv_num(r.get("irr"), 6),
                    _csv_str(_tier(r.get("tier_live"))) if live else "", _csv_num(r.get("irr_live"), 6) if live else "",
                    _csv_str(lo), _csv_str(hi),
                    _csv_num(r.get("price_live") if live else r.get("price"), 2),
                    _csv_str(r.get("price_date") if live else r.get("analysis_date")),
                    _csv_num(r.get("iv15"), 2), _csv_num(r.get("upside15_live") if live else r.get("upside15"), 2),
                    _csv_str(r.get("analysis_date")), _csv_str(r.get("engine_release")),
                    _csv_bool(r.get("alert_eligible")), _csv_bool(r.get("watchlist"))])
    return out


def write_history_csv(out_dir, index, date):
    """<out_dir>/history/ranking-<date>.csv — the compact committed daily
    snapshot (UTF-8, \\n line endings, header row, plain values: IRRs as
    decimals with 6 digits, money and upside % with 2). The same day's file
    is overwritten. Returns (path, rows)."""
    import io
    rows = history_rows(index)
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(HISTORY_COLUMNS)
    w.writerows(rows)
    path = os.path.join(out_dir, "history", f"ranking-{date}.csv")
    write_atomic(path, buf.getvalue())
    return path, len(rows)


# ---------------------------------------------------------------- pre-render
class PrerenderError(Exception):
    """The attachment's static layer could not be built: the build fails and
    the previous attachment stays in place (an unrendered file must never
    replace a good one silently — the iOS chat viewer cannot run the app)."""


def find_node():
    """Node for _system/prerender.js: the PATH first, then the system install."""
    return shutil.which("node") or ("/usr/bin/node" if os.path.isfile("/usr/bin/node") else None)


def prerender_fragment(site_dir, payload):
    """Run the app's own renderers in Node (prerender.js) over the exact
    SITE_DATA payload. Returns (fragment_html, node_stdout_line). Raises
    PrerenderError on any failure; temp files live in the site dir (a
    gitignored cache) and are always removed."""
    node = find_node()
    if node is None:
        raise PrerenderError("node not found (PATH or /usr/bin/node) — cannot pre-render the attachment; "
                             "install node or pass --no-prerender")
    script = os.path.join(HERE, "prerender.js")
    if not os.path.isfile(script):
        raise PrerenderError(f"pre-render script missing: {script}")
    pf = ff = None
    try:
        fd, pf = tempfile.mkstemp(prefix=".prerender-payload-", suffix=".json", dir=site_dir)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(dump(payload))
        fd, ff = tempfile.mkstemp(prefix=".prerender-fragment-", suffix=".html", dir=site_dir)
        os.close(fd)
        try:
            r = subprocess.run([node, script, "--payload", pf, "--app", os.path.join(site_dir, "app.js"), "--out", ff],
                               capture_output=True, text=True, errors="replace", timeout=900)
        except subprocess.TimeoutExpired:
            raise PrerenderError("prerender.js timed out after 900 s")
        except OSError as e:
            raise PrerenderError(f"could not run node: {e}")
        if r.returncode != 0:
            lines = [ln.strip() for ln in (r.stderr or "").splitlines() if ln.strip()]
            why = next((ln for ln in lines if "Error" in ln), lines[0] if lines else "no stderr")
            raise PrerenderError(f"prerender.js failed (exit {r.returncode}): {why}")
        for line in (r.stderr or "").splitlines():
            print(f"build_site: {line}", file=sys.stderr)
        with open(ff, encoding="utf-8") as f:
            fragment = f.read()
        if '<div id="static">' not in fragment:
            raise PrerenderError("prerender.js output has no static layer")
        return fragment, (r.stdout or "").strip()
    finally:
        for p in (pf, ff):
            if p:
                try:
                    os.remove(p)
                except OSError:
                    pass


STATIC_CLEANUP = ("<script>(function(){var s=document.getElementById('static');"
                  "if(s&&s.parentNode)s.parentNode.removeChild(s);})();</script>")


def apply_static_layer(doc, fragment):
    """Splice the pre-rendered layer into the attachment document: it replaces
    the shell's "Loading…" card inside #app (with JavaScript on, the cleanup
    script removes it during parsing — before the app boots into the pristine
    shell — and boot would replace #app's content anyway; with JavaScript off
    it simply stays and IS the page), the shell's <noscript> "JavaScript is
    required" block goes (no longer true), and the cleanup script lands just
    before the SITE_DATA script."""
    out, k = re.subn(r'(<div id="app">)<div class="card loading"[^>]*>.*?</div>',
                     lambda m: m.group(1) + fragment.rstrip("\n"), doc, count=1, flags=re.S)
    if not k:
        raise PrerenderError("the attachment shell has no #app loading card to replace — index.html shape changed")
    out = re.sub(r"<noscript>.*?</noscript>", "", out, count=1, flags=re.S)
    i = out.find("<script>window.SITE_DATA=")
    if i < 0:
        raise PrerenderError("the attachment has no SITE_DATA script to anchor the cleanup script to")
    return out[:i] + STATIC_CLEANUP + out[i:]


def build_attachment(base, site_dir, meta, rows, records_by_ticker, top, date, prerender=True, info=None):
    """records_by_ticker and data/<T>.json are both keyed by row.ticker (the
    served key), so every top-N row with a record is embedded."""
    recs = {}
    for r in rows[:max(0, top)]:
        rec = records_by_ticker.get(r["ticker"])
        if rec is None:
            rec = jload(os.path.join(site_dir, "data", f"{r['ticker']}.json"))
        if isinstance(rec, dict):
            rec = dict(rec)
            rec["row"] = r  # the index row is authoritative (watchlist flag may have moved since the record was written)
            recs[r["ticker"]] = trim_record(rec)
    payload = {"meta": meta, "index": rows, "records": recs, "embedded_top": top, "embedded": sorted(recs)}
    data_js = "<script>window.SITE_DATA=" + script_json(payload) + ";</script>"
    doc = inline_shell(site_dir, data_js)
    if prerender:
        # Only the real app shell can be pre-rendered; the placeholder shell
        # (no index.html / app.js in the site dir) keeps its data-only page.
        if os.path.isfile(os.path.join(site_dir, "index.html")) and os.path.isfile(os.path.join(site_dir, "app.js")):
            fragment, note = prerender_fragment(site_dir, payload)
            doc = apply_static_layer(doc, fragment)
            if info is not None:
                info["prerender"] = note
        else:
            print("build_site: pre-render skipped — the app shell (index.html + app.js) is not in the site dir; "
                  "placeholder attachment as before", file=sys.stderr)
            if info is not None:
                info["prerender"] = "skipped (no app shell)"
    out_dir = attachment_dir(base, site_dir)  # next to the site directory, never the real _daily/ for a --site-dir build
    path = os.path.join(out_dir, f"ranking-{date}.html")
    size = write_atomic(path, doc)
    write_atomic(os.path.join(out_dir, "latest.html"), doc)
    return path, size, len(recs)


# ---------------------------------------------------------------- build
def build(base=None, site_dir=None, only=None, force=False, attachment=False, top=150, quiet=False, now=None, prerender=True):
    base = os.path.abspath(base or os.environ.get("STOCKS_BASE") or os.path.dirname(HERE))
    site_dir = os.path.abspath(site_dir or os.path.join(base, "_daily", "site"))
    data_dir = os.path.join(site_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    only = set(x.strip().upper() for x in only if x.strip()) if only else None
    now = now or datetime.datetime.now(NY)
    built_at, date = now.isoformat(timespec="seconds"), now.date().isoformat()
    # the builder's code: this script and the fundamentals.price_dividends it reprices every dividends block with
    builder_mtime = max(os.path.getmtime(os.path.abspath(__file__)),
                        os.path.getmtime(FUND.__file__) if FUND is not None and os.path.exists(FUND.__file__) else 0.0)
    registry = load_registry(base)
    watchlist, watchlist_outside, watchlist_entries = load_watchlist(base)
    wl = set(watchlist)
    def warn(msg):  # failures go to stderr even under --quiet: a cron must see them
        print(f"build_site: {msg}", file=sys.stderr)

    def statements_path(t):
        return os.path.join(data_dir, f"{t}{STATEMENTS_SUFFIX}")

    def remove_file(path):
        try:
            os.remove(path)
        except OSError:
            pass

    def sync_statements(t, folder, files, obj=None, rebuilt=False):
        """data/<T>.statements.json follows the folder's statements.json: written
        (verbatim, NaN/inf → null) when the record is rebuilt or the copy is
        missing, removed when the folder has no usable file. `obj` is the
        already-loaded dict when the caller has it. Returns 'written' /
        'removed' / None."""
        path = statements_path(t)
        want = "statements.json" in files
        if want and obj is None:
            obj = jload(os.path.join(folder, "statements.json"))
            want = isinstance(obj, dict)
        if want and (rebuilt or not os.path.exists(path)):
            write_atomic(path, dump(finite(obj)))
            return "written"
        if not want and os.path.exists(path):
            remove_file(path)
            return "removed"
        return None

    # 1. classify every scored folder (score.json + dcf_numbers.json only), keyed by
    #    the served ticker (score.ticker, else the folder name)
    current, stale, duplicates, seen = {}, [], [], {}
    folders = sorted((os.path.basename(os.path.dirname(p)), os.path.dirname(p)) for p in glob.glob(os.path.join(base, "*", "score.json")))
    for fname, folder in folders:
        if fname.startswith("_") or fname.startswith("."):
            continue
        c = load_light(folder)
        if not c["score"]:
            continue
        t = ticker_key(c)
        if t in seen:  # two folders claim one ticker: the folder NAMED after it wins, else the first by name
            keep, drop = (c, seen[t]) if fname == t != seen[t]["folder"] else (seen[t], c)
            duplicates.append(f"{drop['folder']} (ticker {t} is served from {keep['folder']})")
            warn(f"duplicate ticker {t}: folder {drop['folder']} ignored, {keep['folder']} is served")
            if keep is seen[t]:
                continue
            current.pop(t, None)
            stale[:] = [e for e in stale if e["ticker"] != t]
            c = keep
        seen[t] = c
        c["ticker"] = t
        if qualifies(c):
            current[t] = c
        elif not is_current(c["numbers"]) and not c["numbers"].get("data_gap_uncovered"):
            s = c["score"]
            stale.append({"ticker": t, "name": s.get("name") if isinstance(s.get("name"), str) else None,
                          "tier": _tier(s.get("tier_final")) or _tier(s.get("tier_by_numbers")),
                          "irr": num(s.get("implied_irr")), "analysis_date": s.get("analysis_date") if isinstance(s.get("analysis_date"), str) else None,
                          "watchlist": t in wl})
    current = dict(sorted(current.items()))

    # 2. previous state: rows from index.json, mtimes + file lists from state.json. Both are
    #    gitignored caches: absent (fresh clone) or unreadable counts as empty, and neither is
    #    trusted over the data/ directory itself — a record whose data/<T>.json is missing is
    #    rebuilt whatever they claim (`have` below), and entries for tickers that are no longer
    #    current are dropped.
    prev_rows = {r.get("ticker"): r for r in _l(jload(os.path.join(site_dir, "index.json"))) if isinstance(r, dict)}
    state = _d(_d(jload(os.path.join(site_dir, "state.json"))).get("records"))
    state = {t: e for t, e in state.items() if t in current and isinstance(e, dict)}
    all_json = [os.path.basename(p) for p in glob.glob(os.path.join(data_dir, "*.json"))]
    existing = {f[:-5] for f in all_json if not f.endswith(STATEMENTS_SUFFIX)}
    existing_statements = {f[:-len(STATEMENTS_SUFFIX)] for f in all_json if f.endswith(STATEMENTS_SUFFIX)}

    # 3. remove records whose folder no longer qualifies (their statements copy goes with them;
    #    an orphan statements copy with no record is removed too)
    removed = sorted(t for t in existing if t not in current)
    for t in removed:
        remove_file(os.path.join(data_dir, f"{t}.json"))
        remove_file(statements_path(t))
        state.pop(t, None)
        prev_rows.pop(t, None)
    statements_removed = list(removed)
    for t in sorted(existing_statements):
        if t not in current and t not in removed:
            remove_file(statements_path(t))
            statements_removed.append(t)

    # 4. build / skip — one malformed folder never aborts the run
    written, skipped, failed, rows, records, sizes = [], [], [], {}, {}, {}
    statements_written, missing_outside_only = [], []
    replayed = 0

    def note_sync(t, outcome):
        if outcome == "written":
            statements_written.append(t)
        elif outcome == "removed":
            statements_removed.append(t)

    def previous_row(t, rec_path):
        row = prev_rows.get(t)
        if row is None:
            rec = jload(rec_path)
            row = rec.get("row") if isinstance(rec, dict) and isinstance(rec.get("row"), dict) else None
        return row

    for t, c in current.items():
        rec_path = os.path.join(data_dir, f"{t}.json")
        files = folder_files(c["path"])
        newest = newest_mtime(c["path"], files)
        st = state.get(t) if isinstance(state.get(t), dict) else None
        have = t in existing and t not in removed
        if only and t not in only and c["folder"].upper() not in only:
            row = previous_row(t, rec_path) if have else None
            if row:
                rows[t] = row
                skipped.append(t)
                continue
            # no usable record (fresh clone, deleted data/): build it anyway, or the index
            # would silently lose a current company for as long as --only runs continue
            missing_outside_only.append(t)
        if have and not force:
            bfm, bm, bfiles = (num(st.get("built_from_mtime")), num(st.get("builder_mtime")), st.get("files")) if st else (None, None, None)
            if bfm is None or bm is None:  # no state: recover from the record itself
                rec = jload(rec_path)
                if isinstance(rec, dict):
                    bfm = num(rec.get("built_from_mtime"))
                    bfiles = rec.get("files")
                    try:
                        bm = os.path.getmtime(rec_path)
                    except OSError:
                        bm = None
                    if t not in prev_rows and isinstance(rec.get("row"), dict):
                        prev_rows[t] = rec["row"]
            # unchanged = nothing newer than the record, same file list (a deleted
            # live.json / segments.json never bumps a surviving file's mtime), same builder
            if (bfm is not None and bm is not None and bfm >= newest and bm >= builder_mtime
                    and bfiles == files and t in prev_rows):
                rows[t] = prev_rows[t]
                skipped.append(t)
                # re-seed a lost / unreadable state.json entry from what the record proved
                state[t] = {**(st or {}), "built_from_mtime": bfm, "builder_mtime": bm, "files": bfiles}
                try:  # a skipped record keeps its statements copy in step with the folder (missing copy → written)
                    note_sync(t, sync_statements(t, c["path"], files))
                except Exception as e:  # noqa: BLE001
                    warn(f"statements copy for {t} failed: {type(e).__name__}: {e}")
                continue
        try:
            full = load_company(c["path"])
            full["ticker"] = t
            rec = build_record(full, registry, built_at, newest, wl)
            rec["builder_mtime"] = builder_mtime
            text = dump(rec)
        except Exception as e:  # noqa: BLE001 — keep the previous row/record, report, carry on
            failed.append(t)
            warn(f"FAILED {t} ({c['folder']}): {type(e).__name__}: {e}")
            row = previous_row(t, rec_path) if have else None
            if row:
                rows[t] = row
            continue
        sizes[t] = write_atomic(rec_path, text)
        rows[t] = rec["row"]
        records[t] = rec
        try:  # the statements copy next to the record (never inside it)
            note_sync(t, sync_statements(t, c["path"], files, obj=full.get("statements"), rebuilt=True))
        except Exception as e:  # noqa: BLE001
            warn(f"statements copy for {t} failed: {type(e).__name__}: {e}")
        state[t] = {"built_from_mtime": newest, "builder_mtime": builder_mtime, "built_at": built_at, "files": files}
        replayed += 1 if rec["forecast"].get("replayed") else 0
        written.append(t)

    # 5. index + meta + state. The watchlist flag is re-derived on EVERY row from the
    #    current list (it is not part of the record's skip check).
    for r in rows.values():
        r["watchlist"] = r.get("ticker") in wl
    index = sorted(rows.values(), key=rank_key)
    tiers = {k: 0 for k in "SABCDF"}
    for r in index:
        if r.get("tier") in tiers:
            tiers[r["tier"]] += 1
    stale.sort(key=lambda r: (-(r["irr"] if r["irr"] is not None else -9), r["ticker"] or ""))
    releases = sorted({r.get("engine_release") for r in index if isinstance(r.get("engine_release"), str)})
    latest_release = getattr(ENGINE, "ENGINE_RELEASE", None) or (releases[-1] if releases else None)
    withheld = sorted(r.get("ticker") or "" for r in index if r.get("live_withheld"))
    restated = sorted(f"{r.get('ticker')} {_d(r.get('split_restated')).get('split')}" for r in index if _d(r.get("split_restated")))
    notes = [f"ranked by the live IRR (live.json, scored paths repriced at the last close) when present and not older than the scored analysis, else the scored IRR; nulls last",
             f"this run: {len(written)} record(s) written, {len(skipped)} skipped unchanged, {len(removed)} removed" + (f" ({', '.join(removed)})" if removed else ""),
             "watchlist: _system/watchlist.json tickers in file order (meta.watchlist; meta.watchlist_outside = not in the universe), flagged on every row (row.watchlist)",
             f"statements: {len(statements_written)} data/<T>.statements.json cop(ies) written, {len(statements_removed)} removed; served next to the record, loaded by the Financials tab on demand, never embedded"]
    if withheld:
        notes.append(f"{len(withheld)} live.json close(s) older than the scored analysis withheld (scored figures shown, row.live_withheld): " + ", ".join(withheld))
    if restated:
        notes.append(f"{len(restated)} record(s) restated for a split since scoring (record.split_restated): " + ", ".join(restated))
    if failed:
        notes.append(f"{len(failed)} folder(s) FAILED to build and kept their previous row/record if any ({', '.join(failed)}) — see stderr")
    if duplicates:
        notes.append(f"{len(duplicates)} folder(s) ignored for a duplicate ticker: " + "; ".join(duplicates))
    if replayed:
        notes.append(f"{replayed} of the records written carry forecast paths replayed from pre-5.4 run inputs through dcf_engine.replay_paths")
    if only:
        notes.append("built with --only " + ",".join(sorted(only)) + ": other rows come from the previous index")
    if missing_outside_only:
        notes.append(f"{len(missing_outside_only)} record(s) outside --only had no data/<T>.json and were built anyway: " + ", ".join(missing_outside_only))
    meta = {"built_at": built_at, "date": date, "data_version": DATA_VERSION, "engine_release_latest": latest_release,
            "sweep": sweep_counts(base),
            "counts": {"current": len(index), "stale": len(stale), "misfits": sum(1 for r in index if r.get("fit") == "misfit"),
                       "tiers": tiers, "with_live": sum(1 for r in index if _d(r.get("has")).get("live")),
                       "live_withheld": len(withheld), "split_restated": len(restated),
                       "watchlist": sum(1 for r in index if r.get("watchlist")), "failed": len(failed),
                       "statements": sum(1 for r in index if _d(r.get("has")).get("statements")),
                       "profiles": sum(1 for r in index if _d(r.get("has")).get("profile"))},
            # Where the complete site is hosted, for the attachment's "open the site"
            # links (statements are served on demand there, never embedded). Set
            # STOCKS_SITE_URL once a host exists; null otherwise (the repo is
            # private, so GitHub Pages needs a paid plan).
            "site_url": (os.environ.get("STOCKS_SITE_URL") or "").strip() or None,
            "hurdles": HURDLES, "tabs": TABS, "watchlist": watchlist, "watchlist_outside": watchlist_outside,
            "watchlist_entries": watchlist_entries, "stale": stale, "failed": failed, "notes": notes}
    index, meta = finite(index), finite(meta)
    write_atomic(os.path.join(site_dir, "index.json"), dump(index))
    write_atomic(os.path.join(site_dir, "meta.json"), dump(meta, compact=False))
    write_atomic(os.path.join(site_dir, "state.json"), dump({"built_at": built_at, "builder_mtime": builder_mtime, "records": state}))

    # 6. attachment + the committed daily history snapshot (same date). A
    #    pre-render failure raises out of build_attachment BEFORE any file is
    #    written — the previous attachment and history snapshot stay in place.
    att = hist = None
    info = {}
    if attachment:
        att = build_attachment(base, site_dir, meta, index, records, top, date, prerender=prerender, info=info)
        hist = write_history_csv(attachment_dir(base, site_dir), index, date)

    largest = max(sizes.items(), key=lambda kv: kv[1]) if sizes else None
    summary = (f"build_site: {len(written)} written / {len(skipped)} skipped / {len(removed)} removed"
               + (f" [{', '.join(removed)}]" if removed else "")
               + (f" / {len(failed)} FAILED [{', '.join(failed)}]" if failed else "")
               + (f" / {len(duplicates)} duplicate folder(s) ignored" if duplicates else "")
               + f" | statements {len(statements_written)} written / {len(statements_removed)} removed"
               + (f" | largest record {largest[0]} {largest[1]:,} B" if largest else " | no record written")
               + (f" | attachment {att[1]:,} B ({att[2]} records) -> {att[0]}" if att else "")
               + (f" | {info['prerender']}" if info.get("prerender") else "")
               + (f" | history {hist[1]} rows -> {hist[0]}" if hist else "")
               + f" | {len(index)} rows, {len(stale)} stale -> {site_dir}")  # ASCII only: Windows consoles
    if not quiet:
        print(summary)
    return {"written": written, "skipped": skipped, "removed": removed, "failed": failed, "duplicates": duplicates,
            "statements_written": statements_written, "statements_removed": statements_removed,
            "missing_outside_only": missing_outside_only,
            "rows": index, "meta": meta, "records": records, "watchlist": watchlist, "watchlist_outside": watchlist_outside,
            "largest": largest, "attachment": att, "history": hist, "site_dir": site_dir, "summary": summary,
            "prerender": info.get("prerender")}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Build the site data layer (meta.json, index.json, data/<T>.json).")
    ap.add_argument("--only", help="comma-separated tickers to (re)build; other rows come from the previous index")
    ap.add_argument("--force", action="store_true", help="rebuild every record")
    ap.add_argument("--attachment", action="store_true",
                    help="also write _daily/ranking-<date>.html and latest.html, and the committed _daily/history/ranking-<date>.csv")
    ap.add_argument("--top", type=int, default=150, help="records embedded in the attachment (default 150)")
    ap.add_argument("--site-dir", help="output directory (default <base>/_daily/site)")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--no-prerender", action="store_true",
                    help="emergency opt-out: write the attachment without the pre-rendered static layer "
                         "(the file then needs JavaScript to read, like before 2026-10-16)")
    a = ap.parse_args(argv)
    # One builder at a time: WORKER_SPEC step 10, the second pass and the daily
    # cron all call this from workers that fire concurrently (re-verification
    # finding). Same cross-platform lock as queue.py / make_score.py.
    from _lock import locked
    base = os.path.abspath(os.environ.get("STOCKS_BASE") or os.path.dirname(HERE))
    site_dir = os.path.abspath(a.site_dir or os.path.join(base, "_daily", "site"))
    os.makedirs(site_dir, exist_ok=True)
    with locked(site_dir + ".lock"):
        try:
            build(site_dir=a.site_dir, only=(a.only.split(",") if a.only else None), force=a.force, attachment=a.attachment,
                  top=a.top, quiet=a.quiet, prerender=not a.no_prerender)
        except PrerenderError as e:
            print(f"build_site: {e} — the previous attachment was NOT overwritten", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
