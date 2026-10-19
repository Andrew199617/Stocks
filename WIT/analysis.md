# WIT — Wipro Limited
Engine 5.4.0 run, 2026-10-16. In scope (market cap $20.355B, under the $40B cutoff). All figures below are copied from key_numbers.md, dcf_numbers.json, financials_history.csv, fundamentals.json or the cited results releases — none are recomputed.

## What it is
One of India's big-four IT services firms (NYSE ADS, 20-F filer, reports in INR under IFRS): application development and maintenance, infrastructure and cloud services, consulting and BPO for global enterprises, overwhelmingly delivered from India. 236,328 employees at September 30, 2026 (Q2 FY27 results release). The business has been ex-growth in USD terms for four years: filed USD revenue $10.425B (FY22) → $11.011B (FY23) → $10.770B (FY24) → $10.428B (FY25), and the latest quarter (Q2 FY27, ended 2026-09-30, released 2026-10-15) printed IT services revenue of $2,611.5M — flat sequentially in constant currency, +0.6% YoY in constant currency, +0.3% YoY in USD — with Q3 FY27 guidance of −1.5% to +0.5% constant currency.

## Owner's earnings
**FY2025 (20-F via EDGAR, from financials_history.csv):** operating cash flow $1,983,000,000; capex $173,000,000; SBC $65,000,000 (always a real cost — and genuinely small here, 0.62% of revenue per fundamentals.json).
- **Conservative owner's earnings FY2025: $1,745,000,000 = $0.17/share** (key_numbers.md: latest FY OE/share $0.17; exact base figure $0.1664 in dcf_numbers.json).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $813,074,300 in FY2025 — far below the conservative figure because FY25 carries a $907,000,000 working-capital build (ΔNWC in financials_history.csv). The maintenance series is ΔNWC-dominated and whipsaws: $867,168,320 (FY23) → $1,797,511,290 (FY24) → $813,074,300 (FY25). The OCF-based conservative definition is the steadier series and is the one the engine bases on; the gap between the two definitions is a real method-range caveat and is priced into the low confidence below.
- OE positive 5 of the last 5 fiscal years. Net debt $467.0M (key_numbers.md), plus lease liabilities of $354,000,000 (dcf_numbers.json) — net debt is 0.27x normalized OE; leverage is not part of the story either way.
- **Base used = $0.1664/share, the median of the last 3 fiscal years' conservative OE/share** (base_source: median_of_last_3_fy_oe_per_share). Latest and normalized base are the same $0.17 in key_numbers.md — no BASE_DIVERGENCE. The base years (FY23–25) are on a consistent share basis (~10.5–11.0B shares, see DILUTION below) and tie to the current diluted count of 10,488,939,392.
- No TTM base: this is an IFRS filer, ttm.py reads us-gaap only and exited non-zero, so the median base stands per the worker spec (see STALE_FY).

## Moat: 4/10 — weak, eroding
Justification: Scale and sticky multi-year enterprise relationships are real, and ROIC proxy has stayed above the cost of capital (~13% FY23–25, gross margin stable ~29–31%) — but the labor-arbitrage model is replicable, pricing power is weak, AI automation deflates the legacy ADM/infra base, and returns have converged from ~20% (FY16/FY21) toward ~13% while USD revenue has been flat for four years and peers (TCS, Infosys, Accenture) take share.
- Evidence (fundamentals.json, roic_proxy = after-tax operating income over equity + debt − cash): 20.5% (FY16), 20.5% (FY21), 16.1% (FY22), 12.8% (FY23), 12.9% (FY24), 13.1% (FY25) — a decade of convergence toward the cost of capital, not a wide-moat return profile. Gross margin over the last five fiscal years: 31.7% / 29.7% / 28.7% / 29.6% / 30.7% (FY21–25) — stable, but stable at commodity-services levels with no expansion. Operating margin compressed from 19.9% (FY21) to 17.0% (FY25).
- FOR: Top-tier Indian IT scale: ~$10.4B revenue, 236,328 employees (Q2 FY27 release), multi-year outsourcing relationships with genuine switching friction; ROIC proxy still above cost of capital — 12.8–13.1% FY23–25 — with gross margin stable at 28.7–30.7% over the last five fiscal years; durable cash conversion: operating cash flow ran well above net income in recent prints (Q2 FY27 OCF 165.8% of net income per the results release), funding dividends and repeated buybacks.
- AGAINST: Labor-arbitrage delivery model is replicable — no proprietary product, data or network effect; TCS, Infosys, Accenture and HCLTech bid the same wallet; AI automation deflates traditional application/infrastructure work and clients demand the productivity be passed through — pricing power is weak; growth has lagged peers for a decade: USD revenue flat FY22–25, IT services +0.6% YoY constant currency in Q2 FY27, large-deal bookings down ~59% QoQ in that release; ROIC proxy down from ~20% (FY16 and FY21) to ~13% (FY23–25) — returns converging toward the cost of capital; client global capability centers (insourcing) compete for the same spend.
- A 4 gives CAP = 7.2 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 7.2 years, 15-year projection.

