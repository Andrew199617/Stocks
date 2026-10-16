# DINO — HF Sinclair Corp
v5 run, 2026-10-15. In scope (market cap $23.271B at $124.80, nasdaq_quote_api — under the $40B cutoff).

All figures below are copied from dcf_numbers.json, ttm.py output (ttm.json), or financials_history.csv — none are recomputed.

## What it is
Independent US downstream energy company formed in March 2022 by the merger of HollyFrontier and Sinclair Oil. Five segments: Refining (the earnings engine — seven complex refineries across the Mid-Continent, Southwest, Rocky Mountains and Pacific Northwest, ~76.5% of 2025 revenues per company reporting), Renewables (renewable diesel), Marketing (Sinclair-branded stations and brand licensing), Lubricants & Specialties (base oils, white oils, waxes, finished lubricants — separation into an independent public company announced with Q2 2026 results, targeted for H2 2027, alongside retirement of the Mississauga base-oil assets), and Midstream (pipelines, terminals, tankage — partly via its MLP interest). This is a commodity refining business with diversifying side segments, not a compounder: earnings are set by crack spreads the company does not control.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** revenue $26,869,000,000; operating cash flow $1,315,000,000; capex $449,000,000; SBC $33,000,000 (always a real cost, and small here); D&A $909,000,000; net income $579,000,000.
- **Conservative owner's earnings FY2025: $833,000,000 = $4.47/share** (dcf_numbers.json: base OE latest $4.4673/share).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $1,211,000,000 — above the conservative figure because D&A ($909M) far exceeds capex ($449M) in a year of modest turnaround spend; the OCF-based conservative figure is the one used, and for a refiner it is the honest one — sustaining a refining system costs closer to D&A over a full turnaround cycle than to one light capex year.
- OE history (conservative totals, financials_history.csv): FY2021 −$357,664,000 (the one negative year — engine: OE positive 4 of the last 5 years), FY2022 $3,222,000,000, FY2023 $1,871,000,000, FY2024 $617,000,000, FY2025 $833,000,000. That is the refining cycle in one line: a war-driven supercycle peak in 2022, fading since.
- Net debt $1,791,000,000 (dcf_numbers.json), 2.15x normalized OE (diagnostics) — modest, investment-grade-style leverage; Q2 2026 reporting put cash at $2.26B against $2.77B of consolidated debt after the strong first half.

**Base used = normalized base, the median of the last 3 fiscal years' OE/share: $4.4673/share** (base_source: median_of_last_3_fy_oe_per_share; the latest FY and the median coincide at $4.4673).

**TTM was computed and deliberately NOT used as the base.** ttm.py (filing-direct, no hand math) through Q2 2026:
- OCF: FY $1,315,000,000 − prior YTD $498,000,000 + current YTD $1,967,000,000 = **TTM $2,784,000,000**
- Capex: FY $449,000,000 − prior YTD $197,000,000 + current YTD $220,000,000 = **TTM $472,000,000**
- SBC: FY $33,000,000 − prior YTD $13,000,000 + current YTD $15,000,000 = **TTM $35,000,000**
- Shares (current-YTD weighted diluted): **180,032,000**
- **TTM OE total $2,277,000,000 → TTM OE/share $12.65**
- Why rejected: H1 2026 is a peak-cycle print, not a run rate. Q2 2026 net income was $892M ($4.93/diluted share; adjusted $5.31) — the strongest quarter since 2022 — because adjusted refinery gross margin jumped 57.3% YoY to $25.95 per produced barrel on war-driven product tightness (Reuters: US refiners are the biggest beneficiaries of the Iran war, with margins past the 2022 post-invasion records and 5–7M bbl/d of global capacity offline). Analyst consensus already models 2027 earnings declining ~26% (Zacks). Capitalizing a geopolitical margin spike at $12.65/share would be the classic peak-earnings trap; the through-cycle median is the defensible base for a refiner. The TTM figure is still the bull-case anchor — see Thoughts for what it does and doesn't change.

