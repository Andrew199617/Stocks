# SWK — Stanley Black & Decker, Inc.
Engine 5.4.0 run, 2026-10-17. Market cap $14.05B at $92.48 (nasdaq_quote_api) — in scope under $40B.

All figures below are copied from dcf_numbers.json, ttm.json, financials_history.csv, or fundamentals.json — none are recomputed.

## What it is
Global tools and outdoor leader: DEWALT (professional power tools), STANLEY, CRAFTSMAN, BLACK+DECKER, Cub Cadet outdoor, plus Engineered Fastening for auto/aerospace. Two segments (Tools & Outdoor dominant, Engineered Fastening). In the tail of a multi-year transformation: $2B+ cost-savings program, portfolio pruning (Consolidated Aerospace Manufacturing sold April 2026 for ~$1.8B), and a deleveraging drive after the post-COVID inventory blowout.

## Owner's earnings
**FY2025 (10-K, period ended 2026-01-03, from financials_history.csv):** operating cash flow $971,200,000; capex $283,300,000; SBC $94,100,000 (always a real cost).
- **Conservative owner's earnings FY2025: $593,800,000 = $3.91/share** (base_oe_latest_per_share).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $1,201,300,000 — well above the conservative figure because the filed history's delta_nwc term for FY2025 is −$717,100,000, which the maintenance formula subtracts (i.e. adds). The OCF-based conservative figure is the cleaner one and is what the engine uses.
- OE positive 4 of the last 5 fiscal years. The exception is the year ended 2022-12-31: OCF −$1,459,500,000 and OE/share −$13.29 on the post-COVID inventory glut — the defining volatility event in this history.
- Net debt at FY end: $5,583,600,000 (LongTermDebtNoncurrent+LongTermDebtCurrent+ShortTermBorrowings basis). Post-period: the Q2 2026 release reports debt was reduced by $1.7B in that quarter using CAM sale proceeds, so the current balance sheet is materially less levered than the engine's FY-end figure (the engine figure is the one used in the diagnostics below).

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $971,200,000 − prior YTD −$205,700,000 + current YTD $374,300,000 = **TTM $1,551,200,000**
- Capex: FY $283,300,000 − prior YTD $144,600,000 + current YTD $123,400,000 = **TTM $262,100,000**
- SBC: FY $94,100,000 − prior YTD $64,400,000 + current YTD $52,600,000 = **TTM $82,300,000**
- Shares (current-YTD weighted diluted): **151,401,000**
- **TTM OE total $1,206,800,000 → base OE/share $7.97** (base_source: ttm_json)
- The engine's normalized base (median of last 3 FY OE/share) is $4.28/share. The TTM base is nearly double it because H1 2026 cash generation inflected hard (Q2 2026 alone: OCF $763M, FCF $698M, gross margin 33.0% vs ~27% a year earlier) on cost savings, pricing, and ~250bp of one-off tariff refunds. I use the TTM base — it is the current run-rate and the STALE_FY remedy — but the gap is the central judgment in this run: on the median base the preliminary run printed weighted IRR 6.75%, on the TTM base 9.89%. Both are Tier D, so the verdict does not hinge on the choice; the TTM base is the generous end of the method range. Caveat inside the TTM base: tariff refunds are non-recurring, so normalized TTM OE is somewhat below $7.97.

## Moat: 5/10 — moderate/narrow
Justification: DEWALT's professional brand and battery-platform lock-in are real, but share is contested by Milwaukee, the consumer brands are weak, and returns collapsed through the last downturn — no through-cycle pricing power proof.
- FOR: DEWALT professional brand equity and trust (most-trusted pro power-tool brand; ~17% dollar share per industry coverage); 20V MAX / FLEXVOLT battery ecosystem lock-in — pros who own the platform keep buying the tools; distribution scale across Home Depot, Lowe's and pro channels that smaller rivals cannot match; engineered fastening niches with co-engineered, qualified positions in auto/aerospace; high-margin consumables (blades, bits, accessories) that recur.
- AGAINST: TTI's Milwaukee has been gaining professional share with faster cordless innovation; Makita/Bosch compete hard in pro, retailer private labels and low-cost Chinese brands erode the consumer tier (BLACK+DECKER, entry CRAFTSMAN); demand is housing- and DIY-cycle-driven; tariff exposure on imported content; measured returns do not support a wide moat — roic_proxy (fundamentals.json) was 8.8% (FY2018), 14.3% (FY2019) and 15.0% (FY ended 2021-01-02), i.e. mid-teens at the peak, and gross margin fell from 37.2% (FY2019) to 24.9–25.3% in the 2022–23 downturn before recovering to 29.4% (FY2024), 30.3% (FY2025) and 33.0% in Q2 2026. A franchise with pricing power does not give up 12 points of gross margin in a downturn. (roic_proxy is not computable from fundamentals.json for FY2022 onward — the operating-income tag series breaks there — so the recent ROIC leg is stated as unavailable rather than estimated.)
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — 5.4 final run (2026-10-17)
Growth sanity check: the engine's blended start is −1.61% (components: revenue CAGR 5y +3.48%, 3y −3.70%, latest FY YoY −1.53%, OE/share CAGR 2y −12.66%; share count −1.00%/yr credited to the revenue components only). Recent prints: FY2025 revenue −1.5% YoY; TTM revenue +0.57% YoY (fundamentals.json); Q2 2026 sales flat YoY with organic +3%. The base start of −1.6% sits on the total-revenue trend and below the current organic print — defensible, since part of the Q2 margin print is tariff refunds that do not repeat. Bull start +3.39% ≈ the current organic print sustained — that is the right size for a bull case, not a stretch. Super-bull start +10.39% requires a housing upcycle with operating leverage; it is a 10% tail, and its starting OE (1.25 × $7.97 = $9.96/share) sits just above the best historical year ($9.63/share, FY ended 2021-01-02), which is as far as a super bull should reach here. Probabilities were shifted bear-ward from the 10/25/30/25/10 defaults to 15/30/30/15/10 per the OE_VOLATILE and HIGH_NET_DEBT flags; offsets and OE multipliers are the defaults (−12/−5/0/+5/+12pp; 0.75/0.90/1.00/1.10/1.25). The engine floors the super-bear growth start at −10.0%. Price $92.48.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | −10.0% | 0.75 | Housing downturn repeats 2022: WC blows out, margins re-collapse, leverage bites | $29.03 | 5.92% |
| Bear | 30% | −6.61% | 0.90 | Flat-to-down revenue, tariff costs return, recovery stalls | $40.17 | 7.54% |
| Base | 30% | −1.61% | 1.00 | Current run-rate decays per the blend; savings hold, no volume recovery | $55.05 | 9.78% |
| Bull | 15% | +3.39% | 1.10 | Organic +3% sustains, margins rebuild toward mid-30s gross | $74.60 | 12.60% |
| Super bull | 10% | +10.39% | 1.25 | Housing upcycle + share gains + full margin recovery | $113.25 | 17.57% |

