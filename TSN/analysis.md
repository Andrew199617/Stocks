# TSN — Tyson Foods, Inc.
v5 run, 2026-10-16. Price $54.04 (nasdaq_quote_api), market cap $19.29B — in scope under $40B. All figures below are copied from dcf_numbers.json, financials_history.csv, or ttm.py output — none are recomputed.

## What it is
One of the world's largest protein processors: Beef, Chicken, Pork, and Prepared Foods (Tyson, Jimmy Dean, Hillshire Farm, Ball Park, Wright, Aidells brands), sold through retail, foodservice, and export channels. Vertically integrated in chicken; commodity-exposed in beef and pork. FY2025 sales $54,441M.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** revenue $54,441,000,000; net income $474,000,000; operating cash flow $2,155,000,000; capex $978,000,000 (tag PaymentsToAcquirePropertyPlantAndEquipment); SBC $100,000,000 (tag ShareBasedCompensation — a real cost, but small for this business).
- **Conservative owner's earnings FY2025: $1,077,000,000 = $3.02/share** (base_oe_per_share $3.0168067226890756 in dcf_numbers.json)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $960,000,000 — same ballpark as the conservative figure.
- OE positive 4 of the last 5 fiscal years (oe_positive_years_of_last_5: "4/5"). Conservative OE totals from financials_history.csv: FY2021 $2,540,000,000; FY2022 $707,000,000; FY2023 −$248,000,000; FY2024 $1,357,000,000; FY2025 $1,077,000,000 — a commodity cycle, not a growth curve.
- **Base used = the engine's normalized base, median of last 3 FY OE/share = $3.02/share** (base_source: median_of_last_3_fy_oe_per_share). Latest-FY and normalized bases are identical ($3.0168067226890756), so there is no BASE_DIVERGENCE to resolve. A TTM base could not be used — see STALE_FY under Flags.
- Balance-sheet caveat: dcf_numbers.json reports net_debt_latest −$320,000,000 and net debt −0.30x normalized OE, but its used_tags show debt_lt: null — the engine found no long-term-debt tag, so that net-cash figure understates leverage and is not relied on here. External reporting on the Q3 FY2026 results put net debt at about $8 billion at roughly 2.1x leverage with about $4 billion of liquidity (cited search result, Aug 2026). The DCF itself runs off per-share owner's earnings, so this affects the risk read, not the IV arithmetic.

## Moat: 3/10 — weak
Justification: Scale, distribution, and branded Prepared Foods are real, but most of the sales base is raw commodity protein with little brand or pricing power, so returns are driven by cattle/hog/feed cycles Tyson does not control — Morningstar's published assessment likewise assigns Tyson no moat.
- FOR: Largest US meat company by volume; scale in procurement, processing, and distribution across retail, foodservice, and export
- FOR: Branded Prepared Foods portfolio (Jimmy Dean, Hillshire Farm, Ball Park) with the segment's steadier, higher margins (~9% adjusted operating margin in FY2025 per earnings reporting)
- FOR: Vertically integrated chicken operations, the current profit engine (FY2025 chicken adjusted operating income up sharply on execution and lower feed costs)
- FOR: Multi-protein diversification — chicken and prepared foods profits are currently offsetting beef losses
- AGAINST: Raw beef/pork/chicken are commodities with little to no pricing power; margins are set by livestock and feed spreads
- AGAINST: Beef cycle exposure is structural right now — cattle herd at multi-decade lows, FY2025 beef operating loss and a $343M beef goodwill impairment, and FY2026 beef losses guided wider through the year
- AGAINST: Recurring legal contingency accruals ($698M–$738M in FY2025 reporting) hit beef and pork repeatedly — looks systemic, not one-off
- AGAINST: Limited revenue or cost synergies across the three proteins; diversification adds complexity as much as stability
- A 3 gives CAP = 5.9 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 5.9 years, 15-year projection.

## DCF — v5 final run (2026-10-16)
Growth sanity check: the engine's blended growth is 2.12% (rev CAGR 5y 4.76%, rev CAGR 3y 0.72%, latest rev YoY 2.12%; oe_ps_cagr_2y null) and g_base is 2.68% after a +0.56pp share-count adjustment (share count −0.56%/yr). That base start is in line with actual prints — FY2025 revenue +2.12% YoY and Q3 FY2026 sales essentially flat year over year ($13,868M vs $13,884M a year ago, per Zacks' earnings report), with adjusted EPS $0.99 in Q3 FY2026. Bull (7.68%) and super-bull (14.68%) starts sit above anything Tyson has recently printed — by design: they are beef-cycle-recovery cases (herd rebuild eventually restoring beef margins on top of durable chicken/prepared-foods profits), not trend extrapolations, and they carry only 17% / 8% weight. Even the super-bull case does not clear the 15% hurdle at this price (see table).
Probabilities were skewed bearish vs the 10/25/30/25/10 defaults — 15/30/30/17/8 — because of OE_VOLATILE (below) and because FY2026 guidance moved down during the year: Q3 FY2026 reporting cut total adjusted operating income guidance to $2.1–$2.3B, and September reporting widened the expected FY2026 beef segment loss to $625M–$775M. Offsets and OE multipliers are the defaults (−12/−5/0/+5/+12pp; 0.75/0.90/1.00/1.10/1.25).

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | -9.32% | 0.75 | Beef losses persist, chicken margins normalize down, legal accruals keep recurring | $12.14 | 5.08% |
| Bear | 30% | -2.32% | 0.90 | Beef stays a drag through the herd cycle; flat protein demand | $18.78 | 6.73% |
| Base | 30% | 2.68% | 1.00 | Chicken + Prepared Foods carry a slowly recovering beef segment | $24.89 | 8.26% |
| Bull | 17% | 7.68% | 1.10 | Beef cycle turns, chicken margins hold near current levels | $32.56 | 10.14% |
| Super bull | 8% | 14.68% | 1.25 | Full beef recovery plus branded mix shift compounds | $46.85 | 13.44% |

