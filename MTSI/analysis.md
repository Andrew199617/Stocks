# MTSI — MACOM Technology Solutions Holdings, Inc.
v5 run, 2026-10-15. Market cap $20.931B at $282.90 (nasdaq_quote_api) — in scope under $40B. All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.json, or financials_history.csv — none are recomputed.

## What it is
Analog/mixed-signal semiconductor maker in Lowell, MA: RF, microwave, millimeter-wave and photonic components (amplifiers, switches, drivers, photodetectors, TIAs) for three end markets — Data Center, Industrial & Defense, and Telecom. The current growth engine is AI data-center optical connectivity (800G/1.6T PAM4, photodetectors), with radar/GaN defense and LEO satellite programs behind it. Q3 FY2026 (ended 2026-07-03) revenue was $342.2M, +35.8% YoY, with a record 1.6:1 book-to-bill, and Q4 FY2026 was guided to $415–$425M revenue at 60–61% adjusted gross margin (company results via search).

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** revenue $967,258,000; operating cash flow $235,368,000; capex $42,551,000; SBC $79,362,000 (always a real cost).
- **Conservative owner's earnings FY2025: $113,455,000 = $1.53/share** (latest FY OE/share, dcf_numbers.json).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): **−$314,151,000** in FY2025 — distorted by a $280,685,000 ΔNWC swing in the filed history, so it is not used as the base; the OCF-based conservative figure is the cleaner series here.
- OE positive 5 of the last 5 fiscal years. Net debt $388,434,000 (dcf_numbers.json) — see HIGH_NET_DEBT below.

**Base used = TTM owner's earnings through Q3 FY2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $235,368,000 − prior YTD $165,732,000 + current YTD $201,550,000 = **TTM $271,186,000**
- Capex: FY $42,551,000 − prior YTD $22,332,000 + current YTD $46,889,000 = **TTM $67,108,000**
- SBC: FY $79,362,000 − prior YTD $61,593,000 + current YTD $65,873,000 = **TTM $83,642,000**
- Shares (current-YTD weighted diluted): **77,561,000** — up from the FY2025 diluted count of 73,986,000, i.e. the share count is rising, not shrinking.
- **TTM OE total $120,436,000 → base OE/share $1.55** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $1.46/share — close to the TTM figure, so the base choice is not the verdict driver here; both are tiny against a $282.90 price.

## Moat: 5/10 — moderate / narrow
Justification: Real design-win and qualification stickiness in RF/photonics sockets and decades of compound-semiconductor process know-how, with premium adjusted gross margins — but no network effects, no owned platform, faster and far larger rivals in every socket, and technology transitions (silicon photonics, co-packaged optics, CW lasers) that must be re-won each generation.
- FOR: Design-win / requalification stickiness in defense, telecom and data-center sockets (aerospace-grade certifications, long program lives); deep RF/microwave/mmWave and indium-phosphide photonics process know-how with a broad catalog serving 6,000+ customers; proven premium positioning — adjusted gross margin guided to 60–61% for Q4 FY2026; diversification across Data Center, Industrial & Defense and Telecom, all three growing sequentially in Q3 FY2026.
- AGAINST: Much larger rivals (Broadcom, Marvell, Coherent, Lumentum, Analog Devices/Qorvo class) contest every optical/RF socket with bigger R&D budgets; technology transitions can strand the current product lead — CW lasers are still pre-revenue, with production only toward late 2027/2028 on management's own framing; hyperscaler customer concentration and AI-capex cyclicality make orders lumpy; SBC-heavy compensation and acquisition amortization keep GAAP owner's earnings far below the adjusted earnings the market prices, and the diluted share count is rising (77,561,000 TTM vs 73,986,000 in FY2025).
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — v5 final run (2026-10-15)
Growth recalibration (written reason): the engine's growth blend is 12.73%, built from revenue CAGRs of 12.78% (5y) / 12.69% (3y), latest FY revenue YoY +32.58%, and OE/share CAGR 2y of only 2.61%, adjusted −1.30pp for the rising share count to g_base 11.43%. The default scenario starts (−0.6% to +23.4%) would sit far below what the company is actually printing on revenue (+32.58% FY2025, +35.8% YoY in Q3 FY2026, Q4 guided well above Q3 sequentially). Offsets were therefore recalibrated to −0.064 / +0.036 / +0.136 / +0.236 / +0.336, giving starts of 5.0 / 15.0 / **25.0** / 35.0 / 45.0%. The base start (25.0%) still sits *below* the recent revenue prints for a written reason: owner's-earnings growth lags revenue growth here — OE/share CAGR 2y is only 2.61%, TTM capex rose to $67,108,000, SBC is $83,642,000 TTM, and the share count is rising — so OE/share cannot be assumed to compound at the revenue rate. Bull (35.0%) matches the latest revenue print and super bull (45.0%) exceeds it, staying under the 50% scenario cap. Probabilities are the defaults 10/25/30/25/10; OE multipliers are the defaults 0.75/0.90/1.00/1.10/1.25. Price $282.90.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | 5.0% | 0.75 | AI-capex digestion; data-center orders stall, defense/telecom can't offset | $10.61 | 2.78% |
| Bear | 25% | 15.0% | 0.90 | Growth halves from current prints; margins stop expanding | $19.21 | 3.48% |
| Base | 30% | 25.0% | 1.00 | Strong data-center ramp decays normally over the CAP; OE/share lags revenue | $31.92 | 4.24% |
| Bull | 25% | 35.0% | 1.10 | Revenue growth holds at the Q3 FY2026 print; operating leverage lifts OE | $51.96 | 5.42% |
| Super bull | 10% | 45.0% | 1.25 | 1.6T/3.2T and photonics ramps compound; CW lasers land late-decade | $86.36 | 7.29% |

