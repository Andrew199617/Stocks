# STE — STERIS plc
v5 run, 2026-10-15. Market cap $22.14B at $224.33 (nasdaq_quote_api) — in scope (<$40B). Fiscal year ends March 31.

All figures below are copied from key_numbers.md, dcf_numbers.json, financials_history.csv, or ttm.py output — none are recomputed. Guidance and segment detail are from the company's fiscal 2026 release and fiscal Q1 2027 reports, cited as such.

## What it is
Infection-prevention and sterilization franchise with three segments: Healthcare (sterile processing systems, endoscopy products, surgical equipment, consumables and services to hospitals and surgery centers — the largest segment), Applied Sterilization Technologies / AST (contract sterilization — gamma, ethylene oxide and other modalities — for medical-device and pharmaceutical manufacturers who cannot sterilize in-house), and Life Sciences (sterilization and formulation/filling products and services for pharma and biotech manufacturing). The model leans recurring: installed capital equipment pulls through proprietary consumables and service contracts, and AST sells regulated, validated capacity by the load. Demand is non-discretionary — sterile processing is legally mandatory — but capital-equipment orders are cyclical.

## Owner's earnings
**FY2026 (10-K via EDGAR, from financials_history.csv):** operating cash flow $1,341,400,000; capex $369,000,000; SBC $61,700,000 (always a real cost).
- **Conservative owner's earnings FY2026: $910,700,000 = $9.23/share** (base_oe_latest_per_share, key_numbers.md).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $628,800,000 — below the conservative figure this year because FY2026 carried a working-capital build (ΔNWC $271,000,000) after FY2025's inventory-reduction program had flattered cash flow. The OCF-based conservative figure is the cleaner base; the maintenance version warns that FY2025–26 working capital whipsaws both ways.
- OE positive 5 of the last 5 fiscal years. Net debt $1,812,800,000 = 2.08x normalized OE (diagnostics) — modest leverage; the company also authorized a new $1B buyback in its FY2026 release, and share count is drifting down (share_cagr −0.52%/yr, already credited in the growth blend).

**Base used = TTM owner's earnings through Q1 FY2027 (ended 2026-06-30), from ttm.py (filing-direct, no hand math):**
- OCF: FY $1,341,400,000 − prior YTD $420,000,000 + current YTD $367,100,000 = **TTM $1,288,500,000**
- Capex: FY $369,000,000 − prior YTD $93,600,000 + current YTD $87,500,000 = **TTM $362,900,000**
- SBC: FY $61,700,000 − prior YTD $11,900,000 + current YTD $12,800,000 = **TTM $62,600,000**
- Shares (current-YTD weighted diluted): **97,900,000**
- **TTM OE total $863,000,000 → base OE/share $8.82** (base_source: ttm_json)
- Why TTM over the alternatives: the engine's normalized base (3-yr median) is $7.27/share — dragged by FY2024, when OCF was $973,300,000 before the FY2025–26 recovery. The latest FY alone ($9.23/share) ignores that TTM OCF has since cooled (current-YTD OCF $367,100,000 vs prior-YTD $420,000,000 in ttm.py's legs). The TTM base sits between the two and is the most current filing-derived figure — it is not a momentum cherry-pick, since it is *below* the latest FY.

## Growth recalibration (written reason)
The engine's blend (rev CAGR 5y 13.82%, 3y 9.38%, latest YoY 8.73%, OE/share CAGR 2y 28.40% — the last a recovery artifact off the depressed FY2024 base) gives g_blend 11.60% and g_base 12.11%. That is above what the company is actually printing and guiding: FY2026 revenue grew 8.73% (latest YoY), Q1 FY2027 revenue grew 7.3% with constant-currency organic growth of 6.2%, and FY2027 guidance (company release, reiterated at Q1) is as-reported revenue growth of 7–8%, constant-currency organic growth of 6–7%, and adjusted EPS of $11.10–$11.30. Scenario starts were therefore set via offsets (−0.12 / −0.08 / −0.04 / −0.01 / +0.02 vs g_base) to 0.1 / 4.1 / **8.1** / 11.1 / 14.1%. Sanity check against prints: the base start (8.1%) sits between the revenue guide (7–8%) and the adjusted-EPS guide (+9–11% vs FY2026), which is where OE/share growth should land given modest buybacks; the bull start (11.1%) is the top of the EPS guide sustained; the super-bull start (14.1%) is above every current print — it is an explicit 10%-weight tail requiring a capital-equipment rebound plus tuck-in M&A, not a forecast. Bear/super-bear starts sit below current prints for written reasons: EO regulatory tightening, capital-equipment cyclicality (AST capital-equipment revenue fell sharply in Q4 FY2026), and tariff/inflation cost pressure the company itself flagged in FY2026 results.

