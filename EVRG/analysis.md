# EVRG — Evergy, Inc.
v5 run, 2026-10-16. In scope (market cap $19.055B at $81.57, nasdaq_quote_api — under the $40B cutoff).

All figures below are copied from dcf_numbers.json, financials_history.csv, or ttm.py output — none are recomputed.

## What it is
Regulated electric utility serving ~1.7 million customers in Kansas and Missouri (Kansas City metro), formed from the Westar/KCP&L merger. Fully regulated: earnings are essentially allowed ROE × rate base. The current story is a step-change in load: ~3.0 GW of signed large-load Electric Service Agreements (data centers — Google, Meta, others — plus Panasonic's EV battery plant) under new Large Load Power Service (LLPS) tariffs in both states, with 16–17-year minimum billing commitments, supporting guided retail load growth of ~7–8% CAGR through 2030 and a $21.6B 2026–2030 capital plan (plus ~$1B incremental generation), lifting expected rate-base CAGR to ~12%. Q2 2026 adjusted EPS was $0.88 (vs $0.82 a year ago); management reaffirmed 2026 adjusted EPS guidance of $4.14–$4.34 and a long-term adjusted EPS growth target of 6–8%+ through 2030 (>8% from 2028). (Research: Q2 2026 earnings reporting/coverage, Oct 2026.)

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** revenue $5,705,100,000; net income $855,600,000; operating cash flow $2,045,200,000; capex $2,796,900,000 (tag PaymentsToAcquirePropertyPlantAndEquipment); SBC $20,700,000 (immaterial — utilities barely use equity comp); D&A $1,162,900,000.
- **Conservative owner's earnings FY2025: −$772,400,000 = −$3.31/share** (base_oe_latest_per_share −$3.3065). Capex runs well ahead of OCF because most of it is growth/rate-base investment (new generation, grid, data-center interconnection), not maintenance.
- **Normalized base (median of last 3 FY OE/share): −$1.6117/share** — negative. Conservative OE was positive in **0 of the last 5 fiscal years**.
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): **+$1,195,100,000 in FY2025**, and positive in every recent year shown in financials_history.csv. The two definitions diverge completely here, and the divergence IS the finding: on a D&A-capped maintenance view Evergy earns money; on the sweep's conservative total-capex view it cannot, because the company is deliberately spending ~$3B/yr building rate base that earns a regulated return only after it enters rates.
- **Base used = the engine's normalized median (−$1.6117/share).** No TTM pin was applied: the TTM figure is even more negative (below), so no defensible base choice changes the verdict.
- Net debt $13,386,400,000 (dcf_numbers.json) against equity of $10,221,300,000 (FY2025, financials_history.csv) — normal leverage for a regulated utility funding a rate-base build, serviced from regulated cash flows, but it means equity holders sit behind a large, growing debt stack while the capex plan is financed with a mix of debt and ATM equity issuance (~$425M priced under forward sales YTD per Q2 coverage).
- Share count is drifting up, not down: share CAGR +0.48%/yr (growth blend adjustment −0.48pp), and the financing plan implies continued mild dilution.

**TTM check (ttm.py, filing-direct, through Q1 2026) — quoted inputs:**
- OCF: FY $2,045,200,000 − prior YTD $449,600,000 + current YTD $362,500,000 = **TTM $1,958,100,000**
- Capex: FY $2,796,900,000 − prior YTD $592,800,000 + current YTD $851,900,000 = **TTM $3,056,000,000**
- SBC: FY $20,700,000 − prior YTD $4,500,000 + current YTD $5,600,000 = **TTM $21,800,000**
- Shares (current-YTD weighted diluted): **235,600,000**
- **TTM OE total −$1,119,700,000 → TTM OE/share −$4.75** — worse than FY2025, because capex accelerated into 2026 while OCF softened. There is no TTM rescue for this name.

## Moat: 5/10 — moderate; a real franchise, capped economics
Justification: Evergy holds exclusive regulated service territories in Kansas and Missouri — customers are captive and the service is essential, which is as durable as franchises get. But the moat's economics are capped by construction: pricing and returns are set by the Kansas Corporation Commission and the Missouri PSC in rate cases, not by the company, so the franchise converts into allowed-ROE earnings, not pricing power. Score sits mid-scale: structurally protected demand, regulator-capped returns.
- FOR: Exclusive regulated service territory — no competitor can serve its Kansas/Missouri customers
- FOR: Essential service with captive demand; weather-normalized load now inflecting up on signed large-load contracts
- FOR: ~3.0 GW of signed ESAs with 16–17-year minimum billing commitments under LLPS tariffs that make large customers pay premium rates and their share of system costs
- FOR: Rate-base growth is close to self-funding earnings growth once assets enter rates (~12% guided rate-base CAGR)
- AGAINST: No pricing power — allowed ROE and cost recovery are decided by KS/MO regulators, and Kansas rate outcomes have historically been the less constructive side
- AGAINST: Returns are capped by design: even perfect execution earns the allowed ROE, not a wide-moat compounder's return on capital
- AGAINST: The $21.6B+ capex plan needs continuous external capital — debt plus ATM equity — so per-share economics leak to financing costs and mild dilution
- AGAINST: Weather exposure (mild 2025 weather was a stated full-year headwind), storm costs, and coal-fleet/environmental transition spend
- AGAINST: Customer/project concentration — a handful of data-center and industrial projects carry the load-growth thesis; delays or tougher rate treatment hit the plan directly
- A 5 gives CAP = 8.5 years (growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection) — moot here, because the base the fade would apply to is negative.

