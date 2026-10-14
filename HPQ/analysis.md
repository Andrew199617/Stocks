# HPQ — HP INC.
v5 run, 2026-10-14. In scope (market cap $28.811B at $30.2323, nasdaq_quote_api — under the $40B cutoff).

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.py output (ttm.json), financials_history.csv, or the cited search results — none are recomputed.

## What it is
Personal computers and printing: Personal Systems (consumer and commercial PCs, workstations, peripherals/AI PCs) and Printing (home and office printers, supplies/cartridges, managed print and industrial print). In fiscal Q3 2026 (ended 2026-07-31, search result), net revenue was $15.7B, up 12.5% year over year — Personal Systems $11.8B, up 18%, with a 4.6% operating margin; Printing $3.9B, down 2%, with an 18.1% operating margin. Nine-month FY2026 revenue was $44.5B, up 10% (search result). The revenue growth was price/mix driven: unit volumes fell even as average selling prices rose on AI-PC mix, and non-GAAP EPS included a $0.11/share tariff-refund benefit in Q3 (search result) — a one-off tailwind, not run-rate earnings power. Management raised FY2026 free-cash-flow guidance to $3.0–$3.2B (search result).

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $3,697,000,000; capex $897,000,000 (tag PaymentsToAcquireProductiveAssets); SBC $522,000,000 (always a real cost).
- **Conservative owner's earnings FY2025: $2,278,000,000 = $2.39/share latest FY** (dcf_numbers.json: base_oe_total_latest_fy $2,278,000,000; base_oe_latest_per_share $2.3903).
- Maintenance version FY2025 (from financials_history.csv): $2,439,000,000 — same ballpark as the conservative figure.
- OE positive 5 of the last 5 fiscal years. Net debt $5,976,000,000 (dcf_numbers.json); final-run diagnostics put net debt at 1.71x normalized OE.
- Historical growth is weak: revenue CAGR 5y −0.48%, revenue CAGR 3y −4.21%, latest FY revenue YoY +3.24%, OE/share CAGR 2y −2.99%, blended growth −1.73% before the share-count adjustment (dcf_numbers.json growth components).

**Base used = TTM owner's earnings through Q3 FY2026, from ttm.py (filing-direct, no hand math), because FY2025 ended 11.43 months ago (STALE_FY):**
- OCF: FY $3,697,000,000 − prior YTD $2,073,000,000 + current YTD $3,044,000,000 = **TTM $4,668,000,000**
- Capex: FY $897,000,000 − prior YTD $700,000,000 + current YTD $590,000,000 = **TTM $787,000,000**
- SBC: FY $522,000,000 − prior YTD $432,000,000 + current YTD $389,000,000 = **TTM $479,000,000**
- Shares (current-YTD weighted diluted): **927,000,000**
- **TTM OE total $3,402,000,000 → base OE/share $3.6699** (base_source: ttm_json)
- The engine's normalized base (median of last 3 FY OE/share) is $2.54/share. The TTM base is materially higher than both the median and the latest FY ($2.39) — it reflects the strong 9M FY2026 operating cash flow, lower capex and SBC in the current YTD legs, and a smaller share count. It is used as instructed for a stale FY, but it is the single most generous input in this run: it likely flatters run-rate OE because the period includes tariff-refund benefits and ASP/pull-forward PC demand (see FLAGS and Thoughts). The preliminary median-base run (moat 5, default probabilities) gave a weighted IRR of 11.38% and weighted IV@15% of $21.38 — also Tier C, which bounds the method range for this name to Tier C on both bases tried.

## Moat: 4/10 — weak to moderate
Justification: scale as the #2 global PC vendor and the #1 print vendor with a high-margin supplies annuity and commercial channel/service relationships, but PC hardware is commoditized (no OS or chip control, thin Personal Systems margins), switching costs are low outside managed commercial fleets, and printing is in secular decline against Lenovo/Dell/Apple competition and digitization.
- FOR: #2 global PC vendor at scale — global distribution and channel strength; #1 in print (33.5% global share cited on the Q1 FY2026 call, search result) with a high-margin supplies/cartridge annuity on the installed base; commercial fleet and managed-print relationships with service attach; Printing operating margin far above Personal Systems (18.1% vs 4.6% in Q3 FY26).
- AGAINST: PC hardware commoditized — no OS/chip control, thin Personal Systems margins; printing in secular decline (Q3 FY26 printing revenue down 2%, supplies down 3% and hardware units down 7% per search results); low switching costs outside managed commercial fleets, with Lenovo, Dell and Apple competing on price and premium positioning; memory/component cost inflation and tariff exposure squeezing gross margin (Q3 FY26 gross margin 18.8% vs 20.5% a year earlier, search result); recent growth is ASP/pull-forward driven while unit shipments fall sharply (preliminary calendar Q3 2026 HP PC shipments down 30.9% year over year, search result).
- A 4 gives CAP = 7.2 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 7.2 years, 15-year projection.

