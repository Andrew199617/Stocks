# DOV — Dover Corporation
v5 run, 2026-10-15. In scope (market cap $26.636B at $193.33, nasdaq_quote_api).

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.py output, or financials_history.csv — none are recomputed.

## What it is
Diversified global industrial manufacturer across five segments: Engineered Products, Clean Energy & Fueling, Imaging & Identification, Pumps & Process Solutions, and Climate & Sustainability Technologies. A classic bolt-on-M&A compounder: many niche product lines (fueling equipment, pumps, marking/coding, refrigeration and heat exchangers, engineered components) sold into industrial, energy, retail-fueling, food-retail and data-center cooling end markets, with meaningful aftermarket and consumables pull-through. Q2 2026 (reported July 23, 2026): revenue $2.19B, +7% year over year with 5% organic growth; all five segments delivered positive organic growth; GAAP diluted EPS from continuing operations $2.31, adjusted $2.74. First-half 2026 revenue was $4,244M, +8%. Management raised full-year 2026 guidance: revenue growth 6–8% (4–6% organic), GAAP EPS $8.94–$9.14, adjusted EPS $10.55–$10.75.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $1,338,005,000; capex $220,263,000; SBC $43,981,000 (always a real cost); diluted shares 137,777,000.
- **Conservative owner's earnings FY2025: $1,073,761,000 = $7.79/share** (key_numbers.md: latest FY OE/share $7.79)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $1,245,523,000 — above the conservative figure, same order of magnitude; the conservative OCF-based figure is the one used, so no verdict depends on the maintenance definition being right.
- OE positive 5 of the last 5 fiscal years. Net debt $3.328B (key_numbers.md). Share count is shrinking: share count CAGR -1.37% (already credited in the growth blend as a +1.37% adjustment).
- SBC is small relative to OCF — this is an old-economy manufacturer, not an SBC-funded tech name; dilution is not a red flag here.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $1,338,005,000 − prior YTD $369,814,000 + current YTD $427,168,000 = **TTM $1,395,359,000**
- Capex: FY $220,263,000 − prior YTD $109,124,000 + current YTD $107,591,000 = **TTM $218,730,000**
- SBC: FY $43,981,000 − prior YTD $30,877,000 + current YTD $27,759,000 = **TTM $40,863,000**
- Shares (current-YTD weighted diluted): **135,725,000**
- **TTM OE total $1,135,766,000 → base OE/share $8.37** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $7.79/share — here the latest FY and the median are the same figure, and the TTM base sits modestly above both on stronger H1 2026 cash flow. Using the TTM base is the less conservative choice and it still does not rescue the verdict (see Thoughts), which makes the conclusion robust rather than base-sensitive.

## Moat: 5/10 — moderate / narrow
Justification: Dover holds leading niche positions across five diversified industrial segments with real installed-base, aftermarket and consumables pull-through, a pricing/productivity record, and disciplined bolt-on M&A compounding. But the advantages are local to each niche: no network effects, no portfolio-wide structural cost advantage, credible well-resourced rivals in every segment, and end-markets tied to cyclical industrial capex — revenue CAGR was only 1.04% over 3 years and 3.90% over 5 years. That is a collection of narrow moats, not a wide one.
- FOR: Leading niche positions across five diversified industrial segments; installed-base, aftermarket and consumables pull-through (marking/coding, pumps, fueling, refrigeration); pricing/productivity record — Q2 2026 total segment earnings margin 24.0%; disciplined bolt-on M&A compounding and a long record of consecutive dividend increases.
- AGAINST: No network effects; engineered components face credible rivals in every segment; cyclical industrial-capex end markets — revenue CAGR 1.04% (3y) / 3.90% (5y); pricing power is modest and segment-specific, not portfolio-wide; conglomerate structure — advantages are local, not structural at group level.
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — v5 final run (2026-10-15)
Growth recalibration (written reason): the engine's blended growth base is 3.84% (components: rev CAGR 5y 3.90%, rev CAGR 3y 1.04%, latest rev YoY 4.48%, OE/share CAGR 2y -1.18%, plus the +1.37% share-count adjustment). That blend is dragged by the flat 2023–24 period, while the current prints are stronger: Q2 2026 revenue +7% (+5% organic), H1 2026 revenue +8%, full-year 2026 guidance of 6–8% revenue growth, and Q2 adjusted EPS growth of +12%. Offsets were therefore recalibrated upward to −0.10 / −0.04 / +0.02 / +0.07 / +0.11 vs g_base, putting the base start at 5.8% — in line with guided organic growth — and the bull start at 10.8%, in line with current adjusted-EPS prints. Sanity check against prints: the super-bull start of 14.8% sits above any revenue print; it is defensible only as a 10% tail combining margin expansion, buybacks and bolt-on M&A, and it is weighted accordingly. The bear (−0.2%) and super-bear (−6.2%) starts sit below current prints on purpose — they are the industrial-downturn cases for a cyclical manufacturer after a strong first half, not a forecast. Probabilities kept at the defaults 10/25/30/25/10; OE multipliers kept at the defaults 0.75/0.90/1.00/1.10/1.25. Price $193.33.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -6.2% | 0.75 | Industrial capex downturn; volumes and margins compress together | $35.82 | 4.58% |
| Bear | 25% | -0.2% | 0.90 | Growth stalls to flat; the 2026 momentum fades | $55.27 | 5.98% |
| Base | 30% | 5.8% | 1.00 | Guided organic growth fades normally over the CAP | $78.84 | 7.72% |
| Bull | 25% | 10.8% | 1.10 | Current EPS-level growth persists; clean-energy/climate mix lifts margins | $106.59 | 9.67% |
| Super bull | 10% | 14.8% | 1.25 | Margin expansion + buybacks + M&A all compound at once | $142.66 | 12.01% |

