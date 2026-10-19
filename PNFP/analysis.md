# PNFP — Pinnacle Financial Partners, Inc.
Engine 5.4 run, 2026-10-17. In scope (see market-cap note below). **Finance sector — the OE/capex DCF fits banks poorly; confidence is low by rule, and the tier is a screen result, not a bank valuation.**

All figures below are copied from dcf_numbers.json, financials_history.csv, ttm.json, or fundamentals.json — none are recomputed.

## What it is
Southeast regional bank holding company (SIC 6021, National Commercial Banks): banking, investment, trust, mortgage and insurance for commercial and consumer clients, headquartered in Tennessee/Georgia, No. 1 deposit share in the Nashville MSA and No. 4 in Atlanta, offices across TN, GA, FL, NC, SC, AL, KY, VA and MD. **The defining event is the merger with Synovus Financial Corp., which closed Jan. 1, 2026**: reported results for Q1/Q2 2026 are the combined organization, all prior periods are legacy Pinnacle only, and the company itself warns year-over-year comparisons are significantly impacted by the merger and purchase accounting. Combined assets were $129.1B at June 30, 2026 (company press release) vs legacy-only assets of $57,706,053,000 at FY2025 (fundamentals.json). Q2 2026: net income available to common $313M, diluted EPS $2.07 GAAP / $2.50 adjusted (excluding merger-related expenses, securities losses and other items), net interest income $956M, NIM 3.4%, tangible book value $63.02/share. Q3 2026 results are due Oct. 21, 2026.

**Market-cap note (engine figure is stale):** dcf_numbers.json carries market_cap_est $7,358,666,654.72, built on the FY2025 diluted count of 77,688,626 shares. That count is pre-merger: shares outstanding were 151,112,640 at 2026-07-31 (fundamentals.json, dei 10-Q) and the current-YTD diluted count in ttm.json is 151,470,000 — the share count roughly doubled when Synovus holders were paid in stock. At $94.72 the real market cap is roughly $14.3B (third-party quote pages put it at $14.3–14.6B in Oct. 2026), still well under the $40B scope line. make_score.py computes in-scope from the engine figure; the conclusion (in scope) is the same on the corrected count.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv, legacy Pinnacle only):** operating cash flow $759,008,000; capex $79,926,000 (PaymentsToAcquirePropertyPlantAndEquipment); SBC $43,626,000 (always a real cost).
- **Conservative owner's earnings FY2025: $635,456,000 = $8.1795/share** (base_oe_latest_per_share).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $641,865,000 — essentially the net income figure ($641,865,000); for a bank both definitions are approximations (loan growth, the real "capex" of a bank, is an investing outflow neither captures), which is the sector-mismatch caveat.
- OE positive 3 of the last 3 fiscal years available (the whole history under this CIK). Filed history OE/share: $4.6742 (2023), $9.9681 (2024), $8.1795 (2025) — the 2024 spike is an OCF artifact, see NI_OCF_DIVERGENCE below.
- Balance sheet (FY2025 10-K via fundamentals.json): assets $57,706,053,000; liabilities $50,662,338,000; equity $7,043,715,000; cash $3,473,908,000; goodwill $1,848,904,000. No debt tag reports for the latest fiscal year — net debt is unknown, not zero (see DEBT_TAGS_BLANK).

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $759,008,000 − prior YTD $239,000,000 + current YTD $1,016,000,000 = **TTM $1,536,008,000**
- Capex: FY $79,926,000 − prior YTD $31,000,000 + current YTD $38,000,000 = **TTM $86,926,000**
- SBC: FY $43,626,000 − prior YTD $21,000,000 + current YTD $110,000,000 = **TTM $132,626,000**
- Shares (current-YTD weighted diluted): **151,470,000**
- **TTM OE total $1,316,456,000 → base OE/share $8.6912** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $8.1795/share. The TTM base is used instead per the STALE_FY rule, and it is the only base on the right share count: the median is computed on legacy-only per-share figures (77.7M shares), the TTM base divides a mixed total (H2 2025 legacy + H1 2026 combined) by the combined 151.47M count. The two landing within ~6% of each other is partly coincidence — Synovus earnings per new share are similar to legacy Pinnacle's — and the TTM figure is if anything conservative against the combined run rate (Q2 2026 adjusted EPS $2.50 annualizes above it, though that print excludes merger costs). The bank-OCF caveat applies: OCF adds back the credit provision, so an OCF base in a benign-credit period flatters distributable earnings — handled by the bear-case OE multipliers and named here rather than hidden.

