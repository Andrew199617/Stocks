# DCF Sweep — Fixes Implemented (round 2, for re-audit)

**Date:** 2026-10-13 (America/New_York)
**Supersedes:** `dcf-sweep-audit-2026-10-13.zip` (the package you audited).
**Context:** Your audit's verdict was that the outputs were not reliable enough to act on — the ranking's top was model artifacts and the core defect was silent zero-fill. The owner approved your P0 plan as-is, sequenced: P0 first → re-run all scored names under the fixed system → restart pass 1 → then P1/P2. Pass 2 stays paused until its governance (materiality rule + adversarial framing) is added.

This package is the current live system: full `stocks/` tree (code, per-company outputs, daily HTML) and the current automation definitions under `automation/`.

## What was fixed, mapped to your findings

1. **Silent zero-fill (your core defect) → hard DATA_GAP gate.** `dcf_engine.py` is now v5: if SBC, capex, or diluted shares are missing for ANY of the last 3 fiscal years, the price is unavailable, or the filer reports non-USD (checked as: any non-USD unit on revenue/NI/OCF facts, because JD carries USD convenience translations), the engine emits `data_gap` + `DATA_GAP:<field>` flags, tier null, exit code 4 (price-only gap: exit 3). Flags are computed BEFORE the F branch. No tier is ever emitted on a gap. New fallback tags: SBC `AllocatedShareBasedCompensationExpense`; capex `PaymentsForConstructionInProcess`, `PaymentsToAcquireOtherProductiveAssets`.
2. **Hand arithmetic (DFTX net income, ED net debt) → code.** TTM is computed by `ttm.py` (10-Q YTD facts, full audit-trail JSON; hard exit on partial capex facts). Additionally, worker instructions now require every figure in analysis.md to be copied from computed outputs — `make_score.py` generates a `key_numbers.md` per company as the quotable source; derived figures may not be recomputed in prose.
3. **JD's 2× hand-scaled score → impossible by construction.** `make_score.py` is the only writer of score.json and builds it solely from `dcf_numbers.json` + `judgment.json`. JD now DATA_GAPs on currency. Related display bug found during this round: JD's stale v4 score.json kept rendering in the ranking after the block — `build_daily_html.py` now skips any score whose sibling `dcf_numbers.json` carries uncovered gaps.
4. **Queue integrity → `queue.py`.** Claim/done/block/reap with an fcntl lock, atomic rename, 90-minute leases. Two simultaneous claims verified to return distinct tickers.
5. **Timestamps / identity.** America/New_York dates (zoneinfo) everywhere; SEC User-Agent carries a real contact email; 3-try retry/backoff on EDGAR fetches.
6. **Sector misfits.** `SECTOR_MODEL_MISMATCH` extended beyond Finance to Real Estate and Utilities (the "not modeled" separate list is P1, not yet done).
7. **Naming.** `oe_ps_cagr_3y` renamed `oe_ps_cagr_2y` (it was always 2-year).
8. **Pass 2.** Both pass-2 jobs remain PAUSED. They restart only after the materiality rule (score change only if weighted IRR moves ≥2pp or tier changes, driver filing-sourced, reproducible inputs) and adversarial framing are added.

## The override layer (new since your audit — owner's decision)

Rule set by the owner: code does arithmetic and flags gaps; the agent decides what to do about them; every decision lands in a structured field, not prose.

