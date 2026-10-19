# ARW — Arrow Electronics, Inc.
Pass-1 run, 2026-10-18, engine 5.4.0. Price $214.61 (nasdaq_quote_api), market cap $11.214B — in scope under $40B.

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.json or fundamentals.json — none are recomputed.

## What it is
Global distributor of electronic components (Global Components) and value-added enterprise computing solutions (ECS). Scale duopoly with Avnet: it aggregates thousands of suppliers for hundreds of thousands of OEMs, contract manufacturers and VARs, adding design-in engineering, supply-chain services and financing. Structurally thin economics: gross margin 11.2% and operating margin 2.7% in FY2025 (fundamentals.json), and the model is working-capital-heavy — cash flow is a cash-conversion game, not an earnings game. No dividend; capital return is buybacks only (shares diluted 92.03M in FY2016 → 52,255,000 latest).

Current state: a cyclical upswing. Q2 2026 (10-Q, period ended 2026-07-04) revenue was $9.99B, +31.8% YoY, with Global Components +39% and ECS +14% on AI-infrastructure demand; Q3 2026 guidance is sales of $9.6–$10.2B (+28% at the midpoint). Against that, leadership is in transition: CEO Sean Kerins separated on 2025-09-16 (company stated it was not related to its financial statements) and director Bill Austen is interim president and CEO while a permanent search runs. ECS also took charges on underperforming multiyear contracts with a strategic partner ($21.7M in Q1 2026, $26.6M in Q2 2026, per the Q2 reporting), and one element of that Beyond Distribution agreement has been terminated.

## Owner's earnings
**Filed history (financials_history.csv / fundamentals.json):** OE/share by fiscal year — FY2021 $4.09, FY2022 -$2.37, FY2023 $10.18, FY2024 $18.65, FY2025 -$1.25. OE-positive in only 3 of the last 5 years. Net income is far steadier than OCF (FY2025 net income $571M vs OCF $64M; FY2024 net income $392M vs OCF $1,130M) — the OE series is dominated by working-capital swings, not by earnings power appearing and disappearing.

**Base used = normalized median of the last 3 FY OE/share: $10.18/share** (base_source: median_of_last_3_fy_oe_per_share; latest FY OE total -$65.1M). The three median inputs are themselves WC extremes ($10.18 / $18.65 / -$1.25), which is exactly why the median — not any single year and not the TTM print — is the defensible base for this name.

**TTM was computed and rejected as the base.** ttm.py through 2026-07-04, legs quoted verbatim:
- OCF: FY $64,049,000 − prior YTD $145,783,000 + current YTD $1,018,101,000 = **TTM $936,367,000**
- Capex: FY $101,254,000 − prior YTD $43,597,000 + current YTD $53,246,000 = **TTM $110,903,000**
- SBC: FY $27,883,000 − prior YTD $30,200,000 + current YTD $22,415,000 = **TTM $20,098,000**
- Shares (current-YTD weighted diluted): **51,787,000**
- **TTM OE total $805,366,000 → $15.55/share**

Why rejected: the H1 2026 OCF leg ($1,018M vs $146M in H1 2025) is timing, not run-rate. Management said on the Q2 2026 call that the strong cash generation is driven in part by timing effects from the supply-chain services offering, which may partially unwind as the year progresses, and that AR/AP flows in that offering create quarter-end swings. The filed balance sheet shows the same gross-up: receivables went from $13.03B (FY2024) to $19.74B (FY2025) while total assets went from $21.76B to $29.08B (fundamentals.json) — AR and AP ballooning together. A TTM-base variant run is reported under Thoughts as the method range, not used as the headline.

Balance sheet: net debt $2.779B (key_numbers.md; basis LongTermDebtNoncurrent+DebtCurrent), lease liabilities $263,258,000, equity $6,584,712,000 on the FY2025 history — net debt is 5.22x normalized OE, so the equity is a levered claim on a cyclical OE stream.

