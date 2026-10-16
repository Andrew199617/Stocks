# UTHR — United Therapeutics Corporation

v5 run, 2026-10-15. Price $545.08 (nasdaq_quote_api), market cap $26.109B — in scope under $40B. All figures below are copied from dcf_numbers.json, ttm.json, financials_history.csv, or key_numbers.md — none are recomputed.

## What it is
Biotechnology company built on treprostinil for pulmonary arterial hypertension (PAH) and pulmonary hypertension associated with interstitial lung disease (PH-ILD): Tyvaso DPI and nebulized Tyvaso, Remodulin, Orenitram, plus Unituxin (neuroblastoma). A public benefit corporation also investing heavily in manufactured / xenotransplantation organs, with two xeno-organ production facilities planned to launch in Minnesota and Texas. Revenue is concentrated in the treprostinil franchise — Tyvaso alone was about 58% of Q2 2026 revenue per the earnings reporting.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** revenue $3,182,700,000; net income $1,334,700,000; operating cash flow $1,561,200,000; capex $520,500,000; SBC $147,700,000 (always a real cost); D&A $85,600,000.
- **Conservative owner's earnings FY2025: $893,000,000 = $18.64/share** (OCF − capex − SBC; latest FY OE/share in dcf_numbers.json).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $1,188,500,000 for FY2025 — higher than the conservative figure because capex far exceeds D&A. That gap is the central OE judgment: capex jumped from $230,400,000 in FY2023 and $246,500,000 in FY2024 to $520,500,000 in FY2025, and TTM capex is higher still, reflecting the manufacturing / xeno-organ buildout. Some of that is growth capex, but the engine's conservative definition charges it all, and this analysis keeps that charge — the facilities must be built and maintained whether or not xeno-organs ever earn revenue.
- OE positive 5 of the last 5 fiscal years. Cash at FY2025 was $1,557,100,000 in financials_history.csv; the engine produced no net-debt figure (net_debt_latest is null, debt tags absent in its output), so no net-debt multiple is quoted here. Search reporting put cash, cash equivalents and investments at $3.8 billion at Q2 2026 — a liquid, lightly levered balance sheet by that reporting, folded into the verdict qualitatively, not as a computed figure.
- Q2 2026 (search results, earnings reporting): total revenue $783.3 million, down 2% year over year and below consensus; diluted EPS $7.27, up 13% year over year, helped by an 11% tax rate versus 24% a year earlier and by accelerated share repurchases. Tyvaso DPI revenue $326.6 million, up 4%; nebulized Tyvaso $126.0 million, down 18%; Remodulin $126.3 million, down 6%; Orenitram $125.7 million, up 1%; Unituxin $65.2 million, up 12%. Management declined to reaffirm or update its 2026 revenue growth outlook and conceded a narrower path to its $4 billion run-rate goal for the end of 2027.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $1,561,200,000 − prior YTD $652,900,000 + current YTD $776,900,000 = **TTM $1,685,200,000**
- Capex: FY $520,500,000 − prior YTD $137,100,000 + current YTD $208,800,000 = **TTM $592,200,000**
- SBC: FY $147,700,000 − prior YTD $69,600,000 + current YTD $77,300,000 = **TTM $155,400,000**
- Shares (current-YTD weighted diluted): **46,500,000** (down from the FY2025 47,900,000 after the $1.5 billion accelerated repurchase in March 2026 reported in search results)
- **TTM OE total $937,600,000 → base OE/share $20.16** (base_source: ttm_json)
- The engine's normalized base (median of last 3 FY OE/share) is $18.64/share — close to the TTM figure, so the base choice is not what drives the verdict; both bases produce Tier D (see Thoughts).

## Moat: 6/10 — moderate-strong, concentrated
Justification: entrenched prostacyclin leadership, device and specialist-channel advantages and proven pricing power in PAH/PH-ILD, but the franchise rests overwhelmingly on one molecule facing generic and branded competition, with the next growth leg binary on 2027 approvals.
- FOR: Dominant treprostinil franchise across inhaled, oral and infused delivery — breadth no single rival matches in PAH/PH-ILD
- FOR: Tyvaso DPI device differentiation and patent protection reported through 2035, with litigation defending it
- FOR: Proven pricing power — Tyvaso DPI Q2 growth included a price increase, and margins / returns on capital have held through a cycle
- FOR: Deep specialist prescriber relationships and clinical experience; record starts, referrals and total patients exiting Q2 2026 per management
- FOR: Pipeline breadth inside its own pathway — ralinepag (once-daily oral prostacyclin) and Tyvaso label expansion into IPF/PPF
- AGAINST: Single-molecule concentration — treprostinil products supply the bulk of revenue; Tyvaso alone about 58% of Q2 revenue
- AGAINST: Generic / branded erosion already visible — nebulized Tyvaso down 18% and Remodulin down 6% in Q2 2026, nebulized generic entry from January 2026, Orenitram generics expected after 2027
- AGAINST: New PAH mechanisms (e.g. sotatercept-class therapies) are changing the treatment paradigm and competing for the same patients
- AGAINST: The growth reset is binary — Tyvaso in IPF (FDA review due late April 2027) and ralinepag in PAH (action date June 24, 2027) must both land and ramp; IPF launch initially relies on nebulized delivery, with dosing-frequency / tolerability questions raised by analysts
- AGAINST: Xenotransplantation / manufactured organs consume large capex today with no commercial revenue — optionality, not a moat yet
- A 6 gives CAP = 9.8 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 9.8 years, 15-year projection.

