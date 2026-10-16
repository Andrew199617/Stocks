# VRSK — Verisk Analytics, Inc.
v5 run, 2026-10-15. Market cap $26.674B at $190.415 (nasdaq_quote_api) — in scope under $40B.

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.py output, or cited search results — none are recomputed.

## What it is
Data analytics and technology provider almost exclusively to the property & casualty insurance industry: ISO rating and policy forms, catastrophe models, Xactimate claims estimating, anti-fraud and underwriting data. Subscription-heavy — search results put subscription revenue at 83% of total in Q2 2026, growing 8% on an organic constant-currency basis, while transactional revenue fell 4.2% on that measure on quiet weather / low claims volumes. Q2 2026 revenue was $806.3M, up 4.4% YoY (search result), and management reaffirmed FY2026 guidance of $3.19–3.24B consolidated revenue (search result) vs FY2025 revenue of $3,072,700,000 in financials_history.csv.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $1,436,000,000; capex $244,100,000; SBC $54,200,000 (always a real cost); D&A $259,200,000; net income $908,300,000.
- **Conservative owner's earnings FY2025: $1,137,700,000 = $8.12/share** (base_oe_latest_per_share in dcf_numbers.json)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $1,023,300,000 — same ballpark as the conservative figure, which raises confidence in the OE level.
- OE positive 5 of the last 5 fiscal years. Net debt $4,104,200,000 (dcf_numbers.json).

**Base used = TTM owner's earnings from ttm.py (filing-direct, no hand math).** Note ttm.py's latest matched YTD period ends 2026-03-31, so this TTM runs through Q1 2026; Q2 2026 prints from search were used only as a growth sanity check, not as base math.
- OCF: FY $1,436,000,000 − prior YTD $444,700,000 + current YTD $390,400,000 = **TTM $1,381,700,000**
- Capex: FY $244,100,000 − prior YTD $53,700,000 + current YTD $64,000,000 = **TTM $254,400,000**
- SBC: FY $54,200,000 − prior YTD $15,600,000 + current YTD $18,400,000 = **TTM $57,000,000**
- Shares (current-YTD weighted diluted): **135,222,570**
- **TTM OE total $1,070,300,000 → base OE/share $7.92** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $6.11/share — it averages in the depressed 2023 year (see NI_OCF_DIVERGENCE below) and the weaker 2024 OCF year, so it understates the current run-rate; the latest FY figure is $8.12/share. The TTM base ($7.92) sits between the two and is the more current, filing-derived figure, so it is used. This choice is generous to the stock vs the median base, and the tier still does not clear the hurdle.

## Moat: 8/10 — strong, bordering wide
Justification: 50+ years of proprietary, industry-contributed P&C data that carriers cannot replicate, embedded workflow tools and regulatory filing infrastructure, proven pricing power on renewals, and ~56%+ adjusted EBITDA margins (search results). Single-industry concentration and the AI-disruption question keep it out of 9-10.
- FOR: Proprietary industry-wide datasets built over decades (statistical and claims records insurers contribute to and cannot rebuild); ISO rating/forms and 2,000+ regulatory filings a year make Verisk part of the industry's compliance plumbing; Xactimate embedded in claims workflows (search results: used by ~80% of US insurers; serves the top 100 US P&C providers); 83% recurring subscription revenue with demonstrated price realization on renewals; asset-light, high-margin model with aggressive buybacks.
- AGAINST: Now a single-industry company (P&C insurance) after divesting its energy and financial-services segments — no diversification if insurer IT/data budgets tighten; AI disruption scrutiny is live (Morgan Stanley cut its target Oct 13, 2026 citing weaker organic growth attracting sharper AI-disruption scrutiny, per search results); transactional revenue is weather/claims-cyclical (−4.2% OCC in Q2 2026); credible adjacent competitors (LexisNexis, CoreLogic, Guidewire) and in-house insurer AI builds; growth has decelerated to mid-single digits.
- An 8 gives CAP = 12.4 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 12.4 years, 15-year projection.

## DCF — v5 final run (2026-10-15)
Growth inputs: engine g_base 11.01% = blended growth 6.89% (components: rev CAGR 5y 6.25%, rev CAGR 3y 7.16%, latest rev YoY 6.63%, OE/share CAGR 2y 24.10%) plus the +4.12pp share-count adjustment. Default offsets −12/−5/0/+5/+12pp, default OE multipliers 0.75/0.90/1.00/1.10/1.25, default probabilities 10/25/30/25/10 were kept — the evidence (steady mid-single-digit revenue growth, recurring base, cyclical transactional tail) does not justify skewing the weights.

