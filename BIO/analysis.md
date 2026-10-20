# BIO — Bio-Rad Laboratories, Inc.
v5 run, 2026-10-20. Engine release 5.5.0. All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.json or fundamentals.json — none are recomputed.

## What it is
Life science research tools and clinical diagnostics (SIC 3826, Laboratory Analytical Instruments). Two segments: Life Science (research instruments/consumables, including digital PCR) and Clinical Diagnostics (quality controls, blood typing, diabetes/infectious-disease testing for hospital and reference labs). Price $352.82 (nasdaq_quote_api), market cap $9.625B — in scope under $40B.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $532,200,000; capex $157,600,000; SBC $58,000,000.
- **Conservative owner's earnings FY2025: $316,600,000 = $11.61/share** (key_numbers.md: latest FY OE/share $11.61, latest FY OE total $316.6M)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC) for FY2025 is $982,700,000 in the CSV — not usable here: it is built on GAAP net income, which Bio-Rad's Sartorius AG equity stake marks to market every period (see NI_OCF_DIVERGENCE below), so the maintenance series swings from -$603,932,000 (FY2023) to -$1,796,900,000 (FY2024) to +$982,700,000 (FY2025) while the OCF-based conservative series is $156,900,000 / $227,300,000 / $316,600,000. The conservative OCF-based figure is the clean one.
- OE positive 5 of the last 5 fiscal years. Net debt $671.9M (key_numbers.md).

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $532,200,000 − prior YTD $246,400,000 + current YTD $206,800,000 = **TTM $492,600,000**
- Capex: FY $157,600,000 − prior YTD $80,100,000 + current YTD $62,000,000 = **TTM $139,500,000**
- SBC: FY $58,000,000 − prior YTD $27,200,000 + current YTD $29,500,000 = **TTM $60,300,000**
- Shares (current-YTD weighted diluted): **26,852,000**
- **TTM OE total $292,800,000 → base OE/share $10.90** (base_source: ttm_json; key_numbers.md base OE/share $10.90)
- The engine's normalized base (3-yr median) is $8.06/share and the latest FY is $11.61/share — see BASE_DIVERGENCE for why the TTM sits between them and is used.

## Moat: 5/10 — moderate / narrow
Justification: real switching costs from validated diagnostic systems and a consumables pull-through model, plus ddPCR leadership, but no growth for four years, falling margins, and low measured returns on capital do not support a wide-moat score.
- Evidence first (fundamentals.json): ROIC proxy (after-tax operating income over equity + debt − cash) was 3.54% (FY2020), 2.95% (FY2021), 3.67% (FY2022), 2.80% (FY2023), 2.92% (FY2024) and 0.44% (FY2025). The denominator is inflated by the balance-sheet value of the Sartorius stake, so the proxy understates core returns — but even allowing for that, it has never shown the well-above-cost-of-capital profile a 7+ moat requires. Gross margin: 56.5% (FY2020), 56.1% (FY2021), 55.9% (FY2022), 53.4% (FY2023), 53.7% (FY2024), 51.9% (FY2025) — a high level, but a clear downtrend.
- FOR: Razor-and-blade model: installed instruments pull through high-margin consumables, quality controls and reagents; Leading positions in quality controls, blood typing and diabetes testing in Clinical Diagnostics — validated systems create switching costs; Digital PCR (ddPCR) leadership, strengthened by the Stilla acquisition — Q2 2026 ddPCR revenue up ~6% and instrument sales up >20% (Q2 2026 earnings reporting); Gross margin has held around 52-56% through a cycle despite volume softness; Recurring consumables/services mix and a long installed-base history in hospital and reference labs.
- AGAINST: Revenue flat for four years (FY2022 $2,802M to FY2025 $2,583M in the CSV history); 2026 guidance -3% to +0.5% currency-neutral (Q2 2026 release, reaffirmed); Academic/government research funding softness hits Life Science; China weakness persists; Gross margin slipped from 56.5% (FY2020) to 51.9% (FY2025) and operating margin collapsed to 1.8% in FY2025 (operating income $47,200,000 on revenue $2,583,200,000 in the CSV); Process chromatography is lumpy and concentrated; the restructuring announced in Q2 2026 ($90M one-time costs, $30-35M targeted annual savings) is unproven, and activist Elliott Management is engaged.
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — v5 final run (2026-10-20)
Growth recalibration (written reason): the engine's blended growth is 3.36% (key_numbers.md), but two of its components do not describe the business the price buys — the OE/share CAGR 2y is 46.95%, an artefact of OE recovering off the depressed FY2023 base ($5.37/share), and the blend credits a +2.88% buyback adjustment. The revenue signals are near zero: rev CAGR 5y 0.29%, rev CAGR 3y -2.68%, latest rev YoY 0.65% (all key_numbers.md); Q2 2026 revenue was $651.0M, flat year-over-year, and management reaffirmed FY2026 currency-neutral revenue guidance of -3% to +0.5%. Scenario starts were therefore set via offsets (-0.094 / -0.054 / -0.024 / +0.006 / +0.036 vs g_base) to -6.0 / -2.0 / **1.0** / 4.0 / 7.0%. Even the super-bull start (7.0%) is a bet on a recovery the company has not printed in four years — it is not below a recent print, it is above all of them, which is why it carries only 10%. Probabilities 15/30/30/15/10 — bear weight widened per OE_VOLATILE; OE multipliers 0.75/0.90/1.00/1.10/1.25 (defaults). Price $352.82.

