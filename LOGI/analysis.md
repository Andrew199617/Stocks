# LOGI — Logitech International S.A.
Engine 5.4.0 run, 2026-10-17. In scope (market cap $15.47B at $104.41, nasdaq_quote_api).

All figures below are copied from dcf_numbers.json, financials_history.csv, ttm.json, or fundamentals.json — none are recomputed.

## What it is
Swiss computer-peripherals maker: pointing devices, keyboards & combos, gaming (Logitech G), video collaboration, webcams, tablet accessories, headsets. Sold in 100+ countries, roughly 60% consumer / 40% B2B. Global #1 in gaming mice/keyboards/headsets and a leading share position (~60% cited for mice) across most categories; Q4 FY26 shareholder letter reports share gains in Pointing Devices, Keyboards & Combos, Video Collaboration, Webcams and headsets. Asset-light hardware: FY2026 revenue $4,840,761,000, gross margin 43.20%.

## Owner's earnings
**FY2026 (10-K via EDGAR, period ended 2026-03-31, from financials_history.csv):** operating cash flow $1,037,207,000; capex $61,562,000; SBC $112,392,000 (always a real cost).
- **Conservative owner's earnings FY2026: $863,253,000 = $5.8246/share.**
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $841,442,000 — same ballpark as the conservative figure, which raises confidence.
- OE positive 5 of the last 5 fiscal years, but violently cyclical across the pandemic cycle: OE/share ran $7.5473 (FY2021) → $0.6789 (FY2022) → $2.2655 (FY2023) → $6.3623 (FY2024) → $4.5588 (FY2025) → $5.8246 (FY2026).
- Balance sheet (FY2026 10-K / Q4 release): cash $1,741,546,000; total assets $3,848,588,000; total liabilities $1,637,194,000; equity $2,211,394,000. No interest-bearing debt lines at all — the company is debt-free; the only lease figure the engine finds is operating lease liabilities of $88,155,000. Buybacks are the capital-return engine: diluted share count shrinking 3.3%/yr (share CAGR −3.26%), Q1 FY27 alone returned $114M via repurchases per the company release.

**Base used = median of the last 3 FY OE/share: $5.8246/share** (base_source: median_of_last_3_fy_oe_per_share; the three years are FY24 $6.3623, FY25 $4.5588, FY26 $5.8246, so the median equals the latest FY). The median is the right base for a cyclical whose single years swing from $0.68 to $7.55.

**TTM cross-check (ttm.py, through Q1 FY27 ended 2026-06-30; not used as the base):**
- OCF: FY $1,037,207,000 − prior YTD $125,045,000 + current YTD $166,708,000 = **TTM $1,078,870,000**
- Capex: FY $61,562,000 − prior YTD $16,276,000 + current YTD $16,798,000 = **TTM $62,084,000**
- SBC: FY $112,392,000 − prior YTD $32,828,000 + current YTD $29,632,000 = **TTM $109,196,000**
- Shares (current-YTD weighted diluted): **145,038,000**
- **TTM OE total $907,590,000 → $6.2576/share**
- Not used as the base: the TTM window's newest quarter (Q1 FY27) includes a $61M tariff refund in operating results (company Q1 FY27 release: GAAP operating income $259M including the refund; non-GAAP operating income ex-refund grew 14% YoY vs 44% reported), and for this cyclical the 3-yr median smoothing is the more conservative, defensible base. The TTM print says the median base is not stale-low — it says current run-rate OE is somewhat higher, with a one-off inside it.

