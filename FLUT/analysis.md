# FLUT — Flutter Entertainment plc
Engine 5.4.0 run, 2026-10-17. Price $75.60 (nasdaq_quote_api), market cap $13,381,999,999.999998 (~$13.38B), diluted shares 177,000,000, shares outstanding 173,539,102 as of 2026-07-31. In scope under $40B.

All figures below are copied from dcf_numbers.json, ttm.json, financials_history.csv or fundamentals.json — none are recomputed.

## What it is
The world's largest online sports-betting and iGaming operator: FanDuel in the US (#1 sportsbook at 39% GGR share and #1 iGaming at 27% GGR share, Q2 2026 release), plus Paddy Power / Betfair / Sky Bet (UK & Ireland), Snai (Italy, acquired April 2025), Sisal, Betnacional/NSX (Brazil, May 2025), PokerStars heritage assets and others. The stock has collapsed ~64% in 2026 (52-week range $72.56–$255.26 per search results) on the Q2 2026 shock: prediction-market competition (Kalshi/Polymarket), a deliberate marketing arms race, rising gambling taxes, the India real-money ban (Junglee closure) and a Brazil ban hitting its local brands.

## Owner's earnings
**FY2025 (10-K, financials_history.csv):** revenue $16,383,000,000; operating cash flow $1,184,000,000; capex $105,000,000; SBC $246,000,000 (always a real cost).
- **Conservative owner's earnings FY2025: $833,000,000 = $4.71/share**
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $1,303,000,000 — higher than the conservative figure; the gap is mostly the very large acquisition-intangible D&A ($1,517,000,000 in FY2025). The OCF-based conservative figure is used throughout.
- OE positive 5 of the last 5 fiscal years (dcf_numbers.json: "5/5"), but per-share OE is volatile: $5.14 (2022), $3.38 (2023), $7.01 (2024), $4.71 (2025).
- Net debt $10,438,000,000 at FY2025 (LongTermDebtNoncurrent + LongTermDebtCurrent basis), plus lease liabilities $606,000,000 — see HIGH_NET_DEBT below. No dividend; buybacks TTM $804,000,000 (fundamentals.json).

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $1,184,000,000 − prior YTD $547,000,000 + current YTD $693,000,000 = **TTM $1,330,000,000**
- Capex: FY $105,000,000 − prior YTD $56,000,000 + current YTD $39,000,000 = **TTM $88,000,000**
- SBC: FY $246,000,000 − prior YTD $126,000,000 + current YTD $120,000,000 = **TTM $240,000,000**
- Shares (current-YTD weighted diluted): **175,000,000**
- **TTM OE total $1,002,000,000 → base OE/share $5.73** (base_source: ttm_json)
- The engine's normalized base (median of last 3 FY OE/share) is $4.71/share — it equals the FY2025 figure because the 3-year window ($3.38 / $7.01 / $4.71) medians there. The TTM base is used because FY2025 is ~10 months stale and the TTM window is filing-derived; the method range below shows what the median base would do instead.

