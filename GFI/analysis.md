# Gold Fields Limited (GFI) — NOT SCORED — NEEDS_MAIN_AGENT escalation

Date: 2026-10-14 (v5 sweep run). Status: blocked via queue.py, no tier emitted.
Do not use the preliminary engine numbers below as a valuation — they are on a 2015 base.

## What it is
South African gold miner (NYSE/JSE: GFI), 20-F filer reporting under IFRS in USD.
Nine mines across Australia, South Africa, Ghana, Peru and Chile plus the Windfall
project in Canada (per its FY2025 20-F summary). Attributable gold-equivalent
production 2,438koz in 2025, all-in costs US$1,927/oz, adjusted free cash flow
US$2,970m in 2025 (search-cited FY2025 results, released 19 Feb 2026: revenue
US$8,751m in 2025 vs US$5,202m in 2024; profit attributable to owners
US$3,567.4m / US$3.99 per share in 2025 vs US$1,245.0m / US$1.39 in 2024;
net debt US$1,442m at end-2025). None of those current figures are in the
engine's outputs — see below — so none were used to score it.

## Why it cannot be scored in this run (bounded-authority limit)
- Preliminary engine run (dcf_engine.py GFI) exited 0 with no data_gap, but its
  history ends at latest_period_end 2015-12-31 (financials_history.csv, 2007–2015
  only). Verified directly: the SEC us-gaap OCF concept for CIK 1172724 also ends
  2015-12-31. Gold Fields has reported under IFRS since then; the engine reads
  only us-gaap tags, so FY2023–FY2025 OCF / capex / SBC / diluted shares are
  simply not in this run's code outputs.
- ttm.py GFI exited 3: "cannot compute TTM for GFI (CIK 1172724): ocf: no annual
  (FY) fact; sbc: no annual (FY) fact; shares_diluted: no annual (FY) fact;
  capex: no capex facts in companyfacts under any candidate tag" — same cause.
- A current base_override would have to be built from the FY2025 20-F financial
  statements (web/filing figures), not exclusively from this run's
  dcf_numbers.json / ttm.json / financials_history.csv. That is outside the
  bounded authority in step 8(c) — so it escalates, it is not declared here.
- Scoring on the engine's stale base would be false: base_oe_per_share
  $0.17448421387195884 (median of last 3 FY in the engine dataset, i.e. 2013–2015),
  price $35.285, preliminary weighted IV@15% $1.4531472487402994, weighted IRR
  0.030219249494869385, tier_by_numbers D — all artefacts of the 2015 base, not
  of the 2025 business described above.

## ADS ratio — sourced, but not sufficient to unblock
The FY2025 Form 20-F cover (filed 30 March 2026, for fiscal year ended
31 December 2025) lists the registered security as American Depositary Shares,
each representing one ordinary share — i.e. ratio 1.0. That satisfies the
step 8(d) sourcing test on its own, but with ratio 1.0 it changes no per-share
figure, and it does not cure the IFRS history gap above. No judgment.json was
written and make_score.py was not run, deliberately: a score.json built on the
2015 base must not ship.

## Fragility flags from the preliminary run — resolution
- STALE_FY (129 months since FY end): CONFIRMED and decisive — see above;
  ttm.py attempted and failed (quoted above); no TTM base available.
- ADS_RATIO_MISSING: resolved as a fact (1:1, 20-F cover above), not as a fix.
- OE_VOLATILE / NI_OCF_DIVERGENCE (2013, 2014, 2015) / LOW_OE_YIELD (0.5%) /
  WIDE_SCENARIO_SPREAD (4.4x) / HIGH_NET_DEBT (10.3x normalized OE): all are
  computed on the 2013–2015 dataset and are not meaningful for the current
  company; they must be re-derived once an IFRS-capable history exists, not
  waved off or carried forward.

## What the main agent needs to decide
An IFRS path for GFI (and IFRS 20-F filers generally — the parked IFRS
go/no-go): either (1) authorise a filing-sourced base_override from the FY2025
20-F statements as a main-agent decision, with full construction, or
(2) an engine fix to read ifrs-full facts, or (3) leave GFI blocked_data_gap /
not-modeled until that build exists. Until then: no tier.
