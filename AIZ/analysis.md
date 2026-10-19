# AIZ — Assurant, Inc.
Pass-1 run, 2026-10-17. Engine release 5.4.0. Price $283.31 (nasdaq_quote_api), market cap $14.473B — in scope under $40B.

All figures below are copied from dcf_numbers.json, ttm.json, financials_history.csv or fundamentals.json — none are recomputed.

## What it is
Specialty insurer / protection-services company (SIC 6399, Insurance Carriers NEC) selling embedded protection through partners rather than direct to consumers, in two segments: **Global Lifestyle** (mobile-device protection, trade-in and repair, extended service contracts for electronics/appliances, vehicle protection) and **Global Housing** (lender-placed homeowners insurance, manufactured housing, flood, renters). Q2 2026: revenue $3,454.2M (+9.4% YoY per the earnings release), GAAP net income $298.6M (+27% YoY), Adjusted EBITDA ex-catastrophes $491.4M (+18% YoY) — the beat was helped by unusually light reportable catastrophes ($12.2M in Q2 2026; $36.6M for 6M 2026 vs $186.8M for 6M 2025). Management raised the 2026 outlook on 2026-08-04: mid-single-digit growth in Adjusted EBITDA and adjusted EPS ex-catastrophes, ~10% on an underlying basis excluding the headwind from lower favorable prior-year reserve development, with Global Lifestyle guided to low-double-digit Adjusted EBITDA growth and buybacks toward the upper end of a $300–350M range.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $1,833,900,000; capex $235,500,000; SBC $85,700,000.
- **Conservative owner's earnings FY2025: $1,512,700,000 = $29.61/share** (base_oe_latest_per_share $29.61 in dcf_numbers.json)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $887,200,000 — far below the conservative figure. That gap is the central fact about this name: for an insurer, OCF includes premiums and reserve/float growth collected ahead of claims, so the OCF-based definition overstates distributable owner's earnings. Net income FY2025 was $872,700,000, close to the maintenance figure, not to the conservative one.
- OE positive 5 of the last 5 fiscal years, but the path is volatile: OE/share $8.78 (2021), $6.35 (2022), $16.18 (2023), $19.79 (2024), $29.61 (2025) — catastrophe years and reserve development move it by multiples.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $1,833,900,000 − prior YTD $657,900,000 + current YTD $694,700,000 = **TTM $1,870,700,000**
- Capex: FY $235,500,000 − prior YTD $113,300,000 + current YTD $92,900,000 = **TTM $215,100,000**
- SBC: FY $85,700,000 − prior YTD $37,500,000 + current YTD $43,400,000 = **TTM $91,600,000**
- Shares (current-YTD weighted diluted): **50,082,767**
- **TTM OE total $1,564,000,000 → base OE/share $31.23** (base_source: ttm_json)
- Caveat on the TTM base: H1 2026 was a light-catastrophe half (reportable cats $36.6M vs $186.8M in H1 2025), so the TTM OE is flattered relative to a through-cycle year. Handled by the heavier bear-side probabilities (45% on super bear + bear) and by the tier softening below, not by changing the filing-derived base.
- The engine's normalized base (3-yr median) is $19.79/share — see BASE_DIVERGENCE under Flags.

