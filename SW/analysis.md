# SW — Smurfit Westrock plc
v5 run, 2026-10-15. Price $41.28 (nasdaq_quote_api), market cap $21.713B — in scope under $40B. All figures below are copied from dcf_numbers.json, ttm.json / ttm.py output, financials_history.csv, or key_numbers.md — none are recomputed.

## What it is
Global paper-based packaging company formed by the July 2024 combination of Smurfit Kappa and WestRock: containerboard mills plus corrugated and consumer packaging converting across North America, EMEA & APAC, and LATAM. Q2 2026 (reported July 29, 2026, per web search): net sales $8,031 million, net income $88 million, Adjusted EBITDA $1,140 million at a 14.2% margin; North America corrugated volumes were down in the quarter while EMEA/APAC and LATAM volumes rose. Management guided Q3 2026 Adjusted EBITDA of approximately $1.3 billion and full-year 2026 Adjusted EBITDA between $4.9 billion and $5.1 billion, with higher freight and energy costs flagged as 2026 headwinds. In September 2026 it agreed to acquire CMPC's Chilean containerboard and corrugated business for $420 million, expected to close in H1 2027.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $3,392,000,000; capex $2,192,000,000 (tag PaymentsToAcquireProductiveAssets); SBC $139,000,000 (always a real cost).
- **Conservative owner's earnings FY2025: $1,061,000,000 = $2.02/share** (base_oe_latest_per_share $2.017110266159696 in dcf_numbers.json)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $1,148,000,000 for FY2025 — same ballpark as the conservative figure, which raises confidence the base is not a definition artifact.
- OE history is merger-shaped, not organic: FY2022 conservative OE $435,000,000, FY2023 $564,000,000, FY2024 −$189,000,000 (partial combined year, capex and SBC stepped up before a full year of combined OCF), FY2025 $1,061,000,000. OE positive 3 of the last 4 years (dcf_numbers.json: "3/4").
- Net debt latest: $12,677,000,000 (dcf_numbers.json).

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $3,392,000,000 − prior YTD $1,064,000,000 + current YTD $969,000,000 = **TTM $3,297,000,000**
- Capex: FY $2,192,000,000 − prior YTD $999,000,000 + current YTD $1,089,000,000 = **TTM $2,282,000,000**
- SBC: FY $139,000,000 − prior YTD $79,000,000 + current YTD $55,000,000 = **TTM $115,000,000**
- Shares (current-YTD weighted diluted): **526,000,000**
- **TTM OE total $900,000,000 → base OE/share $1.71** (ttm_oe_per_share 1.7110266159695817; base_source: ttm_json)
- The engine's normalized base (median of last 3 FY) is $2.02/share — the same figure as FY2025 because the median year is FY2025 itself. The TTM base was used instead: it is the more current read and it is lower, reflecting weaker H1 2026 OCF and heavier capex, so it is also the conservative choice. Either base leaves the verdict in Tier D territory on the recalibrated growth below (see Thoughts for the rejected preliminary run).

## Moat: 4/10 — weak to moderate
Justification: Real scale and vertical integration in a commodity product, but only a small global share, limited demonstrated pricing power, cyclical volumes, and a capex bill that consumes most of operating cash flow — returns are earned by cost position and integration execution, not by a durable pricing moat.
- FOR: Scale and vertical integration — mills feeding a large converting network across North America, EMEA/APAC and LATAM, so global consumer customers can be served in multiple regions from one supplier.
- FOR: Merger synergy and cost program — at least $400 million of synergy targets cited in coverage of the combination, plus mill closures / footprint rationalization and contract clean-up lifting the historically weaker WestRock assets.
- FOR: Diversified, largely staple end-markets (food, beverage, consumer goods and e-commerce packaging) — demand is cyclical, not secularly collapsing, and paper packaging benefits from sustainability substitution away from plastic.
- AGAINST: Commodity containerboard economics — the combined company holds only about 6% of global containerboard capacity (Fastmarkets, via web search), so it is largely a price-taker; the announced $100/ton containerboard price hike is a test of pricing power, not proof of it.
- AGAINST: Cyclical volumes and overcapacity — North America corrugated volumes fell in Q2 2026, and new European containerboard capacity / oversupply can blunt pricing.
- AGAINST: Capex intensity and leverage — TTM capex of $2,282,000,000 against TTM OCF of $3,297,000,000 leaves thin owner's earnings, and net debt is $12,677,000,000 (14.1x the TTM OE total in the final diagnostics), so a downcycle hits equity OE first.
- AGAINST: Input-cost exposure — management flagged higher freight and energy costs for 2026; if containerboard pricing does not stick, those costs compress margins directly.
- A 4 gives CAP = 7.2 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 7.2 years, 15-year projection.

