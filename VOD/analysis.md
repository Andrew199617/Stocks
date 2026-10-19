# VOD — Vodafone Group Plc
v5 run, 2026-10-14. 20-F filer (EUR reporting, IFRS), ADS-listed on Nasdaq (1 ADS = 10 ordinary shares). **Scope note:** score.json records `in_scope_under_40b: false`, consistent with make_score.py's computation from the engine's market_cap_est ($405.571B) — but that figure is an ADS artifact: the engine prices every *ordinary* share at the full *ADS* price. On an ADS-equivalent share count the market cap is roughly a tenth of the printed figure, i.e. borderline at the $40B scope line. The per-share DCF figures themselves are correctly ADS-scaled (see ADS_RATIO_APPLIED below).

All DCF figures below are copied from key_numbers.md / dcf_numbers.json — none are recomputed. Company-reported figures are cited to Vodafone's published results.

## What it is
One of Europe's largest telecom operators plus a majority stake in Vodacom (Africa). After a three-year restructuring under CEO Margherita Della Valle — Spain sold (May 2024), Italy sold (Dec 2024/Jan 2025), UK merged with Three (completed 31 May 2025, creating VodafoneThree, the UK's largest mobile operator with ~28m customers) — the group is now Europe (Germany is the largest single market), the UK, Türkiye, and Africa, plus Vodafone Business (enterprise, IoT). FY26 (ended 31 Mar 2026, company-reported): revenue €40.5B (+8.0% reported, incl. Three UK consolidation from 1 June 2025), service revenue €33.5B (organic +5.4%), adjusted EBITDAaL €11.4B, operating profit €2.8B (vs a €0.4B loss in FY25), adjusted free cash flow €2.6B, dividend 4.6125 eurocents (+2.5%), €2B buyback completed. Q1 FY27: organic service revenue +5.2%, organic adjusted EBITDAaL +6.2% — growth has genuinely resumed, led by Africa (+12.6% organic) and Türkiye, with Germany back to growth (+1.2% organic).

## Owner's earnings — and why the engine's base is not believable for a telecom
**FY2025 (20-F via EDGAR, from financials_history.csv, USD-converted at the period-end rate):** operating cash flow $16.626B; capex $4.676B (tag: PurchaseOfPropertyPlantAndEquipmentClassifiedAsInvestingActivities); SBC $0.119B.
- **Conservative owner's earnings FY2025: $11.831B = $4.52/share (per ADS)** (key_numbers.md: latest FY OE/share $4.52; normalized 3-yr median $4.87/share).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $2.957B — far below the conservative figure, because FY2025 net income (−$4.051B) is loaded with non-cash impairments (see NI_OCF_DIVERGENCE).
- OE positive 5 of the last 5 fiscal years on the conservative definition.
- **Base used = the engine's normalized base, $4.87/share** (median of last 3 FY OE/share, per ADS). ttm.py cannot run for this filer (see STALE_FY), so no TTM base exists.

**The measurement problem (the reason for the tier override):** the conservative OE subtracts only the PP&E-purchase capex tag. For a telecom that misses most of the cash cost of running the network:
- Group **capital additions were €6.9B in FY25** (FY26 results presentation) vs the ~€4.3B the engine's PP&E tag captures — the difference is spectrum licences and intangible (software/network) capex, filed under investing tags the engine does not read.
- **Lease principal payments** sit in financing cash flows, outside the OCF the engine starts from.
- **Cash interest** likewise sits outside the read OCF presentation.
Vodafone's own adjusted free cash flow — EBITDAaL less capital additions, lease payments, cash interest and cash tax — was **€2.5B in FY25 and €2.6B in FY26**, roughly a *quarter* of the engine's €10.9B FY25 OE total. The two OE definitions the engine prints bracket the truth ($11.83B conservative vs $2.96B maintenance), and the company's own cash measure sits at the maintenance end. A DCF built on the conservative base is therefore measuring a cash stream roughly 4x the one shareholders actually receive. This cannot be fixed with a bounded override: capex overrides only fill periods where the tag is *absent* (the PP&E tag is present every year), and a corrected base would have to be built from figures outside this run's code outputs. It is handled instead as a tier override, below.

