# JBHT — J.B. Hunt Transport Services, Inc.
v5 run, 2026-10-15. In scope: market cap $22.468B at $230.00 (nasdaq_quote_api).

All figures below are copied from key_numbers.md / dcf_numbers.json, ttm.py output (ttm.json), or financials_history.csv — none are recomputed.

## What it is
North American multimodal freight carrier headquartered in Lowell, Arkansas. Core is Intermodal (JBI) — domestic containers moved line-haul by Class I railroads (BNSF in the West since 1990, Norfolk Southern in the East) under its own containers/drayage — roughly half of revenue and the segment where it holds a 20%-plus share of an approximately $25B market, ahead of Hub Group, Schneider, STG and Knight-Swift (per Morningstar summaries found in research). Other segments: Dedicated Contract Services (DCS, contract private-fleet outsourcing), Integrated Capacity Solutions (ICS, brokerage), Truckload (JBT) and Final Mile Services (FMS). Purchased transportation is more than half of total costs, so a large part of the cost base is variable with load volume.

Recent prints: Q2 2026 revenue $3.50 billion, up 19% year over year (up 11% excluding fuel surcharge), operating income $259.5 million, up 32%, diluted EPS $1.91, up 45% — intermodal set a quarterly volume record on higher loads and revenue per load, and ICS returned toward profitability. Management then warned at a September conference that Q3 2026 EPS could fall 5–10% sequentially on higher purchased-transportation, drayage and driver-recruitment costs — the freight inflection is real, but so is the cost snap-back.

## Owner's earnings
**FY2025 (10-K via EDGAR, financials_history.csv):** operating cash flow $1,678,272,000; capex $730,687,000 (tag PaymentsToAcquirePropertyPlantAndEquipment); SBC $71,753,000 (tag ShareBasedCompensation, always a real cost).
- **Conservative owner's earnings FY2025: $875,832,000 = $8.97/share** (latest FY OE/share in dcf_numbers.json)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $792,820,000 — same ballpark as the conservative figure; the gap between the two definitions is not the story here.
- OE positive 4 of the last 5 fiscal years — the exception is FY2023, when conservative OE was negative on a capex spike (see BASE_DIVERGENCE / OE_VOLATILE below). Net debt $1,449,513,000 (dcf_numbers.json).
- Balance sheet in the verdict: net debt is 1.37x normalized OE (diagnostics) — manageable, not a solvency issue, but it is real leverage on a cyclical earnings stream and is already deducted via the engine's net-debt handling; it does not rescue or sink the verdict.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $1,678,272,000 − prior YTD $806,245,000 + current YTD $723,266,000 = **TTM $1,595,293,000**
- Capex: FY $730,687,000 − prior YTD $462,291,000 + current YTD $227,175,000 = **TTM $495,571,000**
- SBC: FY $71,753,000 − prior YTD $38,107,000 + current YTD $38,084,000 = **TTM $71,730,000**
- Shares (current-YTD weighted diluted): **95,073,000**
- **TTM OE total $1,027,992,000 → base OE/share $10.81** (base_source: ttm_json)
- Caution on this base, stated plainly: TTM capex ($495,571,000) is well below FY2025 gross capex ($730,687,000) and below the company's own reported net capex for 2025 (~$575 million in its Q4/FY2025 release, per research). Tractor/trailer capex is lumpy and deferrable for a few quarters, not forever — so the TTM base is, if anything, generous to the stock. The bear/super-bear OE multipliers (0.90 / 0.75) are where capex normalization is charged. Even on this generous base the stock is Tier D; on the engine's normalized median base ($5.37/share) the preliminary run printed a weighted IRR of only 5.03%.

## Moat: 6/10 — moderate-strong, not wide
Justification: Intermodal scale and rail partnerships built since 1990 plus sticky dedicated contracts give real network and retention advantages, but JBHT owns no railroad, pricing power is cyclical, and truckload/brokerage are near-commodity.
- FOR: Intermodal leadership — 20%-plus share, largest domestic container fleet economics, network density that cuts empty moves and improves asset turns as volume grows
- FOR: Long-standing Class I rail partnerships (BNSF West since 1990, Norfolk Southern East) that are hard to replicate at scale
- FOR: Dedicated Contract Services stickiness — contract-based, operationally embedded, with customer retention around 96% cited for Q1 2026 in research
- FOR: Scale cost-to-serve program and the J.B. Hunt 360 platform across segments; buybacks shrinking the share count 2.5%/yr (already credited in the growth blend)
- AGAINST: Owns no railroad — line-haul depends on Class I service quality and pricing
- AGAINST: Freight pricing power is cyclical; when highway capacity loosens, intermodal's price umbrella and volumes compress
- AGAINST: Direct competition from Hub Group, Schneider, Knight-Swift and STG in intermodal, and near-zero switching costs in truckload/brokerage
- AGAINST: Cost inflation it cannot fully control — purchased transportation (over half of costs), driver pay/recruitment, insurance and claims
- A 6 gives CAP = 9.8 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 9.8 years, 15-year projection.

## DCF — v5 final run (2026-10-15)
Engine blended growth is only 1.73% (g_blend −0.73% from rev CAGR 5y 4.48% / 3y −6.78% / latest YoY −0.73%, plus a +2.46pp buyback adjustment) — a trough-freight blend. Probabilities were widened to the bear side versus the 10/25/30/25/10 defaults (15/30/30/15/10) on the OE_VOLATILE instruction, the guided sequential Q3 EPS decline, and the capex-deferral flattery in the TTM base. Offsets and OE multipliers are the defaults (−12/−5/0/+5/+12pp; 0.75/0.90/1.00/1.10/1.25). Price $230.00.

