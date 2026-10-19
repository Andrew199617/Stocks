# NYT — The New York Times Company
Engine 5.4.0 run, 2026-10-18. In scope (market cap $11.180B at $67.78, nasdaq_quote_api).

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.json or fundamentals.json — none are recomputed. Balance-sheet and quarter facts are from the FY2025 10-K / Q4 2025 release and the Q2 2026 release as cited.

## What it is
Subscription-first digital publisher: the core news product bundled with Games (Wordle), Cooking, Wirecutter and The Athletic, plus a declining print business. Q2 2026: 13.35M total subscribers, 12.80M digital-only, +280k net digital adds in the quarter; total revenue $762.5M, +11.2% YoY; digital-only subscription revenue +16.4%; digital-only ARPU $9.94 (+3.1% YoY). Q3 2026 guidance: digital-only subscription revenue +12–15%, adjusted operating costs +8–9%.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $584,489,000; SBC $74,183,000 (always a real cost); capex $33,984,000.
- **Conservative owner's earnings FY2025: $476,322,000 = $2.89/share** (key_numbers.md: latest FY OE/share $2.89, latest FY OE total $476.3M)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC, financials_history.csv): $412,422,000 — same ballpark, below the conservative figure, so the base is not flattered by the choice of definition.
- OE positive 5 of the last 5 fiscal years. Share count is shrinking slowly (share count CAGR −0.44%/yr; buybacks TTM $174,560,000 and dividends paid TTM $126,267,000 per fundamentals.json).
- FY2025 OCF quality caveat (Q4 2025 release): 2025 operating cash flow was helped by lower cash tax payments due to the One Big Beautiful Bill Act and included ~$33M of net proceeds from the lease and subsequent sale of excess land at the College Point printing facility (finalized February 2025). Those are not run-rate cash flows — one reason the bear weight was widened and confidence is low.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $584,489,000 − prior YTD $212,726,000 + current YTD $286,500,000 = **TTM $658,263,000**
- Capex: FY $33,984,000 − prior YTD $19,573,000 + current YTD $20,834,000 = **TTM $35,245,000**
- SBC: FY $74,183,000 − prior YTD $35,156,000 + current YTD $39,262,000 = **TTM $78,289,000**
- Shares (current-YTD weighted diluted): **163,374,000**
- **TTM OE total $544,729,000 → base OE/share $3.33** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $1.89/share — rejected as the base; see BASE_DIVERGENCE under Flags. It is still reported in key_numbers.md.
- TTM flattery note: the TTM window inherits part of the OBBBA cash-tax benefit, and management noted H1 2026 free cash flow benefited from working-capital timing expected to reverse in H2. The TTM base is the most current filing-derived figure, but it is not a clean run-rate — handled via the widened bear weight (30%) and low confidence, not by hand-adjusting the base.

## Balance sheet (DEBT_TAGS_BLANK resolution — from the filing, not the engine)
Per the FY2025 10-K consolidated balance sheet (December 31, 2025): cash and cash equivalents $255,445,000; short-term marketable securities $386,712,000; long-term marketable securities $525,695,000 — about $1.17B of cash and marketable securities. Per the Q4 2025 release: as of December 31, 2025 there were **no outstanding borrowings** under the $400M unsecured revolving credit facility and **the Company did not have other outstanding debt**. The only lease figure the engine carries is operating lease liabilities of $48,721,000. The blank debt tags are a tagging artifact: NYT is genuinely debt-free with a large net cash position. The engine's net debt is null (shown as — in key_numbers.md) and no leverage adjustment is made either way.

