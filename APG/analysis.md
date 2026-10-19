# APG — APi Group Corporation
Engine 5.4 run, 2026-10-16. All figures below are copied from key_numbers.md / dcf_numbers.json, ttm.json, or financials_history.csv — none are recomputed. Search-result figures are identified as such.

## What it is
Global provider of life safety, security and specialty services, in two segments: Safety Services (fire detection/suppression, security — design, installation, inspection, service and monitoring, including the Chubb Fire & Security business acquired from Carrier on 2022-01-03 for a $3.1B enterprise value) and Specialty Services (maintenance/repair of underground electric, gas, water, sewer and telecom infrastructure). In scope: market cap $16.707B at $40.19 (nasdaq_quote_api).

## Owner's earnings
**FY2025 (10-K via EDGAR, financials_history.csv):** operating cash flow $759,000,000; capex $96,000,000; SBC $44,000,000 (always a real cost).
- **Conservative owner's earnings FY2025: $619,000,000 = $1.489/share** (latest FY OE/share).
- Maintenance version (from financials_history.csv): $408,000,000 — below the conservative figure, so the conservative OCF-based figure is not the flattering choice; it is also the cleaner series here (see NI_OCF_DIVERGENCE below).
- OE positive 5 of the last 5 fiscal years. Net debt $1.847B (debt total $2.759B less cash $912,000,000, FY2025 history); lease liabilities $304,000,000 on top.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $759,000,000 − prior YTD $145,000,000 + current YTD $168,000,000 = **TTM $782,000,000**
- Capex: FY $96,000,000 − prior YTD $39,000,000 + current YTD $49,000,000 = **TTM $106,000,000**
- SBC: FY $44,000,000 − prior YTD $21,000,000 + current YTD $23,000,000 = **TTM $46,000,000**
- Shares (current-YTD weighted diluted): **435,988,487**
- **TTM OE total $630,000,000 → base OE/share $1.445** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $1.255/share — below both the latest FY ($1.489) and the TTM ($1.445) because it averages in the earlier post-Chubb years. The TTM base is used: it is the most current filing-derived figure and sits between the median and the latest FY, so it is not the flattering choice.

## Moat: 5/10 — moderate / narrow
Justification: statutorily required, recurring life-safety work and leading scale give stickiness, but the model is labor-intensive and locally fragmented, and measured returns are not yet wide-moat level.
- Evidence (fundamentals.json, filing-direct): **ROIC proxy** (after-tax operating income over equity + debt − cash) rose from 2.9% in 2022 to 6.0% in 2023, 7.0% in 2024 and **7.7% in 2025** — improving, but not well above the cost of capital through a cycle, so the spec's bar for a 7+ moat is not met. **Gross margin** expanded steadily: 26.1% (2022), 28.0% (2023), 31.0% (2024), **31.4% (2025)**, on mix shift toward inspection/service/monitoring.
- FOR: statutorily required fire/life-safety inspection, service and monitoring — recurring, non-discretionary demand; scale and route density as a leading global life-safety provider (Chubb platform, 17+ countries); gross margin expansion 26.1% (2022) to 31.4% (2025) on mix shift to inspection/service/monitoring; record backlog over $5B at Q2 2026 and diversified building/infrastructure end markets (backlog is a search-result figure, Q2 2026 earnings reports).
- AGAINST: fragmented local competition and low entry barriers; labor-intensive model with limited pricing power; ROIC proxy only 7.7% in 2025, not proven above cost of capital through a cycle; growth is acquisition-dependent with a goodwill/intangible-heavy balance sheet.
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — engine 5.4 final run (2026-10-16)
Growth sanity check (mandatory): the engine's blended growth is 9.93% (components: rev CAGR 5y 17.14%, rev CAGR 3y 6.45%, latest rev YoY 12.72%, OE/share CAGR 2y 14.72%, with a −5pp share-count adjustment applied to the revenue components only). Recent prints: FY2025 revenue +12.72%, Q2 2026 revenue +13.3% reported / +10.1% organic (search result, Q2 2026 earnings). The base start of 9.93% sits *below* the latest reported prints for a written reason: the reported prints include acquisition contributions (Onyx-Fire and WTech closed in 2026), while management's FY2026 guidance is for 7–9% *organic* growth (search result) — 9.93% sits between the organic guide and the reported prints and is not a momentum extrapolation. The bull start (14.93%) is slightly above the latest print and requires acquisition contribution to continue at the 2026 pace. The super-bull start (21.93%) is above any recent print; it is kept only as a 10%-probability tail (a step-change M&A year), and it does not flatter the verdict — even that scenario's IRR is 13.01%, below the 15% hurdle. The 5-yr CAGR (17.14%) is not trusted as a growth signal because it straddles the Chubb basis break (see FLAGS). Probabilities 10/25/30/25/10 (defaults); OE multipliers 0.75/0.90/1.00/1.10/1.25 (defaults). Price $40.19.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -2.07% | 0.75 | Construction downturn, labor cost squeeze, levered OE compresses | $7.34 | 4.66% |
| Bear | 25% | 4.93% | 0.90 | Organic growth halves, M&A pauses | $11.80 | 6.25% |
| Base | 30% | 9.93% | 1.00 | Blend: organic guide plus modest acquisition contribution | $16.12 | 7.77% |
| Bull | 25% | 14.93% | 1.10 | Reported growth at the latest print persists with M&A | $21.76 | 9.67% |
| Super bull | 10% | 21.93% | 1.25 | Step-change M&A year plus organic acceleration (tail only) | $32.81 | 13.01% |

