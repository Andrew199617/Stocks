# RVTY — Revvity, Inc.
Engine 5.4.0 run, 2026-10-16. In scope (market cap $17.776B at $152.46, nasdaq_quote_api).

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.json or fundamentals.json — none are recomputed.

## What it is
The former PerkinElmer, renamed Revvity in 2023 after selling its Applied, Food and Enterprise Services (AES) businesses to New Mountain Capital for $2.45B (closed Q1 2023). What remains is a pure-play Life Sciences + Diagnostics company: high-content screening and life-sciences instruments/reagents and Signals informatics software on one side; newborn screening, reproductive health and immunodiagnostics on the other. Q2 2026 (per the company's reported results, via search): pro forma revenue $711.1M with 3% organic growth — Diagnostics +11% organic offset by Life Sciences −3% organic and Signals software down ~20% organically — and full-year 2026 guidance raised to 4–5% organic growth. The company also announced a divestiture of its China immunodiagnostics business alongside that quarter.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $582,933,000; capex $73,522,000; SBC $22,847,000 (always a real cost — and small here, ~4% of OCF).
- **Conservative owner's earnings FY2025: $486,564,000 = $4.17/share** (key_numbers.md: latest FY OE/share $4.17)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $1,117,490,000 in financials_history.csv — rejected as the headline: its ΔNWC leg is a large positive swing that year, so it overstates repeatable earnings. The OCF-based conservative figure is the cleaner one.
- OE positive 4 of the last 5 fiscal years. The negative year is the fiscal year ended 2023-12-31 (conservative OE −$31,506,000, −$0.25/share, OCF only $91,272,000) — the AES divestiture year; see NI_OCF_DIVERGENCE below.
- Net debt $2.300B (key_numbers.md); lease liabilities $148,108,000 (dcf_numbers.json).

**Base used = TTM owner's earnings through Q2 2026 (period ended 2026-07-05), from ttm.py (filing-direct, no hand math):**
- OCF: FY $582,933,000 − prior YTD $262,473,000 + current YTD $307,173,000 = **TTM $627,633,000**
- Capex: FY $73,522,000 − prior YTD $34,850,000 + current YTD $30,848,000 = **TTM $69,520,000**
- SBC: FY $22,847,000 − prior YTD $17,864,000 + current YTD $19,446,000 = **TTM $24,429,000**
- Shares (current-YTD weighted diluted): **111,746,000**
- **TTM OE total $533,684,000 → base OE/share $4.78** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $4.10/share and the latest FY is $4.17/share. The TTM base is higher than both because the two post-divestiture clean years plus the current TTM are genuinely above the median that still includes the divestiture-depressed year — the TTM figure is the current run-rate, so it is used. The verdict does not depend on the choice: at the median base the preliminary run printed a weighted IRR of 5.77%, also Tier D.

## Moat: 4/10 — weak-to-moderate
Justification: niche installed bases give recurring reagents and switching friction, but the measured returns are poor — roic_proxy in fundamentals.json fell from 12.8% at the COVID-peak year to 5.16%, then 2.72% / 3.22% / 3.34% in the last three fiscal years, well below any plausible cost of capital for three straight years. Gross margin in fundamentals.json is carried only through the fiscal year ended 2023-01-01 (60.1%, still COVID-mix-inflated; 48.4% pre-COVID) — the extraction carries no gross margin for the last three fiscal years, so no recent gross-margin figure is quoted; the recent GAAP operating margin is 12.5% (FY2025, dcf history operating income $356,635,000 on revenue $2,856,051,000 as filed). A moat above 4 would need ROIC evidence this company does not currently produce.
- FOR: Installed base in newborn screening and reproductive health — assays embedded in regional/national screening programs, real switching friction; High-content screening instruments (Opera Phenix line) are a de facto standard in phenotypic drug discovery, pulling through reagents and assay kits; Recurring reagent/consumable revenue attached to the instrument base in both Diagnostics and Life Sciences; Signals informatics software embedded in pharma discovery workflows.
- AGAINST: ROIC proxy collapsed to ~3% for three straight years (fundamentals.json) — the BioLegend-era capital base is not earning its cost of capital; Much larger, better-capitalized rivals (Thermo Fisher, Danaher, Abbott) contest every category; China immunodiagnostics weakness forced a divestiture of that business (announced with Q2 2026 results); Signals software revenue fell ~20% organically in Q2 2026 — the software pillar is not currently compounding; End-market exposure to pharma/biotech and academic budgets is cyclical, as the post-COVID revenue decline showed.
- A 4 gives CAP = 7.2 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 7.2 years, 15-year projection.

## DCF — engine 5.4.0 final run (2026-10-16)
Growth sanity check: the engine's blended growth is 4.08% (components: rev CAGR 5y 1.41%, rev CAGR 3y −4.83%, latest rev YoY 3.67%, share-count adjustment +2.67pp). The historical CAGRs straddle both the COVID diagnostics surge (revenue $3,827,808,000 in the fiscal year ended 2022-01-02, financials_history.csv) and the 2023 AES divestiture, so they are not clean trend signals in either direction; the usable anchors are the latest FY YoY (+3.67%), TTM revenue YoY in fundamentals.json, Q2 2026 organic growth of 3%, and the raised full-year guidance of 4–5% organic growth. A 4.1% base start sits exactly on those prints — no recalibration. Default offsets and multipliers were kept. The bull start (9.1%) is above every recent print: it is defensible only as a Diagnostics-led recovery case (Diagnostics printed +11% organic in Q2 2026), and the super-bull start (16.1%) is above anything the post-divestiture company has printed — it is a tail scenario at 10% weight, not a forecast, and even it does not clear 10% IRR. Probabilities 10/25/30/25/10; OE multipliers 0.75/0.90/1.00/1.10/1.25. Price $152.46.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -7.9% | 0.75 | End-market budgets tighten again; leverage bites | $19.56 | 3.93% |
| Bear | 25% | -0.9% | 0.9 | Flat revenue, no operating leverage | $30.89 | 4.96% |
| Base | 30% | 4.1% | 1.0 | Guidance-level organic growth, fading over the CAP | $41.62 | 5.95% |
| Bull | 25% | 9.1% | 1.1 | Diagnostics momentum spreads to Life Sciences | $55.37 | 7.22% |
| Super bull | 10% | 16.1% | 1.25 | Full AI-driven discovery demand cycle | $81.71 | 9.55% |

- **Probability-weighted: IV@15% $44.18 (-71.0% vs price), IV@12% $58.58 (-61.6%), IV@10% $74.63, weighted IRR 6.22%, base-case IRR 5.95%**
- **Tier by numbers: D — and every scenario, bear to super bull, is also D.** Diagnostics (key_numbers.md): OE yield 3.13%, terminal value 18.5% of IV@15%, scenario spread 4.18x, net debt 4.13x normalized OE, 9.6 months since FY end.
- Hurdle-clearing prices (weighted path): 15% at $44.18 · 20% at $31.21 · 25% at $24.05.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.6 months ago): resolved by construction — the base is the TTM figure from ttm.py through 2026-07-05, legs quoted above.
- **BUYBACK_TAILWIND** (share count shrinking 2.7%/yr): already credited via the growth adjustment in the blend; not double-counted. Shares fell from 126,426,000 (fiscal year ended 2023-01-01) to 116,595,000 latest FY in financials_history.csv, funded in part by divestiture proceeds — a real but non-operating tailwind.
- **NI_OCF_DIVERGENCE** (2023): the fiscal year ended 2023-12-31 — net income $693,094,000 vs operating cash flow $91,272,000 (financials_history.csv). That is the year the AES sale closed (Q1 2023, $2.45B): net income carries the divestiture/discontinued-operations effects while continuing-operations OCF collapsed, leaving conservative OE at −$31,506,000 for that year. It is a portfolio-break artifact, not an earnings-quality signal for the continuing business — and it is exactly why the base is the post-divestiture TTM rather than any series that averages that year in at face value.
- **WIDE_SCENARIO_SPREAD** (4.18x): real — the outcome range is wide, driven mostly by the growth-start range. Confidence is capped at medium, and the verdict is sized to the conservative end. Note the spread does not threaten the tier: even the super-bull end is Tier D.
- **HIGH_NET_DEBT** (net debt 4.13x normalized OE in key_numbers.md; $2.300B against latest FY OE total $486.6M): confirmed from the filing basis in dcf_numbers.json (LongTermDebtNoncurrent+LongTermDebtCurrent, cash $919,860,000). This is investment-grade-style leverage for a diagnostics name, not distress — but at 4x+ the owner's earnings, a revenue downturn compresses equity OE fast, which is what the bear cases (0.75–0.90 multipliers) are pricing.

