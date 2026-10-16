# SN — SharkNinja, Inc.
v5 run, 2026-10-15. Market cap $26.47B at $186.32 (nasdaq_quote_api) — in scope (<$40B).

All figures below are copied from dcf_numbers.json, ttm.py output (ttm.json), or financials_history.csv — none are recomputed.

## What it is
Consumer small-appliance product company behind two brands: Shark (floorcare, home environment, beauty — hair tools, skincare devices) and Ninja (kitchen: cooking, beverage, outdoor). Design-and-marketing-led, manufacturing outsourced to Southeast Asia contract manufacturers. Spun out of JS Global Lifestyle in July 2023; Xuning Wang (JS Global chair) remains controlling shareholder. Growth engine is category creation and viral/social marketing (~25 launches a year — CREAMi, SLUSHi, Luxe Café), sold omnichannel (mass retail, Amazon, DTC, TikTok Shop). Q2 2026: net sales +22.2% YoY to $1.77B (domestic +15.5%, international +36.6%), adjusted EPS $1.26, adjusted EBITDA $265M (+18.6%); management raised FY2026 guidance to sales growth of 16–17%, adjusted EPS $6.45–$6.55, adjusted EBITDA $1.36–$1.37B (partly reflecting an expected ~$247.1M tariff-refund benefit to be recognized in Q3 2026 — a one-off NOT in the TTM base below, which ends Q2 2026).

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** revenue $6,399,188,000; net income $701,374,000; operating cash flow $634,132,000; capex $146,082,000; SBC $43,872,000.
- **Conservative owner's earnings FY2025: $444,178,000 = $3.13/share** (latest FY OE/share, dcf_numbers.json).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $392,153,000 — same ballpark as the conservative figure, which raises confidence in the level.
- OE positive 5 of the last 5 fiscal years. Balance sheet is roughly neutral: net debt −$41,150,000 (small net cash, dcf_numbers.json) against guided FY2026 capex of $190–210M (per Q2 reporting) — the balance sheet neither helps nor hurts the verdict.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $634,132,000 − prior YTD −$63,938,000 + current YTD $275,499,000 = **TTM $973,569,000** (prior-year H1 OCF was negative — seasonal working-capital outflow)
- Capex: FY $146,082,000 − prior YTD $60,093,000 + current YTD $83,056,000 = **TTM $169,045,000**
- SBC: FY $43,872,000 − prior YTD $22,478,000 + current YTD $77,523,000 = **TTM $98,917,000** — note SBC more than doubled TTM vs FY2025; it is charged in full as a real cost.
- Shares (current-YTD weighted diluted): **142,056,803**
- **TTM OE total $705,607,000 → base OE/share $4.97** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $1.59/share — rejected as the base: it is the FY2024 figure and lags a genuine ramp (see BASE_DIVERGENCE below). It is retained in the method range under Thoughts.

## Moat: 5/10 — moderate/narrow
Justification: two genuinely strong consumer brands with leading share in many categories and a repeatable product-creation/marketing machine, but no lock-in of any kind — every purchase is a fresh contest, growth is hit-driven, and pricing sits deliberately below premium rivals, which caps pricing power.
- FOR: Shark and Ninja brands hold leading positions in numerous US small-appliance and floorcare categories; a proven category-creation engine (~25 launches/yr — CREAMi, SLUSHi, Luxe Café, CryoGlow beauty) rather than one hit; social-first + omnichannel distribution flywheel (mass retail, Amazon, DTC, TikTok Shop) that converts launches fast; supply-chain agility — roughly 90–100% of US volume moved out of China, a tariff-mitigation lead rivals have not matched; premium-but-accessible pricing with adjusted gross margin ~48.7% in Q2 2026 despite tariff pressure.
- AGAINST: no recurring revenue, consumables lock-in, or switching costs — consumers re-decide every category purchase; hit-driven growth can stall if the launch cadence falters (core US categories are mature, mid-to-high-single-digit growers per management); intense competition (Dyson, iRobot, Breville, Keurig, private label) with patent litigation a constant; retailer/shelf-space concentration — distribution is rented, not owned; tariffs remain a live cost headwind across Southeast Asia supply, and the expected ~$247.1M refund is one-off; controlling shareholder (Xuning Wang / JS Global ties) and product-safety recall risk (1.8M-unit Ninja Foodi pressure-cooker recall, May 2025).
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — v5 final run (2026-10-15)
Growth sanity check: the engine's blended growth is 17.79%, adjusted −0.74pp for the +0.74%/yr share-count trend (mild dilution, offset by buybacks) to g_base 17.05%. That base start sits exactly on management's raised FY2026 sales-growth guidance of 16–17% and below Q2 2026's +22.2% print — defensible, since Q2 is the strongest recent quarter and the full-year guide is the company's own anchor. The blend's OE/share CAGR component (98.15%) is an artifact off the separation-depressed 2023 base and was NOT allowed to lift the starts (the median-based blend already trims it). Default offsets and multipliers kept; probabilities at defaults 10/25/30/25/10. Super-bull start (29.05%) exceeds the best recent sales print (22.2%) — that is deliberate for a 10% tail case and rests on operating leverage (OE grew far faster than sales in FY2025 as margins expanded), not on a sales forecast. Price $186.32.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | 5.05% | 0.75 | Launch cadence stalls, tariffs bite, US consumer fades | $33.97 | 4.84% |
| Bear | 25% | 12.05% | 0.90 | Growth decays to core-category rate; margin pressure sticks | $54.41 | 6.44% |
| Base | 30% | 17.05% | 1.00 | Guided FY26 growth, fading over the 8.5-yr CAP | $74.12 | 7.94% |
| Bull | 25% | 22.05% | 1.10 | Q2 pace holds; international + new categories keep compounding | $99.73 | 9.77% |
| Super bull | 10% | 29.05% | 1.25 | Category-creation machine runs hot for years | $149.61 | 12.94% |

