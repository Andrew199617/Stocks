# AVTR — Avantor, Inc.
Pass-1 run, 2026-10-19, engine release 5.4.0. All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.json, or financials_history.csv — none are recomputed.

## What it is
Global provider of mission-critical products and services to life sciences and advanced technology customers: the VWR lab distribution & services platform plus proprietary Bioscience/Medtech products (J.T. Baker high-purity chemicals, NuSil silicones). In scope: market cap $11.175B at $16.42 (nasdaq_quote_api).

## Owner's earnings
Conservative OE = OCF − capex − SBC; maintenance OE is the NI + D&A variant in financials_history.csv. OE positive 5 of the last 5 fiscal years.

- FY2025 (10-K): OCF $623,800,000; capex $128,800,000; SBC $46,400,000 → latest FY OE total $448.6M, latest FY OE/share $0.66.
- Normalized base (3-yr median OE/share): $0.95 — the FY2023–FY2024 years ($1.01 / $0.95 per share in financials_history.csv) predate the FY2025 step-down, so the median overstates the current run-rate.
- **Base used = TTM through Q1 2026, from ttm.py (filing-direct):**
  - OCF: FY $623,800,000 − prior YTD $109,300,000 + current YTD $58,700,000 = **TTM $573,200,000**
  - Capex: FY $128,800,000 − prior YTD $28,000,000 + current YTD $33,500,000 = **TTM $134,300,000**
  - SBC: FY $46,400,000 − prior YTD $12,400,000 + current YTD $8,600,000 = **TTM $42,600,000**
  - Shares (current-YTD weighted diluted): **676,800,000**
  - **TTM OE total $396,300,000 → base OE/share $0.59** (base_source: ttm_json)
- TTM data limit: the Q2 2026 10-Q (period 2026-06-30, filed 2026-07-29) is not yet in EDGAR companyfacts, so filing-direct TTM stops at 2026-03-31 (fundamentals.json note). The Q2 2026 press release (July 29, 2026) reported net sales $1,692.3M (+0.5% reported, −0.4% organic), operating cash flow $178.2M and free cash flow $142.8M for the quarter, and raised FY2026 organic revenue guidance to −0.5% to +0.5% with adjusted EPS $0.80–$0.83 — stabilization, not a return to the FY2023–24 OE level, so the TTM base stands.

## Moat: 4/10 — weak-moderate
Justification: Real distribution scale and spec-in embedment, but economics say narrow: ROIC proxy ran 5.2–9.3% in FY19–FY24 (never durably above cost of capital), gross margin is eroding, revenue has fallen three straight years, and the Distribution unit itself was written down $785M in Q3 2025. That is a weak-moderate moat, not a wide one.
- Evidence (fundamentals.json): ROIC proxy FY19–FY25: 7.0% / 7.7% / 6.8% / 8.5% / 5.2% / 9.3% / −2.1% (FY2025 negative on the impairment-driven operating loss). Gross margin: 34.6% FY2022 → 33.9% FY2023 → 33.6% FY2024 → 32.7% FY2025 → 32.1% TTM. A moat of 7+ cannot sit on this ROIC history.
- FOR: VWR distribution scale — one of the two largest global lab distributors, 300,000+ customer locations in ~180 countries; spec-in stickiness — materials specified into 85% of the top 20 commercialized biologics, giving recurring bioprocessing demand; proprietary brands with regulatory trust (J.T. Baker, NuSil); cGMP / regulated-workflow embedment raises switching friction in production labs.
- AGAINST: distribution is contestable — larger platforms compete for the same lab spend; revenue down three straight years (FY23–FY25) and the Distribution unit took a $785M goodwill impairment in Q3 2025 on market conditions and projected performance; ROIC at/barely above cost of capital; gross margin eroding; levered balance sheet (below).
- A 4 gives CAP = 7.2 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 7.2 years, 15-year projection.

## DCF — final run (2026-10-19)
Growth sanity check (written reason for recalibration): the engine blend is −3.99% (rev CAGR 5y 0.49%, rev CAGR 3y −4.46%, latest rev YoY −3.41%, OE/share CAGR 2y −19.08%), but the latest prints are better than the blend: TTM revenue −2.0% YoY (fundamentals.json), Q2 2026 reported +0.5% / organic −0.4%, and FY2026 organic guidance is −0.5% to +0.5%. A base start of −4% would sit below what the company just printed and guided, so scenario starts were recalibrated via offsets (−0.06 / −0.01 / +0.04 / +0.08 / +0.13 vs g_base) to −10 / −5 / **0** / +4 / +9%. Probabilities kept at the 10/25/30/25/10 defaults; OE multipliers at the 0.75/0.90/1.00/1.10/1.25 defaults. Price $16.42.

