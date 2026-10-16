# SNA — Snap-on Inc
v5 run, 2026-10-16. In scope (market cap $19.644B at $370.65, nasdaq_quote_api). All DCF figures below are copied from dcf_numbers.json, ttm.json / ttm.py output, or financials_history.csv — none are recomputed. Research figures are attributed where they appear.

## What it is
Premium professional tools, equipment, diagnostics and repair-information systems, founded 1920, sold in ~130 countries. Four segments: Commercial & Industrial Group (direct/distributor channels to industrial, government, aviation, natural-resource customers), Snap-on Tools Group (the franchise van channel to vehicle-repair technicians — the largest block, ~38% of consolidated revenues per the FY2025 10-K), Repair Systems & Information Group (diagnostics, repair data, shop management systems, OEM dealership equipment), and Financial Services (captive financing for franchisees and for technicians buying on extended-term plans). Morningstar estimates ~60% share of US mobile tool distribution.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** net sales $4,709,300,000; net income $1,016,900,000; operating cash flow $1,081,700,000; SBC $28,900,000 (always a real cost); capex $76,000,000 — by override, see OVERRIDE.
- **Conservative owner's earnings FY2025: $976,800,000 = $18.43/share** (base_oe_latest_per_share in dcf_numbers.json).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $847,000,000 — below the conservative figure mainly because FY2025 carries a ΔNWC of $192,400,000 in the CSV; the OCF-based conservative figure is the cleaner base.
- OE positive 5 of the last 5 fiscal years. Net debt is **negative: −$438,100,000 (net cash)** — see Thoughts for why that does not move the verdict.
- Growth history (dcf_numbers.json): revenue CAGR 5-yr 5.70%, 3-yr 1.76%, latest FY YoY +0.68%; OE/share CAGR (2-yr) −1.95%; blended growth 1.22% plus a +0.74pp share-count adjustment (share count −0.74%/yr on buybacks) gives the engine base growth of 1.96%.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $1,081,700,000 − prior YTD $535,700,000 + current YTD $640,200,000 = **TTM $1,186,200,000**
- Capex: **TTM $77,249,315**, all three legs filled by the override (see OVERRIDE)
- SBC: FY $28,900,000 − prior YTD $13,000,000 + current YTD $16,200,000 = **TTM $32,100,000**
- Shares (current-YTD weighted diluted): **52,611,800**
- **TTM OE total $1,076,850,685 → base OE/share $20.47** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $19.17/share. The TTM base was used because the FY is 9.4 months stale and H1 2026 OCF ran ahead of H1 2025; the median is retained in the reporting — and using it would only lower the IRR further (see method range under Thoughts).

## OVERRIDE — capex (filing-sourced, bounded authority)
- **The gap:** Snap-on files no capex under any candidate tag the engine reads, in any year. The preliminary engine run exited 4 with `DATA_GAP:capex` (missing for FY2023, FY2024 and FY2025 of the last 3) — no tier, correctly.
- **The decision (worker, under the 2026-10-14 bounded authority, kind "filing"):** judgment.json carries `capex_override = {value: 76000000, kind: "filing", source: "Form 10-K for fiscal year ended January 3, 2026 (filed 2026-02-12, accession 0000091440-26-000045), Consolidated Statements of Cash Flows, investing activities line 'Capital expenditures' tagged us-gaap:PaymentsForCapitalImprovements (a tag the engine does not read): $76.0M for FY2025, with $83.5M for FY2024 and $95.0M for FY2023 in the same statement; corroborated in EDGAR companyfacts under PaymentsForCapitalImprovements with identical values"}`. Snap-on reports capex only under PaymentsForCapitalImprovements; the FY2025 10-K's own statement gives all three missing years ($95.0M / $83.5M / $76.0M).
- **Distortions, disclosed:** the engine applies the single $76.0M value to every missing period (in fact every history year — capex_tag = "OVERRIDE" throughout financials_history.csv). Against the filer's true per-year values it understates FY2023 capex by $19.0M and FY2024 by $7.5M, raising those years' OE by ~1.9% / ~0.7%; true historical values under the same tag for 2016–2022 run $65.6M–$99.4M, the same magnitude, so no historical year is distorted by more than ~$23M. On the binding TTM base the applied capex is $77,249,315 (ttm.py prorates the 371-day FY leg) vs a true filed-leg TTM of $77.7M (FY2025 $76.0M − H1 2025 $42.6M + H1 2026 $44.3M under the same tag) — a ~$0.5M difference, ~0.05% of TTM OE.
- **Out-of-band flag:** mechanical only — the band anchors on the last value filed under an engine-read tag, and none exists (last_filed_value: null). judgment.json carries an ack_reason stating exactly that; the value itself is the filer's own filed figure, not an estimate.
- **Measured impact (key_numbers.md, on the TTM base actually used):** base OE/share $21.94 (no override) → $20.47 (with override), −6.69%; weighted IRR 9.05% → 8.62% (−0.43pp); **unblocks_tier: YES** — the override is the only reason this company has a tier. (The engine-native measurement in dcf_numbers.json, on the median base, moves weighted IRR 8.66% → 8.62%.) Every variant lands in Tier D; the override's binding effect is that a tier exists at all, and it moves the TTM base in the conservative direction.

