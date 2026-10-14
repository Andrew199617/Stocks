# Ingersoll Rand Inc. (IR) — Owner's-Earnings DCF

**Date:** 2026-10-14 · **Price:** $78.43 · **Market cap (engine est.):** $31.44B · **Tier: D** (weighted IRR 8.22%)

## What it is

Ingersoll Rand is a global industrial flow-creation company formed in its current shape by the 2020 Gardner Denver merger: air compressors, blowers, vacuum systems, fluid-handling and life-science equipment, sold under brands including Ingersoll Rand, Gardner Denver, CompAir and Thomas. Two segments — Industrial Technologies & Services (the compressor/air-treatment core, ~79% of revenue) and Precision & Science Technologies. Roughly 37% of sales are aftermarket parts and services on a large installed base, which is the recurring, higher-margin engine. Growth is a mix of mid-single-digit organic growth plus a steady bolt-on M&A program (e.g. Lone Star Blower and Fai Filtri closed/agreed in Q2 2026; $525.0M of acquisitions in FY2025 after $2,958.7M in FY2024).

Recent prints: Q2 2026 revenue $2.05B, +8.5% YoY; adjusted EPS $0.86; adjusted EBITDA margin compressed 160bp to 25.4% on China pricing pressure, technology investment and higher corporate costs. Management raised FY2026 revenue-growth guidance to 4.5–6.5% (from 2.5–4.5%) while holding adjusted EPS guidance at $3.45–$3.57 — i.e. more volume, no more profit, until an expected H2 margin recovery. Orders were $2.04B in Q2 (+5.3% YoY, book-to-bill 1.00x), with strong July order intake as delayed long-cycle projects resumed.

## Owner's earnings

From `financials_history.csv` (SEC EDGAR, conservative = OCF − capex − SBC; maintenance = NI + D&A − min(capex, D&A) − ΔNWC):

| FY | Conservative OE | Maintenance OE |
|---|---|---|
| 2023 | $1,220.1M | $1,191.0M |
| 2024 | $1,188.8M | $1,023.2M |
| 2025 | $1,167.1M | $823.8M |

The two definitions diverge in 2025 mainly through the maintenance version's working-capital and net-income legs: FY2025 GAAP net income was hit by non-cash charges (see FLAGS), while cash OE barely moved — conservative OE has been essentially flat for three years ($1,220M → $1,189M → $1,167M) even as revenue grew from $6,876M to $7,651M. That is the central fact of this name: revenue compounds, owner's earnings do not, because acquisition amortization-era costs, margin mix and corporate spend absorb the growth.

**Base used: TTM OE/share of $2.9704** (via `--ttm`), vs the engine's median-of-last-3-FY base of $2.9194/sh. ttm.py inputs (FY2025 − H1 2025 YTD + H1 2026 YTD, all from EDGAR 10-K/10-Q YTD facts):

- OCF: FY $1,355.7M − prior YTD $502.1M + current YTD $495.6M = TTM $1,349.2M
- Capex: FY $135.6M − prior YTD $69.0M + current YTD $63.3M = TTM $129.9M
- SBC: FY $53.0M − prior YTD $30.9M + current YTD $33.7M = TTM $55.8M
- Diluted shares: FY 401.0M; current YTD weighted average 391.7M (buybacks are shrinking the count ~2%/yr)
- TTM OE total $1,163.5M → **$2.9704/sh**

The TTM base is only +1.7% above the 3-yr median, so the base choice is not the story — the price is. OE yield at $78.43 is 3.79%.

## MOAT — score 6/10 (CAP 9.8 years)

**FOR:**
- Large installed base of mission-critical compressors/vacuum equipment generating ~37% of sales as recurring aftermarket parts and service
- #2 global position in industrial air behind Atlas Copco, with multi-brand coverage (Ingersoll Rand, Gardner Denver, CompAir) across price tiers and regulated end-markets (pharma, food, life science)
- Products are mission-critical with real downtime costs for customers — service responsiveness and parts availability create switching stickiness
- Proven bolt-on M&A machine that buys aftermarket-heavy niche leaders and plugs them into the global service network
- Net cash balance sheet (net debt −$1,247.4M) funds the M&A/buyback flywheel without financial risk

**AGAINST:**
- Atlas Copco is the premium benchmark with deeper service coverage and more mature monitoring/energy-recovery tech — IR is the challenger, not the standard-setter
- China pricing pressure is actively compressing margins (adj. EBITDA margin −160bp YoY in Q2 2026)
- Equipment itself is cyclical industrial capital goods; organic IT&S growth was negative as recently as Q3 2025
- Growth is substantially bought, not organic — acquisition pace ($2,958.7M in FY2024) carries integration and goodwill risk (FY2025 already took a $273.4M impairment)
- No network effects or contractual lock-in; customers run mixed fleets and can dual-source

