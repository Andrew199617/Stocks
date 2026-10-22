---
id: dcf-live-refresh
title: Live price refresh — reprice every scored name at the latest close (market hours)
enabled: true
owner: goal:russell-3000-owner-s-earnings-dcf-sweep
mode: task
schedule:
  kind: interval
  timezone: America/New_York
  at: 2026-10-15T09:45:00
  every: 30m
timeout_secs: 1500
delivery:
  - chat_id: be9b1806-e747-4d34-97fc-f5080aadead5
metadata:
  tags: [cron:automatic-interval-anchor]
  originating_chat_context_json: '{"chat_id":"be9b1806-e747-4d34-97fc-f5080aadead5","origin_provider":"main","chat_kind":"direct","event_kind":"message","require_mention":false,"device_id":"70fbb853-a274-4b72-9764-c40089a5f6af"}'
  presentation_locale: en-US
---
Keep the site's expected returns close to live. Silent job: never post to chat unless the scripts themselves fail.

1. Outside US market hours (before 09:30 or after 16:30 America/New_York, or on a weekend / NYSE holiday) do nothing and finish — the daily ranking job refreshes everything after the close.
2. `python3 ~/workspace/stocks/_system/prices.py --all --quiet` (one Nasdaq history request plus one intraday request per scored name, well under 10 per second), then `python3 ~/workspace/stocks/_system/reprice.py --all` (the scored cash-flow paths repriced at the latest close → live.json; Tier F names are skipped by design), then `python3 ~/workspace/stocks/_system/build_site.py` (no attachment — just the data layer the static app reads). Everything this job writes (prices.json, live.json, _daily/site/) is a gitignored cache, so there is nothing to commit. Inside market hours wrap the three scripts with `python3 ~/workspace/stocks/_system/run_health.py start dcf-live-refresh` first and `run_health.py record dcf-live-refresh ok|fail` after them (ok when all three exited 0, else fail with the failing script's last line), and post any line it prints. Outside market hours (step 1) there is no `start`.
3. If the universe is fully scored and this takes longer than ~15 minutes per run, slow the interval to 60m or restrict the refresh to the watchlist and the top-ranked names — say so in automation/GOAL.md rather than silently skipping.
