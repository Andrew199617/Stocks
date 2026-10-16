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
--all summary and a single ticker exits 3. An unreadable score.json only
degrades the scored block (tier_final unknown); it never fails the name.
A close that passes that gate but is older than STALE_DAYS against today
(the refresh keeps failing) is still written — it is newer than the scored
price — but flagged `stale_price` with `price_age_days`, named in the --all
summary and kept out of its tier-change list.

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
An override is only read from a score.json built from THIS dcf_numbers.json
(score_matches_run — Codex review of PR #2: a same-day score from an earlier
engine run used to pass on its date alone, and its stale tier_final was kept
as an "override"). make_score.py copies the run's numbers verbatim, so the
score must agree with the run on analysis_date = as_of, tier_by_numbers
(which must also be the tier the recorded weighted IRR gives), implied_irr
(4 dp), price, base_oe_per_share, iv_at_15 (2 dp), engine_version and
engine_release. Any disagreement: `score_json_fresh` false, `score_mismatch`
lists each field, no override is applied and scored.tier_final is null
(unknown for this run), exactly as for an unreadable score.json.

Exit codes: 0 written; 2 usage; 3 single ticker skipped (reason printed).
--all exits 0 whenever the sweep itself completes.
"""
import json, math, os, sys, datetime
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.environ.get("STOCKS_BASE") or os.path.dirname(HERE)
sys.path.insert(0, HERE)
import dcf_engine as E  # noqa: E402

LABELS = ["super_bear", "bear", "base", "bull", "super_bull"]
PRICE_SOURCE = "prices.json (Nasdaq last close)"
BASIS = ("same base OE/share, scenario paths and probabilities as the scored run; only the price moved; "
         "per-share values are restated in today's share units when a split since the scored run is detected (split_factor); "
         "an agent tier override (score.json tier_final, from this same engine run) is preserved in `tier` unless the numbers tier itself moved")
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


def _same(a, b, tol):
    a, b = _f(a), _f(b)
    return a is not None and b is not None and abs(a - b) <= tol


def score_matches_run(scored, numbers):
    """(matches, mismatches): whether score.json was built by make_score.py
    from THIS dcf_numbers.json. make_score copies the run's figures verbatim
    (implied_irr rounded to 4 dp, iv_at_15 to 2 dp), so every one must agree,
    and the numbers tier must also be the tier the run's own weighted IRR
    gives. A shared date alone is not identity (Codex review of PR #2)."""
    if not isinstance(scored, dict):
        return False, ["score.json is not an object"]
    mm = []
    if not scored.get("analysis_date") or scored.get("analysis_date") != numbers.get("as_of"):
        mm.append(f"analysis_date {scored.get('analysis_date')!r} vs run as_of {numbers.get('as_of')!r}")
    tier_run = numbers.get("tier_by_numbers")
    tier_irr = E.tier_for_irr(_f(numbers.get("implied_irr_weighted")))
    if tier_run != tier_irr:
        mm.append(f"run tier_by_numbers {tier_run!r} is not the tier of its weighted IRR ({tier_irr!r})")
    if scored.get("tier_by_numbers") != tier_run:
        mm.append(f"tier_by_numbers {scored.get('tier_by_numbers')!r} vs run {tier_run!r}")
    if not _same(scored.get("implied_irr"), numbers.get("implied_irr_weighted"), 0.5e-4 + 1e-9):
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


def reprice(numbers, price, price_date=None, scored=None, today=None, prices=None, fund=None):
    """Pure function: the live.json payload for a recorded run at `price`.
    `scored` is the folder's score.json (for tier_final) when available.
    `prices` is the folder's prices.json: when given, the run's per-share
    basis is checked against it (check_basis) and a split since scoring is
    divided out of every per-share value; `fund` (fundamentals.json) only
    adds the SEC's split record to that evidence. Without `prices` the basis
    is "unchecked" (factor 1); reprice_folder always passes it.
    Raises Skip when the run is not eligible, its per-share basis cannot be
    verified, or its paths cannot be replayed."""
    check_eligible(numbers)
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

    scenarios = {}
    for k in LABELS:
        irr, capped, floor = E.solve_irr(paths[k], price, gterm)
        scenarios[k] = {"irr": irr, "tier": E.tier_for_irr(irr), "irr_capped": bool(capped), "irr_at_floor": bool(floor)}
    w = paths["weighted"]
    irr_w, w_capped, w_floor = E.solve_irr(w, price, gterm)
    tier_numbers = E.tier_for_irr(irr_w)

    # Intrinsic values do not depend on the price: copy the run's own figures;
    # a pre-5.4 run never stored the 20 / 25% hurdle prices, so replay those
    # on the same weighted path (present_value is the engine's own function).
    # The recorded ones are per scored-run share: divided by the split factor.
    def iv(rate_key, rate):
        v = _f(w_rec.get(rate_key))
        if v is None:
            v = _f(numbers.get(rate_key))
        return v / factor if v is not None else E.present_value(w, rate, gterm)
    iv15, iv12, iv20, iv25 = iv("iv_at_15", 0.15), iv("iv_at_12", 0.12), iv("iv_at_20", 0.20), iv("iv_at_25", 0.25)

    shares = _f(numbers.get("shares_diluted_latest"))
    mcap = price * shares * factor if shares else None
    scored_price = _f(numbers.get("price"))
    if scored_price is not None:
        scored_price /= factor  # in today's share units, like `price`
    scored_irr = _f(numbers.get("implied_irr_weighted"))
    scored_tier = numbers.get("tier_by_numbers")
    # The agent's override (tier_final != tier_by_numbers, reason in analysis.md)
    # is a judgment on the business, not on the price: keep it while the numbers
    # tier is where it was on scoring day; let the live numbers tier through —
    # flagged — only when the price move actually moved the numbers tier.
    # Only a score.json built from THIS run carries this run's judgment: one
    # left over from an earlier engine run (same day or not) is ignored, and
    # its tier_final is unknown for this run, as for an unreadable score.json.
    if isinstance(scored, dict):
        scored_fresh, score_mismatch = score_matches_run(scored, numbers)
    else:
        scored_fresh, score_mismatch = False, []
    scored_final = scored.get("tier_final") if scored_fresh else None
    override_active = bool(scored_fresh and scored_final and scored_tier and scored_final != scored_tier)
    numbers_moved = tier_numbers != scored_tier
    if override_active and not numbers_moved:
        tier, override_superseded = scored_final, False
    else:
        tier, override_superseded = tier_numbers, override_active
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
        "score_json_fresh": scored_fresh if isinstance(scored, dict) else None,
        "score_mismatch": score_mismatch if (isinstance(scored, dict) and not scored_fresh) else None,
        "price_change_pct": (price / scored_price - 1) * 100 if scored_price else None,
        "irr_weighted": irr_w,
        "tier": tier,
        "tier_display": tier,
        "tier_by_numbers": tier_numbers,
        "override_active": override_active,
        "override_superseded": override_superseded,
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
            "tier_final": scored_final,
            "tier_override_reason": (scored or {}).get("tier_override_reason") if (override_active and isinstance(scored, dict)) else None,
            "upside_at_15": _f(numbers.get("upside_at_15")),
        },
        "delta": {
            "irr_pp": (irr_w - scored_irr) * 100 if scored_irr is not None else None,
            "tier_changed": numbers_moved,
            "tier_changed_vs_final": tier != (scored_final or scored_tier),
        },
        "engine_release_of_run": numbers.get("engine_release") or f"pre-5.4 (engine_version {numbers.get('engine_version')})",
        "basis": BASIS,
    }
    if isinstance(scored, dict) and not scored_fresh:
        out["score_note"] = ("score.json is not from this engine run (" + "; ".join(score_mismatch)
                             + ") — tier_final unknown, no override applied; re-run make_score.py")
    return out


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
    (check_basis). An unreadable score.json degrades to scored=None
    (tier_final unknown, override not applied) and is noted in the payload;
    fundamentals.json is optional evidence only."""
    folder = os.path.join(BASE, ticker)
    try:
        np_, pp_ = os.path.join(folder, "dcf_numbers.json"), os.path.join(folder, "prices.json")
        if not os.path.isfile(np_):
            raise Skip("no dcf_numbers.json")
        numbers = _load(np_)
        check_eligible(numbers)
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
        sp = os.path.join(folder, "score.json")
        scored, score_note = None, None
        if os.path.isfile(sp):
            try:
                scored = _load(sp)
                if not isinstance(scored, dict):
                    scored, score_note = None, "score.json is not an object — tier_final unknown"
            except Skip as e:
                score_note = f"{e} — tier_final unknown, no override applied"
        live = reprice(numbers, price, price_date, scored, prices=prices, fund=fund)
        if score_note:
            live["score_note"] = score_note
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
    scored_shown = s["tier_by_numbers"] + (f" (final {s['tier_final']})" if live["override_active"] else "")
    live_shown = live["tier"] + (f" (numbers {live['tier_by_numbers']}, override kept)" if (live["override_active"] and not live["override_superseded"])
                                 else f" (numbers moved from {s['tier_by_numbers']}, override {s['tier_final']} superseded)" if live["override_superseded"] else "")
    return (f"{live['ticker']}: scored ${live['scored_price']:.2f} ({live['scored_date']}) "
            f"{scored_shown} {_pct(s['irr_weighted'])} -> live ${live['price']:.2f} ({live['price_date']}) "
            f"{live_shown} {_pct(live['irr_weighted'])} ({d['irr_pp']:+.2f}pp"
            f"{', TIER CHANGED' if d['tier_changed'] else ''}"
            f"{', at floor' if live['irr_at_floor'] else ''}{', capped' if live['irr_capped'] else ''}"
            f"{(', STALE PRICE (' + str(live['price_age_days']) + ' days old)') if live['stale_price'] else ''}"
            f"{(', SPLIT ' + str(_split_label(live)) + ' since scoring, per-share values restated') if _split_label(live) else ''}"
            f"{', scored session close not posted yet' if _basis_method(live) == 'no_close_since_scoring' else ''}"
            f"{', score.json from another run (no override)' if live.get('score_mismatch') else ''}); "
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


def main():
    argv = sys.argv[1:]
    quiet = "--quiet" in argv
    args = [a for a in argv if not a.startswith("--")]
    if "--all" in argv:
        written, skipped, changed, stale, split, foreign_score = [], [], [], [], [], []
        for t in company_folders():
            try:
                live = reprice_folder(t)
                written.append(t)
                if _split_label(live):
                    split.append(f"{t} {_split_label(live)}")
                if live.get("score_mismatch"):
                    foreign_score.append(t)
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
              + (f"; split since scoring, per-share values restated: {', '.join(split)}" if split else "")
              + (f"; score.json not from the current engine run (no override applied, re-run make_score.py): "
                 f"{', '.join(foreign_score)}" if foreign_score else ""))
        for t, why in skipped:
            print(f"  skipped {t}: {why}")
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
    if not quiet:
        print(json.dumps(live, indent=1))


if __name__ == "__main__":
    main()
