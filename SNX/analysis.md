# SNX — TD SYNNEX Corporation
v5 run, 2026-10-15. Market cap $21.031B at $255.14 (nasdaq_quote_api) — in scope under $40B.

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.json, or financials_history.csv — none are recomputed. Research figures are from cited earnings coverage of Q3 FY2026.

## What it is
One of the world's largest IT distributors, formed by the 2021 merger of SYNNEX and Tech Data: it buys hardware, software and services from ~1,500 technology vendors and resells/logistics-supports them to ~150,000 customers in 100+ countries. Segments are Distribution (Americas / Europe / APJ) plus Hyve Solutions, which designs and builds custom servers/racks directly for hyperscalers. It is a scale-and-logistics business, not a pricing-power business: Q3 FY2026 gross margin was 6.61% (down 61bp on low-margin AI rack mix, per earnings coverage).

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $1,531,704,000; capex $142,282,000 (tag PaymentsToAcquireProductiveAssets); SBC $66,428,000 (always a real cost).
- **Conservative owner's earnings FY2025: $1,322,994,000 = $16.05/share** (base_oe_latest_per_share $16.0499)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $1,403,242,000 — same ballpark, which supports the conservative figure.
- OE positive 4 of the last 5 fiscal years; the negative year was FY2022, the first full post-merger year (conservative OE −$206,062,000 on OCF of −$49,604,000 — a working-capital year, not an earnings collapse: FY2022 net income was $651,307,000).
- Balance sheet at FY2025 end: net debt −$1,417,068,000, i.e. net cash, −1.36× normalized OE (diagnostics). That cushion is a Nov-2025 snapshot and no longer describes the balance sheet — see FLAGS / Thoughts for the Q3 FY2026 working-capital borrowing.

**Base used = the engine's normalized base, median of the last 3 FY OE/share: $12.6262/share** (base_source: median_of_last_3_fy_oe_per_share). The TTM base was computed by ttm.py and REJECTED — see STALE_FY below for the full inputs and the reason.

**TTM inputs from ttm.py (quoted, not hand-computed):**
- OCF: FY $1,531,704,000 − prior YTD $71,326,000 + current YTD −$2,078,194,000 = **TTM −$617,816,000**
- Capex: FY $142,282,000 − prior YTD $103,989,000 + current YTD $158,853,000 = **TTM $197,146,000**
- SBC: FY $66,428,000 − prior YTD $46,238,000 + current YTD $57,771,000 = **TTM $77,961,000**
- Shares (current-YTD weighted diluted): **79,777,000**
- **TTM OE total −$892,923,000 → TTM OE/share −$11.19**

## Moat: 4/10 — weak-to-moderate, scale without pricing power
Justification: TD SYNNEX has real scale, breadth and Hyve's hyperscaler seat, but distribution is a thin-margin, low-switching-cost business where vendors and cloud marketplaces can route around the middleman and growth itself consumes working capital.
- FOR: Largest-scale IT distributor (the 2021 merger made it larger than Ingram Micro) — purchasing, logistics and credit capacity smaller rivals cannot match
- FOR: Breadth: ~1,500 vendors and ~150,000 customers in 100+ countries; selected by Microsoft in its 2025 consolidation of its global distributor network
- FOR: Hyve Solutions — direct design/build relationships with the major hyperscalers, a seat Ingram Micro and Arrow do not hold in the same way
- FOR: Durable vendor/customer operating relationships and systems integration across regions
- AGAINST: No demonstrated pricing power — Q3 FY2026 gross margin contracted 61bp to 6.61% precisely when AI volume surged; the growth mix dilutes margin
- AGAINST: Low switching costs and head-on scale competition from Ingram Micro and Arrow Electronics; vendors can sell direct and cloud marketplaces disintermediate distribution
- AGAINST: Working-capital intensity — accelerating volume consumed cash in FY2026 (TTM OCF negative, inventories $15.3B in Q3 coverage); growth is not self-funding at this mix
- AGAINST: Razor-thin earnings margin on revenue leaves little buffer against a hardware downcycle
- A 4 gives CAP = 7.2 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 7.2 years, 15-year projection.

