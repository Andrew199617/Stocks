# WMG — Warner Music Group Corp.
5.4 run, 2026-10-17. In scope (market cap $16.344B at $31.40, nasdaq_quote_api). First pass; the preliminary run exited 4 with `DATA_GAP:shares` and was unblocked by a filing override — see OVERRIDE.

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.json, or financials_history.csv — none are recomputed.

## What it is
One of the three global music majors: Recorded Music (FY2025 revenue $5,408M — digital/streaming, physical, artist services, licensing) and Music Publishing / Warner Chappell ($1,306M — performance, digital, mechanical, sync), on FY2025 total revenue of $6,707M. Controlled by Access Industries (Class B, 375,380 thousand of the 520,508 thousand weighted shares); only Class A trades. Current story is a margin-expansion one: a $300M annualized cost-reduction program, DSP renewals with better economics, and guided FY2026 Adjusted OIBDA margin expansion of 150-200bp.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $678,000,000; capex $139,000,000; SBC $54,000,000 (always a real cost).
- **Conservative owner's earnings FY2025: $485,000,000 = $0.93/share** (key_numbers.md: latest FY OE/share $0.93, latest FY OE total $485.0M)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $617,000,000 total — above the conservative figure, so the conservative series is the binding one.
- OE positive 5 of the last 5 fiscal years. Net debt $3,531,000,000 (key_numbers.md), lease liabilities $243,000,000. Dividends paid TTM $400M (fundamentals.json) consume over half of TTM OE — the equity is priced as a growth asset while cash is paid out like a yield asset, on a levered balance sheet.

**Base used = TTM owner's earnings through Q3 FY2026 (period ended 2026-06-30), from ttm.py (filing-direct, no hand math):**
- OCF: FY $678,000,000 − prior YTD $447,000,000 + current YTD $708,000,000 = **TTM $939,000,000**
- Capex: FY $139,000,000 − prior YTD $111,000,000 + current YTD $75,000,000 = **TTM $103,000,000**
- SBC: FY $54,000,000 − prior YTD $1,000,000 + current YTD $40,389,041 (override-prorated leg, see OVERRIDE) = **TTM $93,389,041** — see the artifact note under Flags: this leg overstates SBC, so the TTM base is a floor, not a ceiling.
- Shares (override, FY2025 two-class total from the 10-K EPS note): **520,508,000**
- **TTM OE total $742,610,959 → base OE/share $1.43** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $0.98/share — rejected as the base because FY2026 is a genuine step-up, not noise: the current-YTD OCF leg alone ($708M for nine months) already exceeds all of FY2025 ($678M), nine-month FY2026 revenue grew 12% YoY and Q3 FY2026 revenue 10% (company releases), and fundamentals.json puts TTM revenue at $7,304M, +12.9% YoY. The median is retained in key_numbers.md and in the method range below.

## OVERRIDE — shares (filing), and the SBC leg fill
- **The gap:** WMG reports EPS under the two-class method (Class A / Class B); no single aggregated diluted share tag survives into EDGAR companyfacts, so the preliminary engine run exited 4 with `DATA_GAP:shares` for FY2023, FY2024, FY2025 — no tier, correctly. The zero-fill baseline in that run printed a nonsense base of $274,714.83/share, which is what the gate exists to prevent.
- **The decision (bounded authority (a), kind "filing"):** judgment.json carries `shares_override = 520,508,000` — the FY2025 weighted-average total from the filer's own 10-K, Note 3 (Earnings per Share): Class A 145,128 thousand + Class B 375,380 thousand. The same note gives FY2024 517,523 thousand and FY2023 515,720 thousand and states potentially dilutive shares had no dilutive effect in FY2023-FY2025 (the FY2025 diluted denominator adds only ~397 shares), so basic = diluted and the two-class sum is the diluted count. The engine applies the single value to every missing period: it overstates the FY2023/FY2024 counts by 0.9%/0.6% versus the note's own totals (conservative — it understates OE/share slightly) and the ungated 2020-2022 history counts by ~1-3%.
- **Out-of-band, acknowledged:** the override check flags out_of_band because there is no filed diluted value at all to band against (last_filed_value: null); judgment.json carries an ack_reason stating exactly that — the value is the filer's printed EPS-note total, not an estimate.
- **Measured impact (key_numbers.md):** unblocks the tier — YES; without it there is no score at all. On the TTM base actually used, base OE/share is $1.43 with the override and undefined without it.
- **sbc_override (filing, $54,000,000):** annual SBC is filed for every year, so this fills nothing in the annual run and is exactly the last filed value (in-band). It exists for ttm.py: companyfacts carries no post-FY YTD SBC fact for the FY2026 10-Q periods, and ttm.py's documented assembly fills the missing current-YTD leg with the filed annual value prorated by days ($40,389,041 over 273 days). Filed legs always win where they exist.

