#!/usr/bin/env python3
"""Price-history store (v5.4, 2026-10-14).

Usage: python3 prices.py <TICKER> [--years 10] [--no-write] [--quiet]
       python3 prices.py --all [--years 10] [--quiet]

Pulls up to ten years of daily closes from the Nasdaq historical-quotes API —
the same source the engine already uses for the spot price — and writes
<TICKER>/prices.json: a compact daily series for the last year, a weekly
series (last close of each week) for the full window, a monthly series, and
a few return / drawdown statistics computed from those closes. The company
page draws its price-vs-value chart from this file and reprice.py reads
stats.last / stats.last_date as the live price (and `fetched_at`, the ET
time this file was pulled, to refuse a file the daily refresh failed to
update); nothing in the valuation reads it. Failures exit non-zero and write nothing (the page degrades to the
value-only view). Exit 2 = no rows returned.

--all   refresh every folder that has a score.json, sequentially with a 0.3 s
        pause between names; a failure is reported and the sweep continues;
        one summary line at the end (exit 1 if any name failed).
--quiet print no per-name JSON (failures still go to stderr).
"""
import json, sys, os, datetime, time, urllib.request
from zoneinfo import ZoneInfo

BASE = os.environ.get("STOCKS_BASE") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UA = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
ALL_SLEEP_S = 0.3


def get_json(url, timeout=40):
    last = None
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read())
        except Exception as e:
            last = e
            if attempt < 2:
                time.sleep(2 ** attempt)
    raise last


def _num(s):
    try:
        return float(str(s).replace("$", "").replace(",", "").strip())
    except Exception:
        return None


def fetch_daily(ticker, years):
    today = datetime.datetime.now(ZoneInfo("America/New_York")).date()  # Codex review of PR #2: the VM runs UTC
    frm = today - datetime.timedelta(days=int(years * 365.25) + 7)
    url = (f"https://api.nasdaq.com/api/quote/{ticker}/historical?assetclass=stocks"
           f"&fromdate={frm.isoformat()}&todate={today.isoformat()}&limit=9999")
    d = get_json(url)
    rows = (((d or {}).get("data") or {}).get("tradesTable") or {}).get("rows") or []
    out = []
    for r in rows:
        try:
            dt = datetime.datetime.strptime(r["date"], "%m/%d/%Y").date().isoformat()
        except Exception:
            continue
        c = _num(r.get("close"))
        if c is None or c <= 0:
            continue
        out.append((dt, c, _num(r.get("volume"))))
    out.sort()
    return out


def _last_per_bucket(daily, keyfn):
    buckets = {}
    for dt, c, _ in daily:
        buckets[keyfn(dt)] = (dt, c)  # ascending order → last trading day wins
    return [[dt, round(c, 2)] for _, (dt, c) in sorted(buckets.items())]


def _close_at_or_before(daily, target):
    best = None
    for dt, c, _ in daily:
        if dt <= target:
            best = c
        else:
            break
    return best


def stats(daily):
    if not daily:
        return {}
    last_dt, last_c, _ = daily[-1]
    today = datetime.date.fromisoformat(last_dt)
    out = {"last_date": last_dt, "last": round(last_c, 2)}
    if len(daily) >= 2:
        prev = daily[-2][1]
        out["prev_close"] = round(prev, 2)
        out["change_1d_pct"] = round((last_c / prev - 1) * 100, 2) if prev else None
    yr = [c for dt, c, _ in daily if dt >= (today - datetime.timedelta(days=365)).isoformat()]
    if yr:
        out["high_52w"], out["low_52w"] = round(max(yr), 2), round(min(yr), 2)
    for label, days in (("1m", 30), ("3m", 91), ("6m", 182), ("1y", 365), ("3y", 1096), ("5y", 1826), ("10y", 3652)):
        ref = _close_at_or_before(daily, (today - datetime.timedelta(days=days)).isoformat())
        first_dt = daily[0][0]
        if ref and first_dt <= (today - datetime.timedelta(days=days - 10)).isoformat():
            out[f"ret_{label}_pct"] = round((last_c / ref - 1) * 100, 2)
    ytd_ref = _close_at_or_before(daily, f"{today.year - 1}-12-31")
    if ytd_ref:
        out["ret_ytd_pct"] = round((last_c / ytd_ref - 1) * 100, 2)
    # max drawdown over the last 5 years
    five = [c for dt, c, _ in daily if dt >= (today - datetime.timedelta(days=1826)).isoformat()]
    peak, mdd = None, 0.0
    for c in five:
        peak = c if peak is None or c > peak else peak
        mdd = min(mdd, c / peak - 1)
    out["max_drawdown_5y_pct"] = round(mdd * 100, 2)
    first_dt, first_c, _ = daily[0]
    yrs = (today - datetime.date.fromisoformat(first_dt)).days / 365.25
    if yrs >= 1 and first_c > 0:
        out["cagr_window_pct"] = round(((last_c / first_c) ** (1 / yrs) - 1) * 100, 2)
        out["window_years"] = round(yrs, 1)
    return out


