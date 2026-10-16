# ULTA — Ulta Beauty, Inc.
v5 run, 2026-10-15. In scope: market cap $26.606B at $591.36 (nasdaq_quote_api), under the $40B limit.

All figures below are copied from dcf_numbers.json, financials_history.csv, or (after scoring) key_numbers.md — none are recomputed.

## What it is
Largest U.S. specialty beauty retailer: mass and prestige beauty, haircare, fragrance, skincare and salon services in one store format, plus e-commerce. Differentiator versus Sephora is the all-price-points assortment in a single destination; versus Amazon it is discovery, trial and services. Recent expansion: Space NK acquired 2025-07-10 (UK prestige foothold, contributing to Q2 FY2026 sales growth), new stores, and a digital marketplace. The Ulta Beauty at Target shop-in-shop partnership ended in August 2026.

Latest quarters since the fiscal year-end (from web research, company reports):
- Q1 FY2026: net sales $3.16B, comparable sales +5.3%, diluted EPS $7.74.
- Q2 FY2026 (ended 2026-08-01, filed 2026-08-27): net sales $3.036B, +8.9% YoY; comparable sales +3.8% on a larger average ticket with transactions roughly flat; operating income $379.6M, +10.1%; diluted EPS $6.55, +13.3%; gross margin 39.1%, down 0.1pp.
- FY2026 guidance raised after Q2: net sales growth 6.7–7.2%, comparable sales +3.2–3.7%, operating income growth 8.3–9.3%, diluted EPS $28.70–$29.00; second-half guidance is slower (sales +4–5%, comps +2–3%). Fiscal 2026 buyback target raised to $1.8B; capex guidance $400–450M.

## Owner's earnings
**FY2026 (ended 2026-01-31, 10-K via EDGAR, from financials_history.csv):** revenue $12,392,820,000; net income $1,153,479,000; operating cash flow $1,502,780,000; capex $434,829,000 (tag PaymentsToAcquirePropertyPlantAndEquipment); SBC $37,426,000 (tag ShareBasedCompensation — always a real cost, and small here); D&A $300,772,000; cash $424,243,000.
- **Conservative owner's earnings FY2026: $1,030,525,000 = $22.91/share latest FY** (dcf_numbers.json: base_oe_latest_per_share $22.9051).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC, from financials_history.csv): $1,204,047,000 — above the conservative figure, so the conservative base is not flattered by the maintenance definition.
- OE positive 5 of the last 5 fiscal years. Operating income has nonetheless compressed over the last three filed years ($1,678,029,000 in FY2024, $1,564,972,000 in FY2025, $1,532,992,000 in FY2026 in the filed history) while revenue rose — margin pressure from wages, occupancy and investment is real, not hypothetical.
- Balance sheet: the engine reports net_debt_latest as null — no debt_current / debt_lt tags were filed in the extracted series and cash was $424,243,000. That is an engine extraction result, not a claim the business is obligation-free: store operating leases are the material fixed obligation for this retailer and are not in the engine's net-debt figure, so the verdict does not credit a net-cash balance sheet.

**Base used = normalized median of the last 3 FY OE/share: $20.02/share** (dcf_numbers.json: base_oe_normalized_per_share $20.0168, base_source median_of_last_3_fy_oe_per_share).
- The latest FY ($22.91) sits above the median; the median is used because FY2026 OE rebounded off two softer years and a single year would overstate the run rate. No BASE_DIVERGENCE flag was raised.
- TTM attempt (STALE_FY resolution): `ttm.py ULTA` exited non-zero with: "ttm.py: cannot compute TTM for ULTA (CIK 1403568): sbc: no post-FY YTD fact (no 10-Q since the 2026-01-31 fiscal year end)". Per the sweep rules, that message is recorded here and the engine's median base is used instead, with that reason stated. No TTM figures were hand-computed. The quarterly evidence above (sales +8.9% in Q2, EPS +13.3%) does not suggest the median base is stale-low in a way that would change the tier: even the latest-FY base is far below what the current price requires (see verdict).

## Moat: 5/10 — moderate / narrow
Justification: Scale, the broadest mass-plus-prestige assortment in U.S. beauty, and a ~47-million-member loyalty program (per Q2 FY2026 reporting) give Ulta real repeat-purchase and data advantages, but it owns almost no product, switching costs are low, brands can sell through Sephora, Amazon or direct, and pricing is largely set by brands — a narrow retail moat, not a wide one.
- FOR:
  - Largest U.S. specialty beauty scale with mass + prestige in one destination
  - ~47M-member loyalty program driving repeat sales and first-party data
  - Broad assortment (600+ brands in company descriptions) as a discovery destination brands need
  - In-store services and trial that pure e-commerce replenishment cannot replicate
  - Consistently positive owner's earnings (5/5 years) and disciplined buybacks
