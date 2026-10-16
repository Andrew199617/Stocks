# PKG — Packaging Corporation of America
v5 run, 2026-10-15. All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.py output, or financials_history.csv — none are recomputed.

## What it is
Third-largest producer of containerboard in North America and a leading producer of uncoated freesheet paper. Vertically integrated: mills produce containerboard that is pulled through its own network of corrugated products plants, plus a smaller Paper segment. Completed the acquisition of Greif's containerboard business (two mills, ~800,000 tons of capacity, eight sheet feeder / corrugated plants) for $1.8B in cash effective August 31, 2025, funded with cash on hand and new term loans / senior notes. Market cap $20.83872B at $232.575 (nasdaq_quote_api) — in scope under $40B.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $1,557,500,000; capex $828,900,000; SBC $45,200,000.
- **Conservative owner's earnings FY2025: $683,400,000 = $7.627232142857143/share** (latest FY OE/share, dcf_numbers.json)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $650,900,000 — same ballpark as the conservative figure, which raises confidence in the base level.
- OE positive 5 of the last 5 fiscal years. History is cyclical and capex-lumpy: conservative OE was $805,400,000 in FY2023, $472,700,000 in FY2024, and $683,400,000 in FY2025 (financials_history.csv).
- Net debt $3,438,300,000 (dcf_numbers.json) — see HIGH_NET_DEBT under Flags.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $1,557,500,000 − prior YTD $638,700,000 + current YTD $705,300,000 = **TTM $1,624,100,000**
- Capex: FY $828,900,000 − prior YTD $317,800,000 + current YTD $370,600,000 = **TTM $881,700,000**
- SBC: FY $45,200,000 − prior YTD $28,100,000 + current YTD $32,300,000 = **TTM $49,400,000**
- Shares (current-YTD weighted diluted): **89,100,000**
- **TTM OE total $693,000,000 → base OE/share $7.777777777777778** (base_source: ttm_json)
- The engine's normalized base (median of last 3 FY OE/share) is $7.627232142857143/share — close to the TTM figure, so the base choice does not drive the verdict; the TTM base is used because it is more current and includes the Greif business for most of the period.

**TTM / recent prints:** Q2 2026 revenue was $2.49B, up 14.7% year-on-year in the search results, with GAAP EPS $2.15 — but that revenue growth is substantially the acquired Greif business, not organic growth; legacy adjusted EPS fell year-on-year on higher freight and recycled fiber costs, with record corrugated shipments. FY2025 revenue grew 7.23% (latest rev YoY in dcf_numbers.json is 7.228656972791137%). This is a low-single-digit organic grower with an acquisition overlay, not a double-digit grower.

## Moat: 5/10 — moderate / narrow
Justification: Scale, vertical integration and a dense plant network give a real freight / service cost edge in a bulky, low value-to-weight product, and a historically disciplined low-cost operating culture — but containerboard is a commodity, pricing follows industry supply/demand rather than company-specific pricing power, and larger rivals can match scale.
- FOR: Vertical integration — mills feed its own corrugated plants, insulating volume from the open containerboard market
- FOR: Scale as the third-largest North American containerboard producer, enlarged by the Greif mills and plants
- FOR: Dense corrugated plant network close to customers — freight is a major delivered cost for bulky boxes, so proximity is a structural edge
- FOR: Proven through-cycle profitability — OE positive 5 of the last 5 fiscal years
- AGAINST: Commodity product — containerboard / box pricing is industry supply/demand driven, no durable company-specific pricing power
- AGAINST: Larger, equally integrated rivals (e.g. International Paper, Smurfit Westrock) can match scale and capacity
- AGAINST: Input costs it does not control — recycled fiber (OCC), freight, energy and chemicals squeezed margins in Q2 2026 despite record volumes
- AGAINST: Cyclical end demand (consumer goods / e-commerce shipments) and industry capacity additions can pressure prices for years
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — v5 final run (2026-10-15)
Engine blended growth: g_blend 4.079604678007697%, share-count adjustment +1.1271130816981723pp (share count −1.1271130816981723%/yr), g_base 5.20671775970587%. Growth components: rev CAGR 5y 6.188473425456498%, rev CAGR 3y 1.970735930558898%, latest rev YoY 7.228656972791137%, OE/share CAGR 2y −7.930931292019383%. Default probabilities 10/25/30/25/10, default offsets −12/−5/0/+5/+12pp and default OE multipliers 0.75/0.90/1.00/1.10/1.25 were kept — the evidence is a cyclical low-single-digit organic grower, which is what the defaults describe.
SANITY CHECK: the base start (5.21%) sits below FY2025 revenue growth (+7.23%) and well below Q2 2026's +14.7% print — defensible because the Q2 print is acquisition-driven (Greif) and TTM OE already capitalizes most of a year of Greif; organic / legacy earnings fell year-on-year in Q2 2026. The super-bull start (17.21%) is above any organic print and is only defensible as a low-probability (10%) combination of announced price increases realizing, Greif synergies, and a volume cycle upswing — it is not a forecast. Price $232.575.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -6.79% | 0.75 | Containerboard price downturn + fiber/freight costs stay high; levered OE compresses | $32.42 | 4.04% |
| Bear | 25% | 0.21% | 0.90 | Flat volumes, price increases only offset input costs | $52.16 | 5.23% |
| Base | 30% | 5.21% | 1.00 | Low-single-digit organic growth + Greif synergies, normal cycle | $71.37 | 6.43% |
| Bull | 25% | 10.21% | 1.10 | Price increases stick, volumes grow, synergies exceed plan | $96.52 | 7.96% |
| Super bull | 10% | 17.21% | 1.25 | Full price + volume + synergy stack in a tight-supply market | $145.97 | 10.76% |

