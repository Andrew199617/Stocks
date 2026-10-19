# YUMC — Yum China Holdings, Inc.
Engine 5.4.0 run, 2026-10-17. In scope (market cap $16.740B, nasdaq_quote_api). All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.json or fundamentals.json — none are recomputed.

## What it is
China's largest restaurant operator: KFC and Pizza Hut in mainland China, plus Taco Bell, Lavazza, Huang Ji Huang and own concepts. 19,297 stores at Q2 2026, mostly company-owned (18% franchised), targeting over 20,000 stores in 2026 with ~1,900+ net new openings. Q2 2026 (company release, via search): revenue $3.138B (+13% YoY reported, system sales +6% ex-FX), operating profit $348M (+14%), diluted EPS $0.70 (+21%), same-store sales +1% with same-store transactions up for the 14th straight quarter, delivery sales +26% and ~54% of company sales. The company also expects to acquire ownership of the Pizza Hut brand in mainland China (announced as closing August 2026) after operating it under licence for 36 years; KFC remains licensed from Yum! Brands.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $1,466,000,000; capex $626,000,000; SBC $42,000,000 (always a real cost).
- **Conservative owner's earnings FY2025: $798.0M = $2.15/share** (latest FY OE/share, key_numbers.md)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $1,012,000,000 — above the conservative figure, so the conservative OCF-based series is the binding, cleaner one.
- OE positive 5 of the last 5 fiscal years. Balance sheet (filing, per dcf_numbers.json): net debt $-476.0M (net cash) on the engine's CURRENT_ONLY basis — short-term borrowings $30,000,000 vs cash $506,000,000; the real fixed obligation is operating lease liabilities of $2,261,000,000, which the engine carries separately from net debt. Net debt / normalized OE: -0.50x.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $1,466,000,000 − prior YTD $864,000,000 + current YTD $976,000,000 = **TTM $1,578,000,000**
- Capex: FY $626,000,000 − prior YTD $259,000,000 + current YTD $271,000,000 = **TTM $638,000,000**
- SBC: FY $42,000,000 − prior YTD $22,000,000 + current YTD $23,000,000 = **TTM $43,000,000**
- Shares (current-YTD weighted diluted): **351,000,000**
- **TTM OE total $897,000,000 → base OE/share $2.56** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $1.73/share and latest FY is $2.15/share. The TTM base is used because it is the current run-rate: OCF is up TTM, capex is guided at roughly $600–700M for 2026 (company guidance via search), and the share count has fallen from 390,000,000 (FY2024) to the 351,000,000 TTM weighted count on $1.5B/yr of planned capital returns — the per-share gain is real cash returned, not an accounting artifact. The method range this creates is stated under Thoughts.

## Moat: 6/10 — moderate, not wide
Justification: Scale, brands, supply chain and digital membership give a real but narrow-to-moderate moat: ROIC recovered to 19.2% in FY2025 after an 8.2% FY2022 trough, operating margins hold ~10-11%, but there are no switching costs, competition is intense and fragmented, and the KFC brand is licensed — 6/10, not wide.
- Evidence (fundamentals.json, filing-direct): roic_proxy 8.2% (FY2022) → 14.9% (FY2023) → 16.6% (FY2024) → 19.2% (FY2025); operating margin 10.1% / 10.3% / 10.9% over FY2023–25. Gross margin is not used: Yum China reports restaurant costs by category rather than a COGS line, so fundamentals.json carries no gross-margin series for recent years — operating margin and ROIC are the filing-based margin evidence.
- FOR: Largest restaurant operator in China — 19,297 stores at Q2 2026 (KFC + Pizza Hut), unmatched store density and brand reach; proprietary supply chain and procurement scale built over ~40 years, plus food-safety trust that is hard to buy; digital membership scale — over 270 million active KFC/Pizza Hut members, delivery sales +26% YoY in Q2 2026; new-store paybacks of 2-3 years and side-by-side modules (KCOFFEE, KPRO, Pizza Hut WOW/Burger Bar) extend the network into lower-tier cities.
- AGAINST: No customer switching costs — diners switch freely in a fragmented, intensely competitive market; delivery-platform dependence and rising delivery mix pressure restaurant margins; China consumer softness pins same-store sales near flat (Q2 2026 SSS +1%) and average ticket is falling; KFC is licensed from Yum! Brands (royalty drag) and Pizza Hut brand ownership is only being acquired in 2026; ROIC fell to 8.2% in FY2022 — returns are cyclical, not through-cycle wide-moat level.
- A 6 gives CAP = 9.8 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 9.8 years, 15-year projection.

