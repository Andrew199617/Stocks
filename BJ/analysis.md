# BJ — BJ's Wholesale Club Holdings, Inc.
v5.4 run, 2026-10-18. Market cap $13.596B at $102.95 (nasdaq_quote_api) — in scope under $40B.

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.json, financials_history.csv or fundamentals.json — none are recomputed.

## What it is
The #3 US membership warehouse club: 267 clubs and 205+ BJ's Gas locations in 22 states, East-Coast concentrated, headquartered in Marlborough, MA (fundamentals.json profile: SIC 5331 Retail-Variety Stores). Grocery-first assortment drives frequent trips; members pay an annual fee (record 8.5 million members at Q2 FY27, per the Q2 release). Growth is footprint-led: 25–30 new clubs every two years, including a Texas entry.

## Owner's earnings
**FY2026 (10-K, fiscal year ended 2026-01-31, from financials_history.csv):** operating cash flow $1,030,056,000; capex $702,048,000; SBC $47,200,000 (always a real cost, and small here).
- **Conservative owner's earnings FY2026: $280,808,000 = $2.13/share** (latest FY OE/share $2.1263 in dcf_numbers.json).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $676,372,000 — far above the conservative figure, and the gap is the story of the base: FY2026 capex of $702,048,000 runs at more than twice D&A of $288,594,000 because most of it is growth capex (new clubs, a new ambient distribution center; management guided capex of approximately $800 million for the current fiscal year). The standardized conservative base charges all of it, which penalizes a growing club operator; the verdict below survives even that debate because the price is so far above either base's value (see Thoughts).
- OE positive 5 of the last 5 fiscal years, but the OE/share path is falling under the capex ramp: $4.45 (FY2021) → $3.29 → $2.55 → $1.57 → $1.98 → $2.13 (FY2026), while capex climbed from $218,333,000 (FY2021) to $702,048,000 (FY2026).
- Net debt $472,854,000 (1.50x normalized OE per diagnostics); operating lease liabilities are a further $2,089,632,000 — the clubs are leased, standard for the model. No meaningful dividend; buybacks were $552,653,000 TTM (fundamentals.json) and diluted shares fell from 139,109,188 (FY2020) to 132,066,000 (FY2026), 128,561,000 on the TTM current-YTD count.

**Base used = TTM owner's earnings through Q2 FY27 (period ended 2026-08-01), from ttm.py (filing-direct, no hand math):**
- OCF: FY $1,030,056,000 − prior YTD $457,957,000 + current YTD $541,439,000 = **TTM $1,113,538,000**
- Capex: FY $702,048,000 − prior YTD $306,065,000 + current YTD $359,339,000 = **TTM $755,322,000**
- SBC: FY $47,200,000 − prior YTD $24,599,000 + current YTD $28,740,000 = **TTM $51,341,000**
- Shares (current-YTD weighted diluted): **128,561,000**
- **TTM OE total $306,875,000 → base OE/share $2.39** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $1.98/share. The TTM base is preferred: it captures two quarters of the new-club cohort and the buyback-shrunk share count, and it is charged with even heavier growth capex ($755,322,000 TTM) than FY2026, so it is not a flattering pick.

