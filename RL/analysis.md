# RL — Ralph Lauren Corporation
v5 run, 2026-10-15. In scope (market cap $24.44B at $392.36, nasdaq_quote_api).

All figures below are copied from dcf_numbers.json, financials_history.csv, or key_numbers.md — none are recomputed. Research prints (guidance, latest quarter) are from cited earnings reporting and are labelled as such.

## What it is
Global luxury/premium lifestyle brand founded in 1967: apparel, footwear, accessories, home and fragrances, sold through wholesale, directly operated retail/e-commerce, and licensing. FY2026 revenue passed $8B for the first time (financials_history.csv: $8,114,500,000), balanced across North America, Europe and Asia, under the "Next Great Chapter: Drive" plan — brand elevation, full-price selling, key-city ecosystems, and recruiting younger consumers.

## Owner's earnings
**FY2026 (10-K via EDGAR, from financials_history.csv, with the capex override below):** operating cash flow $1,154,200,000; SBC $111,000,000 (always a real cost); capex $408,100,000 (override — see OVERRIDE).
- **Conservative owner's earnings FY2026: $635,100,000 = $10.19/share** (dcf_numbers.json: base_oe_latest_per_share $10.19)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $1,001,800,000 for FY2026 (financials_history.csv). It is materially above the conservative figure because FY2026 capex ($408.1M) far exceeded D&A ($233,000,000) — part of that capex is growth investment (new/flagship stores, digital), so the truth sits between the two definitions; the conservative figure is the base-case standard and is what the engine uses.
- OE positive 5 of the last 5 fiscal years. Net debt is -$749,100,000 — a net cash position (dcf_numbers.json); net debt is -0.99x normalized OE (diagnostics).
- **Base used = normalized base, median of last 3 FY OE/share = $12.11/share** (dcf_numbers.json: base_oe_normalized_per_share, base_source median_of_last_3_fy_oe_per_share). The latest FY ($10.19/share) is depressed by the FY2026 capex spike; the median (FY2024–FY2026) smooths that one-year spike without using the zero-filled preliminary figure. No TTM pin was used: the FY ended 6.6 months ago (diagnostics: months_since_fy_end 6.6), so no STALE_FY flag fired, and the median base is the engine standard.
- Latest prints since FY end (research, cited): Q1 FY2027 revenue $1.96B, up 14% reported / 13% constant currency, adjusted EPS up 22%, and management raised FY2027 guidance to 5–6% constant-currency revenue growth with 60–80bp of operating-margin expansion. FY2026 itself printed revenue +14.6% YoY (dcf_numbers.json: rev_yoy_latest) with gross margin 69.9% on mid-teens AUR growth (earnings reporting).

## OVERRIDE — capex (filing-sourced, bounded authority)
- **The gap:** the preliminary engine run exited 4 with `DATA_GAP:capex` — no full-year FY2026 capex under any tag the engine reads, so no tier was emitted.
- **The decision (worker, bounded authority (a) kind "filing"):** judgment.json carries `capex_override = {value: 408100000, kind: "filing", source: "Ralph Lauren FY2026 Form 10-K filed 2026-05-21 (accession 0001628280-26-037074), Consolidated Statements of Cash Flows, period ended 2026-03-28: Capital expenditures (408.1) tagged us-gaap:PaymentsToAcquireMachineryAndEquipment, scale 6 (millions); FY2025 comparative (216.2) on the same line"}`. The FY2026 figure is filed under `PaymentsToAcquireMachineryAndEquipment`, a tag outside the engine's candidate set; companyfacts carries only Q1–Q3 YTD values under the old tag. The value is 1.89x the last filed FY2025 capex of $216,200,000 — inside the 0.1x–10x band (dcf_numbers.json override_checks: out_of_band false).
- **Measured impact (dcf_numbers.json override_impact):** normalized base OE/share $14.23 zero-fill → $12.11 with the override; weighted IRR on the final configuration 9.10% zero-fill → 7.36% with the override. The override is the only reason a tier exists at all (unblocks the gap), and it moves the verdict down, not up — the zero-filled base was flattering the stock.
- The override fills only the missing FY2026 period (overrides_applied periods_filled: ["2026-03-28"], capex_tag "OVERRIDE" in financials_history.csv); filed values are never replaced.

## Moat: 6/10 — strong brand, not wide
Justification: Strong, durable brand moat (narrow-wide): proven pricing power and full-price selling through cycles, but no switching costs or network effects and fashion/macro exposure cap it below wide-moat 8+.
- FOR: Nearly 60-year iconic American luxury brand with proven pricing power — AUR up mid-teens in FY2026, gross margin 69.9%; full-price DTC model and key-city flagship ecosystem raise direct consumer control and lifetime value; balanced global footprint (North America / Europe / Asia) and multi-category lifestyle breadth; high returns on capital held through cycles, OE positive 5 of last 5 fiscal years; net cash balance sheet supports brand investment through downturns.
- AGAINST: No switching costs or network effects — consumers can move to rival luxury/premium brands freely; aspirational (not ultra-high-net-worth) customer base is macro and discretionary-spending sensitive; fashion and brand-heat cyclicality — taste shifts can erode pricing power; tariff and Asia sourcing exposure pressures gross margin (sourcing diversified, China now a minority of production, but not immune); founder-linked brand identity is a long-term succession/narrative risk.
- A 6 gives CAP = 9.8 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 9.8 years, 15-year projection.

