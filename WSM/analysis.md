# WSM — Williams-Sonoma, Inc.
v5 run, 2026-10-14. In scope (market cap $29.536B at $239.84, nasdaq_quote_api — key_numbers.md).

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.json, or financials_history.csv — none are recomputed. Quarterly/guidance facts are from cited web search results on the Q2 FY2026 report (Aug 26, 2026).

## What it is
Premium specialty home-furnishings retailer: Pottery Barn, West Elm, Williams Sonoma, Pottery Barn Kids/Teen, Rejuvenation, Mark & Graham, GreenRow and other banners — the largest omnichannel player in a highly fragmented category where no competitor holds more than ~5% (2026 investor presentation via search). Digital-first but not digital-only, in-house design, an affluent customer base, plus a B2B arm that grew 14.5% in Q2 FY2026. Latest quarter (Q2 FY2026, ended 2026-08-02, per search of the earnings report): net revenue $1.96B, +6.7% YoY; comparable brand revenue +6.2% with every brand positive; non-GAAP EPS $2.10; non-GAAP operating margin 17.3%. Management raised FY2026 guidance to net revenue growth +4.7% to +7.2%, comps +4.0% to +6.5%, non-GAAP operating margin 17.8% to 18.2% — assuming current tariffs stay in place and excluding any further tariff refund benefit.

## Owner's earnings
**FY2026 (10-K via EDGAR, financials_history.csv):** operating cash flow $1,314,889,000; capex $259,438,000 (tag PaymentsToAcquirePropertyPlantAndEquipment); SBC $106,522,000 (tag ShareBasedCompensation — always a real cost).
- **Conservative owner's earnings FY2026: $948,929,000 = $7.71/share** (latest FY OE/share, key_numbers.md)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $978,839,000 (financials_history.csv) — close to the conservative figure, which supports the base.
- OE positive 5 of the last 5 fiscal years. Balance sheet: cash $1,019,801,000 at FY2026 (financials_history.csv) and no debt figures filed in the history (debt_current / debt_lt blank; engine net debt is null) — search coverage of Q2 FY2026 likewise describes a debt-free balance sheet with buyback capacity remaining. No HIGH_NET_DEBT / BIG_NET_CASH flag was raised; the balance sheet is a quality plus, not a valuation driver at this price.
- History caveat: OE is working-capital volatile (see NI_OCF_DIVERGENCE under Flags) — FY2024 conservative OE was flattered by a large working-capital release, and the COVID-boom years sit well above the recent run rate.

**Base used = TTM owner's earnings through Q2 FY2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $1,314,889,000 − prior YTD $401,678,000 + current YTD $695,862,000 = **TTM $1,609,073,000**
- Capex: FY $259,438,000 − prior YTD $110,293,000 + current YTD $116,434,000 = **TTM $265,579,000**
- SBC: FY $106,522,000 − prior YTD $46,974,000 + current YTD $61,530,000 = **TTM $121,078,000**
- Shares (current-YTD weighted diluted): **119,375,000**
- **TTM OE total $1,222,416,000 → base OE/share $10.24** (base_source: ttm_json)
- Caution on this base: it is an *upper* bound. Q2 FY2026 reporting (via search) shows the company collected substantially all of an initial ~$197.8M IEEPA tariff refund claim by 2026-08-02 and booked a large refund benefit that GAAP results include and non-GAAP results exclude; cash collected in the TTM window flatters TTM operating cash flow. No adjusted figure is computed here (the computed outputs do not provide one) — instead the verdict is sized conservatively: even on this flattering base the stock is Tier D, and the engine's normalized base (3-yr median) is lower at $8.12/share, which would score worse. The conclusion does not depend on the refund question.

## Moat: 5/10 — moderate / narrow
Justification: durable premium brands and best-in-class operations in a fragmented category, but no network effects, low switching costs, housing-cycle demand, and tariff-exposed sourcing.
- FOR: Premium brand portfolio (Pottery Barn, West Elm, Williams Sonoma) with in-house design; largest omnichannel specialty home-furnishings player in a fragmented market, gaining share in a flat industry; affluent (~$150k income) customer base, relatively resilient through cycles; proven pricing power / full-price selling, operating margin up sharply vs pre-pandemic; debt-free balance sheet, strong cash generation funding buybacks + rising dividend; B2B segment growing double digits (14.5% in Q2 FY2026), diversifying beyond housing turnover.
- AGAINST: No network effects, low switching costs; fragmented competition (Wayfair, RH, Amazon, IKEA/mass); housing-cycle and big-ticket discretionary exposure — revenue fell in FY2023–24 when housing froze (rev CAGR 3y −3.44%); tariff/sourcing exposure on imported goods (Q2 FY2026 gross margin −160 bps on tariff costs); premium multiple leaves no cushion; OE is working-capital volatile.
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — v5 final run (2026-10-14)
Growth inputs: engine blend −1.10% (rev CAGR 5y 2.85%, rev CAGR 3y −3.44%, latest rev YoY 1.24%, OE/share CAGR 2y −15.36%) plus the buyback adjustment +3.76pp → g_base 2.66%. Scenario starts were recalibrated with offsets −0.11 / −0.05 / +0.015 / +0.045 / +0.075 for written reasons under the sanity check: the default super-bull start (14.7%) sits far above anything the company has recently printed (Q2 FY2026 revenue +6.7%, FY2026 guidance +4.7% to +7.2%) and is not defensible; the base start (4.2%) sits at the low end of current prints because the guidance is a *revenue* range while tariffs are compressing merchandise margins, so OE/share growth should not be assumed to match the revenue top line; bull (7.2%) is roughly the guidance top plus the buyback tailwind already credited in g_base; super bull (10.2%) requires a housing recovery on top of share gains and is weighted only 8%. Probabilities 15/30/30/17/8 widen the bear side per the OE_VOLATILE flag. OE multipliers are the defaults 0.75/0.90/1.00/1.10/1.25. Price $239.84.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | -8.3% | 0.75 | Housing stays frozen, tariffs bite margins, discretionary big-ticket slumps | $39.98 | 4.30% |
| Bear | 30% | -2.3% | 0.90 | Flat-to-down comps, tariff pressure persists, WC tailwind reverses | $61.73 | 5.56% |
| Base | 30% | 4.2% | 1.00 | Guidance-like revenue growth, margins held near guide, buybacks continue | $89.96 | 7.25% |
| Bull | 17% | 7.2% | 1.10 | Guidance top end, B2B/emerging brands compound, tariff pressure moderates | $112.05 | 8.51% |
| Super bull | 8% | 10.2% | 1.25 | Housing recovery + continued share capture + margin expansion | $144.10 | 10.26% |

