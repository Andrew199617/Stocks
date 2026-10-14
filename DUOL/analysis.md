# DUOL — Duolingo, Inc.
v5 re-run, 2026-10-13 (supersedes the v4 analysis of 2026-10-12; method and judgment inputs unchanged, price updated). In scope: market cap $6.768B (key_numbers.md), under the $40B scope limit, watchlist name.

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.py output, or financials_history.csv — none are recomputed.

## What it is
The dominant consumer language-learning app: free ad-supported tier plus Super Duolingo and Duolingo Max subscriptions, family plans, and early expansion into math, music, and chess. Asset-light subscription software. Scale at Q2 2026 (shareholder-letter figures via search): 58.7M daily active users (+23% YoY), 12.7M paid subscribers (+17% YoY), paid penetration ~9% of monthly users. 2026 strategy is an explicit pivot: management is prioritizing DAU growth (target 100M DAU by 2028) over near-term monetization, reducing paywall friction after the 2025 monetization push demonstrably slowed DAU growth. Q2 2026 revenue was $298.5M (+18.3% YoY) and bookings grew only +8% YoY; FY2026 is guided to ~$1.21B revenue (~+16%), bookings growth of 10–12%, and adjusted EBITDA of ~$320M.

## Owner's earnings (SEC EDGAR, filing-direct)
History (conservative OE = OCF − capex − SBC, from financials_history.csv): negative in 2020–22 (−$2,699,000, −$35,220,000, −$25,726,000), then a clean profitability inflection: +$55,202,000 (2023), +$162,920,000 (2024), **+$232,290,000 in FY2025 = $4.81/share** (key_numbers.md: latest FY OE/share $4.81) on revenue of $1,037,589,000 (+38.71% YoY, key_numbers.md).
- Maintenance version FY2025: $458,562,000 (financials_history.csv) — **rejected as the base**. FY2025 net income ($414,065,000, CSV) sits far above operating income ($135,570,000, CSV) and the CSV tax line shows a benefit of $231,655,000 — the deferred-tax valuation-allowance release identified in the v4 pass. The maintenance formula starts from net income, so it inherits that non-cash one-off; the OCF-based conservative figure excludes it and is the cleaner measure.
- SBC is a real and heavy cost: $137,437,000 in FY2025 and $144,684,000 TTM (ttm.py, below) — roughly a third of operating cash flow. It is subtracted in full in every scenario.
- Balance sheet: cash $1,036,389,000 at FY2025 (financials_history.csv) and **no debt reported** (no current/long-term debt tags in EDGAR; engine net debt = null in key_numbers.md). The net cash is a downside cushion, not a growth engine — it does not close the valuation gap below.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $387,823,000 (2025-01-01 → 2025-12-31) − prior YTD $196,306,000 (2025-01-01 → 2025-06-30) + current YTD $239,031,000 (2026-01-01 → 2026-06-30) = **TTM $430,548,000**
- Capex: FY $18,096,000 − prior YTD $2,507,000 + current YTD $7,028,000 = **TTM $22,617,000** (tag: PaymentsToAcquirePropertyPlantAndEquipment)
- SBC: FY $137,437,000 − prior YTD $65,610,000 + current YTD $72,857,000 = **TTM $144,684,000** (tag: ShareBasedCompensation)
- Shares (current-YTD weighted diluted): **50,080,000**
- **TTM OE total $263,247,000 → base OE/share $5.26** (key_numbers.md: $5.26, source: agent_supplied_ttm_override; engine input 5.256529552715655)
- The engine's normalized base (3-yr median) is $3.46/share — rejected as the base; see BASE_DIVERGENCE below.

## Moat: 5/10 — moderate / narrow
Justification: dominant brand and mindshare, habit/streak mechanics and a decade of A/B-testing process power, and learner-data scale feeding AI content — but weak proven pricing power (the 2025 monetization push slowed DAU and was reversed), no hard switching costs, Apple/Google platform dependence, and free general-purpose AI lowering the entry barrier.
- FOR: Brand and mindshare — the default language-learning app globally, organic word-of-mouth acquisition; Habit mechanics — streaks, leagues, and a decade of A/B-tested behavioral design create psychological switching costs; Learner-data scale — billions of exercises from 58.7M DAUs feed personalization and AI content generation; Recurring subscription revenue with lower-churn family plans; ~70%+ gross margins held through the AI transition.
- AGAINST: Weak pricing power — the 2025 monetization push slowed DAU growth and management had to reverse it; AI lowers the entry barrier — free ChatGPT/Gemini/Translate offer conversational tutoring and Duolingo owns no foundation model; No hard switching costs — month-to-month subscriptions, users multi-home, no enterprise lock-in; Platform dependence on Apple/Google app stores for distribution and billing; Monetization stalling at scale — Q2 2026 bookings +8% vs DAU +23%, paid penetration ~9% of MAU after 14 years.
- A 5 gives CAP = 8.5 years (key_numbers.md): growth holds 2 years, then converges to the 2.5% terminal rate over the CAP, 15-year projection.

