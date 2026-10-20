# MTCH — Match Group, Inc.
v5 run (engine release 5.5.0), 2026-10-20. In scope: market cap $11,865,182,375 at $45.205 (nasdaq_quote_api) — under the $40B limit.

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.json, financials_history.csv or fundamentals.json — none are recomputed.

## What it is
The largest online-dating portfolio company: Tinder (the volume engine, in a management-led turnaround under CEO Bernard "Spencer" Rascoff since early 2025), Hinge (the growth asset — "designed to be deleted," aimed at intentioned daters), Evergreen & Emerging brands (OkCupid, Plenty of Fish, niche apps) and MG Asia (Hyperconnect's Azar). Asset-light subscription / à-la-carte model: capex is ~$57–66M a year against ~$1.1–1.2B of operating cash flow. Q2 2026 prints (company results, via press coverage): total revenue $853.1M, −1.2% YoY; total payers 13.3M, −6% YoY; revenue per payer +6% to $21.13; Hinge direct revenue +22% to ~$203.5M with payers +17%; Tinder direct revenue −1% with payers −5%. Q3 2026 guidance: revenue $885–895M (−2% to −3% YoY), adjusted EBITDA $330–335M.

## Owner's earnings
Two definitions, from financials_history.csv:
- **Conservative (OCF − capex − SBC):** FY2023 $597,280,000 ($2.0365/sh), FY2024 $614,760,000 ($2.2029/sh), FY2025 $765,413,000 ($2.9161/sh). OE positive 5 of the last 5 fiscal years — but see OE_VOLATILE below for the FY2022 trough ($272,683,000, $0.9237/sh).
- **Maintenance (NI + D&A − min(capex, D&A) − ΔNWC):** FY2025 $1,113,205,000 — above the conservative figure; the conservative series is the one used throughout, so SBC ($258,202,000 in FY2025) is always charged in full.
- FY2025 detail: revenue $3,487,197,000 (+0.2% YoY), OCF $1,080,380,000, capex $56,765,000 (PaymentsToAcquirePropertyPlantAndEquipment, rollup), SBC $258,202,000. Cash $1,027,838,000; total debt $3,972,953,000; **net debt $2,945,115,000**. Fundamentals.json TTM shareholder returns: buybacks $614,534,000 and dividends paid $182,216,000 in the TTM to Q2 2026 (DPS TTM $0.78).

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $1,080,380,000 − prior YTD $436,959,000 + current YTD $564,199,000 = **TTM $1,207,620,000**
- Capex: FY $56,765,000 − prior YTD $28,297,000 + current YTD $37,698,000 = **TTM $66,166,000**
- SBC: FY $258,202,000 − prior YTD $137,861,000 + current YTD $120,588,000 = **TTM $240,929,000**
- Shares (current-YTD weighted diluted): **249,620,000**
- **TTM OE total $900,525,000 → base OE/share $3.6076** (base_source: ttm_json; no ttm warnings, no overrides used)
- The engine's normalized base (median of the last 3 FY) is $2.2029/share and the latest FY alone is $2.9161/share — both are reported, and the median-base variant is the conservative end of the method range below. The TTM step-up is not a single-quarter artifact: OCF has risen three straight years ($896,791,000 → $932,719,000 → $1,080,380,000) on cost rationalization (fundamentals.json TTM operating margin 28.2% vs 25.0% in FY2025) while SBC fell and buybacks shrank the denominator.

## Moat: 6/10 — moderate, scale-based, eroding at the core brand
- FOR: Tinder's scale — the largest dating-app user pool gives local matching liquidity rivals cannot replicate quickly; portfolio breadth (Hinge direct revenue +22% and payers +17% in Q2 2026, Evergreen & Emerging niche brands, MG Asia) diversifies a single-app decline; demonstrated pricing power — revenue per payer +6% YoY in Q2 2026 even as payers fell 6%; high returns on capital — the fundamentals.json ROIC proxy (after-tax operating income over equity + debt − cash) ran 23.1% / 17.0% / 26.0% / 22.9% / 26.7% across FY2021–25, with gross margins of 71.9% / 69.9% / 71.6% / 71.5% / 72.8% (note the equity book is negative from years of buybacks, so the proxy's denominator is mostly net debt — the margin evidence is the cleaner half of the claim); trust & safety and brand scale globally.
- AGAINST: Tinder erosion — payers −5% and MAU declining in Q2 2026, total payers −6% YoY to 13.3M; near-zero switching costs and routine multi-homing — network effects are local and can unravel market by market; Gen Z fatigue with swipe dating and substitution toward social apps, events and offline meeting; focused rivals (Bumble — itself taken private in October 2026 at a distressed multiple, Grindr, niche and AI-companion apps) competing for intentioned daters; app-store fee and regulatory pressure on the in-app purchase model.
- A 6 gives CAP = 9.8 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 9.8 years, 15-year projection.

