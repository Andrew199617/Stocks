# DGX — Quest Diagnostics Inc
v5 run, 2026-10-15. Price $233.43 (nasdaq_quote_api), market cap $26.38B — in scope under $40B.

All figures below are copied from dcf_numbers.json, ttm.json, financials_history.csv, or key_numbers.md — none are recomputed.

## What it is
The largest independent clinical laboratory in the US, in a national duopoly with Labcorp: routine and esoteric diagnostic testing sold through physicians, hospitals/health systems, payers and a growing consumer channel (QuestHealth), plus hospital Co-Lab outsourcing partnerships. Roughly 2,400 patient service centers and a national courier/logistics network. Growth lately has been volume + M&A: the 2024 deals (LifeLabs in Canada and the Allina / OhioHealth / University Hospitals outreach labs) annualized into FY2025 revenue of $11,035M, up 11.8% (rev_yoy_latest in dcf_numbers.json), and Q2 2026 revenue grew +10.2% YoY on +13.1% requisition volume. Management raised FY2026 guidance to $11.95–12.05B revenue and $11.05–11.25 adjusted EPS after Q2 2026.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $1,886M; capex $527M (tag PaymentsToAcquirePropertyPlantAndEquipment); SBC $88M (always a real cost).
- **Conservative owner's earnings FY2025: $1,271M = $11.25/share** (base_oe_latest_per_share $11.2478).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $1,127M — below the conservative figure, same ballpark; the gap between the two definitions is capex running close to D&A in a lab network that must keep reinvesting.
- OE positive 5 of the last 5 fiscal years. Net debt $5,251M (dcf_numbers.json). Shares are shrinking slowly (share_cagr −1.43%/yr), a modest buyback tailwind already credited in the growth blend.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $1,886M − prior YTD $858M + current YTD $875M = **TTM $1,903M**
- Capex: FY $527M − prior YTD $225M + current YTD $252M = **TTM $554M**
- SBC: FY $88M − prior YTD $43M + current YTD $43M = **TTM $88M**
- Shares (current-YTD weighted diluted): **112,000,000**
- **TTM OE total $1,261M → base OE/share $11.26** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $7.27/share — rejected as the base: it is the trough figure, see BASE_DIVERGENCE below. The TTM base independently reproduces the latest FY level ($11.26 vs $11.25), so the current run rate is corroborated by two windows.

## Moat: 6/10 — moderate-strong, narrow
Justification: genuine national scale and cost advantage in a duopoly, embedded health-system relationships and an advanced-test menu — but the largest payers set the price, routine testing is commoditized, and Labcorp bids for every contract Quest holds. That is a narrow moat with weak pricing power, not a wide one.
- FOR: National scale — one of two national labs, ~2,400 patient service centers and a dense logistics network rivals cannot replicate cheaply; structural cost advantage from scale.
- FOR: Payer and health-plan access built over decades; broad managed-care coverage steers volume to Quest.
- FOR: Health-system embedding — Co-Lab partnerships and the Corewell Health joint venture, plus acquired hospital outreach labs, raise switching costs versus spot testing.
- FOR: Advanced diagnostics breadth (Haystack MRD oncology, AD-Detect, esoteric testing) differentiates the high end of the menu from routine-only labs.
- FOR: Automation / Invigorate productivity program targeting ~3% annual cost and productivity improvement — compounding cost edge.
- AGAINST: No pricing power over the price-setters: CMS/PAMA reimbursement, with proposed lab rate cuts of up to 15% from January 1, 2027, and hard commercial-payer negotiations.
- AGAINST: Routine testing is commoditized and Labcorp is a near-equal national rival contesting the same managed-care and health-system contracts.
- AGAINST: Low switching costs for physicians and patients on routine tests; volume follows payer steering, not loyalty.
- AGAINST: Labor/wage inflation is a recurring margin headwind — Q2 2026 reported operating margin fell to 15.1% from 15.9% a year earlier even as revenue grew +10.2%.
- AGAINST: Hospital customers can insource or re-bid outreach work at contract renewal; partnerships are won, not owned.
- A 6 gives CAP = 9.8 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 9.8 years, 15-year projection.

## DCF — v5 final run (2026-10-15)
Growth recalibration (written reason): the engine's g_base is 9.19% (blend 7.76% plus the +1.43pp share-count adjustment), but two blend components are rebound artifacts — OE/share CAGR 2y of 27.06% is measured off the 2023-24 trough base, and the latest revenue YoY (+11.8%) annualizes the 2024 acquisitions. Management's own long-term framework is 4-5% revenue growth and 7-9% EPS growth, and the raised FY2026 outlook (+8.3-9.2% revenue) is a near-term, volume-and-partnership-driven guide, not a steady state. Scenario starts were therefore set via offsets −0.12 / −0.07 / −0.02 / +0.02 / +0.06 vs g_base to −2.8 / 2.2 / **7.2** / 11.2 / 15.2%. Sanity check vs prints: the base start (7.2%) sits below the FY2025 revenue print (+11.8%), the Q2 2026 revenue print (+10.2%) and the FY2026 revenue guide (+8.3-9.2%) because OE must also absorb rising capex (TTM capex $554M vs FY2025 $527M) and wage pressure; the bull start (11.2%) matches the latest revenue prints; the super-bull start (15.2%) is above every revenue print but below Q2 2026 adjusted EPS growth (+19.1%), defensible only as a volume-surge plus operating-leverage plus buyback case — and it is weighted at just 10%. Probabilities 15/25/30/20/10 skew bearish vs the defaults for the January 2027 PAMA cut risk and the balance sheet (see FLAGS); OE multipliers are the defaults 0.75/0.90/1.00/1.10/1.25. Price $233.43.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | -2.8% | 0.75 | PAMA cuts land near the maximum; volume and pricing both roll over | $54.69 | 5.22% |
| Bear | 25% | 2.2% | 0.90 | Reimbursement pressure and wage inflation eat the volume growth | $81.97 | 6.88% |
| Base | 30% | 7.2% | 1.00 | Guide-level growth decays to the long-term framework over the CAP | $113.77 | 8.80% |
| Bull | 20% | 11.2% | 1.10 | Current volume momentum holds; partnerships ramp; margins stabilize | $149.49 | 10.82% |
| Super bull | 10% | 15.2% | 1.25 | Volume surge with operating leverage; advanced diagnostics mix lifts OE | $202.80 | 13.55% |

