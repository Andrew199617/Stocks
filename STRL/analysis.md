# STRL — Sterling Infrastructure, Inc.
v5 / engine 5.4 run, 2026-10-16. In scope: market cap $13,132,668,920 at $424.36 (nasdaq_quote_api) — under the $40B cutoff.

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.json, fundamentals.json, or financials_history.csv — none are recomputed.

## What it is
Specialty infrastructure contractor in three segments. E-Infrastructure Solutions (site development plus mission-critical electrical for data centers, semiconductor fabs, manufacturing and distribution) was 58.9% of FY2025 revenue ($1,466,777,000 of $2,490,049,000, segments.json) and is the whole growth story; Transportation Solutions $640,674,000 (25.7%, shrinking by design as resources shift to E-Infrastructure); Building Solutions $382,598,000 (15.4%, residential concrete/plumbing in Sun Belt markets, soft with housing). The company has pivoted from low-margin heavy-highway work to mission-critical builds: gross margin expanded every year from 14.4% (FY2021) to 23.0% (FY2025), TTM 23.8% (fundamentals.json).

## Owner's earnings
**FY2025 (10-K via EDGAR, financials_history.csv):** operating cash flow $439,988,000; capex $77,312,000; SBC $24,181,000 (always a real cost).
- **Conservative owner's earnings FY2025: $338,495,000 = $10.94/share** (base_oe_latest_per_share $10.937893818463825).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $284,593,000 for FY2025 — below the conservative figure, a reminder that the OCF version is not the harshest lens here.
- OE positive 5 of the last 5 fiscal years. Balance sheet is net cash: net debt −$99,672,000 (cash $390,721,000 vs debt $291,049,000 at FY2025), lease liabilities $58,865,000 — leverage is not the risk in this name.
- History caveat: OE/share stepped from $4.76 (FY2022) to $12.80 (FY2023) and $12.75 (FY2024), then fell to $10.94 (FY2025) even as net income rose — the 2023–24 OCF was flattered by working-capital inflows that faded in 2025 (see NI_OCF_DIVERGENCE below). The engine's normalized base (3-yr median) is $12.751139793231875/share and inherits some of that flattery.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $439,988,000 − prior YTD $170,311,000 + current YTD $328,021,000 = **TTM $597,698,000**
- Capex: FY $77,312,000 − prior YTD $31,262,000 + current YTD $69,646,000 = **TTM $115,696,000**
- SBC: FY $24,181,000 − prior YTD $12,278,000 + current YTD $15,639,000 = **TTM $27,542,000**
- Shares (current-YTD weighted diluted): **31,110,000**
- **TTM OE total $454,460,000 → base OE/share $14.608164577306333** (base_source: ttm_json)
- The TTM base is above both the latest FY ($10.94) and the median ($12.75) because H1 2026 was a genuine step-up quarter-set (Q2 2026 revenue $1.17B, +90% YoY, ~50% organic with the rest from the CEC Facilities and Stone Ridge acquisitions; H1 OCF $328,021,000 vs $170,311,000 a year earlier). It is used because it is the most current filing-derived base, and the scenario multipliers/bear weight below carry the cyclicality discount instead.