## Moat: 5/10 — moderate/narrow
Justification: Embedded B2B2C partnerships and program-integration switching costs in device protection and lender-placed insurance, but partners are large, concentrated and can rebid or in-source, there is no direct consumer relationship, and returns are mid-teens ROE with a weak year in the last five — not a wide-moat compounder.
- FOR: Embedded distribution — protection is sold inside carrier, retailer, auto-dealer and lender channels under multi-year programs, with Assurant's systems integrated into the partner's point of sale and claims flow; real switching friction at renewal. Scale repair / trade-in / claims platform in Connected Living (Q2 2026 Connected Living Adjusted EBITDA +29% YoY on new and expanded programs). Leading lender-placed position — placement is automatic when a borrower's coverage lapses, a countercyclical, captive-demand niche with inflation-guard pricing. Growing fee-based mix (fees and other income +19.6% YoY in Q2 2026) that is less cat-exposed than underwriting.
- AGAINST: Partner concentration — a small number of large carriers/retailers/lenders control distribution and can rebid programs, squeeze economics, or move to competitors (Asurion, Likewize, carrier in-house programs). No owned consumer brand or direct relationship — the end customer is the partner's. Lender-placed insurance is politically and regulatorily exposed and countercyclical to mortgage health. Global Housing carries real catastrophe tail risk. Returns do not show wide-moat pricing power: ROE (fundamentals.json) was 6.5% in 2022, 13.4% in 2023, 14.9% in 2024 and 14.9% in 2025.
- Evidence note: fundamentals.json carries no `roic_proxy` series and no gross margin for AIZ — the insurer presentation files no operating-income/gross-profit lines the proxy needs — so the moat is evidenced on ROE (above) instead. A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — final run (2026-10-17)
Growth sanity check and recalibration (written reason): the engine's blended growth is 10.21%, but its components mix unlike things — revenue CAGR 5y 5.95%, 3y 7.93%, latest revenue YoY +7.89% (FY2025; TTM revenue YoY +9.36% and Q2 2026 revenue +9.4% in the release) against an OE/share CAGR of 35.27% that is an artifact of the depressed 2023 base and the light-cat TTM, not a growth rate. Management's raised 2026 guide is mid-single-digit Adjusted EBITDA/EPS growth ex-cat (~10% underlying before the reserve-development headwind). Scenario starts were therefore set via offsets (−0.12 / −0.082 / −0.032 / +0.008 / +0.058 vs g_base) to −1.79% / 2.01% / **7.01%** / 11.01% / 16.01% — the base start sits between the headline guide and the ~10% underlying guide, with buybacks (−2.3%/yr share count) supporting per-share growth; no start exceeds what the underlying guide plus buybacks can explain except super bull, which is priced as the low-probability case it is. Probabilities skewed bear-side to 15/30/30/20/5 for catastrophe/reserve mean-reversion off a light-cat TTM base; OE multipliers are the defaults 0.75/0.90/1.00/1.10/1.25. Price $283.31.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | -1.79% | 0.75 | Cat-heavy year(s), adverse reserve development, a major program loss | $160.53 | 9.41% |
| Bear | 30% | 2.01% | 0.90 | Cats normalize upward from the light H1 2026, growth at/below guide | $225.78 | 12.45% |
| Base | 30% | 7.01% | 1.00 | Guide delivered: mid-single-digit headline, ~10% underlying, buybacks continue | $308.76 | 16.07% |
| Bull | 20% | 11.01% | 1.10 | Lifestyle low-double-digit growth sustains, cats stay benign | $400.50 | 19.67% |
| Super bull | 5% | 16.01% | 1.25 | Multi-year benign cats plus program wins compound | $558.25 | 25.08% |

