# AR — Antero Resources Corporation
Pass-1 run, 2026-10-19, engine release 5.5.0. This is AR's first score. AR was blocked on 2026-10-18 (`NEEDS_MAIN_AGENT: capex`) because engine 5.4 read about 1% of its capex. Engine 5.5 reads the filed capex components (Andrew's ruling 4), and that is what unblocks it. In scope: market cap $12.091B, under $40B.

Every engine figure below is copied from the final run's key_numbers.md, dcf_numbers.json, ttm.json and score.json. ROIC, margins and the cash-flow and balance-sheet history come from fundamentals.json and statements.json (WORKER_SPEC step 5). A few figures come from research, and each one names its filing: the capex line the engine does not read, the 2026 guidance, the hedges, the post-FY debt mix and the July 2026 acquisitions. They are not engine outputs, and a reviewer cannot verify them from the diff. A preliminary same-day run on the engine-native 3-year-median base was replaced by the `--ttm` run, because STALE_FY fired and the median sits on the 2024 price trough; that run is not recorded, and none of its figures or flags appear here.

## What it is
Antero produces natural gas and NGLs in Appalachia: liquids-rich Marcellus acreage in West Virginia, plus Ohio Utica acreage until early 2026. It holds firm transportation to the Gulf Coast and the LNG corridor, and its gathering, processing and water services come from Antero Midstream, in which Antero holds an equity stake. In February 2026 it closed two deals: it bought HG Energy's Marcellus upstream assets for $2.8B in cash and sold its Ohio Utica assets for $800M. In July 2026, after the TTM window closed, it completed about $315M of further acquisitions in its West Virginia Marcellus footprint, which the release calls "strategic acquisitions" (Q2 2026 results release, 2026-07-29; not in the run outputs, whose acquisitions series ends at Q2 2026). The business is a price-taker. Henry Hub and Mont Belvieu prices drive its results, and its volumes are set by a maintenance-level drilling program.

## Owner's earnings
**Base used: TTM owner's earnings through Q2 2026, from ttm.py** (base_source `ttm_json`). The latest fiscal year ended 9.6 months ago, so the TTM figure is used. The legs are below; every capex leg is the sum of `PaymentsToExploreAndDevelopOilAndGasProperties + PaymentsToAcquireOilAndGasProperty + PaymentsToAcquireOtherPropertyPlantAndEquipment`.
- OCF: FY $1,630,930,000 − prior YTD $950,097,000 + current YTD $1,297,907,000 = **TTM $1,978,740,000**
- Capex (components): FY $944,003,000 − prior YTD $414,554,000 + current YTD $508,897,000 = **TTM $1,038,346,000**
  - The FY and current-YTD legs are `components`; the prior-YTD leg is `components_mixed_filings`.
  - **The capex-completeness section below shows this figure is not the whole capex line.**
- SBC (`ShareBasedCompensation` in all three legs; no reconciled legs): FY $60,812,000 − prior YTD $31,000,000 + current YTD $24,999,000 = **TTM $54,811,000**
- Shares (current-YTD weighted diluted): **310,931,000**
- **TTM OE total $885,583,000, so base OE/share is $2.85** (ttm.json: 2.848165670196925). ttm.json lists no warnings and no overrides.

**FY2025 (10-K), conservative definition:** latest FY OE total $626.1M, or $2.00/share. The 3-year median (normalized) OE/share is $0.21. key_numbers.md counts four of the last five years as OE-positive; FY2023 is the negative one.

**Maintenance definition:** NI + D&A − min(capex, D&A) − ΔNWC. financials_history.csv records it in the `oe_maintenance` column. key_numbers.md does not print it, so no figure is quoted here. For FY2025 it lands almost exactly on the conservative figure: D&A is below that year's capex, so this definition deducts depletion rather than capex. Two definitions that roughly agree make the FY2025 level more credible. Even so, both inherit the capex gap described next.

