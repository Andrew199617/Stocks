# TRU — TransUnion
Engine 5.4.0 run, 2026-10-18. Price $74.08 (nasdaq_quote_api), market cap $14.564B, diluted shares 196,600,000, shares outstanding 192,800,000 as of 2026-03-31. In scope under $40B.

All figures below are copied from key_numbers.md (after make_score.py), dcf_numbers.json, ttm.json, fundamentals.json or financials_history.csv — none are recomputed.

## What it is
One of the three national U.S. credit bureaus (with Equifax and Experian, together >90% of the U.S. credit agency market), plus fraud / identity (Neustar, Sontiq), marketing and analytics, and international bureaus (UK, India, Canada, LatAm, and a majority stake in Trans Union de Mexico acquired March 2026). Revenue is U.S. Markets, International and Consumer Interactive; growth in 2026 is being driven by Financial Services, mortgage (including FICO score royalty pass-through), fraud / TruIQ / alternative data, and the OneTru platform migration.

## Owner's earnings
**FY2025 (10-K via EDGAR, financials_history.csv):** revenue $4,576,300,000; net income $455,400,000; operating income $857,800,000; operating cash flow $987,600,000; capex $326,000,000; SBC $145,600,000; D&A $574,800,000.
- **Conservative owner's earnings FY2025: $516,000,000 = $2.62/share** (OCF − capex − SBC; SBC is always a real cost).
- Maintenance version (from financials_history.csv): $632,300,000 — above the conservative figure, mainly because D&A exceeds capex; the conservative OCF-based figure is the one used throughout.
- OE positive 4 of the last 5 fiscal years. OE/share history: FY2021 $2.67, FY2022 −$0.43, FY2023 $1.21, FY2024 $2.01, FY2025 $2.62 — a real cycle trough in 2022–23, not a smooth compounder.
- Net debt $4,250,200,000 (LongTermDebtAndCapitalLeaseObligations + DebtCurrent, per dcf_numbers.json), lease liabilities $54,600,000.
- The engine's normalized base (median of last 3 FY OE/share) is $2.01/share — it is the median year FY2024 and it averages in the trough; it understates the current run-rate, which is why the TTM base below is used. The preliminary median-base run is reported under Method range.

**Base used = TTM owner's earnings through Q1 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $987,600,000 − prior YTD (Q1 2025) $52,500,000 + current YTD (Q1 2026) $84,200,000 = **TTM $1,019,300,000**
- Capex: FY $326,000,000 − prior YTD $68,400,000 + current YTD $65,200,000 = **TTM $322,800,000**
- SBC: FY $145,600,000 − prior YTD $30,300,000 + current YTD $37,500,000 = **TTM $152,800,000**
- Shares (current-YTD weighted diluted): **194,500,000**
- **TTM OE total $543,700,000 → base OE/share $2.80** (base_source: ttm_json; exact $2.7953727506426733 in dcf_numbers.json)
- Caveat: fundamentals.json warns the latest 10-Q (period 2026-06-30) is not yet in EDGAR companyfacts, so this TTM stops at Q1 2026. Q2 2026 is known from the earnings release (below) but its OCF is not yet in the filing-direct TTM — the base is therefore, if anything, slightly stale in the company's favour-negative direction, and no hand-built Q2 TTM was substituted.

**Recent prints (earnings releases, for the growth sanity check):** Q1 2026 revenue +13.7% YoY; Q2 2026 revenue $1,310M, +14.9% YoY, adjusted diluted EPS $1.23, adjusted EBITDA $456M (34.8% margin). Management raised FY2026 guidance to revenue $5,127M–$5,162M (+12–13% reported, 8–9% organic constant currency, 5–6% ex-FICO mortgage royalties, with acquisitions contributing roughly 3.5–4pp), adjusted EBITDA $1,807M–$1,827M, adjusted diluted EPS $4.75–$4.83.

