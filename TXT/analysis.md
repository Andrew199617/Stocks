# TXT — Textron Inc.
Engine 5.4.0 run, 2026-10-17. Price $75.93 (nasdaq_quote_api), market cap est. $13.69B — in scope under $40B.

All figures below are copied from dcf_numbers.json, ttm.json, financials_history.csv, or fundamentals.json — none are recomputed.

## What it is
Diversified aerospace/defense and industrial conglomerate: Textron Aviation (Cessna jets, Beechcraft turboprops — largest segment, $1,544M revenue in Q2 2026, $8.0B backlog), Bell (military and commercial rotorcraft, $1,074M in Q2 2026, including the MV-75 / FLRAA program), Textron Systems ($347M in Q2 2026), Industrial ($848M in Q2 2026 — Kautex fuel systems and specialized vehicles/E-Z-GO), and a small Finance segment. In April 2026 Textron announced intent to separate the Industrial segment, leaving a pure-play aerospace & defense company with >$12B expected 2026 revenue and $19B backlog (company announcement). Q3 2026 results are scheduled October 29, 2026; full-year 2026 adjusted EPS guidance reiterated at $6.40–$6.60, with manufacturing cash flow before pension guided $700–800M — both at risk ($0.20–$0.30 EPS, $150–250M cash flow) if additional MV-75 funding does not arrive.

## Owner's earnings
**Latest FY (period ended 2026-01-03, from financials_history.csv):** operating cash flow $1,312,000,000; capex $383,000,000; SBC $81,000,000 (always a real cost).
- **Conservative owner's earnings (OCF − capex − SBC): $848,000,000 = $4.70/share** (base_oe_latest_per_share $4.7044)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC, from financials_history.csv): $939,000,000 — same ballpark, modestly above the conservative figure.
- OE positive 5 of the last 5 fiscal years (oe_positive_years_of_last_5: 5/5). OE/share history is volatile: $1.72 (period ended 2021-01-02), $4.97 (2022-12-31), $3.82 (2023-12-30), $3.07 (2024-12-28), $4.70 (2026-01-03).
- Normalized base (median of last 3 FY OE/share): $3.8162/share.

**Base used = TTM owner's earnings through 2026-07-04, from ttm.py (filing-direct, no hand math):**
- OCF: FY $1,312,000,000 − prior YTD $263,000,000 + current YTD $187,000,000 = **TTM $1,236,000,000**
- Capex: FY $383,000,000 − prior YTD $134,000,000 + current YTD $228,000,000 = **TTM $477,000,000**
- SBC: FY $81,000,000 − prior YTD $34,000,000 + current YTD $40,000,000 = **TTM $87,000,000**
- Shares (current-YTD weighted diluted): **175,591,000**
- **TTM OE total $672,000,000 → base OE/share $3.8271** (base_source: ttm_json)
- The TTM base ($3.8271) essentially confirms the normalized median ($3.8162) — the two independent bases agree within $0.02, so neither is distorted. The latest-FY $4.70 is the high outlier, not the base. TTM capex is rising (Bell MV-75 buildout: H1 2026 capex $228M vs $134M prior YTD), which is why TTM OE sits well below the latest-FY figure despite TTM revenue of $15,299,000,000 (fundamentals.json TTM, +8.8% YoY).

