# ZTO — ZTO Express (Cayman) Inc.
Engine 5.4.0 run, 2026-10-16. Price $20.17 (nasdaq_quote_api). Market cap est. $16,555,591,729.71 (dcf_numbers.json) — in scope under $40B. 20-F filer (FY ends Dec 31), reporting currency CNY, ADS listed on NYSE.

All figures below are copied from dcf_numbers.json, financials_history.csv, ttm.py output, or fundamentals.json — none are recomputed.

## What it is
China's leading express delivery company by parcel volume ( #1 since 2016; 19.9% share in Q2 2026 per the company's Q2 2026 release). Network-partner model: the company owns and operates the middle mile — 93 sorting hubs with 596 automation lines, approximately 3,800 line-haul routes, over 10,000 owned line-haul vehicles (FY2025 20-F, via profile.json) — while over 6,000 direct network partners run over 31,000 pickup/delivery outlets and approximately 100,000 last-mile posts; coverage is over 99% of China's cities and counties. Core express delivery plus value-added logistics (KA / reverse logistics, retail parcels, cross-border, cold chain, LTL, warehousing).

## Owner's earnings
**FY2025 (20-F via EDGAR, from financials_history.csv, USD as converted by the engine):** operating cash flow $1,711,461,000; capex $745,632,000; SBC $32,782,000 (always a real cost — here it is small, ~2% of OCF).
- **Conservative owner's earnings FY2025: $933,047,000 = $1.14/share** (latest FY OE/share $1.1367493410837848 in dcf_numbers.json)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): **−$416,228,000 in FY2025** — distorted by the ΔNWC leg of $1,714,746,000 in financials_history.csv, not by the operating business; the OCF-based conservative figure is the cleaner one and is the series used throughout. (The maintenance series printed $1,473,398,000 in FY2023 and $2,001,209,000 in FY2024, so FY2025's negative print is a working-capital swing, not a collapse.)
- OE positive 4 of the last 5 fiscal years (dcf_numbers.json): the miss is FY2021 (−$0.26568937985137625/share), when capex of $1,311,944,000 ran ahead of OCF of $1,133,010,000 during the hub/truck build-out. Capex remains structurally heavy for this model — $745,632,000 in FY2025 against D&A of $483,259,000 — which is why OE/share has barely grown (OE/share CAGR 2y: 1.46%) even as revenue compounded.
- Balance sheet on the engine's basis: net debt $131,971,000 (debt $1,563,601,000, CURRENT_ONLY:ShortTermBorrowings, minus cash $1,431,630,000), lease liabilities $57,348,000, net debt 0.15x normalized OE (diagnostics). The engine's cash tag excludes short-term investments, so this net-debt print is an upper bound; leverage is immaterial to the verdict either way.

**Base used = normalized median of the last 3 fiscal years' OE/share: $1.1042046060402482/share** (base_source: median_of_last_3_fy_oe_per_share; the three years are $1.1042046060402482 / $0.9644687181884642 / $1.1367493410837848). The latest FY ($1.14) sits just above the median, so the median is not stale-optimistic or stale-pessimistic; no base override was needed or taken.

## Moat: 5/10 — moderate / narrow
Justification: scale and density are real, returns are only mid-teens, and the product is a commodity the customer can re-tender.
- FOR: #1 by parcel volume in China since 2016, 19.9% share in Q2 2026 (+0.4pp YoY while industry volume grew 4.2%); density/scale cost advantage from the owned automated middle mile (93 hubs, 596 automation lines, 10,000+ owned line-haul vehicles, ~3,800 routes, 31,000+ outlets, >99% city/county coverage); network-partner last-mile model keeps the edge asset-light and partners aligned; unit economics still improving — combined unit sorting + transportation costs fell in Q2 2026 despite higher oil prices, and mix shift to KA / reverse logistics lifted core ASP +15.5% YoY in Q2 2026.
- AGAINST: commoditized service with low switching costs — platforms and merchants multi-home across SF, JD Logistics, YTO, Yunda, STO and J&T; ROIC proxy (fundamentals.json, after-tax operating income over equity + debt − cash) ran 10.7% / 13.0% / 14.8% / 15.3% / 12.9% in FY2021–25 — above the cost of capital but mid-teens, not the high through-cycle returns a 7+ moat requires; gross margin (fundamentals.json) swung 21.7% / 25.6% / 30.4% / 31.0% / 25.0% over the same five years, i.e. it moves with the price war rather than through it; the current ASP recovery leans partly on anti-involution regulation staying in force; China volume growth is slowing and courier social-insurance and fuel costs are rising; China/VIE ADS tail risk and CNY translation exposure.
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — engine 5.4.0 final run (2026-10-16)
Growth sanity check (mandatory): the engine blend is 11.84% (rev CAGR 5y 12.69%, rev CAGR 3y 11.03%, latest FY revenue YoY +15.74%, OE/share CAGR 2y 1.46%; share count essentially flat, share CAGR 0.02%). Recent prints: FY2025 revenue +15.74% (engine), Q1 2026 revenue +22% YoY on volume +13.2%, Q2 2026 revenue +23.0% YoY (RMB14,549.9M) on volume +6.5%, and management's FY2026 parcel-volume guidance is 6–10%. The base scenario start (11.84%) sits **below** the recent revenue prints — written reason: the 2026 revenue spike is ASP/mix-driven (core ASP +15.5% in Q2 2026, mostly KA/reverse-logistics mix), not volume-driven, volume guidance is only 6–10%, and OE/share — the thing being projected — has compounded at only 1.46% over two years because capex absorbs the operating gains. Projecting OE/share growth at the revenue print would double-count the mix shift. The super-bull start (23.84%) is in line with the latest revenue prints, not below them, so no scenario start is left unjustified. Default offsets (−12/−5/0/+5/+12pp) and OE multipliers (0.75/0.90/1.00/1.10/1.25) and default probabilities (10/25/30/25/10) were kept: the anti-involution pricing recovery supports the bull side, slowing volume and the one-off CNY344.3M tax refund inside Q2 2026's adjusted net income (+50.3%) argue against skewing probabilities upward. Price $20.17.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -0.2% | 0.75 | Price war returns; volume stalls; capex stays heavy | $6.08 | 6.17% |
| Bear | 25% | 6.8% | 0.90 | Volume grows at guidance low end; ASP gains fade | $9.76 | 8.70% |
| Base | 30% | 11.8% | 1.00 | Blend trajectory; mix gains partly retained | $13.32 | 11.02% |
| Bull | 25% | 16.8% | 1.10 | Anti-involution pricing holds; KA/reverse mix keeps lifting ASP | $17.97 | 13.79% |
| Super bull | 10% | 23.8% | 1.25 | 2026 revenue momentum converts to OE/share at last | $27.05 | 18.44% |

