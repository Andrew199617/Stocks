# AIT — Applied Industrial Technologies, Inc.
v5.4 run, 2026-10-18. Market cap $12.511B at $330.48 (nasdaq_quote_api) — in scope under $40B.

All figures below are copied from key_numbers.md, dcf_numbers.json, financials_history.csv or fundamentals.json — none are recomputed.

## What it is
A technical industrial distributor headquartered in Cleveland (fundamentals.json profile: SIC 5080 Wholesale-Machinery, Equipment & Supplies, NYSE). Two businesses: Service Center (local MRO distribution — bearings, power transmission, general maintenance parts, with repair and technical support) and Engineered Solutions (fluid power, flow control and automation — designed/integrated systems for OEM and industrial customers). Growth is organic MRO/engineered demand plus disciplined tuck-in acquisitions in a fragmented market (Hydradyne and IRIS Factory Automation closed in fiscal 2025, per research).

## Owner's earnings
**FY2026 (10-K, fiscal year ended 2026-06-30, from financials_history.csv):** operating cash flow $484,082,000; capex $23,565,000; SBC $12,904,000 (always a real cost, and small here).
- **Conservative owner's earnings FY2026: $447,613,000 = $11.82/share** (latest FY OE/share in key_numbers.md).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $410,552,000 — in the same ballpark as the conservative figure, which raises confidence in the base; this is a low-capex distributor, not a capital-intensive operator.
- OE positive 5 of the last 5 fiscal years. OE/share path: $5.52 (FY2021) → $4.03 → $7.78 → $8.50 → $11.68 → $11.82 (FY2026) — the FY2025 jump was operating-cash-flow driven (OCF $492,385,000 in FY2025 on revenue of $4,563,424,000, up only slightly from FY2024), so the level is real cash but the recent growth rate overstates the underlying revenue trend.
- Net debt $135,170,000 (0.31x normalized OE per diagnostics); operating lease liabilities are a further $221,144,000. Balance sheet at FY2026 (financials_history.csv): assets $3,009,973,000, liabilities $1,148,224,000, equity $1,861,749,000, total debt $262,300,000 against cash of $127,130,000 — see the CASH_INCLUDES_RESTRICTED flag below for the cash caveat.
- Capital return (fundamentals.json): dividends paid TTM $72,598,000 and buybacks TTM $317,218,000; DPS has grown for 16 years with no cut in the filed series (dps_ttm $1.99, 5-yr DPS CAGR 8.89%). Diluted shares fell to 37,857,000 (share CAGR -1.17%).

**Base used = normalized owner's earnings, median of the last 3 fiscal years: $11.68/share** (base_source: median_of_last_3_fy_oe_per_share; latest FY $11.82/share, normalized $11.68/share). No TTM pin: the latest fiscal year ended only 3.6 months ago, there is no STALE_FY flag, and fundamentals.json's TTM period is the same 2026-06-30 fiscal year. The median is not distorted here — it sits essentially on the latest year.

## Moat: 5/10 — moderate / narrow
Justification: a technical, service-heavy distributor with ROIC proxy sustained at 19.3–21.0% in FY2023–FY2026 and gross margin edging up from 28.9% (FY2021) to 30.3% (FY2026) in fundamentals.json — evidence of real, service-based pricing power and returns well above the cost of capital through recent years. But it holds only about 2% of a fragmented market, sells other manufacturers' branded products that customers can multi-source, and its demand is cyclical industrial MRO, so the moat is narrow rather than strong.
- FOR: Technical Engineered Solutions (fluid power, flow control, automation) — embedded engineering and specification work raises switching costs versus catalog distributors; ROIC proxy (fundamentals.json) 11.2% (FY2021), 16.9%, 21.0%, 21.0%, 19.3%, 21.0% (FY2026), on a gross margin of 28.9% (FY2021), 29.0%, 29.2%, 29.8%, 30.3%, 30.3% (FY2026); dense local service-center network supplying critical MRO parts — customer downtime cost dwarfs the part cost, making availability and technical support sticky; disciplined tuck-in M&A in a fragmented market plus buybacks, with the diluted share count falling (share CAGR -1.17%).
- AGAINST: Only about 2% share of a fragmented US industrial distribution market — no dominant scale versus Grainger or Fastenal; sells other manufacturers' branded products, so suppliers can sell direct and customers can multi-source commodity parts; demand is cyclical MRO/industrial production — FY2020-21 revenue was flat and OE is working-capital sensitive; pricing power is service-based, not product-based — gross margin is only about 30% and operating margin about 11%.
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — v5.4 final run (2026-10-18)
Growth recalibration (written reason): the engine's blended start is 10.06% (components: revenue CAGR 5y 8.95%, 3y 4.02%, latest rev YoY 8.84%, OE/share CAGR 2y 17.97%). The OE/share CAGR component is an artifact — OE/share jumped in FY2025 on an operating-cash-flow swing while revenue grew only slightly that year — and the blend sits well above the company's own forward guide. Recent prints: FY2026 revenue +8.84% (latest rev YoY, key_numbers.md) and Q4 FY2026 sales +10.4% year over year with organic growth +9.7% (Q4 release, via research), but fiscal 2027 guidance is for sales growth of 4.0% to 6.5% and EPS of $11.65–$12.15 (via research). Scenario starts were therefore recalibrated downward via offsets (-0.121 / -0.081 / -0.041 / -0.011 / +0.029 vs the blended start) to -2.0 / 2.0 / **6.0** / 9.0 / 13.0%: the base start sits inside the FY2027 guidance range, the bull start sits near the FY2026/Q4 prints, and the super-bull start above them is the upside case (automation/Engineered Solutions acceleration plus acquisition contribution), not a forecast. Probabilities 10/25/30/25/10; OE multipliers 0.75/0.90/1.00/1.10/1.25. Price $330.48.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -2.0% | 0.75 | Industrial downturn; MRO demand contracts, OE compresses | $59.41 | 4.63% |
| Bear | 25% | 2.0% | 0.90 | Growth below guidance; soft manufacturing through FY2027 | $84.26 | 5.67% |
| Base | 30% | 6.0% | 1.00 | FY2027 guidance range delivered, then fade over the CAP | $110.56 | 6.80% |
| Bull | 25% | 9.0% | 1.10 | FY2026/Q4 momentum persists; Engineered Solutions outgrows Service Center | $137.67 | 7.94% |
| Super bull | 10% | 13.0% | 1.25 | Automation acceleration plus accretive M&A on top of organic growth | $184.37 | 9.81% |