- **Probability-weighted: IV@15% $55.43 (−40.1% vs price), IV@12% $72.41, IV@10% $91.21, weighted IRR 9.89%, base-case IRR 9.78%**
- **Tier by numbers: D** (bear D at 7.54%, bull C at 12.60% — see TIER_BAND). Diagnostics (dcf_numbers.json): OE yield 8.62%, terminal value 17.1% of IV@15%, scenario spread 3.90x, net debt 4.61x the TTM OE base (8.59x the normalized median base), 9.4 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.4 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026 (period ended 2026-07-04), legs quoted above.
- **OE_VOLATILE** (OE/share spans >3x over 5 years): real and structural — OE/share ran $9.63 (FY ended 2021-01-02) → −$13.29 (2022) → $5.13 → $4.28 → $3.91, driven by the COVID demand surge and the 2022 inventory unwind. Handled with the bear-shifted probabilities (45% on bear-or-worse) and sized verdict; the normalized median base ($4.28) is reported alongside as the conservative end of the method range.
- **NI_OCF_DIVERGENCE** (NI vs OCF differ >40% in 2023, 2024, 2026): the gap is non-cash, not cash leakage. In those years D&A alone was $432.4M / $426.3M / $365.6M against net income of −$310.5M / $294.3M / $401.9M, and the transformation years carried large non-cash impairment and restructuring charges (2023 printed a net loss while OCF was +$1,191.3M). The OCF-based conservative OE series is used throughout, so the divergence does not contaminate the base; if anything it means GAAP EPS understates cash earnings here.
- **HIGH_NET_DEBT** (net debt 8.6x normalized OE in the preliminary run; 4.61x the TTM base in the final run): balance sheet stated from the filing — net debt $5,583,600,000 at FY end (2026-01-03) on the engine's debt basis, plus lease liabilities $133,100,000. Stress applied via the bear-shifted weights and the 0.75 super-bear OE multiplier. Post-period improvement noted above: $1.7B of debt repaid in Q2 2026 from CAM proceeds, targeting ~2.5x net debt/EBITDA — the direction is right, but at the FY-end balance sheet the leverage was real, and the equity remains a levered claim on a cyclical OE stream.
- **TIER_BAND** (bear tier D 7.54% vs bull tier C 12.60%): verdict sized to the bear end — the final tier is D either way, and even the bull case does not reach the 15% hurdle.

## My thoughts / overlay
- The method range is D on both defensible bases: weighted IRR 6.75% on the normalized median base ($4.28/share), 9.89% on the TTM base ($7.97/share). The TTM run is the generous end because it capitalizes a quarter flattered by ~250bp of tariff refunds and peak seasonal cash conversion.
- The turnaround is genuinely progressing — $2B+ of cost savings, gross margin rebuilt from ~25% to 33%, FY2026 adjusted EPS guidance raised to $5.20–$5.80, CAM sold, debt coming down — but at $92.48 the market is already paying for most of it: the price sits above even the IV@10% weighted value ($91.21) and roughly at the super-bull's doorstep on any normal discount rate.
- Quality is mid-tier industrial: a good pro brand, a weak consumer flank, mid-teens peak ROIC, and a demonstrated ability to destroy OE in a downturn year. That is a moat-5 business priced like a compounder.
- Hurdle math: the stock clears a 15% hurdle only at or below the weighted IV@15% of $55.43 — about 40% below the current price. Even at a 10% discount rate the weighted value ($91.21) is below the price.

## Final verdict
- **Final tier: D** (weighted IRR 9.89% on the TTM base; 6.75% on the median base — D across the method range)
- Confidence: **Medium** (bases and flags are resolved and the tier is robust to the base choice, but OE volatility and the bear-to-bull tier band cap it below high)
- One-liner: Turnaround in progress with a real DEWALT franchise, moat 5/10 — but even on the generous TTM base it returns 9.9% weighted (IV@15% $55.43 vs $92.48); it only clears 15% at ~$55 or below.
