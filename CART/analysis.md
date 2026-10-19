# CART — Maplebear Inc. dba Instacart
Pass-1 run, 2026-10-18, engine 5.4.0. Price $49.83 (nasdaq_quote_api), market cap est. $13,933,514,430 — in scope under $40B.

All figures below are copied from dcf_numbers.json, ttm.json, financials_history.csv, or fundamentals.json — none are recomputed.

## What it is
The leading third-party online grocery marketplace in the US (~21.6% US online grocery share per industry estimates cited in research, and >70% share of large baskets over $75), connecting customers to 1,500+ retail banners, plus an enterprise technology platform (white-label storefronts, fulfillment, Caper smart carts) sold to those same retailers, and a closed-loop advertising business. Q2 2026: GTV $10,351M (+14% YoY), orders 90.3M (+9%), total revenue $1,043M (+14%), advertising & other revenue $297M (+16%, 2.9% of GTV), GAAP net income $111M, Adjusted EBITDA $313M (+19%).

## Owner's earnings
Two definitions, FY2025 (10-K, financials_history.csv):
- **Conservative (OCF − capex − SBC):** OCF $971,000,000 − capex $61,000,000 − SBC $352,000,000 = **$558,000,000 = $1.995558273520229/share** (base_oe_latest_per_share).
- **Maintenance (NI + D&A − min(capex, D&A) − ΔNWC): $453,000,000** — same ballpark, below the conservative figure, so the conservative base is not flattered by the maintenance definition.
- OE positive 3 of the last 5 fiscal years (oe_positive_years_of_last_5); the negatives are 2021 (−$239,000,000) and 2023 (−$2,224,000,000, the IPO SBC spike — see NI_OCF_DIVERGENCE).
- SBC is always a real cost here and it is large: $22M (2021), $33M (2022), $2,756,000,000 (2023, IPO vesting), $300,000,000 (2024), $352,000,000 (2025), $401,000,000 TTM — about 10% of revenue and a rising absolute dollar cost even after the IPO spike washes out.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $971,000,000 − prior YTD $501,000,000 + current YTD $762,000,000 = **TTM $1,232,000,000**
- Capex: FY $61,000,000 − prior YTD $34,000,000 + current YTD $29,000,000 = **TTM $56,000,000**
- SBC: FY $352,000,000 − prior YTD $172,000,000 + current YTD $221,000,000 = **TTM $401,000,000**
- Shares (current-YTD weighted diluted): **251,254,000**
- **TTM OE total $775,000,000 → base OE/share $3.0845280075143084** (base_source: ttm_json)
- The engine's normalized base (median of last 3 FY OE/share) is $1.117036360743953/share — rejected as the base; see BASE_DIVERGENCE. Fundamentals.json's independent TTM cut gives OE $773,000,000 and $2.9088123689574332/share on a duration-weighted share count — corroborating the order of magnitude.

**Balance sheet (filing, 10-K / Q2 2026 10-Q):** at 2025-12-31, cash $637,000,000, short-term marketable securities $50M, long-term marketable securities $81M, total assets $3,687,000,000, total liabilities $974,000,000, stockholders' equity $2,518,000,000, lease liabilities $36,000,000, and **no funded debt line items at all**. At 2026-06-30: cash $757M, total assets $3,510M, total liabilities $988M, equity $2,322M. Buybacks were $1,859,000,000 TTM per fundamentals.json — equity is falling because cash is being returned, not because the business is losing money.

