# INCY — Incyte Corporation
v5 run, 2026-10-15. Market cap $22.84B at $113.78 (nasdaq_quote_api) — in scope under $40B.

All figures below are copied from dcf_numbers.json, ttm.py output (ttm.json), or financials_history.csv — none are recomputed.

## What it is
Biopharmaceutical company built on JAK inhibition. Core product Jakafi/Jakafi XR (ruxolitinib) for myelofibrosis, polycythemia vera and graft-versus-host disease; the same molecule as a cream is Opzelura (atopic dermatitis, vitiligo). A broadening hematology/oncology portfolio (Niktimvo, Monjuvi/Minjuvi, Zynyz, Iclusig royalties) and an inflammation/autoimmunity pipeline (povorcitinib and others) are the diversification story ahead of Jakafi's patent cliff — core patents protected by litigation settlement and pediatric exclusivity only until December 2028, with generic entry expected from then.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** revenue $5,141,242,000; net income $1,286,650,000; operating cash flow $1,413,498,000; capex $58,867,000; SBC $249,346,000 (always a real cost).
- **Conservative owner's earnings FY2025: $1,105,285,000 = $5.51/share** (base_oe_latest_per_share in dcf_numbers.json).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $819,508,000 — below the conservative figure, mainly on a large working-capital swing in FY2025; the OCF-based conservative figure is the cleaner series here.
- OE positive 4 of the last 5 fiscal years (oe_positive_years_of_last_5 in dcf_numbers.json) — the one negative year is FY2024, explained under FLAGS: it carries the Escient acquisition charge.
- Balance sheet: cash $3,097,817,000 at FY2025 (financials_history.csv; the 10-K reports $3,580.6M of cash, cash equivalents and marketable securities); no debt tags filed — the engine's net_debt_latest is null. This is a net-cash company; there is no HIGH_NET_DEBT flag and leverage is not part of the verdict.

**Base used = TTM owner's earnings through Q1 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $1,413,498,000 − prior YTD $266,067,000 + current YTD $369,351,000 = **TTM $1,516,782,000**
- Capex: FY $58,867,000 − prior YTD $3,169,000 + current YTD $10,200,000 = **TTM $65,898,000**
- SBC: FY $249,346,000 − prior YTD $60,982,000 + current YTD $64,126,000 = **TTM $252,490,000**
- Shares (current-YTD weighted diluted): **206,830,000**
- **TTM OE total $1,198,394,000 → base OE/share $5.79** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $1.10/share — rejected as the base, see BASE_DIVERGENCE under FLAGS. It is a 2023 figure carried forward by a one-off-crushed 2024, and it describes a company with roughly $3.7B of revenue, not the current ~$5.1B one.
- TTM quality note: the TTM window contains the May 2025 Novartis contract-dispute settlement — Incyte **paid** $280.0M cash and recorded a $242.2M non-cash gain (accrued royalties in excess of the amount paid). On the OCF-based conservative definition the cash payment depresses TTM OE while the gain adds no cash, so the $5.79 TTM base is if anything penalized, not flattered, by the settlement. The settlement also halves the Jakafi royalty rate payable to Novartis from January 1, 2025, a recurring benefit to forward margins.
- Post-TTM print (Q2 2026, research): total revenue $1.67B, reported +38% YoY, but that includes a $246M one-time, non-cash Opzelura benefit from a CMS settlement — underlying net sales growth was +17%. Jakafi net sales $816.7M (+7%); Opzelura $204M excluding the one-time benefit (+24%); hematology/oncology portfolio +69%. Management raised 2026 net product revenue guidance to $5.13–$5.26B (Jakafi held at $3.22–$3.27B; Opzelura raised to $1.05–$1.10B).

