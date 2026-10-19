# MAA — Mid-America Apartment Communities, Inc.

**Superseded by the Engine 5.5 re-score (2026-10-19) at the end of this file:** Tier D · weighted IRR 6.63% · weighted IV@15% $39.66 · base OE/share $5.71 (source: ttm_json) · 15% hurdle clears at $39.66 (key_numbers.md). The header line below and the 2026-10-17 record through "Final verdict" are left as written.

Price $116.63 · Tier **D** · weighted IRR 7.48% · weighted IV@15% $46.51 · moat 4/10 · confidence **low** (SECTOR_MODEL_MISMATCH)

## What it is

The largest U.S. apartment REIT: ~105,000 units across 16 Sun Belt states, focused on high-growth primary and mid-tier markets (Dallas, Atlanta, Tampa, Austin, Phoenix, Charlotte, Nashville and peers), with in-house development, redevelopment and interior-renovation programs. SIC 6798 (REIT), NYSE-listed, FY ends Dec 31. Market cap (est) $13.663B — in scope under $40B. Q2 2026 (reported Jul 29, 2026): Core FFO $2.08/diluted share, same-store NOI -1%, occupancy ~95.3%, renewal lease pricing +5.2%, new-lease pricing -5.3%, record-low resident turnover 39.6%; FY2026 Core FFO guidance midpoint maintained at $8.53/share while the same-store NOI outlook was narrowed to -1.70% to +0.10% (search results, Q2 2026 call coverage).

## Owner's earnings

- Conservative definition (OCF − capex − SBC), capex = the filing override below: FY2023 $780,264,000 = $6.69/share; FY2024 $741,279,000 = $6.35/share; FY2025 $720,112,000 = $6.15/share (financials_history.csv). OE positive 5 of the last 5 fiscal years.
- Maintenance definition (NI + D&A − min(capex, D&A) − ΔNWC): FY2025 $728,654,000 (financials_history.csv) — close to the conservative figure, as usual for a REIT whose D&A dwarfs its recurring capex line.
- **Base used = TTM OE/share $5.76** (base_source: ttm_json). ttm.json legs: OCF FY $1,078,175,000 − prior YTD $196,618,000 + current YTD $149,644,000 = **TTM $1,031,201,000**; capex **TTM $341,224,000** (override, prorated evenly — the FY and both YTD legs are the same override value, so the TTM capex leg is a full year at the filed run rate, not the half-year artifact that invalidated the TTM base for KIM); SBC FY $16,839,000 − prior YTD $5,261,000 + current YTD $5,822,000 = **TTM $17,400,000**; shares (current-YTD weighted diluted) **116,740,000**; **TTM OE total $672,577,000 → $5.7613/share** (ttm.json).
- Why TTM over the normalized median ($6.35/share): the FY ended 9.5 months ago and every current print is below the FY2024 year the median sits on — TTM OCF is down vs FY2025, FY2026 same-store NOI is guided negative (-1.70% to +0.10%) and Core FFO is guided down to $8.53 from $8.74 in FY2025 (search results). The TTM base is the current run rate; the median is the stale one. The median variant was computed with identical scenarios for the method range (below) and also lands in Tier D.

## OVERRIDE — capex (filing)

- **The gap:** the preliminary engine run exited 4 with `DATA_GAP:capex` — capex missing for FY2023, FY2024 and FY2025 of the last 3 under every candidate tag the engine reads, because MAA reports its real-estate capex on the cash-flow line "Payments for capital improvements", tagged us-gaap `PaymentsForCapitalImprovements`, which is not in the engine's candidate tag list (the same REIT dead end as KIM, except Kimco's line existed only under an extension tag; MAA's is a standard us-gaap tag the engine simply doesn't read).
- **The decision (bounded authority, kind "filing"):** judgment.json carries `capex_override = {value: 341224000, kind: "filing"}` — the filed FY2023 figure, which is also the median of the three filed years ($341,224,000 FY2023 / $322,372,000 FY2024 / $360,238,000 FY2025), from the FY2025 10-K Consolidated Statements of Cash Flows (filed 2026-02-06, accession 0001193125-26-041208). The engine applies the single value to every missing period (2012–2025 in the history; only 2023–2025 are in the base window). Against the true per-year figures it overstates FY2024 capex by $18,852,000 (conservative direction) and understates FY2025 capex by $19,014,000 (flatters the latest year slightly).
- **Out-of-band, acknowledged:** the engine's band anchors on the last filed value under a tag it reads ($32,855,000 — a stray partial fact, not the filer's capex line), putting the override at ~10.4x the anchor; judgment.json carries the ack_reason — there is no filed value for the real capex line under any engine-read tag, and the override value is the filer's own filed figure, not an estimate.
- **Excluded, deliberately:** acquisition and development spend ("payments to acquire real estate" and similar lines) is property M&A / growth investment presented separately by the filer; charging it as capex would double-count growth the unit count already paid for.
- **Measured impact** (key_numbers.md, on the TTM base actually used): base OE/share $8.37 without the override → $5.76 with it (-31.16%); weighted IRR 9.74% → 7.48% (-2.26pp). Unblocks tier: YES — without it the filing gap blocks scoring entirely.

