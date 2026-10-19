# SGI — SomniGroup International Inc.
Pass-1 run, 2026-10-17. Engine 5.4.0. Price $63.58 (nasdaq_quote_api); market cap $13.30B — in scope under $40B.

All figures below are copied from dcf_numbers.json, ttm.json, financials_history.csv, or fundamentals.json — none are recomputed.

## What it is
The renamed Tempur Sealy: the largest US bedding maker (Tempur-Pedic, Sealy Posturepedic, Stearns & Foster) that bought its largest customer, Mattress Firm, on Feb 5, 2025 for ~$5.1B (~$3.1B cash + 34.2M shares), becoming a vertically integrated manufacturer-retailer with 2,852 company-owned stores (2,174 Mattress Firm) at Dec 31, 2025, plus Dreams in the UK. That acquisition — not organic growth — explains almost every distorted input in this run. A second deal followed after the TTM window: the all-stock Leggett & Platt combination closed Aug 26, 2026 (per company/Wikipedia reporting), issuing shares not yet in any figure below.

## Owner's earnings
**FY2025 (10-K via EDGAR, financials_history.csv):** OCF $800,100,000; capex $166,900,000; SBC $41,000,000.
- **Conservative OE FY2025: $592,200,000 = $2.83/share** (latest FY OE/share; also the 3-yr median, because FY2025 is the median year).
- Maintenance version FY2025: −$690,900,000 — meaningless here: its ΔNWC leg (+$1,198,600,000) is the Mattress Firm balance-sheet consolidation, not operations. The OCF-based conservative figure is the usable one.
- OE positive 5 of the last 5 fiscal years, but violently cyclical: OE/share $2.64 (2021) → $0.11 (2022) → $1.90 (2023) → $2.99 (2024) → $2.83 (2025).
- Net debt $4,550,800,000 plus operating lease liabilities $1,989,400,000 (dcf_numbers.json). Goodwill jumped to 39.6% of assets in FY2025 (fundamentals.json) — the acquisition premium sits on the balance sheet.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $800,100,000 − prior YTD $292,500,000 + current YTD $482,800,000 = **TTM $990,400,000**
- Capex: FY $166,900,000 − prior YTD $60,700,000 + current YTD $115,200,000 = **TTM $221,400,000**
- SBC: FY $41,000,000 − prior YTD $18,500,000 + current YTD $22,600,000 = **TTM $45,100,000**
- Shares (current-YTD weighted diluted): **212,600,000**
- **TTM OE total $723,900,000 → base OE/share $3.40** (base_source: ttm_json)
- Why TTM over the FY/median base ($2.83): FY2025 holds only ~11 months of Mattress Firm and its stub-period eliminations; the TTM window is the first clean full-ownership period, and Q2 2026 was a record cash-flow quarter (OCF $236M in the quarter per the Q2 release). The LEG share issuance (closed Aug 26, 2026) post-dates the TTM share count — a real, unquantified-in-these-filings dilution overhang that argues for the conservative scenario weights below, and is one reason confidence is low.

