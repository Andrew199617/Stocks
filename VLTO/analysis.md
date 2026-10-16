# VLTO — Veralto Corporation
v5 run, 2026-10-15. In scope (market cap $25.405B at $101.50, nasdaq_quote_api). All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.py output, financials_history.csv, or the cited Q2 2026 earnings reports — none are recomputed.

## What it is
Danaher spin-off (2023). Two segments: Water Quality (~60% of revenue — Hach, Trojan Technologies, ChemTreat: water analytics and treatment) and Product Quality & Innovation (~40% — Videojet, Linx, Esko, X-Rite/Pantone: marking & coding, packaging and color). Razor-and-blade model: a large installed instrument base drives consumables, service and software; recurring revenue was 62% of total sales in Q2 2026 (search: Zacks/StockTitan Q2 2026 reports).

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** revenue $5,503M; net income $940M; operating cash flow $1,077M; capex $63M; SBC $74M (always a real cost).
- **Conservative owner's earnings FY2025: $940M = $3.76/share** (key_numbers.md: latest FY OE/share $3.76, latest FY OE total $940.0M)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $951M — essentially the same as the conservative figure, which raises confidence in the base.
- OE positive 5 of the last 5 fiscal years. Net debt (latest, key_numbers.md) $642.0M; net debt / normalized OE 0.66x — the balance sheet is not a verdict driver at the FY2025 snapshot. Note in words only: Q2 2026 reports put net debt higher after the In-Situ and GlobalVision acquisitions (search-cited, not an engine figure), so acquisition spending, not operating leverage, is the watch item.
- History is short as a standalone filer (spin in 2023); the engine history back to 2021 is on the Danaher carve-out basis — treated as continuous for the OE series, but it is one reason confidence is not high.

**Base used = TTM owner's earnings from ttm.py (filing-direct, no hand math), via `--ttm`:**
- OCF: FY $1,077M − prior YTD $157M + current YTD $182M = **TTM $1,102M**
- Capex: FY $63M − prior YTD $15M + current YTD $12M = **TTM $60M**
- SBC: FY $74M − prior YTD $16M + current YTD $16M = **TTM $74M**
- Shares (current-YTD weighted diluted): **249,200,000**
- **TTM OE total $968M → base OE/share $3.88** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $3.46/share and the latest FY is $3.76/share; the TTM base sits above both because FY2025/Q1 cash generation stepped up. The TTM figure is used — it is the most current filing-derived base.
- Provenance caveat, stated plainly: ttm.py's latest available YTD leg in this run ends 2026-04-03 (Q1 2026). Q2 2026 was reported in the press (below) but its YTD facts were not the leg ttm.py returned, so no Q2 figure enters the base — Q2 is used only for the growth sanity check.

**Recent prints (search, for the sanity check only):** Q2 2026 sales $1.47B, +7.6% YoY reported, core +4.2% (Water Quality core +5.7%, PQI core +2.0%); core growth was +3% price and +1.2% volume, with acquisitions adding 2.4pp and FX 1pp; recurring revenue grew high-single-digit at 62% of sales; adjusted EPS $1.11, +19.4% YoY, including a $0.05/share IEEPA tariff-refund benefit. Full-year 2026 guidance was raised to core sales growth 4.0–4.5% and adjusted EPS $4.35–$4.43. Q1 2026 sales rose 6.7% YoY.

## Moat: 7/10 — strong
Justification: razor-and-blade installed base in water analytics/treatment and marking/coding drives ~62% recurring revenue, with regulatory/workflow switching costs and proven pricing power; capped below wide because growth is only mid-single-digit, there is no network effect, and capable rivals plus municipal/industrial cyclicality erode at the edges.
- FOR: Razor-and-blade installed base (Hach, Trojan, ChemTreat, Videojet) driving ~62% recurring consumables/service/software revenue; regulatory and validated-workflow switching costs in water testing and pharma/food packaging; proven pricing power — +3% price contribution to Q2 2026 core growth; leading brands held for decades plus Veralto Business System margin discipline; asset-light, high-margin model — capex only $63M vs OCF $1,077M in FY2025.
- AGAINST: No network effects; share must be defended product-by-product against large rivals in water and coding; mid-single-digit core growth ceiling — municipal budgets and industrial capex cycles cap demand; PQI is more cyclical (consumer packaging) than Water Quality; growth partly bought — In-Situ and GlobalVision acquisitions added 2.4pp of Q2 reported growth; tariff and restructuring noise — Q2 2026 included a $0.05/share tariff-refund benefit and cost-optimization charges.
- A 7 gives CAP = 11.1 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 11.1 years, 15-year projection.

