# JBL — Jabil Inc
v5 run, 2026-10-14. Market cap $33.744B at $304.27 (nasdaq_quote_api) — in scope under $40B.

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.py output, or the cited search results — none are recomputed.

## What it is
One of the largest electronics manufacturing services (EMS) companies: design, manufacturing, and supply-chain services for other brands, organized into Intelligent Infrastructure (AI/data-center hardware — servers, networking, power, liquid cooling), Regulated Industries (healthcare — including drug-delivery devices — automotive, aerospace/defense, renewables), and Connected Living & Digital Commerce. Structurally thin margins: FY2025 revenue $29,802,000,000 produced operating income of $1,182,000,000 (financials_history.csv). The current story is the AI build-out: search results report Intelligent Infrastructure at roughly half of revenue and guided to grow 43% in fiscal 2027, with total fiscal 2027 revenue guided to $44.5 billion, and the fiscal Q4 2026 quarter printed revenue up 28.6% year on year (cited search results, company earnings release/coverage).

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $1,640,000,000; capex $468,000,000; SBC $107,000,000 (always a real cost).
- **Conservative owner's earnings FY2025: $1,065,000,000 = $9.60/share** (base_oe_latest_per_share in dcf_numbers.json)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $1,099,000,000 — close to the conservative figure, which supports using the OCF-based series.
- OE positive 5 of the last 5 fiscal years. Net debt $952,000,000 (dcf_numbers.json), 0.79x normalized OE in the final run's diagnostics — modest for a manufacturer, partly because the model is supplier-funded (negative working capital).
- OE history is genuinely volatile: conservative OE was $172,000,000 (FY2021), $185,000,000 (FY2022), $609,000,000 (FY2023), $843,000,000 (FY2024), $1,065,000,000 (FY2025) — a capex-heavy trough followed by a steep climb, not a stable base.

**Base used = TTM owner's earnings through Q3 FY2026 (2026-05-31), from ttm.py (filing-direct, no hand math):**
- OCF: FY $1,640,000,000 − prior YTD $1,052,000,000 + current YTD $1,269,000,000 = **TTM $1,857,000,000**
- Capex: FY $468,000,000 − prior YTD $299,000,000 + current YTD $382,000,000 = **TTM $551,000,000**
- SBC: FY $107,000,000 − prior YTD $84,000,000 + current YTD $115,000,000 = **TTM $138,000,000**
- Shares (current-YTD weighted diluted): **107,200,000**
- **TTM OE total $1,168,000,000 → base OE/share $10.90** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $6.78/share — rejected as the base; see BASE_DIVERGENCE under Flags. Corroboration since the TTM window: the fiscal 2026 earnings release (cited search result) reports full-year FY2026 operating cash flow of $2,002 million and capex of $628 million — directionally consistent with the TTM step-up, though no OE figure is computed from it here (the FY2026 10-K is not yet in the engine's filing history).

## Moat: 4/10 — weak-to-moderate
Justification: Real scale, customer integration, and regulated-industry qualifications, but this is a price-competitive contract-manufacturing business with structurally thin margins (~4-6% operating), concentrated customers, and rivals (Flex, Celestica, Sanmina, Foxconn) bidding for the same programs — pricing power is limited and programs can be dual-sourced or moved.
- FOR: Global scale and footprint (US/Mexico/India/China) that few EMS rivals can match for hyperscaler ramps
- FOR: Deep customer integration — design, systems integration, and supply-chain management, not just assembly; switching a qualified line is slow and risky for the customer
- FOR: Regulated Industries qualifications (healthcare/drug-delivery, aerospace/defense) carry certification barriers and long program lives
- FOR: AI infrastructure capability stack (power, liquid cooling, photonics, networking) built partly by acquisition, now the growth engine
- AGAINST: Structurally thin margins — FY2025 operating income $1,182,000,000 on $29,802,000,000 of revenue leaves almost no error tolerance
- AGAINST: Customer concentration — cited search results put the five largest customers at ~36% of FY2025 revenue and one customer at 16%
- AGAINST: EMS is bid competitively; customers dual-source and can in-source or shift programs to Flex/Celestica/Foxconn
- AGAINST: The growth engine is the hyperscaler AI capex cycle — a digestion year hits growth and the multiple at the same time
- A 4 gives CAP = 7.2 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 7.2 years, 15-year projection.

## DCF — v5 final run (2026-10-14)
Growth recalibration (written reason): the engine's blended growth is 2.49% and g_base is 7.49% after the +5pp buyback adjustment — but the blend is straddling the Mobility divestiture break (rev CAGR 3y −3.80%) and pre-inflection years, while the company just printed fiscal 2026 revenue growth of 21%, a fiscal Q4 2026 quarter up 28.6% year on year, and guided fiscal 2027 revenue to $44.5 billion with adjusted EPS guidance of $17.55 (all cited search results). Scenario starts were therefore set via offsets (−0.075 / +0.025 / +0.165 / +0.245 / +0.325 vs g_base) to 0 / 10 / **24** / 32 / 40%. Sanity check against prints: the base start (24%) sits below the latest quarterly revenue print (+28.6%) and below the guided core-EPS trajectory — deliberate, because OE deducts rising AI-capacity capex (TTM capex $551,000,000 vs FY2025's $468,000,000) and SBC, and EMS margins are thin; the bull start (32%) roughly matches the guided earnings trajectory and the super-bull (40%) requires execution above guide. Even under the preliminary engine defaults the stock was Tier D (weighted IRR 5.71%, IV@15% $73.20), so the recalibration — not the defaults — is what gets it to C. Probabilities 15/25/30/20/10 (bear weight widened per OE_VOLATILE); OE multipliers at the defaults 0.75/0.90/1.00/1.10/1.25. Price $304.27.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | 0.0% | 0.75 | Hyperscaler digestion year; AI programs stall, OE margin compresses | $60.81 | 4.94% |
| Bear | 25% | 10.0% | 0.90 | AI growth halves; regulated industries carry a slow year | $106.93 | 7.09% |
| Base | 30% | 24.0% | 1.00 | FY2027 guide broadly delivered, then a normal fade over the CAP | $198.91 | 11.11% |
| Bull | 20% | 32.0% | 1.10 | AI ramp + margin expansion + buybacks track the guided EPS path | $290.59 | 14.53% |
| Super bull | 10% | 40.0% | 1.25 | Multi-year AI supercycle, share gains, margins keep expanding | $435.13 | 19.08% |

