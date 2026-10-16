# MKL — Markel Group Inc.
v5 run, 2026-10-15. Market cap $23.083B at $1,825.00 (key_numbers.md, nasdaq_quote_api) — in scope under $40B. Finance / Property-Casualty Insurance.

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.py output (ttm.json), or financials_history.csv — none are recomputed. Research figures from web search are attributed where used.

## What it is
A holding company built around specialty insurance. The cornerstone business, Markel Insurance, writes specialized / hard-to-place property-casualty risks not typically available in the standard market; the insurance operation generates and holds the capital that supports the rest of the group. Around it sit majority-owned non-insurance businesses (Markel Ventures — industrial, consumer and other operating companies, from bakery equipment to ornamental plants) and a public equity portfolio held primarily inside the insurance operations. Management's own framing in the FY2025 10-K is a three-engine compounding system: underwriting, investments, and owned businesses, with capital redeployed between them, into acquisitions, and into buybacks.

Latest reported quarter (Q2 2026, per web search of the earnings reports): total operating revenues flat year-on-year for the first half, Markel Insurance adjusted operating income up with a 93% combined ratio in Q2, offset by a Financial segment adjusted operating loss that included a $205 million reserve charge tied to a State National collateral shortfall, and consolidated adjusted operating income down year-on-year. Share repurchases continued in the quarter.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $2,761,256,000; capex $206,894,000; SBC $54,982,000 — by filing override, see OVERRIDE below.
- **Conservative owner's earnings FY2025: $2,499,380,000 = $197.61/share** (key_numbers.md: latest FY OE/share $197.61, latest FY OE total $2.499B)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $2,248,034,000 (financials_history.csv) — same ballpark as the conservative figure. For an insurer this second definition is the weaker one: ΔNWC here is dominated by insurance reserve / reinsurance-recoverable swings, not ordinary working capital, which is one reason confidence is low (see SECTOR_MODEL_MISMATCH).
- OE positive 5 of the last 5 fiscal years (key_numbers.md). Net debt $339.1M (key_numbers.md); net debt / normalized OE 0.16x — the holding-company balance sheet itself is not leveraged in this engine's measure, which excludes the insurance float and reserves that are the real liabilities of the business. Do not read 0.16x as "unlevered insurer."

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $2,761,256,000 − prior YTD $880,588,000 + current YTD $444,781,000 = **TTM $2,325,449,000**
- Capex: FY $206,894,000 − prior YTD $91,353,000 + current YTD $91,592,000 = **TTM $207,133,000**
- SBC: **TTM $54,982,000**, all three legs filled by the override, prorated by days (ttm.json overrides_used)
- Shares (current-YTD weighted diluted): **12,631,000**
- **TTM OE total $2,063,334,000 → base OE/share $163.35** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $184.87/share — higher than the TTM base, because TTM OCF fell: current-YTD OCF ($444,781,000) is roughly half the prior-YTD figure ($880,588,000) on the ttm.py inputs above. The TTM base is used anyway: it is the current, filing-derived cash run-rate, it already absorbs the H1 2026 reserve-charge period, and using the higher median after a halving of YTD OCF would be picking the flattering base. The method range this creates is documented under Thoughts.

## OVERRIDE — SBC (filing, unblocks tier)
- **The gap:** the preliminary engine run exited 4 with `DATA_GAP:sbc` — no SBC fact for FY2023, FY2024 or FY2025 under ShareBasedCompensation or AllocatedShareBasedCompensationExpense (companyfacts carries no such fact after FY2019, and the FY2025 10-K Consolidated Statements of Cash Flows lists no share-based compensation addback line). No tier was emitted, correctly.
- **The decision (bounded worker authority, kind "filing"):** judgment.json carries `sbc_override = {value: 54982000, kind: "filing", source: "Form 10-K for fiscal year ended December 31, 2025 (filed 2026-02-26), Consolidated Statements of Changes in Equity: 'Equity awards expensed' $54,982 thousand in 2025, $53,302 thousand in 2024 and $35,787 thousand in 2023 …"}`. That equity-statement line is the filer's own reported cost of its equity awards — the same economic item the missing cash-flow tag would have carried.
- **Out-of-band acknowledgement:** the engine flags the override out of band only because there is no filed value at all to anchor the 0.1×–10× band (last_filed_value null). judgment.json carries an `ack_reason` stating exactly that; the value is a printed filing figure, not an unanchored estimate.
- **Measured impact (key_numbers.md, on the TTM base actually used):** base OE/share $167.71 (no override) → $163.35 (with override), −2.60%; weighted IRR 13.22% → 12.95% (−0.27pp). Unblocks tier: YES — without it there is no tier at all. The engine applies the single FY2025 value to every missing period; the true series ($35.787M / $53.302M / $54.982M) means the earlier years are overstated, i.e. the base errs conservative.

