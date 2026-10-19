# IESC — IES Holdings, Inc.
**BLOCKED 2026-10-18 — NEEDS_MAIN_AGENT: shares.** No score emitted; no tier. The preliminary engine run (release 5.4.0) printed a Tier C on corrupted per-share figures — do not use it.

## The defect (share-basis family — same as DD in `_system/SHARE_BASIS_SPEC_DRAFT.md`)
IES announced a **2-for-1 forward stock split** in its Q3 FY2026 release (2026-07-31): record date 2026-08-14, distribution after the close 2026-08-21, split-adjusted trading from 2026-08-24 (OCC memo #59517, 2026-08-04). The split post-dates every filing the engine reads:

- FY2025 10-K diluted shares: **20,182,797** (pre-split) — `dcf_numbers.json` shares_diluted_latest
- Q3 FY2026 10-Q cover DEI outstanding: **19,924,356** as of 2026-07-27 (pre-split)
- ttm.py TTM shares (10-Q YTD weighted diluted): **20,186,894** (pre-split); Q3 FY26 diluted EPS as filed was $7.57, also pre-split basis
- Engine price **$251.96** (Nasdaq quote API, 2026-10-16 close) is **post-split**

So every per-share figure is overstated 2x: printed TTM OE/share $10.59 vs ~$5.29 on the post-split count (~40.37M diluted); printed market cap $5.09B vs ~$10.2B real (cross-check: external quote of $13.4B at $336.03 on 2026-10-06 implies ~39.9M shares). Still in scope under $40B either way — the corruption is in OE/share, IV and IRR, not scope.

## Why the worker cannot fix it in bounds
`shares_override` only fills periods where no diluted tag is filed; here a stale-basis tag *is* filed, so the override cannot replace it (verified on DD, 2026-10-16 — DD was blocked the same way). A `base_override` would need the 2x split factor, which is not a figure printed by this run's dcf_numbers.json / ttm.json / financials_history.csv, so it fails the "built exclusively from this run's outputs" rule. Per WORKER_SPEC step 8, anything outside bounded authority blocks as NEEDS_MAIN_AGENT.

## What the (corrupted) run showed, for the record
Preliminary run at pre-split share basis: normalized base OE/share $9.00 (median of last 3 FY), latest FY $10.20, TTM OE/share $10.59 (ttm.json legs: OCF $371,422,000 − capex $143,025,000 − SBC $14,648,000 = TTM OE $213,749,000). Flags printed: STALE_FY, OE_VOLATILE, WIDE_SCENARIO_SPREAD, TIER_BAND. On a corrected post-split base (~$5.29 TTM), the weighted IRR at $251.96 would land far below the printed 11.39% — the name needs a full re-run once share counts are on one basis, not a haircut of these numbers.

## Business context gathered before the block (for the re-run)
- Electrical/technology systems contractor; segments Communications, Infrastructure Solutions, Commercial & Industrial, Residential. Data-center work drove Q3 FY26: revenue $1,242.7M (+40% YoY), operating income $178.5M (+60%), backlog ~$4.5B (+91% since FY25 end); data-center-serving segments were 92% of segment operating income. Residential weak (revenue −6%, housing softness).
- Capex surge is real and guided: 9M FY26 capex $123.0M (+160% YoY); FY26 capex outlook raised to $145–160M for fabrication capacity (Infrastructure Solutions / Communications). FY25 capex was $67.3M.
- Acquisitions: Gulf Island Fabrication closed FY26; **DBM Global closed 2026-10-05 for ~$691M cash + stock** (largest to date; ~$1.5B TTM revenue, new "Structural" segment, ~4,000 employees, funded partly with borrowings + equity) — post-dates the TTM window; the re-run must treat it as a basis break and use post-deal share counts from the FY26 10-K / 8-K amendment.
- Balance sheet at Q3 FY26: no debt, $77.3M cash + $310.6M marketable securities (engine net debt −$127.2M on FY25 basis).

## Unblock condition
FY2026 10-K (FY ends 2026-09-30) restating share counts on the post-split basis, or the share-basis guard from SHARE_BASIS_SPEC_DRAFT.md shipping in the engine. Then re-run from scratch: TTM base, DBM as basis break, moat/scenarios still to be set.
