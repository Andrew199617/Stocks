# SNAP — Second pass (2026-10-13)

**Verdict: NO MATERIAL FINDING — score stands. Tier F, base OE (TTM through Q2 2026) −$0.1941/share, moat 4/10, price at pass 1 $6.53. score.json not touched.**

Pass 1's load-bearing assumptions, attacked in order: (1) the conservative (total-capex) OE base is the honest one and is negative under every window (FY2025 −$0.342, 3-yr median −$0.496, filing-derived TTM −$0.194); (2) the blocker is SBC — $1,030.8M TTM vs $919.1M TTM OCF; (3) the maintenance-version positive (+$0.077 TTM) is an artifact of a marketable-securities drawdown inside ΔNWC and was correctly rejected; (4) moat 4/10 with growth coming from low-ARPU Rest of World and the direct-revenue leg; (5) scenario probabilities are moot — the engine cannot project a negative base, by v4 design.

## Filing freshness (step 0)

Forensic pull reports **no newer 10-K/10-Q since pass 1's 2026-10-12 analysis and no material 8-Ks** (full output below). Pass 1 already built its base filing-direct as a TTM override through Q2 2026 (the 10-Q period ended 2026-06-30), so there is no stale base to recompute: the TTM base of −$325.285M / −$0.1941/share stands as the freshest filing-derived number available. No recompute was triggered.

## Forensic battery — full output

```
# Forensic battery — SNAP (CIK 1564408)
Tags used: revenue=RevenueFromContractWithCustomerExcludingAssessedTax, gross_profit=None, cogs=CostOfRevenue, sga=SellingAndMarketingExpense+GeneralAndAdministrativeExpense, ni=NetIncomeLoss, oi=OperatingIncomeLoss, disc_ops=None, nonop=OtherNonoperatingIncomeExpense, prepaids=PrepaidExpenseAndOtherAssetsCurrent, assets=Assets

| FY end | Revenue | Gross margin | COGS %rev | SG&A %rev | (COGS+SG&A) %rev | NI vs OI gap | Disc ops | Nonop inc |
|---|---|---|---|---|---|---|---|---|
| 2020-12-31 | $2.51B | n/a | +47.2% | +43.3% | +90.4% | -9.6% | n/a | $15M |
| 2021-12-31 | $4.12B | n/a | +42.5% | +36.5% | +79.0% | +30.5% | n/a | $240M |
| 2022-12-31 | $4.60B | n/a | +39.4% | +45.0% | +84.5% | -2.5% | n/a | $-43M |
| 2023-12-31 | $4.61B | n/a | +45.9% | +43.0% | +88.9% | +5.4% | n/a | $-42M |
| 2024-12-31 | $5.36B | n/a | +46.1% | +37.0% | +83.1% | +11.4% | n/a | $-17M |
| 2025-12-31 | $5.93B | n/a | +45.0% | +33.7% | +78.7% | +13.5% | n/a | $69M |

## Prepaid battery
- 2024-09-30: prepaids $201M = 2.6% of assets
- 2024-12-31: prepaids $182M = 2.3% of assets
- 2025-03-31: prepaids $213M = 2.8% of assets
- 2025-06-30: prepaids $226M = 3.1% of assets
- 2025-09-30: prepaids $235M = 3.1% of assets
- 2025-12-31: prepaids $272M = 3.5% of assets
- 2026-03-31: prepaids $269M = 3.6% of assets
- 2026-06-30: prepaids $310M = 4.1% of assets
- YoY change at 2026-06-30: +36.8%
- Prepaids / latest FY SG&A: 15%

## Battery flags
- COGS_SWING 2021-12-31: COGS % of revenue moved -4.7% YoY — weak cost control / moat evidence.
- NI_OI_GAP 2021-12-31: net income differs from operating income by +30.5% — noncore items are material to earnings quality.
- COGS_SWING 2022-12-31: COGS % of revenue moved -3.1% YoY — weak cost control / moat evidence.
- COGS_SWING 2023-12-31: COGS % of revenue moved +6.4% YoY — weak cost control / moat evidence.
- PREPAID_YOY 2026-06-30: prepaids up +36.8% YoY — verify against OCF trend (earnings up + OCF down + prepaids up = deferral pattern).

## Filing freshness
- Pass 1 analysis date: 2026-10-12; latest period pass 1 used: 2025-12-31
- Newer periodic filing since pass 1: NONE — pass 1 data is filing-current.
- Material 8-Ks since pass 1: none
```

## Battery flags — resolved in writing

