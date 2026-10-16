# BRO — Brown & Brown, Inc.
v5 run, 2026-10-15. In scope (market cap $21.278B at $67.98, nasdaq_quote_api).

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.py output, financials_history.csv, or the cited research — none are recomputed.

## What it is
One of the largest US insurance brokerages: retail brokerage plus specialty/wholesale distribution (including E&S lines). The model is a decentralized roll-up — hundreds of acquired agencies run locally, growth historically delivered by continuous M&A on top of a recurring renewal-commission base. In 2025 it closed its largest deal, Accession (RSC Topco / Risk Strategies), funded with debt and a large equity issuance.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** revenue $5,902M; net income $1,054M; operating cash flow $1,450M; capex $68M; SBC $93M.
- **Conservative owner's earnings FY2025: $1,289M = $4.12/share** (latest FY OE/share, key_numbers.md)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $1,254M — close to the conservative figure, which raises confidence in the base. Capex is structurally tiny for a broker; the OCF-based definition is the cleaner one and is used throughout.
- OE positive 5 of the last 5 fiscal years. Net debt $6.534B (key_numbers.md) — see HIGH_NET_DEBT below.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $1,450,000,000 − prior YTD $538,000,000 + current YTD $608,000,000 = **TTM $1,520,000,000**
- Capex: FY $68,000,000 − prior YTD $32,000,000 + current YTD $38,000,000 = **TTM $74,000,000**
- SBC: FY $93,000,000 − prior YTD $52,000,000 + current YTD $49,000,000 = **TTM $90,000,000**
- Shares (current-YTD weighted diluted): **335,000,000**
- **TTM OE total $1,356,000,000 → base OE/share $4.05** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $3.49/share — rejected as the base because it predates the Accession step-change in scale; the TTM base already carries the full post-deal share count (335M vs 313M in FY2025), so it is not flattered by the deal. The latest-FY figure ($4.12) and the TTM figure ($4.05) bracket each other closely, which supports the TTM choice.

## Moat: 5/10 — moderate / narrow
Justification: recurring renewal commissions, carrier scale and contingent-commission leverage, and a proven decentralized M&A platform — but a people business with low formal switching costs, cyclical pricing exposure, and growth bought with debt and equity rather than earned organically.
- FOR: Recurring renewal commission base with high client retention; carrier scale and contingent (profit-sharing) commission leverage; proven decentralized acquisition platform with a decades-long track record; broad specialty / wholesale (E&S) distribution position; asset-light model — minimal capex, strong cash conversion.
- AGAINST: People business — producers can leave and take accounts (a startup competitor formed by departed employees had taken ~$31M of annualized revenue by Q1 2026; litigation ongoing); low formal switching costs for clients; organic growth stalling (2.8% in 2025, −0.3% ex-contingents in H1 2026) with soft P&C pricing and cat-property rate declines; growth depends on continuous M&A funded with debt and equity; Accession integration risk and margin dilution, with Q2 2026 interest expense roughly double the prior year.
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — v5 final run (2026-10-15)
**Growth recalibration (written reason):** the engine's blended growth is 17.95% and g_base 14.05%, but those filing-history components (rev CAGR 5y 17.70%, 3y 18.21%, latest YoY 22.83%, OE/share CAGR 2y 16.53%) are acquisition accounting, not organic compounding — they straddle the Accession step-change. The organic prints are what the existing business actually earns: +10.4% organic in 2024, +2.8% in 2025, −0.3% ex-contingents in H1 2026 (+1.6% with contingents), Q2 2026 organic −0.7%, with management guiding 2H 2026 organic ex-contingents to Retail 1.5–2.5% / Specialty 2–4%. Per-share growth also has to absorb the deal share issuance. Scenario starts were therefore set via offsets (−0.1405 / −0.1005 / −0.0605 / −0.0205 / +0.0295 vs g_base) to 0 / 4 / **8** / 12 / 17% — the base case assumes a normal M&A cadence resumes on top of low-single-digit organic growth; even the super-bull start (17%) sits below the latest reported revenue YoY (+22.83%), with the written reason that the reported figure is deal-driven, not a run-rate. Probabilities 10/30/30/20/10 (skewed bear-ward vs defaults for the leverage and the organic stall); OE multipliers at defaults 0.75/0.90/1.00/1.10/1.25. Price $67.98.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -0.0% | 0.75 | Soft pricing cycle deepens, organic stays negative, debt service bites | $22.42 | 6.53% |
| Bear | 30% | 4.0% | 0.90 | Organic low-single-digit, M&A throttled by leverage | $31.79 | 8.40% |
| Base | 30% | 8.0% | 1.00 | Modest organic recovery + normal acquisition cadence | $41.69 | 10.34% |
| Bull | 20% | 12.0% | 1.10 | Accession synergies land, organic re-accelerates | $54.06 | 12.63% |
| Super bull | 10% | 17.0% | 1.25 | Roll-up compounding resumes at historical pace | $75.32 | 16.17% |

