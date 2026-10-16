# HUBB — Hubbell Incorporated

v5 run, 2026-10-15. Market cap $25.17B at $470.53 (nasdaq_quote_api) — in scope under $40B.

All figures below are copied from dcf_numbers.json, ttm.json, or financials_history.csv — none are recomputed.

## What it is
Designs, manufactures and sells electrical and utility solutions, mainly in the US: Utility Solutions (connectors, enclosures, arresters, grid/connectivity products for transmission & distribution) and Electrical Solutions (wiring devices, lighting/control, connectors for non-residential, residential, industrial and data-center applications), across 75+ brands. Demand is tied to grid modernization/resiliency, electrification and data-center power build-out.

## Owner's earnings
From financials_history.csv (SEC EDGAR 10-Ks):
- FY2025: revenue $5,844,600,000; net income $887,100,000; operating cash flow $1,029,800,000; capex $155,100,000 (tag PaymentsToAcquireProductiveAssets); SBC $33,000,000 (tag ShareBasedCompensation).
- **Conservative OE FY2025 (OCF − capex − SBC): $841,700,000 = $15.73/share latest FY** (dcf_numbers.json base_oe_latest_per_share).
- Maintenance version FY2025 (NI + D&A − min(capex, D&A) − ΔNWC, from financials_history.csv): $826,200,000 — close to the conservative figure, which supports OE quality.
- OE positive 5 of the last 5 fiscal years. SBC is small relative to OCF and is treated as a real cost throughout.
- Engine normalized base (median of last 3 FY OE/share): $14.448148148148148/share. Latest FY is above the median — no BASE_DIVERGENCE flag was raised.

**Base used = TTM owner's earnings from ttm.py (--ttm), because STALE_FY fired (see Flags). ttm.json inputs, quoted exactly:**
- OCF: FY $1,029,800,000 (2025-01-01 to 2025-12-31) − prior YTD $37,400,000 (2025-01-01 to 2025-03-31) + current YTD $86,600,000 (2026-01-01 to 2026-03-31) = **TTM $1,079,000,000**
- Capex: FY $155,100,000 − prior YTD $26,000,000 + current YTD $40,600,000 = **TTM $169,700,000**
- SBC: FY $33,000,000 − prior YTD $14,400,000 + current YTD $14,400,000 = **TTM $33,000,000**
- Shares (current-YTD weighted diluted): **53,300,000**
- **TTM OE total $876,300,000 → base OE/share $16.440900562851784** (base_source: ttm_json)
- Caveat: ttm.py's latest YTD leg is Q1 2026 only. Q2 2026 was reported on 2026-07-28 (see Thoughts) but is not in the ttm.json legs, so the TTM base does not yet include Q2.

Balance sheet (engine, FY2025): net debt $1,842,900,000; diagnostics net_debt_to_normalized_oe 2.095185044169357 on the TTM base basis reported by the engine. This is pre-NSI — see Thoughts for the post-period leverage change, which the engine figures do not capture.

## Moat: 7/10 — strong
Justification: Spec-in, code-certified products embedded in utility standards with real switching friction and proven pricing power, held through cycles; capped at 7 because the products are ultimately manufactured components exposed to large diversified rivals (Eaton, ABB, Legrand, AMETEK) and to utility/construction capex cycles, with no network effect.
- FOR:
  - Spec-in position: products specified into utility standards and certified (UL/IEEE-type requirements), making displacement slow and risky for the buyer
  - Switching costs / reliability criticality: low-cost components whose failure is expensive, so buyers do not shop on price alone
  - Proven pricing power: targeted price actions have held/expanded margins through cost inflation
  - Installed breadth: 75+ brands across utility T&D and electrical, front-of-meter and behind-the-meter (data centers)
  - High cash conversion and returns on capital held through cycles (OE positive 5/5 years)
- AGAINST:
  - Large diversified rivals (Eaton, ABB, Legrand, AMETEK, Rockwell) with greater scale and R&D budgets
  - Cyclical end markets: utility capex, non-residential construction and industrial demand can defer
  - Manufactured components — no network effect or recurring-revenue lock-in; share must be re-won on specs and service
  - Acquisition-led growth adds integration and leverage risk (NSI, $3.0B, closed in Q2 2026)
- A 7 gives CAP = 11.1 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 11.1 years, 15-year projection.

## DCF — v5 final run (2026-10-15)
Engine blended growth: g_blend 0.07693806957934413 (components: rev CAGR 5y 0.0968011593749123, rev CAGR 3y 0.05707497978377596, latest rev YoY 0.03839388824731271, OE/share CAGR 2y 0.11066719037461281), share-count adjustment +0.003709764435900431 (share CAGR -0.003709764435900431), giving g_base 0.08064783401524456. Default offsets (-12/-5/0/+5/+12pp) and OE multipliers (0.75/0.90/1.00/1.10/1.25) and default probabilities 10/25/30/25/10 were kept — no recalibration was needed (see sanity check). Price $470.53.

