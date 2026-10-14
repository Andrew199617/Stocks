# PAYX — Paychex, Inc.
v5 re-run, 2026-10-14 (supersedes the 2026-10-13 run; verdict unchanged — see method range under Thoughts). In scope (market cap $38.25B at $106.25, nasdaq_quote_api — under the $40B cutoff).

All figures below are copied from key_numbers.md, dcf_numbers.json, or ttm.py output — none are recomputed.

## What it is
Payroll, HR, benefits, PEO and insurance outsourcing for small and mid-sized businesses: Paychex Flex for SMBs, Paycor (acquired April 2025 for ~$4.1B) for the mid/upmarket, SurePayroll at the micro end, plus a PEO co-employment offering. Revenue is overwhelmingly recurring; the company also earns interest on client funds held between collection and payroll/tax remittance. Management Solutions is roughly three-quarters of revenue; PEO & Insurance Solutions is the faster-growing remainder (Q1 FY2027: Management Solutions +4%, PEO & Insurance +12%, total revenue +6% to $1,630.5M per Q1 FY2027 earnings coverage).

## Owner's earnings
**FY2026 (10-K via EDGAR, from financials_history.csv):** operating cash flow $2,556,700,000; capex $234,900,000; SBC $96,100,000 (always a real cost).
- **Conservative owner's earnings FY2026: $2,225,700,000 = $6.1825/share** (latest FY OE/share, key_numbers.md).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $2,014,700,000 — same ballpark as the conservative figure, which raises confidence.
- OE positive 5 of the last 5 fiscal years. Net debt $3,467,900,000 (key_numbers.md) — acquisition debt from the Paycor deal; diagnostics put net debt at 1.78x normalized OE.
- History caveat — the Paycor basis break: FY2026 is the first full year of Paycor consolidation. Reported FY2026 revenue growth of ~17% includes roughly 12 points contributed by Paycor (per FY2026 earnings coverage); the EDGAR contract-revenue series shows latest YoY +16.47%. D&A stepped from $209,500,000 (FY2025) to $442,600,000 (FY2026) on acquisition amortization, and debt stepped up in FY2025 to fund the deal. Pre- and post-deal years are not a clean organic series.

**Base used = TTM owner's earnings through Q1 FY2027 (period ended 2026-08-31), from ttm.py (filing-direct, no hand math):**
- OCF: FY $2,556,700,000 − prior YTD $718,400,000 + current YTD $413,500,000 = **TTM $2,251,800,000**
- Capex: FY $234,900,000 − prior YTD $55,900,000 + current YTD $56,100,000 = **TTM $235,100,000**
- SBC: FY $96,100,000 − prior YTD $26,800,000 + current YTD $19,300,000 = **TTM $88,600,000**
- Shares (current-YTD weighted diluted): **356,600,000**
- **TTM OE total $1,928,100,000 → base OE/share $5.4069** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $4.6263/share — rejected as the base: two of its three years (FY2024, and FY2025 with only a stub of Paycor) predate the combined company's scale, so the median understates the current run-rate. The latest-FY figure ($6.1825) is the first clean combined year, but the TTM base is the more current choice — it prices the combined perimeter on its most recent four quarters. The TTM runs below FY2026 because Q1 FY2027 OCF ($413,500,000) ran well below Q1 FY2026 ($718,400,000); Paychex OCF is seasonal and Q1 timing swings are large, which is noted as a base caveat and is one reason confidence is medium, not high. The prior run used the FY2026 base and landed at a 10.0% weighted IRR — same tier (see Thoughts).

## Moat: 7/10 — strong
Justification: Payroll is mission-critical and compliance-laden, which makes switching painful and retention durable; the PEO co-employment model deepens lock-in further. Scale, a direct sales force, and a bundled HR/benefits/retirement stack give real pricing power — adjusted operating margin guided at ~44% and held through cycles. It is not a 9-10: ADP is larger with greater enterprise reach, and cloud-native rivals (Paycom, Paylocity, Rippling, Gusto) innovate faster at the product layer and attack from both ends of the market; per-employee pricing is also structurally exposed to SMB employment levels and, over time, to AI automation of the underlying HR workflows. (The prior run scored this 6/10 on the same facts; the 6-7 range does not change the tier — both runs land at Tier D.)
- FOR: High switching costs — payroll/tax compliance is mission-critical and embedded in client workflows; recurring revenue with durable retention through cycles; PEO co-employment model raises lock-in and lifetime value (ASO-to-PEO conversions ran at ~2x plan in Q1 FY2027); scale + direct distribution + bundled HCM/benefits/retirement/insurance stack; proven pricing power with ~44% adjusted operating margins; client-funds float is a structural earnings kicker while rates stay higher.
- AGAINST: ADP has greater scale and enterprise reach; cloud-native competitors innovate faster at the UI layer and pressure both SMB and mid-market segments; growth is capped by SMB employment growth — a soft labor market hits client counts and per-client revenue directly; interest on client funds is rate-sensitive — Fed cuts shrink that earnings stream; Paycor integration/synergy execution ($80M+ targeted cost synergies) is not yet fully proven on an organic basis; acquisition debt (net debt $3,467,900,000) replaced a previously near-unlevered balance sheet.
- A 7 gives CAP = 11.1 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 11.1 years, 15-year projection.

