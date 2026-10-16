# TSEM — Tower Semiconductor Ltd.
v5 run, 2026-10-15. In scope (market cap $23,759,948,520 at $209.16, nasdaq_quote_api — under the $40B cutoff).

All figures below are copied from dcf_numbers.json, financials_history.csv, ttm.py output, or cited search results — none are recomputed.

## What it is
Israeli specialty analog foundry: it manufactures other companies' designs on specialized process platforms — silicon photonics (SiPho) for AI data-center optical interconnect, silicon germanium (SiGe) BiCMOS, RF SOI for mobile front-ends, BCD power management, and CMOS image sensors — from fabs in Israel, the US and Japan. It does not compete in leading-edge logic. The current story is SiPho: Q2 2026 (company release, reported Aug 2026) was a record quarter — revenue $460 million, +24% year over year, gross margin 30%, net profit $90.8 million, operating cash flow $177 million — with SiPho at a $680 million annualized run rate versus $180 million a year earlier, Q3 2026 revenue guided to $520 million (±5%), and the 2028 target model raised to $3.6 billion of revenue and $1.2 billion of net profit, backed by ~$1.3 billion of SiPho customer contracts for 2027 and ~$290 million of customer prepayments.

## Owner's earnings
**FY2025 (20-F via EDGAR, from financials_history.csv):** revenue $1,566,104,000 (+9.05% YoY, the engine's latest rev YoY); net income $220,470,000; operating cash flow $395,482,000; capex $444,425,000; SBC $37,768,000 (always a real cost in this sweep).
- **Conservative owner's earnings FY2025: −$86,711,000 = −$0.76/share** (base_oe_latest_per_share, dcf_numbers.json). Capex alone exceeded operating cash flow; SBC is not the problem here — capacity spending is.
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): **+$233,559,000** (financials_history.csv). The two definitions disagree on sign, and the disagreement is the central judgment of this run: FY2025 capex of $444,425,000 versus D&A of $303,112,000 means a large slice of capex is growth capacity (the 20-F describes a $920 million capex plan, primarily for SiPho/SiGe capacity), not maintenance. The sweep's conservative definition charges all capex, and that is the base the tier keys on — the maintenance figure is reported for the range, not used as the base.
- **Normalized base used (engine default): median of last 3 FY OE/share = −$0.19/share.** OE positive in only 3 of the last 5 fiscal years.
- The one strongly positive year in the window is not run-rate: FY2023 conservative OE was +$204,128,000 on operating cash flow of $676,561,000, with net income of $518,494,000 and operating income of $547,264,000 on revenue that *fell* to $1,422,680,000 — that is the year the Intel acquisition collapsed and the termination payment landed. Since then OCF fell to $448,682,000 (FY2024) and $395,482,000 (FY2025) while capex stayed at $436,153,000 / $444,425,000, so conservative OE went −$21,308,000 then −$86,711,000.
- Balance sheet is not the risk: net debt (latest, dcf_numbers.json) is −$73,851,000 — a small net-cash position. It is also small against a $23,759,948,520 market cap; it does not cushion the valuation.
- Dilution is mild: diluted shares 113,597,000, share-count CAGR +0.85%/yr (engine), already deducted as a −0.85pp adjustment in the growth blend. SBC of $37,768,000 is modest by sweep standards.

**TTM check via ttm.py — failed, and the failure is recorded, not worked around:**
- ttm.py exited 3 with: "cannot compute TTM for TSEM (CIK 928876): ocf: no annual (FY) fact; sbc: no annual (FY) fact; shares_diluted: no annual (FY) fact; capex: no capex facts in companyfacts under any candidate tag and no capex_override in judgment.json — refusing to zero-fill (same DATA_GAP standard as the engine)".
- No TTM base was pinned and no TTM figure was hand-computed. The engine's median base is used, with the reason stated: ttm.py produced no TTM for this 20-F filer in this run.
- Directional check from the Q2 2026 release (cited above, not a computed TTM): in that record quarter, investments in property and equipment were $187 million against operating cash flow of $177 million — capex still exceeded OCF before any SBC deduction. There is no evidence in the prints that a TTM conservative OE through Q2 2026 would be positive; staleness does not rescue this name.

