# EFX — Equifax Inc

Pass-1 run, 2026-10-16 (engine 5.4.0). Price $160.85 (nasdaq_quote_api, dcf_numbers.json). Market cap est. $19.96B — in scope under $40B. All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.json, financials_history.csv, or fundamentals.json — none are recomputed.

## What it is
One of the three national U.S. consumer credit bureaus (with Experian and TransUnion), plus the dominant electronic employment/income verification database (The Work Number, via Workforce Solutions) and an international bureau business. FY2025 revenue $6,074.5M by segment: Workforce Solutions $2,582.3M, U.S. Information Solutions $2,078.5M, International $1,413.7M (Q4 2025 earnings release segment table). Q2 2026 segment revenue: Workforce Solutions $705.4M, USIS $611.6M, International $383.1M, total $1,700.1M (10-Q segment note). Asset base is data, not plant: capex is mostly capitalized software / cloud build.

## Owner's earnings
**FY2025 (10-K via EDGAR, financials_history.csv):** operating cash flow $1,615,700,000; capex $481,400,000; SBC $78,400,000 (always a real cost).
- **Conservative owner's earnings FY2025: $1,055,900,000 = $8.51/share** (base_oe_latest_per_share, dcf_numbers.json).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $1,038,700,000 = same ballpark, which raises confidence in the OCF-based figure.
- OE positive 5 of the last 5 fiscal years (5/5), but violently cyclical — see OE_VOLATILE below. OE/share history: 2021 $6.56, 2022 $0.57, 2023 $3.58, 2024 $5.86, 2025 $8.51.
- Net debt $4,912,500,000 (debt total $5,093,300,000 less cash $180,800,000, financials_history.csv).

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $1,615,700,000 − prior YTD $585,000,000 + current YTD $581,700,000 = **TTM $1,612,400,000**
- Capex: FY $481,400,000 − prior YTD $229,400,000 + current YTD $255,400,000 = **TTM $507,400,000**
- SBC: FY $78,400,000 − prior YTD $46,600,000 + current YTD $60,500,000 = **TTM $92,300,000**
- Shares (current-YTD weighted diluted): **119,900,000**
- **TTM OE total $1,012,700,000 → base OE/share $8.45** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $5.86/share — rejected as the base: it is the median of a trough sequence (2023 $3.58, 2024 $5.86, 2025 $8.51) and is contradicted by the TTM, which independently reproduces the FY2025 level ($8.45 vs $8.51). The median is still reported and used in the method range below.

## MOAT — 7/10
- **FOR:** (1) Regulated triopoly — one of only three national credit bureaus; bureau data files cannot be replicated by a new entrant at any realistic cost, and lenders' models/scorecards are calibrated to all three files. (2) The Work Number payroll database — the antitrust complaint itself alleges Equifax exclusively controls >40% of the payroll data required for electronic verification of income/employment; verification is embedded in mortgage, auto, and government-benefit workflows. (3) Pricing power at the segment level — FY2025 adjusted EBITDA margins: Workforce Solutions 51.5%, U.S. Information Solutions 35.2%, International 28.5% (earnings-release segment reconciliation). (4) Switching costs / workflow embedding — verification and bureau pulls sit inside lender LOS and employer HR/payroll processes; multi-year contracts.
- **AGAINST:** (1) Measured returns are only mid-single-to-low-double digits: roic_proxy (fundamentals.json) ran 10.37% (2021), 8.41% (2022), 7.15% (2023), 8.10% (2024), 8.54% (2025) — not "well above cost of capital." Written reason the history understates the franchise: the denominator carries decades of acquisition goodwill (the balance sheet is mostly acquired data assets), and the numerator spans the worst mortgage/hiring trough in 20 years; the segment EBITDA margins above are the cleaner pricing-power evidence. This tension is exactly what pass 2 should attack, and it is why the score is 7, not 8–9. (2) Regulatory/antitrust erosion — the VOIE antitrust suit survived a motion to dismiss (E.D. Pa.); potential elimination of the tri-merge requirement would cut bureau-pull volumes structurally; FICO's direct-licensing push and the FHFA's VantageScore opening re-route score economics. (3) Mortgage/hiring cyclicality — Q3 2026 mortgage origination growth already deteriorating per Oppenheimer's downgrade note. (4) Payroll-data challengers (Argyle and peers) attacking The Work Number's exclusivity model. (5) 2017 breach legacy — recurring legal/regulatory cost line in every adjusted reconciliation.
- Gross margin: the fundamentals extract carries a gross margin only for 2016 (64.60%) and 2017 (63.99%); the COGS tag is not carried for later years in the standardized extract, so no 5-yr gross-margin trend can be quoted from computed outputs — operating margin is the usable series: 23.1% (2021), 20.6% (2022), 17.7% (2023), 18.3% (2024), 18.0% (2025) — compressed vs history and not yet recovered, a real mark against a higher moat.
- CAP = 11.1 years (clamp(2 + 1.3 × 7)); growth holds 2 years, then fades to 2.5% terminal.

