# FTV — Fortive Corporation
v5 / engine 5.4 run, 2026-10-16. Price $57.40 (nasdaq_quote_api), market cap $19.206B — in scope under $40B.

All figures below are copied from dcf_numbers.json, ttm.json, financials_history.csv, or fundamentals.json — none are recomputed.

## What it is
Industrial-technology compounder spun out of Danaher in 2016, now two continuing segments after the June 28, 2025 tax-free separation of Precision Technologies as Ralliant Corporation (discontinued operations; 1 RAL share per 3 FTV shares): **Intelligent Operating Solutions** — Fluke electrical test, Accruent, Gordian, ServiceChannel, Industrial Scientific, Intelex facility/asset and worker-safety software and instruments; **Advanced Healthcare Solutions** — ASP sterilization, Provation clinical workflow software, Censis, Fluke Biomedical, Landauer. Roughly 50% recurring revenue (software, services, consumables). HQ Everett, WA; ~10,000 employees.

## Owner's earnings
**FY2025 (10-K, continuing operations):** operating cash flow $1,083,200,000; capex $105,100,000; SBC $116,800,000 (always a real cost).
- **Conservative owner's earnings FY2025: $861,300,000 = $2.5741/share** (latest FY OE/share in dcf_numbers.json).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC, financials_history.csv): $1,468,700,000 — materially higher only because ΔNWC was −$557,000,000 in the separation year (working-capital / balance-sheet moves around the Ralliant distribution). The OCF-based conservative figure is the cleaner one and is what the engine uses.
- OE positive 5 of the last 5 fiscal years. Normalized (3-yr median) base is $3.3197/share (FY23 $3.3197, FY24 $3.8282, FY25 $2.5741) — it overstates the post-spin run rate: FY25 OCF fell to $1,083.2M from $1,526.8M and the TTM print stayed soft, so the median was not used as the base.
- Net debt $2,830,500,000 (total debt $3,206,000,000 = $899,500,000 current + $2,306,500,000 noncurrent, less cash $375,500,000); lease liabilities $100,600,000; equity $6,453,400,000 post-distribution (was $10,188,600,000 at FY24).

**Base used = TTM owner's earnings through Q1 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $1,083,200,000 − prior YTD $241,700,000 + current YTD $234,800,000 = **TTM $1,076,300,000**
- Capex: FY $105,100,000 − prior YTD $21,100,000 + current YTD $26,600,000 = **TTM $110,600,000**
- SBC: FY $116,800,000 − prior YTD $23,400,000 + current YTD $21,300,000 = **TTM $114,700,000**
- Shares (current-YTD weighted diluted): **312,800,000**
- **TTM OE total $851,000,000 → base OE/share $2.7206** (base_source: ttm_json)
- TTM stops at the quarter ended 2026-04-03 because the Q2 2026 10-Q (period ended 2026-07-03, filed 2026-07-29) is not yet in EDGAR companyfacts (fundamentals.json warning). Q2 prints were therefore used only for the growth sanity check, not the base: Q2 2026 revenue $1.10B, +7.9% reported / +6.7% core, adjusted EPS $0.74, and full-year guidance raised to ~4% core revenue growth with adjusted EPS $2.95–$3.05.

## Moat: 5/10 — moderate / narrow
Justification: Leading niche brands (Fluke, ASP, Provation) with installed-base consumables, service and workflow-software switching costs and ~50% recurring revenue, but measured returns on capital have stayed below a normal cost of capital through the cycle and organic growth is low-single-digit.
- FOR: Fluke's dominant position in electrical test and calibration with an installed base pulling service/consumables; ASP sterilization and Provation/Censis workflow software embedded in hospital processes (switching costs, regulatory lock-in); ~50% recurring revenue from software, services and consumables; gross margin 63.50% in FY2025 (64.18% FY24, 63.29% FY23) showing pricing power in the continuing portfolio; Fortive Business System operating discipline.
- AGAINST: ROIC proxy (fundamentals.json) was only 5.82% / 6.98% / 4.48% / 5.22% / 6.86% in FY21–FY25 — below cost of capital, weighed down by acquisition goodwill/intangibles; a 7+ moat is not supported on this record. Continuing revenue grew only +1.9% in FY2025 and is guided to ~4% core in 2026; hardware/instrument demand is cyclical and exposed to tariffs, healthcare policy and government spending; gross-margin pressure from product mix and tariffs flagged through 2026.
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — final run (2026-10-16)
Growth recalibration (written reason): the engine's blended start is −3.90%, but its components straddle the Ralliant basis break — rev CAGR 3y −10.62% and 5y −2.14% compare pre-spin totals with restated continuing operations, and OE/share CAGR 2y is −11.94%. Continuing-operations prints are positive: FY2025 revenue +1.92% YoY, Q1 2026 core growth ~5%, Q2 2026 core +6.7%, FY2026 core guidance raised to ~4%. Scenario starts were therefore set via offsets (−0.001 / +0.039 / +0.079 / +0.109 / +0.139 vs g_base −3.90%) to −4 / 0 / **+4** / +7 / +10%. The bull start (+7%) sits right at the Q2 core print (+6.7%) rather than below it; super bull (+10%) requires sustained re-acceleration plus the buyback pace continuing. Probabilities 10/25/30/25/10; OE multipliers 0.75/0.90/1.00/1.10/1.25 (defaults, appropriate for a stable recurring-revenue mix). Price $57.40.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -4.0% | 0.75 | Industrial/healthcare downturn, tariff margin hit, leverage bites | $12.75 | 5.08% |
| Bear | 25% | 0.0% | 0.90 | Flat core growth, no margin expansion | $18.09 | 6.35% |
| Base | 30% | 4.0% | 1.00 | Guidance-level core growth decays over the CAP | $23.74 | 7.73% |
| Bull | 25% | 7.0% | 1.10 | Q2 core pace holds, software mix and buybacks compound | $29.58 | 9.10% |
| Super bull | 10% | 10.0% | 1.25 | Durable re-acceleration to double-digit OE/share growth | $38.04 | 11.00% |