## Moat: 4/10 — weak

Evidence first: fundamentals.json cannot compute the `roic_proxy` series for MAA in any recent year (the filed presentation does not split out an operating-income line the tool reads — roic_proxy and gross margin are null for 2017–2025), and filed ROE has run only ~8–11% over the last five fiscal years (fundamentals.json annual rows). There is no evidence of sustained returns well above the cost of capital, so a 7+ moat is not available; what exists is scale and execution.

FOR:
- Scale: ~105,000 units across 16 Sun Belt states — the largest apartment REIT platform, with in-house development, redevelopment and renovation capability (interior renovations earning ~25% cash-on-cash, Q2 2026 call).
- Operating platform and expense discipline: same-store opex growth held to ~80–90 bps YoY through Q2 2026 while revenue fell; record-low resident turnover of 39.6% and renewal pricing +5.2%.
- Balance-sheet strength as a competitive tool: net debt/EBITDA ~4.5x, ~6-year average maturity at a 3.9% effective rate (Q2 2026 call) — cheaper, longer capital than private landlords.
- Diversified Sun Belt footprint across primary and mid-tier markets cushions single-market supply shocks (mid-tier markets outperforming high-supply ones in 2026).

AGAINST:
- Apartments are a commodity product — Q2 2026 new-lease rates were -5.3% under Sun Belt oversupply, proving no pricing power when supply lands.
- Low tenant switching costs; leases are 12-month and residents can move to a competing new property with concessions.
- Returns are capped by replacement cost / cap-rate arbitrage — new supply is the permanent competitor.
- ROE has run only ~8–11% in recent years (fundamentals.json) and the roic_proxy series is not computable from the filed presentation — no evidence of sustained returns well above the cost of capital.
- Sun Belt concentration: the same migration markets (Austin, Phoenix, Charlotte, Nashville) took the record supply wave.

CAP = 7.2 years (moat 4): growth holds 2 years, then converges to the 2.5% terminal rate over 7.2 years.

## DCF — v5 final run (2026-10-17)

Engine 5.4.0, TTM base $5.76/share, price $116.63. Growth blend 1.48% (components: rev CAGR 5y 5.65% · rev CAGR 3y 3.03% · latest rev YoY 0.83% · OE/share CAGR 2y -4.14%; share count CAGR 0.45%, growth adj -0.45%).

**Growth sanity check (written, per the standing rule):** the default offsets would have produced starts of -10.0% / -3.5% / +1.5% / +6.5% / +13.5% — a +13.5% super-bull start is not a credible forward print for an apartment REIT (even the 2021–22 rent-spike years are in the 5y revenue CAGR of 5.65%, not at 13%), and -10% super-bear overstates any downturn MAA has filed (worst recent OE/share CAGR 2y is -4.14%). Offsets were recalibrated to starts of **-5.0 / -2.0 / +1.5 / +4.5 / +8.0%**. Against the actual prints: latest FY revenue YoY +0.83%, TTM revenue YoY +0.77% (fundamentals.json TTM), FY2026 same-store NOI guided -1.70% to +0.10% and Core FFO guided at $8.53 vs $8.74 in FY2025 (search results). The bear start (-2.0%) sits on the current NOI/FFO trajectory. The base start (+1.5%) sits above the latest NOI print for a written reason: new deliveries in MAA's markets are falling sharply from the peak (deliveries down over 60% from recent highs, sector coverage), H1 2026 absorption exceeded deliveries, and blended lease pricing had already turned positive (+0.7%) in Q2 2026 — the base case is a supply-absorption recovery, not a continuation of the trough. The bull start (+4.5%) requires that absorption to restore mid-single-digit rent growth, in line with the 5y revenue CAGR; the super-bull start (+8.0%) is a 10% tail requiring a 2021–22-style rent spike on top — stated as a tail, not a forecast. Probabilities 10/25/30/25/10; OE multipliers 0.75/0.90/1.00/1.10/1.25 (defaults, unadjusted — the scenario spread is carried by the growth starts).

