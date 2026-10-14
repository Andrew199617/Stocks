# MTB — M&T Bank Corporation
v5 run, 2026-10-14. In scope (market cap $34.208B at $215.43, nasdaq_quote_api). **Finance sector — the OE/capex DCF fits banks poorly; confidence is low by rule, and the tier is a screen result, not a bank valuation.**

All figures below are copied from dcf_numbers.json, financials_history.csv, or ttm.py's output message — none are recomputed.

## What it is
Large Northeast/Mid-Atlantic regional bank holding company (Buffalo, NY): commercial and retail banking through M&T Bank plus Wilmington Trust wealth/trust. ~$216B of assets (Q2 2026 average), $163.5B of deposits. Q2 2026 was a record print: net income $818M, diluted EPS $5.32, net interest income $1,792M at a 3.70% NIM, efficiency ratio 52.8%, CET1 10.19%, and the strongest core loan growth since 2012 per the company's release.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $3,003,000,000; capex $143,000,000 — by override, see OVERRIDE; SBC $136,000,000 (AllocatedShareBasedCompensationExpense, always a real cost).
- **Conservative owner's earnings FY2025: $2,724,000,000 = $17.15/share** (base_oe_latest_per_share $17.1546).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $3,031,000,000 — above the conservative figure; for a bank both definitions are approximations (loan growth, the real "capex" of a bank, is an investing outflow neither captures), which is exactly the sector-mismatch caveat.
- OE positive 5 of the last 5 fiscal years. Net debt as the engine computes it is $10,911,000,000 (long-term debt minus cash — deposits, a bank's real funding, are not in this figure; see HIGH_NET_DEBT below).
- **Base used = normalized median of the last 3 FY OE/share: $20.0276/share** (the median year is FY2024, on the override-filled capex). The FY is stale (ended 9.4 months ago) but no TTM base could be built — see STALE_FY.

## OVERRIDE — capex (bounded worker authority, filing kind)
- **The gap:** the preliminary engine run exited 4 with `DATA_GAP:capex` — capex missing for FY2024 and FY2025 of the last 3 under every candidate tag in EDGAR companyfacts (filed values through FY2023 came via PaymentsToAcquireProductiveAssets, $256M in FY2023). No tier was emitted, correctly.
- **The decision:** judgment.json carries `capex_override = {value: 143000000, kind: "filing", source: "Form 10-K for fiscal year ended December 31, 2025, Consolidated Statements of Cash Flows, investing activities line 'Capital expenditures, net': $143M for FY2025, with $216M for FY2024 in the same statement (corroborated by the filer's 10-Q cash-flow statements: $87M for the nine months ended Sep 30, 2025 and $131M for the nine months ended Sep 30, 2024, with Q4 adding the remainder in each year)"}`. In band: $143M vs the last filed value of $256M (override_checks out_of_band: false). The override fills ONLY the two missing periods (capex_tag = "OVERRIDE" for 2024/2025 in financials_history.csv); filed values are never replaced.
- **Known imperfection, stated:** the engine applies the single $143M value to FY2024 as well, where the filing figure is $216M — understating FY2024 capex by $73M (~2% of that year's conservative OE, in the direction of raising that year's OE). The median year of the base is FY2024, so the base is flattered by roughly that amount; it does not change the tier (the zero-fill comparison below brackets it).
- **Measured impact (dcf_numbers.json override_impact, engine-native base):** base OE/share $20.8823 zero-fill → $20.0276 with the override; weighted IRR 12.74% → 11.85%. Tier C either way. Its binary effect: without it there is no tier at all (unblocks_tier).

## Moat: 5/10 — moderate, standard regional-bank franchise
Justification: a sticky low-cost core deposit franchise and disciplined underwriting, against a commodity product, full credit/rate-cycle exposure, and capital-regulated capital return.
- FOR:
  - Sticky low-cost core deposit base — $163.5B deposits funding a Northeast/Mid-Atlantic relationship franchise
  - Disciplined underwriting culture — nonaccruals 0.84% of loans and net charge-offs 0.23% annualized at Q2 2026, improving
  - Through-cycle profitability — OE positive 5 of last 5 FY, FY2025 net income $2,851M, ROA 1.35%
  - Scale in its footprint — ~$216B assets; Wilmington Trust wealth arm adds fee income
  - Consistent capital return — diluted shares down from 167.3M (FY2024) to 158.8M (FY2025), buybacks continuing in 2026
- AGAINST:
  - Commodity product — deposits and loans are fungible; no network effect or structural pricing power (NIM 3.70% is earned, not owned)
  - Credit-cycle exposure — commercial real estate book in deliberate runoff ($24.0B at Sep 2025 vs $28.7B a year earlier); a recession hits provisions first
  - Capital-constrained growth — CET1 fell to 10.19% at Q2 2026 from 10.99% a year earlier; buybacks compete with loan growth for capital
  - Rate sensitivity — earnings ride NIM and the yield curve; deposit repricing pressure is outside management control
  - Scale disadvantage vs national banks' technology and compliance budgets
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — v5 final run (2026-10-14)
Growth recalibration (written reason): the engine's blended growth is not usable as printed for a bank. Its revenue series is the contract-revenue tag, which for a bank excludes interest income — the CSV revenue line drops from ~$6.0B (FY2021) to ~$1.5B (FY2022 onward) purely on the tag, so rev_cagr_5y prints −22.58% and the blend lands at g_base −2.48% even after the +1.08pp buyback adjustment; OE/share CAGR 2y is −9.92% off the FY2023 OCF peak. Actual earnings prints: FY2025 net income $2,851M (+10% vs FY2024's $2,588M), Q2 2026 net income $818M vs $716M in Q2 2025, diluted EPS $5.32 vs $4.24 — flattered by lower credit costs and buybacks, not a sustainable growth rate. Scenario starts were therefore set via offsets (−0.12 / −0.06 / +0.04 / +0.09 / +0.14 vs g_base) to −10.0 / −8.5 / **+1.5** / +6.5 / +11.5%: a low-single-digit base (bank earnings power grows with loans, deposits and buybacks, roughly nominal-GDP-like at best through a cycle), bears carrying a real credit cycle, super bull capped well below the current provision-flattered EPS prints. Probabilities 10/25/30/25/10; OE multipliers 0.75/0.90/1.00/1.10/1.25. Price $215.43.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -10.0% | 0.75 | Credit cycle turns; CRE losses, provisions spike, buybacks halt | $72.94 | 6.21% |
| Bear | 25% | -8.5% | 0.90 | Recession-lite: charge-offs normalize up, NIM compresses | $93.30 | 7.43% |
| Base | 30% | +1.5% | 1.00 | Low-single-digit earnings-power growth, steady buybacks | $157.65 | 11.62% |
| Bull | 25% | +6.5% | 1.10 | Loan growth momentum holds, credit stays benign | $213.46 | 14.89% |
| Super bull | 10% | +11.5% | 1.25 | Sustained mid-teens EPS compounding off buybacks + loan growth | $298.08 | 19.31% |

