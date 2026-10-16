# FCNCA — First Citizens BancShares, Inc.

v5 run, 2026-10-15. Market cap $27.048B at $2,080.19 (nasdaq_quote_api) — in scope under $40B.

All figures below are copied from dcf_numbers.json, financials_history.csv, or key_numbers.md — none are recomputed.

## What it is
Raleigh, NC bank holding company (First-Citizens Bank & Trust), founded 1898. Transformed twice by acquisition: CIT Group (closed January 2022) and the FDIC-assisted purchase of Silicon Valley Bank's loans and deposits on March 27, 2023. Now a top-20 US bank: Q2 2026 deposits $173.43B, loans and leases $151.03B, net interest margin 3.10%, CET1 ratio 10.77% (Q2 2026 results via StockTitan summary). Segments include general commercial/retail banking, the former SVB innovation/fund banking franchise, and CIT's commercial finance and rail businesses. A BMO branch acquisition (~$5.3B of deposits, ~$700M of loans) was expected to close in Q3 2026. Next earnings: Q3 2026 on October 23, 2026.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $2,923,000,000; capex $710,000,000 (tag PaymentsToAcquirePropertyPlantAndEquipment); SBC $0 as filed (tag ShareBasedCompensation).
- **Conservative owner's earnings FY2025: $2,213,000,000 = $170.20/share** (base_oe_per_share in dcf_numbers.json).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $2,206,000,000 — essentially identical to the conservative figure, because for this filer both collapse toward net income ($2,206,000,000 in FY2025). That agreement is mechanical, not corroborating: for a bank, OCF and capex are not the earnings drivers (see SECTOR_MODEL_MISMATCH below).
- Recent history (conservative OE): FY2023 $2,250,000,000; FY2024 $2,559,000,000; FY2025 $2,213,000,000. OE positive 4 of the last 5 fiscal years (FY2021 was −$391,000,000, an OCF-driven negative in the CIT closing period).
- Net debt per the engine: $35,784,000,000 (see HIGH_NET_DEBT below).

**Base used = the engine's normalized base, median of last 3 FY OE/share = $170.20/share** (base_source: median_of_last_3_fy_oe_per_share; the latest FY figure is also $170.20/share, so there is no BASE_DIVERGENCE flag).
- STALE_FY handling: `ttm.py FCNCA` exited non-zero with: "ttm.py: cannot compute TTM for FCNCA (CIK 798941): sbc: no post-FY YTD fact (no 10-Q since the 2025-12-31 fiscal year end)". No TTM base was therefore pinned; the engine's median base is used, with the reason stated here as required. Cross-check from reported quarters (search results, not used as model inputs): Q1 2026 net income $534M and Q2 2026 net income $672M, Q2 adjusted EPS $57.09, net interest income $1.66B — a run-rate consistent with the FY2025 base being roughly current, not stale in substance.

## Moat: 4/10 — weak-to-moderate
Justification: a real niche in innovation/fund banking inherited from SVB and a disciplined relationship-banking franchise, but core banking products are commodities, spreads are rate-hostage, and there is no network effect or structural cost advantage (efficiency is mid-pack).
- FOR: SVB innovation-banking and fund-banking franchise — specialized, relationship-sticky venture/tech client base few regionals can replicate; conservative, family-led underwriting culture with a long record of opportunistic, discount-priced acquisitions (CIT, SVB with FDIC support, BMO branches); large, diversified deposit base ($173.43B at Q2 2026) funding loan growth; capital building (CET1 10.77% at Q2 2026) plus heavy buybacks ($600M in Q2 2026, $1.5B in H1 2026).
- AGAINST: commodity products — loans and deposits compete on price, switching costs are low outside the innovation niche; earnings hostage to rates, deposit repricing and the credit cycle (CRE and venture exposures included); the SVB deposit/client base already proved flight-prone in a stress event and is concentrated in the cyclical venture economy; SVB purchase-accounting accretion fades over time, removing a reported-earnings tailwind; no cost leadership — expenses run at a mid-60s efficiency level per Q2 2026 reporting.
- A 4 gives CAP = 7.2 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 7.2 years, 15-year projection.

## DCF — v5 final run (2026-10-15)
Growth recalibration (written reason, required by the sanity-check rule): the engine's blended growth is 14.11% and g_base is 19.11% after the +5pp buyback adjustment — both are basis-break artifacts. The revenue CAGRs (5-yr and 3-yr both 23.36%) straddle the CIT (2022) and SVB (2023) balance-sheet step-ups, while the company's actual recent prints are flat-to-low-single-digit: latest FY revenue YoY −2.22% (dcf_numbers.json), Q2 2026 revenue +2.5% YoY and net interest income −2.3% YoY (search results), with sell-side FY earnings growth expectations around +2.3%. Scenario starts were therefore set via offsets (−0.2211 / −0.1911 / −0.1511 / −0.1211 / −0.0911 vs g_base) to −3 / 0 / **4** / 7 / 10%. Probabilities were skewed defensive (15/30/30/20/5 vs the 10/25/30/25/10 default) because purchase-accounting accretion fades, the growth evidence is thin, and this is a bank model fit graded low-confidence. OE multipliers are the defaults 0.75/0.90/1.00/1.10/1.25. Price $2,080.19.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | −3.0% | 0.75 | Credit cycle hits CRE/venture book; accretion fades; deposit costs bite | $845.86 | 7.41% |
| Bear | 30% | 0.0% | 0.90 | Flat earnings — NIM pressure offsets loan growth and buybacks | $1,140.65 | 9.28% |
| Base | 30% | 4.0% | 1.00 | Low-single-digit earnings growth plus buyback shrink, fading over the CAP | $1,478.56 | 11.42% |
| Bull | 20% | 7.0% | 1.10 | Innovation banking recovers with the venture cycle; BMO deal adds deposits cheaply | $1,823.61 | 13.51% |
| Super bull | 5% | 10.0% | 1.25 | Another discount acquisition or a strong venture/credit upcycle compounds book value | $2,321.19 | 16.36% |

