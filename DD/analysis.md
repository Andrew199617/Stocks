# DD — DuPont de Nemours, Inc.
Engine 5.5 run, 2026-10-19. This is DD's first score. The 2026-10-16 pass-1 run was blocked (`NEEDS_MAIN_AGENT: shares`) and wrote no score.json; engine 5.5 now handles the share basis that blocked it (see the last section). This re-score kept the worker's judgment.json, re-quoting only its one-liner to the final figures, and regenerated ttm.json with engine 5.5's ttm.py (legs and totals unchanged). There is **no override** in this run, as ruled (Andrew, ruling 2). One worker judgment changed in the re-score: the base-case growth start went from 5.0% to 4.0% (reason under "DCF").

All model figures below come from the final run's key_numbers.md, dcf_numbers.json, ttm.json, score.json and judgment.json. None are recomputed. History figures come from the SEC enrichment files in this folder (fundamentals.json, statements.json, segments.json, profile.json) and are marked with their file. Research facts are marked with their source document, each listed under Sources: the Q2 2026 earnings release ("DuPont Reports Second Quarter 2026 Results", behind the Item 2.02 results 8-K filed 2026-08-04 in profile.json), the Q2 2026 Form 10-Q (quarter ended 2026-06-30, filed 2026-08-04) and the September 2026 North Carolina settlement announcements. The run outputs carry none of these research figures, except where judgment.json repeats the worker's own figure (the 30.1% Healthcare & Water margin, the New Jersey settlement value), which restates them rather than verifies them; so none can be verified from the run outputs. The few background facts this file cites to no document are marked that way where they appear. None of the history or research facts feeds the valuation.

## What it is
DuPont is now a smaller specialty-materials company. Its portfolio has shrunk step by step. The first three steps below are background history that this file cites to no filing, and they cannot be verified from the run outputs: statements.json's discontinued-operations income line is large in those years ($724M FY2019, $5,308M FY2021, $4,856M FY2022) but names no transaction, and profile.json lists the former name DowDuPont Inc.
- the Dow and Corteva separations (2019),
- Nutrition & Biosciences to IFF (2021),
- Mobility & Materials (2022),
- the Qnity Electronics spin-off (November 2025),
- the Aramids (Kevlar / Nomex) sale, closed in April 2026 (judgment.json).

Two segments remain. Their FY2025 revenue (segments.json) ties to the $6,849M consolidated total:
- **Healthcare & Water Technologies:** Tyvek medical packaging, FilmTec reverse-osmosis membranes, other water-treatment and medical-device components. FY2025 revenue $3,233M (47.2%). Q2 2026 operating EBITDA margin was 30.1% (Q2 2026 release; judgment.json repeats it).
- **Diversified Industrials:** Tyvek building envelopes, construction materials, industrial and printing / packaging materials. FY2025 revenue $3,616M (52.8%). Q2 2026 operating EBITDA margin was 22.1% (Q2 2026 release; cannot verify from the run outputs).

Nasdaq's company profile puts the stock in the Industrials sector, industry "Major Chemicals" (profile.json; this is Nasdaq's own classification, not a dated GICS record), and its SEC SIC code is 2821, plastic materials and synthetic resins (profile.json). A 1-for-3 reverse stock split was approved at the May 21, 2026 annual meeting and took effect on June 24, 2026 (Q2 2026 10-Q). DuPont employed about 15,000 people at the end of 2025, about 1,700 of them in the since-sold Aramids business (profile.json, from the FY2025 10-K).

## Owner's earnings
**FY2025 (10-K, continuing operations; ttm.json FY legs):**
- operating cash flow $560,000,000
- capex $333,000,000
- SBC $38,000,000 (always a real cost)

That gives a **latest FY OE total of $189.0M, $1.35/share** (key_numbers.md, on the post-split share basis).

The three CSV rows FY2023–25 are on the continuing basis the FY2025 10-K restated (excluding Qnity and Aramids). Capex was $302.0M / $285.0M / $333.0M, all on `PaymentsToAcquireProductiveAssets` with $0.00 of intangible purchases (key_numbers.md capex basis lines). The **3-yr median OE/share is $3.03**.

