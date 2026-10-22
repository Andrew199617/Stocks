# Stocks

Repo going through 3000 stocks in russel using ai to give buy signals.

## What this is

A systematic owner's-earnings DCF sweep of ~2,617 US-listed companies under ~$40B
market cap (the reproducible equivalent of the Russell 3000 under $40B; the
official Russell list is licensed). Each company gets a filing-direct analysis
from SEC EDGAR data — no third-party financial data:

- Owner's earnings = operating cash flow − capex − stock-based compensation
  (conservative; SBC always treated as a real cost). In-process R&D bought in an
  acquisition and expensed (so no OE leg sees it) is deducted once from every
  intrinsic value and added to the IRR price — never from the base (engine 5.6)
- Base = median of the last 3 fiscal years' OE/share. When the fiscal year is
  stale, a TTM from the 10-Qs replaces it (at a 20-F / 40-F filer, a declared
  6-K interim bridge can). A worker may reject that TTM only with a reason that
  names the distorting cash-flow line and a number; both bases are then
  recorded (engine 5.7)
- Five scenarios (super bear → super bull) with assigned probabilities. A 0–10
  moat score drives how fast growth fades to a 2.5% terminal rate. Since
  engine 5.7 the moat has two layers that make_score checks: its sources (why
  the advantage exists) and an evidence scorecard (does it compound). Its
  direction (eroding or widening, measured by make_score) sets how long growth
  holds before the fade
- Headline = probability-weighted intrinsic value / IRR. Tiers at the owner's
  hurdles: **S ≥ 25%, A 20–25%, B 15–20%, C 10–15%, D < 10%, F = no positive
  normalized owner's earnings**
- A sector misfit (a bank, insurer, REIT or utility, by its Nasdaq sector or
  its EDGAR SIC) publishes one tier below its numbers tier. make_score applies
  this notch by rule (engine 5.7). A numbers tier of D or F is not notched, and
  neither is the insurer payable-earnings base

## The gate (v5)

The engine never emits a tier on incomplete filing data. If SBC, capex, diluted
shares, or operating cash flow is missing for any of the last 3 fiscal years —
or the filer reports non-USD — the company blocks as `DATA_GAP` instead of
scoring on silently zero-filled numbers. Gaps can be closed only by a structured
override in `judgment.json` (`{value, source, reason, kind}`), decided by the
agent, measured against the base the final run actually used, and recorded in
`_system/overrides_registry.json` — including whether the override is the only
reason the company has a tier at all.

Mechanics are code, never hand arithmetic: `queue.py` (locked claim/block/done),
`ttm.py` (TTM from 10-Q YTD facts or, with `--interim`, from a declared 6-K
interim bridge at a 20-F / 40-F filer, saved to `ttm.json`), `make_score.py`
(the only writer of `score.json`; verifies the engine's content hash and refuses
pre-v5 or drifted inputs) and `check_quotes.py` (since engine 5.7 every number in
`analysis.md` must trace to a generated file; `queue.py done` refuses a 5.7 run
that fails). A worker runs `preflight.py` before it claims a company: it stops
when its tree's method files differ from origin/main. Company PRs are cut with
`pr_worktree.py`, as `_system/PR_PROTOCOL.md` says.

## Layout

- `_system/` — engine, tooling, method docs (`README.md` there is the full
  method + "Fixes & lessons"; `PR_PROTOCOL.md` says how a company PR is cut;
  `ENGINE_BACKLOG.md` lists every deferred code defect), the two external
  audits and responses under `audits/`, queue/universe state, and the
  overrides registry
- `<TICKER>/` — one folder per company: `financials_history.csv`,
  `dcf_numbers.json`, `analysis.md`, `score.json`, plus `judgment.json`,
  `key_numbers.md`, `ttm.json` where applicable (the judgment record), and the
  SEC files `fundamentals.json`, `statements.json`, `segments.json`,
  `profile.json` (see "What is in git" below). Since engine 5.7 the judgment
  record can also hold `facts.json` (the worker's declared facts: numbers the
  engine cannot produce, each with its source), saved engine runs
  `dcf_numbers_<label>.json`, and `annual_instance.json` (when the engine read a
  fiscal year from the filing's own XBRL instance)
- `_daily/` — the static site (`site/`: the app; its data is built locally),
  `history/` (one small CSV per day: that day's ranking), and the dated ranking
  HTML from before 2026-10-16
- `automation/` — the scheduled-job definitions that run the sweep (pass-1
  and pass-2 workers, a filing watcher, a market-hours live refresh, and the
  daily ranking; which jobs are enabled and their cadences live there and in
  each job's front matter)

## What is in git

Committed: the code and specs, each company's judgment record, its SEC files
(rewritten only when a filing changes their content, so they do not churn),
the moat scorecard's industry medians (`_system/industry_returns.json`, rebuilt
by the daily ranking job) and the daily ranking CSVs in `_daily/history/`. Not
committed: data anyone can re-fetch or rebuild in minutes. That covers Nasdaq
prices (`<T>/prices.json`), the Street block (`<T>/street.json`), live returns
(`<T>/live.json`), the built site data (`_daily/site/data/`, `index.json`,
`meta.json`, `state.json`), `_daily/latest.html`, `_daily/preview-*.html` and
the ~45 MB dated ranking attachments. The per-machine job health file
(`_system/run_health.json`) is not committed either. `.gitignore` lists them.

## Run it on your own computer

```
python -m pip install -r requirements.txt     # Windows only needs tzdata
python _system/refresh.py                     # Nasdaq prices + Street, live returns, the site
python -m http.server 8791 --directory _daily # then open http://localhost:8791/site/
```

`python _system/refresh.py --quick` refreshes prices and live returns only;
`--sec` also re-checks every name's SEC files; `--tickers APP,KR` limits the
per-company refreshes to those names (the site build still scans every scored
folder). `--attachment` also writes the dated ranking file
(`_daily/ranking-<date>.html`, plus `latest.html`) and the
`_daily/history/ranking-<date>.csv` — only the CSV is tracked. Tests: one Python suite by name, e.g.
`python _system/tests/test_engine_math.py`, and
`python _system/tests/test_build_site.py` (it also builds every committed folder once, ≈ 40 s — the
compatibility check of the site fields), and
`node _daily/site/tests/app.test.js`.

The APP folder is the worked example of the required output shape, including a
proper override. This repo is the live working tree itself — the sweep runs
in this clone, on `main` — so queue state and company outputs change as runs
complete. That scheduled run happens only in the canonical VM checkout; a
fresh clone elsewhere schedules nothing on its own.
