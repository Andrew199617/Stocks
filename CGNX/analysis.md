# CGNX — Cognex Corporation
Engine 5.4 run, 2026-10-19. Price $53.99 (nasdaq_quote_api), market cap $9,144,124,330 — in scope under $40B. All figures below are copied from key_numbers.md or the run's other generated outputs (dcf_numbers.json, ttm.json, financials_history.csv, statements.json, fundamentals.json) — none are recomputed.

## What it is
The global leader in industrial machine vision: cameras, barcode readers, deep-learning vision software and the new OneVision AI platform, sold into factory automation, logistics and consumer-electronics manufacturing. Asset-light and debt-free. Cyclical: revenue fell from $1,006,090,000 (2022) to $837,547,000 (2023) in the post-COVID automation downturn, then recovered to $994,359,000 in FY2025; Q2 2026 printed record revenue of $291 million, +17% year over year, with a 29.4% operating margin (company Q2 2026 release), and full-year 2026 guidance is $1.13–1.15B of revenue.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $245,514,000; capex $8,743,000; SBC $48,517,000 (always a real cost).
- **Conservative owner's earnings FY2025: $188,254,000 = $1.11/share** (base_oe_latest_per_share $1.1115)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $133,111,000 total — lower than the conservative figure, mainly because ΔNWC and the tax-deposit timing sit differently; the OCF-based conservative figure is the one used throughout.
- OE positive 5 of the last 5 fiscal years. FY2025 buybacks $151,233,000 and dividends paid $54,627,000 (fundamentals.json); diluted share count has shrunk ~1.06%/yr (share_cagr −1.0597%), already credited in the growth blend.

