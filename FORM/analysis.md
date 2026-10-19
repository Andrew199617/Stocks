# FORM — FormFactor, Inc.
Engine 5.4.0 pass-1 run, 2026-10-18. All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.json or fundamentals.json — none are recomputed.

## What it is
The #1 global supplier of wafer probe cards and related test/measurement systems (Livermore, CA; SIC 3674): MEMS, vertical and cantilever probe cards plus probe stations used to test DRAM/HBM, foundry & logic and RF devices at the wafer stage. Demand is riding the AI cycle — HBM4 test intensity, data-center logic, and co-packaged-optics systems. Q2 2026 was a record quarter: revenue $258,242,000 (fundamentals.json quarterly; reported +31.9% YoY), GAAP gross margin 50.7% in the quarter, and management guided Q3 2026 revenue to $270M ± $10M with a multi-year target model of ~$1.6B revenue by 2030. Price $105.01 (nasdaq_quote_api), market cap (est) $8.224B — in scope under $40B.

## Owner's earnings
**FY2025 (10-K via EDGAR, financials_history.csv):** revenue $784,993,000; operating cash flow $115,398,000; capex $103,658,000; SBC $38,576,000 (always a real cost).
- **Conservative owner's earnings FY2025: −$26,836,000 = −$0.34/share** (key_numbers.md: latest FY OE/share $-0.34). The year was consumed by the Farmers Branch, Texas fab build — capex of $103,658,000 vs $38,436,000 in FY2024 and $56,027,000 in FY2023, with $84,840,000 of it in H1 2025 alone (ttm.json capex legs); the 10-K describes significant investment in the new manufacturing site, and FY2025 opex already carries $3,025,000 of factory start-up costs.
- Maintenance version FY2025 (NI + D&A − min(capex, D&A) − ΔNWC, financials_history.csv): $7,553,000 — also essentially zero. Both definitions agree FY2025 produced no meaningful owner's earnings at the filed capex level.
- The 3-yr median window is worse than any single story: FY2023 OE −$30,041,000 (−$0.38/share), FY2024 +$39,335,000 (+$0.50/share), FY2025 −$26,836,000 (−$0.34/share); normalized (median) base **−$0.34/share**. The preliminary engine run on that base printed Tier F with sub-type `sbc_exceeds_cash` (OCF − capex is positive over the window; SBC consumes it) — OE-positive years are only 3 of the last 5.
- Balance sheet is not the problem: net debt −$91.1M (net cash; key_numbers.md), lease liabilities $20,150,000 (dcf_numbers.json), equity $1,035,403,000 (financials_history.csv).

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $115,398,000 − prior YTD $42,432,000 + current YTD $106,764,000 = **TTM $179,730,000**
- Capex: FY $103,658,000 − prior YTD $84,840,000 + current YTD $24,791,000 = **TTM $43,609,000** (the Farmers Branch spike annualizes out; the TTM leg still carries ramp spend, so this base is if anything conservative)
- SBC: FY $38,576,000 − prior YTD $19,187,000 + current YTD $16,721,000 = **TTM $36,110,000**
- Shares (current-YTD weighted diluted): **79,546,000**
- **TTM OE total $100,011,000 → base OE/share $1.26** (base_source: ttm_json; exact $1.2573 in dcf_numbers.json)
- TTM context (fundamentals.json): revenue $902,225,000, gross margin 43.1%, operating income $115,942,000, net income $115,465,000. The TTM base is the right one: it is the first window in which the AI/HBM demand surge and normalized capex coexist. Even so, base OE yield is only **1.20%** at $105.01 — the entire valuation question is growth, which is what the scenarios are for.