| Scenario | Prob | Growth start | OE mult | IV@15 | IRR |
|---|---|---|---|---|---|
| Super bear | 15% | -6.0% | 0.75 | $46.90 | 3.98% |
| Bear | 30% | -2.0% | 0.90 | $66.56 | 4.73% |
| Base | 30% | 1.0% | 1.00 | $83.84 | 5.42% |
| Bull | 15% | 4.0% | 1.10 | $104.50 | 6.25% |
| Super bull | 10% | 7.0% | 1.25 | $134.48 | 7.42% |

- **Probability-weighted: IV@15% $81.28 (-77.0% vs price), IV@12% $106.54, weighted IRR 5.34%, base-case IRR 5.42%**
- **Tier by numbers: D** (bear D → bull D). Diagnostics (key_numbers.md): OE yield 3.09%, terminal value 17.4% of IV@15%, scenario spread 2.87x, net debt 2.26x normalized OE, 9.6 months since FY end.
- Hurdle-clearing prices (key_numbers.md): 15% at $81.28, 20% at $58.37, 25% at $45.60.

## Flags — every fragility flag resolved
- **STALE_FY** (latest fiscal year ended 10 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, quoted above (TTM OE/share $10.90).
- **BUYBACK_TAILWIND** (share count shrinking 2.9%/yr; key_numbers.md share count CAGR -2.88%): already credited via the growth adjustment in the blend — and the recalibration above deliberately did not double-count it, since the scenario starts were set from revenue prints, not from the adjusted blend.
- **OE_VOLATILE** (OE/share range over the last 5 years spans >3x): real. The CSV OE/share path runs from the depressed FY2023 $5.37 through $8.06 to $11.61, with earlier years far higher on pandemic-era volumes. Handled by the TTM base (not the single latest FY) plus probabilities widened to 45% on bear-or-worse (15% super bear + 30% bear).
- **NI_OCF_DIVERGENCE** (net income and operating cash flow differ by >40% in 2023, 2024, 2025): the cause is the Sartorius AG equity investment, marked to market in GAAP net income every period. Net income was -$637,300,000 (FY2023), -$1,844,200,000 (FY2024) and +$759,900,000 (FY2025) in the CSV while operating cash flow was a steady $374,900,000 / $455,200,000 / $532,200,000; Q2 2026 reporting likewise attributes the quarter's $371.4M net income substantially to the change in fair value of the Sartorius investment. Those fair-value moves are non-operating and do not enter operating cash flow, so the conservative OCF-based OE base is not contaminated by them. The maintenance OE definition, which starts from net income, is contaminated — see Owner's earnings.
- **BASE_DIVERGENCE** (latest FY OE/share $11.61 vs 3-yr median $8.06): both ends are partly distorted. The median is dragged down by FY2023 ($5.37/share), when OCF was only $374,900,000 as revenue fell post-pandemic; the latest FY ($11.61) sits on the strongest OCF of the three years ($532,200,000), and H1 2026 OCF already softened (current YTD $206,800,000 vs prior YTD $246,400,000 in ttm.json). The TTM base ($10.90) — above the median, below the latest FY — is the balanced choice and is what the score uses.
- Preliminary-run flags that did not recur in the final run: WIDE_SCENARIO_SPREAD and HIGH_NET_DEBT fired on the median base (spread 4.52x, net debt 3.06x normalized OE in the preliminary dcf_numbers); on the TTM base the final diagnostics are spread 2.87x and net debt 2.26x normalized OE. Confidence is still capped at low (see below), and the balance sheet from the filing history is: cash $529,800,000, total debt $1,201,700,000, net debt $671,900,000 (CSV latest row / key_numbers.md), plus lease liabilities $181,800,000 in dcf_numbers.json.

## My thoughts / overlay
- The operating business alone does not support the price on any scenario here: even the super-bull IV@15% ($134.48) is far below $352.82. One method limit matters for interpreting that gap, not for changing the tier: Bio-Rad holds a substantial equity stake in Sartorius AG. That stake is a real asset the market prices, its fair-value changes dominate GAAP net income, and an owner's-earnings DCF on operating cash flow does not capitalise it separately. A sum-of-the-parts view would credit it; this sweep's method does not, and no figure for the stake is quoted here because it is not in the computed outputs.
- Quality is middling, not poor: consumables pull-through, ~52-54% gross margins and 5/5 OE-positive years, against four flat revenue years, a falling gross margin, a 1.8% FY2025 operating margin, and a restructuring whose savings are promised, not delivered.
- Risks: academic/government funding (Life Science demand), China, process-chromatography customer concentration, restructuring execution, and the Sartorius stake's own market volatility flowing through reported earnings.

## Final verdict
- **Final tier: D** (weighted IRR 5.34% on the TTM base; bear and bull both D)
- Confidence: **Low** (OE volatility, the NI/OCF divergence's scale, and a growth outlook guided at -3% to +0.5% for 2026)
- One-liner: Solid diagnostics franchise, moat 5/10, but flat revenue and a $352.82 price leave it far short of 15% — weighted IRR 5.34%, IV@15% $81.28 vs $352.82; it would need to fall to about $81 to clear 15%.
