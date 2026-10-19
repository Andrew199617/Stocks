# HAS — Hasbro, Inc.
Pass-1 run, 2026-10-17, engine 5.4.0. In scope (market cap $13.846B at $98.76, nasdaq_quote_api).

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.json, fundamentals.json, or financials_history.csv — none are recomputed.

## What it is
Two businesses under one ticker. **Wizards of the Coast & Digital Gaming** — Magic: The Gathering and Dungeons & Dragons — is the growth and profit engine: Q2 2026 segment revenue +27% to $663.8M at a 40.7% operating margin, with Magic posting its first $500M+ quarter (Marvel Super Heroes set) and FY2025 Magic revenue +59%. **Consumer Products** (toys: Play-Doh, Transformers, Peppa Pig, licensed brands) is the legacy business — it grew 5% in Q2 2026 but posted an operating loss in the quarter and took a $1,021.9M goodwill impairment in 2025. Entertainment is now residual (−20% in Q2 2026, post-eOne divestiture). Management's FY2026 guidance (raised at Q2): revenue +5–7% in constant currency, adjusted operating margin 25–26%, adjusted EBITDA $1.45–1.50B; dividend $0.70/qtr (DPS TTM $2.80, fundamentals.json).

## Owner's earnings
**FY2025 (10-K via EDGAR, financials_history.csv):** operating cash flow $893,200,000; capex $63,300,000; SBC $80,400,000 (always a real cost).
- **Conservative owner's earnings FY2025: $749,500,000 = $5.35/share** (key_numbers.md: latest FY OE/share $5.35).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): **−$40,000,000** for FY2025 — useless as printed because net income (−$322,400,000) carries the $1,021.9M non-cash goodwill impairment. The OCF-based conservative series is the clean one throughout; the impairment never touched cash.
- OE positive 5 of the last 5 fiscal years, but volatile: OE/share $5.82 (2020), $4.24 (2021), $1.16 (2022), $3.73 (2023), $5.06 (2024), $5.35 (2025) per financials_history.csv.
- Balance sheet (FY2025, financials_history.csv): total debt $3,264,900,000, cash $776,200,000, **net debt $2,488,700,000** (key_numbers.md: $2.489B), lease liabilities $131,400,000, equity down to $565,500,000 after the impairment. Net debt / normalized OE 2.27x (key_numbers.md diagnostics).

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $893,200,000 − prior YTD $209,400,000 + current YTD $604,400,000 = **TTM $1,288,200,000**
- Capex: FY $63,300,000 − prior YTD $29,900,000 + current YTD $41,200,000 = **TTM $74,600,000**
- SBC: FY $80,400,000 − prior YTD $31,300,000 + current YTD $46,400,000 = **TTM $95,500,000**
- Shares (current-YTD weighted diluted): **143,200,000**
- **TTM OE total $1,118,100,000 → base OE/share $7.81** (base_source: ttm_json)
- Why TTM over the normalized median ($5.06/share): the FY ends 2025-12-28, 9.6 months ago (STALE_FY), and the earnings power genuinely stepped up after it — record Magic quarters in H1 2026 and guidance raised twice. The median averages in the 2023 eOne-era year ($3.73). The cost of this choice is stated plainly in the method range below: on the median base this is a Tier D; the TTM base is doing real work, so bear-case multipliers were deepened and bear weight widened to compensate (see Scenarios).

