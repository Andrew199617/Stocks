# CRCL — Circle Internet Group, Inc.
v5 run, 2026-10-15. Price $86.30 (nasdaq_quote_api), market cap $13.70B — in scope under $40B. All figures below are copied from dcf_numbers.json, ttm.json, financials_history.csv, or the cited earnings reporting — none are recomputed.

## What it is
Issuer of USDC, the second-largest USD stablecoin. Circle earns reserve income on the cash and short-term Treasuries backing USDC in circulation and keeps only part of it — the rest is paid out as distribution costs, principally to Coinbase. Q2 2026 (reported): total revenue and reserve income $701M, up 7% YoY; reserve income $668M; USDC in circulation $73.3B at quarter end, up 19% YoY (average $76.5B, up ~25%); reserve return rate 3.5%, down from 3.81% a year earlier; adjusted EBITDA $143M; net income from continuing operations $48M; revenue less distribution costs $289M. Roughly 95% of revenue is reserve yield, so the P&L is a levered function of two variables Circle does not control: USDC float and short-term interest rates. Newer lines (Circle Payments Network, the Arc Layer-1, transaction/other revenue) are real but still small against reserve income.

## Owner's earnings
From financials_history.csv (EDGAR filing-direct):
- FY2023: OCF $139,568,000; capex $654,000; SBC $107,999,000; conservative OE $30,915,000.
- FY2024: OCF $344,576,000; capex $18,128,000; SBC $50,134,000; conservative OE $276,314,000.
- FY2025: OCF $542,129,000; capex $12,432,000; SBC $566,177,000; conservative OE **-$36,480,000 (-$0.23/share)**. The FY2025 SBC figure is dominated by the June 2025 IPO: Q2 2025 alone carried $424M of stock-based compensation from RSU vesting triggered by the IPO, plus a $167M convertible-debt fair-value charge — together $591M of non-cash items behind that quarter's $482M net loss.
- Maintenance OE diverges wildly (FY2025: -$569,338,000, driven by a $564,025,000 change in net working capital in the engine's calc) — for a stablecoin issuer the "working capital" line is entangled with reserve/float flows, so the maintenance definition is not meaningful here; the OCF-based conservative definition is the series used. This is part of the SECTOR_MODEL_MISMATCH problem below.
- OE positive in 2 of the last 3 fiscal years (dcf_numbers.json). Net debt is null in the engine output — the balance sheet is dominated by reserves backing USDC (customer liabilities, not corporate cash), so no net-debt multiple is quoted.
- Tag caveat: the engine's revenue series uses RevenueFromContractWithCustomerExcludingAssessedTax, which captures only a narrow slice of Circle's reported total revenue and reserve income. The resulting revenue CAGRs in dcf_numbers.json (135.02% 5y/3y, latest YoY +623.98%) are tagging artifacts, not the business's growth — reported total revenue grew 7% YoY in Q2 2026. No growth input in this run is taken from those CAGRs (see growth recalibration).

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $542,129,000 − prior YTD $303,716,000 + current YTD $538,505,000 = **TTM $776,918,000**
- Capex: FY $12,432,000 − prior YTD $7,419,000 + current YTD $10,389,000 = **TTM $15,402,000**
- SBC: FY $566,177,000 − prior YTD $447,682,000 + current YTD $105,435,000 = **TTM $223,930,000**
- Shares (current-YTD weighted diluted): **267,940,000**
- **TTM OE total $537,586,000 → base OE/share $2.01** (base_source: ttm_json)
- The TTM base is the right base: it laps the IPO SBC spike (TTM SBC $223.9M vs FY2025's $566.2M — still a heavy, real cost, but a run-rate rather than a one-off vesting event) and it uses the post-IPO share count. The engine's normalized base (3-yr median) is $0.46/share and the latest-FY base is -$0.23/share; both are distorted by the pre-IPO capital structure and the IPO charges, in opposite directions. Even on the TTM base the OE yield is only 2.32% at $86.30 — the valuation still rests almost entirely on growth.

## Moat: 5/10 — moderate, regulatory but economically shared away
Justification: USDC's compliance stack and institutional distribution are real advantages, but the float is a commodity, the larger rival keeps far more of its reserve economics, and Circle pays away the majority of its reserve income for distribution.
- FOR: Regulatory moat — GENIUS Act framework (federal supervision, 1:1 reserves, effective Jan 2027), OCC national trust charter and NYDFS limited-purpose trust charter, audited reserves and institutional custody; compliance is now a legal barrier to entry, not just a feature.
- FOR: Network/distribution — USDC integrated across exchanges, DeFi and payments; $73.3B in circulation, ~27% stablecoin market share; institutional partner network and Coinbase distribution.
- FOR: Trust/brand with regulated institutions that cannot touch non-compliant tokens — the segment where USDC leads.
- AGAINST: Tether's USDT is ~$184B, roughly 60% of the market and ~2.5x USDC, and Tether keeps ~100% of its reserve income while Circle keeps ~37% — Circle pays for distribution like a challenger while priced like an incumbent.
- AGAINST: The Coinbase revenue share (50/50 on Coinbase-held USDC, extended through Aug 2029) hands the core economics to a partner; analysts have flagged the arrangement's durability.
- AGAINST: Tether's USAT (launched Jan 2026, GENIUS-compliant, via a federally regulated issuer) attacks the compliance home field directly; PayPal, bank and consortium coins, and yield-sharing challengers crowd in from the other side.
- AGAINST: No pricing power over the product itself — revenue is the Treasury yield on float, set by the Fed; GENIUS bars paying interest to holders, which protects reserve income but removes a growth lever.
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — v5 final run (2026-10-15)
Growth recalibration (written reason — the opposite failure from the usual one): the engine's blended growth hit the 35% cap off tagging artifacts (see the revenue-tag caveat above), so every default scenario start (23–47%) sat far above what Circle just printed — Q2 2026 total revenue +7% YoY, with average circulation +25% mostly offset by the reserve rate falling 3.81% → 3.50%. Offsets were therefore recalibrated downward (−0.35 / −0.29 / −0.23 / −0.15 / −0.07 vs the capped g_base) to starts of 0 / 6 / **12** / 20 / 28%: circulation growth in the teens-to-20s, minus continued rate drag, minus distribution share, is what an OE/share path can actually deliver. Probabilities were skewed bearish (15/30/30/17/8 vs the 10/25/30/25/10 default) on the rate headwind and the Tether/USAT competitive step-up. OE multipliers are the defaults 0.75/0.90/1.00/1.10/1.25. Price $86.30.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | 0.0% | 0.75 | Fed cuts crush reserve yield; USAT/new entrants stall USDC growth | $11.12 | 4.06% |
| Bear | 30% | 6.0% | 0.90 | Circulation grows but rate drag eats most of it | $17.12 | 5.07% |
| Base | 30% | 12.0% | 1.00 | Mid-teens circulation growth, mild rate drag, distribution share holds | $24.36 | 6.32% |
| Bull | 17% | 20.0% | 1.10 | Circulation compounds 20%+; Arc/CPN fees start to diversify revenue | $37.09 | 8.42% |
| Super bull | 8% | 28.0% | 1.25 | Stablecoin market inflects; USDC takes share and non-reserve revenue scales | $57.97 | 11.48% |

- **Probability-weighted: IV@15% $25.06 (−71.0% vs price), IV@12% $33.96, IV@10% $43.96, weighted IRR 6.49%, base-case IRR 6.32%**
- **Tier by numbers: D.** Diagnostics (dcf_numbers.json): OE yield 2.32%, terminal value 20.7% of IV@15%, scenario spread 5.21x, 9.5 months since FY end.
- The decisive fact: even the super-bull case (28% growth start, 1.25x OE) yields only an 11.48% IRR and a $57.97 IV@15% — below the $86.30 price. At this price there is no scenario in the set that clears the 15% hurdle.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.5 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, quoted above with all four legs.
- **DILUTION** (share count +53.2%/yr): this is IPO mechanics, not a steady-state dilution rate — preferred conversion, IPO primary shares, RSU vesting and the Aug 2025 secondary took diluted shares from 73,042,000 (FY2024) to 158,699,000 (FY2025) to 267,940,000 (current YTD). The TTM base already divides by the post-IPO 267.9M count, so the historical CAGR does not flatter the base. The ongoing cost is SBC: TTM SBC of $223,930,000 against TTM OCF of $776,918,000 (both from ttm.json) — deducted in full in the conservative OE, as always.
- **BASIS_BREAK_SUSPECT**: the break is the June 2025 IPO itself (capital-structure conversion, SBC vesting trigger, convertible revaluation) layered on the revenue-tag artifact described above. No CAGR from the filed history is used as a growth input; scenario starts are anchored to reported Q2 2026 total-revenue growth (+7%) instead.
- **NI_OCF_DIVERGENCE** (2023, 2024, 2025): identified — the gaps are the non-cash SBC addback (FY2025 SBC $566,177,000 against a net loss), the $167M Q2 2025 convertible-debt fair-value increase (a share-price effect, not operations), and stablecoin float/working-capital swings. The OCF-based conservative OE is used throughout, so the divergence does not contaminate the base beyond the SBC spike, which the TTM base laps.
- **THIN_HISTORY** (only 3 fiscal years): real — Circle IPO'd in June 2025 and EDGAR carries 3 fiscal years. One more reason for low confidence and bear-skewed probabilities.
- **SECTOR_MODEL_MISMATCH** (Finance): accepted in full. A stablecoin issuer's reserves are customer-backed float, capex ($15.4M TTM) is trivial against the balance sheet, and OE/capex DCF logic fits poorly. Confidence is low and the tier is soft — though here the mismatch does not rescue the verdict, because even the finance-friendly TTM base and the super-bull scenario stay far below the hurdle.
- **BASE_DIVERGENCE** (latest FY -$0.23 vs 3-yr median $0.46): both are distorted — the latest FY by the IPO SBC/convertible charges, the median by the pre-IPO share count and SBC regime. Resolved by using the TTM base ($2.01/share), which laps the one-offs and uses the current share count.
- **WIDE_SCENARIO_SPREAD** (5.21x): real — outcomes hinge on Fed policy and float growth, both outside management's control. Confidence is capped (set to low on the sector flag in any case) and the verdict is sized to the conservative end.
- The preliminary run's **LOW_OE_YIELD** flag (0.5% on the median base) no longer fires on the TTM base (2.32%) but the substance stands: at a 2.32% OE yield the price is a pure growth/rate bet.

## My thoughts / overlay
- Method range: on the preliminary run's median base ($0.46/share) with default scenarios the weighted IRR was 5.27% (IV@15% $14.77); on the TTM base with recalibrated growth it is 6.49% (IV@15% $25.06). Both are Tier D, and the super-bull ceiling (11.48% IRR) is below the 15% hurdle under either base — the tier is not method-sensitive here, which is the strongest statement this screen can make.
- Quality is not the issue: USDC circulation +19% YoY, on-chain volume growing triple digits, RLDC margin expanding, and a genuine regulatory moat being codified by the GENIUS Act. The issue is arithmetic: $86.30 capitalizes reserve income at a 2.32% OE yield while the two drivers of that income (float growth, short rates) are moving in opposite directions and the majority of the economics are shared with distribution partners.
- Rate sensitivity is the tail that wags this dog: a 200bp fall in short rates against flat circulation would cut reserve income by roughly half before any growth offset — that is the super-bear/bear block, given 45% combined probability.
- Hurdle-clearing price: the weighted IV@15% is $25.06 — that is the price at which the weighted case clears 15%. With a margin of safety against the 5.21x scenario spread and the sector-model mismatch, a buyer needing 15% with protection would need the low-$20s or below. Even paying the super-bull IV@15% ($57.97) only buys an 11.48% IRR at $86.30 terms — there is no defensible entry near the current price on owner's earnings.

## Final verdict
- **Final tier: D** (weighted IRR 6.49% on the v5 final inputs; no tier override — the numbers and the overlay agree)
- Confidence: **Low** (SECTOR_MODEL_MISMATCH, thin 3-year history, 5.21x scenario spread, rate-driven revenue)
- One-liner: Real regulatory moat (5/10) on a commodity float — TTM OE of $2.01/share is a 2.3% yield at $86.30 and even the super-bull case returns only 11.5%; clears 15% only at ~$25.
