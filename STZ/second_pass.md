# STZ — Second pass (2026-10-13)

**Verdict: NO MATERIAL FINDING.** Pass 1's score stands: Tier C, weighted IRR 10.1%, weighted IV@15% $77.67, price $126.40, base OE $10.31/share (TTM through Q2 FY2027), moat 6/10, probs 15/30/30/20/5. score.json is NOT touched.

Pass 1 (2026-10-12) was unusually fresh and deep — it already read the Q2 FY27 release/10-Q (Oct 6, 2026) line-by-line, built the base TTM filing-direct, and resolved the wine divestiture basis break. This pass attacked its load-bearing assumptions (TTM base, per-share scenario starts embedding a ~2.5%/yr buyback, bear-skewed probabilities, moat 6) and found no quantified evidence to move any of them.

## Filing freshness + forensic battery (step 0, every run)

Full `forensic_pull.py STZ` output:

```
# Forensic battery — STZ (CIK 16918)
Tags used: revenue=RevenueFromContractWithCustomerExcludingAssessedTax, gross_profit=GrossProfit, cogs=CostOfGoodsAndServicesSold, sga=SellingGeneralAndAdministrativeExpense, ni=NetIncomeLoss, oi=OperatingIncomeLoss, disc_ops=None, nonop=None, prepaids=PrepaidExpenseAndOtherAssetsCurrent, assets=Assets

| FY end | Revenue | Gross margin | COGS %rev | SG&A %rev | (COGS+SG&A) %rev | NI vs OI gap | Disc ops | Nonop inc |
|---|---|---|---|---|---|---|---|---|
| 2021-02-28 | $8.61B | +51.8% | +48.2% | +19.4% | +67.6% | -28.4% | n/a | n/a |
| 2022-02-28 | $8.82B | +53.4% | +46.6% | +19.4% | +66.0% | -101.7% | n/a | n/a |
| 2023-02-28 | $9.45B | +50.5% | +49.5% | +20.4% | +69.9% | -102.5% | n/a | n/a |
| 2024-02-29 | $9.96B | +50.4% | +49.6% | +18.4% | +68.0% | -45.5% | n/a | n/a |
| 2025-02-28 | $10.21B | +52.1% | +47.9% | +19.1% | +67.0% | -122.9% | n/a | n/a |
| 2026-02-28 | $9.14B | +51.6% | +48.4% | +20.2% | +68.7% | -38.0% | n/a | n/a |

## Prepaid battery
- 2024-11-30: prepaids $590M = 2.6% of assets
- 2025-02-28: prepaids $561M = 2.6% of assets
- 2025-05-31: prepaids $628M = 2.8% of assets
- 2025-08-31: prepaids $700M = 3.3% of assets
- 2025-11-30: prepaids $669M = 3.1% of assets
- 2026-02-28: prepaids $712M = 3.3% of assets
- 2026-05-31: prepaids $765M = 3.5% of assets
- 2026-08-31: prepaids $804M = 3.6% of assets
- YoY change at 2026-08-31: +15.0%
- Prepaids / latest FY SG&A: 44%

## Battery flags
- NI_OI_GAP 2022-02-28: net income differs from operating income by -101.7% — noncore items are material to earnings quality.
- NI_OI_GAP 2023-02-28: net income differs from operating income by -102.5% — noncore items are material to earnings quality.
- NI_OI_GAP 2024-02-29: net income differs from operating income by -45.5% — noncore items are material to earnings quality.
- NI_OI_GAP 2025-02-28: net income differs from operating income by -122.9% — noncore items are material to earnings quality.
- NI_OI_GAP 2026-02-28: net income differs from operating income by -38.0% — noncore items are material to earnings quality.

## Filing freshness
- Pass 1 analysis date: 2026-10-12; latest period pass 1 used: 2026-02-28
- Newer periodic filing since pass 1: NONE — pass 1 data is filing-current.
- Material 8-Ks since pass 1: none
```

### Freshness resolution
No newer 10-K/10-Q and no material 8-K since pass 1. Note the battery's "latest period pass 1 used: 2026-02-28" is the FY end in dcf_numbers.json; pass 1's actual base was already TTM through the Q2 FY27 10-Q (period ended 2026-08-31, filed/released Oct 6, 2026) — OCF TTM $2,658.3M − capex TTM $819.0M − SBC TTM $70.5M = $1,768.8M = $10.31/share on 171.503M shares. There is no newer filing to recompute from, so no TTM recompute is triggered. Pass 1 is filing-current.

