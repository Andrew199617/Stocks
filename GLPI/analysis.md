# GLPI — Gaming and Leisure Properties, Inc.
Engine 5.4.0 run, 2026-10-18. **Sector model misfit (REIT) — confidence low by rule.** All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.json, financials_history.csv or fundamentals.json — none are recomputed. Market cap (est) $11.000B at $39.28 (nasdaq_quote_api) — in scope under $40B.

## What it is
Triple-net gaming REIT spun out of PENN National in 2013. Owns the real estate under 71 gaming facilities in 21 states and leases it back to operators under long-term master leases (tenants pay taxes, insurance and maintenance). Tenants at 2026-06-30 (Q2 2026 release): PENN 34 facilities, Bally's 16, Caesars 6, Boyd 4, Strategic Gaming 4, Cordish 3, American Racing 1, Hard Rock 1, plus 2 under development (Bally's Chicago; Live! Virginia, Petersburg). Also extends development loans that convert to rent on completion/stabilization. Q2 2026: total revenue $430.5M, +9.0% YoY (acquisition-aided: Bally's Lincoln and the Bally's Chicago lease added cash income in the quarter); AFFO $304.0M, $1.03/share; 2026 AFFO/share guidance raised to $4.10–$4.12; quarterly dividend raised 5.1% to $0.82/share.

## Owner's earnings
**FY2025 (10-K via EDGAR, financials_history.csv):** operating cash flow $1,129,417,000; capex $191,289,000 (tag: PaymentsForConstructionInProcess — development/construction spend, not building maintenance; tenants bear maintenance under the triple-net leases); SBC $21,181,000 (always a real cost, but small here).
- **Conservative owner's earnings FY2025: $916,947,000 = $3.27/share** (key_numbers.md: latest FY OE/share $3.27)
- Maintenance version (oe_maintenance in financials_history.csv): $916,766,000 — essentially identical to the conservative figure, because D&A and the capex leg are the same construction spend here.
- OE positive 5 of the last 5 fiscal years. Net debt $6.979B (key_numbers.md).
- The OE definition is structurally harsh on this name: it deducts every dollar of development/construction funding (which buys future rent) as if it were maintenance capex, and gives no credit for the real-estate asset base. That is the SECTOR_MODEL_MISMATCH in one line — the company's own AFFO guide for 2026 is $4.10–$4.12/share against a $3.69 OE base.

**TTM check (ttm.py through Q2 2026, filing-direct):**
- OCF: FY $1,129,417,000 − prior YTD $545,867,000 + current YTD $619,831,000 = **TTM $1,203,381,000**
- Capex: FY $191,289,000 − prior YTD $0 + current YTD $9,078,000 = **TTM $200,367,000** — the legs mix tags: the FY leg is PaymentsForConstructionInProcess, both YTD legs are PaymentsToAcquireOtherPropertyPlantAndEquipment, so this is not a like-for-like leg.
- SBC: FY $21,181,000 − prior YTD $15,014,000 + current YTD $12,748,000 = **TTM $18,915,000**
- Shares (current-YTD weighted diluted): **284,593,000**
- **TTM OE total $984,099,000 → $3.46/share**

**Base used = the engine's normalized base, median of last 3 FY OE/share: $3.69/share** (base_source: median_of_last_3_fy_oe_per_share). The TTM $3.46 was not used as the base: its capex leg mixes two different tags (above), and both it and the latest FY ($3.27) are depressed by lumpy development funding rather than by rent deterioration — OCF itself rose through the TTM window ($1,203,381,000 TTM vs $1,129,417,000 FY2025). The median sits between the two filed prints and below the $4.10–$4.12 AFFO guide, so it is not the flattering choice.

