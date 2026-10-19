# Review guide — owner's-earnings DCF sweep

This repo holds the output of an automated DCF sweep over ~2,600 US-listed
companies, produced by worker agents ("Muse") from SEC EDGAR filings. Most
PRs add or refresh company folders `<TICKER>/`. Review a company PR like an
auditor checking internal consistency and arithmetic. You cannot fetch EDGAR
from a review: verify from what is in the diff and in the repo, and when a
claim can only be checked against the filing, say "cannot verify from the
diff" instead of guessing.

Every finding needs: file, line, the two values that disagree, why it
matters, and a severity from the scale below. Order comments by severity.

Severity scale:
- **P1 — wrong tier risk.** The published tier or a chat alert would be
  wrong: share-scale defects, incomplete capex, a tier alongside a DATA_GAP,
  a base built on a distorted year, an S/A whose IRR rests on a flagged
  artifact.
- **P2 — rule violation.** An override without source, an unresolved flag,
  a code change without a spec or test update, a dated record rewritten.
- **P3 — consistency.** Text that disagrees with generated numbers, stale
  wording, missing enrichment.

## What is in a PR

Two kinds of PR come from the sweep, and they must not be mixed:

1. **Company data PRs** — folders under `<TICKER>/`,
   `_system/overrides_registry.json`, `_daily/history/ranking-<date>.csv`.
   (`_system/queue.json` is synced to main separately and never reviewed
   here.)
2. **Code and spec PRs** — anything under `_system/*.py`, `_system/tests/`,
   `_system/*.md`, `automation/`, `_daily/site/`.

A PR that changes `_system/*.py` or a spec together with hundreds of data
files is a P2 finding on its own: say which code lines changed and ask for
them in a separate PR. One exception: the catch-up PR that first brings the
live VM's state onto main after the 2026-10-16 merge may mix the two (it
carries spec drafts, this file and ~1,500 data files); the separation binds
from the first per-company PR after it. Policy-bearing files are `make_score.py` (tiers,
alert gates), `dcf_engine.py` (the formula), `queue.py` (claims and pass 2),
`WORKER_SPEC.md` and `SECOND_PASS.md` (what workers must do). A change to
any of them needs (a) a test in `_system/tests/` that fails on the old code,
(b) the matching sentence in the specs and `README.md` updated, and (c) a
commit message that says what decision it implements and who made it. Grep
the specs for the old rule and list every stale passage with file:line.

## Files in each company folder

- `financials_history.csv` — the engine input, one row per fiscal year.
  Columns include `ocf`, `capex`, `capex_tag`, `capex_assumed_zero`, `sbc`,
  `sbc_tag`, `da`, `shares_diluted`, `cash`, `debt_current`, `debt_lt`.
- `dcf_numbers.json` — engine output: `base_oe_per_share`, `base_source`,
  `base_oe_latest_per_share` vs `base_oe_normalized_per_share`, `g_base`,
  `scenarios`, `weighted`, `implied_irr_weighted`, `tier_by_numbers`,
  `fragility_flags`, `data_gap`, `used_tags`, `overrides_applied`,
  `ads_ratio`, `shares_diluted_latest`, `market_cap_est`,
  `net_debt_latest`, `engine_version`, `engine_release`, `content_hash`.
- `judgment.json` — the worker's decisions: `moat_score`, `moat_for` /
  `moat_against`, `probs_used`, `confidence`, `tier_override` +
  `tier_override_reason`, per-field overrides as top-level keys
  (`capex_override`, `sbc_override`, `shares_override`, `base_override`,
  `ads_ratio`; each `{value, source, reason, kind}`), `second_pass` when
  pass 2 ran.
- `score.json` — generated ONLY by `make_score.py`: `tier_final`,
  `tier_by_numbers`, `implied_irr`, `iv_at_15`, `irr_bear` / `irr_bull`,
  `tier_bear` / `tier_bull`, `alert_eligible`, `exit_alert_eligible`,
  `engine_release`, `in_scope_under_40b`, `model_fit`.
- `key_numbers.md` — generated quotable figures. `analysis.md` may only
  quote numbers from here.
