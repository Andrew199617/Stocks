# KRYS — Krystal Biotech, Inc.
Pass-1 run, 2026-10-20 (engine release 5.5.0). Market cap $9.592B at $320.25 (nasdaq_quote_api) — in scope (under $40B).

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.json, or financials_history.csv — none are recomputed.

## What it is
Pittsburgh genetic-medicines company built on a redosable HSV-1 delivery platform. Its one commercial product, VYJUVEK (beremagene geperpavec), is the first FDA-approved gene therapy for dystrophic epidermolysis bullosa (DEB), approved in 2023 for patients from birth and administered topically, including at home. Revenue is effectively all VYJUVEK: $50.7M in the 2023 launch year, $290.5M in FY2024, $389.1M in FY2025, and $440.5M TTM through Q2 2026 (fundamentals.json TTM revenue), with Q2 2026 at $119.2M, +24% year over year, at a 95% gross margin (Q2 2026 release). U.S. penetration already exceeds 60% of the diagnosed DEB pool (730+ reimbursement approvals, 640+ prescribers); Germany, France, Japan and the UK are launched, with Italy and Spain targeted by end-2026. The pipeline reuses the platform: KB803 (ocular DEB) and KB801 (neurotrophic keratitis) registrational readouts are due in late 2026, KB407 (cystic fibrosis), KB408 (alpha-1 antitrypsin deficiency) and KB707 (NSCLC) are behind them.

## Owner's earnings
**History (financials_history.csv):** OE was negative every year through FY2023 (pre-commercial), then inflected: FY2023 −$5.06/share, FY2024 $2.36/share (OE total $70.1M), FY2025 $4.49/share (OE total $134.4M). OE-positive years: 2 of the last 5. FY2025 detail: OCF $200.9M − capex $12.0M (PaymentsToAcquirePropertyPlantAndEquipment rollup) − SBC $54.5M = $134.4M. The maintenance definition tells the same story — this is a genuinely cash-generative business now, not an accounting artifact.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $200,865,000 − prior YTD $83,698,000 + current YTD $155,171,000 = **TTM $272,338,000**
- Capex: FY $11,951,000 − prior YTD $8,108,000 + current YTD $10,713,000 = **TTM $14,556,000**
- SBC: FY $54,514,000 − prior YTD $27,597,000 + current YTD $27,765,000 = **TTM $54,682,000**
- Shares (current-YTD weighted diluted): **30,584,000**
- **TTM OE total $203,100,000 → base OE/share $6.64** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $2.36/share — rejected as the base: its window still contains pre-commercial FY2023 (−$5.06/share), so the median is the distorted figure, not the latest year (see BASE_DIVERGENCE). TTM OE margin is 46.1% of TTM revenue (fundamentals.json), consistent with the 95% gross margin minus a still-full R&D/SG&A load.

