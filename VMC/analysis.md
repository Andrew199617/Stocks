# VMC — Vulcan Materials Company
v5 run, 2026-10-14. Market cap $31.759B at $239.33 (nasdaq_quote_api) — in scope under $40B. All figures below are copied from dcf_numbers.json, ttm.py output (ttm.json), financials_history.csv, or key_numbers.md — none are recomputed.

## What it is
The largest U.S. producer of construction aggregates (crushed stone, sand, gravel), plus asphalt and ready-mixed concrete. Aggregates are a local, logistics-bound business: rock is heavy, transport costs dominate delivered price, and quarry permits are extremely hard to obtain, so permitted reserves near growing metros function as local monopolies. Demand splits between public infrastructure (highways — the stabilizer) and private residential/commercial construction (the cyclical part). FY2025: revenue $7,941M, +7.06% YoY (latest rev YoY, dcf_numbers.json); full-year aggregates shipments +3% (volume from late-2024 acquisitions more than offset slightly lower same-store shipments) and mix-adjusted aggregates pricing +6%, per the company's FY2025 results release. Q2 2026 (reported July 29, 2026): revenue $2.16B, +2.5% YoY, adjusted EPS $2.59 vs $2.42 in Q2 2025, aggregates shipments +1%, freight-adjusted price +4% (+5% mix-adjusted), aggregates cash gross profit per ton $12.02 vs $11.88 a year earlier — pricing held despite a large diesel/energy cost headwind and weather disruption; operating earnings fell and adjusted EBITDA was roughly flat YoY on those energy costs. Management reaffirmed FY2026 adjusted EBITDA guidance of $2.4–2.6B. In June 2026 the company divested its California ready-mixed concrete operations, continuing the shift toward a pure-play aggregates portfolio.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv / dcf_numbers.json):** operating cash flow $1,813,000,000; capex $677,700,000 (tag: PaymentsToAcquirePropertyPlantAndEquipment); SBC $63,100,000 (tag: ShareBasedCompensation — always a real cost, and small here).
- **Conservative owner's earnings FY2025: $1,072,200,000 = $8.08/share** (base_oe_total_latest_fy and base_oe_latest_per_share, dcf_numbers.json).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $586,000,000 for FY2025 (financials_history.csv) — well below the conservative figure, the gap being a large working-capital build in the ΔNWC column ($561,500,000). The conservative OCF-based figure is the standardized DCF input; the maintenance version is a reminder that FY2025 cash conversion was not as clean as the headline OE suggests.
- OE positive 5 of the last 5 fiscal years. Net debt $4,178,800,000 (dcf_numbers.json) — see HIGH_NET_DEBT under Flags.
- History shape: OE was depressed in FY2023 (conservative OE total $601,000,000, with capex spiking to $872,600,000 that year), recovered in FY2024 ($752,700,000), then jumped in FY2025 on OCF rising to $1,813,000,000 with capex back at $677,700,000. That path matters for the base choice below.

**Base used = TTM owner's earnings from ttm.py (filing-direct, no hand math), saved to ttm.json:**
- OCF: FY $1,813,000,000 − prior YTD (Q1 2025) $251,500,000 + current YTD (Q1 2026) $241,100,000 = **TTM $1,802,600,000**
- Capex: FY $677,700,000 − prior YTD $168,000,000 + current YTD $176,500,000 = **TTM $686,200,000**
- SBC: FY $63,100,000 − prior YTD $13,900,000 + current YTD $15,500,000 = **TTM $64,700,000**
- Shares (current-YTD weighted diluted): **131,200,000**
- **TTM OE total $1,051,700,000 → base OE/share $8.02** (ttm_oe_per_share $8.016006097560975; base_source: ttm_json)
- The engine's normalized base (3-yr median) is $5.66/share — rejected as the base; see BASE_DIVERGENCE under Flags. The TTM base essentially confirms the FY2025 level ($8.08 latest FY) rather than the median.

