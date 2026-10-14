# QSR — Restaurant Brands International Inc.
v5 run, 2026-10-14. In scope (market cap $32.474B at $71.06, nasdaq_quote_api — under the $40B cutoff).

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.py output (ttm.json), or financials_history.csv — none are recomputed.

## What it is
Global quick-service franchisor: Burger King, Tim Hortons, Popeyes, and Firehouse Subs — more than 33,000 restaurants at June 30, 2026, more than 95% franchised (Q2 2026 reporting). Revenue is mostly franchise royalties/rent, Tim Hortons supply-chain sales, and — temporarily — company restaurants from the Carrols acquisition (the Restaurant Holdings segment, being refranchised, with management targeting a wind-down by end-2027 and a ~99% franchised model). Q2 2026 print: consolidated system-wide sales +6.4%, comparable sales +3.8% (Burger King US +8.5%, International comparable +5.5%, Tim Hortons Canada +0.1%, Popeyes comparable −5.1%), revenue $2.52B (+4.6% YoY), adjusted EPS $1.07, and management reiterated it is on track for 8% organic adjusted operating income growth in 2026.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $1,714M; capex $265M (tag PaymentsToAcquirePropertyPlantAndEquipment); SBC $151M (tag ShareBasedCompensation — always a real cost).
- **Conservative owner's earnings FY2025: $1,298M = $2.84/share** (base_oe_latest_per_share)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $1,245M — same ballpark as the conservative figure, which raises confidence.
- OE positive 5 of the last 5 fiscal years. Net debt $13.282B (latest, from dcf_numbers.json) — see HIGH_NET_DEBT under Flags.
- Capex has stepped up from the $100–120M/yr range (FY2022–23) to $201M (FY2024) and $265M (FY2025) as the acquired Carrols company restaurants were consolidated; this is largely Restaurant Holdings capex that should fall as refranchising proceeds, so the conservative definition (total capex) is, if anything, currently harsh on the franchisor core — one reason the verdict below leans on the TTM base rather than inventing a maintenance-capex adjustment.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $1,714,000,000 − prior YTD $567,000,000 + current YTD $757,000,000 = **TTM $1,904,000,000**
- Capex: FY $265,000,000 − prior YTD $102,000,000 + current YTD $109,000,000 = **TTM $272,000,000**
- SBC: FY $151,000,000 − prior YTD $81,000,000 + current YTD $70,000,000 = **TTM $140,000,000**
- Shares (current-YTD weighted diluted): **459,000,000**
- **TTM OE total $1,492,000,000 → base OE/share $3.25** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $2.49/share — it averages in FY2023–24, before the Burger King US turnaround and International growth lifted cash generation; the TTM figure is the more current, filing-derived base and is used instead. The preliminary run on the median base also produced Tier D (weighted IRR 8.86%, weighted IV@15% $33.78), so the verdict's direction does not depend on the base choice.

## Moat: 6/10 — moderate-strong franchisor, not wide
Justification: Durable, scaled restaurant brands on an asset-light royalty model with proven through-cycle cash generation, but the brands are mostly #2 in their categories, Tim Hortons is concentrated in a slow Canadian market, Popeyes US has declined in seven of the last eight quarters (per Q2 2026 reporting), and the equity sits behind heavy leverage — a step below a wide-moat franchisor.
- FOR: Four scaled brands (Burger King, Tim Hortons, Popeyes, Firehouse Subs) with >33,000 restaurants and >95% franchised — royalties on system sales, not restaurant-level margins; Tim Hortons' entrenched position in Canada (~41% of operating income per Q2 2026 reporting); International segment compounding (system-wide sales +10.7% in Q2 2026) with master-franchise economics; Burger King US turnaround proving out (+8.5% comparable sales in Q2 2026, its strongest since mid-2023); OE positive 5/5 years including the 2020 COVID year in the filed history.
- AGAINST: No clear #1 brand position in the US — Burger King trails McDonald's, Popeyes trails Chick-fil-A, and both face Yum!/McDonald's scale in marketing and tech; Popeyes US comparable sales −5.1% in Q2 2026 and negative in seven of the last eight quarters; Tim Hortons Canada comparable sales only +0.1% in Q2 2026, with commodity/beef cost pressure cited in the September 2026 Argus downgrade; franchisee economics are the real moat constraint — royalties only compound if franchisees earn enough to remodel and open units; high financial leverage (net debt $13.282B) leaves equity holders a thin claim ahead of creditors.
- A 6 gives CAP = 9.8 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 9.8 years, 15-year projection.

