# LAMR — Lamar Advertising Company
Pass-1 v5 / engine 5.4.0 run, 2026-10-17. All figures below are copied from dcf_numbers.json, ttm.json, financials_history.csv, or fundamentals.json — none are recomputed.

## What it is
A REIT and one of the largest owners/operators of outdoor advertising in the US: billboards (the bulk of revenue), plus transit, airport and interstate logo displays. Headquartered in Baton Rouge. Market cap $15.255B at $150.10 (dcf_numbers.json, nasdaq_quote_api) — in scope under $40B. It is valued by the sector primarily on AFFO, not on a conventional owner's-earnings DCF — see SECTOR_MODEL_MISMATCH below.

## Owner's earnings
- FY2025 (10-K via EDGAR, financials_history.csv): operating cash flow $864,049,000; capex $180,800,000; SBC $33,959,000. Conservative owner's earnings (OCF − capex − SBC): $649,290,000 = $6.39/share (dcf_numbers.json: base_oe_latest_per_share $6.3885).
- Maintenance version FY2025: $729,149,000 (financials_history.csv oe_maintenance) — same ballpark; the conservative OCF-based figure is used throughout.
- OE positive 5 of the last 5 fiscal years (dcf_numbers.json).
- Net debt $3,354,095,000 (dcf_numbers.json, LongTermDebtNoncurrent+LongTermDebtCurrent basis), plus lease liabilities $1,486,537,000 — see HIGH_NET_DEBT.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct):**
- OCF: FY $864,049,000 − prior YTD $357,232,000 + current YTD $399,807,000 = **TTM $906,624,000**
- Capex: FY $180,800,000 − prior YTD $68,088,000 + current YTD $75,859,000 = **TTM $188,571,000**
- SBC: FY $33,959,000 − prior YTD $17,725,000 + current YTD $25,269,000 = **TTM $41,503,000**
- Shares (current-YTD weighted diluted): **101,525,836**
- **TTM OE total $676,550,000 → base OE/share $6.66** (ttm.json: $6.6638; dcf_numbers.json base_source: ttm_json)
- The engine's normalized base (median of last 3 FY) is $6.39/share — close to the TTM figure (+4.3%), so the choice of base is not the driver of the verdict.

## Moat: 6/10 — moderate
Justification: Scarce permitted billboard locations and the largest US outdoor network give durable local pricing power, with ROIC and gross margin evidence below, but advertising is cyclical, online/social platforms compete for the same budgets, leases and permits renew, and leverage is high — moderate moat, not wide.
- Evidence (fundamentals.json): roic_proxy 12.3% (2021), 12.5% (2022), 14.7% (2023), 12.5% (2024), 17.1% (2025) — consistently above a normal cost of capital but mid-teens, not exceptional. Gross margin: 67.7% (2021), 67.2% (2022), 67.0% (2023), 67.0% (2024), 67.0% (2025) — high and very stable. That supports a 6, not a 7+: returns are good through the period shown, but the business carries high debt and ad-cycle exposure.
- FOR: Scarce, permit-restricted billboard locations that are largely irreplaceable in high-traffic corridors; largest US outdoor network and scale, concentrated in secondary/local markets with an entrenched local sales force; digital billboard scale — a small share of faces drives a disproportionate share of billboard revenue, with programmatic growth; stable ~67% gross margin and ROIC in the 12–17% range through 2021–2025 (fundamentals.json).
- AGAINST: Advertising spend is highly cyclical — a recession cuts revenue directly; competition for ad budgets from online/social platforms; ground-lease renewals, zoning and permit regulation can erode or displace sites; high leverage: net debt $3.354B plus $1.487B lease liabilities (dcf_numbers.json).
- A 6 gives CAP = 9.8 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 9.8 years, 15-year projection.

## DCF — final run (2026-10-17)
Growth sanity check: the engine blend is 4.75% (rev CAGR 5y 7.63%, rev CAGR 3y 3.70%, latest FY rev YoY 2.68%, OE/share CAGR 2y 5.80% — dcf_numbers.json). Recent prints: FY2025 revenue +2.68%, TTM revenue growth 4.39% (fundamentals.json ttm), and Q2 2026 revenue +6.5% with acquisition-adjusted revenue +6.1% and raised full-year AFFO guidance to $8.75–$8.90/share (company Q2 2026 release, via search). The base start of 4.75% sits between the TTM print and the Q2 print — reasonable for a mature billboard portfolio. The default offsets were recalibrated downward (written reason): the default super-bull start of 16.75% has no support in any recent print for this mature, low-single-digit business, so scenario starts were set via offsets −7.75 / −3.75 / 0 / +2.75 / +5.25pp to −3.0 / 1.0 / **4.75** / 7.5 / 10.0%. Bull at 7.5% and super-bull at 10.0% sit above the Q2 print on digital mix shift and programmatic growth, with the reason written here. Probabilities 10/25/30/25/10; OE multipliers 0.75/0.90/1.00/1.10/1.25 (defaults). Price $150.10. Base OE/share $6.66 (TTM).

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -3.0% | 0.75 | Ad recession; levered OE compresses | $32.09 | 4.97% |
| Bear | 25% | 1.0% | 0.90 | Flat ad market, lease/rate pressure | $46.00 | 6.27% |
| Base | 30% | 4.75% | 1.00 | Blend growth decays normally over the CAP | $60.40 | 7.63% |
| Bull | 25% | 7.5% | 1.10 | Q2 momentum holds; digital/programmatic mix lifts growth | $75.09 | 8.97% |
| Super bull | 10% | 10.0% | 1.25 | Sustained digital conversion + acquisitions at high returns | $95.36 | 10.72% |

