# APP — AppLovin Corporation
v5 run, 2026-10-13 (supersedes the v4 pilot analysis of 2026-10-12; the v4 method history is summarized under Thoughts). **Exception to the <$40B scope** (market cap $93.112B at $272.28, nasdaq_quote_api) — kept as the worked example / engine test case only. This is also the worked example of the v5.1 override mechanism — see OVERRIDE.

All figures below are copied from key_numbers.md, dcf_numbers.json, or ttm.py output — none are recomputed.

## What it is
Pure-play AI advertising software since selling its game studios in 2025: AXON ad engine, MAX mediation, Adjust attribution, Wurl CTV. Asset-light, ~82-84% adjusted EBITDA margins.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $3,971,094,000; SBC $210,421,000 (always a real cost); capex $19.0M — by override, see below.
- **Conservative owner's earnings FY2025: $3,741,673,000 = $10.94/share** (key_numbers.md: latest FY OE/share $10.94; the v4 zero-filled figure was $11.00/share before the capex override)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $3,457,309,000 — same ballpark as the conservative figure, which raises confidence. FY2025 net income includes the apps-divestiture gain; the OCF-based conservative figure is the cleaner one because the gain is non-operating/investing.
- OE positive 5 of the last 5 fiscal years. Net debt $1.026B (key_numbers.md). Buybacks were $2.19B in FY2025 per the 10-K review in the v4 pass.
- History caveat: 2023-25 are on a continuing-operations basis after the divestiture, 2019-22 are total-company as originally filed — there is a comparability break at 2023. The 5-yr revenue CAGR (30.45%) mixes bases; the continuing business grew +69.99% in FY2025 (latest rev YoY, key_numbers.md) and H1 2026 prints ran +53-56%.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $3,971,094,000 − prior YTD $1,603,938,000 + current YTD $2,160,433,000 = **TTM $4,527,589,000**
- SBC: FY $210,421,000 − prior YTD $97,026,000 + current YTD $168,981,000 = **TTM $282,376,000**
- Capex: **TTM $18,947,945**, all three legs filled by the override (see OVERRIDE)
- Shares (current-YTD weighted diluted): **337,875,000**
- **TTM OE total $4,226,265,055 → base OE/share $12.51** (base_source: agent_supplied_ttm_override)
- The engine's normalized base (3-yr median) is $4.96/share — rejected as the base for the same reason as v4: it is dragged by pre-inflection years (FY23 OE/share $1.91 on the filed history). It is still reported in key_numbers.md and used in the override-impact measurement below.

