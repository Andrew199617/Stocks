# BWA — BorgWarner Inc.
Engine 5.4.0 run, 2026-10-18. In scope (market cap $12.579B at $58.13, nasdaq_quote_api). All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.json, financials_history.csv, or fundamentals.json — none are recomputed.

## What it is
Tier-1 automotive propulsion supplier (Auburn Hills, MI; SIC 3714): Turbos & Thermal Technologies, Drivetrain & Morse Systems (transfer cases), PowerDrive Systems (e-motors, inverters, integrated drive modules) and Battery Energy Systems. The portfolio deliberately spans combustion, hybrid and battery-electric propulsion. A new industrial leg (turbine generators for data-center/microgrid power, production expected early 2027) is optionality, not yet revenue.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $1,648,000,000; capex $469,000,000; SBC $66,000,000 (always a real cost).
- **Conservative owner's earnings FY2025: $1,113,000,000 = $5.14/share** (key_numbers.md: latest FY OE/share $5.14, latest FY OE total $1.113B)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $108,000,000 — not comparable: GAAP net income of $277,000,000 carries the year's impairment/restructuring and other non-comparable charges (see NI_OCF_DIVERGENCE below) and the year had a large working-capital swing, so the NI-anchored version is the distorted one. The OCF-based conservative figure is the series used throughout, cross-checked against the company's reported FY2025 free cash flow of ~$1.2B in its earnings releases.
- OE positive 5 of the last 5 fiscal years. Net debt $1.586B (key_numbers.md); lease liabilities $158,000,000 (dcf_numbers.json). Buybacks were $650,000,000 TTM (fundamentals.json) and the board added a $1.0B repurchase authorization in Q2 2026 (total $1.35B).

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $1,648,000,000 − prior YTD $661,000,000 + current YTD $738,000,000 = **TTM $1,725,000,000**
- Capex: FY $469,000,000 − prior YTD $196,000,000 + current YTD $239,000,000 = **TTM $512,000,000**
- SBC: FY $66,000,000 − prior YTD $14,000,000 + current YTD $10,000,000 = **TTM $62,000,000** (ttm.py's SBC YTD legs are Q1-only filings; the resulting TTM SBC is what ttm.py printed)
- Shares (current-YTD weighted diluted): **207,300,000**
- **TTM OE total $1,151,000,000 → base OE/share $5.55** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $2.89/share — rejected as the base: it is the distorted side of BASE_DIVERGENCE (see Flags). It is still reported in key_numbers.md and drives the diagnostics (net debt / normalized OE 1.32x).

## Moat: 4/10 — weak-moderate
Justification: Leading designed-in positions in turbos, transfer cases and e-propulsion with platform-life switching costs, but an OEM price-taker in a cyclical industry: GAAP ROIC proxy fell from 10.2% (2023) to 4.9% (2025) on recurring impairments/restructuring, gross margin is only ~18-19%, and the EV transition plus the loss-making battery segment erode durability.
- FOR: Designed-in content with platform-life switching costs — once certified into a vehicle platform, removal requires re-engineering; diversified propulsion portfolio (turbos/thermal, drivetrain/transfer cases, PowerDrive e-products) hedges ICE, hybrid and BEV paths; scale and systems-integration capability (integrated drive modules, eTurbo, 800V inverters/SiC) few tier-1 rivals match; adjusted operating margin expanded to 10.7% in FY2025 and 11.3% in Q2 2026 on cost control.
- AGAINST: OEM customer concentration and annual pricing pressure — a price-taker, not a price-maker; GAAP ROIC proxy declining (10.2% in 2023 to 5.7% in 2024 to 4.9% in 2025) with recurring impairment/restructuring charges; cyclical light/commercial vehicle production exposure, gross margin only ~18-19%; EV transition pace risk and a weak Battery Energy Systems segment (Q2 2026 sales -37.1% YoY, still loss-making).
- Evidence (fundamentals.json): roic_proxy 4.2% (2020), 8.5% (2021), 7.9% (2022), 10.2% (2023), 5.7% (2024), 4.9% (2025) — GAAP-basis, depressed by the recurring non-comparable charges; adjusted operating margin (10.7% FY2025) implies a higher underlying return, but the charges recur every year, so the GAAP series is the honest through-cycle picture and it does not support a moat above 4. Gross margin: 18.8% (2020), 18.4% (2021), 18.7% (2022), 18.1% (2023), 18.8% (2024), 18.7% (2025), 19.5% TTM — flat for five years, improving only in the latest TTM.
- A 4 gives CAP = 7.2 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 7.2 years, 15-year projection.

## DCF — final run (2026-10-18)
Growth recalibration (written reason): the engine's blended growth is 8.63% because two components are artifacts — OE/share CAGR 2y 54.16% (off the capex-spiked, charge-depressed 2023 base) and revenue CAGRs (5y 7.09%, 3y 4.25%) that predate the current flat regime. Actual recent prints: latest FY revenue YoY +1.63%, TTM revenue +2.16% YoY (fundamentals.json), Q2 2026 sales +0.3% YoY with organic sales -1.2%, and FY2026 guidance of $14.0-14.3B sales (vs $14.316B in FY2025), adjusted operating margin 10.7-10.9% and adjusted EPS $5.05-$5.30 (vs $4.91 in FY2025). OE/share can still grow faster than sales via the ~3%/yr buyback and modest margin expansion, so scenario starts were set via offsets (-0.127 / -0.086 / -0.046 / -0.016 / +0.024 vs g_base 8.63%) to -4.1 / 0.0 / **4.0** / 7.0 / 11.0%. Probabilities 10/25/30/25/10; OE multipliers 0.75/0.90/1.00/1.10/1.25 (defaults kept — the TTM base sits near the top of the company's own FY2026 free-cash-flow guidance range of $900M-$1.1B, so no upward tilt is warranted). Price $58.13.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -4.1% | 0.75 | Vehicle production downturn; battery losses widen; charges recur | $26.46 | 7.97% |
| Bear | 25% | 0.0% | 0.9 | Flat sales persist; OE/share treads water ex-buyback | $37.25 | 10.44% |
| Base | 30% | 4.0% | 1.0 | Flat revenue, buyback + modest margin gains drive OE/share | $48.28 | 12.91% |
| Bull | 25% | 7.0% | 1.1 | eProducts/hybrid awards convert; PowerDrive scales to profit | $59.55 | 15.29% |
| Super bull | 10% | 11.0% | 1.25 | Hybrid supercycle plus industrial/data-center leg lands from 2027 | $78.69 | 19.08% |

