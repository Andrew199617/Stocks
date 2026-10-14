# SMCI — Super Micro Computer, Inc.
v5 run, 2026-10-14. Market cap $24.99B at $35.83 (nasdaq_quote_api) — in scope under $40B.

All figures below are copied from dcf_numbers.json, key_numbers.md, or financials_history.csv — none are recomputed.

## What it is
AI server and rack-scale systems assembler: GPU server platforms, storage, and full rack / data-center building-block solutions built largely on Nvidia GPUs. Revenue is overwhelmingly hardware systems — FY2025 server and storage systems were ~97% of revenue per press coverage. The business buys scarce components, assembles and integrates them fast, and sells to hyperscalers and large AI customers at structurally thin margins.

## Owner's earnings
**FY2026 (10-K via EDGAR, from financials_history.csv):** revenue $39,063,072,000 (+77.79% YoY, latest rev YoY from dcf_numbers.json); net income $2,230,453,000; operating cash flow **−$6,809,886,000**; capex $161,999,000 (tag: PaymentsToAcquirePropertyPlantAndEquipment); SBC $412,115,000 (tag: ShareBasedCompensation).
- **Conservative owner's earnings FY2026: −$7,384,000,000 = −$10.59/share** (base_oe_latest_per_share −$10.5887).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): −$6,027,268,000 — also deeply negative; the two definitions agree, so the result is not a definition artifact.
- **Base used = the engine's normalized base (median of last 3 FY OE/share): −$4.72/share.** No TTM override: FY2026 ended 2026-06-30, ~3.5 months before this run, and no STALE_FY flag fired — the annual base is current. There is nothing to override toward in any case: the latest year is *worse* than the median (−$10.59 vs −$4.72), so no base choice rescues the DCF.
- OE history (conservative, from financials_history.csv): FY2023 +$572,354,000; FY2024 −$2,841,758,000; FY2025 +$1,217,858,000; FY2026 −$7,384,000,000. **OE positive in only 2 of the last 5 years** (dcf_numbers.json). The pattern is mechanical: in hypergrowth years the working-capital build (ΔNWC drag of $3,552,158,000 in FY2024 and $8,257,721,000 in FY2026) swallows net income whole; in slower years OCF recovers.
- Balance sheet: cash $7,521,474,000 and equity $14,479,452,000 at FY2026 (financials_history.csv). The engine reports net_debt_latest as null (recent-year debt tags are not populated in the pulled history), so no net-debt figure is quoted here rather than hand-computed. Press coverage reports the FY2026 working capital was funded in part by ~$5.6B of equity raised in Q4 FY2026 — consistent with the dilution flag below.

## Moat: 3/10 — weak
Justification: speed-to-market and rack-scale integration are real but replicable capabilities; the economics prove it — TTM gross margin ~10.8% (press figure) against hyperscaler customers with overwhelming bargaining power, single-source Nvidia GPU dependence, and Dell/HPE competing for the same racks. Nothing here has held pricing power through the cycle: gross margin fell from ~18% three years ago to ~10.8% TTM even as revenue went up ~5.5x.
- FOR: first-mover in direct liquid cooling and rack-scale integration; building-block architecture gives fast customization and time-to-first-deployment that matters to AI customers; scale and an early Nvidia allocation relationship; DCBBS (full data-center solutions) is a push into higher-margin work.
- AGAINST: commodity assembly economics — Dell and HPE sell the same capability and have won deals SMCI lost; extreme customer concentration (press reports one customer was 63% of revenue in Q2 FY2026); total dependence on Nvidia GPU supply, which Nvidia can steer toward larger OEMs; no proprietary silicon, software, or switching costs — customers multi-source; thin and falling gross margin through the strongest demand cycle in the industry's history.
- A 3 gives CAP = 5.9 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 5.9 years, 15-year projection. (Moot here — there is no positive base to fade.)

## DCF — v5 final run (2026-10-14)
Final pass: `--moat 3 --probs 0.10,0.25,0.30,0.25,0.10`, default offsets (−12/−5/0/+5/+12pp) and multipliers (0.75/0.90/1.00/1.10/1.25). The engine emits **no scenario IVs or IRRs**: the normalized base OE is negative (−$4.72/share), so an owner's-earnings DCF is not supportable on numbers alone (engine note, dcf_numbers.json).

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | n/a | 0.75 | WC build continues; margins stay in single digits | not emitted — negative base | not emitted |
| Bear | 25% | n/a | 0.90 | Growth slows but cash conversion stays broken | not emitted — negative base | not emitted |
| Base | 30% | n/a | 1.00 | FY26 pattern repeats: NI positive, OCF negative | not emitted — negative base | not emitted |
| Bull | 25% | n/a | 1.10 | Q4 FY26 margin print holds; WC intensity falls | not emitted — negative base | not emitted |
| Super bull | 10% | n/a | 1.25 | FY27 guide ($65–72B) lands at durable mid-teens margins | not emitted — negative base | not emitted |

