# STLD — Steel Dynamics, Inc.
v5 run, 2026-10-14 (supersedes the v4 analysis of 2026-10-13; the v4 result was also Tier D — weighted IRR 5.3%, IV@15% $52.57 at $240.63 — and is summarized under Thoughts). Price $251.4915 (nasdaq_quote_api), market cap $37.322B (dcf_numbers.json) — in scope (<$40B).

All figures below are copied from dcf_numbers.json, ttm.json / ttm.py output, financials_history.csv, or key_numbers.md — none are recomputed. Quarterly figures are from the company's Q2 2026 results as reported in search coverage of the release.

## What it is
One of the largest US steel producers and metals recyclers (Fort Wayne, Indiana). Electric-arc-furnace (EAF) mini-mills melt scrap into flat-rolled and long-product steel; vertically integrated through OmniSource metals recycling (scrap supply), steel fabrication, and a new aluminum flat-rolled platform (Aluminum Dynamics, Columbus, Mississippi) still in ramp. End markets: non-residential construction, automotive, energy, manufacturing — currently boosted by infrastructure funding, reshoring, and Section 232 trade protection.

Latest earnings: Q2 2026 — net sales $6.1 billion (+33.4% YoY), net income $534 million / $3.69 diluted EPS (including a $16 million non-cash impairment for relocating the planned second aluminum recycled slab center to Columbus, Mississippi), operating income $700 million, adjusted EBITDA $921 million, record steel shipments of 3.7 million tons at an average steel price of $1,298/ton. Aluminum operations lost $33 million in the quarter, improving sequentially, with management expecting volume and profitability to improve in H2 2026 as the mill exits 2026 at at least 90% of capacity; the through-cycle aluminum EBITDA target management repeats is $650–$700 million. The company guided Q3 2026 earnings sharply higher sequentially on wider metal margins, record shipments, higher realized prices, and lower scrap costs, while metals recycling was expected to weaken. Share repurchases were $200 million in Q2 2026 ($315 million year-to-date) and total liquidity was $2.0 billion at 2026-06-30. Management cited a three-year after-tax return on invested capital of 13% in the Q2 release.

Red flags: (1) earnings are a steel-spread derivative — filed net income went $3,862,674,000 (2022) → $2,450,882,000 (2023) → $1,537,134,000 (2024) → $1,185,595,000 (2025), and the current surge is the same cycle in reverse; (2) the aluminum platform is unproven and still loss-making; (3) part of the current spread environment is trade policy, which a government can withdraw; (4) at $251.4915 the price has already capitalized the upcycle.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $1,449,534,000; capex $948,025,000; SBC $68,983,000.
- **Conservative owner's earnings FY2025: $432,526,000 = $2.91/share** (base_oe_latest_per_share in dcf_numbers.json)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $677,182,000 — above the conservative figure because FY2025 capex ($948,025,000) exceeded D&A ($551,390,000); the gap is the growth-capex window (capex was $1,657,905,000 in 2023 and $1,868,006,000 in 2024, building Sinton and Aluminum Dynamics).
- Conservative OE totals by year (financials_history.csv): 2021 $1,140,182,000; 2022 $3,492,261,000; 2023 $1,800,279,000; 2024 −$90,092,000; 2025 $432,526,000. OE positive 4 of the last 5 fiscal years. This is a cyclical in a heavy-investment phase, not a compounder.
- Net debt (dcf_numbers.json): $3,441,285,000.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $1,449,534,000 − prior YTD $454,214,000 + current YTD $576,252,000 = **TTM $1,571,572,000**
- Capex: FY $948,025,000 − prior YTD $593,837,000 + current YTD $261,821,000 = **TTM $616,009,000**
- SBC: FY $68,983,000 − prior YTD $31,103,000 + current YTD $31,613,000 = **TTM $69,493,000**
- Shares (current-YTD weighted diluted): **144,956,000**
- **TTM OE total $886,070,000 → base OE/share $6.11** (ttm.json: $6.112682469163056; base_source: ttm_json)
- The engine's normalized base (3-yr median) is $2.91/share — it is arithmetically identical to the latest year (median of 2023, 2024, 2025 per-share figures) and inherits the growth-capex distortion of the investment window, so the TTM base on post-construction capex is the run-rate the DCF projects from. The TTM choice is generous relative to the median — and the verdict does not depend on it (method range below).

