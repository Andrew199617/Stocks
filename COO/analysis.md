# COO — The Cooper Companies, Inc.
Pass-1 run, 2026-10-19 (engine release 5.4.0). Price $57.38 (nasdaq_quote_api), market cap $11.477B — in scope under $40B.

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.json, or fundamentals.json — none are recomputed.

## What it is
Global medical-device company with two segments: CooperVision — one of the four major contact-lens makers (MyDay daily silicone hydrogel, toric/multifocal, MiSight myopia-control), and CooperSurgical — fertility (genomics, lab platforms) plus office/surgical devices including the Paragard IUD. Fiscal year ends October 31.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $796.1M; capex $362.4M; SBC $70.5M (always a real cost).
- **Conservative owner's earnings FY2025: $363.2M = $1.82/share** (key_numbers.md: latest FY OE/share $1.82; latest FY OE total $363.2M)
- OE positive 5 of the last 5 fiscal years. Net debt $2.393B (key_numbers.md).

**Base used = TTM owner's earnings through Q3 FY2026 (period ended 2026-07-31), from ttm.py (filing-direct, no hand math):**
- OCF: FY $796,100,000 − prior YTD $548,200,000 + current YTD $785,400,000 = **TTM $1,033,300,000**
- Capex: FY $362,400,000 − prior YTD $264,400,000 + current YTD $257,300,000 = **TTM $355,300,000**
- SBC: FY $70,500,000 − prior YTD $55,300,000 + current YTD $50,600,000 = **TTM $65,800,000**
- Shares (current-YTD weighted diluted): **195,200,000**
- **TTM OE total $612,200,000 → base OE/share $3.14** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $1.06/share — rejected as the base; see BASE_DIVERGENCE below. It is retained in key_numbers.md and in the method range.
- **Caveat on the TTM base:** the TTM OCF leg runs through Q3 FY2026 and therefore sits *before* the fertility-litigation cash settlement management guided to for Q4 FY2026 (~$272M of payments excluded from its Q4 free-cash-flow guide of ~$170M, per the Q3 FY2026 reporting). That payment will land in a future OCF print, so the TTM base is, if anything, flattered. This is handled by sizing the verdict to the bear end and putting 45% of probability on bear-or-worse, not by overriding the filing-derived TTM figure.

## Moat: 5/10 — moderate, real but not wide
Justification: prescription/fitter lock-in, premium differentiated lenses (MyDay, MiSight) and a decade of ~66% gross margins, capped at 5 because the ROIC proxy has run only ~3.8–5.1% for six years — the acquisition-heavy balance sheet has not earned its cost of capital — and share is contested in a four-player oligopoly.
- Evidence (fundamentals.json): gross margin 63.1% / 66.9% / 64.7% / 65.6% / 66.6% / 65.5% (FY2020–FY2025), TTM 65.9% — stable through COVID and the FY2026 destocking. ROIC proxy (after-tax operating income over equity + debt − cash): 5.1% / 4.8% / 4.2% / 3.8% / 4.5% / 4.3% over the same years — persistently below a plausible cost of capital, which is why this is a 5 and not a 7+.
- FOR: CooperVision is a global top-tier contact lens maker with prescription/fitter lock-in — wearers rarely switch brands once fitted; MyDay daily silicone hydrogel and MiSight (only FDA-approved myopia-control lens) are differentiated, premium-priced franchises (MiSight grew ~20% organically in Q3 FY2026); gross margin stable at ~65–67% for a decade; CooperSurgical fertility (genomics, lab platforms) holds a strong niche position with recurring services demand.
- AGAINST: ROIC proxy only ~4–5% for six straight years (FY20–25) — the acquisition-heavy balance sheet earns below its cost of capital; contact lenses are a four-player oligopoly (J&J Vision, Alcon, Bausch + Lomb) — share is contested, not locked; legacy hydrogel portfolio shrinking double digits, so growth depends on the MyDay/MiSight mix shift; Paragard faces a new non-hormonal IUD competitor and fertility carries the litigation overhang above.
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — final run (2026-10-19)
Growth recalibration (written reason): the engine's blended growth is 8.96%, but one blend component is an artifact — the 2-yr OE/share CAGR of 53.81% is measured off the depressed FY2023 base ($0.77/share, the capex-peak year). The revenue prints that mean something are far slower: latest FY +5.06%, TTM revenue $4,236.9M vs FY2025 $4,092.4M (+3.5%, fundamentals.json), Q3 FY2026 revenue +1% with CooperVision flat on deliberate U.S. channel destocking, and FY2026 guidance cut to $4.229–4.252B (organic growth guided 0–2% for Q4). Scenario starts were therefore set via offsets (−0.1196 / −0.0896 / −0.0496 / −0.0196 / +0.0104 vs g_base) to −3 / 0 / **4** / 7 / 10%: base sits at the top of the current guide on management's statement that destocking is temporary and underlying consumption is mid-single-digit; bull 7% requires the destocking to end and the FY2027 commercial investments to restore growth; super bull 10% is a return to the FY2023–24 revenue pace and gets only 7%. Probabilities 15/30/30/18/7 — 45% on bear-or-worse, reflecting the guidance cut, the failed CooperSurgical sale process (strategic review closed 2026-09-09 with the unit retained), and the pending litigation cash payment. OE multipliers are the defaults 0.75/0.90/1.00/1.10/1.25. Price $57.38.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | -3.0% | 0.75 | Destocking persists, IUD competitor takes share, litigation payment repeats in OE | $15.33 | 5.65% |
| Bear | 30% | 0.0% | 0.90 | Flat revenue — Q3 FY26 run-rate sticks | $20.86 | 6.95% |
| Base | 30% | 4.0% | 1.00 | Guide-level growth; destocking ends during FY27 | $27.38 | 8.52% |
| Bull | 18% | 7.0% | 1.10 | FY27 recovery lands; fertility strength carries | $34.10 | 10.08% |
| Super bull | 7% | 10.0% | 1.25 | Return to FY23–24 growth pace | $43.86 | 12.22% |