## Moat: 6/10 — moderate, not wide
Justification: leading third-party grocery marketplace with retailer network effects, an enterprise platform that raises retailer switching costs, and closed-loop advertising, supported by two clean years of high returns on capital — capped at 6 because Walmart and Amazon out-scale it, consumers multi-home, and gross margin is slipping.
- FOR: Leading third-party grocery marketplace — ~21.6% US online grocery share and >70% share of large baskets over $75; retailer network effects across 1,500+ banners plus scale data from 1.6B lifetime orders; enterprise platform (storefronts, fulfillment, Caper carts) embedded in retailer operations — real switching costs; closed-loop advertising: ad revenue +16% in Q2 2026 to 2.9% of GTV, monetizing purchase intent a second time; ROIC proxy 22.3% (2024) and 21.3% (2025) with gross margin 75.3% / 73.7% — returns well above cost of capital in the clean post-IPO years.
- AGAINST: Walmart (largest US grocer, own logistics) and Amazon same-day fresh expansion can compress share and take rate; DoorDash and Uber Eats encroaching on grocery from adjacent delivery networks; low consumer switching costs — shoppers multi-home and retailers can insource or dual-source; gross margin eroding: 75.3% (2024) to 73.7% (2025) to 72.6% TTM as ad publisher payments and cost of revenue rise; SBC is a large, rising real cost: $300M (2024) to $352M (2025) to $401M TTM, ~10% of revenue.
- Evidence (fundamentals.json): gross margin 66.8% (2021), 71.8% (2022), 74.9% (2023), 75.3% (2024), 73.7% (2025), 72.6% TTM. ROIC proxy 3.95% (2021), −3.1% (2022), −104.9% (2023, SBC-distorted operating loss), 22.3% (2024), 21.3% (2025). A moat above 6 would need that >20% ROIC proven through a cycle against Walmart/Amazon pressure; two clean years is not a cycle.
- A 6 gives CAP = 9.8 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 9.8 years, 15-year projection.

## DCF — final run (2026-10-18)
**Growth recalibration (written reason):** the engine's blended growth is 8.62% (g_blend 0.08619216455899985) after a −5pp share-count adjustment driven by a 40.2%/yr share CAGR (share_cagr 0.4018330859284902) that is a pre-IPO artifact — diluted counts were 65,874,000 (2021) and 130,616,000 (2023) before preferred conversion at the September 2023 IPO, versus 289,158,000 (2024). Forward, the count is *falling*: diluted 282,117,000 (H1 2025) → 251,254,000 (H1 2026), shares outstanding 231,500,067 at 2026-07-31, on $1,859,000,000 of TTM buybacks. The adjustment's direction is therefore wrong for OE/share. Recent prints: FY2025 revenue +10.78% (rev_yoy_latest), TTM revenue +12.6% YoY (fundamentals.json revenue_yoy 0.12605752961082906), Q2 2026 revenue and GTV both +14% YoY, advertising +16%. Scenario starts were therefore reset via offsets (−0.086 / −0.026 / +0.044 / +0.104 / +0.174 vs g_blend) to 0.0% / 6.0% / **13.0%** / 19.0% / 26.0% — the base start sits on the current revenue/GTV print, *not* on the unsustainable OE/share jumps (+79% in FY2025; TTM OE +70.6% YoY in fundamentals.json), which include a working-capital receivable swing in H1 2026. Probabilities 10/25/30/25/10 (defaults, kept); OE multipliers 0.75/0.90/1.00/1.10/1.25 (defaults).
Sanity check against prints: base 13.0% ≈ Q2's +14% revenue/GTV and +16% ads; bull 19.0% and super-bull 26.0% are above every revenue print and require advertising/enterprise acceleration plus buyback tailwind — they are paid for in probability (25% / 10%), not assumed; super-bear 0.0% is a share-loss stall, not a collapse, because even the bear history here is double-digit revenue growth.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | 0.0% | 0.75 | Walmart/Amazon take share, take rate compresses, OE/share stalls | $16.99 | 6.65% |
| Bear | 25% | 6.0% | 0.90 | Growth halves from current prints; SBC keeps rising | $26.62 | 9.33% |
| Base | 30% | 13.0% | 1.00 | Current ~14% GTV/revenue trajectory decays over the CAP | $40.37 | 12.85% |
| Bull | 25% | 19.0% | 1.10 | Ads and enterprise outgrow GTV; buybacks compound OE/share | $57.87 | 16.67% |
| Super bull | 10% | 26.0% | 1.25 | Category consolidates to Instacart; operating leverage persists | $89.30 | 22.21% |

- **Probability-weighted: IV@15% $43.86, IV@12% $60.01, IV@10% $78.25, weighted IRR 13.69%, base-case IRR 12.85%**
- **Tier by numbers: C.** Bear tier D (9.33%), bull tier B (16.67%). Diagnostics (dcf_numbers.json): OE yield 6.19%, terminal value 21.8% of IV@15%, scenario spread 5.26x, 9.56 months since FY end.
- **Hurdle-clearing prices:** $43.86 clears 15%, $29.66 clears 20%, $22.05 clears 25% (hurdle_prices). Upside vs price at 15% is −12.0% (upside_at_15 −0.11975543175348591).

