# TS — Tenaris S.A.
v5 run, 2026-10-14. Luxembourg-incorporated, IFRS (Form 20-F) filer; NYSE price is per ADS, each ADS = 2 ordinary shares (see OVERRIDE / ADS). All DCF figures below are copied from dcf_numbers.json / key_numbers.md or the filed history in financials_history.csv — none are recomputed. Interim 2026 figures are from the company's Q2 2026 results release (GlobeNewswire, Aug 5, 2026), cited as such.

## What it is
The world's leading maker of steel pipes for energy: seamless and welded OCTG (casing and tubing) and line pipe for oil & gas drilling and transport, plus premium connections, threading, coating and the Rig Direct just-in-time delivery/service model. Tubes were 95% of H1 2026 sales per the Q2 2026 release; the rest is other oilfield services and products, mainly in Argentina. Demand is a direct derivative of E&P capex and rig counts — this is a high-quality cyclical, not a compounder.

## Owner's earnings
**FY2025 (20-F via EDGAR, from financials_history.csv):** revenue $11,981,157,000; net income $1,973,279,000; operating cash flow $2,599,580,000; capex $617,183,000; SBC $0 — by filing-sourced override, see OVERRIDE.
- **Conservative owner's earnings FY2025: $1,982,397,000** (OCF − capex − SBC). Latest FY OE/share $3.9185 per ADS (dcf_numbers.json).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $1,864,350,000 — same ballpark as the conservative figure, which raises confidence in the base.
- OE positive 4 of the last 5 fiscal years (oe_positive_years_of_last_5: 4/5): the exception is FY2021, when conservative OE was −$120,443,000 on collapsed post-COVID activity. FY2023 was the cycle peak at $3,775,628,000.
- Balance sheet: engine net debt −$266,925,000 (net cash, on the engine's cash-only definition; net debt is −0.07x normalized OE in the diagnostics). The company's own broader net-cash definition, which includes its investment portfolio, put net cash at $3.6 billion at June 30, 2026 after a $606 million dividend payment in the quarter (Q2 2026 release). Either way leverage is not a factor in this verdict; the return of cash is — dividends plus a buyback that has been shrinking the count ~5%/yr (see BUYBACK_TAILWIND).
- **Base used = the engine's normalized base: median of the last 3 FY OE/share = $4.0069 per ADS** (base_source: median_of_last_3_fy_oe_per_share). The latest FY figure ($3.9185) sits just below the median, so — unlike an inflection name — the median is not stale here; it is a mid-to-late-cycle base spanning the FY2023 peak and the FY2024–25 downleg, which is the right foundation for a cyclical. No TTM base was used: ttm.py is us-gaap-only and exited 3 on this IFRS filer (see STALE_FY).

## OVERRIDE — sbc $0 (filing) and ADS ratio 2.0
- **The gap:** the preliminary engine run exited 4 with `DATA_GAP:sbc` — no SBC facts under any engine tag (ifrs-full share-based-payment concepts) for FY2023, FY2024 or FY2025, in fact for no year 2016–2025. Under v5 no tier is emitted on that gap, correctly.
- **The decision (bounded worker authority, kind "filing"):** judgment.json carries `sbc_override = {value: 0, kind: "filing"}`. This is the filer's own reported position, not an estimate: the FY2025 20-F's consolidated cash-flow statement enumerates every adjustment reconciling income to operating cash flow for 2025, 2024 and 2023, and there is no share-based payment addback in any year; the term "share-based" appears nowhere in the 20-F. Tenaris's compensation disclosure states directors and the CEO are paid cash only, with no long-term incentive or pension plan for them, and its sole long-term program (Note II.P.3) grants units valued on shareholders' equity that are mandatorily redeemed for cash seven years after grant — a cash-settled "other long-term benefit" whose cost already runs through income and provisions, and therefore through operating cash flow. Subtracting it again as equity SBC would double-count it. Equity-settled SBC in the gap years is $0.
- **Band status:** the override is flagged out-of-band by construction (ack_reason in judgment.json): the engine has no filed SBC value in any period to anchor a 0.1x–10x band to (last_filed_value: null). FER's sbc/capex overrides are the same shape — a filing figure where no engine-readable filed value exists.
- **Measured impact (dcf_numbers.json override_impact):** zero, exactly as expected for a $0 override — base OE/share $4.0069 zero-fill → $4.0069 with override; weighted IRR 10.47% both ways. Its only effect is binary: without it there is no tier at all (unblocks_tier).
- **ADS ratio:** judgment.json carries `ads_ratio = {ratio: 2.0}`, sourced from the filer's own 20-F: the consolidated income statements' EPS footnote states each ADS equals two shares (FY2025 EPS $1.83 per share vs $3.66 per ADS), and the ADS is the NYSE-registered class on the 20-F cover. The engine scaled all per-share figures x2 (ADS_RATIO_APPLIED flag), so every per-share figure in this analysis is per ADS and comparable to the $58.17 ADS price. One engine artifact to know: its market_cap_est ($58.858B) still multiplies the ordinary share count (1,011,823,958) by the ADS price, overstating the traded market cap by the 2x ratio; make_score.py's computed in_scope flag follows that engine figure, so score.json records in_scope_under_40b: false on the engine basis.

## Moat: 6/10 — moderate, carried by premium qualification and footprint
Justification: global premium-OCTG leadership with real qualification/logistics friction, proven through-cycle cash generation — but the product is a steel tube sold into a capex cycle Tenaris does not control.
- FOR: Global leader in seamless and premium OCTG — proprietary premium connections qualified into demanding shale, sour-service and deepwater wells, where failure costs dwarf pipe price; Vertically integrated steelmaking-to-threading footprint inside the major basins (US, Canada, Mexico, Argentina, Italy, Romania, Middle East) — logistics and lead-time advantage rivals importing at distance cannot match; Rig Direct service model and technical collaboration with majors/NOCs embed Tenaris in well design and inventory, creating real switching friction beyond the pipe itself; Through-cycle economics: positive owner's earnings in 4 of the last 5 fiscal years, mid-teens net margins in 2024-25, and a company-reported net cash position ($3.6B at June 30, 2026 per the Q2 2026 release); Aggressive buybacks: share count fell from 1,167,888,739 (FY2023) to 1,011,823,958 (FY2025) in the filed history, a 5.0%/yr tailwind already credited in the growth blend.
- AGAINST: Demand is a derivative of E&P capex and rig counts: revenue went $5.1B (2020) to $14.9B (2023) to $12.0B (2025) — Tenaris is a price-taker on the cycle, not on its own products only; Customers are majors and NOCs with concentrated bargaining power; work is re-won program by program with no long-term lock-in; Capable premium rivals — Vallourec, Nippon Steel, TMK and US mills — contest the same wells, and standard OCTG is a commodity; Cost-side exposure it cannot fully pass through: US tariff costs and rising raw-material/logistics costs cut H1 2026 EBITDA margin to 22.8% from 23.8% (Q2 2026 release); Long-term oil & gas demand / energy-transition risk caps the terminal story, and regional shocks hit shipments directly (Hormuz closure postponed Middle East deliveries in Q2 2026).
- A 6 gives CAP = 9.8 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 9.8 years, 15-year projection.

## DCF — v5 final run (2026-10-14)
Growth sanity check against actual prints (mandatory): the blend's components are rev CAGR 5y +18.41% (a trough-base artifact — see BASIS_BREAK_SUSPECT), rev CAGR 3y +0.62%, latest FY revenue YoY −4.33%, OE/share CAGR 2y −22.14% (off the FY2023 peak); blend −1.86%, plus the capped +5.00pp buyback adjustment = base growth start +3.14% in per-ADS OE terms. That base start is a per-share figure, and it matches what the company is actually printing per share right now: H1 2026 sales rose just 1% YoY and net income was flat, yet EPS per ADS rose 4% on the shrunken share count (Q2 2026 release); management guides H2 2026 sales and EBITDA in line with H1, with Q4 helped by higher prices and volumes. So the base start (+3.14%) is honest, the bull start (+8.14%) requires the guided price/volume recovery plus Hormuz normalization, and the super-bull start (+15.14%) requires a genuine new drilling upcycle — possible (2022 printed far hotter) but correctly low-weighted. No offset recalibration was made: the defaults already straddle the prints. Probabilities 10/25/30/25/10, OE multipliers 0.75/0.90/1.00/1.10/1.25, price $58.17 per ADS.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -8.9% | 0.75 | New drilling downturn; OCTG prices and volumes fall together | $14.89 | 5.21% |
| Bear | 25% | -1.9% | 0.90 | Flat-to-down activity, tariff/raw-material margin squeeze persists | $24.36 | 7.52% |
| Base | 30% | 3.1% | 1.00 | H1 2026 run-rate continues; buybacks carry per-share growth | $33.81 | 9.79% |
| Bull | 25% | 8.1% | 1.10 | US pricing, offshore and Argentina volumes recover; Hormuz reopens | $46.45 | 12.62% |
| Super bull | 10% | 15.1% | 1.25 | Full new upcycle toward 2022-23 conditions | $72.00 | 17.54% |

- **Probability-weighted: IV@15% $36.53 (−37.2% vs price), IV@12% $48.54, IV@10% $61.94, weighted IRR 10.47%, base-case IRR 9.79%**
- **Tier by numbers: C.** Diagnostics (key_numbers.md): OE yield 6.89%, terminal value 18.8% of IV@15%, scenario spread 4.84x, net debt −0.07x normalized OE, 9.4 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (FY2025 ended 9.4 months ago): ttm.py was run and exited 3 — "cannot compute TTM for TS (CIK 1190723): ocf: no annual (FY) fact; sbc: no annual (FY) fact; shares_diluted: no annual (FY) fact" — the expected IFRS failure, since ttm.py reads us-gaap facts only. Per the sweep spec the engine's median base is used instead. Cross-check that nothing material is stale: the Q2 2026 release shows H1 2026 sales $6,067M (+1% YoY), net income $1,056M (flat YoY), Q2 2026 sales $2,967M (−4% YoY) with EBITDA margin squeezed to 21.9% by Hormuz shipment postponements, higher logistics costs and rising raw-material costs, and H2 guided in line with H1 — current earning power is in line with the FY2025-based median, not inflecting away from it.
- **BUYBACK_TAILWIND** (share count −5.01%/yr): real and already credited — the +5.00pp share-count adjustment is inside the +3.14% base growth start; it is not counted again anywhere in the verdict. The filed count fell from 1,167,888,739 (FY2023) to 1,011,823,958 (FY2025), and the company has continued cancelling treasury shares since.
- **BASIS_BREAK_SUSPECT** (>60% revenue jump/drop in the last 5 yrs): resolved as a cycle artifact, not a basis break. The jump is FY2021 revenue $6,521,207,000 → FY2022 $11,762,526,000 → FY2023 peak $14,868,860,000 — the post-COVID rig-count and OCTG price surge, on the same consolidated business; there is no divestiture, restatement or M&A of anything like that scale in the period (the only announced deal is small and post-period: an agreement in May 2026 to buy a Romanian tube plant for EUR 86M, closing expected Q4 2026). Consequence handled in the inputs: the +18.41% 5-yr revenue CAGR is a trough-base artifact, and the blend's median construction already keeps it from driving the model (blend −1.86% before the buyback adjustment).
- **OE_VOLATILE** (OE/share range >3x over the last 5 yrs): real cyclicality — conservative OE totals ran from −$120,443,000 (FY2021) to the $3,775,628,000 FY2023 peak to $1,982,397,000 (FY2025). Handled by construction: the base is the 3-yr median (which spans peak and downleg rather than extrapolating either), and 35% of probability sits on bear-or-worse scenarios. This is also why no tier above C is reachable without assuming a new upcycle.
- **ADS_RATIO_APPLIED**: see OVERRIDE — per-share figures scaled x2.0 from the filer's own 20-F, including the engine market-cap artifact noted there.
- **OVERRIDE_APPLIED:sbc**: see OVERRIDE — filing-sourced $0, measured impact zero, binary unblocks_tier effect only.
- **WIDE_SCENARIO_SPREAD** (4.84x): real — a cyclical's outcome range IS this wide (super-bull IV@15% $72.00 vs super-bear $14.89). Confidence is held at medium and the verdict is sized to the conservative end.

## My thoughts / overlay
- The honest headline is narrower than APP's: defensible bases cluster tightly here (latest FY $3.9185/ADS vs 3-yr median $4.0069/ADS), so the method range is not the story. The story is the price: at $58.17 the market is already paying for the bull path — even the super-bull case, a full return toward 2022-23 upcycle conditions at a 1.25x OE level, returns only 17.54%, and the base case returns 9.79%.
- Quality is not the debate: net cash on either definition, a 6.89% normalized OE yield, buybacks shrinking the count 5%/yr, and a dividend on top (an interim dividend was approved for November 2026 payment per the Q2 2026 release). The debate is purely what you pay for a mid-cycle earnings stream whose next leg is set by rig counts, tariffs and geopolitics (Hormuz), none of which Tenaris controls.
- Standing watch items: the long-running Usiminas-participation litigation provision, which recurs as a line in the 20-F cash-flow adjustments; Techint/Rocca control of the register; US tariff cost pass-through in H2 2026 prints.
- Margin of safety: the stock clears Andrew's 15% hurdle only at or below the weighted IV@15% of $36.53 per ADS; with a real margin of safety against the bear case you would be looking nearer the bear IV@15% of $24.36. At $58.17 there is no margin of safety — the weighted IV@15% sits 37.2% below the price (the engine's upside_at_15 of −37.2%).

