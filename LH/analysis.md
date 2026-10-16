# LH — Labcorp Holdings Inc.
v5 run, 2026-10-15. In scope (market cap $26.775B at $319.51, nasdaq_quote_api).

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.py output, or financials_history.csv — none are recomputed. Recent-quarter and guidance figures are from cited web search results (Q2 2026 reporting, July 30, 2026).

## What it is
One half of the US clinical-laboratory duopoly (with Quest Diagnostics): routine and specialty diagnostic testing for physicians, hospitals, and payers, plus Biopharma Laboratory Services (central labs and early-development services for pharma, the retained Covance legacy after the 2023 Fortrea spin-off of the clinical-development business). Q2 2026 (search results): revenue $3.73B, +5.8% YoY; Diagnostics revenue $2.9B, +5.5%; Biopharma Laboratory Services revenue $836M, +6.5%, with an $8.7B backlog and 1.14 quarterly book-to-bill; adjusted EPS $4.99, +14.9%. FY2026 guidance (raised at Q2, reaffirmed Sept 10, 2026): revenue growth 5.4–6.3%, adjusted EPS $18.10–$18.55, free cash flow $1.24–1.36B. Longer-term targets through 2029: revenue CAGR 5–8%, adjusted EPS CAGR 8.5–11.5%.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** revenue $13,951,700,000; operating cash flow $1,640,500,000; capex $434,500,000; SBC $125,800,000 (always a real cost, and here a modest one relative to OCF); D&A $681,100,000.
- **Conservative owner's earnings FY2025: $1,080,200,000 = $12.89/share** (latest FY OE/share, key_numbers.md)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $916,200,000 — below the conservative figure because FY2025 working capital absorbed cash (ΔNWC $206,900,000 in the CSV); the two definitions bracket the same ~$1B scale.
- OE positive 5 of the last 5 fiscal years. Net debt $5,052,400,000 (FY2025 cash $532,300,000; debt current $500,100,000 + long-term $5,084,600,000 in the CSV).

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $1,640,500,000 − prior YTD $639,100,000 + current YTD $637,000,000 = **TTM $1,638,400,000**
- Capex: FY $434,500,000 − prior YTD $203,900,000 + current YTD $252,600,000 = **TTM $483,200,000** (capex is rising — automation/lab investment — which is why TTM OE/share sits below the FY2025 figure)
- SBC: FY $125,800,000 − prior YTD $66,900,000 + current YTD $66,600,000 = **TTM $125,500,000**
- Shares (current-YTD weighted diluted): **82,400,000**
- **TTM OE total $1,029,700,000 → base OE/share $12.50** (dcf_numbers.json base $12.4964, base_source: ttm_json)
- The engine's normalized base (3-yr median) is $11.60/share and the latest FY is $12.89/share — the three candidate bases span only ~11%, so unlike an inflection name there is no wide method range here; the TTM base is the most current and is used.

