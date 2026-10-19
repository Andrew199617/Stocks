# WTS — Watts Water Technologies, Inc.
Engine 5.4.0 run, 2026-10-18. All figures below are copied from dcf_numbers.json, ttm.json, financials_history.csv, or fundamentals.json — none are recomputed.

## What it is
Water safety, quality, and flow-control components: backflow preventers, pressure-reducing valves, drainage, hydronic/HVAC controls, and water-quality products, sold through plumbing distribution (Americas / Europe / APMEA segments) into repair-and-replacement, commercial, and new-construction end markets. A newer growth leg is data-center cooling (Cool Vault thermal storage; data-center sales were ~8% of year-to-date sales in Q2 2026 and more than tripled year over year). Price $356.70 (nasdaq_quote_api); market cap ~$11.95B — in scope under $40B.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $402,000,000; capex $45,700,000; SBC $21,200,000 (always a real cost).
- **Conservative owner's earnings FY2025: $335,100,000 = $10.00/share** (base_oe_latest_per_share in dcf_numbers.json)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $262,400,000 — below the conservative figure, driven by the $89,500,000 working-capital build in a growth/acquisition year; the OCF-based conservative figure is the cleaner base series.
- OE positive 5 of the last 5 fiscal years. Net debt −$207,800,000 (net cash, dcf_numbers.json); lease liabilities $91,600,000 on top. Share count essentially flat (33.5M diluted, share CAGR −0.10%/yr) — no buyback tailwind and no dilution problem; SBC is small at ~0.9% of revenue.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $402,000,000 − prior YTD $124,900,000 + current YTD $120,800,000 = **TTM $397,900,000**
- Capex: FY $45,700,000 − prior YTD $19,800,000 + current YTD $22,600,000 = **TTM $48,500,000**
- SBC: FY $21,200,000 − prior YTD $9,500,000 + current YTD $13,500,000 = **TTM $25,200,000**
- Shares (current-YTD weighted diluted): **33,500,000**
- **TTM OE total $324,200,000 → base OE/share $9.68** (base_source: ttm_json)
- The engine's normalized base (median of last 3 FY OE/share) is $9.14/share — close to the TTM figure, so the base choice is not the story here; the latest FY figure is $10.00/share. TTM revenue is $2,677,300,000, +17.1% YoY (fundamentals.json TTM), with TTM OE/share up +8.8% YoY — OE is growing slower than revenue as acquisitions dilute margins and capex steps up.

## Moat: 6/10 — moderate-strong, not wide
Justification: code-approved, spec-driven components with a 150-year brand, distribution depth, and demonstrated pricing power — evidenced by ROIC and margins — but these are components, not lock-in: strong rivals (Zurn Elkay, Aalberts, Pentair, Xylem) contest every category, distributors hold buyer power, and end markets are construction-cyclical.
- FOR: Return on invested capital (roic_proxy, fundamentals.json) of 18.0% / 19.4% / 18.8% in FY2023–25 (22.6% in FY2022) — well above the cost of capital through the cycle; gross margin expanded from 41.5% (FY2020) to 49.5% (FY2025), TTM 48.9%, and operating margin from 12.0% to 18.4%, TTM 19.1% — proven pricing power, including passing through ~$40M of 2025 tariff costs; plumbing-code approvals and spec-in position with contractors/distributors raise entry barriers; large repair-and-replacement installed base smooths the construction cycle; net-cash balance sheet.
- AGAINST: No network effects or hard switching costs — products are specified but substitutable category by category; concentrated distributor buyer power (e.g., Ferguson); commodity brass/copper input exposure and tariff costs; construction cyclicality in residential and nonresidential new build; data-center demand is project-based and lumpy, with hyperscaler concentration; serial acquisitions (Josam, I-CON, EasyWater, Haws, Superior Boiler, Saudi Cast) dilute margins near term (~50bp guided) and add integration risk; European weakness.
- A 6 gives CAP = 9.8 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 9.8 years, 15-year projection.

