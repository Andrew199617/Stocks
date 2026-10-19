# TSCO — Tractor Supply Company
v5 run, 2026-10-16. In scope (market cap $18.033B at $33.88, nasdaq_quote_api — key_numbers.md).

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.py output, or financials_history.csv — none are recomputed. Earnings/guidance color is from cited Q1/Q2 2026 reporting (10-Q/press coverage via search).

## What it is
The dominant US rural-lifestyle retailer: ~2,400+ Tractor Supply stores (plus Petsense pet stores) selling animal feed and pet food (needs-based consumables), farm/ranch supplies, tools, seasonal and big-ticket outdoor goods to rural and exurban homeowners, farmers and ranchers. Growth has historically come from steady new-store openings plus low-single-digit comps; capital returns (dividend + buybacks) on top.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $1,635,259,000; capex $894,770,000 (tag PaymentsToAcquirePropertyPlantAndEquipment); SBC $57,063,000 (always a real cost, but small here).
- **Conservative owner's earnings FY2025: $683,426,000 = $1.28/share** (key_numbers.md: latest FY OE/share $1.28)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $1,136,081,000 — well above the conservative figure because capex (new stores, remodels, distribution) runs far ahead of D&A; the conservative full-capex deduction is the right base standard for this sweep, but it does charge growth capex against current OE.
- OE positive 5 of the last 5 fiscal years. Net debt $1.571B (key_numbers.md). Shares diluted (latest) 532,178,000; the count shrinks ~1.73%/yr (buybacks), already credited in the growth blend via the +1.73pp share-count adjustment.
- History (financials_history.csv, conservative OE totals): FY2022 $529,778,000; FY2023 $523,135,000; FY2024 $588,421,000; FY2025 $683,426,000 — flat for two years, then recovering. Revenue followed the same shape (FY2023 $14,555,741,000 → FY2025 $15,524,046,000), after the post-COVID surge years.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $1,635,259,000 − prior YTD $1,002,575,000 + current YTD $653,136,000 = **TTM $1,285,820,000**
- Capex: FY $894,770,000 − prior YTD $351,644,000 + current YTD $435,713,000 = **TTM $978,839,000**
- SBC: FY $57,063,000 − prior YTD $25,976,000 + current YTD $33,162,000 = **TTM $64,249,000**
- Shares (current-YTD weighted diluted): **526,416,000**
- **TTM OE total $242,732,000 → base OE/share $0.46** (base_source: ttm_json)
- Why TTM over the median: the STALE_FY resolution prescribes the TTM base, and the TTM deterioration is corroborated, not a data artifact — H1 2026 OCF of $653,136,000 (ttm.py current-YTD leg; Zacks' Q2 coverage reports the same $653.1M) is down sharply from the H1 2025 leg of $1,002,575,000, while H1 capex rose to $435,713,000. The Q1 2026 10-Q detail (via press-release coverage) shows the mechanics: Q1 OCF $91,120,000 vs $216,775,000 a year earlier, on a Q1 inventory build of $499,515,000 vs $355,486,000, with Q1 net income $164,524,000 vs $179,369,000. Q2 2026 then missed (net sales $4.54B, +2.3% YoY; comps −1.5% on a weak May, higher fuel costs and southeastern drought hitting big-ticket/discretionary), and management cut FY2026 guidance (net sales growth 2.5–3.5%, comps −1% to flat, adjusted EPS $1.90–2.00, down from $2.13–2.23) and withdrew the December 2024 long-term framework. Part of the OCF drop is inventory timing that can reverse in H2, and part of the capex is growth capex for ~85–100 planned 2026 stores — which is exactly why the median base is carried as the method range below rather than discarded. The engine's normalized base (3-yr median) is $1.09/share.

## Moat: 5/10 — moderate / narrow
Justification: dominant rural-lifestyle niche and needs-based consumables give real repeat traffic, but retail switching costs are near zero and pricing power is capped by big-box and online rivals; the moat did not prevent a guidance cut and framework withdrawal in 2026.
- FOR: Dominant rural-lifestyle niche; scale procurement across ~2,400+ Tractor Supply stores plus Petsense; small-town locations with limited direct farm/ranch competition nearby; needs-based consumables (feed, pet food) drive repeat trips and retention; Neighbor's Club loyalty base and private brands; historically high returns on capital through cycles.
- AGAINST: Near-zero customer switching costs; price capped by Walmart/Amazon/Home Depot/Lowe's; discretionary big-ticket mix is weather, fuel and farm-income cyclical (Q2 2026 comps −1.5%); pet category contested by Chewy, Petco and Walmart; no protection in 2026 — guidance cut and long-term framework withdrawn; store-expansion capex rising into negative comps.
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — v5 final run (2026-10-16)
Growth recalibration (written reason): the engine's blended g_base is 7.83%, built from rev CAGR 5y 7.88%, rev CAGR 3y 3.02%, latest rev YoY 4.31%, and an OE/share CAGR 2y of 16.12% that is a recovery artifact off the flat FY2023 base. That blend sits above everything the company is currently printing — Q2 2026 net sales +2.3%, FY2026 guided sales growth of 2.5–3.5% with comps guided −1% to flat and EPS guided down. Scenario starts were therefore set via offsets (−0.128 / −0.078 / −0.048 / −0.018 / +0.012 vs g_base) to −5 / 0 / **3** / 6 / 9% — the base start matches guidance, and even the super-bull start (9%) only asks for a return to the post-COVID-era growth the blend remembers. Probabilities were skewed bearish vs the 10/25/30/25/10 default (15/30/30/15/10) because guidance was cut, the long-term framework was withdrawn, comps are negative, and the OE_VOLATILE flag instructs a wider bear weight. OE multipliers are the defaults 0.75/0.90/1.00/1.10/1.25. Price $33.88.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | -5.0% | 0.75 | Comps stay negative, inventory needs markdowns, expansion capex strands | $2.07 | 3.19% |
| Bear | 30% | 0.0% | 0.90 | Comps at the guided −1% to flat, inventory overhang clears slowly | $3.07 | 3.60% |
| Base | 30% | 3.0% | 1.00 | Guidance path: sales +2.5–3.5%, adjusted EPS $1.90–2.00, capex step-up absorbed | $3.87 | 3.94% |
| Bull | 15% | 6.0% | 1.10 | Comps turn positive, H1 inventory timing reverses, new-store cohort matures | $4.82 | 4.35% |
| Super bull | 10% | 9.0% | 1.25 | Full return to the post-COVID growth pattern the blend remembers | $6.19 | 4.94% |

- **Probability-weighted: IV@15% $3.73 (−89.0% vs price), IV@12% $4.92, IV@10% $6.24, weighted IRR 3.89%, base-case IRR 3.94%**
- **Tier by numbers: D.** Every scenario is a D — even the super-bull case returns 4.94%. Diagnostics (key_numbers.md): OE yield 1.36%, terminal value 18.0% of IV@15%, scenario spread 2.99x, net debt 6.40x normalized OE, 9.6 months since FY end.
- **Method range (disclosed, from the OE section):** on the engine's normalized median base ($1.09/share) instead of the TTM base, the weighted IRR is 7.1% with IV@15% of ~$11.93 — still Tier D, and still nowhere near the $33.88 price. The verdict does not depend on the base choice; the TTM base is used because the STALE_FY resolution prescribes it and the TTM deterioration is corroborated by the H1 2026 filing legs (see Owner's earnings).

