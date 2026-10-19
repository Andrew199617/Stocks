# OWL — Blue Owl Capital Inc.
Pass-1 run, 2026-10-17 (engine 5.4.0). All figures copied from dcf_numbers.json, ttm.json or financials_history.csv — none recomputed.

## What it is
Alternative asset manager built on permanent capital: Credit (direct lending, ~$158B AUM), Real Assets (net-lease real estate, digital infrastructure), and GP Strategic Capital (Dyal GP stakes). Total AUM $319B at Q2 2026 (+12% YoY), fee-paying AUM $190.6B, permanent capital ~$225B. Revenue is overwhelmingly management fees on long-duration/permanent vehicles — fee-related earnings (FRE) margin 58.5% in Q2 2026. The stock has fallen from above $26 to $8.85 on private-credit fears (BDC redemption headlines, software-loan exposure worries, an unresolved Girard Sharp investigation into the OBDE→OBDC merger) even as AUM and FRE kept growing.

## Owner's earnings
**FY2025 (10-K via EDGAR, financials_history.csv):** OCF $1,256,032,000; capex $57,748,000; SBC $673,524,000 (always a real cost — and here it is the dominant one).
- **Conservative OE FY2025: $524,760,000 = $0.79/share** (latest FY OE/share). Maintenance version (NI-based) is $78,833,000 — far lower, because GAAP net income is Class A-attributable only while OCF is consolidated (see NI_OCF_DIVERGENCE below); the OCF-based conservative figure is the usable one.
- OE history per share: FY2022 $0.56, FY2023 $1.19, FY2024 $1.12, FY2025 $0.79 — positive 4 of the last 5 years (FY2021 was deeply negative on $1,205,336,000 of merger-era SBC).
- Engine normalized base (median of last 3 FY): **$1.1152/share**. Net debt $3,129,914,000 (TOTAL:LongTermDebt basis), 5.3x the TTM OE total — corporate leverage is real for an asset manager.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct):**
- OCF: FY $1,256,032,000 − prior YTD $440,093,000 + current YTD $564,061,000 = **TTM $1,380,000,000**
- Capex: FY $57,748,000 − prior YTD $23,385,000 + current YTD $22,129,000 = **TTM $56,492,000**
- SBC: FY $673,524,000 − prior YTD $338,730,000 + current YTD $381,397,000 = **TTM $716,191,000**
- Shares (current-YTD weighted diluted): **684,813,494**
- **TTM OE total $607,317,000 → base OE/share $0.8868** (base_source: ttm_json)
- Why TTM over the $1.1152 median: the median year (FY2024) predates the FY2025 SBC step-up ($312,609,000 → $673,524,000); the TTM base charges the current, higher SBC run-rate in full. Cross-check: LTM distributable earnings per share reported for Q2 2026 was ~$0.87 — the TTM OE/share of $0.8868 sits right on the company's own cash-earnings measure, which supports it as the honest base. Caveat that cuts the other way: the $0.92/yr dividend exceeds that ~$0.87 DE/share (trailing coverage ~95%) — the payout is not fully covered by distributable earnings today.

## Moat: 6/10 — moderate, scale-based, not wide
- FOR: permanent capital base (~$225B, roughly 70%+ of AUM) makes the fee stream unusually durable for an alt manager — no fund-life redemption clock on most of it; scale leadership in US middle-market direct lending and net-lease; diversified across Credit / Real Assets / GP stakes so no single strategy carries the firm; FRE margin 58.5% and expanding (57.0% a year earlier) shows operating leverage; $31.1B of AUM not yet fee-paying ≈ ~$380M of embedded future annual management fees once deployed; LTM FRE +15%, Q2 2026 FRE +9% YoY with $7.6B raised in the quarter despite the sentiment overhang.
- AGAINST: private credit is commoditizing — BX/KKR/APO and bank re-entry compress spreads and fee rates; the wealth/retail channel brings redemption and headline risk (2026 non-traded BDC redemption story is what broke the stock); credit quality of the underlying loan book (software exposure) is the real franchise risk and is only revealed in a downturn; founder/key-person concentration; heavy SBC (TTM $716,191,000, more than half of OCF) and a share count growing 15.2%/yr dilute the per-share compounding the AUM story promises.
- ROIC evidence: **not available from the computed outputs** — fundamentals.json's roic_proxy series is null because the engine found no operating-income tag for this filer (used_tags operating_income: null), and an asset manager's fee business makes the standard invested-capital frame weak anyway. With no ROIC history evidencing returns well above the cost of capital through a cycle, the moat is capped at 6 per the rubric's evidence-first rule.
- A 6 gives CAP = 9.8 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 9.8 years, 15-year projection.

## DCF — final run (2026-10-17)
Growth recalibration (written reason): the engine's blended start of 21.50% is built on revenue CAGRs (5y 62.96%, 3y 27.96%) that straddle the 2021 Dyal/Owl Rock merger basis break, while the OE/share CAGR (2y) is −18.35% on dilution and the SBC step-up. The current, post-break prints are: revenue +25.04% YoY in FY2025, Q2 2026 AUM +12% YoY, fee-paying AUM +7%, FRE +9% YoY (LTM +15%). Scenario starts were therefore set via offsets (−0.215 / −0.155 / −0.105 / −0.055 / −0.005 vs the blended 21.50%) to 0 / 6 / **11** / 16 / 21% — the base start sits on the AUM/FRE prints, not the merger-inflated CAGRs. Probabilities shifted one notch bearish vs defaults (10/30/30/20/10) for the live credit-cycle and litigation overhang. OE multipliers are the defaults 0.75/0.90/1.00/1.10/1.25. Base = TTM OE/share $0.8868 (--ttm). Price $8.85.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | 0.0% | 0.75 | Credit event in the loan book; fundraising stalls; fee pressure | $4.88 | 9.27% |
| Bear | 30% | 6.0% | 0.90 | Private-credit growth slows to mid-single digits; SBC stays heavy | $7.65 | 13.37% |
| Base | 30% | 11.0% | 1.00 | AUM/FRE grow at current prints; dry powder deploys on schedule | $10.61 | 17.23% |
| Bull | 20% | 16.0% | 1.10 | Deployment of the $31.1B pipeline accelerates FRE; sentiment normalizes | $14.57 | 21.64% |
| Super bull | 10% | 21.0% | 1.25 | Full pipeline conversion plus wealth-channel scaling | $20.62 | 27.28% |

