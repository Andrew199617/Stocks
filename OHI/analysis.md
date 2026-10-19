# OHI — Omega Healthcare Investors, Inc.
Pass-1 v5 / engine 5.4.0 run, 2026-10-17. In scope (market cap $13.918B at $45.64, nasdaq_quote_api).

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.json, financials_history.csv or fundamentals.json — none are recomputed. External facts are from the Q2 2026 earnings reporting cited in the research notes.

## What it is
Self-administered healthcare REIT (Hunt Valley, MD; NYSE since 1992): roughly 900 skilled nursing and senior housing properties across 80+ operators in the U.S. and U.K., mostly long-term triple-net leases with contractual ~2% escalators, plus a growing RIDEA/operating (SHOP) book and real-estate loans. Q2 2026: revenue $328M (+16% YoY), AFFO $0.83/share (+7.8% YoY), FY2026 AFFO guidance raised to $3.22–$3.26/share, quarterly dividend raised $0.01 to $0.68 in August 2026. Portfolio pruning is active: $563M of Q2 asset sales including the $480M disposition of 18 CommuniCare facilities, proceeds used to pay the $2B revolver down to $6M drawn. Leadership transition: Q2 2026 was the final earnings call for CEO Taylor Pickett and CFO Bob Stephenson (retiring after ~25 years); President Matthew Gourmand leads the next team. October 5, 2026: 32 Florida skilled nursing facilities moved to PACS under Omega's master lease, adding $26.1M of scheduled rent in year one.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $878,551,000; capex (tag: PaymentsForConstructionInProcess) $33,589,000; SBC $44,189,000.
- **Conservative owner's earnings FY2025: $800,773,000 = $2.63/share** (key_numbers.md: latest FY OE/share $2.63)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC) FY2025 total: $881,843,000 — same ballpark as the conservative figure, which supports the base.
- OE positive 5 of the last 5 fiscal years. Net debt $4.229B (key_numbers.md).
- Caveat that defines this name: the capex tag captures only construction in process. Under triple-net leases the operators bear property maintenance capex, so the engine's OE is closer to a net cash-rent measure than to a fully-loaded economic owner's earnings — one reason the sector model fit is poor (see FLAGS). The sector's own yardstick, AFFO, is guided at $3.22–$3.26/share for 2026 — above OE/share because FFO adds back real-estate depreciation (D&A was $325,247,000 in FY2025).

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $878,551,000 − prior YTD $421,217,000 + current YTD $433,224,000 = **TTM $890,558,000**
- Capex: FY $33,589,000 − prior YTD $29,731,000 + current YTD $7,860,000 = **TTM $11,718,000**
- SBC: FY $44,189,000 − prior YTD $25,046,000 + current YTD $34,043,000 = **TTM $53,186,000**
- Shares (current-YTD weighted diluted): **315,690,000**
- **TTM OE total $825,654,000 → base OE/share $2.62** (base_source: ttm_json)
- The TTM base ($2.62) sits essentially on top of the latest FY ($2.63) and above the engine's normalized 3-yr median ($2.38), which is dragged by the FY2023 trough year ($2.15/share). TTM is the current, filing-derived figure, so it is the base; the median is retained in key_numbers.md for reference.

## Moat: 4/10 — weak-to-moderate
Justification: Scale and diversification are real (80+ operators, ~900 properties, long triple-net leases with ~2% escalators, BBB- access to unsecured debt) but the triple-net healthcare REIT model is replicable, pricing power stops at contractual escalators, and returns are a levered real-estate spread hostage to operator credit and Medicare/Medicaid reimbursement.
- FOR: Scale — ~900 properties across 80+ operators diversifies single-tenant rent risk; long-term triple-net leases with contractual ~2% escalators and TTM operator EBITDAR coverage improved to 1.65x (Q2 2026); investment-grade (BBB-) unsecured capital access with leverage cut to 3.3x net debt/adjusted EBITDA and the revolver nearly undrawn; demographic tailwind — aging population drives skilled nursing / senior housing demand with low new supply.
- AGAINST: Triple-net model is replicable — no network effects, no pricing power beyond contractual escalators; tenant credit is the business risk (Genesis bankruptcy, the CommuniCare exit, Maplewood stress); hostage to Medicare/Medicaid reimbursement policy; growth is bought with constant equity issuance — diluted shares +7.7%/yr, so per-share OE was flat FY2021–25 despite revenue growth; ROE only 6.8%–12.2% FY2021–25.
- Filing evidence on returns: fundamentals.json carries **no gross margin and no roic_proxy series for OHI** — the filings tag no COGS and no operating income in recent years, so neither series is computable from the filed data, and no figure is invented here. The return evidence that does exist is ROE (fundamentals.json): 11.0% (2021), 12.2% (2022), 6.8% (2023), 9.0% (2024), 11.4% (2025) — a levered real-estate return hovering around the cost of capital, not well above it through a cycle. That caps the moat at 4.
- A 4 gives CAP = 7.2 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 7.2 years, 15-year projection.