- `analysis.md` — the narrative; must resolve every flag.
- `ttm.json` — TTM legs; required when `base_source` is `ttm_json`.
- `fundamentals.json`, `statements.json`, `segments.json`, `profile.json`
  — SEC-derived enrichment. `statements.json` is the full cash-flow and
  balance-sheet history; use it to cross-check the CSV.

Method in one line: OE = operating cash flow − total capex − stock-based
compensation. Base OE/share = median of the last 3 fiscal years, or a TTM
figure when the last FY is stale. Five probability-weighted scenarios give
the headline IRR. Tiers: S ≥ 25%, A 20–25%, B 15–20%, C 10–15%, D < 10%,
F = no positive normalized OE. Hurdle prices: IV@15 (B), IV@20 (A), IV@25
(S).

## Arithmetic you can redo from the diff

Do these for every scored folder in the PR. They catch most fake tiers.

1. **OE per row.** For each of the last 3 fiscal years in the CSV:
   `oe_conservative == ocf − capex − sbc`. Then the base: median of the
   last three `oe_conservative / shares_diluted` (× `ads_ratio` for ADS
   filers) must equal `base_oe_per_share` when `base_source` is
   `median_of_last_3_fy_oe_per_share`; when it is `ttm_json`, `ttm.json`'s
   legs must give it; when it is `agent_supplied_ttm_override`, the
   `base_override` construction in `analysis.md` must reproduce it.
2. **Share scale.** `shares_diluted` across the CSV's years must move by
   less than ~3× year to year unless a split or reverse split is named in
   `analysis.md`. A single year 1,000× off is a units defect (filers tag
   thousands as units). Base OE/share above ~20× the price, or below 0.1%
   of it, is the same defect. This class produced fake Tier S results
   (NTNX, VIV); it is always P1.
3. **ADS market cap.** `market_cap_est` must equal
   `price × shares_diluted_latest ÷ ads_ratio`. The engine has multiplied
   the ADS price by the ordinary share count before (VOD 10×, JD 2×); when
   `score.json.market_cap_b` disagrees with the cap implied by the price and
   the ADS count, flag it and note that `in_scope_under_40b` and the
   HIGH_NET_DEBT diagnostic are then wrong too.
4. **Capex completeness.** This is where 20-F filers and companies with
   custom XBRL tags go wrong (JD: one of four capex lines read, capex
   understated 2–6×; PFG and TKO: capex on an extension tag the feed
   drops). Check, in order:
   - `capex_assumed_zero` true, or `capex_tag` blank, in any of the last 3
     years with no `capex_override` → P1 (a DATA_GAP that was not raised).
   - `capex / da` below ~0.5 for three straight years at a company that
     owns assets (retail, logistics, telecom, manufacturing, casinos,
     utilities) → P1 until `analysis.md` explains it from the cash-flow
     statement. Asset-light software can be lower.
   - When `statements.json` is in the PR, its cash-flow capex line(s) for
     the same years must sum to the CSV's `capex`. A gap is P1.
   - A 20-F / 40-F filer whose `capex_tag` is a single `PaymentsToAcquire…`
     tag deserves a comment asking whether the filing has other investing
     lines (construction in progress, land use rights, intangibles,
     spectrum). Say "cannot verify from the diff" if nothing in the PR
     shows the statement.
5. **Net debt.** `net_debt_latest` must equal `debt_current + debt_lt −
   cash` from the CSV's latest row. If the CSV's `debt_lt` is blank or
   tiny while `statements.json` or `fundamentals.json` shows borrowings,
   the engine read the wrong tag (FISV: $0.4B recorded against $28B).
6. **Tier and band.** `tier_by_numbers` must match the band of
   `implied_irr_weighted`; `tier_final` must equal it unless
   `tier_override` is set. `irr_bear ≤ implied_irr ≤ irr_bull`, and each
   scenario's IV must rise from super bear to super bull. `probs_used`
   sums to 1. `engine_release` must be present; a score with
   `engine_version` 5 and no `engine_release` is a pre-5.4 run and must
   not claim the band or alert fields.