A solid installed-base/aftermarket moat, but contested by a stronger #1 and with margins currently moving the wrong way: 6/10, moderate-to-strong. CAP = clamp(2 + 1.3×6) = 9.8 years.

## Five scenarios (probs 10/25/30/25/10, default offsets/mults)

Engine blended base growth g_base = 8.10% (rev CAGR 5y 14.0%, 3y 8.9%, latest YoY 5.7%, OE/share CAGR 2y −1.2%, +0.75pp buyback adjustment).

| Scenario | Prob | Growth start | OE mult | IV@15% | IRR |
|---|---|---|---|---|---|
| Super bear | 10% | −3.9% | 0.75 | $13.74 | 4.49% |
| Bear | 25% | +3.1% | 0.90 | $22.52 | 6.11% |
| Base | 30% | +8.1% | 1.00 | $31.25 | 7.72% |
| Bull | 25% | +13.1% | 1.10 | $42.92 | 9.75% |
| Super bull | 10% | +20.1% | 1.25 | $66.41 | 13.37% |
| **Weighted** | | | | **$33.75** | **8.22%** |

Sanity check vs actual prints: the base start of 8.1% sits above FY2026 guided revenue growth (4.5–6.5%) but is supported by Q2 2026's +8.5% revenue print, strong July orders, and buyback-driven per-share leverage — defensible, if not conservative. The super-bull start of 20.1% is well above anything the company has printed recently (revenue +8.5%, OE/share roughly flat over 2 years); it is a genuine tail case requiring simultaneous margin recovery, M&A accretion and multiple years of double-digit orders, which is why it carries only 10% weight and the standard 1.25 multiplier rather than a recalibrated offset set — and even that tail only returns 13.37% IRR at $78.43. No recalibration was applied: lowering the bull offsets would change nothing at the tier level, since even the unadjusted super bull fails the 15% hurdle.

Diagnostics: OE yield 3.79%; terminal value share at 15% only 20.3% (the shortfall is not a terminal-value artifact — the cash flows themselves are too small for the price); scenario spread (super-bull/super-bear IV) 4.83x; net debt / normalized OE −1.05 (net cash).

## FLAGS — resolution

- **STALE_FY** (FY ended 2025-12-31, 9.4 months ago): Resolved by running ttm.py and using the `--ttm` base ($2.9704/sh, inputs quoted above). TTM OE is essentially flat vs FY2025, confirming no inflection is being missed.
- **NI_OCF_DIVERGENCE** (2023, 2025): Resolved. In 2025, GAAP net income ($581.4M per the engine file) was depressed by non-cash items that OCF adds back: a $273.4M impairment of goodwill and other intangible assets and a $127.1M loss on equity-method investments, on top of $505.8M of D&A. In 2023 the gap is mostly the same D&A-heavy reconciliation (D&A $459.1M against NI $778.7M / OCF $1,377.4M). The divergence therefore impugns GAAP net income, not the OCF-based owner's earnings — the conservative OE base is trustworthy, and the impairment is a (real) signal about past acquisition pricing, not about current cash generation.
- **WIDE_SCENARIO_SPREAD** (4.83x): Acknowledged, not removable — it reflects genuine uncertainty about whether margin recovery + M&A can re-accelerate OE off a flat 3-year base. Confidence is capped at medium, and the verdict is sized to the conservative end.

No BASE_DIVERGENCE, BASIS_BREAK_SUSPECT, HIGH_NET_DEBT or SECTOR_MODEL_MISMATCH flags. The balance sheet is a strength: net cash of $1,247.4M.

## Thoughts / overlay

This is a good business at a price that assumes a much better one. Owner's earnings have been flat for three years while the market cap is $31.4B — 27x TTM conservative OE. Method range is narrow: the median-3yr base ($2.9194/sh) produced a weighted IRR of 7.93% in the preliminary run vs 8.22% on the TTM base — Tier D under both, no defensible input set spans tiers here. Even the super-bull scenario (20.1% starting growth, 1.25x OE) values the stock at $66.41 at a 15% discount — below today's $78.43.

**Price that clears 15%:** the probability-weighted IV@15% is **$33.75**; with a ~20% margin of safety, ~$27. That is less than half the current price — the gap is too wide to be closed by any plausible near-term execution.

## Verdict

**Tier D.** Quality compounder profile (installed base, aftermarket, net cash, disciplined buybacks) but owner's earnings are flat, margins are compressing, and at $78.43 the weighted IRR is 8.22% — not even the super-bull case clears Andrew's 15% hurdle. Revisit only on a major price reset toward the mid-$30s or evidence that OE/share has actually re-accelerated for several quarters.