## DCF — final run (2026-10-20)
**Growth sanity check / recalibration (written reason):** the engine's blended g_base is 9.27%, but its components do not describe the current business — the 5-yr revenue CAGR (7.84%) reaches back to the post-separation growth era, and the OE/share CAGR component (19.65%) is measured off the FY2022 settlement trough (see OE_VOLATILE). The prints that matter now: FY2025 revenue +0.2%, TTM revenue $3,509,320,000 at +1.7% YoY (fundamentals.json), Q2 2026 revenue −1.2% YoY, Q3 2026 guided −2% to −3%. Per-share OE can still grow faster than revenue — the share count is shrinking 3.8%/yr on buybacks and operating margin is expanding — so scenario starts were set via offsets (−0.1527 / −0.0927 / −0.0527 / −0.0027 / +0.0473 vs g_base) to −6 / 0 / **+4** / +9 / +14%: the base case is roughly "flat total OE plus the buyback shrink," the bull case needs Hinge's growth to keep offsetting Tinder plus RPP gains, and super bull needs an actual Tinder reacceleration — deliberately below the company's own recent OE/share growth prints, because those prints are margin-recovery and trough effects, not a run rate. Probabilities are bear-tilted at 15/30/30/17/8 (defaults 10/25/30/25/10) for the payer declines, the leverage and the OE_VOLATILE flag. OE multipliers are the defaults 0.75/0.90/1.00/1.10/1.25. Price $45.205.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | −6.0% | 0.75 | Payer spiral: Tinder MAU losses compound, RPP gains stall, margin reset reverses | $15.21 | 6.29% |
| Bear | 30% | 0.0% | 0.90 | Revenue drifts down low-single digits; buybacks + cost control only just hold OE/share flat | $23.82 | 8.97% |
| Base | 30% | +4.0% | 1.00 | Flat-to-slightly-down revenue, Hinge offsets Tinder, buyback shrink carries per-share growth | $31.63 | 11.30% |
| Bull | 17% | +9.0% | 1.10 | Tinder stabilizes on the product reset, Hinge keeps compounding ~20%, RPP keeps rising | $43.46 | 14.55% |
| Super bull | 8% | +14.0% | 1.25 | Tinder reaccelerates, alternative-payment savings drop through, buybacks accelerate | $61.65 | 18.90% |

