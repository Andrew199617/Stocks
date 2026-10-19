# BWXT — BWX Technologies, Inc.
Engine 5.4.0 run, 2026-10-17. Price $137.01 (nasdaq_quote_api), market cap $12,585,192,341.13, shares diluted latest 91,856,013, shares outstanding 91,621,980 as of 2026-07-31. In scope under $40B.

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.json, fundamentals.json, or financials_history.csv — none are recomputed.

## What it is
Designer and manufacturer of nuclear reactors, components and fuel for government and commercial use. Sole-source / exclusive manufacturer of naval nuclear reactors and fuel for the U.S. Naval Nuclear Propulsion Program (420 compact naval reactors delivered over five decades per search results), and the only commercial heavy nuclear component manufacturer in North America per search results. Two segments cited in Q2 2026 reporting: Government Operations and Commercial Operations. Backlog $8.4 billion at Q2 2026, up 40% year over year, trailing book-to-bill 1.7x (search results).

## Owner's earnings
**FY2025 (10-K, financials_history.csv):** revenue $3,198,425,000; net income $328,945,000; operating income $404,459,000; operating cash flow $479,848,000; capex $184,557,000; SBC $26,072,000 (always a real cost).
- **Conservative owner's earnings FY2025: $269,219,000 = $2.9308805292909894/share** (base_oe_latest_per_share in dcf_numbers.json)
- Maintenance version FY2025: $322,074,000 (financials_history.csv oe_maintenance)
- OE positive 5 of the last 5 fiscal years on the engine count (oe_positive_years_of_last_5: 5/5 for the median window used), but the 5-year OE/share history is volatile — see OE_VOLATILE below.
- Net debt latest $1,516,204,000 (basis LongTermDebtNoncurrent+LongTermDebtCurrent, dcf_numbers.json); lease liabilities latest $8,800,000.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct):**
- OCF: FY $479,848,000 − prior YTD $209,693,000 + current YTD $249,003,000 = **TTM $519,158,000**
- Capex: FY $184,557,000 − prior YTD $66,098,000 + current YTD $83,937,000 = **TTM $202,396,000**
- SBC: FY $26,072,000 − prior YTD $13,735,000 + current YTD $20,117,000 = **TTM $32,454,000**
- Shares (current-YTD weighted diluted): **91,957,928**
- **TTM OE total $284,308,000 → base OE/share $3.0917182040030307** (base_source: ttm_json)
- The engine's normalized base (median of last 3 FY OE/share) is $2.5375754416527148/share — reported, not used as the base, because the TTM figure is more current and filing-derived; using the median would only lower the valuation further.
- Fundamentals TTM (fundamentals.json, period 2026-06-30): revenue $3,513,970,000, operating income $426,232,000, net income $355,177,000, OE conservative $284,242,000, OE/share $3.0915739651518437 — consistent with ttm.py.

## Moat: 7/10 — strong, not wide
Justification: Sole-source naval nuclear monopoly with extreme licensing/security barriers and a $8.4B backlog, but government-contract pricing limits pricing power, ROIC has fallen from 19.2% to 12.2% and gross margin from 27.1% to 22.9% over the last five fiscal years in fundamentals.json, so measured returns are only moderately above a normal cost of capital and are compressing as commercial mix and growth capex rise.
- FOR: Exclusive manufacturer of naval nuclear reactors and fuel for the Naval Nuclear Propulsion Program — no licensed substitute for highly enriched naval fuel/reactor work
- FOR: Only commercial heavy nuclear component manufacturer in North America (search results); contracted for the BWRX-300 reactor pressure vessel
- FOR: Backlog $8.4B, up 40% YoY, book-to-bill 1.7x in Q2 2026 — multi-year revenue visibility
- FOR: ROIC proxy stayed positive and double-digit through the cycle in fundamentals.json: 19.2% (2020), 14.9% (2021), 13.2% (2022), 14.2% (2023), 14.9% (2024), 12.2% (2025)
- AGAINST: ROIC proxy fell from 19.2% to 12.2% and gross margin fell from 27.1% to 22.9% over 2020–2025 (fundamentals.json) — returns are compressing, not widening
- AGAINST: Pricing is set inside U.S. government contracts, not by the market — limited independent pricing power despite the monopoly position
- AGAINST: Customer/program concentration in the U.S. Navy / DOE; commercial nuclear and SMR demand is still order-dependent
- AGAINST: Growth now requires heavy capex and acquisitions (Kinectrics, Precision Components Group closed July 1, 2026 per search results), which depresses conservative OE
- A 7 gives CAP = 11.1 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 11.1 years, 15-year projection.