## Growth recalibration (mandatory sanity check — written reason)
The engine's blended growth is 43.06% → g_base capped at 35.00% (key_numbers.md), built from backward-looking signals (rev CAGR 5y 45.04%, rev CAGR 3y 41.07%, latest rev YoY 38.71%, OE/share CAGR 2y 101.21% — the last an inflection artifact off a near-zero base). **Those rates are not what the company is printing now, and using them would repeat the APP cap error in reverse.** Actual recent prints and guidance:
- Revenue: FY2025 +38.71% → Q1 2026 +26.5% → Q2 2026 +18.3% → Q3 2026 guided ~$302M; FY2026 guided ~$1.21B ≈ +16%.
- Bookings: Q2 2026 +8% YoY; FY2026 guided +10–12%.
- Adjusted EBITDA: FY2026 guided ~$320M, with margins being deliberately spent on DAU growth and AI.
- DAU +23% is the counterweight: engagement is still compounding even as reported revenue decelerates.
Scenario starts are therefore set far below the engine cap (offsets −0.37/−0.28/−0.20/−0.12/−0.03 vs the 35% capped base). The bear/super-bear starts sit below recent revenue prints **because the company's own bookings (+8%) and EBITDA guides already sit there** — that is the written reason. The super-bull start (32%) sits above current revenue prints deliberately: it is the re-acceleration tail (100M DAU converting to paid at higher penetration plus new subjects), weighted only 8%.

## DCF — v5 final run (2026-10-13)
Price: **$140.10** (nasdaq_quote_api). Probabilities 15/30/30/17/8 — bear-tilted vs the 10/25/30/25/10 default because guided deceleration, the litigation overhang, and AI entry-barrier erosion are live, while the DAU pivot's payoff is unproven. Probabilities sum to 100%.

| Scenario | Prob | Growth start | OE mult | Story | IV@15% | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | −2.0% | 0.75 | Free AI tutors commoditize the category; DAU stalls, monetization push fails again, margins compress | $26.79 | 4.77% |
| Bear | 30% | 7.0% | 0.90 | Bookings-style growth persists; DAU grows but won't pay; SBC stays ~1/3 of OCF | $46.76 | 6.83% |
| Base | 30% | 15.0% | 1.00 | FY26 revenue guide (~+16%) roughly holds, then fades over the 8.5-yr CAP | $72.16 | 9.35% |
| Bull | 17% | 23.0% | 1.10 | DAU growth converts: paid penetration rises, family/Max mix lifts ARPU, operating leverage returns | $109.61 | 12.65% |
| Super bull | 8% | 32.0% | 1.25 | 100M DAU path achieved and monetized; math/music/chess become real second engines | $177.67 | 17.58% |

