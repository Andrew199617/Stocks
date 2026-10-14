# CCL — Carnival Corp Ltd.

v5 run, 2026-10-14. In scope under $40B (market cap $37.602B at $26.82, nasdaq_quote_api). Supersedes the v4 analysis of 2026-10-13 — conclusion unchanged (Tier C, ~12.2% weighted IRR).

All figures below are copied from dcf_numbers.json, ttm.json, or financials_history.csv — none are recomputed.

## What it is
The world's largest cruise operator — more than 90 ships across nine brands (Carnival Cruise Line, Princess, Holland America, Seabourn, Cunard, P&O, AIDA, Costa) spanning value to ultra-luxury. Revenue is ticket plus onboard spend. Capacity is broadly flat over the next 12 months per Q3 FY2026 reporting, so earnings growth must come from yields/pricing and onboard spend, not new berths. Q3 FY2026 was a record quarter in search summaries: revenue $8.435B, net yields up nearly 2.5% YoY, record customer deposits of about $7.6B, and full-year FY2026 adjusted EPS guidance raised to about $2.24 — essentially flat versus FY2025, with fuel as the offset. 2027 is already about half booked at record occupancy and pricing in management commentary.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $6,218,000,000; capex $3,611,000,000 (tag PaymentsToAcquirePropertyPlantAndEquipment); SBC $98,000,000 (tag ShareBasedCompensation, always a real cost); D&A $2,790,000,000.
- **Conservative owner's earnings FY2025: $2,509,000,000 = $1.79/share** (base_oe_latest_per_share $1.789586305278174 in dcf_numbers.json)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $3,047,000,000 in financials_history.csv — above the conservative figure because capex exceeds D&A in a fleet-renewal year; the conservative OCF-based figure is the one used for the base.
- OE positive 3 of the last 5 fiscal years — the negative years are the COVID shutdown years, not normal cyclicality.
- Net debt latest: $24,712,000,000 (dcf_numbers.json). This is the central fact of the equity case — see HIGH_NET_DEBT below.

**Base used = TTM owner's earnings through Q3 FY2026 (2026-08-31), from ttm.py (filing-direct, no hand math):**
- OCF: FY $6,218,000,000 − prior YTD $4,700,000,000 + current YTD $5,303,000,000 = **TTM $6,821,000,000**
- Capex: FY $3,611,000,000 − prior YTD $2,105,000,000 + current YTD $2,139,000,000 = **TTM $3,645,000,000**
- SBC: FY $98,000,000 − prior YTD $70,000,000 + current YTD $73,000,000 = **TTM $101,000,000**
- Shares (current-YTD weighted diluted): **1,382,000,000**
- **TTM OE total $3,075,000,000 → base OE/share $2.2250361794500724** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $0.8834048640915594/share — rejected as the base: it is dragged by FY2023, the first full post-COVID recovery year. Latest FY ($1.79) and TTM ($2.23) both show the median is the distorted figure (see BASE_DIVERGENCE).