- **Probability-weighted: IV@15% $61.14 (−59.3% vs price), IV@12% $81.15, IV@10% $103.48, weighted IRR 7.71%, base-case IRR 7.63%**
- **Tier by numbers: D** (bear D, bull D — no TIER_BAND divergence). Diagnostics (dcf_numbers.json): OE yield 4.44%, terminal value 18.7% of IV@15%, scenario spread 2.97x, net debt 4.95x normalized OE, 9.5 months since FY end.
- Hurdle-clearing prices (dcf_numbers.json): clears 15% only at/below $61.14, 20% at $43.15, 25% at $33.24.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.5 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, quoted above ($6.66/share vs $6.39 normalized).
- **NI_OCF_DIVERGENCE** (2024): resolved — 2024 net income fell to $361,867,000 from $495,763,000 in 2023 while OCF rose to $873,610,000 (financials_history.csv) because Lamar revised its asset retirement obligation estimate, recording an additional $159.7M in depreciation and amortization in 2024 (company FY2024 release, via search); D&A in the history spikes to $462,967,000 in 2024 vs $293,423,000 in 2023 and $326,332,000 in 2025. It is non-cash and does not touch OCF, so the OCF-based conservative OE base is not contaminated by it.
- **SECTOR_MODEL_MISMATCH** (Real Estate): resolved as a grading rule — Lamar is a REIT (SIC 6798, fundamentals.json profile) valued by the sector on AFFO (2026 guidance $8.75–$8.90/share, via search), and an OE/capex DCF fits REITs poorly. Confidence is therefore **low**, and the D tier is a statement about this model at this price, not a claim that the AFFO-based valuation is identical.
- **HIGH_NET_DEBT**: net debt $3,354,095,000 is 4.95x normalized OE (dcf_numbers.json diagnostics), with a further $1,486,537,000 of lease liabilities on top. Balance sheet from the filing history (financials_history.csv, FY2025): total debt $3,418,907,000, cash $64,812,000, equity $1,024,779,000, assets $6,931,954,000. The bear/super-bear cases carry that leverage via the 0.90/0.75 OE multipliers.
- **WIDE_SCENARIO_SPREAD** was flagged on the preliminary run (4.51x) and is resolved in the final run by the growth recalibration written above: the final spread is 2.97x (dcf_numbers.json diagnostics). Confidence is in any case capped — it is low for the sector mismatch, never high.

## My thoughts / overlay
- The verdict is not base-sensitive: TTM ($6.66) and normalized ($6.39) bases are 4% apart, and even the super-bull case (10% growth start, 1.25x OE) yields only a 10.72% IRR at $150.10. At this price the OE-DCF does not come close to the 15% hurdle under any scenario in the set.
- Method caveat is the headline alongside the tier: for a REIT, AFFO per share ($8.26 in FY2025 and guided $8.75–$8.90 for 2026, via search) is the sector's cash measure and runs well above the conservative OE/share here, in part because this model's capex line captures growth/digital-conversion spend, not maintenance alone. Treat the D as model-specific; pass 2 / an AFFO lens would be the right second look, not a re-run of this DCF.
- Quality is real but priced: ~67% gross margins, mid-teens ROIC, 21 consecutive quarters of revenue growth per the Q2 2026 call (via search), and a raised dividend signal — none of that is in dispute. The dispute is only price vs the 15% hurdle on this model.

## Final verdict
- **Final tier: D** (weighted IRR 7.71% on the final TTM-base inputs; bear and bull both D)
- Confidence: **Low** (SECTOR_MODEL_MISMATCH — REIT; per spec, grade low)
- One-liner: Solid billboard REIT, moat 6/10 — does not clear 15% on owner's-earnings DCF (7.7% weighted IRR, IV@15% $61.14 vs $150.10 price; clears 15% only below ~$61); sector AFFO model fits better, so confidence is low.
