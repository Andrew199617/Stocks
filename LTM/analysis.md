# LTM — LATAM Airlines Group S.A.
Engine 5.4 run, 2026-10-17. **ADS basis (read first):** each ADS represents **2,000 ordinary shares** (FY2025 20-F cover/ADS description; ratio changed from 1:1 on July 24, 2024). judgment.json carries a filing-sourced `ads_ratio` of 2000 and the engine scaled every per-share figure ×2000: all OE/share and IV figures below are **per ADS**, directly comparable to the $47.47 price. All figures are copied from key_numbers.md, dcf_numbers.json, or financials_history.csv — none are recomputed.

## What it is
Latin America's largest airline group (SIC 4512, scheduled air transportation), formed from LAN (Chile) and TAM (Brazil): passenger operations across Chile, Brazil, Peru, Colombia and Ecuador plus international long-haul, the LATAM Pass loyalty program, an antitrust-immunized joint venture with Delta, and LATAM Cargo. It went through Chapter 11 in 2020 and emerged on November 3, 2022 with a full recapitalization. It reports in USD under IFRS on Form 20-F (FY2025 filed 2026-03-05).

## Owner's earnings
**FY2025 (20-F via EDGAR, from financials_history.csv):** operating cash flow $3,737,096,000; capex (purchases of property, plant and equipment) $1,775,818,000; equity SBC $0 — by filing override, see OVERRIDES.
- **Conservative owner's earnings FY2025: $1,961,278,000 = $6.66/share (per ADS, key_numbers.md latest FY OE/share)**
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $2,176,645,000 — same ballpark, modestly above the conservative figure.
- OE positive 3 of the last 5 fiscal years: FY2021 and FY2022 were negative (COVID / Chapter 11), FY2023–FY2025 positive at $1,467,781,000 / $1,780,864,000 / $1,961,278,000 (financials_history.csv OE totals, before the per-share ADS scaling).
- Net debt $5.938B (key_numbers.md): Borrowings of $8,088,526,000 less cash $2,150,113,000 (financials_history.csv). The filing's own financing-liabilities reconciliation (Note 34 of the December 2025 statements) shows that Borrowings total includes a lease liability of $3,792,861,000 — the fleet lease book is inside the debt figure, not hidden from it. The company reported adjusted net leverage of 1.5x and liquidity of $3.7B (25.7% of LTM revenue) at year-end 2025 in its 2025 results reporting.
- **Base used = the engine's normalized base, median of the last 3 FY OE/share: $6.04/share** (base_source: median_of_last_3_fy_oe_per_share). No TTM base: ttm.py cannot compute TTM for this IFRS filer (it reads us-gaap tags only and exited non-zero this run), so per the worker spec the median base stands. The median year is FY2024.

## OVERRIDES — sbc, shares, ads_ratio (the preliminary run exited 4, DATA_GAP)
- **SBC = $0, kind "filing":** EDGAR carries no SBC fact for LATAM under any tag the engine reads, in any year. That is because there is no equity-settled SBC to file: Note 33 of the December 2025 statements (filed with the FY2025 20-F) describes the company's only share-based program, the CIP created on exit from Chapter 11, as a **cash-settlement award** under IFRS 2 — synthetic units paid in cash, carried as a liability, remeasured through profit or loss in Administrative expenses. Its cost is already inside operating cash flow; deducting it again as SBC would double-count. Same treatment as SQM and TS in this sweep.
- **Shares = 589,306,002,483 diluted, kind "filing":** EDGAR tags only the basic WeightedAverageShares count, which the engine records as a fallback and (v5.4) refuses to silently swap for diluted. Note 29 (Earnings Per Share) of the same statements prints the diluted count: basic 589,302,090,735 plus 3,911,748 shares on assumed conversion of the Chapter 11 exit convertible notes = **589,306,002,483** for FY2025 (FY2024 diluted 604,441,789,335 in the same table). The engine applies the single FY2025 value to every gap year; for FY2024/FY2023 that is a smaller denominator than the filer's own, raising those years' OE/share — measured impact below.
- **ADS ratio = 2000, filing-sourced** (see header).
- **Measured impact (key_numbers.md, overrides toggled off at the same final configuration):** base OE/share $5.89 → $6.04 (+2.57%); weighted IRR 20.97% → 22.40% (+1.44pp). The SBC leg contributes nothing (zero-fill equals the filing figure of $0); the whole measured lift is the shares denominator. Unblocks tier: YES — without the overrides the data gate blocks scoring entirely, and score.json therefore records the alert as suppressed ("tier exists only because of a judgment override"). Note the tier does not depend on the overrides' economics: even on the zero-fill baseline the weighted IRR is 20.97%, still Tier A.

