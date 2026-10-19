# ALLE — Allegion plc
Engine 5.4.0 run, 2026-10-17. In scope: market cap $13,556,364,000 at $156.54 (nasdaq_quote_api, dcf_numbers.json).

All figures below are copied from dcf_numbers.json, ttm.json, financials_history.csv, or fundamentals.json — none are recomputed.

## What it is
Dublin-based security-products company spun out of Ingersoll Rand: Schlage locks, Von Duprin exit devices, LCN closers and electronic access control, sold mainly through specification into North American non-residential buildings (education, healthcare, government, hospitality, retail) plus premium residential. Two segments in substance: Americas (the profit engine) and International (weaker — organic revenue fell in Q2 2026).

## Owner's earnings
**FY2025 (10-K via EDGAR, financials_history.csv):** operating cash flow $783,800,000; capex $98,100,000; SBC $29,800,000 (always a real cost, and small here — about 4% of OCF).
- **Conservative owner's earnings FY2025: $655,900,000 = $7.573903002309469/share** (base_oe_latest_per_share, dcf_numbers.json)
- Maintenance version (financials_history.csv): $638,500,000 — same ballpark, which raises confidence.
- OE positive 5 of the last 5 fiscal years. Net debt $1,623,900,000 (LongTermDebtNoncurrent+DebtCurrent basis, dcf_numbers.json), lease liabilities $170,200,000; diagnostics put net debt at 2.526185576599305x normalized OE.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $783,800,000 − prior YTD $314,200,000 + current YTD $299,700,000 = **TTM $769,300,000**
- Capex: FY $98,100,000 − prior YTD $38,800,000 + current YTD $38,900,000 = **TTM $98,200,000**
- SBC: FY $29,800,000 − prior YTD $16,800,000 + current YTD $17,500,000 = **TTM $30,500,000**
- Shares (current-YTD weighted diluted): **86,300,000**
- **TTM OE total $640,600,000 → base OE/share $7.422943221320973** (base_source: ttm_json)
- The engine's normalized base (median of last 3 FY OE/share) is $6.332191780821918/share — reported, not used: it averages in the weaker FY2023 year and is stale against both FY2025 ($7.57) and the TTM print ($7.42). The TTM base sits between the median and the latest FY, so it is not the aggressive choice.

## Moat: 6/10 — moderate-strong, not wide
Justification: spec-driven security hardware leader (Schlage, Von Duprin, LCN) with trusted brands, code/specification placement in commercial buildings, installed-base and professional-channel stickiness, and proven pricing power — capped at 6 because ASSA ABLOY is larger globally, mechanical hardware faces smart-lock/biometric substitution, and growth is tied to cyclical non-residential construction.
- FOR: Schlage / Von Duprin / LCN brands specified into commercial buildings — spec placement and code compliance create installed-base stickiness; ROIC and margin evidence below; professional/institutional channel and trusted-brand position in North American commercial and premium residential locks; electronic access control growth and recurring specification/replacement demand.
- AGAINST: ASSA ABLOY is the larger global rival, with Spectrum/Kwikset, dormakaba and smart-lock tech entrants contesting every category; smart locks, mobile credentials and biometrics can commoditize or bypass mechanical hardware; demand is tied to cyclical non-residential construction and International organic revenue fell 1.2% in Q2 2026; the FY2026 organic growth guide is only 3.5–4.5% — reported growth leans on acquisitions, pricing and FX.
- Evidence (fundamentals.json): roic_proxy was 19.5% (2020), 27.1% (2021), 19.0% (2022), 21.7% (2023), 22.3% (2024), 19.5% (2025) — well above the cost of capital through the cycle. Gross margin: 43.3% (2020), 42.0% (2021), 40.4% (2022), 43.3% (2023), 44.2% (2024), 45.2% (2025) — expanding, consistent with the pricing actions management described in Q2 2026.
- A 6 gives CAP = 9.8 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 9.8 years, 15-year projection.