## Moat: 6/10 — moderate (narrow), durable but not wide
Justification: Morningstar-style narrow moat — real switching costs and regulatory intangibles in AST and the installed Healthcare base, proven pricing power, but no network effect, several credible large rivals in Healthcare products, and an EO regulatory overhang on part of AST.
- FOR: Global contract-sterilization (AST) network scale — validated capacity, geographic redundancy device makers rely on; installed sterilizer/endoscopy equipment base in hospitals driving recurring consumables and service revenue with real switching friction; regulatory know-how (sterility validation and compliance) as an intangible barrier to entry; demonstrated pricing power — price contributed to FY2026 growth per the company release; defensive, non-discretionary demand (infection prevention is mandatory, not deferrable).
- AGAINST: Ethylene-oxide sterilization faces EPA emissions tightening and emissions-litigation risk; Healthcare products compete with large diversified rivals (e.g. Stryker, 3M, Getinge) where the moat is thinner; capital-equipment revenue is cyclical (AST capital equipment fell sharply in Q4 FY2026); tariff and inflation cost pressure on margins, flagged by the company in FY2026; growth partly bought via acquisitions, leaving heavy intangible amortization; large device makers can insource sterilization at the margin.
- A 6 gives CAP = 9.8 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 9.8 years, 15-year projection.

## DCF — v5 final run (2026-10-15)
Base OE/share $8.82 (TTM, ttm.py). Probabilities 10/25/30/25/10; OE multipliers 0.75/0.90/1.00/1.10/1.25 (defaults). Price $224.33.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | 0.1% | 0.75 | EO rules/litigation bite AST; capital-equipment downturn compounds | $48.75 | 5.13% |
| Bear | 25% | 4.1% | 0.90 | Growth halves vs guide; tariffs/inflation squeeze margins | $69.90 | 6.46% |
| Base | 30% | 8.1% | 1.00 | Guided 7–8% revenue / 9–11% adj-EPS path decays over the CAP | $92.80 | 7.91% |
| Bull | 25% | 11.1% | 1.10 | Top-of-guide EPS growth sustains; AST volumes and pricing hold | $116.63 | 9.35% |
| Super bull | 10% | 14.1% | 1.25 | Capital-equipment rebound + tuck-in M&A + operating leverage | $151.38 | 11.31% |

- **Probability-weighted: IV@15% $94.49 (−57.88% vs price), IV@12% $126.78, IV@10% $162.95, weighted IRR 8.04%, base-case IRR 7.91%**
- **Tier by numbers: D.** Diagnostics (key_numbers.md): OE yield 3.93%, terminal value 19.76% of IV@15%, scenario spread 3.11x, net debt 2.08x normalized OE, 6.5 months since FY end.

## Flags — every fragility flag resolved
- **NI_OCF_DIVERGENCE** (net income vs OCF differ by >40% in 2024, 2025, 2026): resolved — the gap is primarily non-cash D&A, dominated by acquisition-intangible amortization. From financials_history.csv: FY2024 net income $378,200,000 vs D&A $565,200,000 and OCF $973,300,000; FY2025 net income $614,600,000 vs D&A $476,200,000 and OCF $1,148,100,000; FY2026 net income $782,300,000 vs D&A $486,500,000 and OCF $1,341,400,000. D&A of $476–565M/yr against net income of $378–782M mechanically produces the divergence; the same pattern holds in FY2022–23 (net income $243,888,000 / $107,030,000 against D&A of $553,104,000 / $552,897,000). Working capital is the second driver: FY2025's OCF was flattered by a targeted inventory-reduction program, and the company noted FY2026's working-capital contribution was significantly lower. Because the base throughout is the OCF-based conservative OE (OCF − capex − SBC), the NI-side non-cash charges do not contaminate it — if anything, net income understates this company's cash earnings.
- **WIDE_SCENARIO_SPREAD** (preliminary run, 4.45x): after the growth recalibration above, the final spread is 3.11x and the flag no longer fires. The range is still wide in absolute terms — even the super-bull IV@15% ($151.38) sits well below the $224.33 price — so confidence is held at medium, not high.

## My thoughts / overlay
- This is a quality-vs-price verdict, not a quality verdict. The business is defensive, recurring, modestly levered (net debt 2.08x normalized OE), and growing at a guided high-single-digit rate — and none of that rescues the math at $224.33. The price needs growth far above guidance for a decade; the company's own FY2027 outlook (revenue +7–8%, adjusted EPS $11.10–$11.30, free cash flow guided to $850M with ~$375M of capex including a new Mentor, Ohio plant) describes a good business compounding at high single digits, not the mid-teens path the multiple embeds.
- Method range is unusually tight for this sweep: the preliminary run (median base $7.27/share, engine growth 12.11%) gave weighted IRR 8.18% and IV@15% $94.84; the final run (TTM base $8.82/share, guided growth) gives 8.04% and $94.49. Two very different input pairs land in the same place — Tier D either way. The verdict does not hinge on the base choice.
- One generosity already in the numbers: the conservative OE charges *all* capex, including growth capex for the new plant; and the TTM base is above the 3-yr median. Neither closes a gap of this size.
- The price that clears 15% on the weighted case is the weighted IV@15% itself: **$94.49**. Even clearing 10% requires ~$162.95 (weighted IV@10%). There is no margin of safety at the current price under any scenario run — the super-bull case (10% weight) still values the share at $151.38 at a 15% discount rate.

## Final verdict
- **Final tier: D** (weighted IRR 8.04% on the v5 final inputs; method range across defensible runs stays in D)
- Confidence: **Medium** (high on the filing-derived OE base and the guided growth path; the flag set is resolved, but the scenario spread is still 3.11x and growth recalibration is a judgment input)
- One-liner: see judgment.json.
