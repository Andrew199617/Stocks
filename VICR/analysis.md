# VICR — Vicor Corporation
Engine 5.4.0 run, 2026-10-18. Price $191.50 (nasdaq_quote_api), market cap est. $8.70B — in scope (<$40B). All figures below are copied from dcf_numbers.json, ttm.json, financials_history.csv, or fundamentals.json — none are recomputed.

## What it is
Power-module maker (Andover, MA): Factorized Power Architecture / ChiP modules — Brick products (legacy DC-DC converters) and Advanced Products (high-density modules for high-performance computing). The current story is second-generation Vertical Power Delivery (VPD) for AI accelerators — feeding very high current at low voltage into the processor from below the board — plus a patent-licensing business enforced by ITC import bans (early 2025, against infringing modules/systems from Delta Electronics, Quanta and two Foxconn units). Management raised its long-term targets to $2.5B revenue at 70% gross margin / 40% operating margin (from $1B / 65%), and is adding fab capacity (second fab; New Hampshire sites bought). Q2 2026 (reported, pre-10-Q companyfacts): revenue $143.4M (+26.9% sequential), EPS $1.04, gross margin 58.0%, Advanced Products $94.2M = 65.7% of revenue, backlog $379.7M (+145% YoY). A second VPD patent license to an AI system maker was announced 2026-09-16.

## Owner's earnings
**FY2025 (10-K, financials_history.csv):** OCF $139,548,000; capex $20,318,000; SBC $16,787,000 (always a real cost).
- **Conservative OE FY2025: $102,443,000 = $2.25/share.** Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $123,728,000 — same ballpark.
- FY2025 is flattered: net income $118,556,000 exceeds operating income $81,828,000 on a **tax benefit of −$24,025,000** plus non-operating income, and the filer's total revenue of $452,701,000 (fundamentals.json) exceeds the engine's contract-revenue line of $407,701,000 by ~$45M of royalty/license and other revenue — settlement and licensing money from the patent campaign (~$300M expected from settlements through 2026 per company commentary; one-time in nature). Q2 2026 alone carried $15M of royalty income, guided unevenly ($5M in Q3, then $10M/quarter for four quarters).
- OE positive 3 of the last 5 fiscal years; the 5-year OE/share path is violently cyclical (FY2022 −$1.14, FY2023 $0.63, FY2024 $0.26, FY2025 $2.25).

**Base used = TTM owner's earnings through Q1 2026, from ttm.py (filing-direct):**
- OCF: FY $139,548,000 − prior YTD $20,128,000 + current YTD −$3,942,000 = **TTM $115,478,000**
- Capex: FY $20,318,000 − prior YTD $4,550,000 + current YTD $12,387,000 = **TTM $28,155,000**
- SBC: FY $16,787,000 − prior YTD $4,349,000 + current YTD $3,852,000 = **TTM $16,290,000**
- Shares (current-YTD weighted diluted): **47,254,000**
- **TTM OE total $71,033,000 → base OE/share $1.50** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $0.63/share and the latest FY is $2.25/share; the TTM base sits between them and is the least distorted of the three (see BASE_DIVERGENCE). Note the TTM window stops at Q1 2026 — the Q2 2026 10-Q (period 2026-06-30, filed 2026-07-29) is not yet in EDGAR companyfacts (fundamentals.json warning), so the strong Q2 print is in the growth scenarios, not the base.

## Moat: 5/10 — moderate/narrow, patent-led
Justification: a real, court-enforced patent estate on vertical power delivery and designed-in module positions, but a decade of volatile, mid-teens-at-best returns on capital says the franchise has never compounded like a wide moat.
- FOR: patent estate with teeth — ITC import bans already issued against Delta/Quanta/Foxconn units, and AI system makers are signing licenses (two in four months, incl. 2026-09-16) because supplier indemnification cannot overcome an import ban; design-in switching costs — power delivery is qualified into processor platforms and is painful to re-engineer; current-density lead in gen-2 VPD (3 A/mm² baseline at the lead customer, >4 targeted); gross margin expanding with mix (50.6% FY2023 → 51.2% FY2024 → 57.3% FY2025 → 58.0% Q2 2026, fundamentals.json / Q2 reporting).
- AGAINST: ROIC history is cyclical, not wide-moat — roic_proxy (fundamentals.json): 23.0% FY2021, 8.8% FY2022, 15.3% FY2023, **−0.3% FY2024**, 20.9% FY2025, with negative years in 2016–17; earnings were near zero for most of a decade before the AI/licensing inflection; customer concentration around a lead AI customer/hyperscaler engagements not yet ramped; deep-pocketed competition (Monolithic Power, Infineon, Delta, Navitas) working around the patents; a growing share of profit is license/settlement income, which decays unless the module business converts it; capacity-constrained (Andover fab near full; second fab is execution + capex risk).
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — final run (2026-10-18)
**Growth recalibration (written reason):** the engine's blended start is 9.65%, but its components are stale or artifactual — rev CAGR 5y 6.57% and 3y 0.71% predate the inflection, latest FY YoY is +13.55%, while the OE/share CAGR 2y of 89.55% is an artifact of the near-zero FY2024 base. The prints that mean something: Q1 2026 revenue +20% YoY, Q2 2026 +26.9% sequential with backlog +145% YoY, full-year 2026 guided above $600M against FY2025 total revenue of $452.7M. Scenario starts were therefore set via offsets (−0.0465 / +0.0535 / +0.2035 / +0.3235 / +0.4035 vs the 9.65% blend) to 5 / 15 / **30** / 42 / 50% (super bull at the 50% engine cap). Base start of 30% sits *below* the implied FY2026 revenue growth because the TTM base still contains settlement/licensing income that lapses. Multipliers adjusted to 0.60 / 0.85 / 1.00 / 1.10 / 1.25: the super-bear 0.60 (vs the 0.75 default) strips the one-time settlement/licensing layer out of the base. Probabilities 15/30/30/15/10 — bear-weighted for a stock up several hundred percent in a year on an unproven-at-scale ramp.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | 5.0% | 0.60 | Settlements lapse, VPD ramp slips or is designed around; OE falls back toward the core module business | $8.21 | 3.05% |
| Bear | 30% | 15.0% | 0.85 | Licensing decays, Advanced Products grows but at normal component economics | $17.54 | 3.81% |
| Base | 30% | 30.0% | 1.00 | FY2026 guide delivered; VPD ramps at the lead customer; royalties fade to a running stream | $37.59 | 5.53% |
| Bull | 15% | 42.0% | 1.10 | Hyperscaler + OEM ramps land; second fab on time; mix pushes GM toward the mid-60s | $65.63 | 7.74% |
| Super bull | 10% | 50.0% | 1.25 | A real path toward the $2.5B / 70% GM target emerges | $100.54 | 10.11% |

