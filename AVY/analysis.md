# AVY — Avery Dennison Corporation
Engine 5.4.0 run, 2026-10-17. In scope (market cap $13,726,773,000 at $175.31, nasdaq_quote_api). All figures below are copied from dcf_numbers.json, ttm.json, fundamentals.json, or financials_history.csv — none are recomputed.

## What it is
Global materials-science and digital-identification company, two segments: **Materials Group** (~$6.1B of FY2025 sales — pressure-sensitive label and graphic materials, the volume base) and **Solutions Group** (~$2.8B — RFID / Intelligent Labels, Embelex, Vestcom branding and identification solutions; 5-yr revenue CAGR 12.7% vs Materials 3.2%, per company IR summaries). High-value categories are ~45% of sales. Q2 2026: net sales $2.46B, +10.9% YoY (organic +7.6%), adjusted EPS $2.89 (+19.4%); FY2026 adjusted EPS guidance raised to $10.00–$10.30 (reported $9.40–$9.70). Management attributed roughly half of Q2 organic growth to customer inventory pre-buys (~$0.25 EPS tailwind) and expects most of it to unwind in H2 2026 (~$0.25 headwind in Q3).

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $881,400,000; capex $169,000,000; SBC $27,900,000 (always a real cost, though small here).
- **Conservative owner's earnings FY2025: $684,500,000 = $8.74/share** (oe_per_share, financials_history.csv)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $669,700,000 — same ballpark, which cross-checks the conservative figure.
- OE positive 5 of the last 5 fiscal years. OE/share by period end: $7.73 (2022-12-31), $6.64 (2023-12-30), $8.69 (2024-12-28), $8.74 (2025-12-31) — a cyclical, not a smooth, series (it printed $2.22 in FY2018).
- Capital returns exceed OE: FY2025 dividends paid $288,400,000 + buybacks $572,300,000 = $860,700,000 returned vs $684,500,000 of OE, and net debt rose from $2,823,100,000 to $3,530,100,000 in the year (fundamentals.json / financials_history.csv). Dividend streak intact: DPS raised every year since the 2010 cut ($3.70 FY2025, $3.82 TTM, payout ~42% of OE).

**TTM check (ttm.py, filing-direct, run for STALE_FY — quoted in full, NOT used as the base):**
- OCF: FY $881,400,000 − prior YTD $192,500,000 + current YTD $544,700,000 = **TTM $1,233,600,000**
- Capex: FY $169,000,000 − prior YTD $66,000,000 + current YTD $67,500,000 = **TTM $170,500,000**
- SBC: FY $27,900,000 − prior YTD $14,700,000 + current YTD $12,200,000 = **TTM $25,400,000**
- Shares (current-YTD weighted diluted): **76,700,000**
- **TTM OE total $1,037,700,000 → TTM OE/share $13.53** (ttm.json)

**Base used = the engine's normalized base, median of last 3 FY OE/share: $8.69/share** (base_source: median_of_last_3_fy_oe_per_share; latest FY $8.74, so median and latest agree — neither is distorted by an old year). **The TTM pin was rejected, with reason:** the TTM jump is a working-capital swing, not earnings growth. TTM revenue is $9,248,100,000 (+5.84% YoY) and TTM net income is $704,900,000 (**−0.86% YoY**) while TTM OCF is +51.59% YoY and TTM OE +70.31% YoY (fundamentals.json ttm block) — a $13.53 OE/share run rate cannot sit on flat net income, exceeds the company's own FY2026 adjusted EPS guide ($10.00–$10.30) by ~33%, and carries an 11.22% TTM OE margin vs 6.2–9.0% across the last ten fiscal years. The quarterly OCF rows show why: Q1 2025 OCF was −$16,300,000 (a trough base quarter) and Q2 2026 OCF was $408,200,000, inflated by the same pre-buy quarter management says unwinds in H2 2026. A TTM-flattered run is quantified under Thoughts as the optimistic end of the method range.

