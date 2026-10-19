# TRMB — Trimble Inc.
Pass-1 run, 2026-10-17, engine 5.4.0. All figures below are copied from dcf_numbers.json, ttm.json, fundamentals.json, financials_history.csv, or the cited company press releases — none are recomputed.

## What it is
Positioning/GNSS technology and workflow software for construction, geospatial, agriculture and transportation, under a "Connect & Scale" pivot from hardware to subscriptions: segments AECO (architecture/engineering/construction software), Field Systems (GNSS hardware + positioning services, incl. the retained GNSS supply to the PTx Trimble JV), and Transportation & Logistics (Transporeon + telematics software). ARR was $2.51B at Q2 2026, up 14% YoY (Trimble Q2 2026 release, 2026-08-12). Price $59.46 (nasdaq_quote_api); market cap est. $14,359,590,000 — in scope under $40B. No dividend; capital return is buybacks ($875.4M repurchased in FY2025 per the FY2025 results release; new $1.0B authorization approved 2026-08-12).

## Owner's earnings
Conservative OE = OCF − capex − SBC (SBC always a real cost). Maintenance OE = NI + D&A − min(capex, D&A) − ΔNWC.
- **FY2025 (ended 2026-01-02):** OCF $386,200,000; capex $25,300,000; SBC $146,500,000 → conservative OE $214,400,000 = **$0.89/share**. Maintenance OE $467,100,000 — higher, because net income carries non-cash charges the OCF line already absorbs differently; the conservative figure is the one used.
- **History (conservative OE/share):** FY2023 $1.64, FY2024 $1.37, FY2025 $0.89; 3-yr median (engine normalized base) **$1.37/share**. OE positive 5 of the last 5 fiscal years.
- **FY2025 is the distorted year, not the median and not the trend:** FY2025 OCF absorbed a $311,200,000 decrease in income taxes payable (FY2025 cash-flow statement, via the FY2025 results release), including ~$277.4M of cash taxes on the April 2024 Ag divestiture gain. That is a one-off cash tax on a non-operating gain, paid out of OCF.
- **Base used = TTM owner's earnings through Q2 2026 (period ended 2026-07-03), from ttm.py, filing-direct:**
  - OCF: FY $386,200,000 − prior YTD $102,100,000 + current YTD $515,000,000 = **TTM $799,100,000**
  - Capex: FY $25,300,000 − prior YTD $12,500,000 + current YTD $13,200,000 = **TTM $26,000,000**
  - SBC: FY $146,500,000 − prior YTD $76,300,000 + current YTD $85,100,000 = **TTM $155,300,000**
  - Shares (current-YTD weighted diluted): **233,700,000**
  - **TTM OE total $617,800,000 → base OE/share $2.6436** (base_source: ttm_json)
  - The TTM window drops the H1-2025 tax-payment bulge (prior-YTD leg) and replaces it with H1 2026, so the base is the cleanest filing-derived run-rate available. It is still stress-tested below: on the engine's median base ($1.37) the preliminary run printed weighted IRR 4.73% — Tier D either way.

## Moat: 6/10 — moderate, real but not wide
Justification: installed-base GNSS/positioning leadership plus construction-workflow software with genuine switching costs and a 70%-ish recurring mix, but returns on capital are only mid-single-to-high-single digits — the measured franchise does not support a 7+.
- Evidence first (fundamentals.json): gross margin has climbed every year on the software mix shift — 55.6% (FY2021) → 57.3% → 61.4% → 65.1% → 69.1% (FY2025), TTM 69.8%. But roic_proxy (after-tax operating income over equity + debt − cash) ran only 9.8% / 7.2% / 5.0% / 5.4% / 7.1% over the same five fiscal years — around the cost of capital, not well above it, because the balance sheet carries acquisition goodwill (incl. Transporeon) that keeps writing down (see Flags).
- FOR: GNSS/positioning technology leadership with a large installed field base; AECO software (Tekla/SketchUp/Viewpoint-class workflows) embedded in construction processes — real switching friction; ARR $2.51B growing 14% with record Q2 gross margins; exclusive GNSS/guidance supply agreement into PTx Trimble (AGCO) locks in a channel.
- AGAINST: ROIC ~5–10% through the cycle — no proven wide-moat economics yet; serial-acquirer goodwill keeps impairing ($562.0M T&L goodwill impairment in Q2 2026 alone); competition from Autodesk, Hexagon, Topcon and OEM in-sourcing (Deere, Caterpillar); construction-cycle exposure in Field Systems hardware; T&L under strategic review (announced 2026-08-12) — portfolio still unsettled; material weaknesses in internal controls disclosed in 2025 filings and under remediation.
- A 6 gives CAP = 9.8 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 9.8 years, 15-year projection.

