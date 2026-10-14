# CMPS — COMPASS Pathways plc — Second pass
Date: 2026-10-13
Pass 1: 2026-10-12, engine v4, Tier F, base OE (TTM through Q2 2026) −$1.4194/share, moat 3/10, price $11.60, weighted IRR/IV n/a (no positive OE in any base).

## Verdict: NO MATERIAL FINDING — score stands
Pass 1's load-bearing assumptions were: (1) owner's earnings are negative under every defensible base (latest FY −$1.83/sh, 3-yr median −$2.06/sh, filing-derived TTM −$1.42/sh), so Tier F is not a base-choice artifact; (2) GAAP net income is unusable because non-cash warrant fair-value marks dominate it, while the OCF-based OE is clean of them; (3) dilution is financing-driven (Feb 2026 raise), not SBC-driven (SBC only ~$13M/yr TTM); (4) the equity is a binary FDA-approval option, not an earnings stream — the OE DCF is a documented poor fit for pre-revenue biotech. Every check below either confirms those assumptions or is immaterial to them. There are no segments to unmask (single asset, $0 revenue in every period), no post-pass-1 filing, and no event since pass 1 that creates revenue or positive OE.

## Filing freshness + forensic battery (step 0, every run)

Full output of `python3 ~/workspace/stocks/_system/forensic_pull.py CMPS`:

```
# Forensic battery — CMPS (CIK 1816590)
Tags used: revenue=None, gross_profit=None, cogs=None, sga=None, ni=NetIncomeLoss, oi=OperatingIncomeLoss, disc_ops=None, nonop=NonoperatingIncomeExpense, prepaids=PrepaidExpenseAndOtherAssetsCurrent, assets=Assets

| FY end | Revenue | Gross margin | COGS %rev | SG&A %rev | (COGS+SG&A) %rev | NI vs OI gap | Disc ops | Nonop inc |
|---|---|---|---|---|---|---|---|---|---|
| 2020-12-31 | n/a | n/a | n/a | n/a | n/a | -17.4% | n/a | $-9M |
| 2021-12-31 | n/a | n/a | n/a | n/a | n/a | +13.8% | n/a | $12M |
| 2022-12-31 | n/a | n/a | n/a | n/a | n/a | +17.1% | n/a | $19M |
| 2023-12-31 | n/a | n/a | n/a | n/a | n/a | +13.5% | n/a | $19M |
| 2024-12-31 | n/a | n/a | n/a | n/a | n/a | +13.0% | n/a | $25M |
| 2025-12-31 | n/a | n/a | n/a | n/a | n/a | -60.8% | n/a | $-111M |

## Prepaid battery
- 2024-09-30: prepaids $26M = 10.6% of assets
- 2024-12-31: prepaids $36M = 16.8% of assets
- 2025-03-31: prepaids $45M = 14.1% of assets
- 2025-06-30: prepaids $54M = 18.4% of assets
- 2025-09-30: prepaids $56M = 21.9% of assets
- 2025-12-31: prepaids $42M = 19.7% of assets
- 2026-03-31: prepaids $44M = 8.4% of assets
- 2026-06-30: prepaids $42M = 8.3% of assets
- YoY change at 2026-06-30: -22.5%

## Battery flags
- NI_OI_GAP 2022-12-31: net income differs from operating income by +17.1% — noncore items are material to earnings quality.
- NI_OI_GAP 2025-12-31: net income differs from operating income by -60.8% — noncore items are material to earnings quality.

## Filing freshness
- Pass 1 analysis date: 2026-10-12; latest period pass 1 used: 2025-12-31
- Newer periodic filing since pass 1: NONE — pass 1 data is filing-current.
- Material 8-Ks since pass 1: none
```
### Freshness resolution
No newer 10-K/10-Q than pass 1 used, and no material 8-K since the 2026-10-12 analysis date. Pass 1 already incorporated the newest periodic filing — the Q2 2026 10-Q (filed with the Aug 5, 2026 results) — via its TTM override, so there is no stale base to recompute. The TTM base stands: OCF −$161.136M − SBC $12.982M − capex ~$0 = OE −$174.118M = −$1.42/share.