- **Probability-weighted: IV@15% $113.03 (-65.8% vs price), IV@12% $150.39, IV@10% $192.09, weighted IRR 6.92%, base-case IRR 6.80%**
- **Tier by numbers: D.** Bear→bull band is D→D (bear IRR 5.67%, bull IRR 7.94%); scenario range 4.63% – 9.81% — even the super-bull case is a D. Diagnostics (key_numbers.md): OE yield 3.53%, terminal value 18.9% of IV@15%, scenario spread 3.10x, net debt 0.31x normalized OE, 3.6 months since FY end.
- Hurdle prices: clears 15% at $113.03 (IV@15), 20% at $79.48 (IV@20), 25% at $61.04 (IV@25).

## Flags — every fragility flag resolved
- **CASH_INCLUDES_RESTRICTED** (the only cash tag filed for the latest fiscal year is the combined cash + restricted-cash total, CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents at $127,130,000 in financials_history.csv, with no separate restricted-cash tag): resolved in words — the restricted amount is not separately quantified in the computed outputs, so reported net debt of $135,170,000 is understated by that unknown amount. It does not change the verdict: total debt is only $262,300,000 and net debt is 0.31x normalized OE, so leverage is low on any plausible restricted slice, and no HIGH_NET_DEBT conclusion is being relied on — the D tier comes from price versus owner's earnings, not from the balance sheet.
- **WIDE_SCENARIO_SPREAD** (preliminary run only, 4.47x): the preliminary run at the unrecalibrated 10.06% blend carried this flag. In the final recalibrated run the spread is 3.10x (key_numbers.md diagnostics) and the flag no longer fires; confidence is still held at medium, not high.

## My thoughts / overlay
- The honest headline is the method range: the preliminary run on the engine's unrecalibrated blend (weighted IRR 8.13%, weighted IV@15% $140.05 in the preliminary dcf_numbers.json output) and this final guidance-anchored run (6.92%, $113.03) are both Tier D, by a wide margin. Anyone quoting one number for AIT without its method is hiding the ball, but no defensible method in this pass gets it near 15% at $330.48.
- Quality is not the debate: OE positive 5/5 years, ROIC proxy around 20%, gross margin slowly rising, net debt 0.31x normalized OE, SBC only $12,904,000 against OCF of $484,082,000, and a 16-year dividend growth record. This is a good business priced as if much faster growth were assured.
- Risks: US industrial-production cyclicality (the FY2027 guide already steps growth down to 4.0–6.5%); working-capital swings making OE lumpier than revenue (the FY2025 OE jump); supplier disintermediation and e-commerce/catalog competition (Grainger, Fastenal) on the commodity side of the catalog; acquisition integration as Engineered Solutions mix rises.

## Final verdict
- **Final tier: D** (weighted IRR 6.92% on the v5.4 final inputs; the preliminary-to-final method range is also D at both ends)
- Confidence: **Medium** (high on OE quality and the low leverage, medium on any single growth path — the scenario spread is 3.10x)
- One-liner: High-quality technical industrial distributor, moat 5/10 with ROIC around 20% — but at $330.48 the OE yield is only 3.53% and the weighted IRR is 6.92%; it clears 15% only near $113.03.
