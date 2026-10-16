# WCC — WESCO International, Inc.
v5 run, 2026-10-16. In scope (market cap $17.127B at $346.01, nasdaq_quote_api).

All figures below are copied from dcf_numbers.json, ttm.py output (ttm.json), or financials_history.csv — none are recomputed.

## What it is
B2B distribution, logistics and supply-chain solutions in ~50 countries, ~700 sites, ~21,000 employees (2025 annual report). Three segments (2025 sales mix from the annual report): Communications & Security Solutions (CSS, ~39% — data-center, enterprise network infrastructure, security), Electrical & Electronic Solutions (EES, ~38% — construction, industrial, OEM), and Utility & Broadband Solutions (UBS, ~23% — utilities, broadband). The 2020 Anixter acquisition is the step-change in the filed history: revenue $8,358.9M (2019) → $12,326.0M (2020) → $18,217.5M (2021), so the 5-yr revenue CAGR of 13.79% mixes pre- and post-Anixter bases and is not a growth run-rate. Current demand is led by AI data centers: Q2 2026 sales $6.67B, +13% YoY (organic +12.6%), data-center sales ~$1.5B in the quarter up ~45% YoY, total backlog up ~60% YoY to a record, and management raised FY2026 guidance to 10–12% reported sales growth with adjusted EPS of $16.00–$17.50 (Q2 2026 earnings reports).

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** revenue $23,510,900,000; net income $640,200,000; operating cash flow $125,000,000; capex $99,800,000 (tag PaymentsToAcquireProductiveAssets); SBC $40,500,000 (tag ShareBasedCompensation); D&A $197,600,000.
- **Conservative owner's earnings FY2025: −$15,300,000 = −$0.31/share** (base_oe_total_latest_fy / base_oe_latest_per_share in dcf_numbers.json).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $120,500,000 for FY2025 — also thin. Both definitions agree the latest year produced almost no owner's earnings despite $640.2M of net income, because working capital absorbed the cash: ΔNWC was +$617,500,000 in FY2025 (financials_history.csv).
- **OE positive in only 2 of the last 5 fiscal years** (oe_positive_years_of_last_5: 2/5). Conservative OE totals: FY2021 −$18,400,000; FY2022 −$134,800,000; FY2023 $352,800,000; FY2024 $977,600,000; FY2025 −$15,300,000. This is the signature of a working-capital-hungry distributor: growth years build inventory/receivables and OCF collapses; the slow year (FY2024, revenue down) released working capital (ΔNWC −$444,900,000) and OCF spiked to $1,101,200,000. Net income, by contrast, was stable at $640–861M across FY2022–25 — the earnings are real, the cash conversion is violently cyclical.
- Net debt $5,781,400,000 (dcf_numbers.json) — see HIGH_NET_DEBT under Flags.

**Base used = the engine's normalized base, median of last 3 FY OE/share = $6.75/share** (base_oe_normalized_per_share $6.7457, base_source: median_of_last_3_fy_oe_per_share). Reason: both single-point alternatives are working-capital snapshots taken during growth spurts — the latest FY (−$0.31) sits inside a $617.5M WC build, and the TTM figure (below) sits inside the H1 2026 build that accompanied +13.4% sales growth. The median is the only one of the three bases that is not a single WC-timing snapshot; it is also generous relative to the 2-of-5 positive-year history, which makes the resulting Tier D verdict conservative-proof: even on the most flattering defensible base, the stock does not clear 10%.

**TTM evidence (ttm.py, filing-direct, quoted from ttm.json; FY end 2025-12-31, YTD end 2026-06-30) — computed, checked, and NOT used as the base, for the reason above:**
- OCF: FY $125,000,000 − prior YTD $135,800,000 + current YTD $275,100,000 = **TTM $264,300,000**
- Capex: FY $99,800,000 − prior YTD $42,200,000 + current YTD $51,600,000 = **TTM $109,200,000**
- SBC: FY $40,500,000 − prior YTD $18,600,000 + current YTD $35,200,000 = **TTM $57,100,000**
- Shares (current-YTD weighted diluted): **49,500,000**
- **TTM OE total $98,000,000 → TTM OE/share $1.98** — positive but far below the median base, confirming H1 2026's double-digit growth again consumed most of the cash earnings. A TTM-based run would land deeper in Tier D; the verdict does not turn on the base choice.

