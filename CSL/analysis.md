# CSL — Carlisle Companies Incorporated
Engine 5.4.0 run, 2026-10-17. All figures below are copied from dcf_numbers.json, ttm.json, financials_history.csv, or fundamentals.json — none are recomputed.

## What it is
Pure-play building-envelope manufacturer since the divestitures of its interconnect and fluid-technologies businesses: Carlisle Construction Materials (CCM — commercial roofing systems, ~70% of its roofing revenue from non-discretionary re-roofing) and Carlisle Weatherproofing Technologies (CWT — waterproofing, insulation, air/vapor barriers). Q2 2026 (filed 10-Q, period 2026-06-30): revenue +8.3% YoY in the quarter (fundamentals.json quarterly), CCM revenue +8% and CWT +10% YoY per company commentary, record adjusted EPS +12% YoY; management raised FY2026 revenue guidance to mid-single-digit growth, cut the margin guide 50bp to flat adjusted EBITDA margin on petroleum-based raw-material and freight inflation (price realization lags, expected to turn positive in Q4), guides ROIC ~25%, free-cash-flow margin ~15%, double-digit adjusted EPS growth, and raised the 2026 buyback target to $1.2B.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $1,101,800,000; capex $131,200,000; SBC $34,800,000.
- **Conservative owner's earnings FY2025: $935,800,000 = $21.66/share** (dcf_numbers.json base_oe_latest_per_share)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC, financials_history.csv): $883,700,000 — same ballpark, which raises confidence.
- OE positive 5 of the last 5 fiscal years. Net debt $1,774,300,000 (LongTermDebtNoncurrent+LongTermDebtCurrent basis, dcf_numbers.json), lease liabilities $135,600,000; net debt is 2.01x normalized OE (diagnostics).
- History caveat: the 5-year OE/share range spans >3x (OE_VOLATILE) — the early years are the pre-divestiture conglomerate (OE/share $5.03 in FY2021) and the series steps up as Carlisle became a pure play and bought back stock aggressively; that is a basis/mix break plus cyclicality, not a clean organic series.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $1,101,800,000 − prior YTD $288,900,000 + current YTD $197,100,000 = **TTM $1,010,000,000**
- Capex: FY $131,200,000 − prior YTD $57,800,000 + current YTD $70,000,000 = **TTM $143,400,000**
- SBC: FY $34,800,000 − prior YTD $19,500,000 + current YTD $17,900,000 = **TTM $33,200,000**
- Shares (current-YTD weighted diluted): **40,800,000**
- **TTM OE total $833,400,000 → base OE/share $20.43** (base_source: ttm_json)
- The engine's normalized base (median of last 3 FY OE/share) is $20.19/share — essentially identical to TTM, so the base choice is not the swing factor here; TTM is used because it is the more current figure and resolves STALE_FY.

## Moat: 7/10 — strong, not wide
Justification: dominant specification position in North American commercial roofing, warranted single-ply systems sold through deep contractor/architect relationships, and a recurring re-roofing base — evidenced by ROIC and margins — but the products compete against well-capitalized rivals (Holcim/Firestone, Johns Manville, GAF) and demand still rides the construction cycle.
- Evidence (fundamentals.json roic_proxy and gross margin, annual): ROIC proxy 10.6% (2020), 8.6% (2021), 17.5% (2022), 16.7% (2023), 24.7% (2024), 22.0% (2025); gross margin 28.7% (2020) → 28.6% (2021) → 34.2% (2022) → 35.6% (2023) → 37.7% (2024) → 35.7% (2025). Management guides ~25% ROIC for 2026. The high-ROIC history is real but only ~4 years on the pure-play mix; the pre-2022 conglomerate earned high-single/low-double-digit ROIC, which is why this is 7 and not 8.
- FOR: leading share and specification position in commercial roofing — architects/facility managers specify warranted Carlisle systems, creating switching friction; ~70% of CCM roofing revenue is re-roofing, a non-discretionary, recurring demand pool tied to the aging commercial building stock; proven pricing power through inflation cycles (three broad price increases in 2026); vertical integration in insulation (Insulfoam/ThermaFoam EPS, Bonded Logic) and the Carlisle Operating System driving structural margin gains; gross margin expanded ~7pp over five years.
- AGAINST: no network effects and no lock-in beyond warranty/spec — rivals with deep pockets contest every bid; pricing power lags cost inflation (Q2 2026 price-cost was negative; FY margin guide cut 50bp); ~30% of demand is new construction, which is cyclical and currently down low-to-mid single digits; petroleum-based inputs (MDI, asphalt, polymers) expose margins to commodity/freight shocks; distribution-channel M&A turmoil has previously cost temporary share.
- A 7 gives CAP = 11.1 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 11.1 years, 15-year projection.

