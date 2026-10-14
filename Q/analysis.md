# Q — Qnity Electronics, Inc.
v5 run, 2026-10-14. Market cap $25.568B at $121.8685 (nasdaq_quote_api) — in scope under $40B. All figures below are copied from dcf_numbers.json, financials_history.csv, or ttm.json — none are recomputed.

## What it is
Pure-play electronics / semiconductor materials provider spun off from DuPont on November 1, 2025. Two segments: Semiconductor Technologies (fab consumables — CMP, photoresists, seals such as Kalrez) and Interconnect Solutions (advanced packaging, laminates, thermal and PCB materials). Q2 2026 from research: net sales $1.429B, +22% year over year, with Semiconductor Technologies $744M and Interconnect Solutions $685M; management raised full-year 2026 guidance twice to net sales $5.55B–$5.65B, adjusted EPS $4.40–$4.60, and adjusted free cash flow $600M–$700M, citing AI, advanced packaging and advanced-node demand (advanced-node sales grew over 20% in Q2).

## Owner's earnings
From financials_history.csv (EDGAR filing-direct):
- 2023: revenue $4,035,000,000; OCF $882,000,000; capex $231,000,000 (tag PaymentsToAcquireProductiveAssets); SBC $13,000,000; conservative OE $638,000,000; maintenance OE $705,000,000
- 2024: revenue $4,335,000,000; OCF $1,061,000,000; capex $200,000,000; SBC $13,000,000; conservative OE $848,000,000; maintenance OE $918,000,000
- 2025: revenue $4,754,000,000; OCF $1,273,000,000; capex $285,000,000; SBC $20,000,000; conservative OE $968,000,000; maintenance OE $907,000,000
- Conservative and maintenance definitions are in the same ballpark in all three years, which supports the OE series. OE positive 3/3 years in the engine history. SBC is small relative to OCF and is treated as a real cost throughout.
- Latest FY OE/share $4.613918017159199; normalized (median of last 3 FY) OE/share $4.049665711556829 (dcf_numbers.json).

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $1,273,000,000 − prior YTD $480,000,000 + current YTD $376,000,000 = TTM $1,169,000,000
- Capex: FY $285,000,000 − prior YTD $153,000,000 + current YTD $212,000,000 = TTM $344,000,000
- SBC: FY $20,000,000 − prior YTD $8,000,000 + current YTD $25,000,000 = TTM $37,000,000
- Shares (current-YTD weighted diluted): 210,300,000
- **TTM OE total $788,000,000 → base OE/share $3.747028055159296** (base_source: ttm_json)
- Why TTM over the median: the FY ended 9.4 months ago (STALE_FY), and the TTM window captures the weaker H1 2026 OCF and the elevated capex for capacity builds. It is also the more conservative base — it sits below both the latest FY figure and the 3-year median. Note the tension and do not hide it: revenue is accelerating (+22% in Q2) while TTM OE/share fell, because capex and spin/transformation costs rose faster than OCF in H1 2026. If capex normalizes toward the long-term rate management discussed in research, OE/share would be higher than this base; the scenario multipliers and growth recalibration below are where that possibility is priced, not in a hand-adjusted base.

## Moat: 6/10 — moderate
Justification: qualified, mission-critical semiconductor materials with long qualification cycles, portfolio breadth and co-development ties give real switching costs, but the business is cyclical, concentrated, levered from the spin, and has no standalone track record to prove pricing power through a downturn.
- FOR: Mission-critical qualified materials — long fab qualification cycles create switching costs; Portfolio breadth across semiconductor fabrication and interconnect / advanced packaging; Deep co-development relationships and local-for-local footprint near major fabs; AI / advanced-node content growth — advanced-node sales grew >20% in Q2 2026
- AGAINST: Semiconductor cyclicality — consumables demand tracks fab utilization; Customer and China concentration — China >30% of sales per research; Levered spin balance sheet — $4.0B debt, ~$250M expected 2026 interest (research figures, not engine outputs); Elevated growth capex — TTM capex $344,000,000 and rising for Delaware/Taiwan builds; No long standalone history — only 3 carve-out fiscal years, spin completed Nov 1 2025
- A 6 gives CAP = 9.8 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 9.8 years, 15-year projection.

## DCF — v5 final run (2026-10-14)
Growth recalibration (written reason): the engine's g_base is 9.006562593490075% (growth blend 9.101962680066367% in dcf_numbers.json), built from carve-out history — rev CAGR 8.538412096003545%, latest FY rev YoY 9.665513264129189%, OE/share CAGR 2y 23.041409992362394%. That blend is stale against current prints: Q2 2026 sales +22% year over year and full-year 2026 sales guidance $5.55B–$5.65B against FY2025 revenue $4,754,000,000. Scenario starts were therefore set via offsets −0.09 / −0.01 / +0.07 / +0.12 / +0.18 vs g_base, to 0.01% / 8.01% / 16.01% / 21.01% / 27.01%. The base start (16.01%) sits below the Q2 print and roughly at guided full-year sales growth, because OE has lagged revenue in H1 2026 on elevated capex; the super-bull start (27.01%) sits above the Q2 revenue print on the argument that capex normalization plus operating leverage could make OE grow faster than sales — that is the optimistic case, weighted only 10%. Probabilities 10/25/30/25/10 (defaults, kept: AI tailwind is real but cyclicality, leverage and concentration argue against skewing bullish); OE multipliers 0.75/0.90/1.00/1.10/1.25 (defaults). Price $121.8685.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | 0.01% | 0.75 | Semi downturn, fab utilization falls, levered OE compresses | $20.62 | 4.54% |
| Bear | 25% | 8.01% | 0.90 | Growth reverts to carve-out history, capex stays elevated | $35.33 | 6.34% |
| Base | 30% | 16.01% | 1.00 | Guided 2026 growth decays normally over the CAP | $55.97 | 8.77% |
| Bull | 25% | 21.01% | 1.10 | Q2 pace holds, capex begins to normalize | $76.71 | 10.96% |
| Super bull | 10% | 27.01% | 1.25 | AI content supercycle plus full capex normalization | $113.22 | 14.29% |

