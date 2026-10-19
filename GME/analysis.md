# GME — GameStop Corp.
Engine 5.4.0 run, 2026-10-17. Price $26.81 (nasdaq_quote_api), market cap (est) $14.721B — in scope under $40B.

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.json, fundamentals.json or financials_history.csv — none are recomputed.

## What it is
Specialty retailer of video games, hardware and — increasingly — collectibles/trading cards, through a shrinking physical fleet (global stores cut from 3,203 to 2,206 in the fiscal year ended 2026-01-31, per the 10-K review) plus e-commerce. The historic core (physical software/hardware) is in structural decline as platform owners sell digitally direct; the P&L is being rebuilt on collectibles (45.1% of Q2 (ended 2026-08-01) sales, +57% YoY per the Q2 report), cost cuts, and returns on a very large cash/investment pile raised from shareholders and convertible-note buyers.

## Owner's earnings
**Fiscal year ended 2026-01-31 (10-K via EDGAR, from financials_history.csv):** operating cash flow $614,800,000; capex $17,500,000; SBC $26,700,000.
- **Conservative owner's earnings (OCF − capex − SBC): $570,600,000 = $1.04/share** (key_numbers.md: latest FY OE/share $1.04, latest FY OE total $570.6M, on 549,100,000 diluted shares).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): **−$2,699,400,000 for the same year — unusable.** The ΔNWC leg in financials_history.csv is $3,119,700,000, a balance-sheet artifact of the treasury operation (multi-billion cash raise and convertible notes moving through current assets/liabilities), not store working capital. The OCF-based conservative series is the one used throughout.
- OE-positive years (last 5): 3/5 (key_numbers.md). Net debt (latest): **−$2.140B — i.e. net cash** (cash $6,304,700,000 less debt total $4,164,300,000 at FY end, financials_history.csv); lease liabilities $197,600,000 (dcf_numbers.json).

**Base used = TTM owner's earnings through Q2 (period ended 2026-08-01), from ttm.py (filing-direct, no hand math):**
- OCF: FY $614,800,000 − prior YTD $309,900,000 + current YTD $399,800,000 = **TTM $704,700,000**
- Capex: FY $17,500,000 − prior YTD $7,000,000 + current YTD $6,200,000 = **TTM $16,700,000**
- SBC: FY $26,700,000 − prior YTD $11,800,000 + current YTD $15,800,000 = **TTM $30,700,000**
- Shares (current-YTD weighted diluted): **592,500,000**
- **TTM OE total $657,300,000 → base OE/share $1.11** (key_numbers.md; base_source: ttm_json)
- The engine's normalized base (3-yr median) is $0.29/share — rejected as the base: its window contains the trough year ended 2024-02-03 (OE/share −$0.85) from before the cost cuts and the collectibles mix shift. Latest FY ($1.04) and TTM ($1.11) corroborate each other, so the current run-rate is the TTM figure. This choice is **generous** to the stock — see Thoughts for the interest-income double-count it embeds — and the verdict is still D.

## Moat: 2/10 — essentially none
Justification: narrow collectibles distribution and brand/community advantages, but no pricing power in its historic core — platform owners control digital game distribution — and the measured record shows no franchise economics: the `roic_proxy` series in fundamentals.json (after-tax operating income over equity + debt − cash) was **−64.58% (ended 2021-01-30), −77.49% (2022-01-29), −110.49% (2023-01-28), −3.96% (2024-02-03), −13.21% (2025-02-01)** and only turned positive at **+5.55% (2026-01-31)** — below any plausible cost of capital through the whole cycle. Gross margin does show the mix shift working: 24.5% → 29.1% → 33.0% over the last three fiscal years, 37.9% TTM (fundamentals.json) — that is a product-mix improvement in a shrinking store base, not pricing power, and a 2/10 carries no requirement to explain it away.
- FOR: largest specialty footprint for collectibles/trading cards with a PSA grading partnership — collectibles 45.1% of Q2 (ended 2026-08-01) sales, +57% YoY; recognized brand, loyal community and a trade-in/pre-owned network physical rivals cannot easily replicate; fortress liquidity (cash $6,304,700,000 at FY end) funds the pivot and removes distress risk.
- AGAINST: platform owners (Steam, PlayStation, Xbox, Nintendo) control digital distribution — no pricing power in hardware/software, the historic core; ROIC negative five straight years before +5.55% in the latest FY; revenue structurally shrinking (5-yr CAGR −6.53%, 3-yr −15.04%, TTM revenue −7.7% YoY per fundamentals.json); collectibles concentration/fad risk — one category now carries the margin story; supplier-allocation dependence for cards and hardware, no owned product or platform.
- A 2 gives CAP = 4.6 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 4.6 years, 15-year projection.