**Capex completeness.** statements.json's investing section for FY2023–25 shows:
- one capital-expenditure line, matching the CSV;
- acquisitions;
- marketable-securities purchases and sales;
- a small "other investing" line.

There is no capitalized-software, intangible-purchase or construction-in-progress line. The Q2 2026 10-Q investing section has the same shape: capital expenditures, business-sale proceeds and "other investing, net". So the engine read the whole capex line. Capex runs at about half of D&A in FY2023–25 (D&A $580,000,000 / $635,000,000 / $647,000,000 in the CSV); CAPEX_COVERAGE_LOW did not fire, because not all three years are below 50%. The reason is that D&A includes the amortization of acquired intangibles ($2.9B of intangibles beside $7.9B of goodwill at FY2025, fundamentals.json); DuPont is not under-investing in plant. The outputs do not split depreciation from amortization, so the split cannot be quantified here.

**Maintenance version** (NI + D&A − min(capex, D&A) − ΔNWC): not meaningful for FY2023–25. The ΔNWC line in financials_history.csv swings by billions with the Qnity deconsolidation, and net income includes discontinued operations (see NI_OCF_DIVERGENCE). The OCF-based conservative figure is the one used.

**Base used: TTM owner's earnings through Q2 2026, from ttm.py (ttm.json, filing-direct, no hand math):**
- OCF: FY $560,000,000 − prior YTD $151,000,000 + current YTD $632,000,000 = **TTM $1,041,000,000** (all legs `NetCashProvidedByUsedInOperatingActivitiesContinuingOperations`)
- Capex: FY $333,000,000 − prior YTD $172,000,000 + current YTD $178,000,000 = **TTM $339,000,000** (`PaymentsToAcquireProductiveAssets`; ttm.json `capex_components` shows intangibles of 0.0 on all three legs)
- SBC: FY $38,000,000 − prior YTD $22,000,000 + current YTD $27,000,000 = **TTM $43,000,000** (`ShareBasedCompensation`; no leg reconciled)
- Shares: **137,200,000**, the current-YTD weighted diluted count from the Q2 2026 10-Q. That count is already on the post-split basis, because the 10-Q restates all periods for the split; ttm.json's `split_adjustment` records this (`ytd_current_before` 137,200,000, `applied: false`). The FY leg's 419,200,000 (`fy_diluted`) is the pre-split 10-K count and does not enter the per-share figure.
- **TTM OE total $659,000,000 → base OE/share $4.80** (base_source `ttm_json`). ttm.json has no warnings and uses no overrides; `sbc_reconciled_legs`, `capex_override_superseded_legs` and `sbc_reconciliation_withdrawn_legs` are empty.

## Moat: 5/10 — moderate / narrow
**Justification:** DuPont has market-leading, spec-in franchises with qualification switching costs. But measured returns on capital are low through the cycle, and gross margin sits in the low-to-mid 30s.

**Evidence (WORKER_SPEC step 5):**
- **ROIC:** fundamentals.json's `roic_proxy` is null in every fiscal year. DuPont does not tag operating income, so no ROIC series can be computed.
- **ROE:** the nearest filed return measure is 1.7% (2023), 3.0% (2024) and -5.6% (2025) (fundamentals.json). It is depressed by goodwill-heavy equity ($7.9B of goodwill against $13.9B of equity at FY2025) and by discontinued-operations results inside net income. Even allowing for that, nothing in the filed history shows returns well above the cost of capital.
- **Gross margin:** 36.6% (2021), 35.5% (2022), 32.8% (2023), 33.0% (2024), 34.5% (2025) (fundamentals.json). 2021–22 are pre-spin bases from older filings, and 2023–25 are the restated continuing basis. The margin is stable, not expanding.

That is a 5, not a 7+.

**FOR:**
- Tyvek leadership in medical packaging and construction envelopes: spec-in, qualification-locked positions.
- FilmTec reverse-osmosis membranes: a leading position in water treatment with installed-base replacement demand.
- Healthcare & Water Technologies operating EBITDA margin of 30.1% in Q2 2026 (Q2 2026 release; judgment.json).
- Patents, brands and regulatory qualifications that raise customer switching costs.