- **Probability-weighted: IV@15% $161.09 (−25.2% vs price), IV@12% $212.12, IV@10% $268.85, weighted IRR 11.85%, base-case IRR 11.62%**
- **Tier by numbers: C.** Diagnostics: OE yield 9.30%, terminal value 17.9% of IV@15%, scenario spread 4.09x, net debt 3.43x normalized OE, 9.4 months since FY end.

## Flags — every fragility flag resolved
- **DATA_GAP:capex** (preliminary run): resolved by the filing-sourced override — see OVERRIDE. data_gap_uncovered is empty in the final run.
- **STALE_FY** (FY ended 9.4 months ago): ttm.py was run and failed — its exact message: "ttm.py: cannot compute TTM for MTB (CIK 36270): sbc: no post-FY YTD fact (no 10-Q since the 2025-12-31 fiscal year end); capex: no post-FY YTD fact (no 10-Q since the 2023-12-31 fiscal year end)". Per the sweep rules the engine's median base is used instead, with this reason stated. Direction of the error: H1 2026 prints (net income $1,482M vs $1,300M in H1 2025, per the Q2 2026 release) suggest a TTM base would be higher than the median base, so the stale base is more likely conservative than flattering — but it is unbuilt, not assumed.
- **BASIS_BREAK_SUSPECT**: two breaks, both in the revenue series, neither in the OE series used for the base. (1) The revenue tag break at FY2022 described above (contract-revenue tag excludes bank interest income) — it poisons the revenue CAGRs, which is why growth was recalibrated from earnings prints instead. (2) The People's United acquisition (closed April 2022) stepped the balance sheet up — visible in shares (128.8M FY2021 → 164.0M FY2022) and OCF — which is why no CAGR straddling 2022 is trusted at face value.
- **SECTOR_MODEL_MISMATCH** (Finance): accepted in full. A bank's "owner's earnings" are not its distributable cash — loan growth consumes capital, provisions are a through-cycle cost the OCF line only partially carries, and value in banking is normally judged on ROE vs cost of equity and tangible book, neither of which this model computes. Confidence is low and the tier is soft.
- **OVERRIDE_APPLIED:capex**: see OVERRIDE — gap, decision, single-value imperfection, and measured impact are all recorded in fields (judgment.json, dcf_numbers.json overrides_applied/override_impact, overrides_registry.json), not just here.
- **WIDE_SCENARIO_SPREAD** (4.09x): real — a bank's outcome range across a credit cycle IS wide (super-bear IV $72.94 vs super-bull $298.08). Confidence is low (also mandated by the sector flag), and the verdict is sized to the conservative end.
- **HIGH_NET_DEBT** (3.43x normalized OE): an artifact of applying an industrial leverage lens to a bank. The engine's net debt is long-term borrowings minus cash ($10,911,000,000); it excludes the deposit base that actually funds the bank and the loan book that actually backs it. The leverage that matters is regulatory capital: CET1 10.19% at Q2 2026 (down from 10.99% a year earlier as buybacks and loan growth consumed capital — a real, monitored drift, flagged in the moat AGAINST list). The bear scenarios carry the credit stress this flag asks for.

