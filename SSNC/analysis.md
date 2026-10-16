# SSNC — SS&C Technologies Holdings, Inc.
v5 run, 2026-10-16. Market cap $21.308B at $84.19 (nasdaq_quote_api) — in scope under $40B.

All figures below are copied from key_numbers.md / dcf_numbers.json, ttm.py output, or financials_history.csv — none are recomputed.

## What it is
Global provider of software and technology-enabled services for financial services and healthcare: fund administration and accounting (including alternatives/hedge funds), transfer agency, wealth and investment-management platforms (Advent, Eze, Intralinks heritage), plus healthcare claims/Rx technology (DomaniRx). Revenue is largely recurring under multi-year contracts across 20,000+ clients; growth has historically been acquisition-led (DST, Eze, Intralinks, Calastone and end-2025 deals) layered on mid-single-digit organic growth. Q2 2026: GAAP revenue $1,695.7M, up 10.3% YoY (adjusted organic growth 7.6% constant-currency, flattered by large license renewals), adjusted EBITDA margin 39.5%, and full-year revenue guidance raised slightly to ~$6.75B at the midpoint (company release via Business Wire / earnings coverage).

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $1,744,800,000; capex $80,800,000; SBC $257,700,000 (always a real cost).
- **Conservative owner's earnings FY2025: $1,406,300,000 = $5.556301856973528/share** (latest FY OE/share in dcf_numbers.json)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $1,441,600,000 — close to the conservative figure, which supports the base.
- OE positive 5 of the last 5 fiscal years.
- The engine's normalized base (median of last 3 FY OE/share) is $4.42828999211978/share — it lags the current run-rate because FY2023–24 OE/share was depressed relative to FY2025 and the TTM period (see base choice below).

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $1,744,800,000 − prior YTD (H1 2025) $645,100,000 + current YTD (H1 2026) $716,400,000 = **TTM $1,816,100,000**
- Capex: FY $80,800,000 − prior YTD $35,600,000 + current YTD $19,300,000 = **TTM $64,500,000**
- SBC: FY $257,700,000 − prior YTD $112,900,000 + current YTD $123,700,000 = **TTM $268,500,000**
- Shares (current-YTD weighted diluted): **244,600,000** (down from 253,100,000 in FY2025 — buybacks, including a record repurchase quarter in Q2 2026 per earnings coverage)
- **TTM OE total $1,483,100,000 → base OE/share $6.063368765331153** (base_source: ttm_json)
- The TTM base is above even the latest FY figure because H1 2026 OCF grew double-digits YoY and the share count fell ~3% — both filing-derived, not estimated. The median base is retained in the reporting and in the method range below.

