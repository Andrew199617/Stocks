# APA — APA Corporation
Engine 5.4.0 run, 2026-10-16. Price $49.18 (nasdaq_quote_api); market cap est. $17.656B — in scope under $40B. All figures below are copied from dcf_numbers.json, ttm.json, financials_history.csv or fundamentals.json — none are recomputed. Where a figure comes from the filing text or a cited search result instead, it is marked as such.

## What it is
Independent oil & gas E&P (former Apache): Permian Basin core in the U.S., a large Egyptian position under production-sharing contracts, North Sea remnants (2024 impairments taken), Alaska exploration, and the GranMorgu development in Suriname Block 58 (50% working interest, TotalEnergies operator) targeting first oil in mid-2028. Q2 2026 reported production ~410,000 BOE/d (adjusted production 347,000 BOE/d excluding Egypt noncontrolling-interest and tax barrels); U.S. oil production 123,500 bbl/d beat guidance (search result: Q2 2026 earnings coverage). Pure commodity price-taker.

## Owner's earnings
**FY2025 (10-K via EDGAR, financials_history.csv):** operating cash flow $4,545,000,000; SBC $107,000,000 (always a real cost); capex $2,740,000,000 — by filing override, see OVERRIDES.
- **Conservative owner's earnings FY2025: $1,698,000,000 = $4.73/share** (dcf_numbers.json base_oe_total_latest_fy / base_oe_latest_per_share).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $2,064,000,000 for FY2025 (financials_history.csv) — same ballpark as the conservative figure; FY2024 maintenance OE was $900,000,000 vs conservative $831,000,000 (both with the override capex fill).
- OE positive 5 of the last 5 fiscal years (dcf_numbers.json). With the capex override applied the series is $0.99 (2023) / $2.35 (2024) / $4.73 (2025) per share, and turns negative in 2019–2020 purely because the single-value fill overstates capex in those low-capex years (true filed additions were $2,634M in 2019 and $1,274M in 2020 — companyfacts, PaymentsToExploreAndDevelopOilAndGasProperties; the fill is $2,740M in every year). Pre-2023 history in financials_history.csv is a fill artifact, not filed truth; the last-3 median is barely affected (below).
- Net debt $3,977,000,000 (dcf_numbers.json), plus lease liabilities $317,000,000. Management is deleveraging toward a $3B net-debt target and guides to returning ≥60% of free cash flow (search result: Q2 2026 call coverage); no debt maturities until 2029 after $634M of near-term maturities repaid in early 2026 (search result: Q1 2026 call coverage). Dividend $1.00/share TTM (fundamentals.json dividends).

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $4,545,000,000 − prior YTD $2,277,000,000 + current YTD $2,260,000,000 = **TTM $4,528,000,000**
- Capex: **TTM $2,740,000,000**, all three legs filled by the capex override at the FY2025 rate (they cancel; see OVERRIDES). Caveat, from the filer's own Q2 2026 10-Q cash-flow statement (filing text): actual additions to upstream oil and gas property were $1,111M in H1 2026 vs $1,437M in H1 2025, so a true TTM capex is lower than $2,740M and the TTM base used here is conservative on the capex leg — the direction that lowers OE.
- SBC: **TTM $107,000,000**, YTD legs filled by the sbc_override at the last filed annual rate (see OVERRIDES); the FY leg is the filed $107,000,000.
- Shares (current-YTD weighted diluted): **354,000,000**
- **TTM OE total $1,681,000,000 → base OE/share $4.75** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $2.35/share — the FY2024 trough year (Callon stub year, weak gas, North Sea impairment era). It is retained as the method-range floor below, not used as the base: the TTM base is the current post-Callon asset base, its OCF leg is flat vs FY2025 ($4,528M vs $4,545M — not a price spike), and its capex leg is if anything overstated.

## OVERRIDES — capex (filing) and SBC (estimate)
- **The gap:** the preliminary engine run exited 4 with `DATA_GAP:capex`. APA files capital expenditures only as additions to oil and gas property under the us-gaap tag PaymentsToExploreAndDevelopOilAndGasProperties — the only capex-like Payments* tag in its companyfacts — which the engine does not read; every candidate tag is empty in every year.
- **capex_override = {value: 2740000000, kind: "filing"}**: the FY2025 figure from the FY2025 10-K MD&A Sources and Uses table ('Additions to oil and gas property' $2,740M for FY2025, $2,851M for FY2024, $2,313M for FY2023; the table's footnote states these are capital expenditures on a cash basis), identical to the companyfacts tag values. $2,740M is also the median of the three filed years. The engine applies the single value to every missing period: vs the true per-year figures it overstates FY2023 capex by $427M (conservative direction) and understates FY2024 by $111M (raises that year's OE slightly — noted, not hidden); FY2025 is exact. **Measured impact (key_numbers.md, on the TTM base actually used, same final configuration with overrides toggled off):** base OE/share $12.49 (no override) → $4.75 (with override), −61.98%; weighted IRR 17.55% → 10.82% (−6.73pp). Unblocks tier: YES — without the override the filing gap blocks scoring entirely. The out-of-band flag is mechanical (last_filed_value is null — no engine-read tag was ever filed) and is acknowledged in judgment.json's ack_reason.
- **sbc_override = {value: 107000000, kind: "estimate"}**: APA tags SBC only annually; its 10-Q cash-flow statements present no stock-compensation line at all (verified in the Q2 2026 10-Q reconciliation), so ttm.py exited with 'sbc: no post-FY YTD fact'. The override is exactly 1.0× the last filed annual SBC ($107M, FY2025 10-K), inside the estimate band, and only fills ttm.py's YTD legs (prorated by days); the annual history is untouched because SBC is filed for every annual period. SBC is ~2.4% of FY2025 OCF, so the assumption moves the base by cents.
- Both overrides are recorded in score.json and the central registry (_system/overrides_registry.json).