## Moat: 4/10 — weak
Justification: Vodafone owns scarce spectrum and sunk network infrastructure in 15+ markets and is now the UK's largest mobile operator via VodafoneThree, with real scale in Germany (largest market), a majority stake in Vodacom with M-Pesa financial services in Africa, and a top-tier enterprise/IoT franchise. But connectivity is a commodity: switching costs are low, regulators cap returns and mandate wholesale access, MVNOs and price competition (Germany especially) grind ARPU, and ROCE has run below the cost of capital for years — the FY26 investor targets only promise ROCE above WACC by FY32. Scale buys survival and synergies, not pricing power.
- FOR: scarce licensed spectrum + sunk network assets in 15+ markets; VodafoneThree is the UK's largest mobile operator (~28m customers) with a £1bn/yr cost-saving target by FY32 (upgraded Oct 2026 from £700m by FY30); Germany scale — largest single market, cable/fibre footprint to ~75% of homes; Vodacom + M-Pesa African growth and mobile-money franchise (Safaricom effective stake raised to 55% in June 2026, consolidated from 1 July 2026); Vodafone Business — global enterprise and a 240m+-connection IoT platform, digital services growing high-double-digit.
- AGAINST: commodity connectivity — low switching costs, MVNO and price competition, Germany in particular; regulated returns — spectrum auctions, wholesale-access mandates and price interventions cap ROCE (below WACC for years); structural decline in legacy fixed/voice while OTT players capture the value layer above the network; emerging-market/FX exposure — Türkiye hyperinflation accounting (IAS 29), EGP/ZAR volatility; leverage constrains the investment race — company net debt €25.4B at FY26-end (2.2x adjusted EBITDAaL) plus the £4.3B (€4.9B) cash buyout of CK Hutchison's 49% of VodafoneThree agreed May 2026.
- A 4 gives CAP = 7.2 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 7.2 years, 15-year projection.

## DCF — v5 final run (2026-10-14)
Probabilities were skewed defensive vs the 10/25/30/25/10 defaults (15/30/30/18/7): the filed OE/share history is disposal-broken (revenue 5-yr CAGR −3.85%, OE/share CAGR 2y −5.60% per key_numbers.md), leverage is real, and the bull case requires synergy delivery plus a German turnaround holding simultaneously. Offsets and multipliers are the defaults (−12/−5/0/+5/+12pp; 0.75/0.90/1.00/1.10/1.25). Growth blend −2.16% → g_base 1.35% after the +3.51pp buyback adjustment. Price $15.51.

**Sanity check vs actual prints:** FY26 organic service revenue grew +5.4% and Q1 FY27 +5.2% (EBITDAaL +6.2% organic) — above the 1.4% base start. Written reasons the base start still sits below the prints: (1) the prints are *service revenue*, not OE/share — the engine's base variable has a filed 2-yr CAGR of −5.60% across the disposal years; (2) reported growth is flattered by the Three UK consolidation (+8.0% reported FY26 revenue) and by Türkiye, where IAS 29 hyperinflation accounting added 5.5pps to reported Q1 growth (organic Türkiye +30.2% is mostly inflation pass-through, not real OE growth); (3) the core European business ex-Türkiye grows organically at ~1-3% (Germany +1.2%, UK +0.6%, Other Europe +1.0% in Q1 FY27). The bull start (6.3%) roughly equals today's organic print sustained with synergy delivery; the super-bull start (13.4%) exceeds any sustained print in the company's history and is weighted only 7%. The growth debate is second-order here in any case: it is the *level* of the base, not its growth rate, that is mis-measured (see Owner's earnings).

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | −10.0% | 0.75 | German price war resumes; synergy delivery slips; EM FX bites | $18.37 | 17.65% |
| Bear | 30% | −3.6% | 0.90 | Filed-history drift continues; disposals' drag not fully replaced | $28.30 | 26.22% |
| Base | 30% | 1.4% | 1.00 | Post-restructuring portfolio grows at its filed-blend rate | $38.19 | 33.61% |
| Bull | 18% | 6.3% | 1.10 | Current organic prints hold; VodafoneThree synergies land | $50.89 | 41.75% |
| Super bull | 7% | 13.4% | 1.25 | Synergies + Africa/Türkiye momentum compound for a decade | $75.27 | 54.58% |