## Capex completeness — reconciliation against the cash-flow statement
Engine 5.5 sums Antero's filed PP&E components because Antero has filed no `PaymentsToAcquirePropertyPlantAndEquipment` roll-up since FY2022. The resulting capex is $943,971,000 for FY2022 (roll-up), $1.132B for FY2023, $716.8M for FY2024 and $944.0M for FY2025 (key_numbers.md). `capex_provenance` breaks each year down as follows:

| Fiscal year | Explore and develop (drilling and completion) | `PaymentsToAcquireOilAndGasProperty` | Other PP&E | `PaymentsToAcquireOilAndGasProperty` filed in |
|---|---|---|---|---|
| FY2023 | $964,346,000 | $151,135,000 | $16,382,000 | FY2024 10-K (2025-02-12) |
| FY2024 | $614,855,000 | $90,995,000 | $10,929,000 | FY2024 10-K (2025-02-12) |
| FY2025 | $685,468,000 | $253,128,000 | $5,407,000 | FY2025 10-K (2026-02-11) |

I checked these against the investing section of the cash-flow statement (FY2025 10-K figures from the Q4 2025 release, 8-K exhibit 99.1, filed 2026-02-11). One filed capex line is not read for FY2025 or for the 2026 quarters:
- **FY2024 is complete, and FY2023 reads the same three lines.** Up to the FY2024 10-K, Antero tagged its "Additions to unproved properties" line (leasehold/land) as `PaymentsToAcquireOilAndGasProperty`. The FY2023 and FY2024 values above are that line: each equals the year's costs-incurred unproved figure. The FY2024 statement shows no other capex line (2024: unproved additions (90,995), drilling and completion (614,855), other PP&E (10,929), acquisitions —). I did not see the FY2023 statement itself, so FY2023's completeness rests on the same tagging.
- **FY2025 misses the land line.** In the FY2025 10-K, `PaymentsToAcquireOilAndGasProperty` carries a new line, "Acquisitions of oil and gas properties" (253,128). This was the 2025 purchase of higher working interests. "Additions to unproved properties" (**129,247**, in thousands) moved to a company extension tag. EDGAR companyfacts carries that amount only as `CostsIncurredAcquisitionOfUnprovedOilAndGasProperties`, a supplemental-note tag the engine correctly does not read as cash capex. FY2025 capex is therefore understated by that line. Because OE = OCF − capex − SBC, the $2.00 latest-FY OE/share is overstated (inflated) by it.
- **statements.json is consistent with this.** Its FY2025 net investing outflow is $1,077,813,000 against the engine's $944,003,000 of capex, and the unread 129,247 land line accounts for most of that difference. The FY2024 outflow ($714,153,000) sits just below the engine's $716.8M, and the FY2023 outflow ($1,140,767,000) close to its $1.132B, as two complete years should. Net investing cash flow also carries other items (asset-sale proceeds, other investing), so this is a consistency check, not a line-by-line reconciliation.
- **The TTM legs are inconsistent.**
  - The FY leg ($944,003,000) misses the 129,247 land line.
  - The prior-YTD leg ($414,554,000) *includes* the H1 2025 land line (56,640). That 10-Q, filed 2025-07-30, still used the old tag, and the Q2 2026 10-Q's comparative column does not re-file that tag for H1 2025.
  - The current-YTD leg ($508,897,000) misses the H1 2026 land line (**45,551**, Q2 2026 release cash-flow statement). It does include 7,631 of property acquisitions.
  - So the TTM subtracts the H1 2025 land line once and never adds a land line back. The land line's net contribution to the $1,038,346,000 TTM capex is negative, not just missing, and ttm.json raises no warning for it.