## Moat: 5/10 — moderate, and it is an average of two very different businesses
Justification: Wizards (Magic, D&D) is a genuine franchise moat — durable player network effects, pricing power, 40%+ segment margins — while Consumer Products toys are close to moatless and just absorbed a $1,021.9M goodwill impairment. Consolidated ROIC (fundamentals.json roic_proxy) is unstable rather than wide-moat-like: 26.4% in 2016, 5.0–9.4% in 2020–22, −30.3% in 2023 (eOne-era losses/impairments), 14.1% in 2024, 0.3% in 2025 (goodwill impairment inside operating income). The cash OE series is steadier than reported ROIC because the charges are non-cash, but a 7+ moat needs returns that stay above the cost of capital through a cycle, and Hasbro's printed history does not show that at the consolidated level. Gross margin has improved from 62.0% (2016) to 75.8% (2025) on mix shift toward Wizards/licensing, which supports a moderate 5 rather than a weak score.
- FOR: Magic: The Gathering — 30+ year franchise, record revenue in 2025 (+59%) and first $500M+ quarter in Q2 2026, player network effects and a hobby-store distribution network rivals cannot replicate; Wizards segment economics (~41–45% operating margins, high-30s/40% targeted through 2027 — proven pricing power); Dungeons & Dragons plus the D&D Beyond platform; owned IP library (Monopoly, Transformers, Play-Doh, Peppa Pig) monetized asset-light via licensing, including MONOPOLY GO! royalties.
- AGAINST: Consumer Products toys commoditized against Mattel, LEGO and private label with retailer bargaining power — the 2025 goodwill impairment is the receipt; tariff exposure on imported toys; Magic growth is set-cycle driven and management guided Magic lower in Q4 2026 on a tough comp and a set shifting to early 2027; leverage plus the $0.70/qtr dividend limit flexibility; Entertainment shrinking and digital games just took a $56M impairment on cancelled projects.
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — final run (2026-10-17)
**Growth sanity check (mandatory):** the engine blend is 5.05% (components: rev CAGR 5y −2.97%, rev CAGR 3y −7.04%, latest rev YoY +13.68%, OE/share CAGR 2y +19.79%). Recent prints are hotter than the blend: FY2025 revenue +13.68%, Q2 2026 revenue +16.2%, Wizards +27%. The base start (5.1%) and bull start (10.1%) sit **below** the latest prints, with this written reason: those prints are set-cycle peaks (a record Marvel Magic quarter; FY2025 Magic +59% on Universes Beyond), and management's own raised FY2026 guidance is only +5–7% in constant currency with Magic guided *down* in Q4 2026 on a tough comp and a set shifting into early 2027. Guidance, not the peak print, is the forward anchor; the super-bull start (17.1%) is set at roughly the latest print, i.e. it assumes peak cadence persists. Scenario adjustments vs defaults, with reasons: probabilities widened to 15/30/30/15/10 (OE_VOLATILE — bear-or-worse carries 45%); OE multipliers deepened at the bear end to 0.65/0.85 — the super-bear 0.65× on the TTM base lands OE/share essentially on the normalized 3-yr median ($5.06), i.e. the bear case is "the TTM step-up fully normalizes," and 0.85× is partial normalization. Offsets left at the engine defaults (−12/−5/0/+5/+12pp). Price $98.76.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | -7.0% | 0.65 | TTM step-up fully normalizes to the median base; toys downturn + tariff squeeze | $28.02 | 5.70% |
| Bear | 30% | 0.1% | 0.85 | Partial normalization; Magic cadence cools, Consumer Products flat-to-down | $49.13 | 8.62% |
| Base | 30% | 5.1% | 1.0 | Guidance path: mid-single-digit growth, Wizards margins hold | $71.18 | 11.58% |
| Bull | 15% | 10.1% | 1.1 | Magic momentum persists above guidance; licensing compounds | $96.27 | 14.71% |
| Super bull | 10% | 17.1% | 1.25 | Peak set cadence becomes the run rate; digital games land | $145.60 | 20.02% |