- **Probability-weighted: IV@15% $24.12 (−58.0% vs price), IV@12% $31.91, weighted IRR 7.83%, base-case IRR 7.73%**
- **Tier by numbers: D** (bear D, bull D — no tier band). Diagnostics (dcf_numbers.json): OE yield 4.74%, terminal value 18.3% of IV@15%, scenario spread 2.98x, net debt 3.1x normalized OE, 9.5 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.5 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q1 2026 (quarter ended 2026-04-03), quoted above. The Q2 2026 10-Q is filed but not yet in EDGAR companyfacts (fundamentals.json warning), so no filing-direct Q2 TTM exists yet; Q2 reported prints were used for growth only.
- **NI_OCF_DIVERGENCE** (NI vs OCF differ >40% in 2024, 2025): explained by non-cash charges, not a one-off tax deposit. FY2024: NI $832,900,000 vs OCF $1,526,800,000 — D&A $430,900,000 plus SBC $90,100,000 bridges most of the gap. FY2025: NI $579,200,000 vs OCF $1,083,200,000 — D&A $437,600,000 plus SBC $116,800,000 more than bridges it, with FY25 NI also depressed in the Ralliant separation year. The OCF-based conservative OE used throughout is not contaminated by these non-cash items.
- **BUYBACK_TAILWIND** (share count shrinking 2.5%/yr): already credited via the growth adjustment in the engine blend; not double-counted. Note the recent pace is far faster than the long-run rate — buybacks were $1,907,700,000 TTM (fundamentals.json) and shares outstanding were 304,861,021 at 2026-04-24 — but that post-spin pace (funded around the separation) is not assumed to persist in the scenario starts.
- **HIGH_NET_DEBT** (net debt 3.1x normalized OE): balance sheet stated above from the filing — total debt $3,206,000,000, cash $375,500,000, net debt $2,830,500,000, leases $100,600,000. Leverage is real but does not change the verdict: bear cases are stressed at 0.75x/0.90x OE and even the super bull IRR is only 11.00%.
- **Basis break (not engine-flagged, resolved here):** the June 28, 2025 Ralliant separation restated the annual history to continuing operations from FY2023 (fundamentals.json warns the Q4 2023 derivation breaks on the restatement); pre-2023 totals include Precision Technologies. Growth inputs were set from continuing-operations prints and guidance, not the mixed-base CAGRs.

## My thoughts / overlay
- Method range: on the preliminary run (median base $3.3197/share, engine blend growth) the weighted IRR was 7.27% with IV@15% $22.61; on the final TTM base with recalibrated continuing-ops growth it is 7.83% / $24.12. Both are Tier D — the verdict is not assumption-sensitive at this price. Even the super bull case (10% growth start, 1.25x OE) yields only an 11.00% IRR and a $38.04 IV@15%, well under the $57.40 price.
- The quality debate is real but secondary: 63–64% gross margins and ~50% recurring revenue are attractive, yet ROIC proxy has printed 4.48–6.98% for five straight years — the market is paying a compounder multiple for a business whose measured capital returns have not covered its cost of capital.
- Capital return is the bull's best friend and is already visible: ~$1.9B of TTM buybacks retired roughly a tenth of the share count around the spin. If that pace persisted, OE/share growth would beat the revenue-led starts used here — it is treated as upside, not base case, because it was separation-funded.
- Hurdle prices (dcf_numbers.json): the stock clears a 15% hurdle only at or below $24.12, 20% at $17.09, 25% at $13.21.

## Final verdict
- **Final tier: D** (weighted IRR 7.83% on the TTM base; bear and bull cases are also D)
- Confidence: **Medium** (flags all resolved and the tier is robust across methods, but the filing-direct TTM stops at Q1 2026 and the post-spin history is short)
- One-liner: Quality niche industrial-tech compounder, moat 5/10 — does not clear 15% at $57.40 (7.8% weighted IRR, IV@15% $24.12); it clears 15% only below ~$24.