## DCF — v5 final run (2026-10-15)
Growth recalibration (written reason — the central judgment of this run): the engine's blended growth is 32.15% and g_base 27.15% only because every revenue component straddles the July 2024 merger — rev CAGR 5y 32.15%, rev CAGR 3y 32.15%, latest rev YoY +47.70% are Smurfit Kappa-only history being compared with the combined company, and the share count went from 260,000,000 (FY2023, Smurfit Kappa only) to 526,000,000 for the same reason. The actual current print is Q2 2026 revenue +1.15% year over year (web search). Scenario starts were therefore set via offsets (−0.3215 / −0.2715 / −0.2315 / −0.1915 / −0.1415 vs g_base) to −5 / 0 / **4** / 8 / 13%. The 4% base start sits above the Q2 revenue print for one stated reason: OE can grow faster than revenue for a period if the synergy/cost program and containerboard pricing land on a depressed TTM OE base — and the OE multipliers, not a higher growth start, carry most of that recovery. Bull/super-bull starts of 8%/13% require sustained pricing plus synergy delivery; they are deliberately not set anywhere near the preliminary run's 32–39% starts, which no recent print supports. Probabilities were shifted bearish (15/30/30/15/10 vs the 10/25/30/25/10 default) for the leverage, the falling TTM base, and the volume/cost picture above. OE multipliers are the defaults 0.75/0.90/1.00/1.10/1.25. Price $41.28.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | -5.0% | 0.75 | Containerboard pricing fails, volumes fall, freight/energy costs stick; levered OE shrinks | $7.86 | 4.71% |
| Bear | 30% | 0.0% | 0.90 | No real growth; synergies only offset cost inflation | $11.46 | 5.90% |
| Base | 30% | 4.0% | 1.00 | Low-single-digit growth plus gradual synergy/pricing capture on the TTM base | $14.86 | 7.04% |
| Bull | 15% | 8.0% | 1.10 | Price hike sticks, volumes recover, cost take-out delivers | $19.04 | 8.42% |
| Super bull | 10% | 13.0% | 1.25 | Full synergy + pricing + volume cycle all land together | $26.10 | 10.66% |

