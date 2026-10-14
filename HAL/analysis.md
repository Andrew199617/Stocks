# HAL — Halliburton Company
v5 run, 2026-10-14. Market cap $28.021B at $32.85 (nasdaq_quote_api) — in scope under $40B. All figures below are copied from dcf_numbers.json, ttm.json, financials_history.csv, or cited search results — none are recomputed.

## What it is
One of the world's largest oilfield-services companies — the Big 3 with SLB and Baker Hughes — providing drilling, evaluation, completion and production services to oil and gas producers. Two segments (FY2025 revenue, Q4 2025 release): Completion and Production $12,782M and Drilling and Evaluation $9,402M, on total revenue of $22,184M. Halliburton is the North American completions / pressure-pumping leader, with international and offshore work as the longer-cycle cushion. Q2 2026 (latest quarter): revenue $5.7B, up 3.7% year over year, reported net income $534M / $0.64 diluted, adjusted net income $461M / $0.55.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $2,926,000,000; capex $1,254,000,000 (PaymentsToAcquireProductiveAssets); SBC $213,000,000 — by filing override, see OVERRIDE below.
- **Conservative owner's earnings FY2025: $1,459,000,000 = $1.71/share** (dcf_numbers.json base_oe_latest_per_share $1.7104)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $1,774,000,000 — above the conservative figure, mainly because FY2025 net income carries the impairment charges discussed under NI_OCF_DIVERGENCE; the OCF-based conservative figure is the cleaner base series.
- OE positive 5 of the last 5 fiscal years. Net debt $4,952,000,000 (dcf_numbers.json net_debt_latest) — see HIGH_NET_DEBT.
- Revenue fell -3.31% in FY2025 (growth_components rev_yoy_latest) after a strong 2022-23 upcycle; OE/share CAGR 2y is -9.07%.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $2,926,000,000 − prior YTD (H1 2025) $1,273,000,000 + current YTD (H1 2026) $1,097,000,000 = **TTM $2,750,000,000**
- Capex: FY $1,254,000,000 − prior YTD $656,000,000 + current YTD $427,000,000 = **TTM $1,025,000,000**
- SBC: **TTM $213,000,000**, all three legs filled by the override (see OVERRIDE)
- Shares (current-YTD weighted diluted): **838,000,000**
- **TTM OE total $1,512,000,000 → base OE/share $1.8043** (base_source: ttm_json)
- The engine's normalized base (median of last 3 FY OE/share) is $2.0687/sh — higher than both the latest FY ($1.7104) and the TTM figure, because it is anchored on the stronger 2023-24 upcycle years. The TTM base was used instead: it is the most current filing-derived figure and the more conservative of the two. The preliminary median-base run (same probabilities) gave weighted IRR 9.31% and IV@15% $17.74 — Tier D on either base, so the choice does not drive the verdict.

## OVERRIDE — SBC (filing, bounded authority)
- **The gap:** the preliminary engine run exited 4 with `DATA_GAP:sbc` — Halliburton files no SBC under the engine's tags (ShareBasedCompensation / AllocatedShareBasedCompensationExpense) for FY2023, 2024 or 2025; EDGAR companyfacts carries ShareBasedCompensation only through 2014.
- **The decision (worker, under the 2026-10-14 bounded filing authority):** judgment.json carries `sbc_override = {value: 213000000, kind: "filing", source: "Form 10-K for fiscal year ended December 31, 2025 (filed 2026-02-06, accession 0000045012-26-000015), Note 14 Stock-based Compensation table: stock-based compensation cost $213 million for 2025, $223 million for 2024 and $219 million for 2023. EDGAR companyfacts carries ShareBasedCompensation only through 2014, so the engine found no FY SBC for 2023-2025.", reason: "DATA_GAP:sbc — SBC missing for fiscal years 2023, 2024, 2025 of the last 3 under the engine's tags. The filer's own reported FY2025 stock-based compensation cost from its 10-K Note 14 fills the gap; the engine applies this single value to every missing period. The true per-year series in the same table is $219M (FY2023) / $223M (FY2024) / $213M (FY2025), so applying $213M to all three years is within $10M of the true figure in each year and is immaterial to the median base (under $0.02/share in the median year)."}`. The engine's override check records it as **in band** (value $213,000,000 vs last filed value $298,000,000, out_of_band: false) — no ack_reason needed.
- **How it was applied:** the engine filled every missing annual period (2016-2025, sbc_tag = "OVERRIDE" in financials_history.csv; filed values are never replaced — there simply are none after 2014); ttm.py prorated the same value across its three legs, leaving TTM SBC at exactly $213,000,000.
- **Measured impact (dcf_numbers.json override_impact):** on the engine-native base, zero-fill $2.3049/sh → $2.0687/sh normalized (the zero-fill baseline deducted no SBC at all, so it was never a real candidate base). **Measured impact on the TTM base actually used (key_numbers.md, same final configuration, overrides toggled off): base OE/share $2.06 (no override) → $1.80 (with override), -12.35% · weighted IRR 9.28% → 8.45% (-0.83pp).** The override is also the only reason a tier exists at all — without it the run stays DATA_GAP-blocked (key_numbers.md: "Unblocks tier: YES").

