# ITT — ITT Inc.
v5 run, 2026-10-16. In scope (market cap $15.783B at $197.54, nasdaq_quote_api).

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.py output, or financials_history.csv — none are recomputed.

## What it is
Diversified maker of engineered critical components in three segments: Flow Technologies (Industrial Process — Goulds Pumps and other centrifugal/twin-screw pumps, engineered valves, Svanehøj), Motion Technologies (brake friction, KONI shock absorbers), and Connect & Control Technologies (ITT Cannon harsh-environment connectors and control components for aerospace, defense and industrial markets). Customers in ~40+ countries; end markets are transportation, industrial, energy, aerospace and defense.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** revenue $3,938.5M; operating cash flow $668.8M; capex $121.3M; SBC $36.2M (always a real cost).
- **Conservative owner's earnings FY2025: $511.3M = $6.40/share** (latest FY OE/share, key_numbers.md)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $476.4M — same ballpark as the conservative figure, which supports the base.
- OE positive 4 of the last 5 fiscal years. The miss is FY2021, when conservative OE was negative on the filed history (OCF leg was negative that year despite positive net income) — the core of the OE_VOLATILE flag below.
- SBC is modest relative to OCF on the filed history ($36.2M in FY2025) — no dilution/SBC red flag in the annual data. The dilution issue is forward, not historical: see STALE_FY / SPX FLOW below.

**Base used = TTM owner's earnings through Q2 2026 (period ended 2026-07-04), from ttm.py (filing-direct, no hand math):**
- OCF: FY $668.8M − prior YTD $267.1M + current YTD $231.1M = **TTM $632.8M**
- Capex: FY $121.3M − prior YTD $53.2M + current YTD $55.2M = **TTM $123.3M**
- SBC: FY $36.2M − prior YTD $17.2M + current YTD $20.1M = **TTM $39.1M**
- Shares (current-YTD weighted diluted): **88,400,000** — up sharply from 79,900,000 in FY2025, reflecting the equity raise that funded the SPX FLOW acquisition
- **TTM OE total $470.4M → base OE/share $5.32** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $5.02/share; the latest FY is $6.40/share. The TTM base sits between them and is the most current filing-derived figure, but it is NOT a clean run-rate: it carries the enlarged post-raise share count for the full denominator while SPX FLOW contributed only part of the TTM period (its first full quarter was Q2 2026), and H1 OCF is seasonally the weaker half. Both distortions are noted rather than adjusted — no base_override was declared, because any SPX run-rate construction would need figures outside this run's code outputs.

## Moat: 6/10 — moderate, niche-strong
Justification: spec-in engineered components with installed-base aftermarket in pumps, qualified high-reliability aerospace/defense connectors, and leading friction/KONI brands support pricing power and ~20% adjusted operating margins, but positions are niche-by-niche against larger diversified rivals, end markets are cyclical, and the SPX FLOW deal adds integration and leverage risk.
- FOR: Spec-in, qualified components for harsh/critical applications — switching requires requalification; Installed-base aftermarket in pumps (Goulds) and flow products — recurring, higher-margin revenue; Leading niche brands: Goulds Pumps, ITT Cannon connectors, KONI, Friction Technologies; Demonstrated pricing power — price/cost favorable, adjusted operating margin guided to ~20.5% for 2026; Aerospace/defense backlog and multi-year program visibility in Connect & Control.
- AGAINST: Niche-by-niche competition from larger, deeper rivals (Eaton, Parker Hannifin, Flowserve, TE Connectivity, ZF/Knorr-Bremse); Cyclical end markets — auto production, industrial short-cycle, energy capex; SPX FLOW integration risk and post-deal leverage after the FY-end net-cash position was deployed; Equity raise for SPX FLOW lifted diluted shares from 79.9M (FY2025) to 88.4M (H1 2026 YTD) — historical buyback tailwind reversed; Commodity/steel and tariff cost exposure, only partly offset by pricing.
- A 6 gives CAP = 9.8 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 9.8 years, 15-year projection.

