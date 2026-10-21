#!/usr/bin/env python3
"""Live repricing (v5.4, 2026-10-14).

Usage: python3 reprice.py <TICKER> | --all   [--quiet]

The scored run's expected return (weighted IRR) was solved at whatever price
the engine fetched on scoring day. The last close moves every day; the owner's
earnings paths do not. This script re-solves every scenario IRR and the
weighted IRR on the SAME paths at the last close in <TICKER>/prices.json
(prices.py — Nasdaq last close) and writes <TICKER>/live.json. Nothing here
is estimated: the paths are the scored run's own (replayed from its recorded
inputs via dcf_engine.replay_paths, exactly as the engine computed them), the
price is the filed close, and every other figure is arithmetic on the two.

Eligible: a current dcf_numbers.json (engine_version >= 5, scenarios and
inputs present, base_oe_per_share > 0, tier_by_numbers not F / null) AND a
prices.json for THIS ticker whose close is not stale against the scored run:
  * prices.json["ticker"] must equal the folder name (a copied file is refused);
  * stats.last and stats.last_date must both be present;
  * the file must have been refreshed on or after the scored run's as_of —
    `fetched_at` (prices.py writes it) on or after as_of; for an older
    prices.json without `fetched_at`, last_date no more than STALE_DAYS
    calendar days before as_of (a weekend / holiday gap is not staleness, a
    failed refresh is). prices.py is non-blocking and --all leaves the old
    file in place on a failed fetch, so this is the only thing that stops an
    old close from being labelled "last close".
  * the scored run's per-share basis must still be today's (check_basis —
    Codex review of PR #2): the paths, IVs and share count are in the share
    units of the scoring day, the last close in today's. Nasdaq's historical
    closes are split-adjusted on every pull (verified 2026-10-15 on splits in
    this universe: CMG 50:1 2024-06-26 — the 2024-06-07 close reads $63.38,
    $3,169 / 50; SMCI 10:1 2024-10-01 — 2024-09-13 reads $45.72; IBKR 4:1
    2025-06-18 — 2025-06-06 reads $52.96), so prices.json's close on the
    scoring day is in TODAY's units. The scored price over the nearest close
    (the scored day's or the session before it; weekly closes for a run older
    than daily_1y) is ~1 when nothing happened: within ORDINARY_LOG_TOL
    (|ln ratio| <= 0.10, i.e. the quote within about 10% of the close; the
    largest gap in the universe on 2026-10-14 was an intraday quote 4.3% off,
    HIG) nothing changes. A ratio within SPLIT_LOG_TOL (0.05 in log terms) of
    exactly one ratio in SPLIT_RATIOS (2:1 to 10:1, 12, 15, 20, 25, 30, 40,
    50 and 100 to 1, 3:2 and 5:2, and the reverse of each; anything else,
    11:1 or 5:4 say, is refused, never guessed) is a split since scoring:
    every per-share value of the run (the scenario paths, IV@15/12/20/25, the
    scored price) is divided by the factor and the share count multiplied by
    it, so the IRR is solved in one unit (an unmoved price reproduces the
    scored IRR) and live.json records `split_factor` and `basis_check`
    (factor, ratio, scored price raw / adjusted, the reference close and
    date, any split filed with the SEC after the run per fundamentals.json —
    evidence only, its dates are approximate). Anything else — no reference
    close, a ratio that is neither ordinary nor one clean split — is refused
    like the cases below: a repriced IRR in mixed units is never published;
    the scored figures stand until the run is re-scored. Two timing rules
    (Codex review of PR #2, second round):
      - Nasdaq posts a session's daily row hours after the close, so on
        scoring day (and through every market-hours refresh) the series
        usually stops BEFORE the scored session. Such closes hold no session
        after the scored run, so they cannot carry a split since scoring (its
        ex-date is after the scored date): the basis is "ok" with factor 1
        and method "no_close_since_scoring", and the quote's gap to the prior
        close — that day's move — is never fitted to a split ratio. Fitting
        it read a -33% day as a 2:3 reverse split and refused a -15% earnings
        day; the ratio test runs once the scored session's close is posted.
        (A series that stops more than REF_WINDOW_DAYS before the scored date
        is a stale pull, not that lag, and is refused as unverifiable.)
      - Should Nasdaq ever post a post-split close before adjusting the
        history, the reference close would still read in the scored units
        and the step would sit in the series. A one-session move into a
        session after the scored date whose size is a clean split ratio
        (split_like_moves) is therefore HELD while it is among the newest
        HOLD_SESSIONS closes: no live.json until the history is adjusted (a
        split, then divided out above) or the move has stood that long (a
        real move: SMCI, ZS and DFTX each had one in the year to 2026-10).
    A corporate action of 10% or less (an 11:10 stock dividend) sits inside
    the ordinary band and cannot be told from quote noise by price alone;
    none appears in the universe's SEC split records.
Everything else (Tier F, data gap, pre-v5 or pre-stamp runs without inputs,
no / stale / foreign / unreadable prices.json, an unverifiable or unexplained
per-share basis, a held split-sized move, unreadable dcf_numbers.json):
nothing is written, a stale live.json is deleted, the reason is listed in the
--all summary and a single ticker exits 3. So, since Codex review round 11
of PR #47, does a score.json that is unreadable, not an object or not built
from this run (below), and, since Codex review round 29, a folder with no
score.json yet (make_score has not scored the run: no verdict to reprice).
A close that passes that gate but is older than STALE_DAYS against today
(the refresh keeps failing) is still written — it is newer than the scored
price — but flagged `stale_price` with `price_age_days`, named in the --all
summary and kept out of its tier-change list.

Sweep staleness guard (2026-10-20): the check above compares a close to
TODAY; sweep_price_staleness compares it to the sweep itself — every scored
name whose last close on file is more than one session behind the newest
close on file across the sweep (the session set is the union of the names'
own daily_1y series dates; one session behind is the normal posting lag).
--all prints a
WARNING block naming each such name: a refresh that silently never runs —
October 2026, when the bulk refresh was not executing and HALO sat two
sessions behind for two days, visible only as a withheld live block — can
no longer pass unnoticed. build_site.py flags the same names in the site
data (row.prices_stale, meta.counts.prices_stale).

live.json: price, price_date, the scored price/date and the % move, the live
weighted IRR + tier, the five scenario IRRs / tiers (with the solver's capped /
at-floor flags), the band (irr_bear / irr_bull, tier_bear / tier_bull), the
price-independent IVs (copied from the run; iv_at_20 / 25 replayed when the
run predates them), upside at 15 / 12, market cap at the live price, the
scored headline for comparison and the delta (pp and tier change).

Tiers and agent overrides. `tier_by_numbers` is the numbers tier at the live
price (tier_for_irr of the live weighted IRR). `tier` (= `tier_display`) is
what the page badges: when score.json carries an active override
(tier_final != tier_by_numbers) and the live numbers tier still equals the
scored numbers tier, the price move changed nothing and the override is
PRESERVED (`tier` = tier_final, `override_active` true). Only when the numbers
tier itself moved does the live numbers tier take over, flagged
`override_superseded` so the page can say so. `delta.tier_changed` is the
numbers tier vs the scored numbers tier; `delta.tier_changed_vs_final` is the
displayed tier vs the scored final tier (what a reader sees move).
Since engine 5.7 (v5.7 below) a sector misfit's live tier is one notch below
its live numbers tier (D/F and a payable-earnings base not notched), as
recorded in score.json misfit_notch, and an "override" is a final tier other
than the scored NOTCHED tier; a superseded override gives way to the notched
live tier.
An override is only read from a score.json built from THIS dcf_numbers.json
(score_matches_run — Codex review of PR #2: a same-day score from an earlier
engine run used to pass on its date alone, and its stale tier_final was kept
as an "override"). make_score.py copies the run's numbers verbatim, so the
score must agree with the run on analysis_date = as_of, tier_by_numbers
(which must also be the tier the recorded weighted IRR gives), implied_irr
(4 dp), price, base_oe_per_share, iv_at_15 (2 dp), engine_version and
engine_release. Any disagreement used to write live.json with
`score_json_fresh` false, `score_mismatch` listing each field and no override;
since Codex review round 11 of PR #47 it writes NO live.json (check_score —
the new run's figures beside another run's verdict are not a live repricing
of that verdict), so `score_json_fresh` is true and `score_mismatch` null on
every live.json written (since round 29 a folder with no score.json writes
none either). Since Codex review round 12 of PR #47 make_score also copies
the run's content_hash into score.json
(dcf_content_hash): a score carrying it matches only the run with that
(valid) hash — run_hash_problem — since rounded headline figures cannot tell
two same-day runs apart; a score built earlier, without it, is judged on the
headline figures as before.

Exit codes: 0 written; 2 usage; 3 single ticker skipped (reason printed).
--all exits 0 whenever the sweep itself completes.

v5.5 (2026-10-19, engine release 5.5.0 — decision 1, ADS market cap): the live
`market_cap_est` (and `in_scope_under_40b`, which follows it) is computed by
live_market_cap with the engine's own formula, dcf_engine.market_cap_est:
last close × shares ÷ numbers.ads_ratio.ratio when an ADS ratio applies (the
price is per ADS, the share count per ordinary share — the old price × shares
put TLK's live cap at $1.09T beside its $10.93B score), times the split factor
as before. The share count is the one the run's market cap used
(numbers.market_cap_basis.shares_used: a split- or scale-corrected diluted
count or the cover-page count) when the run records it, else
shares_diluted_latest. Without an ADS ratio the figure is unchanged bit for
bit (close × shares_diluted_latest × split_factor) for a run whose
market_cap_basis.shares_source is diluted_latest, or with no basis record;
otherwise the count is market_cap_basis.shares_used (M6, round-1
verification: an HBAN-shaped dei_latest run prices on the cover-page count).

v5.6 (2026-10-19, engine release 5.6.0 — Andrew's acquired-IPR&D decision): a
run whose dcf_numbers.json carries iprd_adjustment with treatment
one_time_value_deduction deducted a one-time charge per share from every IV
and solved every IRR at price + charge. The live IRRs are solved the same way
(dcf_engine.adjusted_irr at the last close + the charge, the charge divided by
the split factor like every per-share value), a replayed IV is
dcf_engine.adjusted_value, and live.json records `iprd_charge_per_share` (in
today's share units; 0.0 for every other record, which reprices exactly as
before). Without it the site would show unadjusted live returns.
[Codex review round 2 of PR #47] A run whose treatment is
not_applied_share_count_unverified (a share-scale defect rescued by a pin with
no power-of-ten factor: the engine deducted nothing, and make_score publishes
it only through the main agent's tier_override quantifying a hand deduction)
is skipped like an unverifiable per-share basis (check_eligible: no live.json,
a stale one removed): its live IRRs would be the unadjusted ones, and a moved
numbers tier would supersede the override with them. build_site withholds
any live.json of such a record (record.live_withheld reason
iprd_share_count_unverified) and shows the scored figures.
[Codex review round 6 of PR #47] So is every run make_score refuses for an
unresolved acquired-IPR&D charge (dcf_engine.iprd_unresolved: a period
awaiting its cash-flow check, or excluded non_usd_no_rate with a positive
native expense or cash outflow, whatever the treatment): the engine wrote its
dcf_numbers.json, the score.json on disk is an earlier run's, and
score_matches_run's mismatch alone only drops the tier override — the live
IRRs would be the refused run's unadjusted ones. build_site withholds any
live.json of such a record (reason iprd_unresolved).
[Codex review round 11 of PR #47, the main agent's general rule] No live
figures exist for a run its score.json was not built from, whatever the
reason: make_score refused the run (an unresolved charge, a deleted deferred
payment its registry recorded, any other refusal) or has not run on it yet.
reprice() raises Skip when the score.json it is given does not pass
score_matches_run, and reprice_folder skips (no live.json, a stale one
removed) when the folder's score.json is unreadable, not an object or not
from this run — before, a mismatch only dropped the tier override and
live.json still carried the new run's figures beside the old run's verdict.
make_score copies the run's figures verbatim, so a release-mismatch rebuild
of the same run still reprices. Live figures therefore pause between an
engine run and its make_score.
[Codex review round 29 of PR #47, the main agent's shape] A folder with no
score.json yet had still been repriced (score_json_fresh null, tier_final
unknown) on the reasoning that build_site publishes only scored folders —
but once make_score scored that same run (with a tier_override, say) the
folder was published and the old live.json passed every check (same run,
same dates), so the page showed the numbers tier at the last close and the
agent's override was silently dropped until the next reprice. Now
reprice_folder treats a folder with no score.json as unscored: no live.json
is written, an existing one is removed and the reason given, exactly as for
a score.json from another run (pure reprice() still accepts scored=None —
it writes nothing). And live.json records the score it was computed
against — score_json_fresh, scored.tier_final, scored.tier_override_reason
(when the override was active) and scored.dcf_content_hash (the score's run
identity) — so build_site.live_score_problem withholds a live.json computed
against any other score.json (reason live_not_from_this_score): a pre-score
repricing, one computed before make_score re-scored the same run (an
override added or removed), or one beside a same-day score of another run.
[Codex review round 29 of PR #47, polish review] A live.json this script
wrote before round 29 records no scored.dcf_content_hash: beside a
score.json that carries one, build_site.live_score_identity_missing
withholds it (reason live_without_score_identity) until the next run here
rewrites it.

v5.7 (2026-10-19, engine release 5.7.0 — Andrew's ruling R1, the mechanical
sector-misfit notch; lane L1): make_score publishes every sector misfit one
tier below its numbers tier (score.json misfit_notch), and the live tier
follows the same rule at the last close. live_misfit decides it from the
score's own block: a score.json with misfit_notch (not on the payable-earnings
base) is notched live — `tier` is notch_tier(live numbers tier), so a misfit
scored B -> C reads C at the scored price, B when the live numbers tier is A,
D when it is C or D (D / F are never notched: a numbers tier of D stays D).
An override is now a final tier other than the scored notched tier
(override_active): a legacy one-notch override is the notch and follows the
live numbers tier; a judgment downgrade below the notch is kept while the
numbers tier holds and then gives way to the NOTCHED live tier (it used to be
the raw one). A score.json with no block (a misfit scored before 5.7, whose
final tier is the legacy tier_override) reprices exactly as before until
make_score rebuilds it, so build_site.live_score_problem's check of
scored.tier_override_reason holds in every state with no build_site change.
live.json adds `misfit_notch` {tier_by_numbers, tier_after_notch, applies,
basis} (null on a modeled name) and `scored.tier_after_notch`; the BASIS text
and one_line say so ("numbers B, misfit notch"). Pure use without a score.json
(tests) reads dcf_engine.misfit_status on the record and the folder_sic given;
reprice_folder passes none. A rebuild that changes tier_final makes the
existing live.json mismatch scored.tier_final, so it is withheld until
`reprice.py --all` rewrites it — run it after every rebuild apply.
"""
import json, math, os, re, sys, datetime, hashlib
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.environ.get("STOCKS_BASE") or os.path.dirname(HERE)
sys.path.insert(0, HERE)
import dcf_engine as E  # noqa: E402