## Five scenarios (final run, --ttm, moat 7)
Probabilities adjusted from the 10/25/30/25/10 default to **10/30/30/20/10**: bear weight widened for OE volatility, leverage, tri-merge and antitrust overhangs; bull weight trimmed because the bull case needs a mortgage recovery that Q3 2026 prints are moving away from. Offsets and multipliers at defaults (−12/−5/0/+5/+12pp; 0.75/0.90/1.00/1.10/1.25).

| Scenario | Prob | Growth start | OE mult | IV@15 | IV@12 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -4.74% | 0.75 | $37.02 | $47.33 | 5.04% |
| Bear | 30% | 2.26% | 0.90 | $61.65 | $81.04 | 7.28% |
| Base | 30% | 7.26% | 1.00 | $86.76 | $116.20 | 9.48% |
| Bull | 20% | 12.26% | 1.10 | $121.03 | $164.90 | 12.21% |
| Super bull | 10% | 19.26% | 1.25 | $191.82 | $267.14 | 16.93% |

**Weighted: IRR 9.94%, IV@15 $91.61, IV@12 $123.60, IV@10 $159.56.** Tier by numbers **D** (bear D 7.28% → bull C 12.21%). Hurdle prices: clears 15% at $91.61, 20% at $63.24, 25% at $47.89. Upside at 15%: −43.0% (key_numbers.md).

**Growth-start sanity check.** Recent prints: FY2025 revenue YoY +6.92% (engine latest rev YoY); TTM revenue YoY +10.35% (fundamentals.json TTM block); Q2 2026 revenue +10.6% YoY to $1.7B with USIS +17% and Workforce Solutions +7% (Q2 2026 reporting); FY2026 guidance reconfirmed at $6.75B revenue midpoint and $8.54 adjusted EPS midpoint. The base start (7.26%) sits **below** the current ~10–11% prints — written reason: the current prints are a cyclical rebound off the 2022–23 mortgage/hiring trough (the blend is anchored on rev CAGR 5y 8.04% / 3y 5.85%, which span the collapse), and two forward headwinds (tri-merge elimination, VOIE antitrust) are not in any print yet. The 54.09% OE/share 2-yr CAGR component is a trough-rebound artifact and the blend correctly resists it. Bull (12.26%) requires the current print rate to persist plus mortgage recovery; super bull (19.26%) is above every recent print and is kept at 10% for that reason — it is the housing-recovery tail, not a forecast.

