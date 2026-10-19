# AMH — American Homes 4 Rent

Price $31.28 · Tier **C** · weighted IRR 10.36% · weighted IV@15% $19.52 · moat 4/10 · confidence **low** (SECTOR_MODEL_MISMATCH)

## What it is

A leading large-scale integrated owner, operator and developer of single-family rental homes — an internally managed Maryland REIT (SIC 6798, NYSE: AMH), FY ends Dec 31. Market cap (est) $11.602B — in scope under $40B. Its differentiator inside SFR is the AMH Development Program: it builds its own rental communities instead of only buying existing homes (more than 15,000 homes delivered since inception, per the CEO in the Q2 2026 release). Q2 2026 (reported Jul 30, 2026): Core FFO $0.49/share, +5.2% YoY; revenue $470.1 million, +2.8%; Same-Home Core NOI +2.7% in the quarter; Same-Home occupancy 96.0% (96.1% preliminary in July); blended lease spreads +2.7% (renewals +3.2%, new leases +1.4%); full-year 2026 Core FFO guidance raised by $0.03 to a $1.95 midpoint (+4.3% YoY), with Same-Home Core NOI growth guided at 1.40%–3.40% (search results — Q2 2026 release and call coverage).

## Owner's earnings

- Conservative definition (OCF − capex − SBC), capex = the filing override below: FY2023 $673,182,000 = $1.86/share; FY2024 $740,414,000 = $2.01/share; FY2025 $798,375,000 = $2.15/share (financials_history.csv). OE positive 5 of the last 5 fiscal years.
- Maintenance definition (NI + D&A − min(capex, D&A) − ΔNWC): FY2025 $977,596,000 (financials_history.csv) — above the conservative figure, as usual for a REIT whose D&A ($504,341,000 in FY2025) dwarfs its recurring capex line; the conservative OCF-based figure is the base series used throughout.
- **Base used = TTM OE/share $2.20** (base_source: ttm_json). ttm.json legs: OCF FY $864,327,000 − prior YTD $495,261,000 + current YTD $495,689,000 = **TTM $864,755,000**; capex **TTM $40,137,000** (override — the FY leg is the full override value and both YTD legs are the same prorated override amount, so they cancel and the TTM capex leg is a full year at the filed run rate); SBC FY $25,815,000 − prior YTD $14,134,000 + current YTD $13,405,000 = **TTM $25,086,000**; shares (current-YTD weighted diluted) **362,643,354**; **TTM OE total $799,532,000 → $2.2047/share** (ttm.json).
- Why TTM over the normalized median ($2.01/share): the FY ended 9.6 months ago. TTM OCF is essentially flat vs FY2025 ($864,755,000 vs $864,327,000), so the TTM base is not a spike — its per-share lift over the latest FY ($2.15) is the 2026 buyback in the share count (current-YTD diluted 362,643,354 vs FY2025 370,906,582; 4.1M shares repurchased in Q2 2026 alone, search results), and every current print supports the run rate (Core FFO +5.2% YoY in Q2, FY2026 guidance raised). The median variant was computed with identical scenarios for the method range (below) and lands in Tier D — the base choice moves the tier by one notch, not the verdict.

## OVERRIDE — capex (filing)

