# JBS — JBS N.V.
Engine 5.4.0 run, 2026-10-17. In scope under $40B (market cap est $13.923B at $13.03, nasdaq_quote_api, key_numbers.md).

All figures below are copied from key_numbers.md, dcf_numbers.json, fundamentals.json or financials_history.csv — none are recomputed.

## What it is
Dutch-incorporated holding company for the JBS Group, the world's largest animal-protein processor: beef, pork, poultry and lamb, plus prepared foods, leather and related by-products, across the US, Brazil, Australia, Europe and elsewhere. Brands include Seara, Pilgrim's, Moy Park, Swift and Primo. Class A common shares listed directly on the NYSE under JBS (listed June 2025 in the dual-listing restructuring); Level II BDRs trade on B3 as JBSS32. SIC 2011, Meat Packing Plants (fundamentals.json).

## Owner's earnings
**Filed history (financials_history.csv, 20-F via EDGAR — only 3 fiscal years under this holding structure):**

| FY | Revenue | OCF | Capex | SBC | Conservative OE | OE/share |
|---|---|---|---|---|---|---|
| 2023 | $72,918,123,000 | $2,378,774,000 | $1,502,137,000 | $6,913,000 | $869,724,000 | $0.81 |
| 2024 | $77,182,547,000 | $4,229,549,000 | $1,480,298,000 | $15,794,000 | $2,733,457,000 | $2.56 |
| 2025 | $86,184,182,000 | $2,931,953,000 | $2,099,269,000 | $28,851,000 | $803,833,000 | $0.75 |

- Conservative OE = OCF − capex − SBC. SBC is tiny here (cash-settled plans) but is deducted as a real cost anyway.
- Maintenance OE (NI + D&A − min(capex, D&A) − ΔNWC, financials_history.csv) tells a harsher 2025 story: −$41,935,000 in FY2025 vs $515,194,000 (2023) and $2,676,859,000 (2024), driven by a $2,480,978,000 ΔNWC leg in FY2025. The two definitions agree in 2023–24 and diverge violently in 2025 — the business consumes working capital as it grows, and the OCF-based conservative figure is the cleaner base, with the divergence disclosed rather than averaged away.
- **Base used = the engine's normalized base: median of the last 3 FY OE/share, $0.81/share** (base_source: median_of_last_3_fy_oe_per_share; latest FY $0.75/share, latest FY OE total $803.8M). OE-positive years 3/3.
- **No TTM base:** STALE_FY applies (FY ended 9.5 months ago per key_numbers.md), but ttm.py reads us-gaap only and exited non-zero for this IFRS filer ("cannot compute TTM for JBS … no annual (FY) fact" under its candidate tags), so no ttm.json exists and no --ttm / --base-oe-ps pin was used — per spec, the median base stands for IFRS filers. The 2026 interim prints that are available point down, not up: Q2 2026 (filed 2026-08-10) showed record net revenue of $23.9B, up ~14% YoY, but adjusted EBITDA fell 18% YoY and the quarter swung to a net loss attributable to shareholders of $102M on tight US cattle supply — a TTM base built from 2026 would more likely be lower than the FY2025 figure, so the median base is not flattering the result.
- Balance sheet (latest filed, key_numbers.md / dcf_numbers.json): net debt $16.525B (basis LongtermBorrowings+ShorttermBorrowings, total borrowings $21,090,568,000 in financials_history.csv), lease liabilities $1,767,285,000. Net debt is 19.00x normalized OE (diagnostics).

## OVERRIDES — shares (filing) and ads_ratio 1.0
- **The gap:** the preliminary engine run exited 4 with `DATA_GAP:shares` — no diluted share count is filed for FY2023–25, only WeightedAverageShares (1,068,508,877 in all three years, recorded as FALLBACK in financials_history.csv), and a 20-F filer also triggers `ADS_RATIO_MISSING` until judgment.json carries an ads_ratio.
- **Shares decision (bounded authority, kind "filing"):** judgment.json carries `shares_override = {value: 1068508877, kind: "filing"}` from the 20-F EPS note, which prints a single line "Basic and diluted earnings (loss) per share" ($1.89 / $1.65 / −$0.19) on that same weighted-average count for 2025/2024/2023 (2024/2023 retrospectively adjusted to the 2025 share structure); the same filing's share-based compensation note describes the JBS/Seara plans as cash-settled with no share issuance for settlement, which is why there is no separate dilutive count in those years. The override fills only the missing diluted slot (periods filled: 2023-12-31, 2024-12-31, 2025-12-31); it never replaces a filed value.
- **Measured impact (key_numbers.md / dcf_numbers.json override_impact):** zero on the numbers — normalized base OE/share $0.81 zero-fill → $0.81 with override, weighted IRR 10.70% → 10.70% — because the filed fallback count is the same number. Its effect is binary: unblocks_tier is YES; without it there is no tier at all. Note score.json therefore records the tier as resting on an override for alert purposes (exit_alert_suppressed_reason), even though the override changes no figure.
- **ADS ratio:** 1.0, kind filing-equivalent from the filer's own 20-F Note 1: the NYSE security is the Class A common share itself, listed under JBS — there is no ADS program for the NYSE listing (the depositary instrument is the BDR on B3). Per-share figures are already comparable to the $13.03 NYSE price; the engine flag records this as ADS_RATIO_APPLIED x1.0.