| Scenario | Prob | Growth start | OE mult | IV@15 | IV@12 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -5.0% | 0.75 | $26.47 | $34.23 | 5.15% |
| Bear | 25% | -2.0% | 0.9 | $35.72 | $46.52 | 6.20% |
| Base | 30% | 1.5% | 1.0 | $45.42 | $59.63 | 7.34% |
| Bull | 25% | 4.5% | 1.1 | $56.11 | $74.15 | 8.57% |
| Super bull | 10% | 8.0% | 1.25 | $72.85 | $96.96 | 10.45% |

**Weighted result: IRR 7.48%, IV@15% $46.51** (IV@12% $61.17, IV@10% $77.46; upside at 15% -60.1%). IRR band: bear 6.20% (tier D) → bull 8.57% (tier D); scenario range 5.15% – 10.45%. Diagnostics: OE yield 4.94%, TV share @15% 17.8%, scenario spread (IV@15 super-bull / super-bear) 2.75x. Hurdle-clearing prices (weighted path): 15% at $46.51 · 20% at $33.25 · 25% at $25.88.

Method range: the normalized-median base ($6.35/share) with identical scenarios gives weighted IRR 7.99% — also Tier D. Every computed variant lands in D; even the super-bull scenario (IRR 10.45%, IV@15% $72.85) does not reach the 15% hurdle at $116.63.

## Flags — every fragility flag resolved

- **DATA_GAP:capex** (preliminary run): resolved by the filing override in the OVERRIDE section above — gap, source, per-year accuracy and measured impact are all recorded in fields (judgment.json, dcf_numbers.json overrides_applied / override_impact, key_numbers.md). data_gap_uncovered is empty in the final run.
- **STALE_FY** (latest fiscal year ended 10 months ago; 9.5 months at scoring): ttm.py was run and its legs are quoted in the Owner's earnings section — TTM OE $672,577,000 → $5.7613/share — and the TTM figure **is** the base (the --ttm pin was used), because every current print (TTM OCF down vs FY2025, FY2026 same-store NOI guided negative, Core FFO guided down) sits below the FY2024 year the median base rests on. Note the TTM stops at 2026-03-31 in EDGAR companyfacts: fundamentals.json warns the latest 10-Q (period 2026-06-30, filed 2026-07-30) is not yet in companyfacts, so the TTM legs are built from the Q1 2026 10-Q — the Q2 figures cited elsewhere here come from earnings-call coverage (search results), not from the computed outputs.
- **NI_OCF_DIVERGENCE** (net income and OCF differ by >40% in 2023, 2025): this is structural REIT arithmetic, not a one-off in the OE base. The gap is non-cash depreciation: FY2023 net income $552,806,000 plus D&A $565,857,000 lands essentially on OCF $1,137,187,000, and FY2025 net income $446,909,000 plus D&A $622,969,000 lands essentially on OCF $1,078,175,000 (financials_history.csv). FY2025 net income additionally absorbed a ~$53M antitrust (RealPage) settlement charge (search results) — a real but non-recurring drag on the net-income leg only. Owner's earnings are built from OCF, so neither effect distorts the base; no adjustment.
- **DEBT_TAGS_BLANK** (no debt tag reports for the latest fiscal year — net debt UNKNOWN to the engine, not zero): from the filing itself (EDGAR companyfacts for the FY2025 10-K balance sheet), total borrowings at 2025-12-31 are filed as NotesPayable $5,405,372,000 — secured debt $360,393,000 plus unsecured debt $5,044,979,000 — against cash of $60,258,000 (financials_history.csv). The engine's net_debt_latest is null and no leverage ratio is quoted from it; the leverage picture used here is management's: net debt/EBITDA ~4.5x, ~6-year average maturity at a 3.9% effective rate, ~$880M of combined cash/revolver capacity (Q2 2026 call, search results). This is a moderately levered but well-laddered REIT balance sheet — leverage is not the story; price vs OE is.
- **SECTOR_MODEL_MISMATCH** (Real Estate): accepted in full — the OE/capex DCF fits REITs poorly in both directions: it charges all capital-improvements capex (including renovation spend the company reports earning ~25% cash-on-cash) against OE, and it gives no credit for the underlying property asset value or for FFO/AFFO, the industry's own metrics (FY2026 Core FFO guided at $8.53/share; DPS TTM $6.075 per fundamentals.json — a ~5.2% yield at $116.63 that this model does not price). Confidence is graded **low** and the tier is read as "fails the standardized conservative OE screen," not as "the rental business loses cash." The mismatch does not rescue the hurdle math: even the kindest computed variant (median base, weighted IRR 7.99%) and even the super-bull scenario (10.45%) stay far below 15% at $116.63.
- **OVERRIDE_APPLIED:capex**: see OVERRIDE — filing gap filled for 2012–2025, never replacing a filed value (there were none under engine-read tags); measured impact recorded in key_numbers.md (base $8.37 → $5.76 on the TTM base; weighted IRR 9.74% → 7.48%).

