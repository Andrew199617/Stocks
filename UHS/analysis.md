# UHS — Universal Health Services, Inc.

Engine 5.4 run, 2026-10-19. Market cap $11.932B at $185.10 (nasdaq_quote_api) — in scope under $40B.

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.json, financials_history.csv or fundamentals.json — none are recomputed.

## What it is
One of the largest US hospital operators: acute care hospitals plus the largest behavioral-health platform (inpatient psychiatric facilities structurally undersupplied in many local markets), with outpatient/freestanding ED expansion and a pending Talkspace acquisition to add virtual behavioral care. Revenue FY2025 $17,364,829,000 (financials_history.csv). Q2 2026 revenue $4.64 billion, up 8.3% year on year (Q2 2026 earnings reporting).

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $1,864,397,000; capex $1,015,152,000; SBC $95,688,000 (always a real cost).
- **Conservative owner's earnings FY2025: $753,557,000 = $11.69/share** (key_numbers.md: latest FY OE/share $11.69, latest FY OE total $753.6M)
- Maintenance version (oe_maintenance total in financials_history.csv): $1,938,178,000 — but read its construction before trusting it: with FY2025 capex ($1,015,152,000) above D&A ($618,743,000), the engine's NI + D&A − min(capex, D&A) − ΔNWC has the D&A add-back and the capex cap cancel exactly, so the figure is NI ($1,488,796,000) minus ΔNWC (−$449,382,000) — i.e. the entire uplift over net income is the favorable FY2025 working-capital swing, the same cash-flow volatility that argues against leaning on it. The conservative OCF − capex − SBC figure is the one used, as capex has run above D&A on de novo hospitals and bed expansions, i.e. the spend is real.
- OE positive 4 of the last 5 fiscal years (key_numbers.md) — FY2021 was negative (OE/share −$0.55 in fundamentals.json) when OCF collapsed on working-capital outflows and labor costs.
- Net debt $4.615B (key_numbers.md); lease liabilities $413,952,000 (dcf_numbers.json).

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $1,864,397,000 − prior YTD $909,026,000 + current YTD $844,931,000 = **TTM $1,800,302,000**
- Capex: FY $1,015,152,000 − prior YTD $505,040,000 + current YTD $444,790,000 = **TTM $954,902,000**
- SBC: FY $95,688,000 − prior YTD $45,707,000 + current YTD $45,413,000 = **TTM $95,394,000**
- Shares (current-YTD weighted diluted): **60,789,000**
- **TTM OE total $750,006,000 → base OE/share $12.34** (base_source: ttm_json)
- The normalized (3-yr median) base is $11.69/share (key_numbers.md) — close to the TTM base, so the choice is not load-bearing; TTM is used because FY2025 ended 9.6 months ago (months since FY end, key_numbers.md).

