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
Everything else (Tier F, data gap, pre-v5 or pre-stamp runs without inputs,
no / stale / foreign / unreadable prices.json, unreadable dcf_numbers.json):
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

Exit codes: 0 written; 2 usage; 3 single ticker skipped (reason printed).
--all exits 0 whenever the sweep itself completes.
"""
import json, os, sys, datetime
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.environ.get("STOCKS_BASE") or os.path.dirname(HERE)
sys.path.insert(0, HERE)
import dcf_engine as E  # noqa: E402

LABELS = ["super_bear", "bear", "base", "bull", "super_bull"]
PRICE_SOURCE = "prices.json (Nasdaq last close)"
BASIS = ("same base OE/share, scenario paths and probabilities as the scored run; only the price moved; "
         "an agent tier override (score.json tier_final) is preserved in `tier` unless the numbers tier itself moved")
STALE_DAYS = 4  # a prices.json without fetched_at: last_date may trail as_of by a weekend + holiday, never more


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


def reprice(numbers, price, price_date=None, scored=None, today=None):
    """Pure function: the live.json payload for a recorded run at `price`.
    `scored` is the folder's score.json (for tier_final) when available.
    Raises Skip when the run is not eligible or its paths cannot be replayed."""
    check_eligible(numbers)
    paths, _ = E.replay_paths(numbers)
    if not paths or any(k not in paths for k in LABELS + ["weighted"]):
        raise Skip("scenario paths could not be replayed from the recorded inputs")
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
    def iv(rate_key, rate):
        v = _f(w_rec.get(rate_key))
        if v is None:
            v = _f(numbers.get(rate_key))
        return v if v is not None else E.present_value(w, rate, gterm)
    iv15, iv12, iv20, iv25 = iv("iv_at_15", 0.15), iv("iv_at_12", 0.12), iv("iv_at_20", 0.20), iv("iv_at_25", 0.25)

    shares = _f(numbers.get("shares_diluted_latest"))
    mcap = price * shares if shares else None
    scored_price = _f(numbers.get("price"))
    scored_irr = _f(numbers.get("implied_irr_weighted"))
    scored_tier = numbers.get("tier_by_numbers")
    scored_final = (scored or {}).get("tier_final") if isinstance(scored, dict) else None
    # The agent's override (tier_final != tier_by_numbers, reason in analysis.md)
    # is a judgment on the business, not on the price: keep it while the numbers
    # tier is where it was on scoring day; let the live numbers tier through —
    # flagged — only when the price move actually moved the numbers tier.
    # Re-verification finding: a score.json left over from an EARLIER engine run
    # is not evidence of an override on this run. make_score.py copies the
    # engine's as_of into analysis_date, so a fresh score carries the same
    # date as dcf_numbers.json; anything else is stale and ignored here.
    scored_fresh = bool(isinstance(scored, dict) and scored.get("analysis_date")
                        and scored.get("analysis_date") == numbers.get("as_of"))
    override_active = bool(scored_fresh and scored_final and scored_tier and scored_final != scored_tier)
    numbers_moved = tier_numbers != scored_tier
    if override_active and not numbers_moved:
        tier, override_superseded = scored_final, False
    else:
        tier, override_superseded = tier_numbers, override_active
    tz_today = today or datetime.datetime.now(ZoneInfo("America/New_York")).date().isoformat()
    # The close is never older than the scored price (live_price enforces that),
    # but a refresh that keeps failing leaves it old against TODAY: say so, so
    # the page can mark it and --all keeps it out of the tier-change summary.
    age = (_date(tz_today) - _date(price_date)).days if (_date(tz_today) and _date(price_date)) else None
    irrs = [s["irr"] for s in scenarios.values()]
    return {
        "ticker": numbers.get("ticker"),
        "as_of": tz_today,
        "price": price,
        "price_date": price_date,
        "price_source": PRICE_SOURCE,
        "price_age_days": age,
        "stale_price": (age > STALE_DAYS) if age is not None else None,
        "scored_price": scored_price,
        "scored_date": numbers.get("as_of"),
        "score_json_fresh": scored_fresh if isinstance(scored, dict) else None,
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
    stale. An unreadable score.json degrades to scored=None (tier_final
    unknown, override not applied) and is noted in the payload."""
    folder = os.path.join(BASE, ticker)
    try:
        np_, pp_ = os.path.join(folder, "dcf_numbers.json"), os.path.join(folder, "prices.json")
        if not os.path.isfile(np_):
            raise Skip("no dcf_numbers.json")
        numbers = _load(np_)
        check_eligible(numbers)
        if not os.path.isfile(pp_):
            raise Skip("no prices.json — run prices.py first")
        price, price_date = live_price(_load(pp_), ticker, numbers.get("as_of"))
        sp = os.path.join(folder, "score.json")
        scored, score_note = None, None
        if os.path.isfile(sp):
            try:
                scored = _load(sp)
                if not isinstance(scored, dict):
                    scored, score_note = None, "score.json is not an object — tier_final unknown"
            except Skip as e:
                score_note = f"{e} — tier_final unknown, no override applied"
        live = reprice(numbers, price, price_date, scored)
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
            f"{(', STALE PRICE (' + str(live['price_age_days']) + ' days old)') if live['stale_price'] else ''}); "
            f"band {live['tier_bear']}->{live['tier_bull']}; IV@15 ${live['iv_at_15']:.2f} ({live['upside_at_15'] * 100:+.1f}%)")


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
        written, skipped, changed, stale = [], [], [], []
        for t in company_folders():
            try:
                live = reprice_folder(t)
                written.append(t)
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
              + (f"; STALE close (> {STALE_DAYS} days old, run prices.py): {', '.join(stale)}" if stale else ""))
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