- **Probability-weighted: IV@15% $10.94 (+23.6% vs price), IV@12% $14.84, weighted IRR 17.60%, base-case IRR 17.23%**
- **Tier by numbers: B.** Bear tier C (13.37%), bull tier A (21.64%) — per TIER_BAND the verdict is sized to the bear end. Hurdle prices: clears 15% below $10.94, 20% below $7.49, 25% below $5.63. Diagnostics: OE yield 10.02%, terminal value 20.9% of IV@15%, scenario spread 4.23x, net debt 5.33x normalized OE, 9.5 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.5 months ago): resolved by construction — the base is TTM through Q2 2026 from ttm.py, legs quoted above.
- **DILUTION** (share count +15.2%/yr): structural, not a blip — the Up-C exchange of operating-group units into Class A plus equity comp steadily expands the count (661,885,114 FY2025 diluted → 684,813,494 current-YTD). The growth adjustment already deducts it from revenue components; the TTM base uses the current, larger count. SBC is the mechanism: TTM SBC $716,191,000 is charged in full in the OE definition.
- **BASIS_BREAK_SUSPECT**: the May 2021 Dyal Capital + Owl Rock mergers (revenue $249,815,000 in FY2020 → $823,878,000 in FY2021) plus later deals (IPI, Kuvare) inflate every long-window CAGR. Growth inputs were set from post-break prints (AUM +12%, FRE +9%, revenue +25.04% latest YoY), not the 5y/3y CAGRs — see the recalibration note.
- **NI_OCF_DIVERGENCE** (2023, 2024, 2025): structural Up-C arithmetic, not a one-off. Consolidated OCF ($1,256,032,000 FY2025) captures 100% of the operating group's cash flow including the share attributable to noncontrolling interests, while GAAP net income ($78,833,000 FY2025) is Class A-attributable only and is after the full non-cash SBC charge. The OCF-based conservative OE used throughout is the right series; the NI-based maintenance OE is not meaningful for this structure and is not used.
- **SECTOR_MODEL_MISMATCH** (Finance): agreed — an OE/capex DCF is a rough frame for an asset manager whose "capex" is trivial and whose earnings are fee streams on other people's capital. Confidence is low, and the ranking lists the name under sector misfits. The TTM base's agreement with the company's reported distributable earnings (~$0.87/share LTM) is the main mitigant.
- **WIDE_SCENARIO_SPREAD** (4.23x): real — outcomes hinge on credit-cycle and deployment paths. Confidence capped at low (already low on the sector flag); verdict sized to the bear end.
- **HIGH_NET_DEBT** (5.33x normalized OE): corporate debt $3,129,914,000 against TTM OE of $607,317,000. This is holding-company debt serviced by fee income, not fund-level leverage, but it is senior to the equity's OE stream — in the super-bear case (0.75x OE mult) coverage thins fast, which is one reason the bear probabilities were raised.
- **TIER_BAND** (bear C 13.37% vs bull A 21.64%): verdict sized to the bear end — final tier B by the weighted number, treated as a low-B/C-boundary name, not a clean B.

## My thoughts / overlay
- The honest headline is the gap between the two defensible reads: on the preliminary defaults (median base $1.1152, merger-inflated 21.50% blended growth) the engine printed Tier S at 28.02% weighted IRR; on current prints (TTM base $0.8868, growth starts anchored to AUM/FRE) it prints B at 17.60% with a bear case in C. The second read uses the fresher base and the non-straddling growth inputs, so it is the one that stands — but the spread between them is itself the finding: this score is assumption-dominated.
- The market is pricing a private-credit accident ($8.85 vs $26+ highs; dividend yield ~10.4% on the $0.92 payout). The filing numbers through Q2 2026 do not show one yet: AUM +12%, FRE +9%, FRE margin up, $7.6B raised in the quarter. What they do show is a payout running ahead of distributable earnings (~95% coverage) and an SBC line that doubled in a year — the per-share economics lag the platform economics.
- Watch items: any credit-quality disclosure in the BDC complex, the Girard Sharp OBDE→OBDC investigation, SBC trajectory vs the ~$365M 2026 guide figure cited in coverage, and whether fee-paying AUM growth re-accelerates as the $31.1B pipeline deploys.

## Final verdict
- **Final tier: B** (weighted IRR 17.60% on the final inputs; method range across defensible runs spans C to S, and the TIER_BAND bear case is C — size it as a low-B at best)
- Confidence: **Low** (SECTOR_MODEL_MISMATCH plus WIDE_SCENARIO_SPREAD; no ROIC series available to evidence the moat)
- One-liner: Permanent-capital fee machine, moat 6/10 — clears 15% at $8.85 on TTM numbers (17.6% weighted, IV@15 $10.94) but only just, the bear case is Tier C, and the dividend currently outruns distributable earnings; hurdle price for a clean 15% is $10.94, for 20% is $7.49.
