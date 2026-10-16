# WWD — Woodward, Inc.
v5 run, 2026-10-16. In scope (market cap $20.484B at $333.27, nasdaq_quote_api).

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.py output, or financials_history.csv — none are recomputed.

## What it is
Energy-control systems for aerospace and industrial markets: fuel, actuation and engine controls specified into commercial and defense aircraft platforms (plus a services/aftermarket annuity on the installed base), and industrial controls for power generation, marine transportation, and oil & gas. Q3 FY26 (ended June 30, 2026): net sales $1.1B, +21% YoY; Aerospace sales $709M (+19%), Industrial $401M (+26%) — per the company's Q3 FY26 release (GlobeNewswire, July 29, 2026). FY26 guidance raised at Q3: sales growth +20–23%, adjusted EPS $9.30–$9.50, free cash flow $300–350M, capex ~$290M.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $471,294,000; capex $130,928,000; SBC $31,674,000 (always a real cost).
- **Conservative owner's earnings FY2025: $308,692,000 = $5.02/share** (latest FY OE/share, key_numbers.md)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $293,133,000 — same ballpark as the conservative figure, which raises confidence.
- OE positive 5 of the last 5 fiscal years. Net debt $252,471,000 (dcf_numbers.json). Share count is drifting down slowly (share CAGR −0.95%/yr, credited in the blend as +0.95pp).

