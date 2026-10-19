# E&P capex tags spec draft — additive oil & gas capex missed, decoy tag suppresses the gate

Status: DRAFT, prepared 2026-10-18 by the AR pass-1 worker. Engine untouched (v5.4.0 live).
Case: AR (Antero Resources, CIK 1433270), blocked NEEDS_MAIN_AGENT this run.
Sibling cases: APA (scored 2026-10, different variant — see below). Candidate retro-check: PR.

## The defect

For oil & gas E&Ps, cash capex is filed under us-gaap tags that are NOT in the
engine's capex candidate list (`dcf_engine.py` ~line 574, `ttm.py` CAPEX_TAGS):

- `PaymentsToExploreAndDevelopOilAndGasProperties` (drilling & completion — the dominant leg)
- `PaymentsToAcquireOilAndGasProperty` (leasehold / property acquisition)

The two legs are ADDITIVE components of total capex, not alternatives: in FY2022,
the last year Antero filed the roll-up tag, the components sum EXACTLY to it:

  Explore 780,649,000 + AcquireOG 149,009,000 + OtherPPE 14,313,000
  = 943,971,000 = `PaymentsToAcquirePropertyPlantAndEquipment` FY2022 as filed.

From FY2023 Antero stopped filing the roll-up and files only the components.

## Two variants

1. **APA variant (gate works):** APA files NO candidate capex tag in any year, so
   the preliminary run exited 4 `DATA_GAP:capex` and the worker resolved it with a
   filing-sourced `capex_override` (single FY2025 value $2,740M, per-year
   distortions disclosed). Scored Tier C. No engine change was strictly required.

2. **AR variant (gate is bypassed — worse):** AR files a candidate tag,
   `PaymentsToAcquireOtherPropertyPlantAndEquipment`, at $16.4M / $10.9M / $5.4M
   for FY2023/24/25. Because a candidate value EXISTS, no DATA_GAP fires and the
   override mechanism cannot help: `dcf_engine.py` applies `capex_override` only
   where the filed value is None (fill-only). The engine therefore scored AR on
   ~0.5–1.5% of true capex, silently.

## Measured impact on AR (all figures EDGAR companyfacts, pulled 2026-10-18)

| Period | Engine capex | True capex (3 tags summed) | Engine OE/sh | Corrected OE/sh |
|---|---|---|---|---|
| FY2023 | $16,382,000 | $1,131,863,000 | $2.95 | −$0.63 |
| FY2024 | $10,929,000 | $716,779,000 | $2.46 | $0.21 |
| FY2025 | $5,407,000 | $944,003,000 | $5.01 | $2.00 |
| TTM to Q2 2026 | $12,721,000 | $1,038,346,000 | $6.15 (ttm.py) | $2.85 |

- Engine normalized base (3-yr median): $2.9487/sh. Corrected median: $0.2107/sh (~14x overstatement).
- Engine preliminary print: Tier B, weighted IRR 17.27%, IV@15 $46.92 at price $38.65 — a fake tier.
  On the corrected median base the name is nowhere near B; even the corrected TTM
  base ($2.85/sh) is a commodity-price derivative, not a 17% compounder.
- Corroboration: Antero's own 2026 guidance (Q4 2025 release, 2026-02-11) budgets
  $1.0B of drilling & completion capital ($900M maintenance) + $100M land capital.

## Why the worker could not fix it in bounds (WORKER_SPEC step 8)

- (a) `capex_override` kind "filing": mechanically fill-only (see above); also a
  single value applied to every period — wrong shape for three additive legs
  that vary $717M–$1,132M by year.
- (c) `base_override`: must be built EXCLUSIVELY from this run's
  dcf_numbers.json / ttm.json / financials_history.csv figures. The corrected
  capex legs are in none of them, so a corrected-base pin is out of bounds.
- `tier_override` (VOD precedent): VOD's missing costs are a modelling-policy
  question (spectrum/leases/interest — TELECOM_CAPEX_SPEC_DRAFT #6). AR's are a
  plain filed-capex measurement error with an exact corrected series; stamping a
  hand-sized tier on a base known to be ~14x overstated would ship a number no
  code produced. Blocked instead.

## Proposed fix (for Andrew's ruling, same shape as decision-sheet items 1–5)

1. Add an ADDITIVE capex component group, mirroring the debt_current component
   logic: when the roll-up `PaymentsToAcquirePropertyPlantAndEquipment` is
   absent for a period, total capex = sum of the filed components among
   {`PaymentsToExploreAndDevelopOilAndGasProperties`,
   `PaymentsToAcquireOilAndGasProperty`,
   `PaymentsToAcquireOtherPropertyPlantAndEquipment`,
   `PaymentsForConstructionInProcess`, `PaymentsToAcquireProductiveAssets`, …}.
   When the roll-up IS present it stays authoritative (never sum roll-up +
   components — FY2022 proves they are the same dollars).
   Apply identically in `dcf_engine.py` and `ttm.py`.
2. Provenance: record every component tag used per period in financials_history.csv
   (capex_tag already records one tag; extend to the summed list).
3. Regression shape: AR FY2022 must stay $943,971,000 bit-identical (roll-up
   present); AR FY2023–25 must print the summed totals above; APA must reproduce
   its filed series WITHOUT its override (its Explore leg FY2023–25:
   $2,313M / $2,851M / $2,740M per its analysis.md) and then be re-scored
   override-free; APP/STZ/CCJ exact-match pattern for unaffected names.

## Retro-check list

Folders whose financials_history.csv carries `PaymentsToAcquireOtherPropertyPlantAndEquipment`
as the capex tag: AHR, ARES, EXE (pre-2023 years only — 2023+ use the roll-up, verified),
IP, LNT, PR, VICI, WEC. Most are REITs/utilities/paper where the tag may be the
genuine capex line; **PR (Permian Resources) is an E&P and should be checked
first** — it has no score.json yet, so nothing false has shipped from it.
Any E&P not yet run will hit the AR or APA variant until this is fixed.