## Moat: 5/10 — moderate, a real cost advantage inside a commodity business
Justification: a genuine lowest-quartile EAF cost structure, OmniSource scrap integration, a diversified value-added mix, and best-in-class through-cycle returns — against commodity price-taking, the same EAF model at larger scale at Nucor, no switching costs or pricing power, spreads partly underwritten by tariffs, and an unproven aluminum platform.
- FOR: Lowest-quartile EAF cost structure — variable scrap-based costs, flexes with demand; OmniSource vertical integration secures scrap supply and captures the recycling spread; 13% three-year after-tax ROIC (Q2 2026 release) — best-in-class through-cycle returns; diversified value-added mix: flat-rolled, long/rail, fabrication, ramping aluminum; a decade of buybacks — diluted shares 245,298,000 (2016) to 148,404,000 (2025) in the filed history.
- AGAINST: Commodity price-taker on the steel price and the scrap spread — no pricing power or switching costs; Nucor runs the same EAF model at larger scale — the cost edge is shared, not proprietary; earnings fell three straight years 2022–2025 as spreads compressed; current spreads partly underwritten by Section 232 tariffs — policy, not a company asset; aluminum platform still loss-making in ramp (Q2 2026 operating loss $33 million per company-results coverage).
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — v5 final run (2026-10-14)
Base OE $6.11/share (TTM, above). g_base 3.55% (blend −1.45% plus the +5pp buyback adjustment). Growth sanity check (mandatory): recent prints are FY2025 revenue +3.63% YoY and Q2 2026 revenue +33.4% YoY with EPS $3.69 vs $2.01 a year ago. The scenario starts below sit far below the Q2 print, with the written reason the rules require: that print is steel-price/spread expansion plus record volume — a cyclical margin event on a fixed asset base, not a compoundable growth rate. No steelmaker compounds owner's earnings at 33%. Probabilities were skewed bearish vs the 10/25/30/25/10 defaults to 15/30/30/20/5: OE_VOLATILE, a price that has already capitalized the upcycle, and an unproven aluminum ramp argue for more left-tail weight. Offsets and OE multipliers are the defaults (−12/−5/0/+5/+12pp; 0.75/0.90/1.00/1.10/1.25). Price $251.4915.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | -8.45% | 0.75 | Spreads compress hard; aluminum ramp stalls | $23.76 | 3.50% |
| Bear | 30% | -1.45% | 0.90 | Normal mid-cycle spread fade | $38.25 | 4.31% |
| Base | 30% | 3.55% | 1.00 | Through-cycle volume growth plus aluminum/Sinton ramp | $52.36 | 5.13% |
| Bull | 20% | 8.55% | 1.10 | Wide spreads persist; aluminum reaches profitable utilization | $70.85 | 6.21% |
| Super bull | 5% | 15.55% | 1.25 | Peak spreads persist and aluminum hits its through-cycle target early | $107.25 | 8.26% |

