# TTWO — Second pass (2026-10-13)

**Verdict: NO MATERIAL FINDING — score stands.** Pass 1 (2026-10-12, engine v4): Tier F, base OE/share −$0.07 (TTM through Q1 FY2027), normalized 3-yr median −$2.90, latest FY +$0.85, moat 6/10, price $208.82. score.json untouched.

## What pass 1 assumed (load-bearing)
- Base OE: TTM conservative OE = OCF $500.2M − capex $162.7M − SBC $350.6M = −$13.1M (−$0.07/sh on 186.2M Q1 FY27 diluted shares). Both the normalized median and the TTM base are negative; the lone positive FY (FY2026, +$0.85/sh) capitalises only to Tier D (weighted IRR 3.2%, IV@15% $10.40) in pass 1's sensitivity run.
- Moat 6/10 (CAP 9.8y) — franchise-level strength (GTA, NBA 2K, 78% recurrent bookings) diluted by Zynga mobile, licensed (not owned) NBA 2K, no owned platform, and single-title concentration on GTA VI (Nov 19, 2026, twice delayed).
- Scenario probabilities 10/25/30/25/10 carried for the record only — no scenario IVs are computable on a negative base, by design.
- Flag resolutions rested mainly on: goodwill impairments ($2,342M FY2024, $3,545M FY2025, $0 FY2026) explaining the NI/OCF gaps; dilution +4.8%/yr (Zynga stock consideration + SBC $305–351M/yr); the FY2027 guide (bookings $8.0–8.2B, OCF >$1B, GAAP net income only $104–143M) as a forward year, not a filing-derived base.

## Step 0 — Filing freshness + forensic battery

`python3 ~/workspace/stocks/_system/forensic_pull.py TTWO` full output:

```
# Forensic battery — TTWO (CIK 946581)
Tags used: revenue=RevenueFromContractWithCustomerExcludingAssessedTax, gross_profit=GrossProfit, cogs=CostOfRevenue, sga=SellingAndMarketingExpense+GeneralAndAdministrativeExpense, ni=NetIncomeLoss, oi=OperatingIncomeLoss, disc_ops=IncomeLossFromDiscontinuedOperationsNetOfTax, nonop=NonoperatingIncomeExpense, prepaids=PrepaidExpenseAndOtherAssetsCurrent, assets=Assets

| FY end | Revenue | Gross margin | COGS %rev | SG&A %rev | (COGS+SG&A) %rev | NI vs OI gap | Disc ops | Nonop inc |
|---|---|---|---|---|---|---|---|---|
| 2021-03-31 | $3.37B | +54.5% | n/a | +24.8% | n/a | -6.4% | n/a | n/a |
| 2022-03-31 | $3.50B | +56.2% | +43.8% | +29.3% | +73.1% | -11.7% | n/a | n/a |
| 2023-03-31 | $5.35B | +42.7% | +57.3% | +45.3% | +102.6% | +3.5% | n/a | n/a |
| 2024-03-31 | $5.35B | +41.9% | +58.1% | +42.4% | +100.5% | -4.3% | n/a | n/a |
| 2025-03-31 | $5.63B | +54.4% | +45.6% | +45.6% | +91.2% | -2.0% | n/a | n/a |
| 2026-03-31 | $6.66B | +57.2% | +42.8% | +39.7% | +82.5% | -186.2% | n/a | n/a |

## Prepaid battery
- 2024-09-30: prepaids $433M = 3.3% of assets
- 2024-12-31: prepaids $370M = 2.9% of assets
- 2025-03-31: prepaids $403M = 4.4% of assets
- 2025-06-30: prepaids $428M = 4.4% of assets
- 2025-09-30: prepaids $356M = 3.5% of assets
- 2025-12-31: prepaids $345M = 3.4% of assets
- 2026-03-31: prepaids $302M = 3.2% of assets
- 2026-06-30: prepaids $404M = 4.5% of assets
- YoY change at 2026-06-30: -5.5%
- Prepaids / latest FY SG&A: 15%

## Battery flags
- COGS_SWING 2023-03-31: COGS % of revenue moved +13.5% YoY — weak cost control / moat evidence.
- COGS_SWING 2025-03-31: COGS % of revenue moved -12.5% YoY — weak cost control / moat evidence.
- NI_OI_GAP 2026-03-31: net income differs from operating income by -186.2% — noncore items are material to earnings quality.
- PREPAID_QOQ 2026-06-30: prepaids moved +34.0% QoQ — check for expense deferral.

## Filing freshness
- Pass 1 analysis date: 2026-10-12; latest period pass 1 used: 2026-03-31
- Newer periodic filing since pass 1: NONE — pass 1 data is filing-current.
- Material 8-Ks since pass 1: none
```

**Freshness result:** No newer 10-K/10-Q than pass 1 used and no material 8-Ks since the 2026-10-12 analysis date. No TTM recompute is triggered — and pass 1's base was already TTM through Q1 FY2027 (Jun 30, 2026), the latest filed quarter. Base stands at −$0.07/sh.