## My thoughts / overlay
- The story is valuation, not business quality collapse: a real franchise with recurring revenue is priced at $152.46 against a TTM OE yield of 3.13%. The stock has already re-rated hard this year (search results noted a ~56% year-to-date rally into late September 2026) on the diagnostics/AI-discovery narrative, and the DCF cannot follow it there — the weighted IV@15% is $44.18 and even the super-bull IV@15% ($81.71) is barely half the price.
- Method range: median-base preliminary run 5.77% weighted IRR vs TTM-base final 6.22% — both Tier D, both by a wide margin. Unlike most names in this sweep, the conclusion is method-insensitive.
- What would have to be true: sustained double-digit OE/share growth for a decade (super-bull still only yields 9.55% IRR) or a much higher starting OE — neither is in the recent prints (revenue +3.67% latest FY, ROIC ~3%).
- Risks to the short/avoid case: buybacks shrinking the count ~2.7%/yr, a genuine pharma spending recovery, and AI-driven screening demand are real; they are in the bull cases and still do not rescue the price.

## Final verdict
- **Final tier: D** (weighted IRR 6.22%; bear→bull band D→D, scenario range 3.93%–9.55%)
- Confidence: **Medium** (high that the price is far above any defensible IV; medium on any single growth path — the scenario spread is 4.18x)
- One-liner: Decent diagnostics/life-sciences franchise, moat 4/10 with ~3% ROIC — does not clear 15% at $152.46 (weighted IRR 6.2%, IV@15% $44.18, even super-bull IRR only 9.5%); clears 15% only below $44.18.