## DCF — final run (2026-10-17)
Growth recalibration (written reason): the engine blend is 6.93%, built from rev CAGR 5y 5.93%, rev CAGR 3y 10.66%, latest rev YoY 13.19% and OE/share CAGR 2y 10.54%. The 2-yr OE/share CAGR is a recovery artifact off the FY2023 trough ($2.15/share): OE/share was $2.48 in FY2021 and $2.63 in FY2025 — roughly flat over four years, because revenue growth is funded by share issuance (+7.67%/yr share CAGR). Scenario starts were therefore recalibrated down via offsets (−0.12 / −0.05 / −0.0193 / +0.0207 / +0.0707 vs g_base) to −5.1 / 1.9 / **5.0** / 9.0 / 14.0%. Even the recalibrated base start (5.0%) sits above the long-run per-share history; it is justified only by the current prints — Q2 2026 AFFO/share +7.8% YoY, revenue +16% YoY, coverage at 1.65x, and redeployment of the Q2 sale proceeds plus the PACS Florida rent addition. The super-bull start (14.0%) is still below the latest revenue YoY print (13.19% revenue, not per-share) only in spirit — no per-share series has ever printed 14%, so super bull is a genuine stretch case and carries only 10%. Probabilities 15/25/30/20/10 (extra super-bear weight for tenant credit and leverage); OE multipliers at the defaults 0.75/0.90/1.00/1.10/1.25. Price $45.64.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | -5.1% | 0.75 | Operator failures / reimbursement cut; rent relief and impairments | $11.98 | 5.57% |
| Bear | 25% | 1.9% | 0.90 | Escalators only; dilution eats acquisition growth | $18.88 | 7.65% |
| Base | 30% | 5.0% | 1.00 | AFFO-guide trajectory decays over the CAP | $23.60 | 9.04% |
| Bull | 20% | 9.0% | 1.10 | Redeployment + RIDEA upside compounds per-share | $30.22 | 10.93% |
| Super bull | 10% | 14.0% | 1.25 | Sustained double-digit per-share growth — never yet printed | $41.41 | 13.93% |