## My thoughts / overlay

- The honest headline is the same two-lens gap as every REIT in this sweep. On the REIT lens this is a healthy credit and a decent operator: 95%+ occupancy through a record supply wave, renewal pricing +5.2%, turnover at record lows, expense growth under 1%, a maintained Core FFO guide and a growing dividend. On the owner's-earnings lens the same company converts $1,031,201,000 of TTM OCF into $5.76/share of OE because keeping ~105,000 aging apartments leasable and renovated costs ~$341M a year of capital improvements, forever — that spend is the rent roll's maintenance bill, and the sweep is right to charge it.
- What the price is actually underwriting: at $116.63 the buyer pays ~13.7x guided Core FFO and gets a ~5.2% dividend yield plus whatever rent growth the post-supply-cliff recovery delivers. That can be a fine bond-proxy return; it is not a 15% owner's-earnings return on any scenario this run computed, including the super bull.
- What would change the tier: the price, mostly — the 15% hurdle clears below ~$47 on the TTM base and the 12% discount-rate value is $61.17. On fundamentals, same-store NOI would have to inflect to sustained mid-single-digit growth with capital improvements flat; the supply data (deliveries down >60% from peak) says the setup for that exists in 2027, but it has not filed yet. Next checkpoint: Q3 2026 results on October 28, 2026 (search results).
- Confidence: **Low** (SECTOR_MODEL_MISMATCH for a REIT and a capex series the engine cannot read natively — though every computed variant lands in D, so the tier itself is robust to the data problems).

## Final verdict

**Tier D.** Quality Sun Belt apartment REIT, moat 4/10 — scale, expense discipline and a 4.5x-levered balance sheet are real, but apartments are a commodity with no pricing power against new supply (new-lease rates -5.3% in Q2 2026, same-store NOI guided negative for 2026); on a TTM owner's-earnings base of $5.76/share after charging filed capital-improvements capex, weighted IRR is 7.5% (IV@15% $46.51) at $116.63, so it clears the 15% hurdle only below ~$47 — the REIT lens (FY2026 Core FFO guided at $8.53/share, DPS TTM $6.075) is kinder than the OE lens, but neither supports 15% at this price.

## Engine 5.5 re-score (2026-10-19)

This section supersedes the figures above. Everything above it is the 2026-10-17 record, left as written, except the one pointer line under the title, which was added on 2026-10-19 and points here.

**Result: Tier D, unchanged.**

| | Old (engine 5.4.0, 2026-10-17) | New (engine 5.5.0, 2026-10-19) |
|---|---|---|
| Base OE/share | $5.7613 (TTM pin, scored on the single-value `capex_override` of $341.224M) | $5.71 (source: ttm_json, no override) |
| Scenario growth starts | -5.0 / -2.0 / 1.5 / 4.5 / 8.0% | -8.9 / -5.9 / -2.4 / 0.6 / 4.1% (base start set at the FY2026 Core FFO/share guide; see "Growth and scenario inputs") |
| Weighted IRR | 7.48% | 6.63% |
| Tier (numbers / final) | D / D | D / D |

New headline (key_numbers.md): price $116.63 (source: nasdaq_quote_api). Weighted IV @15% $39.66 · @12% $51.71 · @10% $65.05. Base-case IRR 6.50%. IRR band: bear 5.53% (tier D) → bull 7.57% (tier D). Scenario range 4.65% – 9.22%. Hurdle-clearing prices (weighted path): 15% at $39.66 · 20% at $28.70 · 25% at $22.56. Confidence **low**.

### What engine 5.5 changed for this filer

