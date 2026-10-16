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