7. **Base year choice.** When `BASE_DIVERGENCE` fires (latest FY vs 3-year
   median differ a lot), `analysis.md` must say which one is distorted and
   why, with the cash-flow line that explains it. "Working-capital timing"
   with no figure is not a resolution (LVS: the real cause was an $848M
   land-premium payment in operating cash flow). A base year that still
   contains a sold or discontinued business is P1 (VOD).

## Overrides

Every override in `judgment.json` needs `{value, source, reason, kind}`:
- `filing`: the value comes from the company's own filing; the source must
  name the form, period and the statement line.
- `estimate`: only within 0.1×–10× of the last filed value for that field
  (anchor in the CSV / `dcf_numbers.json`).
- `base_override`: built only from figures printed in that PR's
  `dcf_numbers.json` / `ttm.json` / CSV, with the construction shown in
  `analysis.md`, and the arithmetic must reproduce.
- `ads_ratio`: only when stated in the filer's own 20-F/40-F, and the
  filing citation must be in `reason`.
- `tier_override`: a written reason is required, and the reason must be
  consistent with the numbers it cites. An override that lowers the tier
  while the narrative calls the numbers IRR an "artifact" or "upper bound"
  must give the figure it rests on; "materially lower" with no number is
  P2. An override may never raise a tier above the band of the
  numbers without a sourced base figure.

Each override must also appear in `_system/overrides_registry.json` with
its measured base/IRR impact. `overrides_applied` in `dcf_numbers.json`
must list the same keys as `judgment.json`. Overrides only fill periods
with no filed value: an override that claims to correct a filed figure
without a `base_override` has not changed the engine's result — check
`dcf_numbers.json` to see whether it actually applied.

## Flags and confidence

Every entry in `fragility_flags` must be addressed by name in `analysis.md`
with a resolution, not a restatement. The flags: `STALE_FY`,
`BASE_DIVERGENCE`, `NI_OCF_DIVERGENCE`, `WIDE_SCENARIO_SPREAD`,
`OE_VOLATILE`, `BASIS_BREAK_SUSPECT`, `BUYBACK_TAILWIND`, `IRR_AT_FLOOR`,
`TIER_BAND`,
`HIGH_NET_DEBT`, `BIG_NET_CASH`, `FX_CONVERTED`, `USD_TRANSLATIONS_USED`,
`ADS_RATIO_APPLIED`, `CASH_INCLUDES_RESTRICTED`, `DEBT_TAGS_BLANK`,
`DATA_GAP:<field>`.

- `STALE_FY` resolved with "no TTM available" at a 20-F filer: ask whether
  the interim 6-K prints TTM operating cash flow and capex; the worker
  should have used it or escalated.
- `TIER_BAND` (bear and bull tiers differ): the analysis must size to the
  bear end or say why not.
- `WIDE_SCENARIO_SPREAD` or any unresolved flag: confidence must not be
  "high". Confidence "low" on an S/A name: say so explicitly, because
  alerts no longer check confidence.
- `DATA_GAP`: if SBC, capex, diluted shares or OCF is missing for ANY of
  the last 3 fiscal years and no override fills it, the company must be
  blocked with no tier. A `score.json` tier beside a non-empty `data_gap`
  is P1.

## Scenarios, growth and moat

- Growth starts should be plausible against the last two revenue and OE
  prints in the CSV. A base-case start above the company's own latest
  guidance, when `analysis.md` quotes that guidance, is P2; when the
  analysis never mentions guidance for a company that gives it, ask for the
  guidance-vs-model check `WORKER_SPEC` step 4 requires (FISV, PFG).
- Probabilities sum to 1. Default probabilities with a narrative that
  describes a specific committed capex program or a known cliff is P3.
- The moat score needs FOR and AGAINST pillars in `analysis.md` and the
  ROIC or margin history `WORKER_SPEC` step 5 requires. When
  `fundamentals.json` is in the PR, its `roic_proxy` series is the
  evidence; a moat of 7+ with ROIC below 10% needs a reason.
- Consolidated OE at a company with a listed majority-owned subsidiary
  (Sands China at LVS, JD Logistics/Health at JD): the analysis must say
  what share belongs to minority holders. Silence is P3; it is a method
  limit, not a worker error.
