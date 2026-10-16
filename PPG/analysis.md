# PPG — PPG Industries, Inc.
v5 run, 2026-10-15. In scope: market cap $24.414B at $107.50 (nasdaq_quote_api), under the $40B cutoff.

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.py output, or financials_history.csv — none are recomputed.

## What it is
One of the top global coatings makers alongside Sherwin-Williams and AkzoNobel: automotive OEM and refinish coatings, aerospace coatings, protective and marine, packaging, and architectural coatings outside the US/Canada (that architectural business was divested after a portfolio review; the company has been pruning non-core assets — European/Australian traffic solutions and a silicas review were part of the same program in 2023). End markets are cyclical: auto production, construction, and industrial activity. Q2 2026 (reported July 28, 2026): net sales $4,495M, +7% year over year (organic +4%, volumes +2%, price +2%, growth in 8 of 9 businesses led by aerospace); adjusted EPS $2.23 vs $2.22 a year earlier — sales grew, earnings did not. Full-year 2026 adjusted EPS guidance reaffirmed at $7.70–$8.10. Q3 2026 results are due October 27, 2026.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $1,941M; capex $778M (tag PaymentsToAcquirePropertyPlantAndEquipment); SBC $46M (always a real cost, but small here).
- **Conservative owner's earnings FY2025: $1,117M = $4.92/share** (engine base_oe_latest_per_share $4.9185)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $1,186M — same ballpark as the conservative figure, which supports the base.
- OE positive 5 of the last 5 fiscal years, but the totals swing hard: $1,134M (2021), $443M (2022), $1,839M (2023), $657M (2024), $1,117M (2025) — a working-capital and raw-material cycle, not a steady compounder.
- Net debt $5,145M (dcf_numbers.json) — 4.26x normalized OE per diagnostics. This is a levered equity stub on a cyclical cash stream.
- Share count is shrinking slowly: diluted shares 227.1M in FY2025, share_cagr −1.45%/yr, which the engine credits as a +1.45pp growth adjustment. Q2 2026 buybacks were $75M in the quarter, $175M year to date.

**Base used = TTM owner's earnings from ttm.py (filing-direct, no hand math). ttm.json's latest YTD period ends 2026-03-31:**
- OCF: FY $1,941M − prior YTD −$18M + current YTD $33M = **TTM $1,992M**
- Capex: FY $778M − prior YTD $209M + current YTD $196M = **TTM $765M**
- SBC: FY $46M − prior YTD $23M + current YTD $11M = **TTM $34M**
- Shares (current-YTD weighted diluted): **224,400,000**
- **TTM OE total $1,193M → base OE/share $5.32** ($5.3164, base_source: ttm_json)
- The engine's normalized base (median of last 3 FY) is $4.92/share, identical to the latest FY here. The TTM base was used because it is the more current figure and is higher; using it is the generous choice, and the verdict still fails the hurdle by a wide margin — so the choice of base does not drive the conclusion.

## Moat: 5/10 — moderate, not wide
Justification: real scale, technical-service and qualification stickiness in aerospace/auto coatings, and demonstrated pricing power, but no dominant consumer/store moat (Sherwin-Williams is stronger in US architectural, a business PPG exited), commodity raw-material exposure, and low-single-digit long-run growth (rev CAGR 5y 2.79%, 3y 0.55%).
- FOR: Top-tier global scale alongside Sherwin-Williams/AkzoNobel with manufacturing and distribution reach (including the ~5,200-location Comex concessionaire network in Mexico cited in 2023 results calls); qualification and technical-service switching costs in aerospace and automotive OEM/refinish coatings, where a coating failure is far more expensive than the coating; demonstrated pricing power — selling prices +2% in Q2 2026 after the 2022–23 raw-material pass-through cycle; diversified end markets (aerospace backlog and growth cushioned the 2022–24 auto/construction swings).
- AGAINST: Sherwin-Williams holds the stronger US architectural position and PPG exited US/Canada architectural coatings — an admission that part of the portfolio had no moat; raw-material (resins, titanium dioxide) cost volatility it can pass through only with a lag — 2022 conservative OE fell to $443M; end markets are cyclical (auto builds, housing, industrial production); AkzoNobel, Axalta, Nippon Paint and regional players contest every segment; long-run revenue growth is low-single-digit at best (3y CAGR 0.55%, latest FY YoY +0.19%).
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — v5 final run (2026-10-15)
Growth sanity check (written reasons): the engine's blended growth is 0.37% and g_base 1.83% after the +1.45pp buyback adjustment. The base start (1.83%) sits below Q2 2026's prints (sales +7% total, +4% organic) — deliberately: Q2 adjusted EPS was flat year over year ($2.23 vs $2.22) despite the sales growth, FY2025 revenue grew only +0.19%, the 3-year revenue CAGR is 0.55%, and OE/share CAGR over 2 years is −20.34%. One quarter of price/volume-led sales growth with no earnings conversion does not reset the base rate. In the other direction there is no cap problem: the bull start (6.83%) roughly matches Q2's total sales growth and the super-bull start (13.83%) is well above anything recently printed, so the upside cases are generous, not suppressed. Probabilities are the defaults 10/25/30/25/10 — the 35% cumulative bear weight is the OE-volatility and leverage adjustment; OE multipliers are the defaults 0.75/0.90/1.00/1.10/1.25. Price $107.50.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -10.0% | 0.75 | Auto/construction downturn repeats 2022; WC and raw materials bite a levered balance sheet | $19.36 | 4.40% |
| Bear | 25% | -3.2% | 0.90 | Flat volumes, price pass-through lags input costs again | $30.95 | 5.90% |
| Base | 30% | 1.8% | 1.00 | Low-single-digit growth on the TTM base, buyback tailwind included | $42.39 | 7.40% |
| Bull | 25% | 6.8% | 1.10 | Q2 2026 sales momentum converts to earnings; aerospace keeps compounding | $57.39 | 9.33% |
| Super bull | 10% | 13.8% | 1.25 | Sustained share gains plus margin recovery to a new profile | $86.96 | 12.82% |

