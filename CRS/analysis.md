# CRS — Carpenter Technology Corporation
v5 run, 2026-10-16. In scope (market cap $19.180B at $380.56, nasdaq_quote_api).

All figures below are copied from key_numbers.md, dcf_numbers.json, or financials_history.csv — none are recomputed.

## What it is
Producer of high-performance specialty alloys — nickel-based superalloys, titanium, stainless and powder metals — for critical applications in aerospace and defense (its largest market), medical, energy, transportation and industrial markets. Two segments: Specialty Alloys Operations (SAO, the core melt and mill business) and Performance Engineered Products (PEP). FY2026 (ended 2026-06-30) was a record year: revenue $3,124.2M, operating income $702.0M per the filing history, driven by aerospace demand, pricing and mix. Management guided FY2027 operating income of $850–$880M (+21–25%) and a path toward roughly $1.2–$1.3B by FY2029 tied to a brownfield melt-capacity expansion due to complete in FY2028 (company guidance reported in earnings coverage, Jul 30, 2026). Near-term overlay: newly appointed CEO Brian Malloy died suddenly after taking the role on July 1, 2026 and former CEO Tony Thene was reappointed indefinitely — a real leadership-disruption event, though the operating plan was left intact in guidance.

## Owner's earnings
**FY2026 (10-K via EDGAR, from financials_history.csv):** operating cash flow $605,000,000; capex $242,700,000 (tag PaymentsToAcquireProductiveAssets); SBC $26,400,000 (always a real cost).
- **Conservative owner's earnings FY2026: $335,900,000 = $6.66/share** (key_numbers.md: latest FY OE/share $6.66; latest FY OE total $335.9M)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $427,400,000 — above the conservative figure because capex ($242.7M) exceeds D&A ($147.1M); the engine correctly charges total capex in the conservative/base case, and with a brownfield expansion underway some of that capex is growth capex — but even crediting the higher maintenance figure in words does not change the verdict (see Thoughts).
- OE-positive years: 3 of the last 5 (key_numbers.md). Conservative OE was negative in FY2022 (−$96,100,000) and FY2023 (−$84,000,000) — this is a cyclical that lost cash on the conservative definition at the trough, which is central to both the moat score and the scenario weights.
- Balance sheet is not the problem: net debt $297.4M, net debt / normalized OE 1.14x (key_numbers.md) — modest leverage.
- Shares diluted (latest): 50,400,000; share count CAGR 0.81%/yr (a slight dilution headwind, credited as a −0.81% growth adjustment in the blend).

**Base used = normalized (median of last 3 FY OE/share) $5.19/share** (base_source: median_of_last_3_fy_oe_per_share). The latest FY ($6.66) sits above the median because FY2024 was still early in the recovery; the median is the less flattering, more cycle-honest anchor and no divergence flag fired. No TTM override: FY2026 ended 3.5 months ago (months since FY end 3.5), so the annual base is not stale and no STALE_FY flag fired.

## Moat: 6/10 — moderate, real but cyclical
Justification: real qualification and certification barriers in aerospace alloys — alloys are certified per engine/airframe program and re-qualifying a supplier takes years — plus scarce high-purity melt capacity and proven pricing power (record SAO margin, long run of margin expansion). But it is not wide: owner's earnings were negative in FY2022 and FY2023, so returns were not held through the cycle; the business is capital-intensive, aerospace/defense-concentrated, and exposed to raw-material prices and OEM build rates.
- FOR: Qualification/certification barriers — alloys certified per jet engine and airframe program, re-qualification takes years; proven pricing power — record SAO operating margin and a long run of consecutive margin expansion; scarce high-purity melt capacity, being added to by the brownfield expansion; long OEM relationships in aerospace and defense with multi-year order visibility.
- AGAINST: Cyclical — conservative owner's earnings were negative in FY2022 and FY2023; aerospace and defense concentration, tied to OEM build rates and defense budgets; capital-intensive — FY2026 capex $242.7M vs D&A $147.1M, plus brownfield execution risk; raw-material (nickel, titanium, cobalt) price volatility and capable rivals such as ATI.
- A 6 gives CAP = 9.8 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 9.8 years, 15-year projection.

## DCF — v5 final run (2026-10-16)
Growth inputs: growth blend 12.39% → g_base 11.58% (key_numbers.md). Components: rev CAGR 5y 16.19%, rev CAGR 3y 7.00%, latest rev YoY 8.59%, OE/share CAGR 2y 45.47%. Default offsets (−12/−5/0/+5/+12pp) and default OE multipliers (0.75/0.90/1.00/1.10/1.25) were kept, probabilities 10/25/30/25/10.

