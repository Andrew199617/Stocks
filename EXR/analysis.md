# EXR — Extra Space Storage Inc.
v5 run, 2026-10-14. Market cap $28.378B at $133.955 (nasdaq_quote_api, dcf_numbers.json) — in scope under $40B.

All figures below are copied from key_numbers.md (after make_score), dcf_numbers.json, ttm.json, or financials_history.csv — none are recomputed.

## What it is
The largest U.S. self-storage operator by store count since the all-stock Life Storage merger closed in July 2023. Owns/operates self-storage properties plus a large third-party management platform (1,964 third-party managed stores at Q2 2026 per the Q2 release) and tenant reinsurance and bridge-loan ancillaries. A REIT: month-to-month leases, need-based demand, low maintenance capex in reality — but see the sector-model caveat below. Q2 2026: Core FFO $2.15/share (+4.9% YoY), same-store revenue +2.4%, same-store NOI +3.5%, ending occupancy 94.2%; full-year 2026 Core FFO guidance raised to $8.25–$8.40/share, same-store revenue guidance +1% to +2% and same-store NOI guidance +0.5% to +2.5% (search results from the Q2 2026 release/coverage).

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv / dcf_numbers.json):** operating cash flow $1,850,193,000; capex $561,723,000 (tag: PaymentsToAcquireProductiveAssets); SBC $35,537,000 (always a real cost, and here small relative to OCF).
- **Conservative owner's earnings FY2025: $1,252,933,000 = $5.91/share latest FY** (base_oe_latest_per_share $5.914231383929426 in dcf_numbers.json)
- Maintenance version FY2025 (from financials_history.csv): $1,127,453,000 — same ballpark as the conservative figure.
- OE positive 5 of the last 5 fiscal years (dcf_numbers.json).
- Engine net debt is null in dcf_numbers.json (debt tags not populated), so no net-debt figure is quoted or folded in numerically — that is a limitation of this run, stated in words rather than calculated.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $1,850,193,000 − prior YTD $1,025,265,000 + current YTD $1,076,266,000 = **TTM $1,901,194,000**
- Capex: FY $561,723,000 − prior YTD $278,813,000 + current YTD $99,164,000 = **TTM $382,074,000**
- SBC: FY $35,537,000 − prior YTD $15,679,000 + current YTD $16,443,000 = **TTM $36,301,000**
- Shares (current-YTD weighted diluted): **220,343,045**
- **TTM OE total $1,482,819,000 → base OE/share $6.73** (ttm_oe_per_share $6.729592939954152; base_source: ttm_json)
- The engine's normalized base (median of last 3 FY OE/share) is $6.519496763552753/share — close to the TTM base, so the choice is not outcome-driving here; the TTM base was used because FY-end is 9.4 months stale.

**Capex / revenue-tag caveats (material to this name):** the capex tag is PaymentsToAcquireProductiveAssets — acquisition/development spend, not maintenance capex — so conservative OE understates true maintenance owner's earnings for a storage REIT. Symmetrically, the revenue tag (RevenueFromContractWithCustomerExcludingAssessedTax) records only $129,476,000 for FY2025 in financials_history.csv, which is plainly not total rental revenue (Q2 2026 total revenue alone was $874.2 million per Zacks coverage of the release); the engine's revenue CAGRs (5y 19.96%, 3y 15.55%) are therefore not usable as operating growth evidence and were not relied on for scenario starts.

## Moat: 5/10 — moderate / narrow
Justification: real scale and revenue-management advantages from being the largest operator, but the product is a commodity box on a month-to-month lease — local location and price dominate, switching costs are near zero, and Public Storage, CubeSmart and thousands of independents compete store-by-store.
- FOR: Largest U.S. operator by store count after the Life Storage merger — density in local markets lowers marketing cost per rental; data / revenue-management platform applied across a very large owned plus 1,964-store third-party managed base; diversified ancillaries (tenant reinsurance, bridge loans) that smaller operators cannot match at scale; geographic diversification across 43 states at merger close per the merger release.
- AGAINST: Commodity product with month-to-month leases and near-zero switching costs; competition is local and fragmented — a new facility nearby erodes pricing directly; demand is hostage to housing turnover / mobility, which has been soft; new supply waves (notably Sun Belt) pressure rents and occupancy — occupancy was 94.2% in Q2 2026, essentially flat YoY; no network effect that locks a customer to Extra Space over the facility down the road.
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — v5 final run (2026-10-14)
Growth recalibration (written reason): the engine's g_base is 6.34% (g_blend 11.34% minus the 5pp share-count adjustment). That blend is not credible for this company: its revenue components come from the broken contract-revenue tag above and the merger step-up, and its OE/share CAGR 2y is -10.17%. Actual recent prints are far lower — same-store revenue +2.4% in Q2 2026, guided +1% to +2% for FY2026; same-store NOI guided +0.5% to +2.5%; Core FFO +4.9% in Q2. Scenario starts were therefore recalibrated with offsets −0.09 / −0.06 / −0.03 / 0.00 / +0.03 vs g_base, to −2.66% / +0.34% / +3.34% / +6.34% / +9.34%. Even the super-bull start (+9.34%) sits above guided same-store growth — it is justified only as a supply-thins / pricing-recovery upside case, not as a current print. Probabilities were skewed bear-ward (15/25/30/20/10) for the sector-model mismatch and the OE-volatility history. OE multipliers are the defaults 0.75/0.90/1.00/1.10/1.25. Price $133.955.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | -2.66% | 0.75 | Housing turnover stays soft, new supply pressures rents, OE compresses | $33.37 | 5.44% |
| Bear | 25% | 0.34% | 0.90 | Flat same-store growth, expenses outrun rents | $45.39 | 6.66% |
| Base | 30% | 3.34% | 1.00 | Guided 1–2% same-store revenue with modest FFO-style growth | $57.16 | 7.87% |
| Bull | 20% | 6.34% | 1.10 | Supply thins, pricing power returns, occupancy holds | $71.21 | 9.28% |
| Super bull | 10% | 9.34% | 1.25 | Full pricing-recovery cycle plus external growth | $91.59 | 11.24% |

