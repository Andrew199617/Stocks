# ONTO — Onto Innovation Inc.
Pass-1 v5 / engine 5.4.0 run, 2026-10-17. Price $220.70 (nasdaq_quote_api, dcf_numbers.json); market cap $10,874,551,100 — in scope under $40B. All figures below are copied from dcf_numbers.json, ttm.json, fundamentals.json, statements.json or financials_history.csv — none are recomputed.

## What it is
Semiconductor process-control equipment: optical metrology, macro-defect inspection (Dragonfly), packaging lithography and process/yield software for fabs and OSATs. The current story is advanced packaging for AI/HBM: Q2 2026 revenue $343.1M was +35.3% YoY (search result, company release), advanced-packaging growth outlook for 2026 was raised to ~80%, backlog passed $1.1B, and Q3 2026 was guided to $380–400M revenue with H2 revenue +25% or more vs H1. It closed the Semilab materials-analysis acquisition in FY2025 (statements.json cash-flow acquisitions line: $436,124,000 in the latest FY).

## Owner's earnings
**Latest FY (ended 2026-01-03, 10-K via EDGAR, financials_history.csv):** revenue $1,005,263,000 (+1.8% YoY); operating cash flow $328,315,000; capex $28,513,000; SBC $27,617,000.
- **Conservative owner's earnings latest FY: $272,185,000 = $5.52/share** (dcf_numbers.json base_oe_latest_per_share 5.524019239745906).
- Maintenance version in financials_history.csv is $528,277,000 — not usable: it is inflated by the latest FY's working-capital swing (see NI_OCF_DIVERGENCE / BASE_DIVERGENCE below), so the OCF-based conservative series is the one used throughout.
- OE positive 5 of the last 5 fiscal years (dcf_numbers.json oe_positive_years_of_last_5: 5/5).

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $328,315,000 − prior YTD $149,923,000 + current YTD $87,829,000 = **TTM $266,221,000**
- Capex: FY $28,513,000 − prior YTD $22,005,000 + current YTD $7,242,000 = **TTM $13,750,000**
- SBC: FY $27,617,000 − prior YTD $13,492,000 + current YTD $17,026,000 = **TTM $31,151,000**
- Shares (current-YTD weighted diluted): **49,841,000**
- **TTM OE total $221,320,000 → base OE/share $4.44** (dcf_numbers.json base_oe_per_share 4.440520856323108, base_source: ttm_json)
- The engine's normalized base (3-yr median) is $3.73/share and the latest FY is $5.52/share; the TTM $4.44 sits between them and is the least distorted of the three (see BASE_DIVERGENCE).

## Moat: 5/10 — moderate / narrow
Justification: niche leadership in advanced-packaging inspection/metrology and fab qualification switching costs, but KLA dominates process control, measured ROIC is not wide-moat grade, and gross margin is slipping.
- Evidence (fundamentals.json): **ROIC proxy** — FY2022 15.4%, FY2023 7.1%, FY2024 10.0%, latest FY 6.4%. That is around, not well above, the cost of capital through a cycle, so a moat above 6 is not supported without a written excuse, and none is offered here. **Gross margin** — FY2022 53.6%, FY2023 51.5%, FY2024 52.2%, latest FY 49.7%, TTM (fundamentals.json) 50.4%: a ~50% level with a down trend, consistent with contested pricing power.
- FOR: leading position in advanced-packaging inspection/metrology (Dragonfly G5) riding HBM/AI packaging demand; tool qualification and process-integration switching costs at fabs and OSATs; Semilab broadens the metrology suite; debt-free balance sheet (below).
- AGAINST: KLA is the dominant process-control rival with far broader portfolio and scale, Nova and Camtek contest the same niches; ROIC proxy only 6.4% in the latest FY; gross margin down from 53.6% to 49.7%; semiconductor capex cyclicality and customer concentration, China export-control exposure; goodwill up to $644,015,000 after Semilab (fundamentals.json latest FY) — integration/impairment risk.
- A 5 gives CAP = 8.5 years (dcf_numbers.json cap_years): growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — final run (engine 5.4.0, --ttm)
**Growth-start sanity check (mandatory):** the engine's blended start is 7.49% (g_blend 0.07486837073973907), anchored to the flat latest FY (revenue +1.8%) and a 3-yr revenue CAGR of ~0.0% — it is stale against the 2026 prints: TTM revenue +8.1% (fundamentals.json ttm revenue_yoy), Q1 2026 +9.5% YoY, Q2 2026 +35.3% YoY, Q3 2026 guided $380–400M, H2 guided +25% or more vs H1, advanced packaging guided ~+80% for 2026 (search results, company guidance). Scenario starts were therefore recalibrated upward via offsets (−0.075 / +0.045 / +0.165 / +0.245 / +0.345 vs the blend) to ~0 / 12 / **24** / 32 / 42%. The base 24% start is below the Q2 print (+35.3%) and in line with the H2 guide; the super-bull 42% start is above every print except the advanced-packaging segment guide, which is the written reason it carries only 10% probability and a 1.25 OE multiplier. Probabilities 10/25/30/25/10; OE multipliers 0.75/0.90/1.00/1.10/1.25 (defaults).

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -0.0% | 0.75 | AI-packaging capex air-pocket; growth stalls at the FY2025 level | $24.59 | 3.85% |
| Bear | 25% | 12.0% | 0.90 | Inflection fades to low-double-digits; semi cycle turns | $48.51 | 5.50% |
| Base | 30% | 24.0% | 1.00 | H2 guide delivered, then normal CAP fade | $87.55 | 8.10% |
| Bull | 25% | 32.0% | 1.10 | Q2 momentum persists; Dragonfly / Atlas G6 share gains | $132.01 | 10.70% |
| Super bull | 10% | 42.0% | 1.25 | Advanced-packaging supercycle at the ~80% segment guide, sustained | $220.22 | 14.98% |

