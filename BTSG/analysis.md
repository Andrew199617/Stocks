# BTSG — BrightSpring Health Services, Inc.
Engine 5.4.0 run, 2026-10-17. In scope (market cap $13.378B at $60.87, nasdaq_quote_api).

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.json or fundamentals.json — none are recomputed.

## What it is
Home and community-based health services for complex populations, in two segments: Pharmacy Solutions (specialty, infusion, home & community pharmacy — the large majority of revenue) and Provider Services (home health, hospice, rehab, personal/primary care). Founded 1974, KKR-backed, IPO January 2024. Q2 2026: revenue $3.87B (+23.0% YoY), Pharmacy Solutions +22%, Provider Services +30%, Specialty & Infusion revenue +30% with script growth +31% (company report via search). In March 2026 it closed the sale of its Community Living business to Sevita for $835M cash and used part of the proceeds to repay $300M of term loan.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $490,169,000; capex $95,484,000; SBC $70,099,000 (always a real cost).
- **Conservative owner's earnings FY2025: $324,586,000 = $1.48/share** (key_numbers.md: latest FY OE/share $1.48)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC) is far lower and working-capital-dominated in both directions across the short history — the pharmacy build consumes receivables as it grows — so the OCF-based conservative figure is the series used throughout.
- OE positive only 2 of the last 4 fiscal years (key_numbers.md): OE/share −$0.66 (2022), $1.13 (2023), −$0.65 (2024), $1.48 (2025) in financials_history.csv. This is a young, volatile OE record, not a proven compounder's.
- Net debt $2.419B at FY2025 (key_numbers.md), lease liabilities $178,356,000 (dcf_numbers.json).

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $490,169,000 − prior YTD $150,674,000 + current YTD $166,859,000 = **TTM $506,354,000**
- Capex: FY $95,484,000 − prior YTD $42,057,000 + current YTD $50,576,000 = **TTM $104,003,000**
- SBC: FY $70,099,000 − prior YTD $38,483,000 + current YTD $23,169,000 = **TTM $54,785,000**
- Shares (current-YTD weighted diluted): **221,191,000**
- **TTM OE total $347,566,000 → base OE/share $1.57** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $1.13/share — it averages in the negative-OE 2024 year and the pre-IPO share base, so it understates the current continuing business; it is still reported in key_numbers.md and drives the net-debt multiple the engine prints. The TTM base is only modestly above the latest FY ($1.48), so the choice is not aggressive: even on the TTM base every scenario lands in Tier D.

## Moat: 4/10 — weak-moderate
Justification: Scale, limited-distribution drug access (149 drugs) and an integrated pharmacy+provider platform give sticky clinical/payer relationships, but ROIC proxy was only 1.2%/2.0%/5.2% in 2023/2024/2025 and gross margin fell from 17.5% (2022) to 11.8% (2025) on low-margin specialty pharmacy mix — no proven pricing power or through-cycle returns above the cost of capital.
- Evidence (fundamentals.json): gross margin 17.54% (2022) → 14.81% (2023) → 12.57% (2024) → 11.76% (2025), TTM 12.38%; operating margin 0.76–2.43% across FY2023–25, TTM 3.12%; roic_proxy 19.66% (2022, a year of negative net income — not a clean read), 1.17% (2023), 2.03% (2024), 5.22% (2025). A 7+ moat cannot sit on that record.
- FOR: National scale in home/community care for complex populations — ~475,000 patients daily, national payer contracts and procurement leverage; Limited-distribution drug portfolio (149 drugs, 16-20 launches expected next 12-18 months) — access smaller specialty pharmacies cannot replicate; Integrated Pharmacy Solutions + Provider Services platform: cross-referrals, sticky clinically-managed infusion/specialty cases with complex payer authorization; Specialty & Infusion momentum: Q2 2026 revenue +30%, script growth +31%.
- AGAINST: ROIC and gross-margin record above; Reimbursement is set by Medicare/Medicaid/commercial payers, not the company — IRA impact ~$200M on Home & Community Pharmacy in 2026, that segment's revenue fell 8.6% in H1 2026; Insurer-owned rivals (UnitedHealth/Optum, CVS) and focused peers (Option Care) compete for the same specialty/infusion volume; Labor-intensive provider services with thin operating margins and clinician-retention risk on acquired Amedisys/LHC branches; Levered history and sponsor overhang: KKR secondary offering in June 2026; net debt $2.42B at FY2025.
- A 4 gives CAP = 7.2 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 7.2 years, 15-year projection.

