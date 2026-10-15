#!/usr/bin/env python3
"""Site data layer (v6 presentation, 2026-10-14) — see _system/SITE_CONTRACT.md.

Usage: python3 build_site.py [--only T,T] [--force] [--attachment] [--top N]
                             [--site-dir PATH] [--quiet]

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

--attachment inlines <site>/index.html + app.css + app.js (or a placeholder
shell when the app is not there yet) with window.SITE_DATA = {meta, index,
records of the top N rows (default 150), trimmed} into
<base>/_daily/ranking-<America/New_York date>.html and <base>/_daily/latest.html.

Every number comes from a file; the only computation here is the forecast
replay through the engine's own functions (dcf_engine.replay_paths,
present_value, solve_irr, tier_for_irr) when a pre-5.4 run lacks the stored
values, plus the display arithmetic (upside = IV / price − 1) the v2 pages
did. Stdlib only. The loaders and derivations were copied from
build_daily_html.py (v2, being retired) — nothing is imported from it.
"""
import argparse
import csv
import datetime
import glob
import json
import math
import os
import re
import sys
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
try:
    import dcf_engine as ENGINE
except Exception:  # the data layer still builds without the forecast replay
    ENGINE = None

DATA_VERSION = 1
HURDLES = {"S": 0.25, "A": 0.20, "B": 0.15, "C": 0.10}
LABELS = ["super_bear", "bear", "base", "bull", "super_bull"]
RATES = (10, 12, 15, 20, 25)
TABS = ["overview", "financials", "dividends", "segments", "forecast", "analysis", "data"]
NY = ZoneInfo("America/New_York")
COMPANY_FILES = ("score.json", "dcf_numbers.json", "financials_history.csv", "fundamentals.json", "prices.json",
                 "live.json", "segments.json", "ttm.json", "judgment.json", "analysis.md", "second_pass.md",
                 "profile.json", "statements.json")
STATEMENTS_SUFFIX = ".statements.json"  # data/<T>.statements.json — served next to the record, loaded on demand
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
    c["statements"] = jload(os.path.join(folder, "statements.json"))  # copied next to the record, never embedded
    c["analysis_md"] = tread(os.path.join(folder, "analysis.md"))
    c["second_pass_md"] = tread(os.path.join(folder, "second_pass.md"))
    c["files"] = folder_files(folder)
    for k in ("fund", "prices", "ttm", "live", "segments", "judgment", "profile", "statements"):
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
    gterm = inp.get("g_terminal", 0.025)
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
    return num(_d(n.get("inputs")).get("g_terminal")) or num(n.get("g_terminal")) or 0.025


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
    """{label: {"10".."25": iv, irr, irr_live, irr_live_at_floor}} from stored
    values (5.4) or present_value on the replayed paths; irr_live from live.json."""
    scn = _d(n.get("scenarios")) or _d(s.get("scenarios"))
    if not scn:
        return None
    g = _gterm(n)
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
    """score.irr_at_floor (5.4) → diagnostics.irr_at_floor → for an older run,
    solve_irr's at-floor flag on the replayed weighted path at the scored price."""
    s, n = c["score"], c["numbers"]
    if "irr_at_floor" in s:
        return bool(s.get("irr_at_floor"))
    diag = _d(n.get("diagnostics"))
    if "irr_at_floor" in diag:
        return bool(diag.get("irr_at_floor"))
    px = num(s.get("price")) or num(n.get("price"))
    if _l(_d(paths).get("weighted")) and px and ENGINE is not None and hasattr(ENGINE, "solve_irr"):
        try:
            return bool(ENGINE.solve_irr(paths["weighted"], px, _gterm(n))[2])
        except Exception:
            return False
    return False


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
        if row["iv20"] is None and num(lv.get("iv_at_20")) is not None:
            row["iv20"] = num(lv.get("iv_at_20"))
        if row["iv25"] is None and num(lv.get("iv_at_25")) is not None:
            row["iv25"] = num(lv.get("iv_at_25"))
    return row


def rank_key(row):
    v = row.get("irr_live") if row.get("irr_live") is not None else row.get("irr")
    return (0, -v, row.get("ticker") or "") if v is not None else (1, 0.0, row.get("ticker") or "")