## Moat: 5/10 — moderate, strong near-term, time-limited
Justification: a patented, entrenched lead product with real pricing power and a second franchise growing off the same molecule — but the lead product's protection expires in December 2028, concentration is extreme, and nothing yet replaces Jakafi at scale. A patent moat with a known expiry date inside the forecast window is a moderate moat, not a wide one.
- FOR: Jakafi is the entrenched standard in myelofibrosis/PV/GVHD with deep prescriber familiarity; litigation settlement plus pediatric exclusivity blocks U.S. generics until December 2028, and the Jakafi XR formulation gives a conversion lever into the cliff.
- FOR: Ruxolitinib extends into dermatology — Opzelura is the first topical JAK inhibitor (vitiligo, atopic dermatitis) and is growing +24% underlying with guidance just raised.
- FOR: Diversification is real and accelerating — hematology/oncology portfolio +69% in Q2 2026 (Niktimvo, Monjuvi/Minjuvi, Zynyz), plus late-stage pipeline (povorcitinib) with ten data readouts expected in H2 2026.
- FOR: Net-cash balance sheet ($3,580.6M cash and marketable securities at FY2025 per the 10-K) funds the pipeline and launches through the cliff with no financing risk.
- AGAINST: Concentration — Jakafi is over 60% of revenue and faces generic entry from December 2028, with erosion of 25–30% a year or worse the standard expectation; the DCF fade (growth to a +2.5% terminal rate, never negative) cannot model that cliff, which is a model limitation the verdict compensates for with heavier bear weights.
- AGAINST: JAK-class safety overhang (boxed warnings) and direct competition — GSK's Ojjaara in myelofibrosis with anemia, AbbVie/Lilly systemics competing for dermatology share of mind.
- AGAINST: Pipeline/binary risk — the post-2028 growth story depends on Phase 3 readouts and launches that have not happened yet.
- AGAINST: U.S. pricing pressure, including Inflation Reduction Act Medicare negotiation exposure for a high-spend drug.
- AGAINST: Persistent SBC load — TTM SBC $252,490,000, a real and recurring cost already charged in the base.
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection. Even this fade is generous past 2028 — see the scenario weights.

## DCF — v5 final run (2026-10-15)
Growth recalibration (written reason): the engine's g_base is 21.62%, built from a blend (rev CAGR 5y 14.03%, 3y 14.84%, latest rev YoY 21.22%, OE/share CAGR 2y 123.81%) plus a +3.59pp share-count adjustment. Two components are artifacts: the 123.81% OE/share CAGR is measured off the Escient-depressed base period (see FLAGS), and the share-count adjustment credits the one-off June 2024 $2.0B buyback (33.3M shares at $60.00) as if it were a recurring trend — TTM diluted shares actually **rose** to 206,830,000. The prints that mean something center lower: 5y/3y revenue CAGRs of ~14–15%, FY2025 revenue +21.22%, and Q2 2026 underlying net sales +17% (the reported +38% carries the $246M one-time CMS benefit). Scenario starts were therefore set via offsets (−0.17 / −0.10 / −0.05 / 0.00 / +0.07 vs g_base) to 4.6 / 11.6 / **16.6** / 21.6 / 28.6%. The base start (16.6%) matches the latest underlying print; bull (21.6%) matches FY2025's revenue growth; super bull (28.6%) sits below the reported +38% Q2 print because that print is one-off-inflated — it requires Opzelura acceleration plus new launches to land, which is why it gets only 10%.
Probabilities were skewed bear-heavy vs the 10/25/30/25/10 defaults — 15/30/30/15/10 — because of OE_VOLATILE, the December 2028 cliff arriving inside the hold period, and the fade model's inability to go negative after it. OE multipliers are the defaults 0.75/0.90/1.00/1.10/1.25. Price $113.78.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | 4.6% | 0.75 | Cliff erosion starts early and bites hard; pipeline readouts disappoint | $38.91 | 6.85% |
| Bear | 30% | 11.6% | 0.90 | Growth decays to high-single digits; post-2028 Jakafi erosion offsets Opzelura | $62.34 | 9.65% |
| Base | 30% | 16.6% | 1.00 | Underlying mid-teens growth holds to the cliff, diversification partly offsets it | $84.94 | 12.14% |
| Bull | 15% | 21.6% | 1.10 | FY2025 pace sustains; XR conversion blunts generic erosion | $114.31 | 15.05% |
| Super bull | 10% | 28.6% | 1.25 | Opzelura plus new launches fully replace Jakafi economics | $171.54 | 19.86% |

