# AMRZ — Amrize Ltd
v5 run, 2026-10-16. Market cap $20.660B at $37.32 (nasdaq_quote_api) — in scope (<$40B).

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.py output, or financials_history.csv — none are recomputed. Balance-sheet debt figures are quoted in words from the company's Q2 2026 reporting because the engine could not read AMRZ's debt tags (see FLAGS).

## What it is
North America's largest cement producer and second-largest commercial roofing company, spun off from Holcim in June 2025. Two segments: Building Materials (cement, aggregates, ready-mix concrete, asphalt) and Building Envelope (commercial roofing, wall systems). Ranked #1 or #2 in 85% of the aggregates markets it serves; roughly 46 years of aggregates reserves and 71 years of cement reserves at end-2024 (Morningstar). Q2 2026: revenue $3,494M, +8.6% YoY (organic +6.7%), net income $476M, +14.4%, Adjusted EBITDA $986M, +5.8% with margin down 80bp on oil-driven freight/diesel/raw-material cost inflation. FY2026 guidance raised on revenue ($12.5–12.7B) but trimmed on Adjusted EBITDA ($3.1–3.2B) for the same cost inflation; guided 2026 capex ~$900M.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** revenue $11,815M; net income $1,185M; operating cash flow $2,208M; capex $788M; D&A $758M; SBC $14M (negligible — dilution is a non-issue here).
- **Conservative owner's earnings FY2025: $1,406M = $2.54/share** (latest-FY OE/share in dcf_numbers.json).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $1,929M in FY2025 — above the conservative figure because 2025 carried a large working-capital release; the OCF-based conservative figure is the one used throughout.
- Filed history (carve-out basis, see THIN_HISTORY): conservative OE $1,401M (2023) / $1,634M (2024) / $1,406M (2025); revenue essentially flat at $11,677M / $11,704M / $11,815M. OE positive 3 of the last 3 fiscal years.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $2,208M − prior YTD −$441M + current YTD −$475M = **TTM $2,174M** (H1 OCF is negative — building materials is heavily seasonal, earnings land in H2)
- Capex: FY $788M − prior YTD $448M + current YTD $520M = **TTM $860M**
- SBC: FY $14M − prior YTD $3M + current YTD $20M = **TTM $31M**
- Shares (current-YTD weighted diluted): **554,100,000**
- **TTM OE total $1,283M → base OE/share $2.32** (base_source: ttm_json)
- The engine's normalized base (median of last 3 FY) is $2.54/share. The TTM base was used instead: it is more current (STALE_FY) and more conservative — TTM OE fell vs FY2025 because capex is stepping up toward the ~$900M guided for 2026 while OCF is flat. The preliminary median-base run produced a nearly identical result (weighted IRR 9.42%, weighted IV@15% $20.63), so the verdict does not hinge on the base choice.

## Moat: 6/10 — moderate-strong, local-market moats on a commodity product
Justification: cement and aggregates are local oligopolies by physics — transport costs wall off each market, permitted reserves are scarce and slow to replicate, and Amrize holds the #1/#2 position in 85% of its aggregates markets with decades of reserves. That earns real pricing power in aggregates. But the products are commodities, national rivals are equally scaled, demand is construction-cyclical, and standalone cement pricing power is not yet proven (Q2 2026 cement pricing was −0.2% constant-currency while costs inflated).
- FOR: largest cement producer in North America; #1/#2 position in 85% of aggregates markets served; transport-cost local oligopolies — heavy, low-value-density products cannot be shipped far profitably; scarce permitted reserves (~46 yrs aggregates, ~71 yrs cement) that take years to permit; vertical integration from cement and aggregates through ready-mix to roofing (cross-selling, supply security); demonstrated aggregates pricing (+4.0% constant-currency, freight-adjusted, in Q2 2026).
- AGAINST: commodity products with no brand or switching-cost protection; equally scaled national rivals (CRH, Vulcan, Martin Marietta, Heidelberg Materials); demand tied to the construction cycle (infrastructure/commercial strong now, residential roofing soft); cement pricing power unproven as a standalone — Q2 2026 cement price −0.2% constant-currency against oil-driven cost inflation, which forced an EBITDA guidance cut even as revenue guidance rose; energy and carbon-compliance costs are structural headwinds for cement kilns; growth capex and bolt-on M&A (PB Materials, Rapid Redi-Mix) consume the cash the moat generates.
- A 6 gives CAP = 9.8 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 9.8 years, 15-year projection.