**Sanity check vs recent prints (required):** the base start of 11.01% sits above recent revenue prints (latest FY YoY 6.63%; Q2 2026 OCC growth 5.8% per search results; FY2026 guidance range $3.19–3.24B). That is defensible only because the start is an OE/share rate, not a revenue rate: it already includes the +4.12pp buyback tailwind, and the OE/share CAGR 2y component printed 24.10% off the depressed 2023 base. The bull (16.01%) and super-bull (23.01%) starts are above every recent revenue print — they are tail cases (10% and 25% weights on bull/super-bull combined 35%) requiring subscription growth to re-accelerate from its Q2 8% OCC pace, buybacks to keep shrinking the count, and margins to hold; they are not the expectation. The super-bear start (−0.99%) prices an AI/competitive or claims-cycle shock to the transactional book. If anything these starts flatter the result: a revenue-only growth path would push the weighted IRR toward Tier D.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -0.99% | 0.75 | AI/in-house builds bite; transactional slump persists; pricing pushback | $40.99 | 5.02% |
| Bear | 25% | 6.01% | 0.90 | Growth settles at recent revenue prints; no OE/share leverage | $69.59 | 7.28% |
| Base | 30% | 11.01% | 1.00 | Blended growth + buyback tailwind decay normally over the CAP | $99.45 | 9.50% |
| Bull | 25% | 16.01% | 1.10 | Subscription re-accelerates; buyback pace holds; margins expand | $140.98 | 12.23% |
| Super bull | 10% | 23.01% | 1.25 | Category-killer path: data moat monetizes AI for carriers instead of being disrupted by it | $228.86 | 16.88% |

- **Probability-weighted: IV@15% $109.46 (−42.52% vs price), IV@12% $150.75, IV@10% $197.68, weighted IRR 10.25%, base-case IRR 9.50%**
- **Tier by numbers: C.** Diagnostics (dcf_numbers.json): OE yield 4.16%, terminal value 22.82% of IV@15%, scenario spread 5.58x, net debt 3.70x normalized OE, 9.46 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.46 months ago): resolved by construction — the base is the TTM figure from ttm.py quoted above (through Q1 2026, the latest YTD period ttm.py matched). Q2 2026 search prints (revenue $806.3M, +4.4% YoY) show no inflection that would invalidate that base.
- **BUYBACK_TAILWIND** (share count shrinking 4.12%/yr): already credited via the +4.12pp growth adjustment in g_base; not double-counted in the verdict. It is also the main reason the OE/share base holds up while TTM OCF dollars fell vs FY2025.
- **NI_OCF_DIVERGENCE** (2023, >40%): explained from the FY2023 cash-flow statement (search result, GlobeNewswire FY2023 release): FY2023 net income was $614.6M vs OCF $1,060.7M, with the gap carried by non-cash items — depreciation & amortization of fixed assets $206.8M plus intangible amortization $74.6M, a $131.1M loss on sale of assets (divestiture-era, non-operating; $128.4M of it in Q1 2023 alone), SBC $54.0M and deferred taxes $52.7M. Net income was depressed, cash was not. The OCF-based conservative OE series used throughout is not contaminated by it; its only residue is the low 2023 OE year inside the 3-yr median, which is one reason the TTM base was preferred.
- **WIDE_SCENARIO_SPREAD** (5.58x): real — the AI-disruption question makes the outcome range genuinely wide. Confidence is capped at medium, and the verdict is sized to the conservative end.
- **HIGH_NET_DEBT** (net debt 3.70x normalized OE in the final run's diagnostics; $4,104,200,000): leverage is buyback-funded, not operating distress — OCF covers it in the base case — but it is folded into the verdict: in the bear/super-bear cases levered OE per share compresses fast, which is why no tier above the numbers was considered despite the moat.

## My thoughts / overlay
- Quality is not the debate: this is one of the strongest data moats in the sweep universe, with 83% recurring revenue and OE positive 5/5 years. The debate is purely price: even on the generous TTM base, with an 11.01% OE/share growth start and a 12.4-year CAP from the 8/10 moat, the weighted IV@15% is $109.46 against a $190.415 price. Even the bull case IV@15% ($140.98) sits below the price; only the 10%-weight super bull clears it.
- Method range: on the engine's median base ($6.11/share) the preliminary run printed weighted IRR 7.86% / Tier D; on the TTM base the final is 10.25% / Tier C. Defensible inputs span D to C — neither clears 15%.
- Hurdle math: the price that clears 15% on the weighted case is the weighted IV@15% itself, $109.46; a margin of safety against the bear cases ($69.59) argues for a materially lower entry than that.
- Risks to the short/avoid side: a buyback pace even faster than the credited tailwind, or subscription growth re-accelerating toward double digits, would lift OE/share faster than modeled — the super-bull case shows how much ($228.86) — but at 10% weight it does not rescue the weighted verdict at this price.

## Final verdict
- **Final tier: C** (weighted IRR 10.25% on the v5 final inputs; method range D to C across defensible bases)
- Confidence: **Medium** (capped by WIDE_SCENARIO_SPREAD; high on OE quality and the filing-derived TTM base, low on any single growth path)
- One-liner: Elite insurance-data franchise, moat 8/10, but priced for perfection — weighted IRR 10.3% (IV@15 $109.46 vs $190.42) clears Andrew's 15% hurdle only below ~$109.
