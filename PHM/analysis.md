# PHM — PulteGroup, Inc.
v5 run, 2026-10-15. In scope (market cap $22.564B at $113.08, nasdaq_quote_api). All figures below are copied from dcf_numbers.json, ttm.py output (ttm.json), or financials_history.csv — none are recomputed.

## What it is
Third-largest US homebuilder: single-family homes across 47 markets under Pulte Homes, Centex (first-time), Del Webb (active adult — the margin leader), DiVosta and John Wieland Homes, plus Pulte Mortgage/title (mortgage capture rate 85% in Q2 2026). 2025 closing mix: 38% first-time, 40% move-up, 22% active adult. Deeply cyclical, land-heavy, and currently mid-downturn: FY2025 revenue $17,311,953,000 (−3.54% YoY), and Q2 2026 home sale revenues fell 11% YoY on closings of 6,997 (−8%) at a $544,000 average price (−3%), with net income of $472M / EPS $2.48 vs $608M / $3.03 a year earlier. The forward indicators are stabilizing: Q2 2026 net new orders rose 6% to 7,536, backlog rose 2% to 10,966 units, and management reaffirmed FY2026 guidance of 28,500–29,000 closings (vs 29,500 in 2025) at a $550,000–$560,000 average price and a 24.5–25% home sale gross margin.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $1,871,249,000; capex $122,716,000; SBC $54,823,000 (always a real cost).
- **Conservative owner's earnings FY2025: $1,693,710,000 = $8.49/share** (latest FY OE/share, dcf_numbers.json).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $2,218,730,000 — higher than the conservative figure because it starts from net income and does not charge the year's land/inventory cash build; for a homebuilder the OCF-based conservative figure is the honest one, since inventory spend is a real, recurring cash cost of this business, not a one-off.
- OE positive 5 of the last 5 fiscal years. Net debt is **negative $1,936,969,000 — a net cash position** (diagnostics: net debt −1.28x normalized OE; Q2 2026 debt-to-capital 12.3%). The balance sheet is not the problem; the cycle is.
- SBC is small ($54.8M FY2025; $58.1M TTM) — dilution is not a story here; the share count is shrinking (see BUYBACK_TAILWIND).

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $1,871,249,000 − prior YTD $421,733,000 + current YTD $176,802,000 = **TTM $1,626,318,000**
- Capex: FY $122,716,000 − prior YTD $64,138,000 + current YTD $55,297,000 = **TTM $113,875,000**
- SBC: FY $54,823,000 − prior YTD $30,973,000 + current YTD $34,207,000 = **TTM $58,057,000**
- Shares (current-YTD weighted diluted): **191,990,000**
- **TTM OE total $1,454,386,000 → base OE/share $7.58** (base_source: ttm_json)
- The engine's normalized base (median of last 3 FY OE/share) is $8.49/share. The TTM base is used because the FY base is 9.5 months stale and 2026 prints are materially weaker (Q2 EPS −18% YoY, H1 OCF well below the prior-year pace); the median also spans the 2023 blowout year. The TTM base is the conservative, current one. Note TTM OCF is itself depressed by the seasonal H1 land/inventory build — that cuts the other way and is one reason confidence is low rather than the verdict harsher.

## Moat: 4/10 — weak-to-moderate
Justification: #3-builder scale and the Del Webb active-adult franchise are real, but the product is a commodity, there is no through-cycle pricing power, land is bought in an open market, and demand is set by mortgage rates, not by the company.
- FOR: #3 US homebuilder scale — national purchasing leverage, 47 markets, ~235,000 controlled lots; Del Webb active-adult brand leadership — highest gross margins in the portfolio, demographic tailwind; diversified buyer mix (38% first-time / 40% move-up / 22% active adult in 2025); fortress balance sheet — net cash, 12.3% debt-to-capital, return-focused operating model with disciplined spec inventory (finished specs down to ~1.3 per community); Pulte Mortgage capture rate of 85% adds financial-services margin on top of the home sale.
- AGAINST: commodity product with no switching costs — buyers shop on price and incentives; no through-cycle pricing power — incentives reached 9.9% of gross sales in Q4 2025 and home sale gross margin fell from 27.0% (Q2 2025) to 25.0% (Q2 2026); land is bought in a competitive open market and the land-heavy model traps cash in inventory — unlike NVR's land-light model, Pulte's earnings overstate its cash in build years (see NI_OCF_DIVERGENCE); demand is hostage to mortgage rates and affordability; deeply cyclical — OE/share has spanned >3x over the last 5 fiscal years.
- A 4 gives CAP = 7.2 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 7.2 years, 15-year projection.