- **Probability-weighted: IV@15% $197.16 (−35.2% vs price), IV@12% $270.63, IV@10% $353.46, weighted IRR 11.07%, base-case IRR 11.11%**
- **Tier by numbers: C.** Diagnostics (dcf_numbers.json): OE yield 3.58%, terminal value 21.9% of IV@15%, scenario spread 7.15x, net debt 0.79x normalized OE, 13.4 months since FY end.
- Hurdle-clearing price: the weighted IV@15% of $197.16 is the price at which the weighted case clears 15% — and the bear case ($106.93) sits far below it, so a margin of safety means paying well under $197.16, not at it. Even the bull case ($290.59) does not clear the current $304.27 price at a 15% discount rate.

## Flags — every fragility flag resolved
- **STALE_FY** (latest FY ended 13.4 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q3 FY2026 (2026-05-31), quoted above, and the FY2026 earnings release since then (OCF $2,002 million, capex $628 million, cited search result) corroborates the step-up rather than contradicting it.
- **BASE_DIVERGENCE** (latest FY OE/share $9.60 vs 3-yr median $6.78): the median is the lagging figure, not the distorted one. The last-3-FY series is a rising trend — FY2023 OE was depressed by capex of $1,030,000,000, and OE/share has since climbed as capex normalized and the share count shrank (135,900,000 diluted shares in FY2023 to 110,900,000 in FY2025, financials_history.csv). The TTM base ($10.90) continues that trend on filed numbers, so the TTM base is used and the median is reported for reference.
- **NI_OCF_DIVERGENCE** (2025): explained by one-offs inside net income, not by the cash series. FY2025 net income of $657,000,000 absorbed restructuring charges, a pre-tax loss of $97 million on the divestiture of the Italy operations (partly offset by a $54 million post-closing Mobility gain), hurricane damage costs, and a preferred-stock impairment (cited search results, FY2025 earnings release footnotes); the comparison year FY2024 net income of $1,388,000,000 was itself inflated by a $942 million pre-tax gain on the Mobility sale to BYD. The conservative OE series is built on OCF ($1,640,000,000 in FY2025), which excludes those divestiture gains/losses, so the divergence does not contaminate the base.
- **OE_VOLATILE** (OE/share spans >3x over 5 years): real — capex cyclicality (FY2021–22 capex above $1.1B against weak OCF) plus the AI ramp. Handled with 40% combined weight on bear/super-bear, default bear multipliers, and low confidence.
- **BUYBACK_TAILWIND** (share count shrinking 8.4%/yr): already credited via the +5pp share-count adjustment in the engine's blend; the recalibrated scenario starts are absolute OE/share growth rates, so buybacks are counted once, inside them — not added again in the verdict.
- **WIDE_SCENARIO_SPREAD** (super-bull IV 7.15x super-bear IV): real — the outcome hinges on how long the AI capex cycle runs. Confidence is low, and the verdict is sized to the conservative end.

## My thoughts / overlay
- The honest headline is the method range: defensible inputs span Tier D (preliminary defaults: weighted IRR 5.71% on the median base) to Tier C (final: 11.07% on the TTM base with guidance-calibrated growth). No defensible run gets near the 15% hurdle at $304.27 — even the super-bull scenario only reaches a 19.08% IRR, and it carries 10% weight.
- Quality is middling, not poor: OE positive 5/5 years, net debt $952,000,000 is modest, the maintenance OE definition corroborates the conservative one, and buybacks are real (diluted shares 135,900,000 in FY2023 → 107,200,000 TTM). The problem is purely price versus a thin-margin OE stream: a 3.58% OE yield on the TTM base has to compound at guide-level rates for years just to reach a C.
- Risks: hyperscaler concentration and AI capex cyclicality; thin margins mean a single program loss, tariff hit, or working-capital swing moves OE a lot; capex is already rising again for AI capacity (TTM $551,000,000 vs FY2025 $468,000,000), which directly docks conservative OE; recurring restructuring/divestiture charges (FY2024–FY2026) are a pattern, not a one-off, even though they sit mostly outside OCF-based OE.

## Final verdict
- **Final tier: C** (weighted IRR 11.07% on the v5 final inputs; method range D to C)
- Confidence: **Low** (wide scenario spread 7.15x, OE volatility, and a growth recalibration that depends on the AI cycle lasting)
- One-liner: Real AI-driven OE growth and buybacks, moat 4/10 — but at $304.27 the thin-margin OE stream only returns 11.1% weighted (IV@15% $197.16); it clears 15% only well below $197.16, and even the bull case sits under the current price.