Growth-start sanity check (required): the super-bull start (13.73%) sits below Q2 2026's printed revenue growth (+19%, +11% ex-fuel surcharge) and EPS growth (+45%), with a written reason — Q2 is a rebound print off a freight-recession trough, management has already guided Q3 EPS down 5–10% sequentially on costs, TTM capex is at a deferrable low that will normalize against OE, and the 5-year revenue CAGR is only 4.48%. Extrapolating the rebound quarter as a 15-year fade start would repeat the inflection-artifact error in the opposite direction.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | -10.00% | 0.75 | Freight recession resumes; capex normalizes into falling volumes | $38.20 | 4.18% |
| Bear | 30% | -3.27% | 0.90 | Trough persists; cost inflation eats the recovery | $61.75 | 5.61% |
| Base | 30% | 1.73% | 1.00 | Slow mid-cycle grind at the blended growth rate | $85.69 | 7.12% |
| Bull | 15% | 6.73% | 1.10 | Intermodal conversion and dedicated growth sustain a real upcycle | $117.75 | 9.08% |
| Super bull | 10% | 13.73% | 1.25 | Durable mode-conversion supercycle at rebound growth rates | $182.57 | 12.68% |

- **Probability-weighted: IV@15% $85.88, IV@12% $113.25, IV@10% $143.71, weighted IRR 7.20%, base-case IRR 7.12%**
- **Tier by numbers: D.** Diagnostics: OE yield 4.70%, terminal value 18.04% of IV@15%, scenario spread 4.78x, net debt 1.37x normalized OE, 9.46 months since FY end.
- Note the ceiling: even the super-bull case (12.68% IRR, IV@15 $182.57) does not clear the 15% hurdle at $230.00, and does not even reach the current price.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.46 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, with all four legs quoted above.
- **BASE_DIVERGENCE** (latest FY $8.97 vs 3-yr median $5.37): both are distorted, in opposite directions. The median is dragged down by FY2023, when capex of $1,862,431,000 (financials_history.csv) — a fleet/container investment spike well above that year's D&A of $737,954,000 — drove conservative OE negative for the year; that is a capex-cycle trough, not run-rate earning power. The latest FY and TTM are flattered the other way by capex falling back. The TTM base was used because it is the most current filing-derived figure and the verdict is D on either base (preliminary median-base run: weighted IRR 5.03%); the flattery is charged in the bear weights and multipliers rather than by picking the lower base.
- **OE_VOLATILE** (OE/share range >3x over 5 years): real cyclicality plus the 2023 capex spike. Handled by widening bear-side probabilities to 45% combined (15/30) and keeping confidence below high.
- **NI_OCF_DIVERGENCE** (NI vs OCF >40% apart in 2023, 2024, 2025): explained by non-cash depreciation on a large owned fleet, not by a one-off — D&A was $737,954,000 in 2023, $761,141,000 in 2024 and $714,785,000 in 2025 (financials_history.csv), which bridges most of the NI–OCF gap in each named year; the remainder is normal working-capital movement for a carrier. The OE base is built from OCF directly, so the divergence does not contaminate it.
- **BUYBACK_TAILWIND** (share count shrinking 2.5%/yr): already credited via the +2.46pp share-count adjustment in the growth blend; not double-counted in the verdict.
- **WIDE_SCENARIO_SPREAD** (super-bull IV 4.78x super-bear): real — a cyclical carrier at a cycle inflection genuinely has a wide outcome range. Confidence is set to medium (and is capped there by make_score.py), and the verdict below is sized to the conservative end.

## My thoughts / overlay
- Method range: median base → weighted IRR 5.03% (Tier D); latest-FY base sits between the two; TTM base → 7.20% (Tier D). Every defensible base lands in Tier D — unusually for this sweep, the verdict does not depend on the base fight. What the market is paying for at $230.00 is not current owner's earnings; it is a multi-year freight supercycle plus mode conversion, already priced past even this model's super-bull case.
- Quality is not the problem: the intermodal franchise is the best asset in US surface freight, dedicated is sticky, the balance sheet carries only 1.37x net debt to normalized OE, and management is cutting structural cost while buying back stock. The problem is purely price versus cash generation: a 4.70% OE yield on a generous TTM base for a cyclical.
- Risks to this (bearish-on-price) view: a genuine, sustained truckload capacity exit could hand intermodal pricing power for several years; the Q2 2026 volume record and cost program could compound longer than the fade assumes. Those are the bull/super-bull cases — together only 25% weight, and even they do not clear 15% at this price.
- Hurdle price: the weighted IV@15% is $85.88 — the stock clears Andrew's 15% hurdle only at or below that level on these inputs, i.e. the current $230.00 price would need to fall by roughly two-thirds; a buyer demanding a margin of safety below the weighted IV would need a lower entry still. No margin of safety exists at the current price under any scenario in the table.

## Final verdict
- **Final tier: D** (weighted IRR 7.20% on the TTM base; Tier D on every defensible base, and even the super-bull case at 12.68% fails the 15% hurdle)
- Confidence: **Medium** (high on the filing-derived OE figures, low on any single freight-cycle path — scenario spread 4.78x)
- One-liner: High-quality intermodal leader, moat 6/10, but priced for a supercycle — weighted IRR 7.2%, IV@15 $85.88 vs $230.00 price; clears 15% only at or below $85.88.
