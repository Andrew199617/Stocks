#!/usr/bin/env python3
"""Filing watcher (v5.4, 2026-10-14) — audit round-1 P1: "watch for new 10-Q/10-K
filings daily and re-queue; freshness moves out of pass 2".

Usage: python3 filing_watch.py [--dry-run] [--only T,T] [--quiet]

For every DONE name in the queue, read the small EDGAR submissions feed and
compare the newest periodic filing's report period with what the folder was
scored on:
  - annual:    dcf_numbers.json latest_period_end  (the last fiscal year the engine used)
  - quarterly: ttm.json ytd_end when a TTM pin was used, else the same annual date
A newer 10-K / 20-F / 40-F period, or a newer 10-Q period for a name whose base
was a TTM pin, means the score rests on stale filings: the name goes back to
pending through `queue.py refresh <T> --stdin` with the reason on the entry, so
the next pass-1 worker re-scores it with the new filing (judgment.json and any
overrides carry over automatically; the worker writes a dated supersession).
Names scored on the median base are re-queued on a new 10-K only — a new 10-Q
does not change a 3-year-median base, and STALE_FY already tells the worker to
pin TTM when it matters.

One request per name (≤10/s); nothing is written except the queue entries.
Prints a summary: checked / refreshed (with form + period) / unchanged / errors.
"""
import json, sys, os, time, datetime, subprocess, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.environ.get("STOCKS_BASE") or os.path.dirname(HERE)
UA = {"User-Agent": "Muse research andrewmauro199612@gmail.com"}
ANNUAL = ("10-K", "10-K/A", "20-F", "40-F")
QUARTERLY = ("10-Q", "10-Q/A")


def get_json(url, timeout=60):
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


def jload(p):
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def newest_periodic(sub):
    """{'annual': (form, report, filed), 'quarterly': (...)} from submissions.recent."""
    rec = (sub.get("filings") or {}).get("recent") or {}
    forms, filed, rep = rec.get("form", []), rec.get("filingDate", []), rec.get("reportDate", [])
    out = {}
    for i, form in enumerate(forms):
        kind = "annual" if form in ANNUAL else "quarterly" if form in QUARTERLY else None
        if kind is None or i >= len(rep) or not rep[i]:
            continue
        cur = out.get(kind)
        if cur is None or rep[i] > cur[1]:
            out[kind] = (form, rep[i], filed[i] if i < len(filed) else "")
    return out


def main():
    args = sys.argv[1:]
    dry = "--dry-run" in args
    quiet = "--quiet" in args
    only = set(x.upper() for x in args[args.index("--only") + 1].split(",")) if "--only" in args else None
    q = jload(f"{BASE}/_system/queue.json") or {"queue": []}
    done = [e["ticker"] for e in q["queue"] if e.get("status") == "done" and (not only or e["ticker"] in only)]
    refreshed, unchanged, errors = [], 0, []
    for t in done:
        n = jload(f"{BASE}/{t}/dcf_numbers.json") or {}
        cik = n.get("cik")
        if not cik:
            errors.append(f"{t}: no cik in dcf_numbers.json"); continue
        scored_annual = n.get("latest_period_end") or ""
        ttm = jload(f"{BASE}/{t}/ttm.json") or {}
        pinned = "ttm" in str(n.get("base_source") or "").lower()
        scored_quarter = (ttm.get("ytd_end") or "") if pinned else ""
        try:
            sub = get_json(f"https://data.sec.gov/submissions/CIK{int(cik):010d}.json")
        except Exception as e:
            errors.append(f"{t}: submissions fetch failed ({e})"); continue
        newest = newest_periodic(sub)
        reason = None
        a = newest.get("annual")
        if a and scored_annual and a[1] > scored_annual:
            reason = f"NEW_FILING: {a[0]} for the period ending {a[1]} (filed {a[2]}) is newer than the scored fiscal year {scored_annual}"
        qq = newest.get("quarterly")
        if reason is None and pinned and qq and scored_quarter and qq[1] > scored_quarter and (not a or qq[1] > a[1]):
            reason = f"NEW_FILING: {qq[0]} for the period ending {qq[1]} (filed {qq[2]}) is newer than the TTM pin through {scored_quarter}"
        if reason:
            refreshed.append((t, reason))
            if not dry:
                r = subprocess.run([sys.executable, f"{HERE}/queue.py", "refresh", t, "--stdin"], input=reason, capture_output=True, text=True)
                if r.returncode != 0:
                    errors.append(f"{t}: queue refresh failed: {r.stderr.strip()}")
            if not quiet:
                print(f"{'[dry-run] ' if dry else ''}{t}: {reason}")
        else:
            unchanged += 1
        time.sleep(0.12)
    print(f"filing_watch: checked {len(done)} done names — {len(refreshed)} refreshed, {unchanged} unchanged, {len(errors)} errors"
          + (f"\n  " + "\n  ".join(errors) if errors else ""))


if __name__ == "__main__":
    main()