## DCF — v5 final run (2026-10-16)
The engine emits **no scenario table, no IV, and no IRR for EVRG**: the normalized base OE is negative, so every scenario (any growth offset, any OE multiplier ≤1.25 applied to a negative base) stays negative. Defaults were run anyway (moat 5, probabilities 10/25/30/25/10, offsets −12/−5/0/+5/+12pp, multipliers 0.75/0.90/1.00/1.10/1.25) and the output is unchanged from the preliminary pass.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | n/a | 0.75 | Rate cases turn hostile; data-center projects slip | n/a — negative base | n/a |
| Bear | 25% | n/a | 0.90 | Capex continues to outrun OCF; allowed ROE compresses | n/a — negative base | n/a |
| Base | 30% | n/a | 1.00 | Normalized base OE −$1.6117/share | n/a — negative base | n/a |
| Bull | 25% | n/a | 1.10 | Load growth lands; still no positive conservative OE at current capex pace | n/a — negative base | n/a |
| Super bull | 10% | n/a | 1.25 | Even 1.25× a negative base is negative | n/a — negative base | n/a |

- **Probability-weighted IV/IRR: not computable. Tier by numbers: F** ("No positive NORMALIZED (3-yr median) conservative owner's earnings — OE DCF not supportable on numbers alone").
- Diagnostics from dcf_numbers.json: blended growth g_blend 0.69% (rev CAGR 5y 3.60%, rev CAGR 3y 0.69%, latest revenue YoY +0.01%, OE/share CAGR not computable on a negative series); net debt $13,386,400,000; FY ended 9 months before this run.
- **Sanity check against recent prints:** the company's actual growth story — guided adjusted EPS growth of 6–8%+ and Q2 2026 adjusted EPS +7.3% YoY — is a *net-income* story, driven by rate-base growth. It does not contradict the F: adjusted EPS rises precisely because capex is being converted into rate base, while conservative OE (OCF − total capex − SBC) falls further negative as the build accelerates (TTM OE/share −$4.75 vs FY2025 −$3.31). No scenario growth start can fix a negative base, so the usual "start below the latest print" failure mode does not arise.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9 months ago): resolved by running ttm.py — TTM through Q1 2026 is −$4.75/share (inputs quoted above), worse than FY2025. No TTM base pin was used; the median base stands and the verdict is identical on either base.
- **NI_OCF_DIVERGENCE** (NI vs OCF differ by >40% in 2023, 2025): structural, not a one-off. OCF 2023 $1,980,200,000 vs net income $731,300,000; OCF 2025 $2,045,200,000 vs net income $855,600,000 (financials_history.csv). The gap is dominated by non-cash D&A — $1,076,500,000 in 2023 and $1,162,900,000 in 2025 — the standard signature of a capital-heavy utility, not tax deposits or impairments. The conservative OE uses OCF directly, so the divergence does not flatter the base; if anything the OE problem sits on the capex line, not the OCF line.
- **SECTOR_MODEL_MISMATCH: Utilities**: accepted in full. The OE/total-capex lens fits utilities poorly — it charges growth/rate-base capex (which earns a regulated return for decades) entirely against current-period earnings. Confidence is graded **low** and the tier is read softly: F means "this screen cannot support a hurdle for this name," not "this business earns nothing" — the maintenance-definition OE (+$1,195,100,000 FY2025) and the $4.14–$4.34 adjusted EPS guide both say the regulated earnings are real. The tier is NOT overridden upward, because within the sweep's stated conservative definition the numbers genuinely are what they are, and the ranking's comparability depends on applying the same definition to every name.

## My thoughts / overlay
- Method range: under the sweep's conservative definition EVRG is an unambiguous F in every year and on the TTM — there is no defensible input set inside this model that produces a tier, so the *range* is not C-to-A like APP; it is "F on this screen, unrateable-to-fine on a utility lens (allowed ROE × rate-base growth, dividend yield, FFO/debt)." Anyone quoting EVRG's sweep tier without the sector caveat is hiding the ball in the opposite direction.
- On utility terms the equity case is coherent: ~12% rate-base CAGR, 6–8%+ guided EPS growth, LLPS tariffs shifting system costs onto the data centers causing them, FFO/debt guided at 14–15%. The risks are equally utility-typical: rate-case outcomes (allowed ROE is THE valuation variable), execution/financing of a $21.6B+ plan, weather, and the concentration of the growth story in a few large-load projects.
- Balance sheet folded in: net debt $13,386,400,000 is large in absolute terms but is the regulated model working as designed — debt funds rate base that regulators let the company earn on. It caps equity upside to roughly the allowed ROE minus financing drag; it is not, by itself, a distress signal.
- Hurdle-clearing price: **none is computable** — with a negative OE base there is no price at which this DCF clears 15% (or any positive hurdle), and no margin-of-safety price can be quoted from this model. That is a statement about the model's fit for utilities, recorded plainly, not a claim the stock is worthless.

## Final verdict
- **Final tier: F** (tier by numbers F; no override — no positive normalized conservative owner's earnings, 0/5 years, TTM worse at −$4.75/share)
- Confidence: **Low** (SECTOR_MODEL_MISMATCH rule for utilities; the F is a model-fit result as much as a company result)
- One-liner: Regulated KS/MO franchise, moat 5/10, with real regulated earnings growth (6–8%+ guided EPS, ~12% rate-base CAGR on signed data-center load) that the conservative OE screen structurally cannot credit — capex for rate base runs ~$3B/yr against ~$2B OCF, so OE is negative 0/5 years and no 15%-clearing price is computable; Tier F on the numbers, read with the utility-model caveat.
