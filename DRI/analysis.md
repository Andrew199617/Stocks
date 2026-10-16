# DRI — Darden Restaurants, Inc.
v5 run, 2026-10-15. In scope (market cap $24.921B at $214.28, nasdaq_quote_api — key_numbers.md).

All figures below are copied from key_numbers.md, dcf_numbers.json, financials_history.csv, or the cited earnings research — none are recomputed.

## What it is
The largest US full-service restaurant operator (~2,200 company-owned restaurants at FY2026 end): Olive Garden (largest brand), LongHorn Steakhouse, fine dining (Ruth's Chris, The Capital Grille, Eddie V's), and Other Business (Cheddar's, Chuy's, Yard House, Seasons 52, Bahama Breeze — the last being closed/converted). FY2026 was a 53-week year ended 2026-05-31.

## Owner's earnings
**FY2026 (10-K via EDGAR, from financials_history.csv):** revenue $13,210,900,000; operating cash flow $1,853,100,000; capex $734,000,000; SBC $79,100,000 (always a real cost, and small here — restaurant labor is paid in cash wages, not equity).
- **Conservative owner's earnings FY2026: $1,040,000,000 = $8.94/share** (key_numbers.md: latest FY OE/share $8.94; latest FY OE total $1.040B)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $1,245,300,000 (financials_history.csv) — above the conservative figure because capex in a growth year includes new-unit build-out, not just maintenance. The conservative figure is the base used; the gap is a reminder that true maintenance capex for a growing restaurant fleet sits between the two definitions.
- OE positive 5 of the last 5 fiscal years (5/5). Net debt $2.112B (key_numbers.md), 2.19x normalized OE — moderate for a company-owned restaurant fleet with steady cash flow, folded into the verdict below, not a distress input.
- Shares are shrinking: diluted count 116,300,000 latest, share-count CAGR −1.82%/yr (buybacks; a new repurchase authorization and an 8% dividend raise were announced with FY2026 results in June 2026).

**Base used = normalized owner's earnings, median of last 3 FY OE/share: $8.30/share** (base_source: median_of_last_3_fy_oe_per_share). Latest FY is $8.94/share; the median is the more conservative, non-distorted choice — no BASE_DIVERGENCE flag fired, and FY2026 itself was flattered by the 53rd week. No TTM pin: FY ended 4.5 months ago, no STALE_FY flag, so the engine's median base stands per the v5 method.

**Since FY end (research, Q1 FY2027, quarter ended Aug 2026, reported Sep 24, 2026):** sales $3.20B, +5.1% YoY; comparable-calendar same-restaurant sales +3.2% blended — LongHorn +6.2% (its 22nd consecutive positive-comp quarter), Olive Garden only +1.0–1.1%; adjusted EPS $2.05, +4.1% YoY, while reported net income fell YoY on Bahama Breeze closure-related costs. Management reaffirmed FY2027 guidance: sales $13.60–13.75B, same-restaurant sales +2.5% to +3.5%, adjusted EPS $11.10–11.35 (vs FY2026 adjusted EPS $10.64). Restaurant-level margins were flat under food/beef and labor cost pressure (~3.5% labor inflation expected in FY27).

## Moat: 5/10 — moderate / narrow
Justification: the largest US full-service operator with genuine scale in purchasing, talent and data, and two proven anchor brands that have compounded same-restaurant sales through cycles — but restaurants have no switching costs, pricing power is capped by consumer elasticity and value rivals, and returns depend on re-earning traffic every quarter against beef and labor inflation.
- FOR: Scale — largest US full-service operator (~2,200 restaurants): purchasing, talent and data advantages smaller chains cannot match.
- FOR: Anchor brands Olive Garden and LongHorn with long positive-comp records; LongHorn +6.2–6.8% comps in Q1 FY2027.
- FOR: Diversified portfolio across casual, steakhouse and fine dining dampens single-concept slumps.
- FOR: Disciplined capital return — buybacks shrinking the share count ~1.8%/yr; dividend raised 8% in June 2026.
- FOR: Proven through-cycle operator — owner's earnings positive 5 of last 5 fiscal years.
- AGAINST: No switching costs; guests can trade down to fast-casual, QSR or home meals at any time.
- AGAINST: Pricing power limited by value competition — Brinker's Chili's value resurgence pressures Olive Garden directly; Texas Roadhouse contests LongHorn.
- AGAINST: Beef inflation at cyclical highs hits LongHorn, the fastest-growing brand; ~3.5% labor inflation guided for FY2027.
- AGAINST: Olive Garden comps slowed to +1.0–1.1% in Q1 FY2027; management flagged softness among younger guests.
- AGAINST: Mature US casual-dining market — underlying unit and comp growth is low-single-digit.
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — v5 final run (2026-10-15)
**Growth recalibration (written reason):** the engine's blended growth is 8.68% → g_base 10.50%, but its components overstate the underlying run rate: rev CAGR 5y 12.91% spans the COVID-recovery years plus the Ruth's Chris (2023) and Chuy's (2024) acquisitions, and latest rev YoY 9.39% includes the 53rd week of FY2026. The current, guidance-anchored evidence is much lower: FY2027 guided sales growth to $13.60–13.75B, same-restaurant sales +2.5% to +3.5%, guided adjusted EPS $11.10–11.35 vs $10.64 in FY2026, and Q1 FY2027 prints of sales +5.1% / adjusted EPS +4.1%. Scenario starts (OE/share growth, which embeds the ~1.8%/yr buyback already in g_base) were therefore set via offsets (−0.125 / −0.09 / −0.055 / −0.03 / 0.0 vs g_base) to −2.0 / +1.5 / **+5.0** / +7.5 / +10.5%. The base start of 5.0% sits inside the guided EPS growth range — it is not below what the company just printed, it *is* what the company guided. Bull (7.5%) requires comp acceleration beyond guidance; super bull (10.5%) is set at the engine's own unadjusted g_base as the ceiling case. Probabilities kept at the defaults 10/25/30/25/10; OE multipliers at the defaults 0.75/0.90/1.00/1.10/1.25. Price $214.28.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -2.0% | 0.75 | Consumer pullback + beef/labor squeeze; comps go negative | $42.32 | 4.84% |
| Bear | 25% | 1.5% | 0.90 | Low-single-digit comps, margin pressure persists | $58.79 | 5.90% |
| Base | 30% | 5.0% | 1.00 | Guidance path: +2.5–3.5% comps, steady units + buybacks | $75.56 | 7.00% |
| Bull | 25% | 7.5% | 1.10 | Olive Garden re-accelerates; LongHorn momentum holds | $92.18 | 8.06% |
| Super bull | 10% | 10.5% | 1.25 | Engine's unadjusted blend proves right; sustained high-single-digit OE growth | $118.54 | 9.68% |