- **Probability-weighted: IV@15% $25.98 (−54.7% vs price), IV@12% $34.29, IV@10% $43.55, weighted IRR 8.21%, base-case IRR 8.52%**
- **Tier by numbers: D.** Bear→bull band: D (6.95%) → C (10.08%). Diagnostics (key_numbers.md): OE yield 5.47%, terminal value 18.1% of IV@15%, scenario spread 2.86x, net debt 3.81x normalized OE, 11.6 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (latest FY ended 11.6 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q3 FY2026 (period ended 2026-07-31), legs quoted above.
- **BASE_DIVERGENCE** (latest FY OE/share $1.82 vs 3-yr median $1.06): the median is the distorted one. The median year (FY2024, $1.06) and FY2023 ($0.77) carry the manufacturing-capex peak ($421.2M and $392.5M in financials_history.csv, vs $355.3M TTM) on softer OCF; FY2025 and the TTM reflect capex normalizing and record free cash flow (Q3 FY2026 FCF $273.0M was a quarterly record, per the Q3 release). TTM base used; the median-base run is kept in the method range below.
- **NI_OCF_DIVERGENCE** (net income vs OCF differ by >40% in FY2025): D&A-explained, not a one-off that contaminates the base. FY2025 net income $374.9M vs OCF $796.1M is a $421.2M gap; D&A alone is $377.4M and SBC $70.5M (financials_history.csv) — non-cash charges cover the gap, with working capital a small drag. The OCF-based conservative OE is unaffected.
- **OE_VOLATILE** (OE/share spans >3x over 5 years): partly a basis artifact, partly real. The span runs from FY2021's $9.65/share — filed on the pre-split share count (~49.8M shares, before the 4-for-1 split effective February 2024) — to the FY2023 trough of $0.77 on the post-split count (~199.3M). On a consistent post-split basis the real swing is the FY2023 capex-peak trough to the $3.14 TTM. Handled by the TTM base plus 45% probability on bear-or-worse.
- **HIGH_NET_DEBT** (net debt 3.81x normalized OE): balance sheet from the latest filed row (FY2025, financials_history.csv): debt current $47.8M + long-term debt $2,455.7M − cash $110.6M = net debt $2,392.9M, plus lease liabilities $278.3M not in the net-debt figure. Leverage is manageable against $612.2M of TTM OE but leaves no cushion if the bear case lands — one more reason the verdict sizes to the bear end. Management is directing cash to buybacks ($339.1M repurchased in Q3 FY2026) rather than deleveraging.
- **TIER_BAND** (bear tier D at 6.95% vs bull tier C at 10.08%): verdict sized to the bear end — final tier D.
- Preliminary-run flags **LOW_OE_YIELD** (1.8%) and **WIDE_SCENARIO_SPREAD** (4.5x) fired only on the rejected median base; on the final TTM base the OE yield is 5.47% and the spread 2.86x, and neither flag fires.

## My thoughts / overlay
- The honest headline is that the tier does not depend on the contested base choice: the preliminary median-base run gave weighted IRR 5.37% and IV@15% $12.19 (Tier D); the final TTM-base run gives 8.21% and $25.98 (Tier D). The method range is D to D — what changes is only how far below the price the value sits. Even the super-bull IV@15% ($43.86) is below the $57.38 price.
- The market is pricing a FY2027 recovery (post-destocking reacceleration, fertility growth, buybacks at a depressed price) that this owner's-earnings model cannot underwrite at current OE: at a $3.14 TTM base the stock needs sustained high-single-digit OE growth for 15% — the company's own current guide is ~3.5% revenue growth with EPS guided down.
- Quality is middling, not poor: 5/5 OE-positive years, ~66% gross margins, real lock-in in lenses. The problem is purely price vs cash flow, compounded by a balance sheet earning ~4% ROIC proxy on a goodwill-heavy asset base.
- Watch items: whether Q4 FY2026 OCF confirms the ~$272M litigation payment as one-time; whether CooperVision organic growth reaccelerates in FY2027 as management guides; the new non-hormonal IUD entrant against Paragard.

## Final verdict
- **Final tier: D** (weighted IRR 8.21% on the final TTM-base inputs; bear end of the D–C band; method range D–D across the median and TTM bases)
- Confidence: **Medium** (TTM base is filing-direct and both bases agree on the tier; growth path and the litigation-payment timing keep it from high)
- Hurdle-clearing prices (weighted path): 15% at $25.98 · 20% at $18.47 · 25% at $14.31
- One-liner: Solid med-device franchise, moat 5/10, but priced for a recovery the model can't see: weighted IRR 8.2% and IV@15% $25.98 vs $57.39 price — clears 15% only below ~$26.