## Moat: 5/10 — moderate/narrow
Justification: local scale and scarce behavioral-health beds plus a diversified acute/behavioral footprint, but payer-set reimbursement, labor scarcity and ROIC that fell to 7.2% in 2022 and only recovered to 12.9% in 2025 — not well above the cost of capital through a cycle.
- FOR: Largest US behavioral-health platform; inpatient psychiatric beds structurally undersupplied locally; scale across ~400 facilities in acute care and behavioral health with negotiating leverage with commercial payers; diversified acute + behavioral mix, resilient through cycles, operating margin recovered to 11.5% in FY2025 (fundamentals.json); local facility density, licensure/CON barriers and referral relationships.
- AGAINST: Government payers set much of reimbursement — Medicare/Medicaid rates lag cost inflation and supplemental Medicaid benefits shrink under OBBBA from 2028 (see Thoughts); labor shortages constrain capacity and drive wage/professional-fee costs; ROIC proxy only 7.2–12.9% over 2022–2025 (fundamentals.json roic_proxy: 7.2% in 2022, 8.2% in 2023, 11.8% in 2024, 12.9% in 2025) — a thin, volatile spread; larger rivals (HCA in acute, Acadia in behavioral) and non-profit systems in every local market; professional/general liability severity rising (reserve increases in Q2 2026).
- Evidence note: fundamentals.json reports no gross profit / gross margin series for UHS (hospital filers do not break out COGS that way), so the margin evidence is operating margin: 7.5% in 2022, 8.2% in 2023, 10.6% in 2024, 11.5% in 2025, and 11.4% TTM (fundamentals.json). A 5, not higher, because ROIC spent 2022–2023 in single digits.
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — final run (2026-10-19)
**Growth recalibration (written reason):** the engine's blended growth is 13.79% (key_numbers.md), but it is an artifact: OE/share CAGR 2y is 36.93% off the depressed 2022–2023 base, and the revenue components carry the +4.42% buyback adjustment on top of revenue CAGRs of 8.48% (5y) / 9.02% (3y) and latest YoY 9.71%. Actual prints are lower and decelerating: Q2 2026 revenue +8.3%, and updated 2026 guidance is for ~7% revenue growth, ~3% EBITDA-less-NCI growth and ~6% EPS growth at the midpoint (Q2 2026 earnings call). Scenario starts were therefore set via offsets (−0.12 / −0.09 / −0.06 / −0.02 / +0.02 vs g_base) to 1.8 / 4.8 / **7.8** / 11.8 / 15.8% — the base start sits on guidance and recent prints, and even the super-bull start (15.8%) is capped near twice the guided revenue growth, justified only by buyback-boosted per-share growth. Probabilities were shifted bear-ward to 15/30/30/15/10 (45% bear-or-worse) for OE_VOLATILE, HIGH_NET_DEBT and the enacted OBBBA Medicaid supplemental phase-down (see Thoughts): the engine's scenarios are growth paths off the base and cannot carry a dated line-item step-down, so that headwind is carried in the super-bear story, the bear-ward weights and these below-blend growth starts rather than as an explicit reduction in the base and bear paths — a method limit, stated plainly. OE multipliers are the defaults 0.75/0.90/1.00/1.10/1.25. Price $185.10.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | 1.8% | 0.75 | Medicaid supplemental cuts bite early; labor/liability costs squeeze margins; levered OE stalls | $73.66 | 7.45% |
| Bear | 30% | 4.8% | 0.90 | Low-single-digit growth, margin pressure persists | $100.14 | 9.35% |
| Base | 30% | 7.8% | 1.00 | Guidance-like revenue growth decaying over the CAP | $125.99 | 11.16% |
| Bull | 15% | 11.8% | 1.10 | Volume + capacity additions + Talkspace outpatient ramp beat guidance | $163.39 | 13.65% |
| Super bull | 10% | 15.8% | 1.25 | Sustained double-digit per-share OE growth with buybacks | $218.61 | 16.98% |

- **Probability-weighted: IV@15% $125.26 (−32.3% vs price), IV@12% $167.44, IV@10% $214.60, weighted IRR 11.14%, base-case IRR 11.16%**
- **Tier by numbers: C.** Diagnostics (key_numbers.md): OE yield 6.67%, terminal value 19.3% of IV@15%, scenario spread 2.97x, net debt 5.80x normalized OE, 9.6 months since FY end.
- Hurdle-clearing prices (weighted path, key_numbers.md): 15% at $125.26 · 20% at $87.51 · 25% at $66.84.

