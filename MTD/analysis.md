# MTD — Mettler-Toledo International Inc.
v5 run, 2026-10-14. In scope: market cap $33.362B at $1,613.91 (nasdaq_quote_api), under the $40B cutoff.

All figures below are copied from key_numbers.md, dcf_numbers.json, or ttm.py output — none are recomputed.

## What it is
Precision instruments for laboratory, industrial, and food-retailing applications: laboratory balances and analytical instruments (the largest segment), industrial weighing and product inspection, and retail weighing. Sold with a large direct service network; service is a recurring, sticky part of the mix. Q2 2026 (reported 2026-07-30): revenue $1.03B, +4.5% year over year (+6% in local currency), adjusted EPS $11.46, +13.6% year over year; management raised FY2026 adjusted EPS guidance to $47.15–$47.50 and guided local-currency sales growth of 4%–5%. China local-currency sales grew 9% in the quarter. Note on quality: the Q2 GAAP result included a tariff-related benefit (reported as $0.92/share and a $52.4M tariff refund in secondary coverage) — part of the recent EPS strength is one-off, not run-rate.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $955,772,000; capex $107,124,000 (tag: PaymentsToAcquirePropertyPlantAndEquipment); SBC $22,512,000 (tag: ShareBasedCompensation, always a real cost).
- **Conservative owner's earnings FY2025: $826,136,000 = $39.96/share latest FY** (key_numbers.md).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $849,047,000 in FY2025 from financials_history.csv — same ballpark as the conservative figure, which raises confidence.
- OE positive 5 of the last 5 fiscal years. Net debt $2.152B (key_numbers.md), 2.51x normalized OE — moderate leverage for a business this stable; it is folded into the verdict below and is not a distress factor, but it also offers no offset to the valuation gap.
- SBC is small relative to OCF — dilution is not the story here; buybacks are (see BUYBACK_TAILWIND).

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $955,772,000 − prior YTD $430,815,000 + current YTD $450,210,000 = **TTM $975,167,000**
- Capex: FY $107,124,000 − prior YTD $41,132,000 + current YTD $45,206,000 = **TTM $111,198,000**
- SBC: FY $22,512,000 − prior YTD $10,521,000 + current YTD $10,840,000 = **TTM $22,831,000**
- Shares (current-YTD weighted diluted): **20,251,532**
- **TTM OE total $841,138,000 → base OE/share $41.53** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $39.61/share. The TTM base is used because it is more current (STALE_FY) and modestly higher; the choice does not drive the verdict — even the higher base leaves every scenario except super bull in single-digit IRR.
- Caveat stated in words, not recomputed: if part of the Q2 tariff refund flowed through TTM operating cash flow, the TTM base is slightly flattered. The gap to the price is so large that this cannot change the tier.

## Moat: 7/10 — strong
Justification: global leader in laboratory balances with >50% share and ~25% average share across most other product lines, instruments embedded in validated QC/research workflows with high re-validation switching costs, proven pricing power, a large direct service network with recurring service revenue, and high returns on capital held through cycles. Not 9–10: most lines beyond balances are competitive, end markets grow slowly, and lower-cost/Chinese rivals pressure the low end.
- FOR: >50% share in laboratory balances, ~25% average share in most other lines; high switching costs — instruments in validated workflows, costly to re-validate; proven pricing power and premium brand in precision instruments; large direct service network, service a recurring sticky stream; integrated software/automation ecosystem deepening installed-base stickiness; high returns on capital and ~30% operating margins held through cycles.
- AGAINST: beyond balances, competitive markets vs Thermo Fisher, Agilent, Waters, Sartorius; slow-growing end markets limit organic growth to mid-single digits; lower-cost and Chinese local competitors at the low end; biopharma/lab capex cyclicality and China/tariff exposure; growth increasingly reliant on buybacks rather than organic acceleration.
- A 7 gives CAP = 11.1 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 11.1 years, 15-year projection.

