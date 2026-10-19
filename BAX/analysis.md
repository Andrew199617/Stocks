# BAX — Baxter International Inc.
Engine 5.4.0 run, 2026-10-18. Market cap $12,968,640,000 at $25.28 (nasdaq_quote_api) — in scope under $40B.

All figures below are copied from dcf_numbers.json, ttm.json, financials_history.csv, or fundamentals.json — none are recomputed.

## What it is
Global medtech / hospital-supplies company on a continuing-operations basis after selling its Kidney Care business (Vantive) to Carlyle, closed January 2025: U.S. leader in IV solutions, plus infusion systems (Spectrum IQ; Novum IQ still on a shipment/installation hold), pharmaceuticals (injectables and drug compounding), advanced surgery, and the Hillrom hospital beds / connected-care business (Healthcare Systems & Technologies) acquired in 2021 for ~$10.5B. Q2 2026 (search results, Business Wire release and earnings summaries): worldwide sales $2.96B, +5% reported and organic; adjusted EPS $0.56 including a one-time ~$0.11 IEEPA tariff refund; full-year 2026 guidance raised to reported sales +3–4%, organic +2–3%, adjusted EPS $1.95–$2.15, adjusted operating margin 13–14%, with a stated priority of cutting net leverage to ~3x by year-end.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $845,000,000; capex $513,000,000; SBC $117,000,000 (always a real cost).
- **Conservative owner's earnings FY2025: $215,000,000 = $0.42/share** (base_oe_latest_per_share $0.4191 in dcf_numbers.json)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): **−$1,847,000,000** in FY2025 — this version is distorted by the GAAP net loss (−$957,000,000, which carries noncash impairments and other special items, see NI_OCF_DIVERGENCE below) and a $1,358,000,000 working-capital swing in the history file, so the OCF-based conservative figure is the cleaner series and is used throughout.
- OE positive 5 of the last 5 fiscal years, but collapsing: OE/share $2.73 (2021), $1.38 (2022), $2.32 (2023), $0.90 (2024), $0.42 (2025). Net debt $7,510,000,000 at FY2025 (total debt $9,476,000,000, cash $1,966,000,000, lease liabilities $304,000,000, equity $6,129,000,000 — fundamentals.json), a legacy of the debt-funded Hillrom acquisition (net debt was $14,709,000,000 in FY2021).

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $845,000,000 − prior YTD $24,000,000 + current YTD $498,000,000 = **TTM $1,319,000,000**
- Capex: FY $513,000,000 − prior YTD $262,000,000 + current YTD $253,000,000 = **TTM $504,000,000**
- SBC: FY $117,000,000 − prior YTD $45,000,000 + current YTD $43,000,000 = **TTM $115,000,000**
- Shares (current-YTD weighted diluted): **517,000,000**
- **TTM OE total $700,000,000 → base OE/share $1.3540** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $0.90/share and the latest FY is $0.42/share — both are reported and neither is used as the base; see BASE_DIVERGENCE below. The TTM base is the most current filing-derived figure and still sits well below the $2.32–$2.73/share Baxter earned in 2021–2023.

## Moat: 4/10 — weak to moderate
Justification: a real installed-base and scale position in mission-critical hospital categories, but commodity-like core products, GPO pricing pressure, and a return-on-capital record that has collapsed — the measured history does not support a moat above 4.
- FOR: largest IV solutions supplier in North America with an extensive manufacturing network (search result, market landscape); installed base of infusion pumps and Hillrom hospital beds / patient-support systems creating consumables, service and replacement pull-through; mission-critical, regulated products with long hospital qualification cycles and real switching friction; scale across IV, compounding, surgery and connected care.
- AGAINST: IV fluids are commodity-like with hospital/GPO pricing power sitting with the buyer — Fresenius Kabi, B. Braun and others contest every category; no demonstrated pricing power in the numbers (gross margin and ROIC below); the Hillrom "moat" was overpaid for — ~$3.1B of goodwill/intangible impairments followed within a year of the 2021 acquisition (search result); quality and supply disruptions erode the franchise (Novum IQ shipment/installation hold still unresolved, infusion-pump field corrective actions, Hurricane Helene plant disruption, injectables supply constraints at a contract manufacturer); high leverage limits investment.
- **ROIC evidence (roic_proxy in fundamentals.json):** 14.14% (2019), 12.45% (2020), 5.25% (2021), −10.78% (2022), 2.77% (2023), 0.06% (2024), −1.78% (2025) — below any plausible cost of capital for five straight years.
- **Gross margin (fundamentals.json):** 41.90% (2019), 39.30% (2020), 38.86% (2021), 35.29% (2022), 40.06% (2023), 37.46% (2024), 30.05% (2025); TTM through Q2 2026 is 30.08% — level down ~12pp from 2019 and not yet recovering in the TTM window (Q2 2026 alone: 34.86%).
- A 4 gives CAP = 7.2 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 7.2 years, 15-year projection.

