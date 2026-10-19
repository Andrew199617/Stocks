# GPC — Genuine Parts Company
Engine 5.4.0 run, 2026-10-16. Price $134.63 (nasdaq_quote_api). Market cap est. $18,747,227,500. In scope under $40B.

All figures below are copied from dcf_numbers.json, ttm.json, financials_history.csv, or fundamentals.json — none are recomputed.

## What it is
Global distributor of automotive replacement parts (NAPA, ~two-thirds of sales, North America / Europe / Australasia, mostly professional installers) and industrial parts (Motion, ~one-third, higher margin). Announced in Feb 2026 a separation of the Automotive and Industrial businesses into two public companies, targeted Q1 2027. Dividend raised for the 69th consecutive year in 2025; TTM DPS $4.185 (fundamentals.json).

## Owner's earnings
**FY2025 (10-K via EDGAR, financials_history.csv):** operating cash flow $890,762,000; capex $469,838,000; SBC $48,847,000.
- **Conservative owner's earnings FY2025: $372,077,000 = $2.67/share** (base_oe_latest_per_share $2.6720071813285458)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $681,493,000 — well above the conservative figure because FY2025 net income was crushed by non-cash charges (see NI_OCF_DIVERGENCE below) that the maintenance formula adds back differently; the OCF-based conservative series is the one used throughout.
- OE positive 5 of the last 5 fiscal years. Net debt $4,318,572,000 (basis LongTermDebtNoncurrent+LongTermDebtCurrent+ShortTermBorrowings), plus lease liabilities $2,134,014,000 not in that net-debt basis.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $890,762,000 − prior YTD $169,115,000 + current YTD $464,114,000 = **TTM $1,185,761,000**
- Capex: FY $469,838,000 − prior YTD $248,822,000 + current YTD $205,391,000 = **TTM $426,407,000**
- SBC: FY $48,847,000 − prior YTD $24,180,000 + current YTD $29,698,000 = **TTM $54,365,000**
- Shares (current-YTD weighted diluted): **138,017,000**
- **TTM OE total $704,989,000 → base OE/share $5.11** (base_oe_per_share $5.107986697290913, base_source: ttm_json)
- The engine's normalized base (3-yr median) is $4.61/share (base_oe_normalized_per_share $4.605276723705878) — not used as the base because the TTM figure is more current and already reflects the post-charge run rate; the median is retained in the reporting. Either base produces Tier D at this price, so the choice does not drive the verdict.

## Moat: 5/10 — moderate / narrow
Justification: a real distribution-density moat in professional auto parts and a leading industrial distributor, but mid-single-digit share of a fragmented aftermarket, structurally lower margins than O'Reilly/AutoZone, and no measured ROIC history in the filed series that supports a wide-moat claim.
- FOR: distribution density — ~10,840 locations incl. ~190 distribution centers placing inventory near professional demand, where speed and assortment decide the sale; NAPA brand and long supplier relationships; Motion's technical-service position in industrial MRO; scale purchasing across $24,301,141,000 of FY2025 revenue; gross margin expanding every year in the series — 35.2% (2021), 35.0% (2022), 35.9% (2023), 36.3% (2024), 36.8% (2025) — evidence of some pricing/mix power.
- AGAINST: ROIC evidence is thin and not wide-moat grade — fundamentals.json's roic_proxy series is only populated for 2016–2018 (20.6% / 12.1% / 17.2%) because the operating-income tag drops out of the captured series after 2018, so there is no filed ROIC run here showing sustained well-above-cost-of-capital returns through a cycle; North America Automotive EBITDA margin runs ~7–8% vs >20% at the best peers; competition from O'Reilly, AutoZone, Advance, RockAuto and Amazon; a large share of NAPA stores are independently owned, limiting control; EV adoption shrinks the moving-parts count over time; the planned separation adds execution and dis-synergy risk.
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — 5.4 final run (2026-10-16)
Growth sanity check: the engine blend is 4.07% (rev CAGR 5y 8.00%, 3y 3.22%, latest YoY 3.46%, OE/share CAGR 2y −34.00%). Actual recent prints: FY2025 revenue +3.46%, TTM revenue +5.47% YoY (fundamentals.json TTM), Q2 2026 sales +6.0% YoY, and management's reaffirmed 2026 guidance is total sales growth of 3% to 5.5% with adjusted EPS $7.50–$8.00. The default super-bull start (16.07%) was recalibrated down — nothing GPC has printed supports it. Offsets used −0.10 / −0.04 / 0.00 / +0.03 / +0.07, giving starts of −5.93% / 0.07% / **4.07%** / 7.07% / 11.07%. Even the bull start (7.07%) sits only modestly above the latest +6.0% print, justified by restructuring savings and separation focus; the base start sits inside the guidance range. Probabilities at the defaults 10/25/30/25/10; OE multipliers 0.75/0.90/1.00/1.10/1.25. Price $134.63.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -5.93% | 0.75 | Aftermarket softens, separation stumbles, leverage bites | $22.07 | 4.34% |
| Bear | 25% | 0.07% | 0.90 | Flat OE, SG&A inflation deleverage persists | $34.06 | 5.58% |
| Base | 30% | 4.07% | 1.00 | Guidance-range growth decays over the CAP | $44.71 | 6.71% |
| Bull | 25% | 7.07% | 1.10 | Restructuring savings + Industrial strength carry OE | $55.69 | 7.84% |
| Super bull | 10% | 11.07% | 1.25 | Separation unlocks both units, OE compounds double-digit | $74.62 | 9.71% |