| Scenario | Prob | Growth start | OE mult | IV@15 | IRR |
|---|---|---|---|---|---|
| Super bear | 10% | -10.0% | 0.75 | $2.21 | 3.96% |
| Bear | 25% | -5.0% | 0.9 | $3.23 | 4.79% |
| Base | 30% | 0.0% | 1.0 | $4.36 | 5.75% |
| Bull | 25% | 4.0% | 1.1 | $5.60 | 6.80% |
| Super bull | 10% | 9.0% | 1.25 | $7.69 | 8.54% |

- **Probability-weighted: IV@15% $4.50 (−72.6% vs price), IV@12% $5.91, weighted IRR 5.90%, base-case IRR 5.75%**
- **Tier by numbers: D.** Bear → bull band is D → D (4.79% → 6.80%); even the super bull (8.54%) stays in D.
- Diagnostics (key_numbers.md): OE yield 3.57%, terminal value 17.5% of IV@15%, scenario spread 3.48x, net debt 8.99x normalized OE, 9.6 months since FY end.
- Hurdle-clearing prices (weighted path): 15% at $4.50 · 20% at $3.23 · 25% at $2.52.

## Flags — every fragility flag resolved
- **STALE_FY** (latest fiscal year ended 10 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q1 2026, legs quoted above. The Q2 2026 10-Q is filed but not yet in EDGAR companyfacts, so no filing-direct TTM through Q2 exists; the Q2 press-release figures (quoted above) show stabilization consistent with the recalibrated growth starts, not a higher OE base.
- **NI_OCF_DIVERGENCE** (2023, 2025): 2025 is the $785.0M non-cash goodwill impairment on the Distribution reporting unit recorded in Q3 2025 (company Q3 2025 release) — it drove FY2025 net income to −$530,200,000 and operating income to −$246,200,000 while OCF stayed $623,800,000; it is non-cash and does not touch the OCF-based OE base. 2023: net income $321,100,000 vs OCF $870,000,000 — the gap is the non-cash add-backs in the cash-flow statement, led by depreciation & amortization of $402,300,000 plus SBC $40,500,000 (financials_history.csv). No tax-deposit or working-capital one-off is needed to explain either year, and the conservative OE series is OCF-based throughout, so the divergence does not contaminate the base.
- **HIGH_NET_DEBT** (net debt 9.0x normalized OE on the final run's basis; 5.6x on the preliminary median base): balance sheet from the filing (financials_history.csv, FY2025): cash $365,400,000, debt_current $30,800,000 (LongTermDebtCurrent), debt_lt $3,915,500,000 → net debt $3,580,900,000, plus lease liabilities $185,500,000. The bear and super-bear cases are already stressed (OE multipliers 0.90 / 0.75 with negative growth starts) and still land at 4.79% / 3.96% IRR — leverage is a reason the equity is fragile, but the D verdict does not depend on it: the unlevered OE yield at price is only 3.57%.

## My thoughts / method range
- Method range: on the preliminary median base ($0.95/share) with default starts, the weighted IRR was 7.23% and IV@15% $6.42 — still Tier D. On the TTM base with recalibrated starts it is 5.90% / $4.50. Every defensible method lands in D; the range is $4.50–$6.42 of IV@15% against a $16.42 price.
- The market is pricing the Revival turnaround: Q2 2026 did stabilize (VWR back to organic growth, guidance raised, $112.1M of debt repaid in the quarter per the release), and the $400M run-rate cost-savings program targeted by end-2027 is real optionality. But on filed owner's earnings the stock needs roughly a 73% fall to clear a 15% hurdle — the turnaround has to roughly triple TTM OE/share before the current price clears 15%.
- What would change the verdict: TTM OE/share back above ~$0.95 (the old median) with revenue growing again, or the price near the hurdle prices above.

## Final verdict
- **Final tier: D** (weighted IRR 5.90%; bear → bull D → D)
- Confidence: **Medium** (filing-direct TTM base and all flags resolved; capped below high because companyfacts lags the filed Q2 2026 10-Q)
- One-liner: Levered lab-distribution turnaround, moat 4/10 — does not clear 15% on any scenario (weighted IRR 5.90%, IV@15% $4.50 vs $16.42 price); it would need to fall to ~$4.50 to clear the 15% hurdle on TTM owner's earnings.
