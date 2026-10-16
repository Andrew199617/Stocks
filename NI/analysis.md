# NI — NiSource Inc.
v5 run, 2026-10-16. Price $41.25 (nasdaq_quote_api), market cap $19.573B — in scope under $40B. All figures below are copied from dcf_numbers.json, financials_history.csv, or ttm.py output — none are recomputed. Research figures are attributed to the cited press coverage / company releases.

## What it is
Regulated utility holding company: Columbia Gas distribution (gas utilities across several states) and NIPSCO (Indiana gas distribution plus electric generation/distribution). Essential, monopoly service territories; earnings are whatever regulators allow on an expanding rate base. Currently executing a $28.6B 2026–2030 capital plan — $21.0B base utility investment plus $7.6B of strategic data-center infrastructure (GenCo, serving Amazon and Alphabet agreements approved by Indiana regulators) — guided to support 9%–11% rate-base growth and 9%–10% adjusted EPS CAGR 2026–2033 (company Q2 2026 release, Business Wire). Q2 2026: GAAP net income $45.5M / $0.09 diluted EPS (vs $102.2M / $0.22 a year ago), adjusted EPS $0.16; H1 2026 adjusted EPS $1.22 vs $1.19; 2026 adjusted EPS guidance reaffirmed at $2.02–$2.07 (company Q2 2026 release).

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** revenue $6,522,800,000; net income $929,500,000; operating cash flow $2,362,300,000; capex $2,782,300,000 (tag PaymentsToAcquirePropertyPlantAndEquipment); D&A $1,167,670,000; SBC $50,900,000 (a real cost, but small here).
- **Conservative owner's earnings FY2025: −$470,900,000 = −$0.99/share** (base_oe_latest_per_share −0.9924130663856692). FCF −$420,000,000.
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): **+$1,191,500,000** — positive, and the gap between the two definitions is the whole story of this name: the maintenance version caps capex at D&A, while the conservative version charges the full $2,782,300,000. Most of that capex is rate-base growth and data-center build, not upkeep of the existing system — but under the sweep's standardized conservative definition it is all charged, every year.
- **OE positive 0 of the last 5 fiscal years** (oe_positive_years_of_last_5: "0/5"). Conservative OE by year (financials_history.csv): FY2021 −$644,400,000; FY2022 −$818,600,000; FY2023 −$744,200,000; FY2024 −$876,100,000; FY2025 −$470,900,000. This is structural, not a one-off year: capex has exceeded OCF in every year of the 10-year history shown.
- **Base used = the engine's normalized base (median of last 3 FY OE/share): −$1.66/share** (base_oe_normalized_per_share −1.6615315918731859). The latest year (−$0.99/share) is less negative but still negative, so no defensible base pin changes the verdict — there is no positive base to pin. A TTM base was attempted and failed (see STALE_FY under Flags).
- Growth inputs (reported, not used — no DCF runs on a negative base): rev CAGR 5y 7.84%, rev CAGR 3y 4.36%, latest revenue YoY +23.47%, blended growth 7.84%, share-count CAGR +2.34%/yr with a −2.34pp share-count adjustment (dilution, see Flags/thoughts).
- Balance sheet caveat: the engine prints net_debt_latest of −$90,400,000, but the debt_lt column in financials_history.csv is blank for every year, so that figure captures only current debt minus cash and must NOT be read as a net-cash position. Leverage is in fact material for this name: secondary coverage of the filings put long-term debt at $15.48B carrying amount plus $1.29B commercial paper at March 31, 2026 (StockTitan 10-Q summary), and the financing plan calls for roughly $400M–$600M of new equity per year alongside new long-term debt (company earnings-call remarks, Q1/Q2 2026).

## Moat: 5/10 — moderate: a real regulated monopoly, with the return capped by the regulator
Justification: Exclusive regulated service territories and essential service make the franchise durable, but NiSource owns no pricing power beyond what commissions grant, allowed ROE is under active scrutiny in Indiana, and the equity story depends on regulators continuing to let a very large capex program into rate base.
- FOR: Exclusive regulated monopoly territories (Columbia Gas, NIPSCO) — customers cannot switch providers
- FOR: Essential gas and electric service with inelastic demand
- FOR: Rate-base growth engine — $28.6B 2026–2030 plan guided to 9%–11% rate-base growth, with Amazon/Alphabet data-center agreements already approved in Indiana
- FOR: Long-lived infrastructure franchise; the asset base compounds through tracker/modernization recovery mechanisms
- AGAINST: Returns are capped by regulators — no pricing power beyond rate cases and trackers
- AGAINST: Indiana ROE and tracker proceedings under scrutiny (BMO cut its target $49 → $45 on 2026-09-28 citing regulatory clarity, per press coverage)
- AGAINST: Perpetual external financing — ~$400M–$600M/yr of planned equity issuance dilutes (share count CAGR +2.34%/yr) and the debt load makes earnings rate-sensitive
- AGAINST: GenCo data-center build adds large-load / counterparty and execution risk outside the traditional regulated model
- A 5 gives CAP = 8.5 years (growth would hold 2 years, then converge linearly to the 2.5% terminal rate over 8.5 years, 15-year projection) — moot here, because no scenario DCF is emitted on a negative base.