## DCF — v5 final run (2026-10-14)
Growth recalibration (written reason): the engine's blended growth is 13.24% (g_base 13.09%), built from revenue CAGRs of 13.69% (5y) / 13.19% (3y) / 12.23% (latest YoY) and OE/share CAGR 2y of 13.29%. Those revenue figures are flattered by the May 2024 Carrols acquisition, which consolidated company-restaurant sales into reported revenue — they are not underlying system growth. The underlying prints are: system-wide sales +6.4% and comparable sales +3.8% in Q2 2026, Q2 revenue +4.6% YoY, and management's own algorithm of 8%+ organic adjusted operating income growth through 2028 with ~5% net restaurant growth. Scenario starts were therefore set via offsets (−0.121 / −0.081 / −0.041 / −0.011 / +0.019 vs g_base) to 1.0 / 5.0 / **9.0** / 12.0 / 15.0% — the base start sits just above the guided 8% AOI algorithm (resumed buybacks, ~$500M planned for 2026, add a little per-share lift), and even the super-bull start (15.0%) stays below the filing revenue prints it would need to beat, with the written reason being that those prints are consolidation-inflated, not organic. Probabilities are the defaults 10/25/30/25/10; OE multipliers are the defaults 0.75/0.90/1.00/1.10/1.25. Price $71.06.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | 1.0% | 0.75 | Consumer downturn, Popeyes/TH deteriorate, leverage bites | $18.69 | 5.73% |
| Bear | 25% | 5.0% | 0.90 | System growth halves; BK turnaround stalls | $26.80 | 7.33% |
| Base | 30% | 9.0% | 1.00 | Guided 8%+ AOI algorithm delivered; ~5% unit growth | $35.58 | 9.04% |
| Bull | 25% | 12.0% | 1.10 | BK momentum spreads to Popeyes; International keeps compounding | $44.71 | 10.71% |
| Super bull | 10% | 15.0% | 1.25 | All four brands fire; refranchising unlocks cash returns | $58.03 | 12.96% |

- **Probability-weighted: IV@15% $36.22 (−49.0% vs price), IV@12% $48.73, IV@10% $62.75, weighted IRR 9.17%, base-case IRR 9.04%**
- **Tier by numbers: D.** Diagnostics (key_numbers.md): OE yield 4.57%, terminal value 20.0% of IV@15%, scenario spread 3.10x, net debt 8.9x normalized OE, 9.4 months since FY end.
- The decisive fact: even the super-bull scenario (15% growth start, 1.25× OE) yields only a 12.96% IRR at $71.06 — no scenario in the set clears Andrew's 15% hurdle at this price.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.4 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, quoted in full above (OCF/capex/SBC/shares inputs and periods).
- **HIGH_NET_DEBT** (net debt 8.9x normalized OE in the final run's diagnostics; $13.282B net debt): real and central to the verdict. Q2 2026 reporting put net leverage at 4.1x (down from 4.6x) on the company's adjusted-EBITDA basis, and management targets investment-grade leverage by 2028 — but on an owner's-earnings basis the load is heavy, interest consumes a large share of cash flow before equity holders, and it is why the bear/super-bear scenarios carry 35% combined weight and why no tier credit is given for the deleveraging path until it happens. The leverage does not change the direction of the verdict: the weighted IV is roughly half the price even before any distress assumption.
- **WIDE_SCENARIO_SPREAD** (raised on the preliminary run at 4.4x; 3.10x on the final run): the spread narrowed with the recalibrated growth starts but the outcome range is still wide ($18.69–$58.03 IV@15%). Confidence is therefore not high — it is set to medium — and the verdict is sized to the weighted/conservative end, not the bull cases.

## My thoughts / overlay
- Quality is not the debate: this is a real franchisor with durable royalties, 5/5 OE-positive years, a working Burger King turnaround, and a credible 8% AOI algorithm. The debate is purely price: at $71.06 the market is paying for growth and cash conversion well above what the filing-derived OE base ($3.25/share TTM, a 4.57% OE yield) can return at a 15% hurdle.
- Method range: the preliminary run (3-yr median base $2.49/share, engine-default growth) gave weighted IRR 8.86% / Tier D; the final run (TTM base, recalibrated organic growth) gives 9.17% / Tier D. The tier is stable across the defensible bases tried; what moves is only how far below the hurdle it sits.
- Hurdle-clearing price: the weighted IV@15% is $36.22 — that is the price at which the weighted case clears 15%. With a margin of safety against the bear cases (bear IV@15% $26.80), a buyer demanding 15% with protection would need a price in the high-$20s to mid-$30s — roughly half the current quote. Even at the IV@12% of $48.73 the stock would only clear a 12% hurdle on the weighted case.
- Watch items that could change the picture: Popeyes US comparable-sales recovery, Tim Hortons Canada re-acceleration, the pace of Restaurant Holdings refranchising (which would cut reported capex and lift franchisor-pure OE), and deleveraging toward the 2028 investment-grade target.

## Final verdict
- **Final tier: D** (weighted IRR 9.17% on the v5 final inputs; no scenario clears 15% at $71.06)
- Confidence: **Medium** (high on the TTM filing base and the leverage picture; the scenario spread is still 3.10x, so not high)
- One-liner: Quality franchisor, moat 6/10, but priced for far more than its OE delivers — weighted IRR 9.2%, IV@15% $36.22 vs $71.06 price; clears 15% only near $36, and with a margin of safety in the high-$20s to mid-$30s.
