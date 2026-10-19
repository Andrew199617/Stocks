# ELS — Equity LifeStyle Properties, Inc.
Pass-1 run, 2026-10-19, engine release 5.5.0. **First score for ELS.** On 2026-10-18 engine 5.4.0 blocked it (`DATA_GAP:capex`; the worker escalated `NEEDS_MAIN_AGENT: capex`), so it was never scored and no earlier analysis exists. Andrew's ruling 3 for engine 5.5 (capital improvements) unblocks it. In scope: market cap $12.249B at $61.21 (key_numbers.md; basis diluted_latest, price × shares).

This file describes the final run only. Every valuation figure below is copied from that run's key_numbers.md, dcf_numbers.json, ttm.json, score.json, judgment.json or financials_history.csv; none is recomputed (the few ratios and differences added to explain a flag or a cross-check name their inputs). Figures from research (the Q2 2026 release, call coverage, the 10-Q and the FY2025 10-K) and from the enrichment files (fundamentals.json, statements.json, profile.json) are labelled with their source. The research figures are not carried by any run output, so they cannot be verified from the run outputs; each one names its document (Sources, at the end, links them; profile.json lists the Q2 2026 8-K and 10-Q filings).

## What it is
A Chicago-based, self-managed REIT. ELS owns the land under manufactured homes (MH), RV sites and marinas and leases it to customers who own the homes, RVs or boats, on long-term or short-term terms. It also sells right-to-use memberships (Thousand Trails) for limited stays.

- **Size:** per profile.json (company description as of June 30, 2026), 453 properties with 173,559 sites in 35 states and British Columbia.
- **Markets:** concentrated in retirement and vacation markets (Florida, Arizona, California).
- **Model:** the 10-K describes it as having "low maintenance costs and low customer turnover costs".
- **History:** Sam Zell chaired the board from the IPO until his death in May 2023.

Latest operating facts (research: Q2 2026 earnings release for the quarter ended June 30, 2026, Form 8-K exhibit 99.1, report date July 22, 2026, filed July 23, 2026, accession 0001628280-26-049302 per profile.json; first link under Sources). None of these figures is in the run outputs (fundamentals.json and statements.json stop at 2026-03-31), so they cannot be verified from the run outputs:
- **Q2 2026 revenue:** total revenues $397.8M vs $376.9M in Q2 2025. Only the comparative is in the run outputs: fundamentals.json Q2 FY2025 revenue is $376,866,000.
- **Normalized FFO:** $0.74/sh in Q2 (+7.7%); $1.58/sh for six months (+3.6%).
- **FY2026 Normalized FFO guidance:** $3.13–3.23/sh (midpoint $3.18, up from $3.17).
- **Core 2026 guidance:**
  - MH base rent +5.2–6.2%.
  - RV and marina base rent +1.1–2.1%.
  - Property operating revenues +3.9–4.9%.
  - Income from property operations (excluding property management) +5.5–6.5%.
