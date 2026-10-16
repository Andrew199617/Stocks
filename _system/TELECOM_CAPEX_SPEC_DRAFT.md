# DRAFT SPEC — Telecom total-capex leg for the DCF engine (v5.3.1)

Status: DRAFT, prepared 2026-10-14 (proactive research run). Not implemented.
Decision needed from Andrew: implement, or keep handling telecoms by manual
tier override (VOD precedent).

## Why

VOD (scored 2026-10-14) printed Tier S by numbers — weighted IRR 32.57%,
IV@15% $37.13 vs $15.51 price — on an owner's-earnings base that is
structurally ~4x too high:

- Engine FY2025 OE: $11.831B (OCF $16.626B − PP&E capex $4.676B − SBC $0.119B;
  `~/workspace/stocks/VOD/financials_history.csv`, `key_numbers.md`).
- Vodafone's own adjusted FCF FY25: €2.5B (FY26: €2.6B) — EBITDAaL less
  capital additions, lease payments, cash interest and cash tax.
- Group capital additions FY25 were €6.9B vs the ~€4.3B the engine's PP&E tag
  (`PurchaseOfPropertyPlantAndEquipmentClassifiedAsInvestingActivities`)
  captures. The gap is spectrum licences + intangible (software/network)
  capex, filed under investing tags the engine does not read.
- Lease principal sits in financing cash flows, outside the OCF the engine
  starts from. Cash interest likewise sits outside the OCF presentation for
  this IFRS filer (US-GAAP OCF already includes interest paid — see the
  asymmetry note below).

The worker caught it and overrode S → D, documented in
`~/workspace/stocks/VOD/score.json` / `analysis.md`. That override is
one-off: capex overrides only fill periods where the tag is *absent*, and
the PP&E tag is present every year, so no bounded override can fix the base.

## Who else this hits

- Already scored telecoms: VOD only, so far (ECHO is Telecommunications /
  Pay-TV but its OE is negative on OCF alone — capex leg does not change
  its F; re-check after implementation anyway).
- In flight / queued: CHT (folder exists, `dcf_numbers.json` present, no
  `score.json` yet) and ERIC (folder created, unscored) are both IFRS
  telecoms in the requeued foreign-filer set. US carriers still ahead in
  the queue (descending market cap) will hit the US-GAAP version of the
  same gap: spectrum purchases are intangible capex, not PP&E.
- Every future telecom worker will otherwise have to rediscover the trap
  and hand-override, with inconsistent results.

## Proposed change (engine, narrow)

1. **Total-capex leg for telecom-flagged names only.** When the filer's
   sector is Telecommunications (the sector string already in score.json),
   capex = PP&E capex (existing tag list) + intangible capex, from:
   - US-GAAP: `PaymentsToAcquireIntangibleAssets`,
     `PaymentsToAcquireOtherIntangibleAssets` (dedupe against any combined
     tag already counted — do not double-count).
   - IFRS (ifrs-full): `PurchaseOfIntangibleAssetsOtherThanGoodwill`,
     and handle the already-supported combined tag
     `PurchaseOfPropertyPlantAndEquipmentIntangibleAssetsOtherThanGoodwillInvestmentPropertyAndOtherNoncurrentAssets`
     as the *total* (when that tag is the source, add nothing further).
2. **Lease principal leg (same names):** subtract finance-lease principal
   payments where filed separately from OCF
   (`PaymentsOfFinanceLeaseObligations` / IFRS principal-portion tags).
   If the tag is absent, flag, don't zero-fill silently.
3. **Interest asymmetry — flag, do not auto-subtract.** US-GAAP OCF is
   after cash interest; IFRS filers may classify interest paid in
   financing. Subtracting interest only for IFRS names would make the two
   populations inconsistent in the opposite direction. Spec decision for
   Andrew: either (a) leave interest out of OE for everyone (current,
   VOD's gap then rests on capex + leases alone — still most of the 4x),
   or (b) a separate documented telecom adjustment. Recommendation: (a)
   for v1 of this leg.
4. **Guardrail flag even before/without the leg:**
   `TELECOM_CAPEX_INCOMPLETE` — fires for a telecom name when no
   intangible-capex tag was found in any of the last 3 FYs. Same spirit as
   SECTOR_MODEL_MISMATCH: confidence low, and the ranking badges it, so a
   numbers-tier S/A on an incomplete telecom base is visibly suspect
   instead of relying on the worker catching it.

## Acceptance tests

- VOD re-run: total capex FY25 should land near the filed €6.9B capital
  additions (converted), OE should fall from $11.83B toward the company's
  €2.5B adjusted-FCF neighbourhood (not exact — definitions differ on tax
  and interest), and the numbers tier should no longer print S.
- Non-telecom regressions bit-identical: STZ (US-GAAP), CCJ and JD (IFRS)
  — the same battery used for v5.3.1.
- ECHO re-run: tier stays F (negative OE is OCF-driven, not capex-driven).
- No double-count case: a filer using the combined IFRS tag gets that tag
  as its total, once.

## What this does NOT do

- No change to Finance / Real Estate / Utilities handling (separate
  not-modeled decisions already on Andrew's list).
- No retroactive rescoring until Andrew approves implementation; VOD's
  D-by-override stands either way.
- No interest subtraction in v1 (see §3).
