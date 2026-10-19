# GNRC — Generac Holdings Inc.
Engine 5.4.0 run, 2026-10-17. All figures below are copied from dcf_numbers.json, ttm.json, ttm.py output, or fundamentals.json — none are recomputed.

## What it is
Designer/manufacturer of backup power and energy technology (SIC 3621, Motors & Generators, NYSE). Three engines: Residential (home standby generators — >70% US category share — plus portables), Commercial & Industrial (large standby gensets, mobile power, controls; now riding data-center backup demand), and energy technology (PWRcell storage, smart thermostats/load control). Home standby category penetration was only 6.75% at end-2025 per the Q4 2025 call, so the residential runway is real but demand is outage-driven and lumpy. Market cap $11,421,257,483 at $192.68 (nasdaq_quote_api) — in scope under $40B. No dividend.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $437,978,000; capex $169,850,000; SBC $49,947,000 (always a real cost).
- **Conservative owner's earnings FY2025: $218,181,000 = $3.68/share** (base_oe_latest_per_share $3.6808).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC) is −$3,439,000 for FY2025 — not usable: it is crushed by the $187,978,000 working-capital build in the history file, not by operations. The OCF-based conservative figure is the series used throughout.
- OE positive 4 of the last 5 fiscal years: OE/share ran $6.33 (2020), $4.31 (2021), **−$0.88 (2022 — OCF collapsed to $58,518,000 on a $512,363,000 working-capital build during the supply crunch)**, $5.75 (2023), $9.20 (2024), $3.68 (2025). This is a genuinely cyclical OE stream, not a compounder's staircase.
- Net debt $925,147,000 (LongTermDebtNoncurrent + LongTermDebtAndCapitalLeaseObligationsCurrent + ShortTermBorrowings, per dcf_numbers.json), plus lease liabilities $51,881,000; net debt is 2.83x normalized OE (diagnostics). Gross leverage ~1.9x Adjusted EBITDA per the Q4 2025 call — manageable, not a balance-sheet story either way.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $437,978,000 − prior YTD $130,341,000 + current YTD $240,496,000 = **TTM $548,133,000**
- Capex: FY $169,850,000 − prior YTD $88,653,000 + current YTD $87,687,000 = **TTM $168,884,000**
- SBC: FY $49,947,000 − prior YTD $26,360,000 + current YTD $27,447,000 = **TTM $51,034,000**
- Shares (current-YTD weighted diluted): **59,436,379**
- **TTM OE total $328,215,000 → base OE/share $5.52** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $5.75/share — the TTM base sits just below it, and the two corroborate each other (see BASE_DIVERGENCE below). TTM revenue $4,438,732,000 and TTM gross margin 39.5% per fundamentals.json.

## Moat: 5/10 — moderate/narrow, real in residential, unproven in C&I
Justification: dominant home-standby share, brand and dealer network are genuine, but the returns evidence has compressed for five straight years and the new growth leg is contested ground where Generac holds no share dominance.
- FOR: >70% share of the US home standby category built over decades — the default brand for an infrequent, high-ticket, dealer-installed purchase; extensive dealer/installer and retail distribution network that is expensive to replicate; installed base feeds parts, service and monitoring attach; scale in large-megawatt genset production now converting into hyperscale data-center supply agreements (backlog $1.6B at Q2 2026).
- AGAINST: ROIC proxy (fundamentals.json) fell from 23.1% (2020) to 19.2% (2021), 12.8% (2022), 7.8% (2023), 11.7% (2024), 6.6% (2025) — a moat that wide should not print 6.6% in year five of the fade; gross margin has oscillated in a 33.3–38.8% band (33.3% in 2022, 38.8% in 2024, 38.3% in 2025) with mix and tariffs, i.e. no demonstrated pricing power through the cycle; in C&I/data-center Generac faces Cummins and Caterpillar with deeper diesel franchises and no share dominance; residential demand is hostage to outage activity (an exogenous weather variable, not a franchise asset); clean-energy/PWRcell has consumed capital without establishing a second moat.
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection. A 7+ would need ROIC sustained well above the cost of capital through the cycle — the filed history shows the opposite trend, so 5 is the honest score.

