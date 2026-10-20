# GMED — Globus Medical, Inc.
Pass-1 run, 2026-10-19, engine release 5.5.0. Market cap $10.368B at $75.65 (nasdaq_quote_api) — in scope under $40B.

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.json or fundamentals.json — none are recomputed.

## What it is
The #2 global spine company: musculoskeletal implants (spine, trauma, joint reconstruction) plus the ExcelsiusGPS robotic-navigation / ExcelsiusHub / Excelsius3D enabling-technology platform. The September 2023 NuVasive merger roughly doubled the business; the February 2025 Nevro acquisition ($250M) added spinal-cord stimulation (neuromodulation). Q2 2026 revenue $789.6M, +5.9% reported and +9% excluding Nevro; U.S. Spine +7% — its fifth consecutive quarter of above-market growth — and International Spine +14%. FY2026 guidance (reaffirmed/raised in Q2 2026): revenue $3.18–3.22B, non-GAAP EPS $4.95–5.05.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $753,447,000; capex $174,425,000 (PP&E $164,679,000 + intangible purchases $9,746,000); SBC $49,779,000 (always a real cost).
- **Conservative owner's earnings FY2025: $529,243,000 = $3.86/share** (key_numbers.md).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $76,238,000 — not usable here: its $564,047,000 ΔNWC leg (financials_history.csv) swings with the post-merger balance-sheet reshaping (the same leg was −$518,826,000 in FY2024) and measures working-capital definition noise, not maintenance economics. The OCF-based conservative figure is the clean one.
- OE positive 5 of the last 5 fiscal years. No dividend. Buybacks $221,058,000 TTM (fundamentals.json), including $136.1M repurchased in Q2 2026.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $753,447,000 − prior YTD $255,165,000 + current YTD $412,105,000 = **TTM $910,387,000**
- Capex: FY $174,425,000 − prior YTD $87,665,000 + current YTD $72,783,000 = **TTM $159,543,000**
- SBC: FY $49,779,000 − prior YTD $26,823,000 + current YTD $26,000,000 = **TTM $48,956,000**
- Shares (current-YTD weighted diluted): **137,787,000**
- **TTM OE total $701,888,000 → base OE/share $5.09** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $2.55/share — rejected as the base: its window is FY2023 ($0.98, the partial merger year) and FY2024 ($2.55, the integration year). The latest FY ($3.86) and the TTM ($5.09) are the post-integration run rate, corroborated by Q2 2026 adjusted EBITDA margin of 35.4% vs 28.0% a year earlier and FY2026 non-GAAP EPS guidance of $4.95–5.05.

