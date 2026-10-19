# BURL — Burlington Stores, Inc.
Pass-1 run, 2026-10-16, engine 5.4.0. In scope: market cap $16.685B at $260.19 (nasdaq_quote_api), under the ~$40B cap.

All figures below are copied from dcf_numbers.json, ttm.json, financials_history.csv, or fundamentals.json — none are recomputed.

## What it is
The third-largest US off-price retailer (apparel, footwear, home, beauty, baby) behind TJX and Ross Stores: 1,287 stores at Q2 FY2027 (period ended 2026-08-01), a "treasure hunt" model built on opportunistic buying, a reserve-inventory "chase" model, and smaller ~25,000 sq ft stores, many acquired cheaply from bankrupt retailers' leases. Long-term target is 2,000 stores, at roughly 110–115 net new stores a year. No dividend; capital returns are buybacks ($345,834,000 TTM per fundamentals.json).

## Owner's earnings
**FY2026 (fiscal year ended 2026-01-31, 10-K filed 2026-03-19, from financials_history.csv):** operating cash flow $1,231,382,000; capex $1,059,793,000; SBC $106,732,000 (always a real cost).
- **Conservative owner's earnings FY2026: $64,857,000 = $1.01/share.** OE-positive 4 of the last 5 fiscal years (FY2025 was −$104,580,000 / −$1.62/share, FY2021 was −$109,946,000).
- Maintenance version FY2026 (financials_history.csv): $681,951,000 — an order of magnitude above the conservative figure. The entire gap is capex: at $1,059,793,000 it runs at roughly 2.5x depreciation & amortization ($417,871,000 in FY2026). That capex is mostly growth, not upkeep — 104 net new stores in FY2026 plus new distribution centers (Savannah, GA and Arizona capacity per company commentary in search results), and management guides capex of approximately $875 million for the fiscal year ending January 2027 to fund ~110–115 net new stores and the Savannah DC. The scored method charges all of it against OE anyway; that is the conservative convention of this sweep, and the verdict below is stated on that basis.
- Capex intensity is the central fact of this name: capex was $492,644,000 in FY2024, $880,384,000 in FY2025, $1,059,793,000 in FY2026, and $1,002,936,000 TTM. OCF has not kept pace dollar-for-dollar, so conservative OE collapsed even as net income rose from $339,649,000 (FY2024) to $503,639,000 (FY2025) to $610,153,000 (FY2026).
- Balance sheet (latest, dcf_numbers.json / financials_history.csv): cash $1,232,525,000, total debt $2,082,326,000, net debt $849,801,000 — plus operating lease liabilities of $3,922,811,000 that sit outside the engine's net debt. Leases, not funded debt, are the real fixed-charge load.

**Base used = TTM owner's earnings through Q2 FY2027, from ttm.py (filing-direct, no hand math):**
- OCF: FY $1,231,382,000 − prior YTD $150,532,000 + current YTD $334,624,000 = **TTM $1,415,474,000**
- Capex: FY $1,059,793,000 − prior YTD $589,241,000 + current YTD $532,384,000 = **TTM $1,002,936,000**
- SBC: FY $106,732,000 − prior YTD $54,264,000 + current YTD $68,416,000 = **TTM $120,884,000**
- Shares (current-YTD weighted diluted): **64,022,000**
- **TTM OE total $291,654,000 → base OE/share $4.56** (base_source: ttm_json; ttm.json prints $4.555527787323108)
- The engine's normalized base (3-yr median) is $1.01/share — rejected as the base: the median year is FY2026 itself, whose OE was crushed by the capex peak, and FY2025's −$1.62/share drags the set. It is still reported and was the preliminary run's base (weighted IRR 3.16%, IV@15% $12.23 on that base — also Tier D). The verdict does not depend on which base is picked.

