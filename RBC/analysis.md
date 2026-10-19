# RBC — RBC Bearings Incorporated
Engine 5.4.0 run, 2026-10-16. In scope (market cap $15.77B at $498.52, nasdaq_quote_api). All figures below are copied from dcf_numbers.json, ttm.json, fundamentals.json or financials_history.csv — none are recomputed.

## What it is
Manufacturer of highly engineered precision bearings, components and essential systems (SIC 3562, Ball & Roller Bearings) for industrial, aerospace and defense markets. Two segments: Industrial (~57% of Q1 FY2027 sales) and Aerospace & Defense (~43%). The current company is substantially acquisition-built: Dodge (closed 2021) more than doubled the revenue base, Specline followed in 2023, and VACCO Industries (engineered valves, regulators and manifolds for defense/space) was acquired in July 2025 for ~$275M and contributed $34.4M of Q1 FY2027 sales. Fiscal year ends late March; latest filings are the FY2026 10-K (period ended 2026-03-28, filed 2026-05-15) and the Q1 FY2027 10-Q (period ended 2026-06-27, filed 2026-07-31).

## Owner's earnings
**FY2026 (10-K via EDGAR, from financials_history.csv):** operating cash flow $415,700,000; SBC $34,500,000 (always a real cost); capex $73,100,000 — by override (see OVERRIDE; FY2026 is the override's own filing year, so this leg is the exact filed figure).
- **Conservative owner's earnings FY2026: $308,100,000 = $9.74/share** (dcf_numbers.json base_oe_latest_per_share).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $432,200,000 — above the conservative figure, because D&A of $128,800,000 runs well ahead of capex and working capital released cash in FY2026; the OCF-based conservative figure is the one used.
- OE positive 5 of the last 5 fiscal years. Net debt $818,200,000 (LongTermDebtNoncurrent + LongTermDebtCurrent basis, dcf_numbers.json), plus lease liabilities $69,700,000.
- Share count dilutes, it does not shrink: diluted shares rose from 24,716,213 (FY2019) to 31,634,888 (FY2026), a share-count CAGR of +2.87%/yr in the engine blend — acquisition issuance, already charged against the revenue components of blended growth.

**Base used = TTM owner's earnings through Q1 FY2027, from ttm.py (filing-direct, no hand math):**
- OCF: FY $415,700,000 − prior YTD $120,000,000 + current YTD $171,800,000 = **TTM $467,500,000**
- Capex: **TTM $72,899,726**, all three legs filled by the override, prorated by days (FY leg $72,899,726 over 364 days; both YTD legs $18,224,932 over 91 days; they cancel in the TTM math)
- SBC: FY $34,500,000 − prior YTD $6,600,000 + current YTD $6,700,000 = **TTM $34,600,000**
- Shares (current-YTD weighted diluted): **31,714,686**
- **TTM OE total $360,000,274 → base OE/share $11.35** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $6.33/share — rejected as the binding base: two of its three years are depressed by the override's flat capex (see BASE_DIVERGENCE) and all three predate a genuine operating-cash-flow step-up (filed OCF: FY2024 $274.7M → FY2025 $293.6M → FY2026 $415.7M → TTM $467.5M). The median run is retained below as the method-range low end.

## OVERRIDE — capex (filing, bounded authority step 8a)
- **The gap:** the preliminary engine run exited 4 with `DATA_GAP:capex` — no tier emitted. RBC Bearings reports capital expenditures only under `PaymentsForCapitalImprovements` from FY2024 onward, a tag the engine does not read; the tag it does read (`PaymentsToAcquirePropertyPlantAndEquipment`) stops after FY2023 ($42.0M). Capex was missing for FY2024, FY2025 and FY2026 (dcf_numbers.json data_gap: ["capex"]).
- **The decision:** judgment.json carries `capex_override = {value: 73100000, kind: "filing", source: "Form 10-K for fiscal year ended March 28, 2026 (filed 2026-05-15), Consolidated Statements of Cash Flows, investing line 'Capital expenditures' tagged us-gaap:PaymentsForCapitalImprovements: $73.1M for FY2026, with $49.8M for FY2025 and $33.2M for FY2024 in the same statement; corroborated in EDGAR companyfacts under PaymentsForCapitalImprovements with identical values"}`. Sanity band: $73.1M vs the last engine-filed capex value of $42.0M — inside the 0.1×–10× band (override_checks out_of_band: false).
- **Distortions, disclosed:** an override is a single value applied to every missing period. Against the same statement's true per-year values it overstates FY2024 capex by $39.9M (true $33.2M) and FY2025 by $23.3M (true $49.8M), understating those years' OE/share in financials_history.csv ($6.31 and $6.33 as printed) — a conservative direction for the median base, and one reason the median is not the binding base. In the TTM the same value understates the true filed-leg TTM capex (FY2026 $73.1M − Q1 FY2026 $15.7M + Q1 FY2027 $24.9M under the same tag in the 10-Qs) by $9.2M, ~2.6% of TTM OE — anti-conservative but small, and stated here rather than hidden.
- **Measured impact (key_numbers.md, on the TTM base actually used, final configuration with the override toggled off):** base OE/share $13.65 zero-fill → $11.35 with the override (−16.84%); weighted IRR 7.47% → 6.69% (−0.79pp). On the engine-native median basis (dcf_numbers.json override_impact) the same override moves the median base $8.81 → $6.33. Its other effect is binary: unblocks_tier is true — without it there is no tier at all.
- Recorded in score.json and in _system/overrides_registry.json by make_score.py.

## Moat: 6/10 — moderate-strong, narrow
Justification: mission-critical, highly engineered precision bearings and components designed into aerospace/defense and industrial platforms, where requalifying a substitute supplier is slow and costly, giving sole/primary-source stickiness and proven pricing power — capped at 6 because measured returns on capital have not yet re-earned a wide-moat grade.
- **Evidence first (fundamentals.json):** gross margin 37.9% (FY2022) → 41.2% (FY2023) → 43.0% (FY2024) → 44.4% (FY2025) → 44.4% (FY2026), 45.2% TTM, and the Q1 FY2027 release reports 47.7% — sustained expansion, i.e. real pricing power / favorable mix. ROIC proxy (after-tax operating income over equity + debt − cash): 11.2% / 11.8% (FY2019/20, pre-Dodge), 2.2% (FY2022, the Dodge balance-sheet year), then 6.0% → 7.1% → 7.5% → 7.8% (FY2023–26). The recovery trend is real but the level is still mid-to-high single digits — the Dodge acquisition loaded the capital base with goodwill and intangibles, so measured history understates the franchise's returns on tangible capital, yet not by enough to grade this 7+ today.
- FOR: designed-in, mission-critical bearings/components — requalifying a substitute on an aerospace or defense platform is slow and costly; proven pricing power (gross-margin record above); sole/primary-source positions and a $2.3B backlog at Q1 FY2027 across commercial aero, defense and space programs; proprietary plain-bearing / engineered-component know-how built over decades, in fragmented niches.
- AGAINST: measured ROIC proxy only 6.0–7.8% FY2023–26 (above); larger diversified rivals (Timken, SKF, Schaeffler) and powerful, concentrated OEM customers (Boeing/Airbus/defense primes); cyclical end markets — commercial aero build rates, defense budgets and industrial capex all swing; growth has been substantially bought (Dodge 2021, Specline 2023, VACCO 2025), with true capex climbing ($33.2M FY2024 → $73.1M FY2026).
- A 6 gives CAP = 9.8 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 9.8 years, 15-year projection.

## DCF — engine 5.4.0 final run (2026-10-16)
Growth sanity check and recalibration (written reason): the engine's blended start is 13.68%, but its components mix bases — the 5-yr revenue CAGR of 18.75% straddles the Dodge acquisition (revenue $609M in FY2021 → $1,469M in FY2023 was mostly bought, not organic), and the OE/share CAGR of 24.32% rides the same step-change. The signals that describe the current business: 3-yr revenue CAGR 8.42%, FY2026 revenue +14.34% YoY, Q1 FY2027 revenue +19.2% YoY of which VACCO contributed $34.4M of the $519.5M total (underlying organic growth nearer the low teens), and management's Q2 FY2027 sales guidance of $505–515M implying +10.9–13.1% YoY. Scenario starts were therefore set via offsets (−0.14 / −0.08 / −0.02 / +0.03 / +0.10 vs the blend) to −0.3% / 5.7% / **11.7%** / 16.7% / 23.7%. The base start sits inside the company's own Q2 guidance range. The bull start (16.7%) is below the Q1 FY2027 total print (+19.2%) for a stated reason: that print includes VACCO's inorganic contribution, and bull assumes A&D strength plus a full VACCO year, not a repeat of acquisition-boosted prints. Probabilities 10/25/30/25/10; OE multipliers 0.75/0.90/1.00/1.10/1.25. Price $498.52.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | −0.3% | 0.75 | Aero destock + industrial recession; margins give back the FY26 step-up | $61.58 | 3.98% |
| Bear | 25% | 5.7% | 0.90 | A&D cools to mid-single digits; industrial flat | $96.51 | 5.02% |
| Base | 30% | 11.7% | 1.00 | Guidance-range growth decaying over the 9.8-yr CAP | $140.00 | 6.35% |
| Bull | 25% | 16.7% | 1.10 | A&D supercycle persists, VACCO synergies, industrial recovery | $192.12 | 7.87% |
| Super bull | 10% | 23.7% | 1.25 | Sustained aero/defense boom plus another value-creating deal cycle | $296.81 | 10.63% |

- **Probability-weighted: IV@15% $150.00 (−69.9% vs price), IV@12% $204.23, IV@10% $265.36, weighted IRR 6.69%, base-case IRR 6.35%**
- **Tier by numbers: D** — and D in both the bear and bull cases (tier_bear D, tier_bull D); even the super-bull scenario IRR (10.63%) does not reach the 15% hurdle.
- Diagnostics (dcf_numbers.json): OE yield 2.28%, terminal value 21.3% of IV@15%, scenario spread 4.82x, net debt 2.28x normalized OE, 6.6 months since FY end.
- **Method range:** the preliminary override run on the engine-native median base ($6.33/share, default scenario inputs) printed weighted IRR 5.00% and Tier D; the final TTM-base run prints 6.69% and Tier D. With true per-year capex the median base would be higher than $6.33 but still well under the TTM figure, because filed OCF genuinely stepped up in FY2026. Every defensible method lands in Tier D — the range changes the depth, not the verdict.

## Flags — every fragility flag resolved
- **DATA_GAP:capex** (preliminary run): resolved by the filing override above (step 8a bounded authority); data_gap_uncovered is empty in the final run.
- **OVERRIDE_APPLIED:capex**: see OVERRIDE — gap, source, band check, both distortion directions and measured impact are recorded in judgment.json, dcf_numbers.json (overrides_applied / override_impact) and the registry, not just here.
- **BASE_DIVERGENCE** (latest FY OE/share $9.74 vs 3-yr median $6.33): both are distorted in opposite directions. The median is dragged down by the override's flat $73.1M capex in FY2024/25 (true filed capex was $33.2M / $49.8M) — with true per-year capex the median would be higher, though the computed outputs do not print that figure, so it is stated in words only. The latest FY is not a one-off spike: filed OCF rose FY2024 $274.7M → FY2025 $293.6M → FY2026 $415.7M and TTM OCF is $467.5M, i.e. the step-up persisted into Q1 FY2027 (Q1 OCF $171.8M vs $120.0M in the prior-year quarter, ttm.json legs). Resolution: TTM base ($11.35) is binding; the median run is kept as the method-range low end, and both methods tier D.
- **SHARES_FALLBACK** (no diluted count filed for 2021, 2022 — those history years use the basic/outstanding/dei count in the shares_tag column): noted — per-share history for FY2021/22 is approximate. It does not touch the base: the TTM denominator (31,714,686) and the latest FY count (31,634,888) are both filed diluted counts.
- **WIDE_SCENARIO_SPREAD** (super-bull IV 4.82x super-bear IV): real — the outcome range is wide because the starting OE yield is only 2.28% and the verdict rests on growth duration. Confidence is capped at medium, and the verdict is sized to the conservative end; note the spread does not straddle the hurdle — even the super-bull IRR (10.63%) is below 15%.
- **LOW_OE_YIELD** (raised on the median-base run at 1.3%; 2.28% on the TTM base): stands as a characterization — at $498.52 the buyer is paying ~44x TTM owner's earnings, so the valuation rests almost entirely on growth. That is exactly why the tier is D despite a genuinely strong current trajectory.
- **HIGH_NET_DEBT** (raised on the median-base run at 4.1x normalized OE; 2.28x on the TTM base): balance sheet stated from the filings — net debt $818,200,000 (debt on the LongTermDebtNoncurrent + LongTermDebtCurrent basis, cash $57,300,000 in financials_history.csv), plus lease liabilities $69,700,000. Leverage is being paid down fast out of the OCF step-up (Q1 FY2027 releases report $77M of debt repaid in the quarter and a further $50M after it, with management aiming to retire the remaining term loan by November 2026). ~2.3x TTM OE is serviceable, not fragile; the bear cases already stress it via the 0.75/0.90 OE multipliers.

## My thoughts / overlay
- Quality is not the debate: designed-in positions, gross margin expanding into the high 40s, backlog $2.3B, OCF up ~70% in two years on the filed history, and a balance sheet delevering quickly. If the A&D cycle holds, this business compounds for years.
- Price is the debate. $498.52 is ~44x TTM owner's earnings of $11.35/share. The DCF cannot get there from here: the weighted IV@15% is $150.00, the price at which the stock would clear Andrew's 15% hurdle is that same ~$150, and even the 10%-probability super-bull path (23.7% starting growth, 1.25x OE) values it at $296.81 — 40% below the market.
- Watch items: whether ROIC keeps climbing toward the pre-Dodge 11–12% as VACCO margins are lifted (management commentary points to VACCO margin gains over 18–24 months); whether capex keeps climbing faster than revenue (true capex more than doubled FY2024→FY2026); defense budget / missile-and-space order durability; and the next acquisition's price discipline, since the growth model depends on deals.
- Method honesty: the two judgment calls that matter are both disclosed and measured — the capex override (binary: no tier without it; conservative on the median, ~2.6% generous on the TTM) and the TTM pin over the median base. Neither flips the tier: D on every method tried.

## Final verdict
- **Final tier: D** (weighted IRR 6.69% on the TTM base; the preliminary median-base run at default inputs printed 5.00% — Tier D across the method range, and in both the bear and bull cases)
- Confidence: **Medium** (capped by WIDE_SCENARIO_SPREAD; high on the filing data and the override source, medium on any single growth path)
- One-liner: High-quality precision-bearings franchise, moat 6/10 — but at $498.52 the weighted IRR is only 6.7% (Tier D, IV@15% $150.00); it clears the 15% hurdle only near $150, about 70% below the current price.

## Engine 5.5 re-score (2026-10-19)
Engine release 5.5.0, run 2026-10-19 under Andrew's ruling 3 (the capital-improvements capex tag). The steps: `capex_override` deleted from judgment.json, `ttm.py` re-run, final engine pass, `make_score.py`, then enrichment. The text above is the dated 2026-10-16 record and is left as written. Where it disagrees with this section (the capex override, the base, the IRR, the flag list), this section supersedes it. Every figure below comes from the final run's key_numbers.md. The TTM legs are quoted from the final ttm.json and the run inputs from the final dcf_numbers.json. Old figures are the pre-5.5 ones.

**Old → new**

| | 2026-10-16 (engine 5.4.0) | 2026-10-19 (engine 5.5.0) |
|---|---|---|
| Base OE/share | $11.3512 (TTM pin, capex legs filled by the single-value $73.1M override) | $11.05 (source: ttm_json, every capex leg filed) |
| Weighted IRR | 6.69% | 6.58% (base-case 6.25%) |
| Tier (numbers / final) | D / D | D / D |
| IRR band | see the 2026-10-16 text above | bear 4.95% (tier D) → bull 7.74% (tier D) |
| Capex, last 3 FY | override $73.1M in each of FY2024, FY2025, FY2026 | filed: FY2024 $33.2M · FY2025 $49.8M · FY2026 $73.1M |

**What engine 5.5 changed for this filer**
- **Capex tag (decision 3).** `PaymentsForCapitalImprovements` is now on the capex component list in both `dcf_engine.py` and `ttm.py`. RBC files no PP&E roll-up for FY2024–26, so each year's capex is the sum of the filed components, and here there is one. key_numbers.md prints the basis line by line: FY2024 (2024-03-30) $33.2M, FY2025 (2025-03-29) $49.8M and FY2026 (2026-03-28) $73.1M, each "components: PaymentsForCapitalImprovements (PP&E … + intangibles $0.00)". FY2023 and earlier keep the roll-up tag `PaymentsToAcquirePropertyPlantAndEquipment` (CSV `capex_source` "rollup"). The zero-guard changes no RBC period because no $0 candidate is filed. RBC files no intangible purchases (intangibles $0.00 in each year), so the additive intangible leg (decision 5) adds nothing.
- **TTM legs (ttm.py, same helpers), from ttm.json.** Capex is now filed in all three legs under `PaymentsForCapitalImprovements`: FY $73,100,000 − prior YTD $15,700,000 + current YTD $24,900,000 = **TTM $82,300,000**. On 2026-10-16 the TTM capex was the override, prorated by days.
  - OCF: $415,700,000 − $120,000,000 + $171,800,000 = **$467,500,000**.
  - SBC: $34,500,000 − $6,600,000 + $6,700,000 = **$34,600,000**.
  - **TTM OE $350,600,000 over 31,714,686 diluted shares (current-YTD weighted average) = base OE/share $11.05.**
  - ttm.json carries no warnings and no `capex_override_superseded_legs`, because the override is gone.
- **SBC tag (decision 6): no change.** `ShareBasedCompensation` is the SBC tag for FY2024–26 and for every TTM leg. `SBC_TAG_RECONCILED` did not fire. In dcf_numbers.json `sbc_provenance`, every period listed (the years that file both `ShareBasedCompensation` and `AllocatedShareBasedCompensationExpense`, FY2026 among them) shows `reconciled: false` and `used: ShareBasedCompensation`. ttm.json `sbc_reconciled_legs` and `sbc_reconciliation_withdrawn_legs` are both empty.
- **Share basis (decision 2): no change.** In dcf_numbers.json `share_scale.defect` is false: test (a), base against 20× the price, and test (b), latest diluted count against the cover-page count, are both false. `share_basis` records no split fact and no divergence. So `SHARE_SCALE_SUSPECT`, `DATA_GAP:shares — SHARE_SCALE`, `SHARE_BASIS_ADJUSTED` and `SHARE_BASIS_DIVERGENCE` are all absent, and judgment.json declares no `share_class_mismatch`.
- **Market cap / ADS (decision 1): no change.** RBC is a 10-K filer with no ADS ratio. Market cap (est) $15.771B (basis: diluted_latest; price × shares), the same cap as on 2026-10-16. Scope: in scope (market cap under $40B), matching `in_scope_under_40b: true`.
- **USD-override branch (decision 7): not applicable.** RBC reports in USD, nothing is FX-converted, and no override remains.
- **Working capital in FY2026 (corrects the 2026-10-16 maintenance-OE sentence).** The 2026-10-16 text says working capital released cash in FY2026. It did not. In statements.json's FY2026 cash-flow statement, the change-in-receivables and change-in-inventory lines are both increases, which absorb cash. The CSV's negative FY2026 `delta_nwc`, and the maintenance OE above the conservative figure that the 2026-10-16 text quotes, come from the engine's working-capital formula instead:
  - The formula takes current debt out of current liabilities only when it is tagged `DebtCurrent`. RBC files its current debt as `LongTermDebtCurrent` (dcf_numbers.json `used_tags`: `debt_current` null, `debt_cur_ltd` LongTermDebtCurrent).
  - The current portion of the term loan rose sharply in FY2026 (CSV `debt_current`, the same LongTermDebtCurrent balance that net debt includes). Left inside current liabilities, that reclassification reads as a working-capital release, so the CSV's FY2026 maintenance OE is overstated.
  - The base and tier are unaffected: the engine prices conservative OE (OCF − capex − SBC; latest FY OE total $308.1M). The fix belongs in the engine (take the combined current debt out of current liabilities in the NWC formula) and needs a separate code PR with a test. It is escalated, not changed here.

**New 5.5 flags, resolved by name**
- **OVERRIDE_SUPERSEDED_BY_FILED_TAG:capex.** Raised on the preliminary run, made with the old judgment.json that still declared the $73.1M `capex_override`. The engine now reads the filed FY2024 capital-improvements figure of $33.2M, which is outside 0.5×–2× of the override, so the override filled nothing (a filed value always wins).
  - Reconciliation against the cash-flow statement: the `PaymentsForCapitalImprovements` line is the 10-K's whole "Capital expenditures" investing line, not a slice of it. The old override's own source cites that line with the same three per-year values. statements.json's cash-flow capex line for FY2024–26 equals the three figures key_numbers.md prints. Its investing section for those years holds only that capex line and business-acquisition payments (VACCO in FY2026), with no construction-in-progress, intangible or capitalised-software line beside it.
  - Resolution, per ruling 3 and WORKER_SPEC step 4: the override was removed. The final run has empty `overrides_applied`, `data_gap` and `data_gap_uncovered`. make_score dropped RBC's capex entry from `_system/overrides_registry.json`.
- **CAPEX_COVERAGE_LOW did not fire.** Capex is not below 50% of D&A in all of the last three fiscal years. FY2024 and FY2025 capex do sit below half of D&A (FY2026 does not). The reason is in the cash-flow statement: the D&A addback (`DepreciationDepletionAndAmortization`) includes amortization of the large acquired-intangibles balance from Dodge, carried on the balance sheet in statements.json. The investing section shows no unread capex line (above). The split between depreciation and amortization is not in the computed outputs, so the ratio against depreciation alone cannot be checked from them.
- No other 5.5 flag fired (share-scale, share-basis, share-class and SBC-reconciliation flags: reasons above).

**Flags on the final run (key_numbers.md)**
- **SHARES_FALLBACK.** The two history rows on a non-diluted count are fragment rows dated 2021-04-30 and 2022-04-30, with `shares_tag` FALLBACK:dei. They carry no operating cash flow, so the engine computes no OE/share on them. The fiscal-year rows for FY2021 (2021-04-03) and FY2022 (2022-04-02) carry filed diluted counts. The base does not touch either fragment row: the TTM denominator 31,714,686 (ttm.json) and the latest FY count 31,634,888 are filed diluted counts.
  - Both fragment rows were in the 5.4 file too.
  - Side effect: the engine's "5-yr" revenue CAGR (18.75%) reads the sixth row back, so these rows shorten its window to start at FY2022. The scenario starts below are anchored on guidance, not on the blend, so this does not move the tier. It is noted for the engine owner.
- **WIDE_SCENARIO_SPREAD.** Super-bull IV is 4.82x super-bear IV. The spread is real because the OE yield is only 2.22% even on the TTM pin (below 2% on the 3-yr median, see LOW_OE_YIELD below) and the value rests on growth duration. It does not straddle the hurdle: even the super-bull IRR (10.44%) is below 15%. Confidence stays **medium**, never high, with the verdict sized to the conservative end (Tier D on both bases, see "Why the TTM pin is kept").

**Flags from the 2026-10-16 run that no longer fire**
- **OVERRIDE_APPLIED:capex.** Gone, because no override is declared or applied.
- **BASE_DIVERGENCE.** Not raised. With filed capex the 3-yr median is $7.68 against a latest FY of $9.74. The 2026-10-16 divergence came mostly from the override's flat capex depressing FY2024–25 OE, the distortion that record disclosed.

**STALE_FY did not fire on either run.** It is not on the 2026-10-16 flag list, and the final run's months since FY end is 6.7, under the engine's seven-month trigger. The trigger is crossed seven months after the 2026-03-28 FY end, in late October 2026. Any re-run from then on raises STALE_FY, and WORKER_SPEC step 4 then calls for the `--ttm` pin.

**Flags live on the normalized base (not raised on the final run): LOW_OE_YIELD and HIGH_NET_DEBT**
- **What the final-run diagnostics measure.** The engine computes OE yield and the net-debt ratio on the base the run prices, here the $11.05 TTM pin. So OE yield 2.22% and the key_numbers.md line "Net debt / normalized OE: 2.34x" are both on the TTM base, despite the "normalized" label. That is why neither flag fires on the final run.
- **On the 3-yr normalized base both conditions hold.** Normalized (3-yr median) OE/share is $7.68, over 31,634,888 diluted shares, against net debt (latest) of $818.2M. On that base net debt is above the engine's 3x HIGH_NET_DEBT trigger. The OE yield, $7.68 against the $498.52 price, is below its 2% LOW_OE_YIELD trigger. Both flags fired on the preliminary median-base run for this reason. The median-base ratio and yield are not printed in the final computed outputs, so they are given here only as threshold crossings, not as figures. I treat both flags as live.
- **HIGH_NET_DEBT, resolution.** Net debt (latest) is $818.2M, on the debt/cash basis in the 2026-10-16 text (unchanged). The 2026-10-16 text records the term loan being paid down out of the operating-cash-flow step-up, and that step-up continues: ttm.json current-YTD OCF is $171,800,000 against $120,000,000 prior-YTD. The term-loan payoff is still on the watch list below. The bear cases stress leverage through the 0.75 / 0.9 OE multipliers. The flag does not move the tier: D on either base.
- **LOW_OE_YIELD, resolution.** On either base the price pays almost entirely for growth. That is why the tier is D even on the higher TTM base: weighted IRR 6.58%, and even the super-bull path (10.44%) is short of 15%. A median-base run would sit lower still (see "Why the TTM pin is kept").

**Why the TTM pin is kept (pending Andrew's ruling).** The pin is the carried-over 2026-10-16 judgment (a re-run keeps prior decisions unless the filing changes them), and ruling 3 asks for ttm.py to be re-run. The reason the 2026-10-16 text gave for the pin is gone: BASE_DIVERGENCE no longer fires, and the override that depressed the median has been removed. STALE_FY, the method's own trigger for a TTM base, did not fire either (above). What still supports the pin:
- The TTM through Q1 FY2027 is the latest four filed quarters.
- The operating-cash-flow step-up continued into the new year: ttm.json current-YTD OCF is $171,800,000 against $120,000,000 prior-YTD.
- The 3-yr median still averages in FY2024–25, before that step-up.
- Any re-run from late October 2026 raises STALE_FY (above), and the pin is then required.

The TTM base ($11.05) is the less conservative of the two bases; the median is $7.68. The published IV@15% and hurdle prices (15% at $146.04 · 20% at $99.43 · 25% at $74.39) rest on the TTM base. This run's outputs print no weighted IRR or IV@15% for the median base, so the conservative-end hurdle price cannot be quoted here. The tier does not depend on the choice: a lower positive base can only lower an IRR that is already in Tier D, and the preliminary 5.5 run on the median base (default offsets) also tiered D. Whether to keep the pin or re-score on the median is escalated to Andrew. The pin is also what keeps LOW_OE_YIELD and HIGH_NET_DEBT off the final run's flag list; both are treated as live above, so the pin hides neither.

**Growth and scenarios (final run).** The engine's blend is 12.07% → g_base 12.07%. Its components:
- rev CAGR 5y 18.75%
- rev CAGR 3y 8.42%
- latest rev YoY 14.34%
- OE/share CAGR 2y 12.68%, now on filed capex in both endpoint years

The scenario growth starts are held where the 2026-10-16 guidance check put them: −0.3% / 5.7% / 11.7% / 16.7% / 23.7%. The base start stays inside the company's Q2 FY2027 sales guidance range quoted above, and the bull start stays below the acquisition-boosted Q1 print, for the reason given above. To hold the starts on the lower blend, the offsets were re-set from (−0.14, −0.08, −0.02, +0.03, +0.10) to (−0.124, −0.064, −0.004, +0.046, +0.116) (dcf_numbers.json `inputs.offsets`). The blend moved for a data reason (capex), not because of new business evidence. Keeping the old offsets would have dropped the base start below the guidance range with nothing to support it. The other inputs are unchanged: probabilities 10/25/30/25/10 (judgment.json `probs_used`), OE multipliers 0.75 / 0.9 / 1.0 / 1.1 / 1.25, moat 6/10, CAP 9.8 yrs, terminal growth 2.50%, price $498.52 (nasdaq_quote_api).

| Scenario | Prob | Growth start | OE mult | IV@15 | IV@12 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -0.3% | 0.75 | $59.95 | $78.14 | 3.94% |
| Bear | 25% | 5.7% | 0.9 | $93.96 | $124.89 | 4.95% |
| Base | 30% | 11.7% | 1.0 | $136.30 | $184.43 | 6.25% |
| Bull | 25% | 16.7% | 1.1 | $187.05 | $256.56 | 7.74% |
| Super bull | 10% | 23.7% | 1.25 | $288.97 | $403.20 | 10.44% |

- **Weighted: IV@15% $146.04 (-70.7% vs price), IV@12% $198.83, IV@10% $258.34; weighted IRR 6.58%, base-case IRR 6.25%.**
- Hurdle-clearing prices (weighted path): 15% at $146.04 · 20% at $99.43 · 25% at $74.39.
- Diagnostics: OE yield 2.22% · TV share @15% 21.3% · scenario spread 4.82x · net debt / normalized OE 2.34x · months since FY end 6.7. OE yield and the net-debt ratio are computed on the $11.05 TTM pin; on the 3-yr median base both cross their flag triggers (see LOW_OE_YIELD and HIGH_NET_DEBT above).

**Research (2026-10-19).**
- RBC has not yet reported Q2 FY2027; third-party calendars project late October. The Q2 sales guidance issued with the Q1 FY2027 release on 31 July 2026 is the latest the company has given ([Q1 FY2027 release](https://secure.businesswire.com/news/home/20260731711418/en/RBC-Bearings-Incorporated-Announces-Fiscal-First-Quarter-2027-Results); [Q1 call highlights](https://www.marketbeat.com/instant-alerts/rbc-bearings-q1-earnings-call-highlights-2026-07-31/)).
- The Q1 FY2027 10-Q guides FY2027 capex as a percentage of net sales, funded from cash and internal funds ([10-Q](https://www.sec.gov/Archives/edgar/data/0001324948/000121390026083879/ea0299277-10q_rbcbear.htm)). Capex keeps climbing with sales, which supports using the filed TTM capex leg as the run-rate rather than treating it as a peak.
- No new red flag was found. The open watch items in the 2026-10-16 text (VACCO margins, capex intensity, deal discipline, term-loan payoff) are unchanged.

**Why the tier is D.** The weighted IRR is 6.58%, below the 10% floor of Tier C. The bear (4.95%) and bull (7.74%) ends are both Tier D, so there is no TIER_BAND. Even the super-bull path (10.44%) is short of the 15% hurdle, and the stock clears 15% only near $146.04.
- Engine 5.5 lowered the base from $11.3512 to $11.05 because the filed TTM capex is higher than the override's prorated legs. That cost 6.69% → 6.58% of weighted IRR and changed no tier.
- `tier_override` stays null. The tier no longer rests on any judgment override, so score.json now reports `exit_alert_eligible: true`. `alert_eligible` stays false (Tier D).
- Confidence: **medium**, capped by WIDE_SCENARIO_SPREAD. The filing data now comes straight from the filings for every leg.

**Data / enrichment (2026-10-19).** All six enrichment steps ran without failure:
- `fundamentals.py`: fundamentals.json refreshed, now carrying the scored price. It has no capex for FY2024–26, because `fundamentals.py`'s capex tag list does not include `PaymentsForCapitalImprovements` (decision 3 added the tag to `dcf_engine.py` and `ttm.py`; `statements.py` already reads it). So fundamentals.json's FY2024–26 and TTM capex, owner's-earnings, FCF and capex-to-revenue fields are blank, and the site's fundamentals view shows none of them for the years the score rests on. The filed figures are in the CSV, statements.json and ttm.json, and neither the base nor the tier reads fundamentals.json. The fix is a separate code PR (a test, and the README decision-3 sentence updated), then a fundamentals.py re-run for RBC and the other capital-improvements filers. It is escalated.
- `prices.py`
- `segments.py`
- `statements.py`: statements.json content unchanged. Its capex line agrees with the CSV for FY2024–26.
- `profile.py`: profile.json unchanged. One warning: no headcount sentence was found in the 10-K filed 2026-05-15.
- `reprice.py`: live.json written.