## Moat: 6/10 — moderate-strong oligopoly, not a proven wide moat
Justification: a regulated three-bureau oligopoly with an irreplicable consumer-file database is a real structural moat, but TransUnion is the smallest of the three, it has no exclusive verification database comparable to Equifax's Work Number, and its measured returns on capital do not prove a wide moat.
- FOR: One of only three national bureaus — ~200M U.S. consumer files and ~10,000 furnisher relationships that no entrant can replicate; regulatory and sunk-cost barriers are near-insurmountable. Switching costs — lender underwriting, models and compliance workflows are built around bureau data. Diversifying, recurring non-mortgage revenue (fraud, identity, marketing, insurance and other emerging verticals) on the OneTru platform. Gross margin was 66.0% / 66.6% / 65.9% / 64.5% in FY2016–19, the years fundamentals.json tags cost of revenue (see data note below).
- AGAINST: Measured ROIC does not support 7+: the roic_proxy series in fundamentals.json is 7.1% (FY2020), 5.7% (FY2021), 4.7% (FY2022), 1.1% (FY2023), 5.8% (FY2024), 7.2% (FY2025) — at or below a normal cost of capital through the cycle, on a goodwill- and intangibles-heavy balance sheet built by acquisition. The FY2023 UK goodwill impairment (below) is direct evidence that at least one acquisition overpaid. Smallest of the Big Three, facing Equifax, Experian, LexisNexis and FICO; upstream FICO royalty pricing is a margin headwind management itself guides to (~90 bps of EBITDA-margin drag in 2026). Mortgage and consumer-lending volume cyclicality: OE/share fell to −$0.43 in FY2022 and $1.21 in FY2023. Leverage and regulatory / data-privacy exposure are permanent features of a bureau.
- Data note on gross margin: fundamentals.json reports no cogs / gross margin for FY2020–25 (the tag is absent in its series), so no recent gross-margin figure is quoted here rather than inventing one; the FY2016–19 figures above are the last tagged level, in the mid-60s.
- A 6 gives CAP = 9.8 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 9.8 years, 15-year projection.

## DCF — engine 5.4.0 final run (2026-10-18)
Growth: the engine blend is 10.38% (rev CAGR 5y 12.58%, rev CAGR 3y 7.25%, latest FY rev YoY 9.38%, OE/share CAGR 2y 47.12%, share-count adjustment −0.60pp applied to the revenue components only; share CAGR +0.60%). The 47.12% OE/share CAGR is an artifact off the depressed FY2023 base and is not taken at face value — the revenue components and current guidance are the meaningful signals, and they centre near the blend.
**Sanity check against actual prints:** the base start of 10.38% sits *below* the Q1 2026 (+13.7%) and Q2 2026 (+14.9%) revenue prints and below guided reported FY2026 growth (+12–13%) — written reason: that guidance includes roughly 3.5–4pp from acquisitions (Mexico) and FICO mortgage-royalty pass-through; the organic constant-currency guide is 8–9% (5–6% ex-FICO), so 10.38% sits between organic and reported, which is the right mid-cycle anchor. The bull start (15.38%) is essentially the Q2 print sustained; the super-bull start (22.38%) is a tail case requiring a mortgage-volume recovery plus OneTru / fraud acceleration, and carries only 10% weight. Bear (5.38%) and super-bear (−1.62%) reflect the demonstrated 2022–23 slowdown, when revenue growth fell to low single digits and OE/share collapsed.
Probabilities 10/25/30/25/10 (defaults, kept — the distribution of bureau outcomes is roughly symmetric around a cyclical base); OE multipliers 0.75/0.90/1.00/1.10/1.25 (defaults). Price $74.08.

| Scenario | Prob | Growth start | OE mult | IV@15 | IRR |
|---|---|---|---|---|---|
| Super bear | 10% | −1.62% | 0.75 | $14.31 | 4.78% |
| Bear | 25% | 5.38% | 0.90 | $23.45 | 6.58% |
| Base | 30% | 10.38% | 1.00 | $32.55 | 8.33% |
| Bull | 25% | 15.38% | 1.10 | $44.68 | 10.50% |
| Super bull | 10% | 22.38% | 1.25 | $69.06 | 14.30% |