## OVERRIDE — capex (the v5.1 worked example)
- **The gap:** AppLovin files no capex under any candidate tag from FY2025 onward. Under v5's data gate the preliminary engine run exited 4 with `DATA_GAP:capex` (dcf_numbers.json data_gap: ["capex"]) — no tier, correctly.
- **The decision (main agent, per Andrew's 2026-10-13 rule — the agent decides, and the decision lands in a field):** judgment.json carries `capex_override = {value: 19000000, kind: "estimate", source: "Higher of the last tagged FY2024 capex ($4.8M, FY24 10-K) and the v4 TTM estimate (~$19M), per Andrew's conservative rule (2026-10-13)", reason: "AppLovin tags no capex from FY2025 onward under any candidate tag. Tagged capex ran $0.7–4.8M/yr FY19–24 vs OCF in the billions — structurally immaterial; $19M is ~4x the last filed figure and still moves base OE by <0.5%."}`. Filed capex FY19–24 was $3.4M / $3.2M / $1.4M / $0.7M / $4.2M / $4.8M against OCF of $2.1B (FY24) and $4.0B (FY25) — zero was defensible, but the conservative sourced figure was chosen. The override fills ONLY periods where the tag is absent (FY25 in the annual history: capex_tag = "OVERRIDE" in financials_history.csv); filed values are never replaced.
- **How it was applied:** the engine filled FY2025 annual capex (overrides_applied periods_filled: ["2025-12-31"]); ttm.py filled all three capex legs on the OCF anchor timeline, prorated by days (FY leg $18,947,945 over 364 days; both YTD legs $9,369,863 over 180 days; they cancel in the TTM math, leaving TTM capex $18,947,945) and reported them in overrides_used with no CAPEX_NOT_FILED warning.
- **Measured impact (from dcf_numbers.json override_impact + ttm.py output):** on the engine-native base the override moves nothing — normalized base OE/share $4.96 zero-fill → $4.96 with override, engine-native weighted IRR 10.28% → 10.28% — because the FY25 year is not the median year. The binding effect is on the TTM base actually used: $12.57/share in the v4 zero-filled run → **$12.51/share** with the override (−0.45%, inside the <0.5% bound in the override's reason). Its other effect is binary: without it there is no tier at all.
- The override is recorded in score.json ("overrides") and in the central registry (_system/overrides_registry.json), and the ranking shows APP with a "capex: AI estimate" badge.

## Moat: 6/10 — moderate-strong, not wide
Justification: AXON + MAX data flywheel and integration switching costs, but inputs are bought not owned, the model lead is re-earned quarterly, Unity Vector is closing, and platform privacy rules are a hostage risk.
- FOR: AXON model plus the data flywheel from MAX mediation's installed publisher base; deep integrations and real switching friction for publishers and advertisers; proven pricing power — net revenue per install compounding; asset-light cost structure rivals can't easily undercut.
- AGAINST: raw inputs (publisher supply, training data) are bought, not owned; model lead must be re-earned every quarter (Q2 2026 showed a model-timing slip); Unity Vector is growing fast off the same supply; no owned consumer surface; hostage to Apple/Google privacy rules.
- A 6 gives CAP = 9.8 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 9.8 years, 15-year projection.

## DCF — v5 final run (2026-10-13)
Growth recalibration (written reason, unchanged from v4): the engine's blended growth is 50.22% and g_base hit the 35% cap because two blend components are inflection artifacts (OE/share CAGR 2y 138.92% off a tiny base; latest YoY +69.99% on the divestiture-restated base). The revenue signals that mean something — 5-yr CAGR 30.45%, 3-yr CAGR 24.83%, current prints ~53% decelerating toward a +46-48% guide — center on ~30%. Scenario starts were therefore set via offsets (−0.20 / −0.13 / −0.05 / +0.03 / +0.10 vs the capped g_base) to 15 / 22 / **30** / 38 / 45%. Probabilities 10/25/35/20/10; OE multipliers 0.75/0.90/1.00/1.10/1.25. Price $272.28.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | 15.0% | 0.75 | Vector/Meta close the model gap fast; ad cycle turns | $134.03 | 9.15% |
| Bear | 25% | 22.0% | 0.90 | Deceleration to the low-20s sticks; multiple compresses | $218.82 | 12.93% |
| Base | 35% | 30.0% | 1.00 | Current trajectory decays normally over the CAP | $344.10 | 17.47% |
| Bull | 20% | 38.0% | 1.10 | AXON keeps share; e-commerce ads ramp | $532.45 | 22.70% |
| Super bull | 10% | 45.0% | 1.25 | Durable category-killer path | $810.95 | 28.58% |

- **Probability-weighted: IV@15% $376.13 (+38.1% vs price), IV@12% $535.47 (+96.7%), IV@10% $718.13, weighted IRR 18.43%, base-case IRR 17.47%**
- **Tier by numbers: B.** Diagnostics (key_numbers.md): OE yield 4.59%, terminal value 26.2% of IV@15%, scenario spread 6.05x, net debt 0.24x normalized OE, 9.4 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.4 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, quoted above.
- **BASE_DIVERGENCE** (latest FY $10.94 vs median $4.96): the median is the distorted one — it averages in pre-inflection FY23 ($1.91/share). TTM base used; median retained in the reporting and in the impact measurement.
- **OVERRIDE_APPLIED:capex**: see OVERRIDE — gap, decision, and measured impact are all recorded in fields (judgment.json, dcf_numbers.json overrides_applied/override_impact, overrides_registry.json), not just here.
- **BASIS_BREAK_SUSPECT**: the 2023 apps-divestiture restatement. Growth inputs were chosen on continuing-operations signals (3-yr CAGR and current prints), not the mixed-base 5-yr CAGR.
- **OE_VOLATILE** (OE/share spans >3x over 5 years): real — it is an inflection, not cyclicality. Handled by the TTM base plus scenario weights that put 35% on bear-or-worse outcomes.
- **NI_OCF_DIVERGENCE** (2023): divestiture-era tax and working-capital effects; the OCF-based conservative OE is the series used throughout, so the divergence does not contaminate the base.
- **BUYBACK_TAILWIND** (share count −2.73%/yr): already credited via the +2.73pp growth adjustment in the blend; not double-counted in the verdict.
- **WIDE_SCENARIO_SPREAD** (6.05x): real — this stock's outcome range IS wide. Confidence is capped at medium, and the verdict is sized to the conservative end.

## My thoughts / overlay
- The honest headline remains the *range* across defensible methods: the day's v4 runs spanned weighted IV@15% from $178 (single-FY base, harsh cap) to $452 (TTM base, momentum growth) — tiers C to A. The v5 final ($376.13) sits on the two most current, filing-derived inputs, now with the capex gap decided and measured instead of silently zero-filled. Anyone quoting one number for APP without its method is hiding the ball.
- Quality is not the debate: near-zero capex even after a conservative override, SBC $282M TTM and falling as a share of OCF, net debt 0.24x normalized OE, buybacks shrinking the count 2.7%/yr (already credited).
- Risks unchanged: per-install monetization gains must be re-earned against Unity Vector and Meta/Google; ad-cycle exposure; securities-litigation headline risk (SEC inquiry reportedly closed with no action); single-engine concentration; growth already decelerating from +59% → +53% → guided +46-48%.
- Margin of safety on the final numbers: the weighted IV@15% sits 38.1% above the price — equivalently, the price is 27.6% below the weighted IV@15%. That is a margin against the weighted case, not against the bear cases (bear IV@15% $218.82 sits below the $272.28 price). A buyer here is paid for the base case, not insured against the bear case.

## Final verdict
- **Final tier: B** (weighted IRR 18.43% on the v5 final inputs; the method range runs C to A, which is itself the finding)
- Confidence: **Medium** (high on OE quality and the TTM base, medium-low on any single growth path — the scenario spread is 6.05x)
- One-liner: Elite owner's-earnings machine, moat 6/10 — clears 15% on current TTM numbers (18.4% weighted, IV $376 vs $272) but the verdict is assumption-dominated (methods span C to A); size it like a B, not an A.
