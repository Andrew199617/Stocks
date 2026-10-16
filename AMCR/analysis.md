# AMCR — Amcor plc
v5 run, 2026-10-16. Market cap $20.286612B at $43.74 (nasdaq_quote_api) — in scope under $40B. All figures below are copied from dcf_numbers.json, financials_history.csv, or cited earnings reporting — none are recomputed.

## What it is
Global leader in consumer packaging: flexible packaging, rigid packaging, cartons and closures/dispensing for nutrition, health, beauty and wellness customers, 400+ locations in 40+ countries. On April 30, 2025 Amcor completed its all-stock acquisition of Berry Global (7.25 Amcor shares per Berry share), adding Berry's flexibles and rigid consumer packaging businesses. That deal — plus a 1-for-5 reverse stock split effective January 14, 2026 — distorts almost every historical series the engine blends, and correcting for it is the central judgment of this run (see Growth recalibration and FLAGS).

## Owner's earnings
**FY2026 (10-K via EDGAR, from financials_history.csv):** revenue $23,506,000,000; operating cash flow $2,151,000,000; capex $922,000,000; SBC $83,000,000 (always a real cost); D&A $1,479,000,000; net income $1,106,000,000; diluted shares 463,800,000; cash $1,115,000,000.
- **Conservative owner's earnings FY2026: $1,146,000,000 = $2.47/share** (dcf_numbers.json: base_oe_total_latest_fy and base_oe_per_share $2.4708926261319535).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $1,507,000,000 in FY2026 — above the conservative figure, mainly because D&A ($1,479M, swollen by Berry intangible amortization) far exceeds capex. The conservative OCF-based figure is the one used; it is the lower, cleaner anchor.
- OE positive 5 of the last 5 fiscal years (dcf_numbers.json: 5/5).
- **Base used = normalized base, median of last 3 FY OE/share = $2.4708926261319535/share** (base_source: median_of_last_3_fy_oe_per_share). Here the median and the latest FY are the same number: FY2026 is both the middle value of the last three years and the first full year of the combined Amcor+Berry company on a split-adjusted share count, so the median is not dragged by pre-merger years the way it usually is — it is the cleanest base available. No TTM override: FY2026 ended 2026-06-30, only 3.55 months before this run (no STALE_FY flag), and FY2026 already contains a full year of Berry.
- Balance sheet: the engine's net_debt_latest is null (recent debt tags are blank in the filed history), so no engine net-debt figure is quoted. Per Amcor's FY2026 earnings reporting (August 2026), net debt was $12.9 billion at June 30, 2026 at 3.5x leverage, with management expecting to recover more than $500M of Middle East-conflict working-capital / integration cash impacts over the following 12 months and targeting ~3.0x leverage by end of calendar 2027. That leverage is folded into the verdict below — this is a levered equity, not a net-cash compounder.

## Growth recalibration — written reason (mandatory sanity check)
The engine's preliminary run produced g_base 19.88% (blend 14.88% + 5.00pp share-count adjustment) and a naive weighted IRR of 15.09% (Tier B). **That growth rate is an artifact, not a print, and was rejected:**
- Latest revenue YoY +56.61% and the 3-yr/5-yr revenue CAGRs (16.95% / 12.82%) straddle the Berry acquisition: FY2026 included approximately $7.9 billion of acquired net sales (FY2026 earnings reporting), while **organic volume was −2% for FY2026** and Q4 organic volume/price-mix was −1%.
- The +5pp share-count adjustment comes from a share_cagr of −32.01%/yr that does not describe buybacks at all (see BUYBACK_TAILWIND below): pre-2024 share counts in the filed history were not restated for the 1-for-5 reverse split, and Berry actually *increased* the split-adjusted share count.
- The prints that describe the underlying business: FY2026 adjusted EPS $4.02, +13% vs FY2025's $3.56 (earnings reporting — adjusted figures exclude the integration/amortization charges the conservative OE definition bears); Q4 FY2026 adjusted EPS $1.23, +23% YoY; guidance for double-digit adjusted EPS growth in calendar 2027, helped by Berry synergies ($285M delivered in FY2026 toward a $650M target by FY2028). Amcor is also shifting its fiscal year-end from June to December, with adjusted EPS of $1.80–$1.90 guided for the six-month transition period ending Dec 31, 2026.
- Scenario starts were therefore set in absolute terms via offsets vs g_base (−0.2388 / −0.1688 / −0.1188 / −0.0688 / −0.0188): super bear −4%, bear +3%, **base +8%**, bull +13%, super bull +18%. Base +8% sits *below* the +13% adjusted-EPS print for a written reason: adjusted EPS strips out charges that conservative OE carries, the synergy tailwind is front-loaded and fades, and organic volumes are currently negative. Bull +13% equals the adjusted print; super bull +18% requires synergy over-delivery plus a volume recovery. Probabilities kept at the 10/25/30/25/10 defaults; OE multipliers at the 0.75/0.90/1.00/1.10/1.25 defaults.