## Moat: 3/10 — weak
Justification: A price-taking commodity refiner whose 2026 windfall was handed to it by geopolitics, not earned by any durable advantage; its real edges are locational and logistical (inland refinery placement, complexity, integration), which soften the cycle but have never repealed it — OE was negative as recently as FY2021 and the 2022 peak OE total is roughly 4x the FY2025 figure.
- FOR: Complex, flexible refineries in advantaged inland regions (Mid-Continent, Rockies, Southwest, Pacific Northwest) that capture discounted inland crude differentials and can shift crude slate and product mix
- FOR: Integrated midstream, marketing and the Sinclair brand — steadier, fee/brand-based earnings that dampen pure spot-refining exposure
- FOR: Lubricants & Specialties is a genuinely steadier, higher-margin business (top-5 North American position) — the planned H2 2027 spin-off could surface its value
- FOR: Modest balance-sheet risk — net debt $1,791,000,000, 2.15x normalized OE — so downcycles are survivable, not existential
- AGAINST: Pure price-taker on both sides — crude in, commodity fuels out; crack spreads are set by global supply/demand and geopolitics, as the war-driven 2026 spike proves in both directions
- AGAINST: No pricing power, no switching costs, no network effects in commodity gasoline/diesel/jet fuel
- AGAINST: Capital-intensive with heavy turnaround and environmental compliance capex; sustaining capex runs near D&A over a cycle, not at one light year's level
- AGAINST: Subscale versus Marathon Petroleum, Phillips 66 and Valero in procurement, logistics and turnaround execution
- AGAINST: Long-term US gasoline demand decline (EV penetration, fuel-economy gains) hangs over the terminal value of every refining asset
- A 3 gives CAP = 5.9 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 5.9 years, 15-year projection.

## DCF — v5 final run (2026-10-15)
Growth sanity check (mandatory): the engine's blend is already negative — rev CAGR 5y +19.16% (merger-inflated, see BASIS_BREAK), rev CAGR 3y −11.07%, latest rev YoY −5.99%, OE/share CAGR 2y −32.62%, g_blend −8.53%, +2.72pp buyback adjustment → g_base −5.00%. Recent prints do not contradict a negative normalized start: FY2025 revenue fell 5.99% YoY and normalized OE/share has fallen for two straight years off the 2022 peak; the H1 2026 spike is a margin event on flat volumes (Q2 crude charge +3.9% YoY), not volume or share growth, and consensus models it fading in 2027. No scenario start was raised toward the TTM spike — for a refiner the spike is the cycle, not the trend. Default offsets (−12/−5/0/+5/+12pp) and default OE multipliers (0.75/0.90/1.00/1.10/1.25) were kept; probabilities were shifted bearish (15/30/30/15/10 vs the 10/25/30/25/10 default) per the OE_VOLATILE instruction to widen bear weight, and because the stock has already re-rated ~146% in a year to its 52-week high area on the peak print. Price $124.80.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | −10.0% | 0.75 | Crack spreads collapse as war premium unwinds and capacity returns; a 2021-style downcycle | $17.54 | 4.09% |
| Bear | 30% | −10.0% | 0.90 | Normalization to soft mid-cycle margins; 2027 consensus decline (−26%) is the start, not the end | $21.05 | 4.41% |
| Base | 30% | −5.0% | 1.00 | Through-cycle margins on the normalized $4.47 base, fading over the 5.9-yr CAP | $28.06 | 5.17% |
| Bull | 15% | 0.0% | 1.10 | Tight capacity keeps margins above mid-cycle for years; L&S spin surfaces value | $36.90 | 6.14% |
| Super bull | 10% | +7.0% | 1.25 | Structural product shortage persists; elevated cracks become the new mid-cycle | $53.52 | 7.96% |

