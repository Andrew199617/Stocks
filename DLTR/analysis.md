# DLTR — Dollar Tree, Inc.
v5 run, 2026-10-15. In scope (market cap $25,525,499,000 at $123.73, nasdaq_quote_api).

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.py output, or financials_history.csv — none are recomputed. External reporting is cited in words; where a search-reported figure is used it is attributed as such.

## What it is
Pure-play Dollar Tree discount retailer since completing the sale of the Family Dollar business on July 5, 2025 (search-reported; company release via corporate.dollartree.com). Roughly nine and a half thousand Dollar Tree stores (search-reported store count at Q2) selling consumables, variety and seasonal goods, increasingly under a multi-price format that layers $3/$5/$7 items over the traditional low base price. Latest fiscal year (ended 2026-01-31) revenue $19,395,700,000 on the continuing-operations basis (financials_history.csv).

## Owner's earnings
**FY ended 2026-01-31 (10-K via EDGAR, from financials_history.csv):** operating cash flow (continuing operations tag) $2,190,700,000; capex $1,134,000,000; SBC $58,900,000 (always a real cost).
- **Conservative owner's earnings latest FY: $997,800,000 = $4.84/share** (dcf_numbers.json: base_oe_total_latest_fy and base_oe_latest_per_share).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $1,047,500,000 for the same year (financials_history.csv) — same ballpark as the conservative figure, which supports the base's order of magnitude.
- OE positive 5 of the last 5 fiscal years. Net debt $1,713,900,000 (dcf_numbers.json), 1.72x normalized OE (diagnostics) — a real but not crushing load for a retailer; it is in the verdict via the low OE yield, not as a separate haircut.
- Capex is the structural drag: at $1,134,000,000 against D&A of $648,100,000 (financials_history.csv), the standardized model charges all of it — new stores, remodels and multi-price conversions included — against owner's earnings. That conservatism is the sweep's standard, and it is why OE/share sits well below reported EPS.

**TTM check (ttm.py, filing-direct, full inputs):**
- OCF: FY $2,190,700,000 − prior YTD $639,200,000 + current YTD $1,565,500,000 = **TTM $3,117,000,000**
- Capex: FY $1,134,000,000 − prior YTD $493,900,000 + current YTD $498,800,000 = **TTM $1,138,900,000**
- SBC: FY $58,900,000 − prior YTD $31,600,000 + current YTD $40,700,000 = **TTM $68,000,000**
- Shares (current-YTD weighted diluted): **194,100,000**
- **TTM OE total $1,910,100,000 → TTM OE/share $9.84**

**Base used = the engine's normalized base, $4.84/share (median of last 3 FY OE/share; here the median and the latest FY coincide). The TTM base was run, quoted, and NOT adopted**, for three documented reasons:
1. The TTM window's OCF leg is flattered by one-offs: the current-YTD OCF of $1,565,500,000 more than doubles the prior-YTD $639,200,000, and the company's own Q2 reporting (search-reported) attributes a large part of the surge to tariff refunds received in the quarter — cash the company says it is reinvesting back into pricing, stores and operations in the second half, with only a partial net benefit retained in full-year guidance. A refund received is real cash; treated as a permanent OE run-rate it is not.
2. Working-capital release: Q1 reporting (search-reported) highlighted a deliberate inventory reduction — inventory fell while sales rose — which converts a balance-sheet level shift into one year's OCF. It does not repeat annually.
3. The TTM denominator is the current-YTD share count (194,100,000), below the latest FY diluted count (206,300,000) after accelerated buybacks, which lifts the per-share figure beyond the cash actually generated per share outstanding over the window.
The TTM figure is therefore disclosed as the top of the method range (see Thoughts), not used as the base. A full engine run on the TTM base (default probabilities, moat 5) printed weighted IRR 11.90%, weighted IV@15% $92.09, Tier C — even the flattered base does not clear 15% at this price.

