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
| Super bear | 15% | -5.0% | 0.75 | Comps stay negative, inventory needs markdowns, expansion capex strand
...[truncated 6187 chars]