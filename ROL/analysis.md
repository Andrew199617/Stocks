# ROL — Rollins, Inc.
Engine 5.4.0 run, 2026-10-16. All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.json or financials_history.csv — none are recomputed.

## What it is
The second-largest pest-control operator in North America, built around Orkin plus HomeTeam Pest Defense, Critter Control and acquired brands such as Saela. Recurring residential, commercial and termite/ancillary services, mostly North America, sold against Rentokil/Terminix and a highly fragmented base of local operators. Market cap (est) $16.195B at $33.45 (nasdaq_quote_api) — in scope under $40B.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $678,107,000; capex $28,086,000; SBC $39,707,000 (always a real cost).
- **Conservative owner's earnings FY2025: $610,314,000 = $1.26/share** (latest FY OE/share, key_numbers.md).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC) FY2025: $744,041,000 — above the conservative figure because D&A ($124,744,000) runs well ahead of the small capex bill in this asset-light route business; the conservative OCF-based series is the one used throughout.
- OE positive 5 of the last 5 fiscal years. Net debt (latest) $509.8M, 0.88x normalized OE; operating lease liabilities are a further $428,175,000 (dcf_numbers.json). Share count CAGR −0.56%/yr — a mild buyback, already credited in the growth blend.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $678,107,000 − prior YTD $322,014,000 + current YTD $290,873,000 = **TTM $646,966,000**
- Capex: FY $28,086,000 − prior YTD $13,857,000 + current YTD $13,568,000 = **TTM $27,797,000**
- SBC: FY $39,707,000 − prior YTD $19,809,000 + current YTD $21,495,000 = **TTM $41,393,000**
- Shares (current-YTD weighted diluted): **481,397,000**
- **TTM OE total $577,776,000 → base OE/share $1.20** (base_source: ttm_json)
- The TTM base sits below the latest FY ($1.26) because H1 2026 operating cash flow fell versus H1 2025 — the softness behind the Q2 2026 print (revenue +7.9% YoY, organic +5.7%, residential organic +3.6%, gross margin down 100bp on people/medical and fuel costs, per the company's Q2 reporting). The 3-yr median base is lower still at $1.14/share; using any of the three bases leaves the tier unchanged (see method range).

## Moat: 7/10 — strong
Justification: Orkin brand, route density and recurring contracts drive ROIC well above the cost of capital through the cycle, but residential switching costs are low, the industry stays fragmented, and labor costs pressure margins.
- Evidence (fundamentals.json): the `roic_proxy` series runs 32.9% (FY2021), 31.1% (FY2022), 41.1% (FY2023), 29.7% (FY2024), 29.0% (FY2025) — well above the cost of capital in every year. Gross margin is level and high: 50.7% (FY2019) and 51.5% (FY2020) in fundamentals.json, ~52.7% in the FY2024-25 filings, and 52.8% in Q2 2026 (down 100bp YoY on medical/people and fuel costs).
- FOR: ROIC proxy 29-41% across FY2021-25, well above cost of capital through the cycle; Orkin brand awareness lowers customer-acquisition cost vs 20,000+ local rivals; local route density spreads fixed costs and supports industry-leading margins; recurring contracted revenue with proven pricing power (annual price increases accepted); fragmented industry gives a long tuck-in acquisition runway (e.g. Saela).
- AGAINST: Low residential switching costs; service is replicable by local operators; Rentokil/Terminix is larger globally and integrating its US network; labor, medical and fuel costs pressured gross margin -100bp in Q2 2026; AI-mediated search is raising residential customer-acquisition cost; termite damage litigation is a recurring tail risk.
- A 7 gives CAP = 11.1 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 11.1 years, 15-year projection. Not 9-10: there is no network effect or lock-in — a homeowner can switch exterminators with one phone call, so the moat is brand + density + execution, re-earned route by route.

## DCF — final run (2026-10-16)
Growth recalibration (written reason): the engine's blended growth is 12.29% (rev CAGR 5y 11.72%, 3y 11.74%, latest rev YoY 10.99%, OE/share CAGR 2y 14.49%), but every current print sits below it — TTM revenue +9.9% YoY (fundamentals.json ttm block), Q1 2026 revenue +10.2%, Q2 2026 +7.9% with organic only +5.7% and full-year organic guided at ≥6%. The blend is flattered by the 14.49% OE/share CAGR off the margin-expansion years. Scenario starts were therefore set via offsets (−0.093 / −0.058 / −0.028 / −0.003 / +0.017 vs g_base) to 3.0 / 6.5 / **9.5** / 12.0 / 14.0%. Base 9.5% ≈ TTM revenue growth and the ~9.6% next-12-month consensus growth reported in Q2 coverage; bull 12.0% requires the FY2021-23 pace plus acquisition contribution to return; super bull 14.0% matches the best recent year (FY2023 revenue +14.0% on the filed history) and is held to a 10% tail. Probabilities 10/25/30/25/10 (defaults — the earnings stream is unusually stable, but the Q2 margin/residential softness argues against loading the bull side); OE multipliers 0.75/0.90/1.00/1.10/1.25 (defaults). Price $33.45.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | 3.0% | 0.75 | Residential acquisition costs stay structurally higher; margins do not recover | $7.55 | 5.34% |
| Bear | 25% | 6.5% | 0.90 | Growth settles at the organic guide (~6%) with no acquisition kicker | $10.70 | 6.69% |
| Base | 30% | 9.5% | 1.00 | TTM-pace growth, normal fade over the 11.1-yr CAP | $13.70 | 7.97% |
| Bull | 25% | 12.0% | 1.10 | Residential recovers, commercial/termite strength holds, tuck-ins add | $16.97 | 9.30% |
| Super bull | 10% | 14.0% | 1.25 | Best-recent-year growth sustained with margin expansion | $21.21 | 10.89% |

- **Probability-weighted: IV@15% $13.91 (−58.4% vs price), IV@12% $18.80, IV@10% $24.31, weighted IRR 8.07%, base-case IRR 7.97%**
- **Tier by numbers: D; bear tier D → bull tier D (no TIER_BAND).** Diagnostics (key_numbers.md): OE yield 3.59%, terminal value 20.6% of IV@15%, scenario spread 2.81x, net debt 0.88x normalized OE, 9.5 months since FY end.
- Hurdle-clearing prices (weighted path): 15% at $13.91 · 20% at $9.57 · 25% at $7.23. Even the super-bull IV@15% ($21.21) sits 37% below the $33.45 price.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.5 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, legs quoted above. Note the TTM base is *lower* than the latest FY ($1.20 vs $1.26), so this is not a flattering adjustment.
- **WIDE_SCENARIO_SPREAD** (preliminary run, 4.45x): an artifact of the default offsets, which put the super-bull growth start at 24.3% — a rate Rollins has never printed. The recalibrated starts above narrow the final spread to 2.81x (key_numbers.md); the flag does not appear in the final run. Confidence is still held at medium, not high.
- No other flags fired in either run: no data gaps, no basis break, no NI/OCF divergence, no sector mismatch, no dilution (share count is shrinking slightly), IRR not at the floor.

## My thoughts / overlay
- The honest headline is the gap between business quality and price: this is one of the cleanest compounders in the sweep so far (ROIC 29-41%, gross margin ~52-53%, OE positive 5/5 years, net debt 0.88x normalized OE) and it still only earns an 8.07% weighted IRR at $33.45, because the market capitalizes it at roughly 28x TTM owner's earnings (OE yield 3.59%).
- Method range: the defensible bases span $1.14 (3-yr median) to $1.26 (latest FY) per share; scaling the weighted IV@15% across that range gives roughly $13-15 — Tier D on every variant, and even the preliminary default-growth run (12.29% blend, median base) printed only 8.48% weighted. The verdict does not rest on the recalibration; if anything the recalibration *raised* the base versus the median while cutting unrealistic bull growth.
- Watch items: whether residential organic growth (3.6% in Q2 2026) recovers or the AI-search acquisition-cost drag is structural; whether the Q2 gross-margin squeeze (medical/people +70bp, fuel +20bp per the Q2 call reporting) reverses under management's cost realignment; CFO transition execution; termite litigation.
- Margin of safety: none at this price — the weighted IV@15% is 58.4% below it. A buyer at $33.45 is paying for the bull case and getting paid like the base case.

## Final verdict
- **Final tier: D** (weighted IRR 8.07% on the final inputs; bear D → bull D, method range D throughout)
- Confidence: **Medium** (clean filing data and a stable history, held below high by the growth recalibration judgment and the open margin/residential questions)
- One-liner: Elite pest-control compounder, moat 7/10 — does not clear 15% at $33.45 (weighted IRR 8.1%, IV@15% $13.91); clears 15% only below ~$13.91.
