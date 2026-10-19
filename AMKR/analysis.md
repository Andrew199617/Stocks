# AMKR — Amkor Technology, Inc.
Engine 5.4.0 run, 2026-10-18. Price $41.82 (nasdaq_quote_api), market cap $10.39B — in scope under $40B.

All figures below are copied from dcf_numbers.json, financials_history.csv, or fundamentals.json — none are recomputed.

## What it is
The world's #2 outsourced semiconductor assembly and test (OSAT) provider: advanced packaging (HDFO, 2.5D, co-packaged optics — ~81% of revenue from advanced products) and test for fabless customers, with plants across Asia plus a large new advanced-packaging campus in Peoria, Arizona built under a 10-year TSMC agreement (total planned Arizona investment raised to ~$12B including Phase 2; lead customers include NVIDIA and Apple). Deeply cyclical and extremely capital-intensive.

## Owner's earnings
**FY2025 (10-K via EDGAR, financials_history.csv):** operating cash flow $1,095,606,000; capex $904,614,000; SBC $20,099,000 (always a real cost, though tiny here).
- **Conservative OE FY2025: $170,893,000 = $0.69/share** (latest FY OE/share $0.69 in dcf_numbers.json)
- Maintenance version FY2025: $137,696,000 (~$0.55/share) — same low ballpark; the gap between the two definitions is not the issue, capex is.
- OE positive 5 of the last 5 fiscal years, but the 5-yr OE/share path is $0.86 / $1.35 / $0.72 / $2.07 / $1.32 / $0.69 (2020–2025) — a capex-cycle series, not a growth series.
- Net debt is small: $66,899,000 (0.20× normalized OE), plus lease liabilities $71,689,000 (dcf_numbers.json). The balance sheet is not the problem; the reinvestment rate is.
- **Base used = normalized median of the last 3 FY OE/share: $1.3183/share** (base_source: median_of_last_3_fy_oe_per_share). Rationale under BASE_DIVERGENCE below.
- **TTM check:** ttm.py could not compute a TTM OE — Amkor does not tag SBC in its 10-Qs ("sbc: no post-FY YTD fact"). fundamentals.json's TTM through 2026-03-31 shows why a TTM base would not rescue the verdict anyway: revenue $7,071,107,000 (+12.7% YoY), OCF $1,216,544,000, but capex already $1,049,322,000 and FCF only $167,222,000 ($0.67/share) — and that is before the guided 2026 capex step-up (below).

**The 2026 capex supercycle (research, cited in Flags):** Q1 2026 revenue $1.68B (+27.5% YoY) and Q2 2026 a record $1.90B (+25.6% YoY, GAAP EPS $0.70, operating margin 10.5%, gross margin 16.8%); Q3 2026 guided to $1.95–2.05B revenue at 18.5–19.5% gross margin. But full-year 2026 capex is guided at **$2.5–3.0B** (65–70% Arizona facility expansion) against ~$1.1B of FY2025 operating cash flow; H1 2026 free cash flow was negative. On the conservative OE definition (all capex subtracted), 2026 owner's earnings will be deeply negative. The DCF base is a *normalized through-cycle* OE, which is the only defensible way to run this name through the engine — but it means the model gives Amkor full credit for normalized conversion while the market price asks it to also deliver a growth re-rating.

## Moat: 4/10 — weak
Justification: scale and technology are real; the returns on capital are not.
- FOR: #2 global OSAT scale (~$6.7B FY2025 revenue); advanced-packaging technology portfolio (HDFO, 2.5D, co-packaged optics) that AI/HPC demand is pulling hard (OSAT revenue +22% YoY industry-wide in Q2 2026); scarce US footprint — Arizona campus under a 10-year TSMC agreement and a multi-year NVIDIA partnership, CHIPS-aligned; qualification and switching friction with leading fabless customers.
- AGAINST (evidence first, from fundamentals.json): **ROIC (roic_proxy) was 21.2% (2021) and 20.4% (2022), then fell to 9.5% (2023), 8.7% (2024), 8.7% (2025)** — at or below the cost of capital for the last three years. **Gross margin compressed 18.2% / 18.2% / 16.5% / 16.0% / 17.8% / 20.0% / 18.8% / 14.5% / 14.8% / 14.0% (2016–2025)** — a decade of no pricing power, with the 2026 recovery (Q2 16.8%, Q3 guide 18.5–19.5%) still only back to the historical mid-range. Customer concentration is high (top 10 ≈ 72% of 2024 sales; Apple ≈ 31%, Qualcomm ≈ 10% per third-party summaries of the 10-K). ASE is the larger rival; TSMC insources the most strategic advanced packaging (CoWoS) and uses OSATs partly as overflow/second source. Capital intensity is structural, not incidental.
- A 4 gives CAP = 7.2 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 7.2 years, 15-year projection.