LABELS = ["super_bear", "bear", "base", "bull", "super_bull"]
PRICE_SOURCE = "prices.json (Nasdaq last close)"
BASIS = ("same base OE/share, scenario paths and probabilities as the scored run (and the same one-time acquired-IPR&D "
         "charge per share, iprd_charge_per_share, when the run deducted one); only the price moved; "
         "per-share values are restated in today's share units when a split since the scored run is detected (split_factor); "
         "an agent tier override (score.json tier_final, from this same engine run) is preserved in `tier` unless the numbers tier itself moved; "
         "a sector misfit's live tier is one notch below its live numbers tier (D/F and a payable-earnings base not notched), "
         "as recorded in score.json misfit_notch")
IPRD_SHARE_COUNT_UNVERIFIED = "not_applied_share_count_unverified"  # dcf_engine's treatment name; never repriced
STALE_DAYS = 4  # a prices.json without fetched_at: last_date may trail as_of by a weekend + holiday, never more

# Per-share basis check (see the module docstring). Tolerances are on |ln(ratio)|.
ORDINARY_LOG_TOL = 0.10   # scored quote vs the nearest split-adjusted close, nothing happened (largest seen 2026-10-14: 0.042, HIG)
SPLIT_LOG_TOL = 0.05      # residual around a clean split ratio: the same quote noise, after the split is divided out
REF_WINDOW_DAYS = 7       # the reference close lies within a week of the scored date
HOLD_SESSIONS = 3         # a clean-ratio one-session move after the scored date is held while it is among the newest closes