## DCF — v5 final run (2026-10-15)
Growth sanity check (mandatory): the engine's blended growth is −0.44% (rev CAGR 5y 9.42%, rev CAGR 3y 2.65%, latest rev YoY −3.54%, OE/share CAGR 2y −4.45%), adjusted +5pp for the buyback (share count −5.46%/yr, capped) → g_base 4.56%. Scenario starts use the default offsets (−12/−5/0/+5/+12pp). Against actual prints: current prints are negative (Q2 2026 revenue −11%, EPS −18%), so no start sits implausibly *below* what the company just printed on the bull side; the base start (+4.56%) is above the current print rate and is defensible only because it is a *per-share* rate carried largely by the ~5%/yr buyback against a trough-depressed TTM base, with orders already inflecting (+6% in Q2 2026) and community count guided +3–5%. The super-bull start (+16.56%) requires a real housing upcycle (rate relief + volume surge) — hence its probability was cut to 5%. Probabilities were skewed bearish vs the 10/25/30/25/10 defaults per the OE_VOLATILE flag: **15/30/30/20/5**. OE multipliers default 0.75/0.90/1.00/1.10/1.25. Price $113.08, TTM base $7.58/share.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | −7.44% | 0.75 | Rates stay high, affordability worsens, margins compress further | $31.62 | 5.71% |
| Bear | 30% | −0.44% | 0.90 | Long flat trough; incentives stay elevated, OE stuck below base | $49.90 | 7.92% |
| Base | 30% | 4.56% | 1.00 | Stabilization per guidance; per-share growth mostly buyback-carried | $67.22 | 9.99% |
| Bull | 20% | 9.56% | 1.10 | Orders inflection converts; community growth + margin recovery | $89.40 | 12.50% |
| Super bull | 5% | 16.56% | 1.25 | Rate relief triggers a volume upcycle off the trough base | $131.89 | 16.85% |

- **Probability-weighted: IV@15% $64.35 (−43.1% vs price), IV@12% $85.11, IV@10% $108.21, weighted IRR 9.68%, base-case IRR 9.99%**
- **Tier by numbers: D.** Diagnostics: OE yield 6.70%, terminal value 18.28% of IV@15%, scenario spread 4.17x, net debt −1.28x normalized OE, 9.46 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.46 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, quoted above, passed via `--ttm`.
- **BUYBACK_TAILWIND** (share count −5.46%/yr): already credited via the +5pp growth adjustment in g_base; not double-counted in the verdict. It is also the main reason the base scenario's per-share growth start is positive while total-company prints are negative.
- **OE_VOLATILE** (OE/share range >3x over 5 years): real and structural — the swing is the land/inventory cash cycle (heavy build years crush OCF while net income stays high; see 2021–22 vs 2023 in financials_history.csv). Handled by the normalized/TTM base plus bear-skewed probabilities (45% on bear-or-worse).
- **NI_OCF_DIVERGENCE** (2024: net income $3,083,262,000 vs OCF $1,680,794,000): the working-capital cycle, not a one-off gain or an accounting problem — 2024 was a record earnings year in which cash went into land acquisition/development and homes under construction ahead of closings (the same pattern in 2021: NI $1,946,320,000 vs OCF $1,004,021,000, and 2022: NI $2,617,317,000 vs OCF $668,466,000; it reverses in harvest years like 2023: OCF $2,196,762,000). The OE base used throughout is OCF-based, so the divergence makes the base *more* conservative, not less — no adjustment needed, but it is why the maintenance-definition OE ($2,218,730,000 for FY2025) is rejected as the headline.
- **WIDE_SCENARIO_SPREAD** (super-bull IV 4.17x super-bear IV): real — a cyclical at a trough genuinely has this outcome range. Confidence is low and the verdict is sized to the conservative end.

## My thoughts / overlay
- The method range is narrow for once: the preliminary run (median 3-yr base $8.49/share, default probabilities) gave weighted IRR 11.59% / Tier C; the final run (TTM base $7.58/share, bear-skewed probabilities) gives 9.68% / Tier D. Every defensible input set lands below the 15% hurdle — the disagreement is only C vs D. The market is pricing PHM for a recovery the current cash flows don't yet support.
- Quality is real: net cash balance sheet, disciplined spec management, Del Webb, 85% mortgage capture, buybacks at ~5%/yr of the count. None of that closes a 43% gap between price ($113.08) and weighted IV@15% ($64.35). At ~$64 the weighted case clears 15%; a buyer who wants a margin of safety against the bear case ($49.90 IV@15%) needs a lower price still. Even the super-bull scenario only just clears the hurdle (16.85% IRR at 5% probability).
- What would change the verdict: a mortgage-rate break that converts the +6% orders inflection into closing volume and gross-margin recovery, or a price reset toward the $60s. Until then this is a good company at a full price.

## Final verdict
- **Final tier: D** (weighted IRR 9.68% on the v5 final inputs; method range C to D — below the 15% hurdle on every defensible base)
- Confidence: **Low** (WIDE_SCENARIO_SPREAD 4.17x, OE_VOLATILE, and a TTM base depressed by seasonal land spend — but the shortfall vs the hurdle is far larger than the base uncertainty)
- One-liner: Quality cyclical homebuilder, moat 4/10 — TTM owner's earnings do not clear 15% at $113.08 (weighted IRR 9.7%, weighted IV@15% $64.35); the price only clears the hurdle below ~$64.
