# GIS — General Mills, Inc.
Engine 5.4.0 run, 2026-10-16. Price $32.81 (nasdaq_quote_api). Market cap est. $17.645B. In scope under $40B.

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.json, financials_history.csv, or fundamentals.json — none are recomputed.

## What it is
Branded packaged-food major: cereal (Cheerios), snacks (Nature Valley), meals and baking (Betty Crocker, Pillsbury, Old El Paso), Häagen-Dazs, and premium pet food (Blue Buffalo). It is in a portfolio-reshaping downcycle — the U.S. yogurt business was divested (a $1,049.4M divestiture gain sits in FY2026), Brazil was sold after the fiscal year-end (completed Sept. 2, 2026), and the mainland China Häagen-Dazs shops sale is pending — while North America Retail volumes shrink.

## Owner's earnings
**FY2026 (10-K via EDGAR, financials_history.csv):** operating cash flow $2,166,200,000; capex $539,900,000; SBC $79,400,000.
- **Conservative owner's earnings FY2026: $1.547B = $2.88/share** (key_numbers.md: latest FY OE total $1.547B, latest FY OE/share $2.88)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): −$408,200,000 — meaningless this year because FY2026 net income (−$87.6M) was crushed by non-cash impairments and a divestiture-related valuation loss (see NI_OCF_DIVERGENCE below) that the NI-based formula cannot see past; the OCF-based conservative series is the one used throughout.
- OE positive 5 of the last 5 fiscal years. Net debt $13.084B (basis LongTermDebtNoncurrent+LongTermDebtAndCapitalLeaseObligationsCurrent+ShortTermBorrowings), plus lease liabilities $402,400,000 not in that basis. Dividend $2.44/share paid in FY2026.

**Base used = normalized owner's earnings, median of the last 3 fiscal years: $3.95/share** (base_source: median_of_last_3_fy_oe_per_share; FY2024 $4.20, FY2025 $3.95, FY2026 $2.88 per financials_history.csv). The median is the engine's normalized base and is not stale (FY ended 4.5 months ago); it deliberately averages the pre-downcycle years with FY2026 rather than pinning the base to the trough year.

**TTM cross-check, from ttm.py (filing-direct, no hand math) — NOT used as the base:**
- OCF: FY $2,166,200,000 − prior YTD $397,000,000 + current YTD $297,800,000 = **TTM $2,067,000,000**
- Capex: FY $539,900,000 − prior YTD $109,500,000 + current YTD $90,500,000 = **TTM $520,900,000**
- SBC: FY $79,400,000 − prior YTD $15,100,000 + current YTD $21,800,000 = **TTM $86,100,000**
- Shares (current-YTD weighted diluted): **537,900,000**
- **TTM OE total $1,460,000,000 → $2.71/share**
- The TTM figure runs below even the trough FY2026 figure, and its OCF leg is depressed by cash taxes on the yogurt divestiture gain (Q1 FY2027 reporting attributes the OCF decline mainly to taxes-payable changes including tax on that gain). It is therefore quoted as the current run-rate and used for the method range below, not as the base.

## Moat: 5/10 — moderate / narrow
Justification: iconic brands (Cheerios, Betty Crocker, Pillsbury, Nature Valley, Blue Buffalo) and shelf/distribution scale, with ROIC_proxy of 11-13% in FY2022-25 and gross margin held in a 32.6-34.9% band — above cost of capital but narrowing, not wide-moat grade; pricing power is now exhausted (private-label share gains, volumes falling), and the FY2026 North America Pet goodwill impairment shows the premium pet franchise was overpaid for and is weakening.
- FOR: iconic brand portfolio (Cheerios, Betty Crocker, Pillsbury, Nature Valley, Old El Paso, Häagen-Dazs, Blue Buffalo) with national shelf space and distribution scale; ROIC_proxy stayed 11.1-13.2% across FY2022-25 (fundamentals.json: 13.16% / 12.82% / 12.59% / 11.12%) — above cost of capital through the inflation cycle; gross margin held in a narrow band over the last five fiscal years (33.7% / 32.6% / 34.9% / 34.6% / 33.6%, fundamentals.json) despite input-cost inflation; category positions across cereal, snacks, meals, baking and premium pet that retailers must stock.
- AGAINST: pricing power exhausted — the 2022-23 price hikes widened the gap to private label, which is taking unit share in cereal and snacks, and volumes are falling; ROIC trend is down (13.2% FY2022 → 11.1% FY2025; reported FY2026 3.42% on impairment-crushed operating income) and gross margin is flat, not expanding; FY2026 impairments — $1,500M North America Pet goodwill plus $250M Nudges/True Chews brands, plus a $53M Uncle Toby's charge in Q2 — are an admission the Blue Buffalo-era pet moat is narrower than paid for; GLP-1 drugs and value-seeking consumers shrink stomach share for cereal/snack categories; net debt $13.084B is 6.16x normalized OE and buybacks are paused for deleveraging, removing the per-share tailwind.
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — 5.4 final run (2026-10-16)
Growth sanity check: the engine blend is −0.50% (rev CAGR 5y 0.33%, 3y −2.84%, latest rev YoY −5.45%, OE/share CAGR 2y −17.13%). Actual recent prints: FY2026 revenue −5.45% (divestiture-affected), Q1 FY2027 revenue −3% with organic sales essentially flat, and reaffirmed FY2027 guidance of organic net sales −1.5% to +0.5%, adjusted operating profit −8% to −13% in constant currency, adjusted EPS $3.00–$3.20 vs FY2026 adjusted $3.55. The base start (−0.5%) sits at the guidance midpoint. The preliminary run's default bull (+4.5%) and super-bull (+11.5%) starts were recalibrated down — no recent print or guidance supports them for a mature packaged-food portfolio; offsets used −0.075 / −0.035 / 0.00 / +0.03 / +0.06, giving starts of −8.0% / −4.0% / **−0.5%** / +2.5% / +5.5%. Probabilities were skewed bearish to 15/30/30/15/10 (defaults 10/25/30/25/10) on the down-guidance, the paused buyback, and 6.16x leverage; OE multipliers at the defaults 0.75/0.90/1.00/1.10/1.25. Price $32.81.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | -8.0% | 0.75 | Volume erosion accelerates, pet weakens again, leverage forces cuts | $15.64 | 7.99% |
| Bear | 30% | -4.0% | 0.90 | FY2027 down-guidance repeats; private label keeps taking share | $22.20 | 10.73% |
| Base | 30% | -0.5% | 1.00 | Guidance-midpoint sales, OE/share flat-to-down then fading to terminal | $28.56 | 13.33% |
| Bull | 15% | 2.5% | 1.10 | Innovation/renovation restores modest volume growth; deleveraging resumes buybacks | $35.61 | 16.06% |
| Super bull | 10% | 5.5% | 1.25 | Pet recovers, GLP-1 companion products land, OE compounds mid-single-digit | $45.84 | 19.77% |