## Moat: 5/10 — moderate / narrow
Justification: Big-3 oligopoly scale as the #2 global oilfield servicer and North American completions leader, proprietary drilling/fracturing/digital technology and integrated well delivery that creates real switching friction, plus a global footprint that diversifies shale exposure — but demand is set by the commodity cycle (net losses in 2016, 2019, 2020), pricing power erodes when pressure pumping is oversupplied, consolidated E&P customers bargain hard, work is re-won project by project, and SLB/Baker Hughes contest every program.
- FOR: Big-3 oligopoly scale — #2 global oilfield servicer, leader in North American completions and pressure pumping; proprietary technology (LOGIX autonomous drilling, Zeus electric fracturing, Landmark / DecisionSpace digital platform); integrated well delivery across drilling, evaluation, completion and production creates switching friction once embedded; global footprint diversifies North America shale exposure with longer-cycle international and offshore work; through-cycle cash generation — owner's earnings positive 5 of the last 5 fiscal years, buybacks shrinking the count 2.1%/yr.
- AGAINST: commodity cycle rules demand — customers cut capex fast when oil falls, and HAL printed net losses in 2016, 2019 and 2020; pricing power erodes in oversupplied North American pressure pumping and E&P consolidation strengthens customer bargaining power; SLB and Baker Hughes contest the same programs with comparable technology; work is re-won project by project — no long-term lock-in beyond current integrated contracts; long-term energy-transition / oil-demand risk caps the terminal story.
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — v5 final run (2026-10-14)
Engine blended growth: g_blend -0.15% (rev CAGR 5y 8.96%, rev CAGR 3y 3.01%, latest rev YoY -3.31%, OE/share CAGR 2y -9.07%), plus the +2.06pp buyback share-count adjustment = **g_base 1.91%**. Default probabilities 10/25/30/25/10, default offsets -12/-5/0/+5/+12pp and OE multipliers 0.75/0.90/1.00/1.10/1.25 were kept — the evidence (a soft FY2025, a stabilizing H1 2026) does not justify skewing them. Price $32.85.

**Sanity check vs actual prints:** the base start (1.91%) sits below Q2 2026's +3.7% revenue YoY print — written reason: Q2 is a single quarter off a soft comparison, while the full-year prints the blend is built on are negative (FY2025 revenue -3.31%, OE/share CAGR 2y -9.07%) and TTM OCF through Q2 2026 ($2,750M) is still below FY2025 ($2,926M). The bull (6.91%) and super-bull (13.91%) starts both sit above every recent print, so no scenario is silently capped below observed reality; the super-bear start is floored at -10.00% by the engine.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -10.00% | 0.75 | Oil downturn; North America completions activity and pricing collapse | $6.57 | 4.62% |
| Bear | 25% | -3.09% | 0.90 | FY2025 softness persists; oversupplied pressure pumping, flat international | $10.54 | 6.30% |
| Base | 30% | 1.91% | 1.00 | Stabilization at current activity; buyback tailwind offsets flat demand | $14.43 | 7.97% |
| Bull | 25% | 6.91% | 1.10 | Activity recovery plus international / integrated-contract growth (e.g. Aramco, Eni awards) | $19.54 | 10.09% |
| Super bull | 10% | 13.91% | 1.25 | Full upcycle re-run of 2022-23 with pricing power restored | $29.61 | 13.88% |

