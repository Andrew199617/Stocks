# DG — Dollar General Corp
v5 run, 2026-10-14. In scope (market cap $28.73B at $130.10, nasdaq_quote_api).

All figures below are copied from dcf_numbers.json, ttm.py output, or financials_history.csv — none are recomputed.

## What it is
The largest US small-box discount retailer: ~20,900 stores, concentrated in rural and small-town markets (towns under 20k people), selling mostly low-ticket consumables plus seasonal/home/apparel at everyday low prices. Mid-turnaround under returned CEO Todd Vasos ("Back to Basics": shrink reduction, inventory/SKU cuts, store standards) after the FY2023–24 margin collapse.

## Owner's earnings
**Latest FY (ended 2026-01-30, from financials_history.csv):** operating cash flow $3,634,500,000; capex $1,241,162,000 (tag: PaymentsToAcquireProductiveAssets); SBC $91,453,000 (a real cost, but small for a retailer this size).
- **Conservative owner's earnings latest FY: $2,301,885,000 = $10.42/share** (base_oe_latest_per_share, dcf_numbers.json)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $2,076,791,000 — same ballpark, raises confidence in the OCF-based figure.
- OE positive 5 of the last 5 fiscal years, but the path was violent: conservative OE totals ran $351,261,000 (FY2023) → $639,685,000 (FY2024) → $1,627,438,000 (FY2025) → $2,301,885,000 (latest FY) — the shrink/inventory crisis and its recovery, not steady compounding.
- Balance sheet: the engine's net_debt_latest is null (latest-FY debt tags incomplete in the companyfacts pull), and Dollar General also carries substantial operating-lease obligations this engine does not capture — no net-debt figure is quoted rather than a hand-built one. This is a leased-store retailer; treat the equity as more leveraged than the OE yield alone suggests.

**Base used = TTM owner's earnings through Q2 FY2026 (ended 2026-07-31), from ttm.py (filing-direct, no hand math):**
- OCF: FY $3,634,500,000 − prior YTD $1,814,855,000 + current YTD $1,496,705,000 = **TTM $3,316,350,000**
- Capex: FY $1,241,162,000 − prior YTD $693,918,000 + current YTD $758,450,000 = **TTM $1,305,694,000**
- SBC: FY $91,453,000 − prior YTD $52,977,000 + current YTD $61,213,000 = **TTM $99,689,000**
- Shares (current-YTD weighted diluted): **221,532,000**
- **TTM OE total $1,910,967,000 → base OE/share $8.63** (base_source: ttm_json)
- Why TTM over the alternatives: the 3-yr median ($7.40/share) is dragged by the FY2024 trough year, and the latest FY ($10.42/share) is a recovery year flattered by a strong H2 and tariff refunds (Q2 FY26 GAAP EPS included ~$0.25 of tariff-refund benefit that management says will not repeat in H2). The TTM figure sits between them and already reflects the softer H1 FY27 cash flow (current-YTD OCF $1,496,705,000 vs prior-YTD $1,814,855,000).

## Moat: 5/10 — moderate/narrow
Justification: real proximity and scale advantages in rural small towns, but no pricing power over Walmart, no switching costs, and a customer whose wallet is the constraint.
- FOR: store density and proximity — ~20,900 small-box stores embedded in rural/small-town markets where a Walmart supercenter trip is the alternative, and trip frequency on consumables rewards being closest; purchasing scale across that fleet; growing private-brand penetration; a low-cost operating model that is hard to undercut at this ticket size.
- AGAINST: Walmart competes on the same value customer with deeper pockets and is investing in price and convenience; Dollar Tree/Family Dollar and Amazon pressure the same basket; zero customer switching costs; mix is dominated by low-margin consumables; chronic shrink and store-condition/labor issues are what broke earnings in FY2023–24 and can recur; core low-income customer is squeezed by fuel/food inflation (management itself flagged pressure spreading to $100k households).
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — v5 final run (2026-10-14)
Growth sanity check: the engine's blended growth is 5.01% and g_base is 5.83% — the median blend neutralized the oe_ps_cagr_2y artifact (89.74%, off the FY2024 trough) and rests on the revenue signals (5-yr CAGR 4.83%, 3-yr 4.14%, latest YoY 5.20%). Against actual prints: FY2026 guidance (raised at Q2) is net sales +4.0–4.3% and same-store sales +2.5–2.9%, with EPS guided to $7.80–8.00. The base start (5.8% OE/share growth) sits modestly above the sales guide because margin recovery (shrink, damages) and buybacks (up to $700M planned in H2) add per-share leverage — that is the recovery story, and it is guided, not assumed. The super-bull start (17.8%) is BELOW the latest recovery prints (Q2 EPS +33% YoY; latest-FY OE/share up sharply off the trough) — deliberately: those prints are recovery-off-a-trough plus a non-repeating tariff refund, and management guided margin expansion in FY2026 to be "much lesser" than FY2025 with shrink gains decelerating. Default offsets (−12/−5/0/+5/+12pp) and multipliers (0.75/0.90/1.00/1.10/1.25) kept; probabilities at defaults 10/25/30/25/10. Price $130.10.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -6.2% | 0.75 | Shrink/store problems relapse; Walmart takes share; OE falls back toward trough economics | $36.91 | 5.73% |
| Bear | 25% | 0.8% | 0.90 | Recovery stalls at sales-guide growth with no further margin gains | $59.38 | 8.14% |
| Base | 30% | 5.8% | 1.00 | Guided path: low-single-digit comps, gradual margin repair, buybacks | $81.24 | 10.42% |
| Bull | 25% | 10.8% | 1.10 | Shrink gains and remodels keep compounding; mix shifts to higher-margin nonconsumables | $109.84 | 13.19% |
| Super bull | 10% | 17.8% | 1.25 | Full Vasos-era restoration of historical margins plus sustained traffic gains | $166.04 | 17.94% |

