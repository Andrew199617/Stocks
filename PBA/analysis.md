# PBA — Pembina Pipeline Corporation
v5 run, 2026-10-14. In scope (market cap $28.239B at $48.52, nasdaq_quote_api). Canadian IFRS filer (Form 40-F), reporting currency CAD converted to USD by engine v5.3 — see FLAGS.

All figures below are copied from dcf_numbers.json, financials_history.csv, or ttm.py output — none are recomputed. Research facts are summarized from the company's Q2 2026 results release coverage (Business Wire, 2026-07-30) and are not used as DCF inputs.

## What it is
Calgary-based midstream operator serving Western Canada for 70+ years: Pipelines (oil, NGL and gas transportation, including Alliance and Cochin), Facilities (gas processing, NGL fractionation at Redwater, storage) and Marketing & New Ventures (commodity marketing, Cedar LNG, export terminals). Predominantly fee-based and contracted, with a marketing arm that keeps some commodity-margin exposure.

## Owner's earnings
**FY2025 (40-F via EDGAR, IFRS, USD-converted — from financials_history.csv):** operating cash flow $2,410,918,360; capex $572,602,240; SBC $68,653,840 (always a real cost).
- **Conservative owner's earnings FY2025: $1,769,662,280 = $3.04/share** (latest FY OE/share, dcf_numbers.json)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $1,647,420,730 — same ballpark as the conservative figure, which raises confidence in the base.
- OE positive 5 of the last 5 fiscal years. Net debt $8,442,961,600 (dcf_numbers.json) — see HIGH_NET_DEBT below.
- **Base used = the engine's normalized base: $2.68/share** (median of the last 3 fiscal years' OE/share, base_source: median_of_last_3_fy_oe_per_share). The latest year ($3.04/share) sits above the median; the median is the more conservative, cycle-resistant choice for a midstream name and no flag says it is the distorted one, so it stands.
- **TTM check (STALE_FY):** ttm.py was run and exited non-zero with: "ttm.py: cannot compute TTM for PBA (CIK 1546066): ocf: no annual (FY) fact; sbc: no annual (FY) fact; shares_diluted: no annual (FY) fact; capex: no capex facts in companyfacts under any candidate tag and no capex_override in judgment.json — refusing to zero-fill (same DATA_GAP standard as the engine)". This is the expected IFRS limitation — ttm.py reads us-gaap facts only — so the engine's median base is used, per the sweep spec. As a reasonableness check only (not an input): Q2 2026 results showed adjusted EBITDA up about 5% year over year, operating cash flow up double digits, 2026 adjusted EBITDA guidance reaffirmed, and management targeting 5–7% annual fee-based adjusted EBITDA per-share growth through 2030.

## Moat: 7/10 — strong
Justification: Irreplaceable Western Canadian midstream infrastructure with predominantly fee-based, long-term contracted cash flows, a leading NGL/fractionation franchise at Redwater, and strategic export corridors (Alliance, Cedar LNG) — a strong 7/10. It is not a 9-10: Enbridge/TC Energy are larger rivals, Marketing & New Ventures keeps commodity exposure, growth depends on regulatory approvals and producer volumes, and long-term hydrocarbon demand declines.
- FOR: Irreplaceable integrated midstream network in Western Canada — pipelines, gathering/processing, fractionation and export terminals that cannot be replicated on an investable timeline
- FOR: Predominantly fee-based, long-term contracted toll-road cash flows — producers pay for capacity, insulating the core from direct commodity prices
- FOR: Leading NGL franchise: Redwater fractionation (RFS IV added 55,000 bpd in May 2026) and Montney/Duvernay basin position
- FOR: Strategic corridors and export optionality: Alliance (rich gas to Chicago), Cochin, Cedar LNG and LPG export terminals diversify end markets beyond the US
- FOR: Proven through-cycle OE: owner's earnings positive in 5 of the last 5 fiscal years (engine), including the 2020 downturn
- AGAINST: Larger rivals Enbridge and TC Energy compete for the same Western Canadian volumes and growth projects
- AGAINST: Marketing & New Ventures retains commodity-margin exposure — not all earnings are fee-based
- AGAINST: New pipeline/facility growth needs Canadian regulatory approvals and producer volume growth; long-term hydrocarbon demand is in structural decline
- AGAINST: Levered balance sheet: net debt 5.4x normalized OE (engine) constrains flexibility if volumes or margins fall
- AGAINST: Share count is rising (~1.7%/yr engine share CAGR), diluting per-share growth
- A 7 gives CAP = 11.1 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 11.1 years, 15-year projection.

## DCF — v5 final run (2026-10-14)
Growth recalibration (written reason): the engine's blended growth is 5.24% and g_base is 3.59% after the share-count adjustment (share CAGR +1.66%/yr). The blend's revenue components are distorted for a midstream name — the 3-yr revenue CAGR is −12.83% because marketing revenue tracks commodity prices, not fee volumes, while the latest revenue YoY is +10.69% and OE/share CAGR (2y) is +6.50%. Management's own target is 5–7% fee-based adjusted EBITDA per-share growth through 2030, and Q2 2026 printed about +5% adjusted EBITDA growth. Scenario starts were therefore set via offsets (−0.086 / −0.036 / +0.014 / +0.044 / +0.084 vs g_base) to −5 / 0 / **5** / 8 / 12%: the base start sits at the low end of the guided range, the bull start modestly above it, and the super-bull start (12%, 10% weight) requires the sanctioned project slate (including the ~C$3B net Greenlight Electricity Centre and Heartland Extraction Plant sanctioned in Q2 2026, Cedar LNG and export growth) to outperform — a tail case, not a forecast. Probabilities 10/25/30/25/10; OE multipliers 0.75/0.90/1.00/1.10/1.25 (defaults). Price $48.52.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | −5.0% | 0.75 | Volumes/margins fall; growth projects stall; leverage bites | $11.60 | 5.13% |
| Bear | 25% | 0.0% | 0.90 | Flat fee volumes, soft marketing margins, no per-share growth | $17.58 | 6.89% |
| Base | 30% | 5.0% | 1.00 | Low end of the 5–7% fee-based growth target, delivered | $24.72 | 9.00% |
| Bull | 25% | 8.0% | 1.10 | Target beaten; sanctioned projects land on time and on budget | $31.34 | 10.81% |
| Super bull | 10% | 12.0% | 1.25 | Project slate plus LNG/data-center power demand all outperform | $43.07 | 13.75% |