## DCF — v5 final run (2026-10-14)
Engine inputs: g_base 1.44% (blended growth −1.73% plus a +3.18pp share-count adjustment for the shrinking share count). Growth sanity check: the base start (1.44%) sits well below the latest prints (FY2025 revenue +3.24%; 9M FY2026 revenue +10%; Q3 FY2026 revenue +12.5%). Written reason: those prints are ASP/pull-forward driven, not volume — Q3 FY2026 revenue rose while units fell, Q3 non-GAAP EPS carried a $0.11 tariff-refund benefit, GAAP EPS fell year over year in Q3 despite the revenue gain, and preliminary calendar-Q3 shipments then fell 30.9%. Long-run revenue CAGRs are negative (5y −0.48%, 3y −4.21%) and printing declines secularly, so a low-single-digit OE growth start is the honest center, not conservatism for its own sake. The super-bull start (13.44%) sits just above the latest quarter's revenue print, so no scenario start is below what the company just printed without the reason above. Probabilities were skewed bearish versus the 10/25/30/25/10 defaults — 15/30/30/20/5 — because the TTM base is generous (tariff refunds, pull-forward demand), printing is shrinking, and the post-period shipment data deteriorated. OE multipliers are the defaults 0.75/0.90/1.00/1.10/1.25. Price $30.2323.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | -10.00% | 0.75 | PC pull-forward unwinds hard; print decline accelerates; memory costs bite | $13.84 | 7.78% |
| Bear | 30% | -3.56% | 0.90 | Refresh fades, units keep falling, supplies keep shrinking | $21.41 | 11.20% |
| Base | 30% | 1.44% | 1.00 | Flat-to-low growth on the TTM base; buybacks offset print decay | $28.89 | 14.44% |
| Bull | 20% | 6.44% | 1.10 | AI-PC ASP mix holds and commercial refresh extends | $38.50 | 18.29% |
| Super bull | 5% | 13.44% | 1.25 | Durable AI-PC cycle plus a print stabilization that has not been printed yet | $56.93 | 24.74% |

- **Probability-weighted: IV@15% $27.71 (−8.33% vs price), IV@12% $36.41, IV@10% $46.07, weighted IRR 13.95%, base-case IRR 14.44%**
- **Tier by numbers: C.** Diagnostics (dcf_numbers.json): OE yield 12.14%, terminal value 17.66% of IV@15%, scenario spread 4.11x, net debt 1.71x normalized OE, 11.43 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (latest fiscal year ended 11 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q3 FY2026 (ytd_end 2026-07-31), with all four legs quoted above. Caveat carried into the probabilities: the TTM window includes tariff-refund benefits and pull-forward PC demand, so the bearish probability skew is the offset, not a change to the filing-derived base.
- **BUYBACK_TAILWIND** (share count shrinking 3.2%/yr): already credited via the +3.18pp share-count adjustment inside g_base (share CAGR −3.18%); not double-counted in the verdict. TTM shares (927,000,000) are also below the latest FY count (953,000,000) in the filing data.
- **WIDE_SCENARIO_SPREAD** (super-bull IV 4.11x super-bear IV): real — the range runs from a post-refresh air-pocket to a durable AI-PC cycle. Confidence is therefore capped at medium, and the verdict is sized to the weighted case, not the bull cases.

## My thoughts / overlay
- Quality is middling, not broken: OE positive 5/5 years, the maintenance and conservative OE definitions agree in FY2025, and buybacks steadily shrink the count. The problem is growth and durability, not current cash generation — 5y and 3y revenue CAGRs are negative and the profit pool leans on a printing segment that shrinks every year.
- The balance sheet is a real input, not a footnote: net debt $5,976,000,000 at 1.71x normalized OE on the final run. That is manageable for a cash generator of this size, but it leaves less room when the PC cycle turns down, and it is part of why the super-bear case is weighted 15%.
- Method range: both bases tried land in Tier C — 11.38% weighted IRR on the median base (preliminary run) and 13.95% on the TTM base (final run). The TTM run is the headline because the FY is stale, but nobody should quote 13.95% without noting that the median-base run is almost 2.6 points lower and that the TTM base embeds one-off tariff/pull-forward help.
- Hurdle math: the weighted IV@15% is $27.71, so HP clears Andrew's 15% hurdle at or below $27.71 on these inputs — the $30.2323 price sits above that. With a margin of safety against the wide scenario spread, a buyer would want a price closer to the bear-case IV@15% of $21.41; at the current price the base case (14.44% IRR) does the heavy lifting and it still falls short of 15%.

## Final verdict
- **Final tier: C** (weighted IRR 13.95% on the v5 final inputs; Tier C on the median base as well)
- Confidence: **Medium** (capped by WIDE_SCENARIO_SPREAD; high on the filing-derived TTM inputs, low on how much of the TTM step-up is run-rate)
- One-liner: Mature cash generator, moat 4/10 — on a TTM base it comes close but does not clear 15% (13.95% weighted IRR, IV@15% $27.71 vs $30.23 price); it clears 15% at or below $27.71.
