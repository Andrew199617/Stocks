# TPR — Tapestry, Inc.
v5 run, 2026-10-15. In scope (market cap $25.150B at $119.65, nasdaq_quote_api — under the $40B cutoff).

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.py output, or financials_history.csv — none are recomputed.

## What it is
US accessible-luxury house built around Coach (handbags / leather goods), plus kate spade new york. Stuart Weitzman was divested in 2025, so this is now effectively a one-engine company: Coach drove FY2026 — revenue $8,004,200,000, up 14.17% YoY (latest rev YoY, dcf_numbers.json) — with Kate Spade shrinking (revenue down ~10% in FY2025 and down again through FY2026, guided to a high-single-digit decline in FY2027 per the Q4 FY2026 release coverage). FY2027 guidance from that release: revenue $8.4–$8.5B (mid-single-digit growth) and EPS $7.80–$7.90 (low-double-digit growth), tariffs expected roughly net neutral.

## Owner's earnings
**FY2026 (10-K via EDGAR, from financials_history.csv):** operating cash flow $1,978,500,000; capex $166,000,000; SBC $104,500,000 (always a real cost).
- **Conservative owner's earnings FY2026: $1,708,000,000 = $8.13/share** (dcf_numbers.json: base_oe_latest_per_share $8.125594671741199)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $1,530,500,000 — same ballpark, which supports the conservative figure.
- OE positive 5 of the last 5 fiscal years. Net debt $1,421,900,000 (dcf_numbers.json); diagnostics put net debt at 0.83x normalized OE — leverage is not the story here.
- SBC is modest relative to OCF ($104,500,000 against $1,978,500,000 in FY2026) and buybacks are real: diluted shares fell from 241,300,000 (FY2023) to 210,200,000 (FY2026) in the filed history; the company returned ~$1.7B to shareholders in FY2026 per the earnings release.

**Base used = latest FY2026 OE/share, via a declared base_override (see BASE_DIVERGENCE below) — NOT the engine's 3-yr median:**
- Construction, exclusively from this run's code outputs: FY2026 OCF $1,978,500,000 − capex $166,000,000 − SBC $104,500,000 = conservative OE $1,708,000,000, over 210,200,000 diluted shares = **$8.125594671741199/share** (dcf_numbers.json base_oe_latest_per_share; financials_history.csv FY2026 row).
- ttm.py was run and exits non-zero: "ocf: no post-FY YTD fact (no 10-Q since the 2026-06-27 fiscal year end)" — the same for capex, SBC and shares. There is no post-FY quarter yet, so TTM = FY2026 and the latest-FY base is the current run rate, not an extrapolation.
- The engine's normalized base (3-yr median) is $4.548885077186964/share — reported in key_numbers.md and used in the method range below.

## Moat: 5/10 — moderate, brand-only
Justification: Coach has demonstrated real pricing power (handbag AUR up mid-teens in Q4 FY2026, gross margin expansion, operating margin 23.4% non-GAAP in FY2026 per the release) and is gaining share with Gen Z customers (11M new customers added in FY2026) — but this is a fashion brand moat with no switching costs, no recurring revenue and no structural cost advantage, and the portfolio around it is shrinking.
- FOR: Coach brand heat and proven pricing power — mid-teens handbag AUR gains with units still growing; direct-to-consumer control of distribution protects price integrity; scale in accessible luxury (top-three handbag position in North America and Greater China); Gen Z customer flywheel (11M new customers in FY2026, ~35% Gen Z in Q4).
- AGAINST: No switching costs or recurring revenue — brand heat is re-earned every season and fashion cycles are fickle; single-brand concentration: Coach is ~86% of revenue while Kate Spade shrinks (FY2025 Kate Spade impairment ~$855M); aspirational-consumer cyclicality — the customer trades down first in a downturn; tariff exposure on imported leather goods (a ~$160M FY2026 drag was flagged in coverage; FY2027 guided roughly neutral, not guaranteed); European luxury houses and resale compete for the same wallet.
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — v5 final run (2026-10-15)
Growth recalibration (written reason): the engine's g_base is 15.03% (blend 10.52% + buyback adjustment 4.51pp), but the blend is inflated by oe_ps_cagr_2y of 33.79% — an artifact of the FY2026 step-up off the deal-cost-depressed FY2024–25 OE base. The prints that mean something — rev CAGR 5y 6.88%, rev CAGR 3y 6.34%, latest YoY 14.17%, and FY2027 guidance of mid-single-digit revenue growth with low-double-digit EPS growth — center the base case on ~10% OE/share growth (revenue growth + margin + the buyback already in the blend). Scenario starts were therefore set via offsets (−0.15 / −0.10 / −0.05 / −0.01 / +0.03 vs g_base) to ~0 / 5 / **10** / 14 / 18%. Probabilities skewed one notch bearish vs default (10/30/30/20/10) for the concentration and deceleration evidence below; OE multipliers are the defaults 0.75/0.90/1.00/1.10/1.25. Price $119.65.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | 0.0% | 0.75 | Coach heat fades, Kate Spade keeps shrinking, tariffs bite | $45.09 | 7.12% |
| Bear | 30% | 5.0% | 0.90 | Growth settles at guidance revenue pace, no EPS leverage | $66.63 | 9.55% |
| Base | 30% | 10.0% | 1.00 | Guided path: mid-single revenue, low-double EPS via buybacks | $91.02 | 12.18% |
| Bull | 20% | 14.0% | 1.10 | Coach holds double-digit growth, Kate Spade stabilizes | $117.96 | 14.84% |
| Super bull | 10% | 18.0% | 1.25 | Coach momentum persists, margins keep expanding | $157.70 | 18.37% |