## Moat: 7/10 — strong
Justification: permitted quarry reserves in the right places are close to irreplicable — new quarry permits face years of community and environmental opposition, transport economics give each quarry a protected local radius, and Vulcan has proven pricing power through the cycle (mix-adjusted pricing +6% in FY2025, +4–5% in Q2 2026, cash gross profit per ton still rising through an energy-cost shock). That earns a strong score, not a wide one: the product is an undifferentiated commodity, volumes are hostage to the construction cycle and public budgets, and returns must carry a heavy, continuous capex load.
- FOR: permitted reserves are scarce and effectively irreplicable — permitting barriers create local monopolies around each quarry
- FOR: transport-cost economics — heavy, low-value rock means proximity to the job site, not brand, decides the sale, and Vulcan's network sits near high-growth U.S. metros
- FOR: proven pricing power — mix-adjusted aggregates price +6% FY2025 and +4–5% in Q2 2026, with cash gross profit per ton rising even against a major diesel headwind
- FOR: scale and density — No. 1 U.S. aggregates producer; public infrastructure demand (~highways) cushions private-cycle downturns
- FOR: long reserve life and an aggregates-led portfolio (California ready-mix divested June 2026) focused on the highest-return segment
- AGAINST: undifferentiated commodity product — the moat is location and permits, not the product; a permitted rival quarry in the same radius competes head-on
- AGAINST: cyclical volumes — residential weakness already bit in FY2025 (same-store shipments slightly lower; growth came from acquisitions), and private construction is rate-sensitive
- AGAINST: energy/diesel and labor cost exposure — Q2 2026 operating earnings fell despite price gains because energy costs compressed margins
- AGAINST: heavy continuous capex ($677,700,000 in FY2025) and acquisition dependence to sustain volume growth
- AGAINST: regulatory/environmental exposure runs both ways — the same permitting regime that protects Vulcan's quarries constrains its own expansions and operations
- A 7 gives CAP = 11.1 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 11.1 years, 15-year projection.

## DCF — v5 final run (2026-10-14)
Growth recalibration (written reason): the engine's blended growth is 8.92% (g_base), but its components are flattered — the OE/share CAGR (2y) component is 34.04%, an artifact of measuring off the capex-spike-depressed FY2023 base, and the 5-yr revenue CAGR is 10.33% against a 3-yr revenue CAGR of only 2.77%. The observable current prints are pricing-led mid-single digits: FY2025 revenue +7.06%, Q2 2026 revenue +2.5%, shipments guided/printing +1–3%, mix-adjusted pricing +5–6%. Scenario starts were therefore set via offsets (−0.11 / −0.07 / −0.03 / 0.00 / +0.04 vs g_base) to center the base case at 5.92% — between the revenue prints and FY2025's margin-expansion year, and deliberately below the engine blend. The super-bull start of 12.92% is far below the 34.04% OE CAGR component for the same artifact reason; no scenario start sits below a current print without that reason — volume +1–3% with price +5% supports the base start. Probabilities kept at the defaults 10/25/30/25/10 (no evidence strong enough to skew them; Q2 resilience and reaffirmed guidance argue against loading the bear side, cyclicality against loading the bull side); OE multipliers are the defaults 0.75/0.90/1.00/1.10/1.25. Base OE/share $8.02 (TTM), price $239.33.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -2.08% | 0.75 | Construction downturn: volumes fall, pricing sticks but operating leverage cuts OE | $39.76 | 4.41% |
| Bear | 25% | 1.92% | 0.90 | Weak housing/commercial, public work cushions; energy costs stay high | $57.56 | 5.48% |
| Base | 30% | 5.92% | 1.00 | Pricing-led compounding at current prints, modest volume growth | $77.26 | 6.71% |
| Bull | 25% | 8.92% | 1.10 | Engine-blend growth: infrastructure + data-center demand lifts volumes on top of pricing | $97.98 | 7.94% |
| Super bull | 10% | 12.92% | 1.25 | Sustained volume + pricing + margin expansion, acquisition engine compounding | $134.66 | 10.00% |