**Balance sheet (FY2025, financials_history.csv):** cash $496.3M (the company reports ~$955M of cash and investments at YE2025 and $1.1B at Q2 2026 — the difference is marketable securities the engine's cash tag does not capture), total liabilities $114.2M, equity $1,219.6M, lease liabilities $9.3M, and no borrowings — the company is debt-free (see DEBT_TAGS_BLANK).

## Moat: 6/10 — real but narrow
Justification: VYJUVEK's orphan exclusivity, 95% gross margin, entrenched reimbursement/prescriber base and the redosable HSV-1 platform give a real but narrow moat: one product, one small patient pool, only two years of positive ROIC history, and competition (ZEVASKYN) now entering DEB.
- FOR: First and only FDA-approved redosable gene therapy for DEB (approved 2023, from birth); orphan-drug exclusivity and the patent estate around the HSV-1 platform. 95% gross margin (Q2 2026) on lean in-house manufacturing — a structural cost advantage. Entrenched access: 730+ U.S. reimbursement approvals, 640+ prescribers, >60% penetration of the diagnosed U.S. DEB pool. The platform carries an FDA Platform Technology Designation and registrational programs in eye (KB803, KB801), lung (KB407, KB408) and skin (KB111) reuse the same delivery engine. Returns inflecting: ROIC proxy (fundamentals.json roic_proxy) −22.1% (2023) → +10.2% (2024) → +17.6% (2025), TTM operating margin 44.9%; debt-free with ~$1.1B cash and investments (Q2 2026).
- AGAINST: Single product — VYJUVEK is effectively 100% of revenue and the DEB pool is small, with U.S. penetration already above 60% of diagnosed patients. Growth is decelerating (FY2025 +33.9%, TTM revenue +22.6%, Q2 2026 +24%). Abeona's ZEVASKYN (approved 2025) now competes for recessive DEB wounds. European pricing/reimbursement is still being negotiated, so ex-U.S. realized pricing is uncertain. Everything beyond VYJUVEK is binary clinical optionality (KB803/KB801 readouts late 2026), and SBC runs ~12–14% of revenue.
- ROIC check (step 5): a 6 — not 7+ — because the measured history has only just crossed above the cost of capital and has not held there through a cycle; the franchise's durability past the first product is unproven.
- A 6 gives CAP = 9.8 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 9.8 years, 15-year projection.

## DCF — final run (2026-10-20)
**Growth recalibration (written reason):** the engine's blended growth is 171.85% and g_base hit the 35% cap because the revenue CAGRs are launch artifacts — revenue was $0 through FY2022, so the 5-yr and 3-yr CAGRs (both 176.85%) measure a launch, not a growth rate. The prints that mean something are decelerating: latest FY revenue YoY +33.94%, TTM revenue +22.6% YoY (fundamentals.json), Q2 2026 +24%. Scenario starts were therefore set via offsets (−0.25 / −0.18 / −0.13 / −0.08 / −0.01 vs the capped g_base) to 10 / 17 / **22** / 27 / 34%. The base start (22%) sits on the TTM print. The super-bull start (34%) is above the latest print for a written reason: it is the path where Italy/Spain launch on schedule and a second product (KB803 or KB801, readouts due late 2026) starts contributing inside the hold period — that re-acceleration is exactly what the 10%-weighted super-bull case is for. Probabilities 10/25/30/25/10; OE multipliers 0.75/0.90/1.00/1.10/1.25. Price $320.25.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | 10.0% | 0.75 | U.S. saturation bites, EU pricing disappoints, pipeline readouts fail | $57.01 | 4.94% |
| Bear | 25% | 17.0% | 0.90 | Growth decays to the high-teens; single-product multiple compresses | $93.27 | 6.66% |
| Base | 30% | 22.0% | 1.00 | TTM trajectory decays normally over the CAP; intl ramp offsets U.S. maturity | $129.08 | 8.25% |
| Bull | 25% | 27.0% | 1.10 | Italy/Spain launch well; one pipeline program reaches market late in the CAP | $176.53 | 10.19% |
| Super bull | 10% | 34.0% | 1.25 | Multi-product platform path — two more approvals, growth re-accelerates | $271.06 | 13.50% |

- **Probability-weighted: IV@15% $138.98 (−56.6% vs price), IV@12% $194.19, IV@10% $257.04, weighted IRR 8.71%, base-case IRR 8.25%**
- **Tier by numbers: D.** Diagnostics (key_numbers.md): OE yield 2.07%, terminal value 24.1% of IV@15%, scenario spread 4.75x, 9.6 months since FY end. Even the super-bull case (13.50% IRR, IV@15 $271.06) does not clear the 15% hurdle at $320.25 — the price already pays for the platform outcome.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.6 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, legs quoted above.
- **BASE_DIVERGENCE** (latest FY $4.49 vs 3-yr median $2.36): the median is the distorted one — its window contains pre-commercial FY2023 at −$5.06/share, a year in which VYJUVEK had only a partial launch year of revenue ($50.7M). The latest FY and TTM figures are on the commercial run-rate; TTM base used, median retained in the reporting.
- **BASIS_BREAK_SUSPECT**: the >60% revenue jumps are the VYJUVEK launch itself (revenue $0 through FY2022 → $50.7M FY2023 → $290.5M FY2024), not a divestiture, M&A or restatement — no business was bought or sold. Consequence handled in the growth recalibration: no CAGR from the pre-launch base is used anywhere.
- **NI_OCF_DIVERGENCE** (2023): net income was +$10.9M while OCF was −$88.8M because FY2023 net income includes a **$100.0M gain on the sale of a Priority Review Voucher** (FY2023 results release / 10-K) plus $22.6M of interest and other income — the voucher proceeds are an investing inflow, so they never touched OCF. The OE base is OCF-based throughout, so the one-off does not contaminate it; operations in 2023 genuinely burned cash.
- **DILUTION** (share count +5.52%/yr): the 5-yr CAGR is inflated by the pre-profit years; the recent pace is ~2–3%/yr (29.74M FY2024 → 29.95M FY2025 → 30.58M TTM weighted). The driver is SBC — $54.5M in FY2025, $54.7M TTM, ~12–14% of revenue — which is already deducted in full in the OE definition; no buyback offsets it. Noted as a moat-against, not a base adjustment.
- **SHARES_FALLBACK** (2017–2019): those pre-/early-public years use the basic/outstanding count recorded in the shares_tag column, so per-share history there is approximate. It does not touch the base: the last-3-FY window and the TTM all use filed diluted counts.
- **DEBT_TAGS_BLANK**: no debt tag reports for the latest fiscal year because there is no debt to report — from the FY2025 filing (financials_history.csv): total liabilities $114.2M against equity $1,219.6M, lease liabilities $9.3M, cash $496.3M (~$955M including marketable securities per the company). Net debt is not merely unknown; the balance sheet is unlevered, so no leverage verdict is needed.
- **WIDE_SCENARIO_SPREAD** (4.75x): real — the outcome range is genuinely wide because most of the price is pipeline optionality. Confidence is capped at medium, and the verdict is sized to the conservative end.
- **TIER_BAND** (bear D at 6.66% vs bull C at 10.19%): the verdict is sized to the bear end — the final tier is D either way, and even the bull case does not reach the 15% hurdle.
- Share basis (key_numbers.md, informational): an in-history split fact dated 2017-09-05 (ratio 0.222222) is already reflected in the filed history; no adjustment applies and no recent share-count jump matches it, so DILUTION above is a real SBC pace, not a split artifact.

## My thoughts / method range
- The method range here is narrower than the scenario spread suggests: on the rejected median base ($2.36/share) the same scenarios would print far lower; on the TTM base the range is D across bear/base and C only in the bull case. The TTM base is the defensible one — it is filing-derived, current, and its 46.1% OE margin is corroborated by the reported 95% gross margin.
- Quality is not the debate: debt-free, ~$1.1B of cash and investments, 95% gross margin, profitable while funding five registrational programs. Price is the debate: at $320.25 the market is paying $9.592B for $203.1M of TTM owner's earnings (2.07% OE yield) — i.e., paying today for KB803/KB801/KB407 success that has not read out yet.
- What would change the verdict: the late-2026 KB803 (IOLITE) and KB801 (EMERALD-1) top-line readouts, Italy/Spain launch pricing, and any sign the U.S. DEB pool keeps expanding the treated population (penetration is already >60% of diagnosed, so growth must come from diagnosis expansion and ex-U.S. uptake).
- Hurdle prices (weighted path, key_numbers.md): clears 15% at $138.98, 20% at $91.07, 25% at $65.91. At the current price a buyer is underwriting the super-bull path at a 10% probability and still not clearing 15% on it.

## Final verdict
- **Final tier: D** (weighted IRR 8.71%; bear D 6.66% → bull C 10.19%)
- Confidence: **Medium** (high on the TTM base and balance sheet, low on any single growth path — scenario spread 4.75x)
- One-liner: Profitable single-product gene-therapy leader (VYJUVEK at a 95% gross margin, debt-free, $1.1B cash), moat 6/10 — does not clear 15% at $320.25 (weighted IRR 8.7%, weighted IV@15% $138.98); it would clear the 15% hurdle only below ~$139.