- **The gap:** the preliminary engine run exited 4 with `DATA_GAP:capex` — capex missing for FY2023, FY2024 and FY2025 of the last 3 under every candidate tag the engine reads, because AMH reports its recurring real-estate capex on the cash-flow line "Payments for capital improvements", tagged us-gaap `PaymentsForCapitalImprovements`, which is not in the engine's candidate tag list (the same dead end documented for MAA, ELS, CR, IT, RBC and SNA in `_system/CAPEX_TAG_CAPITAL_IMPROVEMENTS_SPEC_DRAFT.md`).
- **The decision (bounded authority, kind "filing"):** judgment.json carries `capex_override = {value: 40137000, kind: "filing"}` — the median of the three filed years ($40,137,000 FY2023 / $34,052,000 FY2024 / $40,645,000 FY2025), from the FY2025 10-K Consolidated Statements of Cash Flows (filed 2026-02-20, accession 0001562401-26-000010). The engine applies the single value to every missing period (2022–2025 in the history; only 2023–2025 are in the base window). Against the true per-year figures it overstates FY2024 capex by $6,085,000 (conservative direction) and understates FY2025 capex by $508,000 (negligible). The override is **in band**: 1.79x the last filed value under an engine-read tag ($22,367,000, FY2021) — no ack_reason required (dcf_numbers.json override_checks).
- **Excluded, deliberately:** acquisition and development spend on rental homes (e.g. 542 wholly owned development deliveries in Q2 2026 for ~$220 million, search results) is growth investment presented separately by the filer; charging it as capex would double-count growth the home count already paid for.
- **Measured impact** (key_numbers.md, on the TTM base actually used): base OE/share $2.23 without the override → $2.20 with it (-1.18%); weighted IRR 10.45% → 10.36% (-0.09pp). Unblocks tier: YES — without it the filing gap blocks scoring entirely. The no-override TTM figure is itself built on stale 2021/2022 capex legs in ttm.py, so the small measured impact understates the correction; the point of the override is that the capex charged is the filer's own filed recurring line.

## Moat: 4/10 — weak

Evidence first: fundamentals.json cannot compute the `roic_proxy` series or gross margin for AMH in any year (the filed REIT presentation does not split out an operating-income / gross-profit line the tool reads — both are null for 2016–2025), and filed ROE has run only 3.5% (2021), 4.8% (2022), 6.2% (2023), 6.5% (2024), 7.3% (2025) (fundamentals.json annual rows). There is no evidence of sustained returns well above the cost of capital, so a 7+ moat is not available; what exists is scale, density and a development channel. This is the same 4/10 given to direct peer Invitation Homes in this sweep.

FOR:
- Scale and local density as an integrated owner-operator: professionally managed SFR platform with in-house leasing, renovation and property management lowering per-home turn and maintenance costs vs fragmented landlords.
- AMH Development Program — a genuine differentiator vs peers who must buy existing homes: more than 15,000 homes delivered since inception, 651 delivered in Q2 2026 (542 to the wholly owned portfolio), at initial yields management and outside coverage put above acquisition cap rates.
- Structural demand tailwind: high cost of homeownership keeps rent-vs-own economics favorable — Same-Home occupancy 96.0% in Q2 2026 with blended lease spreads +2.7% (renewals +3.2%, new leases +1.4%).
- Expense discipline and balance-sheet access: controllable expense growth held below 1% YTD through Q2 2026, net debt/Adjusted EBITDA ~5.2x including preferreds, and buyback capacity used in Q2 2026 (4.1M shares repurchased at $29.88 average).

AGAINST:
- No network effects or tenant switching costs — leases are typically 12 months, rent is set by the local market, and a tenant can move to a competing home or apartment at renewal.
- Single-family rental supply is overwhelmingly fragmented mom-and-pop stock; AMH's scale is operating efficiency, not a barrier — Invitation Homes and other institutional landlords replicate the model with capital.
- Returns are capped by replacement cost and cap-rate arbitrage — new build-for-rent supply is the permanent competitor, including AMH's own development channel.
- Filed returns are thin: ROE ran 3.5% in 2021 to 7.3% in 2025 (fundamentals.json) and roic_proxy / gross margin are not computable from the filed presentation — no evidence of sustained returns well above the cost of capital.
- Political and regulatory scrutiny of institutional single-family landlords is a live, recurring risk (partly eased by the 21st Century ROAD to Housing Act, per Q2 2026 coverage).

CAP = 7.2 years (moat 4): growth holds 2 years, then converges to the 2.5% terminal rate over 7.2 years.

## DCF — v5 final run (2026-10-18)

Engine 5.4.0, TTM base $2.20/share, price $31.28. Growth blend 5.48% (components: rev CAGR 5y 7.71% · rev CAGR 3y 7.19% · latest rev YoY 3.45% · OE/share CAGR 2y 7.65%; share count CAGR 1.97%, growth adj -1.97%).