### Battery flags — resolved in writing
- **Margin structure / moat evidence:** Gross margin recovered from 41.9% (FY2024) to 54.4% (FY2025) to 57.2% (FY2026) — above the ≥40% durable-advantage rule of thumb and sector-appropriate for a publisher with owned IP. But the level is mix-driven (console/owned-IP vs mobile), not a stable cost moat: the FY2023–24 collapse to ~42% on Zynga consolidation shows the consolidated margin is a weighted average of two very different businesses. Consistent with pass 1's moat 6 — real franchise pricing power, diluted at company level. No moat change.
- **COGS_SWING FY2023 (+13.5pp to 57.3%):** Mix, not cost-control failure in the legacy business — Zynga closed May 2022, consolidating a full year of mobile cost of revenue (platform fees, acquired-intangible amortisation in cost of revenue) into FY2023. Revenue +52.8% the same year confirms a basis break (pass 1 flagged BASIS_BREAK_SUSPECT in substance). Resolved: acquisition mix, already reflected in pass 1.
- **COGS_SWING FY2025 (−12.5pp to 45.6%):** The mirror image — cost of revenue fell as impairment/amortisation load in cost of revenue dropped and the 2024 cost-reduction plan bit. Note SG&A % *rose* the same year (42.4% → 45.6%), so part of the gross-margin "improvement" is split migration (see next point); the rest is the absence of FY2024's charges. Not evidence of a newly durable cost advantage.
- **SG&A-vs-COGS split test (IBM pattern):** Combined (COGS+SG&A)/revenue: 73.1% (FY22) → 102.6% (FY23) → 100.5% (FY24) → 91.2% (FY25) → 82.5% (FY26). The combined series falls in both FY2025 and FY2026, so the improvement is not pure presentation optics — costs genuinely came down (2024 Plan + no repeat of FY24 charges). But the FY2025 split move (COGS −12.5pp while SG&A +3.2pp) means the *gross-margin* line alone overstates FY2025 progress; the combined series is the honest one, and on the combined series FY2026 (82.5%) is still far worse than pre-Zynga FY2022 (73.1%). Trust the combined series; it supports pass 1, not a revision.
- **NI_OI_GAP FY2026 (−186.2%):** Percentage artefact of a near-zero denominator, exactly the caution in the method: operating income was −$104M, net income −$298M — a −$194M absolute gap (~2.9% of revenue) from interest/other and the $100M tax charge, not a noncore item carrying earnings. In FY2024/25 the gaps were small in % terms (−4.3%, −2.0%) precisely because both NI and OI were dominated by the goodwill impairments. OE is built on OCF with SBC subtracted explicitly, so none of this touches the base. Resolved: no earnings-quality hit beyond what pass 1 documented.
- **PREPAID_QOQ 2026-06-30 (+34.0%, $302M → $404M):** Not the deferral pattern. The full pattern requires prepaids spiking *while earnings improve and OCF weakens*, reversing later. Here: (1) YoY at Jun 30 prepaids are *down* 5.5% ($404M vs $428M); the QoQ jump is off the fiscal-year-end low ($302M was the lowest print in the battery) and Q1 prepaids were also the annual high in 2025 ($428M) — a seasonal build into the launch/marketing year; (2) earnings did not improve — Q1 FY27 net loss widened to −$34.1M; (3) prepaids are 4.5% of assets and 15% of FY SG&A — too small to manufacture the OE story either way. Resolved: seasonal, no deferral finding.
- **Discontinued ops:** Battery shows n/a in every year — no discontinued operations on the books. No divestiture-optics comparison is triggered (the Private Division disposal in the Zynga-era portfolio cleanup was never presented as discontinued ops and left no discontinued-ops line or stranded-cost disclosure that moves OE).

