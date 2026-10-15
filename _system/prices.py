#!/usr/bin/env python3
"""Price-history store (v5.4, 2026-10-14; intraday capture 2026-10-15).

Usage: python3 prices.py <TICKER> [--years 10] [--no-write] [--no-intraday] [--quiet]
       python3 prices.py --all [--years 10] [--no-intraday] [--quiet]

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

Intraday (second request per name, after the daily history): the no-dates
chart endpoint returns the current (or, on a weekend / holiday, the last)
session at one-minute resolution from 4:00 AM to 7:59 PM ET. It becomes
  "intraday"    — that session downsampled to 5-minute bars (last price in
                  each bucket; pre-market, regular and after-hours as returned)
                  with prev_close / last / last_time, or null when the chart
                  call failed (the daily series is never lost because of it;
                  a "warnings" entry says why);
  "sessions_5d" — a rolling buffer of the most recent up to five sessions
                  (oldest first, today's included), maintained by reading the
                  existing prices.json before writing: a re-run on the same
                  day REPLACES that day's entry, never duplicates it — unless
                  the entry on disk already reaches a LATER minute of that
                  session (an out-of-order run never shortens a session).
Bars are keyed by the bucket's END minute (right-closed: prints 15:56-16:00
→ 960, so the 16:00 closing print is the regular segment's last bar and the
9:30 opening print sits at 570; 19:56-19:59 → 1200).
prev_close is the filed daily close strictly before session_date (the same
series stats.prev_close uses) — Nasdaq's data.previousClose is only used
when no earlier daily row exists, because before the regular open it still
holds the close of TWO sessions ago (verified 2026-10-15 08:40 ET: session
10-15, previousClose = the 10-13 close). A disagreement is recorded in
`warnings`; the raw value is kept as prev_close_nasdaq.
Every session carries captured_at (ET) and complete (true when the last
1-minute print is at or after 19:55 ET, or the capture happened at or after
20:00 ET of the session date — the endpoint keeps serving the finished
session until the next pre-market, observed until 02:07 ET). A session
captured during the day stays partial until a later run the SAME day
(the endpoint moves on the next morning), so one run after 20:00 ET is the
only way to a complete day. `close` is the official regular-session close:
the daily row for session_date when it exists, else data.lastSalePrice once
the session is past 16:00 (verified HBAN 2026-10-14: lastSalePrice 15.10 =
the daily close while the 19:58 after-hours print was 15.11), else null.
The chart's `x` is the ET wall-clock encoded as if it were UTC (verified
2026-10-14: x=1791950400000 is labelled "4:00 AM ET"); decode_point() checks
each point's label against both that convention and a true epoch, so a
format change on Nasdaq's side cannot silently shift the bars.

--all          refresh every folder that has a score.json, sequentially with a 0.3 s
               pause between names; a failure is reported and the sweep continues;
               one summary line at the end (exit 1 if any name failed).
--no-intraday  skip the chart request; the previous file's intraday /
               sessions_5d are carried over unchanged (noted in warnings).
--quiet        print no per-name JSON (failures still go to stderr).
"""
import json, sys, os, datetime, time, urllib.request
from zoneinfo import ZoneInfo

BASE = os.environ.get("STOCKS_BASE") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UA = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
ALL_SLEEP_S = 0.3
INTRADAY_PAUSE_S = 0.1          # between the two requests of one name (10 req/s ceiling)
ET = ZoneInfo("America/New_York")
BAR_MINUTES = 5
SESSIONS_KEEP = 5
INTRADAY_SOURCE = "api.nasdaq.com chart (no dates)"
BAR_KEY = "end"                 # bars are keyed by the bucket's END minute (right-closed)
REGULAR_CLOSE_MIN = 16 * 60     # 960
SESSION_LAST_BAR_MIN = 19 * 60 + 55   # 1195: a session whose last print is here or later is complete
SESSION_OVER_MIN = 20 * 60      # 1200: after 20:00 ET the served session is finished whatever its last print