**AGAINST:**
- Low measured returns through the cycle (above; no computable ROIC).
- Gross margin in the low-to-mid 30s: pricing power is real but bounded.
- PFAS legacy liabilities, a multi-decade cash drag:
  - Under the 2021 memorandum of understanding (MOU) with Chemours, DuPont and Corteva together carry half of qualified PFAS spend, up to a $4B aggregate. This file cites no document for these terms and they cannot be verified from the run outputs; nothing in the valuation rests on them.
  - The September 2026 North Carolina settlement is $455M over 15 years in total. DuPont's share has a present value of about $126M, 44% of it reimbursable by Qnity (the September 2026 settlement announcements under Sources: the joint DuPont, Chemours and Corteva release and Chemours's Form 8-K dated 2026-09-10). Cannot verify from the run outputs: judgment.json records only "NC settlement cost-sharing".
  - The New Jersey settlement share has a present value of about $177M over 25 years (judgment.json).
- Cyclical end markets in Diversified Industrials: construction, automotive, printing and packaging.
- A portfolio still shrinking (Qnity spun, Aramids sold): a smaller, less diversified base.

**Fade:** moat 5 gives a **CAP of 8.5 years**. Growth holds for 2 years, then converges linearly to the **2.50%** terminal rate.

## DCF — final run (2026-10-19)
**Price:** $130.00 (nasdaq_quote_api).

**Growth recalibration (written reason).** The engine's blend is **-9.26% → g_base -5.00%** (the floor). Every component except the latest year straddles a portfolio change:
- **rev CAGR 5y -9.25% and 3y -19.27%:** these compare the continuing-basis FY2025 row with pre-spin rows from older filings that still carried Electronics, Aramids, and before that N&B and M&M.
- **OE/share CAGR 2y -35.38%:** this ends on FY2025, which carries the Qnity separation costs.

None of these measures organic growth. The organic prints are:
- latest rev YoY **1.93%** (FY2025, continuing basis);
- Q2 2026 net sales up 4.0% ($1,819M against $1,749M in Q2 2025, segments.json), and organic sales up 4% (Q2 2026 release; the organic figure cannot be verified from the run outputs);
- FY2026 organic growth guided "slightly above 4%", with mid-single-digit organic growth in H2 (Q2 2026 release; no run output carries the guidance, so it cannot be verified from them).

Scenario starts were therefore set with offsets of 0 / +5 / +9 / +14 / +19pp over the floored g_base (dcf_numbers.json `inputs.offsets`), giving **-5.0% / 0.0% / 4.0% / 9.0% / 14.0%**:
- **Base, 4.0%:** organic growth at the FY2026 guide, equal to the Q2 2026 organic print (4%) and above neither (both from the Q2 2026 release, not the run outputs); the H2 mid-single-digit guide is deliberately not used to lift it. The worker's pass-1 judgment, carried through this morning's earlier runs, set 5.0% ("the organic guide plus modest operating leverage"); this re-score lowered it because that start sat above the guidance this section quotes, and no figure in the run outputs (no 2025 adjusted-EPS figure, no separation-cost run-off figure) can size the leverage increment.
- **Bull, 9.0%:** the 2026 adjusted-EPS guidance ($7.17–$7.32, Q2 2026 release; cannot verify from the run outputs) converts to cash owner's earnings.
- **Super bull, 14.0%:** clean cash conversion plus sustained mid-single-digit organic growth.
- **Bear, 0.0%:** no growth from the TTM level, for example if the H1 2026 working-capital release reverses.
- **Super bear, -5.0%:** an industrial downturn plus heavier PFAS cash.

Only the two bear starts sit below a recent organic print, by design. The TTM's jump over FY2025 is a recovery from separation-depressed cash flow, not a growth rate, so no start is set from it.