### Battery flag resolutions
- **Margin structure / COGS % / SG&A-vs-COGS split:** Not applicable, and that is itself the finding — revenue, gross profit, COGS and SG&A tags are all None because the company has never reported revenue. There is no gross margin to judge against the ≥40% durable-advantage rule of thumb, and no COGS/SG&A split that could migrate. This is consistent with pass 1's moat 3/10: no demonstrated pricing power or cost advantage exists yet. No optics issue is possible in a cost structure that is simply R&D + G&A against zero sales.
- **NI_OI_GAP 2022 (+17.1%) and 2025 (−60.8%):** Resolved — same root cause pass 1 identified. The gaps are nonoperating items, dominated by warrant-liability fair-value marks (2025 nonop −$111M; pass 1 documented the $122.6M non-cash warrant loss in FY2025 vs $0 in 2024) plus R&D tax-credit benefit swings. Operating loss was actually flat (−$179.0M in both FY2024 and FY2025). The pattern repeats in 2026 and confirms the diagnosis: Q1 2026 reported +$91.2M net income only because of a +$130.9M warrant fair-value gain, while Q2 2026 net loss was −$253.8M on a −$201.1M total other-expense line — GAAP NI swings ±$200M+ on marks while operations burn steadily. Conclusion: NI is unusable; the OCF-based OE correctly excludes these non-cash, non-operating marks. No adjustment to the base.
- **Prepaid battery:** The spike is real in % terms (10.6% of assets at 2024-09-30 → 21.9% at 2025-09-30; $26M → $56M absolute) but the deferral pattern does NOT complete. The pattern requires prepaids spiking *while earnings improve and OCF weakens, reversing into expense later*. Here earnings did not improve — operating loss was flat at −$179M and net loss worsened in 2025 — so prepaids flattered nothing. OCF did weaken (−$119.2M → −$157.2M), but a prepaid build is itself a cash outflow inside OCF, so the OCF-based OE is already penalized by it, not flattered. In 2026 the % collapsed to 8.3–8.4% only because the Feb 2026 raise inflated total assets (Q1 2026 balance sheet: cash $466.0M, total assets $531.7M vs $210.3M at FY2025); absolute prepaids were flat ($44.5M at 2026-03-31 vs $41.5M at 2025-12-31 in the Q1 filing), with no reversal-into-expense spike visible. For a company running two Phase 3 trials and pre-launch manufacturing/site preparation, prepaid clinical/CRO and launch costs are the ordinary explanation. Not a hard forensic hit.
- **Discontinued ops:** None reported in any year (tag None throughout). No divestiture, held-for-sale line, or discontinued operation exists, so the pre/during/post divestiture-optics comparison has nothing to attach to — stated plainly: no divestiture optics, real or accounting.
- **Noncore income reconstruction (judgment):** Core = operating result, because there is no revenue at all: core operating loss −$179.0M (FY2025), essentially identical to FY2024. Everything below that line — warrant marks, interest, R&D tax credits, FX — is noncore by construction, and in 2025 it was materially negative (−$111M nonop), not carrying the business. The OE base is built on OCF, which already excludes the non-cash warrant marks, so the base is already a core number. Rebuilding the base on core figures changes nothing: still deeply negative. Noncore is NOT carrying the base — no material finding.
- **Capitalized-cost shifting (judgment, WorldCom pattern):** No legs present. Capex is ~$0 (no tagged PPE purchases in FY2024/FY2025; PPE net is negligible and disappears from the FY2025 balance sheet), there is no growing capitalized-software balance, and earnings do not outrun OCF — both are deeply negative and OCF (−$157.2M) is actually better than NI (−$287.9M) in FY2025. Nothing is being shifted off the income statement into the balance sheet.
- **Honest OE definition:** Pass 1's **conservative (total-capex) definition** is the honest one, confirming pass 1. The maintenance version's FY2025 figure (−$91.5M) is flattered by a −$196.1M ΔNWC swing driven by warrant-liability presentation, not operations. It makes no verdict difference — both definitions are deeply negative in every year.