- **Net effect on the base.** TTM capex of $1,038,346,000 understates total PP&E investment by the two unread land lines. At the same time it counts the property acquisitions in full (253,128 in FY2025, 7,631 in H1 2026), which a maintenance view would leave out. For comparison, the 2026 budget is $1.0B of drilling and completion ($900M of it maintenance) plus $100M of land capital (Q4 2025 release). The TTM capex sits just below that budget.
  - **Every recorded valuation figure is therefore an upper bound** (see "Status of the recorded band" in the re-score section).
  - I made an exploratory engine run with both unread land lines added to TTM capex. It is not the recorded run, so no figure from it is quoted. Its weighted result stays in Tier C, its bear case falls to Tier D and its bull case falls to Tier C.
- **No override can fix this.** An override fills only periods with no filed value, and a `base_override` may use only figures this run printed, which do not include the land line. The engine gap is raised with Andrew, and I sized the verdict to the bear end (see Final verdict).
- **The median base is not affected.** Its median year, FY2024, is verified complete.

## Moat: 3/10 — weak; scale and logistics, no franchise
Justification: Antero is a scaled, low-cost Appalachian producer. It has deep core Marcellus inventory, deepened by HG, and firm transportation that earns a premium to NYMEX. But it is a pure price-taker. fundamentals.json's `roic_proxy` reads:

| FY2021 | FY2022 | FY2023 | FY2024 | FY2025 |
|---|---|---|---|---|
| 0.24% | 26.2% (price spike) | 3.87% | 0.00% | 7.48% |

Only the 2022 spike cleared the cost of capital. fundamentals.json prints no gross-margin series because no cost-of-revenue tag is filed. Operating margin went from 35.6% (FY2022) to 0.01% (FY2024) and 16.7% (FY2025). Returns follow the commodity price.
- FOR:
  - Deep core Marcellus inventory in the liquids-rich window.
  - Firm transportation to Gulf Coast and LNG-corridor markets, which earns a realized premium to Henry Hub.
  - One of the largest US NGL producers, with export access.
  - Long-term gathering, processing and water agreements with Antero Midstream.
- AGAINST:
  - Price-taker on gas, NGLs and oil.
  - ROIC below the cost of capital in four of the last five years.
  - Large fixed firm-transport and gathering commitments; dcf_numbers.json records lease liabilities of $2,125,058,000.
  - Recent growth was bought, not drilled, on top of a maintenance-level plan: HG with debt (balance-sheet section), then the July 2026 acquisitions, whose funding the run outputs do not show.
  - Appalachian takeaway and basis risk.
- A 3 gives CAP = 5.9 years: growth holds 2 years, then fades linearly to the 2.50% terminal rate.

## DCF — engine 5.5 final run (2026-10-19)
Inputs: moat 3, probabilities 15/25/30/20/10, default growth offsets (−12/−5/0/+5/+12pp) and default OE multipliers (0.75/0.90/1.00/1.10/1.25), `--ttm`. Price $38.71.
- **Growth:** the blend is 10.34%, so g_base is 10.34%. Its components are 5-year revenue CAGR 8.61%, 3-year revenue CAGR −9.59% and latest revenue YoY 21.97%; the 2-year OE/share CAGR is "—" because its FY2023 endpoint is negative. Revenue components get a 1.74% adjustment for the share count, which shrinks 1.74% a year.
- **Guidance check** (Q2 2026 release, 2026-07-29): FY2026 production guidance was raised to 4.15–4.2 Bcfe/d, with Q4 2026 at 4.4–4.5 Bcfe/d, and Q2 production was up 21% year on year.
  - The base start of 10.3% sits below both the 21.97% FY2025 revenue print and the volume step-up. That is deliberate. The FY2025 print is a gas-price recovery off the 2024 trough plus the working-interest purchase. The 2026 volume step-up is HG, bought for cash, and the TTM base already holds about five months of it. The budget itself is maintenance-level.
  - The bull (15.3%) and super-bull (22.3%) starts cover a full year of HG plus LNG-driven price strength. The super bear (−1.7%) covers a return to 2024-type prices.