- **Probability-weighted: IV@15% $17.24 (−57.1% vs price), IV@12% $23.24, IV@10% $29.98, weighted IRR 8.19%, base-case IRR 7.77%**
- **Tier by numbers: D** (bear D, bull D — no TIER_BAND issue). Diagnostics: OE yield 3.60%, terminal value 20.2% of IV@15%, scenario spread 4.47x, net debt 3.07x normalized OE, 9.5 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.5 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, legs quoted above. TTM OE/share $1.445 vs latest FY $1.489: no TTM deterioration that would change the verdict.
- **DILUTION** (share count growing 16.0%/yr): the historical CAGR straddles the SPAC/predecessor era, the Chubb-era share issuance and Series B preferred conversion, and the 3-for-2 stock split completed in Q2 2025 (fundamentals.json notes the 1.5 split ratio). The recent pace is far lower: filed diluted shares rose from 401,513,646 (FY2024) to 415,709,895 (FY2025), and TTM diluted shares are 435,988,487. SBC itself is small — $44,000,000 in FY2025 and $46,000,000 TTM, already deducted in full in owner's earnings. Buybacks have begun: $66,000,000 TTM (fundamentals.json), 1.6M shares repurchased in Q2 2026 (search result). Known future dilution is also small: 4,000,000 Series A preferred shares convert into 6,000,000 common shares on the last day of 2026 (10-K note, via search result). The engine's −5pp growth adjustment is therefore conservative for the forward path, and it is left in place.
- **BASIS_BREAK_SUSPECT**: named — (1) FY2019 revenue of $985,000,000 is on the SPAC predecessor/stub basis (FY2020: $3,587,000,000), and (2) the Chubb Fire & Security acquisition closed 2022-01-03 lifted FY2022 revenue to $6,558,000,000. Growth inputs therefore do not rely on the 5-yr CAGR (17.14%); the blend's usable signals are the 3-yr CAGR (6.45%), the latest YoY (12.72%) and the OE/share CAGR (14.72%), cross-checked against the 7–9% organic guidance.
- **NI_OCF_DIVERGENCE** (net income vs OCF differ by >40% in 2023, 2024, 2025): FY2025 net income $302,000,000 vs OCF $759,000,000. The gap is structural, not a one-off cash problem: net income is depressed by non-cash amortization of the large acquired-intangible base from Chubb and the roll-up (the company's adjusted results explicitly add back amortization expense — search result, Q2 2026 8-K adjustments), plus interest and tax, while OCF is unaffected by the amortization. The OCF-based conservative OE used throughout is therefore the right series; no single tax-deposit or impairment one-off was found.
- **WIDE_SCENARIO_SPREAD** (super-bull IV 4.47x super-bear IV): real, driven mainly by the super-bull tail start. Confidence is capped at medium, and the verdict is sized to the conservative end — which changes nothing here, since even the super-bull scenario is Tier D.
- **HIGH_NET_DEBT** (net debt 3.07x normalized OE on the final diagnostics; 3.54x on the preliminary run): balance sheet from the filing (financials_history.csv, FY2025): debt total $2,759,000,000, cash $912,000,000, net debt $1,847,000,000, plus lease liabilities $304,000,000. Leverage is material and is why the bear/super-bear OE multipliers (0.90/0.75) matter, but debt is termed out and the services cash flow is recurring; management reported net leverage of 2.2x at Q2 2026 on its adjusted EBITDA basis (search result). No tier adjustment — the numbers already produce D in every scenario.

## My thoughts / overlay
- The honest headline is how far the price is from any defensible value: the preliminary run on the median base gave weighted IRR 7.48% / IV@15% $14.98, and the final TTM-base run gives 8.19% / $17.24 — a narrow method range, both firmly Tier D. Even the super-bull scenario (21.93% growth start, 1.25x OE) only reaches a 13.01% IRR.
- Quality is not the debate: OE positive 5/5 years, gross margin up every year since 2022, recurring statutorily required revenue, record backlog, guidance raised in Q2 2026 (FY2026 revenue guided to $8,875–$9,025M and adjusted EBITDA to $1,205–$1,245M — search result). It is a good business at a price that already pays for the bull case.
- Risks: acquisition execution and integration (Onyx-Fire, WTech in 2026 on top of the Chubb base), labor availability/cost in a technician-driven model, construction-cycle exposure in project work, and the leverage above if project revenue softens.

## Final verdict
- **Final tier: D** (weighted IRR 8.19% on the TTM base; method range across the preliminary median-base and final TTM-base runs is 7.48–8.19%, both D, and every scenario including super bull is D)
- Confidence: **Medium** (capped by WIDE_SCENARIO_SPREAD; the D verdict itself is robust — no scenario clears 15%)
- Hurdle-clearing price: it clears 15% only at or below the weighted IV@15% of **$17.24**, vs the $40.19 price.
- One-liner: Solid recurring-revenue services compounder, moat 5/10 — does not clear 15% at $40.19 (weighted IRR 8.2%, IV@15% $17.24; even super bull is 13.0%); it clears 15% only near $17.24.