## DCF — v5 final run (2026-10-15)
Growth recalibration (written reason): the engine's blended growth is 15.42% and g_base is 15.84%, built from the 5-yr revenue CAGR of 16.50%, 3-yr CAGR of 18.01%, latest FY revenue YoY of 10.61% and OE/share CAGR of 14.35%. Those historical inputs overstate the current run rate: Q2 2026 revenue fell 2% year over year, the base business shrank, and management declined to reaffirm its 2026 outlook. Scenario starts were therefore recalibrated via offsets (−0.158 / −0.118 / −0.068 / −0.008 / +0.062 vs g_base) to 0.0 / 4.0 / 9.0 / 15.0 / 22.0%. The base start of 9.0% sits just under the latest FY revenue print of 10.61% and well above the Q2 stall — a recovery, not a continuation of the stall, is already assumed. The bull start of 15.0% approximates the historical revenue CAGRs and requires the 2027 catalysts to land; the super-bull start of 22.0% requires IPF + ralinepag to become multi-billion-dollar contributors and capex to normalize — it is deliberately above every recent revenue print, which is why it carries only 8% probability. Probabilities were skewed bearish versus defaults (15/30/30/17/8) for the shrinking base business and the binary 2027 calendar. OE multipliers are the defaults 0.75/0.90/1.00/1.10/1.25.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | 0.0% | 0.75 | Generic / branded erosion accelerates; IPF or ralinepag disappoints; capex stays elevated | $111.13 | 4.96% |
| Bear | 30% | 4.0% | 0.90 | Base business flat-to-low growth; one catalyst lands late or ramps slowly | $159.35 | 6.22% |
| Base | 30% | 9.0% | 1.00 | Growth recovers toward the FY2025 print; catalysts land but ramp normally | $221.15 | 7.85% |
| Bull | 17% | 15.0% | 1.10 | Historical-CAGR growth resumes on IPF + ralinepag; capex normalizes | $317.39 | 10.24% |
| Super bull | 8% | 22.0% | 1.25 | Both 2027 approvals become multi-billion-dollar lines; xeno optionality gains credibility | $490.71 | 13.96% |

- **Probability-weighted: IV@15% $224.03, IV@12% $302.31, IV@10% $390.25, weighted IRR 7.98%, base-case IRR 7.85%**
- **Tier by numbers: D.** Diagnostics (dcf_numbers.json): OE yield 3.70%, terminal value 20.36% of IV@15%, scenario spread 4.42x, 9.5 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (latest fiscal year ended 9.5 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, quoted above with all four inputs (FY, prior YTD, current YTD for OCF/capex/SBC, and the current-YTD share count). TTM OE/share of $20.16 is above the FY2025 / normalized $18.64, driven by the shrunken share count and higher TTM OCF despite record capex.
- **WIDE_SCENARIO_SPREAD** (super-bull IV 4.42x super-bear IV): real — the 2027 approval calendar makes the outcome range genuinely wide. Confidence is set to low, and the verdict is sized to the conservative end. Note the spread does not rescue the price: even the super-bull scenario's IRR of 13.96% is below the 15% hurdle at $545.08.

## My thoughts / overlay
- The honest headline is that the price, not the business, is the problem. This is a profitable, cash-generative franchise with OE positive 5/5 years — and at $545.08 the OE yield on the TTM base is only 3.70%. The market is paying today for IPF, ralinepag and xeno-organ success that an owner's-earnings DCF on filed cash flows cannot yet see.
- Method range: the preliminary run (median base $18.64/share, default growth / probabilities, moat 5) gave a weighted IRR of 9.47% and weighted IV@15% of $282.76 — also Tier D. The final TTM-based, growth-recalibrated run gives 7.98% / $224.03. Defensible inputs span the D tier only; no defensible run approached the 15% hurdle, and even the 8%-probability super bull printed 13.96%.
- Capex is the swing judgment. Charging all capex (conservative definition) treats the xeno / manufacturing buildout as a cost of staying in business. If a reader believes most of the $592,200,000 TTM capex is pure growth investment, the maintenance definition ($1,188,500,000 in FY2025 vs $893,000,000 conservative) points to a materially higher OE — but that reader is then underwriting unproven organ-manufacturing revenue, which is a venture bet, not owner's earnings.
- Q2 2026 earnings quality was flattered: EPS rose 13% on falling revenue via an 11% tax rate (vs 24%) and buybacks. The filing-direct OE series is immune to the tax-rate optics — SBC and the full capex charge are already in it.
- Price that clears 15%: the weighted IV@15% of **$224.03** — the stock would need to trade near that level, less than half the $545.08 price, to clear Andrew's hurdle on these inputs, and a margin of safety against the bear cases ($159.35 / $111.13) argues for waiting for a price below the weighted IV, not at it.

## Final verdict
- **Final tier: D** (weighted IRR 7.98% on the v5 final inputs; preliminary and final methods both print D)
- Confidence: **Low** (WIDE_SCENARIO_SPREAD of 4.42x, single-molecule concentration, and two binary 2027 FDA decisions dominate any single path)
- One-liner: Quality treprostinil franchise, moat 6/10 — but at $545.08 it does not clear 15% (weighted IRR 7.98%, IV@15 $224.03 vs $545.08 price; even super-bull prints 13.96%); it clears 15% only near $224.