- **Probability-weighted: IV@15% $25.11 (−48.2% vs price), IV@12% $33.44, IV@10% $42.75, weighted IRR 9.14%, base-case IRR 9.00%**
- **Tier by numbers: D.** Diagnostics (dcf_numbers.json): OE yield 5.52%, terminal value 19.0% of IV@15%, scenario spread 3.71x, net debt 5.41x normalized OE, 9.4 months since FY end.
- Sanity check: even the super-bull case (12% start, 1.25x OE) yields only 13.75% IRR at $48.52 — no defensible scenario clears the 15% hurdle at this price. That is a price finding, not a growth-input finding.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.4 months ago): ttm.py was run; it exits non-zero for this IFRS filer because it reads us-gaap facts only (its exact message is quoted under Owner's earnings). The engine's median base is used instead, as the spec directs for IFRS names, and Q2 2026 prints (adjusted EBITDA about +5% YoY, guidance reaffirmed) give no evidence the FY2025-based median is stale in a way that would change the tier — the gap to the hurdle is roughly 2x, not a few percent.
- **NI_OCF_DIVERGENCE** (2024, 2025): structural, not a one-off. FY2024 net income was $1,302,448,740 vs OCF $2,233,762,140, with D&A of $599,098,620; FY2025 net income was $1,237,229,840 vs OCF $2,410,918,360, with D&A of $720,865,320 (all from financials_history.csv). A pipeline/facilities asset base carries very large non-cash depreciation, so OCF persistently exceeds net income. The conservative OE used throughout is OCF-based and subtracts full capex and SBC, so the divergence does not inflate the base; no tax-deposit, impairment or working-capital one-off was identified as the driver.
- **FX_CONVERTED**: reporting currency CAD was converted to USD at period-end ECB reference rates recorded in dcf_numbers.json (2025: 0.73036; 2024: 0.69501). Flow facts use the period-end rate, not a period average — a documented simplification. Currency moves therefore shift the USD base and IV mechanically; the verdict gap (~2x) is far larger than plausible FX noise.
- **ADS_RATIO_APPLIED**: ratio 1.0 declared in judgment.json under the bounded authority — Pembina is direct-listed: its common shares trade on the TSX (PPL) and NYSE (PBA), so the NYSE security is the common share itself, not an ADS, and per-share figures are already on the traded basis. The engine applied the ratio (x1.0, no change to any figure) and make_score's DATA_GAP:ads_ratio gate is satisfied by the sourced declaration.
- **HIGH_NET_DEBT** (net debt 5.41x normalized OE, $8,442,961,600): folded into the verdict — 35% of probability weight sits on bear-or-worse cases, the super-bear OE multiplier is 0.75, and no leverage benefit is credited anywhere. Midstream leverage is normally judged against EBITDA rather than after-capex OE, but on this screen's own OE basis the warning stands: levered OE is thin relative to the debt load, and it is one more reason the D is sized conservatively rather than argued up.
- **WIDE_SCENARIO_SPREAD** (preliminary run only, 4.51x): the preliminary default-offset run spanned −8.4% to +15.6% growth starts, wider than this company's evidence supports. The recalibrated offsets narrowed the final spread to 3.71x and the flag cleared in the final run. Confidence is still held at medium, not high, because of the leverage, FX conversion and stale-FY items above.

## My thoughts / overlay
- This is a quality-vs-price result. The business did what a midstream toll road should do: OE positive 5/5 years, fee-based growth targeted at 5–7% per share through 2030, and a sanctioned growth slate. None of that rescues the arithmetic at $48.52 — the weighted IV@15% is $25.11 and even the super-bull IV@15% ($43.07) sits below the price.
- Method range: on the preliminary default inputs (median base, g_base 3.59%, default offsets) the weighted IRR was 8.97%; on the final recalibrated inputs it is 9.14%. Both are Tier D, and the super-bull ceiling (13.75%) is below 15% in the final run — the tier is robust to the defensible input range, which is why no method-range caveat changes the verdict.
- The dividend is the real reason most holders own this name; this screen prices owner's earnings against a 15% total-return hurdle and gives no separate credit for income, so a D here means "does not clear Andrew's 15% hurdle at this price," not "bad company."
- Balance-sheet overlay: net debt $8,442,961,600 at 5.41x normalized OE (engine) is the main fragility if volumes or marketing margins disappoint; it is already reflected in the scenario weights, not added as a tier override.

## Final verdict
- **Final tier: D** (weighted IRR 9.14% on the v5 final inputs; clears 15% only below ~$25.11, the weighted IV@15%)
- Confidence: **Medium** (high on the OE history and the tier's robustness across inputs; medium on the USD-converted, median-based base for an IFRS filer with a stale FY)
- One-liner: Strong fee-based midstream franchise, moat 7/10 — but at $48.52 the price is nearly double the 15%-hurdle value: weighted IRR 9.1%, weighted IV@15 $25.11; clears 15% only below ~$25.11.
