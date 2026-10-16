# EXPD — Expeditors International of Washington, Inc.
v5 run, 2026-10-15. Market cap $26.757B at $196.38 (nasdaq_quote_api) — in scope under $40B.

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.json, or financials_history.csv — none are recomputed.

## What it is
Global asset-light freight forwarder, top-10 worldwide with 250+ offices on six continents. It owns no planes or ships: it buys air and ocean carrier capacity and resells it, earning the buy/sell spread. Three legs — airfreight services, ocean freight and ocean services (as an NVOCC), and customs brokerage and other services (customs, Transcon, distribution, order management). Customs is the high-value, regulation-heavy leg; airfreight is the most cyclical. Founded 1979, historically all-organic growth, no large M&A.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $1,006,501,000; capex $53,101,000 (tag PaymentsToAcquireProductiveAssets); SBC $69,231,000 (always a real cost).
- **Conservative owner's earnings FY2025: $884,169,000 = $6.49/share latest FY** (dcf_numbers.json base_oe_latest_per_share $6.4894)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $890,452,000 — essentially the same as the conservative figure, which raises confidence in the base.
- OE positive 5 of the last 5 fiscal years.
- Balance sheet: cash $1,314,285,000 at FY2025 (financials_history.csv); no debt_current or debt_lt tags were filed, so the engine reports net_debt_latest as null — the company carries no material reported borrowings in this history. No HIGH_NET_DEBT or BIG_NET_CASH flag fired; the verdict does not hinge on the balance sheet.
- OE history is cyclical, not smooth: conservative OE was $955,478,000 in FY2023, $618,531,000 in FY2024, and $884,169,000 in FY2025, driven by operating-cash-flow and working-capital swings in the post-COVID freight-rate normalization, not by a change in the business.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $1,006,501,000 − prior YTD $521,834,000 + current YTD $487,874,000 = **TTM $972,541,000**
- Capex: FY $53,101,000 − prior YTD $29,027,000 + current YTD $24,603,000 = **TTM $48,677,000**
- SBC: FY $69,231,000 − prior YTD $38,816,000 + current YTD $45,023,000 = **TTM $75,438,000**
- Shares (current-YTD weighted diluted): **132,724,000**
- **TTM OE total $848,426,000 → base OE/share $6.3924** (base_source: ttm_json)
- The engine's normalized base (median of last 3 FY) is $6.3620/share and the latest FY is $6.4894/share — all three sit within a narrow band, so there is no BASE_DIVERGENCE issue: the TTM base is used because the FY is stale (see FLAGS), not because the median is distorted.

## Moat: 7/10 — strong
Justification: A dense global network and customs expertise give Expeditors a real, durable edge and high returns on capital through the cycle, but forwarding itself has limited pricing power — the buy/sell spread is set by the freight market, customers can multi-source, and equally scaled rivals exist.
- FOR: Network effect — a dense global office and trade-lane network that becomes more useful to multinational customers as it grows, in a fragmented industry of smaller forwarders
- FOR: Customs brokerage and regulatory expertise — clearing goods through tightening tariff and trade rules is sticky, high-value work, and customs / Transcon / distribution / order management each grew double-digit for a second consecutive quarter in Q2 2026
- FOR: Asset-light model — no fleet capex burden, structurally low capex ($53,101,000 in FY2025 against OCF of $1,006,501,000), and flexibility to pivot capacity in volatile rate markets
- FOR: Cohesive organic culture — growth built organically rather than by acquisition, with commission-based, profit-linked branch compensation that has produced industry-leading profitability through cycles
- AGAINST: Limited pricing power — earnings are a market-set spread between buy and sell rates; Q2 2026 showed the spread widening on tight air capacity, and spreads mean-revert
- AGAINST: Low switching barriers at the core — freight forwarding is fragmented and customers can dual-source or switch; DSV, Kuehne+Nagel and DHL have equal or greater scale, and digital forwarders / carrier-direct models press from below
- AGAINST: Cyclical, concentrated exposure — results ride global trade, Asia–North America lanes, tariffs and geopolitics; revenue swung from $17,071,284,000 in FY2022 to $9,300,110,000 in FY2023 when rates normalized
- A 7 gives CAP = 11.1 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 11.1 years, 15-year projection.

## DCF — v5 final run (2026-10-15)
Engine blended growth: g_base 6.96% — components rev CAGR 5y 2.92%, rev CAGR 3y -13.44% (a COVID-peak base artifact, see FLAGS), latest revenue YoY +4.42%, OE/share CAGR 2y +1.00%, blended 1.96% plus a +5.00pp share-count adjustment for the buyback (capped). Probabilities and offsets/multipliers are the defaults 10/25/30/25/10, -12/-5/0/+5/+12pp, 0.75/0.90/1.00/1.10/1.25 — no skew, because the Q2 2026 strength and the spread-normalization risk roughly offset.

