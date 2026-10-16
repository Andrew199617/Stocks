# SBAC — SBA Communications Corporation
v5 run, 2026-10-16. In scope (market cap $19.756B at $183.72, nasdaq_quote_api).

All DCF figures below are copied from key_numbers.md, dcf_numbers.json, or ttm.py output — none are recomputed. Operating facts (Q2 2026 prints, churn, guidance) are from the company's Q2 2026 report / earnings coverage found by web search, cited in line.

## What it is
Tower REIT. Owns or operates 46,390 communication sites (17,362 in the US and territories, 29,028 international, per the Q2 2026 report) and leases space on them to wireless carriers under long-term contracts with fixed escalators; a smaller site-development services segment builds and installs for carriers. One of the three large US tower owners, alongside American Tower and Crown Castle. Q2 2026: total revenues $715.3M (+2.3% YoY), site leasing revenue $663.9M (+5.1% YoY, +3% ex-FX), AFFO $3.05/share; management's full-year 2026 outlook is AFFO of $11.95–12.40/share (Q2 2026 report via search).

## Owner's earnings
**FY2025 (10-K via EDGAR, from key_numbers.md / financials_history.csv):** operating cash flow $1,291,328,000; capex $224,819,000; SBC $75,734,000 (always a real cost).
- **Conservative owner's earnings FY2025: $990.8M total, $9.21/share latest FY** (key_numbers.md).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC) is not usable for this filer: the ΔNWC term swings by more than a billion dollars between years in financials_history.csv, whipsawing that definition (it prints deeply negative in FY2024 and far above the conservative figure in FY2025). The OCF-based conservative figure is the series used throughout.
- OE positive 5 of the last 5 fiscal years. Net debt (latest) $12.636B (key_numbers.md) — see HIGH_NET_DEBT below.
- **Data caveat on revenue:** the engine's revenue series in financials_history.csv ($152.9M–$296.9M/yr) is a disaggregated contract-revenue component under the `RevenueFromContractWithCustomerExcludingAssessedTax` tag, not total company revenue (Q2 2026 total revenues alone were $715.3M). The blend's revenue components (5y CAGR 13.70%, 3y CAGR −6.26%, latest YoY 59.94%) are therefore artifacts and were NOT trusted for scenario calibration; the OE legs (OCF / capex / SBC / shares) are complete and consistent, and the base rests on them.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $1,291,328,000 − prior YTD $669,273,000 + current YTD $662,263,000 = **TTM $1,284,318,000**
- Capex: FY $224,819,000 − prior YTD $102,038,000 + current YTD $110,816,000 = **TTM $233,597,000**
- SBC: FY $75,734,000 − prior YTD $37,229,000 + current YTD $45,734,000 = **TTM $84,239,000**
- Shares (current-YTD weighted diluted): **106,188,000**
- **TTM OE total $966,482,000 → base OE/share $9.10** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $9.55/share and the latest FY is $9.21/share. The TTM base was used because FY2025 ended 9.5 months ago (STALE_FY) and the TTM figure is the most current filing-derived basis; it is also the lowest of the three, so the choice is conservative, not flattering. The trend across the three — $9.55 median → $9.21 latest FY → $9.10 TTM — is flat-to-declining OE/share, consistent with AFFO/share printing down year over year in Q2 2026.

## Moat: 7/10 — strong, not wide
Justification: zoning/permitting scarcity makes existing sites nearly impossible to replicate, long-term leases with fixed escalators, very high incremental margin on colocation (tower cash flow margin 79.5% in Q2 2026, per the Q2 report), and a three-player US oligopoly serving carriers who cannot easily relocate equipment. Capped below 9–10 because the customer base is only three major US carriers, pricing is contractual escalators rather than true pricing power, the US market is mature, and leverage leaves the equity as a levered claim on slow growth.
- FOR: Zoning/permitting scarcity — existing towers cannot be replicated; Long-term leases with fixed escalators — contracted, visible revenue; Colocation economics — added tenants drop through at ~79.5% tower cash flow margin; Three-player tower oligopoly (AMT / CCI / SBAC), high carrier switching costs; 46,390 sites, scale in international growth markets (Millicom portfolio)
- AGAINST: Customer concentration — three major US carriers; consolidation drives churn (Sprint, then Dish 2027-28); No pricing power beyond contractual escalators; Mature US market — domestic site leasing flat in Q2 2026, growth is international/FX-exposed; High leverage — net debt 12.9x normalized OE (6.4x Adj. EBITDA), rate-sensitive REIT equity; Ground-lease renewals and satellite direct-to-cell as long-run erosion forces
- A 7 gives CAP = 11.1 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 11.1 years, 15-year projection.