## Moat: 5/10 — moderate/narrow, contractual not economic
Justification: long-term triple-net master leases and scarce licensed supply give durable rent, but ROIC is only ~10%, pricing power stops at the contractual escalator, and tenant credit (PENN, Bally's) is concentrated.
- Evidence (fundamentals.json): **ROIC proxy ~10.1% (2020), 8.7% (2021), 10.1% (2022), 10.6% (2023), 9.8% (2024), 10.3% (2025)** — stable through COVID and the rate shock, but only a modest spread over a levered REIT's cost of capital. Gross margin is not filed for this name (fundamentals.json gross_margin is null — a triple-net landlord books no COGS against rental income); the margin that exists is operating margin: 75.3% in FY2025 (operating income $1,201,453,000 on revenue $1,594,752,000).
- FOR: triple-net master leases — 15–30yr terms, annual escalators, cross-collateralization and corporate guarantees; tenants pay taxes, insurance and maintenance; no rent defaults since inception (2013); most leases carry rent coverage above 1.8x; scarce, license-limited gaming real estate in 21 states — a tenant cannot readily relocate a casino.
- AGAINST: tenant concentration — PENN operates 34 of 71 properties and levered Bally's 16 of 71; no pricing power beyond contractual escalators; single-sector (gaming only) exposure to the regional-casino consumer and to state gaming regulation; growth requires external capital — share count +3.3%/yr and net debt 6.8x normalized OE; ROIC proxy only ~10%.
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — engine 5.4.0 final run (2026-10-18)
**Growth recalibration (written reason):** the engine's blended growth (1.77%) is built on a broken revenue series — see BASIS_BREAK_SUSPECT below: the rev CAGR 3y component is 72.98%, a tagging artifact, and OE/share CAGR 2y is −6.21%, dragged by the FY2025 construction-capex spike. Neither is a rent signal. The prints that are clean: FY2025 total revenue +4.13% YoY (the two aligned tagging years, 2024→2025), TTM revenue $1,655,145,000, +5.76% YoY (fundamentals.json), Q2 2026 revenue +9.0% YoY (acquisition-aided), escalators plus a funded development pipeline converting to rent, offset by 3.3%/yr share issuance. Scenario starts were therefore set via offsets (−0.068 / −0.018 / +0.018 / +0.052 / +0.092 vs g_base 1.77%) to −5.0 / −0.0 / **3.6** / 7.0 / 11.0%. The base start (3.6%) sits below the latest clean prints (TTM revenue +5.76%, Q2 +9.0%) deliberately: most of the recent growth was bought with issued shares and debt, and per-share rent growth after dilution and escalator-only organic growth is slower than headline revenue growth. Probabilities 10/25/30/25/10 (defaults — contractual rent argues against fat tails in either direction); OE multipliers 0.75/0.90/1.00/1.10/1.25 (defaults). Price $39.28.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -5.0% | 0.75 | A major tenant (Bally's/PENN) credit event; rent restructured down | $16.56 | 7.45% |
| Bear | 25% | -0.0% | 0.90 | Escalators offset by dilution and a soft regional-casino consumer; no new deals | $24.50 | 10.20% |
| Base | 30% | 3.6% | 1.00 | Escalators + funded pipeline converts to rent; issuance continues | $31.63 | 12.59% |
| Bull | 25% | 7.0% | 1.10 | Pipeline (Chicago, Virginia) delivers on time; accretive acquisitions continue | $40.06 | 15.24% |
| Super bull | 10% | 11.0% | 1.25 | Development yields compound; tenant coverage improves; multiple re-rates | $53.68 | 19.15% |

