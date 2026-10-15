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
"""
import json, csv, re, sys, os, datetime, urllib.request

BASE = os.environ.get("STOCKS_SYS") or os.path.dirname(os.path.abspath(__file__))
def _load_watchlist():
    """v5.4: the canonical watchlist lives in _system/watchlist.json (Andrew edits it or
    asks Muse to); the old hard-coded list is the fallback."""
    try:
        return [x["ticker"].upper() for x in json.load(open(f"{BASE}/watchlist.json", encoding="utf-8"))["tickers"]]
    except Exception:
        return ["U","META","NFLX","RDDT","CMPS","ADBE","MSFT","AMZN","APP","LFTO","NTDOY","SONY","SNAP","GOOGL","DUOL","SE","NVO","TTWO","OTLY","STZ","INTC","DFTX","XIACY","FIG"]
WATCHLIST = _load_watchlist()

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

    rows = json.load(open(f"{BASE}/nasdaq_screener.json"))["data"]["rows"]
    sec = json.load(open(f"{BASE}/sec_tickers_exchange.json"))
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
    with open(f"{BASE}/universe.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out_rows[0].keys())); w.writeheader(); w.writerows(out_rows)

    # preserve existing progress if queue.json exists
    status = {}
    try:
        old = json.load(open(f"{BASE}/queue.json"))
        status = {e["ticker"]: e.get("status", "pending") for e in old.get("queue", [])}
    except Exception: pass
    queue = [{"ticker": r["ticker"], "queue_pos": r["queue_pos"], "status": status.get(r["ticker"], "pending")} for r in out_rows]
    json.dump({"built": today, "cutoff_market_cap_b": 40, "universe_size": len(out_rows), "queue": queue}, open(f"{BASE}/queue.json", "w"), indent=1)

    no_cik = [r["ticker"] for r in out_rows if not r["cik"]]
    with open(f"{BASE}/universe_notes.md", "w") as f:
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