## Moat: 5/10 — moderate/narrow
Justification: durable #1 share positions and brand/design leadership with high measured returns on capital, but peripherals carry low switching costs, no network effects, and must be re-won every product cycle against HP/Dell/Apple/Microsoft, Razer/Corsair and low-cost rivals.
- FOR: #1 global share in most core categories (mice, keyboards & combos, gaming peripherals, video collaboration) held for years, with share gains reported again in Q4 FY26; brand + industrial design + retail/enterprise distribution in 100+ countries; gross margin recovered from 37.88% (FY2023) to 43.20% (FY2026) — some pricing power; debt-free, asset-light model (capex ~$62M on $4.84B revenue).
- AGAINST: low switching costs — a mouse or webcam is a one-purchase decision with no lock-in or network effect; platform owners (Apple, Microsoft) and PC OEMs (HP, Dell) compete in adjacent categories; tariff exposure on China-made hardware (the Q1 FY27 tariff refund shows how policy swings hit results both ways); a semiconductor supplier incident is expected to pressure Q2/Q3 FY27 revenue ($20M in Q2, up to $200M in Q3, per company commentary reported Oct 2026); pandemic pulled demand forward once and OE/share fell ~91% peak-to-trough (FY21 $7.5473 → FY22 $0.6789).
- ROIC evidence (fundamentals.json roic_proxy — after-tax operating income over equity + debt − cash): FY2022 0.6009, FY2023 0.3253, FY2024 0.8114, FY2025 0.9373, FY2026 1.4197. Even the trough year stayed far above any cost of capital — but the denominator is tiny by construction (net-cash balance sheet, buyback-shrunk equity of $2,211,394,000 against $1,741,546,000 cash), so the level overstates franchise strength; it proves capital efficiency, not pricing power. Gross margin level (low-to-mid 40s, hardware-like) and the FY23 dip to 37.88% are the honest moat read: real but narrow. That is why the score is 5, not 7+.
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — final run (engine 5.4.0, 2026-10-17)
Growth sanity check (mandatory): the engine's blended start is 3.54% (g_base) — components: rev CAGR 5y −1.62%, rev CAGR 3y +2.17%, latest FY rev YoY +6.28%, OE/share CAGR 2y −4.32%, with the −3.26%/yr share-count shrink credited as +3.26pp on the revenue components only. Recent prints: FY2026 revenue +6.28% YoY; Q1 FY27 revenue $1.23B, +7% in USD / +5% constant currency (company release, July 28, 2026) — the tenth consecutive growth quarter, with double-digit growth in Pointing Devices. The base start (3.54%) sits BELOW the latest prints, with written reasons: (1) Q1 FY27 profit includes the $61M tariff-refund one-off; (2) the supplier incident pressures the next two quarters' revenue; (3) the 5-yr revenue CAGR is still negative and OE/share 2-yr CAGR is −4.32% — the blend correctly refuses to extrapolate two good quarters off a cyclical base. Bull start 8.54% sits modestly above the latest +7% print — justified by the double-digit pointing-device growth and continued share gains; super-bull 15.54% requires a pandemic-scale demand surge and carries only 10% weight. Probabilities adjusted from the 10/25/30/25/10 default to 15/30/25/20/10 — bear weight widened per the OE_VOLATILE flag. Offsets (−12/−5/0/+5/+12pp) and OE multipliers (0.75/0.90/1.00/1.10/1.25) are the defaults. Price $104.41.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | −8.46% | 0.75 | PC/gaming demand rolls over post-cycle; tariff/supplier hits land | $22.63 | 4.86% |
| Bear | 30% | −1.46% | 0.90 | Flat-to-down revenue, OE/share repeats its cyclical slide | $36.43 | 6.71% |
| Base | 25% | 3.54% | 1.00 | Blended growth: mid-single-digit revenue, buyback tailwind | $49.86 | 8.51% |
| Bull | 20% | 8.54% | 1.10 | Recent +6-7% growth persists; video collaboration + gaming share gains | $67.47 | 10.76% |
| Super bull | 10% | 15.54% | 1.25 | New demand supercycle (AI peripherals / hybrid-work refresh) | $102.14 | 14.76% |

- **Probability-weighted: IV@15% $50.50 (−51.6% vs price), IV@12% $66.91, IV@10% $85.19, weighted IRR 8.64%, base-case IRR 8.51%**
- **Tier by numbers: D.** Hurdle prices: clears 15% only at/below $50.50, 20% at $35.73, 25% at $27.58. Diagnostics (dcf_numbers.json): OE yield 5.58%, terminal value 18.5% of IV@15%, scenario spread 4.51x, 6.6 months since FY end.