## Moat: 4/10 — weak-to-moderate, in a structurally bad industry
Justification: airlines are close to moat-less — commodity product, minimal switching costs, and an industry that destroyed capital through the last cycle; LATAM itself filed Chapter 11 in 2020 and printed negative owner's earnings in FY2021–FY2022. Evidence first (fundamentals.json): roic_proxy ran 3.3% / 6.4% / 8.0% / 4.0% in 2016–2019, −39.4% / −93.7% in 2020–2021, then 21.5% / 18.6% / 25.7% / 29.0% in 2022–2025. The recent strength is real but sits on a bankruptcy-written-down capital base (equity was $31M in FY2022, rebuilding to $1,337M in FY2025), so it does not establish a through-cycle moat at 7+. Gross margin expanded from 24.3% (FY2023) to 25.5% (FY2024) to 29.2% (FY2025).
- FOR: dominant South American network — hubs at Santiago, Lima and São Paulo/Guarulhos and leading positions in the Chilean, Peruvian, Colombian, Ecuadorian and Brazilian domestic markets; LATAM Pass loyalty plus the Delta joint venture; cargo leadership in South America (about 30% regional share, per company/industry reporting) on the same network; post-Chapter 11 cost and fleet reset visible in the margin expansion above.
- AGAINST: commodity, price-shopped product with low passenger switching costs; through-cycle ROIC is poor (above); cyclicality is proven, not theoretical (Chapter 11, OE positive only 3 of the last 5 years); fuel and FX exposure — costs largely USD against BRL and other local-currency revenue, and 2026 guidance was cut then reinstated around a fuel shock; rivals GOL and Azul are resetting their own cost bases in Chapter 11 (2025), eroding LATAM's cost edge; Brazilian tax/contingency overhang (Note 30 of the statements).
- A 4 gives CAP = 7.2 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 7.2 years, 15-year projection.

## DCF — final run (2026-10-17)
Growth sanity check (mandatory): the blend is 15.32% (components: rev CAGR 5y 29.46% · rev CAGR 3y 15.07% · latest rev YoY 11.16% · OE/share CAGR 2y 15.58%). The 5y CAGR is a COVID/Chapter 11 artifact — it runs off the 2020–21 collapse and the November 2022 emergence — and the 3y CAGR spans the post-emergence ramp; neither is a forward growth rate, and both are investigated under BASIS_BREAK_SUSPECT below rather than trusted. The scenario design therefore keeps the blend as the base start (the latest prints — FY2025 revenue +11.16% YoY with OE/share compounding off the reset cost base — do support a low-teens start) but re-weights the tails for an airline at a cyclical high: probabilities 15/25/30/20/10 (super-bear raised from the 10% default) and super-bear/bear OE multipliers cut to 0.65/0.85 in place of the default 0.75/0.90. Starts run 3.3% / 10.3% / 15.3% / 20.3% / 27.3% — the super-bear start at 3.3% still assumes revenue growth in a downturn, which is the deliberate conservatism check in the other direction: the bear machinery bites through the OE multipliers and the fade, not through a negative start the filed record does not support. Price $47.47, all figures per ADS.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | 3.3% | 0.65 | Fuel shock + BRL slide + GOL/Azul post-Chapter 11 price war; OE compresses hard | $33.25 | 11.28% |
| Bear | 25% | 10.3% | 0.85 | Cyclical normalization off the post-restructuring high | $56.73 | 17.28% |
| Base | 30% | 15.3% | 1.00 | Blend start fades over the 7.2-year CAP as the reset cost base matures | $80.43 | 22.58% |
| Bull | 20% | 20.3% | 1.10 | Network + LATAM Pass + Delta JV keep compounding at recent prints | $106.30 | 27.57% |
| Super bull | 10% | 27.3% | 1.25 | Sustained post-emergence trajectory with margin expansion intact | $155.40 | 35.47% |

- **Probability-weighted: IV@15% $80.10 (+68.7% vs price), IV@12% $108.41, IV@10% $140.16, weighted IRR 22.40%, base-case IRR 22.58%**
- **Tier by numbers: A.** IRR band: bear 17.28% (Tier B) → bull 27.57% (Tier S) — see TIER_BAND below. Diagnostics (key_numbers.md): OE yield 12.73%, terminal value 20.5% of IV@15%, scenario spread 4.67x, months since FY end 9.5. Hurdle-clearing prices on the weighted path: 15% at $80.10, 20% at $54.93, 25% at $41.27 — the $47.47 price clears 20% but not 25%.
- The alert is suppressed and badged, by rule: score.json records the tier as existing only because of the judgment overrides (alert_eligible: false). The dependence is on the overrides' *existence*, not their economics — on the zero-fill baseline the weighted IRR is 20.97%, still Tier A (see OVERRIDES for the measured impacts).