- **Probability-weighted: IV@15% $69.29 (−29.8% vs price), IV@12% $92.15 (−6.7%), IV@10% $117.65, weighted IRR 11.38%, base-case IRR 11.58%**
- **Tier by numbers: C.** Diagnostics (key_numbers.md): OE yield 7.91%, terminal value 18.8% of IV@15%, scenario spread 5.20x, net debt 2.27x normalized OE, 9.6 months since FY end.
- Hurdle-clearing prices (weighted path): 15% at $69.29 · 20% at $48.77 · 25% at $37.49.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.6 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, legs quoted above.
- **OE_VOLATILE** (OE/share range >3x over 5 years): real — $1.16 (2022) to $5.82 (2020) on the filed history, driven by the 2022 OCF collapse and the eOne era. Handled by widening bear-or-worse probability to 45% and deepening bear multipliers so the super-bear case returns OE to the normalized median.
- **NI_OCF_DIVERGENCE** (2023, 2024, 2025): identified, all non-cash or working-capital, none contaminates the OCF-based base. 2025: net loss −$322.4M vs OCF $893.2M — the $1,021.9M non-cash goodwill impairment in Consumer Products plus a $25.0M loss on disposal of business (FY2025 results release cash-flow reconciliation). 2023: net loss −$1,489.3M vs OCF $725.6M — eOne-era operating loss (−$1,538.8M operating income) full of non-cash charges while cash held up. 2024: net income $385.6M vs OCF $847.4M — D&A of $163.0M and disposal losses ($37.4M) added back, partly offset by a working-capital build (ΔNWC $424.4M in the maintenance calc, financials_history.csv).
- **WIDE_SCENARIO_SPREAD** (5.20x): real — the outcome genuinely hinges on whether the Magic step-up is a new run rate or a set-cycle peak. Confidence is low, and the verdict is sized to the bear end.
- **TIER_BAND** (bear D at 8.62% vs bull C at 14.71%): even the bull case does not clear 15% — only the super bull (10%) does. Position sizing, if any, belongs at the bear end.
- **HIGH_NET_DEBT** (preliminary run, 3.5x on the median base; 2.27x on the TTM base in the final diagnostics): balance sheet stated from the filing above — $3,264.9M total debt against $776.2M cash, equity of only $565.5M after impairments, plus a $2.80/yr dividend to service. Levered OE can shrink fast in the bear cases; that is priced into the widened bear weight.

## My thoughts / overlay
- The honest headline is the method range: preliminary run on the normalized median base ($5.06/share) gave weighted IRR 8.92%, IV@15% $49.36, Tier D; the final TTM-base run gives 11.38%, $69.29, Tier C. Both bases are filing-derived; the disagreement is about whether H1 2026's cash step-up persists. Either way, at $98.76 the stock does not clear Andrew's 15% hurdle — the argument is only about how far short it falls.
- Quality split: Wizards at ~41–45% segment operating margins with a 30-year franchise is a genuinely good business trapped inside a leveraged, impairment-prone toy company. The $1,021.9M goodwill write-down and the $56M cancelled-games impairment in Q2 2026 are a pattern of capital-allocation misses, not one-offs to wave away.
- Cash discipline is the offset: OCF has been positive every year in the history, capex is tiny ($63.3M FY2025), and the dividend ($2.80/yr DPS) is covered by the conservative OE even in FY2025 ($749.5M OE vs ~$392.5M dividends paid per the FY2025 release).
- Street context (street.json, non-blocking enrichment): consensus Buy, n=11, target $108.73 — the Street is pricing the Magic story at face value; this sweep's weighted IV@15% is well below both price and target.
- Data/enrichment: fundamentals, prices, segments, statements, profile and reprice all completed (live.json written). Segments note: an intersegment-eliminations reconciling row was dropped by segments.py because the remaining rows already tie to the consolidated total. Profile warning: no employee headcount sentence found in the 10-K — cosmetic only.

## Final verdict
- **Final tier: C** (weighted IRR 11.38% on the TTM base; method range D→C across the two filing-derived bases)
- Confidence: **Low** (wide scenario spread, OE volatility, and the verdict's dependence on the TTM-vs-median base choice)
- One-liner: Two-speed IP company (Magic/D&D strong, toys weak), moat 5/10 — even on the stepped-up TTM base it returns 11.4% weighted (IV@15% $69.29 vs $98.76 price), so it does not clear 15% until ~$69; on the normalized median base it is a D.
