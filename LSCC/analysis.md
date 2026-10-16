# LSCC — Lattice Semiconductor Corporation
v5 run, 2026-10-16. In scope (market cap $14.653B at $106.00, nasdaq_quote_api).

All figures below are copied from dcf_numbers.json, ttm.py output (ttm.json), or financials_history.csv — none are recomputed.

## What it is
Fabless designer of low-power, small-form-factor FPGAs — the leader in that niche and the last fully independent FPGA maker, against AMD (Xilinx) and Intel (Altera) at the high end. End markets: communications/computing (increasingly AI-server control and security sockets — root-of-trust, platform firmware resiliency, post-quantum crypto), industrial, and automotive. After a severe 2024–25 downturn (revenue fell from $737,154,000 in FY2023 to $509,401,000 in FY2024), the business is inflecting hard on AI-server attach: Q1 CY2026 revenue +42.2% YoY, Q2 CY2026 revenue $201.1M, +62.2% YoY, with Q3 guided to a $255M midpoint (press/earnings coverage, cited from search results).

## Owner's earnings
**FY2025 (10-K, period ended 2026-01-03, from financials_history.csv):** revenue $523,262,000; operating cash flow $175,107,000; capex $42,527,000 (tag PaymentsToAcquirePropertyPlantAndEquipment); SBC $115,613,000 (tag ShareBasedCompensation — always a real cost).
- **Conservative owner's earnings FY2025: $16,967,000 = $0.12/share** (base_oe_latest_per_share $0.1227).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $19,690,000 — same ballpark; both definitions say the latest FY produced almost no owner's earnings after charging SBC.
- OE positive 5 of the last 5 fiscal years, but the range is extreme: FY2023 conservative OE was $179,293,000 on $737,154,000 of revenue; the 2024–25 downturn crushed it.
- The story in one line: OCF held up ($175.1M in FY2025) while GAAP net income collapsed to $3,084,000, because SBC more than doubled ($52,985,000 in FY2024 → $115,613,000 in FY2025) and keeps rising (TTM $143,626,000). The conservative OE charges that SBC in full — that is the honest series, and it is thin.

**Base used = TTM owner's earnings through Q2 CY2026 (period ended 2026-07-04), from ttm.py (filing-direct, no hand math):**
- OCF: FY $175,107,000 − prior YTD $70,423,000 + current YTD $138,557,000 = **TTM $243,241,000**
- Capex: FY $42,527,000 − prior YTD $15,846,000 + current YTD $17,553,000 = **TTM $44,234,000**
- SBC: FY $115,613,000 − prior YTD $44,459,000 + current YTD $72,472,000 = **TTM $143,626,000**
- Shares (current-YTD weighted diluted): **140,024,000**
- **TTM OE total $55,381,000 → base OE/share $0.3955** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $0.4837/share — not used: it averages in peak-cycle FY2023 and understates the new SBC run-rate, which the TTM charges in full. The latest-FY figure ($0.1227) is not used either: it is trough-distorted (see BASE_DIVERGENCE). The TTM sits between them and is the current run-rate.

## Moat: 5/10 — moderate/narrow
Justification: a genuine niche leader with sticky design wins, but a niche player nonetheless — dwarfed in R&D by AMD/Intel, hostage to cyclical end markets, and its cash economics are heavily taxed by SBC.
- FOR: clear leader in low-power, small-form-factor FPGAs — the segment AMD/Xilinx and Intel/Altera underserve; last fully independent FPGA maker, so it gets sockets the platform owners won't prioritize; design-win stickiness — once designed into industrial/auto/server platforms with long lifecycles, sockets are hard to displace; security differentiation (Sentry platform-firmware-resiliency stack, hardware root of trust, post-quantum crypto) that maps directly onto AI-server control-plane demand; fabless, asset-light model.
- AGAINST: AMD (Xilinx) and Intel (Altera) dwarf Lattice in R&D and can contest any socket that gets big enough to matter; the niche is small — share of the overall FPGA/semi market is modest, so the moat protects a pond, not an ocean; end markets are brutally cyclical (revenue fell ~31% peak-to-trough in 2024); SBC load is enormous and rising ($143.6M TTM against $243.2M TTM OCF) — shareholders' slice of the cash economics is structurally diluted; AI-server demand is hyperscaler-capex-driven and outside Lattice's control.
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — v5 final run (2026-10-16)
Growth recalibration (written reason): the engine's blended growth is −1.78% and is unusable as printed — its components are backward-looking trough artifacts (rev CAGR 3y −7.44%, OE/share CAGR 2y −68.84%, latest FY rev YoY +2.72% measured across the trough), while the company just printed revenue +42.2% YoY (Q1 CY2026) and +62.2% YoY (Q2 CY2026) and guided Q3 to a $255M midpoint vs $201.1M in Q2. A base-case start below those prints would be the growth-cap failure mode, not conservatism. Scenario starts were therefore set via offsets (+0.0678 / +0.1678 / +0.2678 / +0.3678 / +0.4678 vs g_base −1.78%) to 5 / 15 / **25** / 35 / 45% OE/share growth. These are OE growth starts, not revenue: they assume operating leverage on the revenue ramp partly offset by the rising SBC charge. Probabilities 10/20/30/25/15 (modest bullish skew for the guided, already-printing ramp; still 30% on bear-or-worse for cyclicality). OE multipliers at defaults 0.75/0.90/1.00/1.10/1.25. Price $106.00.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | 5.0% | 0.75 | AI-server attach stalls, industrial/auto relapse; SBC keeps climbing | $2.70 | 0.09% |
| Bear | 20% | 15.0% | 0.90 | Ramp is real but short; cycle reasserts by 2028 | $4.89 | 3.17% |
| Base | 30% | 25.0% | 1.00 | Guided ramp lands, then normal FPGA cyclicality over the CAP | $8.12 | 3.70% |
| Bull | 25% | 35.0% | 1.10 | Security/control sockets compound with hyperscaler capex | $13.21 | 4.54% |
| Super bull | 15% | 45.0% | 1.25 | Durable AI-infrastructure franchise; SBC leverage finally bites | $21.97 | 5.90% |