## Moat: 4/10 — weak-to-narrow
Justification: a real but replicable buying organization and a long store runway, against larger scaled rivals, no switching costs, no pricing power, and no measurable ROIC series to prove returns above the cost of capital through a cycle.
- FOR: Opportunistic off-price buying organization with a reserve-inventory chase model (flexibility to buy in-season); structural share tailwind as department stores shrink — off-price keeps taking that share; opportunistic real estate (bankruptcy-acquired leases at low cost, smaller format); gross margin expanding for five years (fundamentals.json annual: 41.59% FY2022, 40.45% FY2023, 42.49% FY2024, 43.25% FY2025, 43.83% FY2026) and adjusted EBIT margin expanding (8.0% in FY2026 per company reporting in search results); store runway from 1,287 stores toward a stated 2,000-store target.
- AGAINST: #3 in scale behind TJX and Ross — less buying leverage over the same vendor supply, and recent traffic comparisons in search results show Ross gaining share against Burlington head-to-head; no customer switching costs or network effects — the assortment is bought, not owned; adjusted EBIT margin ~8.0% trails larger off-price peers, i.e. the scale disadvantage shows up in profitability; tariff exposure on imported merchandise hitting a price-sensitive $25k–$100k income customer; no e-commerce channel of consequence.
- ROIC evidence: fundamentals.json's `roic_proxy` series is null for every year (the operating-income tag is not filed under a candidate tag), so there is no computed ROIC history to quote — per the spec, that absence is stated here rather than filled in. What is computable points the other way for a high moat: five-year gross margin in the low-40s and rising is a mid-pack retail margin, not a wide-moat signature. A 4 gives CAP = 7.2 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 7.2 years, 15-year projection.

## DCF — final run (2026-10-16)
Growth sanity check (mandatory): the engine blend is 10.27% (rev CAGR 5y 14.96%, rev CAGR 3y 9.94%, latest rev YoY 8.79%, OE/share CAGR 2y −52.71% — the last is a capex artifact, not a demand signal). Against actual prints: FY2026 revenue +8.79%, TTM revenue +10.90% (fundamentals.json), Q2 FY2027 total sales +11% with comps +2%, and raised FY2027 guidance of total sales +10% to +11% with comps +3% to +4% (company release, search results). The base start of 10.27% sits inside the current print/guidance range — no recalibration. Bull at 15.27% is above any recent print: it is the upside case (115-store year plus comp acceleration) and is weighted accordingly. Super bear at −1.73% is a tariff/recession shock case, below all prints by construction. Probabilities were shifted bear-ward from the 10/25/30/25/10 defaults to 15/25/30/20/10 per the OE_VOLATILE resolution below. OE multipliers are the defaults 0.75/0.90/1.00/1.10/1.25. Price $260.19.

| Scenario | Prob | Growth start | OE mult | IV@15 | IRR |
|---|---|---|---|---|---|
| Super bear | 15% | −1.73% | 0.75 | $23.78 | 3.59% |
| Bear | 25% | 5.27% | 0.90 | $37.38 | 4.34% |
| Base | 30% | 10.27% | 1.00 | $50.20 | 5.06% |
| Bull | 20% | 15.27% | 1.10 | $66.54 | 5.98% |
| Super bull | 10% | 22.27% | 1.25 | $97.70 | 7.67% |