## Moat: 5/10 — moderate/narrow
Justification: leading premium brands with real pricing power and now unmatched US distribution, but a cyclical, low-switching-cost product, a falling measured ROIC, and a low-margin retail segment diluting the manufacturing franchise.
- Evidence (fundamentals.json): ROIC proxy 29.9% (2021) → 19.9% (2022) → 16.8% (2023) → 11.4% (2024) → 7.9% (2025). The pre-acquisition manufacturing business earned well above its cost of capital; the 2025 print is depressed by the acquisition-inflated capital base (goodwill 39.6% of assets) and stub economics, but the five-year trend is down either way. Consolidated gross margin has held ~40.3–44.6% over the last five fiscal years (42.6% in FY2025) — brand pricing power is real at the manufacturing level (North America adjusted gross margin 61.8% in Q2 2026 per the Q2 release), while Mattress Firm retail runs ~33% gross margin and drags the blend.
- FOR: #1 US bedding share with Tempur-Pedic / Sealy / Stearns & Foster premium brands and demonstrated pricing power; vertical integration — Tempur Sealy brands are now >50% of Mattress Firm sales, capturing retail margin and shelf control no rival manufacturer has; scale in manufacturing, logistics and advertising (~$690M planned 2026 ad spend) across 2,852 stores; Mattress Firm same-store sales flat in Q1 2026 against an industry management believes was down mid-single digits — share is being taken.
- AGAINST: mattresses are a deferrable, housing-linked discretionary purchase with near-zero switching costs; DTC and private-label rivals (and other retailers' multi-brand floors) cap pricing; measured ROIC has fallen every year since 2021 and the retail segment structurally earns less than the manufacturing it replaced on the income statement; goodwill at 39.6% of assets is an impairment exposure if synergies disappoint; the LEG combination adds a second integration on top of an unfinished first one.
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — final run (2026-10-17)
**Growth recalibration (mandatory sanity check, written reason):** the engine's blended start is 16.12%, built on acquisition artifacts — latest revenue YoY +51.63% is the Mattress Firm consolidation (organic revenue was flat at ~$4.93B for four straight years, FY2021–FY2024), and the 5-yr/3-yr revenue CAGRs (15.25% / 14.96%) straddle the deal. Organic prints say something else entirely: Q1 2026 reported sales +12.3% only on the stub comparison with like-for-like roughly flat; Q2 2026 sales −3.0% YoY; 2026 guidance (cut at Q2) is ~$7.6B of sales vs $7.48B in FY2025, adjusted EPS $2.85–$3.15, on an industry expected to decline mid-single digits. OE/share growth can still outrun revenue near-term via the $100M synergy run-rate targeted by 2028, mix shift to Tempur Sealy brands inside Mattress Firm, and deleveraging (leverage 2.99x adj. EBITDA at Q2 2026, down from 3.56x a year earlier) — so scenario starts were set via offsets (−0.181 / −0.141 / −0.111 / −0.061 / −0.001 vs the blended 16.12%) to −2.0 / +2.0 / **+5.0** / +10.0 / +16.0%. Probabilities widened toward the bear end (15/30/30/17/8 vs the 10/25/30/25/10 default) per OE_VOLATILE and HIGH_NET_DEBT. OE multipliers are the defaults 0.75/0.90/1.00/1.10/1.25. Base OE/share $3.40 (TTM, above). Price $63.58.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | −2.0% | 0.75 | Industry slump persists; MF deleverages the P&L the wrong way; LEG integration distracts; levered OE shrinks | $17.37 | 5.76% |
| Bear | 30% | 2.0% | 0.90 | Flat-to-down industry through the fade; synergies mostly offset volume decline | $24.63 | 7.32% |
| Base | 30% | 5.0% | 1.00 | Guidance path: low-single-digit organic growth plus synergy/mix OE leverage | $31.00 | 8.69% |
| Bull | 17% | 10.0% | 1.10 | Housing/bedding cycle recovers; $100M synergies land; share gains compound | $41.93 | 10.97% |
| Super bull | 8% | 16.0% | 1.25 | Full cycle recovery plus LEG synergies — management's $5.15 2028 EPS ambition, roughly | $60.90 | 14.53% |

- **Probability-weighted: IV@15% $31.29 (−50.8% vs price), IV@12% $41.60, IV@10% $53.10, weighted IRR 8.80%, base-case IRR 8.69%**
- **Tier by numbers: D.** Diagnostics (dcf_numbers.json): OE yield 5.36%, terminal value 18.8% of IV@15%, scenario spread 3.51x, net debt 6.39x normalized OE, 9.5 months since FY end.
- Hurdle-clearing prices (weighted): 15% at $31.29, 20% at $22.04, 25% at $16.94. Even the super-bull IV@15% ($60.90) sits below the $63.58 price.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.5 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, legs quoted above.
- **DILUTION** (share count +5.1%/yr): the trend is deal issuance, not SBC creep — 34.2M shares issued for Mattress Firm in Feb 2025 took diluted shares from 178.2M (FY2024) to 209.2M (FY2025); SBC itself is small and stable ($41.0M FY2025, $45.1M TTM, ~5% of OCF) and is deducted in OE throughout. The −5pp growth adjustment is retained as a further haircut. Forward warning: the all-stock LEG deal closed Aug 26, 2026, after the TTM share count (212.6M) — pro-forma dilution is NOT in these numbers and cuts against the bull cases.
- **OE_VOLATILE** (OE/share spans >3x over 5 years): real cyclicality — $0.11/share in the 2022 bedding downturn vs $2.99 in 2024. Handled with bear-weighted probabilities (45% on bear-or-worse) and a super-bear OE multiplier of 0.75; the TTM base is a mid-cycle-ish print, not a peak (2024 was higher on the old share count).
- **NI_OCF_DIVERGENCE** (>40% in 2024, 2025): identified — FY2025 net income $384.1M vs OCF $800.1M, and FY2024 $384.3M vs $666.5M. The gap is non-cash and deal-driven: D&A of $290.5M in FY2025 (acquired intangibles/store base), Mattress Firm transaction and integration costs running through net income, and acquisition working-capital consolidation (the maintenance-OE ΔNWC legs of −$1.72B in 2024 and +$1.20B in 2025 are balance-sheet effects, not operations). The OCF-based conservative OE used throughout is not contaminated by the NI-side charges; if anything it is the cleaner series.
- **HIGH_NET_DEBT** (6.39x normalized OE on the final run; 7.68x on the preliminary): balance sheet stated from the filing — total debt $4,685.7M against cash $134.9M = net debt $4,550.8M, plus $1,989.4M operating lease liabilities on 2,852 stores (dcf_numbers.json / financials_history.csv FY2025). On the company's own measure, leverage was 2.99x trailing adj. EBITDA at Q2 2026, down from 3.56x, with net debt down >$500M over the trailing year per the Q2 release — deleveraging is happening, but at $63.58 the equity is a levered stub: the bear cases (45% weight) are sized accordingly.
- **TIER_BAND** (bear D 7.32% vs bull C 10.97%): the verdict is sized to the bear end — the final tier is D on the weighted figure (8.80%), and no scenario reaches the 15% hurdle.
- **WIDE_SCENARIO_SPREAD** (preliminary run, 4.41x): after recalibration the spread is 3.51x and the flag cleared, but the range is still wide for a levered cyclical — confidence is capped at low, not medium-high.
- **Basis break (not engine-flagged, resolved here):** the Feb 2025 Mattress Firm consolidation breaks revenue, share-count and balance-sheet comparability at FY2025. All growth inputs were re-anchored to post-deal organic evidence (quarterly prints and 2026 guidance) rather than any CAGR straddling the deal — see the recalibration note above.

## My thoughts / overlay
- The market is pricing SGI as a synergy-and-recovery story: at $63.58 the stock needs roughly the super-bull path (16% OE/share growth start, 1.25x OE) just to reach a 15% return — and that path is management's own 2028 EPS ambition, before any haircut for the LEG shares issued in August 2026 that these filings don't yet count.
- Quality is mixed, not bad: the manufacturing core earned 17–30% ROIC through 2023 and still holds ~58–62% adjusted gross margins in North America; what's changed is that the equity now sits behind $4.55B of net debt plus $1.99B of leases, a 39.6%-of-assets goodwill pile, and a low-margin retail segment, in an industry management itself expects to shrink mid-single digits in 2026.
- Method range: on the engine's unadjusted preliminary inputs (median base $2.83, 16.12% blended growth) the weighted IRR printed 11.44% (Tier C) — that run capitalizes acquisition growth as if it were organic and is not defensible. On the filing-clean TTM base with organic growth, the answer is 8.80% (Tier D). Both runs agree on the only thing that matters: at $63.58 the stock does not clear 15% under any defensible method; it clears 15% only below ~$31.
- Dividend: $0.64/share TTM declared (fundamentals.json) — a ~1% yield, not a reason to own it at this price.

## Final verdict
- **Final tier: D** (weighted IRR 8.80% on the TTM base with organic growth inputs; bear D 7.32%, bull C 10.97% — sized to the bear end)
- Confidence: **Low** (post-acquisition basis break, LEG dilution not yet in any filing figure, levered balance sheet, cyclical industry in decline)
- One-liner: Good brands, moderate moat 5/10, now a levered retailer-manufacturer — at $63.58 it prices in the synergy/recovery story and returns only 8.8% weighted; it clears 15% only at ~$31.
