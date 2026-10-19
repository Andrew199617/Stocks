# NBIX — Neurocrine Biosciences, Inc.

Engine 5.4.0 run, 2026-10-17. Price $135.71 (nasdaq_quote_api), market cap $13.91B — in scope under $40B.

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.json, fundamentals.json, or financials_history.csv — none are recomputed by hand beyond quoting a ratio of two printed figures, which is shown as such.

## What it is
San Diego biotech (SIC 2836, large accelerated filer) with three first-in-class commercial products in CNS/endocrine:
- **INGREZZA (valbenazine)** — VMAT2 inhibitor for tardive dyskinesia and Huntington's disease chorea; the revenue engine (~75% of sales). Q2 2026 net sales $716M, +15% YoY; FY2026 guidance raised to $2.825–2.875B.
- **CRENESSITY (crinecerfont)** — CRF1 antagonist for classic congenital adrenal hyperplasia, approved Dec 2024; $301M in its first full year (FY2025), Q2 2026 sales $184M (+247% YoY), still only ~15% of the diagnosed CAH population per company commentary.
- **VYKAT XR (diazoxide choline)** — first FDA-approved treatment for Prader-Willi syndrome, acquired with Soleno Therapeutics (closed May 18, 2026, ~$2.9B); contributed $54M in the partial Q2 2026 quarter after closing.
- Pipeline optionality is 2027-weighted: Phase 3 readouts for osavampator (major depressive disorder) and direclidine / NBI-1117568 (schizophrenia, muscarinic M4) — binary events the current OE base does not depend on but the price partly does.
- Total revenue: FY2025 $2,860.5M (+21.4% YoY); Q2 2026 $959M (+39% YoY, acquisition-inflated — see growth check); TTM revenue $3,373.9M (fundamentals.json).

## Owner's earnings
**FY2025 (10-K via EDGAR, financials_history.csv):** OCF $782.7M; capex $34.0M; SBC $217.9M (always a real cost).
- **Conservative owner's earnings FY2025: $530.8M = $5.18/share** (latest FY OE/share in dcf_numbers.json).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $396.3M — lower than the conservative figure because FY2025 net working capital absorbed $82.3M (receivables scaling with the Crenessity launch and Ingrezza growth); the OCF-based conservative figure is the cleaner series here.
- OE positive 5 of the last 5 fiscal years, and rising every year: OE/share $1.01 (2021) → $1.51 (2022) → $1.66 (2023) → $3.49 (2024) → $5.18 (2025). SBC is heavy — $234.5M TTM, ~26% of TTM OCF — and is fully deducted in the base; dilution is modest (share count CAGR +1.20%/yr, dcf_numbers.json).

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $782,700,000 − prior YTD $166,800,000 + current YTD $282,200,000 = **TTM $898,100,000**
- Capex: FY $34,000,000 − prior YTD $23,200,000 + current YTD $16,900,000 = **TTM $27,700,000**
- SBC: FY $217,900,000 − prior YTD $105,600,000 + current YTD $122,200,000 = **TTM $234,500,000**
- Shares (current-YTD weighted diluted): **103,800,000**
- **TTM OE total $635,900,000 → base OE/share $6.1262** (base_source: ttm_json)
- The TTM base is, if anything, conservative on Vykat: the TTM window contains only ~6 weeks of Vykat XR post-close (Soleno closed May 18, 2026), so a full-year Vykat contribution is not yet in the run-rate OE.
- The engine's normalized base (3-yr median) is $3.4879/share — rejected as the base: the median year is FY2024, and the OE/share series ($1.66 → $3.49 → $5.18 → $6.13 TTM) shows a business compounding through it, not oscillating around it. The median is reported here and in key_numbers.md, and the method range below shows what it does to the verdict.

