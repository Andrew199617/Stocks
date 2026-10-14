# DXCM — Dexcom, Inc.
v5 run, 2026-10-14. In scope (market cap $34,055,917,500 at $83.985, nasdaq_quote_api).

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.py output, or financials_history.csv — none are recomputed. Guidance and market figures are from the cited Q2 2026 earnings reporting.

## What it is
Continuous glucose monitoring (CGM) for diabetes: a wearable sensor (G7, including the 15-day version, plus the over-the-counter Stelo) replaced every 10–15 days, a transmitter/app ecosystem, and data sharing with clinicians and caregivers. Revenue is mostly recurring disposable sensors, reimbursed by Medicare, Medicaid, and most US commercial insurers for eligible Type 1 and Type 2 patients. Q2 2026: revenue $1.308 billion, up 13% year over year (US up 11%, international up 19%); full-year 2026 revenue guidance raised to $5.18–$5.25 billion (approximately 11–13% growth), with non-GAAP gross margin guidance of approximately 64% and non-GAAP operating margin guidance of 23.5–24%.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** revenue $4,662,000,000; net income $836,300,000; operating cash flow $1,440,700,000; capex $363,500,000 (tag: PaymentsToAcquirePropertyPlantAndEquipment); SBC $159,600,000 (tag: ShareBasedCompensation) — always a real cost.
- **Conservative owner's earnings FY2025: $917,600,000 = $2.26/share** (base_oe_latest_per_share $2.26288532675709).
- Maintenance version FY2025: $626,500,000 — lower than the conservative figure, mainly because the maintenance definition subtracts the increase in net working capital printed in the history; the two definitions bracket the base rather than agree on it, which is one reason the verdict is not sized aggressively.
- OE positive 4 of the last 5 fiscal years (FY2021 conservative OE was negative on heavy capex).
- The engine reports net_debt_latest as null, so no net-debt or net-cash figure is quoted here and no balance-sheet adjustment is folded into the verdict beyond what is already in the cash-flow history.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $1,440,700,000 − prior YTD $486,800,000 + current YTD $794,800,000 = **TTM $1,748,700,000**
- Capex: FY $363,500,000 − prior YTD $181,100,000 + current YTD $161,300,000 = **TTM $343,700,000**
- SBC: FY $159,600,000 − prior YTD $79,500,000 + current YTD $82,300,000 = **TTM $162,400,000**
- Shares (current-YTD weighted diluted): **391,800,000**
- **TTM OE total $1,242,600,000 → base OE/share $3.1715160796324655** (base_source: ttm_json)
- The engine's normalized base (median of last 3 FY OE/share) is $1.1153380179307002/share — rejected as the base: it is the median year FY2024, and it sits below both the latest FY ($2.26/share) and the TTM figure, because FY2023–FY2024 predate the margin/OCF step-up that FY2025 and H1 2026 printed. The median is distorted here, not the latest year (see BASE_DIVERGENCE below).

## Moat: 6/10 — moderate-strong, not wide
Justification: a duopoly CGM franchise with recurring disposable revenue, pump/app integrations, and reimbursement coverage, held back by a close, larger, cheaper substitute (Abbott FreeStyle Libre), payer/CMS pricing power, and product-quality/regulatory exposure — pricing power is real but contested, not structural.
- FOR: Recurring disposable sensor revenue — the sensor is replaced every 10–15 days, so the installed base re-buys continuously
- FOR: Integration switching costs — iCGM integrations with insulin pumps, smartphones/watches, and clinician/caregiver data sharing (Dexcom Share)
- FOR: US CGM leadership and clinician/patient brand, with reimbursement coverage across Medicare, Medicaid, and most commercial insurers
- FOR: Scale manufacturing and margin proof — Q2 2026 gross margin expanded sharply on G7 15-day efficiencies, and H1 2026 free cash flow more than doubled year over year per earnings reporting
- FOR: Expansion runway — Type 2 non-insulin users (CONNECT trial results), Stelo OTC, and international growth (up 19% in Q2 2026)
- AGAINST: Abbott FreeStyle Libre — a close substitute with larger global scale and an aggressive lower-price strategy; Dexcom has already cut sensor pricing in response per industry reporting
- AGAINST: Payer power — potential CMS competitive bidding / pricing pressure can reset reimbursement regardless of product quality
- AGAINST: Product quality and regulatory exposure — sensor recalls/adverse-event scrutiny and an ongoing CEO/leadership transition flagged in earnings coverage
- AGAINST: No owned distribution or payer channel — Dexcom rents access through distributors, pharmacies, and payers it does not control
- A 6 gives CAP = 9.8 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 9.8 years, 15-year projection.

