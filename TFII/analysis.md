# TFII — TFI International Inc.
Engine 5.5 run, 2026-10-20. Canadian 40-F (IFRS) filer; SIC 4210 Trucking & Courier Services. Price $111.59 (nasdaq_quote_api), market cap $9.308B — in scope (<$40B).

All figures below are copied from key_numbers.md, dcf_numbers.json, financials_history.csv, fundamentals.json or the cited Q2 2026 release — none are recomputed.

## What it is
North American transportation and logistics group built by acquisition: Less-Than-Truckload (anchored by TForce Freight, the former UPS Freight), Truckload (including Daseke, North America's largest flatbed/specialized carrier), Package and Courier, and Logistics. Headquartered in Saint-Laurent, Québec; common shares listed directly on NYSE and TSX under TFII (no ADS). Management has announced an intention to redomicile to the U.S. and has discussed a possible separation of the Daseke/truckload business — neither is in the numbers.

## Owner's earnings
**FY2025 (40-F via EDGAR, from financials_history.csv):** operating cash flow $977,788,000; capex $282,923,000 (rollup: PP&E $273.2M + intangibles $9.7M); SBC $15,148,000 (always a real cost, though small here).
- **Conservative owner's earnings FY2025: $679,717,000 = $8.15/share** (latest FY OE/share $8.15 in key_numbers.md; latest FY OE total $679.7M).
- Maintenance version (from financials_history.csv): $699,015,000 — same ballpark as the conservative figure.
- OE/share for the base window: FY2023 $7.31, FY2024 $7.65, FY2025 $8.15. **Base used = median of last 3 FY OE/share: $7.65** (base_source: median_of_last_3_fy_oe_per_share). OE positive 5 of the last 5 fiscal years.
- No TTM base: TFII is an IFRS 40-F filer with no 10-Qs; ttm.py reads us-gaap facts only and could not compute a TTM (it reported no annual FY fact under its candidate tags, and fundamentals.json warns no quarterly facts could be assembled for this filer). Per the worker spec, the median base is used for IFRS filers. Interim evidence does not argue the median is stale-low: the Q2 2026 release (company press release, July 27, 2026) shows H1 2026 net cash from operating activities of $377.1M vs $440.2M in H1 2025 — interim cash generation ran below the prior year even as operating income recovered.
- Balance sheet (latest FY, financials_history.csv / dcf_numbers.json): cash $210,186,000; debt current $222,498,000; debt long-term $2,355,477,000; **net debt $2.368B**, i.e. 3.71x normalized OE. Lease liabilities of $637,764,000 sit on top of that and are not in the engine's net debt.

## Moat: 4/10 — weak-to-narrow
Justification: scale and a proven decentralized acquisition platform in a fragmented industry, but freight is a commodity with low switching costs, and returns have compressed straight through the cycle.
- FOR: one of North America's largest trucking groups and the largest flatbed/specialized carrier via Daseke, with LTL terminal-network density from TForce Freight (ex-UPS Freight); the decentralized acquisition platform under Alain Bédard — decades of buying fragmented carriers, keeping local operators, improving operating ratios; diversification across LTL, Truckload, Logistics and Package & Courier and across industrial end markets.
- AGAINST: commodity freight with low shipper switching costs and a deep rival set (Old Dominion, XPO, ArcBest, FedEx Freight); returns compression — see ROIC below; cyclical and cost-exposed (unionized U.S. LTL workforce, driver/purchased-transportation cost pressure flagged into Q3 2026); acquisition-led model carries leverage (3.71x) and execution risk (Daseke integration/separation, planned redomiciliation).
- Evidence (fundamentals.json): ROIC proxy (after-tax operating income over equity + debt − cash) by FY: 2019 11.7%, 2020 11.9%, 2021 20.9%, 2022 24.4%, 2023 13.7%, 2024 10.7%, **2025 8.6%** — a clear downtrend from the freight-cycle peak to roughly the cost of capital. Operating margin: 13.6% (2021), 13.0% (2022), 10.1% (2023), 8.6% (2024), 7.2% (2025). Gross margin is not separable in this IFRS presentation (fundamentals.json files no COGS/gross-profit split), so operating margin is the margin evidence. A 4/10 sits on that record: no pricing power that survives a freight recession.
- A 4 gives CAP = 7.2 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 7.2 years, 15-year projection.

## DCF — final run (2026-10-20)
Growth sanity check (mandatory): the engine blend is 2.46% (rev CAGR 5y 15.84% — rejected as a basis-break artifact, see BASIS_BREAK below; rev CAGR 3y -3.64%; latest rev YoY -6.10%; OE/share CAGR 2y 5.60%; share-count adjustment +2.95pp applied to revenue components only). Recent prints: FY2025 revenue fell 6.10%; Q2 2026 total revenue rose 12.4% YoY to $2,289.9M but revenue **before fuel surcharge** rose only ~6% ($1,900.0M vs $1,794.0M, Q2 2026 release), and management guided Q3 2026 EPS ($1.70–1.80) below Q2's $1.85 print. The base start of 2.5% sits **below** the latest ex-fuel print for a written reason: the recovery is one quarter old, FY2025 was still down, and H1 2026 operating cash flow fell YoY. The bull start (7.5%) is in line with the ex-fuel Q2 print; the super-bull start (14.5%) exceeds any recent organic print and is carried only at 10% probability as a full freight-recovery-plus-accretion case. Default probabilities 10/25/30/25/10, default offsets −12/−5/0/+5/+12pp, default OE multipliers 0.75/0.90/1.00/1.10/1.25 were kept — the evidence supports the default shape, with the verdict sized to the bear end per TIER_BAND.

| Scenario | Prob | Growth start | OE mult | IV@15 | IRR |
|---|---|---|---|---|---|
| Super bear | 10% | -9.5% | 0.75 | $29.40 | 5.45% |
| Bear | 25% | -2.5% | 0.90 | $46.46 | 7.54% |
| Base | 30% | 2.5% | 1.00 | $62.66 | 9.52% |
| Bull | 25% | 7.5% | 1.10 | $83.44 | 11.95% |
| Super bull | 10% | 14.5% | 1.25 | $123.30 | 16.19% |

- **Probability-weighted: IV@15% $66.54 (−40.4% vs price), IV@12% $87.95, IV@10% $111.77, weighted IRR 10.01%, base-case IRR 9.52%.**
- **Tier by numbers: C.** Diagnostics (key_numbers.md): OE yield 6.86%, terminal value 18.2% of IV@15%, scenario spread 4.19x, net debt 3.71x normalized OE, 9.6 months since FY end.
- Hurdle-clearing prices (weighted path): 15% at $66.54, 20% at $47.24, 25% at $36.55. The current $111.59 price clears only a ~10% discount rate on the weighted path.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.6 months ago): no TTM is buildable — IFRS 40-F filer, ttm.py reads us-gaap only and returned no TTM (see Owner's earnings). The median-of-3-FY base is used per spec for IFRS filers, and the interim check (H1 2026 OCF $377.1M vs $440.2M H1 2025, Q2 2026 release) gives no evidence the median understates current cash generation.
- **BUYBACK_TAILWIND** (share count shrinking 3.0%/yr; key_numbers.md: share count CAGR −2.95%): already credited via the +2.95pp growth adjustment in the blend; not double-counted in the verdict.
- **BASIS_BREAK_SUSPECT**: named — the UPS Freight acquisition (closed April 2021, $800M) is the >60% jump: revenue $3,781,134,000 (FY2020) → $7,220,429,000 (FY2021). The Daseke acquisition (closed April 2024, ~$1.1B including debt) likewise inflates FY2024 growth, and CFI's truckload business was sold in 2022. The 5y revenue CAGR (15.84%) straddles these breaks and was not used to set growth starts; starts rest on the 3y CAGR, latest YoY, OE/share CAGR and the 2026 prints (see the sanity check above).
- **NI_OCF_DIVERGENCE** (2023, 2024, 2025): D&A-explained, not a one-off. Net income was $504,877,000 / $422,484,000 / $310,553,000 against OCF of $1,013,839,000 / $1,062,651,000 / $977,788,000 (financials_history.csv), while depreciation & amortisation — the non-cash fleet charge added back in OCF — was $441,975,000 / $582,069,000 / $610,504,000 in the same years, more than covering each gap. The base is OCF-built throughout, so the divergence does not contaminate it; the falling net-income line itself is the margin story told under Moat.
- **ADS_RATIO_APPLIED**: resolved with judgment.json `ads_ratio` ratio 1.0, kind filing-equivalent declaration — the 40-F cover (FY2025, filed 2026-02-17) registers "Common Shares", symbol TFII, on the New York Stock Exchange, and states 84,408,437 common shares outstanding (matching the engine's dei count of 84,408,437). The NYSE security is the common share itself (dual-listed on TSX), not an ADS, so no scaling applies and market cap is price × shares ($9.308B).
- **WIDE_SCENARIO_SPREAD** (4.19x): real — a levered cyclical at a cycle turn has a wide outcome range. Confidence is capped at low and the verdict is sized to the conservative end.
- **HIGH_NET_DEBT** (3.71x normalized OE): balance sheet stated above from the filing — $2.368B net debt plus $637,764,000 of lease liabilities. The bear and super-bear cases (OE multipliers 0.90 / 0.75, IRRs 7.54% / 5.45%) are the stress the flag asks for; at those OE levels leverage is the difference between a bad year and an equity problem.
- **TIER_BAND** (bear D 7.54% vs bull C 11.95%): the verdict spans tiers, so it is sized to the bear end — the one-liner and final verdict below are written off the bear case, not the weighted midpoint.

## Data / enrichment notes
- fundamentals.json: no quarterly facts (40-F filer) — TTM/dividend-per-share fields null by construction; FY2025 cash dividends paid $151.1M is filed on the total dividends line.
- segments.py printed a KeyError ('segments') in its summary step, but segments.json was written and parses — treated as produced; segment colour above comes from the company's reported segment structure in the Q2 2026 release. prices.py, statements.py and profile.py ran in the enrichment pass.

## My thoughts / overlay
- The market is pricing the freight recovery, not the current owner's earnings: at $111.59 the stock trades at roughly the weighted IV@10% ($111.77) — a buyer accepts a ~10% expected return on the weighted path, ~7.5% if the bear case (freight recession extends, LTL costs bite) is what arrives.
- The bull ingredients are real and visible in Q2 2026: operating income up ~30% YoY in the quarter, Truckload operating income up 50%, LTL pricing discipline improving. What is missing is evidence the recovery restores through-cycle returns: ROIC has fallen for three straight years to 8.6% and H1 2026 operating cash flow fell even as operating income rose.
- Method range: the verdict is not assumption-fragile in the usual direction — even the bull case (11.95%) and the super-bull case at 10% weight (16.19%) leave the weighted result at 10.01%; the stock would need the super-bull path as the *base* case to clear 15% at this price. It clears 15% at $66.54.

## Final verdict
- **Final tier: C** (weighted IRR 10.01%; bear D 7.54% → bull C 11.95%)
- Confidence: **Low** (WIDE_SCENARIO_SPREAD, no buildable IFRS TTM, cycle-turn uncertainty)
- One-liner: North American trucking consolidator, moat 4/10 — Tier C: weighted IRR 10.0%, IV@15% $66.54 vs $111.59 price; does not clear the 15% hurdle until ~$67, and with the bear case at 7.5% (Tier D) any position should be sized to the bear end.
