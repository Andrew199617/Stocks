# FSLR — First Solar, Inc.

Price $178.81 (nasdaq_quote_api, 2026-10-16) · Market cap $19.23B · Diluted shares 107,537,000 · Net debt -$2,304,942,000 (net cash)

## What it is

The largest US solar manufacturer and the only scaled maker of cadmium-telluride (CdTe) thin-film modules. It designs, builds and sells utility-scale modules from a vertically integrated, mostly US footprint, with a supply chain that does not run through Chinese crystalline silicon. Revenue is contracted multi-year: backlog was 45.1 GW / $13.6B through 2030 at 2026-06-30 (company Q2 2026 release, via search), with US production substantially committed through 2028. Q2 2026: net sales $1.06B (-4% YoY), diluted EPS $3.92; Q1 2026: net sales $1.04B (+24% YoY), EPS $3.22. FY2026 guidance was reaffirmed after Q2: net sales $4.9–5.2B (vs FY2025 actual $5,219,376,000 — i.e. guided flat), volume sold 17.0–18.2 GW, capex $0.8–1.0B, adjusted EBITDA $2.6–2.8B, with Section 45X production credits of $2.10–2.19B inside the guide.

## Owner's earnings

Conservative definition (OCF − total capex − SBC) from financials_history.csv:

- FY2023: OCF $602,260,000 − capex $1,386,775,000 − SBC $34,219,000 = OE -$818,734,000
- FY2024: OCF $1,217,999,000 − capex $1,526,076,000 − SBC $28,104,000 = OE -$336,181,000
- FY2025: OCF $2,057,105,000 − capex $869,875,000 − SBC $19,223,000 = OE $1,168,007,000 ($10.86/sh)

The 3-yr median base is -$3.13/sh — the preliminary engine run therefore printed Tier F. That median is distorted, not representative: FY2023–24 capex ($1.39B / $1.53B vs D&A of $307,994,000 / $423,498,000) was a factory construction wave (new US plants), i.e. overwhelmingly growth capex, and it ended — FY2025 capex fell to $869,875,000 against D&A of $529,216,000. The maintenance definition (NI + D&A − min(capex, D&A) − ΔNWC) was positive throughout: $624,986,000 (FY2023), $1,143,300,000 (FY2024), $1,967,673,000 (FY2025). Only 1 of the last 5 years is positive on the conservative definition (engine: oe_positive_years_of_last_5 = 1/5), so the latest year alone would be a flag, not a pass — the resolution is the TTM base below, which uses the same conservative definition on post-build-out data.

**Base used: TTM $13.71/sh** (base_source: ttm_json). ttm.py inputs, quoted from ttm.json — FY leg (2025-01-01→2025-12-31): OCF $2,057,105,000, capex $869,875,000, SBC $19,223,000, diluted shares 107,537,000. Prior YTD (2025-01-01→2025-06-30): OCF -$458,405,000, capex $494,100,000, SBC $9,394,000, shares 107,468,000. Current YTD (2026-01-01→2026-06-30): OCF -$359,767,000, capex $279,849,000, SBC $13,826,000, shares 107,677,000. TTM result: OCF $2,155,743,000, capex $655,624,000, SBC $23,655,000, shares 107,677,000 → TTM OE $1,476,464,000 = $13.7120/sh. Note TTM capex ($655,624,000) still exceeds a pure maintenance level and FY2026 capex is guided back up to $0.8–1.0B, so the TTM base is if anything not flattered by a capex trough — but it does embed today's 45X-supported margins (see AGAINST).

Growth inputs: rev CAGR 5y 14.0%, rev CAGR 3y 25.8%, latest FY revenue YoY +24.1%, engine blend g_base 23.78%. Those are backward-looking: FY2025's +24.1% revenue print and the TTM OE jump ($10.86 → $13.71/sh) were driven by the capex cliff and margin/45X step-up, not by volume growth that repeats. FY2026 sales are guided flat. Scenario starts are therefore recalibrated down via offsets (see DCF section) — a written guided-deceleration / one-off-base reason, per the sanity-check rule.

## Moat: 6/10 — moderate-strong, but substantially policy-conferred

FOR:
- Only scaled CdTe thin-film platform — differentiated technology, vertically integrated, cumulative module sales past 100 GW
- Fully US-integrated supply chain independent of Chinese crystalline silicon — insulation from the tariff regime that raises rivals' costs
- Contracted backlog 45.1 GW / $13.6B through 2030, US capacity substantially sold out through 2028; ~41 GW of backlog carries domestic-content requirements only FSLR can fill at scale
- Pricing power on new US bookings (~$0.36/W recent ASPs vs ~$0.20/W in India, per search results)
- Net-cash balance sheet (-$2,304,942,000 net debt) — survives a policy or demand downturn that would break leveraged rivals