- **Probability-weighted: IV@15% $37.07 (−86.9% vs price), IV@12% $51.83, IV@10% $68.60, weighted IRR 4.58%, base-case IRR 4.24%**
- **Tier by numbers: D.** Diagnostics (dcf_numbers.json): OE yield 0.55%, terminal value 24.0% of IV@15%, scenario spread 8.14x, net debt 3.38x normalized OE, 12.4 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 12.4 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q3 FY2026 (2026-07-03), quoted above.
- **NI_OCF_DIVERGENCE** (2023, 2024, 2025): filed history shows net income of $91,577,000 / $76,859,000 / −$54,210,000 against OCF of $166,917,000 / $162,640,000 / $235,368,000. The gap direction is explained by the non-cash items in the same filed history — D&A of $52,153,000 / $67,249,000 / $63,295,000 and SBC of $38,103,000 / $45,644,000 / $79,362,000 across those years — and in FY2025 operating income was a positive $129,652,000 while net income was negative, i.e. the net loss sits below the operating line. The OCF-based conservative OE used throughout is not contaminated by the net-income side of the divergence; the maintenance definition *is* distorted (ΔNWC $280,685,000 in FY2025, maintenance OE −$314,151,000) and was not used as the base for that reason.
- **LOW_OE_YIELD** (base OE yield 0.55%): real and decisive. The market is pricing adjusted (non-GAAP) earnings, which add back the $83,642,000 TTM SBC and acquisition amortization; on an owner's-earnings basis the current cash yield on the price is 0.55%, so the entire valuation rests on growth and margin expansion actually converting into OE/share. That is why even the super-bull case (45% start, 1.25x OE) only reaches a 7.29% IRR.
- **WIDE_SCENARIO_SPREAD** (8.14x): real — recalibrating growth starts up to the actual prints widened the spread. Confidence is set to low, and the verdict is sized to the conservative end; note the spread does not change the tier, because even the top of the range is a D.
- **HIGH_NET_DEBT** (net debt 3.38x normalized OE): folded into the verdict explicitly. Engine net debt is $388,434,000, counted on cash-and-equivalents only; management has described the company as roughly $325M net cash when short-term investments are counted against the $340M convertible notes due December 2029 (Q2 FY2026 reporting, via search). Either way the balance sheet is small next to the $20.931B market cap — leverage is not the story; it matters only because OE is currently so thin that 3.38x normalized OE leaves little cushion if the bear cases land, and those cases are already stressed at 0.75x/0.90x OE multipliers.

## My thoughts / overlay
- The method range here is unusually honest: every defensible input set lands in Tier D. The preliminary run (defaults, median base) gave a weighted IRR of 3.43%; the final run — TTM base *and* growth starts recalibrated up to the company's actual revenue prints — gives 4.58%. Even the super-bull scenario alone is 7.29%. There is no C, let alone a hurdle-clearing case, without assuming OE/share growth far beyond anything in the filed history (OE/share CAGR 2y: 2.61%).
- Quality is not the debate: the business is genuinely improving — revenue +35.8% YoY in Q3 FY2026, record book-to-bill, adjusted gross margin heading to 60–61%. The debate is purely price vs owner's earnings: at $282.90 the buyer is paying today for adjusted earnings that treat $83,642,000 of TTM SBC as free and assume the AI optical ramp compounds for years without a digestion year.
- The price that clears Andrew's 15% hurdle on the weighted case is the weighted IV@15% itself: **$37.07**. With a margin of safety against the wide scenario spread, a buyer would want to be at or below the bear/base IV range ($19.21–$31.92) — i.e. this is a watch-list name at a fraction of the current price, not a near-miss.
- Risks to the short-the-valuation view (reasons the price could stay rich): continued AI data-center capex, defense/LEO program ramps, CW-laser qualification toward late 2027/2028, and further multiple expansion on adjusted EPS growth — none of which change today's owner's-earnings math.

## Final verdict
- **Final tier: D** (weighted IRR 4.58% on the v5 final inputs; no tier override — the numbers tier and the verdict agree, and the method range is D under both the preliminary and recalibrated runs)
- Confidence: **Low** (WIDE_SCENARIO_SPREAD at 8.14x plus a 0.55% OE yield — the outcome is assumption-dominated, even though the tier itself is robust across assumptions)
- One-liner: Real AI-optical growth story, moat 5/10 — but owner's earnings of $1.55/share TTM cannot support $282.90 (weighted IRR 4.58%, IV@15% $37.07); it clears 15% only at or below ~$37.
