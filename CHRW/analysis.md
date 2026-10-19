# CHRW — C. H. Robinson Worldwide, Inc.
Engine 5.4.0 run, 2026-10-16. Price $139.95 (nasdaq_quote_api), market cap est. $17.004B — in scope under $40B.

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.json or fundamentals.json — none are recomputed.

## What it is
The largest US asset-light freight broker / 3PL: North American Surface Transportation (NAST — truckload and LTL brokerage), Global Forwarding (ocean/air), plus managed services and produce sourcing. It owns almost no transportation equipment — FY2025 capex was $19.6M against OCF of $914.5M — and earns a spread (adjusted gross profit, AGP) between what shippers pay and what carriers charge. Gross revenue is mostly pass-through: FY2025 revenue $16.23B, down from $24.70B in FY2022 as spot rates normalized. Q2 2026 (release, via search): revenue $4.93B (+19.3% YoY, spot-rate inflated — truckload linehaul cost per mile +29%), AGP +6.5%, adjusted operating income +19.5%, adjusted EPS $1.61 (+24.8%); management reaffirmed a 2026 operating-income target of $964M–$1.04B against FY2025 filed operating income of $795.0M.

## Owner's earnings
- **Conservative (OCF − capex − SBC), latest FY2025:** OE total $814.8M = **$6.71/share** (key_numbers.md).
- **Maintenance (NI + D&A − min(capex, D&A) − ΔNWC), FY2025:** $363.2M (financials_history.csv) — far below the conservative figure because the ΔNWC leg ($307.0M) swings violently for a broker whose receivables/payables are pass-through freight billings. The conservative OCF-based series is the one used; the maintenance series is reported here as the cross-check and is the less reliable of the two for this business.
- OE positive 4 of the last 5 years; the negative year is FY2021 (OE/share −$0.52) when OCF collapsed to $95.0M on a working-capital build during the freight boom despite net income of $844.2M — a WC-timing artifact, not a franchise loss.
- Net debt $928.6M (key_numbers.md), 1.59x normalized OE; lease liabilities $305.9M (dcf_numbers.json). DPS TTM $2.51, buybacks TTM $658.1M, dividends paid TTM $303.3M (fundamentals.json).

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct):**
- OCF: FY $914,519,000 − prior YTD $333,659,000 + current YTD $104,497,000 = **TTM $685,357,000**
- Capex: FY $19,628,000 − prior YTD $10,640,000 + current YTD $7,610,000 = **TTM $16,598,000**
- SBC: FY $80,070,000 − prior YTD $44,028,000 + current YTD $53,005,000 = **TTM $89,047,000**
- Shares (current-YTD weighted diluted): **120,350,000**
- **TTM OE total $579,712,000 → base OE/share $4.82** (base_source: ttm_json)
- The TTM base is below both the normalized 3-yr median ($5.38/share) and the latest FY ($6.71/share) because H1 2026 OCF was drained by working capital (Q2 2026 operating cash flow was only $35.9M per the Q2 release). It is kept as the base anyway: it is the most current filing-direct figure, it is the conservative choice, and the verdict does not depend on it — the preliminary run on the $5.38 median base printed a weighted IRR of 5.84% and IV@15% of $38.43, also Tier D.

## Moat: 6/10 — moderate, scale-based, not wide
Justification: largest US freight broker with a two-sided shipper/carrier network, Navisphere data scale and Lean AI productivity, but shippers and carriers multi-home with low switching costs, supply is not owned, and the business is freight-cycle exposed.
- FOR: Scale network — largest US freight broker, tens of thousands of shippers and carriers, volume/data advantage in matching and pricing; ROIC proxy 14.3%–32.8% FY2020–25 (fundamentals.json: 19.9% / 24.3% / 32.8% / 14.3% / 18.2% / 23.3%), above the cost of capital through the trough; Lean AI productivity >60% since end-2022 in NAST and Global Forwarding with headcount down while volumes rose, and 13 straight quarters outgrowing the Cass Freight Shipment Index (Q2 2026 release); asset-light variable-cost model cushions downturns.
- AGAINST: Low switching costs — shippers deliberately multi-home brokers in routing guides and carriers are not owned or exclusive; fragmented, transparent-priced competition (TQL, RXO, J.B. Hunt, Echo/Uber Freight, digital/AI entrants) on the same capacity pool; freight cyclicality — revenue $24.70B (FY2022) → $16.23B (FY2025) and OE/share spanning −$0.52 to $11.78 over five years; Montgomery negligent-hiring legal exposure plus the pending RXO acquisition's integration, leverage and customer-overlap risk.
- Gross-margin note: fundamentals.json's filed gross-margin series (~90%) is not economically usable here — gross revenue is pass-through billings and the filed COGS tag captures only part of transportation cost. The economic margin is AGP: Q2 2026 AGP was $738M on $4.93B of revenue per the Q2 release. The moat case therefore rests on the ROIC proxy series above, which stayed well above the cost of capital through the 2023 trough (14.3%) — consistent with a 6, not a 7+: returns are strong, but they are earned in a low-switching-cost, multi-homed market.
- A 6 gives CAP = 9.8 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 9.8 years, 15-year projection.

