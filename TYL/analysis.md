# TYL — Tyler Technologies, Inc.
v5 / engine 5.4 run, 2026-10-17. In scope (market cap $15.810B at $360.87, nasdaq_quote_api — under the $40B cap).

All figures below are copied from key_numbers.md, dcf_numbers.json, or ttm.py output — none are recomputed.

## What it is
The dominant U.S. public-sector vertical software company: mission-critical systems of record for courts/justice, public safety dispatch, property tax assessment, municipal finance, permitting, payments and school administration, sold to state and local governments across all 50 states. Two engines: Enterprise Software (core back-office systems) and Platform Technologies (payments/digital citizen services, built on the 2021 NIC acquisition). Recurring revenue was 87.8% of FY2025 revenue; client retention runs ~98%. The current growth engine is the on-premise-to-SaaS conversion — SaaS revenue +21.7% in Q2 2026, the 22nd straight quarter of ≥20% SaaS growth — partly offset by the planned decline of maintenance revenue and the terminated Texas payments contract dragging transaction revenue.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $653,543,000; capex $16,015,000; SBC $151,276,000 (always a real cost).
- **Conservative owner's earnings FY2025: $486,252,000 = $11.10/share** (key_numbers.md: latest FY OE/share $11.10; latest FY OE total $486.3M)
- Normalized (3-yr median) base: $11.06/share — close to the latest FY because FY2024 printed the same $11.06 after a step-change in OCF; FY2023 was $5.88/share.
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC) prints far above the conservative figure in FY2025 — it is distorted by a large working-capital swing (ΔNWC −$557,408,000 in the filed history), so the OCF-based conservative figure is the cleaner one and is used throughout.
- OE positive 5 of the last 5 fiscal years. Net debt $-415.7M — i.e. net cash (key_numbers.md); net debt / normalized OE −0.71x. Balance-sheet note: that net-cash figure is the FY2025 position; in 2026 the company issued $1.4B of convertible notes and spent heavily on buybacks ($928,050,000 TTM per fundamentals.json, including ~$505M in Q2 2026 alone) plus the For The Record acquisition (~$213M), so the current balance sheet is less net-cash than the FY-end figure the engine carries.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $653,543,000 − prior YTD $154,469,000 + current YTD $231,673,000 = **TTM $730,747,000**
- Capex: FY $16,015,000 − prior YTD $7,822,000 + current YTD $8,288,000 = **TTM $16,481,000**
- SBC: FY $151,276,000 − prior YTD $75,962,000 + current YTD $80,821,000 = **TTM $156,135,000**
- Shares (current-YTD weighted diluted): **41,853,000** (below the FY2025 43,812,000 — the buyback is shrinking the count)
- **TTM OE total $558,131,000 → base OE/share $13.34** (base_source: ttm_json)
- The normalized median ($11.06/share) was not used as the base: it averages in the step-change and understates the run rate the last four quarters actually printed (TTM revenue +8.2% YoY, TTM OE +14.6% YoY per fundamentals.json). The Q2 2026 $25M gain on remeasurement of the For The Record equity stake sits in net income, not OCF, so it does not contaminate the OCF-based TTM base.

## Moat: 7/10 — strong, with a measured-ROIC caveat
Justification: Dominant U.S. state/local govtech franchise: mission-critical systems of record, ~98% client retention, 87–88% recurring revenue, 12–24 month implementations and state-by-state regulatory logic embedded in the product make switching rare and painful. Measured ROIC proxy is only 4.3–8.8% over the last five fiscal years (rising every year since 2021), which understates the franchise: the invested-capital denominator carries goodwill/intangibles from 50+ acquisitions including the ~$2.3B NIC deal, and the SaaS conversion depressed margins mid-transition — gross margin has recovered from 42.4% (2022) to 46.5% (FY2025) and 47.2% TTM as SaaS mix rises. That written reason is why a 7 stands despite ROIC not yet sitting well above the cost of capital.
- FOR: Mission-critical systems of record for courts, public safety, tax assessment, municipal finance and schools — switching means re-implementing core government operations; ~98% client retention and 87.8% recurring revenue (FY2025), contracts long and rarely re-bid; state-by-state regulatory and workflow logic built for government from the ground up, vs generic ERP adapted by Oracle/SAP/Workday; breadth across 50 states plus the NIC payments platform monetizing the installed base (~500M transactions/yr); SaaS conversion tailwind — SaaS +21.7% in Q2 2026, 22 straight quarters of ≥20% SaaS growth, gross margin expanding with mix (fundamentals.json: gross margin 42.4% in 2022 → 46.5% FY2025 → 47.2% TTM; ROIC proxy 4.3% → 5.5% → 5.4% → 7.9% → 8.8% over 2021–2025).
- AGAINST: Measured ROIC proxy only 4.3–8.8% over the last five fiscal years — pricing power has not yet converted into high returns on the acquisition-heavy capital base; AI lowers the cost of building software, eroding the switching-cost moat of legacy vertical vendors over time, and government buyers are actively evaluating AI budget share; growth has decelerated to high-single digits (Q2 2026 revenue +8.2%) and one-off contract losses happen (Texas payments contract termination); competition from CentralSquare, Motorola Solutions and horizontal platforms with far larger R&D budgets; customer budgets are municipal/state appropriations — long sales cycles and budget timing deferred bookings in 2025.
- A 7 gives CAP = 11.1 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 11.1 years, 15-year projection.