## Moat: 5/10 — moderate
Justification: a clear #2 spine franchise at Medtronic's scale with a robotics ecosystem that pulls through implants, but ROIC and margin history that have only just recovered to pre-merger levels and four large rivals contesting every placement.
- FOR: #2 spine position, effectively neck-and-neck with Medtronic on spine revenue after NuVasive, with the broadest musculoskeletal portfolio; ExcelsiusGPS + ExcelsiusHub/3D placements pull through proprietary implants, instruments and service (recurring revenue per installed robot); surgeon relationships and competitive recruiting — U.S. Spine +7% in Q2 2026, five straight quarters of above-market growth; vertical in-house manufacturing; debt-free balance sheet funding placements, leasing models and tuck-ins.
- AGAINST: ROIC (fundamentals.json roic_proxy) was 10.5% in 2022, collapsed to 2.8% (2023) and 4.2% (2024) on merger amortization and integration, and only recovered to 10.5% in FY2025 — not a through-cycle wide-moat record at the new scale; gross margin 74.2% (2022) → 58.9% (2024) → 67.4% (FY2025), with management guiding only to the low 70s by end-2026 and mid-70s in 2027; Medtronic (Mazor/Stealth), Zimmer (ROSA), Stryker and J&J all place rival robotics; surgeon loyalty is personal and reps can be poached; Enabling Technologies revenue fell 25.8% and Nevro 14.3% in Q2 2026 — the two newest growth legs are shrinking; the underlying spine market grows only ~3%/yr and hospital pricing pressure caps implant pricing power.
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — final run (2026-10-19)
Growth recalibration (written reason): the engine's blended growth is 31.12%, and it is a merger artefact — its components are a 42.15% 3-yr revenue CAGR and a 98.28% OE/share CAGR measured across the NuVasive consolidation, plus a −5pp share-count adjustment from merger stock issuance. The prints that describe the combined company are: FY2025 revenue +16.65%, Q2 2026 revenue +5.9% reported / +9% ex-Nevro, and FY2026 revenue guidance $3.18–3.22B (+8–10% over FY2025). OE grows faster than revenue near term on gross-margin recovery (67.4% FY2025 → 69.4% adjusted in Q2 2026 → low-70s targeted by end-2026), but nothing supports a 31% start. Scenario starts were therefore set via offsets (−0.29 / −0.25 / −0.20 / −0.15 / −0.09 vs the blended g_base) to 2.12 / 6.12 / **11.12** / 16.12 / 22.12%. Probabilities 10/30/30/20/10 (bear weight widened per OE_VOLATILE); OE multipliers 0.75/0.90/1.00/1.10/1.25. Base = TTM $5.09/share (--ttm). Price $75.65.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | 2.1% | 0.75 | Margin recovery stalls, enabling tech/Nevro drag persists, share gains stop | $30.84 | 7.58% |
| Bear | 30% | 6.1% | 0.90 | Revenue grows at guidance's low end with no further margin leverage | $43.69 | 9.85% |
| Base | 30% | 11.1% | 1.00 | Guided revenue growth plus gradual gross-margin recovery toward the low 70s | $59.67 | 12.54% |
| Bull | 20% | 16.1% | 1.10 | Mid-70s gross margin by 2027, robotics pull-through compounds, Nevro stabilizes | $80.50 | 15.71% |
| Super bull | 10% | 22.1% | 1.25 | Sustained share capture from Medtronic plus full margin restoration | $116.53 | 20.43% |

- **Probability-weighted: IV@15% $61.85 (−18.2% vs price), IV@12% and IV@10% in dcf_numbers.json, weighted IRR 12.90%, base-case IRR 12.54%**
- **Tier by numbers: C.** Hurdle prices (key_numbers.md): clears 15% at ≤ $61.85, 20% at ≤ $42.60, 25% at ≤ $32.15. Diagnostics: OE yield 6.73%, terminal value 20.3% of IV@15%, scenario spread 3.78x, 9.6 months since FY end, net-debt ratio not computed (DEBT_TAGS_BLANK — see flags).