## DCF — final run (2026-10-17)
**Growth sanity check (mandatory):** the engine's blended start is 0.52%, built entirely from filed FY history (latest FY revenue YoY −2.02%, 3-yr revenue CAGR −2.67%, OE/share 2-yr CAGR −20.01%) — it predates the 2026 inflection and cannot be used as-is. Actual recent prints: Q2 2026 net sales $1.17B, +11% YoY (C&I +29% to $556M on data-center shipments >$100M in the quarter; Residential −2% to $617M), and management guides FY2026 consolidated net sales growth to the mid-to-high teens with C&I in the low-30s. Scenario starts were therefore recalibrated via offsets (−0.055243 / +0.014757 / +0.094757 / +0.154757 / +0.234757 vs the 0.52% blend):
- **Base start 10% is deliberately below the +11% Q2 print and below the mid-to-high-teens revenue guide** — written reason: OE/share growth lags revenue growth here because the growth mix is lower-margin C&I (management expects 2026 gross margin near the low end of its 38.5–39.5% range excluding the Q2 tariff refund), residential is still declining, and Q2 2026 profitability was flattered by a one-time tariff refund (Q2 gross margin printed 44.5% in fundamentals.json) that does not repeat in OE.
- Bull 16% ≈ the revenue guide with modest operating leverage. Super bull 24% requires the data-center backlog ($1.6B, ~$1B booked in the 90 days to Q2, ~$450M of 2026 data-center revenue expected, ~$700M of 2027 hyperscale commitments) to convert at expanding margins plus a residential recovery on normalized outage activity — aggressive against an OE history that printed −$0.88/share in 2022 and a −20% 2-yr OE CAGR, so it is not set higher.
- Super bear −5%: the outage drought persists, residential slides again, and data-center orders slip against the capacity Generac is adding.
Probabilities shifted 5pp from bear to super bull (10/20/30/25/15) for the contracted data-center visibility; OE multipliers are the defaults 0.75/0.90/1.00/1.10/1.25. Price $192.68.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | −5.0% | 0.75 | Outage drought persists; data-center orders slip; capacity overhang | $24.82 | 3.96% |
| Bear | 20% | +2.0% | 0.90 | C&I grows but residential drag and mix keep OE near flat | $39.91 | 5.08% |
| Base | 30% | +10.0% | 1.00 | Data-center ramp + residential stabilization, OE lagging revenue on mix | $61.77 | 6.75% |
| Bull | 25% | +16.0% | 1.10 | Guide delivered with modest leverage; backlog converts on time | $86.84 | 8.58% |
| Super bull | 15% | +24.0% | 1.25 | Hyperscale scale-up + outage normalization + margin expansion | $136.17 | 11.81% |