- **Probability-weighted: IV@15% $1,393.43 (−33.01% vs price), IV@12% $1,837.71, IV@10% $2,331.80, weighted IRR 10.90%, base-case IRR 11.42%**
- **Tier by numbers: C.** Diagnostics (dcf_numbers.json): OE yield 8.18%, terminal value 18.02% of IV@15%, scenario spread 2.74x, net debt 16.17x normalized OE, 9.46 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.46 months ago): ttm.py was run and failed — "sbc: no post-FY YTD fact (no 10-Q since the 2025-12-31 fiscal year end)" — so no TTM pin exists and the median-of-3-FY base is used, per spec. Q1/Q2 2026 reported results (above) are consistent with that base, so the staleness is a filing-tag artifact, not an earnings break.
- **BUYBACK_TAILWIND** (share count shrinking 5.8%/yr): real and continuing ($1.5B repurchased in H1 2026). It is already credited via the +5pp share-count adjustment inside g_base; because the scenario starts were recalibrated off actual prints rather than taken from g_base, the tailwind is reflected in the per-share growth starts and is not double-counted in the verdict.
- **BASIS_BREAK_SUSPECT**: identified — two of them. CIT Group closed January 2022 and SVB's loans/deposits were acquired March 27, 2023. Revenue stepped from the pre-deal base to $5,082,000,000 in FY2022 and $18,787,000,000 in FY2023 (financials_history.csv; the filed "Revenues" tag also changes character post-deal). No CAGR spanning 2021–2023 is an organic growth rate; that is exactly why the engine's 23.36% revenue CAGRs and 19.11% g_base were rejected and scenario starts were anchored to current prints instead.
- **NI_OCF_DIVERGENCE** (2023): identified — FY2023 net income was $11,466,000,000 vs OCF of $2,660,000,000 (financials_history.csv). The gap is the one-off, non-cash bargain purchase gain on the SVB acquisition: $9.82B net of tax booked in Q1 2023 (Reuters, May 10 2023). It never entered OCF, so the OCF-based conservative OE series used for the base is uncontaminated by it; the gain is excluded from any earnings-power read.
- **SECTOR_MODEL_MISMATCH** (Finance): accepted in full. For a bank, deposits and borrowings are raw material, capex is trivial next to the balance sheet, and OCF swings with loan/deposit flows rather than earnings — the OE/DCF frame is a rough screen here, not a valuation. Confidence is graded **low** and the tier is soft; tangible book value and ROE would be the primary frame for a real decision (reported tangible book value per share was ~$1,722 at Q2 2026 per search results, i.e. the price is a modest premium to tangible book).
- **HIGH_NET_DEBT** (net debt 16.17x normalized OE): for a bank this ratio is structural, not a corporate-leverage alarm — the engine's net debt ($35,784,000,000) counts borrowings while the deposit base that funds the loan book sits outside it. The leverage gauge that matters is regulatory capital: CET1 10.77% at Q2 2026. The flag is still honored in the scenario design: bear and super-bear carry 45% combined probability and OE multipliers of 0.90/0.75, because a levered balance sheet is precisely how bank OE vanishes in a credit event.
- The preliminary run's **WIDE_SCENARIO_SPREAD** (4.38x) was an artifact of the un-recalibrated 19.11% g_base; on the final inputs the spread is 2.74x and the flag no longer fires. Confidence is still low — because of the sector mismatch, not the spread.

## My thoughts / overlay
- The method range here is mostly a growth-input range, not a base range (latest FY and 3-yr median OE/share coincide at $170.20): at the engine's unadjusted g_base the preliminary run printed Tier B (weighted IRR 19.26%) — a number built entirely on acquisition-stepped CAGRs — while the print-anchored final run prints Tier C at 10.90%. The honest headline is the second one; the first is the basis-break bug the sanity-check rule exists to catch.
- Quality is decent, price is the problem: this is a well-run, well-capitalized acquirer, but at $2,080.19 the stock already pays for mid-single-digit compounding. Even the super-bull case (10% start, 1.25x OE) only reaches a 16.36% IRR.
- The price that clears Andrew's 15% hurdle on the weighted case is the weighted IV@15% itself: **$1,393.43** — about a third below the current price. With any margin of safety against the bear cases (bear IV@15% $1,140.65), an entry would need to be lower still.
- Watch items: Q3 2026 results on October 23, 2026 (first quarter including the BMO branches), the pace of SVB accretion fade, venture-economy deposit stability, and whether buybacks at this price continue — repurchasing above IV@15% destroys the per-share value the buyback tailwind is supposed to create.

## Final verdict
- **Final tier: C** (weighted IRR 10.90% on the v5 final inputs; no tier override — the numbers tier stands, graded soft because of the sector model mismatch)
- Confidence: **Low** (SECTOR_MODEL_MISMATCH: the OE/capex DCF fits a bank poorly, per the standing rule for Finance names)
- One-liner: Quality regional bank with a real innovation-banking niche, moat 4/10 — but at $2,080.19 it doesn't clear 15% (weighted IRR 10.9%, IV@15% $1,393.43); it clears the hurdle only at or below ~$1,393.