**Probabilities:** 15/30/30/15/10 (judgment.json `probs_used`), which puts 45% on bear-or-worse (the default is 35%) for OE_VOLATILE, HIGH_NET_DEBT and the PFAS tail. **OE multipliers:** the defaults, 0.75/0.90/1.00/1.10/1.25.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IV@12 | IRR |
|---|---|---|---|---|---|---|---|
| Super bear | 15% | -5.0% | 0.75 | Construction / auto downturn, PFAS cash rises, TTM working-capital gains reverse | $21.59 | $27.80 | 4.39% |
| Bear | 30% | 0.0% | 0.9 | Owner's earnings stall near the TTM level; separation savings offset by legacy costs | $31.94 | $41.73 | 5.49% |
| Base | 30% | 4.0% | 1.0 | Organic growth at the FY2026 guide, no operating-leverage increment, decaying over the CAP | $41.92 | $55.38 | 6.58% |
| Bull | 15% | 9.0% | 1.1 | Adjusted-EPS guidance converts to cash; water and healthcare mix lifts margin | $56.72 | $75.89 | 8.19% |
| Super bull | 10% | 14.0% | 1.25 | Clean cash conversion, Aramids proceeds redeployed well, sustained mid-single-digit organic growth | $79.13 | $107.13 | 10.46% |

- **Probability-weighted:**
  - IV@15% **$41.82** (-67.8% vs price)
  - IV@12% **$55.40** (-57.4%)
  - IV@10% **$70.54**
  - **weighted IRR 6.61%**; base-case IRR 6.58%
- **IRR band:** bear 5.49% (Tier D) → bull 8.19% (Tier D); scenario range 4.39% – 10.46%.
- **Tier by numbers: D.** Hurdle-clearing prices on the weighted path: 15% at **$41.82**, 20% at $29.59, 25% at $22.84.
- **Diagnostics (key_numbers.md):**
  - OE yield 3.69%
  - terminal value 18.5% of IV@15%
  - scenario spread 3.67x
  - net debt / normalized OE 3.69x
  - 9.6 months since FY end
  - market cap $18.165B (basis `diluted_latest_split_adjusted`), in scope
  - net debt $2.479B
  - OE positive in 4/5 of the last five years (5/5 on a consistent cash-flow basis; see OE_VOLATILE)

## Flags — every fragility flag resolved
Seven flags fire (dcf_numbers.json `fragility_flags`); each is resolved below. `data_gap` is empty, and TIER_BAND, WIDE_SCENARIO_SPREAD, CAPEX_COVERAGE_LOW and SBC_TAG_RECONCILED did not fire.

- **STALE_FY** (the FY ended 9.6 months before the run). Resolved by construction: the base is the TTM through Q2 2026 from ttm.py ($4.80/share, legs above), re-run under engine 5.5 in this re-score. The Q2 2026 10-Q (filed 2026-08-04) is still DuPont's latest periodic report: the only later filing is an 8-K filed 2026-09-10 (material agreement; profile.json), the latest cover-page count is dated 2026-07-31, and DuPont reports Q3 in early November.
- **BASE_DIVERGENCE** (latest FY $1.35 vs 3-yr median $3.03; the TTM base is $4.80). **FY2025 is the distorted year**, and the TTM is the base used. Its depression shows in the cash-flow lines:
  - The H1 2025 continuing OCF is only $151,000,000 (ttm.json prior-YTD leg), against $632,000,000 in H1 2026.
  - The Q2 2026 10-Q's cash-flow statement (six months ended June 30) explains the swing. Income from continuing operations went from $104M (H1 2025) to $341M (H1 2026), and the accounts-payable change from -$19M to +$92M; statements.json's quarterly rows reproduce both (income $80M + $24M and $150M + $191M; payables -$8M and -$11M, then -$6M and +$98M). Two further lines come from the 10-Q only, because statements.json has no receivables-change or swap-gain row, and cannot be verified from the run outputs: the accounts-and-notes-receivable change went from -$213M to -$88M, and H1 2025's continuing income included a $51M non-cash interest-rate-swap gain, which the OCF reconciliation deducts.
  - Separation-related transaction costs and other payments fell from $136M in H1 2025 to $19M in H1 2026 (Q2 2026 release, where part of the amount is capex; cannot verify from the run outputs).

  FY2025 therefore carries the Qnity separation year's costs and an H1 receivables build (the 10-Q-only figure above), so it is not the run-rate. The median is pulled down by that year too. The TTM is not clean either. It includes H2 2025 (still a separation half), and its H1 2026 half is flattered by a payables inflow of about $92M (10-Q; statements.json's quarterly rows agree). That is why the bear cases carry 45% weight and the bear start is 0%. Choosing the median instead would lower the base ($3.03) and keep the tier at D, so the choice cannot lift the verdict.