## Flags — every fragility flag resolved
- **STALE_FY** (latest fiscal year ended 10 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, quoted above ($12.34/share vs $11.69 normalized).
- **BUYBACK_TAILWIND** (share count shrinking 4.4%/yr): share count CAGR −4.42% (key_numbers.md) is already credited via the growth adjustment in the blend; it is not double-counted — indeed the recalibration above strips most of that credit out of the revenue starts. Buybacks are real (Q2 2026: $320 million for 1.89 million shares, per the Q2 call) and are why EPS can grow faster than revenue.
- **OE_VOLATILE** (OE/share range over the last 5 years spans >3x): real and explained — FY2021 OE/share was −$0.55 and FY2022 $2.39 (fundamentals.json) on the pandemic working-capital swing and agency-labor spike, vs $15.08 in FY2024 and $11.69 in FY2025 (financials_history.csv). Handled with the TTM base, 45% probability on bear-or-worse, and confidence capped at medium.
- **NI_OCF_DIVERGENCE** (net income and operating cash flow differ by >40% in 2024): FY2024 net income was $1,142,097,000 vs OCF $2,067,101,000 (financials_history.csv). The gap is mostly non-cash D&A of $584,831,000 plus SBC of $99,349,000 added back in OCF, with a favorable working-capital swing in 2024 (delta_nwc −$198,665,000 in financials_history.csv, i.e. a source of cash on the engine's sign convention) — not a tax-deposit or impairment one-off. Consequence: FY2024 OE/share ($15.08) is flattered by that WC swing, which is why neither the latest-FY nor a single-year base is used; the TTM base ($12.34) and the $11.69 median bracket it.
- **HIGH_NET_DEBT** (net debt 5.8x normalized OE): net debt $4.615B (key_numbers.md: $4,614,754,000 in score.json) plus lease liabilities $413,952,000. One construction note on the printed 5.80x (key_numbers.md): the engine's diagnostic divides net debt by the TTM base per share × the FY2025 share count ($12.34 × 64,462,000 ≈ $795.4M), which matches neither OE total in the folder — against the FY2025 OE total printed in key_numbers.md ($753.6M) the same net debt is 6.12x, and 6.67x including the lease liabilities. Either way the point stands: levered OE can shrink fast if reimbursement or labor turns. Stressed via the 0.75/0.90 bear multipliers and the bear-weighted probabilities.
- **TIER_BAND** (bear-case tier D at 9.35% vs bull-case tier C at 13.65%): the verdict spans D→C; sized to the bear end — the headline is C and even the bull case does not clear 15%.

## My thoughts / overlay
- The method range is narrow here, which helps: the preliminary run on the median base with default (uncalibrated) growth gave a weighted IRR of 13.68% and IV@15% of $163.20 — still Tier C. The final, guidance-calibrated run gives 11.14% / $125.26. Every defensible variant is Tier C; none clears 15% at $185.10.
- The structural headwind the model cannot fade away: state supplemental Medicaid payments. Q2 2026 reporting puts UHS's 2026 net benefit from these programs at about $1.52 billion, falling by about $500 million by 2032 under the 2025 federal budget law (OBBBA), with the phase-down starting in 2028. That is a direct, dated OE headwind inside the projection window and a reason the super-bull weight is only 10%. It is also, as noted in the DCF section, carried by scenario weights and stories rather than as a step-down in the base path: the $500 million is a revenue-side benefit decline (pre-mitigation, and UHS has until 2028 before the phase-down starts), but if a large share of it flowed to OE the weighted IRR would compress toward the C/D boundary — one more reason the verdict is sized to the bear end and confidence is medium, not high.
- Quality is adequate, not elite: revenue has compounded at 8.48% (5y) with operating margin back to 11.5%, but OE conversion is hostage to capex (de novo hospitals, bed expansions) and working capital (receivables days rose in H1 2026 per Q2 reporting), and EPS growth in Q2 2026 was mostly buybacks, not net-income growth.
- Margin of safety: there is none at $185.10 on these numbers — the weighted IV@15% sits 32.3% below the price (equivalently, the price is 47.8% above IV@15%) and the price is above even the bull-case IV@15% ($163.39). The stock clears Andrew's 15% hurdle only below ~$125.

## Final verdict
- **Final tier: C** (weighted IRR 11.14%; bear→bull band D→C, sized to the bear end)
- Confidence: **Medium** (TTM and median bases agree within ~6%, but OE volatility and the Medicaid phase-down keep it from high)
- One-liner: Solid hospital operator, moat 5/10 — does not clear 15% at $185.10 (11.1% weighted IRR, IV@15% $125.26); clears 15% only below ~$125, with Medicaid supplemental cuts and leverage capping the upside.