### Battery flag resolutions
- **Margin structure / moat evidence:** Gross margin is 50.4–53.4% across FY21–FY26 with no trend break — comfortably above the 40% durable-advantage rule of thumb, and sector-relative it is premium-import-beer economics (beer segment operating margin ~39% in Q2 FY27, even after the −160bp step-down). This supports, and does not exceed, moat 6: the margin is real, but pass 1 already credited it; the moat cap comes from concentration/category, not margin.
- **COGS % of revenue:** 46.6–49.6% over six years, a ~3pp band with no directional drift (48.2% FY21 → 48.4% FY26). No cost-control red flag; the FY23 uptick to 49.5% reversed. Not a non-compounder swing pattern.
- **SG&A-vs-COGS split test:** No migration. SG&A % rose (18.4% FY24 → 20.2% FY26) while COGS % also rose slightly (47.9% → 48.4% FY25→FY26); combined (COGS+SG&A)/revenue moved 67.0% → 68.7%, i.e. costs genuinely rose (stepped-up marketing/SG&A, per the Q2 release) rather than being reclassified between lines. The combined series and the reported series tell the same story — no IBM-pattern optics.
- **NI_OI_GAP (all five flagged years) — resolved, does not touch the base:** The gap is persistently negative because net income sits far below operating income: net interest expense, historical equity-method losses (Canopy Growth era), taxes, and — decisively in FY25 — ~$2.8B of non-cash wine & spirits impairments plus a ~$478M held-for-sale write-down (FY25 NI −$81.4M vs OI $354.9M vs OCF $3,152.2M). The base OE is OCF − capex − SBC: impairments never touch OCF, and cash interest/taxes are already inside OCF. Noncore items are therefore *dragging reported NI*, not carrying the base. See the noncore reconstruction below.
- **Prepaid battery — no deferral pattern:** Prepaids rose gradually from 2.6% of assets (Feb 2025) to 3.6% (Aug 2026), +15.0% YoY at Aug 31, 2026, at 44% of FY SG&A. The deferral pattern requires prepaids spiking *while earnings improve and OCF weakens*; here the rise is gradual and within-year seasonal (builds Feb→Aug in both years shown), comparable EPS is guided flat, and OCF TTM ($2,658.3M) is essentially flat vs FY26 ($2,669.0M), not weakening against improving earnings. No leg of the pattern is present beyond a modest prepaid build, which is noted, not flagged as a finding.
- **Discontinued ops:** Battery tag is None/n-a — the divested wine brands were not carried as discontinued operations; they sat in Wine & Spirits until the June 2, 2025 close. Pass 1's BASIS_BREAK resolution already handles the comparability break. No hidden disc-ops line on the books.

### Judgment checks
- **Divestiture optics — pre/during/post (wine divestitures, closed Jun 2, 2025):** Pre (FY24): OI $3,169.7M, SG&A 18.4% of revenue, OCF $2,780.0M, FCF $1,510.9M. During (FY25): OI collapsed to $354.9M on the impairments/write-down above, OCF actually rose to $3,152.2M. Post (FY26): OI $2,721.4M, SG&A % *rose* to 20.2%, OCF *fell* to $2,669.0M, conservative OE $1,726.3M. Plainly: **not accounting optics flattering the parent** — post-sale, the remaining company shows higher SG&A intensity and lower cash flow than pre-sale; nothing was stranded off the P&L to fake an improvement, and the profit that remains is the beer segment's ~39% operating margin, which predates the sale. The divestiture shrank revenue (−10.5% reported FY26) while organic sales were roughly flat — pass 1 correctly used organic/TTM inputs, not the reported CAGR.
- **Noncore income reconstruction:** Core = operating income (beer-dominated). The NI-vs-OI gap (above) is noncore *drag* (interest, equity losses, impairments, tax), not noncore income carrying earnings. Rebuilding base OE on core numbers changes nothing: the OCF-based base already excludes non-cash impairments and already bears cash interest and taxes. Noncore is not material to the base in the inflating direction — no reconstruction finding.
- **Capitalized-cost shifting (WorldCom pattern) — no legs present:** Capex is *falling*, not growing faster than revenue (FY24 $1,269.1M → FY25 $1,214.1M → FY26 $875.0M; capex/revenue 12.7% → 9.6%); SG&A % is rising, not falling; and net income runs far *below* OCF in every flagged year (earnings do not outrun cash flow). Zero of the pattern's legs hold.
- **Recurring "one-offs":** The impairment charges pass 1 treated as non-recurring were tied to the specific wine portfolio that has now been sold; post-sale, Q2 FY27's reported-vs-comparable EPS gap narrowed enough that reported FY27 guidance was *raised* ($11.85–12.55) on fewer expected comparability items while comparable guidance stayed flat. No evidence of a new recurring charge stream replacing the old one in the one quarter since.
- **Honest OE definition:** The **conservative total-capex definition (OCF − total capex − SBC)** is the honest headline for STZ, as pass 1 held. The NI-based maintenance version is unusable for FY24–FY25 (impairments flow through NI but only D&A is added back), and while a maintenance-capex = D&A sensitivity gives ~$12.64/share, pass 1 already quantified that it only lifts the weighted IRR to ~12–13% — still below the 15% hurdle — because the Mexico/Veracruz capex program (~$800M/yr guided through FY28) is a real, multi-year cash commitment, not yet a rolled-off steady state. The definition choice does not change the verdict.

