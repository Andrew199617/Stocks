# GEN — Gen Digital Inc.
Engine 5.4.0 run, 2026-10-17. Market cap $14,955,040,000 at $24.16 (nasdaq_quote_api) — in scope under $40B.

All figures below are copied from dcf_numbers.json, ttm.json, financials_history.csv, or fundamentals.json — none are recomputed.

## What it is
Consumer cyber-safety and trust platform formed by the 2022 NortonLifeLock + Avast merger: Norton, Avast, Avira, LifeLock and CCleaner across antivirus, VPN, identity protection and scam protection, plus MoneyLion (acquired April 2025) — a financial-wellness / Engine marketplace business (110M connected financial accounts at Q1 FY27) that supplies most of the current growth. Asset-light subscription model; capex is trivial ($22M in FY26 against $1,545M OCF). On 2026-09-24 the FT reported a preliminary takeover approach for GoDaddy (~$12B target); GEN fell ~30% from ~$31 over the following sessions. No agreement exists, and RBC (2026-09-29) judged a bid less likely after GEN's 8-K and guidance update, with cash more likely going to buybacks — but the approach is unconfirmed-dead and remains a live capital-allocation overhang on the price used here.

## Owner's earnings
**FY26 (10-K, period ended 2026-04-03, from financials_history.csv):** OCF $1,545,000,000; capex $22,000,000; SBC $237,000,000 (always a real cost).
- **Conservative owner's earnings FY26: $1,286,000,000 = $2.08/share** (619,000,000 diluted shares).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $1,071,000,000 — same ballpark, raises confidence in the OCF-based figure.
- OE positive 5 of the last 5 fiscal years. Net debt $7,794,000,000 (debt $8,196,000,000 vs cash $402,000,000 on the FY26 balance sheet) — the Avast/MoneyLion acquisition debt; the company reported net leverage of 2.95x at Q1 FY27 after repaying $45M in the quarter.

**Base used = TTM owner's earnings through Q1 FY27 (period ended 2026-07-03), from ttm.py (filing-direct, no hand math):**
- OCF: FY $1,545,000,000 − prior YTD $409,000,000 + current YTD $434,000,000 = **TTM $1,570,000,000**
- Capex: FY $22,000,000 − prior YTD $4,000,000 + current YTD $4,000,000 = **TTM $22,000,000**
- SBC: FY $237,000,000 − prior YTD $66,000,000 + current YTD $54,000,000 = **TTM $225,000,000**
- Shares (current-YTD weighted diluted): **603,000,000** — buybacks are shrinking the count (624M in the prior-year YTD period)
- **TTM OE total $1,323,000,000 → base OE/share $2.19** (base_source: ttm_json)
- The engine's normalized base (median of last 3 FY OE/share: FY24 $2.97, FY25 $1.72, FY26 $2.08) is $2.08/share. TTM is used instead because FY26 ended 6.5 months ago and a clean Q1 FY27 10-Q is on file (filed 2026-08-07); the two bases are within ~6% of each other, so the choice is not load-bearing — the method range below shows the median-base result.

## Moat: 5/10 — narrow / moderate
Justification: Norton, Avast and LifeLock give Gen the leading consumer cyber-safety subscription franchise — brand trust, OEM/partner distribution and high retention — but core antivirus commoditizes against free platform offerings, switching costs are low, and MoneyLion's marketplace is a competitive lead-gen business with no real moat. The returns evidence caps the score: post-Avast roic_proxy (fundamentals.json) ran 8.5% (FY23), 8.9% (FY24), 10.6% (FY25), 13.1% (FY26) — improving but only around the cost of capital on the acquisition-swollen capital base, versus 33.0% / 46.8% in FY21–22 pre-Avast. Gross margin is high but eroding with mix: 85.4% (FY22) → 82.2% (FY23) → 80.8% (FY24) → 80.3% (FY25) → 78.5% (FY26), TTM 78.0%, as lower-margin MoneyLion revenue scales (Q1 FY27 non-GAAP gross margin 82.0%, guided down by Engine marketplace mix).
- FOR: category-leading consumer brands (Norton, Avast, LifeLock) in subscription cyber safety with high retention; distribution scale via OEM, ISP and retail partner channels plus ~110M connected financial accounts via MoneyLion; recurring subscription revenue with Cyber Safety segment operating margin of 61% (Q1 FY27); cross-sell working — 35% of the paid customer base now engages with financial-wellness tools.
- AGAINST: free platform competition (Microsoft Defender, Apple/Google built-in security) commoditizes core antivirus; low switching costs and a mature category; ROIC only ~9–13% post-Avast; gross margin drifting down as no-moat MoneyLion mix grows; growth-by-acquisition model (Avast, MoneyLion, reported GoDaddy approach) — the moat is bought, not organic.
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — engine 5.4.0 final run (2026-10-17)
**Growth sanity check (mandatory):** the engine's blended start is 14.77%, but its components are acquisition-inflated — 5-yr revenue CAGR 14.40% and 3-yr 14.61% straddle the Avast (2022) and MoneyLion (2025) consolidations, and the latest revenue YoY of +27.06% is MoneyLion consolidation, not organic growth. The prints that mean something: FY27 revenue guidance of +9–11% (raised 2026-09-28; management says results track toward the high end), Q2 FY27 guided at +9–11%, and non-GAAP EPS guided +14–18% (buybacks plus interest savings on deleveraging lift per-share growth above revenue growth). Scenario starts were therefore set via offsets (−0.1477 / −0.0877 / −0.0277 / +0.0223 / +0.0923 vs the blended g_base) to 0 / 6 / **12** / 17 / 24%. The base start (12%) sits above the revenue guide on the documented per-share tailwinds but below the EPS guide's low end; the super-bull start (24%) sits below FY26's printed +27.06% revenue YoY with the written reason that that print was acquisition consolidation, not an organic run-rate. Probabilities shifted bear-ward (15/30/30/17/08 vs the 10/25/30/25/10 default) for the 5.7x OE leverage and the unresolved GoDaddy overhang. OE multipliers are the defaults 0.75/0.90/1.00/1.10/1.25. Base OE/share $2.19 (TTM). Price $24.16.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | 0.0% | 0.75 | GoDaddy (or similar) debt-funded deal lands and indigests; core AV erodes to free rivals | $12.16 | 8.69% |
| Bear | 30% | 6.0% | 0.90 | MoneyLion growth fades post-consolidation; core grows low-single-digits; leverage stays high | $18.73 | 12.27% |
| Base | 30% | 12.0% | 1.00 | FY27 guide delivered (+9–11% revenue, mid-teens EPS), buybacks and deleveraging continue | $26.65 | 16.17% |
| Bull | 17% | 17.0% | 1.10 | MoneyLion cross-sell compounds; EPS guide top end sustained; deal overhang lifts | $35.94 | 20.16% |
| Super bull | 8% | 24.0% | 1.25 | Financial-wellness platform becomes a second growth engine; rapid deleveraging | $54.11 | 26.61% |

