# WF — Woori Financial Group Inc.
v5 run, 2026-10-16. NYSE ADS (each ADS = 3 common shares), price $70.07 per ADS (nasdaq_quote_api). Form 20-F filer, K-IFRS, reporting currency KRW — the engine converted KRW figures to USD at period-end ECB rates and used the issuer's own filed USD translations where present.

All figures below are copied from dcf_numbers.json, financials_history.csv, or cited 6-K/search results — none are recomputed.

## What it is
One of Korea's four major financial holding companies, formed January 11, 2019 by comprehensive stock transfer of Woori Bank and affiliates. Woori Bank is the core; the group also runs card, capital, securities, asset-management and insurance (Tongyang Life) units. The transformation story is working on the mix: non-bank subsidiaries contributed 22.3% of H1 2026 net profit (vs 6.9% in H1 2025), and a share exchange to make Tongyang Life wholly owned was approved in April 2026 for completion in August 2026. Latest quarter (2Q 2026, preliminary 6-K): consolidated net income KRW 1,026,539M (+60.54% QoQ, +9.24% YoY), profit attributable to equity holders KRW 1,004,635M (+7.41% YoY); H1 2026 attributable profit KRW 1,608,953M (+3.67% YoY). CET1 ratio 13.71% (Q2 2026); the board resolved a KRW 150,000M treasury-share acquisition-and-cancellation on July 24, 2026, and management guides to a total shareholder return above 50% for 2026 including non-taxable dividends.

## Owner's earnings
Bank cash-flow statements make the conservative (OCF-based) definition structurally noisy — OCF for a bank sweeps in deposit, loan and other operating balance-sheet flows. The filed history (USD after FX conversion, financials_history.csv) shows exactly that:

| FY | Net income | OCF | Conservative OE | Maintenance OE |
|---|---|---|---|---|
| 2022 | $2,673,444,000 | $14,778,701,000 | $14,633,910,720 | $3,273,695,000 |
| 2023 | $2,034,774,000 | $1,256,347,000 | $1,118,806,580 | $2,676,510,000 |
| 2024 | $2,145,784,000 | −$4,147,022,000 | −$4,315,915,720 | $2,783,093,000 |

- Net income is stable ($2.0–2.7B across the three years, and growing again in 2026 per the 6-Ks above); the OCF leg is what swings, from +$14.78B to −$4.15B. The maintenance definition (NI + D&A − min(capex, D&A) − ΔNWC) is correspondingly steadier, but the engine's base is the conservative series — that mismatch is the single biggest caveat on this run (see SECTOR_MODEL_MISMATCH).
- Capex is small ($150,106,000 in FY2024, PurchaseOfPropertyPlantAndEquipment tag); SBC is immaterial ($18,787,720 in FY2024, ExpenseFromSharebasedPaymentTransactionsWithEmployees tag) — neither drives the result.
- OE positive in 3 of the last 5 fiscal years (engine diagnostic). Net debt is not meaningful for a bank and the engine reports net_debt_latest as null (bank debt tags are not mapped) — the balance-sheet verdict rests on the CET1 13.71% cited above instead.
- **Base used = the engine's normalized base, median of last 3 FY OE/share, scaled to per-ADS by the declared ads_ratio of 3: $4.4639 per ADS.** No TTM base: ttm.py reads us-gaap facts only and exited 3 for this IFRS filer ("ttm.py: cannot compute TTM for WF (CIK 1264136): ocf: no annual (FY) fact; sbc: no annual (FY) fact; shares_diluted: no annual (FY) fact; capex: no capex facts in companyfacts under any candidate tag...") — expected per the sweep spec, so the median base stands with the reason stated here.
- Growth: the engine has no revenue series for WF (the IFRS revenue concept is not in its used_tags — revenue: null), so every revenue/OE growth component is null and g_blend fell back to 3%, giving g_base 2.34% after the −0.66pp share-count adjustment. That fallback is a modeling limitation, flagged here rather than hidden.