- **Probability-weighted: IV@15% $56.90, IV@12% $75.14, IV@10% $95.44, weighted IRR 7.86%, base-case IRR 7.87%**
- **Tier by numbers: D.** Diagnostics (dcf_numbers.json): OE yield 5.02%, terminal value 18.15% of IV@15%, scenario spread 2.75x, 9.4 months since FY end.
- No scenario clears 15% at the current price: even the super-bull IV@15% ($91.59) is below $133.955. The price that clears 15% on the weighted case is the weighted IV@15% itself, $56.90 — there is no margin of safety at the current price on this model; there is a large shortfall.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.4 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, with all inputs quoted above.
- **DILUTION** (share count +14.3%/yr): this is the Life Storage all-stock merger (closed July 2023), not ongoing dilutive issuance — diluted shares in financials_history.csv step from 141,681,388 (2022) to 169,220,882 (2023) to 211,577,680 (2024) around the merger. SBC is only $35,537,000 in FY2025 against OCF of $1,850,193,000, so SBC dilution is immaterial here. The engine's −5pp share-count growth adjustment overstates forward dilution; that is one reason scenario starts were set explicitly rather than taken from g_base unexamined.
- **OE_VOLATILE** (OE/share range >3x over 5 years): driven mainly by the capex tag — capex in financials_history.csv is $1,193,261,000 in 2022 under PaymentsToAcquireProductiveAssets versus $135,577,000 in 2023, crushing 2022 OE on an acquisition-spend year, plus the merger step-up in shares. It is a tag/basis artifact more than operating cyclicality, but the response stands: normalized/TTM base used and bear-side weight raised to 40% combined.
- **NI_OCF_DIVERGENCE** (>40% in 2023, 2024, 2025): structural REIT depreciation, not a one-off tax or working-capital item — D&A in financials_history.csv is $506,053,000 (2023), $783,023,000 (2024) and $715,177,000 (2025), a large non-cash charge that depresses net income relative to operating cash flow every year. The OCF-based conservative OE used throughout is not contaminated by it; if anything, GAAP net income understates cash earnings for this asset class, which is why the industry uses FFO.
- **SECTOR_MODEL_MISMATCH** (Real Estate): accepted in full — an OE/capex DCF fits a storage REIT poorly: the capex leg is acquisition spend, not maintenance, and the standard industry metric is Core FFO ($8.25–$8.40/share guided for 2026), not owner's earnings as defined here. Confidence is graded **low** and the tier is treated as soft for this reason.
- **WIDE_SCENARIO_SPREAD** (preliminary run: super-bull IV 4.5x super-bear): resolved in part by the recalibration above — the final run's spread is 2.75x (dcf_numbers.json diagnostics). Confidence remains low because of the sector mismatch, not the spread.

## My thoughts / overlay
- This is a quality, recession-resilient operator priced as one: at $133.955 the market is paying for the FFO stream and the dividend record, not for the conservative owner's-earnings stream this engine measures (which deducts all acquisition capex). That definitional gap cuts both ways — true maintenance OE is higher than the conservative figure — but even crediting the super-bull case (IV@15% $91.59, IRR 11.24%) the stock does not clear a 15% hurdle on any scenario in this run, so the method range does not span the hurdle: it is D on the numbers used, and at best a higher-D / low-C story on a maintenance-capex view that the computed outputs do not quantify (stated in words, per the no-hand-arithmetic rule, rather than calculated).
- Balance-sheet / rate risk is real for any REIT and the engine captured no net-debt figure (null in dcf_numbers.json), so leverage was not folded into the verdict numerically — another reason for low confidence, noted rather than filled in.
- The operating cycle may be turning (Q2 same-store revenue accelerated, guidance raised, new supply moderating per management commentary in search coverage), but a turn from ~0–2% to the growth this price needs is a multi-year pricing story, not a current print.

## Final verdict
- **Final tier: D** (weighted IRR 7.86% on the v5 final inputs; no tier override)
- Confidence: **Low** (SECTOR_MODEL_MISMATCH for a REIT, broken revenue tag, capex leg is acquisition spend, no engine net-debt figure)
- One-liner: High-quality self-storage REIT, moat 5/10 — does not clear 15% on any scenario (weighted IRR 7.86%, weighted IV@15% $56.90 vs $133.96 price; hurdle-clearing price $56.90, even super-bull only $91.59).