## DCF — final run (engine 5.4.0)
Growth sanity check: the engine's blended start is 8.748% (rev CAGR 5y 8.38%, 3y 7.52%, latest FY YoY 7.82%, OE/share CAGR 2y 16.81%). Recent prints: Q2 2026 reported revenue +12.7% YoY with Americas organic +8.9% and International organic −1.2% (search results, Zacks/StockTitan Q2 summary); FY2026 guidance raised to reported growth 7.5–8.5% and organic 3.5–4.5%. The base start (8.75%) sits slightly above the reported guide because OE/share growth also carries pricing, mix, acquisitions and a shrinking share count (share CAGR −0.65%/yr, credited in the blend) — written reason for a base start modestly above the organic guide. The bull start (13.75%) is roughly the Q2 reported print sustained; the super-bull start (20.75%) has no print behind it and is treated as a 10%-weighted tail requiring sustained double-digit reported growth plus acquisition contribution, not as a forecast. Probabilities 10/25/30/25/10; OE multipliers 0.75/0.90/1.00/1.10/1.25 (defaults — the business is steady enough that no company-specific reweighting was justified). Price $156.54.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -3.25% | 0.75 | Non-res downturn, International worsens, pricing reverses | $35.35 | 5.10% |
| Bear | 25% | 3.75% | 0.90 | Organic guide low end only, no acquisition help | $57.91 | 7.18% |
| Base | 30% | 8.75% | 1.00 | Reported guide delivered, pricing + mix + buybacks carry OE/share | $80.38 | 9.18% |
| Bull | 25% | 13.75% | 1.10 | Q2 reported pace sustains, electronics/access control mix lifts margins | $110.37 | 11.65% |
| Super bull | 10% | 20.75% | 1.25 | Tail: sustained double-digit reported growth plus M&A | $170.73 | 15.93% |

- **Probability-weighted: IV@15% $86.79 (−44.56% vs price), IV@12% $117.25, IV@10% $151.48, weighted IRR 9.77%, base-case IRR 9.18%**
- **Tier by numbers: D.** Diagnostics (dcf_numbers.json): OE yield 4.74%, terminal value 20.48% of IV@15%, scenario spread 4.83x, net debt 2.53x normalized OE, 9.53 months since FY end.
- Hurdle prices (dcf_numbers.json): clears 15% at $86.79, 20% at $59.76, 25% at $45.13 — all far below the $156.54 price.

## Flags — every fragility flag resolved
- **STALE_FY** (latest fiscal year ended 10 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, legs quoted above. TTM OE/share $7.42 sits below the latest FY $7.57, so the TTM base is not flattering the result.
- **WIDE_SCENARIO_SPREAD** (super-bull IV 4.83x super-bear IV): real — it is driven by the deliberately stretched super-bull growth start, which has no recent print behind it. Confidence is capped at medium (not high), and the verdict is sized to the conservative end: even the bull case (11.65% IRR) does not clear 15%.
- **TIER_BAND** (bear tier D at 7.18% vs bull tier C at 11.65%): the verdict spans D–C and is sized to the bear end — final tier D. No scenario except the 10%-weighted super-bull tail clears the 15% hurdle.

## Thoughts / method range
- Quality is not the debate: OE positive 5/5 years, SBC only ~$30.5M TTM against $769.3M TTM OCF, steady buybacks (share count falling), ROIC ~20%+ and gross margin at a decade high. This is a good business at a full price.
- Method range: on the engine's normalized median base ($6.33/share) the preliminary default run printed weighted IRR 8.54% and IV@15% $71.97 — also Tier D. The TTM base lifts the answer to 9.77% / $86.79, still D. The tier does not depend on the base choice.
- The Q2 2026 print was genuinely strong (reported revenue +12.7%, adjusted EPS $2.40, guidance raised), but the growth the market is paying for at $156.54 (≈21x TTM OE/share on the figures above) requires the bull/super-bull path to become the base case.
- Balance sheet is manageable, not a flag beyond the diagnostics: net debt $1,623,900,000 plus $170,200,000 of lease liabilities against $640,600,000 of TTM OE.

## Final verdict
- **Final tier: D** (weighted IRR 9.77% on the TTM base; bear-to-bull band D to C)
- Confidence: **Medium** (high on OE quality and the filing-derived TTM base; the scenario spread is 4.83x, so no single growth path deserves high confidence)
- One-liner: High-quality security-hardware compounder, moat 6/10 — but at $156.54 it does not clear 15%: weighted IRR 9.8%, weighted IV@15 $86.79 vs $156.54, bear-to-bull tier D to C; clears 15% only below ~$86.79.
