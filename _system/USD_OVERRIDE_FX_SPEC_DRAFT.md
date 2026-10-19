# DRAFT SPEC — USD-translation override FX bug in the DCF engine (v5.4.0)

Status: DRAFT, prepared 2026-10-17 (proactive research run). Not implemented.
Engine untouched. Decision needed from Andrew: implement, or keep both
names blocked and rely on no workaround.

This consolidates two blocked names that are the same defect, surfaced
two weeks apart: PUK (blocked 2026-10-14) and CX / Cemex (blocked
2026-10-17, escalated NEEDS_MAIN_AGENT). In both, a filing-sourced
monetary override is already in USD, but `_override_usd()` in
`dcf_engine.py` (line ~761) demands a foreign-currency ECB rate for
every fill period whenever any `fx_info` exists — and returns None
(no fill, gap stands) when that period has no such rate.

## The two verified cases

1. **PUK (Prudential plc) — reports in USD, stray GBP history poisons the lookup.**
   - Prudential reports in US dollars. Its SBC tag
     (`ExpenseFromSharebasedPaymentTransactionsWithEmployees`) was last
     filed for FY2019 ($181M USD); FY2020–25 are missing under every
     ifrs-full tag the engine reads.
   - Filing-sourced override in `~/workspace/stocks/PUK/judgment.json`:
     $85M, kind "filing", from Annual Report 2024 note B2.2(d)
     (2024: $85M, 2023: $81M — ~2–3% of OCF, same magnitude).
   - Why it fails: stray GBP facts through 2018 created `fx_info` with
     `from_currency: GBP`; `rates_by_currency[GBP]` covers only
     2014–2018 (see PUK `dcf_numbers.json` fx_conversion). For fill
     periods 2023–2025 `_override_usd` finds no GBP rate → returns None.
   - Result: DATA_GAP:sbc stands, no tier. Price $23.81, ADS ratio 2.

2. **CX (Cemex) — recent SBC is filed as the issuer's own USD translations.**
   - ADS ratio cured cleanly in bounds: 30 ordinary shares / ADS
     (20-F FY2024 Note 1; corroborated Note 21), per-ADS zero-fill base
     $0.6086 vs $10.25 ADS price.
   - Filing-sourced override in `~/workspace/stocks/CX/judgment.json`:
     $55M, kind "filing", from 20-F FY2024 Note 22 (2024: $55M /
     2023: $61M / 2022: $52M, statements presented in millions of USD).
     Engine `override_checks`: last filed $77M USD (FY2021),
     `out_of_band: false`.
   - Why it fails: `fx_info.from_currency` is MXN, but
     `fx_conversion.rates` holds only 2014–2017 — 2022–2024 facts are
     the issuer's own USD convenience translations (flagged
     USD_TRANSLATIONS_USED), so there are no MXN-unit facts and no MXN
     rate for those periods. `_override_usd` returns None for every
     fill period; `overrides_applied` stays [].
   - Result: DATA_GAP:sbc stands, no tier. Moat work is done and saved
     in CX/judgment.json (5/10) and carries over on requeue.
     Note: the engine's $451.7B `market_cap_est` for CX is the known
     ADS share-basis artifact (ADS price × ordinary shares); true cap
     ~$14.9B — that is the share-basis spec's territory, not this one's.
     (The $451.7B is CX's recorded pre-fix value: the ADS formula fix
     shipped 2026-10-18, so CX's cap corrects to ~$14.9B on its next
     engine run; CX itself stays blocked on the FX defect above.)

## Root cause, in one line

`_override_usd()` keys conversion solely off `fx_info["from_currency"]`
and the period, and never asks what currency the override value itself
is in — even though the engine already records the answer:
`override_checks[field].last_filed_unit` is "USD" in both cases, and
both filings state the override figure in USD.

The v5.3.1 fix this function implements (convert overrides declared in
the reporting currency, Codex PR #1 finding) is correct for its case —
FER's €50M override *should* convert. The defect is the missing
branch for overrides that are already USD.

## Proposed change (engine, narrow)

In `_override_usd(field, p)`, before the FX lookup:

1. If the override is declared in USD, return the value verbatim and
   do NOT add the field to `ov_fx_fields` / `overrides_converted`.
   Declaration source, in order of preference:
   - (preferred) an explicit `currency: "USD"` field on the override
     object in judgment.json, accepted only for kind "filing" with a
     source quoting the USD figure; or
   - `override_checks[field].last_filed_unit == "USD"` for that field.
   Recommendation: implement the explicit field AND fall back to
   last_filed_unit, logging which one fired in dcf_numbers.json.
2. Everything else is unchanged: reporting-currency overrides still
   convert at the period-end rate; a missing rate for a genuinely
   foreign-currency override still returns None and the gap stands
   (fail-safe preserved); share counts are never converted.

Guardrail: a USD declaration must not be usable to smuggle a
local-currency figure past conversion. The sanity band already anchors
on the last filed value in its filed unit — for both cases here the
band check passes in USD ($85M vs $181M PUK; $55M vs $77M CX), and a
mismatched declaration would normally trip out_of_band. Keep that
check ahead of the new branch.

## Acceptance tests

- PUK re-run from its saved folder: SBC fills at $85M for the missing
  years, DATA_GAP:sbc clears, `overrides_applied` lists sbc, and
  `fx_conversion.overrides_converted` does NOT list sbc. A tier emits
  (expected low-confidence, Finance sector misfit — tier itself is the
  re-run's output, not pre-judged here).
- CX re-run from its saved folder: SBC fills at $55M, DATA_GAP:sbc
  clears, ADS ratio 30 still applied, moat 5/10 judgment carried over.
  Indicative base: zero-fill $0.6086/ADS less ~$55M SBC over
  ~1.47B ADS ≈ $0.57/ADS — the re-run's computed number governs.
- FER-style regression: a synthetic €50M SBC override on an
  EUR-converted name still fills converted (the v5.3.1 proof:
  $53.33M/$55.25M/$51.945M/$58.75M at each period's rate).
- Regressions bit-identical: APP (B, 18.43%), STZ (D, 9.8%),
  CCJ (D, 5.91%) — the same battery used for the 5.4 port.

## What this does NOT do

- No engine change until Andrew approves; PUK and CX stay blocked.
- Does not cure BSAC (blocked 2026-10-17): its whole filing is
  CLP-only and CLP has no ECB/frankfurter rate at all — that is a
  rate-source decision, a different problem from this override branch.
- Does not touch the share-basis / market-cap ADS artifact (CX's
  $451.7B estimate) — that stays with SHARE_BASIS_SPEC_DRAFT.md.
- No base_override workaround for either name: for CX the worker
  already established that would violate the
  exclusively-from-run-outputs rule (SBC is blank in all run outputs).
