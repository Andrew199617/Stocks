# CLH — Clean Harbors, Inc.

Pass-1 run, 2026-10-16, engine 5.4.0. All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.json, fundamentals.json or financials_history.csv — none are recomputed.

## What it is
North America's largest hazardous-waste disposal operator: Environmental Services (technical services, field services, Safety-Kleen environmental, emergency response) plus Safety-Kleen Sustainability Solutions (used-oil collection and re-refining). SIC 4955, Hazardous Waste Management. Revenue FY2025 $6,030,837,000. Market cap $17,192,342,960 at $320.06 (nasdaq_quote_api) — in scope under $40B.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $866,725,000; capex $424,918,000; SBC $32,702,000 (always a real cost).
- **Conservative owner's earnings FY2025: $409,105,000 = $7.616/share** (latest FY OE/share).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $371,919,000 — same ballpark, raises confidence in the conservative figure.
- OE positive 5 of the last 5 fiscal years. Net debt $1,949,848,000 on the LongTermDebtNoncurrent+LongTermDebtCurrent basis, plus lease liabilities of $259,534,000 — and see CASH_INCLUDES_RESTRICTED below: that net debt is a floor, not an exact figure.
- Normalized base (median of last 3 FY OE/share) is $5.859/share (FY2023 $5.361, FY2024 $5.859, FY2025 $7.616) — it lags a real step-up in FY2025 OCF, so the TTM base below is used; the median is retained in the reporting.

**Base used = TTM owner's earnings through Q1 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $866,725,000 − prior YTD $1,605,000 + current YTD $6,297,000 = **TTM $871,417,000**
- Capex: FY $424,918,000 − prior YTD $118,695,000 + current YTD $98,443,000 = **TTM $404,666,000**
- SBC: FY $32,702,000 − prior YTD $7,635,000 + current YTD $9,578,000 = **TTM $34,645,000**
- Shares (current-YTD weighted diluted): **52,992,000**
- **TTM OE total $432,106,000 → base OE/share $8.154** (base_source: ttm_json)
- Data lag, stated plainly: the Q2 2026 10-Q (period 2026-06-30, filed 2026-07-29) is not yet in EDGAR companyfacts (fundamentals.json warning), so every filing-direct TTM series stops at 2026-03-31. Q2 2026 prints from the company's reported results — revenue $1.74B, up ~12% YoY; diluted EPS $3.22; Adjusted EBITDA $409.0M — are used only for the growth sanity check below, never in the base math.

## Moat: 6/10 — moderate-strong, permit-bound, not wide
Justification: the permitted hazardous-waste network is close to irreplaceable, but measured returns are only modestly above the cost of capital — ROIC proxy (fundamentals.json) ran 8.2% (2020), 7.3% (2021), 12.6% (2022), 11.2% (2023), 10.8% (2024), 10.6% (2025), and gross margin held a narrow 30.7–32.0% band over the same years (31.3% in FY2025). That is a real franchise earning ~10–12% ROIC, not a 7+ wide moat earning well above its cost of capital through a cycle, so 6 is the honest score.
- FOR: largest North American network of permitted hazardous-waste incinerators, secure landfills and treatment/storage/disposal facilities — new permits are effectively unobtainable, so the footprint cannot be replicated; cradle-to-grave customer liability under environmental law makes switching vendors risky and sticky; regulatory tightening (including PFAS destruction rules) routes non-deferrable demand to permitted capacity; integrated transport + disposal network gives routing/cost advantages and cross-selling across ES and SKSS; proven pricing — incineration utilization and landfill volumes grew while ES margins expanded.
- AGAINST: ROIC proxy only ~10.6–12.6% in recent years and gross margin flat near 31% — pricing power is real but bounded; industrial-cycle exposure — volumes follow manufacturing and project activity; SKSS re-refining economics ride base-oil spreads (its Q2 2026 surge was price-led and can reverse); capital-intensive — capex $404,666,000 TTM against OCF $871,417,000; large rivals (WM, Republic, Veolia) and regional competitors contest field/industrial services where permits matter less; growth partly bought — EnviroServe ($470M) and ES&H ($305M) closed in Oct 2026, funded in part with new 6.250% senior notes due 2034, adding integration and debt-service risk.
- A 6 gives CAP = 9.8 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 9.8 years, 15-year projection.