## DCF — v5 final run (2026-10-15)
Growth recalibration (written reason): the engine's g_base is 13.87% (g_blend 10.51% + share-count adjustment 3.36pp), built from backward-looking prints — 5-yr revenue CAGR 13.01%, latest revenue YoY 14.63%, OE/share CAGR 2y -8.28% after the capex spike. Forward evidence points the other way: management guides FY2027 revenue growth to 5–6% in constant currency (raised after Q1), i.e. a guided deceleration from FY2026's pace. Scenario starts were therefore set via offsets (−0.16 / −0.10 / −0.05 / 0.00 / +0.06 vs g_base) to −2.1 / 3.9 / **8.9** / 13.9 / 19.9%. Sanity check against prints: the base start (8.9%) sits above guided revenue growth because OE/share gets margin-expansion and buyback leverage on top of revenue; the bull start (13.9%) matches the latest revenue YoY print (14.63%); the super-bull start (19.9%) sits below Q1 FY2027's adjusted EPS growth print (+22%) — no bull start exceeds a recent print. Bear and super-bear starts sit below recent prints for the written reason above: guided deceleration plus discretionary cyclicality (OE_VOLATILE flag). Probabilities 10/25/30/25/10 (defaults retained — the OE_VOLATILE instruction to widen bear weight is already reflected in the 35% combined bear-or-worse weight and the recalibrated starts); OE multipliers 0.75/0.90/1.00/1.10/1.25 (defaults). Price $392.36.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -2.1% | 0.75 | Discretionary recession; brand heat fades, capex stays elevated | $60.63 | 4.30% |
| Bear | 25% | 3.9% | 0.90 | Guided deceleration undershoots; tariffs bite margin | $95.02 | 5.58% |
| Base | 30% | 8.9% | 1.00 | Mid-single-digit revenue growth + margin expansion + buybacks | $131.87 | 6.96% |
| Bull | 25% | 13.9% | 1.10 | FY2026 momentum persists; Asia/China strength continues | $181.08 | 8.73% |
| Super bull | 10% | 19.9% | 1.25 | Q1 FY27 EPS pace sustained; capex normalizes down | $268.08 | 11.55% |

- **Probability-weighted: IV@15% $141.46, IV@12% $191.05, IV@10% $246.77, weighted IRR 7.36%, base-case IRR 6.96%**
- **Tier by numbers: D.** Diagnostics (dcf_numbers.json): OE yield 3.09%, terminal value 20.4% of IV@15%, scenario spread 4.42x, net debt -0.99x normalized OE, 6.6 months since FY end.
- Robustness check: the first final-configuration run with default offsets (base start 13.9%, super-bull 25.9%) gave weighted IRR 8.69% and weighted IV@15% $177.58 — still Tier D. The D verdict does not depend on the growth recalibration; it is driven by the $392.36 price against a $12.11 normalized OE/share base (3.09% OE yield).

## Flags — every fragility flag resolved
- **DATA_GAP:capex** (preliminary run): resolved by the filing-sourced override — see OVERRIDE. data_gap_uncovered is empty in the final run.
- **OVERRIDE_APPLIED:capex**: see OVERRIDE — gap, source, band check, and measured impact (base $14.23 → $12.11, weighted IRR 9.10% → 7.36% on the final configuration) are all recorded in judgment.json, dcf_numbers.json, and the override registry.
- **BUYBACK_TAILWIND** (share count shrinking 3.4%/yr): already credited via the +3.36pp share-count adjustment in g_base; not double-counted in the verdict.
- **OE_VOLATILE** (OE/share range over the last 5 years spans >3x): real — the series runs from the COVID-depressed years through the FY2025 peak and the FY2026 capex-spike year. Handled by the 3-yr median base, 35% combined bear-or-worse probability, and growth starts recalibrated to guidance rather than to peak prints.
- **WIDE_SCENARIO_SPREAD** (4.42x): real — outcomes range from recession-hit discretionary demand to sustained brand momentum. Confidence is capped at medium, and the verdict is sized to the conservative end.

## My thoughts / overlay
- This is a quality-versus-price verdict, not a quality verdict. The business just printed its best year on record, holds net cash (-$749,100,000 net debt), buys back stock at -3.4%/yr share count, and still only yields 3.09% on normalized owner's earnings at $392.36. Even the super-bull scenario (19.9% OE growth start, 1.25x OE) returns only 11.55% IRR at this price — below the 15% hurdle in every single scenario, not just on the weighted average.
- The main upside argument against this DCF is the maintenance-OE definition: FY2026 maintenance OE was $1,001,800,000 vs $635,100,000 conservative, because $408.1M of capex in an expansion year overstates maintenance needs (D&A was $233,000,000). That argument is real, but it was stress-tested implicitly: the zero-fill / default-offset runs and the bull cases all still land in Tier D, so no defensible input set found in this run clears 15% at $392.36.
- Balance sheet is a mitigant, not a catalyst: net cash of $749,100,000 is small against a $24.44B market cap and is already in the engine's IV via net debt.
- Hurdle price: the stock clears 15% at the weighted IV@15% of **$141.46**; a margin of safety requires a price meaningfully below that level. At $392.36 the price sits far above even the super-bull IV@15% of $268.08.

## Final verdict
- **Final tier: D** (weighted IRR 7.36% on the v5 final inputs; Tier D under both the recalibrated and default growth calibrations)
- Confidence: **Medium** (filing data complete after a sourced override and guidance is explicit, but the scenario spread is 4.42x and the FY2026 capex spike leaves the maintenance-vs-growth capex split genuinely uncertain)
- One-liner: High-quality luxury brand, moat 6/10, but priced far above owner's-earnings value — weighted IRR 7.4% and IV@15 $141 vs $392 price (Tier D); clears 15% only near $141.
