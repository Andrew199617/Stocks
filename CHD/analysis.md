# CHD — Church & Dwight Co., Inc.
v5 run, 2026-10-15. Market cap $25.561B at $104.63 (nasdaq_quote_api) — in scope under $40B. Sector: Consumer Staples — household & personal care.

All figures below are copied from dcf_numbers.json, ttm.py output (ttm.json), financials_history.csv, or key_numbers.md — none are recomputed. Research figures from web sources are noted as such.

## What it is
Maker of niche-leading consumer brands: ARM & HAMMER (baking soda, laundry, cat litter), OxiClean, Trojan, TheraBreath, Hero, Waterpik, and Touchland (acquired in 2025). Three segments — Consumer Domestic, Consumer International, and Specialty Products (animal/agriculture). The model is a brand-acquisition compounder: buy #1/#2 brands in slow categories, scale them through its distribution and e-commerce, harvest steady cash. It reshaped the portfolio in 2025, exiting the Flawless, Spinbrush, and Waterpik showerheads businesses and selling the vitamin (VMS) business.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $1,215,400,000; capex $122,400,000; SBC $58,000,000 (always a real cost).
- **Conservative owner's earnings FY2025: $1,035,000,000 = $4.24/share** (base_oe_latest_per_share $4.2366 in dcf_numbers.json)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $1,132,100,000 — same ballpark, which raises confidence. The maintenance figure is flattered by the working-capital swing in the CSV; the OCF-based conservative figure is the cleaner one, and FY2025 net income also carries noncash exit charges (below).
- OE positive 5 of the last 5 fiscal years. Net debt $1,796,100,000 — 1.68x normalized OE (diagnostics), modest for a staples cash generator. Capital allocation in 2025 (per the FY2025 earnings-release cash-flow statement found in research): $900.0M of buybacks and $656.0M of acquisitions (Touchland).

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $1,215,400,000 − prior YTD $416,500,000 + current YTD $461,600,000 = **TTM $1,260,500,000**
- Capex: FY $122,400,000 − prior YTD $39,000,000 + current YTD $61,800,000 = **TTM $145,200,000**
- SBC: FY $58,000,000 − prior YTD $30,200,000 + current YTD $42,600,000 = **TTM $70,400,000**
- Shares (current-YTD weighted diluted): **238,200,000** (down from the FY2025 244,300,000 on buybacks)
- **TTM OE total $1,044,900,000 → base OE/share $4.39** (ttm_oe_per_share $4.3866; base_source: ttm_json)
- The engine's normalized base (3-yr median) is $3.71/share. The TTM base was used per the STALE_FY rule; it is also the more current figure after the 2025 portfolio exits, and the verdict is identical on either base (see Thoughts).

**Recent prints (research, Q2 2026 earnings release / call coverage):** net sales $1,530.0M, +1.6% reported (suppressed by the 2025 business exits) but +5.8% organic — volume +4.3%, price/mix +1.5%; adjusted EPS $0.89; adjusted gross margin 45.4%. Management raised FY2026 guidance: organic sales growth 4–5% (from 3%), adjusted EPS growth 6–8%, operating cash flow ~$1,175M. The company's own framing is that its categories grow at a ~3% weighted-average rate and share gains have historically delivered ~4% organic growth.