- **Probability-weighted: IV@15% $37.67 (−80.3% vs the $191.50 price), weighted IRR 5.60%, base-case IRR 5.53%**
- **Tier by numbers: D** (bear D, bull D — no band ambiguity). Diagnostics: OE yield 0.78%, terminal value 24.7% of IV@15%, scenario spread 12.25x, 9.6 months since FY end.
- Hurdle-clearing prices: clears 15% only at or below **$37.67**, 20% at $24.39, 25% at $17.44. Even the super-bull IV@15% ($100.54) is barely half the price — at $191.50 the market is pricing in execution *beyond* this model's super bull.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.6 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q1 2026, legs quoted above. Caveat recorded: the Q2 2026 10-Q is filed (2026-07-29) but not yet in EDGAR companyfacts, so no filing-direct TTM through Q2 exists yet; Q2's strength is carried in the scenario starts instead.
- **BASE_DIVERGENCE** (latest FY $2.25 vs 3-yr median $0.63): **both are distorted.** The FY2025 figure is inflated by settlement/licensing income and a −$24.0M tax benefit (NI $118.6M vs OI $81.8M); the median is dragged by trough years FY2023–24, before the AI inflection. The TTM base of $1.50/share is the defensible middle and is what the score uses.
- **NI_OCF_DIVERGENCE (2024)**: FY2024 net income was only $6,129,000 vs OCF $50,842,000. Resolution: operating income was −$1,310,000 — net income was depressed by the ITC patent-litigation spend running through SG&A — while OCF carries $18,626,000 of D&A and $15,302,000 of SBC as non-cash addbacks. It is a litigation-cost / addback story, not a cash-quality red flag, and the OCF-based OE series used throughout is unaffected by it.
- **DEBT_TAGS_BLANK**: balance sheet stated from the filing (financials_history.csv, FY2025): cash $402,805,000, total assets $785,831,000, total liabilities only $74,015,000, equity $711,557,000, operating lease liabilities $7,176,000, and no debt tags because there is essentially no debt — Vicor is debt-free with a large net cash position. The engine's null net debt is a tagging artifact, not unknown leverage.
- **OE_VOLATILE** (OE/share spans >3x over 5 years): real and structural — this is a cyclical component business now overlaid with lumpy license income. Handled by the TTM base, the 0.60 super-bear multiplier, and 45% combined weight on bear-or-worse.
- **IRR_AT_FLOOR** (preliminary run): with the normalized base the solver sat at the ~2.5% floor. On the final TTM base the flag clears (weighted IRR 5.60%), but the super-bear IRR of 3.05% still sits near the floor — read it as "at most ~3%", consistent with the verdict.
- **LOW_OE_YIELD** (0.78% on the TTM base): real — at $191.50 the valuation rests almost entirely on growth that has not yet been filed. This is the core of the D verdict.
- **WIDE_SCENARIO_SPREAD** (12.25x): real — outcomes genuinely range from "licensing annuity fades" to "power-delivery standard." Confidence is capped at low and the verdict is sized to the conservative end.

## My thoughts / method range
- The method range is narrower than usual and all of it is far below the price: normalized-median base (preliminary run) → weighted IV@15% $7.39, IRR 3.04%; TTM base with recalibrated growth (final) → $37.67, IRR 5.60%; super bull alone → $100.54. No defensible pass-1 method gets within half of $191.50.
- Quality is not the debate: debt-free, $402.8M cash, gross margin expanding on mix, backlog +145% YoY, and a patent estate competitors are paying to license. The debate is purely price — the stock has run several hundred percent in a year and now discounts a $2.5B-revenue, 70%-gross-margin future that management itself frames as a long-term target, not a guide.
- What would change the verdict: the Q2 2026 10-Q landing in companyfacts (a filing-direct TTM base including Q2), named hyperscaler VPD ramps converting backlog to revenue, and royalty streams proving recurring rather than settlement-driven. A re-score on the next filing is the right trigger, not a higher growth guess now.
- Risks to the *bear* sizing: licensing momentum is accelerating (second license in four months, Sept 2026), and scarcity value in AI power delivery has repeatedly outrun fundamentals models. That is a trading observation, not a DCF input.

## Final verdict
- **Final tier: D** (weighted IRR 5.60% on the final TTM-based run; tier by numbers D, bear D, bull D)
- Confidence: **Low** (12.25x scenario spread, 0.78% OE yield, TTM base missing the Q2 2026 quarter in companyfacts)
- One-liner: Real patent moat and an AI power ramp, moat 5/10 — but at $191.50 the price is beyond even the super-bull IV@15% of $100.54; weighted IRR 5.6%, and it clears 15% only below $37.67.