## Moat: 6/10 — moderate, upper end
Justification: global scale leader in pressure-sensitive label materials with qualified-materials switching costs and demonstrated pricing power, plus a growing Intelligent Labels / RFID franchise — capped at 6 because base label materials remain commodity-adjacent and cyclical, gross margin under 30% is not wide-moat territory, and no measured ROIC history exists in the outputs to support 7+.
- FOR: global scale leader; materials are qualified into converter/brand specifications, so switching risks label failure for a trivial cost saving; demonstrated pricing power — price held through 2021-22 inflation and rose low-single-digits in Q2 2026; Intelligent Labels / RFID franchise with high-value categories ~45% of sales and Solutions compounding faster than Materials; OE positive 5/5 years and a 15-year dividend-growth streak.
- AGAINST: base materials compete on price (UPM Raflatac, Fedrigoni, CCL) with paper/petrochemical input exposure; cyclical end demand (FY2023 OE/share $6.64 on destocking; FY2018 $2.22); the Q2 2026 print itself was ~half pre-buys that unwind in H2; leverage — net debt 5.19x normalized OE and rising because capital returns exceed OE.
- **Returns evidence (fundamentals.json):** gross margin 26.6% (FY ended 2022-12-31) → 27.2% → 28.9% → 28.8% (FY2025), 29.0% TTM — a real, steady expansion on mix shift and productivity. **roic_proxy is null for every year in fundamentals.json** (operating income is untagged in the engine's outputs), so no ROIC series can be quoted; the available proxy is ROE of 30.7% in FY2025 (23.6–48.9% across the decade) on an equity base shrunk by years of buybacks (equity $2,242,100,000 on assets of $8,801,700,000), which flatters it. That evidence gap is one reason the score stops at 6 rather than 7.
- A 6 gives CAP = 9.8 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 9.8 years, 15-year projection.

## DCF — final run (2026-10-17)
Growth check against actual prints (mandatory sanity check): the engine's blended start is 4.63% (components: rev CAGR 5y +4.91%, rev CAGR 3y −0.68%, latest FY YoY +1.14%, OE/share CAGR 2y +14.72% — the last is a base effect off the FY2023 trough; share count −1.61%/yr adds +1.61pp to the revenue legs only). Against the prints: FY2026 guidance embeds ~3–4% organic sales growth; underlying Q2 2026 organic growth ex-pre-buys is ~3.8%; guided adjusted EPS growth is ~+6.5% at the $10.15 midpoint (buybacks and margin expansion lift per-share growth above sales growth). The 4.63% base start sits between those anchors — no recalibration needed, and no scenario start sits below the latest relevant print without a reason: bear (−0.37%) and super bear (−7.37%) are deliberately set at destocking-year levels (FY2023 revenue fell, OE/share dropped ~14%), which is the written reason. Bull (+9.63%) asks for a repeat of Q2 2026's pre-buy-inflated reported sales growth (+10.9%) sustained as OE growth — demanding, which is what a bull case is. Super bull (+16.63%) exceeds every recent revenue print; it is defensible only as an OE/share tail (the +14.72% 2-yr OE/share CAGR actually printed, plus RFID mix) at 10% probability — and even it does not clear 15% (IRR 14.47%). Probabilities 10/25/30/25/10; OE multipliers 0.75/0.90/1.00/1.10/1.25 (defaults kept — the evidence is a steady compounder with a real but bounded cycle). Price $175.31.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | −7.37% | 0.75 | Hard destocking + input-cost squeeze; levered OE shrinks fast | $34.48 | 4.61% |
| Bear | 25% | −0.37% | 0.90 | Pre-buy unwind + flat volumes, a FY2023-style year that sticks | $56.44 | 6.40% |
| Base | 30% | +4.63% | 1.00 | Guided 3–4% organic growth, steady mix shift, buybacks continue | $78.35 | 8.18% |
| Bull | 25% | +9.63% | 1.10 | High-value / RFID mix accelerates; margin expansion compounds | $107.64 | 10.45% |
| Super bull | 10% | +16.63% | 1.25 | Intelligent Labels inflects company-wide growth | $166.77 | 14.47% |

- **Probability-weighted: IV@15% $84.65 (−51.71% vs price), IV@12% $112.99, IV@10% $144.67, IV@20% $59.29, IV@25% $45.41; weighted IRR 8.74%, base-case IRR 8.18%**
- **Tier by numbers: D.** Diagnostics (dcf_numbers.json): OE yield 4.96%, terminal value 19.24% of IV@15%, scenario spread 4.84x, net debt 5.19x normalized OE, 9.53 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.53 months ago): ttm.py was run and its full legs are quoted above. The TTM pin was *not* adopted — the TTM OE/share of $13.53 is a working-capital artifact (TTM net income −0.86% YoY; OE margin 11.22% vs a 6.2–9.0% ten-year range; the base quarter Q1 2025 printed −$16,300,000 OCF and the current quarter rode customer pre-buys that management guides to unwind in H2 2026). The median base ($8.69) and latest FY ($8.74) agree, so staleness is not flattering the result in either direction; the TTM figure is carried as the optimistic bound of the method range instead.
- **WIDE_SCENARIO_SPREAD** (super-bull IV 4.84x super-bear IV): real — it is mostly leverage and cycle amplitude (super-bear IV@15 $34.48 vs super-bull $166.77), not model noise. Confidence is capped at medium, and the verdict is sized to the bear end.
- **HIGH_NET_DEBT** (net debt 5.19x normalized OE): balance sheet from the filing (financials_history.csv / fundamentals.json): total debt $3,732,900,000 (current $522,900,000 + long-term $3,210,000,000), cash $202,800,000 → net debt $3,530,100,000, plus operating lease liabilities of $220,700,000. FY2025 interest expense was $135,400,000 — covered ~5x by OE — so this is not distress leverage; the risk is that it is *growing* leverage (net debt +$707,000,000 in FY2025) funding returns above OE. The bear and super-bear cases carry the stress (0.90x / 0.75x OE multipliers), and even the base case does not clear 15%, so leverage is not what makes this a D — the price is.
- **TIER_BAND** (bear tier D at 6.40% vs bull tier C at 10.45%): the verdict spans D to C; sized to the bear end — D. Note the band never reaches B under any scenario, including super bull (14.47%).

