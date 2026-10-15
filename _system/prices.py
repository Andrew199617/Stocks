#!/usr/bin/env python3
"""Price-history store (v5.4, 2026-10-14).

Usage: python3 prices.py <TICKER> [--years 10] [--no-write]

Pulls up to ten years of daily closes from the Nasdaq historical-quotes API —
the same source the engine already uses for the spot price — and writes
<TICKER>/prices.json: a compact daily series for the last year, a weekly
series (last close of each week) for the full window, a monthly series, and
a few return / drawdown statistics computed from those closes. The company
page draws its price-vs-value chart from this file; nothing in the valuation
reads it. Failures exit non-zero and write nothing (the page degrades to the
value-only view). Exit 2 = no rows returned.
"""
import json, sys, os, datetime, time, urllib.request

BASE = os.environ.get("STOCKS_BASE") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UA = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}


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
    today = datetime.date.today()
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


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__); sys.exit(2)
    ticker = args[0].upper()
    years = float(sys.argv[sys.argv.index("--years") + 1]) if "--years" in sys.argv else 10
    daily = fetch_daily(ticker, years)
    if not daily:
        print(f"prices.py: no price rows returned for {ticker}", file=sys.stderr)
        sys.exit(2)
    today = daily[-1][0]
    one_year_ago = (datetime.date.fromisoformat(today) - datetime.timedelta(days=370)).isoformat()
    out = {"ticker": ticker, "source": "Nasdaq historical quotes API (api.nasdaq.com)", "currency": "USD",
           "as_of": today, "first_date": daily[0][0], "rows": len(daily),
           "daily_1y": [[dt, round(c, 2)] for dt, c, _ in daily if dt >= one_year_ago],
           "weekly": _last_per_bucket(daily, lambda dt: datetime.date.fromisoformat(dt).isocalendar()[:2]),
           "monthly": _last_per_bucket(daily, lambda dt: dt[:7]),
           "stats": stats(daily)}
    if "--no-write" not in sys.argv:
        folder = f"{BASE}/{ticker}"
        os.makedirs(folder, exist_ok=True)
        with open(f"{folder}/prices.json", "w", encoding="utf-8") as f:
            json.dump(out, f, separators=(",", ":"))
    print(json.dumps({k: v for k, v in out.items() if k not in ("daily_1y", "weekly", "monthly")}, indent=1))


if __name__ == "__main__":
    main()
