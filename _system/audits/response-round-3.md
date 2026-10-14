# DCF Sweep — Round-3 bundle (response to the round-2 re-audit)

**Date:** 2026-10-14 (America/New_York)
**Supersedes:** `dcf-sweep-fixes-2026-10-13.zip`.
**For:** re-test with the same harnesses as round 2. Your round-2 verdict — P0 real, perimeter too narrow, eight ways past the gate — was accepted in full; every item in your closing brief plus the P1 set was implemented. One item was NOT built, with evidence: TKO's extension tags are unreachable in companyfacts (see "Not built" below).

This package is the live system mid-re-run: full `stocks/` tree and current automation definitions under `automation/`.

## Implemented, mapped to your round-2 findings

**Now items**
1. `make_score.py` refuses any `dcf_numbers.json` with engine_version < 5 or no `data_gap` field ("this folder holds pre-v5 output and the engine must be re-run under v5"). Verified live on HIG's v4 folder: refusal, nothing written.
2. The ranking partitions by engine vintage: pre-v5 rows render only in a collapsed "Pre-v5 results — re-run pending" section (ticker + old tier, stale badge). At build time: 6 current / 34 stale; HIG, PRU, PCG confirmed in the stale section. Pass-2 badges now render ONLY from a `second_pass` object on the current score.json (a v5 re-score drops the old one); `second_pass_queue.json` entries for all 7 previously reviewed names (all v5_rerun names) were reset to pending so a restarted pass 2 re-checks them against v5 numbers.

**P0**
3. OCF gated: `NetCashProvidedByUsedInOperatingActivitiesContinuingOperations` added as a fallback OCF tag (provenance in a new `ocf_tag` CSV column); OCF missing in any of the last 3 FY → DATA_GAP:ocf, exit 4. Harness-verified both ways on doctored APP companyfacts (renamed tag → found via fallback; FY25 OCF removed → exit 4). ttm.py's OCF tags gained the same fallback.
4. Override bounds: negative values refused outright (engine + make_score). Outside 0.1×–10× of the last filed value for that field (or no filed value) → engine flags OVERRIDE_OUT_OF_BAND and make_score refuses without an `ack_reason` on the override object. Verified on a synthetic: an override of `19` reproduced your fake Tier A at the engine, was flagged, refused, then admitted with an ack. APP's $19M is 3.98× its last filed $4.776M — in band, no ack, scores unchanged.
5. TTM pin provenance: ttm.py writes `ttm.json` into the company folder on every run; the engine takes `--ttm` and records `base_pin_source`; make_score refuses when the score's base differs from ttm.json by >0.1%. A pin not from ttm.json requires a `base_override` {value, source, reason} in judgment.json and is recorded in the registry. Both worker specs now use `--ttm` and quote ttm.json. make_score's internal measurement runs set DCF_TTM_NO_WRITE=1 so they cannot clobber a worker's ttm.json.

**P1**
6. Currency check scoped to facts in the last 3 FY (a stray 2016 EUR fact no longer blocks — harness-verified). Foreign filers: the engine records `filer_annual_form` from EDGAR submissions; a 20-F/40-F filer without an `ads_ratio` {ratio, source, reason} in judgment.json is refused by make_score as DATA_GAP:ads_ratio; with one, per-share figures are scaled and the ratio is recorded (and registered as a judgment event).
7. Registry integrity: every make_score run REPLACES the ticker's entries wholesale (verified: a planted stale entry vanished on re-score, other tickers untouched). The registry now also records tier overrides, manual prices, base_override pins, non-default gterm, non-default/fallback CIK, and ads_ratio as event entries. The ranking badges tier overrides on the row and detail page.
8. make_score computes rule fields: `in_scope_under_40b` from the engine's market-cap estimate, refusing a contradicting judgment claim; confidence clamped to medium when WIDE_SCENARIO_SPREAD is present, recorded as `confidence_capped: true`.
9. queue.py: `claim` reaps expired leases under the same lock before claiming (verified: an expired lease was reaped and re-claimed); `block --stdin` reads reasons from stdin (verified byte-for-byte with `$127M`, quotes, and `$93.753M` intact); DATA_GAP reasons auto-select the new `blocked_data_gap` status, distinct from `blocked_no_data`; `requeue` added. The four existing DATA_GAP entries (CMPS, STZ, DFTX, TKO) were migrated through queue.py itself.
10. ttm.py: never-filed capex hard-blocks (exit 3) unless an override fills it — the zero-fill path is gone (verified on DFTX); day counts inclusive (APP's filled TTM capex is now exactly $19,000,000); leg matching tolerates filed facts with start dates shifted ≤5 days.
11. IRR solver: value still above price at a 200% discount rate now returns a capped 2.0 with an IRR_CAPPED flag (harness at $0.01 price: Tier S, was blank → D). Diluted shares missing with basic present → DATA_GAP:shares (no silent swap; the basic figure stays in the CSV for reference). Provenance: the engine stamps a `content_hash` over dcf_numbers.json; make_score recomputes and refuses on mismatch OR absence (verified: a +$1 price edit refuses).

**P2**
12. key_numbers.md: OE yield and TV share lines are unconditional now (a bad conditional dropped them when scenario spread was blank); the duplicated shares-reason line is removed.
13. APP analysis.md margin sentence corrected: 38.1% is the upside; the price is 27.6% below the weighted IV.

## APP, re-derived after all changes

Still Tier B. ttm.json: TTM OE/share $12.5082 (the 4th decimal moved −$0.0002 vs round 2's $12.5084 because inclusive day counts make the filled FY capex leg exactly $19.00M; the round-2 brief anticipated identical numbers — the two audit items conflicted at that precision and the explicit $19.00M requirement won). Weighted IRR 18.43%, IV@15 $376.12 vs price $272.28. Registry entry unchanged in substance: TTM basis, $12.5644 → $12.5082 (−0.448%), IRR −0.053pp, unblocks_tier true.

## Not built

- **TKO namespace scanning.** Verified directly against EDGAR: companyfacts for CIK 1973266 carries only dei/ecd/us-gaap — extension taxonomies are not in the payload, exactly as you suspected. TKO's capex ($127M FY25) lives in the filing's own XBRL instance. Options if the owner wants it: filing-instance parsing (heavier), or a filing-sourced override under the existing flow. TKO sits in blocked_data_gap meanwhile.
- Everything else from your P2 list beyond items 12–13 remains as previously logged (backtest, filing watcher, HTML list/detail split, forensic_pull fixes, pass-2 governance — pass 2 is still paused).

## Consequences to be aware of when re-testing

- The five folders scored under v5 before hash-stamping (U, RDDT, SNAP, DUOL, TTWO) now refuse make_score until their next engine run — absence of a hash refuses by design. Their existing score.jsons are valid and render as current.
- JD was pending (not blocked) at migration time, so it has no blocked_data_gap status yet; its next worker run lands it there.
- The re-run continues live: at bundle time the queue shows 6 done, 4 blocked_data_gap, 9 blocked_no_data, ~2,597 pending. Folders are a snapshot; several still hold v4 output by design (they render in the stale section only).

## Re-test asks

Re-run your round-2 harnesses unchanged: the gate attempts table, the override-integrity probes (including the TTM-pin drift — now checkable against ttm.json), and the APP folder reconciliation (note the $12.5082 base). Plus anything new the seams suggest.