## DCF — engine 5.4.0 final run (2026-10-18)
Growth sanity check (mandatory): the engine's blended start is 0.93% (components: revenue CAGR 5y −0.75%, 3y +3.79%, latest FY revenue YoY +5.72%, OE/share CAGR 2y −57.48%). Recent prints are stronger on sales — TTM revenue YoY +5.36% and Q2 2026 revenue YoY +5.34% (fundamentals.json), and management guides FY2026 organic sales to +2–3% (search results). Written reasons for the scenario starts: (1) the base start of 0.93% is an OE/share start, not a sales start — it sits below the sales prints deliberately, because near-term OE faces the roll-through of higher-cost inventory produced at the end of 2025, the Novum IQ hold, and injectables supply constraints, so OE growth lags sales near-term; (2) the bull start of 5.93% is in line with the latest sales prints; (3) the super-bull start of 12.93% is an OE operating-leverage case — gross margin recovering from 30.05% toward its historical 38–40% range on a flat-to-modest sales base — not a sales forecast, and it is weighted only 5%. Probabilities were bear-shifted from the 10/25/30/25/10 defaults to 15/30/30/20/5 for OE volatility and leverage (see FLAGS); OE multipliers are the defaults 0.75/0.90/1.00/1.10/1.25. Price $25.28.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | −10.00% | 0.75 | IV conservation becomes permanent, Novum hold spreads, levered OE squeezed | $5.11 | 4.72% |
| Bear | 30% | −4.07% | 0.90 | Margin stays near 30%, sales flat-to-down, deleveraging absorbs all cash | $7.74 | 6.14% |
| Base | 30% | 0.93% | 1.00 | TTM OE holds, sales grow at guide, no gross-margin recovery | $10.45 | 7.62% |
| Bull | 20% | 5.93% | 1.10 | Sales at recent prints, partial margin recovery, Novum clears | $13.93 | 9.48% |
| Super bull | 5% | 12.93% | 1.25 | Full operating leverage: margin back toward 38–40%, leverage falls | $20.60 | 12.84% |