## DCF — v5 final run (2026-10-15)
Growth recalibration (written reason): the engine's g_base is 14.63%, built from g_blend 9.84% plus a +4.79pp share-count adjustment. Two pieces of that do not deserve to be the centre case. (1) The +4.79pp buyback credit assumes the −4.79%/yr share shrink continues at pace; earnings coverage reports the $1B buyback program announced 2024 was completed in the Mar–May 2026 quarter, so the same pace needs a new authorization I have no evidence for. (2) The blend's revenue signals that are not merger artifacts centre lower: rev CAGR 3y 0.09%, latest FY revenue YoY +6.94%, OE/share CAGR 2y 12.74%. Scenario starts were therefore set via offsets (−0.1463 / −0.0863 / −0.0463 / +0.0137 / +0.0937 vs g_base) to 0 / 6 / **10** / 16 / 24%. Probabilities were skewed bear-ward to 15/25/30/20/10 (from the 10/25/30/25/10 default) because the current AI-volume surge is arriving with margin compression and negative cash conversion. OE multipliers are the defaults 0.75/0.90/1.00/1.10/1.25. Price $255.14.

Sanity check vs recent prints — the bull/super-bull starts (16% / 24%) sit below Q3 FY2026's reported revenue growth (+37.7% YoY, $21.6B) and non-GAAP EPS growth (+58.7%, $5.68), and that gap has a written reason: those prints are Hyve AI-rack pass-through volume at a 6.61% gross margin, and on the cash basis this DCF uses, the same period produced negative TTM owner's earnings because inventory/working capital absorbed the cash. Accrual EPS growth that consumes cash cannot be plugged in as owner's-earnings growth. Q4 FY2026 guidance (revenue $21.8–22.6B, non-GAAP EPS $5.65–6.15, per earnings coverage) says the volume persists into year-end; whether it converts to cash is exactly what the scenario spread is pricing.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | 0.0% | 0.75 | AI rack volume fades, WC stays trapped, hardware cycle turns | $70.50 | 5.89% |
| Bear | 25% | 6.0% | 0.90 | Volume grows but at dilutive margins; cash conversion stays weak | $106.53 | 7.82% |
| Base | 30% | 10.0% | 1.00 | Mid-single-digit revenue growth, OE/share compounding from buybacks at a slower pace and normal Q4 cash collection | $137.72 | 9.45% |
| Bull | 20% | 16.0% | 1.10 | AI/data-center demand sustains, Hyve mix improves, WC normalizes | $189.48 | 12.03% |
| Super bull | 10% | 24.0% | 1.25 | Durable AI infrastructure supercycle with restored cash conversion | $288.22 | 16.38% |

