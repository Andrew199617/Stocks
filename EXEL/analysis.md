# EXEL — Exelixis, Inc.
Engine 5.4.0 run, 2026-10-17. All figures below are copied from dcf_numbers.json, ttm.json, financials_history.csv, or fundamentals.json — none are recomputed.

## What it is
Single-franchise oncology company built on cabozantinib (CABOMETYX tablets / COMETRIQ). Cabozantinib is ~91% of total revenue: U.S. net product revenue was $573M in Q2 2026 (+10.2% YoY, volume-driven), plus royalties from ex-U.S. partners Ipsen and Takeda (global franchise revenue $806M in Q2, +13% YoY). Market leader in renal cell carcinoma (47% share of the oral TKI prescription basket, Q2 2026) and, about a year after approval, 45% of oral second-line-plus new-patient share in neuroendocrine tumors. The designated successor is zanzalintinib, a next-generation TKI whose first NDA (with atezolizumab in previously treated metastatic colorectal cancer) has a PDUFA date of December 3, 2026. Market cap $17.54B at $62.23 (nasdaq_quote_api) — in scope under $40B.

## Owner's earnings
**FY2025 (10-K, period ended 2026-01-02, from financials_history.csv):** operating cash flow $884,267,000; capex $8,429,000; SBC $112,983,000 (always a real cost).
- **Conservative owner's earnings FY2025: $762,855,000 = $2.71/share** (latest FY OE/share in dcf_numbers.json).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC, from financials_history.csv): $1,094,475,000 — higher than the conservative figure, flattered by a working-capital release; the conservative OCF-based figure is the one used.
- OE positive 5 of the last 5 fiscal years. Capex is structurally trivial (~$8–11M/yr against ~$0.9–1.2B OCF) — this is an IP business, not a plant business.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $884,267,000 − prior YTD $260,430,000 + current YTD $559,586,000 = **TTM $1,183,423,000**
- Capex: FY $8,429,000 − prior YTD $5,790,000 + current YTD $8,325,000 = **TTM $10,964,000**
- SBC: FY $112,983,000 − prior YTD $62,001,000 + current YTD $61,613,000 = **TTM $112,595,000**
- Shares (current-YTD weighted diluted): **263,499,000**
- **TTM OE total $1,059,864,000 → base OE/share $4.02** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $1.95/share — rejected as the base; see BASE_DIVERGENCE under Flags. It is still reported in dcf_numbers.json.

