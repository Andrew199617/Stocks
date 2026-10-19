# CHT — Chunghwa Telecom Co., Ltd.
v5 run, 2026-10-14. All figures below are copied from dcf_numbers.json, financials_history.csv, or ttm.py output — none are recomputed. Prices and per-share figures are per ADS (1 ADS = 10 ordinary shares, see ADS flag below); the engine's raw per-share figures are per ordinary share.

## What it is
Taiwan's largest integrated telecommunications company and the clear incumbent: fixed-line, mobile (5G), fixed broadband/internet, and a growing enterprise ICT business (cloud, cybersecurity, IDC/AIDC, big data, IoT, smart-city projects) across Consumer, Enterprise and International business groups. Former state monopoly, privatized in 2005; the Ministry of Transportation and Communications remains the largest shareholder. Defensive, subscription-based revenue in a saturated market.

Recent prints (company reports): Q2 2026 revenue NT$61.36B, +8.2% YoY, operating income +5.7%, net income attributable to stockholders NT$10.64B (+4.7%), EPS NT$1.38, EBITDA NT$23.52B at a 38.32% margin (down from 39.80% a year earlier). H1 2026 revenue +7.8% YoY, net income +3.9%, EPS NT$2.68 vs NT$2.57. August 2026 revenue +25.6% YoY and Jan–Aug revenue +9.5% include lumpy ICT project deliveries and a one-off gain from asset utilization in August — the growth acceleration is real but mix-driven (project/product revenue) rather than a step-change in core service growth: Q2 mobile service revenue grew +3.2%, fixed broadband revenue +3%.