- **Probability-weighted: IV@15% $10.28 (−90.3% vs price), IV@12% $14.42, IV@10% $19.13, weighted IRR 4.08%, base-case IRR 3.70%**
- **Tier by numbers: D.** Diagnostics (dcf_numbers.json): OE yield 0.37%, terminal value 24.3% of IV@15%, scenario spread 8.14x, 9.4 months since FY end.
- Method range: the preliminary run (median base $0.4837, engine's backward blend, default probabilities) printed weighted IV@15% $3.58 and weighted IRR 1.63%. The final run — TTM base, growth recalibrated to the actual prints, bullish-skewed probabilities — prints $10.28 / 4.08%. The methods span $3.58–$10.28 of value against a $106 price; every defensible variant is deep Tier D, so the verdict does not depend on which end you pick. Even the single super-bull scenario (45% growth start, 1.25× OE) yields only $21.97 at a 15% discount.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.4 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 CY2026, legs quoted above.
- **BASE_DIVERGENCE** (latest FY $0.12 vs 3-yr median $0.48): both are distorted, in opposite directions. The latest FY is depressed by the SBC step-up ($52,985,000 → $115,613,000) and a capex doubling ($20,985,000 → $42,527,000) landing in the trough-recovery year; the median averages in peak-cycle FY2023 (revenue $737,154,000, OE $179,293,000). The TTM base ($0.3955) is the resolution: current revenue run-rate, full current SBC charge.
- **NI_OCF_DIVERGENCE** (2024, 2026): no hidden one-off — the gap is SBC plus D&A, both non-cash addbacks in OCF. FY2024: net income $61,131,000 vs OCF $140,876,000, with SBC $52,985,000 and D&A $19,300,000 (financials_history.csv). FY2025: net income $3,084,000 vs OCF $175,107,000, with SBC $115,613,000 and D&A $19,900,000. The divergence is precisely why the OCF-only view flatters this company; the conservative OE deducts SBC in full, so the base is not contaminated — but it does flag that GAAP profitability is far weaker than cash flow suggests.
- **OE_VOLATILE** (OE/share range >3x over 5 years): real cyclicality, not noise — FPGA demand peaked in FY2023 and collapsed in 2024. Handled with 30% combined weight on bear/super-bear and by refusing to extrapolate either the peak (median base) or the trough (latest FY).
- **LOW_OE_YIELD** (base OE yield 0.4%): conceded and central to the verdict — at $106 the price is a pure growth claim. The final run grants the growth (25% base start, 45% super-bull) and the stock still returns 4.08% weighted. The fragility cuts against the price, not against the tier.
- **WIDE_SCENARIO_SPREAD** (super-bull IV 8.1x super-bear): real — outcomes genuinely range from "cyclical niche" to "AI-infrastructure franchise." Confidence is set to low, and the verdict is sized to the conservative end — which changes nothing here, since even the super-bull end is Tier D at this price.

## My thoughts / overlay
- The business inflection is real: revenue +62.2% YoY, guidance raised, AI-server security/control sockets are a genuine structural seat. None of that is the question. The question is what $106 pays for $0.3955/share of SBC-charged owner's earnings — roughly 268x the TTM base. The DCF would need the super-bull path to be several times better than modeled before 15% is even visible.
- The SBC trajectory is the quiet killer: $53.0M → $115.6M → $143.6M TTM while revenue first fell, then recovered. If SBC keeps compounding faster than OCF, OE/share growth will undershoot every scenario start above, which are already generous relative to history (OE/share CAGR 2y is −68.84% on the filed series).
- Balance sheet: no HIGH_NET_DEBT or BIG_NET_CASH flag fired, and the extracted latest-FY series shows cash of $133,886,000 with no debt figures reported — the balance sheet is not the risk here; the price is.
- Price that clears 15%: the weighted IV@15% is $10.28 — i.e., the stock would need to fall roughly 90% before the weighted path clears Andrew's hurdle, and even ~$22 only clears 15% on the super-bull path alone. There is no margin-of-safety framing that rescues $106.

## Final verdict
- **Final tier: D** (weighted IRR 4.08% on the v5 final inputs; tier by numbers D, no override — the method range $3.58–$10.28 IV@15% is D under every variant)
- Confidence: **Low** (WIDE_SCENARIO_SPREAD 8.14x, OE yield 0.37%, SBC trajectory unresolved — but note the low confidence attaches to the point estimates, not the tier: the gap to the price is ~10x)
- One-liner: Real low-power FPGA franchise (moat 5/10) inflecting on AI-server demand, but SBC-charged owner's earnings are $0.40/share against a $106 price — weighted IRR 4.1%, IV@15 $10.28; clears 15% only near ~$10.