# ---------------------------------------------------------------- record
def build_record(c, registry, built_at, built_from_mtime, watchlist=()):
    s, n = c["score"], c["numbers"]
    has_scn = bool(_d(n.get("scenarios")))
    paths, gpaths, replayed = forecast_paths(n) if has_scn else (None, None, False)
    paths, gpaths = (_d(paths) or None), (_d(gpaths) or None)
    hp = hurdle_prices(n, s, paths) if has_scn else None
    sens = scenario_sensitivity(n, s, paths, c.get("live"))
    row = index_row(c, registry, paths, hp, watchlist)
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
           "live": c.get("live") if live_ok(c.get("live")) else None,
           "history": c.get("history") or [],
           "fundamentals": c.get("fund"), "prices": prices, "segments": c.get("segments"), "ttm": c.get("ttm"),
           "judgment": c.get("judgment"),
           "profile": c.get("profile") if isinstance(c.get("profile"), dict) else None,
           "registry": registry_entries(registry, c, row["ticker"]),
           "analysis_md": c.get("analysis_md"), "second_pass_md": c.get("second_pass_md"),
           "files": c.get("files") or []}
    return finite(rec)  # NaN / inf anywhere in a verbatim file -> null


def trim_record(rec):
    """The attachment copy: no judgment / ttm / prices.daily_1y /
    prices.sessions_5d / numbers.used_tags (prices.intraday and profile are
    kept; the statements never live in a record, so nothing to drop there)."""
    out = {k: v for k, v in rec.items() if k not in ("judgment", "ttm", "statements")}
    if isinstance(out.get("prices"), dict):
        out["prices"] = {k: v for k, v in out["prices"].items() if k not in ("daily_1y", "sessions_5d")}
    if isinstance(out.get("numbers"), dict):
        out["numbers"] = {k: v for k, v in out["numbers"].items() if k != "used_tags"}
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
    for e in (jload(os.path.join(base, "_system", "overrides_registry.json")) or {}).get("entries", []) or []:
        if isinstance(e, dict):
            reg.setdefault(e.get("ticker"), []).append(e)
    return reg


def sweep_counts(base):
    qd = jload(os.path.join(base, "_system", "queue.json")) or {}
    q = [e for e in (qd.get("queue") or []) if isinstance(e, dict)]
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


def build_attachment(base, site_dir, meta, rows, records_by_ticker, top, date):
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
    # The attachment lives next to the site directory: <base>/_daily for the
    # default site, the parent of --site-dir otherwise (a temp-dir test build
    # must never overwrite the real ranking file — review finding).
    default_site = os.path.abspath(os.path.join(base, "_daily", "site"))
    out_dir = os.path.join(base, "_daily") if os.path.abspath(site_dir) == default_site else os.path.dirname(os.path.abspath(site_dir))
    path = os.path.join(out_dir, f"ranking-{date}.html")
    size = write_atomic(path, doc)
    write_atomic(os.path.join(out_dir, "latest.html"), doc)
    return path, size, len(recs)


