# MDB — MongoDB, Inc.
v5 run, 2026-10-14. In scope (market cap $29.70B at $365.55, nasdaq_quote_api).

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.py output, or financials_history.csv — none are recomputed.

## What it is
Developer database platform: the document-model database sold as Atlas (cloud DBaaS, consumption-priced, ~three-quarters of revenue) and Enterprise Advanced (self-managed licenses). Q2 FY2027 (ended 2026-07-31, reported 2026-09-01): revenue $771.8M, +30% YoY; Atlas revenue $565.9M, +29%; Enterprise Advanced and other +36%; net ARR expansion 122%; more than 70,600 customers (search results, Zacks/Kalkine). FY2027 revenue guidance raised to $2.99–3.03B. The quarter was the company's first GAAP operating profit. Leadership flag: CEO CJ Desai departed to join Meta; former CEO Dev Ittycheria returned as interim CEO (search results).

## Owner's earnings
**FY2026 (10-K via EDGAR, from financials_history.csv):** revenue $2,463,797,000; net income −$71,151,000; operating cash flow $505,148,000; capex $4,960,000; SBC $550,454,000 (always a real cost).
- **Conservative owner's earnings FY2026: −$50,266,000 = −$0.62/share.** OE positive in **0 of the last 5 fiscal years** — a decade of growth was funded by SBC that consumed essentially all of the operating cash flow.
- Maintenance version FY2026: $455,866,000 — positive only because of a −$509,583,000 working-capital swing in the CSV (ΔNWC column); FY2025's maintenance figure was −$884,017,000 on a +$754,945,000 ΔNWC. The maintenance series whipsaws with working capital; the conservative OCF-based series is the one used throughout.
- **Normalized base (3-yr median OE/share): −$4.79/share** — on the normalized basis, and on the latest fiscal year alone, this is a Tier F company: no positive conservative owner's earnings.

**Base used = TTM owner's earnings through Q2 FY2027, from ttm.py (filing-direct, no hand math):**
- OCF: FY $505,148,000 − prior YTD $182,034,000 + current YTD $343,509,000 = **TTM $666,623,000**
- Capex: FY $4,960,000 − prior YTD $2,148,000 + current YTD $4,791,000 = **TTM $7,603,000**
- SBC: FY $550,454,000 − prior YTD $272,831,000 + current YTD $286,769,000 = **TTM $564,392,000**
- Shares (current-YTD weighted diluted): **81,850,579**
- **TTM OE total $94,628,000 → base OE/share $1.16** (base_source: ttm_json)
- The TTM base is the prescribed STALE_FY resolution and the only positive filing-based base: OCF inflected hard (FY2026 $505,148,000 → TTM $666,623,000) while SBC growth slowed. It is still a knife-edge base — TTM SBC of $564,392,000 stands against TTM OCF of $666,623,000, so a modest SBC re-acceleration or OCF slip turns OE negative again. The normalized median (−$4.79) is rejected as the base because it averages in the pre-inflection scaling years, but it is reported here and drives the method range below.

## Moat: 5/10 — moderate/narrow
Justification: MongoDB is the de facto standard document database with real production-embedding switching costs and a consumption model that expands inside accounts (net ARR expansion 122%), but the document model itself is commoditizing — hyperscalers bundle rival DBaaS with distribution and credits, Postgres/JSONB covers more of the use case every year, and Atlas growth has held ~29% rather than accelerating despite the AI tailwind. No network effect; pricing power unproven.
- FOR: developer mindshare and default-choice status for document workloads; data gravity — production apps are costly to re-platform; Atlas consumption model with 122% net ARR expansion; multi-cloud portability that hyperscaler-native databases cannot match; platform broadening (vector search, search) — 48% of $100k+ Atlas customers use two or more platform features (search results).
- AGAINST: hyperscaler competition (AWS DocumentDB, Azure Cosmos DB) bundled with cloud distribution, credits, and procurement; Postgres + JSONB and open-source document stores eroding the model's differentiation; consumption pricing means revenue is re-earned continuously — no contractual lock-in; SBC-funded talent model structurally dilutes holders (share count +5.8%/yr); CEO transition in progress.
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — v5 final run (2026-10-14)
Engine blended growth 24.26% (rev CAGR 5y 33.08%, 3y 24.26%, latest rev YoY 22.79%; OE/share CAGR not computable off negative bases), less the −5pp share-count adjustment (share CAGR 5.79%) → **g_base 19.26%**. Default offsets and multipliers; probabilities 10/25/30/25/10. Price $365.55.

