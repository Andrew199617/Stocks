# HST — Host Hotels & Resorts, Inc.
Engine 5.4.0 pass-1 run, 2026-10-16. Price $23.97 (nasdaq_quote_api), market cap $16.64B — in scope under $40B.

All figures below are copied from dcf_numbers.json, ttm.json, fundamentals.json, or financials_history.csv — none are recomputed.

## What it is
The largest lodging REIT in the US (S&P 500): roughly 76 luxury and upper-upscale hotels, ~41,700 rooms, in top urban, resort and convention markets, operated under Marriott, Ritz-Carlton, Hyatt, Hilton, Fairmont and Westin brands via long-term management agreements. Host owns the real estate; the brands run the hotels and own the guest relationship.

## Owner's earnings
**FY2025 (10-K via EDGAR, financials_history.csv):** OCF $1,510M; capex $362M; SBC $26M.
- Conservative OE FY2025: $1,122M = $1.62/share. Maintenance OE FY2025: $1,198M — same ballpark.
- Engine normalized base (median of last 3 FY OE/share): $1.62/share (FY2023 $1.35, FY2024 $1.68, FY2025 $1.62).
- OE positive 5 of the last 5 fiscal years on the engine's window, but the longer history includes the COVID collapse: FY2020 OCF was −$307M and OE/share was deeply negative, FY2021 OE/share $0.20.
- Net debt $506M (net_debt_to_normalized_oe 0.40x on the TTM base), plus lease liabilities $563M. Balance sheet is a genuine strength: Q2 2026 reporting put leverage at 2.2x with ~$3B liquidity, and H1 2026 asset sales produced $1.07B of net proceeds.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct):**
- OCF: FY $1,510M − prior YTD $749M + current YTD $845M = **TTM $1,606M**
- Capex: FY $362M − prior YTD $189M + current YTD $140M = **TTM $313M**
- SBC: FY $26M − prior YTD $11M + current YTD $12M = **TTM $27M**
- Shares (current-YTD weighted diluted): **688,100,000**
- **TTM OE total $1,266M → base OE/share $1.84** (base_source: ttm_json)
- Caveat on the capex leg: management guides 2026 capital expenditures of roughly $550–630M (including transformational renovation programs), roughly double the TTM filed capex of $313M. To the extent that spend is maintenance rather than growth, the TTM OE base is flattered. This is stated, not adjusted — no override was taken.

## Moat: 4/10 — weak-to-moderate
Justification: irreplaceable prime locations and scale give real asset-level advantages, but Host owns no brand, no guest relationship and no pricing system — the operators do — and lodging is deeply cyclical with heavy ongoing capex needs.
- FOR: Largest lodging REIT — scale in acquiring prime assets and negotiating with the major managers; luxury/upper-upscale portfolio in supply-constrained top markets that peers cannot replicate; investment-grade, largely unencumbered balance sheet (net debt 0.40x normalized OE) that lets it buy through downturns; renovation programs have produced documented RevPAR index share gains (~9 points average across 21 renovated properties per Q2 2026 reporting).
- AGAINST: No owned brand or loyalty program — Marriott/Hyatt/Hilton own the guest and charge management/loyalty fees; hotels are capex-hungry (guided 2026 capex ~$550–630M vs TTM OE of $1,266M); extreme cyclicality — FY2020 revenue fell to $1,620M from $5,469M and OCF went negative; labor and insurance cost inflation pressures margins; business travel remains softer than pre-pandemic norms.
- ROIC evidence (fundamentals.json roic_proxy): FY2022 10.95%, FY2023 12.66%, FY2024 12.34%, FY2025 11.48% — respectable and fairly stable in good years, but FY2020 −17.0% and FY2021 −3.25% show it collapses through a downturn, so it has NOT stayed above the cost of capital through a full cycle. Gross margin is not filed in a usable form for this REIT (fundamentals.json gross_margin is null for every year); operating margin ran 14.0–15.8% over FY2022–25. That evidence supports 4, not a higher score.
- A 4 gives CAP = 7.2 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 7.2 years, 15-year projection.

