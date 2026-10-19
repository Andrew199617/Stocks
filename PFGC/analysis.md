# PFGC — Performance Food Group Company
Engine 5.4.0 run, 2026-10-17. In scope (market cap $15.351B at $97.78, nasdaq_quote_api).

All figures below are copied from key_numbers.md, dcf_numbers.json, financials_history.csv or fundamentals.json — none are recomputed. Guidance and FY2026 release detail are paraphrased from the company's Q4/FY2026 release (Business Wire, 2026-08-12).

## What it is
One of the largest North American food distributors: Foodservice (broadline to independent and chain restaurants — the core), Convenience (Core-Mark, to convenience stores), and Specialty (Vistar — vending, office coffee, theaters). Over 350,000 customer locations per the company release. This is a scale-and-logistics business on razor-thin margins: FY2026 gross margin 11.93%, operating margin 1.31% (fundamentals.json).

## Owner's earnings
**FY2026 (10-K via EDGAR, from financials_history.csv):** operating cash flow $1,413,700,000; capex $384,100,000; SBC $51,500,000.
- **Conservative owner's earnings FY2026: $978,100,000 = $6.23/share** (key_numbers.md: latest FY OE/share $6.23, latest FY OE total $978.1M)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC, from financials_history.csv): $756,200,000 — below the conservative figure; the gap is working-capital build (inventories and receivables grew with cases and with advance inventory purchases noted in the release) plus the LIFO/deferred-tax non-cash items below. The OCF-based conservative figure is the cleaner series and is what the engine uses.
- OE positive 5 of the last 5 fiscal years (key_numbers.md), but the level swings hard — see OE_VOLATILE under Flags.
- Balance sheet: net debt $5.007B (key_numbers.md), lease liabilities $973.1M (dcf_numbers.json). No dividend; a $500M buyback was authorized in May 2025 but FY2026 repurchases were only $1.5M per the release — essentially no buyback tailwind, and share count is flat (share count CAGR 0.19%, key_numbers.md).

**Base used = normalized owner's earnings: $4.65/share** (median of the last 3 FY OE/share: FY2024 $4.65, FY2025 $4.20, FY2026 $6.23, from financials_history.csv; base_source: median_of_last_3_fy_oe_per_share). The latest FY ($6.23) is not used as the base: FY2026 OCF was flattered by $52.3M of income-tax refunds received (per the release) and by capex falling to $384.1M from $506.0M in FY2025, while FY2025 was depressed by Cheney Brothers integration. The median sits between those two distorted years. No STALE_FY flag — the fiscal year ended 3.7 months ago (key_numbers.md), so no TTM override was needed.

## Moat: 4/10 — weak-to-moderate
Justification: Scale as the #3 US food distributor, route density and a differentiated Convenience business give moderate advantages, but the service is largely undifferentiated, margins are ~1.3% operating, customers/suppliers have power, and ROIC has not stayed well above the cost of capital through a cycle.
- Evidence (fundamentals.json, roic_proxy and gross margin): ROIC proxy was 3.06% in FY2022, 7.76% in FY2023, 8.24% in FY2024, 6.14% in FY2025 and 6.63% in FY2026 — single digits, dipping toward 3% in a soft year. Gross margin over the last five fiscal years: 11.60% (FY2021), 10.33% (FY2022), 10.92% (FY2023), 11.29% (FY2024), 11.72% (FY2025), 11.93% (FY2026) — recovering from the Core-Mark mix trough but still below the 12.68–13.01% of FY2017–18. That evidence caps the moat at 4: a 7+ score would need ROIC durably well above the cost of capital, which this history does not show.
- FOR: #3 US food distributor — scale in procurement, logistics and route density smaller rivals cannot match; independent-restaurant focus (43.1% of Foodservice sales in Q4 FY2026) with Performance Brands private label and higher-touch service; diversified Convenience (Core-Mark) and Specialty (Vistar) segments peers cannot replicate in one house; dense Southeast footprint deepened by Cheney Brothers (acquired Oct 2024).
- AGAINST: Largely undifferentiated distribution — low switching costs, no long-term contracts with many customers, intense Sysco/US Foods competition; thin economics (gross margin 11.93%, operating margin 1.31% in FY2026; ROIC proxy 6.63%); supplier and product-cost inflation/deflation pass-through risk plus fuel, labor and insurance cost exposure; Convenience mix depends in part on cigarettes/alternative nicotine, a structurally declining category.
- A 4 gives CAP = 7.2 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 7.2 years, 15-year projection.

## DCF — final run (2026-10-17)
**Growth recalibration (written reason):** the engine's blended growth is 11.39%, but two of its components straddle an acquisition break — the 5-yr revenue CAGR of 17.48% spans the Core-Mark deal (see BASIS_BREAK) and the OE/share CAGR of 15.80% is off the depressed FY2024 base. The organic prints are much lower: revenue CAGR 3y 5.84%, latest revenue YoY 7.17% (key_numbers.md), FY2026 net sales growth of 7.2% and Q4 growth of 6.4% in the release, and FY2027 guidance of $72.5–$73.0B in net sales with Adjusted EBITDA of $2.125–$2.225B (release) — sales growing at roughly the FY2026 rate, EBITDA faster. Scenario starts were therefore set via offsets (−0.124 / −0.079 / −0.039 / +0.006 / +0.046 vs g_base) to −1.0 / 3.5 / **7.5** / 12.0 / 16.0%. Sanity check against the prints: the base start (7.5%) sits on the FY2026 sales print (7.2%) and the FY2027 sales guide; the bull start (12.0%) is above every sales print and is justified only as an OE/share path — guided double-digit EBITDA growth, Cheney synergies and mix shift to independents can grow OE/share faster than sales; the super-bull start (16.0%) exceeds even that and is held to a 5% probability. The super-bear start (−1.0%) is a restaurant-downturn case, below all recent prints by construction. Probabilities 15/30/30/20/5 put 45% on bear-or-worse (see OE_VOLATILE and HIGH_NET_DEBT). OE multipliers are the defaults 0.75/0.90/1.00/1.10/1.25. Price $97.78.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | -1.0% | 0.75 | Restaurant downturn, fuel/WC squeeze on a levered balance sheet | $24.97 | 5.60% |
| Bear | 30% | 3.5% | 0.9 | Case growth stalls, inflation pass-through lags costs | $35.65 | 7.09% |
| Base | 30% | 7.5% | 1.0 | Sales grow at the FY2026/guided rate, margins inch up | $46.14 | 8.54% |
| Bull | 20% | 12.0% | 1.1 | Guided EBITDA growth converts to OE/share; Cheney synergies land | $60.13 | 10.42% |
| Super bull | 5% | 16.0% | 1.25 | Sustained share gains plus real margin expansion | $79.29 | 12.83% |