- **Probability-weighted IV/IRR: none — Tier F by numbers.** Sanity check on the growth inputs, for the record: the engine's blended growth is 76.32% (rev CAGR 3y) with revenue prints of +77.79% (FY2026) and Q4 FY2026 +93% YoY, plus an FY2027 revenue guide of $65–72B from press coverage — growth is not the problem and no scenario start would be below recent prints. The problem is entirely cash conversion: at ~$0.65 of working capital consumed per incremental revenue dollar (press estimate), growth itself destroys owner's earnings on the conservative definition.

## Flags — every fragility flag resolved
- **DILUTION** (share count +7.6%/yr, already deducted via the −5pp growth adjustment): confirmed and worsening — SBC rose from $54,433,000 (FY2023) to $231,507,000 (FY2024) to $314,452,000 (FY2025) to $412,115,000 (FY2026) in financials_history.csv, and diluted shares reached 697,348,000. On top of SBC, press coverage reports ~$5.6B of equity raised in Q4 FY2026 alone to fund working capital. Dilution here is structural funding of the WC model, not a one-off.
- **BASIS_BREAK_SUSPECT** (>60% revenue jump in the last 5 years): resolved — organic, not a break. No divestiture, big M&A, or restatement drives it: revenue went $7,123,482,000 (FY2023) → $14,989,251,000 (FY2024) → $21,972,042,000 (FY2025) → $39,063,072,000 (FY2026) on AI data-center demand. The 2024 filing-delay episode ended with an independent committee review requiring no restatements (press coverage). The CAGRs (5y 61.49%, 3y 76.32%) are real demand growth — but they must not be trusted as *value* growth, because the same growth is what makes OE negative.
- **NI_OCF_DIVERGENCE** (2024, 2026): resolved — working-capital swings, both years. FY2024: NI $1,152,666,000 vs OCF −$2,485,972,000 with a $3,552,158,000 ΔNWC drag. FY2026: NI $2,230,453,000 vs OCF −$6,809,886,000 with an $8,257,721,000 ΔNWC drag (inventory reported at $12.90B and receivables up ~176% YoY in press coverage of Q4 FY2026). Not tax deposits or impairments — it is inventory and receivables pre-funding the backlog. This is exactly why the OCF-based conservative OE is the right series and the NI-based story is not.

## My thoughts / overlay
- The bull case is a cash-conversion case, not a growth case: Q4 FY2026 OCF turned positive (+$747M per press coverage, after −$6.6B in Q3) and gross margin printed 17.5% — but management attributed ~25% of that margin jump to one-off tariff/inventory-reserve benefits and guided Q1 FY2027 gross margin back to 10.4–10.8%. Even the good quarter does not yet show a durable fix.
- Governance overhang is real and unresolved: 2024 Hindenburg allegations, EY resigning as auditor, DOJ/SEC subpoenas, material weaknesses in internal controls, a 2020 SEC settlement in the company's past. Filings are current again (BDO, Nasdaq compliance regained Feb 2025, no restatements) — but "the numbers are filed" is a lower bar than "the numbers are trusted," and the stock's discount reflects it.
- Method range: there is no defensible OE-DCF range to report — every base (latest FY −$10.59, median −$4.72, maintenance definition −$6,027,268,000 total) is negative. A price that clears 15% cannot be computed from owner's earnings that don't exist; the honest statement is that SMCI only clears any hurdle if working-capital intensity collapses toward zero while mid-teens margins hold — neither is in the filed numbers yet.
- What would change this: two or three consecutive quarters of positive OCF at guided growth, with gross margin holding above ~13% without one-off help. Watch Q1 FY2027 (already ended, results pending per press coverage).

## Final verdict
- **Final tier: F** (no positive normalized owner's earnings — weighted IRR not computable; OE positive in only 2 of the last 5 years and FY2026, the biggest revenue year ever, produced the worst OE in the series)
- Confidence: **Low** (the F is arithmetically solid on filed numbers, but the forward story is genuinely binary on cash conversion — a real fix would move this name fast, in either direction)
- One-liner: AI rack assembler with a weak 3/10 moat whose hypergrowth consumes cash — FY2026 net income $2.23B but owner's earnings −$7.38B; Tier F, no hurdle-clearing price exists on filed numbers until working capital converts.