## Moat: 3/10 — weak; asset quality, no franchise
Justification: a pure commodity price-taker. The roic_proxy series in fundamentals.json swings from −40.3% (2019) and −47.2% (2020) to +70.4% (2022), +37.6% (2023), +16.6% (2024) and +18.6% (2025) — the cycle sets returns, not the company. Gross margin is not computable from filed tags (revenue itself is filed only under a filer extension concept; fundamentals.json gross_margin is null for every year), so no margin evidence offsets that. A 7+ would need ROIC above the cost of capital through a cycle; APA has two deeply negative years in the last seven.
- FOR: Permian capital efficiency — full-year U.S. oil guidance raised to 123,000 bbl/d on an unchanged $1.3B U.S. capital budget, four rigs sustaining output once estimated to need eight (search results: Q2 2026 call coverage); GranMorgu carried economics — TotalEnergies pays 87.5% of the first $10B of gross Block 58 development capex under the JV terms in the FY2025 10-K (filing text), first oil targeted mid-2028; Egypt gas re-pricing — nearly half of Egyptian gas production now under a revised higher-price agreement (search result: Q2 2026 coverage); cost program — exit-2026 run-rate savings target raised to $500M, LOE guidance cut to $1.5B (search result: Q2 2026 call coverage).
- AGAINST: no pricing power (ROIC evidence above); depleting asset base — reserves must be continuously replaced, FY2025 capex $2,740M against OCF $4,545M; Egypt PSC mechanics — higher oil prices mechanically reduce APA's entitlement (adjusted) volumes, plus sovereign/arrears exposure; per-share dilution from M&A — diluted shares 309M (FY2023) → 359M (FY2025) on the all-stock Callon acquisition; U.S. gas price collapse in Q2 2026 (realized gas price fell sharply year over year, search result: Zacks Q2 coverage) offsetting oil strength.
- A 3 gives CAP = 5.9 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 5.9 years, 15-year projection.

## DCF — engine 5.4 final run (2026-10-16)
Growth recalibration (written reason, mandatory sanity check): the engine's blended growth is 118.79% and g_base hit the 35% cap. Every component is an artifact: revenue components are all null (revenue is filed only under a filer extension tag), so the blend is a single OE/share CAGR 2y of +118.79% that itself runs off the override-filled FY2023 OE/share ($0.99, depressed because the single-value capex fill overstates FY2023 capex). Actual recent prints say volume is flat-to-down and OE is a price derivative: Q2 2026 reported production fell year over year, U.S. oil guidance is +2.5% (120k → 123k bbl/d), FY2026 upstream capital is guided to ~$2.07B (search result: Q2 2026 coverage) vs $2,740M spent in FY2025, and management's ~$2.3B FY2026 free-cash-flow guide at strip includes ~$950M of pretax gas-trading cash flow (search result: Q2 2026 call coverage) — a windfall, not a growth rate. Scenario starts were therefore set via offsets (−0.50 / −0.42 / −0.35 / −0.29 / −0.23 vs the capped g_base) to **−10 / −7 / 0 / +6 / +12%**: the base case holds OE/share flat from the TTM base (volume growth and GranMorgu's 2028 start offset decline and price normalization), bear starts are negative because OE is a commodity derivative, and even the super-bull start sits far below the engine blend — justified because the blend is a fill artifact, not a print. (The engine floors the super-bear start at −10%.) OE multipliers were widened on the bear side to 0.50/0.75/1.00/1.10/1.25 (from 0.75/0.90 defaults) because the filed record shows trough OE is a small fraction of peak (the override-filled history in financials_history.csv prints OE/share of −$3.70 in 2020 and $0.99 in 2023 against $4.73 in FY2025, and even the 2020 figure is flattered by that year's capex having been flexed down hard). Probabilities bear-weighted to 15/30/30/15/10 per the OE_VOLATILE flag. Price $49.18.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | −10.0% | 0.50 | Oil/gas downcycle: OE halves from the TTM base, capex flexes but cannot offset price | $12.43 | 5.39% |
| Bear | 30% | −7.0% | 0.75 | Prices normalize lower; gas stays weak; Egypt entitlement volumes shrink | $20.81 | 7.54% |
| Base | 30% | 0.0% | 1.00 | Flat OE/share: Permian efficiency + cost savings + GranMorgu (2028) offset decline | $35.66 | 11.52% |
| Bull | 15% | 6.0% | 1.10 | Strip prices hold; Egypt gas repricing expands; Suriname on schedule | $48.37 | 14.80% |
| Super bull | 10% | 12.0% | 1.25 | Sustained high oil + GranMorgu upside + exploration success (Alaska/Uruguay) | $67.43 | 19.32% |

