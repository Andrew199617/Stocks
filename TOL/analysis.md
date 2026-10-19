# TOL — Toll Brothers, Inc.
Engine 5.4.0 run, 2026-10-18. Price $133.70 (nasdaq_quote_api), market cap (est) $13.340B — in scope under $40B.

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.json, or fundamentals.json — none are recomputed.

## What it is
The largest US luxury homebuilder: build-to-order and spec homes at an average delivered price of ~$996,000 (Q3 FY2026), plus land sales, joint ventures and ancillary services. Fiscal year ends October 31. Q3 FY2026 (ended 2026-07-31): 2,662 deliveries, home sales revenue $2.65B, net income $280.1M / $2.97 diluted EPS, net signed contracts +5% in units YoY, 471 selling communities, FY2026 guidance 10,500–10,600 deliveries and ~$10.5B home sales revenue (company Q3 release, via search results).

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $1,112,411,000; capex $86,195,000; SBC $30,834,000 (always a real cost).
- **Conservative owner's earnings FY2025: $995,382,000 = $9.98/share** (key_numbers.md: latest FY OE/share $9.98; latest FY OE total $995.4M)
- Maintenance version FY2025: $1,346,486,000 — materially above the conservative figure. For a homebuilder the gap is working capital: inventory (homes under construction and land development) sits in operating cash flow, so the conservative OCF-based figure charges a build year in full while the maintenance version follows net income. Neither is clean alone; the truth for a still-growing builder is between them, closer to the conservative figure while community count is expanding.
- OE positive 5 of the last 5 fiscal years. OE/share history is cyclical and WC-driven: FY2021 $9.64, FY2022 $7.58, FY2023 $10.53, FY2024 $8.66, FY2025 $9.98 (financials_history.csv).

**Base used = TTM owner's earnings through Q3 FY2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $1,112,411,000 − prior YTD $312,381,000 + current YTD $392,060,000 = **TTM $1,192,090,000**
- Capex: FY $86,195,000 − prior YTD $58,363,000 + current YTD $74,031,000 = **TTM $101,863,000**
- SBC: FY $30,834,000 − prior YTD $27,110,000 + current YTD $27,704,000 = **TTM $31,428,000**
- Shares (current-YTD weighted diluted): **95,568,000**
- **TTM OE total $1,058,799,000 → base OE/share $11.08** (base_source: ttm_json)
- The normalized base (3-yr median) is $9.98/share — identical to the latest FY figure, so there is no BASE_DIVERGENCE dispute: the TTM base is $11.08 only because buybacks cut the share count and TTM OCF held up, not because one year is an outlier. Using the median instead would lower every IV proportionally; the method range is noted under Thoughts.

## Moat: 5/10 — moderate / narrow
Justification: Luxury brand, affluent less rate-sensitive buyers, land optioning and design-studio pricing power have held ROIC proxy at 19.4–25.6% in FY2021–25, but homebuilding is cyclical, land and construction are contestable inputs, gross margin has faded, and pre-2021 ROIC proxy ran only ~11–13% — a moderate/narrow moat, not a wide one.
- Evidence (fundamentals.json, filing-direct): ROIC proxy FY2021 22.1%, FY2022 25.6%, FY2023 24.8%, FY2024 25.3%, FY2025 19.4% — well above cost of capital for five years, but FY2016–20 ran ~10.8–13.4%, so through a full cycle the franchise earns mid-teens, not wide-moat returns. Gross margin: FY2023 26.4%, FY2024 27.9%, FY2025 25.1% — high for a builder, and falling.
- FOR: Luxury brand and affluent, less mortgage-rate-sensitive buyer base — industry-low 2.6% cancellation rate in Q3 FY2026; pricing power — average delivered price ~$996,000 in Q3 FY2026, above the guidance high end, on mix and personalization; land discipline — ~75,500 owned or controlled lots, ~58% optioned, a capital-light pipeline supporting 8–10%/yr community growth; returns — ROIC proxy 19.4–25.6% across FY2021–25 and gross margin 25.1–27.9% in FY2024–25.
- AGAINST: Pure cyclicality — housing demand is hostage to mortgage rates and consumer confidence; Q3 FY2026 deliveries fell 10% and revenue 9.7% YoY; margin erosion already visible — gross margin 27.9% (FY2024) to 25.1% (FY2025), Q3 FY2026 adjusted gross margin 25.6% vs 27.5% a year earlier, SG&A deleveraging; land, labor and lots are bought in contestable markets — no owned scarce input or switching cost, and D.R. Horton, PulteGroup and local luxury builders contest every community; through-cycle returns are mid-teens, not wide-moat — ROIC proxy was only ~11–13% in FY2016–20.
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — engine 5.4.0 final run (2026-10-18)
Growth sanity check (mandatory): the engine blend is 6.65% (rev CAGR 5y 9.15%, rev CAGR 3y 2.19%, latest rev YoY 1.11%, OE/share CAGR 2y −2.65%, share count CAGR −5.43% with a 5.00% adjustment credited to the revenue components only). Recent prints are soft in total terms — Q3 FY2026 revenue −9.7% YoY, TTM revenue in fundamentals.json −1.08% YoY, FY2026 guided home sales revenue ~$10.5B vs FY2025 total revenue $10,966,723,000 — but the scenario starts are **per-share** OE growth, and ~5pp of the base start is the buyback tailwind (share count shrinking 5.4%/yr; FY2026 buybacks raised to $700M per the Q3 release), leaving underlying total-OE growth of only ~1–2% in the base case, consistent with flat revenue and community growth offsetting margin pressure. The bull start of 11.7% per share is ~6–7% total growth — a rate-cut/volume recovery off 471 communities growing 8–10%/yr, not a return to FY2021–22 prints. Super-bull 18.6% per share requires a full housing upcycle and is weighted only 10%. Default offsets (−12/−5/0/+5/+12pp) and multipliers (0.75/0.90/1.00/1.10/1.25) kept; probabilities 10/25/30/25/10 kept — the soft near term is already in the per-share arithmetic above. Price $133.70.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -5.3% | 0.75 | Housing downturn: volumes and luxury pricing break, buybacks cannot offset | $49.06 | 6.77% |
| Bear | 25% | 1.7% | 0.9 | Rates stay high; margin stays compressed; per-share growth is buybacks only | $78.92 | 9.85% |
| Base | 30% | 6.7% | 1.0 | Flat revenue, community growth + buybacks carry per-share OE | $107.93 | 12.68% |
| Bull | 25% | 11.7% | 1.1 | Rate relief revives volumes; margin stabilizes at ~26% adjusted | $145.88 | 16.04% |
| Super bull | 10% | 18.6% | 1.25 | Full upcycle: volume + pricing + margin recovery together | $220.43 | 21.68% |