**Base used = TTM owner's earnings through Q2 2026 (period ended 2026-07-05), from ttm.py (filing-direct, no hand math):**
- OCF: FY $245,514,000 − prior YTD $83,127,000 + current YTD $114,246,000 = **TTM $276,633,000**
- Capex: FY $8,743,000 − prior YTD $4,695,000 + current YTD $4,289,000 = **TTM $8,337,000**
- SBC: FY $48,517,000 − prior YTD $22,233,000 + current YTD $23,145,000 = **TTM $49,429,000**
- Shares (current-YTD weighted diluted): **169,166,000**
- **TTM OE total $218,867,000 → base OE/share $1.2938** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $0.4727/share — rejected as the base: it is the median of a cyclical trough (FY2023 $0.2023, FY2024 $0.4727, FY2025 $1.1115). It is still reported in key_numbers.md; replaying this run's final scenario configuration on that base (same probabilities, offsets, multipliers and moat — engine --measure, verified 2026-10-19) gives a weighted IV@15% of $5.63 and a 3.96% weighted IRR, so the method range is D on either base — the TTM base is the generous end. (The preliminary default-scenario run printed $5.11 / 3.79%; the gap between that and $5.63 / 3.96% is scenario calibration, not the base choice.)
- TTM caveats, stated plainly: the TTM window contains two non-repeating tailwinds inside OCF — a one-time commercial-partnership benefit in 2025 (reported FY2025 revenue $994M vs $982M excluding it, per the company's Q4 2025 call) and a working-capital release (management: cash conversion cycle improved 57 days in 2025). Both flatter the TTM base; they are handled by the widened bear weight and the 0.75/0.90 bear-end OE multipliers, not by adjusting the filed figures.

## Moat: 5/10 — moderate/narrow, a leader in a contested niche
Evidence first (fundamentals.json): gross margin 75.6% (2017), 73.8% (2019), 74.5% (2020), 73.3% (2021), 71.8% (2022), 71.8% (2023), 68.4% (2024), 66.9% (2025) — a near-decade of erosion. ROIC proxy: 16.2% (2020), 22.2% (2021), 16.8% (2022), then 8.4% (2023), 7.0% (2024), 8.3% (2025) — three trough years at or below a plausible cost of capital. That record supports a mid-pack score, not a wide-moat one, even though Q2 2026 (29.4% operating margin) shows what the franchise earns mid-recovery.
- FOR: global leadership in industrial machine vision — installed base, application know-how and brand with automation OEMs and end users; historically premium gross margins (72–76% through 2022) evidencing real pricing power; asset-light cost structure (FY2025 capex $8,743,000 on $994,359,000 of revenue) with no debt; OneVision AI platform and software attach extending the franchise into AI-enabled inspection.
- AGAINST: gross margin has eroded ~9 points from the 2017 peak to 66.9% in 2025 — pricing and mix pressure is measured, not hypothetical; ROIC proxy fell from 22.2% (2021) to 7–8% in 2023–25; Keyence and low-cost Asian rivals (e.g. Hikrobot) contest the same budgets; end markets are cyclical factory/logistics capex — OE/share fell to $0.2023 in 2023; demand concentrates in consumer-electronics and logistics capex cycles.
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — engine 5.4 final run (2026-10-19)
Growth recalibration (written reason): the engine's blended growth is 7.51%, but the blend is a median dragged down by trough-window CAGRs (rev CAGR 3y −0.39%, 5y +4.16%) while a second component (OE/share CAGR 2y +134.29%) is a trough-base artifact. The prints that mean something: FY2025 revenue +8.73% YoY (latest rev YoY), Q2 2026 revenue +17% YoY, and FY2026 guidance of $1.13–1.15B (+14–16% vs FY2025). The base-case start was therefore set to 13.0% via offsets (−12.51 / −4.51 / +5.49 / +9.49 / +14.49pp vs the blend) — below the current +17% print and the guidance midpoint, because the TTM base already contains the non-repeating tailwinds noted above. Probabilities 15/25/30/20/10 (bear weight widened for OE_VOLATILE); OE multipliers at the defaults 0.75/0.90/1.00/1.10/1.25. Price $53.99.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | −5.0% | 0.75 | Automation capex rolls over again as in 2023; margin gains reverse | $5.81 | 3.71% |
| Bear | 25% | +3.0% | 0.90 | Recovery stalls at low-single-digit growth; WC tailwind unwinds | $9.75 | 4.77% |
| Base | 30% | +13.0% | 1.00 | Guidance-like growth near term, fading over the 8.5-yr CAP | $16.37 | 6.61% |
| Bull | 20% | +17.0% | 1.10 | Q2 2026 momentum holds; OneVision broadens the customer base | $21.19 | 7.87% |
| Super bull | 10% | +22.0% | 1.25 | Sustained AI-inspection supercycle at expanding margins | $29.45 | 9.89% |

- **Probability-weighted: IV@15% $15.40 (−71.5% vs price), IV@12% $20.79, IV@10% $26.85, IV@20% $10.60, IV@25% $8.00, weighted IRR 6.38%, base-case IRR 6.61%**
- **Tier by numbers: D** (bear D, bull D — the whole band is D). Diagnostics (dcf_numbers.json): OE yield 2.40%, terminal value 20.4% of IV@15%, scenario spread 5.07x, 9.59 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (latest FY ended 9.59 months ago): resolved by construction — the base is the TTM figure from ttm.py through the Q2 2026 period ended 2026-07-05 (10-Q filed 2026-08-06), quoted above.
- **BASE_DIVERGENCE** (latest FY $1.1115 vs 3-yr median $0.4727): the median is the distorted one — it is built from the 2023–24 downturn (OE/share $0.2023 / $0.4727 on revenue of $837,547,000 / $914,515,000). The cash-flow line that makes the median distorted is operating cash flow itself: FY2023 OCF fell to $112,916,000 from $243,406,000 in FY2022 as net income fell to $113,234,000 on the revenue trough, and FY2024 OCF was still only $149,081,000 (net income $106,171,000). There is no one-off item inside either year — both years' OE is low because OCF collapsed with earnings, so the median capitalizes a trough, not a run rate. The latest FY and TTM figures are corroborated by the recovery prints (Q2 2026 revenue +17% YoY, operating margin 29.4%). TTM base used; median retained in the reporting and in the method range above.
- **NI_OCF_DIVERGENCE** (2025 NI $114,442,000 vs OCF $245,514,000): NI was depressed by a discrete tax expense of $33,650,000 in Q3 2025 (company Q3 2025 presentation; that quarter's GAAP tax rate was 71.9%) and a $13M excess-and-obsolescence inventory charge (Q4 2025 call), while OCF added back non-cash SBC $48,517,000, D&A $20,289,000 and +$39,697,000 of deferred income taxes (vs −$20,010,000 in 2024, per statements.json). The OE series used throughout is OCF-based, so the divergence does not contaminate the base — but the same working-capital/tax timing that lifts OCF is why the base is not extrapolated naively (see TTM caveats).
- **DEBT_TAGS_BLANK** (no debt tag for the latest FY): stated from the filing via fundamentals.json — Cognex reports no borrowings in any year of the history. FY2025 balance sheet: cash $262,925,000 plus short-term investments $74,037,000, total liabilities $524,654,000, equity $1,491,901,000, operating lease liabilities $76,586,000. The blank is a genuine zero-debt balance sheet (net cash), not missing leverage data; the engine's null net debt is a tagging artifact.
- **OE_VOLATILE** (OE/share range >3x over 5 years): real cyclicality — $1.4164 (2021) → $0.2023 (2023) → $1.2938 TTM. Handled with 40% probability on bear-or-worse scenarios and the 0.75/0.90 bear-end multipliers.
- **WIDE_SCENARIO_SPREAD** (5.07x): real — the outcome range for a cyclical at a recovery inflection is wide. Confidence is capped at medium and the verdict is sized to the conservative end; note even the super-bull IV@15% ($29.45) sits far below the $53.99 price, so the spread does not change the verdict.
- Preliminary-run flags **IRR_AT_FLOOR** and **LOW_OE_YIELD** were artifacts of the trough-median base ($0.4727); on the TTM base the OE yield is 2.40% and no scenario sits at the solver floor (super-bear IRR 3.71%).

## My thoughts / overlay
- This is a quality business priced for a flawless decade. At $53.99 the market is paying for sustained mid-teens-plus growth with expanding margins; the model — run on the generous TTM base, with a base-case start set near guidance — returns a 6.38% weighted IRR. Even the super-bull case (22% growth start, 1.25x OE) yields only a 9.89% IRR and a $29.45 IV@15%.
- The method range is unusually honest here: trough-median base → weighted IV@15% $5.63 (same final scenario configuration); TTM base → $15.40. Both are Tier D and both are less than a third of the price. The disagreement is about how bad, not about whether.
- What would change the answer: several years of the Q2 2026 pattern (record revenue, ~29% operating margins) compounding OE/share well past the super-bull path, or a price near the hurdle levels — the stock clears 15% only at or below $15.40, 20% at or below $10.60, 25% at or below $8.00.
- Balance-sheet risk is not the story: no debt, cash of $262,925,000 plus short-term investments of $74,037,000, and OE positive in all of the last 5 years. The risk is purely the entry price against a cyclical earnings stream whose gross margin has been eroding for most of a decade.

## Final verdict
- **Final tier: D** (weighted IRR 6.38% on the TTM base; bear and bull cases are also D)
- Confidence: **Medium** (high on the filing-derived OE legs and the debt-free balance sheet; the scenario spread is 5.07x and the TTM base carries the two stated tailwinds)
- One-liner: Debt-free machine-vision leader, moat 5/10, in a genuine recovery — but at $53.99 the weighted IRR is 6.4% (IV@15% $15.40); it clears 15% only below ~$15.40.