## Moat: 4/10 — weak-to-moderate regional-bank franchise
Justification: a real Southeast deposit franchise and a talent/relationship model that has taken share in its home markets, but a commodity banking product with no structural pricing power, and returns that have not cleared the cost of capital: legacy ROE was 9.31% (2023), 7.39% (2024) and 9.11% (2025) in fundamentals.json, the roic_proxy series is null for a bank (no operating-income/debt split is filed in a usable form) and gross margin is not presented for a bank — so there is no ROIC evidence to support a higher score, and the merger that would test the franchise at scale is nine months old.
- FOR:
  - Deposit franchise in growth markets — No. 1 deposit share in Nashville, No. 4 in Atlanta, $129.1B combined assets across nine Southeast/mid-Atlantic states
  - Talent-led relationship model — No. 12 on Fortune's 100 Best Companies to Work For in 2026 (10th straight year); the model demonstrably hires revenue producers away from larger banks
  - Merger scale — the Synovus combination (closed Jan. 1, 2026) roughly doubles the balance sheet and adds Georgia/Florida scale without a cash premium
  - Earnings momentum in the combined prints — Q2 2026 adjusted EPS $2.50 vs $2.00 a year earlier (legacy basis), NIM 3.4%
- AGAINST:
  - Commodity product — deposits and loans are fungible; the return is earned through the cycle, not from structural pricing power
  - Returns below a moat standard — legacy ROE 7.4–9.3% over FY2023–25 (fundamentals.json) has not stayed above the cost of equity through a cycle
  - Credit-cycle exposure — provisions are the swing factor and OCF adds them back; a Southeast real-estate downturn hits the bear cases fast
  - Merger integration risk — brand transition in Florida runs through Q1 2027, purchase-accounting marks and merger costs already cut Q1 2026 EPS to $0.89, and the combined franchise is unproven through any credit stress
  - Capital-constrained growth — loan growth, dividends and buybacks compete for the same regulatory capital
- A 4 gives CAP = 7.2 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 7.2 years, 15-year projection.

## DCF — engine 5.4 final run (2026-10-17)
Growth recalibration (written reason): the engine's g_blend of 32.26% is unusable as printed. It is a single component — OE/share CAGR 2y of 32.26% — built from a depressed 2023 OE/share ($4.6742, on OCF of only $478,404,000 against net income of $562,152,000) through the OCF-spiked 2024 ($9.9681/share while net income actually fell to $475,056,000 and EPS fell to $5.96). No revenue CAGR exists at all (the engine's revenue tag is null for a bank; fundamentals.json builds bank revenue as net interest + noninterest income: $1,695,371,000 / $1,736,768,000 / $2,054,851,000 for FY2023–25). A mature regional bank does not compound owner's earnings at 32%; the default scenario starts (super-bear +20.26%!) would have printed a fake Tier S (preliminary run: weighted IRR 27.58%, Tier S, IV@15% $237.49). Scenario starts were therefore set via offsets (−0.40259 / −0.34259 / −0.27259 / −0.22259 / −0.17259 vs g_base) to −8 / −2 / **+5** / +10 / +15%: a mid-single-digit base (balance-sheet growth plus buybacks through a cycle), bears carrying a real credit cycle, bull/super-bull anchored on merger synergies and the adjusted-EPS trajectory. Sanity check against prints: Q2 2026 revenue grew +132% YoY and adjusted EPS +25% YoY — both are merger step-ups (combined vs legacy-only comparatives, per the company's own warning), not organic start rates for a 15-year fade, which is the written reason even the super-bull start (+15%) sits below them. Probabilities skewed bear-ward for integration/credit risk at 15/25/30/20/10; OE multipliers default 0.75/0.90/1.00/1.10/1.25. Price $94.72. Base OE/share $8.6912 (TTM, above).

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | -8.0% | 0.75 | Credit cycle turns: provisions spike, NIM compresses, merger synergies stall | $35.49 | 6.83% |
| Bear | 25% | -2.0% | 0.90 | Recession-lite: charge-offs normalize up, earnings shrink before recovering | $53.89 | 9.47% |
| Base | 30% | +5.0% | 1.00 | Mid-single-digit earnings-power growth: loan/deposit growth plus buybacks, mid-cycle credit | $78.44 | 12.89% |
| Bull | 20% | +10.0% | 1.10 | Synergies delivered, ROTCE expands, credit stays benign | $104.29 | 16.19% |
| Super bull | 10% | +15.0% | 1.25 | Combined franchise compounds at low-teens with clean credit and full synergy capture | $142.85 | 20.62% |

- **Probability-weighted: IV@15% $77.47 (−18.2% vs price), IV@12% $102.64, IV@10% $130.69, weighted IRR 12.78%, base-case IRR 12.89%**
- **Tier by numbers: C.** Bear→bull band D (9.47%) → B (16.19%). Diagnostics (dcf_numbers.json): OE yield 9.18%, terminal value 18.46% of IV@15%, scenario spread 4.03x, 9.53 months since FY end. Hurdle prices: clears 20% only at $54.80, 25% only at $42.28.