## Final verdict
- **Final tier: C** (weighted IRR 10.47% on the v5 final inputs; no tier override)
- Confidence: **Medium** (high on the filing base and the $0 SBC / ADS determinations, medium on any single cycle path — the scenario spread is 4.84x)
- One-liner: Global premium OCTG leader, moat 6/10, company-reported net cash — but on a normalized mid-cycle base the price already pays for a recovery: weighted IRR 10.47%, weighted IV@15% $36.53 vs $58.17 per ADS, Tier C; clears 15% only below ~$36.53 per ADS.

## Engine 5.5 re-score (2026-10-19)
This is a dated addendum. The 2026-10-14 text above is the record of that run and has not been rewritten. Where it is now out of date, the correction is made here (see "Corrections to the 2026-10-14 text"). This is a **make_score-only** re-score under ruling 1 ("Re-run make_score (not the engine)"): dcf_engine.py and ttm.py were not run, so dcf_numbers.json, financials_history.csv and the fragility-flag list are the 2026-10-14 engine output, unchanged and still hash-verified by make_score. That output is pre-5.4 (`engine_version` 5, no `engine_release`). Every score figure below is copied from the regenerated key_numbers.md. The items under "Pending" are not applied and are not this score's figures. Where one of them quotes a figure key_numbers.md does not print (the share-basis replay the 2026-10-19 audit raised), it is labelled as a replay figure.

