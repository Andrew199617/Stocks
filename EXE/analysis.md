# EXE — Expand Energy Corporation
v5 run, 2026-10-15. In scope (market cap $21.826B at $90.80, nasdaq_quote_api).

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.py output, financials_history.csv, or a cited search result — none are recomputed.

## What it is
The largest independent natural gas producer in the US, formed by the October 1, 2024 merger of Chesapeake Energy and Southwestern Energy (predecessors per search results / Wikipedia). Operations are in the Haynesville Shale (Louisiana) and the Marcellus (Northeast and Southwest Appalachia). 2025 production was 7,183 MMcfe/d (42% Haynesville, 36% Northeast Appalachia, 22% Southwest Appalachia) with 25,880 Bcf of proved reserves at December 31, 2025 (search results). This is a pure commodity E&P: revenue is Henry Hub-linked gas, and owner's earnings swing with the gas price.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** revenue $12,124,000,000; net income $1,819,000,000; operating cash flow $4,575,000,000; capex $2,736,000,000; SBC $46,000,000 (always a real cost, and here genuinely small).
- **Conservative owner's earnings FY2025: $1,793,000,000 = $7.46/share** (latest FY OE/share, key_numbers.md)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $1,610,000,000 (financials_history.csv) — same ballpark; for an E&P the conservative version is the honest one anyway, because total capex is what keeps a depleting reserve base producing.
- OE positive 4 of the last 5 fiscal years (key_numbers.md). The negative year is 2024 (conservative OE −$30,000,000), the merger year — see FLAGS.
- Net debt $4,393,000,000 at the latest FY end (key_numbers.md).

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $4,575,000,000 − prior YTD $2,418,000,000 + current YTD $3,498,000,000 = **TTM $5,655,000,000**
- Capex: FY $2,736,000,000 − prior YTD $1,220,000,000 + current YTD $1,460,000,000 = **TTM $2,976,000,000**
- SBC: FY $46,000,000 − prior YTD $22,000,000 + current YTD $22,000,000 = **TTM $46,000,000**
- Shares (current-YTD weighted diluted): **239,559,000**
- **TTM OE total $2,633,000,000 → base OE/share $10.99** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $3.62/share — rejected as the primary base because it straddles the merger break (see BASE_DIVERGENCE below), but retained as the conservative end of the method range: the preliminary run on the median base printed weighted IRR 11.79% and weighted IV@15% $64.29 (Tier C) even with the engine's default, far more optimistic growth starts.
- Caveat on the TTM base itself: it is cyclically elevated. The TTM OCF leg rests on a strong H1 2026 (current YTD OCF $3,498,000,000 vs prior YTD $2,418,000,000), while Q2 2026 alone already rolled over — revenue $2,960M vs $3,690M in Q2 2025, net income $522M vs $968M, operating cash flow $1,096M vs $1,322M (search results, StockTitan earnings summary). That elevation is why the final tier is sized down (see verdict).

## Moat: 4/10 — weak (scale and cost, no pricing power)
Justification: Scale and cost position are real — largest independent US natural gas producer with low-cost Haynesville/Marcellus acreage, >15 years of inventory, market/LNG connectivity and $500-600M of merger synergies — but it is a pure commodity price-taker: Henry Hub sets its price, reserves deplete and must be re-drilled, and OE swings with gas prices. That is a weak moat (4/10), not a moderate one.
- FOR: Largest independent US natural gas producer — scale across Haynesville and Marcellus; Low-cost acreage with more than 15 years of drilling inventory; Market-connected portfolio with LNG/export access and pricing premiums; Merger synergies — $500M in 2025, $600M targeted by end-2026 (search results); Investment-grade rating regained post-merger, debt being paid down.
- AGAINST: Pure commodity price-taker — Henry Hub sets the price, no pricing power; Reserves deplete — owner's earnings must be reinvested in drilling just to stand still; Gas price volatility drives OE/share from negative (2024) to $7.46 (2025); Appalachia takeaway/pipeline constraints and regulatory exposure; Long-term energy-transition demand risk for natural gas.
- A 4 gives CAP = 7.2 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 7.2 years, 15-year projection.

## DCF — v5 final run (2026-10-15)
Growth recalibration (written reason): the engine's blended growth is 24.74% and g_base 19.74%, but the blend is contaminated by the merger — latest revenue YoY is +186.28% (first full combined year vs a predecessor-only base) and OE/share CAGR 2y is 43.45% off the same break, while the clean signals are revenue CAGR 5y 6.03% and 3y 1.07% (key_numbers.md). Actual operating prints say volume is roughly flat: 2025 production 7,183 MMcfe/d, Q2 2026 production ~7.48 Bcfe/d, and full-year 2026 guidance reaffirmed at 7.4–7.6 Bcfe/d (search results). Scenario starts were therefore set via offsets (−0.2974 / −0.2274 / −0.1674 / −0.0974 / −0.0174 vs g_base) to −10 / −3 / **3** / 10 / 18%: the base start matches flat-to-modest volume growth plus synergy capture, the bear starts are negative because OE here is a gas-price derivative (Q2 2026 already printed down year-on-year), and even the super-bull start of 18% sits below the company's headline prints — justified because those prints are merger-consolidation artifacts, not organic growth. Probabilities were bear-weighted to 15/30/30/17/08 for a cyclical commodity producer (OE_VOLATILE); OE multipliers are the defaults 0.75/0.90/1.00/1.10/1.25. Price $90.80.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | -10.0% | 0.75 | Gas price slump; OE compresses off the elevated TTM base | $41.46 | 7.76% |
| Bear | 30% | -3.0% | 0.90 | Soft prices persist; flat volumes, no re-rating | $65.54 | 11.39% |
| Base | 30% | 3.0% | 1.00 | Guided volumes, synergies land, mid-cycle prices | $91.88 | 15.15% |
| Bull | 17% | 10.0% | 1.10 | LNG/data-center demand tightens the gas market | $131.90 | 20.24% |
| Super bull | 8% | 18.0% | 1.25 | Sustained gas price strength on current volumes | $201.79 | 27.69% |