## DCF — v5 final run (2026-10-14)
Sanity check against recent prints: the engine's blended growth is 3.03%, adjusted to g_base 6.13% for the −3.10%/yr share-count trend. That 6.1% OE/share base start sits above the revenue prints (latest FY revenue YoY 3.98%, Q2 2026 revenue +4.5% reported / +6% local currency, FY2026 guided local-currency sales growth 4%–5%) — defensible only because OE/share, unlike revenue, benefits directly from the buyback already credited in g_base. Bull (11.1%) and super-bull (18.1%) starts are above every revenue print; they are upside cases requiring adjusted-EPS-style growth like Q2's +13.6% (itself flattered by the tariff benefit) to persist, which is why they carry only 25%/10% weight. Defaults kept throughout: probabilities 10/25/30/25/10, offsets −12/−5/0/+5/+12pp, OE multipliers 0.75/0.90/1.00/1.10/1.25. Price $1,613.91.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -5.9% | 0.75 | Lab/biopharma capex downturn; China and tariff pressure bite | $172.70 | 3.62% |
| Bear | 25% | 1.1% | 0.90 | Slow end markets; growth is buyback only | $287.33 | 4.67% |
| Base | 30% | 6.1% | 1.00 | Guided 4–5% local sales growth plus buyback tailwind | $404.26 | 5.79% |
| Bull | 25% | 11.1% | 1.10 | Automation/biopharma demand accelerates; pricing holds | $563.80 | 7.28% |
| Super bull | 10% | 18.1% | 1.25 | Sustained double-digit EPS compounding | $893.67 | 10.08% |

- **Probability-weighted: IV@15% $440.70 (−72.7% vs price), IV@12% $593.09, IV@10% $764.27, weighted IRR 6.19%, base-case IRR 5.79%**
- **Tier by numbers: D.** Diagnostics (key_numbers.md): OE yield 2.57%, terminal value 20.2% of IV@15%, scenario spread 5.17x, net debt 2.51x normalized OE, 9.4 months since FY end.
- The decisive fact: even the super-bull scenario — 18.1% growth start, 1.25x OE multiplier, 10% weight — returns only 10.08% IRR at this price. There is no defensible scenario set in which MTD clears 15% at $1,613.91.

## Flags — every fragility flag resolved
- **STALE_FY** (latest fiscal year ended 9.4 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, quoted above with all four legs (OCF, capex, SBC, shares).
- **BUYBACK_TAILWIND** (share count shrinking 3.1%/yr): already credited via the +3.10pp growth adjustment in g_base; not double-counted in the verdict. It is also the main engine of recent per-share growth — revenue CAGR is only 5.47% over 5 years and 0.90% over 3 years — which is why the base growth start is not set any higher.
- **WIDE_SCENARIO_SPREAD** (super-bull IV 5.17x super-bear IV): real, and driven mostly by the low super-bear denominator at this OE yield. Confidence is capped at medium. The verdict is nonetheless robust to the spread: the entire scenario range sits below the 15% hurdle, including super bull.

## My thoughts / overlay
- This is a quality-versus-price result, not a quality dispute. The franchise is elite — dominant share in its core line, pricing power, recurring service, 5/5 positive OE years, conservative and maintenance OE definitions in the same ballpark. The stock simply prices in far more than the owner's earnings can deliver: a 2.57% OE yield at $1,613.91 leaves no margin of safety under any scenario run.
- Method range: using the lower normalized median base ($39.61) instead of TTM ($41.53) would lower every IV further; using TTM was the generous choice and the tier is still D. The defensible range is D under both bases — no tier-spanning method range to report.
- Balance sheet: net debt $2.152B at 2.51x normalized OE is manageable given the stability of the OE stream; it neither rescues nor worsens the verdict materially.
- Risks to the (already low) case: a lab/biopharma capex downturn, China exposure, tariff costs reversing the Q2 refund benefit, and low-end share loss. Risks to the bearish-on-price view: a large price correction, or a genuine organic growth re-acceleration — neither is in the current prints (guidance is 4%–5% local-currency sales growth).
- Hurdle-clearing price: the weighted IV@15% is $440.70 — that is the price at which the weighted case clears 15%, before any additional margin of safety. A buyer demanding a margin of safety against the bear cases would need a price below even that.

## Final verdict
- **Final tier: D** (weighted IRR 6.19% on the v5 final inputs; no tier override)
- Confidence: **Medium** (capped by WIDE_SCENARIO_SPREAD; high on the direction — no scenario clears the hurdle — medium on any single IV figure given the 5.17x spread)
- One-liner: Elite precision-instruments franchise, moat 7/10, but priced far beyond its owner's earnings — weighted IRR 6.19% (Tier D) at $1,613.91, weighted IV@15% $440.70; clears 15% only near $441.