- **Probability-weighted: IV@15% $50.28 (−80.01% vs price), IV@12% $66.42, IV@10% $84.39, weighted IRR 5.04%, base-case IRR 5.13%**
- **Tier by numbers: D.** Diagnostics (dcf_numbers.json): OE yield 2.43%, terminal value 18.20% of IV@15%, scenario spread 4.51x, net debt 3.79x normalized OE, 9.43 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.43 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, quoted above with all four inputs (FY, prior YTD, current YTD for OCF/capex/SBC, and the share basis).
- **BUYBACK_TAILWIND** (share count shrinking 7.02%/yr): verified in the filed history — diluted shares fell from 245,298,000 (2016) to 148,404,000 (2025), and repurchases continued in 2026 ($200 million in Q2, $315 million year-to-date per company-results coverage). Already credited via the +5pp growth adjustment in g_base; not double-counted in the verdict.
- **BASIS_BREAK_SUSPECT** (>60% revenue move in the last 5 years): a price-cycle artifact, not a corporate event. Revenue jumped from $9,587,691,000 (2020) to $18,408,850,000 (2021) to $22,260,774,000 (2022) on the post-COVID steel-price spike, then fell to $18,795,316,000 (2023) — no divestiture, large M&A, or restatement explains it; Sinton was greenfield and aluminum is a new segment, not a basis change. Consequence: the 5-yr revenue CAGR (13.65%) and the OE/share CAGR 2y (−47.91%) are both unusable as growth inputs, which is why the sanity check above governs the scenario starts rather than the blend components.
- **OE_VOLATILE** (OE/share range >3x over 5 years): structural — spread cyclicality plus the 2023–25 growth-capex surge (conservative OE totals: $3,492,261,000 in 2022 → −$90,092,000 in 2024 → $432,526,000 in 2025). Handled by the TTM base on post-construction capex, wider bear/super-bear weight (45% combined), and the 0.75 super-bear OE multiplier.
- **WIDE_SCENARIO_SPREAD** (super-bull IV 4.51x super-bear IV): real — the spread is the steel cycle itself. Confidence is capped at medium. It does not create tier ambiguity here: even the super-bull IV@15% ($107.25) is less than half the $251.4915 price.
- **HIGH_NET_DEBT** (net debt 3.79x normalized OE on the final run; 7.96x on the preliminary median base): the multiple is inflated by the capex-depressed OE denominator. Net debt is $3,441,285,000 and liquidity was $2.0 billion at 2026-06-30 — not a solvency concern. It still matters in the bear cases: conservative OE went negative in 2024, and a levered equity claim on a flow that can vanish for a year deserves the wider bear weight it got (45% combined).

## My thoughts / overlay
- **Method range:** every defensible base lands in Tier D. The preliminary run on the engine's median base ($2.91/share) gave weighted IRR 3.88% and weighted IV@15% $26.74. The TTM base used here ($6.11/share) gives 5.04% / $50.28. The v4 pass ($240.63 price, TTM base) gave 5.3% / $52.57. The honest headline is a robust D, not a borderline one.
- The market is pricing STLD on earnings at a guided record quarter plus an aluminum platform option. On owner's earnings — cash after all capex and SBC — the TTM base yields 2.43% at $251.4915, and no scenario in the set, including super bull (15.55% growth start, 1.25x OE), produces an IV@15% above $107.25 or an IRR above 8.26%. There is no path in this model where buying at $251.4915 clears 15%; it does not clear 10% in any single scenario.
- Quality is not the question: STLD is arguably the best-run US steelmaker — a real EAF cost edge, 13% three-year after-tax ROIC, disciplined buybacks, investment-grade-style liquidity. The question is price: $251.4915 for a commodity spread business whose earnings fell for three straight years before this upcycle, with the upcycle partly underwritten by trade policy.
- **Hurdle math:** the weighted path clears 15% at $50.28 (the weighted IV@15%); a purchase with a margin of safety needs to be materially below that. At $251.4915 you are paying roughly five times the hurdle-clearing price.

## Final verdict
- **Final tier: D** (weighted IRR 5.04%; no tier override)
- Confidence: **Medium** (high that the stock does not clear 15% at this price — no defensible base or scenario gets close; medium on the point estimate, given OE volatility and the 4.51x scenario spread)
- One-liner: Best-in-class EAF steelmaker with a real cost advantage but no pricing power, moat 5/10 — at $251.49 (TTM owner's earnings $6.11/share, a 2.43% OE yield, into a guided record quarter) it yields a 5.04% weighted IRR with IV@15% of $50.28; it clears the 15% hurdle only at ~$50, and even the super-bull case ($107.25) stays below half today's price.