## Moat: 5/10 — moderate/narrow
Justification: real scale and service-embedding advantages in a business whose ~5–6% operating margins and commodity product mix prove pricing power is limited; equally scaled rivals (Graybar, Ferguson, Grainger, Rexel) contest the same national accounts.
- FOR: Distribution scale — ~$23.5B sales, ~700 sites in ~50 countries, millions of SKUs; few rivals can serve a hyperscaler's multi-site build-out nationally.
- FOR: Integrated supply / VMI / project-services embedding (One Wesco cross-selling) raises switching friction beyond spot product sales; backlog up ~60% YoY shows customers committing multi-year programs through Wesco.
- FOR: Data-center solutions position across all three segments (CSS white/gray space, EES power, UBS grid services — including a multi-year Grid Services award from a hyperscale customer in Q2 2026) ties Wesco to the strongest secular capex cycle in its end markets.
- FOR: Supplier breadth and availability — premier-supplier relationships and fill-rate reliability matter more than price in project work.
- AGAINST: Products are largely commoditized (wire, cable, electrical gear) with transparent pricing; gross margin ~21–22% and operating margin ~5–6% through the cycle show no durable pricing power.
- AGAINST: Powerful counterparties on both sides — giant suppliers and hyperscaler/utility customers with procurement leverage.
- AGAINST: Low switching costs on the product-only share of wallet; regional distributors and manufacturer-direct channels constantly contest share.
- AGAINST: The model carries its moat in working capital and debt, not intangibles — growth must be funded with inventory, receivables and a $5,781.4M net-debt stack.
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — v5 final run (2026-10-16)
Growth inputs: engine blended growth 7.76% (components: rev CAGR 5y 13.79% — Anixter-inflated, rev CAGR 3y 3.15%, latest rev YoY 7.76%, OE/share CAGR not computable on negative endpoints), share-count adjustment +1.88pp (share count −1.88%/yr), g_base 9.63%. Default offsets and multipliers kept — no recalibration: the sanity check below supports the default ladder.
**Sanity check vs actual prints:** Q2 2026 sales grew +13% YoY and FY2026 sales are guided +10–12%, so the base OE growth start (9.6%) sits *below* the current sales print — deliberately, and here is the written reason: for Wesco, OE growth is not sales growth. Double-digit sales growth has repeatedly produced negative OE (FY2021, FY2022, FY2025) because the growth itself consumes working capital. Capitalizing 13% OE growth off a base the company only reaches in WC-release years would double-count the cycle. The bull (14.6%) and super-bull (21.6%) starts do exceed the sales print, which is the right shape: they are the scenarios where growth *and* cash conversion happen together. Probabilities 10/25/30/25/10; OE multipliers 0.75/0.90/1.00/1.10/1.25. Price $346.01.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | −2.4% | 0.75 | Data-center capex pauses; WC build meets falling volumes; leverage bites | $33.86 | 3.64% |
| Bear | 25% | 4.6% | 0.90 | Growth normalizes to GDP-like distribution; OE stays conversion-poor | $54.40 | 4.51% |
| Base | 30% | 9.6% | 1.00 | Guided growth fades over the CAP; WC conversion stays cyclical-average | $74.33 | 5.38% |
| Bull | 25% | 14.6% | 1.10 | Data-center/grid supercycle sustains; backlog converts with better mix | $100.35 | 6.49% |
| Super bull | 10% | 21.6% | 1.25 | Multi-year infrastructure supercycle with clean cash conversion | $151.34 | 8.56% |

