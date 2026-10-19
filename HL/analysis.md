# HL — Hecla Mining Company
Engine 5.4 run, 2026-10-18. All figures below are copied from dcf_numbers.json, ttm.json, financials_history.csv, or fundamentals.json — none are recomputed.

## What it is
The largest primary silver producer in the United States and Canada (founded 1891, Coeur d'Alene, Idaho). Three operating mines after the March 2026 sale of the Casa Berardi gold mine in Quebec: Greens Creek in Alaska (the crown jewel — silver with gold/zinc/lead by-products whose credits drive consolidated silver cash costs negative), Lucky Friday in Idaho (record 1.5 Moz in Q2 2026), and Keno Hill in the Yukon (high-grade, still ramping, slowed in 2026 for infrastructure and permitting). It is a pure price-taker: revenue is the silver/gold spot price times ounces, and the current earnings level is a metal-price print, not a franchise print. Updated 2026 silver production guidance is 15.1–16.1 Moz — below the ~17 Moz the three continuing mines produced in 2025 — so volume is flat-to-down; all of the recent "growth" is price.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $562,638,000; capex $252,389,000; SBC $10,918,000 (always a real cost, and here genuinely small next to OCF).
- **Conservative owner's earnings FY2025: $299,331,000 = $0.4565/share** (base_oe_latest_per_share).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $188,553,000 — lower than the conservative figure, same order of magnitude.
- The through-cycle history is the problem: conservative OE/share was $0.194 (2021), −$0.118 (2022), −$0.256 (2023), −$0.008 (2024), $0.456 (2025) — positive in only **2 of the last 5 fiscal years**, and the engine's normalized base (3-yr median) is **−$0.0078/share**. On the median base alone this is a Tier F: no positive through-cycle conservative OE. Net debt at FY2025 end was only $27,069,000 (dcf_numbers.json), and after the Casa Berardi sale proceeds Hecla redeemed its remaining senior notes in 2026 — by Q2 2026 reporting it was effectively debt-free with ~$483M cash. The balance sheet is not the problem; the earnings base is a peak-price snapshot.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $562,638,000 − prior YTD $197,534,000 + current YTD $369,165,000 = **TTM $734,269,000**
- Capex: FY $252,389,000 − prior YTD $80,514,000 + current YTD $78,407,000 = **TTM $250,282,000**
- SBC: FY $10,918,000 − prior YTD $4,923,000 + current YTD $6,081,000 = **TTM $12,076,000**
- Shares (current-YTD weighted diluted): **675,865,000**
- **TTM OE total $471,911,000 → base OE/share $0.6982** (base_source: ttm_json)
- Why the TTM base and not the median: the median is the distorted figure in the opposite direction — it averages the 2023–24 trough years (negative OE at low silver prices and peak capex) and says the company earns nothing, which the last six quarters refute. But the TTM base is struck at historically extreme realized prices (Q1 2026 realized silver $82.70/oz, Q2 2026 $63.06/oz vs $34.82/oz a year earlier, per Q2 2026 reporting) and consolidates Casa Berardi only until its March 2026 disposal. That peak-price strike is handled in the scenarios and the bear-weighted probabilities, not hidden — and the verdict below is sized to the conservative end.

## Moat: 4/10 — weak-to-moderate; asset quality, not pricing power
Justification: Hecla has no pricing power and no customer lock-in — it sells a commodity at spot. What passes for a moat in mining is cost-curve position, reserve life, and jurisdiction, and Hecla is genuinely above average there (Greens Creek's by-product credits make its silver cash cost negative; Lucky Friday has a long reserve life; it is the largest primary silver producer in the U.S. and Canada, all in tier-1 jurisdictions with decades-old permits and infrastructure). The measured history caps the score: **ROIC (roic_proxy, fundamentals.json) was 3.2% (2021), −0.4% (2022), −1.4% (2023), 2.2% (2024), 13.2% (2025)** — near zero through the cycle, spiking only when silver spiked. Gross margin tells the same story: 27.0% / 16.2% / 15.7% / 21.3% / 43.7% over 2021–25. A moat that only shows up at peak metal prices is an asset-quality edge, not a franchise — 4/10.
- FOR: Greens Creek — one of the world's largest, lowest-cost silver mines, with gold/zinc/lead by-product credits covering production costs (negative consolidated silver cash costs in Q2 2026); Lucky Friday — deep, long-life (17-yr reserve life per company reporting) high-grade mine at record production; scale as North America's largest primary silver producer in U.S./Canadian jurisdictions only — permitting and political-risk advantage over Latin-American peers; effectively debt-free balance sheet after the Casa Berardi sale funds exploration and the Keno Hill ramp internally.
- AGAINST: pure commodity price-taker — earnings are the silver price, which Hecla does not control and which struck the current base at $63–83/oz realized; reserves deplete every year and must be replaced with capex or M&A; three-mine concentration after the Casa Berardi sale, with Greens Creek roughly half of silver production; Keno Hill still not at a sustainable commercial rate (power/permitting issues, 2026 ramp deliberately slowed); through-cycle ROIC near zero (above) — no demonstrated ability to earn above the cost of capital at mid-cycle prices.
- A 4 gives CAP = 7.2 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 7.2 years, 15-year projection. The 2.5% terminal rate is generous for a depleting-asset business and is kept only for sweep comparability — the verdict is sized accordingly.

## DCF — engine 5.4 final run (2026-10-18)
Growth recalibration (written reason): the engine's blended growth is 20.55% (after the −5pp share-count adjustment) because its components are metal-price artifacts — latest revenue YoY +53.03% and 3-yr revenue CAGR 25.55% are the silver price going from ~$35 to $63–83/oz realized, not volume: 2026 production guidance (15.1–16.1 Moz) is *below* 2025 continuing-mine output (~17 Moz). None of that is repeatable OE/share growth. Scenario starts were therefore set via offsets (−0.3255 / −0.2655 / −0.2055 / −0.1455 / −0.0855 vs the blend) to −10 / −6 / **0** / +6 / +12%. The base start of 0% assumes prices merely hold near current highs and flat volume offsets Keno Hill's ramp — it sits far below the printed growth rates for the price reason above; this is the APP lesson applied in reverse, the prints are the artifact. Probabilities are bear-weighted (15/30/30/17/8) because the TTM base is struck at peak prices; OE multipliers are the defaults 0.75/0.90/1.00/1.10/1.25. Price $15.30.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | −10.0% | 0.75 | Silver corrects hard back toward the $30s; OE mean-reverts toward the trough years | $2.63 | 4.38% |
| Bear | 30% | −6.0% | 0.90 | Prices normalize partway; costs inflate; full share count bites | $3.70 | 5.30% |
| Base | 30% | 0.0% | 1.00 | Prices hold near highs, flat volume, Keno Hill ramps slowly | $5.20 | 6.67% |
| Bull | 17% | +6.0% | 1.10 | Silver stays elevated; Keno Hill reaches a sustainable rate | $7.20 | 8.49% |
| Super bull | 8% | +12.0% | 1.25 | Metal bull market persists; production pushes toward 20 Moz | $10.26 | 11.10% |

- **Probability-weighted: IV@15% $5.11, IV@12% $6.70, weighted IRR 6.63%, base-case IRR 6.67%**
- **Tier by numbers: D** (bear tier D, bull tier D — no TIER_BAND split). Diagnostics (dcf_numbers.json): OE yield 4.56%, terminal value 17.5% of IV@15%, scenario spread 3.90x, net debt 0.06x normalized OE, 9.6 months since FY end.
- Even the super-bull case (8%) only reaches an 11.10% IRR at this price — there is no plausible path here to Andrew's 15% hurdle without a much lower entry. Hurdle prices (dcf_numbers.json): clears 15% below $5.11, 20% below $3.67, 25% below $2.86.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended ~10 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, quoted in full above.
- **DILUTION** (share count +5.6%/yr): equity issuance, not SBC leakage — SBC is only $10,918,000 (FY2025) / $12,076,000 (TTM), ~2% of operating cash flow. The count went from 527,329,000 diluted (2020) to 655,768,000 (2025) and 675,865,000 TTM-weighted (671,768,431 outstanding at 2026-07-31) on acquisition and financing issuance (e.g. the Alexco/Keno Hill deal). The −5pp growth adjustment is already in the blend, and the recalibrated scenario starts sit far below it anyway; the residual drag is carried in the bear weighting.
- **NI_OCF_DIVERGENCE** (2025: net income $321,712,000 vs OCF $562,638,000): the classic miner pattern — the gap is mostly non-cash depreciation/depletion/amortization of $165,570,000 (financials_history.csv) sitting between the two lines, with the remainder in deferred taxes and working-capital timing. The OCF-based conservative OE used throughout is unaffected by the non-cash side; the divergence does not flatter the base (if anything the maintenance OE definition, which charges the divergence back, is lower at $188,553,000).

## My thoughts / overlay
- The honest headline is the method range: on the normalized median base (−$0.0078/share) this is a Tier F — no positive through-cycle OE. On the TTM base struck at $63–83/oz realized silver, it is a Tier D at 6.63% weighted. Both methods agree on the only thing that matters at $15.30: the price capitalizes peak-cycle earnings several times over. Even granting the peak base forever (base case, 0% growth, no price normalization) yields only a 6.67% IRR.
- Quality notes in its favor: SBC is negligible, the balance sheet is now effectively debt-free, Greens Creek/Lucky Friday are real low-cost assets, and management used the cycle top to sell Casa Berardi and retire the senior notes rather than buying growth — good capital allocation at the peak.
- Watch items: realized silver price (already down from $82.70 in Q1 to $63.06 in Q2 2026), Keno Hill's path to a sustainable commercial rate, and whether the share count finally stops growing now that the balance sheet is clean.

## Final verdict
- **Final tier: D** (weighted IRR 6.63% on the TTM base; Tier F on the normalized median base — the method range is F to D, and even the generous end is nowhere near the 15% hurdle)
- Confidence: **Low** (cyclical price-taker, TTM base struck at peak metal prices, scenario spread 3.90x)
- One-liner: Largest North American primary silver producer, moat 4/10 — TTM OE is real but struck at peak silver prices and the through-cycle median OE is negative; at $15.30 the weighted IRR is only 6.6% (IV@15 $5.11), and it clears 15% only below ~$5.11.