def _split_ratios():
    """((factor, label), ...): factor = new shares per scored-run share
    (2.0 for a 2:1 split, 0.1 for a 1:10 reverse split). Nothing finer than
    3:2: a 5:4 or 4:3 split (ln 0.22 / 0.29) sits too close to a large
    ordinary quote gap to tell apart, so such a ratio is refused, never
    guessed. Every window (+-SPLIT_LOG_TOL) is disjoint from the others and
    from the ordinary band (a test checks it), so at most one ratio fits."""
    out = []
    for p, q in ((2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1), (8, 1), (9, 1), (10, 1), (12, 1), (15, 1), (20, 1),
                 (25, 1), (30, 1), (40, 1), (50, 1), (100, 1), (3, 2), (5, 2)):
        out += [(p / q, f"{p}:{q}"), (q / p, f"{q}:{p}")]
    return tuple(out)


SPLIT_RATIOS = _split_ratios()


class Skip(Exception):
    """The folder is not eligible for a live price; the message is the reason."""


def _f(v):
    try:
        if v is None or isinstance(v, bool):
            return None
        return float(v)
    except (TypeError, ValueError):
        return None


def _load(path):
    """Parse a JSON file; Skip (never a traceback) when it is missing,
    unreadable or not valid JSON. JSONDecodeError is a ValueError."""
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError) as e:
        raise Skip(f"{os.path.basename(path)} unreadable: {type(e).__name__}: {e}") from e


def check_eligible(numbers):
    """Raise Skip with the reason when the run cannot be repriced."""
    if not isinstance(numbers, dict):
        raise Skip("dcf_numbers.json is not an object")
    ev = numbers.get("engine_version")
    if not isinstance(ev, (int, float)) or ev < 5:
        raise Skip(f"pre-v5 engine output (engine_version {ev!r}) — re-run pending")
    if numbers.get("data_gap_uncovered") or numbers.get("tier_by_numbers") is None:
        gaps = numbers.get("data_gap_uncovered") or numbers.get("data_gap") or []
        raise Skip(f"data gap ({', '.join(gaps) or 'no tier emitted'}) — no tier to reprice")
    if numbers.get("tier_by_numbers") == "F":
        raise Skip(f"Tier F ({numbers.get('f_subtype') or 'no positive owner\'s earnings'}) — no IRR exists at any price")
    if not numbers.get("scenarios"):
        raise Skip("no scenarios recorded")
    if not numbers.get("inputs"):
        raise Skip("no recorded inputs (v5 run before input stamping) — re-run pending")
    base = _f(numbers.get("base_oe_per_share"))
    if base is None or base <= 0:
        raise Skip(f"base_oe_per_share {numbers.get('base_oe_per_share')!r} is not positive")
    if _f(numbers.get("price")) is None:
        raise Skip("scored run has no price")
    blk = numbers.get("iprd_adjustment")
    if isinstance(blk, dict) and blk.get("treatment") == IPRD_SHARE_COUNT_UNVERIFIED:
        # [Codex review r2 of PR #47] withheld like an unverifiable per-share basis: the engine deducted nothing and the
        # published tier is the main agent's tier_override with a hand deduction reprice cannot replay, so live IRRs
        # here would be the unadjusted ones and a moved numbers tier would supersede the override with them
        raise Skip(f"acquired-IPR&D treatment {IPRD_SHARE_COUNT_UNVERIFIED}: the charge was deducted by hand in the main "
                   "agent's tier_override (share count unverified), which a live repricing cannot replay — no live figures")
    why = E.iprd_unresolved(numbers)
    if why:
        # [Codex review r6 of PR #47] make_score refused this run (ACQUIRED_IPRD_UNCONFIRMED / _UNCONVERTED), so the
        # score.json on disk is an earlier run's: live IRRs here would be the refused run's unadjusted ones
        raise Skip(f"acquired-IPR&D charge unresolved ({why}): make_score refuses this run, so the score on file is an "
                   "earlier run's and a live repricing would carry unadjusted figures — no live figures")


def _date(s):
    try:
        return datetime.date.fromisoformat(str(s)[:10])
    except (TypeError, ValueError):
        return None


def live_price(prices, ticker=None, scored_as_of=None):
    """(price, price_date) from prices.json stats. Skip when stats.last or
    stats.last_date is absent, when the file belongs to another ticker, or
    when the close is stale against the scored run (see module docstring)."""
    if not isinstance(prices, dict):
        raise Skip("prices.json is not an object")
    st = prices.get("stats") if isinstance(prices.get("stats"), dict) else {}
    px = _f(st.get("last"))
    if px is None or px <= 0:
        raise Skip("prices.json has no stats.last")
    price_date = st.get("last_date")
    if _date(price_date) is None:
        raise Skip("prices.json has no stats.last_date")
    if ticker and prices.get("ticker") and str(prices.get("ticker")).upper() != str(ticker).upper():
        raise Skip(f"prices.json belongs to {prices.get('ticker')}, not {ticker} — run prices.py {ticker}")
    as_of = _date(scored_as_of)
    if as_of is not None:
        fetched = _date(prices.get("fetched_at"))
        if fetched is not None:
            if fetched < as_of:
                raise Skip(f"prices.json fetched {fetched.isoformat()} predates the scored run {as_of.isoformat()} — run prices.py")
        elif (as_of - _date(price_date)).days > STALE_DAYS:
            raise Skip(f"prices.json last_date {price_date} predates the scored run {as_of.isoformat()} by more than {STALE_DAYS} days — run prices.py")
    return px, price_date


def _closes(rows):
    """[(date, close)] from a prices.json series ([[date, close], ...]),
    ascending; malformed rows are dropped."""
    out = []
    for r in rows if isinstance(rows, list) else []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            d, c = _date(r[0]), _f(r[1])
            if d is not None and c is not None and c > 0:
                out.append((d, c))
    return sorted(out)


def reference_closes(prices, as_of):
    """[(date, close)] the scored quote is compared with, all in today's
    (split-adjusted) units: the last two daily closes on or before the scored
    date within REF_WINDOW_DAYS — the scored session's own close and the one
    before it (a pre-market run quotes the prior close, an intraday run sits
    near them). A run older than daily_1y falls back to the weekly closes
    within REF_WINDOW_DAYS either side of the scored date."""
    lo = as_of - datetime.timedelta(days=REF_WINDOW_DAYS)
    daily = [(d, c) for d, c in _closes(prices.get("daily_1y")) if lo <= d <= as_of]
    if daily:
        return daily[-2:]
    hi = as_of + datetime.timedelta(days=REF_WINDOW_DAYS)
    return [(d, c) for d, c in _closes(prices.get("weekly")) if lo <= d <= hi]


