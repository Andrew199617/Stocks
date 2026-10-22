# Automation — what runs, when, and why

The sweep is a set of scheduled jobs run by Muse (the agent on the VM at
`~/workspace/stocks`). Each job is a Markdown file: YAML front matter the scheduler reads
(`id`, `enabled`, `schedule`, `timeout_secs`, `delivery`) and a body that is the job's
instruction. The bodies are deliberately short: they point at the specs under
`_system/` so the two pass-1 workers (and the two pass-2 workers) can never drift apart
again. Change the method in the spec, not in a cron body.

A note on confidence: these files were created inside Muse's own automation platform and
this folder is the mirror of them. The scheduler's exact semantics (what `at` anchors,
whether an overlapping run is skipped or stacked, how `delivery` is used) are Muse's, not
documented here, so the cadence choices below are deliberately conservative. If the
platform behaves differently from what a body assumes, fix the body, not the spec.

## The big idea (so a job's purpose is never in doubt)
Find companies whose **true owner's earnings** — operating cash flow minus capex minus
stock-based compensation, filing-direct, with every data gap surfaced instead of
zero-filled — support a probability-weighted DCF that clears the 15 / 20 / 25% hurdles at
today's price. The 0–10 moat score sets how fast growth fades. Since engine 5.7 it has two
layers that make_score checks: its sources (why the advantage exists) and an evidence
scorecard (does it compound — the **return on invested capital** history, margins,
retention, pricing). Its direction — eroding or widening returns and margins over the last
5 FY — sets how long growth holds before the fade (0 / 2 / 3 years).
Everything else (pages, charts, statements, live repricing) exists to make that verdict
and its evidence readable and current.