- **Probability-weighted: IV@15% $44.28 (-54.7% vs price), IV@12% $58.89, IV@10% $75.18, weighted IRR 8.31%, base-case IRR 8.54%**
- **Tier by numbers: D.** Diagnostics (key_numbers.md): OE yield 4.76%, terminal value 18.8% of IV@15%, scenario spread 3.18x, net debt 6.86x normalized OE, 3.7 months since FY end.
- Hurdle-clearing prices (weighted path, key_numbers.md): 15% at $44.28, 20% at $31.15, 25% at $23.92. Even the super-bull IV@15% ($79.29) sits below the $97.78 price.

## Flags — every fragility flag resolved
- **BASIS_BREAK_SUSPECT**: named — the revenue history straddles three acquisitions: Reinhart Foodservice (closed Dec 2019), Core-Mark (closed Sep 2021; FY2022 was its first full year, and revenue in financials_history.csv jumps from $30,398,900,000 in FY2021 to $50,894,100,000 in FY2022), and Cheney Brothers (closed Oct 2024, a driver of FY2025–26 growth per the release). The 5-yr revenue CAGR (17.48%) therefore mixes acquired with organic growth and was not trusted; growth inputs were set from post-Core-Mark signals (3-yr CAGR 5.84%, latest YoY 7.17%, FY2027 guidance) that do not straddle the break.
- **OE_VOLATILE**: real — OE/share in financials_history.csv runs $0.11 (FY2022, the Core-Mark integration / COVID-recovery trough) to $6.23 (FY2026). Handled by the normalized median base ($4.65, not the latest $6.23) and by widening bear-or-worse probability to 45%.
- **NI_OCF_DIVERGENCE** (2024, 2025, 2026): explained, not an earnings-quality red flag. FY2026 net income was $359.3M against OCF of $1,413.7M (release/financials_history.csv); the gap is mainly non-cash depreciation and intangible amortization of $813.9M (financials_history.csv D&A), plus LIFO reserve and deferred-tax items in the release's cash-flow statement. A distributor carrying acquired intangibles and a large fleet/warehouse base will structurally report OCF well above net income. The base is OCF-derived throughout, so the divergence does not contaminate it.
- **HIGH_NET_DEBT**: net debt $5.007B is 6.86x normalized OE (key_numbers.md), plus lease liabilities of $973.1M (dcf_numbers.json). Against cash earnings it is less extreme — FY2026 Adjusted EBITDA was $1,929.4M per the release — but the leverage is real, interest is a material line, and it is why the bear cases carry 45% combined weight and stressed OE multipliers.
- **TIER_BAND**: bear-case tier D (7.09%) vs bull-case tier C (10.42%) — the verdict is sized to the bear end: D. Note the band is narrow in the only way that matters here — neither end clears 15%.

## My thoughts / overlay
- The honest headline is the method range: the preliminary run on engine defaults (moat 5, default probabilities/offsets) printed a weighted IRR of 10.37% and Tier C; the recalibrated final run prints 8.31% and Tier D. Both are far below the 15% hurdle at $97.78 — the disagreement is over how overvalued the stock is, not whether it clears.
- Quality is middling, not poor: OE-positive 5/5 years, FY2026 free cash flow of $1,029.6M per the release, and consistent independent-case share gains (organic independent case volume +5.9% in FY2026). The problem is price versus a ~1.3% operating-margin, ~6–8% ROIC business with $5.007B of net debt — at $97.78 the market is paying for margin expansion the five-year gross-margin and ROIC history (fundamentals.json) has not yet delivered.
- Risks to this verdict (i.e., what would make it too harsh): a US Foods combination (the two companies agreed to share information in 2025 after US Foods' approach was declined — any deal would reprice the stock on synergies, not on standalone OE); sustained gross-margin recovery toward the FY2017–18 level; faster deleveraging from the guided EBITDA step-up. None of those are in the OE base today.
- Margin of safety: there is none at this price on these numbers — the weighted IV@15% ($44.28) is 54.7% below the price, and even the 5%-probability super-bull IV@15% ($79.29) is below it.

## Final verdict
- **Final tier: D** (weighted IRR 8.31% on the final inputs; method range C to D across the day's defensible runs, neither clearing 15%)
- Confidence: **Medium** (high on the filing-derived OE and debt figures and on the direction — no defensible run clears the hurdle; medium on any single growth path for a business this cyclical and acquisition-shaped)
- One-liner: Solid #3 food distributor, moat 4/10 — does not clear 15% at $97.78 (weighted IRR 8.31%, weighted IV@15% $44.28); it clears 15% only below $44.28.
