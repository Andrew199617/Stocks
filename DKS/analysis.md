# DKS — DICK'S Sporting Goods, Inc.
Pass-1 run, 2026-10-18, engine 5.4.0. Price $144.35 (nasdaq_quote_api), market cap est. $12.29B — in scope under $40B.

All figures below are copied from dcf_numbers.json, ttm.json, financials_history.csv or fundamentals.json — none are recomputed.

## What it is
Largest US sporting-goods retailer. Closed the ~$2.5B cash-and-stock acquisition of Foot Locker on September 8, 2025, creating a ~3,195-store global platform. The core DICK'S Business is healthy (Q2 FY2027 comps +4.9%, FY guidance for core comps held at +2.5% to +4.0%); the acquired Foot Locker Business is not (Q2 pro forma comps −3.6%, a $31.9M segment operating loss in the quarter, full-year segment guide cut to a $40–80M operating loss from a previously guided profit). On August 25, 2026 the stock fell ~30% in one session on the Q2 miss and guidance cut (adjusted EPS guide $13.50–14.50 → $11–12); a securities class action over the Foot Locker outlook statements followed (lead-plaintiff deadline November 3, 2026). Up to $750M of pretax Foot Locker acquisition/integration charges are expected, $516M recognized through Q2.

## Owner's earnings
**FY2026 (10-K, period ended 2026-01-31, from financials_history.csv):** OCF $1,537,343,000; capex $1,137,176,000; SBC $123,667,000.
- **Conservative OE FY2026: $276,500,000 = $3.25/share** (latest FY OE/share in dcf_numbers.json).
- Maintenance version FY2026: $388,937,000 (financials_history.csv) — same depressed ballpark.
- OE positive 5 of the last 5 fiscal years, but the per-share series is violently cyclical: $13.80 (FY2021) → $11.46 → $5.11 → $10.27 → $5.28 → $3.25 (FY2026).

**Base used = the engine's normalized base, median of last 3 FY OE/share = $5.28/share** (base_source: median_of_last_3_fy_oe_per_share). That median year is FY2025 — the last clean, pre-Foot-Locker DICK'S-only year.
- **TTM check (ttm.py, through 2026-08-01):** OCF FY $1,537,343,000 − prior YTD $735,641,000 + current YTD $792,274,000 = TTM $1,593,976,000; capex FY $1,137,176,000 − prior YTD $526,076,000 + current YTD $743,470,000 = TTM $1,354,570,000; SBC TTM $139,570,000; shares (current-YTD weighted diluted) 90,269,000 → **TTM OE $99,836,000 = $1.11/share**. The TTM figure was NOT used as the base: it is the trough of a capex surge (House of Sport build-out plus Foot Locker integration capex, TTM capex $1.35B vs $0.59B in FY2024) layered on up to $750M of guided deal charges. But it is not ignored either — it is why the scenario weights are bear-heavy and why the verdict carries a method range (below).

## Moat: 4/10 — weak-to-moderate
- FOR: US scale leader in sporting goods with the buying leverage and vendor allocations (notably Nike) that come with it; House of Sport experiential format and GameChanger youth-sports platform (~$150M revenue scale, ~40% CAGR since 2017 per company commentary) are genuine differentiators; ~30M-member ScoreCard loyalty base and the DICK'S Media Network; core comps +4.9% in Q2 FY2027 while the broader market was promotional — evidence the core franchise takes share.
- AGAINST: the product belongs to the brands — Nike and peers control allocation and sell direct; Amazon and off-price (TJX) pressure price with no structural cost answer; gross margin is thin and falling (35.9% FY2025 → 32.9% FY2026 → 32.1% TTM, fundamentals.json) as promotional footwear and Foot Locker mix dilute it; Foot Locker itself is a mall-based, Nike-dependent asset with negative comps — scale bought at the top of its cycle; ROIC history (roic_proxy in fundamentals.json) is not usable as moat evidence — the proxy prints absurd values in pre-deal years (75–184%) because the filer carries almost no funded debt and a small equity-plus-debt-minus-cash denominator, and the first post-deal year prints 19.5% on a much larger capital base. A 4 does not need the ROIC crutch: this is a well-run retailer, not a franchise with pricing power.
- A 4 gives CAP = 7.2 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 7.2 years, 15-year projection.

## DCF — final run (2026-10-18)
**Growth sanity check (mandatory):** the engine's blended start of 16.99% is an acquisition artifact and was rejected. Its components: latest revenue YoY +28.06% is the Foot Locker consolidation (core comps were +4.5% for FY2026), the 5-yr/3-yr revenue CAGRs (12.42% / 11.62%) straddle the deal, OE/share CAGR 2y is −43.88%, and a +4.97pp share-count adjustment was added even though the diluted count is now RISING (85,144,000 FY2026 → 90,269,000 TTM after 9.6M shares were issued for Foot Locker). Organic reality: core comps guided +2.5% to +4.0%, Foot Locker comps guided −2% to 0%. Scenario starts were therefore set via offsets (−0.19 / −0.15 / −0.11 / −0.07 / −0.02 vs the blended start) to −2 / +2 / **+6** / +10 / +15% — the base 6% credits OE/share recovery as the $750M charge program rolls off and capex normalizes, on top of low-single-digit organic sales growth; the super-bull 15% requires a full Foot Locker turnaround plus synergy delivery ($100–125M medium-term cost savings targeted). Probabilities shifted bear-heavy to 15/30/30/15/10 per the OE_VOLATILE flag; OE multipliers at defaults 0.75/0.90/1.00/1.10/1.25.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | −2.0% | 0.75 | Foot Locker bleeds on; promotional footwear worsens; charges overrun | $27.30 | 4.77% |
| Bear | 30% | +2.0% | 0.90 | Core comps at guide low end; Foot Locker stuck at a small loss | $38.25 | 5.80% |
| Base | 30% | +6.0% | 1.00 | Charges roll off, capex normalizes, core holds share | $49.54 | 6.89% |
| Bull | 15% | +10.0% | 1.10 | Foot Locker reaches breakeven-to-profit; synergies land | $63.40 | 8.20% |
| Super bull | 10% | +15.0% | 1.25 | Full turnaround; consolidated OE/share compounds double-digit | $86.84 | 10.32% |

