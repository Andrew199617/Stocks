# MKC — McCormick & Company, Incorporated
Pass-1 run, 2026-10-18, engine 5.4.0. Price $46.35 (nasdaq_quote_api), market cap $12.487B — in scope under $40B. **This DCF values standalone McCormick on the current share count; it does NOT model the pending Unilever Foods combination (see Overlay), which would roughly triple the share count. Treat every per-share figure as standalone-only.**

All figures below are copied from dcf_numbers.json, ttm.json, financials_history.csv, or fundamentals.json — none are recomputed.

## What it is
The world's largest spices/seasonings company: consumer brands (McCormick, Lawry's, Frank's RedHot, French's, Cholula) plus Flavor Solutions selling flavor systems to packaged-food makers and foodservice. Fy ends Nov 30. In FY2025 it bought out the remaining stake in McCormick de Mexico, which is now consolidated and dominates reported FY2026 growth.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $962.2M; capex $221.8M; SBC $46.2M (always a real cost).
- **Conservative owner's earnings FY2025: $694.2M = $2.58/share**
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $889.0M total — above the conservative figure, helped by a working-capital release; the OCF-based conservative figure is the one used.
- OE positive 5 of the last 5 fiscal years. Net debt $3,900.4M (debt $3,996.3M less cash $95.9M); lease liabilities $226.6M on top. Dividend: DPS TTM $1.83, 5-yr DPS CAGR 7.6% (fundamentals.json).
- OE/share history is working-capital noisy: FY21 $1.79, FY22 $1.22 (WC build), FY23 $3.37 (WC release), FY24 $2.22, FY25 $2.58. No single year is trustworthy — see NI_OCF_DIVERGENCE below.

**Base used = TTM owner's earnings through Q3 FY2026 (period ended 2026-08-31), from ttm.py (filing-direct, no hand math):**
- OCF: FY $962.2M − prior YTD $420.2M + current YTD $598.8M = **TTM $1,140.8M**
- Capex: FY $221.8M − prior YTD $138.1M + current YTD $131.2M = **TTM $214.9M**
- SBC: FY $46.2M − prior YTD $37.3M + current YTD $34.5M = **TTM $43.4M**
- Shares (current-YTD weighted diluted): **269.3M**
- **TTM OE total $882.5M → base OE/share $3.28** (base_source: ttm_json)
- Why TTM over the engine's normalized base ($2.58, median of FY23–25): the TTM window is the first that fully consolidates McCormick de Mexico, a permanent step-up in the earnings base, and FY2026 adjusted EPS guidance of $3.05–$3.13 (reaffirmed with Q3 FY26 results, 2026-10-01) corroborates ~$3+ of per-share earnings power. The median base is retained as the method-range low end below — it produces the same tier.

## Moat: 5/10 — moderate/narrow
Justification: category-defining brands and real, repeatedly demonstrated pricing power, but measured returns on capital sit at roughly the cost of capital — ROIC (fundamentals.json roic_proxy) ran 9.5% / 8.5% / 7.2% / 8.1% / 8.9% / 8.7% across FY2020–FY2025, and goodwill is ~40% of assets because growth has been bought (Frank's/French's, Cholula, Mexico) rather than compounded organically. Gross margin: 41.1% FY20 → 35.8% FY22 trough → 37.9% FY25 → 39.1% TTM, with Q3 FY26 +190bp YoY — recovering, not expanding to new highs.
- FOR: #1 global position in spices/seasonings with unmatched retail shelf presence and distribution; proven pricing power (Q3 FY26 price +2.2% with gross margin +190bp despite 6–7% guided cost inflation); Flavor Solutions B2B embeddedness with packaged-food manufacturers; brand portfolio breadth across consumer and foodservice channels.
- AGAINST: ROIC ~8–9% is at/barely above the cost of capital through the cycle — the brand earns its keep, not a wide surplus; organic growth is only 1–3% (FY26 guided) with volume/mix negative (−0.3% in Q3 FY26) — growth has come from pricing and M&A; private-label and retailer pressure in a low-switching-cost category; commodity/freight cost exposure (6–7% cost inflation guided for FY26); goodwill ~40% of assets — the balance sheet carries the acquisition strategy.
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — final run (2026-10-18)
Growth sanity check: the engine's blended start is 2.22% (rev CAGR 5y 4.08%, 3y 2.51%, latest FY YoY 1.73%, OE/share CAGR 2y −12.59% — the last is a base effect off the WC-flattered FY23, not a trend). Against actual prints: Q3 FY26 reported sales +17.4% but organic only +1.9%; FY26 guidance is organic +1–3% with reported +13–17% almost entirely the one-time Mexico consolidation step. Reported growth is therefore NOT a run-rate, and scenario starts were set on organic OE/share terms with compressed offsets (−0.10 / −0.05 / 0 / +0.04 / +0.08 vs the blended start) — even the super-bull start of 10.2% already assumes Mexico synergies, continued pricing, and margin recovery stacking for years. Probabilities tilted bear-ward (15/30/30/15/10, 45% bear-or-worse) for the 4.4x leverage and the deal overhang. OE multipliers are the defaults 0.75/0.90/1.00/1.10/1.25. Price $46.35.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | −7.8% | 0.75 | Volumes keep sliding, cost inflation sticks, deal closes on dilutive terms or breaks with costs sunk | $13.10 | 5.65% |
| Bear | 30% | −2.8% | 0.90 | Organic ~0%, pricing exhausted, leverage forces caution | $19.40 | 7.51% |
| Base | 30% | 2.2% | 1.00 | Guided organic 1–3% with Mexico consolidated; margins hold ~39% | $26.56 | 9.65% |
| Bull | 15% | 6.2% | 1.10 | Pricing + volume recovery + Mexico synergies compound | $34.50 | 11.90% |
| Super bull | 10% | 10.2% | 1.25 | Sustained high-single-digit OE growth — above anything organic prints support today | $46.24 | 14.97% |