- `judgment.json` gains optional `capex_override` / `sbc_override` / `shares_override`: `{value, source, reason, kind: "filing" | "estimate"}`. An override fills ONLY periods where the filing tag is absent; it never overwrites a filed value (the history CSV records tag `OVERRIDE` for filled periods).
- The engine applies overrides and records `overrides_applied` (with `periods_filled`) in `dcf_numbers.json`; partially covered gaps still exit 4, listing only the uncovered fields. Impact is measured by `make_score.py` on the base the final run actually used: the counterfactual replays the final run's exact configuration (same moat/probs/offsets/mults/price, same base pin) with overrides toggled off — for a TTM base the without-figure is the zero-fill TTM (for APP, `ttm.py` with overrides off cannot compute, so the zero-fill is reconstructed from the with-override run's legs and lands exactly on OCF − SBC). Each registry entry and score.json carries `base_used` (ttm | median_3y), base OE/share without → with (%), weighted IRR without → with (pp), and `unblocks_tier` — true when the override is the only reason the company has a tier at all. (An earlier build measured impact on the engine-native median base, which read 0.0 for APP and was misleading; superseded the same night at the owner's direction.)
- `ttm.py` applies the same overrides, prorating flow legs (capex/SBC) by days/365; share counts are applied unprorated (a weighted average is not a flow).
- `make_score.py` validates override shape, refuses on uncovered gaps, and refuses when judgment.json and dcf_numbers.json disagree on an override's value/kind. It also maintains the central registry `_system/overrides_registry.json` (one upserted entry per ticker+field, with measured impact) for owner review and later backtesting of whether overrides helped.
- The daily ranking marks override-based scores: an amber badge in the list ("capex: AI estimate" / "capex: filing override"), a chip in the verdict card, and an Overrides section on the company page with source, reason, periods filled, and measured impact.
- Workers still BLOCK on DATA_GAP. Entering an override is currently the main agent's decision, case by case. The re-run's tier-change report will include the DATA_GAP count/rate; if more than ~1 in 7 names block, the owner decides whether workers get override authority in their spec.

**Worked example — APP (in this package).** AppLovin tags no capex from FY2025 onward. Tagged capex FY19–FY24: $3.4M / $3.2M / $1.4M / $0.7M / $4.2M / $4.8M vs OCF $2.1B (FY24) and $4.0B (FY25). Override: $19M/yr, kind `estimate` — the higher of the last tagged FY2024 figure and the ~$19M v4 TTM estimate, per the owner's conservative rule. Result under v5: Tier B, TTM base OE $12.51/sh (vs $12.57 zero-fill, −0.45%), weighted IRR 18.43%, IV@15 $376.13 vs price $272.28. See `stocks/APP/` (judgment.json, dcf_numbers.json, key_numbers.md, analysis.md OVERRIDE section).

## Verification performed on this build

- Unity regression reproduces v4 to the dollar (TTM OE/sh $0.45052; weighted IRR 0.0495; IV $7.73) — no model drift for override-free names.
- APP: engine exits 4 without judgment.json, exits 0 with the override; tampering with the judgment override value makes make_score refuse; registry upsert is idempotent (one entry after two runs).
- JD exits 4 (currency) and make_score refuses its stale score.
- DFTX exits 4 on never-filed capex; its v4 OE base is reproduced exactly by ttm.py (the audit's −$486M vs −$354M error was in TTM net income, which never fed owner's earnings).
- ED: construction-in-process capex and allocated SBC now found; the bare engine says Tier F — v4's D rested on an agent-adjusted base.
- ROP: capex found via `PaymentsToAcquireOtherProductiveAssets`; Tier C 11.9% on bare engine defaults.

## Re-run status

All 43 v4-scored queue names were requeued (`v5_rerun`) and are being re-run under v5 by both pass-1 workers; the tier-change report (including DATA_GAP count/rate) follows when they finish. Company folders in this package are a mid-re-run snapshot — most still hold v4 outputs; APP and U are v5-final.

## Known open items (P1/P2, acknowledged, not yet done)

- Pre-block IFRS / 20-F / 40-F filers universe-wide (engine reads US-GAAP tags only).
- Extension-tag gap: TKO files capex under a custom `tko:` tag ($127M FY25) and blocks DATA_GAP; fix is namespace scanning of the same companyfacts payload.
- Separate "not modeled" list for Finance / Real Estate / Utilities in the ranking.
- IRR band in engine + HTML, tier set on the low end.
- Point-in-time backtest of the mechanical engine (filed-date cutoffs, mechanical inputs only).
- Daily filing watcher to re-queue done names on new 10-Q/10-K (freshness moves out of pass 2).
- HTML list/detail split (file is ~550KB at 44 companies and will not scale to 2,617 as one file).
- forensic_pull.py bugs: STALE_PASS1 flag ordering; routine 8-K items 2.02/7.01 counted as material.
- Pass-2 governance (materiality rule + adversarial framing) before restart; guidance-vs-model check approved for pass 2; insider/buyback signals rejected per your audit.

## Re-audit asks

1. Try to make the gate emit a tier on incomplete data (any path: overrides, TTM pin, manual price).
2. Check override integrity end-to-end: can a score exist whose numbers don't match its recorded override? Does the registry capture every override in the tree?
3. Re-derive APP from its folder alone — do the filed figures, the override, and the headline numbers reconcile?
4. Whatever new failure modes you find.
