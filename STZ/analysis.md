# STZ — Constellation Brands, Inc.

**STATUS: SCORED — Tier D (2026-10-14, engine v5 re-run).** This run re-claimed STZ after it was requeued under the 2026-10-14 bounded worker override authority. The filing-sourced shares override (carried in judgment.json, verified in the FY2026 10-K) covers DATA_GAP:shares, and `make_score.py` now builds score.json successfully — the override-impact measurement blocker recorded in the earlier same-day run no longer reproduces (make_score records the override as unblocks_tier: YES, with the no-override counterfactual base/IRR null because no share series exists at all without it; see key_numbers.md).
Runs this session: preliminary engine run with the override in place (defaults, price $126.25, Tier C on default probs/moat 5); ttm.py re-run (TTM OE/share $10.0747, inputs below unchanged); final calibrated pass below (price $126.37). In scope: market cap $22.187B (engine, final pass, key_numbers.md).

## What it is

Constellation Brands produces and markets beer, wine and spirits. Post the 2025 wine divestitures, beer is ~94% of sales: the Modelo family (Modelo Especial — the #1 U.S. beer by dollars — Modelo Chelada), Corona Extra, Pacifico and Victoria, imported from its own Mexican breweries under exclusive, perpetual U.S. rights to the Modelo/Corona brands. The remaining wine & spirits portfolio (Kim Crawford, Mi CAMPO, SVEDKA sold) is small.

- Latest quarter (Q2 FY27, ended Aug 31, 2026, reported Oct 6, 2026): net sales $2,633M (+6% YoY), comparable EPS $3.74 (+3%). Beer shipments +5.5% on distributor restocking while beer depletions (consumer sell-through) fell 0.6% — Modelo Especial depletions ~-2%, Corona Extra ~-5%, partly offset by Pacifico ~+19%, Victoria ~+15%, Chelada ~+5%. Beer operating margin 39.0% (-160 bps) on higher marketing. FY27 guidance reaffirmed: comparable EPS $11.20–$11.90, organic net sales roughly -1% to +1%; management said sustained September demand improvement would support the high end.
- Demand context (unchanged from the 2026-10-12 pass, re-verified): high-end beer buy rates have decelerated for over a year, with Hispanic consumers — an outsized share of Modelo/Corona demand — pulling back more than the general market. Two consecutive quarters of negative flagship depletions; the Q2 shipment beat is restocking, not sell-through.
- Balance sheet: net debt $10,194.1M at FY26 end (engine, dcf_numbers.json). $530M of buybacks in H1 FY27 (10-Q, per Q2 coverage).

## Owner's earnings

Conservative OE totals (OCF − total capex − SBC, EDGAR 10-K, from financials_history.csv): FY24 $1,447.3M, FY25 $1,865.9M, FY26 $1,726.3M; positive 5 of the last 5 years.

Per-share figures exist only via the shares override below (companyfacts carries no weighted-share series for this filer). The engine applies the single FY26 count (175.568M) to every period, so its FY24/FY25 per-share figures use a lower denominator than those years' own counts (183.959M / 181.476M) — but the normalized base is unaffected: the 3-yr median of OE/share is the FY26 figure under either denominator set.

- **Normalized base (engine, final pass) = $9.8327/share** — median of last 3 FY OE/share, base_source `median_of_last_3_fy_oe_per_share`, equal to FY26 OE/share itself.
- **TTM base (ttm.py, saved to ttm.json) = $10.0747/share.** Inputs quoted from ttm.json: OCF FY $2,669.0M − prior YTD (H1 FY26) $1,489.3M + current YTD (H1 FY27) $1,478.6M = TTM $2,658.3M; capex FY $875.0M − $410.1M + $354.1M = TTM $819.0M; SBC FY $67.7M − $32.1M + $34.9M = TTM $70.5M; TTM OE total $1,768.8M over the override denominator 175.568M shares. Note the denominator: ttm.py uses the override (the FY26 annual count) unprorated, not the H1 FY27 10-Q count of 171.503M used in the v4 pass — the TTM base is therefore slightly lower/more conservative than the v4 pass's $10.31.
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): FY26 $1,984.1M (financials_history.csv). The FY24–25 maintenance figures are distorted by the wine impairments flowing through net income (see NI_OCF_DIVERGENCE below); the conservative OCF-based definition is the cleaner headline in both directions — impairments are non-cash and never touch it.
- Capex judgment (carried from the v4 pass, guidance unchanged): a large share of recent capex is growth — ~$800M/yr guided, ~$2B of Mexico beer capacity over FY26–28 including Veracruz, vs D&A of ~$420M/yr. The conservative definition charges all of it; that is the screening-consistent choice and it is kept for the headline. The v4 pass quantified the maintenance-capex sensitivity (IRR ~12–13%) — still below the 15% hurdle — and nothing in Q2 FY27 changes that arithmetic's inputs materially.

## OVERRIDE — shares (filing kind, bounded authority)

EDGAR companyfacts carries **no** weighted-average share series for CIK 16918 in any period (the filer tags share counts with class dimensions the aggregated facts drop), so the engine filed zero share values and exited 4 with DATA_GAP:shares. The gap is filled with a `shares_override`, kind "filing":