- **Probability-weighted: IV@15% $79.51 (−66.78% vs price), IV@12% $106.31, IV@10% $136.32, weighted IRR 6.87%, base-case IRR 6.71%**
- **Tier by numbers: D.** Diagnostics (dcf_numbers.json): OE yield 3.35%, terminal value 19.46% of IV@15%, scenario spread 3.39x, net debt 3.93x normalized OE, 9.43 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (latest fiscal year ended 9.43 months ago): resolved by construction — the base is the TTM figure from ttm.py (ttm.json, inputs quoted above; TTM OE/share $8.02), passed via --ttm in the final run, and Q2 2026 prints (revenue +2.5% YoY, adjusted EPS $2.59 vs $2.42) corroborate that the TTM run-rate held into mid-2026.
- **BASE_DIVERGENCE** (latest FY OE/share $8.08 vs 3-yr median $5.66): the median is the distorted one. It sits on FY2024 and averages in the recovery path from FY2023, when OE was depressed by a capex spike ($872,600,000 in FY2023 vs $677,700,000 in FY2025). FY2025's jump is OCF-driven ($1,813,000,000) on real pricing/volume prints, and the independently computed TTM base ($8.02) lands on the FY2025 level, not the median — two current, filing-derived measures agree, so the TTM base is used and the median is retained only in the reporting.
- **HIGH_NET_DEBT** (net debt $4,178,800,000, 3.93x normalized OE in the final diagnostics): real leverage against owner's earnings, and it is folded into the verdict two ways — the bear/super-bear cases carry OE multipliers of 0.90/0.75, which is where levered OE would compress first in a volume downturn, and no credit is taken for financial engineering in any scenario. Mitigants are qualitative, not numerical: the debt funds long-life permitted reserves, aggregates pricing has historically held through downturns, and public-sector demand cushions volumes. Even so, at this price the equity is priced far above every scenario's value, so leverage argues for more caution, not less.
- **WIDE_SCENARIO_SPREAD** (preliminary run: super-bull IV 4.5x super-bear): in the final run the spread is 3.39x — still wide in absolute terms, which is honest for a cyclical. Confidence is set to medium, not high, and the verdict below is sized to the fact that even the super-bull case fails the hurdle, so the spread does not change the tier.

## My thoughts / overlay
- The honest headline is how robust the tier is to method: the preliminary run on the (rejected) median base gave weighted IRR 6.14% and weighted IV@15% $64.73; the final TTM-base run gives 6.87% and $79.51. Both are Tier D by a wide margin. Even the super-bull scenario — 12.92% growth start, 1.25x OE — yields only a 10.00% IRR and an IV@15% of $134.66, far below the $239.33 price. This is a quality business at a price that already pays for the bull case several times over.
- Quality is not the debate: pricing power is proven, SBC is trivial ($64,700,000 TTM), the share count is roughly flat (share CAGR −0.23%/yr), and OE has been positive 5 of the last 5 years. The debate is purely price vs. a mid-single-digit pricing-led growth engine with heavy capex.
- Risks: a private-construction downturn (housing already soft), diesel/energy margin compression (visible in Q2 2026), acquisition-dependent volume growth, and the working-capital build that makes the maintenance OE definition ($586,000,000) much weaker than the conservative one ($1,072,200,000) for FY2025.
- Price that clears 15%: the weighted IV@15% is $79.51 — that is the price at which the weighted case earns Andrew's 15% hurdle. With any margin of safety the entry would need to be below that; the current $239.33 is roughly triple it, and even the super-bull IV@15% ($134.66) sits far below the market price.

## Final verdict
- **Final tier: D** (weighted IRR 6.87% on the v5 final inputs; Tier D under both the median-base and TTM-base methods — no defensible method range crosses a tier boundary)
- Confidence: **Medium** (high on the direction — every scenario fails 15% — medium on any single growth path given the 3.39x scenario spread and cyclical OE history)
- One-liner: Strong-moat aggregates compounder (moat 7/10) with proven pricing power, but at $239.33 it prices in far more than even the super-bull case delivers — weighted IRR 6.87%, weighted IV@15% $79.51; it would only clear the 15% hurdle at or below $79.51.
