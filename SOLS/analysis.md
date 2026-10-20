# SOLS — Solstice Advanced Materials Inc.
Pass-1 run, 2026-10-20, engine release 5.5.0. In scope: market cap $9.609B at $60.47 (nasdaq_quote_api), under the $40B scope limit.

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.json, financials_history.csv or fundamentals.json — none are recomputed.

## What it is
Honeywell's former Advanced Materials business, spun off as a standalone company on October 30, 2025. Two segments: Refrigerants & Applied Solutions (low-GWP Solstice refrigerants including the R-454B transition, blowing agents, solvents, healthcare packaging, and Nuclear / Alternative Energy Services — uranium conversion) and Electronic & Specialty Materials (semiconductor sputtering targets and electronic materials, Spectra high-strength fibers, research & performance chemicals). Over 3,000 customers in ~120 countries and over 5,700 issued patents and pending applications (company 2026 proxy statement). Q2 2026 net sales were $1,148M, up 11% year over year, with six of seven businesses growing; management raised FY2026 guidance to net sales of $4.125–4.185B, adjusted EBITDA of $1.035–1.055B and adjusted EPS of $2.75–$2.95, with capex guided at $420–440M. The announced Element Solutions acquisition (July 2026) was mutually terminated on August 27, 2026 with no termination fee, and the board authorized a first $500M share repurchase program the same day — deal risk is out, buyback is in, neither changes the cash base below.

## Owner's earnings
**Annual history (financials_history.csv; conservative OE = OCF − capex − SBC):**
- FY2023: OCF $760M, capex $299M, SBC $18M → OE $443M = $2.79/share
- FY2024: OCF $842M, capex $296M, SBC $17M → OE $529M = $3.33/share
- FY2025: OCF $455M, capex $352M (PP&E $336.0M + intangibles $16.0M, key_numbers.md), SBC $27M → OE $76M = $0.48/share (latest FY OE total $76.0M, key_numbers.md)
- Maintenance-definition OE (CSV): $621M / $594M / $213M for FY2023–25 — above the conservative figure every year, but it leans on the filed D&A tag, which is small relative to capex, so the conservative (OCF-based) series is the one used throughout.
- OE positive 3 of the last 3 fiscal years (key_numbers.md: 3/3).

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct):**
- OCF: FY $455M − prior YTD $310M + current YTD $461M = **TTM $606M**
- Capex: FY $352M − prior YTD $138M + current YTD $213M = **TTM $427M**
- SBC: FY $27M − prior YTD $12M + current YTD $11M = **TTM $26M**
- Shares (current-YTD weighted diluted): **159,300,000**
- **TTM OE total $153M → base OE/share $0.96** (base_source: ttm_json)

