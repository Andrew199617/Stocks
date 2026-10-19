# DRAFT SPEC — Add PaymentsForCapitalImprovements to the DCF engine capex tags

Status: DRAFT, prepared 2026-10-18 (proactive research run). Not implemented.
Engine untouched. Decision needed from Andrew: implement, or keep curing this
tag gap name-by-name with single-value filing overrides where they are
in-bounds (and blocking where they are not).

This consolidates six verified instances of one defect: filers whose only
capex line is tagged us-gaap `PaymentsForCapitalImprovements` are invisible to
the engine's capex candidate list. Five names were scored anyway via
single-value capex overrides (with disclosed per-year distortions); the
sixth, ELS (2026-10-18), could not be cured in-bounds and is blocked.

## Root cause (verified in code, 2026-10-18)

`dcf_engine.py` (capex candidate list, ~line 574):

```python
"capex": ["PaymentsToAcquirePropertyPlantAndEquipment", "PaymentsForConstructionInProcess",
          "PaymentsToAcquireOtherPropertyPlantAndEquipment", "PaymentsToAcquireProductiveAssets",
          "PaymentsToAcquireOtherProductiveAssets", (IFRS tuples...)]
```

`PaymentsForCapitalImprovements` is not in the list. `ttm.py` carries its own
copy of the list (`CAPEX_TAGS`, lines 48–50) and is missing the tag too — a
fix must land in both files or TTM bases stay broken for these filers.

`period_series` (dcf_engine.py line 464) merges candidate tags **per period
in priority order**: a later tag only fills periods no earlier tag supplied.
Appending the new tag at the end of the us-gaap group is therefore the safe
placement — it can only fill gaps, never displace a filed PPE-capex value —
with one exception, ELS FY2023, covered as a sub-decision below.

## The six verified cases

1. **ELS (Equity Lifestyle Properties) — BLOCKED 2026-10-18, no score.**
   Files capex only as PaymentsForCapitalImprovements: FY2023 $317.086M,
   FY2024 $241.279M, FY2025 $237.091M (10-K filed 2026-02-18, accession
   0001628280-26-008722; sole capex line in the FY2025 cash-flow statement).
   The engine instead picked a $0 PaymentsToAcquireOtherProductiveAssets
   value for FY2023 (printed OE/share $2.713 vs true $1.090) and nothing for
   FY2024/25 → DATA_GAP:capex. A single-value override would leave the
   median base at $1.781 vs the true $1.633 (+9.1%, anti-conservative), and
   a correcting base_override falls outside bounded authority rule (c), so
   the worker correctly blocked it (NEEDS_MAIN_AGENT: capex).
2. **CR (Crane) — Tier D, scored via override.** Filed $39.0M / $36.6M /
   $53.5M (FY2023/24/25, 10-K filed 2026-02-26, accession
   0001944013-26-000095). Override was a TTM-derived $48.5M single value;
   the (unused) median base came out ~6% conservative ($3.15 vs $3.36/sh
   on true per-year figures).
3. **IT (Gartner) — Tier C, scored via override.** Filed $103.124M /
   $101.737M / $115.142M (FY2023/24/25, 10-K filed 2026-02-12). Override
   was the $103.124M median — the tightest case, distortion small.
4. **MAA (Mid-America Apartment Communities) — Tier D, scored via
   override.** Filed $341.224M / $322.372M / $360.238M (FY2023/24/25, 10-K
   filed 2026-02-06, accession 0001193125-26-041208) on the cash-flow line
   "Payments for capital improvements". Override was the median
   $341.224M (overstates FY2024 by $18.85M, understates FY2025 by $19.01M).
   Note the worker deliberately excluded "Payments to acquire real estate"
   / development spend — for REITs this tag *is* the recurring capex line.
   This is distinct from the open ESS question, where the filer splits
   real-estate additions into four lines including acquisitions; adding
   this tag does not decide ESS.
5. **RBC (RBC Bearings) — Tier D, scored via override.** Filed $33.2M /
   $49.8M / $73.1M (FY2024/25/26, 10-K filed 2026-05-15); the prior tag
   (PaymentsToAcquirePropertyPlantAndEquipment) stops after FY2023.
   Override applied the FY2026 $73.1M to every year — overstates FY2024
   capex by $39.9M and FY2025 by $23.3M (conservative direction), and
   understates true TTM capex by $9.2M (~2.6% of TTM OE).
6. **SNA (Snap-on) — Tier D, scored via override.** Filed $95.0M / $83.5M /
   $76.0M (FY2023/24/25, 10-K filed 2026-02-12, accession
   0000091440-26-000045). Override applied the FY2025 $76.0M to every year —
   understates FY2023 capex by $19.0M and FY2024 by $7.5M (raises those
   years' OE ~1.9% / ~0.7%, anti-conservative but small); TTM capex off by
   $1.7M (~0.2% of TTM OE).

Pattern: every override is a single value standing in for three different
filed years, so every one of these scores carries a disclosed approximation
that the filed data never required. The tag is the filer's *only* capex
line in all six cases — this is a standard us-gaap tag for "capital
expenditures" / "capital improvements" cash-flow lines, not an exotic
extension tag.

## Proposed fix

1. Append `"PaymentsForCapitalImprovements"` to the capex candidate list in
   `dcf_engine.py` (end of the us-gaap group, after
   `PaymentsToAcquireOtherProductiveAssets`) and to `CAPEX_TAGS` in
   `ttm.py` (same position).
2. Re-run the five scored names (CR, IT, MAA, RBC, SNA) without their
   capex overrides; expect small base moves in the directions documented
   above (RBC/SNA bases rise/fall per their distortion notes; no tier
   change is expected — all five are C or D with headroom — but the
   re-runs must confirm, and any tier change gets reported).
3. Unblock and score ELS (subject to the sub-decision below).
4. Retro-check: scan all scored folders' companyfacts for periods where
   PaymentsForCapitalImprovements exists *alongside* an engine-read tag —
   confirm the append-only placement changed nothing for them (by
   construction it cannot, except the $0 case below).

## Sub-decision: the ELS FY2023 $0 problem

Appending the tag does **not** fully fix ELS. For FY2023 an earlier
candidate (PaymentsToAcquireOtherProductiveAssets) supplies a filed $0,
and per-period priority merge lets that $0 stand over the real $317.086M
capital-improvements value. FY2024/25 fill correctly; FY2023 stays wrong
(OE/share $2.713 vs $1.090), which still corrupts the median-of-3 base.

Options, in the drafter's order of preference:

- **(a) Zero-guard for fallback tags:** a $0 value supplied by a
  non-primary candidate tag does not block a non-zero value from a later
  candidate for the same period. Needs the retro-check in step 4 extended:
  count scored periods where any candidate supplies $0 while a later
  candidate is non-zero, and eyeball them before shipping.
- **(b) Promote the tag:** place PaymentsForCapitalImprovements above
  PaymentsToAcquireOtherProductiveAssets (only). Risk: a filer that files
  both, with capital improvements a genuine subset of its capex, would
  have its real capex replaced by the subset for overlapping periods.
  The step-4 retro-check would have to rule this out name by name.
- **(c) Append only, leave ELS FY2023 to a base decision:** ELS stays
  blocked or takes a one-off main-agent base_override built from the
  three filed years. Cheapest, but leaves a known-wrong $0 in the record
  for any future filer with the same shape.

## What this does not do

- Does not decide ESS (summed real-estate additions incl. acquisitions),
  AER (flight equipment), or any other sector-capex packet — those are
  definition questions; this one is a missing standard tag.
- Does not change any filer's score until the re-runs in step 2 are run
  and reported.