- **Probability-weighted: IV@15% $292.45 (+3.2% vs price), IV@12% $389.30, IV@10% $497.40, IV@20% $205.54, IV@25% $157.77, weighted IRR 15.39%, base-case IRR 16.07%**
- **Tier by numbers: B** (bear tier C at 12.45%, bull tier B at 19.67%). Diagnostics (dcf_numbers.json): OE yield 11.02%, terminal value 18.9% of IV@15%, scenario spread 3.48x, 9.5 months since FY end.
- **Final tier: C — softened one notch from B by tier_override** (see SECTOR_MODEL_MISMATCH / NI_OCF_DIVERGENCE below and the standing insurer rule).

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.5 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, quoted above.
- **BUYBACK_TAILWIND** (share count −2.3%/yr): already credited via the growth adjustment in the blend; not double-counted. Corroborated by fundamentals.json buybacks TTM $377,900,000 and the raised 2026 repurchase guide ($300–350M, toward the upper end).
- **OE_VOLATILE** (OE/share spans >3x over 5 years): real — $6.35 (2022) to $29.61 (2025), driven by catastrophe load and reserve development, not operating leverage alone. Handled by bear-side probability weight (45% super bear + bear) and the softened final tier.
- **NI_OCF_DIVERGENCE** (2023, 2024, 2025): structural, not a one-off — OCF vs net income was $1,138,100,000 vs $642,500,000 (2023), $1,332,700,000 vs $760,200,000 (2024) and $1,833,900,000 vs $872,700,000 (2025) (financials_history.csv). An insurer collects premiums and builds reserves ahead of claims, so OCF systematically exceeds earnings; the maintenance OE ($887,200,000 FY2025) sits next to net income, the conservative OE ($1,512,700,000) does not. This is the float-capitalization artifact behind the tier softening.
- **DEBT_TAGS_BLANK** (no debt tag for the latest FY — engine net debt UNKNOWN, not zero): balance sheet from the filing record instead — the company's Q1 2026 financial supplement reports debt of $2,206.9M and total stockholders' equity of $5,871.6M at 2025-12-31 (debt-to-total-capital 27.3%; equity matches fundamentals.json FY2025 equity $5,871,600,000), against cash of $1,834,100,000 at FY2025 (financials_history.csv). Leverage is modest for an insurer; the engine simply cannot see the debt tag, so no leverage figure from the engine is quoted anywhere here.
- **SECTOR_MODEL_MISMATCH** (Finance sector): insurer — the OE/capex DCF fits poorly, confidence is **low**, and per Andrew's standing insurer rule (2026-10-15; same treatment as PFG/HIG/ACGL/WRB) the final tier is softened one notch, B → C, because the OCF-based base capitalizes float/reserve growth (see NI_OCF_DIVERGENCE). The numbers do not win.
- **BASE_DIVERGENCE** (latest FY $29.61 vs 3-yr median $19.79): the median is the distorted one as a *level* — it is the middle value of a steeply rising series ($16.18 / $19.79 / $29.61), not a stable through-cycle level, and the latest FY is corroborated by the TTM base ($31.23). The TTM base is used; the counter-risk (the TTM embeds a light-cat half) is handled in probabilities and the tier softening rather than by reverting to a stale median. Method range: on the median base the preliminary run printed weighted IRR 13.19% (Tier C) — the same final tier the softening lands on.
- **TIER_BAND** (bear C 12.45% vs bull B 19.67%): the verdict spans tiers; any position is sized to the bear end — which is Tier C, the same as the softened final tier.

## My thoughts / overlay
- The honest headline is the method range, not the B: median base → 13.19% (C); TTM base → 15.39% (B by numbers); float-adjusted judgment → C. Two of the three defensible reads are C, and the B read rests on an OCF base that counts float as owner's earnings in a light-catastrophe period.
- Quality is real but ordinary for a specialty insurer: OE positive 5/5 years, revenue growing 8–9%, ROE mid-teens, disciplined buybacks, modest holding-company leverage (27.3% debt-to-capital per the supplement). None of that makes the OCF base distributable.
- Risks: catastrophe normalization (H1 2026 cats were $36.6M vs $186.8M a year earlier — that tailwind reverses), reserve development turning adverse after years of favorable development, loss or repricing of a major carrier/retailer program, regulatory pressure on lender-placed pricing, and housing/mortgage-cycle exposure in Global Housing.
- Hurdle math on the numbers run: the weighted IV@15% of $292.45 sits only 3.2% above the $283.31 price — there is no margin of safety in the weighted case, and the bear-case IV@15% ($225.78) sits well below price. A buyer at $283 is paid only if cats stay benign and the float-flattered base is treated as real.

## Final verdict
- **Final tier: C** (tier by numbers B at weighted IRR 15.39%, softened one notch for the insurer-float artifact; bear case is also C at 12.45%)
- Confidence: **Low** (sector model mismatch on an insurer; NI_OCF_DIVERGENCE is structural)
- One-liner: Specialty insurer with embedded partner distribution, moat 5/10 — B by numbers on a TTM base (15.4% weighted, IV@15 $292 vs $283) but the OCF base capitalizes float in a light-cat period, so softened to C at low confidence; it does not cleanly clear 15% until the bear case (12.5%) is covered.