## DCF — final run (2026-10-17)
Growth recalibration (written reason): the engine's blended start is −0.54% (components: rev CAGR 5y +2.65%, rev CAGR 3y −0.81%, latest rev YoY −2.61%, OE/share CAGR 2y −26.39%). Every one of those components straddles the basis break — the Ag business was deconsolidated into PTx Trimble on 2024-04-01 and the global transportation telematics business was sold to Platform Science (closed Feb 2025) — so the consolidated history mechanically shows shrinkage the continuing business is not experiencing. Post-divestiture prints: Q2 2026 revenue $972.0M, +11% YoY (+10% organic); ARR +14% (+12% organic); FY2026 guidance raised to $3.90–3.95B revenue vs $3,587,300,000 filed for FY2025 (Trimble Q2 2026 release). Scenario starts were therefore set on continuing-business evidence via offsets (−0.0446 / +0.0254 / +0.0954 / +0.1454 / +0.2054 vs g_base): super bear −5% (construction recession), bear +2%, base +9% (guided growth, held flat — OE/share also gets buyback help not counted here), bull +14% (the ARR growth rate), super bull +20%. Probabilities 10/25/30/25/10; OE multipliers 0.75/0.90/1.00/1.10/1.25 (defaults kept).

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | −5.0% | 0.75 | Construction downturn; T&L review ends in a weak sale; hardware slump | $11.65 | 4.69% |
| Bear | 25% | +2.0% | 0.90 | Organic growth decays to low-single digits; mix gains stall | $19.08 | 6.49% |
| Base | 30% | +9.0% | 1.00 | Guided FY2026 growth holds, then fades over the 9.8-yr CAP | $28.95 | 8.86% |
| Bull | 25% | +14.0% | 1.10 | ARR compounds at its current rate; buybacks add per-share torque | $39.75 | 11.23% |
| Super bull | 10% | +20.0% | 1.25 | Software re-rating path: AECO + Field Systems both compound high-teens | $58.84 | 14.89% |

- **Probability-weighted: IV@15% $30.44 (−48.8% vs the $59.46 price), IV@12% $41.09, IV@10% $53.06 (dcf_numbers.json weighted), weighted IRR 9.24%, base-case IRR 8.86%.**
- **Tier by numbers: D** (bear D, bull C). Diagnostics: OE yield 4.45%, terminal value 20.4% of IV@15%, scenario spread 5.05x, net debt 1.78x normalized OE, 9.46 months since FY end.
- Balance sheet: net debt $1,138,800,000 at FY2025 end (debt basis LongTermDebtNoncurrent+none in dcf_numbers.json), plus lease liabilities $168,900,000. Hurdle prices (weighted): clears 15% only at **$30.44**, 20% at $20.98, 25% at $15.86.

## Flags — every fragility flag resolved
- **STALE_FY** (latest FY ended 9.46 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026 (period ended 2026-07-03), legs quoted above.
- **BASE_DIVERGENCE** (latest FY $0.89 vs 3-yr median $1.37): the latest FY is the distorted one — FY2025 OCF paid ~$277.4M of cash taxes on the 2024 Ag divestiture gain (income taxes payable −$311,200,000 in the FY2025 cash-flow statement). The TTM base ($2.64) excludes that bulge; the median is retained in reporting, and the tier is D on both bases.
- **NI_OCF_DIVERGENCE** (2023, 2025 in the preliminary run's labels — the filing years ended 2023-12-29 and 2025-01-03): FY2024 net income of $1,504,400,000 contains the $1,687,900,000 pre-tax divestiture gain on PTx Trimble (closed 2024-04-01; $1.9B cash proceeds; Trimble kept 15%) — a non-operating gain that never touches OCF, which is why NI ≫ OCF that year. The 2023 gap runs the other way (NI $311,300,000 vs OCF $597,100,000) on $250,600,000 of D&A. The OCF-based conservative OE series used throughout is unaffected by either.
- **WIDE_SCENARIO_SPREAD** (super-bull IV 5.05x super-bear): real — the range is driven by whether the post-divestiture software growth rate (ARR +14%) or the consolidated-history shrinkage is the true run-rate. Confidence is capped at medium and the verdict is sized to the conservative end.
- **TIER_BAND** (bear D 6.49% vs bull C 11.23%): the verdict spans tiers; sized to the bear end — even the bull case (11.23%) does not clear 15%.
- **HIGH_NET_DEBT** (preliminary run, 3.44x the median-based normalized OE): on the TTM base the final run measures net debt at 1.78x normalized OE ($1,138,800,000 net debt, plus $168,900,000 of lease liabilities). Leverage is moderate, not distressing, after the post-JV debt repayment — but it is why the super-bear OE multiplier (0.75) bites: levered OE/share falls faster than revenue in a downturn.

## My thoughts / overlay
- The honest headline is the method range: median base → weighted IRR 4.73%; TTM base with divestiture-cleaned growth → 9.24%. Both are Tier D, and even the super-bull case (IRR 14.89%, IV@15% $58.84) does not clear 15% at $59.46 — remarkably, the super-bull IV@15% is essentially the current price. The market is pricing Trimble as if the bull path is the base path.
- Quality is genuinely improving: gross margin 55.6% → 69.1% in four years on mix, ARR +14%, guidance raised in Q2 2026, buybacks shrinking the count (diluted shares 241,500,000 FY2025 → 233,700,000 current-YTD). None of that is in dispute — the dispute is only the price. At $59.46 against TTM OE/share of $2.6436 (an OE yield of 4.45%, per key_numbers.md) for a company with ~7% ROIC, there is no margin of safety.
- Watch items: the T&L strategic review outcome (a clean sale at a good price would simplify the story and cut goodwill risk); whether H2 2026 OCF confirms the TTM run-rate or H1 was working-capital timing; remediation of the disclosed material weaknesses; further goodwill impairments.
- What would change the verdict: a price near $30 (the 15% hurdle price on weighted cash flows), or two more years of ARR compounding at mid-teens with ROIC pushing into double digits — that combination would justify re-basing growth and moat upward.

## Final verdict
- **Final tier: D** (weighted IRR 9.24%; tier D on both the median and TTM bases; bull case only C)
- Confidence: **Medium** (every flag resolved with filing evidence; capped by the 5.05x scenario spread)
- One-liner: Improving software-quality compounder, moat 6/10 — but at $59.46 the market already prices the bull case: weighted IRR 9.24%, IV@15% $30.44; it clears 15% only near $30.
