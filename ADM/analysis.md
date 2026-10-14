# ADM — Archer-Daniels-Midland Company
Run date: 2026-10-13. Engine v4. Price $80.42 (Nasdaq quote API, final run), market cap ~$38.9B — in scope (<$40B).

## What it is
One of the world's largest agricultural processors and commodity merchants (founded 1902, Chicago). Three segments: Ag Services & Oilseeds (origination, logistics — elevators, rail, barge, export terminals — and soybean/corn crushing, the largest segment), Carbohydrate Solutions (starches, sweeteners, corn ethanol/biofuels), and Nutrition (flavors, specialty ingredients, animal nutrition — the small, higher-margin "growth" segment). This is a commodity-spread business: it earns the crush margin, the ethanol margin, and merchandising/logistics spreads on volumes it does not price. Revenue is commodity pass-through — total revenue (EDGAR `Revenues` tag) was $101.6B in 2022, $93.9B in 2023, $85.5B in 2024, $80.3B in 2025, a decline driven mostly by commodity-price deflation, not volume collapse. TTM revenue through Q2 2026 is $82.1B (+2.3% vs FY2025; Q2 2026 revenue $22.68B, +7.2% YoY).

Latest earnings: Q2 2026 (reported 2026-08-04) — net earnings $908M, GAAP EPS $1.87, adjusted EPS $1.84 (+98% YoY), total segment operating profit $1.45B (+75%; Ag Services & Oilseeds +129%). Full-year 2026 adjusted EPS guidance was **raised** to $5.15–$5.60 (from $4.15–$4.70; FY2025 adjusted EPS was $3.43). The driver is explicit in ADM's own release: the EPA finalized 2026/2027 renewable volume obligations (RVO) in March 2026, lifting crush and ethanol margins, helped by elevated energy prices. That is a policy-and-cycle rebound off a trough — real, but not a durable growth rate. Adjusted ROIC on the trailing four quarters was only 7.8% per ADM's Q2 release.

Red flags: (1) the 2024 Nutrition intersegment-accounting scandal — sales between Nutrition and the other segments were not recorded at market rates, inflating Nutrition's segment profit; ADM restated its FY2023 10-K and Q1/Q2 2024 10-Qs in November 2024 (10-K/A and 10-Q/A filings are all over the EDGAR history), and in January 2026 settled the SEC investigation for $40M without admitting wrongdoing, with the former CFO charged separately. Crucially the SEC matter was segment-reporting only: **no impact on consolidated balance sheet, earnings, or cash flows**, so the consolidated owner's-earnings history used here stands. (2) Earnings are hostage to US biofuel policy, crush margins, crop prices, and trade flows — all outside management's control. (3) Owner's earnings are extremely lumpy from working-capital / readily-marketable-inventory swings (see flags).

## Owner's earnings
FY2025 (SEC 10-K via EDGAR): OCF $5.452B − capex $1.248B − SBC $0.083B = **conservative OE $4.121B = $8.51/share**. Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $1.799B = $3.72/share. The two definitions diverge wildly because both are working-capital distorted in opposite directions in any single year (see NI_OCF_DIVERGENCE below).

OE/share history (conservative): 2021 $9.30, 2022 $3.57, 2023 $5.27, 2024 $2.34, 2025 $8.51 — positive 5/5 years but spanning a 3.6× range. This is a cyclical, not a compounder.

**Base used: the engine's normalized 3-yr median, $5.27/share** (median of 2023 $5.27, 2024 $2.34, 2025 $8.51). Both single-point alternatives are distorted, in opposite directions:
- Latest FY ($8.51) is inflated by a working-capital/inventory release in a down-revenue year — it cannot repeat annually.
- TTM (computed below) is deflated by a working-capital build in H1 2026 even as net income more than doubled YoY — equally unrepeatable.
The median is the through-cycle earning power, and the verdict below is robust to the choice (method range section).