## Targeted research (what a standardized pass misses)
1. **Segment masking — checked, pass 1 had it right, in both directions.** Beer is ~94% of H1 FY27 net sales; there is no large legacy segment left to drag or flatter the total after the wine exit. *Within* beer, the split pass 1 flagged is confirmed by Q2 coverage: total beer depletions −0.6%, with Modelo Especial ~−2% and Corona Extra ~−5% partly offset by Pacifico ~+19%, Victoria ~+15%, Chelada ~+5% — the growing smaller brands are not yet large enough to mask the flagship decline, and pass 1's scenario starts (base +2% per-share ≈ flat total OE) already reflect exactly that mix. Wine & Spirits depletions +10.2% on a $159M quarter is real but immaterial to consolidated OE. Sources: Constellation Q2 FY27 earnings recap (cbrands.com); Zacks Q2 recap, Oct 7, 2026.
2. **Post-filing events — none material after pass 1's analysis date.** The Q2 print (Oct 6), the SpikedAde acquisition ($75M upfront + up to $278M contingent over five years; company states it does not affect FY27 outlook; ~108k cases in NielsenIQ channels — immaterial to a $1.77B OE base), the reported-EPS guidance raise to $11.85–12.55 with comparable EPS reaffirmed flat at $11.20–11.90, and the $1.03 dividend declaration all predate or coincide with pass 1 (Oct 12) and are already in its analysis. Searches found no guidance change, M&A, customer loss, or product sunset in the Oct 12–13 window. Sources: American Banking News / Markets Daily SpikedAde and guidance coverage, Oct 6–8, 2026; Shanken News Daily, Oct 6, 2026.
3. **SBC / dilution trajectory — confirms pass 1's buyback tailwind, refutes dilution risk.** SBC TTM is only $70.5M (~2.7% of OCF) and is charged in full in the base. Diluted shares fell 183.959M (FY24) → 175.568M (FY26) → 171.503M (H1 FY27) on $530M of H1 FY27 repurchases. Independent Q2 coverage confirms comparable net income was flat YoY ($637.3M vs $637.8M) and the +3% comparable EPS growth came entirely from the lower share count — exactly the ~2.5%/yr per-share tailwind embedded in pass 1's scenario starts, not double-counted and not reversed.
4. **Thin-flag re-check (demand/Hispanic consumer):** Post-earnings coverage (Oct 7) reiterates that ~40% of Constellation's beer spend comes from Hispanic consumers vs ~15% for the category, that management is holding price increases to the low end of its range to retain that cohort, and that elevated fuel costs were cited by analysts as an added headwind — all consistent with, and none worse than, pass 1's bear-skewed 45% combined bear weight. No evidence the demand picture has either recovered (which would challenge the bear skew upward) or deteriorated beyond what Q2 already showed.

## Sanity check on scenario starts (standing rule)
Unchanged from pass 1 and re-verified against the latest prints: base +2% per-share vs depletions −0.6% (Q2) / −0.3% (Q1), flat organic guide (−1% to +1%), flat comparable EPS guide — consistent. Bull +5% remains a recovery case above current prints, weighted 20%. Super bull +8.6% remains a full-normalization case, weighted 5%. No start sits below the latest print without its written pass-1 reason.

## Conclusion
Every forensic flag resolves to items pass 1 already identified and correctly routed around (impairment-driven NI gap, divestiture basis break); the freshness check is clean; segment, post-filing, and dilution hunts surface nothing pass 1 missed in either direction. **Score stands — Tier C, weighted IRR 10.1%, IV@15% $77.67. No change to score.json.**