## Moat: 6/10 — moderate-strong brand portfolio, not wide
Justification: a portfolio of #1/#2 niche brands with decades of shelf presence and proven pricing, run asset-light — but the categories are low-switching-cost staples where shelf space is rented from powerful retailers, bigger rivals can out-promote, and the VMS episode proved acquired brands can decay.
- FOR: #1/#2 positions in its niches — ARM & HAMMER cat litter at 24.5% share and TheraBreath the #2 mouthwash at 25.3% share (Q2 2026 call, per research); proven pricing power — price/mix +1.5% in Q2 2026 while ARM & HAMMER laundry held share against a heavy P&G/Henkel promotional wave (per research); decades-old brand equity (ARM & HAMMER, Trojan, OxiClean) with national distribution and a growing e-commerce channel; a repeatable acquisition playbook (TheraBreath, Hero, Touchland) that buys niche leaders and scales them internationally; asset-light cash conversion — capex runs ~2% of sales and OE has been positive 5 of the last 5 years.
- AGAINST: near-zero consumer switching costs and private-label exposure in commoditized categories (baking soda, value laundry); retailer power — shelf space and distribution are rented, not owned; larger rivals (P&G, Henkel, Colgate) with deeper promotional and marketing budgets; slow category growth (~3% weighted average, by management's own framing) caps the organic runway; brand durability is not guaranteed — the $357.1M VMS impairment in 2024 and the 2025 business exits show acquired brands can lose relevance; growth depends on continued acquisitions at full prices.
- A 6 gives CAP = 9.8 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 9.8 years, 15-year projection.

## DCF — v5 final run (2026-10-15)
Default probabilities 10/25/30/25/10, default growth offsets −12/−5/0/+5/+12pp vs the engine's g_base of 5.14% (growth blend 4.87% plus the share-count adjustment), default OE multipliers 0.75/0.90/1.00/1.10/1.25 — no recalibration needed. Sanity check against actual prints: the base start of 5.14% sits inside the company's own current evidence (FY2026 organic guide raised to 4–5%, adjusted EPS growth guided 6–8%, Q2 2026 organic +5.8%, 5-yr and 3-yr revenue CAGRs 4.85% and 4.89%). The latest reported revenue YoY of 1.57% understates the underlying business because it includes the exited brands. The bull start (10.14%) is above guidance and is a share-gain-plus-buyback case, not a forecast; the super-bull start (17.14%) approaches the 18.77% OE/share CAGR 2y print, which was flattered by the capex drop from the 2023–24 plant-build years — it is a 10% tail, and even it does not clear the hurdle (below). Price $104.63.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -6.86% | 0.75 | Private label + promo war bite; categories stall | $17.80 | 4.33% |
| Bear | 25% | 0.14% | 0.90 | Category growth ~0; share gains only offset promo pressure | $29.14 | 5.88% |
| Base | 30% | 5.14% | 1.00 | ~4–5% organic + buybacks, per current guidance | $40.45 | 7.45% |
| Bull | 25% | 10.14% | 1.10 | Touchland/Hero/TheraBreath international ramps compound | $55.58 | 9.45% |
| Super bull | 10% | 17.14% | 1.25 | Sustained double-digit OE/share growth — tail case | $86.10 | 13.07% |

- **Probability-weighted: IV@15% $43.71 (−58.23% vs price), IV@12% $58.43, IV@10% $74.90, weighted IRR 7.94%, base-case IRR 7.45%**
- **Tier by numbers: D.** Diagnostics (key_numbers.md): OE yield 4.19%, terminal value 19.4% of IV@15%, scenario spread 4.84x, net debt 1.68x normalized OE, 9.5 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.5 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, quoted above with all four legs.
- **NI_OCF_DIVERGENCE** (2024): identified — FY2024 net income of $585,300,000 was depressed by a $357.1M noncash trade-name and other asset impairment in the vitamins/minerals/supplements (VMS) business, recorded in SG&A ($327.4M Consumer Domestic, $29.7M Consumer International, per the 10-K segment note found in research). Being noncash, it is added back in the cash-flow statement and never touched operating cash flow of $1,156,200,000; the OCF-based conservative OE series used for the base is therefore uncontaminated. (FY2025 has smaller echoes — $45.6M business-exit impairments and a $58.5M loss on sale of the vitamin business — likewise net-income items, not OCF items.)
- **WIDE_SCENARIO_SPREAD** (4.84x): largely mechanical — ±12pp offsets around a ~5% staples growth base produce a wide IV range even though the business itself is stable (OE positive 5/5 years, guidance just raised). Confidence is capped at medium, and the spread does not threaten the verdict's direction: even the super-bull IV@15 of $86.10 sits below the $104.63 price.

## My thoughts / overlay
- The method range is narrow and one-directional: on the preliminary median-base run the weighted IRR was 7.02% with IV@15% $36.40; on the final TTM base it is 7.94% / $43.71. Both are Tier D. More telling, the super-bull scenario alone — 17.14% growth start, 1.25x OE — yields only a 13.07% IRR, below the 15% hurdle. At $104.63 the market is pricing in more than the model's best case.
- Quality is not the debate: this is a durable, asset-light cash compounder with modest net debt (1.68x normalized OE), a falling share count, and freshly raised guidance. The debate is purely price — a 4.19% OE yield on the TTM base cannot compound to 15% at staples growth rates.
- Risks to the (already low) base case: promotional escalation from P&G/Henkel, private-label gains in a weak consumer environment, and acquisition discipline — the VMS write-off is the standing reminder that the playbook sometimes buys decaying brands.
- Price that clears 15%: the weighted IV@15% is $43.71 — the stock would need to trade at or below that level (and lower still for any margin of safety) before it clears Andrew's hurdle on these inputs. That is roughly a 58% decline from $104.63, so this is a watchlist-quality business at an uninvestable price, not a near-miss.

## Final verdict
- **Final tier: D** (weighted IRR 7.94% on the v5 final inputs; Tier D on both the median and TTM bases, and even the super-bull scenario alone is below 15%)
- Confidence: **Medium** (capped by WIDE_SCENARIO_SPREAD; high on OE quality and the TTM base, but the IV range across scenarios is wide)
- One-liner: High-quality staples compounder, moat 6/10 — at $104.63 the weighted IRR is only 7.94% (IV@15 $43.71); it clears 15% only at or below $43.71.