## Moat: 6/10 — moderate-to-strong, narrow-to-solid
Justification: Core fund-administration and investment-operations systems are deeply embedded, mission-critical, and painful to migrate, with high reported revenue retention and scale advantages from serial acquisitions — but the moat is assembled by M&A rather than organically compounding, organic growth is mid-single-digit, and large platform rivals and in-house builds cap pricing power.
- FOR: High switching costs — fund accounting/administration migrations take years and carry operational-error risk; recurring multi-year contract revenue with ~97% retention reported in investor materials; scale as one of the largest independent fund administrators, with breadth across alternatives, wealth, and healthcare that smaller rivals cannot match; cross-sell across an installed base of 20,000+ clients and acquired networks (e.g. Calastone's fund network); proven pricing/margin discipline — adjusted EBITDA margin 39.5% in Q2 2026.
- AGAINST: Moat is bought, not built — goodwill-heavy roll-up with integration and amortization drag; leverage (net debt $6,971,300,000) limits strategic flexibility; competition from FIS, Fiserv, Broadridge, State Street / BNY outsourcing and clients in-sourcing; organic growth only mid-single-digit (rev CAGR 5y 6.09%, 3y 5.89%) — no network-effect acceleration; AI/automation (including its own Blue Prism asset) can compress per-transaction services pricing over time.
- A 6 gives CAP = 9.8 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 9.8 years, 15-year projection.

## DCF — v5 final run (2026-10-16)
Growth sanity check: the engine's blended growth is 6.36% and g_base is 7.51% after the +1.15pp buyback/share-count adjustment. That sits squarely on the evidence: FY2025 revenue +6.63% YoY, 5-yr revenue CAGR 6.09%, Q2 2026 revenue +10.3% YoY (7.6% organic constant-currency). Scenario starts use the default offsets (−12/−5/0/+5/+12pp). The bull (12.51%) and super-bull (19.51%) OE/share starts sit above revenue growth deliberately: OE/share CAGR over the last 2 years printed 18.96% on buybacks and margin expansion, so per-share starts above the revenue line have a recent print behind them — but super bull requires that per-share compounding to persist, hence only 10% weight. Probabilities 10/25/30/25/10; OE multipliers 0.75/0.90/1.00/1.10/1.25. Price $84.19.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -4.49% | 0.75 | Fund outflows / client losses hit admin fees; leverage bites | $27.32 | 6.23% |
| Bear | 25% | 2.51% | 0.90 | Organic growth stalls at low-single digits; renewals disappoint | $44.76 | 9.15% |
| Base | 30% | 7.51% | 1.00 | Mid-single-digit organic growth plus buybacks, per recent prints | $62.13 | 11.88% |
| Bull | 25% | 12.51% | 1.10 | Renewal cycle + AI automation lifts growth and margins | $85.33 | 15.15% |
| Super bull | 10% | 19.51% | 1.25 | OE/share compounding at its recent 2-yr pace persists | $132.06 | 20.65% |

- **Probability-weighted: IV@15% $67.10, IV@12% $90.32, IV@10% $116.39, weighted IRR 12.64%, base-case IRR 11.88%**
- **Tier by numbers: C.** Diagnostics: OE yield 7.20%, terminal value 20.11% of IV@15%, scenario spread 4.83x, net debt 4.54x normalized OE, 9.49 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.49 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, inputs quoted above.
- **NI_OCF_DIVERGENCE** (2025: net income $796,900,000 vs OCF $1,744,800,000): structural, not a one-off. The filed history shows D&A of $703,800,000 and SBC of $257,700,000 in FY2025 — the roll-up model's heavy acquisition amortization plus non-cash comp explains the bulk of the gap between net income and cash flow. The conservative OE series is OCF-based and deducts both SBC and capex in full, so the divergence does not inflate the base; if anything the maintenance definition ($1,441,600,000) corroborates it.
- **WIDE_SCENARIO_SPREAD** (super-bull IV 4.83x super-bear IV): real — outcomes hinge on whether per-share compounding persists and on the levered balance sheet. Confidence capped at medium; verdict sized to the conservative end.
- **HIGH_NET_DEBT** (net debt $6,971,300,000; 4.54x normalized OE in the final run's diagnostics; debt_lt $7,408,400,000 + debt_current $25,000,000 vs cash $462,100,000 at FY2025): folded into the verdict — leverage is serviceable on current OCF (company-reported net leverage 2.75x adjusted EBITDA at Q2 2026) and buybacks continue, but it amplifies the bear cases, which is why bear/super-bear carry 35% combined weight and reduced OE multipliers, and why the tier is not upgraded on the TTM base alone.

## My thoughts / overlay
- Method range: on the engine's normalized median base ($4.43/share) the preliminary run printed a weighted IRR of 9.84% (Tier D); on the current TTM base ($6.06/share) the final run prints 12.64% (Tier C). The honest headline is C-on-current-numbers, D-on-normalized-numbers — the stock needs the recent OCF strength and buyback pace to be the new normal.
- Quality is solid but not exceptional: asset-light capex ($64.5M TTM), SBC $268.5M TTM is a real and growing cost, and growth is substantially bought with debt rather than generated organically.
- The price that clears the 15% hurdle on the weighted case is the weighted IV@15% itself: **$67.10** — about 20% below the $84.19 price. With a margin of safety against the wide spread and leverage, a buyer needs the high-$50s to low-$60s, not $84.
- Risks: acquisition-integration and goodwill, client concentration among large asset managers, fee pressure in fund administration, AI-driven deflation in back-office services pricing, and refinancing costs on a still-levered balance sheet.

## Final verdict
- **Final tier: C** (weighted IRR 12.64% on the TTM base; method range D–C)
- Confidence: **Medium** (capped by WIDE_SCENARIO_SPREAD; high on the filing-derived TTM base, lower on growth persistence)
- One-liner: Durable, levered financial-software compounder, moat 6/10 — does not clear 15% at $84.19 (weighted IRR 12.6%, IV@15 $67.10); it clears the hurdle only at or below ~$67.
