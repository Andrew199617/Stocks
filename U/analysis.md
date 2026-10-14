# U — Unity Software Inc.
Sweep run, 2026-10-13 (engine v5 rerun of the 2026-10-12 v4 pass; same filing-derived inputs, re-verified — the v5 audit regression check reproduces this name's TTM base to the dollar).

## What it is
The dominant game engine for mobile and indie development (Create Solutions: engine subscriptions, ~29% of revenue) plus an advertising/monetization business (Grow Solutions, ~71%): the Unity Ads Network, now driven by the Unity Vector AI ad platform (launched May 2025, ex-ironSource), and a shrinking "non-strategic" tail (ironSource Ads Network, Supersonic publishing) being deliberately wound down / sold (Supersonic sold to Tripledot, Aug 2026). The investment story in 2026 is a Vector-led re-acceleration sitting on top of a still GAAP-loss-making company.

## Owner's earnings (SEC EDGAR, filing-direct)
History (conservative OE = OCF − capex − SBC): FY2023 −$470M, FY2024 −$310M, FY2025 +$18.7M — **positive in only 1 of the last 5 fiscal years**. The drag is not capex (trivial, $19M in FY2025) and not OCF (positive and rising: $235M → $316M → $423M FY23→25). The drag is SBC: $649M / $596M / $385M in FY23/24/25.

- **Normalized base (engine default, 3-yr median OE/share): −$0.78/share → preliminary v5 run verdict Tier F, no tier emitted on scenarios.** Rejected as the final base — see BASE_DIVERGENCE in Flags: the median is built from the two post-ironSource-reset years when SBC ran at 30-33% of revenue and Grow was collapsing. It describes the old company, not the current one.
- **Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): FY2025 $626.6M — NOT credible, do not use.** It is an artifact: $556M of convertible notes were reclassified into current liabilities at Dec 2025 (current liabilities $889M → $1,526M), and because the engine's debt-current tag doesn't capture Unity's convertible tags, that reclass ran through ΔNWC (−$587M) and straight into maintenance OE. The OCF-based conservative figure is the clean one here.
- **Base used — TTM owner's earnings through Q2 2026, computed by `ttm.py` from EDGAR 10-Q YTD facts (never hand-computed):**
  - OCF: FY2025 $422.955M − prior YTD (H1'25) $146.122M + current YTD (H1'26) $276.908M = **TTM $553.741M**
  - Capex: FY2025 $19.024M − prior YTD $12.164M + current YTD $8.492M = **TTM $15.352M**
  - SBC: FY2025 $385.214M − prior YTD $200.394M + current YTD $157.113M = **TTM $341.933M**
  - Shares: TTM diluted = current-YTD weighted average **436.069M**
  - **TTM OE = 553.741 − 15.352 − 341.933 = $196.456M = $0.45052/share** (`--base-oe-ps 0.45051585872877914`)
  - SBC is falling fast — 29.7% / 32.9% / 20.8% of revenue FY23/24/25, 16.9% TTM, ~14% in Q2'26 (lowest in company history per the Q2 call) — but at $342M TTM it is still 1.7× the OE it leaves behind. OE before SBC would be $538M ($1.23/share); the gap between those two numbers *is* the Unity debate.
- TTM revenue ~$2,028M. Balance sheet (manual, engine can't see the convertible tags — net_debt_latest is null in dcf_numbers.json): cash ~$2.35B at Jun 30 2026 vs convertible debt ~$2.24B ($557M current + $1,680M non-current) → **net cash ≈ +$115M, immaterial either way**; the current converts are covered ~4× by cash. Leverage is not the story.

## Moat score: 5/10 — moderate/narrow
**FOR:**
- Installed base — Unity powers the majority of mobile games (commonly cited ~70% of the top-1,000 mobile titles; ~51% of 2024 Steam releases); switching engines mid-project or mid-live-service is genuinely costly: code, pipelines, staff skills, Asset Store content.
- Engine↔ads flywheel is unique: the Create installed base is supply and signal for Grow/Vector, and Vector's data advantage compounds with that supply — Strategic Grow +63% YoY in Q2'26, Vector passed a $1B run rate two quarters early, Q3'26 Strategic Grow guided +68-70%.
- Create revenue increasingly recurring (~80% subscription/seat-based).

**AGAINST:**
- Pricing power tested and failed — the 2023 Runtime Fee was reversed within ~a year after developer revolt; Godot (free, open source) is the standing Plan B, its Steam release share roughly doubling since 2024.
- Share erosion at the high end: GDC 2026 survey put Unreal as primary engine for 42% of developers vs Unity 30% — Unreal owns AAA/AA and a disproportionate share of Steam *revenue*.
- Create itself barely grows: +2% YoY in Q2'26 (+14% ex a $12M one-time item in Q2'25) — the moat business is not the growth business.
- In ads, Unity is the challenger, not the leader: AppLovin's AXON is ahead and competes for the same publisher supply, which is bought, not owned.
- No owned consumer surface; hostage to Apple/Google privacy and store rules.
- Returns on capital still negative on a GAAP basis.

