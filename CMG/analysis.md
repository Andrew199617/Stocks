# CMG — Chipotle Mexican Grill, Inc.
v5 run, 2026-10-14 (supersedes the 2026-10-12 sweep run). Price $30.35 (nasdaq_quote_api); engine market-cap estimate $40.748B — just over the sweep's $40B scope line (it entered the universe under $40B; the estimate is copied from dcf_numbers.json, and judgment.json records in_scope_under_40b = false on the current estimate).

All figures below are copied from dcf_numbers.json, ttm.py output (ttm.json), or financials_history.csv — none are recomputed.

## What it is
The dominant US fast-casual restaurant chain: ~4,200 mostly company-owned restaurants (no franchising in North America), ~350–370 openings planned for 2026 with ~80% including a Chipotlane drive-thru pickup lane. Digital sales were 38.3% of Q2 2026 revenue; international growth is partner-operated (first Mexico location opened July 2026, first Seoul location September 2026). CEO Scott Boatwright is running a "Recipe for Growth" program (menu innovation/LTOs, revamped Rewards loyalty, high-efficiency kitchen equipment in 1,000+ restaurants) to rebuild traffic after a weak 2025.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** revenue $11,925,601,000; net income $1,535,761,000; operating cash flow $2,113,926,000; capex $666,336,000 (tag: PaymentsToAcquirePropertyPlantAndEquipment); SBC $119,543,000 (tag: ShareBasedCompensation — always a real cost; it is small here, ~1% of revenue, because restaurant staff are paid in cash wages).
- **Conservative owner's earnings FY2025: $1,328,047,000 = $0.989/share** (this is also the engine's 3-yr median normalized base, $0.9891487960816794).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $1,470,777,000 — above the conservative figure because most capex is growth capex for ~350 new stores a year, not maintenance. The conservative definition is the base case; the gap between the two is the honest range on how much of the $666M capex is truly maintenance.
- OE positive 5 of the last 5 fiscal years. Balance sheet: net debt −$350,545,000, i.e. a net cash position (cash $350,545,000, no debt tagged) — diagnostics put net debt at −0.23x normalized OE. Buybacks are aggressive: $630.7M repurchased in Q2 2026 alone and $1.7B of authorization remained at June 30, 2026 (Q2 2026 earnings release); diluted shares fell from 1,355,478,000 (H1 2025 YTD) to 1,290,462,000 (H1 2026 YTD) in the ttm.py inputs.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $2,113,926,000 − prior YTD $1,118,402,000 + current YTD $1,332,003,000 = **TTM $2,327,527,000**
- Capex: FY $666,336,000 − prior YTD $305,395,000 + current YTD $397,601,000 = **TTM $758,542,000**
- SBC: FY $119,543,000 − prior YTD $75,150,000 + current YTD $54,518,000 = **TTM $98,911,000**
- Shares (current-YTD weighted diluted): **1,290,462,000**
- **TTM OE total $1,470,074,000 → base OE/share $1.1392** (base_source: ttm_json)
- The TTM base sits above the $0.989 median because H1 2026 OCF recovered and the buyback shrank the share count; it is the fresher, less distorted base, so it is the one used.