- **Probability-weighted: IV@15% $45.52 (−66.2% vs price), IV@12% $60.26, IV@10% $76.68, weighted IRR 6.81%, base-case IRR 6.71%**
- **Tier by numbers: D.** Bear tier D, bull tier D — no TIER_BAND issue. Diagnostics: OE yield 3.79%, terminal value 18.4% of IV@15%, scenario spread 3.38x, net debt 6.07x normalized OE, 9.49 months since FY end.
- Hurdle-clearing prices: 15% at $45.52, 20% at $32.24, 25% at $24.90. Even the super-bull IV@15% ($74.62) is far below the $134.63 price.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.49 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, legs quoted above.
- **NI_OCF_DIVERGENCE** (2025 NI $65,945,000 vs OCF $890,762,000): the one-offs are identified — a $742M non-cash U.S. pension-plan settlement/termination charge in Q4 2025, an ~$150M credit loss on receivables from the First Brands Group bankruptcy, and a $103M asbestos-liability remeasurement; total Q4 pre-tax adjustments ~$1.1B. These crush net income but are largely non-cash, which is why the OCF-based conservative OE is the series used and the maintenance (NI-based) figure is not trusted as the base.
- **CASH_INCLUDES_RESTRICTED**: the FY2025 cash figure in financials_history.csv ($477,179,000) is filed only under the combined cash + restricted-cash tag with no separate restricted-cash tag, so net debt of $4,318,572,000 is understated by the unknown restricted amount. Leverage is therefore at least as bad as reported — this only strengthens the HIGH_NET_DEBT resolution below; it does not change the tier (already D on every scenario).
- **BASE_DIVERGENCE** (latest FY $2.67 vs 3-yr median $4.61): the latest FY is the distorted one — FY2025 OCF fell and capex stayed elevated through the charge-heavy year. The TTM base ($5.11) shows the run rate recovering as OCF rebounds (TTM OCF $1,185,761,000 vs FY $890,762,000). TTM base used; median retained in reporting.
- **HIGH_NET_DEBT** (net debt 6.1x normalized OE in the final run; 6.07x in diagnostics): real and stressed in the scenarios — bear/super-bear OE multipliers of 0.90/0.75 are applied on top of the leverage, and lease liabilities of $2,134,014,000 sit on top of the $4,318,572,000 net debt. Even so, every scenario clears solvency (OE positive 5/5 years, $2.3B liquidity at Q2 2026 per the 8-K summary); the leverage is a valuation/return problem, not a going-concern one.
- Preliminary run also carried WIDE_SCENARIO_SPREAD (4.51x); the recalibrated growth starts narrowed the final spread to 3.38x, but confidence is still capped below high on spread plus leverage and separation uncertainty.

## My thoughts / overlay
- This is a price problem, not a business-collapse problem: a durable, dividend-growing distributor whose TTM owner's earnings yield is 3.79% at $134.63 simply cannot clear a 15% hurdle — it would need to trade near $45.52.
- The method range is narrow for once: median base, latest-FY base, and TTM base all land in Tier D; the super-bull case (11.07% start, 1.25x OE) still only yields 9.71% IRR.
- Watch items for pass 2: separation terms and which entity keeps the debt/asbestos liabilities, First Brands-type supplier concentration, and whether restructuring savings actually lift the North America Automotive margin toward peers.

## Final verdict
- **Final tier: D** (weighted IRR 6.81% on the TTM base; bear D, bull D)
- Confidence: **Low** (scenario spread, 6x+ leverage on normalized OE, separation execution, and one-off-heavy recent filings)
- One-liner: Quality narrow-moat distributor (moat 5/10) in a charge-heavy separation year — at $134.63 it yields only 6.8% weighted IRR vs IV@15% of $45.52; it clears 15% only below ~$46.