- **NI_OCF_DIVERGENCE** (2025). The one-off is discontinued operations. The CSV's net income is `NetIncomeLoss`, the total company result: -$779M for FY2025, including -$836M of discontinued operations (the Qnity separation and Aramids, with PFAS / MOU activity, which DuPont books in discontinued operations; fundamentals.json / statements.json). Income from continuing operations was $98M (statements.json). The OCF in the base is continuing-only, so the divergence does not contaminate the OE base.

  **One caveat, which cannot be verified from the outputs:** if PFAS / MOU cash payments sit in discontinued-operations cash flow, the continuing-ops OE base leaves out a recurring legacy cost. The 10-Q shows MOU charges inside discontinued operations, but its excerpt does not show where the cash lands. That is a further reason the base is treated as generous on that dimension and sized to the bear end (open item 3 below).
- **SHARE_BASIS_ADJUSTED** (1-for-3 split, filed ratio 0.333, fact dated 2026-06-30). The split is DuPont's **1-for-3 reverse split, effective June 24, 2026**, reported in the Q2 2026 10-Q (approved May 21, 2026); the filed fact carries the 10-Q's period-end date. The engine confirmed the filed ratio against the post-split cover-page count, dei 135,042,975 on 2026-07-31 (dei_to_shares 0.322145, confirmed against the FY2025 filed count). It then multiplied every history count FY2016–FY2025 by 0.333333 (CSV `shares_split_factor`), so the history, the TTM pin and the price share one basis. The latest diluted count is 139,733,333, and the market cap is $18.165B (basis `diluted_latest_split_adjusted`, price × shares). The TTM pin needs no rescale: ttm.json's `split_adjustment` shows the 137,200,000 denominator already post-split (`applied: false`), as the README's Engine 5.5 entry records for DD's Q2 2026 leg. No override count exists, so none was left unrescaled (`periods_override_not_rescaled` is empty).

  **One qualification: FY2016 is still on the pre-2019 share basis.** The 2019 1-for-3 reverse split carries no split-ratio fact (dcf_numbers.json `share_basis.in_history_split_facts` is empty), so the engine applied only the 2026 ratio. The CSV's FY2016 `shares_diluted` is 374,400,000. statements.json infers the 2019 split from the re-filed counts ("read as a 1-for-3 reverse split effective 2019-08-06") and prints 124,675,200 for FY2016. FY2016 is outside the base, the 3-yr median, the growth window and the five-year OE window, so nothing in the valuation uses it; the one-basis statement holds for FY2017–FY2025 (open item 2 below).
- **BUYBACK_TAILWIND** (share count CAGR -5.67%, growth adjustment 5.00% on the revenue components). The shrink is the 2022–24 buyback funded by divestiture proceeds, and it is not repeatable at that pace. It has no effect on g_base, because the blend (-9.26%) sits below the -5.00% floor with or without the credit. The scenario starts were set from organic prints, not from the share CAGR, so the buyback is not counted in the verdict. Forward buybacks are smaller: $250M is planned for Q3 2026 (Q2 2026 release; cannot verify from the run outputs).
- **OE_VOLATILE** (OE/share spans >3x over five years; OE positive 4/5). The volatility is mostly portfolio churn plus a cash-flow basis mix in the history rows, not a loss year:
  - **The basis mix:** the CSV's FY2021–22 rows take total operating cash flow, which includes discontinued operations (`ocf_tag` `NetCashProvidedByUsedInOperatingActivities`: $2,281,000,000 and $588,000,000). From that they subtract capex that statements.json's warning calls continuing-only for the 2021-12-31..2026-03-31 periods ($788,000,000 and $662,000,000). FY2023–25 use continuing OCF (`NetCashProvidedByUsedInOperatingActivitiesContinuingOperations`).
  - **On a consistent basis:** statements.json's owner's earnings, on continuing OCF, are $991,000,000 (FY2021) and $512,000,000 (FY2022), against the CSV's $1,426,000,000 and -$149,000,000. FY2023–25 agree ($486,000,000 / $424,000,000 / $189,000,000). So all five of the last five years are positive, not the 4/5 key_numbers.md prints.
  - **What remains:** OE_VOLATILE fires on either basis, because the FY2021 per-share figure is still more than 3x the FY2025 one. FY2021–22 are pre-spin bases from older filings, and FY2025 carries separation costs; the rest is genuine end-market cyclicality in Diversified Industrials. Neither FY2021–22 row enters the TTM base, the FY2023–25 median or the growth inputs, so nothing in the valuation moves (open item 1 below).
  - **Handling:** the TTM base, 45% weight on bear-or-worse (default 35%), and a super-bear start of -5.0% at a 0.75 OE level.