AGAINST:
- The moat is substantially conferred by policy: Section 45X credits of $2.10–2.19B sit inside the FY2026 guide, plus tariff/import-price protection and domestic-content adders — a legislature can shrink all of it, and post-2028 bookings reprice into that uncertainty
- Global module pricing is set by Chinese crystalline-silicon oversupply; CdTe's cost/efficiency edge is real in hot, utility-scale settings but not universal
- Single product family, utility-scale only — no residential/commercial diversification
- Backlog is shrinking at the margin (47.9 GW at Q1 2026 → 45.1 GW at Q2 2026); bookings pace is the swing factor for post-2028 growth
- Tellurium supply constrains ultimate CdTe scale; customer base is a concentrated set of utility developers

Justification: genuine technology, integration and contracted-demand advantages earn a 6, but the largest single pillar (45X + trade protection) is rented from policy rather than owned, which caps it below the 7–8 strong band. CAP = clamp(2 + 1.3 × 6) = 9.8 years.

## DCF — v5 final run (2026-10-16)

Base OE $13.7120/sh (TTM), moat 6, CAP 9.8y, terminal growth 2.5%, probs skewed slightly bearish (15/25/30/20/10) for the binary policy exposure. Growth offsets are recalibrated down from the engine defaults (-0.2578/-0.2078/-0.1578/-0.0978/-0.0378 vs g_base 23.78%) because FY2026 revenue is guided flat and the FY2025/TTM growth prints are capex-cliff and 45X artifacts, not repeatable volume growth; even the super-bull start (20.0%) sits below the FY2025 revenue print (+24.1%) for that stated reason.

| Scenario | Prob | Growth start | OE mult | IV@15% | IRR |
|---|---|---|---|---|---|
| Super bear | 15% | -2.0% | 0.75 | $69.02 | 7.11% |
| Bear | 25% | 3.0% | 0.90 | $103.46 | 9.75% |
| Base | 30% | 8.0% | 1.00 | $143.60 | 12.67% |
| Bull | 20% | 14.0% | 1.10 | $206.14 | 16.66% |
| Super bull | 10% | 20.0% | 1.25 | $305.17 | 21.90% |

**Weighted: IV@15% $151.05, IV@12% $203.54, IV@10% $262.47, weighted IRR 13.21% → Tier C by numbers.** Price $178.81 is 15.53% above the weighted IV@15% (upside_at_15 = -15.53%). Diagnostics: OE yield 7.67%, terminal-value share at 15% 20.2%, scenario spread (super-bull/super-bear IV@15) 4.42×.

Scenario stories: super bear = 45X curtailed/phased down early and tariff protection diluted — OE level cut 25% and no growth; bear = policy survives but bookings stay soft, pricing flat; base = guidance-like flat start compounding into capacity/backlog growth at modest rates; bull = Section 232 import price floor reprices post-2028 bookings up and volume grows mid-teens; super bull = floor pricing + full capacity absorption + CuRe yield gains hold growth at 20%.

## Flags — every fragility flag resolved

- **STALE_FY** (latest FY ended 2025-12-31, 9.5 months ago): resolved with ttm.py — TTM OE $13.7120/sh computed in code from 10-Q YTD legs (quoted in full above) and passed via `--ttm`; the final base is the TTM pin, not the FY median.
- **WIDE_SCENARIO_SPREAD** (super-bull IV 4.42× super-bear IV): real and structural — the value hinges on US policy (45X, tariffs) more than on operations. Confidence is therefore medium (and would be capped there regardless); the verdict is sized to the conservative end of the method range.
- Preliminary-run Tier F / negative normalized base (-$3.13/sh median): resolved above in Owner's earnings — the median straddles the FY2023–24 factory build-out; the TTM base on the identical conservative definition is positive and current. No data gap: data_gap is empty, no overrides declared.

## My thoughts / overlay

Method range: the engine-native growth path (default offsets, base start 23.78%) on the same TTM base printed weighted IRR 21.71% and IV@15% $310.00 — Tier A. I do not stand behind that path: it compounds a capex-cliff year at ~24% for two years against flat FY2026 guidance. The defensible range is therefore C (guidance-calibrated) to A (engine-native), and per the wide-spread rule the verdict sizes to the conservative end: **Tier C**. The honest summary is that FSLR's operations and backlog are strong, its balance sheet is net cash, and at $178.81 the market is already paying for a good part of the policy-protected future — the weighted IRR of 13.21% does not clear Andrew's 15% hurdle. It clears 15% at the weighted IV@15% of $151.05; a buyer wanting a margin of safety on top of the hurdle needs a price well under that level. The single biggest swing factor is not execution — it is whether 45X and the import price floor survive in current form past 2028.

## Final verdict

Tier C (weighted IRR 13.21%, IV@15% $151.05 vs price $178.81), moat 6/10, confidence medium. A high-quality, policy-levered manufacturer priced above what guidance-calibrated owner's earnings support at a 15% hurdle; revisit below ~$151, or if bookings re-accelerate enough to lift the base-case growth start.