## ADS RATIO (declared this run, bounded authority)
judgment.json declares `ads_ratio = {ratio: 3, source: Woori's own SEC filings (CIK 1264136) — the F-6 ADS registration statement states each ADS represents three (3) shares of common stock, par value KRW 5,000, and the NYSE security name carries the same ratio, reason: engine per-share figures are per ordinary share while the traded price is per ADS}`. The engine applied it (ADS_RATIO_APPLIED flag): per-share figures are now per ADS and comparable to the $70.07 price. One artifact to note: the engine's market_cap_est ($52,029,606,548.92) multiplies the per-ADS price by the ordinary share count, so it overstates the cap 3x; make_score's computed scope therefore reads out-of-scope and judgment.json's in_scope_under_40b is false to match the computed value. The group's actual Korea Exchange market capitalization is KRW 23.72 trillion (Finnhub, 316140.KS) — genuinely inside the sweep's <$40B universe. This is an engine artifact, not a scope violation.

## Moat: 3/10 — weak
Justification: one of Korea's big-four banking groups — the license, systemic importance and Woori Bank deposit franchise are real barriers, but the products are commoditized, there is no pricing-power or cost edge over KB/Shinhan/Hana, earnings ride the Korean credit cycle and regulator policy, and bank ROE economics cap returns. Non-bank diversification (22.3% of H1 2026 profit) is improving but is not yet a moat.
- FOR: Licensed major-bank franchise: regulatory barriers and systemic importance in Korean banking; large domestic deposit base and nationwide branch/digital network via Woori Bank; diversification improving — non-bank units (securities, card, capital, Tongyang Life) reached 22.3% of H1 2026 net profit; CET1 13.71% (Q2 2026) supports sustained dividends and buybacks, incl. the treasury-share cancellation resolved Jul 2026.
- AGAINST: Commoditized products — no pricing-power differentiation vs KB Financial, Shinhan and Hana; earnings tied to the Korean credit cycle, real-estate PF exposure and household-debt regulation; NIM pressure and policy caps on household lending limit the core spread business; KRW/USD exposure for ADS holders — won weakness directly cuts USD-translated earnings; structurally low bank ROE economics in a mature domestic market.
- A 3 gives CAP = 5.9 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 5.9 years, 15-year projection.

## DCF — v5 final run (2026-10-16)
Probabilities were tilted bear-ward from the 10/25/30/25/10 defaults to 15/30/30/15/10 because the base itself is an OCF artifact for a bank (see Flags) and the OE series is volatile; offsets and multipliers are the defaults (−12/−5/0/+5/+12pp; 0.75/0.90/1.00/1.10/1.25). Sanity check against actual prints: earnings (the stable series) grew mid-single digits — FY2024 net income $2,145,784,000 vs FY2023 $2,034,774,000, H1 2026 attributable profit +3.67% YoY, Q2 2026 attributable +7.41% YoY. The base start (2.34%) sits below those earnings prints for a written reason: the modeled series is OCF-based OE, whose filed history is far weaker and more volatile than net income, and the growth blend itself is the engine's 3% fallback (no revenue series mapped). The bull start (7.34%) matches the Q2 attributable print (+7.41%); the super-bull start (14.34%) exceeds any recent print and is carried only at 10% weight as a rate-cycle/non-bank-ramp tail.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | −9.66% | 0.75 | Credit cycle turns; OCF stays negative like FY2024 | $17.75 | 5.41% |
| Bear | 30% | −2.66% | 0.90 | OCF noise dominates; earnings flat | $27.45 | 7.27% |
| Base | 30% | 2.34% | 1.00 | Normalized median base, fallback growth | $36.40 | 8.99% |
| Bull | 15% | 7.34% | 1.10 | Earnings growth at the Q2 2026 print persists | $47.62 | 11.08% |
| Super bull | 10% | 14.34% | 1.25 | Non-bank ramp + benign credit + buybacks compound | $68.55 | 14.75% |

- **Probability-weighted: IV@15% $35.82, IV@12% $47.18, IV@10% $59.82, weighted IRR 8.91%, base-case IRR 8.99%**
- **Tier by numbers: D.** Diagnostics (dcf_numbers.json): OE yield 6.37% (per ADS), terminal value 17.9% of IV@15%, scenario spread 3.86x, 21.5 months since FY end. Even the super-bull scenario (14.75% IRR) does not clear the 15% hurdle at $70.07.