## DCF — engine 5.4.0 final run (2026-10-18)
Engine blended growth g_base is 1.70% (components: rev CAGR 5y 5.84%, rev CAGR 3y −1.84%, latest rev YoY +6.18%, OE/share CAGR 2y −42.37% — the OE leg is the capex cycle, not demand). Default scenario offsets (−12/−5/0/+5/+12pp) and OE multipliers (0.75/0.90/1.00/1.10/1.25) were kept. Probabilities were shifted to widen the bear side per the OE_VOLATILE flag: **15/30/30/15/10** (45% on bear-or-worse).

**Growth-start sanity check (mandatory):** the scenario OE growth starts (−10.0% / −3.3% / +1.7% / +6.7% / +13.7%) are all below the company's recent *revenue* prints (Q1 2026 +27.5% YoY, Q2 2026 +25.6% YoY, Q3 guided ~$2.0B). Written reason: these are **owner's-earnings** growth starts, not revenue growth starts. With 2026 capex guided at $2.5–3.0B — roughly 3× FY2025 capex and ~2.5× FY2025 OCF — conservative OE is negative in 2026 no matter how fast revenue grows; OE growth can only resume once capex normalizes toward the ~$0.75–0.9B/yr historical band and the new capacity converts to cash. A bull OE start at the revenue print (~+26%) would assume instant capex normalization, which the company's own guidance contradicts.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | −10.0% | 0.75 | AI packaging cycle turns before Arizona capacity pays back; capex stranded at low utilization | $4.97 | 3.79% |
| Bear | 30% | −3.3% | 0.90 | Capex stays elevated, margins stay at the 14–15% gross level, OE stuck below the normalized base | $7.77 | 4.70% |
| Base | 30% | +1.7% | 1.00 | Normalized $1.32/share OE base, capex fades back over the CAP, low-single-digit OE growth | $10.48 | 5.61% |
| Bull | 15% | +6.7% | 1.10 | HDFO/2.5D ramps fill, gross margin holds the guided 18–19%, capex normalizes on schedule | $13.96 | 6.79% |
| Super bull | 10% | +13.7% | 1.25 | Arizona becomes the strategic US packaging hub; sustained double-digit OE growth off the normalized base | $20.65 | 8.97% |