- **Probability-weighted: IV@15% $84.32 (−25.9% vs price), IV@12% $115.11, IV@10% $149.80, weighted IRR 12.10%, base-case IRR 12.14%**
- **Tier by numbers: C.** Diagnostics (dcf_numbers.json): OE yield 5.09%, terminal value 21.5% of IV@15%, scenario spread 4.41x, 9.5 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.5 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q1 2026, quoted above. Q2 2026 prints (research section) confirm the TTM run-rate is not stale: underlying growth continued at +17%.
- **BASE_DIVERGENCE** (latest FY OE/share $5.51 vs 3-yr median $1.10): the **median** is the distorted one. The last-3-FY set is 2023 ($1.10), 2024 (−$0.08 on the filed history: OE −$16,984,000) and 2025 ($5.51); the median lands on 2023 only because 2024 was crushed by a one-off (next flag). The latest FY and the TTM ($5.79) agree with each other and with the current revenue scale; the TTM base is used.
- **NI_OCF_DIVERGENCE (2024)**: the one-off is the Escient Pharmaceuticals acquisition (closed Q2 2024, $750M plus net cash). Q2 2025 reporting states R&D included $691.9M of expense relating to the Escient acquisition in Q2 2024, and the 10-K notes $710.9M of nondeductible charges associated with it. That charge — acquired in-process R&D expensed through operations — is why FY2024 net income was $32,615,000 and operating income $61,366,000 against revenue of $4,241,217,000, and why FY2024 conservative OE was −$16,984,000. It is an investment outlay, not a recurring operating cost, and it is outside both the FY2025 and TTM windows. The OCF-based series is used throughout, as filed.
- **OE_VOLATILE** (OE/share range >3x over 5 years): real on the filed series, but the volatility is event-driven, not cyclical — the Escient charge (2024 down) and the recovery plus Novartis settlement year (2025 up). Handled by the TTM base (which excludes the Escient year) plus bear-heavy weights: 45% on bear-or-worse.
- **BUYBACK_TAILWIND** (share count −3.59%/yr): driven by the single June 2024 $2.0B repurchase, not a recurring program at that pace — the current-YTD diluted count (206,830,000) is **above** the FY2025 count (200,700,000). The +3.59pp growth credit inside g_base is one reason the scenario offsets were recalibrated downward; the tailwind is not double-counted in the verdict.
- **WIDE_SCENARIO_SPREAD** (4.41x): real — the outcome range genuinely is this wide with a patent cliff inside the window. Confidence is capped at medium and the verdict is sized to the conservative end.
- **LOW_OE_YIELD** fired only on the preliminary median-base run (1.0%); on the TTM base actually used, OE yield is 5.09% and the flag does not fire. Noted so the preliminary flag is not left dangling.

## My thoughts / overlay
- The honest headline is the method range. On the engine's median base the preliminary run printed weighted IRR 5.27% / IV@15% $21.00 (Tier D) — a number built on a 2023 base year and an Escient-crushed median, not on the current business. On the TTM base with unadjusted default growth/probabilities the run printed weighted IRR 14.74% / IV@15% $110.80 (Tier C, top of the band). The final run — TTM base, growth recalibrated to underlying prints, bear weight raised for the cliff — prints 12.10% / $84.32. Every defensible TTM-based method lands in Tier C; only the distorted median base says D, and only un-recalibrated momentum growth gets near B. Tier C is robust, its position inside C is not.
- Model limitation, stated plainly: the standardized fade takes growth to +2.5% and never negative, so no scenario in the engine actually models Jakafi revenue falling after December 2028. The bear/super-bear OE multipliers (0.90/0.75) and the 45% bear-or-worse weight are the compensation. A bespoke model with an explicit cliff would print lower than this screen does.
- Quality is not the debate: asset-light (TTM capex $65,898,000 against OCF $1,516,782,000), net cash, SBC charged in full, and a royalty-rate halving that structurally lifts forward Jakafi margins. The debate is duration — how much of the current $5.79/share survives 2029.
- Hurdle math: the price that clears 15% on the weighted case is the weighted IV@15% itself, **$84.32**. With a margin of safety against the bear case (IV@15% $62.34), a buyer wanting the 15% hurdle to survive the cliff landing badly needs an entry nearer the $62–$84 range, not $113.78. At $113.78 even the bull case only just clears 15% (IRR 15.05%).

## Final verdict
- **Final tier: C** (weighted IRR 12.10% on the v5 final inputs; TTM-based methods span C, the distorted median base would say D)
- Confidence: **Medium** (high on the TTM base and OE quality, low on any single post-cliff path — scenario spread 4.41x caps confidence)
- One-liner: Quality net-cash biopharma, moat 5/10 — does not clear 15% at $113.78 (weighted IRR 12.1%, IV@15% $84.32) because the December 2028 Jakafi cliff sits inside the forecast window; it clears 15% at $84.32.