- **Probability-weighted: IV@15% $82.08 (−65.8% vs price), IV@12% $108.19, IV@10% $137.22, weighted IRR 6.80%, base-case IRR 7.25%**
- **Tier by numbers: D.** Diagnostics (key_numbers.md): OE yield 4.27%, terminal value 18.0% of IV@15%, scenario spread 3.60x, 8.4 months since FY end.
- Even the super-bull scenario (10.2% growth start, 1.25x OE) only reaches a 10.26% IRR at this price — no scenario in the table clears the 15% hurdle.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 8.4 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 FY2026 (2026-08-02), with all inputs quoted above. Caveat recorded there: the TTM window includes the tariff refund cash collection, so the TTM base is treated as an upper bound and the verdict is sized to the conservative end.
- **BUYBACK_TAILWIND** (share count −3.76%/yr): already credited via the +3.76pp growth adjustment in g_base; not double-counted in the verdict. Note the share history also reflects the company's stock split in the earlier years of the CSV — the engine's CAGR is computed on the filed series as delivered.
- **OE_VOLATILE** (OE/share range over 5 yrs spans >3x): real and structural for this name — COVID-boom OE, a capex/WC-heavy dip, then a WC-release spike (see next flag). Handled with the normalized context ($8.12 median vs $10.24 TTM base), bear-side probability weight widened to 45% on bear-or-worse, and confidence held at medium.
- **NI_OCF_DIVERGENCE** (2024): FY2024 (ended 2024-01-28, financials_history.csv) net income $949,762,000 vs operating cash flow $1,680,273,000, with delta NWC of −$454,810,000 — i.e. the gap is a working-capital release (inventory drawdown after the prior year's overstock build), not earnings quality fraud or a tax deposit. Consequence: FY2024 conservative OE ($1,407,061,000 in the CSV) is flattered and is not used as the base; the TTM/median bases sit well below it.
- **WIDE_SCENARIO_SPREAD**: present in the preliminary run (4.52x) and resolved in the final run by the recalibrated offsets — final spread is 3.60x (key_numbers.md). Uncertainty is still material, so confidence is medium, not high, regardless.

## My thoughts / overlay
- This is a quality-versus-price result, not a quality indictment: debt-free, share-gaining, guidance-raising, dividend-growing — and priced at $239.84 against a weighted IV@15% of $82.08. The market is capitalizing the current (tariff refund-flattered) TTM earnings power as if mid-to-high-single-digit OE growth were durable; the filed record (5-yr revenue CAGR 2.85%, 3-yr −3.44%, OE/share CAGR 2y −15.36%) does not show that durability.
- Method range: on the engine's normalized median base ($8.12/share) with default scenarios the preliminary run gave a weighted IRR of 6.32% (Tier D); on the TTM base ($10.24/share) with default scenarios, 7.31% (Tier D); the final recalibrated run is 6.80% (Tier D). Defensible inputs span only D — unusually, the range does not rescue the stock.
- Tariffs are the live swing factor in both directions: Q2 FY2026 gross margin fell 160 bps on tariff costs while a ~$197.8M refund claim was collected (search-reported); guidance assumes tariffs stay and no further refunds. Neither leg should be extrapolated.
- Price that clears the hurdle: the weighted IV@15% is $82.08 — the stock would need to trade at or below roughly that level to clear 15% on these inputs, and a buyer wanting a margin of safety against the bear case ($61.73) would need to pay less still.

## Final verdict
- **Final tier: D** (weighted IRR 6.80%; no tier override)
- Confidence: **Medium** (high on the filing-derived OE history and TTM inputs; the tariff refund flattery of the TTM base and OE volatility keep it from high, and the verdict is robust across the method range)
- One-liner: High-quality premium home retailer, moat 5/10, but at $239.84 it does not clear 15% — weighted IRR 6.8%, weighted IV@15 $82.08; it would need to fall to ~$82 (the weighted IV@15) to clear the 15% hurdle.