## MOAT: 5/10 — moderate / narrow
Justification: a differentiated specialty foundry, not a scale leader. Tower leads in silicon photonics for AI data-center optical interconnect and holds deep, hard-to-replicate process know-how across SiPho, SiGe BiCMOS, RF SOI and CMOS image sensors, where customer designs are qualified onto specific process recipes and switching means re-qualification; contracted SiPho demand and customer prepayments evidence real stickiness. Capped at moderate: Tower is sub-scale versus TSMC/GlobalFoundries, has no leading-edge logic position, earned only thin foundry margins through the cycle before the current ramp, and its growth is now concentrated in one hot end-market whose demand and pricing it does not control — funded by a capex program that consumes all of its operating cash flow.
- FOR: leading silicon photonics foundry position for AI data-center optical interconnect — SiPho at a $680M annualized run rate in Q2 2026, guided by management to cross a $1B run rate in Q4 2026
- FOR: deep specialty process know-how (SiPho, SiGe BiCMOS, RF SOI, BCD power, CMOS image sensors) — designs qualified onto Tower recipes are slow and expensive to move
- FOR: contracted demand visibility — ~$1.3B of SiPho customer contracts for 2027 and ~$290M of customer prepayments received
- FOR: multi-fab footprint across Israel, the US and Japan, with Japanese government (METI) support for the 300mm expansion — a scarce diversified-supply asset
- FOR: net-cash balance sheet (engine net debt −$73,851,000) funds the expansion without forced dilution
- AGAINST: sub-scale specialty player with no leading-edge logic; TSMC, GlobalFoundries and Intel are all pushing into silicon photonics
- AGAINST: capex intensity consumes the business — FY2025 capex of $444,425,000 exceeded operating cash flow, and the $920M expansion plan plus a further Japan build-out keep OE negative while capacity is built
- AGAINST: growth concentration in AI optical interconnect — a narrow set of transceiver customers; an AI capex slowdown or a co-packaged-optics architecture shift hits the core growth leg
- AGAINST: thin through-cycle pricing power — FY2025 revenue grew only 9.05% and net income was $220,470,000 on $1,566,104,000 of revenue with the SiPho ramp already starting
- AGAINST: capacity execution risk — the Japan dual-track expansion must be built, qualified and filled at high utilization for the raised 2028 target model ($3.6B revenue) to hold
- A moat of 5 gives CAP = 8.5 years — moot for the valuation here, since there is no positive OE base to fade.

## DCF — v5 final run (2026-10-15)
Final engine pass: `--moat 5 --probs 0.10 0.25 0.30 0.25 0.10` (default probabilities; offsets/multipliers never reached, because the F branch fires first). Engine output: tier_by_numbers **F**, implied IRR null, weighted IV null. The five scenario slots carry the default likelihoods for the record, each with its story — no IVs or IRRs exist, by design:

| Scenario | Prob | Growth start | OE mult | Story | IV@15% | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | n/a — no OE base | n/a | AI capex cycle turns before the Japan capacity fills; SiPho commoditizes as larger foundries enter; capex stays high and OE stays negative for years | n/a (OE < 0) | n/a |
| Bear | 25% | n/a | n/a | SiPho grows but pricing/utilization disappoint; capex only slowly falls toward D&A; first positive conservative OE is late-decade and small vs a $23.76B cap | n/a (OE < 0) | n/a |
| Base | 30% | n/a | n/a | Q3 guide and the 2027 SiPho contracts deliver, margins hold near Q2 2026 levels, and capex normalizes as the $920M program completes — OE turns positive, but years too late and too small to support $209.16 on an OE DCF run today | n/a (OE < 0) | n/a |
| Bull | 25% | n/a | n/a | The 2028 target model ($3.6B revenue, $1.2B net profit) is real and capex drops sharply once capacity is installed — a forward earnings-power story, not an owner's-earnings story on current filings | n/a (OE < 0) | n/a |
| Super bull | 10% | n/a | n/a | Tower becomes the default optical foundry for the AI build-out and holds 30%-type gross margins at scale — a narrative/consensus-EPS valuation, not underwritable from today's OE | n/a (OE < 0) | n/a |