A 5 gives CAP = 2 + 1.3×5 = **8.5 years** (growth holds 2 years, then converges to the 2.5% terminal rate over 8.5 years, 15-yr projection) — respects the mobile installed base, refuses to grant a durable wide moat to a company that couldn't hold a price increase.

## DCF — FINAL v5 run (2026-10-13)
**Growth recalibration (written reason, per the standing rules):** the engine's blended growth is 9.96% (rev CAGR 5y 19.1% / 3y 10.0% / latest YoY 2.0% — all straddling the ironSource basis break and the deliberate 2024 portfolio reset) minus a 5pp dilution deduction = **g_base 4.96%**. That blend describes a company that no longer exists. Scenario starts were instead set as absolute levels via offsets (−5/+3/+11/+19/+27pp) anchored to current prints: Q1'26 revenue +17% YoY, Q2'26 +24% (Grow +35%, Strategic Grow +63%, strategic revenue +38%, Create +2%), H1'26 +20%, Q3'26 strategic guidance +44-47%. Two honest caveats: (a) the starts are revenue-anchored while the engine grows OE/*share* — ongoing dilution drags per-share growth, partly offset by SBC falling in absolute dollars, which makes total OE grow *faster* than revenue; (b) base 16% sits below the Q2 +24% print on purpose — Vector laps its May-2025 launch comps, the non-strategic tail (~$60M/qtr, −33% YoY) keeps shrinking to zero, and Create grows low-single digits. Probabilities nudged one notch from defaults toward the bull side (bear 25→20, super bull 10→15) because the inflection is in filed numbers (two accelerating quarters, SBC down in dollars), not just guidance. Multipliers left at defaults 0.75/0.90/1.00/1.10/1.25 for cross-company comparability — note even the super-bull 1.25× captures only part of what full SBC normalization would do, and it still doesn't matter (below).
Price: **$46.63** (Nasdaq quote API; market cap ~$19.6B, in scope <$40B) — ~104× TTM owner's earnings, ~9.7× TTM sales.

| Scenario | Prob | Growth start | OE mult | IV@15% | IRR |
|---|---|---|---|---|---|
| Super bear | 10% | 0.0% | 0.75 | $2.49 | 3.1% |
| Bear | 20% | 8.0% | 0.90 | $4.17 | 3.7% |
| **Base** | **30%** | **16.0%** | **1.00** | **$6.43** | **4.5%** |
| Bull | 25% | 24.0% | 1.10 | $9.76 | 5.6% |
| Super bull | 15% | 32.0% | 1.25 | $15.20 | 7.4% |
| **Probability-weighted** | | | | **$7.73** | **5.0%** |

Weighted IV@12% $10.63. **Tier by numbers: D** (weighted IRR 4.95%). Diagnostics: OE yield 1.0%, terminal value 22% of IV@15% (low — the shortfall is the base, not the terminal), scenario spread 6.1×, months since FY end 9.4.

Scenario sanity check vs actual prints: super bear 0% is below every current print — justified: total revenue *fell* 17% in 2024 when this company last stumbled, and an ad recession + Vector share loss to AppLovin is a live path, not a tail fantasy. Bear 8% ≈ the trailing pace ex-inflection. Base 16% < Q2's +24% for the comp/runoff reasons above. Bull 24% = holding the Q2 total-company print. Super bull 32% is below the +38% strategic print for a stated reason: it is a *total-company OE/share* rate, and Create (~29% of revenue, +2%) caps the blend no matter what Vector does.