- **Probability-weighted (engine, uncorrected base): IV@15% $37.13 (+139.4% vs price), IV@12% $48.81, IV@10% $61.78, weighted IRR 32.57%, base-case IRR 33.61%**
- **Tier by numbers: S.** Diagnostics (key_numbers.md): OE yield 31.39%, terminal value 17.7% of IV@15%, scenario spread 4.10x, months since FY end 18.5. (The printed net-debt/normalized-OE of 0.36x is an ADS-scaling artifact — see ADS_RATIO_APPLIED; the preliminary pre-scaling run printed 3.58x on the same data.)
- **These numbers are not credible as economics** — see the tier override in the verdict. Even the super-bear case (0.75x base, −10% growth start) "earns" 17.65%, because every scenario is built on a base ~4x the cash shareholders receive.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 18.5 months ago; engine history ends FY2025): ttm.py was run and exited 3 with: "ttm.py: cannot compute TTM for VOD (CIK 839923): ocf: no annual (FY) fact; sbc: no annual (FY) fact; shares_diluted: no annual (FY) fact; capex: no capex facts in companyfacts under any candidate tag and no capex_override in judgment.json — refusing to zero-fill". ttm.py reads us-gaap facts only, so this failure is expected for an IFRS filer; per the method, the engine's median base is used and that is stated here. Corroboration from published results (not used as a base — no hand TTM math): FY26 revenue €40.5B, adjusted EBITDAaL €11.4B, operating profit €2.8B, adjusted FCF €2.6B — the business grew after the engine's last filed year, so the stale base is not flattering the verdict on direction; the override below rests on the capex/lease/interest measurement gap, which FY26's own presentation confirms (capital additions €7.3B in FY26).
- **BUYBACK_TAILWIND** (share count −3.51%/yr): already credited via the +3.51pp growth adjustment in the blend (g_blend −2.16% → g_base 1.35%); the €2B buyback was completed in FY26. Not double-counted in the verdict.
- **NI_OCF_DIVERGENCE** (2024, 2025): identified one-offs. FY2025 net income −$4.051B vs OCF $16.626B — the gap is non-cash impairments (the FY25 reported loss was impairment-driven; operating profit was −€0.4B while cash generation held). FY2024 net income $1.627B vs OCF $17.900B — the same pattern of non-cash charges against intact cash flow; the mirror image is FY2023 (net income $13.414B vs OCF $19.634B), where the ~€8.6B Vantage Towers disposal gain inflated net income without touching OCF. The OCF-based conservative OE used throughout is the cleaner series; it is the maintenance (NI-based) figure that the impairments distort.
- **FX_CONVERTED**: EUR reporting converted to USD at period-end ECB reference rates (FY2025: 1.0815; full rate table in dcf_numbers.json). Flow facts use the period-end rate, not a period average — a documented simplification; EUR/USD has been range-bound enough (1.08-1.14 across the last five fiscal year-ends) that this is not a verdict driver.
- **USD_TRANSLATIONS_USED**: where Vodafone files its own USD convenience translations, the engine used the filed USD figures rather than converting — noted; the base rests partly on issuer translations.
- **ADS_RATIO_APPLIED**: ads_ratio {ratio: 10} declared in judgment.json under the bounded authority — the ratio is stated in the filer's own Form 20-F (filed 14 June 2024, cover: ADSs "each representing ten ordinary shares"). Effect: all per-share figures scaled x10 to ADS terms, making the DCF comparable to the $15.51 ADS price. Two diagnostics do *not* inherit the scaling consistently and are flagged rather than trusted: market_cap_est ($405.571B — ordinary shares priced as ADSs) and net debt / normalized OE (0.36x printed vs 3.58x on the pre-scaling preliminary run).
- **HIGH_NET_DEBT** (fired on the preliminary run at 3.58x normalized OE; absent from the final flag list only because of the scaling artifact above): leverage is real and is folded into the verdict. Company-reported net debt was €25.4B at FY26-end (2.2x adjusted EBITDAaL), *before* the £4.3B (€4.9B) cash payment for CK Hutchison's 49% of VodafoneThree (agreed May 2026; completion reported 30 July 2026). On levered equity, a cash stream overstated 4x by the model is exactly how an S-tier mirage forms — another reason the numbers tier cannot stand.
- **WIDE_SCENARIO_SPREAD** (4.10x): real even before the base problem — outcomes range from German-relapse decline to a synergy-compounded recovery. Confidence is low and the verdict is sized to the conservative end.

