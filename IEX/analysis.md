# IEX — IDEX Corporation
Engine 5.4.0 run, 2026-10-16. Price $235.70 (nasdaq_quote_api), market cap (est) $17.748B — in scope under $40B.

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.json or fundamentals.json — none are recomputed.

## What it is
Diversified engineered-components maker: pumps, valves, flow meters, compressors, dispensing and precision fluidics across three segments — Fluid & Metering Technologies, Health & Science Technologies, and Fire & Safety/Diversified Products. Products are mission-critical, specified into customer systems, and a small share of total system cost. Recent demand is being pulled by semiconductor, data-center (power generation and liquid cooling) and space & defense applications, notably in Health & Science after the Mott acquisition.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $680,400,000; SBC $27,300,000 (always a real cost); capex $63,600,000.
- **Conservative owner's earnings FY2025: $589,500,000 = $7.83/share** (key_numbers.md: latest FY OE/share $7.83; normalized 3-yr median also $7.83)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC) FY2025: $349,800,000 — materially below the conservative figure because of a $145,600,000 working-capital swing in the ΔNWC leg in financials_history.csv. The OCF-based conservative figure is the cleaner base; the maintenance series is volatile year to year on working capital, not on cash generation.
- OE positive 5 of the last 5 fiscal years. Net debt $1.241B (key_numbers.md), lease liabilities $121,900,000 (dcf_numbers.json). Net debt / normalized OE 2.00x.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $680,400,000 − prior YTD $267,400,000 + current YTD $303,700,000 = **TTM $716,700,000**
- Capex: FY $63,600,000 − prior YTD $29,100,000 + current YTD $40,700,000 = **TTM $75,200,000**
- SBC: FY $27,300,000 − prior YTD $18,800,000 + current YTD $21,900,000 = **TTM $30,400,000**
- Shares (current-YTD weighted diluted): **74,300,000**
- **TTM OE total $611,100,000 → base OE/share $8.22** (base_source: ttm_json)
- The normalized base and the latest FY are both $7.83/share, so the TTM base ($8.22) is only modestly above the filed median — no base distortion to resolve. TTM is used because the fiscal year ended 9.5 months ago (see STALE_FY below).

## Moat: 6/10 — moderate
Justification: mission-critical, spec-in engineered components that are a small share of system cost across Fluid & Metering, Health & Science and Fire & Safety niches, with stable ~44-45% gross margins — but ROIC proxy has fallen from 18.6% in 2019 to 10.1% in 2025, growth is mid-single-digit organic plus acquisitions, and larger diversified industrials compete in adjacent markets.
- Evidence (fundamentals.json, filing-direct): roic_proxy 18.6% (2019), 16.3% (2020), 15.7% (2021), 14.4% (2022), 13.2% (2023), 10.4% (2024), 10.1% (2025) — still above a typical cost of capital, but declining every year for six years, which is why this is not a 7+. Gross margin: 44.3% (2021), 44.8% (2022), 44.2% (2023), 44.2% (2024), 44.5% (2025); Q2 2026 gross margin 46.4% in fundamentals.json quarterly — pricing power is holding even as returns on capital compress.
- FOR:
  - Mission-critical, spec-in components — small share of total system cost, high cost of failure, real switching friction once designed in
  - Pricing power evidenced by gross margin held at 44.2-45.1% over the last five fiscal years (44.5% in FY2025, 46.4% in Q2 2026)
  - Diversified niche portfolio (Fluid & Metering, Health & Science, Fire & Safety/Diversified) — weakness in one end market is partly offset by strength in another
  - 80/20 discipline and high-mix, low-volume manufacturing model shifting mix toward semiconductor, data-center and space & defense applications
  - Disciplined bolt-on M&A platform (e.g. Mott) that adds spec-in positions in adjacent high-value niches
- AGAINST:
  - ROIC proxy declining for six straight years: 18.6% (2019) to 10.1% (2025) — franchise returns are compressing toward the cost of capital
  - Organic growth is only mid-single-digit; reaching higher growth depends on acquisitions, with goodwill-heavy balance sheet risk
  - Net income fell from $596.1M in FY2023 to $483.2M in FY2025 despite revenue growth — acquisition debt, interest and amortization are eating operating gains
  - Larger, better-scaled competitors (Eaton, Parker-Hannifin, Emerson, AMETEK, Roper) in adjacent fluid and engineered-component markets
  - Cyclical industrial end markets; Q2 2026 strength leans on data-center/semiconductor/space demand and included a one-off tariff refund benefit
- A 6 gives CAP = 9.8 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 9.8 years, 15-year projection.