- **Probability-weighted: IV@15% $71.13 (−63.1% vs price), IV@12% $96.30, IV@10% $124.58, weighted IRR 7.49%, base-case IRR 6.75%**
- **Tier by numbers: D** (bear D, bull D — no band question). Diagnostics: OE yield 2.87%, terminal value 20.6% of IV@15%, scenario spread 5.49x, net debt 2.83x normalized OE, 9.5 months since FY end.
- Hurdle-clearing prices (weighted): 15% at $71.13, 20% at $48.80, 25% at $36.71. Even the super-bull IV@15% ($136.17) sits 29% below the $192.68 price, and the super-bull IRR (11.81%) does not clear 15%.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.5 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, legs quoted above (TTM OE/share $5.52 vs latest FY $3.68).
- **BASE_DIVERGENCE** (latest FY $3.68 vs 3-yr median $5.75): the latest FY is the distorted one — FY2025 absorbed an extremely low outage environment (residential sales −7% for the year), a Q4 2025 net loss amid a legal settlement charge, Q4 gross margin of 36.3% vs 40.6% a year earlier on mix/inventory charges, and clean-energy drag. The median is corroborated independently by the TTM base ($5.52 through Q2 2026, with Q2 net income of $143M annualizing well above the FY2025 trough), so the normalized/TTM zone — not the trough FY — is the right base. Neither figure flatters the verdict at this price.
- **NI_OCF_DIVERGENCE** (NI vs OCF differ >40% in 2023, 2024, 2025): explained, not sinister. It is a non-cash-heavy P&L plus working-capital swings: D&A ran $166,602,000 (2023), $171,768,000 (2024), $194,835,000 (2025) and SBC $35,492,000 / $49,248,000 / $49,947,000 — together most of the NI→OCF gap each year — on top of working-capital releases reversing 2022's $512,363,000 build (ΔNWC −$141,654,000 in 2023, −$198,186,000 in 2024), and 2025 net income was further depressed by the Q4 legal settlement and inventory charges that do not consume operating cash the same way. The OCF-based conservative OE used throughout is unaffected by the NI-side charges; if anything it is the generous series (2024's $9.20/share OE print rode the WC release, which is why the median/TTM base, not 2024, anchors the run).
- **BUYBACK_TAILWIND** (share count −2.9%/yr): already credited via the +2.87pp growth adjustment applied to the revenue components of the blend (v5.4 basis, dcf_numbers.json); the final run's recalibrated starts are OE/share growth rates set against actual prints, so the tailwind is not double-counted in the verdict. Note the pace is modest in cash terms: ~1.11M shares repurchased for $148M in FY2025, new $500M authorization approved Feb 2026.
- **WIDE_SCENARIO_SPREAD** (super-bull IV 5.49x super-bear IV): real — the outcome genuinely hinges on whether data-center OE compounds at 20%+ for years or the residential cycle reasserts itself. Confidence is capped at medium per the rule, and the verdict is sized to the conservative end: every scenario, including super bull, prices below the market.

## My thoughts / overlay
- The honest headline is not the growth debate — it is the starting multiple. At $192.68 the market pays ~35x TTM OE/share ($5.52) for a business whose OE/share has compounded negatively over the last two filed years and whose ROIC has slid from 23.1% to 6.6% in five years. The preliminary engine run (filed-history growth, median base) printed weighted IV@15% $46.70; this final run — TTM base, growth recalibrated up to the current prints and guidance, 5pp of probability shifted to super bull — prints $71.13. That $47–$71 band across defensible methods is the method range, and the entire band sits 63–76% below the price. The verdict does not depend on winning any single assumption.
- The data-center pivot is real and contracted (backlog, hyperscale agreements, C&I guided to low-30s growth), and it is the first credible second engine Generac has had. But C&I/data-center is lower-margin, capacity-hungry (capex already 4% of sales and rising with new plants), and contested by Cummins/Caterpillar — it buys growth, not obviously returns on capital. Watch whether ROIC re-rates above ~12% as the backlog converts; that, not the revenue line, is what would change this score.
- Method note: with the base at the TTM print and bull starts at the guidance rate, the remaining upside case needs a decade of what Generac has never strung together — uninterrupted double-digit OE compounding. Possible; not payable at $192.68 under a 15% hurdle.

## Final verdict
- **Final tier: D** (weighted IRR 7.49% on the final inputs; bear and bull both D; even super bull earns only 11.81%)
- Confidence: **Medium** (high on the OE base — TTM and median corroborate; capped at medium by the 5.49x scenario spread)
- One-liner: Real home-standby franchise (70%+ share, moat 5/10) but fading returns — ROIC 23.1%→6.6% in five years — and at $192.68 (~35x TTM OE) even the super-bull case earns 11.8%; Tier D, clears 15% only below $71.13.
