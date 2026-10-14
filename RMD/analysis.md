# RMD — ResMed Inc.
v5 run, 2026-10-14. In scope (market cap $34.213B at $234.25, nasdaq_quote_api — key_numbers.md).

All figures below are copied from key_numbers.md, dcf_numbers.json, or financials_history.csv — none are recomputed.

## What it is
Global leader in sleep-apnea and respiratory care: CPAP/APAP devices (AirSense platform), masks and recurring resupply, ventilators (Astral), and the AirView/myAir cloud ecosystem connecting devices, providers, and patients. Fiscal year ends June 30. Q4 FY2026 (reported Aug 6, 2026): revenue +9% headline (+8% constant currency), non-GAAP EPS +16%; full FY2026 revenue +10% with gross margin up 290bp for the year on supply-chain productivity. FY2027 is the company's first formal guidance: core constant-currency revenue growth of 5–7% and core EPS growth of 12–14% (search results, Q4 FY2026 earnings coverage). The MatrixCare software business was divested (closed September 1, 2026) to focus the portfolio on the core.

## Owner's earnings
**FY2026 (10-K via EDGAR, from financials_history.csv):** operating cash flow $1,805,829,000; capex $156,285,000 (tag: PaymentsToAcquirePropertyPlantAndEquipment); SBC $104,348,000 (always a real cost); D&A $201,342,000; net income $1,523,293,000; revenue $5,653,443,000.
- **Conservative owner's earnings FY2026: $1,545,196,000 = $10.58/share** (key_numbers.md: latest FY OE total $1.545B, base OE/share $10.58)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $1,384,990,000 — below the conservative figure because of the FY2026 working-capital build recorded in the history file; the OCF-based conservative figure is the cleaner base and is what the engine uses.
- OE positive 5 of the last 5 fiscal years. Net debt $-1.070B — i.e. net cash (key_numbers.md); net debt / normalized OE −0.69x. The balance sheet is a strength, not a risk: FY2026 free cash flow was over $1.6B (search results) and the company plans to return over $1.85B in FY2027 via a raised dividend (+10%) and buybacks including a $450M accelerated repurchase and a $1.5B repurchase program.
- SBC is modest relative to OCF and capex is light (FY2027 capex guided at $160–180M, search results) — this is a genuinely cash-generative franchise, not an accounting-earnings story.

**Base used = normalized base, median of last 3 FY OE/share = $10.58/share** (base_source: median_of_last_3_fy_oe_per_share). Latest FY OE/share is also $10.58, so the normalized and latest bases coincide — no BASE_DIVERGENCE flag and no base dispute to resolve. FY end was 3.5 months ago (key_numbers.md), so no STALE_FY flag and no TTM override was needed; the FY2026 10-K is the current base.

## Moat: 7/10 — strong
Justification: Dominant global CPAP franchise (~48% global share; US share estimated far higher while Philips Respironics has been out of the US market since its 2021 recall) with a large installed base that throws off recurring mask/resupply revenue, a cloud ecosystem (AirView/myAir) embedded in provider workflows, a deep patent portfolio, and proven pricing/margin power (FY2026 gross margin expanded 290bp, non-GAAP EPS +17% on +10% revenue). Capped at 7, not higher: Philips is expected to re-enter the US (analysts point to FY2028), Fisher & Paykel and low-cost BMC compete on masks/devices, GLP-1 therapy is a long-run narrative headwind even though current claims data shows it aiding PAP starts/adherence, and the core is concentrated in one therapy category — plus a live Astral ventilator Class I recall/sales suspension.
- FOR: Dominant CPAP share (~48% global; US share est. much higher with Philips out since 2021 recall); installed base drives recurring masks/resupply revenue; AirView/myAir cloud ecosystem embedded in provider and patient workflows; deep patent portfolio and regulatory/reimbursement know-how; proven pricing and margin power — FY26 gross margin +290bp, EPS growing faster than revenue.
- AGAINST: Philips Respironics US re-entry expected (analysts point to FY2028) caps share gains; Fisher & Paykel and low-cost BMC/React compete in masks and devices; GLP-1 drugs are a long-run OSA-treatment narrative headwind; single-category concentration in sleep/respiratory therapy; Astral ventilator Class I recall — FY27 sales suspended, $42M Q4 charge.
- A 7 gives CAP = 11.1 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 11.1 years, 15-year projection.

## DCF — v5 final run (2026-10-14)
Growth inputs: engine blend 11.14% → g_base 11.46% (components, key_numbers.md: rev CAGR 5y 12.08%, rev CAGR 3y 10.21%, latest rev YoY 9.85%, OE/share CAGR 2y 13.05%; share-count CAGR −0.32% adds +0.32pp). Default offsets (−12/−5/0/+5/+12pp) and OE multipliers (0.75/0.90/1.00/1.10/1.25) kept; probabilities at the 10/25/30/25/10 defaults. Price $234.25.