- **Probabilities:** shifted toward the bear (super bear 15%, bull 20%) because OE_VOLATILE is real.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IV@12 | IRR |
|---|---|---|---|---|---|---|---|
| Super bear | 15% | -1.7% | 0.75 | Gas back to trough pricing; LNG start-ups slip; fixed transport costs bite | $15.13 | $19.76 | 7.29% |
| Bear | 25% | 5.3% | 0.9 | Strip fades after the 2026–27 hedges roll off; maintenance mode only | $23.20 | $30.68 | 10.05% |
| Base | 30% | 10.3% | 1.0 | Full-year HG volumes at mid-cycle prices, then flat | $30.60 | $40.76 | 12.48% |
| Bull | 20% | 15.3% | 1.1 | LNG demand tightens Henry Hub; NGL exports strong | $39.79 | $53.38 | 15.33% |
| Super bull | 10% | 22.3% | 1.25 | Sustained structural gas-price reset plus discretionary growth capital | $56.84 | $76.94 | 20.09% |

- **Probability-weighted:** IV@15% $30.89 (−20.2% vs price), IV@12% $41.23 (+6.5%), IV@10% $52.77; **weighted IRR 12.59%**, base-case IRR 12.48%.
- **IRR band:** bear 10.05% (Tier C) to bull 15.33% (Tier B); scenario range 7.29%–20.09%.
- **Tier by numbers: C.**
- **Diagnostics** (key_numbers.md): OE yield 7.36%; terminal value 19.1% of IV@15%; scenario spread 3.76x; net debt 1.57x normalized OE (on FY2025 debt; see the balance-sheet section); 9.6 months since FY end.
- **Hurdle-clearing prices:** 15% at $30.89, 20% at $21.61, 25% at $16.51.

## Flags — every fragility flag resolved
The final run raised five flags (key_numbers.md): STALE_FY, OE_VOLATILE, NI_OCF_DIVERGENCE, BASE_DIVERGENCE and TIER_BAND. No other flag fired (none of the engine 5.5 flags either; see the re-score section), and there is no DATA_GAP.
- **STALE_FY** (the latest FY ended 9.6 months ago; the flag text rounds to 10). Resolved with the TTM base from ttm.py through Q2 2026, legs quoted above. The capex legs carry the land-line defect described above, so the TTM IRR is an upper bound. The tier holds in the exploratory check.
- **BASE_DIVERGENCE** (latest FY OE/share $2.00 vs 3-year median $0.21). Both readings are distorted, in opposite directions:
  - The median sits on FY2024, the gas-price trough (fundamentals.json: operating margin 0.01%, roic_proxy 0.00%), inside a window whose FY2023 OE was negative. That is cycle-low earnings, not today's earning power.
  - The latest FY ($2.00) is overstated (inflated) by the unread 129,247 land line.
  - The TTM base ($2.85) is the current reading. It is used with its stated upper-bound caveat, and the median ($0.21) is kept as the trough-price reference.
- **OE_VOLATILE** (OE/share spans more than 3x over 5 years). This is real commodity cyclicality: the 2022 spike, the 2023–24 trough and the 2025–26 recovery. I handled it with bear-skewed probabilities (15% super bear) and by sizing to the bear end. It is not an artifact.
- **NI_OCF_DIVERGENCE** (FY2025 net income $674,567,000 vs OCF $1,630,930,000, statements.json). The cause is recurring non-cash charges, not a one-off:
  - Depletion is the largest non-cash charge for a producer: D&A was $749,675,000 (the engine reads the `DepreciationDepletionAndAmortization` tag).
  - FY2025's income-tax expense was almost entirely deferred: the cash-flow statement's deferred-tax line is $213,965,000 against $215,867,000 of income-tax expense (statements.json).
  - Derivative marks also contribute; statements.json does not separate them.
  - The OE base starts from OCF and deducts actual capex, not depletion, so neither item contaminates the base.
- **TIER_BAND** (bear Tier C at 10.05%, bull Tier B at 15.33%). Size to the bear end. With the unread land lines deducted, the bear end falls into Tier D and the bull end into Tier C (exploratory run, see above), so I size the position as a D/C, not a C/B.