- **Probability-weighted: IV@15% $95.88 (-56.6% vs price), IV@12% $133.47, IV@10% $176.13, weighted IRR 8.66%, base-case IRR 8.10%** (dcf_numbers.json weighted / implied_irr_weighted)
- **Tier by numbers: D.** Diagnostics (dcf_numbers.json): OE yield 2.01%, terminal value 23.5% of IV@15%, scenario spread 9.0x, 9.4 months since FY end.
- Hurdle prices (dcf_numbers.json): clears 15% at $95.88, 20% at $63.09, 25% at $45.77. Even the super-bull IV@15% ($220.22) only matches the $220.70 price — the market is already paying for the super-bull case.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.4 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, legs quoted above.
- **NI_OCF_DIVERGENCE** (net income vs OCF >40% apart in the latest FY): statements.json cash-flow lines for the latest FY show the gap is non-cash plus working capital, not a tax deposit: D&A $21,030,000 (up from $12,872,000 — Semilab amortization), SBC $27,617,000, deferred taxes +$12,865,000 (a swing from −$26,476,000), and a payables surge of +$50,937,000 partly offset by receivables −$53,783,000. The OCF-based conservative OE is the series used, and the TTM base (OCF $266,221,000, down from the FY's $328,315,000 as payables normalized in H1 2026) strips most of the surge out.
- **DEBT_TAGS_BLANK** (no debt tag in the latest FY — net debt unknown to the engine): balance sheet from the filing (fundamentals.json latest FY): cash $346,119,000 plus short-term investments $293,503,000 = $639,622,000 of liquid assets, total liabilities $267,094,000, equity $2,100,647,000, lease liabilities $17,475,000 (dcf_numbers.json), and no debt tag filed in any recent year. This is an effectively debt-free company; the engine's null net debt understates, not overstates, its strength — and it does not change the tier, which fails on price vs growth, not leverage.
- **BASE_DIVERGENCE** (latest FY $5.52 vs 3-yr median $3.73): the latest FY is the distorted one — its OCF was flattered by the +$50,937,000 payables swing in the Semilab closing year (above). The median is arguably too low (it averages in the FY2023 trough), so the TTM base $4.44, which sits between them and already reflects the payables normalization, is used.
- **WIDE_SCENARIO_SPREAD** (super-bull IV 9.0x super-bear IV): real — the range between a semi-cycle air-pocket and an AI-packaging supercycle IS that wide. Confidence is capped at medium, and the verdict is sized to the conservative end.
- **TIER_BAND** (bear tier D at 5.5% vs bull tier C at 10.7%): the verdict spans D–C across bear/bull; sized to the bear end (D) per the flag. The weighted result (8.66%) is itself D, so no tier_override is needed.
- Preliminary-run flag **LOW_OE_YIELD** (1.7% on the median base) did not recur on the TTM base (OE yield 2.01% in the final diagnostics) but the substance stands: at $220.70 the valuation rests almost entirely on growth, which is why even a 24% base growth start only yields 8.10%.

## My thoughts / overlay
- The business inflection is real — guidance, backlog and Q2 prints all point the same way, and the growth recalibration above gives it full credit, including a super-bull start (42%) above the latest consolidated print. It still does not clear 15%: the super-bull IV@15% is $220.22, essentially today's price. A buyer at $220.70 needs the super-bull case just to earn ~15%.
- Method range: on the preliminary (median base, blended growth) run the weighted IRR was 4.95% and IV@15% $40.25; on this final (TTM base, recalibrated growth) run it is 8.66% / $95.88. Both are Tier D — the tier is robust to method, only the size of the overvaluation moves.
- Balance-sheet quality is not the problem: no debt, $639,622,000 liquid at FY end, buybacks $204,979,000 TTM (fundamentals.json dividends block). The problem is purely the price against a 6.4% latest-FY ROIC proxy and a ~50% gross margin.
- Risks to the D (i.e. upside risks): advanced-packaging demand compounding longer than the CAP fade assumes, Semilab synergy, or a semi upcycle that makes the 42% super-bull start the base case. Risks confirming the D: KLA/Nova/Camtek share pressure, China controls, Semilab goodwill ($644,015,000) impairment, customer concentration.

## Final verdict
- **Final tier: D** (weighted IRR 8.66% on the final TTM inputs; bear D / bull C band, sized to the bear end)
- Confidence: **Medium** (high that the price embeds the super-bull case; medium on any single growth path — scenario spread 9.0x)
- One-liner: Real AI-packaging growth inflection, moat 5/10 — but at $220.70 the price already discounts the super-bull case: weighted IRR 8.7%, IV@15% $95.88, clears 15% only below $95.88; Tier D.