- **Probability-weighted: IV@15% $113.01 (−51.6% vs price), IV@12% $151.23, IV@10% $194.01, weighted IRR 8.79%, base-case IRR 8.80%**
- **Tier by numbers: D.** Diagnostics (key_numbers.md): OE yield 4.82%, terminal value 19.5% of IV@15%, scenario spread 3.71x, net debt 4.1x normalized OE, 9.46 months since FY end.
- No scenario clears the 15% hurdle at this price — even the super-bull case returns 13.55%. The price that clears 15% on the weighted path is the weighted IV@15% itself: **$113.01**.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.46 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, with all inputs quoted above.
- **BASE_DIVERGENCE** (latest FY OE/share $11.25 vs 3-yr median $7.27): the median is the distorted one. FY2023-24 were the post-COVID trough — revenue fell to $9,252M (2023) and $9,872M (2024) as COVID testing wound down, and OCF was depressed at $1,272M / $1,334M against $1,886M in FY2025, when volume recovered and the 2024 acquisitions annualized. The latest FY and the TTM window agree ($11.25 vs $11.26), so the TTM base is used and the median is rejected with this reason stated.
- **NI_OCF_DIVERGENCE** (2025, NI vs OCF differ by >40%): FY2025 net income is $992M vs OCF of $1,886M, from financials_history.csv. The gap runs the safe direction — NI is the *lower* figure — and is mostly non-cash: D&A of $570M and SBC of $88M are added back in OCF (both from financials_history.csv), and the maintenance OE definition, which starts from NI, still lands at $1,127M. Earnings reporting around H1 2025 also noted a one-time CARES Act tax credit contributing to that period's OCF step-up; the TTM base rolls H1 2025 out of the window (TTM = FY − prior YTD + current YTD, inputs quoted above) and still reproduces the FY2025 level, so the base does not rest on that item. The OCF-based conservative OE is the series used throughout.
- **HIGH_NET_DEBT** (net debt 4.1x normalized OE in the final run's diagnostics; $5,251M net debt): real, and it funded the acquisition program — about $2.8B of M&A deployed since 2024 per management commentary in search results. Leverage is why the probabilities skew bearish (40% on bear-or-worse) and why the super-bear OE multiplier stays at 0.75: at this leverage, a reimbursement-driven OE drop hits equity value fast. It does not change the tier — the name is Tier D on the unlevered cash flows already.
- **WIDE_SCENARIO_SPREAD** (raised on the preliminary run; final diagnostics show a 3.71x spread between super-bull and super-bear IV@15%): the spread is honest — the January 2027 PAMA decision genuinely swings this equity. Confidence is held at medium, never high, and the verdict below is sized to the weighted (not bull) case.

## My thoughts / overlay
- The verdict is unusually robust for this sweep: change the base and the tier does not move. On the trough-median base the preliminary run (default scenarios) gave a weighted IRR of 7.30% and weighted IV@15% of $84.11; on the corroborated TTM base the final run gives 8.79% and $113.01. The method range is D to D — the disagreement is only about how far below the hurdle the stock sits, not whether it clears it.
- Quality is not the problem. This is a durable duopoly cash generator with 5/5 positive OE years, a slowly shrinking share count, and real volume momentum (+13.1% requisitions in Q2 2026). The problem is purely the price: at $233.43 the market is paying more than the super-bull IV@15% ($202.80). A buyer here needs a better-than-super-bull decade to earn 15%.
- The swing factor is policy, not execution: CMS lab reimbursement cuts of up to 15% from January 1, 2027 would land directly on the routine-testing base that funds everything else, against $5,251M of net debt. Offsetting that, management is executing — Q2 2026 beat, guidance raised twice in 2026, Corewell Co-Lab ramping — which is why the bear skew stops at 40% rather than going further.
- Margin of safety: none at this price on any scenario. The weighted IV@15% of $113.01 is the 15%-clearing price; a buyer wanting a margin of safety on top of that needs a price below $113.01, i.e. a fall of more than half from $233.43.

## Final verdict
- **Final tier: D** (weighted IRR 8.79% on the v5 final inputs; no scenario, including super bull at 13.55%, clears the 15% hurdle at $233.43)
- Confidence: **Medium** (high on the TTM base — two windows agree — held down by the 3.71x scenario spread and the unresolved January 2027 PAMA decision)
- One-liner: Durable duopoly cash generator, moat 6/10 — but priced past its super-bull case: weighted IRR 8.8%, IV@15% $113 vs $233 price; it clears 15% only at $113 or below.
