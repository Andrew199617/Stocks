# BALL — Ball Corporation
Engine 5.4.0 run, 2026-10-16. In scope (market cap $17.44B at $63.20, nasdaq_quote_api).

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.json, or fundamentals.json — none are recomputed.

## What it is
The world's largest aluminum beverage-can maker (SIC 3411, Metal Cans): beverage packaging in North & Central America, EMEA, and South America, plus aerosol/other packaging. Pure-play packaging since selling Ball Aerospace to BAE Systems on 2024-02-16 for $5.6B. Q2 2026: global beverage-can volumes +4.3%, comparable operating earnings +7.7%, comparable diluted EPS +14.4% YoY; management reaffirmed 2026 guidance of >10% comparable EPS growth, FCF above $900M, ~3% global volume growth, and ~$800M of shareholder returns.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $1,262M; capex $474M; SBC $28M (always a real cost).
- **Conservative owner's earnings FY2025: $760M = $2.75/share** (base_oe_latest_per_share $2.7539)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $1,098M — above the conservative figure; the OCF-based figure is the cleaner, lower one and is what the engine uses.
- OE positive in only **2 of the last 5 fiscal years**: FY2022 OE/share was −$4.34 (OCF collapsed to $301M against $1,651M capex in the capacity build-out) and FY2024 was −$1.40 (see NI_OCF_DIVERGENCE below). This is a cyclical, capex-heavy OE stream, not a steady compounder.
- Net debt $5.80B (LongTermDebtAndCapitalLeaseObligations + DebtCurrent basis), plus lease liabilities $361M.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $1,262M − prior YTD −$333M + current YTD −$169M = **TTM $1,426M**
- Capex: FY $474M − prior YTD $177M + current YTD $302M = **TTM $599M**
- SBC: FY $28M − prior YTD $18M + current YTD $13M = **TTM $23M**
- Shares (current-YTD weighted diluted): **267,271,000**
- **TTM OE total $804M → base OE/share $3.01** (base_source: ttm_json)
- The engine's normalized base (median of last 3 FY) is $2.48/share — it averages in the distorted FY2024 (−$1.40, aerospace-sale tax year). The TTM base is more current and avoids that distortion; it is used, and the median is retained here for the method range.

## Moat: 5/10 — moderate / narrow
Justification: Scale leadership in an oligopoly with long-term customer contracts and metal pass-through, but ROIC has not stayed well above the cost of capital — fundamentals.json roic_proxy ran 8.8% (2020), 10.1% (2021), 8.3% (2022), 8.3% (2023), with 2024–25 not computed (operating-income tag absent in the filed history used). Gross margin was ~15.5–16.0% in the last years fundamentals.json computes it (2016–2019 series: 15.7% / 16.0% / 15.5%); recent-year gross margin is not in the computed outputs, so no recent figure is quoted. That ROIC/margin profile supports a moderate moat, not a 7+.
- FOR: Largest global beverage-can footprint — scale and plant proximity to customer filling lines that rivals cannot replicate cheaply; long-term supply contracts with the major beverage companies; aluminum's recyclability tailwind as brands shift off plastic; metal cost pass-through in contracts limits commodity margin risk.
- AGAINST: Powerful, concentrated buyers (global beverage majors) who dual-source with Crown and Ardagh; can-making is proven, replicable technology — no proprietary lock-in; pricing is largely cost pass-through, so real pricing power is thin; ROIC ~8–10% through the recent cycle is at, not well above, the cost of capital; high leverage (net debt 7.0x normalized OE on the final run) leaves little room for a volume downturn.
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — 5.4 final run (2026-10-16)
Growth-start sanity check: the engine's blended start is 6.25%. Against actual prints — revenue CAGR 5y +2.24%, 3y −0.53%, latest FY revenue +11.58% and TTM revenue +15.56% YoY (both inflated by aluminum price pass-through, not volume), Q2 2026 volumes +4.3%, guided 2026 volume growth ~3% and comparable EPS growth >10% (buyback-assisted, share count −4.8%/yr already credited in the blend) — a 6.25% OE/share start sits between real volume growth and guided EPS growth and is defensible. The super-bull start of 18.25% is above every recent print; it is kept only as the 10%-probability tail paired with the 1.25x OE multiplier, not as a forecast. Probabilities 10/25/30/25/10; OE multipliers 0.75/0.90/1.00/1.10/1.25 (defaults — this company's evidence does not justify skewing them). Price $63.20.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | −5.75% | 0.75 | Volume downturn + leverage bites; OE compresses like 2022 | $13.10 | 4.84% |
| Bear | 25% | 1.25% | 0.90 | Flat volumes, cost/start-up pressure persists in North America | $21.08 | 6.62% |
| Base | 30% | 6.25% | 1.00 | ~3% volume growth + buyback-driven OE/share growth, fading over CAP | $28.83 | 8.34% |
| Bull | 25% | 11.25% | 1.10 | Sustained substrate shift to aluminum, EPS guide beaten | $38.97 | 10.48% |
| Super bull | 10% | 18.25% | 1.25 | Tail: multi-year volume + margin breakout | $58.90 | 14.26% |

