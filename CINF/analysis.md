# CINF — Cincinnati Financial Corporation
v5 run, 2026-10-15. Market cap $26.28B at $166.67 (nasdaq_quote_api, dcf_numbers.json) — in scope under $40B.

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.py output, or financials_history.csv — none are recomputed. Earnings-release figures are labelled with their source.

## What it is
Property & casualty insurer founded in 1950, writing business, home and auto cover through local independent agencies across 46 states, plus life/disability and annuities, excess & surplus, reinsurance (Cincinnati Re / Global), finance/leasing and asset management. Earnings have two engines: P&C underwriting and a large investment portfolio — the second dominates reported net income in most years.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $3,112,000,000; capex $20,000,000; SBC $46,000,000 — by filing-sourced override, see OVERRIDE below.
- **Conservative owner's earnings FY2025: $3,046,000,000 = $19.32/share** (dcf_numbers.json: base_oe_total_latest_fy $3,046,000,000, base_oe_latest_per_share $19.315155358275206)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $2,409,000,000 for FY2025 (financials_history.csv) — below the conservative figure, mainly because net income excludes the unrealised equity-portfolio gains that operating cash flow also strips out differently; the OCF-based conservative figure is the cleaner series for an insurer and is used throughout.
- OE positive 5 of the last 5 fiscal years (dcf_numbers.json). Net debt $790,000,000 (dcf_numbers.json) — long-term debt only in this model's terms; for an insurer this is not the real balance-sheet picture (loss reserves and the investment portfolio sit outside the OE/capex frame — see SECTOR_MODEL_MISMATCH below). Book value per share was $102.35 at year-end 2025 and $108.64 at June 30, 2026 (company Q4 2025 and Q2 2026 earnings releases).
- Earnings quality caveat: reported net income swings with the equity portfolio — FY2022 net income was -$487,000,000 on revenue of $6,563,000,000 (financials_history.csv) while operating cash flow was $2,052,000,000 and conservative OE was positive. Revenue and net-income growth rates for this name are therefore not premium growth rates.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $3,112,000,000 − prior YTD $1,051,000,000 + current YTD $1,356,000,000 = **TTM $3,417,000,000**
- Capex: FY $20,000,000 − prior YTD $7,000,000 + current YTD $4,000,000 = **TTM $17,000,000**
- SBC: **TTM $46,000,000**, all three legs filled by the override (see OVERRIDE)
- Shares (current-YTD weighted diluted): **156,300,000**
- **TTM OE total $3,354,000,000 → base OE/share $21.46** (ttm.json: ttm_oe_per_share 21.45873320537428, base_source: ttm_json)
- The engine's normalized base (3-yr median) is $16.36/share (base_oe_normalized_per_share 16.35614702154626) — anchored on FY2024. The TTM base sits above both the median and the latest FY ($19.32/share) because operating cash flow rose through FY2025 and H1 2026. The TTM base is used per the STALE_FY rule, but the gap to the median is the main sensitivity in this run — see Thoughts.