## Moat: 5/10 — moderate / narrow
Justification: the largest consumer-packaging supplier globally, with real qualification switching costs and plant-network density, but largely commoditized products sold to FMCG customers with far more bargaining power, pass-through (not earned) pricing, and low returns on capital through the cycle.
- FOR: Global scale — largest consumer packaging supplier, 400+ locations in 40+ countries
- FOR: Customer qualification switching costs in food and healthcare packaging
- FOR: Dense plant network located close to FMCG customers
- FOR: Materials-science and sustainability innovation; Berry adds dispensing and closures
- FOR: $650M Berry synergy program with $285M already delivered in FY2026
- AGAINST: Largely commoditized products; customers are powerful global FMCG groups
- AGAINST: Resin/raw-material costs are passed through — pricing power is contractual, not structural
- AGAINST: Low returns on capital through the cycle for a capital-intensive plant base
- AGAINST: High leverage — reported net debt $12.9B at ~3.5x (FY2026 earnings reporting)
- AGAINST: Organic volumes negative in FY2026 (−2%); regulatory/sustainability pressure on plastics packaging
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — v5 final run (2026-10-16)
Final engine pass: `--moat 5 --probs 0.10,0.25,0.30,0.25,0.10 --offsets -0.2388,-0.1688,-0.1188,-0.0688,-0.0188`, multipliers at defaults. Price $43.74.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -4.0% | 0.75 | Volumes keep falling, resin/inflation squeeze, deleveraging stalls | $11.58 | 5.59% |
| Bear | 25% | 3.0% | 0.90 | Synergies land but organic growth stays near zero | $18.62 | 7.84% |
| Base | 30% | 8.0% | 1.00 | Synergy ramp + modest volume recovery, fading to terminal | $25.46 | 9.96% |
| Bull | 25% | 13.0% | 1.10 | Guided double-digit EPS growth sustains; leverage falls to ~3x | $34.39 | 12.54% |
| Super bull | 10% | 18.0% | 1.25 | Synergy over-delivery plus volume and margin expansion | $47.90 | 16.03% |

- **Probability-weighted: IV@15% $26.84 (−38.64% vs price), IV@12% $35.98, IV@10% $46.21, weighted IRR 10.40%, base-case IRR 9.96%**
- **Tier by numbers: C.** Diagnostics (dcf_numbers.json): OE yield 5.65%, terminal value 19.63% of IV@15%, scenario spread 4.14x, 3.55 months since FY end.

## Flags — every fragility flag resolved
- **BUYBACK_TAILWIND** (share count shrinking 32.0%/yr): **artifact, not a buyback.** The filed history's share counts are 1,476,000,000 in FY2023 then 288,100,000 in FY2024 — the FY2024+ counts are retroactively adjusted for the 1-for-5 reverse split (effective January 14, 2026; outstanding shares fell from ~2.3 billion to ~461 million) while the earlier years in the series were not restated, so the computed "shrinkage" is the split. On a split-adjusted basis Berry *raised* the count (FY2025 weighted 318,600,000 → FY2026 463,800,000). Resolution: the +5pp growth credit embedded in g_base was explicitly removed by setting scenario starts in absolute terms (see Growth recalibration); no buyback tailwind is credited anywhere in the verdict.
- **OE_VOLATILE** (OE/share range over 5 years spans >3x): mostly the same split artifact — OE/share prints ~$0.46–$0.62 on unrestated pre-FY2024 share counts vs $2.47 on the split-adjusted FY2026 count — compounded by the Berry step-up in OE totals. The last-3-FY window the base is built from (FY2024–FY2026) is consistently split-adjusted, so the base itself is clean. The genuine residual volatility is integration-era earnings quality, handled by the default 35% weight on bear-or-worse scenarios rather than by widening them further.
- **NI_OCF_DIVERGENCE** (2025): FY2025 net income was $511,000,000 vs operating cash flow of $1,390,000,000. The gap is explained by the filed non-cash and deal items: D&A of $722,000,000 (stepped-up Berry intangible amortization is non-cash) plus Berry merger/integration charges depressing GAAP net income in the closing year, while cash generation held. The maintenance OE definition shows the working-capital side of that year (ΔNWC $504,000,000 outflow; maintenance OE only $149,000,000). Resolution: the base uses the OCF-based conservative definition throughout, so the depressed GAAP net income does not contaminate the base; FY2025 is also not the median year.
- **WIDE_SCENARIO_SPREAD** (super-bull IV 4.14x super-bear IV): real — the range is synergy execution vs a levered volume decline. Confidence is set to medium (and is capped there), and the verdict is sized to the conservative end.

## My thoughts / overlay
- Method range: the naive engine run (uncorrected Berry/split blend) prints Tier B at 15.09% weighted IRR; the artifact-corrected run prints Tier C at 10.40%. The B is not a defensible method — it capitalizes an acquisition as if it were organic growth — so the honest headline is C, with the spread itself documenting how much of this stock's apparent cheapness is deal arithmetic.
- Quality: a real, cash-generative franchise (FY2026 free cash flow $1.3B per earnings reporting) with a credible synergy program, but it is a low-growth, capital-intensive, levered packaging business. At $43.74 the market is paying for the bull case — double-digit EPS growth sustained and deleveraging to ~3x — while the weighted case here is worth $26.84 at a 15% discount rate.
- The price that clears 15% on the weighted case is the weighted IV@15% itself, **$26.84**; a buyer wanting a margin of safety against the bear cases ($18.62 and below) needs a price materially under that.
- Dividend and deleveraging are the equity's carrying case in the meantime, but neither changes the DCF math at this price.

## Final verdict
- **Final tier: C** (weighted IRR 10.40% on the artifact-corrected v5 final inputs; no tier override)
- Confidence: **Medium** (clean split-adjusted base and a fresh FY, offset by the 4.14x scenario spread and integration/leverage uncertainty)
- One-liner: Narrow-moat global packaging leader (moat 5/10) mid-Berry-integration — at $43.74 it prices in the synergy bull case and does not clear 15% on the weighted case (10.4% weighted IRR, IV@15% $26.84); it clears 15% only at or below $26.84.
