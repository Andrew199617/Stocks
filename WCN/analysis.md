# WCN — Waste Connections, Inc.
v5 run, 2026-10-14 (supersedes the v4 analysis of 2026-10-13; the v4 result was essentially identical — see method range). In scope: market cap $39.643B at $153.67 (nasdaq_quote_api, dcf_numbers.json) — just under the $40B cutoff.

All figures below are copied from dcf_numbers.json, ttm.json, financials_history.csv, or cited search results — none are recomputed.

## What it is
North America's third-largest solid waste company (after Waste Management and Republic Services): non-hazardous waste collection, transfer and disposal (including by rail), recycling/resource recovery and renewable fuels (landfill-gas RNG), serving ~9 million residential/commercial/industrial customers across 46 U.S. states and 6 Canadian provinces, mostly in exclusive and secondary markets. Plus E&P (oilfield) waste treatment/disposal and Pacific Northwest intermodal. Asset-heavy and acquisition-driven: growth = core pricing + tuck-in M&A, with volumes currently slightly negative. Note on classification: the Nasdaq screener buckets the company as Utilities / Environmental Services (universe.csv), and public classifications put it in Industrials / Commercial Services & Supplies — it is not a rate-regulated utility (see SECTOR_MODEL_MISMATCH below).

## Owner's earnings
FY2025 (SEC 10-K via EDGAR, from financials_history.csv):
- OCF $2,414,069,000; capex (PaymentsToAcquirePropertyPlantAndEquipment) $1,179,228,000; SBC $79,448,000 (a real cost, but small relative to OCF; share count essentially flat for years and now falling on buybacks)
- **Conservative owner's earnings FY2025: $1,155,393,000 = $4.48/share (latest FY OE/share, dcf_numbers.json)**
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $1,273,813,000 (financials_history.csv) — higher than the conservative figure because total capex includes growth/RNG/land spend above D&A; the conservative figure is the right base for a hurdle test.
- Engine normalized base (median of last 3 FY OE/share): $4.35/share. OE positive 5/5 of the last 5 years.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math; ttm.json):**
- OCF: FY $2,414,069,000 − prior YTD (2025-01-01 to 2025-06-30) $1,179,741,000 + current YTD (2026-01-01 to 2026-06-30) $1,278,886,000 = **TTM $2,513,214,000**
- Capex: FY $1,179,228,000 − prior YTD $497,765,000 + current YTD $598,949,000 = **TTM $1,280,412,000**
- SBC: FY $79,448,000 − prior YTD $41,956,000 + current YTD $41,539,000 = **TTM $79,031,000**
- Shares (current-YTD weighted diluted): **254,860,729**
- **TTM OE total $1,153,771,000 → base OE/share $4.53** (dcf_numbers.json base_oe_per_share $4.5271, base_source: ttm_json)
- TTM is essentially flat vs FY2025, because the H1 2026 capex increase absorbed the pricing gains. That flatness is the story: Q2 2026 revenue +6.4% YoY (search: Zacks/Waste360 Q2 2026 reports), OE/share roughly flat TTM.
- Cross-check vs guidance (search results, Q2 2026 reports): raised FY2026 outlook — revenue $10.02–10.05B, net income $1.169–1.173B, adjusted EBITDA $3.33–3.34B, capex approximately $1.25B, OCF $2.63–2.68B — is H2-weighted and embeds Chiquita closure outlays guided at $100–150M inside 2026 OCF/free cash flow (search: Q4 2025 call summary). Even a higher guided base would not change the verdict at this price (see method range).

