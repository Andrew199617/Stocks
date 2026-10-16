# LYB — LyondellBasell Industries N.V.
v5 run, 2026-10-16. Market cap $20.185B at $62.67 (nasdaq_quote_api) — in scope under $40B. Sector: Materials / petrochemicals.

All figures below are copied from dcf_numbers.json, financials_history.csv, ttm.py output (ttm.json), or the company's Q2 2026 earnings release as returned in search results — none are recomputed.

## What it is
One of the world's largest producers of olefins and polyolefins (polyethylene, polypropylene), plus Intermediates & Derivatives (propylene oxide, oxyfuels), Advanced Polymer Solutions, and a Technology licensing/catalyst business. Vertically integrated, with its lowest-cost capacity on the U.S. Gulf Coast using natural-gas-liquids feedstock, versus naphtha-based capacity in Europe/Asia. It exited refining (Houston refinery, now in discontinued operations) and in Q2 2026 completed the divestiture of four European assets; the U.S. specialty powders business was sold in September 2025. Management's Cash Improvement Plan targets a $500M incremental cash improvement by end-2026 (company release, Q2 2026).

## Owner's earnings
From financials_history.csv (SEC EDGAR 10-Ks):
- FY2025: revenue $30,153M; net income -$738M; operating cash flow $2,262M; capex $1,878M; D&A $1,390M; SBC $91M.
- **Conservative owner's earnings (OCF − capex − SBC): FY2025 $293M = $0.91/share** (base_oe_latest_per_share); FY2024 $1,889M ($5.83/share is the 3-yr median — see base below); FY2023 $3,320M.
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): FY2025 $152M — same trough ballpark as the conservative figure.
- OE positive 5 of the last 5 fiscal years (oe_positive_years_of_last_5: 5/5), but the range is extreme: the 2025 trough OE/share of $0.91 sits far below the earlier years in the filed history — this is a deep cyclical trough, not a stable earnings stream.
- Balance sheet: the engine reports net_debt_latest as null (the debt_current tag is absent in the filed history), so no net-debt figure is quoted here. Filed FY2025 cash was $3,443M and long-term debt $15,833M (financials_history.csv); the Q2 2026 release reported $2.6B cash and $7.1B available liquidity at quarter-end. The dividend is a real cash claim on a trough business — FY2025 dividends paid were $1,764M per the earnings release — well above FY2025 conservative OE.

**Base used = normalized median of the last 3 FY OE/share: $5.83/share** (base_source: median_of_last_3_fy_oe_per_share). Rationale in FLAGS (BASE_DIVERGENCE / STALE_FY): the latest FY is an impairment-and-trough year, and the TTM pin from ttm.py is unusable this run because its share-count leg is broken (below).

**ttm.py output (quoted, not used as the base):**
- OCF: FY $2,262,000,000 (2025-01-01 to 2025-12-31) − prior YTD -$228,000,000 (2025-01-01 to 2025-06-30) + current YTD $483,000,000 (2026-01-01 to 2026-06-30) = **TTM $2,973,000,000**
- Capex: FY $1,878,000,000 − prior YTD $1,022,000,000 + current YTD $539,000,000 = **TTM $1,395,000,000**
- SBC: FY $91,000,000 − prior YTD $55,000,000 + current YTD $66,000,000 = **TTM $102,000,000**
- TTM OE total: **$1,476,000,000**
- Shares leg is broken: ttm.json's shares_diluted inputs are a FY period of 2011-01-01 to 2011-12-31 and a current-YTD period of 2012-01-01 to 2012-03-31, giving ttm_shares_diluted 575,000,000 and ttm_oe_per_share $2.57. That share count is not the company's — the engine reports shares_diluted_latest 322,084,769 and the Q2 2026 release reports a weighted diluted count of 323M. The $2.57 TTM per-share figure is therefore rejected and `--ttm` was NOT passed in the final run; the median base is used instead, with the reason stated here as required.