## Targeted research (what a standardized pass misses)
- **(a) Segment masking:** Impossible here. CMPS reports no segments and $0 revenue in the Q2 2026 release (revenue 0, EPS −$1.88, reported Aug 5, 2026). There is one asset (COMP360 for TRD), one late-stage follow-on (PTSD), and no legacy/discontinued line dragging or flattering a consolidated total. The Unity-style masking case cannot occur with zero consolidated revenue.
- **(b) Recurring "one-offs":** The only recurring non-operating item is the warrant fair-value mark, which recurs every quarter in both directions (+$130.9M gain Q1 2026; −$205.6M loss implied in Q2 2026 per pass 1 / −$201.1M total other expense). Pass 1 did not "normalize it away" incorrectly — it correctly excluded it from OE because it is non-cash and non-operating, and it will keep recurring until the warrants are exercised/expire. It does not affect cash burn or the OE base. No other one-off was found that is actually structural; the operating burn itself (~$179M/yr operating loss) is already fully in the base, un-normalized.
- **(c) Post-filing / post-pass-1 events:** Nothing after pass 1's 2026-10-12 analysis date, and nothing material in the window pass 1 might have missed: the rolling NDA remains on track for final submission in Q4 2026 with an H1 2027 launch target, restated at TD Cowen's neuropsychiatry summit (Sep 25–26, 2026 coverage) and in the Sep 9, 2026 COMP005 Part C extension release (average 13-point MADRS reduction at Week 52 after an additional 25 mg dose; 40–45% response in the first six weeks of Part C). No guidance change, M&A, customer win/loss, or product sunset. Even a clean approval would not change the OE verdict today — pass 1 already stated the tier changes only after approval plus 2–3 years of post-launch filings showing revenue covering the ~$180M/yr spend.
- **(d) SBC / dilution trajectory:** Confirms pass 1, hard. SBC stays small (TTM $12.982M). The dilution is warrant/equity financing: the Feb 2026 financing (1,250,000 prefunded warrants issued, plus 19,898,829 prefunded warrants issued on exercise of 2025 ADS warrants, per the FY2025 10-K) took shares outstanding from 96,085,785 at 2025-12-31 to 134,923,295 at 2026-03-31, and weighted diluted shares to 135,039,810 in Q2 2026 — exactly the counts pass 1 used. Cash consequently rose to $433.3M at Q2 2026 (guided to fund operations "well beyond launch and into 2028"), matching pass 1's $382.6M net-cash update. The only newer equity event, the Oct 2, 2026 inducement grants (121,800 options + 58,000 RSUs to one senior hire; 97,100 options + 46,200 awards to 10 new non-executive employees, ~0.32M shares total ≈ 0.2% of the count), is immaterial and pre-dates pass 1's analysis date. Pass 1's expectation of further raises before OE breakeven stands, but no new raise since Q2 changes the base.
- **(e) Thin pass-1 flag resolutions re-examined:** NI_OCF_DIVERGENCE (warrant marks — re-verified against Q1/Q2 2026 filings above), DILUTION (re-verified share counts above), STALE_FY (freshness check: no newer filing). All three hold up on the primary sources.

## Why the score stands
Tier F rests on an arithmetic fact no check disturbed: owner's earnings are negative in all 7 years of history under both OE definitions and under the latest-FY, 3-yr-median, and TTM bases, and there is still no revenue, no segment, and no post-filing event that creates a positive base to project. score.json is NOT touched.

## Sources
- Forensic battery + filing freshness: `forensic_pull.py CMPS` output above (EDGAR, CIK 1816590).
- Pass 1 folder: analysis.md, score.json, dcf_numbers.json, financials_history.csv (~/workspace/stocks/CMPS/).
- Q2/H1 2026 results release (Aug 5, 2026): revenue $0, net loss −$253.8M Q2 / −$162.6M H1, weighted shares 135,039,810 Q2 / 122,679,123 H1, cash $433M, runway into 2028, rolling NDA final submission Q4 2026, launch H1 2027 — via Business Wire release reproduced at markets.financialcontent.com and StockTitan summary.
- Q1 2026 results / 10-Q balance sheet: net income +$91.2M on +$130.9M warrant fair-value gain; prepaid expenses $44,478K at 2026-03-31 vs $41,503K at 2025-12-31; shares outstanding 134,923,295 vs 96,085,785; cash $466,010K — via Business Wire release reproduced at markets.financialcontent.com.
- Feb 2026 prefunded warrants (1,250,000 issued; 19,898,829 on 2025 warrant exercise): FY2025 10-K text via stocklight.com.
- Sep 2026 events: TD Cowen summit NDA-on-track coverage (defenseworld.net, Sep 26, 2026); Sep 9, 2026 Part C extension data and Oct 2, 2026 inducement grants (ad-hoc-news.de summary).