- **Probability-weighted: IV@15% $86.97 (−33.2% vs price), IV@12% $116.11, IV@10% $148.67, weighted IRR 11.02%, base-case IRR 10.42%**
- **Tier by numbers: C.** Diagnostics (dcf_numbers.json): OE yield 6.63%, terminal value 19.2% of IV@15%, scenario spread 4.50x, 8.4 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 8.4 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 FY2026, quoted above.
- **BASE_DIVERGENCE** (latest FY $10.42 vs 3-yr median $7.40): BOTH are distorted in opposite directions — the median averages in the FY2024 shrink-crisis trough, the latest FY is a recovery year flattered by tariff refunds. TTM base ($8.63) used as the filing-derived middle; the spread between the three bases is itself the honest uncertainty here.
- **OE_VOLATILE** (OE/share spans >3x over 5 years): real and explained — FY2023–24 shrink/inventory crisis, then recovery. Handled by the TTM base plus full default bear/super-bear weight (35% combined) rather than pretending the recovered level is a stable run-rate.
- **NI_OCF_DIVERGENCE** (2025, 2026): explained by non-cash D&A ($971,703,000 in FY2025; $1,046,318,000 in latest FY, financials_history.csv) plus working-capital release from the inventory-reduction program (delta_nwc was a source of cash in both years). No tax-deposit or impairment one-off found; the OCF-based conservative OE is the series used throughout, so the divergence does not contaminate the base.
- **WIDE_SCENARIO_SPREAD** (4.50x): real — the outcome hinges on whether recovered margins hold. Confidence is capped at medium, and the verdict is sized to the conservative end.

## My thoughts / overlay
- The turnaround is real (Q2 FY26: sales +5.2%, SSS +3.5% on +2.0% traffic, gross margin +127bps, guidance raised) — but the market has already paid for it. At $130.10 the stock trades above even the bull scenario's IV@15 ($109.84); only the super-bull path (10% weight) justifies today's price at a 15% discount rate.
- Method range: the same engine on the 3-yr median base ($7.40) gave a weighted IRR of 9.85% (Tier D territory) in the preliminary run; on the TTM base it is 11.02% (Tier C). Defensible bases span D→C — no defensible base gets this price to the 15% hurdle.
- Quality notes: SBC is immaterial ($99.7M TTM), share count is roughly flat (share_cagr −0.82%/yr, mild buyback tailwind already in the blend via the +0.82pp adjustment), capex is heavy and real (TTM $1,305,694,000 — remodels, new stores, supply chain), so the conservative OE definition is the right one here.
- Risks: tariff-refund benefit does not repeat in H2 FY26 (management's own statement); fuel costs flagged as much higher than anticipated; CEO transition risk (Vasos succession is a live topic in coverage); lease leverage not captured in the engine's net-debt field.
- Hurdle math: the price that clears 15% on the weighted case is the weighted IV@15 itself, **$86.97** — roughly a third below today's price. Even with no extra margin of safety, DG does not clear Andrew's hurdle here; with a margin of safety against the bear case ($59.38 IV@15), an entry would need to be lower still.

## Final verdict
- **Final tier: C** (weighted IRR 11.02% on the v5 final inputs; defensible-base range D→C)
- Confidence: **Medium** (capped by the 4.50x scenario spread; high on the filing data itself — no gaps, no overrides)
- One-liner: Genuine turnaround at a narrow-moat rural discounter, but $130 already prices in the recovery — weighted IRR 11.0%, IV@15 $87; clears 15% only below ~$87.