- **Probability-weighted: IV@15% $48.63 (−66.3% vs the $144.35 price), IV@12% $64.53, IV@10% $82.27, weighted IRR 6.82%, base-case IRR 6.89%**
- **Tier by numbers: D.** Bear and bull tiers are both D (5.80% / 8.20%) — no tier band in the final run. Diagnostics: OE yield 3.66%, terminal value 18.6% of IV@15%, scenario spread 3.18x, 8.5 months since FY end.
- Hurdle prices: clears 15% only at or below $48.63, 20% at $34.31, 25% at $26.42.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 8.5 months ago): ttm.py run and quoted above — TTM OE/share is $1.11, far below the median base. Not used as the base (capex/integration trough, reasoned above), but it caps confidence and drives the bear-heavy weights. This is the single biggest softness in the run: on a TTM base the name would score F-adjacent.
- **BASE_DIVERGENCE** (latest FY $3.25 vs 3-yr median $5.28): BOTH are distorted, in opposite directions. The latest FY is depressed by partial-year Foot Locker losses, deal charges and the capex ramp; the median is a pre-deal DICK'S-only year that excludes a permanently larger, lower-margin consolidated business and a share count ~6% higher. The median was kept as the base because the TTM alternative ($1.11) capitalizes trough capex as if permanent — but the honest read is that normalized consolidated OE/share sits somewhere between $3.25 and $5.28, and every scenario is therefore, if anything, generous.
- **NI_OCF_DIVERGENCE** (2026): FY2026 net income $849,239,000 vs OCF $1,537,343,000 — OCF exceeds net income because the gap is non-cash: D&A of $488,630,000 plus Foot Locker inventory/asset write-downs and integration charges running through earnings (part of the up-to-$750M program). The OCF-based conservative OE used throughout is not flattered by this divergence; if anything the charges depress both legs.
- **OE_VOLATILE** (OE/share spans >3x over 5 years): real retail cyclicality amplified by the deal — handled with bear-heavy probabilities (45% on bear-or-worse) and confidence capped at low.
- **BUYBACK_TAILWIND** (share count −5.0%/yr): historical only, and now REVERSED — 9.6M shares were issued for Foot Locker and the diluted count rose to 90,269,000 TTM. The engine's +4.97pp growth adjustment is one of the artifacts removed by the growth recalibration above; no buyback credit is taken in the verdict. (fundamentals.json: TTM buybacks $184,669,000 vs dividends paid $442,551,000 — the dividend, $1.25/quarter declared, is now the main capital return.)
- **DEBT_TAGS_BLANK**: resolved from the filing-direct data — the filer reports no funded-debt balance for FY2026 (statements.json long-term debt: none; the engine's debt tags are blank because there is essentially no funded debt to tag, consistent with the pre-deal history of near-zero debt). The balance sheet's real fixed obligations are operating leases: lease liabilities $5,841,344,000, against cash $1,353,226,000, equity $5,540,120,000 and total assets $17,411,499,000 (financials_history.csv, FY2026). Lease-adjusted leverage is material for a retailer earning a 0.47% TTM OE margin — noted, and one more reason the verdict sizes to the conservative end.
- **WIDE_SCENARIO_SPREAD / TIER_BAND** (preliminary run only: 4.4x spread, bear D vs bull C): both disappeared in the final run because the recalibrated starts compress the range (final spread 3.18x, bear and bull both D). The uncertainty itself has not shrunk — confidence stays low.

## My thoughts / overlay
- The honest headline is the method range: median base → Tier D (weighted IRR 6.82%); TTM base ($1.11/share) → F territory; even the super-bull scenario only reaches a 10.32% IRR. No defensible base gets this price near the 15% hurdle — the market at $144.35 is paying for a Foot Locker turnaround that has so far produced guidance cuts, a segment loss, $750M of charges and a securities suit.
- The core DICK'S business is genuinely good — +4.9% comps into a promotional market is share-taking. The problem is purely what was bought and what was paid: the consolidated entity's OE margin TTM is 0.47% (fundamentals.json) because capex and charges are eating the cash flow the core generates.
- What would change the verdict: Foot Locker comps back to positive with the charge program actually finished, capex back under ~$800M, and consolidated OE/share printing above the $5.28 median on the higher share count. None of that is in evidence yet.
- Margin of safety: none at this price on owner's earnings — the weighted IV@15% is 66% below it. The stock already fell ~30% in August; the DCF says the de-rating has further to go unless the turnaround lands.

## Final verdict
- **Final tier: D** (weighted IRR 6.82% on the median base; method range D-to-F across defensible bases)
- Confidence: **Low** (STALE_FY with a TTM base 79% below the base used, OE volatility, integration and litigation overhang)
- One-liner: Strong core retailer, moat 4/10, that bought a broken Foot Locker — at $144.35 it does not clear 15% on any defensible base (weighted IRR 6.8%, IV@15% $48.63); it would need to fall to ~$49 to clear the hurdle.