## DCF — final run (2026-10-16)
Growth recalibration (written reason): the engine's blended start is 10.08%, but its components are flattered — the 5-yr revenue CAGR of 13.92% straddles the 2022 revenue step-up after the 2021 acquisition wave, and the 2-yr OE/share CAGR is 19.18%. The prints that mean something are slower and just re-accelerating: FY2025 revenue +2.39% YoY, TTM revenue +1.9% YoY (fundamentals.json, through Q1 2026), then Q2 2026 revenue up ~12% YoY with full-year 2026 Adjusted EBITDA guidance raised to $1.35–$1.41B. Scenario starts were therefore set via offsets (−0.12 / −0.08 / −0.03 / +0.02 / +0.09 vs the blended start) to −1.92 / 2.08 / **7.08** / 12.08 / 19.08%. Sanity check against prints: bear 2.08% ≈ the FY2025/TTM print; base 7.08% sits between the FY2025 print and the Q2 2026 print, consistent with raised guidance; bull 12.08% ≈ the Q2 2026 print itself; super bull 19.08% is above any revenue print and requires PFAS demand, the Kimball incinerator ramp, the new 10-year disposal contract (commencing Q4 2026) and a full year of the Oct 2026 acquisitions — it is priced as a 10% tail, not a plan; super bear −1.92% is a cyclical downturn case, below recent prints by construction. Probabilities 10/25/30/25/10; OE multipliers 0.75/0.90/1.00/1.10/1.25 (defaults, unadjusted). Price $320.06.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -1.92% | 0.75 | Industrial downturn; SKSS oil spreads reverse; levered OE compresses | $41.19 | 4.00% |
| Bear | 25% | 2.08% | 0.90 | FY2025-pace growth sticks; no guidance delivery | $59.05 | 4.79% |
| Base | 30% | 7.08% | 1.00 | Guidance delivered, then normal fade over the CAP | $81.97 | 5.87% |
| Bull | 25% | 12.08% | 1.10 | Q2 2026 pace holds; PFAS + Kimball + contract ramp | $112.59 | 7.28% |
| Super bull | 10% | 19.08% | 1.25 | Full regulatory/acquisition supercycle | $174.28 | 9.91% |

- **Probability-weighted: IV@15% $89.05 (−72.2% vs price), IV@12% $119.75, IV@10% $154.18, weighted IRR 6.24%, base-case IRR 5.87%**
- **Tier by numbers: D — and bear, base, bull and super bull are all D too.** Diagnostics: OE yield 2.55%, terminal value 20.0% of IV@15%, scenario spread 4.23x, net debt 4.45x normalized OE, 9.5 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.5 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q1 2026, quoted above. The Q2 2026 10-Q is filed but not yet in EDGAR companyfacts, so no filing-direct TTM through Q2 exists; Q2 prints were used only for growth sanity.
- **NI_OCF_DIVERGENCE** (2025): explained by non-cash D&A, not a one-off distorting OCF. FY2025 net income $390,974,000 vs OCF $866,725,000; D&A alone was $446,006,000 (financials_history.csv), which with SBC $32,702,000 bridges essentially the whole gap, partly offset by working-capital use. The OCF-based conservative OE is the series used throughout, so the divergence does not contaminate the base.
- **CASH_INCLUDES_RESTRICTED**: confirmed as filed — the only cash tag for FY2025 is the combined cash + restricted-cash total ($826,315,000) with no separate restricted-cash tag, so reported net debt of $1,949,848,000 is understated by the restricted amount, which the filings data does not separate. Net debt is therefore treated as a floor throughout this analysis and the leverage flag below is read with that in mind.
- **LOW_OE_YIELD** (preliminary run, 1.83% on the median base): on the TTM base actually used the OE yield is 2.55% — still low. The valuation rests heavily on growth; that fragility is real and is one reason the verdict is sized to the conservative end.
- **WIDE_SCENARIO_SPREAD** (4.23x on the final run): real — super-bull IV@15 $174.28 vs super-bear $41.19. Confidence is capped at medium, and the verdict is sized to the conservative end. Note the spread does not change the tier: every scenario, super bull included, is Tier D.
- **HIGH_NET_DEBT**: net debt 4.45x normalized OE on the final diagnostics (and a floor, per CASH_INCLUDES_RESTRICTED), plus lease liabilities $259,534,000 and new 6.250% notes due 2034 issued around the Oct 2026 acquisitions. Levered OE can compress fast in a downturn — that is exactly the super-bear case (0.75x OE mult, IRR 4.00%).

## My thoughts / overlay
- The honest headline is the gap, not the growth story: the business is genuinely good — permitted, sticky, ~10–12% ROIC, OE positive 5/5 years, Q2 2026 accelerating — but at $320.06 the market is paying for far more than even the super-bull path delivers here (super-bull IV@15 $174.28, IRR 9.91%).
- Method range: on the preliminary median base ($5.859/share) with default scenarios the weighted IRR was 5.51% (IV@15 $70.32); on the TTM base with recalibrated growth it is 6.24% (IV@15 $89.05). Both are Tier D — the tier does not depend on which defensible base is chosen.
- What would have to be true to clear 15%: the share would need to trade near the weighted IV@15 of $89.05 — roughly 72% below the current price — or OE/share would need to compound far beyond the super-bull path for years.
- Risks to this verdict (i.e. ways it could be too harsh): companyfacts lag means H1 2026 filing-direct OE is not yet in the base — Q2 was strong; the Oct 2026 acquisitions and the 10-year contract add revenue the TTM base contains none of. Both are credited in the bull/super-bull growth starts, and even the super bull does not reach a 10% IRR.

## Final verdict
- **Final tier: D** (weighted IRR 6.24% on the final inputs; every scenario is D)
- Confidence: **Medium** (filing-direct TTM base and unanimous scenario tier, capped by the 4.23x scenario spread, the companyfacts Q2 lag and the unseparated restricted cash)
- One-liner: Quality permitted hazardous-waste franchise, moat 6/10 — but at $320.06 it does not come close to clearing 15% (weighted IRR 6.24%, IV@15 $89.05; clears 15% only near $89).