## Moat: 5/10 — moderate/narrow
Justification: #1 global probe-card supplier with qualification stickiness and a MEMS lead, but measured returns are mediocre and falling, and five years of flat gross margin say pricing power was unproven until this cycle.
- FOR: #1 global probe-card supplier (~22-25% share; TechInsights #1 in Test Subsystems for 13 consecutive years); probe cards are qualified per device and process — requalification friction makes incumbency sticky at TSMC, Samsung, Intel and the memory makers; MEMS / advanced-probe technology lead for HBM and advanced packaging, with a reported second-source position for Nvidia GPU probe cards at TSMC (Deutsche Bank initiation, Sept 2026); net-cash balance sheet (net debt −$91.1M) funds the Farmers Branch build through the cycle.
- AGAINST: ROIC proxy (fundamentals.json, after-tax operating income over equity + debt − cash) ran 13.1% / 12.1% / 6.7% / 10.2% / 7.4% / **4.9%** across FY2020–25 — positive but near the cost of capital and falling into the cycle peak, not "well above through a cycle"; GAAP gross margin was flat at 41.5% / 41.9% / 39.6% / 39.0% / 40.3% / 39.3% over the same years (the Q2 2026 jump to 50.7% GAAP is one quarter, at peak mix); Technoprobe is a strong #2 (~16% share) with Micronics Japan, MPI and low-cost Chinese entrants behind it; revenue is concentrated in a handful of memory/logic customers and is violently cyclical (revenue −11% in FY2023); SBC consumes most of pre-SBC cash generation in soft years.
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — final run (2026-10-18)
Growth recalibration (written reason): the engine's blended growth of 2.46% is built entirely from filed history through FY2025 (rev CAGR 5y 2.50%, 3y 1.63%, latest YoY 2.80% — key_numbers.md) and is stale against the actual prints: Q2 2026 revenue +31.9% YoY, Q3 2026 guided to $270M ± $10M, TTM revenue $902,225,000 vs $784,993,000 for FY2025, and a management target model of ~$1.6B revenue by 2030. Scenario starts were therefore set via offsets (−0.075 / +0.005 / +0.095 / +0.175 / +0.255 vs the blend) to −5.0 / +3.0 / **+12.0** / +20.0 / +28.0%. The base start of 12.0% sits below the current revenue prints and below the ~2030 target-model trajectory because OE must also absorb Farmers Branch start-up costs and a normal semi cycle inside the window; the super-bull start of 28.0% sits just under the Q2 print (+31.9%) for the same reason — OE leverage at peak gross margin cuts both ways. Probabilities were shifted defensive (15/30/30/17/8 vs the 10/25/30/25/10 default) for cyclicality and customer concentration. OE multipliers are the defaults 0.75/0.90/1.00/1.10/1.25. Price $105.01.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | -5.0% | 0.75 | AI test demand rolls over like 2023 (revenue −11%, OE negative); Farmers Branch fixed costs land on falling volume | $5.64 | 3.10% |
| Bear | 30% | 3.0% | 0.90 | 2026 surge annualizes, then the cycle flattens; GM gives back the peak mix | $9.46 | 3.63% |
| Base | 30% | 12.0% | 1.00 | HBM/logic demand compounds toward the 2030 target model, one normal downturn inside the CAP | $15.24 | 4.50% |
| Bull | 17% | 20.0% | 1.10 | Nvidia GPU second-source ramps at TSMC; HBM4 supercycle extends; Farmers Branch accretive at scale | $23.20 | 5.69% |
| Super bull | 8% | 28.0% | 1.25 | Target model beaten — revenue doubles early, >55% gross margin, OE leverage compounds | $36.27 | 7.53% |