**Sanity check against actual recent prints — written reason required and given:** Q2 2026 printed revenue +32.1% to $3.5 billion, diluted EPS $2.03 (+51% year over year), and operating income +41%, led by airfreight. Those headline prints sit above every scenario growth start, including super bull at 19.0%. That is deliberate, not a cap artifact: the Q2 growth was mostly rate, not volume — airfreight tonnage rose 14% and ocean container volume was flat, with airfreight revenue up 57.1% on elevated buy/sell rates and AI-hyperscaler demand for freighter capacity. A forwarder does not keep its gross revenue; it keeps the spread, and that spread is cyclical. Extrapolating a +32% revenue / +51% EPS quarter as a growth start would capitalize a rate spike. The super-bull start of 19.0% is instead set near the underlying net-revenue pace of that quarter, and the base start of 7.0% sits above the latest FY revenue YoY (+4.42%) and the 5-yr revenue CAGR (2.92%), reflecting the stronger current momentum without treating it as permanent.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -5.0% | 0.75 | Trade downturn; air/ocean rates and spreads collapse | $27.62 | 4.02% |
| Bear | 25% | 2.0% | 0.90 | Q2 rate spike fully normalizes; low-single-digit growth | $45.99 | 5.40% |
| Base | 30% | 7.0% | 1.00 | Through-cycle growth plus buyback tailwind, fading over the CAP | $64.72 | 6.84% |
| Bull | 25% | 12.0% | 1.10 | Sustained air demand and customs share gains hold longer | $90.28 | 8.71% |
| Super bull | 10% | 19.0% | 1.25 | Rate strength and share gains persist near the Q2 net-revenue pace | $143.09 | 12.11% |

- **Probability-weighted: IV@15% $70.55 (-64.1% vs price), IV@12% $95.23, IV@10% $122.97, weighted IRR 7.34%, base-case IRR 6.84%**
- **Tier by numbers: D.** Diagnostics (dcf_numbers.json): OE yield 3.26%, terminal value 20.5% of IV@15%, scenario spread 5.18x, 9.5 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (latest FY ended 9.5 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, with all inputs quoted in the Owner's earnings section above. The TTM base ($6.3924) is close to both the median ($6.3620) and the latest FY ($6.4894), so staleness was not hiding a break in earnings power.
- **BUYBACK_TAILWIND** (share count shrinking 6.1%/yr): already credited via the +5.00pp growth adjustment in the engine blend — not double-counted in the verdict. Diluted shares fell from 182,704,000 in FY2016 to 136,249,000 in FY2025 (financials_history.csv), and the company returned $461 million to shareholders in Q2 2026 alone per its Q2 release; the per-share math benefits, but a buyback at $196.38 against a $70.55 weighted IV destroys value per dollar spent rather than creating it.
- **BASIS_BREAK_SUSPECT** (>60% revenue jump/drop in the last 5 years): identified — this is the COVID freight supercycle, not a divestiture, M&A, or restatement. Revenue went $9,584,393,000 (FY2020) → $16,523,517,000 (FY2021) → $17,071,284,000 (FY2022) → $9,300,110,000 (FY2023) as pandemic rates spiked and then normalized. Consequence handled explicitly: the 3-yr revenue CAGR (-13.44%) is a peak-base artifact and the 5-yr CAGR (2.92%) straddles the cycle, so neither is trusted alone — the blend's median construction and the scenario starts anchored to the latest YoY (+4.42%), the TTM base, and current-quarter underlying net-revenue momentum are the inputs that do the work.
- **WIDE_SCENARIO_SPREAD** (super-bull IV 5.18x super-bear IV): real — this is a cyclical spread business and the outcome range IS wide. Confidence is capped at medium, and the verdict is sized to the conservative end. Note the spread does not rescue the price: even the super-bull IV@15% ($143.09, IRR 12.11%) sits below the $196.38 price.

## My thoughts / overlay
- Quality is not the debate. This is one of the best-run forwarders in the world: asset-light, no material reported debt, OE positive 5/5 years, both OE definitions agreeing, and a buyback that has cut the share count by roughly a quarter in a decade.
- Price is the entire debate. At $196.38 the market is pricing Expeditors as if the Q2 2026 rate environment — or something close to it — is the new normal. On the filing-derived TTM base of $6.3924/share the OE yield is 3.26%; no scenario in the set, including super bull at a 19.0% growth start and a 1.25x OE multiplier, clears Andrew's 15% hurdle, and the super bull does not even clear its own IV at the current price.
- Method range: unusually narrow in its conclusion. The preliminary run (moat 5, median base) gave a weighted IRR of 7.00% and IV@15% of $67.19; the final run (moat 7, TTM base, longer CAP) gives 7.34% and $70.55. Every defensible variant lands in Tier D — this is not an assumption-dominated name at this price.
- Hurdle-clearing price: the weighted case clears 15% at or below $70.55 (the weighted IV@15%). A margin of safety against the bear cases would require a price below even that — the bear IV@15% is $45.99. There is no plausible near-term path at $196.38.
- Risks to this (bearish-on-price) verdict: a structural, not cyclical, step-up in airfreight demand from AI infrastructure and in customs complexity from tariffs could hold spreads wider for longer than the scenarios assume; the stock has already re-rated sharply (consensus targets clustered well below the price in recent analyst notes), so the market is knowingly paying for that possibility.

## Final verdict
- **Final tier: D** (weighted IRR 7.34% on the v5 final inputs; no tier override)
- Confidence: **Medium** (high on OE quality and the TTM base; capped at medium by the 5.18x scenario spread and freight cyclicality)
- One-liner: High-quality asset-light forwarder with a strong moat (7/10), but at $196.38 it clears nothing — weighted IRR 7.3%, IV@15% $70.55, and even the super-bull case stays below the price; it would need to fall to $70.55 or below to clear the 15% hurdle on the weighted case.