- **Probability-weighted: IV@15% $28.25 (−77.36% vs price), IV@12% $36.77, IV@10% $46.21, weighted IRR 5.22%, base-case IRR 5.17%**
- **Tier by numbers: D.** Diagnostics (dcf_numbers.json): OE yield 3.58%, terminal value 16.84% of IV@15%, scenario spread 3.05x, net debt 2.15x normalized OE, 9.46 months since FY end. Note the verdict does not hinge on the terminal value (only 16.84% of IV) or on heroic bear assumptions — even the super-bull case (7.96% IRR) does not clear a 10% return at this price.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.46 months ago): ttm.py was run and its full inputs are quoted above (TTM OE/share $12.65 through Q2 2026). The TTM base was NOT adopted: it capitalizes a war-driven crack-spread spike (Q2 gross margin $25.95/bbl, +57.3% YoY; strongest quarter since 2022) that consensus already models fading in 2027. For a cyclical refiner the normalized 3-yr median is the undistorted base — the opposite distortion from a growth inflection, and the reason is stated here as required.
- **BUYBACK_TAILWIND** (share count shrinking 2.72%/yr): already credited via the +2.72pp growth adjustment in the blend; not double-counted. It is real and continuing — a new $1.5B repurchase authorization was announced in September 2026 and Q2 returned $265M via dividends and buybacks — but buybacks at $124.80 destroy value if the normalized IV is anywhere near $28, so the tailwind is a governance concern at this price, not a plus.
- **BASIS_BREAK_SUSPECT** (>60% revenue jump in the last 5 yrs): identified — the March 2022 HollyFrontier + Sinclair Oil merger roughly doubled the company (revenue $18,389,142,000 in FY2021 → $38,205,000,000 in FY2022, financials_history.csv), and FY2022 revenue also rode the crude-price spike. Pre-2022 history is HollyFrontier-only and not comparable. Consequence: the 5-yr rev CAGR (+19.16%) is a merger artifact and was given no weight; scenario starts were anchored to normalized OE/share and post-merger years only.
- **OE_VOLATILE** (OE/share range >3x over 5 yrs): real and structural — this is the refining cycle (conservative OE totals: −$357,664,000 FY2021 → $3,222,000,000 FY2022 → $617,000,000 FY2024). Handled by (a) the normalized median base instead of any single year, and (b) bear-weighted probabilities (45% on bear-or-worse vs 35% default). Confidence held at medium, not high.
- **NI_OCF_DIVERGENCE** (2024): resolved from the filed figures — FY2024 net income was $177,000,000 against OCF of $1,110,000,000 with D&A of $832,000,000 (financials_history.csv). The gap is the non-cash depreciation load of a capital-intensive refining system (D&A alone is several times FY2024 net income), not a tax deposit, impairment one-off or working-capital trick; the OCF-based conservative OE used throughout is unaffected by it. FY2024 is also not the median year, so it does not distort the base either way.

## My thoughts / overlay
- The method range here is unusually honest because both ends fail: on the normalized median base ($4.47/share) the weighted IRR is 5.22% (Tier D); on the peak TTM base ($12.65/share, ~2.8x the normalized base) the IV scales up by that same factor and still lands far below the $124.80 price — the price gap is wider than the base gap. There is no defensible base on which DINO clears 15%, or even 10%, at $124.80. This is a peak-earnings, peak-multiple setup: the stock is up ~146% in a year, trades near its five-year valuation high (Zacks), and consensus 2026 EPS of $11.85 is a war number that the same consensus expects to fall ~26% in 2027.
- What the bulls actually own: genuinely tight global refining capacity (5–7M bbl/d offline), a real L&S business about to be spun off (H2 2027), renewables swinging to profit ($123M adjusted EBITDA in Q2 2026), a 5% dividend raise to $0.525/quarter, and $1.5B of buyback authorization. All of that is worth something — the super-bull case prices it — and it still only gets to a $53.52 IV@15%.
- Red flags beyond the cycle: executive churn at the top during the best year in four years (CEO separated; CFO terminated in May 2026 after a leave of absence, with the chief accounting officer acting as CFO), and the Mississauga base-oil retirement carrying a reported cost of up to $505M. Neither changes the tier; both argue against paying a peak multiple.
- Balance sheet is not the problem: net debt $1,791,000,000 (2.15x normalized OE) and $2.26B of cash at June 30, 2026 mean the company survives the downcycle whenever it comes. The problem is purely the price paid for cyclical earnings at their peak.
- Margin of safety: the shares clear a 15% hurdle only at or below the weighted IV@15% of $28.25 — roughly a quarter of the current price — and a buyer wanting a margin of safety below the weighted case (e.g. against the $21.05 bear IV) would need the low $20s. At $124.80 the buyer is paying for the war premium to be permanent.

## Final verdict
- **Final tier: D** (weighted IRR 5.22% on the normalized base; no tier override — the numbers and the judgment agree, and the peak-TTM alternative base does not rescue it)
- Confidence: **Medium** (high on the filing data and on the direction of the verdict — the gap is too wide for base choice to matter; medium because refining margins can stay extreme longer than any model assumes)
- One-liner: Peak-cycle refiner, moat 3/10 — war-driven crack spreads handed it a $12.65 TTM OE/share, but on the normalized $4.47 base the weighted IRR is 5.22% (IV@15% $28.25 vs $124.80); it clears 15% only at ~$28 or below.
