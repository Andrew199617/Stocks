# CDW — CDW Corporation
v5 run, 2026-10-16. Market cap $20.534B at $155.44 (nasdaq_quote_api) — in scope (<$40B).

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.py output, or financials_history.csv — none are recomputed.

## What it is
Multi-brand IT solutions provider / value-added reseller: hardware, software and services sourced from 1,000+ vendor partners, sold to commercial, government, education and healthcare customers via a direct sales force plus eProcurement platform. Q2 2026 net sales were $6.57B, up 10% YoY on AI-infrastructure and modernization demand, but gross margin fell 70bp to 20.1% as mix shifted toward large, lower-margin hardware deals; services grew only 1% in the quarter. CDW closed the Lovelytics acquisition (data/AI consulting, 600+ specialists) on 2026-09-25, pushing the mix toward higher-value services.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** revenue $22,424,100,000; operating cash flow $1,205,200,000; capex $117,100,000; SBC $83,600,000 (always a real cost).
- **Conservative owner's earnings FY2025: $1,004,500,000 = $7.60/share** (key_numbers.md: latest FY OE total $1.004B, latest FY OE/share $7.60).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $1,212,900,000 for FY2025 (financials_history.csv) — above the conservative figure, so the conservative OCF-based series is the binding, cleaner base input.
- OE positive 5 of the last 5 fiscal years. Net debt (latest) $5.011B (key_numbers.md). Revenue is choppy, not compounding: rev CAGR 5y 3.96%, rev CAGR 3y -1.89%, latest rev YoY +6.79%, and OE/share CAGR 2y is -12.59% — revenue growth has not converted into per-share owner's earnings, because mix is shifting to low-margin hardware and working capital absorbs cash on large deals.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $1,205,200,000 − prior YTD $443,100,000 + current YTD $219,700,000 = **TTM $981,800,000**
- Capex: FY $117,100,000 − prior YTD $49,400,000 + current YTD $53,900,000 = **TTM $121,600,000**
- SBC: FY $83,600,000 − prior YTD $44,000,000 + current YTD $50,200,000 = **TTM $89,800,000**
- Shares (current-YTD weighted diluted): **128,400,000**
- **TTM OE total $770,400,000 → base OE/share $6.00** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $8.06/share. The TTM base is used because FY2025 ended 9.5 months ago (STALE_FY) and the TTM window shows the current reality: OCF down vs FY2025 on working-capital absorption from large hardware deals. The median base is retained in the method range below — the verdict does not depend on which base is chosen.

## Moat: 5/10 — moderate / narrow
Justification: Scale leader in a fragmented US IT channel with deep vendor relationships, embedded procurement workflows and a growing services attach, but the core economics are low-margin reselling: vendors and cloud marketplaces can bypass the channel, competition is intense, and pricing/mix power is limited.
- FOR: Scale — leading US IT solutions provider with 1,000+ vendor partners and reach across commercial, government, education and healthcare customers; embedded procurement — eProcurement integration, account teams and lifecycle services create real switching friction; services & solutions attach rising (Lovelytics data/AI acquisition closed Sep 2026 adds 600+ specialists); consistent buybacks shrink the share count ~1.2%/yr, supporting per-share owner's earnings.
- AGAINST: Low-margin reseller economics — mix shift to large hardware deals cut Q2 2026 gross margin 70bp to 20.1%; disintermediation risk — vendors selling direct and hyperscaler cloud marketplaces bypass the channel; intense competition from Insight, SHI, Connection and vendor-direct channels in a fragmented market; dependence on vendor partners, rebate terms and corporate IT spending cycles; levered balance sheet — net debt 6.3x normalized OE on the TTM base (engine diagnostics).
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — v5 final run (2026-10-16)
Scenario sanity check (written reasons): the engine's blended growth is 1.03% → g_base 2.24%. That base start sits below recent *revenue* prints (FY2025 +6.79%, Q2 2026 +10% YoY) on purpose: the model grows owner's earnings, not revenue, and OE/share has actually fallen (CAGR 2y -12.59%; TTM OE/share $6.00 vs latest FY $7.60) as mix shifted to low-margin hardware and working capital absorbed cash. The super-bull start of 14.2% is a 10%-weighted tail that requires a services-mix recovery plus buyback support — and even that tail only returns 10.86% IRR at this price. Default offsets (-12/-5/0/+5/+12pp), default OE multipliers (0.75/0.90/1.00/1.10/1.25) and default probabilities (10/25/30/25/10) were kept. Price $155.44.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -9.8% | 0.75 | IT spending downturn; hardware mix and leverage bite | $22.07 | 3.99% |
| Bear | 25% | -2.8% | 0.90 | Flat-to-down OE; WC absorption persists | $35.54 | 5.19% |
| Base | 30% | 2.2% | 1.00 | Low-single-digit OE growth on the TTM base | $48.67 | 6.40% |
| Bull | 25% | 7.2% | 1.10 | Services mix recovers; AI infrastructure demand holds | $65.88 | 7.97% |
| Super bull | 10% | 14.2% | 1.25 | Services-led re-acceleration plus buybacks | $99.81 | 10.86% |

