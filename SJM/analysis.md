# SJM — The J. M. Smucker Company

Engine 5.4.0 run, 2026-10-17. In scope (market cap $13.622B at $127.43, nasdaq_quote_api). The preliminary run exited 4 with `DATA_GAP:shares`; the gap was cured under the bounded override authority with a filing-sourced shares override (see OVERRIDE) and the final run scored.

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.json, or financials_history.csv — none are recomputed.

## What it is

U.S. packaged-food staples, fiscal year ending April 30: U.S. Retail Coffee (Folgers, Dunkin', Café Bustelo), U.S. Retail Frozen Handheld and Spreads (Uncrustables, Jif, Smucker's fruit spreads), U.S. Retail Pet Foods (Meow Mix, Milk-Bone), Sweet Baked Snacks (Hostess, acquired November 2023 for ~$5.6B), and Away From Home. FY2026 net sales $9,050.9M (+3.72% latest rev YoY per key_numbers.md). Q1 FY27 (ended 2026-07-31) printed net sales $2,219.3M (+5%) and adjusted EPS $3.24, and management raised FY27 guidance to adjusted EPS $10.50–$11.00, net sales −1% to −2%, free cash flow ~$1.1B — but the Q1 print includes $115M of tariff refunds (~$0.84/share of the adjusted EPS beat), a one-off that flatters every TTM figure below.

## Owner's earnings

**FY2026 (10-K via EDGAR, from financials_history.csv):** operating cash flow $1,473,600,000; capex $317,400,000; SBC $23,600,000 (always a real cost).

- **Conservative owner's earnings FY2026: $1,132,600,000 = $10.59/share** (key_numbers.md: latest FY OE/share $10.59; latest FY OE total $1.133B)
- Maintenance version (NI + D&A − capex − ΔNWC, from financials_history.csv): −$61,300,000 for FY2026, −$2,511,700,000 for FY2025, +$2,816,400,000 for FY2024 — unusable. It runs through net income, which carries the non-cash Hostess impairments (FY2026: goodwill $507.5M + other intangibles $454.2M; FY2025: goodwill $1,661.6M + other intangibles $320.9M), and through working-capital swings of ±$1–2B. The OCF-based conservative definition is the only clean one here, and it is what the engine uses.
- OE positive 5 of the last 5 fiscal years. Net debt (latest) $6.905B (key_numbers.md); lease liabilities $155,700,000 (dcf_numbers.json). Dividends: 25 consecutive annual increases; FY2026 debt repayment was $720.0M and Q1 FY27 reached the company's ~3.0x net-debt/adjusted-EBITDA leverage target early, with ~$500M more repayment planned for FY27.

**Base used = the engine's normalized base, median of the last 3 fiscal years' OE/share: $7.36/share** (key_numbers.md: base OE/share $7.36, source: median_of_last_3_fy_oe_per_share; the three years are FY2024 $5.79, FY2025 $7.36, FY2026 $10.59 on the override denominator). The median is conservative here — see BASE_DIVERGENCE under Flags — and the verdict is sized to it.

**TTM check (ttm.py, through Q1 FY27, not pinned):** OCF: FY $1,473,600,000 − prior YTD −$10,600,000 + current YTD $425,700,000 = TTM $1,909,900,000; capex: FY $317,400,000 − prior YTD $84,300,000 + current YTD $88,400,000 = TTM $321,500,000; SBC: FY $23,600,000 − prior YTD $9,000,000 + current YTD $12,200,000 = TTM $26,800,000; TTM OE total $1,561,600,000 → $14.61/share on ttm.json's 106,900,000 shares. Not pinned, for two reasons: (1) the TTM OCF leg swaps out a −$10.6M prior-year Q1 for a $425.7M current Q1 that contains the $115M tariff refund — a one-off, not run-rate; TTM OCF of $1,909.9M sits above every full-year OCF in the filed history and above the FY27 guidance-implied level. (2) ttm.py's shares legs matched stale FY2022/FY2023 periods (its FY leg is the 2022-04-30 diluted count) because the current diluted series is exactly the DATA_GAP field — the 106,900,000 it lands on coincides with the FY2026 filing count, but its provenance is not current-period. The TTM figure is used only as the top of the method range below.