## Moat: 6/10 — moderate, one notch above plain P&C
Justification: specialty-insurance-led conglomerate with disciplined niche underwriting, conservative reserving, permanent float funding equities and Markel Ventures, and a decades-long compounding culture — capped at 6 because the core product has no switching costs or network effect, pricing is cyclical, and earnings are driven by investment markets and reserve estimates.
- FOR: Specialty underwriting niche — hard-to-place risks (equine, museums, camps, specialty casualty) with less direct competition and a long disciplined record; Q2 2026 Markel Insurance combined ratio 93% (web search, earnings reports).
- FOR: Permanent-capital three-engine model — insurance float funds a public equity portfolio and Markel Ventures' majority-owned businesses, diversifying cash flow beyond underwriting.
- FOR: Conservative reserving and low leverage culture — reserves set to be more likely redundant than deficient per the FY2025 10-K; net debt $339,106,000 in dcf_numbers.json.
- FOR: Buyback and capital discipline — share count shrinking 2.3%/yr in dcf_numbers.json, with repurchases funded from earnings.
- AGAINST: Core insurance product has no switching costs or network effect — specialty cover is re-bid at renewal and pricing is cyclical across P&C.
- AGAINST: Earnings and OCF are hostage to investment markets and reserve estimates — net investment gains were $1,076,081,000 in FY2025 in the 10-K income statement, and H1 2026 carried a $205 million State National reserve charge (web search).
- AGAINST: Reserve and legacy risk is recurring, not theoretical — CATCo run-off, State National collateral shortfall, social inflation in US casualty.
- AGAINST: Conglomerate complexity and key-person capital allocation — the investment edge and Ventures deal flow are people and reputation, not a structural barrier.
- A 6 gives CAP = 9.8 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 9.8 years, 15-year projection.

## DCF — v5 final run (2026-10-15)
**Growth recalibration (written reason — the central judgment of this run):** the engine's blended growth is 21.23% and g_base 23.58% (key_numbers.md), built from rev CAGR 5y 37.75% and rev CAGR 3y 43.61%. Those two components are tagging artifacts, not growth — see BASIS_BREAK_SUSPECT below. The components that describe the actual business are latest rev YoY 4.72% and OE/share CAGR 2y 3.39% (key_numbers.md), and H1 2026 operating revenues were flat year-on-year (web search). The preliminary default run on the unadjusted blend printed a Tier S (weighted IRR above 25%) — a fake S of exactly the kind this sweep's rules exist to catch. Scenario starts were therefore set via offsets (−0.2558 / −0.2258 / −0.1858 / −0.1458 / −0.1058 vs g_base) to −2 / +1 / **+5** / +9 / +13%. Sanity check against prints: the base start (5.0%) sits essentially on the latest FY revenue print (4.72%); the bull start (9.0%) and super-bull start (13.0%) are above anything the consolidated business has recently printed on a like-for-like basis — that is deliberate, they are the bull cases, and they are weighted 20% and 10%. No start needs a deceleration excuse: even the super-bull start is far below the engine's artifact-driven 35.58% default. Probabilities 15/25/30/20/10 (super-bear weighted above default for reserve/investment volatility); OE multipliers are the defaults 0.75/0.90/1.00/1.10/1.25. Price $1,825.00.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | -2.0% | 0.75 | Reserve charges repeat, equity portfolio drags, underwriting softens | $822.21 | 7.91% |
| Bear | 25% | 1.0% | 0.90 | Flat premiums, mid-single investment income, no compounding engine traction | $1,127.49 | 10.16% |
| Base | 30% | 5.0% | 1.00 | Current like-for-like trajectory: ~5% revenue/OE growth fading over the CAP | $1,496.91 | 12.81% |
| Bull | 20% | 9.0% | 1.10 | Insurance turnaround holds (93% combined), Ventures and investment income compound | $1,967.24 | 15.90% |
| Super bull | 10% | 13.0% | 1.25 | Full mini-Berkshire compounding reasserts across all three engines | $2,669.66 | 19.99% |

- **Probability-weighted: IV@15% $1,514.69 (−17.0% vs price), IV@12% $2,015.36 (+10.4%), IV@10% $2,574.44, weighted IRR 12.95%, base-case IRR 12.81%**
- **Tier by numbers: C.** Diagnostics (key_numbers.md): OE yield 8.95%, terminal value 18.9% of IV@15%, scenario spread 3.25x, net debt 0.16x normalized OE, 9.5 months since FY end.

