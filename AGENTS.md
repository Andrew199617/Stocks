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
from the first per-company PR after it. A second exception: an
owner-directed acceptance re-score named in the PR body (the PR #31
engine-5.5 bundle and PR #47's engine-5.6 HALO re-score) may ride with its
engine change — the PR body must say the owner directed it; do not ask for
it to be split out. Policy-bearing files are `make_score.py` (tiers,
alert gates), `dcf_engine.py` (the formula), `queue.py` (claims and pass 2),
`WORKER_SPEC.md` and `SECOND_PASS.md` (what workers must do). A change to
any of them needs (a) a test in `_system/tests/` that fails on the old code,
(b) the matching sentence in the specs and `README.md` updated, and (c) a
commit message that says what decision it implements and who made it. Grep
the specs for the old rule and list every stale passage with file:line.

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
- `judgment.json` — the worker's decisions: `moat_score`, `moat_for` /
  `moat_against`, `probs_used`, `confidence`, `tier_override` +
  `tier_override_reason`, per-field overrides as top-level keys
  (`capex_override`, `sbc_override`, `shares_override`, `base_override`,
  `ads_ratio`; each `{value, source, reason, kind}`, and since engine 5.5
  an optional `currency: "USD"` on a kind `filing` override),
  `share_class_mismatch` (5.5: `true` or `{value: true, source, reason}`;
  any other shape is malformed and make_score refuses it),
  `second_pass` when pass 2 ran.
- `score.json` — generated ONLY by `make_score.py`: `tier_final`,
  `tier_by_numbers`, `implied_irr`, `iv_at_15`, `irr_bear` / `irr_bull`,
  `tier_bear` / `tier_bull`, `alert_eligible`, `exit_alert_eligible`,
  `engine_release`, `in_scope_under_40b`, `model_fit`; since 5.5
  `market_cap_b` carries `market_cap_basis`,
  `in_scope_corrected_by_make_score` marks a scope make_score corrected,
  and `net_debt_to_normalized_oe_ads_basis` is a pre-5.5 ADS record's
  net-debt ratio on the ADS basis; since 5.6 `iprd_adjustment` whenever the
  engine recorded the block — any treatment, including `none`,
  `no_value_to_adjust`, `not_applied_share_count_unverified`,
  `awaiting_cash_flow_check`, `non_usd_no_rate` and
  `amortized_in_base` (the charge; the weighted IV@15/20/25 and IRR
  before → after only when a one-time deduction ran).
- `key_numbers.md` — generated quotable figures. `analysis.md` may only
  quote numbers from here.
- `analysis.md` — the narrative; must resolve every flag.
- `ttm.json` — TTM legs; required when `base_source` is `ttm_json`.
- `fundamentals.json`, `statements.json`, `segments.json`, `profile.json`
  — SEC-derived enrichment. `statements.json` is the full cash-flow and
  balance-sheet history; use it to cross-check the CSV.

Method in one line: OE = operating cash flow − total capex − stock-based
compensation (engine 5.6: acquired in-process R&D expensed at acquisition is
deducted once from every IV and added to the IRR price, never from the base). Base OE/share = median of the last 3 fiscal years, or a TTM
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
   the fix.
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
   not claim the band or alert fields. Since 5.5, make_score rebuilding a
   score on output from another engine release sets `alert_eligible` and
   `exit_alert_eligible` false ("engine output predates release <the current release> (5.6.0 since 2026-10-19) —
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
   replayed with field overrides off), never through ttm.py.
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
   `shares_source` is `diluted_latest_scale_corrected`); `total` is the sum of the periods' `deducted`; every
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
   cash-flow statement, never an exclusion; say "cannot verify from the diff"
   when the PR does not show the filing. A score with a period still `awaiting_cash_flow_check` cannot exist
   (make_score refuses it), nor one with a period excluded `non_usd_no_rate` beside a positive `expense_native`
   (`ACQUIRED_IPRD_UNCONVERTED`, `NEEDS_MAIN_AGENT: currency` — Codex review round 3 of PR #47) or a positive
   `cash_native` (a cash-only payment with no FX rate that could settle a charge — round 4 — or the period's
   cash outflow beside a positive expense, the preferred amount, with no FX rate: never replaced by the
   expense — round 6). A
   `deferred_payment` period counts cash the window's earlier cash-basis charge left unpaid (BIIB), never more
   than that remainder — or, declared in `iprd_deferred_payment` against a `first_charged_period` before the
   window that companyfacts shows expensed (`first_charge_evidence` `companyfacts_expense_fact`), a cash-tag-only
   payment of that pre-window charge (round 3): its cited filing must show the deferred consideration or
   milestone paid in that period, P1 otherwise. [Codex review round 12 of PR #47] A cash-basis period carrying
   a `paid_in_shares` check (`residual_paid_in_shares`: its expense less cash, never accrued as unpaid) needs a
   source showing that residual paid in shares (a non-cash stock-consideration line), P1 otherwise; a
   `deferred_payment` carrying `deferred_payment_assumption` (matched against a residual nothing declared) whose
   analysis.md does not say how that residual was settled is P2 — one the filing shows paid in shares, deducted
   again, is P1. `ACQUIRED_IPRD_UNMATCHED_PAYMENT` resolved without saying what
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
   charges, a first charge whose whole charge is itself declared deferred, a pre-window first charge
   companyfacts covers with no expense fact there, a source accession outside the original filing's years,
   a current-YTD entry, a missing or inconsistent `contingent_total`, one deal's declared amounts summing
   past its `contingent_total`, and — round 8 — an impossible date; make_score refuses a deal whose
   declarations sum below the `paid_to_date` its registry event recorded, or whose lifetime passes the cap.
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
   (P2 otherwise).
   `ACQUIRED_IPRD_CHARGE` / `ACQUIRED_IPRD_RECURRENT` resolved without
   the deal, the cash vs stock consideration or the recurrence assessment is P2. An `iprd_amortized`
   `base_override` must reproduce native base − mean(figures) ÷ shares × ads_ratio to the cent (P1
   otherwise), its figures must be the run's FY `deducted` amounts (three; two at a filer with only two FY;
   each within $1) and the treatment `amortized_in_base` (no one-time deduction on top — both is
   double-counting, P1). Its `native_base` must be the base the one-time run scored — `ttm_json` when that
   run was `--ttm`, and always when `STALE_FY` fires and ttm.json carries a TTM base (the engine refuses the
   median there) — else the median; a native base chosen for a better tier is P1. Treatment
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
   rounded headline figures alone are identity only for a score built before round 12.
   [Codex review round 11 of PR #47, the main agent's shape] A period whose expense or cash figure carries
   `context_basis` `aggregated_quarters` was summed from the three-month / year-to-date facts in
   `aggregated_contexts` (no fact covered the period exactly): those contexts must tile the period with no gap
   and no overlap, P1 otherwise. `ACQUIRED_IPRD_PARTIAL_PERIOD` (`iprd_adjustment.partial_coverage`: a tag
   filed for only part of a window period, nothing counted for it) resolved without the period's full figure
   from the filing and its effect on the IVs / IRR is P2; a material one OE never saw published without
   `NEEDS_MAIN_AGENT: iprd_partial_period` is P1. Since round 12 a $0 fact on one detector tag never hides a
   positive partial fact on the other (only a positive full-period detector fact reads the period).
   With field overrides in force, `override_impact`'s counterfactual holds the
   final run's IPR&D treatment and charge (`DCF_IPRD_HOLD`) in every branch (declared pin, TTM, median,
   payable), so the measured impact is the override's alone.

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
- `tier_override`: a written reason is required, and the reason must be
  consistent with the numbers it cites. An override that lowers the tier
  while the narrative calls the numbers IRR an "artifact" or "upper bound"
  must give the figure it rests on; "materially lower" with no number is
  P2. An override may never raise a tier above the band of the
  numbers without a sourced base figure.

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
`ACQUIRED_IPRD_UNCONVERTED`, `ACQUIRED_IPRD_UNMATCHED_PAYMENT` and `ACQUIRED_IPRD_PARTIAL_PERIOD` (check 8).

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
  is P1 (since 5.5 a filed share count ≤ 0 counts as missing). Engine
  5.5 adds two share gaps no override covers:
  `DATA_GAP:shares — SHARE_SCALE` (gap key `share_scale`) and
  `DATA_GAP:shares — SHARE_CLASS_MISMATCH` (gap key `share_class`).

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
  make_score refuses it). A P&C name scored on the OCF base with only the
  notch is P2 — ask for the payable-earnings base. Life insurers, banks and
  REITs keep the 2026-10-15 rule.

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
  count; a partly deferred period still counts. [Codex review round 8 of PR #47]
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