## Moat: 5/10 — moderate/narrow, strong product, finite life
Justification: CABOMETYX has genuine clinical/brand leadership and a defended patent estate, but the franchise is one molecule, its composition-of-matter patent expired in August 2026, and the successor franchise is unapproved — durability past ~2030 is asserted, not proven.
- FOR: RCC leadership — 47% of the oral TKI prescription basket and still gaining (was 45% a year earlier); rapid NET uptake (45% of oral 2L+ new-patient share ~1 year post-approval); patent estate actively defended — the Federal Circuit upheld the malate salt patents and MSN's generic is barred until at least January 15, 2030; ex-U.S. royalty stream via Ipsen/Takeda on the same molecule; ~96% gross margin funds $1.11B of TTM buybacks (fundamentals.json).
- AGAINST: single-molecule concentration (~91% of revenue is cabozantinib); composition-of-matter patent expired August 2026 — protection now rests on secondary/formulation patents (a further formulation patent expiring February 2032 goes to trial in November 2026); a different-salt cabozantinib product (Handa's OMCAZIO, approved via 505(b)(2) in September 2026) sits outside the malate estate and is a live circumvention risk; gross-to-net deductions run ~30% of gross sales and guided 30–31% for 2026, with 340B utilization rising; zanzalintinib is unproven and binary (PDUFA December 3, 2026).
- ROIC / margin evidence (fundamentals.json roic_proxy, after-tax operating income over equity + debt − cash): FY2021 14.5%, FY2022 8.0%, FY2023 6.7%, FY2024 23.6%, FY2025 41.0%. Gross margin held ~96% every year (96.3% / 96.4% / 96.0% / 96.5% / 96.4% over the same five years). The ROIC history is exactly why this is a 5, not a 7+: returns sat at or below a plausible cost of capital through FY2023 and have only been well above it for two years, driven by operating leverage on a maturing drug — that is a product cycle, not yet a through-cycle franchise.
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — final run (2026-10-17)
**Growth recalibration (written reason):** the engine's blended start is 20.33%, but one blend component is an artifact — OE/share CAGR (2y) of 114.97% measured off the depressed FY2023 base of $0.58/share. The revenue signals that mean something all sit near high-single digits: latest FY revenue YoY +6.98%, TTM revenue YoY +9.2% (fundamentals.json), Q2 2026 total revenue +10.6% YoY, and FY2026 guidance of $2.500–2.550B total revenue against FY2025's $2,320,126,000. Scenario starts were therefore set via offsets (−0.20333 / −0.15333 / −0.11333 / −0.07333 / −0.02333 vs the blended start) to 0 / 5 / **9** / 13 / 18%. Probabilities were bear-weighted to 15/30/30/15/10 (defaults 10/25/30/25/10) for the patent-cliff and single-molecule risks and the OE_VOLATILE flag; OE multipliers are the defaults 0.75/0.90/1.00/1.10/1.25. Price $62.23. Base OE/share $4.02 (TTM).

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | 0.0% | 0.75 | Different-salt / generic erosion bites before zanzalintinib lands; growth stalls | $22.29 | 6.88% |
| Bear | 30% | 5.0% | 0.90 | Cabometyx matures at mid-single digits; NET ramp stays gradual (the reason guidance was cut in August 2026); gross-to-net keeps rising | $32.94 | 9.21% |
| Base | 30% | 9.0% | 1.00 | Current prints persist: ~9% revenue growth, margins hold, buybacks continue | $43.18 | 11.35% |
| Bull | 15% | 13.0% | 1.10 | NET + RCC share gains compound; zanzalintinib approved and ramps as second franchise | $55.98 | 13.85% |
| Super bull | 10% | 18.0% | 1.25 | Zanzalintinib becomes a full successor franchise and the cliff is bridged | $77.95 | 17.69% |

- **Probability-weighted: IV@15% $42.37 (−31.9% vs price), IV@12% $56.78, IV@10% $72.90, weighted IRR 11.21%, base-case IRR 11.35%**
- **Tier by numbers: C.** Diagnostics (dcf_numbers.json): OE yield 6.46%, terminal value 19.6% of IV@15%, scenario spread 3.50x, 9.5 months since FY end. Hurdle prices: clears 15% at $42.37, 20% at $29.49, 25% at $22.46.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.5 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026 (period ended 2026-07-03), quoted above.
- **BASE_DIVERGENCE** (latest FY $2.71 vs 3-yr median $1.95): the median is the distorted one. It averages in FY2023 ($0.58/share, operating margin 9.3%) before operating leverage and the buyback bit; operating margin has since risen to 27.9% (FY2024) and 37.6% (FY2025), and the TTM print ($4.02) confirms the latest FY was not a one-off spike. TTM base used; the steep TTM jump is instead handled by recalibrating growth down to revenue-supported rates (above) rather than by shrinking the base.
- **OE_VOLATILE** (OE/share spans >3x over 5 years: $0.23 → $4.02 TTM): real, and it is an inflection plus buyback denominator effect, not commodity cyclicality — but the forward risk it signals (one drug's life cycle) is genuine. Handled with bear-weighted probabilities (45% on bear-or-worse) and a 0% super-bear growth start.
- **BUYBACK_TAILWIND** (share count −4.6%/yr): already credited via the growth adjustment in the blend; the recalibrated starts are revenue-based, so the buyback is not double-counted in the scenario starts — it enters only through the TTM base's actual share count (263,499,000 vs 281,863,000 in FY2025). TTM buybacks were $1,114,979,000 (fundamentals.json).
- **DEBT_TAGS_BLANK** (no debt tag for the latest FY — net debt unknown to the engine): stated from the filing data — Exelixis carries no borrowings. Latest FY balance sheet (financials_history.csv / fundamentals.json): cash $482,488,000 plus short-term investments $576,603,000 against total liabilities of $683,104,000 and equity of $2,161,319,000; the only debt-like item is operating lease liabilities of $200,920,000. The company is effectively debt-free and net cash; no leverage verdict is needed beyond that.
- **SHARES_FALLBACK** (no diluted count filed for 2016): noted — only the 2016 history year uses the outstanding count; it does not touch the TTM base, the median base, or any scenario input.
- **TIER_BAND** (bear tier D at 9.21% vs bull tier C at 13.85%): the verdict spans tiers; the final verdict below is sized to the bear end.
- The preliminary run's **WIDE_SCENARIO_SPREAD** flag cleared in the final run after the growth recalibration (spread now 3.50x); uncertainty is still material, so confidence is capped at medium.

## My thoughts / overlay
- The honest tension: on current cash generation this is cheap-looking (OE yield 6.46% on a debt-free, ~96%-gross-margin business buying back ~8% of its shares a year), but the entire cash stream is one molecule whose core patent has already expired. The market price of $62.23 pays for the bull case today — even the bull scenario (13% growth, 1.10x OE) yields only 13.85% IRR, below the 15% hurdle. Only the super-bull path (zanzalintinib fully bridges the cliff) clears 15%.
- Method range: on the engine's normalized median base ($1.95) with default growth, the preliminary run printed weighted IRR 10.19% / IV@15% $35.44 (Tier C); on the TTM base with recalibrated growth, 11.21% / $42.37 (Tier C). The tier is C on both defensible bases — the disagreement is about how much downside protection the price lacks, not about the verdict.
- Watch items: the December 3, 2026 zanzalintinib PDUFA; the November 2026 formulation-patent trial; whether the different-salt OMCAZIO launches commercially; gross-to-net / 340B trajectory; NET ramp pace (the stated reason for the August 2026 guidance cut, which lowered FY2026 total revenue guidance midpoint by $50M while R&D guidance was cut the same amount, leaving guided FCF roughly unchanged).

## Final verdict
- **Final tier: C** (weighted IRR 11.21% on the final inputs; bear case D at 9.21% — size to the bear end)
- Confidence: **Medium** (high on the TTM base and balance sheet, low on any post-2030 franchise path — the scenario spread is 3.50x)
- One-liner: High-quality single-drug cash machine, moat 5/10 — at $62.23 it does not clear 15% (weighted IRR 11.2%, IV@15% $42.37); it clears 15% only at or below $42.37, and the patent cliff means the bear case (Tier D) is the one to size to.