## Owner's earnings
**FY2024 (latest fiscal year in the engine's EDGAR history, from financials_history.csv):** operating cash flow $2,417,000,000; capex $877,000,000 (tag PurchaseOfPropertyPlantAndEquipmentClassifiedAsInvestingActivities); SBC $0 as filed (tag ExpenseFromSharebasedPaymentTransactionsWithEmployees — SBC is immaterial for this issuer, ~$1M or less in the filed years, so treating it as a real cost changes nothing).
- **Conservative owner's earnings FY2024: $1,540,000,000** — OE positive 5 of the last 5 fiscal years, and every year in the 10-year history.
- **Maintenance version: NOT USABLE.** financials_history.csv shows D&A jumping from $1,215,147,070 (2019) to $37,138,000,000 (2020) and $40,525,000,000 (2024) — a TWD-denominated D&A series sitting inside an otherwise USD-translated history. The maintenance definition (NI + D&A − min(capex, D&A) − ΔNWC) inherits that break and produces a figure larger than revenue; it is a data-series artifact, not economics. The OCF-based conservative definition is unaffected (OCF, capex and SBC series are consistent) and is the base used throughout.
- **Base used = the engine's normalized base: median of the last 3 FY OE/share = $0.1861 per ordinary share = $1.8609 per ADS** (base_source: median_of_last_3_fy_oe_per_share). Latest-FY OE/share is $0.1981 per ordinary share ($1.9807 per ADS) — the median and the latest year are close, so there is no base-divergence problem; the median is mildly conservative. No TTM pin was used — see STALE_FY under Flags.
- Balance sheet: net debt latest −$788,000,000, i.e. a net cash position; diagnostics put net debt at −0.05x normalized OE. The balance sheet is not a risk factor in the verdict either way — the gap to the price is far too large for net cash to matter.
- Market-cap note: the engine's market_cap_est ($361,615,250,000) multiplies ordinary shares by the ADS price and so overstates the true cap 10x; external references put the real market cap at ~$34.5B, which is why the name is in the under-$40B universe. judgment.json's in_scope_under_40b follows the engine's computed figure (false), per the standing make_score convention for ADS names (same treatment as JD and VOD).

## Moat: 6/10 — moderate/narrow, the strongest incumbent in its market
Justification: Taiwan's #1 operator across mobile, broadband and fixed, with scarce spectrum, a sunk incumbent network and very low churn supporting modest premium pricing — but telecom returns are capped by capital intensity and regulation, the market is saturated, and two capable rivals contest every segment.
- FOR: Taiwan's #1 operator — mobile revenue share 41.2% (record high, Q2 2026) above its 39.8% subscriber share; ~54.6% share of broadband access/internet; leading 5G share; scarce licensed spectrum plus the sunk incumbent fiber/last-mile network rivals cannot replicate; very low churn (postpaid 0.36%) and premium mix — 5G migration fee uplift ~36%, postpaid ARPU +2.4% YoY, broadband ARPU rising; enterprise/ICT bundling (cloud, cybersecurity, IDC, AIDC) anchored to the incumbent network; fortress defensive cash generation — net cash, OE positive 5/5 years, minimal SBC.
- AGAINST: saturated, mature market (smartphone penetration >90%) — core growth is low-single-digit; capital-intensive and regulated (spectrum/network capex never stops, the NCC caps the return the moat can earn); two capable consolidated rivals (Taiwan Mobile, Far EasTone) and entry-tier price competition; OTT erosion of legacy fixed voice/SMS, while the fast-growing ICT revenue is project-based, lumpy and lower-margin; state influence via the MOTC's stake, and TWD/USD exposure for ADS holders.
- A 6 gives CAP = 9.8 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 9.8 years, 15-year projection.

## DCF — v5 final run (2026-10-14)
Growth recalibration (written reason): the engine's blended growth (g_base −1.23%; components: rev CAGR 5y +0.22%, rev CAGR 3y −2.59%, latest rev YoY −3.79%, OE/share CAGR 2y +3.17%) is built from the USD-translated history ending FY2024 and reads as decline, while the company's TWD results grew through that window and current prints run well above it (H1 2026 revenue +7.8%, EPS +4.3%; Q2 2026 revenue +8.2%). The negative blend is largely a currency-translation and stale-base artifact, so scenario starts were recalibrated via offsets (−0.068 / −0.008 / +0.042 / +0.072 / +0.112 vs g_base) to −8.0% / −2.0% / +3.0% / +6.0% / +10.0%. Sanity check against prints: the base start (+3.0%) sits deliberately below the latest EPS prints (+4–5%) because the 2026 revenue acceleration is mix-driven (lumpy ICT projects, handset/product sales, an August one-off asset-utilization gain) while H1 net income grew only +3.9% and EBITDA margin compressed; the bull (+6.0%) and super-bull (+10.0%) starts bracket the current revenue prints, so no scenario start is below what the company just printed without that reason. Probabilities at the defaults 10/25/30/25/10; OE multipliers at the defaults 0.75/0.90/1.00/1.10/1.25. Price $46.51 per ADS.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | −8.0% | 0.75 | Price war + ICT project cliff; OE/share contracts | $7.17 | 4.11% |
| Bear | 25% | −2.0% | 0.90 | Legacy decline outruns ICT; flat-to-down OE | $11.23 | 5.34% |
| Base | 30% | +3.0% | 1.00 | Core low-single-digit growth, ICT mix offsets legacy erosion | $15.58 | 6.71% |
| Bull | 25% | +6.0% | 1.10 | 2026 momentum holds: 5G/broadband ARPU + ICT/AIDC demand | $19.59 | 7.92% |
| Super bull | 10% | +10.0% | 1.25 | Sustained high-single-digit growth with margin recovery | $26.59 | 9.94% |

- **Probability-weighted: IV@15% $15.75 (−66.1% vs price), IV@12% $20.80, IV@10% $26.42, weighted IRR 6.78%, base-case IRR 6.71%**
- **Tier by numbers: D.** Diagnostics (dcf_numbers.json): OE yield 4.00%, terminal value 18.2% of IV@15%, scenario spread 3.71x, net debt −0.05x normalized OE, 21.4 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (latest fiscal year in the engine history ended 21 months ago, FY2024): ttm.py was run and cannot produce a TTM base for this issuer — its exact output: "ttm.py: cannot compute TTM for CHT (CIK 1132924): ocf: no annual (FY) fact; sbc: no annual (FY) fact; shares_diluted: no annual (FY) fact; capex: no capex facts in companyfacts under any candidate tag and no capex_override in judgment.json — refusing to zero-fill (same DATA_GAP standard as the engine)". ttm.py reads us-gaap facts only and CHT is an IFRS filer, so this failure is expected; the engine's median base is used instead. The direction of the staleness is conservative, not flattering: the FY2025 20-F (filed 2026-04-15) and the company's FY2025 statements report revenue and net income above the engine's FY2024 figures (~$7.5B revenue, ~$1.3B net income per external summaries of the filing), and 2026 prints grew further — a fresher base would raise, not lower, the IVs, and even the super-bull case at the stale base reaches only a 9.94% IRR, so the verdict does not turn on the stale base.
- **FX_CONVERTED**: the reporting currency is TWD; where the issuer did not file USD figures, the engine converted at period-end ECB reference rates (frankfurter.app), recorded in dcf_numbers.json fx_conversion — flow facts use period-end rates, not period averages. This is also why the USD revenue history (and the engine's negative growth blend) understates the company's TWD growth; the scenario recalibration above addresses it.
- **USD_TRANSLATIONS_USED**: for most recent years the base rests on the issuer's own filed USD convenience translations (the round figures in financials_history.csv from 2017 onward), used as-is. One exception found in the same file: the D&A series from 2020 onward is TWD-denominated (see Owner's earnings) — it corrupts only the maintenance OE definition, which is not used.
- **ADS_RATIO_APPLIED**: 20-F filer — judgment.json declares ads_ratio 10.0, sourced from the filer's own Form 20-F for the fiscal year ended December 31, 2025 (filed 2026-04-15), share capital note (Global depositary receipts): one ADS represents 10 common stocks; the same statement appears in the Q1 2026 statements furnished on Form 6-K and in the Form F-6 registration. The engine scaled per-share figures x10 so they are comparable to the $46.51 ADS price.
- **LOW_OE_YIELD** (preliminary run only, 0.4%): an artifact of the missing ADS ratio — per-ordinary-share OE against a per-ADS price. After the ADS scaling the base OE yield is 4.00% and the flag no longer fires. A 4% OE yield on a low-single-digit grower is the actual valuation problem: at a 15% hurdle the math cannot close a ~25x OE multiple.

## My thoughts / overlay
- This is a quality-versus-price result, not a quality debate. The business is a stable, net-cash, #1 incumbent with a decade of uninterrupted positive owner's earnings — and the ADS price capitalizes it as if it were a growth stock. Every scenario, including a super-bull that assumes +10% OE/share growth the company has never sustained, produces an IRR below 10%.
- The method range is narrow: defensible inputs (median base vs latest-FY base, growth starts a few points either way) move the weighted IRR within roughly the 5–9% band — Tier D under all of them. There is no plausible input set under this method that gets CHT near 15% at $46.51.
- What would change the answer is price, not the business: the shares clear the 15% hurdle only at or below the weighted IV@15% of $15.75 per ADS, and a margin of safety against the bear cases ($7.17–$11.23) argues for a buy price below even that. At the current price the ADS is a dividend/defensive holding, not a 15%-hurdle investment.
- Risks to this (bearish-on-price) view: TWD appreciation would lift USD-denominated OE/share mechanically; a sustained ICT/AIDC buildout for Taiwan's semiconductor sector could keep growth nearer the bull case; and the August 2026 one-off gain flatters recent prints in the other direction. None of these bridge a 66% gap to IV@15%.

## Final verdict
- **Final tier: D** (weighted IRR 6.78% on the v5 final inputs; Tier D under every defensible input set tried)
- Confidence: **Medium** (high on OE quality and the ADS/FX mechanics; the base is 21 months stale, but the staleness biases the result conservatively and the verdict is not close)
- One-liner: Taiwan's dominant incumbent telecom, moat 6/10 — quality is not the issue, price is: Tier D, weighted IRR 6.8%, IV@15% $15.75 per ADS vs $46.51, and even the super-bull case ($26.59) sits far below the price; it clears 15% only under ~$15.75 per ADS.

## Engine 5.5 re-score (2026-10-19)
This is a dated addendum. The 2026-10-14 text above stays as written; where this section disagrees with it, this section supersedes it. This was a make_score-only re-score under ruling 1 ("Re-run make_score (not the engine) ... so market_cap / in_scope_under_40b are corrected without changing tiers"). `dcf_engine.py` and `ttm.py` were not run. dcf_numbers.json and financials_history.csv are still the 2026-10-14 output: engine_version 5 with no engine_release, which makes it a pre-5.4 run. On 2026-10-19, `make_score.py CHT` rebuilt score.json and key_numbers.md from that record, and then `prices.py CHT` and `reprice.py CHT` ran. The new figures below are quoted from the 2026-10-19 key_numbers.md and the old ones from the 2026-10-14 key_numbers.md. There are two marked exceptions: rows copied verbatim from financials_history.csv, and the open items' replay figures, each marked "cannot verify from the diff".

| | 2026-10-14 (pre-5.4 run) | 2026-10-19 (make_score 5.5 on the same record) |
|---|---|---|
| Base OE/share (3-yr median, per ADS) | $1.86 | $1.86 (unchanged) |
| Latest FY OE/share / OE total | $1.98 / $1.540B | $1.98 / $1.540B (unchanged) |
| Weighted IRR / base-case IRR | 6.78% / 6.71% | 6.78% / 6.71% (unchanged) |
| IV@15 (weighted) | $15.75 | $15.75 (unchanged) |
| Tier by numbers / final | D / D | D / D (unchanged) |
| Market cap (est) | $361.615B | $36.162B (ADS-corrected by make_score) |
| Scope (under $40B) | out of scope (`in_scope_under_40b` false) | in scope (`in_scope_under_40b` true) |
| Net debt / normalized OE | −0.05x | −0.54x on the ADS basis |
| Alert gates | not computed (pre-5.4) | `alert_eligible` false, `exit_alert_eligible` false |

**What make_score 5.5 changed for this filer: the market cap and the scope (ruling 1).**
- **Market cap.** The pre-5.5 engine priced the cap as the per-ADS price × the ORDINARY share count, so $46.51 × 7,775,000,000 printed $361.615B. That is 10× the traded cap, because one ADS represents 10 common shares (`ads_ratio` 10.0 in judgment.json, sourced to the FY2025 20-F share-capital note). make_score now applies the single cap formula, price × shares ÷ ads_ratio. key_numbers.md prints "$36.162B (ADS-corrected by make_score: price × shares ÷ ratio; the pre-5.5 engine printed $361.615B)", and score.json's `market_cap_basis` reads `ads_corrected_by_make_score`.
- **Scope call: in scope.** At the scored price of $46.51, the corrected cap of $36.162B is under the $40B line.
  - make_score rewrote judgment.json's `in_scope_under_40b` from false to true, because the old cap fully explains the old value. score.json carries `in_scope_corrected_by_make_score` true.
  - `_system/overrides_registry.json` gained a `scope_correction` event (old cap $361.615B → new cap $36.162B, in scope).
  - The `ads_ratio` declaration did not change: same ratio 10.0, same source, same reason. Its registry event therefore keeps its first-recorded date, 2026-10-14. The 2026-10-19 make_score run re-dated that event to 2026-10-19. That is a make_score defect handled outside this folder, not an outcome of this re-score.
  - This supersedes the 2026-10-14 "Market-cap note" bullet. judgment.json no longer follows the inflated engine figure, and CHT is now inside the under-$40B universe on its own computed cap. It no longer relies on the external market-cap reference in that bullet, which was never a figure from the run's files.
  - The cap is clearly under the line, not borderline. reprice.py's live.json prices the cap and scope at each new close with the same formula, so a large enough rise in the ADS price would show up there first.
- **Net debt / normalized OE (ruling 1, "anything downstream").** The pre-5.5 engine divided net debt by per-ADS OE × ORDINARY shares, which made the ratio 10× too small: it printed −0.05x. key_numbers.md now prints "-0.54x on the ADS basis (make_score: the pre-5.5 engine's ratio × ads_ratio 10 — it divided net debt by per-ADS OE × ORDINARY shares; the engine printed -0.05x)". score.json records `net_debt_to_normalized_oe_ads_basis` −0.5446. This supersedes the "−0.05x" in the 2026-10-14 balance-sheet bullet.

**HIGH_NET_DEBT / BIG_NET_CASH on the ADS basis: neither would fire, so no flag changes.**
- The engine's thresholds are > 3x for HIGH_NET_DEBT and < −2x for BIG_NET_CASH. −0.54x is inside both.
- The balance sheet behind the ratio is a modest net-cash position. Net debt (latest) is $-788.0M, which is borrowings less cash. It comes from financials_history.csv's FY2024 row: debt_current 268,000,000 plus debt_lt 50,000,000, less cash 1,106,000,000. That reproduces the engine's net debt exactly.
- −0.54x means net cash equals about half a year of normalized owner's earnings. The price is not carried by a cash pile, which is what BIG_NET_CASH tests. Borrowings are negligible, which is what HIGH_NET_DEBT tests.
- The 2026-10-14 conclusion stands: the balance sheet is not a factor in the verdict.

**Alert gates: both closed until an engine re-run, as expected.**
- make_score 5.5 treats output from any other engine release as stale. score.json has `alert_eligible` false and `exit_alert_eligible` false. Its `exit_alert_suppressed_reason` reads "engine output predates release 5.5.0 — re-run the engine before an exit alert". At Tier D no entry alert would fire in any case.
- The record is pre-5.4, so score.json carries no bear/bull band: `irr_bear`, `irr_bull`, `tier_bear` and `tier_bull` are null, and it claims no band.
- CHT declares no capex, SBC, shares or base override, so make_score had no override impact to carry. The only judgment input the engine applies is the `ads_ratio`.

**Flags on the record: none new.** make_score does not recompute flags. The four on the record are the 2026-10-14 flags, and each is resolved by name.
- **STALE_FY** (21.4 months since FY end).
  - The 2026-10-14 bullet says the stale base "biases the result conservatively". It supports that with FY2025 revenue and net income "per external summaries", not with operating cash flow and capex, so this section does not rely on it.
  - The resolution that rests on generated figures is a bound. The tier changes only if the weighted IRR clears the 10% C line. The super-bull case already starts from 1.25× the base (OE mult 1.25) with a +10.0% growth start, and it returns 9.94%.
  - A base 25% higher would give the base case that same starting OE, but with a +3.0% growth start instead of +10.0%, so it would return less than 9.94%. The weighted IRR tracks the base case (6.78% vs 6.71%).
  - So a FY2025 or TTM base would have to be more than 25% above $1.86 per ADS to move the tier. Whether it is cannot be checked from this folder: the CSV ends at FY2024, and there is no ttm.json because ttm.py reads us-gaap facts only. See open item 4.
- **FX_CONVERTED**, **USD_TRANSLATIONS_USED** and **ADS_RATIO_APPLIED** (×10) are resolved in the 2026-10-14 text, and the corrected cap and ratio change none of those resolutions. The one known exception inside USD_TRANSLATIONS_USED, the untranslated D&A column, is now escalated as an engine defect (open item 3). It does not touch OCF, capex, SBC or the base.

Confidence stays **medium**. There is no WIDE_SCENARIO_SPREAD and no unresolved flag, CHT is not a sector misfit (`model_fit` modeled), and ruling 1 keeps every judgment input as recorded.

**Moat evidence (WORKER_SPEC step 5), added 2026-10-19.** The 2026-10-14 moat section names FOR and AGAINST pillars but quotes no five-year margin or ROIC history. financials_history.csv (the issuer's USD convenience translations) gives operating income against revenue as follows. Each percentage is one CSV column divided by another, not an engine-printed figure.

| FY | Operating income | Revenue | Operating margin |
|---|---|---|---|
| FY2020 | 1,508,000,000 | 7,393,000,000 | 20.4% |
| FY2021 | 1,620,000,000 | 7,588,000,000 | 21.3% |
| FY2022 | 1,524,000,000 | 7,053,000,000 | 21.6% |
| FY2023 | 1,514,000,000 | 7,289,000,000 | 20.8% |
| FY2024 | 1,429,000,000 | 7,013,000,000 | 20.4% |

The margin is flat in a 20–22% band with no widening. That fits a moderate/narrow 6, a stable regulated incumbent, rather than a 7+.
- The CSV has no gross-profit line, and the folder has no fundamentals.json, so the gross-margin and `roic_proxy` series that step 5 names are not available here. They await enrichment.
- Moat 6 is below the 7+ level that requires a ROIC reason, and the score is unchanged.

**Open items for the next engine 5.5 re-run.** None of these is applied, because ruling 1 limits this name to make_score. Each also appears in the run report for Andrew. Figures that are not in key_numbers.md, dcf_numbers.json or financials_history.csv are marked "cannot verify from the diff". None of them is part of this score.
1. **Capex completeness: intangible purchases (ruling 5, narrowed).**
   - FY2022–24 capex is recorded from a single IFRS PP&E tag, `PurchaseOfPropertyPlantAndEquipmentClassifiedAsInvestingActivities`: 1,026,000,000 / 1,004,000,000 / 877,000,000 in financials_history.csv. The folder has no `capex_ppe`, `capex_intangibles` or `capex_source` columns and no `capex_provenance`.
   - A replay of the recorded inputs through the 5.5 engine, run outside this folder, adds the filed `PurchaseOfIntangibleAssetsClassifiedAsInvestingActivities`: +$62M / +$8M / +$7M. That gives capex of $1,088M / $1,012M / $884M, a base of $1.834 per ADS against the published $1.86, and a weighted IRR of 6.72% against 6.78%. The tier is D either way. Cannot verify from the diff.
   - The re-run worker should reconcile capex against the FY2022–24 20-F cash-flow investing section, including spectrum and other intangible lines, and quote it.
2. **Spectrum.**
   - The same replay reads intangible purchases of $1,695M in FY2020. Cannot verify from the diff. The timing is consistent with Taiwan's 2020 5G spectrum auction, but the line's contents are not in this folder.
   - FY2020 is outside the FY2022–24 median window, which carries almost no such spending. With it inside the last five years, a 5.5 run may raise OE_VOLATILE.
   - Normalizing spectrum into the base would add cost to a window that carries little of it. That would lower the base, which deepens D rather than changing it.
   - Whether to normalize is the re-run worker's decision, made with the 20-F investing section quoted.
3. **D&A currency defect (engine FX).**
   - The CSV's `da` is in USD through FY2019 (1,215,147,070) and in NT$ from FY2020 (37,138,000,000; FY2024 40,525,000,000, against FY2024 revenue of 7,013,000,000 in USD).
   - dcf_numbers.json `fx_conversion.rates` stop at 2019-12-31. The engine used the issuer's USD translations for the other fields from FY2020 on, but left D&A untranslated.
   - As a result, the AGENTS.md capex / D&A completeness check cannot be done from the CSV: FY2024 capex 877,000,000 against da 40,525,000,000 compares US$ with NT$. CAPEX_COVERAGE_LOW would also fire spuriously on a 5.5 re-run.
   - The folder has no USD D&A for FY2022–24 (no statements.json), so it cannot verify from the diff that capex covers at least half of D&A. Escalated as an engine defect: translate D&A in years where it has no USD figure. The re-run worker should quote FY2022–24 D&A from the 20-F cash-flow statement in USD, or converted.
4. **Stale base.**
   - The worker should quote FY2025 operating cash flow, capex (PP&E plus intangibles) and SBC from the FY2025 20-F cash-flow statement, which judgment.json's `ads_ratio` source dates to 2026-04-15. Failing that, quote TTM legs from the 2026 6-Ks.
   - The worker should also check whether that filing's XBRL has reached companyfacts. Until then, the STALE_FY bound above is the resolution, not evidence of direction.
5. **Guidance.**
   - Neither section quotes management guidance. The 2026-10-14 growth sanity check used the H1 and Q2 2026 prints only.
   - Whether and what Chunghwa guides (revenue, EPS, capex) cannot be verified from the diff.
   - The re-run worker should compare the base start (+3.0%) and the capex run-rate with current-year guidance, as WORKER_SPEC step 6 requires.

**The other 5.5 rules, checked against this folder.**
- **SBC.** The recorded tag is the IFRS `ExpenseFromSharebasedPaymentTransactionsWithEmployees` (dcf_numbers.json `used_tags`). The ruling-6 reconciliation compares two us-gaap tags only, so SBC_TAG_RECONCILED cannot fire. The CSV's SBC is 1,000,000 / 0 / 0 for FY2022–24.
- **Share basis.** The CSV's diluted counts run from 7,765,000,000 to 7,776,000,000 across FY2015–24, with no scale break and no split. The cover-page dei comparison is a re-run check, because that count is not in this folder.
- **Market cap.** The corrected $36.162B uses the formula a 5.5 engine run uses, price × shares ÷ ads_ratio.
- **USD-override branch (ruling 7).** Not engaged: CHT declares no monetary override, only the `ads_ratio`.

**Why the tier is D.** This re-score leaves the numbers unchanged.
- The weighted IRR is 6.78% at $46.51 per ADS. Every scenario is under the 10% C line, from super bear 4.11% to super bull 9.94%.
- The weighted IV@15% is $15.75, −66.1% versus the price, on a base of $1.86 per ADS and an OE yield of 4.00%.
- The scope correction moves CHT into the ranked under-$40B universe, where it ranks as Tier D. It does not move the tier.
- The replay in open item 1 also gives D, which cannot be verified from the diff. The STALE_FY bound is what a fresher base would have to beat.
- `tier_override` stays null, and the one-liner and moat (6/10, CAP 9.8 years) are unchanged. confidence: medium.

**Data (2026-10-19).**
- make_score.py: ran (exit 0).
- prices.py: ran. It warned that the intraday chart request returned no usable points, and the daily series was kept. prices.json is a gitignored cache.
- reprice.py: ran. The live tier is D, unchanged from the scored tier. live.json is a gitignored cache.
- fundamentals.json, statements.json, segments.json and profile.json: still absent from this folder. They are not part of a make_score-only pass, and this page is not claimed complete.
- After an AGENTS.md audit later on 2026-10-19, only this section's text was corrected. No script was re-run, and no generated figure changed. The corrections: the unsupported replay figures are now marked or removed, the net-debt wording is fixed, the registry date note is corrected, the STALE_FY bound and the margin history are added, and the open items are listed.