## DCF — v5 final run (2026-10-16)
Final engine pass: `dcf_engine.py NI --moat 5 --probs 0.10,0.25,0.30,0.25,0.10` with default offsets (−12/−5/0/+5/+12pp) and default OE multipliers (0.75/0.90/1.00/1.10/1.25).

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | n/a | 0.75 | Not emitted — base OE is negative | n/a | n/a |
| Bear | 25% | n/a | 0.90 | Not emitted — base OE is negative | n/a | n/a |
| Base | 30% | n/a | 1.00 | Not emitted — base OE is negative | n/a | n/a |
| Bull | 25% | n/a | 1.10 | Not emitted — base OE is negative | n/a | n/a |
| Super bull | 10% | n/a | 1.25 | Not emitted — base OE is negative | n/a | n/a |

- **Probability-weighted IV/IRR: none.** The engine's note states it directly: "No positive NORMALIZED (3-yr median) conservative owner's earnings — OE DCF not supportable on numbers alone." **Tier by numbers: F.**
- Sanity check on scenario growth starts is not applicable in the usual form: there are no scenario starts because there is no positive base to grow. The company's own guided adjusted EPS CAGR of 9%–10% (2026–2033) does not rescue the OE math — it is earnings on a rate base funded by capex that the conservative OE definition charges in full, plus $400M–$600M/yr of new equity.
- Price that clears 15%: none exists on this method. With normalized OE/share of −$1.66, no entry price produces a 15% owner's-earnings IRR in this model; the hurdle question would have to be asked with a utility-appropriate method (dividend / FFO / rate-base earnings), which is outside this sweep.

## Flags — every fragility flag resolved
- **STALE_FY** (latest FY ended 2025-12-31, 9 months before this run): ttm.py was run as required and **exited non-zero (exit 3)** with: "ttm.py: cannot compute TTM for NI (CIK 1111711): sbc: no post-FY YTD fact (no 10-Q since the 2025-12-31 fiscal year end)". Per the sweep rules the engine's median base is used instead, with the reason stated here: no TTM pin exists. (Q2 2026 results do exist in press coverage — adjusted EPS $0.16, H1 adjusted EPS $1.22 — but ttm.py requires filed YTD SBC facts and found none it could use; and since both the median base and the latest FY are negative, a TTM pin could not change the tier in any case.) No --ttm was passed to the final engine run.
- **NI_OCF_DIVERGENCE** (net income vs operating cash flow differ by >40% in 2023 and 2025): resolved — this is structural utility depreciation, not a one-off. FY2023: net income $714,300,000 vs OCF $1,935,100,000, with D&A of $908,200,000. FY2025: net income $929,500,000 vs OCF $2,362,300,000, with D&A of $1,167,670,000. The non-cash D&A charge explains the bulk of the gap in both named years; the remainder is working-capital movement (delta_nwc −$870,300,000 in 2023 and −$262,000,000 in 2025, financials_history.csv). No tax deposit, impairment, or one-off gain was found in research for those years. The divergence does not flatter the OE base — the base is built from OCF, and it is negative anyway.
- **SECTOR_MODEL_MISMATCH** (Utilities): accepted in full. The OE/capex DCF fits utilities poorly — for a regulated utility, capex is predominantly growth investment that earns an allowed return through rate base, so charging it all against current OCF mechanically produces negative owner's earnings even in good years (0/5 positive years here, including years when adjusted EPS grew). Confidence is graded **low** and the F tier is a statement about this method applied to this sector, not a claim that the equity is worthless.

## My thoughts / overlay
- The honest headline is the method range, and it is extreme: on the conservative OE definition this is an F (negative base, no DCF possible); on the maintenance definition FY2025 OE was +$1,191,500,000 — the difference is entirely whether growth capex for rate-base and data-center expansion counts as a current cost. Andrew's sweep standardizes on the conservative definition, so F is the recorded verdict, sized with low confidence because of the sector mismatch.
- Quality underneath the F: a durable regulated franchise growing adjusted EPS (FY2025 adjusted EPS $1.90 vs $1.75 in FY2024, company release), guidance reaffirmed, and a genuinely new growth leg in approved hyperscaler data-center agreements. None of that is visible to an OCF-minus-all-capex screen.
- Real risks that have nothing to do with the method: regulatory pushback in Indiana (ROE/tracker scrutiny; BMO target cut), execution and counterparty risk on the $7.6B data-center program, rate sensitivity of a heavily levered balance sheet (the engine's net-debt line is unusable here — see the balance-sheet caveat above), and steady dilution from the planned $400M–$600M/yr equity issuance on top of the +2.34%/yr historical share-count CAGR.
- SBC is not a factor: $50,900,000 in FY2025 against OCF of $2,362,300,000.

## Final verdict
- **Final tier: F** (tier by numbers F; no tier override — the numbers say what the method says, and the method's limits are documented above rather than papered over with an override)
- Confidence: **Low** (SECTOR_MODEL_MISMATCH: the OE/capex DCF fits utilities poorly; treat the F as method-bound)
- One-liner: Regulated utility monopoly, moat 5/10 — conservative owner's earnings are negative in all of the last 5 fiscal years (capex for rate-base and data-center growth far exceeds OCF), so the OE DCF returns Tier F at $41.25 with no hurdle-clearing price on this method; verdict is method-bound, confidence low.