## Moat: 6/10 — moderate-strong patent/franchise moat, finite life
Evidence first (fundamentals.json): **ROIC proxy** (after-tax operating income over equity + debt − cash) — 2021 8.8%, 2022 12.4%, 2023 9.5%, 2024 17.0%, 2025 16.5%: mid-teens and rising, above a biotech cost of capital, and understated because the denominator carries a ~$2.5B cash/securities pile earning deposit rates rather than product returns. **Gross margin** (gross profit / revenue, both from fundamentals.json annual rows): FY2023 $1,847.4M / $1,887.1M, FY2024 $2,321.3M / $2,355.3M, FY2025 $2,808.4M / $2,860.5M — ~98% every year, the classic patent-protected pharma signature. That supports a 6, not a 7+: the returns history above the cost of capital is only ~2 years long at the current level, and the moat is patent-dated, not structural.
- FOR: Patent exclusivity on valbenazine (patent estate extending toward 2032; generic insulation into ~2029 per company/analyst reporting) with ~60% share of new tardive-dyskinesia prescriptions and once-daily dosing vs Teva's Austedo; first-in-class monopoly positions in CAH (Crenessity, only CRF1 antagonist) and Prader-Willi (Vykat XR, first approved therapy); ~98% gross margins = proven pricing power; established specialty commercial infrastructure across neurology and endocrinology that each new product reuses.
- AGAINST: Concentration — Ingrezza is still ~75% of revenue (Q2 2026: $716M of $959M), so the franchise is one patent cliff (early 2030s) from a very different company; Austedo XR is a real, growing VMAT2 competitor; Medicare/IRA price negotiation is a structural overhang for a high-list-price specialty drug; the post-Ingrezza story depends on binary 2027 Phase 3 readouts (osavampator, direclidine) and on muscarinic competition from BMS's Cobenfy; SBC runs ~26% of OCF.
- A 6 gives CAP = 9.8 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 9.8 years, 15-year projection.

## DCF — final run (2026-10-17)
Growth sanity check (mandatory): the engine's blended start is 22.11% (components: revenue CAGR 5y 22.29%, 3y 24.31%, latest FY YoY 21.45%, OE/share CAGR 2y 76.74% — the last is an inflection artifact off the small FY2023 base and the blend's median correctly mutes it). Recent prints: FY2025 revenue +21.4%, TTM revenue +34.4% (fundamentals.json), Q2 2026 total revenue +39% YoY. **The bull (27.11%) and even super-bull (34.11%) starts sit at or below the latest quarterly print — written reason:** the +39% Q2 print is not the organic run rate — it bundles ~6 weeks of acquired Vykat XR revenue and Crenessity's +247% growth off a launch-quarter base, while Ingrezza (~75% of sales) grew +15% in Q2 and is guided to ~+13% for FY2026. A blended organic start in the low-20s (base case) with a 27% bull is the honest read of those prints; default offsets (−12/−5/0/+5/+12pp) and default OE multipliers (0.75/0.90/1.00/1.10/1.25) were kept. Probabilities kept at defaults 10/25/30/25/10 — 35% on bear-or-worse already reflects the OE_VOLATILE flag's instruction to widen bear weight. Price $135.71.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | 10.11% | 0.75 | Austedo XR takes share, IRA pricing bites, 2027 readouts fail | $52.84 | 7.69% |
| Bear | 25% | 17.11% | 0.90 | Ingrezza decelerates to guide, Crenessity ramp slows | $86.44 | 10.95% |
| Base | 30% | 22.11% | 1.00 | Current trajectory decays normally over the CAP | $119.63 | 13.76% |
| Bull | 25% | 27.11% | 1.10 | Crenessity + full-year Vykat compound; pipeline de-risks | $163.60 | 16.98% |
| Super bull | 10% | 34.11% | 1.25 | 2027 Phase 3 wins open MDD/schizophrenia franchises | $251.19 | 22.16% |