- **Probability-weighted: IV@15% $49.20 (-15.4% vs price), IV@12% $65.04 (+11.9%), IV@10% $82.69, weighted IRR 13.11%, base-case IRR 12.91%**
- **Tier by numbers: C.** Bear→bull IRR band 10.44% (C) → 15.29% (B). Hurdle-clearing prices (weighted path): 15% at $49.20, 20% at $34.90, 25% at $26.99. Diagnostics (key_numbers.md): OE yield 9.55%, terminal value 18.3% of IV@15%, scenario spread 2.97x, net debt 1.32x normalized OE, 9.6 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.6 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, legs quoted above.
- **BUYBACK_TAILWIND** (share count shrinking 3.0%/yr; key_numbers.md share count CAGR -2.96%): already credited via the growth adjustment in the blend; the recalibrated scenario starts include the buyback contribution to OE/share growth and do not double-count it — flat-revenue scenarios still grow OE/share only at buyback-plus-margin pace.
- **NI_OCF_DIVERGENCE** (net income vs OCF differ by >40% in 2023, 2024, 2025): the one-offs are identified — GAAP earnings carry recurring non-comparable items: impairment charges, restructuring expense, accelerated depreciation, costs to exit the charging business, a legal settlement and CEO-transition compensation (itemized in the company's Q3 2025 guidance reconciliation), plus PHINIA spin-off-related balances in the 2023 spin year. FY2025 GAAP operating margin was 3.7% vs 10.7% adjusted. These charges are largely non-cash, so OCF (and the OCF-based OE base) is not flattered by them directly — but their recurrence every year is a real economic cost of staying in this portfolio, which is why the moat is 4 and the bear/super-bear OE multipliers (0.90/0.75) haircut the TTM base rather than treating adjusted earnings as clean.
- **CASH_INCLUDES_RESTRICTED** (latest FY cash is the combined cash + restricted-cash tag, $2,313,000,000 per financials_history.csv, with no separate restricted-cash tag): net debt ($1.586B) is therefore understated by the restricted amount. In every prior year where a separate restricted-cash tag was filed it was $0-5,000,000 (2021: $3,000,000; 2022: $5,000,000; 2023: $0; 2024: $0), so the understatement is immaterial to the verdict; the balance sheet otherwise: total debt $3,899,000,000, equity $5,442,000,000 (financials_history.csv FY2025).
- **BASE_DIVERGENCE** (latest FY OE/share $5.14 vs 3-yr median $2.89): the median is the distorted side. The median window (2023: $2.16, 2024: $2.89, 2025: $5.14) is dragged by 2023's capex spike ($832,000,000, the PHINIA spin year) and 2024's elevated capex ($671,000,000) against FY2025 capex of $469,000,000 and TTM capex of $512,000,000. Current cash generation corroborates the higher base: FY2025 free cash flow ~$1.2B as reported by the company, TTM FCF/share $5.75 (fundamentals.json), and FY2026 FCF guidance of $900M-$1.1B — all far above what a $2.89/share base (~$0.6B total) implies. The TTM base is used; the residual risk that TTM capex is cyclically low is carried in the bear multipliers.
- **TIER_BAND** (bear C 10.44% vs bull B 15.29%): the verdict spans tiers — sized to the bear end in the final verdict below; confidence capped at medium.

## My thoughts / overlay
- The honest headline is the method range: on the engine's median base with default growth, the preliminary run printed weighted IRR 9.80% / IV@15% $32.65 (Tier D); on the TTM base with recalibrated growth, the final prints 13.11% / $49.20 (Tier C). Both defensible inputs agree the stock does not clear 15% at $58.13 — the disagreement is only about how far below it sits.
- Quality is real but cyclical: OE/share yield 9.55% on the TTM base, five straight OE-positive years, disciplined capital return ($650M TTM buybacks, dividend $0.68/share TTM per fundamentals.json). What the price already pays for is the bull path — eProducts conversion, PowerDrive profitability and the 2027 industrial/data-center leg — none of which is in the current OE base.
- Risks: light-vehicle production downturn, further EV-policy retreat hitting PowerDrive/Battery volumes, recurring restructuring becoming a permanent earnings leak, and OEM pricing givebacks absorbing the cost-out gains that produced Q2 2026's 11.3% adjusted margin.

## Final verdict
- **Final tier: C** (weighted IRR 13.11% on the final inputs; bear→bull band C→B, sized to the bear end)
- Confidence: **Medium** (high on the TTM cash base, medium on growth — revenue has been flat for three years and the growth case rests on awards not yet in production)
- One-liner: Solid cyclical auto supplier, moat 4/10 — does not clear 15% at $58.13 (13.1% weighted IRR, IV@15% $49.20); clears the 15% hurdle only below $49.20, size to the bear end (Tier C).
