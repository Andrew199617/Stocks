# DVA — DaVita Inc.
v5 run (engine 5.4.0), 2026-10-18. Market cap $14.21B at $187.31 (nasdaq_quote_api) — in scope under $40B.

All figures below are copied from dcf_numbers.json, ttm.json (ttm.py), financials_history.csv, or fundamentals.json — none are recomputed.

## What it is
The largest US dialysis provider: 2,671 US outpatient centers (3,266 worldwide) serving ~298,500 patients as of Q2 2026, ~38% US market share in a duopoly with Fresenius Kidney Care (~34%; ~72% combined). Life-sustaining, non-discretionary treatment, paid mostly by Medicare with a high-rate commercial minority that carries the margin. Integrated Kidney Care (IKC) had ~64,900 patients in risk-based arrangements. Q2 2026: revenue $3.554B (+5.2% YoY), operating income $579M, diluted EPS $4.02; FY2026 guidance reconfirmed (adjusted operating income midpoint $2.2B, adjusted EPS midpoint $14.65; total treatment growth now expected near the top of +25–50bp).

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $1,886,500,000; capex $575,864,000; SBC $139,953,000 (always a real cost).
- **Conservative owner's earnings FY2025: $1,170,683,000 = $15.43/share** (maintenance version, NI + D&A − capex basis: $616,989,000 — lower because net income carries heavy interest on the levered balance sheet; the OCF-based conservative figure is the one used throughout).
- OE positive 5 of the last 5 fiscal years. Net debt $9,596,751,000 plus operating lease liabilities $2,601,142,000 (dcf_numbers.json); net debt is 5.77x normalized OE on the TTM base (8.2x on the median base).
- OE/share history (financials_history.csv): $9.89 (2020), $10.80 (2021), $9.03 (2022), $14.80 (2023), $15.63 (2024), $15.43 (2025) — the 2022 dip is the reimbursement-vs-labor-cost squeeze (operating margin 11.5% in FY2022 vs 15.5% in FY2021, fundamentals.json).
- Aggressive buybacks: diluted share count 93,182,000 (2023) → 87,274,000 (2024) → 75,885,000 (2025); $785M repurchased YTD through Q2 2026 (2.2M shares in Q2 at $154.95 average). Leverage held at 3.37x against a 3.0–3.5x target; Q2 added a $500M Term Loan B-2 tranche.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $1,886,500,000 − prior YTD $504,245,000 + current YTD $810,900,000 = **TTM $2,193,155,000**
- Capex: FY $575,864,000 − prior YTD $264,349,000 + current YTD $271,836,000 = **TTM $583,351,000**
- SBC: FY $139,953,000 − prior YTD $62,567,000 + current YTD $54,189,000 = **TTM $131,575,000**
- Shares (current-YTD weighted diluted): **67,476,000**
- **TTM OE total $1,478,229,000 → base OE/share $21.91** (base_source: ttm_json)
- The engine's normalized base (median of last 3 FY) is $15.43/share. It is reported here and in the method range below, not used as the base: FY ended 9.6 months ago (STALE_FY), H1 2026 is filed fact (H1 OCF $810.9M vs $504.2M in H1 2025, on both higher net income and a smaller working-capital drag per the Q2 10-Q), guidance confirms earnings growth, and the share count the OE is actually divided by today is ~67.5M, not the 75.9M FY2025 average. Caveat stated plainly: TTM OCF of $2,193M is above every full year in the filed history (best prior $2,072M in 2019), so part of the H1 strength may be working-capital timing that mean-reverts; that is what the recalibrated growth and the bear weights are for (see DCF).

## Moat: 6/10 — narrow, strong end
Justification: US dialysis duopoly (~38% share), life-sustaining non-discretionary demand and scale, with ROIC proxy 11–20% over the last five fiscal years — but the payer sets the price, Fresenius is vertically integrated into equipment, and GLP-1/transplant progress is a long-term volume headwind.
- FOR: duopoly scale (~38% US share, 2,671 US centers, largest network); life-sustaining, non-discretionary demand with high switching friction (nephrologist relationships, clinic proximity); ROIC proxy (fundamentals.json, after-tax operating income over equity + debt − cash) of 14.1% / 15.6% / 11.3% / 14.4% / 19.5% / 17.9% for FY2020–25 — above the cost of capital through a cycle, including the 2022 squeeze; scale purchasing and clinical-operations leverage, with IKC extending the franchise into value-based care.
- AGAINST: no pricing power vs the payer — government reimbursement updates lag labor/cost inflation (FY2022 margin crush is the proof); Fresenius is vertically integrated (machines, NxStage home platform) and supplies equipment into DaVita's own home program while DaVita owns no manufacturing; commercial-mix erosion as ACA exchange enrollment falls (management cited it in the Q2 sequential revenue-per-treatment decline); long-term volume risk from GLP-1s and transplant advances; leverage (net debt $9.60B, 3.37x) leaves little shock absorber.
- Gross margin: DaVita files no COGS/gross-profit tag (services presentation in fundamentals.json — gross_margin is null for every year); the margin evidence used instead is operating margin, 15.0% in FY2025 and 15.2% on TTM (fundamentals.json), in an 11.5–16.3% five-year range.
- A 6 gives CAP = 9.8 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 9.8 years, 15-year projection.

