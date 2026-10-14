# TDY — Teledyne Technologies Incorporated
v5 run, 2026-10-14. In scope (market cap $28.815B at $607.91, nasdaq_quote_api). This run carries one filing-sourced override — see OVERRIDE.

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.py output (ttm.json), financials_history.csv, or a cited search result — none are recomputed.

## What it is
Diversified high-technology conglomerate in sensors and instrumentation, four segments: Digital Imaging (anchored by FLIR thermal imaging), Instrumentation, Aerospace & Defense Electronics, and Engineered Systems. Q2 2026 (search: Teledyne Q2 2026 release summaries) was a record quarter: sales $1,662.5M, +9.8% YoY, non-GAAP EPS $6.28, funded backlog ~$5.0B, book-to-bill 1.23, and full-year 2026 guidance raised to just under $6.53B of revenue (~7% growth) with non-GAAP EPS guided to $24.45–$24.65.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** revenue $6,115,400,000; net income $894,800,000; operating cash flow $1,191,300,000; capex $117,300,000; SBC $39,600,000 — by override, see below (SBC is always a real cost).
- **Conservative owner's earnings FY2025: $1,034,400,000 = $21.82/share** (key_numbers.md: latest FY OE/share $21.82)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $854,100,000 — below the conservative figure because FY2025 carried a $259,700,000 increase in net working capital (financials_history.csv); the OCF-based conservative figure is the cleaner base here.
- OE positive 5 of the last 5 fiscal years. Net debt $2.123B (key_numbers.md), 1.90x normalized OE — and falling: the Q2 2026 release summaries (search) put net debt at $1,686.9M at the end of Q2 2026 after $450.0M of debt repayment in that quarter.
- SBC load is small and stable: the 10-K cash-flow statement prints $32.3M (FY2023) / $37.7M (FY2024) / $39.6M (FY2025) against OCF above $1.1B in the last two years — dilution is not the story here; share count CAGR is −0.21%/yr (key_numbers.md).

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $1,191,300,000 − prior YTD $469,200,000 + current YTD $549,200,000 = **TTM $1,271,300,000**
- Capex: FY $117,300,000 − prior YTD $48,300,000 + current YTD $60,200,000 = **TTM $129,200,000**
- SBC: FY leg filled by the override (prorated $39,491,507) − prior YTD $20,200,000 + current YTD $19,500,000 = **TTM $38,791,507**
- Shares (current-YTD weighted diluted): **46,900,000**
- **TTM OE total $1,103,308,493 → base OE/share $23.52** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $21.82/share — the same value as the latest FY, and the median year is FY2025 itself, where the SBC override equals the true filed figure exactly. The TTM base is used because it is higher, more current, and still filing-derived; using the lower median would only deepen the Tier D result.

## OVERRIDE — sbc (filing-sourced, bounded authority)
- **The gap:** the preliminary engine run exited 4 with `DATA_GAP:sbc` — no annual-duration SBC fact exists under the engine's tags for fiscal 2023, 2024 or 2025 (EDGAR companyfacts carries the expense only as quarterly/segment AllocatedShareBasedCompensationExpense facts; the 9M 2025 figure of $30.7M in the Q3 2025 10-Q cash-flow statement matches the same series). No tier was emitted, correctly.
- **The decision (worker, under the 2026-10-14 bounded authority, kind "filing"):** judgment.json carries `sbc_override = {value: 39600000, kind: "filing", source: "Form 10-K for fiscal year ended December 28, 2025 (filed 2026-02-20, accession 0001094285-26-000017), Consolidated Statements of Cash Flows: 'Stock-based compensation' $39.6 million for FY2025, $37.7 million for FY2024 and $32.3 million for FY2023 …"}`. The override fills ONLY periods where the tag is absent (sbc_tag = "OVERRIDE" in financials_history.csv); filed values are never replaced. Applying the FY2025 value to the earlier missing years overstates their SBC versus the true $32.3M/$37.7M series — conservative, and immaterial to the base (see the measured impact).
- **Measured impact (key_numbers.md, on the TTM base actually used):** base OE/share $24.19 (no override) → **$23.52 (with override), −2.77%**; weighted IRR 8.44% → **8.29% (−0.15pp)**. **Unblocks tier: YES** — without it the filing gap blocks scoring entirely. The engine's override check records the value as in band (out_of_band: false, last_filed_value $5,800,000 in dcf_numbers.json override_checks).

