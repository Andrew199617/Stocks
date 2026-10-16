# TOST — Toast, Inc.
v5 run, 2026-10-16. All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.py output, or financials_history.csv — none are recomputed. Market cap $19.56B at $32.22 (nasdaq_quote_api) — in scope under $40B.

## What it is
Cloud platform purpose-built for restaurants: point-of-sale, payment processing, online ordering, kitchen display, payroll, loyalty/marketing, and lending (Toast Capital). Revenue is mostly payment processing (fintech solutions) plus subscriptions, and scales with Gross Payment Volume across ~180,000 locations (Q2 2026). US restaurant-POS leader by depth; competitors are Square (Block), Clover (Fiserv), Lightspeed, Shift4 and legacy NCR/Oracle systems.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** revenue $6,153M; net income $342M; operating cash flow $661M; capex $53M; SBC $242M (always a real cost).
- **Conservative owner's earnings FY2025: $366M = $0.60/share** (base_oe_latest_per_share $0.6030).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $267M — same order as the conservative figure; the conservative OCF-based figure is used throughout.
- OE positive only **2 of the last 5 fiscal years** — Toast crossed into profitability in FY2024–25; FY2023 OE was negative. This is an inflection story, not a long cash-compounding history.
- Balance sheet: the engine reports net debt as null (no debt series was tagged for the latest period); cash at FY2025 was $1,353M per financials_history.csv. No leverage concern is visible in the filed data used, and no net-debt figure is asserted beyond that.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $661,000,000 − prior YTD $302,000,000 + current YTD $276,000,000 = **TTM $635,000,000**
- Capex: FY $53,000,000 − prior YTD $25,000,000 + current YTD $31,000,000 = **TTM $59,000,000**
- SBC: FY $242,000,000 − prior YTD $120,000,000 + current YTD $109,000,000 = **TTM $231,000,000**
- Shares (current-YTD weighted diluted): **596,000,000**
- **TTM OE total $345,000,000 → base OE/share $0.5789** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $0.0897/share — rejected as the base: it is the FY2024 figure, bracketed by a negative-OE FY2023 and the FY2025 inflection year (see BASE_DIVERGENCE below). The TTM base and the latest FY ($0.6030) agree closely, which is the cross-check that the TTM base is the current run-rate, not a spike.

## Moat: 6/10 — moderate-strong, contested
Justification: Toast is the restaurant-vertical leader with real switching costs once POS + payments + back-office modules run a restaurant's daily operations, and it is compounding locations and wallet share (record ~9,500 net adds in Q2 2026, ARR +25% YoY). But the customer base is fragile SMB restaurants, payments take-rates are contestable, and Square/Clover/Lightspeed/Shift4 are discounting hardware and software aggressively to win locations — the moat is real but must be re-defended location by location.
- FOR: Restaurant-specific depth no horizontal rival matches (kitchen display, table management, tip handling, online ordering in one stack)
- FOR: Switching costs — POS + payments + payroll/loyalty modules are mission-critical and painful to rip out mid-operation
- FOR: Scale and data across ~180,000 locations feeding product/AI features (e.g. Toast IQ) and underwriting
- FOR: Expanding wallet per location — fintech, payroll, marketing and new verticals (retail, enterprise, international) raise revenue per site
- AGAINST: Payments processing is commoditizing; rivals (Square, Shift4, Clover) are discounting hardware/software to buy share
- AGAINST: Customer base is SMB restaurants — high failure/churn rates cap durability of the installed base
- AGAINST: No consumer-side network effect; diners don't choose restaurants by POS vendor
- AGAINST: Pricing resentment — processing-fee increases and add-on stacking push operators to price-shop alternatives
- A 6 gives CAP = 9.8 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 9.8 years, 15-year projection.

