# PINS — Pinterest, Inc.
Engine 5.4.0 run, 2026-10-18. Price $21.91 (nasdaq_quote_api); market cap $15.069B; in scope under $40B. All figures below are copied from dcf_numbers.json, ttm.json, financials_history.csv, or fundamentals.json — none are recomputed.

## What it is
Visual discovery and search platform monetized almost entirely by advertising: 640 million global MAUs in Q2 2026 (11th straight quarter of double-digit user growth, record users), built around high-commercial-intent visual search (management cites 80B+ searches/month, >96% unbranded) and the AI "Taste Graph" trained on human curation. Q2 2026 revenue $1,180M, +18% YoY; Q3 2026 guidance +13–15% — growth is decelerating into the mid-teens. Gen Z is the fastest-growing cohort. New monetization pushes: Performance+ AI ad suite and Visual Search Ads (beta, announced Sept 2026).

## Owner's earnings
**FY2025 (10-K via EDGAR, financials_history.csv):** operating cash flow $1,284,264,000; SBC $880,463,000 (always a real cost — here it is 69% of OCF); capex $32,375,000.
- **Conservative owner's earnings FY2025: $371,426,000 = $0.54/share** (latest FY OE/share in dcf_numbers.json).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $246,047,000 — same order, lower; the OCF-based figure is the cleaner one.
- OE positive 3 of the last 5 fiscal years (negative in the 2022–23 SBC-heavy reset years on the normalized series).
- Balance sheet (FY2025, fundamentals.json / financials_history.csv): cash $969,342,000 plus short-term investments $1,497,811,000 against total liabilities of only $746,894,000 and equity $4,745,238,000 — a net-cash company with no borrowings; the only debt-like item is operating lease liabilities of $262,018,000 (dcf_numbers.json).

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $1,284,264,000 − prior YTD $571,399,000 + current YTD $620,908,000 = **TTM $1,333,773,000**
- SBC: FY $880,463,000 − prior YTD $414,660,000 + current YTD $555,963,000 = **TTM $1,021,766,000**
- Capex: FY $32,375,000 − prior YTD $18,299,000 + current YTD $39,293,000 = **TTM $53,369,000**
- Shares (current-YTD weighted diluted): **599,629,000** — down sharply from the FY2025 count of 687,771,000 after >$2B of buybacks year-to-date in 2026 (fundamentals.json: buybacks TTM $2,724,273,000)
- **TTM OE total $258,638,000 → base OE/share $0.4313** (base_source: ttm_json)
- Why TTM over the alternatives: the engine's normalized base (3-yr median) is $0.2494/share — distorted downward, it is the FY2024 value sitting between a negative FY2023 (−$0.06/share) and the FY2025 inflection. The latest FY figure ($0.54/share) is distorted the other way against the current run-rate: TTM OE total is *lower* than FY2025 despite higher OCF, because SBC surged to $1,021,766,000 TTM (77% of TTM OCF). The TTM base is the current, filing-derived figure and is the conservative choice versus the latest FY.

## Moat: 5/10 — moderate/narrow
Justification: a genuinely differentiated commercial-intent dataset and audience, but returns on capital have only just turned positive and monetization outside UCAN remains a fraction of potential — no through-cycle proof of durable pricing power.
- Evidence first (fundamentals.json): gross margin is high and rising — 79.5% (2021), 75.8% (2022), 77.5% (2023), 79.4% (2024), 80.1% (2025). The ROIC proxy tells the harder story: +19.9% (2021), −4.8% (2022), −5.7% (2023), +3.9% (2024), +7.9% (2025) — negative through the last downturn and still only around the cost of capital in the best recent year. A moat above 5 would need ROIC sustained well above the cost of capital; Pinterest has not shown that yet.
- FOR: Taste Graph / human-curation dataset behind 80B+ monthly searches with explicit commercial intent (planning and purchase intent, not passive scrolling); 640M MAUs with 12 consecutive record quarters and Gen Z momentum; ~80% gross margin ad economics; Performance+ and Visual Search Ads extending monetization into lower-funnel placements.
- AGAINST: ROIC negative in 2022–23 and only ~8% in 2025 — pricing power unproven through a cycle; huge unclosed monetization gap (Q2 2026 ARPU: UCAN $8.30 vs Europe $1.35 vs Rest of World $0.23) that has closed slowly for years; users and advertisers multi-home — Meta, Google Lens, TikTok and Amazon can and do replicate visual search; SBC consuming 77% of TTM OCF means the talent cost of staying relevant eats most of the cash the franchise generates.
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — 5.4 final run (2026-10-18)
Growth sanity check (mandatory): the engine's blended start is 14.7% (rev CAGR 5y 20.06%, 3y 14.63%, latest FY YoY +15.79%, share-count adjusted). Against actual prints — FY2025 revenue +15.8%, Q2 2026 +18%, Q3 2026 guided +13–15% — the base start of 14.7% sits inside the guided range, no recalibration needed. The bear start (9.7%) is a real deceleration case; the bull start (19.7%) sits slightly *above* the latest print (18%) and is written as the bull case it is: it requires Performance+/visual-search-ads acceleration, not continuation. The super-bull start (26.7%) is a re-acceleration tail at 10% probability only. Default offsets (−12/−5/0/+5/+12pp) and OE multipliers (0.75/0.90/1.00/1.10/1.25) and default probabilities (10/25/30/25/10) were kept — the evidence does not justify skewing them. Price $21.91.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | 2.7% | 0.75 | Ad budgets rotate to Meta/TikTok; growth stalls to terminal early | $2.67 | 4.03% |
| Bear | 25% | 9.7% | 0.90 | Guided deceleration extends; international ARPU gap stays shut | $4.29 | 5.13% |
| Base | 30% | 14.7% | 1.00 | Mid-teens growth decays normally over the CAP | $5.85 | 6.19% |
| Bull | 25% | 19.7% | 1.10 | Performance+ / visual search ads re-accelerate monetization | $7.88 | 7.52% |
| Super bull | 10% | 26.7% | 1.25 | Pinterest becomes a default commerce-search budget line | $11.84 | 9.93% |

