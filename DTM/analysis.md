# DTM — DT Midstream, Inc.
Engine 5.4.0 run, 2026-10-17. Price $123.67 (nasdaq_quote_api), market cap est. $12.68B — in scope under $40B.

All figures below are copied from dcf_numbers.json, ttm.json, financials_history.csv, or fundamentals.json — none are recomputed.

## What it is
Pure-play natural gas midstream, spun off from DTE Energy in 2021: interstate pipelines (NEXUS, Millennium, Vector, Guardian, LEAP — Louisiana Energy Access Project), gathering systems in the Haynesville and Appalachia, and storage. ~70% Pipeline / ~30% Gathering by EBITDA. ~95% of revenue under demand-based (take-or-pay / minimum-volume) contracts, ~8-year weighted average tenor. $3.4B organic project backlog for 2026–2030, ~60% commercialized (~$2B committed, >80% pipeline projects), tied to LNG export, power-generation and data-center gas demand.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $867,000,000; capex $426,000,000; SBC $26,000,000 (always a real cost, small here).
- **Conservative owner's earnings FY2025: $415,000,000 = $4.05/share** (base_oe_latest_per_share $4.0488)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $289,000,000 — below the conservative figure, dragged by the ΔNWC leg; the OCF-based conservative figure is the cleaner series for a business with large JV equity earnings and D&A.
- OE positive 5 of the last 5 fiscal years, but the level is capex-cycle driven: OE/share ran $4.33 (2021) / $3.81 (2022) / **$0.06 (2023, capex spiked to $772M during LEAP construction)** / $3.96 (2024) / $4.05 (2025). Conservative OE subtracts ALL capex including growth capex, so build years understate run-rate cash generation — a structural feature of applying this model to midstream (see SECTOR_MODEL_MISMATCH).
- Net debt $3,270,000,000 (LongTermDebtNoncurrent + ShortTermBorrowings basis, dcf_numbers.json); lease liabilities $48,000,000. Dividend $0.88/quarter declared Q2 2026, guided to grow in line with adjusted EBITDA.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $867,000,000 − prior YTD $432,000,000 + current YTD $502,000,000 = **TTM $937,000,000**
- Capex: FY $426,000,000 − prior YTD $152,000,000 + current YTD $183,000,000 = **TTM $457,000,000**
- SBC: FY $26,000,000 − prior YTD $12,000,000 + current YTD $12,000,000 = **TTM $26,000,000**
- Shares (current-YTD weighted diluted): **102,700,000**
- **TTM OE total $454,000,000 → base OE/share $4.4206** (base_source: ttm_json)
- The engine's normalized base (median of last 3 FY OE/share: 2023 $0.06 / 2024 $3.96 / 2025 $4.05) is $3.9634/share — the median happens to dodge the 2023 capex-spike year, but it is stale (FY end 9.5 months ago) and below both the latest FY and the TTM print; TTM is the better base. TTM capex ($457M, with ~$425M of committed 2026 growth capital) still contains heavy growth spend, so the TTM base is if anything conservative for a fee-based asset base.

