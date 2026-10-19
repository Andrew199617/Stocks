# J — Jacobs Solutions Inc.
Engine 5.4.0 run, 2026-10-16. Price $138.67 (nasdaq_quote_api), market cap $16.91B — in scope under $40B. All figures copied from dcf_numbers.json, ttm.json, or fundamentals.json — none recomputed.

## What it is
Global engineering, design, procurement/construction-management and consulting firm (Infrastructure & Advanced Facilities plus PA Consulting), ~47,000 people in 40 countries per company materials found in research. Revenue is mostly people-billed fees plus large pass-through procurement — Q3 FY2026 gross revenue rose 34.5% y/y but adjusted net revenue (fees) rose only 8.3%, because pass-through roughly doubled. End markets: data centers, semiconductors, energy & power, transportation, water, life sciences. The Critical Mission Solutions / cyber business was spun off into Amentum on 2024-09-27 (the Separation Transaction) and is now discontinued operations — the pre-spin revenue base is not comparable to the continuing business.

## Owner's earnings
- FY2025 (10-K, financials_history.csv via dcf_numbers.json): OCF $686,704,000; capex $79,232,000; SBC $60,960,000 (always a real cost). Conservative OE $546,512,000 = $4.48/share (base_oe_latest_per_share).
- Engine normalized base (median of last 3 FY OE/share): $6.00/share (FY2023 $6.00, FY2024 $6.83, FY2025 $4.48 in financials_history.csv) — rejected as the base: FY2024 still straddles the Amentum separation and its OE was flattered relative to the post-spin continuing business; the median sits well above the current TTM print.
- **Base used = TTM through Q3 FY2026 (2026-06-26), from ttm.py (filing-direct, no hand math):**
  - OCF: FY $686,704,000 − prior YTD $303,619,000 + current YTD $352,758,000 = **TTM $735,843,000**
  - Capex: FY $79,232,000 − prior YTD $49,655,000 + current YTD $61,722,000 = **TTM $91,299,000**
  - SBC: FY $60,960,000 − prior YTD $47,421,000 + current YTD $56,882,000 = **TTM $70,421,000**
  - Shares (current-YTD weighted diluted): **118,486,000**
  - **TTM OE total $574,123,000 → base OE/share $4.85** (base_source: ttm_json)
- OE positive 5/5 of the last 5 fiscal years on the filed history, but the per-share range is wide ($2.27–$6.83 over FY2022–FY2025) — see OE_VOLATILE below. Net debt $1,001,008,000 (LongTermDebtNoncurrent+LongTermDebtCurrent basis, dcf_numbers.json), plus lease liabilities $473,401,000; net debt is 1.69x normalized OE (diagnostics). Buybacks: shares fell at a −1.98%/yr CAGR (share_cagr), already credited in the blend via the revenue-component adjustment — not double-counted.

## Moat: 4/10 — weak-to-moderate
Justification: a people-based services franchise with scale and reputation but no structural lock-in. Evidence from fundamentals.json: ROIC proxy was 7.1% (FY2020), 5.3% (FY2021), 5.6% (FY2022), 6.3% (FY2023), then 10.2% (FY2024) and 11.2% (FY2025) — through most of the cycle it sat at or below a plausible cost of capital, only recently rising above it, and the TTM gross margin in fundamentals.json is 22.1% (FY2025 24.8%) as low-margin pass-through mix surged. That history does not support a 7+ moat.
- FOR: scale and reputation — ENR ranks Jacobs #1 in 18 categories including data centers (Q3 FY2026 release, via search); record backlog $28.9B, up 27.3% y/y, TTM book-to-bill 1.4x gross / 1.2x on adjusted net revenue; diversified end markets with secular data-center, semiconductor, power and water capex behind them; long-standing government and blue-chip client relationships; PA Consulting adds higher-end advisory.
- AGAINST: the assets walk out the door — engineers are poachable and contracts are competitively re-bid, so there is no network effect, switching cost, or owned IP moat; ROIC history (above) shows pricing power is thin through a cycle; pass-through procurement inflates revenue with almost no fee margin; goodwill-heavy, acquisition-built balance sheet (PA Consulting integration and its temporarily higher tax rate already hit GAAP EPS in Q3 FY2026); exposure to client capex cycles and public-sector budgets.
- A 4 gives CAP = 7.2 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 7.2 years, 15-year projection.