## Moat: 6/10 — moderate-strong, not wide
Justification: brand trust plus the multi-product bundle creates real habit and switching friction at 13.35M subscribers, with proven price step-ups; but ROIC is mid-teens, not wide-moat through a cycle, and discovery is hostage to search/AI platforms.
- Evidence (fundamentals.json): **ROIC proxy** 16.7% (2021), 10.8% (2022), 14.4% (2023), 15.6% (2024), 18.4% (2025) — above the cost of capital and rising, but the cycle range (and 9.8% back in 2016) is mid-teens, not the sustained 20%+ of a wide moat. The filing tags do not yield a clean gross margin for recent years (fundamentals.json gross_margin is null from 2020 on — costs are not split that way), so the margin evidence used is **operating margin**: 8.7% (2022) → 11.4% (2023) → 13.6% (2024) → 15.3% (2025) → 16.0% TTM — steady expansion, consistent with pricing power plus fixed-cost leverage, not with a cost moat.
- FOR: scarce trusted news brand; the bundle (News + Games + Cooking + Wirecutter + Athletic) builds daily habit and lowers churn; direct paid relationship at scale — 13.35M total subscribers, 12.80M digital-only (Q2 2026); proven pricing power — digital-only ARPU $9.94, +3.1% YoY in Q2 2026, on promo step-ups and tenured price increases; journalism cost spread over millions of subscribers, with operating margin expanded as above.
- AGAINST: AI answers and search-referral erosion threaten discovery, and the new-subscriber funnel depends on platforms NYT does not control; news is partially substitutable and attention competition is intense, the US subscriber pool eventually saturates, and bundle adds dilute ARPU; print is in structural decline with legacy costs attached; content and video investment keeps adjusted costs growing 8–9%, and the OpenAI/Microsoft litigation is expensive — a fair-use loss would also weaken AI licensing leverage across the industry.
- A 6 gives CAP = 9.8 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 9.8 years, 15-year projection.

## DCF — final run (2026-10-18)
Growth sanity check (written, per spec): the engine blend is 9.87% (components: rev CAGR 5y 9.61%, rev CAGR 3y 6.96%, latest rev YoY 9.24%, OE/share CAGR 2y 29.95%). Recent prints: FY2025 revenue +9.24%, Q2 2026 revenue +11.2%, TTM revenue +10.8% (fundamentals.json), while OE/share printed far faster (FY2025 $2.89 vs FY2024 $1.89; TTM OE/share $3.33) on margin expansion plus the non-recurring OBBBA tax benefit and land proceeds above. The base growth start of 9.9% is therefore set at the *revenue* growth rate, deliberately below the recent OE/share prints: margin expansion from an 8.7% base cannot repeat at the 2023–25 pace with costs guided to +8–9%, and the tax/land tailwinds do not recur. Bull (14.9%) and super bull (21.9%) carry the continued-margin-expansion cases and bracket the recent operating-income growth rate. Probabilities were adjusted from the 10/25/30/25/10 defaults to 10/30/30/20/10 — bear widened per the OE_VOLATILE flag and the flattered TTM base. OE multipliers are the defaults 0.75/0.90/1.00/1.10/1.25. Price $67.78.

| Scenario | Prob | Growth start | OE mult | IV@15 | IV@12 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -2.1% | 0.75 | $16.69 | $21.62 | 5.39% |
| Bear | 30% | 4.9% | 0.9 | $27.34 | $36.25 | 7.65% |
| Base | 30% | 9.9% | 1.0 | $37.94 | $51.08 | 9.80% |
| Bull | 20% | 14.9% | 1.1 | $52.09 | $71.11 | 12.41% |
| Super bull | 10% | 21.9% | 1.25 | $80.54 | $111.91 | 16.90% |

