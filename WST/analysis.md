# WST — West Pharmaceutical Services, Inc.
v5 run, 2026-10-15. In scope (market cap $27.24B at $374.65, nasdaq_quote_api).

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.py output, or financials_history.csv — none are recomputed.

## What it is
Maker of packaging, containment and delivery components for injectable drugs: elastomer stoppers/closures, syringe and cartridge components, vial seals, and delivery devices (Proprietary Products, plus a lower-value Contract Manufactured Products segment). Its components are designed into customers' drugs and are frequently spec'd into the drug's FDA filing, so demand rides injectable biologics and GLP-1 volumes rather than drug prices. Q2 2026 printed revenue of $872.3M, +13.8% year over year, with adjusted EPS of $2.37 (+29%); management raised FY2026 guidance to revenue of $3.345–3.380B (10–11% organic growth) and adjusted EPS of $8.85–9.05. High-Value Products are the engine — HVP components ran ~49% of revenue in Q2 with +18% organic growth, biologics +29%, driven in part by GLP-1 elastomers.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** revenue $3,074.1M; operating cash flow $754.8M; capex $285.9M; SBC $23.8M (always a real cost, and small here).
- **Conservative owner's earnings FY2025: $445.1M = $6.12/share** (latest FY OE/share, key_numbers.md)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $464.8M — close to the conservative figure, which raises confidence in the OE level. Net income FY2025 was $493.7M.
- OE positive 5 of the last 5 fiscal years. Balance sheet is a strength: net debt is **−$588.5M (net cash)** per dcf_numbers.json (diagnostics: net debt −1.44x normalized OE).
- OE history is capex-cycle noisy, not demand noisy: conservative OE totals ran $391.2M (FY2023) → $257.7M (FY2024) → $445.1M (FY2025) as capex peaked at $362.0M / $377.0M in FY2023–24 for capacity expansion and then fell to $285.9M. That is why the 3-yr median base ($5.20/share) sits well below the latest FY ($6.12/share).

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $754.8M − prior YTD $306.5M + current YTD $213.9M = **TTM $662.2M**
- Capex: FY $285.9M − prior YTD $146.5M + current YTD $85.9M = **TTM $225.3M**
- SBC: FY $23.8M − prior YTD $8.7M + current YTD $17.5M = **TTM $32.6M**
- Shares (current-YTD weighted diluted): **71.9M**
- **TTM OE total $404.3M → base OE/share $5.62** (base_source: ttm_json)
- The TTM base was chosen over both alternatives: the 3-yr median ($5.20) is dragged by the FY2024 capex peak, and the latest FY ($6.12) ignores the softer H1 2026 cash generation (Q2 operating cash flow was only $124M per the earnings summary — West's OCF is H2-weighted). TTM sits between them and uses the freshest filed legs; capex continuing to fall from its peak is a real TTM tailwind already in this base.

## Moat: 7/10 — strong
Justification: components spec'd into FDA drug filings create regulatory lock-in that is expensive and risky for a drug maker to change mid-product-life; scale and materials-science know-how (e.g. the Daikyo FluroTec barrier-film partnership) are hard to replicate; West is the dominant elastomer supplier into GLP-1 pens. Held below 8 because the moat protects share, not volume — customers (notably Lilly and Novo) and drug-modality shifts (oral GLP-1) sit outside it, and credible scaled rivals exist.
- FOR: Regulatory lock-in — components spec'd into FDA filings; requalifying a new supplier risks the drug's approval and supply
- FOR: Near-dominant position in elastomer components for GLP-1 injectable pens (Lilly / Novo supply relationships)
- FOR: Materials-science and quality intangibles (FluroTec via Daikyo) plus efficient scale in a safety-critical niche
- FOR: Proven through-cycle economics — OE positive 5/5 years, net cash balance sheet, mix shifting to High-Value Products (~49% of Q2 revenue)
- AGAINST: Customer concentration at the top of the GLP-1 market (Lilly, Novo set the volumes)
- AGAINST: Modality risk — oral GLP-1 formulations would bypass injectable components entirely
- AGAINST: Real scaled rivals (Datwyler, Gerresheimer, Stevanato, Aptar) expanding capacity into the same GLP-1 demand
- AGAINST: Demand is cyclical at the margin — the 2023–24 destocking flattened revenue (3-yr revenue CAGR only 2.1%) despite the moat
- A 7 gives CAP = 11.1 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 11.1 years, 15-year projection.

## DCF — v5 final run (2026-10-15)
Engine blended growth: revenue CAGR 5y 7.44%, 3y 2.12%, latest YoY 6.25%, OE/share CAGR 2y 8.55% → g_blend 6.85%, plus +1.38pp share-count adjustment (share count shrinking ~1.38%/yr) = **g_base 8.23%**. Default offsets and multipliers kept; probabilities 10/25/30/25/10.

Sanity check vs actual prints: the base start (8.2%) sits slightly *below* current revenue prints (Q2 +13.8% YoY; FY26 guided 10–11% organic) — deliberately, because OE is not adjusted EPS: TTM OE actually fell vs FY2025 on H1-weighted OCF seasonality and still-elevated capex, and the guided +21–24% adjusted-EPS growth leans on buybacks and non-GAAP items. The bull start (13.2%) matches the current revenue print, and the super-bull start (20.2%) matches the guided EPS growth rate — the upside cases are not sandbagged. None of it matters to the verdict: even the super-bull cannot clear 10% IRR at this price.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -3.8% | 0.75 | Oral GLP-1 / destocking repeat; OE compresses | $25.78 | 3.25% |
| Bear | 25% | 3.2% | 0.90 | Growth reverts to the flat 2023–24 pattern | $42.95 | 3.95% |
| Base | 30% | 8.2% | 1.00 | Blended historical growth, HVP mix keeps lifting OE | $60.47 | 4.70% |
| Bull | 25% | 13.2% | 1.10 | Current revenue momentum holds; capex keeps normalizing | $84.36 | 5.73% |
| Super bull | 10% | 20.2% | 1.25 | Guided EPS-grade growth compounds for years | $133.70 | 7.73% |

- **Probability-weighted: IV@15% $65.92 (−82.4% vs price), IV@12% $89.35, IV@10% $115.76, weighted IRR 4.98%, base-case IRR 4.70%**
- **Tier by numbers: D.** Diagnostics (key_numbers.md): OE yield 1.50%, terminal value 20.9% of IV@15%, scenario spread 5.19x, net debt −1.44x normalized OE, 9.5 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.5 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, quoted above.
- **LOW_OE_YIELD** (base OE yield 1.5%): real and decisive — at $374.65 the buyer pays ~67x TTM owner's earnings, so the entire return case rests on growth the scenarios already stretch to credit (super-bull 20.2% start, 1.25x mult, 11.1-yr CAP) and it still returns 7.7%. This flag *is* the verdict.
- **WIDE_SCENARIO_SPREAD** (5.19x): real — outcomes range from destocking-repeat to a GLP-1 supercycle. Confidence is capped at medium, and the verdict is sized to the conservative end; note the spread here is between bad and merely poor, not bad and good.

## My thoughts / overlay
- This is a quality/price mismatch, not a quality debate. The business clears every quality test the sweep applies — regulatory lock-in moat, 5/5 positive OE years, net cash, falling capex, small SBC — and fails the only test that sets the tier: at $374.65 there is no defensible OE path to a 15% return. The method range is unusually honest here: median base, TTM base, and latest-FY base all land in Tier D, and the super-bull case on the most generous base still yields single digits.
- Balance sheet folded into the verdict explicitly: net cash of $588.5M (dcf_numbers.json) removes financial risk from the bear cases — the super-bear is a growth disappointment, not a solvency story — but $588.5M of net cash against a $27.24B market cap cannot rescue the valuation math.
- Watch items that could change the inputs, not the conclusion at this price: oral GLP-1 readouts (modality risk to the whole injectable chain), the CGM contract exit / SmartDose transition, tariff exposure on a global plant footprint, and whether H1 OCF seasonality or a real slowdown explains the soft TTM OCF leg (Q3 prints Oct 22).
- Price that clears the hurdle: the weighted IV@15% is **$65.92** — the stock would need to fall ~82% to clear 15% on these inputs; even the super-bull IV@15% ($133.70) is ~64% below the current price. There is no margin-of-safety framing that makes $374.65 work on owner's earnings.

## Final verdict
- **Final tier: D** (weighted IRR 4.98%; no tier override — the numbers and the story agree)
- Confidence: **Medium** (capped by WIDE_SCENARIO_SPREAD; high on the direction — the gap to the hurdle is far wider than any input uncertainty)
- One-liner: Excellent business, impossible price — strong 7/10 regulatory-lock-in moat and net cash, but at $374.65 the weighted IRR is 5.0% (IV@15% $65.92); it would need to fall to ~$66 to clear the 15% hurdle.