## Moat: 4/10 — weak-to-moderate, mostly cost position, no pricing power
Justification: Scale and a U.S. Gulf Coast NGL cost advantage are real but are commodity cost-curve positions, not franchises: the products are undifferentiated, prices are set by global spreads, and the cost edge depends on the oil-to-gas spread and on competitors' capacity decisions (notably China's).
- FOR: U.S. Gulf Coast ethane/NGL feedstock cost advantage vs naphtha-based European/Asian crackers; global scale and vertical integration from olefins through polymers; Technology segment licensing and catalyst sales (a genuinely differentiated, higher-margin niche); Advanced Polymer Solutions specialty compounding adds some non-commodity mix; demonstrated cash conversion and cost-cutting (Cash Improvement Plan) through the trough.
- AGAINST: Commodity products with no pricing power — margins are polyethylene/polypropylene spreads set by the market; Chinese capacity additions have turned a former export market into a self-sufficient competitor and depressed global margins; European naphtha-based footprint is structurally high-cost (being exited at a loss — Q2 2026 included a $734M loss on the European asset sales per the release summary); the NGL advantage narrows whenever oil falls relative to gas; long-term plastics-demand regulation (single-use bans, recycled-content rules) caps terminal volume growth.
- A 4 gives CAP = 7.2 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 7.2 years, 15-year projection.

## DCF — v5 final run (2026-10-16)
Engine blended growth g_blend is -12.73% and g_base is floored at -5.00% (growth_components: rev CAGR 5y +2.24%, rev CAGR 3y -15.76%, latest rev YoY -9.71%, OE/share CAGR 2y -70.16% — the last two straddle the basis break and the trough, see FLAGS). Scenario starts use the default offsets (-12/-5/0/+5/+12pp) against that floored base, with the engine's growth-start floor clipping the two bear cases at -10%. Probabilities were shifted bear-ward from the 10/25/30/25/10 defaults to 15/30/30/15/10 per the OE_VOLATILE instruction (widen bear weight) and the trough evidence; OE multipliers are the defaults 0.75/0.90/1.00/1.10/1.25. Price $62.67.

Sanity check vs recent prints: the starts are growth on the *normalized* $5.83 base, not on the $0.91 trough, so they are not comparable to trough-recovery percentages. Q2 2026 printed sales of $9,177M (+19.8% YoY per the release coverage), net income $559M and adjusted EBITDA of $2.1B excluding identified items — a strong quarter helped by Middle East supply disruption tightening polyethylene markets. That supports the bull cases existing, but a disruption-driven quarter does not justify raising the normalized-base super-bull start above +7%: mid-cycle OE/share has not printed above the $5.83 median in the recent history, and the FY2025 revenue print was -9.71% YoY. No scenario start was raised above the engine defaults, for that written reason.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | -10.0% | 0.75 | China overcapacity persists, spreads stay at trough, Europe drag continues | $22.00 | 6.47% |
| Bear | 30% | -10.0% | 0.90 | Slow, shallow recovery; normalized OE not regained | $26.40 | 7.32% |
| Base | 30% | -5.0% | 1.00 | Gradual mid-cycle normalization on the median base, faded over CAP 7.2y | $35.73 | 9.38% |
| Bull | 15% | 0.0% | 1.10 | Q2 2026-style tight markets persist; cost plan delivers | $47.77 | 11.97% |
| Super bull | 10% | +7.0% | 1.25 | Full cyclical upswing on a leaner, Americas-weighted portfolio | $71.00 | 16.60% |