def filed_splits_after(fund, as_of):
    """Splits fundamentals.json (SEC ratio facts) dates after the scored run:
    [{effective, ratio}], [] when none, None when the file has no split
    record. Evidence only: a ratio fact is tagged at approval / record /
    distribution / fiscal-year-end dates and filed a quarter late, so it can
    neither date nor detect a split on its own."""
    div = fund.get("dividends") if isinstance(fund, dict) else None
    rows = div.get("split_adjustments") if isinstance(div, dict) else None
    if not isinstance(rows, list):
        return None
    out = []
    for r in rows:
        eff = _date(r.get("effective")) if isinstance(r, dict) else None
        if eff is not None and eff > as_of:
            out.append({"effective": eff.isoformat(), "ratio": _f(r.get("ratio"))})
    return out


def _split_fit(ratio):
    """[(factor, label, |ln residual|)] of the clean split ratios within
    SPLIT_LOG_TOL of `ratio` (at most one: the windows are disjoint)."""
    return [(k, label, abs(math.log(ratio) - math.log(k))) for k, label in SPLIT_RATIOS
            if abs(math.log(ratio) - math.log(k)) <= SPLIT_LOG_TOL]


def split_like_moves(prices, as_of):
    """[{from_date, from_close, to_date, to_close, ratio, split}]: one-session
    moves INTO a session after the scored date, among the newest
    HOLD_SESSIONS daily closes, whose size is a clean split ratio (prior
    close / close within SPLIT_LOG_TOL of one). Nasdaq's history is
    split-adjusted, so a split shows no such step once it is adjusted; one
    that is there is either a real move of exactly that size or a split
    whose history Nasdaq has not adjusted yet, which the closes alone cannot
    tell apart. A move into the scored session itself is not counted: the
    scored quote already carries it."""
    daily = _closes(prices.get("daily_1y")) if isinstance(prices, dict) else []
    out = []
    for (d0, c0), (d1, c1) in list(zip(daily, daily[1:]))[-HOLD_SESSIONS:]:
        if d1 <= as_of:
            continue
        for _k, label, _res in _split_fit(c0 / c1):
            out.append({"from_date": d0.isoformat(), "from_close": c0, "to_date": d1.isoformat(), "to_close": c1,
                        "ratio": c0 / c1, "split": label})
    return out


def check_basis(numbers, prices, fund=None):
    """The scored run's per-share basis vs today's (see the module docstring).
    Returns the basis_check record — status "ok" (factor 1.0) or
    "split_adjusted" (factor = new shares per scored-run share, the split
    label and the evidence) — or raises Skip when the basis cannot be
    verified, is not explained by exactly one clean split ratio, or a fresh
    one-session move after the scored date has a split's exact size (held:
    see split_like_moves): a repriced IRR in mixed units is never published."""
    scored_px, as_of = _f(numbers.get("price")), _date(numbers.get("as_of"))
    if scored_px is None or scored_px <= 0 or as_of is None:
        raise Skip("scored run has no price or as_of — its per-share basis cannot be checked against prices.json")
    if not isinstance(prices, dict):
        raise Skip("prices.json is not an object")
    fund_splits = filed_splits_after(fund, as_of)

    def record(status, k, label, fitted, method="ratio"):
        res, d, c = fitted
        return {"status": status, "factor": k, "split": label, "method": method,
                "scored_price_raw": scored_px, "scored_price_adjusted": scored_px / k, "scored_date": as_of.isoformat(),
                "ref_close": c, "ref_close_date": d.isoformat(), "observed_ratio": scored_px / c, "log_residual": res,
                "filed_splits_after_scoring": fund_splits}

    # Nasdaq posts a session's daily row hours after the close (all 93 files
    # pulled 2026-10-15 19:29-20:49 ET ended at 10-14), so on scoring day, and
    # all through the market-hours refresh, the series stops BEFORE the scored
    # session. Its closes then hold no session after the scored run, so no
    # split since scoring can be in them (its ex-date is after the scored
    # date): the last close is in the scored quote's own units, factor 1, and
    # the quote's distance from the prior close is that day's move, never a
    # split ratio (a -33% day used to read as a 2:3 reverse split, a -15%
    # earnings day as an unexplained mismatch). A series that stops more than
    # REF_WINDOW_DAYS before the scored date is not that lag but a stale pull,
    # refused below like any basis that cannot be checked.
    daily = _closes(prices.get("daily_1y"))
    if daily and as_of - datetime.timedelta(days=REF_WINDOW_DAYS) <= daily[-1][0] < as_of:
        d, c = daily[-1]
        return record("ok", 1.0, None, (abs(math.log(scored_px / c)), d, c), method="no_close_since_scoring")
    refs = reference_closes(prices, as_of)
    if not refs:
        raise Skip(f"prices.json has no close within {REF_WINDOW_DAYS} days of the scored date {as_of.isoformat()} — "
                   "the per-share basis cannot be checked (a split since scoring would go unnoticed); run prices.py")

    def fit(k):
        # (|ln residual|, date, close): the reference close that best explains the scored quote at factor k
        return min((abs(math.log(scored_px / c) - math.log(k)), d, c) for d, c in refs)

    # The run records its quote but not the time of day, so the quote may be
    # the prior close (pre-market), any intraday print, or the scored close:
    # a quote within ORDINARY_LOG_TOL of either reference close is ordinary.
    # Otherwise, when the two closes agree (an ordinary session), exactly one
    # clean split ratio must explain the quote. When the scored session itself
    # moved more than ORDINARY_LOG_TOL, a quote between the two closes is that
    # day's trading (factor 1), and a split-sized gap to one of them cannot be
    # told apart from the day's move (a -33% open that closed -20% fits 2:3
    # against the prior close), so it is refused rather than read as a split
    # (Codex review of PR #2, second round).
    lo_c, hi_c = min(c for _, c in refs), max(c for _, c in refs)
    refs_agree = math.log(hi_c / lo_c) <= ORDINARY_LOG_TOL
    ordinary = fit(1.0)
    _, d0, c0 = ordinary
    seen = (f"scored ${scored_px:,.2f} ({as_of.isoformat()}) vs split-adjusted close ${c0:,.2f} "
            f"({d0.isoformat()}), ratio {scored_px / c0:.4f}")
    if ordinary[0] <= ORDINARY_LOG_TOL:
        out = record("ok", 1.0, None, ordinary)
    else:
        hits = [(k, label, fit(k)) for k, label in SPLIT_RATIOS]
        hits = [h for h in hits if h[2][0] <= SPLIT_LOG_TOL]
        if not refs_agree:
            day_move = (f"the closes around the scored date moved {(refs[-1][1] / refs[0][1] - 1) * 100:+.1f}% "
                        f"({refs[0][0].isoformat()} -> {refs[-1][0].isoformat()})")
            if hits:
                raise Skip(f"per-share basis ambiguous: {seen}; {day_move}, and the quote fits a {hits[0][1]} split "
                           "against one of them, which cannot be told apart from that day's move — no repriced IRR "
                           "published (the scored figures stand); re-score the run")
            if not lo_c * math.exp(-ORDINARY_LOG_TOL) <= scored_px <= hi_c * math.exp(ORDINARY_LOG_TOL):
                raise Skip(f"per-share basis mismatch: {seen}; {day_move} and the quote lies more than ~10% outside "
                           "both — no repriced IRR published (the scored figures stand); re-score the run")
            out = record("ok", 1.0, None, ordinary, method="within_scored_day_range")
        else:
            if len(hits) > 1:
                raise Skip(f"per-share basis ambiguous: {seen} fits more than one split ratio "
                           f"({', '.join(h[1] for h in hits)}) — no repriced IRR published; re-score the run")
            if not hits:
                raise Skip(f"per-share basis mismatch: {seen} — the scored quote is more than ~10% from both the scored "
                           "session's close and the one before it, and no clean split ratio explains it; no repriced IRR "
                           "published (the scored figures stand); re-score the run")
            k, label, fitted = hits[0]
            out = record("split_adjusted", k, label, fitted)
    # A split Nasdaq has not adjusted the history for yet would leave the
    # reference close in the scored units and put the step in the series
    # instead: hold while such a step is fresh. Adjusted within HOLD_SESSIONS
    # it is divided out above; still there after that, it was a real move
    # (2025-10..2026-10: three in the universe — SMCI, ZS, DFTX).
    held = split_like_moves(prices, as_of)
    if held:
        m = held[-1]
        raise Skip(f"held: the {m['from_date']} -> {m['to_date']} close moved {(1 / m['ratio'] - 1) * 100:+.1f}% "
                   f"(${m['from_close']:,.2f} -> ${m['to_close']:,.2f}), the exact size of a {m['split']} split that "
                   f"Nasdaq may not have adjusted the history for yet — no repriced IRR until the history is adjusted "
                   f"(a split, then divided out) or the move has stood {HOLD_SESSIONS} sessions (a real move, then repriced)")
    return out