- **Probability-weighted: IV@15% $76.50 (−64.3% vs price), IV@12% $101.45, IV@10% $129.27, weighted IRR 7.07%, base-case IRR 7.00%**
- **Tier by numbers: D.** Diagnostics (key_numbers.md): OE yield 3.88%, terminal value 18.6% of IV@15%, scenario spread 2.80x, net debt 2.19x normalized OE, 4.5 months since FY end.

## Flags — every fragility flag resolved
- **Final run: no fragility flags** (key_numbers.md: "(none)").
- **WIDE_SCENARIO_SPREAD (preliminary run only, 4.46x):** fired on the preliminary pass because the default offsets put the super-bull start at 22.5% — a rate no Darden print or guidance supports. The recalibration above narrowed the spread to 2.80x and the flag cleared. Confidence is still held at medium, not high, because restaurant earnings remain consumer- and commodity-cyclical.
- **Net debt (not flagged):** $2.112B, 2.19x normalized OE. For a company-owned fleet generating $1.040B of conservative OE, this is manageable leverage, not a fragility — but it is equity-holder leverage: in the bear cases the OE stream, not the balance sheet, is what fails to clear the hurdle.
- **Buyback tailwind (not flagged, credited once):** share-count CAGR −1.82%/yr is already inside g_base via the +1.82pp adjustment; scenario starts are OE/*share* growth rates consistent with guided EPS growth, so it is not double-counted in the verdict.
- **One-offs:** Q1 FY2027 reported net income fell YoY on Bahama Breeze closure costs while adjusted EPS rose — closure/integration noise sits in reported NI, not in the OCF-based conservative OE base, so the base is not contaminated. FY2026's 53rd week flatters the latest-FY figures; using the 3-yr median base ($8.30 vs latest $8.94) is the conservative correction.

## My thoughts / overlay
- The verdict does not hinge on the recalibration. The preliminary run on the engine's *unadjusted* inputs (g_base 10.50% as the base start, super-bull start 22.5%) still produced only a weighted IRR of 8.76% and weighted IV@15% of $101.41 — Tier D — and even its super-bull IV@15% ($192.89) sat below the $214.28 price. On the recalibrated, guidance-anchored inputs, *no* scenario — including super bull at 10.5% growth with a 1.25x OE multiplier — clears even 10% IRR. The method range here is D to D; the spread is in how far below the hurdle, not in which side of it.
- Quality is not the problem: 5/5 OE-positive years, minimal SBC, disciplined buybacks, brands still gaining share (LongHorn especially). The problem is purely price: at $214.28 the market is paying for growth Darden has never sustained organically, for a business whose guided growth is mid-single-digit.
- The price that clears 15% on the final inputs is the weighted IV@15% itself: **$76.50**. With a margin of safety against the bear cases (bear IV@15% $58.79), a buyer wanting insurance as well as the hurdle would need a price below that. Nothing in the recent prints argues the market is misreading the business — it argues the multiple, not the operations, is the risk.

## Final verdict
- **Final tier: D** (weighted IRR 7.07% on the v5 final inputs; Tier D under both the recalibrated and the engine-default growth inputs)
- Confidence: **Medium** (high on the OE base and on the tier's robustness across methods; medium on any single growth path)
- One-liner: High-quality, narrow-moat restaurant operator (moat 5/10) that does not come close to the 15% hurdle at $214.28 — weighted IRR 7.07%, weighted IV@15% $76.50; it would need to fall to about $76.50 to clear 15% on these inputs.