## Moat: 7/10 — strong
Justification: dominant (~60%) share of US mobile tool distribution through a franchise van network whose weekly in-person, consultative sales are notoriously sticky; a century-old premium brand with proven pricing power (gross margin above 50%); and a captive Financial Services arm that finances both franchisees and technicians and locks the channel together. Diagnostics/repair-information adds software and data exposure. Erosion forces are real but slow: franchisee dependence, discretionary big-ticket demand tied to technician confidence, lower-cost premium-price competition, the EV/ADAS product shift, finance-receivable credit cycles, and mature end markets growing under 2% on a 3-yr view.
- FOR: ~60% share of US mobile tool distribution; franchise van network with sticky weekly in-person sales; premium brand with proven pricing power — gross margin above 50%; captive Financial Services flywheel financing franchisees and technicians, locking in the channel; diagnostics and repair-information systems (software, data, OEM dealership tools) diversify beyond hand tools; net cash balance sheet; owner's earnings positive 5 of the last 5 fiscal years.
- AGAINST: franchisee dependence — franchisee failure hits sales, collections and finance receivables; big-ticket tool demand is discretionary and moves with technician confidence and hours; premium pricing faces lower-cost rivals (Harbor Freight, Milwaukee, Matco/Cornwell); EV/ADAS shift needs constant diagnostics reinvestment and fewer mechanical repairs per vehicle over time; captive finance carries credit-cycle risk — loan-loss provisions rise in downturns; mature end markets — 3-yr revenue CAGR under 2%.
- A 7 gives CAP = 11.1 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 11.1 years, 15-year projection.

## DCF — v5 final run (2026-10-16)
Final pass: `dcf_engine.py SNA --moat 7 --probs 0.10,0.25,0.30,0.25,0.10 --ttm`, default offsets (−12/−5/0/+5/+12pp) and default OE multipliers (0.75/0.90/1.00/1.10/1.25) around the engine base growth of 1.96%. Price $370.65.

**Sanity check against actual prints:** Q2 2026 (company release, Jul 23 2026): net sales $1,235.1M, +4.7% reported — +3.0% organic, plus $11.5M acquisition sales and $8.7M favorable FX; gross margin 51.4% vs 50.5%; diluted EPS $4.96 vs $4.72; Financial Services revenue $99.7M vs $101.7M a year ago. Two written reasons on the starts: (1) the **base start (1.96%) sits below Q2's +3.0% organic print** because the blend is a median of slower filing signals (3-yr revenue CAGR 1.76%, latest FY YoY +0.68%, OE/share CAGR −1.95%) and Q2's reported gain was flattered by acquisitions and FX — one quarter does not reset a mature grower's trend; (2) the **super-bull start (13.96%) is roughly 3x the latest organic print by construction** — it is the default +12pp scenario bound, not a forecast, and it is kept deliberately: even granting it, the stock does not clear 15% (see table), so the verdict does not rest on taming the bull case. No growth-cap artifact is present (base growth is far from the 35% cap).

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -10.0% | 0.75 | Technician recession; big-ticket deferral, finance losses rise | $70.40 | 4.35% |
| Bear | 25% | -3.0% | 0.90 | Flat-to-down sales, premium price pressure | $116.49 | 6.13% |
| Base | 30% | 2.0% | 1.00 | Mature GDP-ish growth, buybacks continue | $163.62 | 7.99% |
| Bull | 25% | 7.0% | 1.10 | C&I + diagnostics momentum compounds | $227.96 | 10.39% |
| Super bull | 10% | 14.0% | 1.25 | Sustained high-single-digit-plus growth at premium margins | $361.25 | 14.73% |