- **Probability-weighted: IV@15% $10.04 (−60.29% vs price), IV@12% $13.18, IV@10% $16.66, IV@20% $7.20, IV@25% $5.62, weighted IRR 7.43%, base-case IRR 7.62%**
- **Tier by numbers: D** — the bear and bull scenarios are both Tier D (bear IRR 6.14%, bull IRR 9.48%), and even the super-bull case at 12.84% only reaches Tier C. Diagnostics (dcf_numbers.json): OE yield 5.36%, terminal value 17.56% of IV@15%, scenario spread 4.03x, net debt 10.81x normalized OE, 9.56 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.56 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, legs quoted above.
- **OE_VOLATILE** (OE/share range over the last 5 years spans >3x — actually $0.42 to $2.73): real, driven by the Hillrom debt/impairment cycle, the Vantive separation, and the FY2025 margin collapse, not ordinary cyclicality. Handled by bear-shifted probabilities (45% on bear-or-worse, super bull cut to 5%) and confidence capped at low.
- **NI_OCF_DIVERGENCE** (net income vs OCF differ by >40% in 2024, 2025): FY2024 net income −$649,000,000 vs OCF $1,019,000,000; FY2025 net income −$957,000,000 vs OCF $845,000,000. The filings' own special-item notes (search results, Baxter results releases) name the drivers: restructuring and business-optimization costs tied to the post-Vantive cost program and the new operating model, Hillrom integration costs including a noncash PPE impairment in 2025, infusion-pump field corrective action warranty/remediation charges, EU medical-device-regulation compliance costs, and — in FY2025 — tax expense of $395,000,000 despite a pretax loss of −$505,000,000 (fundamentals.json). These are largely noncash or below-the-OCF-line items, which is exactly why the OCF-based conservative OE is the series used; the cash restructuring burden itself remains inside OCF and is not added back.
- **BASE_DIVERGENCE** (latest FY $0.42 vs 3-yr median $0.90): the latest FY is the distorted one on the downside — Q4 2025 alone printed a 19.4% gross margin and −$729,000,000 operating income (fundamentals.json quarterly), on high-cost inventory and year-end charges, dragging FY2025 gross margin to 30.05%. The median is also not clean: it mixes the stronger pre-separation years with the collapse. The TTM base ($1.3540) is used instead: it includes the weak Q4 2025, and its OCF recovery (TTM OCF $1,319,000,000 vs FY2025 $845,000,000) is filed, not projected.
- **WIDE_SCENARIO_SPREAD** (super-bull IV 4.03x super-bear IV): real — the outcome range is dominated by whether gross margin ever recovers. Confidence is low, and the verdict is sized to the conservative end; note every scenario is Tier D regardless, so the spread does not change the tier.
- **HIGH_NET_DEBT** (net debt 10.81x normalized OE in the final diagnostics): balance sheet stated from the filing in the OE section above — total debt $9,476,000,000 against cash $1,966,000,000 and equity $6,129,000,000, plus $304,000,000 of lease liabilities. This is Hillrom acquisition debt being worked down (net debt $14,709,000,000 at FY2021); management targets ~3x net leverage by end-2026 (search results) and the declared dividend was cut to $0.01/quarter in 2026 from $0.17/quarter in 2025 (fundamentals.json dividends), preserving cash — but at the final run's OE the leverage still means a margin relapse hits equity OE first.

## My thoughts / overlay
- The honest headline is the method range, and it is narrow for once: on the normalized $0.90 median base the preliminary run printed weighted IRR 6.20% and IV@15% $7.42; on the recovered TTM $1.3540 base the final run prints 7.43% and $10.04. Both are Tier D, and in the final run no scenario clears the 15% hurdle — only the 5%-weighted super bull clears even 10%. The conclusion does not depend on the base choice.
- Quality is the debate, and the filings answer it: this was a 12–16% ROIC, ~42% gross-margin business in 2018–2019 (fundamentals.json), and it has earned roughly zero on invested capital for five years while gross margin fell to 30%. That is a broken return profile, not a temporarily depressed one — the recovery case requires margin repair that has not yet appeared in a TTM window.
- The Q2 2026 beat is real but flattered: adjusted EPS included a ~$0.11 one-time tariff refund (search results), GAAP TTM net income is still −$1,063,000,000 and TTM operating income −$274,000,000 (fundamentals.json TTM), and IV-solutions demand sits at a post-Helene "new norm" of fluid conservation with the Novum IQ hold unresolved.
- Hurdle math: at $25.28 the market is paying roughly 2.5x the weighted IV@15%. The stock clears a 15% hurdle only at or below $10.04, a 20% hurdle at or below $7.20, and a 25% hurdle at or below $5.62 (dcf_numbers.json hurdle prices).

## Final verdict
- **Final tier: D** (weighted IRR 7.43% on the TTM base; Tier D on the median base as well, with the bear and bull scenarios both Tier D and only the 5%-weighted super bull reaching Tier C)
- Confidence: **Low** (WIDE_SCENARIO_SPREAD, OE_VOLATILE and HIGH_NET_DEBT all unresolved as business facts, even though each is resolved analytically above)
- One-liner: Levered hospital-supplies incumbent, moat 4/10 — even on recovered TTM owner's earnings it does not clear 15% (weighted IRR 7.4%, IV@15% $10.04 vs $25.28 price); it clears 15% only below ~$10.04.