# dcf_engine.market_cap_est — one formula for the engine,
# make_score and this script (no local copy that could drift).
_market_cap_estimate = E.market_cap_est


def live_market_cap(numbers, price, factor=1.0):
    """Market cap at `price` (today's share units) — see the module docstring
    (v5.5). Shares: numbers.market_cap_basis.shares_used when the run recorded
    the count its market cap used, else shares_diluted_latest; divided by
    numbers.ads_ratio.ratio when an ADS ratio applies; multiplied by the split
    factor after, exactly as before (so a non-ADS run whose shares_source is
    diluted_latest, or with no basis record, is bit-identical; any other
    shares_source prices on shares_used)."""
    mb = numbers.get("market_cap_basis")
    shares = _f(mb.get("shares_used")) if isinstance(mb, dict) else None
    if not shares:
        shares = _f(numbers.get("shares_diluted_latest"))
    ads = numbers.get("ads_ratio")
    ratio = ads.get("ratio") if isinstance(ads, dict) else None
    if isinstance(ratio, bool) or not isinstance(ratio, (int, float)) or ratio <= 0:
        ratio = None  # make_score only accepts a positive number; anything else is no ratio (as in the engine)
    mcap = _market_cap_estimate(price, shares, ratio) if shares else None
    return mcap * factor if mcap is not None else None


def _same(a, b, tol):
    a, b = _f(a), _f(b)
    return a is not None and b is not None and abs(a - b) <= tol


# [Codex review r13 of PR #47] the first engine release whose score.json must carry dcf_content_hash (make_score
# writes it for every run since round 12; build_site.HASH_REQUIRED_FROM_RELEASE mirrors it, a test holds the two equal)
HASH_REQUIRED_FROM_RELEASE = "5.6.0"


def _release_tuple(rel):
    """'5.6.0' -> (5, 6, 0); '5.5' -> (5, 5, 0); None / unparseable -> None (make_score.release_tuple)."""
    m = re.match(r"\s*(\d+)\.(\d+)(?:\.(\d+))?", rel) if isinstance(rel, str) else None
    return tuple(int(x or 0) for x in m.groups()) if m else None


def requires_content_hash(d):
    """[Codex review r13 of PR #47] True when a score.json / dcf_numbers.json names an engine_release at or after
    HASH_REQUIRED_FROM_RELEASE: its score is the run's only through dcf_content_hash."""
    t = _release_tuple(d.get("engine_release")) if isinstance(d, dict) else None
    return t is not None and t >= _release_tuple(HASH_REQUIRED_FROM_RELEASE)


def run_hash_problem(scored, numbers):
    """[Codex review r12 of PR #47] None when score.json's dcf_content_hash equals the run's content_hash and that
    hash matches the record's content (make_score's own integrity check); else the mismatch. [Codex review r13 of
    PR #47] A score.json with no dcf_content_hash is judged on the headline comparison alone only when neither it
    nor the run is release HASH_REQUIRED_FROM_RELEASE or later (a run from an earlier release); a current-release
    score without it is another run's (make_score writes the hash for every such run)."""
    if "dcf_content_hash" not in scored:
        if requires_content_hash(scored) or requires_content_hash(numbers):
            rel = scored.get("engine_release") if requires_content_hash(scored) else numbers.get("engine_release")
            return (f"score.json carries no dcf_content_hash though the run is release {rel} (make_score writes it "
                    f"for every run since release {HASH_REQUIRED_FROM_RELEASE}: rounded headline figures are not "
                    "run identity)")
        return None
    h, ch = scored.get("dcf_content_hash"), numbers.get("content_hash")
    if not h or h != ch:
        return f"dcf_content_hash {h!r} vs run content_hash {ch!r} (another engine run)"
    canon = json.dumps({k: v for k, v in numbers.items() if k != "content_hash"},
                       sort_keys=True, separators=(",", ":"), default=str)
    if hashlib.sha256(canon.encode()).hexdigest() != ch:
        return "run content_hash does not match its content (dcf_numbers.json edited after the engine run)"
    return None


def score_matches_run(scored, numbers):
    """(matches, mismatches): whether score.json was built by make_score.py
    from THIS dcf_numbers.json. make_score copies the run's figures verbatim
    (implied_irr rounded to 4 dp, iv_at_15 to 2 dp), so every one must agree,
    and the numbers tier must also be the tier the run's own weighted IRR
    gives. A shared date alone is not identity (Codex review of PR #2).
    [Codex review r12 of PR #47] Nor are rounded headline figures: a score.json
    carrying dcf_content_hash (make_score writes it since round 12) must name
    this run's content_hash, itself valid (run_hash_problem); one without it
    is judged on the headline figures as before only for a run from before
    release 5.6.0 ([Codex review r13 of PR #47]: a current-release score.json
    with no hash is another run's). [Codex review r19 of PR #47] A run with no
    weighted IRR (Tier F or untiered) is matched by the same identity: its
    score.json carries no implied_irr either and the same f_subtype (before, it
    never matched: tier_for_irr(None) is None, not 'F'). build_site mirrors it."""
    if not isinstance(scored, dict):
        return False, ["score.json is not an object"]
    mm = []
    hp = run_hash_problem(scored, numbers)
    if hp:
        mm.append(hp)
    if not scored.get("analysis_date") or scored.get("analysis_date") != numbers.get("as_of"):
        mm.append(f"analysis_date {scored.get('analysis_date')!r} vs run as_of {numbers.get('as_of')!r}")
    tier_run = numbers.get("tier_by_numbers")
    # [Codex review r19 of PR #47] a run with no weighted IRR (Tier F / untiered): none on the score either, same f_subtype
    no_irr = _f(numbers.get("implied_irr_weighted")) is None and tier_run in ("F", None)
    tier_irr = E.tier_for_irr(_f(numbers.get("implied_irr_weighted")))
    if not no_irr and tier_run != tier_irr:
        mm.append(f"run tier_by_numbers {tier_run!r} is not the tier of its weighted IRR ({tier_irr!r})")
    if scored.get("tier_by_numbers") != tier_run:
        mm.append(f"tier_by_numbers {scored.get('tier_by_numbers')!r} vs run {tier_run!r}")
    if no_irr:
        if scored.get("implied_irr") is not None:
            mm.append(f"implied_irr {scored.get('implied_irr')!r} vs run None (a run with no weighted IRR)")
        if scored.get("f_subtype") != numbers.get("f_subtype"):
            mm.append(f"f_subtype {scored.get('f_subtype')!r} vs run {numbers.get('f_subtype')!r}")
    elif not _same(scored.get("implied_irr"), numbers.get("implied_irr_weighted"), 0.5e-4 + 1e-9):
        mm.append(f"implied_irr {scored.get('implied_irr')!r} vs run {numbers.get('implied_irr_weighted')!r}")
    # copied verbatim (price, base) or rounded to 2 dp (iv_at_15); absent on both sides is no evidence either way
    for key, tol in (("price", 1e-9), ("base_oe_per_share", 1e-9), ("iv_at_15", 0.005 + 1e-9)):
        a, b = scored.get(key), numbers.get(key)
        if a is None and b is None:
            continue
        if not _same(a, b, tol if key == "iv_at_15" else tol * max(1.0, abs(_f(b) or 0.0))):
            mm.append(f"{key} {a!r} vs run {b!r}")
    for key in ("engine_version", "engine_release"):
        if scored.get(key) != numbers.get(key):
            mm.append(f"{key} {scored.get(key)!r} vs run {numbers.get(key)!r}")
    if scored.get("ticker") and numbers.get("ticker") and str(scored["ticker"]).upper() != str(numbers["ticker"]).upper():
        mm.append(f"ticker {scored.get('ticker')!r} vs run {numbers.get('ticker')!r}")
    return not mm, mm