- **Probability-weighted: IV@15% $58.18, IV@12% $80.01, IV@10% $104.71, weighted IRR 9.05%, base-case IRR 8.77%**
- **Tier by numbers: D.** Diagnostics (dcf_numbers.json): OE yield 3.07%, terminal value 22.35% of IV@15%, scenario spread 5.49x, net debt 4.08x normalized OE (on the TTM base basis reported by the engine), 9.43 months since FY end.
- Net debt latest $3,209,000,000 and FY2025 cash $915,000,000 with long-term debt $4,100,000,000 are from dcf_numbers.json / financials_history.csv — the leverage is folded into the verdict below, not added again to the IV (the engine's IV is an equity value on OE after interest-bearing OCF).

## Flags — every fragility flag resolved
- **STALE_FY** (latest fiscal year ended 9 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, quoted in full above (OCF $1,169,000,000; capex $344,000,000; SBC $37,000,000; shares 210,300,000; TTM OE/share $3.747028055159296).
- **NI_OCF_DIVERGENCE** (net income and OCF differ by >40% in 2025): FY2025 net income $729,000,000 vs OCF $1,273,000,000 in financials_history.csv, with D&A $376,000,000 in the same row — the bulk of the gap is non-cash D&A, which the OCF-based conservative OE already handles correctly (it starts from OCF, not net income). The maintenance OE for 2025 ($907,000,000) sits close to the conservative figure ($968,000,000), so the divergence does not contaminate the base. No one-off tax deposit or impairment was found in research that changes this reading; spin/transformation charges depress GAAP net income relative to OCF, which is the same direction.
- **THIN_HISTORY** (only 3 fiscal years of data): real and unresolved by construction — these are DuPont carve-out years and Qnity has traded standalone only since November 1, 2025. This is a primary reason confidence is low, not medium: there is no through-cycle standalone record.
- **WIDE_SCENARIO_SPREAD** (super-bull IV is 5.5x super-bear IV): real — the outcome range is wide because OE is levered to the semi cycle and to capex normalization. Confidence is capped at low in judgment (engine cap would be medium under this flag in any case), and the verdict is sized to the conservative end.
- **HIGH_NET_DEBT** (net debt is 4.1x normalized OE on the engine's reported basis): folded explicitly into the verdict — net debt latest $3,209,000,000 against TTM OE total $788,000,000 means a demand downturn hits equity OE fast, and research puts total debt at $4.0B with roughly $250M of expected 2026 interest. This is why the bear/super-bear weights (35% combined) were not cut despite the guidance raises, and why no tier upgrade is defensible on leverage grounds.

## My thoughts / overlay
- The method range is narrow on tier, wide on value: the preliminary default run (median base $4.049665711556829, default growth) and this final run (TTM base $3.747028055159296, growth recalibrated up to current prints) both land in Tier D. Even the super-bull scenario — 27.01% growth start, 1.25x OE multiplier — returns only 14.29% IRR at $121.8685, below the 15% hurdle. A buyer at this price needs more than the super-bull case as modeled.
- Quality is not the problem: a real franchise, guided sales acceleration, small SBC load, and two OE definitions that agree. Price is the problem: OE yield 3.07% on the TTM base at $121.8685 leaves no margin of safety against cyclicality or the levered balance sheet.
- Price that clears 15%: the weighted IV@15% is $58.18 — that is the hurdle-clearing price on the weighted numbers, roughly half the current price, before any additional margin of safety. With a wide spread and thin history, a conservative buyer would demand a price below $58.18, not at it.
- Risks to this verdict (upside): capex normalization from the elevated TTM $344,000,000 toward a lower run rate would lift OE/share mechanically; sustained +20%+ revenue growth with operating leverage would push realized OE above the base case. Both are in the bull/super-bull cases and still do not clear 15% at this price.

## Final verdict
- **Final tier: D** (weighted IRR 9.05% on the v5 final inputs; Tier D under both the preliminary median-base run and this TTM-base run)
- Confidence: **Low** (WIDE_SCENARIO_SPREAD 5.49x, THIN_HISTORY with only carve-out years, and a levered spin balance sheet)
- One-liner: Good semiconductor-materials franchise, moat 6/10 — does not clear 15% at $121.87 (weighted IRR 9.05%, IV@15 $58.18); even the super-bull case is 14.29%; hurdle-clearing price is $58.18 on weighted numbers.