## OVERRIDE — shares (filing)

- **The gap:** the preliminary run exited 4, `DATA_GAP:shares` — diluted shares missing for fiscal years 2024, 2025, 2026 of the last 3; companyfacts files only a non-diluted count for those years (2024: 106,194,281; 2025: 106,425,081; 2026: 106,661,858, all CommonStockSharesOutstanding). No tier was emitted, correctly.
- **The decision (bounded authority, kind "filing"):** judgment.json carries `shares_override = {value: 106900000, kind: "filing", source: "Form 10-K for fiscal year ended April 30, 2026 (filed 2026-06-09), EPS note and the FY26 results non-GAAP reconciliation (Ex. 99.1, 2026-06-09): 'Weighted-average shares outstanding – assuming dilution' 106.9M for FY2026 (FY2025: 106.6M), computed under the treasury stock method…"}`. In band: the engine's override check records last filed diluted value 108,400,000 and out_of_band: false. The GAAP diluted count in the FY2025/FY2026 loss years equals basic because stock awards were anti-dilutive (the release's note C); the treasury-method count is the economically correct denominator and the higher, more conservative one. Quarterly diluted counts since (106.9M Q4 FY26, 107.1M Q1 FY27) confirm the level.
- **How it was applied:** the engine filled 2023-04-30, 2024-04-30, 2025-04-30 and 2026-04-30 (overrides_applied periods_filled). One side effect to note: with a single count in every filled year, key_numbers.md reports share count CAGR 0.00% — the true trend is a slow creep up (filed outstanding counts rise ~0.2–0.3%/yr), so the blend gets no dilution drag; immaterial at this growth rate.
- **Measured impact (key_numbers.md, on the median base actually used):** base OE/share $7.39 (no override) → $7.36 (with override), −0.44% · weighted IRR 8.92% → 9.11% (+0.19pp). Unblocks tier: YES — this override is the only reason this company has a tier.

## Moat: 5/10 — moderate/narrow