## Moat: 5/10 — moderate/narrow, leadership without proven returns on capital
Justification: FanDuel's #1 US position, global scale and local-hero brands are real, but the measured economics do not support a strong moat: the roic_proxy series in fundamentals.json is −0.7% (2022), −2.8% (2023), +4.7% (2024) and +0.1% (2025), with TTM operating income of −$641,000,000 — nowhere near "well above the cost of capital through a cycle." Part of that is acquisition accounting (huge goodwill/intangibles and their amortization from The Stars Group, Snai and other deals depress operating income and inflate invested capital), which is why the score is 5 and not lower — but a moat claim above 6 cannot be made on this ROIC record. Gross margin is also eroding: 49.1% (2022), 47.4% (2023), 47.7% (2024), 45.2% (2025), 42.5% TTM — gambling-tax hikes and promotional intensity are being absorbed, not passed through.
- FOR: #1 US sportsbook (39% GGR share) and #1 US iGaming (27%) — scale, liquidity and brand with FanDuel; global diversification across US, UKI, Italy, Australia and SEA with local-hero brands; product edge in parlays / same-game parlays and proprietary iGaming content (direct casino AMPs +26% in Q2 2026); iGaming growth (+14% US in Q2 2026) diversifies away from volatile sportsbook hold.
- AGAINST: ROIC near zero across 2022–2025 on the filing-direct proxy and gross margin falling ~7 points in under four years — no demonstrated pricing power against taxes and promos; prediction markets (Kalshi, Polymarket) compete for the same handle without the sportsbook tax/licensing burden, forcing a costly FanDuel Predicts build-out; regulatory hostage in every market — India banned real-money gaming outright (Junglee closed, $556M goodwill impairment in 2025), Brazil's ban costs a company-quantified $70M revenue / $20M adjusted EBITDA in 2026, UK and US state gambling taxes keep rising; sports results (hold) swing quarters — Q2 2026 US sportsbook revenue fell 15% partly on adverse results; leverage (4.3x at Q2 2026 per the release) limits how long a marketing war can be funded.
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — final run (2026-10-17)
**Growth sanity check and recalibration (written reason):** the engine's blended growth start is 19.04% (components: revenue CAGR 5y 34.76%, 3y 20.07%, latest FY YoY 16.62%, OE/share CAGR 2y 18.01%). Every one of those inputs straddles acquisition-driven basis breaks (Stars Group in 2020; Snai April 2025 and NSX/Betnacional May 2025 inflating FY2025 YoY) and predates the 2026 deterioration. Actual recent prints: Q2 2026 group revenue $4,326M, +3% YoY, with US revenue −6% and US sportsbook −15% (Q2 2026 release, via search); FY2026 guidance was cut on 2026-08-05 to $17.91B revenue (≈+9% vs FY2025's $16,383M) and $2,655M adjusted EBITDA, with ~$270M of EBITDA deliberately given up to H2 marketing/prediction-market investment. Scenario starts were therefore recalibrated via offsets (−0.1904 / −0.1404 / −0.0904 / −0.0404 / +0.0096 vs the blend) to 0 / 5 / **10** / 15 / 20% — the base start sits on the guidance print, the bull start (15%) is still below the FY2025 print of 16.62% because that print was M&A-assisted, and even the super-bull start (20%) only matches the inorganic 3-yr CAGR. Probabilities 15/30/30/18/7 — bear weight widened above the 10/25 default per the OE_VOLATILE and HIGH_NET_DEBT flags and the Q2 deterioration; OE multipliers are the defaults 0.75/0.90/1.00/1.10/1.25. Price $75.60.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | 0.0% | 0.75 | Prediction markets take structural handle share; tax hikes and the promo war stick; levered OE stalls | $31.73 | 7.65% |
| Bear | 30% | 5.0% | 0.90 | Low-single-digit organic growth, margins stay at Q2 2026's compressed level | $46.89 | 10.34% |
| Base | 30% | 10.0% | 1.00 | Guidance-level growth decays normally over the CAP; marketing drag laps | $64.05 | 13.21% |
| Bull | 18% | 15.0% | 1.10 | FanDuel Predicts + iGaming offset sportsbook pressure; operating leverage returns | $86.46 | 16.58% |
| Super bull | 7% | 20.0% | 1.25 | Full re-acceleration to the M&A-era growth rate, organically | $120.30 | 21.03% |

