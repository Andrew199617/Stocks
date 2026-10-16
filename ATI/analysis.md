# ATI — ATI Inc.
v5 run, 2026-10-15. Market cap $26.636B at $187.84 (nasdaq_quote_api) — in scope (<$40B). All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.py output, or financials_history.csv — none are recomputed.

## What it is
Specialty materials producer for aerospace & defense (~68-70% of sales): nickel-based superalloys, titanium, isothermal forgings, and high-purity hafnium/zirconium for jet engines, airframes, and naval nuclear propulsion. Two segments — High Performance Materials & Components and Advanced Alloys & Solutions. Q2 2026: sales $1.26B (+11% YoY), adjusted EBITDA $284M (+37%, 22.6% margin), record backlog $4.4B (+18% YoY); management raised FY2026 guidance to adjusted EBITDA $1.135-1.185B, adjusted EPS $4.90-5.18, adjusted FCF $550-600M.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** revenue $4,587.4M; net income $404.3M; operating cash flow $614.3M; capex $280.6M (tag: PaymentsToAcquireProductiveAssets); SBC $29.0M (a real cost, but small here).
- **Conservative owner's earnings FY2025: $304.7M = $2.15/share** (latest FY OE/share, key_numbers.md).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $311.9M — essentially the same as the conservative figure, which raises confidence in the FY2025 cash earnings.
- OE positive 4 of the last 5 fiscal years; the weak years are 2020-21 (COVID aero collapse; FY2020 net income -$1,572.6M) and the pension-hit 2023 (see NI_OCF_DIVERGENCE below).
- Net debt latest: **-$385.6M (net cash)** per dcf_numbers.json — the balance sheet is not the risk here.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $614.3M − prior YTD $69.0M + current YTD $260.0M = **TTM $805.3M**
- Capex: FY $280.6M − prior YTD $125.4M + current YTD $123.8M = **TTM $279.0M**
- SBC: FY $29.0M − prior YTD $14.6M + current YTD $14.1M = **TTM $28.5M**
- Shares (current-YTD weighted diluted): **138.5M**
- **TTM OE total $497.8M → base OE/share $3.59** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $0.91/share — rejected as the base: the median year is FY2024 and the window is dragged down by the pension-distorted FY2023 (see BASE_DIVERGENCE). The TTM base is also the conservative cross-check against guidance: it sits below the company's own raised FY2026 adjusted FCF guide of $550-600M.

## Moat: 6/10 — moderate-strong, qualification-based, but cyclical
Justification: ATI's materials are qualified into specific engine and airframe programs, its melt/forge capacity is scarce (20+ month lead times), and it holds oligopoly positions in strategic metals — real pricing power, proven by 440bp of margin expansion in Q2 2026. But through-cycle returns are poor (losses in 2020-21, negative OE years), the customer base is a handful of powerful OEMs, and the earnings stream rides the commercial aero cycle.
- FOR: Aero qualification / switching costs — materials are certified per program; requalifying a new supplier takes years, so incumbency is sticky.
- FOR: Scarce capacity — premium titanium lead times ~20 months and isothermal forging >24 months; demand outpaces available supply.
- FOR: One of only three qualified Western producers of high-purity hafnium and zirconium, materials China is restricting exports of.
- FOR: Long-term agreements and a record $4.4B backlog (+18% YoY, ~70% converting within 12 months); naval nuclear agreement ~$1B over five years, extending through 2030.
- FOR: Proven pricing power — Q2 2026 adjusted EBITDA margin 22.6%, +440bp YoY, on price/mix, not just volume.
- AGAINST: Deep cyclicality — FY2020 net income -$1,572.6M; OE/share has spanned negative to $2.15 within five years; a downturn in build rates hits OE directly.
- AGAINST: Customer concentration and bargaining power — a few airframe/engine OEMs set terms; ATI is a price-taker on program volumes.
- AGAINST: Capital intensity — capex $280.6M in FY2025 vs D&A $168.1M, with nickel capacity expansion still to fund through ~2028; scarcity rents require continuous reinvestment.
- AGAINST: Commodity input exposure (nickel, titanium sponge/scrap) and credible rivals (Howmet, Haynes, Carpenter) adding qualified capacity over time.
- A 6 gives CAP = 9.8 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 9.8 years, 15-year projection.

## DCF — v5 final run (2026-10-15)
Growth inputs: engine blended growth 6.17% (rev CAGR 5y 13.19%, 3y 6.17%, latest rev YoY 5.16%) + 2.12pp share-count adjustment = **g_base 8.29%**. Sanity check vs actual prints: FY2025 revenue grew 5.16%, Q2 2026 revenue +11% YoY, backlog +18%, and adjusted EPS grew 66% YoY in Q2 2026 — the base start of 8.29% sits inside the observed revenue range, and even the super-bull OE/share start (20.29%) is below the current EPS print because OE/share carries operating leverage plus buybacks; it still fades to 2.5% over the 9.8-year CAP. No recalibration needed. Probabilities were bear-tilted to 15/30/30/15/10 (from the 10/25/30/25/10 default) because of OE_VOLATILE — this business has printed negative OE within the last five years. OE multipliers are the defaults 0.75/0.90/1.00/1.10/1.25. Price $187.84.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | -3.71% | 0.75 | Aero build rates roll over; pricing gains unwind | $16.77 | 3.50% |
| Bear | 30% | 3.29% | 0.90 | Cycle plateaus at current backlog; margins normalize | $27.47 | 4.35% |
| Base | 30% | 8.29% | 1.00 | Backlog converts, mid-single-digit revenue growth, buybacks continue | $38.13 | 5.22% |
| Bull | 15% | 13.29% | 1.10 | Engine content gains + defense ramp compound | $52.37 | 6.38% |
| Super bull | 10% | 20.29% | 1.25 | Scarcity rents persist a full decade; capacity lands on time | $81.03 | 8.56% |