## Moat: 5/10 — moderate / narrow
Justification: a proven, durable membership model with ROIC well above the cost of capital through the last five years, but subscale against Costco and Sam's Club, East-Coast concentrated, with only an annual membership fee as lock-in and a steadily fading ROIC trend.
- FOR: Membership economics — record 8.5 million members, membership fee income +9.9% YoY in Q2 FY27, higher-tier members at a record 43% of the base; ROIC proxy (fundamentals.json) above 20% for five straight years — 35.1% (FY2021), 34.9%, 29.5%, 26.6%, 23.9%, 22.8% (FY2026) — on a stable gross margin (19.31% FY2021, 18.47%, 17.77%, 18.24%, 18.36%, 18.64% FY2026); East-Coast density plus gas stations driving frequent grocery-first trips, 18 consecutive quarters of traffic growth and 15 of market-share gains; disciplined expansion (25–30 clubs per two years; 2022–24 cohorts performing above chain average).
- AGAINST: Subscale #3 — 267 clubs vs Costco's ~900 and Sam's ~600, with correspondingly weaker supplier leverage and no international business; near-zero switching costs beyond the annual fee; ROIC has faded every year for five years as growth capex rises, and merchandise gross margin fell ~20bp in Q2 FY27 on pricing investment — pricing power is defensive; structurally thin operating margin (3.81% FY2026) leaves no buffer in a price war.
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — v5.4 final run (2026-10-18)
Growth sanity check (mandatory): the engine's blended start is 6.82% (components: revenue CAGR 5y 6.81%, 3y 3.56%, latest FY YoY 4.66%, OE/share CAGR 2y 16.26%). Recent prints: FY2026 revenue +4.66%; TTM revenue $22,811,630,000, +9.09% YoY (fundamentals.json); Q2 FY27 total revenue +15.7% YoY — but that print is gasoline-inflated (total comparable club sales +11.9% vs +3.1% excluding gasoline, and management guides comparable sales ex-gasoline of 2.0–3.0%). Default scenario starts are kept, with the bull-case reason written here: the bull start of 11.82% sits *below* the Q2 total print of +15.7% because that print is a fuel price/volume spike, not merchandise growth; the underlying business grows at guided comps of 2–3% plus ~4–5% from new clubs on a ~265-club base, which is exactly what the 6.82% base start embeds. The super-bull start of 18.82% exceeds even the fuel-inflated print, so no scenario is capped below observed reality. Probabilities 10/25/30/25/10; OE multipliers 0.75/0.90/1.00/1.10/1.25. Price $102.95.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -5.18% | 0.75 | Price war / consumer pullback; club growth stalls, OE compresses | $10.65 | 3.66% |
| Bear | 25% | 1.82% | 0.90 | Comps at the low end of guidance, no footprint benefit | $17.13 | 4.56% |
| Base | 30% | 6.82% | 1.00 | Guided 2–3% ex-gas comps plus steady club openings fade over the CAP | $23.42 | 5.47% |
| Bull | 25% | 11.82% | 1.10 | Texas/new-market clubs outperform, higher-tier mix keeps compounding | $31.65 | 6.64% |
| Super bull | 10% | 18.82% | 1.25 | Sustained share gains plus operating leverage on the bigger base | $47.82 | 8.82% |

- **Probability-weighted: IV@15% $25.07 (−75.6% vs price), IV@12% $33.55, IV@10% $43.03, weighted IRR 5.73%, base-case IRR 5.47%**
- **Tier by numbers: D.** Bear→bull band is D→D (bear IRR 4.56%, bull IRR 6.64%) — no TIER_BAND ambiguity; even the super-bull case (8.82%) is a D. Diagnostics: OE yield 2.32%, terminal value 19.5% of IV@15%, scenario spread 4.49x, net debt 1.50x normalized OE, 8.5 months since FY end.
- Hurdle prices: clears 15% at $25.07 (IV@15), 20% at $17.49 (IV@20), 25% at $13.34 (IV@25).

## Flags — every fragility flag resolved
- **STALE_FY** (latest FY ended 8.5 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 FY27 (period ended 2026-08-01, 10-Q filed 2026-08-25), quoted above.
- **NI_OCF_DIVERGENCE** (net income vs OCF differ by >40% in FY2025 and FY2026): D&A explains the bulk of it — FY2026 net income $578,377,000 plus D&A $288,594,000 and SBC $47,200,000 closes most of the gap to OCF of $1,030,056,000, with the remainder working-capital timing (inventory/payables swings around the January fiscal year-end and other non-cash items). No one-off distorts the base: the divergence is D&A scale, not an earnings-quality break, and the base is built from OCF directly, so the steadier series is the one in use.
- **WIDE_SCENARIO_SPREAD** (super-bull IV 4.5x super-bear IV): the spread is the growth-capex debate, priced — the conservative base charges all $755,322,000 of TTM capex (mostly new clubs) while the maintenance view charges only D&A; the five scenarios span that argument (IV@15 $10.65 → $47.82). Confidence is held at medium, never high, while this flag stands. The verdict is insensitive to the spread: every scenario, super-bull included (8.82%), is Tier D at $102.95.

## Final verdict
**Tier D.** Weighted IRR 5.73%, weighted IV@15% $25.07 against a $102.95 price (−75.6%); the name clears 15% only at or below $25.07, 20% at $17.49, 25% at $13.34. A dependable, narrow-moat membership operator with five straight years of 20%+ ROIC — but at this price the market is paying for growth the conservative owner's-earnings stream does not support, on either the TTM base ($2.39/share) or the maintenance view. Not a buy at $102.95 on this model.