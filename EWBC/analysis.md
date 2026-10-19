# EWBC — East West Bancorp, Inc.
v5.4 run, 2026-10-16 (first pass). Price $126.47 (nasdaq_quote_api), market cap ~$17.6B — in scope under $40B.

All figures below are copied from dcf_numbers.json, ttm.json, or fundamentals.json — none are recomputed.

## What it is
The largest US bank built on the US–Asia cross-border niche: East West Bank (Pasadena, CA) serves commercial and consumer customers — heavily Chinese-American and cross-border trade clients — across the US and Greater China. $80.4B in assets, $56.9B in total loans, $67.1B in deposits at FY2025 (10-K). Q2 2026 printed records across the board: revenue $791M (+12.5% YoY), NII $685M, NIM 3.43%, diluted EPS $2.63 (+18% YoY per the release), efficiency ratio 36.7%, CET1 15.4%; management raised FY2026 guidance (loan growth 6–8%, NII growth 7–9%).

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $1,501,700,000; SBC $76,189,000 (always a real cost); capex $14.0M — by override, see OVERRIDE.
- **Conservative owner's earnings FY2025: $1,411,511,000 = $10.15/share** (base_oe_latest_per_share, after the capex override); maintenance version $1,538,352,000 (financials_history.csv oe_maintenance) — same ballpark, modestly higher.
- OE positive 5 of the last 5 fiscal years. Net income FY2025 $1,325,188,000 (diluted EPS $9.52); net income grew every year 2020–2025.
- **Base used = the engine's normalized base: median of the last 3 FY OE/share = $9.66/share** (base_source: median_of_last_3_fy_oe_per_share).

**TTM check (STALE_FY resolution — ttm.py, filing-direct):**
- OCF: FY $1,501,700,000 − prior YTD $556,554,000 + current YTD $1,030,030,000 = **TTM $1,975,176,000**
- Capex: FY leg filled by the override ($14,000,000) − prior YTD $4,614,000 + current YTD $112,528,000 = **TTM $121,914,000** — the current-YTD leg is dominated by a one-off $99,046,000 premises purchase in Q1 2026 (10-Q), not a maintenance run-rate
- SBC: FY $76,189,000 − prior YTD $26,480,000 + current YTD $36,855,000 = **TTM $86,564,000**
- Shares (current-YTD weighted diluted): **138,568,000**
- **TTM OE total $1,766,698,000 → $12.75/share**
- The TTM base was **not** used as the scored base: a bank's OCF leg swings with balance-sheet working items (the TTM OCF leg is +32% vs FY2025 on those swings), and its capex leg carries the one-off building purchase. The median FY base is the conservative, through-cycle figure, and the verdict is sized to it. The TTM variant is reported under Thoughts as the top of the method range.

## OVERRIDE — capex (estimate, bounded authority)
- **The gap:** the preliminary engine run exited 4 with `DATA_GAP:capex` — no tier emitted. EWBC's 10-K cash flow statements for FY2023–FY2025 contain no purchases-of-premises-and-equipment line at all (verified directly in the FY2025 10-K, accession 0001069157-26-000009: the spend is folded into "Other investing activities, net"); the us-gaap tag `PaymentsToAcquirePropertyPlantAndEquipment` is filed only in 10-Qs from 2025 onward. Premises & equipment net is $82,310,000 on an $80,434,997,000 balance sheet — capex is structurally immaterial for this bank.
- **The decision:** judgment.json carries `capex_override = {value: 14000000, kind: "estimate"}` — at the top of the filed FY2016–2021 range ($2.66M–$13.79M/yr) and ~2.3× the last filed value ($6,017,000, FY2021), inside the 0.1×–10× band; the engine filled FY2022–FY2025 (overrides_applied periods_filled).
- **Measured impact (dcf_numbers.json override_impact):** normalized base OE/share $9.76 zero-fill → **$9.66** with the override; weighted IRR 12.24% → **12.15%**. Its other effect is binary: without it there is no tier at all.

## Moat: 6/10 — moderate, a strong niche franchise with concentration risk
Justification: a dominant, decades-deep position in US–Asia cross-border banking with elite, through-cycle returns, but the franchise is one niche — CRE-heavy lending, one customer diaspora, and a geopolitical exposure that can impair the niche itself.
- Returns evidence: fundamentals.json's `roic_proxy` and gross-margin series are not computable for a bank presentation (both null); the bank-relevant series is ROE — 12.6% / 13.2% / 15.9% / 13.4% / 10.8% / 15.0% / 18.8% / 16.7% / 15.1% / 14.9% for FY2016–FY2025, never below ~11% even through COVID, plus Q2 2026 ROTCE of 17% and a 36.7% efficiency ratio. Returns have stayed well above a bank's cost of equity through a cycle, which is what a 6 rests on; the concentration below is what keeps it from 7+.
- FOR: the leading US bank for US–Asia cross-border business — relationships, language/culture, and trade-finance know-how rivals don't replicate; low-cost relationship deposit franchise (noninterest-bearing deposits +19% YoY in Q2 2026; deposits +8% YoY to a record $70.1B); elite efficiency (36.7%) and NIM (3.43%) for a regional; fortress capital (CET1 15.4%, tangible common equity 10.4%); disciplined credit through cycles (Q2 2026 net charge-offs 19bp, NPAs 29bp).
- AGAINST: commercial-real-estate concentration in the loan book; the niche itself is concentrated — one diaspora/cross-border corridor, directly exposed to US–China tension and Chinese capital controls; deposit competition is raising funding costs (flagged by management in Q2 2026); rate-sensitive NII; long-tenured CEO Dominic Ng is a succession question; a regional bank's funding moat is structurally thinner than a money-center's.
- A 6 gives CAP = 9.8 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 9.8 years, 15-year projection.