## My thoughts / overlay
- The honest headline is the spread, not the point estimate: at $215.43 the buyer needs the bull case (IV@15% $213.46, IRR 14.89%) just to roughly clear 15%, and the weighted case returns 11.85%. Only the super-bull scenario (10%) clears the hurdle outright.
- Quality is not the problem: this is one of the better-run regionals — disciplined underwriting, improving credit metrics into Q2 2026, record EPS, real buybacks. The problem is price vs a bank's structurally capped earnings growth: a 9.30% OE yield sounds cheap until the growth fade and the credit-cycle bears are priced in.
- Method range: defensible variants cluster in C — the zero-fill base gives 12.74% weighted, the override base 11.85%; a TTM base (unbuildable here, see STALE_FY) would likely push toward the top of C, not into B, given H1 2026 momentum. No defensible variant found reaches B at this price.
- Price that clears 15%: the weighted IV@15% is $161.09 — the stock clears Andrew's hurdle at or below that level, roughly a quarter below the current price, before any additional margin of safety.

## Final verdict
- **Final tier: C** (weighted IRR 11.85% on the v5 final inputs; tier by numbers C, no override of the tier)
- Confidence: **Low** (sector-model mismatch plus a 4.09x scenario spread; the OE base itself is filing-solid once the capex override is in)
- One-liner: Disciplined regional bank, moat 5/10 — normalized OE $20.03/sh is a 9.3% yield at $215.43, but weighted IRR is only 11.85% (IV@15% $161.09), so it clears 15% only below ~$161; bank-model mismatch, confidence low.