- **Probability-weighted: IV@15% $145.24 (−43.07% vs price), IV@12% $195.00, IV@10% $250.67, weighted IRR 9.88%, base-case IRR 9.45%**
- **Tier by numbers: D.** Diagnostics: OE yield 4.95%, terminal value 19.71% of IV@15%, scenario spread 4.09×, net debt −1.36× normalized OE (FY2025 end), 10.48 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 2025-11-30, 10.48 months ago): ttm.py was run and its full inputs are quoted above. The TTM base was NOT used, with this specific reason: the TTM window ending 2026-08-31 is structurally distorted for this company. The ttm.json inputs themselves show FY2025 OCF of $1,531,704,000 against prior-YTD (9-month) OCF of only $71,326,000 — i.e. this distributor's cash arrives overwhelmingly after the 9-month mark, in the fiscal Q4 collection quarter, so any TTM ending at Q3 systematically omits the strongest cash quarter. In FY2026 that seasonal hole coincides with a real Hyve inventory build (current-YTD OCF −$2,078,194,000; Q3 coverage: inventories $15.3B, Q3 free cash flow −$975.6M, 9-month operating cash outflow $2.08B to support Hyve's new customers/programs). The resulting TTM OE of −$11.19/share measures a working-capital position at Aug 31, not normalized earnings power — FY2025 OE was +$16.05/share and Q3 FY2026 accrual earnings grew strongly. Using it would force a fake Tier F. The median-of-3-FY base ($12.6262/share) is used instead, and the verdict is sized down (bear-skewed probs, growth recalibrated down, confidence low) for the genuine cash-conversion risk the TTM exposes.
- **BUYBACK_TAILWIND** (share count shrinking 4.8%/yr): the engine already credited +4.79pp via the growth adjustment; the final run's recalibrated offsets deliberately remove reliance on that pace continuing (the $1B program was reported complete in May 2026), so the tailwind is not double-counted in the verdict — if anything the final starts are set as if it slows.
- **BASIS_BREAK_SUSPECT** (>60% revenue jump in the last 5 years): identified — the SYNNEX + Tech Data merger that formed TD SYNNEX in 2021. Revenue in financials_history.csv goes from $31,614,169,000 (FY2021) to $62,343,810,000 (FY2022). The 5-yr revenue CAGR of 25.63% is a merger artifact and was discarded; growth inputs were set from the post-merger signals only (3-yr revenue CAGR 0.09%, latest FY YoY +6.94%, OE/share CAGR 2y 12.74%).
- **NI_OCF_DIVERGENCE** (NI vs OCF differ >40% in 2023, 2024, 2025): resolved — this is a distributor's working-capital and non-cash profile, not a one-off tax deposit or impairment. In each flagged year OCF exceeded net income (2023: NI $626,911,000 vs OCF $1,407,373,000; 2024: NI $689,091,000 vs OCF $1,217,724,000; 2025: NI $827,660,000 vs OCF $1,531,704,000) with D&A of $418,315,000 / $407,532,000 / $414,219,000 and large ΔNWC swings in the history file. The OCF-based conservative OE is the series used throughout, so the divergence does not contaminate the base — but its mirror image in FY2026 (accrual profits, negative OCF) is the live risk, and it is handled in STALE_FY above and in the bear-skewed probabilities.
- **WIDE_SCENARIO_SPREAD** (super-bull IV 4.09× super-bear IV): real — cash conversion of the AI volume is a genuinely binary near-term question. Confidence is set to low and the verdict is sized to the conservative end.

## My thoughts / overlay
- Method range: the engine's default-input preliminary run (moat 5, default probs/offsets, same median base) printed weighted IRR 11.78% / IV@15% $182.36 — Tier C. The final recalibrated run (moat 4, growth centred on post-merger organic signals without the full buyback credit, bear-skewed probs) prints 9.88% — Tier D. The defensible range is therefore C-to-D, and the verdict takes the conservative end: at $255.14 the buyer needs the bull case just to reach a low-teens IRR.
- Quality is mixed, not broken: FY2023–25 conservative OE was consistently positive and the maintenance definition agrees with the conservative one; SBC is small ($66,428,000 in FY2025). The problem is price and cash conversion, not the existence of earnings.
- Balance-sheet overlay: FY2025 ended in net cash (−$1,417,068,000 net debt), but Q3 FY2026 coverage reports cash of $749.3M and long-term borrowings of $3.60B after the working-capital build — the FY cushion was spent funding Hyve growth. I do not credit the FY net-cash figure as current protection in the verdict.
- Price that clears the hurdle: the weighted IV@15% is $145.24 — SNX clears 15% only at or below that price on these inputs, roughly 43% below the current $255.14. There is no margin of safety at the current price; even the bull case ($189.48) sits below it.

## Final verdict
- **Final tier: D** (weighted IRR 9.88% on the final inputs; defensible method range C to D)
- Confidence: **Low** (wide scenario spread, and the FY2026 cash-conversion question is not resolved until the Q4 collection quarter prints)
- One-liner: Real scale distributor, moat 4/10, but thin-margin AI volume is consuming cash (TTM OE negative on a working-capital build) and at $255.14 it does not clear 15% — it clears 15% only at or below $145.24.