- **Probability-weighted: IV@15% $30.86 (−51.2% vs price), IV@12% $41.24, IV@10% $52.85, weighted IRR 8.82%, base-case IRR 8.34%**
- **Tier by numbers: D.** Diagnostics: OE yield 4.76%, terminal value 19.3% of IV@15%, scenario spread 4.50x, net debt 6.99x normalized OE, 9.5 months since FY end.
- Even the super-bull scenario (14.26% IRR, IV@15% $58.90) does not clear 15% at $63.20.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.5 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, quoted above.
- **BUYBACK_TAILWIND** (share count −4.8%/yr): already credited via the growth adjustment in the blend; not double-counted in the verdict. Note the flip side: buybacks at $63.20 against a $30.86 weighted IV@15% destroy per-share value rather than create it.
- **NI_OCF_DIVERGENCE** (2023, 2024): 2024 is the aerospace divestiture — net income of $4,014M includes the $4.61B pre-tax gain on the sale to BAE (an investing item, per the FY2025 10-K), while OCF was only $115M after roughly $766M of taxes paid on the transaction through 2024. 2023's gap runs the other way (NI $711M vs OCF $1,863M) on non-cash D&A ($605M) and working-capital effects in the held-for-sale period. In both years the OCF-based conservative OE series used throughout is uncontaminated by the gain; the FY2024 OE/share of −$1.40 is a tax-payment timing artifact, which is one reason the TTM base is preferred over the 3-yr median.
- **WIDE_SCENARIO_SPREAD** (4.50x): real — the OE stream has swung from −$4.34 to +$2.75/share within four years. Confidence is capped at low, and the verdict is sized to the conservative end.
- **HIGH_NET_DEBT** (7.0x normalized OE on the final run; 8.5x on the preliminary run): balance sheet from the filing — net debt $5.80B plus $361M lease liabilities against equity of $5,421M (FY2025). Levered OE can vanish fast, as FY2022 showed; the bear cases are stressed accordingly (super-bear OE multiplier 0.75).
- **TIER_BAND** (bear D at 6.62% vs bull C at 10.48%): the verdict spans tiers, and even the bull end only reaches C — sized to the bear end, the conclusion is unchanged: D.

## My thoughts / overlay
- Method range: on the preliminary median base ($2.48/share) the weighted IRR was 7.74% with IV@15% $25.40; on the TTM base ($3.01/share) it is 8.82% / $30.86. Both are Tier D — the verdict is not base-sensitive.
- The business is fine; the price is the problem. Ball guides to >10% comparable EPS growth and >$900M FCF for 2026, volumes are growing, and the aluminum substrate shift is a real tailwind. But at $63.20 the market is paying for a decade of flawless execution from a company whose OE was negative in two of the last five years and whose ROIC runs ~8–10%.
- Hurdle-clearing prices (final run): clears 15% at **$30.86**, 20% at $21.57, 25% at $16.48. The stock would need to fall by roughly half before the weighted case clears Andrew's 15% hurdle.

## Enrichment data notes (non-blocking)
- fundamentals.json, prices.json, statements.json, profile.json/street.json, and reprice (live.json: Tier D at the same $63.20 close, no change) all completed. segments.json completed but returned no tables — no dimensioned facts for the tracked segment/product/geography concepts in the filing XBRL instance — so no segment breakdown is quoted. profile.json carries no employee headcount (none found in the FY2025 10-K text searched).

## Final verdict
- **Final tier: D** (weighted IRR 8.82% on the TTM base; bear D → bull C band, sized to the bear end)
- Confidence: **Low** (wide scenario spread, volatile OE history — positive in only 2 of the last 5 years — and 7.0x net debt to normalized OE)
- One-liner: Decent oligopoly can maker, moat 5/10, but levered, cyclical owner's earnings — at $63.20 the weighted IRR is 8.8% (IV@15% $30.86); it only clears 15% below ~$31.
