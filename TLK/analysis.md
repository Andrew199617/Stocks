# TLK — PT Telkom Indonesia (Persero) Tbk
Engine 5.4.0 run, 2026-10-17. First pass. ADS (NYSE: TLK) at $11.03 (nasdaq_quote_api); each ADS = 100 Series B ordinary shares (see OVERRIDES). Market cap ~$10.64B per MarketBeat's TLK profile — inside the <$40B scope.

All figures below are copied from key_numbers.md, dcf_numbers.json, financials_history.csv, fundamentals.json, or a cited filing/search result — none are recomputed.

## What it is
Indonesia's state-controlled integrated carrier: Telkomsel (largest mobile operator, 153.5M subscribers at 2Q26 per Bina Artha's company update), IndiHome fixed broadband, enterprise/data services, towers and data centres. Ultimate parent is the Government of the Republic of Indonesia (FY2024 statements, Note 1); the state stake (54.5%) is now held via Danantara (UOB Kay Hian, 2Q26 update). Reports in IDR under IFRS; files Form 20-F.

## Owner's earnings
**FY2024 (filer's own USD convenience translations, financials_history.csv):** operating cash flow $3,827M; capex $1,616M; SBC $0 — by filing override, see OVERRIDES.
- **Conservative owner's earnings FY2024: $2,211M = $0.022319 per ordinary share = $2.23 per ADS** (dcf_numbers.json base_oe_per_share, ADS-scaled). The maintenance definition (NI + D&A − min(capex, D&A) − ΔNWC) prints $3,734M for FY2024 in financials_history.csv — higher than the conservative $2,211M; the base uses the conservative definition, the lower of the two. (Corrected 2026-10-19: this section originally claimed the two definitions agree at $2,211M; $2,211M is the conservative total only.)
- OE/share (per ordinary share): FY2022 $0.024873, FY2023 $0.017686, FY2024 $0.022319. OE positive 5 of the last 5 fiscal years.
- **Base used = the engine's normalized base: median of the last 3 FY OE/share = $2.2319 per ADS** (base_source: median_of_last_3_fy_oe_per_share; the median year is FY2024 itself). No TTM base: ttm.py cannot compute one for TLK (it reports no annual FY facts for ocf/sbc/shares under the tags it reads), and per the worker spec an IFRS filer without a TTM uses the median base. Directional check on staleness: the company's own FY2025 highlights (restated basis) show revenue of Rp146,742B vs Rp149,967B in FY2024 and profit attributable to owners of Rp17,814B vs Rp23,649B — FY2025 was weaker than every base year, so the median base is, if anything, generous; confidence is capped low for this (see STALE_FY).
- Balance sheet (dcf_numbers.json): net debt $1,181M, lease liabilities $1,486M, against FY2024 equity of $10,075M (financials_history.csv) — lightly levered for a carrier. The printed net-debt-to-normalized-OE diagnostic is distorted by the ADS scaling and is not quoted.

## OVERRIDES — three filing-sourced, all in judgment.json
The preliminary run exited 4 with `DATA_GAP: sbc, shares` plus `ADS_RATIO_MISSING` — no tier, correctly. All three gaps were resolved inside the bounded authority (kind "filing" / the ads_ratio rule), from the filer's own FY2024 audited consolidated financial statements (furnished on Form 6-K filed 2025-04-18; Form 20-F for FY2024 filed 2025-04-28):
- **ads_ratio = 100.** Note 2t: "Income per ADS is computed by multiplying the basic earnings per share by 100, the number of shares represented by each ADS"; the income statement face reads "Profit per ADS (100 Series B shares per ADS)", and Note 1 records the ratio change (200 → 100) effective October 26, 2016.
- **shares_override = 99,062,216,600 (kind "filing").** Note 28 (Basic EPS): the weighted average is 99,062,216,600 shares for FY2024 and FY2023, and "The Company does not have potentially dilutive financial investments for the years ended December 31, 2024 and 2023" — diluted equals the basic count the engine found; the count is identical in every year since 2017 in financials_history.csv, so filling FY2022 with it changes nothing.
- **sbc_override = $0 (kind "filing", with ack_reason).** The FY2024 statements contain no share-based compensation line, note, plan or amount anywhere (the terms "share-based" and "stock option" do not appear); the direct-method cash-flow statement has no SBC add-back; capital stock (Rp4,953B) and APIC (Rp2,711B) are flat across FY2023–FY2024 with no stock-compensation credit in the equity statement. The $0 is the filer's reported position, not a zero-fill (COKE/ARCC treatment).
- **Measured impact (dcf_numbers.json override_impact): zero.** Base OE/share is $2.2319 per ADS and weighted IRR 19.11% both with and without the overrides — they unblock the tier without moving a single number, because the missing values were genuinely $0 / genuinely equal to the filed counts.

## Moat: 6/10 — moderate, durable but not growth-converting
Justification: Telkomsel is the largest mobile operator and IndiHome the leading fixed-broadband brand, on a nationwide fibre, tower (301,000 BTS on air at 2Q26, Bina Artha) and spectrum base rivals cannot replicate; licences are granted for unlimited periods (FY2024 statements, Note 1) and the state is anchor holder. Measured returns back a real franchise: roic_proxy (fundamentals.json, IDR as filed) ran 22.3% / 22.8% / 18.8% / 19.8% / 18.6% over FY2020–FY2024, well above the cost of capital through the cycle, and company-reported FY2024 EBITDA margin was ~50% (Rp75,029B on Rp149,967B revenue, Telkom financial highlights). Gross margin is not meaningful here — fundamentals.json carries no COGS split (expenses are presented by nature). Capped at 6: the moat does not convert into growth or pricing power (IDR revenue +1.3% FY2023, +0.5% FY2024, −2.2% FY2025; mobile subs −3.1% YoY at 2Q26; Indosat/XLSmart competition), and state control now carries an open governance overhang (below).
- FOR: market leadership at scale with fixed-mobile convergence switching friction; irreplicable physical base — telecommunication infrastructure of Rp161,035B is 54% of total assets (FY2024 auditor key audit matter); ROIC ~19–23% through the cycle; state anchor shareholder (Danantara 54.5%); self-funding dividend (Rp17,683B paid for FY2023, Note 29) with modest net debt.
- AGAINST: no growth conversion in a saturated, price-competitive market; SEC and DOJ investigations (revenue recognition, financial reporting, FCPA), an ICFR material weakness, restated FY2023/FY2024 figures and a March 2026 non-reliance 6-K; state control is not purely commercial; IDR translation drag (period-end rate 6.5e-05 in 2022 → 6.2e-05 in 2024, dcf_numbers.json); structural capex intensity (FY2024 cash capex Rp26,005B PP&E + Rp3,658B intangibles vs OCF Rp61,600B, plus Rp7,387B of lease principal in financing).
- A 6 gives CAP = 9.8 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 9.8 years, 15-year projection.

## DCF — engine 5.4.0 final run (2026-10-17)
The engine's blended growth is −5.27% — its only live component is OE/share CAGR 2y (−5.27%); every revenue component is null because the filer's revenue is not tagged under any candidate the engine maps, so the blend is an OE/FX series, not a revenue series. Probabilities are the defaults 10/25/30/25/10, offsets the defaults −12/−5/0/+5/+12pp, OE multipliers the defaults 0.75/0.90/1.00/1.10/1.25; the engine's printed scenario starts (after its rounding/floor) are in the table. Price $11.03 per ADS.
**Growth-start sanity check (mandatory):** recent prints are IDR revenue +0.5% (FY2024), −2.2% (FY2025) and +3.9% YoY (1H26, UOB Kay Hian), with USD OE/share printing −28.9% (FY2023) then +26.2% (FY2024) on FX and OE swings. The bull start (0%) sits *below* the latest IDR revenue print (+3.9%) — written reason: the scenarios are USD OE/share growth, and IDR translation has cost roughly 2–5pp a year (period-end rates above) while FY2025 IDR profit to owners fell from Rp23,649B to Rp17,814B on early-retirement/restructuring costs, so flat USD OE/share is what a +3.9% IDR revenue print has recently translated into. The super-bull start (+7%) exceeds recent prints — it is a recovery case only (2Q26 EBIT +22.9% YoY in IDR and mobile ARPU +11.6% YoY on pricing discipline, UOB Kay Hian) and carries only 10% probability. The base start (−5%) matches the direction of the actual FY2025 IDR profit decline.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | −10.0% | 0.75 | Investigations bite, IDR slides, price war | $7.88 | 10.89% |
| Bear | 25% | −10.0% | 0.90 | FY2025-style decline persists in USD terms | $9.46 | 12.91% |
| Base | 30% | −5.0% | 1.00 | Flat IDR operations, steady FX drag | $13.11 | 17.65% |
| Bull | 25% | 0.0% | 1.10 | 1H26 recovery holds; ARPU discipline sticks | $18.01 | 23.27% |
| Super bull | 10% | +7.0% | 1.25 | Margin recovery + pricing + FX stabilises | $27.95 | 32.51% |

- **Probability-weighted: IV@15% $14.39 (+30.4% vs the $11.03 price), IV@12% $18.62, weighted IRR 19.11%, base-case IRR 17.65%**
- **Tier by numbers: B.** Diagnostics (dcf_numbers.json): OE yield 20.24%, terminal value 16.2% of IV@15%, scenario spread (IV15) 3.54x, 21.5 months since FY end, IRR not at floor, not capped.
- Hurdle-clearing prices (dcf_numbers.json): the ADS clears a 20% hurdle at or below $10.51 and a 25% hurdle at or below $8.32; on the bear case alone it clears 15% only at or below the bear IV@15% of $9.46.

## Flags — every fragility flag resolved
- **DATA_GAP:sbc / DATA_GAP:shares / ADS_RATIO_MISSING** (preliminary run): resolved by the three filing-sourced overrides above; measured impact zero.
- **OVERRIDE_OUT_OF_BAND:sbc**: acknowledged in judgment.json (ack_reason) — there is no filed SBC value in any year to band against; the $0 is the filer's own reported position, evidenced in the override source.
- **OVERRIDE_APPLIED:sbc / OVERRIDE_APPLIED:shares**: see OVERRIDES — gap, filing evidence, and measured impact (zero) are recorded in judgment.json, dcf_numbers.json overrides_applied/override_impact, and the overrides registry.
- **STALE_FY** (latest FY ended 22 months ago at the preliminary run; 21.5 months in the final diagnostics): real and unresolved by construction. The FY2025 Form 20-F was filed 2026-05-15 (fundamentals.json profile) but "latest 20-F (period 2025-12-31) is not yet in EDGAR companyfacts" (fundamentals.json note), so the filed history stops at FY2024 and no TTM can be built (ttm.py reports no annual FY facts for TLK). The median base is used per the IFRS rule in the spec; the company's own FY2025 highlights show FY2025 was weaker than the base years, so staleness flatters rather than penalises the result — one reason confidence is low.
- **NI_OCF_DIVERGENCE (2022)**: depreciation-dominated, not a one-off. FY2022 net income was $1,781M against OCF of $4,713M (financials_history.csv), with D&A of $2,153M — the depreciation of the Rp161T infrastructure base explains most of the gap; no tax-deposit, impairment or single working-capital item was identified (the filer's direct-method cash-flow statement does not present an NI-to-OCF reconciliation). The base is OCF-based throughout, so the divergence is the normal capital-heavy carrier pattern and does not distort it.
- **FX_CONVERTED / USD_TRANSLATIONS_USED**: noted. Reporting currency is IDR; the engine used the issuer's own filed USD convenience translations where present and period-end ECB reference rates otherwise (rates recorded in dcf_numbers.json: 6.5e-05 for 2022–2023, 6.2e-05 for 2024). Flow facts converted at period-end rather than average rates is a known approximation, and steady IDR depreciation biases USD OE/share growth downward — embedded in the scenario sanity check above.
- **ADS_RATIO_APPLIED**: per-share figures scaled ×100 ordinary shares per ADS from the filer's own statements (see OVERRIDES); the price and all per-share outputs are on the ADS basis.
- **SHARES_FALLBACK (2015–2021)**: noted — those history years use the basic/outstanding count. The count was in fact flat at 99,062,216,600 from 2017 onward (financials_history.csv), and the EPS note proves basic = diluted, so the approximation is immaterial; the base years are covered by the shares override.
- **TIER_BAND**: bear Tier C (12.91%) vs bull Tier A (23.27%) — the verdict is sized to the bear end (see Final verdict).

## My thoughts / overlay
- The investment question is not the franchise — a ~19–23% ROIC, ~50% EBITDA-margin incumbent trading at a 20.24% owner's-earnings yield is objectively cheap on filed numbers. The question is whether the filed numbers can be trusted right now: the SEC and DOJ are investigating revenue recognition, financial reporting and FCPA matters (company 6-K, April 2025, via Willkie's summary), there is an ICFR material weakness, FY2023/FY2024 were restated in the FY2025 report, and a March 10, 2026 6-K is a non-reliance disclosure whose remediation plan is promised in the FY2025 20-F. Until the FY2025 statements are tagged in companyfacts and the investigations resolve, every figure here carries that asterisk.
- Operating momentum is genuinely mixed, not broken: FY2025 IDR revenue −2.2% and owners' profit −24.7% on restructuring/early-retirement costs, then 1H26 revenue +3.9% YoY with ARPU +11.6% offsetting subscriber losses — pricing discipline replacing volume, which is what a maturing incumbent should do.
- The dividend is part of the return: Rp17,683B was paid for FY2023 (Rp178.50/share, Note 29) and the balance sheet (net debt $1,181M) does not strain to pay it — but note the DCF here values OE only; it does not capitalise any governance discount or premium.
- Method range: on the same filed base, defensible reads span the bear Tier C (12.91%) to the bull Tier A (23.27%). The weighted Tier B is the honest headline, sized to the bear end per the TIER_BAND rule.

## Final verdict
- **Final tier: B** (weighted IRR 19.11%; band bear C → bull A, sized to the bear end — at the $11.03 price the bear case does not clear 15%, clearing it only at or below $9.46)
- Confidence: **Low** (FY2025 not yet in companyfacts, restatements, open SEC/DOJ investigations and a material weakness; partially offset by two OE definitions agreeing and overrides with zero measured impact)
- One-liner: Dominant Indonesian integrated carrier (Telkomsel mobile + IndiHome broadband), moat 6/10 on ~19–23% ROIC through the cycle — the weighted case clears 15% (weighted IRR 19.11%, weighted IV@15% $14.39 vs $11.03 ADS price, base OE $2.23 per ADS for a 20.24% OE yield), but the band spans bear Tier C to bull Tier A and sized to the bear end it clears 15% only at or below the bear IV@15% of $9.46; confidence low — FY2025 20-F is not yet in EDGAR companyfacts (base stops at FY2024), FY2023/FY2024 were restated, and SEC/DOJ investigations with an ICFR material weakness are open.

**Completion note, 2026-10-19:** the block recorded above is resolved. The ADS market-cap fix shipped (Andrew's ruling, 2026-10-18; Stocks PR #5) — the engine now computes `market_cap_est = price × shares ÷ ads_ratio` = $10.93B for TLK, make_score accepts the in-scope judgment as written, and the score stands exactly as analyzed: **Tier B, weighted IRR 19.11%, IV@15% $14.39, moat 6, low confidence**. Enrichment and queue completion were finished in the same run.

## Engine 5.5 re-score (2026-10-19)
This is a dated addendum. The text above stays as written: the 2026-10-17 first pass, its 2026-10-19 corrections and the 2026-10-19 completion note. Where this section disagrees with that text, this section supersedes it.

This was a make_score-only re-score under ruling 1 ("Re-run make_score (not the engine) ... so market_cap / in_scope_under_40b are corrected without changing tiers"). `dcf_engine.py` and `ttm.py` were not run. dcf_numbers.json and financials_history.csv are still the engine 5.4.0 output that main re-ran with Muse's ADS market-cap fix. On 2026-10-19, `make_score.py TLK` rebuilt score.json and key_numbers.md from that record, and then `prices.py TLK` and `reprice.py TLK` ran (both exited 0). Every new figure below is quoted from the final key_numbers.md. The old figures are from the key_numbers.md that make_score wrote before this run. Where a figure comes from somewhere else (financials_history.csv, statements.json, dcf_numbers.json, the filer's own 20-F XBRL facts, or the independent audit of this folder), the text names the source.

**Read this first: the published figures rest on incomplete capex.** An independent audit of this folder against the review guide found two problems. First, the engine 5.4.0 capex leaves out a filed investing line, purchases of intangibles. Second, the earlier text's STALE_FY resolution does not hold. A make_score-only run cannot fix either one, so both are escalated to Andrew under "Open items" below. Until the engine re-runs, score.json publishes a base of $2.23 per ADS, a weighted IRR of 19.11%, IV@15 of $14.39 and hurdle prices of $10.51 (20%) and $8.32 (25%). None of these is a complete-capex figure.

| | Before (engine 5.4.0 record, pre-5.5 make_score) | After (make_score 5.5 on the same record) |
|---|---|---|
| Base OE/share (3-yr median, per ADS) | $2.23 | $2.23 (unchanged) |
| Latest FY OE total | $2.211B | $2.211B (unchanged) |
| Weighted IRR / base-case IRR | 19.11% / 17.65% | 19.11% / 17.65% (unchanged) |
| IV@15 (weighted) | $14.39 | $14.39 (unchanged) |
| IRR band | bear 12.91% (tier C) → bull 23.27% (tier A) | bear 12.91% (tier C) → bull 23.27% (tier A) (unchanged) |
| Tier by numbers / final | B / B | B / B (unchanged) |
| Market cap (est) | $10.927B | $10.927B (basis: diluted_latest), unchanged |
| Scope (under $40B) | in scope | in scope (unchanged) |
| Net debt / normalized OE | 0.01x (as the engine printed it) | 0.53x on the ADS basis |
| Alert gates | `alert_eligible` false, `exit_alert_eligible` false (the tier rests on an override) | both false; the exit reason now also names the engine release |

**What make_score 5.5 changed for this filer: the basis of the net-debt ratio, and nothing else.**
- **Market cap and scope: unchanged.** TLK is one of the eight records (PAC, EMBJ, FUTU, HTHT, LTM, TX, FMS, TLK) that `_system/README.md` (Engine 5.5 entry) lists as re-scored on main with Muse's cap fix, so its record is `engine_release` 5.4.0 with a corrected cap.
  - Its `market_cap_est` already applies price × shares ÷ ads_ratio: the $11.03 ADS price, the 99,062,216,600 ordinary shares and 100 Series B shares per ADS print $10.927B. The pre-fix engine had printed $1,092.66B (`_system/README.md`, Engine 5.5 entry), which is the defect behind the block that the completion note above closes.
  - make_score 5.5 recognises a cap that already divides and does not divide it twice. score.json's `market_cap_basis` reads `diluted_latest`, not `ads_corrected_by_make_score`.
  - judgment.json's `in_scope_under_40b` (true) already agreed with the cap, so make_score did not rewrite judgment.json and recorded no `scope_correction` event. TLK's four registry entries (sbc, shares, manual_price, ads_ratio) are identical to main's. This run added none and rewrote none.
  - The cap is far below the $40B line. reprice.py prices the live cap at each close with the same formula, and no plausible price move would cross the line.
- **Net debt / normalized OE (ruling 1, "anything downstream").** Muse's fix divided the cap by the ratio but not the normalized-OE total behind this diagnostic. The engine still divided net debt by per-ADS OE × ORDINARY shares, which made the ratio 100× too small: it printed 0.01x.
  - key_numbers.md now prints "0.53x on the ADS basis (make_score: the pre-5.5 engine's ratio × ads_ratio 100 — it divided net debt by per-ADS OE × ORDINARY shares; the engine printed 0.01x)". score.json records `net_debt_to_normalized_oe_ads_basis` 0.5341.
  - This supersedes the owner's-earnings section's note that the printed diagnostic "is distorted by the ADS scaling and is not quoted". The corrected figure is 0.53x.

**HIGH_NET_DEBT / BIG_NET_CASH on the ADS basis: neither would fire, so no flag changes.**
- The engine fires HIGH_NET_DEBT above 3x and BIG_NET_CASH below −2x. 0.53x is inside both, and make_score's line names no crossing.
- **What the balance sheet says.** Net debt (latest) of $1.181B is financials_history.csv's FY2024 row: debt_current 1,702,000,000 plus debt_lt 1,585,000,000, minus cash 2,106,000,000. That reproduces the engine's figure exactly.
  - The engine reads three borrowing tags: `LongtermBorrowings` + `CurrentPortionOfLongtermBorrowings` + `ShorttermBorrowings` (dcf_numbers.json `net_debt_basis`).
  - statements.json (IDR, as filed) carries exactly those three borrowing lines for FY2024: short-term debt Rp11,525B, current portion of long-term debt Rp15,866B and long-term debt Rp25,518B. No borrowing line is missing from the debt figure.
  - Lease liabilities of $1,486M (dcf_numbers.json `lease_liabilities_latest`) sit outside net debt under the engine's definition. Counting them too would still leave leverage well under the 3x line.
- 0.53x means net debt equals about half a year of normalized owner's earnings. That is light leverage for a carrier, as the 2026-10-17 text said. The balance sheet does not strain the dividend and does not drive the verdict, so the earlier conclusion stands.

**Alert gates: both closed until an engine re-run, as expected.**
- make_score 5.5 treats output from any other engine release as stale. score.json has `alert_eligible` false and `exit_alert_eligible` false. The exit reason is "engine output predates release 5.5.0 — re-run the engine before an exit alert; tier exists only because of a judgment override". At Tier B no entry alert would fire in any case.
- **Override impact was carried over, not re-measured.** key_numbers.md marks the override impact (base OE/share $2.23 → $2.23, weighted IRR 19.11% → 19.11%) as "carried from the prior score.json, not re-measured (engine output release 5.4.0 vs current 5.5.0)". score.json's `override_impact` carries `impact_carried_from_prior_score` true and `counterfactual_engine_release` 5.4.0.
- The three filing-sourced judgment inputs are unchanged: `sbc_override` $0, `shares_override` 99,062,216,600 and `ads_ratio` 100. "Unblocks tier: YES" still holds.

**Flags: no new 5.5 flag on this record. Two earlier resolutions are corrected here.**
- make_score does not recompute flags, so the flag list is the engine 5.4.0 list.
  - The Flags section above resolves FX_CONVERTED, USD_TRANSLATIONS_USED, ADS_RATIO_APPLIED, SHARES_FALLBACK, OVERRIDE_APPLIED:sbc, OVERRIDE_APPLIED:shares and TIER_BAND by name, and those resolutions stand.
  - Its resolutions of STALE_FY and NI_OCF_DIVERGENCE do not stand. Both are replaced below.
- The only new figure is the ADS-basis ratio. It triggers neither HIGH_NET_DEBT nor BIG_NET_CASH (above).
- **STALE_FY: escalated to Andrew, not resolved.** key_numbers.md reads 21.6 months since FY end. The earlier text calls the flag "real and unresolved by construction" and uses the median base under the IFRS rule (WORKER_SPEC step 4: ttm.py reads us-gaap only, so an IFRS filer gets no ttm.json). The review guide does not accept "no TTM available" at a 20-F filer as a resolution. Here the base years make it matter:
  - The FY2025 Form 20-F exists. statements.json (as_of 2026-10-19) records `latest_filed` as a 20-F for period 2025-12-31, filed 2026-05-15. Its `covered_through` is 2024-12-31, and its warning says that 20-F "is not yet in EDGAR companyfacts".
  - The FY2025 20-F restated two of the three base years, after the March 2026 non-reliance 6-K (first-pass text above). This run's FY2023 and FY2024 rows predate that restatement, because companyfacts carries nothing after the FY2024 20-F: statements.json dates FY2023 to the 20-F filed 2024-04-01 and FY2024 to the 20-F filed 2025-04-28. Whether the restatement changed OCF, PP&E capex or intangible purchases cannot be verified from the diff.
  - The FY2025 highlights quoted in the owner's-earnings section show FY2025 weaker than every base year. The stale base is therefore more likely to overstate than to understate.
  - A TTM or base pin taken from the FY2025 20-F or a 1H26 interim 6-K would use figures that are not in this run's outputs. The base_override rule does not allow that, and ruling 1 forbids judgment-input changes on this name. The flag is escalated as open item 2.
- **NI_OCF_DIVERGENCE (2022): the earlier resolution is withdrawn and replaced.**
  - **Why depreciation cannot be the answer.** The engine raises this flag only when the NI–OCF gap is above 40% of OCF *and* larger than the year's D&A (the `ni_ocf_gap_years` test in `dcf_engine.py`). The FY2022 row in financials_history.csv has net income (consolidated `ProfitLoss`) of 1,781,000,000, OCF of 4,713,000,000 and D&A of 2,153,385,000. The audit puts the part of the gap beyond D&A at $779M. FY2023 and FY2024 stay under their D&A and do not fire.
  - **The one-off, from the filing.** The FY2022 Form 20-F (filed 2023-04-06, accession 0001558370-23-005567) tags a fair-value loss on financial assets at fair value through profit or loss (`GainsLossesOnFinancialAssetsAtFairValueThroughProfitOrLoss`) of −Rp6,438B for FY2022, or −$414M in the filer's own USD convenience translation. The same fact reads +Rp3,432B for FY2021, −Rp748B for FY2023 and +Rp188B for FY2024 in the later 20-Fs, so FY2022's loss is the outlier.
  - The loss is a remeasurement recorded in profit. It lowers net income and leaves OCF untouched; any cash from buying or selling such assets sits in investing activities. It accounts for about half of the audit's $779M.
  - The files in this PR cannot attribute the rest, because the direct-method cash-flow statement carries no NI-to-OCF reconciliation. Cannot verify from the diff; this is open item 3.
  - **Why the base is still not distorted.** OE is OCF − capex − SBC, so a non-cash loss in profit never enters it. FY2022 delta_nwc is −123,000,000 in financials_history.csv, so working capital does not inflate FY2022 OCF materially. The median year is FY2024 (score.json `base_year` 2024), so FY2022 does not set the base.
- Confidence stays **low**. TLK is not a sector misfit (`model_fit` modeled).
- **Correction to the earlier text (confidence).** The Final verdict's confidence line says confidence is "partially offset by two OE definitions agreeing". That offset does not hold. The base is the conservative definition (latest FY OE total $2.211B). The two definitions do not agree, but the CSV's maintenance figure cannot say which one is higher.
  - **The CSV's FY2024 maintenance figure is distorted.** financials_history.csv prints FY2024 oe_maintenance of 3,733,952,000. That figure subtracts a delta_nwc of −1,420,000,000, and the delta_nwc comes from a change in how the current debt is tagged, not from the business.
    - The engine's working-capital measure takes current debt out of current liabilities only when the debt is filed under the combined current-borrowings tag.
    - TLK filed that tag for FY2023 (`debt_tag` LongtermBorrowings+CurrentBorrowingsAndCurrentPortionOfNoncurrentBorrowings). For FY2024 it filed current debt as two separate lines (`debt_tag` LongtermBorrowings+CurrentPortionOfLongtermBorrowings+ShorttermBorrowings).
    - So FY2024's current borrowings (debt_current 1,702,000,000) stay inside current liabilities, and the year-on-year change in working capital shows a large fall that did not happen.
  - Net debt reads both FY2024 lines correctly (balance-sheet bullet above). Only the working-capital diagnostic is affected, and the base is OCF − capex − SBC, so the base and the tier do not move. Any display of the CSV's FY2024 oe_maintenance repeats the distortion.
  - An independent check of this folder rebuilt working capital with current debt treated the same way in both years. Rebuilt that way, the maintenance figure still differs from the conservative one, so the two definitions do not agree.
  - This supersedes the owner's-earnings section's 2026-10-19 correction where it calls the maintenance figure "higher than the conservative $2,211M" and the conservative base "the lower of the two". The record shows neither.
  - The only remaining offset is the overrides' zero measured impact. Confidence was low and stays low.
- **Correction to the earlier text (opening line).** The opening line gives the price source as nasdaq_quote_api and quotes a MarketBeat market cap. The run's price is manual:
  - key_numbers.md prints "Price: $11.03 (source: manual)".
  - dcf_numbers.json `price_source` is manual, and the registry records a `manual_price` event dated 2026-10-19.
  - The market cap is key_numbers.md's $10.927B. The MarketBeat figure is not a run figure.

**Minority share of the base (the earlier text did not state it).** The base is consolidated OCF − capex divided by TLK's own shares, but Telkomsel is not wholly owned (profile.json: "65%-owned subsidiary").
- The 20-Fs put profit attributable to non-controlling interests at Rp6,984B / Rp7,641B / Rp7,114B, against consolidated profit of Rp27,720B / Rp32,068B / Rp30,725B, for FY2022–FY2024 (`ProfitLossAttributableToNoncontrollingInterests` and `ProfitLoss`).
- Profit to owners of the parent is Rp20,736B / Rp24,427B / Rp23,611B in statements.json, and statements.json shows minority interest of Rp20,258B on the FY2024 balance sheet.
- Minority holders therefore get about a quarter of consolidated profit; the audit puts it at 25.2% / 23.8% / 23.1%. The per-ADS base overstates what belongs to TLK holders by roughly that share.
- This is a method limit, not a correction to the score: the engine values consolidated OE for every filer. It is one more reason to size to the bear end.

**Open items for Andrew. Each needs an engine re-run or a ruling, and none is applied.**
1. **Capex leaves out the filed intangible-purchases line (the audit's P1).** In all three median years, financials_history.csv's `capex_tag` is the single IFRS PP&E line `PurchaseOfPropertyPlantAndEquipmentClassifiedAsInvestingActivities`. That is the single-tag 20-F case the review guide asks about.
   - statements.json shows a second investing line beside it, "Purchases of intangibles / software" (`PurchaseOfIntangibleAssetsClassifiedAsInvestingActivities`). The moat AGAINST pillar above already cites both lines for FY2024.
   - Engine 5.5 adds that tag on top of the PP&E roll-up (rulings 4 and 5). The 5.4.0 record this score is built on does not.

   | FY | PP&E capex (statements.json, IDR) | Intangibles (statements.json, IDR) | CSV capex (filer's USD) | Intangibles (filer's USD translation) | PP&E + intangibles (USD) |
   |---|---|---|---|---|---|
   | FY2022 | Rp35,010B | Rp3,259B | $2,249,000,000 | $209,000,000 | $2,458,000,000 |
   | FY2023 | Rp33,603B | Rp2,817B | $2,182,000,000 | $183,000,000 | $2,365,000,000 |
   | FY2024 | Rp26,005B | Rp3,658B | $1,616,000,000 | $227,000,000 | $1,843,000,000 |

   - The USD intangible figures are the filer's own convenience translations, tagged in each year's 20-F (FY2022 filed 2023-04-06, FY2023 filed 2024-04-01, FY2024 filed 2025-04-28). The last column adds the two USD columns.
   - **The audit's arithmetic on complete capex.** It takes financials_history.csv's OCF less the last column, with SBC at $0, divided by 99,062,216,600 shares × 100.
     - OE comes to $2,255M / $1,569M / $1,984M, which is $2.2764 / $1.5839 / $2.0028 per ADS.
     - The median is $2.003 against the published $2.2319, 10.3% lower. Net debt / normalized OE becomes 0.5953 instead of 0.5341.
     - These are audit figures, not engine output, and they are not part of this score.
   - The IRR, IV and tier on that base cannot be verified until `dcf_engine.py` re-runs. No replay figure is quoted here, because none is in a committed output.
   - **Andrew must rule** on one of two paths:
     - (a) a full engine 5.5 run for TLK in this release. Ruling 1 limits TLK to make_score, but the same ruling says "unblock TLK per its queue note".
     - (b) holding TLK as `NEEDS_MAIN_AGENT: capex` until that run. That is WORKER_SPEC's block for an unread filed capex line; here the line is intangibles of Rp3,259B / Rp2,817B / Rp3,658B.
   - Until then, the published base, IRR, IV@15 and hurdle prices rest on capex understated by the amounts above.
2. **STALE_FY and the restated base years** (see Flags). **Andrew must rule** on one of three paths:
   - (a) keep the FY2022–FY2024 median base at low confidence until companyfacts carries the FY2025 20-F;
   - (b) authorize a filing-sourced TTM or base pin from the FY2025 20-F and a 1H26 interim 6-K, which is outside the worker's base_override authority today;
   - (c) hold TLK unscored until the restated years are in companyfacts.

   Whichever path is chosen, the worker on the next engine run should check the FY2025 20-F's cash-flow statement for whether the restatement changed FY2023/FY2024 OCF, PP&E capex or intangible purchases.
3. **The rest of the FY2022 NI–OCF gap** (worker item, no ruling needed). The worker on the next engine run should attribute what the fair-value loss does not explain from the FY2022 20-F's notes; cannot verify from the diff. It does not move the base (see Flags).

**Other engine 5.5 checks on this record (to confirm on the re-run).**
- **CAPEX_COVERAGE_LOW would not fire.** Recorded PP&E capex alone is more than half of D&A in each median year; for FY2024, financials_history.csv has capex 1,616,000,000 against da 2,020,952,000. The flag is a coarse floor, so its silence does not show capex is complete (open item 1).
- **The FY2024 maintenance-OE distortion would survive a re-run.** The 5.5 engine's working-capital line still takes out only the combined current-borrowings tag (`dcf_engine.py`, the `nwc` line in the history loop), so a re-run on the same filings would print the same kind of FY2024 delta_nwc. This is a diagnostic only and does not touch the base. Changing it is a code decision for Andrew, not a worker fix.
- **SBC (ruling 6): no change.** TLK files neither `ShareBasedCompensation` nor `AllocatedShareBasedCompensationExpense` (dcf_numbers.json `used_tags.sbc` is null). The $0 `sbc_override` still fills all three years.
- **Override currency (ruling 7): no restatement needed.**
  - TLK's overrides carry no currency amount: SBC is $0, which is zero in any currency; the shares override is a share count; and `ads_ratio` is a ratio.
  - make_score's refusal of a filing override used verbatim under `last_filed_unit_usd` cannot reach the sbc override, because dcf_numbers.json `override_checks.sbc.last_filed_unit` is null: no SBC value is filed in any unit.
- **Share basis (ruling 2): no action expected.** Base OE/share of $2.23 against the $11.03 price is far inside the 20× guard, and the count has been flat at 99,062,216,600 since 2017. This 5.4.0 record carries no cover-page count (dcf_numbers.json `shares_outstanding_dei_latest` is null), so the dei comparison is first recorded on the re-run. At a 20-F filer a divergence is only recorded.
- **STALE_FY will not clear on a re-run today.** statements.json (as_of 2026-10-19) still stops at FY2024, with the warning that the FY2025 20-F is not yet in companyfacts. An engine re-run now would keep the FY2022–FY2024 window and STALE_FY. It fixes capex, not staleness (open item 2).

**Why the tier is B, and what it rests on.**
- The weighted IRR of 19.11% sits in the 15–20% band. Tier by numbers equals the final tier, and no tier override is set.
- make_score 5.5 changed only the basis of a diagnostic: it moved no input, no scenario and no band.
- The band still spans bear tier C (12.91%) to bull tier A (23.27%). Sized to the bear end, the ADS clears 15% only at or below the bear IV@15% of $9.46, as the Final verdict says.
- That B rests on the 5.4.0 capex, which leaves out the intangible line. On the audit's arithmetic the complete-capex base is $2.003 per ADS, 10.3% below the published one. Whether Tier B survives cannot be verified until the engine re-runs (open item 1). Until then, the bear-end sizing is the reading to act on, and about a quarter of the consolidated base belongs to Telkomsel's minority holders.