- **Capex tag (ruling 3).** Engine 5.5 adds `PaymentsForCapitalImprovements` to the capex component list in both dcf_engine.py and ttm.py. The engine now reads MAA's "Payments for capital improvements" line directly. Capex basis (key_numbers.md): FY2023 $341.2M, FY2024 $322.4M, FY2025 $360.2M. Each year comes from the single component `PaymentsForCapitalImprovements` (PP&E leg; intangibles $0.00).
  - `used_tags.capex` is now `PaymentsForCapitalImprovements` (dcf_numbers.json). The 5.4 run had named a stray `PaymentsToAcquireOtherPropertyPlantAndEquipment` fact there.
  - Every history year now carries a filed capex value. None is assumed zero.
  - As ruling 3 directs, I deleted the `capex_override` from judgment.json before the preliminary run. That run exited 0 with no data gap: `data_gap` and `data_gap_uncovered` are both empty, and so are `overrides_applied` and `override_checks`.
  - make_score dropped MAA's capex event from `_system/overrides_registry.json`, because no override is declared any more.
  - The zero-guard has nothing to act on here: no $0 candidate sits beside the filed line.
  - Development and acquisition outflows in the investing section stay excluded. The 2026-10-17 OVERRIDE section explains why: they are growth spending, not the recurring capital-improvements line.
  - `CAPEX_COVERAGE_LOW` did not fire.
- **SBC tag (ruling 6).** `AllocatedShareBasedCompensationExpense` exceeds `ShareBasedCompensation` in every year from FY2017 to FY2025, so 5.5 uses the Allocated figure (key_numbers.md):
  - FY2023: $18.3M over $15.7M (+16.6%)
  - FY2024: $17.7M over $15.8M (+12.1%)
  - FY2025: $18.3M over $16.8M (+8.7%)

  `used_tags.sbc` is now `AllocatedShareBasedCompensationExpense`. The flag is resolved under SBC_TAG_RECONCILED below.
- **Share basis and market cap (rulings 1–2).** No split fact, no divergence and no scale defect. The latest diluted count is 117,149,000 against a cover-page count of 116,384,802 dated 2026-04-27 (dcf_numbers.json `share_scale`). The market cap therefore stays price × diluted shares: $13.663B (basis: diluted_latest; price × shares), in scope under $40B (`in_scope_under_40b` true).
- **Not applicable:** no ADS ratio, no FX conversion and no override, so the USD-override branch (ruling 7) does not arise.

### How the base moved

**The final base is still the TTM pin, as on 2026-10-17.** ttm.py was re-run under 5.5. ttm.json legs:

| Leg | FY | − prior YTD | + current YTD | = TTM |
|---|---|---|---|---|
| OCF (unchanged) | $1,078,175,000 | $196,618,000 | $149,644,000 | $1,031,201,000 |
| Capex (`PaymentsForCapitalImprovements`, all three legs) | $360,238,000 | $72,636,000 | $58,369,000 | $345,971,000 |
| SBC | $18,300,000 (Allocated, reconciled leg) | $5,261,000 | $5,822,000 | $18,861,000 |

- Shares: 116,740,000 (current-YTD weighted diluted).
- TTM OE: $666,369,000 → $5.70814630803495/share (ttm.json). key_numbers.md prints this as $5.71.
- The TTM capex leg is now filed on all three legs. It replaces the prorated override.
- Why the base slipped from $5.7613 to $5.71: the filed TTM capex is a little above the old override, and the reconciled FY SBC leg is larger.

**Annual figures (key_numbers.md):**
- Latest FY OE/share is $5.97 (FY2025 OE total $699.6M); the 5.4 run had $6.15. It falls because FY2025 now carries its true $360.2M capex.
- The normalized 3-year median is $6.49; the 5.4 run had $6.35. It rises because FY2024, the year that sets it, now carries its true $322.4M capex instead of the $341.2M fill.

**Growth and scenario inputs:**
- The OE/share CAGR (2y) is -5.35% (was -4.14%).
- The growth blend stays 1.48% (g_base 1.48%). The blend is the median of four components, and the OE/share CAGR is the lowest of the four in both runs, so it does not set the median.
- **The offsets were reset on 2026-10-19, and the starts moved down.** The first 2026-10-19 pass kept the 2026-10-17 offsets. Because g_base did not change, those offsets gave the same starts as on 2026-10-17, so the base start stayed at +1.5%. That is above the company's own FY2026 guidance, which this analysis quotes:
  - Core FFO is guided at $8.41–$8.65 a share, midpoint $8.53, against $8.74 for FY2025 (2026-10-17 section, search results). That is a decline of 2.4%.
  - Same-store NOI is guided at -1.70% to +0.10%.
  - The guidance has not moved since the Q2 2026 release (search results). Q3 2026 Core FFO is guided at $2.04–$2.16.