Sanity check vs prints: the scenario starts below are growth in OE/share off a just-turned-positive $1.16 base, where a "growth rate" against the negative FY2026 base is not measurable. Revenue prints +30% YoY in Q2 FY2027 and the super-bull start (31.26%) sits at that print. The verdict is not growth-start-sensitive in any case: the binding constraint is the 0.32% starting OE yield — even the super-bull path (31.26% start, 1.25× OE) produces an IV@15% of $37.96 against the $365.55 price.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | 7.26% | 0.75 | SBC re-accelerates, Atlas decelerates vs hyperscalers | $8.66 | −0.20% |
| Bear | 25% | 14.26% | 0.90 | Growth fades to low-teens; OE stays marginal | $13.86 | 3.05% |
| Base | 30% | 19.26% | 1.00 | Current trajectory decays normally over the CAP | $18.86 | 3.28% |
| Bull | 25% | 24.26% | 1.10 | Atlas holds mid-20s; operating leverage builds OE | $25.35 | 3.58% |
| Super bull | 10% | 31.26% | 1.25 | AI workloads make Atlas the default agent data layer | $37.96 | 4.18% |

- **Probability-weighted: IV@15% $20.12 (−94.5% vs price), IV@12% $27.67, IV@10% $36.20, weighted IRR 3.34%, base-case IRR 3.28%**
- **Tier by numbers: D.** Diagnostics (key_numbers.md): OE yield 0.32%, terminal value 22.2% of IV@15%, scenario spread 4.38x, 8.4 months since FY end. Balance sheet: the engine reports net_debt_latest as null (no debt balances under the tags it reads in recent years); financials_history.csv shows cash of $1,083,540,000 at FY2026 end — no balance-sheet flag fired in either direction.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 8.4 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 FY2027, quoted above.
- **DILUTION** (share count +5.79%/yr): structural, not incidental — SBC is the compensation model. TTM SBC $564,392,000 vs FY2026 $550,454,000 shows dollar SBC still rising even as it shrinks relative to revenue (reported FY2027 guidance adds back ~$628.9M of SBC, search results). The −5pp growth adjustment is already in g_base; not double-counted in the verdict. This dilution is precisely why a decade of revenue growth produced zero positive OE years.
- **NI_OCF_DIVERGENCE** (2024, 2025, 2026): no hidden one-off — the gap IS the SBC. FY2024: NI −$176,600,000 vs OCF $121,477,000, SBC $456,907,000. FY2025: NI −$129,072,000 vs OCF $150,191,000, SBC $493,940,000, plus a +$754,945,000 ΔNWC drag. FY2026: NI −$71,151,000 vs OCF $505,148,000, SBC $550,454,000 (all financials_history.csv). SBC is non-cash in the OCF statement but a real cost here — which is why the conservative OE deducts it and the base was negative until the TTM window.
- **LOW_OE_YIELD** (0.32%): real and decisive — at $365.55 the valuation rests almost entirely on future growth and margin expansion, not on any current owner's-earnings stream. The tier is fragile by construction.
- **WIDE_SCENARIO_SPREAD** (4.38x): real. Confidence is capped at low (also for the knife-edge TTM base), and the verdict is sized to the conservative end.

## My thoughts / overlay
- The honest headline is the method range: **F on the normalized-median and latest-FY bases (both negative OE), D on the TTM base** — and even the TTM-based super-bull case returns 4.18%. Every filing-based owner's-earnings method lands in the same place: the price capitalizes a mature, high-margin future that the OE record has not yet produced a single positive year of.
- Quality of the business is not the debate: revenue +30% in the latest quarter, guidance raised, first GAAP operating profit, 122% net ARR expansion, near-zero capex ($7,603,000 TTM). The debate is purely the $365.55 price against a $1.16 TTM OE/share.
- Watch items that would change the answer: SBC dollars flattening while OCF compounds (the TTM trend is the start of this, not proof of it); Atlas growth re-accelerating on AI workloads; the interim-CEO transition resolving; buybacks appearing to offset dilution (none in the filed history — the count only grows).
- Margin of safety: the price that clears 15% on the weighted path is the weighted IV@15% itself, **$20.12** (upside at 15% from the current price: −94.5%, per key_numbers.md), and even the super-bull IV@15% is only $37.96. There is no margin-of-safety framing that makes $365.55 work on owner's earnings; a buyer here is underwriting the revenue story, not the OE story.

## Final verdict
- **Final tier: D** (weighted IRR 3.34% on the TTM base; method range F on normalized/FY bases to D on TTM — the range is documented above, and no point in it approaches the 15% hurdle)
- Confidence: **Low** (WIDE_SCENARIO_SPREAD present; TTM base is a six-month inflection with SBC still consuming most of OCF)
- One-liner: Excellent growth franchise, moat 5/10, but owner's earnings turned positive only in the TTM window ($1.16/sh) against a $365.55 price — weighted IRR 3.3%, IV@15% $20.12; clears 15% only near ~$20.