## DCF — engine 5.4.0 final run (2026-10-16)
Scenario design: engine defaults kept throughout — probabilities 10/25/30/25/10, growth offsets −12/−5/0/+5/+12pp against the blended start, OE multipliers 0.75/0.90/1.00/1.10/1.25 — because the evidence (four flat USD years, flat constant-currency prints, weak deal bookings) genuinely centers on stagnation, and the deviations the blend contains are itemized under the growth sanity check below rather than silently re-centered. Price $1.94 (key_numbers.md; $1.9406 in dcf_numbers.json, nasdaq_quote_api).

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -10.0% | 0.75 | AI deflation + GCC insourcing bite; USD revenue shrinks outright | $0.63 | 6.14% |
| Bear | 25% | -7.4% | 0.9 | INR keeps sliding, cc growth stays at/below zero | $0.83 | 7.54% |
| Base | 30% | -2.4% | 1.0 | The last four years repeat: flat cc, USD drag | $1.13 | 9.62% |
| Bull | 25% | 2.6% | 1.1 | AI-led deals convert, cc growth recovers to low single digits | $1.51 | 12.21% |
| Super bull | 10% | 9.6% | 1.25 | Full re-acceleration to FY23-style USD growth and beyond | $2.24 | 16.78% |

- **Probability-weighted: IV@15% $1.21 (−37.6% vs price), IV@12% $1.58, IV@10% $2.00, weighted IRR 10.22%, base-case IRR 9.62%**
- IRR band: bear 7.54% (tier D) → bull 12.21% (tier C). Hurdle-clearing prices on the weighted path: 15% at $1.21, 20% at $0.87, 25% at $0.68.
- **Tier by numbers: C.** Diagnostics (key_numbers.md): OE yield 8.57%, terminal value 17.3% of IV@15%, scenario spread 3.56x, net debt 0.27x normalized OE, 18.5 months since FY end.
- **Growth sanity check:** the base start (−2.4%) sits below the latest constant-currency print (Q2 FY27: +0.6% YoY cc, flat QoQ; Q3 guidance −1.5% to +0.5% cc). Written reason for keeping it: the blend is computed in USD, and a USD ADS holder really does eat the translation drag — the engine's period-end ECB rate fell from 0.01199 (FY24) to 0.0117 (FY25) USD per INR (dcf_numbers.json fx_conversion), and the Q2 FY27 release guides at USD/INR 95.76. The blend also carries the spurious −5.00% share-count adjustment resolved under DILUTION. Both effects make the weighted result conservative rather than aggressive. At the other end, the super-bull start of 9.6% is above the fastest USD revenue growth in the filed history (FY23, when revenue rose from $10.425B to $11.011B) — it is a deliberate 10% tail, not a forecast.

## Flags — every fragility flag resolved
- **STALE_FY** (latest fiscal year ended 19 months ago): the FY2026 20-F exists — filed 2026-06-02, period ended 2026-03-31 — but is "not yet in EDGAR companyfacts," so the engine's annual history stops at 2025-0
...[truncated 2185 chars]