- **Probability-weighted: IV@15% $62.02 (−18.0% vs price), IV@12% $83.29, IV@10% $107.11, weighted IRR 12.90%, base-case IRR 13.21%**
- **Tier by numbers: C.** Diagnostics (dcf_numbers.json): OE yield 7.57%, terminal value 19.8% of IV@15%, scenario spread 3.79x, net debt 10.3x normalized OE, 9.5 months since FY end.
- Hurdle prices (weighted): clears 15% at $62.02, 20% at $43.05, 25% at $32.70 — all below the $75.60 price.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.5 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, legs quoted above.
- **BASIS_BREAK_SUSPECT** (>60% revenue jump in the last 5 years): named — The Stars Group acquisition (closed May 2020; revenue steps from $2,528M in 2019 to $9,463M in 2022 on the filed history, with 2020–2021 absent from the US-GAAP series), plus Snai (April 2025) and NSX/Betnacional (May 2025) inflating FY2025. No CAGR straddling these breaks was trusted: scenario starts were set from the Q2 2026 print (+3%) and the cut FY2026 guidance (~+9%), not from the blend.
- **OE_VOLATILE** (OE/share spans >3x over 5 years; filed range in the scored window $3.38–$7.01): real — sports-hold swings, tax and promo cycles. Handled by the TTM base, a widened bear weight (45% on bear-or-worse vs 35% default) and verdict sizing to the bear end.
- **NI_OCF_DIVERGENCE** (2023, 2024, 2025): explained, not a cash problem — net income is −$1,211M / +$162M / −$407M against OCF of $937M / $1,602M / $1,184M because of very large non-cash charges: D&A of $1,285M / $1,097M / $1,517M (acquisition-intangible amortization) and, in 2025, the $556M non-cash Junglee goodwill impairment after India's ban (Q3 2025 reporting, via search), plus Q2 2026 historical tax provisions ($62M Junglee GST, $33M US sales-and-use accrual). The OCF-based conservative OE series used throughout is not contaminated by these non-cash items.
- **WIDE_SCENARIO_SPREAD**: the preliminary default run printed 4.38x; the final recalibrated run prints 3.79x (super-bull IV@15 $120.30 vs super-bear $31.73) and the flag no longer fires, but the range is still wide — confidence is capped at medium and the verdict is sized to the bear end.
- **HIGH_NET_DEBT** (net debt 10.3x normalized OE on the final run): balance sheet from the filing (financials_history.csv, FY2025): total debt $12,266,000,000, cash $1,828,000,000, net debt $10,438,000,000, plus lease liabilities $606,000,000; equity $9,038,000,000. The debt step-up funded Snai, NSX and the $1.76B purchase of Boyd's 5% FanDuel stake (July 2025); the company-reported leverage ratio was 3.7x at Dec 2025 and 4.3x at Q2 2026 against a 2.0–2.5x medium-term target. This is why bear-or-worse carries 45%.
- **TIER_BAND** (bear tier C at 10.34% vs bull tier B at 16.58%): the verdict spans tiers — sized to the bear end: the final tier is the weighted C, and even the base case (13.21%) does not clear 15%.

## My thoughts / overlay
- Method range matters here: the preliminary run on the engine's own inputs (median-of-3 base $4.71, blend growth 19.04%, default probs) printed Tier B at 15.78% weighted IRR and $81.20 IV@15. Switching only to filing-current inputs — TTM base $5.73 (bullish for the score) but growth starts anchored to the +3% Q2 print and cut guidance (bearish) and bear weight widened for leverage — moves it to Tier C at 12.90% / $62.02. The growth recalibration, not the base, is the binding decision, and it is driven by the company's own August guidance cut.
- The bull case for the stock at $75.60 is a sentiment case, not a numbers case: the price already embeds a ~65% drawdown, FanDuel still holds #1 share, iGaming is compounding, and management's $500M cost-savings program (by 2029, per the Q2 release) is not in any scenario above. But on owner's earnings actually filed, a buyer at $75.60 is paying above the 15%-hurdle price in every scenario except bull and super bull (combined 25% weight).
- Watch items: whether the H2 marketing spend actually buys share back (Q3 handle/AMPs), prediction-market regulation, UK budget gambling taxes, Brazil restart, and deleveraging from 4.3x back toward target. CEO transition (Peter Jackson → Dan Taylor, effective 2026-10-01) adds execution uncertainty.
- Data notes: 2020–2021 are absent from the US-GAAP annual history (the filer reported on a 40-F/IFRS basis as The Stars Group before the Flutter combination era) — the engine's 5-yr CAGR is computed across that gap, another reason it was not trusted. Enrichment outputs are filed alongside this analysis; any enrichment failure is non-blocking per spec.

## Final verdict
- **Final tier: C** (weighted IRR 12.90% on the final inputs; bear C 10.34% / bull B 16.58%)
- Confidence: **Medium** (filing-direct TTM base; capped by the 3.79x scenario spread, leverage and the live prediction-market / tax uncertainty)
- One-liner: Global betting leader with a real but unproven-in-ROIC moat 5/10 — at $75.60 it does not clear 15% on current filings (12.9% weighted, IV@15 $62.02 vs $75.60); it clears 15% only at $62.02 or below.