## Moat: 5/10 — moderate / narrow
Justification: real corridor monopolies and contracted cash flows, but measured returns are regulated-like, not wide-moat: the roic_proxy series in fundamentals.json (after-tax operating income over equity + debt − cash) ran 7.28% (2020) / 4.46% (2021) / 5.16% (2022) / 5.10% (2023) / 4.44% (2024) / 5.82% (2025) — around the cost of capital, never well above it through a cycle. Gross profit is not filed as a separate line (midstream presentation); operating margin is ~49.6% on a TTM basis (fundamentals.json), high but consistent with fee-based pipeline economics rather than pricing power above regulated/contracted rates.
- FOR: Pipelines are natural corridor monopolies — rights-of-way, FERC certificates and replacement cost are hard barriers to a competing line; ~95% demand-based contracts at ~8-year average tenor make revenue close to an annuity while contracts run; premier footprint — Haynesville gathering at record volumes (2.2 Bcf/d Q2 2026) with LEAP delivering directly into the Gulf Coast LNG corridor, plus Appalachia gathering into NEXUS/Texas Eastern; investment-grade balance sheet (agencies raised leverage downgrade thresholds in 2026); contracted backlog — $3.4B of projects, ~60% commercialized, each backed by long-term agreements before capital is committed.
- AGAINST: Returns are capped by construction — FERC rate proceedings and contract resets keep ROIC near the cost of capital (4.4–5.8% measured, above); gathering is exposed to producer drilling decisions and basin decline (Haynesville and Appalachia concentration, a small number of large producer customers); smaller scale than Kinder Morgan / Williams limits diversification and synergies; part of the pipeline portfolio is JV interests (Millennium, NEXUS, Vector) not wholly controlled; long-tail natural gas demand / energy-transition risk beyond the projection window.
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — engine 5.4.0 final run (2026-10-17)
Growth recalibration (written reason): the engine's blended growth is 16.84%, but two of its components are artifacts — OE/share CAGR 2y is 709.97% because it is measured off the 2023 capex-spike year (OE/share $0.06), and latest revenue YoY is +26.71%, flattered by the December 2024 Midwest pipeline acquisition step-up. Neither is an organic run rate. The prints that mean something: revenue CAGR 5y 10.52% / 3y 10.55% (themselves acquisition-flattered), TTM revenue YoY +18.12% (fundamentals.json), and company guidance — 2026 adjusted EBITDA guided at $1.155–1.225B with the 2027 early outlook at $1.225–1.295B, i.e. ~+6% at the midpoints — plus a contracted $3.4B backlog entering service 2026–2030. Scenario starts were therefore set via offsets (−0.1484 / −0.1234 / −0.0984 / −0.0734 / −0.0484 vs the blended 16.84%) to 2.0 / 4.5 / **7.0** / 9.5 / 12.0%. Probabilities shifted slightly bear-ward (15/25/30/20/10) per the OE_VOLATILE instruction to widen bear weight; OE multipliers are the defaults 0.75/0.90/1.00/1.10/1.25. Base OE/share $4.4206 (TTM), price $123.67.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | 2.0% | 0.75 | Haynesville/Appalachia volumes disappoint, contract resets bite, growth capex earns little | $26.63 | 5.18% |
| Bear | 25% | 4.5% | 0.90 | Backlog slips; EBITDA growth runs below guidance | $35.46 | 6.15% |
| Base | 30% | 7.0% | 1.00 | Guidance-like EBITDA growth (~+6%) plus backlog in-service ramp | $43.70 | 7.07% |
| Bull | 20% | 9.5% | 1.10 | LNG/power/data-center demand pulls backlog faster; full commercialization | $53.29 | 8.13% |
| Super bull | 10% | 12.0% | 1.25 | Sustained double-digit growth — above anything the company has guided | $67.11 | 9.60% |

