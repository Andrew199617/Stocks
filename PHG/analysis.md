# PHG — Koninklijke Philips N.V. (Royal Philips)
v5 run, 2026-10-15. In scope: market cap $24.236B at $25.18 (nasdaq_quote_api) — under the $40B cutoff. Dutch health-technology company filing on Form 20-F under IFRS in EUR; the engine converted EUR to USD at period-end ECB rates (see FX_CONVERTED). NYSE shares are New York Registry Shares, 1 = 1 common share (see ADS flag).

All figures below are copied from dcf_numbers.json or financials_history.csv — none are recomputed.

## What it is
One of the big three in hospital health technology: Diagnosis & Treatment (diagnostic imaging, image-guided therapy / Azurion, ultrasound), Connected Care (hospital patient monitoring, plus the sleep & respiratory business impaired by the Respironics recall), and Personal Health (consumer appliances). Sales are roughly flat in EUR over the decade; 2026 guidance is 3–4.5% comparable sales growth (Q2 2026 printed +4% comparable), with the recovery story resting on margin/productivity rather than volume growth.

## Owner's earnings
**FY2025 (20-F via EDGAR, USD-converted, from financials_history.csv):** operating cash flow $1,377,100,000; capex $316,075,000; SBC $165,675,000 (always a real cost).
- **Conservative owner's earnings FY2025: $895,350,000 = $0.93/share** (dcf_numbers.json: base_oe_latest_per_share $0.9302)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $1,111,010,100 — above the conservative figure, mainly because FY2025 net income carries non-cash Respironics-era charges while the settlement cash had already left through OCF.
- OE positive 4 of the last 5 fiscal years (2022 was negative on the recall collapse). Net debt $6,154,650,000 = 5.0x normalized OE — the balance sheet is part of the verdict, not a footnote.
- **Base used = normalized base, median of last 3 FY OE/share = $1.2867/share.** The latest FY ($0.93) is the distorted year: FY2025 operating cash flow absorbed the cash payment of the ~$1.1B Respironics personal-injury/medical-monitoring settlement (provisioned in Q1 2024, paid in 2025), so the median is the cleaner base. No TTM pin: ttm.py reads us-gaap facts only and exited 3 for this IFRS filer ("ocf: no annual (FY) fact; sbc: no annual (FY) fact; shares_diluted: no annual (FY) fact; capex: no capex facts in companyfacts under any candidate tag and no capex_override in judgment.json") — expected for an ifrs-full filer, so the engine's median base stands, per the sweep spec.

## Moat: 5/10 — moderate / narrow
Justification: a top-3 global position in diagnostic imaging, image-guided therapy and hospital patient monitoring with a large installed base, multi-year service contracts and regulatory-clearance barriers — but GE HealthCare and Siemens Healthineers contest every category, hospital capex is cyclical and price-competitive, the Respironics consent decree bars Philips from the US sleep-therapy device market until FDA conditions are met, and a decade of flat comparable growth shows limited pricing power.
- FOR: Top-3 global franchise in diagnostic imaging, image-guided therapy (Azurion) and hospital patient monitoring, with a large installed base; installed base drives recurring service, parts and software revenue and real switching costs for hospital platforms; regulatory clearances and clinical validation are genuine entry barriers in imaging and monitoring; scale R&D and AI imaging pipeline (e.g. SmartIQ for Azurion) plus a record equipment order backlog.
- AGAINST: GE HealthCare and Siemens Healthineers match Philips category by category; no durable technology gap; Respironics recall fallout: FDA consent decree restricts US sleep/respiratory device sales, DOJ investigation still open, ~$1.1B personal-injury settlement paid in 2025; hospital capital budgets are cyclical and price-competitive; China health-system demand is weak; a decade of roughly flat comparable sales (2026 guide only 3–4.5%) shows weak pricing power; net debt 5.0x normalized owner's earnings leaves little room for another recall-scale shock.
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — v5 final run (2026-10-15)
Default scenario structure retained — the evidence does not justify skewing it: probabilities 10/25/30/25/10, growth offsets −12/−5/0/+5/+12pp vs the engine's blended growth (g_base 1.14%), OE multipliers 0.75/0.90/1.00/1.10/1.25. Sanity check against actual prints: the base start (1.1%) sits below the 3–4.5% comparable-sales guide deliberately — the guide is nominal sales, while the OE base is the post-settlement normalized median and OE growth is not sales growth; the recovery case lives in the bull (6.1%) and super-bull (13.1%) starts, which are consistent with settlement outflows rolling off and with Q2 2026's profit rebound (itself flattered by a one-off US tariff refund — see Flags/Thoughts), and no scenario start contradicts a recent print. Note the engine's +11.93% latest revenue YoY is a USD-conversion artifact (the EUR/USD period-end rate moved from 1.0389 to 1.175), not real growth — EUR comparable growth is low-single-digit, which is what the scenario starts are anchored to. Price $25.18.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -10.0% | 0.75 | New quality/litigation shock lands on a 5.0x-levered OE stream | $4.69 | 4.47% |
| Bear | 25% | -3.9% | 0.90 | Consent-decree drag and China weakness persist; OE erodes | $7.28 | 5.88% |
| Base | 30% | 1.1% | 1.00 | Guided low-single-digit growth, normalized post-settlement OE | $9.97 | 7.40% |
| Bull | 25% | 6.1% | 1.10 | Settlement outflows roll off; productivity program lifts OE | $13.50 | 9.33% |
| Super bull | 10% | 13.1% | 1.25 | Full OE recovery plus imaging/monitoring share gains | $20.46 | 12.85% |

