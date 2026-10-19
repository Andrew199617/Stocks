# RMBS — Rambus Inc.
Engine 5.4.0 pass-1 run, 2026-10-18. Price $87.25 (nasdaq_quote_api), market cap (est) $9.531B — in scope under $40B.

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.json, financials_history.csv, or fundamentals.json — none are recomputed.

## What it is
Provider of memory-interface chips and silicon IP for data-center / AI servers: DDR5 registered clock drivers (RCDs) and companion chips for server memory modules, plus royalty / licensing and contract IP revenue (HBM, PCIe, CXL, security IP). Q2 2026 (press release, July 27, 2026): record quarterly revenue of $207.4 million, up 20% year over year, product revenue $99.2 million, royalties $84.2 million, contract and other $24.0 million, cash from operating activities $61.2 million in the quarter.

## Owner's earnings
**FY2025 (10-K via EDGAR, financials_history.csv):** revenue $707,630,000 (+27.13% latest rev YoY per key_numbers.md), operating cash flow $360,019,000; capex $26,842,000; SBC $54,267,000 (always a real cost — 15.1% of FY2025 operating cash flow per fundamentals.json).
- **Conservative owner's earnings FY2025: $278,910,000 = $2.55/share** (latest FY OE/share, key_numbers.md).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $53,706,000 in financials_history.csv — far below the conservative figure because it is charged with a very large working-capital swing (delta_nwc $176,749,000); the OCF-based conservative figure is the cleaner base here.
- OE positive 5 of the last 5 fiscal years. Shares diluted (latest): 109,235,000; share count CAGR −0.07% — essentially flat, no buyback tailwind and no dilution problem.

**Base used = TTM owner's earnings through Q1 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $360,019,000 − prior YTD $77,414,000 + current YTD $83,209,000 = **TTM $365,814,000**
- Capex: FY $26,842,000 − prior YTD $7,872,000 + current YTD $11,635,000 = **TTM $30,605,000**
- SBC: FY $54,267,000 − prior YTD $11,383,000 + current YTD $11,453,000 = **TTM $54,337,000**
- Shares (current-YTD weighted diluted): **109,716,000**
- **TTM OE total $280,872,000 → base OE/share $2.56** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $1.42/share — rejected as the base; see BASE_DIVERGENCE below. It is still reported in key_numbers.md.
- Data caveat: the TTM legs stop at 2026-03-31 because the Q2 2026 10-Q (filed 2026-07-28, period 2026-06-30) is not yet in EDGAR companyfacts (fundamentals.json warning). The Q2 2026 press release figures quoted above (revenue +20% YoY, quarterly OCF $61.2 million) are consistent with the TTM base level, not a step-change from it. Enrichment note: segments.py found dimensioned facts but no axis with two members for the same concept, so segments.json carries no usable segment breakdown — non-blocking, the score does not use it.

## Moat: 6/10 — moderate-strong niche moat, not wide
Justification: roughly 40% share of DDR5 RCDs in a three-player oligopoly, a deep patent/IP portfolio, and module-qualification switching costs — but high ROIC is recent, not cycle-proven.
- FOR: ~40% share of DDR5 RCDs in a three-player oligopoly (Rambus / Renesas / Montage) — every DDR5 server module needs an RCD; patent and silicon-IP portfolio generating high-margin royalty and licensing revenue, consolidated gross margin 79.6% in FY2025 (gross margin held 75.3–80.2% across FY2020–25 in fundamentals.json); qualification / design-in switching costs at DRAM makers and module vendors, standards and signal-integrity expertise at high data rates; debt-free balance sheet and rising returns — roic_proxy 12.9% → 16.1% → 18.0% over FY2023–25.
- AGAINST: narrow niche TAM — one product family drives the story and DDR generation / form-factor transitions reset share; Montage and Renesas contest the same RCD sockets while Synopsys / Cadence bundle competing IP with EDA; customer and end-market concentration in the server DRAM cycle and AI data-center capex; high ROIC is recent (roic_proxy was −4.4% in 2020, 2.5% in 2021, 9.3% in 2022 — not proven through a downcycle, which is why this is 6 and not 7+); SBC is a persistent real cost ($54,267,000 in FY2025).
- A 6 gives CAP = 9.8 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 9.8 years, 15-year projection.