## Moat: 5/10 — moderate / narrow
Justification: Carnival has real scale — roughly 37-42% global share in search summaries, nine brands, purchasing leverage, private destinations, and a large forward deposit float — but no durable pricing power that survives a downturn, no switching costs for passengers, intense rivalry from Royal Caribbean, Norwegian, Viking and MSC, and a levered, fuel-exposed, capital-intensive fleet. Returns have only just recovered after a near-death dilutive recapitalisation. This is one notch above the v4 score of 4 on the strength of the private-destination build-out and the record forward book; the CAP difference (8.5y vs 7.2y) does not change the tier.
- FOR: Largest global fleet and share (about 40% in multiple summaries) across nine brands from value to luxury
- FOR: Scale purchasing, deployment flexibility, and home-port network rivals cannot match at the low end
- FOR: Private destinations (Celebration Key, opened July 2025) capture the full shore-side spend and differentiate the itinerary
- FOR: Record forward bookings and customer deposits (about $7.6B) give demand visibility and an interest-free float
- FOR: Brand breadth lets Carnival shift ships and pricing tiers to follow demand by region and segment
- AGAINST: No passenger switching costs — cruises are a discretionary, price-compared purchase, with resorts, hotels and theme parks as substitutes
- AGAINST: Royal Caribbean's premium position and MSC's aggressive North America/Caribbean expansion pressure pricing; Caribbean industry capacity growth was flagged at about 37% over three years
- AGAINST: Fuel is unhedged in the Q3 FY2026 summaries — a small fuel move swings quarterly profit by a material double-digit percentage
- AGAINST: High leverage and heavy recurring capex claim cash before equity holders
- AGAINST: Emissions and environmental regulation raise compliance capex on older tonnage
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — v5 final run (2026-10-14)
Growth recalibration (written reason, required): the engine's blended growth is 33.21% and g_base is 28.21% because its components straddle COVID — rev CAGR 5y 36.62%, rev CAGR 3y 29.81%, OE/share CAGR 2y 54.63% are all recovery arithmetic off a collapsed base. The signals that describe the business today are latest revenue YoY +6.40%, Q3 FY2026 net yields up nearly 2.5%, broadly flat capacity, and FY2026 EPS guidance of about $2.24, flat versus FY2025. Scenario starts were therefore set via offsets −0.3021 / −0.2621 / −0.2321 / −0.1921 / −0.1421 vs g_base to −2 / +2 / **+5** / +9 / +14%. The super-bear −2% is a deliberate downturn case (fuel spike / consumer pullback / Caribbean pricing war), not a forecast; the base +5% sits between the +6.40% revenue print and the flat EPS guide, reflecting yield growth partly eaten by fuel and capex. Probabilities were skewed slightly bearish (15/25/30/20/10 vs the 10/25/30/25/10 default) for leverage and unhedged fuel. OE multipliers are the defaults 0.75/0.90/1.00/1.10/1.25. Price $26.82.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | -2.0% | 0.75 | Fuel spike + consumer downturn + Caribbean pricing war; levered OE compresses | $11.34 | 7.60% |
| Bear | 25% | 2.0% | 0.90 | Yields stall, fuel stays high, deleveraging slows | $16.09 | 9.98% |
| Base | 30% | 5.0% | 1.00 | Mid-single-digit yield-led growth on flat capacity, normal fuel | $20.25 | 12.00% |
| Bull | 20% | 9.0% | 1.10 | Record 2027 pricing holds, fuel eases, destinations lift onboard spend | $26.28 | 14.76% |
| Super bull | 10% | 14.0% | 1.25 | Sustained pricing power + rapid deleveraging re-rates the equity | $36.66 | 19.03% |