## Moat: 6/10 — moderate-strong, not wide
Justification: one of the three majors, with an evergreen catalog and publishing copyrights that monetize every format shift and proven DSP pricing power — capped at 6 because it is the number-three major, distribution belongs to the DSPs, and a decade of ~46-48% gross margin shows pricing gains are shared, not kept.
- FOR: evergreen recorded catalog + Warner Chappell publishing copyrights — long-lived scarce IP (streaming, social, sync, now AI licensing, e.g. the Suno settlement-to-license path); proven DSP pricing power — FY2026 renewals carry contractual per-subscriber minimum increases and Q3 FY2026 subscription streaming grew 12.5%; returns through a cycle — ROIC proxy (fundamentals.json) 14.2% / 16.2% / 15.7% / 17.1% / 12.5% across FY2021-FY2025, gross margin ~46-48% for ten straight years; two-engine mix — Recorded Music $5,408M plus steadier publishing royalties $1,306M in FY2025.
- AGAINST: distribution belongs to the DSPs, who control the customer and take their cut first; number-three major, subscale vs Universal and Sony; hit-driven frontline with rising artist advances/royalties and AI-generated supply; levered, controlled equity — net debt $3,531M (4.75x normalized OE), leases $243M, Access Industries control; no gross-margin expansion in a decade, OE margin capped at 7-9% of revenue.
- A 6 gives CAP = 9.8 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 9.8 years, 15-year projection.

## DCF — 5.4 final run (2026-10-17)
Default scenario parameters kept (probabilities 10/25/30/25/10, growth offsets −12/−5/0/+5/+12pp vs the 4.31% blend, OE multipliers 0.75/0.90/1.00/1.10/1.25). **Growth sanity check, with the written reason the spec requires:** the base start (4.3%) sits below the latest prints — TTM revenue +12.9% YoY (fundamentals.json), Q3 FY2026 revenue +10%, subscription streaming +12.5% — deliberately. The TTM base pin already capitalizes the FY2026 step-up (base $1.43 vs normalized $0.98, +45%), including the guided 150-200bp of margin expansion now landing; projecting double-digit OE growth on top of that elevated base would double-count the step-up. Forward growth from the higher base reverts toward the filed revenue signals (5y CAGR 8.49%, 3y 4.25%, latest FY YoY 4.37%). The bull start (9.3%) sits at the current revenue print and the super-bull start (16.3%) above it, so the upside cases are not starved. Price $31.40.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -7.7% | 0.75 | Streaming growth stalls, DSP terms reverse, leverage bites | $5.58 | 4.38% |
| Bear | 25% | -0.7% | 0.90 | Step-up fades, OE flatlines at FY2025 levels | $9.14 | 6.00% |
| Base | 30% | 4.3% | 1.00 | Mid-single-digit growth off the TTM base over the CAP | $12.68 | 7.63% |
| Bull | 25% | 9.3% | 1.10 | Current ~10% revenue growth persists, margins expand as guided | $17.43 | 9.72% |
| Super bull | 10% | 16.3% | 1.25 | Sustained double-digit growth + full $300M savings + AI licensing upside | $27.00 | 13.47% |

- **Probability-weighted: IV@15% $13.70 (−56.4% vs price), IV@12% $18.27, IV@10% $23.38, weighted IRR 8.14%, base-case IRR 7.63%**
- **Tier by numbers: D — and the band is D at both ends (bear tier D, bull tier D).** Diagnostics (key_numbers.md): OE yield 4.54%, terminal value 19.1% of IV@15%, scenario spread 4.84x, net debt 4.75x normalized OE, 12.5 months since FY end.
- Hurdle-clearing prices (weighted path): 15% at $13.70 · 20% at $9.61 · 25% at $7.37.