## My thoughts / overlay
- **Method range (the real headline):** on the sustainable median base this run prints Tier D (weighted IRR 8.74%, IV@15% $84.65). On the rejected TTM base ($13.53/share, same moat/probs) the identical structure prints Tier C — weighted IRR 12.03%, IV@15% $131.79 — still 25% below the $175.31 price and still short of 15%. The base dispute moves the answer by one tier; it does not change the conclusion. No defensible variant clears 15% at this price; the super-bull case alone (16.63% growth start, 1.25x OE) yields 14.47%.
- Quality is not the debate: a decade of positive OE, gross margin grinding up to ~29%, a 15-year dividend-growth streak, disciplined buybacks (−1.61%/yr share count), negligible SBC ($25,400,000 TTM). This is a good business priced like a great one — at $175.31 the buyer pays ~20x the sustainable OE/share for ~4–5% starting growth.
- What would change the verdict: a price near the 15% hurdle ($84.65), or evidence the TTM OE level is earnings-backed rather than working-capital-backed (two more quarters of net income growing in line with OCF), or Intelligent Labels growth large enough to lift the company-wide growth start into double digits sustainably.
- Watch item: H2 2026 pre-buy unwind (~$0.25 EPS headwind guided for Q3) and whether net debt keeps climbing to fund buybacks — returns ran 126% of OE in FY2025.

## Final verdict
- **Final tier: D** (weighted IRR 8.74% on the median base; method range D to C, sized to the conservative end)
- Confidence: **Medium** (high on the OE history and the filing data; the base-choice dispute is documented and does not change the verdict; capped below high by WIDE_SCENARIO_SPREAD)
- One-liner: Steady label-materials compounder, moat 6/10 — does not clear 15% at $175.31 (weighted IRR 8.7%, IV@15% $84.65; clears 15% only below ~$85), and even the rejected working-capital-flattered TTM base yields only 12.0%; quality is real, the price already pays for it.