- **Probability-weighted: IV@15% $32.80 (−33.3% vs price), IV@12% $43.09 (−12.4%), IV@10% $54.52, weighted IRR 10.82%, base-case IRR 11.52%**
- **Tier by numbers: C.** Diagnostics (dcf_numbers.json): OE yield 9.66%, terminal value 17.7% of IV@15%, scenario spread 5.43x, net debt 2.33x normalized OE (4.7x on the preliminary zero-capex basis — see HIGH_NET_DEBT), 9.5 months since FY end.

## Flags — every fragility flag resolved
- **DATA_GAP:capex** (preliminary run): resolved by the filing-sourced capex_override — see OVERRIDES. Never scored on gapped data.
- **STALE_FY** (FY ended 9.5 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, legs quoted above. ttm.py only ran once the SBC estimate override was in place (APA presents no SBC line in its 10-Qs).
- **BASE_DIVERGENCE** (latest FY $4.73 vs 3-yr median $2.35): the median is the distorted one for the base decision — its middle year is FY2024, the Callon stub/trough year, on a smaller pre-acquisition share count's economics. The TTM base ($4.75) sits on the current asset base with a flat OCF leg; the median is retained as the method-range floor.
- **NI_OCF_DIVERGENCE** (2024, 2025): explained from the filed history — it is the non-cash depletion load of an E&P, not a one-off trick. FY2025: net income $1,434M vs OCF $4,545M with D&A of $2,304M (financials_history.csv). FY2024: net income $804M vs OCF $3,620M with D&A of $2,266M, plus $796M of North Sea proved-property impairments recorded in 2024 (FY2025 10-K, filing text). The OCF-based conservative OE used throughout is not contaminated by either.
- **OE_VOLATILE** (OE/share spans >3x over 5 years): real and structural — commodity cyclicality. Handled by bear-weighted probabilities (45% on bear-or-worse), widened bear multipliers, and growth starts rebuilt from production guidance instead of the OE CAGR.
- **OVERRIDE_APPLIED:capex**: see OVERRIDES — gap, decision, per-year truth and measured impact are all recorded in fields (judgment.json, dcf_numbers.json overrides_applied/override_impact, overrides_registry.json).
- **HIGH_NET_DEBT** (preliminary basis: net debt 4.7x normalized OE): on the final run the diagnostic is 2.33x normalized OE (dcf_numbers.json), with net debt $3,977M against equity $6,093M. Still a levered E&P: the super-bear case applies a 0.50 OE multiplier to the base, and debt service against a halved OE is why the bear multipliers are widened. Mitigants as filed/reported: no maturities until 2029 (search result), deleveraging toward a $3B net-debt target (search result).
- **WIDE_SCENARIO_SPREAD** (5.43x): real — this is a commodity derivative on a $4.75 base, in a business whose override-filled OE/share history (financials_history.csv) spans −$3.70 (2020) to $5.57 (2022). Confidence is low, and the verdict is sized to the bear end.
- **TIER_BAND** (bear tier D at 7.54% vs bull tier C at 14.80%): the verdict spans tiers; any position sizing should use the bear end. Final tier is left at the weighted C (no tier_override) because the TTM base already carries a conservative capex leg — but see the method range below.
- **Revenue not filed under any engine-read tag** (no flag emitted; noted here because it shapes the run): revenue and gross margin are null in financials_history.csv and fundamentals.json for every year — APA reports revenue under a filer extension concept companyfacts does not expose to the engine's candidate list. Growth inputs therefore could not use any revenue CAGR and were rebuilt from production guidance and OE evidence, as documented in the recalibration above.

## My thoughts / overlay
- The honest headline is the *range* across defensible methods: TTM base with recalibrated scenarios → Tier C, weighted IRR 10.82%, IV@15% $32.80; the same scenarios on the normalized median base ($2.35/share) → Tier D, weighted IRR 6.61%, IV@15% $16.26 (engine run this session, same inputs except the base pin). The zero-capex counterfactual in key_numbers.md (base OE/share $12.49, weighted IRR 17.55% even under this run's bear-weighted scenarios) shows what the data gate + override exist to kill: scored on zero capex, this depleting-asset E&P would print as a comfortable clearer of the 15% hurdle. Every defensible method puts IV@15% well below the $49.18 price.
- What the price is paying for: strip oil prices holding, the gas-trading windfall repeating, and GranMorgu arriving on time in 2028. Those are real assets — GranMorgu's carry (TotalEnergies funds 87.5% of the first $10B gross) is genuinely shareholder-friendly — but they are commodity and execution bets, not owner's-earnings compounding.
- The balance sheet is moving the right way (net debt $5,419M at FY2024 → $3,977M at FY2025, per financials_history.csv) and capital discipline is real (2026 upstream capital guided ~$2.07B vs $2,740M in FY2025). At a lower price this is a reasonable cyclical cash machine; at $49.18 the buyer is underwriting the top half of the scenario table.
- Hurdle-clearing prices (dcf_numbers.json hurdle_prices): clears 15% at ≤$32.80, 20% at ≤$23.49, 25% at ≤$18.31 — on the TTM base. On the median base the 15% hurdle price is $16.26.

## Final verdict
- **Final tier: C** (weighted IRR 10.82% on the TTM base; method range C→D, bear case D — size any position to the bear end)
- Confidence: **Low** (WIDE_SCENARIO_SPREAD 5.43x, TIER_BAND spanning D–C, commodity-price-dependent base, two judgment overrides — one filing, one estimate — in the build)
- One-liner: Commodity E&P, moat 3/10 — no pricing power and cycle-set returns; on the TTM base ($4.75/share) the weighted IRR is 10.8% with IV@15% $32.80 vs the $49.18 price, so it does not clear the 15% hurdle (clears only below ~$32.80), and the method range runs down to Tier D on the median base — size to the bear end.

## Engine 5.5 re-score (2026-10-19)
Engine 5.5.0 run, 2026-10-19, under Andrew's ruling 4 (additive E&P capex). The single-value `capex_override` was deleted from judgment.json before the run, and APA is re-scored with no capex override. `sbc_override` is kept because it feeds ttm.py's SBC legs (see Overrides now). The 2026-10-16 text above is the dated record of the 5.4 score and is left as written. Where it disagrees with this section, this section is current. Figures below come from the final run's key_numbers.md, ttm.json and dcf_numbers.json. Old figures are the pre-5.5 score's. Figures from the FY2025 10-K and Q2 2026 10-Q statements are marked as filing text with their accession numbers. Research figures are marked as search results.

| | Pre-5.5 (2026-10-16, engine 5.4.0) | Engine 5.5.0 (2026-10-19) |
|---|---|---|
| Base OE/share | $4.7486 (TTM pin; capex legs filled by the single-value override) | $5.67 (source: ttm_json; filed capex legs) |
| Weighted IRR | 10.82% | 12.45% |
| Tier (numbers / final) | C / C | C / C |

Price $49.14 (nasdaq_quote_api). Market cap (est) $17.643B (basis: diluted_latest; price × shares). Scope: in scope (market cap under $40B). Net debt (latest) $3.977B.

### What engine 5.5 changed for this filer
- **Capex tags (ruling 4, additive components).** APA files no PP&E roll-up (`PaymentsToAcquirePropertyPlantAndEquipment`). It tags its capital spending as the E&P component `PaymentsToExploreAndDevelopOilAndGasProperties`, which 5.4 did not read. That is why the 5.4 run gapped and needed the override. When no roll-up is filed, 5.5 sums the filed components. key_numbers.md prints this capex basis:
  - FY2023: $2.313B
  - FY2024: $2.851B
  - FY2025: $2.740B

  Each year comes from PaymentsToExploreAndDevelopOilAndGasProperties alone (the PP&E leg, intangibles $0.00, `capex_source` `components`). These are the same three per-year figures the deleted override's source quoted from the FY2025 10-K MD&A. So the override would fill nothing, and `overrides_applied` is now empty. `used_tags.capex_components` also names `PaymentsToAcquireOilAndGasProperty` (leasehold acquisitions). In `capex_provenance` that tag is filed only for the FY2019–FY2021 history rows, not for FY2023–25.
- **What the change fixes.** The 5.4 run put one value into every year, so the OE history before 2023 was a fill artefact. The 2026-10-16 text says so. Every CSV year now carries its own filed capex. The 3-year median now sits on the FY2023 filed row (normalized OE/share $2.37) instead of the FY2024 fill year. The latest FY OE/share is unchanged at $4.73, because FY2025 was the override's exact year.
- **TTM legs.** ttm.py reads the same component in the 10-Qs (ttm.json):
  - OCF: FY $4,545,000,000 − prior YTD $2,277,000,000 + current YTD $2,260,000,000 = **TTM $4,528,000,000**. Unchanged.
  - Capex: FY $2,740,000,000 − prior YTD $1,437,000,000 + current YTD $1,111,000,000 = **TTM $2,414,000,000**. Every leg is tagged PaymentsToExploreAndDevelopOilAndGasProperties. No leg is an override, and `capex_override_superseded_legs` is empty. The two YTD legs are the H1 2025 and H1 2026 additions that the 2026-10-16 section quoted from the Q2 2026 10-Q cash-flow statement, as its caveat that the override-filled TTM capex was conservative. The filed series now carries them.
  - SBC: FY $107,000,000 (`AllocatedShareBasedCompensationExpense`). Both YTD legs are filled by the sbc_override, prorated by days, and they cancel: **TTM $107,000,000**.
  - Shares: 354,000,000, the current-YTD weighted diluted count.
  - Result: **TTM OE total $2,007,000,000 → base OE/share $5.67.**
- **SBC tag.** No SBC value moved. `sbc_provenance` finds both SBC tags only in FY2019–FY2022. In those years `ShareBasedCompensation` ≥ Allocated (note `share_ge_allocated`), so nothing was reconciled. FY2023–25 file only `AllocatedShareBasedCompensationExpense`, which the CSV already used. `used_tags.sbc` now names that tag, the one the latest year used, where the 5.4 record named `ShareBasedCompensation`.
- **Share basis.** No change. The `share_scale` tests (a) and (b) are both false: the latest diluted count is 359,000,000 against a cover-page count of 350,351,510 (2026-07-31). No split fact is filed (`share_basis` is empty).
- **Market cap.** $17.643B on `diluted_latest`, price × shares. APA is not an ADS filer, so ruling 1 changes nothing here.
- **USD-override branch.** Not engaged. APA reports in USD (`fx_conversion` null), the sbc_override's `currency_basis` is `no_fx`, and no override carries `currency`.

### Flags: every new 5.5 flag, by name
None of the 5.5 flags fired on the final run. Each one was checked:
- **SHARE_SCALE_SUSPECT / DATA_GAP:shares — SHARE_SCALE.** Not raised. The $5.67 base is far below 20× the $49.14 price, and the cover-page count agrees with the diluted count (above).
- **SHARE_BASIS_ADJUSTED / SHARE_BASIS_DIVERGENCE.** Not raised. No split ratio is filed, and the cover-page count is within 25% of the latest diluted count. APA bought back shares in Q3 2026 (search result: APA's Q3 2026 supplemental 8-K, sec.gov accession 0001841666-26-000058). A falling count makes the diluted-count cap conservative, not optimistic.
- **CAPEX_COVERAGE_LOW.** Not raised: capex is above D&A in each of FY2023–25 (financials_history.csv `da` column).
  - Investing-section check: 5.5 reads the "Additions to oil and gas property" line in full.
  - Not summed: the cash-flow statement's separate "Leasehold and property acquisitions" line. It is a ruling-4 component the engine missed, not spend outside capex. Ruling 4 sums oil-and-gas property acquisition (`PaymentsToAcquireOilAndGasProperty`), and `capex_provenance` sums that tag in the FY2019–21 rows ($40M / $4M / $9M). From FY2023 APA tags the line under its own extension concept, `apa:PaymentsToAcquireOilAndGasPropertiesUnprovedLeasehold`. EDGAR companyfacts carries only standard-taxonomy facts, so the engine cannot read it.
  - Filed amounts (filing text): $26M FY2025, $60M FY2024 and $20M FY2023 (FY2025 10-K, accession 0001841666-26-000015, Statement of Consolidated Cash Flows); $20M H1 2025 and $6M H1 2026 (Q2 2026 10-Q, accession 0001841666-26-000053, same statement). FY2023 also prints a $24M "Acquisition of Delaware Basin properties" line on another extension concept.
  - Effect: the TTM leg would be $26M − $20M + $6M = $12M, about $0.03 per share on 354,000,000 shares. FY2025 alone is about $0.07 per share on 359,000,000. Counting it would lower the base slightly and does not move the tier. A capex_override cannot add it, because the PP&E leg is filed for every year and an override never replaces a filed value. It is a method limit, not a worker error.
  - statements.json carries no capex line for APA (see Data), so this cross-check rests on `capex_provenance` and the 10-K / 10-Q figures quoted above.
- **SBC_TAG_RECONCILED.** Not raised (see SBC tag above).
- **OVERRIDE_SUPERSEDED_BY_FILED_TAG:capex.** Not raised. The `capex_override` was deleted before the run under ruling 4. The filed per-year values are the override's own source figures, so it would have filled nothing.
- **DATA_GAP:capex and OVERRIDE_APPLIED:capex.** Both were on the 5.4 record and both are gone: `data_gap` and `overrides_applied` are empty. make_score therefore sees no applied override, and score.json no longer carries the "tier exists only because of a judgment override" exit-alert suppression (`exit_alert_eligible` is true). The TTM base still depends on the `sbc_override`, which make_score does not see (see Overrides now). That rule question is escalated to Andrew.

### Flags carried from 5.4 (final run)
- **STALE_FY** (9.6 months since FY end). Resolved by the TTM pin from ttm.py through Q2 2026 (legs above). Q3 2026 results are not yet filed; the call is scheduled for Nov 5 (search result: APA's Q3 2026 supplemental release).
- **BASE_DIVERGENCE** (latest FY $4.73 vs 3-year median $2.37). Neither figure is a clean run-rate, and the TTM base used is lifted as well. The income-statement and cash-flow lines below are filing text from the FY2025 10-K (accession 0001841666-26-000015) and the Q2 2026 10-Q (accession 0001841666-26-000053). TTM figures use the ttm.py construction, FY2025 − H1 2025 + H1 2026.
  - **The median (FY2023 row, $2.37).** It predates the all-stock Callon acquisition, which closed in 2024. FY2024 sits below it ($2.04 in financials_history.csv): it holds a partial Callon year and the highest capex of the three, $2.851B.
  - **The latest FY ($4.73).** Two operating lines lift it against FY2023. The first is the net margin on purchased oil and gas (purchased oil and gas revenue less purchased oil and gas costs, Statement of Consolidated Operations): $1,691M − $1,070M = $621M in FY2025, against $894M − $742M = $152M in FY2023. The second is the Receivables line of the cash-flow statement: an $850M inflow in FY2025, against a $157M outflow in FY2023. A $365M accounts-payable outflow offsets part of the FY2025 inflow (statements.json `change_payables`; see NI_OCF_DIVERGENCE).
  - **The TTM base ($5.67).** TTM OE is $2,007,000,000, against $1,698,000,000 for FY2025. The OCF leg is flat ($4,528,000,000 vs $4,545,000,000), so the capex leg ($2,414,000,000 vs $2,740,000,000) accounts for the difference.
  - **Inside the flat OCF leg, the purchased-gas margin rose.** H1 2026: $721M − (−$47M) = $768M (the cost line reads as net proceeds of $47M). H1 2025: $1,057M − $778M = $279M. The TTM margin is therefore $621M − $279M + $768M = $1,110M, which is $489M above FY2025. The Receivables line adds $850M − $433M + (−$147M) = $270M to TTM OCF. The purchased-gas margin is an income-statement figure (accrual, pre-tax), so its effect on OCF is approximate; the Receivables line is a cash-flow figure.
  - **The capex leg.** H1 2026 additions to upstream oil and gas property were $1,111M, against $1,437M in H1 2025. 2026 upstream capital is guided below FY2025 (2026-10-16 text, search result), so much of the decline is the guided program. The part that is Suriname Block 58 exploration timing is not quantified in the filings or in this run's outputs.
  - **What it does to the tier.** Taking the $489M purchased-gas excess out of TTM OE leaves $2,007M − $489M = $1,518M, or $4.29 per share on 354,000,000 shares. That is below the FY2025 OE/share ($4.73) and below the pre-5.5 TTM base ($4.7486, scored 10.82%, Tier C). On this run's scenarios it sits at the C/D boundary. That IRR is not printed in this run's outputs, so it is escalated rather than quoted. The same window carries a further lift (the $270M Receivables inflow, and any Suriname timing in the capex leg) and a drag (H1 2026 Accounts payable −$123M and Accrued expenses −$50M). None of these is netted here.

  Resolution: the TTM base is kept as the method's STALE_FY base, and the tier stays at the numbers tier, C. That C holds only while the H1 2026 purchased-gas margin counts in full as earnings: removing its $489M excess over FY2025 alone takes the base to the C/D boundary. This cannot be settled within a worker's bounded authority. A `base_override` may use only this run's printed figures, and these normalizations need filing figures; a tier_override is outside this pass's authority. The choice between C and a final tier of D is therefore escalated to Andrew. Until he rules, any position is sized to the bear end (D, 8.57%), and the median stays as the method-range floor.
- **NI_OCF_DIVERGENCE** (2024, 2025). The inputs are unchanged: 5.5 moved only the capex columns of financials_history.csv. The 2026-10-16 resolution holds for FY2024 but is incomplete for FY2025. Working-capital lines below are from statements.json (`change_receivables`, `change_payables`, tagged IncreaseDecreaseInAccountsReceivable and IncreaseDecreaseInAccountsPayable).
  - **FY2024.** The gap is the depletion load of an E&P: net income $804M against OCF $3,620M, with D&A of $2,266M (financials_history.csv). On top of that come the $796M of 2024 North Sea impairments (filing text, quoted in the 2026-10-16 section). The working-capital lines are small: a $104M receivables outflow and an $81M accounts-payable inflow. FY2024 OCF carries no working-capital one-off.
  - **FY2025.** Depletion is still most of the gap: net income $1,434M against OCF $4,545M, with D&A of $2,304M (financials_history.csv). It is not the only cause. `change_receivables` reads −$850,000,000 for FY2025, an $850M receivables release, which is a cash inflow inside OCF. A $365M accounts-payable outflow offsets part of it, so the two lines net to a $485M working-capital inflow. That inflow lifts FY2025 OCF, and with it the latest FY OE ($1.698B, $4.73/share).
  - The 2026-10-16 sentence that the OCF-based OE "is not contaminated" is therefore true of depletion and the impairments, but not of FY2025's working capital. The $4.73 latest FY figure is not a clean run-rate. See BASE_DIVERGENCE above, which carries the receivables line into the base and tier discussion. The same line adds $270M to the TTM window.
- **OE_VOLATILE.** Still real. The flag reads the last five fiscal years, FY2021–25. Their OE/share in financials_history.csv (`oe_per_share`, on filed capex) is $5.90 / $8.48 / $2.37 / $2.04 / $4.73. The FY2022 peak of $8.48 is more than four times the FY2024 trough of $2.04. It also sits above the $4.73 latest FY, so the latest year is not the top of the range. The FY2019–20 rows, outside the window, are lower still ($0.25 / $0.18). Bear-weighted probabilities and widened bear multipliers are kept.
- **WIDE_SCENARIO_SPREAD** (5.43x). Real: this is a commodity derivative. Confidence stays low.
- **TIER_BAND** (bear 8.57%, tier D → bull 17.14%, tier B). The band now reaches B, but only in the bull case. The weighted IRR is C, and any position is sized to the bear end, which is D.
- **HIGH_NET_DEBT.** It fired on the preliminary run (engine defaults, median base) and not on the final run. On the TTM base, net debt / normalized OE is 1.95x, with net debt of $3.977B. Management targets lower net debt and repaid near-term bonds in H1 2026 (search result: Q2 2026 release).

### DCF: final run (judgment inputs unchanged from 2026-10-16)
Final command: `--moat 3 --probs 0.15,0.3,0.3,0.15,0.1 --offsets -0.5,-0.42,-0.35,-0.29,-0.23 --mults 0.5,0.75,1.0,1.1,1.25 --ttm`.

Why the growth inputs are kept:
- The growth blend is 41.27% → g_base 35.00%. It is still a single OE/share CAGR 2y (41.27%), because no revenue component exists: revenue is filed only under an extension concept.
- It is now computed on filed capex instead of the fill. It still measures a commodity-driven recovery from the FY2023 row, not volume growth. U.S. oil guidance is 123,000 bbl/d on unchanged $1.3B U.S. capital (search result: Q2 2026 release).
- The same offsets therefore give the same starts: −10.0% (the engine's super-bear floor) / −7.0% / 0.0% / +6.0% / +12.0%. Every start sits far below the blend, for the reason written in the 2026-10-16 recalibration.
- The bear multipliers stay widened at 0.5 / 0.75. The filed history still shows trough OE as a small fraction of the latest year.

Moat 3/10 · CAP 5.9 yrs · terminal growth 2.50%.

| Scenario | Prob | Growth start | OE mult | IV@15 | IV@12 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | -10.0% | 0.5 | $14.84 | $19.08 | 5.98% |
| Bear | 30% | -7.0% | 0.75 | $24.84 | $32.13 | 8.57% |
| Base | 30% | 0.0% | 1.0 | $42.58 | $55.78 | 13.30% |
| Bull | 15% | 6.0% | 1.1 | $57.75 | $76.42 | 17.14% |
| Super bull | 10% | 12.0% | 1.25 | $80.51 | $107.50 | 22.36% |

- **Probability-weighted:** IV@15% $39.16 (−20.3% vs price), IV@12% $51.45 (+4.7%), IV@10% $65.09. Weighted IRR 12.45%, base-case IRR 13.30%. Scenario range 5.98% – 22.36%.
- **Hurdle-clearing prices (weighted path):** 15% at $39.16 · 20% at $28.04 · 25% at $21.86.
- **Diagnostics:** OE yield 11.54% · TV share @15% 17.7% · scenario spread 5.43x · net debt / normalized OE 1.95x · OE-positive years (last 5) 5/5.

### Overrides now
- **`capex_override`: deleted** (ruling 4). APA has no capex override and no capex entry in `_system/overrides_registry.json`: make_score replaced APA's entries wholesale, and none remain.
- **`sbc_override` {value 107000000, kind "estimate"}: kept. Rule question escalated to Andrew.**
  - The engine applies nothing from it. `override_checks.sbc` records a last filed value of $107,000,000 USD, not out of band (1.0× its named anchor), with `currency_basis` `no_fx`. SBC is filed for every annual period, so the engine fills nothing with it. `overrides_applied` is empty, and make_score writes no registry entry, because it records only overrides the engine applies.
  - It still carries the tier. APA's 10-Q cash-flow statements present no SBC line, so without it ttm.py exits ("sbc: no post-FY YTD fact") and no TTM base exists. It fills ttm.py's two YTD SBC legs ($53,060,273.97 each, prorated by days; ttm.json `overrides_used`). The two legs cancel, so TTM SBC equals the filed $107,000,000. The $5.67 base, and with it the Tier C, exists only because of this override. Without a TTM base the score falls back to the 3-year median, $2.37 under 5.5. This run's outputs do not price that median. The 2026-10-16 record priced its own $2.35 median at 6.61% (Tier D), with the same moat, probabilities, offsets and multipliers.
  - AGENTS.md requires `overrides_applied` to list the same keys as judgment.json, and every override to appear in the registry with its measured impact. Neither holds here. The README's Engine 5.5 entry says make_score does not refuse this override, but AGENTS.md has no exemption for an override that fills only ttm.py legs. Andrew must rule between a registry event for such overrides (a make_score change) and an exemption written into AGENTS.md and the specs.
  - Correction to the dated record: the 2026-10-16 text says both overrides were in the registry, but origin/main's registry held only the capex entry for APA.
  - Risk: APA's Q3 2026 supplemental reports a stock-based compensation charge in Q3 G&A that is large against the FY2025 annual figure, mostly share-price mark-to-market (search result). If that pace held across the TTM window, the TTM SBC leg at the FY2025 rate would understate SBC, and the base would be high by the excess spread over 354,000,000 shares. This is not computed here. It is one more reason to size to the bear end.

### Minority interest (method limit)
Consolidated OCF includes the Egypt noncontrolling interest's share; APA's adjusted production excludes Egypt noncontrolling-interest and tax barrels (2026-10-16 text). The engine cannot split owner's earnings between APA's shareholders and the noncontrolling partner. The base is therefore consolidated and overstates what APA's holders own by that share. The run's outputs do not split it. The filing gives its size: net income attributable to noncontrolling interest was $258M of $1,692M consolidated net income in FY2025, about 15%, and distributions to the noncontrolling interest were $430M (FY2025 10-K, Statements of Consolidated Operations and Cash Flows). That share of net income is a proxy, not an OE split. It is a method limit, not a worker error.

### Why the tier is C
- The weighted IRR of 12.45% sits in the 10–15% band. Tier by numbers C = final tier C, with no tier override.
- The move from 10.82% comes from the filed capex legs. The TTM capex leg is now $2,414,000,000 of tagged additions instead of a fill at the $2.740B FY2025 rate, which lifts the base from $4.7486 to $5.67 per share.
- The price of $49.14 is above the 15% hurdle price of $39.16, so APA does not clear the hurdle. It clears 15% only below $39.16.
- The band runs from bear D (8.57%) to bull B (17.14%), and the position is sized to D.
- The method-range floor (the same scenarios on the $2.37 normalized median) was not re-run under 5.5, so this run's outputs do not price it. That base is under half the $5.67 TTM pin. The 2026-10-16 record priced its $2.35 median at 6.61% (Tier D) on the same moat, probabilities, offsets and multipliers.
- Confidence is **low**, for these reasons:
  - WIDE_SCENARIO_SPREAD 5.43x.
  - A TIER_BAND from D to B.
  - A commodity-price base.
  - A TTM base lifted by a purchased-gas margin $489M above FY2025's. Removing that excess alone takes the base to the C/D boundary (see BASE_DIVERGENCE; escalated).
  - SBC YTD legs filled by an estimate.
- APA is not Tier S/A, so no entry alert applies. The score is now on engine 5.5.0 output.

### Data and enrichment (2026-10-19)
All six enrichment scripts ran without failure, in order: fundamentals.py, prices.py, segments.py, statements.py, profile.py, reprice.py.
- fundamentals.json was rewritten: its price-dependent block is now priced. Its buyback yield reads 0.00%, marked `bound` "exact" with the basis "never filed in any period — zero by the filer's own statements", and its `warnings` list is empty. That zero is a reader gap, not a filed zero:
  - The filer prints "Treasury stock activity, net" of $280M in FY2025 and $100M in H1 2026 (cash-flow statements, FY2025 10-K and Q2 2026 10-Q), tagged under an APA extension concept.
  - The us-gaap `TreasuryStockValueAcquiredCostMethod` is filed at $283M for FY2025 (EDGAR companyfacts). fundamentals.py reads only `PaymentsForRepurchaseOfCommonStock`.
  - The page's buyback and shareholder yields are therefore understated. This is a display gap, not a valuation input. The fundamentals.py fix is a code follow-up outside this folder.
- statements.json, segments.json and profile.json were unchanged in content (stable writes). street.json and live.json were refreshed; reprice found no split since scoring.
- Neither fundamentals.json nor statements.json carries a capex line for APA, because their capex readers do not use the 5.5 E&P component tags. The page's FCF and OE fields from those files are therefore blank for APA. This affects display only: the valuation's capex is the engine's (`capex_provenance`, key_numbers.md capex basis).
- Research used:
  - APA's Q3 2026 supplemental information, 8-K filed 2026-10-07: https://www.sec.gov/Archives/edgar/data/0001841666/000184166626000058/a3q26supplementalguide-ear.htm
  - APA's Q2 2026 results release: https://investor.apacorp.com/news-releases/news-release-details/apa-corporation-announces-second-quarter-2026-financial-and
  - Coverage of the Q3 call date: https://finviz.com/news/400071/apa-corporation-provides-third-quarter-2026-supplemental-information-and-schedules-results-conference-call-for-nov-5-at-10-am-central-time

### Final verdict (supersedes the 2026-10-16 verdict above)
- **Final tier: C.** Weighted IRR 12.45% on the TTM base of $5.67/share, with no capex override ("override-free" in the one-liner below means that; the SBC YTD legs still use the estimate override). The band runs from bear D (8.57%) to bull B (17.14%); size any position to the bear end.
- The C rests on the TTM base. Removing its $489M purchased-gas margin excess over FY2025 alone takes the base to the C/D boundary, so the call between C and D is with Andrew (see BASE_DIVERGENCE).
- Confidence: **Low.**
- One-liner (judgment.json, verbatim): Commodity E&P, moat 3/10 — no pricing power and cycle-set returns; on the override-free TTM base ($5.67/share, filed E&P capex now read by engine 5.5) the weighted IRR is 12.45% with IV@15% $39.16 vs the $49.14 price, so it does not clear the 15% hurdle (clears only below ~$39.16); band D (8.57%) to B (17.14%) — size to the bear end.