**Runs (2026-10-19).**
- `make_score.py TS`: exit 0, tier C, weighted IRR 10.47%, IV@15 $36.53. It rewrote judgment.json `in_scope_under_40b` from false to true, giving the ADS-corrected cap as its reason (item 2). It was run a second time after the `ads_ratio.reason` text in judgment.json was updated (item 7); score.json and key_numbers.md came out identical.
- `prices.py TS`: exit 0, with one warning. Nasdaq's previousClose disagreed with the last daily close, so the daily close was used.
- `reprice.py TS`: exit 0. At the last close the live repricing (live.json, gitignored and not a scored record) keeps Tier C and keeps the cap in scope. Its weighted IRR is slightly lower than the scored one, so it sits a little closer to the 10% C/D line.
- Audit follow-up (2026-10-19): no script was re-run. The share-basis replay under "Pending" is a read-only computation with the engine's own replay functions and wrote no file. Ruling 1 bars the engine run, so the audit's share-basis and STALE_FY findings are recorded as open items, not applied.

| | 2026-10-14 (pre-5.4 engine, pre-5.5 make_score) | 2026-10-19 (make_score 5.5, same engine output) |
|---|---|---|
| Price (scored) | $58.17 | $58.17 |
| Base OE/share (per ADS, 3-yr median) · latest FY | $4.01 · $3.92 | $4.01 · $3.92 |
| Weighted IRR · base-case IRR | 10.47% · 9.79% | 10.47% · 9.79% |
| Weighted IV@15% | $36.53 | $36.53 |
| Tier by numbers / final | C / C | C / C |
| Market cap (est) | $58.858B (per-ADS price × ordinary shares) | $29.429B (price × shares ÷ ads_ratio 2; `market_cap_basis` `ads_corrected_by_make_score`) |
| `in_scope_under_40b` | false | **true** |
| Net debt (latest) · net debt / normalized OE | $-266.9M · -0.07x | $-266.9M · -0.13x on the ADS basis |
| Alert gates | not recorded (pre-5.4 score) | `alert_eligible` false · `exit_alert_eligible` false |

