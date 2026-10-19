# HUBS — HubSpot, Inc.
Engine 5.4.0 run, 2026-10-18. Price $230.94 (nasdaq_quote_api), market cap $12.285B — in scope under $40B.

All figures below are copied from dcf_numbers.json, ttm.json, key_numbers.md, fundamentals.json or financials_history.csv — none are recomputed.

## What it is
Unified CRM / customer platform for SMB and mid-market companies: Marketing, Sales, Service, Content and Operations Hubs sold per seat, plus newer usage/outcome-priced AI agents (Breeze; Customer Agent at $0.50 per resolved conversation). 306k+ customers at Q2 2026 (+14% YoY), net revenue retention only 102% in Q2 2026. Revenue: FY2025 $3,131,266,000; TTM through Q2 2026 $3,448,999,000 (fundamentals.json).

## Owner's earnings
**FY2025 (10-K via EDGAR, financials_history.csv):** operating cash flow $760,717,000; SBC $528,153,000 (always a real cost — 16.9% of revenue); capex $53,165,000.
- **Conservative owner's earnings FY2025: $179,399,000 = $3.37/share** (base_oe_latest_per_share).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $576,556,000 — higher than the conservative figure mainly because it does not deduct SBC the same way; the conservative OCF − capex − SBC figure is the one used throughout, and it is the harsher one.
- OE positive 3 of the last 5 fiscal years: OE/share was −$1.56 (2020), +$0.92 (2021), −$0.83 (2022), −$2.31 (2023), +$1.08 (2024), +$3.37 (2025) — the negative years are SBC exceeding OCF − capex, not cash burn (FCF/share was positive throughout).

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $760,717,000 − prior YTD $325,932,000 + current YTD $421,580,000 = **TTM $856,365,000**
- Capex: FY $53,165,000 − prior YTD $29,370,000 + current YTD $35,074,000 = **TTM $58,869,000**
- SBC: FY $528,153,000 − prior YTD $257,668,000 + current YTD $244,227,000 = **TTM $514,712,000**
- Shares (current-YTD weighted diluted): **51,564,000**
- **TTM OE total $282,784,000 → base OE/share $5.48** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $1.08/share — rejected as the base: it is the FY2024 figure and is dragged by the SBC-heavy pre-inflection years (FY2023 OE/share −$2.31). Latest FY ($3.37) and TTM ($5.48) show the inflection is real — OCF is growing faster than SBC (TTM SBC actually fell vs FY2025 while OCF rose). Even on the generous TTM base the stock does not clear any hurdle (see below), so the base choice does not drive the verdict.

## Moat: 5/10 — moderate / narrow
Justification: a real platform-and-workflow moat for SMB/mid-market, but no ROIC evidence of a wide moat yet and the seat model is under AI pressure.
- Evidence first (fundamentals.json): gross margin is high and stable — 80.1% (2021), 82.2% (2022), 84.4% (2023), 85.0% (2024), 83.8% (2025), 83.2% TTM. But the roic_proxy series is negative to zero through the whole window: −8.8% (2021), −12.2% (2022), −16.8% (2023), −3.8% (2024), +0.4% (2025), with TTM GAAP operating income only just positive ($130,738,000, 3.8% margin). GAAP returns have never covered the cost of capital because SBC (~17-20% of revenue in 2023-25) consumes the gross profit. A moat above 6 would need ROIC proof this history does not give.
- FOR: unified multi-hub platform — once marketing, sales and service workflows and customer data live in one system, ripping it out is painful; free-CRM funnel converts a huge SMB base (306k+ customers); large app/integration ecosystem; ease-of-use advantage vs Salesforce in the mid-market, with expanding upmarket and multi-hub adoption.
- AGAINST: Salesforce, Microsoft Dynamics and low-cost rivals (Zoho, Pipedrive) contest every segment, and SMB customers churn and switch more easily than enterprise; net revenue retention of only 102% (Q2 2026) shows weak expansion pricing power; per-seat pricing is directly threatened by AI agents doing seat work — HubSpot itself cut Customer Agent to outcome pricing ($0.50/resolution) in April 2026; SBC at ~$515M TTM is a persistent real cost that keeps GAAP ROIC near zero.
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — engine 5.4 final run (2026-10-18)
Growth sanity check: the engine's blended start is 18.40% (components, share-adjusted: 5-yr rev CAGR 25.38%, 3-yr 18.40%, latest YoY 15.73%). Against actual prints — FY2025 revenue +19.17% YoY, Q2 2026 revenue +20% as reported (+17.5% constant currency), Q3 2026 guidance ~+14% YoY and revised FY2026 guidance $3.678–3.686B — the 18.4% base start for OE/share (not revenue) is defensible only with operating leverage and buybacks; revenue growth alone is decelerating into the mid-teens. That deceleration plus the OE_VOLATILE flag is why bear-side weight was raised: probabilities 15/30/30/15/10 (45% bear-or-worse) instead of the 10/25/30/25/10 default. Offsets and multipliers are the defaults (−12/−5/0/+5/+12pp; 0.75/0.90/1.00/1.10/1.25). Super-bull start 30.40% is an OE/share figure requiring both revenue re-acceleration and continued SBC leverage — possible, not the plan.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | 6.4% | 0.75 | AI agents compress seats; growth fades to high-single digits | $39.66 | 4.74% |
| Bear | 30% | 13.4% | 0.90 | Guided mid-teens deceleration sticks; SBC stays ~17% of revenue | $63.48 | 6.26% |
| Base | 30% | 18.4% | 1.00 | Mid-teens revenue growth plus operating leverage on the TTM base | $86.43 | 7.68% |
| Bull | 15% | 23.4% | 1.10 | Upmarket/multi-hub and AI-agent monetization re-accelerate OE | $116.21 | 9.41% |
| Super bull | 10% | 30.4% | 1.25 | Durable category-winner path with real SBC leverage | $174.16 | 12.43% |