- AGAINST:
  - No owned product moat — brands can go direct, to Sephora, or to Amazon
  - Sephora in Kohl's (850+ locations) invading Ulta's suburban territory, with LVMH-backed exclusives
  - Amazon is the leading online beauty channel for replenishment purchases
  - Low customer switching costs — loyalty points are weak lock-in
  - U.S. store maturity, middle-income consumer pressure, shrink, and wage/occupancy cost pressure; Target shop-in-shop channel now ended
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — v5 final run (2026-10-15)
Growth sanity check and recalibration (written reason): the engine's g_base is 12.89%, built as g_blend 8.35% (rev CAGR 5y 15.03%, rev CAGR 3y 6.66%, latest rev YoY 9.71%, OE/share CAGR 2y 7.00%) plus a +4.54pp share-count adjustment. The 5-yr revenue CAGR spans the post-COVID rebound and overstates the forward rate: management's own FY2026 guide is sales +6.7–7.2% with H2 at +4–5%, and Q2 comps slowed to +3.8%. Scenario starts were therefore recalibrated via offsets (−0.119 / −0.079 / −0.029 / +0.011 / +0.061 vs g_base) to 0.99% / 4.99% / **9.99%** / 13.99% / 18.99%. The base start (9.99%) sits below guided diluted-EPS growth implied by the $28.70–$29.00 guide because OE is OCF − capex − SBC, capex is guided at $400–450M, and margins are compressing in the filed history; the super-bull start (18.99%) sits above recent revenue prints only on the combination of margin recovery, Space NK / new-store contribution and continued buyback-driven share shrinkage — it is deliberately the 10% tail, not the expectation. Probabilities 10/25/30/25/10; OE multipliers 0.75/0.90/1.00/1.10/1.25 (defaults, unchanged). Price $591.36.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | 0.99% | 0.75 | Consumer / prestige cycle turns, Sephora + Amazon take share, margins compress further | $115.60 | 4.90% |
| Bear | 25% | 4.99% | 0.90 | Guided H2 deceleration sticks, comps stay low-single-digit | $163.85 | 6.04% |
| Base | 30% | 9.99% | 1.00 | Guided sales growth plus buyback tailwind, fading over the CAP | $223.85 | 7.49% |
| Bull | 25% | 13.99% | 1.10 | Comps re-accelerate, Space NK and marketplace add, margins stabilise | $290.09 | 9.01% |
| Super bull | 10% | 18.99% | 1.25 | Margin recovery plus sustained high-single-digit sales and aggressive buybacks | $403.80 | 11.45% |

- **Probability-weighted: IV@15% $232.58, IV@12% $312.93, IV@10% $402.99, weighted IRR 7.72%, base-case IRR 7.49%**
- **Tier by numbers: D.** Diagnostics: OE yield 3.38%, terminal value 20.0% of IV@15%, scenario spread 3.49x, 8.4 months since FY end.
- Even the super-bull scenario (11.45% IRR, IV@15% $403.80) does not clear the 15% hurdle at $591.36 — this is a price problem, not a scenario-weighting problem.

## Flags — every fragility flag resolved
- **STALE_FY** (latest fiscal year ended 8.4 months ago): ttm.py was run and failed for the reason quoted verbatim in the Owner's earnings section (no post-FY YTD SBC fact in its us-gaap pull). The engine's median-of-3-FY base is used instead, per the rules, and the Q1/Q2 FY2026 prints are reported above as a cross-check; they do not support a base high enough to change the tier.
- **BUYBACK_TAILWIND** (share count shrinking 4.54%/yr): already credited via the +4.54pp growth adjustment in g_base; not double-counted. Note the adjustment is also a reason the raw g_base was recalibrated down — a $1.8B annual buyback pace cannot be assumed to compound indefinitely. Diluted shares in the filed history fell from 51,738,000 in FY2023 to 44,991,000 in FY2026.
- **WIDE_SCENARIO_SPREAD** (raised on the preliminary run at 4.44x; 3.49x on the final run): real retail outcome range, narrower after recalibration. Confidence is set to medium, not high, and the verdict is sized to the conservative end.

## My thoughts / overlay
- Quality is not the debate: OE positive 5/5 years, SBC is tiny ($37,426,000 in FY2026 against OCF $1,502,780,000), capex is real and fully counted, and the maintenance OE definition sits above the conservative one.
- The debate is price and margin direction. Revenue is still growing (latest YoY +9.71%, Q2 +8.9%) but filed operating income fell for two straight years while revenue rose, and management guides H2 FY2026 slower than H1. At $591.36 the market is paying for a growth / margin-recovery path that even this run's super-bull case (18.99% start, 1.25x OE) prices at only $403.80 at a 15% discount.
- Method range: using the engine's default offsets (base start 12.89%, super-bull 24.89%) on the preliminary run gave a weighted IRR of 8.61% and weighted IV@15% of $269.46 — still Tier D. The recalibrated final run ($232.58, 7.72%) and the preliminary run span the defensible range; both are D, so there is no tier-spanning method range to report.
- Price that clears 15%: $232.58 (the weighted IV@15%). With a margin of safety against the weighted case, a buyer would want a price below that, not at it. The current $591.36 price is more than double the hurdle-clearing price.
- Red flags checked: dilution is the opposite problem (buybacks, not dilution; SBC load is minimal); no going-concern or litigation flag surfaced in research; customer concentration does not apply to a consumer retailer; the basis-break risk is Space NK consolidation from July 2025 and the ended Target partnership, both handled by using guided / recent growth rather than the 5-yr CAGR.

## Final verdict
- **Final tier: D** (weighted IRR 7.72% on the v5 final inputs; no tier override)
- Confidence: **Medium** (high on OE quality and the filed base, medium on the forward path — scenario spread 3.49x and a TTM base could not be computed)
- One-liner: Quality narrow-moat beauty retailer, moat 5/10 — does not clear 15% at $591.36 (weighted IRR 7.72%, weighted IV@15% $232.58); clears 15% only below $232.58.