- **Probability-weighted IV@15% / weighted IRR: not computable — no positive normalized owner's earnings.**
- Growth sanity check: revenue growth is real and accelerating — FY2025 +9.05%, Q2 2026 +24% YoY, Q3 2026 guided to $520 million — and the engine's blended growth of 4.35% (5-yr revenue CAGR; 3-yr CAGR −2.27%) badly understates the current trajectory. It changes nothing: no scenario start was ever applied, because the F branch keys on the negative OE base, not on growth. The failure is below the revenue line — in capex absorption, not demand.
- **Hurdle math:** there is no price at which TSEM "clears 15%" on current conservative owner's earnings, because those earnings are negative on both the normalized base (−$0.19/share) and the latest FY (−$0.76/share); no margin-of-safety price can be quoted from this method. At $209.16 the market is paying today for the 2028 target model and a post-build capex collapse that the filings do not yet show.

## FLAGS — every fragility flag resolved
- **STALE_FY** (latest FY ended 2025-12-31, 9 months ago): ttm.py was run and exited 3 (full message quoted under Owner's earnings) — it produced no TTM for this filer, so no `--ttm` pin was used and the engine's median base stands, with that reason stated. The Q2 2026 prints were checked as a directional substitute: record revenue and margins, but quarterly capex ($187M) still exceeded quarterly OCF ($177M), so a current TTM would not obviously flip the sign. Flag resolved by disclosure, not by a pin.
- **ADS_RATIO_MISSING** (preliminary run) → **ADS_RATIO_APPLIED** (final run): resolved with an ads_ratio of 1.0 declared in judgment.json under step 8(d) bounded authority. Tower is a direct-listed foreign private issuer — its own FY2025 Form 20-F (Item 9) states its ordinary shares are listed and traded on Nasdaq and the TASE under TSEM; the Section 12 security is the ordinary share itself, there is no ADS program, and per-share figures and the traded price are on the same basis (scaling ×1.0 in the final dcf_numbers.json).

## My thoughts / overlay
- The business inflection is genuine — record revenue, record 30% gross margin, contracted 2027 SiPho demand — and it still screens F, because the sweep charges all capex as a cost and Tower is mid-build: $444,425,000 of capex against $395,482,000 of OCF in FY2025, with a $920M program and a further Japan expansion still ahead. That is the screen working as designed, not a data error.
- The honest method range: conservative OE is negative on every basis the engine computes (normalized median −$0.19/share, latest FY −$0.76/share). The only positive figure is the maintenance definition (+$233,559,000 in FY2025), which assumes most capex is growth — plausible, but even that total is small set against a $23,759,948,520 market cap, and the maintenance definition is not the sweep's base. There is no defensible alternative tier today.
- What would change the verdict: the capacity actually filling (Q3 guide $520M and the 2027 contracts are the first tests) **and** capex falling below OCF − SBC on filed numbers — i.e. conservative OE printing positive for a full fiscal year. Until then the bull case is a forecast about 2028, not a reading of current filings.
- Balance sheet is a non-issue in both directions: net cash of $73,851,000 (engine) neither funds the remaining build on its own nor threatens solvency; the risks are valuation (the price pre-pays the 2028 model), customer/end-market concentration in AI optics, and Japan capacity execution.

## Final verdict
- **Final tier: F** (tier_by_numbers F; no override — there is no positive normalized owner's earnings to underwrite any hurdle)
- Confidence: **Medium** (high that conservative OE is negative on the filed FY bases; the TTM check could not be completed because ttm.py exited 3 for this 20-F filer, and the F says nothing about whether the contracted SiPho ramp eventually flips OE positive — that is the live question for a future re-run)
- One-liner: Real specialty-foundry franchise riding the AI silicon-photonics wave, moat 5/10 — but conservative owner's earnings are negative on the normalized base (−$0.19/share) and in the latest FY (−$0.76/share) because capex absorbs all operating cash flow, so it cannot clear 15% at $209.16 on an OE DCF at any scenario; Tier F until the capacity build converts to positive OE.