## DCF — engine 5.4 final run (2026-10-17)
Growth sanity check: the engine's blended start is 4.45% (rev CAGR 5y 4.81%, rev CAGR 3y −2.70%, latest FY rev YoY +0.33%, OE/share CAGR 2y 3.58%, with the +5pp buyback adjustment applied to revenue components only). Against actual prints — TTM revenue +1.9% YoY (fundamentals.json TTM through 2026-06-30), Q1 2026 revenue −4.0% YoY, Q2 2026 +8.3% YoY, FY2026 guidance mid-single-digit revenue growth — the 4.45% base start sits right at guidance and needs no recalibration. Bull start 9.45% is above the Q2 print: written reason — it requires the guided Q4 price-cost turn, continued data-center traction, and new construction stabilizing. Super-bull start 16.45% is well above any recent print: written reason — it is a full Vision 2030 path (construction recovery + share gains + accretive M&A) and carries only 10% weight for exactly that reason. Probabilities 10/25/30/25/10 (defaults kept — 35% on bear-or-worse already reflects OE_VOLATILE and the construction cycle); OE multipliers 0.75/0.90/1.00/1.10/1.25. Price $333.86.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | −7.55% | 0.75 | Construction downturn deepens; price-cost stays negative; re-roofing defers | $78.61 | 4.96% |
| Bear | 25% | −0.55% | 0.90 | Flat revenue, margins stuck at the cut guide | $130.62 | 7.22% |
| Base | 30% | 4.45% | 1.00 | Mid-single-digit growth per guidance; buybacks continue | $183.66 | 9.48% |
| Bull | 25% | 9.45% | 1.10 | Price-cost turns positive Q4; new construction stabilizes | $256.06 | 12.31% |
| Super bull | 10% | 16.45% | 1.25 | Vision 2030 execution: recovery + share + M&A | $405.88 | 17.22% |

- **Probability-weighted: IV@15% $200.22 (−40.0% vs price), IV@12% $267.87, IV@10% $343.65, weighted IRR 10.21%, base-case IRR 9.48%**
- **Tier by numbers: C.** Hurdle prices (dcf_numbers.json): clears 15% at $200.22, 20% at $139.84, 25% at $106.88. Diagnostics: OE yield 6.12%, terminal value 19.5% of IV@15%, scenario spread 5.16x, net debt 2.01x normalized OE, 9.53 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.53 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, legs quoted above. TTM OE/share $20.43 vs normalized $20.19 and latest FY $21.66 — no material staleness distortion.
- **BUYBACK_TAILWIND** (share count shrinking 6.3%/yr): already credited via the +5pp growth adjustment applied to revenue components in the blend; not double-counted in the verdict. Buybacks are real and large ($1.1B TTM per fundamentals.json; 2026 target raised to $1.2B) and are funded from OCF, but they are also why per-share figures flatter a flat-revenue business.
- **OE_VOLATILE** (OE/share range >3x over 5 years): explained above — pre-divestiture conglomerate years ($5.03/share in FY2021) versus the pure-play, heavily bought-back current company, plus construction cyclicality. Handled by the normalized/TTM base (the two agree within ~1%) and 35% probability on bear-or-worse.
- **WIDE_SCENARIO_SPREAD** (super-bull IV 5.16x super-bear IV): real — the outcome hinges on the construction cycle and the price-cost lag. Confidence is capped at low, and the verdict is sized to the bear end.
- **TIER_BAND** (bear-case tier D at 7.22% vs bull-case tier C at 12.31%): the verdict spans tiers and even the weighted C (10.21%) sits barely above the C/D line; any position sizing must use the bear end (D economics at this price).

## My thoughts / overlay
- Quality is not the debate: ~22-25% ROIC, ~36% gross margins, $1.01B TTM OCF, modest SBC ($33.2M TTM), 17 years of dividend growth (fundamentals.json) and a 50th consecutive annual increase guided. The debate is price: at $333.86 the market is already paying for the bull path — even the base case (guidance-level growth) yields only 9.48% IRR, and the stock clears Andrew's 15% hurdle only at $200.22, ~40% below the current price.
- Method range: on the preliminary median-base run (moat 5 defaults) the weighted IRR was 9.85% (Tier D, IV@15% $192.30); on this final TTM-base, moat-7 run it is 10.21% (Tier C, IV@15% $200.22). The defensible range is D-to-C — no reasonable input set gets CSL near 15% at $333.86.
- Risks: extended new-construction slump, petroleum input inflation outrunning the pricing lag again, distribution disruption, and multiple compression if the Vision 2030 $40 EPS path slips.

## Final verdict
- **Final tier: C** (weighted IRR 10.21%; bear case D — size to the bear end per TIER_BAND)
- Confidence: **Low** (WIDE_SCENARIO_SPREAD 5.16x and OE_VOLATILE cap confidence; the base itself is high-quality filing data)
- One-liner: High-quality building-envelope leader, moat 7/10 — at $333.86 the weighted IRR is 10.2% and it does not clear 15%; it clears 15% only at or below $200.22.