## OVERRIDE — SBC (filing-sourced, bounded authority)
- **The gap:** the preliminary engine run exited 4 with `DATA_GAP:sbc` — SBC missing for fiscal years 2023, 2024, 2025 of the last 3. `ShareBasedCompensation` was last filed for FY2021 ($33,000,000, financials_history.csv); the engine's tags have no annual values after that.
- **The decision (worker, under Andrew's 2026-10-14 bounded authority, kind "filing"):** judgment.json carries `sbc_override = {value: 46000000, kind: "filing", source: "Form 10-K for fiscal year ended December 31, 2025, Note 17 — Share-Based Associate Compensation Plans: share-based compensation cost after tax was $37 million (2025), $37 million (2024) and $32 million (2023), with related income tax benefit of $9 million, $9 million and $8 million respectively — pre-tax cost $46 million (2025), $46 million (2024) and $40 million (2023). The FY2024 10-K Note 17 corroborates the 2023 figure (after tax $32 million + $8 million benefit)."}`. The engine applies a single value to every missing period (periods_filled 2022-2025 in dcf_numbers.json); $46,000,000 is the exact filed FY2024 and FY2025 pre-tax figure, and FY2024 is the median year of the normalized base, so the base year is exact, with at most a $6,000,000 overstatement in FY2023 — the conservative direction. Override check in dcf_numbers.json: last filed value $33,000,000, out_of_band false.
- **Measured impact (from key_numbers.md, on the TTM base actually used):** base OE/share $21.52 (no override) → $21.46 (with override), -0.27%; weighted IRR 18.31% → 18.42% (+0.10pp). Unblocks tier: YES — this override is the only reason this company has a tier; without it the filing gap blocks scoring entirely. (The engine-native override_impact block in dcf_numbers.json is measured on the normalized base and is not the headline figure when a TTM pin is in force.)

## Moat: 5/10 — moderate / narrow
Justification: Disciplined P&C underwriter with a loyal independent-agent network, 14 consecutive years of underwriting profit through FY2025 and a long dividend-growth record — but P&C cover is re-shopped at renewal with low policyholder switching costs, pricing is cyclical, catastrophe losses are a permanent tail, and earnings are dominated by a large equity-investment portfolio rather than a defensible underwriting franchise.
- FOR: Independent-agent distribution network built since 1950, with local-agent relationships competitors cannot replicate quickly
- FOR: Disciplined underwriting: 14 consecutive years of P&C underwriting profit through FY2025, FY2025 combined ratio 94.9% (company FY2025 earnings release)
- FOR: Conservative balance sheet and long dividend-growth record supporting agent and policyholder trust through cycles
- FOR: Diversified P&C, life, excess & surplus and reinsurance lines across 46 states smooths single-line cycles
- FOR: Large investment portfolio and rising investment income (+14% in FY2025, company earnings release) provide a second earnings engine
- AGAINST: P&C policies are re-shopped at renewal — low policyholder switching costs and agents can place business elsewhere
- AGAINST: Pricing power is cyclical: Q2 2026 combined ratio rose to 100.8% and operating income fell 28% YoY as competition intensified (company Q2 2026 earnings release / call reports)
- AGAINST: Catastrophe exposure is structural — Q2 2026 Ohio catastrophe losses were nearly 4x the state's 5-year Q2 average (company Q2 2026 reporting)
- AGAINST: Net income is dominated by equity-portfolio fair-value swings, not underwriting (2022 net loss on revenue of $6,563,000,000 in the filed history)
- AGAINST: Capable national rivals (Travelers, Progressive, Chubb and others) contest the same agency business
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — v5 final run (2026-10-15)
Growth recalibration (written reason): the engine's blended growth is 17.67% and g_base is 17.90% (dcf_numbers.json), but its components are inflection artifacts for an insurer — rev CAGR 3y 24.38% is a rebound off the equity-loss-depressed FY2022 revenue base, rev YoY latest 11.41% and OE/share CAGR 2y 23.92% carry the same distortion. The prints that measure the underlying business are premium growth: FY2025 net written premiums +9% and Q2 2026 consolidated net written premiums +3% with earned premiums +6.3% YoY (company earnings releases), decelerating as management chooses underwriting discipline over growth in a softening cycle. Scenario starts were therefore set via offsets (-0.18 / -0.15 / -0.11 / -0.08 / -0.05 vs g_base) to -0.1 / 2.9 / **6.9** / 9.9 / 12.9%. Probabilities 10/25/30/25/10 (defaults, kept); OE multipliers 0.75/0.90/1.00/1.10/1.25 (defaults). Price $166.67.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -0.1% | 0.75 | Soft pricing cycle plus a heavy catastrophe year; combined ratio stays above 100% | $118.40 | 11.30% |
| Bear | 25% | 2.9% | 0.90 | Premium growth stalls near the Q2 2026 +3% print; underwriting profit thins | $161.02 | 14.58% |
| Base | 30% | 6.9% | 1.00 | High-single-digit premium and investment-income growth decays normally over the CAP | $211.21 | 18.17% |
| Bull | 25% | 9.9% | 1.10 | FY2025 premium momentum (+9%) holds and the combined ratio improves back toward the low-90s | $262.95 | 21.56% |
| Super bull | 10% | 12.9% | 1.25 | Sustained hard market plus strong investment income compounding book value | $337.94 | 26.05% |

- **Probability-weighted: IV@15% $214.99 (+29.0% vs price), IV@12% $286.63, IV@10% $366.64, weighted IRR 18.42%, base-case IRR 18.17%**
- **Tier by numbers: B.** Diagnostics (dcf_numbers.json): OE yield 12.87%, terminal value 19.08% of IV@15%, scenario spread 2.85x, net debt 0.23x normalized OE, 9.46 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (latest fiscal year ended 9 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, quoted above with all four legs' inputs.
- **SECTOR_MODEL_MISMATCH** (Finance sector): real and unresolved by design — an insurer's owner's earnings are not OCF minus capex in any economically complete sense: float, loss reserves and the investment portfolio drive value, and capex ($17,000,000 TTM) is trivial. The DCF is a screening approximation only, confidence is graded low, and the tier is soft. The book-value record ($102.35 at YE2025 to $108.64 at Q2 2026, company releases) is the cross-check a buyer should weight alongside this model.
- **OVERRIDE_APPLIED:sbc**: see OVERRIDE — gap, filing source, and measured impact are all recorded in fields (judgment.json, dcf_numbers.json overrides_applied/override_impact, overrides_registry.json), not just here.
- **Base divergence (not a formal flag in the final run, addressed because it drives the verdict):** TTM base $21.46/share vs normalized median $16.36/share vs latest FY $19.32/share. The median is anchored on FY2024 and lags a genuine OCF uptrend (FY OCF $2,052,000,000 in 2023 → $2,649,000,000 in 2024 → $3,112,000,000 in 2025, financials_history.csv); the TTM figure extends that same trend through H1 2026 rather than inventing a new one. The TTM base is used, and the verdict is sized to the conservative end because of this gap.

## My thoughts / overlay
- The method range is the honest headline alongside the tier: on the TTM base the weighted IRR is 18.42% (Tier B); on the normalized median base of $16.36/share the same cash-flow shape would clear the 15% hurdle only marginally, if at all. Defensible inputs therefore span roughly Tier C to B — the TTM run is the fresher, filing-derived one, but it is not the only defensible one.
- Quality is real: 14 consecutive years of underwriting profit, FY2025 combined ratio 94.9%, FY2025 value creation ratio 18.8% against the company's own 10-13% average target (company FY2025 earnings release), and a long dividend-growth record. The Q2 2026 print is the caution: combined ratio 100.8%, non-GAAP operating income $224,000,000 down from $311,000,000 a year earlier (company Q2 2026 release), with net income of $1,255,000,000 carried by equity-portfolio gains — underwriting is currently not the engine.
- Balance sheet in model terms is light (net debt $790,000,000, 0.23x normalized OE), but that figure excludes insurance reserves by construction; it should not be read as low leverage for an insurer.
- Margin of safety: the weighted IV@15% of $214.99 sits 29.0% above the $166.67 price — equivalently the price is below the weighted IV. That is a margin against the weighted case, not against the bear cases: bear IV@15% is $161.02, just below the current price. A buyer wanting a margin of safety against the bear case needs a price near or below $161.02; the hurdle-clearing price on the weighted case is $214.99.

## Final verdict
- **Final tier: B** (weighted IRR 18.42% on the v5 final inputs; method range roughly C to B across the TTM vs normalized-median bases, which is itself a finding)
- Confidence: **Low** (Finance sector-model mismatch on an insurer, plus a TTM base well above the normalized median — the spread between defensible bases is wide even though the scenario spread, 2.85x, is not flagged wide)
- One-liner: Disciplined P&C insurer with a loyal agency network, moat 5/10 — clears 15% on TTM owner's earnings (18.4% weighted, IV@15% $214.99 vs $166.67) but the Finance sector-model mismatch and a TTM base well above the 3-yr median keep confidence low; a margin of safety against the bear case needs ~$161 or below.