## Moat: 6/10 — moderate-strong, not wide
Justification: US clinical-lab duopoly scale with Quest — national patient-service-center network, payer and health-system contracts, broad specialty test menu, and an $8.7B Biopharma Laboratory Services backlog give real scale and switching friction; but routine testing is commoditized, pricing is set by payers/CMS rather than Labcorp, and Quest matches its scale on every contract, so pricing power and durability cap the score at moderate-strong.
- FOR: Duopoly scale with Quest: national network of 2,000+ patient service centers and logistics regionals cannot replicate; payer and health-system contracts / preferred-provider status drive recurring volume, with the hospital-outsourcing trend a tailwind; broad and specialty test menu (oncology, neurology, women's health growing double-digit per Q2 2026 reporting); Biopharma Laboratory Services backlog of $8.7B gives contracted revenue visibility; longitudinal test-result data scale and physician-workflow IT integrations create switching friction.
- AGAINST: Routine testing is commoditized — prices are set by payers and CMS/PAMA, not by Labcorp, so little pricing power on core volume; Quest matches Labcorp's scale and contests every managed-care contract (no share lock-in); hospital in-sourcing, regional labs, and direct-to-consumer entrants pressure the low end; recurring reimbursement, billing-regulation, and healthcare-data cybersecurity risk; Biopharma services revenue rides pharma R&D spending cycles.
- A 6 gives CAP = 9.8 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 9.8 years, 15-year projection.

## DCF — v5 final run (2026-10-15)
Growth inputs: the engine's blended growth is 6.40% and g_base is 9.32% after the +2.92pp buyback adjustment. Two cautions, both handled in the scenario design rather than by overriding the base: (1) the blend's OE/share CAGR component (23.06% over 2y) is a trough-recovery artifact off the depressed FY2023 base (COVID-testing unwind plus the Fortrea spin year), not a run rate — revenue signals are the honest ones (5-yr CAGR −0.04%, 3-yr CAGR 5.55%, latest YoY +7.25%, Q2 2026 +5.8%, FY2026 guided +5.4–6.3%); (2) a 9.32% OE/share base start is nonetheless defensible because it is a *per-share earnings* rate, and management's own targets put adjusted EPS CAGR at 8.5–11.5% through 2029 (margin expansion plus buybacks on 5–8% revenue growth). Sanity check against prints: base start 9.3% sits inside the guided EPS range; bull 12.3% sits just above its top end (requires top-end specialty mix and buyback pace — that is what bull means); super bull was trimmed from the default +12pp offset to +7pp (16.3% start) because no print or target supports a >20% sustained OE/share start — the only >20% figure in the file is the trough-recovery artifact named above. Super bear assumes PAMA-style reimbursement cuts and volume loss. Probabilities 10/25/30/25/10; OE multipliers 0.75/0.90/1.00/1.10/1.25. Price $319.51, TTM base $12.50/share.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -2.7% | 0.75 | Reimbursement cuts + volume loss; leverage bites | $61.04 | 4.71% |
| Bear | 25% | 4.3% | 0.90 | Revenue grows but margins/capex absorb it | $100.01 | 6.49% |
| Base | 30% | 9.3% | 1.00 | Guided path: 5–6% revenue, EPS compounding at target pace | $138.80 | 8.22% |
| Bull | 25% | 12.3% | 1.10 | Specialty mix + BLS backlog conversion + buybacks at pace | $174.43 | 9.71% |
| Super bull | 10% | 16.3% | 1.25 | Sustained double-digit specialty growth, EPS above LT target range | $236.57 | 12.12% |

- **Probability-weighted: IV@15% $140.01 (−56.2% vs price), IV@12% $188.48, IV@10% $242.86, weighted IRR 8.29%, base-case IRR 8.22%**
- **Tier by numbers: D.** Diagnostics (key_numbers.md): OE yield 3.91%, terminal value 20.1% of IV@15%, scenario spread 3.88x, net debt 4.82x normalized OE, 9.5 months since FY end.
- The decisive fact: **not one of the five scenarios clears 15% at $319.51** — even super bull returns 12.12% and its IV@15 ($236.57) sits below the price. This is a price problem, not a scenario-design problem.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.5 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, quoted above.
- **BUYBACK_TAILWIND** (share count −2.92%/yr): diluted shares fell from 104,300,000 (FY2016) to 83,800,000 (FY2025) in the CSV; already credited via the +2.92pp growth adjustment in g_base — not double-counted in the verdict.
- **OE_VOLATILE** (OE/share range over the last 5 years spans >3x): real and explained — conservative OE totals in the CSV ran from $2,555,200,000 (FY2021, COVID-testing peak) down to $745,400,000 (FY2023, COVID unwind + Fortrea spin year) and back to $1,080,200,000 (FY2025). The TTM base plus a 35% combined weight on bear-or-worse scenarios handles it; the volatility is a completed COVID cycle, not ongoing cyclicality of the base business.
- **NI_OCF_DIVERGENCE** (NI vs OCF differ by >40% in 2023, 2024, 2025): resolved — it is structural plus spin-era one-offs, not a cash-quality problem. FY2025 net income was $876,500,000 vs OCF $1,640,500,000, and D&A alone was $681,100,000 (non-cash, added back in OCF). FY2023 net income of $418,000,000 was additionally depressed by Fortrea spin-off restructuring and separation charges, early-development goodwill/intangible impairments, and discontinued-operations losses (per the FY2023 earnings-release reconciliations). The OCF-based conservative OE series is therefore the cleaner base, and it is what the engine uses.
- **HIGH_NET_DEBT** (net debt 4.82x normalized OE on the final run): folded into the verdict — $5,052,400,000 of net debt against ~$1B of annual OE means the bear cases have no equity cushion from deleveraging speed, and it is one reason bear-or-worse carries 35%. It is not, however, the binding problem: even the unlevered-looking super-bull case fails the hurdle at this price.

## My thoughts / overlay
- Quality is not the debate: a duopoly franchise, contracted BLS backlog, guided mid-single-digit revenue growth and high-single-to-low-double-digit EPS growth through 2029, disciplined buybacks. At the right price this is exactly the kind of compounder the sweep exists to find.
- The price is the debate: $319.51 against a TTM OE yield of 3.91% leaves no room — the market is capitalizing Labcorp as if the guided EPS path were a floor rather than a target, and paying in advance for the super-bull path (which still only returns 12.12%).
- Method range: narrow. Median base $11.60, TTM base $12.50, latest-FY base $12.89 — every defensible base produces Tier D at this price, because no scenario on any of them clears 15%. The verdict does not depend on which base you pick.
- Hurdle-clearing price: the weighted IV@15% is **$140.01** — the price only clears Andrew's 15% hurdle at roughly that level, and a margin of safety would require buying meaningfully below it (the bear-case IV@15 is $100.01).

## Final verdict
- **Final tier: D** (weighted IRR 8.29% on the v5 final inputs; no tier override — the numbers and the judgment agree)
- Confidence: **Medium** (high on the OE base and the filing data — no gaps, no overrides; medium on any single growth path, and the 3.88x scenario spread plus 4.82x leverage argue against high)
- One-liner: High-quality duopoly lab franchise, moat 6/10, but priced far above owner's-earnings value — weighted IRR 8.3%, IV@15 $140 vs $319.51 price; doesn't clear 15% until ~$140, and even the super-bull case returns only 12.1%.