Sanity check vs recent prints: base start 8.06% sits just below Q2 2026 organic sales growth (+10%) and inside the FY2026 organic guidance range reported with Q2 (9–11%) — reasonable for OE growth off the TTM base, not a cap artifact. Bull start 13.06% is above organic guidance but below guided total sales growth (16–18%, including NSI M&A). Super-bull start 20.06% is above even the top of total-sales guidance — justified only on sustained grid/data-center demand plus NSI synergies and operating leverage, which is why it carries only 10% probability. Super-bear start -3.94% reflects a utility/construction capex downturn.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -3.94% | 0.75 | Utility/construction capex downturn; NSI leverage bites | $74.79 | 4.26% |
| Bear | 25% | 3.06% | 0.90 | Growth fades to low-single digits; margins give back | $124.61 | 5.84% |
| Base | 30% | 8.06% | 1.00 | Grid/electrification demand compounds near guidance organic rate | $175.42 | 7.44% |
| Bull | 25% | 13.06% | 1.10 | Data-center + grid demand and NSI contribution sustain low-teens growth | $244.72 | 9.50% |
| Super bull | 10% | 20.06% | 1.25 | Multi-year grid supercycle with synergy and margin leverage | $387.85 | 13.17% |

- **Probability-weighted: IV@15% $191.22, IV@12% $259.07, IV@10% $335.49, weighted IRR 7.98%, base-case IRR 7.44%**
- **Tier by numbers: D.** Diagnostics (dcf_numbers.json): OE yield 0.03494123767422223, terminal value share at 15% 0.20866433487547573, scenario spread (IV15) 5.185637225120602x, months since FY end 9.461235216819974.
- Even the super-bull scenario (IV@15 $387.85, IRR 13.17%) does not clear 15% at $470.53.

## Flags — every fragility flag resolved
- **STALE_FY** (latest fiscal year ended 9 months ago): resolved by using the ttm.py base — TTM OE/share $16.440900562851784 from the FY / prior-YTD / current-YTD legs quoted in full above, passed via --ttm. Limitation stated plainly: ttm.json's current YTD leg ends 2026-03-31, so Q2 2026 (reported 2026-07-28) is not in the base; Q2 evidence is addressed qualitatively in Thoughts and does not change the tier (even super bull is below 15%).
- **WIDE_SCENARIO_SPREAD** (super-bull IV is 5.2x super-bear IV): real — the range reflects genuine uncertainty over how long grid/data-center growth holds and how NSI integrates. Confidence is therefore not high (medium), and the verdict is sized to the conservative end.

No other flags were emitted: no DATA_GAP, no BASE_DIVERGENCE, no NI_OCF_DIVERGENCE, no BASIS_BREAK_SUSPECT, no HIGH_NET_DEBT/BIG_NET_CASH, no SECTOR_MODEL_MISMATCH.

## Thoughts / overlay
- Quality is not the debate; price is. This is a durable, cash-generative compounder whose current price already capitalizes years of grid/data-center growth: OE yield is only 0.03494123767422223 on the TTM base.
- Latest quarter (Q2 2026, reported 2026-07-28, from web search of the earnings coverage): net sales $1,711.8M, up 15% year over year (organic +10%, M&A +5%); adjusted diluted EPS $5.52, up 12%; Utility Solutions sales up 10% to $1,026M; Electrical Solutions sales up 25% to $686M; FY2026 guidance raised to total sales growth 16–18% (organic 9–11%), GAAP EPS $17.25–$17.55 and adjusted EPS $20.25–$20.55. These prints support the base/bull growth starts above; they do not rescue the valuation — the weighted case still returns under 8%.
- Post-period balance-sheet change not in the engine figures: Hubbell completed the ~$3.0B acquisition of NSI Industries in Q2 2026, funded with a new term loan, senior notes and commercial paper per the Q2 coverage, taking pro-forma leverage materially above the FY2025 net debt $1,842,900,000 in dcf_numbers.json. That raises the bear-case risk and is a reason not to stretch for a higher tier; it does not affect the TTM OE base (NSI contribution is only partly in recent results).
- Method range: on the preliminary median base ($14.448148148148148/share, moat 5) the weighted IRR was 7.00% with weighted IV@15 $159.68; on the final TTM base with moat 7 it is 7.98% / $191.22. Both are Tier D — the verdict is not assumption-sensitive across these defensible inputs.
- Hurdle-clearing price: the weighted IV@15% is $191.22 — that is the price at which the weighted case clears 15%. With a margin of safety against the wide scenario spread, an entry would need to be materially below $191.22, versus $470.53 today (upside_at_15 -0.5936018562613342 on the final run).

## Final verdict
- **Final tier: D** (weighted IRR 7.98% on the v5 final TTM inputs; tier_by_numbers D, no override)
- Confidence: **Medium** (capped by WIDE_SCENARIO_SPREAD; TTM base is filing-direct but only through Q1 2026, and post-period NSI leverage is outside the engine figures)
- One-liner: Strong-moat (7/10) grid/electrical compounder with clean owner's earnings — but at $470.53 it does not clear 15% (weighted IRR 7.98%, weighted IV@15 $191.22); it would need to fall to about $191 to clear the hurdle.
