# CFG — Citizens Financial Group, Inc.
v5 run, 2026-10-14. In scope (market cap $26.851B at $61.46, nasdaq_quote_api). **Finance sector — the OE/capex DCF fits banks poorly; confidence is low by rule, and the tier is a screen result, not a bank valuation.**

All figures below are copied from dcf_numbers.json, financials_history.csv, ttm.json, or the FY2025 10-K cash-flow statement — none are recomputed.

## What it is
Large Providence, RI regional bank holding company for Citizens Bank: Consumer Banking and Commercial Banking segments, roughly 1,000 branches concentrated in the Northeast/Midwest plus a fast-growing Private Bank. Q2 2026 (per the company's release): total revenue $2,283M (+12% YoY), net income $587M (+35% YoY), diluted EPS $1.30 (+41% YoY), NIM 3.17% (+22bp YoY), ROTCE 13.9%, period-end deposits $185.6B and loans $147.5B, spot loan-to-deposit ratio 79.5%, CET1 10.4%, tangible book value $38.29/share. FY2026 guidance given with Q4 2025 results: NII up 10-12%, NIM expanding toward 3.25% in Q4 2026, spot loans up 3-5%, noninterest income up 6-8%, expenses up 4.5%, net charge-offs in the mid-to-high 30s bp, $700-850M of buybacks, and a path to 16-18% ROTCE by end-2027.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $2,211,000,000; capex $174,000,000 — by override, see OVERRIDE; SBC $120,000,000 (AllocatedShareBasedCompensationExpense, always a real cost).
- **Conservative owner's earnings FY2025: $1,917,000,000 = $4.3878/share** (base_oe_latest_per_share $4.3878).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $2,135,000,000 — above the conservative figure; for a bank both definitions are approximations (loan growth, the real "capex" of a bank, is an investing outflow neither captures), which is exactly the sector-mismatch caveat.
- OE positive 5 of the last 5 fiscal years. Net debt as the engine computes it is $11,224,000,000 (long-term debt; the pulled series carries no cash leg for the latest year and deposits — a bank's real funding — are not in this figure at all; see HIGH_NET_DEBT below).

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $2,211,000,000 − prior YTD $673,000,000 + current YTD $963,000,000 = **TTM $2,501,000,000**
- Capex: **TTM $174,000,000**, all three legs filled by the override (see OVERRIDE; the prorated YTD legs cancel in the TTM math)
- SBC: FY $120,000,000 − prior YTD $74,000,000 + current YTD $82,000,000 = **TTM $128,000,000**
- Shares (current-YTD weighted diluted): **428,274,078**
- **TTM OE total $2,199,000,000 → base OE/share $5.1346** (base_source: ttm_json)
- The engine's normalized base (3-yr median, override-filled) is $4.3878/share — the TTM base is used instead per the STALE_FY rule, and it is corroborated by the print run: H1 2026 net income of $517M (Q1) + $587M (Q2) with EPS +41% YoY in Q2. The bank-OCF caveat applies in both directions: OCF adds back the credit provision, so a TTM OCF base in a benign-credit half flatters distributable earnings — handled by the bear-case OE multipliers and the growth recalibration below, and named here rather than hidden.

## OVERRIDE — capex (bounded worker authority, filing kind)
- **The gap:** the preliminary engine run exited 4 with `DATA_GAP:capex` — capex missing for FY2023, FY2024 and FY2025 of the last 3 under every candidate tag in EDGAR companyfacts (filed values through FY2019 came via PaymentsToAcquirePropertyPlantAndEquipment, $126M in FY2019; from FY2020 the filer presents capex only as a single net line in its cash-flow statement, tagged PaymentsForProceedsFromProductiveAssets, which the engine does not read). No tier was emitted, correctly.
- **The decision:** judgment.json carries `capex_override = {value: 174000000, kind: "filing", source: "Form 10-K for fiscal year ended December 31, 2025 (filed 2026-02-12), Consolidated Statements of Cash Flows, investing activities line 'Capital expenditures, net': $174M for FY2025, with $122M for FY2024 and $172M for FY2023 in the same statement (corroborated in EDGAR companyfacts under PaymentsForProceedsFromProductiveAssets with identical values)"}`. In band: $174M vs the last filed value of $126M (override_checks out_of_band: false). The override fills ONLY periods where the tag is absent (capex_tag = "OVERRIDE" for FY2020-FY2025 in financials_history.csv); filed values are never replaced.
- **Known imperfections, stated:** (1) the engine applies the single $174M value to every missing period — for FY2023 it overstates true capex by $2M (true $172M, negligible) and for FY2024 by $52M (true $122M, in the conservative direction: it lowers that year's OE), and likewise overstates FY2020-FY2022 (true net $118M/$124M/$126M); only FY2023-FY2025 touch the median base. (2) The filed figure is *net* of proceeds from sales of premises and equipment, whereas the pre-FY2020 filed values the engine used were gross — the net basis, if anything, understates gross capex, but at this scale (FY2025 capex against OCF of $2,211M) it cannot move the verdict.
- **Measured impact (key_numbers.md, measured by make_score.py on the TTM base actually used, same final configuration with overrides toggled off):** base OE/share $5.54 (no override) → $5.13 (with override), −7.33%; weighted IRR 13.40% → 12.63% (−0.77pp). Tier C either way on this scenario set. Its binary effect is the one that matters: unblocks_tier — without it there is no tier at all.

## Moat: 5/10 — moderate, standard large-regional franchise
Justification: a scaled deposit franchise with improving returns and a real Private Bank growth engine, against a commodity banking product with no structural pricing power, full credit- and rate-cycle exposure, and capital-regulated capital return.
- FOR:
  - Deposit franchise at scale — $185.6B period-end deposits at Q2 2026 funding $147.5B of loans (spot loan-to-deposit 79.5%); consumer deposits are 64% of total deposits vs a ~56% peer average per management
  - Improving returns — ROTCE 13.9% in Q2 2026 vs 11.0% a year earlier, guided path to 16-18% by end-2027; NIM 3.17% in Q2 2026, guided toward 3.25% in Q4 2026
  - Private Bank build-out — spot deposits $17.8B at Q2 2026, contributing $0.15 of Q2 EPS, a fee-rich growth engine inside a commodity business
  - Credit discipline — net charge-offs 0.37% of average loans in Q2 2026, down from 0.48% a year earlier; allowance coverage 1.48% of loans and 152% of nonaccruals (0.97% of loans)
  - Consistent buybacks — diluted shares shrinking 2.9%/yr; $700-850M of repurchases guided for 2026; treasury stock purchased $600M in FY2025 per the 10-K
- AGAINST:
  - Commodity product — deposits and loans are fungible; NIM 3.17% is earned through the cycle, not structural pricing power
  - Credit-cycle exposure — provisions are the swing factor (FY2025 provision for credit losses $608M, added back inside OCF); a recession turns the bear cases fast
  - Capital-constrained growth — CET1 10.4% at Q2 2026, managed to ~10.5%; loan growth, dividends and buybacks compete for the same capital, and Basel III endgame requirements are still evolving
  - Rate sensitivity — the current NIM expansion leans on terminated-swap benefits and fixed-rate asset repricing, tailwinds that fade; deposit repricing pressure is outside management control
  - Efficiency / scale disadvantage — Q2 2026 efficiency ratio 61.1%, still well behind the money-center banks' technology and compliance scale
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — v5 final run (2026-10-14)
Growth recalibration (written reason): the engine's g_base of 10.25% is not usable as printed for this bank. Its revenue series is the contract-revenue tag, which for a bank excludes interest income — the CSV revenue line is $1,635M for FY2025 against total revenue of roughly $2.2-2.3B *per quarter* in 2026, and the series breaks at FY2018 ($5,707M in FY2017 to $1,119M in FY2018) purely on the tag. The blend's revenue CAGRs (5y 8.65%, 3y 7.97%) therefore describe only the fee/contract slice, and the blend discards the OE/share CAGR 2y of −11.98%. Worse, the default offsets put the *bear* start at +5.25% — a bank bear case that never has a credit cycle is not a bear case. Scenario starts were therefore set via offsets (−0.18 / −0.12 / −0.05 / 0.00 / +0.06 vs g_base) to −7.75 / −1.75 / **+5.25** / +10.25 / +16.25%: a mid-single-digit base (earnings power grows with loans guided +3-5%, fees +6-8% and buybacks, roughly nominal-GDP-plus-buyback through a cycle), bears carrying a real provision cycle, and bull/super-bull anchored on the ROTCE-expansion path. Sanity check against prints: Q2 2026 EPS grew +41% YoY and Q1 +47% — recovery prints off a NIM trough with falling charge-offs (0.48% → 0.37%), flattered by swap-termination benefits; even the super-bull start of +16.25% sits well below those prints *with that written reason* — they are a rebound rate, not a start rate for a 15-year fade. Probabilities 10/25/30/25/10; OE multipliers 0.75/0.90/1.00/1.10/1.25. Price $61.46.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -7.75% | 0.75 | Credit cycle turns: provisions spike, NIM compresses, buybacks halt | $20.56 | 6.27% |
| Bear | 25% | -1.75% | 0.90 | Recession-lite: charge-offs normalize up through the guide, earnings shrink before recovering | $31.73 | 8.78% |
| Base | 30% | +5.25% | 1.00 | Mid-single-digit earnings-power growth: loan/fee growth plus buybacks, credit stays mid-cycle | $47.20 | 12.17% |
| Bull | 25% | +10.25% | 1.10 | ROTCE path to 16-18% delivered, loan growth holds, credit stays benign | $63.83 | 15.45% |
| Super bull | 10% | +16.25% | 1.25 | ROTCE target beaten and held; Private Bank compounds; sustained double-digit EPS growth | $92.70 | 20.41% |

- **Probability-weighted: IV@15% $49.38 (−19.66% vs price), IV@12% $65.74, IV@10% $84.01, weighted IRR 12.63%, base-case IRR 12.17%**
- **Tier by numbers: C.** Diagnostics: OE yield 8.35%, terminal value 18.95% of IV@15%, scenario spread 4.51x, net debt 5.00x normalized OE, 9.43 months since FY end.

## Flags — every fragility flag resolved
- **DATA_GAP:capex** (preliminary run): resolved by the filing-sourced override — see OVERRIDE. data_gap_uncovered is empty in the final run.
- **STALE_FY** (FY ended 9.43 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, with its inputs quoted in the Owner's earnings section above (FY / prior YTD / current YTD for OCF, capex, SBC and shares).
- **BUYBACK_TAILWIND** (share count −2.94%/yr): already credited via the +2.94pp share-count adjustment inside g_base; the recalibrated scenario starts were set against total earnings-power growth including buybacks, not on top of them — not double-counted in the verdict.
- **NI_OCF_DIVERGENCE** (2023: net income $1,608M vs OCF $2,961M): resolved from the FY2025 10-K's own cash-flow reconciliation for 2023 — the gap is the recurring non-cash bank addbacks (provision for credit losses $687M and depreciation/amortization/accretion $478M in 2023) plus a $612M *decrease in other assets* (a working-capital release), partly offset by a $242M deferred-tax benefit and a $339M decrease in other liabilities. No one-off gain was found in net income. The structural point matters more than the year: the provision is a real through-cycle cost that OCF adds back every year, so the OCF-based OE base is systematically flattering for a bank — one more reason confidence is low and the bears carry 0.75/0.90 OE multipliers.
- **SECTOR_MODEL_MISMATCH** (Finance): accepted in full. A bank's "owner's earnings" are not its distributable cash — loan growth consumes regulatory capital, provisions are a through-cycle cost the OCF line only partially carries, and value in banking is normally judged on ROTCE vs cost of equity and tangible book (TBV $38.29/share at Q2 2026; the $61.46 price is a substantial premium to it), none of which this model computes. Confidence is low and the tier is soft.
- **OVERRIDE_APPLIED:capex**: see OVERRIDE — gap, decision, single-value and net-vs-gross imperfections, and measured impact are all recorded in fields (judgment.json, dcf_numbers.json overrides_applied/override_impact, overrides_registry.json), not just here.
- **WIDE_SCENARIO_SPREAD** (4.51x): real — a bank's outcome range across a credit cycle IS wide (super-bear IV@15% $20.56 vs super-bull $92.70). Confidence is low (also mandated by the sector flag), and the verdict is sized to the conservative end.
- **HIGH_NET_DEBT** (5.00x normalized OE): an artifact of applying an industrial leverage lens to a bank. The engine's net debt is long-term borrowings of $11,224,000,000 with no cash leg in the pulled series; it excludes the $185.6B deposit base that actually funds the bank and the loan book that backs it. The leverage that matters is regulatory capital: CET1 10.4% at Q2 2026, guided to end 2026 at 10.5-10.6% — adequate, not lavish, and the reason buybacks are sized at $700-850M rather than more. The bear scenarios carry the credit stress this flag asks for.

## My thoughts / overlay
- The honest headline is the method range, not the point estimate: the same TTM base with the engine's default scenario offsets returns weighted IRR 15.11% and IV@15% $62.06 (Tier B); the recalibrated through-cycle starts return 12.63% / $49.38 (Tier C). The entire gap is one judgment — whether a 10.25% growth start built on a fee-only revenue tag, with a bear case that never stresses credit, describes a mature regional bank. It does not, so the verdict sits at the conservative end: C.
- Quality is genuinely improving, and the screen can see it: NIM expanding, ROTCE 13.9% and rising toward a 16-18% target, charge-offs falling, Private Bank compounding, real buybacks. None of that is the debate. The debate is price: at $61.46 the buyer pays for the bull case (IV@15% $63.83, IRR 15.45%) just to roughly clear 15%, and the weighted case returns 12.63%.
- Bank-specific cross-check the model cannot do: at $61.46 against tangible book of $38.29/share, the market is already capitalizing a mid-teens ROTCE as durable. If ROTCE stalls at ~14% instead of reaching 16-18%, even the base case here is generous; if the target is hit and held, the bull case is the right anchor and the stock is merely fairly priced for a 15% hurdle.
- Price that clears 15%: the weighted IV@15% is $49.38 — the stock clears Andrew's hurdle at or below that level, roughly a fifth below the current price, before any additional margin of safety.

## Final verdict
- **Final tier: C** (weighted IRR 12.63% on the v5 final inputs; tier by numbers C, no override of the tier)
- Confidence: **Low** (sector-model mismatch plus a 4.51x scenario spread; the OE base itself is filing-solid once the capex override is in)
- One-liner: Large regional bank in a genuine earnings recovery, moat 5/10 — TTM OE $5.13/sh is an 8.35% yield at $61.46, but on through-cycle growth starts the weighted IRR is 12.63% (IV@15% $49.38), so it clears 15% only below ~$49; bank-model mismatch, confidence low.
