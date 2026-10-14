# Stocks

Repo going through 3000 stocks in russel using ai to give buy signals.

## What this is

A systematic owner's-earnings DCF sweep of ~2,617 US-listed companies under ~$40B
market cap (the reproducible equivalent of the Russell 3000 under $40B; the
official Russell list is licensed). Each company gets a filing-direct analysis
from SEC EDGAR data — no third-party financial data:

- Owner's earnings = operating cash flow − capex − stock-based compensation
  (conservative; SBC always treated as a real cost)
- Base = median of the last 3 fiscal years' OE/share, with a TTM override from
  10-Qs when the fiscal year is stale
- Five scenarios (super bear → super bull) with assigned probabilities; a
  justified 0–10 moat score drives how fast growth fades to a 2.5% terminal rate
- Headline = probability-weighted intrinsic value / IRR. Tiers at the owner's
  hurdles: **S ≥ 25%, A 20–25%, B 15–20%, C 10–15%, D < 10%, F = no positive
  normalized owner's earnings**

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
`ttm.py` (TTM from 10-Q YTD facts, saved to `ttm.json`), `make_score.py` (the
only writer of `score.json`; verifies the engine's content hash and refuses
pre-v5 or drifted inputs).

## Layout

- `_system/` — engine, tooling, method docs (`README.md` there is the full
  method + "Fixes & lessons"), the two external audits and responses under
  `audits/`, queue/universe state, and the overrides registry
- `<TICKER>/` — one folder per company: `financials_history.csv`,
  `dcf_numbers.json`, `analysis.md`, `score.json`, plus `judgment.json`,
  `key_numbers.md`, `ttm.json` where applicable
- `_daily/` — the daily ranking HTML (current + dated snapshots)
- `automation/` — the scheduled-job definitions that run the sweep (two pass-1
  workers every 15 minutes, a daily ranking; pass 2 is currently paused
  pending governance rules)

The APP folder is the worked example of the required output shape, including a
proper override. This repo is a snapshot mirror of the live working tree; the
sweep runs continuously, so queue state and company outputs move after each
push.