- **Probability-weighted: IV@15% $14.24 (−29.4% vs price), IV@12% $19.28, IV@10% $24.94, weighted IRR 11.62%, base-case IRR 11.02%**
- **Tier by numbers: C.** Diagnostics (dcf_numbers.json): OE yield 5.47%, terminal value 20.63% of IV@15%, scenario spread 4.45x, net debt 0.15x normalized OE, 9.49 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (latest FY ended 9.49 months ago): `ttm.py ZTO` was run and exits non-zero — it cannot assemble a TTM for this 20-F filer from EDGAR companyfacts (no quarterly 10-Q facts; it reports no annual FY fact under its assembly for OCF/SBC/shares and refuses to zero-fill). Per the worker spec for such filers, the normalized median base is used and that is stated here plainly: **the base is FY2023–25 median OE/share, not a TTM figure.** Cross-check in words only (no TTM OE is computed from it): the company's unaudited H1 2026 releases show revenue +22–23% YoY and parcel volume +6.5–13.2% YoY, so trading since FY end has not deteriorated against the median base; confidence is still capped at low partly for this gap.
- **FX_CONVERTED**: reporting currency CNY converted to USD at period-end ECB reference rates (frankfurter.app); flow facts use the period-end rate, not a period average; the rates used are recorded in dcf_numbers.json fx_conversion. CNY moves flow straight into the USD per-share figures.
- **USD_TRANSLATIONS_USED**: the issuer files its own USD convenience translations alongside CNY; the engine used the filed USD figures where present.
- **ADS_RATIO_APPLIED** (preliminary run: ADS_RATIO_MISSING): resolved under bounded authority (d) — judgment.json carries ads_ratio {ratio: 1.0} sourced from the filer's own FY2025 20-F cover (Section 12(b) table; the Introduction states the same ratio): each ADS represents one Class A ordinary share, so per-share figures are already per-ADS and no scaling changes any number.
- **WIDE_SCENARIO_SPREAD** (super-bull IV 4.45x super-bear IV): real — the outcome hinges on whether ASP/mix gains survive. Confidence is low, not high, and the verdict is sized to the conservative end.
- **TIER_BAND** (bear tier D at 8.70% vs bull tier C at 13.79%): the verdict spans tiers; any position sizing should use the bear end (D), per the flag's own instruction.

## Data / enrichment notes
- fundamentals.py, prices.py, statements.py and profile.py all wrote successfully. segments.py completed but produced no breakdown tables — the filing's dimensioned facts collapse to a single reportable segment equal to the consolidated total, and a 20-F filer files no 10-Qs, so no quarterly segment tables exist. That is a data-shape fact about the filing, not a scoring gap; no figure in this analysis depends on it.
- Street consensus (street.json, via profile.py): Buy, n=8, target $21.87 — noted for context only; no scored figure uses it.

## My thoughts / overlay
- The quality debate is not the issue: this is the share leader with a falling unit cost line, a near-unlevered balance sheet on the engine's basis, and SBC that is a rounding error next to OCF. The issue is conversion — a decade of revenue compounding has produced OE/share of $0.75 → $1.10 → $0.96 → $1.14 over FY2022–25 because the network eats capex. The DCF pays for OE/share growth the company has not yet demonstrated, and at $20.17 even the bull case (13.79%) does not clear 15%.
- Method range: on the median base the weighted result is Tier C (11.62%); the bear case is a D (8.70%) and even super-bull only reaches 18.44%. There is no defensible base choice in this run's outputs that gets the weighted IRR to 15% at this price — the hurdle-clearing price on the weighted case is $14.24 (IV@15%), and $9.77 clears 20%.
- What would change the verdict: two or three years of OE/share actually compounding near the base-case start (proving the ASP/mix gains convert after capex), or a price in the mid-teens. The Q2 2026 tax refund (CNY344.3M inside the +50.3% adjusted net income print) is a one-off and was not capitalized anywhere in this run.

## Final verdict
- **Final tier: C** (weighted IRR 11.62% on the normalized median base; band D to C across bear/bull, sized to the bear end)
- Confidence: **Low** (STALE_FY with no computable TTM from EDGAR, wide scenario spread 4.45x, FX-converted CNY financials — partly offset by a stable median-vs-latest base and a clean 1:1 ADS basis)
- One-liner: China's volume-leading express carrier, moat 5/10 — real scale and mid-teens ROIC, but at $20.17 the weighted IRR is only 11.6% (IV@15 $14.24); clears 15% only below ~$14.24, so size it like the bear end of its D-to-C band.