**Base used = TTM owner's earnings through Q3 FY26 (June 30, 2026), from ttm.py (filing-direct, no hand math):**
- OCF: FY $471,294,000 − prior YTD $237,976,000 + current YTD $351,937,000 = **TTM $585,255,000**
- Capex: FY $130,928,000 − prior YTD $78,537,000 + current YTD $156,337,000 = **TTM $208,728,000**
- SBC: FY $31,674,000 − prior YTD $25,490,000 + current YTD $28,653,000 = **TTM $34,837,000**
- Shares (current-YTD weighted diluted): **61,317,000**
- **TTM OE total $341,690,000 → base OE/share $5.57** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $4.99/share. The TTM base is used because the FY ended 12.5 months ago and FY26 is printing a step-change (sales +20–23% guided). Note the TTM base is *conservative* in one respect: TTM capex of $208,728,000 is a capacity-expansion figure (FY26 guided capex ~$290M vs FY2025's $130,928,000), so a chunk of it is growth capex the conservative definition charges in full anyway, per the standardized method.

## Moat: 7/10 — strong
Justification: certified, specified-in content on long-lived airframe/engine platforms with a services annuity and demonstrated pricing power; held back from 8+ by customer concentration (top 5 ≈ 36% of revenue, per analyst research summaries), dependence on Boeing/Airbus build rates, and a front-loaded capacity-capex phase.
- FOR: Sole-source / specified-in positions on major commercial and defense platforms — certification and requalification costs lock Woodward in for the platform's life; Decades-long platform lives plus a high-margin aftermarket/services annuity (Q3 FY26: commercial services +24%, defense services +20%); Deep fuel-system and actuation engineering know-how, extended into electrification by the Safran North American electromechanical actuation acquisition; Demonstrated pricing power — companywide pricing ~8% in FY26 (per Q3 FY26 reporting), guided to normalize to 3–5%.
- AGAINST: Customer concentration — top 5 customers ≈ 36% of revenue; hostage to Boeing/Airbus production schedules and program health; OEM pricing pressure at concentrated customers once the current pricing cycle normalizes; Heavy front-loaded capex phase (including a new U.S. facility for the A350 spoiler-actuator win, initial deliveries not expected until late CY28) depresses near-term OE/FCF; Cyclical aero and industrial end-markets, and the China on-highway business exit is a drag until substantially completed.
- A 7 gives CAP = 11.1 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 11.1 years, 15-year projection.

## DCF — v5 final run (2026-10-16)
Growth recalibration (written reason): the engine's blended g_base is 11.85% (components: rev CAGR 5y 7.41%, rev CAGR 3y 14.39%, latest FY rev YoY 7.30%, OE/share CAGR 2y 21.63%, share-count adj +0.95pp). That blend is backward-looking — it averages in the COVID-era trough and FY25's +7.30% year — while FY26 is actually printing sales growth of +20–23% (guided), Q3 sales +21%, and Q3 adjusted EPS +43% YoY. Scenario starts were therefore recalibrated upward via offsets (−0.1385 / −0.0485 / +0.0315 / +0.0815 / +0.1615) to −2 / 7 / **15** / 20 / 28%. The starts still sit below the current EPS prints for a written reason: FY26 pricing of ~8% is guided to normalize to 3–5%, Q3 aero margin included a retroactive contract-pricing benefit (~100bp), and owner's earnings — unlike EPS — must absorb the guided ~$290M capex year. Probabilities 10/25/30/25/10; OE multipliers 0.75/0.90/1.00/1.10/1.25. Price $333.27.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -2.0% | 0.75 | Aero downcycle + OEM rate cuts; capex already spent | $27.75 | 3.45% |
| Bear | 25% | 7.0% | 0.90 | Growth mean-reverts to the 5-yr revenue CAGR; pricing normalizes hard | $50.88 | 4.55% |
| Base | 30% | 15.0% | 1.00 | Aero ramp + data-center power demand decay normally over the CAP | $82.68 | 6.10% |
| Bull | 25% | 20.0% | 1.10 | FY26 growth rates persist longer; capex normalizes after the build-out | $115.33 | 7.58% |
| Super bull | 10% | 28.0% | 1.25 | Durable multi-year supercycle in aero + power generation | $191.29 | 10.60% |

- **Probability-weighted: IV@15% $88.26 (−73.5% vs price), IV@12% $122.22, IV@10% $160.83, weighted IRR 6.41%, base-case IRR 6.10%**
- **Tier by numbers: D.** Diagnostics (key_numbers.md): OE yield 1.67%, terminal value 23.3% of IV@15%, scenario spread 6.89x, net debt 0.74x normalized OE, 12.5 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 12.5 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q3 FY26 (June 30, 2026), quoted above.
- **OE_VOLATILE** (OE/share spans >3x over 5 years): real and visible in the filed history — conservative OE was $405,505,000 in FY2021, fell to $120,661,000 in FY2022 (OCF trough of $193,638,000 in the aero downturn), and recovered to $308,692,000 by FY2025. It is cyclicality plus working-capital swings, not accounting noise; handled by the TTM base and by keeping 35% of probability on bear-or-worse outcomes.
- **LOW_OE_YIELD** (base OE yield 1.67%): the central fact of this stock at $333.27 — the valuation rests almost entirely on future growth. Even the super-bull scenario (28% growth start, 1.25x OE) produces only a 10.60% IRR and an IV@15% of $191.29, well below the price. The flag does not make the tier fragile in the usual sense: no plausible growth path rescues it at this price.
- **WIDE_SCENARIO_SPREAD** (6.89x): real — outcomes genuinely range from downcycle to supercycle. Confidence is capped at medium, and the verdict needs no sizing adjustment because every scenario, including super bull, lands in Tier D territory.

## My thoughts / overlay
- Method range: the preliminary run (median base $4.99/sh, default offsets) gave a weighted IRR of 5.19% and IV@15% of $64.38; the final run (TTM base, growth starts recalibrated toward actual FY26 prints) gives 6.41% and $88.26. Both are Tier D, and the *best single scenario* in the final run (super bull, 10.60% IRR) still fails the 15% hurdle — the conclusion does not depend on method choices.
- Quality is not the debate: 5/5 positive OE years, modest net debt ($252,471,000; 0.74x normalized OE), a real aftermarket annuity, and FY26 execution is strong (guidance raised at Q3). The debate is purely price: at $333.27 the market is paying for a decade of high-teens compounding that even this generous scenario set does not deliver at a 15% discount rate.
- The capex surge cuts both ways: it depresses the TTM base today (conservative), but the spending is for contracted capacity (A350 spoiler actuators, Glatten fuel-injection expansion +50% capacity) whose returns arrive from late CY28 — a buyer today funds the build-out years at a full price.
- Price that clears 15%: at or below the weighted IV@15% of **$88.26** on the final inputs — roughly a quarter of the current price. Even crediting the super-bull path alone, the hurdle-clearing price is $191.29.

## Final verdict
- **Final tier: D** (weighted IRR 6.41% on the v5 final inputs; no tier override — the numbers and the overlay agree)
- Confidence: **Medium** (high on the filing-derived base and on the conclusion's robustness across methods; capped at medium by the 6.89x scenario spread)
- One-liner: see judgment.json.