## Balance sheet and claims ahead of common
- **FY2025 net debt.** The engine's figure is $1.398B (`LongTermDebtNoncurrent`; cash reads 0 because the $210,000,000 year-end balance was restricted cash, `RestrictedCashCurrent`).
- **Net debt after the year end.** statements.json shows total debt of $2,614,258,000 at June 30, 2026 (short-term debt $182,000,000 plus long-term debt $2,432,258,000) with cash read as 0; the Q2 2026 release's net-debt table gives the same $2,614,258 thousand.
  - It covers commercial paper, a new $1.1B term loan, the 2030 notes and new 2036 notes; the 2029 notes were retired (Q2 2026 release).
  - The rise came from the HG purchase. statements.json's acquisitions line shows $2,794,308,000 in Q1 2026 and $8,887,000 in Q2 2026, the release's 2,803,195 cash out in H1 2026, against 756,986 of asset-sale proceeds (release).
  - The engine's 1.57x leverage diagnostic uses FY2025 debt and understates current leverage. On the recorded base, June 2026 net debt sits just under the engine's 3x HIGH_NET_DEBT line; on the exploratory land-corrected base it sits above it.
- **Why it does not change the IV.** The model values levered OE: interest on the new debt runs through OCF, and the TTM legs already carry part of it. Debt feeds diagnostics only, so the IV is not reduced a second time.
- **Hedges** (Q2 release) cushion the next 18 months: H2 2026 gas swaps on 1.39 Bcf/d at $3.90 and 2027 swaps on 1.0 Bcf/d at $3.84.
- **Minority holders.** Consolidated OCF includes a variable-interest entity whose third-party owners receive distributions (noncontrolling interests). The OE base does not deduct them, so it slightly overstates what common holders own. statements.json gives the scale: FY2025 net income of $674,567,000 against net income to common of $634,418,000, and a minority-interest balance of $164,822,000 at the FY2025 year end. The run outputs do not compute the OE-level share, so this is a method limit. That the gap between the two income lines is only the noncontrolling share cannot be verified from the diff.
- **Fixed commitments.** Operating lease liabilities of $2,125,058,000 (dcf_numbers.json) are mostly long-term midstream and transport commitments, paid out of OCF.

## My thoughts / overlay
- **Why AR was blocked.** The 5.4 Tier B was fake. It computed OE = OCF − capex − SBC with capex read off the other-PP&E line alone ($16,382,000 / $10,929,000 / $5,407,000 for FY2023–25). With the components summed, AR is a capital-intensive producer. FY2023 OE was negative, FY2024 was close to zero, and only the 2025–26 price recovery (plus HG) lifts TTM OE to $2.85/share.
- **The method range.** The 3-year median base ($0.21/share) is a trough-price reading and is not the recorded run. The TTM base gives Tier C (weighted IRR 12.59%), and the exploratory land-corrected TTM run stays in Tier C, with its bear case in Tier D and its bull case in Tier C. No weighted reading clears 15%. The base case needs mid-cycle prices to persist just to earn 12.48%.
- **What would change the verdict:** a structural Henry Hub reset from LNG demand (the bull and super-bull rows), or a price near $30.89 (IV@15%).
- **Margin of safety:** none at 15%. The weighted IV@15% sits 20.2% below the price, and even the base case's IV@15% ($30.60) is below the $38.71 price.

## Final verdict
- **Final tier: C** (weighted IRR 12.59% on the TTM base; numbers tier C, no override).
- **Sizing:** to the bear end. The bear case reads 10.05% (Tier C) as recorded and falls to Tier D once the unread land capex is deducted.
- **Confidence: low.** Three reasons: the earnings are a commodity price; the TTM capex legs omit an extension-tagged land line, so the recorded IRR is an upper bound; and TIER_BAND fires. Tier C is not alert-eligible (score.json: `alert_eligible` false, `exit_alert_eligible` true).
- **One-liner:** Scaled Appalachian gas/NGL price-taker, moat 3/10. On the TTM base it does not clear 15% (weighted IRR 12.59%, IV@15% $30.89 vs $38.71). The TTM capex misses an extension-tagged land line, so 12.59% is an upper bound; size to the bear end (10.05%). It clears 15% only below about $30.89.