## DCF — engine 5.4.0 final run (2026-10-17)
**Growth sanity check (mandatory):** the engine's blend is revenue-driven (−11.53% → g_base −5.00%; components: rev CAGR 5y −6.53%, 3y −15.04%, latest rev YoY −5.05%). OE prints are better than revenue prints because margins are expanding: TTM OE total grew +43.0% YoY (fundamentals.json TTM) and TTM OE/share $1.11 vs latest FY $1.04, while TTM revenue fell −7.7% YoY and Q2 revenue fell −18.7% YoY against the Nintendo Switch 2 launch comparison. Scenario starts were therefore set via offsets (−0.05 / 0.00 / +0.05 / +0.10 / +0.17 vs g_base) to **−10 / −5 / 0 / +5 / +12%**: the base start (0%) sits above the revenue trend because the collectibles mix and closure savings are still annualizing, but below the latest OE/share momentum because those are level shifts that anniversary, revenue is still falling, and the diluted count keeps rising. Probabilities were widened to the bear side (15/30/30/15/10 vs the 10/25/30/25/10 default) per the OE_VOLATILE flag. OE multipliers are the defaults 0.75/0.90/1.00/1.10/1.25. Price $26.81.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | −10.0% | 0.75 | Collectibles fad cools, revenue decline re-accelerates, margin gains give back | $4.55 | 4.48% |
| Bear | 30% | −5.0% | 0.90 | Revenue keeps shrinking at the recent pace; mix gains plateau | $6.44 | 5.40% |
| Base | 30% | 0.0% | 1.00 | OE/share flat near term as mix gains offset revenue decline, then fades to terminal | $8.41 | 6.38% |
| Bull | 15% | 5.0% | 1.10 | Collectibles keep compounding, fleet stabilizes, margins hold | $10.81 | 7.58% |
| Super bull | 10% | 12.0% | 1.25 | Collectibles become a durable growth category and OE/share compounds double-digit | $15.19 | 9.72% |