- **Margin structure / COGS_SWING (2021 −4.7pp, 2022 −3.1pp, 2023 +6.4pp).** The battery's gross-profit tag is None, so gross margin is implied as 100 − COGS%: 52.8% (2020), 57.5% (2021), 60.6% (2022), 54.1% (2023), 53.9% (2024), 55.0% (2025) — and Q2 2026 printed 58% in earnings coverage. That clears the ≥40% durable-advantage rule of thumb for an ad/subscription platform, so the level is moat-supportive. The swings are real but explained: COGS here is dominated by infrastructure (hosting/AI) costs, which Snap itself just guided *up* for FY2026 ($1.65–1.70B vs $1.60–1.65B prior) to support AI/ML — the 2023 spike coincides with the ad-market trough (revenue +0.1% that year, a denominator effect), not a reclassification. Verdict: volatility is a modest moat negative already consistent with 4/10; it does not touch the OE base, which is built from OCF, not gross margin.
- **SG&A-vs-COGS split test (IBM pattern).** No optics found. The combined (COGS+SG&A)/revenue series is *not* flat while the split migrates — it moves materially: 90.4% → 79.0% → 84.5% → 88.9% → 83.1% → 78.7%. The recent improvement is driven by SG&A falling 43.0% → 37.0% → 33.7% of revenue (2023→2025) while COGS% stayed roughly flat (45.9% → 46.1% → 45.0%). If costs were being reclassified into COGS to flatter SG&A, COGS% would have risen to offset; it did not. The SG&A leverage is real (headcount −9% YoY to 4,723 after the April 2026 restructuring, per Q2 coverage), and the combined series confirms it.
- **NI_OI_GAP 2021 (+30.5%, nonop +$240M).** One year only. Operating income in 2021 was −$702M (not near zero, so the % is meaningful), and the gap is the +$240M nonoperating line that year. Every later year is small (−2.5%, +5.4%, +11.4%, +13.5%) with nonop between −$43M and +$69M against operating losses of −$0.5B to −$1.4B. Noncore items are not carrying reported earnings in any recent year — and they cannot carry the OE base in any case, because OE is OCF − capex − SBC, and OCF here is *positive only because of* the ~$1B SBC add-back, which the base then subtracts explicitly. Pass 1's resolution of the NI/OCF divergence stands.
- **PREPAID_YOY (+36.8% at 2026-06-30).** Deferral pattern NOT present. The pattern requires earnings improving *while OCF weakens*; here OCF strengthened over the same window (TTM OCF $919.1M vs FY2025 $656.2M) alongside the narrowing loss. Scale is also immaterial: prepaids are 4.1% of assets and 15% of latest-FY SG&A; the YoY increase is ~$84M ($226M → $310M) against $6,351M TTM revenue and a −$325M TTM OE gap — even capitalizing the entire increase the wrong way would not flip the sign of the base. No hard forensic hit.
- **Discontinued ops.** Battery tag is None / n/a in every year; no discontinued-ops or held-for-sale line in the history pass 1 used. Nothing to resolve.

## Judgment checks

- **Divestiture optics.** No divestiture, held-for-sale line, or discontinued operation appears in the filings covered. There is no pre/during/post comparison to run; pass 1's BASIS_BREAK check (no material M&A/divestiture/restatement) is corroborated by the battery's empty disc-ops column. Not applicable — stated plainly rather than skipped.
- **Noncore income reconstruction.** Core = the advertising + direct-revenue business; its operating result is a *loss* in every year (FY2025 operating income −$532.2M on $5,931.4M revenue). Net income (−$460.5M FY2025) is actually *better* than operating income, i.e. noncore (nonop +$69M in 2025, plus interest/tax lines) slightly flatters the GAAP bottom line rather than carrying it. Rebuilding base OE on core numbers alone would make the base *more* negative, not less. Noncore is not material to the base; no rebuild.
- **Capitalized-cost shifting (WorldCom pattern).** Not present. Capex was $69.9M / $129.3M / $211.7M / $194.8M / $219.0M for 2021–2025 — growth stalled after 2023 while revenue kept growing (capex 3.7% of revenue in 2025, roughly at the D&A level of $163.6M), so capex is not outrunning revenue. SG&A *dollars* are not collapsing into a capitalized balance; SG&A% fell on genuine headcount/restructuring cuts. Earnings do not outrun OCF for an unexplained reason — the NI-vs-OCF gap is fully explained by the SBC add-back, as pass 1 documented. No two legs of the pattern hold together.
- **Honest OE definition.** The **total-capex conservative definition** is the honest one, confirming pass 1. Snap is asset-light (capex ≈ D&A), so the two definitions differ mainly through the maintenance formula's ΔNWC term — and that term is corrupted here because Snap's current assets include its marketable-securities portfolio, so portfolio drawdowns ($266.2M Jun-2025 → Jun-2026) masquerade as operating NWC releases. The maintenance version's only positive reading (+$0.077/share TTM) rests on counting investment liquidation as earnings. Rejected again, for the same documented reason.

## Targeted research — what pass 1 might have missed