- **Probability-weighted: IV@15% $72.54, IV@12% $98.90, IV@10% $128.61, weighted IRR 9.44%** (base-case IRR 9.35%) — all from key_numbers.md.
- **Tier by numbers: D** (weighted IRR < 10%). Upside at 15%: −48.2%.
- Diagnostics (key_numbers.md): OE yield 3.75%, terminal value 21.3% of IV@15%, scenario spread 6.63x, 9.4 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY (latest fiscal year ended 9 months ago; 9.4 months in key_numbers.md):** Resolved with the TTM base above, computed by ttm.py from 10-Q YTD filings and quoted line-by-line — not estimated.
- **BASE_DIVERGENCE (latest FY OE/share $4.81 vs 3-yr median $3.46):** The median is the distorted one. It is the 2024 value, dragged down by the pre-scale years of a genuine profitability inflection (conservative OE: −$25,726,000 in 2022 → +$55,202,000 → +$162,920,000 → +$232,290,000, CSV). A through-cycle median is the wrong tool for a company that crossed into profitability in 2023 and has grown OE every year since; the TTM base ($5.26) is used instead, with this reasoning on record.
- **WIDE_SCENARIO_SPREAD (6.63x):** Real, not an artifact — the equity story genuinely bifurcates on whether the DAU-first pivot converts to bookings or AI commoditizes the product. Confidence is capped at medium (never high) for this reason, and bear-side weight was raised to 45% combined.
- **DILUTION (share count growing 7.0%/yr; key_numbers.md share count CAGR 6.97%, growth adj −5.00%):** The engine's long-window figure is inflated by IPO-era share counts (12,735,000 diluted in 2020, 23,433,000 in 2021 — pre/early-IPO artifacts, CSV). The current run-rate is still material: 46,522,000 (2023) → 48,308,000 (2025) → 50,080,000 (H1 2026, ttm.py). SBC TTM of $144,684,000 is already subtracted in full from OE. Scenario growth rates are per-share, so dilution is embedded in the recalibrated starts rather than double-counted via the engine's blend adjustment. A $400M buyback was announced in Feb 2026 (v4 pass) — it only partly offsets issuance.
- **OE_VOLATILE (OE/share range over the last 5 yrs spans >3x):** This is inflection volatility, not cyclicality — OE went from negative to $5.26/share TTM as the business scaled past breakeven. The normalized median would understate current earning power (see BASE_DIVERGENCE); the volatility is instead handled by the widened bear weight (45% combined) and the super-bear OE multiplier of 0.75.
- **NI_OCF_DIVERGENCE (2023, 2024):** Explained, no cash-quality problem. In 2023, OCF of $153,614,000 vs net income of $16,067,000 (CSV): the gap is SBC of $95,221,000 (CSV) — non-cash, added back in OCF but expensed in NI — plus D&A and growth in deferred subscription revenue. In 2024 the same structure repeats (OCF $285,513,000 vs NI $88,574,000; SBC $110,477,000, CSV). There is no KO-style one-off tax deposit. The mirror-image one-off is in 2025 net income — the valuation-allowance tax benefit — which is exactly why the OCF-based conservative OE (not the NI-based maintenance figure) anchors this valuation.

## Thoughts / overlay
- **Method range:** the unrecalibrated preliminary v5 run (3-yr-median base $3.46, capped 35% growth, default probs) gave weighted IRR 12.95% / Tier C / IV@15% $111.60 (dcf_numbers.json preliminary pass); the final recalibrated run gives 9.44% / Tier D. Defensible range is **C → D — every variant is below the 15% hurdle**, so the verdict's direction is robust even though the exact number is growth-assumption-driven.
- Even the **bull case does not clear 15%** at this price (IRR 12.65%, IV@15% $109.61 vs $140.10). Only the 8%-weighted super bull does (17.58%). At $140.10 the market is still paying for DAU-pivot success that management has guided will not show up in 2026 bookings or EBITDA.
- Overhangs: a securities class action has been filed alleging the 2025 monetization-friction/DAU disclosures and AI content quality were misleading (allegations unproven; lead-plaintiff deadline Dec 7, 2026 per plaintiff-firm notices, still live per Oct 2026 notices); the CFO resigned in January 2026; the stock fell roughly another 5% into this run ($147.74 prior close → $140.10) — the de-rating is real, it just hasn't reached hurdle-clearing levels on owner's earnings. Q3 2026 results are expected in early November and are the next test of the DAU-pivot math.
- **Hurdle math:** the weighted IV@15% is **$72.54** — that is the price that clears 15% on the weighted path. With a ~25% margin of safety against the wide scenario spread, an entry near **~$54** is where this starts to compensate for the AI/binary risk. Net cash cushions, but does not change, that math.

## Final verdict
- **Final tier: D** (same as tier by numbers — no override). Weighted IRR 9.44% at $140.10; IV@15% $72.54 vs price $140.10.
- Confidence: **Medium** (filing-derived TTM base and a robust below-hurdle direction across all defensible runs; capped at medium by the 6.63x scenario spread and genuine growth-path uncertainty).
- One-liner: High-quality learning platform, moat 5/10 — but growth has decelerated to guided ~16% revenue / ~11% bookings with SBC eating a third of operating cash flow, so at $140.10 (26.6x TTM OE of $5.26/share) the weighted IRR is only 9.4% (IV@15% $72.54); it clears the 15% hurdle only at ~$73, nearer ~$54 with a margin of safety.