- **Probability-weighted: IV@15% $6.25 (−71.5% vs price), IV@12% $8.51, IV@10% $11.06, weighted IRR 6.48%, base-case IRR 6.19%**
- **Tier by numbers: D — and D in every scenario** (bear tier D, bull tier D; even the super bull IRR of 9.93% does not reach Tier C). Diagnostics (dcf_numbers.json): OE yield 2.0%, terminal value 21.3% of IV@15%, scenario spread 4.43x, 9.6 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.6 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, legs quoted above.
- **BASE_DIVERGENCE** (latest FY $0.54 vs 3-yr median $0.25): both are distorted, in opposite directions — the median is the FY2024 value from a pre-inflection window that includes negative FY2023; the latest FY overstates the current run-rate because TTM SBC ($1,021,766,000) has since surged past the FY2025 figure ($880,463,000), cutting TTM OE total to $258,638,000. TTM base used; both figures retained here for the record.
- **NI_OCF_DIVERGENCE** (2023, 2024, 2025): explained, and it does not contaminate the OCF-based base. 2023: net loss −$35,610,000 vs OCF $612,961,000 — the gap is non-cash SBC of $647,860,000 (plus a $117,315,000 lease impairment in the reconciliation). 2024: net income $1,862,106,000 vs OCF $964,594,000 — net income was inflated by the $1,597M release of the valuation allowance on deferred tax assets (a non-cash tax benefit; deferred income taxes −$1,600,434,000 in the cash-flow reconciliation; FY2024 operating income was only $179,817,000). 2025: net income $416,855,000 vs OCF $1,284,264,000 — again SBC ($880,463,000). In every year the divergence is SBC or the one-off tax release, which is exactly why the conservative OCF-minus-SBC base is the right series.
- **SHARES_FALLBACK** (2018): no diluted count filed for 2018 — that history year uses the basic/outstanding count; per-share history there is approximate. It does not touch the TTM base or any of the last-5-year figures the verdict rests on. Noted also: the diluted count fell from 687,771,000 (FY2025) to 599,629,000 (current YTD) on >$2B of 2026 buybacks — ttm.py's current-YTD share basis already reflects the retired shares.
- **DEBT_TAGS_BLANK**: resolved from the filing (see Owner's earnings): no debt tags exist because there are no borrowings — FY2025 shows cash $969,342,000 + short-term investments $1,497,811,000 vs total liabilities $746,894,000; the only debt-like obligation is operating leases of $262,018,000. Net cash, no leverage verdict needed beyond that.
- **LOW_OE_YIELD** (2.0% on the TTM base): real — at $21.91 the valuation rests almost entirely on growth that must survive both SBC and the fade. This is a core reason the tier is fragile in level even though the D conclusion is robust (every scenario is D).
- **WIDE_SCENARIO_SPREAD** (4.43x): real — the IV level is assumption-dominated. Confidence is capped below high; the verdict is sized to the conservative end. The *tier* is not in doubt (all five scenarios are D); the *gap* between price and IV is what is wide.

## My thoughts / overlay
- The story in one line: Pinterest's free cash flow looks rich (TTM FCF $1,280,404,000 per fundamentals.json) until SBC is treated as the real cost it is — $1,021,766,000 TTM — leaving owner's earnings of $258,638,000 on a $15.07B market cap. The market is pricing the FCF; this method prices what's left after paying the engineers.
- Method range: on the engine's normalized median base ($0.2494/share) the preliminary run printed weighted IV@15% $3.61 and weighted IRR 4.86%; on the TTM base, $6.25 and 6.48%; even on the most generous defensible base (latest FY $0.54/share, not run as final) the weighted IV would scale to roughly the high-single digits — every defensible method lands in Tier D at $21.91. The range changes the size of the overvaluation, not the verdict.
- What would have to be true: sustained >20% OE/share growth for a decade, or a step-change in international ARPU, or SBC falling sharply as a share of OCF. Q2 2026 showed the opposite SBC direction (TTM SBC up vs FY2025) and guided revenue deceleration — none of the three is in the current prints.
- Buybacks are genuinely shareholder-friendly here (>$2B YTD 2026 at prices averaging well below today's) and shrink the count ~1.1%/yr on the engine's share CAGR — already credited in the blend's share-count adjustment; not double-counted.

## Final verdict
- **Final tier: D** (weighted IRR 6.48% on the TTM base; D in all five scenarios, super bull included at 9.93%)
- Confidence: **Medium** (high on the filing arithmetic and the SBC/tax one-off resolutions; the IV level is spread-dominated at 4.43x, but the tier conclusion is robust across every scenario and every defensible base)
- One-liner: Real commercial-intent franchise, moat 5/10, but SBC eats 77% of TTM operating cash flow — at $21.91 it returns 6.5% weighted and only clears the 15% hurdle below $6.25.
