# RPM — RPM International Inc.
Engine 5.4.0 run, 2026-10-18. All figures below are copied from dcf_numbers.json, ttm.json, financials_history.csv or fundamentals.json — none are recomputed.

## What it is
Specialty coatings, sealants and building materials in three groups: Construction Products (Tremco, Dryvit, Euclid — roofing, waterproofing, flooring for commercial/institutional buildings), Performance Coatings (Carboline, Stonhard — corrosion protection, flooring for industrial/infrastructure) and Consumer (Rust-Oleum, DAP, Zinsser, Varathane, plus The Pink Stuff acquired in 2025). Mostly repair-and-maintenance demand, sold through big-box/shelf space on the consumer side and specification/warranty systems on the commercial side. Serial acquirer of #1/#2 niche brands. Price $99.73 (nasdaq_quote_api), market cap $12.721B, shares diluted 127,554,000.

## Owner's earnings
**FY2026 (10-K, period ended 2026-05-31, from financials_history.csv):** revenue $7,863,422,000; operating cash flow $898,708,000; capex $223,507,000; SBC $32,848,000.
- **Conservative owner's earnings FY2026: $642,353,000 = $5.04/share** (OCF − capex − SBC).
- Maintenance version (from financials_history.csv): $979,522,000 — higher than the conservative figure because it adds back D&A and credits a working-capital release; the conservative OCF-based figure is the one used throughout.
- OE positive 4 of the last 5 fiscal years (FY2022 was negative, −$0.65/share, on the inventory/working-capital build — see OE_VOLATILE below). History OE/share: FY2024 $6.88, FY2025 $3.99, FY2026 $5.04 — the 3-yr median and the latest FY coincide at $5.04/share (base_oe_normalized_per_share $5.04, dcf_numbers.json).

**Base used = TTM owner's earnings through Q1 FY2027 (period ended 2026-08-31, 10-Q filed 2026-10-06), from ttm.py (filing-direct, no hand math):**
- OCF: FY $898,708,000 − prior YTD $237,510,000 + current YTD $263,936,000 = **TTM $925,134,000**
- Capex: FY $223,507,000 − prior YTD $62,461,000 + current YTD $58,505,000 = **TTM $219,551,000**
- SBC: FY $32,848,000 − prior YTD $5,475,000 + current YTD $9,601,000 = **TTM $36,974,000**
- Shares (current-YTD weighted diluted): **127,240,000**
- **TTM OE total $668,609,000 → base OE/share $5.25** (base_source: ttm_json)
- Why TTM over the median: the latest FY ended 4.6 months ago and Q1 FY2027 is already filed (record sales $2.22B, +4.8% YoY; adjusted EPS $1.98, +5.3%). The TTM base is only modestly above the $5.04 median/latest figure, and the verdict does not depend on the choice — the preliminary run on the median base gave weighted IRR 8.62%, Tier D, vs 8.40% here (the difference is the wider bear weighting below, not the base).

## Moat: 5/10 — moderate / narrow
Justification: a portfolio of #1/#2 niche brands with real shelf-space and specification positions and demonstrated pricing power, but no network effects, low switching costs on the consumer half, larger scaled rivals (Sherwin-Williams, PPG, Behr/Masco), and raw-material cyclicality that repeatedly overwhelms pricing for a year at a time.
- FOR: Leading niche brands (Rust-Oleum, DAP, Tremco, Carboline, Stonhard) that hold #1/#2 positions in small, fragmented categories; commercial specification + warranted-system selling (Tremco roofing/building envelope) creates switching friction; pricing power proven over the cycle — gross margin recovered from 36.3% (FY2022) to 41.4% (FY2025 and FY2026) in fundamentals.json after the raw-material shock; returns on equity stayed 20.0–28.9% across FY2021–FY2026 in fundamentals.json; diversified repair-and-maintenance demand across construction, industrial and consumer end-markets.
- AGAINST: Consumer DIY products are low-switching-cost and shelf space is contested by Sherwin-Williams, PPG and private label; no network effects or structural cost advantage vs larger coatings rivals; raw-material inflation outran pricing again in Q1 FY2027 (gross margin down 100bp in the quarter, per the Q1 release coverage); earnings are construction-cycle exposed — Construction Products organic sales fell 1.7% in Q1 FY2027 on healthcare/education softness; acquisition-led growth leaves goodwill/intangibles on the balance sheet and a serial deal cadence to sustain.
- ROIC note: the `roic_proxy` series in fundamentals.json is null for every year because RPM does not tag an operating-income line the tool can use — no ROIC figure is quoted because none was computed. The return evidence actually available is ROE (20.0–28.9%, FY2021–FY2026, fundamentals.json) and the gross-margin level/trend above (41.4% TTM 41.2% in fundamentals.json). That supports a moderate moat, not a 7+: returns are strong but the proxy that would prove durable excess ROIC through a cycle is not in the computed outputs, and FY2022 showed OE can go negative.
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — final run (2026-10-18)
Growth sanity check: the engine blend is 4.28% (rev CAGR 5y 5.19%, rev CAGR 3y 2.71%, latest rev YoY 6.66%, OE/share CAGR 2y −14.43% — the last is an artifact of the FY2024 OE spike to $6.88/share, not a trend). Against actual prints: FY2026 revenue +6.7%, Q1 FY2027 revenue +4.8% with 3.1% organic, and management's narrowed FY2027 guidance is mid-single-digit sales and adjusted EBITDA growth, with Q2 guided low-to-mid single digits. The base start of 4.28% sits just below the guided sales range — reasonable for OE, since Q1 gross margin fell 100bp on raw-material inflation outpacing pricing. Bull (9.28%) and super-bull (16.28%) starts are above anything recently printed on sales; they are OE-leverage cases (margin recovery toward RPM's 42% gross-margin target plus a Construction Products recovery), which is why their combined weight is cut to 25%. Bear weight was widened (super bear 15%, bear 30% vs the 10%/25% defaults) per the OE_VOLATILE and HIGH_NET_DEBT flags. Default offsets (−12/−5/0/+5/+12pp) and OE multipliers (0.75/0.90/1.00/1.10/1.25) retained. Price $99.73.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | -7.7% | 0.75 | Construction downturn + raw-material squeeze repeats the FY2022 OE collapse | $21.06 | 4.82% |
| Bear | 30% | -0.7% | 0.90 | CPG softness persists, margin recovery stalls, OE flat | $33.90 | 6.63% |
| Base | 30% | 4.3% | 1.00 | Mid-single-digit sales growth per guidance, OE tracks sales | $46.40 | 8.38% |
| Bull | 15% | 9.3% | 1.10 | CPG recovers, pricing catches inflation, OE leverage on sales | $62.77 | 10.58% |
| Super bull | 10% | 16.3% | 1.25 | Full MAP margin rebuild + cycle upswing compounds OE | $94.98 | 14.47% |

