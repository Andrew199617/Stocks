# XP — XP Inc.
Engine 5.4.0 run, 2026-10-16 (first pass). Price $29.26 (nasdaq_quote_api), market cap $16.04B, diluted shares 548,319,000. Cayman-incorporated holding company for Brazil's leading independent investment platform; files Form 20-F under IFRS, reports in BRL (all engine figures FX-converted to USD at period-end ECB rates).

All figures below are copied from dcf_numbers.json, financials_history.csv, or fundamentals.json — none are recomputed.

## What it is
Brazil's largest independent investment platform: retail brokerage and wealth (4.8M active clients, ~R$2.2tn client assets AUM+AUA at 2Q26), distributed through ~18.4k independent advisors plus a growing internal/RIA channel, and diversifying into wholesale banking, cards, credit, insurance and retirement. SIC 6211 (security brokers/dealers).

## Owner's earnings
**FY2024 (latest FY in EDGAR companyfacts, USD-converted):** operating cash flow $1,807,526,689; SBC $67,466,284 (always a real cost); capex $23,414,006.
- **Conservative owner's earnings FY2024 (OCF − capex − SBC): $1,784,112,684**
- **Maintenance version FY2024: $1,716,646,399 = $3.13/share** (the engine's base_oe_total_latest_fy)
- OE positive 4 of the last 5 fiscal years — FY2021 was negative (−$1.48/share) because broker-dealer OCF swung negative that year despite $644.8M of net income (see NI_OCF_DIVERGENCE below).
- **Base used = normalized: median of last 3 FY OE/share = $2.9143/share** (FY2022 $0.39, FY2023 $2.91, FY2024 $3.13). No TTM base: ttm.py reads us-gaap only and exits non-zero for this IFRS filer, and the FY2025 20-F (filed 2026-04-29) is not yet in EDGAR companyfacts, so no filing-direct TTM exists. Per spec, the median base stands.
- Balance sheet (FY2024, USD-converted): cash $2,087,355,488 vs total borrowings $269,445,390 → **net cash $1,817,910,098**; lease liabilities $50,341,696. Total assets $56,180,283,524 against equity of $3,241,437,751 — the balance sheet is mostly client/financial balances, as expected for a broker-dealer. 2Q26 Basel ratio 20.3%.

## Moat: 6/10 — moderate, scale distribution without captivity
Justification: Scale distribution (18.4k advisors, R$2.2tn client assets) and a two-decade brand produce durable ~20-25% ROE, but advisors are not captive, take rates compress ~5bp/yr, and banks/fintechs with bigger balance sheets contest every product line — a moderate moat, not a wide one.
- FOR: Brazil's leading independent investment platform: ~R$2.2tn client assets (AUM+AUA, 2Q26, +17% YoY), 4.8M active clients; largest advisor distribution network in Brazil (~18.4k advisors) — distribution scale rivals cannot replicate quickly; sustained ROE ~20-25% (22.5% in 2Q26; FY ROE 20-25% across 2020-2024 in fundamentals.json) on a capital-light model; diversifying beyond brokerage: wholesale banking +32% YoY in 2Q26, cards, credit (loan book R$78bn, +16%), insurance, retirement (R$101bn, +18%); brand and investor-education franchise built over two decades in a market structurally shifting from bank deposits to investments.
- AGAINST: advisor network is not captive — independent advisors can multi-home or leave, and internal/RIA migration is still in progress; take-rate compression is structural (annualized retail take rate fell 5bp YoY to 1.20% in 2Q26); entrenched banks (Itaú, BTG Pactual, Bradesco) and Nubank/Inter attack with bigger balance sheets and customer bases; earnings geared to Brazilian rates, market volumes and BRL — USD returns carry unhedged currency risk; revenue still concentrated in Brazilian retail investing, core wealth segment maturing (~16% share).
- Returns evidence: fundamentals.json ROE runs 19.1% / 24.9% / 21.0% / 20.0% / 22.5% for FY2020-2024 (BRL as filed), and BRL net margin expanded from 41.5% to 60.8% over the same years. The `roic_proxy` series is null and gross margin is not tagged — this IFRS financial filer files no operating-income or COGS lines — so the moat rests on the sustained ROE record rather than a computed ROIC series. A 6 sits on ROE that has stayed well above any plausible cost of capital through the 2020-2024 cycle, capped below 7 by non-captive distribution and take-rate compression.
- A 6 gives CAP = 9.8 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 9.8 years, 15-year projection.

## DCF — engine 5.4.0 final run (2026-10-16)
Blended growth start 5.80% (components: revenue CAGR 5y 6.06%, 3y 2.58%, latest USD revenue YoY −10.82%, OE/share CAGR 2y 183.95% — the last is an artifact off FY2022's depressed $0.39/share and does not drive the blend's median). Scenario offsets and OE multipliers are the defaults (−12/−5/0/+5/+12pp; 0.75/0.90/1.00/1.10/1.25). Probabilities adjusted from the 10/25/30/25/10 default to 15/30/30/15/10: the OE_VOLATILE flag directs a wider bear weight, and the finance-sector model misfit argues against paying for the bull tail.

**Growth-start sanity check against actual prints:** 2Q26 net revenue grew +9% YoY in BRL and net income +5%, diluted EPS +9% (earnings release, Aug 17, 2026); management targets double-digit growth for 2026. In USD the same business printed −10.82% revenue YoY in FY2024 purely on BRL depreciation (period-end rate 0.20609 → 0.16169). The base start of 5.8% (USD) sits between the BRL operating prints and the FX-dragged USD prints — high-single-digit BRL growth with a modest FX drag. The bull start (10.8%) requires the guided double-digit BRL growth with roughly stable FX — at, not above, the latest guided print. The super-bull start (17.8%) exceeds every recent print and requires double-digit BRL growth *plus* BRL appreciation; it is the stretch case and carries only 10% weight for that reason. The super-bear start (−6.2%) is precedented by FY2024's actual −10.8% USD revenue print.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | −6.2% | 0.75 | BRL slides again, volumes and take rates compress together | $12.18 | 7.25% |
| Bear | 30% | 0.8% | 0.90 | BRL growth stalls near zero in USD; banks take share | $19.94 | 10.95% |
| Base | 30% | 5.8% | 1.00 | High-single-digit BRL growth, modest FX drag, slow diversification payoff | $27.68 | 14.35% |
| Bull | 15% | 10.8% | 1.10 | Guided double-digit growth lands, FX stable, wholesale keeps compounding | $38.03 | 18.35% |
| Super bull | 10% | 17.8% | 1.25 | Double-digit growth plus BRL appreciation and operating leverage | $58.90 | 24.94% |

- **Probability-weighted: IV@15% $27.71 (−5.3% vs the $29.26 price), IV@12% $37.01, IV@10% $47.40, weighted IRR 14.37%, base-case IRR 14.35%**
- **Tier by numbers: C.** Hurdle prices: clears 15% only below $27.71, 20% below $19.39, 25% below $14.84. Diagnostics: OE yield 9.96%, terminal value 19.3% of IV@15%, scenario spread 4.84x, net debt −1.14x normalized OE (net cash), 21.5 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (latest parsed FY ended 21.5 months ago): the FY2025 20-F was filed 2026-04-29 but its facts are not yet in EDGAR companyfacts (fundamentals.py states this explicitly), so neither the engine nor ttm.py can build a filing-direct FY2025/TTM base; ttm.py additionally reads us-gaap only and exits non-zero for this IFRS filer. Median-of-3-FY base used per spec. Corroboration that the stale base is not flattering the result: 2Q26 printed net revenue +9% and net income +5% YoY in BRL — the business kept growing after the base period, in local currency.
- **OE_VOLATILE** (OE/share spans >3x over 5 years): real and structural — broker-dealer OCF includes financial-asset and client-balance flows, so OE/share ran −$1.48 (2021) to $3.13 (2024). Handled by the normalized median base plus bear-or-worse probability weight raised to 45%.
- **NI_OCF_DIVERGENCE** (NI vs OCF differ >40% in 2022, 2023, 2024): no single one-off — this is the broker-dealer model. OCF runs through trading/financial balances and client flows: FY2021 OCF was −$721.6M against $644.8M net income, while FY2023-24 OCF ran roughly 2.1-2.5x net income as the balance sheet grew (assets $36.3B → $56.2B USD-converted). Consequence: the OCF-based OE base is inherently noisy for this name, which is one reason confidence is low and the median (not latest) base is used.
- **FX_CONVERTED** (BRL → USD at period-end ECB rates): flow facts use the period-end rate, not a period average; the BRL fell from 0.24878 (end-2019) to 0.16169 (end-2024) USD, so USD growth materially understates BRL growth — FY2024 revenue grew +13.7% in BRL (fundamentals.json, as filed) while the converted series prints −10.82% YoY. All scenario growth starts are USD-basis and were sanity-checked on that basis above.
- **ADS_RATIO_APPLIED** (x1.0): XP has no ADS program — its Class A common shares are themselves the Section 12(b)-registered security traded on Nasdaq (FY2025 20-F cover, filed 2026-04-29), so per-share figures are already per traded share. Ratio recorded in judgment.json from the filer's own 20-F.
- **SECTOR_MODEL_MISMATCH** (Finance): confidence graded low, as directed. An OE/capex DCF fits a broker-dealer poorly — capex is trivial next to balance-sheet flows, and value here is really ROE-vs-cost-of-equity on a growing equity base. The tier is reported as scored, but it is a misfit-model number.
- **WIDE_SCENARIO_SPREAD** (super-bull IV 4.84x super-bear): real — the range is mostly a BRL range. Confidence is low and the verdict is sized to the conservative end.
- **TIER_BAND** (bear tier C at 11.0% vs bull tier B at 18.4%): verdict sized to the bear end, per the flag.

## My thoughts / overlay
- The honest headline is the method range, not the point estimate: on the default probabilities the preliminary run printed weighted IRR 15.04% (Tier B); widening the bear weight as OE_VOLATILE directs moves it to 14.37% (Tier C), and the whole question is really a BRL question — in local currency this is a ~22% ROE franchise compounding client assets at +17% YoY.
- Quality is not the debate: net cash balance sheet at the corporate level, Basel 20.3%, buybacks (R$1bn executed in 2Q26, another R$1bn announced) plus dividends, share count drifting down (−1.49%/yr share CAGR, already credited in the blend).
- Risks the model cannot price: a Selic easing cycle cuts the float/fixed-income revenue XP earns on client balances even as it helps volumes; advisor attrition to BTG/banks; Brazilian political/FX shocks hitting USD returns regardless of operating performance.
- Margin of safety: at $29.26 the price sits 5.6% *above* the weighted IV@15% — there is none on the scored numbers. The bear-case IV@15% is $19.94, a third below the price. A buyer here needs the bull FX/growth combination, not just the base case.

## Final verdict
- **Final tier: C** (weighted IRR 14.37% on the final 5.4.0 inputs; bear C / bull B band, sized to the bear end)
- Confidence: **Low** (sector model misfit, stale FY2024 base with no filing-direct TTM available, 4.84x scenario spread)
- One-liner: High-quality Brazilian investment platform, moat 6/10 — at $29.26 it does not clear 15% on the scored numbers (weighted IRR 14.4%, weighted IV@15% $27.71; it clears 15% only below $27.71), and the finance-sector OE model plus a stale FY2024 base cap confidence at low — size it to the bear end (Tier C).