## DCF — final run (2026-10-18)
Growth recalibration (written reason): the engine's blended growth is 25.39%, but one blend component — OE/share CAGR 2y of 48.96% — is a step-up artifact off the depressed FY2023 OE/share, and the most recent prints have decelerated to ~20%: TTM revenue +19.1% YoY (fundamentals.json TTM through 2026-03-31) and Q2 2026 revenue +20% year over year. Applying 25.39% growth on top of the already-stepped-up TTM base of $2.56/share would double-count the step-up. Scenario starts were therefore set via offsets (−0.174 / −0.114 / −0.054 / +0.006 / +0.066 vs the blended g_base) to 8 / 14 / **20** / 26 / 32%. The base start (20.0%) matches the latest prints; the bull start (26.0%) is roughly the FY2025 revenue pace (+27.13%) and the super-bull start (32.0%) requires a written reason — it assumes DDR5 Gen 3 / MRDIMM content gains re-accelerate growth beyond anything printed in 2026 so far, and it is weighted at only 10%. Probabilities 10/25/30/25/10; OE multipliers 0.75/0.90/1.00/1.10/1.25 (defaults).

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | 8.0% | 0.75 | Server DRAM cycle turns; share loss to Montage / Renesas | $20.10 | 5.57% |
| Bear | 25% | 14.0% | 0.90 | Growth halves from current prints and stays there | $31.47 | 7.46% |
| Base | 30% | 20.0% | 1.00 | Current ~20% print pace decays normally over the CAP | $45.56 | 9.66% |
| Bull | 25% | 26.0% | 1.10 | FY2025 pace resumes on Gen 3 RCD / companion-chip content | $65.13 | 12.37% |
| Super bull | 10% | 32.0% | 1.25 | Re-acceleration: MRDIMM + IP attach compound for years | $95.88 | 15.93% |

- **Probability-weighted: IV@15% $49.42 (−43.4% vs price), IV@12% $68.76 (−21.2%), IV@10% $90.76, weighted IRR 10.26%, base-case IRR 9.66%**
- **Tier by numbers: C.** Diagnostics (key_numbers.md): OE yield 2.93%, terminal value 23.6% of IV@15%, scenario spread 4.77x, 9.6 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (latest fiscal year ended 10 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q1 2026, quoted above; the Q2 2026 10-Q is filed but not yet in EDGAR companyfacts, and its press-release figures are consistent with the TTM level.
- **NI_OCF_DIVERGENCE** (2023): net income of $333,904,000 vs operating cash flow of $195,786,000 in FY2023 (financials_history.csv). The one-off is non-cash and non-operating: a $149.4 million discrete tax benefit in Q2 2023 from releasing the valuation allowance on U.S. deferred tax assets (FY2023 tax line: −$146,744,000), with a divestiture gain also in that year's non-GAAP reconciliation. The OCF-based conservative OE used throughout is unaffected by either item.
- **DEBT_TAGS_BLANK** (no debt tag reports for the latest fiscal year — net debt UNKNOWN from the engine): stated from the filing history instead — FY2025 (financials_history.csv / fundamentals.json): cash $182,822,000, total liabilities $165,120,000, equity $1,364,425,000, total assets $1,529,545,000, lease liabilities $24,981,000, and no debt tag in any filed year. The balance sheet is effectively debt-free; the Q2 2026 press release reported cash, cash equivalents and marketable securities of $824.9 million as of June 30, 2026. There is no leverage verdict to make — there is no debt.
- **BASE_DIVERGENCE** (latest FY OE/share $2.55 vs 3-yr median $1.42): the median is the distorted one — it is the FY2024 figure and averages in FY2023's $1.15/share, when OCF dipped even as reported net income was inflated by the tax item above. The latest level is confirmed twice over: FY2025 OE/share $2.55 on revenue +27.13% and TTM OE/share $2.56 with TTM revenue +19.1% YoY. TTM base used; the step-up is handled by recalibrating growth down (see DCF section) rather than by keeping a stale base.
- **WIDE_SCENARIO_SPREAD** (super-bull IV is 4.8x super-bear IV): real — the outcome range IS wide because the price capitalizes the bull path. Confidence is capped at medium, and the verdict is sized to the conservative end.
- **TIER_BAND** (bear-case tier D at 7.46% vs bull-case tier C at 12.37%): the verdict spans tiers; any position sizing should use the bear end (Tier D, IV@15% $31.47).

## My thoughts / overlay
- The honest headline is the method range: the preliminary run on the engine's normalized median base ($1.42/share, default growth) printed weighted IRR 7.73% and IV@15% $31.57 (Tier D); the final run on the filing-confirmed TTM base with growth recalibrated to current prints prints 10.26% / $49.42 (Tier C). Both defensible runs sit far below the $87.25 price — the disagreement is about how overvalued, not whether.
- Quality is not the debate: OE positive 5/5 years, gross margin ~80%, no debt, SBC contained at 15.1% of OCF and already charged in full in the base.
- What the price requires: at $87.25 the market is paying above even the bull case's IV@15% ($65.13) and close to the super-bull's ($95.88) — i.e., it needs the 10%-weighted path, sustained, to clear 15%.
- Risks: server DRAM / AI capex cyclicality, RCD share fights at each DDR generation transition, customer concentration, and a valuation that leaves no room for a single soft year.

## Final verdict
- **Final tier: C** (weighted IRR 10.26% on the final inputs; method range D to C; bear case is D — size to the bear end)
- Confidence: **Medium**
- One-liner: High-quality, debt-free memory-interface/IP franchise, moat 6/10 — at $87.25 it does not clear 15% (weighted IRR 10.3%, weighted IV@15% $49.42); it clears the 15% hurdle only at or below $49.42.