- **Probability-weighted: IV@15% $15.47 (-52.91% vs price), IV@12% $20.45, IV@10% $25.99, weighted IRR 8.45%, base-case IRR 7.97%**
- **Tier by numbers: D.** Diagnostics (dcf_numbers.json): OE yield 5.49%, terminal value 18.24% of IV@15%, scenario spread 4.51x, net debt 3.22x normalized OE, 9.4 months since FY end.

## Flags — every fragility flag resolved
- **DATA_GAP:sbc** (preliminary run): resolved by the filing override — see OVERRIDE. True per-year SBC from the same 10-K table is $219M / $223M / $213M for 2023 / 2024 / 2025, so the single-value fill is within $10M of truth in each gated year.
- **STALE_FY** (latest FY ended 9.4 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, with all inputs quoted above.
- **NI_OCF_DIVERGENCE** (2025): identified — FY2025 net income is $1,283M against OCF of $2,926M because net income carries $831M of pre-tax impairments and other charges in FY2025 (vs $116M in FY2024, per the Q4 2025 release; $392M of it in Q3 alone, plus a $125M Q3 tax valuation allowance against US foreign tax credits), while OCF adds back those non-cash charges and $1,136M of D&A (financials_history.csv). The divergence is an impairment year, not a cash-quality problem; the OCF-based conservative OE series is used throughout, so it does not contaminate the base — if anything FY2025 OE is understated to the extent the impairments signal permanently impaired capacity, which the bear-side multipliers cover.
- **BUYBACK_TAILWIND** (share count shrinking 2.1%/yr): already credited via the +2.06pp growth adjustment in the blend; not double-counted in the verdict. Q2 2026 buybacks continued ($200M in the quarter per the Q2 release summary).
- **OVERRIDE_APPLIED:sbc**: see OVERRIDE — gap, decision, band check and measured impact are all recorded in fields (judgment.json, dcf_numbers.json overrides_applied / override_impact, overrides_registry.json), not just here.
- **WIDE_SCENARIO_SPREAD** (super-bull IV 4.51x super-bear IV): real — this is a commodity-cyclical whose outcome range IS wide. Confidence is held at medium and the verdict is sized to the conservative end.
- **HIGH_NET_DEBT** (net debt 3.22x normalized OE): net debt is $4,952M. Manageable in an upcycle, but it is exactly the leverage that makes OE vanish fast in a downturn — the bear and super-bear cases carry 35% combined probability with 0.90 / 0.75 OE multipliers for this reason, and the verdict does not lean on the bull cases.

## My thoughts / overlay
- The method range is narrow for once: TTM base ($1.8043) → weighted IRR 8.45%; normalized median base ($2.0687) → 9.31% on the preliminary run. Both are Tier D, and even the super-bull scenario (13.88% IRR) does not clear the 15% hurdle at $32.85 — the price already pays for a recovery that has not yet printed in owner's earnings: TTM OCF is still below FY2025, and FY2025 OE/share is below both 2023 and 2024.
- Quality is not the debate: positive OE in 5 of 5 years, moderate SBC ($213M against OCF of $2,926M in FY2025), real buybacks, and a Big-3 position. The debate is purely price vs cycle: at an OE yield of 5.49% on the TTM base, there is no margin of safety against the bear IV@15% of $10.54.
- The price that clears 15% on the weighted case is the weighted IV@15% itself: **$15.47**. A buyer wanting a margin of safety against the bear case would be looking nearer the bear IV@15% of $10.54 — both are far below the current $32.85.

## Final verdict
- **Final tier: D** (weighted IRR 8.45% on the v5 final inputs; Tier D also on the normalized median base at 9.31%)
- Confidence: **Medium** (high on the filing-derived TTM base and the SBC override, which is sourced to the dollar from Note 14; the scenario spread is 4.51x, so no single growth path deserves high confidence)
- One-liner: Cyclical Big-3 oilfield servicer, moat 5/10 — at $32.85 on TTM owner's earnings of $1.80/share (OE yield 5.49%) it does not clear 15%: weighted IRR 8.45%, weighted IV@15% $15.47; it clears the 15% hurdle only at ~$15.47, and even the super-bull case only returns 13.88%.
