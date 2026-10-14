# GEHC — GE HealthCare Technologies Inc.
v5 run, 2026-10-14. In scope (market cap $31.201B at $68.12, nasdaq_quote_api).

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.py output, or financials_history.csv — none are recomputed.

## What it is
Medical imaging and diagnostics company spun out of GE in January 2023: Advanced Imaging Solutions (CT, MRI, ultrasound, molecular imaging), Patient Care Solutions (monitoring, anaesthesia, ECG), Pharmaceutical Diagnostics (PDx — contrast agents and radiopharmaceuticals), plus imaging software/AI layered on a very large installed base. Q2 2026 (reported 2026-07-29): revenue $5.295 billion, up 5.7% year over year (organic +3.5%), adjusted EPS $1.13; PDx revenue +15.6%, Advanced Imaging Solutions grew, Patient Care Solutions revenue declined 13.3%. Orders grew 11.1% organically, book-to-bill 1.15x, backlog a record $23.9 billion. Management reaffirmed 2026 guidance for organic growth of 3%-4% and adjusted EPS of $4.80–$5.00. Two deals frame the current balance sheet: Intelerad (imaging software) acquired for approximately $2.30 billion in cash in March 2026, and a pending $945 million cash acquisition of SOFIE Biosciences to expand the PET radiopharmaceutical network. The CFO also stepped down in mid-2026, with an interim CFO in place while a permanent successor is sought.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** revenue $20,625,000,000; net income $2,084,000,000; operating cash flow $1,987,000,000; capex $482,000,000 (tag PaymentsToAcquireProductiveAssets); SBC $130,000,000 (tag ShareBasedCompensation).
- **Conservative owner's earnings FY2025: $1,375,000,000 = $3.00/share latest FY OE/share** (key_numbers.md: latest FY OE total $1.375B, latest FY OE/share $3.00)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $1,652,000,000 (financials_history.csv) — above the conservative figure, so the conservative OCF-based series is the binding, cleaner base.
- OE positive 5 of the last 5 fiscal years (key_numbers.md). Net debt $5.505B (key_numbers.md). Share count is essentially flat: share count CAGR 0.29% (growth adj -0.29%).
- Growth quality is weak for a DCF: rev CAGR 5y 4.07%, rev CAGR 3y 3.99%, latest rev YoY 4.84%, but OE/share CAGR 2y -7.29% — margins and cash conversion have gone backwards even as revenue inched up, with tariffs a named drag in 2026 quarters (and a one-off tariff refund benefit flattering Q2 2026 GAAP EPS, so that quarter's EPS overstates run-rate cash earnings).

**Base used = TTM owner's earnings through Q1 2026, from ttm.py (filing-direct, no hand math) — ttm.py's latest YTD leg is 2026-03-31:**
- OCF: FY $1,987,000,000 − prior YTD $250,000,000 + current YTD $290,000,000 = **TTM $2,027,000,000**
- Capex: FY $482,000,000 − prior YTD $152,000,000 + current YTD $178,000,000 = **TTM $508,000,000**
- SBC: FY $130,000,000 − prior YTD $22,000,000 + current YTD $35,000,000 = **TTM $143,000,000**
- Shares (current-YTD weighted diluted): **457,000,000**
- **TTM OE total $1,376,000,000 → base OE/share $3.01** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $3.11/share and the latest FY is $3.00/share — all three bases sit within a narrow band, so there is no BASE_DIVERGENCE distortion to adjudicate; the TTM base was used because it is the most current and sits between the other two.

## Moat: 6/10 — moderate
Justification: huge installed imaging base, service attach, broadest modality portfolio and Pharmaceutical Diagnostics consumables give real switching costs and recurring revenue, and the regulatory/FDA barrier is high. But Siemens Healthineers, Philips, Canon and United Imaging contest every modality, hospital capex is cyclical, pricing power is unproven (revenue CAGR ~4%, OE/share CAGR 2y negative), and tariffs/China and PCS weakness erode returns. CAP 9.8 years.
- FOR: Large installed imaging base with service and upgrade attach; broadest modality portfolio (CT, MRI, ultrasound, molecular imaging); Pharmaceutical Diagnostics consumables — recurring contrast/radiopharmaceutical revenue, +15.6% in Q2 2026; record backlog $23.9B and book-to-bill 1.15x in Q2 2026; high FDA/regulatory barriers and hospital workflow integration / switching costs; leading AI clearance portfolio and Edison/CareIntellect software layer on the installed base.
- AGAINST: Siemens Healthineers (photon-counting CT lead), Philips, Canon and low-cost United Imaging contest every sale; no proven pricing power — revenue CAGR ~4% and OE/share down over the last 2 years; hospital capital budgets are cyclical and budget-constrained; US-China tariff exposure and choppy China demand; Patient Care Solutions declining (-13.3% in Q2 2026) and under strategic review; leverage and acquisition load (Intelerad, pending SOFIE) limit flexibility.
- A 6 gives CAP = 9.8 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 9.8 years, 15-year projection.

## DCF — v5 final run (2026-10-14)
Growth sanity check: the engine's blended growth is 4.03% and g_base is 3.74% — squarely in line with actual prints (latest FY rev YoY 4.84%, Q2 2026 organic +3.5%, guided 2026 organic growth 3%-4%). The base start was therefore left at 3.7%. Offsets were recalibrated from the defaults (-0.11 / -0.05 / 0.00 / +0.03 / +0.06, vs default +0.12 for super bull) with a written reason: the default super-bull start of 15.7% has no support in any print — this is a mature imaging market growing at mid-single digits, GEHC's own 5-yr revenue CAGR is 4.07%, and even the bull case needs backlog conversion, PDx momentum and photon-counting adoption, not a step-change to mid-teens growth. Super-bull start was set to 9.7%. Probabilities 10/25/35/20/10 (base weighted up to 35% on reaffirmed guidance and the record backlog); OE multipliers at the defaults 0.75/0.90/1.00/1.10/1.25. Price $68.12.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -7.3% | 0.75 | Tariff/China shock plus hospital capex freeze; PCS deteriorates | $12.00 | 4.38% |
| Bear | 25% | -1.3% | 0.90 | Growth stalls, tariff and input-cost pressure sticks, debt service bites | $18.79 | 5.79% |
| Base | 35% | 3.7% | 1.00 | Guided 3-4% organic growth, flat margins, backlog converts normally | $26.09 | 7.34% |
| Bull | 20% | 6.7% | 1.10 | Backlog and PDx/AI software drive above-guide growth, margins recover | $32.79 | 8.70% |
| Super bull | 10% | 9.7% | 1.25 | Durable share gains, PDx compounding, margin expansion and deleveraging | $42.58 | 10.58% |

- **Probability-weighted: IV@15% $25.84 (-62.1% vs price), IV@12% $34.17, IV@10% $43.44, weighted IRR 7.31%, base-case IRR 7.34%**
- **Tier by numbers: D.** Diagnostics (key_numbers.md): OE yield 4.42%, terminal value 18.3% of IV@15%, scenario spread 3.55x, net debt 3.99x normalized OE, 9.4 months since FY end.
- Even the super-bull case (10.58% IRR, IV@15% $42.58) sits well below the $68.12 price — this is not a close call driven by one assumption.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.4 months ago): resolved by construction — the base is the TTM figure from ttm.py, quoted above. Note ttm.py's current YTD leg ends 2026-03-31; Q2 2026 reported results (revenue +5.7%, organic +3.5%) are consistent with the TTM trajectory and were used only as a sanity check, never hand-computed into a TTM figure.
- **HIGH_NET_DEBT** (net debt 4.0x normalized OE; key_numbers.md: net debt $5.505B, net debt / normalized OE 3.99x): folded into the verdict explicitly — leverage is a core reason the bear weights are material (25% bear + 10% super bear), the bull cases require deleveraging from operating cash flow rather than more acquisition debt, and the Intelerad ($2.30 billion, closed March 2026) and pending SOFIE ($945 million) deals add to the load before any deleveraging. At a 4.42% OE yield, levered owner's earnings have little cushion if growth stalls.
- **WIDE_SCENARIO_SPREAD** (preliminary run: super-bull IV 4.5x super-bear IV): addressed by recalibrating the super-bull offset as written above; the final spread is 3.55x, which still reflects a genuinely wide outcome range for a levered, tariff-exposed name. Confidence is therefore set to medium, not high.