- **Probability-weighted: IV@15% $51.05 (−80.4% vs price), IV@12% $68.44, IV@20% $35.49, IV@25% $26.99, weighted IRR 5.13%, base-case IRR 5.06%**
- **Tier by numbers: D** (bear D, bull D — no TIER_BAND split). Hurdle prices: clears 15% only at $51.05, 20% at $35.49, 25% at $26.99.
- Diagnostics (dcf_numbers.json): OE yield 1.75%, terminal value 19.6% of IV@15%, scenario spread 4.11x, net debt 2.91x normalized OE, 8.5 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (latest FY ended 8.5 months ago): resolved by construction — the base is the TTM figure from ttm.py through 2026-08-01, legs quoted above.
- **BASIS_BREAK_SUSPECT** (>60% revenue jump in the last 5 yrs): the jump is FY2021 → FY2022 revenue, $5,751,541,000 → $9,306,549,000 (+61.81% in fundamentals.json). It is the COVID rebound off the store-closure-depressed FY2021 (revenue −20.79% that year), not a divestiture, acquisition, or restatement — no basis break in the underlying business. Consequence: the 5-yr revenue CAGR (14.96%) is flattered by that rebound and is the least trustworthy blend component; the 3-yr CAGR (9.94%), latest YoY (8.79%), and current guidance (+10–11%) all cluster near the 10.27% blend actually used, so no growth input straddles a real break.
- **OE_VOLATILE** (OE/share range >3x over 5 yrs): real and capex-driven — OE/share ran $6.20 (FY2022), $1.24, $4.50, −$1.62, $1.01 as capex tripled. Handled by the TTM base plus bear-shifted probabilities (15% super bear vs the 10% default).
- **NI_OCF_DIVERGENCE** (>40% in 2024, 2025, 2026): explained by non-cash addbacks, not a one-off. FY2026: net income $610,153,000 vs OCF $1,231,382,000 — D&A $417,871,000 plus SBC $106,732,000 account for most of the $621,229,000 gap; the same D&A + SBC pattern, in the same direction, explains FY2024 ($307,064,000 + $83,948,000 against a $529,086,000 gap) and FY2025 ($347,575,000 + $87,572,000 against a $359,737,000 gap), with working capital/inventory swings as the remainder. No tax-deposit or impairment one-off was found. The OCF-based conservative OE is the series used throughout, so the divergence is the OE construction itself (D&A added back in OCF, capex subtracted in full), not contamination of the base.
- **LOW_OE_YIELD** (base OE yield 1.75%): real — at $260.19 the valuation rests almost entirely on growth and on capex eventually normalizing, neither of which the scored method credits in advance. This is why the tier is D despite a growing, profitable business.
- **WIDE_SCENARIO_SPREAD** (super-bull IV 4.11x super-bear): real. Confidence is capped at low, and the verdict is sized to the conservative end.
- Preliminary-run flags that cleared on the final (TTM) run, for the record: **IRR_AT_FLOOR** and **HIGH_NET_DEBT** (13.10x) were both artifacts of the distorted $1.01/share median base — on the TTM base no scenario sits at the IRR floor and net debt is 2.91x normalized OE. The lease load ($3,922,811,000) remains the balance-sheet caveat regardless of which flag prints.

## Enrichment note
All 5.4 enrichment steps ran. segments.py returned no segment tables (warning: dimensioned facts exist but no axis has two members with values for the same concept) — BURL reports as a single segment, so the company page has no segment breakdown; non-blocking and does not affect the score. fundamentals.py, prices.py, statements.py, profile.py (Street consensus in street.json), and reprice.py all completed; reprice reports no tier change vs the scored run.

## My thoughts / overlay
- The honest headline is the method range, and here it is unusually wide in level but unanimous in verdict: preliminary median base ($1.01/share) → weighted IRR 3.16%, IV@15% $12.23; scored TTM base ($4.56/share) → 5.13%, $51.05; even the super-bull scenario tops out at IV@15% $97.70, 62% below the $260.19 price. On owner's earnings as this sweep defines them, there is no defensible scored path to even a C.
- The bull case a buyer is actually underwriting is not in the scored numbers: it is that ~$875M–$1,060M of annual capex is growth investment that will throw off future OCF for decades (new stores, DC capacity), so today's OE understates normalized earning power — the FY2026 maintenance OE of $681,951,000 vs the conservative $64,857,000 is that argument in one line. It may be right; it is also exactly the kind of normalization this method refuses to grant before the returns show up in OCF. Guidance (adjusted EPS $11.77–$11.97 for FY2027, search results) and the price both assume it lands.
- Quality is mid-pack, not poor: sales growing ~10–11%, comps positive, gross and EBIT margins expanding, buybacks shrinking the diluted count (share count CAGR −0.90%, already credited in the blend), funded net debt modest at $849,801,000. The risks are execution against two larger, better-margin rivals, tariff pass-through to a low-income customer, and saturation/cannibalization as the store base grows ~9% a year.
- Margin of safety: none on the scored basis — the price is roughly 5.1x the weighted IV@15%. A buyer at $260.19 is paying for the growth-capex payoff in full, in advance.

## Final verdict
- **Final tier: D** (weighted IRR 5.13% on the TTM base; D on the median base and in every scenario — sized to the conservative end, which here is the whole range)
- Confidence: **Low** (WIDE_SCENARIO_SPREAD 4.11x, OE yield 1.75%, and a base that hinges on how growth capex is treated)
- One-liner: Growing, margin-expanding off-price #3, moat 4/10 — but ~$1B/yr of growth capex crushes owner's earnings to a 1.75% yield, so at $260.19 it does not clear 15% on any scored basis (weighted IRR 5.13%, IV@15% $51.05; clears 15% only at $51.05).