**Why the TTM base and not the $2.79 median:** both candidate bases are distorted, in opposite directions, and the distortion is the October 30, 2025 spin-off itself. The 3-year median ($2.79) is built mostly from pre-spin carve-out years (FY2023–24 and most of FY2025) that carried no standalone debt (debt was $22M total at FY2024 year-end vs $1,986M at FY2025 year-end, financials_history.csv), capex of ~$296–299M/yr, and Honeywell-allocated costs — it is not the earning power of the standalone company at its current capex level. The TTM base is depressed by spin-era items (below) but it is the only base that reflects the standalone capital structure, standalone costs, and the guided capex level ($420–440M for 2026, vs the TTM's $427M — the capex step-up is guided to persist, not a one-year spike). The preliminary median-base run is reported under Thoughts as the method range; both bases produce Tier D.

## Moat: 5/10 — moderate / narrow
Justification: patent-protected low-GWP refrigerant franchise, the sole US uranium conversion operation, and qualification switching costs in electronic materials — real positions, but gross margin is eroding and there is no ROIC series or standalone track record to support a higher score.
- FOR: Patent-protected low-GWP refrigerants (Solstice 454B / HFO transition) with regulatory tailwind; 5,700+ issued patents and pending applications across the portfolio (2026 proxy); Nuclear Alternative Energy Services — sole US uranium conversion capacity, accelerating backlog; qualification switching costs in semiconductor sputtering targets and electronic materials; Spectra high-strength fibers and healthcare packaging niches with spec-in positions.
- AGAINST: Gross margin eroding — 35.2% FY2023 → 34.6% FY2024 → 32.2% FY2025 (fundamentals.json); refrigerant competition from Chemours and Daikin and HFO patent expiries over time; no ROIC evidence — `roic_proxy` is null for every year in fundamentals.json because operating income is not tagged, so no ROIC figure can be quoted, and ROE on a carve-out equity base is not a standalone record; cyclical end markets (construction, autos, semiconductors); no standalone operating history before the spin-off.
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — final run (2026-10-20)
Growth sanity check: the engine's blend is 3.07% (key_numbers.md: rev CAGR 5y 3.19%, rev CAGR 3y 3.19%, latest rev YoY 3.08%, OE/share CAGR 2y −58.58%) — that blend is built on pre-spin fiscal years and sits below what the company is actually printing now: Q2 2026 sales +11% year over year and FY2026 guidance of $4.125–4.185B against FY2025 revenue of $3,886M (financials_history.csv). Scenario starts were therefore recalibrated upward via offsets to −5 / 0 / **+7** / +11 / +16% — the base start sits inside the guided range, the bull start sits above the latest +11% print because refrigerant aftermarket and nuclear/electronics demand are still ramping, and the bear starts assume the HFO-transition mix drag and plant turnarounds persist. Probabilities 15/25/30/20/10 (super-bear weight raised from the 10% default per OE_VOLATILE, below); OE multipliers are the defaults 0.75/0.90/1.00/1.10/1.25. Price $60.47.

| Scenario | Prob | Growth start | OE mult | IV@15 | IRR |
|---|---|---|---|---|---|
| Super bear | 15% | -5.0% | 0.75 | $4.32 | 3.30% |
| Bear | 25% | 0.0% | 0.90 | $6.39 | 3.78% |
| Base | 30% | 7.0% | 1.00 | $9.49 | 4.56% |
| Bull | 20% | 11.0% | 1.10 | $12.32 | 5.26% |
| Super bull | 10% | 16.0% | 1.25 | $17.17 | 6.44% |

- **Probability-weighted: IV@15% $9.27 (−84.7% vs price), IV@12% $12.36, IV@10% $15.81, weighted IRR 4.52%, base-case IRR 4.56%**
- **Tier by numbers: D** (bear D → bull D; scenario range 3.30%–6.44%). Hurdle-clearing prices on the weighted path: 15% at $9.27, 20% at $6.50, 25% at $4.99.
- Diagnostics (key_numbers.md): OE yield 1.59%, terminal value 19.1% of IV@15%, scenario spread 3.98x, net debt 9.51x normalized OE, 9.6 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (latest FY ended 9.6 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, legs quoted above.
- **OE_VOLATILE** (OE/share spans >3x): real and explained, not smoothed away — OE/share went $2.79 → $3.33 → $0.48 across FY2023–25 because of the spin-off break (see BASE_DIVERGENCE). Handled by raising the super-bear probability to 15% and keeping confidence low.
- **NI_OCF_DIVERGENCE** (2025): FY2025 net income was $237M against OCF of $455M (financials_history.csv). The company's own 2025 reporting attributes the net-income drop (from $594M in FY2024) to costs associated with the separation from Honeywell and higher income tax expense driven by frictional taxes associated with the spin-off; the CSV shows FY2025 tax expense of $362M vs $192M in FY2024. The divergence is a spin-year P&L effect; the OCF-based conservative OE used throughout already reflects the cash side, and Q3 2025 — the spin quarter — printed a net loss and negative quarterly OCF in fundamentals.json before recovering in 2026 quarters.
- **THIN_HISTORY** (only 3 fiscal years): structural — the filer did not exist standalone before the spin-off and EDGAR carries only the FY2023–25 carve-out history. Nothing to extend it with; it caps confidence at low.
- **BASE_DIVERGENCE** (latest FY $0.48 vs 3-yr median $2.79): both are distorted by the spin-off, in opposite directions — the median is a pre-spin carve-out figure with no standalone debt and ~$296–299M capex; the latest FY and TTM carry spin costs and frictional taxes but also the real standalone structure and the guided $420–440M capex level. The TTM base ($0.96) was used; the median-base preliminary run is in Thoughts so the range is on the record.
- **LOW_OE_YIELD** (base OE yield 1.6%, key_numbers.md 1.59%): accurate, not a model error — at $60.47 the price capitalizes adjusted EBITDA (~$1.04B guided) and growth, while conservative cash OE after full capex is $153M TTM. The tier rests on that gap, which is exactly why the verdict is sized to the conservative end.
- **HIGH_NET_DEBT** (net debt 9.5x normalized OE): net debt is $1.452B (key_numbers.md) — the ~$2.0B debt package placed at the spin (FY2025 debt total $1,986M, cash $534M, financials_history.csv), plus $87M of lease liabilities in dcf_numbers.json. Against adjusted EBITDA the company itself reports net leverage of ~1.3x; the 9.5x figure is against the depressed TTM conservative OE base. Either way the debt is new, standalone, and real — interest is now a cash cost the carve-out years never bore — and the bear cases were stressed via the raised super-bear weight.

## My thoughts / overlay
- The honest headline is the method range, and unusually both ends agree on the tier: the preliminary run on the engine's median base ($2.79/share, default probabilities and offsets) printed weighted IRR 7.80% and weighted IV@15% $25.11 — also Tier D. The TTM-base final ($0.96/share) prints 4.52% / $9.27. The range is D at $9–25 of IV@15% against a $60.47 price; no defensible base in the computed outputs gets this price near a 15% hurdle.
- Why the market disagrees: it is paying for adjusted EBITDA and adjusted EPS ($2.75–$2.95 guided) — measures that add back the spin costs and treat the $420–440M capex program as growth investment. The owner's-earnings method charges every capex dollar. If the Spokane / Spectra / nuclear capex truly earns high returns, OE/share inflects up in 2027–28 and this score is too harsh; that is a forecast, not a filing, and pass 1 scores filings.
- Watch items: whether FY2026 OCF conversion recovers now that separation costs roll off (H1 2026 OCF was $461M, the current-YTD TTM leg), whether the $500M buyback actually shrinks the count, and gross margin — a third straight year of decline below 32.2% would argue the refrigerant mix drag is structural, not transitory.
- Data notes: fundamentals.json carries no `roic_proxy` (operating income untagged) and no operating-income series, so no ROIC claim is made anywhere in this analysis. Enrichment outputs are noted in the folder; any enrichment failure is non-blocking per spec.

## Final verdict
- **Final tier: D** (weighted IRR 4.52% on the TTM base; method range across the two computed bases is 4.52%–7.80%, Tier D either way)
- Confidence: **Low** (3-year carve-out history only, spin-off basis break through every input, wide scenario spread)
- One-liner: Real specialty-materials franchise, moat 5/10, but on standalone cash economics it does not clear 15%: TTM owner's earnings are $0.96/share after the post-spin capex step-up, giving a 4.5% weighted IRR and a weighted IV@15% of $9.27 vs the $60.47 price — it would need to trade near $9.27 to clear 15% on these inputs.