Justification: Moderate/narrow brand moat: leading shelf positions (Folgers/Dunkin'/Café Bustelo coffee, Jif, Uncrustables, Meow Mix/Milk-Bone) with proven price realization (coffee net price +21pp in Q4 FY26), but the measured economics are mid-single-digit — ROIC proxy ran only ~5-8% in clean years (FY17-22, FY24) and was negative/near-zero in the impairment years, GAAP gross margin swung 32.8%-38.8% over the last five fiscal years on coffee commodity costs and derivative marks, categories are mature with falling volumes (Q4 FY26 volume/mix -4pp), and the Hostess/Sweet Baked Snacks acquisition has absorbed ~$2.9B of impairments since FY25 — brands that earn ~6% on a goodwill-heavy capital base do not clear the 7+ moat bar.

Evidence (fundamentals.json, filing-direct): roic_proxy — FY2022 6.2%, FY2023 1.1%, FY2024 6.1%, FY2025 −3.9%, FY2026 2.3%; the clean pre-Hostess years FY2017–FY2021 ran 5.8% / 6.6% / 4.9% / 6.9% / 8.3%. Gross margin — FY2022 33.8%, FY2023 32.8%, FY2024 38.1%, FY2025 38.8%, FY2026 33.5% (adjusted FY2026 34.9% vs adjusted FY2025 38.2%): the level is a commodity/derivative-mark outcome as much as a brand outcome. A 7+ moat needs ROIC well above the cost of capital through a cycle; ~6% clean-year ROIC on a capital base stacked with acquisition goodwill is a 5.

- FOR: Leading branded shelf positions: Folgers/Dunkin'/Café Bustelo in U.S. retail coffee, Jif peanut butter, Uncrustables (>$1B sales platform, still growing high-single-digits), Meow Mix/Milk-Bone in pet; proven pricing power — coffee net price realization +21pp in Q4 FY26 and +13% coffee sales in Q1 FY27, taken to recover commodity costs without share collapse (~two-thirds of portfolio holding/gaining share); recurring, staple demand through cycles: OE positive 5/5 last years, OCF $1.2-1.5B/yr, 25 years of consecutive dividend increases.
- AGAINST: ROIC proxy only ~5-8% in clean years and negative in FY25 (impairments) — returns sit near/below cost of capital on an acquisition-heavy capital base; Hostess deal destroyer: ~$2.9B of goodwill/trademark impairments FY25–Q3 FY26 on the $5.6B Sweet Baked Snacks acquisition, segment sales and volumes still falling (Q1 FY27 −7%); commodity hostage: coffee input costs drove GAAP gross margin to 33.5% in FY26 (adjusted 34.9% vs 38.2% FY25), pricing is cost-recovery not expansion, and volumes fall when price rises (Q4 FY26 volume/mix −4pp); mature/declining center-store categories, private-label and retailer power, health/GLP-1 headwinds, net debt $6,905.1M (8.78x normalized OE, 6.1x latest-FY OE).
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — final run (engine 5.4.0, 2026-10-17)

Growth: the blend is 3.11% (key_numbers.md) — components: rev CAGR 5y 2.49% · rev CAGR 3y 2.00% · latest rev YoY 3.72% · OE/share CAGR 2y 35.30%. The 35.30% OE/share CAGR is a rebound artifact (FY2024's capex-peak base to FY2026) and the median-of-components construction correctly keeps it from driving the blend. Default offsets (−12/−5/0/+5/+12pp) and OE multipliers (0.75/0.90/1.00/1.10/1.25) and default probabilities (10/25/30/25/10) were kept: nothing in the evidence justifies skewing a mature staples name.

**Growth-start sanity check (mandatory):** base start 3.1% vs recent prints — FY2026 reported sales +3.72%, comparable sales +5%, Q1 FY27 sales +5%, but FY27 sales are guided −1% to −2% (price give-back as coffee costs fall). The bull (8.1%) and super-bull (15.1%) starts sit above the guided FY27 sales path — written reason: these are owner's-earnings growth starts, not sales. FY27 adjusted EPS is guided $10.50–$11.00 vs FY2026 adjusted EPS $9.15 (margin recovery as lower coffee costs flow through, lower interest on repaid debt, ~$0.60/share of tariff-refund benefit), so near-term OE/share growth above the sales line is the company's own guidance shape; the fade then pulls every path to 2.5% over the 8.5-year CAP. The bear (−1.9%) and super-bear (−8.9%) starts bracket the guided sales decline with volume/mix deterioration on top.

| Scenario | Prob | Growth start | OE mult | IV@15 | IV@12 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -8.9% | 0.75 | $28.08 | $35.73 | 4.89% |
| Bear | 25% | -1.9% | 0.9 | $45.21 | $58.76 | 6.76% |
| Base | 30% | 3.1% | 1.0 | $61.89 | $81.57 | 8.59% |
| Bull | 25% | 8.1% | 1.1 | $83.76 | $111.83 | 10.89% |
| Super bull | 10% | 15.1% | 1.25 | $126.83 | $172.14 | 14.95% |

- **Probability-weighted: IV@15% $66.30, IV@12% $87.90, IV@10% $111.98, weighted IRR 9.11%, base-case IRR 8.59%** (key_numbers.md)
- **Tier by numbers: D.** IRR band: bear 6.76% (tier D) → bull 10.89% (tier C); scenario range 4.89% – 14.95%. Hurdle-clearing prices (weighted path): 15% at $66.30 · 20% at $46.86 · 25% at $36.14.
- Diagnostics (key_numbers.md): OE yield 5.78%, TV share @15% 18.5%, scenario spread (IV@15 super-bull / super-bear) 4.52x, net debt / normalized OE 8.78x, months since FY end 5.6.

## Flags — every fragility flag resolved

- **NI_OCF_DIVERGENCE** (2025, 2026): the one-off is the Hostess/Sweet Baked Snacks non-cash impairments — FY2025 net income −$1,230,800,000 vs OCF $1,210,400,000 (goodwill impairment $1,661.6M + other intangible impairment $320.9M, plus a $310.1M divestiture loss in the GAAP lines), FY2026 net income −$138,700,000 vs OCF $1,473,600,000 (goodwill $507.5M in Q3 FY26, wiping out the unit's remaining goodwill, + other intangibles $454.2M). Impairments do not touch OCF, so the OCF-based OE base is not contaminated; what they contaminate is book value and the maintenance-OE definition (see Owner's earnings).
- **SHARES_FALLBACK** (2023): noted — FY2023 per-share history uses the filed outstanding count and is approximate; the final run's override also fills 2023-04-30 with 106,900,000, and FY2023 is outside the last-3-FY base window, so the scored base is unaffected.
- **CASH_INCLUDES_RESTRICTED**: checked against fundamentals.json — the latest-FY combined cash + restricted-cash total is only $58,600,000 against total debt $6,963,700,000 and net debt $6,905,100,000. Whatever the restricted slice is, it cannot change the leverage conclusion; net debt is effectively gross debt here.
- **OVERRIDE_APPLIED:shares**: see OVERRIDE — gap, decision, source, and measured impact (−0.44% on the base, +0.19pp on weighted IRR, unblocks the tier) are all recorded in judgment.json / dcf_numbers.json / score.json, not just here.
- **BASE_DIVERGENCE** (latest FY OE/share 10.59 vs 3-yr median 7.36): both are distorted, in opposite directions. The median is dragged down by FY2024 ($5.79/share), whose capex peaked at $586,500,000 during the Uncrustables capacity build and Hostess integration, and by FY2025's soft OCF year. The latest FY is the cleaner run-rate signal (capex normalized to $317,400,000; FY27 capex guided at $325M and FCF at ~$1.1B), but it is a single year. Per the method the scored base stays the median and the verdict is sized to it; the divergence is carried into the method range below instead of being overridden away.
- **WIDE_SCENARIO_SPREAD** (4.52x): real — it is mostly base uncertainty (capex cycle + impairment-era OCF path), not growth fantasy. Confidence is medium, never high, and the verdict is sized to the conservative end.
- **HIGH_NET_DEBT** (net debt 8.78x normalized OE): real on the scored base. Mitigants, stated not netted: net debt is 6.1x the latest-FY OE total ($1.133B), the company repaid $720.0M in FY2026, hit its ~3.0x net-debt/adjusted-EBITDA target early in Q1 FY27, and plans ~$500M more repayment in FY27 before buybacks. The bear cases (IV@15 $45.21 / $28.08) are the stress answer.
- **TIER_BAND** (bear tier D 6.8% vs bull tier C 10.9%): the verdict is sized to the bear end — Tier D.

## My thoughts / method range

- The honest headline is the range across defensible bases: median base $7.36/share → weighted IRR 9.11%, IV@15% $66.30, Tier D (scored). Latest-FY base would sit between the two. TTM pin ($14.61/share, run with the same moat/probabilities) → weighted IRR 15.40%, IV@15% $131.61, Tier B — but that TTM is flattered by the $115M tariff refund and a working-capital swing, so B is the ceiling of the range, not a candidate verdict. Even the ceiling barely clears the $127.43 price at a 15% discount rate.
- Quality is middling, not broken: OCF has printed $1.14–1.57B every year for a decade, SBC is trivial ($23.6M FY2026), the dividend is covered by FCF ($1,156.2M FY2026), and deleveraging is actually happening. The problem is price vs normalized cash generation, plus a capital-allocation record that just wrote off ~$2.9B of a $5.6B acquisition inside three years.
- Watch items: Sweet Baked Snacks volumes (still falling), coffee price/volume elasticity as list prices are given back in FY27, whether FY27 FCF ~$1.1B lands, and Elliott Management's engagement (two independent directors added) as a governance catalyst.

## Final verdict

- **Final tier: D** (weighted IRR 9.11% on the scored median base; band bear D → bull C; method range D to B across bases, sized to the conservative end)
- Confidence: **Medium** (WIDE_SCENARIO_SPREAD present; base divergence documented, not resolved away)
- One-liner: Staple-brand cash generator with a busted Hostess acquisition, moat 5/10 — on the scored median base OE $7.36/share the weighted IRR is 9.11% (IV@15% $66.30 vs $127.43), and even the tariff-flattered TTM base only reaches 15.40% / $131.61; it clears the 15% hurdle only below ~$66 on the scored base.
