# CW — Curtiss-Wright Corporation
v5 run, 2026-10-16. In scope (market cap $18.872B at $501.49, nasdaq_quote_api).

All figures below are copied from dcf_numbers.json, ttm.py output (ttm.json), or financials_history.csv — none are recomputed.

## What it is
Diversified engineered-products supplier in three segments — Naval & Power (naval nuclear propulsion, commercial nuclear, e.g. reactor coolant pumps), Defense Electronics (embedded computing, mission systems — the highest-margin segment), and Aerospace & Industrial (sensors, actuation, surface treatment). Content sits on long-life platforms: Columbia/Virginia-class submarines, Ford-class carriers, F-35 and other aircraft, plus commercial nuclear. Q2 2026: sales $924 million, up 5% YoY; adjusted EPS $3.72, up 15%; adjusted operating margin 19.4%; new orders $1.1 billion, up 8% (1.16x book-to-bill); backlog $4.5 billion, up 10% from Dec 31, 2025. Management raised FY2026 guidance: sales growth 8–9%, diluted EPS $15.10–$15.40 (up 14–16%).

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $643,402,000; capex $89,692,000 (tag PaymentsToAcquirePropertyPlantAndEquipment); SBC $21,520,000 (a real cost, but small — ~3% of OCF).
- **Conservative owner's earnings FY2025: $532,190,000 = $14.14/share** (latest FY OE/share, dcf_numbers.json).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $550,092,000 — close to the conservative figure, which raises confidence in the OE level.
- OE positive 5 of the last 5 fiscal years. Net debt $957,884,000; net debt is 1.57x normalized OE (diagnostics) — modest leverage, not a verdict driver.
- Share count is shrinking slowly (share CAGR −0.89%/yr; diluted shares 38,373,000 in FY2024 → 37,631,000 in FY2025), a mild buyback tailwind already credited in the growth blend (+0.89pp).

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $643,402,000 − prior YTD $97,820,000 + current YTD $175,528,000 = **TTM $721,110,000**
- Capex: FY $89,692,000 − prior YTD $35,154,000 + current YTD $41,283,000 = **TTM $95,821,000**
- SBC: FY $21,520,000 − prior YTD $10,484,000 + current YTD $14,305,000 = **TTM $25,341,000**
- Shares (current-YTD weighted diluted): **37,085,000**
- **TTM OE total $599,948,000 → base OE/share $16.18** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $12.10/share — lower because it averages in FY2023–24 before the recent margin/order inflection. The TTM base is used because it is the current, filing-derived run rate and is consistent with the raised FY2026 EPS guidance; the median-base preliminary run is reported in Thoughts as the conservative end of the method range.

## Moat: 7/10 — strong
Justification: qualified, often sole-source positions on nuclear-naval and flight-critical programs that run for decades, with aftermarket/spares annuity — but customers are concentrated (US government and a few primes), there are no network effects, and larger primes and budget politics bound pricing power.
- FOR: Sole-source / qualified-supplier status on naval nuclear propulsion and reactor coolant pumps — requalification is slow and safety-critical; Embedded content on long-life platforms (submarines, carriers, F-35) generates decades of spares, upgrades and service; Defense Electronics earns segment margins in the high-20s, evidence of pricing power in mission computing; $4.5B backlog (up 10% since Dec 2025) with 1.16x book-to-bill gives multi-year revenue visibility; Diversified across naval, defense electronics, commercial aerospace and commercial nuclear — no single program decides the outcome.
- AGAINST: Customer concentration — US DoD / Navy and a handful of prime contractors set budgets, timing and terms; Program and budget risk — ground defense sales fell 8% in Q2 2026 and Defense Electronics shipments slipped on program timing; No network effects or consumer surface — the moat is qualification and engineering depth, which determined competitors and in-housing primes can erode over a cycle; Commercial nuclear / SMR upside is real but slow and policy-dependent; CEO transition in January adds execution uncertainty.
- A 7 gives CAP = 11.1 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 11.1 years, 15-year projection.