- **Probability-weighted: IV@15% $38.16 (-79.7% vs price), IV@12% $51.33, IV@10% $66.12, weighted IRR 5.27%, base-case IRR 5.22%**
- **Tier by numbers: D.** Diagnostics (dcf_numbers.json): OE yield 1.91%, terminal value 20.1% of IV@15%, scenario spread 4.83x, net debt / normalized OE -0.76x (net cash), 9.6 months since FY end.
- The verdict does not hinge on the base choice: the preliminary run on the 3-yr median base ($0.91/share) gave weighted IRR 3.25% and IV@15% $10.20 — also Tier D. Even the super-bull case (IV@15% $81.03, IRR 8.56%) values the stock at less than half the price.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.6 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, quoted above.
- **BASE_DIVERGENCE** (latest FY $2.15 vs 3-yr median $0.91): the median is the distorted one. The 3-yr window includes FY2023, whose OE was crushed by $272M of voluntary pension contributions (below), and FY2024, still early in the OCF recovery ($407.2M). Latest FY and TTM both reflect the current run-rate; TTM base used.
- **NI_OCF_DIVERGENCE** (2023): identified, two-sided. FY2023 net income was $410.8M but OCF only $85.9M: (1) OCF included $272M of voluntary contributions to the U.S. defined-benefit pension plans — excluding them, the company's own FY2023 release puts OCF at $358M; (2) net income was flattered by a $137.4M non-cash discrete tax benefit from reversing the valuation allowance in Q4 2023; plus a working-capital build on rising operating levels. Neither effect is in the TTM base window, and the OCF-based conservative OE is the series used throughout.
- **OE_VOLATILE** (OE/share spans >3x over 5 years): real cyclicality (COVID collapse, pension year, recovery). Handled by the TTM base plus bear-tilted probabilities (45% on bear-or-worse).
- **BUYBACK_TAILWIND** (share count shrinking 2.1%/yr): already credited via the +2.12pp growth adjustment in the blend; not double-counted in the verdict. Q2 2026 buybacks were $50M with $495M of authorization remaining at quarter-end.
- **LOW_OE_YIELD** (1.91% on the TTM base): acknowledged — at $187.84 the price rests almost entirely on future growth. That is precisely why the tier is fragile in the downward direction only: no plausible growth path in the scenario set clears even 10%.
- **WIDE_SCENARIO_SPREAD** (4.83x): real, driven by the cyclicality above. Confidence is capped at medium; the verdict is sized to the conservative end — which here changes nothing, since every scenario is below the hurdle.
- **BIG_NET_CASH** (preliminary run: net cash 3.0x the median-normalized OE): net cash is $385.6M — real but immaterial against a $26.6B market cap; it does not rescue the valuation and is already inside the engine's IV via net debt. Noted, no adjustment.

## My thoughts / overlay
- Quality is not the debate; price is. The operating story is genuinely strong — record backlog, qualification moat, pricing power, raised guidance, net cash balance sheet, SBC a trivial $28.5M TTM. The stock, however, trades at ~39x the midpoint of the company's own raised FY2026 adjusted EPS guidance (per contemporaneous analyst coverage) and ~52x TTM owner's earnings/share of $3.59.
- Method range: median base → weighted IRR 3.25% (D); TTM base → 5.27% (D); super-bull alone → 8.56% (D). Every defensible input set lands in Tier D. This is one of the rare names where the spread of methods does not matter.
- What would have to be true at $187.84: roughly a decade of 20%+ OE/share compounding with no aero downturn — a path no scenario here assigns more than 10% probability, and one the company's own history (negative OE twice in five years) argues against.
- Hurdle price: the weighted IV@15% is **$38.16** — the price would need to fall ~80% to clear Andrew's 15% hurdle on the weighted case, and even the super-bull IV@15% ($81.03) is 57% below the current price. There is no margin-of-safety entry anywhere near the current quote.

## Final verdict
- **Final tier: D** (weighted IRR 5.27% on the TTM base; D under every base and every scenario)
- Confidence: **Medium** (capped by WIDE_SCENARIO_SPREAD; the direction of the verdict is not in doubt, the exact IV is)
- One-liner: Real qualification moat (6/10) and a record $4.4B backlog, but at $187.84 the price pre-pays a decade of flawless aero compounding — weighted IRR 5.3%, IV@15% $38.16; clears the 15% hurdle only below ~$38.
