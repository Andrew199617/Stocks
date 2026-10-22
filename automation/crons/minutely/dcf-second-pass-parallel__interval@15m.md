---
id: dcf-second-pass-parallel
title: DCF second pass (parallel B) — 1 company per 15 min
enabled: false
owner: goal:russell-3000-owner-s-earnings-dcf-sweep
mode: task
schedule:
  kind: interval
  timezone: America/New_York
  at: 2026-10-13T22:17:00
  every: 15m
timeout_secs: 3600
delivery:
  - chat_id: be9b1806-e747-4d34-97fc-f5080aadead5
metadata:
  originating_chat_context_json: '{"chat_id":"be9b1806-e747-4d34-97fc-f5080aadead5","origin_provider":"main","chat_kind":"direct","event_kind":"message","require_mention":false,"device_id":"70fbb853-a274-4b72-9764-c40089a5f6af"}'
  presentation_locale: en-US
---
Run a SECOND PASS on ONE company already scored by the owner's-earnings DCF sweep. Read ~/workspace/stocks/_system/SECOND_PASS.md and follow its "Worker steps" exactly — preflight (`python3 ~/workspace/stocks/_system/preflight.py`; any exit but 0: do not claim, record the run as failed and finish), then claim with `queue.py pass2-claim`, freshness + forensic battery via forensic_pull.py, the hunts in both directions plus the guidance-vs-model check and the two adversarial tier tests, the materiality rule (score changes only on a ≥2pp weighted-IRR move or a tier change driven by a filing-sourced figure), and the mechanics: a verdict lands in judgment.json as a `second_pass` object and goes through make_score.py — never edit score.json or second_pass_queue.json by hand; `queue.py pass2-check <T>` before you write anything for the review (second_pass.md, the analysis.md addendum, judgment.json, ttm.json, the engine) — if it refuses, write nothing, report nothing and finish; `queue.py pass2-done <T> done_no_change|done_changed` closes the claim — if it refuses (the name was refreshed or re-scored while you wrote), delete the second_pass.md and the analysis.md addendum you wrote in this run, leave the rest as the refusal says and report nothing. On a 5.7 run `pass2-done` also refuses an analysis that fails `check_quotes.py` (run it before pass2-done); that refusal ("analysis.md fails the quote check") is not a re-score: delete nothing, fix the addendum's figures and run pass2-done again (SECOND_PASS step 7). A pass-2 change is cut as a PR per _system/PR_PROTOCOL.md. Report to chat only when a change moves the company into Tier S/A and score.json says alert_eligible: true, or out of Tier S/A and score.json says exit_alert_eligible: true. Run health: begin with `python3 ~/workspace/stocks/_system/run_health.py start dcf-second-pass-parallel` and end every run with `run_health.py record dcf-second-pass-parallel ok|fail` (SECOND_PASS step 8 says which); post to chat any line it prints.
