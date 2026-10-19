# ZBH — ZIMMER BIOMET HOLDINGS, INC.
Pass-1 run, 2026-10-16 (engine 5.4.0). Price $94.98 (nasdaq_quote_api), market cap ~$18.87B — in scope under $40B.

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.json, or fundamentals.json — none are recomputed.

## What it is
The largest pure-play orthopedics company: Knees, Hips, S.E.T. (sports medicine, extremities, trauma, craniomaxillofacial/thoracic) and Technology & Data, Bone Cement and Surgical (incl. the ROSA robotics platform). Warsaw, Indiana; NYSE; SIC 3842.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $1,697.1M; capex $224.5M; SBC $90.2M (always a real cost).
- **Conservative owner's earnings FY2025: $1,382.4M = $6.96/share** (latest FY OE/share, key_numbers.md).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $1,325.2M — same ballpark as the conservative figure.
- OE positive 5 of the last 5 fiscal years. Net debt $6,927.2M (LongTermDebtNoncurrent+LongTermDebtCurrent basis) plus $233.0M lease liabilities — legacy Biomet-merger leverage, see HIGH_NET_DEBT below.
- Management guides up to $1B of buybacks in FY2026; diluted share count fell from 209.7M (FY2023) to 198.7M (FY2025), share CAGR −1.87%/yr.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $1,697.1M − prior YTD $761.0M + current YTD $807.2M = **TTM $1,743.3M**
- Capex: FY $224.5M − prior YTD $94.7M + current YTD $90.5M = **TTM $220.3M**
- SBC: FY $90.2M − prior YTD $40.8M + current YTD $48.8M = **TTM $98.2M**
- Shares (current-YTD weighted diluted): **194,300,000**
- **TTM OE total $1,424.8M → base OE/share $7.33** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $5.86/share. The TTM base is used because the FY ended 9.5 months ago and the TTM legs are all filed; the median is retained in the reporting. Method range note: on the median base the preliminary run printed weighted IRR 11.4% / IV@15% $65.96 — also Tier C, so the tier does not rest on the TTM choice.

## Moat: 5/10 — moderate/narrow
Justification: #1/#2 positions in knees and hips with durable ~70% gross margins, but the measured ROIC history does not support more. fundamentals.json roic_proxy (after-tax operating income over equity + debt − cash) ran 0.14%–4.5% over FY2018–22, recovering to 6.88% (FY2023), 6.19% (FY2024), 4.75% (FY2025) — persistently below a normal cost of capital, because the balance sheet carries ~$10.6B goodwill plus ~$8.8B intangibles from the Biomet merger. Gross margin held 68.9%–72.7% across FY2016–25 (69.7% in FY2025) — stable, not expanding.
- FOR: leading share in large-joint reconstruction (knees, hips); surgeon training and hospital/GPO relationships create real switching friction; installed implant base plus the ROSA robotics ecosystem (ROSA Shoulder cleared 2026; TMINI distribution extended Oct 2026) ties procedures to the platform; pricing has held gross margin near 70% for a decade.
- AGAINST: ROIC proxy below the cost of capital through the whole measured cycle — the franchise earns its margin on an acquisition-inflated capital base; annual pricing erosion of up to ~100bps guided by management itself; knees nearly flat (+0.4% in Q2 2026) against Stryker and DePuy Synthes robotics competition; adjusted gross margin fell 120bps and adjusted operating margin 210bps YoY in Q2 2026 on acquisition mix (Paragon 28, Monogram); China/international volatility and go-to-market disruption risk.
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — engine 5.4 final run (2026-10-16)
Growth sanity check (mandatory): the engine's blended start is 8.51%, built from rev CAGR 5y 6.08% / 3y 5.85%, latest YoY 7.20%, OE/share CAGR 2y 10.68%, plus a +1.87pp share-count adjustment on the revenue legs. The actual prints are slower: Q2 2026 revenue +4.8% reported / +4.0% organic constant currency; FY2026 guidance is reported growth 3.9–4.9%, organic constant currency 2.25–3.25%, adjusted EPS $8.47–8.59. The blend's OE/share CAGR leg is a recovery artifact (margin normalization off depressed FY2024–25 plus buybacks), not a revenue trajectory. Scenario starts were therefore recalibrated down 2.5pp via offsets (−0.145 / −0.075 / −0.025 / +0.025 / +0.095) to −6.0 / +1.0 / **+6.0** / +11.0 / +18.0%: the 6.0% base start = guided reported revenue growth (~4–5%) plus the ~2%/yr buyback tailwind on a per-share basis. Probabilities 10/25/30/25/10; OE multipliers 0.75/0.90/1.00/1.10/1.25. Price $94.98.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | −6.0% | 0.75 | Pricing erosion compounds, China/GMT disruption, leverage bites | $31.62 | 6.33% |
| Bear | 25% | +1.0% | 0.90 | Organic growth at the low guide, knees stay flat, margins slip | $50.87 | 9.14% |
| Base | 30% | +6.0% | 1.00 | Guided reported growth + buyback tailwind, normal fade | $69.58 | 11.75% |
| Bull | 25% | +11.0% | 1.10 | ROSA/robotics + Paragon 28/Monogram drive share and margin recovery | $94.07 | 14.89% |
| Super bull | 10% | +18.0% | 1.25 | Robotics-led re-acceleration sustained | $142.20 | 20.20% |

