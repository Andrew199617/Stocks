# SANM — Sanmina Corporation
Engine 5.4.0 run, 2026-10-18. In scope (market cap $9.693B at $175.67, nasdaq_quote_api).

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.json or fundamentals.json — none are recomputed. Deal and guidance facts are from cited search results (earnings-call coverage of Q4 FY25, Q2 FY26 and Q3 FY26).

## What it is
Electronics manufacturing services (EMS): integrated manufacturing (assembly, test, supply chain) plus vertically integrated components — PCBs, backplanes, optical transceivers, enclosures, and now energy products. End markets: industrial/energy/medical/defense/aerospace/auto (62% of FY2025 revenue) and communications networks + cloud/AI infrastructure (38%). On 2025-10-27 it closed the acquisition of ZT Systems' manufacturing business from AMD for an estimated $2.05B (AMD took 1.15M shares as part consideration) — rack-scale AI server integration at a $5–6B annual revenue run rate. That deal is a basis break: FY2025 revenue was $8.13B; FY2026 is guided to $14.0–$14.3B and management guides to >$16B in FY2027. Everything filed before the close describes a different, smaller company.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $620,657,000; capex $147,357,000; SBC $63,396,000 (always a real cost).
- **Conservative owner's earnings FY2025: $409,904,000 = $7.43/share** (key_numbers.md: latest FY OE/share $7.43; latest FY OE total $409.9M)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $432,607,000 — same ballpark, which corroborates the FY2025 level (see NI_OCF_DIVERGENCE below).
- OE positive 4 of the last 5 fiscal years — the exception is FY2023 at −$0.11/share, a working-capital build year (ΔNWC +$297,780,000) on peak revenue of $8.94B. That year is the standing proof that this OE series can go to zero when growth absorbs working capital.
- Balance sheet (latest filed FY): net debt −$625.8M, i.e. net cash (key_numbers.md); leases $57,747,000. Net debt / normalized OE −1.24x (key_numbers.md). The cash pile is real but modest next to the $175.67 price — it does not rescue the valuation.

**Base used = TTM owner's earnings through Q3 FY2026 (2026-06-27), from ttm.py (filing-direct, no hand math):**
- OCF: FY $620,657,000 − prior YTD $421,578,000 + current YTD $701,977,000 = **TTM $901,056,000**
- Capex: FY $147,357,000 − prior YTD $84,890,000 + current YTD $244,441,000 = **TTM $306,908,000** (the step-up is the ZT capacity build-out — liquid cooling, automation, power infrastructure)
- SBC: FY $63,396,000 − prior YTD $47,163,000 + current YTD $72,502,000 = **TTM $88,735,000**
- Shares (current-YTD weighted diluted): **55,254,000**
- **TTM OE total $505,413,000 → base OE/share $9.15** (base_source: ttm_json; fundamentals.json TTM agrees: OE/share $9.16 on TTM revenue $12,763,372,000, revenue YoY +58.56%)
- Why TTM and not the alternatives: the engine's normalized base (3-yr median) is $3.01/share — it is struck on the pre-ZT company and includes the FY2023 WC-build trough, so it values a business that no longer exists. Latest FY $7.43 is also pre-ZT in scale. The TTM base is the only one measured on the current company. Its own flattery — a working-capital release tailwind (see below) and peak AI-cycle demand — is handled in the scenarios (45% weight on bear-or-worse, bear OE multipliers of 0.50/0.80), not by reverting to a stale median.