**TTM arithmetic (STALE_FY resolution, from EDGAR 10-Q YTD figures):**
- OCF: FY25 $5.452B − H1'25 $3.956B + H1'26 $1.299B = $2.795B
- Capex: FY25 $1.248B − H1'25 $0.596B + H1'26 $0.466B = $1.118B
- SBC: FY25 $0.083B − H1'25 $0.072B + H1'26 $0.138B = $0.149B
- TTM OE = $2.795B − $1.118B − $0.149B = **$1.528B = $3.15/share** on 485M diluted shares (H1 2026 weighted avg)
TTM OE of $3.15 was **not** used as the base: H1 OCF at ADM is dominated by seasonal inventory builds (H1 net income was $1.206B, up from $0.514B in H1'25, while H1 OCF fell from $3.956B to $1.299B — earnings and cash moved in opposite directions). Substituting TTM would swap the FY2025 release distortion for a larger H1 build distortion.

Balance sheet: net debt $6.60B at FY2025 ($6.54B at Q2 2026: debt $7.60B − cash $1.06B) = 2.6× normalized OE — manageable for a commodity merchant with liquid inventories, but it is not a net-cash cushion and it does not rescue the valuation.

## Moat score: 4/10 — weak-to-moderate
FOR — Scale and infrastructure that are genuinely hard to replicate: one of the largest global origination, storage, rail/barge, and export-terminal networks; among the world's largest crush capacities, so unit costs and logistics optionality (rerouting crop flows around trade disruptions) are real advantages vs sub-scale processors. Diversification across origination, crush, carbs/ethanol, and Nutrition dampens any single spread. A century of through-cycle survival and 53 consecutive years of dividend growth say the franchise endures.
AGAINST — No pricing power where it matters: ADM is a price-taker on both what it buys (corn, soy) and most of what it sells; crush and ethanol margins are set by commodity markets and, increasingly, by EPA policy (the entire 2026 earnings rebound is RVO-driven). Returns prove it: adjusted ROIC 7.8% TTM at a cyclical *upswing* print, and earnings fell from $4.34B net income (2022) to $1.08B (2025) with no moat stopping it. Competition is Bunge, Cargill (private, larger in some lines), and COFCO — equally scaled, equally undifferentiated. Nutrition, the one segment that could have earned a moat premium, is where the accounting fraud lived, and at ~$0.1–0.15B of quarterly segment profit it is too small to move consolidated returns.
CAP = 2 + 1.3 × 4 = **7.2 years** (growth holds 2 years, then fades to the 2.5% terminal rate over 7.2 years, 15-yr projection).

## DCF — final v4 run
Base OE $5.27/share (normalized median, above). Price $80.42 = 15.3× normalized OE, a 6.5% normalized OE yield — a full price for a cyclical at a policy-driven earnings rebound, after a ~40% YTD share-price run.

Growth inputs were recalibrated by offsets to judgment starts, because both components of the engine's g_base (4.46%) are compromised: its revenue blend uses a corrupted revenue series (BASIS_BREAK below), and its +4.91pp buyback adjustment is stale (BUYBACK_TAILWIND below). Scenario starts vs actual prints: real revenue growth is TTM +2.3%, H1 +4.4%, Q2 +7.2%; the 2026 adjusted-EPS rebound (+50–63% guided vs FY2025) is a trough/policy recovery, not a sustainable OE growth rate, so even the super-bull start (10%) sits far below the 2026 EPS print — written reason: that print is margin recovery on a fixed asset base, and revenue (the thing that can compound) is growing at 2–7%.

| Scenario | Prob | Growth start | OE mult | IV@15% | IRR |
|---|---|---|---|---|---|
| Super bear | 15% | −5.0% | 0.75 | $24.15 | 6.0% |
| Bear | 30% | −0.0% | 0.90 | $35.23 | 7.9% |
| Base | 30% | +3.0% | 1.00 | $43.94 | 9.3% |
| Bull | 17% | +6.0% | 1.10 | $54.22 | 11.0% |
| Super bull | 8% | +10.0% | 1.25 | $71.69 | 13.7% |

Probabilities are skewed bearish vs the 10/25/30/25/10 defaults (15/30/30/17/8): OE_VOLATILE plus a share price that has already capitalized the RVO rebound argue for more left-tail weight; the super-bull case requires the policy/margin environment to persist *and* compound, which commodity spreads rarely do.
- **Probability-weighted: IV@15% $42.33 (−47% vs price), IV@12% $55.75, weighted IRR 9.1%**
- **Tier by numbers: D** (weighted IRR <10%)
- Diagnostics: OE yield 6.5%, terminal value 18% of IV@15% (low — the verdict is not a terminal-value artifact), net debt 2.59× normalized OE, scenario spread (final recalibrated) 3.0×.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9 months ago): TTM OE computed in full above from 10-Q YTD figures = $3.15/share. Not used as the base, with the reason documented: H1 OCF is a working-capital build (H1 net income $1.206B vs H1 OCF $1.299B, vs $3.956B OCF in H1'25 on $0.514B of income) — the TTM figure is more distorted than the median it would replace. The Q2 2026 earnings recovery *is* reflected — in the scenario growth starts and in rejecting any claim that FY2025's trough earnings power is the run rate.
- **BASE_DIVERGENCE** (latest $8.51 vs median $5.27): the latest year is the distorted one. FY2025 OCF ($5.45B) was flattered by inventory/working-capital release as revenue fell $5.3B; FY2024 OE/share was $2.34 on the opposite swing. Median $5.27 chosen; see method range below for the cost of choosing otherwise.
- **WIDE_SCENARIO_SPREAD**: fired on the preliminary run (4.5×); after recalibration the final spread is 3.0× ($71.69 / $24.15). Still wide — commodity spreads are genuinely bimodal around policy — so confidence is capped at medium even though the flag no longer fires.
- **BUYBACK_TAILWIND** (share count −4.9%/yr credited in g_base): stale. Diluted shares fell 566M (2021) → 484M (2025), but the count has been flat at 483–485M from Q3 2024 through Q2 2026 — the buyback that produced the trailing CAGR has stopped shrinking the count. The forward tailwind is ~0, which is one reason scenario starts were offset below the engine's g_base rather than taken from it.
- **BASIS_BREAK_SUSPECT** (>60% revenue move): **engine artifact, not a company event.** The engine's revenue series uses `RevenueFromContractWithCustomerExcludingAssessedTax`, which for ADM captures only a sub-component (~$25B/yr in 2022–25 vs actual total revenue of $80–102B under the `Revenues` tag) and collapses from $85.2B (2021) to $27.6B (2022) in the CSV. ADM had no such divestiture. Real total revenue declined smoothly 2022→2025 on commodity deflation ($101.6B → $80.3B; real 3-yr CAGR −7.5%). Two genuine basis items were checked and cleared: (a) the November 2024 Nutrition restatement was segment-only with no consolidated impact (SEC settlement Jan 2026, $40M); (b) no large M&A/divestiture in the window. Consequence: the engine's rev CAGRs (−17.3% 5-yr, −3.3% 3-yr) and blended growth were not trusted; scenario starts were set from the real revenue/earnings prints.
- **OE_VOLATILE** (OE/share range >3× over 5 yrs: $2.34–$8.51): real and structural — crush/ethanol spreads plus inventory-driven OCF. Handled by the normalized median base, wider bear/super-bear weight (45% combined), and a super-bear OE multiplier of 0.75.
- **NI_OCF_DIVERGENCE** (2025: NI $1.078B vs OCF $5.452B): working capital, not a tax deposit. FY2025 net income was depressed by non-cash charges (GAAP EPS $2.23 vs adjusted $3.43) while OCF was boosted by drawing down inventories/receivables into falling revenue — the mirror image of H1 2026. Neither the NI-based maintenance OE ($3.72/sh) nor the OCF-based conservative OE ($8.51/sh) is a clean single-year run rate for ADM; this is the core reason the base is a 3-yr median.

## My thoughts / overlay
- **Method range:** defensible bases span tiers but never reach the hurdle. TTM base ($3.15) → weighted IV@15% ~$25, IRR ~5–6% (deep D). Median base ($5.27, used) → 9.1% (D). Latest-FY base ($8.51, the most generous defensible choice) → IV@15% scales to ~$68 and IRR to roughly 12–13% (C). The honest headline is D-to-C, sized to the conservative end: **D**.
- Even the super-bull scenario (10% growth start, 1.25× OE, 8% weight) yields only a 13.7% IRR and an IV@15% of $71.69 — below today's $80.42 price. There is no scenario in the set where buying here clears 15%; the stock has already been paid for the RVO rebound.
- Quality is not the question — ADM will be processing crops in 15 years, pays a growing dividend, and carries manageable leverage. The question is price: 15.3× normalized owner's earnings for a business whose through-cycle ROIC is high-single-digits and whose earnings just got a policy gift.
- **Hurdle math:** the weighted path clears 15% at **~$42** (the weighted IV@15%); with a 20% margin of safety, ~$34. At $80.42 you are paying roughly double the hurdle-clearing price.

## Final verdict
- **Final tier: D** (weighted IRR 9.1%; tier_final = tier_by_numbers, no override)
- Confidence: **Medium** (high that the stock does not clear 15% at this price — no defensible base or scenario gets there; medium on the point estimate, given OE volatility and the $3.15–$8.51 base range)
- One-liner: Enduring commodity processor with scale/logistics advantages but no pricing power, moat 4/10 — at $80.42 (15.3× normalized OE of $5.27/share, after the RVO-driven guidance raise was priced in) it yields a 9.1% weighted IRR with IV@15% of $42.33; it clears the 15% hurdle only at ~$42 (~$34 with a margin of safety), and even the super-bull case stays below today's price.
