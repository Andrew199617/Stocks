# FTI — TechnipFMC plc
v5 run, 2026-10-14. In scope (market cap $29.169B at $69.50, nasdaq_quote_api).

All figures below are copied from dcf_numbers.json, financials_history.csv, or the cited company releases — none are recomputed.

## What it is
Oilfield equipment and services company built around Subsea: subsea production systems, integrated iEPCI project execution, Subsea Services for the installed base, plus a smaller Surface Technologies segment. Revenue is operator offshore capex converted through a large project backlog — FY2025 revenue $9,932.6M, with backlog of $16.6B at FY2025 year-end per the company's Q4 2025 release.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $1,764,600,000; capex $317,200,000; SBC $61,900,000 (AllocatedShareBasedCompensationExpense tag; always a real cost).
- **Conservative owner's earnings FY2025: $1,385,500,000 = $3.30/share** (base_oe_latest_per_share in dcf_numbers.json)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $1,178,600,000 — same ballpark, below the conservative figure.
- OE positive 5 of the last 5 fiscal years, but the longer history is deeply cyclical: net income was negative in 2018, 2019 and 2020 (financials_history.csv) during the offshore downturn.
- Balance sheet: net debt −$601,900,000, i.e. net cash (dcf_numbers.json); net debt is −1.02x normalized OE (diagnostics). A cushion, not a thesis at this price.
- **Base used = normalized median of last 3 FY OE/share: $1.41/share** (base_source: median_of_last_3_fy_oe_per_share). The TTM base that would normally supersede it could not be built — see STALE_FY below. The median is the middle of a steep recovery (conservative OE totals from financials_history.csv: $426.9M in 2023, $621.1M in 2024, $1,385.5M in 2025), so it understates current earnings power; the latest FY likely overstates run-rate (see BASE_DIVERGENCE). The standardized median is retained per the v5 fallback rule, confidence is set to low, and the method range is stated in Thoughts.

