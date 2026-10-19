# MANH — Manhattan Associates, Inc.
Engine 5.4.0 run, 2026-10-18. Price $222.17 (nasdaq_quote_api), market cap $13.564B — in scope under $40B.

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.json, fundamentals.json or financials_history.csv — none are recomputed.

## What it is
Supply-chain and omnichannel commerce software (SIC 7372, prepackaged software): warehouse management (WMS), transportation (TMS), order management and store/inventory on the unified, versionless Manhattan Active cloud platform. Revenue is a mix of cloud subscriptions (growing fast), professional services (roughly half of revenue) and a shrinking on-premise license/maintenance tail that customers are converting to cloud.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $389,470,000; SBC $111,263,000 (always a real cost); capex $15,457,000.
- **Conservative owner's earnings FY2025: $262,750,000 = $4.30/share** (key_numbers.md: latest FY OE/share $4.30)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $258,000,000 — essentially the same as the conservative figure, which corroborates the FY2025 base despite the OCF jump that year (see NI_OCF_DIVERGENCE below).
- OE positive 5 of the last 5 fiscal years. Share count is shrinking: diluted shares 61,054,000 latest, share-count CAGR −1.25%/yr, backed by buybacks of $435,000,000 TTM (fundamentals.json).

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $389,470,000 − prior YTD $149,310,000 + current YTD $174,725,000 = **TTM $414,885,000**
- Capex: FY $15,457,000 − prior YTD $4,871,000 + current YTD $5,108,000 = **TTM $15,694,000**
- SBC: FY $111,263,000 − prior YTD $53,101,000 + current YTD $55,880,000 = **TTM $114,042,000**
- Shares (current-YTD weighted diluted): **59,515,000**
- **TTM OE total $285,149,000 → base OE/share $4.79** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $3.11/share — rejected as the base; see BASE_DIVERGENCE below. It is still reported in key_numbers.md.

## Moat: 6/10 — moderate-strong, not wide
Justification: Tier-1 WMS leader (~15-20% share) on a versionless cloud platform with mission-critical switching costs, 5.5-6yr contracts and RPO of $2.47B, but share is not commanding vs Blue Yonder/SAP/Oracle, roughly half of revenue is low-growth services, and gross margin (53-56%) reflects that mix; ROIC proxy is not meaningful because the net-cash balance sheet makes invested capital near-zero/negative.
- FOR: Mission-critical WMS/TMS/OMS installed base with high switching costs and reimplementation risk for customers; Versionless Manhattan Active cloud platform, quarterly updates, unified WMS/TMS/store/order suite for cross-sell; Long contracted backlog: RPO $2.47B at Q2 2026 (+23% YoY), contract duration ~5.5-6 years; Premium pricing position and >70% win rate cited by management; cloud revenue +26% YoY in Q2 2026; Asset-light, debt-free, high cash conversion: OE positive 5/5 years, operating margin expanded to 25.9% in FY2025.
- AGAINST: No commanding share: Blue Yonder, SAP, Oracle and Körber contest every tier-1 deal; WMS share estimated only ~15-20%; Services is roughly half of revenue and grows ~3%, dragging gross margin to 53-56% vs pure SaaS peers; Growth decelerated hard in the cloud transition: total revenue +3.7% in FY2025 as license/maintenance attrits; SBC is heavy and rising: $111.3M in FY2025, 28.6% of OCF, requiring large buybacks ($435M TTM) to shrink the count; End-demand tied to retail/logistics capex and macro; bookings are lumpy by management's own guidance language.
- **Returns evidence (fundamentals.json):** gross margin last five fiscal years: 55.1% (2021), 53.3% (2022), 53.6% (2023), 54.8% (2024), 56.3% (2025) — stable to rising, but at a services-diluted level, not pure-SaaS 70%+. Operating margin rose from 19.9% (2022) to 25.9% (2025). The `roic_proxy` series is **not usable here**: with cash of $328,747,000 exceeding equity of $314,765,000 and no filed debt, invested capital (equity + debt − cash) is near zero or negative, so the proxy swings wildly sign-to-sign. The honest returns evidence is the margin record, 5/5 OE-positive years and debt-free cash conversion — enough for a 6, not enough (no usable through-cycle ROIC series, no commanding share) for a 7+.
- A 6 gives CAP = 9.8 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 9.8 years, 15-year projection.

## DCF — final run (2026-10-18)
**Growth recalibration (written reason):** the engine's blended growth is 13.83% (rev CAGR 5y 13.02%, rev CAGR 3y 12.12%, latest rev YoY 3.75%, OE/share CAGR 2y 25.90%). That blend is stale: the CAGRs average in the 2022-23 boom, and the OE/share CAGR rides the FY2025 OCF jump. Actual recent prints are far lower — FY2025 revenue +3.75%, Q1 2026 +7.4% YoY, Q2 2026 +9.3% YoY, and FY2026 guidance of $1.160-1.166B total revenue (~7-8% growth; ~11-13% excluding license/maintenance attrition, cloud guided +24%). Scenario starts were therefore set via offsets (−0.1183 / −0.0783 / −0.0383 / +0.0117 / +0.0717 vs g_base) to 2 / 6 / **10** / 15 / 21%. The base start of 10% sits *above* guided total-revenue growth, crediting cloud mix shift, RPO conversion (RPO +23% YoY) and the shrinking share count; bull at 15% requires total growth back at the 2024 pace, and super bull at 21% is a return to the 2023 boom pace, hence only 10% weight. Probabilities were bear-tilted to 10/30/30/20/10 (from the 10/25/30/25/10 default) because three record bookings quarters and +23% RPO argue against the super-bear getting more weight, while the price demands growth the company has not printed since 2023. OE multipliers are the defaults 0.75/0.90/1.00/1.10/1.25. Price $222.17.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | 2.0% | 0.75 | Cloud conversion stalls; macro cuts retail/logistics capex; growth stays at the 2025 trough | $28.81 | 4.11% |
| Bear | 30% | 6.0% | 0.90 | Growth stays at guided total-revenue pace; license/maintenance attrition offsets cloud | $41.31 | 4.93% |
| Base | 30% | 10.0% | 1.00 | Cloud +26% mix shift and RPO conversion lift total OE growth modestly above revenue guidance | $54.84 | 5.85% |
| Bull | 20% | 15.0% | 1.10 | Bookings momentum converts; total growth returns to the 2024 pace; Active AI agents monetize | $75.28 | 7.22% |
| Super bull | 10% | 21.0% | 1.25 | Return to 2023-boom growth on Editions/AI-agent expansion into smaller customers | $111.41 | 9.44% |

