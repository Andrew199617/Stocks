# LFUS — Littelfuse, Inc.

Engine 5.4.0 run, 2026-10-18. Price $380.89 (nasdaq_quote_api), market cap $9.453B — in scope under $40B.

All figures below are copied from key_numbers.md, dcf_numbers.json, or ttm.py output — none are recomputed.

## What it is
The largest independent maker of circuit-protection products — fuses, PPTC resettable devices, protection and power semiconductors, sensors and control products — sold into Electronics, Transportation and Industrial end markets. Recent portfolio moves dominate the story: the 200mm Dortmund wafer fab (acquired from Elmos, closed Dec 31, 2024) in Electronics-Semiconductors, and Basler Electric (closed Dec 11, 2025 for $350.3M net of cash acquired, ~$130M annualized sales, reported in Industrial).

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $433,764,000; capex $67,637,000; SBC $27,301,000 (always a real cost).
- **Conservative owner's earnings FY2025: $338,826,000 = $13.65/share** (OCF − capex − SBC).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): **−$10,460,000** for FY2025 — not usable: it starts from net income, which carries the $301.2M non-cash goodwill impairment (see Flags). The OCF-based conservative figure is the clean one, because the impairment is non-cash and never touched operating cash flow.
- OE positive 5 of the last 5 fiscal years. Net debt $239,236,000 (0.68x normalized OE); lease liabilities $83,011,000.

**Base used = TTM owner's earnings through Q1 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $433,764,000 − prior YTD $65,758,000 + current YTD $80,258,000 = **TTM $448,264,000**
- Capex: FY $67,637,000 − prior YTD $23,102,000 + current YTD $14,094,000 = **TTM $58,629,000**
- SBC: FY $27,301,000 − prior YTD $4,855,000 + current YTD $5,671,000 = **TTM $28,117,000**
- Shares (current-YTD weighted diluted): **25,420,000**
- **TTM OE total $361,518,000 → base OE/share $14.22** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is also $13.65/share — it equals the latest FY figure, so the TTM/median choice moves the verdict very little here. Data caveat, in words only (no computed figure exists): ttm.py stops at 2026-03-28 because the Q2 2026 10-Q (period 2026-06-27, filed 2026-07-29) is not yet in EDGAR companyfacts (fundamentals.json warning). Q2 2026 reported sales were $738.8M, up 20% YoY, so a Q2-inclusive TTM base would be higher than $14.22 — but no filing-direct TTM figure through Q2 exists in the computed outputs, and the gap to the price (weighted IV@15% is 53.3% below it) is far larger than one strong quarter of OE can close.

## Moat: 5/10 — moderate / narrow
Justification: Largest specialist in circuit protection with design-in and safety-certification switching costs and a broad portfolio, but components face Eaton/TE/Bourns/Bel/Mersen and low-cost Asian rivals, no network effects, and measured ROIC has not held above the cost of capital through this cycle.
- Evidence first (fundamentals.json): **ROIC proxy** 15.6% (FY2021, period ended 2022-01-01), 15.9% (2022), 10.2% (2023), 4.1% (2024), 1.1% (2025) — the last two years are depressed by non-cash impairments sitting in operating income ($93.5M in 2024, $302.1M in 2025), but the direction ex-charge is still down from the peak. **Gross margin** over the same five fiscal years: 37.1%, 40.1%, 38.1%, 35.9%, 38.0% — held, which supports a real but narrow franchise rather than none.
- FOR: Largest independent fuse / circuit-protection specialist; leading share in automotive fuses and PPTC resettable devices. Design-in switching costs: components are qualified into OEM designs and safety-certified, so sockets are sticky for a product generation. Broad portfolio across protection, power semiconductors, sensors and control (Basler, Dortmund fab) enabling cross-sell into data-center, grid and EV demand. Gross margin held 35.9–40.1% over the last five fiscal years despite the downturn. Conservative balance sheet: net debt $239.2M, 0.68x normalized OE.
- AGAINST: ROIC proxy collapsed from 15.9% in 2022 to 1.1% in 2025 (impairment-depressed, but ex-charge returns also fell) — no proof of durable excess returns through a cycle. $301.2M goodwill impairment in Electronics-Semiconductors (Q4 2025) after $93.5M of impairments in 2024: past semiconductor M&A destroyed value; Allen, TX fab closure announced for 2027. Components are contestable against Eaton, TE Connectivity, Bourns, Bel Fuse, Mersen and low-cost Chinese makers. Cyclical end markets (autos, consumer electronics, HVAC, commercial vehicles), with the 2023–24 decline still in the 3-yr revenue CAGR (−1.73%). Growth is partly bought: Basler and the Dortmund fab supplied much of recent inorganic growth.
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — final run (2026-10-18)
**Growth recalibration (written reason, mandatory sanity check):** the engine's blended growth is 4.24% (components: rev CAGR 5y 10.54%, rev CAGR 3y −1.73%, latest FY rev YoY 8.92%, OE/share CAGR 2y −0.66%) — it is anchored on the 2023–24 downturn and is far below what the company is actually printing now: Q1 2026 sales +18% YoY (+15% organic), Q2 2026 sales $738.8M +20% YoY (+14% organic), and Q3 2026 guidance of $780–$800M (≈+26% YoY at the midpoint, +21% organic), with Basler contributing roughly 6pp of Q2 growth. Scenario starts were therefore set via offsets (−0.0724 / −0.0024 / +0.0676 / +0.1276 / +0.1976 vs g_base) to −3 / 4 / **11** / 17 / 24%. The base start of 11% is still *below* the current prints — deliberately: the 2026 surge is a cyclical snap-back plus Basler inorganic growth off a depressed base, not a 15-year run rate, and the fade over the 8.5-year CAP does the rest. Probabilities 10/25/30/25/10 (defaults); OE multipliers 0.75/0.90/1.00/1.10/1.25 (defaults). Price $380.89, base OE/share $14.22 (TTM).

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -3.0% | 0.75 | Cycle rolls over; semis restructuring and fab-closure costs bite; auto/HVAC stay soft | $69.52 | 4.63% |
| Bear | 25% | 4.0% | 0.90 | 2026 snap-back fades to low-single-digit; Basler is the only growth | $111.73 | 6.22% |
| Base | 30% | 11.0% | 1.00 | Recovery year, then fade to terminal over the CAP | $165.79 | 8.24% |
| Bull | 25% | 17.0% | 1.10 | Data-center / grid / EV content gains sustain high-teens growth near term | $232.96 | 10.57% |
| Super bull | 10% | 24.0% | 1.25 | 2030 ambition path: sustained electrification supercycle plus accretive M&A | $350.75 | 14.16% |