## DCF — engine 5.4.0 final run (2026-10-17)
Growth sanity check: engine blended growth g_base 14.855621008634545% from rev CAGR 5y 8.53779577643925%, rev CAGR 3y 12.723563840467866%, latest revenue YoY 18.300085735822713%, OE/share CAGR 2y 17.043576885477663%. Recent prints: Q2 2026 revenue $901.6 million, up 18.0% YoY, and FY2026 guidance raised to revenue of approximately $3.8 billion vs FY2025 revenue $3,198,425,000, adjusted EBITDA $662 million–$672 million, non-GAAP EPS $4.70–$4.80 and free cash flow $345 million–$360 million (search results). The base start at 14.86% sits below the latest 18% prints — reason: management's own Investor Day outline in search results puts 2030 revenue at $5.50 billion to $6.00 billion off the ~$3.8 billion 2026 guide, a materially slower medium-term path than the current high-teens print, and part of the recent growth is acquisition contribution (Commercial Operations +72% in Q2 2026 with only part organic per search results). Bull start was cut to 17.86% (offset +0.03, roughly the current guided print, not above it) and super-bull to 21.86% (offset +0.07) because the default +0.12 super-bull start of 26.86% has no support in any recent print. Bear weight was widened (probs 15/30/30/20/5 vs default 10/25/30/25/10) for OE_VOLATILE and HIGH_NET_DEBT. OE multipliers are the defaults 0.75/0.90/1.00/1.10/1.25.

| Scenario | Prob | Growth start | OE mult | IV@15 | IRR |
|---|---|---|---|---|---|
| Super bear | 15% | 2.86% | 0.75 | $19.33561764714011 | 4.275015361497583% |
| Bear | 30% | 9.86% | 0.90 | $32.324757417691146 | 5.751402387997134% |
| Base | 30% | 14.86% | 1.00 | $45.554554959582774 | 7.214959830907952% |
| Bull | 20% | 17.86% | 1.10 | $57.7908931580395 | 8.4687418425485% |
| Super bull | 5% | 21.86% | 1.25 | $79.39830259076855 | 10.500484756099249% |

- **Probability-weighted: IV@15% $41.79223012139952, IV@12% $57.30323096872145, IV@10% $74.86279678120302, weighted IRR 6.831986643577012%, base-case IRR 7.214959830907952%**
- **Tier by numbers: D** (tier_bear D, tier_bull D — no TIER_BAND). Diagnostics (dcf_numbers.json): OE yield 2.2565639033669302%, terminal value 22.15888379168547% of IV@15%, scenario spread 4.106323575472241x, net debt 5.338879809139274x normalized OE, 9.526938239159001 months since FY end.
- Hurdle prices: clears 15% at $41.79223012139952, 20% at $28.191029600289475, 25% at $20.941860466231724. Upside at 15%: -69.49694903919457% vs the $137.01 price.