- **Probability-weighted: IV@15% $57.93 (−73.9% vs price), IV@12% $78.44, IV@10% $101.51, weighted IRR 6.10%, base-case IRR 5.85%**
- **Tier by numbers: D** (bear D → bull D — the whole band is D; even the super bull only reaches 9.44% IRR). Diagnostics (key_numbers.md): OE yield 2.16%, terminal value 20.7% of IV@15%, scenario spread 3.87x, 9.6 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (latest fiscal year ended 10 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, legs quoted above.
- **NI_OCF_DIVERGENCE** (net income and operating cash flow differ by >40% in 2025): structural, not a one-off. FY2025 net income was $219,948,000 vs OCF of $389,470,000. The largest single bridge is SBC of $111,263,000 — a non-cash expense deducted in net income and added back in OCF — with the remainder in working-capital/deferred-revenue timing (ΔNWC −$38,052,000 in financials_history.csv). It does **not** flatter the base: conservative OE deducts SBC in full, and the maintenance definition (which starts from net income) lands at $258,000,000 vs the conservative $262,750,000 for FY2025. No tax-deposit or impairment one-off was found.
- **DEBT_TAGS_BLANK** (no debt tag reports for the latest fiscal year — net debt UNKNOWN to the engine): stated from the filing — Manhattan carries essentially **no debt**. FY2025 balance sheet (fundamentals.json / financials_history.csv): cash $328,747,000, equity $314,765,000, total assets $839,388,000, operating lease liabilities $61,063,000, and no debt tag in any filed year. Q2 2026 reporting likewise describes $186M cash and no debt after $275M of H1 buybacks. The engine's null net debt means "no leverage to model," not hidden leverage; the only debt-like item is the $61.06M operating lease liability the engine does report.
- **BASE_DIVERGENCE** (latest FY OE/share $4.30 vs 3-yr median $3.11): the **median is the distorted one** — it is a lagging figure for a business whose OE/share climbed sequentially ($2.71 in 2023, $3.11 in 2024, $4.30 in 2025, per financials_history.csv) as OCF expanded, and the TTM figure of $4.79 extends the same progression for two more quarters rather than spiking and reversing. Caution noted: part of the FY2025 OCF step-up ($295,003,000 → $389,470,000) is working-capital timing while net income was flat, which is why the growth starts were recalibrated down (above) instead of extrapolating the OE/share CAGR of 25.90%. TTM base used; median retained in key_numbers.md.
- Preliminary-run flags **LOW_OE_YIELD** (1.4% on the median base) and **WIDE_SCENARIO_SPREAD** (4.43x) do not appear in the final run: on the TTM base the OE yield is 2.16% and the spread is 3.87x. Both points still stand in substance — at $222.17 the valuation rests almost entirely on growth, and the outcome range is wide — which is why confidence is capped at medium and the verdict is sized to the conservative end. The tier is nevertheless not fragile in direction: every scenario, including the super bull, lands in Tier D.

## My thoughts / overlay
- This is a quality-vs-price case, not a quality debate: debt-free, OE-positive 5/5 years, RPO $2.47B (+23% YoY), cloud +26%, record bookings three quarters running, guidance raised in Q2 2026 — and the stock still only offers a 6.10% weighted IRR at $222.17 — the base OE yield at this price is just 2.16% (key_numbers.md).
- Method range: on the engine's median base ($3.11/share) with the unadjusted blend, the preliminary run printed a weighted IRR of 5.26% and IV@15% of $43.42; on the TTM base with recalibrated growth, 6.10% and $57.93. Both are Tier D — the range (D to D) is unusually tight for this sweep because no defensible base or growth path gets near the price.
- Watch items: the Q2 2026 GAAP margin dip (an $8.3M restructuring charge on a ~6% headcount cut), SBC at 28.6% of OCF and rising in dollars, services growth of only ~3%, and whether the September 2026 "Editions" tiering (Essentials/Enterprise/Enterprise Premier) actually expands the addressable market or just discounts the premium product.
- Hurdle-clearing prices (weighted path, key_numbers.md): clears 15% at $57.93, 20% at $39.75, 25% at $29.93 — i.e. at the −73.9% upside figure in key_numbers.md, the price sits far above the level where the weighted case earns Andrew's base hurdle.

## Final verdict
- **Final tier: D** (weighted IRR 6.10% on the final inputs; bear and bull scenarios are also D, super bull 9.44%)
- Confidence: **Medium** (high on the OE base and the direction of the verdict — every scenario is D — medium on any single growth path given the 3.87x scenario spread)
- One-liner: High-quality supply-chain software leader, moat 6/10 — does not clear 15% at $222.17 (weighted IRR 6.1%, IV@15% $57.93, even super-bull IRR only 9.4%); clears 15% only below ~$58.