## Flags — every fragility flag resolved
- **STALE_FY** (latest fiscal year ended 10 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, legs quoted in the Owner's earnings section above.
- **NI_OCF_DIVERGENCE** (2024: net income $475,056,000 vs OCF $904,306,000, >40% apart): resolved — the divergence is the OCF leg spiking, not earnings power: in the same year net income fell from $562,152,000, diluted EPS fell from $7.14 to $5.96 and ROE fell to 7.39% (fundamentals.json), while OCF nearly doubled. For a bank this gap is structural cash-flow presentation (non-cash provision and depreciation addbacks plus loans-held-for-sale origination/sale timing inside operating activities), and it is exactly what manufactured the fake OE/share of $9.9681 in 2024 and the 32.26% OE CAGR. Neither the 2024 OE figure nor any growth rate built on it is trusted: the base is the TTM pin and the scenario starts are set through-cycle (above).
- **THIN_HISTORY** (only 3 fiscal years): real, and explained — this CIK (2082866, filed former name "Steel Newco Inc." in fundamentals.json) is the new holding company formed for the Synovus merger, so EDGAR history under it starts at FY2023 and every pre-2026 period is legacy Pinnacle only. There is no combined-company audited annual history at all; the first combined 10-K is still to come. Confidence stays low.
- **DEBT_TAGS_BLANK** (no debt tag for the latest fiscal year — net debt unknown, not zero): stated from the filing (fundamentals.json, FY2025 10-K): assets $57,706,053,000, liabilities $50,662,338,000, equity $7,043,715,000, cash $3,473,908,000 on the legacy balance sheet; the combined company reported $129.1B of assets at June 30, 2026. An industrial net-debt verdict is meaningless for a bank in any case — deposits (inside liabilities) are the funding, loans are the assets, and the leverage that matters is regulatory capital, which this model does not compute.
- **SECTOR_MODEL_MISMATCH** (Finance): accepted in full. A bank's "owner's earnings" are not its distributable cash — loan growth consumes regulatory capital, provisions are a through-cycle cost the OCF line only partially carries, and bank value is normally judged on ROTCE vs cost of equity and tangible book (TBV $63.02/share at Q2 2026; the $94.72 price is ~1.5x that), none of which this model computes. Confidence is low, the alert gate suppresses on the misfit, and the tier is soft.
- **WIDE_SCENARIO_SPREAD** (super-bull IV 4.03x super-bear IV): real — a bank's outcome range across a credit cycle IS wide ($35.49 vs $142.85). Confidence is capped at low (also mandated by the sector flag), and the verdict is sized to the conservative end.
- **TIER_BAND** (bear tier D at 9.47% vs bull tier B at 16.19%): accepted — the verdict spans tiers, so any position is sized to the bear end (D). The headline stays the weighted C.

## My thoughts / overlay
- The honest headline is the correction, not the point estimate: the engine's preliminary run printed **Tier S (weighted IRR 27.58%, IV@15% $237.49)** off a 32.26% growth blend that traces to one OCF-spiked year and a depressed base year, on a pre-merger share count. Every part of that print is an artifact. On filing-defensible inputs — TTM base on the combined share count, through-cycle bank growth starts — the same model returns 12.78% / $77.47 (Tier C), and the bear end is D.
- Quality is not the debate: the Southeast deposit franchise is real, Q2 2026 adjusted EPS of $2.50 shows the combined earnings power, and the TTM OE yield is 9.18% at $94.72. The debate is price and proof: at ~1.5x tangible book the market is already paying for synergy delivery and ROTCE expansion from a franchise whose legacy ROE ran 7.4–9.3%, nine months after a merger of equals, before its first combined 10-K and before any credit weather.
- Method range: keep the engine's growth blend and the print is S; use the TTM base with through-cycle starts and it is C with a D bear. That spread is the finding — for a bank this screen can rank, it cannot certify.
- Price that clears 15%: the weighted IV@15% is $77.47 — the stock clears Andrew's hurdle at or below that level, roughly 18% below the current price, before any additional margin of safety; at the bear IV ($53.89) the margin would be real.

## Final verdict
- **Final tier: C** (weighted IRR 12.78% on the final inputs; tier by numbers C, no tier override — sized to the conservative end via the recalibrated scenarios and the D bear band)
- Confidence: **Low** (sector-model mismatch, wide scenario spread, thin combined history)
- One-liner: Quality Southeast regional bank fresh off the Synovus merger, moat 4/10 — the engine's Tier S print is a merger/OCF artifact; on a TTM base ($8.69/sh, combined share count) with through-cycle growth the weighted IRR is 12.78% (IV@15% $77.47 vs $94.72), so it clears 15% only below ~$77; bank-model mismatch, confidence low.
