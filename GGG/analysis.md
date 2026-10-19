# GGG — Graco Inc.
Engine 5.4.0 run, 2026-10-17. In scope (market cap $13.874B at $81.99, nasdaq_quote_api).

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.json, financials_history.csv, or fundamentals.json — none are recomputed.

## What it is
Minneapolis maker of fluid-handling systems: pumps, meters, sprayers and dispensing equipment for difficult fluids (paint, adhesives, sealants, lubricants). Reorganized January 1, 2025 into three segments — Contractor (professional paint sprayers), Industrial (finishing, process, lubrication) and Expansion Markets (semiconductor, environmental and other growth niches). SIC 3561, Pumps & Pumping Equipment. Dividend payer with DPS TTM $1.16 (fundamentals.json).

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $683,591,000; capex $45,669,000; SBC $34,333,000 (always a real cost).
- **Conservative owner's earnings FY2025: $603,589,000 = $3.57/share** (key_numbers.md: latest FY OE/share $3.57, latest FY OE total $603.6M)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $619,363,000 — same ballpark as the conservative figure, which raises confidence.
- OE positive 5 of the last 5 fiscal years. Net debt $-622.5M (net cash; key_numbers.md). Shares diluted (latest) 169,219,000.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $683,591,000 − prior YTD $308,103,000 + current YTD $297,965,000 = **TTM $673,453,000**
- Capex: FY $45,669,000 − prior YTD $30,187,000 + current YTD $28,516,000 = **TTM $43,998,000**
- SBC: FY $34,333,000 − prior YTD $16,594,000 + current YTD $15,569,000 = **TTM $33,308,000**
- Shares (current-YTD weighted diluted): **167,029,000**
- **TTM OE total $596,147,000 → base OE/share $3.57** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $2.80/share — rejected as the base: the median year is FY2024 ($2.80), and the series has risen every year since the FY2022 capex trough (OE/share $0.88 in FY2022, $2.53 in FY2023, $2.80 in FY2024, $3.57 in FY2025), with the TTM figure ($3.57) confirming the latest FY rather than contradicting it. The median is a lagging base here, not the distorted-versus-clean one. It is still reported in key_numbers.md.
- Capex caveat, stated plainly: the current base rests on capex having normalized — $45,669,000 in FY2025 and $43,998,000 TTM vs $201,161,000 in FY2022 and $184,775,000 in FY2023 during the facility-investment years. If capex reverts toward the FY2024 level ($106,737,000), OE/share falls materially; the bear and super-bear OE multipliers (0.90 / 0.75) are where that risk is carried.

**Latest quarter (Q2 2026, company release July 22, 2026):** net sales $590.6M, +3% YoY — acquisitions contributed 3 points and currency 1 point, partly offset by a 1-point organic decline on finishing-systems timing in Industrial. H1 2026 sales $1,130.7M, +3%. Adjusted EPS $0.91 in Q2. Gross margin rose 130bp with help from $9M of tariff refunds, net of surcharges — a tailwind that will not repeat cleanly. Management maintained full-year guidance for low-single-digit organic growth at constant currency (mid-single-digit total including acquisitions), guided Q3 revenue of $580–$600M excluding Valco Melton (expected to close in Q3), and repurchased $315M of shares in Q2 ($331M year to date). TTM revenue in fundamentals.json is $2,267,210,000, +4.58% YoY, at a 52.64% gross margin and 28.06% operating margin.

## Moat: 7/10 — strong
Justification: Strong niche moat: ROIC proxy stayed 24.6–37.2% over FY2019–2025 (25.0% in FY2025) with gross margin 49.3–53.1% through the cycle, pricing power and mission-critical installed base in Contractor/Industrial fluid handling; capped at 7 because growth is low-single-digit organic, end markets are cyclical, and Nordson/EXEL/Asian rivals contest every niche.
- Evidence (fundamentals.json, roic_proxy series): FY2021 37.2%, FY2022 29.2%, FY2023 31.9%, FY2024 24.6%, FY2025 25.0% — well above any plausible cost of capital through a full cycle, though down from the 30s as cash and acquisition goodwill built up. Gross margin for the last five fiscal years: 52.0% / 49.3% / 52.9% / 53.1% / 52.5% (FY2021–FY2025) — the FY2022 dip to 49.3% recovered within a year, which is pricing power in practice.
- FOR: ROIC proxy 24.6–37.2% FY2019–2025, well above cost of capital through a cycle; gross margin 49.3–53.1% for seven straight years — proven pricing power; mission-critical niche specialization (difficult fluids, precision dispensing) with high switching costs and 500+ patents; leading share (~20–25% core segments) and global service/distribution network; net-cash balance sheet (−$622M net debt) funding buybacks and bolt-on M&A through downturns.
- AGAINST: low-single-digit organic growth — Q2 2026 organic sales −1%, guidance low-single-digit for 2026; cyclical Contractor (construction/housing) and Industrial capex exposure; competition from Nordson, EXEL Industries and lower-cost Asian entrants; growth increasingly acquisition-bought (COROB, Radia, Valco Melton) — integration and goodwill risk; tariff and input-cost exposure, with Q2 2026 margin helped by $9M of tariff refunds.
- A 7 gives CAP = 11.1 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 11.1 years, 15-year projection.

