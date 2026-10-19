# LII — Lennox International Inc
Engine 5.4.0 run, 2026-10-18. All figures below are copied from dcf_numbers.json, ttm.json, financials_history.csv, or fundamentals.json — none are recomputed.

## What it is
North American HVACR manufacturer (SIC 3585): premium residential heating/cooling (Home Comfort Solutions) and commercial building climate systems (Building Climate Solutions), plus refrigeration. One of the North American "big four" alongside Carrier, Trane Technologies and Daikin in commercial HVAC, which collectively hold an estimated 50–60% of that market (web search, industry market report). Differentiates on premium residential branding, high SEER2 efficiency ratings and a direct-to-dealer relationship; a 2024 Samsung joint venture added ductless/VRF exposure. FY2025 revenue $5,195,300,000, down from $5,341,300,000 in FY2024 (latest revenue YoY −2.73% in dcf_numbers.json).

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $757,600,000; capex $118,800,000; SBC $29,100,000 (always a real cost; small here at ~0.6% of revenue per fundamentals.json history).
- **Conservative owner's earnings FY2025: $609,700,000 = $17.22/share** (OCF − capex − SBC).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $432,000,000 in FY2025 — materially below the conservative figure because of a working-capital build, and wildly volatile across years ($1,008,000,000 in FY2024, −$61,500,000 in FY2023 on the same definition in financials_history.csv). The OCF-based conservative series is the cleaner base; the maintenance series is a working-capital-noise warning, not the base.
- OE positive 5 of the last 5 fiscal years (dcf_numbers.json), but the per-share range is wide: $10.25 (2021), $5.01 (2022), $12.77 (2023), $21.05 (2024), $17.22 (2025) — see OE_VOLATILE below.
- Net debt $1,354,200,000 (dcf_numbers.json; basis LongTermDebtAndCapitalLeaseObligations + current portion + Commercial Paper), plus lease liabilities $382,300,000. Net debt is 2.12x normalized OE (diagnostics). Share count is roughly flat to slightly shrinking: share CAGR −0.37%/yr, diluted count 35,400,000 in FY2025 vs 44,000,000 in 2016 after years of buybacks (fundamentals.json: $416,600,000 of buybacks in the TTM window it covers).

**Base used = TTM owner's earnings through Q1 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $757,600,000 − prior YTD −$35,800,000 + current YTD $16,100,000 = **TTM $809,500,000**
- Capex: FY $118,800,000 − prior YTD $25,500,000 + current YTD $55,500,000 = **TTM $148,800,000**
- SBC: FY $29,100,000 − prior YTD $6,300,000 + current YTD $6,300,000 = **TTM $29,100,000**
- Shares (current-YTD weighted diluted): **35,000,000**
- **TTM OE total $631,600,000 → base OE/share $18.05** (base_source: ttm_json)
- The engine's normalized base (median of last 3 FY OE/share) is $17.22/share — close to the TTM figure, so the base choice is not load-bearing here (no BASE_DIVERGENCE flag). TTM is used because FY2025 ended 9.6 months ago (STALE_FY).
- Data note: the Q2 2026 10-Q (period 2026-06-30, filed 2026-07-29 per fundamentals.json profile) is not yet in EDGAR companyfacts — fundamentals.json states annual/quarterly rows, TTM flows and dividends stop at 2026-03-31 for that reason. So the filing-direct TTM legitimately ends at Q1 2026. Press coverage of Q2 2026 (web search, not used in any figure): revenue $1.55 billion, +3% YoY, GAAP EPS $7.72 flat YoY, residential unit volumes down ~12% with commercial/BCS revenue up strongly; full-year 2026 EPS guidance was cut to $23.00–$24.00 while enterprise revenue growth guidance of ~8% (including acquisitions; Home Comfort ~+1%, Building Climate ~+20%) and $750–$850M free-cash-flow guidance were maintained. That mix — flat earnings, weak residential, strong commercial — is consistent with the TTM base, not a step-change from it.

