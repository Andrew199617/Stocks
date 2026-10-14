# ON — ON Semiconductor Corporation (onsemi)
v5 run, 2026-10-14. In scope: market cap $29.691B at $72.10 (nasdaq_quote_api). All figures below are copied from dcf_numbers.json, ttm.py output (ttm.json), or financials_history.csv — none are recomputed.

## What it is
Power and sensing semiconductors for automotive, industrial, and increasingly AI data centers: silicon carbide (SiC) and IGBT power devices, intelligent power modules, and automotive image sensors. Fab-heavy and deeply cyclical — revenue fell from $8,326.2M in FY2022 to $5,995.4M in FY2025 through the auto/industrial inventory correction, and the company is now in early recovery (Q2 2026 revenue $1,603.5M, +9.2% YoY per the earnings release; Q3 2026 guided to $1,650–1,750M). At its September 16, 2026 analyst day, management raised the long-term target to 12–14% annual revenue growth through 2030 ($11.0B revenue by 2030, 53% gross-margin target) — and the stock fell ~9% that day on skepticism, which is the right prior for those targets.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** revenue $5,995.4M; net income $121.0M; operating cash flow $1,759.8M; capex $341.2M; SBC $144.3M (always a real cost).
- **Conservative owner's earnings FY2025: $1,274.3M = $3.09/share** (latest FY OE/share, key figure from dcf_numbers.json).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $803.9M — below the conservative figure because FY2025 net income carries the non-cash impairment load (see NI_OCF_DIVERGENCE below); the OCF-based conservative figure is the cleaner one here.
- OE positive 5 of the last 5 fiscal years, but violently cyclical: FY2023 conservative OE was only $317.3M because capex peaked at $1,539.1M during the SiC fab build-out. Net debt $832.9M; buybacks are shrinking the share count 2.8%/yr (448.2M diluted in FY2022 → 411.8M in FY2025), with a $6B authorization for 2026–2028 per the FY2025 10-K coverage.

**Base used = TTM owner's earnings through Q2 2026 (period ended 2026-07-03), from ttm.py — filing-direct, no hand math:**
- OCF: FY $1,759,800,000 − prior YTD $786,600,000 + current YTD $698,800,000 = **TTM $1,672,000,000**
- Capex: FY $341,200,000 − prior YTD $225,800,000 + current YTD $56,200,000 = **TTM $171,600,000**
- SBC: FY $144,300,000 − prior YTD $68,300,000 + current YTD $74,700,000 = **TTM $150,700,000**
- Shares (current-YTD weighted diluted): **401,500,000**
- **TTM OE total $1,349,700,000 → base OE/share $3.3616** (base_source: ttm_json)
- The engine's normalized base (median of last 3 FY) is $2.4874/share — it is the middle year (FY2024) of a steep capex-normalization path (FY2023 OE/share was crushed by peak fab capex), so it understates the current run-rate; the TTM base is used instead. Caution in the other direction: TTM capex of $171.6M is a trough figure (fab build complete, utilization low), so the TTM base is generous if capex re-accelerates for the 200mm SiC / Czech capacity — that risk is carried in the scenario growth starts and multipliers, not by reverting to the distorted median.

## Moat: 5/10 — moderate, real niches in a commodity-cyclical industry
Justification: genuine leadership positions (SiC, auto image sensing) with long automotive qualification cycles and vertical integration, but semiconductors sell into cyclical end markets with aggressive scaled rivals and Chinese SiC entrants, and FY2023–25 proved onsemi has no pricing power strong enough to hold margins through a downturn — it took $667M of restructuring/impairment charges and cut ~2,400 jobs instead.
- FOR: Vertically integrated SiC chain (boule to module) with roughly 24% global SiC share and the 200mm wafer transition under way; leading automotive image-sensor franchise; long automotive design-win/qualification cycles create real switching friction; $7.1B long-term supply-agreement backlog (FY2025 10-K coverage); AI data-center power revenue ramping (management expects it to more than double in 2026).
- AGAINST: Deeply cyclical — revenue fell from $8,326.2M (FY2022) to $5,995.4M (FY2025) and GAAP profitability collapsed with fab utilization; SiC faces price competition from STMicroelectronics, Infineon, and Chinese entrants; automotive + industrial are ~75% of sales, so two end markets drive everything; roughly 30% of revenue from China (geopolitical/tariff exposure); fab-heavy cost structure means downturns become impairments, not just lower margins.
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — v5 final run (2026-10-14)
Growth recalibration (written reason): the engine's blended growth is −1.06% (g_base), but its components are trough artifacts — revenue 3-yr CAGR −10.37% and latest FY YoY −15.35% measure the correction, while OE/share CAGR 2y of +108.64% is an artifact off the FY2023 capex-peak trough. Current prints say recovery, not decline: Q2 2026 revenue +9.2% YoY, Q3 2026 guided up sequentially, and TTM OE/share ($3.3616) already exceeds every filed FY. Scenario starts were therefore set via offsets (−0.0694 / −0.0094 / +0.0706 / +0.1206 / +0.1706 vs g_base) to −8 / −2 / **+6** / +11 / +16%. Sanity check against prints: the base start (+6%) sits *below* Q2's +9.2% revenue print deliberately — TTM capex is at a trough and will normalize upward as new capacity ramps, dragging OE growth below revenue growth, and management's 12–14% long-term revenue target is an aspiration the market just sold off, not a base case. The super-bull start (+16% OE/share) exceeds the revenue target range only via the buyback tailwind (share count −2.8%/yr, already in the blend) plus utilization-driven margin recovery. Probabilities 10/25/30/25/10; OE multipliers 0.75/0.90/1.00/1.10/1.25 (defaults). Price $72.10.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | −8.0% | 0.75 | Correction resumes; SiC price war; utilization craters again | $13.32 | 4.51% |
| Bear | 25% | −2.0% | 0.90 | Recovery stalls at trough levels; capex normalizes against flat revenue | $20.55 | 5.91% |
| Base | 30% | +6.0% | 1.00 | Modest cyclical recovery; AI power grows, auto/industrial heal slowly | $31.87 | 8.16% |
| Bull | 25% | +11.0% | 1.10 | Recovery compounds; 200mm SiC and AI power deliver | $43.09 | 10.24% |
| Super bull | 10% | +16.0% | 1.25 | Management's 2030 path lands — growth plus margin recovery plus buybacks | $60.07 | 13.13% |

