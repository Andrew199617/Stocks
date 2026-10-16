# GH — Guardant Health, Inc.
v5 run, 2026-10-15. In scope (market cap $20.738B at $165.41, nasdaq_quote_api).

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.py output, or financials_history.csv — none are recomputed.

## What it is
Precision-oncology diagnostics: blood-based (liquid biopsy) cancer testing. Guardant360 for comprehensive genomic profiling / therapy selection (new FDA approval for Guardant360 Liquid CDx and a companion-diagnostic approval in HER2-mutant NSCLC in Q2 2026), Reveal for molecular residual disease / monitoring, Shield for colorectal cancer screening (FDA-approved blood test, added to American Cancer Society screening guidelines, first major commercial coverage from UnitedHealth Group in Q2 2026), plus biopharma & data services. Q2 2026 (search results, Business Wire release): total revenue $335.0M, +44% YoY — oncology $219.1M (+38%, ~104,000 tests), biopharma & data $60.9M (+9%), screening $52.9M (~66,000 Shield tests, vs $14.8M and 16,000 tests a year earlier); non-GAAP gross margin 67%; full-year 2026 revenue guidance raised to $1.34–$1.36B (+36% to +38%).

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** revenue $982,021,000; net income −$416,277,000; operating cash flow −$184,760,000; capex $48,306,000; SBC $166,217,000 (always a real cost).
- **Conservative owner's earnings FY2025: −$399,283,000 = −$3.18/share** (base_oe_latest_per_share in dcf_numbers.json).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): −$897,399,000 — far worse than the conservative figure, driven by the ΔNWC leg in financials_history.csv ($481,122,000 for FY2025); the OCF-based conservative figure is the cleaner series and is the one the engine uses.
- **OE positive 0 of the last 5 fiscal years** (dcf_numbers.json). This is not one bad year: conservative OE was negative in every year of the filed history shown in financials_history.csv, even as revenue compounded.
- Net debt $1,125,797,000 (dcf_numbers.json); cash $378,203,000 and long-term debt $1,504,000,000 in FY2025 (financials_history.csv).

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY −$184,760,000 − prior YTD −$122,974,000 + current YTD −$123,401,000 = **TTM −$185,187,000**
- Capex: FY $48,306,000 − prior YTD $10,108,000 + current YTD $17,339,000 = **TTM $55,537,000**
- SBC: FY $166,217,000 − prior YTD $80,219,000 + current YTD $105,333,000 = **TTM $191,331,000**
- Shares (current-YTD weighted diluted): **132,074,000**
- **TTM OE total −$432,055,000 → base OE/share −$3.27** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is −$3.38/share and the latest-FY figure is −$3.18/share. All three bases are negative and tightly clustered — there is no base choice that makes this DCF supportable. The TTM base was used because it is the most current, per the STALE_FY resolution below.

## Moat: 5/10 — moderate / narrow
Justification: a genuine technology and evidence lead in liquid biopsy with first-mover Shield in blood-based colorectal screening, but no demonstrated pricing power or profitability, payer-by-payer reimbursement, and well-funded rivals in every segment — the lead must be re-earned as sequencing costs and assay sensitivity move.
- FOR: Guardant360 installed oncologist base and clinical-evidence depth, extended by the FDA-approved Liquid CDx panel and companion-diagnostic approvals
- FOR: Shield is the first FDA-approved blood test for colorectal screening, now in ACS guidelines with first major commercial coverage (UnitedHealth) — a first-mover position in a very large screening market
- FOR: Reveal MRD / monitoring as a second growth leg on the same platform, plus biopharma & data revenue from pharma partnerships
- FOR: Platform scale lowering per-test cost (higher-throughput Shield workflow and sequencer transition reported in Q2 2026 results coverage)
- AGAINST: Competition in every leg — Exact Sciences (Cologuard, profitable and entrenched in CRC screening), Natera (MRD), Roche / Foundation Medicine, Grail and Tempus
- AGAINST: Reimbursement is payer-by-payer and policy-dependent; early-stage sensitivity limits mean tissue testing is not displaced
- AGAINST: No profitability through a cycle — losses persist at ~$1B revenue scale, so returns on capital are unproven and negative
- AGAINST: Growth is funded by shareholders — SBC rising every year and repeated equity / convertible issuance (a ~$300M equity offering and $350M convertible notes in late 2025, per search results)
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection. (Moot for the tier here — see DCF.)

