---
id: dcf-daily-ranking
title: Daily DCF ranking HTML
enabled: true
owner: goal:russell-3000-owner-s-earnings-dcf-sweep
mode: task
schedule:
  kind: daily
  timezone: '@user.current'
  time: 19:07:00
timeout_secs: 1800
delivery:
  - chat_id: be9b1806-e747-4d34-97fc-f5080aadead5
metadata:
  tags: [cron:flexible-time]
  originating_chat_context_json: '{"chat_id":"be9b1806-e747-4d34-97fc-f5080aadead5","origin_provider":"main","chat_kind":"direct","event_kind":"message","require_mention":false,"device_id":"70fbb853-a274-4b72-9764-c40089a5f6af"}'
  presentation_locale: en-US
---
Send Andrew today's owner's-earnings DCF ranking.

Steps:
0. `python3 ~/workspace/stocks/_system/run_health.py start dcf-daily-ranking`.
1. Refresh prices and the live overlay for every scored name: `python3 ~/workspace/stocks/_system/prices.py --all --quiet` then `python3 ~/workspace/stocks/_system/reprice.py --all` (the scored cash-flow paths repriced at the last close → live.json; Tier F names are skipped by design). Then `python3 ~/workspace/stocks/_system/segments.py --all`, `python3 ~/workspace/stocks/_system/statements.py --all` and `python3 ~/workspace/stocks/_system/profile.py --all --max-age-days 7` (all cheap: each checks the small EDGAR submissions feed first and only re-fetches a name whose latest filing changed; profile.py also re-pulls the Nasdaq Street block into street.json once it is a week old). Then `python3 ~/workspace/stocks/_system/industry_returns.py --write` (the same-ladder SIC-group return medians the moat scorecard reads; rewritten only when a member changed).
2. Build: `python3 ~/workspace/stocks/_system/build_site.py --attachment` — regenerates the data layer in ~/workspace/stocks/_daily/site/ (meta.json, index.json, data/<TICKER>.json; the static app there renders it) and writes the dated self-contained ranking ~/workspace/stocks/_daily/ranking-<today>.html (+ latest.html) with the top rows' pages embedded, and the day's compact record ~/workspace/stocks/_daily/history/ranking-<today>.csv (one row per ranked name). It prints sweep progress (done of 2,617).
2b. `python3 ~/workspace/stocks/_system/pr_audit.py --quiet` and `python3 ~/workspace/stocks/_system/run_health.py check`: add each line they print to the message (pr_audit exit 1 = done names with no PR for their scoring generation, or a score not from its run; exit 3 = it could not run — say so).
3. Deliver the dated ranking file as an attachment in this chat (not latest.html), with a short message: sweep progress (X analyzed of 2,617, plus pilot exceptions), the top 10 by LIVE expected return as a compact list (ticker, live tier, bear→bull band, live IRR at the last close, scored IRR, price, IV@15%, upside), and call out any NEW Tier S or A names whose score.json has alert_eligible: true since yesterday's ranking (compare yesterday's _daily/history/ranking-<date>.csv, else the previous dated file / score.json analysis_dates), plus any name whose live tier crossed into or out of S/A since yesterday. Name sector misfits as such: their published tier is one notch below the numbers tier (a numbers tier of D or F, and the insurer payable-earnings base, are not notched) — quote a notched name as 'D (C by numbers)' from the history CSV's `tier_by_numbers` / `tier_notched`.
4. If zero companies have been analyzed so far, still send the file with one line saying the sweep has not completed its first company yet. Keep the message short and blunt; the file is the deliverable. Do not create Feed units.
5. For the git mirror: the HTML files, the site data, prices.json, live.json and street.json are gitignored caches. What this run changes in git is the history CSV, `_system/industry_returns.json` when a member changed, and any SEC file (fundamentals, statements, segments, profile) whose content changed. `_system/run_health.json` is per-machine state; never commit it.
6. `python3 ~/workspace/stocks/_system/run_health.py record dcf-daily-ranking ok` when the dated file was delivered, else `run_health.py record dcf-daily-ranking fail` with the reason (a failed `build_site.py --attachment` or an undelivered file; refresh-step failures are named in the message, not a failed run). Post any line it prints.