- **Probability-weighted: IV@15% $85.77 (−62.9% vs price), IV@12% $117.52, IV@10% $153.34, weighted IRR 7.67%, base-case IRR 7.68%**
- **Tier by numbers: D** — and every scenario individually is D (bear 6.26%, bull 9.41%, even super bull 12.43% < 15%). Diagnostics (dcf_numbers.json): OE yield 2.37%, terminal value 21.8% of IV@15%, scenario spread 4.39x, 9.6 months since FY end.
- Hurdle-clearing prices (dcf_numbers.json): clears 15% only at or below **$85.77**, 20% at $57.80, 25% at $42.82.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.6 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, legs quoted above.
- **BASE_DIVERGENCE** (latest FY $3.37 vs 3-yr median $1.08): the median is the distorted one — it is FY2024, sitting on top of FY2023's −$2.31 SBC-driven trough. The trend FY2024 $1.08 → FY2025 $3.37 → TTM $5.48 is a genuine OE inflection (OCF up, SBC flat-to-down). TTM base used; the verdict is D on any of the three bases.
- **DILUTION** (share count +3.4%/yr, already deducted via the growth adjustment): historically real — diluted shares rose from 44.76M (2020) to 53.19M (2025) on SBC issuance. The trend is now reversing: TTM buybacks were $1,117,895,000 vs issuance $55,968,000 (fundamentals.json), current-YTD diluted shares are 51.56M vs 53.19M for FY2025, and the board authorized an additional $1B repurchase in Q2 2026. SBC itself is not shrinking as a cost (TTM $514,712,000), so dilution is now being bought back with cash rather than eliminated — the OE base already charges SBC in full.
- **OE_VOLATILE** (OE/share spans >3x over 5 years): real — the range is −$2.31 to +$3.37, driven by SBC scaling faster than OCF until 2023, then reversing. Handled with the TTM base plus 45% combined bear/super-bear weight.
- **NI_OCF_DIVERGENCE** (NI vs OCF differ >40% in 2023, 2024, 2025): explained, not a one-off — SBC is a large non-cash add-back (FY2025 SBC $528,153,000 vs net income $45,911,000 and OCF $760,717,000), plus deferred-revenue growth. The conservative OE series deducts SBC in full, so the divergence is exactly the cost this method exists to charge; no tax-deposit or impairment one-off was found.
- **DEBT_TAGS_BLANK** (no debt tag for the latest FY — net debt unknown to the engine): resolved from the FY2025 10-K balance sheet — the convertible senior notes were repaid during 2025 ($458,184,000 current at Dec 2024 → $0 at Dec 2025). At Dec 31, 2025 HubSpot held cash $882,242,000 plus short-term investments $821,552,000 and long-term investments $136,662,000, against operating lease liabilities of $262,305,000 total (engine figure). This is a net-cash, unlevered balance sheet; there is no debt the tags are missing.
- **WIDE_SCENARIO_SPREAD** (super-bull IV 4.39x super-bear): real, but it does not change the decision — all five scenarios price below the current price and all five IRRs are under 15%. Confidence is capped at medium, not high.
- Preliminary-run flags **IRR_AT_FLOOR** and **LOW_OE_YIELD** (on the $1.08 median base, OE yield 0.47%) do not appear in the final run: on the TTM base the OE yield is 2.37% and no scenario sits at the IRR floor. They were artifacts of the stale median base, which is documented above.

## My thoughts / overlay
- The honest headline is the method range, and here it is unusually one-sided: on the median base the weighted IV@15% was $18.14 (preliminary run); on the TTM base it is $85.77. Both are less than 40% of the $230.94 price. Even granting the super-bull path a 10% weight, its IV@15% of $174.16 is still below the price.
- Quality is not the debate: 83-85% gross margins, net cash, $1.12B of TTM buybacks, OCF growing +26% YoY on a TTM basis (fundamentals.json). The debate is price vs SBC-adjusted cash earnings: at $230.94 the market is paying ~42x TTM conservative OE/share of $5.48 for a business whose revenue growth is guided down to the mid-teens and whose NRR is 102%.
- What would have to be true to clear 15%: OE/share compounding well above 30% for years — i.e., SBC falling sharply as a share of revenue while revenue re-accelerates. Q2 2026 went the other way on growth (guidance cut, ~7k net customer adds vs 9-10k expected, stock fell ~25% on the print), though SBC leverage is genuinely improving.
- Risks to the short/avoid case: AI-agent monetization could inflect revenue; the new $1B buyback plus existing authorization supports the price; S&P 400 inclusion (Oct 2026) adds index demand. None of these close a 2.7x gap to IV@15% on their own.

## Final verdict
- **Final tier: D** (weighted IRR 7.67% on the TTM base; every scenario, including super bull at 12.43%, is below the 15% hurdle)
- Confidence: **Medium** (filing-direct TTM base and a verdict robust across all scenarios and both base choices; capped by the 4.39x scenario spread)
- One-liner: Quality CRM platform, moat 5/10 — even on TTM OE of $5.48/share the weighted IRR is only 7.7% at $230.94 (IV@15% $85.77); clears 15% only below ~$86, dragged by ~$515M TTM SBC and decelerating growth.