## Moat: 6/10 — moderate-strong brand moat, no structural lock-in
Justification: best-in-class unit economics and proven pricing power, but no switching costs or network effects and a demonstrated food-safety/traffic tail risk.
- FOR: brand and pricing power proven over two decades of through-cycle compounding; best-in-class unit economics (average unit volumes ~$3.1M, ~60% second-year cash-on-cash returns, ~2-year payback on new stores — Morningstar via search); digital + loyalty scale (38.3% of sales digital in Q2 2026, ~21M active Rewards members); Chipotlane format advantage — ~80% of new stores, higher volumes and margins than traditional stores; company-owned model gives full control of food quality and throughput with no franchisee friction.
- AGAINST: no switching costs or network effects — a burrito is a choice made fresh every lunch; fast-casual and QSR competition is intense (CAVA, Sweetgreen, value wars at the big chains); food-safety tail risk is real (2015 E. coli precedent; the industry-wide Cyclospora scare in summer 2026 cost ~200bp of Q3 comp traffic even though Chipotle's supply chain was not implicated); value-perception ceiling — 2025 comparable sales fell 1.7% with transactions down 3.2% as checks pushed past what guests would pay; wage and beef inflation with deliberately limited pricing (2026 pricing guided ~1–2%) squeezes margins; the path from ~4,200 to 7,000 North American stores at historical returns is unproven.
- A 6 gives CAP = 9.8 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 9.8 years, 15-year projection.

## DCF — v5 final run (2026-10-14)
Engine blended growth 11.52% (components: revenue CAGR 5y 14.79%, 3y 11.36%, latest FY revenue YoY 5.41%, OE/share CAGR 2y 11.67%), adjusted +1.46pp for the buyback share-count trend → g_base 12.98%. Sanity check against actual prints: Q2 2026 revenue grew 9.3% YoY (comps +2.2%, transactions +1.0%) and TTM OE/share of $1.1392 vs FY2025's $0.989 is a mid-teens per-share growth print, powered by unit growth plus buybacks — the 13.0% base start is in line with what the company is actually printing per share, and the 25.0% super-bull start is below the OE/share growth Chipotle printed in its 2023–24 recovery years, so no recalibration was needed. Default offsets and multipliers kept; probabilities kept at the 10/25/30/25/10 defaults — the recovery evidence (two consecutive quarters of improving transaction comps, FY2026 comp guidance raised to low single digits) is balanced by real margin compression (Q2 2026 restaurant-level margin 25.2% vs 27.4% a year earlier; operating margin 15.7% vs 18.2%).

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | 1.0% | 0.75 | Traffic relapse + food-safety event; margins stay squeezed | $6.55 | 5.14% |
| Bear | 25% | 8.0% | 0.90 | Unit growth carries revenue; comps flat, no margin recovery | $10.73 | 7.15% |
| Base | 30% | 13.0% | 1.00 | Low-single-digit comps + ~9% units + buybacks, gradual margin repair | $14.88 | 9.05% |
| Bull | 25% | 18.0% | 1.10 | Traffic recovery sticks; margins rebuild toward prior peaks | $20.41 | 11.38% |
| Super bull | 10% | 25.0% | 1.25 | Full recovery + international optionality + sustained buyback compounding | $31.52 | 15.38% |

- **Probability-weighted: IV@15% $16.06 (−47.1% vs the $30.35 price), IV@12% $21.94, IV@10% $28.59, weighted IRR 9.61%, base-case IRR 9.05%**
- **Tier by numbers: D.** Diagnostics (dcf_numbers.json): OE yield 3.75%, terminal value 21.7% of IV@15%, scenario spread 4.81x, net debt −0.23x normalized OE, 9.4 months since FY end.
- Even the super-bull scenario (10% weight) only reaches a 15.38% IRR at this price — the entire distribution sits below Andrew's 15% hurdle except the extreme tail.

## Flags — every fragility flag resolved
- **STALE_FY** (FY2025 ended 9.4 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, inputs quoted above.
- **OE_VOLATILE** (OE/share range over 5 years spans >3x): mostly an artifact plus genuine growth, not cyclicality. EDGAR share counts for FY2016–21 are pre-split (~28.5M shares) and FY2022 onward are post-split (~1.3–1.4B) around the June 2024 50-for-1 split, so per-share figures straddle a 50x share-count break. On totals, conservative OE compounded steadily ($663,214,000 FY2021 → $745,985,000 FY2022 → $1,098,730,000 FY2023 → $1,379,743,000 FY2024 → $1,328,047,000 FY2025); the only down year is FY2025, the traffic-slump year. No extra bear widening beyond the default 35% bear-or-worse weight was added — the flag's stated concern (cyclical business) does not match this record.
- **WIDE_SCENARIO_SPREAD** (super-bull IV 4.81x super-bear IV): real — the outcome genuinely hinges on whether margins recover. Confidence is capped at medium, and the verdict is sized to the conservative end.

## Thoughts / overlay
This is a quality-vs-price problem, not a business-quality problem. The market price of $30.35 capitalizes a recovery that has only just started printing: transactions turned positive in Q1–Q2 2026 and guidance was raised, but restaurant-level margins are still ~220bp below a year ago and EPS was flat YoY in Q2 2026. The standardized model says the weighted IV@15% is $16.06 — the price that clears the 15% hurdle on these inputs; a margin of safety means paying meaningfully less than that. Method range: the verdict is not assumption-fragile the way inflection names are — no defensible input set tried here gets the weighted IRR to 15% at $30.35, because even the super-bull path barely clears it. The October 2026 report that Starbucks explored acquiring Chipotle is unconfirmed speculation (no agreement announced) and is not part of this valuation. Q3 2026 earnings (expected late October 2026) are the next check on whether the traffic recovery survives the Cyclospora drag.

## Verdict
**Tier D — weighted IRR 9.61% at $30.35.** An excellent operator with a moderate-strong moat (6/10) and a net-cash balance sheet, priced for a full recovery that hasn't happened yet. It clears Andrew's 15% hurdle only at roughly $16 or below on the weighted path. Not a buy at this price; a watchlist name for a deep drawdown.