## Moat: 7/10 — strong
Justification: Permitted landfill airspace is scarce/irreplaceable, route density in exclusive/secondary markets, internalization rising, proven pricing power (core price +5.6% in Q2 2026 per search results; +6.5% FY2025 per the prior pass) and industry-leading ~33% adjusted EBITDA margin, long municipal/franchise contracts — against larger WM/Republic bidders, rebid risk, no network effects, negative unit volumes, commodity/E&P cyclicality, and landfill closure/environmental liabilities (Chiquita Canyon).
- FOR: Permitted landfill airspace is a scarce, effectively irreplaceable asset — new landfill permits are nearly impossible to obtain, and WCN keeps internalizing disposal, capturing the disposal margin itself instead of paying WM/Republic.
- FOR: Route density + exclusive/secondary-market positioning — dense collection routes feeding owned transfer/disposal is a local cost advantage that compounds with every tuck-in.
- FOR: Proven pricing power through cycles — core price +5.6% in Q2 2026, held above cost inflation; industry-leading adjusted EBITDA margin (guided 33.2–33.3% for FY2026) is the receipt.
- FOR: Long-duration municipal/franchise contracts give revenue visibility rivals cannot bid away overnight.
- FOR: Disciplined M&A machine in a fragmented industry — decades of accretive tuck-ins, and the balance sheet to keep doing them.
- AGAINST: No network effects and no lock-in beyond contract terms — contracts rebid, and WM and Republic are larger, equally disciplined bidders for the same assets and routes.
- AGAINST: The moat asset is also the liability — landfills carry closure/post-closure and environmental obligations (Chiquita Canyon) that can convert a scarce asset into open-ended cost.
- AGAINST: Volumes are not growing (solid waste unit volumes −1.9% in Q2 2026 per search results); growth is price + M&A, both of which have limits.
- AGAINST: Recycled commodity prices and E&P waste volumes are cyclical drags management cannot control.
- AGAINST: Capital intensity is real and rising (RNG build-out, land purchases) — OE conversion of EBITDA is low.
- A 7 gives CAP = 11.1 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 11.1 years, 15-year projection.

## DCF — v5 final run (2026-10-14)
Base OE $4.53/share (TTM, ttm_json), moat 7, probabilities at defaults 10/25/30/25/10, offsets at defaults −12/−5/0/+5/+12pp, OE multipliers 0.75/0.90/1.00/1.10/1.25. Engine growth blend 7.81% → g_base 7.82% (rev CAGR 5y 11.69%, 3y 9.49%, latest rev YoY +6.14%, OE/share CAGR 2y +1.49%; share-count CAGR −0.01%, adjustment +0.01pp). The blend is generous vs OE history, deliberately kept: pricing + buyback shrink support OE/share growing faster than revenue near term.
Price: **$153.67** — OE yield 2.95% (diagnostics).

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | −4.2% | 0.75 | Volume recession, commodity trough, Chiquita cash costs escalate, M&A halts | $20.36 | 3.95% |
| Bear | 25% | 2.8% | 0.90 | Pricing fades toward inflation, capex stays elevated, no M&A contribution | $33.92 | 5.27% |
| Base | 30% | 7.8% | 1.00 | Core price ~5.5% + tuck-ins + buyback shrink; RNG capex rolls off after 2026 | $47.75 | 6.64% |
| Bull | 25% | 12.8% | 1.10 | Guided FY2026 results delivered and compounded; commodity recovery; outsized M&A year | $66.61 | 8.42% |
| Super bull | 10% | 19.8% | 1.25 | Everything above plus margin expansion and sustained double-digit OE growth | $105.57 | 11.67% |

- **Probability-weighted: IV@15% $52.05 (−66.1% vs price), IV@12% $70.46, IV@10% $91.19, weighted IRR 7.11%, base-case IRR 6.64%**
- **Tier by numbers: D.** Diagnostics (dcf_numbers.json): OE yield 2.95%, terminal value 20.8% of IV@15%, scenario spread 5.18x, net debt not returned by the engine (net_debt_latest: null — see flags), 9.4 months since FY end.

**Sanity check vs actual prints:** Q2 2026 revenue +6.4% YoY, core price +5.6%, FY2026 guided revenue +~6% (guidance range above). Base start +7.8% sits modestly above revenue prints — justified only by OE leverage (buyback shrink + RNG capex roll-off) and written here for that reason. Bull +12.8% and super bull +19.8% sit above current revenue prints; super bull is a 10% tail (guide delivered + commodity/M&A upside stacked), not a forecast. Super bear/bear starts are below prints by construction (recession/closure-cost cases).