## FLAGS — every fragility flag resolved
- **STALE_FY (FY ended 9 months ago):** Resolved with the TTM base above — computed by ttm.py, all inputs quoted from its output. The TTM base ($0.45) is 10× the latest-FY figure ($0.04), which is exactly why the stale FY could not be used raw.
- **BASE_DIVERGENCE (real, surfaced in the preliminary run — latest FY +$0.04 vs 3-yr median −$0.78):** The *median* is the distorted one. FY23-24 carry peak SBC ($649M/$596M, ~30-33% of revenue) and the post-merger Grow collapse; OCF has since risen four straight periods (FY23 $235M → TTM $554M) while SBC fell in absolute dollars. An inflection, so the median lags reality — the APP lesson in reverse. But the latest FY alone ($0.04) is also nearly zero; the honest base is TTM, and even it is only $0.45.
- **LOW_OE_YIELD (1.0%):** Confirmed and central. At $46.63 the price rests almost entirely on growth *and* on OE-margin expansion (SBC normalization) that the standardized model only credits through the ≤1.25× multipliers. Even granting the super-bull path outright leaves IV@15% at $15.20 — one-third of the price.
- **WIDE_SCENARIO_SPREAD (6.1×):** Real — a company whose OE was negative 18 months ago genuinely has a wide outcome range. Confidence capped at **low** per the rules.
- **DILUTION (share count growing 10.7%/yr):** The 3-yr window is inflated by the ironSource merger issuance (shares 310.5M FY22 → 380.5M FY23 — merger consideration, not SBC creep). The current pace is still heavy: +6.3% FY24→25, diluted count +4.9% YoY in Q2'26, driven by the $342M TTM SBC bill. Mitigant: SBC dollars are now falling (H1'26 $157M vs H1'25 $200M per EDGAR), so the dilution rate should decay. The engine's −5pp growth deduction was *not* double-applied: scenario starts were set as absolute OE/share levels (see recalibration note), with the dilution drag acknowledged there.
- **NI_OCF_DIVERGENCE (2023, 2024, 2025):** Resolved — structural, not a one-off cash trap. GAAP net losses (−$822M/−$664M/−$403M) vs positive OCF are explained by non-cash SBC plus D&A dominated by ironSource intangible amortization ($564M/$409M/$461M). Named one-offs inside the window: Q1 2026 intangible impairment of **$270.5M** (writing down non-strategic/ironSource intangibles — a big reason TTM net loss *widened* while TTM OCF rose), and a $42.7M gain on convertible-debt extinguishment in FY2025 NI. Conclusion: trust the OCF-based OE; distrust NI-based measures here (see the maintenance-OE artifact above).
- **BASIS_BREAK_SUSPECT (not emitted — no single year crossed the 60% threshold — but present):** FY2023 revenue +57% is ironSource consolidation (closed Nov 2022); FY2024 revenue −17% is the deliberate portfolio reset / non-strategic exit, not demand collapse. Every historical CAGR straddles one or both breaks; that is why scenario starts were anchored to 2026 strategic-business prints instead of the blended CAGR.
- **HIGH_NET_DEBT / BIG_NET_CASH (not emitted — engine's net debt is null because Unity reports converts under ConvertibleDebt tags the engine doesn't map):** Resolved manually above: net cash ≈ +$115M at Jun 30 2026. Neither a cushion nor a risk at this valuation; the $557M current portion is covered ~4× by cash.

## My thoughts / overlay
- The turnaround is real and filed, not promised: revenue re-accelerating (+17% → +24%), Vector ahead of plan (>$1B run rate, +23% QoQ in Q2), SBC falling in dollars, OCF TTM $554M, GAAP operating margin improving sharply. None of that is the argument. The argument is arithmetic: after deducting SBC as the real cost it is, the whole company produced $196M of owner's earnings in the last twelve months against a $19.6B market cap.
- **Method range:** the defensible-inputs range here is F (normalized-median base — rejected with reasons above) to D (this run). There is no defensible standardized run that gets Unity above D at $46.63: the *super-bull scenario taken alone* — 32% growth start, 1.25× OE — yields 7.4% IRR. To clear a 15% hurdle at this price you must believe SBC largely disappears as a cost *and* Vector-scale growth persists for a decade; that is a venture thesis, not an owner's-earnings DCF conclusion.
- What would change the answer: SBC continuing to fall toward ~8-10% of revenue while Grow holds 20%+ — two or three more filed quarters of that and the TTM base roughly doubles, and this screen should be re-run. The next tells are Q3'26 SBC dollars and Strategic Grow growth as Vector laps its launch.
- Hurdle math: the stock clears 15% at the **weighted IV of $7.73**; even on super-bull-only inputs the clearing price is $15.20. A 30% margin of safety on the weighted IV puts an entry near **~$5.40**. At $46.63 the buyer is paying ~6× the weighted IV@15%.

## Final verdict
- **Final tier: D** (weighted IRR 5.0% on the TTM base; preliminary normalized base said F — the TTM resolution moves it to D, and no defensible input set moves it further). No tier override.
- Confidence: **Low** (WIDE_SCENARIO_SPREAD + LOW_OE_YIELD + OE positive in only 1 of the last 5 fiscal years; high confidence only in the narrow claim that the current price is far above any OE-supported value)
- One-liner: Real Vector-led turnaround, moat 5/10 — but TTM owner's earnings are just $0.45/share after a $342M SBC bill, so at $46.63 the weighted IRR is 5.0% (IV@15% $7.73); it clears the 15% hurdle only below ~$7.73, and even the super-bull case alone clears only below $15.20.