- **Probability-weighted: IV@15% $36.20, IV@12% $46.99, IV@10% $58.92, weighted IRR 9.53%, base-case IRR 9.38%**
- **Tier by numbers: D.** Diagnostics (dcf_numbers.json): OE yield 9.31%, terminal value 16.56% of IV@15%, scenario spread 3.23x, 9.49 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (latest FY ended 9.49 months ago): ttm.py was run and its full inputs are quoted above. Its OCF/capex/SBC legs show a TTM OE total of $1,476,000,000 — above the FY2025 trough total of $293,000,000, consistent with the Q2 2026 recovery — but its share-count leg matched 2011/2012 periods (575,000,000 shares), so its per-share output is invalid and no TTM pin was used. The median base is used instead, with this reason stated. Post-FY evidence (Q2 2026: net income $559M, sales $9,177M, operating cash flow $752M in the quarter, per the company release) is reflected in the scenario weights, not in a hand-built base.
- **BASE_DIVERGENCE** (latest FY OE/share $0.91 vs 3-yr median $5.83): the latest FY is the distorted one — FY2025 absorbed $1,251M of non-cash asset write-downs (FY2025 earnings reconciliation) and trough spreads, driving net income to -$738M while OCF held at $2,262M. The median ($5.83, the FY2024 year of the last three) is the least-distorted normalized base available from this run's outputs and is used; the trough year is represented through the bear/super-bear weights (45% combined) rather than as the base.
- **NI_OCF_DIVERGENCE** (2023, 2024, 2025): identified — primarily non-cash items. FY2025: impairments of $1,251M (including Q3 2025 goodwill and asset write-downs in the O&P-EAI and APS segments) sit in net income but not in OCF; D&A of $1,390M (FY2025), $1,522M (FY2024) and $1,534M (FY2023) per financials_history.csv explains most of the remaining NI-to-OCF gap in each flagged year. The OE base is built from OCF, so the divergence does not contaminate it; it does confirm the earnings line is a poor guide for this company right now.
- **BASIS_BREAK_SUSPECT** (>60% revenue jump/drop in the last 5 yrs): two distinct breaks, neither trusted blindly. (1) The 2020→2021 revenue step in the filed history ($26,995M → $46,173M) is the post-COVID price/volume spike, not M&A. (2) The 2022→2023 step down ($50,451M → $33,336M in the filed history) reflects the history being presented on a continuing-operations basis after the refining exit (discontinued operations), which is why the 2023-25 revenue figures (~$30-33B) match the sum of the reported quarters while 2021-22 are total-company as filed. Consequence: all CAGRs straddling either break (rev CAGR 3y -15.76%, OE/share CAGR 2y -70.16%) were treated as artifacts; scenario starts were anchored on the normalized base with default offsets instead of recalibrated off those CAGRs.
- **OE_VOLATILE** (OE/share range >3x over 5 yrs): real and structural — this is a spread-driven commodity business at a cyclical trough. Handled by the normalized median base plus bear-weighted probabilities (super bear 15% + bear 30%) and by capping confidence at low.

## My thoughts / overlay
- The honest headline is the method range: on the normalized median base the weighted result is Tier D (9.53%); on the trough FY2025 base ($0.91/share) it would be far below D territory, and only the 10%-weighted super-bull scenario on its own (IRR 16.60%, IV@15% $71.00) clears the 15% hurdle. No defensible base from this run's outputs clears 15% at $62.67 — the range is D, and the verdict is sized accordingly.
- Quality is mixed, not broken: OE was positive in all of the last 5 years, cash conversion through the trough was real (FY2025 OCF $2,262M against a net loss), SBC is trivial ($91M FY2025), and the share count is roughly flat (share CAGR -0.37%/yr). Against that: capex of $1,878M against D&A of $1,390M in FY2025 means the conservative OE already charges full capex, the dividend ($1,764M paid in FY2025) is not covered by trough OE, and the European exit is being executed at realized losses.
- Q2 2026 shows operating leverage to any spread recovery — that is the bull case, and it is a market call on polyethylene spreads and Chinese capacity, not a company-specific growth story the DCF can underwrite at a normalized base.
- Margin of safety: the weighted IV@15% is $36.20 vs the $62.67 price (upside_at_15: -42.23%). The price that clears 15% on the weighted path is ~$36; even the bull scenario's IV@15% ($47.77) sits below the current price. A buyer at $62.67 is paying for the super-bull case at a 10% weight.

## Final verdict
- **Final tier: D** (weighted IRR 9.53% on the normalized median base; no tier override)
- Confidence: **Low** (cyclical trough, base divergence resolved only to a median, TTM pin unusable this run due to ttm.py's share-leg mismatch, scenario spread 3.23x)
- One-liner: Commodity petrochemical leader, moat 4/10 — does not clear 15% at $62.67 (weighted IRR 9.5%, IV@15 $36.20); it would need ~$36 to clear 15% on the weighted path.
