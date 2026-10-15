---
id: dcf-second-pass
title: DCF second pass — 1 company per 30 min (re-enabled 2026-10-14 under the v5.4 governance)
enabled: true
owner: goal:russell-3000-owner-s-earnings-dcf-sweep
mode: task
schedule:
  kind: interval
  timezone: America/New_York
  at: 2026-10-13T22:09:00
  every: 30m
timeout_secs: 3600
delivery:
  - chat_id: be9b1806-e747-4d34-97fc-f5080aadead5
metadata:
  originating_chat_context_json: '{"chat_id":"be9b1806-e747-4d34-97fc-f5080aadead5","origin_provider":"main","chat_kind":"direct","event_kind":"message","require_mention":false,"device_id":"70fbb853-a274-4b72-9764-c40089a5f6af"}'
  presentation_locale: en-US
---
Run a SECOND PASS on ONE company already scored by the owner's-earnings DCF sweep. Read ~/workspace/stocks/_system/SECOND_PASS.md and follow its "Worker steps" exactly — claim with `queue.py pass2-claim`, freshness + forensic battery via forensic_pull.py, the hunts in both directions plus the guidance-vs-model check and the two adversarial tier tests, the materiality rule (score changes only on a ≥2pp weighted-IRR move or a tier change driven by a filing-sourced figure), and the mechanics: a verdict lands in judgment.json as a `second_pass` object and goes through make_score.py — never edit score.json or second_pass_queue.json by hand; `queue.py pass2-done <T> done_no_change|done_changed` closes the claim. Report to chat only when a change moves the company into or out of Tier S/A and score.json says alert_eligible: true.