## Flags — every fragility flag resolved
- **STALE_FY** (latest FY ended 2024-12-31, 21.5 months ago): ttm.py cannot run on an IFRS filer (exit 3, quoted in Owner's earnings), so no TTM pin exists and the engine's median base is used per spec. Post-FY evidence from the 6-Ks shows no earnings collapse the stale base could be hiding: H1 2026 attributable profit +3.67% YoY and Q2 2026 net income +9.24% YoY.
- **OE_VOLATILE** (OE/share range >3x over 5 years): real and structural — conservative OE totals ran +$14,633,910,720 (2022) → +$1,118,806,580 (2023) → −$4,315,915,720 (2024) on bank balance-sheet flows, not earnings swings. Handled with the normalized median base and bear-tilted probabilities (45% on bear-or-worse).
- **NI_OCF_DIVERGENCE** (2022, 2023, 2024): not a one-off — for a bank, OCF includes changes in deposits, loans and other operating assets/liabilities, so it diverges from net income by construction (2022: OCF $14,778,701,000 vs NI $2,673,444,000; 2024: OCF −$4,147,022,000 vs NI +$2,145,784,000). No tax-deposit or impairment story explains it; it is the bank cash-flow presentation, and it is the core reason confidence is low.
- **FX_CONVERTED**: KRW figures converted at period-end ECB reference rates (recorded in dcf_numbers.json — e.g. 0.00068 USD per KRW at 2024-12-31); flow facts use the period-end rate, not a period average, so won moves between period ends flow straight into the USD series.
- **USD_TRANSLATIONS_USED**: where Woori files its own USD convenience translations alongside KRW, the engine used the filed USD figures.
- **ADS_RATIO_APPLIED**: ratio 3 declared from the filer's own F-6/20-F (see ADS RATIO section); per-share figures are per ADS. The market-cap artifact is documented there too.
- **SECTOR_MODEL_MISMATCH** (Finance): accepted in full — an OCF-minus-capex owner's-earnings DCF fits a bank poorly; confidence is low and the tier is read as a screen result, not a valuation of the franchise.
- **BASE_DIVERGENCE** (latest FY OE/share −$17.44 per ADS vs 3-yr median $4.46 per ADS): the latest year is the distorted one — FY2024 OCF was −$4,147,022,000 on balance-sheet flows while net income was +$2,145,784,000 and maintenance OE +$2,783,093,000. The median base is the right choice of the two.
- **WIDE_SCENARIO_SPREAD**: fired on the preliminary run (4.52x); on the final run the spread is 3.86x and the flag no longer fires, but the outcome range is still wide — confidence stays low on the sector mismatch and unresolved model limits regardless.

## My thoughts / overlay
- The DCF verdict and the earnings reality point in different directions, and the method range is the honest headline: on the engine's conservative OCF base the ADS yields an 8.9% weighted IRR (Tier D), while the NI-based maintenance OE series is stable and the stock trades at a P/E of 7.46 on the Korea listing (Finnhub) with a guided >50% total shareholder return for 2026. A bank screen on OCF will systematically underrate deposit-funded lenders in loan-growth years; this Tier D says "the OCF model can't clear it," not "the earnings are bad."
- What would change the picture is price, not story: the ADS clears the 15% hurdle only at or below the weighted IV@15 of $35.82 — roughly half the $70.07 price — and a margin of safety against the bear cases ($27.45 / $17.75 IV@15) would require materially less than that.
- Balance-sheet overlay: net debt is not applicable to a bank in this engine (null); CET1 13.71% and an active buyback-and-cancel program are the relevant capital facts, and both are supportive.
- Share count: the engine's share-count trend is +0.66%/yr (slight historical dilution, already charged in the growth blend); the July 2026 cancellation resolution (4,854,368 shares, KRW 150,000M program) works the other way but postdates the filed history.

## Final verdict
- **Final tier: D** (weighted IRR 8.91% on the v5 final inputs; no tier override — the numbers tier stands, with the sector caveat above)
- Confidence: **Low** (Finance sector model mismatch, OCF-based base for a bank, stale FY with no TTM available for an IFRS filer)
- One-liner: Weak-moat (3/10) Korean big-four bank holding company; the OCF-based OE model fits banks poorly (sector mismatch) and even the normalized per-ADS base of $4.46 produces only an 8.9% weighted IRR at $70.07 — Tier D. It would clear the 15% hurdle only at or below the weighted IV@15 of $35.82, roughly half the current ADS price.

## Engine 5.5 re-score (2026-10-19)
This is a dated addendum. The 2026-10-16 text above records that run and has not been rewritten; where it is now out of date (the market-cap and scope paragraph under "ADS RATIO"), the correction is made here. This is a **make_score-only** re-score under ruling 1 ("Re-run make_score (not the engine)"): dcf_engine.py and ttm.py were not run, so dcf_numbers.json, financials_history.csv and the fragility-flag list are the 2026-10-16 engine output unchanged. That output is pre-5.4 (`engine_version` 5, no `engine_release`). Every figure below comes from the regenerated key_numbers.md (or, where named, financials_history.csv and dcf_numbers.json of the same record), except the figures marked "cannot verify from the diff" under "Open items for the next engine re-run": those come from outside this PR and are not applied to this score.

**Runs (2026-10-19).**
- `make_score.py WF`: exit 0, tier D, weighted IRR 8.91%, IV@15 $35.82. It rewrote one judgment.json field (item 2 below) and nothing else in judgment.json.
- `prices.py WF`: exit 0. Warning: the intraday chart request returned no usable points, so the daily series was kept.
- `reprice.py WF`: exit 0. Live tier D, no tier change against the scored run, live cap in scope.
- Audit re-check (2026-10-19): `make_score.py WF` re-run on a scratch copy under the final make_score.py reproduced score.json, key_numbers.md and judgment.json unchanged, so the files in this folder are the final make_score output. It was not re-run in place.

| | 2026-10-16 (pre-5.4 engine, pre-5.5 make_score) | 2026-10-19 (make_score 5.5, same engine output) |
|---|---|---|
| Price (scored) | $70.07 | $70.07 |
| Base OE/share (per ADS, 3-yr median) | $4.46 | $4.46 |
| Weighted IRR · base-case IRR | 8.91% · 8.99% | 8.91% · 8.99% |
| Weighted IV@15% | $35.82 | $35.82 |
| Tier by numbers / final | D / D | D / D |
| Market cap (est) | $52.030B (per-ADS price × ordinary shares) | $17.343B (price × shares ÷ ads_ratio 3; basis `ads_corrected_by_make_score`) |
| `in_scope_under_40b` | false | **true** |
| Net debt (latest) · net debt / normalized OE | — · — | — · — (no ADS-basis ratio to print) |
| Alert gates | not recorded (pre-5.4 score) | `alert_eligible` false · `exit_alert_eligible` false |

**What engine 5.5 changed for WF (applied by make_score)**
1. **Market cap on the ADS basis (ruling 1).** The 2026-10-16 engine priced the 742,537,556 ordinary shares at the per-ADS price, which overstated the cap 3×. The earlier ADS RATIO section already called this an engine artifact. key_numbers.md now prints "$17.343B (ADS-corrected by make_score: price × shares ÷ ratio; the pre-5.5 engine printed $52.030B)", and score.json records `market_cap_basis: ads_corrected_by_make_score`.
2. **Scope (ruling 1, make_score's reading).** key_numbers.md reads "in scope (market cap under $40B) — corrected by make_score from the ADS-corrected market cap (the pre-5.5 engine's cap said out of scope)".
   - judgment.json `in_scope_under_40b` still held the value the old cap implied (false). make_score rewrote that one field to **true**, recorded `in_scope_corrected_by_make_score: true` in score.json and added a `scope_correction` event to the registry.
   - **Scope call: WF is in scope.** The corrected cap is less than half of the $40B line, so the call does not hinge on the price (unlike JD and VOD, which sit near the line).
   - The earlier text leaned on the Korea Exchange market cap to argue WF was really in scope. That argument is no longer needed: the run's own cap now agrees.
3. **Net debt / normalized OE on the ADS basis (ruling 1, "anything downstream").** key_numbers.md prints "Net debt / normalized OE: —" and net debt (latest) "—". There is no ratio to rescale, so neither HIGH_NET_DEBT nor BIG_NET_CASH fires on either basis, and nothing changes.
   - Why there is no ratio: the 2026-10-16 engine mapped no debt tag for this bank. `debt_current` and `debt_lt` are blank in every CSV row, and `net_debt_latest` is null.
   - Resolution, as for a flag: net debt here is unknown, not zero. It is also the wrong measure for a bank, because borrowings and debentures fund the loan book rather than lever an operating business. The balance-sheet verdict stays the regulatory capital position cited in the 2026-10-16 text (CET1, from the Q2 2026 6-K), not a net-debt multiple.
4. **Tier, base and IRR unchanged.** make_score reads the same engine output, so the base ($4.46 per ADS), the weighted IRR (8.91%) and the tier (D) are as recorded. WF has no field override, so no override impact was carried. The band fields (`irr_bear`, `irr_bull`, `tier_bear`, `tier_bull`) are null because the run predates 5.4, which introduced them.
5. **Both alert gates closed until an engine re-run (release mechanics; expected).** make_score treats output from any release other than 5.5.0 as stale.
   - `exit_alert_eligible` is false: "engine output predates release 5.5.0 — re-run the engine before an exit alert; sector model misfit".
   - `alert_eligible` is false. At Tier D there is no entry into S/A to gate, and the sector misfit would suppress one anyway.
6. **Not engaged in this run.**
   - SBC tag (ruling 6): WF is an IFRS filer with no us-gaap Share/Allocated pair; `sbc_tag` stays `ExpenseFromSharebasedPaymentTransactionsWithEmployees`.
   - USD-override branch (ruling 7): no field override (`overrides_applied` is empty), so nothing was converted or used verbatim as USD.
   - Capex tags (rulings 3–5) and share basis (ruling 2): these are engine rules, and the engine was not run. See "Open items for the next engine re-run".

**New 5.5 flags.** None in this run. The flag list is the hashed 2026-10-16 engine output, and make_score adds no flags.
- The eight flags it carries are resolved by name in the 2026-10-16 Flags section, and those resolutions stand: STALE_FY, OE_VOLATILE, NI_OCF_DIVERGENCE, FX_CONVERTED, USD_TRANSLATIONS_USED, ADS_RATIO_APPLIED, SECTOR_MODEL_MISMATCH and BASE_DIVERGENCE.
- ADS_RATIO_APPLIED (ratio 3) now also divides the market cap (item 1).
- The new lines make_score prints (market-cap basis, scope) are diagnostics, not flags. Items 1–3 cover them.

**Open items for the next engine re-run (not applied).** Ruling 1 limits WF to make_score, so none of these is applied to this score. Figures marked "cannot verify from the diff" are not in this PR's files. They come from the retro-scan replay of the 5.5 engine on today's SEC companyfacts (PR-body table (i)) or from the companyfacts feed itself, and they are not this score's figures.

1. **DATA_GAP:shares: the published D sits beside a gap the current rules would raise.** AGENTS.md grades a tier beside an unraised DATA_GAP as P1.
   - dcf_numbers.json `used_tags.shares_diluted` is `WeightedAverageShares`, which the engine treats as a basic-only tag. The IFRS diluted tag `AdjustedWeightedAverageShares` ranks ahead of it and supplied no year. `data_gap` is empty only because the 2026-10-16 record predates the 5.4 rule that makes a non-diluted count in any of the last 3 FY a DATA_GAP:shares. WF has no `shares_override`.
   - The CSV's FY2022–24 counts (728,058,225 / 751,895,516 / 742,537,556) equal the cover-page shares-outstanding counts at each year end in the companyfacts feed. They are period-end outstanding counts, not diluted weighted averages (cannot verify from the diff).
   - The replay exits 4 with DATA_GAP:shares on the basic weighted-average counts 728,000,000 / 735,392,653 / 741,273,152, and adds SHARES_FALLBACK for FY2015–21 (cannot verify from the diff).
   - Worker action on the re-run: a kind "filing" `shares_override` from the 20-F earnings-per-share note, or block. The companyfacts feed shows diluted EPS equal to basic EPS in each year (KRW 4,251 / 3,230 / 3,950 for FY2022 / FY2023 / FY2024). That points to an override that cites "diluted equals basic" the way TX's does (cannot verify from the diff).
   - Decision for Andrew: keep D published until that re-run, or block WF now. The D stands here only because ruling 1 limits WF to make_score.
2. **Intangible capex (ruling 5): the recorded base is about 16% too high.**
   - Recorded capex is the single PP&E tag `PurchaseOfPropertyPlantAndEquipmentClassifiedAsInvestingActivities`: $137,181,000 / $127,572,000 / $150,106,000 for FY2022–24 (financials_history.csv).
   - The 20-F also files `PurchaseOfIntangibleAssetsClassifiedAsInvestingActivities`: $138,668,000 / $176,997,000 / $128,637,000 for FY2022–24 as the replay reads them (cannot verify from the diff: no statements.json in the folder). That answers the single-tag question for a 20-F filer: there is a second investing line of about the same size.
   - Base with the intangible leg, on this record's own share counts: (OCF − PP&E capex − intangible capex − SBC) ÷ CSV `shares_diluted` × 3 gives 59.73 (FY2022) / 3.76 (FY2023) / −17.96 (FY2024) per ADS. The median is **$3.76 per ADS**, against the recorded $4.46. The OCF, PP&E capex, SBC and share legs are the CSV's; the intangible legs are the replay's, so this figure cannot be verified from the diff either. The replay prints 3.842 instead (cannot verify from the diff) because it divides by its own basic weighted-average counts (item 1), not the CSV's.
   - Effect: the published base, the 8.91% weighted IRR and the $35.82 IV@15 are overstated. The base stays positive, so capex alone does not move WF to F. D is the lowest positive band, so the tier is not too high on this account, and both alert gates are already closed.
3. **CAPEX_COVERAGE_LOW would fire**, even with the intangible leg: capex is 37% / 40% / 35% of D&A in FY2022 / FY2023 / FY2024 (replay flag text; cannot verify from the diff). The re-run's analysis must explain this from the 20-F cash-flow statement with a figure. A candidate is not enough. One candidate to test: D&A at a bank includes depreciation of leased branch right-of-use assets (IFRS 16), which has no cash-capex counterpart.
4. **STALE_FY: the 2026-10-16 resolution ("no TTM available") is incomplete.**
   - Woori filed its FY2025 20-F on 2026-04-22 (accession 0001193125-26-168715). SEC companyfacts carries only that filing's cover-page facts (shares outstanding 734,022,375 at 2025-12-31) and no IFRS financial facts, so both the recorded run and the replay stop at FY2024. key_numbers.md shows 21.5 months since FY end. This is a feed gap, not a missing filing (cannot verify from the diff).
   - The 2026-10-16 text used the 6-Ks only for net income.
   - Re-run action: read FY2025 OCF, PP&E and intangible capex, and SBC from the FY2025 20-F cash-flow statement, and check whether the 1H 2026 6-K prints a cash-flow statement. State the FY2025 / TTM OE, then either pin the base from it or escalate as NEEDS_MAIN_AGENT.
   - Why it matters: FY2025 would replace FY2022 in the 3-year window, and FY2022 is the +$14,633,910,720 conservative-OE outlier (financials_history.csv). If FY2025 OE were negative, the median would turn negative and the tier would become F.
5. **Net debt.** The replay reads `Borrowings` as total debt and prints net debt of $2.02B, with no ratio because that run gaps (cannot verify from the diff). For a bank the figure needs the same "funding, not leverage" reading as item 3 of "What engine 5.5 changed for WF".
6. **BASE_DIVERGENCE would drop** from the flag list in the replay (cannot verify from the diff). The 2026-10-16 resolution stands until then.
7. **No override needs restating.** WF carries no field override, so neither the USD-override branch (ruling 7) nor an HTHT-style restatement of a local-currency override applies. SBC (ruling 6) is unchanged in the replay. The share-basis scan (ruling 2) records no split or divergence action for WF.
8. **Correction to the 2026-10-16 text** (the dated record is not rewritten): its WIDE_SCENARIO_SPREAD line quotes a preliminary-run spread of 4.52x, which is in no generated file of this PR. The final run's spread is 3.86x (key_numbers.md), and the flag does not fire.

**Why the tier is what it is.**
- **D by numbers.** The weighted IRR is 8.91%, below the 10% line for C. Even the super-bull scenario (14.75%) stays below 15%.
- **No notch below D.** WF is a sector misfit (Finance, SECTOR_MODEL_MISMATCH; score.json `model_fit: misfit`). The 2026-10-15 policy sizes a misfit's final tier one notch below its numbers tier. There is no scored notch below D: F is reserved for no positive normalized OE, and the base is a positive $4.46. So `tier_override` stays null and the final tier is D.
- **The open items only push down.** The shares gap (item 1) would leave WF with no tier, the intangible leg (item 2) lowers the base to about $3.76 per ADS, and a negative FY2025 OE (item 4) would make WF an F. None of them can raise the tier.
- **The D is provisional.** It is published beside a DATA_GAP:shares that the current rules would raise, and it stands only because ruling 1 limits WF to make_score. Andrew decides whether to keep it until the engine re-run or to block WF now. Queue WF for an engine re-run with a filing-sourced `shares_override` and the FY2025 20-F figures.
- **Confidence stays low.** The reasons: sector misfit, an OCF base for a bank, a stale FY (21.5 months since FY end) whose FY2025 figures the feed does not carry, the pending shares gap, and the missing intangible capex leg.