## Flags — every fragility flag resolved
- **STALE_FY** (latest FY ended 10 months ago): ttm.py cannot compute a TTM base for this IFRS filer (us-gaap tags only; it exited non-zero this run), so per the worker spec the median FY2023–25 base stands. Interim 2026 evidence — guidance cut then reinstated around a fuel shock — is the cyclicality already priced in the scenario design; nothing in it argues the FY2025-based median overstates run-rate OE.
- **BASIS_BREAK_SUSPECT** (>60% revenue jump/drop in the last 5 years): identified — the COVID collapse, the 2020 Chapter 11 filing and the November 3, 2022 emergence with full recapitalization. That is exactly why the 5y and 3y revenue CAGRs are not trusted as forward starts (see the growth sanity check): the break is in the capital structure and the demand base, both now reset, and the base itself is a 3-year median of post-emergence years (FY2023–25), not a CAGR.
- **NI_OCF_DIVERGENCE** (net income vs OCF differ by >40% in 2023, 2024, 2025): structural for a fleet-growing IFRS airline — heavy D&A on the fleet, lease and financing presentation, and working-capital scale move the two series apart every year, in a consistent direction. The base is OCF-derived, so net-income presentation never enters it; the maintenance version ($2,176,645,000 for FY2025) lands in the same ballpark as the conservative figure ($1,961,278,000), which is the cross-check that the divergence is presentation, not earnings quality.
- **ADS_RATIO_APPLIED** (×2000): each ADS represents 2,000 ordinary shares (FY2025 20-F cover/ADS description; ratio changed from 1:1 on July 24, 2024) — resolved in the header and OVERRIDES; every per-share figure in this analysis is per ADS and comparable to the $47.47 price.
- **SHARES_FALLBACK** (no diluted count filed for 2017–2022): those history years use the basic/outstanding counts recorded in the shares_tag column, so pre-2023 per-share history is approximate. The exposure is confined to the long-history display: the median base window (FY2023–25) uses the filing-sourced diluted override, and the pre-emergence capital structure those years describe no longer exists in any case.
- **OVERRIDE_APPLIED:sbc** ($0, filing): resolved in OVERRIDES — LATAM's only share-based program (the CIP) is cash-settled under IFRS 2, its cost already sits inside operating cash flow, and no equity SBC fact exists in companyfacts under any tag. Deducting it again would double-count.
- **OVERRIDE_APPLIED:shares** (589,306,002,483 diluted, filing): resolved in OVERRIDES — Note 29 of the December 2025 statements. Measured impact: base $5.89 → $6.04 (+2.57%), weighted IRR 20.97% → 22.40% (+1.44pp); the single FY2025 value applied to FY2024 modestly flatters that base year (the filer's own FY2024 diluted count is larger), disclosed in key_numbers.md and sized into the verdict.
- **WIDE_SCENARIO_SPREAD** (super-bull IV 4.7x super-bear IV): genuine for a post-bankruptcy airline at a cyclical high — the honest range runs from $33.25 to $155.40 at IV@15. Confidence is graded low, never high, while this flag stands, and the scenario design already leans against the spread (super-bear probability raised to 15%, bear-case multipliers cut).
- **TIER_BAND** (bear B 17.3% vs bull S 27.6%): the verdict spans three tiers; the final A is the probability-weighted result, and the standing instruction for this name is the one in the verdict — size it like a B, because the base is a cyclical high and the bear case is a B.

## Final verdict
**Tier A — final, with the alert suppressed (override-dependent tier) and confidence low.** Weighted IRR 22.40%, weighted IV@15% $80.10 against a $47.47 price (+68.7%); the price clears the 20% hurdle ($54.93) but not 25% ($41.27). The numbers are post-restructuring numbers: a bankruptcy-reset cost base, three straight years of growing OE ($1.47B → $1.78B → $1.96B), and a 12.73% OE yield — in a structurally weak industry, at what may be a cyclical high, with a bear case at Tier B (17.28%) and a scenario spread of 4.67x. It does not clear 25%, and it should be sized like a B, not an A.

## Engine 5.5 re-score (2026-10-19)
**This was a make_score-only re-score (ruling 1).** `dcf_engine.py` and `ttm.py` were not run. dcf_numbers.json, financials_history.csv and the override registry entries are unchanged. The engine output is still Muse's 2026-10-19 re-run on main with the ADS market-cap fix (`engine_release` 5.4.0). Only make_score 5.5, `prices.py` and `reprice.py` ran. Every figure below is copied from the final key_numbers.md, dcf_numbers.json, financials_history.csv or statements.json, with four labelled exceptions:
- phrases quoted from the dated 2026-10-17 text;
- *audit / review figures*: the 2026-10-19 audit's and its follow-up review's replication of origin/main's engine math on the recorded inputs. These are not engine output. The replication reproduces the recorded weighted IRR (22.40%) and the recorded zero-fill IRR (20.97%) exactly;
- filing figures that appear in no run output, each with its source;
- *reviewer arithmetic* on CSV, statements.json or filing figures, marked where it appears.

Two filings are cited below. They are LATAM earnings releases furnished on Form 6-K and read on EDGAR, and neither appears in any run output:
- **4Q2025 release**, dated February 3, 2026 (accession 0001047716-26-000011). It prints the FY2025 and FY2024 consolidated cash-flow statement (direct method). Its operating cash flow ($3,737,096,000 / $3,106,327,000) and PP&E purchases ($1,775,818,000 / $1,325,463,000) match financials_history.csv exactly.
- **2Q2026 release**, dated August 4, 2026 (accession 0001047716-26-000087). It prints the six-month cash-flow statement and the 2026 guidance table.

| | Before (pre-5.5 score on 5.4.0 output) | After (make_score 5.5, same engine output) |
|---|---|---|
| Base OE/share | $6.04 (median_of_last_3_fy_oe_per_share) | $6.04, unchanged |
| Weighted IRR | 22.40% | 22.40%, unchanged |
| Tier | A (by numbers A, no tier override) | A, unchanged |
| Market cap (est) | $13.987B | $13.987B (basis: diluted_latest), unchanged |
| Scope | in scope | in scope (market cap under $40B); judgment.json not rewritten |
| Net debt / normalized OE | 0.00x (as the engine printed it) | 3.33x on the ADS basis |
| Entry / exit alert | closed: the tier exists only because of a judgment override | closed: engine output predates release 5.5.0, and the tier exists only because of a judgment override |

**What engine 5.5 changed for this filer**
- **Market cap and scope:** no change. Muse's 2026-10-19 engine run already priced the cap as price × shares ÷ ads_ratio: $47.47 × 589,306,002,483 ÷ 2000 = $13.987B. make_score 5.5 found that the cap already divides by the ratio, so it did not divide a second time, and it recorded the basis as `diluted_latest`. LTM is in scope before and after, so judgment.json's `in_scope_under_40b: true` stands with no rewrite.
- **Normalized-OE basis, which is the fix that matters here.** The 5.4.0 engine built the normalized OE total from per-ADS OE × ORDINARY shares. That total was 2,000× too large, so key_numbers.md printed net debt / normalized OE as 0.00x. Under ruling 1's "anything downstream", make_score now prints the ratio on the ADS basis: **3.33x**. score.json records it as `net_debt_to_normalized_oe_ads_basis`. key_numbers.md states that HIGH_NET_DEBT (> 3x) would fire on this basis. The engine's flag list is hashed 5.4.0 output, so it still lists the flags as they were recorded.
- **Override impact:** carried from the prior score.json, not re-measured, because the engine output is release 5.4.0 and the current release is 5.5.0. Base OE/share $5.89 (no override) → $6.04 (with override), +2.57%. Weighted IRR 20.97% → 22.40% (+1.44pp). Unblocks tier: YES. Open item 3 shows where in the engine that +1.44pp actually arises.
- **Not applied, because the engine did not run:** the capex tags, the SBC tag rule, the share-basis checks and the USD-override branch. The list further down says what each would do on a re-run.

**New 5.5 flags, resolved by name**
- **HIGH_NET_DEBT (ADS basis 3.33x; would fire; not yet in the engine's flag list).** The engine's 0.00x was the artifact. 3.33x is the leverage on the per-ADS basis:
  - Net debt of $5.938B is the IFRS Borrowings total less cash (`net_debt_basis` TOTAL:Borrowings). dcf_numbers.json records no separate lease liability (`lease_liabilities_latest` is null).
  - The 2026-10-17 Owner's earnings section says, citing Note 34 of the December 2025 statements, that this Borrowings total includes the fleet lease liability. That is a filing figure that appears in no run output, so it cannot be verified from the diff. The flag does not depend on it. If the leases sat outside Borrowings, net debt would be larger and the ratio higher, so HIGH_NET_DEBT applies either way. Note 34 only decides whether the aircraft lease book is inside the 3.33x or on top of it.
  - Debt feeds diagnostics only in this engine, so no IV or IRR moves.
  - The flag asks for stressed bear cases. They already are stressed:
    - super-bear: 15% probability at a 0.65 OE multiplier ($33.25 IV@15, 11.28%);
    - bear: 25% at 0.85 ($56.73, 17.28%).
  - "Levered OE can vanish fast" has already happened at this company: the 2020 Chapter 11.
  - **Method limit.** The 4Q2025 release's cash-flow statement puts both lease payments and interest paid under financing:
    - payments of lease liabilities: $344,038,000 (FY2024) and $463,358,000 (FY2025);
    - interest paid: $717,634,000 (FY2024) and $600,740,000 (FY2025).
    - The OE base (OCF − capex − SBC) therefore deducts neither. Ruling 5 rejected a lease leg and an interest leg, so this leverage diagnostic and the sizing instruction are the only places those payments show up in the record. NI_OCF_DIVERGENCE below gives their size.
  - **Resolution:** the flag supports the existing sizing instruction (size like a B). It does not change the tier, and confidence stays low.
- **BIG_NET_CASH:** does not apply. Net debt is positive on either basis.
- **Alert gates (a new make_score 5.5 rule, not a flag):** `alert_eligible` and `exit_alert_eligible` are both false, with the reason "engine output predates release 5.5.0 — re-run the engine before an entry alert". This is expected. make_score 5.5 closes both gates on all pre-5.5 output, so a cap or ratio correction cannot create an alert by itself. The entry alert was already suppressed because the tier depends on an override; the new reason sits beside that one. Both gates stay closed until the engine is re-run on 5.5.

**Pre-5.5 flag and check re-done in this pass**
- **NI_OCF_DIVERGENCE (2023, 2024, 2025): resolved. The divergence is structural, not a one-off.** This replaces the 2026-10-17 resolution, whose cross-check is withdrawn (see the corrections below).
  - *Reviewer arithmetic on CSV figures:* OCF less net income is $1,682,018,000 / $2,128,882,000 / $2,273,535,000 for FY2023 / FY2024 / FY2025. Net income here is the CSV's consolidated `net_income` (tag ProfitLoss).
  - Fleet D&A explains most of the gap. The CSV `da` of $1,205,373,000 / $1,447,656,000 / $1,736,098,000 is 72% / 68% / 76% of it.
  - The rest is $476,645,000 / $681,226,000 / $537,437,000. In every year it is below finance costs (statements.json FinanceCosts $698,231,000 / $881,950,000 / $721,416,000).
  - That fits how LATAM classifies its interest flows. The 4Q2025 release's cash-flow statement puts interest paid under financing and interest received under investing (read for FY2024 and FY2025; FY2023 was not read).
    - Finance costs are expensed in net income, but no interest is paid out of OCF.
    - Finance income is in net income (statements.json FinanceIncome $125,356,000 / $142,411,000 / $146,275,000), but the interest is received outside OCF.
  - *Reviewer arithmetic:* after D&A, finance costs and finance income, what is left of the gap is −$96,230,000 / −$58,313,000 / −$37,704,000. Tax, provisions and working capital therefore net to less than 6% of the gap in each year, and no year carries a one-off.
  - **Consequence for the base:** none. The base is OCF − capex − SBC. It deducts capex in full instead of D&A, and it never used net income.
  - **Method limit (ruling 5: no interest leg, no lease leg):** the same classification keeps interest paid ($717,634,000 in FY2024, the median base year; $600,740,000 in FY2025) and lease principal ($344,038,000 / $463,358,000) out of the base. Part of the fleet D&A is right-of-use depreciation, and its cash cost is that lease principal. The run outputs do not split it.
    - *Reviewer arithmetic:* interest paid plus lease principal is more than half of each year's OE total ($1,780,864,000 / $1,961,278,000).
    - This is why the 3.33x leverage and the "size like a B" instruction matter here. It is a limit of the method, not a defect a worker can fix.
- **Guidance check (WORKER_SPEC step 6): done. The base start sits above guidance.**
  - **Source:** the 2Q2026 release's guidance table. It has three columns: original (December 3, 2025), prior (May 5, 2026) and updated (August 4, 2026).
    - The May column cut adjusted EBITDA to US$3.80–4.20B from US$4.20–4.60B and carried fewer metrics. Its jet-fuel assumption was $170/bbl for Q2–Q3 and $150 for Q4, against $90 in December.
    - The August update describes itself as "reinstating its full set of guidance parameters".
    - This sources the 2026-10-17 phrase "cut then reinstated around a fuel shock".
  - **Updated 2026 guidance (August 4, 2026):**
    - total ASK growth of 9.0%–10.0% vs 2025;
    - revenues of US$17.3–17.7B;
    - adjusted operating income of US$2.10–2.30B, at an adjusted operating margin of 12.0%–13.0%;
    - adjusted EBITDA of US$4.10–4.40B;
    - jet fuel at $147/bbl (Q3) and $130 (Q4).
  - **FY2025 as reported (4Q2025 release):** adjusted operating income of US$2,355M at a 16.2% adjusted operating margin.
  - **Latest quarter (2Q2026, same release):** revenue +27.6% year on year, on ASK +8.9%.
  - **Against the model.** The base start of 15.3% (g_base 15.32%) applies to OE/share. The latest rev YoY is 11.16%.
    - Capacity: guided ASK growth of 9.0%–10.0% sits below the start, and below the latest rev YoY.
    - Profit: guided adjusted operating income is 2%–11% below FY2025's US$2,355M, and the guided margin is 3.2–4.2pp lower (*reviewer arithmetic*). The base path's first-year OE/share is $6.97 (dcf_numbers.json `paths.base`), above the latest FY OE/share of $6.66.
    - Revenue: guided revenue is 21%–24% above FY2025's $14,265,056,000 (*reviewer arithmetic*). This is the only measure above the start. With capacity up 9%–10% and the margin guided down, that revenue growth does not reach profit in the company's own numbers.
  - **Result:** the base start sits above the company's latest guidance on capacity and on operating profit. Under AGENTS.md that is a finding against the scenario offsets. Ruling 1 bars changing offsets in this pass, so it is carried to the re-run as open item 2.

**Pending: what a 5.5 engine re-run would change (none of this is applied)**
The source is the retro-scan, which compares the branch engine with origin/main's engine on recorded inputs.
- **Normalized-OE basis (decision 1):** the re-run computes `normalized_oe_total` = OE/share × shares ÷ ratio, so HIGH_NET_DEBT enters `fragility_flags` at the ratio above. That run must resolve it by name.
- **Intangible capex (decision 5):** in the engine's window, LATAM files the IFRS `PurchaseOfIntangibleAssetsClassifiedAsInvestingActivities` line for FY2016–FY2018 only. The re-run adds it on top of the PP&E leg in those years. The tag is absent for FY2019–FY2025, and decision 5 adds only filed facts, so this rule would not move the median window or the base. LATAM did not stop buying intangibles: its cash-flow statement still carries the line, under no tag the engine reads (open item 4).
- **Additive components (decision 4):** the PP&E roll-up `PurchaseOfPropertyPlantAndEquipmentClassifiedAsInvestingActivities` is filed every year and is authoritative, so the component sum never engages.
- **Capex coverage:** LTM is not in the CAPEX_COVERAGE_LOW hit list.
- **SBC (decision 6):** LTM files no SBC tag (`used_tags.sbc` is null), so there is nothing for the Allocated-vs-Share rule to compare. The $0 filing override (cash-settled CIP, Note 33) keeps filling the gap, and LTM is not in the dual-tag retro-scan.
- **USD-override branch (decision 7):** LTM reports in US dollars and the engine converts nothing (`fx_conversion` is null), so the branch never engages. The $0 SBC override needs no `currency` declaration, and the shares override is a count, not a money figure. No restatement is needed, unlike HTHT's RMB capex override.
- **Share basis (decision 2):**
  - The latest cover-page count sits inside the ±25% divergence band around the diluted override. The retro-scan lists no share-basis action for LTM: neither SHARE_BASIS_ADJUSTED nor SHARE_BASIS_DIVERGENCE fires.
  - The share-scale guard does not fire either: the $6.04 base is nowhere near 20× the $47.47 price.
  - A cover-page count of 0 is no longer offered as a share fallback, so FY2017 leaves the SHARES_FALLBACK list. No number moves, because every row uses the override count.
- **Override counterfactual:** it is re-measured through the 5.5 engine on the re-run instead of being carried.
- **Expected result:** the retro-scan lists no `tier_by_numbers` change for LTM. The re-run should confirm Tier A by numbers, unless it acts on open items 2–4.

**Open items (each needs an engine re-run, a ruling, or both; ruling 1 bars applying them now)**
1. **STALE_FY: escalated to Andrew. The interim cash flow has now been read.** Months since FY end: 9.6.
   - The 2026-10-17 resolution follows WORKER_SPEC step 4's rule for IFRS filers: ttm.py reads us-gaap tags only, so the median base stands. Its closing sentence ("nothing in it argues the FY2025-based median overstates run-rate OE") had no figure behind it and stays withdrawn.
   - The interim 6-K does carry a cash-flow statement. The 2Q2026 release prints these six-month figures (6M 2026 against 6M 2025):
     - operating cash flow: $1,542,912,000 against $1,540,971,000;
     - PP&E purchases: $673,760,000 against $934,050,000;
     - intangible purchases: $62,165,000 against $47,936,000.
   - Read plainly, first-half OCF was flat year on year while PP&E purchases fell, so the half-year figures do not show run-rate OE falling below FY2025's. Two things could change that: aircraft deliveries can shift capex into the second half, and guidance points to lower 2026 operating profit (guidance check above). These are filing figures, not run outputs, so none of this is a TTM base.
   - A worker cannot pin a 6-K-based TTM base: a `base_override` may be built only from figures the run prints, and ttm.py prints none for this filer. That needs either a ruling that admits the 6-K's printed lines, or an IFRS path in ttm.py.
2. **Growth start: the emergence break and guidance.** The base start is 15.3% (g_base 15.32%). It is the median of the four components, which is the midpoint of rev CAGR 3y 15.07% and OE/share CAGR 2y 15.58%. So the 3y CAGR that the 2026-10-17 text calls untrusted sets half the start. The blend is kept as the engine computed it, because ruling 1 bars changing the offsets now. There are two reasons it may sit too high:
   - The two components that do not straddle the November 2022 emergence, latest rev YoY 11.16% and OE/share CAGR 2y 15.58%, would centre the start lower. *Audit figures:* that start is 13.37%. It gives a weighted IRR of 21.28% (bear 16.31%), still Tier A.
   - Guidance sits below the start on capacity and on profit (guidance check above).
   - *Audit / review figures:* the A/B edge is a start of 11.08%. At 11.09% the weighted IRR is 20.004%, still A. Guided ASK growth of 9.0%–10.0% sits below that edge: a start there gives a weighted IRR of 18.86%–19.41%, which is Tier B.
   - The 2026 guidance covers one year, while the model holds the start for two years and then fades it. Either way, the re-run must keep the blend and write down why against these figures, or pass offsets that re-centre the start.
3. **Shares override: its FY2022 fill sits inside the growth window. This is a question for Andrew.**
   - The override fills every year from FY2016 to FY2025 (key_numbers.md, periods filled). The engine's share-count CAGR runs over the last four counts, FY2022 to FY2025.
   - So the override also replaces the filed FY2022 count with 589,306,002,483. The filed count is statements.json `shares_basic` 96,614,464,231, a weighted average that straddles the November 2022 emergence.
   - Filed counts rise 6.3× from FY2022 to FY2023 (to 604,437,869,545); that jump is the emergence share issuance. The CSV hides it because every row carries the override.
   - *Review figures:*
     - On filed counts, the share-count CAGR would be +82.7% a year, DILUTION would fire, and the three revenue components would each take −5pp.
     - Restoring only the FY2022 count gives g_blend 12.82% instead of 15.32%, and a weighted IRR of 20.97% (bear 16.05%): still A, by 0.97pp.
     - The FY2023–FY2025 fills do raise the base by 2.57% ($5.89 → $6.04). But the same denominator lowers the FY2023 endpoint of the OE/share CAGR, so their IRR effect nets to about zero: 22.39% with filed FY2023–25 counts and the override only in FY2022.
     - The whole measured +1.44pp therefore runs through the FY2022 fill.
   - **Question for Andrew:** should a one-time recapitalisation share issuance (the Chapter 11 exit, November 2022) cut forward growth?
     - The worker's reading is no. The issuance is complete and one-off: filed basic counts since are 604,437,869,545 (FY2023) and 589,302,090,735 (FY2025). DILUTION on filed counts would be an artefact, in the same sense WORKER_SPEC step 4 applies to a split-ratio jump inside the window (TPL). On that reading, the flat fill is the better forward basis.
     - Against that, the override's stated rationale (the FY2024 denominator) is not what moves the IRR, and on filed counts Tier A has less than 1pp of cushion.
     - The answer decides whether the 5.5 re-run keeps the flat fill or restates the FY2022 count. Either way, the re-run should rewrite the override's reason text.
4. **Capex completeness: the engine does not read LATAM's intangible-purchase line. Escalated to the main agent.**
   - Capex is the single IFRS PP&E line (`used_tags.capex` PurchaseOfPropertyPlantAndEquipmentClassifiedAsInvestingActivities).
   - The 4Q2025 release's investing section has five lines: sale of PP&E, purchases of PP&E, purchases of intangible assets, interest received, and other cash flows. There is no separate aircraft pre-delivery-payment line.
   - "Purchases of intangible assets" is $104,483,000 (FY2025) and $94,412,000 (FY2024), plus $62,165,000 for 6M 2026.
   - companyfacts carries the IFRS intangible-purchase tag only through FY2018: statements.json `capex_intangibles` is blank from FY2019 to FY2025. The engine's capex therefore leaves the line out, and so would decision 5's additive leg on a re-run. The OE base is overstated by that amount.
   - No override may add to a filed capex value, so this is `NEEDS_MAIN_AGENT: capex — Purchases of intangible assets $94,412,000 (FY2024) / $104,483,000 (FY2025), FY2023 not read, on a tag the feed does not carry`.
   - *Review figures:*
     - Deducting the filed amounts puts the base at $5.72 (FY2024 stays the median year). With g_base held at 15.32%, the weighted IRR is 21.47% (bear 16.54%), still A.
     - The tier flips at about $242M a year with growth held, or about $358M a year with the growth blend recomputed.
     - The recomputed-blend convention gives about 21.7% at FY2018's tagged level of about $96.2M a year; holding growth gives 21.45%.
5. **The engine re-run itself** reopens the alert gates, enters HIGH_NET_DEBT in `fragility_flags`, and re-measures the override counterfactual through the 5.5 engine. Taken together, items 2–4 can move the tier. *Review figures:* the intangible deduction and the filed FY2022 count together give 20.09%, which is A by 0.09pp. A start at guided capacity growth is Tier B on its own.

**Corrections to the dated record.** The 2026-10-17 text above stays as written. Where it disagrees with the entries below, the entries below supersede it.
- **DCF section:** it quotes "months since FY end 9.5". The final key_numbers.md prints 9.6.
- **Growth sanity check:** it says the latest prints "do support a low-teens start". The base start is 15.3% (g_base 15.32%), which is not low-teens. Half of it comes from the rev CAGR 3y (15.07%) that the same paragraph and the BASIS_BREAK_SUSPECT resolution call untrusted, and it sits above guidance (open item 2).
- **NI_OCF_DIVERGENCE resolution, and the "maintenance version" bullet under Owner's earnings:** these claimed that the maintenance figure ($2,176,645,000) landing "in the same ballpark" as the conservative figure ($1,961,278,000) shows the divergence is "presentation, not earnings quality". That claim is withdrawn.
  - In FY2025 capex exceeded D&A, so the D&A and min(capex, D&A) legs cancel. The maintenance figure is then just net income plus the CSV's `delta_nwc` release, and the two figures agree only because of the working-capital swing the flag asks about.
  - `delta_nwc` is not an operating working-capital measure here. The engine computes it as (current assets − cash) − (current liabilities − current borrowings), and financials_history.csv has no current-borrowings figure (`debt_current` is blank) for FY2023–FY2025. Those years' deltas therefore include changes in current borrowings, and FY2023's includes the whole shift of current borrowings into the working-capital term.
  - The direction was also wrong. IFRS classification of lease principal and interest paid moves operating cash flow, not net income, so "net-income presentation never enters" the OCF base does not protect the base. The flag is resolved again above, from the D&A and finance-cost figures and the filer's classification.
- **STALE_FY resolution:** its closing sentence is withdrawn (open item 1).
- **SHARES_FALLBACK resolution:** "those history years use the basic/outstanding counts recorded in the shares_tag column" is wrong.
  - financials_history.csv has `shares_tag` OVERRIDE and 589,306,002,483 shares in every row from 2016 to 2025. key_numbers.md lists the override's periods filled as 2016-12-31 through 2025-12-31. The flag text describes the engine's raw fallback before the override filled the gap.
  - The consequence runs the other way. The FY2016–FY2022 per-share history divides by the post-emergence count, far above the count at the time (*audit figure:* about 970× for 2016–2021; statements.json blanks the 2018–2021 pre-emergence counts as implausible against the post-emergence line). Pre-2023 per-share history is therefore not comparable with today's.
  - The FY2016–FY2021 fill affects only the history display. The FY2022 fill does not: FY2022 is the first count in the share-count CAGR window, so the 0.00% share-count CAGR and the 15.32% growth blend rest on it (open item 3).
- **OVERRIDES section, its "Measured impact" bullet, and the OVERRIDE_APPLIED:shares resolution:** they credit the override's effect to the FY2024 denominator ("the whole measured lift is the shares denominator"; "modestly flatters that base year"). judgment.json's `shares_override.reason`, which key_numbers.md prints, says the same.
  - The +2.57% base effect does come from the FY2023–FY2025 denominator.
  - The +1.44pp IRR effect does not. It is the FY2022 fill's growth effect (open item 3).
  - The reason text is part of the engine's hashed override record (`overrides_applied`), so it is corrected here today and in judgment.json on the re-run. The 2026-10-17 statement that the tier does not depend on the overrides' economics (20.97% on the zero-fill baseline) still holds.
- **Figures that are not in key_numbers.md:**
  - The Owner's earnings section and the Final verdict quote financials_history.csv figures that key_numbers.md does not print. These are the FY2025 OCF and capex, the maintenance version, the FY2023–FY2025 OE totals (rounded in the verdict as "$1.47B → $1.78B"; key_numbers.md prints only the FY2025 total, $1.961B), and the Borrowings and cash legs of net debt. They match the CSV.
  - The Owner's earnings net-debt bullet also gives the lease liability ($3,792,861,000, Note 34), adjusted net leverage (1.5x), liquidity ($3.7B) and "25.7% of LTM revenue". These are filing or results-release figures that appear in no run output: dcf_numbers.json `lease_liabilities_latest` is null, and statements.json has no lease liability after FY2018. They stand as filing-sourced claims that cannot be verified from the diff.
- **Moat AGAINST:** "2026 guidance was cut then reinstated around a fuel shock" is now sourced to the 2Q2026 release's guidance table (guidance check above).

**Why the tier is what it is.**
- **Tier A, unchanged.** The weighted IRR of 22.40% sits in the A band (20–25%), there is no tier override, and make_score 5.5 moved no valuation figure.
- The band runs from bear 17.28% (tier B) to bull 27.57% (tier S). The $47.47 price clears the 20% hurdle ($54.93) but not the 25% hurdle ($41.27).
- **Confidence is low on an A-tier name. This is stated explicitly because alerts no longer check confidence.** Four things keep it low:
  - WIDE_SCENARIO_SPREAD (4.67x) still stands.
  - HIGH_NET_DEBT applies on the ADS basis, and interest paid and lease principal sit outside the base (NI_OCF_DIVERGENCE above).
  - STALE_FY is escalated (open item 1).
  - The base start sits above guidance, and the engine's capex leaves out an intangible-purchase line (open items 2 and 4).
- Taken one at a time, the review's sensitivities leave the tier at A, with one exception: a start at guided capacity growth gives Tier B. The intangible deduction and the filed FY2022 count together leave A by 0.09pp (open items 2–5).
- Both alert gates are closed until an engine re-run.
- The 2026-10-17 instruction stands, reinforced by the 3.33x leverage, the guidance gap and the capex gap: size it like a B, not an A.