## DCF — v5 final run (2026-10-16)
Growth sanity check (mandatory): engine blend 9.68% → g_base 11.22% (components: rev CAGR 5y 9.71%, rev CAGR 3y 9.64%, latest rev YoY 8.48%, OE/share CAGR 2y 13.57%, share-count adj +1.54pp). Against actual prints: Q2 2026 revenue rose 51.5% YoY reported but only ~13% organically (the rest is SPX FLOW); management raised FY2026 guidance to total revenue growth 38–41% with organic growth of only 5–8%, adjusted EPS $8.12–$8.32, and free cash flow $550–580M. So the base start of 11.2% sits above the guided organic revenue rate — defensible only because 2027 gets the first full year of SPX FLOW plus guided synergies and margin expansion, not because the legacy business grows that fast organically; that is a real stretch embedded in the base case and a reason the verdict does not soften. The super-bull start of 23.2% sits above the latest adjusted EPS print (+18% in Q2) — it is a 10%-weight tail requiring SPX synergies, defense backlog conversion and pricing to compound together, not a forecast. The bear start of 6.2% matches the low end of organic guidance; the super-bear start of −0.8% reflects the cyclical precedent in the filed history (revenue fell in 2020 and conservative OE was negative in 2021). The +1.54pp share-count adjustment in g_base is historical (share count CAGR −1.54%); forward, the count has risen with the SPX equity raise, so the blend if anything flatters per-share growth — noted, not adjusted, because the gap to the price is far larger than this effect. Default offsets (−12/−5/0/+5/+12pp) and OE multipliers (0.75/0.90/1.00/1.10/1.25) were kept; probabilities are the defaults 10/25/30/25/10. Price $197.54.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -0.8% | 0.75 | Industrial/auto downturn repeats the 2020-21 pattern; SPX synergies disappoint | $28.28 | 4.20% |
| Bear | 25% | 6.2% | 0.90 | Organic growth at the low end of guidance; integration costs linger | $46.33 | 5.56% |
| Base | 30% | 11.2% | 1.00 | SPX full-year contribution plus guided margin expansion, fading over the CAP | $64.29 | 6.91% |
| Bull | 25% | 16.2% | 1.10 | Defense/aerospace backlog converts, pricing holds, synergies land early | $88.24 | 8.62% |
| Super bull | 10% | 23.2% | 1.25 | Category-compounder path: synergies, share gains and aftermarket mix all compound | $136.35 | 11.70% |

- **Probability-weighted: IV@15% $69.39 (−64.9% vs price), IV@12% $94.39, IV@10% $122.56, weighted IRR 7.33%, base-case IRR 6.91%**
- **Tier by numbers: D.** Diagnostics (key_numbers.md): OE yield 2.69%, terminal value 21.2% of IV@15%, scenario spread 4.82x, net debt −2.26x normalized OE, 9.5 months since FY end.
- Even the super-bull case (IV@15 $136.35, IRR 11.70%) does not reach the $197.54 price — the shortfall is not a scenario-weighting argument.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.5 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, quoted above. Consequence flagged in the base discussion: the TTM window straddles the SPX FLOW close and the equity raise, so it is current but not a clean run-rate.
- **OE_VOLATILE** (OE/share range over the last 5 yrs spans >3x): real and cyclical, not an inflection — FY2021 conservative OE was negative on the filed history while surrounding years were solidly positive. Handled by using a TTM base between the median ($5.02) and latest FY ($6.40), keeping 35% of probability on bear-or-worse, and confidence low.
- **WIDE_SCENARIO_SPREAD** (super-bull IV 4.82x super-bear): real — the outcome range is genuinely wide post-acquisition. Confidence is low (never high under this flag), and the verdict is sized to the conservative end; note even the widest end of the spread does not clear the price.
- **BIG_NET_CASH** (net cash 2.3x normalized OE at FY end; net debt $-960.1M latest, key_numbers.md): resolved with a timing caveat — that cash pile is a FY2025 year-end snapshot and has since been deployed into SPX FLOW. Post-close reporting (Q2 2026) shows cash down to $590.8M with short-term borrowings of $858.4M and a reported leverage ratio of 2.5x, targeted to ~2.3x by year-end. So the "part of the price is a cash pile" reading no longer holds: the balance sheet is now a levered acquirer's, and no net-cash credit is taken in the verdict beyond what the engine's FY-end figure already embeds.

## My thoughts / overlay
- Method range: the preliminary run on the normalized median base ($5.02/share, moat 5 defaults) gave weighted IV@15% $63.06 and weighted IRR 6.84%; the final TTM-base run gives $69.39 and 7.33%. Both are Tier D — the method range is D to D, unusually tight for this sweep, because the price (37x the TTM base OE/share on the engine's OE yield of 2.69%) leaves no room for base choice to matter.
- Quality is not the debate: the business prints ~20% adjusted operating margins, raised guidance in Q2 2026, and carries a growing defense backlog. Valuation is the debate: at $197.54 the market is paying for the SPX FLOW transformation to compound at rates above anything in the filed OE history (rev CAGR ~9.6-9.7%, OE/share CAGR 2y 13.57%).
- Balance-sheet overlay: FY-end net cash has become ~2.5x leverage post-deal (see BIG_NET_CASH). Deleveraging progress and SPX synergy capture ($80M targeted, per management commentary around the deal) are the two things that could legitimately raise the OE path — neither is in the filed TTM yet.
- Hurdle-clearing price: the weighted IV@15% is $69.39 — that is the price at which the weighted case clears 15%. With a margin of safety against the bear cases (bear IV@15 $46.33), a conservative buyer needs a price well under $69.39, i.e. less than a third of the current quote. There is no plausible filing-based input set in this run that gets the 15% hurdle anywhere near $197.54.

## Final verdict
- **Final tier: D** (weighted IRR 7.33% on the v5 final inputs; tier by numbers D, no override)
- Confidence: **Low** (OE volatility, wide scenario spread, and a TTM base that straddles a transformational acquisition and equity raise)
- One-liner: Quality engineered-components maker, moat 6/10 — does not clear 15% at $197.54 (weighted IRR 7.33%, weighted IV@15 $69.39); it clears 15% only at about $69, so the price pays for far more growth than the filing-based OE supports.