- **Probability-weighted: IV@15% $27.50 (−16.2% vs price), IV@12% $35.88, IV@10% $45.17, weighted IRR 12.92%, base-case IRR 13.33%**
- **Tier by numbers: C.** Bear tier C (10.73%), bull tier B (16.06%) — see TIER_BAND. Diagnostics (key_numbers.md): OE yield 12.03%, terminal value 17.0% of IV@15%, scenario spread 2.93x, net debt 6.16x normalized OE, 4.5 months since FY end.
- Hurdle-clearing prices: 15% at $27.50, 20% at $19.87, 25% at $15.60.

## Flags — every fragility flag resolved
- **BUYBACK_TAILWIND** (share count shrinking 3.6%/yr, share count CAGR −3.64%): already credited via the +3.64pp growth adjustment in the blend — and explicitly not extrapolated in the verdict: management said in Q1 FY2027 reporting that buybacks are paused near term in favor of debt reduction toward a 3x net debt/adjusted EBITDA target, so the forward per-share tailwind is smaller than the historical one the blend credits. That is one reason the scenario starts were recalibrated down and the probabilities skewed bearish.
- **NI_OCF_DIVERGENCE** (FY2026 net income −$87.6M vs OCF $2,166.2M): the one-offs are identified and are non-cash or non-operating — restructuring/transformation/impairment costs of $2,970.8M for FY2026 ($2,808.0M in Q4 alone), comprising a $1,500M non-cash goodwill impairment on the North America Pet reporting unit and $250M on the Nudges and True Chews brand intangibles (interim assessment triggered by the sustained market-cap decline and higher discount rates), a $53M Uncle Toby's impairment in Q2, and a $1,032M non-cash pre-tax valuation loss on the planned Brazil divestiture; partly offset by the $1,049.4M divestiture gain (U.S. yogurt). Net income is unusable for FY2026 (the maintenance OE version prints −$408.2M); the OCF-based conservative OE is unaffected by the non-cash charges, which is why it is the series used throughout.
- **HIGH_NET_DEBT** (net debt $13.084B, 6.16x normalized OE in key_numbers.md; 6.2x in the flag): real and stressed — bear/super-bear OE multipliers of 0.90/0.75 sit on top of the leverage, lease liabilities of $402,400,000 are on top of the net-debt basis, and the dividend ($2.44/share paid FY2026) plus interest compete with OE. This is a return problem, not a solvency one: OE has been positive 5/5 years and management's stated priority is deleveraging, with buybacks already sacrificed to it.
- **TIER_BAND** (bear C 10.73% vs bull B 16.06%): the verdict spans tiers, so it is sized to the bear end — final tier C, and on the TTM base (below) the same scenarios print Tier D.
- Preliminary run also carried WIDE_SCENARIO_SPREAD (4.08x); the recalibrated growth starts narrowed the final spread to 2.93x, but confidence is still capped at low by the tier band, the leverage, and the base method range.

## My thoughts / overlay
- The honest headline is the method range: on the normalized median base ($3.95/sh) the weighted IRR is 12.92% (Tier C, IV@15% $27.50); the identical scenario set on the TTM base ($2.71/sh from ttm.py) prints a weighted IRR of 9.59%, Tier D, IV@15% $18.90. The current run-rate supports the lower end; the median base assumes a partial normalization that FY2027 guidance (adjusted EPS $3.00–$3.20, down from $3.55) does not yet promise.
- This is a quality-franchise-at-a-full-price story, not a collapse: even the super-bull case (5.5% start, 1.25x OE) yields only 19.77% — the $32.81 price already pays for a recovery. The market has noticed the other side: the stock fell ~22% in September 2026 around the Q1 print.
- Watch items for pass 2: whether North America Retail volumes stabilize, further pet impairments after the $1,500M write-down, the pace of deleveraging vs the 3x target, and whether the $750M FY2027 cost-savings target offsets the guided profit decline.

## Final verdict
- **Final tier: C** (weighted IRR 12.92% on the normalized base; bear C, bull B; TTM base prints D — size to the conservative end)
- Confidence: **Low** (tier band, 6.16x leverage, and a C→D method range across defensible bases)
- One-liner: Solid branded-food franchise, moat 5/10, in a volume/impairment downcycle — does not clear 15% at $32.81 (weighted IRR 12.9% on the normalized base, IV@15% $27.50; on the TTM base only 9.6%, Tier D); clears 15% only below $27.50.