## Moat: 5/10 — moderate/narrow
Justification: an execution-and-integration edge in a per-project bid business — real enough to have expanded gross margin ~9pp in four years and hold ROIC well above the cost of capital recently, but with no recurring revenue, no network effects, and larger rivals (Quanta, MasTec, EMCOR) able to contest every award.
- Evidence (fundamentals.json): ROIC proxy (after-tax operating income over equity + debt − cash) ran 12.4% (FY2020), 11.3% (FY2021), 17.4% (FY2022), 33.3% (FY2023), 45.4% (FY2024), 31.8% (FY2025). Gross margin: 14.6% / 14.4% / 15.5% / 17.1% / 20.1% / 23.0% over FY2020–FY2025, TTM 23.8%. The recent ROIC is genuinely strong but is a peak-cycle, mix-shifted print — through-cycle (FY2020–21) it was ~11–12%, which is why this is a 5 and not a 7+: the high recent ROIC has not yet survived a downturn in hyperscaler capex.
- FOR: Integrated "site + shell" model — winning site development gives pole position on the higher-value electrical/mechanical phases (CEC Facilities acquisition), compressing customer schedules, which is what mission-critical buyers pay for; proven execution reputation with repeat hyperscaler/manufacturing customers (92% of E-Infrastructure backlog is mission-critical); signed backlog $4.33B at 2026-06-30 (+116% YoY, combined backlog $5.62B) gives multi-year revenue visibility few contractors have; disciplined bid selection — walking away from low-bid transportation work while segment margins rose.
- AGAINST: Per-project competitive bidding — no recurring revenue, no switching costs beyond a single project, every dollar of backlog must be re-won; customer and cycle concentration — growth is now a leveraged bet on hyperscaler data-center capex, one capex pause hits the 59% segment first; scale disadvantage vs Quanta/MasTec/EMCOR on the largest campuses; labor-constrained execution — margins depend on scarce skilled crews, and rapid growth plus two acquisitions (CEC, Stone Ridge) strains exactly that; Building Solutions tied to soft Sun Belt housing.
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — final run (2026-10-16, engine 5.4.0, --ttm)
**Growth sanity check (mandatory):** the engine's blended growth is 13.22% (rev CAGR 5y 15.21%, 3y 12.06%, latest YoY 17.69%, OE/share CAGR 2y −7.57% — the OE component is distorted by the 2023–24 working-capital flattery falling out). Every component is backward-looking and misses the current inflection: Q2 2026 revenue printed +90% YoY, FY2026 guidance is revenue $4.00–$4.15B (+61–67% vs FY2025) and diluted EPS $17.25–$17.85 (vs $9.38 in FY2025). Scenario starts were therefore recalibrated upward to 0 / 8 / **18** / 28 / 38% (offsets −0.1322 / −0.0522 / +0.0478 / +0.1478 / +0.2478 vs the blend). Written reason the starts sit far below the +90% prints: those prints annualize the CEC/Stone Ridge acquisitions and convert a backlog that doubled — the TTM base already captures H1 2026, and g_start is the growth rate *off that stepped-up base* for the following two years; extrapolating +90% would double-count the acquisition step. Even the super-bull start (38%) assumes backlog conversion stays exceptional. Probabilities shifted bear-ward for a cyclical contractor at a peak multiple (15/25/30/20/10, 40% on bear-or-worse, per OE_VOLATILE); OE multipliers are the defaults 0.75/0.90/1.00/1.10/1.25. Price $424.36.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | 0.0% | 0.75 | Hyperscaler capex pauses; backlog converts slowly, margins give back the mix gains | $80.94 | 4.82% |
| Bear | 25% | 8.0% | 0.90 | Data-center work normalizes to high-single-digit growth; WC tailwind gone | $135.43 | 6.67% |
| Base | 30% | 18.0% | 1.00 | Backlog converts on schedule; growth fades over the 8.5-yr CAP as the cycle matures | $226.49 | 9.65% |
| Bull | 20% | 28.0% | 1.10 | Backlog + future phases keep growth near 30%; integrated model gains share | $371.45 | 13.70% |
| Super bull | 10% | 38.0% | 1.25 | Multi-year AI buildout at full tilt; Sterling compounds off the stepped-up base | $622.51 | 19.22% |