## DCF — 5.4 final run (2026-10-17)
Growth sanity check: the engine blend is 11.73% (rev CAGR 5y 7.38%, rev CAGR 3y 7.22%, latest rev YoY 4.37%, OE/share CAGR 2y 13.67%, plus the 4.43pp buyback adjustment on revenue components). Against actual prints — Q2 2026 revenue +13% reported (+6% ex-FX), EPS +21%, TTM OE/share $2.56 vs FY2025 $2.15 — the base start of 11.7% OE/share growth sits between the revenue signals and the per-share prints and needs no recalibration; the super-bull start of 23.7% is above the latest EPS print (+21%) and is carried only at 10% probability with the 1.25 OE multiplier as the genuine upside case (store count +~10%/yr plus buybacks). Default offsets (−12/−5/0/+5/+12pp), multipliers (0.75/0.90/1.00/1.10/1.25) and probabilities (10/25/30/25/10) were kept — this is a steady compounder, not an inflection name. Price $45.12.

| Scenario | Prob | Growth start | OE mult | IV@15 | IRR |
|---|---|---|---|---|---|
| Super bear | 10% | -0.3% | 0.75 | $13.89 | 6.23% |
| Bear | 25% | 6.7% | 0.90 | $22.77 | 8.99% |
| Base | 30% | 11.7% | 1.00 | $31.59 | 11.54% |
| Bull | 25% | 16.7% | 1.10 | $43.35 | 14.58% |
| Super bull | 10% | 23.7% | 1.25 | $66.97 | 19.64% |

- **Probability-weighted: IV@15% $34.09 (−24.4% vs price), IV@12% $46.44 (+2.9%), IV@10% $60.36, weighted IRR 12.25%, base-case IRR 11.54%**
- **Tier by numbers: C.** Diagnostics (key_numbers.md): OE yield 5.66%, terminal value 21.3% of IV@15%, scenario spread 4.82x, net debt −0.50x normalized OE, 9.5 months since FY end.
- Hurdle-clearing prices (weighted path): 15% at $34.09 · 20% at $23.20 · 25% at $17.34.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.5 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, legs quoted above.
- **BUYBACK_TAILWIND** (share count −4.43%/yr): already credited via the +4.43pp growth adjustment on the revenue components of the blend; not double-counted in the verdict. It is also the main reason the TTM per-share base exceeds the FY base — noted, and real (buybacks TTM $1,306,000,000 per fundamentals.json).
- **NI_OCF_DIVERGENCE** (2023): net income $827,000,000 vs operating cash flow $1,473,000,000 in FY2023 (financials_history.csv). The gap is structural, not a one-off: D&A of $453,000,000 plus SBC of $64,000,000 explain most of it, with the remainder in lease and working-capital non-cash items typical of a lease-heavy restaurant operator. No impairment or tax-deposit one-off was found in research. Because the base is the OCF-based conservative OE throughout, the divergence does not contaminate it.
- **WIDE_SCENARIO_SPREAD** (4.82x): real — the range is driven by whether China same-store sales and unit growth compound or stall. Confidence is capped at medium and the verdict is sized to the conservative end.
- **TIER_BAND** (bear D at 8.99% vs bull C at 14.58%): the verdict spans D–C; even the bull case does not clear 15%, so the position call is made on the bear-to-base end.

## My thoughts / overlay
- Method range: on the engine's normalized median base ($1.73/share) the preliminary run printed weighted IRR 9.02% (Tier D); on the TTM base actually used ($2.56/share) the final is 12.25% (Tier C). Both are defensible; the TTM base is the current run-rate, but a buyer should know the verdict moves a full tier with the base choice — neither run clears 15% at $45.12.
- Quality is not the debate: OE positive 5/5 years, net cash on the engine basis, ROIC back to 19.2%, ~$1.5B/yr of dividends plus buybacks, and a store base still growing ~10%/yr with 2-3 year paybacks. The debate is price: at $45.12 the market is already paying for the base-to-bull path (weighted IV@12% $46.44 ≈ price), leaving no margin of safety at a 15% hurdle.
- Risks: China consumer/geopolitical exposure is the whole asset; same-store sales are only +1% with falling ticket; delivery mix (54% of sales) raises rider-cost pressure; KFC royalty to Yum! Brands persists; RMB translation cuts reported growth (Q2 EPS +21% reported vs a lower ex-FX rate).

## Final verdict
- **Final tier: C** (weighted IRR 12.25% on the TTM base; method range D–C across the median and TTM bases)
- Confidence: **Medium** (high on OE quality and the filing-direct TTM base; capped by the 4.82x scenario spread and the D–C tier band)
- One-liner: Quality China QSR leader, moat 6/10 — does not clear 15% at $45.12 (weighted IRR 12.2%, weighted IV@15% $34.09); it clears 15% only at or below ~$34.
