#!/usr/bin/env python3
"""One command that brings a checkout's data up to date (2026-10-16).

Muse's crons run these scripts on the VM on a schedule. On any other
machine (a fresh clone, or Andrew's PC) this does the same work in one go,
so the site can be opened locally:

  python _system/refresh.py               # Nasdaq caches (prices, Street) + live returns + site
  python _system/refresh.py --quick       # prices + live returns + site (the 30-minute job)
  python _system/refresh.py --sec         # also re-check every name's SEC files (about 4 SEC requests per name)
  python _system/refresh.py --tickers APP,KR [--sec]   # just these names
  python _system/refresh.py --attachment  # also write the dated ranking file + history CSV

Then serve the site:   python -m http.server 8791 --directory _daily
and open http://localhost:8791/site/

What lives where (see .gitignore): each company's judgment record and its
SEC files (fundamentals, statements, segments, profile) are committed, and
the SEC files are rewritten only when their content changes. Everything else
is a cache this script recreates: Nasdaq prices (prices.json), the Street
block (street.json), live returns (live.json) and the built site
(_daily/site/data, index.json, meta.json). A fresh clone therefore needs no
SEC requests to show the site, only the Nasdaq refresh (a few minutes for
~100 names; the 5-day intraday chart fills in over five trading days,
because Nasdaq's intraday endpoint returns only the latest session).

Steps run in the order WORKER_SPEC.md step 9 uses; a failed step is
reported and the rest still run. Exit status 1 if any step failed.
Request pacing is each script's own (SEC <= 10 requests/second).
"""
import argparse
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.environ.get("STOCKS_BASE") or os.path.dirname(HERE)


def scored_tickers():
    return sorted(d for d in os.listdir(BASE)
                  if not d.startswith((".", "_")) and os.path.isfile(os.path.join(BASE, d, "score.json")))


def check_timezone():
    """Windows Python ships without the IANA database; every script stamps New York dates."""
    try:
        from zoneinfo import ZoneInfo
        ZoneInfo("America/New_York")
        return True
    except Exception:
        print("refresh.py: the America/New_York time zone is unavailable. Run:\n"
              "  python -m pip install -r requirements.txt\n(it installs tzdata, which Windows Python lacks)",
              file=sys.stderr)
        return False


def run(label, args, results, quiet=False):
    """Run one _system script with this interpreter; quiet drops its stdout (stderr still shows)."""
    env = dict(os.environ, PYTHONIOENCODING="utf-8", STOCKS_BASE=BASE)
    t0 = time.time()
    print(f"\n=== {label}: {' '.join(args)}", flush=True)
    rc = subprocess.call([sys.executable, os.path.join(HERE, args[0])] + args[1:], env=env, cwd=BASE,
                         stdout=subprocess.DEVNULL if quiet else None)
    dt = time.time() - t0
    results.append((label, rc, dt))
    print(f"--- {label}: {'ok' if rc == 0 else f'exit {rc}'} in {dt:.0f}s", flush=True)
    return rc


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--quick", action="store_true", help="prices, live returns and the site only")
    ap.add_argument("--sec", action="store_true", help="also re-check fundamentals, statements and segments for every name")
    ap.add_argument("--tickers", help="comma-separated tickers instead of every scored folder")
    ap.add_argument("--attachment", action="store_true", help="also write the dated ranking file and _daily/history CSV")
    ap.add_argument("--force", action="store_true", help="rebuild every site record (build_site.py --force)")
    a = ap.parse_args(argv)
    if a.quick and a.sec:
        ap.error("--quick and --sec contradict each other")
    if not check_timezone():
        return 1

    results = []
    names = [t.strip().upper() for t in a.tickers.split(",") if t.strip()] if a.tickers else None
    if names:
        missing = [t for t in names if not os.path.isdir(os.path.join(BASE, t))]
        if missing:
            print(f"refresh.py: no folder for {', '.join(missing)}", file=sys.stderr)
            return 2
        for t in names:
            if a.sec:
                run(f"fundamentals {t}", ["fundamentals.py", t], results)
            run(f"prices {t}", ["prices.py", t, "--quiet"], results)
            if a.sec:
                run(f"segments {t}", ["segments.py", t], results)
                run(f"statements {t}", ["statements.py", t], results)
            if a.sec:
                run(f"profile {t}", ["profile.py", t, "--quiet"], results)          # About + filings, and Street
            elif not a.quick:
                run(f"Street {t}", ["profile.py", t, "--street-only", "--quiet"], results)  # Nasdaq only, no SEC request
            run(f"reprice {t}", ["reprice.py", t, "--quiet"], results)
    else:
        if a.sec:
            for t in scored_tickers():
                run(f"fundamentals {t}", ["fundamentals.py", t], results, quiet=True)
        run("prices", ["prices.py", "--all", "--quiet"], results)
        if a.sec:
            run("segments", ["segments.py", "--all"], results)
            run("statements", ["statements.py", "--all"], results)
        if a.sec:
            run("profile + Street", ["profile.py", "--all", "--quiet"], results)    # rebuilt on a new filing; Street weekly
        elif not a.quick:
            run("Street", ["profile.py", "--all", "--street-only", "--quiet"], results)  # Nasdaq only, no SEC request
        run("reprice", ["reprice.py", "--all", "--quiet"], results)

    site = ["build_site.py", "--quiet"]
    if a.force:
        site.append("--force")
    if a.attachment:
        site.append("--attachment")
    run("site", site, results)

    failed = [r for r in results if r[1] != 0]
    total = sum(r[2] for r in results)
    print(f"\nrefresh.py: {len(results) - len(failed)}/{len(results)} steps ok in {total:.0f}s"
          + (f"; failed: {', '.join(label for label, _, _ in failed)}" if failed else ""))
    if not failed:
        print("Serve the site:  python -m http.server 8791 --directory _daily   then open http://localhost:8791/site/")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