# ---------------------------------------------------------------- build
def build(base=None, site_dir=None, only=None, force=False, attachment=False, top=150, quiet=False, now=None):
    base = os.path.abspath(base or os.environ.get("STOCKS_BASE") or os.path.dirname(HERE))
    site_dir = os.path.abspath(site_dir or os.path.join(base, "_daily", "site"))
    data_dir = os.path.join(site_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    only = set(x.strip().upper() for x in only if x.strip()) if only else None
    now = now or datetime.datetime.now(NY)
    built_at, date = now.isoformat(timespec="seconds"), now.date().isoformat()
    builder_mtime = os.path.getmtime(os.path.abspath(__file__))
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

    # 2. previous state: rows from index.json, mtimes + file lists from state.json
    prev_rows = {r.get("ticker"): r for r in (jload(os.path.join(site_dir, "index.json")) or []) if isinstance(r, dict)}
    state = jload(os.path.join(site_dir, "state.json")) or {}
    state = state.get("records") if isinstance(state.get("records"), dict) else {}
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
    statements_written = []
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
            if have:
                row = previous_row(t, rec_path)
                if row:
                    rows[t] = row
                    skipped.append(t)
            continue
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
    notes = [f"ranked by the live IRR (live.json, scored paths repriced at the last close) when present, else the scored IRR; nulls last",
             f"this run: {len(written)} record(s) written, {len(skipped)} skipped unchanged, {len(removed)} removed" + (f" ({', '.join(removed)})" if removed else ""),
             "watchlist: _system/watchlist.json tickers in file order (meta.watchlist; meta.watchlist_outside = not in the universe), flagged on every row (row.watchlist)",
             f"statements: {len(statements_written)} data/<T>.statements.json cop(ies) written, {len(statements_removed)} removed; served next to the record, loaded by the Financials tab on demand, never embedded"]
    if failed:
        notes.append(f"{len(failed)} folder(s) FAILED to build and kept their previous row/record if any ({', '.join(failed)}) — see stderr")
    if duplicates:
        notes.append(f"{len(duplicates)} folder(s) ignored for a duplicate ticker: " + "; ".join(duplicates))
    if replayed:
        notes.append(f"{replayed} of the records written carry forecast paths replayed from pre-5.4 run inputs through dcf_engine.replay_paths")
    if only:
        notes.append("built with --only " + ",".join(sorted(only)) + ": other rows come from the previous index")
    meta = {"built_at": built_at, "date": date, "data_version": DATA_VERSION, "engine_release_latest": latest_release,
            "sweep": sweep_counts(base),
            "counts": {"current": len(index), "stale": len(stale), "misfits": sum(1 for r in index if r.get("fit") == "misfit"),
                       "tiers": tiers, "with_live": sum(1 for r in index if _d(r.get("has")).get("live")),
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

    # 6. attachment
    att = None
    if attachment:
        att = build_attachment(base, site_dir, meta, index, records, top, date)

    largest = max(sizes.items(), key=lambda kv: kv[1]) if sizes else None
    summary = (f"build_site: {len(written)} written / {len(skipped)} skipped / {len(removed)} removed"
               + (f" [{', '.join(removed)}]" if removed else "")
               + (f" / {len(failed)} FAILED [{', '.join(failed)}]" if failed else "")
               + (f" / {len(duplicates)} duplicate folder(s) ignored" if duplicates else "")
               + f" | statements {len(statements_written)} written / {len(statements_removed)} removed"
               + (f" | largest record {largest[0]} {largest[1]:,} B" if largest else " | no record written")
               + (f" | attachment {att[1]:,} B ({att[2]} records) -> {att[0]}" if att else "")
               + f" | {len(index)} rows, {len(stale)} stale -> {site_dir}")  # ASCII only: Windows consoles
    if not quiet:
        print(summary)
    return {"written": written, "skipped": skipped, "removed": removed, "failed": failed, "duplicates": duplicates,
            "statements_written": statements_written, "statements_removed": statements_removed,
            "rows": index, "meta": meta, "records": records, "watchlist": watchlist, "watchlist_outside": watchlist_outside,
            "largest": largest, "attachment": att, "site_dir": site_dir, "summary": summary}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Build the site data layer (meta.json, index.json, data/<T>.json).")
    ap.add_argument("--only", help="comma-separated tickers to (re)build; other rows come from the previous index")
    ap.add_argument("--force", action="store_true", help="rebuild every record")
    ap.add_argument("--attachment", action="store_true", help="also write _daily/ranking-<date>.html and latest.html")
    ap.add_argument("--top", type=int, default=150, help="records embedded in the attachment (default 150)")
    ap.add_argument("--site-dir", help="output directory (default <base>/_daily/site)")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args(argv)
    # One builder at a time: WORKER_SPEC step 10, the second pass and the daily
    # cron all call this from workers that fire concurrently (re-verification
    # finding). Same cross-platform lock as queue.py / make_score.py.
    from _lock import locked
    base = os.path.abspath(os.environ.get("STOCKS_BASE") or os.path.dirname(HERE))
    site_dir = os.path.abspath(a.site_dir or os.path.join(base, "_daily", "site"))
    os.makedirs(site_dir, exist_ok=True)
    with locked(site_dir + ".lock"):
        build(site_dir=a.site_dir, only=(a.only.split(",") if a.only else None), force=a.force, attachment=a.attachment,
              top=a.top, quiet=a.quiet)
    return 0


if __name__ == "__main__":
    sys.exit(main())
