# ULS — UL Solutions Inc.
Engine 5.4.0 run, 2026-10-17. All figures below are copied from dcf_numbers.json, ttm.json, financials_history.csv, or fundamentals.json — none are recomputed.

## What it is
Global testing, inspection and certification (TIC) company — the for-profit arm of the UL safety-science enterprise, founded 1894, IPO April 2024. SIC 8734 (Services-Testing Laboratories). Segments (FY2025 revenue, segments.json): Industrial $1,341M (43.9%), Consumer $1,319M (43.2%), Software and Advisory $393M (12.9%). Controlled company: UL Standards & Engagement (the nonprofit parent) beneficially owned 69.0% of the common stock and 95.7% of combined voting power as of Dec 31, 2024 (10-K risk disclosure, via search) — public holders are minority riders on a controlled register. Price $73.31 (nasdaq_quote_api), market cap est. $14,881,930,000 — in scope under $40B.

## Owner's earnings
**FY2025 (10-K via EDGAR, financials_history.csv):** operating cash flow $600,000,000; capex $197,000,000; SBC $47,000,000 (always a real cost).
- **Conservative owner's earnings FY2025: $356,000,000 = $1.7537/share** (base_oe_latest_per_share).
- Maintenance version FY2025: $263,000,000 — below the conservative figure, driven by the ΔNWC leg (+$62,000,000 in the history file); FY2024 ran the other way (maintenance $372,000,000 vs conservative $264,000,000). The two definitions bracket each other across years; neither changes the verdict at this price.
- OE positive 4 of the last 4 fiscal years (oe_positive_years_of_last_5: 4/4 — history starts FY2022). OE/share history: $1.04 (2022), $1.26 (2023), $1.3134 (2024), $1.7537 (2025).
- Net debt $196,000,000 (LongTermDebtNoncurrent+LongTermDebtCurrent basis), lease liabilities $192,000,000 — net debt is 0.53x normalized OE (diagnostics). Balance sheet is not the story.
- History caveat: SBC is filed as $0 in FY2022–FY2023 and only appears from FY2024 ($23,000,000, then $47,000,000, TTM $61,000,000) — the early-year OE figures carry no SBC charge, so early OE/share is flattered. The TTM base actually used carries the full current SBC, so the base is not flattered.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $600,000,000 − prior YTD $301,000,000 + current YTD $379,000,000 = **TTM $678,000,000**
- Capex: FY $197,000,000 − prior YTD $93,000,000 + current YTD $138,000,000 = **TTM $242,000,000**
- SBC: FY $47,000,000 − prior YTD $21,000,000 + current YTD $35,000,000 = **TTM $61,000,000**
- Shares (current-YTD weighted diluted): **204,000,000**
- **TTM OE total $375,000,000 → base OE/share $1.8382** (base_source: ttm_json)
- The engine's normalized base (median of last 3 FY) is $1.3134/share — lower, dragged by FY2024; the TTM base is the more current and more generous choice, and the verdict is Tier D on either base (preliminary run on the median base: weighted IRR 4.93%, IV@15% $13.39).

## Moat: 7/10 — strong
Justification: the UL mark and accreditation position make certification close to a market-access requirement in core North American electrical/fire-safety categories, and the measured economics back it — but global TIC share is only ~7%, larger rivals (SGS, Bureau Veritas, Intertek, TÜV) contest every category, and growth is structurally mid-single-digit.
- FOR: Regulatory/accreditation moat — the UL mark is embedded in codes, regulator and retailer requirements; re-certification switching costs for manufacturers mid-product-cycle; ROIC proxy (fundamentals.json) stayed well above any plausible cost of capital — 23.6% (2023), 28.5% (2024), 26.3% (2025), with 2022's 44.0% flattered by the pre-IPO capital base; gross margin high and rising — 47.9% (2022), 47.9% (2023), 48.5% (2024), 49.5% (2025) — with operating margin expanding 13.7% → 17.1% over 2023–2025, i.e. demonstrated pricing power; demand tied to non-discretionary safety regulation and to electrification / energy-storage / AI-data-center build-outs.
- AGAINST: Only ~7% share of the global TIC market (2024, industry analysts via search) and smaller than SGS / Bureau Veritas at global scale; standards-setting sits with the nonprofit parent, not the listed company; demand follows customer product-development cycles (tariff/macro freezes hit certification volumes, as in the Q2 2025 slowdown); virtual/AI-assisted testing could commoditize low-complexity work over time; controlled-company governance (ULSE 95.7% voting power at Dec 31, 2024) caps minority influence and any takeover premium.
- A 7 gives CAP = 11.1 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 11.1 years, 15-year projection.