- **Probability-weighted: IV@15% $32.81, IV@12% $43.73, IV@10% $55.92, weighted IRR 8.37%, base-case IRR 8.16%**
- **Tier by numbers: D.** Diagnostics: OE yield 4.66%, terminal value 19.04% of IV@15%, scenario spread 4.51x, net debt 0.60x normalized OE, 9.4 months since FY end.
- Even the super-bull case (13.13% IRR, IV@15% $60.07) does not clear the 15% hurdle at $72.10. The valuation, not the business, is the problem: the price already pays for the recovery.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.4 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, quoted above with all four legs.
- **BUYBACK_TAILWIND** (share count shrinking 2.8%/yr): already credited via the +2.78pp growth adjustment in the blend; not double-counted in the verdict.
- **OE_VOLATILE** (OE/share spans >3x over 5 years): real cyclicality, driven by the capex cycle ($1,539.1M capex in FY2023 vs $171.6M TTM). Handled with the normalized/TTM base choice documented above, default 35% weight on bear-or-worse, and a verdict sized to the conservative end.
- **NI_OCF_DIVERGENCE** (2025): identified — FY2025 net income of $121.0M vs OCF of $1,759.8M. The gap is non-cash restructuring and impairment: the company's own reconciliation shows $608.1M of restructuring, asset impairments and other charges plus $281.5M of restructuring-related inventory charges in FY2025 (equipment impairments ~$496M and a ~$230M sensing inventory write-down per 10-K coverage, ~2,400 terminations). Non-cash charges depress net income without touching OCF, so the OCF-based conservative OE base is not inflated by them; the maintenance definition (built on net income) is the distorted one this year and was not used.
- **WIDE_SCENARIO_SPREAD** (4.51x): real — a cyclical at a recovery inflection has a genuinely wide outcome range. Confidence is capped at medium, and the verdict is sized to the conservative end.

## My thoughts / overlay
- The method range is narrow for once: the preliminary run (median base $2.4874/share, default negative-tilted offsets) gave weighted IRR 5.74% and IV@15% $18.95; this final TTM run gives 8.37% / $32.81. Both are Tier D — the tier is robust to the base choice, which is the finding.
- Quality is not the debate: OE was positive all 5 of the last 5 years including the trough, net debt is only $832.9M, and the buyback is real. The debate is price: at $72.10 the market is paying today for a recovery path close to management's 2030 targets.
- Risks not in the numbers: the planned Synaptics acquisition (announced 2026, terms revised to all-cash per coverage) adds integration and capital-allocation risk on top of the Czech SiC expansion; China revenue exposure ~30%; SiC pricing from Chinese capacity.
- Margin of safety: the weighted IV@15% sits 54.49% below the price (upside_at_15 −54.49%). The price that clears 15% on the weighted case is the weighted IV@15% itself, ~$32.81 — roughly half the current price. There is no margin of safety at $72.10 under any scenario run, including super bull.

## Final verdict
- **Final tier: D** (weighted IRR 8.37% on the v5 final inputs; preliminary median-base run 5.74% — D under both)
- Confidence: **Medium** (high on the filing-derived TTM base and the impairment resolution; the scenario spread is 4.51x, so no higher)
- One-liner: Quality cyclical power/sensing franchise, moat 5/10 — the recovery is real but already paid for: weighted IRR 8.4%, IV@15 $32.81 vs $72.10 price; it clears 15% only near $33.
