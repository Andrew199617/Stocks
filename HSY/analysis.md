# HSY — The Hershey Company
v5 run, 2026-10-14. In scope (market cap $33.322B at $164.28, nasdaq_quote_api — key_numbers.md).

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.py output (ttm.json), financials_history.csv, or the cited earnings releases — none are recomputed.

## What it is
The dominant US confectionery company (Hershey's, Reese's, Kisses and 80+ brands), plus a growing North America Salty Snacks segment (SkinnyPop, Dot's Pretzels, LesserEvil — acquired 2025) and a small International segment. Q2 2026 (reported July 30, 2026): net sales $2.79B, +6.6% YoY, adjusted EPS $1.90 — growth carried by net price realization while total company volume fell ~8% (North America Confectionery volume ~-10%). FY2026 guidance: net sales +4.5–5% (organic +3–3.5%), adjusted EPS $8.36–$8.52.

## Owner's earnings
**FY2025 (10-K via EDGAR, financials_history.csv):** operating cash flow $2,277,367,000; capex $454,622,000; SBC $65,460,000 (always a real cost, and small here relative to OCF).
- **Conservative owner's earnings FY2025: $1,757,285,000 = $8.66/share** (key_numbers.md: latest FY OE total $1.757B, latest FY OE/share $8.66).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $185,297,000 — far below the conservative figure and not representative: FY2025 net income was depressed by non-cash commodity-derivative mark-to-market losses (see NI_OCF_DIVERGENCE below) and the maintenance formula also subtracts a large working-capital swing. The OCF-based conservative figure is the cleaner base here.
- OE positive 5 of the last 5 fiscal years. Share count is drifting down slowly (share count CAGR −0.35%, growth adj +0.35%).
- The engine did not produce a net-debt figure for HSY (net debt shown as — in key_numbers.md), so no balance-sheet ratio is quoted; leverage is not the story in this verdict either way — valuation is.

**Base used = the engine's normalized base (median of last 3 FY OE/share) = $8.66/share** (base_source: median_of_last_3_fy_oe_per_share; the median and the latest FY coincide at $8.66). The TTM alternative was run and rejected — see STALE_FY in Flags. That makes this base the conservative choice: on the ttm.py legs that do align (below), TTM OE total is above the FY2025 total.

## Moat: 7/10 — strong, not wide-open
Justification: dominant US chocolate position and proven pricing power, held back from 8–9 because pricing is now visibly costing volume, cocoa is structurally more expensive, and there is no network-effect or switching-cost protection against slow category erosion.
- FOR: ~36% US chocolate share, #1 position ahead of Mars; flagship brands (Reese's, Hershey's, Kisses) with proven pricing power; entrenched retail shelf relationships — a critical partner retailers won't risk out-of-stocks with; scale cost advantage and high through-cycle returns on capital; salty-snacks diversification (SkinnyPop, Dot's, LesserEvil).
- AGAINST: pricing now costing volume — Q2 2026 volume ~-8%, NA Confectionery ~-10%; structurally elevated cocoa costs, and the hedge book is not positioned to capture cocoa relief during 2026; GLP-1 appetite suppression and health/sugar trends erode category demand slowly; Mars and Mondelez competition, private label at the value end; salty-snacks supply/execution issues (Dot's multipacks, logistics costs).
- A 7 gives CAP = 11.1 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 11.1 years, 15-year projection.

## DCF — v5 final run (2026-10-14)
Growth inputs: the engine's blended growth is 5.93% (rev CAGR 5y 7.49%, rev CAGR 3y 3.92%, latest rev YoY 4.38%, OE/share CAGR 2y 9.71%), adjusted +0.35pp for the shrinking share count → g_base 6.28%. Default scenario offsets (−12/−5/0/+5/+12pp) and OE multipliers (0.75/0.90/1.00/1.10/1.25) and default probabilities (10/25/30/25/10) were kept — checked against recent prints:
- Base start 6.3% sits above guided FY2026 *sales* growth (+4.5–5%) — deliberately: owner's earnings have operating leverage to the guided margin recovery (pricing already taken, cocoa relief building into 2027), and the company's own FY2026 guide implies adjusted EPS growth of 32.5–35% off the depressed FY2025 base.
- Super-bull start 18.3% is *below* that guided adjusted-EPS rebound, so no scenario start sits below what the company just printed/guided without a reason; the bear/super-bear starts (-5.7% / +1.3%) are the volume-elasticity and cocoa-stays-high cases, not print contradictions.
- Price $164.28.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -5.7% | 0.75 | Cocoa stays structurally high, volume losses accelerate, GLP-1 bite | $36.28 | 4.89% |
| Bear | 25% | 1.3% | 0.90 | Pricing sticks but volumes keep shrinking; margin recovery stalls | $60.36 | 7.03% |
| Base | 30% | 6.3% | 1.00 | Guided sales path, gradual margin recovery as cocoa relief lands | $84.93 | 9.16% |
| Bull | 25% | 11.3% | 1.10 | Full margin recovery toward historical levels, volumes stabilize | $118.45 | 11.82% |
| Super bull | 10% | 18.3% | 1.25 | Earnings rebound compounds; salty snacks scale cleanly | $187.76 | 16.45% |

- **Probability-weighted: IV@15% $92.59 (−43.6% vs price), IV@12% $124.67, IV@10% $160.72, weighted IRR 9.85%, base-case IRR 9.16%**
- **Tier by numbers: D.** Diagnostics (key_numbers.md): OE yield 5.27%, terminal value 20.2% of IV@15%, scenario spread 5.18x, 9.4 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.4 months ago): ttm.py was run. Its flow legs align on the 2026 anchor and are quoted verbatim: OCF FY $2,277,367,000 − prior YTD $508,898,000 + current YTD $888,122,000 = TTM $2,656,591,000; capex FY $454,622,000 − prior YTD $230,615,000 + current YTD $204,427,000 = TTM $428,434,000; SBC FY $65,460,000 − prior YTD $31,003,000 + current YTD $34,847,000 = TTM $69,304,000; TTM OE total $2,158,853,000. **However, the shares leg in ttm.json is period-mismatched**: it reports a current-YTD diluted share count of 221,322,000 for the period 2015-01-01 to 2015-10-04 (FY leg 2014), not for the 2026 YTD period — against the engine's latest diluted shares of 202,839,656. The printed TTM base of $9.75/share therefore rests on a stale denominator and was **not** used; the final run uses the engine's normalized median base ($8.66/share) with this reason stated, per the fallback rule for an unusable TTM. No base was hand-reconstructed. Directionally this is conservative: the aligned TTM flow legs show OE total recovering above FY2025.
- **NI_OCF_DIVERGENCE** (2025): identified — FY2025 net income of $883,259,000 (financials_history.csv) was hit by non-cash mark-to-market losses on commodity derivatives: the FY2025 results release reconciliation shows a $423,161,000 pre-tax mark-to-market adjustment for commodity derivatives in FY2025 (vs a $460,437,000 gain in FY2024), plus goodwill impairment charges of $6,403,000 and business-realignment costs. Those losses depress net income (and the maintenance OE definition) but not operating cash flow, which is why the OCF-based conservative OE — the base used throughout — is unaffected. Underlying (non-GAAP) FY2025 net income per the same release was $1,283,406,000, still down on cocoa costs, which the scenarios' bear weights already reflect.
- **WIDE_SCENARIO_SPREAD** (5.18x): real — the spread is the cocoa/margin-recovery question, which is genuinely binary-ish over the next two years. Confidence is capped at medium (never high), and the verdict is sized to the weighted/conservative end.

## My thoughts / overlay
- This is a quality-vs-price result, not a quality doubt. Even the bull case (full margin recovery, IV@15% $118.45) sits below the $164.28 price; only the 10%-weighted super bull ($187.76) clears it. At a 10% discount rate the weighted IV is $160.72 — roughly the current price — i.e. the market is pricing Hershey as a ~10%-return bond-like compounder, which may be fair for the business but is below Andrew's 15% hurdle by a wide margin.
- The verdict is not fragile to the moat call: the preliminary run at the default moat 5 (CAP 8.5y) gave a weighted IRR of 9.46% and weighted IV@15% of $88.97 — same tier D. Nor is it fragile to the rejected TTM pin in the tier sense: a higher base would lift the numbers, but the pin as printed is not defensible (stale share denominator), and no tier above D is claimed on it.
- Hurdle math: the price that clears 15% on the weighted case is the weighted IV@15% itself, **$92.59**; a buyer wanting a margin of safety against the bear cases ($60.36) needs to pay materially less than that. Nothing in the current setup — Q2 2026 volume −8%, Hershey Trust selling reported at ~$108.7M net over the 90 days to late September 2026 (per search-result reporting), salty-snacks execution issues — argues for paying up ahead of volume stabilization.
- Watch items: Halloween/holiday volume prints, cocoa cost trajectory into 2027 (when hedge positioning should let relief through), and whether salty-snacks supply issues clear.

## Final verdict
- **Final tier: D** (weighted IRR 9.85% on the v5 final inputs; no tier override)
- Confidence: **Medium** (clean filing base and a predictable business, capped by the 5.18x scenario spread and the unusable TTM pin)
- One-liner: High-quality wide-brand moat (7/10) but slow-growing and priced for perfection — weighted IRR 9.8% at $164.28 vs weighted IV@15% $92.59; only clears Andrew's 15% hurdle below ~$93.