## DCF — v5 final run (2026-10-16)
Growth recalibration (written reason): the engine's g_base is 4.29% off a 3.72% blend whose revenue components are the tag artifacts described above, and the preliminary run's default offsets produced a 16.3% super-bull start — a rate this business has never printed (actual prints: Q2 2026 total revenue +2.3% YoY, site leasing +5.1% / +3% ex-FX, TTM OE/share below the FY figure). Scenario starts were therefore set via offsets (−0.10 / −0.05 / −0.02 / +0.01 / +0.03 vs g_base) to −5.7 / −0.7 / **2.3** / 5.3 / 7.3%: the base start matches the escalator-plus-colocation print net of guided Sprint churn (and announced Dish churn in 2027–28, per earnings-call coverage), the bull start matches the best recent leasing print, and even super bull (7.3%) requires international lease-up on the Millicom portfolio plus a new-tenant cycle — a stretch, not a fantasy. Probabilities 15/25/30/20/10 skew heavier to bear-or-worse than default because of the leverage and contracted churn; OE multipliers are the defaults 0.75/0.90/1.00/1.10/1.25. Price $183.72.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | -5.7% | 0.75 | Churn (Sprint/Dish, intl) plus high rates bite levered OE | $38.13 | 4.74% |
| Bear | 25% | -0.7% | 0.90 | US leasing stays flat, churn offsets escalators | $57.75 | 6.26% |
| Base | 30% | 2.3% | 1.00 | Escalators + modest colocation, intl offsets US churn | $73.89 | 7.52% |
| Bull | 20% | 5.3% | 1.10 | Intl lease-up + carrier capex cycle lifts leasing | $93.65 | 9.02% |
| Super bull | 10% | 7.3% | 1.25 | Millicom synergy + new spectrum builds + rate relief | $116.99 | 10.67% |

- **Probability-weighted: IV@15% $72.75 (−60.4% vs price), IV@12% $95.76 (−47.9%), IV@10% $121.33, weighted IRR 7.46%, base-case IRR 7.52%**
- **Tier by numbers: D.** Diagnostics (key_numbers.md): OE yield 4.95%, terminal value 17.8% of IV@15%, scenario spread 3.07x, net debt 12.91x normalized OE, 9.5 months since FY end.
- No scenario — not even super bull at a 1.25 OE multiplier — clears the current price at a 15% discount rate; super bull IV@15 ($116.99) is still well below $183.72.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.5 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, quoted above ($9.10/share, below both the median and latest-FY bases).
- **NI_OCF_DIVERGENCE** (2023, 2024): structural REIT accounting, not a cash-quality red flag. Net income is depressed by large non-cash depreciation/accretion on towers (D&A in financials_history.csv: $716,309,000 in FY2023) while OCF adds it back; the subsequent D&A step-down ($269,517,000 in FY2024, $292,285,000 in FY2025) is also why net income rose sharply while OCF was flat-to-down. The OCF-based conservative OE used throughout is unaffected by the divergence.
- **SECTOR_MODEL_MISMATCH** (Real Estate / tower REIT): accepted — the standardized OE/capex DCF fits REITs poorly (the sector's own yardstick is AFFO, guided at $11.95–12.40/share for 2026, which capitalizes items this model treats differently, and total capex here includes growth tower builds). Confidence is graded **low** for this reason; the tier is not overridden, because even the model's most generous scenario does not approach the price.
- **HIGH_NET_DEBT** (net debt 12.91x normalized OE; $12.636B latest): folded into the verdict — the Q2 report puts net debt at 6.4x annualized Adjusted EBITDA, inside the company's 6.0–7.0x target range, so leverage is deliberate REIT policy rather than distress, but it still means the equity is a thin, rate-sensitive claim: bear/super-bear probabilities were raised to 25%/15% and no leverage benefit is credited in any scenario.

## My thoughts / overlay
- This is a quality-asset / wrong-price result, not a broken business: contracted escalator revenue, 79.5% tower cash flow margin (Q2 report), OE positive 5/5 years, and a real moat (7/10). The DCF fails it on arithmetic alone — a $9.10 TTM OE/share base is a 4.95% OE yield at $183.72, and low-single-digit growth cannot compound that into a 15% return.
- Method range: the preliminary run on the median base with default offsets printed weighted IRR 8.80% (also Tier D), and this final TTM run prints 7.46% (Tier D). Every defensible variant tried lands in Tier D; there is no C-or-better method to report.
- Balance sheet overlay is in the flags: 6.4x EBITDA leverage is normal for towers but leaves no room for the equity to be paid like a bond and priced like growth at the same time. The dividend and buyback do not change the OE math used here.
- Price that clears 15%: the weighted IV@15% is **$72.75** — the stock would need to trade below roughly $73 (a ~60% decline) before the weighted case clears Andrew's 15% hurdle, and a margin of safety against the bear cases ($57.75 / $38.13) argues for lower still.

## Final verdict
- **Final tier: D** (weighted IRR 7.46% on the v5 final inputs; tier by numbers D, no override)
- Confidence: **Low** (sector-model mismatch on a REIT, per the flag rule — though the D conclusion itself is robust across bases and scenarios)
- One-liner: Strong-moat (7/10) tower REIT with contracted escalator growth, but slow growth plus 12.9x net debt/OE cannot clear 15% at $183.72 — Tier D, weighted IRR 7.46%, weighted IV@15 $72.75; clears 15% only below ~$73.