## DCF — final run (2026-10-16)
Growth sanity check (written reason for recalibration): the engine's blended start is −2.69%, built from gross-revenue components (5-yr CAGR 0.03%, 3-yr CAGR −13.05%, latest YoY −8.42%) that track pass-through spot rates, not earnings. The earnings prints are positive: Q2 2026 AGP +6.5% and adjusted operating income +19.5% YoY, OE/share CAGR 2y +11.65% (engine component), and the guided 2026 operating-income range sits well above FY2025's filed $795.0M. Scenario starts were therefore set on an earnings basis — base +5.0% (below the current AGP/operating-income prints because AGP, not spot-inflated gross revenue, is the secular driver and guidance comes off a trough), bull +10.0%, super bull +16.0% (still below guided operating-income growth; freight recovery plus Lean AI leverage), bear 0.0% (trough persists, spot-cost squeeze offsets AI gains — Q2 truckload AGP per shipment was flat despite +29% linehaul costs), super bear −5.0%. Probabilities 15/30/30/15/10 widen the bear weight per the OE_VOLATILE flag. OE multipliers are the defaults 0.75/0.90/1.00/1.10/1.25.

| Scenario | Prob | Growth start | OE mult | IV@15 | IRR |
|---|---|---|---|---|---|
| Super bear | 15% | −5.0% | 0.75 | $21.22 | 4.18% |
| Bear | 30% | −0.0% | 0.90 | $31.80 | 5.25% |
| Base | 30% | 5.0% | 1.00 | $44.15 | 6.55% |
| Bull | 15% | 10.0% | 1.10 | $60.65 | 8.24% |
| Super bull | 10% | 16.0% | 1.25 | $89.90 | 10.98% |

- **Probability-weighted: IV@15% $44.06 (−68.5% vs price), IV@12% $58.66, IV@10% $74.97, weighted IRR 6.59%, base-case IRR 6.55%**
- **Tier by numbers: D** (bear D → bull D; no tier band). Diagnostics (key_numbers.md): OE yield 3.44%, terminal value 19.0% of IV@15%, scenario spread 4.24x, net debt 1.59x normalized OE, 9.5 months since FY end.
- Hurdle-clearing prices (weighted path): 15% at $44.06 · 20% at $30.96 · 25% at $23.78.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.5 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, legs quoted above.
- **OE_VOLATILE** (OE/share spans >3x over 5 years, −$0.52 to $11.78): real and structural — pass-through working capital swings OCF (FY2021 OCF $95.0M vs FY2022 $1,650.2M) on top of the freight cycle. Handled by widening the bear weight to 45% on bear-or-worse (15/30) and by checking the verdict on both the TTM and median bases (both D).
- **NI_OCF_DIVERGENCE** (2023: net income $325.1M vs OCF $731.9M): a working-capital release, not a tax deposit or impairment — revenue collapsed from $24.70B to $17.60B in 2023, receivables shrank with billings, and operating income halved to $514.6M while cash was collected on the prior year's book. The OCF-based conservative OE is the series used throughout, and neither the TTM base nor the median base is a 2023 figure, so the divergence does not contaminate the base.
- **WIDE_SCENARIO_SPREAD** (4.24x): real — it is the freight cycle plus the RXO outcome. Confidence is capped at medium, and the verdict is sized to the conservative end: even the super-bull IV@15% ($89.90) sits 36% below the $139.95 price, so the spread does not threaten the tier.

## My thoughts / overlay
- The debate is price, not quality. This is a genuinely good business — asset-light, ROIC proxy 14–33% through a cycle, gaining share for 13 straight quarters, buying back stock — priced at $139.95 against a $4.82 TTM OE/share (3.44% OE yield). No scenario in the set, including a super bull that assumes a freight recovery, Lean AI leverage and a 1.25x OE level, clears even a 12% hurdle at this price (super-bull IRR 10.98%).
- Method range: preliminary run (median base $5.38, default scenarios) → weighted IRR 5.84%, IV@15% $38.43, Tier D. Final run (TTM base $4.82, earnings-recalibrated growth) → 6.59% / $44.06, Tier D. The range is narrow and entirely in D — unusual for this sweep, and it is the finding.
- Post-filing events not in the OE base: the announced RXO acquisition (~$5.8B per press reports, ~$300M of claimed annual savings, $185M breakup fee) would make the combined broker roughly twice its nearest competitor but adds leverage, integration risk and shipper-overlap churn, and it is not yet in any filing the engine reads; the Montgomery negligent-hiring verdict (Texas jury; management says it will appeal) raises a sector-wide legal cost that is likewise unquantified in the filings used. Neither is modeled — both argue against paying a premium multiple, not for it.
- Balance sheet is not the risk: net debt $928.6M is 1.59x normalized OE, capex is negligible, and the dividend (DPS TTM $2.51) plus buybacks ($658.1M TTM) are covered in a normal WC year — though H1 2026 shows how fast OCF can be absorbed by working capital when spot rates spike.

## Final verdict
- **Final tier: D** (weighted IRR 6.59% on the final TTM-based run; bear and bull both D)
- Confidence: **Medium** (high on the valuation gap — every base and every scenario lands in D; medium on any single OE path given WC-driven volatility and the pending RXO deal)
- One-liner: High-quality asset-light freight broker, moat 6/10 — does not clear 15% at $139.95 on any scenario (weighted IRR 6.59%, weighted IV@15% $44.06; even super bull is 10.98% / $89.90); it clears 15% only at or below $44.06.