## Data and enrichment
- **Enrichment steps:** fundamentals.py, prices.py, segments.py, statements.py, profile.py and reprice.py all ran and exited 0.
- **Display mismatch with the engine.** fundamentals.json and statements.json still show "Capital expenditures" as the other-PP&E line alone ($16,382,000 / $10,929,000 / $5,407,000 for FY2023–25). Their free-cash-flow and owner's-earnings rows are built on that line too. They disagree with the engine's summed components above. Those files are display-only and not valuation inputs; the company page's Financials tab will show the decoy capex until those scripts sum components the way dcf_engine.py does. Raised with Andrew.
- **Cover-page check.** The dei cover-page count is 307,439,000 (2026-07-24), consistent with the diluted latest count of 312,361,000. There is no share-scale or split issue.

## Engine 5.5 re-score (2026-10-19)
- **Old:** none (blocked). AR had never been scored. The 2026-10-18 worker blocked it `NEEDS_MAIN_AGENT: capex`. The engine 5.4 files on main were not a score:
  - dcf_numbers.json (release 5.4.0) printed a fake Tier B at a weighted IRR of 17.27% on a 3-year-median base of $2.9487/share, built on about 1% of true capex.
  - ttm.json read TTM capex of $12,721,000, which was the other-PP&E line alone, and TTM OE/share of $6.15 (6.146727087360218).
- **New:** base OE/share $2.85 (TTM, ttm_json); latest FY $2.00; normalized (3-year median) $0.21. Weighted IRR 12.59%, **Tier C**. The recorded band runs from bear 10.05% (Tier C) to bull 15.33% (Tier B); see "Status of the recorded band" below.
- **What engine 5.5 changed for this filer:**
  - **Capex components.** Antero filed no `PaymentsToAcquirePropertyPlantAndEquipment` roll-up for FY2023–25. Engine 5.5 now sums the filed components `PaymentsToExploreAndDevelopOilAndGasProperties + PaymentsToAcquireOilAndGasProperty + PaymentsToAcquireOtherPropertyPlantAndEquipment`.
    - FY2023: $1.132B (`components_mixed_filings`).
    - FY2024: $716.8M (`components_mixed_filings`).
    - FY2025: $944.0M (`components`).
    - FY2022 stays the roll-up, $943,971,000.
    - ttm.py now sums the same components in every leg. Its ttm.json replaces the 5.4 one above: TTM capex goes from $12,721,000 to $1,038,346,000, and TTM OE/share from $6.15 to $2.85.
  - **Unchanged.** No intangible purchases are filed. The SBC tag stays `ShareBasedCompensation`: `sbc_provenance` is empty and there is no reconciliation. The share basis is unchanged; the cover-page ratio is consistent and there was no split or divergence. The market cap is $12.091B (`diluted_latest`, price × shares) with no ADS ratio. The USD-override branch did not apply: this is a USD filer with no FX conversion and no overrides.
- **New 5.5 flags:** none fired on AR's final run. That covers SHARE_SCALE_SUSPECT, SHARE_BASIS_ADJUSTED, SHARE_BASIS_DIVERGENCE, CAPEX_COVERAGE_LOW (capex is well above half of D&A in each of FY2023–25), SBC_TAG_RECONCILED and OVERRIDE_SUPERSEDED_BY_FILED_TAG:capex. There is no DATA_GAP.
- **What 5.5 still does not read.** Antero's FY2025 10-K moved "Additions to unproved properties" to a company extension tag, and companyfacts does not carry extension tags. The capex-completeness section gives the line's amounts and their filings. In ttm.json:
  - The FY leg (2025-01-01 to 2025-12-31) and the current-YTD leg (2026-01-01 to 2026-06-30) are both `components`, and both miss the land line.
  - The prior-YTD leg (2025-01-01 to 2025-06-30) is `components_mixed_filings`. Its `PaymentsToAcquireOilAndGasProperty` value comes from the Q2 2025 10-Q, which still tagged the H1 2025 land line that way.
  - So the TTM subtracts the H1 2025 land line once and never adds a land line back; its net contribution to the $1,038,346,000 TTM capex is negative, and ttm.json raises no warning for it.