def check_score(scored, numbers):
    """[Codex review r11 of PR #47] Raise Skip unless `scored` (the folder's score.json, None when there is none)
    was built from THIS run (score_matches_run). A score from another run means make_score refused this run or has
    not run on it yet: its verdict is not this run's, so no live figures are written for either (they pause between
    an engine run and its make_score). scored=None passes here (the pure reprice() computes the numbers tier);
    [Codex review r29 of PR #47] reprice_folder, the only writer, refuses a folder with no score.json first
    (NO_SCORE_REASON)."""
    if scored is None:
        return
    ok, mm = score_matches_run(scored, numbers)
    if not ok:
        raise Skip("score.json is not from this engine run (" + "; ".join(mm) + "): make_score refused this run or has "
                   "not scored it yet, so the verdict on file is another run's — no live figures until make_score "
                   "scores this run")


def live_misfit(numbers, scored, folder_sic=None):
    """v5.7 (L1, R1): (eligible, basis) — whether the live tier is one notch below the live numbers tier.
    With a score.json (every folder reprice_folder writes): exactly when it carries make_score's misfit_notch block
    and the base is not the payable-earnings pin (basis "score_json"; a D / F misfit is eligible too — a live numbers
    tier of C publishes D). A score with no block — a modeled name, or a misfit scored before engine 5.7 whose final
    tier is a legacy one-notch tier_override — is not eligible, so such a folder reprices exactly as before the notch
    (its override kept or superseded by the raw numbers tier) and build_site.live_score_problem's mirror of the
    recorded override reason still holds; the next make_score rebuild adds the block. Without a score (pure use only):
    never on a payable_base run, else dcf_engine.misfit_status on the record and the given folder SIC (basis
    "engine" / "folder_sic"). Pure."""
    if isinstance(scored, dict):
        mn = scored.get("misfit_notch")
        if isinstance(mn, dict):
            return mn.get("not_applied") != "payable_base", "score_json"
        return False, None
    if not isinstance(numbers, dict) or numbers.get("payable_base"):
        return False, None
    fit, b = E.misfit_status(numbers, sic=(folder_sic, None, "folder_sic") if folder_sic else None)
    if fit != "misfit":
        return False, None
    return True, ("folder_sic" if (b or {}).get("source") == "folder_sic" else "engine")


