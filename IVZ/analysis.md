# IVZ — Invesco Ltd.
Engine 5.4.0 run, 2026-10-17. Price $28.20 (nasdaq_quote_api), market cap est. $12.831B — in scope under $40B.

All figures below are copied from dcf_numbers.json, ttm.json, financials_history.csv or fundamentals.json — none are recomputed.

## What it is
Global asset manager: ETFs and index (flagship Invesco QQQ, ~$498.9B AUM at Sep 2026), fundamental equities and fixed income, private markets, global liquidity, and a China JV. Revenue is management fees on AUM — ending AUM was $2.5T at Q2 2026, up 23.4% YoY, with a record $45.1B of net long-term inflows in the quarter (12th consecutive quarter of inflows; $67B in H1 2026, 7% annualized organic growth). Q2 2026 adjusted EPS $0.71 (+97.2% YoY), adjusted operating margin 37.5% vs 31.2% a year earlier. QQQ converted from a unit investment trust to an open-end ETF in Dec 2025, improving Invesco's retained fee economics; BlackRock has since launched IQQ, a Nasdaq-100 rival at a 10bp net fee, ending Invesco's exclusivity.

## Owner's earnings
**FY2025 (10-K via EDGAR):** operating cash flow $1,525,300,000; capex $84,300,000; SBC $80,000,000.
- **Conservative owner's earnings FY2025: $1,361,000,000 = $2.99/share** (latest FY OE/share in dcf_numbers.json).
- Maintenance version FY2025 (NI + D&A − min(capex, D&A) − ΔNWC): −$103,200,000 — meaningless here: FY2025 net income was −$174,800,000 because of non-cash impairments (operating income −$695,700,000), which never touch operating cash flow. The OCF-based conservative definition is the usable one for this filer.
- OE positive 5 of the last 5 fiscal years. OE/share history: 2021 $1.78, 2022 $0.88, 2023 $2.24, 2024 $2.22, 2025 $2.99 — volatile, market-linked.
- Net debt $787,600,000 (total LongTermDebt basis), 0.77x normalized OE — modest. The Q2 2026 release reports net debt was reduced by more than $450M during that quarter and buybacks rose to $50M.

**Base used = the engine's normalized base: median of the last 3 FY OE/share = $2.24/share** (2023 $2.24, 2024 $2.22, 2025 $2.99). The TTM figure was computed and rejected as the base — see STALE_FY below.

**TTM check (ttm.py, through Q2 2026):**
- OCF: FY $1,525,300,000 − prior YTD $463,300,000 + current YTD $946,800,000 = **TTM $2,008,800,000**
- Capex: FY $84,300,000 − prior YTD $40,900,000 + current YTD $44,700,000 = **TTM $88,100,000**
- SBC: FY $80,000,000 − prior YTD $38,900,000 + current YTD $65,300,000 = **TTM $106,400,000**
- Shares (current-YTD weighted): **451,200,000**
- **TTM OE total $1,814,300,000 → $4.02/share** — not used as the base: TTM OCF of $2.009B exceeds every fiscal year in the filed history (FY2025's $1.525B is the decade's high) and sits well above the adjusted-earnings run-rate implied by Q2 2026 adjusted EPS of $0.71; asset-manager OCF carries seed/co-investment and working-capital swings that are not recurring fee earnings. It is retained as the top of the method range below.

## Moat: 5/10 — moderate/narrow
Evidence first: the roic_proxy series in fundamentals.json runs 10.0% (2016), 11.9% (2017), 9.5% (2018), 4.1% (2019), 4.6% (2020), 9.0% (2021), 6.3% (2022), −2.3% (2023), 4.3% (2024), −4.2% (2025) — never durably above the cost of capital, and negative in the impairment years. Gross margin is not filed (asset manager, no COGS line); GAAP operating margin swung from +25.9% (2021) to −10.9% (2025) on impairments, while the adjusted operating margin reached 37.5% in Q2 2026. That ROIC record caps the moat at moderate.
- FOR: QQQ franchise — ~$498.9B AUM and the 2nd-most-traded US ETF; liquidity and adviser-workflow network effects a cheaper rival cannot quickly replicate. Scale — $2.5T ending AUM with global distribution. Product breadth — private markets $134.9B, China JV $166.3B, fundamental fixed income $307.9B. Flow momentum — 12 straight quarters of net long-term inflows, record $45.1B in Q2 2026. Operating leverage — adjusted operating margin 37.5% and expanding.
- AGAINST: ROIC history above (the franchise has not compounded capital well). Structural fee compression and the passive shift. Nasdaq-100 exclusivity ended — BlackRock IQQ at a 10bp net fee. Sub-scale vs BlackRock/Vanguard/State Street. Market beta: 5-yr revenue CAGR is only 0.7%, so fees fall mechanically in a drawdown. Goodwill-heavy balance sheet with recurring impairments.
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — engine 5.4.0 final run (2026-10-17)
Growth sanity check: the engine's blended start is 3.77% (rev CAGR 5y 0.74%, rev CAGR 3y 1.78%, latest rev YoY 5.11%, OE/share CAGR 2y 15.55%). Recent prints are hotter — Q2 2026 net revenues +20.3% YoY and AUM +23.4% — but those are market-appreciation-driven, not organic run-rate: H1 organic growth was 7% annualized and the 5-yr revenue CAGR is 0.7%. A base start of 3.77% is therefore defensible without a recalibration; the bull (8.77%) and super-bull (15.77%) starts bracket the current print momentum, and no start needs a "below the latest print" exception because asset-manager revenue prints are not a stable growth rate. Probabilities shifted toward the bear end (15/30/25/20/10 vs the 10/25/30/25/10 default) per the OE_VOLATILE flag; offsets and OE multipliers are the defaults.