- **Status of the recorded band.** Every recorded valuation figure is an upper bound: weighted IRR 12.59%, bear 10.05%, bull 15.33%, IV@15% $30.89, and hurdle prices $30.89 / $21.61 / $16.51.
  - The exploratory engine run with both unread land lines added to TTM capex is not the recorded run, so no figure from it is quoted. Its weighted result stays in Tier C, but its bear case falls to Tier D and its bull case falls to Tier C.
  - So the recorded bull tier B does not hold.
  - On that base, the June 2026 net debt in the balance-sheet section would sit above the engine's HIGH_NET_DEBT line.
- **Why no override fixes it.**
  - A `capex_override` fills only periods with no filed value, and FY2025 and every TTM leg carry a filed (incomplete) value.
  - A `base_override` may use only figures this run printed, and none of them carries the land line.
- **Open items for Andrew.**
  - **Capex land line** (`NEEDS_MAIN_AGENT: capex`). Either the engine reads the extension-tagged line, or a filing-sourced base is allowed; then AR is re-run. Until then, size to the bear end, which is Tier D on the exploratory run.
  - **Utica divestiture inside the TTM base** (next bullet), raised together with the capex gap.
  - **Display mismatch** (Data and enrichment section): statements.py / fundamentals.py need a code fix to sum capex components the way dcf_engine.py does.
- **Utica divestiture inside the TTM base.** The TTM window runs from July 2025 to June 2026. Antero owned the Ohio Utica assets (What it is section) until the sale closed in February 2026, so the base holds the sold business from July 2025 until that close. HG's acquired assets count only from February 2026. AGENTS.md check 7 treats a base that still contains a sold business as a defect, so the sold business's share must be stated, and it is not quantified here:
  - Neither this run's outputs nor the Q2 2026 release (re-read 2026-10-19) state the Utica assets' production or cash flow for that period. The Q2 2026 10-Q's divestiture note and MD&A are where to look; this cannot be verified from the diff.
  - The direction is unknown. HG is the larger deal, which points to a forward run-rate above the TTM. But its acquisition debt adds interest, and that interest runs through OCF.
  - The base is not adjusted.
- **Why the tier is C.** On the TTM base AR earns $2.85/share. That is an OE yield of 7.36% at $38.71, with g_base 10.34% and a moat of 3, and gives a weighted IRR of 12.59%, inside the 10–15% band. The 15% hurdle price, $30.89, is below the market. The fake B came only from the missing drilling and leasehold capex. The land-line gap above lowers the result, but on the exploratory run it does not leave Tier C.

## Sources
- Antero Resources, Q2 2026 results release (2026-07-29), https://www.anteroresources.com/news-events/press-releases/detail/259 — investing lines for the six months, net-debt table, hedges, production guidance, and the approximately $315M of West Virginia acquisitions completed in July 2026 (Highlights and Strategic Updates).
- Antero Resources, Q4 2025 results and 2026 guidance, 8-K exhibit 99.1 (filed 2026-02-11), https://www.sec.gov/Archives/edgar/data/1433270/000110465926013420/tm265893d1_ex99-1.htm — FY2024–25 investing lines, 2026 capital guidance.
- Antero Resources, Marcellus acquisition and Utica divestiture announcement (December 2025), https://www.anteroresources.com/news-events/press-releases/detail/252.
- SEC EDGAR companyfacts, CIK 1433270 — tags carrying the unproved-property additions (`CostsIncurredAcquisitionOfUnprovedOilAndGasProperties` only, from FY2025 on).