## DCF — final run (2026-10-18)
Growth sanity check (mandatory): the engine's blended start is 9.28% (rev CAGR 5y 10.08%, 3y 7.20%, latest FY YoY 8.27%, OE/share CAGR 2y 13.32%). Headline revenue prints are much hotter — TTM revenue +17.1%, Q1 2026 +21.4%, Q2 2026 +18.6% (organic +12.2%) — but those are revenue, flattered by acquisitions and price; the series the model grows is OE/share, whose TTM growth is +8.8%, and management's raised FY2026 guidance is 14–17% total / 8–11% organic *revenue* growth. On an OE basis the default starts are therefore defensible: base 9.28% ≈ TTM OE growth; bull 14.28% sits above any sustained OE print and requires the data-center leg to persist — written reason for keeping it as the bull, not the base; super-bull 21.28% has no OE precedent and is priced as a 10% tail. Probabilities 10/25/30/25/10; OE multipliers 0.75/0.90/1.00/1.10/1.25. Price $356.70.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -2.72% | 0.75 | Construction downturn; data-center projects slip; tariff/input squeeze | $47.18 | 4.02% |
| Bear | 25% | 4.28% | 0.90 | Mid-single-digit OE growth; acquisition dilution lingers | $77.30 | 5.27% |
| Base | 30% | 9.28% | 1.00 | TTM OE trajectory decays normally over the CAP | $107.28 | 6.52% |
| Bull | 25% | 14.28% | 1.10 | Data-center cooling becomes a durable second engine | $147.29 | 8.14% |
| Super bull | 10% | 21.28% | 1.25 | Category-killer path in intelligent water + data centers | $227.80 | 11.07% |

- **Probability-weighted: IV@15% $115.83 (−67.5% vs price), IV@12% $156.71, IV@10% $202.69, weighted IRR 6.92%, base-case IRR 6.52%**
- **Tier by numbers: D — and D in the bear and the bull case too (tier_bear D, tier_bull D).** Diagnostics (dcf_numbers.json): OE yield 2.71%, terminal value 20.6% of IV@15%, scenario spread 4.83x, net debt −0.64x normalized OE (net cash), 9.6 months since FY end.
- Hurdle prices: clears 15% only at $115.83, 20% at $79.58, 25% at $59.99 — the $356.70 price is ~3.1x the 15% hurdle price.

## Flags — every fragility flag resolved
- **STALE_FY** (latest fiscal year ended 10 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026 (period end 2026-06-28), legs quoted above.
- **WIDE_SCENARIO_SPREAD** (super-bull IV 4.83x super-bear IV): real — the range is driven by whether data-center/OE growth inflects, which is genuinely uncertain. Confidence is capped at medium per the spec, and the verdict does not depend on resolving it: every scenario, including super-bull at 11.07% IRR, lands in Tier D at this price.

## My thoughts / overlay
- This is a quality/price split, not a quality debate: ROIC ~19%, gross margin ~49% and rising, net cash, 13 straight years of dividend growth (fundamentals.json), and a real data-center growth leg. The problem is purely the entry price — at $356.70 the market is paying for the super-bull path as the base case, and even that path only returns 11.07% in this model.
- Method range: across the defensible bases (median $9.14, TTM $9.68, latest FY $10.00) and the preliminary-to-final runs, weighted IRR spans roughly 6.5–7.5% — Tier D on every variant. The conclusion is method-insensitive, which is why confidence is medium despite the wide scenario spread.
- Risks to the bearish-on-price view: data-center content ($25k–$100k per MW against a ~$2B served market, per Q2 2026 reporting) could compound longer than the fade allows; the Nexa connected-products platform could add recurring revenue the OE history doesn't show yet. Neither is in the filed OE yet.

## Final verdict
- **Final tier: D** (weighted IRR 6.92% on the TTM base; D in bear, base, bull, and super-bull alike)
- Confidence: **Medium** (capped by WIDE_SCENARIO_SPREAD; high on the OE base and balance sheet, low on any single growth path)
- One-liner: High-quality water-components compounder, moat 6/10 — does not clear 15% at $356.70 in any scenario (weighted IRR 6.9%, IV@15% $115.83); it clears 15% only at or below ~$116.