**Growth sanity check (written, per the standing rule):** the default offsets would have produced starts of -6.5% / +0.5% / +5.5% / +10.5% / +17.5% — a +17.5% super-bull start (and +10.5% bull) is not a credible forward print for a single-family landlord whose latest revenue YoY is +3.45%, Q2 2026 revenue grew +2.8% and Same-Home Core NOI is guided at 1.40%–3.40% for 2026; the blend's 7–8% revenue CAGRs are the portfolio-growth years, not a per-share run rate a bull case can compound from. Offsets were recalibrated to starts of **-2.0 / +1.5 / +4.0 / +6.5 / +9.5%**. Against the actual prints: the bear start (+1.5%) sits at the low end of the guided NOI range — a stagnation case, not a collapse; the base start (+4.0%) sits just under the FY2026 Core FFO growth guide (+4.3% to a $1.95 midpoint) and well under the OE/share CAGR 2y of 7.65%, with the written reason that development deliveries and buybacks add per-share growth on top of same-home NOI; the bull start (+6.5%) requires the development channel and rent growth to run at the 5-year revenue CAGR pace; the super-bull start (+9.5%) is a 10% tail requiring a 2021–22-style rent spike — stated as a tail, not a forecast. The super-bear start (-2.0%) is a rent/occupancy downturn case AMH has not filed in the last five years (OE positive 5/5, OE/share up every year) — kept at 10% probability for exactly that reason. Probabilities 10/25/30/25/10; OE multipliers 0.75/0.90/1.00/1.10/1.25 (defaults, unadjusted — the scenario spread is carried by the growth starts).

| Scenario | Prob | Growth start | OE mult | IV@15 | IV@12 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -2.0% | 0.75 | $11.38 | $14.82 | 6.91% |
| Bear | 25% | 1.5% | 0.9 | $15.64 | $20.53 | 8.72% |
| Base | 30% | 4.0% | 1.0 | $19.13 | $25.25 | 10.19% |
| Bull | 25% | 6.5% | 1.1 | $23.15 | $30.72 | 11.84% |
| Super bull | 10% | 9.5% | 1.25 | $29.48 | $39.35 | 14.32% |

**Weighted result: IRR 10.36%, IV@15% $19.52** (IV@12% $25.81, IV@10% $32.80; upside at 15% -37.6%). IRR band: bear 8.72% (tier D) → bull 11.84% (tier C); scenario range 6.91% – 14.32%. Diagnostics: OE yield 7.05%, TV share @15% 18.2%, scenario spread (IV@15 super-bull / super-bear) 2.59x. Hurdle-clearing prices (weighted path): 15% at $19.52 · 20% at $13.86 · 25% at $10.72.

Method range: the normalized-median base ($2.01/share) with identical scenarios gives weighted IRR 9.68% and IV@15% $17.82 — Tier D. The two defensible bases span D–C; even the super-bull scenario (IRR 14.32%, IV@15% $29.48) does not reach the 15% hurdle at $31.28, so the verdict does not depend on the base choice: at this price AMH does not clear 15% on any scenario this run computed.

## Flags — every fragility flag resolved

