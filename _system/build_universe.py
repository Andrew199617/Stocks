#!/usr/bin/env python3
"""
Build the DCF screening universe.

Method (documented, reproducible):
- Source 1: Nasdaq screener download (all US-listed securities, with price + market cap).
- Clean: drop non-operating securities (ETFs, preferreds, notes, warrants, rights, units, grantor/unit trusts).
- Rank by market cap descending and take the top 3,000 = close public approximation of the Russell 3000
  (Russell 3000 = 3,000 largest eligible US companies; the official constituent list is licensed and
  iShares blocks automated download, so this ranking is the free reproducible equivalent).
- Filter: market cap < $40B (Andrew's cutoff, 2026-10-12).
- Attach SEC CIK from SEC company_tickers_exchange.json so each company can be pulled from EDGAR.
- Queue order: Andrew's watchlist first, then descending market cap (largest under-$40B first).
Outputs: universe.csv, queue.json (with status per ticker), universe_notes.md

A rebuild keeps the queue's progress (2026-10-16): every ticker still in the
universe keeps its queue.json entry dict verbatim — status, claimed_at (pass
2's scoring generation), completed, note, v5_rerun, started, blocked_date,
last_done, refresh_reason (WORKER_SPEC step 2's re-score path keys on it),
refresh_date and any field added later; only the list order and its
queue_pos change. A ticker new to the universe gets
{ticker, queue_pos, status: "pending"}; one that left it is dropped. The
read-merge-write runs under queue.py's lock (<queue.json>.lock), so it cannot
interleave with a claim or done, and the file is swapped in atomically (the
swap retried on a Windows PermissionError). An unreadable queue.json stops
the rebuild instead of resetting every name to pending. Before this,
a rebuild kept only ticker, queue_pos and status.
"""
import json, csv, re, sys, os, datetime, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _lock import locked  # noqa: E402  (queue.py's lock: one queue.json writer at a time)
from _stable import _replace  # noqa: E402  (os.replace, retried on a Windows PermissionError)

BASE = os.environ.get("STOCKS_SYS") or HERE
def _load_watchlist():
    """v5.4: the canonical watchlist lives in _system/watchlist.json (Andrew edits it or
    asks Muse to); the old hard-coded list is the fallback."""
    try:
        return [x["ticker"].upper() for x in json.load(open(f"{BASE}/watchlist.json", encoding="utf-8"))["tickers"]]
    except Exception:
        return ["U","META","NFLX","RDDT","CMPS","ADBE","MSFT","AMZN","APP","LFTO","NTDOY","SONY","SNAP","GOOGL","DUOL","SE","NVO","TTWO","OTLY","STZ","INTC","DFTX","XIACY","FIG"]
WATCHLIST = _load_watchlist()

def merge_queue(old_entries, tickers):
    """The rebuilt queue list, one entry per ticker in universe order: a
    surviving ticker keeps its old entry dict verbatim except queue_pos (its
    new position); a new ticker gets {ticker, queue_pos, status: "pending"};
    a ticker no longer in the universe is dropped."""
    old = {e["ticker"]: e for e in old_entries if isinstance(e, dict) and e.get("ticker")}
    queue = []
    for pos, t in enumerate(tickers, 1):
        if t in old:
            e = dict(old[t])
            e["queue_pos"] = pos
            e.setdefault("status", "pending")  # queue.py needs one; every entry it wrote has it
        else:
            e = {"ticker": t, "queue_pos": pos, "status": "pending"}
        queue.append(e)
    return queue


def write_queue(path, tickers, built, cutoff_b=40):
    """Rebuild queue.json at path for the new universe order, keeping each
    surviving entry (merge_queue), under queue.py's lock with an atomic swap.
    A missing file starts a fresh queue; an unreadable one stops the rebuild
    (SystemExit) and is left as it is. Returns the written object."""
    with locked(f"{path}.lock"):
        try:
            with open(path, encoding="utf-8") as f:
                old = json.load(f)["queue"]
        except FileNotFoundError:
            old = []
        except (OSError, ValueError, KeyError, TypeError) as e:
            raise SystemExit(f"build_universe.py: cannot read {path} ({type(e).__name__}: {e}); "
                             "not rebuilding over it, so no queue progress is lost. Restore it (git) and rerun.")
        data = {"built": built, "cutoff_market_cap_b": cutoff_b, "universe_size": len(tickers),
                "queue": merge_queue(old, tickers)}
        tmp = f"{path}.tmp.{os.getpid()}"
        try:
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=1)
            _replace(tmp, path, attempts=50)
        except BaseException:
            try:
                os.remove(tmp)
            except OSError:
                pass
            raise
    return data


def fetch(url, out, ua="Mozilla/5.0"):
    req = urllib.request.Request(url, headers={"User-Agent": ua})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = r.read()
    open(out, "wb").write(data)
    return data