- **Probability-weighted: IV@15% $20.72 (−22.7% vs price), IV@12% $27.54, IV@10% $35.14, weighted IRR 12.25%, base-case IRR 12.00%**
- **Tier by numbers: C.** Diagnostics (dcf_numbers.json): OE yield 8.30%, terminal value 18.78% of IV@15%, scenario spread 3.23x, net debt 7.92x normalized OE (on the TTM base; 19.95x on the rejected median base in the preliminary run), 10.45 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (latest FY ended 10.45 months ago): resolved by construction — the base is the TTM figure from ttm.py through 2026-08-31, quoted in full above.
- **DILUTION** (share count growing 5.9%/yr): that trend is the COVID recapitalisation — diluted shares rose from 692,000,000 in FY2019 to 1,402,000,000 in FY2025 in financials_history.csv. It has reversed at the margin: TTM shares are 1,382,000,000 and Q3 FY2026 summaries report about $1.2B of repurchases. SBC itself is small ($98M FY2025, $101M TTM). The −5pp share-count adjustment in the engine blend is a legacy of the rescue era — one more reason the recalibrated scenario starts, not the blend, carry the verdict. No credit was taken back for this in the offsets; the conservatism is retained.
- **BASIS_BREAK_SUSPECT** (>60% revenue jump/drop in last 5 yrs): identified — it is COVID, not M&A/divestiture. Revenue in financials_history.csv: $20,825,000,000 (2019) → $5,595,000,000 (2020) → $1,908,000,000 (2021) → $12,168,000,000 (2022) → $21,593,000,000 (2023). Every CAGR that straddles 2020-2022 is recovery arithmetic. Growth inputs were chosen on post-recovery signals only (latest YoY, yields, guidance).
- **NI_OCF_DIVERGENCE** (NI vs OCF differ by >40% in 2023, 2024, 2025): structural, not a one-off. OCF exceeds net income in each year because D&A is $2,370,000,000 / $2,557,000,000 / $2,790,000,000 respectively (non-cash fleet depreciation added back in OCF) and advance customer deposits inflate operating cash timing. FY2025: net income $2,760,000,000 vs OCF $6,218,000,000; FY2023: net income −$74,000,000 vs OCF $4,281,000,000. The OCF-based conservative OE is the series used throughout, so the divergence does not contaminate the base.
- **BASE_DIVERGENCE** (latest FY OE/share $1.79 vs 3-yr median $0.88): the median is the distorted one — FY2023 was still a recovery year. Latest FY and the filing-derived TTM ($2.23) agree on direction and are the run-rate; the TTM base was used.
- **WIDE_SCENARIO_SPREAD** (preliminary run 4.29x; final recalibrated run 3.23x): still wide — a levered cruise equity genuinely has a wide outcome range. Confidence is set to low, probabilities were skewed bearish, and the verdict is sized to the conservative end.
- **HIGH_NET_DEBT** (net debt $24,712,000,000; 7.92x normalized OE on the TTM base, 19.95x on the median base): folded explicitly into the verdict. Search summaries report total debt down from a $36B peak in 2023 to below $24B, a $19B refinancing completed in FY2025, and net debt/EBITDA of 3.4x at FY2025-end with a target below 3.0x. That is real repair, not safety: with unhedged fuel and $3,645,000,000 of TTM capex, a single bad year pushes deleveraging back years and the bear/super-bear IVs ($16.09 / $11.34) sit far below the price. The equity is a levered stub on a good operating recovery.

## My thoughts / overlay
- The honest headline is the method range: on the preliminary engine defaults (median base $0.88, 28% growth) the weighted IRR was 13.13% — a similar Tier C by coincidence, via two offsetting errors (base too low, growth absurdly high). On the corrected inputs (TTM base $2.23, realistic 5% base growth) it is 12.25%, Tier C, matching the independent v4 result of 12.2% / $20.45 almost exactly. Defensible variations span roughly Tier C to the bottom of Tier B, never A on any input set that respects the flat EPS guide and the debt load.
- Quality is middling: a real, cash-generative recovery (TTM OCF $6,821,000,000, TTM OE $3,075,000,000) attached to a balance sheet that still claims most of it. Dividend reinstatement and buybacks signal management confidence, but they compete directly with deleveraging.
- Risks: unhedged fuel (the largest near-term swing factor), Caribbean capacity growth and pricing, consumer discretionary exposure, dry-dock and newbuild capex creep, emissions regulation, and the tail risk of a shutdown-type event for a levered cruise operator — FY2020-21 OE was deeply negative and no scenario here models a repeat.
- Price that clears 15%: the weighted IV@15% is $20.72 — at or below that price the weighted case clears Andrew's 15% hurdle on these inputs. With a margin of safety against the bear case (IV@15% $16.09), a conservative entry is in the mid-teens. At $26.82 the buyer is paying for the bull case and getting the base case.

## Final verdict
- **Final tier: C** (weighted IRR 12.25% on the v5 final inputs; method range C to low-B)
- Confidence: **Low** (wide scenario spread, high leverage, unhedged fuel — a single-variable swing moves the tier)
- One-liner: Largest cruise operator, moat 5/10, with a genuine TTM cash recovery ($2.23/share OE) — but at $26.82 it does not clear 15% (12.2% weighted, IV@15 $20.72); it clears at $20.72, and with a margin of safety only in the mid-teens given $24.71B of net debt.