- **Probability-weighted: IV@15% $39.73 (−41.4% vs price), IV@12% $53.77, IV@10% $69.57, weighted IRR 10.18%, base-case IRR 9.80%**
- **Tier by numbers: C.** Bear tier D (7.65%), bull tier C (12.41%) — even the bull case does not clear 15%; only the 10%-weight super bull does.
- Hurdle-clearing prices (weighted path): 15% at $39.73 · 20% at $27.28 · 25% at $20.55.
- Diagnostics (key_numbers.md): OE yield 4.92%, terminal value 20.7% of IV@15%, scenario spread 4.83x, 9.6 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.6 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, quoted above, with its flattery caveats stated.
- **OE_VOLATILE** (OE/share spans >3x over 5 years: $1.26 in 2021, $0.47 in 2022, $1.71 in 2023, $1.89 in 2024, $2.89 in 2025): the 2022 trough is explained, not cyclical mystery — The Athletic closed February 1, 2022 and was dilutive by design (about $41M of adjusted operating loss in 2022, guided dilutive for ~3 years) into a weak ad market, and OCF fell to $150,687,000 that year. The series since is a recovery-plus-margin-expansion ramp, which is exactly why neither the trough-era median nor the latest print is a clean base. Handled with the TTM base plus bear weight widened to 30% (bull cut to 20%).
- **NI_OCF_DIVERGENCE** (2025 net income $343,981,000 vs OCF $584,489,000): explained by non-cash add-backs — D&A $85,007,000 and SBC $74,183,000 total $159,190,000 — plus the OBBBA lower cash taxes and the ~$33M College Point land lease/sale proceeds noted in the Q4 2025 release, and deferred-tax/working-capital timing. No impairment or tax-deposit one-off was found. The divergence flatters OCF modestly (land + tax items), which is stated in the OE section and reflected in the bear weight; the conservative OE still deducts SBC and capex in full.
- **DEBT_TAGS_BLANK**: resolved in the Balance sheet section above — from the 10-K, NYT held ~$1.17B of cash and marketable securities at December 31, 2025 with no outstanding debt and an undrawn $400M revolver. Net debt is not unknown; the company is net cash. No leverage verdict is needed and none was taken from the engine's null.
- **BASE_DIVERGENCE** (latest FY $2.89 vs 3-yr median $1.89): the median is the distorted figure — $1.89 is FY2024's own OE/share and the 3-year window runs through the Athletic-drag and recovery years (2023: $1.71). The latest FY and TTM figures reflect filed subscriber, ARPU and margin growth (Q2 2026 digital subscription revenue +16.4%; operating margin 15.3% in FY2025, 16.0% TTM). TTM base used; the median is retained in key_numbers.md and in the method range below.
- **WIDE_SCENARIO_SPREAD** (4.83x): real — the outcome range hinges on how long double-digit subscription growth and margin expansion run against AI/platform headwinds. Confidence is capped at low, and the verdict is sized to the conservative end.
- **TIER_BAND** (bear D at 7.65% vs bull C at 12.41%): the whole band sits below the 15% hurdle, so the tier decision is not close on the upside; the position-sizing implication is the bear end (D economics at this price).

## My thoughts / overlay
- Method range: on the engine's normalized median base ($1.89/share) the preliminary run printed a weighted IRR of 6.97% and IV@15% of $22.52 (Tier D); on the TTM base the final run prints 10.18% and $39.73 (Tier C). The defensible range is D to C — under no defensible base does NYT clear 15% at $67.78; it needs roughly $40 on the friendliest (TTM) base.
- Quality is not the debate: debt-free, ~$1.17B of cash and securities, OE positive 5/5 years, mid-teens-and-rising ROIC, a real bundle with demonstrated pricing power. The debate is price: at $67.78 the market is already paying for the bull path (bull IV@15% $52.09 is still below the price; only the 10% super bull at $80.54 sits above it).
- Watch items: AI-search referral trends and the OpenAI/Microsoft case (cost drag now, licensing leverage at stake); subscriber-add deceleration as the US pool matures (Q2 adds of 280k vs 310k in Q1 2026); whether the H2 2026 working-capital reversal and the non-recurring ~$60M OBBBA-related tax benefit management flagged for 2026 pull reported OCF back toward the median path.

## Final verdict
- **Final tier: C** (weighted IRR 10.18% on the TTM base; method range D to C; bear-to-bull band D to C — size to the bear end)
- Confidence: **Low** (WIDE_SCENARIO_SPREAD 4.83x, TTM base flattered by non-recurring tax/land/working-capital items, tier band spans D–C)
- One-liner: High-quality debt-free subscription compounder, moat 6/10 — but at $67.78 the weighted IRR is only 10.2% (IV@15% $39.73); it does not clear 15% until ~$40, and the bear-to-bull band (D to C) says size to the bear end.