- **Probability-weighted: IV@15% $42.63 (−37.3% vs price), IV@12% $57.06, IV@10% $73.20, weighted IRR 10.55%, base-case IRR 10.34%**
- **Tier by numbers: C.** Diagnostics (key_numbers.md): OE yield 5.95%, terminal value 19.5% of IV@15%, scenario spread 3.36x, net debt 5.16x normalized OE, 9.5 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.5 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, quoted above, applied via `--ttm`.
- **DILUTION** (share count +3.91%/yr): the trend is deal equity, not SBC creep — SBC is $90M TTM against $1,520M TTM OCF, while the weighted share count rose ~41M to ~334M in Q2 2026 on shares issued for Accession. The growth blend already deducts −3.91pp for the trend, the TTM base uses the full post-deal 335M share count, and all scenario growth starts are per-share rates set well below the filing-history blend.
- **SECTOR_MODEL_MISMATCH** (Finance): noted and confidence graded **low** as required. Mitigant, stated for the record: BRO is a broker, not a balance-sheet insurer or bank — it takes no underwriting risk, capex is real and tiny, and the OE construction fits it better than most Finance names; the flag still caps confidence because fiduciary balances and contingent-commission variability sit outside the standardized model.
- **HIGH_NET_DEBT** (net debt $6.534B, 5.16x normalized OE): the debt funded Accession; Q2 2026 interest expense was roughly double the prior-year quarter. Folded into the verdict explicitly: probabilities skewed bear-ward (40% on bear-or-worse), bear/super-bear OE multipliers at 0.90/0.75, and the final tier is read off the conservative end. Levered OE is exactly what the bear cases stress, and both sit far below the price.
- **WIDE_SCENARIO_SPREAD** (preliminary run 4.43x; final run 3.36x, below the flag threshold): the spread is real — outcomes hinge on whether bought growth resumes. Confidence is low regardless (sector flag + leverage), and the verdict is sized to the conservative end.

## My thoughts / overlay
- The central fact: the filing history says ~18% growth, the organic business says ~0–3%. A standardized DCF fed the filing history (preliminary run, defaults: weighted IRR 11.87% on the median base) still landed in Tier C; recalibrating growth to per-share, post-deal reality and moving to the higher TTM base lands at 10.55% — same tier. The method range across defensible inputs is narrow here (C either way); what changes is how far below the hurdle the name sits.
- Quality is not the problem: 5/5 OE-positive years, the two OE definitions agree, capex is negligible, and the commission base recurs. The problem is price vs. bought growth: at $67.98 the market is paying for the historical roll-up pace to continue per-share, while the company just issued ~41M shares and levered to 5.16x normalized OE to buy its latest leg of growth, and organic growth has stalled for two consecutive quarters.
- Q2 2026 color consistent with that read: total revenue +30.4% YoY (deal-driven), adjusted EPS +3.9%, adjusted EBITDAC margin 35.7% vs 36.7% a year earlier.
- Hurdle math: the stock clears 15% at the weighted IV@15% of **$42.63** — roughly 37% below the current price. Even the super-bull IV@15% ($75.32) is only modestly above the price, so a buyer here needs the bull path just to clear the hurdle with any margin of safety.

## Final verdict
- **Final tier: C** (weighted IRR 10.55% on the v5 final inputs; no tier override)
- Confidence: **Low** (SECTOR_MODEL_MISMATCH grading rule, high net debt, and an outcome range driven by M&A execution rather than organic compounding)
- One-liner: Quality insurance-brokerage roll-up, moat 5/10 — but at $67.98 it does not clear 15% on filing-derived TTM numbers (weighted IRR 10.5%, IV@15 $42.63); the historical growth in the filings is bought, not organic, and the Accession debt load stresses the bear cases. Clears 15% at ~$42.63.