## DCF — v5 final run (2026-10-16)
Growth recalibration (written reason): the engine's blended growth is 0.54%, built entirely from the flat carve-out history (FY2023–25 revenue $11.68B → $11.82B). That history understates the current business: Q2 2026 revenue printed +8.6% YoY and FY2026 revenue is guided to $12.5–12.7B (+6–7.5%). But owner's earnings are NOT growing at the revenue rate — TTM OE/share ($2.32) is below FY2025 ($2.54) because capex steps up to ~$900M guided and oil-driven cost inflation trimmed the EBITDA guide. Scenario starts were therefore set via offsets (−0.09 / −0.03 / +0.035 / +0.075 / +0.12 vs g_base 0.54%) to −8.46% / −2.46% / **4.04%** / 8.04% / 12.54%: the base start (4.04%) sits deliberately below the current revenue prints because OE growth lags revenue growth here; the bull start (8.04%) approximates the current revenue print with H2 price/cost recovery (management guides price increases in H2); the super-bull start (12.54%) is above any OE print the company has produced and requires sustained volume plus full price/cost recovery — story-driven, weighted 10%. Probabilities 10/25/35/20/10 (base weighted up on the raised revenue guidance); OE multipliers at the defaults 0.75/0.90/1.00/1.10/1.25. Price $37.32.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | −8.46% | 0.75 | Construction downturn; volumes and price roll over together | $8.76 | 4.99% |
| Bear | 25% | −2.46% | 0.90 | Cost inflation sticks, pricing lags, capex stays at the higher plateau | $13.71 | 6.85% |
| Base | 35% | 4.04% | 1.00 | Guided revenue growth, OE lagging on capex step-up, gradual price/cost repair | $20.34 | 9.38% |
| Bull | 20% | 8.04% | 1.10 | Data-center/infrastructure demand holds; H2 price increases restore margins | $26.73 | 11.63% |
| Super bull | 10% | 12.54% | 1.25 | Full price/cost recovery plus sustained volume and M&A contribution | $37.09 | 14.93% |

- **Probability-weighted: IV@15% $20.48 (−45.1% vs price), IV@12% $27.14, IV@10% $34.58, weighted IRR 9.46%, base-case IRR 9.38%**
- **Tier by numbers: D.** Diagnostics (dcf_numbers.json): OE yield 6.20%, terminal value 18.6% of IV@15%, scenario spread 4.24x, 9.5 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.5 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026 (ytd_end 2026-06-30), quoted above.
- **NI_OCF_DIVERGENCE** (NI vs OCF >40% apart in 2023, 2024, 2025): structural, not a one-off. This is a heavy-asset cement business — D&A ran $689M / $736M / $758M across 2023–25 against net income of $956M / $1,274M / $1,185M, and non-cash depreciation is most of the NI→OCF bridge every year. No tax deposit, impairment, or single working-capital event drives it. The OCF-based conservative OE already subtracts full capex, so the divergence does not inflate the base.
- **THIN_HISTORY** (only 3 fiscal years): real and structural — Amrize was Holcim's North American business until the June 2025 spin-off, so the filed history is carve-out financials (2023–25) with allocated parent costs, not a long standalone record. Handled by anchoring growth to current guidance/prints rather than the flat carve-out blend, and by not claiming high confidence.
- **WIDE_SCENARIO_SPREAD** (super-bull IV 4.24x super-bear IV): real for a cyclical at a demand inflection, and confidence is held below high. Note the spread does not rescue the verdict: even the super-bull scenario's IRR (14.93%) fails to clear the 15% hurdle at $37.32.
- **Balance sheet (no engine flag — engine read no debt tags, net_debt_latest null):** per the company's Q2 2026 reporting, gross debt was $6,004M and cash $729M at June 30, 2026, i.e. net debt of $5,275M, 1.7x trailing Adjusted EBITDA of $3,024M. Moderate leverage for this sector — not a verdict driver either way; the DCF here is an owner's-earnings yield model, so the leverage is noted, not folded into the IV.

## My thoughts / overlay
- The method range is tight for once: median-base run 9.42% weighted IRR / $20.63 IV@15%; TTM-base final run 9.46% / $20.48. Both Tier D. The disagreement that matters is not base choice — it is the market price, which embeds growth the OE record does not show.
- Quality is not the problem. This is a genuinely strong franchise (moat 6) with negligible SBC, a $1.0B buyback authorization ($197M repurchased in Q2 2026) plus dividends, and demand tailwinds from data centers and infrastructure. The problem is arithmetic: at $37.32 the OE yield on the TTM base is 6.20%, and no scenario in the set — including a 12.54% growth start at a 1.25x OE multiplier — clears 15%.
- Red flags, sized honestly: (1) a prior-period revision disclosed with Q2 2026 — deferred revenue on extended warranties from 2022–2023 acquisitions was understated by $78M at December 31, 2025, and affected 2025/early-2026 periods were revised; small vs revenue, but it is an accounting-controls blemish in year one as a public company. (2) The Q2 pattern of raising revenue guidance while cutting EBITDA guidance — volume is carrying the growth (+$200M of the Q2 revenue increase was volume, per earnings coverage) while price/cost is negative; if H2 price increases don't land, the bear case is the base case. (3) Capex is guided up to ~$900M and M&A is ramping — OE conversion will stay under pressure near-term.
- Margin of safety: the price that clears 15% on the weighted numbers is the weighted IV@15% itself, **$20.48** — roughly 45% below the current $37.32. Even the 12% IV ($27.14) sits below the price. A buyer at $37.32 is paying for the bull/super-bull path and getting paid for none of it.

## Final verdict
- **Final tier: D** (weighted IRR 9.46% on the v5 final inputs; no scenario clears 15% — super bull tops out at 14.93%)
- Confidence: **Medium** (filing-direct data is complete and the method range is tight, but the standalone history is 3 carve-out years and the scenario spread is 4.24x)
- One-liner: Strong NA building-materials franchise, moat 6/10, but at $37.32 the weighted IRR is 9.5% with IV@15% of $20.48 — it clears Andrew's 15% hurdle only below ~$20.48.
