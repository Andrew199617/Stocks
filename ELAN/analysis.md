# ELAN — Elanco Animal Health Incorporated
Engine 5.4 run, 2026-10-18. In scope (market cap $11.69B at $23.55, nasdaq_quote_api).

All figures below are copied from dcf_numbers.json, ttm.json, fundamentals.json, or financials_history.csv — none are recomputed.

## What it is
Animal-health pharmaceuticals, spun out of Eli Lilly (independent 2019) and scaled by the 2020 Bayer Animal Health acquisition. Two product categories, near-evenly split in FY2025: Pet Health (49% of revenue — parasiticides, dermatology, vaccines, pain/therapeutics) and Farm Animal (50% — efficiency, disease prevention, food safety). U.S. is 47% of revenue; sold in 90+ countries. The current growth story is the innovation portfolio — Zenrelia (JAK inhibitor for dogs, now its newest blockbuster) and Credelio Quattro (parasiticide chewable) — with FY2026 innovation revenue targeted at $1.25B. No dividend, no buybacks (fundamentals.json: dividends/buybacks never filed — zero by the filer's own statements); all free cash goes to debt reduction.

## Owner's earnings
**FY2025 (10-K via EDGAR, financials_history.csv):** OCF $560M; capex $276M (a step-up from $147M in FY2024 — capacity investment; TTM capex is still elevated at $238M); SBC $68M (always a real cost).
- **Conservative OE FY2025: $216M = $0.44/share** (OCF − capex − SBC).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $288M — same ballpark.
- OE positive 5 of the last 5 fiscal years, but volatile: OE/share ran $0.53 (2021), $0.45 (2022), $0.17 (2023), $0.68 (2024), $0.44 (2025).
- Engine normalized base (median of last 3 FY OE/share) = $0.435/share. The FY2024 figure ($0.68) is flattered by the aqua divestiture year (gain on sale to Merck Animal Health) and FY2023 ($0.17) is depressed — the median is a fair middle, but it is ~10 months stale.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $560M − prior YTD $233M + current YTD $290M = **TTM $617M**
- Capex: FY $276M − prior YTD $122M + current YTD $84M = **TTM $238M**
- SBC: FY $68M − prior YTD $35M + current YTD $41M = **TTM $74M**
- Shares (current-YTD weighted diluted): **505.9M**
- **TTM OE total $305M → base OE/share $0.60** (base_source: ttm_json)
- The TTM base is the right one: H1 2026 execution is real (Q2 2026 revenue $1.368B, +10.2% YoY, +8% organic constant currency; FY2026 guidance raised to revenue $5.09–5.14B, 6–7% organic CC growth, adjusted EBITDA $1.01–1.035B, adjusted EPS $1.10–1.16). Even on this higher base the stock fails the hurdle by a wide margin — see verdict. Method range: on the normalized median base ($0.435) the preliminary run gave weighted IRR 5.03% / IV@15% $4.48; on the TTM base, 5.62% / $5.66. Both are Tier D; the base choice does not change the verdict.

## Moat: 4/10 — weak-to-moderate
Justification: a real #2/#3 franchise with brands and vet-channel reach, but it plays behind Zoetis's scale, its purchased portfolio keeps taking impairments, and measured returns on capital are weak.
- FOR: Established brands across pet and farm animal with veterinarian-channel relationships in 90+ countries; innovation pipeline actually delivering (Zenrelia the single largest contributor to global growth in Q2 2026, Credelio Quattro in >50% of U.S. clinics); reported gross margin stable in the mid-50s for five straight years (55.2% / 56.6% / 56.3% / 54.9% / 55.0% FY2021–25, fundamentals.json) with adjusted gross margin expanding (58.1% in Q2 2026); diversified revenue — no single product or geography dominates (Pet 49% / Farm 50%, U.S. 47%).
- AGAINST: #2/#3 position behind Zoetis, which outspends it on R&D and owns the category's strongest franchises; the Bayer acquisition's purchased moat keeps eroding on paper — $1,042M goodwill impairment in 2023, a further $47M marketed-product intangible impairment in 2025; legacy parasiticide brands face generic erosion; farm-animal half of revenue rides livestock cycles and producer economics; GAAP returns on capital are poor — roic_proxy is not computable from the computed outputs (Elanco files no operating-income tag in the merged EDGAR facts; engine used_tags operating_income: null), and the visible evidence is five years of GAAP net losses in 3 of them (2021, 2023, 2025) under ~$680M/yr of acquisition amortization; leverage (~3.1x net debt / adjusted EBITDA per Q2 2026 release) constrains investment.
- A 4 gives CAP = 7.2 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 7.2 years, 15-year projection.

## DCF — engine 5.4 final run (2026-10-18)
Growth sanity check: the engine's blended start is 6.35% (5-yr rev CAGR 7.58%, 3-yr 2.25%, latest FY YoY 6.22%, OE/share CAGR 2y 58.7% off the depressed 2023 base — an artifact, entering the blend unadjusted per v5.4). Against actual prints — FY2025 revenue +6.2%, Q2 2026 +10.2% reported / +8% organic CC, FY2026 guidance 6–7% organic CC — the base start of 6.35% sits right on guidance. Bull starts at 11.35%, modestly above the best recent print (Q2's +10.2%), defensible only because OE can outgrow revenue via the Elanco Ascend productivity program and deleveraging; super bull at 18.35% is above any printed revenue growth and is priced as a 10% tail, not a plan. Probabilities shifted toward the bear side per the OE_VOLATILE flag: 15/30/30/15/10; OE multipliers at defaults 0.75/0.90/1.00/1.10/1.25. Price $23.55.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | −5.7% | 0.75 | Generic erosion + farm downturn; levered OE squeezed | $2.70 | 3.81% |
| Bear | 30% | 1.3% | 0.90 | Innovation offsets legacy decline only; margins stall | $4.26 | 4.74% |
| Base | 30% | 6.3% | 1.00 | Guidance-level growth, fades over 7.2-yr CAP | $5.73 | 5.63% |
| Bull | 15% | 11.3% | 1.10 | Zenrelia/Quattro blockbusters + Ascend savings land | $7.61 | 6.77% |
| Super bull | 10% | 18.3% | 1.25 | Category-killer path; sustained double-digit OE growth | $11.21 | 8.86% |