## Flags — every fragility flag resolved
- **STALE_FY** (latest FY ended 12.5 months ago): resolved by construction — the base is the TTM figure from ttm.py through 2026-06-30, legs quoted above. One leg needs a caveat: the SBC prior-YTD leg is a filed $1,000,000 ShareBasedCompensation fact that cannot be the company's real nine-month stock comp (the Q3 FY2025 10-Q equity statement shows $49M of stock-based compensation expense for that period, and the FY2025 total was $54M). ttm.py therefore overstates TTM SBC ($93.4M) and understates TTM OE by roughly $48M (~$0.09/share). The error runs against the stock — the $1.43 base is a floor — and it does not change the tier: even crediting it back, no scenario reaches 15%.
- **SHARES_FALLBACK** (2016-2019): those years' fallback counts in the preliminary history were dei/outstanding figures on an unusable scale (the dei series still shows 1,069 as of 2020-01-31). In the final history the shares override supersedes them (periods_filled covers all ten years), but per-share history for 2016-2019 remains approximate — a single FY2025 count is applied to years whose true counts were ~502-506M. The gated years and the base do not depend on those history years.
- **OVERRIDE_APPLIED:shares**: see OVERRIDE — gap, decision, band acknowledgment and measured impact are recorded in judgment.json, dcf_numbers.json and score.json, not just here.
- **WIDE_SCENARIO_SPREAD** (4.84x): real — the spread is mostly the leverage-and-step-up question (does FY2026 OE hold?) rather than model noise. Confidence is capped at medium, and the verdict needs no sizing adjustment: every scenario, bear to bull, is Tier D.
- **HIGH_NET_DEBT** (net debt 4.75x normalized OE): balance sheet from the FY2025 10-K as filed in the engine history — total debt $4,063M against cash $532M = net debt $3,531M, plus $243M lease liabilities. Post-FY2025, subsidiary debt tied to the Tempo Music acquisition and the Bain Capital catalog JV (Beethoven) is stated by the company to be nonrecourse to WMG. Even so, at 4.75x the levered bear cases are the stress test, and they print IV@15% of $9.14 (bear) and $5.58 (super bear) — the leverage is a reason the D is robust, not a reason to soften it.

## My thoughts / method range
- Method range: the engine-native median base ($0.98/share, preliminary final-config run at default moat 5) printed weighted IV@15% $9.30 and weighted IRR 6.33%; the TTM base used here prints $13.70 / 8.14%. Both are Tier D, and the SBC artifact note above means the TTM end is if anything understated. The range is D to D — unusually, the method debate does not matter.
- The market is paying $31.40 for a super-bull outcome and not getting one: the super-bull case (16.3% growth start, 1.25x OE) earns 13.47% and values at $27.00, still below the price. At $31.40 the buyer needs growth and margins beyond every scenario the engine was given.
- Quality is real but rented: mid-teens ROIC and a decade-stable gross margin on copyrights that do not expire economically — but the customer relationship, the shelf and the price umbrella all belong to the DSPs, and the equity sits behind $3.5B of net debt and a controlling holder while paying out $400M/yr in dividends.
- What would change the verdict: a price near the $13.70 hurdle, or evidence the FY2026 OE step-up compounds (a second year of double-digit revenue growth with OE margin breaking above ~10%) rather than annualizing a one-off margin program.

## Final verdict
- **Final tier: D** (weighted IRR 8.14%; bear and bull cases both D; clears 15% only at ~$13.70 vs the $31.40 price)
- Confidence: **Medium** (filing-direct TTM base with one documented, conservative-direction leg artifact; scenario spread 4.84x bars high)
- One-liner: Durable catalog/publishing major, moat 6/10 — even on the stepped-up TTM base of $1.43/share it clears 15% only at ~$13.70 vs the $31.40 price (weighted IRR 8.14%, IV@15% $13.70, Tier D); even the super-bull case earns only 13.5%.