## DCF — v5 final run (2026-10-18)
Growth recalibration (written reason): the engine's blended start is 9.46%, but it is buyback arithmetic, not business growth — revenue components (5-yr CAGR 3.39%, 3-yr 5.53%, latest YoY 6.46%) each got the full +5pp share-count adjustment for the −7.48%/yr shrink, while treatment volume itself grew only +0.3–0.6% YoY in Q2 2026 and revenue per treatment ~+2.8%. The TTM base already sits on the shrunken 67.5M share count, so crediting another full 5pp/yr of shrink double-counts it — and the shrink itself is capped by the 3.0–3.5x leverage target (already 3.37x) at a price 21% above Q2's average repurchase price. Scenario starts were therefore set via offsets (−0.155 / −0.085 / −0.035 / +0.015 / +0.085 vs g_base) to −6.0 / +1.0 / **+6.0** / +11.0 / +18.0%: the base start (+6.0%) matches the actual recent revenue prints (FY2025 +6.46%, TTM revenue +6.4% per fundamentals.json, Q2 +5.2%) with only modest per-share help from buybacks; no scenario start sits below what the company just printed without that reason being the deliberate de-double-counting above. Probabilities 10/25/30/25/10; OE multipliers 0.75/0.90/1.00/1.10/1.25. Price $187.31.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | −6.0% | 0.75 | Reimbursement cut or commercial-mix collapse repeats 2022, levered | $92.17 | 8.20% |
| Bear | 25% | +1.0% | 0.90 | TTM OCF mean-reverts, volume flat, buybacks slow at the leverage cap | $150.94 | 12.53% |
| Base | 30% | +6.0% | 1.00 | Revenue grows at recent prints; IKC/international offset mix pressure | $209.51 | 16.42% |
| Bull | 25% | +11.0% | 1.10 | Fresenius clinic closures keep feeding share; RPT and IKC both deliver | $287.82 | 20.92% |
| Super bull | 10% | +18.0% | 1.25 | Volume + rate + buyback flywheel all run at once | $445.72 | 28.22% |

- **Probability-weighted: IV@15% $226.33 (+20.8% vs price), IV@12% $303.29, IV@10% $389.49, weighted IRR 17.41%, base-case IRR 16.42%**
- **Tier by numbers: B.** Diagnostics (dcf_numbers.json): OE yield 11.70%, terminal value 19.6% of IV@15%, scenario spread 4.84x, net debt 5.77x normalized OE, 9.6 months since FY end.
- Hurdle-clearing prices: clears 15% at or below $226.33, 20% at or below $157.65, 25% at or below $120.18.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.6 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, legs quoted above.
- **BUYBACK_TAILWIND** (share count −7.48%/yr): real and already credited in the blend — which is exactly why the growth starts were recalibrated down (see DCF): the TTM base's 67.5M denominator plus a full +5pp/yr forward shrink credit would count the same buyback twice. Buyback capacity is also leverage-capped (3.37x vs a 3.0–3.5x target).
- **NI_OCF_DIVERGENCE** (>40% gap in 2023, 2024, 2025): no one-off — it is structural to this business and it is why the OCF-based OE is the right series. Net income is stated after ~$0.7B/yr of non-cash D&A (FY2025 D&A $708,252,000 vs the $1,139,697,000 OCF−NI gap, financials_history.csv) plus SBC and working-capital swings, and after heavy interest expense that OCF also carries. The residual gap is depreciation on a 3,266-center estate plus deferred-tax/WC timing, present in every year of the history, not a single-year distortion; net income actually *understates* the cash the clinics generate. FY2017's negative maintenance-OE print in the CSV is the mirror image (a large negative ΔNWC year) and is not in the base window.
- **WIDE_SCENARIO_SPREAD** (4.84x): real — leverage amplifies the outcome range. Confidence is medium (capped), and the verdict is sized to the conservative end.
- **HIGH_NET_DEBT** (5.77x normalized OE on the TTM base; 8.2x on the median base; net debt $9,596,751,000 plus $2,601,142,000 of operating leases): the bear cases carry it — bear pairs a 0.90 OE multiplier with a +1.0% start (IRR 12.53%), super bear 0.75/−6.0% (8.20%). Management holds leverage at 3.37x inside its 3.0–3.5x target and termed out maturities with the Q2 Term Loan B-2, but there is no deleveraging story here: buybacks, not debt paydown, get the free cash flow.
- **TIER_BAND** (bear C 12.53% vs bull A 20.92%): the verdict spans tiers, so it is sized to the bear end — Tier B headline, with the C outcome on defensible inputs stated in the method range below.

## Thoughts / method range
The honest headline is a range, not a point. On the engine's 3-yr median base ($15.43) with default growth the same company prints a 14.58% weighted IRR — Tier C. On the TTM base with the unadjusted 9.46% blend it prints 19.14% — high Tier B. The final run (TTM base, growth de-double-counted) sits between them at 17.41%, Tier B, and the B is what survives both corrections at once: the stale median ignores a filed H1 that is demonstrably stronger and a share count that is demonstrably smaller, while the raw blend double-counts the buyback. What would change the answer: full-year 2026 OCF (does the $2.19B TTM hold after H2 working-capital seasonality?), the 2027 Medicare ESRD rate update vs labor inflation, and whether buybacks continue at ~7%/yr of the count now that the price is ~$187 rather than ~$155.

## Verdict
Tier B — a durable, levered duopoly cash machine that clears Andrew's 15% hurdle at $187.31 on current (TTM) numbers, with $226.33 as the price where it stops clearing. Sized to the conservative end: on the median base it is a C, the bear case is a C, and the balance sheet (net debt $9.60B) is the reason not to pay up for the bull case.