## Moat: 4/10 — weak
Justification: mid-teens ROIC through a cycle and sticky complex/regulated programs plus ZT rack-scale integration, but 8–9% gross margins, no pricing power, re-biddable programs and rising hyperscaler concentration cap it.
- Evidence (fundamentals.json): ROIC proxy FY2021–FY2025 = 14.8% / 17.0% / 18.2% / 12.2% / 14.5% — above the cost of capital through a cycle that included a −15.3% revenue year (FY2024). Gross margin FY2021–FY2025 = 7.8% / 7.9% / 8.3% / 8.5% / 8.8%, TTM 9.0% — improving, but from a structurally thin EMS base; operating margin runs ~4–5%. The ROIC is a working-capital/asset-turn story, not a pricing-power story, which is why the score stops at 4 despite the returns history.
- FOR: ROIC proxy mid-teens through a cycle on an asset-light, working-capital-disciplined model; vertically integrated components plus design/NPI services raise switching friction vs pure assembly rivals; qualified, sticky programs in regulated markets (medical, defense, industrial/energy = 62% of FY2025 revenue); ZT adds rack-scale AI integration and preferred-manufacturer status with AMD, and the US/Mexico footprint suits defense and reshoring demand.
- AGAINST: structurally thin economics (gross margin 7.8–8.8%, operating margin ~4–5%) — cost pass-through, no real pricing power; programs are re-biddable and insourceable, with Jabil, Flex and Celestica offering near-identical capabilities at greater scale; customer concentration (top 10 = 51.7% of FY2025 revenue pre-ZT, concentrating further into a few hyperscale/AI programs post-ZT); ZT revenue is lumpy and platform-dependent (Q2 FY26 $1.88B vs Q3 FY26 $1.1B) and rides the NVIDIA-to-AMD platform transition; working capital absorbs cash exactly when growth accelerates (FY2023 OE/share −$0.11).
- A 4 gives CAP = 7.2 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 7.2 years, 15-year projection.

## DCF — engine 5.4.0 final run (2026-10-18)
Growth sanity check (mandatory): the headline recent prints are acquisition arithmetic, not organic growth — TTM revenue YoY +58.56% and Q3 FY26 revenue +69.7% YoY are ZT consolidation. The organic evidence: core Sanmina guided to high-single-digit growth for FY2026 with its cloud/AI segment growing 20%+ for six straight quarters (component shortages capped shipments); FY2027 total revenue guided >$16B vs the FY2026 guide of $14.0–$14.3B, i.e. ~+13–14% for one more year, decelerating thereafter; the engine's own pre-deal blend (rev CAGR 5y 3.19%, 3y 0.87%, latest FY YoY 7.40%) is 7.59%. The base start of 7.6% therefore sits *below* the latest prints with a written reason: the prints annualize an acquisition and a peak AI capex cycle, while through-cycle EMS growth is mid-single digits. Bull 12.6% ≈ the FY2027 guide pace sustained — that is the right place for it. Super-bull 19.6% requires a multi-year hyperscaler boom with no digestion year; it gets 8%.

Scenario adjustments vs defaults, with reasons: probabilities moved to 15/30/30/17/8 (OE_VOLATILE instruction — widen bear weight — plus a cyclically flattering TTM base); super-bear OE multiplier cut to 0.50 and bear to 0.80 because in a WC-build/digestion year this company has printed OE/share of −$0.11 (FY2023) and $3.01 (FY2024) — a 0.75 super-bear multiplier on a peak-flattered TTM base understates the demonstrated downside. Offsets left at defaults (−12/−5/0/+5/+12pp). Price $175.67.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | −4.4% | 0.50 | AI capex digestion + WC rebuild; OE/share halves toward FY23–24 experience | $28.68 | 4.41% |
| Bear | 30% | 2.6% | 0.80 | ZT run rate fades, core grows low-single digits; OE normalizes ex-WC-release | $60.21 | 6.79% |
| Base | 30% | 7.6% | 1.00 | TTM OE holds; blended through-cycle growth over the 7.2-yr CAP | $91.10 | 9.13% |
| Bull | 17% | 12.6% | 1.10 | FY27 guide pace ($16B+) sustains; margin mix keeps improving | $120.95 | 11.33% |
| Super bull | 8% | 19.6% | 1.25 | Multi-year hyperscaler boom, ZT + core both compounding | $177.98 | 15.15% |