## DCF — final run (2026-10-17)
Growth sanity check (mandatory): the scenario starts are OE/share growth starts, not revenue growth. The engine blend is 13.97% (components, key_numbers.md: rev CAGR 5y 18.69%, rev CAGR 3y 18.69%, latest rev YoY 28.18%, OE/share CAGR 2y 14.25%, share-count adjustment −5.00pp). Recent prints run hotter on revenue — FY2025 +28.18%, Q1 2026 +25.6%, Q2 2026 +23.0%, TTM revenue +26.35% (fundamentals.json) — but management's own raised FY2026 guidance is $15.1–15.425B revenue (about 17–19.5% growth) and $820–845M adjusted EBITDA, the Community Living exit removes a revenue block, and the IRA drags Home & Community Pharmacy by ~$200M. So the base start (14.0%) sits below the latest revenue prints for a written reason — guided deceleration plus divestiture/IRA mix — and the bull start (19.0%) is set at the top of the guided revenue range rather than at the Q2 print, because OE/share has compounded at 14.25% (2-yr CAGR), not at the revenue rate. The super-bull start (26.0%) does match the current TTM revenue print. Default probabilities 10/25/30/25/10 and default OE multipliers 0.75/0.90/1.00/1.10/1.25 were kept — the evidence does not justify skewing the weights for a business with OE positive in only 2 of 4 years. Price $60.87.

| Scenario | Prob | Growth start | OE mult | IV@15 | IRR |
|---|---|---|---|---|---|
| Super bear | 10% | 2.0% | 0.75 | $9.47 | 4.43% |
| Bear | 25% | 9.0% | 0.90 | $14.84 | 5.70% |
| Base | 30% | 14.0% | 1.00 | $19.89 | 6.87% |
| Bull | 25% | 19.0% | 1.10 | $26.30 | 8.32% |
| Super bull | 10% | 26.0% | 1.25 | $38.50 | 10.89% |

