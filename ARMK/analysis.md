# ARMK — Aramark
Engine 5.4.0 run, 2026-10-17. Price $55.28 (nasdaq_quote_api); market cap $14,779,052,720 — in scope under $40B.

All figures below are copied from dcf_numbers.json, ttm.json, financials_history.csv, or fundamentals.json — none are recomputed.

## What it is
Pure-play food and facilities services since the Vestis uniform-services spin-off (completed September 30, 2023): Food and Support Services (FSS) United States and FSS International — contract catering and facilities for business/industry, education, healthcare, sports/entertainment and corrections, plus the Avendra group-purchasing organization. New growth vector: Aramark Nexus, hospitality/facilities services for hyperscale AI data-center campuses, launched April 2026 with a top global hyperscaler; first Texas site began operations late in fiscal Q3 2026. FY2025 revenue $18,506,299,000; TTM revenue through 2026-07-03 $19,845,264,000 (fundamentals.json).

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $921,035,000; capex $489,240,000; SBC $58,643,000 (always a real cost).
- **Conservative owner's earnings FY2025: $373,152,000 = $1.3957/share** (base_oe_latest_per_share in dcf_numbers.json).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC) is not usable for ARMK: financials_history.csv prints −$490,811,000 for FY2025 and $2,137,845,000 for FY2023, whipsawed by ΔNWC swings of +$817,205,000 (2025) and −$1,437,416,000 (2023) around the Vestis separation and working-capital reclassifications. The OCF-based conservative figure is the clean series and is used throughout.
- OE positive 5 of the last 5 fiscal years. Net debt at FY2025 end $4,766,842,000 (debt total $5,405,937,000 less cash $639,095,000), plus operating lease liabilities of $316,049,000 not in that net-debt figure.