## My thoughts / overlay
- Quality is real but slow: a durable installed base, recurring service and consumables, and a record $23.9B backlog support the revenue line, yet revenue has compounded at only ~4% and OE/share has shrunk over the last two years (OE/share CAGR 2y -7.29%). A screening DCF on owner's earnings cannot get a $68 stock with a $3.01 base OE/share (4.42% OE yield) and ~4% growth anywhere near a 15% hurdle.
- Method range: the bases are unusually tight ($3.00 latest FY / $3.01 TTM / $3.11 median), so unlike inflection names there is no defensible alternative base that changes the tier — on any of the three, and even on the super-bull scenario alone, the result stays Tier D. The verdict does not hinge on the moat score either: a materially higher moat would lengthen the fade but cannot bridge a -62.1% gap to IV@15%.
- What would change the picture is price, not narrative: the weighted IV@15% is $25.84, so the stock would need to fall toward $25.84 to clear 15% on these inputs — and even at IV@12% ($34.17) it is roughly half the current price.
- Risks to the (already low) base case: tariff costs persisting or expanding, China demand/policy, Siemens photon-counting CT taking premium share, PCS continuing to shrink, integration/debt from Intelerad and SOFIE, and CFO-transition execution risk. Upside risks: PDx compounding at mid-teens, AI software attach, and backlog conversion beating guide.

## Final verdict
- **Final tier: D** (weighted IRR 7.31% on the v5 final inputs; no tier override)
- Confidence: **Medium** (bases are tight and filings are clean with no data gap, but the scenario spread is 3.55x and leverage/tariff exposure is unresolved)
- One-liner: Solid, moderate-moat (6/10) imaging franchise with recurring service/PDx revenue, but slow ~4% growth and 4.0x net debt leave it well short of 15% at $68.12 — weighted IRR 7.31%, IV@15% $25.84; it would need to fall toward $25.84 to clear 15%.
