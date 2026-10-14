# DHI — D.R. Horton, Inc.
v5 run, 2026-10-14 (supersedes the v4 analysis of 2026-10-13; verdict unchanged). Scope note: the universe entry was $37.7B at build time, but the engine's current market-cap estimate is $41.976B (key_numbers.md), computed on the latest fiscal-year diluted share count of 309,900,000 — so `in_scope_under_40b` is false in this run's score.json, even though the TTM diluted share count in ttm.json is down to 288,400,000. The analysis proceeds because the name was claimed from the queue; the scope flag is recorded honestly rather than adjusted.

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.json, or financials_history.csv — none are recomputed.

## What it is
The largest U.S. homebuilder by volume every year since 2002 — roughly 15% of new U.S. homes. Homebuilding is the core (brands: D.R. Horton, Express, Emerald, Freedom; average closing price $362,000 in Q3 FY2026 — an explicit affordability/first-time-buyer focus), plus a Rental segment (single- and multi-family built to sell to investors), Forestar (majority-owned lot development), and Financial Services (mortgage/title). Q3 FY2026 (ended 2026-06-30, per the company's release): revenue $9.23B (flat YoY), net income $904.9M (-11.7%), diluted EPS $3.20 (-4.8%), closings 23,983 (+4%), home-sales gross margin 20.7% (down from 21.8%), cancellation rate 20% (up from 17%). Management cut FY2026 guidance in July to revenue $32.5–$33.0B and 83,800–84,300 closings (from $33.5–$34.5B). FY2026 full-year results are due 2026-10-29.

## Owner's earnings
Fiscal year ends September 30. FY2025 (10-K via EDGAR, financials_history.csv): OCF $3,420,900,000 − capex $137,400,000 − SBC $131,000,000 = **conservative OE $3,152,500,000 = $10.17/share** (latest FY OE/share, key_numbers.md). Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC) prints $3,585,200,000 for FY2025 — it equals net income exactly here because capex exceeds D&A and the engine captures no ΔNWC; for a homebuilder that is a real omission, since inventory *is* the working capital (see NI_OCF_DIVERGENCE below).

The conservative series is inventory-timing noise on a single year, not earning power: conservative OE totals were $349,500,000 (FY2021) and $308,500,000 (FY2022) while net income was $4,175,800,000 and $5,857,500,000 — OCF collapsed because the company was funding a massive inventory build — then OE snapped to $4,044,300,000 in FY2023 as homes closed. OE positive 5 of the last 5 fiscal years. The engine's normalized base (median of the last 3 FY OE/share) is $10.17/share.

**Base used = TTM owner's earnings through Q3 FY2026, from ttm.py (resolves STALE_FY; inputs quoted verbatim from ttm.json — never hand-computed):**
- OCF: FY (2024-10-01 to 2025-09-30) $3,420,900,000 − prior YTD (to 2025-06-30) $949,100,000 + current YTD (to 2026-06-30) $880,800,000 = **TTM $3,352,600,000**
- Capex: FY $137,400,000 − prior YTD $93,600,000 + current YTD $106,600,000 = **TTM $150,400,000**
- SBC: FY $131,000,000 − prior YTD $101,100,000 + current YTD $107,500,000 = **TTM $137,400,000**
- Shares: current-YTD weighted diluted **288,400,000** (ttm.py basis; FY2025 average was 309,900,000)
- **TTM OE total $3,064,800,000 → base OE/share $10.63** (base_source: ttm_json)

Note vs the v4 pass: v4 divided the same TTM OE total by the single-quarter share count and got $10.83; v5's standardized ttm.py basis (current-YTD weighted diluted shares) gives $10.63. The TTM base sits only modestly above the 3-yr median of $10.17, so there is no base fight to adjudicate — and the preliminary run on the median base (weighted IRR 10.40%, weighted IV@15% $85.22, dcf_numbers.json preliminary pass) lands in the same tier.