- **Probability-weighted: IV@15% $25.55 (−44.9% vs price), IV@12% $33.61, weighted IRR 9.39%, base-case IRR 9.65%**
- **Tier by numbers: D.** Diagnostics (dcf_numbers.json): OE yield 7.07%, terminal value 17.8% of IV@15%, scenario spread 3.53x, net debt 4.42x normalized (TTM) OE, 10.6 months since FY end.
- Hurdle-clearing prices (weighted): clears 15% only at/below **$25.55**, 20% at $18.26, 25% at $14.21 — i.e., roughly half the current price for a 15% return.

## Flags — every fragility flag resolved
- **STALE_FY** (latest FY ended 10.6 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q3 FY2026, legs quoted above.
- **NI_OCF_DIVERGENCE** (2023: OCF $1,237.3M vs NI $680.6M): the gap is D&A ($199.3M) plus a large working-capital release — inventories drawn down after the FY2022 supply-chain build (the mirror image of FY21–22, when WC build crushed OCF-based OE to $1.79/$1.22 per share). No impairment or tax-deposit one-off is involved. Consequence: FY23's OE/share of $3.37 is WC-flattered, which is why the 2-yr OE/share CAGR prints −12.59% and why neither the FY23 year nor the median is treated as clean. The TTM base spans a full four quarters of the same WC cycle, which dampens (does not eliminate) the noise.
- **HIGH_NET_DEBT** (net debt 4.42x TTM-normalized OE; 5.62x on the median base): real leverage from the acquisition strategy, most recently the Mexico buyout. Balance sheet per FY25 10-K figures in the history file: total debt $3,996.3M, cash $95.9M, plus $226.6M lease liabilities. Management guided to repaying $1.5–2.0B of debt over two years (Q3 FY26 coverage). Handled by 45% probability on bear-or-worse and the 0.75 super-bear OE multiplier.
- **TIER_BAND** (bear tier D at 7.51% vs bull tier C at 11.90%): the verdict is sized to the bear end — final tier D.
- **WIDE_SCENARIO_SPREAD** (preliminary run, 4.52x): narrowed to 3.53x in the final run once scenario starts were recalibrated to organic reality, but the range is still wide and the pending deal (below) is unmodelable — confidence is **low**, not medium.
- History caveat (not engine-flagged): pre-2021 per-share figures in the raw EDGAR pull sit on the pre-split share basis (a 2-for-1 split was re-filed in Jan 2021; fundamentals.json documents it) — FY16–17 share counts print ~128M vs ~269M today. The base uses only FY23–25 and the TTM window, so this does not touch the score; it only means the long OE/share history overstates early per-share figures ~2x.

## My thoughts / overlay
- **The Unilever deal dominates everything and is not in these numbers.** Announced 2026-03-31: McCormick combines with Unilever's Foods business (Hellmann's, Knorr) in a $44.8B-EV transaction — $15.7B cash plus $29.1B in McCormick shares; Unilever and its shareholders end up with ~65% of the combined company, current MKC holders ~35%; ~$20B combined revenue; close targeted mid-2027, with $600M of expected run-rate cost synergies cited in Q3 FY26 coverage. The UK CMA opened a Phase 1 investigation in Sept 2026 (preliminary ruling expected by 2026-11-11 per press coverage), and remedies (e.g., Colman's) are reportedly under discussion. A standalone DCF on 269M shares cannot price a claim that becomes 35% of a ~3x-larger, more levered company; whether the deal creates or destroys per-share value depends on the exchange economics and synergies, not on standalone MKC cash flows. This is the main reason confidence is low.
- **Method range:** the preliminary run on the median base ($2.58/share, default probs/offsets) gave weighted IRR 8.61% and IV@15% $22.38 — also Tier D. The TTM base lifts the weighted IRR to 9.39%. Both defensible bases land in D; the tier is robust even though the exact IRR is base-sensitive.
- Quality is not the debate — this is a durable, dividend-growing staples franchise (DPS +7.6%/yr over 5 years) whose organic engine runs at 1–3%. The debate is price: at $46.35 the market is paying for the deal option and a growth rate the standalone business has never organically printed. Even the super-bull scenario (10.2% OE growth start, 1.25x OE) only reaches a 14.97% IRR — it does not clear the 15% hurdle.
- Risks: deal break or punitive remedies; integration leverage if it closes; continued volume decline if pricing has exhausted elasticity; commodity inflation running ahead of pricing.

## Final verdict
- **Final tier: D** (weighted IRR 9.39% on the TTM base; median base gives 8.61% — D either way; sized to the bear end of the D–C band)
- Confidence: **Low** (standalone cash flows are well-evidenced, but the pending Unilever combination — unmodelable in this framework — will decide what a share actually claims)
- One-liner: Durable spice/flavor franchise, moat 5/10, but at $46.35 it doesn't clear 15% on any defensible standalone base (weighted IRR 9.4%, IV@15% $25.55; clears 15% only below ~$26) — and the pending Unilever deal, not standalone DCF value, is what the price is really trading on.