## DCF — final run (2026-10-16)
Growth sanity check: the engine's blended growth is 4.60% (rev CAGR 5y 8.02%, rev CAGR 3y 2.81%, latest rev YoY 5.77%, OE/share CAGR 2y -0.90%; share count CAGR -0.31%). Recent prints are stronger than the blend: Q1 2026 revenue YoY +8.9% and Q2 2026 revenue YoY +6.4% in fundamentals.json quarterly, Q2 organic revenue +5%, and management raised FY2026 organic sales growth guidance to 5% to 6%. The base start was therefore lifted +1pp to 5.6% to sit on the guidance midpoint rather than below what the company just printed. The default super-bull start (16.6% on the preliminary run) was compressed to 11.6% — IDEX has not printed sustained growth near 16% organically, and a super-bull case for a mature industrial should be an acceleration to low-double-digits plus buybacks/M&A, not a growth-stock path. Probabilities 10/25/30/25/10; OE multipliers 0.75/0.90/1.00/1.10/1.25. Price $235.70.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -5.4% | 0.75 | Industrial recession; data-center/semiconductor orders pause; mix reverses | $35.60 | 4.16% |
| Bear | 25% | -0.4% | 0.90 | Flat organic growth; ROIC keeps drifting down; no M&A contribution | $53.34 | 5.22% |
| Base | 30% | 5.6% | 1.00 | Guidance-level organic growth fades normally over the CAP | $77.41 | 6.74% |
| Bull | 25% | 8.6% | 1.10 | HST / Mott, data-center and semiconductor demand sustains high-single-digit growth | $97.31 | 7.92% |
| Super bull | 10% | 11.6% | 1.25 | Durable low-double-digit compounding with successful bolt-ons and margin recovery | $126.34 | 9.57% |

- **Probability-weighted: IV@15% $77.08 (-67.3% vs price), IV@12% $102.52, IV@10% $130.91, weighted IRR 6.73%, base-case IRR 6.74%**
- **Tier by numbers: D** — bear tier D, bull tier D; the whole band is D. Diagnostics (key_numbers.md): OE yield 3.49%, terminal value 18.9% of IV@15%, scenario spread 3.55x, net debt 2.00x normalized OE, 9.5 months since FY end.
- Hurdle-clearing prices (weighted path): 15% at $77.08, 20% at $54.26, 25% at $41.71.

## Flags — every fragility flag resolved
- **STALE_FY** (latest fiscal year ended 9 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026 ($8.22/share), quoted above, not the FY2025 $7.83/share.
- No other fragility flags on the final run. The preliminary run's WIDE_SCENARIO_SPREAD (4.5x) was addressed by the written growth recalibration above: the final spread is 3.55x, and confidence is held at medium — never high — in part for that remaining spread and the ROIC trend.

## My thoughts / overlay
- This is a valuation verdict, not a quality verdict. OE has been positive 5/5 years, the TTM base is clean (no overrides, no data gaps), gross margin is stable, and Q2 2026 orders and the raised FY2026 guide (organic 5% to 6%, adjusted EPS $8.70 to $8.85 in the quarter's reporting) point the right way. None of that matters at $235.70 against a $8.22 TTM OE/share — an OE yield of only 3.49%.
- The method range does not save it: every scenario, including super bull at 11.6% growth start and a 1.25 OE multiplier, is Tier D (super-bull IRR 9.57%, IV@15% $126.34). Changing the base back to the filed median ($7.83) or keeping the default scenario offsets only makes the result worse or leaves it in D (preliminary weighted IRR 6.63%).
- The real debate for a buyer is the ROIC slope, not this year's guide: 18.6% → 10.1% in six years, and net income falling while revenue rises, says acquired growth is being bought at rising capital intensity. If ROIC stabilizes in the low teens and HST/Mott mix lifts organic growth sustainably, the growth fade (CAP 9.8y) could prove conservative — but the price already assumes far more than even that case delivers here.
- Balance sheet is not the problem: net debt $1.241B is 2.00x normalized OE, and buybacks are shrinking the count slowly (share count CAGR -0.31%, already credited in the blend).

## Final verdict
- **Final tier: D** (weighted IRR 6.73% on the final inputs; bear→bull band D→D, full scenario range 4.16%–9.57%)
- Confidence: **Medium** (high on the OE base — clean TTM, no gaps or overrides — medium on the growth path given the 3.55x scenario spread and the ROIC decline)
- One-liner: Quality engineered-components compounder, moat 6/10 — does not clear 15% at $235.70 (weighted IRR 6.7%, weighted IV@15% $77.08); clears 15% only below $77.08, and even the super-bull case yields only 9.6%.