## DCF — final run (2026-10-16)
Growth recalibration (written reason): the engine blend is 3.09%, but its components straddle the Amentum basis break — rev CAGR 5y −2.38% compares pre-spin revenue to the smaller continuing business, and OE/share CAGR 2y −13.59% falls off the separation-flattered FY2024. The meaningful current signals are fee-based: Q3 FY2026 adjusted net revenue +8.3% y/y, FY2026 guidance raised for the third consecutive quarter to adjusted net revenue growth of 9.5–10.0% and adjusted EPS $7.20–7.30 (per the Q3 release via search), backlog +27.3%. Base start is therefore set to 8.0% — at the latest fee-revenue print, below the gross-revenue print (+34.5%, pass-through-driven, explicitly not used) and below guidance, because OE conversion lags fee growth. Scenario starts via offsets −0.051 / −0.001 / +0.049 / +0.099 / +0.149 vs the 3.09% blend. Probabilities 10/25/30/25/10 (defaults — backlog strength is offset by OE volatility, so no bullish shift); OE multipliers 0.75/0.90/1.00/1.10/1.25 (defaults).

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | −2.0% | 0.75 | Capex cycle turns, backlog converts poorly, OE repeats a down year | $25.02 | 4.66% |
| Bear | 25% | 3.0% | 0.90 | Fee growth fades to low single digits, margins stay thin | $36.44 | 5.80% |
| Base | 30% | 8.0% | 1.00 | Current fee trajectory decays normally over the CAP | $48.99 | 7.07% |
| Bull | 25% | 13.0% | 1.10 | Data-center/power demand sustains double-digit fee growth | $65.03 | 8.65% |
| Super bull | 10% | 18.0% | 1.25 | AI-infrastructure supercycle plus operating leverage | $88.91 | 10.86% |

- **Probability-weighted: IV@15% $51.46 (−62.9% vs price), IV@12% $68.72, IV@20% $35.98, IV@25% $27.50, weighted IRR 7.34%, base-case IRR 7.07%**
- **Tier by numbers: D; bear tier D, bull tier D — no TIER_BAND issue, the whole band is D.** Even the super-bull case (10.86% IRR, IV@15 $88.91) does not clear 15% at $138.67.
- Diagnostics: OE yield 3.49%, terminal value 19.2% of IV@15%, scenario spread 3.55x, net debt 1.69x normalized OE, 12.6 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 13 months ago): resolved by construction — the base is the TTM figure from ttm.py through 2026-06-26, legs quoted above. TTM OE/share $4.85 is below the $6.00 median, so the stale median would have flattered the result; it was not used.
- **OE_VOLATILE** (OE/share range >3x over 5 years): real and structural here — separation-era distortions plus working-capital swings in a contracting business (OCF ranged from −$366M in FY2019 to $1,055M in FY2024 on the filed history). Handled by the TTM base, 35% combined weight on bear-or-worse, and confidence capped at medium.
- **NI_OCF_DIVERGENCE** (2025, >40%): FY2025 net income was $289,336,000 vs OCF $686,704,000. The gap is below-the-operating-line separation noise, not cash earnings quality: operating income actually rose to $863,634,000 in FY2025, while miscellaneous/other income swung to −$189,663,000 (vs +$219,454,000 in FY2024, which included Amentum-related gains), there was a $20,510,000 loss on extinguishment of debt, and discontinued operations lost $23,966,000 after contributing +$206,850,000 in FY2024 (8-K/10-K figures found in research). The OCF-based conservative OE used throughout is not contaminated by those non-cash/non-operating items, so the base stands.
- No WIDE_SCENARIO_SPREAD flag on the final run (spread 3.55x), no DATA_GAP, no sector mismatch, no overrides applied.

## My thoughts / method range
- The verdict does not hinge on the growth recalibration: on the preliminary run (median base $6.00, blend growth 3.09%, default scenarios) the weighted IRR was 7.47% and weighted IV@15% $53.98 — also Tier D. On the final TTM base with growth recalibrated up to current fee prints, it is 7.34% / $51.46. Two quite different defensible input sets land in the same place because the $138.67 price against a $4.85 TTM OE/share (OE yield 3.49%, diagnostics) already capitalizes years of the backlog story.
- Quality is middling, not poor: positive OE every filed year, buybacks shrinking the count ~2%/yr, backlog at a record. But cash conversion is lumpy, ROIC only recently cleared the cost of capital, and the Q3 FY2026 gross-revenue surge is mostly pass-through money Jacobs collects and pays out — the fee business grew 8.3%.
- Hurdle-clearing prices (dcf_numbers.json): the weighted cash flows clear 15% only at or below $51.46, 20% at $35.98, 25% at $27.50 — roughly a 63% fall from $138.67 for the 15% hurdle.

## Final verdict
- **Final tier: D** (weighted IRR 7.34%; bear→bull band D→D)
- Confidence: **Medium** (high on the filing-derived TTM base, medium on any single growth path given OE volatility)
- One-liner: Sound engineering franchise, moat 4/10, but at $138.67 it prices in the backlog supercycle — weighted IRR 7.3%, IV@15% $51.46; it clears 15% only below ~$51.