- Two tickers with the same CIK (dual share classes) must carry the same
  moat, probabilities and offsets; different workers choosing differently
  gives two intrinsic values for one company.

## Sector misfits (insurers, banks, REITs, utilities)

Operating cash flow at an insurer includes policyholder money; at a bank
it includes deposit and loan flows. The engine marks these `model_fit:
misfit`. For them:
- Standing policy (Andrew, 2026-10-15): the final tier is sized one notch
  down from the numbers tier with a written reason. That override is
  expected, not a finding, and the notch is not re-litigated in review.
- The written reason must carry a number: the payable-earnings measure the
  analysis relied on (operating EPS, dividends from subsidiaries, capital
  returned) or the IRR it implies. "Screens materially lower" with no
  figure is P2. Do not grade the notch itself as wrong (PFG's B stands
  under the policy even though a payable-earnings base gives C; that gap
  is a known limit of the method, listed in the analysis, not a defect).
- A misfit ranked in the top 10 by numbers IRR deserves one P3 comment
  saying the IRR shown is not the one the analysis defends.
- P&C insurers and reinsurers (Andrew, 2026-10-19): when the filer prints
  "operating income (loss) available to common shareholders", the folder
  must carry a `base_override` of kind `filing` equal to the average of the
  last five fiscal years of that line ÷ the CSV's latest `shares_diluted`,
  with the five figures and their sources in `source` and the construction
  quoted in `analysis.md` (`WORKER_SPEC.md` step 4). Check the arithmetic
  reproduces to the cent; a mismatch is P1. With that base the one-notch
  `tier_override` must NOT also be applied (double-counting the same
  correction is P2); the alert-gate suppression and low confidence stand.
  A P&C name scored on the OCF base with only the notch is P2 — ask for
  the payable-earnings base. Life insurers, banks and REITs keep the
  2026-10-15 rule.

## Ranking and history files

- `_daily/history/ranking-<date>.csv` is append-only: a PR may add
  today's file, never rewrite an earlier date's. The same holds for any
  dated file under `_daily/`. Rewriting a past date is P2 (the 2026-10-14
  ranking was overwritten once).
- Rows are ordered by live IRR, then scored IRR, by design; a name whose
  `tier_final` was overridden below its numbers tier still sorts on the
  numbers IRR, so a Tier D can rank #1 with its override displayed. That
  is not a finding. Only per-company PRs are reviewed row by row; the CSV
  appears in state PRs, where the only checks are append-only dates and
  row count = scored folders minus uncovered DATA_GAPs.
- `alert_eligible` / `exit_alert_eligible` empty in the CSV means the
  score predates make_score 5.4, not "false".

## Deliberate choices — do NOT flag these

- Missing `prices.json`, `live.json`, `street.json`, `_daily/site/data/`,
  `index.json`, `meta.json`, `latest.html`, new `ranking-*.html`:
  gitignored caches, rebuilt by `_system/refresh.py`.
- `fundamentals.json` / `statements.json` / `segments.json` / `profile.json`
  absent from a brand-new folder: enrichment runs later (the 19:07 job and
  `refresh.py --sec`). Note it as P3 only when the PR claims the page is
  complete.
- `$0` overrides with kind `filing` where the filer genuinely does not
  report the item, with the cash-flow statement cited.
- Ordinary-share counts in the CSV at ADS filers; per-ADS figures use
  `ads_ratio`.
- `queue.json` absent from company PRs; it is synced separately.
- A `tier_override` with a quantified written reason (see Sector misfits).
- The two cron files under `automation/crons/daily/` showing as deleted in
  a Windows checkout: a filename artifact, not a change.

## Comment style

One comment per concrete finding: severity, file:line, the two values that
disagree, and why it matters. Lead with P1s. Consistency and rule
violations are findings; disagreement with a documented, quantified
judgment call is not. When you suspect a filing-level problem you cannot
check from the diff (an extension-tagged capex line, a discontinued
operation inside OCF), say what the worker should look at and mark it
"cannot verify from the diff" rather than asserting it.