def reprice(numbers, price, price_date=None, scored=None, today=None, prices=None, fund=None, folder_sic=None):
    """Pure function: the live.json payload for a recorded run at `price`.
    `scored` is the folder's score.json (for tier_final) when available.
    `folder_sic` (v5.7, pure use without a score only): the folder's SIC code
    for the misfit rule (live_misfit); reprice_folder never passes it — every
    folder it reprices has a score.json, whose misfit_notch block decides.
    `prices` is the folder's prices.json: when given, the run's per-share
    basis is checked against it (check_basis) and a split since scoring is
    divided out of every per-share value; `fund` (fundamentals.json) only
    adds the SEC's split record to that evidence. Without `prices` the basis
    is "unchecked" (factor 1); reprice_folder always passes it.
    Raises Skip when the run is not eligible, its per-share basis cannot be
    verified, or its paths cannot be replayed."""
    check_eligible(numbers)
    check_score(scored, numbers)
    if prices is not None:
        basis = check_basis(numbers, prices, fund)
    else:
        basis = {"status": "unchecked", "factor": 1.0, "split": None}
    factor = basis["factor"]
    paths, _ = E.replay_paths(numbers)
    if not paths or any(k not in paths for k in LABELS + ["weighted"]):
        raise Skip("scenario paths could not be replayed from the recorded inputs")
    if factor != 1.0:
        # every flow is per scored-run share: restate it per share today
        paths = {k: [f / factor for f in v] for k, v in paths.items()}
    inp = numbers["inputs"]
    gterm = inp.get("g_terminal", E.DEFAULT_GTERM)
    scn_rec, w_rec = numbers["scenarios"], numbers.get("weighted") or {}
    # v5.6: the scored run's one-time acquired-IPR&D charge per share (0.0 — the identity — for every record without
    # one): a year-0 outflow on the same paths, so the live IRR is solved at the close + the charge, exactly as the
    # engine solved the scored IRR. Per scored-run share, so restated per today's share like the paths.
    charge = E.iprd_charge_per_share(numbers)
    if factor != 1.0:
        charge = charge / factor

    scenarios = {}
    for k in LABELS:
        irr, capped, floor = E.adjusted_irr(paths[k], price, gterm, charge)
        scenarios[k] = {"irr": irr, "tier": E.tier_for_irr(irr), "irr_capped": bool(capped), "irr_at_floor": bool(floor)}
    w = paths["weighted"]
    irr_w, w_capped, w_floor = E.adjusted_irr(w, price, gterm, charge)
    tier_numbers = E.tier_for_irr(irr_w)

    # Intrinsic values do not depend on the price: copy the run's own figures;
    # a pre-5.4 run never stored the 20 / 25% hurdle prices, so replay those
    # on the same weighted path (present_value is the engine's own function).
    # The recorded ones are per scored-run share: divided by the split factor.
    # (A 5.6 record's recorded IVs already carry the IPR&D deduction; the
    # replay subtracts it through the engine's adjusted_value.)
    def iv(rate_key, rate):
        v = _f(w_rec.get(rate_key))
        if v is None:
            v = _f(numbers.get(rate_key))
        return v / factor if v is not None else E.adjusted_value(w, rate, gterm, charge)
    iv15, iv12, iv20, iv25 = iv("iv_at_15", 0.15), iv("iv_at_12", 0.12), iv("iv_at_20", 0.20), iv("iv_at_25", 0.25)

    mcap = live_market_cap(numbers, price, factor)  # v5.5: ÷ ads_ratio when one applies
    scored_price = _f(numbers.get("price"))
    if scored_price is not None:
        scored_price /= factor  # in today's share units, like `price`
    scored_irr = _f(numbers.get("implied_irr_weighted"))
    scored_tier = numbers.get("tier_by_numbers")
    # The agent's override (tier_final != tier_by_numbers, reason in analysis.md)
    # is a judgment on the business, not on the price: keep it while the numbers
    # tier is where it was on scoring day; let the live numbers tier through —
    # flagged — only when the price move actually moved the numbers tier.
    # Only a score.json built from THIS run carries this run's judgment:
    # [Codex review r11 of PR #47] check_score has already refused one from another run
    scored_fresh = isinstance(scored, dict)
    scored_final = scored.get("tier_final") if scored_fresh else None
    # v5.7 (L1, R1): a sector misfit's tier is one notch below its numbers tier, live as when scored — the live tier
    # is the notch of the LIVE numbers tier, and only a final tier other than the scored notch is an override
    notch_ok, notch_basis = live_misfit(numbers, scored if scored_fresh else None, folder_sic)
    scored_notched = E.notch_tier(scored_tier) if notch_ok else scored_tier
    live_notched = E.notch_tier(tier_numbers) if notch_ok else tier_numbers
    _mn = scored.get("misfit_notch") if scored_fresh and isinstance(scored.get("misfit_notch"), dict) else {}
    override_active = bool(scored_fresh and scored_final and scored_notched
                           and (scored_final != scored_notched
                                # an override in force AT the notched tier (the acquired-IPR&D hand deduction —
                                # never repriced, check_eligible) keeps its reason, as build_site's mirror expects
                                or (_mn.get("applies") and scored.get("tier_override_reason"))))
    numbers_moved = tier_numbers != scored_tier
    if override_active and not numbers_moved:
        tier, override_superseded = scored_final, False
    else:
        tier, override_superseded = live_notched, override_active
    tz_today = today or datetime.datetime.now(ZoneInfo("America/New_York")).date().isoformat()
    # The close comes from a file refreshed on or after the scored day
    # (live_price enforces that; until Nasdaq posts the scored session's row it
    # is the close before it), but a refresh that keeps failing leaves it old
    # against TODAY: say so, so the page can mark it and --all keeps it out of
    # the tier-change summary.
    age = (_date(tz_today) - _date(price_date)).days if (_date(tz_today) and _date(price_date)) else None
    irrs = [s["irr"] for s in scenarios.values()]
    out = {
        "ticker": numbers.get("ticker"),
        "as_of": tz_today,
        "price": price,
        "price_date": price_date,
        "price_source": PRICE_SOURCE,
        "price_age_days": age,
        "stale_price": (age > STALE_DAYS) if age is not None else None,
        "scored_price": scored_price,
        "scored_date": numbers.get("as_of"),
        "split_factor": factor,
        "basis_check": basis,
        "iprd_charge_per_share": charge,
        "score_json_fresh": True if scored_fresh else None,
        "score_mismatch": None,   # [Codex review r11 of PR #47] a mismatching score.json writes no live.json
        "price_change_pct": (price / scored_price - 1) * 100 if scored_price else None,
        "irr_weighted": irr_w,
        "tier": tier,
        "tier_display": tier,
        "tier_by_numbers": tier_numbers,
        "override_active": override_active,
        "override_superseded": override_superseded,
        # v5.7 (L1, R1): the live notch — null on a modeled name (and on a misfit whose score.json predates the notch)
        "misfit_notch": ({"tier_by_numbers": tier_numbers, "tier_after_notch": live_notched,
                          "applies": tier_numbers in E.NOTCH_BELOW, "basis": notch_basis} if notch_ok else None),
        "irr_base": scenarios["base"]["irr"],
        "irr_bear": scenarios["bear"]["irr"],
        "irr_bull": scenarios["bull"]["irr"],
        "tier_bear": scenarios["bear"]["tier"],
        "tier_bull": scenarios["bull"]["tier"],
        "irr_low": min(irrs),
        "irr_high": max(irrs),
        "irr_capped": bool(w_capped),
        "irr_at_floor": bool(w_floor),
        "scenarios": scenarios,
        "iv_at_15": iv15,
        "iv_at_12": iv12,
        "iv_at_20": iv20,
        "iv_at_25": iv25,
        "upside_at_15": iv15 / price - 1,
        "upside_at_12": iv12 / price - 1,
        "market_cap_est": mcap,
        "in_scope_under_40b": (mcap < 40e9) if mcap is not None else None,
        "scored": {
            "irr_weighted": scored_irr,
            "tier_by_numbers": scored_tier,
            "tier_after_notch": scored_notched if notch_ok else None,   # v5.7 (L1): the scored notched tier
            "tier_final": scored_final,
            "tier_override_reason": (scored or {}).get("tier_override_reason") if (override_active and isinstance(scored, dict)) else None,
            # [Codex review r29 of PR #47] the score's run identity: with score_json_fresh, tier_final and the
            # override reason, what build_site.live_score_problem compares with the score.json on file
            "dcf_content_hash": scored.get("dcf_content_hash") if scored_fresh else None,
            "upside_at_15": _f(numbers.get("upside_at_15")),
        },
        "delta": {
            "irr_pp": (irr_w - scored_irr) * 100 if scored_irr is not None else None,
            "tier_changed": numbers_moved,
            "tier_changed_vs_final": tier != (scored_final or scored_notched),
        },
        "engine_release_of_run": numbers.get("engine_release") or f"pre-5.4 (engine_version {numbers.get('engine_version')})",
        "basis": BASIS,
    }
    return out


# [Codex review r29 of PR #47] a folder make_score has not scored: no verdict to reprice (the same Skip path as a
# score.json from another run — no live.json, a stale one removed, the reason listed / exit 3)
NO_SCORE_REASON = ("no score.json: make_score has not scored this engine run, so there is no verdict to reprice — no "
                   "live figures until make_score scores this run")


def _remove_stale(folder):
    p = os.path.join(folder, "live.json")
    if os.path.exists(p):
        os.remove(p)
        return True
    return False


