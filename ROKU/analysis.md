# ROKU — Roku, Inc.
v5 run, 2026-10-15. In scope (market cap $23.326B at $154.57, nasdaq_quote_api).

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.py output, or financials_history.csv — none are recomputed. Quarterly prints and the Fox transaction terms are from web research reporting, attributed as such.

## What it is
The leading TV streaming operating system in the US (~37% OS/CTV share in survey and industry reporting, ~100M households reached). Devices and licensed Roku TVs are distribution; the profit engine is the Platform segment — advertising (home screen, video ads, The Roku Channel, which reporting ranks as the #2 app on the platform by engagement) plus subscription revenue share. Per Q2 2026 reporting: total revenue $1.35B, up 21.9% YoY, platform revenue $1.22B, up 25%, net income $164.2M — a record-profitability quarter after years of losses.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $483,718,000; capex $5,280,000; SBC $354,169,000 (always a real cost).
- **Conservative owner's earnings FY2025: $124,269,000 = $0.82/share** (key_numbers.md: latest FY OE/share $0.82, latest FY OE total $124.3M)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC) for FY2025 is **−$606,801,000** in financials_history.csv — distorted by the working-capital swing in that definition (delta_nwc $735,482,000 in the same row), so it is not the usable definition here; the OCF-based conservative figure, which deducts SBC in full, is the cleaner one.
- OE positive only **2 of the last 5 fiscal years** (key_numbers.md). FY2023 and FY2024 conservative OE were negative in financials_history.csv (−$196,893,000 and −$171,678,000); the business only inflected to positive OE in FY2025.
- Balance sheet: financials_history.csv shows cash $1,587,068,000 at FY2025 with the debt columns blank for that year, and the engine reports net debt as null (key_numbers.md shows net debt "—") — this is a cash-rich, essentially debt-free balance sheet in the filed history, which supports the company but does not fix the valuation gap below.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $483,718,000 − prior YTD $248,465,000 + current YTD $483,784,000 = **TTM $719,037,000**
- Capex: FY $5,280,000 − prior YTD $3,053,000 + current YTD $6,904,000 = **TTM $9,131,000**
- SBC: FY $354,169,000 − prior YTD $180,134,000 + current YTD $154,003,000 = **TTM $328,038,000**
- Shares (current-YTD weighted diluted): **151,461,000**
- **TTM OE total $381,868,000 → base OE/share $2.52** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is **−$1.19/share** — rejected as the base: the median spans the pre-inflection loss years (FY2023–FY2024 OE was negative), while the latest FY is +$0.82 and the TTM is +$2.52. The inflection is real in the filings (Q2 2026 reporting corroborates it), so the TTM base is used — and the verdict is checked against the median base in the method range below.

## MOAT — 6/10, moderate
Justification: Leading TV operating system in the US (~37% share, ~100M households) with home-screen gatekeeper economics and a high-margin platform (advertising + subscriptions) on top, but no owned must-have content, rival OSes from Amazon/Google/Samsung/Apple that can subsidize distribution, cyclical ad exposure, and SBC still large enough to dilute 3.1%/yr. Moderate moat, not wide.
- FOR: #1 TV OS in the US (~37% share) reaching ~100M households — home-screen gatekeeper for discovery and advertising; platform mix is the profit engine (high-margin advertising and subscription revenue; devices are distribution, not the business); The Roku Channel engagement plus first-party viewing data for ad targeting and measurement; asset-light model — capex is negligible against operating cash flow in the filed history.
- AGAINST: Amazon, Google, Samsung and Apple all ship rival TV operating systems and can subsidize hardware and defaults; no owned must-have content — The Roku Channel largely aggregates other owners' programming; advertising revenue is cyclical and platform mix shifts pressure gross margin; SBC was $328,038,000 TTM — share count still growing 3.1%/yr despite buybacks; pending Fox acquisition (DOJ second request, Sept 2026) makes standalone economics secondary until the deal closes or breaks.
- A 6 gives CAP = 9.8 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 9.8 years, 15-year projection.

## DCF — v5 final run (2026-10-15)
Growth recalibration (written reason): the engine's blend is revenue-only here — the OE/share CAGR component is absent (key_numbers.md shows it as "—") because prior-year OE was negative — so g_base is 12.07% (blend 15.18% with the −3.11% dilution adjustment). That understates OE growth at a margin inflection: the TTM base itself inflected from a negative median, Q2 2026 revenue printed +21.9% total / +25% platform per reporting, and management had already raised full-year platform guidance during 2026 per earnings reporting. Offsets were therefore set to −0.07 / 0.00 / +0.08 / +0.15 / +0.23, giving starts of 5.1 / 12.1 / **20.1** / 27.1 / 35.1%. Probabilities stay at the 10/25/30/25/10 defaults; OE multipliers stay 0.75/0.90/1.00/1.10/1.25. Price $154.57.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | 5.1% | 0.75 | Ad cycle turns, OS share leaks to Amazon/Google, SBC stays heavy | $17.39 | 3.96% |
| Bear | 25% | 12.1% | 0.9 | Revenue growth fades to the engine blend; margins stall | $28.48 | 5.08% |
| Base | 30% | 20.1% | 1.0 | 2026 platform growth holds near prints, operating leverage continues | $45.04 | 6.75% |
| Bull | 25% | 27.1% | 1.1 | Platform outgrows guidance, Roku Channel monetization compounds | $67.23 | 8.79% |
| Super bull | 10% | 35.1% | 1.25 | Sustained hyper-growth with expanding margins over the full CAP | $107.72 | 11.97% |

- **Probability-weighted: IV@15% $49.95 (−67.7% vs price), IV@12% $69.66, IV@10% $92.09, weighted IRR 7.26%, base-case IRR 6.75%**
- **Tier by numbers: D.** Diagnostics (key_numbers.md): OE yield 1.63%, terminal value 23.9% of IV@15%, scenario spread 6.20x, 9.5 months since FY end.
- The decisive fact: even the super-bull case — a 35.1% growth start, 1.25x OE, the most generous defensible inputs — returns only 11.97% at $154.57. No scenario in the set clears the 15% hurdle at this price.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.5 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, quoted above.
- **DILUTION** (share count +3.1%/yr): already deducted via the −3.11% growth adjustment in g_base. SBC trend from the filings: $370,130,000 (FY2023), $384,662,000 (FY2024), $354,169,000 (FY2025), $328,038,000 TTM — falling in absolute terms and as the business grows, and Q4 2025 reporting noted buybacks brought quarterly dilution to near 0%, but the multi-year share count still rose from 141,572,000 (FY2023) to 150,912,000 (latest) in financials_history.csv. SBC remains the single largest deduction in the OE base.
- **NI_OCF_DIVERGENCE** (2023, 2024, 2025): resolved — the bridge is SBC, not a one-off tax deposit or impairment. From financials_history.csv: FY2023 net income −$709,561,000 vs OCF $255,856,000 with SBC $370,130,000; FY2024 net income −$129,386,000 vs OCF $218,045,000 with SBC $384,662,000; FY2025 net income $88,361,000 vs OCF $483,718,000 with SBC $354,169,000. OCF adds SBC back as non-cash; the conservative OE deducts it in full, so the divergence does not flatter the base — it is exactly why the base is conservative.
- **LOW_OE_YIELD** (base OE yield 1.63%): real and decisive — at $154.57 the price is almost entirely growth and, in practice, the pending acquisition (see overlay). Handled by stressing growth upward in the recalibration above; the tier still lands D, so the flag changes the confidence in the verdict's direction, not the tier.
- **WIDE_SCENARIO_SPREAD** (6.20x): real — a business at a profitability inflection has a genuinely wide outcome range. Confidence is capped at medium, and the verdict is sized to the conservative end; notably the spread here runs from bad to still-below-hurdle, not from bad to good.

## My thoughts / overlay
- **Method range: F to D, all below the hurdle.** On the normalized 3-yr median base (−$1.19/share) the preliminary engine run returned Tier F with no scenarios. On the TTM base with default offsets, weighted IRR was 5.64% (IV@15 $34.15). On the TTM base with the generous recalibrated offsets above, weighted IRR is 7.26% (IV@15 $49.95). Every defensible method lands below 10%; quoting any one number without its base would hide that the range is F→D, never near B.
- **The price is a merger price, not a standalone DCF price.** Per reporting on the announced Fox transaction, Roku holders are to receive $96.00 in cash plus 0.9693 Fox Class A shares per Roku share; the U.S. Department of Justice issued a second request on September 8, 2026, and the companies expect closing in the first half of 2027 subject to regulatory clearance and shareholder approvals. The standalone DCF in this file values the operating business only — it does not price deal completion. If the deal closes, the DCF gap is moot for a seller into the deal; if it breaks, the standalone numbers above are the fallback, and they sit far below $154.57.
- **Quality is improving, price is the problem.** The inflection is filing-real: OCF TTM $719,037,000, SBC falling, capex negligible, cash $1,587,068,000 at FY2025 in the filed history. None of that is in dispute. What the DCF says is narrower: $2.52/share of TTM owner's earnings cannot support $154.57 at a 15% hurdle under any growth path in the scenario set.
- **Hurdle-clearing price:** the weighted IV@15% is $49.95 — that is the price at which the weighted case clears 15% with no margin of safety. A buyer wanting protection against the bear cases needs the bear IV@15% of $28.48 or lower.

## Final verdict
- **Final tier: D** (weighted IRR 7.26% on the v5 final inputs; method range F to D)
- Confidence: **Medium** (capped by WIDE_SCENARIO_SPREAD; high on the direction — no defensible input set clears the hurdle — medium on any single IV figure given the 6.20x spread)
- One-liner: Profitability-inflecting CTV platform leader, moat 6/10 — standalone DCF does not clear 15% even on generous operating-leverage growth (weighted IRR 7.26%, IV@15 $49.95 vs $154.57 price); the price is a Fox-merger price, not standalone value — it clears 15% only at or below the weighted IV@15 of $49.95.