## DCF — 5.4 final run (2026-10-17)
Engine blended growth start 6.11% (rev CAGR 5y/3y 6.60%, latest rev YoY 6.38%, OE/share CAGR 2y 17.96%, share-count adjustment −0.50pp on revenue components). Defaults kept throughout — probabilities 10/25/30/25/10, growth offsets −12/−5/0/+5/+12pp, OE multipliers 0.75/0.90/1.00/1.10/1.25 — because the evidence is a steady mid-single-digit grower with expanding margins, not an inflection name.
**Growth-start sanity check (mandatory):** scenario starts are OE/share growth, not revenue growth. Recent prints: FY2025 revenue +6.4%, Q2 2026 reported revenue +5.2% with organic growth +6.6% (EHS-software divestiture dilutes the reported line), FY2026 guidance mid-single-digit organic growth with Adjusted EBITDA margin ~27% (Q2 2026 release, Business Wire). Base start 6.11% sits on the revenue prints; bull 11.11% and super-bull 18.11% sit above revenue growth and are justified only as OE/share growth via margin expansion — Q2 2026 Adjusted Net Income rose 17.3% YoY and the filed 2-yr OE/share CAGR is 17.96%. Super-bear −5.89% prices a product-cycle freeze. No start contradicts a print without that written reason.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | −5.89% | 0.75 | Product-development freeze; certification volumes fall | $7.64 | 3.59% |
| Bear | 25% | 1.11% | 0.90 | Low-single-digit stall; capex stays elevated | $12.70 | 4.62% |
| Base | 30% | 6.11% | 1.00 | Mid-single-digit growth, margins hold | $17.87 | 5.70% |
| Bull | 25% | 11.11% | 1.10 | Margin expansion compounds OE/share at low-double digits | $24.93 | 7.16% |
| Super bull | 10% | 18.11% | 1.25 | Filed 2-yr OE/share CAGR persists for years | $39.51 | 9.91% |

- **Probability-weighted: IV@15% $19.48 (−73.4% vs price), IV@12% $26.22, IV@10% $33.79, weighted IRR 6.10%, base-case IRR 5.70%**
- **Tier by numbers: D — and bear, base, bull and super-bull are all D too.** Even the super-bull IV@15% ($39.51) is barely half the $73.31 price.
- Diagnostics: OE yield 2.51%, terminal value 20.2% of IV@15%, scenario spread 5.17x, net debt 0.53x normalized OE, 9.5 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (latest FY ended ~10 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026 (legs quoted above), passed with `--ttm`.
- **NI_OCF_DIVERGENCE** (NI vs OCF >40% apart in 2023 and 2025): explained by non-cash D&A, not a one-off inflating cash. 2023: NI $260,000,000 vs OCF $467,000,000 — D&A was $154,000,000. 2025: NI $325,000,000 vs OCF $600,000,000 — D&A was $188,000,000. The conservative OE starts from OCF but then subtracts full capex ($215,000,000 in 2023, $197,000,000 in 2025 — roughly D&A-sized), so the D&A add-back does not leak into the base. The separate Q2 2026 net-income spike (+161.9% YoY) is the $191,000,000 gain on the EHS-software divestiture (closed April 1, 2026; Q2 2026 release) — a non-operating gain that sits in net income, not in OCF, so it does not touch the OE base either.
- **WIDE_SCENARIO_SPREAD** (super-bull IV 5.17x super-bear): real — it is mostly the arithmetic of a 2.51% OE yield, where small growth differences compound into wide IV ratios. Confidence is capped at medium per the rule; note the spread does not create verdict uncertainty here, because every scenario tier is D.
- **LOW_OE_YIELD** (preliminary run, 1.79% on the median base): on the TTM base the yield is 2.51% — the substance stands: at $73.31 the valuation rests almost entirely on future growth, which is exactly why no scenario clears even 10%.

## My thoughts / overlay
- This is a quality-versus-price case, not a quality debate. The franchise evidence (ROIC proxy 24–28%, gross margin ~49.5% and rising, regulatory embedding) supports moat 7 — and the stock still needs to fall to the $19.48 weighted IV@15% to clear a 15% hurdle, or to $13.50 / $10.25 to clear 20% / 25%. The market price is roughly 3.8x the weighted IV@15%.
- Method range: median-base preliminary run gave weighted IRR 4.93% / IV@15% $13.39 (Tier D); the TTM-base final gives 6.10% / $19.48 (Tier D). The range is D to D — the method choice moves the IV, not the tier.
- Watch items that could move the base, not the moat: capex guided up to ~8.5% of revenue for FY2026 (vs 6.5% in 2025) to build lab capacity for AI data centers, energy storage and auto electrification — TTM capex already rose to $242,000,000, and if that intensity persists, OE growth trails EPS growth; the EHS divestiture removes a software revenue stream (Risk & Compliance revenue −17.5% reported in Q2 2026, +4.8% organic ex-divestiture); ULSE's controlling stake is a permanent governance discount and a potential overhang if it sells down further.
- Street context (not an input): consensus target $95.88 (MarketBeat, via search) prices the earnings multiple, not owner's earnings — the gap between that and $19.48 IV@15% is the whole finding.

## Final verdict
- **Final tier: D** (weighted IRR 6.10% on the TTM base; every scenario, bear to super-bull, is also D)
- Confidence: **Medium** (capped by WIDE_SCENARIO_SPREAD; tier itself is robust across bases and scenarios)
- One-liner: High-quality TIC franchise, moat 7/10 — but at $73.31 it does not clear 15% (weighted IRR 6.1%, IV@15% $19.48); it clears 15% only at ~$19.48.