## DCF — final run (2026-10-16)
Growth recalibration (written reason): the engine's blended start is 9.13%, but it is built on COVID-rebound artifacts — the 5-yr revenue CAGR of 30.43% straddles the 2020 collapse, and the OE/share CAGR is measured off depressed bases. The prints that describe the current business are much lower: FY2025 revenue YoY +7.57%, TTM revenue YoY +4.93% (fundamentals.json), Q2 2026 revenue +3.4% with comparable RevPAR +7.0%, and raised FY2026 guidance of 4.75–5.25% comparable RevPAR growth (which itself includes a ~70bp World Cup contribution). Scenario starts were therefore set via offsets (−0.1213 / −0.0713 / −0.0413 / −0.0113 / +0.0287 vs the blended start) to −3 / 2 / **5** / 8 / 12%. Probabilities 15/30/30/15/10 — bear-weighted for cyclicality and the sector misfit; OE multipliers are the defaults 0.75/0.90/1.00/1.10/1.25.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | −3.0% | 0.75 | Recession hits lodging as in past downturns; RevPAR falls | $9.14 | 7.09% |
| Bear | 30% | 2.0% | 0.90 | Rate growth normalizes post-World Cup; cost inflation bites | $13.32 | 9.43% |
| Base | 30% | 5.0% | 1.00 | Guidance-level RevPAR growth decaying over the CAP | $16.60 | 11.22% |
| Bull | 15% | 8.0% | 1.10 | Renovation index gains + group strength persist | $20.47 | 13.24% |
| Super bull | 10% | 12.0% | 1.25 | Sustained luxury outperformance, Maui stabilization upside | $27.04 | 16.48% |

- **Probability-weighted: IV@15% $16.12 (−32.7% vs price), IV@12% $21.33, IV@10% $27.14, weighted IRR 10.97%, base-case IRR 11.22%**
- **Tier by numbers: C.** Bear tier D (9.43%), bull tier C (13.24%). Hurdle price at 15%: $16.12.
- Diagnostics (dcf_numbers.json): OE yield 7.68%, terminal value 18.3% of IV@15%, scenario spread 2.96x, net debt 0.40x normalized OE, 9.5 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.5 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, quoted above.
- **BASIS_BREAK_SUSPECT**: the break is COVID, not a divestiture or restatement — FY2020 revenue fell ~70% to $1,620M and rebounded through FY2022. Any CAGR straddling 2020 is meaningless; growth inputs were set from FY2025 YoY, TTM YoY, Q2 2026 prints and FY2026 guidance instead (see the recalibration note).
- **OE_VOLATILE** (OE/share spans >3x over 5 years): real cyclicality — negative in FY2020, $0.20 in FY2021, $1.35–1.68 since. Handled by bear-weighted probabilities (45% on bear-or-worse) rather than by pretending the normalized base removes it.
- **NI_OCF_DIVERGENCE** (2023, 2024): explained by depreciation, not a one-off tax deposit or working-capital swing — D&A was $697M in FY2023 and $762M in FY2024 against net income of $740M and $697M, so NI + D&A lands on OCF ($1,441M / $1,498M) as expected for a real-estate owner. The OCF-based conservative OE used throughout is unaffected.
- **SECTOR_MODEL_MISMATCH**: confirmed — Host is a lodging REIT (SIC 6798); the OE/capex DCF fits it poorly versus the FFO/AFFO framework the market uses (guided FY2026 adjusted FFO $2.15–2.18/share). Confidence is low and the name belongs with the sector misfits.
- **WIDE_SCENARIO_SPREAD** (preliminary run, 4.47x): the recalibrated final run narrows the IV@15 spread to 2.96x because the super-bull start no longer extrapolates the COVID rebound. Uncertainty is still wide in IRR terms (7.1% to 16.5%); confidence is not high.
- **TIER_BAND** (bear D 9.43% vs bull C 13.24%): the verdict spans tiers — sized to the bear end, per the verdict below.

## My thoughts / overlay
- The honest headline is the method range: on the engine's preliminary inputs (median base $1.62, 9.13% blended growth) the weighted IRR was 12.42%; on the TTM base with growth recalibrated to current prints it is 10.97%. Both are Tier C, and both sit well below the $23.97 price — the disagreement is about how far below, not about whether it clears 15%. It does not, in any scenario except super bull.
- Quality is real but it is asset quality, not franchise quality: prime hotels, a strong balance sheet, disciplined capital recycling ($1.07B of H1 2026 sale proceeds, a $0.72 special dividend declared from sale gains, $0.20 regular quarterly dividend). None of that creates the compounding the DCF rewards — the cash yield is the return, and at $23.97 the OE yield of 7.68% plus mid-single-digit growth does not reach a 15% hurdle.
- The capex caveat cuts against the stock: if a normalized year really costs ~$550M+ of capex rather than the TTM-filed $313M, true OE/share is materially below $1.84 and the weighted IRR falls further. The Tier C here is, if anything, generous.
- What would change the answer: a price near $16 (the 15% hurdle price), or evidence that renovation-driven RevPAR index gains compound at high-single-digit rates for years rather than fading.

## Final verdict
- **Final tier: C** (weighted IRR 10.97%; bear end is D at 9.43% — size to that)
- Confidence: **Low** (sector model mismatch per spec; REIT graded on an OE/capex DCF)
- One-liner: High-quality lodging REIT with a weak franchise moat 4/10 — at $23.97 it does not clear 15% (weighted IRR 11.0%, IV@15% $16.12); it would need ~$16 to clear.
