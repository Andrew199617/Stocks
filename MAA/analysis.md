# MAA — Mid-America Apartment Communities, Inc.

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