## The day, in America/New_York time
| When | Job | What it does |
|---|---|---|
| 06:30 daily | `dcf-filing-watch` | `filing_watch.py`: one small EDGAR request per done name; a newer 10-K/10-Q than the one scored sends the name back to pending with the reason (`queue.py refresh`, which also reopens a finished second pass: the re-score is a new scoring generation), so the sweep re-scores it on fresh filings (the audit's "freshness" item). Exit 3 when every fetch failed (an EDGAR outage): a failed run. |
| every 15 min | `dcf-hourly-sweep` (name is historical) | Pass 1 on one company per `_system/WORKER_SPEC.md`: `preflight.py` (stops on engine drift: this tree's policy files differ from origin/main) → claim → preliminary engine run (saved with `check_quotes.py --save-run`) and its exit cases → SEC enrichment (fundamentals, segments, statements, profile) → research, recorded as facts → every fragility flag resolved (STALE_FY: `--ttm`, or `ttm_rejection_reason` with a cash-flow line and a number; ttm.py exit 3: `ttm_unavailable_reason` quoting it) → moat 0-10: sources + pillar scorecard (`moat_scorecard.py` dry run; it prints the `--moat-trend` for the final run) → five scenarios → analysis.md → judgment.json + facts.json → final engine run → make_score → check_quotes → prices, reprice → `queue.py done` (refuses a 5.7 run that fails the quote check) → `build_site.py`; the company PR is cut per `_system/PR_PROTOCOL.md`. |
| every 15 min, offset | `dcf-sweep-parallel` | A second pass-1 worker, identical spec. **Disabled**: the round-1 audit said hold at one worker until correctness landed; v5.4 landed it. Enabling doubles throughput; the queue lock makes it safe. Andrew's call. |
| every 30 min | `dcf-second-pass` | Pass 2 on one already-scored company per `_system/SECOND_PASS.md`: `preflight.py`, then `queue.py pass2-claim` (materiality ≥2pp or a tier change, adversarial tier tests, guidance check; verdicts flow through judgment.json → make_score; `pass2-done` refuses a 5.7 analysis that fails `check_quotes.py`; a finished review's PR is cut per `_system/PR_PROTOCOL.md`). One review per scoring generation: `queue.py pass2-check` before the first write, and `pass2-done`, refuse a claim whose name was refreshed or re-scored meanwhile (the worker then writes nothing, or deletes the second_pass.md it wrote, and reports nothing). **Re-enabled 2026-10-14** now that the governance the audit required exists; 30 min so it never starves pass 1. |
| every 15 min, offset | `dcf-second-pass-parallel` | Second pass-2 worker. **Disabled**; same reasoning as above. |
| every 30 min, market hours | `dcf-live-refresh` | `prices.py --all` → `reprice.py --all` → `build_site.py`: the hosted site's expected returns follow the latest close. Does nothing outside 09:30–16:30 ET. |
| 19:07 daily | `dcf-daily-ranking` | Prices and reprice for every scored name; segments and statements refreshes (each skips a name with no new filing); `profile.py --all --max-age-days 7`, which re-pulls a name's `street.json` (the Nasdaq Street block) once it is a week old or a source failed in its last pull, and rebuilds `profile.json` only when the EDGAR filing feed changed or a source failed in its last build; `industry_returns.py --write` (the same-ladder SIC-group return medians the moat scorecard reads, rewritten only when a member changed); then `build_site.py --attachment` (the dated ranking file plus the committed `_daily/history/ranking-<date>.csv`), then the dated ranking file into the chat with the top 10 by live expected return, any new alert-eligible S/A names and any name whose live tier crossed into or out of S/A; then `pr_audit.py --quiet` (done names whose folder differs from main with no PR for their scoring generation — a finished second pass counts as its own generation, cut as a Second pass PR — and scores not from their run) and `run_health.py check` (a job that stopped starting), each a line in the message only when it finds something. |

Off the VM (a fresh clone, Andrew's PC) the same refreshes are one command,
`python _system/refresh.py`: prices, the Street (`profile.py --all --street-only`, no SEC
request), reprice and the site; `--quick` runs only the live-refresh job's three steps,
`--sec` also re-checks the SEC files, `--attachment` adds the daily file and history CSV.
It schedules nothing.

## Rules every body obeys
- What a job may commit: each company's judgment record and its SEC files (`fundamentals.json`,
  `statements.json`, `segments.json`, `profile.json`, which the scripts rewrite only when their
  content changes), `_daily/history/ranking-<date>.csv` and `_system/industry_returns.json`
  (the daily ranking job's build; a stable write). Prices, the Street block (`street.json`),
  live returns and the built site are gitignored caches the jobs recreate, so `git add <T>/`
  never picks them up. `_system/run_health.json` is per-machine state, gitignored; never
  commit it.
- Company PRs are cut per `_system/PR_PROTOCOL.md` (`pr_worktree.py`), never by hand. A
  review's "didnt fix" that names a code defect appends an entry to
  `_system/ENGINE_BACKLOG.md` in the same PR.
- Nothing edits `queue.json`, `score.json`, `second_pass_queue.json` or any HTML by hand.
  `queue.py`, `make_score.py` and `build_site.py` are the only writers (plus
  `build_universe.py`'s universe rebuild, which keeps every surviving queue entry and takes
  queue.py's lock).
- Chat is for exceptions: an alert-eligible S/A name (`alert_eligible`: medium+ confidence,
  not a sector misfit, tier not resting on an override, IRR not at the model's floor), a
  pass-2 change that takes a name out of S/A with `exit_alert_eligible` (medium+ confidence,
  not a sector misfit, tier not existing only because an override fills a data gap), or a
  broken job (run_health's lines). Everything else is read on the site or in the daily file.
- **Run health.** Every body opens a run with `run_health.py start <id>` and closes it with
  `record <id> ok|fail`. Any line it prints goes to chat: ALERT on the second failed run in a
  row, STILL FAILING once a day after that, RECOVERED once. The 19:07 job's `check` names a
  job that stopped starting (idle more than max(3 × its interval, interval + 60 min)). A run
  that started and never recorded (a timeout, a crash) counts as failed at a later start,
  once it is older than the job's `timeout_secs` (its front matter). Runs that overlap inside
  the timeout (a slow 15-minute worker still going at the next firing) are not failures, and
  `record` closes the newest open run. What counts as failed:

  | job | ok | fail |
  |---|---|---|
  | pass 1 (`dcf-hourly-sweep`, `dcf-sweep-parallel`) | the run ended at a state WORKER_SPEC names: no pending entry; `queue.py done` + `build_site.py`; a `queue.py block` (DATA_GAP / NO_DATA). A `reprice.py` exit 3 (Skip) is not a failure | preflight exit ≠ 0; a mandated script crashed (a non-zero exit no step-2 exit case covers); make_score / `queue.py done` refused and the run ended without done or block |
  | pass 2 (`dcf-second-pass`, `-parallel`) | no candidates; a pass2-check / pass2-done refusal handled as SECOND_PASS steps 5 / 7 say; pass2-done recorded | preflight exit ≠ 0; a mandated script crashed; make_score refused unresolved |
  | `dcf-filing-watch` | `filing_watch.py` exit 0 | exit ≠ 0 (exit 3 = every submissions fetch failed: an EDGAR outage) |
  | `dcf-daily-ranking` | the dated file was delivered | `build_site.py --attachment` failed or the file was not delivered (refresh-step failures are named in the message, not a failed run) |
  | `dcf-live-refresh` (market hours only; outside them no `start`) | the three scripts exited 0 | any of them exited ≠ 0 |

- Rate limits are Muse's cost: EDGAR and Nasdaq at most 10 requests/second, and every SEC
  `--all` refresh checks the small EDGAR submissions feed before touching a large file.
- A cron body never carries method. It says which spec to follow and the few operational
  lines that belong to scheduling (silence rules, market-hours guard, cadence advice).

## Changing cadence or enabling a worker
Edit the front matter (`enabled`, `schedule.every`) and record the change with a dated
line in `GOAL.md`. The `timeout_secs: 3600` on the 15-minute workers predates the lease:
a slow run can overlap the next firing; the claim lease (90 min) makes that safe for the
queue, but if the platform stacks copies, lower the timeout to ~25 minutes. Each new job id
needs nothing in run_health.py: `check` reads the cadence from the front matter
(dcf-live-refresh is market-hours only and never overdue).