- AGENTS.md does not allow a base start above guidance that the analysis quotes. The 2026-10-17 reason for +1.5% (a supply-absorption recovery) is a forecast of a recovery, not the company's guide. The final pass therefore puts the base start on the Core FFO/share guide, -2.4%. That is the company's own per-share earnings guide, the nearest match to OE/share, and the lower of the two guides; it also sits below the bottom of the same-store NOI range.
  - Base offset: -0.0388. g_base 1.48% minus 3.88 points gives a start of -2.4%.
  - The other four offsets move by the same -0.0388, so the 2026-10-17 spread between scenarios is unchanged.
  - Offsets: -0.1036 / -0.0736 / -0.0388 / -0.0086 / 0.0264 (dcf_numbers.json `inputs.offsets`). Starts: -8.9 / -5.9 / -2.4 / 0.6 / 4.1% (key_numbers.md).
- **Sanity check of each start against the prints** (key_numbers.md: latest revenue YoY 0.83%, revenue CAGR 3y 3.03% and 5y 5.65%, OE/share CAGR 2y -5.35%, TTM base $5.71 below the latest FY's $5.97):
  - **Super bear, -8.9% (10%).** A tail case: a second supply wave or a recession pushes per-share OE down faster than the 2-year rate of -5.35%. It sits above the engine's -10% floor on starts.
  - **Bear, -5.9% (25%).** The current per-share decline continues: about the filed OE/share CAGR (2y) of -5.35%.
  - **Base, -2.4% (30%).** The Core FFO/share guide. It is above the per-share OE decline and below the same-store NOI range.
  - **Bull, +0.6% (25%).** This is below the latest revenue print (+0.83%). Reason: per-share OE has been falling while revenue grew (OE/share CAGR 2y -5.35% against revenue CAGR 3y 3.03%). Operating cash flow fell from $1,137,187,000 in FY2023 to $1,078,175,000 in FY2025 (financials_history.csv) while capital improvements rose from $341.2M to $360.2M (key_numbers.md). A bull that turns per-share OE from decline to slight growth is already above every per-share print and both guides. The 2026-10-17 recovery thesis (deliveries falling, absorption ahead of deliveries, blended lease pricing positive in Q2 2026) now sits here.
  - **Super bull, +4.1% (10%).** The recovery brings back mid-single-digit rent growth. It is still below the 5y revenue CAGR (5.65%), which includes the 2021–22 rent spike.
- Carried unchanged from judgment.json and the 2026-10-17 run: moat 4 (CAP 7.2 yrs, terminal growth 2.50%), probabilities 10/25/30/25/10, OE multipliers 0.75/0.9/1.0/1.1/1.25. Only the offsets changed. The engine was re-run with the recorded inputs and `--ttm`, then make_score and reprice. The re-run left financials_history.csv and ttm.json unchanged, so the base ($5.71) and every annual figure above stand.
- Effect: the weighted IRR falls to 6.63% and the tier stays D. The first 2026-10-19 pass, on the 2026-10-17 starts, was also Tier D.

### Scenarios — final run (key_numbers.md)

| Scenario | Prob | Growth start | OE mult | IV@15 | IV@12 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -8.9% | 0.75 | $22.51 | $28.82 | 4.65% |
| Bear | 25% | -5.9% | 0.9 | $30.40 | $39.23 | 5.53% |
| Base | 30% | -2.4% | 1.0 | $38.71 | $50.38 | 6.50% |
| Bull | 25% | 0.6% | 1.1 | $47.88 | $62.74 | 7.57% |
| Super bull | 10% | 4.1% | 1.25 | $62.26 | $82.21 | 9.22% |

**Weighted result: IRR 6.63%, IV@15% $39.66.** Upside vs price: @15% -66.0%, @12% -55.7%.

Diagnostics: OE yield 4.89% · TV share @15% 17.0% · scenario spread (IV@15 super-bull / super-bear) 2.77x · net debt / normalized OE — (not computed) · months since FY end 9.6.

### Flags — every flag in the final run, resolved

- **STALE_FY** ("latest fiscal year ended 10 months ago"; months since FY end 9.6). **Resolution:** ttm.py was re-run and the final pass used `--ttm`, so `base_source` is ttm_json.
  - The TTM base ($5.71) sits below both the latest FY ($5.97) and the median ($6.49). It is the current run rate and the conservative end. The current-YTD OCF leg ($149,644,000) is below the prior-YTD leg ($196,618,000).
  - The TTM still stops at 2026-03-31. The Q2 2026 10-Q (period 2026-06-30, filed 2026-07-30) is not yet in EDGAR companyfacts; fundamentals.py and statements.py print the same warning. The Q3 2026 results noted in the section above are the next checkpoint.
- **NI_OCF_DIVERGENCE** (2023, 2025). **Resolution:** unchanged from the 2026-10-17 resolution above. The gap is non-cash real-estate depreciation, plus the RealPage antitrust settlement charge in FY2025 net income. Search results: a $53M class settlement paid in two installments, plus a $1.2M D.C. settlement in September 2026. Neither enters the OCF-based OE. Engine 5.5 changes neither leg.
- **DEBT_TAGS_BLANK.** **Resolution:** the balance-sheet statement in the 2026-10-17 resolution above stands. It quotes the filed NotesPayable total from the FY2025 10-K balance sheet against the filed cash balance.
  - 5.5 does not change the debt tags, so `net_debt_latest` is still null and net debt / normalized OE prints "—". HIGH_NET_DEBT was therefore not tested.
  - The ratio the engine would have computed, worked by hand from filed figures:
    - Borrowings: us-gaap `NotesPayable` $5,405,372,000 at 2025-12-31. That is secured debt $360,393,000 plus unsecured debt $5,044,979,000. Source: the FY2025 10-K balance sheet (accession 0001193125-26-041208, filed 2026-02-06), checked against EDGAR companyfacts on 2026-10-19.
    - Cash: $60,258,000 (financials_history.csv FY2025 `cash`, tag `CashAndCashEquivalentsAtCarryingValue`).
    - Net debt: $5,345,114,000.
    - Denominator: the engine's normalized OE total is base OE/share × latest diluted shares (dcf_numbers.json). On the TTM base used, $5.70814630803495 × 117,149,000 = $668,703,632, so net debt is **7.99x**. On the 3-year median base, $6.492943755566213 × 117,149,000 = $760,641,868, so it is **7.03x**.
    - Both figures are well above the engine's 3x HIGH_NET_DEBT line, so the flag would have fired had the engine read the borrowings.
  - Why the engine misses them: its debt tags read `NotesPayableCurrent` and `LongTermNotesPayable` but not the total `NotesPayable` tag MAA files. That needs a code change, outside this re-score.
  - Leverage does not enter the per-share DCF, which runs on OCF after interest, so the tier does not depend on it. HIGH_NET_DEBT asks for the bear cases to be stressed. The final bear and super-bear starts (-5.9% and -8.9%) already do that, and both cases are D (5.53% and 4.65%). Management's own leverage figure is ~4.5x net debt/EBITDA (section above).
- **SBC_TAG_RECONCILED** (new in 5.5; FY2017–FY2025, the Allocated figure used). **Resolution:**
  - The differences in the last three FY are +16.6%, +12.1% and +8.7%. They exceed 1%, so this is not tag rounding.
  - Against the cash-flow statement: statements.json builds its cash-flow stock-compensation addback row from the `ShareBasedCompensation` tag, and its FY2023–25 values are the Share figures in the flag ($15.7M / $15.8M / $16.8M). At MAA the Share tag is the full cash-flow addback, not a note-level slice as at JLL. The Allocated figure ($18.3M / $17.7M / $18.3M, rounded to $0.1M) is the larger note-level total.
  - The gap is stock compensation recognized in the note but not added back as non-cash expense on the cash-flow statement. Its makeup cannot be verified from the computed outputs or from my search, which did not surface the note. One example would be award cost capitalized into development or renovation projects.
  - The direction is conservative: the base charges the larger figure. Capitalized stock compensation would otherwise escape OE altogether, because it is not a cash capex payment.
  - TTM: ttm.json `sbc_reconciled_legs` shows only the FY leg reconciled (Allocated 18,300,000 over Share 16,839,000, +8.7%). The two 10-Q legs stay on `ShareBasedCompensation` (prior YTD $5,261,000, current YTD $5,822,000), so TTM SBC of $18,861,000 mixes tags across legs, as ttm.json's warning says. `sbc_reconciliation_withdrawn_legs` is empty: the floor did not bind.
  - statements.json's owner's-earnings row differs from the figure of record. That row subtracts the Share addback, so FY2023–25 read $780,264,000 / $760,131,000 / $701,098,000. financials_history.csv `oe_conservative` subtracts the Allocated figure and reads $777,663,000 / $758,220,000 / $699,637,000 (key_numbers.md latest FY OE total $699.6M). Each year's gap equals that year's SBC difference in the flag. For FY2025 it is 18,300,000 − 16,839,000 = $1,461,000. The company page's statements table will therefore show a slightly higher OE than the engine. The CSV / key_numbers.md figure is the one of record, and it is the one the base and tier use.
  - The whole reconciliation is a few million dollars a year against TTM OCF of $1,031,201,000. It cannot carry a weighted IRR of 6.63% across the 10% Tier C line.
- **SECTOR_MODEL_MISMATCH** (Real Estate). **Resolution:** accepted as before. Confidence is **low**, and the name ranks under sector misfits.
  - The 2026-10-15 policy sizes the final tier one notch below the numbers tier. There is no notch below D: F is a different verdict, meaning no positive normalized OE, and MAA's normalized median is $6.49 with OE-positive years 5/5. So `tier_override` stays null and the final tier is D.
  - The REIT lens in the section above (FY2026 Core FFO guide, dividend) is kinder than the OE lens. Even so, every scenario IRR (4.65% – 9.22%) is below 15% at $116.63.
- **No longer raised:**
  - DATA_GAP:capex and OVERRIDE_APPLIED:capex: the override is removed and the capex is now filed.
  - WIDE_SCENARIO_SPREAD and TIER_BAND appeared only in the preliminary 5.5 run, on the median base with default offsets. They do not recur on the final inputs: the scenario spread is 2.77x, and the bear and bull cases are both tier D.
  - No 5.5 share-basis flag fired, and neither did `CAPEX_COVERAGE_LOW` or `OVERRIDE_SUPERSEDED_BY_FILED_TAG:capex`.

### Why the tier is D

- **Numbers:** weighted IRR 6.63% is in the D band (< 10%). Tier by numbers is D, and the bear (5.53%) and bull (7.57%) cases are both D.
- **No scenario clears 10%:** the super bull gives 9.22% at a 10% probability. No scenario comes near 15%.
- **Robust to the base and the starts:** the preliminary 5.5 run on the normalized median base ($6.49) also printed Tier D by numbers. So did the first 2026-10-19 pass, on the 2026-10-17 starts.
- **Final tier:** D. No override, for the sector-misfit reason above.
- **Hurdle price:** 15% clears at $39.66, against $116.63.
- **Alerts:** `alert_eligible` and `exit_alert_eligible` are false (sector misfit).
- **Net effect of 5.5 and the reset:** the base is better grounded, built from filed per-year capex instead of a single-value fill, and the base start now sits at the company's guide. The verdict does not change.

### Data and enrichment (2026-10-19)

- All six enrichment steps ran without failure, in order: fundamentals.py, prices.py, segments.py, statements.py, profile.py, reprice.py.
- fundamentals.json and statements.json both stop at 2026-03-31, because the Q2 2026 10-Q is not yet in companyfacts.
- fundamentals.json's capex and OE columns are still blank. fundamentals.py's own capex tag list does not read `PaymentsForCapitalImprovements` (its `tags_used.capex` names `PaymentsToAcquireOtherPropertyPlantAndEquipment`), so its capex-derived fields are not the engine's. Fixing that needs a change to fundamentals.py, which is outside this re-score. Until then, the company page's capex, OE and FCF columns from fundamentals.json stay blank for MAA.
- statements.json's cash-flow capex row does read `PaymentsForCapitalImprovements` and agrees with the engine's FY2023–25 capex.
- The figures of record are financials_history.csv, dcf_numbers.json, ttm.json and key_numbers.md.

Sources (2026-10-19 searches):
- MarketBeat, "Mid-America Apartment Communities updates Q3 2026 earnings guidance" (2026-07-29): https://www.marketbeat.com/instant-alerts/mid-america-apartment-communities-nysemaa-updates-q3-2026-earnings-guidance-2026-07-29/
- Panabee, Q2 2026 earnings coverage: https://www.panabee.com/news/mid-america-apartment-communities-earnings-q2-2026
- Multifamily Dive, RealPage settlement: https://www.multifamilydive.com/news/maa-settles-realpage-lawsuit/810899/
- Cohen Milstein, D.C. RealPage settlement: https://www.cohenmilstein.com/dc-inks-9-3m-deals-with-2-more-landlords-in-realpage-case/
- MAA Q2 2026 10-Q on EDGAR: https://www.sec.gov/Archives/edgar/data/0000912595/000119312526326153/maa-20260630.htm