- **Probability-weighted: IV@15% $79.13 (−57.53% vs price), IV@12% $108.35, IV@10% $141.31, weighted IRR 8.34%, base-case IRR 7.94%**
- **Tier by numbers: D.** Diagnostics (dcf_numbers.json): OE yield 2.67% (on the TTM base), terminal value 21.77% of IV@15%, scenario spread 4.40x, net debt −0.06x normalized OE (net cash), 9.46 months since FY end.
- Even the super-bull case does not clear the hurdle at this price: its IV@15% of $149.61 sits below the $186.32 price and its IRR is 12.94%.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.46 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, inputs quoted above. TTM OE/share $4.97 vs latest FY $3.13 confirms the business kept growing after FY end; the FY-only base would understate run-rate OE.
- **BASE_DIVERGENCE** (latest FY OE/share $3.13 vs 3-yr median $1.59): the median is the distorted one. The last-3-FY OE series (filed totals $110,894,000 / $224,402,000 / $444,178,000, from financials_history.csv) is a genuine ramp, not a spike: revenue rose from $4,253,710,000 (2023) to $6,399,188,000 (2025) and OCF from $280,601,000 to $634,132,000 as post-separation margins normalized. The median ($1.59/share) is simply the middle year of a steep climb. TTM base used; the median-base run is kept in the method range below.
- **NI_OCF_DIVERGENCE** (2023: net income $167,078,000 vs OCF $280,601,000): 2023 net income was depressed by the JS Global separation — transaction/separation costs, non-deductible items, shareholder-funded executive bonuses and withholding taxes (GAAP effective tax rate ~43% that year per company reporting) plus divested SNJP/APAC effects — while OCF adds back non-cash SBC of $46,966,000. The OCF-based conservative OE series is used throughout, so the depressed GAAP net income does not contaminate the base; the divergence is explained, not ignored.
- **OE_VOLATILE** (OE/share range >3x over 5 years): real but mostly a level shift, not cyclicality — 2021–23 OE was held down by the pre-separation structure and separation costs, 2024–TTM reflects the standalone margin structure. Residual hit-driven cyclicality is genuine for consumer durables, handled by 35% combined weight on bear/super-bear and the 0.75–0.90 multipliers there.
- **WIDE_SCENARIO_SPREAD** (4.40x): real — outcomes hinge on how long the launch engine compounds. Confidence is capped at medium and the verdict is sized to the conservative end; note the spread does not straddle the hurdle — even the top end fails it.
- **LOW_OE_YIELD** (preliminary run, on the median base: 0.85%): resolved by the TTM base — OE yield is 2.67% on $4.97/share. Still low in absolute terms: at $186.32 the valuation rests mostly on growth, which is exactly what the scenario table prices.

## My thoughts / overlay
- Method range: defensible bases span weighted IRR 4.50% (median base $1.59, preliminary run, weighted IV@15% $25.34) to 8.34% (TTM base $4.97) — **both Tier D**. Unlike APP, the method choice does not change the verdict; the stock fails the 15% hurdle on every defensible base, and even the 10%-weighted super-bull case (12.94% IRR) fails it.
- Quality is real: 13 consecutive quarters of double-digit sales growth per Q2 reporting, adjusted EBITDA margin 17.7% in FY2025, roughly neutral balance sheet, buybacks running ($99.7M in Q2 2026). The problem is purely price: $186.32 capitalizes years of flawless category creation.
- Watch items: SBC is rising fast (TTM $98,917,000 vs FY2025 $43,872,000) — a real, growing owner cost already charged in full here; the ~$247.1M tariff refund will flatter Q3 2026 reported results and OCF when received and must not be read as run-rate OE; tariff rates on Southeast Asia production remain the swing cost factor; Foodi recall litigation is a live tail risk.
- Margin of safety: the price that clears 15% on the weighted case is the weighted IV@15% itself, **$79.13** — the current price is more than double that. There is no margin of safety at $186.32 under any scenario in the table, including super bull ($149.61).

## Final verdict
- **Final tier: D** (weighted IRR 8.34% on the v5 final TTM-base inputs; the method range is D on every defensible base)
- Confidence: **Medium** (clean filings and a filing-direct TTM base; capped by the 4.40x scenario spread and hit-driven growth)
- One-liner: High-quality hit-driven appliance brands, moat 5/10 — at $186.32 even the super-bull case returns only 12.9%; weighted IRR 8.3% (Tier D), and it clears 15% only at or below $79.13.