## DCF — v5 final run (2026-10-16)
Growth sanity check: the engine's blended growth is 11.55% (rev CAGR 5y 7.91%, 3y 11.01%, latest rev YoY 12.08%, OE/share CAGR 2y 18.70%) plus the +0.89pp buyback adjustment = g_base 12.43%. That base start sits between guided FY2026 sales growth (8–9%) and guided EPS growth (14–16%) — reasonable for OE/share given margin expansion and buybacks. Bull (17.43%) sits modestly above guided EPS growth and assumes naval/nuclear orders convert faster than guide. Super bull (24.43%) is above any recent print — it is a deliberate 10%-probability tail requiring a multi-year naval + SMR nuclear supercycle at a 1.25x OE level; it is not presented as a forecast. Default offsets (−12/−5/0/+5/+12pp) and OE multipliers (0.75/0.90/1.00/1.10/1.25) were kept; probabilities 10/25/30/25/10. Price $501.49.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | 0.43% | 0.75 | Defense budgets slip, program delays compound, nuclear stalls | $90.27 | 4.67% |
| Bear | 25% | 7.43% | 0.90 | Growth fades to sales-guide level, margins stop expanding | $150.77 | 6.49% |
| Base | 30% | 12.43% | 1.00 | Guided trajectory decays normally over the CAP | $212.43 | 8.28% |
| Bull | 25% | 17.43% | 1.10 | Naval + commercial nuclear orders convert above guide | $296.39 | 10.50% |
| Super bull | 10% | 24.43% | 1.25 | Naval/SMR supercycle, sustained high-teens OE growth | $469.36 | 14.37% |

- **Probability-weighted: IV@15% $231.48 (−53.8% vs price), IV@12% $318.12, IV@10% $416.30, weighted IRR 8.85%, base-case IRR 8.28%**
- **Tier by numbers: D.** Diagnostics (dcf_numbers.json): OE yield 3.23%, terminal value 22.4% of IV@15%, scenario spread 5.20x, net debt 1.57x normalized OE, 9.5 months since FY end.
- Note the starkest fact in the table: even the super-bull scenario's IV@15% ($469.36) sits below the $501.49 price — at this price no scenario in the set clears a 15% return.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.5 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, quoted above with all four legs.
- **WIDE_SCENARIO_SPREAD** (5.20x): real — the range is driven by how long the current defense/nuclear upcycle lasts, not by data problems. Confidence is capped at medium, and the verdict is sized to the conservative end. It does not rescue the name: the weighted result is D on both the TTM base and the median base (see Thoughts).

## My thoughts / overlay
- Method range: the preliminary run on the normalized median base ($12.10/share, moat 5 defaults) gave weighted IRR 6.86% and weighted IV@15% $159.91 — Tier D. The final TTM-base run gives 8.85% — still Tier D. Defensible methods span D only; there is no input dispute that changes the verdict.
- Quality is not the debate: OE positive 5/5 years, SBC only ~3% of OCF, FCF conversion above 100% in Q2, backlog at a record, guidance raised. The debate is price: at $501.49 the OE yield is 3.23% and the stock trades at roughly double the weighted IV@15%. The price already pays for the bull path and part of the super-bull path.
- Balance sheet folded in: net debt $957,884,000 (1.57x normalized OE) is manageable and does not change the tier in either direction.
- Risks to the short/avoid case (i.e., what would make this D wrong): a genuine naval shipbuilding + SMR supercycle sustaining >20% OE/share growth for a decade, or large accretive M&A. Risks to holders: CEO transition, program timing slips (already visible in ground defense), and multiple compression from a ~34x earnings multiple.
- Margin of safety: the price that clears 15% on the weighted case is the weighted IV@15% itself, $231.48 — 53.8% below the current price. There is no margin of safety at $501.49; a buyer needs the super-bull world just to approach the hurdle.

## Final verdict
- **Final tier: D** (weighted IRR 8.85% on the TTM base; 6.86% on the median base — D under both)
- Confidence: **Medium** (high on OE quality and the TTM base; capped at medium by the 5.20x scenario spread)
- One-liner: High-quality defense/nuclear compounder, moat 7/10 — but at $501.49 it does not clear 15% in any scenario (weighted IRR 8.85%, IV@15 $231.48); it would need to fall to ~$231 to clear the hurdle on the weighted case.
