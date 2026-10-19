# MLI — Mueller Industries, Inc.
Engine 5.4.0 run, 2026-10-17. All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.json, fundamentals.json, or the cited company releases — none are recomputed.

## What it is
Collierville, Tennessee industrial manufacturer (SIC 3350, nonferrous metals) fabricating products from copper, brass, aluminum and plastic across three segments — Piping Systems, Industrial Metals and Climate — for air/water/oil & gas distribution, climate comfort, food preservation, electrical transmission, medical, aerospace and automotive markets. It describes itself as the only vertically integrated North American manufacturer of copper tube & fittings, brass rod and forgings. Price $60.07 (nasdaq_quote_api). In scope under $40B: see the market-cap note under Thoughts.

## The share-basis break — read this first
Mueller announced a two-for-one forward stock split on June 1, 2026 (Business Wire): record date June 25, 2026, distribution after close June 30, 2026, split-adjusted trading from July 1, 2026, taking shares outstanding to approximately 221.1 million. The $60.07 price is post-split, and the Q2 2026 10-Q restates share counts on the post-split basis — but the FY2025 10-K was filed before the split, so the annual history in financials_history.csv is on the pre-split basis (FY2025 diluted shares 111,492,000; latest FY OE/share $5.92; normalized 3-yr median OE/share $5.24 — all pre-split).

The preliminary engine run scored that pre-split base against the post-split price and printed a weighted IRR of 14.94% and Tier C — an invalid, basis-mixing result, and a near-miss at the 15% hurdle that did not exist. The final run therefore uses the TTM base from ttm.py, whose share leg is the post-split count, and every per-share figure in the final score is on the post-split basis. This is the same share-basis defect family already documented for the sweep (NTNX, VIV, DD); the TTM route resolves it for this name without any override.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $755,444,000; capex $68,805,000; SBC $26,764,000 (always a real cost).
- **Conservative owner's earnings FY2025: $659,875,000** (latest FY OE total, key_numbers.md) — $5.92/share on the pre-split count.
- Maintenance version (from financials_history.csv): $676,596,000 — same ballpark as the conservative figure, which raises confidence.
- OE positive 5 of the last 5 fiscal years (the soft year in the longer history is FY2017, when conservative OE was negative).
- Balance sheet: net debt $-1.367B at FY2025 — i.e. net cash; cash $1,367,003,000 with no debt balance filed for FY2025 (net_debt_basis CURRENT_ONLY:LongTermDebtCurrent), lease liabilities $27,490,000. The Q2 2026 release reports cash and short-term investments of $1.42 billion and a current ratio of 4.8 to 1.
- Capital return (fundamentals.json): dividends paid TTM $130,746,000, buybacks TTM $76,439,000, DPS TTM $0.60; the quarterly dividend was raised to $0.175/share post-split in 2026.

**Base used = TTM owner's earnings through Q2 2026 (period ended 2026-06-27), from ttm.py (filing-direct, no hand math):**
- OCF: FY $755,444,000 − prior YTD $304,161,000 + current YTD $292,001,000 = **TTM $743,284,000**
- Capex: FY $68,805,000 − prior YTD $30,691,000 + current YTD $38,796,000 = **TTM $76,910,000**
- SBC: FY $26,764,000 − prior YTD $13,940,000 + current YTD $15,846,000 = **TTM $28,670,000**
- Shares (current-YTD weighted diluted, post-split): **221,506,000**
- **TTM OE total $637,704,000 → base OE/share $2.88** (base_source: ttm_json)
- The engine's normalized base ($5.24/share) was rejected as the base for one reason only: it is on the pre-split share basis (see above). It is still reported in key_numbers.md. On economics, the TTM total ($637.7M) sits just below the FY2025 total ($659.9M) — H1 2026 operating cash flow absorbed working capital as copper prices rose, despite higher net income.

## Moat: 6/10 — moderate, real but cyclical
Justification: dominant, vertically integrated North American copper tube/fittings and brass franchise with ROIC well above the cost of capital through the cycle, but the products are commodity fabrications with low switching costs and earnings are leveraged to copper prices and the construction cycle.
- FOR: Only vertically integrated North American manufacturer of copper tube & fittings, brass rod and forgings — structural scale/cost position. ROIC proxy (fundamentals.json) of 42.8% / 49.1% / 47.8% / 33.3% / 39.3% across FY2021–25, and 13.4% / 12.2% / 14.1% / 16.2% / 18.4% in the soft FY2016–20 years — above the cost of capital through a cycle. Pricing power via copper cost pass-through with spread capture — operating margin expanded from 10.25% (FY2020) to 22.94% (FY2025) and 22.96% TTM (fundamentals.json). Net-cash balance sheet funds dividends, buybacks and accretive M&A (Bison Metals Technologies, closed March 30, 2026, and Chicago Extruded Metals, both in Q2 2026). Established wholesale distribution and spec position in plumbing/HVACR; US tariffs on semi-finished copper imports favor the domestic footprint.
- AGAINST: Commodity fabrication products — low switching costs; competition from Wieland, Cambridge-Lee, Cerro Flow and imports. Earnings leveraged to COMEX copper and the construction cycle (roughly half of demand construction-linked); FY2017 owner's earnings were negative. Headline revenue growth is inflated by copper price pass-through (COMEX averaged $6.16/lb in Q2 2026, +30.6% YoY), not volume alone. Gross margin volatile — the Q2 2026 release reports 27.7% for the quarter vs 31.0% a year earlier (28.8% vs 29.2% for the half), and the prior-year quarter included a $36.3M insurance gain; fundamentals.json carries no annual gross-margin series for FY2021–25 (null), so the margin evidence quoted is the operating-margin and release figures. No recurring revenue or contractual lock-in — returns depend on sustaining a favorable metal spread.
- A 6 gives CAP = 9.8 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 9.8 years, 15-year projection.

