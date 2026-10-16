# TW — Tradeweb Markets Inc.
v5 run, 2026-10-15. Market cap $23.78B at $110.68 (nasdaq_quote_api) — in scope under $40B.

All figures below are copied from dcf_numbers.json, ttm.py output (ttm.json), or financials_history.csv — none are recomputed.

## What it is
Electronic marketplaces for trading rates, credit, equities, and money markets — a pioneer in electronic bond trading (founded 1996). Clients are dealers, asset managers, and other financial institutions. Q2 2026 was its second-highest revenue quarter ever: revenue $558.9M (+9.0% YoY, with June accelerating to over +20% YoY), average daily volume $3.0 trillion (+18.2% YoY), adjusted EBITDA margin 54.4%. Full-year 2026 guidance was left unchanged (adjusted expenses $1,100–1,160M, trending to the top half; cash capex and capitalized software ~$107–117M).

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $1,167,646,000; capex $40,552,000; SBC $103,537,000 (always a real cost).
- **Conservative owner's earnings FY2025: $1,023,557,000 = $4.76/share** (latest FY OE/share, dcf_numbers.json)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $1,022,429,000 — essentially identical to the conservative figure, which raises confidence in the OE level.
- OE positive 5 of the last 5 fiscal years. Revenue FY2025 $2,052,429,000 (+18.92% YoY); revenue CAGR 18.12% (5y) / 19.96% (3y).
- Balance sheet: the engine captured cash of $2,084,739,000 (FY2025) but no debt tags, so net_debt_latest is null in dcf_numbers.json and no net-debt figure is quoted here — the model carries no balance-sheet adjustment. (Reported interest expense is negligible relative to operating income, so this is a reporting gap in the pull, not a leverage concern.)
- Structure caveat: Tradeweb is an Up-C — consolidated OCF includes earnings attributable to non-controlling interests (Q2 2026: net income $206.7M total, $181.3M attributable to Tradeweb Markets Inc., $25.4M to NCI, per the Q2 2026 release). The standardized engine divides consolidated OE by the parent's diluted shares, which modestly overstates attributable OE/share. This is not adjusted in the numbers; it is one reason the verdict is sized conservatively and confidence is low.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $1,167,646,000 − prior YTD $469,394,000 + current YTD $497,936,000 = **TTM $1,196,188,000**
- Capex: FY $40,552,000 − prior YTD $7,110,000 + current YTD $17,929,000 = **TTM $51,371,000**
- SBC: FY $103,537,000 − prior YTD $49,096,000 + current YTD $54,865,000 = **TTM $109,306,000**
- Shares (current-YTD weighted diluted): **213,059,281**
- **TTM OE total $1,035,511,000 → base OE/share $4.86** (base_source: ttm_json)
- The engine's normalized base (median of last 3 FY OE/share) is $3.57/share — rejected as the base because it is dragged by FY2023 (conservative OE total $662,432,000 in the filed history, vs $1,023,557,000 in FY2025) before the FY2024–25 step-up; the latest FY ($4.76) and the TTM ($4.86) agree closely, so the TTM is the cleaner current run-rate. The median is retained in the method range below.

## Moat: 7/10 — strong
Justification: dominant rates franchise with real network effects — over 50% institutional U.S. Treasury electronic share for the ninth consecutive quarter in Q2 2026 and a record 24.1% core risk (swaps) share — plus workflow embedding (AiEX automated trading, trades +45% YoY) and 54% EBITDA margins. Not 8+: credit is contested (MarketAxess and others), wholesale Treasury share is slipping against streaming competitors, fees per million are compressing on mix (−10.3% swaps, −11.4% cash credit in Q2 2026), and volumes ride market volatility.
- FOR: Network effects — liquidity attracts liquidity across its dealer and institutional client network; #1 in rates with >50% institutional U.S. Treasury share for nine straight quarters
- FOR: Workflow embedding and switching costs — AiEX automation and integrated protocols are built into client trading workflows
- FOR: Secular electronification tailwind — fixed income still shifting from voice to electronic, especially credit and international markets (international revenue +13.9% in Q2 2026, 65% of total growth)
- FOR: Capital-light, high-margin model — 54.4% adjusted EBITDA margin, capex trivial vs OCF
- AGAINST: Fee compression — average fees per million fell double digits in swaps and cash credit in Q2 2026 on mix shift
- AGAINST: Contested adjacencies — credit share still being fought for against MarketAxess/Bloomberg; wholesale Treasury revenue −1% YoY in Q2 2026 amid intense streaming competition
- AGAINST: Volatility dependence — volumes (and revenue) spike and fade with market volatility; Q2 2026 revenue growth slowed to +9.0% as volatility normalized
- AGAINST: Retail credit weakness — retail credit / muni revenue fell 22% in Q2 2026
- A 7 gives CAP = 11.1 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 11.1 years, 15-year projection.