- **Probability-weighted: IV@15% $24.21 (−55.21% vs price), IV@12% $31.89, IV@10% $40.43, weighted IRR 8.12%, base-case IRR 8.26%**
- **Tier by numbers: D.** Diagnostics (dcf_numbers.json): OE yield 5.58%, terminal value 17.92% of IV@15%, scenario spread 3.86x, months since FY end 12.61.
- The price that clears 15% on the weighted case is the weighted IV@15% itself: $24.21 — less than half the $54.04 price. Strikingly, even the super-bull IV@15% ($46.85) sits below the current price, so a buyer at $54.04 is not paid 15% even if the full beef-recovery case lands.

## Flags — every fragility flag resolved
- **STALE_FY** (latest fiscal year ended 13 months ago, 2025-09-27): ttm.py was run and exited non-zero with: "ttm.py: cannot compute TTM for TSN (CIK 100493): sbc: no post-FY YTD fact (no 10-Q since the 2025-09-27 fiscal year end)" — no ttm.json was produced, so the engine's median-of-3-FY base ($3.02/share) is used, per the fallback rule. Direction check from post-FY prints: Q3 FY2026 sales were flat year over year and FY2026 adjusted operating income guidance was cut to $2.1–$2.3B with wider beef losses, so a TTM base would if anything argue lower, not higher — the median base is not flattering the verdict.
- **OE_VOLATILE** (OE/share range over the last 5 years spans >3x): real and structural — conservative OE totals swung from $2,540,000,000 (FY2021) to −$248,000,000 (FY2023) to $1,077,000,000 (FY2025) on protein spreads. Handled by the normalized median base plus the bearish probability skew (45% on bear-or-worse).
- **NI_OCF_DIVERGENCE** (net income vs operating cash flow differ by >40% in 2023, 2024, 2025): explained, not a cash-quality red flag. D&A alone (financials_history.csv: $1,329,000,000 in FY2023, $1,388,000,000 in FY2024, $1,350,000,000 in FY2025) bridges most of the gap between net income (−$648,000,000 / $800,000,000 / $474,000,000) and OCF ($1,752,000,000 / $2,590,000,000 / $2,155,000,000); the rest is non-cash charges concentrated in the same years — the $343M beef goodwill impairment in FY2025 and legal contingency accruals that are expensed before they are paid. The OCF-based conservative OE used throughout is unaffected by those non-cash items, which is the right series to trust here — but the recurring legal accruals are a real future cash cost, noted under Moat AGAINST.
- **WIDE_SCENARIO_SPREAD** (preliminary run: super-bull IV 4.52x super-bear IV): in the final run the spread is 3.86x — still wide, reflecting genuine cycle uncertainty. Confidence is set to low, not high, and the verdict below is sized to the conservative end.

## My thoughts / overlay
- This is a commodity protein cycle story priced like a steady compounder. At $54.04 the market is paying for the chicken/prepared-foods strength and a beef recovery that, on Tyson's own FY2026 guidance, is still getting worse (beef loss guidance widened twice during FY2026; new CEO transition in October 2026 adds execution uncertainty).
- The method range is narrow for once: latest-FY base = median base = $3.02/share, the maintenance OE definition ($960,000,000) sits close to the conservative one ($1,077,000,000), and every scenario — including super bull at a 14.68% growth start Tyson has never printed recently — produces an IV@15% below the current price. There is no defensible input set in this run that gets TSN near the 15% hurdle.
- What would change the call: a confirmed cattle-herd rebuild timeline, beef segment losses narrowing for consecutive quarters, and an end to the recurring legal accrual pattern. None of those are in the current prints.
- No tier override: Tier D by numbers is the final tier. Confidence low — not because the inputs are gapped (there is no data gap; SBC, capex, and shares are all filed), but because the earnings stream is cyclical, FY2026 guidance is deteriorating, and the engine's net-debt diagnostic is unreliable for this name (debt_lt tag missing, noted above).

## Final verdict
- **Final tier: D** (weighted IRR 8.12% on the v5 final inputs; weighted IV@15% $24.21 vs price $54.04)
- Confidence: **Low**
- One-liner: Weak-moat (3/10) commodity protein processor — chicken and branded prepared foods are real, but beef-cycle losses and recurring legal accruals cap owner's earnings; at $54.04 it does not clear 15% in any scenario (weighted IRR 8.1%, IV@15% $24.21; hurdle-clearing price $24.21, super-bull IV only $46.85).