## DCF — final run (2026-10-17)
Growth sanity check (mandatory): the blend is 8.83% (rev CAGR 5y 11.74%, rev CAGR 3y 1.62%, latest rev YoY 10.87%, OE/share CAGR 2y 6.30%). Recent prints: Q2 2026 net sales $1.43 billion, +25.5% YoY — but driven by higher selling prices on copper (COMEX +30.6%), the Bison acquisition and unit volume growth in all three segments, partly offset by the Sherwood divestiture; operating income rose only 1.9% as reported (+15.7% excluding the prior-year $36.3M insurance gain) and split-adjusted diluted EPS was $1.13 vs $1.11. Fundamentals TTM revenue is $4,661,137,000, +14.81% YoY. The base start of 8.8% therefore sits below the revenue prints (which are price-inflated) and above the 3-yr revenue CAGR — a defensible OE/share start. The super-bull start of 20.8% exceeds every recent OE print; it is kept at the default offset only as a 10%-probability sustained copper/volume upcycle case, which is the written reason. Default probabilities 10/25/30/25/10 and default OE multipliers 0.75/0.90/1.00/1.10/1.25 were used unchanged. Price $60.07.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -3.2% | 0.75 | Copper and construction roll over together; spread compresses | $13.76 | 5.15% |
| Bear | 25% | 3.8% | 0.90 | Volume flat, price tailwind fades, margins normalize down | $22.54 | 7.25% |
| Base | 30% | 8.8% | 1.00 | Blend growth decays over the 9.8-yr CAP | $31.28 | 9.28% |
| Bull | 25% | 13.8% | 1.10 | Volume + acquisitions + tariff shelter sustain the spread | $42.95 | 11.77% |
| Super bull | 10% | 20.8% | 1.25 | Sustained copper upcycle with volume growth | $66.45 | 16.09% |

- **Probability-weighted: IV@15% $33.78 (−43.8% vs price), IV@12% $45.64, IV@10% $58.98, weighted IRR 9.87%, base-case IRR 9.28%**
- **Tier by numbers: D.** Diagnostics (key_numbers.md): OE yield 4.79%, terminal value 20.5% of IV@15%, scenario spread 4.83x, net debt −4.26x normalized OE, 9.7 months since FY end.
- Hurdle-clearing prices (weighted path): 15% at $33.78 · 20% at $23.25 · 25% at $17.55.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.7 months ago): resolved by construction — the base is the TTM figure from ttm.py through 2026-06-27, quoted above, which also puts the base on the post-split share basis.
- **WIDE_SCENARIO_SPREAD** (4.83x): real — a copper-levered cyclical's outcome range IS wide. Confidence is capped at medium, and the verdict is sized to the bear end.
- **BIG_NET_CASH** (net debt −4.26x normalized OE): stated from the filing — cash $1,367,003,000 at FY2025 with no debt balance filed, $1.42 billion of cash and short-term investments at Q2 2026. A material part of the $60.07 price is this cash pile, not the operating business; the cash cushions the downside but does not make the operating business clear 15% at this price.
- **TIER_BAND** (bear D at 7.25% vs bull C at 11.77%): the whole band sits below the 15% hurdle — even the bull case does not reach Tier B. Verdict sized to the bear end: D.

## My thoughts / overlay
- The honest headline is the basis correction: the same company prints Tier C / 14.94% weighted IRR on the invalid pre-split base and Tier D / 9.87% on the correct post-split TTM base. Anyone quoting the preliminary run without its share basis is hiding the ball. No judgment override was needed or used — the fix is the engine's own --ttm route.
- Market-cap note: key_numbers.md prints an estimated market cap of $6.697B, built from the post-split price and the pre-split diluted count (111,492,000). The DEI shares outstanding in dcf_numbers.json are 221,181,388 (as of 2026-07-17) — roughly double — so the true market cap is roughly double the printed estimate and still well under the $40B scope line either way.
- Quality is not the debate: OE-positive 5/5 years, ROIC proxy 33–49% in the current era, net cash, a raised dividend, and two accretive-looking core-metals acquisitions closed in 2026. The debate is price: at $60.07 the buyer pays for the bull case and gets the base case. Even the super-bull scenario (10% probability) only just clears 15%.
- Q2 2026 quality check: revenue beat was price-led (COMEX +30.6%); underlying operating income growth ex-insurance-gain was 15.7%, volumes grew in all three segments, and backlogs were described as strong with demand strengthening in commercial, industrial and electrical markets. None of that rescues the valuation at $60.07 — it supports the franchise, not the price.

## Final verdict
- **Final tier: D** (weighted IRR 9.87% on the post-split TTM base; bear→bull band D→C)
- Confidence: **Medium** (high on OE quality and the balance sheet; the scenario spread is 4.83x and the annual per-share history is on a dead share basis)
- One-liner: High-quality cyclical metals franchise, moat 6/10 — on the post-split TTM base it does not clear 15% at $60.07 (weighted IRR 9.9%, weighted IV@15% $33.78); it clears 15% only at or below ~$33.78.
