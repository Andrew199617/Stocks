---
id: dcf-filing-watch
title: Filing watcher — re-queue scored names after a new 10-K / 10-Q
enabled: true
owner: goal:russell-3000-owner-s-earnings-dcf-sweep
mode: task
schedule:
  kind: daily
  timezone: '@user.current'
  time: 06:30:00
timeout_secs: 1800
delivery:
  - chat_id: be9b1806-e747-4d34-97fc-f5080aadead5
metadata:
  tags: [cron:flexible-time]
  originating_chat_context_json: '{"chat_id":"be9b1806-e747-4d34-97fc-f5080aadead5","origin_provider":"main","chat_kind":"direct","event_kind":"message","require_mention":false,"device_id":"70fbb853-a274-4b72-9764-c40089a5f6af"}'
  presentation_locale: en-US
---
Keep every verdict on current filings. Silent job unless it breaks.

1. Run `python3 ~/workspace/stocks/_system/filing_watch.py`. For every done name it reads the small EDGAR submissions feed and compares the newest periodic filing with what the folder was scored on (the fiscal year in dcf_numbers.json; the TTM pin's quarter in ttm.json). A newer filing sends the name back to pending through `queue.py refresh <T> --stdin` with a NEW_FILING reason on the entry; the next pass-1 worker re-scores it with the new filing (judgment.json and overrides carry over; the worker writes a dated supersession in analysis.md).
2. Post nothing to chat unless the script fails; the summary line it prints (checked / refreshed / unchanged / errors) goes in the job log. If more than ~40 names refresh on one day (earnings season), say so in one line so Andrew knows the ranking will churn for a few days.