## Moat: 5/10 — moderate/narrow
Justification: a real technology and integration position in subsea (iEPCI, Subsea 2.0, direct-award flow, services installed base) that has demonstrably expanded margins this cycle, but no protection against the operator-capex cycle itself — earnings collapsed in the last downturn — and credible integrated competitors (SLB's OneSubsea, Baker Hughes) contest every award.
- FOR: iEPCI integrated execution model and Subsea 2.0 configurable technology; direct awards, iEPCI and Subsea Services accounted for more than 80% of 2025 Subsea inbound per the company's Q4 2025 release — relationship/ incumbency flow, not open-bid commodity work; large backlog ($15.9B Subsea at FY2025 year-end per the same release) and a services tail on the installed base; proven margin expansion (adjusted EBITDA margin 18.4% in FY2025 per the release; Subsea adjusted EBITDA margin 23.2% in Q2 2026 per the Q2 2026 release).
- AGAINST: earnings are hostage to offshore operator capex — net income was negative in 2018–2020 (financials_history.csv); integrated competition from SLB OneSubsea and Baker Hughes; backlog was essentially flat year over year at Q2 2026 (Subsea backlog $15,833.2M vs $15,810.0M a year earlier, Q2 2026 release) — orders are replacing executed work, not yet compounding it; Surface Technologies is shrinking (revenue down 13.3% year over year in Q2 2026 per the release coverage); long-run energy-transition shrinkage of the offshore addressable market; project execution and geopolitics across volatile regions.
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — v5 final run (2026-10-14)
Engine blended growth is 11.68%; with the buyback adjustment (+2.26pp for a share count shrinking 2.26%/yr) g_base is 13.94%. Sanity check against actual prints: FY2025 revenue grew 9.35% and Q2 2026 revenue grew 9.0% year over year (Q2 2026 release) — the OE growth starts sit above revenue growth because they embed continued margin expansion (2026 Subsea adjusted EBITDA margin guided to 21–22% per company guidance reported with Q2 2026) plus buybacks, not revenue acceleration. The 86.94% OE/share CAGR (2y) in the blend components is a trough-base artifact and was not used as a scenario anchor. Probabilities were skewed bearish vs the 10/25/30/25/10 defaults (15/30/30/17/8) per the OE_VOLATILE flag's instruction to widen bear weight in a cyclical. Offsets and multipliers are the defaults. Price $69.50.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | 1.9% | 0.75 | Offshore sanctioning stalls; margins give back the cycle gains | $8.47 | 4.01% |
| Bear | 30% | 8.9% | 0.90 | Backlog executes but orders only replace it; Surface drag persists | $13.59 | 5.11% |
| Base | 30% | 13.9% | 1.00 | Margin expansion + buybacks carry OE, fading over the CAP | $18.54 | 6.17% |
| Bull | 17% | 18.9% | 1.10 | Greenfield awards step up in 2027; margins hold at guided levels | $24.98 | 7.50% |
| Super bull | 8% | 25.9% | 1.25 | Durable supercycle: backlog compounds and services mix lifts OE | $37.56 | 9.91% |

- **Probability-weighted: IV@15% $18.16 (−73.87% vs price), IV@12% $24.63, IV@10% $31.91, weighted IRR 6.12%, base-case IRR 6.17%**
- **Tier by numbers: D.** Diagnostics (dcf_numbers.json): OE yield 2.03%, terminal value 20.80% of IV@15%, scenario spread 4.43x, net debt −1.02x normalized OE, 9.43 months since FY end.
- Even the super-bull scenario (8% weight) produces an IV@15% of $37.56, roughly half the $69.50 price — on the normalized base, no scenario clears the 15% hurdle at this price.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.43 months ago): ttm.py was run and failed — it exited non-zero with "sbc: no post-FY YTD fact (no 10-Q since the 2025-12-31 fiscal year end)", so no ttm.json base exists. Per the v5 fallback, the engine's median base ($1.41/share) is used and the reason is stated here. Partial mitigation from reported quarters: Q2 2026 revenue was $2.76B, up 9.0% year over year, with net income of $362.7M and total backlog of $16.44B (Q2 2026 release) — current trading is well above the median-base years, which is why confidence is low rather than the tier being treated as precise.
- **BASE_DIVERGENCE** (latest FY $3.30 vs 3-yr median $1.41): both are distorted in opposite directions. The median is dragged by the recovery years 2023–2024, when the backlog built after the downturn had not yet converted to high-margin revenue (conservative OE $426.9M in 2023, $621.1M in 2024, financials_history.csv). The latest FY is flattered the other way: FY2025 operating cash flow of $1,764.6M jumped far faster than revenue (+9.35%), consistent with favorable working-capital/project timing on large backlog execution that may not repeat. With the TTM code path unavailable (above), the standardized median stands; the divergence is the main reason confidence is low and the method range is flagged in Thoughts.
- **NI_OCF_DIVERGENCE** (2023, 2025): in 2023 net income was $56.2M against operating income of $658.2M and OCF of $693.0M (financials_history.csv) — below-the-operating-line charges (interest, tax and other non-operating items) consumed the operating profit while OCF added back D&A of $377.8M. In 2025 net income was $963.9M vs OCF of $1,764.6M, with tax expense of $302.9M and D&A of $441.8M (financials_history.csv) explaining much of the gap. The base uses the OCF-based conservative OE throughout, so the divergence does not contaminate the base; it does reinforce that FY2025 OCF had tailwinds.
- **OE_VOLATILE** (OE/share range >3x over 5 years): real cyclicality, not an artifact — handled by the normalized median base and by skewing probabilities to 45% bear-or-worse (15/30) vs the 35% default.
- **BUYBACK_TAILWIND** (share count −2.26%/yr): already credited via the +2.26pp growth adjustment in g_base; not double-counted in the verdict. Buybacks remained heavy in 2026 ($420.1M of repurchases in Q2 2026 per the Q2 2026 release).
- **WIDE_SCENARIO_SPREAD** (4.43x): real — the outcome range for a cyclical at a peak-multiple price is wide. Confidence is set to low, and the verdict is sized to the conservative end.

## My thoughts / overlay
- The honest headline is the base sensitivity: the standardized median base ($1.41/share) is a trough-weighted figure, and the latest FY ($3.30/share) is a peak-execution figure — defensible inputs span a wide range, and the stock's verdict depends on which end of the cycle you normalize to. What does not change across that range: at $69.50 the price already pays for the recovery. Even the final run's super-bull IV@15% ($37.56) sits far below the price, and the FY2025 earnings power would need to be both permanent and still growing for years to justify today's quote — that is a supercycle assumption, not a margin of safety.
- Quality is mid-tier: net cash balance sheet (−$601.9M net debt), SBC is small ($61.9M in FY2025), capex is modest ($317.2M), and the direct-award/iEPCI mix genuinely de-risks execution versus the last cycle. Against that, backlog was flat year over year at Q2 2026 and Surface is shrinking — the growth engine is one segment deep.
- Hurdle math on the final numbers: the weighted IV@15% is $18.16, so on the normalized base the stock clears a 15% hurdle only at or below $18.16 — and a buyer wanting a margin of safety against the bear cases ($13.59 / $8.47) would need to pay less than that. Anyone underwriting it higher is explicitly underwriting the latest-FY base as the new normal.

## Final verdict
- **Final tier: D** (weighted IRR 6.12% on the v5 final inputs; no scenario clears 15% at $69.50)
- Confidence: **Low** (TTM base unavailable, BASE_DIVERGENCE unresolved in the code outputs, 4.43x scenario spread, cyclical earnings)
- One-liner: Quality subsea franchise, moat 5/10, but at $69.50 the price pays for the recovery and more — weighted IRR 6.12%, weighted IV@15 $18.16 on the normalized base; clears 15% only at or below $18.16, and even the super-bull IV is $37.56.