- **Probability-weighted: IV@15% $15.10 (−85.6% vs price), IV@12% $20.44, IV@10% $26.43, weighted IRR 4.52%, base-case IRR 4.50%**
- **Tier by numbers: D** — and the band is D at both ends (bear 3.63% tier D → bull 5.69% tier D; full scenario range 3.10%–7.53%, all D). Diagnostics (key_numbers.md): OE yield 1.20%, terminal value 20.6% of IV@15%, scenario spread 6.43x, net debt −0.93x normalized OE, 9.7 months since FY end.
- **Hurdle-clearing prices (weighted path): 15% at $15.10 · 20% at $10.37 · 25% at $7.80.**

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.7 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026 (filed 2026-08-04), legs quoted above.
- **NI_OCF_DIVERGENCE** (2024, 2025): identified, and it does not contaminate the OCF-based base. In both years OCF far exceeds net income (2024: NI $69,614,000 vs OCF $117,534,000; 2025: NI $54,361,000 vs OCF $115,398,000 — financials_history.csv) because non-cash addbacks are huge relative to earnings: D&A + SBC were $72,666,000 in 2024 ($32,903,000 + $39,763,000) and $76,165,000 in 2025 ($37,589,000 + $38,576,000). The 2024 gap exists despite NI carrying a $20,581,000 gain on sale of business that is stripped back out in the OCF reconciliation; 2025 was partly offset by working-capital drag (the 10-Q shows "other activity impacting operating cash flows" of −$32,838,000 for the first nine months, including a $9,922,000 excess/obsolete inventory provision). No tax-deposit or impairment one-off distorts the OCF series itself.
- **LOW_OE_YIELD** (base OE yield 1.2%): real and decisive — at $105.01 the valuation rests almost entirely on growth. Handled by sizing the verdict to the conservative end: even the super-bull path (28% growth start, 1.25x OE) yields only a 7.53% IRR, so the fragility does not rescue the tier.
- **WIDE_SCENARIO_SPREAD** (6.43x): real — the outcome range is genuinely wide (a cyclical at an inflection). Confidence is capped at medium, and both the bear→bull band and the full scenario range sit entirely in Tier D, so the spread does not change the verdict.
- Preliminary-run note (not an engine flag on the final run): the normalized-median base printed Tier F, sub-type `sbc_exceeds_cash`. That window (FY2023–25) mixes the 2023 downcycle and the Farmers Branch capex spike with SBC of $38,576,000–$39,763,000/yr; the TTM base supersedes it on current evidence, and the F print is retained here as the conservative end of the method range.

## My thoughts / overlay
- The honest headline is the *range* across defensible methods: Tier F on the filed 3-yr median base, Tier D on the current TTM base — and no defensible path gets near the price. Even granting the TTM base, a 28% super-bull growth start and a 1.25x OE multiplier, IV@15% is $36.27, roughly a third of the $105.01 price. The stock is priced for the 2030 target model ($1.6B revenue, >55% gross margin) to arrive early and then keep compounding; the owner's-earnings math pays for none of that today.
- Business quality is genuinely improving — record Q2 2026, GAAP gross margin 50.7% in the quarter, TTM OCF $179,730,000, net cash — but the through-cycle record is a ~5-13% ROIC, ~40% gross-margin, SBC-heavy cyclical whose conservative OE was negative in 2 of the last 3 fiscal years. Quality at the wrong price is still the wrong price: at ~83x TTM owner's earnings there is no margin of safety against the bear cases (super-bear IV@15% $5.64).
- Risks to this verdict (i.e., what would make it wrong): the Nvidia GPU probe-card second-source win scaling faster than the bull case, HBM test intensity structurally repricing probe-card content per wafer, or Farmers Branch delivering >55% gross margins at scale years early. Those are exactly the super-bull inputs, and they still do not clear 15% at $105.01.

## Final verdict
- **Final tier: D** (weighted IRR 4.52% on the TTM base; method range F on the filed median base to D on TTM — every scenario, bear to super bull, is D)
- Confidence: **Medium** (filing data complete, no data gaps, TTM legs clean; capped by the 6.43x scenario spread and the 1.2% OE yield)
- One-liner: Real AI/HBM wafer-test franchise, moat 5/10, but at $105.01 the price embeds far more than even the super-bull owner's-earnings path delivers — weighted IRR 4.52%, weighted IV@15% $15.10 vs $105.01; it clears a 15% hurdle only near $15.