## Moat: 6/10 — moderate, niche-strong
Justification: leading, vertically integrated positions in thermal imaging (FLIR) and other sensor niches, proprietary IP and defense-program qualification incumbency, diversified end markets and proven Digital Imaging pricing — but much of the portfolio is competitive industrial product, rivals contest the same defense programs, growth is partly acquired, and returns on capital are solid rather than exceptional.
- FOR: Leading niche positions in sensors and imaging — FLIR is the thermal-imaging leader, vertically integrated from detectors/ROICs to full camera systems; proprietary sensor IP and decades of qualification incumbency on defense and space programs — hard to displace once designed in; diversified end markets (defense, industrial, environmental, marine, medical) smooth single-program cycles; proven pricing power in Digital Imaging — Q2 2026 segment margin expanded on pricing and mix (search); disciplined capital allocation: consistent OE, buybacks, and debt paydown (net debt down to ~$1.69B by Q2 2026 per the Q2 release summaries).
- AGAINST: much of the portfolio sells competitive industrial/instrumentation products with limited pricing power; capable defense-electronics rivals (L3Harris, Leonardo DRS and the primes' in-house units) contest the same programs; US government / defense-budget exposure; growth is partly bought, not organic — serial M&A carries goodwill and integration risk (FLIR is the big one; the FY2025 10-K cash-flow statement also shows a $52.5M impairment of acquired intangible assets in FY2024); short-cycle commercial markets are cyclical, and tariffs / supply chain feature in 2025–26 guidance commentary.
- A 6 gives CAP = 9.8 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 9.8 years, 15-year projection.

## DCF — v5 final run (2026-10-14)
Growth recalibration (written reason): the engine's blended growth is 11.28% (g_base 11.49%), but two components are artifacts — the 5-yr revenue CAGR of 14.71% straddles the FLIR acquisition step-up (revenue $3,086,200,000 in the year ended 2021-01-03 → $4,614,300,000 the next year, financials_history.csv), and the OE/share CAGR 2y of 23.93% is measured off the working-capital-depressed year ended 2023-01-01 (see OE_VOLATILE below). The prints that mean something — latest FY revenue YoY +7.86%, Q2 2026 revenue +9.8%, FY2026 revenue guided to just under $6.53B (~7% growth, search) — center revenue growth at ~7–10%, with OE/share able to run a little hotter on Digital Imaging margin expansion and buybacks. Scenario starts were therefore set via offsets (−0.11 / −0.07 / −0.03 / +0.01 / +0.06 vs g_base) to 0.5 / 4.5 / **8.5** / 12.5 / 17.5%. The super-bull start of 17.5% is an OE/share rate, not a revenue rate — it assumes the Q2 2026 pattern (non-GAAP EPS +20.8% YoY, search) persists via defense mix, pricing and buybacks; even it does not clear the hurdle (IRR 12.50%). Probabilities are the defaults 10/25/30/25/10; OE multipliers are the defaults 0.75/0.90/1.00/1.10/1.25. Price $607.91.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | 0.5% | 0.75 | Defense budgets stall, short-cycle commercial rolls over, tariff drag | $132.32 | 5.15% |
| Bear | 25% | 4.5% | 0.90 | Low-single-digit organic growth, no margin help | $189.73 | 6.48% |
| Base | 30% | 8.5% | 1.00 | Guided ~7% revenue growth plus modest margin/buyback lift | $251.87 | 7.94% |
| Bull | 25% | 12.5% | 1.10 | Defense imaging supercycle persists, backlog converts at high margin | $330.88 | 9.70% |
| Super bull | 10% | 17.5% | 1.25 | Q2 2026 EPS momentum becomes the run-rate | $468.98 | 12.50% |

- **Probability-weighted: IV@15% $265.84 (−56.3% vs price), IV@12% $358.06, IV@10% $461.55, weighted IRR 8.29%, base-case IRR 7.94%**
- **Tier by numbers: D.** Diagnostics (key_numbers.md): OE yield 3.87%, terminal value 20.2% of IV@15%, scenario spread 3.54x, net debt 1.90x normalized OE, 9.5 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (latest fiscal year ended 10 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, with all four legs' inputs quoted above.
- **OE_VOLATILE** (OE/share range over the last 5 years spans >3x): the low end is one working-capital year, not structural cyclicality — in the year ended 2023-01-01, OCF was $486,800,000 against net income of $788,600,000 with a $500,200,000 increase in net working capital (financials_history.csv), in the FLIR integration / post-acquisition period; OCF then printed $1,191,900,000 (FY2024) and $1,191,300,000 (FY2025). Handled by the normalized median and the TTM base, and by keeping 35% of probability on bear-or-worse.
- **OVERRIDE_APPLIED:sbc**: see OVERRIDE — gap, filing source, and measured impact are all recorded in fields (judgment.json, dcf_numbers.json overrides_applied/override_impact, overrides_registry.json), not just here.

## My thoughts / overlay
- This is a quality-vs-price verdict, and it is not assumption-fragile: the super-bull path — 17.5% OE/share growth start, 1.25x OE level — still returns only 12.50%, below the 15% hurdle. No defensible input set tried here (TTM base $23.52 or the lower normalized $21.82) gets TDY to Tier C or better at $607.91; the method range is D on both bases, with the TTM base the more generous one.
- The business itself is doing what a compounder should: record orders, sales and operating profit in Q2 2026, backlog ~$5.0B, leverage falling. None of that is in dispute — the price simply capitalizes it already, at an OE yield of 3.87%.
- Balance-sheet watch items, in words: acquisition goodwill and intangibles from the FLIR-era deals are the main asset-quality question (one $52.5M acquired-intangible impairment already printed in FY2024), and net debt of $2.123B at FY end is real even if Q2 2026 brought it down. Neither changes the tier — the gap to the hurdle is a price gap, not a solvency gap.
- **Hurdle math:** the stock clears 15% at the weighted IV@15% of **$265.84**; with a margin of safety against the scenario spread, nearer the bear-case IV@15% of **$189.73**. At $607.91 a buyer is paying more than even the super-bull IV@15% of $468.98.

## Final verdict
- **Final tier: D** (weighted IRR 8.29% on the v5 final inputs; D on every base tried)
- Confidence: **Medium** (high on OE quality and the filing-derived TTM base; the SBC override unblocks the tier but is measured and small, −0.15pp of IRR)
- One-liner: High-quality diversified sensor/imaging compounder, moat 6/10 — but at $607.91 (~25.8x TTM owner's earnings of $23.52/share) it does not clear 15%: weighted IRR 8.29%, weighted IV@15% $265.84; it clears the 15% hurdle only at ~$266, and nearer ~$190 (the bear-case IV@15%) with a margin of safety.