- **Probability-weighted: IV@15% $35.13 (−52.6% vs price), IV@12% $47.68, IV@10% $61.81, weighted IRR 8.85%, base-case IRR 8.33%**
- **Tier by numbers: D.** Bear tier D, bull tier C (TIER_BAND — sized to the bear end).
- Diagnostics (dcf_numbers.json): OE yield 3.77%, terminal value 20.95% of IV@15%, scenario spread 4.83x, net debt 7.73x normalized OE, 9.56 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (latest FY ended 9.56 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q1 2026, legs quoted above. The Q2 2026 10-Q is not yet in EDGAR companyfacts (fundamentals.json warning), so no filing-direct Q2 TTM exists yet; the earnings-release Q2 figures are used only for the growth sanity check, not for the base.
- **NI_OCF_DIVERGENCE** (2023, 2024): 2023 net income was −$206,200,000 against OCF of $645,400,000. The gap is non-cash: a $414,000,000 goodwill impairment on the UK reporting unit in the FY2023 results reconciliation (management described a ~$495M UK impairment in Q3 2023, including the goodwill charge), plus D&A of $524,400,000, the $77,600,000 operating-model optimization program and $70,600,000 of accelerated technology investment. 2024 net income was $284,400,000 against OCF of $832,500,000, with D&A of $537,800,000 the dominant non-cash leg. The OCF-based conservative OE is unaffected by the non-cash impairment, so the base is not contaminated — but the impairment itself is real evidence of overpayment for acquired assets and is counted against the moat above.
- **SECTOR_MODEL_MISMATCH** (Finance sector): confidence graded **low** per the rule, and the name will list under sector misfits. In substance TransUnion is a data / analytics bureau, not a balance-sheet lender, so OCF − capex − SBC maps to its economics better than to a bank's (capex is a real, tagged ~7% of revenue and SBC is real and growing) — but the rule is applied as written, not argued away.
- **WIDE_SCENARIO_SPREAD** (super-bull IV 4.83x super-bear IV): real — outcomes range from a lending recession to a mortgage-recovery tail. Confidence is low (never high with this flag), and the verdict is sized to the conservative end.
- **HIGH_NET_DEBT** (net debt 7.73x normalized OE in the final diagnostics; $4,250,200,000): leverage is acquisition-built (Neustar era). On the company's own adjusted-EBITDA basis it reported 2.6x leverage in Q2 2026 with a long-term target below 2.5x, and it is buying back stock (~$150M YTD through July 2026 under a $1B authorization) — deleveraging is happening, but on an owner's-earnings basis the cushion is thin and levered OE can vanish fast in the bear cases, which is exactly what FY2022 (−$0.43/share) demonstrated.
- **TIER_BAND** (bear D at 6.58% vs bull C at 10.50%): the verdict spans tiers; it is sized to the bear end — final tier D.

## My thoughts / method range
- The tier is robust to the base choice, which is the useful finding: the preliminary run on the normalized median base ($2.01/share) gave weighted IRR 6.95% and IV@15% $24.43 (Tier D); the final TTM-base run ($2.80/share) gives 8.85% and $35.13 (still Tier D). Even the super-bull case (14.30% IRR, IV@15% $69.06) does not clear 15% at $74.08.
- Quality is not the debate — a bureau oligopoly with recurring data revenue is a good business. Price and capital structure are: at $74.08 the buyer pays ~26x TTM conservative OE for a company whose measured ROIC proxy has run 1–7% for six years and whose OE/share went negative within the last four years.
- What would change the verdict: a sustained return to double-digit organic growth ex-FICO and ex-acquisitions, ROIC proxy moving durably above ~10% as the goodwill denominator is earned back, and continued deleveraging. None of that is in the current filing-direct numbers yet.
- Hurdle-clearing prices (dcf_numbers.json): clears 15% at or below **$35.13**, 20% at or below $24.03, 25% at or below $18.05.

## Final verdict
- **Final tier: D** (weighted IRR 8.85% on the TTM base; method range across the median and TTM bases is D in both runs)
- Confidence: **Low** (SECTOR_MODEL_MISMATCH rule, WIDE_SCENARIO_SPREAD, and HIGH_NET_DEBT)
- One-liner: Oligopoly credit-bureau data franchise, moat 6/10, but levered and with low measured ROIC — on TTM OE of $2.80/share it does not clear 15% at $74.08 (weighted IRR 8.85%, IV@15 $35.13); it clears 15% only at or below $35.13.