def now_et():
    """The sweep's clock (ET, second precision). Tests replace it."""
    return datetime.datetime.now(ET).replace(microsecond=0)


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
    today = datetime.datetime.now(ET).date()  # Codex review of PR #2: the VM runs UTC
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


def _row_before(daily, date_iso):
    """The last (date, close) in the daily series dated STRICTLY before date_iso, or None."""
    best = None
    for dt, c, _ in daily:
        if dt < date_iso:
            best = (dt, c)
        else:
            break
    return best


def _close_on(daily, date_iso):
    for dt, c, _ in daily:
        if dt == date_iso:
            return c
    return None


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


# ---------------------------------------------------------------- intraday

def ms_to_et(ms):
    """A TRUE ms epoch → (ET date iso, minutes since ET midnight). DST-aware."""
    dt = datetime.datetime.fromtimestamp(ms / 1000.0, datetime.timezone.utc).astimezone(ET)
    return dt.date().isoformat(), dt.hour * 60 + dt.minute


def ms_as_wallclock(ms):
    """Nasdaq's chart convention: `x` is the ET wall-clock encoded as if it were
    UTC (x=1791950400000 ↔ "4:00 AM ET"). Read the UTC fields as ET directly."""
    dt = datetime.datetime.fromtimestamp(ms / 1000.0, datetime.timezone.utc)
    return dt.date().isoformat(), dt.hour * 60 + dt.minute


def label_minutes(label):
    """'4:00 AM ET' / '7:59 PM ET' / '16:00' → minutes since midnight, else None."""
    if not isinstance(label, str):
        return None
    s = label.upper().replace("ET", "").strip()
    for fmt in ("%I:%M %p", "%H:%M"):
        try:
            t = datetime.datetime.strptime(s, fmt)
            return t.hour * 60 + t.minute
        except ValueError:
            continue
    return None


def decode_point(p):
    """One chart point → (date iso, minutes since ET midnight, price) or None.
    The z.dateTime label is the ground truth for the minute: whichever reading
    of `x` (wall-clock-as-UTC first, then true epoch) agrees with it wins; with
    no label the wall-clock convention is assumed; with a label that matches
    neither, the label's minute is kept with the wall-clock date."""
    if not isinstance(p, dict):
        return None
    z = p.get("z") if isinstance(p.get("z"), dict) else {}
    price = p.get("y")
    price = float(price) if isinstance(price, (int, float)) else _num(z.get("value"))
    if price is None or price <= 0:
        return None
    x = p.get("x")
    if not isinstance(x, (int, float)):
        return None
    lm = label_minutes(z.get("dateTime"))
    cands = [ms_as_wallclock(x), ms_to_et(x)]
    for d, m in cands:
        if lm is None or m == lm:
            return d, m, price
    return cands[0][0], lm, price


def minutes_hhmm(m):
    return f"{m // 60:02d}:{m % 60:02d}"