def run_one(ticker, years=10, write=True, quiet=False):
    """Fetch + write one ticker. Returns the payload (daily/weekly/monthly
    included). Raises on a fetch failure; raises ValueError when the API
    returns no rows."""
    daily = fetch_daily(ticker, years)
    if not daily:
        raise ValueError(f"no price rows returned for {ticker}")
    today = daily[-1][0]
    one_year_ago = (datetime.date.fromisoformat(today) - datetime.timedelta(days=370)).isoformat()
    # fetched_at: when THIS file was pulled (ET, the sweep's clock), distinct from
    # as_of = the last close in it. reprice.py compares fetched_at with the scored
    # run's as_of to refuse a file the daily refresh failed to update.
    fetched_at = datetime.datetime.now(ZoneInfo("America/New_York")).replace(microsecond=0).isoformat()
    out = {"ticker": ticker, "source": "Nasdaq historical quotes API (api.nasdaq.com)", "currency": "USD",
           "as_of": today, "fetched_at": fetched_at, "first_date": daily[0][0], "rows": len(daily),
           "daily_1y": [[dt, round(c, 2)] for dt, c, _ in daily if dt >= one_year_ago],
           "weekly": _last_per_bucket(daily, lambda dt: datetime.date.fromisoformat(dt).isocalendar()[:2]),
           "monthly": _last_per_bucket(daily, lambda dt: dt[:7]),
           "stats": stats(daily)}
    if write:
        folder = f"{BASE}/{ticker}"
        os.makedirs(folder, exist_ok=True)
        tmp = f"{folder}/prices.json.tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(out, f, separators=(",", ":"))
        os.replace(tmp, f"{folder}/prices.json")  # atomic: a reader never sees a half-written file
    if not quiet:
        print(json.dumps({k: v for k, v in out.items() if k not in ("daily_1y", "weekly", "monthly")}, indent=1))
    return out


def scored_tickers():
    """Every company folder with a score.json, sorted (system folders excluded)."""
    out = []
    for name in sorted(os.listdir(BASE)):
        if name.startswith(("_", ".")):
            continue
        if os.path.isfile(os.path.join(BASE, name, "score.json")):
            out.append(name)
    return out


def main():
    argv = sys.argv[1:]
    quiet, do_all = "--quiet" in argv, "--all" in argv
    years = float(argv[argv.index("--years") + 1]) if "--years" in argv else 10
    write = "--no-write" not in argv
    args = [a for i, a in enumerate(argv) if not a.startswith("--") and (i == 0 or argv[i - 1] != "--years")]
    if do_all:
        tickers = scored_tickers()
        ok, failed = [], []
        for i, t in enumerate(tickers):
            if i:
                time.sleep(ALL_SLEEP_S)
            try:
                out = run_one(t, years, write, quiet)
                ok.append(t)
            except Exception as e:
                failed.append(t)
                print(f"prices.py: {t} FAILED — {type(e).__name__}: {e}", file=sys.stderr)
        print(f"prices.py --all: {len(ok)}/{len(tickers)} updated, {len(failed)} failed"
              + (f" ({', '.join(failed)})" if failed else ""))
        sys.exit(1 if failed else 0)
    if not args:
        print(__doc__); sys.exit(2)
    ticker = args[0].upper()
    try:
        run_one(ticker, years, write, quiet)
    except ValueError as e:
        print(f"prices.py: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