1. **Segment growth masked by consolidated figures.** Already in pass 1 and re-verified: Q2 2026 advertising revenue $1.28B, +9% YoY, vs "other" revenue (Snapchat+, Memories Storage, Lens+) $316M, +85% YoY, ~20% of the quarter, with <3% of 971M MAU paying. There is no sunset/legacy segment dragging a hidden core, and no dying segment flattering the total — the mix story is two live legs growing at very different rates, and pass 1 priced the moat (4/10) on exactly that. Regional detail from Q2 coverage cuts the same way pass 1 had it: DAU +5% globally but North America −7% / Europe −2%, all net growth in $1.00-ARPU Rest of World vs $10.26 in North America. Nothing here changes a base that is negative *in aggregate* — segment reallocation cannot create owner's earnings the consolidated OCF statement doesn't have.
2. **One-offs that recur.** The $128.5M Q2 2026 restructuring charge is the latest in a repeated pattern (Snap has restructured repeatedly, including an April 2026 program guided at $95–130M of Q2 charges with >$500M of annualized cost cuts claimed). That recurrence actually *supports* pass 1's refusal to normalize it away — and pass 1 already showed the verdict is insensitive either way: adding back the entire $128.5M still leaves TTM OE at −$196.8M. No finding.
3. **Post-filing / post-pass-1 events.** Pass 1 ran 2026-10-12, one day before this pass, and the forensic pull confirms no new periodic filing and no material 8-K since. The items in current coverage predate or match pass 1's window: Q3 2026 guidance ($1.70–1.74B revenue, Adj. EBITDA $300–350M), SBC guided flat at ~$1.05B for 2026, Specs launch (Sept 16 event, $2,195, fall availability, spend inside the existing opex guide), and the new multi-year dilution-management program targeting a stable fully diluted count in 2027. One item pass 1 did not name: activist Blue Duck Capital's open letter urging Snap to raise external capital for Specs, claiming ~$500M/yr of Specs spend and a $5B+ Specs value. It is an activist estimate, not a filing figure; under the second-pass standing caution, stripping out asserted "growth spend" is a sensitivity only, and there is no filing-concrete evidence to rebuild the base on a Specs-excluded core. Even taken at face value it describes future financing optionality, not current owner's earnings. Not a material finding.
4. **SBC / dilution trajectory.** Unchanged and confirming pass 1: SBC guided ~$1.05B for 2026 (H1 2026 actual $513.2M, on pace), buybacks of $601.0M in H1 2026 running to offset grants, diluted share count CAGR +1.76%/yr in the engine window. Management's Q2 framing (fully diluted count growth limited to ~2% over five years, stable count targeted for 2027 under the new program) is a plan about the *count*, not a reduction in the SBC *cost* the base subtracts. The trajectory pass 1 baked in stands.
5. **Thin flag resolutions re-checked.** The two pass-1 judgments most open to attack were the HIGH_NET_DEBT non-fire (corrected net debt ~$874.8M at Q2 2026 counting marketable securities — corroborated by Q2 coverage putting cash + marketable securities at ~$2.7B) and the maintenance-base rejection (re-argued above from the battery's own data). Both hold.

## Why the score stands

Every conservative base is negative (FY −$0.342, median −$0.496, TTM −$0.194/share), the forensic battery produced no hard hit (no deferral pattern, no cost shifting, noncore flatters NI only slightly and cannot touch an OCF-based base), freshness is current, and the research directions that could have rescued the name — segment mix, restructuring add-back, Specs spend, the activist letter — were each quantified or sourced and none flips the sign of owner's earnings while SBC runs at ~$1.03–1.05B/yr against ~$919M of TTM OCF. Tier F stands, confidence medium, exactly as pass 1 left it. The trigger pass 1 named remains the right one: two consecutive filings with TTM conservative OE > 0.

## Sources

- Forensic battery + filing freshness: `python3 ~/workspace/stocks/_system/forensic_pull.py SNAP` (SEC EDGAR, CIK 1564408), run 2026-10-13 — full output pasted above.
- Pass 1 folder: analysis.md, score.json, dcf_numbers.json, financials_history.csv in ~/workspace/stocks/SNAP/ (all figures cross-checked against them).
- Q2 2026 segment split, DAU/ARPU, Q3 guidance, SBC ~$1.05B guide, TTM OCF $919M / FCF $706M: Snap Q2 2026 prepared remarks via StockTitan 8-K summary (https://www.stocktitan.net/sec-filings/SNAP/8-k-snap-inc-reports-material-event-f2b0aa190ccd.html) and Eulerpool transcript summary via ad-hoc-news (https://www.ad-hoc-news.de/boerse/corporate-news/snap-stock-gains-1-70-percent-as-q2-growth-meets-a-tougher-test/70236654).
- Restructuring recurrence, headcount, gross margin 58%: MLQ / TechTimes Q2 2026 coverage (https://www.techtimes.com/articles/322885/20260803/snap-q2-2026-earnings-prove-restructuring-worked-stock-jumps-ebitda-surge.htm).
- Blue Duck Capital Specs letter (~$500M/yr claimed Specs spend, $5B+ claimed value): PR Newswire release (https://www.prnewswire.com/news-releases/blue-duck-capital-urges-snap-inc-board-of-directors-to-raise-external-capital-for-specs-to-unlock-sum-of-the-parts-value-302899724.html).
- Subscriber penetration <3% of MAU: Trefis, 2026-10-12 (https://www.trefis.com/stock/snap/articles/618338/why-every-snap-investor-is-looking-at-this-one-number/2026-10-12).
