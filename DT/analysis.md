# DT — Dynatrace, Inc.
v5 run, 2026-10-16. In scope (market cap $19.442B at $64.01, nasdaq_quote_api — under the $40B cutoff).

All figures below are copied from dcf_numbers.json, ttm.py output, or financials_history.csv — none are recomputed.

## What it is
AI-powered observability platform for large enterprises: OneAgent instrumentation across hybrid/multi-cloud estates, Davis causal AI for root-cause analysis, plus logs, security and AI-workload monitoring, sold largely on the Dynatrace Platform Subscription (consumption) model. Gartner Leader for observability for the 16th consecutive year (2026 Magic Quadrant, company announcement). Q1 FY2027 (quarter ended 2026-06-30, reported 2026-08-05): total ARR $2,136 million, +17% YoY; revenue $555 million, +16%; net new ARR +66% (+41% organic); log-management consumption nearly doubled to ~$200 million annualized; $275 million of stock repurchased in the quarter; CFO Jim Benson announced he will retire by 2027-03-31; the Arize AI-observability acquisition closed 2026-10-01 (per search coverage — a ~$915M deal per Insider Monkey, an integration/execution watch item, not in any filing figure used here).

## Owner's earnings
**FY2026 (10-K via EDGAR, financials_history.csv):** operating cash flow $561,850,000; capex $32,173,000; SBC $299,626,000 (always a real cost).
- **Conservative owner's earnings FY2026: $230,051,000 = $0.76/share** (base_oe_latest_per_share $0.7574)
- Maintenance version FY2026: $238,642,000 — same ballpark as the conservative figure.
- OE positive 5 of the last 5 fiscal years.
- The structural fact of this company: SBC eats more than half of operating cash flow (FY2026 SBC $299,626,000 vs OCF $561,850,000; TTM SBC $301,307,000 vs TTM OCF $598,398,000). Management noted FY2026 SBC was just under 15% of revenue, down >100bp from FY2025 — improving, but the gap between headline free cash flow ($529,677,000 FY2026 in the CSV) and owner's earnings after SBC ($230,051,000) is the whole valuation story here.
- Balance sheet: the CSV shows cash of $1,097,220,000 at FY2026 and no debt balances in the extracted debt fields; the engine's net_debt_latest is null. There is no leverage risk, but the cash pile is small next to a $19.442B market cap and does not change the verdict.