- **Probability-weighted: IV@15% $8.28 (−69.1% vs price), IV@12% $10.87, IV@10% $13.75, weighted IRR 6.34%, base-case IRR 6.38%**
- **Tier by numbers: D.** Bear→bull band is D→D (bear IRR 5.40%, bull 7.58%); even the super-bull IV@15 ($15.19) sits below the $26.81 price. Diagnostics (key_numbers.md): OE yield 4.14%, terminal value 17.6% of IV@15%, scenario spread 3.34x, net debt −3.51x normalized OE, 8.5 months since FY end.
- **Hurdle-clearing prices (weighted path): 15% at $8.28 · 20% at $5.93 · 25% at $4.63.**

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 8.5 months ago): resolved by construction — the base is the TTM figure from ttm.py through 2026-08-01, legs quoted above.
- **DILUTION** (share count CAGR 21.69%): this is financing issuance, not SBC — SBC is small ($16,400,000 in FY2025 → $26,700,000 latest FY → $30,700,000 TTM, financials_history.csv/ttm.json). The count ballooned on at-the-market equity raises and convertible notes: diluted shares 305,200,000 (year ended 2024-02-03) → 394,700,000 → 549,100,000 → 592,500,000 TTM YTD. The engine already deducted the maximum −5.00% growth adjustment (key_numbers.md). Post-TTM, the September 2026 exchange of $1.4B of convertible notes for ~55.5M shares plus $358.4M cash (reported at the time) converts dilution already inside the diluted count into basic shares — it does not create a new per-share claim beyond it.
- **OE_VOLATILE** (OE/share spans >3x over 5 years): real — the filed series runs −$1.81, $0.04, −$0.85, $0.29, $1.04 (financials_history.csv). Handled with bear-heavy probabilities (45% on bear-or-worse) and by requiring two corroborating periods (latest FY + TTM) before trusting the $1.11 base.
- **NI_OCF_DIVERGENCE** (2024): in the year ended 2024-02-03 net income was $6,700,000 while operating cash flow was −$203,700,000 (financials_history.csv) — a working-capital outflow year in a shrinking fleet (the history's ΔNWC leg for that year is $272,400,000). The base series is OCF-based, so the divergence does not flatter the base; that year's conservative OE was −$260,800,000.
- **BASE_DIVERGENCE** (latest FY $1.04 vs 3-yr median $0.29): the median is the distorted one — its window holds the trough year (−$0.85) from before the closures and collectibles mix shift. Latest FY and TTM agree ($1.04 / $1.11), so TTM is the base; the median is retained here and in key_numbers.md, and the preliminary run on the median base is in the method range below.
- **BIG_NET_CASH** (net cash 3.5x normalized OE): stated from the filing — at FY end cash was $6,304,700,000 against debt total $4,164,300,000, i.e. net cash $2,140,400,000 (net debt −$2.140B, key_numbers.md), plus lease liabilities $197,600,000. A real part of the $26.81 price is this pile, not the operating business — the verdict below keeps the two separate. Note the engine's balance sheet is the FY-end one: it does not carry the digital assets (4,710 BTC acquired in 2025) as cash, and it predates the 2026 deployment of cash into a ~43.4M-share eBay stake (reported at ~$4.9B alongside $5.4B of cash, securities and digital assets at Q2) — that asset transformation is a sum-of-the-parts question for pass 2, not an owner's-earnings input.

## My thoughts / overlay
- **Method range:** the preliminary run on the engine's median base ($0.29/share, default probabilities) printed weighted IRR 3.31% and IV@15% $1.87. The final run — TTM base, growth starts lifted to the OE evidence, bear-heavy weights — prints 6.34% and $8.28. The honest headline is the range: **every defensible owner's-earnings method lands in Tier D, at one-third or less of the price.** Even the super-bull scenario (12% growth start, 1.25x OE) yields 9.72%.
- **The TTM base is generous in a specific way:** TTM net income is $893,300,000 (fundamentals.json) against OCF of $704,700,000 — recent earnings include large non-operating investment gains (the eBay stake boosted Q2 net income to $298,700,000), and the OCF-based OE itself capitalizes interest earned on the cash pile while the DCF separately adds net cash back. Both effects flatter IV@15; the verdict survives them, which is the point of using the generous base.
- **What the price actually is:** at $26.81 the market is paying for the financial-asset pile (cash, BTC, the eBay stake), the collectibles option, insider buying by the CEO, and meme/ scarcity dynamics — none of which an owner's-earnings DCF prices. External sum-of-the-parts work cited in research still landed below the price (one published SOTP put fair value at $23.02/share). Street consensus in street.json is Strong Buy on n=2 with a $32.00 target — two analysts is not a consensus, it is a coin flip with a label.
- Quality is genuinely improving — record Q2 operating income of $160,200,000 (fundamentals.json quarterly), gross margin 43.66% in Q2 — but improvement from a negative-ROIC base to a 4.14% OE yield at this price is a turnaround story, not a 15%-hurdle investment.

## Final verdict
- **Final tier: D** (weighted IRR 6.34% on the generous TTM base; D on every scenario and on the median-base method too)
- Confidence: **Medium** (high on the filing arithmetic and on the direction — no plausible OE path reaches $26.81; medium on the exact IV, because the post-FY-end balance-sheet transformation into investment assets sits outside this model)
- One-liner: Improving but moatless retailer, moat 2/10 — even on the generous TTM base it does not clear 15% (weighted IRR 6.34%, IV@15% $8.28 vs $26.81 price; clears 15% only below $8.28); the price is a cash/investment-asset and meme story, not owner's earnings.

## Data / enrichment
fundamentals.py, prices.py, segments.py, statements.py, profile.py and reprice.py all ran clean (reprice: live price $26.81, tier D unchanged). statements.json carries filer's-custom-tag warnings for the FY2026 income statement — the standardized lines explain part of the revenue-to-operating-income bridge; no enrichment failure affects the score.