- **Probability-weighted: IV@15% $81.97 (-57.6% vs price), IV@12% $109.21, IV@10% $139.63, weighted IRR 7.97%, base-case IRR 7.72%**
- **Tier by numbers: D.** Diagnostics (key_numbers.md): OE yield 4.33%, terminal value 19.0% of IV@15%, scenario spread 3.98x, net debt 2.89x normalized OE, 9.5 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (latest fiscal year ended 9 months ago — 9.5 months in the final run): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, quoted above with all its inputs.
- **NI_OCF_DIVERGENCE** (2024): identified — it is divestiture gains in net income, not a cash problem. FY2024 net income of $2,697,126,000 (financials_history.csv) includes the gains on Dover's 2024 dispositions: the Environmental Solutions Group sale (completed October 8, 2024, for $2.0B, preliminary pretax gain of $1.6B in discontinued operations), the De-Sta-Co sale (pretax gain of $530.3M) and a minority-investment sale (pretax gain of $67.4M) — per the FY2024 10-K. Those gains are non-operating and largely non-cash in the OCF sense; operating cash flow is on a continuing-operations basis. The conservative OE used throughout is built from OCF, so the gains do not contaminate the base. The maintenance definition is the distorted one in 2024 (it starts from net income), which is another reason the verdict rests on the conservative definition.
- **WIDE_SCENARIO_SPREAD** (preliminary run: super-bull IV 4.5x super-bear): on the final run the spread is 3.98x and the flag no longer fires, but the outcome range is still wide for an industrial — confidence is held at medium, not high, and the verdict below is sized to the weighted case, not the bull cases.
- **HIGH_NET_DEBT** (preliminary run: net debt 3.1x normalized OE): on the final run net debt is $3.328B, 2.89x normalized OE, and the flag no longer fires. Folded into the verdict explicitly: this is manageable leverage for a diversified cash generator, not a distress setup — but it means owner's earnings are levered, and even the bull and super-bull cases (which already carry that leverage) return only 9.67% and 12.01% at the current price. Leverage is not what breaks this stock; price is.

## My thoughts / overlay
- The method range is narrow and one-directional: the preliminary run (defaults, median base $7.79/share) gave weighted IRR 7.31% and weighted IV@15% $72.38; the final run (TTM base, growth recalibrated up to current prints) gives 7.97% and $81.97. Every defensible input set lands in Tier D. Even the super-bull scenario alone — 14.8% growth start, 1.25x OE — yields only a 12.01% IRR at $193.33, below the 15% hurdle.
- Quality is not the issue: OE positive 5/5 years, SBC small, buybacks shrinking the count, segment margins expanding, bookings growing double digits in Q2 2026, guidance raised. The issue is purely valuation: at an OE yield of 4.33% on the TTM base, there is no plausible growth path in this model that pays a 15% return.
- The price that clears 15% on the weighted case is the weighted IV@15% itself: **$81.97**. A buyer who wants a margin of safety on top of the hurdle needs to pay less than that. At $193.33 the market is pricing Dover as if much faster, much more durable growth than its 1.04% 3-year / 3.90% 5-year revenue record is already in hand.
- No tier override: the numbers tier and the qualitative picture agree.

## Final verdict
- **Final tier: D** (weighted IRR 7.97% on the v5 final inputs)
- Confidence: **Medium** (high on the OE base and the TTM inputs; the scenario spread of 3.98x and cyclical end-markets cap it there)
- One-liner: Quality diversified industrial compounder, moat 5/10, but at $193.33 it does not clear 15% — weighted IRR 7.97%, weighted IV@15% $81.97; it would need a price at or below $81.97 to clear the hurdle on the weighted case.