## Flags — every fragility flag resolved
- **STALE_FY** (latest fiscal year ended 9 months ago; diagnostics: 9.4 months since FY end): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, quoted in full above (FY, prior YTD, current YTD for OCF/capex/SBC/shares). TTM OE/share $4.53 vs the $4.35 median and $4.48 latest FY — staleness was not hiding growth; it was hiding a capex increase.
- **NI_OCF_DIVERGENCE** (net income and operating cash flow differ by >40% in 2023, 2024, 2025): resolved — structural, not a one-off distorting the OE base. D&A in financials_history.csv is $1,003,211,000 / $1,163,769,000 / $1,232,106,000 in 2023/24/25 against net income of $762,800,000 / $617,573,000 / $1,076,557,000: a landfill/truck fleet this size mechanically makes OCF roughly double NI. The 2024 gap was widened by large non-cash Chiquita Canyon closure/impairment charges that depressed net income while OCF held (identified in the prior pass's 10-K review). Because the conservative OE base is built from OCF − capex − SBC, these non-cash charges do not inflate it; if anything the recurring cadence of closure charges argues the base is not understated.
- **SECTOR_MODEL_MISMATCH** (Utilities sector — OE/capex DCF fits utilities names poorly; grade confidence low): the flag fires because the screener/universe classification is Utilities / Environmental Services. The business is not a rate-regulated utility — it is contracted waste services with demonstrated pricing power, so the OE/capex DCF fits materially better than for a regulated utility — but per the sweep rule confidence is graded **low** and the tier is treated as soft. Softness does not change the outcome here: even the super-bull IV is below the price (see WIDE_SCENARIO_SPREAD).
- **WIDE_SCENARIO_SPREAD** (super-bull IV is 5.2x super-bear IV): real but mechanical at a 2.95% OE yield — when the base cash flow is this small vs price, plausible growth paths fan out enormously in IV terms. Confidence is not high (graded low, above). Critically, the spread does not straddle the hurdle — even the super-bull IV@15% ($105.57) is below the $153.67 price, so the spread creates no tier ambiguity.
- **Balance-sheet note (no flag fired — engine output recorded here):** the engine returned net_debt_latest as null, so no net-debt figure or net-debt/OE ratio is quoted in this analysis (per the hard rule, it is stated in words instead of being calculated). The OE stream here is an equity cash flow (OCF is after interest), so debt would not be subtracted again in any case; leverage remains a qualitative risk overlay.

## Thoughts / overlay
- This is a genuinely good business at a price that pays for perfection: pricing power, scarce landfills, disciplined M&A, industry-leading margins — and a 2.95% owner's-earnings yield. At $153.67 the market is capitalizing WCN like a compounder that will grow OE at double digits for a decade; its own TTM OE is flat and its OE/share CAGR 2y is 1.49%.
- **Method range:** preliminary v5 run (median base $4.35, moat 5) → weighted IV@15% $47.58, weighted IRR 6.61%. Final v5 (TTM base $4.53, moat 7) → $52.05, 7.11%. The v4 pass landed at the same $52.05 / 7.1%. Every defensible input set lands in D; there is no tier ambiguity to size around.
- Red flags, honestly sized: Chiquita Canyon is the big one — closed at the start of 2025 after an elevated-temperature event, ongoing mitigation/cover orders, guided closure outlays of $100–150M inside 2026, many resident lawsuits, and in June 2026 a WCN subsidiary sued Los Angeles County seeking at least $825M over the forced closure (search results). It has not broken the cash machine (OCF grew through it), but the tail is unquantifiable and it is the template for landfill-liability risk across the asset base. Lesser flags: unit volumes negative, recycled commodity values weak, fuel-cost spikes (Q2 2026 margin pressure), acquisition-price discipline as the obvious growth lever gets more competitive.
- SBC/dilution: clean. SBC TTM $79,031,000 (ttm.json), share count now shrinking on buybacks (search: 2,057,386 shares repurchased April 1–July 22, 2026) — buybacks at this multiple are, however, a questionable use of that cash.
- **Hurdle math:** the price that clears 15% on the weighted case is **$52.05**; with a 20% margin of safety, **~$42**. Even the super-bull case only justifies $105.57. The gap is not a close call.

## Final verdict
- **Final tier: D** (weighted IRR 7.11%; tier = tier_by_numbers, no override)
- Confidence: **Low** (per the SECTOR_MODEL_MISMATCH rule — screener Utilities bucket — and the 5.18x scenario spread; the direction itself is not in doubt, as no defensible method clears even 10% weighted)
- One-liner: Strong-moat (7/10) waste compounder with real pricing power, but at $153.67 (TTM owner's earnings of $4.53/share, 2.95% yield) it yields a 7.11% weighted IRR — clears the 15% hurdle only at ~$52 (~$42 with a margin of safety); even the super-bull case ($105.57) is below today's price.
