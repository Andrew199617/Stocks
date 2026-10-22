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
Run ONE company through the owner's-earnings DCF sweep (pass 1). Read ~/workspace/stocks/_system/WORKER_SPEC.md and follow it exactly — it is the single source for pass 1: mechanics (never hand-edit queue.json / score.json; queue.py, ttm.py, make_score.py only), the eleven steps (preflight + claim → preliminary engine run (saved with check_quotes.py --save-run) and its exit cases → SEC enrichment (fundamentals, segments, statements, profile; non-blocking) → research, recorded as facts → every fragility flag resolved (STALE_FY: --ttm, or ttm_rejection_reason with a cash-flow line and a number; ttm.py exit 3: ttm_unavailable_reason quoting it) → moat 0-10: sources + pillar scorecard (moat_scorecard.py dry run before the final engine run — pass the --moat-trend it prints to the final engine run) → five scenarios with the growth-start sanity check → analysis.md → judgment.json + facts.json under the bounded override authority → final engine run → make_score.py → check_quotes.py → prices, reprice (non-blocking) → queue.py done (refuses a 5.7 run that fails the quote check) + build_site.py; the company PR per _system/PR_PROTOCOL.md), and the reporting rule (chat only when score.json has alert_eligible: true). Run health: begin with `python3 ~/workspace/stocks/_system/run_health.py start dcf-hourly-sweep` and end every run with `run_health.py record dcf-hourly-sweep ok|fail` (WORKER_SPEC step 11 says which); post to chat any line it prints. README.md "Fixes & lessons" and DCF_AUDIT.md explain why each rule exists; APP/ is the worked example.
