# WTW — Willis Towers Watson Public Limited Company
v5 run, 2026-10-14. Market cap $29.418B at $297.15 (nasdaq_quote_api) — in scope under $40B. All figures below are copied from dcf_numbers.json, ttm.json, financials_history.csv, or key_numbers.md — none are recomputed.

## What it is
Global advisory, broking and solutions company in two segments: Health, Wealth & Career (benefits, retirement and talent consulting/administration) and Risk & Broking (corporate risk advice and insurance brokerage, placing premiums for large clients). Asset-light, people-and-relationships business: revenue is commissions and fees, not underwritten insurance risk — which matters for the SECTOR_MODEL_MISMATCH flag below. Q2 2026 (reported 2026-07-30): revenue $2.46B, up 9% reported / 5% organic, adjusted diluted EPS $3.35, up 17% year over year; management reaffirmed full-year 2026 guidance, set mid-single-digit organic growth expectations for both segments, announced Propel (an AI/automation plan targeting ~30% adjusted operating margin in 2028), and added $1.5B to buyback authority, with 2026 repurchases guided to at least $1.0B.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $1,775,000,000; capex $229,000,000; SBC $153,000,000 (always a real cost).
- **Conservative owner's earnings FY2025: $1,393,000,000 = $14.07/share** (base_oe_latest_per_share in dcf_numbers.json)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $1,934,000,000 for FY2025 (financials_history.csv) — above the conservative figure; the conservative OCF-based figure is used throughout, so the verdict does not lean on the higher one.
- OE positive 5 of the last 5 fiscal years. Net debt $3,174,000,000 (dcf_numbers.json); diagnostics put net debt at 2.04x normalized OE on the final (TTM-base) run — material but serviceable for a steady fee business, and folded into the verdict below: leverage is one reason the price has no slack.
- Growth history is distorted at both ends: revenue CAGR is only 2.15% (5y) / 2.93% (3y) and latest reported revenue YoY is −2.29%, because the TRANZACT direct-to-consumer business was sold on 2024-12-31 and its revenue left the continuing base (see NI_OCF_DIVERGENCE); the OE/share CAGR (2y) of 23.47% is equally unrepresentative, rebounding off the impairment-depressed period. Organic revenue growth — the clean signal — runs mid-single-digit (5% in Q2 2026).

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $1,775,000,000 − prior YTD $326,000,000 + current YTD $474,000,000 = **TTM $1,923,000,000**
- Capex: FY $229,000,000 − prior YTD $109,000,000 + current YTD $114,000,000 = **TTM $234,000,000**
- SBC: FY $153,000,000 − prior YTD $68,000,000 + current YTD $109,000,000 = **TTM $194,000,000**
- Shares (current-YTD weighted diluted): **95,000,000**
- **TTM OE total $1,495,000,000 → base OE/share $15.74** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $11.24/share — it averages in the TRANZACT-impairment era and a higher share count; the TTM base is the current continuing business on the current share count, so it is used. Both bases produce Tier D (see Thoughts), so the choice does not drive the verdict.

## Moat: 6/10 — moderate, real but contestable
Justification: Scale global broker/adviser with high client retention, embedded relationships and data/analytics, but it is the #3 player behind Marsh McLennan and Aon, the assets walk out the door (brokers/consultants), and a softening insurance pricing cycle plus AI-enabled challengers pressure the model.
- FOR: Global scale and network — large multinational clients need a broker/adviser that can serve them across countries and lines
- FOR: High retention and switching friction — embedded benefits/retirement administration and broking relationships are sticky and trust-based
- FOR: Data, analytics and specialty expertise (climate, cyber, M&A, specialty lines) that generalists cannot easily replicate
- FOR: Asset-light, recurring commission/fee model with proven buyback-funded per-share compounding — share count shrinking 4.0%/yr
- AGAINST: #3 scale position behind Marsh McLennan and Aon, with Arthur J. Gallagher consolidating the middle market via M&A
- AGAINST: People are the asset — producer/consultant poaching is a permanent erosion force in broking and consulting
- AGAINST: Insurance pricing cycle turning — large/complex property rates fell sharply in Q2 2026, a direct headwind to brokerage commissions
- AGAINST: AI/automation and technology-native brokers (e.g. the Newfront model WTW itself bought) can compress middle-market broking economics
- A 6 gives CAP = 9.8 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 9.8 years, 15-year projection.