- **Probability-weighted: IV@15% $10.70 (−57.5% vs price), IV@12% $14.11, IV@10% $17.91, weighted IRR 7.85%, base-case IRR 7.40%**
- **Tier by numbers: D.** Diagnostics (dcf_numbers.json): OE yield 5.11%, terminal value 18.05% of IV@15%, scenario spread 4.37x, net debt 4.97x normalized OE, 9.46 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.46 months ago): ttm.py cannot run for this IFRS filer (exit 3, message quoted under Owner's earnings), so no TTM pin exists and the median base is used, as the spec directs. Post-FY evidence checked instead: Q2 2026 (company report, July 27, 2026) printed +4% comparable sales growth, reiterated the 3–4.5% FY2026 comparable-growth outlook, and raised adjusted EBITA/free-cash-flow outlooks only to reflect a one-off US tariff refund — consistent with the normalized base, not with a step-change in OE.
- **NI_OCF_DIVERGENCE** (2023, 2024): identified — the Respironics provisions. Net income was −$511,615,000 (2023) and −$725,152,200 (2024) while OCF stayed positive at $2,360,280,000 and $1,630,034,100 (financials_history.csv) because the charges that crushed net income were non-cash provisions (€575M economic-loss provision in Q1 2023; €982M personal-injury provision in Q1 2024, partly offset by €540M of insurance income recognized in 2024). The cash left later — FY2025 OCF absorbed the settlement payments, which is exactly why the latest-FY OE/share ($0.93) is below the median base ($1.29) and why the OCF-based series, not net income, is the right OE input.
- **FX_CONVERTED**: Philips reports in EUR; the engine converted all fields to USD at period-end ECB reference rates (frankfurter.app), flows at the period-end rate rather than a period average — a documented simplification. The 2025 rate was 1.175 vs 1.0389 for 2024, which inflates USD growth rates (the +11.93% revenue YoY is mostly FX); scenario growth starts were anchored to EUR comparable growth instead.
- **ADS_RATIO_APPLIED (x1.0)**: judgment.json declares ads_ratio 1.0 under bounded authority — Philips' Form 20-F (Exhibit 2, Description of Securities, CIK 313216) registers the NYSE-traded class itself as "Common Shares — par value EUR 0.20 per share" under symbol PHG; the New York Registry Shares are those common shares held in registered form, so per-share figures and the $25.18 price are on the same basis and no scaling applies.
- **WIDE_SCENARIO_SPREAD** (4.37x): real — the range runs from another quality shock on a levered base to a full post-settlement OE recovery. Confidence is capped at medium and the verdict is sized to the conservative end; note even the super-bull IV@15% ($20.46) sits below the $25.18 price.
- **HIGH_NET_DEBT** (net debt 5.0x normalized OE, $6,154,650,000): folded into the verdict — leverage is why the bear cases are graded as harshly as they are and why no benefit of the doubt is given on recovery timing; a levered, low-growth OE stream cannot clear a 15% hurdle at this price.

## My thoughts / overlay
- The market is pricing a recovery the OE stream has not yet delivered: at $25.18 the stock needs more than the super-bull case (12.85% IRR) to clear 15% — every one of the five scenarios fails the hurdle at this price, so the method range does not span the hurdle; it sits entirely below it.
- Quality caveats cut both ways: the FY2025 OE is genuinely depressed by one-off settlement cash outflows, and Q2 2026's headline profit jump leaned on a one-off US tariff refund (€186M in the quarter per the company report). Neither changes the conclusion — crediting the recovery is what the bull/super-bull cases already do.
- Remaining tail risks: the DOJ Respironics investigation is still open and the FDA consent decree keeps Philips out of US sleep-therapy device sales until conditions are met; China demand is weak; order intake dipped 1% in Q2 2026 on order timing.
- Price that clears 15%: the weighted IV@15% is $10.70 — Philips clears Andrew's 15% hurdle only below ~$10.70, roughly 58% under the current price, and even a margin-of-safety buyer gets no help from the scenario table, since the super-bull IV@15% is $20.46.

## Final verdict
- **Final tier: D** (weighted IRR 7.85%; no tier override — the numbers and the overlay agree)
- Confidence: **Medium** (capped by the 4.37x scenario spread; high on the filing data, which is complete under IFRS with no data gap)
- One-liner: Solid health-tech franchise, moat 5/10, but owner's earnings are still depressed by Respironics settlement outflows and net debt is 5.0x normalized OE — at $25.18 it does not clear 15% (weighted IRR 7.85%, weighted IV@15 $10.70); clears 15% only below ~$10.70.