## DCF — final run (2026-10-17)
Growth sanity check (mandatory): the engine's blended growth is 6.77% (components: rev CAGR 5y 6.27%, rev CAGR 3y 1.43%, latest rev YoY 5.83%, OE/share CAGR 2y 18.76%). The 18.76% OE/share CAGR is a rebound artifact off the FY2022–23 capex-suppressed base, not a revenue signal — actual recent prints are FY2025 revenue +5.83%, TTM revenue +4.58%, Q2 2026 revenue +3.3%, and management guidance of low-single-digit organic / mid-single-digit total growth. The default scenario starts (−5.2% / 1.8% / 6.8% / 11.8% / 18.8%) would have put the super-bull start at 18.8%, above every revenue print the company has produced recently, with no evidence to support it. Scenario starts were therefore recalibrated via offsets (−0.0877 / −0.0527 / −0.0177 / +0.0133 / +0.0433 vs the blend) to −2.0% / 1.5% / **5.0%** / 8.1% / 11.1%. The base start (5.0%) sits on the TTM/FY prints and the mid-single-digit total-growth guide; the bull start (8.1%) requires Valco Melton plus an organic recovery, and the super-bull start (11.1%) requires a construction/industrial upcycle — both are written as stretch cases, not extrapolations. Probabilities 15/25/30/20/10 (bear weight widened from the 10/25/30/25/10 default for OE_VOLATILE, see Flags); OE multipliers 0.75/0.90/1.00/1.10/1.25. Price $81.99.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | -2.0% | 0.75 | Construction/industrial downturn; capex re-rates back up | $17.77 | 5.01% |
| Bear | 25% | 1.5% | 0.9 | Organic stagnation sticks; acquisitions only offset cyclicality | $25.12 | 6.28% |
| Base | 30% | 5.0% | 1.0 | Mid-single-digit total growth per guidance, fading over the CAP | $32.93 | 7.65% |
| Bull | 20% | 8.1% | 1.1 | Valco Melton integrates well; organic growth recovers | $41.95 | 9.18% |
| Super bull | 10% | 11.1% | 1.25 | Full upcycle plus Expansion Markets (semi/environmental) scaling | $54.98 | 11.22% |

- **Probability-weighted: IV@15% $32.71 (−60.1% vs price), IV@12% $43.53, IV@10% $55.62, weighted IRR 7.65%, base-case IRR 7.65%**
- **Tier by numbers: D** — and the band is tight: bear tier D → bull tier D (key_numbers.md), scenario range 5.01%–11.22%. Even the super-bull case (11.22%) does not reach the 15% hurdle.
- Diagnostics (key_numbers.md): OE yield 4.35%, terminal value 19.0% of IV@15%, scenario spread 3.09x, net debt −1.03x normalized OE, 9.7 months since FY end.
- Hurdle-clearing prices (weighted path): 15% at $32.71 · 20% at $23.02 · 25% at $17.69.

## Flags — every fragility flag resolved
- **STALE_FY** (latest fiscal year ended 10 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026 (FY end 2025-12-26, YTD end 2026-06-26), with all four legs quoted above. TTM OE/share $3.57 vs latest FY $3.57: no drift, the stale year is not hiding a deterioration.
- **OE_VOLATILE** (OE/share range over the last 5 years spans >3x): the range is FY2022's $0.88 against FY2025's $3.57, and it is explained, not mysterious — FY2022–23 capex of $201,161,000 / $184,775,000 (facility investment) plus an OCF dip to $377,394,000 in FY2022 crushed the conservative OE, which then recovered as capex normalized ($106,737,000 → $45,669,000) and OCF recovered ($651,017,000 → $683,591,000). Handled three ways: the TTM base (post-normalization, confirmed by two independent periods), a widened bear weight (super-bear probability raised 10% → 15%, bull cut 25% → 20%), and the capex-reversion caveat carried in the bear multipliers. The residual risk is real: the base assumes the low-capex regime persists.
- **WIDE_SCENARIO_SPREAD** (preliminary run only, 4.49x): resolved by the growth recalibration above — the default super-bull start of 18.8% was an artifact of the inflated blend. The final run's spread is 3.09x (key_numbers.md) and the flag no longer fires; confidence is still capped at medium given the 3.09x spread and the capex-regime question.

## My thoughts / overlay
- Quality is not the debate — this is the cleanest balance sheet and one of the steadiest ROIC records in the sweep so far (net cash, 5/5 OE-positive years, ~52–53% gross margins, aggressive buybacks: $315M in Q2 2026 alone). The debate is price: at $81.99 the market is paying for a decade of flawless compounding, and the filing-derived numbers support roughly 7.6% weighted IRR, not 15%.
- Method range: the preliminary default run (normalized median base $2.80/share, default scenarios) printed weighted IRR 7.20% and IV@15% $29.36; the final TTM-base recalibrated run prints 7.65% and $32.71. Both are Tier D — the verdict is not assumption-sensitive here, which is itself the finding. Even granting the super-bull path outright (11.22% IRR) the stock does not clear 15% at this price.
- The one assumption that could move the verdict is capex: the TTM base capitalizes a $44M capex regime. Graco's own history says capex regimes change (2021–23 averaged ~$173M/yr). If that regime returns, the base falls and Tier D gets worse, not better — the asymmetry runs against the buyer at $81.99.
- Watch items: Valco Melton close and integration (Q3 2026), whether organic growth turns positive after Q2's −1%, and whether the buyback pace ($331M YTD) shrinks the share count fast enough to lift OE/share growth above revenue growth — the share count CAGR is only −0.72%/yr so far (key_numbers.md), so buybacks are mostly offsetting issuance/dilution, not compounding per-share value at a dramatic rate.

## Final verdict
- **Final tier: D** (weighted IRR 7.65% on the final inputs; bear and bull both Tier D)
- Confidence: **Medium** (high on the TTM base and balance sheet, medium on the growth path — 3.09x scenario spread and the capex-regime assumption)
- One-liner: High-quality compounder, moat 7/10 — does not clear 15% at $81.99 (weighted IRR 7.6%, IV@15% $32.71); clears 15% only below ~$32.71.