- **Probability-weighted: IV@15% $25.88 (+7.1% vs price), IV@12% $34.93, IV@10% $45.09, weighted IRR 15.80%, base-case IRR 16.17%**
- **Tier by numbers: B.** Bear-case tier C (12.27%), bull-case tier A (20.16%) — see TIER_BAND. Diagnostics (dcf_numbers.json): OE yield 9.08%, terminal value 20.3% of IV@15%, scenario spread 4.45x, net debt 5.74x normalized OE, 6.5 months since FY end.
- Hurdle-clearing prices (weighted): clears 15% at $25.88, 20% at $17.82, 25% at $13.46. At $24.16 the 15% hurdle is cleared with almost no margin of safety.

## Flags — every fragility flag resolved
- **OE_VOLATILE** (OE/share spans >3x over 5 years: FY22 $1.52, FY23 $0.99, FY24 $2.97, FY25 $1.72, FY26 $2.08): the volatility is deal- and tax-timing-driven, not demand cyclicality — the Avast merger closed into FY23 and FY24 carries the tax/WC one-offs below. Handled by the median/TTM bases (neither takes FY24's spike) and by putting 45% probability on bear-or-worse.
- **NI_OCF_DIVERGENCE** (2024, 2025): FY24 OCF of $2,064M vs net income of $607M is explained by the FY24 cash-flow statement (comparative in the Q4 FY25 release): an ~$861M decrease in other assets (tax-deposit-related release), a $446M build in income taxes payable, $485M of D&A add-back, partly offset by a −$991M deferred income tax item — i.e., FY24 OCF was flattered by tax-timing, which is exactly why FY24's $2.97 OE/share is the outlier the median discards and the TTM base dilutes. FY25 shows a further ~$906M other-assets inflow on the same tax-deposit line, plus a $66M non-cash legal contract dispute cost. The OCF-based conservative OE is used throughout and the binding bases (median $2.08, TTM $2.19) sit well below the FY24 print, so the divergence does not contaminate the verdict.
- **WIDE_SCENARIO_SPREAD** (super-bull IV 4.45x super-bear): real — the range is driven by a genuine binary (deal indigestion vs platform compounding) on a levered equity. Confidence is capped at medium and the verdict is sized to the bear end.
- **HIGH_NET_DEBT** (net debt 5.74x normalized OE): from the filing — net debt $7,794M (debt $8,196M, cash $402M) at FY26-end; company-reported net leverage 2.95x at Q1 FY27 after $45M of repayment, target below 3.0x. Leverage is acquisition debt being actively paid down, but at 5.7x OE the equity is a levered claim: bear and super-bear carry 45% combined weight and the super-bear OE multiplier (0.75) plus 0% growth is the stress case.
- **TIER_BAND** (bear C 12.27% vs bull A 20.16%): the verdict spans tiers, so any position is sized to the bear end — the headline B rests on the base case, not the weighted tails.

## Thoughts / method range
- Method range: on the engine's median base ($2.08/share) with the preliminary default scenarios the run printed weighted IRR 17.68% / IV@15% $30.18 (still Tier B); on the TTM base with guidance-anchored growth and bear-shifted weights, 15.80% / $25.88. The honest range is **mid-B to high-B** — GEN clears 15% under both bases, but never with a wide margin at $24.16.
- The price embeds the GoDaddy scare (~$31 pre-report to $24.16). If the approach is formally abandoned, the overhang discount likely closes toward the base case; if a ~$12B+ debt-funded deal is signed, the super-bear/bear branch (45% weight) is the right frame and the stock is expensive.
- SBC is modest for software ($225M TTM, ~14% of OE) and falling as a share of revenue; share count is shrinking on buybacks (603M diluted shares in the TTM window vs 624M in the prior-year YTD period, ttm.json) — a real per-share tailwind already reflected in the scenario starts, not double-counted.
- Verdict: **Tier B, sized to the bear end.** A durable, cash-generative franchise at a deal-scare price that just clears the 15% hurdle on the weighted scenarios; it becomes a clear buy below ~$20 (the 20%-hurdle price is $17.82) and is not a bargain if the GoDaddy deal proceeds on debt.