## Flags — every fragility flag resolved
- **DATA_GAP:sbc** (preliminary run): resolved by the filing override — see OVERRIDE. Measured impact and unblocks-tier status are in key_numbers.md and score.json.
- **OVERRIDE_APPLIED:sbc**: same — gap, decision, source, ack_reason and measured impact are all recorded in fields (judgment.json, dcf_numbers.json overrides_applied, overrides_registry.json), not just here.
- **STALE_FY** (FY ended 9.5 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, with all inputs quoted above. Note the TTM base ($163.35) is *below* the median base ($184.87), so resolving staleness lowered the verdict, not raised it.
- **BASIS_BREAK_SUSPECT**: a tagging break, not a business break. The engine's revenue series (financials_history.csv) runs $5,236,521,000 in FY2022 and $14,279,576,000 in FY2023 — the pre-2023 figure is only the contract-revenue component, while FY2023 onward is total operating revenues as presented in the FY2025 10-K income statement ($14,279,576,000 / $14,813,544,000 / $15,513,233,000 for 2023/2024/2025). No acquisition or divestiture explains a near-tripling; the 5y/3y revenue CAGRs that straddle 2022→2023 are therefore meaningless, which is why growth was recalibrated onto the components that do not straddle the break (latest YoY, OE/share CAGR) in the DCF section above.
- **BUYBACK_TAILWIND** (share count −2.34%/yr, key_numbers.md): already credited via the +2.34% growth adjustment in the blend — and note the recalibrated scenario starts were set *after* that credit, as absolute starts, so the buyback is not double-counted in the verdict; it is one reason the base start can sit at the revenue print rather than below it.
- **SECTOR_MODEL_MISMATCH** (Finance): real and unresolved by design. An insurer's "operating cash flow" includes premium float and reserve movements, its capex is trivial next to its investment portfolio, and book value / combined ratio — not OE/share — are the industry's native valuation language. Confidence is graded **low**, the tier is soft, and the verdict below is sized accordingly. This is a screen result, not an insurance valuation.

## My thoughts / overlay
- The honest headline is the method range, verified with variant runs on 2026-10-15. On the engine's unadjusted blended growth the preliminary run printed Tier S — rejected as a tagging artifact (above). With the recalibrated growth but the median base ($184.87) instead of the TTM base, a variant run printed weighted IRR 14.27% and IV@15% $1,714.20 — still Tier C, at the top of the band. The final run (TTM base, same recalibrated growth) is Tier C at 12.95%. Anyone quoting one number for MKL without its growth and base inputs is hiding the ball: every defensible input set here lands in C, and only the artifact growth gets to S.
- Quality is not the debate: OE positive 5/5 years, a 93% Q2 combined ratio in the core segment, conservative reserving language in the 10-K, buybacks shrinking the count, and a diversified Ventures/industrial cash-flow base. The debate is price and cash timing: at $1,825.00 the market is already paying for a recovery in the OCF run-rate that H1 2026 (current-YTD OCF $444,781,000 vs prior-YTD $880,588,000, ttm.json) has not yet delivered, plus compounding well above the like-for-like prints.
- Risks: further reserve / collateral charges in the fronting and Financial segment (State National is the current example, CATCo was the prior one), equity-portfolio drawdowns flowing straight through net income, a softening P&C pricing cycle, and the ever-present conglomerate discount. Balance-sheet leverage in the engine's measure (net debt $339.1M) is small, but that measure excludes insurance reserves — treat it as a non-answer for an insurer.
- Margin of safety: the weighted IV@15% ($1,514.69) sits 17.0% below the price — equivalently the price is above the weighted value, so there is no margin of safety at $1,825.00 on these inputs. The stock clears Andrew's 15% hurdle at or below $1,514.69 on the weighted case; even the bull case (IV@15% $1,967.24) only just clears the current price, and the bear cases sit far below it.

## Final verdict
- **Final tier: C** (weighted IRR 12.95% on the v5 final inputs; tier by numbers C, no override)
- Confidence: **Low** (SECTOR_MODEL_MISMATCH for an insurer, a TTM base depressed by a halved YTD OCF, and a 3.25x scenario spread — sized to the conservative end)
- One-liner: High-quality specialty-insurance conglomerate, moat 6/10 — but sector-mismatched for an OE DCF and priced above value on current TTM cash flow: Tier C, weighted IRR 12.95%, weighted IV@15% $1,514.69 vs $1,825.00 price; it clears 15% only at or below $1,514.69.