- **Probability-weighted: IV@15% $178.36 (−51.9% vs price), IV@12% $236.48, IV@10% $301.31, weighted IRR 8.62%, base-case IRR 7.99%**
- **Tier by numbers: D.** Diagnostics (dcf_numbers.json): OE yield 5.52%, terminal value 18.60% of IV@15% (low — the shortfall is not a terminal-value artifact), scenario spread 5.13x, net debt −0.40x normalized OE (net cash), 9.4 months since FY end.

## Flags — every fragility flag resolved
- **DATA_GAP:capex** (preliminary run): resolved by the filing-sourced override above; final dcf_numbers.json has data_gap_uncovered = [] and the tier is emitted on filed figures, not a zero-fill.
- **STALE_FY** (FY ended 9.4 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, inputs quoted above.
- **OVERRIDE_APPLIED:capex**: see OVERRIDE — gap, decision, distortions, out-of-band explanation and measured impact are all recorded in fields (judgment.json, dcf_numbers.json overrides_applied / override_impact, overrides_registry.json), not just here.
- **WIDE_SCENARIO_SPREAD** (5.13x): real but partly mechanical — on a ~2% base grower, the default scenario fan (−10% to +14% starts, 0.75x–1.25x OE) mechanically spans a wide IV range. Confidence is set to medium (never high under this flag), and the verdict is sized to the conservative end — which changes nothing here, because even the super-bull end fails the hurdle.

## My thoughts / overlay
- The honest headline is the gap between quality and price: this is a strong-moat, net-cash, 5/5-positive-OE compounder priced as if its growth were much faster than its filings show. At $370.65 the OE yield is 5.52% and the weighted IRR is 8.62%; even the super-bull scenario (14.0% growth start, 1.25x OE) returns only 14.73% and its IV@15% ($361.25) still sits below the price.
- Method range is narrow on the verdict, unlike the scenario range: without the capex override the TTM base prints $21.94/sh and a 9.05% weighted IRR (key_numbers.md) vs $20.47/sh and 8.62% with it, and the median base ($19.17/sh vs TTM $20.47/sh) would print lower still. Every defensible base lands in Tier D — the D is a price finding, not a method artifact.
- Balance sheet folded in explicitly: net cash of $438,100,000 (−0.40x normalized OE) is a genuine quality point, but at ~2% of the $19.644B market cap it cannot close a ~52% valuation gap. FY2025 capital returns (dividends and buybacks, per the 10-K cash-flow statement) are funded comfortably by the $976.8M conservative OE; that supports the base case, not a re-rating.
- Financial Services cuts both ways and is not separately modelled (the engine runs consolidated OCF): it is a high-margin flywheel in good times and the main credit-loss channel in bad ones — one reason the bear weights total 35%.
- **Hurdle-clearing price:** the weighted IV@15% is **$178.36** — SNA clears Andrew's 15% hurdle only at/below roughly half the current price. With a margin of safety against the bear cases (bear IV@15% $116.49), a buyer is not paid for anything close to the base case until well under $178.

## Final verdict
- **Final tier: D** (weighted IRR 8.62% on the v5 final inputs; no tier override — the numbers tier stands)
- Confidence: **Medium** (high on the business and the filing-sourced base; capped by WIDE_SCENARIO_SPREAD)
- One-liner: High-quality premium tool franchise, moat 7/10 — but at $370.65 the weighted IRR is only 8.6% (Tier D, IV@15% $178.36); it clears the 15% hurdle only at roughly half the current price.
