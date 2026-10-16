# XYL — Xylem Inc.
v5 run, 2026-10-15. In scope (market cap $25.068B at $102.74, nasdaq_quote_api).

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.py output, or financials_history.csv — none are recomputed.

## What it is
The largest pure-play water technology company: pumps and transport, treatment, Sensus metering/measurement & control (MCS), and water solutions & services (the Evoqua business, acquired 2023 in a $7.5B all-stock deal). Sells to municipal utilities, industrial and commercial customers across 50+ countries. Currently reshaping the portfolio under an "80/20" simplification program, retreating from China, and — announced August–September 2026 — buying the Cornell Pump and Roper Pump businesses for ~$1.46B cash, funded with $1.5B of new senior notes plus a $1.5B revolver (closing expected Q4 2026). The stock fell to near its 52-week low ($102.42; 52-week high $154.27) on the financing.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** revenue $9,035M; net income $957M; operating cash flow $1,241M; capex $331M (tag: PaymentsToAcquireProductiveAssets); SBC $53M.
- **Conservative owner's earnings FY2025: $857.0M = $3.51/share** (key_numbers.md).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $1,536M in FY2025 per financials_history.csv — higher than the conservative figure mainly because D&A ($575M) runs well above capex ($331M) at this asset-heavy, acquisition-built company. The conservative OCF-based figure is the one used; the gap is a reminder that reported "adjusted EPS" ($5.55–$5.70 guided for 2026) is not owner's earnings.
- OE positive 5 of the last 5 fiscal years. Net debt (latest): **−$71.0M, i.e. slight net cash** (−0.08x normalized OE, key_numbers.md) — but that predates the Cornell/Roper financing noted above; leverage is rising after the balance-sheet date.
- SBC is small and flat: $53M in FY2025 and $53M TTM against TTM OCF of $1,301M — not a dilution story (see DILUTION flag).

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $1,241M − prior YTD $338M + current YTD $398M = **TTM $1,301M**
- Capex: FY $331M − prior YTD $169M + current YTD $179M = **TTM $341M**
- SBC: FY $53M − prior YTD $25M + current YTD $25M = **TTM $53M**
- Shares (current-YTD weighted diluted): **239,967,000**
- **TTM OE total $907M → base OE/share $3.78** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $3.51/share — the TTM base is used because FY2025 is 9.5 months stale and TTM OE is genuinely higher (OCF grew while capex/SBC stayed flat); the median is retained in the reporting.

## Moat: 6/10 — moderate-strong, not wide
Justification: Largest pure-play water platform post-Evoqua, installed-base service revenue, specified-in metering, global network, proven pricing power; but a fragmented market, contestable equipment lines, and only good-not-exceptional returns cap it at 6.
- FOR: Largest pure-play water platform post-Evoqua; scale in treatment, transport and metering
- FOR: Installed base drives recurring aftermarket, services and outsourced-water revenue
- FOR: Sensus AMI metering specified into long utility replacement cycles (switching costs)
- FOR: Global service/distribution network in 50+ countries
- FOR: Proven pricing power — operating margin 13.3% → 16.7% YoY in Q2 2026 through tariff pressure
- FOR: Regulatory demand drivers (PFAS remediation, IIJA funding) favor the incumbent leader
- AGAINST: Fragmented market — leader holds only single-digit share in smart water; no network effects
- AGAINST: Much of the portfolio is engineered equipment contestable by Veralto, Pentair, Ecolab and local rivals
- AGAINST: China business in retreat (orders collapsed; headcount cut ~40%)
- AGAINST: Applied Water exposed to residential/commercial construction cycles
- AGAINST: Serial-acquirer model: growth partly bought (Evoqua, now Cornell/Roper pumps) with integration and leverage risk
- AGAINST: Metering (MCS) segment currently declining — electric-metering headwinds
- A 6 gives CAP = 9.8 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 9.8 years, 15-year projection.