- **Probability-weighted: IV@15% $91.17 (−23.8% vs price), IV@12% $122.49 (+2.4%), IV@10% $157.57, weighted IRR 12.21%, base-case IRR 12.18%**
- **Tier by numbers: C.** Diagnostics (key_numbers.md): OE yield 6.79%, terminal value 19.8% of IV@15%, scenario spread 3.50x, net debt 0.83x normalized OE, 3.6 months since FY end.
- Sanity check vs recent prints: the super-bull start (18.0%) sits below FY2026's actual prints (revenue +14.17%, non-GAAP EPS +38% per the release) for a written reason — FY2026 was the step-up year and management has already guided FY2027 down to mid-single-digit revenue / low-double-digit EPS growth, so even the bull cases are calibrated to the guided deceleration, not to the step-up. The base start (10.0%) matches the guided EPS growth rate.

## Flags — every fragility flag resolved
- **BASE_DIVERGENCE** (latest FY $8.13 vs 3-yr median $4.55): the median is the distorted one. It is anchored on FY2024–25, when OE/share was flat at ~$4.5 despite non-GAAP EPS rising ($4.29 → $5.10 → $7.05 across FY2024–26 per release coverage), because OCF was depressed by terminated-Capri costs (FY2025 pre-tax charges of $268.4M including a $119.4M debt-extinguishment loss, per the FY2025 10-K excerpt) and deal-era financing drag. FY2026 is corroborated independently: revenue +14.17%, non-GAAP operating income +33% and GAAP net income of $1,527,700,000 converting to OCF of $1,978,500,000, with FY2027 guidance building on the FY2026 level rather than reversing it. Resolution: latest-FY base via the declared base_override above; the step-up risk is carried in the growth recalibration (starts cut to 0–18%) and the 40% combined bear-side weight, not by halving the base. On the median base the preliminary run gave weighted IRR 9.93% / IV@15% $66.79 (Tier D) — that is the method range, documented below.
- **NI_OCF_DIVERGENCE** (2025): FY2025 GAAP net income was $183,200,000 against OCF of $1,216,600,000 (financials_history.csv). The one-off is identified: a ~$855M non-cash Kate Spade goodwill/intangible impairment (FY2025 10-K: $854.8M) crushed net income but is added back in OCF, alongside the Capri termination charges above. The OCF-based conservative OE used throughout is not contaminated by the impairment; it was, if anything, depressed by the cash deal costs.
- **OE_VOLATILE** (OE/share spans >3x over 5 years): real, and it is the step-up pattern above plus the COVID-era trough (FY2020 OE/share was the low end of the filed history). Handled by the latest-FY base with recalibrated (lower) growth starts and a 30% bear weight — volatility is priced in the scenarios, not smoothed away by the median.
- **BUYBACK_TAILWIND** (share count −4.51%/yr): already credited via the +4.51pp share-count adjustment inside g_base; the growth recalibration was applied to the total g_base including that credit, so buybacks are not double-counted in the verdict.
- **WIDE_SCENARIO_SPREAD** (preliminary run, 4.42x): the final run's spread is 3.50x — still wide because the outcome genuinely hinges on how long Coach's heat lasts. Confidence is therefore medium, not high, and the verdict is sized to the conservative end.

## My thoughts / overlay
- The honest headline is the method range: defensible bases span Tier D (median base, weighted IRR 9.93%, IV@15% $66.79) to Tier C (latest-FY base, weighted IRR 12.21%, IV@15% $91.17). Both sit below the 15% hurdle at $119.65 — the disagreement is about how far below, not about whether it clears. Even the final run's super-bull case (18.37% IRR) is the only scenario clearing 15%, at 10% probability.
- Quality is real but the price already pays for it: Coach's pricing power, a clean balance sheet (net debt $1,421,900,000) and heavy buybacks are visible to everyone after a +38% non-GAAP EPS year; the stock fell ~16.5% on the Q4 print and is still priced above the weighted IV@15%.
- Key risks: Coach concentration (~86% of revenue), Kate Spade still shrinking after the impairment, tariff guidance ("roughly neutral") depending on mitigation holding, and an aspirational customer who is the first to pull back in a downturn.
- Hurdle price: the weighted IV@15% of $91.17 is the price that clears 15% on these inputs; a buyer wanting a margin of safety against the bear cases ($66.63 / $45.09) needs to pay materially less than that.

## Final verdict
- **Final tier: C** (weighted IRR 12.21% on the final inputs; method range D to C)
- Confidence: **Medium** (high on the FY2026 filing figures, medium on how durable the Coach step-up is — scenario spread 3.50x)
- One-liner: Strong Coach franchise, moat 5/10 — but at $119.65 the weighted IRR is only 12.2% with IV@15% of $91.17; it clears the 15% hurdle only below ~$91.