## DCF — v5 final run (2026-10-15)
Growth recalibration (written reason): the engine's blended growth is 4.17% and g_base is 3.63% (blend minus the 0.54pp share-count dilution adjustment; share count CAGR +0.54%). The default offsets (−12/−5/0/+5/+12pp) would have put the super-bull start at 15.6% — far above anything the company has printed (latest FY revenue YoY 5.97%, Q1 2026 +6.7%, Q2 2026 reported +7.6% / core +4.2%, 2026 core guidance 4.0–4.5%). That is a standardization artifact, not conservatism or realism. Offsets were therefore recalibrated downward to −0.06 / −0.025 / +0.01 / +0.03 / +0.055, giving starts of −2.4% / 1.1% / **4.6%** / 6.6% / 9.1% — the base start matches guided core growth, the bull start matches recent reported growth including acquisitions, and even the super-bull start sits only modestly above the best recent reported print, which is defensible only with the 1.25 OE multiplier story below. Probabilities are the defaults 10/25/30/25/10; OE multipliers are the defaults 0.75/0.90/1.00/1.10/1.25. Price $101.50.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -2.4% | 0.75 | Municipal/industrial downturn, PQI slumps, pricing gives back | $19.01 | 4.65% |
| Bear | 25% | 1.1% | 0.90 | Core growth stalls near 1%, margins pressured by restructuring/tariffs | $26.87 | 5.74% |
| Base | 30% | 4.6% | 1.00 | Guided 4.0–4.5% core growth holds, then fades over the CAP | $35.22 | 6.95% |
| Bull | 25% | 6.6% | 1.10 | Reported-growth pace (acquisitions + pricing + volume) persists | $42.59 | 7.96% |
| Super bull | 10% | 9.1% | 1.25 | High-single-digit growth plus operating leverage and buyback-funded OE/share lift | $54.49 | 9.53% |

- **Probability-weighted: IV@15% $35.28 (−65.2% vs price), IV@12% $46.83, IV@10% $59.72, weighted IRR 6.97%, base-case IRR 6.95%**
- **Tier by numbers: D.** Diagnostics (key_numbers.md): OE yield 3.83%, terminal value 18.7% of IV@15%, scenario spread 2.87x, net debt 0.66x normalized OE, 9.5 months since FY end.
- Even the super-bull case (9.53% IRR, IV@15 $54.49) does not clear 10%, let alone 15%, at $101.50 — the verdict does not hinge on the recalibration; the preliminary run on default offsets and the median base also produced Tier D (weighted IRR 6.54%).

## Flags — every fragility flag resolved
- **STALE_FY** (latest fiscal year ended 9.5 months ago): resolved by construction — the base is the TTM figure from ttm.py, quoted above with all its inputs. Caveat recorded there: ttm.py's YTD leg ends 2026-04-03, so the TTM base does not yet include Q2 2026; Q2 prints were used only for the growth sanity check.
- **WIDE_SCENARIO_SPREAD** (preliminary run: 4.5x): present in the preliminary run on default offsets, absent in the final run — the recalibrated offsets narrowed the spread to 2.87x (key_numbers.md). Confidence is still held at medium, not high, because the TTM leg is a quarter behind the reported results and the standalone history is short.

## My thoughts / overlay
- This is a quality-vs-price story, not a quality debate: 5/5 OE-positive years, the two OE definitions agree ($940M conservative vs $951M maintenance in FY2025), capex is trivial against OCF, SBC is a modest $74M, and recurring revenue is 62%. None of that is in dispute.
- What is in dispute is only the price: at $101.50 the OE yield is 3.83% for a business whose core growth is guided at 4.0–4.5%. A 15% hurdle needs either far faster growth than management guides or a far lower entry price — the model says both, in effect.
- Method range: the defensible runs here span only Tier D — preliminary (median base, default offsets) weighted IRR 6.54%, final (TTM base, recalibrated offsets, moat 7) 6.97%. Unlike inflection names, there is no plausible input set in this run that moves VLTO near the hurdle; even the super-bull scenario alone is 9.53%.
- Risks to the (already low) base case: the $0.05/share tariff-refund benefit in Q2 is one-off; the 2026 Cost Optimization Program charges are real cash costs behind the adjusted figures; acquisition-led growth (In-Situ, GlobalVision) raises net debt off the FY2025 snapshot and must earn its return.
- Price that clears 15%: the weighted IV@15% is $35.28 — that is the hurdle-clearing price on the weighted case, with no extra margin of safety. With a margin of safety against the bear case (bear IV@15 $26.87), a buyer demanding 15% with protection needs to be nearer the bear IV than the weighted IV.

## Final verdict
- **Final tier: D** (weighted IRR 6.97% on the v5 final inputs; no tier override)
- Confidence: **Medium** (high on OE quality and the filing-derived base, held back by the Q1-only TTM leg and short standalone history)
- One-liner: High-quality, strong-moat (7/10) compounder, but far too expensive — weighted IRR 6.97% and weighted IV@15 $35.28 vs $101.50 price; clears 15% only below ~$35.