## DCF — v5 final run (2026-10-14)
Engine blended growth: g_blend 2.54% + share-count adjustment +4.03pp (buybacks) = g_base 6.57%. Sanity check against actual prints: base 6.57% sits just above Q2 2026 organic revenue growth of 5% and management's mid-single-digit organic guidance for both segments, with the difference being the buyback credit the engine already adds — reasonable, not heroic. Bull 11.57% requires the guided ~100bp/yr Risk & Broking margin expansion plus buybacks to land. Super bull 18.57% is above the revenue prints but in line with Q2 2026 adjusted EPS growth of +17%, and is only defensible as a 10% tail in which Propel delivers its ~30% 2028 adjusted-margin target early — it is a tail, not a forecast, and it still only reaches a 16.12% IRR. Default probabilities 10/25/30/25/10 and default OE multipliers 0.75/0.90/1.00/1.10/1.25 were kept — the evidence (steady MSD organic growth, margin plan, buybacks vs a softening pricing cycle and integration costs) is balanced, with no reason to skew. Price $297.15.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -5.43% | 0.75 | Pricing cycle hardens downward, producers leave, Propel costs without payoff | $68.04 | 5.05% |
| Bear | 25% | 1.57% | 0.90 | Low-single-digit organic growth, margin plan stalls, Newfront/Willis Re drag persists | $111.43 | 7.14% |
| Base | 30% | 6.57% | 1.00 | Mid-single-digit organic growth + buybacks, gradual margin expansion | $154.68 | 9.18% |
| Bull | 25% | 11.57% | 1.10 | Margin expansion lands, specialty lines and Health (guided high-single-digit) carry growth | $212.47 | 11.71% |
| Super bull | 10% | 18.57% | 1.25 | Propel delivers ~30% margins early, buybacks compound, pricing stabilizes | $328.96 | 16.12% |

- **Probability-weighted: IV@15% $167.08 (−43.8% vs price), IV@12% $224.29, IV@10% $288.43, weighted IRR 9.79%, base-case IRR 9.18%**
- **Tier by numbers: D.** Diagnostics (dcf_numbers.json): OE yield 5.30%, terminal value 19.8% of IV@15%, scenario spread 4.83x, net debt 2.04x normalized OE, 9.4 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.4 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, quoted above (TTM OE/share $15.74 vs latest-FY $14.07 and 3-yr median $11.24).
- **BUYBACK_TAILWIND** (share count shrinking 4.0%/yr): already credited via the +4.03pp share-count adjustment inside g_base 6.57%; not double-counted in the verdict. TTM shares of 95,000,000 vs 99,000,000 in FY2025 confirm the shrink is continuing, funded by the guided ≥$1.0B of 2026 repurchases.
- **NI_OCF_DIVERGENCE** (2024): identified — the TRANZACT divestiture. FY2024 net income was −$98,000,000 against OCF of $1,512,000,000 (financials_history.csv) because the sale (closed 2024-12-31) triggered a pretax loss on disposal and a goodwill impairment in the Benefits, Delivery & Administration unit — over $1.0B of pretax impairment/disposal charges per the FY2024 reporting, all non-cash. The OCF-based conservative OE series used throughout is not contaminated by it; if anything the median base is depressed by that era, which is a second reason the TTM base is preferred.
- **SECTOR_MODEL_MISMATCH** (Finance): partially mitigated in substance — WTW is a fee/commission broker and adviser, not a balance-sheet insurer or bank, so OCF − capex − SBC describes its economics far better than it would an underwriter's. Per the flag's instruction, confidence is still graded **low** and the tier is treated as soft.
- **WIDE_SCENARIO_SPREAD** (super-bull IV 4.83x super-bear IV): real — the spread is driven mainly by the growth-start range on a long CAP, not by data uncertainty. Confidence is capped (graded low in any case per the sector flag) and the verdict is sized to the conservative end: even the super-bull case barely clears 15%.

## My thoughts / overlay
- The method range is narrow for once: the preliminary run on the 3-yr median base ($11.24/share) gave weighted IRR 7.64% and IV@15% $116.78; the final TTM-base run gives 9.79% and $167.08. Both are Tier D — the TTM run sits just under the 10% Tier C line, so the honest headline is "D, borderline C on the most current base," not a tier that flips with method.
- Quality is not the problem: OE positive 5/5 years, recurring fees, buybacks shrinking the count ~4%/yr, and a credible margin plan (Propel, ~30% adjusted operating margin targeted for 2028). The problem is price: at $297.15 the market is already paying for the bull path. Even the super-bull scenario (18.57% growth start, 1.25x OE) values the stock at $328.96 — only modestly above the price — and the base case values it at $154.68.
- Balance sheet folded in: net debt $3,174,000,000 (2.04x normalized OE on the final run) is manageable for this cash profile but leaves no room for the price to be wrong; Q2 2026 GAAP EPS also fell year over year on Newfront transaction/integration costs, a reminder that the M&A-funded growth model carries recurring "one-off" costs, and the Willis Re joint venture and Newfront are guided EPS headwinds in 2026.
- Price that clears 15%: the weighted IV@15% is **$167.08** — a buyer needs roughly that level (before any extra margin of safety) for the weighted case to clear Andrew's 15% hurdle. At $297.15 there is no margin of safety on any scenario except the super-bull tail.

## Final verdict
- **Final tier: D** (weighted IRR 9.79% on the v5 final TTM-base inputs; Tier D on the median base too — borderline C at best)
- Confidence: **Low** (sector-model mismatch per flag instruction, plus a 4.83x scenario spread — the business quality itself is well evidenced)
- One-liner: Good asset-light broker/adviser, moat 6/10 — but at $297.15 it does not clear 15% (9.8% weighted IRR, IV@15 $167.08); it would need to fall to about $167 to clear the hurdle.