## Flags — every fragility flag resolved
- **STALE_FY** (latest fiscal year ended 10 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, legs quoted above. Final-run diagnostics still print 9.526938239159001 months since FY end, but the base_source is ttm_json.
- **OE_VOLATILE** (OE/share range over the last 5 years spans >3x): real and explained by the capex cycle, not by demand collapse — revenue rose every year in financials_history.csv from 2020 to 2025 while capex surged in 2020–2021 ($255,027,000 / $311,052,000), crushing conservative OE in those years (OE/share was negative in 2020 in fundamentals.json), then capex normalized to $151,286,000–$184,557,000 in 2023–2025 and OE/share recovered to $2.9308805292909894 in FY2025. Handled by the TTM base plus widened bear/super-bear weights (45% combined).
- **LOW_OE_YIELD** (preliminary run only, base OE yield 1.9%): on the TTM base the OE yield is 2.2565639033669302% — still low. The valuation rests almost entirely on growth; that fragility is real and is why the verdict is sized to the conservative end even though the tier does not change.
- **WIDE_SCENARIO_SPREAD** (super-bull IV 4.106323575472241x super-bear IV): real — confidence is capped at medium, never high. Note the spread does not threaten the verdict direction: even the super-bull IRR of 10.500484756099249% is below the 15% hurdle.
- **HIGH_NET_DEBT** (net debt 5.338879809139274x normalized OE in the final run; 6.5047571094673x in the preliminary run): balance sheet from the filing-derived history — FY2025 total debt $2,015,983,000 against cash $499,779,000, for net debt $1,516,204,000 (dcf_numbers.json). Search results add that long-term debt was $2,019,897 thousand at June 30, 2026 and that the company completed a $1.25 billion 0% convertible offering whose proceeds repaid credit-facility/term-loan balances. Leverage is material for an OE stream this size; it is stressed via the widened bear weights and the 0.75/0.90 OE multipliers, and it does not change the tier — the name fails the hurdle on growth-vs-price alone.

## My thoughts / overlay
- Quality is not the debate: this is a genuine sole-source franchise with a $8.4B backlog. Price is the debate. At $137.01 the market is paying for the 2030 Investor Day path ($5.50B–$6.00B revenue, $1.10B–$1.20B adjusted EBITDA, per search results) and more, while the TTM owner's-earnings yield is only 2.2565639033669302%.
- Method range: on the preliminary median-base run the weighted IRR was 6.286741353752545% with IV@15% $36.99089657185172; on this final TTM-base run it is 6.831986643577012% with IV@15% $41.79223012139952. Both are Tier D, and even the super-bull case (10.500484756099249% IRR) only reaches Tier C territory — there is no defensible method here that clears 15% anywhere near $137.01.
- Positives since FY2025: Q2 2026 revenue +18.0%, guidance raised, $1.4 billion of Naval Nuclear Propulsion Program contracts in May 2026 and a ~$189 million Navy fuel contract in October 2026 (search results), and the agreed sale of >80% of the medical business for $750 million upfront (up to $800 million) while retaining a 20% stake — proceeds would cut net debt if applied there, but that is not in the filed TTM numbers and is not credited in the base.
- Risks: falling ROIC and gross margin, acquisition integration (PCG, Kinectrics), commercial-capacity capex guided at ~6% of sales and possibly higher (search results), and government program timing/funding.

## Data / enrichment notes
- Enrichment (fundamentals, prices, segments, statements, profile, reprice) all ran. One non-blocking gap: segments.py reported the 2026-06-30 10-Q had no XBRL instance document, so segments.json is marked complete: false, though annual and Q1 segment/geography tables are present. This does not affect the score, which is built from EDGAR companyfacts via the engine and ttm.py.

## Final verdict
- **Final tier: D** (weighted IRR 6.831986643577012%; bear→bull band D→D)
- Confidence: **Medium** (capped by WIDE_SCENARIO_SPREAD; the direction is robust — no scenario clears 15%)
- One-liner: Strong sole-source naval nuclear franchise, moat 7/10 — but at $137.01 it does not clear 15% on TTM owner's earnings (6.8% weighted IRR, IV@15% $41.79); it would need to fall to $41.79 to clear the hurdle.