## Moat: 6/10 — moderate, top of the moderate band
Justification: a rational big-four oligopoly with a premium brand, direct dealer network and demonstrated pricing power, earning very high measured returns on capital — but the product is equipment a homeowner replaces through an installer, switching costs are low, and Trane/Carrier/Daikin are equally strong rivals, so there is no wide-moat structure (no network effect, no captive installed base, little recurring revenue).
- Evidence first (fundamentals.json, annual): **roic_proxy** (after-tax operating income over equity + debt − cash) was 52.15% (2021), 41.74% (2022), 38.67% (2023), 49.83% (2024), 33.45% (2025) — well above any plausible cost of capital through the cycle, albeit flattered by a buyback-shrunk equity base. **Gross margin** rose from 28.34% (2021) and 27.23% (2022) to 31.10% (2023), 33.28% (2024) and 33.39% (2025), and operating margin from 14.07% (2021) to 20.05% (2025) — that expansion through a refrigerant transition and a soft residential market is proven pricing power / mix discipline (management walked away from low-margin new-construction volume in 2026 rather than chase it, per Q2 coverage).
- FOR: Big-four oligopoly structure with rational pricing in North American HVAC; premium residential brand and highest-tier efficiency ratings; direct-to-dealer distribution relationship; commercial/BCS share gains and national-account wins in 2026, with bolt-on M&A (Comfort-Aire/Century/Coast-Air) adding parts/accessories breadth; replacement-driven demand (~75% of residential sales are replacement, per industry coverage) makes the revenue base less cyclical than new construction alone.
- AGAINST: Low end-customer switching costs — the installer/dealer, not Lennox, owns the replacement decision; Trane is extending its commercial lead and Carrier/Daikin match Lennox on efficiency and scale; no meaningful recurring/service revenue moat; earnings are housing- and rate-sensitive (residential volumes −12% YoY in Q2 2026); the R-454B low-GWP refrigerant transition raises component costs (leak-detection sensors), training burden and share-loss risk if mishandled; regulatory/tax-credit policy can shift demand overnight.
- A 6 gives CAP = 9.8 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 9.8 years, 15-year projection.

## DCF — final run (engine 5.4.0)
Growth sanity check: the engine's blended growth start is 5.71% (components: 5-yr revenue CAGR 7.41%, 3-yr 3.26%, latest FY revenue YoY −2.73%, OE/share 2-yr CAGR 16.12%). Against actual recent prints — FY2025 revenue −2.73%, Q1 2026 revenue +5.83% YoY (fundamentals.json quarterly), Q2 2026 revenue +3% YoY (web search), and FY2026 guided enterprise revenue growth ~8% including ~4pp from acquisitions — a 5.71% base start sits inside the observed/guided range and needs no recalibration. The default bull offsets were, however, recalibrated down (written reason): the default super-bull start of 17.71% has no support in any recent print (the last double-digit revenue years were the 2021–22 post-COVID boom), so offsets were set to −12 / −5 / 0 / +3 / +8pp, giving starts of −6.29% / +0.71% / **+5.71%** / +8.71% / +13.71%. Probabilities were bear-widened to 15/30/30/15/10 per the OE_VOLATILE flag (defaults 10/25/30/25/10). OE multipliers are the defaults 0.75/0.90/1.00/1.10/1.25. Price $357.73 (nasdaq_quote_api); market cap est. $12,663,642,000 — in scope under $40B.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | −6.29% | 0.75 | Housing slump deepens, refrigerant-transition share loss, OE revisits 2022-type trough | $75.10 | 4.80% |
| Bear | 30% | +0.71% | 0.90 | Residential recovery slips into 2027+, commercial only offsets | $122.98 | 6.72% |
| Base | 30% | +5.71% | 1.00 | Guided ~8% total / ~4% organic growth decays normally over the CAP | $170.70 | 8.61% |
| Bull | 15% | +8.71% | 1.10 | 2027 residential rebound plus continued BCS share gains | $214.57 | 10.24% |
| Super bull | 10% | +13.71% | 1.25 | Full replacement supercycle plus heat-pump electrification tailwind | $304.38 | 13.33% |

