# MEDP — Medpace Holdings, Inc.
Engine 5.4.0 run, 2026-10-16. In scope (market cap $18,121,900,980 at $613.74, nasdaq_quote_api).

All figures below are copied from dcf_numbers.json, ttm.json, financials_history.csv, or fundamentals.json — none are recomputed.

## What it is
Full-service contract research organization (CRO) running Phase I–IV clinical trials for small and mid-sized biotech sponsors — study design, site/recruitment management, labs (four owned), data, and regulatory/FDA presentation under one roof. ~6,500 employees across 46 countries (Q2 2026 earnings release). Roughly 5% share of a fragmented CRO market dominated by IQVIA and ICON; Medpace's niche is high-science, complex trials (oncology, metabolic, CNS) for sponsors too small to run trials in-house. Asset-light, no dividend, aggressive buyback (share count shrinking 4.3%/yr).

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $713,223,000; capex $31,356,000; SBC $34,786,000 (always a real cost).
- **Conservative owner's earnings FY2025: $647,081,000 = $21.91/share** (base_oe_latest_per_share).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $557,536,000 — below the conservative figure, mainly working-capital timing (customers prepay; ΔNWC was −$106,413,000 in FY2025). The OCF-based conservative figure is the one used.
- OE positive 5 of the last 5 fiscal years. OE/share history: $5.85 (2021), $9.79 (2022), $11.82 (2023), $17.08 (2024), $21.91 (2025).

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $713,223,000 − prior YTD $274,362,000 + current YTD $313,799,000 = **TTM $752,660,000**
- Capex: FY $31,356,000 − prior YTD $16,107,000 + current YTD $30,725,000 = **TTM $45,974,000**
- SBC: FY $34,786,000 − prior YTD $22,843,000 + current YTD $9,266,000 = **TTM $21,209,000**
- Shares (current-YTD weighted diluted): **28,761,000**
- **TTM OE total $685,477,000 → base OE/share $23.83** (base_source: ttm_json)
- The engine's normalized base (median of last 3 FY OE/share) is $17.08/share. It is reported but not used as the base: it is dragged by FY2023 ($11.82/share), and the TTM figure is filing-derived and current. The preliminary run on the median base gave weighted IRR 10.88% / IV@15% $380.51 — the verdict does not depend on the base choice (see method range).

**Balance sheet (DEBT_TAGS_BLANK resolution):** the engine found no debt tag for FY2025 because there is essentially no debt to tag. FY2025 cash was $497,049,000 (financials_history.csv); the Q2 2026 earnings call reported cash of $502.7M at 2026-06-30 and $527M remaining buyback authorization. Operating lease liabilities are $136,852,000. This is a net-cash balance sheet; the engine's null net debt means "no borrowings filed," not missing leverage risk.

## Moat: 6/10 — moderate, earned by execution not structure
Justification: integrated full-service model with genuine mid-trial switching friction and best-in-class margins, but project-based contracts, ~5% share against far larger rivals, concentrated clients, and a funding-sensitive small-biotech customer base cap durability. ROIC evidence: the `roic_proxy` series in fundamentals.json runs 4.4% (2016) → 12.0% (2018) → 27.3% (2020) → 59.2% (2022) → 90.5% (2023) and then breaks (243% in 2024, negative in 2025) — not because returns collapsed, but because buybacks shrank book equity to $459,071,000 against $497,049,000 of cash, driving measured invested capital toward zero. The cleaner margin evidence: operating margin 21.1% in FY2025 ($534,935,000 on $2,530,234,000 revenue) and 21.0% TTM ($583,404,000 on $2,782,288,000), vs peer CRO EBITDA margins of ~15–18%. Gross margin is not separately tagged in Medpace's filings (service costs sit in operating expenses), so operating margin is the quoted series. Returns are genuinely high; the measured ROIC series itself is unusable in the recent years and is not the basis for a score above 6.
- FOR: full-service integration (design → labs → data → FDA filing under one roof) that small biotechs cannot replicate in-house; switching a CRO mid-trial carries real operational/regulatory risk for the sponsor; deep scientific/regulatory expertise in oncology, metabolic and CNS; high repeat-business rate; asset-light, negative-working-capital model (net days sales outstanding −59.6 days in Q2 2026 — customers fund operations); operating margin ~21% vs ~15–18% peer EBITDA margins.
- AGAINST: ~5% market share vs IQVIA (~19%) and ICON (~10%) with far greater scale and data assets; contracts are project-based — no recurring-revenue lock-in once a trial ends; client concentration: top 5 customers ≈31% and top 10 ≈40% of LTM revenue (Q2 2026 call); customer base is overwhelmingly small/mid biotech, whose R&D budgets are hostage to capital-market funding cycles; growth is already decelerating (FY2026 revenue guided +10.9–14%).
- A 6 gives CAP = 9.8 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 9.8 years, 15-year projection.