## Moat: 5/10 — moderate/narrow
Justification: Store density, purchasing scale and a proven ability to move the price architecture (the $1.25 reset, then multi-price) are real, but there are no switching costs, Walmart and Dollar General contest the same basket with deeper pockets, the mix is import- and tariff-exposed, and the core customer is financially squeezed.
- FOR: Store density and proximity across roughly nine and a half thousand stores (search-reported) — the closest, fastest trip for fill-in consumables
- FOR: Purchasing scale across the fleet and a low-cost small-box operating model
- FOR: Multi-price format broadens the ticket and is drawing higher-income shoppers (search-reported), reducing dependence on the most squeezed cohort
- FOR: Demonstrated pricing flexibility — the base price point was reset and higher price tiers added without breaking traffic
- AGAINST: No switching costs and no pricing power against Walmart; Dollar General and Five Below contest the same value customer
- AGAINST: Import-heavy assortment — tariff costs and refunds have swung reported results in both directions within a year
- AGAINST: Core low-income customer squeezed by cumulative food/fuel inflation; traffic growth is thin and ticket-led
- AGAINST: Thin operating margins leave little buffer for shrink, wage or freight shocks
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — v5 final run (2026-10-15)
Probabilities bear-skewed to 15/30/30/15/10 (defaults 10/25/30/25/10) because the OE_VOLATILE flag directs a wider bear weight and the current year's cash print is one-off-flattered. Offsets and multipliers are the defaults (−12/−5/0/+5/+12pp; 0.75/0.90/1.00/1.10/1.25). Engine g_base is 4.03% (blend 1.31% + 2.71pp buyback adjustment).
**Growth sanity check:** the base start (4.03%) sits below the recent revenue prints — latest FY revenue +10.42% YoY, 3-yr revenue CAGR +7.95% (both continuing basis, dcf_numbers.json), and post-FY quarters reporting sales growth with comparable sales guided at 3–4% for the current year (search-reported). The written reason: revenue growth has not converted to OE/share growth in this history — OE/share CAGR (2y) is −13.33% on working-capital swings and tariff costs absorbed in the base years — and current-year guidance itself embeds reinvestment of the tariff refund and an assumed tariff-rate step-up in the second half (search-reported). Bull (9.03%) and super-bull (16.03%) starts exceed recent OE prints deliberately and only as tails: they require multi-price mix gains plus buyback compounding (share count shrinking 2.7%/yr, already credited in g_base) to convert revenue growth into OE/share growth at a rate the last three years did not show; super-bull carries only a 10% weight and a 1.25x multiplier on a normalized base that excludes the refund flattery.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | -7.97% | 0.75 | Tariff step-up lands, low-income traffic turns negative, refund reinvestment buys nothing | $19.18 | 4.18% |
| Bear | 30% | -0.97% | 0.90 | Comps stall at the low end; margins give back the multi-price gains | $30.88 | 5.51% |
| Base | 30% | 4.03% | 1.00 | Guided comp growth plus store growth, OE conversion at the normalized rate | $42.26 | 6.82% |
| Bull | 15% | 9.03% | 1.10 | Multi-price keeps lifting ticket; buybacks compound per-share OE | $57.17 | 8.51% |
| Super bull | 10% | 16.03% | 1.25 | Turnaround fully annualizes at TTM-level cash generation with growth | $86.53 | 11.58% |