**Growth sanity check (mandatory):** engine blended growth is -3.09% (rev CAGR 5y 11.02%, rev CAGR 3y 0.76%, latest rev YoY -6.93%, OE/share CAGR 2y -7.07%), +4.41pp buyback adjustment = **g_base +1.32%**. Against actual prints: FY2025 revenue -6.93%, Q3 FY2026 revenue flat YoY, Q3 EPS -4.8%, Q3 net income -11.7%, FY2026 guided revenue cut to $32.5–$33.0B. The base start (+1.3%) is above the total-company prints — defensible only as a per-share number, and the reason is written here: buybacks are shrinking the count fast ($2.2B repurchased year-to-date through Q3 FY2026; FY2026 repurchases expected to reach at least $3.25B; new $5.0B authorization 2026-09-15). Bear -3.7% tracks the guided decline; super bear -10.0% (engine floor under the -12pp offset) tracks the Q3 net-income decline; bull +6.3% and super bull +13.3% sit at/below recovery-year prints (5-yr revenue CAGR 11.02%) — no cap artifact in either direction.

## MOAT — score 5/10, moderate/narrow. CAP = 8.5 years
Justification: scale that has actually compounded, lot-option discipline, and a balance sheet that gains share through downturns — against a commodity product with no switching costs, no pricing power, and capable rivals.
- **FOR:** #1 U.S. builder by volume since 2002, ~15% national share — procurement and subcontractor scale no sub-scale rival can match; lot discipline: 570,000 lots with only 22% owned / 78% controlled through purchase contracts, plus captive Forestar supply, caps land blow-up risk; balance-sheet strength lets it keep building and buying back stock through a trough while small builders starve — share is structurally gained in downturns; affordability positioning ($362k average closing price) targets the deepest, most undersupplied buyer pool.
- **AGAINST:** the product is a commodity — no switching costs, no network effects, no lock-in; buyers choose on price, location, and the rate buydown; no visible pricing power — incentives ran ~10% of revenue and home-sales gross margin still fell 21.8% → 20.7%; land and lots are bought in a competitive open market (lot costs +5% YoY in Q3 FY2026); Lennar, PulteGroup, and NVR are capable, well-capitalized rivals, and NVR's asset-light model earns structurally higher ROE.
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — final v5 run
Base OE $10.63/share (TTM, above), moat 5 (CAP 8.5y), probabilities skewed bearish vs the 10/25/30/25/10 defaults — **written reason:** FY2026 guidance cut ~$1B in July, cancellations up to 20%, incentives still elevated, margins compressing, and the FY2026 print (2026-10-29) still ahead. Offsets/multipliers left at defaults (-12/-5/0/+5/+12pp; 0.75/0.90/1.00/1.10/1.25). Price: **$135.45** (nasdaq_quote_api).

| Scenario | Prob | Growth start | OE mult | Story | IV@15% | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | -10.0% | 0.75 | Rates stay high, margins trough, closings fall | $38.70 | 5.59% |
| Bear | 30% | -3.7% | 0.90 | Guided decline extends through FY2027 | $60.58 | 7.83% |
| Base | 30% | +1.3% | 1.00 | Flat total business, buybacks carry per-share OE | $82.97 | 10.11% |
| Bull | 15% | +6.3% | 1.10 | Rate relief, orders recover, margins stabilize | $112.35 | 12.94% |
| Super bull | 10% | +13.3% | 1.25 | Housing upcycle off the trough, EPS snapback | $170.29 | 17.86% |

**Probability-weighted: IV@15% $82.75 (-38.9% vs price), IV@12% $108.92, IV@10% $138.01, weighted IRR 10.14%. Tier by numbers: C.** Diagnostics (key_numbers.md): OE yield 7.85%, terminal value 17.8% of IV@15% (low — the verdict is not a terminal-value artifact), scenario spread 4.40x, net debt not extracted (see flags).