## Moat: 4/10 — weak-to-moderate, scale without pricing power
Justification (from judgment.json): scale and multi-protein, multi-geography diversification give real cost and resilience advantages, but this is commodity protein processing: gross margin was only 10.9% (FY2023), 15.0% (FY2024) and 13.1% (FY2025) in fundamentals.json, and the roic_proxy series in fundamentals.json fell from 16.7% (FY2023) to 14.5% (FY2024) to 13.6% (FY2025) — above a normal cost of capital in all three filed years, which is what keeps the score at 4 rather than lower, but declining and earned in a commodity spread business, not from pricing power. The company's own reported LTM ROIC of 17.4% for FY2025 (Q4 2025 release) uses its adjusted definition and is not the series scored here.
- FOR: world's largest protein processor — scale in procurement, plant utilization and distribution across beef, pork, poultry and lamb; multi-protein, multi-geography platform (US, Brazil, Australia, Europe) diversifies single-protein and single-country cycles; branded and value-added businesses (Seara, Pilgrim's, Moy Park, Swift, Primo) sit above pure commodity slaughter; ROIC proxy stayed above cost of capital in all three filed years (16.7% / 14.5% / 13.6%, fundamentals.json).
- AGAINST: commodity processing with thin gross margins (10.9%–15.0%) and no control over livestock input prices or meat cutout prices; cattle-cycle exposure — tight US cattle supply drove a Q2 2026 net loss and an 18% YoY fall in adjusted EBITDA despite record sales; powerful retail/foodservice buyers and low consumer switching costs limit pricing power; leverage and governance — net debt $16.525B filed for FY2025, Q2 2026 leverage reported at 3.1x adjusted EBITDA (above the 2.4x level at FY2025 year-end), Batista family control, antitrust / food-safety / ESG exposure.
- A 4 gives CAP = 7.2 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 7.2 years, 15-year projection.

## DCF — engine 5.4.0 final run (2026-10-17)
Growth: engine blend 8.71% (components: rev CAGR 5y 8.71%, rev CAGR 3y 8.71% — identical because only 3 years are filed — latest rev YoY 11.66%, OE/share CAGR 2y −3.86%). Default offsets (−12/−5/0/+5/+12pp) and default OE multipliers (0.75/0.90/1.00/1.10/1.25) were kept; probabilities were widened toward the bear end to 15/30/30/15/10 (from the 10/25/30/25/10 default) per the OE_VOLATILE flag and the deteriorating 2026 prints.
**Sanity check against actual prints:** FY2025 revenue grew 11.66% and Q2 2026 revenue grew ~14% YoY, so the bull growth start of 13.7% sits right at the latest revenue print and does not need a special reason. The base start of 8.7% is below the recent revenue prints for a written reason: the scenarios grow owner's earnings, not revenue, and OE is currently moving the other way (FY2025 OE/share $0.75 vs $2.56 in FY2024; Q2 2026 swung to a loss) as the US cattle cycle compresses beef spreads. The super-bull start of 20.7% is above every recent revenue print; it is defensible only as a cyclical OE recovery off depressed beef margins (OE/share has already printed $2.56 in a good year, 3.4x the FY2025 figure), it carries only 10% weight, and even it produces only a 17.86% IRR. The super-bear start of −3.3% is mild against a business whose OE/share fell ~71% in FY2025 — the 0.75 OE multiplier carries the rest of that stress. Price $13.03.

| Scenario | Prob | Growth start | OE mult | IV@15 | IRR |
|---|---|---|---|---|---|
| Super bear | 15% | -3.3% | 0.75 | $4.00 | 6.17% |
| Bear | 30% | 3.7% | 0.9 | $6.29 | 8.57% |
| Base | 30% | 8.7% | 1.0 | $8.46 | 10.77% |
| Bull | 15% | 13.7% | 1.1 | $11.22 | 13.39% |
| Super bull | 10% | 20.7% | 1.25 | $16.50 | 17.86% |

- **Probability-weighted: IV@15% $8.36 (−35.9% vs price), IV@12% $11.16 (−14.3%), IV@10% $14.30, weighted IRR 10.70%, base-case IRR 10.77%**
- **Tier by numbers: C.** Bear tier D (8.57%), bull tier C (13.39%). Diagnostics (key_numbers.md): OE yield 6.25%, terminal value 19.2% of IV@15%, scenario spread 4.13x, net debt 19.00x normalized OE, 9.5 months since FY end.
- Hurdle-clearing prices (weighted path): 15% at $8.36, 20% at $5.84, 25% at $4.47.