- **Probability-weighted: IV@15% $76.42, IV@12% $101.87, IV@10% $130.29, weighted IRR 6.78%, base-case IRR 6.43%**
- **Tier by numbers: D.** Diagnostics (dcf_numbers.json): OE yield 3.344201989800184%, terminal value 19.06400294199014% of IV@15%, scenario spread 4.5030659615832995x, net debt 4.933785076530612x normalized OE, 9.461235216819974 months since FY end.
- Method range: even the super-bull scenario (10.76% IRR, IV@15% $145.97) does not clear the 15% hurdle, and the normalized-median base preliminary run also printed Tier D — the tier does not span tiers on defensible inputs.

## Flags — every fragility flag resolved
- **STALE_FY** (latest fiscal year ended 9.461235216819974 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, quoted above with all four legs (OCF / capex / SBC / shares).
- **NI_OCF_DIVERGENCE** (net income and operating cash flow differ by >40% in 2023, 2025): explained by the capital-intensive mill model, not a one-off that distorts the base. In financials_history.csv, D&A was $517,700,000 in FY2023 against net income of $765,200,000 (OCF $1,315,100,000), and $652,800,000 in FY2025 against net income of $774,100,000 (OCF $1,557,500,000) — large non-cash depreciation on the mill base is the dominant reconciling item in both years. The base used throughout is the OCF-based conservative OE, so the NI/OCF gap does not contaminate it; the maintenance definition, which is NI-based, lands in the same ballpark in FY2025 ($650,900,000 vs $683,400,000 conservative).
- **WIDE_SCENARIO_SPREAD** (super-bull IV is 4.5030659615832995x super-bear IV): real — a cyclical commodity producer's outcome range is wide. Confidence is capped at medium (not high) for this reason, and the verdict is sized to the conservative end. Note the spread is in IV levels, not in the tier conclusion: every scenario's IRR is below 15%.
- **HIGH_NET_DEBT** (net debt is 4.933785076530612x normalized OE): folded into the verdict explicitly. Net debt is $3,438,300,000, stepped up to fund the $1.8B Greif acquisition with new term loans and senior notes. Leverage of ~4.9x normalized OE means a containerboard price downturn hits equity OE hard — that is exactly the super-bear case (OE mult 0.75, IV@15% $32.42, IRR 4.04%), which is weighted at 10% and still does not change the tier, because even the unlevered-looking bull cases fail the hurdle at this price.

## My thoughts / overlay
- Quality is not the debate: this is a disciplined, vertically integrated, through-cycle profitable operator. Valuation is: at $232.575 the market pays for an OE yield of only 3.344201989800184% on the TTM base, and no scenario in the set — including super-bull at a 17.21% growth start and a 1.25 OE multiplier — clears 15%.
- The price that clears 15% on the weighted case is the weighted IV@15% itself, $76.42; a buyer wanting a margin of safety against the bear cases would need to pay materially less than that. There is no defensible method range that reaches the hurdle — the preliminary median-base run and the final TTM-base run are both Tier D.
- Risks to the (already bearish) verdict in the other direction: announced corrugated price increases realizing faster than modeled, Greif synergies above plan, or industry capacity closures tightening supply — all of those live in the bull / super-bull cases, which still fall short at this price.
- Balance sheet watch: post-Greif leverage (~4.9x normalized OE) plus a large, lumpy mill capex program (TTM capex $881,700,000) leaves little room for a price downturn before dividends / buybacks compete with debt service.

## Final verdict
- **Final tier: D** (weighted IRR 6.78% on the v5 final inputs; no tier override)
- Confidence: **Medium** (capped by WIDE_SCENARIO_SPREAD; the tier itself is robust — every scenario is below the hurdle)
- One-liner: Quality integrated containerboard producer, moat 5/10 — does not clear 15% at $232.58 (weighted IRR 6.78%, weighted IV@15% $76.42); it would need a price near $76.42 to clear 15% on the weighted case.