**Base used = TTM owner's earnings through Q3 FY2026 (2026-07-03), from ttm.py (filing-direct, no hand math):**
- OCF: FY $921,035,000 − prior YTD −$254,527,000 + current YTD −$264,755,000 = **TTM $910,807,000** (both YTD legs are negative — Aramark's cash generation is Q4-weighted; the TTM construction handles that)
- Capex: FY $489,240,000 − prior YTD $347,039,000 + current YTD $335,801,000 = **TTM $478,002,000**
- SBC: FY $58,643,000 − prior YTD $44,721,000 + current YTD $54,109,000 = **TTM $68,031,000**
- Shares (current-YTD weighted diluted): **267,191,000**
- **TTM OE total $364,774,000 → base OE/share $1.3652** (base_source: ttm_json)
- The engine's normalized base (median of last 3 FY OE/share) is $1.1674/share — lower, dragged by FY2024's $0.8886/share. The TTM base sits between the median and the latest FY ($1.3957) and is the most current filing-derived figure, so it is used; the verdict does not change on either base (the preliminary run on the median base printed weighted IRR 5.61%, also Tier D).

## Moat: 4/10 — weak-to-moderate
Justification: real scale and retention in a top-3 US oligopoly, but contracts are competitively rebid every 3–5 years, Compass Group is larger, margins are structurally thin, and measured returns have only just reached the cost of capital.
- FOR: Top-3 scale in US contract catering (Compass, Aramark and Sodexo together hold over 50% of the US market per industry research) with purchasing leverage through Avendra, its group-purchasing organization (over $1.1B of annualized new spend added fiscal YTD 2026 per management); record client retention near 98% in Q3 FY2026 and $1.6B of net-new business fiscal YTD, up 51%; diversified across education, healthcare, B&I, sports/entertainment and corrections, plus a first-mover Nexus position in data-center hospitality; operating margin expanding steadily — 3.03% (2022) → 3.89% (2023) → 4.06% (2024) → 4.28% (2025) → 4.39% TTM (fundamentals.json).
- AGAINST: ROIC proxy (fundamentals.json) has never been well above the cost of capital through a cycle: −2.2% (2020), 1.57% (2021), 3.37% (2022), 5.88% (2023), 6.64% (2024), 7.60% (2025) — improving, but a 7.6% peak in a good year is not a wide-moat return profile; gross margin is not separately meaningful as filed (Aramark's cost tag carries nearly all operating costs into the gross line, so the filed gross profit collapses to operating income and the series is inconsistent), leaving the ~4.3% operating margin as the margin evidence — structurally thin, with food and labor inflation passed through only with a lag; contracts rebid competitively, so retention must be re-won and Compass competes with greater global scale; labor-intensive model with wage pressure; COVID showed the cyclicality — OE/share was −$1.08 in FY2020; leverage (see HIGH_NET_DEBT below) consumes the equity cushion.
- A 4 gives CAP = 7.2 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 7.2 years, 15-year projection.

## DCF — engine 5.4.0 final run (2026-10-17)
Growth blend (dcf_numbers.json): rev CAGR 5y 7.60%, rev CAGR 3y 10.54%, latest rev YoY 6.35%, OE/share CAGR 2y 9.28%; share count +1.05%/yr applies a −1.05pp adjustment to the revenue components only, giving g_blend 7.92%. Default scenario offsets (−12/−5/0/+5/+12pp) and OE multipliers (0.75/0.90/1.00/1.10/1.25) and probabilities (10/25/30/25/10) were kept — the spread they produce already brackets every defensible path for a business growing revenue at 6–11%.

**Growth-start sanity check (written, per spec):** the base start of 7.92% sits below the latest prints — Q3 FY2026 organic revenue growth of +9% (about +11% excluding a calendar shift, per company reporting) and raised FY2026 organic guidance of 9–10%. That is deliberate: FY2026 is a single guidance year flattered by record net-new business and the first Nexus ramp, while the blend's median construction anchors on the 5-year CAGR (7.60%) and the latest filed FY YoY (+6.35%); a 15-year fade start is not a one-year forecast. The bull start (12.92%) and super-bull start (19.92%, with a 1.25 OE multiplier for margin expansion, buybacks and Nexus scale) sit above guidance, so above-trend paths are fully represented — and even the super-bull case returns only 9.02% at this price.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | −4.08% | 0.75 | Volume shock (COVID-type) or loss of anchor contracts; levered OE compresses | $6.50 | 3.87% |
| Bear | 25% | 2.92% | 0.90 | Growth fades to low-single digits; food/labor costs squeeze the thin margin | $10.24 | 4.82% |
| Base | 30% | 7.92% | 1.00 | Blended growth decays normally over the 7.2-yr CAP | $13.77 | 5.74% |
| Bull | 25% | 12.92% | 1.10 | Net-new momentum and Nexus ramp sustain double-digit growth near term | $18.27 | 6.90% |
| Super bull | 10% | 19.92% | 1.25 | Nexus becomes a multi-billion run-rate business; margins expand; buybacks compound | $26.88 | 9.02% |

- **Probability-weighted: IV@15% $14.60 (−73.6% vs price), IV@12% $19.50, weighted IRR 5.98%, base-case IRR 5.74%**
- **Tier by numbers: D** — and bear and bull cases are also D, so there is no tier band to size across.
- Diagnostics (dcf_numbers.json): OE yield 2.47%, terminal value 19.3% of IV@15%, scenario spread 4.13x, net debt 13.06x the TTM OE base, 12.5 months since FY end.
- Hurdle-clearing prices: 15% at $14.60, 20% at $10.20, 25% at $7.79 — the $55.28 price is roughly 3.8x the 15% hurdle price.

## Flags — every fragility flag resolved
- **STALE_FY** (latest FY ended 12.5 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q3 FY2026 (2026-07-03), legs quoted above.
- **NI_OCF_DIVERGENCE** (net income vs OCF differ by >40% in 2024, 2025): explained, not a one-off hiding in the base. FY2025 net income was $326,394,000 vs OCF of $921,035,000; the gap is non-cash D&A of $476,345,000 plus SBC of $58,643,000 (together $534,988,000, most of the $594,641,000 gap), with the remainder working capital and other non-cash items. FY2024 is the same shape: net income $262,522,000 + D&A $435,547,000 + SBC $62,552,000 ≈ OCF $726,514,000. The business is depreciation-heavy (client-site equipment and facilities), so NI understates cash generation structurally; the OCF-based conservative OE already charges full capex and SBC against that OCF, so the divergence does not inflate the base.
- **WIDE_SCENARIO_SPREAD** (super-bull IV 4.13x super-bear IV): real — the spread is driven by the leverage and the low starting OE yield (2.47%), which make IV hypersensitive to the growth start. Confidence is capped at medium, and the verdict is sized to the conservative end; note the spread does not create tier uncertainty here, because every scenario, super bull included, lands in Tier D.
- **HIGH_NET_DEBT** (net debt 13.06x normalized OE): confirmed from the filing figures — FY2025-end debt total $5,405,937,000, cash $639,095,000, net debt $4,766,842,000, plus $316,049,000 of operating lease liabilities outside that figure. On management's EBITDA-based definition the leverage ratio was about 3.25x at FY2025 end (the lowest in nearly 20 years per company reporting) with a target below 3x by FY2026 year-end and roughly 3.5x reported at Q3 FY2026; the engine's 13.1x is against owner's earnings after capex and SBC, which is the thinner and more honest cushion for equity holders. The bear cases carry the stress: at a 0.75–0.90 OE multiplier the weighted IV falls to $6.50–$10.24. Deleveraging is the stated first use of cash, ahead of accelerated buybacks.

## My thoughts / overlay
- The story and the valuation point in opposite directions. Operationally this is the best Aramark in years: raised FY2026 organic growth guidance (9–10%), adjusted EPS growth guided at 20–25%, record retention, record net-new business, and a genuinely capital-light Nexus option on data-center build-outs (management expects $400–500M of Nexus revenue across FY2027–28). None of that is in dispute — it is in the price. At $55.28 the stock trades at roughly 40x TTM owner's earnings (OE yield 2.47%); adjusted-EPS multiples look kinder only because adjusted EPS adds back the costs the conservative OE definition charges.
- Method range: median base (preliminary run) weighted IRR 5.61% → TTM base 5.98%; latest-FY base would print modestly higher still. Every defensible base lands in Tier D, and the super-bull scenario — 19.92% growth start, 1.25x OE — still yields only 9.02%. This is one of the rare sweep names where the verdict is not assumption-dominated: the price, not the model, is the outlier.
- Share count is a slow leak, not a tailwind: diluted shares grew +1.05%/yr in the blend window; TTM buybacks of $96,906,000 against issuance of $49,722,000 (fundamentals.json) and a $0.465 TTM dividend per share are real but small against a $14.78B market cap.
- What would change the answer: a price near the hurdle levels, or Nexus scaling to the multi-billion run-rate analysts project for 2028 while the core holds high-single-digit growth — that combination is the super-bull case, and it still does not clear 15% from $55.28.

## Final verdict
- **Final tier: D** (weighted IRR 5.98% on the TTM base; bear and bull cases also D)
- Confidence: **Medium** (filing-direct TTM base and a verdict robust across every base and scenario, capped by the wide scenario spread and leverage)
- One-liner: Improving contract food/facilities operator with scale and record ~98% retention but thin ~4.3% operating margins and ROIC only just reaching 7.6%, moat 4/10 — at $55.28 it does not clear 15% (weighted IRR 5.98%, weighted IV@15% $14.60; even the super-bull case is 9.02%); it clears 15% only at ~$14.60.