## Moat: 4/10 — weak-to-narrow
Justification: Scale duopoly with Avnet in global components distribution plus design-in and supply-chain services give real but narrow advantages; the business is a thin-margin, working-capital-heavy intermediary with no pricing power — gross margin fell from 13.0% (FY2022) to 11.2% (FY2025) and roic_proxy fell from 17.2% (FY2022) to 7.1% (FY2024) and 7.0% (FY2025), at/below the cost of capital through the downcycle.
- FOR: Global scale duopoly with Avnet — largest components distributor, broad line card and logistics network smaller rivals cannot replicate; design-in, engineering and supply-chain services embed Arrow in customer bills of materials, creating switching friction; supplier and customer fragmentation (thousands of vendors, hundreds of thousands of OEMs/CMs/VARs) makes aggregation genuinely valuable; ECS value-added distribution (bundled hardware/software/cloud, financing, pre/post-sales support) is stickier than commodity components.
- AGAINST: No pricing power — gross margin 13.0% (FY2022) → 11.2% (FY2025), operating margin 2.7% in FY2025, distribution economics are competed away; ROIC fell through the cycle (roic_proxy 17.2% FY2022, 12.2% FY2023, 7.1% FY2024, 7.0% FY2025 — not durably above the cost of capital); disintermediation risk (suppliers selling direct; Digi-Key/TTI/Future and marketplaces); working-capital intensity (FY2025 revenue +10.5% but OE -$65M; OCF dominated by AR/AP timing swings); deep cyclicality (revenue -10.8% in FY2023 and -15.7% in FY2024 on the filed history; OE/share swung from +$18.65 in FY2024 to -$1.25 in FY2025).
- ROIC / margin evidence (fundamentals.json, roic_proxy series): FY2021 15.7%, FY2022 17.2%, FY2023 12.2%, FY2024 7.1%, FY2025 7.0%. Gross margin: 12.2% / 13.0% / 12.5% / 11.8% / 11.2% over the same years. A moat above 4 would need ROIC held well above the cost of capital through the cycle; Arrow earned that in the 2021-22 shortage boom and gave it back in the downcycle. Management cited Q2 2026 return on invested capital of 13.9% YoY-improved on the call — that is the upcycle annualizing, consistent with the pattern, not a break from it.
- A 4 gives CAP = 7.2 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 7.2 years, 15-year projection.

## DCF — final run (2026-10-18)
Growth and scenario design (written reasons): the engine blend is 6.48% (components: rev CAGR 5y 1.48%, rev CAGR 3y -5.98%, latest rev YoY 10.49%, share-count adj +5.00pp capped). Scenario starts were set via offsets -0.12 / -0.05 / 0 / +0.08 / +0.15 vs g_base.
- **Sanity check vs recent prints:** TTM revenue growth is +26.0% and Q2 2026 printed +31.8% YoY with Q3 guided +28% — every scenario start, including super bull at 21.5%, sits below the latest revenue prints. That is deliberate, for three written reasons: (1) the prints are a cyclical AI-components upswing off a two-year downcycle (revenue CAGR is 1.48% over 5 years and -5.98% over 3 years on the filed history); (2) part of the print is the supply-chain-services AR/AP gross-up, which inflates revenue and OCF timing without adding equivalent owner's earnings; (3) in this business OE growth does not follow revenue growth in upcycles — growth absorbs working capital (FY2025: revenue +10.49%, OE/share -$1.25). The bull (+14.5%) and super-bull (+21.5%) offsets were raised above the +5/+12pp defaults to credit the real momentum (book-to-bill, backlog, AI demand) without capitalizing a peak print.
- Probabilities 15/30/30/15/10 — bear weight widened from the 10/25 defaults per the OE_VOLATILE and HIGH_NET_DEBT flags; OE multipliers are the defaults 0.75/0.90/1.00/1.10/1.25. Price $214.61.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | -5.5% | 0.75 | Components downcycle repeats; WC build and ECS charges eat the OE stream; leverage bites | $45.82 | 4.98% |
| Bear | 30% | 1.5% | 0.9 | Upturn fades fast; through-cycle distribution economics at trough margins | $72.22 | 6.68% |
| Base | 30% | 6.5% | 1.0 | Normalized median OE grows at the blend; buyback tailwind already credited | $97.19 | 8.28% |
| Bull | 15% | 14.5% | 1.1 | AI-components upcycle persists with WC-neutral conversion, as in FY2023-24 | $144.40 | 11.17% |
| Super bull | 10% | 21.5% | 1.25 | Multi-year AI infrastructure cycle at shortage-era returns on capital | $212.15 | 14.87% |