- **Probability-weighted: IV@15% $46.16 (−53.7% vs price), IV@12% $61.23, IV@10% $78.03, weighted IRR 8.40%, base-case IRR 8.38%**
- **Tier by numbers: D.** Diagnostics (dcf_numbers.json): OE yield 5.27%, terminal value 18.6% of IV@15%, scenario spread 4.51x, net debt 3.31x normalized OE, 4.6 months since FY end.
- Even the super-bull case (10% weight) only reaches a 14.47% IRR at this price — no scenario in the set clears the 15% hurdle at $99.73.

## Flags — every fragility flag resolved
- **OE_VOLATILE** (OE/share range >3x over 5 years): real and cyclical, not an accounting artifact — FY2022 OE/share was −$0.65 on an inventory/working-capital build (FY2022 OCF only $178,731,000 in financials_history.csv) and FY2024 spiked to $6.88 on the release. Handled by the normalized/TTM base (neither the trough nor the spike) and by widening bear weight to 45% combined.
- **NI_OCF_DIVERGENCE** (2024): FY2024 net income $588,397,000 vs OCF $1,122,305,000 (financials_history.csv). The company's own FY2024 release attributes the OCF jump to improved profitability plus working-capital efficiency under MAP 2025 — i.e. a working-capital release after the FY2022 build, the mirror image of that year's divergence in the other direction. It is a WC swing, not an earnings-quality break; the OCF-based conservative OE is the series used throughout, and the FY2024 spike year is not the base.
- **WIDE_SCENARIO_SPREAD** (4.51x): real — the outcome range for a cyclical, levered coatings name at this price IS wide. Confidence is capped at medium and the verdict is sized to the bear end.
- **HIGH_NET_DEBT** (net debt 3.31x normalized OE in the final run): balance sheet from the filings — net debt $2,218,336,000 (dcf_numbers.json; debt basis LongTermDebtAndCapitalLeaseObligations + current portion), plus lease liabilities $415,854,000. Q1 FY2027 coverage showed total debt down $263M YoY and OCF conversion ~1:1 in the quarter, so the leverage is serviceable, but at 3.3x OE it amplifies the bear cases — another reason for the 45% bear weight.
- **TIER_BAND** (bear tier D at 6.63% vs bull tier C at 10.58%): the verdict spans D–C; sized to the bear end — the final tier is D and no position case rests on the bull leg.

## My thoughts / overlay
- This is a good business at a full price, not a bad business. The OE machine works — TTM OE $668,609,000, dividends and buybacks funded from OCF ($90.5M returned in Q1 FY2027 alone per the Q1 release coverage) — but at $99.73 the buyer pays ~19x TTM OE/share for a mid-single-digit grower with cyclical OE.
- Method range: median base with default probs gave weighted IRR 8.62% / IV@15% $47.62; the final TTM base with widened bear weight gives 8.40% / $46.16. Both are Tier D — the verdict is not assumption-sensitive at this price, which is the finding.
- Near-term watch items: Construction Products recovery timing (the stated reason for the FY2027 guidance narrowing), raw-material inflation vs pricing (gross margin −100bp in Q1), and the November 9, 2026 investor day.
- Data note: fundamentals.json carries no roic_proxy or operating-income series for RPM (untagged), and its dividend per-share fields are null (only total dividends paid are filed) — noted here per the enrichment rule; neither affects the score, which is built from dcf_numbers.json / ttm.json. Enrichment otherwise completed (fundamentals, prices, segments, statements, profile/street, reprice); segments carries a minor tie-out warning on one quarterly D&A breakdown (rows sum to 97.5% of consolidated for 2026-08-31) and statements flags pre-2019 filing-generation basis breaks in old quarters — neither touches the scored annual history.

## Final verdict
- **Final tier: D** (weighted IRR 8.40%; bear D 6.63% → bull C 10.58%)
- Confidence: **Medium** (filing history is deep and the divergence is explained, but OE is genuinely cyclical and the scenario spread is 4.51x)
- Hurdle-clearing price: the weighted IV@15% is $46.16 — RPM clears a 15% hurdle only below ~$46, less than half the current price.
- One-liner: Quality niche-brand coatings compounder, moat 5/10 — but cyclical OE and 3.3x net debt at $99.73 give only an 8.4% weighted IRR (IV@15% $46.16); it clears 15% only below ~$46.