| Scenario | Prob | Growth start | OE mult | IV@15 | IRR |
|---|---|---|---|---|---|
| Super bear | 15% | −8.23% | 0.75 | $8.79 | 5.97% |
| Bear | 30% | −1.23% | 0.90 | $14.15 | 8.62% |
| Base | 25% | 3.77% | 1.00 | $19.37 | 11.12% |
| Bull | 20% | 8.77% | 1.10 | $26.20 | 14.17% |
| Super bull | 10% | 15.77% | 1.25 | $39.66 | 19.37% |

- **Probability-weighted: IV@15% $19.61 (−30.5% vs the $28.20 price), IV@12% $26.00, weighted IRR 11.28%, base-case IRR 11.12%**
- **Tier by numbers: C.** Bear tier D (8.6%), bull tier C (14.2%). Hurdle prices: clears 15% at $19.61, 20% at $13.86, 25% at $10.69. Diagnostics: OE yield 7.94%, terminal value 18.5% of IV@15%, scenario spread 4.51x, net debt 0.77x normalized OE, 9.5 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.5 months ago): ttm.py was run (legs quoted above). TTM OE/share $4.02 was rejected as the base — TTM OCF $2.009B exceeds every filed fiscal year and the adjusted-earnings run-rate, i.e. it carries non-recurring cash swings; the normalized median base is used and the TTM variant is reported as the method-range top.
- **OE_VOLATILE** (OE/share spans >3x over 5 years: $0.88 to $2.99): real — AUM-fee earnings are market-cyclical. Handled by the median base and by shifting scenario weight to the bear end (45% on bear-or-worse).
- **NI_OCF_DIVERGENCE** (2023, 2024, 2025): the one-off is non-cash impairment. GAAP net income was −$333.7M in 2023 and −$174.8M in 2025 with operating income of −$434.8M and −$695.7M, while OCF stayed $1.30B and $1.53B — impairment charges hit earnings, not cash. The OCF-based OE base is therefore the cleaner series and is not contaminated by the divergence.
- **SECTOR_MODEL_MISMATCH** (Finance): agreed — an OE/capex DCF fits an asset manager poorly (earnings are a fee yield on market-valued AUM, and the balance sheet carries consolidated-product noise). Confidence is low and the verdict is sized to the bear end.
- **WIDE_SCENARIO_SPREAD** (4.51x): real — the outcome range is genuinely wide for a market-beta earnings stream. Confidence is low, never high.
- **TIER_BAND** (bear D 8.6% vs bull C 14.2%): the verdict spans tiers; sized to the bear end — even the bull case (14.2%) does not clear the 15% hurdle at $28.20.

## My thoughts / overlay
- The honest headline is the method range: on the normalized median base the weighted IRR is 11.28% (Tier C, IV@15% $19.61); on the TTM base of $4.02/share the same scenario set prints weighted IRR 18.0% and IV@15% $35.20 (Tier B). The truth depends on how much of the TTM OCF surge is recurring fee earnings — the filed history says most of it is not.
- What is genuinely improving: flows (record H1 inflows), adjusted margins (37.5%), deleveraging, buybacks, and the QQQ open-end conversion. What is not: a decade of single-digit-to-negative ROIC and a fee base that a market drawdown cuts automatically.
- Balance sheet: net debt $787.6M on the filing tags (0.77x normalized OE) is not a constraint; goodwill and intangibles are the recurring impairment source, not leverage.

## Final verdict
- **Final tier: C** (weighted IRR 11.28% on the normalized base; method range C to B)
- Confidence: **Low** (sector model mismatch + wide scenario spread, per the flags)
- One-liner: Decent-quality asset manager with a narrow QQQ/scale moat (5/10), but at $28.20 it does not clear the 15% hurdle on the normalized base — weighted IRR 11.3%, weighted IV@15% $19.61; it clears 15% only at ~$19.61 or below.