- **Probability-weighted: IV@15% $79.51 (−77.0% vs price), IV@12% $107.12, IV@10% $138.08, weighted IRR 5.63%, base-case IRR 5.38%**
- **Tier by numbers: D.** Diagnostics (dcf_numbers.json): OE yield 1.95%, terminal value 20.1% of IV@15%, scenario spread 4.47x, net debt 17.31x normalized OE, 9.49 months since FY end.
- Note the ceiling: even the *super-bull alone* — 21.6% growth start, OE ×1.25 — yields only an 8.56% IRR at $346.01. There is no scenario in the ladder, let alone a weighted one, where today's price clears even 10%.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.49 months ago): resolved by evidence, not by pin — ttm.py was run and its inputs are quoted in full above (TTM OE/share $1.98 through Q2 2026). No TTM pin was applied because the TTM window is itself a WC-build snapshot (see BASE_DIVERGENCE); the median base stands, and the TTM figure is reported so the reader can see the pin would only deepen the D.
- **BASE_DIVERGENCE** (latest FY −$0.31 vs 3-yr median $6.75): the latest FY is the distorted one — FY2025 net income was $640,200,000 but ΔNWC absorbed +$617,500,000 as sales grew 7.8% into a record backlog, leaving OCF of $125,000,000 and OE of −$15,300,000. The TTM ($1.98) is distorted the same way (H1 2026 sales +13.4%). The median ($6.75) is the least-distorted base and, given the 2-of-5 positive-year history, if anything flatters the company — kept deliberately so the D verdict cannot be dismissed as a base-choice artifact.
- **NI_OCF_DIVERGENCE** (2023, 2025): working capital, not tax deposits or impairments. FY2023: net income $765,500,000 vs OCF $493,200,000 with ΔNWC +$428,100,000. FY2025: net income $640,200,000 vs OCF $125,000,000 with ΔNWC +$617,500,000 (all financials_history.csv). The OCF-based conservative OE is the series used throughout, so the divergence is the phenomenon being measured, not a data error — but it is exactly why no single year can be trusted as the base.
- **LOW_OE_YIELD** (base OE yield 1.95%): real and decisive. At $346.01 the buyer gets under 2% normalized OE yield and must be paid entirely by growth that, in this business, consumes cash as it arrives. This is the core of the verdict.
- **WIDE_SCENARIO_SPREAD** (super-bull IV 4.47x super-bear): real — it reflects genuine OE volatility (2 of 5 years positive). Confidence is set to low, and the verdict needs no sizing adjustment because even the top of the spread fails the hurdle.
- **HIGH_NET_DEBT** (net debt 17.31x normalized OE): net debt $5,781,400,000 against a normalized OE base that vanishes in growth years is the bear-case transmission channel: a demand pause leaves interest and WC commitments against thin OCF. Mitigants, from 2026 reports: the company refinanced in 2026 (new senior notes due 2031/2034, 2028 notes redeemed) and states no significant maturities until 2029, and leverage on adjusted EBITDA is far lower than on OE — but on the owner's-earnings definition this sweep uses, the flag stands and is a reason the bear weights are not lower.

## My thoughts / overlay
- The honest headline is the *range of bases*, and it does not save the stock: latest FY −$0.31 (no DCF supportable), TTM $1.98 (deeper D), median $6.75 (D at 5.63% weighted). Every defensible base lands in D; the median was chosen precisely because it is the most generous of the three.
- The equity story being priced at $346.01 is an earnings story, not an owner's-earnings story: adjusted EPS guided $16.00–$17.50 for 2026, Q2 adjusted EPS $4.57 +35% YoY, backlog +60%, data-center sales +~45%. That story may be true — but Wesco's filed history says reported earnings convert to owner cash only in the years growth pauses (FY2024's $977.6M OE came with falling revenue). Paying a full growth multiple for a distributor whose growth eats its cash flow is the risk the price ignores.
- Balance sheet: $5,781.4M net debt is manageable against ~$23.5B of sales and a termed-out maturity ladder (nothing significant until 2029 per the company), but it removes the margin for error the OE volatility demands.
- Price that clears the hurdle: the weighted IV@15% is $79.51 — at roughly that level the weighted path clears 15%; any margin-of-safety entry sits below it. Today's $346.01 is more than four times that figure (upside_at_15: −77.0%). Even the super-bull IV@15% ($151.34) is less than half the price.

## Final verdict
- **Final tier: D** (weighted IRR 5.63% on the v5 final inputs; no tier override — the numbers tier and the verdict agree, and the verdict survives every defensible base)
- Confidence: **Low** (WIDE_SCENARIO_SPREAD, OE positive in only 2 of 5 years, 17.31x net debt to normalized OE — the direction is certain, the exact depth of D is not)
- One-liner: Real scale distributor riding the data-center cycle, moat 5/10 — but owner's earnings were positive in only 2 of the last 5 years because growth consumes its working capital; at $346.01 it yields a 5.63% weighted IRR with IV@15% of $79.51 and clears the 15% hurdle only at ~$79.51.