- **Probability-weighted: IV@15% $250.49 (−41.0% vs price), IV@12% $345.39, IV@10% $452.74, weighted IRR 10.44%, base-case IRR 9.65%**
- **Tier by numbers: C.** Bear tier D (6.67%), bull tier C (13.70%) — see TIER_BAND. Diagnostics (dcf_numbers.json): OE yield 3.44%, terminal value 22.5% of IV@15%, scenario spread 7.69x, net debt −0.22x normalized OE, 9.5 months since FY end.
- Hurdle prices (weighted): clears 15% at $250.49, 20% at $167.24, 25% at $122.92. Even the super-bull case (19.22% IRR) does not clear 20% at $424.36.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.5 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, legs quoted above.
- **OE_VOLATILE** (OE/share spans >3x over 5 years: $2.78 → $3.45 → $4.76 → $12.80 → $12.75 → $10.94): real cyclicality plus a mix break, not noise — the 2023 step-up is margin mix (E-Infrastructure) plus working-capital inflows, and 2025 shows the WC leg reversing. Handled with the TTM base, 40% probability on bear-or-worse, and a super-bear OE multiplier of 0.75.
- **NI_OCF_DIVERGENCE** (NI vs OCF differ >40% in 2023, 2024): found — working capital, not earnings quality fraud. In 2023 OCF was $478,584,000 vs net income $138,655,000: the 10-K cash-flow statement shows changes in working capital contributed roughly $253M (contract liabilities / billings build as large E-Infrastructure projects ramped), plus D&A $57,403,000 and SBC $14,622,000. In 2024 OCF was $497,104,000 vs net income $257,461,000: working capital contributed roughly $200M, partly offset in the NI line by the $91.289M non-cash gain on deconsolidation of the RHB joint venture (which inflates NI, not OCF). By 2025 the WC contribution faded to roughly $9M and OCF ($439,988,000) sat much closer to net income ($290,153,000). Consequence: the 2023–24 OE bases are flattered and the 2-yr OE/share CAGR (−7.57%) is an artifact of that flattery rolling off — which is why the growth blend was recalibrated on revenue/backlog/guidance evidence instead, and why no high confidence is claimed for any OE base in this name.
- **WIDE_SCENARIO_SPREAD** (super-bull IV 7.69x super-bear IV): real — the outcome genuinely hinges on the duration of the hyperscaler capex cycle. Confidence is low and the verdict is sized to the conservative end.
- **TIER_BAND** (bear tier D at 6.67% vs bull tier C at 13.70%): the verdict spans tiers; any position sizing should use the bear end. The weighted result (C, 10.44%) sits between, closer to bear than bull.

## My thoughts / overlay
- Method range is the honest headline: the preliminary run (median base $12.75, engine-default growth/probabilities) printed weighted IRR 8.05%, IV@15% $173.95, Tier D. The final run — TTM base, growth recalibrated to the backlog/guidance evidence, bear weight raised — prints 10.44% / $250.49 / Tier C. Defensible methods span **D to C**; no defensible run gets near the $424.36 price, and even the super-bull scenario only reaches 19.22%.
- The business quality is not the debate: net cash, gross margin up ~9pp in four years, backlog $4.33B signed, FY2026 guidance implying EPS nearly doubles. The debate is price and cycle duration: at $424.36 the stock trades at roughly 29x the TTM OE/share base and already pays for years of backlog conversion going right. The stock printed a $1,005.68 twelve-month high before pulling back to here (search result, MarketBeat via Cantor note) — the pullback has not made it cheap on owner's earnings, it has made it less extreme.
- Street disagreement is noted for the record: street.json shows a Buy consensus with mean target $814.83 — the Street is capitalizing guided EPS growth at a contractor-premium multiple; this sweep's owner's-earnings lens, with SBC charged and growth faded over an 8.5-year CAP, does not follow it there.
- Risks: hyperscaler capex concentration (92% mission-critical backlog cuts both ways), acquisition integration (CEC, Stone Ridge contributed $250.8M of Q2 revenue — bought growth must convert to organic), skilled-labor constraints, Transportation/Building drag if housing stays soft, and 2026 capex guidance raised to $130–140M, which pressures near-term OE conversion.
- Margin of safety: none at this price on the weighted case — the price is 69% above the weighted IV@15% ($424.36 vs $250.49). A buyer here needs the bull-to-super-bull path, not the base case.

## Final verdict
- **Final tier: C** (weighted IRR 10.44% on the final inputs; method range D to C, bear band D — size any interest to the bear end)
- Confidence: **Low** (filing data is clean and the TTM base is solid, but OE is WC-volatile, the scenario spread is 7.69x, and the result is dominated by how long the data-center capex cycle runs)
- One-liner: High-quality cyclical contractor, moat 5/10 — record backlog and a real margin inflection, but at $424.36 it does not clear 15% (10.4% weighted, IV $250); it clears 15% only at or below ~$250.