## DCF — v5 final run (2026-10-14)
Growth recalibration (written reason): the engine's g_base is 19.92% (blended growth 18.17% — median of revenue CAGR 5y 19.33%, revenue CAGR 3y 17.01%, latest revenue YoY 15.60%, OE/share CAGR 2y 63.24% — plus a +1.75pp share-count adjustment for the falling share count). That 19.92% OE-growth start is **recalibrated down** in every scenario, for one specific reason: the TTM base already captures the margin step-up (Q2 2026 gross and operating margins jumped year over year on G7 15-day efficiencies), and FY2026 margin guidance sits at roughly the Q2 level rather than promising a second identical step-up. Projecting 19.92% OE growth off the already-expanded TTM base would double-count that leverage. The recalibrated base start of 13.92% is built to sit just above guided revenue growth (11–13%) plus the buyback tailwind already in the share-count adjustment. Sanity check against actual prints: the base start (13.92%) is below the latest FY revenue YoY (15.60%) and far below the OE/share CAGR print (63.24%) — that is deliberate and explained above (one-off margin leverage in the OE print, already in the base), not a cap artifact. The bull (18.92%) and super-bull (25.92%) starts restore the leverage case if margin expansion does repeat. Offsets used vs g_base: −0.17 / −0.11 / −0.06 / −0.01 / +0.06. Probabilities 10/25/30/25/10; OE multipliers 0.75/0.90/1.00/1.10/1.25 (defaults). Price $83.985.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | 2.92% | 0.75 | CMS pricing bites, Abbott takes share, growth stalls | $19.87 | 5.47% |
| Bear | 25% | 8.92% | 0.90 | Revenue decelerates below guidance; margins give back part of the step-up | $31.14 | 7.41% |
| Base | 30% | 13.92% | 1.00 | Guided 11–13% revenue growth plus buybacks; margins hold at guided levels | $43.19 | 9.38% |
| Bull | 25% | 18.92% | 1.10 | Type 2 / Stelo / international adoption accelerates; operating leverage resumes | $59.23 | 11.78% |
| Super bull | 10% | 25.92% | 1.25 | Category-killer path: broad non-insulin adoption and a second margin leg | $91.41 | 15.87% |

- **Probability-weighted: IV@15% $46.68, IV@12% $63.96, IV@10% $83.48, weighted IRR 9.96%, base-case IRR 9.38%**
- **Tier by numbers: D.** Diagnostics: OE yield 3.78% (on the TTM base), terminal value 21.96% of IV@15%, scenario spread 4.60x, 9.4 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.4 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, quoted in full above.
- **BASE_DIVERGENCE** (latest FY OE/share $2.26 vs 3-yr median $1.12): the median is the distorted one. The history shows a step-up, not a spike: conservative OE rose from $361,100,000 (FY2023) to $460,300,000 (FY2024) to $917,600,000 (FY2025), and the TTM legs through H1 2026 rose further (TTM OE $1,242,600,000). FY2025's jump is corroborated by the filed OCF ($1,440,700,000) and by Q2 2026 earnings (margin expansion, guidance raised). TTM base used; median retained in the reporting.
- **NI_OCF_DIVERGENCE** (net income and operating cash flow differ by >40% in 2024, 2025): explained by the non-cash structure printed in the history, not by a one-off gain in the OE base. In FY2025 net income was $836,300,000 against OCF of $1,440,700,000, with D&A of $251,800,000 and SBC of $159,600,000 printed as the large non-cash items (FY2024: net income $576,200,000, OCF $989,500,000, D&A $217,700,000, SBC $170,400,000). The conservative OE definition subtracts SBC again after OCF, so SBC is not double-counted as free money; the OCF-based series is the one used throughout.
- **OE_VOLATILE** (OE/share range over the last 5 years spans >3x): real, but it is a growth/margin inflection plus a capex-heavy FY2021 (conservative OE negative that year), not commodity cyclicality. Handled by the TTM base, the recalibrated (lower) growth starts, and 35% of probability on bear-or-worse outcomes.
- **LOW_OE_YIELD** (preliminary run, on the median base): superseded by the TTM base — the final run's OE yield is 3.78%. The substance stands even at 3.78%: the valuation still rests mostly on growth, which is why the tier is fragile and the verdict below is sized to the conservative end.
- **WIDE_SCENARIO_SPREAD** (super-bull IV 4.60x super-bear IV): real — the outcome range is wide because the price embeds years of adoption and margin assumptions. Confidence is capped at medium, and the verdict is sized to the conservative end.

## My thoughts / overlay
- Method range: on the preliminary median base ($1.12/share) with default scenarios the weighted IRR was 5.96% (Tier D); on the TTM base with the engine's un-recalibrated default growth offsets it was 11.41% (Tier C); on the TTM base with the recalibrated growth above it is 9.96% (Tier D, a hair below the C line). The honest headline is that range — **D to C** — and every defensible method sits below the 15% hurdle at $83.985. The disagreement is about how far below, not whether it clears.
- Quality is not the debate: recurring sensor revenue, filed OCF growth, buybacks shrinking the diluted count (FY2025 405,500,000 to current-YTD 391,800,000 in the TTM inputs), and SBC that is material but not runaway ($162,400,000 TTM). The debate is price: at an OE yield of 3.78% on the best current base, the buyer needs the bull case just to reach the low teens.
- Risks that would move this down, not up: CMS competitive bidding/pricing, Abbott price competition, sensor quality/recall headlines, and execution through the leadership transition. Risks are payer- and competitor-driven, not demand-driven — Q2 2026 demand and guidance were strong.
- Hurdle-clearing price: the weighted IV@15% is $46.68 — that is the price at which the weighted case clears 15% by construction, and a margin of safety means paying below it, not at it. Even the super-bull IV@15% ($91.41) sits only modestly above the current price, so at $83.985 there is no margin of safety against anything but the best case.

## Final verdict
- **Final tier: D** (weighted IRR 9.96% on the v5 final inputs; method range D to C — no tier override)
- Confidence: **Medium** (high on the filing-derived TTM base, low on any single growth/margin path — the scenario spread is 4.60x)
- One-liner: High-quality CGM duopolist, moat 6/10 — but at $83.985 it does not clear 15% on any defensible base (weighted IRR 9.96%, weighted IV@15% $46.68); it clears 15% only at or below $46.68.