def reprice_folder(ticker):
    """Write <ticker>/live.json. Returns the payload; raises Skip (after
    deleting any stale live.json) when the folder is not eligible — including
    when dcf_numbers.json or prices.json is missing, unreadable, foreign or
    stale, or when the run's per-share basis does not match today's and no
    single clean split explains it, or a fresh split-sized move is held
    (check_basis), or [Codex review r11 of PR #47] when score.json is
    unreadable, not an object or not built from this run (check_score), or
    [Codex review r29 of PR #47] when there is no score.json at all
    (NO_SCORE_REASON: it had been repriced with scored=None, tier_final
    unknown, and that live.json was shown once make_score scored the run);
    fundamentals.json is optional evidence only."""
    folder = os.path.join(BASE, ticker)
    try:
        np_, pp_ = os.path.join(folder, "dcf_numbers.json"), os.path.join(folder, "prices.json")
        if not os.path.isfile(np_):
            raise Skip("no dcf_numbers.json")
        numbers = _load(np_)
        check_eligible(numbers)
        # [Codex review r11 of PR #47] a score.json that cannot be shown to be this run's writes no live.json
        sp = os.path.join(folder, "score.json")
        if not os.path.isfile(sp):
            raise Skip(NO_SCORE_REASON)
        try:
            scored = _load(sp)
        except Skip as e:
            raise Skip(f"{e} — it cannot be shown to be from this engine run, so no live figures") from e
        if not isinstance(scored, dict):
            raise Skip("score.json is not an object — it cannot be shown to be from this engine run, so no live figures")
        check_score(scored, numbers)
        if not os.path.isfile(pp_):
            raise Skip("no prices.json — run prices.py first")
        prices = _load(pp_)
        price, price_date = live_price(prices, ticker, numbers.get("as_of"))
        fund = None
        fp = os.path.join(folder, "fundamentals.json")
        if os.path.isfile(fp):
            try:
                fund = _load(fp)
            except Skip:
                fund = None  # evidence only: never fails the name
        live = reprice(numbers, price, price_date, scored, prices=prices, fund=fund)
    except Skip:
        _remove_stale(folder)
        raise
    tmp = os.path.join(folder, "live.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(live, f, indent=1)
    os.replace(tmp, os.path.join(folder, "live.json"))
    return live


def _pct(x):
    return "n/a" if x is None else f"{x * 100:.2f}%"


def one_line(live):
    s = live["scored"]
    d = live["delta"]
    mn = live.get("misfit_notch") or {}   # v5.7 (L1): the live misfit notch
    scored_shown = s["tier_by_numbers"] + (f" (final {s['tier_final']})" if (live["override_active"] or (
        s.get("tier_after_notch") and s.get("tier_final") and s["tier_final"] != s["tier_by_numbers"])) else "")
    live_shown = live["tier"] + (f" (numbers {live['tier_by_numbers']}, override kept)" if (live["override_active"] and not live["override_superseded"])
                                 else f" (numbers moved from {s['tier_by_numbers']}, override {s['tier_final']} superseded"
                                      + (", misfit notch)" if mn.get("applies") else ")") if live["override_superseded"]
                                 else f" (numbers {live['tier_by_numbers']}, misfit notch)" if mn.get("applies") else "")
    return (f"{live['ticker']}: scored ${live['scored_price']:.2f} ({live['scored_date']}) "
            f"{scored_shown} {_pct(s['irr_weighted'])} -> live ${live['price']:.2f} ({live['price_date']}) "
            f"{live_shown} {_pct(live['irr_weighted'])} ({d['irr_pp']:+.2f}pp"
            f"{', TIER CHANGED' if d['tier_changed'] else ''}"
            f"{', at floor' if live['irr_at_floor'] else ''}{', capped' if live['irr_capped'] else ''}"
            f"{(', STALE PRICE (' + str(live['price_age_days']) + ' days old)') if live['stale_price'] else ''}"
            f"{(', SPLIT ' + str(_split_label(live)) + ' since scoring, per-share values restated') if _split_label(live) else ''}"
            f"{', scored session close not posted yet' if _basis_method(live) == 'no_close_since_scoring' else ''}); "
            f"band {live['tier_bear']}->{live['tier_bull']}; IV@15 ${live['iv_at_15']:.2f} ({live['upside_at_15'] * 100:+.1f}%)")


def _split_label(live):
    b = live.get("basis_check")
    return b.get("split") if isinstance(b, dict) and b.get("status") == "split_adjusted" else None


def _basis_method(live):
    b = live.get("basis_check")
    return b.get("method") if isinstance(b, dict) else None


def company_folders():
    out = []
    for name in sorted(os.listdir(BASE)):
        if name.startswith(("_", ".")):
            continue
        if os.path.isfile(os.path.join(BASE, name, "dcf_numbers.json")):
            out.append(name)
    return out


def sweep_price_staleness():
    """({ticker: {"last_date": d, "sessions_behind": n}}, latest_close | None):
    the scored names whose last close on file (prices.json stats.last_date,
    else as_of) is more than one trading session behind the newest close the
    sweep holds. The population is the scored folders (score.json +
    dcf_numbers.json) — exactly what prices.py --all maintains; an unscored
    engine leftover is not a missed refresh, is never reported, and its
    cache dates never enter the session baseline (Codex review of PR #83).
    The session set is the union of the dates in the names' own daily_1y
    series (plus their terminal dates), so no market calendar is needed
    and a session no cache happens to END on still counts — counting
    distinct terminal dates alone would call a Fri→Tue gap one session
    (Codex review of PR #83, second round). A name one session behind —
    the normal lag while Nasdaq posts the newest session — is not
    flagged. A name the refresh missed falls further behind every day;
    in October 2026 the bulk refresh silently never ran and HALO sat two
    sessions behind for two days, visible only as a withheld live block.
    Missing / unreadable prices.json files are skipped, never fatal:
    a guard must not break the run it guards."""
    last, session_set = {}, set()
    for t in company_folders():
        if not os.path.isfile(os.path.join(BASE, t, "score.json")):
            continue
        try:
            p = _load(os.path.join(BASE, t, "prices.json"))
        except Skip:
            continue
        if not isinstance(p, dict):
            continue
        daily = p.get("daily_1y")
        if isinstance(daily, list):
            for row in daily:
                if isinstance(row, (list, tuple)) and row:
                    sd = _date(row[0])
                    if sd:
                        session_set.add(sd)
        stats = p.get("stats") if isinstance(p.get("stats"), dict) else {}
        d = _date(stats.get("last_date")) or _date(p.get("as_of"))
        if d:
            last[t] = d
    sessions = sorted(session_set | set(last.values()))
    if not sessions:
        return {}, None
    stale = {}
    for t, d in last.items():
        behind = sum(1 for s in sessions if s > d)
        if behind > 1:
            stale[t] = {"last_date": d.isoformat(), "sessions_behind": behind}
    return stale, sessions[-1].isoformat()


def staleness_warning_lines(stale, latest):
    """The loud surface for sweep_price_staleness: a WARNING header plus one
    line per stale name. Printed by --all after its summary (and for a
    single-ticker run whose name is stale), never gated on --quiet."""
    if not stale:
        return []
    lines = [f"WARNING: {len(stale)} scored name(s) hold a last close more than one session behind the sweep's latest close ({latest}) — prices.py has not refreshed them:"]
    for t in sorted(stale):
        v = stale[t]
        lines.append(f"  STALE-PRICES {t}: last close {v['last_date']}, {v['sessions_behind']} sessions behind — run prices.py {t}")
    return lines


def main():
    argv = sys.argv[1:]
    quiet = "--quiet" in argv
    args = [a for a in argv if not a.startswith("--")]
    if "--all" in argv:
        written, skipped, changed, stale, split = [], [], [], [], []
        for t in company_folders():
            try:
                live = reprice_folder(t)
                written.append(t)
                if _split_label(live):
                    split.append(f"{t} {_split_label(live)}")
                if live["stale_price"]:
                    stale.append(f"{t} ({live['price_date']})")
                elif live["delta"]["tier_changed"]:
                    changed.append(f"{t} {live['scored']['tier_by_numbers']}->{live['tier_by_numbers']}"
                                   + (f" (override {live['scored']['tier_final']} superseded)" if live["override_superseded"] else ""))
                if not quiet:
                    print(one_line(live))
            except Skip as e:
                skipped.append((t, str(e)))
            except Exception as e:  # never let one bad folder stop the sweep
                skipped.append((t, f"ERROR {type(e).__name__}: {e}"))
        print(f"reprice.py --all: {len(written)} live.json written, {len(skipped)} skipped"
              + (f"; tier changed at the live price: {', '.join(changed)}" if changed else "")
              + (f"; STALE close (> {STALE_DAYS} days old, run prices.py): {', '.join(stale)}" if stale else "")
              + (f"; split since scoring, per-share values restated: {', '.join(split)}" if split else ""))
        for t, why in skipped:
            print(f"  skipped {t}: {why}")
        stale_sweep, latest_close = sweep_price_staleness()
        for line in staleness_warning_lines(stale_sweep, latest_close):
            print(line)
        sys.exit(0)
    if not args:
        print(__doc__); sys.exit(2)
    ticker = args[0].upper()
    try:
        live = reprice_folder(ticker)
    except Skip as e:
        print(f"reprice.py: {ticker} skipped — {e} (no live.json; any stale one removed)")
        sys.exit(3)
    print(one_line(live))
    stale_sweep, latest_close = sweep_price_staleness()
    if ticker in stale_sweep:
        for line in staleness_warning_lines({ticker: stale_sweep[ticker]}, latest_close):
            print(line)
    if not quiet:
        print(json.dumps(live, indent=1))


if __name__ == "__main__":
    main()
