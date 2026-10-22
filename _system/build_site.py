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
{reason, note, price, price_date, scored_date, method} (reason
live_older_than_score; live_from_earlier_run for one left from an earlier
run of a re-scored name), the row's live fields stay null with
row.live_withheld = true, so the ranking sorts on the scored IRR and the
page shows the scored figures until a close after the scored session
arrives.
[Codex review round 2 of PR #47] A run whose acquired-IPR&D treatment is
not_applied_share_count_unverified is never repriced (reprice.py skips it),
so record.live_withheld carries reason iprd_share_count_unverified with or
without a live.json on file, and the scored figures are the current ones.
[Codex review round 6 of PR #47] The same, reason iprd_unresolved, for a run
make_score refused for an unresolved acquired-IPR&D charge (a period awaiting
its cash-flow check or one the engine cannot convert): reprice.py skips it
too, and the score.json on disk is an earlier run's.
[Codex review round 11 of PR #47, the main agent's general rule] And, reason
score_not_from_this_run, for ANY live.json beside a score.json that was not
built from the current dcf_numbers.json (score_from_run, reprice.py's
score_matches_run mirrored here): make_score refused the new run (whatever
its reason — a deleted deferred payment its registry recorded is one the
engine record alone cannot show) or has not run on it yet, so the verdict on
file is another run's and live figures pause until the folder is scored
again; reprice.py writes no live.json for it either. The more specific
iprd_unresolved / iprd_share_count_unverified reasons keep precedence.
[Codex review round 12 of PR #47] A score.json carrying dcf_content_hash
(make_score writes the run's content_hash since round 12) is from the run
only when that hash is the run's, itself valid over the record; one without
it is judged on the rounded headline figures as before.
[Codex review round 29 of PR #47] And, reason live_not_from_this_score, for
a live.json beside a run record that was not computed against the
score.json on file (live_score_problem; reprice.py records what it read:
score_json_fresh, scored.tier_final / tier_override_reason /
dcf_content_hash): repriced before make_score scored or re-scored the run,
or beside another run's same-day score. [Codex review round 29 of PR #47,
polish review] A live.json written before round 29 records no score
identity: beside a score.json that carries one it is withheld with its own
reason, live_without_score_identity (live_score_identity_missing; its note
says it records no score identity and the next repricing rewrites it, never
that it was computed before the score). The score is the run's, so the
scored figures are the latest available. Precedence, in the order
live_shown checks them: iprd_unresolved / iprd_share_count_unverified, then
score_not_from_this_run, then live_from_earlier_run,
live_not_from_this_score, live_without_score_identity and
live_older_than_score.

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

Engine 5.6 (acquired IPR&D, Andrew 2026-10-19): a run with a one-time
acquired-IPR&D deduction (numbers.iprd_adjustment, treatment
one_time_value_deduction) stores adjusted IVs, hurdle prices and IRRs, which
are shown as stored; every replay fallback below subtracts the same charge
(dcf_engine.iprd_charge_per_share / adjusted_value / adjusted_irr), so a
recomputed sensitivity cell, hurdle price or at-floor flag equals the
engine's. A record without the block replays exactly as before.

Rulings round (Andrew, 2026-10-19 — engine 5.7, rulings R1-R9; lane L6): the
record carries facts.json verbatim (record.facts, the worker's declared facts,
R3), the quote checker's compact report on analysis.md (record.quote_check,
from check_quotes.check_folder; null without the checker or without
analysis.md; a checker exception is status 'error', never a failed build) and
score_from_run's answer (record.score_from_run {matches, mismatches}: whether
score.json was built from this dcf_numbers.json — the Data tab's "Content
hash" line). score.json's misfit_notch, moat_evidence, declared_facts,
interim_bridge, interim_bridge_declined, base_alternatives, share_classes,
method_runs and previous_score, and dcf_numbers.json's sector_model,
annual_from_instance, share_classes and capex_provenance software, ride
inside the verbatim copies. The index row's tier_override now means a
judgment override BEYOND the sector-misfit notch: tier != (misfit_notch.
applies ? tier_after_notch : tier_by_numbers) (R1; row.misfit_notch,
row.tier_notched; live: tier_by_numbers_live, misfit_notch_live from the
live.json live_shown accepts); plus moat_evidence / interim_bridge summaries,
share_basis ("total_units" on a declared share-class run, R6) and has.facts.
The forecast block names the growth hold the engine recorded (hold_years,
moat_trend, hold_by_scenario; 2 / null on a record before 5.7). The
attachment keeps facts and a declared-interim ttm.json (ttm.basis
"declared_interim", R2a); a legacy quote_check keeps its counts, not its
list. The history CSV appends tier_by_numbers, tier_notched, the six moat
columns, moat_trend / hold_years and tier_by_numbers_live (29 columns; dated files are never
rewritten). The builder mtime includes check_quotes.py, facts.py and
quote_tokens.py (record.quote_check depends on their code). A page whose
latest engine run is not scored yet keeps every panel, labelled "as scored
<date>" or "latest run, not scored yet" by the app (lane default Q11 (a),
main agent 2026-10-21) — no data-layer exclusion.

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
import hashlib
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
try:  # the quote checker (R3, engine 5.7): its report on analysis.md is shown on the Analysis tab
    import check_quotes as QUOTES
except Exception:  # the data layer still builds; record.quote_check is then null
    QUOTES = None

DATA_VERSION = 1
HURDLES = {"S": 0.25, "A": 0.20, "B": 0.15, "C": 0.10}
LABELS = ["super_bear", "bear", "base", "bull", "super_bull"]
RATES = (10, 12, 15, 20, 25)
TABS = ["overview", "financials", "dividends", "segments", "forecast", "analysis", "data"]
NY = ZoneInfo("America/New_York")
COMPANY_FILES = ("score.json", "dcf_numbers.json", "financials_history.csv", "fundamentals.json", "prices.json",
                 "live.json", "segments.json", "ttm.json", "judgment.json", "analysis.md", "second_pass.md",
                 "profile.json", "statements.json", "street.json",
                 "facts.json")  # engine 5.7 (R3): the worker's declared facts, served as record.facts
STATEMENTS_SUFFIX = ".statements.json"  # data/<T>.statements.json — served next to the record, loaded on demand
DEFAULT_GTERM = getattr(ENGINE, "DEFAULT_GTERM", 0.025)
PROJECTION_YEARS = getattr(ENGINE, "PROJECTION_YEARS", 15)  # the projection horizon: a recorded hold lies in 0..15
# _daily/history/ranking-<date>.csv (committed): what the daily chat message quotes, one row per ranked company
HISTORY_COLUMNS = ("rank", "ticker", "name", "sector_misfit", "tier_scored", "irr_scored", "tier_live", "irr_live",
                   "band_low_tier", "band_high_tier", "price", "price_date", "iv15", "upside15_pct",
                   "analysis_date", "engine_release", "alert_eligible", "watchlist",
                   # engine 5.7 rulings (append-only; earlier dated files keep their 18 columns): the misfit notch (R1),
                   "tier_by_numbers", "tier_notched",
                   # the moat record for backtesting (R4 revised, 03b §7.1),
                   "moat_score", "moat_evidence_score", "moat_return_measure", "moat_return_median", "moat_sources",
                   "moat_widest_source",
                   # and the growth hold the moat's direction set (M6, 10 §4)
                   "moat_trend", "hold_years",
                   # [whole-PR review fix, 2026-10-21] the LIVE numbers tier reprice notched (blank without live data):
                   # the daily message quotes a live notched name as "<tier_live> (<tier_by_numbers_live> by numbers)"
                   "tier_by_numbers_live")
# Split restatement (see the module docstring): dotted paths in the record, `*` = every key / item at that level.
# SPLIT_DIVIDE holds every per-share figure of the scored run the page shows; SPLIT_MULTIPLY its share counts.
_IV_KEYS = tuple(f"iv_at_{r}" for r in RATES)
SPLIT_DIVIDE = (tuple(f"score.{k}" for k in ("price", "base_oe_per_share") + _IV_KEYS)
                + tuple(f"score.scenarios.*.{k}" for k in _IV_KEYS)
                + ("score.override_impact.base_oe_without_override", "score.override_impact.base_oe_with_override",
                   "score.second_pass.prior_iv_at_15")
                + tuple(f"numbers.{k}" for k in ("price", "base_oe_per_share", "base_oe_latest_per_share", "base_oe_normalized_per_share") + _IV_KEYS)
                + tuple(f"numbers.scenarios.*.{k}" for k in _IV_KEYS) + tuple(f"numbers.weighted.{k}" for k in _IV_KEYS)
                # engine 5.6: the one-time acquired-IPR&D charge per share and the IVs kept beside it
                + ("numbers.iprd_adjustment.charge_per_share", "numbers.iprd_adjustment.base_oe_per_share",
                   "numbers.iprd_adjustment.before.*.iv_at_10", "numbers.iprd_adjustment.before.*.iv_at_12",
                   "numbers.iprd_adjustment.before.*.iv_at_15", "numbers.iprd_adjustment.before.*.iv_at_20",
                   "numbers.iprd_adjustment.before.*.iv_at_25", "numbers.iprd_adjustment.after.weighted.*",
                   "score.iprd_adjustment.charge_per_share", "score.iprd_adjustment.iv_before.*",
                   "score.iprd_adjustment.iv_after.*",
                   # [v5.6 review] an amortized_in_base run's native and pinned bases (and the declared value)
                   "numbers.iprd_adjustment.amortized.native_base_per_share",
                   "numbers.iprd_adjustment.amortized.pinned_per_share",
                   "numbers.iprd_adjustment.amortized.expected_value",
                   "numbers.iprd_adjustment.amortized.declared_value",
                   "score.iprd_adjustment.amortized.native_base_per_share",
                   "score.iprd_adjustment.amortized.pinned_per_share")
                + ("numbers.hurdle_prices.*", "numbers.inputs.base_oe_ps_arg",
                   "numbers.override_impact.base_oe_per_share_zero_fill", "numbers.override_impact.base_oe_per_share_final")
                + ("forecast.paths.*.*", "forecast.hurdle_prices.*", "forecast.inputs.base_oe_ps_arg")
                + tuple(f"forecast.sensitivity.*.{r}" for r in RATES)
                + tuple(f"row.{k}" for k in ("price", "iv15", "iv12", "iv20", "iv25"))
                + ("ttm.ttm_oe_per_share",)
                # engine 5.7 rulings (lane L6): every base the run recorded beside the published one (R7 / R2a
                # base_alternatives), the saved method runs and the previous score (R3), a declared 6-K bridge's
                # per-ordinary-share figure and zero-fill pin (R2a), the moat fade counterfactual's IV (M6)
                + ("score.base_alternatives.bases.*.base_oe_per_share", "score.base_alternatives.bases.*.iprd_charge_per_share",
                   "score.method_runs.*.base_oe_per_share", "score.method_runs.*.iv_at_15",
                   "score.method_runs.*.iprd_charge_per_share",
                   "score.previous_score.base_oe_per_share", "score.previous_score.iv_at_15",
                   "ttm.ttm_oe_per_ordinary_share", "ttm.override_counterfactual.base_oe_per_share_zero_fill",
                   "score.moat_evidence.fade.counterfactual.*.iv_at_15")
                # declared share classes (R6, design 08 §10): exact keys, never a wildcard over a block holding ratios
                + ("numbers.share_classes.ttm.ttm_oe_per_share", "numbers.share_classes.ttm.ttm_oe_per_share_filed_basis",
                   "ttm.ttm_oe_per_share_filed_basis", "ttm.ttm_oe_per_ordinary_share_filed_basis",
                   "ttm.override_counterfactual.base_oe_per_share_zero_fill_filed_basis",
                   "numbers.share_classes.cap_check.universe_price", "numbers.up_c_check.universe_price",
                   "score.share_classes.base_oe_filed_basis", "score.share_classes.base_oe_total_units",
                   "score.share_classes.replay_pin"))
SPLIT_MULTIPLY = ("numbers.shares_diluted_latest", "history.*.shares_diluted", "ttm.ttm_shares_diluted",
                  "numbers.iprd_adjustment.shares_denominator", "score.iprd_adjustment.shares_denominator",
                  "numbers.iprd_adjustment.amortized.shares", "score.iprd_adjustment.amortized.shares",
                  # engine 5.7 (R2a): a declared 6-K bridge's current-interim diluted count and the FY count beside it
                  "ttm.shares.current_interim.value", "ttm.shares.fy_diluted",
                  # declared share classes (R6, design 08 §10): per applied period and per class, the TTM and the latest
                  "numbers.share_classes.applied.*.filed_traded", "numbers.share_classes.applied.*.declared_units",
                  "numbers.share_classes.applied.*.units_equivalent", "numbers.share_classes.applied.*.total_units",
                  "numbers.share_classes.applied.*.diluted_minus_basic", "numbers.share_classes.applied.*.classes.*.value",
                  "numbers.share_classes.ttm.filed_traded", "numbers.share_classes.ttm.units_equivalent",
                  "numbers.share_classes.ttm.total_units",
                  "numbers.share_classes.latest.filed_traded", "numbers.share_classes.latest.units_equivalent",
                  "numbers.share_classes.latest.total_units",
                  "numbers.market_cap_basis.traded_shares", "numbers.market_cap_basis.declared_units",
                  "numbers.share_classes.applied.*.included_units", "numbers.share_classes.included_periods.*.included_units",
                  "numbers.share_classes.included_periods.*.filed_traded",
                  "ttm.ttm_shares_diluted_filed", "ttm.share_classes.filed_traded", "ttm.share_classes.units_equivalent",
                  "ttm.share_classes.total_units", "ttm.share_classes.included_units", "ttm.share_classes.classes.*.value",
                  # [merge L6] the merged shapes (lane L8): make_score.share_classes_impact writes the latest counts flat
                  # (units_latest / filed_latest — no latest / ttm sub-block in score.json); every class row carries
                  # share_classes.period_detail's units (value × exchange_ratio) beside its value; the engine's TTM leg
                  # and ttm.json's block carry the diluted - basic gap like every applied period
                  "score.share_classes.units_latest", "score.share_classes.filed_latest",
                  "numbers.share_classes.applied.*.classes.*.units", "ttm.share_classes.classes.*.units",
                  "numbers.share_classes.ttm.diluted_minus_basic", "ttm.share_classes.diluted_minus_basic")
QUOTE_UNTRACED_MAX = 40   # untraced numbers kept per record (the Analysis tab lists them; the counts are always exact)
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
    c["facts"] = jload(os.path.join(folder, "facts.json"))  # R3 declared facts (judgment record) -> record.facts
    c["analysis_md"] = tread(os.path.join(folder, "analysis.md"))
    c["second_pass_md"] = tread(os.path.join(folder, "second_pass.md"))
    c["files"] = folder_files(folder)
    for k in ("fund", "prices", "ttm", "live", "segments", "judgment", "profile", "street", "statements", "facts"):
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


IPRD_SHARE_COUNT_UNVERIFIED = "not_applied_share_count_unverified"   # reprice.py never reprices this treatment
IPRD_WITHHELD_NOTE = ("The acquired-IPR&D charge was not deducted by the engine (share count unverified): the published tier "
                      "is the main agent's tier_override with a hand deduction that reprice.py cannot replay, so the scored "
                      "figures are the current ones and no live repricing is shown.")
# [Codex review r6 of PR #47] dcf_engine's names for the acquired-IPR&D states make_score refuses (dcf_engine.iprd_unresolved)
IPRD_AWAITING, IPRD_UNCONVERTED = "awaiting_cash_flow_check", "non_usd_no_rate"
IPRD_UNRESOLVED_NOTE = ("The latest engine run left an acquired-IPR&D charge unresolved (awaiting the worker's cash-flow check, "
                        "or in a currency the engine cannot convert), so make_score refused it: the score on file is an earlier "
                        "run's, a live repricing of the new run would carry unadjusted figures, and none is shown until the "
                        "folder is scored again.")


SCORE_NOT_FROM_RUN_NOTE = ("The score on file was not built from the latest engine run (make_score refused that run or has "
                           "not scored it yet), so the scored figures are the current ones and no live repricing is shown "
                           "until the folder is scored again.")
# [Codex review r29 of PR #47] a live.json not computed against the score on file (live_score_problem)
LIVE_NOT_FROM_SCORE_NOTE = ("The live repricing on file was computed before the current score of this run (make_score has "
                            "scored it since), so the scored figures are the latest available until the folder is repriced.")
# [Codex review r29 of PR #47, polish review] a live.json from before round 29 beside a score.json that carries its run's
# identity (live_score_identity_missing): it may well have been computed against this very score, so the note never says
# it was computed before it — only that it records no score identity and that the next repricing rewrites it
LIVE_NO_SCORE_IDENTITY_NOTE = ("The live repricing on file records no score identity (it was written before live.json "
                               "recorded the score it was computed against), so it is not shown beside this score: the "
                               "scored figures are the latest available until the next repricing rewrites it.")


def _same(a, b, tol):
    a, b = num(a), num(b)
    return a is not None and b is not None and abs(a - b) <= tol


# [Codex review r13 of PR #47] reprice.HASH_REQUIRED_FROM_RELEASE mirrored (a test holds the two equal)
HASH_REQUIRED_FROM_RELEASE = "5.6.0"


def _requires_content_hash(d):
    """reprice.requires_content_hash mirrored: an engine_release at or after HASH_REQUIRED_FROM_RELEASE."""
    rt = lambda rel: (tuple(int(x or 0) for x in m.groups())
                      if (m := re.match(r"\s*(\d+)\.(\d+)(?:\.(\d+))?", rel) if isinstance(rel, str) else None)
                      else None)
    t = rt(d.get("engine_release")) if isinstance(d, dict) else None
    return t is not None and t >= rt(HASH_REQUIRED_FROM_RELEASE)


def score_from_run(score, numbers):
    """[Codex review r11 of PR #47] (matches, mismatches): whether score.json was built by make_score.py from THIS
    dcf_numbers.json — reprice.score_matches_run mirrored here so the site needs no reprice import (a test holds the
    two equal): make_score copies the run's figures verbatim (implied_irr to 4 dp, iv_at_15 to 2 dp), and the run's
    numbers tier must be the tier of its own weighted IRR. [Codex review r12 of PR #47] A score.json carrying
    dcf_content_hash must name this run's content_hash, itself valid over the record (reprice.run_hash_problem); one
    without it is judged on the headline figures alone only for a run from before release 5.6.0 ([Codex review r13
    of PR #47]: a current-release score.json with no hash is another run's). [Codex review r19 of PR #47] A run with
    no weighted IRR — Tier F (no positive owner's earnings) or untiered — is matched by the same identity (the hash
    when present, as_of, tier, base, price, release): its score.json carries no implied_irr either and the same
    f_subtype; before, it never matched (tier_for_irr(None) is None, not 'F'; implied_irr None never equalled None),
    which is why live_shown limited its no-live.json notice to repriceable runs."""
    if not isinstance(score, dict):
        return False, ["score.json is not an object"]
    n = _d(numbers)
    mm = []
    if "dcf_content_hash" not in score:
        if _requires_content_hash(score) or _requires_content_hash(n):
            rel = score.get("engine_release") if _requires_content_hash(score) else n.get("engine_release")
            mm.append(f"score.json carries no dcf_content_hash though the run is release {rel} (make_score writes it "
                      f"for every run since release {HASH_REQUIRED_FROM_RELEASE}: rounded headline figures are not "
                      "run identity)")
    else:
        h, ch = score.get("dcf_content_hash"), n.get("content_hash")
        if not h or h != ch:
            mm.append(f"dcf_content_hash {h!r} vs run content_hash {ch!r} (another engine run)")
        else:
            canon = json.dumps({k: v for k, v in n.items() if k != "content_hash"},
                               sort_keys=True, separators=(",", ":"), default=str)
            if hashlib.sha256(canon.encode()).hexdigest() != ch:
                mm.append("run content_hash does not match its content (dcf_numbers.json edited after the engine run)")
    if not score.get("analysis_date") or score.get("analysis_date") != n.get("as_of"):
        mm.append(f"analysis_date {score.get('analysis_date')!r} vs run as_of {n.get('as_of')!r}")
    tier_run = n.get("tier_by_numbers")
    # [Codex review r19 of PR #47] a run with no weighted IRR (Tier F / untiered): none on the score either, same f_subtype
    no_irr = num(n.get("implied_irr_weighted")) is None and tier_run in ("F", None)
    tier_irr = tier_for_irr(num(n.get("implied_irr_weighted")))
    if not no_irr and tier_run != tier_irr:
        mm.append(f"run tier_by_numbers {tier_run!r} is not the tier of its weighted IRR ({tier_irr!r})")
    if score.get("tier_by_numbers") != tier_run:
        mm.append(f"tier_by_numbers {score.get('tier_by_numbers')!r} vs run {tier_run!r}")
    if no_irr:
        if score.get("implied_irr") is not None:
            mm.append(f"implied_irr {score.get('implied_irr')!r} vs run None (a run with no weighted IRR)")
        if score.get("f_subtype") != n.get("f_subtype"):
            mm.append(f"f_subtype {score.get('f_subtype')!r} vs run {n.get('f_subtype')!r}")
    elif not _same(score.get("implied_irr"), n.get("implied_irr_weighted"), 0.5e-4 + 1e-9):
        mm.append(f"implied_irr {score.get('implied_irr')!r} vs run {n.get('implied_irr_weighted')!r}")
    for key, tol in (("price", 1e-9), ("base_oe_per_share", 1e-9), ("iv_at_15", 0.005 + 1e-9)):
        a, b = score.get(key), n.get(key)
        if a is None and b is None:
            continue
        if not _same(a, b, tol if key == "iv_at_15" else tol * max(1.0, abs(num(b) or 0.0))):
            mm.append(f"{key} {a!r} vs run {b!r}")
    for key in ("engine_version", "engine_release"):
        if score.get(key) != n.get(key):
            mm.append(f"{key} {score.get(key)!r} vs run {n.get(key)!r}")
    if score.get("ticker") and n.get("ticker") and str(score["ticker"]).upper() != str(n["ticker"]).upper():
        mm.append(f"ticker {score.get('ticker')!r} vs run {n.get('ticker')!r}")
    return not mm, mm


def run_published(n):
    """[Codex review r19 of PR #47] Whether the site publishes a scored folder with this run (qualifies, its run half):
    engine v5+ and no uncovered data gap. live_shown gives the score_not_from_this_run notice without a live.json to
    every such run — round 13 limited it to runs reprice.py reprices (run_repriceable), so a new run that turned
    Tier F published the earlier run's verdict beside its own flags with no notice."""
    n = _d(n)
    return is_current(n) and not n.get("data_gap_uncovered")


def iprd_unresolved(n):
    """[Codex review r6 of PR #47] True when the run's acquired-IPR&D record is one make_score refuses
    (dcf_engine.iprd_unresolved, mirrored here so the site needs no engine import): a period awaiting its cash-flow
    check, or excluded non_usd_no_rate with a positive native expense or cash outflow (or, Codex review r24, a positive
    detector tag it cannot convert beside the other: expense_tag_unconverted), or such a treatment."""
    blk = _d(_d(n).get("iprd_adjustment"))
    pos = lambda v: num(v) is not None and num(v) > 0
    for p in _l(blk.get("periods")):
        p = _d(p)
        if p.get("excluded") == IPRD_AWAITING:
            return True
        if p.get("excluded") == IPRD_UNCONVERTED and (pos(p.get("expense_native")) or pos(p.get("cash_native"))
                                                      or pos(_d(p.get("expense_tag_unconverted")).get("native"))):
            return True
    return blk.get("treatment") in (IPRD_AWAITING, IPRD_UNCONVERTED)


def live_score_problem(lv, score, numbers):
    """[Codex review r29 of PR #47] Why live.json was not computed against THIS score.json (None when it was). reprice
    reads only these from score.json — whether there is one (score_json_fresh), tier_final, tier_override_reason
    (recorded only while the override is active: tier_final differs from the run's tier_by_numbers) — plus, recorded
    since this round, the score's run identity (scored.dcf_content_hash: the score.json's, null when it carries
    none). Any difference means the live tier and override were computed against another score: a repricing written
    before make_score scored the run (score_json_fresh null — reprice_folder writes none since this round), one
    computed before make_score re-scored the same run (an override added, removed or reworded), or one beside a
    same-day score of another run. Before, live_shown compared only dates, so the numbers tier at the last close was
    published beside a new tier_override. [Codex review r29 of PR #47, review note] A live.json that records no
    scored.dcf_content_hash (written before this round) was not computed against a score.json that carries one: it
    had been exempt from the identity check, so beside a same-day score of another run it was shown as current. It
    is withheld until the next reprice rewrites it. A score.json with no dcf_content_hash (a run from before release
    5.6.0; score_from_run judges it on the headline figures) has no identity to bind: a live.json beside it matches
    when it records none either (null or no key). [Codex review r29 of PR #47, polish review] That missing identity
    is no longer reported here: nothing it records shows such a live.json was computed against another score (the
    reprice before round 29 usually computed it against this very one), so live_score_identity_missing names it and
    live_shown gives it its own reason, live_without_score_identity. A recorded identity that differs (a null one
    beside a hashed score included) is still this function's."""
    lv, s, n = _d(lv), _d(score), _d(numbers)
    if lv.get("score_json_fresh") is not True:
        return "computed with no score.json of this run on file"
    sc = _d(lv.get("scored"))
    if sc.get("tier_final") != s.get("tier_final"):
        return f"computed against tier_final {sc.get('tier_final')!r}, the score on file has {s.get('tier_final')!r}"
    tier_run, final = n.get("tier_by_numbers"), s.get("tier_final")
    want = s.get("tier_override_reason") if (final and tier_run and final != tier_run) else None
    if sc.get("tier_override_reason") != want:
        return "computed against another tier_override_reason than the score on file's"
    if "dcf_content_hash" in sc and sc.get("dcf_content_hash") != s.get("dcf_content_hash"):
        return (f"computed against the score of run {sc.get('dcf_content_hash')!r}, the score on file is run "
                f"{s.get('dcf_content_hash')!r}")
    # v5.7 [whole-PR review fix, 2026-10-21] the notch reprice computed the live tier under: scored.tier_after_notch
    # (None when the score was not notch-eligible) against what reprice.live_misfit reads from THIS score — a rebuild
    # that adds or drops misfit_notch without changing tier_final (a D-tier misfit: D stays D) left the other
    # computation's live tier shown. A live.json with no such key is live_score_identity_missing's.
    if "tier_after_notch" in sc and sc.get("tier_after_notch") != expected_scored_notch(s, n):
        return (f"computed with scored notch {sc.get('tier_after_notch')!r}, the score on file gives "
                f"{expected_scored_notch(s, n)!r} (misfit_notch {'present' if _d(s.get('misfit_notch')) else 'absent'})")
    return None


LIVE_NOTCH_BELOW = {"S": "A", "A": "B", "B": "C", "C": "D"}   # dcf_engine.NOTCH_BELOW (test_misfit_notch_57 pins it)


def expected_scored_notch(score, numbers=None):
    """The scored.tier_after_notch reprice.py writes beside THIS score.json (reprice.live_misfit): the notch of the run's
    numbers tier when score.json carries misfit_notch on a base other than the payable pin, else None."""
    s, n = _d(score), _d(numbers)
    mn = s.get("misfit_notch")
    if not isinstance(mn, dict) or mn.get("not_applied") == "payable_base":
        return None
    t = n.get("tier_by_numbers") or s.get("tier_by_numbers")
    return LIVE_NOTCH_BELOW.get(t, t)


def live_score_identity_missing(lv, score, numbers=None):
    """[Codex review r29 of PR #47, polish review] Why live.json cannot be bound to THIS score.json (None when it can):
    it records no score identity (no scored.dcf_content_hash key: written by the reprice before round 29) beside a
    score.json that carries one. live_shown withholds it, reason live_without_score_identity, right after
    live_not_from_this_score (live_score_problem: what it did record disagrees, so it WAS computed against another
    score). Nothing such a live.json records shows it was computed against another score — right after the merge it
    is every published name's, usually computed against this very score — so its note says only that it records no
    identity and that the next repricing rewrites it; it had been withheld as live_not_from_this_score, whose note says
    it was computed before the current score and that make_score has scored the run since. A recorded null identity
    is a score with no hash, so beside a hashed score it is another score's (live_score_problem); beside a score.json
    with no dcf_content_hash there is no identity to bind (None).
    v5.7 [whole-PR review fix, 2026-10-21] Likewise a live.json that records no scored.tier_after_notch (written before
    reprice read the misfit notch) beside a score.json reprice would notch (expected_scored_notch not None): nothing
    says which notch its live tier was computed under, so it waits for the next repricing too."""
    sc, s = _d(_d(lv).get("scored")), _d(score)
    if "tier_after_notch" not in sc and expected_scored_notch(s, numbers) is not None:
        return ("records no misfit notch (scored.tier_after_notch: written before live.json recorded it), the score on "
                f"file notches its numbers tier to {expected_scored_notch(s, numbers)!r}")
    if "dcf_content_hash" in sc or s.get("dcf_content_hash") is None:
        return None
    return (f"records no score identity (scored.dcf_content_hash: written before live.json recorded it), the score on "
            f"file is run {s.get('dcf_content_hash')!r}")


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
    (Andrew's ruling, 2026-10-20: never described as "pending").
    [Codex review r2 of PR #47] A run whose acquired-IPR&D treatment is
    not_applied_share_count_unverified is never repriced (reprice.py skips it:
    its published tier is the main agent's tier_override with a hand deduction
    no replay can carry), so any live.json on file is withheld, and the record
    says why it has none even without one (reason iprd_share_count_unverified).
    [Codex review r6 of PR #47] The same, reason iprd_unresolved, for a run make_score refused for an unresolved
    acquired-IPR&D charge (iprd_unresolved): reprice.py skips it too, and the score.json on disk is an earlier run's.
    [Codex review r11 of PR #47] And, reason score_not_from_this_run, for any live.json beside a score.json not built
    from this dcf_numbers.json (score_from_run), whatever make_score's reason: live figures pause until the run is
    scored (reprice.py writes none either). A record with no run record has no run to compare (never published).
    [Codex review r13 of PR #47] That check runs with or without a live.json on file (as the IPR&D reasons do; price
    and price_date null without one): reprice.py removes the live.json beside a score from another run, and the
    record must still say why it has no live figures. Without a live.json it applies to every run the site publishes
    (run_published: [Codex review r19 of PR #47] a Tier F or untiered run included — round 13's run_repriceable limit
    left a new Tier F run's page showing the earlier run's verdict with no notice; score_from_run now matches a Tier F
    score to its own run) beside a score.json on file.
    [Codex review r29 of PR #47] After live_from_earlier_run, reason live_not_from_this_score for a live.json beside
    a run record that was not computed against the score.json on file (live_score_problem: no score when it was
    written, an earlier score of the same run, another run's same-day score) — the scored figures are the latest
    available (never "pending", Andrew 2026-10-20); it wins over live_older_than_score (a newer close would not make
    it this score's). [Codex review r29 of PR #47, polish review] Right after it, reason live_without_score_identity
    for a live.json from before round 29 that records no score identity beside a score.json that carries one
    (live_score_identity_missing): it had read live_not_from_this_score, whose note says it was computed before the
    current score, which nothing it records shows; its own note says it records no score identity and that the
    next repricing rewrites it.
    [merge of main #83 into PR #47] Precedence: (as corrected in Codex review r29 of PR #47) in the order the code
    checks them — iprd_unresolved / iprd_share_count_unverified, then score_not_from_this_run (the PR #47 reasons:
    the run is never repriced, or the score on file is not its verdict; the app words them "Live figures withheld —
    …"), then live_from_earlier_run, live_not_from_this_score, live_without_score_identity and live_older_than_score
    (the score on file is the run's; the app words all four "Scored figures are the latest — …"). The prices
    staleness guard
    (row.prices_stale, build() step 5) is not a withheld reason: it is derived independently on every row, whatever
    live_withheld says, and never changes the reason or its note."""
    lv = c.get("live")
    unresolved = iprd_unresolved(c.get("numbers"))
    if unresolved or _d(_d(c.get("numbers")).get("iprd_adjustment")).get("treatment") == IPRD_SHARE_COUNT_UNVERIFIED:
        ok = live_ok(lv)
        return None, {"reason": "iprd_unresolved" if unresolved else "iprd_share_count_unverified",
                      "price": num(lv.get("price")) if ok else None,
                      "price_date": _date10(lv.get("price_date")) if ok else None,
                      "scored_date": _date10(_d(c.get("score")).get("analysis_date")) or _date10(_d(c.get("numbers")).get("as_of")),
                      "method": None, "note": IPRD_UNRESOLVED_NOTE if unresolved else IPRD_WITHHELD_NOTE}
    ok = live_ok(lv)
    if (_d(c.get("numbers")) and (ok or (c.get("score") is not None and run_published(c.get("numbers"))))
            and not score_from_run(c.get("score"), c.get("numbers"))[0]):
        return None, {"reason": "score_not_from_this_run", "price": num(lv.get("price")) if ok else None,
                      "price_date": _date10(lv.get("price_date")) if ok else None,
                      "scored_date": _date10(_d(c.get("score")).get("analysis_date")) or _date10(_d(c.get("numbers")).get("as_of")),
                      "method": None, "note": SCORE_NOT_FROM_RUN_NOTE}
    if not ok:
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
    if _d(c.get("numbers")) and live_score_problem(lv, c.get("score"), c.get("numbers")):
        # [Codex review r29 of PR #47] computed against another score.json than the one on file
        return None, {"reason": "live_not_from_this_score", "price": num(lv.get("price")), "price_date": pd,
                      "scored_date": sa or _date10(_d(c.get("numbers")).get("as_of")), "method": None,
                      "note": LIVE_NOT_FROM_SCORE_NOTE}
    if _d(c.get("numbers")) and live_score_identity_missing(lv, c.get("score"), c.get("numbers")):
        # [Codex review r29 of PR #47, polish review] a live.json from before round 29: no score identity to bind
        return None, {"reason": "live_without_score_identity", "price": num(lv.get("price")), "price_date": pd,
                      "scored_date": sa or _date10(_d(c.get("numbers")).get("as_of")), "method": None,
                      "note": LIVE_NO_SCORE_IDENTITY_NOTE}
    scored = [d for d in (sa, ls) if d]
    sd = max(scored) if scored else None
    if pd is None or sd is None or pd >= sd:
        return lv, None
    method = _d(lv.get("basis_check")).get("method")
    return None, {"reason": "live_older_than_score", "price": num(lv.get("price")), "price_date": pd, "scored_date": sd,
                  "method": method if isinstance(method, str) else None,
                  "note": (f"The last close on file ({pd}) predates the scored analysis ({sd}) — no close after the analysis "
                           f"is on file, so the scored figures are the latest available, as of the {pd} close.")}


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


# ---------------------------------------------------------------- engine 5.7 rulings (lane L6): row summaries
def notch_summary(mn):
    """score.json misfit_notch (R1, Andrew 2026-10-19 — make_score.misfit_notch: every sector misfit publishes one
    tier below its numbers tier) as the index row carries it: {applies, tier_by_numbers, tier_after_notch,
    reason_source, not_applied} — the reason and the detection basis stay in the record. None without the block (a
    modeled name, or a misfit scored before the mechanical notch)."""
    mn = _d(mn)
    if not mn:
        return None
    s = lambda k: mn.get(k) if isinstance(mn.get(k), str) else None  # noqa: E731
    return {"applies": mn.get("applies") is True, "tier_by_numbers": _tier(mn.get("tier_by_numbers")),
            "tier_after_notch": _tier(mn.get("tier_after_notch")), "reason_source": s("reason_source"),
            "not_applied": s("not_applied")}


def live_notch(lv):
    """live.json misfit_notch (reprice.py, L1: the notch of the LIVE numbers tier — {tier_by_numbers,
    tier_after_notch, applies, basis}) as the row carries it, with notch_summary's keys (reason_source and
    not_applied are None: live.json records neither). None without the block."""
    m = _d(_d(lv).get("misfit_notch"))
    if not m:
        return None
    return dict(notch_summary(m), basis=m.get("basis") if isinstance(m.get("basis"), str) else None)


def published_numbers_tier(tier_by_numbers, notch):
    """The tier make_score publishes before any judgment override: the notched tier when the notch applies, else
    the numbers tier. The row's tier_override means 'a judgment override beyond this' (R1, design 01 §5)."""
    if notch and notch.get("applies") and notch.get("tier_after_notch"):
        return notch["tier_after_notch"]
    return tier_by_numbers


TRENDS = ("eroding", "stable", "widening")


def engine_moat_trend(n):
    """The moat trend the engine ran with (M6, design 10): dcf_numbers.json inputs.moat_trend, else the top-level
    copy — the record the recorded hold comes from (never moat_evidence.fade.trend, which make_score re-measures on
    every rebuild). None on a record from before 5.7."""
    n = _d(n)
    for v in (_d(n.get("inputs")).get("moat_trend"), n.get("moat_trend")):
        if v in TRENDS:
            return v
    return None


def recorded_hold_years(n):
    """The growth hold (years at the starting growth before the fade) the run recorded: dcf_engine.recorded_hold_years
    (M6, lane L3b) — inputs.hold_years; 2 when absent (every record before 5.7 held two years); None when it is not an
    int in 0..PROJECTION_YEARS (bool refused). A build without the engine reads exactly the same here [merge L6]: the
    top-level copy is never read (the replay runs inputs.hold_years), so the page and the replay cannot disagree."""
    if ENGINE is not None and hasattr(ENGINE, "recorded_hold_years"):
        try:
            return ENGINE.recorded_hold_years(n)
        except Exception:  # noqa: BLE001
            return None
    inp = _d(_d(n).get("inputs"))
    if "hold_years" not in inp:
        return 2
    v = inp["hold_years"]
    return v if isinstance(v, int) and not isinstance(v, bool) and 0 <= v <= PROJECTION_YEARS else None


def _int_or_none(v):
    return v if isinstance(v, int) and not isinstance(v, bool) else None


def moat_summary(s, n=None, from_run=None):
    """score.json moat_evidence (R4 revised: Dorsey's sources + the evidence scorecard, make_score / moat_scorecard)
    -> the row's summary, else None: {score (the evidence score), status (checked | report_only), within_tolerance,
    divergence, core_score, supporting_adjustment, measure (the governing return: roic | roic_tangible | roe; null when
    the returns_on_capital pillar is not measured — insufficient_data — so the history CSV's moat_return_measure is
    blank there, 03b §7.1), return_median, return_note, sources (the declared source count; null on a record with no
    scorecard — "not declared" is not "no source"), widest (wide | narrow | none | null), flags, industry ({code,
    level, label, ladder, peers, rank, of} when industry_structure was measured, else null), fade_trend (the ENGINE's
    moat trend), fade_in_sync (moat_evidence.fade.in_sync), fade_direction (the current measurement), hold_years
    (engine-recorded, 2 on a record before 5.7)} (03b §7.2, 10 §4).
    [rebase L3b A14, L6 review r3] fade_in_sync / fade_direction are make_score's trend test of the run IT scored:
    they are read only when score.json was built from this run (from_run — score_from_run(s, n)[0], computed here when
    the caller does not pass it), else null; fade_trend and hold_years are always the engine record's."""
    me = _d(s.get("moat_evidence"))
    if not me:
        return None
    if from_run is None:
        from_run = bool(score_from_run(s, n)[0])
    gov, src = _d(me.get("governing")), _d(me.get("sources"))
    ind, fade = _d(_d(me.get("pillars")).get("industry_structure")), (_d(me.get("fade")) if from_run else {})
    roc = _d(_d(me.get("pillars")).get("returns_on_capital"))
    st = lambda d, k: d.get(k) if isinstance(d.get(k), str) else None  # noqa: E731
    # the governing return is measured when its pillar says so (a record without the pillar: when it has a median or a note)
    gov_measured = (roc.get("status") == "measured") if roc else (gov.get("median") is not None or st(gov, "median_note") is not None)
    declared = src.get("declared") is True
    wt, sync = me.get("within_tolerance"), fade.get("in_sync")
    industry = ({"code": st(ind, "group"), "level": _int_or_none(ind.get("level")), "label": st(ind, "label"),
                 "ladder": st(ind, "ladder"), "peers": _int_or_none(ind.get("peers")), "rank": _int_or_none(ind.get("rank")),
                 "of": _int_or_none(ind.get("of"))} if ind.get("status") == "measured" else None)
    return {"score": num(me.get("evidence_score")), "status": st(me, "status"),
            "within_tolerance": wt if isinstance(wt, bool) else None, "divergence": num(me.get("divergence")),
            "core_score": num(me.get("core_evidence_score")), "supporting_adjustment": num(me.get("supporting_adjustment")),
            "measure": st(gov, "measure") if gov_measured else None,
            "return_median": num(gov.get("median")), "return_note": st(gov, "median_note"),
            "sources": _int_or_none(src.get("count")) if declared else None,
            "widest": st(src, "widest") if declared else None,
            "flags": [str(f) for f in _l(me.get("flags"))], "industry": industry,
            "fade_trend": engine_moat_trend(n), "fade_in_sync": sync if isinstance(sync, bool) else None,
            "fade_direction": st(fade, "direction"), "hold_years": recorded_hold_years(n)}


def interim_summary(s):
    """score.json interim_bridge (R2a, a declared 6-K interim bridge; its figures are base_alternatives', R7's one
    record) -> {tier_bridged, tier_annual_median, estimate_legs, measured, published_base} for the row, else None.
    published_base is base_alternatives.published ("declared_interim" when the bridge is the scored base; another
    kind when a STALE_FY rejection published the median, R7)."""
    ib = _d(s.get("interim_bridge"))
    if not ib:
        return None
    alts = _d(s.get("base_alternatives"))
    bases = {b.get("kind"): b for b in _l(alts.get("bases")) if isinstance(b, dict)}
    pub = _d(bases.get("declared_interim")) or _d(ib.get("bridged"))
    med = _d(bases.get("annual_median")) or _d(ib.get("annual_median"))
    measured = med.get("measured") if isinstance(med.get("measured"), bool) else (alts.get("measured") if alts else ib.get("measured"))
    return {"tier_bridged": _tier(pub.get("tier_by_numbers")), "tier_annual_median": _tier(med.get("tier_by_numbers")),
            "estimate_legs": len(_l(ib.get("estimate_legs"))), "measured": measured is True,
            "published_base": alts.get("published") if isinstance(alts.get("published"), str) else None}


def share_basis(n):
    """The share basis the run's per-share figures stand on, for the ranking chip (R6, design 08 §10): "total_units"
    when dcf_numbers.json carries a declared share-class record (traded class + declared exchangeable units), else
    None (the filed diluted count)."""
    sc = _d(_d(n).get("share_classes"))
    return "total_units" if sc.get("declared") is True and not sc.get("counterfactual") else None


def quote_check(folder):
    """check_quotes.check_folder's report on analysis.md, compacted for the Analysis tab (R3, engine 5.7) — or None
    without the checker or without analysis.md. A checker exception is recorded as status 'error', never raised: a
    page must build whatever the checker does."""
    if QUOTES is None or not os.path.isfile(os.path.join(folder, "analysis.md")):
        return None
    try:
        rep = _d(QUOTES.check_folder(folder))
    except Exception as e:  # noqa: BLE001
        return {"status": "error", "gated": False, "engine_release": None, "checked": None, "matched": None,
                "ignored": None, "untraced_count": None, "untraced": [], "integrity": [], "warnings": [],
                "error": f"{type(e).__name__}: {e}"[:300]}
    unt = [u for u in _l(rep.get("untraced")) if isinstance(u, dict)]
    ign = _d(rep.get("ignored"))
    st = rep.get("status") if rep.get("status") in ("pass", "fail", "legacy", "error") else "error"
    _i = lambda v: v if isinstance(v, int) and not isinstance(v, bool) else None  # noqa: E731
    return {"status": st, "gated": rep.get("gated") is True,
            "engine_release": rep.get("engine_release") if isinstance(rep.get("engine_release"), str) else None,
            "checked": _i(rep.get("checked")), "matched": _i(rep.get("matched")),
            "ignored": sum(v for v in ign.values() if _i(v) is not None) if ign else None,
            "untraced_count": len(unt),
            "untraced": [{"line": _i(u.get("line")), "col": _i(u.get("col")), "raw": str(u.get("raw"))[:40],
                          "kind": u.get("kind") if isinstance(u.get("kind"), str) else None}
                         for u in unt[:QUOTE_UNTRACED_MAX]],
            "integrity": [str(x)[:300] for x in _l(rep.get("integrity"))][:10],
            "warnings": [str(x)[:300] for x in _l(rep.get("warnings"))][:20], "error": None}


def score_run_record(score, numbers):
    """record.score_from_run (rebase B5): score_from_run's answer once, for the Data tab's "Content hash" line —
    {matches, mismatches (at most 5, each at most 200 characters)}. The same function live_shown applies (it also
    re-validates the hash over the record, applies the pre-5.6 headline-figure rule and covers Tier F runs)."""
    ok, mm = score_from_run(score, numbers)
    return {"matches": bool(ok), "mismatches": [str(m)[:200] for m in _l(mm)[:5]]}


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
        g0s = [max(ENGINE.GROWTH_FLOOR_START, min(ENGINE.GROWTH_CAP_START, gb + inp["offsets"][i])) for i in range(len(LABELS))]
        # engine 5.7 (M6, design 10 §4): the per-scenario holds the record carries (2 on every record before 5.7)
        hs = ENGINE.recorded_scenario_holds(n, g0s, gterm) if hasattr(ENGINE, "recorded_scenario_holds") else [2] * len(LABELS)
        if hs is None:
            return None, None, False
        for i, k in enumerate(LABELS):
            g0 = g0s[i]
            paths[k] = ENGINE.project_path(base * inp["mults"][i], g0, cap, gterm, hold=hs[i])
            gpaths[k] = ENGINE.growth_path(g0, cap, gterm, hold=hs[i])
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


def iprd_charge(n):
    """The run's one-time acquired-IPR&D charge per share (engine 5.6:
    dcf_engine.iprd_charge_per_share — 0.0 for every record without one, and
    when the engine module is unavailable)."""
    if ENGINE is None or not hasattr(ENGINE, "iprd_charge_per_share"):
        return 0.0
    try:
        return float(ENGINE.iprd_charge_per_share(n))
    except Exception:
        return 0.0


def _value(flows, r, g, charge_ps):
    """IV at r on the replayed flows less the run's one-time charge (dcf_engine.adjusted_value; the identity at 0)."""
    if charge_ps and hasattr(ENGINE, "adjusted_value"):
        return ENGINE.adjusted_value(flows, r, g, charge_ps)
    return ENGINE.present_value(flows, r, g)


def scored_floor(recorded, flows, px, g, charge_ps=0.0):
    """Whether a SCORED IRR sits at the solver's floor. The first boolean in
    `recorded` (the run's own flags — engine 5.4 writes them per scenario and
    for the weighted case) wins. A pre-5.4 run recorded none, so the flag is
    inferred through the engine: solve_irr's at_floor on the replayed flows at
    the scored price (engine 5.6: plus the run's one-time acquired-IPR&D
    charge, dcf_engine.adjusted_irr — the price the scored IRR was solved at).
    Only the flag is taken from the replay — the recorded (historical) IRR is
    never replaced. None when there is neither a flag nor anything to replay."""
    for v in recorded:
        if isinstance(v, bool):
            return v
    flows = _l(flows)
    if not flows or px is None or px <= 0 or ENGINE is None or not hasattr(ENGINE, "solve_irr"):
        return None
    try:
        if charge_ps and hasattr(ENGINE, "adjusted_irr"):
            return bool(ENGINE.adjusted_irr(flows, px, g, charge_ps)[2])
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
    g, w, c = _gterm(n), paths["weighted"], iprd_charge(n)
    return {"15": _value(w, 0.15, g, c), "20": _value(w, 0.20, g, c), "25": _value(w, 0.25, g, c)}


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
    c = iprd_charge(n)
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
                    v = _value(paths[k], rate / 100, g, c)
                except Exception:
                    v = None
            row[str(rate)] = num(v)
        row["irr"] = num(r.get("irr")) if k != "weighted" else (num(r.get("irr")) if r.get("irr") is not None else num(n.get("implied_irr_weighted") if n.get("implied_irr_weighted") is not None else s.get("implied_irr")))
        recorded = (r.get("irr_at_floor"),) if k != "weighted" else _weighted_floor_recorded(n, s)
        row["irr_at_floor"] = scored_floor(recorded, paths.get(k), px, g, c) if row["irr"] is not None else None
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
    inp, scn = _d(n.get("inputs")), _d(n.get("scenarios"))
    return {"paths": paths, "growth_paths": gpaths, "sensitivity": sens, "hurdle_prices": hp, "inputs": inp or None,
            "g_base": num(n.get("g_base")), "g_blend": num(n.get("g_blend")), "g_terminal": _gterm(n),
            "cap_years": num(n.get("cap_years")) if n.get("cap_years") is not None else num(s.get("cap_years")),
            "growth_components": _d(n.get("growth_components")), "growth_components_adjusted": _d(n.get("growth_components_adjusted")) or None,
            "share_cagr": num(n.get("share_cagr")), "share_count_adj": num(n.get("share_count_adj")), "share_adj_basis": n.get("share_adj_basis"),
            "replayed": bool(replayed),
            # engine 5.7 (M6, design 10 §4): the growth hold the moat's direction set — engine-recorded (2 on a record
            # before 5.7; None when malformed), the engine's trend (None before 5.7) and the per-scenario holds
            "hold_years": recorded_hold_years(n), "moat_trend": engine_moat_trend(n),
            "hold_by_scenario": ({k: _d(scn.get(k)).get("hold_years") for k in LABELS}
                                 if any("hold_years" in _d(scn.get(k)) for k in LABELS) else None)}


def irr_at_floor_flag(c, paths):
    """score.irr_at_floor (5.4) → diagnostics.irr_at_floor → weighted.irr_at_floor
    → for an older run, solve_irr's at-floor flag on the replayed weighted path
    at the scored price (scored_floor; the same answer as
    forecast.sensitivity.weighted.irr_at_floor). False when undecidable."""
    s, n = c["score"], c["numbers"]
    return bool(scored_floor(_weighted_floor_recorded(n, s), _d(paths).get("weighted"), _scored_price(n, s), _gterm(n),
                             iprd_charge(n)))


# ---------------------------------------------------------------- index row
def _tier(v):
    return v if isinstance(v, str) and v in ("S", "A", "B", "C", "D", "F") else None


def registry_entries(registry, c, ticker):
    return [e for e in (_l(registry.get(ticker)) or _l(registry.get(c["folder"])) or _l(registry.get(c["score"].get("ticker")))) if isinstance(e, dict)]


def index_row(c, registry, paths, hp, watchlist=(), from_run=None):
    """One index.json row. from_run: score_from_run(score, numbers)[0] when the caller has it (build_record computes
    it once for record.score_from_run); moat_summary computes it otherwise (rebase L3b A14)."""
    s, n = c["score"], c["numbers"]
    lv = c.get("live") if live_ok(c.get("live")) else None
    scn = _d(n.get("scenarios")) or _d(s.get("scenarios"))
    diag = _d(n.get("diagnostics"))
    tier_by_numbers = _tier(s.get("tier_by_numbers")) or _tier(n.get("tier_by_numbers"))
    tier = _tier(s.get("tier_final")) or tier_by_numbers or "?"
    # engine 5.7 rulings: the misfit notch (R1), the moat evidence (R4) and the declared 6-K bridge (R2a) summaries
    mn = notch_summary(s.get("misfit_notch"))
    me, ib = moat_summary(s, n, from_run), interim_summary(s)
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
        # R1 (design 01 §5): a judgment override BEYOND the sector-misfit notch (identical to the old flag without a block)
        "tier": tier, "tier_by_numbers": tier_by_numbers,
        "tier_override": bool(tier_by_numbers and tier != published_numbers_tier(tier_by_numbers, mn)),
        "tier_notched": bool(mn and mn["applies"]), "misfit_notch": mn,
        "tier_by_numbers_live": None, "misfit_notch_live": None,  # set from live.json below
        "tier_live": None, "tier_bear": _tier(s.get("tier_bear")) or tier_for_irr(irr_bear), "tier_bull": _tier(s.get("tier_bull")) or tier_for_irr(irr_bull),
        "irr": irr, "irr_live": None, "irr_bear": irr_bear, "irr_bull": irr_bull,
        "irr_at_floor": irr_at_floor_flag(c, paths), "irr_capped": bool(s.get("irr_capped") or diag.get("irr_capped")),
        "live_withheld": False, "split_restated": None,  # set by build_record (live_shown / restate_split)
        "prices_stale": None,  # set on the index row in build() step 5 (the sweep session set is only known there)
        "f_subtype": s.get("f_subtype") or n.get("f_subtype"),
        "price": price, "price_live": None, "price_date": None, "ret_1y_pct": num(st.get("ret_1y_pct")),
        "iv15": num(s.get("iv_at_15")) if s.get("iv_at_15") is not None else num(n.get("iv_at_15")),
        "iv12": num(s.get("iv_at_12")) if s.get("iv_at_12") is not None else num(n.get("iv_at_12")),
        "iv20": num(hp.get("20")), "iv25": num(hp.get("25")),
        "upside15": num(s.get("upside_at_15_pct")), "upside15_live": None,
        "market_cap_b": num(s.get("market_cap_b")), "market_cap_b_live": None,
        "moat": num(s.get("moat_score")), "moat_evidence": me,
        "cap_years": num(s.get("cap_years")), "confidence": s.get("confidence"),
        "confidence_capped": bool(s.get("confidence_capped")),
        "one_liner": s.get("one_liner"), "analysis_date": s.get("analysis_date"), "engine_release": s.get("engine_release") or n.get("engine_release"),
        "flags": flags_of(s, n),
        "overrides": [{"field": o.get("field"), "kind": o.get("kind")} for o in _l(s.get("overrides")) if isinstance(o, dict) and o.get("field")],
        "interim_bridge": ib, "share_basis": share_basis(n),
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
                "statements": isinstance(c.get("statements"), dict), "profile": isinstance(c.get("profile"), dict),
                "facts": isinstance(c.get("facts"), dict)},
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
                    "irr_at_floor_live": bool(lv.get("irr_at_floor")),
                    # engine 5.7 (R1): reprice.py notches the LIVE numbers tier (a bound live.json only: live_shown)
                    "tier_by_numbers_live": _tier(lv.get("tier_by_numbers")), "misfit_notch_live": live_notch(lv)})
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
    sfr = score_run_record(s, n)   # rebase B5, computed once: record.score_from_run and the row's fade fields (L3b A14)
    row = index_row(c, registry, paths, hp, watchlist, from_run=sfr["matches"])
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
           "facts": c.get("facts"),                                  # facts.json verbatim (R3 declared facts) | null
           "quote_check": quote_check(c["path"]) if c.get("path") else None,  # check_quotes' compact report | null
           "score_from_run": sfr,                                     # rebase B5: is score.json this run's?
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
    are kept; the statements never live in a record, so nothing to drop there).
    Engine 5.7 (lane L6): a declared 6-K interim bridge's ttm.json (ttm.basis
    'declared_interim', R2a — its legs and provenance are the Data tab's Interim
    bridge section, and only a handful of foreign records carry one) is KEPT;
    facts (the Declared facts panel, R3 — Andrew reads the attachment on a phone)
    is kept; a legacy (not gated) quote_check keeps its counts, not its untraced
    list. [whole-PR review fix, 2026-10-21] R9's capitalized-software rows of the
    dropped capex_provenance stay as numbers.capex_software
    (capex_software_summary), so the Data tab's "Capitalized software (in
    capex)" row reaches the attachment."""
    out = {k: v for k, v in rec.items() if k not in ("judgment", "ttm", "statements")}
    ttm = rec.get("ttm")
    if isinstance(ttm, dict) and ttm.get("basis") == "declared_interim":
        out["ttm"] = ttm
    qc = rec.get("quote_check")
    if isinstance(qc, dict) and not qc.get("gated"):
        out["quote_check"] = dict(qc, untraced=[])
    if isinstance(out.get("prices"), dict):
        out["prices"] = {k: v for k, v in out["prices"].items() if k not in ("daily_1y", "sessions_5d")}
    if isinstance(out.get("numbers"), dict):
        soft = capex_software_summary(out["numbers"].get("capex_provenance"))
        out["numbers"] = {k: v for k, v in out["numbers"].items() if k not in TRIM_NUMBERS_KEYS}
        if soft:
            out["numbers"]["capex_software"] = soft
    return out


def capex_software_summary(prov):
    """[whole-PR review fix, 2026-10-21] R9's capitalized-software rows of numbers.capex_provenance in the attachment's
    compact shape {FY end: {"software": {tag: value}, "unit": the intangible leg's filed unit}} — the Data tab's
    "Capitalized software (in capex)" row (app.js capexSoftwareText) — None when no year carries software. The rest of
    capex_provenance stays out of the attachment."""
    out = {}
    for pe, rec in sorted(_d(prov).items()):
        sw = {t: v for t, v in _d(_d(rec).get("software")).items() if num(v) is not None}
        if sw:
            out[pe] = {"software": sw, "unit": _d(rec).get("intangibles_unit") or None}
    return out or None


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


def _csv_moat_median(me):
    """moat_return_median (03b §7.1): the governing return's median as a 6-dp decimal; `inf` for an unbounded median
    (return_note unbounded_high), `-inf` for a loss on non-positive / unstable capital (loss_on_*) — both parse as
    floats in Python and pandas; blank when unmeasured."""
    note = me.get("return_note") if isinstance(me.get("return_note"), str) else ""
    if note == "unbounded_high":
        return "inf"
    if note.startswith("loss_on"):
        return "-inf"
    return _csv_num(me.get("return_median"), 6)


def _csv_int(v):
    """An integer-valued number as plain digits ('' for null): a moat score 6.0 prints 6."""
    v = num(v)
    if v is None:
        return ""
    return str(int(v)) if float(v).is_integer() else f"{v:g}"


def history_key(r):
    """Live IRR desc, then scored IRR desc, then ticker (nulls after values)."""
    lv, sc = num(r.get("irr_live")), num(r.get("irr"))
    return (lv is None, -lv if lv is not None else 0.0, sc is None, -sc if sc is not None else 0.0, str(r.get("ticker") or ""))


def history_rows(index):
    """index.json rows -> HISTORY_COLUMNS value lists, in history_key order.
    Live figures where the row has live.json, else the scored ones: price and
    price_date (the scored price's date is the analysis date), upside at 15%,
    and the bear -> bull band tiers; tier_live / irr_live stay blank without
    live data. Engine 5.7 (append-only): tier_by_numbers (the scored numbers
    tier) and tier_notched (R1: a notched name reads "D (C by numbers)"); the
    moat record (03b §7.1: moat_score, moat_evidence_score 2 dp, the governing
    return's measure and median — inf / -inf for unbounded medians —, the
    declared source count and the widest source, both blank when no scorecard
    is declared, never 0 / none); moat_trend (the engine's, blank before 5.7)
    and hold_years (engine-recorded, 2 before 5.7) (M6); tier_by_numbers_live
    (the live numbers tier reprice notched, blank without live data — whole-PR
    review fix, 2026-10-21: the scored tier_by_numbers is not the live one)."""
    out = []
    for i, r in enumerate(sorted(index, key=history_key), 1):
        live = num(r.get("price_live")) is not None and num(r.get("irr_live")) is not None
        lo, hi = (_tier(r.get("tier_bear_live")), _tier(r.get("tier_bull_live"))) if live else (None, None)
        if lo is None or hi is None:
            lo, hi = _tier(r.get("tier_bear")), _tier(r.get("tier_bull"))
        me = _d(r.get("moat_evidence"))
        hold = me.get("hold_years") if me else 2
        out.append([str(i), _csv_str(r.get("ticker")), _csv_str(r.get("name")), _csv_bool(r.get("fit") == "misfit"),
                    _csv_str(_tier(r.get("tier")) or r.get("tier")), _csv_num(r.get("irr"), 6),
                    _csv_str(_tier(r.get("tier_live"))) if live else "", _csv_num(r.get("irr_live"), 6) if live else "",
                    _csv_str(lo), _csv_str(hi),
                    _csv_num(r.get("price_live") if live else r.get("price"), 2),
                    _csv_str(r.get("price_date") if live else r.get("analysis_date")),
                    _csv_num(r.get("iv15"), 2), _csv_num(r.get("upside15_live") if live else r.get("upside15"), 2),
                    _csv_str(r.get("analysis_date")), _csv_str(r.get("engine_release")),
                    _csv_bool(r.get("alert_eligible")), _csv_bool(r.get("watchlist")),
                    _csv_str(_tier(r.get("tier_by_numbers"))), _csv_bool(r.get("tier_notched")),
                    _csv_int(r.get("moat")), _csv_num(me.get("score"), 2), _csv_str(me.get("measure")),
                    _csv_moat_median(me) if me else "",
                    _csv_int(me.get("sources")) if isinstance(me.get("sources"), int) else "",
                    _csv_str(me.get("widest")) if me.get("sources") is not None else "",
                    _csv_str(me.get("fade_trend")), _csv_int(hold) if hold is not None else "",
                    _csv_str(_tier(r.get("tier_by_numbers_live"))) if live else ""])
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
def builder_code_mtime():
    """The builder's code: this script, the fundamentals.price_dividends it reprices every dividends block with, and
    the quote checker (check_quotes.py with the facts.py and quote_tokens.py it imports) whose report every record
    carries (engine 5.7, R3; rebase B11) — an edit to any of them rebuilds every record."""
    code = [os.path.abspath(__file__)] + [getattr(m, "__file__", None) for m in
                                          (FUND, QUOTES, sys.modules.get("facts"), sys.modules.get("quote_tokens"))
                                          if m is not None]
    return max([os.path.getmtime(p) for p in code if isinstance(p, str) and os.path.exists(p)] or [0.0])


def build(base=None, site_dir=None, only=None, force=False, attachment=False, top=150, quiet=False, now=None, prerender=True):
    base = os.path.abspath(base or os.environ.get("STOCKS_BASE") or os.path.dirname(HERE))
    site_dir = os.path.abspath(site_dir or os.path.join(base, "_daily", "site"))
    data_dir = os.path.join(site_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    only = set(x.strip().upper() for x in only if x.strip()) if only else None
    now = now or datetime.datetime.now(NY)
    built_at, date = now.isoformat(timespec="seconds"), now.date().isoformat()
    builder_mtime = builder_code_mtime()
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
    # Prices staleness guard (2026-10-20, with reprice.sweep_price_staleness):
    # a scored name whose last close on file is more than one session behind
    # the newest close the sweep holds was missed by the refresh — flag it on
    # the row and name it in meta instead of letting it sit silently behind a
    # withheld live block (HALO sat two sessions behind for two days in
    # October 2026). The session set is the union of the candidates' own
    # daily_1y series dates (plus their terminal dates), so no market
    # calendar is needed and a session no cache happens to END on still
    # counts; one session behind is the normal posting lag. Re-derived on
    # every row on every build, like the watchlist flag.
    last_close, session_set = {}, set()
    for t, c in current.items():
        if t not in rows:
            continue  # no surviving row (its record failed to build): not a candidate — it cannot
            # be flagged or counted, and its dates must not shift the baseline (Codex review of PR #83)
        pj = _d(jload(os.path.join(c["path"], "prices.json")))
        ld = _date10(_d(pj.get("stats")).get("last_date"))
        if ld:
            last_close[t] = ld
        for row in _l(pj.get("daily_1y")):
            if isinstance(row, (list, tuple)) and row:
                sd = _date10(row[0])
                if sd:
                    session_set.add(sd)
    sessions = sorted(session_set | set(last_close.values()))
    stale_prices = {}
    if sessions:
        for t, ld in last_close.items():
            behind = sum(1 for s in sessions if s > ld)
            if behind > 1:
                stale_prices[t] = {"last_date": ld, "sessions_behind": behind, "latest_close": sessions[-1]}
    for r in rows.values():
        r["prices_stale"] = stale_prices.get(r.get("ticker") or "")
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
        notes.append(f"{len(withheld)} live repricing(s) withheld — a live.json close older than the scored analysis, a score.json "
                     "not built from the latest engine run, a live.json computed before the current score or recording no "
                     "score identity, or a record "
                     "reprice.py never reprices (acquired-IPR&D charge "
                     "deducted by hand or unresolved; record.live_withheld.reason) — "
                     "scored figures shown, row.live_withheld: " + ", ".join(withheld))
    if stale_prices:
        notes.append(f"{len(stale_prices)} scored name(s) hold a last close on file more than one session behind the sweep's latest close ({sessions[-1]}) — prices.py has not refreshed them (row.prices_stale): "
                     + ", ".join(f"{t} (last close {stale_prices[t]['last_date']})" for t in sorted(stale_prices)))
    misfits = sum(1 for r in index if r.get("fit") == "misfit")
    notched = sum(1 for r in index if r.get("tier_notched"))
    if notched or misfits:
        notes.append(f"sector misfits: {misfits} ({notched} published one tier below their numbers tier — the mechanical "
                     "notch, Andrew 2026-10-19; row.misfit_notch / tier_notched)")
    if QUOTES is None:
        notes.append("quote checker unavailable (check_quotes.py did not import): record.quote_check is null")
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
            "counts": {"current": len(index), "stale": len(stale), "misfits": misfits,
                       "tiers": tiers, "with_live": sum(1 for r in index if _d(r.get("has")).get("live")),
                       "live_withheld": len(withheld), "prices_stale": len(stale_prices), "split_restated": len(restated),
                       "watchlist": sum(1 for r in index if r.get("watchlist")), "failed": len(failed),
                       "statements": sum(1 for r in index if _d(r.get("has")).get("statements")),
                       "profiles": sum(1 for r in index if _d(r.get("has")).get("profile")),
                       # engine 5.7 rulings (R1-R4, M6)
                       "notched": notched, "facts": sum(1 for r in index if _d(r.get("has")).get("facts")),
                       "moat_checked": sum(1 for r in index if _d(r.get("moat_evidence")).get("status") == "checked"),
                       "interim_bridged": sum(1 for r in index if r.get("interim_bridge")
                                              and _d(r.get("interim_bridge")).get("published_base") in (None, "declared_interim")),
                       "moat_eroding": sum(1 for r in index if "MOAT_EROSION" in _l(_d(r.get("moat_evidence")).get("flags"))),
                       "moat_widening": sum(1 for r in index if "MOAT_WIDENING" in _l(_d(r.get("moat_evidence")).get("flags")))},
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