### Judgment checks
- **Divestiture optics:** No divestiture/discontinued-ops presentation in the filing history the battery covers. Nothing to compare pre/during/post; no optics finding.
- **Noncore income reconstruction:** Core vs reported — the material noncore items in the window are the goodwill impairments (−$2,342M FY24, −$3,545M FY25, $0 FY26) and acquired-intangible amortisation, both non-cash and both *below* the OCF line that OE is built from. Interest/other (−$194M gap in FY26) is ~3% of revenue. Noncore items therefore do not carry the base — if anything they flatter reported NI relative to cash reality in impairment years, and OE already excludes them. No core-OE rebuild changes the sign: TTM OE is −$13.1M on OCF alone. Resolved: base is already core-cash.
- **Capitalized-cost shifting (WorldCom pattern) — the closest thing to a hard look, and it cuts AGAINST the stock, not for it:** Take-Two capitalises software development costs, and the balance is growing faster than the P&L expense: capitalised software (internally developed, noncurrent) was $1,845.6M at Mar 31, 2025 and $2,169.2M at Dec 31, 2025 (10-Q disclosure), i.e. the capitalised balance grew ~$324M in nine months heading into the GTA VI launch. The engine's capex is PP&E only ($162.7M TTM); capitalised development spend is not deducted in conservative OE. That means pass 1's OE is, if anything, *generous* — a fuller cash-cost OE that also deducted net capitalised development would be more negative, not less. Software-development impairment charges also recur in small size almost every quarter ($0.4M–$11.5M per quarter in FY2025–26 disclosures, plus the $43.4M cancelled-title impairment in Q1 FY27), confirming capitalised projects regularly fail to earn their carrying value. Two legs of the pattern (capitalised balances growing faster than near-term revenue in the pre-launch window; earnings/OCF weak) are present, but the direction of any adjustment deepens the F — it cannot produce a material finding that changes the score upward, and Tier F is already the floor. Logged as corroboration, not a change.
- **Honest OE definition:** The **total-capex (conservative) definition is the honest one**, as pass 1 held. The maintenance version (−$1,584M in FY2026) is distorted by the engine's ΔNWC swing (+$1,321M) and by NI carrying impairment/amortisation residue; it overstates the damage. Even the honest conservative figure is generous for the reason above (capitalised development not deducted). FY2026 capex of $163M on $6.66B of revenue is genuinely light — capex is not where this P&L leaks; SBC and the Zynga-era cost base are.

## Targeted research (post-filing / segment / SBC hunts)
1. **Segment masking (both directions):** Q1 FY2027 (already the latest filing, and the one pass 1's TTM uses) — consolidated bookings −3% to $1.39B mask a split: console bookings +11% to $525.2M while mobile bookings fell 7% to $739.5M (mobile still ~53% of bookings); recurrent consumer spending was 84% of Q1 bookings, −1% YoY. So the "growing core dragged by a legacy line" pattern exists in miniature — console (GTA Online, NBA 2K) growing, mobile shrinking — exactly as pass 1's moat AGAINST case stated. It does not change the base: the growing side is already fully in the consolidated OCF that produced −$13.1M of TTM OE. Sources: Q1 FY27 earnings coverage (CryptoCompass/Blockonomi summaries of the Aug 7, 2026 release; Insider Monkey, Oct 2026).
2. **One-offs that recur:** The "one-off" label fails in both directions and pass 1 had it right. Goodwill impairments recurred two years running ($2.34B + $3.55B) before stopping in FY2026 — structural evidence of Zynga overpayment, not noise — and small software-development impairments plus 2024-Plan restructuring charges recur quarter after quarter, joined in Q1 FY27 by a fresh $43.4M impairment on a cancelled unannounced title. All are non-cash and excluded from OE by construction; their recurrence is moat/quality evidence (already in the moat 6 AGAINST case), not a base adjustment.
3. **Post-filing events:** None material since pass 1 (one day ago) and none missed by pass 1: FY2027 guidance was *reiterated, not raised*, at Q1 — bookings $8.0–8.2B, GAAP revenue $7.9–8.1B, GAAP net income $104–143M — despite "unprecedented" GTA VI pre-orders (opened Jun 25, 2026; launch Nov 19, 2026 on PS5/Xbox Series X|S reaffirmed in October coverage). Management also flagged console hardware price/memory-cost headwinds on the Q1 call. Guidance standing still after pre-orders opened supports pass 1's refusal to capitalise the launch. Sources: Take-Two FY2027 outlook in the Q4 FY2026 release (ir.take2games.com); MarketBeat Q1 FY27 guidance coverage; Motley Fool, Oct 10, 2026 (stock ~$200, forward P/E ~29×, GTA V >230M units as the bar).
4. **SBC / dilution trajectory:** Worse than flat, consistent with pass 1's DILUTION resolution — not a contradiction of it. FY2027 guidance embeds stock-based compensation of ~$427M in the pre-tax adjustments (vs $350.6M TTM actual) and a guided diluted share count of 189.7M for FY2027, up from 183.9M (FY2026 actual) and 186.2M (Q1 FY27). Dilution is guided to continue at ~3%/yr with SBC rising; pass 1's −4.8pp share-count growth adjustment was, if anything, mild. No revision warranted — the trajectory confirms the F rather than undermining it. Source: Take-Two FY2027 outlook table, Q4 FY2026 earnings release (ir.take2games.com).

## Why the score stands
Every hunt landed on pass 1's side: filing-current (no new filing/8-K), TTM base already through the latest quarter and negative, segment split and recurring impairments already embedded in the moat and flag resolutions, SBC/dilution guided worse not better, and the one forensic pattern with real teeth (capitalised development costs excluded from capex) makes true owner's earnings *lower* than the −$0.07/sh base, not higher. There is no quantified evidence for any input change: base OE, moat 6, probabilities, and Tier F all stand. The known catalyst that can rewrite this — the GTA VI launch quarter filing (Q3 FY2027 10-Q) — remains a future re-run trigger, exactly as pass 1 stated.

**Queue/reporting:** score.json untouched; no Tier S/A crossing (F → F). Silent.