- **Probability-weighted: IV@15% $21.05 (−65.4% vs price), IV@12% $28.44, IV@10% $36.72, weighted IRR 7.16%, base-case IRR 6.87%**
- **Tier by numbers: D** — and the band is D at both ends (bear tier D, bull tier D; scenario range 4.43%–10.89%). Even the super bull does not reach the 15% hurdle at this price.
- Diagnostics (key_numbers.md): OE yield 2.58%, terminal value 20.3% of IV@15%, scenario spread 4.07x, net debt 7.01x normalized OE, 9.5 months since FY end.
- Hurdle-clearing prices (weighted path): clears 15% only below $21.05, 20% below $14.47, 25% below $10.90.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.5 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, legs quoted above.
- **DILUTION** (share count +23.09%/yr): this is primarily an IPO artifact, not ongoing SBC dilution — diluted shares were 117,840,000 in 2022 and 117,868,000 in 2023 (pre-IPO), then 192,997,000 in the January-2024 IPO year, 219,774,000 in 2025 and 221,191,000 TTM (financials_history.csv / ttm.json), i.e. roughly flat since the IPO repricing of the count. The engine's −5.00pp growth adjustment is therefore conservative, and it is kept, not reversed. The SBC leg itself is falling: TTM SBC $54,785,000 vs FY2025 $70,099,000. June 2026 also saw a $60M repurchase of 1,026,465 shares alongside the KKR secondary offering (search).
- **NI_OCF_DIVERGENCE** (2023, 2025): non-cash and working-capital effects, not a one-off tax deposit — 2023 net income −$154,603,000 vs OCF $210,783,000 with D&A $202,336,000; 2025 net income $190,666,000 vs OCF $490,169,000 with D&A $164,277,000 and SBC $70,099,000 (financials_history.csv). The OCF-based conservative OE is the series used throughout, so the divergence does not contaminate the base; the real caution it carries is that reported earnings quality is thin (operating margin 0.76–2.43%).
- **WIDE_SCENARIO_SPREAD** (4.07x): real — a 2-of-4-years-positive OE history priced at a growth multiple genuinely has a wide outcome range. Confidence is capped at low, and the verdict is sized to the conservative end; note the spread does not change the tier, since even the super bull is Tier D.
- **HIGH_NET_DEBT** (7.01x normalized OE): balance sheet from the filing (financials_history.csv, FY2025): total debt $2,507,544,000 (current $52,340,000 + noncurrent $2,455,204,000), cash $88,370,000, net debt $2,419,174,000, plus lease liabilities $178,356,000. Post-FY2025 deleveraging is material and noted, not scored: the Community Living sale (closed March 30, 2026, $835M) funded a $300M term-loan repayment and repricing, and the company reported leverage of 2.15x at June 30, 2026 vs 2.99x at December 31, 2025 (company reports via search). The engine's 7.01x is against the small normalized OE base ($1.13/share), not against EBITDA — leverage against cash earnings is the milder ~2-3x the company reports. Either way the equity sits behind real debt at a 2.58% OE yield, which is why the bear cases are stressed in the weights.
- Preliminary run also carried **LOW_OE_YIELD** (1.9% on the median base): on the TTM base the yield is 2.58% (key_numbers.md) — still thin. The valuation rests almost entirely on growth; that is a fragility, not a flag error.

## My thoughts / overlay
- The business momentum is real — guidance raised twice in 2026, adjusted EBITDA +44% in Q2, deleveraging ahead of plan — and the stock has already been paid for it: at $60.87 the market is capitalizing TTM OE of $1.57/share at ~39x. The DCF question is not whether BrightSpring grows, it is whether any plausible OE path repays this price at 15%: the super bull (26% start, 1.25x OE) still only yields 10.89%.
- Method range: on the engine's normalized median base ($1.13/share) the preliminary run printed weighted IRR 6.15% and IV@15% $15.91; on the TTM base used here, 7.16% and $21.05. Both are Tier D — the conclusion does not depend on the base choice, which is the strongest thing about this score.
- Basis break to watch (not a scored flag): the March 2026 Community Living divestiture and the Amedisys/LHC branch acquisitions mean FY2026 continuing-operations figures will not be cleanly comparable with the FY2022–25 history in financials_history.csv; growth inputs above were chosen on guided continuing-business rates, not on the raw reported series.
- What would change the verdict: sustained operating-margin expansion (TTM 3.12% and rising) converting the 20%+ revenue growth into OE/share compounding well above the 14.25% 2-yr CAGR, at a materially lower price. At ~$21 the weighted case clears 15%.

## Final verdict
- **Final tier: D** (weighted IRR 7.16% on the TTM base; bear and bull both D)
- Confidence: **Low** (WIDE_SCENARIO_SPREAD, OE positive only 2/4 years, high net debt vs OE, post-divestiture basis break — though the D conclusion itself is robust across both defensible bases and all five scenarios)
- One-liner: Real growth pharmacy/provider platform, moat 4/10 — does not clear 15% at $60.87 on any scenario (weighted IRR 7.2%, weighted IV@15% $21.05; clears 15% only below ~$21) despite +23% Q2 revenue growth, because TTM OE is only $1.57/share and margins/ROIC are thin.