- **Probability-weighted: IV@15% $10.38 (−75.2% vs price), IV@12% $13.67, IV@10% $17.32, weighted IRR 5.61%, base-case IRR 5.61%**
- **Tier by numbers: D.** Bear tier D, bull tier D — no TIER_BAND split; even the super-bull scenario (10%) returns only 8.97% from $41.82.
- Diagnostics (dcf_numbers.json): OE yield 3.15%, terminal value 17.9% of IV@15%, scenario spread 4.15×, net debt 0.20× normalized OE, 9.6 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (FY2025 ended 9.6 months ago): ttm.py was run and **failed** — Amkor does not tag SBC in its 10-Qs, so no filing-direct TTM OE exists ("sbc: no post-FY YTD fact (no 10-Q since the 2025-12-31 fiscal year end)" per its EDGAR tag search). The normalized median base was used instead, cross-checked against fundamentals.json TTM through 2026-03-31 (OCF $1,216,544,000, capex $1,049,322,000, FCF $167,222,000): a TTM OE base would be *lower* than the median base, so the median is the generous choice and the verdict does not hinge on staleness.
- **OE_VOLATILE** (OE/share spans >3× over 5 years: $0.72 → $2.07 → $0.69): real and structural — it is the capex cycle (capex $0.55–0.91B/yr against OCF $0.56–1.27B/yr). Handled by the normalized median base plus bear-side probability widening to 15/30 (45% bear-or-worse).
- **NI_OCF_DIVERGENCE** (NI vs OCF differ by >40% in 2023, 2024, 2025): resolved — it is **D&A, not a one-off**. FY2025: net income $373,895,000 vs OCF $1,095,606,000, with D&A of $642,008,000 (financials_history.csv) explaining nearly the entire gap; the same pattern holds in 2023 (NI $359,813,000, D&A $631,508,000) and 2024 (NI $354,012,000, D&A $594,663,000). A plant-heavy OSAT runs D&A at ~10% of revenue every year. No tax-deposit or impairment one-off was found in research. The OCF-based conservative OE already subtracts full capex, so the divergence does not inflate the base — if anything the conservative definition double-counts the burden in heavy-capex years, which is acknowledged in the method range.
- **BASE_DIVERGENCE** (latest FY OE/share $0.69 vs 3-yr median $1.32): **the latest FY is the distorted one, in the downward direction** — FY2025 capex jumped to $904,614,000 (from $743,796,000 in 2024) as the Arizona build began, while OCF was flat. The median ($1.32, the FY2024 print; the 3-yr window is $2.07 / $1.32 / $0.69) is itself flattered by FY2023's unusually light capex year. Neither is "true" run-rate OE; the median is used as the normalized base because it is the engine's through-cycle convention, and the analysis flags that even this generous base fails at the current price. Note FY2023's $2.07 was the median window's high print on OCF of $1,270,020,000 — the best OCF year in the file — so the median carries upside bias, not downside.
- **WIDE_SCENARIO_SPREAD** (super-bull IV 4.2× super-bear IV): real — the outcome genuinely hinges on whether the $12B Arizona program converts to cash OE or strands. Confidence is **low**, and the verdict is sized to the conservative end. Even so, the spread does not straddle the price: the *super-bull* IV@15% ($20.65) is half the $41.82 price.

## My thoughts / overlay
- The market is pricing Amkor as an AI-infrastructure growth stock (revenue +26%, record quarters, Arizona scarcity value); this method prices it as what it has historically been: a cyclical, capital-devouring OSAT whose owner's earnings average ~$1/share across the cycle. Both can be "right" about the business; only one is right about the cash an owner actually receives per share at $41.82.
- Method range: the defensible bases span the maintenance-OE view (~$0.55/share latest FY) to the normalized median ($1.32/share). Every base in that range produces a Tier D at this price — the verdict is robust to the base choice, which is why confidence in the *tier* is higher than the low overall confidence (which reflects the genuine uncertainty about post-2027 capex normalization).
- What would change the verdict: capex actually normalizing after Phase 1 (mid-2027) with gross margins holding 18–19%+, converting the revenue growth into OE/share well above the $1.32 normalized base — i.e., ROIC sustainably back above ~15%. That is a show-me story, not a filed one.
- Risks to this short-looking verdict: CHIPS Act / customer co-funding could offset part of the capex burden (not in the filed OE history); a takeout or strategic re-rating is outside the model's scope.
- Hurdle-clearing prices (dcf_numbers.json): clears 15% at **$10.38**, 20% at $7.41, 25% at $5.76 — versus the $41.82 price.

## Final verdict
- **Final tier: D** (weighted IRR 5.61% on the normalized median base; bear D / bull D; super-bull IRR only 8.97%)
- Confidence: **Low** (wide scenario spread, capex regime change not yet in any filed OE history, TTM OE not computable from filings)
- One-liner: Weak-moat (4/10) cyclical OSAT in a capex supercycle — at $41.82 it does not clear 15% on owner's earnings (weighted IRR 5.6%, weighted IV@15% $10.38; even the super-bull case yields only 9.0%); it would need to trade near $10.38 to clear the 15% hurdle on this method.