- **Probability-weighted: IV@15% $23.78 (−47.9% vs price), IV@12% $31.53, IV@10% $40.15, weighted IRR 9.12%, base-case IRR 9.04%**
- **Tier by numbers: D.** Even the super-bull case (13.93% IRR, IV@15 $41.41) does not clear 15% at $45.64. Diagnostics (key_numbers.md): OE yield 5.73%, terminal value 18.5% of IV@15%, scenario spread 3.46x, net debt 5.30x normalized OE, 9.5 months since FY end.
- Hurdle-clearing prices (weighted path): 15% at $23.78 · 20% at $16.81 · 25% at $12.96.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.5 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, legs quoted above. TTM OE/share ($2.62) ≈ latest FY ($2.63), so staleness is not distorting the base.
- **DILUTION** (share count +7.67%/yr): the driver is acquisition funding, not SBC alone. SBC rose from $21,415,000 (FY2021) to $44,189,000 (FY2025) to $53,186,000 TTM — a real and growing cost, already deducted in OE. The larger diluter is equity issuance: fundamentals.json records ProceedsFromIssuanceOrSaleOfEquity of $606,810,000 for the first nine months of 2025 (ATM/DRIP issuance funding acquisitions). The engine's −5.00pp growth adjustment on the revenue components is already applied; the scenario recalibration above is the second guard — revenue growth is not credited as per-share growth.
- **NI_OCF_DIVERGENCE** (2023, 2024): the one-off is structural, not a cash leak — real-estate depreciation. FY2023: net income $242,180,000 against OCF $617,736,000, with D&A of $319,682,000 the dominant reconciling item (plus operator-related impairments/reserves in the workout years). FY2024: net income $406,326,000 against OCF $749,430,000, with D&A of $304,648,000. Net income is depressed by depreciation on the property portfolio; the OCF-based conservative OE used throughout is unaffected by the divergence. (Note the mirror image is coming: Q2 2026 net income includes a $247M gain on the CommuniCare sale, which inflates NI, not OCF.)
- **SECTOR_MODEL_MISMATCH** (Real Estate): accepted — confidence is **low** and the name is listed under sector misfits. The OE/capex DCF understates a triple-net REIT's cash economics (capex tag = construction in process only; AFFO guide $3.22–$3.26 vs OE $2.62). The D tier is therefore a statement about this model at this price, cross-checked in Thoughts — not a claim that AFFO cash flow is about to fall.
- **HIGH_NET_DEBT** (net debt 5.30x normalized OE): balance sheet from the filing (financials_history.csv, FY2025): total debt $4,256,011,000 (tag LongTermDebt), cash $27,024,000, net debt $4,228,987,000. Against adjusted EBITDA the picture is milder — Q2 2026 reporting puts leverage at 3.3x net debt/adjusted EBITDA with fixed-charge coverage of 6.5x, the revolver at $6M drawn of $2B, and the next maturity in April 2027; total debt has fallen from $5,169,252,000 (FY2020). Leverage is real but termed-out and falling; the bear cases carry the stress (15% super-bear weight at a 0.75 OE multiplier).
- **TIER_BAND** (bear tier D at 7.65% vs bull tier C at 10.93%): the verdict is sized to the bear end — final tier D. Note the band is academic at this price: even the super-bull case does not reach the 15% hurdle.

## My thoughts / overlay
- The honest headline: at $45.64 the market is pricing OHI as an income vehicle (a ~5.7% dividend yield was reported in October 2026 coverage; the dividend was just raised for the first time in years and is covered by AFFO guidance), not as a 15%-IRR compounder. On owner's earnings, no scenario — including a super bull with growth and OE levels the company has never printed per-share — clears 15%. The price would need to roughly halve, to the $23.78 hurdle price, for the weighted path to clear 15%.
- Method range is narrow for once: the preliminary run (median base $2.38, default probabilities/offsets, moat 5) gave weighted IRR 9.60% and IV@15% $25.10; the final TTM run gives 9.12% / $23.78. Both are Tier D — the verdict does not depend on the base choice.
- The genuine bull case lives outside this model: AFFO/share compounding at the guided ~$3.24 with a growing RIDEA operating book, coverage at a 12-year high (1.65x), a cleaned-up tenant base post-CommuniCare/Genesis, and demographic demand. Even granting all of it, the entry price leaves the return at the dividend plus mid-single-digit per-share growth — a ~9–11% proposition (the bull case here: 10.93%), which is exactly what the DCF says.
- Risks to the D (i.e., what would make it worse): a Medicare/Medicaid reimbursement cut, another large operator failure, or rates staying high enough to close the equity-issuance window that funds growth. Risks to the verdict (what would make D too harsh): sustained AFFO/share growth above ~9% would lift the bull case over 15% only at a materially lower price — at $45.64 the arithmetic does not close.

## Final verdict
- **Final tier: D** (weighted IRR 9.12% on the TTM base; bear D 7.65% → bull C 10.93%; no scenario clears 15%)
- Confidence: **Low** (sector model misfit by construction; the OE base and TTM legs themselves are filing-clean)
- One-liner: Durable but commodity healthcare REIT, moat 4/10 — does not clear 15% on any scenario (weighted IRR 9.1%, IV@15% $23.78 vs $45.64 price); it only clears 15% at ~$23.78, roughly half the current price.

## Data / enrichment
- Enrichment completed with no failures: fundamentals.json, prices.json, segments.json, statements.json, profile.json + street.json (consensus Hold, n=16, target $50.64) and live.json all written. fundamentals.json carries no gross-margin or ROIC series for this filer (see Moat).