## My thoughts / overlay
- The honest headline is the **method range**: Tier S on the engine as specified (32.57% weighted IRR) vs Tier D on the company's own cash definition. The gap is not judgment noise — it is a named, mechanical gap in the standardized model (PP&E-only capex tag; lease principal and cash interest outside the OE definition) that hits capital-intensive telecoms the way the Finance/RE/Utilities mismatch hits those sectors. The engine team may want a telecom note alongside SECTOR_MODEL_MISMATCH: any operator whose spectrum/intangible capex is material will print an inflated OE yield (31.39% here) under the current tag set.
- On the cash shareholders actually receive: adjusted FCF was €2.6B in FY26, with FY27 adjusted FCF guided at €2.6-2.9B and the dividend (4.6125 eurocents, +2.5%) covered roughly twice by that FCF. At the recent share price (LSE close GBp 126.80 on 2 Oct 2026, per press reports; ADS $15.51) that is a high-single-digit cash yield — a bond-like equity: respectable, improving, and nowhere near a 15% IRR unless FCF compounds at rates Vodafone has never sustained.
- What is genuinely better than the filed history suggests: the portfolio is finally coherent, Germany has returned to growth, the UK merger synergies were upgraded (£1bn/yr by FY32), Africa compounds double-digit, and buybacks shrink the count ~3.5%/yr. If the engine could read total capital additions, this name would likely land C/D on real numbers with an improving trajectory — cheap-ish, not a table-pounder.
- Price that clears 15%: on the engine's (uncorrected) numbers the weighted IV@15% is $37.13, above the price — that is the artifact, not an opportunity. On the company's own FCF definition, a 15% IRR at anything like guided growth needs an entry price far below $15.51; no code output computes that price, so none is quoted.