## DCF — v5 final run (2026-10-15)
Growth recalibration (written reason): the engine's g_base of 10.48% is built on deal-inflated inputs — revenue CAGR 3y of 17.83% straddles the Evoqua closing (May 2023), and OE/share CAGR 2y of 23.05% reflects deal scale plus integration-era margin recovery, not organic run-rate. Actual organic prints: latest FY revenue YoY +5.52% reported; Q2 2026 revenue $2.34B, +1.5% reported / ~+1% organic; FY2026 organic growth guidance narrowed to 2–3% with reported revenue guided to ~$9.2B. OE/share growth from here is mostly margin (80/20 program; Q2 2026 adjusted EPS $1.46, +15.9%; FY EPS guidance raised to $5.55–$5.70) plus resumed buybacks — real, but not 10%+ compounding of cash OE. Scenario starts were therefore set via offsets (−0.165 / −0.095 / −0.045 / +0.005 / +0.055 vs g_base) to −6.0 / 1.0 / **6.0** / 11.0 / 16.0%. Probabilities 10/25/30/25/10; OE multipliers 0.75/0.90/1.00/1.10/1.25. Price $102.74.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -6.0% | 0.75 | Cornell/Roper integration stumbles, leverage bites, China exit costs mount | $15.92 | 4.19% |
| Bear | 25% | 1.0% | 0.90 | Organic growth stalls at guide's low end; metering keeps declining | $26.07 | 5.61% |
| Base | 30% | 6.0% | 1.00 | 2–3% organic growth + 80/20 margin gains + buybacks | $36.19 | 7.05% |
| Bull | 25% | 11.0% | 1.10 | PFAS/IIJA demand and orders backlog (+42% in Q2) convert; margins keep expanding | $49.71 | 8.90% |
| Super bull | 10% | 16.0% | 1.25 | Full margin program + acquired pumps outperform + data-center cooling ramps | $70.49 | 11.49% |

- **Probability-weighted: IV@15% $38.44 (−62.6% vs price), IV@12% $51.44, IV@10% $66.00, weighted IRR 7.41%, base-case IRR 7.05%**
- **Tier by numbers: D.** Diagnostics (key_numbers.md): OE yield 3.68%, terminal value 19.5% of IV@15%, scenario spread 4.43x, net debt −0.08x normalized OE, 9.5 months since FY end.
- Sanity check on the starts: even the super-bull start (16.0%) sits far above current organic prints (1–3%) — deliberately, because it prices in margin-led OE growth — and it *still* only yields an 11.49% IRR. No scenario start is below what the company just printed on the metric that matters here (cash OE/share); the bull cases are carried by the OE multipliers and margin story, and they are not enough.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.5 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, inputs quoted above. TTM OE/share $3.78 vs FY2025 $3.51: the TTM base is the *higher* one, so staleness is not what's hurting this name.
- **DILUTION** (share count +10.47%/yr, −5.00pp growth adjustment): the share jump is the Evoqua all-stock deal, not creep — diluted shares went 180,979,000 (FY2022) → 218,180,000 (FY2023) → 243,521,000 (FY2024) → 243,994,000 (FY2025) per financials_history.csv, i.e. flat since the deal year, and the TTM current-YTD count of 239,967,000 shows buybacks have resumed. SBC is flat at $53M (FY and TTM). The −5pp adjustment is a historical-deal artifact baked into g_base; the recalibrated scenario starts above were set from organic prints, so the artifact does not drive the verdict — and no plausible adjustment changes it, since even the super-bull scenario IRR is 11.49%.
- **WIDE_SCENARIO_SPREAD** (4.43x): real — outcomes hinge on whether margin expansion compounds for a decade. Confidence is capped at medium, and the verdict is sized to the conservative end. Note the spread does not straddle the hurdle: *every* scenario, super bull included, sits below 15% IRR.

## My thoughts / overlay
- This is a valuation verdict, not a quality verdict. Xylem is a genuinely good business — but at $102.74 the market is paying ~27x TTM owner's earnings (OE yield 3.68%) for a company growing organically at 2–3%. The market price is set off adjusted EPS ($5.55–$5.70 guided); the OE screen deducts full capex and SBC and lands far below. Even discounting at 10% instead of 15%, the weighted IV is $66.00 — still a third below the price.
- There is no method range worth reporting here: TTM base vs median base, recalibrated vs engine growth — every defensible variant lands in Tier D territory, because the binding constraint is the 3.68% starting OE yield, not the growth assumption. The honest headline is the gap itself.
- Watch items that could change the picture: Cornell/Roper closing (Q4 2026) and the leverage it adds to a currently net-cash balance sheet; whether the +42% Q2 orders growth converts to revenue in 2027; PFAS remediation demand into the EPA's 2029 compliance deadline; MCS metering recovery.
- Margin of safety: none at this price on OE terms. The weighted IV@15% of $38.44 is the price at which the weighted case clears 15% — the stock would need to fall roughly to that level, or OE/share would need to roughly triple at the current price, before this screen says buy.

## Final verdict
- **Final tier: D** (weighted IRR 7.41% on the v5 final inputs; no scenario reaches the 15% hurdle)
- Confidence: **Medium** (high on the OE data quality — clean tags, no gaps, TTM confirmed; capped at medium by the 4.43x scenario spread)
- One-liner: High-quality water pure-play, moat 6/10 — but priced for perfection on owner's earnings: weighted IRR 7.4% at $102.74, weighted IV@15% $38.44; clears the 15% hurdle only below ~$38.