- **Probability-weighted: IV@15% $74.49 (−21.6% vs price), IV@12% $99.49 (+4.8%), IV@10% $127.44, weighted IRR 12.43%, base-case IRR 11.75%**
- **Tier by numbers: C.** Diagnostics (dcf_numbers.json): OE yield 7.72%, terminal value 19.3% of IV@15%, scenario spread 4.50x, net debt 4.75x normalized OE (TTM base), 9.5 months since FY end.
- **Hurdle-clearing price: $74.49 at 15%** ($52.11 at 20%, $39.84 at 25%) vs $94.98 paid today.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.5 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, legs quoted above.
- **WIDE_SCENARIO_SPREAD** (super-bull IV 4.5x super-bear): real — outcomes hinge on whether robotics/M&A re-accelerate a business currently growing organically at 2–3%. Confidence capped at medium; verdict sized to the conservative end.
- **HIGH_NET_DEBT** (net debt 4.8x normalized OE on the final run; 6.0x on the preliminary median-base run): balance sheet per the filing history — total debt $7,519.1M vs cash $591.9M at FY2025 year-end, plus $233.0M lease liabilities. This is legacy Biomet-merger debt, serviced comfortably by ~$1.7B OCF, but it means equity OE is levered: the bear cases carry the 0.75/0.90 multipliers and the super-bear start is −6%.
- **TIER_BAND** (bear tier D 9.1% vs bull tier C 14.9%): the verdict spans D–C; even the bull case does not clear 15%. Sized to the bear end — no position case at this price.

## My thoughts / overlay
- The honest headline is the range: median-base run 11.4% weighted IRR, TTM-base run 12.4% — Tier C either way. The method choice moves the IV@15% ($65.96 vs $74.49) but not the verdict.
- Quality is mid-tier medtech, not a compounder: ~70% gross margins and 5/5 positive OE years, but ROIC proxy has never cleared a normal cost of capital on the post-Biomet capital base, and growth is bought (Paragon 28, Monogram) as much as earned — Q2 2026 organic growth was 4.0% with adjusted margins down year over year.
- What would change the answer: the price, mainly — at ~$74 the weighted case clears 15%; or two more quarters of organic growth above guide with adjusted operating margin recovering, which would justify lifting the base start instead of recalibrating it down.
- Q3 2026 results land November 4, 2026 — the next check on the guidance story.

## Final verdict
- **Final tier: C** (weighted IRR 12.43%; bear D 9.1% → bull C 14.9%)
- Confidence: **Medium** (WIDE_SCENARIO_SPREAD caps it; TTM base and flag set are clean, growth path is the uncertainty)
- One-liner: Solid orthopedics franchise, moat 5/10 — at $94.98 it does not clear 15% (weighted IRR 12.4%, IV@15% $74.49); it clears the hurdle at ~$74.
