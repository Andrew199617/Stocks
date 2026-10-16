# MKSI — MKS Inc.
v5 run, 2026-10-16. In scope (market cap $15.348B at $226.70, nasdaq_quote_api). All figures below are copied from key_numbers.md / dcf_numbers.json, ttm.py output, or financials_history.csv — none are recomputed. Q2 2026 quarterly figures are from the company's Q2 2026 earnings release / 10-Q summaries found in web research, as noted.

## What it is
Global supplier of enabling subsystems for semiconductor and advanced manufacturing: vacuum and gas delivery, RF power and plasma sources, photonics/lasers and motion control, plus specialty chemistry and plating for electronics & advanced packaging (the former Atotech business, acquired August 2022). It sells into three end markets — Semiconductor, Electronics & Packaging, and Specialty Industrial — so it is a picks-and-shovels supplier whose results ride its OEM and fab customers' capex cycles. Q2 2026 showed the upcycle clearly: revenue $1.248B, up 28% year-over-year with double-digit growth in all three end markets on AI-driven semiconductor and advanced-packaging demand, and management guided Q3 2026 revenue to $1.35B ± $40M (company release via web research).

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** revenue $3,931M; operating cash flow $645,000,000; capex $148,000,000; SBC $55,000,000 (always a real cost); net income $295,000,000; D&A $344,000,000.
- **Conservative owner's earnings FY2025: $442,000,000 = $6.53/share** (latest FY OE/share, key_numbers.md)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $605,000,000 — above the conservative figure, mainly because D&A includes heavy amortization of acquired Atotech intangibles while the cash business converts well. The conservative OCF-based figure is the one used throughout.
- OE positive 5 of the last 5 fiscal years, but the level is cyclical: conservative OE was $516,000,000 (FY2021), $320,000,000 (FY2022), $178,000,000 (FY2023), $362,000,000 (FY2024), $442,000,000 (FY2025) — the 2023 trough is the semiconductor downturn plus Atotech integration, not a broken business.
- Net debt $3,732,000,000 (dcf_numbers.json) — see HIGH_NET_DEBT under Flags; the equity is a levered claim on a cyclical OE stream.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $645,000,000 − prior YTD $306,000,000 + current YTD $296,000,000 = **TTM $635,000,000**
- Capex: FY $148,000,000 − prior YTD $47,000,000 + current YTD $79,000,000 = **TTM $180,000,000**
- SBC: FY $55,000,000 − prior YTD $34,000,000 + current YTD $34,000,000 = **TTM $55,000,000**
- Shares (current-YTD weighted diluted): **71,900,000**
- **TTM OE total $400,000,000 → base OE/share $5.56** (base_source: ttm_json)
- The engine's normalized base (median of last 3 FY OE/share) is $5.36/share — close to the TTM figure, so the base choice is not the swing factor here. The TTM base is used per the STALE_FY procedure, and it is the more conservative of the two in one respect that matters: TTM OE total ($400M) is *below* FY2025 ($442M) despite strong revenue growth, because capex ramped (capacity build-out) and the diluted share count rose. The latest-FY figure of $6.53/share flatters the current run-rate on both counts.

## Moat: 6/10 — moderate-strong, capped by cyclicality and the Atotech record
Justification: MKS's core subsystems are designed into fab tools and processes, where re-qualifying a supplier risks yield — real switching costs — and it holds leading share in several niches; but it sells to powerful OEM customers into a violently cyclical end market, and the 2023 impairments on the just-closed Atotech deal show the moat in parts of the portfolio was worth far less than the price paid.
- FOR: Design-in / qualification switching costs — RF power, vacuum, plasma and gas-delivery subsystems are qualified into OEM tools and fab processes over multi-year cycles; a swap risks process yield, so incumbency is sticky
- FOR: Leading positions in niches — at/near #1 share in RF power supplies, with strong vacuum and remote-plasma positions tied to etch/deposition complexity at advanced nodes
- FOR: Breadth and cross-sell — vacuum, photonics, motion and chemistry under one roof lets MKS sell tools plus the recurring chemistry and services that run on them
- FOR: Recurring chemistry/services mix (former Atotech) dampens pure equipment cyclicality and carries high attach rates on installed chemistry equipment
- AGAINST: Customer concentration and OEM pricing power — a concentrated set of large semiconductor-equipment customers and their fab customers set the capex cycle and squeeze suppliers in downturns
- AGAINST: Violent end-market cyclicality — FY2023 revenue stalled and OE fell to $178M; orders can reverse within quarters
- AGAINST: Atotech capital allocation — within a year of the August 2022 close, MKS recorded ~$1.3B of impairment in the Materials Solutions Division (former Atotech) plus ~$0.5B in Equipment Solutions in Q2 2023, with smaller additional charges in Q4 2023 (company releases); returns on the deal's invested capital have run below its cost
- AGAINST: Leverage — net debt is 9.9x normalized OE (diagnostics), so equity holders absorb the cycle amplified
- AGAINST: Specialist competition in every niche (RF power, lasers/photonics, vacuum) and OEM insourcing risk; no owned end-demand
- A 6 gives CAP = 9.8 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 9.8 years, 15-year projection. It does not score 7+ because a strong moat grade needs returns on capital proven through a cycle, and the post-Atotech record shows the opposite so far.