**Sanity check against actual prints (required):** the OE/share CAGR 2y of 45.47% is a recovery artifact off the negative-OE trough and was NOT treated as a sustainable growth rate — revenue, the cleaner signal, grew 8.59% in the latest FY with a 7.00% 3-yr CAGR. The base start (11.6%) therefore sits below the 45.47% OE print and below FY2027 guided operating-income growth (+21–25%) for a written reason: the guidance year is a single year of operating leverage on pricing/mix at peak aerospace demand, and owner's earnings must also absorb expansion capex (FY2026 capex already $242.7M, up from $154.3M in FY2025 per financials_history.csv). The super-bull start (23.6%) does match the guided FY2027 operating-income growth range, so the optimistic case is not understated — it still values the stock at $135.21 at a 15% discount.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -0.4% | 0.75 | Aerospace downcycle repeats the FY2022–23 pattern; OE troughs again | $28.05 | 3.38% |
| Bear | 25% | 6.6% | 0.9 | Build rates stall, pricing/mix gains stall, expansion capex still spent | $45.96 | 4.10% |
| Base | 30% | 11.6% | 1.0 | Guided FY2027 step-up lands, then growth fades over the CAP | $63.77 | 4.84% |
| Bull | 25% | 16.6% | 1.1 | FY2029 operating-income path delivered on schedule | $87.52 | 5.82% |
| Super bull | 10% | 23.6% | 1.25 | Guidance-level growth sustains; scarcity capacity earns peak margins for years | $135.21 | 7.69% |

- **Probability-weighted: IV@15% $68.83, IV@12% $93.72, IV@10% $121.78, weighted IRR 5.08%, base-case IRR 4.84%**
- **Tier by numbers: D.** Diagnostics (key_numbers.md): OE yield 1.36%, terminal value 21.3% of IV@15%, scenario spread 4.82x, net debt 1.14x normalized OE, 3.5 months since FY end.

## Flags — every fragility flag resolved
- **LOW_OE_YIELD** (base OE yield 1.4% — valuation rests almost entirely on growth; tier is fragile): accepted as the core finding, not waved off. At $380.56 against a weighted IV@15% of $68.83, the upside at 15% is −81.9% (key_numbers.md). The verdict does not rest on the yield alone: even the super-bull scenario (23.6% growth start, 1.25x OE mult) yields only a 7.69% IRR, so the D tier survives the most generous scenario the engine ran, not just the weighted case.
- **WIDE_SCENARIO_SPREAD** (super-bull IV 4.82x super-bear IV): real — a cyclical at peak earnings has a wide outcome range. Confidence is capped at medium (never high under this flag), and the verdict is sized to the conservative end. Note the spread here does not straddle the hurdle: all five scenarios are individually Tier D (<10% IRR), so the spread affects the size of the shortfall, not the tier.

No other flags fired: no DATA_GAP (data_gap empty), no STALE_FY, no BASE_DIVERGENCE, no SECTOR_MODEL_MISMATCH, no HIGH_NET_DEBT.

## My thoughts / overlay
- This is a quality-versus-price case, not a quality case against the business. Record FY2026 results, +21–25% guided FY2027 operating-income growth, a record SAO margin and a funded capacity expansion are genuinely strong — and the market has already paid for them, and for several more years like them, upfront. The stock also already corrected hard from its highs before this run; at $380.56 it still does not clear even a 10% hurdle in the super-bull case.
- Method range: there is no defensible method range to report across tiers. Every scenario — including one that starts growth at the guided FY2027 operating-income rate and multiplies OE by 1.25 — is Tier D. Using the latest-FY base ($6.66) instead of the median ($5.19), or the maintenance OE definition instead of the conservative one, would raise IVs but, on the super-bull evidence, nowhere near the $380.56 price. The honest headline is the size of the gap, not a range of tiers.
- Hurdle-clearing price: the weighted IV@15% is $68.83 — that is the price at which the weighted case clears Andrew's 15% hurdle. A margin of safety against the bear case would require a price at or below the bear IV@15% of $45.96.
- Risks to this verdict (i.e., what would make D wrong): sustained scarcity pricing in aerospace melt capacity that holds peak margins through a full cycle — the FY2022–23 negative-OE history argues against assuming it — or a step-change in defense demand large enough to keep OE compounding at guidance rates well past the 9.8-year CAP.
- Watch items: the FY2027 Q1 print on Oct 22, 2026 against the $850–$880M full-year operating-income guide; brownfield capex pace vs the FY2028 completion claim; leadership stability under the reappointed CEO.

## Final verdict
- **Final tier: D** (weighted IRR 5.08%; every individual scenario is also below 10%)
- Confidence: **Medium** (high on the filing data and the direction of the gap; capped at medium by the WIDE_SCENARIO_SPREAD flag)
- One-liner: Good cyclical alloy franchise, moat 6/10, at a scarcity price — weighted IRR 5.08% and weighted IV@15% $68.83 vs price $380.56; every scenario, including super bull, is Tier D, and it clears 15% only at about $68.83.