## FLAGS — every fragility flag resolved
- **STALE_FY (latest FY ended 12.5 months ago):** Resolved with the filing-derived TTM base above ($10.63/share from ttm.json). FY2026 ended 2026-09-30 but the 10-K is not filed yet (earnings 2026-10-29); the TTM through Q3 FY2026 is the most current complete picture.
- **BUYBACK_TAILWIND (share count shrinking 4.4%/yr):** Credited via the standardized treatment only: the growth blend carries the +4.41pp share-count adjustment, and the TTM base divides by the shrunken 288,400,000 count. If anything this flatters per-share growth, which makes the below-hurdle verdict more robust, not less. The buyback is real cash: $2.2B in 9M FY2026, at least $3.25B expected for FY2026, new $5.0B authorization with no expiration (2026-09-15 8-K).
- **OE_VOLATILE (OE/share range >3x over the last 5 yrs):** Resolved as a measurement artifact of the conservative definition, not earnings-power volatility: OE totals ranged $308,500,000–$4,044,300,000 across FY2021–25 while net income ranged $3,585,200,000–$5,857,500,000, because OCF absorbs the inventory build/liquidation cycle. Mitigations applied: normalized/TTM base (not a single year) and bear weight widened — super bear + bear = 45% vs the 35% default, per the flag's own instruction.
- **NI_OCF_DIVERGENCE (2024: net income $4,756,400,000 vs OCF $2,189,800,000, financials_history.csv):** Found: working capital — inventory investment. In FY2024 revenue still grew and the company spent heavily on homes under construction and lot development ahead of closings, so cash went into inventory instead of out as OCF; the same pattern, more extreme, explains FY2021–22 (OCF $534,400,000 and $561,800,000 vs net income $4,175,800,000 and $5,857,500,000). No tax deposit, impairment, or one-off gain is involved — capex is trivial ($165,300,000 in FY2024) and SBC is small ($118,100,000). Implication: single-year conservative OE understates earning power in build years and overstates it in liquidation years; the TTM window (which spans both) is the right antidote.
- **WIDE_SCENARIO_SPREAD (super-bull IV 4.40x super-bear IV):** Real, not a modeling error — this is a cyclical at a possible trough, and even the sign of growth is in dispute. Consequence applied: confidence capped at medium (never high with this flag), and the verdict is sized to the conservative end.
- **Not fired, but checked — balance sheet:** the engine extracted no debt (net_debt_latest is null in dcf_numbers.json; DHI's debt tags don't match the engine's candidates), so neither HIGH_NET_DEBT nor BIG_NET_CASH could fire and no net-debt figure is quoted here — per the hard rule, a figure not in the computed outputs is stated in words, not calculated. Nothing in the research suggests balance-sheet distress: the company funded $2.2B of buybacks in 9M FY2026 while guiding to at least $3.25B for the year.

## Thoughts / overlay
- The verdict is robust to the base choice that usually moves homebuilders: preliminary (median base $10.17, default probs) gave 10.40% weighted IRR; the final TTM/bear-skewed run gives 10.14%. Both are Tier C. The method range here is narrow — C on any defensible base tried — unlike the wide spreads seen in inflection names.
- Only the super bull clears the current price at a 15% discount ($170.29), and even the plain bull does not ($112.35). At $135.45 the market is already paying for a housing recovery; the buyer is not paid to wait for one.
- The honest bull case is cyclical, not DCF-visible at trough inputs: chronic U.S. housing undersupply, DHI gaining share, and EPS that has snapped back violently in past recoveries. That case lives in the 10% super-bull weight — sized accordingly.
- Red flags / watch items: margin compression is incentive-driven and incentives get more expensive as rates rise; cancellations at 20%; lot-cost inflation +5% YoY; the Rental segment faces proposed restrictions on institutional single-family purchases (small today — $31M pretax in Q3 FY2026 — but it removes a diversification vector); Q4/FY2026 print on 2026-10-29 is the next hard data point.
- **Hurdle math:** the price that clears 15% on the weighted path is the weighted IV@15% itself, **$82.75**; with a 25% margin of safety, ~$62.

## Final verdict
- **Final tier: C** (weighted IRR 10.14%; tier_final = tier_by_numbers, no override)
- Confidence: **Medium** (TTM base is filing-derived from ttm.py; capped below high by WIDE_SCENARIO_SPREAD and genuine cyclicality)
- One-liner: America's largest builder with a narrow scale moat (5/10) and a real buyback, but at $135.45 (12.7x TTM OE of $10.63) it returns only 10.1% weighted — it clears the 15% hurdle only at ~$83 (~$62 with a 25% margin of safety); even the bull case is worth less than today's price.