- **Probability-weighted: IV@15% $161.99 (−54.7% vs price), IV@12% $215.31, IV@10% $274.82, weighted IRR 8.30%, base-case IRR 8.61%**
- **Tier by numbers: D.** Diagnostics (dcf_numbers.json): OE yield 5.04%, terminal value 18.8% of IV@15%, scenario spread 4.05x, net debt 2.12x normalized OE, 9.6 months since FY end.
- Even the super-bull case (13.33% IRR, IV@15% $304.38) sits below the $357.73 price — no scenario in the set clears a 15% hurdle at this price. The price that clears 15% on the weighted case is the weighted IV@15% itself: **$161.99**; $114.13 clears 20% and $87.80 clears 25%.

## Flags — every fragility flag resolved
- **STALE_FY** (latest fiscal year ended 10 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q1 2026, legs quoted above. The Q2 2026 10-Q is filed but not yet in EDGAR companyfacts (fundamentals.json note), so no filing-direct TTM through Q2 exists yet; Q2 press prints (flat EPS, +3% revenue) do not suggest a materially different base.
- **OE_VOLATILE** (OE/share range over the last 5 years spans >3x — $5.01 in 2022 to $21.05 in 2024): real cyclicality, driven by OCF swings ($302,300,000 in 2022 vs $945,700,000 in 2024) and working-capital swings (see the maintenance-OE series above), not by share count. Handled three ways: the base is a TTM figure close to the 3-yr median ($18.05 vs $17.22), bear weight was widened (super bear + bear = 45% vs 35% default), and confidence is capped below high.
- **WIDE_SCENARIO_SPREAD** (super-bull IV 4.05x super-bear IV): real — the outcome range for a cyclical equipment maker at a premium price IS wide. Confidence is not high, and the verdict is sized to the bear end.
- **TIER_BAND** (bear-case tier D at 6.72% vs bull-case tier C at 10.24%): the verdict spans D–C across bear→bull; sized to the bear end, the tier is D either way — the weighted result (8.30%) is itself in D, so the band does not change the verdict, only its confidence.

## My thoughts / overlay
- This is a quality cyclical being priced as if the cycle does not exist. The franchise evidence is genuinely good — ROIC proxy 33–52% for five straight years, gross margin up ~5pp in three years, disciplined exit from low-margin volume — but at $357.73 the market is paying for more than even the super-bull scenario delivers inside this standardized model (super-bull IV@15% $304.38 < price).
- Method range: the preliminary default run (median base $17.22, moat 5, default probs/offsets) printed weighted IRR 8.73% / IV@15% $172.78; the final run (TTM base, moat 6, bear-widened probs, tempered bull offsets) prints 8.30% / $161.99. Every defensible variant is Tier D — the method range is narrow in verdict terms (D to D), which raises confidence in the tier even though the scenario spread is wide.
- Balance sheet is not the problem: net debt 2.12x normalized OE, maintained free-cash-flow guidance, ongoing buybacks and dividends. The problem is purely entry price versus a mid-single-digit growth, cyclical OE stream.
- Risks to the D (i.e., what would make it better than modeled): a sharp 2027 residential replacement rebound, BCS compounding at ~20% with acquisitions, or a much lower entry price. Risks to the downside: prolonged high rates, R-454B transition share loss to Trane/Daikin, tariff costs.

## Final verdict
- **Final tier: D** (weighted IRR 8.30% on the final inputs; bear D 6.72%, bull C 10.24% — sized to the bear end)
- Confidence: **Medium** (high on the filing-direct OE base and on the verdict's insensitivity to method; capped below high by WIDE_SCENARIO_SPREAD and OE_VOLATILE)
- One-liner: High-quality HVAC oligopolist, moat 6/10 — but at $357.73 it does not clear 15% in any scenario (weighted IRR 8.3%, IV@15% $161.99); it would need to fall to ~$162 to clear the 15% hurdle.