**What engine 5.5 changed for TS (applied by make_score)**
1. **Market cap on the ADS basis (ruling 1).**
   - The 2026-10-14 engine priced the 1,011,823,958 ordinary shares (key_numbers.md "Shares diluted (latest)") at the per-ADS price. That overstated the cap 2×. The earlier OVERRIDE / ADS paragraph already called this an engine artifact.
   - key_numbers.md now prints "$29.429B (ADS-corrected by make_score: price × shares ÷ ratio; the pre-5.5 engine printed $58.858B)". score.json records `market_cap_basis: ads_corrected_by_make_score`.
   - The `market_cap_est` inside dcf_numbers.json is hashed engine output. It keeps the old figure until the engine is re-run.
2. **Scope (ruling 1, make_score's reading).**
   - key_numbers.md reads "in scope (market cap under $40B) — corrected by make_score from the ADS-corrected market cap (the pre-5.5 engine's cap said out of scope)".
   - judgment.json still held the scope the old cap implied (false). make_score rewrote that one field to **true**, recorded `in_scope_corrected_by_make_score: true` in score.json and added a `scope_correction` event to `_system/overrides_registry.json`.
   - **Scope call: TS is in scope.** The corrected cap is well under the $40B line, so the call does not hinge on the scored price. The live repricing at the last close also puts the cap under $40B. Unlike JD and VOD, TS does not sit near the line.
3. **Net debt / normalized OE on the ADS basis (ruling 1, "anything downstream").**
   - key_numbers.md reads "-0.13x on the ADS basis (make_score: the pre-5.5 engine's ratio × ads_ratio 2 — it divided net debt by per-ADS OE × ORDINARY shares; the engine printed -0.07x)".
   - The corrected ratio is twice the old one and still a small net-cash figure. HIGH_NET_DEBT fires above 3x and BIG_NET_CASH below -2x, so neither fires on either basis. key_numbers.md names no crossing. No flag appears or disappears.
   - Resolution, as for a flag (what the balance sheet says): the engine's net debt of $-266.9M is cash and cash equivalents less current and non-current borrowings. It reproduces from the FY2025 row of financials_history.csv (debt_current + debt_lt − cash), where nearly all borrowings are current. The figure counts cash only. Tenaris holds a large part of its liquidity in other current and non-current investments, which is why the company's own net-cash figure (quoted in the 2026-10-14 text from the Q2 2026 release) is much larger.
   - On either definition Tenaris is net cash, and leverage plays no part in the verdict. Net debt feeds the engine's diagnostics only, so no IV or IRR input moves.
4. **Tier, base and IRR unchanged.**
   - make_score reads the same engine output, so the base ($4.01 per ADS, median_of_last_3_fy_oe_per_share), the weighted IRR (10.47%) and the tier (C, no tier override) are as recorded.
   - The band fields in score.json (`irr_bear`, `irr_bull`, `tier_bear`, `tier_bull`, `iv_at_20`, `iv_at_25`) are null because the run predates 5.4, which introduced them.
5. **The sbc override's impact is carried, not re-measured (expected).**
   - key_numbers.md reads "base OE/share $4.01 (no override) → $4.01 (with override), +0.00% · weighted IRR 10.47% → 10.47% (+0.00pp) — carried from the prior score.json, not re-measured (engine output release pre-5.4 vs current 5.5.0)". score.json records `impact_carried_from_prior_score: true`.
   - The override is still the only reason TS has a tier (`unblocks_tier`). On older output, 5.5 never replays an override counterfactual through its own engine.
6. **Both alert gates closed until an engine re-run (release mechanics; expected).**
   - `exit_alert_eligible` is false: "engine output predates release 5.5.0 — re-run the engine before an exit alert; tier exists only because of a judgment override".
   - `alert_eligible` is false. At Tier C there is no entry into S/A to gate.
   - The pre-5.4 score recorded neither field.
7. **judgment.json.** Two fields changed and nothing else moved.
   - `in_scope_under_40b`: make_score's rewrite (item 2).
   - The explanatory `ads_ratio.reason` text. Its note that make_score's scope "follows that overstated engine figure" was no longer true, and an engine re-run would have copied it into the 5.5 record. It now records the 2026-10-19 correction.
   - The ratio (2.0) and its 20-F source are unchanged.
8. **Not engaged in this run.**
   - SBC tag priority (ruling 6) compares the us-gaap ShareBasedCompensation and AllocatedShareBasedCompensationExpense tags. TS is an IFRS filer and files no SBC tag the engine reads, so `sbc_tag` stays `OVERRIDE`.
   - USD-override branch (ruling 7): TS reports in US dollars and `fx_conversion` is null. The $0.00 sbc override was never FX-converted and needs no `currency: "USD"` declaration. That requirement applies only at filers whose figures the engine converts.
   - Capex tags (rulings 3–5) and share basis (ruling 2) are engine rules, and the engine was not run. See "Pending".

**New 5.5 flags.** None in this record. The flag list is the hashed 2026-10-14 engine output, and make_score adds no flags.
- The record carries seven flags. Four keep their 2026-10-14 resolutions unchanged: BASIS_BREAK_SUSPECT, OE_VOLATILE, OVERRIDE_APPLIED:sbc and WIDE_SCENARIO_SPREAD. Three are amended or reopened here:
  - ADS_RATIO_APPLIED (ratio 2) now also divides the market cap (item 1).
  - BUYBACK_TAILWIND: the share counts behind it are year-end counts, not weighted-average counts. On the filed weighted-average counts the rate the engine would credit is lower (first item under "Pending"). The buyback itself is real.
  - STALE_FY is **reopened**. Its 2026-10-14 resolution (ttm.py exited 3, so the median base was used) does not meet the review rule for a 20-F filer: that rule asks whether the interim 6-K prints TTM operating cash flow and capex. The check is the second item under "Pending".
- HIGH_NET_DEBT / BIG_NET_CASH: not raised on either basis (item 3).
- The new lines make_score prints (market-cap basis, scope, ADS-basis net-debt ratio) are diagnostics, not flags. Items 1–3 resolve them.

**Pending: what an engine 5.5 re-run would change.** These come from the retro-scan replay on today's cached companyfacts (PR-body table (i)) and from the 2026-10-19 audit. They are not applied.
- **Share basis: the recorded base sits on year-end counts. On the filed weighted-average counts the tier would be D, and a plain engine re-run would gap.**
  - The CSV's shares_diluted values for FY2023–FY2025, ending with the 1,011,823,958 above, match Tenaris's year-end `NumberOfSharesOutstanding` counts (an instant tag) fact for fact, even though used_tags names `WeightedAverageShares`.
  - The cached companyfacts file higher `WeightedAverageShares` counts, because the buyback retired shares during each year: 1,178,876,000 (FY2023), 1,127,491,000 (FY2024) and 1,055,929,000 (FY2025), with 1,180,537,000 for FY2022. These counts are not in this record's files, so they cannot be verified from the diff. The FY2023 20-F filed 1,178,738,000 for FY2023 and the later 20-Fs restate it; FY2023 is neither the median year nor a CAGR endpoint, so the choice changes nothing below.
  - **Replay figures, not this score's.** The 2026-10-19 audit replayed the recorded inputs through the engine's own `replay_paths` / `solve_irr` on those counts, and the replay here reproduces it:
    - base $3.8533 per ADS instead of $4.01 (FY2024 is still the median year);
    - three-year share-count CAGR -3.65% instead of -5.01%, so the buyback adjustment is 3.65pp instead of the capped 5.00pp, and g_base is 1.79% instead of 3.14%;
    - scenario IRRs 4.91% / 6.96% / 9.05% / 11.68% / 16.33%;
    - **weighted IRR 9.69%, Tier D**, against the recorded 10.47%, Tier C. The base change alone gives 10.17%.
    - The same replay on the recorded year-end counts returns 10.47% and every recorded scenario IRR exactly, which checks the method. The 2026-10-14 growth rule and the 5.4 rule give the same g_base for TS on either share basis.
  - `WeightedAverageShares` is the IFRS *basic* weighted-average tag. The diluted tag is `AdjustedWeightedAverageShares`, which Tenaris does not file. Under main's 5.4 rules, as under 5.5, a basic count in any of the last 3 FY is DATA_GAP:shares, not a silent swap.
  - Main's engine and the 5.5 engine both exit 4 on TS with DATA_GAP:shares, and the 5.5 replay adds SHARES_FALLBACK for the history years (a non-diluted count, noted here as WORKER_SPEC asks). The gap therefore comes from a 5.4 rule, not a 5.5 one. With no scenarios, the replay also drops WIDE_SCENARIO_SPREAD.
  - To re-score, the worker needs a `shares_override` of kind "filing" from the 20-F's earnings-per-share note (the weighted-average share count for FY2023–FY2025), which WORKER_SPEC step 2 puts in bounds, or must block. judgment.json's `ads_ratio` source cites the same basic and diluted EPS for FY2025, so the basic weighted-average count should also be the diluted one. The audit adds that the FY2025 EPS of $1.83 per share reconciles to the weighted-average count, not the year-end count. Cannot verify from the diff.
  - **Tier risk, now measured.** The published C rests on the year-end counts; on the filed weighted-average counts the replay puts the weighted IRR below the 10% C/D line. Ruling 1 limits this run to make_score and keeps the base, the IRR and the tier as the recorded engine output gives them, so C is the recorded tier, not a confirmed one. Neither alert can fire on it: both gates are closed (item 6).
- **STALE_FY: TTM base from the Q2 2026 interim report (reopened).**
  - The 2026-10-14 resolution rests on ttm.py exiting 3 on this IFRS filer and on a cross-check of H1 2026 sales and net income. It quotes no H1 2026 operating cash flow or capex.
  - The re-run worker should check the Q2 2026 6-K / results release for H1 2026 and H1 2025 operating cash flow and capital expenditures. If they are printed, build TTM OE = FY2025 + H1 2026 − H1 2025 on the weighted-average share basis above, show the construction, and pin it as a declared `base_override`. If they are not printed, say so and escalate. Cannot verify from the diff whether the 6-K prints them.
  - The recorded and the replayed weighted IRRs both sit within 1pp of the C/D line, so a TTM base could move the tier either way. It is a new judgment input that needs an engine run, so ruling 1 leaves it to the re-run.
- **Capex: no change.**
  - The capex tag is the IFRS combined `PurchaseOfPropertyPlantAndEquipmentIntangibleAssetsOtherThanGoodwillInvestmentPropertyAndOtherNoncurrentAssets`, which already includes intangible purchases. Decision 5 never adds its intangible leg on top of that tag. Decision 4's component sum applies only when the roll-up is absent, and it is present in every year.
  - The replay's FY2023–FY2025 capex matches the recorded figures on the same tag. The cached facts show no other PP&E or intangible purchase line in those years. That answers the single-tag question for this 20-F filer: the one tag is the combined line.
  - CAPEX_COVERAGE_LOW would not fire, because capex is at or above D&A in each of FY2023–FY2025 (financials_history.csv).
- **SBC: no change.**
  - There is still no SBC tag the engine reads, and the replay fills FY2023–FY2025 with the $0.00 filing override.
  - Caveat for the re-run worker: the cached companyfacts carry a single FY2023 `KeyManagementPersonnelCompensationSharebasedPayment` fact, from the FY2023 20-F's related-party disclosure. It is a key-management compensation disclosure, not a cash-flow addback, and the engine does not read it. It may be the cash-settled retention program the override cites, whose cost already runs through operating cash flow.
  - Whether any part of it is equity-settled cannot be verified from the run. The 2026-10-14 statement that "share-based" appears nowhere refers to the FY2025 20-F.
- **No override needs restating.** The only field override is the $0.00 sbc override, and TS reports in USD. So neither the USD-override branch (ruling 7) nor an HTHT-style restatement of a local-currency override applies. The retro scan records no share-scale or split-basis action (ruling 2) for TS.
- **Band and TIER_BAND.** A 5.4-or-later run prints the band. In the key_numbers.md scenario table the bear case's 7.52% is a D-band IRR and the bull case's 12.62% is a C-band IRR, so TIER_BAND would fire and the position is sized to the bear end. The 2026-10-14 verdict already put its margin-of-safety price there (the bear IV@15%).
- **Market cap on a re-run.** A 5.5 engine run prices the cap itself (price × shares ÷ 2, with `market_cap_basis` recorded) on whatever share count the re-run settles. In the replay the cap stays well under $40B.

**Corrections to the 2026-10-14 text.** This section supersedes the passages below; the text above stays as the record.
- OVERRIDE / ADS paragraph ("market_cap_est ($58.858B)", "score.json records in_scope_under_40b: false on the engine basis"): the cap is now $29.429B on the ADS basis, and score.json and judgment.json both record in scope (items 1–2).
- Owner's earnings balance-sheet bullet and DCF diagnostics ("net debt is −0.07x normalized OE"): it is -0.13x on the ADS basis (item 3).
- Moat FOR pillar and BUYBACK_TAILWIND: the share counts quoted "in the filed history" for FY2023 to FY2025 are year-end outstanding counts, not weighted-average diluted counts (first item under "Pending").
  - The quoted endpoints and the quoted rate also disagree. The two counts are FY2023 and FY2025, two years apart, and imply a faster rate than 5.0%/yr. The 5.0%/yr is the engine's three-year CAGR (key_numbers.md "Share count CAGR: -5.01%"), measured from FY2022's count in financials_history.csv to FY2025's.
  - On the filed weighted-average counts the three-year rate is -3.65% (replay figure). The pillar text in judgment.json and score.json is unchanged, because ruling 1 bars moat changes in this run. The re-run should restate it on the weighted-average counts and the three-year window.

**Why the tier is what it is.**
- **C by numbers, no override.** On the recorded inputs the weighted IRR of 10.47% is inside the 10–15% C band. The base case is 9.79% and the super bull 17.54%. A make_score-only run cannot move the tier, and it did not move.
- **Modeled, not a misfit.** Energy / steel pipes is not a sector misfit (score.json `model_fit: modeled`), so the 2026-10-15 notch policy does not apply.
- **The pending items point down.** On the filed weighted-average counts the replay gives 9.69%, Tier D, and a plain engine re-run would gap on DATA_GAP:shares until a filing-sourced share count fills it. Only the STALE_FY check (a TTM base from the Q2 2026 interim report) could move the figure either way.
- **Why C is still published.** Ruling 1 limits this run to make_score and keeps the recorded base, IRR and tier, so C stands on this record. It is not a confirmed tier, and neither alert gate is open. Queue TS for an engine re-run with a filing-sourced `shares_override` (the weighted-average counts from the 20-F EPS note) and the STALE_FY check.
- **Hurdle price unchanged.** TS clears 15% only at or below the weighted IV@15% of $36.53 per ADS, against a $58.17 price.
- **Confidence stays medium on this record.** WIDE_SCENARIO_SPREAD and the reopened STALE_FY keep it below high. Ruling 1 bars changing it in this run. The measured share-basis defect and an IRR on the C/D line are reasons for the re-run to revisit it.