- **HIGH_NET_DEBT** (net debt 3.69x normalized OE; net debt $2.479B at FY2025). This fires on the FY2025 year-end balance sheet (debt $60M current + $3,134M long-term − $715M cash, in the CSV). Engine 5.5 made it visible: the blocked 5.4 run computed the ratio on mismatched share bases and kept it silent (see the re-score section). Since FY2025 the Aramids sale closed. The Q2 2026 10-Q's cash-flow statement shows $1,158M of business-sale proceeds in H1 2026 investing cash flow; that line is in no run output (statements.json has no divestiture-proceeds row) and cannot be verified from the run outputs. statements.json's H1 2026 net investing cash flow is +$989M (-$102M in Q1, +$1,091M in Q2), which neither confirms nor contradicts it. statements.json's June 30, 2026 balance sheet shows $1,740M of cash against $3,125M of long-term debt and $0 of short-term debt. So current leverage is lower than the flag's figure. Leases add $217,000,000 (dcf_numbers.json `lease_liabilities_latest`), and PFAS accruals sit outside net debt. The bear cases are stressed: 45% weight, 0% and -5% starts. No scenario clears 15%, so leverage does not change the verdict.

## Thoughts / method range
- **The tier is robust to every defensible base.** The engine-native median ($3.03) is below the TTM base ($4.80) and gives a lower IRR. Even the super-bull path, a 14.0% start at a 1.25× OE level, prices IV@15% at $79.13, well below the $130.00 price. A base set at the company's adjusted-EPS guidance instead of cash owner's earnings would still leave the weighted IV@15% far under the price. The gap between adjusted EPS and cash OE has three sources: PFAS, restructuring and separation cash, plus intangible amortization added back in "adjusted" earnings. That gap is the core of the call.
- **Quality is moderate:** stable gross margins, spec-in positions and SBC of only $43,000,000 TTM. Capex at about half of D&A reflects intangible amortization inside D&A, not underinvestment.
- **Risks:**
  - PFAS (MOU cost sharing, the New Jersey and North Carolina settlements, open matters);
  - the cyclical Diversified Industrials segment;
  - execution as a smaller two-segment company;
  - the possibility that the H1 2026 working-capital release reverses.
- **Margin of safety:** none. The weighted IV@15% ($41.82) is 67.8% below the $130.00 price. A 15% return needs a price at or below $41.82; 20% needs $29.59.

## Final verdict
- **Final tier: D** (weighted IRR 6.61%; band D → D; tier by numbers D, no override).
- **Confidence: medium.** Every flag is resolved and the spread is 3.67x, not wide. The base is filing-direct but sits on a TTM still mixing a separation half-year with a working-capital-flattered half-year, and PFAS cash classification cannot be verified from the outputs.
- **One-liner (judgment.json):** Solid specialty-materials franchise, moat 5/10 — on TTM owner's earnings of $4.80/share the weighted IRR is 6.61% at $130.00 (weighted IV@15% $41.82, bear 5.49% → bull 8.19%, all Tier D); it clears the 15% hurdle only below $41.82 — the post-reverse-split price capitalizes an adjusted-EPS recovery that cash owner's earnings do not yet support.