## Flags — every fragility flag resolved
- **STALE_FY** (latest fiscal year ended 10 months ago; months_since_fy_end 9.559789750328514): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, legs quoted above.
- **DILUTION** (share count growing 40.2%/yr): the CAGR is a pre-IPO artifact (see growth recalibration) — the diluted count rose because preferred stock converted at IPO, not because of ongoing issuance. The current trend is shrinkage: 282,117,000 diluted (H1 2025) → 251,254,000 (H1 2026), outstanding 231,500,067 at 2026-07-31, on $1,859,000,000 TTM buybacks. The real residual concern is SBC itself ($401M TTM and rising), which is deducted in full in the OE base.
- **NI_OCF_DIVERGENCE** (>40% in 2023, 2025): 2023 — net income −$1,622,000,000 vs OCF $586,000,000; the gap is the $2,756,000,000 non-cash SBC charge on IPO vesting. 2025 — net income $447,000,000 vs OCF $971,000,000; the gap is principally the non-cash SBC addback ($352,000,000) plus D&A ($91,000,000). No tax-deposit or impairment one-off is needed to explain either year, and the OCF-based conservative OE is the series used throughout, so the divergence does not contaminate the base.
- **DEBT_TAGS_BLANK** (no debt tag for the latest fiscal year — net debt UNKNOWN from the engine): resolved from the filing balance sheet quoted above — Maplebear files no funded-debt line items because it has no funded debt; total liabilities of $974,000,000 at 2025-12-31 are operating liabilities plus $36,000,000 of lease liabilities, against $637,000,000 of cash plus $131M of marketable securities. The leverage verdict from the filing is: unlevered, net cash. The engine's net_debt_latest correctly stays null.
- **BASE_DIVERGENCE** (latest FY OE/share $2.00 vs 3-yr median $1.12): **the median is the distorted figure** — it is mechanically 2024's $1.117036360743953 in a three-year series that runs −$17.02701047344889 (2023, IPO SBC), $1.12 (2024), $2.00 (2025). The progression since is real and OCF-driven: OCF $687,000,000 (2024) → $971,000,000 (2025) → $1,232,000,000 TTM, outpacing SBC growth. TTM base used; median retained in the reporting and in the method range below.
- **WIDE_SCENARIO_SPREAD** (super-bull IV 5.26x super-bear IV): real — the outcome range against Walmart/Amazon genuinely is wide. Confidence is capped at medium, and the verdict is sized to the conservative end.
- **TIER_BAND** (bear tier D at 9.33% vs bull tier B at 16.67%): the verdict spans tiers; any position should be sized to the bear end, per the flag.

## My thoughts / overlay
- The honest headline is the *method range*: the preliminary median-base run printed weighted IRR 5.91% and IV@15% $12.63 (Tier D); the TTM base with engine-default growth offsets printed 11.75% and $35.86 (Tier C); the final run — TTM base plus growth recalibrated off the current +14% prints with the bogus share adjustment neutralized — prints 13.69% and $43.86 (Tier C). The range is D to C; no defensible method gets this price to a 15% hurdle.
- Quality is not the debate: no funded debt, $775,000,000 of TTM conservative owner's earnings after deducting $401,000,000 of SBC, buybacks shrinking the count at a double-digit pace, ROIC above 20% in both clean years.
- What the price already pays for: at $49.83 the market is paying roughly the bull-case path (bull IV@15% $57.87, IRR 16.67%) with base-case probability. The growth acceleration of the last three quarters is real, but so is the gross-margin slide (75.3% → 72.6% TTM) and the Walmart/Amazon response.
- Data note: enrichment failures, if any, are recorded after make_score.py runs; the score does not depend on them.

## Final verdict
- **Final tier: C** (weighted IRR 13.69% on the final inputs; method range D to C, bear D / bull B)
- Confidence: **Medium** (high on the TTM OE base and the unlevered balance sheet; capped by the 5.26x scenario spread and a two-clean-year ROIC history)
- One-liner: High-quality, debt-free grocery platform, moat 6/10 — does not clear 15% at $49.83 on TTM owner's earnings (13.7% weighted IRR, IV@15% $43.86); it clears 15% at or below $43.86, with the bear case at 9.3%.
