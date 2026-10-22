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
   `_system/overrides_registry.json`, `_daily/history/ranking-<date>.csv`,
   and lines appended to `_system/ENGINE_BACKLOG.md` (the backlog
   exception below). (`_system/queue.json` is synced to main separately
   and never reviewed here.)
2. **Code and spec PRs** — anything under `_system/*.py`, `_system/tests/`,
   `_system/*.md`, `automation/`, `_daily/site/`.

A PR that changes `_system/*.py` or a spec together with hundreds of data
files is a P2 finding on its own: say which code lines changed and ask for
them in a separate PR. One exception: the catch-up PR that first brings the
live VM's state onto main after the 2026-10-16 merge may mix the two (it
carries spec drafts, this file and ~1,500 data files); the separation binds
from the first per-company PR after it. A second exception: an
owner-directed acceptance re-score named in the PR body (the PR #31
engine-5.5 bundle and PR #47's engine-5.6 HALO re-score) may ride with its
engine change — the PR body must say the owner directed it; do not ask for
it to be split out. Policy-bearing files are `make_score.py` (tiers,
alert gates), `dcf_engine.py` (the formula), `queue.py` (claims and pass 2),
`facts.py` and `quote_tokens.py` (engine 5.7: which runs carry the 5.7
obligations, the declared-facts and snippet rules make_score applies),
`check_quotes.py` (engine 5.7: the quote gate), `moat_scorecard.py` and
`industry_returns.py` (engine 5.7: the moat evidence rules make_score
applies and the same-ladder industry medians they read),
`fundamentals.py`'s `capital_returns_from_row` (the one ROIC / tangible
ROIC / ROE rule that fundamentals.json, statements.json and the moat
scorecard share), `interim_bridge.py` and `xbrl_instance.py` (engine 5.7:
the 6-K interim bridge rules and the annual facts read from a filing's own
XBRL instance), `share_classes.py` (engine 5.7: the declared share-class
rules), `WORKER_SPEC.md` and `SECOND_PASS.md` (what workers must do). A change to
any of them needs (a) a test in `_system/tests/` that fails on the old code,
(b) the matching sentence in the specs and `README.md` updated, and (c) a
commit message that says what decision it implements and who made it. Grep
the specs for the old rule and list every stale passage with file:line.

**The backlog exception (Andrew, 2026-10-19, R5).** A company data PR may
also carry `_system/ENGINE_BACKLOG.md`. It must, when one of its "didnt
fix" replies names a code defect (a script, function or tag that is
wrong). The data PR may only append lines after the file's last line: a
new `### EB-<NNN>` entry, or an `### EB-<NNN> seen again` entry for a
defect already listed. Each entry carries the thread link.
`pr_worktree.py backlog-next` names the next free id. Any other change to
the file in a data PR is P2. A didnt-fix reply that names a code defect,
with no backlog entry in the same PR, is P2. A code PR that fixes an entry
edits that entry's Status line.

**Company PRs are cut per `_system/PR_PROTOCOL.md`** (`pr_worktree.py`).
The registry delta is make_score's own: only the PR's ticker's entries
change, and another ticker's entry changed is P2. The score was rebuilt
at main's code. The PR body carries a generated `## Mechanics` block that
names the origin/main sha, the release, `score.dcf_content_hash` and
"score built from this run". A company PR with no Mechanics block, or
whose Mechanics sha is not on main, is P1.

## Files in each company folder

- `financials_history.csv` — the engine input, one row per fiscal year.
  Columns include `ocf`, `capex`, `capex_tag`, `capex_assumed_zero`, `sbc`,
  `sbc_tag`, `da`, `shares_diluted`, `cash`, `debt_current`, `debt_lt`;
  engine 5.5 appends `capex_ppe`, `capex_intangibles`, `capex_source`
  (`capex` = `capex_ppe` + `capex_intangibles`) and `shares_split_factor`.