## Flags — every fragility flag resolved
- **STALE_FY** (latest FY ended 10 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, quoted in Owner's earnings, and the choice is corroborated rather than mechanical: H1 2026 OCF of $653,136,000 vs $1,002,575,000 in H1 2025 (with the Q1 inventory build of $499,515,000 identified in the 10-Q detail), a Q2 miss, and cut FY2026 guidance. Part of the OCF drop is inventory timing that can reverse in H2 — which is why the median base is carried as the method range above instead of being discarded.
- **OE_VOLATILE** (OE/share range over the last 5 years spans >3x): acted on as instructed — probabilities were skewed bearish (15/30/30/15/10 vs the 10/25/30/25/10 default) and scenario starts were cut below the blend (base 3.0% vs blended 7.83%). The volatility is the post-COVID surge-and-fade pattern in the history, not a data break.
- **LOW_OE_YIELD** (base OE yield 1.4%): the tier is indeed fragile in construction — at a $0.46 TTM base the valuation rests almost entirely on growth — but the fragility cuts against the price, not for it: at $33.88 the market is capitalizing a recovery the filed OE does not yet show, and no scenario in the table reaches even 5%. Confidence is graded low in recognition of the flag.
- **HIGH_NET_DEBT** (net debt 6.4x normalized OE): $1.571B of net debt against a collapsed TTM OE is the leverage the flag measures; on the normalized base the same debt is roughly 2.7x the $588–683M recent-year OE totals, serviced by a needs-based consumables retailer with 5/5 OE-positive years. The bear cases are stressed accordingly (super-bear/bear OE multipliers 0.75/0.90 on a shrinking start), and the verdict never relies on the levered OE holding up.

## Final verdict
**Tier D.** Weighted IRR 3.89%, weighted IV@15% $3.73 against a $33.88 price (−89.0%). A solid niche retailer (moat 5/10) whose owner's earnings collapsed on a TTM basis ($0.46/share) as H1 2026 operating cash flow halved and capex rose — it does not clear 15% on any base: 3.9% weighted on the TTM base, 7.1% on the median base ($1.09/share, IV@15% ~$11.93). It clears 15% only below ~$3.73 (TTM) or ~$11.93 (median). Guidance was cut and the long-term framework withdrawn in 2026; until the filed OE recovers, the price is paying for a growth story the cash flow has stopped telling.