## DCF — v5.4 final run (2026-10-16)
Growth recalibration (written reason): the engine's blended start is 2.71%, but its revenue components are meaningless for a bank — the revenue tag used (RevenueFromContractWithCustomerExcludingAssessedTax) captures only a fee-income sliver, not NII. Bank growth must key off earnings and balance-sheet prints: diluted EPS $8.33 (FY2024) → $9.52 (FY2025, +14.3% per the earnings release), Q2 2026 EPS +18% YoY on the release's headline (+15% on the $2.63 vs $2.28 comparison), and raised FY2026 guidance of loan growth 6–8% and NII growth 7–9%. Scenario starts were therefore set via offsets (−0.077 / −0.017 / +0.043 / +0.073 / +0.103 vs the 2.71% blend) to −5 / +1 / **+7** / +10 / +13%. Probabilities 10/25/30/25/10 (defaults); OE multipliers 0.75/0.90/1.00/1.10/1.25 (defaults). Base OE $9.66/share, price $126.47.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | −5.0% | 0.75 | CRE credit cycle + cross-border freeze; provisions spike | $42.59 | 6.35% |
| Bear | 25% | +1.0% | 0.90 | NIM compression from deposit repricing; growth stalls | $66.73 | 9.03% |
| Base | 30% | +7.0% | 1.00 | Guided loan/NII growth delivered, then a normal fade | $96.84 | 12.20% |
| Bull | 25% | +10.0% | 1.10 | Deposit franchise keeps compounding; fee income scales | $121.72 | 14.57% |
| Super bull | 10% | +13.0% | 1.25 | 2025-26 momentum persists; capital returns accelerate | $158.00 | 17.72% |

- **Probability-weighted: IV@15% $96.22 (−23.9% vs price), IV@12% $128.52, IV@10% $164.64, weighted IRR 12.15%, base-case IRR 12.20%**
- **Tier by numbers: C** (bear D at 9.03%, bull C at 14.57% — see TIER_BAND). Diagnostics: OE yield 7.64%, terminal value 19.3% of IV@15%, scenario spread 3.71x, net debt −3.09x normalized OE (see BIG_NET_CASH), 9.5 months since FY end.

## Flags — every fragility flag resolved
- **DATA_GAP:capex / OVERRIDE_APPLIED:capex**: see OVERRIDE — the gap, the bounded estimate, and the measured impact (−$0.10/share of base, −0.09pp of weighted IRR) are recorded in judgment.json, dcf_numbers.json (overrides_applied / override_impact), and the registry.
- **STALE_FY** (latest FY ended 9.5 months ago): ttm.py was run and its legs are quoted above; the TTM base was considered and rejected as the scored base for the reasons stated there (bank OCF swings + the one-off Q1 2026 premises purchase in the capex leg). It is carried as the top of the method range.
- **SECTOR_MODEL_MISMATCH** (Finance): real — an OCF-minus-capex DCF fits a bank poorly (deposits are raw material, not debt; regulatory capital, not capex, constrains growth). Confidence is **low**; treat the tier as a rough yield-on-normalized-earnings check, not a bank valuation.
- **BIG_NET_CASH** (net cash 3.1x normalized OE): an artifact of the same mismatch — the engine's net-debt calc counts only long-term debt and short-term borrowings against cash, while a bank's real funding is $67,082,701,000 of deposits (FY2025 10-K) against $56,899,148,000 of total loans and $80,434,997,000 of assets, with equity of $8,899,202,000. There is no distributable cash pile; the "net cash" is operating float of the banking business. No verdict adjustment taken from it.
- **TIER_BAND** (bear D 9.03% vs bull C 14.57%): the verdict is sized to the bear end — even the bull case does not clear 15% on the scored base.

## My thoughts / overlay
- The honest headline is the method range: on the normalized median base the weighted IRR is **12.15% (Tier C)**; on the TTM base (same scenarios, measured run) it is **15.05% (Tier B)** with IV@15% $126.98 ≈ the price. The truth for a bank growing EPS at a mid-teens clip off a 15% ROE is between those, and neither method is a bank model. What both agree on: at $126.47 the market is already paying for the good outcome — there is no margin of safety against the bear cases (bear IV@15% $66.73).
- Quality is genuinely high for a regional: ROE ~15-17% for a decade, efficiency 36.7%, CET1 15.4%, dividend raised 33% for Q1 2026 with DPS TTM $2.80 and a $300M buyback authorization (fundamentals.json dividends: 8 growth years, last cut 2010; TTM dividends paid $389M + buybacks $124M).
- Risks: CRE concentration meeting a higher-for-longer rate path; US–China friction hitting the exact corridor the franchise monetizes; deposit-cost repricing (a large CD book rolls in H2 2026 per the Q2 call coverage); CEO succession.
- Hurdle-clearing price: the weighted IV@15% is **$96.22** — the stock would need to fall ~24% before the scored method clears Andrew's 15% hurdle; at the TTM method it clears only at today's price, with nothing to spare.

## Final verdict
- **Final tier: C** (weighted IRR 12.15% on the scored normalized base; method range C to B)
- Confidence: **Low** (SECTOR_MODEL_MISMATCH — the model is a rough earnings-yield check on a bank, not a bank valuation)
- One-liner: Elite-quality regional bank, moat 6/10 — ~15% ROE through a decade and a real cross-border niche, but at $126.47 it doesn't clear the 15% hurdle on normalized earnings (weighted IRR 12.1%, IV@15% $96.22; clears 15% only at ~$96).
