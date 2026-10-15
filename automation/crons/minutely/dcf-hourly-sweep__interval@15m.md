---
id: dcf-hourly-sweep
title: DCF sweep — 1 company per 15 min
enabled: true
owner: goal:russell-3000-owner-s-earnings-dcf-sweep
mode: task
schedule:
  kind: interval
  timezone: America/New_York
  at: 2026-10-13T21:50:38
  every: 15m
timeout_secs: 3600
delivery:
  - chat_id: be9b1806-e747-4d34-97fc-f5080aadead5
metadata:
  tags: [cron:automatic-interval-anchor]
  originating_chat_context_json: '{"chat_id":"3a736e88-a5b4-4afe-86e9-220f93a4f0e3","origin_provider":"main","chat_kind":"direct","event_kind":"message","require_mention":false}'
  presentation_locale: en-US
---
Run ONE company through the owner's-earnings DCF sweep (pass 1). Read ~/workspace/stocks/_system/WORKER_SPEC.md and follow it exactly — it is the single source for pass 1: mechanics (never hand-edit queue.json / score.json; queue.py, ttm.py, make_score.py only), the eleven steps (claim → preliminary engine run and its exit cases → research → every fragility flag resolved → moat 0-10 with FOR/AGAINST pillars → five scenarios with the growth-start sanity check → analysis.md → judgment.json under the bounded override authority → make_score.py → enrichment (fundamentals.py + prices.py, non-blocking) → queue.py done + build_daily_html.py), and the reporting rule (chat only when score.json has alert_eligible: true). README.md "Fixes & lessons" and DCF_AUDIT.md explain why each rule exists; APP/ is the worked example.