## Flags — every fragility flag resolved
- **STALE_FY** (latest FY ended 10 months ago): ttm.py cannot run for this IFRS filer (us-gaap tags only; it exited non-zero this run), so no TTM pin exists — the median-of-3-FY base is used per spec for IFRS filers. Direction check from the filed 2026 interims: Q2 2026 revenue $23.9B (+~14% YoY) with adjusted EBITDA −18% YoY and a $102M attributable net loss, so current trading is weaker than the base period, not stronger; the stale base is not understating value.
- **OE_VOLATILE** (OE/share spans >3x): real and structural — $0.81 / $2.56 / $0.75 over FY2023–25 is the protein cycle, not a one-off. Handled by the normalized (median) base instead of any single year and by widening bear weight to 45% on bear-or-worse (probs 15/30/30/15/10).
- **NI_OCF_DIVERGENCE** (2023, 2024): resolved as D&A, not a hidden one-off. In financials_history.csv, FY2023 net income was −$131,735,000 against OCF of $2,378,774,000, and D&A alone was $2,149,066,000; FY2024 net income was $1,967,610,000 against OCF of $4,229,549,000 with D&A of $2,189,547,000. Adding back the filed D&A lands next to OCF in both years; the residual is working capital. The base is built on OCF, so the divergence does not contaminate it — but the same D&A-heavy structure is why the maintenance-OE definition (which subtracts ΔNWC) can go negative, as it did in FY2025.
- **ADS_RATIO_APPLIED** (x1.0): see OVERRIDES — direct NYSE listing of Class A shares, no ADS; no scaling applied.
- **THIN_HISTORY** (only 3 fiscal years): real — the JBS N.V. holding structure and its retrospective EPS/share history date from the 2023–25 restructuring, so EDGAR carries 3 annual years under this CIK. The operating business is decades old, but no longer filed series exists to score; this is a direct reason confidence is low and the 5y/3y revenue CAGRs collapse to the same 8.71%.
- **OVERRIDE_APPLIED:shares**: see OVERRIDES — filing-sourced, measured impact zero on base and IRR, unblocks the tier.
- **WIDE_SCENARIO_SPREAD** (4.13x): real — a levered cyclical's outcome range IS wide. Confidence is low, and the verdict is sized to the bear end (TIER_BAND).
- **HIGH_NET_DEBT** (net debt 19.0x normalized OE): balance sheet stated from the filing above — total borrowings $21,090,568,000 and net debt $16,525,432,000 at FY2025, plus $1,767,285,000 of lease liabilities. Against earnings power the company's own leverage measure was 2.4x adjusted EBITDA at FY2025 year-end and a reported 3.1x in Q2 2026; the 19.0x figure is against the depressed normalized OE, which is exactly the stress point: at trough OE, the debt load leaves little equity cushion, and it is why the bear cases are weighted 45%.
- **TIER_BAND** (bear D 8.57% vs bull C 13.39%): the verdict spans tiers and even the bull case does not clear 15%; sized to the bear end — final tier C by numbers, read as a D-leaning C.

## My thoughts / overlay
- The method range here is really a base-choice range: on the FY2024 OE/share of $2.56 this stock would screen as deep value; on FY2025's $0.75 or the negative FY2025 maintenance OE it screens as unownable at $13.03. The median ($0.81) is the honest middle for a full-cycle protein processor, and it still only supports $8.36 at a 15% discount rate.
- What the market price is paying for is cycle recovery: US beef spreads are at a cattle-supply trough, and JBS's diversification (poultry via Pilgrim's, Brazil, Australia, Seara) did visibly cushion it — sales records with only a small Q2 loss. That recovery is a real possibility, but in this system it has to be bought at the hurdle price, not at $13.03.
- Watch items: US cattle herd rebuilding (multi-year), the announced CEO transition to Wesley Batista Filho at the end of 2026 (family succession, governance-relevant), the Mantra/Danantara $2.5B minority investment in the Australia/NZ operations announced with Q2 2026, dividend capacity at 3.1x leverage ($1.00/share was paid in June 2026), and antitrust exposure in US packing.
- Data note: enrichment was run in the standard order after scoring (fundamentals, prices, segments, statements, profile, reprice) and all six succeeded; segments/statements note the usual 20-F limitation (interim reporting on 6-K only, so no quarterly statement tables), which is non-blocking and does not affect the score.

## Final verdict
- **Final tier: C** (weighted IRR 10.70% on the median base; bear D → bull C — size it as the bear end)
- Confidence: **Low** (3 filed years, OE spanning >3x, wide scenario spread, stale FY with no computable IFRS TTM, high leverage)
- One-liner: Global protein scale, moat 4/10, but a commodity cyclical — weighted IRR 10.7% (Tier C, bear D to bull C) at $13.03 vs weighted IV@15% $8.36; clears 15% only below ~$8.36, with net debt 19.0x normalized OE.