- **Probability-weighted: IV@15% $14.54, IV@12% $19.22, IV@10% $24.42, weighted IRR 6.96%, base-case IRR 7.04%**
- **Tier by numbers: D.** Even the super-bull scenario (10.66% IRR, IV@15 $26.10) sits below the $41.28 price — no scenario in this run clears the 15% hurdle at the current price.
- Diagnostics (dcf_numbers.json): OE yield 4.14%, terminal value 18.21% of IV@15%, scenario spread 3.32x, net debt 14.09x normalized OE, 9.5 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (latest fiscal year ended 9 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, quoted in full above (TTM OE/share $1.71 vs FY2025 $2.02).
- **DILUTION** (share count growing 26.3%/yr): not ongoing dilution — it is the merger share issuance. The share series in financials_history.csv goes 261,000,000 (FY2022) / 260,000,000 (FY2023, Smurfit Kappa only) → 389,000,000 (FY2024, partial combined year) → 526,000,000 (FY2025 and current-YTD TTM, flat). SBC is not the driver: SBC was $139,000,000 in FY2025 and $115,000,000 TTM, down from the FY2024 figure in the history file. The engine's −5pp share-count growth adjustment was more than undone by the explicit growth recalibration above, so no dilution drag is double-counted.
- **BASIS_BREAK_SUSPECT** (>60% revenue jump in the last 5 years): identified — the July 2024 Smurfit Kappa / WestRock combination. Revenue went $12,093,000,000 (FY2023, Smurfit Kappa only) → $21,109,000,000 (FY2024, partial) → $31,179,000,000 (FY2025, first full combined year). No CAGR that straddles that break was trusted; scenario starts were set from the current combined company's actual prints (Q2 2026 revenue +1.15% YoY) instead.
- **NI_OCF_DIVERGENCE** (net income vs OCF differ by >40% in 2023, 2025): principally the non-cash depreciation scale of a mill-heavy asset base, which grew with the merger. FY2025 net income $699,000,000 vs OCF $3,392,000,000 with D&A of $2,550,000,000 in the same year (financials_history.csv); FY2023 net income $825,000,000 vs OCF $1,559,000,000 with D&A of $580,000,000. The conservative OE used throughout is built directly on OCF minus capex and SBC, so the NI/OCF gap does not contaminate the base — if anything it shows why the NI-based maintenance definition is the secondary one here (it still lands at $1,148,000,000 for FY2025, close to the conservative $1,061,000,000).
- **WIDE_SCENARIO_SPREAD**: present in the preliminary run (4.30x); in the final run the spread is 3.32x — still wide for a cyclical, levered packager, which is why confidence is low and the verdict is sized to the conservative end. No scenario, including super bull, reaches the price.
- **HIGH_NET_DEBT** (net debt 14.09x normalized OE in the final diagnostics; $12,677,000,000): folded into the verdict explicitly — probabilities were shifted to 45% bear-or-worse, the super-bear OE multiplier is 0.75 on a shrinking growth path, and the tier is D on the weighted case, not on a stress case. Leverage against EBITDA is a different (smaller) multiple, but on the owner's-earnings measure this sweep uses, the cushion is thin: TTM OE total is $900,000,000 against that debt load.

## My thoughts / overlay
- The honest headline is the rejection of the preliminary run, not the final number alone: the unadjusted engine pass (median base $2.02, g_base 27.15%, default scenarios) printed a weighted IRR of 16.61% and IV@15% of $47.99 — Tier B. That result is a merger-accounting artifact: it grows a combined company at the rate created by adding WestRock's revenue to Smurfit Kappa's. Quoting it without the basis break would be exactly the failure this sweep's sanity-check rule exists to catch.
- On defensible inputs the picture is consistent: TTM OE/share has fallen from $2.02 (FY2025) to $1.71, Q2 2026 revenue grew 1.15% YoY, North America volumes fell, and 2026 freight/energy costs are guided up. The bull case is real but operational (synergies, pricing, footprint) — it is a margin-recovery story, and even granting it in the super-bull scenario only reaches a 10.66% IRR at $41.28.
- Balance sheet cuts both ways: the debt is termed and the company is deleveraging per coverage of FY2025, but on owner's earnings the leverage is 14.09x, so equity holders are last in line behind a $2,282,000,000 TTM capex bill that cannot be skipped in a mill business — most of that capex is maintenance in substance, which is why the conservative definition (total capex) is the right base here and the maintenance definition was not used to flatter it.
- Price that clears 15%: the weighted IV@15% is $14.54 — the stock would need to fall to roughly that level for the weighted case to clear Andrew's 15% hurdle, and even the super-bull IV@15% is $26.10. There is no margin of safety at $41.28 on any scenario in this run.

## Final verdict
- **Final tier: D** (weighted IRR 6.96% on the v5 final inputs; tier by numbers D, no override)
- Confidence: **Low** (merger-basis history, cyclical pricing, high leverage, and a 3.32x scenario spread — the direction is clear, the exact OE path is not)
- One-liner: Cyclical, capex-heavy packager with a weak-moderate moat 4/10 — does not clear 15% on any scenario at $41.28 (weighted IRR 6.96%, weighted IV@15 $14.54); it clears 15% only at ~$14.54, and the preliminary Tier B print was a merger basis-break artifact.