- **DATA_GAP:capex** (preliminary run): resolved by the filing override in the OVERRIDE section above — gap, source, per-year accuracy and measured impact are all recorded in fields (judgment.json, dcf_numbers.json overrides_applied / override_impact, key_numbers.md). data_gap_uncovered is empty in the final run.
- **STALE_FY** (latest fiscal year ended 10 months ago; 9.6 months at scoring): ttm.py was run and its legs are quoted in the Owner's earnings section — TTM OE $799,532,000 → $2.2047/share — and the TTM figure **is** the base (the --ttm pin was used), because it is the current run rate: TTM OCF flat vs FY2025, Q2 2026 Core FFO +5.2% YoY, FY2026 guidance raised.
- **SECTOR_MODEL_MISMATCH** (Real Estate): accepted in full — the OE/capex DCF fits REITs poorly in both directions: it charges all capital-improvements capex against OE, and it gives no credit for the underlying property asset value or for FFO/AFFO, the industry's own metrics (FY2026 Core FFO guided at $1.95/share; DPS TTM $1.26 per fundamentals.json). Confidence is graded **low** and the tier is read as "fails the standardized conservative OE screen at this price," not as "the rental business loses cash." The mismatch does not rescue the hurdle math: even the super-bull scenario (14.32%) stays below 15% at $31.28.
- **OVERRIDE_APPLIED:capex**: see OVERRIDE — filing gap filled for 2022–2025, never replacing a filed value (there were none under engine-read tags for those years); measured impact recorded in key_numbers.md (base $2.23 → $2.20 on the TTM base; weighted IRR 10.45% → 10.36%); unblocks tier: YES.
- **HIGH_NET_DEBT** (net debt 6.1x normalized OE): from the filing, net debt at the latest FY is $4.987B — total debt $5,095,735,000 (LongTermDebt, including current maturities) against cash $108,516,000 (financials_history.csv; key_numbers.md net debt $4.987B, net debt / normalized OE 6.10x). The 6.1x is against the OE denominator this model uses (after capex and SBC); on management's own metric the leverage is ~5.2x net debt including preferreds to Adjusted EBITDA at Q2 2026 (search results) — a moderately levered, laddered REIT balance sheet, not a distress case. The stress the flag asks for is in the scenarios: the bear case (IRR 8.72%, IV@15% $15.64) and super bear (6.91%, $11.38) are where levered OE compresses, and the verdict is sized to that end.
- **TIER_BAND** (bear-case tier D at 8.72% vs bull-case tier C at 11.84%): accepted — the headline C sits on the TTM base; the bear case and the median-base variant are both D. Any position is sized to the bear end (D), per the flag.

## My thoughts / overlay

- The honest headline is the two-lens gap every REIT in this sweep shows. On the REIT lens this is a healthy operator: 96% occupancy, renewal spreads +3.2%, controllable expense growth under 1%, a raised Core FFO guide, dispositions match-funding development (~$380M of net proceeds in H1 2026 from >1,300 homes sold, search results), and an active buyback below the current price ($29.88 average in Q2). On the owner's-earnings lens the same company converts $864,755,000 of TTM OCF into $2.20/share of OE because keeping a scattered portfolio of aging single-family homes leasable costs ~$40M a year of capital improvements, forever — and because the OE lens gives no credit for the homes themselves appreciating.
- What the price is actually underwriting: at $31.28 the buyer pays for the development machine and the housing-shortage tailwind to compound per-share FFO at mid-single digits for a long time. That can be a fine REIT return; it is not a 15% owner's-earnings return on any scenario here — the super bull tops out at 14.32%.
- What would change the tier: the price, mostly — the 15% hurdle clears below ~$19.52 on the TTM base ($17.82 on the median base). On fundamentals, Same-Home NOI would have to inflect well above the guided 1.40%–3.40% range while capital improvements stayed flat. Next checkpoint: Q3 2026 results (expected late October 2026, per search results).
- Confidence: **Low** (SECTOR_MODEL_MISMATCH for a REIT and a capex series the engine cannot read natively — though every computed variant and scenario stays below the 15% hurdle, so the "does not clear" verdict is robust to the data problems; only the C-vs-D notch is base-sensitive).

## Final verdict

**Tier C** (sized to the bear end: the bear case and the median-base variant are Tier D). Quality single-family rental REIT, moat 4/10 — scale, local density and the in-house AMH Development Program are real but rent is a market price on 12-month leases and filed ROE is only 7.3%; on a TTM owner's-earnings base of $2.20/share after charging filed capital-improvements capex, weighted IRR is 10.4% (IV@15% $19.52) at $31.28, so it clears the 15% hurdle only below ~$19.52 — the REIT lens (FY2026 Core FFO guided at $1.95/share, DPS TTM $1.26) is kinder than the OE lens, but neither supports 15% at this price.