**Sanity check vs actual prints (required):** the base start of 11.5% is OE/share growth, not revenue growth. It sits above FY2027 guided core revenue growth (5–7% constant currency) but below guided core EPS growth (12–14%) and below FY2026's actual non-GAAP EPS growth (+17%) — defensible because the guide itself has EPS growing roughly twice revenue on margin expansion and buybacks, and this model's OE/share follows the EPS line, not the revenue line. The bull start (16.5%) is in line with what FY2026 actually printed on EPS. The super-bull start (23.5%) exceeds every recent print and the top of guidance — it is a genuine stretch case (Philips re-entry slipping well past FY2028, GLP-1 funnel effects compounding, margin expansion sustained) and carries only 10% weight for that reason. The super-bear start (−0.5%) reflects the known FY2027 Astral suspension headwind (~130bp of revenue, ~$0.15 EPS dilution per search results) compounding with an early Philips return.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -0.5% | 0.75 | Philips returns early and aggressive; Astral drag + GLP-1 erosion bite | $56.40 | 5.37% |
| Bear | 25% | 6.5% | 0.9 | Growth settles at the low end of the revenue guide; margins stop expanding | $94.16 | 7.73% |
| Base | 30% | 11.5% | 1.0 | Guided path: mid-single-digit revenue, low-teens EPS via margin + buybacks | $132.66 | 9.99% |
| Bull | 25% | 16.5% | 1.1 | FY2026-style EPS growth persists; Philips return stays slow | $185.09 | 12.74% |
| Super bull | 10% | 23.5% | 1.25 | Stretch: share keeps compounding, GLP-1 funnel + margins both deliver | $293.17 | 17.39% |

- **Probability-weighted: IV@15% $144.57 (−38.3% vs price), IV@12% $198.06 (−15.4%), IV@10% $258.60, weighted IRR 10.69%, base-case IRR 9.99%**
- **Tier by numbers: C.** Diagnostics (key_numbers.md): OE yield 4.52%, terminal value 22.1% of IV@15%, scenario spread 5.20x, net debt −0.69x normalized OE, 3.5 months since FY end.
- Even the bull case (25% weight) only reaches a 12.74% IRR at this price; only the 10%-weight super bull clears 15%. The price, not the business, is the problem.

## Flags — every fragility flag resolved
- **OE_VOLATILE** (OE/share range over the last 5 years spans >3x): the span is a trough artifact, not current cyclicality. FY2022 operating cash flow collapsed to $351,147,000 (from financials_history.csv) on a $600,756,000 working-capital build in the history file, taking FY2022 conservative OE to $151,055,000; OCF then recovered to $1,401,260,000 in FY2024 and $1,805,829,000 in FY2026, with conservative OE of $1,221,616,000 (FY2024), $1,570,062,000 (FY2025), and $1,545,196,000 (FY2026) — the last three years are stable at the high level, which is exactly the window the normalized median base uses. The recurring mask/resupply mix argues against treating the FY2022 supply-chain trough as the through-cycle level. Bear-or-worse outcomes still carry a combined 35% probability weight.
- **WIDE_SCENARIO_SPREAD** (super-bull IV 5.20x super-bear IV): real — the range is driven by how long ResMed can hold Philips-era share gains and keep expanding margins, which is genuinely uncertain over a 15-year fade. Confidence is held at medium (never high under this flag) and the verdict is sized to the conservative end: the weighted IV itself sits far below the price, so the spread does not rescue the valuation case.

## My thoughts / overlay
- Quality is not the debate: dominant share, recurring consumables, net cash of $1.070B (key_numbers.md), 5/5 OE-positive years, and a guided FY2027 of 12–14% core EPS growth with over $1.85B of planned capital returns. The debate is purely price: at $234.25 the market is already paying for the bull path, and the weighted case (10.69% IRR) lands in Tier C.
- GLP-1 risk is currently more narrative than numbers: the company's claims analysis (search results) shows patients on both GLP-1 and PAP therapy are ~11% more likely to start PAP and resupply at higher rates. The real dated risks are the Astral recall (FY2027 sales suspended, $42M Q4 FY2026 charge) and Philips' eventual US re-entry (analysts point to FY2028) — both are in the bear/super-bear cases, neither breaks the base.
- Method range: the defensible inputs here are narrow (normalized base = latest base, fresh FY, no data gaps), so there is no wide C-to-A method range to report — the spread is scenario spread, not method spread. On these inputs the tier is C under the weighted, base, bear, and bull cases alike; only the super bull clears the hurdle.
- Hurdle-clearing price: the weighted IV@15% is $144.57 — at or below roughly $145 the weighted case clears 15%. With a margin of safety against the bear case (IV@15% $94.16), a conservative buyer wants a price well under the weighted IV, not at it.

## Final verdict
- **Final tier: C** (weighted IRR 10.69% on the v5 final inputs; no tier override)
- Confidence: **Medium** (capped by WIDE_SCENARIO_SPREAD; data is complete and fresh, the uncertainty is competitive duration, not the numbers)
- One-liner: High-quality dominant CPAP franchise, moat 7/10, net cash — but at $234.25 it does not clear 15% (weighted IRR 10.7%, IV@15% $144.57); it clears 15% only at or below ~$145.