- **Probability-weighted: IV@15% $43.34 (−65.0% vs price), IV@12% $57.75, IV@10% $73.85, weighted IRR 7.05%, base-case IRR 7.07%**
- **Tier by numbers: D — and D in every scenario** (bear D, bull D; the preliminary run's TIER_BAND flag disappeared once the artifact growth blend was recalibrated away).
- Diagnostics (dcf_numbers.json): OE yield 3.57%, terminal value 19.0% of IV@15%, scenario spread 2.52x, net debt 7.22x normalized OE, 9.5 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (FY2025 ended 9.5 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, legs quoted above.
- **OE_VOLATILE** (OE/share range over 5 years spans >3x): real and explained — it is the capex cycle, not demand cyclicality: 2023 OE/share collapsed to $0.06 because capex hit $772M building LEAP, while revenue that year was flat ($922M vs $920M). Handled three ways: TTM base (current capex run-rate), probabilities shifted bear-ward (15% super bear), and the verdict sized to the tier every scenario agrees on (D).
- **NI_OCF_DIVERGENCE** (net income vs operating cash flow differ by >40% in 2023, 2024, 2025): structural, not a one-off — FY2025 net income $441M vs OCF $867M. The gap is non-cash D&A ($258M in FY2025) plus equity-method JV earnings/distribution timing and deferred taxes, the standard midstream pattern. The OE base is built on OCF, so the divergence does not contaminate it; if anything NI understates cash generation here.
- **SECTOR_MODEL_MISMATCH** (Utilities sector classification): accepted — confidence is low. DT Midstream is an energy midstream name filed under a utilities-style model fit; the OE/capex DCF penalizes it twice (all growth capex subtracted, regulated-like returns faded to 2.5%). The method range note below carries this caveat; the tier is D on the model's own terms at this price regardless.
- **HIGH_NET_DEBT** (net debt 7.22x normalized OE in the final run; 8.05x in the preliminary): state the balance sheet from the filing — net debt $3,270,000,000 (long-term debt noncurrent + short-term borrowings, less cash $54,000,000), total debt $3,324,000,000, equity $4,736,000,000, lease liabilities $48,000,000. The OE multiple overstates the leverage risk: OE is post-all-capex, while against adjusted EBITDA (~$1.19B guided 2026 midpoint, external guidance) the company's own reported leverage is ~2.9x on-balance-sheet / ~3.5x proportionate (Q2 2026 investor materials) — investment grade, with rating agencies raising downgrade thresholds in 2026. Leverage is not the bear case here; valuation is. Bear cases were still stressed via the 0.75/0.90 OE multipliers.
- **WIDE_SCENARIO_SPREAD** (preliminary run: super-bull IV 4.4x super-bear): an artifact of the 16.84% blended growth start (itself an artifact, see recalibration). On recalibrated starts the spread is 2.52x and the flag cleared. Confidence is still capped at low by SECTOR_MODEL_MISMATCH.
- **TIER_BAND** (preliminary run: bear D vs bull C): also an artifact of the growth blend; on the final run every scenario — including super bull at a 12% growth start the company has never guided to — is Tier D. No sizing ambiguity remains.

## My thoughts / overlay
- The honest headline is the method range: this model charges DT Midstream for every dollar of growth capex while crediting none of the contracted EBITDA that capex buys until it flows through OCF. A distributable-cash-flow lens would be kinder. But no defensible lens closes a gap this size: even the super-bull case (12% growth start, 1.25x OE) yields a 9.60% IRR and an IV@15% of $67.11 — barely half the $123.67 price. The stock is priced for the contracted-growth story to be executed flawlessly and then some; at an OE yield of 3.57% on the TTM base there is no margin of safety at any of Andrew's hurdles.
- Quality is not the problem: ~95% demand-based contracts, record Haynesville volumes, investment-grade balance sheet, dividend growing with EBITDA ($0.88/quarter ≈ 2.8% yield at this price — the yield is real income the OE DCF's IRR only captures through the cash-flow path).
- What would change the verdict: a price near the hurdle levels below, or evidence the backlog earns returns well above the historical 4.4–5.8% ROIC proxy — new-project returns, not consolidated history, are the number to watch in pass 2.
- Hurdle-clearing prices (dcf_numbers.json hurdle_prices, weighted): clears 15% at $43.34, 20% at $30.41, 25% at $23.31. At the $123.67 price the weighted IRR is 7.05%.

## Final verdict
- **Final tier: D** (weighted IRR 7.05%; every scenario D; sized to the bear end per instruction — the bear end is also D)
- Confidence: **Low** (SECTOR_MODEL_MISMATCH mandates low; OE base quality itself is high)
- One-liner: High-quality contracted gas midstream (moat 5/10, ROIC stuck at regulated-like ~5%) — at $123.67 it cannot clear 15% under any scenario (weighted IRR 7.05%, IV@15% $43.34); it would need ~$43 to clear the 15% hurdle.

## Data notes
- Enrichment (5.4) all ran: fundamentals, prices, segments, statements, profile, reprice. Non-blocking warnings only: fundamentals lacks filed TTM buyback/share-issuance legs; profile.py found no 10-K Item 1 Business section or headcount sentence to extract (10-K filed 2026-02-19) — profile.json/street.json still written. Gross profit is not filed as a separate line for this filer, so no gross-margin series exists in fundamentals.json.