## Flags — every fragility flag resolved
- **BUYBACK_TAILWIND** (share count shrinking 3.3%/yr): already credited via the growth adjustment (+3.26pp on revenue components in the blend); not double-counted in the verdict.
- **OE_VOLATILE** (OE/share range over the last 5 yrs spans >3x): real and central — it is the pandemic boom/bust ($7.5473 FY21 → $0.6789 FY22 → $6.3623 FY24). Handled by the 3-yr median base and by widening bear weight (super bear + bear = 45% vs the 35% default).
- **NI_OCF_DIVERGENCE** (2024: NI $612,143,000 vs OCF $1,145,116,000): the one-off is a working-capital release — ΔNWC was −$381,435,000 in FY2024 as the FY2022-23 inventory overhang unwound (FY2022 ΔNWC +$595,911,000 built it, FY2023 OCF was depressed at $534,010,000). OCF ran ahead of earnings because the balance sheet shrank, not because earnings are fake; the OCF-based conservative OE is the series used throughout, and the median base dilutes the flattered FY2024 year ($6.3623) rather than resting on it.
- **DEBT_TAGS_BLANK** (no debt tag for the latest FY): resolved from the filing — this is a genuinely debt-free company, not missing data. FY2026 balance sheet: cash $1,741,546,000, total liabilities $1,637,194,000 (accounts payable $530,983,000 + accrued/other, income taxes payable $86,322,000, other non-current $237,899,000), equity $2,211,394,000, and no borrowings line anywhere; operating lease liabilities $88,155,000. Net debt is not zero — it is materially negative (net cash), which the engine's null correctly refuses to guess at.
- **WIDE_SCENARIO_SPREAD** (super-bull IV 4.51x super-bear IV): real — the range is the business's cyclicality priced in. Confidence is capped at medium, and the verdict is sized to the bear end.
- **TIER_BAND** (bear tier D at 6.71% vs bull tier C at 10.76%): verdict sized to the bear end — even the bull case does not clear 15%; only the 10%-weight super bull (14.76%) comes close.

## My thoughts / overlay
- Quality is not the debate: debt-free, $1.74B cash, capex ~1.3% of revenue, ROE/ROIC arithmetically extreme, a decade of category leadership, and ten straight growth quarters into Q1 FY27. The debate is price: at $104.41 the market pays for the bull path as the base path.
- The method range is narrow for once: median base (used) $5.8246 vs TTM $6.2576 — the TTM base would lift every IV by roughly the base ratio and still leave the weighted IRR far below 15% (this sentence states the direction from the two computed bases; no recomputed IV is quoted). Verdict is not base-sensitive.
- Risks: tariff policy on China-assembled hardware (cuts both ways — refund in Q1 FY27, costs before); the disclosed semiconductor supplier incident pressuring Q2/Q3 FY27 revenue; PC replacement cycle and gaming demand cyclicality (FY22 OE/share fell ~91% in one year); SBC $112.4M in FY26 and rising (from $70.8M in FY23) — treated as a real cost throughout.
- Margin of safety: none at this price on these numbers — the weighted IV@15% ($50.50) is 51.6% below the $104.41 price, and even the super-bull IV@15% ($102.14) sits below the price. The stock clears Andrew's 15% hurdle only at/below ~$50.

## Final verdict
- **Final tier: D** (weighted IRR 8.64%; bear D → bull C band, sized to the bear end)
- Confidence: **Medium** (high on the filing data and balance sheet; the scenario spread is 4.51x and the business is demonstrably cyclical, which caps confidence)
- One-liner: High-quality debt-free peripherals leader, moat 5/10 — but at $104.41 it prices in the bull case: weighted IRR 8.6%, IV@15% $50.50; it only clears 15% at/below ~$50.