def downsample(points, step=BAR_MINUTES):
    """[(minutes, price), ...] → [[bucket_END_minutes, last price in bucket], ...]
    in time order, no empty buckets. Buckets are right-closed and keyed by
    their end: minutes 956-960 → 960 (so the 16:00 closing print is the last
    bar of the regular segment), 961-965 → 965, 926-930 → 570 (the 9:30
    opening print), 236-240 → 240. The last point of a bucket (input order)
    wins, so callers pass points in time order."""
    buckets = {}
    for m, price in points:
        buckets[-(-int(m) // step) * step] = price
    return [[k, round(v, 4)] for k, v in sorted(buckets.items())]


def session_complete(last_minute, captured_at, session_date):
    """True when the session the endpoint served is over: its last 1-minute
    print is at/after 19:55 ET, or the capture happened at/after 20:00 ET of
    session_date (the endpoint keeps serving the finished session until the
    next pre-market). captured_at is an aware datetime or an ISO string."""
    if isinstance(last_minute, (int, float)) and last_minute >= SESSION_LAST_BAR_MIN:
        return True
    if isinstance(captured_at, str):
        try:
            captured_at = datetime.datetime.fromisoformat(captured_at)
        except ValueError:
            return False
    if not isinstance(captured_at, datetime.datetime) or not isinstance(session_date, str):
        return False
    try:
        if captured_at.tzinfo is not None:
            captured_at = captured_at.astimezone(ET)
        sd = datetime.date.fromisoformat(session_date)
    except ValueError:
        return False
    cd = captured_at.date()
    return cd > sd or (cd == sd and captured_at.hour * 60 + captured_at.minute >= SESSION_OVER_MIN)


def parse_chart(payload, captured_at=None):
    """The no-dates chart payload → the `intraday` block. Raises ValueError when
    the payload carries no usable points (the caller turns that into a warning).
    prev_close here is Nasdaq's previousClose; run_one reconciles it against the
    daily series (reconcile_with_daily) because it is stale before the open."""
    data = (payload or {}).get("data") if isinstance(payload, dict) else None
    data = data if isinstance(data, dict) else {}
    pts = [q for q in (decode_point(p) for p in (data.get("chart") or [])) if q]
    if not pts:
        raise ValueError("chart returned no usable points")
    pts.sort(key=lambda q: (q[0], q[1]))
    dates = {}
    for d, _, _ in pts:
        dates[d] = dates.get(d, 0) + 1
    session_date = max(dates.items(), key=lambda kv: (kv[1], kv[0]))[0]  # the day with the most points
    day = [(m, price) for d, m, price in pts if d == session_date]
    last_m, last_p = day[-1]
    captured_at = captured_at or now_et()
    captured_iso = captured_at.isoformat() if isinstance(captured_at, datetime.datetime) else str(captured_at)
    complete = session_complete(last_m, captured_at, session_date)
    last_sale = _num(data.get("lastSalePrice"))
    nasdaq_prev = _num(data.get("previousClose"))
    # lastSalePrice is the official last sale: during the session it is the live
    # print (pre-market included), after 16:00 it is the regular-session close.
    past_close = last_m >= REGULAR_CLOSE_MIN or complete
    return {"session_date": session_date, "tz": "America/New_York",
            "regular_open": "09:30", "regular_close": "16:00",
            "prev_close": nasdaq_prev, "prev_close_source": "nasdaq" if nasdaq_prev is not None else None,
            "prev_close_nasdaq": nasdaq_prev,
            "close": last_sale if past_close else None, "close_source": "nasdaq lastSalePrice" if past_close and last_sale is not None else None,
            "last": round(last_p, 4), "last_time": minutes_hhmm(last_m), "last_minute": last_m,
            "last_sale": last_sale,
            "time_as_of": data.get("timeAsOf") if isinstance(data.get("timeAsOf"), str) else None,
            "captured_at": captured_iso, "complete": complete,
            "points": len(day),
            "bars": downsample(day), "bar_key": BAR_KEY,
            "source": INTRADAY_SOURCE}


def reconcile_with_daily(intra, daily, tol=0.005):
    """Set prev_close / close from the filed daily series (the same closes
    stats uses) and return a list of warnings. prev_close = the daily close
    strictly before session_date when one exists (Nasdaq's previousClose is
    stale before the open); close = the daily close ON session_date when the
    series already has that row (else the lastSalePrice rule from parse_chart).
    Plain lookups on filed values; nothing estimated."""
    warnings = []
    daily = daily or []
    before = _row_before(daily, intra["session_date"])
    nas = intra.get("prev_close_nasdaq")
    if before is not None:
        dt, c = before
        intra["prev_close"], intra["prev_close_source"] = round(c, 4), f"daily close {dt}"
        if nas is not None and abs(nas - c) > tol:
            warnings.append(f"prev_close: Nasdaq previousClose {nas} differs from the daily close {round(c, 4)} "
                            f"({dt}) before session {intra['session_date']}; daily used")
    elif nas is not None:
        warnings.append(f"prev_close: no daily close before session {intra['session_date']}; Nasdaq previousClose {nas} used")
    on = _close_on(daily, intra["session_date"])
    if on is not None:
        if intra.get("close") is not None and abs(intra["close"] - on) > tol:
            warnings.append(f"close: Nasdaq lastSalePrice {intra['close']} differs from the daily close {round(on, 4)} "
                            f"on {intra['session_date']}; daily used")
        intra["close"], intra["close_source"] = round(on, 4), "daily close"
    return warnings


def fetch_intraday(ticker):
    url = f"https://api.nasdaq.com/api/quote/{ticker}/chart?assetclass=stocks"
    return parse_chart(get_json(url))


def session_entry(intraday):
    return {"session_date": intraday["session_date"], "prev_close": intraday.get("prev_close"),
            "close": intraday.get("close"), "captured_at": intraday.get("captured_at"),
            "complete": bool(intraday.get("complete")), "bar_key": intraday.get("bar_key") or BAR_KEY,
            "bars": intraday["bars"]}


def _last_bar_minute(entry):
    bars = [b for b in (entry.get("bars") or []) if isinstance(b, list) and b and isinstance(b[0], (int, float))]
    return max((b[0] for b in bars), default=-1)


def clean_sessions(existing, keep=SESSIONS_KEEP):
    """Well-formed entries of an existing sessions_5d, oldest first, newest `keep`.
    An entry written before 2026-10-15 (no `complete`) gets the flag derived from
    its own bars (last bar at/after 19:55); its bars stay as written."""
    rows = [s for s in (existing or []) if isinstance(s, dict) and isinstance(s.get("session_date"), str)
            and s["session_date"] and isinstance(s.get("bars"), list)]
    for s in rows:
        if not isinstance(s.get("complete"), bool):
            s["complete"] = _last_bar_minute(s) >= SESSION_LAST_BAR_MIN
    rows.sort(key=lambda s: s["session_date"])
    return rows[-keep:]


def merge_sessions(existing, entry, keep=SESSIONS_KEEP):
    """Rolling buffer: replace the existing entry for the same session_date with
    the new one, sort oldest first, keep the newest `keep`. Malformed existing
    entries are dropped. Guard: an existing same-day entry is KEPT when it
    already reaches a later minute of the session than the new one, or the
    same minute with more bars (a later capture of one session is a superset,
    so an out-of-order or late partial run never shortens a stored session)."""
    rows = clean_sessions(existing, keep=10 ** 6)
    same = [s for s in rows if s["session_date"] == entry["session_date"]]
    rows = [s for s in rows if s["session_date"] != entry["session_date"]]
    keep_old = None
    for s in same:
        om, nm = _last_bar_minute(s), _last_bar_minute(entry)
        if om > nm or (om == nm and len(s["bars"]) > len(entry["bars"])):
            keep_old = s if keep_old is None or _last_bar_minute(s) > _last_bar_minute(keep_old) else keep_old
    rows.append(keep_old if keep_old is not None else entry)
    rows.sort(key=lambda s: s["session_date"])
    return rows[-keep:]


def backfill_closes(sessions, daily):
    """Give every stored session whose `close` is missing the filed daily close
    for its date when the daily series has that row (a plain lookup: the entry
    captured before the day's close, or written before `close` existed, gets
    the official close once the historical endpoint carries the day)."""
    for s in sessions or []:
        if not isinstance(s.get("close"), (int, float)):
            c = _close_on(daily, s["session_date"])
            if c is not None:
                s["close"], s["close_source"] = round(c, 4), "daily close"
    return sessions


def read_existing(folder):
    try:
        with open(f"{folder}/prices.json", encoding="utf-8") as f:
            d = json.load(f)
        return d if isinstance(d, dict) else {}
    except Exception:
        return {}


def run_one(ticker, years=10, write=True, quiet=False, intraday=True):
    """Fetch + write one ticker. Returns the payload (daily/weekly/monthly
    included). Raises on a daily fetch failure; raises ValueError when the API
    returns no rows. An intraday failure never raises: intraday is null and
    `warnings` says why."""
    daily = fetch_daily(ticker, years)
    if not daily:
        raise ValueError(f"no price rows returned for {ticker}")
    today = daily[-1][0]
    one_year_ago = (datetime.date.fromisoformat(today) - datetime.timedelta(days=370)).isoformat()
    # fetched_at: when THIS file was pulled (ET, the sweep's clock), distinct from
    # as_of = the last close in it. reprice.py compares fetched_at with the scored
    # run's as_of to refuse a file the daily refresh failed to update.
    fetched_at = now_et().isoformat()
    out = {"ticker": ticker, "source": "Nasdaq historical quotes API (api.nasdaq.com)", "currency": "USD",
           "as_of": today, "fetched_at": fetched_at, "first_date": daily[0][0], "rows": len(daily),
           "daily_1y": [[dt, round(c, 2)] for dt, c, _ in daily if dt >= one_year_ago],
           "weekly": _last_per_bucket(daily, lambda dt: datetime.date.fromisoformat(dt).isocalendar()[:2]),
           "monthly": _last_per_bucket(daily, lambda dt: dt[:7]),
           "stats": stats(daily)}
    folder = f"{BASE}/{ticker}"
    prev = read_existing(folder)
    prev_sessions = prev.get("sessions_5d") if isinstance(prev.get("sessions_5d"), list) else []
    warnings = []
    if intraday:
        time.sleep(INTRADAY_PAUSE_S)
        try:
            intra = fetch_intraday(ticker)
            warnings.extend(reconcile_with_daily(intra, daily))
            sessions = merge_sessions(prev_sessions, session_entry(intra))
            kept = next((s for s in sessions if s["session_date"] == intra["session_date"]), None)
            if kept is not None and kept.get("captured_at") != intra["captured_at"]:
                warnings.append(f"sessions_5d: the stored {intra['session_date']} entry (captured {kept.get('captured_at')}, "
                                f"last bar {minutes_hhmm(int(_last_bar_minute(kept)))}) reaches further than this capture "
                                f"(last bar {intra['last_time']}); stored entry kept")
        except Exception as e:
            intra, sessions = None, clean_sessions(prev_sessions)
            warnings.append(f"intraday: chart request failed - {type(e).__name__}: {e}; daily series kept, "
                            f"sessions_5d carried over from the previous file")  # ASCII: Windows consoles
    else:
        intra = prev.get("intraday") if isinstance(prev.get("intraday"), dict) else None
        sessions = clean_sessions(prev_sessions)
        warnings.append("intraday: skipped (--no-intraday); intraday and sessions_5d carried over from the previous file")
    out["intraday"], out["sessions_5d"], out["warnings"] = intra, backfill_closes(sessions, daily), warnings
    if write:
        os.makedirs(folder, exist_ok=True)
        tmp = f"{folder}/prices.json.tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(out, f, separators=(",", ":"))
        os.replace(tmp, f"{folder}/prices.json")  # atomic: a reader never sees a half-written file
    if not quiet:
        show = {k: v for k, v in out.items() if k not in ("daily_1y", "weekly", "monthly", "sessions_5d", "intraday")}
        show["intraday"] = {k: v for k, v in intra.items() if k != "bars"} | {"bars": len(intra["bars"])} if intra else None
        show["sessions_5d"] = [s["session_date"] for s in sessions]
        print(json.dumps(show, indent=1))
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
    intraday = "--no-intraday" not in argv
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
                out = run_one(t, years, write, quiet, intraday)
                ok.append(t)
                for w in out.get("warnings") or []:
                    print(f"prices.py: {t} warning - {w}", file=sys.stderr)
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
        out = run_one(ticker, years, write, quiet, intraday)
        for w in out.get("warnings") or []:
            print(f"prices.py: {ticker} warning - {w}", file=sys.stderr)
    except ValueError as e:
        print(f"prices.py: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