## DCF — v5 final run (2026-10-16)
Growth inputs: engine blend g_blend 31.09% (rev CAGR 5y 49.54%, rev CAGR 3y 31.09%, latest rev YoY 24.05%), share-count adjustment −5pp for historical dilution → g_base 26.09%. Default offsets (−12/−5/0/+5/+12pp) and OE multipliers (0.75/0.90/1.00/1.10/1.25) kept; probabilities kept at the 10/25/30/25/10 defaults — execution is strong but the price already demands it, so no bullish skew was earned.
**Sanity check vs actual prints:** Q2 2026 revenue grew 23.1% YoY and management guided FY2026 recurring gross profit growth of 23–25% (Q3 guide 22–24%). The base-case OE growth start of 26.09% sits slightly above the revenue prints — justified in writing: OE grows off a thin base (the engine's OE yield on the TTM base is only 1.80%) with documented operating leverage — SBC is falling as a share of recurring gross profit and H1 2026 buybacks are now shrinking the share count, so OE/share can outgrow revenue for a period. The super-bull start of 38.09% is likewise an OE/share figure, not a revenue claim, and sits well below the earnings growth Toast just printed (Q2 2026 net income roughly doubled YoY). The super-bear start of 14.09% still assumes growth — appropriate for a business adding locations at a record pace; the bear cases bite through the 0.75/0.90 OE multipliers instead.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | 14.09% | 0.75 | Discounting war + restaurant downturn compress take rates and OE | $5.96 | 5.14% |
| Bear | 25% | 21.09% | 0.90 | Growth decays to the teens; margin expansion stalls | $9.73 | 6.92% |
| Base | 30% | 26.09% | 1.00 | Low-20s revenue growth with steady operating leverage over the CAP | $13.45 | 8.54% |
| Bull | 25% | 31.09% | 1.10 | Location adds + wallet share keep compounding; SBC leverage continues | $18.36 | 10.49% |
| Super bull | 10% | 38.09% | 1.25 | Durable category-killer path; new verticals and AI products ramp | $28.10 | 13.79% |

- **Probability-weighted: IV@15% $14.46 (−55.12% vs price), IV@12% $20.39, IV@10% $27.15, weighted IRR 8.99%, base-case IRR 8.54%**
- **Tier by numbers: D.** Diagnostics (dcf_numbers.json): OE yield 1.80%, terminal value 25.09% of IV@15%, scenario spread 4.72x, 9.49 months since FY end.
- Even the super-bull scenario at a 10% weight produces a 13.79% IRR — below the 15% hurdle. The price that clears 15% on the weighted path is the weighted IV@15% itself: **$14.46**. There is no margin of safety at $32.22; the stock needs to roughly halve before this DCF pays a 15% buyer.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.49 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, inputs quoted above.
- **BASE_DIVERGENCE** (latest FY OE/share $0.60 vs 3-yr median $0.09): the median is the distorted one — the last-3-FY window contains negative-OE FY2023 and first-profit FY2024 ($0.0897 is literally the FY2024 value). Latest FY ($0.6030) and TTM ($0.5789) corroborate each other, so the TTM base is used and the median is retained only in the reporting.
- **NI_OCF_DIVERGENCE** (2023, 2024, 2025): explained by the SBC non-cash addback, not a one-off. From financials_history.csv: FY2023 net income −$246M vs OCF $135M with SBC $277M; FY2024 net income $19M vs OCF $360M with SBC $253M; FY2025 net income $342M vs OCF $661M with SBC $242M. In each year SBC alone exceeds the NI–OCF gap. The conservative OE deducts SBC in full, so the divergence does not contaminate the base.
- **BASIS_BREAK_SUSPECT** (>60% revenue jump in the last 5 years): the jump is FY2021 revenue ($823M → $1,705M) — post-COVID reopening plus IPO-era location expansion, organic rather than a divestiture, big M&A, or restatement; no basis break was identified in the filed history. Accordingly the 5-yr revenue CAGR (49.54%) is not trusted as a forward input — the blend's median lands on the 3-yr CAGR (31.09%) and the scenario starts were sanity-checked against current 23–24% prints above.
- **DILUTION** (share count +5.84%/yr): the −5pp growth adjustment is already applied in g_base. Trend check: the direction has flipped — TTM diluted shares are 596M vs 607M for FY2025, management reported repurchasing over 19M shares for $486M year-to-date through Q2 2026, and SBC fell to 10% of recurring gross profit from 14% a year earlier. SBC is still large in absolute terms (TTM $231M vs TTM OE $345M) and remains fully deducted; the flag is resolved as a historical headwind now reversing, not ignored.
- **LOW_OE_YIELD** (1.80% on the TTM base): real and decisive — at $32.22 the valuation rests almost entirely on growth and margin expansion. It cuts against the price here: even granting the bull-case growth path, the weighted IRR is 8.99%.
- **WIDE_SCENARIO_SPREAD** (4.72x): real — the outcome range is wide. Confidence is set to medium (never high with this flag), and the verdict is sized to the conservative end; note the tier is D under both defensible bases (see method range), so the spread does not change the verdict.

## My thoughts / overlay
- Method range: the preliminary run on the engine's median base ($0.0897/share) gave a weighted IRR of 3.52% and weighted IV@15% of $2.05; this final TTM-base run gives 8.99% / $14.46. Both are Tier D. Unlike names where the base choice flips the verdict, here every defensible input set lands in D — and even the super-bull scenario (13.79% IRR) fails the 15% hurdle at $32.22. The D is robust, not an artifact.
- Quality is not the debate: 23% revenue growth, ARR +25%, record location adds, raised FY2026 guidance (adj. EBITDA $805–825M), SBC discipline improving, buybacks now offsetting dilution. The debate is purely price: the market is paying today for the bull path with no discount for the bear paths.
- Watch items: hardware/software discounting vs Square and Shift4 (take-rate pressure), Q2 2026 free cash flow dipped on a deliberate hardware-inventory build (management expects conversion to improve in H2 2026), restaurant-industry health, and whether Toast Capital credit losses (credit loss expense is a recurring line in the cash-flow statement) stay contained in a downturn.
- Margin of safety: none at $32.22 on this method. The 15%-clearing price on the weighted path is $14.46; even the bull scenario's IV@15% ($18.36) sits far below the price.

## Final verdict
- **Final tier: D** (weighted IRR 8.99% on the v5 final TTM-base inputs; Tier D also on the median base — no tier override)
- Confidence: **Medium** (high on the filing-derived OE base and on the verdict's robustness across bases; the scenario spread is 4.72x, so no single-path claim is high-confidence)
- One-liner: High-quality restaurant platform, moat 6/10, growing ~23% with a real profit inflection — but at $32.22 even the super-bull case returns only 13.8%; weighted IRR 9.0%, IV@15 $14.46, clears 15% only near ~$14.46.