- **Probability-weighted: IV@15% $115.53 (−13.6% vs price), IV@12% $154.54 (+15.6%), IV@10% $198.18, weighted IRR 13.39%, base-case IRR 12.68%**
- **Tier by numbers: C.** IRR band: bear 9.85% (tier D) → bull 16.04% (tier B); scenario range 6.77% – 21.68%. Hurdle-clearing prices (weighted path): 15% at $115.53 · 20% at $80.63 · 25% at $61.54.
- Diagnostics (key_numbers.md): OE yield 8.29%, terminal value 19.4% of IV@15%, scenario spread 4.49x, months since FY end 11.6. Net debt / normalized OE is not printed — see DEBT_TAGS_BLANK below.

## Flags — every fragility flag resolved
- **STALE_FY** (latest fiscal year ended 12 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q3 FY2026 (2026-07-31), legs quoted above. TTM OE/share $11.08 vs FY2025 $9.98.
- **BUYBACK_TAILWIND** (share count shrinking 5.4%/yr): already credited via the 5.00% growth adjustment in the blend; not double-counted in the verdict. It is also load-bearing — strip it out and the base growth start is ~1.7%, i.e. the bear case; see TIER_BAND.
- **NI_OCF_DIVERGENCE** (2024): FY2024 net income $1,571,195,000 vs operating cash flow $1,010,167,000 (financials_history.csv). This is the homebuilder working-capital swing, not an earnings-quality one-off: cash went into inventory — homes under construction and land development for a growing community/lot base — which OCF charges immediately while net income recognizes it only on delivery. The maintenance OE for FY2024 ($1,578,753,000) tracks net income, confirming the earnings were real but not yet cash-converted. Consequence: single-year conservative OE understates Toll in build years and overstates it in harvest years, which is why the verdict leans on the TTM/median pair ($11.08 / $9.98) rather than any one year.
- **DEBT_TAGS_BLANK** (no debt tag reports for the latest fiscal year): the engine prints **no** net debt figure — net debt is unknown from the engine, not zero, and no leverage verdict is taken from dcf_numbers.json. Balance sheet from the filings as reported for Q3 FY2026 (company release, via search results): cash $1.06B, total liquidity $3.3B including available credit of $2.24B, net debt-to-capital 15.6%, debt-to-capital 24.5%. Filing-direct totals in financials_history.csv for FY2025: assets $14,519,866,000, liabilities $6,233,802,000, equity $8,270,663,000, cash $1,258,997,000. Verdict on leverage, stated in words only: modest for a homebuilder — the balance sheet is a buffer, not a risk driver, in this score.
- **WIDE_SCENARIO_SPREAD** (super-bull IV 4.5x super-bear IV): real — a luxury builder's outcome range across a housing cycle IS this wide. Confidence is capped at medium, and the verdict is sized to the conservative end.
- **TIER_BAND** (bear-case tier D 9.85% vs bull-case tier B 16.04%): the verdict spans tiers; any position sizing should use the bear end (Tier D, IV@15% $78.92), not the weighted C.

## My thoughts / overlay
- The honest headline is the method range: on the TTM base ($11.08) the weighted result is Tier C at 13.39%; on the normalized median base ($9.98) every IV scales down by roughly a tenth and the name sits deeper in C. No defensible base choice gets this price to 15% — the bull case alone clears it, at 16.04%.
- Quality is real but priced: OE yield 8.29% on the TTM base, five straight OE-positive years, buybacks plus a dividend (fundamentals.json: buybacks TTM $681,641,000; DPS TTM $1.02 declared) — against a stock at $133.70 that already capitalizes a housing recovery that Q3 FY2026 prints (deliveries −10%, EPS $2.97 vs $3.73 a year earlier) have not yet delivered.
- The swing factors are all macro: mortgage rates, luxury-buyer confidence, and whether adjusted gross margin holds the guided ~26% or keeps sliding from 27.5%. Toll's own levers — community count +8–10%, optioned-lot mix, buybacks — cushion the per-share line but cannot create demand.
- Margin of safety: there is none against the weighted case at this price (IV@15% $115.53 is 13.6% below $133.70); a buyer at $133.70 is paid only if the bull case happens. The 15% hurdle clears below $115.53 on the weighted path.

## Final verdict
- **Final tier: C** (weighted IRR 13.39% on the TTM base; bear D → bull B)
- Confidence: **Medium** (high on the filing-direct OE history and TTM legs; the spread is 4.49x and the growth start leans on a continuing buyback, so not high)
- One-liner: Quality luxury builder, moat 5/10 — does not clear 15% at $133.70 on TTM owner's earnings (13.4% weighted IRR, IV@15% $115.53); it clears 15% only below ~$115.53, and the bear case is Tier D, so size to the bear end.