def is_non_operating(name: str) -> str | None:
    n = name or ""
    nl = n.lower()
    patterns = [
        (r"\betf\b|\betn\b|exchange traded", "etf/etn"),
        (r"preferred|preference shares|depositary shares.*preferred", "preferred"),
        (r"%\s|notes due|senior notes|subordinated notes|baby bonds", "debt security"),
        (r"\bwarrant", "warrant"),
        (r"\bright\b|\brights\b", "right"),
        (r"\bunits?\b", "unit"),
        (r"unit investment trust|grantor trust|royalty trust", "trust vehicle"),
        (r"closed-end|municipal.*fund|bond fund|income fund", "fund"),
    ]
    for pat, why in patterns:
        if re.search(pat, nl):
            return why
    return None

def main():
    fetch("https://api.nasdaq.com/api/screener/stocks?tableonly=true&limit=9999&download=true", f"{BASE}/nasdaq_screener.json")
    fetch("https://www.sec.gov/files/company_tickers_exchange.json", f"{BASE}/sec_tickers_exchange.json", ua="Muse research andrew@example.com")

    rows = json.load(open(f"{BASE}/nasdaq_screener.json", encoding="utf-8"))["data"]["rows"]
    sec = json.load(open(f"{BASE}/sec_tickers_exchange.json", encoding="utf-8"))
    cik_by_ticker = {}
    for rec in sec["data"]:
        cik, name, ticker, exch = rec[0], rec[1], rec[2], rec[3]
        cik_by_ticker.setdefault(ticker.upper(), (cik, name, exch))
    # also handle nasdaq BRK/A style vs SEC BRK-B
    def cik_for(sym):
        for cand in (sym.upper(), sym.upper().replace("/", "-"), sym.upper().replace("/", ".")):
            if cand in cik_by_ticker:
                return cik_by_ticker[cand]
        return (None, None, None)

    def mc(r):
        try: return float(r.get("marketCap") or 0)
        except Exception: return 0.0
    def price(r):
        try: return float((r.get("lastsale") or "").replace("$", "").replace(",", "") or 0)
        except Exception: return 0.0

    clean, dropped = [], []
    for r in rows:
        if mc(r) <= 0: continue
        sym = (r.get("symbol") or "").strip()
        if not sym or "^" in sym: continue
        why = is_non_operating(r.get("name") or "")
        if why: dropped.append((sym, why)); continue
        clean.append(r)
    clean.sort(key=mc, reverse=True)
    top3000 = clean[:3000]
    under = [r for r in top3000 if mc(r) < 40_000_000_000]

    def queue_key(r):
        sym = (r["symbol"] or "").strip().upper()
        wl = WATCHLIST.index(sym) if sym in WATCHLIST else 999
        return (0, wl) if wl != 999 else (1, -mc(r))

    under.sort(key=queue_key)

    from zoneinfo import ZoneInfo
    today = datetime.datetime.now(ZoneInfo("America/New_York")).date().isoformat()  # Codex review of PR #2: the VM runs UTC
    out_rows = []
    for i, r in enumerate(under, 1):
        sym = (r["symbol"] or "").strip().upper()
        cik, sec_name, exch = cik_for(sym)
        out_rows.append({
            "queue_pos": i, "ticker": sym, "name": (r.get("name") or "").replace(" Common Stock","").replace(" Ordinary Shares","").strip(),
            "sec_name": sec_name or "", "cik": cik or "", "exchange": exch or "",
            "price": price(r), "market_cap": int(mc(r)), "market_cap_b": round(mc(r)/1e9, 3),
            "sector": r.get("sector") or "", "industry": r.get("industry") or "", "country": r.get("country") or "",
            "watchlist": "yes" if sym in WATCHLIST else "",
        })
    with open(f"{BASE}/universe.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out_rows[0].keys())); w.writeheader(); w.writerows(out_rows)

    # preserve existing progress: surviving entries are kept verbatim (module docstring)
    write_queue(f"{BASE}/queue.json", [r["ticker"] for r in out_rows], today)

    no_cik = [r["ticker"] for r in out_rows if not r["cik"]]
    with open(f"{BASE}/universe_notes.md", "w", encoding="utf-8") as f:
        f.write(f"# Universe — built {today}\n\n")
        f.write(f"- Approximation: top 3,000 US-listed operating companies by market cap (Nasdaq screener), Russell 3000 equivalent for screening purposes. Official Russell list is licensed; iShares IWV download is bot-blocked.\n")
        f.write(f"- After <$40B filter: **{len(out_rows)} companies**. Smallest: ${out_rows[-1]['market_cap_b']}B ({out_rows[-1]['ticker']}). Largest under cutoff: ${out_rows[0]['market_cap_b']}B among non-watchlist ordering.\n")
        f.write(f"- Non-operating securities dropped during clean: {len(dropped)}.\n")
        f.write(f"- Tickers with no SEC CIK match (EDGAR DCF may be limited / foreign filer): {len(no_cik)} — {', '.join(no_cik[:40])}\n")
        f.write(f"- Queue order: Andrew's watchlist first (in watchlist order), then descending market cap.\n")
        f.write(f"- At 1 company/hour, 24/day: full sweep ≈ {len(out_rows)/24:.0f} days. At 12/day: ≈ {len(out_rows)/12:.0f} days. Completed companies are re-queued only on Andrew's say-so or after a new 10-K/10-Q.\n")
    print(f"universe={len(out_rows)} no_cik={len(no_cik)} smallest_b={out_rows[-1]['market_cap_b']}")

if __name__ == "__main__":
    main()