## DCF — engine 5.4.0 final run (2026-10-16)
Growth sanity check (mandatory): the engine's blended start is 25.47% (rev CAGR 5y 22.27%, 3y 20.11%, latest rev YoY 19.97%, OE/share CAGR 2y 36.16%, revenue components +4.28pp for the shrinking share count). That blend is above every current print: Q2 2026 revenue +17.2% YoY, and FY2026 guidance is revenue +10.9–14% with diluted EPS guided to $17.25–$17.95. The OE/share CAGR leg is flattered by the FY2023→25 margin snap-back and buybacks. Scenario starts were therefore recalibrated via offsets (−0.20 / −0.125 / −0.08 / −0.025 / +0.045 vs the blend) to 5.5 / 13.0 / **17.5** / 23.0 / 30.0%: the base start is revenue growth near the top of the guide plus the ~4%/yr buyback contribution to OE/share; even the super-bull start (30.0%) stays below the 2-yr OE/share CAGR the company just printed (36.16%), with the written reason that margin expansion of that pace cannot repeat off a 21% operating margin. Probabilities 15/30/30/17/8 — bear weight widened per the OE_VOLATILE flag; OE multipliers at the defaults 0.75/0.90/1.00/1.10/1.25. Price $613.74.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | 5.5% | 0.75 | Biotech funding winter; cancellations rise, backlog burns without replacement | $167.33 | 6.02% |
| Bear | 30% | 13.0% | 0.90 | Growth settles at guide-low; a top-5 client program ends | $280.18 | 8.64% |
| Base | 30% | 17.5% | 1.00 | Guide delivered, buyback continues, margins hold ~21% | $379.78 | 10.74% |
| Bull | 17% | 23.0% | 1.10 | Book-to-bill stays >1.1, oncology momentum sustains low-20s growth | $531.77 | 13.61% |
| Super bull | 8% | 30.0% | 1.25 | Share gains compound; OE/share CAGR re-accelerates toward recent prints | $818.67 | 18.09% |

- **Probability-weighted: IV@15% $378.98 (−38.3% vs price), IV@12% $522.66, IV@10% $685.43, weighted IRR 10.76%, base-case IRR 10.74%**
- **Tier by numbers: C.** Diagnostics (dcf_numbers.json): OE yield 3.88%, terminal value 22.7% of IV@15%, scenario spread 4.89x, 9.5 months since FY end, IRR not at floor, not capped.
- Hurdle prices: clears 15% only at or below **$378.98**; 20% at $253.23; 25% at $186.44.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.5 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, legs quoted above.
- **BUYBACK_TAILWIND** (share count −4.3%/yr): already credited via the +4.28pp adjustment to the revenue components of the blend; the growth recalibration counts the buyback once (≈4pp of the 17.5% base start), not twice.
- **OE_VOLATILE** (OE/share spans >3x over 5 years): real but it is a growth/margin-expansion trajectory ($5.85 → $21.91), not losses — OE was positive 5/5 years. Handled by widening bear-side probability to 45% (super bear + bear) and by the normalized base being reported alongside the TTM base; both bases give Tier C.
- **DEBT_TAGS_BLANK**: resolved above — no borrowings filed because the company is net cash ($497.0M cash at FY2025, $502.7M at Q2 2026, lease liabilities $136.9M). No leverage concern; the engine's null net debt is a true negative, verified from the filing history.
- **WIDE_SCENARIO_SPREAD** (4.89x): real — the range between a funding-winter CRO and a compounding share-gainer is genuinely wide. Confidence capped at medium; verdict sized to the conservative end.
- **TIER_BAND** (bear tier D at 8.6% vs bull tier C at 13.6%): the whole band sits below the 15% hurdle, so the band does not change the action — even the bull case does not clear 15% at $613.74. Sizing language follows the bear end regardless.

## My thoughts / overlay
- The method range is narrow for once: median-base/default-scenario preliminary run → weighted IRR 10.88%, IV@15% $380.51 (Tier C); TTM-base/recalibrated final run → 10.76%, $378.98 (Tier C). Two different bases and two different growth calibrations land within ~1% of each other. This is a valuation verdict, not a method artifact.
- Quality is not the debate: TTM OE $685.5M on $46.0M of capex, SBC falling ($21.2M TTM vs $34.8M in FY2025), net cash, customers prepaying (negative DSO), buybacks retiring ~4%/yr. The debate is purely price: at $613.74 the market is paying for the bull/super-bull path as the base case.
- Risks: a biotech funding downturn hits bookings with a lag but hard (2022-style); top-5 client concentration (~31% of revenue) means one large program cancellation moves the year; wage pressure on clinical staff is the main margin threat; valuation itself — any guide cut re-rates a stock priced at ~26x TTM OE/share.
- Margin of safety: none at this price on these numbers — the weighted IV@15% is 38.3% below the price, and even the bull case ($531.77) sits below it. The stock clears Andrew's 15% hurdle only at or below ~$379.

## Final verdict
- **Final tier: C** (weighted IRR 10.76% on the final TTM-base run; method range C–C across both runs)
- Confidence: **Medium** (high on the TTM base and balance sheet, capped by the 4.89x scenario spread and the D–C tier band)
- One-liner: High-quality asset-light CRO, moat 6/10 — TTM owner's earnings $23.83/share and a raised guide, but at $613.74 the weighted IRR is only 10.8% (IV@15% $379); it clears the 15% hurdle only at or below ~$379.