- **Probability-weighted: IV@15% $92.01 (+1.3% vs price), IV@12% $121.64 (+34.0%), IV@10% $154.63, weighted IRR 15.16%, base-case IRR 15.15%**
- **Tier by numbers: B — final tier C after override (see verdict).** Diagnostics (key_numbers.md): OE yield 12.10%, terminal value 18.3% of IV@15%, scenario spread 4.87x, net debt 1.66x the base OE measure, 9.5 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.5 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, quoted above.
- **DILUTION** (share count growing 18.09%/yr): this is merger stock issuance, not SBC dilution — diluted shares went from 142,976,000 in 2023 to 240,370,000 in 2025 (financials_history.csv / key_numbers.md) because Southwestern holders were paid in stock. SBC itself is only $46,000,000. The trend has already reversed: the TTM share count (239,559,000) sits below the FY2025 count, and Q2 2026 coverage reports a completed repurchase of 10,026,164 shares for $949.02M (search results). The engine's −5.00pp growth adjustment for this "dilution" is one more reason the raw g_base was not used.
- **BASIS_BREAK_SUSPECT**: identified — the Chesapeake + Southwestern merger closed October 1, 2024. Pre-merger history is predecessor-only, 2024 is a part-year combined stub, and 2025 is the first full combined year, which is why latest revenue YoY prints +186.28%. No CAGR that straddles the break was trusted; growth inputs were rebuilt from production guidance and the clean CAGR components (5y 6.03%, 3y 1.07%).
- **OE_VOLATILE** (OE/share spans >3x over 5 years): real and structural — it is gas-price cyclicality (conservative OE total was −$30,000,000 in 2024 and $1,793,000,000 in 2025, financials_history.csv). Handled by bear-weighting the probabilities (45% on bear-or-worse) and by sizing the final tier to the conservative end.
- **NI_OCF_DIVERGENCE** (2024): merger year — net income −$714,000,000 vs operating cash flow $1,565,000,000 (financials_history.csv). The largest bridge visible in the filing history is non-cash depreciation/depletion/amortization of $1,729,000,000; the OCF-based conservative OE used throughout is not contaminated by it. The year's real effect on this run is through the distorted 2024 OE (−$30,000,000) dragging the 3-yr median base.
- **BASE_DIVERGENCE** (latest FY $7.46 vs 3-yr median $3.62): both are distorted in opposite directions. The median straddles the merger break (pre-merger share/asset base plus the negative merger year), so it understates the combined company; the TTM base ($10.99) reflects the combined company but at strong H1 2026 gas prices, so it likely overstates mid-cycle OE. TTM used as the base (current asset base, filing-direct), median retained as the method-range floor, and the gap between them is exactly why the tier is overridden down.
- **WIDE_SCENARIO_SPREAD** (4.87x): real — a gas producer's outcome range IS this wide. Confidence is low, and the verdict is sized to the conservative end.
- **HIGH_NET_DEBT** (preliminary run only; dropped from the final flag list): net debt is $4,393,000,000. Against the preliminary run's median base that was 5.04x normalized OE; against the TTM base actually used it is 1.66x (key_numbers.md). Direction is improving — total debt was $3.7B at Q2 2026 quarter-end, down ~$1.3B from year-end (search results) — but on a mid-cycle OE base the leverage is still material, which supports bear weight rather than a balance-sheet pass.

## My thoughts / overlay
- The honest headline is the method range: **C to B**. On the normalized median base the engine prints Tier C (weighted IRR 11.79%, IV@15% $64.29) even with optimistic growth starts; on the elevated TTM base it prints Tier B (15.16%, $92.01). The truth for a gas producer is mid-cycle, and mid-cycle sits between those bases.
- Quality of the asset base is not the debate: scale, low-cost inventory, $500M of 2025 synergies with $600M targeted by end-2026, an investment-grade rating regained, and debt coming down. The debate is purely what gas price the OE base is struck at — and the TTM base is struck at a strong one, with Q2 2026 already printing down year-on-year.
- Margin of safety: there is none at $90.80. The weighted IV@15% of $92.01 is the price that clears the 15% hurdle on the weighted path, and it sits only 1.3% above the market price; the bear-case IV@15% is $65.54. A buyer who wants to be paid even in the bear case needs an entry nearer that bear IV, not the current quote.
- What would change the verdict: a full year of OE at the TTM level through a soft-price period (proving $10.99 is mid-cycle, not peak), or a price drop toward the median-base IV.

## Final verdict
- **Final tier: C** (tier override of B by numbers, weighted IRR 15.16% — reason: the 15% clearance rests entirely on a cyclically elevated TTM base of $10.99/share vs $7.46 latest FY and $3.62 median; the median-base run prints C, IV@15% is only 1.3% above price, and the scenario spread is 4.87x — sized to the conservative end of a C-to-B method range)
- Confidence: **Low** (wide scenario spread, commodity-price-driven base, merger-break history)
- One-liner: Largest US gas producer, moat 4/10 — clears 15% only on a cyclically elevated TTM base (weighted IRR 15.2%, IV@15 $92.01 vs $90.80 price, no margin of safety); on the normalized median base it prints Tier C, so sized to C.