## DCF — engine 5.4 final run (2026-10-17)
Growth recalibration (written reason): the engine's blended growth is 11.39%, but two blend components are artifacts — the OE/share CAGR 2y of 37.33% is a rebound off the depressed FY2023 base ($5.88/share), not a revenue growth rate, and the 5-yr revenue CAGR of 15.87% straddles the 2021 NIC acquisition year (revenue +42.6% in FY2021 on the deal). The revenue signals that mean something — 3-yr CAGR 8.02%, latest FY YoY 9.10%, TTM revenue +8.2%, Q2 2026 +8.2%, and FY2026 guidance of $2.535–2.575B total revenue (subscription +13–16%, SaaS +21.5–23.5%, maintenance −3% to −5%) — center on ~9.5%. Scenario starts were therefore set via offsets (−0.114 / −0.064 / −0.019 / +0.016 / +0.056 vs g_base) to −0.0 / 5.0 / **9.5** / 13.0 / 17.0%. Even the super-bull start (17.0%) sits below the growth rates Tyler printed in its acquisition/inflection years, which is deliberate: no recent organic print supports a higher start. Probabilities 10/25/30/25/10 (defaults — the recurring, government-funded revenue base argues against fattening either tail); OE multipliers 0.75/0.90/1.00/1.10/1.25 (defaults). Price $360.87.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -0.0% | 0.75 | SaaS conversion stalls, municipal budgets freeze, AI entrants take new deals | $72.87 | 4.92% |
| Bear | 25% | 5.0% | 0.90 | High-single-digit growth fades to mid-single; margin gains stall | $110.69 | 6.46% |
| Base | 30% | 9.5% | 1.00 | Guided trajectory: SaaS growth offsets maintenance decline, fade over the CAP | $152.24 | 8.13% |
| Bull | 25% | 13.0% | 1.10 | Peak conversion years 2027–29 land early; payments re-accelerates post-Texas | $197.77 | 9.83% |
| Super bull | 10% | 17.0% | 1.25 | Conversion + payments + AI products compound; margins head toward the 2030 targets | $271.82 | 12.34% |

- **Probability-weighted: IV@15% $157.25 (−56.4% vs price), IV@12% $213.02 (−41.0%), IV@10% $275.81, weighted IRR 8.35%, base-case IRR 8.13%**
- **Tier by numbers: D** (bear tier D, bull tier D — no TIER_BAND). Diagnostics (key_numbers.md): OE yield 3.70%, terminal value 20.8% of IV@15%, scenario spread 3.73x, net debt −0.71x normalized OE, 9.5 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (latest fiscal year ended 10 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, legs quoted above.
- **NI_OCF_DIVERGENCE** (net income and operating cash flow differ by >40% in 2023, 2024, 2025): structural, not a one-off. In each flagged year OCF runs roughly 2x net income because the two big non-cash charges — SBC ($108,338,000 in 2023; $122,813,000 in 2024; $151,276,000 in 2025) and D&A ($154,079,000 / $143,437,000 / $138,358,000) — are added back in the cash-flow statement (all figures from financials_history.csv). There is no tax-deposit or impairment story to find; the divergence is the normal shape of an acquisitive software P&L with heavy intangible amortization and equity comp. It does not contaminate the base because the conservative OE is OCF-based and deducts SBC in full.
- The preliminary run's **WIDE_SCENARIO_SPREAD** flag (4.46x on default inputs) fell away in the final run after the growth recalibration; the final spread is still 3.73x, which is why confidence is medium, not high.

## My thoughts / overlay
- This is a quality-versus-price result, not a quality dispute. Even the super-bull case (17% growth start, 1.25x OE) yields only a 12.34% IRR at $360.87 — the stock does not clear 15% under any scenario in the set, and both the bear and bull tiers are D.
- The method range is narrow by this sweep's standards: on the normalized median base with default growth (preliminary run) the weighted IRR was 7.72%; on the TTM base with recalibrated growth it is 8.35%. Both are Tier D — the verdict is not assumption-dominated the way an inflection name is.
- What the price embeds: at $360.87 the market is paying for the Tyler 2030 story (SaaS conversion peak in 2027–29, non-GAAP operating margin toward 30%+) essentially in full, today. The cash flows may well arrive; the DCF says a buyer at this price is not paid a 15% return for waiting.
- Watch items: whether H2 2026 free cash flow hits the guided 26–28% margin (H1 ran well below it, on seasonal collections); transaction growth ex-Texas from Q4 2026; whether G&A normalizes after litigation/integration costs; and the pace of buybacks now funded partly by the $1.4B converts.

## Final verdict
- **Final tier: D** (weighted IRR 8.35% on the final inputs; scenario range 4.92%–12.34%, bear and bull both D)
- Confidence: **Medium** (filing-direct TTM base and both flags resolved; held back from high by the 3.73x scenario spread and the ROIC-versus-moat question pass 2 will press)
- Hurdle-clearing prices (weighted path): 15% at $157.25 · 20% at $107.93 · 25% at $81.32
- One-liner: High-quality govtech compounder, moat 7/10, but at $360.87 it does not clear 15% — weighted IRR 8.3%, weighted IV@15% $157.25; it would need to fall to ~$157 to clear the 15% hurdle.