- **Value: 175,568,000** — weighted average common shares outstanding, diluted, FY2026.
- **Source (verified this run, directly in the filing document):** Form 10-K for the fiscal year ended February 28, 2026 (filed 2026-04-22), EPS note / consolidated statements of operations: diluted weighted average shares 175.568M for FY2026, 181.476M for FY2025, 183.959M for FY2024.
- **ack_reason (required — the engine flags the override out-of-band because last_filed_value is null):** there is no filed value in companyfacts to band against; the value is the filer's own reported FY2026 diluted count, not an estimate.
- Mechanical effects, stated plainly: the engine applies this one value to all 10 missing fiscal years. FY24/FY25 OE/share are thereby computed on 175.568M instead of their own higher counts, which overstates those two years individually — but the 3-yr median base is the FY26 value either way ($9.8327), and share_cagr reads 0.0 (flat filled series), so the engine's own share-count adjustment contributes nothing; the real ~-2.5%/yr buyback tailwind (183.959M FY24 → 175.568M FY26 → 171.503M H1 FY27, filing EPS notes) is instead embedded in the per-share scenario starts below, as in the v4 pass — not double-counted.
- **Measured impact (key_numbers.md, this run):** base OE/share — (no override) → $9.83 (with override); weighted IRR — → 9.80%. Unblocks tier: YES — this override is the only reason this company has a tier; without it the filing gap blocks scoring entirely. The no-override side is null by construction (no share series exists in companyfacts for any period), which make_score.py now records rather than refusing on.

## Moat score: 6/10 — moderate-strong brands, concentrated and category-capped

- FOR: (1) Brand equity with proven pricing power — Modelo Especial is the #1 U.S. beer by dollars; the portfolio took price/mix for a decade while gaining share (again the #1 dollar/volume share gainer in Q2 FY27 tracked channels, +0.8 beer share points in a down depletion quarter). (2) Exclusive, perpetual U.S. rights to the Modelo/Corona family plus owned Mexican breweries — no competitor can sell the same brands into its market. (3) Structural margin/cost position: ~39% beer operating margins and a focused, premium-only portfolio after the wine exit. (4) Smaller brands compounding off the same distribution (Pacifico now a top-10 U.S. brand, depletions ~+19%; Victoria ~+15%).
- AGAINST: (1) Concentration on every axis: one category (beer ~94% of sales), one supply country (Mexico — tariff and peso exposure), one demand country (U.S.). (2) Disproportionate exposure to the Hispanic consumer pullback now driving negative flagship depletions. (3) U.S. beer category in secular volume decline; high-end buy rates decelerating for over a year. (4) Net debt $10,194.1M caps financial flexibility precisely in the bear case.
- CAP = 9.8 years (moat 6). Rubric: strong brands and real pricing power, but no network effects, no switching costs beyond taste/loyalty, and single-category concentration caps it at the top of "moderate."

## DCF — v5 final run (2026-10-14, median base, on disk in dcf_numbers.json)

Inputs: base OE $9.8327/share (3-yr median), moat 6 (CAP 9.8y), price **$126.37** (Nasdaq quote API). Net debt $10,194.1M = 5.91× normalized OE, OE yield 7.78% (engine diagnostics / key_numbers.md, median pass).

**Growth recalibration (written reason, standing rule):** the engine's blended growth is +0.04% (g_blend 0.00035), built from revenue signals that straddle the 2025 wine divestiture (rev CAGR 5y +1.19%, 3y -1.12%, latest YoY -10.48%) plus an oe_ps_cagr_2y of +9.22% computed off the override-flattened share series — neither is this company's demand growth (organic guide -1% to +1%; TTM revenue roughly flat). Scenario starts are therefore set directly in per-share terms, identical to the v4 pass (evidence unchanged, price within $0.35): super bear -6%, bear -2%, **base +2%**, bull +5%, super bull +8.6%, via offsets vs the blend. Sanity check vs prints: base +2% per-share ≈ flat total OE after the ~2.5%/yr buyback — consistent with the flat organic guide, flat comparable EPS guide, and depletions at -0.3%/-0.6%. Bull +5% requires depletions to recover to low-single-digit growth — above the last two quarters' prints, justified only as a recovery case (distributor inventories rebuilt, Pacifico/Victoria compounding, September improvement noted on the Q2 call), weighted 20%. Super bull +8.6% is a full demand normalization plus capex roll-off case, hence 5%. Probabilities skewed bearish vs defaults (15/30/30/20/5): two consecutive quarters of negative flagship depletions, shipments flattered by restocking, and 5.9× net-debt/OE leave less room for error than the default book assumes. OE multipliers are the defaults (0.75/0.90/1.00/1.10/1.25).