- **Probability-weighted: IV@15% $52.14 (-66.5% vs price), IV@12% $68.98, IV@10% $87.73, weighted IRR 6.76%, base-case IRR 6.40%**
- **Tier by numbers: D.** Diagnostics (key_numbers.md): OE yield 3.86%, terminal value 18.3% of IV@15%, scenario spread 4.52x, net debt 6.32x normalized OE, 9.5 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.5 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, quoted above. The TTM base ($6.00) is *below* both the latest FY ($7.60) and the median ($8.06), so using it is the conservative choice, not a flattering one.
- **WIDE_SCENARIO_SPREAD** (4.52x): real — it reflects genuine leverage and mix uncertainty. Confidence is capped at medium, and the verdict below is sized to the weighted/conservative end; note that even the super-bull case (10.86% IRR) fails the 15% hurdle, so the spread does not change the tier.
- **HIGH_NET_DEBT** (net debt $5.011B, 6.32x normalized OE per key_numbers.md): folded into the verdict — leverage is why the bear cases are weighted 35% combined and why the low OE yield (3.86%) leaves no cushion: at this price the equity is a levered claim on a low-single-digit-growth cash stream.

## My thoughts / overlay
- Method range: on the preliminary run's median-of-3-FY base ($8.06/share), the same default scenarios gave a weighted IRR of 8.21% and weighted IV@15% of $70.07 — also Tier D. On the TTM base the final run gives 6.76% / $52.14. Both defensible bases land in D; the honest headline is the range 6.8–8.2% weighted IRR, nowhere near the 15% hurdle.
- Quality is not the problem: OE positive 5/5 years, asset-light capex, a real services franchise being built (Lovelytics), and steady buybacks. Valuation is the problem: at $155.44 the market is paying for a growth/mix recovery the filings do not yet show — OE/share has declined for two years while revenue recovered.
- The price that clears 15% on the final (TTM) inputs is the weighted IV@15% itself, $52.14; on the friendlier median base it is $70.07. A buyer wanting 15% with a margin of safety needs a price below even those levels.
- Risks to the short thesis embedded here: a services-mix recovery (implementation work following the AI hardware wave) could lift margins and OCF conversion faster than the fade assumes; CDW guides to outperforming the US IT market by 200–300bp long term, per its Q2 2026 commentary.

## Final verdict
- **Final tier: D** (weighted IRR 6.76% on the TTM base; 8.21% on the median base — D either way)
- Confidence: **Medium** (capped by the wide scenario spread; data is complete, no gaps, no overrides)
- One-liner: Solid scaled IT channel leader, moat 5/10 — does not clear 15% at $155.44 (weighted IRR 6.8%, weighted IV@15% $52.14 on the TTM base); the price would need to fall toward ~$52 for a 15% return on these inputs.