**Base used = TTM owner's earnings through Q1 FY2027, from ttm.py (filing-direct, no hand math):**
- OCF: FY $561,850,000 − prior YTD $269,692,000 + current YTD $306,240,000 = **TTM $598,398,000**
- Capex: FY $32,173,000 − prior YTD $7,482,000 + current YTD $3,151,000 = **TTM $27,842,000**
- SBC: FY $299,626,000 − prior YTD $71,895,000 + current YTD $73,576,000 = **TTM $301,307,000**
- Shares (current-YTD weighted diluted, per ttm.py's stated basis): **293,744,000** — down from the FY2026 weighted 303,727,000 after the Q1 buyback
- **TTM OE total $269,249,000 → base OE/share $0.9166** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $0.5323/share — not used as the base; see BASE_DIVERGENCE under Flags.

## Moat: 6/10 — moderate, real but contested
Justification: a genuine enterprise-grade platform with causal-AI differentiation and deployment switching costs, in a category where two rivals are bigger and the ingest layer is being commoditized; growth is decelerating (revenue +23.5% 5-yr CAGR → +18.8% latest FY → +16% in Q1 FY2027, FY2027 revenue guided to roughly +14.6% per Trefis's summary of guidance) and expansion economics are good rather than elite.
- FOR: Davis causal AI on a unified platform — deterministic root-cause answers rivals approximate with correlation; Gartner Leader 16 straight years
- FOR: OneAgent deployed across the whole enterprise estate — ripping it out is a real project, so incumbent positions are sticky; vendor-consolidation onto Dynatrace is management's top sales play and Q1 new-logo ARR growth was >160%
- FOR: Consumption (DPS) pricing lets spend expand with data volume; logs and AI-workload observability are new expansion vectors (logs ~$200M annualized and nearly doubling)
- AGAINST: Datadog has larger scale and broader product surface; Cisco-Splunk is larger still — Dynatrace is #3 in a three-body market
- AGAINST: Hyperscaler bundled monitors (CloudWatch / Azure Monitor), open-source Grafana/OpenTelemetry, and cheaper New Relic pricing pressure the category from below; OpenTelemetry standardizes the ingest layer Dynatrace charges for
- AGAINST: SBC at just under 15% of revenue — the equity-comp load that keeps owner's earnings thin is itself evidence pricing power does not drop to the bottom line
- A 6 gives CAP = 9.8 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 9.8 years, 15-year projection.

## DCF — v5 final run (2026-10-16)
Growth recalibration (written reason): the engine's blended growth is 21.90% and g_base 20.53%, but those blends lean on the 5-yr revenue CAGR (23.47%) and the OE/share CAGR 2y (26.03%). The current revenue prints are lower and decelerating — latest FY revenue YoY +18.82%, Q1 FY2027 revenue +16%, ARR +17%, FY2027 revenue guided ~+14.6%. Scenario starts were therefore set via offsets (−0.135 / −0.085 / −0.035 / +0.015 / +0.065 vs g_base) to 7.03 / 12.03 / **17.03** / 22.03 / 27.03%. The base start (17.03%) sits between the revenue guide and the faster OE/share trajectory (buybacks plus a falling SBC ratio give OE/share leverage over revenue); the super-bull start (27.03%) exceeds every revenue print but is in line with the printed OE/share CAGR 2y of 26.03% — that is its written justification. Probabilities at the 10/25/30/25/10 defaults; OE multipliers at the 0.75/0.90/1.00/1.10/1.25 defaults. Base OE/share $0.9166 (TTM). Price $64.01.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | 7.03% | 0.75 | Hyperscaler/open-source squeeze + Datadog share gains stall growth | $6.90 | 3.94% |
| Bear | 25% | 12.03% | 0.90 | Guided deceleration continues; SBC ratio stops falling | $10.33 | 4.77% |
| Base | 30% | 17.03% | 1.00 | Mid-teens revenue growth, slow SBC-ratio improvement, buybacks continue | $14.32 | 5.75% |
| Bull | 25% | 22.03% | 1.10 | Consolidation wins + logs/AI observability re-accelerate growth | $19.63 | 7.00% |
| Super bull | 10% | 27.03% | 1.25 | OE/share compounds at its 2-yr CAGR pace for years | $27.73 | 8.77% |

- **Probability-weighted: IV@15% $15.25 (−76.18% vs price), IV@12% $21.04, IV@10% $27.59, weighted IRR 6.00%, base-case IRR 5.75%**
- **Tier by numbers: D.** Diagnostics: OE yield 1.43%, terminal value 22.69% of IV@15%, scenario spread 4.02x, 6.54 months since FY end.

## Flags — every fragility flag resolved
- **NI_OCF_DIVERGENCE** (net income vs OCF differ >40% in 2024, 2026): explained, and it does not contaminate the base. The dominant bridge is SBC — a non-cash expense of $208,896,000 in FY2024 and $299,626,000 in FY2026 (financials_history.csv) that depresses net income ($154,632,000 FY2024; $162,669,000 FY2026) but not OCF ($378,109,000; $561,850,000). The adjacent distorting year is FY2025, whose net income of $483,684,000 was flattered by an income-tax benefit (tax line −$260,255,000 in the CSV; FY2026 swung back to a $137,092,000 expense). The conservative OE definition starts from OCF and subtracts SBC in full, so neither the SBC addback nor the tax one-off inflates the base.
- **BASE_DIVERGENCE** (latest FY OE/share $0.76 vs 3-yr median $0.53): the median is the stale one, not the distorted one — it averages in FY2024 ($142,754,000 total OE) before the OCF ramp and the SBC-ratio improvement. The latest FY is corroborated by the TTM run, which is higher still ($0.9166/share on OCF growth and a buyback-reduced share count). Resolution: TTM base used; median retained in the reporting.
- **LOW_OE_YIELD** (base OE yield 1.43%): real and decisive. At $64.01 the buyer gets $0.9166 of TTM owner's earnings per share; the entire case rests on growth, and even the super-bull path (27.03% start, 1.25x OE) only reaches an 8.77% IRR. This flag is the verdict, not a caveat on it.
- **WIDE_SCENARIO_SPREAD** (super-bull IV 4.02x super-bear IV): real — outcomes genuinely span a wide range. Confidence is capped at medium. It does not soften the verdict, because the spread sits entirely below the hurdle: every scenario, super bull included, prices below $28 at a 15% discount rate against a $64.01 price.

## My thoughts / overlay
- Quality is not the problem; price is. This is a debt-free, GAAP-profitable, 26%-FCF-margin platform growing mid-teens with a strong competitive seat — and owner's earnings after SBC are $269,249,000 TTM against a $19.442B market cap. The market is pricing Dynatrace on pre-SBC free cash flow; on an owner's-earnings basis the stock needs to roughly halve twice over before the weighted case clears 15%.
- Method range: narrow for once. Median base instead of TTM, or default growth offsets instead of the recalibrated ones, move the weighted IRR within the D band (the preliminary run on the median base printed 4.79%); no defensible input set gets this price near the 15% hurdle, because the binding constraint is the 1.43% starting OE yield, not the growth path.
- Watch items that could change the picture over time: whether the SBC ratio keeps falling toward peer levels (each point of revenue is real OE), whether the Arize acquisition and the CFO transition execute cleanly, and whether net new ARR acceleration (+41% organic in Q1) sustains — none of them close a 76% valuation gap on any near-term path.
- Margin of safety: the price that clears 15% on the weighted case is the weighted IV@15% itself, $15.25 — about 76% below the current price. There is no margin of safety at $64.01 under any scenario in the table.

## Final verdict
- **Final tier: D** (weighted IRR 6.00% on the v5 final inputs; every scenario, including super bull at 8.77%, sits in D)
- Confidence: **Medium** (capped by the wide scenario spread; the D conclusion itself is insensitive to base and growth choices)
- One-liner: Quality observability franchise, moat 6/10, but SBC consumes over half of OCF and the $64.01 price is ~4x the $15.25 weighted IV@15% — fails the 15% hurdle in every scenario; it would need to fall to ~$15 to clear it.