| Scenario | Prob | Growth start | OE mult | IV@15% | IRR |
|---|---|---|---|---|---|
| Super bear | 15% | -6.0% | 0.75 | $41.45 | 6.19% |
| Bear | 30% | -2.0% | 0.90 | $59.40 | 8.15% |
| Base | 30% | +2.0% | 1.00 | $78.85 | 10.28% |
| Bull | 20% | +5.0% | 1.10 | $99.13 | 12.37% |
| Super bull | 5% | +8.6% | 1.25 | $132.21 | 15.54% |
| **Weighted** | | | | **$74.13** | **9.80%** |

Weighted IV@12% $97.28, IV@10% $122.97 (key_numbers.md). **Tier by numbers: D** (weighted IRR 9.80% < 10%). Scenario spread (super-bull/super-bear IV@15%) 3.19× (key_numbers.md). The earlier same-day TTM-base pass of the same configuration printed weighted IRR 9.98%, IV@15% $75.96 — also Tier D; the on-disk final pass uses the median base, and both bases land in the same tier.

## FLAGS — every fragility flag resolved

- **DATA_GAP:shares**: diluted shares missing for FY2024/2025/2026 of the last 3 — in fact for every period in companyfacts. Resolved by the filing-kind shares_override documented above (FY2026 10-K EPS note). `data_gap_uncovered` is empty in the final dcf_numbers.json.
- **OVERRIDE_APPLIED:shares**: see the OVERRIDE section. The override is filing-sourced, in-bounds under the 2026-10-14 bounded authority, and its direction is conservative (TTM denominator higher than the current-period count; median base is the FY26 value either way). Measured impact and unblocks_tier: YES are recorded in key_numbers.md / score.json.
- **STALE_FY** (FY ended Feb 28, 2026; ~7.5 months ago): resolved with ttm.py — full inputs quoted in the Owner's earnings section; TTM OE/share $10.0747 vs median $9.8327, so staleness was not flattering the FY base. The on-disk final pass uses the median base; the earlier TTM-base pass landed in the same tier (D, 9.98%).
- **NI_OCF_DIVERGENCE (2025)**: FY2025 net income was -$81.4M against OCF of $3,152.2M because of non-cash Wine & Spirits impairments — the FY2026 10-K's cash-flow statement shows "Goodwill and intangible assets impairment" of $2,797.7M in FY2025 (goodwill $2,740.7M written to zero, plus $57.0M trademark impairment), plus a $478.0M held-for-sale asset impairment. Non-cash; the OCF-based conservative OE never touches it. The OE base is trustworthy; the NI-based maintenance figures for FY24–25 are not (see Owner's earnings).
- **HIGH_NET_DEBT**: net debt $10,194.1M = 5.9× normalized OE (engine diagnostics, median pass). On an EBITDA-scale denominator it is roughly 3×, investment-grade, and being paid down — but the OE lens is the honest stress view for this screen: at bear-case OE the load rises further and caps buyback flexibility exactly when the bear case would need it. Reflected in the bear-skewed probabilities (45% combined); it does not change the tier, which the weighted IRR already sets.
- **WIDE_SCENARIO_SPREAD** fired only on the default-parameter preliminary run (4.2×) — with the calibrated scenarios the spread is ~3.19× and the flag does not fire on the final pass. Confidence is set to medium regardless (never high here: override-dependent per-share data, wide absolute spread).

## My thoughts / overlay

- The honest headline is unchanged from the v4 pass: at ~$126 the market is already paying for the recovery. An ~8% OE yield on the TTM base sounds cheap for a staples compounder, but with depletions negative, organic growth guided flat, and comparable EPS guided flat, the per-share growth on offer is roughly the buyback (~2.5%) plus pricing — mid-single digits at best in the bull case. OE yield + realistic growth ≈ 10% expected return, which is what both v5 passes print.
- **Method range: D↔C boundary, centered ~10%.** Median base ⇒ 9.80% (D); TTM base ⇒ 9.98% (D); the v4 pass's TTM-on-current-share-count method ⇒ 10.1% (low C). Every defensible run sits within ~0.3pp of 10% and none gets anywhere near 15%. The D (not C) is partly a denominator artifact — the override forces the TTM onto the higher FY26 share count — and is disclosed as such rather than overridden: the tier by numbers stands.
- The one real upside lever the conservative screen suppresses is growth capex: if Mexico/Veracruz capex rolls off toward D&A after FY28, steady-state OE/share rises materially (v4 pass quantified ~$12.64 on TTM cash flows, IRR ~12–13%) — still short of the 15% hurdle at this price. The capex argument makes STZ less overvalued, not cheap.
- Q2 FY27 quality check: the headline beat was restocking (shipments +5.5% vs depletions -0.6%) with margin down 160 bps; September improvement is real but unquantified. Nothing since the Oct 12 pass — no new filings, guidance reaffirmed not raised — justifies moving the scenario book.

## Final verdict

**Tier D (weighted IRR 9.80% median base / 9.98% TTM base), moat 6/10, confidence medium — SCORED.** On the merits: a premier beer franchise priced for a recovery that hasn't shown up in sell-through yet. It clears the 15% hurdle only below ~$74 (the weighted IV@15% $74.13); nearer ~$59 with a 20% margin of safety. Revisit if depletions turn positive or the price breaks into the $70s.