- **Probability-weighted: IV@15% $5.66 (−76.0% vs price), IV@12% $7.53, IV@10% $9.61, weighted IRR 5.62%, base-case IRR 5.63%**
- **Tier by numbers: D** — and bear and bull tiers are both D, so there is no band ambiguity. Even the super-bull IV@15% ($11.21) is less than half the $23.55 price.
- Diagnostics (dcf_numbers.json): TTM OE yield 2.56%, terminal value 18.8% of IV@15%, scenario spread 4.15x, net debt 11.6x normalized OE, 9.6 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended ~10 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, legs quoted above.
- **OE_VOLATILE** (OE/share spans >3x over 5 years: $0.17–$0.68): real — impairment/restructuring years and the divestiture year. Handled with the TTM base plus bear-shifted probabilities (45% on bear-or-worse).
- **NI_OCF_DIVERGENCE** (2023, 2025): both identified, both non-cash impairment stories, neither touches the OCF-based base. 2023: GAAP net loss −$1,231M vs OCF $271M — the $1,042M non-cash goodwill impairment in Q3 2023 (primarily higher long-term treasury rates on the Bayer reporting unit, per the Q3 2023 release). 2025: net loss −$232M vs OCF $560M — $237M of adjustments per the FY2025 release: $155M of 2025 Restructuring Plan charges, a $47M marketed-product intangible impairment, $16M of impairments on two suspended capital projects, plus October 2025 refinancing costs. OCF is the clean leg in both years.
- **SHARES_FALLBACK** (2016): no diluted count filed for 2016 (pre-spin Lilly carve-out year) — that year's per-share history uses the basic count and is approximate. It feeds no base or growth input that matters (the blend's OE/share CAGR is 2-yr).
- **WIDE_SCENARIO_SPREAD** (4.15x): real — the range is wide because the base OE yield is only 2.56% and everything rides on growth. Confidence capped at medium; verdict sized to the conservative end (which changes nothing here — every scenario is Tier D).
- **HIGH_NET_DEBT** (11.6x normalized OE): from the filing (financials_history.csv): total debt $4,017M vs cash $545M at FY2025 = net debt $3,472M, plus $124M lease liabilities. On the company's own adjusted-EBITDA yardstick that is ~3.1x (Q2 2026 release) with a ~3.0x year-end target — manageable for the business, but on owner's earnings the leverage is heavy, and debt paydown is the first claim on the OE stream equity holders are pricing.
- **LOW_OE_YIELD** (preliminary run, on the median base): 1.85% there, 2.56% on the TTM base — the flag's point stands either way: at $23.55 the valuation rests almost entirely on future growth, with almost no current cash yield underneath it.

## My thoughts / overlay
- The gap between the market price and owner's earnings is the whole story. The Street prices adjusted EPS ($1.10–1.16 guided for 2026); the OE definition here charges full capex ($238M TTM and still elevated from the capacity build) and SBC, and sits behind $3.47B of net debt. Even granting the TTM base and guidance-level growth, weighted IV@15% is $5.66 — the price would need to fall ~76% to clear a 15% hurdle ($5.66), ~83% for 20% ($3.99), ~87% for 25% ($3.06).
- This is not a broken business: revenue inflected from flat (2022–24, ~$4.4B, including the aqua divestiture drag) to +6.2% in FY2025 and +10.2% in Q2 2026, margins are expanding on an adjusted basis, and leverage is falling. It is a decent business at a price that already pays for the turnaround and then some.
- Watch items: whether capex normalizes back toward the ~$150M/yr pre-2025 run-rate once capacity projects finish (that alone would lift OE/share materially); Zenrelia/Quattro durability against Zoetis's competing dermatology/parasiticide launches; and whether GAAP results ever escape the restructuring/impairment cycle that has hit 2023, 2024 ($44M restructuring + $53M IPR&D impairment) and 2025 in succession — "one-offs" three years running are a cost of this business model, which is why the OE base keeps them in via OCF.
- Data note (non-blocking): fundamentals.json carries no roic_proxy series for ELAN (no operating-income tag in the merged facts), so the moat rests on the gross-margin series and the impairment record instead. Enrichment steps were run after scoring per spec.

## Final verdict
- **Final tier: D** (weighted IRR 5.62% on the TTM base; 5.03% on the normalized median base — Tier D on every defensible base and in every scenario)
- Confidence: **Medium** (high on the direction — the gap to the hurdle is ~4x — capped by the 4.15x scenario spread and the missing ROIC series)
- One-liner: Improving #2 animal-health franchise, moat 4/10 — real innovation-led growth (Q2 2026 +10.2%) but owner's earnings of $0.60/share TTM against $3.47B net debt cannot support $23.55; clears 15% only under ~$5.66.