- **Probability-weighted: IV@15% $177.94 (−53.3% vs price), IV@12% $240.64, IV@10% $311.06, weighted IRR 8.71%, base-case IRR 8.24%**
- **Tier by numbers: D.** Bear-case tier D (6.22%), bull-case tier C (10.57%). Even the super-bull case (14.16% IRR, IV@15% $350.75) does not clear 15% at $380.89.
- Diagnostics: OE yield 3.73%, terminal value 20.5% of IV@15%, scenario spread 5.05x, net debt 0.68x normalized OE, 9.7 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (latest FY ended 2025-12-27, 9.7 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q1 2026, legs quoted above. Residual staleness is disclosed in the OE section: the Q2 2026 10-Q is filed but not yet in EDGAR companyfacts, so no computed TTM through Q2 exists; the verdict's margin (−53.3%) dwarfs that one-quarter gap.
- **NI_OCF_DIVERGENCE** (>40% in 2023, 2024, 2025): found — non-cash impairments, not cash leakage. FY2025 net income was −$71,700,000 against OCF of $433,764,000, driven by $302.1M of non-cash impairment charges in operating income, including the $301.2M goodwill impairment of the Electronics-Semiconductor reporting unit in Q4 2025 (10-K: weaker sales and profitability than original expectations amid persistent soft market conditions), plus $18.0M of restructuring charges. FY2024 (NI $100,190,000 vs OCF $367,621,000) carried $93.5M of non-cash impairments, including $47.8M against acquired customer-relationship intangibles. Because the conservative OE is OCF-based, the divergence does not contaminate the base; it *does* invalidate the NI-based maintenance OE (see above) and it is real economic information about past M&A — it is scored in the moat AGAINST case, not waved away.
- **WIDE_SCENARIO_SPREAD** (super-bull IV 5.05x super-bear IV): real — the outcome range hinges on whether the 2026 electrification/data-center surge persists. Confidence is capped at medium, and the verdict is sized to the conservative end.
- **TIER_BAND** (bear D 6.22% vs bull C 10.57%): the whole band sits below the 15% hurdle, so the band does not change the verdict — there is no tier at this price in any scenario except super-bull approaching it (14.16%).

## My thoughts / overlay
- The preliminary run (default scenarios on the FY-median base) printed weighted IRR 6.87% and IV@15% $128.92. Recalibrating growth to the actual 2026 prints and moving to the TTM base lifted that to 8.71% / $177.94 — that is the honest method range for this name today: **Tier D on both**, IV@15% roughly $129–$178 against a $380.89 price. The stock has already capitalized the recovery (and then some); the DCF question is not whether Littelfuse is recovering — it demonstrably is — but whether even a 24%-start super-bull path pays 15% from here. On filing-direct OE it does not (14.16%).
- Quality is middling-good, not elite: OE positive 5/5 years, gross margin held ~38%, net debt only 0.68x normalized OE, dividend raised (Q2 2026: quarterly dividend increased 7% to $0.80/share per the earnings summary). The debit side is capital allocation: two consecutive years of nine-figure impairments in the semiconductor business management bought, with fab closures following.
- Risks: cyclical snap-backs reverse (2023 revenue fell after the 2022 peak; 3-yr CAGR is still −1.73%); power-semiconductor execution (Allen, TX fab closure in 2027, Dortmund integration); tariff and auto-production exposure; a price that embeds the bull case leaves no room for a normal downturn.

## Data / enrichment notes
- Enrichment (step 9) completed: fundamentals.json, prices.json, statements.json, profile.json / street.json and live.json (reprice) all written. segments.py ran but parsed no segment-revenue facts for LFUS (0 segment facts) — non-blocking; segment color in this analysis comes from the 10-K / earnings-release segment reporting cited in the research, not from segments.json.
- ttm.py / fundamentals.json stop at 2026-03-28 because the Q2 2026 10-Q is not yet in EDGAR companyfacts — disclosed in the OE section above.

## Final verdict
- **Final tier: D** (weighted IRR 8.71% on the final inputs; bear D → bull C band, super-bull 14.16% still below the 15% hurdle)
- Confidence: **Medium** (filing-direct TTM base and resolved flags; capped by the 5.05x scenario spread and the one-quarter TTM staleness disclosed above)
- Hurdle-clearing price: clears 15% only below the weighted IV@15% of **$177.94** (20% below $122.25, 25% below $92.08) — less than half the $380.89 price.
- One-liner: Solid circuit-protection franchise, moat 5/10 — does not clear 15% at $380.89 on TTM OE (weighted IRR 8.71%, weighted IV@15% $177.94); it clears 15% only below $177.94 despite the strong 2026 recovery.
