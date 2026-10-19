# NWSA — News Corporation

Engine 5.4.0 run, 2026-10-16. All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.json/fundamentals.json or financials_history.csv — none are recomputed.

## What it is
Murdoch-controlled media conglomerate (Class A NWSA / Class B NWS, dual class; the family holds ~14% economically and ~40%+ of the vote). Five segments: Dow Jones (WSJ, Barron's, MarketWatch, Risk & Compliance data), Digital Real Estate (majority-owned REA Group in Australia; Move/Realtor.com in the US), Book Publishing (HarperCollins), News Media (NY Post, The Sun, The Times, Australian papers), and Other. Fiscal year ends June 30. Foxtel was sold in March 2025, so recent history is on a continuing-operations basis. Market cap (est) $16.741B — in scope under $40B.

## Owner's earnings
FY2026 (10-K via EDGAR, financials_history.csv): revenue $9,028M, operating cash flow from continuing operations $1,237M, capex $426M, SBC $77M.
- **Conservative owner's earnings FY2026: $734.0M = $1.31/share** (latest FY OE/share).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC, from financials_history.csv): $806M — same ballpark, modestly higher; the conservative OCF-based figure is the one used.
- **Base used = median of last 3 FY OE/share: $1.13** (base_source: median_of_last_3_fy_oe_per_share). The FY2025 leg ($0.85/share) was depressed by Foxtel-exit-era costs, and FY2026's $1.31 is a single strong year (Q4 segment EBITDA +31%); the median is the defensible middle. No STALE_FY flag — FY2026 ended 3.5 months ago and the 10-K is filed, so no TTM override was needed.
- OE positive 5 of the last 5 fiscal years. Balance sheet: net debt $-106.0M (net cash on the engine's debt tags) plus $926M of operating lease liabilities — leverage is not a story here. Net debt / normalized OE: -0.17x.
- Caveat that cuts against the stock: consolidated OCF includes 100% of REA Group's cash flow while REA has a large minority interest; the engine does not deduct noncontrolling interests, so attributable OE/share is somewhat overstated. The verdict is D anyway, and this makes it more so.
- Capital return: a $1B buyback authorized July 2025 was ~53% used by mid-October 2026 (~$535M spent across both classes); share count CAGR is -1.19%/yr, already credited in the growth blend via the +1.19% share-count adjustment.

## Moat: 5/10 — moderate/narrow conglomerate average
Justification: Dow Jones and REA are real franchises, but print news is in structural decline, Move is #2, books are hit-driven, and consolidated returns are modest — owner's earnings of $650-734M on $8.5B of equity is high-single-digit. The `roic_proxy` series is absent from fundamentals.json (no mergeable operating-income tag in EDGAR; the company reports segment EBITDA), and gross margin is likewise untagged — so there is no computed ROIC history showing through-cycle returns well above the cost of capital, which a 7+ would require.
- FOR: Dow Jones professional-information franchise — WSJ/Barron's digital subscriptions (6.26M digital-only across Dow Jones news products), enterprise/B2B now over half of segment profit, Risk & Compliance revenue +16% in FY26 to $392M: recurring data revenue with pricing power; REA Group's dominant Australian portal with listing network effects; HarperCollins as #2 global trade publisher with a deep backlist; scarce premium content gaining AI-licensing value (OpenAI and Meta content deals).
- AGAINST: News Media print in structural decline; Move/Realtor.com #2 to Zillow in a frozen US housing-transaction market; book publishing hit-driven; housing-cycle exposure on both sides of the Pacific; dual-class Murdoch control and a persistent conglomerate discount.
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — 5.4 final run (2026-10-16)
Growth blend 6.47% (rev CAGR 5y -0.72% · rev CAGR 3y 4.06% · latest rev YoY 6.81% · OE/share CAGR 2y 7.70%, revenue components adjusted +1.19% for the shrinking share count). **Sanity check against prints:** FY2026 revenue grew 6.81% and Q4 FY26 revenue +11%, Total Segment EBITDA +15% for the year and +31% in Q4. The base start (6.5%) sits right on the latest FY print. The bull start (11.5%) matches the Q4 revenue print and is below FY26 EBITDA growth. The super-bull start (18.5%) is above every revenue print — written reason: it is an OE/share (not revenue) path, and FY26 OE/share grew far faster than revenue on margin expansion plus buybacks off a depressed FY25 base; as a 10% tail assuming Dow Jones EBITDA compounds toward management's $1B Dow Jones EBITDA pathway while REA and Move ride a housing recovery, it is a tail, not a forecast. Defaults kept: probabilities 10/25/30/25/10, offsets −12/−5/0/+5/+12pp, OE multipliers 0.75/0.90/1.00/1.10/1.25. Price $29.98.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -5.5% | 0.75 | Print decline accelerates, housing stays frozen, AI disrupts news discovery | $4.98 | 4.37% |
| Bear | 25% | 1.5% | 0.9 | Dow Jones growth stalls at low-single digits; REA cycle turns | $8.01 | 5.81% |
| Base | 30% | 6.5% | 1.0 | Current trajectory: DJ mid-single-digit growth, digital real estate compounding | $10.96 | 7.21% |
| Bull | 25% | 11.5% | 1.1 | Q4 momentum holds; housing volumes recover; AI licensing scales | $14.82 | 8.99% |
| Super bull | 10% | 18.5% | 1.25 | DJ EBITDA pathway + housing boom + sustained double-digit OE/share growth | $22.39 | 12.18% |

- **Probability-weighted: IV@15% $11.73 (−60.9% vs price), IV@12% $15.69, IV@10% $20.11, weighted IRR 7.61%, base-case IRR 7.21%.**
- **Tier by numbers: D** — and the band is one-sided: bear tier D, bull tier D. Even the super-bull scenario (12.18% IRR) does not clear the 15% hurdle at $29.98.
- Hurdle-clearing prices (weighted path): 15% at $11.73 · 20% at $8.19 · 25% at $6.26.
- Diagnostics: OE yield 3.78%, terminal value 19.4% of IV@15%, scenario spread 4.49x, net debt −0.17x normalized OE, 3.5 months since FY end.

## Flags — every fragility flag resolved
- **NI_OCF_DIVERGENCE (2024, 2026):** In FY2026, total net income was $573M vs OCF of $1,237M — but net income from continuing operations was $743M (FY26 earnings release); the difference is discontinued-operations losses left over from the Foxtel exit. The remaining gap from $743M to $1,237M is mostly non-cash D&A ($485M) and SBC ($77M). In FY2024, net income of $266M vs OCF of $1,098M: D&A ($440M) and SBC ($91M) explain roughly $531M of the ~$832M gap, with the rest being non-cash charges and tax/working-capital timing in the Foxtel held-for-sale period — the income statement took charges the cash flow statement didn't. In both years the divergence is non-cash or discontinued; OE is built on OCF, so the base is not contaminated.
- **WIDE_SCENARIO_SPREAD (4.49x):** real — the range runs from a melting-print conglomerate to a compounding professional-information business. Confidence is set to low (also for the conglomerate/NCI caveat above), and the verdict is sized to the conservative end. It changes nothing here: every scenario, including super bull, is Tier D at this price.

## My thoughts / overlay
- The honest caveat runs the other way from most D names: a consolidated owner's-earnings DCF is structurally unkind to News Corp, because the market prices it on a sum-of-the-parts basis — the listed REA Group stake and Dow Jones are routinely valued by analysts at a large fraction of (or more than) the entire market cap, with News Media and HarperCollins thrown in at conglomerate-discount values. If the parts were ever separated or the discount closed, value could appear that this cash-flow model cannot see. That is an asset-value argument, not an earnings-power one, and this sweep scores earnings power — on that basis the stock is expensive: a 3.78% OE yield and a 7.61% weighted IRR at $29.98.
- Operating momentum is genuinely the best in years (FY26 revenue +7%, segment EBITDA +15%, FCF $811M, +42%) — and the price already pays for it and more. The gap to the hurdle is not a rounding error: the stock would need to fall ~61% to ~$11.73 for the weighted path to clear 15%.
- Watch items: pace of the remaining ~$465M buyback, Dow Jones EBITDA trajectory toward the $1B pathway, US housing volumes for Move, and any Murdoch-trust/simplification event that attacks the conglomerate discount (the one catalyst this model under-weights).

## Final verdict
- **Final tier: D** (weighted IRR 7.61%; bear 5.81% → bull 8.99%, all scenarios D)
- Confidence: **Low** (wide scenario spread, conglomerate mix, NCI overstatement of attributable OE)
- One-liner: Real franchises (Dow Jones, REA) inside a mediocre-return conglomerate, moat 5/10 — at $29.98 the $1.13 median-base OE/share yields only a 7.6% weighted IRR (weighted IV@15% $11.73); it clears 15% only at ~$11.73, so Tier D.