- **Leverage:** total debt $3,336M at June 30, 2026 (a gross figure for Q2 2026, not the run's FY2025 net debt; see Net debt below); debt / Adjusted EBITDAre 4.4x; interest coverage 5.6x; debt 20.5% of total market cap.
- **Demand:** MH occupancy is about 94% and rose for a second straight quarter. Transient RV demand was uneven (weather, wildfires).

## Owner's earnings
**Conservative OE = OCF − capital improvements − SBC.** The last three fiscal years, from financials_history.csv:

| FY | OCF | Capex (PaymentsForCapitalImprovements) | SBC | OE conservative | Diluted shares |
|---|---|---|---|---|---|
| 2023 | $548,005,000 | $317,086,000 | $17,833,000 | $213,086,000 | 195,429,000 |
| 2024 | $596,721,000 | $241,279,000 | $9,372,000 | $346,070,000 | 196,636,000 |
| 2025 | $571,148,000 | $237,091,000 | $7,252,000 | $326,805,000 | 200,114,000 |

- **Latest FY:** OE total $326.8M, OE/share $1.63. The normalized (3-yr median) OE/share is also $1.63, because FY2025 is the median year (key_numbers.md).
- **Maintenance version:** the CSV's FY2025 oe_maintenance is $402,061,000, which equals net income. Capital improvements exceed D&A ($208,895,000 in FY2025), so that definition charges only D&A.
- **Why the two definitions differ (the main limitation of this valuation):** ELS's capital-improvements line mixes several kinds of spending:
  - recurring, non-revenue-producing improvements ($44.9M for six months of 2026, per the Q2 2026 earnings release, 8-K exhibit 99.1 filed July 23, 2026; cannot verify from the run outputs);
  - growth spending (expansions, site development, property upgrades);
  - purchases of homes for sale or rent;
  - hurricane restoration in FY2023.

  The conservative method charges all of it. That is consistent with the scenarios, which credit the rent and site growth this spending pays for.
- **Base used: TTM through Q1 2026, from ttm.py** (`base_source` ttm_json, base OE/share $1.64):
  - OCF: FY $571,148,000 − prior YTD $193,390,000 + current YTD $194,232,000 = **TTM $571,990,000**.
  - Capex (PaymentsForCapitalImprovements, all three legs): $237,091,000 − $45,202,000 + $45,285,000 = **TTM $237,174,000**.
  - SBC (ShareBasedCompensation on all three legs, no reconciled legs): $7,252,000 − $2,334,000 + $2,148,000 = **TTM $7,066,000**.
  - Shares (current-YTD weighted diluted): **200,176,000**.
  - **TTM OE $327,750,000 → $1.6373/share** (key_numbers.md: $1.64). ttm.json has no warnings, no overrides used and no split adjustment.
- **OE-positive years (last 5): 4/5.** FY2021 is negative because the history years add a second filed line (see Capex completeness).
- **Net debt: $3.338B.** That is LongTermDebt of $3,345,866,000 (`net_debt_basis` TOTAL:LongTermDebt) less unrestricted cash of $7,932,000 (CSV FY2025); the $18,200,000 of restricted cash is kept out. The Q2 2026 release's total debt of $3,336M (research; cannot verify from the run outputs) is not a check on this figure: it is gross debt at June 30, 2026, a later period and a different concept from the run's FY2025 net debt, and it sits about $9.9M below the FY2025 gross LongTermDebt of $3,345,866,000.
- **Share count:** the diluted count (200,114,000) sits above the cover-page common count (193,937,553, dei 2026-04-22). That gap is consistent with operating-partnership units being included in diluted shares, which matches consolidated OCF. I cannot verify this from the run. ELS has no listed subsidiary, so no minority-holder carve-out applies to the consolidated OE.
- **Dividend coverage:** TTM dividends paid of $396,559,000 (fundamentals.json, TTM to 2026-03-31) exceed TTM conservative OE of $327,750,000 (ttm.json). FFO covers the dividend; cash after all capital improvements does not. The balance sheet, equity and dispositions fund the gap.

## Capex completeness (the reason ELS was blocked)
- **Base window FY2023–25:** the CSV's `capex` equals the cash-flow statement's capital-improvements line exactly.
  - statements.json's capex row and dcf_numbers.json's `capex_provenance` both read PaymentsForCapitalImprovements: $317,086,000 / $241,279,000 / $237,091,000.
  - key_numbers.md prints the capex basis as $317.1M (components_mixed_filings) / $241.3M (components) / $237.1M (components), with intangibles $0.00 in each year.
  - FY2023's second component is a $0 PaymentsToAcquireOtherProductiveAssets fact. It contributes nothing (see the Engine 5.5 section).
- **Capex vs D&A:** capex exceeds D&A in all three years: $317,086,000 vs $203,738,000, $241,279,000 vs $203,879,000, and $237,091,000 vs $208,895,000 (CSV). CAPEX_COVERAGE_LOW correctly did not fire.
- **Excluded investing lines:** source is the FY2025 10-K (instance els-20251231, accession 0001628280-26-008722, filed 2026-02-18), Consolidated Statements of Cash Flows, investing section, FY2025 column (research). statements.json carries only the capex, acquisitions and net-investing rows, so the individual lines below cannot be verified from the run outputs; together with capital improvements they sum exactly to statements.json's FY2025 net investing outflow.
  - Lines beside capital improvements ($237,091,000 out):
    - real estate acquisitions, net: $0;
    - proceeds from sale properties (caption as filed): $2,525,000 in;
    - investment in unconsolidated joint ventures: $9,689,000 out;
    - distributions of capital from unconsolidated joint ventures: $13,924,000 in;
    - proceeds from insurance claims, net: $9,358,000 in;
    - issuance of notes receivable: $56,110,000 out.
  - Net cash used in investing activities is $277,083,000, matching statements.json.
  - Capital improvements is the only non-zero property-spending line, and the base charges all of it.
  - Left out of capex:
    - the notes receivable (lending, not property spending; I have not checked the counterparty in the notes);
    - the JV equity investment.
  - The insurance proceeds that partly fund hurricane restoration are not credited to OE either: $5,309,000 in FY2023, $19,703,000 in FY2024 and $9,358,000 in FY2025, per the same FY2025 10-K cash-flow statement (its FY2023–25 columns; research, cannot verify from the run outputs). Leaving them out keeps the base conservative.
- **History years FY2017–2022 (outside the base window):** the engine also sums PaymentsToAcquireProductiveAssets on top of capital improvements.
  - `capex_provenance` shows FY2021 = $398,000,000 + $7,000 (PaymentsToAcquireOtherProductiveAssets) + $204,265,000, and FY2022 = $132,800,000 + $0 + $249,277,000.
  - statements.json's capex row excludes these figures.
  - Their round size and their timing (ELS's acquisition-heavy 2021) suggest real-estate acquisitions rather than capital improvements. **I cannot verify that from the run** (open item below).
  - They do not touch the base (FY2023–25 and TTM) or any growth input: the FY2023 → FY2025 OE/share CAGR uses capital-improvement-only years. They do make FY2021's OE negative (the 4/5 OE-positive count), and they lower FY2022's OE/share to $0.43, which is what fires OE_VOLATILE (see Flags).

## Moat: 6/10 — moderate; the top of the REIT range in this sweep
Justification: the land-lease MH model makes tenants unusually captive, and zoning keeps new supply near zero. Against that, returns on capital are low (about 6%), the RV and marina side is discretionary, and regulation and litigation target the pricing power itself.

**Evidence (fundamentals.json):**
- roic_proxy (after-tax operating income over equity + debt − cash): 5.9% FY2021, 6.1% FY2022, 5.1% FY2023, 6.1% FY2024, 6.1% FY2025.
- ROE: 19.5% / 20.7% / 23.1% / 22.1% / 22.9% over the same years. This reflects leverage on a small, long-depreciated book equity. It does not show returns well above the cost of capital.
- Operating margin: 20.7% (FY2021) → 20.4% → 21.5% → 24.9% → 25.6% (FY2025).
- Gross margin is not computable from the REIT presentation.
- A score of 6 needs no high-ROIC defence. The low ROIC is the main reason the score is not 7+.

**FOR:**
- Residents own their homes on ELS land, and moving a manufactured home is costly. Turnover is low and annual increases stick (2026 MH base-rent guidance +5.2–6.2%; MH occupancy about 94% and rising).
- New MH communities are rarely entitled, and the portfolio sits in high-barrier retirement markets.
- Demand from an ageing 55+ population for the cheapest form of detached housing.
- A conservative balance sheet (4.4x debt / Adjusted EBITDAre) and 22 consecutive annual dividend increases (2026 dividend $2.17/sh, +5.3%; research).

**AGAINST:**
- roic_proxy of about 5–6% (above).
- RV and marina demand is discretionary and weather-exposed. 2026 RV/marina base-rent guidance is only +1.1–2.1%, transient RV demand is uneven, and storm-damaged marinas are waiting on restoration and insurance proceeds.
- Rent regulation (California) and the Datacomp lot-rent antitrust class action (In re Manufactured Home Lot Rents Antitrust Litigation, N.D. Ill. No. 1:23-cv-6715):
  - dismissed without prejudice in December 2025;
  - plaintiffs filed an amended complaint in January 2026;
  - a renewed motion to dismiss is pending, with no accrual (judgment.json records the same). The March 2026 filing date of that motion is research from the Q2 2026 Form 10-Q (period ended June 30, 2026, filed 2026-07-28, accession 0001628280-26-050244) and cannot be verified from the run outputs;
  - ELS owns Datacomp through its MHVillage/Datacomp acquisition. The 2021 date is research from the same 10-Q and cannot be verified from the run outputs (statements.json's FY2021 PaymentsToAcquireBusinessesGross of $41,769,000 is consistent with it but does not name the business).
- Florida and coastal concentration: hurricane restoration lifted FY2023 capital improvements to $317,086,000, and insurance costs move in cycles.
- External growth is constrained (management says transaction activity is limited). Per-share growth rests on internal rent escalation.

Moat 6 gives a CAP of 9.8 years: growth holds for 2 years, then fades to the 2.50% terminal rate.

## DCF — final run (2026-10-19)
**Why growth was recalibrated.** The engine's blend is 11.72% (g_base 11.72%). It is the median of four components; the share-count CAGR of 0.82% (growth adj −0.82%) is applied to the three revenue components only (dcf_numbers.json `growth_components_adjusted`):

| Component | Filed value | After share adjustment | Problem |
|---|---|---|---|
| rev CAGR 5y | 134.22% | 133.39% | Pure tag artefact (see BASIS_BREAK_SUSPECT below) |
| OE/share CAGR 2y | 22.37% | 22.37% (not adjusted) | Starts from FY2023, the hurricane-elevated capital-improvements year ($213,086,000 of OE vs $326,805,000 in FY2025) |
| rev CAGR 3y | 1.90% | 1.08% | None — clean filed print |
| latest rev YoY | 0.34% | −0.48% | None — clean filed print |

Because the artefact is in the set, the median is the midpoint of the 22.37% OE/share CAGR and the 1.08% share-adjusted 3-year revenue CAGR. That is not a growth rate this business has shown, so the scenario offsets were set to land each start on a print or on the company's own guidance.

**Scenario starts.** Offsets of −0.1172 / −0.0972 / −0.0732 / −0.0572 / −0.0402 against g_base give starts of 0.0% / 2.0% / **4.4%** / 6.0% / 7.7%. Each is checked against the prints and guidance:
- **Base 4.4%:** the midpoint of the 2026 property-operating-revenue guidance (+3.9–4.9%; Q2 2026 earnings release, research, cannot verify from the run outputs — judgment.json carries only the MH and RV/marina base-rent guidance). It sits below the guided +6.0% growth in core income from property operations and below MH base-rent guidance (+5.2–6.2%), so it is not above the company's own guidance. It is above the filed revenue prints (3-yr CAGR 1.90%, FY2025 YoY 0.34%), which RV-transient and home-sales softness held down.
- **Bull 6.0%:** the midpoint of the core property-operating-income guidance (+5.5–6.5%; Q2 2026 earnings release, research, cannot verify from the run outputs). It is deliberately below Q2 2026's +7.7% Normalized FFO print (same release). That quarter was lifted by one-off expense savings (Texas real-estate-tax appeals and utilities; expenses 120 bp under guidance — Q2 2026 earnings-call coverage listed under Sources, MarketBeat article dated 2026-07-23; cannot verify from the run outputs), and the six-month print was +3.6% (Q2 2026 earnings release).
- **Super bull 7.7%:** the Q2 2026 Normalized FFO per-share growth (+7.7%, Q2 2026 earnings release; cannot verify from the run outputs) sustained.
- **Bear 2.0%:** near the top of the RV/marina base-rent guidance (+1.1–2.1%, judgment.json) and above both filed revenue prints (3-yr CAGR 1.90%, FY2025 YoY 0.34%; key_numbers.md).
- **Super bear 0.0%:** rent regulation or an adverse antitrust outcome caps MH rent increases while RV keeps shrinking.

**Other inputs.**
- Probabilities: 10/30/30/20/10. Five points moved from bull to bear against the default 10/25/30/25/10, for HIGH_NET_DEBT (net debt / normalized OE 10.19x) and OE_VOLATILE ("widen bear weight").
- OE multipliers: default 0.75 / 0.90 / 1.00 / 1.10 / 1.25.
- Terminal growth: default 2.50% (no `--gterm`, no `--mults`).
- Price: $61.21.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IV@12 | IRR |
|---|---|---|---|---|---|---|---|
| Super bear | 10% | 0.0% | 0.75 | Rent regulation / antitrust remedy caps MH increases; RV keeps shrinking | $9.01 | $11.76 | 4.27% |
| Bear | 30% | 2.0% | 0.9 | RV/marina drag persists; MH increases slow toward inflation | $11.82 | $15.53 | 4.90% |
| Base | 30% | 4.4% | 1.0 | Revenue grows at the 2026 guide, fading over the CAP | $14.61 | $19.35 | 5.55% |
| Bull | 20% | 6.0% | 1.1 | Core NOI growth at the 2026 guide holds; RV recovers | $17.26 | $22.97 | 6.16% |
| Super bull | 10% | 7.7% | 1.25 | Q2 2026's per-share growth sustained | $21.16 | $28.30 | 7.04% |

- **Probability-weighted:** IV@15% $14.40 (upside −76.5%); IV@12% $19.06 (−68.9%); IV@10% $24.26. Weighted IRR **5.51%**; base-case IRR 5.55%.
- **Tier by numbers: D.**
  - IRR band: bear 4.90% (tier D) → bull 6.16% (tier D); scenario range 4.27% – 7.04%.
  - Hurdle-clearing prices: 15% at $14.40, 20% at $10.20, 25% at $7.88.
- **Diagnostics (key_numbers.md):** OE yield 2.67%; TV share @15% 18.4%; scenario spread 2.35x; net debt / normalized OE 10.19x; 9.6 months since FY end.

## Flags — every fragility flag resolved
The final run raises six flags: STALE_FY, BASIS_BREAK_SUSPECT, OE_VOLATILE, SBC_TAG_RECONCILED, SECTOR_MODEL_MISMATCH and HIGH_NET_DEBT.

**STALE_FY** (FY ended 10 months ago). Resolved: the base is ttm.json's TTM through Q1 2026 ($1.64/share), with the legs quoted above.
- ttm.py could not reach Q2 2026. The Q2 10-Q (period 2026-06-30, filed 2026-07-28) is on EDGAR but not yet in EDGAR companyfacts. fundamentals.py and statements.py both warn that their columns stop at 2026-03-31.
- The one-quarter lag cannot move the tier:
  - the TTM and the 3-year median are nearly identical ($1.64 vs $1.63);
  - the Q2 2026 earnings release (8-K exhibit 99.1, filed July 23, 2026) shows six-month non-revenue-producing improvements running above the prior year ($44.9M vs $38.6M; research, cannot verify from the run outputs);
  - even the super-bull scenario (7.04%) stays inside the D band.

**BASIS_BREAK_SUSPECT** (>60% revenue jump). A tag break, not a business event: there was no divestiture, merger or restatement.
- For FY2017–FY2020 the engine's revenue tag (RevenueFromContractWithCustomerExcludingAssessedTax) carries only an ASC 606 slice of revenue: $14,132,000 / $15,191,000 / $19,111,000 / $21,739,000 in the CSV, against $1,316,403,000 from FY2021.
- The filed total (Revenues, statements.json) runs smoothly: $925,312,000 (FY2017), $986,653,000, $1,037,256,000, $1,118,803,000 (FY2020), $1,316,403,000 (FY2021), up to $1,531,382,000 (FY2025).
- The engine's 134.22% rev CAGR 5y is therefore an artefact, and no scenario start relies on it: the starts come from the 2026 guidance and the FY2025 / 3-year prints. The 3-year CAGR (1.90%) and latest YoY (0.34%) both lie inside the clean FY2021+ series.

**OE_VOLATILE** (OE/share spans >3x over 5 years). One cause: FY2022's history-year capex.
- The engine's test (dcf_engine.py, `pos_oe`) compares only the positive OE/share years among the last five. FY2021's negative OE (−$105,939,000, −$0.549/share in the CSV, after the $398,000,000 PaymentsToAcquireProductiveAssets figure) is therefore not part of it.
- The flag fires on FY2022: CSV oe_conservative $83,237,000, OE/share $0.4263, lowered by the $132,800,000 PaymentsToAcquireProductiveAssets figure that looks like an acquisition. FY2024's CSV OE/share of $1.7600 is 4.13x that.
- FY2023's hurricane-elevated capital improvements ($317,086,000) do not fire it. On capital-improvement-only years (statements.json owner_earnings_per_share FY2021–25: $1.514 / $1.115 / $1.090 / $1.760 / $1.633) the range is 1.61x, inside the 3x test.

The base (3-yr median $1.63) and the TTM ($1.64) use capital-improvement-only years. As the flag asks, the bear weight is widened from the default 25% to 30%.

**SBC_TAG_RECONCILED** (new in 5.5).
- FY2019 ($10,481,000 vs $10,500,000, +0.2%) is tag rounding.
- FY2022: the engine used $10,500,000 (Allocated) over $8,760,000 (Share), +19.9%. statements.json shows the cash-flow addback (ShareBasedCompensation) at $8,760,000, so the reconciled figure is a rounded note-level total. It charges more SBC, which is conservative.
- Both years are outside the base window and the OE/share CAGR window:
  - FY2023–25 use ShareBasedCompensation (`sbc_provenance`: Share ≥ Allocated in all three years, not reconciled);
  - `used_tags.sbc` is ShareBasedCompensation;
  - ttm.json's `sbc_reconciled_legs` is empty.
- The reconciliation changes neither the base, the growth starts nor the tier.

**HIGH_NET_DEBT** (net debt 10.2x normalized OE; key_numbers.md 10.19x). Real, but the multiple is high mainly because conservative OE charges every dollar of capital improvements.
- Measured against cash earnings before growth capex, the filer reports 4.4x debt / Adjusted EBITDAre, 5.6x interest coverage and debt at 20.5% of total market cap.
- The debt is mostly fixed-rate secured mortgages (Q2 2026 release and call coverage).
- The bear cases are stressed: 40% of the weight sits on bear-or-worse, and even the bull case earns only 6.16%.

**SECTOR_MODEL_MISMATCH** (Real Estate). Confidence is **low**, and the ranking lists ELS under sector misfits (score.json `model_fit` misfit).
- The OCF − capex − SBC base understates a REIT's distributable earnings as the sector measures them. FFO adds back all capex, and the 2026 Normalized FFO guidance of $3.13–3.23/sh (Q2 2026 earnings release; research, cannot verify from the run outputs) is about twice the $1.64 OE base.
- The tier treatment is in the next section.

**Not raised in the final run: WIDE_SCENARIO_SPREAD.** An earlier same-day run applied the default offsets to the artefact-inflated 11.72% blend and raised it; the offsets were recalibrated to the guidance-anchored starts above for the reasons given under DCF, and on the final starts the scenario spread is 2.35x.

## Sector misfit and the tier
- **The policy:** the standing rule (Andrew, 2026-10-15) sizes a sector misfit's final tier one notch below its numbers tier, with a reason that carries a number.
- **At ELS:** the numbers tier is **D**, and there is no notch below D. `tier_override` is null and the final tier is D.
- **The misfit reading does not rescue a higher tier.**
  - On the conservative base the 15%-hurdle price is $14.40, and in this model IV is proportional to the base.
  - Even a base twice as large (roughly the FFO measure, which charges no capex at all) would leave the 15%-hurdle price far below $61.21.
  - The bull scenario, with growth at the guided core-NOI rate and a 1.1× OE multiplier, earns 6.16%.
- **Direction of the method's error:** the policy's notch exists because OCF overstates earnings at misfits. At ELS the method errs the other way (all growth capex is charged), and the result is still nowhere near the C band.
- **Alerts:** score.json sets `alert_eligible` and `exit_alert_eligible` false (exit alert suppressed: sector model misfit).

## My thoughts / overlay
- **A high-quality franchise priced as one.** At $61.21 the conservative OE yield is 2.67%. The price assumes FFO-style accounting (capital improvements treated as discretionary) plus mid-single-digit growth for a long time. On owner's-earnings terms the weighted IRR is 5.51%, and the whole bear→bull band is Tier D.
- **What would change the answer:**
  - a price near the $14.40 hurdle, which is not plausible for this asset base; or
  - evidence that most of the $237,091,000 of capital improvements is optional growth spending that could stop without hurting rent growth. Even then, the FFO-based arithmetic above stays well short of 15%.
- **Risks to watch:**
  - the Datacomp ruling on the renewed motion to dismiss;
  - rent-control initiatives;
  - hurricane seasons (restoration capex and insurance renewals; premiums fell 18% at the April 2026 renewal per the Q2 2026 earnings-call coverage listed under Sources, MarketBeat article dated 2026-07-23; cannot verify from the run outputs);
  - weakness in transient RV demand;
  - refinancing a $3.3B debt stack at higher coupons.

## Open items for Andrew and the next run
None of these can move the tier: the whole scenario range (4.27% – 7.04%) sits inside the D band.
- **History-year PaymentsToAcquireProductiveAssets.** Ruling 4's additive components sum $398,000,000 (FY2021) and $132,800,000 (FY2022) into capex beside capital improvements. The worker should check the FY2021 and FY2022 10-K investing sections to see whether these are real-estate acquisitions; cannot verify from the run. They affect only OE_VOLATILE and the OE-positive count (4/5).
- **TTM refresh.** Re-run ttm.py and the engine once the Q2 2026 10-Q (period 2026-06-30) reaches EDGAR companyfacts, which clears the one-quarter lag behind STALE_FY.
- **TTM SBC rule (decision for Andrew).** `_system/README.md` known limitation (14) lists ELS among the folders whose TTM SBC would move under the per-span tag alternative. This run's TTM uses ShareBasedCompensation on all three legs ($7,066,000) with no ttm.py warning.

## Data and enrichment
- **Enrichment run (2026-10-19):** fundamentals.py, prices.py, segments.py, statements.py, profile.py and reprice.py all completed.
- **Warnings recorded, none blocking:**
  - fundamentals.py / statements.py: the latest 10-Q (period 2026-06-30) is not yet in EDGAR companyfacts, so columns stop at 2026-03-31.
  - prices.py: the intraday chart request returned no usable points; the daily series was kept.
  - profile.py: no employee-headcount sentence was found in the FY2025 10-K.
  - reprice.py: live.json delta 0.0pp, tier unchanged.
- **Overrides:** none in judgment.json. `overrides_applied` is empty, `override_checks` is empty and the override registry has no ELS entries.

## Final verdict
- **Final tier: D.** Weighted IRR 5.51%, band D→D, numbers tier D. The misfit notch cannot go below D.
- **Confidence: low.** Sector model mismatch: an OE/capex DCF fits REITs poorly. Every flag is resolved above.
- **One-liner:** Best-in-class manufactured-housing / RV landlord, moat 6/10 — but conservative owner's earnings (OCF less all capital improvements and SBC) are only $1.64/sh TTM against a $61.21 price: weighted IRR 5.51% (IV@15% $14.40), bear→bull band D→D, and the price would have to fall to ~$14 to clear the 15% hurdle; confidence low (REIT sector misfit — FFO-based measures read richer, but not near 15%).

## Engine 5.5 re-score (2026-10-19)
**Old (engine 5.4.0, 2026-10-18; origin/main's record):** base OE/share **$2.82**, weighted IRR none, tier **none (blocked)**.
- That run's dcf_numbers.json printed the base (median_of_last_3_fy_oe_per_share, 2.8178738) next to `data_gap` ["capex"], so it emitted no IRR and no tier.
- The base is invalid: it was built on FY2023–25 capex read as $0.
  - FY2023 took a $0 `PaymentsToAcquireOtherProductiveAssets` fact.
  - FY2024 and FY2025 had no capex tag (assumed zero), which raised `DATA_GAP:capex`.
- The worker blocked the name `NEEDS_MAIN_AGENT: capex`. No prior score or analysis existed.

**New (engine 5.5.0):** base OE/share **$1.64** (ttm_json; normalized 3-yr median $1.63), weighted IRR **5.51%**, tier **D**. Numbers tier D, final tier D; band bear 4.90% → bull 6.16%, both D.

**What engine 5.5 changed for this filer:**
- **Capex tags (ruling 3).** `PaymentsForCapitalImprovements`, ELS's only capex line, joined the capex component list in dcf_engine.py and ttm.py.
  - Capex now reads $317.1M (FY2023), $241.3M (FY2024) and $237.1M (FY2025) (key_numbers.md capex basis).
  - ttm.json reads all three TTM capex legs from the same tag.
  - Under 5.4, FY2024–25 had no capex at all; that was the gap.
- **Zero-guard (ruling 3, sub-decision (a)).** Under 5.4, FY2023's $0 `PaymentsToAcquireOtherProductiveAssets` fact supplied a $0 capex for the year. It now contributes 0 beside $317,086,000 of capital improvements (`capex_provenance` FY2023, source components_mixed_filings). `_system/README.md`'s retro-check lists ELS FY2023 as one of exactly two last-3-FY periods the guard changes.
- **Additive components (ruling 4).** With no PP&E roll-up filed, each year's capex is the sum of the filed components.
  - FY2023–25: the capital-improvements line (plus the $0 fact in FY2023).
  - FY2017–22 (history years): it also sums PaymentsToAcquireProductiveAssets, which I cannot verify as capex (see Capex completeness and Open items). This affects only OE_VOLATILE and the OE-positive count, not the base, growth or tier.
- **Intangible purchases (ruling 5).** None are filed (intangibles $0.00 each year).
- **SBC tag (ruling 6).** SBC_TAG_RECONCILED fires for history years FY2019 and FY2022 only. The latest year's `used_tags.sbc` is ShareBasedCompensation, and no TTM leg is reconciled.
- **Share basis (ruling 2).** No defect.
  - `share_scale.defect` is false: latest diluted count 200,114,000 vs cover-page count 193,937,553 (dei 2026-04-22).
  - No split adjustment and no SHARE_BASIS_DIVERGENCE.
  - `share_basis.in_history_split_facts` lists three 2-for-1 facts (2013-09-30, 2014-03-31, 2019-10-15). There were only two splits:
    - statements.json applies only the 2013-09-30 and 2019-10-15 splits;
    - its split-adjusted diluted counts show no doubling in 2014;
    - so the 2014-03-31 fact repeats the 2013 split.
  - All three facts are informational only.
  - The CSV's FY2016 count (92,569,000, vs 186,850,000 in FY2017) is on the pre-2019-split basis, outside every window the engine uses.
- **Market cap (ruling 1).** Basis diluted_latest, price × shares, no ADS ratio: $12.249B, in scope.
- **USD-override branch (ruling 7).** Not applicable. ELS is a USD 10-K filer with no overrides (`override_checks` empty, `fx_conversion` null).

**New 5.5 flags, resolved by name:**
- **SBC_TAG_RECONCILED** — resolved under Flags. FY2019's +0.2% is tag rounding. FY2022's $10,500,000 note-level figure over the $8,760,000 cash-flow addback is conservative and outside the base window.
- **Not raised:** CAPEX_COVERAGE_LOW (capex exceeds D&A in FY2023–25), SHARE_SCALE_SUSPECT, SHARE_BASIS_ADJUSTED, SHARE_BASIS_DIVERGENCE, and OVERRIDE_SUPERSEDED_BY_FILED_TAG:capex (no capex override exists).
- **Newly visible because a tier now exists:** HIGH_NET_DEBT (10.19x net debt / normalized OE), resolved under Flags.

**Why the tier is D.** With complete capex, the conservative OE yield is 2.67%. With growth starts anchored on the 2026 guidance, the weighted IRR is 5.51%. The scenario range is 4.27% – 7.04%, so not even the super-bull case reaches the C band. The 2026-10-15 misfit policy would size the final tier one notch below the numbers tier, but there is no notch below D. `tier_override` is null and the final tier stays D.

## Sources (research)
- Q2 2026 results, 8-K exhibit 99.1 (report date 2026-07-22, filed 2026-07-23, accession 0001628280-26-049302 per profile.json): https://www.sec.gov/Archives/edgar/data/0000895417/000162828026049302/elsex9912q26.htm
- Q2 2026 call coverage: https://www.nasdaq.com/articles/equity-lifestyle-properties-q2-earnings-call-highlights and https://www.marketbeat.com/instant-alerts/equity-lifestyle-properties-q2-earnings-call-highlights-2026-07-23/
- Q2 2026 10-Q (Datacomp litigation status; period 2026-06-30, filed 2026-07-28, accession 0001628280-26-050244 per profile.json): https://www.sec.gov/Archives/edgar/data/0000895417/000162828026050244/els-20260630.htm
- Datacomp case interim co-lead counsel: https://www.hausfeld.com/news/hausfeld-appointed-interim-co-lead-counsel-in-nationwide-antitrust-case-impacting-manufactured-home-owners
- 2026 dividend and risk summary: https://quartr.com/events/equity-lifestyle-properties-inc-els-q2-2026_ozHYVWB5