## Open items for Andrew
None of these moves DD's valuation; the first two are engine follow-ups, not worker fixes.
1. **History-row OCF basis (engine).** History-row OCF should be selected on the same continuing basis as capex. DD's FY2021–22 rows mix total OCF with continuing-only capex (CSV OE $1,426,000,000 / -$149,000,000 against statements.json's $991,000,000 / $512,000,000), so key_numbers.md prints 4/5 OE-positive years instead of 5/5.
2. **Untagged historical splits (engine).** Splits with no ratio fact should be inferred the way statements.py infers them. DD's FY2016 count (374,400,000) still misses the 2019 1-for-3 that statements.json applies (124,675,200).
3. **PFAS / MOU cash classification (cannot verify from the outputs).** Where the MOU and settlement cash lands, continuing or discontinued operating cash flow, decides whether the continuing OE base omits a recurring legacy cost. The next pass should read the discontinued-operations cash-flow note in the FY2025 10-K and the Q2 2026 10-Q.

## Data and enrichment (2026-10-19)
- All six enrichment steps ran: fundamentals.py, prices.py, segments.py, statements.py, profile.py (with street.json) and reprice.py (live.json). None failed.
- Data notes:
  - fundamentals.json has no ROIC proxy (operating income is untagged), and notes that the latest four quarterly dividend-per-share facts are not consecutive quarters.
  - fundamentals.json's dividend and shareholder yields were priced from score.json before the final run, so they do not use the $130.00 price; nothing in this analysis quotes them.
  - segments.json's geography rows cover 86.4% of FY2025 consolidated revenue (`ties_to_total: false`); the business-segment rows tie.
  - statements.json leaves growth cells blank across filing generations (discontinued-operations restatements).
- prices.json, street.json and live.json are gitignored caches. live.json (reprice.py) reprices the same paths at the latest close.

## Sources (research, step 3)
- DuPont 8-K, reverse stock split announcement (May 2026; filed 2026-05-26, accession 0001666700-26-000034 in profile.json): https://www.sec.gov/Archives/edgar/data/0001666700/000166670026000034/dupontrssannouncement.htm
- DuPont Q2 2026 10-Q (quarter ended 2026-06-30, filed 2026-08-04, accession 0001666700-26-000053 in profile.json; cash-flow statement, split note): https://www.sec.gov/Archives/edgar/data/0001666700/000166670026000053/dd-20260630.htm
- DuPont Reports Second Quarter 2026 Results ("the Q2 2026 release"; earnings release for the quarter ended 2026-06-30, behind the Item 2.02 results 8-K filed 2026-08-04, accession 0001666700-26-000049 in profile.json): https://www.investors.dupont.com/news-and-media/press-release-details/2026/DuPont-Reports-Second-Quarter-2026-Results/default.aspx
- DuPont, Chemours and Corteva North Carolina PFAS settlement (September 2026): https://www.dupont.com/news/dupont-chemours-and-corteva-reach-agreement-to-resolve-pfas-related-claims-in-north-carolina.html, and Chemours 8-K dated 2026-09-10: https://www.sec.gov/Archives/edgar/data/0001627223/000162722326000029/cc-20260910.htm
- Cited to no document here, and not verifiable from the run outputs: the 2019, 2021 and 2022 portfolio separations under "What it is", and the 2021 Chemours MOU terms under "AGAINST".

## Engine 5.5 re-score (2026-10-19)
**No prior score existed.** DD was blocked on 2026-10-16 (`NEEDS_MAIN_AGENT: shares`) and never had a score.json, so its old record is "none (blocked)", as in the README's re-score table.

| | Old (origin/main) | New (engine 5.5.0, final run) |
|---|---|---|
| Base OE/share | none (blocked) | $4.80 (ttm_json) |
| Weighted IRR | none (blocked) | 6.61% |
| Tier | none (blocked) | D (band D → D; numbers tier D, no override) |
| Market cap | none (blocked) | $18.165B (score.json $18.17B), in scope |

**What the blocked run printed.** origin/main does carry the engine 5.4.0 dcf_numbers.json of 2026-10-16 (`data_gap` empty, never scored or published): price $132.70, base $4.80 (ttm_json), latest FY / 3-yr median OE/share $0.45 / $1.01 on the pre-split share basis, weighted IRR 6.59%, numbers tier D, market cap $55.628B (pre-split count × post-split price) and net debt / normalized OE 1.23x (HIGH_NET_DEBT silent). The base is the same ttm.json figure in both runs, and every scenario except the base case carries the same IV@15%. The weighted IRR moved only with the price ($132.70 → $130.00) and the lower base-case start (5.0% → 4.0%, reason under "DCF").