**Balance sheet (from the filing, because the engine's debt tags are blank — see FLAGS):** At January 3, 2026 (10-K balance sheet, as reproduced in the Q2 2026 10-Q comparative column): Manufacturing group cash and equivalents $1,940M, Finance group cash $85M (combined $2,025M, matching the filed combined cash tag); Manufacturing total debt $3,539M (long-term $3,534M + current portion $5M, per the 10-K debt note), Finance group debt $339M; total liabilities $10,254M; shareholders' equity $7,875M; total assets $18,129M. Operating lease liabilities $404M (dcf_numbers.json). Leverage is moderate — total filed debt of ~$3.88B against $2.03B cash — not a distress story, but net debt is not zero and the engine cannot compute it from tags.

## Moat: 5/10 — moderate / narrow
Justification: Real franchise assets (Cessna/Beechcraft installed base and aftermarket, Bell's FLRAA program of record) but conglomerate returns are middling — the `roic_proxy` series in fundamentals.json is null for every year (Textron does not tag operating income in the form the tool reads), and the available return evidence is thin: gross margin was 17.8% (FY2016) and 16.7% (FY2017) in fundamentals.json, with gross margin not separately tagged in later years, and net margin is ~6.1% TTM (fundamentals.json). A 7+ moat would need ROIC demonstrably well above cost of capital through a cycle; that evidence is not in the computed outputs, so the score stays at 5.
- FOR: Cessna and Beechcraft are leading general-aviation brands with a large installed base driving recurring aftermarket revenue; Aviation backlog $8.0B at Q2 2026
- FOR: Bell's MV-75 (FLRAA) win is a U.S. Army program of record with multi-decade revenue visibility, plus H-1 / V-22 sustainment; ITAR protection and long qualification histories new entrants cannot replicate
- FOR: Diversified backlog and defense qualification / switching barriers across Bell and Textron Systems (Bell backlog $7.5B, Systems $3.3B at Q2 2026 per search reporting)
- AGAINST: Middling measured returns — net margin ~6%, no computable ROIC series in fundamentals.json, gross margin under 18% in the years it is tagged; no proven pricing power through a cycle
- AGAINST: U.S. government program concentration — MV-75 funding gap puts $0.20–$0.30 of guided EPS and $150–250M of guided cash flow at risk, plus a disclosed expected one-time unfavorable charge of $60–110M at initial production
- AGAINST: Competition in business jets (Gulfstream, Embraer, Dassault, Bombardier) and rotorcraft; cyclical business-jet demand
- AGAINST: Execution drag — Q2 2026 revenue +3.0% YoY but segment profit flat ($353M vs $352M), Aviation margin slipped to 10.7% from 11.2% and Bell margin to 7.0% from 7.9% on productivity / supply-chain issues; Industrial (Kautex) faces the EV transition and is being separated
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — final run (2026-10-17)
**Growth sanity check (mandatory):** The engine's blended start is 10.43%, built from revenue CAGRs of 4.90% (5y) and 4.75% (3y), latest FY revenue YoY +8.01%, and OE/share CAGR 2y +10.96%, with the +5pp buyback adjustment applied to the revenue components — that adjustment inflates the blend above every actual revenue print. Actual recent prints: Q2 2026 revenue +3.0% YoY, H1 2026 revenue +7.2% YoY ($7,522M vs $7,022M), TTM revenue +8.8% YoY (fundamentals.json), Aviation guided to ~+9% revenue in 2026, and Q2 2026 segment profit flat YoY. The preliminary run's super-bull start of 22.43% is far above anything Textron has printed — rejected with this written reason. Scenario starts were recalibrated via offsets (−0.1443 / −0.0843 / −0.0343 / +0.0057 / +0.0457 vs the blended start) to −4 / 2 / **7** / 11 / 15%: base 7% sits on the H1/TTM revenue prints plus the buyback tailwind already credited in the blend; super-bull 15% requires MV-75 ramp plus Aviation delivery recovery and is capped well below the preliminary 22.43%. Probabilities 10/25/30/25/10; OE multipliers 0.75/0.90/1.00/1.10/1.25 (defaults). Base OE/share $3.8271 (TTM). Price $75.93.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -4.0% | 0.75 | MV-75 funding fails / stop-work, business-jet cycle turns, capex stays elevated | $17.93 | 5.24% |
| Bear | 25% | 2.0% | 0.90 | Flat segment profit persists, margins stay compressed, slow deliveries | $27.66 | 7.03% |
| Base | 30% | 7.0% | 1.00 | Revenue grows at recent-print pace, buybacks continue, margins stabilize | $37.82 | 8.89% |
| Bull | 25% | 11.0% | 1.10 | Aviation productivity recovers, MV-75 funded and ramps, Industrial separation unlocks focus | $49.06 | 10.83% |
| Super bull | 10% | 15.0% | 1.25 | Full MV-75 ramp plus a strong jet cycle and margin expansion | $65.66 | 13.48% |

- **Probability-weighted: IV@15% $38.89 (−48.8% vs price), IV@12% $51.91, IV@10% $66.47, weighted IRR 9.10%, base-case IRR 8.89%**
- **Tier by numbers: D.** Diagnostics (dcf_numbers.json): OE yield 5.04%, terminal value 19.2% of IV@15%, scenario spread 3.66x, 9.4 months since FY end.
- Hurdle-clearing prices (dcf_numbers.json): clears 15% only at or below $38.89, 20% at $27.22, 25% at $20.82 — roughly half the current price for the 15% hurdle.

## Flags — every fragility flag resolved
- **STALE_FY** (latest FY ended 9.4 months ago): resolved by construction — the base is the TTM figure from ttm.py through 2026-07-04, legs quoted above. TTM OE/share $3.8271 confirms the normalized median $3.8162.
- **BUYBACK_TAILWIND** (share count shrinking 5.7%/yr): already credited via the +5pp share-count adjustment in the engine blend; noted here because that same adjustment is why the blend (10.43%) overstates revenue growth — scenario starts were recalibrated against actual prints rather than double-counting the tailwind. H1 2026 buybacks were $377M (2.3M shares in Q2 at an average $91.18 per search reporting of the Q2 release).
- **DEBT_TAGS_BLANK** (no debt tag for the latest FY — net debt UNKNOWN, not zero): resolved from the filing — see Balance sheet above: total debt ~$3,878M (Manufacturing $3,539M + Finance $339M at January 3, 2026, 10-K debt note), cash $2,025M combined, total liabilities $10,254M, equity $7,875M. Moderate leverage; no leverage verdict is taken from the engine.
- **CASH_INCLUDES_RESTRICTED** (only the combined cash + restricted-cash tag is filed, $2,025M): the balance sheet split shows Manufacturing cash $1,940M + Finance cash $85M = $2,025M; no separate restricted amount is stated in the computed outputs, so any net-debt figure would be understated by the restricted amount — one more reason no precise net-debt number is quoted.
- **TIER_BAND** (bear tier D at 7.03% vs bull tier C at 10.83%): the verdict spans D–C; the final verdict is sized to the bear end (D). Even the super-bull case (13.48% IRR, IV@15 $65.66) sits below the $75.93 price.
- Preliminary run also carried **WIDE_SCENARIO_SPREAD** (4.46x): after the growth recalibration the final spread is 3.66x — still wide; confidence is capped at medium.

## My thoughts / overlay
- This is a quality-of-price problem, not a quality-of-company problem: a real franchise with $19B of New Textron backlog, 5/5 positive OE years, and two independent bases (TTM and 3-yr median) agreeing at ~$3.82/share. At $75.93 the market is paying ~19.8x that base OE/share for a business whose recent revenue prints are +3% to +9% and whose segment profit was flat in Q2 2026.
- Method range: the preliminary default run (median base, unadjusted scenario starts up to 22.43%) printed weighted IRR 10.46% / IV@15 $46.46 — Tier C. The final TTM-based, print-checked run prints 9.10% / $38.89 — Tier D. Both sit far below the price; the range is C–D, never close to the 15% hurdle.
- Watch items: Q3 2026 print on October 29, 2026; MV-75 funding decision; rising Bell capex (TTM capex $477M vs FY $383M) pressuring OE; the Industrial separation; Aviation productivity recovery guided for next year.

## Final verdict
- **Final tier: D** (weighted IRR 9.10% on the final inputs; method range C–D, sized to the conservative end)
- Confidence: **Medium** (bases agree and filing data is complete, but scenario spread is 3.66x and the verdict spans tiers)
- One-liner: Solid aerospace/defense franchise, moat 5/10 — does not clear 15% at $75.93 (weighted IRR 9.1%, IV@15 $38.89); it would need a price at or below $38.89 to clear the hurdle.