- **Probability-weighted: IV@15% $100.57 (-53.1% vs price), IV@12% $134.12, IV@10% $171.57, weighted IRR 8.54%, base-case IRR 8.28%**
- **Tier by numbers: D.** Diagnostics (key_numbers.md): OE yield 4.74%, terminal value 19.1% of IV@15%, scenario spread 4.63x, net debt 5.22x normalized OE, 9.6 months since FY end.
- Hurdle-clearing prices (weighted path): 15% at $100.57, 20% at $70.48, 25% at $53.96. Even the super-bull scenario alone (IRR 14.87%, IV@15% $212.15) does not clear 15% at $214.61.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.6 months ago): resolved by computing the TTM — ttm.py through 2026-07-04 gives TTM OE $805,366,000 = $15.55/share (legs quoted above). It was NOT used as the base: management attributes the H1 2026 OCF surge in part to supply-chain-services timing that may partially unwind, so the TTM print is the distorted figure here; the median base stands and the TTM run is carried as the optimistic end of the method range.
- **BUYBACK_TAILWIND** (share count -7.23%/yr): already credited via the capped +5.00pp growth adjustment in the blend; not double-counted in the verdict. Note the pace has slowed — TTM buybacks were $126,667,000 per fundamentals.json, small against an $11.214B market cap.
- **OE_VOLATILE** (OE/share range >3x over 5 years): real and structural — FY2021 $4.09, FY2022 -$2.37, FY2023 $10.18, FY2024 $18.65, FY2025 -$1.25, OE-positive only 3/5 years. Handled with the median base, bear-side probabilities raised to 45% combined (super bear + bear), and confidence low.
- **NI_OCF_DIVERGENCE** (2024, 2025): working capital, identified in the filing history — FY2024 net income $392M vs OCF $1,130M with a working-capital release (delta_nwc -$649M in financials_history.csv); FY2025 net income $571M vs OCF $64M with a working-capital build (delta_nwc +$582M) as receivables ballooned from $13.03B to $19.74B on the supply-chain-services gross-up. No tax-deposit or impairment one-off is needed to explain it; the OCF-based OE base is therefore a WC-timing series, which is why the median of three extreme years is used and no single year is trusted.
- **BASE_DIVERGENCE** (latest FY -$1.25 vs 3-yr median $10.18): BOTH are distorted, in opposite directions — FY2025 is a WC-build year (revenue +10.49% consumed the cash) and FY2024's $18.65 inside the median window is a WC-release year. The median is kept because it is the engine's normalized construction and sits between the two distortions; the distortion itself is the finding, and it caps confidence at low.
- **WIDE_SCENARIO_SPREAD** (4.63x): real — a levered cyclical distributor's outcome range IS wide. Confidence is low (never high with this flag), and the verdict is sized to the bear end.
- **HIGH_NET_DEBT** (net debt 5.22x normalized OE): balance sheet stated from the filing outputs — net debt $2.779B, lease liabilities $263,258,000, equity $6,584,712,000 (FY2025). Gross debt has since fallen (management cited $2.2B gross balance-sheet debt at Q2 2026 after paydown), but on the scored (latest FY) balance sheet the leverage stands; bear cases carry the 0.75 / 0.90 OE multipliers against it.
- **TIER_BAND** (bear tier D at 6.68% vs bull tier C at 11.17%): the verdict spans tiers and is sized to the bear end — the final tier is D, and even the bull case does not clear 15%.

## My thoughts / overlay
- The honest headline is the method range: on the normalized median base the weighted IRR is 8.54% (Tier D, IV@15% $100.57); on the rejected TTM base ($15.55/share, moat 4, default probabilities) a variant run printed weighted IRR 11.80% and IV@15% $157.49 (Tier C). No defensible base gets ARW to 15% at $214.61 — the argument is only about how far short it falls.
- Quality is not the debate either: this is a real, scaled franchise in a structurally thin business. Revenue of $30.85B in FY2025 produced $571M of net income and -$65M of conservative OE; the earnings that exist are hostage to AR/AP timing in a supply-chain-services book that grossed the balance sheet up by ~$7B in one year.
- Risks: components downcycle after the AI build-out (the FY2023-24 revenue declines are the template); ECS contract charges recurring ($21.7M Q1, $26.6M Q2 2026) and the restructured strategic-partner relationship; interim-CEO leadership overhang since 2025-09-16; disintermediation; leverage if OE goes negative again as in FY2022 and FY2025.
- What would change the verdict: a price near $100.57 (the 15% hurdle price on the weighted path), or evidence that the TTM OE level survives a working-capital unwind — i.e. a full fiscal year printing OE near $15/share without an AR/AP timing tailwind.

## Final verdict
- **Final tier: D** (weighted IRR 8.54% on the normalized median base; method range D to C across the median and TTM bases)
- Confidence: **Low** (WIDE_SCENARIO_SPREAD 4.63x, both candidate bases distorted by working-capital timing in opposite directions, net debt 5.22x normalized OE)
- One-liner: Cyclical thin-margin distributor, moat 4/10 — does not clear 15% on the normalized median base (8.5% weighted IRR, IV@15% $100.57 vs $214.61 price); even the WC-timing-flattered TTM base only reaches Tier C, and it would need ~$101 to clear 15%.