## Final verdict
- **Final tier: D** (tier_override of the numbers tier S, reason in judgment.json and above: the engine's OE base excludes spectrum/intangible capex, lease principal and cash interest, overstating owner's earnings ~4x vs Vodafone's own adjusted FCF; every scenario inherits the inflated base)
- Confidence: **Low** (high confidence that the S is a measurement artifact; low confidence in any single corrected figure, since no code output produces one)
- One-liner: Post-restructuring telecom, moat 4/10 — engine prints Tier S (32.6% weighted IRR, IV@15 $37.13) only because its capex tag misses spectrum/intangible capex, lease principal and cash interest; on Vodafone's own adjusted FCF (EUR 2.6B in FY26) the cash yield is ~7% with low-single-digit guided growth, so it does not clear 15% at $15.51 — final tier D by override, numbers tier S retained.

## Engine 5.5 re-score (2026-10-19)
This is a dated addendum. The 2026-10-14 text above records that run and has not been rewritten. Every figure in this section comes from the final run's key_numbers.md or dcf_numbers.json (2026-10-19). The only exceptions are the "old" figures: they come from the 2026-10-14 run, which was pre-5.4 output (`engine_version` 5, no `engine_release`).

**Runs.** The recorded judgment inputs were reused unchanged: moat 4, probabilities 15/30/30/18/7, default offsets and multipliers, terminal growth 2.50%, and the median base with no pin. The preliminary run (default inputs) and the final run (`--moat 4 --probs 0.15,0.30,0.30,0.18,0.07`) both exited 0 with no data gap, on engine release 5.5.0. The price is $16.11 (nasdaq_quote_api); the 2026-10-14 run used $15.51. After the audit of this section, make_score and reprice were run again on 2026-10-19 without an engine run: only judgment.json's `tier_override_reason` and `one_liner` changed, and every figure is the same.

| | 2026-10-14 (pre-5.4) | 2026-10-19 (engine 5.5.0) |
|---|---|---|
| Price | $15.51 | $16.11 |
| Base OE/share (per ADS, 3-yr median) | $4.8690 | $3.82 |
| Latest FY OE total (FY2025) | $11.831B | $9.262B |
| Weighted IRR | 32.57% | 25.16% |
| Weighted IV@15% | $37.13 | $29.11 |
| Bear → bull IRR | 26.22% (S) → 41.75% (S): one tier, no band | 20.07% (A) → 32.46% (S) |
| Tier by numbers | S | **S** |
| Final tier | D (override) | **D (override, unchanged)** |
| Market cap (est) | $405.571B (ordinary shares × ADS price) | $42.126B (price × shares ÷ ads_ratio) |
| Net debt / normalized OE | 0.36x | 4.57x |
| `in_scope_under_40b` | false | false |

**What engine 5.5 changed for VOD**
1. **Capex now includes the intangible leg (ruling 5, narrowed).** `capex_tag` is now `PurchaseOfPropertyPlantAndEquipmentClassifiedAsInvestingActivities+PurchaseOfIntangibleAssetsClassifiedAsInvestingActivities`. In the 2026-10-14 run it was the PP&E tag alone. The PP&E roll-up stays authoritative, and the IFRS intangible purchases are added on top of it. key_numbers.md capex basis:
   - FY2023: $8.435B (PP&E $5.391B + intangibles $3.044B)
   - FY2024: $7.416B (PP&E $4.561B + intangibles $2.855B)
   - FY2025: $7.245B (PP&E $4.676B + intangibles $2.569B)

   The intangible leg is the filed EUR 2,799M / 2,641M / 2,375M for FY2023–25, converted at the same period-end ECB rate as the PP&E leg. The engine dropped no fact (`capex_provenance`).
   - **Cross-check (AGENTS.md check 4).** statements.json's cash-flow statement has exactly these two capex lines for FY2023–25: purchases of PP&E, and purchases of intangibles / software. The CSV's `capex` equals their sum at the run's rates. statements.json's other investing lines (acquisitions, purchases and sales of investments) are not capex.
   - **Spectrum: cannot verify from the run.** I could not confirm from this run whether Vodafone's spectrum-licence payments sit inside the intangible-purchases line. If they do, the engine's capex is now stricter on that item than the company's adjusted FCF, which is defined before spectrum.
   - **Effect:** the base falls from $4.8690 to $3.82 per ADS. The FY2025 OE total falls from $11.831B to $9.262B. The OE/share 2-year CAGR moves from −5.60% to −5.68%.
2. **Market cap on the ADS basis (ruling 1).** The cap fell from $405.571B to $42.126B (basis `diluted_latest`; price × shares ÷ ads_ratio). It now prices 26,149,000,000 ordinary shares as ADSs at 10 shares per ADS.
3. **Normalized OE total on the ADS basis (ruling 1, "anything downstream").** Net debt / normalized OE moves from 0.36x to 4.57x, and HIGH_NET_DEBT now fires. The 2026-10-14 text had already called the 0.36x a scaling artifact.
4. **Share basis (ruling 2).** The share-scale guard ran and found no defect:
   - The latest diluted count is 26,149,000,000.
   - The base OE/share is far below 20× the price.
   - The only cover-page count is dated 2021, outside the guard's 18-month window, so the guard ignores it.
   - No split fact, no divergence and no `share_class_mismatch` are recorded, and no SHARE_* flag fired.
5. **SBC tag (ruling 6).** SBC values are unchanged, and SBC_TAG_RECONCILED did not fire: as an IFRS filer, VOD does not file the us-gaap Share/Allocated pair, and `sbc_provenance` is empty. `used_tags.sbc` now names `ExpenseFromSharebasedPaymentTransactionsWithEmployees`, the tag the latest CSV year actually used; it previously read `AdjustmentsForSharebasedPayments`. This is a provenance change only.
6. **USD-override branch (ruling 7).** Not engaged. VOD carries no field override (`overrides_applied` is empty), so no override was converted or used verbatim as USD.
7. **CAPEX_COVERAGE_LOW (ruling 5).** Did not fire: with the intangible leg, capex is above half of D&A in each of FY2023–25.

**Flags in the final run, by name**
- **HIGH_NET_DEBT (new under 5.5).** Net debt is $45.577B (FY2025: borrowings tags less cash), 4.57x normalized OE. The leverage is real, and it is one input to the D.
  - The engine's net debt counts current plus long-term borrowings less cash and cash equivalents at 31 March 2025. Vodafone's own net-debt measure (quoted in the 2026-10-14 text) is narrower, and it is dated a year later (FY26-end).
  - One reason for the gap can be checked in the folder. statements.json's FY2025 balance sheet carries a current-investments line (`short_term_investments`, tag `CurrentInvestments`), and its `metrics.net_cash` nets that line against borrowings. The engine's net debt does not. That amount is not in key_numbers.md or dcf_numbers.json, so it is named here rather than quoted.
  - Netting the current investments would lower the ratio but leave it above the HIGH_NET_DEBT threshold, so the flag fires either way.
  - Lease liabilities inside IFRS borrowings may explain the rest of the difference, but that cannot be verified from the run: the CSV's `lease_liabilities` column is blank.
  - Two transactions add leverage after the engine's last balance sheet: the cash buyout of CK Hutchison's VodafoneThree stake (agreed May 2026), and Vodacom's purchase of a further Safaricom stake (completed 30 June 2026, consolidated from 1 July 2026).
  - Stressing the bear cases on the engine's own base gives super-bear 13.51% and bear 20.07%. The final D sits below every scenario.
- **TIER_BAND (new for VOD).** The bear case is tier A (20.07%) and the bull case is tier S (32.46%).
  - The flag is new because the bear case fell from S (26.22% in the 2026-10-14 run) to A under the intangible leg. The 2026-10-14 bear and bull were both S, so the flag would not have fired then under any engine release.
  - Any sizing would start at the bear end at most. The final tier sits below it (D), because the bear end still uses an OE base that is before lease payments and interest and that still carries Spain and Italy (see "Why the tier is what it is").
- **STALE_FY.** The latest FY ended 18.6 months ago.
  - ttm.py was run on 2026-10-19 and exited 3. It reads us-gaap facts only, and as an IFRS filer VOD has no annual OCF, SBC or diluted-share fact and no capex tag under us-gaap. There is no ttm.json, so the median base is used.
  - The FY2026 20-F (period 2026-03-31, filed 2026-05-22) is not yet in EDGAR companyfacts (fundamentals.py and statements.py warnings). segments.json does read that 20-F's XBRL instance, for FY2026 revenue and D&A by segment. But no output of this run carries FY2026 operating cash flow or capex, so no FY2026 base can be built from it.
  - Interim 6-K results are not companyfacts facts either (fundamentals.py: "no quarterly facts").
  - A `base_override` may be built only from this run's outputs (step 8 (c)), so a FY2026 or TTM base is outside bounded authority. **Queue a re-score once companyfacts carries the FY2026 20-F.**
  - The stale base does not flatter the D: the company's FY26 adjusted FCF in the override reason is in line with FY25.
- **BUYBACK_TAILWIND.** The share count CAGR is −3.51%, and the adjustment of 3.51% applies only to the revenue components (the 5.4 rule), so it is credited once. g_base stays at 1.35%.
- **NI_OCF_DIVERGENCE (2024, 2025).** Unchanged: the impairment-driven gaps resolved above still apply. The intangible leg does not touch OCF.
- **FX_CONVERTED.** Both capex legs are EUR facts converted at the same period-end ECB rate, so the new leg brings no new FX basis.
  - Correction to the 2026-10-14 text: `fx_conversion` records 1.1725 for 2021-03-31, so the FY2021–25 year-end rates span 1.0811–1.1725 (1.08–1.17), not 1.08–1.14.
  - The conclusion stands. The base years FY2023–25 were converted at 1.0811–1.0875, so the period-end simplification does not drive the verdict.
- **USD_TRANSLATIONS_USED.** Correction to the 2026-10-14 text, which said the base rests partly on issuer translations. It does not.
  - The only issuer USD facts the engine used are net income (`ProfitLoss` filed in USD) for FY2016–FY2018.
  - Every FY2023–25 base input (OCF, both capex legs, SBC) and the revenue behind the growth components is a EUR fact converted at the period-end rate (`fx_conversion`). The issuer translations touch neither the base nor the growth inputs.
- **ADS_RATIO_APPLIED.** The ratio is 10, stated on the cover of the 20-F (citation in judgment.json `ads_ratio.source`). Under 5.5 it also divides the market cap and the normalized OE total, which is what moved HIGH_NET_DEBT.
- **WIDE_SCENARIO_SPREAD.** The spread is 4.10x, so confidence stays low.

**Scope call (ruling 1).** The ADS-corrected market cap is $42.126B at $16.11 (price × shares ÷ ads_ratio, basis `diluted_latest`), and key_numbers.md reads "out of scope (market cap $40B or more)".
- judgment.json `in_scope_under_40b` is **false**, which matches the computed cap. VOD sits just above the line.
- The design review measured the corrected cap just above $40B at the old $15.51 price too, so this call does not depend on the price move since 2026-10-14.

**Why the tier is what it is**
- **The numbers tier is still S.** The approved scope (the intangible leg alone) moved the weighted IRR from 32.57% to 25.16% but did not take VOD out of Tier S.
  - Ruling 5 expected the numbers tier to move down from S. Under the approved scope it does not, and that is reported here plainly.
  - The S is marginal: the price of $16.11 sits just under the $16.22 price at which the weighted IRR equals 25%. A small rise in the ADS price would read A.
  - The S also rests on a base that still contains Spain and Italy (next point), so it overstates the numbers tier.
- **The base still contains Spain and Italy (AGENTS.md check 7; open with Andrew).**
  - The engine's OCF is the 20-F's group total (`CashFlowsFromUsedInOperatingActivities`). It still carries the operating cash flow of Spain (sold May 2024) and Italy (sold Dec 2024/Jan 2025) until their sale: EUR 3,464M / 3,296M / 1,657M in FY2023–25. These are the net operating cash flows of discontinued operations in the Form 20-F for FY2024 and FY2025, cited in the override reason that key_numbers.md prints.
  - statements.json shows no restatement break in the operating-cash-flow series (its FY2022 growth cell is filled), so OCF was never re-presented without the two businesses.
  - The capex the engine subtracts was restated to continuing operations. `capex_provenance` takes FY2023's legs (PP&E EUR 4,957M, intangibles EUR 2,799M) from the 20-F filed 2025-06-06. statements.json's "growth across filing generations" warning blanks the FY2022 capex, intangibles and D&A growth cells for the same restatement. No capex offsets the discontinued operating cash, so each base year's OE is overstated by it.
  - The median year is FY2024, a full year before either sale, and FY2025 still holds part-years of both. So the $3.82 base is not a continuing-operations figure.
  - A continuing-operations base needs the discontinued figures above, and no output of this run prints them. A worker `base_override` built from them is outside bounded authority (WORKER_SPEC step 8 (c)). It is escalated to Andrew, as the CCI continuing-operations base was (README, 2026-10-14).
  - Until he rules, the published numbers tier S, and the 25.16% the ranking sorts on, overstate the business. The correction lowers the base, which moves the numbers tier toward the D, so the final tier does not depend on it.
  - The growth inputs cross the same restatement. Rev CAGR 5y (−3.85%) compares FY2020, as filed before the sales, with continuing-only FY2025. After the buyback adjustment it is −0.34%, one of the two middle components (with the adjusted rev CAGR 3y, 3.03%) whose mean sets g_base 1.35%. That leg pulls growth down while the base is pushed up, and this run cannot net the two.
- **Financing-side costs remain outside the OE.** The capex gap the 2026-10-14 override named is now closed. The OE is still operating cash flow before lease payments and before interest, which Vodafone classifies as a financing cash flow (FY2025 20-F). Ruling 5 keeps both out of the engine: no lease leg and no interest leg.
- **The final tier stays D.** Ruling 5 keeps the override. Its reason is restated on the 5.5 figures (judgment.json `tier_override_reason`, printed in key_numbers.md).
  - The D rests on a figure: Vodafone's own adjusted free cash flow was EUR 2.5B in FY25 and EUR 2.6B in FY26, and is guided at EUR 2.6–2.9B for FY27. The engine's FY2025 OE total is $9.262B. On the company measure the ADS yields roughly 7% at the $42.126B market cap, with net debt at 4.57x normalized OE.
  - That comparison deducts interest as well as lease payments, because Vodafone's measure is after both. The 2026-10-14 interest point is dropped only as an engine leg, which ruling 5 rejected. The company's printed FCF, which the D rests on, is still after interest.
  - The FY2025 OE total also still carries EUR 1,657M of Spain/Italy operating cash, which a continuing-operations figure would not. Beyond that, this run's outputs cannot split the gap between lease payments and interest, so no split is quoted.
- **Minority holders.** Consolidated OCF includes all of Vodacom (JSE-listed, majority-owned) and, from 1 July 2026, Safaricom, so part of that cash belongs to minority shareholders. No output of this run sizes that share. This is a method limit, and it pushes the consolidated base up, consistent with the D.
- **Moat 4 is unchanged.** fundamentals.json's `roic_proxy` is below 10% in four of the last five fiscal years and negative in FY2025. The exception, FY2023, carries the Vantage Towers disposal gain. Gross margin is flat in the low-to-mid thirties.
- **Alerts and confidence.** With tier_final D, `alert_eligible` is false and there is no chat alert. Confidence stays low: WIDE_SCENARIO_SPREAD fired, the OE is still before lease payments and interest, and the Spain/Italy base question is open with Andrew.

**Research used (2026-10-19).**
- [Vodafone FY26 results presentation](https://reports.investors.vodafone.com/view/213859904/): adjusted FCF, capital additions, FY27 guidance, and the definition of adjusted FCF as before spectrum, restructuring and integration costs.
- [Vodafone Q1 FY27 trading update, 27 July 2026](https://www.investegate.co.uk/announcement/rns/vodafone-group--vod/vodafone-q1-fy27-trading-update/9687628): growth resumed, Germany is the weakest market, and guidance was raised after the Safaricom consolidation with the upper end expected.
- Coverage of the guidance raise and the Safaricom consolidation: [Kalkine](https://kalkinemedia.com/uk/news/announcements/vodafone-group-reports-52-organic-service-revenue-growth-in-q1-fy27-raises-full-year-guidance-following-safaricom-consolidation) and [CSI Magazine](https://csimagazine.com/csi/Vodafone-lifts-FY27-outlook.php).

**Data and enrichment (2026-10-19).** fundamentals.py, prices.py, segments.py, statements.py, profile.py and reprice.py all ran with exit 0. Warnings:
- The FY2026 20-F is not yet in companyfacts, so the statements stop at FY2025.
- There are no quarterly tables (20-F filer, no 10-Qs).
- profile.py found no Item 4 business description and no headcount sentence in the 20-F filed 2026-05-22, so the About block is degraded.
- statements.py notes that Vodafone tags its other operating lines with custom elements that companyfacts does not carry.

live.json reprices at the close the run used ($16.11, dated 2026-10-16) with no delta. That close is earlier than the 2026-10-19 scoring date, so the page shows the scored figures marked "live pending" until a later close arrives.