## Flags — every fragility flag resolved
- **STALE_FY** (latest FY ended 9.6 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, legs quoted above; ttm.json carries no warnings.
- **DILUTION** (share count +10.1%/yr): a merger artefact, not ongoing dilution. The count rose 102,643,000 (2022) → 114,630,000 (2023) → 137,863,000 (2024) on NuVasive stock consideration, then flattened: 137,056,000 (FY2025) and 137,787,000 (TTM). SBC is $48,956,000 TTM — about 5% of TTM OCF — and buybacks ($221,058,000 TTM) now exceed issuance. The −5pp growth adjustment the engine deducted for this is one reason the blend was recalibrated by hand.
- **BASIS_BREAK_SUSPECT**: the NuVasive merger (closed September 2023). Revenue: $1,022,843,000 (2022) → $1,568,476,000 (2023, partial year) → $2,519,355,000 (2024, first full year) → $2,938,931,000 (2025). Nevro (February 2025) is a second, smaller break inside FY2025. No CAGR straddling 2023 was trusted; scenario growth starts were set from post-merger prints and FY2026 guidance (see the recalibration note).
- **OE_VOLATILE** (OE/share spans >3x over 5 years): merger depression and recovery, not end-market cyclicality — $0.70 (2022) → $0.98 (2023) → $2.55 (2024) → $3.86 (2025) → $5.09 (TTM). Handled by the TTM base plus a widened bear weight (30%).
- **NI_OCF_DIVERGENCE** (2024): net income $102,984,000 vs operating cash flow $520,638,000. The gap is non-cash acquisition accounting: D&A jumped to $253,389,000 in FY2024 (from $145,526,000 in FY2023) on NuVasive intangible amortization, plus $54,191,000 of SBC — both added back in OCF. The conservative OE is OCF-based throughout, so the divergence does not contaminate the base; FY2024's OE was still genuinely depressed by cash integration costs, which is a BASE_DIVERGENCE point, not this one.
- **DEBT_TAGS_BLANK**: stated from the filing — the company is debt-free. The $450M of NuVasive 0.375% convertible notes due 2025 were repaid in early 2025; at FY2025 end Globus held cash $526,156,000 plus short-term marketable securities $31,087,000 and long-term marketable securities $71,819,000 ($629,062,000 total, FY2025 results release / 10-K), the $400M revolving credit facility was undrawn, and the only lease liabilities are $118,656,000 (dcf_numbers.json). Net cash, not unknown leverage — the engine simply has no debt tag to read because there is no debt.
- **BASE_DIVERGENCE** (latest FY $3.86 vs 3-yr median $2.55): the median is the distorted one — its window holds the partial merger year FY2023 ($0.98) and the integration year FY2024 ($2.55, cash merger costs inside OCF). The latest FY and the TTM are the normalized post-integration run rate; TTM used as the base (construction above).
- **TIER_BAND** (bear tier D at 9.85% vs bull tier B at 15.71%): the verdict is sized to the conservative end — the final tier is the weighted C, and at the $75.65 price even the base case (12.54%) does not clear 15%; only the bull and super-bull cases do.

## My thoughts / overlay
- The honest headline is the method range. The preliminary run (median base $2.55, unrecalibrated 31.12% blended growth) printed a weighted IRR of 14.35% and IV@15% of $70.74 — also Tier C, but for the wrong reasons: a depressed base and a fantasy growth rate roughly offset. The final run (TTM base, prints-based growth) is the defensible one: 12.90% weighted, IV@15% $61.85.
- Quality is improving, price is the problem. The earnings recovery is real (TTM OE $5.09/share, adjusted EBITDA margin 28.0% → 35.4% YoY in Q2 2026, debt-free, buybacks running), but at $75.65 the market is already paying for the bull path: the price sits above even the base-case IV@15% of $59.67 and only $5 below the bull case's $80.50.
- Risks: Enabling Technologies (−25.8% in Q2 2026, partly a shift to leasing/rental placements) and Nevro (−14.3%) must stabilize for the bull case; gross margin has to actually reach the mid-70s in 2027; robotics share is contested by Medtronic at every placement; a spine-market slowdown hits a ~3%-growth end market with little cushion.
- Margin of safety: none at this price on the weighted case — the price is 22.3% above the weighted IV@15% ($61.85). A buyer at ≤ $61.85 is paid the 15% hurdle on the weighted case; a buyer here is paid only if the bull path lands.

## Final verdict
- **Final tier: C** (weighted IRR 12.90% on the final inputs; bear D 9.85%, bull B 15.71% — sized to the conservative end)
- Confidence: **Medium** (high on the TTM base and the debt-free balance sheet, medium on the growth path — the verdict depends on a hand-recalibrated growth start and a still-unproven margin recovery)
- One-liner: Quality #2 spine franchise, moat 5/10, post-merger earnings recovering fast (TTM OE $5.09/share) — but at $75.65 the weighted IRR is 12.9%, short of the 15% hurdle; it clears 15% only at or below the $61.85 weighted IV@15%.