## DCF — v5 final run (2026-10-16)
Growth inputs: the engine's blended growth is 10.32% (components: revenue CAGR 5y 11.03%, 3y 3.48%, latest revenue YoY 9.62%, OE/share CAGR 2y 56.48% — the last is an inflection artifact off the impaired FY2023 base and the blend's median correctly gives it little weight), adjusted −4.16pp for the share-count trend, giving g_base 6.16%. Default offsets (−12/−5/0/+5/+12pp) and default OE multipliers (0.75/0.90/1.00/1.10/1.25) were kept. Probabilities were re-weighted bear-ward to 15/30/30/15/10 (from the 10/25/30/25/10 default) per the OE_VOLATILE flag instruction — this is a cyclical, levered name whose last downturn cut OE by roughly two-thirds from peak.
**Sanity check against recent prints (written reason for the super-bull start):** Q2 2026 revenue grew 28% year-over-year and Q3 is guided higher still, so the super-bull OE growth start of 18.16% sits below the latest *revenue* print. That is deliberate, for three filing-grounded reasons: (1) the scenario rates are OE/*share* growth, and TTM OE/share actually fell versus FY2025 ($5.56 vs $6.53) because capex ramped to a $180M TTM pace for capacity expansion and the diluted count rose to 71.9M; (2) the current revenue prints are a cyclical rebound off the depressed 2023–24 downturn base, the same base effect that makes the 56.48% OE/share CAGR component unusable at face value; (3) the verdict is insensitive to the choice — even the super-bull case (18.16% start, 1.25x OE) returns only 9.39% IRR at $226.70, so no defensible growth recalibration changes the tier. Price $226.70.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | -5.84% | 0.75 | Semi capex cycle rolls over; levered OE compresses hard | $23.62 | 3.63% |
| Bear | 30% | 1.16% | 0.90 | Upcycle fades early; growth near zero while debt service continues | $38.68 | 4.59% |
| Base | 30% | 6.16% | 1.00 | Blended historical growth, share dilution already deducted | $53.69 | 5.59% |
| Bull | 15% | 11.16% | 1.10 | AI/WFE upcycle extends through the CAP; deleveraging proceeds | $73.76 | 6.91% |
| Super bull | 10% | 18.16% | 1.25 | Multi-year AI capex supercycle, chemistry attach compounds | $114.21 | 9.39% |

- **Probability-weighted: IV@15% $53.74 (−76.29% vs price), IV@12% $71.85, IV@10% $92.11, weighted IRR 5.64%, base-case IRR 5.59%**
- **Tier by numbers: D.** Diagnostics (key_numbers.md): OE yield 2.45%, terminal value 19.41% of IV@15%, scenario spread 4.84x, net debt 9.91x normalized OE, 9.49 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.49 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, with all inputs quoted above. TTM OE/share ($5.56) sits between the 3-yr median ($5.36) and the latest FY ($6.53), so staleness is not flattering the result.
- **DILUTION** (share count +4.16%/yr): the step-up is acquisition-era, not SBC creep — diluted shares went 55,700,000 (FY2021) → 59,900,000 (FY2022) → 66,800,000 (FY2023) around the August 2022 Atotech close, then flattened at 67,600,000–67,700,000. SBC itself is modest and flat ($37M FY2021 → $55M FY2025; TTM $55M). The current-YTD diluted count of 71,900,000 is a fresh rise; the Q2 2026 report notes the $1,400M 1.25% convertible notes due 2030 became convertible and are classified as short-term debt, which is consistent with dilutive-securities inclusion at the higher share price. Either way, the engine already deducts the trend (−4.16pp growth adjustment) and the TTM base already charges the 71.9M denominator.
- **OE_VOLATILE** (OE/share range >3x over 5 years): real cyclicality, documented in the OE history above (FY2023 trough $178M in the downturn). Handled with the normalized/TTM base and by widening the bear weight to 45% on bear-or-worse (probabilities 15/30/30/15/10).
- **NI_OCF_DIVERGENCE** (2023, 2025): identified, and it does not contaminate the OCF-based base. 2023: net income −$1,841M vs OCF +$319M — the gap is the non-cash goodwill/intangible impairments (~$1.3B Materials Solutions / former Atotech and ~$0.5B Equipment Solutions in Q2 2023, plus ~$62M and ~$13M more in Q4 2023, per company releases) plus D&A of $397M; cash generation never went negative. 2025: net income $295M vs OCF $645M — the gap is mostly D&A of $344M, dominated by amortization of acquired intangibles. In both years the conservative OE series (OCF − capex − SBC) is the right one to trust, and it is what the engine uses.
- **WIDE_SCENARIO_SPREAD** (4.84x): real — outcomes for a levered cyclical at the top of an upcycle genuinely span this wide. Confidence is set to low (below the medium cap this flag imposes) given the leverage and cyclicality on top of the spread.
- **HIGH_NET_DEBT** (net debt 9.91x normalized OE): folded into the verdict explicitly. Net debt is $3,732,000,000 against FY2025 cash of $418,000,000 and long-term debt of $4,150,000,000 (financials_history.csv). Management is deleveraging — Q2 2026 reporting shows total debt carried at $4,023M at June 30, 2026, down from $4,278M at December 31, 2025, after issuing €1,000M of 4.25% notes due 2034 and prepaying $1,274M of the USD Term Loan B, with the company citing a 3.0x net leverage ratio on its EBITDA definition (a much larger denominator than normalized OE — both figures are quoted as reported; the OE-based multiple is the conservative one for equity holders). The bear cases (45% combined weight) are exactly the cases where this leverage bites, and they carry IV@15% of $23.62–$38.68 against a $226.70 price.

## My thoughts / overlay
- This is not a quality dispute: MKS is a real, entrenched supplier in an AI-driven upcycle, currently printing 28% revenue growth with guidance for more. The dispute is purely price versus owner's earnings. On the filing-derived TTM base of $5.56/share, the OE yield at $226.70 is 2.45% — the market is pricing in years of flawless cyclical compounding plus successful deleveraging, and paying for it today.
- The method range does not rescue the price: the preliminary run on the median base ($5.36/share, default probabilities) produced a weighted IRR of 5.69%, and even this run's super-bull scenario — 18.16% growth start at 1.25x OE — yields only 9.39% IRR. Every defensible input set lands in Tier D; there is no C-to-A-style spread to report here, the spread is D-to-D.
- What would have to be true: OE/share would need to roughly quadruple from the TTM base on a sustained basis for $226.70 to clear a 15% hurdle. The price that clears 15% on the weighted case is the weighted IV@15% itself: **$53.74**. Even the super-bull IV@15% is $114.21 — about half the current price.
- Balance-sheet trajectory is the one genuinely improving variable (steady prepayments, refinancing termed out to 2034), and it reduces the left tail over time; it does not close a 76% valuation gap.

## Final verdict
- **Final tier: D** (weighted IRR 5.64% on the v5 final inputs; tier matches tier_by_numbers, no override)
- Confidence: **Low** (wide scenario spread 4.84x, net debt 9.91x normalized OE, and a cyclical OE stream at a cyclical-peak print — direction of the verdict is not in doubt, but no single number here deserves precision)
- One-liner: Entrenched semi-equipment subsystem supplier, moat 6/10, in a strong AI upcycle — but at $226.70 the weighted IRR is only 5.64% (IV@15% $53.74); it clears Andrew's 15% hurdle only at ~$54, and even the super-bull case doesn't reach a 10% IRR at this price.