- **Probability-weighted: IV@15% $45.43 (−57.7% vs price), IV@12% $60.04, IV@10% $76.29, weighted IRR 7.84%, base-case IRR 7.40%**
- **Tier by numbers: D.** Diagnostics (dcf_numbers.json): OE yield 4.95%, terminal value 18.2% of IV@15%, scenario spread 4.49x, net debt 4.26x normalized OE, 9.5 months since FY end.
- The decisive fact: even the super-bull case (IV@15% $86.96, IRR 12.82%) does not clear the 15% hurdle at $107.50. This is not a close call that hinges on the base or the moat.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.5 months ago): resolved by construction — the base is the TTM figure from ttm.py, inputs quoted above (ttm.json YTD through 2026-03-31), cross-checked against the reported Q2 2026 quarter (sales +7%, adjusted EPS flat, guidance reaffirmed), which does not suggest a step-change in OE since the TTM window.
- **OE_VOLATILE** (OE/share spans >3x over 5 years): real and structural — conservative OE totals ran $443M (2022) to $1,839M (2023) to $657M (2024) on the working-capital/raw-material cycle. Handled by using normalized/TTM bases rather than any single year, and by the 35% cumulative bear-or-worse probability weight.
- **NI_OCF_DIVERGENCE** (2023): FY2023 net income was $1,270M vs operating cash flow $2,411M (financials_history.csv). Two drivers, both identified: (1) a working-capital release — management reported working capital down ~$300M through Q3 2023, mainly inventories, and the CSV's ΔNWC for 2023 is −$476M, i.e. cash came in that earnings had counted earlier; (2) Q4 2023 reported net income of $90M vs adjusted net income of $363M — below-the-line charges depressed reported NI without a matching cash outflow. Consequence: 2023's OCF-based OE is flattered by a one-time WC release, which is exactly why neither the base (TTM) nor the normalized median leans on 2023 alone.
- **WIDE_SCENARIO_SPREAD** (4.49x): real — the outcome range for a cyclical, levered coater is wide. Confidence is capped at medium per the rule, and the verdict does not depend on narrowing the spread: every scenario, including super bull, prices below the current quote at a 15% discount.
- **HIGH_NET_DEBT** (net debt 4.26x normalized OE; flag text 4.3x): folded into the verdict — $5,145M of net debt against a normalized OE stream that has printed as low as $443M in a bad year means the equity case has no cushion; the bear cases carry 0.75–0.90 OE multipliers and still may be kind. Leverage is a reason the tier stays D with no override, not a rounding issue.

## My thoughts / overlay
- PPG is a decent business priced like a much better one on an owner's-earnings basis. An OE yield of 4.95% on the TTM base, low-single-digit blended growth, and 4.26x net-debt-to-OE cannot produce a 15% IRR at $107.50 under any scenario this model can defend — the method range here is narrow in tier terms (median base instead of TTM: weighted IRR 7.45%, IV@15% $42.03 on the preliminary run — still D), even though the IV range across scenarios is wide.
- What would change the answer: a price near the weighted IV@15% of $45.43 clears 15% on the weighted case; even the super-bull IV@15% ($86.96) is below today's price, so there is no margin-of-safety entry point anywhere near $107.50. Alternatively, evidence that Q2 2026's sales growth starts converting into OE (it has not yet — adjusted EPS was flat) would lift the base, but that is a hope, not a filing.
- SBC is a non-issue here ($34M TTM against $1,992M TTM OCF); the risks are cyclicality, raw-material lags, and leverage, not dilution — the share count is shrinking.

## Final verdict
- **Final tier: D** (weighted IRR 7.84% on the v5 final inputs; no tier override — the numbers and the overlay agree)
- Confidence: **Medium** (capped by WIDE_SCENARIO_SPREAD; high on the direction — even the super-bull case fails the hurdle — medium on any single IV point estimate)
- One-liner: Moderate-moat (5/10) global coatings leader, but at $107.50 owner's earnings clear only 7.8% weighted — IV@15% $45.43, and even the super-bull case ($86.96) sits below the price; it would need to fall to ~$45 to clear the 15% hurdle.