- `dcf_numbers.json` — engine output: `base_oe_per_share`, `base_source`,
  `base_oe_latest_per_share` vs `base_oe_normalized_per_share`, `g_base`,
  `scenarios`, `weighted`, `implied_irr_weighted`, `tier_by_numbers`,
  `fragility_flags`, `data_gap`, `used_tags`, `overrides_applied`,
  `ads_ratio`, `shares_diluted_latest`, `market_cap_est`,
  `net_debt_latest`, `engine_version`, `engine_release`, `content_hash`;
  engine 5.5 adds `market_cap_basis`, `share_scale`, `share_basis`,
  `share_class_mismatch`, `capex_provenance`, `sbc_provenance`,
  `used_tags.capex_components`, `override_checks.<field>.currency_basis`
  and `fx_conversion.overrides_usd_verbatim` (after the verifier round
  also `share_scale.pin_rejected` / `leverage_unverifiable` /
  `scale_breaks` / `growth_inputs_dropped` and
  `share_basis.in_history_split_facts` / `nonpositive_counts`; after the
  second, `share_scale.pin_over_price` / `growth_inputs_kept`; after the
  third, `share_scale.pin_factor_withheld` and
  `share_basis.split.confirmed_against_period`; after the fourth,
  ttm.json `sbc_reconciliation_withdrawn_legs`); engine 5.6 adds `iprd_adjustment` (the acquired-IPR&D
  one-time value adjustment: periods, `charge_per_share`, `treatment`, and `before` — the unadjusted IVs and
  IRRs; null when nothing was detected — except that a run whose window holds no charge but whose
  judgment.json declares `iprd_deferred_payment` entries records them in a minimal block,
  `deferred_payments_only`, treatment `none`, no charge: Codex review round 5 of PR #47).
  Engine 5.7 adds:
  - `sector_model` on every run: {sector, sic, sic_description,
    sic_source (`edgar_submissions` | `fundamentals.json` |
    `profile.json` | null), sic_class, misfit, basis (the rules that
    fired: `sector`, `sic`, both or none), sector_set_aside_by_sic}.
  - `moat_trend` and `hold_years` (top level and in `inputs`, with
    `hold_rule`), and `scenarios.*.hold_years`: the growth hold each
    scenario ran.
  - `share_classes`: null unless judgment.json declares share classes.
    A declared run records the applied periods (filed, declared and total
    counts, the exchange test), the zero / `in_filed_count` / unused
    periods, `latest`, `ttm`, `market_cap`, `nci_check` and `cap_check`.
    On a declared run `market_cap_basis.shares_source` ends
    `+share_classes` and `iprd_adjustment.shares_basis` is `total_units`.
  - `up_c_check`: the `UP_C_SUSPECT` detector's record, on every run.
  - `annual_from_instance`, when a candidate annual filing was checked,
    or `{applied: false, checked: false, reason}` when the EDGAR
    submissions fetch failed (absent otherwise): {applied, checked, form, accession,
    filed, report_date, periods_added, companyfacts_latest_annual_end,
    instance_url, instance_sha256, facts_merged, conflicts, facts_sha256,
    cache, reason}.
  - `capex_provenance.<FY>.software` (the capitalized-software part of
    the intangible leg, per tag) and the dropped reasons `ppe_duplicate`,
    `in_ppe_total` and `subclass_alone` (check 4).
  - `ttm_inputs.ttm_engine_release`: the release that built ttm.json,
    recorded when the run's basis read ttm.json.
- `judgment.json` — the worker's decisions: `moat_score`, `moat_for` /
  `moat_against`, `probs_used`, `confidence`, `tier_override` +
  `tier_override_reason` (on a sector misfit only below the notched tier;
  Sector misfits names the one exception), per-field overrides as top-level keys
  (`capex_override`, `sbc_override`, `shares_override`, `base_override`,
  `ads_ratio`; each `{value, source, reason, kind}`, and since engine 5.5
  an optional `currency: "USD"` on a kind `filing` override; since Codex
  review round 15 of PR #47 a plain `base_override` pinned through
  `--base-oe-ps` at a value that is not ttm.json's figure carries
  `basis_window` — `{window: "ttm", ytd_current_period}` or
  `{window: "fy"}` — on a 5.6 run),
  `share_class_mismatch` (5.5: `true` or `{value: true, source, reason}`;
  any other shape is malformed and make_score refuses it),
  `second_pass` when pass 2 ran. Engine 5.7 adds:
  - `misfit_notch_reason`: required on a 5.7 run of a notched sector
    misfit. It is a string that carries a number.
  - `moat_scorecard` `{version, business_type, business_type_reason,
    sources, pillars, supporting, volume_price, moat_divergence_reason,
    low_roic_reason, high_return_low_moat_reason, erosion_rebuttal,
    widening_declined}`: required on a 5.7 run, and shape-checked
    whenever present. `widening_declined` is a non-empty string or null:
    why a measured widening is a cycle or a recovery. It needs no number,
    because it only lowers the value.
  - `interim_bridge` (the declared 6-K interim bridge; schema in
    `_system/examples/interim_bridge.example.json`) or
    `interim_bridge_declined {reason (with a number), report}`, never
    both.
  - `share_classes` `{basis: up_c_exchangeable_units |
    multi_class_common, traded_class, reason, classes: [{name, holder,
    exchange_ratio, ratio_source, periods: [{period_end, value,
    count_basis, kind: filing | calc, accession, source, snippet,
    in_filed_count?, zero_event? + event_date?, split_basis?}]}]}`, with
    the optional `ack_reason`, `nci_gap_reason`, `cap_gap_reason` and
    `diluted_gap_reason`. Beside it: `up_c_suspect_reason`,
    `shares_override.share_basis` (`traded_class` | `all_classes`) and
    `base_override.share_basis` (`total_units`) / `share_period`.
  - `ttm_rejection_reason`: one string that names the distorting
    cash-flow line with a number. It is required, and allowed only, on a
    STALE_FY run whose published base is the median or a declared pin
    beside a TTM for its latest FY. The insurer payable pin
    (`--base-judgment`) is exempt: it needs no reason and allows none.
  - `ttm_unavailable_reason` (default Q14): ttm.py's exit-3 line, quoted
    verbatim. It belongs at a STALE_FY 10-K filer with no TTM for its FY,
    or beside a stale ttm.json for the FY that ttm.py can no longer
    rebuild.
  - `capex_unlisted_ack` `{"<tag>": "<reason with the figure>"}` and
    `capex_override.software_included` (check 4).

  On a 5.7 run the reason strings cite declared facts as `[F#]`:
  `tier_override_reason`, `misfit_notch_reason`, a plain `base_override`'s
  reason and source, the moat-scorecard reasons, the share-class reasons,
  `ttm_rejection_reason` and the `capex_unlisted_ack` reasons. make_score
  refuses an untraced number in them. It refuses a reason with no number
  (a plain pin's text is exempt) and a reason that rests only on
  third-party facts. It refuses a hand base pin whose reason traces only
  to the pin itself: the pin needs an engine figure other than the pin,
  or a cited filing / release / folder fact tagged `base_override`.
  Numbers inside worker text that the engine echoes in its flags
  (`ads_ratio.source`, an override's source) never count as engine
  figures.
- `score.json` — generated ONLY by `make_score.py`: `tier_final`,
  `tier_by_numbers`, `implied_irr`, `iv_at_15`, `irr_bear` / `irr_bull`,
  `tier_bear` / `tier_bull`, `alert_eligible`, `exit_alert_eligible`,
  `engine_release`, `in_scope_under_40b`, `model_fit` (sector OR EDGAR SIC
  since 5.7); since 5.5
  `market_cap_b` carries `market_cap_basis`,
  `in_scope_corrected_by_make_score` marks a scope make_score corrected,
  and `net_debt_to_normalized_oe_ads_basis` is a pre-5.5 ADS record's
  net-debt ratio on the ADS basis; since 5.6 `iprd_adjustment` whenever the
  engine recorded the block — any treatment, including `none`,
  `no_value_to_adjust`, `not_applied_share_count_unverified`,
  `awaiting_cash_flow_check`, `non_usd_no_rate` and
  `amortized_in_base` (the charge; the weighted IV@15/20/25 and IRR
  before → after only when a one-time deduction ran) — and, since Codex
  review round 15 of PR #47, a `deferred_payments_only` block copied as a
  minimal one (treatment `none`, `total` / `charge_per_share` 0, no
  periods, the rolled-out list), which every consumer reads as no charge.
  `dcf_content_hash` names the engine run the score was built from. Engine
  5.7 adds:
  - `misfit_notch` on every sector misfit, applied or not, with the
    reason; `misfit_sector_set_aside` when a SIC set a misfit universe
    sector aside. `tier_override_reason` is present only for an override
    in force: a legacy one-notch override's text is now
    `misfit_notch.reason`.
  - `key_numbers_sha256` (the hash of key_numbers.md as make_score wrote
    it), `declared_facts`, `method_runs` and `previous_score`.
  - `moat_evidence` on every rebuild: the sources and their caps; the
    governing return with ROIC, tangible ROIC, ROE and ROA side by side
    (ROE `n/m (negative equity)` where equity is zero or below); industry
    structure on same-ladder SIC peers; the four mechanical pillars and
    the seven declared pillars; the core evidence, the supporting
    adjustment, the evidence score and the gap; the `MOAT_EROSION`,
    `ROIC_DENOMINATOR_UNSTABLE` and `IPRD_CHARGE_IN_WINDOW` flags; the
    gates; the bad-moat lint; `gate_drift` on a rebuild; and the trend
    test both ways (`fade`: the direction, the guards, the hold a 5.7 run
    must run, the engine's recorded trend, `in_sync`, the counterfactual
    at the holds that matter). Its `status` is `report_only` on pre-5.7
    output. On a 5.7 record score.json also copies `moat_trend` /
    `hold_years` beside `cap_years`.
  - `interim_bridge` (the declaration's descriptors: currency, hash,
    periods, report, rates, the estimate / unverified / XBRL-verified
    legs, a like-for-like summary, `iprd_interim_scan`) and
    `interim_bridge_declined`. `fragility_flags` may carry
    `TTM_DECLARED_INTERIM`, make_score's own flag (never in
    dcf_numbers.json).
  - `base_alternatives`: the published base beside every other base
    computed for the run (annual median, TTM, declared-interim TTM). Each
    entry has base OE/share, weighted IRR, tier by numbers, IPR&D charge,
    role (published / rejected / alternative), why and note. make_score
    replays the rejected TTM, or the median beside a STALE_FY TTM. For a
    6-K bridge the block holds the declared-interim published entry beside
    the measured annual-median alternative. `ttm_rejection_reason` and
    `ttm_unavailable_reason` are copied in.
  - `share_classes` on a declared record: the declaration measured both
    ways (base_used, replay pin and scale; base, weighted IRR, tier, cap
    and scope on the filed traded class and on total units;
    raises_tier), plus latest, ttm, nci_check and cap_check. `up_c_check`
    {suspect, s, suppressed_by, waived_reason} is on every 5.7 record.
  - `alert_suppressed_reason` may read "share-class declaration raises
    the tier (… on the filed class → … on total units)". Under default
    Q16 it may read "tier rests on a TTM rejection …": a TTM rejection
    lifted the published tier above the rejected TTM's into S / A.
- `key_numbers.md` — generated quotable figures. It is never hand-edited:
  score.json `key_numbers_sha256` proves it. The engine sections come
  first. Since 5.7 they also hold the price-vs-IV and P/OE lines, "Base
  alternatives" (after the acquired-IPR&D section), the return / margin
  series and the Filed history table (after Growth & moat), the
  probability weights, and "Method runs" (saved runs and the previous
  score). Then come "Moat scorecard" and "Interim bridge", and last
  "Declared facts (not engine output)", rendered from `facts.json`. The
  Moat scorecard section prints only generated numbers, all quotable, and
  no worker free text. Text inside “…” is worker text echoed back, never
  a source. Since engine 5.7 every number in `analysis.md` must appear in
  key_numbers.md, `dcf_numbers.json`, `ttm.json` or a saved method run,
  or be a declared fact rendered here. `_system/check_quotes.py` checks
  it, and `queue.py done` / `pass2-done` refuse a 5.7 run that fails.
- `analysis.md` — the narrative; must resolve every flag.
- `ttm.json` — TTM legs; required when `base_source` is `ttm_json`.
  `basis: "declared_interim"` marks a 6-K bridge that `ttm.py --interim`
  built from judgment.json `interim_bridge`. make_score re-verifies its
  declaration hash, arithmetic, legs, FY leg and ADS ratio. It also
  re-runs the bridge's rules on the declaration
  (`interim_bridge.declaration_rule_problems`, the bundle ttm.py runs).
  A `--base-oe-ps` copy of its figure is refused. On a 5.7 STALE_FY run
  whose base is not the TTM, ttm.json is the rejected alternative
  make_score prices (`base_alternatives`).
- `facts.json` (engine 5.7) — the worker's declared facts: numbers the
  engine cannot produce. Each fact is `{id F<n>, label, value, unit,
  scale, precision, period, kind folder|filing|release|third_party, type
  actual|guidance|estimate|metric|event, metric?, source, snippet,
  used_for, calc?}`. make_score verifies every `folder` fact against the
  named file and reproduces `calc` facts. It refuses a filing / release /
  third-party fact that repeats a folder figure. It checks that a
  non-folder fact's snippet (at most 24 words) contains the number.
- `dcf_numbers_<label>.json` (engine 5.7) — a saved engine run
  (preliminary or exploratory): a byte copy made by
  `check_quotes.py --save-run`. Its content_hash must verify and equal
  the one score.json `method_runs` records under its label. A run
  replaced after make_score needs a make_score re-run. A method range
  quoted in analysis.md comes from here.
- `annual_instance.json` (engine 5.7) — the annual facts the engine read
  from a 10-K / 20-F / 40-F's own XBRL instance when EDGAR companyfacts
  lacks that fiscal year. It is a committed SEC file. It is required, with
  the same accession, instance hash and facts hash, when dcf_numbers.json
  `annual_from_instance.applied` is true.
- `fundamentals.json`, `statements.json`, `segments.json`, `profile.json`
  — SEC-derived enrichment. `statements.json` is the full cash-flow and
  balance-sheet history; use it to cross-check the CSV.

Method in one line: OE = operating cash flow − total capex − stock-based
compensation (engine 5.6: acquired in-process R&D expensed at acquisition is
deducted once from every IV and added to the IRR price, never from the base). Base OE/share = median of the last 3 fiscal years, or a TTM
figure when the last FY is stale (10-Q YTD facts via ttm.py, or a declared
6-K interim bridge at a 20-F / 40-F filer via `ttm.py --interim`). Since
engine 5.7 the worker may reject that TTM only with `ttm_rejection_reason`,
which names the distorting cash-flow line with a number; make_score then
records both bases in `base_alternatives`. Five probability-weighted scenarios give
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
   On a declared run (`share_classes`, engine 5.7), `shares_diluted` is
   the total: the filed traded count plus the declared units. `shares_tag`
   then ends `+SHARE_CLASSES`, and `share_classes.applied` lists both
   counts. Recompute `filed + units` per year from the declaration. An
   `in_filed_count` year adds nothing. A history year with no declaration
   keeps its filed count and a blank `oe_per_share`, so it is outside the
   median and the CAGRs.
2. **Share scale.** `shares_diluted` across the CSV's years must move by
   less than ~3× year to year unless a split or reverse split is named in
   `analysis.md`. A single year 1,000× off is a units defect (filers tag
   thousands as units). Base OE/share above ~20× the price, or below 0.1%
   of it, is the same defect. This class produced fake Tier S results
   (NTNX, VIV); it is always P1. Since engine 5.5 the engine runs the
   check itself and records it in `share_scale` (base OE/share above 20×
   the price, the latest diluted count outside 1/100–100× the latest
   cover-page dei count, or — test `cap`, two-sided — price × that
   count ÷ ads_ratio outside 1/100–100× of universe.csv's market cap,
   skipped at a 20-F / 40-F filer with no applied ads_ratio): it raises
   `DATA_GAP:shares — SHARE_SCALE` and
   emits no tier unless a qualifying pin carries the base — a
   `--base-oe-ps` value that judgment.json declares as a `base_override`
   with no `basis`, equal within 0.1%, and itself within 20× the price.
   Then it scores, flags `SHARE_SCALE_SUSPECT` and rescales the market cap
   by `share_scale.scale_factor` (basis `dei`, `pin` or `universe`; a
   factor that would put the cap outside 1/100–100× of universe.csv's cap
   is rejected, `share_scale.factor_rejected`). A `SHARE_SCALE_SUSPECT` score whose
   judgment.json `base_override` does not match `inputs.base_oe_ps_arg`
   that way is P1 (the engine gaps that run); a pin the engine rejected is
   named in `share_scale.pin_rejected`. A pin-rescued tier exists only
   because of that override: make_score closes both alert gates
   (`alert_eligible` / `exit_alert_eligible` false, "tier exists only
   because of a judgment override"; either gate open on such a score is
   P1) and the registry `base_override` event carries `kind`,
   `base_used: declared_pin`, the median → pin and `unblocks_tier: true`. The pin itself is tested too: a
   `--ttm`, `--base-oe-ps` or `--base-judgment` pin above 20× the price
   is the defect (`share_scale.pin_over_price`) and the run gaps, however
   clean the annual counts (check 2 above: a tier on such a base is P1).
   When the counts break scale inside the growth window (adjacent counts
   among the last four more than 100× apart),
   `share_scale.growth_inputs_dropped` lists the share-count CAGR and,
   when its two endpoint counts are more than 100× apart, the OE/share
   CAGR left out of the growth blend (`growth_inputs_kept` names an
   OE/share CAGR whose endpoints share one scale, whatever lies between
   them); a rescued defect with no scale factor and no dei that confirms
   the count (none, one the latest count fails by more than 100×, or one
   that agrees with a latest count on the same scale as the median year
   test (a) found mis-scaled — a cover page filed in thousands too) sets
   `share_scale.leverage_unverifiable` (no net-debt ratio, no
   HIGH_NET_DEBT / BIG_NET_CASH test; the market cap is then price × the
   filed count and unverified); the pin's power of ten is applied only when the median year's
   count and the latest count share one scale — those two counts are
   compared, not the years between (`share_scale.pin_factor_withheld`
   names one withheld for a break between them; a `pin`-basis factor
   beside such a break is P1 — the cap is off by that factor). A filed
   share count ≤ 0 counts as not filed (`share_basis.nonpositive_counts`,
   which also lists a cover-page zero skipped for a fallback year): a
   tier beside a zero `shares_diluted` in the last 3 years is P1 (TLN). A
   split ratio filed after the latest FY end and confirmed by a later
   cover-page count is applied to the history (`SHARE_BASIS_ADJUSTED` — it
   lists every adjusted year and any `OVERRIDE` year it did not rescale,
   whose `shares_override` must already be on the post-split basis —, CSV
   `shares_split_factor`, `share_basis.split` — confirmed against the
   latest filed count, `confirmed_against_period`, never an override).
   An unconfirmed post-FY
   split fact changes nothing and raises no flag, but key_numbers.md
   prints a "Share basis: unconfirmed split fact" line that `analysis.md`
   must resolve. Split facts dated on or before the FY end are only
   recorded (`share_basis.in_history_split_facts`): a history count from
   a filing older than such a split can still be on the pre-split basis
   (TPL), so a share-count jump of about the ratio inside the last four
   years makes `DILUTION` / `BUYBACK` an artefact. A cover-page count
   and the diluted count with one more than 25% below the other
   (dei ÷ diluted outside 0.75×–1.333×) with no filed split is `SHARE_BASIS_DIVERGENCE` and prices the
   cap on the cover-page count at a 10-K filer; at 20-F / 40-F / ADS
   filers it is only recorded (`share_basis.divergence`).
3. **ADS market cap.** `market_cap_est` must equal
   `price × shares_diluted_latest ÷ ads_ratio`. The engine has multiplied
   the ADS price by the ordinary share count before (VOD 10×, JD 2×); when
   `score.json.market_cap_b` disagrees with the cap implied by the price and
   the ADS count, flag it and note that `in_scope_under_40b` and the
   HIGH_NET_DEBT diagnostic are then wrong too. Facts since the fix: the
   engine divides by the ratio (main, 2026-10-18; `market_cap_basis`
   records `shares_used`, `shares_source`, `ads_ratio` and the formula —
   the count is `shares_diluted_latest` unless `shares_source` reads
   `diluted_latest_scale_corrected` or `dei_latest`), and engine 5.5 puts
   `net_debt_to_normalized_oe` (HIGH_NET_DEBT / BIG_NET_CASH) on the same
   per-ADS basis. make_score also divides, but only for pre-5.5 output
   whose `market_cap_est` equals price × `shares_diluted_latest` (the
   uncorrected formula): score.json `market_cap_b` is then the corrected
   cap with `market_cap_basis: ads_corrected_by_make_score`, and a scope
   the old cap implied is rewritten (`in_scope_corrected_by_make_score:
   true`, registry event `scope_correction`). A cap that already divides
   is never divided twice, and an `ads_ratio` of 1 is never "corrected"
   (the basis stays `diluted_latest`). The net-debt ratio is corrected
   apart from the cap: no engine before 5.5 divided the normalized-OE
   total by the ratio, so for every pre-5.5 record with an applied ratio
   other than 1, whatever state its cap is in, key_numbers.md prints the
   ratio × `ads_ratio` beside the engine's figure, names any
   HIGH_NET_DEBT / BIG_NET_CASH crossing, and score.json records
   `net_debt_to_normalized_oe_ads_basis` (TX 1.04× → 10.44×, LTM 0.00× →
   3.33×: HIGH_NET_DEBT would fire). That is the figure an analysis's
   leverage discussion should use; the recorded `fragility_flags` predate
   the fix. On a declared run (`share_classes`, engine 5.7),
   `shares_diluted_latest` is total units:
   `market_cap_basis.traded_shares` + `declared_units`.
4. **Capex completeness.** This is where 20-F filers and companies with
   custom XBRL tags go wrong (JD: one of four capex lines read, capex
   understated 2–6×; PFG and TKO: capex on an extension tag the feed
   drops). Check, in order:
   - `capex_assumed_zero` true, or `capex_tag` blank, in any of the last 3
     years with no `capex_override` → P1 (a DATA_GAP that was not raised).
   - `capex / da` below ~0.5 for three straight years at a company that
     owns assets (retail, logistics, telecom, manufacturing, casinos,
     utilities) → P1 until `analysis.md` explains it from the cash-flow
     statement. Asset-light software can be lower (its capitalized
     development is in capex since 5.7).
   - When `statements.json` is in the PR, its cash-flow capex line(s) for
     the same years must sum to the CSV's `capex`. A gap is P1.
   - A 20-F / 40-F filer whose `capex_tag` is a single `PaymentsToAcquire…`
     tag deserves a comment asking whether the filing has other investing
     lines (construction in progress, land use rights, intangibles,
     spectrum). Say "cannot verify from the diff" if nothing in the PR
     shows the statement.
   - Engine 5.5 records (facts for the checks above): `capex_tag` may be a
     `+`-joined list of the tags summed — the additive PP&E components
     (E&P, other PP&E, construction in process, productive assets,
     capital improvements) for a year with no PP&E roll-up filed, plus
     intangible purchases (`PaymentsToAcquireIntangibleAssets`,
     `PaymentsToAcquireOtherIntangibleAssets`, IFRS
     `PurchaseOfIntangibleAssetsClassifiedAsInvestingActivities`), which
     are counted as capex except on an `OVERRIDE` year (an intangible fact
     repeating a value the same tag files on a context longer than 380
     days is dropped as a cumulative total — reason `cumulative_duplicate`
     in `capex_provenance`; ECHO). `capex` = `capex_ppe` +
     `capex_intangibles`, except on an `assumed_zero` row: the intangible
     leg is not added where no PP&E leg was filed, so `capex` stays 0 and
     `capex_tag` blank (the first check above still reads the row) while
     `capex_intangibles` and `capex_provenance`
     (`intangibles_not_added: no_ppe_leg`) record the amount. Negative
     intangible facts are dropped (`negative`) and $0 ones never join
     `capex_tag`. A component equal within 0.5% to the sum of two or more
     of the year's other components is kept as the total and the parts
     dropped (`parts_of_total`; GLPI FY2024); other near-equal pairs are
     still summed — when two summed lines look like the same spending
     (GLPI FY2023 / FY2025, GSAT FY2024–25 other PP&E vs intangibles), say
     "cannot verify from the diff" and ask the worker to check the 10-K
     investing section. `capex_source` says how the PP&E leg was built
     (`rollup`, `components`, `components_mixed_filings`, `override`,
     `assumed_zero`); `capex_provenance` in `dcf_numbers.json` lists each
     tag's value per year. The capex / D&A
     check is now also an engine flag, `CAPEX_COVERAGE_LOW` (below 50% of
     D&A in each of the last 3 FY at a filer with positive PP&E). In
     `ttm.json` the FY and prior-YTD legs add their intangible purchases
     only when the FY leg files at least the prior-YTD amount (or the prior
     YTD files none); otherwise neither does
     (`capex_components.<leg>.intangibles_not_added: remainder_unknown`,
     with a warning) and the current-YTD leg still adds its own, so the
     TTM intangible contribution is never negative (BAX). Likewise the
     SBC reconciliation never lowers TTM SBC below the unreconciled
     figure: a reconciled prior-YTD leg that would is kept on
     `ShareBasedCompensation` (`sbc_reconciliation_withdrawn_legs`).
   - Engine 5.7 (Andrew, 2026-10-19, R8 / R9). The PP&E components now
     include `PaymentsToAcquireMachineryAndEquipment` (KNX),
     `PaymentsToAcquireMiningAssets` and
     `PaymentsToAcquireFurnitureAndFixtures`. The last two are
     sub-classes: they are read only beside another component in the same
     unit. Filed alone they show as `subclass_alone` in
     `capex_provenance.<FY>.dropped`, and the year has no PP&E leg (a
     DATA_GAP:capex in the last 3, never a silent small leg). Capitalized
     software and development (`PaymentsToDevelopSoftware`,
     `PaymentsToAcquireSoftware`, `PaymentsForSoftware`, IFRS
     `PaymentsForDevelopmentProjectExpenditure`) are capex inside
     `capex_intangibles`, listed per tag in
     `capex_provenance.<FY>.software`. They are dropped as
     `ppe_duplicate`, `in_ppe_total` or `parts_of_total` when a PP&E or
     intangible figure already contains them. Two cases need a question
     (say "cannot verify from the diff" when the PR does not show the
     statement). First, the PP&E leg is a single combined line such as
     `PaymentsToAcquireProductiveAssets` and a software line is added on
     top: ask whether the combined line already includes software.
     Second, `PaymentsToAcquireIntangibleAssets` and a software line are
     both added and the intangible figure is the larger (FIG FY2025, SN):
     ask whether it already contains the software. A filer whose software
     appears only as `CapitalizedComputerSoftwareAdditions` (PAYC, CPAY,
     DOCU, …) gets nothing added: check that its PP&E purchase line
     includes the capitalized software. A `capex_unlisted_ack` must name a
     real reason with the figure (an acquisition, a deposit, a fleet). An
     ack that calls the filer's own capex line "not capex" is a defect.
     `CAPEX_UNLISTED_COMPONENT_OVERRIDDEN:<tag>` is not refused: an unread
     capex-like tag is filed in a year with no PP&E leg, and an override
     fills it (or the year is DATA_GAP:capex). If the tag is the filer's
     capex line, the override is a stopgap and the engine's list is wrong:
     say so and route the list fix to the main agent. HUT, HTHT and RL
     carried overrides of the unread M&E line for exactly this reason
     before 5.7; RRC's override covers
     `PaymentsToAcquireOilAndGasPropertyAndEquipment` today.
5. **Net debt.** `net_debt_latest` must equal `debt_current + debt_lt −
   cash` from the CSV's latest row. If the CSV's `debt_lt` is blank or
   tiny while `statements.json` or `fundamentals.json` shows borrowings,
   the engine read the wrong tag (FISV: $0.4B recorded against $28B).
6. **Tier and band.** `tier_by_numbers` must match the band of
   `implied_irr_weighted`. `tier_final` must equal it — or, on a sector
   misfit, `misfit_notch.tier_after_notch` — unless a judgment
   `tier_override` is in force. On a misfit an override in force sits
   below the notch (or at it, in check 8's acquired-IPR&D share-count
   case), and score.json then carries `tier_override_reason`.
   `irr_bear ≤ implied_irr ≤ irr_bull`, and each
   scenario's IV must rise from super bear to super bull. `probs_used`
   sums to 1. `engine_release` must be present; a score with
   `engine_version` 5 and no `engine_release` is a pre-5.4 run and must
   not claim the band or alert fields. Since 5.5, make_score rebuilding a
   score on output from another engine release sets `alert_eligible` and
   `exit_alert_eligible` false ("engine output predates release <the current release> (5.7.0 since Andrew's 2026-10-19 rulings; 5.6.0 the acquired-IPR&D release before it) —
   re-run the engine before an entry / exit alert") and carries
   `override_impact` from the prior score.json
   (`impact_carried_from_prior_score: true`) or records it as not
   measured, instead of replaying the override through the new engine.
   The insurer payable pin follows the same rule: its registry
   `base_override` event is carried from the prior event (same pinned
   base and weighted IRR) or recorded as not measured, labelled
   `base_used` `payable_5y`. A `--base-oe-ps` pin equal to a declared
   `base_override` (no `basis`) that is not ttm.json's figure is
   measured as `base_used` `declared_pin` (pin held constant, engine
   replayed with field overrides off), never through ttm.py. A `--ttm`
   pin on a declared 6-K bridge (engine 5.7) is measured as `base_used`
   `declared_interim`: the pin is held constant, the FY override fields
   are zero-filled from ttm.json `override_counterfactual`, and the engine
   is replayed with field overrides off and the run's IPR&D hold — never
   through ttm.py.
   A company PR whose dcf_numbers.json is from an older engine release
   than main's is acceptable only as a make_score rebuild at main's
   release (lane default Q12 (b), main agent 2026-10-21, pending Andrew).
   The misfit notch then applies mechanically, both alert gates are closed
   by the stale-release rule, and no directed engine re-run is needed
   (Andrew's Q3 ruling stands). Its Mechanics block says "the engine
   output predates release <rel>", and the PR body says so too. A
   stale-release score presented as current (no such line) is P1 (MOH
   #37, ESTC #35). A `rebuild/*` PR (a bulk make_score rebuild) is the
   same case for many folders.
7. **Base year choice.** When `BASE_DIVERGENCE` fires (latest FY vs 3-year
   median differ a lot), `analysis.md` must say which one is distorted and
   why, with the cash-flow line that explains it. "Working-capital timing"
   with no figure is not a resolution (LVS: the real cause was an $848M
   land-premium payment in operating cash flow). A base year that still
   contains a sold or discontinued business is P1 (VOD).

8. **Acquired IPR&D (engine 5.6 — Andrew 2026-10-19 decided the one-time value deduction, cash preferred,
   the 5% flag, recurrence and the impairment non-goal; the rest of this check enforces main-agent / review
   additions awaiting his ratification).** When `dcf_numbers.json` carries
   `iprd_adjustment` with treatment `one_time_value_deduction`: `charge_per_share` must equal
   `total ÷ shares_denominator × ads_ratio` (the denominator is ttm.json `ttm_shares_diluted` for a TTM
   base — a `--ttm` pin, a `--base-oe-ps` pin equal to ttm.json's `ttm_oe_per_share`, or an `iprd_amortized`
   pin on native base `ttm_json` —, else the CSV's latest `shares_diluted`, × the share-scale factor when
   `shares_source` is `diluted_latest_scale_corrected`; [Codex review round 30 of PR #47] a TTM base's figures
   are never the latest-FY count: without a positive `ttm_shares_diluted` the engine refuses a TTM run carrying
   an acquired-IPR&D figure per share, `BAD_TTM_SHARES` — so a TTM base whose `shares_source` is not
   `ttm.json ttm_shares_diluted` is P1); `total` is the sum of the periods' `deducted`; every
   scenario's and the weighted IV must equal the `before` figure minus `charge_per_share`, and the base and
   the paths are unchanged (a base cut by the charge is P1 — the rule is a value deduction, never a base
   deduction). `tier_by_numbers` is the band of the ADJUSTED weighted IRR. A period with `amount_basis`
   `expense` is deducted only beside a `cash_flow_check` of presentation `added_back_paid_in_investing`
   (judgment.json `iprd_cash_flow_check`, fixer review round): its `source` must cite the 10-K's operating
   add-back and investing line — a check whose source does not show both is P1 (NBIX pays inside OCF: a
   deduction there charges OE twice), and one declaring `inside_operating_cash_flow` / `paid_in_shares` where the
   filing shows the add-back and an investing payment is P1 the other way. [Codex review round 8 of PR #47] An
   expense-basis period is excluded `already_in_capex` only beside presentation `paid_in_intangible_capex`, whose
   source must cite the intangible-purchase line the engine sums into capex that holds the payment — declared where
   the payment sits on its own investing line (HALO's custom line) it is P1 (a real charge deducted as $0); a
   `capex_overlap_note` (the period's intangible capex is at least 98% of the charge) is a hint to read the
   cash-flow statement, never an exclusion (round 21: no docstring or doc may state the size rule as the
   exclusion); a check on an expense with no FX rate names its `unit` and the native amount (round 21) — one
   whose unit is not the expense's filed unit is never applied; say "cannot verify from the diff"
   when the PR does not show the filing. A score with a period still `awaiting_cash_flow_check` cannot exist
   (make_score refuses it), nor one with a period excluded `non_usd_no_rate` beside a positive `expense_native`
   (`ACQUIRED_IPRD_UNCONVERTED`, `NEEDS_MAIN_AGENT: currency` — Codex review round 3 of PR #47) or a positive
   `cash_native` (a cash-only payment with no FX rate that could settle a charge — round 4 — or the period's
   cash outflow beside a positive expense, the preferred amount, with no FX rate: never replaced by the
   expense — round 6), or (round 24) a positive `expense_tag_unconverted` — one of two positive detector tags with
   no FX rate, which the engine never compares with the other (`expense_tags_conflict` then records each tag's
   {native, unit, usd}, no check is applied — `cash_flow_check_not_applied` — and the period deducts nothing). A
   no-rate cash-only payment after a charge whose USD remainder is unknown carries `unconverted_remainder_of`
   and is refused the same way (round 24: that gate reads the unknown remainder as well as the unpaid one). A
   `deferred_payment` period counts cash the window's earlier cash-basis charge left unpaid (BIIB), never more
   than that remainder — or, declared in `iprd_deferred_payment` against a `first_charged_period` before the
   window that companyfacts shows expensed (`first_charge_evidence` `companyfacts_expense_fact`), a cash-tag-only
   payment of that pre-window charge (round 3): its cited filing must show the deferred consideration or
   milestone paid in that period, P1 otherwise. [Codex review round 12 of PR #47] A cash-basis period carrying
   a `paid_in_shares` check (`residual_paid_in_shares`: its expense less cash, never accrued as unpaid) needs a
   source showing that residual paid in shares (a non-cash stock-consideration line), P1 otherwise; a
   `deferred_payment` carrying `deferred_payment_assumption` (matched against a residual nothing declared) whose
   analysis.md does not say how that residual was settled is P2 — one the filing shows paid in shares, deducted
   again, is P1. [Codex review round 14 of PR #47] A score with a period carrying `cash_flow_check_mismatch` (a
   declared check whose amount is not the filed expense, never applied) cannot exist on any basis (make_score
   refuses it); a `deferred_payment` period with `expense_reversal_note` (a negative detector fact, a reversal,
   beside cash matched like cash beside a $0 expense) follows the same `deferred_payment_assumption` rule above —
   [Codex review round 20 of PR #47] also when that negative fact is filed in a currency with no FX rate (the
   period keeps its `expense_native`; it is a reversal, never `non_usd_no_rate`).
   [Codex review round 15 of PR #47] A score with a cash-basis period carrying `cash_flow_check_inapplicable` (a
   matching check declaring `inside_operating_cash_flow` or `paid_in_intangible_capex` where the investing cash tag
   is filed and its outflow deducted) cannot exist (make_score refuses it, naming the presentation;
   `paid_in_shares` is still read there). [Codex review round 22 of PR #47] Nor can a score whose judgment.json
   IPR&D declarations (`iprd_cash_flow_check`, `iprd_deferred_payment`, `base_override` basis / basis_window /
   iprd_amortized figures) changed after the engine run: the run records `iprd_judgment_hash` and make_score
   refuses a mismatch; a record that predates the hash (HALO's) is refused when a declared check names a window
   period the run shows no trace of reading. A diff that edits those declarations without a fresh
   dcf_numbers.json is P1. [Codex review round 23 of PR #47] Nor can a score whose ttm.json changed after a
   pinned engine run: the run records `ttm_inputs` (ttm_oe_per_share, ttm_shares_diluted, ytd_current_period,
   ttm_input_hash) and make_score refuses any difference (round 25: recorded only when the run's basis reads
   ttm.json — null for a pin declared built on FY figures, which no ttm.json change refuses); a record that predates it (HALO's) is refused when its
   positive IPR&D charge is on a ttm.json share count or YTD window the current ttm.json no longer holds. A diff
   that regenerates ttm.json without a fresh dcf_numbers.json is P1. [Codex review round 26 of PR #47] A pin is
   ttm.json's (or a plain `base_override`'s) only within 0.1%, and a $0.00 figure only by an exact zero: a
   `--base-oe-ps` 0.004 beside a zero TTM base or a plain declaration of 0.0 is an arbitrary pin (refused); the
   half-cent band at zero is the `iprd_amortized` arithmetic's alone, and an amortized pin on the other side of
   zero from the value its figures reproduce is refused (a base <= 0 is Tier F). A period carrying `unit_conflict` (one tag filed for the period in two
   units that disagree after conversion beyond the unit-agreement tolerance, `IPRD_UNIT_TOLERANCE`: max($1, 1% of the
   larger); a positive fact outranks a zero one, the USD one is used between positive
   ones; [Codex review round 16 of PR #47] a cash-only deferred-payment period and an `ignored_cash_only` entry
   carry it too, and a unit filed only in quarters is tiled beside another unit's exact fact; round 17: so does a
   record a declaration builds from an `ignored_cash_only` payment) whose analysis.md does
   not reconcile the units against the filing is P2. [Codex review round 17 of PR #47] A period carrying
   `automatic_settlement` / `declared_residual` deducts both the cash that settled the window's unpaid remainder
   and the declared rest of the same payment (a pre-window deal's `iprd_deferred_payment`): the cited filing must
   show that rest paid for the named pre-window deal, P1 otherwise. A plain `base_override` pin
   that is not ttm.json's `ttm_oe_per_share` carries `basis_window`: `{window: "ttm", ytd_current_period:
   ttm.json's}` when the pin was built from ttm.json's TTM figures on another denominator (at a declaring filer
   the per-unit TTM base is `--ttm` itself, on `share_classes`, and a total-unit pin also states `share_basis:
   "total_units"` — the IPR&D window then reads the current-YTD leg, recorded as `inputs.base_basis_window`; the share
   denominator rule above is unchanged), `{window: "fy"}` when it was built from FY figures (NTNX, VIV). A window
   that is not the pin's construction is P1 (say "cannot verify from the diff" when analysis.md does not show the
   construction); make_score refuses a 5.6 run whose declaration lacks it or differs from the run's record, and a
   `ttm` window whose period ttm.json no longer names. [Codex review round 24 of PR #47] The declaration, not the
   number, places a pin: one declaring `{window: "fy"}`, or an `iprd_amortized` one on native_base the median,
   keeps the FY window and the latest FY count even when it equals ttm.json's `ttm_oe_per_share` within 0.1%
   (make_score checks it as a declared pin, measures its override impact on the declared branch and holds it to no
   TTM-leg override); an `iprd_amortized` one on native_base `ttm_json` reads the TTM window and ttm.json's count.
   `ACQUIRED_IPRD_UNMATCHED_PAYMENT` resolved without saying what
   the payment is (declared, or why it is not the earlier deal's) is P2. A period with `recurrence_excluded` `deferred_payment_of`
   (judgment.json `iprd_deferred_payment`, Andrew's 2026-10-20 ruling, delegated to the main agent, who decided) must be a contingent milestone or deferred
   consideration of the named deal as the cited filing shows it: a distinct deal (another counterparty or
   asset) declared as an installment so `ACQUIRED_IPRD_RECURRENT` does not fire is P1, so is a
   `contingent_total` whose value is not the unrecognized milestones / deferred consideration its cited filing
   discloses for that deal (HALO FY2025 10-K: $100.0M of Surf Bio milestones; an overstated cap lets a second
   purchase pass as an installment) and a `first_charge_evidence` `citation_only_before_companyfacts` whose cited
   filing does not show the deal expensed, and so is a declared period missing from `total` (the deferred
   payment is still deducted); a partly deferred period still counts toward recurrence; say "cannot verify
   from the diff" when the PR does not show the filing. (The engine already refuses one deal with two first
   charges, a first charge whose whole charge is itself declared deferred, an in-window first charge whose
   record carries no acquired-IPR&D expense of its own (round 29: a cash settlement, a reversal, a $0 expense), a
   declaration on a year whose whole charge has no USD figure (round 29: its own expense or cash, or a tag also
   filed in a unit with no FX rate beside the USD figure used), a declaration past the year's whole charge
   (round-29 polish reviews, `dcf_engine.iprd_own_charge_usd`: the largest of its own expense — the largest
   positive figure on any acquired-IPR&D expense tag, the parallel one too, in every unit filed — and its cash in
   every unit; EUR 100M at 1.08 filed beside the USD 40M used, or the parallel tag at $108M, makes $108M the whole
   and $40M a part; [Codex review round 30 of PR #47] "every unit filed" is every unit that disagrees with the
   figure used beyond the unit-agreement tolerance — a unit within it is the figure used, so USD 100M beside EUR
   converting to $100.7M is a $100M charge and a $100M declaration of it is whole; with three or more units filed, the tolerance applies to their spread: once the largest and smallest converted figures differ by more than it, every unit is recorded and the largest counts), a pre-window first charge
   companyfacts covers with no expense fact there, a source accession outside the original filing's years,
   a current-YTD entry, a missing or inconsistent `contingent_total`, one deal's declared amounts summing
   past its `contingent_total`, and — round 8 — an impossible date; make_score refuses a deal whose
   declarations sum below the `paid_to_date` its registry event recorded, or whose lifetime passes the cap.
   [Codex review round 26 of PR #47] It refuses an `overrides_registry.json` that is not a JSON object with an
   `entries` list of objects ("overrides_registry.json is malformed — restore it from git"), never reading or
   rewriting it as empty: a registry without `entries` read as $0 paid and was rewritten holding one ticker. A
   diff that changes the registry's shape is P1. [Codex review round 28 of PR #47] The same refusal covers any
   malformed `iprd_deferred_payment` event, for any ticker (ticker or deal not a non-empty string, an invalid
   first_charged_period, contingent_total, paid_to_date, periods or date — the message names the entry, its
   ticker and the field): a missing `deal` had been skipped, reading the deal's recorded payments as none. A
   diff that hand-edits such an event is P1. Since the round 28 re-verification it also covers an entry
   carrying such an event's fields under a misspelt, missing or other `event` name (it had passed as another
   entry and been erased), a lower-case ticker on such an event (no run reads it), and an entry that is neither
   a field override nor an event make_score writes.
   [Codex review round 9 of PR #47] The rename gap is mechanical now: make_score refuses a recorded deal declared
   with another `contingent_total` or `first_charged_period` (both immutable), and a new deal name carrying a
   recorded (or co-declared) deal's evidence — the same `first_charged_period` and a `contingent_total` source
   accession — as a renamed copy; the engine refuses a rolled-out `period` that is not one of the filer's
   fiscal-year ends. [Codex review round 10 of PR #47] Every period a deal's registry event recorded is immutable:
   make_score refuses a declaration that omits it or declares it more than $1 apart from the recorded amount
   (shrunk or grown), naming the period, and the event keeps the recorded amounts. Still P1 for review: a
   renamed deal whose evidence was changed too (a first charge or cap filing the cited filings do not show for
   it).)
   [Codex review round 8 of PR #47] A period carrying `expense_tags_conflict` (both expense tags filed with
   different positive values; the current tag is used) must be reconciled in analysis.md against the filing
   (P2 otherwise). [Codex review round 24 of PR #47] When one of them has no FX rate the two are never compared:
   each tag's entry is {native, unit, usd} and the period is gated `non_usd_no_rate` (`expense_tag_unconverted`,
   refused by make_score); two unconvertible tags in one unit compare their native figures (entries in that form).
   `ACQUIRED_IPRD_CHARGE` / `ACQUIRED_IPRD_RECURRENT` resolved without
   the deal, the cash vs stock consideration or the recurrence assessment is P2. An `iprd_amortized`
   `base_override` must reproduce native base − mean(figures) ÷ shares × ads_ratio to the cent (P1
   otherwise), its figures must be the run's FY `deducted` amounts (three; two at a filer with only two FY;
   each within $1) and the treatment `amortized_in_base` (no one-time deduction on top — both is
   double-counting, P1). Its `native_base` must be the base the one-time run scored — `ttm_json` when that
   run was `--ttm`, and always when `STALE_FY` fires and ttm.json carries a TTM base (the engine refuses the
   median there, also when the TTM is rejected with `ttm_rejection_reason`) — else the median; a native base chosen for a better tier is P1. Treatment
   `not_applied_share_count_unverified` (a share-scale defect rescued by a pin, no power-of-ten factor):
   nothing was deducted, so the published tier is the UNADJUSTED one; the score must be blocked
   `NEEDS_MAIN_AGENT` or carry a main-agent `tier_override` whose reason quantifies the hand deduction
   (total ÷ the verified share count and the adjusted weighted IRR) — resolving the flag with the deal and
   consideration alone is P1; make_score refuses the score without a `tier_override` whose reason names a
   dollar figure and a percentage (Codex review round 1 of PR #47) — whether those figures are the right hand
   deduction is this check's; reprice.py never reprices such a record (no live.json; the site shows the scored
   figures with `live_withheld` reason `iprd_share_count_unverified` — Codex review round 2 of PR #47); nor
   a run make_score refused for an unresolved charge (`dcf_engine.iprd_unresolved`; the score.json on disk is
   an earlier run's: `live_withheld` reason `iprd_unresolved` — round 6); nor, since round 11 (the main agent's
   general rule), any run its score.json was not built from, whatever make_score refused it for (a deleted
   deferred payment its registry recorded, any other refusal) or because make_score has not run yet:
   `live_withheld` reason `score_not_from_this_run` — live figures pause between an engine run and its
   make_score, so a page showing live figures beside a score from another run is P1. Since round 12 a
   score.json carrying `dcf_content_hash` is the run's only when that hash is the run's (valid) `content_hash`;
   rounded headline figures alone are identity only for a run from before release 5.6.0 (round 13: a
   current-release score.json without the hash is another run's), and the notice stands with or without a
   live.json on file (round 13: reprice.py removes it), so a page mixing an old verdict with a new run's
   forecast and no `live_withheld` notice is P1. [Codex review round 29 of PR #47, the main agent's shape] No
   live figures without the run's current score: reprice.py writes none for a folder with no score.json (an old
   one is removed), and live.json records the score it was computed against (`score_json_fresh`,
   `scored.tier_final` / `tier_override_reason` / `dcf_content_hash`), so a live.json not computed against the
   score.json on file — written before make_score scored the run, before it re-scored it (an override added or
   removed), or beside another run's same-day score — is withheld (`live_withheld` reason
   `live_not_from_this_score`, `build_site.live_score_problem`), and one from before round 29 that records no
   `dcf_content_hash` beside a score.json that carries one cannot be bound to it and is withheld too, with its own
   reason (`live_without_score_identity`, `build_site.live_score_identity_missing`; round-29 polish review: its
   note says it records no score identity and the next repricing rewrites it, never that it was computed before
   the score); a page showing a live tier beside a score it was not computed against (the numbers tier at the last
   close beside a new `tier_override`) is P1. Since 5.7 a sector misfit's live tier is one notch below its live
   numbers tier (reprice.py, from score.json `misfit_notch`; live.json carries `misfit_notch` and
   `scored.tier_after_notch`). So a misfit scored B → C reads B when the live numbers tier is A: not a finding. A
   misfit scored before 5.7 (no block) reprices as before until its rebuild.
   [Codex review round 11 of PR #47, the main agent's shape] A period whose expense or cash figure carries
   `context_basis` `aggregated_quarters` was summed from the three-month / year-to-date facts in
   `aggregated_contexts` (no fact covered the period exactly; since round 18 the unit the figure was read from, other
   tiled units under `aggregated_contexts_other_units`): those contexts must tile the period with no gap
   and no overlap, P1 otherwise. `ACQUIRED_IPRD_PARTIAL_PERIOD` (`iprd_adjustment.partial_coverage`: a tag
   filed for only part of a window period, nothing counted for it) resolved without the period's full figure
   from the filing and its effect on the IVs / IRR is P2; a material one OE never saw published without
   `NEEDS_MAIN_AGENT: iprd_partial_period` is P1. Since round 12 a $0 fact on one detector tag never hides a
   positive partial fact on the other (only a positive full-period detector fact reads the period).
   With field overrides in force, `override_impact`'s counterfactual holds the
   final run's IPR&D treatment and charge (`DCF_IPRD_HOLD`) in every branch (declared pin, TTM, median,
   payable), so the measured impact is the override's alone.

9. **Growth path (engine 5.7).** Year t's growth = g0 − (g0 − g_term) /
   CAP × max(0, t − hold), never past g_term, with CAP = clamp(2 + 1.3 ×
   moat, 2, 15). hold is `scenarios.<k>.hold_years`: `inputs.hold_years`
   for a scenario that starts above terminal growth, else 2. Every older
   record holds 2.

## Overrides

Every override in `judgment.json` needs `{value, source, reason, kind}`:
- `filing`: the value comes from the company's own filing; the source must
  name the form, period and the statement line.
- `estimate`: only within 0.1×–10× of the last filed value for that field
  (anchor in the CSV / `dcf_numbers.json`).
- `base_override`: built only from figures printed in that PR's
  `dcf_numbers.json` / `ttm.json` / CSV, with the construction shown in
  `analysis.md`, and the arithmetic must reproduce.
  One exception (Andrew, 2026-10-19): a `base_override` with `basis`
  `payable_earnings_5y` at a P&C insurer or reinsurer is built from five
  filing figures (operating income available to common, FY by FY) that are
  not in the run outputs; see "Sector misfits" below for what to check.
  Engine 5.6: a `base_override` with `basis` `iprd_amortized` (beside
  `ACQUIRED_IPRD_RECURRENT` only) is built from the run's own `iprd_adjustment`
  figures — check 8 above.
- `ads_ratio`: only when stated in the filer's own 20-F/40-F, and the
  filing citation must be in `reason`.
- `currency: "USD"` (engine 5.5): allowed only on a kind `filing`
  override whose filing states the figure in dollars; the engine then
  uses it verbatim instead of FX-converting it. Without the key, an
  override is also used verbatim where the field's last filed unit is
  USD (the issuer's own USD translations); otherwise it is converted from
  the reporting currency. `override_checks.<field>.currency_basis` records
  which rule applied (`declared_usd`, `last_filed_unit_usd`, `converted`,
  `no_fx`, `shares`); `fx_conversion.overrides_usd_verbatim` lists the
  verbatim ones. make_score refuses every applied kind `filing` override
  used verbatim under `last_filed_unit_usd` unless it declares
  `currency: "USD"`: the engine records that basis only at an
  FX-converted filer, so the fallback alone never yields a score (HTHT's
  RMB capex figure would read as dollars; an engine 5.5 addition awaiting
  Andrew's ratification). A kind `estimate` override under that basis
  is refused too (it cannot declare a currency, and the 0.1×–10× band
  admits CNY at ≈ 7.2×: HTHT's RMB 828M would read as $828M), so a scored
  folder never carries one. A PUK or CX score must show the declaration.
- `share_class_mismatch` (engine 5.5): `{value: true, source, reason}`,
  filing-sourced from the EPS note; it forces `DATA_GAP:shares —
  SHARE_CLASS_MISMATCH` (no tier, no alert) and make_score refuses it.
  Only `true` or an object whose `value` is `true` declares (an object
  without `value` is malformed, even with a source); `false`,
  null and `{value: false}` declare nothing; any other value (the string
  "false", a number) is malformed — the engine records
  `{"malformed": …}` with no gap and make_score refuses it.
- `share_classes` (engine 5.7, R6). Every count must trace to its
  accession. The units are the economic units held outside the filer
  (the ownership table), not voting shares. `nci_check` must agree, or
  `nci_gap_reason` must give the figure. The registry `share_classes`
  event shows both bases (filed traded class vs total units: base, IRR,
  tier, cap, scope). An `UP_C_SUSPECT` waived by `up_c_suspect_reason`
  needs the number that shows the minority is ordinary, or that the count
  already covers every class; a waiver with no figure is P1. A tier at an
  Up-C filer with no declaration and no waiver is P1. A 0 entry in a year
  the class existed for part of is P1 (the engine refuses it; a
  hand-edited record would show it). A `share_basis: "total_units"` pin
  whose construction from total-unit engine outputs is not shown is P1.
  make_score refuses one equal to a filed-basis figure (R-4b), but it
  cannot see every other wrong basis.
- `tier_override`: a written reason is required, and the reason must be
  consistent with the numbers it cites. An override that lowers the tier
  while the narrative calls the numbers IRR an "artifact" or "upper bound"
  must give the figure it rests on; "materially lower" with no number is
  P2. An override may never raise a tier above the band of the
  numbers without a sourced base figure. On a sector misfit an override
  may only go below the notched tier: make_score refuses one above it,
  and on a 5.7 run one equal to it (Sector misfits names the one
  exception). Since 5.7 make_score also refuses a reason whose numbers do
  not trace, that carries no number, or that rests only on third-party
  facts. A 5.7 score showing one is a make_score defect (P1).

Each override must also appear in `_system/overrides_registry.json` with
its measured base/IRR impact. Since engine 5.5 an entry whose
declaration is unchanged keeps the date it was first recorded; a
re-score that re-dates one is a defect in make_score, not in the folder (the identity includes a
field override's `currency` and `scope` and a base_override's `kind`, `basis`, `figures`, `shares`).
`overrides_applied` in `dcf_numbers.json` must list the same keys as `judgment.json`, except an
override that only fills ttm.py legs of the TTM base the score is pinned to (ttm.json
`overrides_used`; APA's SBC estimate): score.json `overrides` lists it with `scope: "ttm_legs"`,
its registry entry and `override_impact` measure it on the TTM base, and when ttm.py cannot build
the TTM base without it (ttm.py exit 3) `unblocks_tier` is true and both alert gates close — a
TTM-pinned score that make_score wrote since this rule (2026-10-19) whose ttm.json used an override
score.json does not list is P1. AFG, CNH and WMG predate it (their tier and gates do not change) and
list the override on their next make_score run; they are README follow-ups, not findings. Overrides only fill periods
with no filed value: an override that claims to correct a filed figure
without a `base_override` has not changed the engine's result — check
`dcf_numbers.json` to see whether it actually applied. Engine 5.5 says
so itself for capex: `OVERRIDE_SUPERSEDED_BY_FILED_TAG:capex` (with
`override_checks.capex.superseded_periods`) fires when a declared
`capex_override` fills nothing in a last-3-FY year because a newly read
filed PP&E leg sits outside 0.5×–2× of it, and make_score refuses while
that `capex_override` is still declared (WY); ttm.py's twin is ttm.json
`capex_override_superseded_legs`, with a warning. Inside 0.5×–2× nothing
fires: the override stops filling and drops out of `overrides_applied`
(AMH and UDR on their next engine run), so the keys-match rule above
catches it — ask for the override's removal.

Since engine 5.7 make_score also writes these registry events (never
hand-edit one):
- `misfit_notch` {tier_by_numbers, tier_final (the notched tier),
  weighted_irr, reason, reason_source, basis} for every notch that
  applies. A D / F / payable block records none. The `tier_override`
  event is written only for an override in force. A legacy one-notch
  tier_override event becomes a misfit_notch event with the same date. An
  auto reason quotes the weighted IRR, so an engine re-run that moves the
  IRR within the tier re-dates that event (the text changed). That is
  intended.
- `declared_facts` (identity: facts_sha256), one per run with a
  facts.json. The `tier_override` and `base_override` events also carry
  `facts`: the facts their reason cites.
- `moat_divergence` (moat_score, evidence_score, core_evidence_score,
  supporting_adjustment, divergence, reason), `moat_low_roic` (moat_score,
  measure, median, median_note, reason) and `moat_high_return_low_moat`
  (the same, plus min). Each is written on a checked 5.7 run when its gate
  applies and its reason is declared.
- `moat_erosion_rebuttal` (moat_score, governing_change_pp,
  margin_change_pp, margin_basis, reason; when the rebuttal restored the
  hold, also hold_years 2, hold_without 0, irr_weighted,
  irr_weighted_without). It is written when G6 applies with a declared
  rebuttal, or when MOAT_EROSION fired and the rebuttal restored the
  2-year hold.
- `moat_widening_declined` (moat_score, governing_change_pp,
  margin_change_pp, margin_basis, hold_years 2, hold_without 3,
  irr_weighted, irr_weighted_without, reason): a declined widening whose
  guards pass. Every moat event's identity is (moat_score, reason). None
  is written on a rebuild whose gate or fade drifted, nor for an
  erosion_rebuttal no run has checked (declared while no erosion was
  measured, then met by a rebuild).
- `interim_bridge` (identity: the declaration hash; it keeps the
  declaration's descriptors, and both bases are the base_alternatives
  event's) and `interim_bridge_declined` (identity: the reason).
- `base_alternatives`, one for a rejected STALE_FY TTM or a published
  6-K bridge: the chosen base, the reason, the TTM's kind and window, and
  every base with weighted IRR and tier. Its identity is chosen, reason,
  TTM kind and window, so an unchanged reason against the same 10-Q keeps
  its first date.
- `share_classes` (the declaration with `units_by_period` and both
  bases; identity: basis and declaration hash) and `up_c_suspect` (the
  waiver's reason). A `base_override` event carries `share_basis` /
  `share_period` when the pin declares them.
- `capex_unlisted_ack` {tag, reason, value}, one per
  `CAPEX_UNLISTED_COMPONENT` tag the ack releases; identity (tag, reason).
  A capex field entry carries `software_included` when the override
  declares it.

## Flags and confidence

Every entry in `fragility_flags` must be addressed by name in `analysis.md`
with a resolution, not a restatement. The flags: `STALE_FY`,
`BASE_DIVERGENCE`, `NI_OCF_DIVERGENCE`, `WIDE_SCENARIO_SPREAD`,
`OE_VOLATILE`, `BASIS_BREAK_SUSPECT`, `BUYBACK_TAILWIND`, `IRR_AT_FLOOR`,
`TIER_BAND`,
`HIGH_NET_DEBT`, `BIG_NET_CASH`, `FX_CONVERTED`, `USD_TRANSLATIONS_USED`,
`ADS_RATIO_APPLIED`, `CASH_INCLUDES_RESTRICTED`, `DEBT_TAGS_BLANK`,
`DATA_GAP:<field>`, and engine 5.5's `SHARE_SCALE_SUSPECT`,
`SHARE_BASIS_ADJUSTED`, `SHARE_BASIS_DIVERGENCE`, `CAPEX_COVERAGE_LOW`,
`SBC_TAG_RECONCILED`, `OVERRIDE_SUPERSEDED_BY_FILED_TAG:capex`, and engine 5.6's
`ACQUIRED_IPRD_CHARGE`, `ACQUIRED_IPRD_RECURRENT`, `ACQUIRED_IPRD_UNCONFIRMED`,
`ACQUIRED_IPRD_UNCONVERTED`, `ACQUIRED_IPRD_UNMATCHED_PAYMENT` and `ACQUIRED_IPRD_PARTIAL_PERIOD` (check 8),
and engine 5.7's `ANNUAL_FROM_INSTANCE`, `MOAT_TREND_HOLD`,
`CAPEX_UNLISTED_COMPONENT:<tag>`, `CAPEX_UNLISTED_COMPONENT_OVERRIDDEN:<tag>`,
`UP_C_SUSPECT`, `SHARE_CLASSES_DECLARED`, `SHARE_CLASSES_CAP_GAP` and
`SHARE_CLASSES_NCI_GAP`, plus make_score's `TTM_DECLARED_INTERIM` (in
score.json only, never in dcf_numbers.json).

- `STALE_FY` on a 5.7 run whose published base is not the TTM (the
  insurer payable pin excepted):
  `base_alternatives` must show the rejected TTM (base, weighted IRR,
  tier), and `ttm_rejection_reason` must name the distorting cash-flow
  line with a number. make_score refuses otherwise, so never grade that
  part. Check the substance. The named line must be the one that moved in
  ttm.json's legs, and the rejection's direction must fit it. A reason
  naming a trough while the TTM sits above the median, or a line whose
  TTM leg did not move, is P1. A qualifying but thin argument (a
  one-quarter swing called a trough with no prior-year comparison) is
  P2. A `computed: false` TTM entry names why it was not priced: no
  ttm.json, another FY, another share-class basis, an orphan bridge, a
  replay data gap, or a stale ttm.json ttm.py cannot rebuild. Check the
  note, not a tier. A STALE_FY 10-K run with no ttm.json (or a stale one
  ttm.py cannot rebuild) carries `ttm_unavailable_reason`: ttm.py's own
  exit-3 line, verbatim (make_score checks the quote). Check that it
  names the missing leg plausibly (a 10-Q filed after the FY end whose
  YTD facts EDGAR lacks).
- `STALE_FY` at a 20-F / 40-F filer on a 5.7 run: the base is a declared
  interim bridge (ttm.json `basis: declared_interim`, pinned with
  `--ttm`), or judgment.json `interim_bridge_declined` names the 6-K
  checked and why it cannot bridge, with a number. make_score refuses a
  run with neither, a hand-built 6-K `base_override` pin included. Check
  the like-for-like declaration against the 6-K: is the comparative
  restated, and does the window hold an acquisition, a disposal or a
  demerger? Check that estimate legs carry a method. Check that
  analysis.md discusses both the bridged and the annual-median tier
  (score.json `base_alternatives`). A bridge resting on
  `same_business_perimeter` (accepted for a demerger only) is a judgment
  call to challenge, not a pass. A bridge from a 6-K without XBRL
  (ttm.json `report.is_xbrl` false) is verified by its snippets only:
  check each leg against the report. On output from before 5.7, a
  `STALE_FY` resolved with "no TTM available" at a 20-F filer still gets
  the old question: does the interim 6-K print TTM operating cash flow and
  capex? The worker should have used it or escalated.
- `ANNUAL_FROM_INSTANCE`: the latest FY came from the filing's own XBRL
  instance. Check `annual_instance.json` against the 20-F.
- `MOAT_TREND_HOLD`: the run held growth 0 or 3 years instead of 2. For
  eroding, analysis.md names the measured decline from key_numbers.md's
  Trend test, or says why the rebuttal does not apply. For widening, it
  says why this is not a cyclical upswing or a recovery from a trough.
- `CAPEX_UNLISTED_COMPONENT:<tag>`: an unread capex-like tag exceeds the
  whole component capex leg. make_score refuses the run without
  `capex_unlisted_ack`. The remedy for a real capex line is
  NEEDS_MAIN_AGENT: capex, never an override.
  `CAPEX_UNLISTED_COMPONENT_OVERRIDDEN:<tag>` is the same kind of tag in a
  year with no PP&E leg. It is not refused; route the list fix (check 4).
- The share-class flags (`UP_C_SUSPECT`, `SHARE_CLASSES_DECLARED`,
  `SHARE_CLASSES_CAP_GAP`, `SHARE_CLASSES_NCI_GAP`): see `share_classes`
  under Overrides.
- `TIER_BAND` (bear and bull tiers differ): the analysis must size to the
  bear end or say why not.
- `WIDE_SCENARIO_SPREAD` or any unresolved flag: confidence must not be
  "high". Confidence "low" on an S/A name: say so explicitly, because
  alerts no longer check confidence.
- `DATA_GAP`: if SBC, capex, diluted shares or OCF is missing for ANY of
  the last 3 fiscal years and no override fills it, the company must be
  blocked with no tier. A `score.json` tier beside a non-empty `data_gap`
  is P1 (since 5.5 a filed share count ≤ 0 counts as missing). Engine
  5.5 adds two share gaps no override covers:
  `DATA_GAP:shares — SHARE_SCALE` (gap key `share_scale`) and
  `DATA_GAP:shares — SHARE_CLASS_MISMATCH` (gap key `share_class`).

## Quotes and declared facts (engine 5.7)

Andrew's ruling R3 (2026-10-19): every number in a 5.7 run's `analysis.md`
traces to a generated file.

1. `check_quotes.py <T>` passes. `queue.py done` and `pass2-done` enforce
   it. A 5.7 folder in a PR whose analysis fails it is P2.
2. make_score verifies folder facts. Do not re-derive them.
3. Filing and release facts: check that the snippet plausibly comes from
   the cited accession. Say "cannot verify from the diff" when it cannot
   be seen.
4. Third-party facts may calibrate scenarios and give context only. A
   tier, base or notch resting on one cannot score (make_score refuses).
   A hand base pin cannot rest on its own figure alone.
5. `not_quantities` entries must be names or identifiers. One that hides
   a quantity is P2.
6. A quoted method range must come from a saved run listed under "Method
   runs". A retyped preliminary figure is P2.
7. `declared_facts.drift` on a rebuild is informational: a folder file
   changed after the score. Re-score at the next filing.
8. Interim-bridge leg values are quoted from the Interim bridge section,
   not re-declared as facts. IPR&D declaration values are quoted from the
   Acquired IPR&D section.
9. The checker traces numbers; it is not proof. A low-precision research
   number ("8%") can coincide with an engine figure, so keep the "cannot
   verify" review.

## Scenarios, growth and moat

- Growth starts should be plausible against the last two revenue and OE
  prints in the CSV. A base-case start above the company's own latest
  guidance, when `analysis.md` quotes that guidance (on a 5.7 run, a
  declared fact of `type: guidance`), is P2. key_numbers.md marks a
  guidance or estimate fact STALE when it predates the latest filing the
  engine used or its period has already reported. Resting the guidance
  check on a STALE fact is P3. When the analysis never mentions guidance
  for a company that gives it, ask for the guidance-vs-model check
  `WORKER_SPEC` step 4 requires (FISV, PFG).
- Probabilities sum to 1. Default probabilities with a narrative that
  describes a specific committed capex program or a known cliff is P3.
- **Moat (Andrew, 2026-10-19: Dorsey's sources plus the evidence
  scorecard, with the M1b and M1c amendments).** One lever per question.
  The moat sets the fade only — its level sets CAP = clamp(2 + 1.3 ×
  moat, 2, 15), its direction the growth hold (next bullet). Risk lives in
  the probabilities, growth in the growth start, and return on capital in
  the capex inside OE. A moat argued from growth, or a risk carried in the
  moat instead of the probabilities, is a finding (P2 when it moves the
  tier, else P3).

  **Sources.** Since engine 5.7 judgment.json `moat_scorecard` names the
  sources: intangible assets, switching costs, network effects, cost
  advantage, size advantage (Dorsey), efficient scale (Morningstar),
  counter-positioning (Helmer) and customer captivity (Greenwald), each
  narrow or wide. It also scores the evidence. make_score checks it
  (score.json `moat_evidence`, key_numbers.md "Moat scorecard"). The caps:
  no source caps the moat at 3; one narrow source caps it at 6; 7+ needs
  a wide source or two fact-backed sources; 9+ needs two wide sources and
  returns_on_capital +2 sustained. A source resting on metrics alone is
  narrow. Returns on capital never supports a source without a fact. A
  brand counts only with pricing power or retention at +1. A patent
  carries its expiry and is narrow under 5 years. Counter-positioning is
  narrow and names the incumbents. Efficient scale names its competitors
  (5 or fewer) and shows returns above the cost of capital (10%; 6% on the
  real-asset ladder; ROE 12%) with no price war.

  **Mechanical pillars.** returns_on_capital, industry_structure
  (same-ladder SIC peers), capital_intensity and scale_economics are
  measured by make_score: never re-grade them. returns_on_capital reads
  the governing return. That is tangible ROIC when goodwill + intangibles
  exceed 30% of invested capital (+2 then also needs the plain ROIC median
  at 10%), ROE at a balance-sheet financial (a mortgage REIT included),
  and ROIC otherwise. ROA is printed as a cross-check. The acquired-IPR&D
  charge engine 5.6 deducts once from value is added back in
  returns_on_capital and scale_economics, in the rows' own currency
  (`IPRD_CHARGE_IN_WINDOW`), so the moat does not take it twice.

  **Supporting factors.** Great products, market share, execution and
  management are supporting factors. Their sum / 4, capped at ±1, moves
  the evidence score (a lone factor by at most 0.25). They never lift the
  moat past a source cap. These bad moats are allowed as supporting
  factors. Presenting them as the moat's source, with no source type
  named, is P2. `moat_evidence.moat_lint` lists candidates from moat_for,
  moat_justification and the source rationales; an item marked
  `(supporting: <factor>)` is support.

  **Reasons make_score requires**, each carrying a traced number:
  `moat_divergence_reason` for a moat more than 2 from the evidence score
  (gate G1); `low_roic_reason` for 7+ on a governing return below 10% (ROE
  below 15%) or unmeasured (G4); `high_return_low_moat_reason` for 4 or
  below on a governing return of 20%+ sustained (G5); and
  `erosion_rebuttal` for an erosion score of +1 under MOAT_EROSION (G6).
  Review: check that each cited
  fact says what the rationale claims (P3; P2 when it contradicts the
  score).

  **Facts.** Facts cited by a pillar or factor list `moat:<pillar>` in
  used_for (sources: `moat:sources`). `event` facts may stand alone only
  on switching_costs, erosion_risks, execution and management.

  **Older output.** On pre-5.7 output `status` is `report_only` and
  nothing in it is a finding. The old rule still applies there: FOR and
  AGAINST pillars, the ROIC history, and a reason for 7+ on ROIC below
  10%.
- **The moat's direction sets the growth hold (Andrew, 2026-10-20, M6:
  "eroding moat should fade faster and vice versa").** Since engine 5.7
  the level still sets CAP, and the direction sets how long growth holds
  before the fade. `dcf_numbers.json` records `moat_trend` / `hold_years`
  (top level and in `inputs`, with `hold_rule`) and, per scenario,
  `scenarios.*.hold_years`. Eroding holds 0 years, stable 2, widening 3.
  The hold applies only to a scenario that starts above the terminal
  rate; one at or below it holds 2.

  The trend is make_score's, never the worker's. The trend test (score.json
  `moat_evidence.fade`; key_numbers.md "Trend test" and "Fade direction")
  reads the governing return AND the margin over the last 5 FY. The margin
  is gross margin, or the filed operating margin where gross margin is not
  filed. The test reads fundamentals.json rows only; a CSV-only folder is
  not measured. Both falling is MOAT_EROSION: the governing return by 3pp
  and 20% of its start, the margin by 2pp. Both rising by the same is
  MOAT_WIDENING.

  Eroding means hold 0. `moat_scorecard.erosion_rebuttal` restores the
  2-year hold only when it explains the decline with a traced number
  ANCHORED outside the trend test: a cited filing / release / folder fact
  tagged erosion_rebuttal (a price, volume or cycle figure), or the filed
  history. make_score refuses a
  rebuttal that only restates the decline, the record's IRR or the
  counterfactual.

  Widening means hold 3 only when every guard passes: a fact-backed
  source; returns_on_capital +1 or better; plain ROIC rising too when
  tangible ROIC governs (acquisition goodwill shrinks the tangible base);
  ROA rising too when ROE governs (buybacks shrink equity); no commodity
  SIC; and no `moat_scorecard.widening_declined`. The commodity SICs are
  mining, oil and gas, primary metals, commodity chemicals, pulp and
  paper, lumber, refining and bulk shipping, plus a SIC-6199 filer booking
  ASC 606 contract revenue (a crypto miner). An unknown SIC fails. A
  commodity SIC passes only when `business_type_reason` quotes a cited
  cost-position fact (cost-curve position, cash cost per unit vs peers). A
  commodity price move never counts.

  make_score refuses an authoring 5.7 run whose recorded trend or hold
  disagrees with the trend test, so never re-derive it. Review the
  judgment around it:
  - A rebuttal whose numbers do not show a cycle is P2 when it moves the
    tier, else P3. Check what each number IS: the matcher compares values.
  - A rebuttal and an erosion_risks threat that describe the same decline
    is P2.
  - A confirmed widening with `WIDENING_FROM_TROUGH` (or a cyclical name:
    airlines, cruise lines, miners) and no explanation in analysis.md is
    P2.
  - A moat score or growth start cut "because the moat is eroding", on top
    of hold 0, is double counting (P2 if it moves the tier, else P3). So
    is an erosion_risks threat scored −1 or −2 whose only evidence is the
    MOAT_EROSION measurement itself. G6 only forbids +1 against a measured
    decline; it never asks for a negative score (a consistency cap, not a
    valuation lever).

  Two tickers with the same CIK carry the same `moat_trend`. On pre-5.7
  output `fade.rule` is `report_only` and nothing in it is a finding.
- Consolidated OE at a company with a listed majority-owned subsidiary
  (Sands China at LVS, JD Logistics/Health at JD): the analysis must say
  what share belongs to minority holders. Silence is P3; it is a method
  limit, not a worker error.
- Two tickers with the same CIK (dual share classes) must carry the same
  moat, probabilities and offsets; different workers choosing differently
  gives two intrinsic values for one company.

## Sector misfits (insurers, banks, REITs, utilities)

Operating cash flow at an insurer includes policyholder money; at a bank
it includes deposit and loan flows. make_score marks these `model_fit:
misfit` (engine 5.7, Andrew 2026-10-19). A name is a misfit when its
universe sector is Finance, Real Estate or Utilities, OR its EDGAR SIC
code is in `dcf_engine.MISFIT_SIC_RANGES`: utilities (4900-4949,
4960-4999), banks (6020-6099), credit lenders (6111-6199) and BDCs
(6726), broker-dealers (6211), insurance carriers (6311-6399, managed
care 6324 included: OSCR, MOH, CNC), real-estate lessors (6510-6519) and
REITs (6798). dcf_numbers.json `sector_model` says which rule fired.

A present SIC outside 6000-6799 and outside every misfit range sets a
misfit universe sector aside (default Q1 (b), main agent 2026-10-21,
pending Andrew; the switch is `dcf_engine.SIC_SETS_ASIDE_SECTOR`). On file
that is EDU (8200, under Real Estate), WCN and GFL (4953) and FN (3661)
under Utilities, and CSGP (7389) and EFX / TRU (7320) under Finance. Such
a name is modeled, and score.json `misfit_sector_set_aside` says why; it
is not a finding. The SIC comes from EDGAR on an engine run, and from the
folder's fundamentals.json / profile.json on a rebuild. So a name with no
folder SIC (GFL) is set aside only on its first 5.7 engine run, and a
rebuild that still scores it a misfit is not a finding either. Finance fee
businesses (exchanges 6200, asset managers 6282, insurance brokers 6411,
agents 6531) stay misfits through the sector rule.

For misfits:
- **The notch is mechanical** (Andrew, 2026-10-19; the 2026-10-15
  standing policy made automatic). make_score publishes every sector
  misfit one tier below its numbers tier (S→A, A→B, B→C, C→D). It records
  the notch in score.json `misfit_notch` {applies, tier_by_numbers,
  tier_after_notch, reason, reason_source, not_applied, basis}. Never
  grade the notch.
  - Not notched: a payable-earnings pin (`not_applied: payable_base`), a
    numbers tier of D (`tier_floor_D`, the lowest graded tier) and a
    numbers tier of F (`tier_F`, no positive owner's earnings). The block
    carries the reason. A judgment override D → F is still allowed and
    published. A hand pin (SF's net-income base via `--base-oe-ps`) IS
    notched.
  - On a 5.7 run the worker writes `misfit_notch_reason` (a number; see
    the next bullet) and leaves `tier_override` null. Output from before
    5.7 carries an auto reason with the weighted IRR (`reason_source:
    auto`) or its legacy one-notch `tier_override` reason
    (`reason_source: tier_override`).
  - make_score refuses a `tier_override` above the notched tier. On a 5.7
    run it refuses one equal to it too: the notch is make_score's. The one
    exception is the acquired-IPR&D share-count case (check 8): the main
    agent's quantified hand-deduction override may sit at the notched
    tier. An override below the notch is a further judgment downgrade and
    needs its own quantified reason.
  - A 5.7 misfit without `misfit_notch_reason`, or with one carrying no
    number, cannot be scored (make_score refuses). So it is not a review
    finding.
- `misfit_notch_reason`, and the reason of any override below the notch,
  must carry a number: the payable-earnings measure the analysis relied
  on (operating EPS, dividends from subsidiaries, capital returned) or the
  IRR it implies. Since 5.7 make_score also checks that the reason
  traces: to an engine figure or a cited fact, never to third-party facts
  alone. "Screens materially lower" with no figure is P2. Do not grade the
  notch itself as wrong (PFG's B stands
  under the policy even though a payable-earnings base gives C; that gap
  is a known limit of the method, listed in the analysis, not a defect).
- A misfit ranked in the top 10 by numbers IRR deserves one P3 comment
  saying the IRR shown is not the one the analysis defends.
- P&C insurers and reinsurers (Andrew, 2026-10-19): when the filer prints
  "operating income (loss) available to common shareholders", the folder
  carries a `base_override` with `basis: payable_earnings_5y`, `kind:
  filing`, the five annual `figures` (USD dollars, oldest first), `shares`
  (the CSV's latest `shares_diluted`) and `value` = average ÷ shares per
  ordinary share, and the final run passed `--base-judgment`:
  `dcf_numbers.json` then carries `payable_base` (figures, average, shares,
  ads_ratio, pinned_per_share) with `base_source`
  `judgment_base_override`, and `key_numbers.md` prints the five exact
  figures. Check: the five figures match between `judgment.json`,
  `payable_base` and `key_numbers.md`; average ÷ shares × ads_ratio equals
  `base_oe_per_share` to the cent (P1 otherwise); `shares` equals the
  CSV's latest diluted count exactly (P1); `payable_base.sic` is 6331 or
  6351 (the engine refuses others, so a scored folder outside that is P1);
  the registry `base_override` event carries the native → pinned impact
  (base, IRR, tiers both ways; absent is P2); the filing cited for each
  figure is a release or 10-K for that fiscal year ("cannot verify from
  the diff" if the PR does not show it). A `payable_base` block together with a
  `tier_override` below the numbers tier is double-counting (P2;
  make_score refuses it). A payable_base run is never notched
  (`misfit_notch.not_applied: payable_base`). A P&C name scored on the OCF
  base with only the notch is P2 — ask for the payable-earnings base. Life
  insurers, banks, REITs and every other misfit get the mechanical 5.7
  notch.

## Ranking and history files

- `_daily/history/ranking-<date>.csv` is append-only: a PR may add
  today's file, never rewrite an earlier date's. The same holds for any
  dated file under `_daily/`. Rewriting a past date is P2 (the 2026-10-14
  ranking was overwritten once).
- Rows are ordered by live IRR, then scored IRR, by design; a name whose
  `tier_final` was notched (sector misfit) or overridden below its numbers
  tier still sorts on the numbers IRR, so a Tier D can rank #1 with its
  notch or override displayed. That is not a finding. Only per-company
  PRs are reviewed row by row; the CSV
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
- The mechanical misfit notch (`misfit_notch`, one tier below the numbers
  tier; D / F / payable not notched), a misfit set aside by its SIC
  (`misfit_sector_set_aside`), and a `tier_override` with a quantified
  written reason (on a misfit, below the notch; see Sector misfits).
- `financials_history.csv` `delta_nwc` / `oe_maintenance` moving on an
  engine 5.7 re-run of a filer of component-only current debt (the NWC
  fix, HII #29 / AVTR). The change is CSV-only: no base or tier moves. A
  declaration quoting `oe_maintenance` (TTMI's base_override) must be
  re-derived on that run (EB-017). That one IS a finding if the PR keeps
  the stale figure.
- Pre-5.7 analyses that `check_quotes.py --all` reports as untraced. They
  are legacy and not gated: not a finding until the folder's next 5.7 run.
- `declared_facts.stale` and the STALE lines in key_numbers.md: a warning
  by design.
- A rebuilt key_numbers.md whose only changes are the 5.7 lines: the
  notch lines of a misfit's tier block, the new engine lines (Filed
  history, return series, Method runs), the report-only Moat scorecard
  section, and “…” around echoed worker text.
- `moat_evidence` outside tolerance, or a gate firing, on pre-5.7 output
  (`status: report_only`). Mechanical evidence alone puts 44.4% of the
  2026-10-21 folders (232 of 522) outside ±2 of the recorded moat.
- `moat_evidence.gate_drift` on a rebuild (the same engine run, judgment
  and facts.json; only the data moved). It is resolved at the next
  re-score, not in a rebuild PR.
- A positive supporting factor at a company with no source (M1b). A moat
  above a source cap is a refusal, never a finding.
- The hold is 0 / 2 / 3, not symmetric (Andrew, 2026-10-20). An eroding
  moat costs both hold years and a widening one earns one, because engine
  defects so far overstated value and an upswing looks like widening.
  Scenarios starting at or below the terminal rate keep 2 (lane default
  Q6).
- `moat_evidence.fade.in_sync: false` with a `fade_sync` gate_drift entry
  on a rebuild (only the data moved since the engine run). It is resolved
  at the next engine run, not in a rebuild PR (lane default Q5). The same
  holds when the entry says an erosion_rebuttal "has never been checked"
  (declared while no erosion was measured): the next authoring run checks
  it, and until then the record keeps the engine's hold and writes no
  rebuttal event.
- A pre-5.7 record's `moat_evidence.fade` (rule `report_only`, its
  counterfactual flagged `report_only`), and a Tier F record's
  `no_projection` fade.
- The `UP_C_SUSPECT` threshold of 20% (08b decision 1, main agent
  2026-10-20, pending Andrew). The shipped rule reproduces the
  calibration: 10 of the 86 calibration folders fire. OWL, SYM, IBKR,
  CHTR, VNOM, ASTS and RKT price only the traded class. ARES and FPS
  already price every class, and VG is not an Up-C, so those three need a
  one-line waiver. TPG, TKO and QSR stay silent because their diluted
  counts include the exchange. Up-Cs whose NCI share is below the
  threshold (TW, AMH) are not flagged; reviewers may still ask for a
  declaration. IBKR leaving the < $40B scope on total units is intended
  (08b decision 6). Period-end unit counts beside weighted-average traded
  counts are accepted (08b decision 2). An exit alert on a corrected tier
  is not suppressed (08b decision 3).
- Engine 5.7 (Andrew, 2026-10-19, R9): capitalized software counts as
  capex. A lower base than the 5.6 record at JKHY / FIS / FLUT-type filers
  is the policy, not an error. Capex stays GROSS of PP&E sale proceeds:
  KNX resells 23–37% of its fleet capex, and R8 measured it (base $0.38
  gross vs $2.19 net, Tier D either way); the policy did not change.
- `base_alternatives` absent from output older than engine 5.7; an
  annual-median or TTM entry "not replayed" when STALE_FY does not fire;
  a TTM-published run's annual-median entry; and a STALE_FY median at a
  10-K filer with no ttm.json whose `ttm_unavailable_reason` quotes
  ttm.py. These are informational, never a finding by themselves.
- Engine 5.6. Andrew's decision (2026-10-19): an impairment of a previously capitalized
  intangible (`ImpairmentOfIntangibleAssetsExcludingGoodwill`) is never deducted —
  that spend went through capex / intangible purchases when it was made; the cash
  outflow is preferred over the expense even when it is lower (BIIB FY2025: $85.0M
  expensed, $50.0M paid → $50.0M; the rest is paid later — counted as a
  `deferred_payment` when that falls in the window — or in shares, which the diluted
  count already holds). Main-agent / review additions awaiting his ratification: a
  cash-tag-only `PaymentsToAcquireInProcessResearchAndDevelopment` year (MAA's
  development-spend mistag) is never a charge unless it settles the window's unpaid
  remainder of an expensed charge; a below-5% acquired-IPR&D
  charge is deducted with no flag (the deduction has no cliff; the threshold only
  decides the flag); an expense-basis charge (no us-gaap cash tag — HALO, NBIX) is
  deducted only on the worker's `iprd_cash_flow_check` and then at the expense figure
  (HALO $284.9M, not its $287.8M investing line net of cash acquired); and the
  `iprd_amortized` mean reads the FY figures only, so a current-YTD charge is in
  neither the mean nor a deduction until it lands in an FY.
- Engine 5.6, Andrew's 2026-10-20 ruling, delegated to the main agent, who decided: a contingent milestone or other
  deferred payment on an acquired-IPR&D deal already charged in an earlier period
  (inside the window or before it) is the same purchase — it is still deducted
  once when expensed or paid, but its period does not count toward
  `ACQUIRED_IPRD_RECURRENT` (that flag catches buying R&D as a habit, distinct
  deals, not one deal paid in installments). Only a cited per-period
  `iprd_deferred_payment` declaring the period's WHOLE charge removes it from the
  count; a partly deferred period still counts. [Codex review round 27 of PR #47]
  A year counts by its own expense, paid that year or accrued and paid later, never
  by its cash timing: two deals expensed with $0 cash and paid the next year are two
  charge years; cash that settles an earlier year's charge (no expense of its own)
  is not a new one, and an accrued year's whole charge is its expense. [Codex review round 28 of PR #47]
  REVERSES round 27's carve-out: a year counts by its own expense whatever its cash
  presentation too — paid in shares, inside operating cash flow, inside intangible
  capex, awaiting its cash-flow check or with no FX rate is still a charge year (round
  27 had left those presentations out, so a cash deal beside a separate share-paid
  deal read one year); the habit is the acquisitions, however paid. Those
  presentations still deduct nothing (OE or the share count carries them) and the
  `iprd_amortized` figures stay the deducted FY figures. The recurrence gate's
  "material" is its own figure: the counted periods' acquired-IPR&D expense (the
  current-YTD leg's too on a TTM base, less a declared installment part) on the same
  denominator, base and 5% threshold — never the cash the window deducted ($1 paid on
  each of two $100M deals read $2, not material) — recorded as
  `recurrence_expense_total` / `recurrence_materiality` only when 2 or more FY charge
  years are counted; a counted period whose acquired-IPR&D expense has no USD figure reads as material.
  `ACQUIRED_IPRD_CHARGE` keeps the deduction's materiality, and a cash settlement
  (a pre-window deal's declared installment) never makes tiny in-window charges
  material. Round 28 re-verification: a charge year's whole charge, for Andrew's
  2026-10-20 declared-installment rule, is the larger of its cash and its own
  expense ($1 paid on a $100M deal is a part, so declaring the $1 no longer takes
  the year out of the count), and a declared part comes first from the cash beyond
  the period's expense, so a new deal expensed beside an earlier deal's settlement
  still counts in full. [Codex review round 29 of PR #47] A declaration is whole only
  when that whole charge is known in USD: a year whose own expense (or cash) has no
  FX rate, even fetched, cannot be declared at all — its cash had stood in for the
  whole charge ($40M paid on a EUR 100M expense read "whole" at $40M) — refused like a
  year with no usable cash, so it stays in the recurrence count; so is a year whose
  expense or cash tag is also filed in a unit with no FX rate beside the USD fact
  used (`unit_conflict`, round-29 review notes). One rule (round-29 polish reviews,
  `iprd_own_charge_usd`): a year's own expense is the largest positive figure on any
  of its acquired-IPR&D expense tags (the parallel one too) in every unit filed, and
  its whole charge the largest of that, every positive cash-tag figure in every unit
  and the cash deducted — EUR 100M at 1.08 on either tag, or the parallel tag at
  $108M, beside the USD 40M expensed and paid makes $40M a part and $108M the whole.
  [Codex review round 30 of PR #47] "Every unit filed" is every unit that disagrees
  with the figure used beyond the engine's unit-agreement tolerance
  (`IPRD_UNIT_TOLERANCE`, 0.01: more than max($1, 1% of the larger) after conversion,
  the units `unit_conflict` records); a unit within it is the figure used — the same
  charge translated at another rate — so USD 100M beside EUR converting to $100.7M is
  a $100M charge (a $100M declaration is whole) and EUR converting to $102M makes
  $102M the whole. With three or more units filed, the tolerance applies to their spread: once the largest and smallest converted figures differ by more than it, every unit is recorded and the largest counts.
  The whole test and its cap read the whole charge; the recurrence figure reads the
  expense side (the own expense, less only a declared part beyond the whole charge
  less that expense) and the whole charge adds the cash side, so the recurrence
  figure is unknown (read as material) only when the own expense has no USD figure —
  a USD expense beside cash with no FX rate reads that expense. The deduction is
  unchanged. And a deal's first
  charge inside the window is a period with its own acquired-IPR&D expense (USD or
  native, however paid), never the cash that settles an earlier charge. An `iprd_amortized` base carries only the deducted FY
  figures: with nothing deducted in the last 3 FY there is nothing to amortize
  (`BAD_BASE_OVERRIDE`), and the RECURRENT flag then asks only for the recurrence
  assessment. [Codex review round 8 of PR #47]
  Each deal's cumulative declared amount IS a registry event (`iprd_deferred_payment`,
  below). Choices made in the
  Codex review round (same ruling, the main agent deciding): FY periods only (the
  recurrence count reads FY periods, so a current-YTD entry is refused rather than
  mislabelling a period that never counted); several deals may share one period
  (their amounts sum to the charge); a first charge before companyfacts begins
  rests on the citation alone, recorded `citation_only_before_companyfacts`; the
  accession's CIK is NOT matched to the filer (filer agents file under their own
  CIK), so that stays a review check (check 8). The per-deal cap (the main agent's
  decision on the review's open item, delegated by Andrew 2026-10-20):
  `deferred_payment_of` carries a required `contingent_total` {value (USD), source:
  accession + section disclosing the deal's unrecognized milestones / deferred
  consideration}, declared once and identically for a deal; the engine refuses
  (`BAD_IPRD_DEFERRED_PAYMENT`) a deal whose declared amounts, summed across every
  entry (a rolled-out one included), exceed it — so the cap is mechanical and the
  review checks the cap's value against the filing. [Codex review round 4 of PR #47]
  A rolled-out entry STAYS in judgment.json (`deferred_payments_rolled_out`: never
  applied, still counted toward the cap); a PR deleting one is P1 — it frees the
  deal's cap for a later declaration — and make_score refuses the run that counted
  it once it is gone. [Codex review round 8 of PR #47] Deleting or shrinking one is
  now refused MECHANICALLY, also after the engine is rerun (which used to leave
  nothing to compare against): make_score records each deal's cumulative declared
  deferred amount as a registry event (`iprd_deferred_payment`: deal,
  contingent_total, paid_to_date, first_charged_period, periods) carried across
  runs the way first-recorded dates are, refuses declarations for a recorded deal
  summing to less than its paid_to_date, and caps max(the declarations on recorded
  periods, paid_to_date) + newly declared periods at the contingent_total. Every
  `period` and `first_charged_period` must be a real date (an impossible one is
  malformed, never counted toward the cap). [Codex review round 5] A run whose window holds no charge at
  all still lists it (a minimal `deferred_payments_only` block, nothing deducted).
  [Codex review round 7] A rolled-out entry is kept and counted toward the cap only
  after the checks that need no window record (first charge before its period, the
  original filing's accession year, companyfacts' expense fact for a pre-window first
  charge); an invalid one is refused (`BAD_IPRD_DEFERRED_PAYMENT`), not kept.
  [Codex review round 9] A rolled-out period must be one of the filer's fiscal-year ends
  (companyfacts' annual period ends where they reach the date, else within 7 days of
  the nearest FY end's month-day; the run records `fy_period_ends` and make_score
  re-checks); a recorded deal's `contingent_total` and `first_charged_period` are
  immutable; a new deal name with a recorded or co-declared deal's first charge and
  cap filing is refused as a renamed copy. [Codex review round 10] So is every
  recorded period's amount: one omitted, or declared more than $1 apart from the
  recorded amount, is refused (naming the period) and the event keeps the record.

## Comment style

One comment per concrete finding: severity, file:line, the two values that
disagree, and why it matters. Lead with P1s. Consistency and rule
violations are findings; disagreement with a documented, quantified
judgment call is not. When you suspect a filing-level problem you cannot
check from the diff (an extension-tagged capex line, a discontinued
operation inside OCF), say what the worker should look at and mark it
"cannot verify from the diff" rather than asserting it.