- **Probability-weighted: IV@15% $42.05 (−66.02% vs price), IV@12% $55.74, IV@10% $70.99, weighted IRR 6.85%, base-case IRR 6.82%**
- **Tier by numbers: D.** Diagnostics (dcf_numbers.json): OE yield 3.91%, terminal value 18.53% of IV@15%, scenario spread 4.51x, net debt 1.72x normalized OE, 8.44 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 8.44 months ago): ttm.py was run and its full inputs are quoted above. The TTM base ($9.84/share) was NOT adopted, for the three documented reasons in the OE section (tariff-refund cash in the current-YTD OCF leg, inventory working-capital release, and a shrunken TTM share denominator). The median base is used and the TTM run is disclosed as the top of the method range. Post-FY evidence checked: Q2 (search-reported) showed sales +7.0% and comparable sales +3.7% with full-year guidance raised — no deterioration the median base is hiding; the staleness cuts in the flattering direction here, not the harmful one.
- **BUYBACK_TAILWIND** (share count shrinking 2.7%/yr): already credited via the +2.71pp share-count adjustment inside g_base (dcf_numbers.json); not double-counted in the verdict. Buybacks have since accelerated (search-reported repurchases in Q2), which is one reason the TTM share denominator is flattering — see STALE_FY.
- **OE_VOLATILE** (OE/share range over the last 5 years spans >3x): real and visible in financials_history.csv — conservative OE totals swing from $330,400,000 (year ended 2022-01-29) to $1,414,400,000 (year ended 2024-02-03) within the last five years on working-capital swings (the ΔNWC column swings by billions year to year). Handled as directed: the normalized median base is used instead of any single year, and the bear-side probability weight was raised (super bear + bear = 45%).
- **NI_OCF_DIVERGENCE** (net income and OCF differ by >40% in 2024, 2025, 2026): resolved year by year from financials_history.csv plus the Family Dollar disposal. The engine's net income is the total-company figure including discontinued operations, while the OCF tag for the two most recent years is continuing-operations only — the bases are mixed by construction. Year ended 2024-02-03: net income −$998,400,000 vs OCF $2,684,500,000 — the GAAP loss is the Family Dollar discontinued business, including its goodwill impairment (non-cash; search-reported from the 10-K discontinued-operations note). Year ended 2025-02-01: net income −$3,030,100,000 vs continuing OCF $2,193,300,000 — again the discontinued business: the loss on classifying Family Dollar as held for sale and further goodwill impairment, both non-cash and both in discontinued operations, while the Dollar Tree banner's cash generation continued. Year ended 2026-01-31: net income $1,282,500,000 vs continuing OCF $2,190,700,000 — the gap here is mostly structural: D&A of $648,100,000 is added back in OCF, and the two series still sit on different (total vs continuing) bases in the disposal year. Consequence: the OCF-based conservative OE is the series used throughout; the divergence is a disposal-accounting artifact, not evidence the OE base is misstated.
- **WIDE_SCENARIO_SPREAD** (super-bull IV 4.51x super-bear IV): real — the outcome range turns on whether TTM-level cash generation is a run-rate or a refund/WC artifact. Confidence is set to low and the verdict is sized to the conservative (median-base) end.
- **Basis break (agent-identified, not an engine flag):** the history straddles the Family Dollar disposal. Revenue rows through the year ended 2022-01-29 ($26,309,800,000) are the old two-banner total company; rows from the year ended 2023-01-28 onward are the Dollar Tree-only continuing basis. The 5-yr revenue CAGR (−5.33%) straddles that break and is not a usable growth signal; the blend's median construction limits its damage, and the growth inputs above lean on the continuing-basis signals (3-yr CAGR +7.95%, latest YoY +10.42%) instead.

## My thoughts / overlay
- The honest headline is the method range: **D on the normalized base (weighted IRR 6.85%, IV@15% $42.05) to C on the TTM base (weighted IRR 11.90%, IV@15% $92.09)** — and both ends sit below the $123.73 price. The investment question is not the tier, it is whether the buyer believes the refund- and working-capital-flattered TTM cash print is the new run-rate; the company's own guidance, which retains only part of the refund benefit and spends the rest, says it is not.
- Quality is genuinely improving: the Family Dollar drag is gone, multi-price is lifting ticket, traffic was positive in Q2 (search-reported), and buybacks are shrinking the count. None of that is free at this price — at $123.73 the market is already capitalizing the TTM run-rate the filings do not yet support as recurring.
- Balance sheet: net debt $1,713,900,000 at 1.72x normalized OE is manageable and is not the story; the story is OE conversion — a full year of guided-level sales growth produced a normalized OE yield of only 3.91% at this price.
- Price that clears 15%: the weighted IV@15% of **$42.05** on the normalized base; even on the flattered TTM base the clearing price is its IV@15% of $92.09 — still well below the current price. A buyer demanding a margin of safety against the bear cases needs a price below the bear IV@15% of $30.88.

## Final verdict
- **Final tier: D** (weighted IRR 6.85% on the normalized base; method range D to C, sized to the conservative end because the TTM base is one-off-flattered)
- Confidence: **Low** (wide scenario spread 4.51x and a 2x disagreement between the two defensible bases)
- One-liner: Narrow-moat discounter (5/10) genuinely improving after the Family Dollar exit, but at $123.73 the price capitalizes a tariff-refund-flattered TTM run-rate — weighted IRR 6.8%, IV@15 $42.05 on the normalized base; clears 15% only below ~$42, and below ~$92 even on the TTM base.