## FLAGS — every fragility flag resolved
- **STALE_FY:** FY ended 9.49 months ago. Resolved with ttm.py: TTM OE/share $8.45 through Q2 2026 (legs quoted above) vs FY2025 $8.51 — the run-rate is confirmed, not stale; final run uses --ttm.
- **OE_VOLATILE:** OE/share spanned $0.57 (2022) → $8.51 (2025) — the 2022–23 mortgage-origination collapse and hiring freeze crushed verification and bureau volumes (2022 OCF fell to $757.1M and working capital absorbed $607.6M, financials_history.csv). Response: TTM base (current run-rate, not a peak-year cherry-pick — TTM ≈ FY25), bear probability widened to 30%, verdict sized to the bear end.
- **NI_OCF_DIVERGENCE (2024, 2025):** NI $604.1M vs OCF $1,324.5M (2024); NI $660.3M vs OCF $1,615.7M (2025). The gap is D&A-explained: D&A was $680.6M (2024) and $726.9M (2025) — amortization of acquired intangibles and capitalized software/cloud assets — plus SBC added back in OCF ($81.6M / $78.4M). No tax-deposit, impairment, or one-off working-capital item of that scale appears in the filed history. Consequence: NI understates cash earnings power for this acquisitive data business; the OCF-based conservative OE is the right basis, and the divergence does not undermine the base.
- **SECTOR_MODEL_MISMATCH:** The queue classifies EFX under Finance. It is not a lender — no loan book, no credit losses, SIC 7320 (Services-Consumer Credit Reporting) — and its capex (capitalized software/cloud, $507.4M TTM) is real and recurring, so the OE/capex DCF fits materially better than for a bank or insurer. Per the standing rule, confidence is graded **low** anyway and the name lists under sector misfits.
- **BASE_DIVERGENCE:** Latest FY $8.51 vs 3-yr median $5.86. The **median is the distorted one**: it is the middle of a trough sequence (2023 $3.58 / 2024 $5.86 / 2025 $8.51) created by the mortgage collapse, and the independent TTM calculation reproduces $8.45. The latest/TTM level is the validated base; the median survives only in the method range below.
- **WIDE_SCENARIO_SPREAD:** Super-bull IV@15 is 5.18x super-bear. Confidence is low (also forced by the sector flag); the verdict is sized to the bear end.
- **HIGH_NET_DEBT:** Net debt $4,912,500,000 = 6.76x normalized OE on the preliminary basis; final diagnostics: net debt / normalized OE 4.69x. Debt is senior unsecured notes (a new two-series offering in 2026 refinances commercial paper; parent-level unsubordinated unsecured debt $5,462.6M at Q2 2026 per the offering summary). Leverage is serviceable at current OCF ($1,612.4M TTM) but it is why a mortgage downturn hits OE/share fast — reflected in the 30% bear weight and the 0.75 super-bear multiplier.
- **TIER_BAND:** Bear tier D (7.28%) vs bull tier C (12.21%) — the verdict spans tiers; sized to the bear end: **D**.

## Thoughts / method range
- **Method range:** preliminary run on the normalized median base ($5.86): weighted IRR 7.61%, IV@15 $62.63, Tier D. Final run on the TTM base ($8.45): weighted IRR 9.94%, IV@15 $91.61, Tier D. Both defensible bases land in **D** — the verdict is not base-sensitive; only a super-bull world (19.26% growth start, 1.25x OE) clears 15%, at 10% probability.
- At $160.85 the market is paying ~19x TTM owner's earnings for a business whose measured ROIC ran 7–11% over the last five years and whose two biggest volume drivers (mortgage pulls, verification) carry live regulatory/antitrust threats. The de-rating is already partway done (stock ~−29% over one year in the Finnhub snapshot) and it is still not enough.
- What would change the verdict: a real mortgage recovery lifting verification volumes for several quarters (watch TTM OE/share vs the $8.45 base), tri-merge surviving intact, or price near the $91.61 hurdle.
- Confidence **low**: sector-model mismatch flag plus a 5.18x scenario spread. No overrides were needed or used — no data gaps.

## Verdict
**Tier D.** A genuinely moated franchise (7/10) at a price that already pays for the bull case. Clears Andrew's 15% hurdle only at **$91.61** — roughly 43% below the $160.85 price. Size any interest to the bear end (IV@15 $61.65, IRR 7.28%).