- **Probability-weighted: IV@15% $31.24 (−30.9% vs the $45.205 price), IV@20% $22.08, IV@25% $17.03, weighted IRR 11.23%, base-case IRR 11.30%**
- **Tier by numbers: C.** Diagnostics (dcf_numbers.json): OE yield 7.98%, terminal value 18.6% of IV@15%, scenario spread 4.05x, net debt 3.11x normalized OE (on the TTM base), 9.6 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (latest FY ended 10 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, quoted above with all four legs; ttm.json carries no warnings and used no overrides.
- **BUYBACK_TAILWIND** (share count shrinking 3.8%/yr): already credited via the growth adjustment in the engine blend and explicitly in the scenario construction (the +4% base start is mostly the buyback shrink); not double-counted in the verdict.
- **OE_VOLATILE** (OE/share range over the last 5 yrs spans >3x): the span is FY2022's $0.9237/sh against FY2025's $2.9161/sh, and the trough is identified, not generic cyclicality: Match agreed in December 2021 to pay $441M to settle the former Tinder employee (Rad et al.) litigation and paid it in June 2022 — statements.json shows the payables/accruals line swinging +$459M in FY2021 (accrual) and −$473M in FY2022 (payment), which is what crushed FY2022 OCF to $525,688,000. A one-off legal payment, not an operating cycle. Handled by the TTM base (outside the window), bear-tilted probabilities (45% on bear-or-worse) and the recalibrated growth starts.
- **NI_OCF_DIVERGENCE** (net income vs OCF differ by >40% in 2024 and 2025): the gap is non-cash addbacks, principally the SBC the conservative OE already deducts. FY2025: net income $613,461,000 vs OCF $1,080,380,000 — a $466,919,000 gap against SBC of $258,202,000, depreciation of $67,112,000 and deferred taxes of +$45M (statements.json), with the remainder in intangible amortization/impairments and other non-cash items. FY2024 is the same shape: net income $551,313,000 vs OCF $932,719,000, with SBC $267,381,000 and depreciation $87,499,000. The divergence flatters net income's *distance* from cash, not the OE base — OE is built from OCF and charges SBC in full.
- **WIDE_SCENARIO_SPREAD** (super-bull IV 4.05x super-bear IV): real — the Tinder turnaround genuinely bifurcates the outcome. Confidence is capped at medium and the verdict is sized to the conservative end.
- **HIGH_NET_DEBT** (net debt 3.11x normalized OE on the TTM base; 5.09x on the median base in the preliminary run): the balance sheet from the filing (financials_history.csv, FY2025): cash $1,027,838,000 against total debt $3,972,953,000 (LongTermDebtNoncurrent + LongTermDebtCurrent), net debt $2,945,115,000, plus lease liabilities of $118,312,000. Leverage is serviceable on TTM OE of $900,525,000 and TTM FCF of $1,141,454,000 (fundamentals.json), and the company is returning cash ($614,534,000 of TTM buybacks), but at 3.1x the bear cases are stressed with the 0.75/0.90 OE multipliers and a 15% super-bear weight.
- **TIER_BAND** (bear tier D at 8.97% vs bull tier C at 14.55%): the verdict spans tiers — sized to the bear end: the position case rests on the D-tier bear outcome, not the weighted C.

## My thoughts / overlay
- **Method range:** the base choice is the whole debate. On the engine's normalized base ($2.2029/share, median of FY2023–25) the preliminary run — even at the engine's un-recalibrated 9.27% blended growth — printed a weighted IRR of 9.87% and IV@15% of $25.58 (Tier D); with this run's recalibrated growth it would sit lower. The TTM base ($3.6076/share) with recalibrated growth gives Tier C at 11.23%. Honest range: **D to C** — under no defensible base does MTCH clear the 15% hurdle at $45.205.
- The quality is not the debate: ~72% gross margins, ROIC proxy in the mid-20s, SBC falling in dollars ($267,381,000 → $258,202,000 → $240,929,000 TTM), capex under 2% of revenue, and over $1B of TTM free cash flow funding buybacks and a dividend. The debate is purely price versus a melting-but-monetizing core asset: payers are falling 6% a year and management's own Q3 guide is for revenue to decline.
- The $441M settlement history cuts both ways: it proves the OE series can absorb a nine-figure legal one-off in a single year — litigation/governance tail risk at this company is not hypothetical.
- Sector context from the October 2026 Bumble take-private ($6.05/share, ~$1.3B): a distressed dating asset cleared at a low multiple, which anchors the super-bear case more than the bull case.
- Hurdle prices (weighted): the stock clears 15% at **$31.24**, 20% at $22.08, 25% at $17.03. At $45.205 a buyer is paying ahead of the bull case ($43.46) — i.e., paying for a Tinder turnaround that has not yet shown up in payers or revenue.

## Final verdict
- **Final tier: C** (weighted IRR 11.23% on the TTM base; method range D–C, bear case D — size any position to the bear end)
- Confidence: **Medium** (high on the TTM base's filing arithmetic and the flag resolutions; the scenario spread is 4.05x and the growth path hinges on an unproven Tinder turnaround)
- One-liner: Quality cash machine, moat 6/10 — TTM owner's earnings $3.61/share and ROIC proxy ~23-27%, but at $45.21 it does not clear 15%: weighted IRR 11.2%, IV@15 $31.24; it clears 15% only below ~$31.