## DCF — v5 final run (2026-10-15)
Engine blended growth 19.44% (rev CAGR 5y 18.12%, 3y 19.96%, latest YoY 18.92%, OE/share CAGR 2y 23.64%), adjusted −1.03pp for share-count trend (dilution ~1.03%/yr), giving g_base 18.41%. Default offsets (−12/−5/0/+5/+12pp) and OE multipliers (0.75/0.90/1.00/1.10/1.25) and default probabilities (10/25/30/25/10) were kept — the evidence is balanced (secular tailwind vs fee compression and a soft Q2 print).
Sanity check vs actual prints: the base start (18.41%) sits above Q2 2026's +9.0% revenue print but in line with FY2025 revenue (+18.92%) and ADV growth (+18.2% in Q2) — Q2 revenue lagged volume on fee mix, and June revenue accelerated to over +20% YoY; the super-bull start (30.41%) is below FY2025's actual OE/share step-up implied by the filed history (latest FY OE/share $4.76 vs the $3.57 median year). No start sits implausibly above or below what the company has actually printed for OE.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | 6.41% | 0.75 | Volatility fades, fee compression bites, credit share stalls | $35.96 | 6.75% |
| Bear | 25% | 13.41% | 0.90 | Q2-style ~9-13% growth sticks; wholesale keeps slipping | $60.17 | 9.79% |
| Base | 30% | 18.41% | 1.00 | Electronification tailwind holds at recent FY rates | $84.79 | 12.51% |
| Bull | 25% | 23.41% | 1.10 | Credit/international share gains compound; AiEX scales | $118.22 | 15.66% |
| Super bull | 10% | 30.41% | 1.25 | Durable multi-asset market-utility path at FY25 OE momentum | $186.82 | 20.80% |

- **Probability-weighted: IV@15% $92.31 (−16.60% vs price), IV@12% $129.15, IV@10% $171.20, weighted IRR 13.29%, base-case IRR 12.51%**
- **Tier by numbers: C.** Diagnostics (dcf_numbers.json): OE yield 4.39%, terminal value 24.43% of IV@15%, scenario spread 5.20x, 9.46 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.46 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, quoted above.
- **NI_OCF_DIVERGENCE** (2023, 2024): structural, not a one-off. Net income was $364,866,000 vs OCF $746,089,000 in 2023 and $501,507,000 vs $897,741,000 in 2024 (financials_history.csv). The gap is dominated by large non-cash D&A — $185,350,000 (2023) and $219,999,000 (2024) in the filed history, much of it acquisition/Refinitiv-transaction intangible amortization (the Q2 2026 release separately reconciles ~$39.9M per quarter of acquisition/Refinitiv D&A) — plus SBC added back in OCF ($65,128,000 in 2023; $89,649,000 in 2024). The OE base is built from OCF, so the divergence does not contaminate it; the honest caveat is the reverse — intangible amortization is non-cash but the acquisitions behind it were real spending, which an OCF-minus-capex OE does not charge for. Another reason for low confidence.
- **SECTOR_MODEL_MISMATCH** (Finance): accepted — Tradeweb is a marketplace, not a lender, so OE/capex logic fits better than for a bank, but the standardized model still misses the Up-C/NCI structure and acquisition-amortization economics above. Confidence graded low and the tier treated as soft, per the flag.
- **WIDE_SCENARIO_SPREAD** (5.20x): real — outcomes hinge on how long mid-to-high-teens growth persists against fee compression. Confidence is capped (graded low), and the verdict is sized to the conservative end.

## My thoughts / overlay
- Method range: the preliminary run (median base $3.57/share, default moat 5) gave weighted IRR 9.82% and IV@15% $60.04 — Tier D. The final run (TTM base, moat 7) gives 13.29% / Tier C. Defensible inputs span D to C; no defensible run clears 15% at $110.68 — even the bull case alone only just clears it (15.66%).
- Quality is not the debate: OE positive 5/5 years, conservative and maintenance OE agree to within ~$1M in FY2025, capex is trivial, SBC is a real but manageable cost (TTM SBC $109,306,000 against TTM OCF of $1,196,188,000), and the share count is roughly flat TTM (213,059,281 current-YTD vs 214,898,240 FY) after ~1%/yr dilution over the longer window (already charged −1.03pp in the blend).
- The debate is price: at $110.68 the market is paying for the bull path. The price that clears 15% on the weighted case is the weighted IV@15% itself, $92.31 — a buyer at today's price is underwriting ~13.3%, not 15%, and a margin of safety means paying materially below $92.31.
- Risks: fee-per-million compression as mix shifts to lower-fee protocols, wholesale Treasury share loss to streaming competitors, a prolonged low-volatility regime cutting volumes, and cost growth (technology/communications +38.9% YoY in Q2 2026 on data/AI investment) trending adjusted expenses to the top half of guidance.

## Final verdict
- **Final tier: C** (weighted IRR 13.29% on the v5 final inputs; method range D to C)
- Confidence: **Low** (SECTOR_MODEL_MISMATCH + WIDE_SCENARIO_SPREAD 5.20x + Up-C/NCI overstatement in the standardized base)
- One-liner: High-quality electronic-trading franchise, moat 7/10 — but at $110.68 it prices in the bull case: weighted IRR 13.29%, IV@15% $92.31; it clears Andrew's 15% hurdle only at or below ~$92.