## DCF — v5 final run (2026-10-14)
Growth recalibration (written reason): the engine's blended growth is 12.57% and g_base 12.78%, but both are acquisition artifacts — the blend's loudest components are the latest revenue YoY (+16.47%) and OE/share CAGR 2y (+15.61%), which straddle the Paycor consolidation. Underlying organic growth is mid-single-digit: FY2027 guidance is total revenue growth of 5%-6% with adjusted EPS growth of 7%-9%, and Q1 FY2027 printed total revenue +6%. Scenario starts were therefore set via offsets (−0.128 / −0.098 / −0.068 / −0.038 / −0.008 vs g_base) to ~0 / 3 / **6** / 9 / 12%. The base start (6%) matches guidance and the Q1 print. The super-bull start (12%) sits below the FY2026 reported print (+16.47% YoY) for a stated reason: that print was consolidation-driven, not organic, and a 12% organic OE start already assumes synergies land, the PEO mix shift accelerates, and Paycor cross-sell compounds — the fastest defensible organic path. Probabilities 10/25/30/25/10; OE multipliers 0.75/0.90/1.00/1.10/1.25. Price $106.25.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -0.0% | 0.75 | SMB employment downturn; float income falls with rate cuts; integration stalls | $29.54 | 5.85% |
| Bear | 25% | 3.0% | 0.90 | Organic growth halves vs guide; Management Solutions softness (Q1 +4%) persists | $40.82 | 7.33% |
| Base | 30% | 6.0% | 1.00 | Guidance delivered: 5-6% revenue growth, synergies on track | $52.27 | 8.83% |
| Bull | 25% | 9.0% | 1.10 | PEO acceleration + Paycor cross-sell lift organic growth above guide | $66.29 | 10.59% |
| Super bull | 10% | 12.0% | 1.25 | Durable low-double-digit organic compounding; synergies exceed target | $86.87 | 12.95% |

- **Probability-weighted: IV@15% $54.10 (−49.08% vs price), IV@12% $72.36, IV@10% $92.81, weighted IRR 9.09%, base-case IRR 8.83%**
- **Tier by numbers: D.** Diagnostics (key_numbers.md): OE yield 5.09%, terminal value 19.49% of IV@15%, scenario spread 2.94x, net debt 1.78x normalized OE, 4.47 months since FY end.

## Flags — every fragility flag resolved
- **WIDE_SCENARIO_SPREAD** (preliminary run: super-bull IV 4.44x super-bear IV): the spread was an artifact of the acquisition-inflated growth blend — scenario starts ran from 0.78% to 24.78% off a 12.78% g_base that does not describe the organic business. After the written recalibration to guided organic growth (starts ~0% to 12%), the final run's spread is 2.94x and the flag no longer fires. Confidence is still held at medium, not high, given the TTM base caveat in the OE section.
- **Base divergence (agent-identified; the engine flag did not fire):** latest FY OE/share $6.1825 vs 3-yr median $4.6263 — a 34% gap created by the Paycor perimeter change, not cyclicality. Resolved by using the TTM base ($5.4069) from ttm.py, quoted in full above.
- **Acquisition basis break (agent-identified):** FY2026 growth prints straddle the Paycor close (April 2025). Growth inputs were chosen on post-deal evidence only — FY2027 guidance (5-6% revenue, 7-9% adjusted EPS) and the Q1 FY2027 print (+6%) — not on the mixed-base CAGRs, which are reported above for transparency and were overridden with the reason written.
- **Net debt / balance sheet:** net debt $3,467,900,000 (1.78x normalized OE) is Paycor acquisition debt. It does not change the tier math — the DCF is on OE/share at current price — but it removes the fortress-balance-sheet credit the pre-deal Paychex carried, and it is folded into the verdict: leverage plus a high payout leaves less room for error if the bear case lands.
- No STALE_FY (4.47 months since FY end, and the base is TTM through Q1 FY2027 in any case), no DATA_GAP (SBC, capex, diluted shares and OCF all filed for the last 3 FY; USD filer; 10-K form), no SECTOR_MODEL_MISMATCH (business services — the OE/capex logic fits), no DILUTION (share count essentially flat; share CAGR −0.21%/yr).

## My thoughts / overlay
- The verdict is not close, and it is robust to method: this v5 run (TTM base $5.4069, moat 7) gives a 9.09% weighted IRR; the prior run (FY2026 base $6.1825, moat 6) gave 10.0%; the preliminary v5 run with the unadjusted acquisition-inflated blend gave 10.18%. Every defensible method lands in Tier D/C-boundary, far below the 15% hurdle. Even this run's super-bull case (12% growth start, 1.25x OE) yields IV@15% $86.87, below the $106.25 price. At this price the stock is priced for its multiple, not its cash flows.
- Quality is not the debate: OE positive 5/5 years, conservative and maintenance OE in the same ballpark, SBC modest ($88,600,000 TTM against $2,251,800,000 TTM OCF), capex light and stable. A genuinely strong franchise (moat 7/10) selling at a price that pre-pays a decade of its guided growth.
- Watch items: Q1 FY2027 Management Solutions grew only 4% vs a 5-6% full-year guide — management attributes it to ASO-to-PEO mix shift, and PEO guidance was raised to 7-8%, but the core segment must reaccelerate to hit guide; Q2 faces a tough comparison (prior-year one-offs). Client-funds interest is a rate-cut headwind. The September 2026 post-earnings selloff (~9% on report day) repriced some of this, not enough.
- Margin of safety: the price that clears Andrew's 15% hurdle on the weighted case is the weighted IV@15% itself — **$54.10**. At $106.25 there is no margin of safety in any scenario, including super bull.

## Final verdict
- **Final tier: D** (weighted IRR 9.09% on the v5 final inputs; no tier override — the method range across runs is 9.1%-10.2%, all far below the hurdle)
- Confidence: **Medium** (high on OE quality and filing completeness; medium on the TTM base given Q1 OCF seasonality, and on how much of Paycor's contribution is durable organic growth vs consolidation)
- One-liner: Strong payroll/HCM franchise, moat 7/10 — but at $106.25 it clears only a 9.1% weighted IRR (IV@15 $54.10) on guided 5-6% organic growth; Tier D, needs ~$54 to clear 15%.