- **Probability-weighted: IV@15% $84.50 (−51.9% vs price), IV@12% $112.65, IV@10% $144.08, weighted IRR 8.69%, base-case IRR 9.13%**
- **Tier by numbers: D.** Bear tier D (6.79%), bull tier C (11.33%). Diagnostics (key_numbers.md): OE yield 5.21%, terminal value 19.0% of IV@15%, scenario spread 6.21x, net debt −1.24x normalized OE, 12.7 months since FY end.
- Hurdle-clearing prices (weighted path): 15% at $84.50 · 20% at $59.23 · 25% at $45.36. Even the super-bull case (IV@15 $177.98, IRR 15.15%) only just reaches today's price — the market is pricing the tail as the base case. Note the gap to non-GAAP optics: FY2026 non-GAAP EPS is guided at $11.90–$12.20, but that excludes SBC ($88,735,000 TTM ≈ $1.61/share) and carries none of the $306,908,000 TTM capex burden the OE definition charges.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 12.7 months ago): resolved by construction — the base is the TTM figure from ttm.py through 2026-06-27, legs quoted above.
- **BASE_DIVERGENCE** (latest FY $7.43 vs 3-yr median $3.01): *both* are distorted. The median is struck on the pre-ZT company and includes the FY2023 WC-build trough (−$0.11/share); the latest FY is pre-ZT in scale but WC-flattered in cash. Neither describes the current company; the TTM base ($9.15) does, and its flattery is priced via bear-weighted scenarios rather than by picking a stale base.
- **NI_OCF_DIVERGENCE** (FY2025 net income $245,893,000 vs OCF $620,657,000): the gap is non-cash charges plus a working-capital release — D&A $119,466,000 and SBC $63,396,000 are added back in OCF, and ΔNWC was −$186,714,000 (the FY2023–24 inventory/receivables build unwound). Cross-check: the NI-based maintenance OE ($432,607,000) lands within ~6% of the OCF-based conservative OE ($409,904,000), so the FY2025 OE level is corroborated, not fabricated. The caution runs the other way: a WC release is a one-time tailwind — Q3 FY2026 OCF was only $124M on $3.46B of revenue as the ZT ramp rebuilt working capital (fundamentals.json quarterly).
- **OE_VOLATILE** (OE/share spans >3x over 5 years): real and structural — FY2023 −$0.11, FY2024 $3.01, FY2025 $7.43, TTM $9.15. It is working-capital cyclicality on thin margins, not an inflection to a new stable level. Handled with 45% bear-or-worse weight and sub-1.0 bear multipliers (0.50/0.80).
- **BUYBACK_TAILWIND** (share count −4.40%/yr): already credited via the growth adjustment in the blend; not double-counted. Note the recent count is roughly flat — diluted shares 55,178,000 (FY2025) vs 55,254,000 TTM — because buybacks (1.1M shares for $160M in Q2 FY26 per earnings coverage) are offset by the 1.15M shares issued to AMD for ZT.
- **WIDE_SCENARIO_SPREAD** (6.21x): real — the outcome hinges on whether AI rack demand digests or compounds, which nobody can call tightly today. Confidence is low, and the verdict is sized to the bear end.
- **TIER_BAND** (bear D 6.79% vs bull C 11.33%): the whole band sits below the 15% hurdle; sized to the bear end per the flag. No tier override — the numbers' D is the verdict on every base except the 8% super-bull tail.

## My thoughts / overlay
- The honest headline is the *method range*: on the engine's stale median base the preliminary run printed weighted IRR 5.00% / IV@15 $32.64 (Tier D); on the TTM base with default scenarios, 9.57% / $96.60 (Tier D); on the final bear-weighted TTM run, 8.69% / $84.50 (Tier D). The tier never moves — only how bad the overvaluation is. Anyone quoting a SANM value near the $175.67 price is capitalizing non-GAAP EPS and assuming the AI ramp never digests.
- The business genuinely improved: ZT integration is ahead of plan per Q3 FY26 coverage, non-GAAP operating margin hit 8.0% in Q3 FY26 vs 5.7% a year earlier, GAAP gross margin printed 10.5% in Q3 FY26 (fundamentals.json), and the balance sheet carries net cash. None of that is the debate. The debate is price: at $175.67 the buyer pays ~19x TTM owner's earnings for a 4/10-moat EMS whose cash earnings went to zero the last time working capital built.
- Watch items for pass 2: ZT quarterly revenue lumpiness and the NVIDIA→AMD platform transition; component shortages (memory, custom ASICs) that capped Q2–Q3 shipments; whether TTM capex ($306,908,000) falls back once the capacity build ends, which would mechanically lift OE; post-deal customer concentration in the FY2026 10-K.

## Final verdict
- **Final tier: D** (weighted IRR 8.69% on the final TTM-base inputs; bear D → bull C, super-bull tail 15.15%)
- Confidence: **Low** (6.21x scenario spread, first post-acquisition year, WC-driven OE series)
- One-liner: Real but thin-moat EMS cash generator, moat 4/10, transformed by ZT Systems — even on a cyclically flattering TTM base of $9.15/sh the weighted IRR is only 8.7% at $175.67; it clears 15% only below ~$85.