- **Probability-weighted: IV@15% $32.65 (−16.9% vs price), IV@12% $43.20 (+10.0%), IV@10% $54.95, weighted IRR 12.93%, base-case IRR 12.59%**
- **Tier by numbers: C.** Diagnostics (key_numbers.md): OE yield 9.39%, terminal value 18.3% of IV@15%, scenario spread 3.24x, net debt 6.76x normalized OE, 9.6 months since FY end.
- Hurdle-clearing prices (weighted path, key_numbers.md): clears 15% at $32.65, 20% at $23.14, 25% at $17.88.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.6 months ago): TTM run via ttm.py through Q2 2026 and quoted above (TTM OE $3.46/share). Not used as the base for the tag-mixing reason stated there; the median base was retained and the TTM is reported alongside it.
- **DILUTION** (share count +3.33%/yr): this is acquisition-funding equity issuance, not compensation dilution — SBC is $21,181,000 in FY2025 and $18,915,000 TTM, small and falling against OCF above $1.1B. The engine already deducted the trend via the −3.33% growth adjustment on the revenue components; the scenario growth starts are per-share thinking, not double-counted again in the verdict.
- **BASIS_BREAK_SUSPECT**: a tagging break, not a divestiture or restatement. The engine's revenue tag (RevenueFromContractWithCustomerExcludingAssessedTax) captures only a slice of revenue in 2019–2021 ($128,391,000 / $102,999,000 / $109,693,000 in financials_history.csv) and nothing in 2022–2023 ($0), because the bulk of GLPI's income is lease revenue filed outside that contract-revenue tag; the series only aligns in 2024–2025 ($1,531,546,000 / $1,594,752,000). Hence the 72.98% rev CAGR 3y is an artifact. Growth inputs were chosen off the clean prints (FY2025 YoY +4.13% on the aligned years, TTM and quarterly revenue) and off OE/OCF, which are cash-flow tags unaffected by the break — no CAGR straddling the break was trusted.
- **CASH_INCLUDES_RESTRICTED**: confirmed on the FY2025 balance sheet (financials_history.csv): total debt $7,203,731,000 against a cash figure of $224,314,000 filed only under the combined cash + restricted-cash tag, giving net debt $6,979,417,000. Because no separate restricted-cash tag is filed, the restricted portion cannot be separated from the computed outputs — so net debt is understated by that unknown restricted amount, and the 6.76x leverage diagnostic is a floor, not the exact figure.
- **SECTOR_MODEL_MISMATCH** (Real Estate): accepted in full — confidence is low, the name is listed under sector misfits, and alert_eligible is false. The OE/capex frame deducts development funding as maintenance and ignores the property asset base; REIT-native AFFO ($4.10–$4.12/share guided for 2026; $1.03/share in Q2 2026) runs well above the $3.69 OE base, so this tier understates the name's cash economics by construction. Read the verdict as "the DCF frame says C," not as a full REIT valuation.
- **HIGH_NET_DEBT** (net debt 6.76x normalized OE): real leverage, partly mitigated by structure — the debt is secured by rent-producing real estate under long master leases with coverage above 1.8x on most leases, and FY2025 equity was $4,626,452,000 against assets of $12,909,609,000 and liabilities of $7,901,349,000. It is still the bear-case transmission channel: if a major tenant's rent is restructured, levered OE falls fast — which is why the super-bear OE multiplier is 0.75 and the verdict is sized to the bear end.
- **TIER_BAND** (bear C at 10.20% vs bull B at 15.24%): the band straddles the 15% hurdle, so the position, if any, is sized to the bear end — bear and base are both Tier C, and only the bull cases clear 15%.
- **WIDE_SCENARIO_SPREAD** (preliminary run, 4.48x): after the growth recalibration the final spread is 3.24x (key_numbers.md) — still wide, driven by tenant-credit outcomes, and confidence is low in any case under the sector-misfit rule.

## My thoughts / overlay
- The honest headline is the method range: on this OE/capex frame GLPI is a C (weighted IRR 12.93%, IV@15% $32.65 vs $39.28); on the REIT-native frame the same company guides to $4.10–$4.12 AFFO/share for 2026 and paid $3.10/share of dividends in FY2025 (fundamentals.json) — a buyer at $39.28 is mostly buying contractual rent yield plus escalator/pipeline growth, which this model prices only crudely. Neither frame alone is the answer; the flag record says which one this sweep used.
- Quality is not the debate: OE positive 5/5 years, no rent defaults since 2013, OCF grew from $1,129,417,000 (FY2025) to $1,203,381,000 TTM, and the dividend was raised in Q2 2026. The debate is price and tenant credit: PENN + Bally's are 50 of 71 facilities, and Bally's is the levered leg.
- What would change the tier inside this frame: a price near $32.65 (the 15% hurdle price), or development capex rolling off so filed OE/share converges toward AFFO.

## Final verdict
- **Final tier: C** (weighted IRR 12.93% on the final inputs; bear C → bull B band, sized to the bear end)
- Confidence: **Low** (sector model misfit by rule; HIGH_NET_DEBT and a 3.24x scenario spread reinforce it)
- One-liner: Durable triple-net gaming landlord, moat 5/10 — contractual rent and no defaults since 2013, but at $39.28 it does not clear 15% (weighted IRR 12.9%, IV@15% $32.65); it clears 15% only at ~$32.65, and the OE/capex model fits REITs poorly (sector misfit, confidence low).