## DCF — v5 final run (2026-10-15)
Growth sanity check: the revenue growth is real — rev CAGR 5y 27.92%, rev CAGR 3y 29.75%, latest FY YoY +32.88% (dcf_numbers.json growth_components), Q2 2026 +44% and 2026 guidance +36% to +38% (search results). The engine's blended growth is 29.75% before the −5pp share-count adjustment. None of that rescues the DCF: **with a negative base OE/share, the engine emits no scenarios, no IV and no IRR** — multiplying a negative base by any scenario multiplier or growing it at any rate is not a valuation. Defaults were passed anyway (probabilities 10/25/30/25/10, offsets −12/−5/0/+5/+12pp, multipliers 0.75/0.90/1.00/1.10/1.25, moat 5) so the run is on the standard configuration.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | — | 0.75 | Not computable — negative base OE | — | — |
| Bear | 25% | — | 0.90 | Not computable — negative base OE | — | — |
| Base | 30% | — | 1.00 | Not computable — negative base OE | — | — |
| Bull | 25% | — | 1.10 | Not computable — negative base OE | — | — |
| Super bull | 10% | — | 1.25 | Not computable — negative base OE | — | — |

- **Probability-weighted IV/IRR: none. Tier by numbers: F** (no positive normalized conservative owner's earnings — OE DCF not supportable on numbers alone).
- Diagnostics: price $165.41; market cap $20.738B; net debt $1,125,797,000; OE positive 0/5 years; share count growing 7.1%/yr.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9 months ago): resolved by construction — ttm.py was run and the final engine pass uses the TTM base from ttm.json through Q2 2026, quoted in full above. TTM OE/share −$3.27 confirms the FY picture instead of reversing it.
- **DILUTION** (share count growing 7.1%/yr): real and worsening. Diluted shares rose from 111,988,000 (FY2023) to 122,745,000 (FY2024) to 125,374,000 (FY2025) in financials_history.csv, and the TTM current-YTD figure is 132,074,000 (ttm.json). SBC — the driver — rose from $90,759,000 (FY2023) to $140,411,000 (FY2024) to $166,217,000 (FY2025), with TTM SBC of $191,331,000. The engine already deducts 5pp via the share-count adjustment; on a negative base the point is simpler — per-share economics deteriorate every year the count grows at this rate while OE stays negative.
- **NI_OCF_DIVERGENCE** (2023, 2024, 2025): not a one-off tax deposit or impairment — it is structural non-cash addbacks. In each year OCF is far less negative than net income (FY2025: NI −$416,277,000 vs OCF −$184,760,000; FY2024: −$436,373,000 vs −$239,858,000; FY2023: −$479,449,000 vs −$324,975,000, all from financials_history.csv), and the filed SBC ($166,217,000 in FY2025) and D&A ($39,736,000 in FY2025) are the non-cash items added back to net income to reach OCF. The divergence therefore does not hide cash earnings: the conservative OE definition subtracts SBC again precisely because it is a real, recurring cost, and OE is negative on either side of the divergence.

## My thoughts / overlay
- This is a growth-equity story priced at $165.41 / $20.7B on revenue momentum (+44% in Q2 2026, guidance raised), not an owner's-earnings story. On this sweep's method there is no method range to report: the FY base, the 3-yr median base and the TTM base are all negative (−$3.18 / −$3.38 / −$3.27 per share), so every defensible input lands on F.
- What would have to change: sustained positive operating cash flow after SBC — i.e. Shield and oncology volume growth converting into operating leverage faster than the commercial spend management is deliberately reinvesting (management commentary in search results targets company-wide cash-flow breakeven around end-2027, while guiding to continued heavy screening investment). Until filed OCF minus capex minus SBC turns positive, there is nothing for a DCF on owner's earnings to discount.
- Balance sheet: net debt $1,125,797,000 against persistently negative OE, with growth funded by SBC, equity issuance and convertible debt — dilution is not a tail risk here, it is the funding model so far.
- Hurdle-clearing price: not computable from this model — with no positive OE base there is no IV@15% at any price, and stating one would require a different (revenue / forward-earnings) model, which is out of scope for this sweep. No tier override: the numbers tier F is retained.

## Final verdict
- **Final tier: F** (weighted IRR / IV@15%: none — no positive conservative owner's earnings in any of the last 5 years or on TTM)
- Confidence: **Low** (high confidence in the negative OE arithmetic from filings; low confidence in any forward path — the investment case rests entirely on growth and eventual operating leverage that have not yet appeared in filed cash flows)
- One-liner: High-growth liquid-biopsy leader, moat 5/10, but owner's earnings are negative in all of the last 5 years and on TTM (base −$3.27/share at $165.41) — Tier F on this screen; it does not clear 15% and no hurdle-clearing price is computable on a negative OE base.