**Why it was blocked.** DuPont's 1-for-3 reverse split took effect after the FY2025 10-K. Engine 5.4 read the history on the pre-split basis (419,200,000 diluted), while the price and the TTM pin were post-split, and it printed a $55.628B market cap. The per-share history, the price and the cap were on different bases.

**What engine 5.5 changed for this filer:**
- **Share basis (ruling 2, split-basis check).**
  - **Split fact and confirmation:** the engine reads the filed split-ratio fact (ratio 0.333, dated 2026-06-30). It confirms the ratio against the post-split cover-page count: dei 135,042,975 on 2026-07-31, dei_to_shares 0.322145, matched to the ratio, confirmed against the FY2025 filed count.
  - **History rescaled:** it multiplies every history count FY2016–FY2025 by 0.333333 (CSV `shares_split_factor`) and raises SHARE_BASIS_ADJUSTED. The latest diluted count is now 139,733,333, and the 3-yr median OE/share reads $3.03 on that basis. (FY2016 still misses the 2019 split; see SHARE_BASIS_ADJUSTED under Flags.)
  - **TTM denominator:** ttm.py checks it too (`split_adjustment`); DD's Q2 2026 leg (137,200,000) is already post-split, so nothing is rescaled.
- **Market cap:** basis `diluted_latest_split_adjusted`, price × shares = **$18.165B**, in scope under $40B. judgment.json's `in_scope_under_40b: true` matches, and make_score accepted it. No ADS ratio applies.
- **Capex tags:** unchanged in the base years. FY2023–25 read `PaymentsToAcquireProductiveAssets` alone ($302.0M / $285.0M / $333.0M, intangibles $0.00). DuPont files no intangible-purchase or capital-improvement line. The additive-component rule adds `PaymentsToExploreAndDevelopOilAndGasProperties` in the FY2016–FY2018 history rows only (`used_tags.capex_components`, `capex_provenance`), so it touches neither the base nor the growth inputs. CAPEX_COVERAGE_LOW did not fire.
- **SBC tag:** `ShareBasedCompensation` equals `AllocatedShareBasedCompensationExpense` in every year both are filed, FY2022–FY2025 (sbc_provenance `share_ge_allocated`). Nothing was reconciled, and SBC_TAG_RECONCILED did not fire.
- **USD-override branch:** not applicable. DuPont is a USD 10-K filer with no overrides (`overrides_applied` is empty), and there is no FX conversion.
- **Leverage diagnostic:** the normalized-OE total is now computed on the same share count as the cap. Net debt / normalized OE reads 3.69x, and **HIGH_NET_DEBT now fires**. The blocked 5.4 run multiplied the post-split TTM pin by the pre-split count; that overstated normalized OE about threefold and kept the flag silent at 1.23x.

**New 5.5 flags, resolved by name:**
- **SHARE_BASIS_ADJUSTED:** the 1-for-3 reverse split effective June 24, 2026 (Q2 2026 10-Q). The cover-page count confirms it, and the TTM denominator (137,200,000) is already post-split. Full resolution, with the FY2016 qualification, under Flags above.
- **HIGH_NET_DEBT**, newly visible because of the basis fix. It fires on the FY2025 balance sheet (net debt $2.479B). The Aramids proceeds have since reduced leverage, and the bear cases are stressed. Full resolution under Flags above.

**Why the tier is D.** On one consistent share basis, the TTM base of $4.80/share against a $130.00 price gives an OE yield of 3.69%. The weighted IRR is 6.61%, and the whole band (bear 5.49% → bull 8.19%) sits in Tier D. Only the super-bull path (10% weight, 10.46%) reaches Tier C. The 15% hurdle price is $41.82. No base choice changes the tier: the median base ($3.03) is lower, and even the super-bull IV@15% ($79.13) is below the price. So D stands with no override, as ruled.