- **Probability-weighted: IV@15% $128.80 (−5.1% vs price), IV@12% $180.01, IV@10% $238.31, IV@20% $84.37, IV@25% $61.05; weighted IRR 14.48%, base-case IRR 13.76%**
- **Tier by numbers: C.** Bear→bull band C (10.95%) → B (16.98%). Diagnostics: OE yield 4.51%, terminal value 24.1% of IV@15%, scenario spread 4.75x, 9.5 months since FY end.
- **Hurdle-clearing price: $128.80 at 15%** — the $135.71 price sits ~5% above it. On the rejected median base ($3.4879) the same model printed weighted IRR 9.40% / IV@15% $68.01 (Tier D) in the preliminary run — that is the method range (D→C), and the TTM end is the defensible one for the reasons under BASE_DIVERGENCE.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.5 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, legs quoted above.
- **BASE_DIVERGENCE** (latest FY $5.18 vs 3-yr median $3.49): the median is the distorted one — it is FY2024's figure, and OE/share has compounded $1.66 → $3.49 → $5.18 → $6.13 TTM since. This is a growth ramp (Ingrezza scale + Crenessity launch), not a one-year spike: revenue grew every year and OCF rose $389.9M → $595.4M → $782.7M over FY2023–25. TTM base used; median retained in the reporting and the method range.
- **OE_VOLATILE** (OE/share range >3x over 5 yrs): real but mislabeled by the flag — the span is a monotone ramp ($1.01 → $5.18), not cyclicality; there is no down year in the last five. Handled by keeping 35% probability on bear-or-worse and by the TIER_BAND sizing rule.
- **NI_OCF_DIVERGENCE** (2024): FY2024 net income $341.3M vs OCF $595.4M — a $254.1M gap, of which SBC $195.5M + D&A $23.5M = $219.0M is non-cash addback (figures from financials_history.csv); the remainder is working-capital/timing. No one-off (no tax deposit, impairment, or settlement) is needed to explain it, and since the conservative OE deducts SBC in full, the divergence does not inflate the base — it is exactly why the OCF−SBC definition is the right one here.
- **DEBT_TAGS_BLANK** (no debt tag for the latest FY): stated from the filing — the FY2025 balance sheet (10-K; comparative column in the Q1 2026 10-Q) carries **no funded debt at all**: cash $713.0M plus available-for-sale securities $767.4M current + $1,063.0M noncurrent ≈ $2.54B liquid, total assets $4,631.5M, equity $3,253.1M; liabilities are payables/accruals ($674.3M) and operating lease liabilities ($471.3M total per financials_history.csv). Net cash, not unknown leverage. Caveat: the ~$2.9B Soleno acquisition closed May 18, 2026 — after this balance-sheet date — and will have drawn the liquidity pile down materially in 2026; the FY2025 statement is the last audited position.
- **WIDE_SCENARIO_SPREAD** (4.75x): real — the outcome range genuinely spans a patent-defense grind to a multi-franchise compounder, and 2027 readouts are binary. Confidence is medium (never high under this flag), and the verdict is sized to the conservative end.
- **TIER_BAND** (bear C 10.95% vs bull B 16.98%): position sizing, if any, belongs at the bear end — the weighted 14.48% sits near the top of the band only because the TTM base is current; the bear case still does not clear 15%.

## My thoughts / overlay
- Quality is high and improving: ~98% gross margins, ROIC proxy up to ~17%, debt-free, OCF $898.1M TTM against capex of just $27.7M. The debate is purely price vs patent-clock: the moat is real but dated (Ingrezza exclusivity into ~2029–2032), and the replacement franchises (Crenessity at ~15% penetration, Vykat, 2027 pipeline) have to be worth most of today's $13.9B market cap by the time the cliff arrives.
- The TTM base flatters nothing: it contains only ~6 weeks of Vykat, deducts SBC in full ($234.5M), and still prints $6.13/share. Even so, at $135.71 the buyer needs the bull half of the distribution to clear 15% — the weighted case lands just under it.
- SBC at ~26% of OCF is the standing quality deduction; watch whether it falls as a share of OCF as Crenessity/Vykat scale, and whether buybacks (only $66M TTM per fundamentals.json) ever offset issuance ($191.3M TTM) — today shareholders are still being diluted ~1.2%/yr net.

## Final verdict
- **Final tier: C** (weighted IRR 14.48% on the TTM base; method range D on the median base → C on TTM; bear→bull band C→B)
- Confidence: **Medium** (capped by WIDE_SCENARIO_SPREAD; high on OE quality and the filing-derived TTM base, lower on any single growth path)
- One-liner: High-quality patent-moat biotech, moat 6/10 — just misses the 15% hurdle at $135.71 (weighted IRR 14.5%, IV@15% $128.80); it clears 15% below ~$129, with the 2027 pipeline readouts as the swing factor.
