#!/usr/bin/env python3
"""score.json builder (v5, 2026-10-13 — zero hand transcription of numbers).

Usage: python3 make_score.py <TICKER>

Builds score.json purely from dcf_numbers.json plus judgment.json in the
company folder. Judgment fields (written by the analyzing agent):
  name, sector, moat_score, moat_justification, moat_for, moat_against
  (optional lists of short pillar strings), probs_used (5 numbers, the
  probabilities passed to the engine), one_liner, confidence,
  tier_override + tier_override_reason, in_scope_under_40b.
  Engine 5.7 (the 2026-10-19 rulings) adds, each read by the lane that
  builds it (v5.7 block below; until then they are not read):
  misfit_notch_reason (R1), moat_scorecard (R4), interim_bridge /
  interim_bridge_declined (R2), share_classes / up_c_suspect_reason (R6),
  capex_unlisted_ack and capex_override.software_included (R8 / R9),
  ttm_rejection_reason (R7); and facts.json beside judgment.json declares
  the facts their reasons cite as [F#] (R3).
Every numeric field in score.json is copied from dcf_numbers.json.

Refuses (exit 1, nothing written) when: dcf_numbers.json has a data gap NOT
covered by an applied override, or no tier; judgment.json is missing/invalid;
probs_used does not sum to 1 or does not match the engine run; moat_score
does not match the engine run; a tier override lacks a written reason.

Round-2 additions (2026-10-14): refuses pre-v5 dcf_numbers.json (engine_version
< 5 or no data_gap field — the v4 bypass); refuses on content_hash mismatch or
absence (hand-edited engine output); refuses a negative override outright and
an out-of-band override (outside 0.1x-10x of the last filed value, or no
filed value) without an ack_reason; refuses a pinned base that differs from
ttm.json's ttm_oe_per_share by >0.1% unless judgment.json declares a matching
base_override; refuses a 20-F/40-F filer with no applied ads_ratio
(DATA_GAP:ads_ratio); refuses an in_scope_under_40b claim that contradicts
the engine's market cap (scope is computed here). Confidence is clamped to
medium (confidence_capped: true) when WIDE_SCENARIO_SPREAD is present. The
registry is rewritten wholesale for the ticker on every run and also records
judgment-call events: tier_override, manual_price, base_override, gterm,
cik, ads_ratio.

Alert gates (v5.4; the exit gate added after the Codex review of PR #2):
alert_eligible gates ENTRIES into Tier S/A — false unless the final tier is
S/A and no suppression reason applies (sector misfit, tier
existing only because of an override, an override lifting a sub-A numeric
tier into S/A, IRR at the solver floor; confidence NEVER suppresses an
alert — Andrew's decision 2026-10-15, applied at the 2026-10-16 live port).
exit_alert_eligible gates EXITS from
S/A — false unless the final tier is below A and the quality checks pass
(sector misfit, tier existing only because of an override).
[v5.5 — re-score audit] "Tier existing only because of an override" covers
a share-scale rescue too: a final run whose share_scale.rescued_by_pin is
true (a declared base_override pin; without it the engine gaps
DATA_GAP:shares — SHARE_SCALE) closes both gates like a field override with
unblocks_tier (NTNX, TEM, VIV).
The IRR floor does not suppress an exit, since a floor IRR reads "at most
terminal growth", which confirms the drop; nor does a tier_override pushing an
S/A numeric tier below A, since a judgment downgrade is still a warning a
holder needs (only a judgment-only upgrade is kept from alerting). Before it,
the S/A tier condition inside alert_eligible meant a qualifying A -> B exit
could never alert.

Overrides (v5.1): judgment.json may carry capex_override / sbc_override /
shares_override ({value, source, reason, kind: "filing"|"estimate"}). They
are validated for shape, cross-checked against dcf_numbers.json's
overrides_applied (value/kind must agree; an override declared for a field
the engine still shows as an uncovered gap refuses), summarized into
score.json, and upserted into the central registry
_system/overrides_registry.json (single writer: this script, fcntl-locked;
the path can be redirected with the MAKE_SCORE_REGISTRY env var, for tests).
[v5.5 — Codex, PR #31] An override that only ttm.py used to fill legs of the
TTM base the score is pinned to (ttm.json overrides_used; the annual engine
applied none, as at APA) is reported (scope ttm_legs), measured on the TTM
base and gated like an applied one: unblocks_tier when ttm.py cannot build
the TTM base without it (ttm_leg_overrides).

Override impact (Andrew's basis, 2026-10-13): measured by THIS script, on
the base the final run actually used — "ttm" when the score's base was a
TTM pin via --base-oe-ps, else "median_3y" — never on the engine-native
base when a TTM pin is in force (that made APP read 0.0%/0.0pp while the
override moved the TTM base actually used by -0.45% and was the only
reason APP had a tier at all). The without-override side reruns the final
run's exact configuration (same moat/probs/offsets/mults/gterm and the
same base pin) with overrides toggled off: for a TTM base the base comes
from ttm.py with DCF_NO_OVERRIDES=1 (zero-fill; reconstructed from the
with-override ttm.py run when the disabled run cannot compute — the gap
is exactly why), for a median base from the engine's side-effect-free
--measure mode with overrides disabled. The block is written to score.json
as override_impact (the HTML and the registry read THIS block) and into
each registry entry, together with unblocks_tier: true when the final
dcf_numbers.json recorded data_gap entries the overrides fully covered —
without them the engine would have exited 4 and there would be no tier.
When the overridden field is shares (a denominator, not a subtractive
leg) no zero-fill counterfactual exists at all: the impact fields are
recorded as null with unblocks_tier: true rather than refusing the score
(first hit: STZ, 2026-10-14, whose FY24-26 diluted shares live only in
the 10-K — both the median and TTM counterfactuals have no denominator).

Also generates <TICKER>/key_numbers.md — every headline figure from the
final dcf_numbers.json in one formatted file. It is the single source
workers quote in analysis.md; no figure should ever be recomputed in prose.

If judgment.json is absent but score.json exists, judgment.json is seeded
from the existing score.json first (the v5 re-run path), then score.json is
rebuilt from the current dcf_numbers.json.

v5.5 (2026-10-19, engine release 5.5.0 — Andrew's rulings on the seven spec
drafts, DESIGN_5.5 §1 / §2c / §7 / §8):
- ADS market cap (decision 1). A run from an engine before 5.5.0
  (engine_release absent or below 5.5.0, and no market_cap_basis record) with
  an applied ads_ratio printed market_cap_est = per-ADS price × ORDINARY share
  count (JD 2x, CHT 10x, TLK 100x too large). For such a run make_score uses
  price × shares_diluted_latest ÷ ratio (dcf_engine.market_cap_est) for
  market_cap_b, the $40B scope check and key_numbers.md (printed with its
  label and the old figure) and records market_cap_basis
  "ads_corrected_by_make_score"; a 5.5 run carries the engine's own
  market_cap_basis.shares_source through untouched (never divided twice).
  When the corrected cap lands on the other side of $40B and judgment.json
  still holds the scope the OLD cap implied, make_score rewrites judgment.json's
  in_scope_under_40b (that one token, formatting kept — precedent:
  seed_judgment), prints the change, and records
  in_scope_corrected_by_make_score: true plus a registry event
  {event: scope_correction, old_cap, new_cap, in_scope}; both stay on every
  later run of the same engine output. Any other disagreement still refuses.
  [ADDITION — M2, round-1 verification] At ads_ratio 1 nothing is corrected
  (price × shares ÷ 1 is the engine's own cap): the basis reads
  diluted_latest and no ADS line is printed.
- [ADDITION — M1, round-1 verification; decision 1's "anything downstream"]
  Net-debt ratio on the ADS basis, separate from the cap correction. No engine
  before 5.5.0 divided the normalized-OE total behind
  diagnostics.net_debt_to_normalized_oe by the ADS ratio (per-ADS OE ×
  ORDINARY shares) — main's 2026-10-18 fix, still stamped 5.4.0, divided the
  cap only (PAC, EMBJ, FUTU, HTHT, LTM, TX, FMS, TLK). So for EVERY pre-5.5
  record with an applied ads_ratio other than 1 and a recorded ratio, whatever
  state its cap is in, key_numbers.md prints the ADS-basis ratio (recorded ×
  ads_ratio) beside the engine's figure and names any crossing ("HIGH_NET_DEBT
  (> 3x) would fire on the ADS basis", "BIG_NET_CASH (< -2x) would fire on the
  ADS basis", "... would no longer fire on the ADS basis"; TX: 1.04x → 10.44x,
  HIGH_NET_DEBT would fire), and score.json records
  net_debt_to_normalized_oe_ads_basis (4 dp). The engine's flag list is hashed
  engine output and is never rewritten here.
- Release mismatch (dcf_numbers.json engine_release != dcf_engine.ENGINE_RELEASE).
  No counterfactual replay: the current engine would measure the override
  against another capex / SBC basis than the recorded run (EMBJ: a 5.5 base
  43% lower from IFRS intangibles alone). override_impact is the prior
  score.json block when it was measured on this run's base, plus
  impact_carried_from_prior_score: true and counterfactual_engine_release;
  otherwise the impact fields are null with a "not measured" note
  (unblocks_tier is computed as before). Both alert gates close:
  alert_eligible / exit_alert_eligible false with the reason "engine output
  predates release 5.5.0 — re-run the engine before an entry / exit alert"
  (a scope-only correction must not turn JD, Tier A on a capex basis the same
  release calls incomplete, into a new alert).
  [ADDITION — M3, round-1 verification] The insurer payable-earnings base
  follows the same rule: under a release mismatch payable_pin_impact (the
  native-base replay through the current engine) is not run. The registry
  base_override event carries the prior run's payable impact (that ticker's
  base_override registry event, when it was measured on this run's pinned base
  and weighted IRR at 4 dp) with impact_carried_from_prior_score: true and
  counterfactual_engine_release; otherwise its impact fields are null with the
  same "not measured" note. Every measurement (the field-override
  counterfactual and the payable replay) runs BEFORE the first write (the
  judgment.json scope rewrite, then score.json), so a failed replay refuses
  with nothing written; an override_impact block on a payable-pinned run is
  labelled base_used "payable_5y" (it was "ttm") also when carried or
  unmeasured.
- share_class_mismatch (decision 2 §5, flag route; [ADDITION — M5,
  round-1 verification] strict shapes): a declaration is ONLY bool true, or an
  object whose `value` is bool true (Codex review 3, PR #31: a non-empty object
  without `value` is malformed, even with a source — an omitted value must not
  block a company). It refuses with DATA_GAP:shares —
  SHARE_CLASS_MISMATCH, also when source / reason are missing. false, null,
  {value: false} and an empty object declare nothing. Anything else — strings
  ("false", "no", "true"), numbers, lists, an object whose `value` is not a
  bool, any non-empty object without `value` (even with a source) — is MALFORMED
  and refuses with "share_class_mismatch must be true or {value: true, source,
  reason}" (dcf_engine.load_share_class_mismatch applies the same rule and
  records {"malformed": <repr>} without raising the gap).
- Override currency (decision 7): an override's `currency`, when present, must
  be "USD" and its kind "filing"; anything else refuses. A USD declaration
  against an engine run that FX-converted the override anyway (a pre-5.5 run,
  or a 5.5 run recording currency_basis "converted") refuses as out of sync.
- key_numbers.md: the market-cap line names its basis, a scope line, one
  "Capex basis" line per last-3 FY (from financials_history.csv's
  capex_source / capex_tag, when the run recorded capex_provenance), a "Share
  basis" line when the run recorded a split adjustment, a cover-page
  divergence or a share-scale defect, and the SBC-reconciled periods.
  [ADDITION — M7, round-1 verification] Also one "Share basis: unconfirmed
  split fact <date> ratio <r> (no post-event cover-page count confirms it) —
  check the latest 10-Q" line per share_basis.unconfirmed_split_facts entry
  (history and price may sit on different bases; no flag of its own), and one
  compact line listing share_basis.in_history_split_facts (informational).
- [ADDITION — WY, after the retro-scan; not in the rulings — it stops an
  approved change (decision 3's PaymentsForCapitalImprovements read) from
  producing a wrong number silently] Superseded capex override: when
  fragility_flags carry OVERRIDE_SUPERSEDED_BY_FILED_TAG:capex (or
  override_checks.capex.superseded_periods is non-empty) AND judgment.json
  still declares capex_override, make_score refuses. The engine's behaviour
  is unchanged (a filed value always wins; an override fills only unfiled
  periods), so the override no longer sets capex where a figure is now filed.
  The worker either (i) removes the override when the newly filed figure IS
  the filer's capex line (RBC / CR / IT: release 5.5 now reads it), or (ii)
  blocks NEEDS_MAIN_AGENT: capex when the filed tag is only part of capex (WY:
  PaymentsForCapitalImprovements 57M / 52M / 51M against a 447M cash-flow
  total, CAPEX_COVERAGE_LOW firing too — scored as is, 3-FY OE would rise
  +76.7% on a partial line).
- [ADDITION — HTHT, same standing] Override read as USD by the last-filed-unit
  fallback: decision 7's fallback stays exactly as ruled in the engine
  (override_checks.<field>.currency_basis 'last_filed_unit_usd' -> used
  verbatim, and recorded). make_score refuses an APPLIED override with that
  basis unless it is a kind "filing" override declaring currency "USD". The
  engine records that basis only at a filer whose figures it FX-converted
  (fx_conversion exists only for a non-USD reporting currency), so this is
  EVERY use of the fallback: under 5.5 the fallback alone no longer yields a
  score — it overturns that part of ruling 7's effect and is listed for
  Andrew's ratification. Reason: the fallback cannot tell a US-dollar figure
  from a local-currency one (HTHT's capex_override is RMB 828M — verbatim it is
  $828M, ~7x the filing's own US$119M). Declare currency "USD" when the source
  states the figure in US dollars (PUK, CX); otherwise restate it or block
  NEEDS_MAIN_AGENT. A kind "estimate" override under that basis is refused too
  (the round-1 exemption was withdrawn after verifier round 2): it cannot
  declare a currency (ruling 7 reserves that for kind filing) and the 0.1x-10x
  band admits a local-currency figure (CNY ~7.2x — HTHT's RMB 828M relabelled
  "estimate" would score as $828M). No recorded folder has such an estimate.

v5.6 (2026-10-19, engine release 5.6.0 — Andrew's acquired-IPR&D one-time
value adjustment):
- score.json `iprd_adjustment` (whenever dcf_numbers.json carries the block —
  output from an older release, or a 5.6 run with no IPR&D expense filed,
  gets no key; [Codex review round 15 of PR #47] a `deferred_payments_only`
  block is copied as a minimal block: treatment none, total and
  charge_per_share 0, no periods, the rolled-out list): treatment, total, charge_per_share, shares_denominator /
  shares_source, materiality / material / recurrent, the per-period records
  (amount, basis, tag, deducted, excluded), the weighted IVs at 15/20/25
  before and after (2 dp), the weighted IRR before and after (4 dp) and the
  tier before; the score's own tier / IRR / IV fields are the engine's
  ADJUSTED figures (the alert gates read them). key_numbers.md prints an
  "Acquired IPR&D adjustment" section: one line per period (amount, basis,
  tag; the deal is not known to the code — analysis.md names it), the total
  and per-share charge, the IVs before → after at 15/20/25% and the weighted
  IRR before → after. The adjustment is mechanical: no registry event.
- base_override basis "iprd_amortized" (the worker's amortized
  maintenance-acquisition base beside ACQUIRED_IPRD_RECURRENT): validated for
  shape (kind filing, one non-negative figure per FY of the engine's
  last-3-FY window — three, or two at a filer with only two FY — a positive share count,
  native_base "ttm_json" | "median_of_last_3_fy_oe_per_share", a numeric
  value) and checked figure for figure against the engine's
  iprd_adjustment.amortized record (treatment amortized_in_base, the run
  pinned through --base-oe-ps at the value); anything else is refused, and an
  amortized engine record without the declaration is refused as out of sync.
  It is a judgment call: the registry base_override event carries basis,
  figures, shares and native_base (part of the declaration identity) and the
  native → pinned base from the run's own record, and ([Codex review r2 of
  PR #47] iprd_amortized_impact) the weighted IRR and tier without the
  override — the final run replayed on its native base, which then takes the
  one-time deduction — beside the run's own. [v5.6 review] Figures are
  compared with the engine's own tolerance ($1 per figure). With
  native_base ttm_json the base is still ttm.json's TTM base: the PR #31
  TTM-leg rules (ttm_leg_overrides) compare ttm.json against the record's
  native base, and the override impact is measured on the TTM branch (the
  no-override TTM base less the same amortization per share).
- [v5.6 review] The override-impact counterfactuals pass DCF_IPRD_HOLD so
  the replay holds the final run's IPR&D treatment and charge per share:
  the charge is mechanical, so the measured impact is the override's alone
  (a --base-oe-ps replay would otherwise read another window and share
  denominator than the --ttm run). [Codex review r1 of PR #47] Every branch
  holds it — declared_pin, ttm, median_3y and payable_5y: on the median and
  payable bases a shares_override that fills the latest FY diluted count
  otherwise moves the replay's share denominator and re-detects the charge.
- Release handling is unchanged: 5.5.0 output rebuilt under the 5.6.0 code is
  another release (both alert gates closed, "engine output predates release
  5.6.0"); predates_55 is False for 5.5.0 and 5.6.0 output alike.
- [ADDITION — fixer review round 2026-10-19, awaiting Andrew's ratification]
  judgment.json `iprd_cash_flow_check` (the worker's reading of the 10-K's
  cash-flow statement for an EXPENSE-basis period, which companyfacts cannot
  show — HALO adds the charge back and pays it in investing, NBIX pays it
  inside OCF): validated for shape (period, window, amount, presentation,
  source; one entry per period and window). make_score refuses a record with
  a period still awaiting the check (ACQUIRED_IPRD_UNCONFIRMED — the run's
  value is not known until the check is declared), a declared check the run
  did not apply or applied differently (judgment.json changed after the run,
  or the amount is not the filed expense), and a check the run applied that
  judgment.json no longer declares. Not a registry event: it records what
  the filing shows, like the cash tag the engine reads itself.
- [fixer review round] An iprd_amortized base on native_base ttm_json is
  refused when ttm.json changed after the run (ttm_oe_per_share no longer
  the record's native base within 0.1%, or ttm_shares_diluted not its share
  count) — the same staleness rule a plain --ttm pin meets; its registry
  event's base_used is "ttm" (the branch its impact is measured on).
- Deferred payments of an earlier deal (Andrew's 2026-10-20 ruling,
  delegated to the main agent, who decided): judgment.json
  `iprd_deferred_payment` ({period, window "fy", amount, deferred_payment_of:
  {deal, first_charged_period, source, contingent_total: {value, source}}})
  is validated for shape (an FY period; an EDGAR accession in the source and
  in the contingent_total's source; one entry per period and deal — several
  deals may share a period; one contingent_total per deal, declared
  consistently, that the deal's declared amounts do not sum past — the
  per-deal cap, the main agent's decision on the review's open item,
  delegated by Andrew 2026-10-20) and must agree with the engine record,
  which validated it against the window and marked the period
  `deferred_payment_of` (a list, one item per deal; `recurrence_excluded`
  when the deals sum to the whole charge): a declaration the run did not
  apply, an applied one judgment.json dropped or now declares differently,
  are refused; an entry whose period left the window is listed in
  `deferred_payments_rolled_out` and STAYS declared ([Codex review round 4 of
  PR #47]: it counts toward its deal's lifetime contingent_total cap, so
  dropping it from judgment.json is refused as out of sync; [Codex review
  round 5] a run whose window holds no charge records the entries in a
  minimal block, `deferred_payments_only`, that score.json copies as a
  minimal block (since Codex review round 15; before, it was dropped, so the
  record and the score disagreed) and
  key_numbers.md shows as a "Rolled out of the window" line — before it the
  block was null and only deleting the entry let the run score). score.json `iprd_adjustment` carries
  `recurrence_excluded` (when the run had declarations) and each period's
  `deferred_payment_of` / `recurrence_excluded`; key_numbers.md says on the
  period line whether it is excluded from the recurrence count or, partly
  deferred, still counts, plus one "Excluded from the recurrence count" line,
  naming each first charge by its date. The deduction is unchanged (except
  a declared cash-tag-only payment of a charge expensed before the window,
  which the engine then deducts — Codex review round 3 of PR #47). [Codex
  review round 8 of PR #47] Each deal's cumulative declared deferred amount
  IS a registry event (`iprd_deferred_payment`: deal, contingent_total,
  paid_to_date, first_charged_period, periods), carried across runs — the
  prior events are read before the wholesale replace and merged — and
  make_score refuses a run whose declarations for a recorded deal sum to less
  than its paid_to_date (an entry deleted or shrunk, even with the engine
  rerun) or whose lifetime (max(the declarations on recorded periods,
  paid_to_date) + newly declared periods) exceeds the contingent_total.
  [Codex review round 10 of PR #47] Every recorded period's amount is
  immutable: a declaration that omits a recorded period or declares it
  more than $1 apart from the recorded amount (shrunk or grown) is
  refused, naming the period, and the event keeps the recorded amounts
  exactly (only new periods merge) — moving amounts between periods at
  an unchanged total had rewritten the record and could make another
  period wholly deferred, out of the recurrence count.
- [Codex review round 3 of PR #47] A period excluded `non_usd_no_rate`
  beside a positive `expense_native` (ACQUIRED_IPRD_UNCONVERTED: a detected
  charge the engine could not convert, so nothing was deducted) is refused,
  NEEDS_MAIN_AGENT: currency, whatever judgment.json says; [Codex review
  round 4] so is one beside a positive `cash_native` (a cash-only payment
  that could settle a charge, with no FX rate even fetched). key_numbers.md's
  total-charge and amortized-base equations print "× ADS ratio r" (per ADS)
  when the applied ratio is not 1, so they reproduce the recorded values.
- [Codex review round 15 of PR #47] A cash-basis period carrying
  `cash_flow_check_inapplicable` (a matching iprd_cash_flow_check whose
  presentation, inside_operating_cash_flow or paid_in_intangible_capex,
  contradicts the deducted cash outflow) is refused, naming the
  presentation. A plain base_override pinned through --base-oe-ps that is not
  ttm.json's figure (base_source agent_supplied_ttm_override) must carry
  `basis_window` on a 5.6 run ({window: "ttm", ytd_current_period} or
  {window: "fy"}), recorded by the run as inputs.base_basis_window and, for
  "ttm", still ttm.json's ytd_current_period; output from an earlier release
  is not held to it (VNOM's 5.4.0 record rebuilds unchanged).
- [Codex review round 22 of PR #47] judgment.json's IPR&D inputs must be
  the ones the run read (check_iprd_judgment_current): a run recording
  iprd_judgment_hash is refused when the current judgment.json hashes
  differently (dcf_engine.iprd_judgment_hash); a record predating the hash
  is refused when an iprd_cash_flow_check names a period the run has a
  record of without a trace of reading it (applied, mismatched,
  inapplicable or unused) — "judgment.json changed after the engine run —
  rerun dcf_engine.py".
- [Codex review round 23 of PR #47] ttm.json must be the one the run read
  (check_ttm_inputs_current): a pinned run records ttm_inputs
  (dcf_engine.ttm_inputs_record — ttm_oe_per_share, ttm_shares_diluted,
  inputs.ocf.ytd_current_period and ttm_input_hash over ttm.json's input
  legs) and is refused when the current ttm.json gives anything else; a
  record predating ttm_inputs whose positive IPR&D charge is on ttm.json's
  share count (HALO's committed 5.6.0 record) is refused unless the current
  ttm_shares_diluted equals its shares_denominator and ytd_current_period
  its window.ttm_current_ytd — "ttm.json changed after the engine run —
  rerun dcf_engine.py". Older records keep the 0.1% base check alone.
- [Codex review round 25 of PR #47] The ttm.json check follows the record:
  ttm_inputs null (a median run, a pin declared built on FY figures) is
  held to nothing. Every declared-pin and ttm.json-figure match
  (dcf_engine.pin_matches) is 0.1% of the reference, or half a cent per
  share when either side is zero, so a $0.00 amortized base and a zero
  TTM base are scoreable.
- [Codex review round 26 of PR #47] The half cent is declaration
  arithmetic only (an iprd_amortized value, dcf_engine.declared_value_matches):
  every undeclared match against ttm.json (base pin provenance via_ttm,
  ttm_leg_overrides, _declared_pin_not_ttm, check_iprd_amortized_ttm_current)
  and a plain declaration's value use dcf_engine.figure_matches — 0.1%, a
  zero only by an exact zero — so a --base-oe-ps 0.004 beside a $0.00 TTM
  base is an arbitrary pin, not Tier D on ttm.json's Tier F base. The
  registry (load_registry, every reader and writer here) must be a JSON
  object with an `entries` list of objects, else "overrides_registry.json
  is malformed — restore it from git"; only a missing file is a first run.
- [Codex review round 24 of PR #47] A --base-oe-ps pin its judgment.json
  base_override declares built on FY figures (declared_fy_built_pin:
  iprd_amortized on the median native base, or basis_window {"window":
  "fy"}) is never ttm.json's pin, even when it equals ttm_oe_per_share
  within 0.1%: base pin provenance checks it as the declared base
  (check_base_basis_window included), its override impact is measured on
  the declared-pin branch, and ttm_leg_overrides does not hold it to
  ttm.json's overrides_used. check_iprd_unconverted also refuses a period
  the engine gated for a positive detector tag it cannot compare with the
  other (expense_tag_unconverted).
- [Codex review round 28 of PR #47] load_registry also refuses a registry
  holding any malformed iprd_deferred_payment event, whatever its ticker
  (registry_deferred_event_problem: ticker and deal non-empty strings, the
  ticker without surrounding whitespace, a real first_charged_period and date, a valid contingent_total, paid_to_date
  a finite number > 0, periods a non-empty list of {real date, finite
  amount > 0} with no period twice), naming the entry's index, its ticker
  and the field; iprd_deferred_lifetime no longer skips one silently (a
  missing deal had read the deal's recorded payments as none, and the
  wholesale replace erased them). When the engine records the recurrence
  gate's own figure (recurrence_expense_total / recurrence_materiality: 2 or
  more FY charge years), score.json `iprd_adjustment` copies it and
  key_numbers.md prints a "Recurrence" line beside the deduction's
  materiality. [Re-verification of round 28] Every entry is read for what
  it is (registry_entry_problem): one carrying a deferred-payment event's
  fields (deal, first_charged_period, contingent_total, paid_to_date,
  periods) must be an iprd_deferred_payment event by its exact name (a
  misspelt or deleted event name had passed, its payments read as none
  and the record erased), a deferred-payment event's ticker must be
  upper-case (make_score's own), and an entry that is neither a field
  override nor an event make_score writes is refused too.

v5.7 (2026-10-19, engine release 5.7.0 — Andrew's rulings R1-R9). "A 5.7
run" is engine output from release 5.7.0 or later (is_57_run =
facts.is_rulings_run; RELEASE_57 = facts.RULINGS_RELEASE, fixed at 5.7.0).
The new worker obligations bind 5.7 runs only; output from an older release
(every folder on file until its next engine run, HALO's 5.6.0 record too) is
rebuilt as before, both alert gates closed ("engine output predates release
5.7.0"). Each lane writes its own item below:
- (L0, the scaffold, 2026-10-21) The release bump, and the places the lanes
  fill, behaviour unchanged: key_numbers.md is built as one text
  (build_key_numbers) before the write phase and written last inside it
  (write_key_numbers_text, the same atomic write), with one empty hook per
  lane (_kn_*) in the 07 §1.9 section order; update_registry takes one
  keyword per lane and appends each lane's events (_*_events, none yet)
  after the deferred-payment events, before keep_first_dates; main() calls
  a no-op placeholder at each 07 §1.12 step, every one before
  registry_transaction (every refusal precedes the first write, the
  registry); quoted() is the echo convention for worker text (07 §1.10);
  check_influence is the one influence-trace entry point (L2 fills it);
  iprd_override_required is check_iprd_share_count_unverified's condition,
  factored out for L1; SCORE_DECISION_KEYS is the score.json decision list
  pr_worktree reads (each lane appends its block). The registry whitelist
  (_EVENT_DECLARATION) declares every event type the 5.7 lanes write
  (misfit_notch, declared_facts, moat_divergence, moat_low_roic,
  moat_high_return_low_moat, moat_erosion_rebuttal, moat_widening_declined,
  interim_bridge, interim_bridge_declined, share_classes, up_c_suspect,
  capex_unlisted_ack, base_alternatives), `facts` on the tier_override and
  base_override identities, `share_basis` / `share_period` on
  base_override's and `software_included` on a field override's (keys no
  recorded entry carries: json null on both sides, so no entry is
  re-dated). A new registry event must be a key of _EVENT_DECLARATION
  before any run writes it — load_registry refuses the whole registry on an
  unknown event — and must not use an iprd_deferred_payment field name
  (IPRD_DEFERRED_EVENT_KEYS: deal, first_charged_period, contingent_total,
  paid_to_date, periods), or registry_entry_problem reads it as a malformed
  deferred-payment event. Deploy order: a pre-5.7 make_score refuses a
  registry holding any 5.7 event, so every tree on the VM runs 5.7 code
  before the first 5.7 write (the drift guard, lane L5).
- (L1, R1) The mechanical sector-misfit notch (misfit_notch,
  misfit_notch_reason, the misfit_notch event). Andrew, 2026-10-19: every
  sector misfit publishes ONE tier below its numbers tier, with a written
  reason that carries a number, mechanically — no reviewer grades it again.
  Detection (misfit_detection = dcf_engine.misfit_status): the 5.7 engine's
  sector_model (universe sector Finance / Real Estate / Utilities OR EDGAR
  SIC in MISFIT_SIC_RANGES), else an older run's SECTOR_MODEL_MISMATCH flag,
  else the folder's own SIC (fundamentals.json / profile.json) — so a rebuild
  catches OSCR / MOH / CNC (6324) and AES (4991) with no engine re-run. A
  present SIC outside 6000-6799 and every misfit range sets a misfit universe
  sector aside (default Q1 (b), main agent 2026-10-21, pending Andrew; the
  switch is dcf_engine.SIC_SETS_ASIDE_SECTOR, and it reaches a 5.7 engine
  record too: misfit_status re-reads its recorded sector and SIC under the
  current rules): such a name is modeled and score.json
  misfit_sector_set_aside says why (EDU 8200, WCN 4953, FN 3661, CSGP 7389,
  EFX / TRU 7320 on a rebuild; GFL 4953, with no folder SIC, on its first
  5.7 engine run). A 5.7 SIC-only misfit's basis names no universe sector.
  model_fit keeps its meaning.
  misfit_notch(...) (after check_no_double_softening, whose refusal keeps
  priority) sets tier_final and score.json misfit_notch {applies,
  tier_by_numbers, tier_after_notch, reason, reason_source judgment |
  tier_override | auto, not_applied null | payable_base | tier_floor_D |
  tier_F, basis}, present on every misfit. Not notched: a payable-earnings
  pin (payable_base, --base-judgment: it already measures what common
  shareholders earn) and a numbers tier of D (the lowest graded tier) or F
  (no positive owner's earnings) — the block records why. A hand pin such as
  SF's --base-oe-ps net-income base IS notched. The notch acts on the
  numbers tier as recorded (the IPR&D-adjusted one when a deduction applies;
  the auto reason then says so). A tier_override above the notched tier is
  refused on every rebuild (R-1); one below it is a further judgment
  downgrade in force (tier_override_reason kept, tier_override event); one
  equal to it is the legacy notch on output from before 5.7 (its reason
  moves to misfit_notch.reason, reason_source tier_override, no
  tier_override event) and refused on a 5.7 run (R-2: the notch is
  mechanical), except where check_iprd_share_count_unverified requires the
  main agent's hand-deduction override (iprd_override_required): it is then
  in force at the notched tier. On a 5.7 run of a notched misfit judgment.json
  must carry misfit_notch_reason with a number (R-3 / R-4; the facts lane
  traces it through check_influence); before 5.7 an auto reason with the
  weighted IRR is written when there is none. misfit_notch_reason must be a
  string or null (R-5). Every refusal precedes registry_transaction. The
  registry records a misfit_notch event {tier_by_numbers, tier_final (the
  notched tier), weighted_irr, reason, reason_source, basis} when the notch
  applies (not-applied blocks record none); a prior tier_override event is
  also matched as a misfit_notch declaration (keep_first_dates), so a legacy
  notch keeps the date it was first taken. Since the declaration includes
  the reason, an auto reason quoting the weighted IRR is re-dated when an
  engine re-run moves the IRR inside the same tier (the text changed); a
  make_score-only rebuild keeps the date — deliberate, do not "fix" it.
  key_numbers.md's tier line names the notch (numbers tier B → C), followed
  by "- Misfit notch (<source>): “reason”" or "- Misfit notch: not applied —
  “reason”"; every echoed reason is quoted() (07 §1.10). The alert gates are
  unchanged (alert_reasons sees the override only while it is in force; a
  misfit closes both gates as before). seed_judgment never seeds the notch as
  a tier_override.
- (L2, R3) facts.json, the quote gate's key_numbers lines, saved method
  runs, the declared_facts event (strict quoting — Andrew, 2026-10-19).
  Every number in a 5.7 run's analysis.md must trace to a generated file
  (check_quotes.py; queue.py done / pass2-done refuse a run that fails).
  load_declared_facts validates <T>/facts.json (facts.py: ids F1.., kinds
  folder / filing / release / third_party, types actual / guidance /
  estimate / metric / event), VERIFIES every folder fact against the named
  file (<file>:<selector>; unit and value at the declared precision),
  reproduces calc facts, checks that a non-folder fact's snippet (under 25
  words) shows its number, refuses a filing / release / third-party fact
  that repeats a folder figure (same metric and period, or a same-period
  leaf at >= 4 significant digits) and marks guidance / estimates older
  than the latest filing the engine used STALE (never a refusal). A
  declaration new or edited since the prior score (facts_sha256) is
  authoring — a folder fact that does not verify refuses; an unchanged one
  is a rebuild — drift is recorded and the run scores. load_method_runs
  reads the saved runs dcf_numbers_<label>.json (check_quotes.py
  --save-run): a tampered or foreign one refuses a 5.7 run and is skipped
  with a warning on an older one. check_influence (5.7 runs only): the
  tier_override_reason and a plain base_override's reason + source (L1
  calls it for misfit_notch_reason, every other lane for its own reason
  fields) cite facts as [F#]; every number in them traces to an engine
  source or a cited fact — never judgment.json, never worker text the
  engine echoes into its flag strings (ads_ratio.source in
  ADS_RATIO_APPLIED, an override's source) — a reason (but not a pin)
  carries a number, rests never on third-party facts alone, a hand pin's
  own figure never anchors its reason (an engine figure other than the pin
  or a cited filing / release / folder fact tagged base_override must),
  and a cited fact lists the field's used_for tag
  (facts.INFLUENCE_TAGS) — an unverified-share-count IPR&D override is held
  to the same rule (its share count a filing fact, the charge a calc fact,
  the adjusted IRR from a saved run; Q2 default, rebase A14). key_numbers.md
  gains engine lines (price vs weighted IV@15%, price ÷ base OE/share, the
  return / margin series, the Filed history table after Growth & moat, the
  probability weights), "Method runs" (+ the previous score), and
  "Declared facts (not engine output)" last; worker text it echoes (the
  Overrides table source and reasons, the payable Source) is in “…”.
  score.json gains key_numbers_sha256 (of the text as written, LF),
  declared_facts, method_runs and previous_score (dcf_content_hash is #47's).
  The registry gains one declared_facts event per run with a facts.json
  (identity facts_sha256) and `facts` citations on the tier_override /
  base_override events whose reason cites facts (only then: legacy events
  are never re-dated). Pre-5.7 output rebuilds with the new lines only; its
  reasons are never traced and its analysis is reported, never gated.
- (L3, R4 revised: sources + 11-pillar evidence + supporting factors,
  M1b / M1c) moat_scorecard / moat_evidence and the moat events: [L3
  writes this item]
- (L3b, M6 moat direction, Andrew 2026-10-20) the trend sync and
  moat_widening_declined: [L3b writes this item]
- (L4, R2) the declared 6-K interim bridge and the annual-instance check:
  [L4 writes this item]
- (L8, R6) declared share classes (Up-C / multi-class) and UP_C_SUSPECT:
  [L8 writes this item]
- (L9, R8 / R9) capex components, capitalized software and the ttm.json
  release stamp: [L9 writes this item]
- (R7) STALE_FY discretion made checkable: ttm_rejection_reason and the
  one base_alternatives record: [R7 writes this item]
- (L5 ops, L6 site) no scoring change: pr_worktree prepare compares
  SCORE_DECISION_KEYS; the site renders the blocks above.
"""
import json, sys, os, re, datetime, subprocess, hashlib, csv, contextlib, math
# Every file is read and written as UTF-8 (most judgment.json files carry raw
# UTF-8 text; Windows Python otherwise defaults to cp1252 and mangles it).
from zoneinfo import ZoneInfo
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _lock import locked  # v5.4: cross-platform exclusive file lock (fcntl / msvcrt)
from _stable import _replace  # [Codex review r21 of PR #47] os.replace, retried on a Windows PermissionError
import dcf_engine as _engine  # v5.5: the release stamp and the market-cap formula (no I/O at import)
from dcf_engine import ENGINE_RELEASE
import check_quotes as _quotes  # v5.7 (L2, R3): the quote gate's sources, saved runs and filed-history rows
import quote_tokens as _qt  # v5.7 (L2, R3): the one tokenizer (reasons carry / trace numbers through it)
import facts as _facts  # v5.7: the rulings-release predicate and the facts.json schema (stdlib, no I/O at import)

# v5.4: $STOCKS_BASE or the parent of _system/ — the tooling runs anywhere.
BASE = os.environ.get("STOCKS_BASE") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SYS_DIR = f"{BASE}/_system"
ENGINE = f"{SYS_DIR}/dcf_engine.py"
TTM_PY = f"{SYS_DIR}/ttm.py"
PAYABLE_BASIS = "payable_earnings_5y"
IPRD_AMORTIZED_BASIS = getattr(_engine, "IPRD_AMORTIZED_BASIS", "iprd_amortized")   # v5.6
IPRD_NATIVE_BASES = tuple(getattr(_engine, "IPRD_NATIVE_BASES", ("ttm_json", "median_of_last_3_fy_oe_per_share")))
IPRD_CF_CHECK_KEY = _engine.IPRD_CF_CHECK_KEY   # [fixer review round] judgment.json iprd_cash_flow_check
IPRD_DEFERRED_KEY = _engine.IPRD_DEFERRED_KEY   # Andrew's 2026-10-20 ruling (delegated): judgment.json iprd_deferred_payment
PAYABLE_SIC = frozenset({"6331", "6351"})  # P&C insurers and reinsurers (mirrors dcf_engine.PAYABLE_SIC)
LABELS = ["super_bear", "bear", "base", "bull", "super_bull"]
TIERS = ("S", "A", "B", "C", "D", "F")
TIER_ORDER = {t: i for i, t in enumerate(reversed(TIERS))}  # F=0 … S=5: higher is better
CONFIDENCE = ("low", "medium", "high")
OVERRIDE_KEYS = {"capex": "capex_override", "sbc": "sbc_override", "shares": "shares_override"}
REGISTRY = os.environ.get("MAKE_SCORE_REGISTRY") or f"{SYS_DIR}/overrides_registry.json"
# v5.7 — R7 STALE_FY discretion made checkable (Andrew, 2026-10-19; L0 placeholders, the R7 lane fills them)
TTM_REJECTION_KEY = "ttm_rejection_reason"            # judgment.json: the reason a STALE_FY TTM base is rejected
BASE_KINDS = ("annual_median", "ttm", "declared_interim", "payable_5y", "declared_pin")
BASE_ROLES = ("published", "rejected", "alternative")
REPLAY_PURPOSE_ENV = "DCF_REPLAY_PURPOSE"             # "base_alternatives" on R7 replays (the engine ignores it)
# v5.7 (lane L5's P2): the score.json fields that carry a decision — pr_worktree prepare compares them between the
# sweep tree's score and the worktree's rebuild. Each lane appends its own block when it starts writing it
# (misfit_notch L1, moat_evidence L3, interim_bridge / interim_bridge_declined L4, share_classes L8,
# base_alternatives R7). Pure data.
SCORE_DECISION_KEYS = ("tier_final", "tier_by_numbers", "implied_irr", "iv_at_15", "base_oe_per_share", "model_fit",
                       "confidence", "alert_eligible", "exit_alert_eligible", "dcf_content_hash", "iprd_adjustment",
                       "fragility_flags",
                       "misfit_notch", "misfit_sector_set_aside")                       # L1 (R1)


def fail(msg):
    print(f"make_score.py: REFUSED — {msg}", file=sys.stderr)
    sys.exit(1)


def seed_judgment(folder, score):
    probs = []
    sc = score.get("scenarios") or {}
    for lbl in LABELS:
        p = (sc.get(lbl) or {}).get("prob")
        if p is None:
            fail("cannot seed judgment.json: existing score.json lacks scenario probabilities")
        probs.append(p)
    override = None
    reason = None
    # v5.7 (L1, R1): a final tier that is the mechanical misfit notch is make_score's own, not a judgment to seed
    # (unless an override was in force at that tier: score.json then still carries its tier_override_reason)
    mn = score.get("misfit_notch") if isinstance(score.get("misfit_notch"), dict) else {}
    notched = bool(mn.get("applies") and score.get("tier_final") == mn.get("tier_after_notch")
                   and not score.get("tier_override_reason"))
    if (score.get("tier_final") and score.get("tier_by_numbers") and score["tier_final"] != score["tier_by_numbers"]
            and not notched):
        override = score["tier_final"]
        reason = "Seeded from the pre-v5 score.json — the original override reason is in analysis.md"
    j = {"name": score.get("name"), "sector": score.get("sector"),
         "moat_score": score.get("moat_score"), "moat_justification": score.get("moat_justification"),
         "probs_used": probs, "one_liner": score.get("one_liner"),
         "confidence": score.get("confidence"), "tier_override": override,
         "tier_override_reason": reason, "in_scope_under_40b": score.get("in_scope_under_40b")}
    if isinstance(score.get("moat_for"), list):
        j["moat_for"] = score["moat_for"]
    if isinstance(score.get("moat_against"), list):
        j["moat_against"] = score["moat_against"]
    with open(f"{folder}/judgment.json", "w", encoding="utf-8") as f:
        json.dump(j, f, indent=1)
    print(f"make_score.py: seeded judgment.json from existing score.json in {folder}")


def check_str_list(j, key):
    if key in j and j[key] is not None:
        if not isinstance(j[key], list) or not all(isinstance(x, str) for x in j[key]):
            fail(f"judgment.json: {key} must be a list of strings")


def validate_overrides(j):
    """Shape-check judgment.json's override objects; returns {field: override}."""
    out = {}
    for field, key in OVERRIDE_KEYS.items():
        o = j.get(key)
        if o is None:
            continue
        if not isinstance(o, dict):
            fail(f"judgment.json: {key} must be an object {{value, source, reason, kind}}")
        if not isinstance(o.get("value"), (int, float)) or isinstance(o.get("value"), bool):
            fail(f"judgment.json: {key}.value must be a number")
        if o["value"] < 0:
            # Round-2: a negative override is impossible, not a judgment call
            # (a negative capex override manufactured a Tier S in the harness).
            fail(f"judgment.json: {key}.value {o['value']} is negative — an override can never be "
                 "negative (capex / SBC / share counts are >= 0); refused outright")
        if o.get("kind") not in ("filing", "estimate"):
            fail(f"judgment.json: {key}.kind must be \"filing\" or \"estimate\"")
        if not str(o.get("source") or "").strip():
            fail(f"judgment.json: {key}.source must be a non-empty string")
        if not str(o.get("reason") or "").strip():
            fail(f"judgment.json: {key}.reason must be a non-empty string")
        # v5.5 (decision 7): an override the filing states in USD may say so;
        # the engine then uses it verbatim instead of FX-converting it. Only a
        # filing figure can carry that declaration, and only USD exists.
        cur = o.get("currency")
        if cur is not None:
            if not isinstance(cur, str) or cur.strip().upper() != "USD":
                fail(f"judgment.json: {key}.currency {cur!r} is not allowed — the only declarable currency is \"USD\" "
                     "(an override in the filing's own currency carries no currency key; the engine FX-converts it)")
            if o["kind"] != "filing":
                fail(f"judgment.json: {key}.currency \"USD\" requires kind \"filing\" (got {o['kind']!r}) — only a "
                     "figure read from the filing in USD is used verbatim; an estimate never is")
        out[field] = o
    return out


SHARE_CLASS_SHAPE = "share_class_mismatch must be true or {value: true, source, reason}"


def _nonempty_str(v):
    return v.strip() if isinstance(v, str) and v.strip() else None


def share_class_status(j):
    """judgment.json share_class_mismatch -> (status, source, reason) with
    status "declared" | "none" | "malformed" — the engine's rule
    (dcf_engine.load_share_class_mismatch; [ADDITION — M5] strict shapes):
      declared: bool True, or an object whose `value` is bool True;
      none:     absent, null, false, {value: false}, an empty object;
      malformed: anything else — strings ("false", "no", "true"), numbers,
                lists, an object whose `value` is not a bool, and (Codex
                review 3, PR #31) any non-empty object without `value`, even
                one that carries a source."""
    v = j.get("share_class_mismatch") if isinstance(j, dict) else None
    if v is None or v is False:
        return "none", None, None
    if v is True:
        return "declared", None, None
    if isinstance(v, dict):
        src, why = _nonempty_str(v.get("source")), _nonempty_str(v.get("reason"))
        if "value" in v:
            if v["value"] is True:
                return "declared", src, why
            if v["value"] is False:
                return "none", None, None
            return "malformed", None, None
        return ("none" if not v else "malformed"), None, None
    return "malformed", None, None


def share_class_declared(j):
    """(declared, source, reason) — see share_class_status (a malformed value
    is not a declaration; refuse_share_class_mismatch refuses it on its own)."""
    status, src, why = share_class_status(j)
    return (status == "declared"), src, why


def refuse_share_class_mismatch(j):
    """DESIGN §2c: a declared share_class_mismatch never scores — not even when
    its source / reason are missing (the engine raises DATA_GAP:shares on it;
    this refusal also covers output from an engine that predates the rule).
    [ADDITION — M5] A malformed value refuses too, naming the accepted shapes
    (a typo such as "false" must neither block silently as a declaration nor
    be ignored)."""
    status, src, why = share_class_status(j)
    if status == "malformed":
        fail(f"judgment.json: {SHARE_CLASS_SHAPE} (got {j.get('share_class_mismatch')!r}); false, null or "
             "{value: false} declare nothing — fix the value and re-run the engine")
    if status != "declared":
        return
    fail("DATA_GAP:shares — SHARE_CLASS_MISMATCH: judgment.json declares that the filed share count is a different class "
         f"from the traded security ({src or 'no source given'}{'; ' + why if why else ''}); no per-share base can be "
         "priced against the traded share — no tier. Block via queue.py with the reason "
         f"'NEEDS_MAIN_AGENT: shares — SHARE_CLASS_MISMATCH: {src or '<filing source>'}' (WORKER_SPEC step 4; no override "
         "can cover this gap, so it is not a DATA_GAP block)"
         + ("" if (src and why) else " (the declaration also lacks a source and/or reason: add them so the block is auditable)"))


# ---------------------------------------------------------------------------
# v5.7 lane L8 (R6 declared share classes, Andrew 2026-10-19/20) — L0 placeholders, no-ops until L8 fills them
# ---------------------------------------------------------------------------
def validate_share_classes(j):
    """v5.7 placeholder (L8, 08 §8.1 step 2): judgment.json share_classes shape + snippets (R-1). None in L0."""
    return None


def check_share_classes_sync(n, j_sc, folder):
    """v5.7 placeholder (L8): the declaration against the engine run's record (R-2 … R-5). No-op in L0."""
    return None


def check_up_c_obligation(n, j):
    """v5.7 placeholder (L8, R-8): an unresolved UP_C_SUSPECT on a 5.7 run. No-op in L0."""
    return None


def check_ttm_on_declaration(n, j_sc, tt):
    """v5.7 placeholder (L8, R-6, after check_ttm_inputs_current): a TTM-pinned score's ttm.json must be on the
    share_classes declaration. No-op in L0."""
    return None


def share_classes_impact(ticker, n, j_sc, prior_score=None):
    """v5.7 placeholder (L8, 08 §8.4): the filed-class vs total-unit replay, before the first write. None in L0."""
    return None


def share_classes_raise_reason(sc_impact):
    """v5.7 placeholder (L8, 08 §8.8): the alert_reasons share_classes_raise text when the declaration RAISES the
    tier (an entry alert is then suppressed). None in L0 (alert_reasons unchanged)."""
    return None


def score_share_classes_fields(score, n, j_sc, sc_impact):
    """v5.7 placeholder (L8, 08 §8.5): score.json share_classes / up_c_check blocks. No-op in L0."""
    return None


# ---------------------------------------------------------------------------
# v5.5: engine release, ADS market cap, scope (DESIGN §1 / §8)
# ---------------------------------------------------------------------------
def release_tuple(rel):
    """'5.4.0' -> (5, 4, 0); '5.5' -> (5, 5, 0); None / unparseable -> None."""
    m = re.match(r"\s*(\d+)\.(\d+)(?:\.(\d+))?", rel) if isinstance(rel, str) else None
    if not m:
        return None
    return tuple(int(x or 0) for x in m.groups())


def predates_55(n):
    """True when dcf_numbers.json comes from an engine before release 5.5.0:
    engine_release absent (a pre-5.4 run) or below 5.5.0, and no
    market_cap_basis record (5.5 writes one; never correct a 5.5 cap twice)."""
    if "market_cap_basis" in n:
        return False
    t = release_tuple(n.get("engine_release"))
    return t is None or t < (5, 5, 0)


def release_mismatch_reason(rel):
    """Why the run is not on the current engine release (alert-gate text)."""
    t, cur = release_tuple(rel), release_tuple(ENGINE_RELEASE)
    if t is None or (cur is not None and t < cur):
        return f"engine output predates release {ENGINE_RELEASE}"
    return f"engine output is from release {rel}, not the current release {ENGINE_RELEASE}"


# v5.7 (07 §1.1): the rulings release — one predicate, defined in facts.py and shared by every 5.7 module
RELEASE_57 = _facts.RULINGS_RELEASE
is_57_run = _facts.is_rulings_run


def _num(v):
    return v if isinstance(v, (int, float)) and not isinstance(v, bool) else None


# dcf_engine.market_cap_est — the one formula (price × shares ÷ ratio when
# an ADS ratio applies, price × shares otherwise), shared with the engine and
# reprice.py; never a local copy that could drift.
market_cap_estimate = _engine.market_cap_est  # the engine's one cap formula (alias kept for this module's call sites)


def _applied_ads_ratio(n):
    """The engine's applied ads_ratio.ratio as a float when it is a positive
    number other than 1 (ratio 1: per-ADS and per-ordinary figures coincide,
    nothing to correct — [ADDITION — M2]); None otherwise."""
    a = n.get("ads_ratio")
    ratio = _num(a.get("ratio")) if isinstance(a, dict) else None
    if not ratio or ratio <= 0 or float(ratio) == 1.0:
        return None
    return float(ratio)


def ads_cap_correction(n):
    """DESIGN §1 (make_score part): for pre-5.5 engine output with an applied
    ads_ratio other than 1, both price and shares_diluted_latest, and a
    recorded cap equal to price × shares_diluted_latest (the uncorrected
    formula), the corrected market cap {cap, old_cap, ratio}; None otherwise
    (no ratio, ratio 1 — M2: the corrected and uncorrected caps are the same
    figure, so the basis reads diluted_latest —, a 5.5 run, a cap that already
    divides by the ratio, or a universe-fallback cap)."""
    if not predates_55(n):
        return None
    ratio = _applied_ads_ratio(n)
    price, shares = _num(n.get("price")), _num(n.get("shares_diluted_latest"))
    if not ratio or not price or not shares:
        return None
    cap = market_cap_estimate(float(price), float(shares), float(ratio))
    if cap is None:
        return None
    old = _num(n.get("market_cap_est"))
    # Correct only a cap the engine actually printed on the ordinary count
    # (price × shares, no division). Main's 2026-10-18 engine fix (still
    # stamped 5.4.0) already divides by the ratio — those records (PAC, EMBJ,
    # FUTU, HTHT, LTM, TX, FMS, TLK re-scored 2026-10-19) must never be divided
    # a second time; a universe-fallback cap is never rescaled either.
    if old is None or abs(old - float(price) * float(shares)) > 1e-6 * max(1.0, abs(old)):
        return None
    return {"cap": cap, "old_cap": old, "ratio": float(ratio)}


# The engine's two net-debt flags and their thresholds (dcf_engine: nd_ratio > 3 / < -2).
ND_FLAG_RULES = (("HIGH_NET_DEBT (> 3x)", lambda x: x > 3), ("BIG_NET_CASH (< -2x)", lambda x: x < -2))


def ads_net_debt_basis(n):
    """[ADDITION — M1] The net-debt ratio on the ADS basis for pre-5.5 engine
    output, independent of the market-cap correction: no engine before 5.5.0
    divided the normalized-OE total by the ADS ratio (it multiplied per-ADS OE
    by the ORDINARY share count — main's 2026-10-18 fix divided the cap only),
    so diagnostics.net_debt_to_normalized_oe is `ratio` times too small.
    Returns {ratio, engine, ads_basis, would_fire, would_no_longer_fire} for a
    pre-5.5 record with an applied ads_ratio other than 1 and a recorded ratio;
    None otherwise (a 5.5 run already computes it on the ADS basis)."""
    if not predates_55(n):
        return None
    ratio = _applied_ads_ratio(n)
    nd = _num((n.get("diagnostics") or {}).get("net_debt_to_normalized_oe"))
    if ratio is None or nd is None:
        return None
    ads = nd * ratio
    fired = lambda x: [name for name, on in ND_FLAG_RULES if on(x)]  # noqa: E731
    return {"ratio": ratio, "engine": nd, "ads_basis": ads,
            "would_fire": [f for f in fired(ads) if f not in fired(nd)],
            "would_no_longer_fire": [f for f in fired(nd) if f not in fired(ads)]}


def net_debt_line(n):
    """key_numbers.md's net-debt line: the engine's figure, or (M1) the
    ADS-basis ratio beside it with any flag crossing named."""
    nd = _num((n.get("diagnostics") or {}).get("net_debt_to_normalized_oe"))
    adj = ads_net_debt_basis(n)
    if adj is None:
        return f"- Net debt / normalized OE: {nd:.2f}x" if nd is not None else "- Net debt / normalized OE: —"
    moved = [f"{f} would fire on the ADS basis" for f in adj["would_fire"]] \
        + [f"{f} would no longer fire on the ADS basis" for f in adj["would_no_longer_fire"]]
    return (f"- Net debt / normalized OE: {adj['ads_basis']:.2f}x on the ADS basis (make_score: the pre-5.5 engine's "
            f"ratio × ads_ratio {adj['ratio']:g} — it divided net debt by per-ADS OE × ORDINARY shares; the engine printed "
            f"{adj['engine']:.2f}x" + (f" — {'; '.join(moved)}; the engine's flag list predates the fix" if moved else "")
            + ")")


def market_cap_basis(n, corr):
    """score.json market_cap_basis: "ads_corrected_by_make_score" for a
    corrected pre-5.5 ADS cap; a 5.5 run's own market_cap_basis.shares_source;
    for other pre-5.5 output "diluted_latest" (the engine's price ×
    shares_diluted_latest) or "universe_market_cap" (its fallback when price or
    shares were missing); None when there is no cap or no record of its basis."""
    if corr:
        return "ads_corrected_by_make_score"
    mb = n.get("market_cap_basis")
    if isinstance(mb, dict):
        # the engine's universe.csv fallback (no price or no share count): engine 5.5 records shares_source
        # "universe_market_cap" there; the formula check also names it for a record whose source says otherwise
        return "universe_market_cap" if str(mb.get("formula") or "").startswith("universe") else mb.get("shares_source")
    if isinstance(mb, str):
        return mb
    if predates_55(n) and _num(n.get("market_cap_est")) is not None:
        return "diluted_latest" if (_num(n.get("price")) and _num(n.get("shares_diluted_latest"))) else "universe_market_cap"
    return None


def scope_decision(j_scope, cap, corr):
    """(computed_scope, rewrite_to, corrected). computed_scope: cap < $40B
    (None without a cap). In the pre-5.5 ADS branch, when the correction moves
    the cap across $40B: rewrite_to = the corrected scope if judgment.json
    still holds the scope the OLD cap implied (else None), and corrected =
    True whenever judgment ends up on the corrected scope (this run's rewrite
    or an earlier one) — the score then differs from what the engine's own cap
    says, which is exactly what in_scope_corrected_by_make_score records."""
    computed = (cap < 40e9) if _num(cap) is not None else None
    if computed is None or not corr or _num(corr.get("old_cap")) is None:
        return computed, None, False
    old_scope = corr["old_cap"] < 40e9
    if old_scope == computed:
        return computed, None, False
    rewrite_to = computed if bool(j_scope) == old_scope else None
    final = computed if rewrite_to is not None else bool(j_scope)
    return computed, rewrite_to, final == computed


def rewrite_judgment_scope(jpath, value):
    """Set judgment.json in_scope_under_40b to `value`, changing only that
    token when it appears exactly once (the files are compact or indented,
    raw UTF-8 or \\u-escaped — the diff stays one token); otherwise re-dump in
    the file's own style. The result is re-parsed and must equal the original
    with only that field changed, or nothing is written."""
    with open(jpath, encoding="utf-8", newline="") as f:
        raw = f.read()
    orig = json.loads(raw)
    want = dict(orig, in_scope_under_40b=bool(value))
    pat = re.compile(r'("in_scope_under_40b"\s*:\s*)(true|false)')
    tok = "true" if value else "false"
    if len(pat.findall(raw)) == 1:
        out = pat.sub(lambda m: m.group(1) + tok, raw)
    else:
        indented = raw.lstrip().startswith("{\n") or raw.lstrip().startswith("{\r\n")
        out = json.dumps(want, indent=1 if indented else None, separators=None if indented else (",", ":"),
                         ensure_ascii=not any(ord(c) > 127 for c in raw))
        if raw.endswith("\n"):
            out += "\n"
    if json.loads(out) != want:
        fail("internal: the in_scope_under_40b rewrite of judgment.json did not round-trip — nothing written")
    tmp = jpath + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        f.write(out)
    os.replace(tmp, jpath)


def _impact_from_run(n):
    """The with-override side and the basis label, read from the run itself —
    the same label compute_override_impact gives: "payable_5y" for a run pinned
    to the insurer payable-earnings base (payable_base recorded, or
    base_pin_source judgment_base_override — M3: it read "ttm"), "ttm" for any
    other pin, else "median_3y"."""
    base_with = n.get("base_oe_per_share")
    irr_with = n.get("implied_irr_weighted")
    base_src = (n.get("base_source") or "").lower()
    inp = n.get("inputs") or {}
    pinned = inp.get("base_oe_ps_arg") is not None or "ttm" in base_src
    gaps = list(n.get("data_gap") or [])
    unblocks = bool(gaps) and not (n.get("data_gap_uncovered") or [])
    base_used = "payable_5y" if (n.get("payable_base") or inp.get("base_pin_source") == "judgment_base_override") \
        else "ttm" if pinned else "median_3y"
    return base_with, irr_with, base_used, unblocks


def _not_measured_note(rel):
    """The "not measured" note of a release-mismatch impact block."""
    if release_mismatch_reason(rel).startswith("engine output predates"):
        return f"not measured: engine output predates release {ENGINE_RELEASE}; re-run the engine to measure"
    return f"not measured: engine output is from release {rel}, not {ENGINE_RELEASE}; re-run the engine to measure"


def carried_override_impact(n, prior):
    """DESIGN §8.2 — release mismatch: no counterfactual replay. The prior
    score.json override_impact when it was measured on THIS run's base (its
    with-override base and weighted IRR equal the run's at the 4 dp the block
    stores) and is itself a measurement, plus impact_carried_from_prior_score /
    counterfactual_engine_release; otherwise the impact fields null with a note.
    unblocks_tier is always computed from the run, as before.
    [ADDITION — verifier round 2] a prior block carrying a "not measured" note
    is never carried (carried_payable_impact's rule): the second make_score run
    over the same stale record wrote impact_carried_from_prior_score: true
    beside that note and null measured fields."""
    base_with, irr_with, base_used, unblocks = _impact_from_run(n)
    rel = n.get("engine_release")
    r4 = lambda v: round(v, 4) if isinstance(v, (int, float)) else None  # noqa: E731
    blk = prior.get("override_impact") if isinstance(prior, dict) else None
    if (isinstance(blk, dict) and not blk.get("note") and blk.get("base_oe_with_override") == r4(base_with)
            and blk.get("weighted_irr_with_override") == r4(irr_with)):
        out = dict(blk)
        out.update({"unblocks_tier": unblocks, "impact_carried_from_prior_score": True,
                    "counterfactual_engine_release": rel})
        return out
    return {"base_used": base_used,
            "base_oe_without_override": None,
            "base_oe_with_override": r4(base_with),
            "base_oe_impact_pct": None,
            "weighted_irr_without_override": None,
            "weighted_irr_with_override": r4(irr_with),
            "weighted_irr_impact_pp": None,
            "unblocks_tier": unblocks,
            "counterfactual_engine_release": rel,
            "note": _not_measured_note(rel)}


PAYABLE_IMPACT_KEYS = ("base_used", "base_oe_without_override", "base_oe_with_override", "base_oe_impact_pct",
                       "weighted_irr_without_override", "weighted_irr_with_override", "weighted_irr_impact_pp",
                       "tier_by_numbers_without_override", "tier_by_numbers_with_override")


def prior_payable_event(ticker):
    """This ticker's base_override registry event from the previous make_score
    run (the payable impact lives only there), read before anything is
    written; None when absent or the registry does not exist yet. [Codex review r26 of PR #47] An unreadable or
    malformed registry is refused (load_registry), never read as no prior event."""
    reg = load_registry()
    for e in reg["entries"] if reg is not None else []:
        if e.get("ticker") == ticker and e.get("event") == "base_override":
            return e
    return None


def carried_payable_impact(n, prior):
    """[ADDITION — M3] DESIGN §8.2 applied to the payable-earnings pin: under a
    release mismatch payable_pin_impact is never run (the current engine's
    native-base replay would measure another capex / SBC basis). The prior
    base_override registry event's impact when it was measured on THIS run's
    pinned base and weighted IRR (4 dp) and is itself a measurement (no
    "not measured" note), plus impact_carried_from_prior_score /
    counterfactual_engine_release; otherwise the impact fields null with the
    "not measured" note."""
    rel = n.get("engine_release")
    r4 = lambda v: round(v, 4) if isinstance(v, (int, float)) and not isinstance(v, bool) else None  # noqa: E731
    bp, ip = r4(n.get("base_oe_per_share")), r4(n.get("implied_irr_weighted"))
    if (isinstance(prior, dict) and prior.get("base_used") == "payable_5y" and not prior.get("note")
            and prior.get("base_oe_with_override") == bp and prior.get("weighted_irr_with_override") == ip):
        out = {k: prior.get(k) for k in PAYABLE_IMPACT_KEYS}
        out.update({"impact_carried_from_prior_score": True, "counterfactual_engine_release": rel})
        return out
    return {"base_used": "payable_5y",
            "base_oe_without_override": None,
            "base_oe_with_override": bp,
            "base_oe_impact_pct": None,
            "weighted_irr_without_override": None,
            "weighted_irr_with_override": ip,
            "weighted_irr_impact_pp": None,
            "tier_by_numbers_without_override": None,
            "tier_by_numbers_with_override": n.get("tier_by_numbers"),
            "counterfactual_engine_release": rel,
            "note": _not_measured_note(rel)}


def check_override_currency_sync(j_over, applied, n):
    """A USD declaration the engine run did not honour refuses (out of sync):
    a pre-5.5 engine FX-converted every override at a converted filer, and a
    5.5 run that recorded currency_basis "converted" did the same."""
    fx = n.get("fx_conversion")
    for field, o in j_over.items():
        if o.get("currency") is None or field not in applied or not fx:
            continue
        basis = ((n.get("override_checks") or {}).get(field) or {}).get("currency_basis")
        if predates_55(n) or basis == "converted":
            fail(f"judgment.json {field}_override declares currency \"USD\" but the engine run FX-converted it "
                 f"(engine_release {n.get('engine_release')!r}, currency_basis {basis!r}) — rerun dcf_engine.py "
                 f"(release {ENGINE_RELEASE} uses a declared USD filing figure verbatim) before scoring")


SUPERSEDED_CAPEX_FLAG = "OVERRIDE_SUPERSEDED_BY_FILED_TAG:capex"


def _flag_present(n, prefix):
    return any(isinstance(f, str) and f.startswith(prefix) for f in (n.get("fragility_flags") or []))


def refuse_superseded_capex_override(n, j_over):
    """[ADDITION — WY] The engine flagged OVERRIDE_SUPERSEDED_BY_FILED_TAG:capex (a capex figure is now FILED for a
    last-3-FY period the override used to fill, outside 0.5x-2x of it; or override_checks.capex.superseded_periods
    says so) and judgment.json still declares capex_override: refuse. A filed value always wins, so the override
    silently stopped setting capex there; the worker must say which figure is the cash-flow total. The engine's
    behaviour is unchanged."""
    if "capex" not in j_over:
        return
    sup = ((n.get("override_checks") or {}).get("capex") or {}).get("superseded_periods") or []
    if not _flag_present(n, SUPERSEDED_CAPEX_FLAG) and not sup:
        return
    parts = []
    for x in (sup if isinstance(sup, list) else []):
        if not isinstance(x, dict):
            continue
        fy, v, tags = str(x.get("period") or "")[:4], _num(x.get("filed_ppe")), x.get("filed_tags") or "tag n/a"
        parts.append(f"FY{fy} {v:,.0f} {x.get('filed_unit') or ''} ({tags})".replace("  ", " ") if v is not None
                     else f"FY{fy} ({tags})")
    filed = ", ".join(parts) if parts else "one or more of the last 3 fiscal years (the flag names them)"
    cov = (" CAPEX_COVERAGE_LOW also fires on this run (capex under half of D&A in each of the last 3 FY) — the "
           "signature of a partial line." if _flag_present(n, "CAPEX_COVERAGE_LOW") else "")
    fail(f"{SUPERSEDED_CAPEX_FLAG} — judgment.json still declares capex_override {j_over['capex']['value']:,.0f}, but "
         f"engine release {n.get('engine_release')} now reads a FILED capex figure for {filed}; an override never "
         "replaces a filed value, so it fills nothing there and the filed figure sets owner's earnings. Resolve before "
         "scoring: (i) if the newly filed figure IS the filer's capex line on the cash-flow statement (the RBC / CR / IT "
         "case — release 5.5 now reads PaymentsForCapitalImprovements and the summed components), remove capex_override "
         "from judgment.json and re-run the engine; (ii) if the filed tag is only PART of capex (WY: "
         "PaymentsForCapitalImprovements 57M / 52M / 51M against a 447M cash-flow total, with CAPEX_COVERAGE_LOW firing "
         "too), block the company NEEDS_MAIN_AGENT: capex via queue.py — an override cannot lift a filed partial figure, "
         "so no tier is possible until the engine reads the full capex line." + cov)


def refuse_last_filed_unit_usd_override(n, j_over, applied):
    """[ADDITION — HTHT] An APPLIED override the engine used verbatim under currency_basis 'last_filed_unit_usd'
    (decision 7's fallback, kept exactly as ruled in the engine) is refused unless it is a kind "filing" override with
    an explicit currency "USD" — the fallback cannot tell a US-dollar figure from a local-currency one (HTHT: RMB 828M
    used as $828M). The engine records that basis only at a filer it FX-converted (fx_conversion exists only for a
    non-USD reporting currency), so this covers every use of the fallback; there is no separate currency precondition.
    A kind "estimate" override is refused too (main agent, closing verifier round 2's follow-up (10)): ruling 7 lets
    only a filing override declare currency, and the 0.1x-10x band admits a CNY figure at ~7.2x, so an estimate at such
    a filer has no way to show its unit — the worker uses the filing's own US-dollar figure (kind filing, currency
    "USD") or blocks NEEDS_MAIN_AGENT. No recorded folder has an estimate under this basis (FMS and SUZ estimates
    convert normally)."""
    ccy = str((n.get("fx_conversion") or {}).get("from_currency") or "").strip().upper() or "a non-USD currency"
    checks = n.get("override_checks") or {}
    for field, o in j_over.items():
        if field not in applied or (checks.get(field) or {}).get("currency_basis") != "last_filed_unit_usd":
            continue
        if o.get("kind") == "estimate":
            fail(f"judgment.json {field}_override {o['value']:,.0f} (kind estimate): the engine used this estimate "
                 f"verbatim as US dollars because the last filed unit for {field} is USD (override_checks.{field}."
                 f"currency_basis 'last_filed_unit_usd'), but this filer reports or historically filed in {ccy} and "
                 "nothing can show the estimate's unit (ruling 7 lets only a kind filing override declare currency; "
                 "the 0.1x-10x band admits a local-currency figure). Use the filing's own US-dollar figure as a kind "
                 f"filing override with currency: \"USD\", or block NEEDS_MAIN_AGENT: {field} via queue.py")
        if str(o.get("currency") or "").strip().upper() == "USD":
            continue
        fail(f"judgment.json {field}_override {o['value']:,.0f}: the engine used this override verbatim as US dollars "
             f"because the last filed unit for {field} is USD (override_checks.{field}.currency_basis "
             f"'last_filed_unit_usd'), but this filer reports or historically filed in {ccy} "
             "(fx_conversion.from_currency) and the override declares no currency. If the source states the figure in "
             "US dollars, declare currency: \"USD\" on the override (kind filing) and re-run the engine; if it is in "
             f"{ccy}, it cannot be used as is — restate it (the filing's own US-dollar figure, declared currency "
             f"\"USD\") or block NEEDS_MAIN_AGENT: {field} via queue.py")


# ---------------------------------------------------------------------------
# v5.7 lane L9 (R8 / R9 capex, Andrew 2026-10-19) — L0 placeholders, no-ops until L9 fills them
# ---------------------------------------------------------------------------
def refuse_capex_override_software(n, j_over, tt=None):
    """v5.7 placeholder (L9, R9): a capex_override beside capitalized software the 5.7 engine now adds (its
    software_included declaration and value test; tt is the current ttm.json for the TTM legs). No-op in L0."""
    return None


def refuse_unlisted_capex_component(n, j):
    """v5.7 placeholder (L9, R8): a CAPEX_UNLISTED_COMPONENT flag not released by judgment.json capex_unlisted_ack.
    No-op in L0."""
    return None


def refuse_pre57_ttm_json(n, tt):
    """v5.7 placeholder (L9, R8 / R9 TTM provenance): a 5.7 run whose basis read a ttm.json built before engine 5.7
    (ttm_inputs.ttm_engine_release). No-op in L0."""
    return None


def validate_base_override(j):
    """judgment.json base_override {value, source, reason} — the declared
    provenance for a base pin that did NOT come from ttm.json. None if absent."""
    o = j.get("base_override")
    if o is None:
        return None
    if not isinstance(o, dict):
        fail("judgment.json: base_override must be an object {value, source, reason}")
    if not isinstance(o.get("value"), (int, float)) or isinstance(o.get("value"), bool):
        fail("judgment.json: base_override.value must be a number")
    if not str(o.get("source") or "").strip():
        fail("judgment.json: base_override.source must be a non-empty string")
    if not str(o.get("reason") or "").strip():
        fail("judgment.json: base_override.reason must be a non-empty string")
    if "basis_window" in o:
        # [Codex review r15 of PR #47] the window a plain pin was built on (dcf_engine.base_basis_window_problem); an
        # iprd_amortized declaration names its native_base and a payable one is five FY figures, so neither takes it
        if o.get("basis") is not None:
            fail("judgment.json: base_override.basis_window applies to a plain base_override only (an iprd_amortized "
                 "one names native_base; a payable one is five annual figures)")
        why = _engine.base_basis_window_problem(o["basis_window"])
        if why:
            fail(f"judgment.json: base_override.{why}")
    if o.get("basis") == IPRD_AMORTIZED_BASIS:
        # v5.6 (acquired IPR&D; a main-agent addition awaiting Andrew's ratification): the amortized
        # maintenance-acquisition base, pinned through --base-oe-ps; the engine
        # recomputes it and check_iprd_amortized compares the record.
        if o.get("kind") != "filing":
            fail("judgment.json: an iprd_amortized base_override must have kind 'filing' (its figures are the filed charges)")
        figs = o.get("figures")
        # one figure per FY of the engine's last-3-FY window: three, or two at a filer with only two FY (the
        # engine's record holds the window; check_iprd_amortized compares the two figure for figure)
        if not (isinstance(figs, list) and len(figs) in (2, 3)
                and all(isinstance(x, (int, float)) and not isinstance(x, bool) and x >= 0 for x in figs)):
            fail("judgment.json: an iprd_amortized base_override.figures must list the last-3-FY window's acquired-IPR&D "
                 "charges (one non-negative dollar figure per FY — three, or two at a filer with only two FY — oldest "
                 "first, from dcf_numbers.json iprd_adjustment)")
        if not isinstance(o.get("shares"), (int, float)) or isinstance(o.get("shares"), bool) or o["shares"] <= 0:
            fail("judgment.json: an iprd_amortized base_override.shares must be a positive share count")
        if o.get("native_base") not in IPRD_NATIVE_BASES:
            fail(f"judgment.json: an iprd_amortized base_override.native_base must be one of {list(IPRD_NATIVE_BASES)}")
        return o
    if o.get("basis") is not None:
        # Insurer payable-earnings base (2026-10-19): the engine reads this
        # shape via --base-judgment; make_score checks it reproduces.
        if o.get("basis") != PAYABLE_BASIS:
            fail(f"judgment.json: base_override.basis must be {PAYABLE_BASIS!r} or {IPRD_AMORTIZED_BASIS!r} when set")
        if o.get("kind") != "filing":
            fail("judgment.json: a payable-earnings base_override must have kind 'filing'")
        figs = o.get("figures")
        if not (isinstance(figs, list) and len(figs) == 5
                and all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in figs)):
            fail("judgment.json: base_override.figures must list exactly five annual figures")
        if not isinstance(o.get("shares"), (int, float)) or isinstance(o.get("shares"), bool) or o["shares"] <= 0:
            fail("judgment.json: base_override.shares must be a positive share count")
        per_ord = sum(float(x) for x in figs) / 5.0 / float(o["shares"])
        if abs(per_ord - float(o["value"])) > 0.005:
            fail(f"judgment.json: base_override.value {o['value']} does not reproduce from figures/shares ({per_ord:.6f}) to the cent")
    return o


def _figures_agree(recorded, declared):
    """[v5.6 review] The engine's own figure tolerance for an iprd_amortized declaration: the same count, each
    within $1 (an FX-converted charge is a float such as value x rate; a dollar-rounded declaration the engine
    accepted must not be refused here)."""
    if not (isinstance(recorded, list) and isinstance(declared, list) and len(recorded) == len(declared)):
        return False
    try:
        return all(abs(float(a) - float(b)) <= 1.0 for a, b in zip(declared, recorded))
    except (TypeError, ValueError):
        return False


def _iprd_amortized_ttm(n):
    """[v5.6 review] The engine's amortized record when the run carries the acquired-IPR&D charge in a base whose
    native base is ttm.json's TTM figure (treatment amortized_in_base, native_base ttm_json), else None. The score's
    base is then the TTM base less the amortization, so the PR #31 TTM-leg rules still apply to it."""
    blk = n.get("iprd_adjustment") if isinstance(n.get("iprd_adjustment"), dict) else None
    am = (blk or {}).get("amortized")
    if (blk and blk.get("treatment") == "amortized_in_base" and isinstance(am, dict)
            and am.get("native_base") == "ttm_json" and _num(am.get("native_base_per_share")) is not None
            and _num(am.get("pinned_per_share")) is not None):
        return am
    return None


def _iprd_hold(n):
    """[v5.6 review] DCF_IPRD_HOLD for an override-impact counterfactual: the final run's IPR&D treatment and charge
    per share (0.0 unless it took the one-time deduction), so the replay toggles the field overrides only."""
    blk = n.get("iprd_adjustment") if isinstance(n.get("iprd_adjustment"), dict) else None
    return json.dumps({"treatment": (blk or {}).get("treatment") or "none",
                       "charge_per_share": _engine.iprd_charge_per_share(n)})


def validate_iprd_cash_flow_check(j):
    """[fixer review round] judgment.json iprd_cash_flow_check: a list of
    {period, window, amount, presentation, source} (dcf_engine's rule), one
    entry per (period, window). None when absent; refuses anything else."""
    v = j.get(IPRD_CF_CHECK_KEY)
    if v is None:
        return None
    shape = ("{period: 'YYYY-MM-DD', window: 'fy' | 'ttm_current_ytd', amount: the period's filed expense (> 0), "
             f"presentation: one of {sorted(_engine.IPRD_CF_PRESENTATIONS)}, source: the filing and the cash-flow line, "
             "optional unit: the amount's unit (required, as the expense's own unit, for an expense filed with no FX "
             "rate)}")
    if not isinstance(v, list) or not v:
        fail(f"judgment.json: {IPRD_CF_CHECK_KEY} must be a non-empty list of {shape}")
    seen = set()
    for e in v:
        if not _engine.iprd_cash_flow_check_entry_ok(e):
            fail(f"judgment.json: {IPRD_CF_CHECK_KEY} entry {e!r} is malformed — each entry is {shape}")
        k = (e["period"], e["window"])
        if k in seen:
            fail(f"judgment.json: {IPRD_CF_CHECK_KEY} names {k[1]} {k[0]} twice")
        seen.add(k)
    return v


def _filed_expense_txt(p):
    """[Codex review r21 of PR #47] A period's filed expense for a refusal: the USD figure, else (no FX rate) the
    native figure with its unit and the `unit` a matching check names — before, a dash the worker could not match."""
    nat = p.get("expense_native")
    if p.get("expense") is None and isinstance(nat, (int, float)) and not isinstance(nat, bool):
        return (f"{nat:,.0f} {p.get('expense_unit')} (no FX rate: declare amount {nat:,.0f} with unit "
                f"\"{p.get('expense_unit')}\")")
    return _usd_exact(p.get("expense"))


def check_iprd_cash_flow(n, entries):
    """[fixer review round] The cash-flow checks and the engine record must
    agree, and no expense-basis period may still await one: the run's value
    is unknown until the worker declares what the 10-K's cash-flow statement
    shows (WORKER_SPEC step 3, ACQUIRED_IPRD_UNCONFIRMED). [Codex review r14
    of PR #47] Nor may any window period carry a declared check the run did
    not apply (cash_flow_check_mismatch: its amount is not the filed expense)."""
    blk = n.get("iprd_adjustment") if isinstance(n.get("iprd_adjustment"), dict) else None
    periods = [p for p in (blk or {}).get("periods") or [] if isinstance(p, dict)]
    lbl = lambda p: (f"FY{p['period'][:4]}" if p.get("window") == "fy" else f"YTD to {p.get('period')}")
    aw = [p for p in periods if p.get("excluded") == _engine.IPRD_AWAITING]
    if aw:
        fail("ACQUIRED_IPRD_UNCONFIRMED: acquired IPR&D expensed with no us-gaap investing cash tag in "
             + ", ".join(f"{lbl(p)} {_usd_exact(p.get('awaiting'))}" for p in aw)
             + " — companyfacts cannot show whether the 10-K's cash-flow statement added it back in operating "
             "activities and paid it in investing (deducted: HALO) or left it inside operating cash flow (not "
             f"deducted: NBIX). Read the cash-flow statement, declare judgment.json {IPRD_CF_CHECK_KEY} for each period "
             "(period, window, amount, presentation, source citing the line — WORKER_SPEC step 3) and rerun the engine"
             + ("; a declared check whose amount is not the filed expense was not applied ("
                + ", ".join(f"{lbl(p)} declared {_usd_exact((p.get('cash_flow_check_mismatch') or {}).get('declared_amount'))}"
                            for p in aw if p.get("cash_flow_check_mismatch")) + ")"
                if any(p.get("cash_flow_check_mismatch") for p in aw) else ""))
    # [Codex review r14 of PR #47] a declared check the run did not apply on a period it evaluated is refused on any
    # basis, not only on an awaiting period: a cash-basis period's mistyped paid_in_shares check was dropped, its
    # residual accrued as unpaid and a later unrelated cash payment deducted against it. A check for a period outside
    # the window has no record here and still carries over across re-scores (round 2).
    mm = [p for p in periods if p.get("cash_flow_check_mismatch") and p.get("excluded") != _engine.IPRD_AWAITING]
    if mm:
        fail(f"judgment.json {IPRD_CF_CHECK_KEY} names a period of this run's window with an amount that is not the "
             "filed acquired-IPR&D expense, so the run did not apply it: "
             + ", ".join(f"{lbl(p)} declared {_usd_exact((p.get('cash_flow_check_mismatch') or {}).get('declared_amount'))}"
                         + (f" {(p.get('cash_flow_check_mismatch') or {}).get('declared_unit')}"
                            if (p.get('cash_flow_check_mismatch') or {}).get('declared_unit') else "")
                         + f", filed expense {_filed_expense_txt(p)}" for p in mm)
             + " — declare the amount as the filed expense (within $1; [Codex review r21 of PR #47] an expense filed "
             "with no FX rate is declared in its own unit, with that `unit`) and rerun the engine, or remove the "
             "entry if the period needs no check (WORKER_SPEC step 3)")
    # [Codex review r15 of PR #47] a cash-basis period deducts its cash outflow; a matching check whose presentation
    # says OE already carried the payment (inside OCF, inside the capex intangible leg) contradicts the deduction and
    # was consumed with no trace — refused, naming the presentation
    ia = [p for p in periods if isinstance(p.get("cash_flow_check_inapplicable"), dict)]
    if ia:
        fail(f"judgment.json {IPRD_CF_CHECK_KEY} declares, for a cash-basis period of this run's window (the us-gaap "
             "investing cash tag is filed and its outflow deducted), a presentation the cash-basis path cannot honor "
             "(cash_flow_check_inapplicable): "
             + ", ".join(f"{lbl(p)} presentation {p['cash_flow_check_inapplicable'].get('presentation')} "
                         f"({_usd_exact(p['cash_flow_check_inapplicable'].get('amount'))})" for p in ia)
             + " — the investing cash tag contradicts a payment inside operating cash flow or inside the capex "
             "intangible leg: remove the entry (a cash-basis period needs no check for its own deduction; "
             "paid_in_shares is the one presentation it reads), or reconcile it with the filing's cash-flow "
             "statement, and rerun the engine (WORKER_SPEC step 3)")
    by = {(e["period"], e["window"]): e for e in entries or []}
    for p in periods:
        k = (p.get("period"), p.get("window"))
        applied = p.get("cash_flow_check") if isinstance(p.get("cash_flow_check"), dict) else None
        d = by.get(k)
        if applied is not None:
            if (d is None or d.get("presentation") != applied.get("presentation")
                    or not isinstance(applied.get("amount"), (int, float)) or abs(float(d["amount"]) - float(applied["amount"])) > 1.0
                    or str(d.get("source")) != str(applied.get("source"))
                    or d.get("unit") != applied.get("unit")):   # [Codex review r21 of PR #47]
                fail(f"dcf_numbers.json applied an {IPRD_CF_CHECK_KEY} for {lbl(p)} ({applied.get('presentation')}, "
                     f"{_usd_exact(applied.get('amount'))}) that judgment.json "
                     + ("no longer declares" if d is None else "now declares differently")
                     + " — the judgment file and the engine run are out of sync; rerun the engine")


def validate_iprd_deferred_payment(j):
    """Andrew's 2026-10-20 ruling (delegated to the main agent): judgment.json
    iprd_deferred_payment — a list of {period, window "fy", amount,
    deferred_payment_of: {deal, first_charged_period, source,
    contingent_total: {value, source}}} (dcf_engine's rule), one entry per
    period and deal (distinct deals may share a period), one contingent_total
    per deal declared consistently and not exceeded by the deal's declared
    amounts summed across the entries (the per-deal cap). None when absent;
    refuses anything else. The window checks (one first
    charge per deal, first charge before the period and not itself wholly an
    installment, the original filing's years, companyfacts before the
    window, amounts within the charge) are the engine's:
    check_iprd_deferred_payment compares its record."""
    v = j.get(IPRD_DEFERRED_KEY)
    if v is None:
        return None
    shape = ("{period: 'YYYY-MM-DD' (an FY end), window: 'fy' (a current-YTD charge never counts toward recurrence: "
             "declare it once it lands in an FY), amount: this deal's deferred part of the period's charge (> 0), "
             "deferred_payment_of: {deal, first_charged_period: 'YYYY-MM-DD', source: the original acquisition filing's "
             "accession (0001234567-YY-NNNNNN) and the section / page showing the contingent milestone or deferred "
             "consideration, contingent_total: {value: the deal's unrecognized milestones / deferred consideration in "
             "USD (> 0), source: accession + section / page disclosing it} — declared once, the same on every entry of "
             "the deal}}")
    if not isinstance(v, list) or not v:
        fail(f"judgment.json: {IPRD_DEFERRED_KEY} must be a non-empty list of {shape}")
    seen = set()
    for e in v:
        if not _engine.iprd_deferred_entry_ok(e):
            fail(f"judgment.json: {IPRD_DEFERRED_KEY} entry {e!r} is malformed — each entry is {shape}")
        k = (e["period"], _engine._deal_key(e["deferred_payment_of"]["deal"]))
        if k in seen:
            fail(f"judgment.json: {IPRD_DEFERRED_KEY} names FY {k[0]} a deferred payment of "
                 f"{e['deferred_payment_of']['deal']!r} twice")
        seen.add(k)
    for reason in _engine.iprd_deferred_cap_problems(v).values():
        fail(f"judgment.json: {IPRD_DEFERRED_KEY}: {reason}")
    return v


def check_iprd_deferred_payment(n, entries):
    """The declared deferred payments and the engine record must agree: every
    declaration applied (the engine refuses one its window does not support,
    so an unapplied one means judgment.json changed after the run), every
    applied one still declared, and declared the same way."""
    blk = n.get("iprd_adjustment") if isinstance(n.get("iprd_adjustment"), dict) else None
    periods = [p for p in (blk or {}).get("periods") or [] if isinstance(p, dict)]
    lbl = lambda k: f"FY{k[0][:4]}"
    applied = {(p.get("period"), p.get("window"), _engine._deal_key(a.get("deal"))): a for p in periods
               if isinstance(p.get("deferred_payment_of"), list)
               for a in p["deferred_payment_of"] if isinstance(a, dict)}
    by = {(e["period"], e["window"], _engine._deal_key(e["deferred_payment_of"]["deal"])): e for e in entries or []}
    rolled = {(e.get("period"), e.get("window"), _engine._deal_key((e.get("deferred_payment_of") or {}).get("deal"))): e
              for e in (blk or {}).get("deferred_payments_rolled_out") or [] if isinstance(e, dict)}
    for k, a in applied.items():
        d = by.get(k)
        dd = (d or {}).get("deferred_payment_of") or {}
        if (d is None or dd.get("deal") != a.get("deal") or dd.get("first_charged_period") != a.get("first_charged_period")
                or str(dd.get("source")) != str(a.get("source"))
                or dd.get("contingent_total") != a.get("contingent_total")
                or not isinstance(a.get("amount"), (int, float)) or abs(float(d["amount"]) - float(a["amount"])) > 1.0):
            fail(f"dcf_numbers.json applied an {IPRD_DEFERRED_KEY} for {lbl(k)} ({a.get('deal')!r}, first charged "
                 f"{a.get('first_charged_period')}, {_usd_exact(a.get('amount'))}) that judgment.json "
                 + ("no longer declares" if d is None else "now declares differently")
                 + " — the judgment file and the engine run are out of sync; rerun the engine")
    for k, e in rolled.items():
        # [Codex review r4 of PR #47] a rolled-out entry stays declared: its payment counts toward the deal's
        # lifetime contingent_total cap, which a deleted entry would no longer bound
        d = by.get(k)
        if d is None or d != e:
            fail(f"dcf_numbers.json counted a rolled-out {IPRD_DEFERRED_KEY} for {lbl(k)} "
                 f"({(e.get('deferred_payment_of') or {}).get('deal')!r}, {_usd_exact(e.get('amount'))}) toward its "
                 "deal's contingent_total that judgment.json "
                 + ("no longer declares" if d is None else "now declares differently")
                 + " — keep every rolled-out entry as declared (it bounds the deal's lifetime contingent_total cap); "
                 "the judgment file and the engine run are out of sync: restore it, or rerun the engine")
    if rolled:
        # [Codex review r9 of PR #47] a rolled-out period must be a fiscal-year end of this filer: re-checked with the
        # engine's helper against the FY ends the run recorded, so a quarter end never counts toward a deal's cap
        fy = (blk or {}).get("fy_period_ends")
        if not (isinstance(fy, list) and fy and all(isinstance(x, str) for x in fy)):
            fail(f"dcf_numbers.json lists rolled-out {IPRD_DEFERRED_KEY} entries but records no fy_period_ends (the "
                 "filer's fiscal-year ends a rolled-out period must be one of: an engine run that predates Codex "
                 "review round 9 of PR #47) — rerun the engine")
        for k, e in rolled.items():
            why = _engine.iprd_fy_end_problem(e.get("period"), fy)
            if why is not None:
                fail(f"dcf_numbers.json counted a rolled-out {IPRD_DEFERRED_KEY} for "
                     f"{(e.get('deferred_payment_of') or {}).get('deal')!r} toward its deal's contingent_total, but "
                     f"{why} — fix the entry's period in judgment.json and rerun the engine")
    for k, d in by.items():
        if k in rolled:
            continue
        if k not in applied:
            fail(f"judgment.json {IPRD_DEFERRED_KEY} declares {lbl(k)} a deferred payment of "
                 f"{d['deferred_payment_of']['deal']!r} but the engine run did not apply it — judgment.json changed "
                 "after the run; rerun the engine (it refuses a declaration its window does not support: "
                 "BAD_IPRD_DEFERRED_PAYMENT)")


IPRD_JUDGMENT_CHANGED = ("judgment.json changed after the engine run — rerun dcf_engine.py (its acquired-IPR&D "
                         "inputs: iprd_cash_flow_check, iprd_deferred_payment, base_override basis / basis_window / "
                         "iprd_amortized value, native_base, figures, shares — WORKER_SPEC step 3)")


def check_iprd_judgment_current(n, j):
    """[Codex review r22 of PR #47] judgment.json's acquired-IPR&D inputs must be the ones the engine run read. The
    other checks compare one way only (what the run applied must still be declared), so an input added after the run
    that leaves no trace scored the stale run: a paid_in_shares check added for a cash-basis period (FY2024 $100M
    expense, $40M cash; FY2025 $60M cash only) — the stale run deducts $100M, a rerun $40M; an
    inside_operating_cash_flow one, which a rerun records cash_flow_check_inapplicable (refused).
    A run that records iprd_judgment_hash (the engine's iprd_judgment_hash of the judgment.json it read) is refused
    when the current judgment.json hashes differently. A record that predates the hash (HALO's committed 5.6.0
    record, anything older) falls back to a per-declaration rule: every iprd_cash_flow_check naming a period the run
    evaluated (a period record of its window) must show on it as applied (cash_flow_check), mismatched or
    inapplicable, or be listed in cash_flow_checks_unused; a check for a period the run has no record of still
    carries over (round 2)."""
    blk = n.get("iprd_adjustment") if isinstance(n.get("iprd_adjustment"), dict) else None
    periods = {(p.get("period"), p.get("window")): p for p in (blk or {}).get("periods") or [] if isinstance(p, dict)}
    unused = [_engine._iprd_canon(e) for e in (blk or {}).get("cash_flow_checks_unused") or [] if isinstance(e, dict)]
    untraced = []
    for e in validate_iprd_cash_flow_check(j) or []:
        p = periods.get((e["period"], e["window"]))
        if p is None:
            continue
        if (isinstance(p.get("cash_flow_check"), dict) or p.get("cash_flow_check_mismatch")
                or isinstance(p.get("cash_flow_check_inapplicable"), dict) or _engine._iprd_canon(e) in unused):
            continue
        untraced.append(e)
    named = (f"judgment.json {IPRD_CF_CHECK_KEY} declares "
             + ", ".join(f"{'FY' + e['period'][:4] if e['window'] == 'fy' else 'YTD to ' + e['period']} "
                         f"({e['presentation']}, {_usd_exact(e['amount'])})" for e in untraced)
             + ", a period this run evaluated, but the run shows no trace of reading it (not applied, mismatched, "
             "inapplicable or unused): it was added after the run") if untraced else None
    rec = n.get("iprd_judgment_hash")
    if rec is not None:
        now = _engine.iprd_judgment_hash(j)
        if rec != now:
            fail(f"{IPRD_JUDGMENT_CHANGED}: dcf_numbers.json records iprd_judgment_hash {str(rec)[:12]}…, the current "
                 f"judgment.json hashes to {now[:12]}…" + (f"; {named}" if named else ""))
        return
    if named:
        fail(f"{IPRD_JUDGMENT_CHANGED}: {named}")


TTM_CHANGED = ("ttm.json changed after the engine run — rerun dcf_engine.py (the run read ttm.json's TTM base, "
               "share count, current-YTD period and input legs: regenerating ttm.json means rerunning the engine — "
               "WORKER_SPEC step 4)")


def _ttm_inputs_txt(r):
    r = r if isinstance(r, dict) else {}
    h = r.get("ttm_input_hash")
    return (f"ttm_oe_per_share {r.get('ttm_oe_per_share')}, ttm_shares_diluted {r.get('ttm_shares_diluted')}, "
            f"ytd_current_period {r.get('ytd_current_period')}, ttm_input_hash {str(h)[:12] + '…' if h else h}")


def check_ttm_inputs_current(n, tt):
    """[Codex review r23 of PR #47] ttm.json (object tt, None when absent or unreadable) must be the one the engine run
    read. The pin-provenance rule compares only the base with ttm_oe_per_share (within 0.1%), but a TTM-basis run also
    takes its IPR&D share denominator (ttm_shares_diluted) and current-YTD window (inputs.ocf.ytd_current_period)
    from ttm.json: regenerated after the run with twice the shares and twice the OE, the run's $0.50 charge on 100M
    shares scored where a rerun deducts $0.25 on 200M; a new 10-Q's YTD period scored the stale window.
    A run that records ttm_inputs (dcf_engine.ttm_inputs_record of the ttm.json it read) is refused when the current
    ttm.json gives anything else. [Codex review r25 of PR #47] The check follows the record: null — a median run, a
    --base-oe-ps pin declared built on FY figures (basis_window "fy", or iprd_amortized on the median native base
    outside STALE_FY), whose basis reads nothing from ttm.json — is held to nothing here (base pin provenance and
    check_base_basis_window still apply). A record that predates it
    (HALO's committed 5.6.0 record, anything older) whose positive IPR&D charge is on ttm.json's share count
    (shares_source "ttm.json ttm_shares_diluted") falls back to its own record: the current ttm_shares_diluted must
    equal shares_denominator (within one share) and, when the window names a current YTD, ytd_current_period must be
    it. Any other older record keeps the 0.1% base check alone."""
    if "ttm_inputs" in n:
        rec = n.get("ttm_inputs")
        if rec is None:
            return
        now = _engine.ttm_inputs_record(tt)
        if rec != now:
            fail(f"{TTM_CHANGED}: dcf_numbers.json records ttm_inputs {_ttm_inputs_txt(rec)}; the current ttm.json "
                 f"gives {_ttm_inputs_txt(now)}")
        return
    blk = n.get("iprd_adjustment") if isinstance(n.get("iprd_adjustment"), dict) else None
    if not blk or blk.get("shares_source") != "ttm.json ttm_shares_diluted":
        return
    cps, tot = _num(blk.get("charge_per_share")), _num(blk.get("total"))
    if not ((cps is not None and cps > 0) or (tot is not None and tot > 0)):
        return
    tt = tt if isinstance(tt, dict) else {}
    ts, sd = _num(tt.get("ttm_shares_diluted")), _num(blk.get("shares_denominator"))
    ins = tt.get("inputs") if isinstance(tt.get("inputs"), dict) else {}
    per = (ins.get("ocf") if isinstance(ins.get("ocf"), dict) else {}).get("ytd_current_period")
    win = (blk.get("window") or {}).get("ttm_current_ytd") if isinstance(blk.get("window"), dict) else None
    why = []
    if ts is None or sd is None or abs(ts - sd) >= 1.0:
        why.append(f"the run's acquired-IPR&D charge is on ttm.json's ttm_shares_diluted {sd} (iprd_adjustment."
                   f"shares_denominator) but ttm.json now holds {ts}")
    if isinstance(win, list) and per != win:
        why.append(f"the run's current-YTD window is {win} (iprd_adjustment.window.ttm_current_ytd) but ttm.json's "
                   f"inputs.ocf.ytd_current_period is now {per!r}")
    if why:
        fail(f"{TTM_CHANGED}: " + "; ".join(why))


IPRD_DEFERRED_EVENT = "iprd_deferred_payment"   # [Codex review r8 of PR #47] the registry event (one per deal)


REGISTRY_LOCK_WAIT = "make_score.py: waiting for the registry lock (another make_score run holds it)"


@contextlib.contextmanager
def registry_transaction():
    """[Codex review r19 of PR #47] ONE acquisition of the registry lock (_lock.locked on REGISTRY + ".lock") around
    main()'s whole write phase: the prior-registry read (registry_prior_entries), the lifetime validation and merge of
    the deal's deferred payments (iprd_deferred_lifetime), then — [Codex review r21 of PR #47] in this order — the
    registry replacement (update_registry, lock_held=True), the judgment.json scope rewrite, score.json
    (write_score_json) and key_numbers.md, each a tmp file plus _stable._replace. The registry goes first: a crash
    after it leaves the deal's periods recorded beside the previous score.json (not this run's, so no live figures),
    a crash before it leaves nothing changed; before, score.json came first, so a crash or a failed registry replace
    in between published a score whose deferred periods the registry never recorded, and deleting the declaration
    reopened the lifetime cap. Overlapping scorers serialize: before, the prior read and
    the cap check ran unlocked long before update_registry took the lock, so two runs of one ticker each saw $0 paid,
    each passed with a different $60M period against a $100M contingent_total, and the last writer left only its own
    $60M ($120M accepted, the cap open again). It says when it waits (REGISTRY_LOCK_WAIT, stderr) and refuses when
    the lock cannot be taken (its file cannot be opened)."""
    stack = contextlib.ExitStack()
    try:
        stack.enter_context(locked(REGISTRY + ".lock",
                                   on_wait=lambda: print(REGISTRY_LOCK_WAIT, file=sys.stderr, flush=True)))
    except OSError as ex:
        fail(f"cannot take the registry lock {REGISTRY}.lock ({type(ex).__name__}: {ex}) — the deferred-payment "
             f"lifetime record ({IPRD_DEFERRED_EVENT} events) is read, checked and replaced only under it, so nothing "
             "was written; fix the path or its permissions and rerun")
    with stack:
        yield


def _atomic_write(path, text):
    """[Codex review r21 of PR #47] Write text to path through a tmp file beside it and _stable._replace (retried on a
    Windows PermissionError): a crash mid-write leaves the previous file whole, never a truncated one. The tmp file
    is removed when the write or the replace fails."""
    tmp = path + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:   # text mode, as the plain writes it replaces
            f.write(text)
        _replace(tmp, path)
    except BaseException:
        try:
            os.remove(tmp)
        except OSError:
            pass
        raise


def write_score_json(spath, score):
    """[Codex review r21 of PR #47] score.json, atomically (_atomic_write), written by main() AFTER the registry: it is
    the run's commit marker — a score.json whose dcf_content_hash matches the run exists only once the registry
    already records the run's judgment events (the deals' deferred-payment periods among them)."""
    _atomic_write(spath, json.dumps(score, indent=1))


def _finite_pos(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) and v > 0


# [Codex review r28 of PR #47, re-verification] the fields only an iprd_deferred_payment registry event carries: an
# entry holding any of them is read as one (registry_entry_problem), whatever its `event` says
IPRD_DEFERRED_EVENT_KEYS = ("deal", "first_charged_period", "contingent_total", "paid_to_date", "periods")


def registry_deferred_event_problem(e, need_date=True):
    """[Codex review r28 of PR #47] (field, why) for the first field of a registry iprd_deferred_payment event that
    is missing or invalid, else None — every field iprd_deferred_lifetime, update_registry and keep_first_dates read,
    checked with the engine's own helpers: [re-verification] `event` exactly iprd_deferred_payment and no `field`
    key (the entry carries the event's fields: a misspelt or missing event name had passed as another entry);
    `ticker` (upper-case, as make_score's own, with no surrounding whitespace) and `deal` non-empty strings;
    `first_charged_period` a real YYYY-MM-DD date (dcf_engine.iprd_date_ok); `contingent_total` {value > 0,
    source: an accession + section} (dcf_engine.iprd_contingent_total_ok); `paid_to_date` a finite number > 0;
    `periods` a non-empty list of {period: a real date, amount: a finite number > 0}, no period twice; `date` a real
    date (need_date; the events make_score writes always carry it). A missing or non-string `deal` had been skipped silently, so the deal's
    recorded payments read as none — a new declaration passed as the first payment against the deal's cap, and the
    wholesale replace erased the event; a periods list of strings or a string paid_to_date read as $0 paid."""
    def got(k):
        return "missing" if k not in e else f"{e[k]!r}"
    if e.get("event") != IPRD_DEFERRED_EVENT or "field" in e:
        # [Codex review r28 of PR #47, re-verification] an entry carrying a deferred-payment event's fields under a
        # misspelt, missing or other event name (or as a field override) had passed as some other entry, so the
        # deal's recorded payments read as none and the wholesale replace erased them
        return "event", (f"is {got('event')}" + (f" beside field {e.get('field')!r}" if "field" in e else "")
                         + f", but the entry carries an {IPRD_DEFERRED_EVENT} event's fields "
                         f"({', '.join(k for k in IPRD_DEFERRED_EVENT_KEYS if k in e)})")
    t = e.get("ticker")
    if not (isinstance(t, str) and t.strip() and t == t.strip().upper()):
        # a ticker with surrounding whitespace is no folder's: every run would read the event as nobody's prior;
        # [Codex review r28 of PR #47, re-verification] nor is a lower-case one (make_score upper-cases its ticker)
        return "ticker", f"is {got('ticker')}, not a non-empty upper-case string without surrounding whitespace"
    d = e.get("deal")
    if not (isinstance(d, str) and d.strip()):
        return "deal", f"is {got('deal')}, not a non-empty string"
    if not _engine.iprd_date_ok(e.get("first_charged_period")):
        return "first_charged_period", f"is {got('first_charged_period')}, not a real YYYY-MM-DD date"
    if not _engine.iprd_contingent_total_ok(e.get("contingent_total")):
        return "contingent_total", (f"is {got('contingent_total')}, not {{value: USD > 0, source: an EDGAR "
                                    "accession + the section / page}")
    if not _finite_pos(e.get("paid_to_date")):
        return "paid_to_date", f"is {got('paid_to_date')}, not a finite number > 0"
    ps = e.get("periods")
    if not (isinstance(ps, list) and ps):
        return "periods", f"is {got('periods')}, not a non-empty list of {{period, amount}}"
    seen = set()
    for k, x in enumerate(ps):
        if not (isinstance(x, dict) and _engine.iprd_date_ok(x.get("period")) and _finite_pos(x.get("amount"))):
            return "periods", f"item {k} is {x!r}, not {{period: a real YYYY-MM-DD date, amount: a finite number > 0}}"
        if x["period"] in seen:
            return "periods", f"lists period {x['period']} twice"
        seen.add(x["period"])
    if (need_date or "date" in e) and not _engine.iprd_date_ok(e.get("date")):
        return "date", f"is {got('date')}, not a real YYYY-MM-DD date"
    return None


def load_registry():
    """[Codex review r26 of PR #47] The registry as every make_score reader and writer takes it: None when the file
    does not exist yet (the first run), else the parsed object — refused unless it is a JSON object whose `entries`
    is a list of objects. An unreadable file (r8) and a parseable one of another shape (a top-level list, `entries`
    missing, null, a dict or a string, a non-object entry) are refused alike, never defaulted to empty: a registry
    object without `entries` read as no prior events, so a recorded $60M paid_to_date counted $0 against the deal's
    contingent_total, and update_registry rewrote the file holding only this ticker's events — every other ticker's
    durable record erased. [Codex review r28 of PR #47] So is one holding a malformed iprd_deferred_payment event,
    whatever its ticker (registry_deferred_event_problem): the refusal names the entry's index, its ticker and the
    field. Every ticker's events are checked, since update_registry keeps the other tickers' entries as they are and
    their own runs read them. [Re-verification of round 28] Every entry goes through registry_entry_problem: an
    entry carrying a deferred-payment event's fields under a misspelt, missing or other event name, a lower-case
    deferred-payment ticker, and an entry that is neither a field override nor an event make_score writes are
    refused alike."""
    try:
        with open(REGISTRY, encoding="utf-8") as f:
            reg = json.load(f)
    except FileNotFoundError:
        return None
    except (OSError, ValueError) as ex:
        fail(f"{REGISTRY} is unreadable ({type(ex).__name__}: {ex}) — it carries the lifetime record of every deal's "
             f"declared deferred payments ({IPRD_DEFERRED_EVENT} events); restore it from git before scoring")
    ents = reg.get("entries") if isinstance(reg, dict) else None
    if not (isinstance(reg, dict) and isinstance(ents, list) and all(isinstance(e, dict) for e in ents)):
        why = ("not a JSON object" if not isinstance(reg, dict)
               else "no 'entries' key" if "entries" not in reg
               else f"'entries' is {type(ents).__name__}, not a list" if not isinstance(ents, list)
               else "an entry that is not an object")
        fail(f"overrides_registry.json is malformed — restore it from git ({REGISTRY}: {why}); it carries the "
             f"lifetime record of every deal's declared deferred payments ({IPRD_DEFERRED_EVENT} events) and every "
             "ticker's override events, so it is never read as empty or rewritten")
    for i, e in enumerate(ents):
        bad = registry_entry_problem(e)
        if bad is not None:
            fail(f"overrides_registry.json is malformed — restore it from git ({REGISTRY}: entry {i} (ticker "
                 f"{e.get('ticker')!r}, event {e.get('event')!r}): field {bad[0]!r} {bad[1]}); it carries the "
                 "lifetime record of every deal's declared deferred payments, so an event that cannot be read is "
                 "never skipped or rewritten")
    return reg


def registry_entry_problem(e, need_date=True):
    """[Codex review r28 of PR #47, re-verification] (field, why) when a registry entry cannot be read for what it
    is, else None. An entry whose `event` is iprd_deferred_payment, or that carries any field only such an event
    carries (IPRD_DEFERRED_EVENT_KEYS), is a deferred-payment event: registry_deferred_event_problem, which also
    requires the exact event name. Any other entry is a field override (a `field`) or an event make_score writes
    (_EVENT_DECLARATION); one with an unknown or missing event name is refused too, since it may be a damaged
    deferred-payment event. Round 28 had checked only entries named exactly iprd_deferred_payment, so the recorded
    Old Bio event with its event name misspelt or deleted passed, iprd_deferred_lifetime ignored it, a new $60M
    declaration scored as the deal's first payment past its $100M cap, and the wholesale replace erased the record."""
    if e.get("event") == IPRD_DEFERRED_EVENT or any(k in e for k in IPRD_DEFERRED_EVENT_KEYS):
        return registry_deferred_event_problem(e, need_date)
    if e.get("field"):
        return None
    if not (isinstance(e.get("event"), str) and e["event"] in _EVENT_DECLARATION):
        return "event", (f"is {e['event']!r}" if "event" in e else "is missing") + (
            f", not an event make_score writes ({', '.join(sorted(_EVENT_DECLARATION))}), and the entry is no field "
            "override")
    return None


def registry_prior_entries(ticker):
    """[Codex review r8 of PR #47] The registry entries an earlier make_score run left for this ticker ([] when the
    registry does not exist yet). An unreadable registry is refused: the deferred-payment record it carries is the only
    memory of a deal's paid milestones (and update_registry would otherwise rewrite it empty). [Codex review r26 of
    PR #47] So is a malformed one (load_registry: an object with an `entries` list of objects)."""
    reg = load_registry()
    if reg is None:
        return []
    return [e for e in reg["entries"] if e.get("ticker") == ticker]


def _norm_src(src):
    """A citation compared without extra whitespace."""
    return " ".join(str(src).split())


def _deal_evidence(first, contingent_total):
    """[Codex review r9 of PR #47] What identifies a deal beyond its name: (first_charged_period, the EDGAR accessions
    its contingent_total source cites)."""
    src = (contingent_total or {}).get("source") if isinstance(contingent_total, dict) else None
    return first, frozenset(m.group(0) for m in _engine.IPRD_ACCESSION_RE.finditer(str(src or "")))


def iprd_deferred_lifetime(ticker, entries, prior):
    """[Codex review r8 of PR #47] The durable lifetime contingent_total cap. entries: judgment.json
    iprd_deferred_payment as validated (or None); prior: this ticker's registry entries from earlier runs. Returns the
    registry events this run records, one per deal ({deal, first_charged_period, contingent_total, paid_to_date,
    periods [{period, amount}]}: every period ever declared, carried), or refuses:
      * a deal the registry recorded whose declarations now sum to LESS than its recorded paid_to_date — a deleted or
        shrunk entry (deleting history must not reopen the cap: before, the cap summed only what judgment.json held
        NOW, so a rolled-out $60M payment deleted and the engine rerun let a later $60M declaration pass a $100M
        contingent_total);
      * a deal whose lifetime — max(the declarations on recorded periods, the recorded paid_to_date) + the
        declarations on periods never recorded — exceeds its declared contingent_total;
      * [Codex review r9 of PR #47] a recorded deal declared with another contingent_total (value more than $1 apart,
        or a source that differs beyond whitespace) or another first_charged_period: the recorded ones are immutable
        (raising the cap reopened it: a $100M deal with $60M recorded took $140M once the cap read $200M) and the
        event keeps them;
      * [Codex review r10 of PR #47] a recorded deal whose declaration for a recorded period is missing or more than
        $1 apart from the recorded amount (shrunk or grown), naming each such period: a recorded period's amount is
        immutable and the event keeps it exactly (the event used to take the new declarations, so amounts moved
        between periods at an unchanged total — which can make another period wholly deferred and drop it from the
        recurrence count — and a deleted period's amount moved onto another one were rewritten into the record);
      * [Codex review r9 of PR #47] a new deal key whose evidence (_deal_evidence: the first_charged_period and a
        contingent_total source accession) matches a recorded event, or another deal declared beside it, under a
        different name — a renamed copy, which would get its own copy of the cap."""
    rec = {}
    for e in prior or []:
        # [Codex review r28 of PR #47] never skipped silently (a missing deal had dropped the recorded payments):
        # load_registry already refuses such a registry; a prior list from elsewhere is held to the same check —
        # [re-verification] every entry, so one carrying a deferred-payment event's fields under a damaged event name
        # is refused, not ignored
        bad = registry_entry_problem(e, need_date=False)
        if bad is not None:
            fail(f"{REGISTRY} event {e.get('event')!r} for ticker {e.get('ticker')!r} is malformed (field "
                 f"{bad[0]!r} {bad[1]}) — restore it from git before scoring")
        if e.get("event") == IPRD_DEFERRED_EVENT:
            rec.setdefault(_engine._deal_key(e["deal"]), []).append(e)
    decl = {}
    for e in entries or []:
        decl.setdefault(_engine._deal_key(e["deferred_payment_of"]["deal"]), []).append(e)
    # [Codex review r9 of PR #47] deal identity is the evidence, not the name: every other deal's evidence, recorded
    # (registry events) or declared (this judgment.json)
    others = [(rk, r.get("deal"), "recorded in the registry",
               _deal_evidence(r.get("first_charged_period"), r.get("contingent_total")))
              for rk, rs in rec.items() for r in rs]
    others += [(dk, des[0]["deferred_payment_of"]["deal"], "declared beside it",
                _deal_evidence(des[0]["deferred_payment_of"]["first_charged_period"],
                               des[0]["deferred_payment_of"]["contingent_total"]))
               for dk, des in decl.items()]
    events = []
    for k in sorted(set(rec) | set(decl)):
        r_es, es = rec.get(k, []), decl.get(k, [])
        if es and not r_es:
            first, accs = _deal_evidence(es[0]["deferred_payment_of"]["first_charged_period"],
                                         es[0]["deferred_payment_of"]["contingent_total"])
            for ok_, oname, where, (ofirst, oaccs) in others:
                if ok_ != k and ofirst == first and accs & oaccs:
                    fail(f"judgment.json {IPRD_DEFERRED_KEY}: deal {es[0]['deferred_payment_of']['deal']!r} carries the "
                         f"evidence of deal {oname!r} ({where}): the same first_charged_period {first} and a "
                         f"contingent_total cited to the same filing ({', '.join(sorted(accs & oaccs))}) — a renamed "
                         f"copy, which would get its own copy of the deal's cap. Declare the payment under {oname!r} "
                         "(WORKER_SPEC step 3); two distinct deals first charged in one period whose caps one filing "
                         "discloses are a main-agent decision (NEEDS_MAIN_AGENT)")
        if es and r_es:
            # [Codex review r9 of PR #47] a recorded deal's contingent_total and first charge are immutable
            d0 = es[0]["deferred_payment_of"]
            for r in r_es:
                r_ct, r_first = r.get("contingent_total"), r.get("first_charged_period")
                if not (_engine.iprd_contingent_total_ok(r_ct) and _engine.iprd_date_ok(r_first)):
                    fail(f"{REGISTRY} event {IPRD_DEFERRED_EVENT} for deal {r.get('deal')!r} is malformed (contingent_total "
                         f"{r_ct!r}, first_charged_period {r_first!r}) — restore it from git before scoring")
                if (abs(float(d0["contingent_total"]["value"]) - float(r_ct["value"])) > 1.0
                        or _norm_src(d0["contingent_total"]["source"]) != _norm_src(r_ct["source"])):
                    fail(f"judgment.json {IPRD_DEFERRED_KEY}: deal {d0['deal']!r} is declared with contingent_total "
                         f"{_usd_exact(d0['contingent_total']['value'])} ({d0['contingent_total']['source']}), but the "
                         f"registry recorded {_usd_exact(r_ct['value'])} ({r_ct['source']}) for it ({REGISTRY} event "
                         f"{IPRD_DEFERRED_EVENT}) — a recorded deal's contingent_total is immutable (changing it would "
                         "reopen the lifetime cap): declare the recorded one; a filing that revises the deal's milestones "
                         "is a main-agent decision (NEEDS_MAIN_AGENT)")
                if d0["first_charged_period"] != r_first:
                    fail(f"judgment.json {IPRD_DEFERRED_KEY}: deal {d0['deal']!r} is declared first charged "
                         f"{d0['first_charged_period']}, but the registry recorded first_charged_period {r_first} for it "
                         f"({REGISTRY} event {IPRD_DEFERRED_EVENT}) — a recorded deal's first charge is immutable")
        r_periods = {}
        for r in r_es:
            for x in r.get("periods") or []:
                a = _num(x.get("amount")) if isinstance(x, dict) else None
                if a is not None and isinstance(x.get("period"), str):
                    r_periods[x["period"]] = max(r_periods.get(x["period"], 0.0), a)
        paid = max([_num(r.get("paid_to_date")) or 0.0 for r in r_es] + [sum(r_periods.values())]) if r_es else 0.0
        name = es[0]["deferred_payment_of"]["deal"] if es else r_es[0]["deal"]
        d_periods = {e["period"]: float(e["amount"]) for e in es}
        ds = sum(d_periods.values())
        rec_txt = ", ".join(f"FY{q[:4]} {_usd_exact(v)}" for q, v in sorted(r_periods.items()))
        # [Codex review r10 of PR #47] every recorded period's amount is immutable (missing, shrunk or grown) — checked
        # first, so the refusal names the period; the deal-level sum below still catches an undeclared deal (and a
        # paid_to_date recorded above its periods' sum)
        moved = [(q, rv, d_periods.get(q)) for q, rv in sorted(r_periods.items())
                 if es and (q not in d_periods or abs(d_periods[q] - rv) > 1.0)]
        if moved:
            fail(f"judgment.json {IPRD_DEFERRED_KEY}: deal {name!r} "
                 + "; ".join(f"no longer declares period {q}" if dv is None
                             else f"declares {_usd_exact(dv)} for period {q}" for q, rv, dv in moved)
                 + f", but the registry recorded {'; '.join(f'{_usd_exact(rv)} for period {q}' for q, rv, _ in moved)} "
                 f"({REGISTRY} event {IPRD_DEFERRED_EVENT}: {rec_txt}; paid_to_date {_usd_exact(paid)}) — a recorded "
                 "period's amount is immutable (moving an amount between periods can make another period wholly "
                 "deferred and drop it from the recurrence count; deleting or shrinking one reopens the deal's "
                 "lifetime contingent_total cap): restore the recorded amounts (WORKER_SPEC step 3); a filing that "
                 "restates a paid milestone is a main-agent decision (NEEDS_MAIN_AGENT)")
        if r_es and (not es or ds < paid - 1.0):
            fail(f"judgment.json {IPRD_DEFERRED_KEY}: deal {name!r} "
                 + ("is no longer declared" if not es else f"is declared for {_usd_exact(ds)} in all")
                 + f", but the registry recorded a paid_to_date of {_usd_exact(paid)} for it ({REGISTRY} event "
                 f"{IPRD_DEFERRED_EVENT}: {rec_txt}) — an entry was deleted or shrunk. A paid milestone counts toward "
                 "the deal's lifetime contingent_total for good: restore the entries (WORKER_SPEC step 3)")
        on_rec = sum(r_periods[q] for q in d_periods if q in r_periods)
        new = sum(v for q, v in d_periods.items() if q not in r_periods)
        lifetime = max(on_rec, paid) + new
        # the recorded deal keeps its recorded cap (checked equal above); a new one takes the declared cap
        ct = r_es[0]["contingent_total"] if r_es else es[0]["deferred_payment_of"]["contingent_total"]
        first = r_es[0]["first_charged_period"] if r_es else es[0]["deferred_payment_of"]["first_charged_period"]
        cap = float(ct["value"])
        if lifetime > cap + 1.0:
            fail(f"judgment.json {IPRD_DEFERRED_KEY}: deal {name!r}: its lifetime deferred payments — "
                 f"{_usd_exact(max(on_rec, paid))} on the periods the registry recorded ({rec_txt or 'none'}) + "
                 f"{_usd_exact(new)} newly declared = {_usd_exact(lifetime)} — exceed its contingent_total "
                 f"{_usd_exact(cap)} (the unrecognized milestones / deferred consideration its source discloses): a "
                 "payment past it is a second purchase, a second charge")
        # the recorded per-period amounts are never overwritten (checked within $1 above); new periods merge
        merged = dict(d_periods)
        merged.update(r_periods)
        events.append({"ticker": ticker, "event": IPRD_DEFERRED_EVENT, "deal": name,
                       "first_charged_period": first,
                       "contingent_total": {"value": cap, "source": ct["source"]},
                       "paid_to_date": lifetime,
                       "periods": [{"period": q, "amount": v} for q, v in sorted(merged.items())]})
    return events


def check_iprd_amortized_ttm_current(folder, n):
    """[fixer review round] An iprd_amortized base on native_base ttm_json IS
    ttm.json's TTM base less the amortization: refuse it when ttm.json moved
    after the run (the plain --ttm pin's provenance rule), so the stale base
    is never scored and the TTM-leg overrides are never silently dropped."""
    am = _iprd_amortized_ttm(n)
    if am is None:
        return
    try:
        with open(f"{folder}/ttm.json", encoding="utf-8") as f:
            tt = json.load(f)
    except Exception:
        tt = None
    tv = _num((tt or {}).get("ttm_oe_per_share")) if isinstance(tt, dict) else None
    ts = _num((tt or {}).get("ttm_shares_diluted")) if isinstance(tt, dict) else None
    nb, sh = _num(am.get("native_base_per_share")), _num(am.get("shares"))
    # [Codex review r26 of PR #47] a ttm.json figure, undeclared: 0.1%, a zero only by an exact zero (figure_matches)
    if not (_engine.figure_matches(nb, tv) and ts is not None and sh is not None
            and abs(ts - sh) < 1.0):
        fail(f"the {IPRD_AMORTIZED_BASIS} base_override's native base is ttm.json's TTM base (record: "
             f"{nb} per share on {sh} shares) but ttm.json now holds ttm_oe_per_share {tv} on ttm_shares_diluted {ts} — "
             "ttm.json changed after the engine run; rerun ttm.py and the engine, then rebuild the declaration from the "
             "new run (WORKER_SPEC step 8)")


def check_base_basis_window(folder, n, o):
    """[Codex review r15 of PR #47] A plain base_override pinned through --base-oe-ps that is not ttm.json's figure
    (base_source agent_supplied_ttm_override) names the window its pin was built on, so the engine's IPR&D window is
    the base's own: a pin built from ttm.json's TTM figures on another denominator (VNOM's per-unit base) has the
    current YTD's cash flows in it, and without the declaration a charge there counted as $0. On a 5.6 run the
    declaration must carry basis_window, the run must have recorded the same one (inputs.base_basis_window), and a
    "ttm" window's ytd_current_period must still be ttm.json's. Output from an earlier release (VNOM's committed 5.4.0
    record) is not held to it; an iprd_amortized declaration names its native_base instead."""
    t = release_tuple(n.get("engine_release"))
    if (t is None or t < (5, 6, 0) or o.get("basis") is not None
            or (n.get("base_source") or "") != "agent_supplied_ttm_override"):
        return
    bw = o.get("basis_window")
    if bw is None:
        fail("judgment.json base_override declares the run's --base-oe-ps pin but no basis_window — on an engine "
             f"{ENGINE_RELEASE} run the declaration names the window its pin was built on, so the acquired-IPR&D window "
             "is the base's own: {\"window\": \"ttm\", \"ytd_current_period\": ttm.json's inputs.ocf.ytd_current_period} "
             "for a pin built from ttm.json's TTM figures (the current YTD's charges are then counted), {\"window\": "
             "\"fy\"} for one built from FY figures — add it and rerun the engine (WORKER_SPEC step 8)")
    rec = (n.get("inputs") or {}).get("base_basis_window")
    if rec != bw:
        fail(f"judgment.json base_override.basis_window {bw!r} is not the one the engine run recorded "
             f"(inputs.base_basis_window {rec!r}) — the judgment file and the engine run are out of sync; rerun the engine")
    if bw.get("window") == "ttm":
        try:
            with open(f"{folder}/ttm.json", encoding="utf-8") as f:
                tt = json.load(f)
        except Exception:
            tt = None
        ins = tt.get("inputs") if isinstance(tt, dict) else None
        ocf = ins.get("ocf") if isinstance(ins, dict) else None
        per = ocf.get("ytd_current_period") if isinstance(ocf, dict) else None
        if per != bw.get("ytd_current_period"):
            fail(f"judgment.json base_override.basis_window names ytd_current_period {bw.get('ytd_current_period')} but "
                 f"ttm.json now holds {per!r} — ttm.json changed after the engine run; rerun ttm.py and the engine, then "
                 "rebuild the declaration from the new run (WORKER_SPEC step 8)")


def check_iprd_amortized(n, j_base_override):
    """v5.6: an iprd_amortized declaration and the engine record must agree —
    the run pinned through --base-oe-ps at the declared value, the engine's
    iprd_adjustment treatment amortized_in_base, and its amortized record
    holding the same figures, shares, native base and value (the engine
    recomputed it to the cent). Also refuses the converse: an amortized engine
    record without the declaration (judgment.json changed after the run)."""
    blk = n.get("iprd_adjustment") if isinstance(n.get("iprd_adjustment"), dict) else None
    am = (blk or {}).get("amortized") if isinstance((blk or {}).get("amortized"), dict) else None
    declared = bool(j_base_override and j_base_override.get("basis") == IPRD_AMORTIZED_BASIS)
    if not declared:
        if blk and blk.get("treatment") == "amortized_in_base":
            fail("dcf_numbers.json carries the acquired-IPR&D charge amortized in the base (iprd_adjustment treatment "
                 "amortized_in_base) but judgment.json declares no iprd_amortized base_override — the judgment file and "
                 "the engine run are out of sync; rerun the engine")
        return
    inp = n.get("inputs") or {}
    pin = inp.get("base_oe_ps_arg")
    if (inp.get("base_pin_source") != "base_oe_ps_arg" or not isinstance(pin, (int, float)) or isinstance(pin, bool)
            or not blk or blk.get("treatment") != "amortized_in_base" or not am):
        fail(f"judgment.json declares an {IPRD_AMORTIZED_BASIS} base_override but the engine run did not carry it "
             f"(base_pin_source {inp.get('base_pin_source')!r}, iprd_adjustment treatment "
             f"{(blk or {}).get('treatment')!r}) — rerun the final pass with --base-oe-ps <its value> so the engine "
             "recomputes and records the amortized base (it is only for ACQUIRED_IPRD_RECURRENT)")
    o = j_base_override
    same = (abs(float(o["value"]) - float(pin)) <= 0.005
            and isinstance(am.get("expected_value"), (int, float)) and abs(float(am["expected_value"]) - float(o["value"])) <= 0.005
            and _figures_agree(am.get("figures"), o["figures"])
            and isinstance(am.get("shares"), (int, float)) and abs(float(am["shares"]) - float(o["shares"])) < 1.0
            and am.get("native_base") == o.get("native_base"))
    if not same:
        fail(f"judgment.json {IPRD_AMORTIZED_BASIS} base_override (value {o['value']}, figures {o['figures']}, shares "
             f"{o['shares']}, native_base {o.get('native_base')!r}) disagrees with the engine's record (value "
             f"{am.get('expected_value')}, figures {am.get('figures')}, shares {am.get('shares')}, native_base "
             f"{am.get('native_base')!r}) — rebuild the declaration from this run's dcf_numbers.json and rerun")


def iprd_override_required(n):
    """[Codex review r1 of PR #47; factored out in v5.7 (L0) for the misfit notch's R-2 exemption, L1] True when the
    engine recorded treatment not_applied_share_count_unverified with a positive acquired-IPR&D total: only a
    main-agent tier_override that quantifies the hand deduction publishes such a run
    (check_iprd_share_count_unverified)."""
    blk = n.get("iprd_adjustment") if isinstance(n.get("iprd_adjustment"), dict) else None
    if not blk or blk.get("treatment") != "not_applied_share_count_unverified":
        return False
    total = _num(blk.get("total"))
    return not (not total or total <= 0)


def check_iprd_share_count_unverified(n, j):
    """[Codex review r1 of PR #47] Treatment not_applied_share_count_unverified (a share-scale defect rescued by a
    pin with no power-of-ten factor): the engine found a positive acquired-IPR&D total but no verified share count to
    put it on, so it deducted nothing and the tier is the UNADJUSTED one. WORKER_SPEC step 4 / AGENTS check 8: the
    worker blocks NEEDS_MAIN_AGENT: shares, and only a main-agent tier_override whose reason quantifies the hand
    deduction publishes it. make_score refuses the score unless judgment.json sets tier_override with a reason that
    names a dollar figure and a percentage (the charge per share on the verified count and the adjusted weighted
    IRR); whether the figures are right is the review's to check. (v5.7: the condition is iprd_override_required.)"""
    if not iprd_override_required(n):
        return
    total = _num(n["iprd_adjustment"].get("total"))
    why = str(j.get("tier_override_reason") or "")
    if j.get("tier_override") and re.search(r"\$\s?\d", why) and re.search(r"\d\s?%", why):
        return
    fail(f"NEEDS_MAIN_AGENT: shares — ACQUIRED_IPRD_CHARGE not deducted: {_usd_exact(total)} (iprd_adjustment "
         "treatment not_applied_share_count_unverified: the share count behind the base is unverified, so the "
         "engine's tier is the UNADJUSTED one). Block the folder NEEDS_MAIN_AGENT; only the main agent publishes it, "
         "through judgment.json tier_override whose tier_override_reason quantifies the hand deduction — the charge "
         "per share on the verified share count ($) and the adjusted weighted IRR (%) (WORKER_SPEC step 4)"
         + ("; the tier_override_reason given names no dollar figure and percentage" if j.get("tier_override") else ""))


def check_iprd_unconverted(n):
    """[Codex review r3 of PR #47] A period excluded non_usd_no_rate with a positive native expense
    (ACQUIRED_IPRD_UNCONVERTED): the engine detected an acquired-IPR&D charge it could not convert (no FX
    rate for the expense's currency and date, no usable cash fact), so it deducted nothing and the tier is
    the UNADJUSTED one. Refused like a period awaiting its cash-flow check: the worker blocks
    NEEDS_MAIN_AGENT: currency; no judgment.json field publishes it (a hand deduction is the share-count
    case's escape only). [Codex review r6 of PR #47] The same for a positive cash_native beside a positive expense
    (the period's preferred amount, its cash outflow, could not be converted). [Codex review r24 of PR #47] And for
    a positive detector tag the engine cannot convert beside the other tag's (expense_tag_unconverted)."""
    blk = n.get("iprd_adjustment") if isinstance(n.get("iprd_adjustment"), dict) else None
    periods = [p for p in (blk or {}).get("periods") or [] if isinstance(p, dict)]
    lbl = lambda p: (f"FY{p['period'][:4]}" if p.get("window") == "fy" else f"YTD to {p.get('period')}")
    # [Codex review r24 of PR #47] a period gated because one positive detector tag cannot be converted beside the
    # other's (the two cannot be compared): its own message; the lists below exclude it
    uct = [p for p in periods if p.get("excluded") == _engine.IPRD_UNCONVERTED
           and (_num(_engine._iprd_tag_unconverted_native(p)) or 0) > 0]
    uc = [p for p in periods if p.get("excluded") == _engine.IPRD_UNCONVERTED and p not in uct
          and (_num(p.get("expense_native")) or 0) > 0]
    # [Codex review r4 of PR #47] a cash-only payment with no FX rate that could settle a charge: gated the same way
    ucc = [p for p in periods if p.get("excluded") == _engine.IPRD_UNCONVERTED and p not in uct
           and (_num(p.get("cash_native")) or 0) > 0]
    if uct:
        fail("NEEDS_MAIN_AGENT: currency — ACQUIRED_IPRD_UNCONVERTED: both acquired-IPR&D expense tags are filed "
             "positive and one has no FX rate the engine holds, in "
             + "; ".join(f"{lbl(p)} (" + ", ".join(
                 f"{t} {_num(v.get('native')):,.0f} {v.get('unit')}"
                 + ("" if v.get("unit") == "USD" else " (no FX rate)" if _num(v.get("usd")) is None
                    else f" = {_usd_exact(v.get('usd'))}")
                 for t, v in sorted((p.get("expense_tags_conflict") or {}).items()) if isinstance(v, dict)) + ")"
                         for p in uct)
             + " — the two cannot be compared, so the period's charge is unknown in USD and the engine deducted nothing "
             "for it (no iprd_cash_flow_check applies there): the record's IVs, IRRs and tier may be the UNADJUSTED "
             "ones. Block the folder NEEDS_MAIN_AGENT: currency (WORKER_SPEC step 3); it is scored once the engine "
             "can convert the tag")
    # [Codex review r6 of PR #47] the same for an unconvertible cash outflow beside a positive expense: the cash is the
    # preferred amount, so the expense never stands in for it
    ucx = [p for p in ucc if (_num(p.get("expense")) or 0) > 0]
    # [Codex review r8 of PR #47] cash after a charge expensed in a currency with no rate: its remainder is unknown
    ucr = [p for p in ucc if p not in ucx and p.get("unconverted_remainder_of")]
    ucc = [p for p in ucc if p not in ucx and p not in ucr]
    if ucr:
        fail("NEEDS_MAIN_AGENT: currency — ACQUIRED_IPRD_UNCONVERTED: a payment on the acquired-IPR&D cash tag, with "
             "no acquired-IPR&D expense in its period, after a charge expensed in a currency the engine holds no FX "
             "rate for, in "
             + ", ".join(f"{lbl(p)} {_num(p['cash_native']):,.0f} {p.get('cash_unit')} (after "
                         + ", ".join(f"FY{str(q)[:4]}" for q in p["unconverted_remainder_of"]) + ")" for p in ucr)
             + " — that charge's unpaid remainder is unknown in USD, so the payment may settle it and the record's "
             "IVs, IRRs and tier may be the UNADJUSTED ones. Block the folder NEEDS_MAIN_AGENT: currency (WORKER_SPEC "
             "step 3); it is scored once the engine can convert the charge")
    if ucx:
        fail("NEEDS_MAIN_AGENT: currency — ACQUIRED_IPRD_UNCONVERTED: the acquired-IPR&D cash outflow, the preferred "
             "amount, filed in a currency the engine holds no FX rate for, beside the expense, in "
             + ", ".join(f"{lbl(p)} {_num(p['cash_native']):,.0f} {p.get('cash_unit')} (expense "
                         f"{_usd_exact(p.get('expense'))})" for p in ucx)
             + " — the engine deducted nothing for it, so the record's IVs, IRRs and tier may be the UNADJUSTED ones. "
             "Block the folder NEEDS_MAIN_AGENT: currency (WORKER_SPEC step 3); it is scored once the engine can "
             "convert the payment")
    if ucc:
        fail("NEEDS_MAIN_AGENT: currency — ACQUIRED_IPRD_UNCONVERTED: a payment on the acquired-IPR&D cash tag, with "
             "no acquired-IPR&D expense in its period, filed in a currency the engine holds no FX rate for, in "
             + ", ".join(f"{lbl(p)} {_num(p['cash_native']):,.0f} {p.get('cash_unit')}" for p in ucc)
             + " — it may settle a charge the window deducts in part (or one expensed before the window), so the "
             "record's IVs, IRRs and tier may be the UNADJUSTED ones. Block the folder NEEDS_MAIN_AGENT: currency "
             "(WORKER_SPEC step 3); it is scored once the engine can convert the payment")
    if uc:
        fail("NEEDS_MAIN_AGENT: currency — ACQUIRED_IPRD_UNCONVERTED: acquired IPR&D expensed in a currency the "
             "engine holds no FX rate for, with no usable us-gaap cash fact, in "
             + ", ".join(f"{lbl(p)} {_num(p['expense_native']):,.0f} {p.get('expense_unit')}" for p in uc)
             + " — the engine deducted nothing, so the record's IVs, IRRs and tier are the UNADJUSTED ones. Block "
             "the folder NEEDS_MAIN_AGENT: currency (WORKER_SPEC step 3); it is scored once the engine can convert "
             "the charge")


def iprd_score_block(n):
    """score.json iprd_adjustment from the engine's block (None when the run
    has none: older-release output, or no acquired-IPR&D expense filed)."""
    b = n.get("iprd_adjustment")
    if not isinstance(b, dict):
        return None
    if b.get("deferred_payments_only"):
        # [Codex review r5 of PR #47] a block recording only rolled-out iprd_deferred_payment entries (no charge in
        # the window) is dcf_numbers.json bookkeeping for check_iprd_deferred_payment: it carries no charge.
        # [Codex review r15 of PR #47] it is still the engine's block, so the score keeps a minimal one (the record and
        # the score agree on whether a block exists); every consumer reads it as no charge (treatment none, 0)
        return {"treatment": b.get("treatment"), "total": b.get("total"), "charge_per_share": b.get("charge_per_share"),
                "deferred_payments_only": True, "periods": [],
                "deferred_payments_rolled_out": [
                    {"period": x.get("period"), "window": x.get("window"), "amount": x.get("amount"),
                     "deal": (x.get("deferred_payment_of") or {}).get("deal"),
                     "first_charged_period": (x.get("deferred_payment_of") or {}).get("first_charged_period")}
                    for x in b.get("deferred_payments_rolled_out") or [] if isinstance(x, dict)]}
    r2 = lambda v: round(v, 2) if isinstance(v, (int, float)) and not isinstance(v, bool) else None
    r4 = lambda v: round(v, 4) if isinstance(v, (int, float)) and not isinstance(v, bool) else None
    before = ((b.get("before") or {}).get("weighted") or {}) if isinstance(b.get("before"), dict) else {}
    after = ((b.get("after") or {}).get("weighted") or {}) if isinstance(b.get("after"), dict) else {}
    out = {"treatment": b.get("treatment"), "total": b.get("total"), "charge_per_share": b.get("charge_per_share"),
           "shares_denominator": b.get("shares_denominator"), "shares_source": b.get("shares_source"),
           "materiality": r4(b.get("materiality")), "material": b.get("material"), "recurrent": b.get("recurrent"),
           "unconfirmed_total": b.get("unconfirmed_total"),
           "periods": [dict({k: p.get(k) for k in ("period", "window", "start", "amount", "amount_basis", "tag_used",
                                                   "deducted", "excluded") if k in p},
                            **({"cash_flow_check": p["cash_flow_check"].get("presentation")}
                               if isinstance(p.get("cash_flow_check"), dict) else {}),
                            **({"deferred_payment": True} if p.get("deferred_payment") else {}),
                            **({"deferred_payment_of": [{k: x.get(k) for k in ("deal", "first_charged_period", "amount")}
                                                        for x in p["deferred_payment_of"] if isinstance(x, dict)]}
                               if isinstance(p.get("deferred_payment_of"), list) else {}),
                            **({"recurrence_excluded": p["recurrence_excluded"]} if p.get("recurrence_excluded") else {}))
                       for p in (b.get("periods") or []) if isinstance(p, dict)]}
    if isinstance(b.get("recurrence_excluded"), list):
        # only when the run had iprd_deferred_payment declarations (Andrew's 2026-10-20 ruling, delegated)
        out["recurrence_excluded"] = b["recurrence_excluded"]
    if "recurrence_expense_total" in b:
        # [Codex review r28 of PR #47] the recurrence gate's own figure, only when the engine recorded it (2 or more FY
        # charge years): the acquisitions' expense, which `material` (the deduction's) does not measure
        out["recurrence_expense_total"] = b.get("recurrence_expense_total")
        out["recurrence_materiality"] = r4(b.get("recurrence_materiality"))
    if before:
        out.update({"iv_before": {k[-2:]: r2(before.get(k)) for k in ("iv_at_15", "iv_at_20", "iv_at_25")},
                    "iv_after": {k[-2:]: r2(after.get(k)) for k in ("iv_at_15", "iv_at_20", "iv_at_25")},
                    "irr_before": r4(before.get("irr")), "irr_after": r4((b.get("after") or {}).get("irr")),
                    "tier_before": b.get("tier_before")})
    if isinstance(b.get("amortized"), dict):
        am = b["amortized"]
        out["amortized"] = {k: am.get(k) for k in ("native_base", "native_base_per_share", "figures", "mean_annual_charge",
                                                   "shares", "pinned_per_share")}
    return out


def _ads_factor(r):
    """(' × ADS ratio r', 'ADS') when an applied ADS ratio other than 1 scales the IPR&D per-share figures, else
    ('', 'share') — the printed equation then reproduces the engine's per-traded-unit value."""
    r = _num(r)
    if r is None or r <= 0 or abs(r - 1.0) < 1e-12:
        return "", "share"
    return f" × ADS ratio {r:g}", "ADS"


def iprd_lines(n):
    """key_numbers.md's acquired-IPR&D section ([] when the run has no block)."""
    b = n.get("iprd_adjustment")
    if not isinstance(b, dict):
        return []
    L = ["", "## Acquired IPR&D adjustment (engine 5.6 — Andrew, 2026-10-19)"]
    ro = [x for x in b.get("deferred_payments_rolled_out") or [] if isinstance(x, dict)]
    # [Codex review r5 of PR #47] the entries kept for their deal's lifetime contingent_total cap, shown
    ro_line = ("- Rolled out of the window (judgment.json iprd_deferred_payment, kept declared: counted toward the "
               "deal's lifetime contingent_total, never applied): " + "; ".join(
                   f"FY{str(x.get('period'))[:4]} {_usd_exact(x.get('amount'))} — "
                   f"{(x.get('deferred_payment_of') or {}).get('deal')}, first charged "
                   f"{(x.get('deferred_payment_of') or {}).get('first_charged_period')}, contingent_total "
                   f"{_usd_exact(((x.get('deferred_payment_of') or {}).get('contingent_total') or {}).get('value'))}"
                   for x in ro)) if ro else None
    if b.get("deferred_payments_only"):
        # no charge in the window: nothing deducted, no treatment to print
        return L + ["- No acquired-IPR&D charge in this run's window: nothing deducted"] + ([ro_line] if ro_line else [])
    t = b.get("treatment")
    one_time = t == "one_time_value_deduction"
    for p in b.get("periods") or []:
        lbl = (f"FY{p['period'][:4]} ({p['period']})" if p.get("window") == "fy"
               else f"Current YTD {p.get('start') or '?'}..{p['period']} (TTM leg)")
        amt = _usd_exact(p.get("amount"))
        # [fixer review round] "deducted" only under the one-time treatment: an amortized run carries the FY charges
        # in the base (the mean reads FY figures only), any other treatment deducts nothing
        counted = ("deducted" if one_time
                   else ("counted in the amortization mean" if p.get("window") == "fy"
                         else "in neither the amortization mean (FY figures only) nor a deduction")
                   if t == "amortized_in_base" else f"counted, not deducted ({t})")
        state = (f"excluded — {p['excluded']}" if p.get("excluded")
                 else f"{counted} {_usd_exact(p.get('deducted'))}" if p.get("deducted") else "nothing to deduct")
        chk = p.get("cash_flow_check") if isinstance(p.get("cash_flow_check"), dict) else None
        dpo = ([x for x in p["deferred_payment_of"] if isinstance(x, dict)]
               if isinstance(p.get("deferred_payment_of"), list) else [])
        dpo_txt = ""
        if dpo:
            # each first charge by its date: a calendar-year "FY" label misnames a non-December filer's quarter
            deals = " and ".join(f"{x.get('deal')} ({_usd_exact(x.get('amount'))}, first charged "
                                 f"{x.get('first_charged_period') or '?'})" for x in dpo)
            _sum = sum(float(x["amount"]) for x in dpo if isinstance(x.get("amount"), (int, float)))
            dpo_txt = (f"; deferred payment of {deals}: excluded from the recurrence count" if p.get("recurrence_excluded")
                       else (f"; partly a deferred payment of {deals} — {_usd_exact(_sum)} of "
                             f"{_usd_exact(p.get('amount'))}: still counts toward recurrence"))
        L.append(f"- {lbl}: {amt} — {p.get('amount_basis') or '—'} basis, tag {p.get('tag_used') or '—'}; {state}"
                 + (f"; cash-flow check: {chk.get('presentation')}" if chk else "")
                 + ("; deferred payment of an earlier window period's accrued charge" if p.get("deferred_payment") else "")
                 # [Codex review r12 of PR #47] a share-paid residual accrues nothing; an assumed-cash one is named
                 + (f"; residual {_usd_exact(p.get('residual_paid_in_shares'))} paid in shares (not accrued as unpaid)"
                    if p.get("residual_paid_in_shares") else "")
                 # [Codex review r21 of PR #47] an expense with no FX rate: the residual is unknown in USD
                 + (f"; residual of the {p.get('expense_native'):,.0f} {p.get('expense_unit')} expense (unknown in USD) "
                    "paid in shares (not accrued as unpaid)" if p.get("residual_paid_in_shares_unknown_usd") else "")
                 + ("; assumes the earlier remainder was payable in cash (no paid_in_shares check declares it settled "
                    "in shares)" if p.get("deferred_payment_assumption") else "")
                 + dpo_txt
                 + ("; deal and consideration: not identified by the engine — name them in analysis.md" if p.get("deducted") else "")
                 # v5.7 (L2, R3; rebase A13): on a 5.7 run the consideration figures are declared facts
                 + (" (declare the consideration in facts.json, kind filing)" if p.get("deducted") and is_57_run(n) else ""))
    mat = b.get("materiality")
    tail = "" if one_time else f" (treatment {t}: no one-time deduction)"
    # [Codex review r4 of PR #47] the engine's per-share figures are per traded unit (× the applied ADS ratio)
    ads_txt, unit = _ads_factor(b.get("ads_ratio"))
    L.append(f"- Total charge: {_usd_exact(b.get('total'))} ÷ {b['shares_denominator']:,.0f} shares ({b.get('shares_source')})"
             f"{ads_txt} = {_money(b.get('charge_per_share'))}/{unit}{tail}" if b.get("shares_denominator")
             else f"- Total charge: {_usd_exact(b.get('total'))} (no share denominator: not deducted)")
    L.append(f"- Treatment: {t}" + (f" · {mat * 100:.2f}% of the base OE total" if isinstance(mat, (int, float)) else "")
             + (" · material (ACQUIRED_IPRD_CHARGE)" if b.get("material")
                else (" · below the 5% flag threshold (deducted, no flag)" if one_time else " · below the 5% flag threshold (no flag)")
                if b.get("total") else "")
             + (" · recurrent (ACQUIRED_IPRD_RECURRENT)" if b.get("recurrent") else ""))
    if "recurrence_expense_total" in b:
        # [Codex review r28 of PR #47] the recurrence gate measures the counted years' acquisition expense, never the
        # cash deducted: shown beside the deduction's materiality so a recurrent run with little deducted reads right
        rm, ru = b.get("recurrence_materiality"), [x for x in b.get("recurrence_expense_unknown_usd") or []]
        # [Codex review r29 of PR #47, second polish review] recurrence_expense_unknown_usd lists only the counted years
        # whose own acquired-IPR&D expense has no USD figure (a USD expense beside cash with no FX rate is read)
        who = "its" if len(ru) == 1 else "each year's"
        L.append("- Recurrence: charge years " + ", ".join(f"FY{str(q)[:4]}" for q in b.get("fy_with_charge") or [])
                 + f" — acquired IPR&D expensed in the counted periods {_usd_exact(b.get('recurrence_expense_total'))}"
                 + (f" (and {', '.join(ru)}: {who} acquired-IPR&D expense has no USD figure — unknown, read as material)"
                    if ru
                    else f" = {rm * 100:.2f}% of the base OE total" if isinstance(rm, (int, float))
                    else " (no valuation to measure it against: read as material)")
                 + (" · recurrent (ACQUIRED_IPRD_RECURRENT)" if b.get("recurrent")
                    else " · below the 5% threshold: not recurrent"))
    rx = b.get("recurrence_excluded") if isinstance(b.get("recurrence_excluded"), list) else []
    if rx:
        L.append("- Excluded from the recurrence count (judgment.json iprd_deferred_payment — a deferred payment of a deal "
                 "first charged earlier; still deducted): " + "; ".join(
                     f"FY{str(x.get('period'))[:4]} {_usd_exact(x.get('amount'))} — {x.get('deal')}, first charged "
                     f"{x.get('first_charged_period')}" for x in rx))
    if ro_line:
        L.append(ro_line)
    if b.get("unconfirmed_total"):
        L.append(f"- Awaiting the cash-flow check (ACQUIRED_IPRD_UNCONFIRMED): {_usd_exact(b['unconfirmed_total'])} — not deducted")
    bw = ((b.get("before") or {}).get("weighted") or {}) if isinstance(b.get("before"), dict) else {}
    if bw:
        w = n.get("weighted") or {}
        L.append("- Weighted IV before → after: " + " · ".join(
            f"@{r}% {_money(bw.get(f'iv_at_{r}'))} → {_money(w.get(f'iv_at_{r}'))}" for r in (15, 20, 25)))
        L.append(f"- Weighted IRR before → after: {_pct(bw.get('irr'))} → {_pct(n.get('implied_irr_weighted'))} · "
                 f"tier {b.get('tier_before')} → {n.get('tier_by_numbers')}")
    am = b.get("amortized") if isinstance(b.get("amortized"), dict) else None
    if am:
        am_ads, _ = _ads_factor(am.get("ads_ratio") if "ads_ratio" in am else b.get("ads_ratio"))
        L.append(f"- Amortized in the base (iprd_amortized base_override): native base {_money(am.get('native_base_per_share'))} "
                 f"({am.get('native_base')}) − mean annual charge {_usd_exact(am.get('mean_annual_charge'))} ÷ "
                 f"{(am.get('shares') or 0):,.0f} shares{am_ads} = pinned base {_money(am.get('pinned_per_share'))}; "
                 "no one-time deduction")
    return L


def check_no_double_softening(n, j, model_fit):
    """A payable-earnings base already measures what common shareholders earn;
    stacking the 2026-10-15 one-notch misfit tier_override on top double-counts
    the same correction (AGENTS.md, sector misfits). Returns the refusal text
    or None."""
    if not (n.get("payable_base") and j.get("tier_override")):
        return None
    tb, tf = n.get("tier_by_numbers"), j.get("tier_override")
    if model_fit == "misfit" and tb and tf and TIER_ORDER.get(tf, -1) < TIER_ORDER.get(tb, -1):
        return (f"judgment.json sets tier_override {tf} below the numbers tier {tb} while the base is already the "
                "payable-earnings base (payable_earnings_5y) — the one-notch insurer softening is not applied on "
                "top of that base (double-counting). Clear tier_override, or drop --base-judgment")
    return None


# ---------------------------------------------------------------------------
# v5.7 lane L1 — R1 the mechanical sector-misfit notch (Andrew, 2026-10-19)
# ---------------------------------------------------------------------------
NOTCH_RULING = "the mechanical sector-misfit notch (Andrew, 2026-10-19)"


def misfit_detection(n, folder):
    """v5.7 (L1, R1): (model_fit, basis) — dcf_engine.misfit_status on this folder (the engine's sector_model on a
    5.7 run, else an older run's SECTOR_MODEL_MISMATCH flag checked against the folder's SIC, else the folder's SIC
    alone). basis is None on a modeled name unless a present SIC set a misfit universe sector aside (Q1 (b))."""
    folder = os.path.normpath(folder)
    return _engine.misfit_status(n, os.path.dirname(folder), os.path.basename(folder))


def _basis_text(basis):
    """'universe sector Finance; EDGAR SIC 6211 Security Brokers, Dealers & Flotation Companies (broker-dealers)' —
    the rules behind a misfit, for its reason and refusal texts."""
    b = basis or {}
    parts = []
    if b.get("sector"):
        parts.append(f"universe sector {b['sector']}")
    if b.get("sic") and b.get("sic_class"):
        desc = f" {b['sic_description']}" if b.get("sic_description") else ""
        parts.append(f"EDGAR SIC {b['sic']}{desc} ({_engine.MISFIT_SIC_LABEL.get(b['sic_class'], b['sic_class'])})")
    return "; ".join(parts) or "SECTOR_MODEL_MISMATCH flag"


def _misfit_label(basis):
    """What the owner's-earnings DCF fits poorly: the SIC class's label, else '<sector> names'."""
    b = basis or {}
    if b.get("sic_class"):
        return _engine.MISFIT_SIC_LABEL.get(b["sic_class"], b["sic_class"])
    return f"{b['sector'].lower()} names" if b.get("sector") else "this business model"


def _irr_s(n):
    """The weighted IRR as the notch texts print it ('11.70%', with the acquired-IPR&D note when the run deducted a
    one-time charge — the notch acts on that adjusted tier, 07 G2)."""
    irr = _num(n.get("implied_irr_weighted"))
    s = f"{irr * 100:.2f}%" if irr is not None else "n/a"
    blk = n.get("iprd_adjustment") if isinstance(n.get("iprd_adjustment"), dict) else {}
    if (_num(blk.get("charge_per_share")) or 0) > 0:
        s += " (after the one-time acquired-IPR&D deduction)"
    return s


def _tier_below(t):
    """The next tier down (S..D -> A..F); F stays F."""
    i = TIERS.index(t) if t in TIERS else len(TIERS) - 1
    return TIERS[min(i + 1, len(TIERS) - 1)]


def misfit_notch(n, j, model_fit, basis, override, run57):
    """v5.7 (L1, R1; Andrew, 2026-10-19): (tier_final, block | None, override_in_force) for one score. Every sector
    misfit publishes ONE tier below its numbers tier (S->A, A->B, B->C, C->D) with a reason that carries a number;
    block is score.json misfit_notch (None on a modeled name):
    {applies, tier_by_numbers, tier_after_notch, reason, reason_source, not_applied, basis}.
    - payable_base (a --base-judgment payable-earnings pin): not notched, not_applied "payable_base" — the base
      already measures what common shareholders earn (check_no_double_softening still refuses an override below it).
    - numbers tier D / F: not notched, not_applied "tier_floor_D" / "tier_F" (D is the lowest graded tier; F has no
      positive owner's earnings). A tier_override there keeps its pre-5.7 meaning.
    - S-C: notched. tier_override above the notched tier -> refused (R-1, every rebuild). Equal to it -> the legacy
      one-notch override before 5.7 (its reason becomes the notch reason, reason_source "tier_override", not in
      force), refused on a 5.7 run (R-2) — unless iprd_override_required(n): the main agent's hand-deduction override
      is then in force at the notched tier. Below it -> a further judgment downgrade, in force. On a 5.7 run
      misfit_notch_reason is required (R-3) and must carry a number (R-4); before 5.7 the reason is
      misfit_notch_reason, else the legacy override's reason, else an auto text with the weighted IRR.
    misfit_notch_reason must be a string or null on every run (R-5). Refusals call fail() — main() calls this before
    registry_transaction, so nothing is written."""
    rj = j.get("misfit_notch_reason")
    if rj is not None and not isinstance(rj, str):
        fail("judgment.json: misfit_notch_reason must be a string or null")
    rj = (rj or "").strip() or None
    tb = n.get("tier_by_numbers")
    if model_fit != "misfit":
        return (override or tb), None, bool(override)
    irr_s = _irr_s(n)
    blk = {"applies": False, "tier_by_numbers": tb, "tier_after_notch": tb, "reason": None, "reason_source": "auto",
           "not_applied": None, "basis": basis}
    pb = n.get("payable_base") if isinstance(n.get("payable_base"), dict) else None
    if pb:
        blk.update(not_applied="payable_base",
                   reason=(f"not notched: the base is the payable-earnings pin ({pb.get('basis') or 'payable_earnings_5y'}, "
                           f"{_money(_num(pb.get('pinned_per_share')))}/share via --base-judgment; weighted IRR {irr_s}), "
                           "which already measures what common shareholders earn — a notch on top would double-count"))
        return (override or tb), blk, bool(override)
    if tb == "D":
        # never "there is no tier below D": a D misfit's judgment may still publish F (01 §3.3 keeps a D -> F
        # override), and key_numbers.md prints that F right above this reason (review of d9618aa)
        blk.update(not_applied="tier_floor_D",
                   reason=(f"cannot notch: numbers tier D (weighted IRR {irr_s}) is the lowest graded tier (F means no "
                           f"positive owner's earnings, not a notch) — {NOTCH_RULING} is not applied"))
        return (override or tb), blk, bool(override)
    if tb not in TIERS[:4]:   # F (or no tier: make_score refused that earlier)
        sub = n.get("f_subtype") or "no positive owner's earnings"
        base = _num(n.get("base_oe_per_share"))
        blk.update(not_applied="tier_F",
                   reason=(f"cannot notch: numbers tier F ({sub}" + (f"; base OE/share {_money(base)}" if base is not None else "")
                           + f") — no positive owner's earnings, so there is no IRR to soften — {NOTCH_RULING} is not applied"))
        return (override or tb), blk, bool(override)
    notched = _engine.notch_tier(tb)
    head = (f"sector misfit ({_basis_text(basis)}): numbers tier {tb} at a weighted IRR of {irr_s} publishes one notch "
            f"lower as {notched}")
    hand = iprd_override_required(n)   # the main agent's hand-deduction override (check_iprd_share_count_unverified)
    if override:
        if TIER_ORDER.get(override, -1) > TIER_ORDER[notched]:
            fail(f"judgment.json tier_override {override} is above the misfit-notched tier {notched} — {head} (Andrew, "
                 "2026-10-19: every sector misfit publishes one tier below its numbers tier); an override may only go "
                 f"further down. Set tier_override to null (or {_tier_below(notched) if (run57 and not hand) else notched} "
                 "or lower with a reason)")
        if override == notched and run57 and not hand:
            fail(f"judgment.json tier_override {override} only restates the mechanical misfit notch ({head}) — since "
                 "engine 5.7 make_score applies the notch itself: set tier_override to null and put the reason in "
                 "misfit_notch_reason")
    if run57:
        if not rj:
            fail(f"judgment.json: misfit_notch_reason is required on a 5.7 run of a sector misfit ({head}) — write the "
                 "payable-earnings measure the analysis relied on (operating EPS, dividends from subsidiaries, capital "
                 "returned) or the IRR it implies; the reason must carry a number")
        if not re.search(r"\d", rj):
            fail(f"judgment.json: misfit_notch_reason must carry a number ({head}) — 'screens materially lower' with no "
                 f"figure is not a reason (got {rj!r})")
    if rj:
        reason, src = rj, "judgment"
    elif override == notched and not hand and str(j.get("tier_override_reason") or "").strip():
        reason, src = str(j["tier_override_reason"]).strip(), "tier_override"   # the legacy one-notch override
    else:
        reason, src = (f"Sector misfit ({_basis_text(basis)}): numbers tier {tb} at a weighted IRR of {irr_s} publishes "
                       f"one notch lower as {notched} — {NOTCH_RULING}: the owner's-earnings DCF fits "
                       f"{_misfit_label(basis)} poorly. No worker reason on record."), "auto"
    blk.update(applies=True, tier_after_notch=notched, reason=reason, reason_source=src)
    if override and (TIER_ORDER.get(override, -1) < TIER_ORDER[notched] or (override == notched and hand)):
        return override, blk, True
    return notched, blk, False


def misfit_set_aside_record(model_fit, basis):
    """v5.7 (L1, R1, Q1 (b)): score.json misfit_sector_set_aside — why a name whose universe sector is a misfit
    sector (an older run's SECTOR_MODEL_MISMATCH flag, or the 5.7 engine's sector_model) is scored as modeled: its
    present SIC lies outside 6000-6799 and every misfit range. None otherwise."""
    if model_fit == "misfit" or not (basis or {}).get("sector_set_aside_by_sic"):
        return None
    b = basis
    desc = f" {b['sic_description']}" if b.get("sic_description") else ""
    return {"sector": b.get("sector"), "sic": b.get("sic"), "sic_description": b.get("sic_description"),
            "sic_source": b.get("sic_source"), "source": b.get("source"),
            "reason": (f"EDGAR SIC {b.get('sic')}{desc} lies outside finance / insurance / real estate (6000-6799) and "
                       f"outside every misfit SIC range: the filer's own industry code contradicts the universe sector "
                       f"{b.get('sector')}, so the sector rule does not make it a misfit (rule Q1 (b) of 2026-10-21; "
                       "dcf_engine.SIC_SETS_ASIDE_SECTOR)")}


def validate_ads_ratio(j):
    """judgment.json ads_ratio {ratio, source, reason} for 20-F/40-F filers.
    None if absent; shape-checked if present."""
    a = j.get("ads_ratio")
    if a is None:
        return None
    if not isinstance(a, dict):
        fail("judgment.json: ads_ratio must be an object {ratio, source, reason}")
    if not isinstance(a.get("ratio"), (int, float)) or isinstance(a.get("ratio"), bool) or a["ratio"] <= 0:
        fail("judgment.json: ads_ratio.ratio must be a positive number (ordinary shares per ADS)")
    if not str(a.get("source") or "").strip():
        fail("judgment.json: ads_ratio.source must be a non-empty string")
    if not str(a.get("reason") or "").strip():
        fail("judgment.json: ads_ratio.reason must be a non-empty string")
    return a


def validate_second_pass(j):
    """v5.4: pass 2 goes through make_score like everything else — the old
    pass-2 spec told workers to hand-edit score.json, which the v5 mechanics
    forbid. judgment.json may carry second_pass {date, verdict
    "changed"|"no_change", prior_tier, prior_weighted_irr, prior_iv_at_15,
    summary}; it is shape-checked and copied into score.json verbatim."""
    sp = j.get("second_pass")
    if sp is None:
        return None
    if not isinstance(sp, dict):
        fail("judgment.json: second_pass must be an object {date, verdict, prior_tier, prior_weighted_irr, prior_iv_at_15, summary}")
    if sp.get("verdict") not in ("changed", "no_change"):
        fail("judgment.json: second_pass.verdict must be \"changed\" or \"no_change\"")
    if not str(sp.get("date") or "").strip():
        fail("judgment.json: second_pass.date is required (YYYY-MM-DD)")
    if not str(sp.get("summary") or "").strip():
        fail("judgment.json: second_pass.summary is required (evidence + sources, 2-4 sentences)")
    if sp["verdict"] == "changed":
        if sp.get("prior_tier") not in TIERS:
            fail("judgment.json: second_pass.prior_tier must be a tier when verdict is \"changed\"")
        for k in ("prior_weighted_irr", "prior_iv_at_15"):
            v = sp.get(k)
            if v is not None and (not isinstance(v, (int, float)) or isinstance(v, bool)):
                fail(f"judgment.json: second_pass.{k} must be a number or null")
    return {k: sp.get(k) for k in ("date", "verdict", "prior_tier", "prior_weighted_irr", "prior_iv_at_15", "summary")}


# ---------------------------------------------------------------------------
# v5.7 lane L2 (R3 strict quoting, Andrew 2026-10-19): declared facts, saved method runs, the previous score and
# the influence trace — every refusal here runs before registry_transaction (07 §1.12; rebase I6)
# ---------------------------------------------------------------------------
def load_declared_facts(folder, n, j, prior_score=None):
    """07 §1.12 step 2 (02 §4): <T>/facts.json read, validated against the schema and verified against the folder
    files (folder facts, calc facts, snippets, folder duplicates, staleness) — no influence yet. Returns the
    facts.FactsCheck every later step reads (by_id / values for the cited facts, summary for score.json, the
    Declared facts section, the declared_facts registry event), or None when the folder declares no facts. A
    declaration that is new or edited since the prior score (its facts_sha256 differs from the prior
    score.json's declared_facts.facts_sha256) is AUTHORING: any folder fact that does not verify refuses; an
    unchanged one is a REBUILD: a folder file that moved since is recorded as drift and the run scores (02 §4.7, so an
    engine-release rebuild or the SEC enrichment never fails on folder-file churn). Schema problems always refuse."""
    doc, err = _facts.load(folder)
    if err:
        fail(err)
    if doc is None:
        return None
    prior = (prior_score or {}).get("declared_facts") if isinstance(prior_score, dict) else None
    prior_sha = prior.get("facts_sha256") if isinstance(prior, dict) else None
    try:
        return _facts.check(doc, folder, os.path.basename(os.path.normpath(folder)).upper(), n=n, prior_sha=prior_sha)
    except _facts.FactsRefusal as e:
        fail(str(e))


def load_method_runs(folder, n):
    """The saved method runs (02 §7.3): every <T>/dcf_numbers_<label>.json — a byte copy of an engine run made by
    check_quotes.py --save-run — whose content_hash verifies and whose ticker is this folder's. On a 5.7 run a
    tampered or foreign saved run refuses (an analysis quoting a method range must quote verbatim engine output);
    on an older run it is skipped with a warning (legacy saved runs are not re-graded). Returns [{"summary": the
    score.json method_runs entry, "n": the record}] sorted by label, or None when there is none."""
    ticker = str(n.get("ticker") or os.path.basename(os.path.normpath(folder))).upper()
    out = []
    for label, _path, rec in _quotes.saved_runs(folder):
        why = _quotes.saved_run_problem(label, rec, ticker)
        if why is None and not _quotes.LABEL_RE.match(label):
            why = f"dcf_numbers_{label}.json: the label must match ^[a-z][a-z0-9_]{{0,31}}$ (check_quotes.py --save-run)"
        if why:
            if is_57_run(n):
                fail(why)
            print(f"make_score.py: warning — {why}; not rendered (an engine run before 5.7: not refused)", file=sys.stderr)
            continue
        iprd = rec.get("iprd_adjustment") if isinstance(rec.get("iprd_adjustment"), dict) else {}
        s = {"label": label, "file": f"dcf_numbers_{label}.json", "content_hash": rec.get("content_hash"),
             "as_of": rec.get("as_of"), "engine_release": rec.get("engine_release"),
             "base_oe_per_share": rec.get("base_oe_per_share"), "base_source": rec.get("base_source"),
             "implied_irr": round(rec["implied_irr_weighted"], 4) if _num(rec.get("implied_irr_weighted")) is not None else None,
             "iv_at_15": round(rec["iv_at_15"], 2) if _num(rec.get("iv_at_15")) is not None else None,
             "tier_by_numbers": rec.get("tier_by_numbers")}
        if iprd.get("treatment") and _num(iprd.get("charge_per_share")) is not None:
            # rebase A15: a saved IPR&D run's IVs / IRR are after its own deduction
            s["iprd_treatment"], s["iprd_charge_per_share"] = iprd["treatment"], iprd["charge_per_share"]
        out.append({"summary": s, "n": rec})
    return out or None


def _legacy_prior_differs(prior, n):
    irr = _num(n.get("implied_irr_weighted"))
    pi = _num(prior.get("implied_irr"))
    base, pb = _num(n.get("base_oe_per_share")), _num(prior.get("base_oe_per_share"))
    return (prior.get("analysis_date") != n.get("as_of") or prior.get("engine_release") != n.get("engine_release")
            or ((irr is None) != (pi is None)) or (irr is not None and abs(round(irr, 4) - pi) > 0.5e-4 + 1e-9)
            or ((base is None) != (pb is None)) or (base is not None and abs(base - pb) > 1e-9 * max(1.0, abs(base))))


def previous_score_summary(prior_score, n):
    """02 §7.3: the score this run replaces when it was ANOTHER engine run's — its dcf_content_hash differs from this
    run's content_hash, or (a prior score from before the hash existed) its analysis_date, engine_release,
    weighted IRR or base differ — as {analysis_date, engine_release, tier_final, tier_by_numbers, implied_irr,
    iv_at_15, base_oe_per_share, dcf_content_hash}; a rebuild of the same run carries the prior score's own
    previous_score forward; None for a first score (or a rebuild of a run nothing preceded)."""
    if not isinstance(prior_score, dict):
        return None
    ph = prior_score.get("dcf_content_hash")
    differs = (ph != n.get("content_hash")) if ph else _legacy_prior_differs(prior_score, n)
    if not differs:
        carried = prior_score.get("previous_score")
        return carried if isinstance(carried, dict) else None
    return {k: prior_score.get(k) for k in ("analysis_date", "engine_release", "tier_final", "tier_by_numbers",
                                            "implied_irr", "iv_at_15", "base_oe_per_share", "dcf_content_hash")}


# 12_lane_defaults Q2 (main agent, 2026-10-21, pending Andrew's ratification; L2 rebase A14 / Q1): the main agent's
# unverified-share-count IPR&D tier_override (#47, check_iprd_share_count_unverified) is held to R3 in full — its
# share count a cited filing fact, the per-share charge a calc fact, the adjusted IRR from a saved run. False is the
# alternative Andrew was offered: that one path keeps #47's "a $ figure and a %" test only and is not traced.
IPRD_HAND_OVERRIDE_TRACED = True


def _numeric_values(obj):
    """A ValueSet of every numeric leaf of obj (a number, a list, a dict, or a ValueSet already)."""
    if isinstance(obj, _qt.ValueSet):
        return obj
    vs = _qt.ValueSet()

    def walk(o):
        if isinstance(o, dict):
            for v in o.values():
                walk(v)
        elif isinstance(o, (list, tuple, set)):
            for v in o:
                walk(v)
        elif _num(o) is not None:
            vs.add(o)
    walk(obj)
    return vs


def _trace_only_split(trace_only):
    """10 §(l): trace_only is a list of values plus dcf_numbers.json key paths (strings), or {"values", "paths"}."""
    if trace_only is None:
        return None, ()
    if isinstance(trace_only, dict):
        vals, paths = trace_only.get("values") or [], trace_only.get("paths") or []
    else:
        vals = [x for x in trace_only if not isinstance(x, str)]
        paths = [x for x in trace_only if isinstance(x, str)]
    # the values at the excluded paths are added by check_influence, which holds the record
    return _numeric_values(vals), tuple(str(p) for p in paths)


def base_pin_trace_only(n, bo):
    """[review r05, 2026-10-21] check_influence's trace_only for a plain base_override (R3: a third-party figure is
    never a base override's sole support): a HAND pin (--base-oe-ps: inputs.base_oe_ps_arg) is the worker's own
    number, recorded in dcf_numbers.json, so it may be quoted in its reason but never anchors it — the paths
    inputs.base_oe_ps_arg and base_oe_per_share (and base_oe_latest_per_share / base_oe_normalized_per_share where
    they equal the pin) leave the engine set, in the scored run and in a saved copy of it, and the declared value
    joins the accepted values. None for a run without a hand pin (a ttm.json base is ttm.py's figure, a real engine
    source)."""
    pin = _num((n.get("inputs") or {}).get("base_oe_ps_arg"))
    if pin is None:
        return None
    vals = [pin] + [v for v in (_num((bo or {}).get("value")),) if v is not None]
    paths = ["inputs.base_oe_ps_arg", "base_oe_per_share"]
    for k in ("base_oe_latest_per_share", "base_oe_normalized_per_share"):
        v = _num(n.get(k))
        if v is not None and abs(v - pin) <= 1e-9 * max(1.0, abs(pin)):
            paths.append(k)
    return {"values": vals, "paths": paths}


def check_influence(field, text, fact_ids, fc, folder, n, extra=None, trace_only=None, require_anchor=False):
    """v5.7 (L2, R3 — Andrew 2026-10-19; 02 §5, 10 §(l)): the one influence-trace entry point every lane's reason
    fields call on a 5.7 run (07 §1.12 step 7; output from an older release is never checked — its reasons predate
    the rule, D1). In order, judgment.json `field`'s `text` is refused when: (1) it cites [F#] ids facts.json does
    not declare; (2) it carries no number (every field except a plain base_override's reason / source); (3) a
    number traces to neither an engine source — dcf_numbers.json, ttm.json, the saved method runs, the filed history
    / return series / derived figures key_numbers.md prints, and `extra`'s numeric leaves; never judgment.json, and
    never the worker text the engine echoes into its flag strings (check_quotes.influence_sources blanks
    check_folder's worker text and the record's own copies of it, review r02) — nor a CITED fact's value
    (`trace_only` values, and the values at its dcf_numbers.json paths, which are removed from the engine set — from
    a saved run too where it repeats them — are accepted but never count as an engine match); (4) every number rests
    only on third-party facts (R3: they calibrate scenarios and give context only); (5) a cited fact does not list the
    field's used_for tag (facts.INFLUENCE_TAGS); (6) require_anchor, the text has a number, and no number matched an
    engine source outside trace_only, `extra`, or a cited non-third-party fact tagged for the field (a plain
    base_override pin uses it with base_pin_trace_only: a pin never traces to itself alone, review r05). Returns
    None; the influence record {facts, engine_numbers, third_party_only} is kept on fc (fc.influence[field]) for
    score.json declared_facts and the registry's `facts` citations. Pure apart from fail(): it reads folder files
    only."""
    if not is_57_run(n):
        return None
    s = "" if text is None else str(text)
    tag = _facts.INFLUENCE_TAGS.get(field) or field
    ids = list(dict.fromkeys(fact_ids or []))
    nq = fc.not_quantities() if fc is not None else ()
    hint = ""
    if field == "tier_override_reason" and iprd_override_required(n):
        hint = (" (an unverified-share-count IPR&D override: cite the verified share count as a filing fact, the "
                "per-share charge as a calc fact, and quote the adjusted IRR from a saved run — check_quotes.py "
                f"--save-run {n.get('ticker')} <label>)")
    vals, paths = _trace_only_split(trace_only)
    if paths:
        vals = vals or _qt.ValueSet()
        for p in paths:
            vals.merge(_numeric_values(_quotes.path_value(n, p)))
    engine = _quotes.influence_sources(folder, n, facts_doc=fc.doc if fc is not None else None, exclude_paths=paths)
    res = _facts.influence_support(s, ids, fc, engine, tag, extra=_numeric_values(extra) if extra is not None else None,
                                   trace_only=vals, not_quantities=nq)
    if res.unknown:
        fail(f"judgment.json {field} cites {res.unknown[0]}, which facts.json does not declare")
    if field not in _facts.NUMBER_OPTIONAL_FIELDS and not res.carries_number:
        fail(f"judgment.json {field} carries no number — the reason must name the figure it rests on{hint}")
    if res.untraced:
        t = res.untraced[0]
        fail(f"judgment.json {field} quotes {t.raw} that is neither an engine figure nor a fact it cites — declare it "
             f"in facts.json and cite it as [F#]{hint}")
    if res.third_party_only:
        fail(f"judgment.json {field} rests only on third-party facts ({', '.join(res.facts_matched)}) — it needs an "
             "engine figure or a filing / release / folder fact (R3)")
    if res.missing_tag:
        fid = res.missing_tag[0]
        fail(f"judgment.json {field} cites {fid}, but {fid} does not list used_for {tag}")
    if require_anchor and res.numbers and not res.anchored:
        if field == "base_override":
            fail("judgment.json base_override traces only to the pinned base itself — the pin must rest on an engine "
                 "figure other than the pin, or on a cited filing / release / folder fact tagged base_override (R3: a "
                 "third-party figure is never a base override's sole support)")
        fail(f"judgment.json {field} traces only through figures that restate the measurement it answers — cite a "
             f"non-third-party fact tagged {tag} or an engine figure outside it")
    if fc is not None:
        fc.influence[field] = {"facts": ids, "engine_numbers": res.engine_numbers, "third_party_only": False}
    return None


def _run_json(cmd, env_extra=None, timeout=600):
    """Run a helper script and parse the JSON object from its stdout.
    Returns None on non-zero exit or unparseable output."""
    env = dict(os.environ)
    if env_extra:
        env.update(env_extra)
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=env)
    except Exception:
        return None
    if out.returncode != 0:
        return None
    txt = out.stdout or ""
    i = txt.find("{")
    if i < 0:
        return None
    try:
        return json.loads(txt[i:])
    except Exception:
        return None


def _run_json_rc(cmd, env_extra=None, timeout=600):
    """(exit code, parsed JSON or None). The exit code is None when the run
    could not complete (timeout, OS error) — callers that must tell "the
    script decided" from "the script failed" use this instead of _run_json."""
    env = dict(os.environ)
    if env_extra:
        env.update(env_extra)
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=env)
    except Exception:
        return None, None
    data = None
    txt = out.stdout or ""
    i = txt.find("{")
    if out.returncode == 0 and i >= 0:
        try:
            data = json.loads(txt[i:])
        except Exception:
            data = None
    return out.returncode, data


TTM_CANNOT_COMPUTE = 3   # ttm.py's exit code for "cannot compute TTM" (a missing or unfillable leg)


def _ttm_no_override_run(ticker, n):
    """[v5.5 — PR #31 verifier] ttm.py with overrides disabled: (base or None,
    built). built True: a TTM base exists without any override; False: ttm.py
    decided it cannot compute one (exit 3). Any other outcome — a crash, a
    fetch failure, a timeout, exit 2 — is not evidence either way and refuses,
    because it would otherwise read as "the tier rests on the override" and
    close an alert gate on a transient failure."""
    cik_args = ["--cik", str(n["cik"])] if n.get("cik") else []
    # DCF_TTM_NO_WRITE: these measurement runs must never clobber the worker's
    # ttm.json — the pin-provenance check compares the score's base against it.
    rc, d = _run_json_rc([sys.executable, TTM_PY, ticker] + cik_args, {"DCF_NO_OVERRIDES": "1", "DCF_TTM_NO_WRITE": "1"})
    if rc == 0 and d is not None and d.get("ttm_oe_per_share") is not None:
        return d["ttm_oe_per_share"], True
    if rc == TTM_CANNOT_COMPUTE:
        return None, False
    fail(f"ttm.py with overrides disabled did not complete (exit {rc}) — a fetch or runtime failure is not evidence "
         "that no TTM base exists without the override; cannot measure override impact, retry make_score")


def _final_run_args(n):
    """Engine CLI args replicating the final run recorded in dcf_numbers.json.
    Prefers the engine-recorded inputs block; falls back to deriving offsets
    from the recorded scenario g_starts minus the recorded g_base (verified
    to reproduce APP's final run bit-for-bit)."""
    scn = n.get("scenarios") or {}
    inp = n.get("inputs") or {}
    moat = inp.get("moat", n.get("moat_score"))
    probs = inp.get("probs") or [(scn.get(l) or {}).get("prob") for l in LABELS]
    mults = inp.get("mults") or [(scn.get(l) or {}).get("oe_mult") for l in LABELS]
    offsets = inp.get("offsets")
    if offsets is None:
        gb = n.get("g_base")
        offsets = [((scn.get(l) or {}).get("g_start") - gb)
                   if gb is not None and (scn.get(l) or {}).get("g_start") is not None else None
                   for l in LABELS]
    gterm = inp.get("g_terminal", n.get("g_terminal"))
    vals = [moat, gterm] + list(probs or []) + list(mults or []) + list(offsets or [])
    if any(v is None for v in vals):
        fail("dcf_numbers.json does not record the final run's inputs (moat/probs/offsets/mults/gterm) — "
             "cannot measure override impact; rerun the engine so it records them")
    args = ["--moat", repr(float(moat)),
            "--probs", ",".join(repr(float(p)) for p in probs),
            "--offsets", ",".join(repr(float(o)) for o in offsets),
            "--mults", ",".join(repr(float(m)) for m in mults),
            "--gterm", repr(float(gterm))]
    if n.get("price") is not None:
        args += ["--price", repr(float(n["price"]))]
    if n.get("cik"):
        args += ["--cik", str(n["cik"])]
    return args


def ttm_leg_overrides(folder, n, j_over, applied):
    """[v5.5 — Codex, PR #31] Field overrides that ttm.py used to fill a TTM
    leg (ttm.json overrides_used) when the score's base IS ttm.json's pin and
    the annual engine applied none for that field — APA: its 10-Qs print no
    SBC line, so the $107M estimate fills both YTD legs, and the TTM base the
    tier rests on exists only because of it, while dcf_numbers.json
    overrides_applied stays empty. Returns {field: record with scope
    "ttm_legs"}; such an override is reported, measured and gated like an
    applied one. Refuses when ttm.json used an override that judgment.json no
    longer declares, or declares with another value / kind (rerun ttm.py)."""
    try:
        with open(f"{folder}/ttm.json", encoding="utf-8") as f:
            tt = json.load(f)
    except Exception:
        return {}
    if not isinstance(tt, dict):
        return {}
    inp = n.get("inputs") or {}
    pinned = inp.get("base_oe_ps_arg") is not None or "ttm" in (n.get("base_source") or "").lower()
    tv, b = _num(tt.get("ttm_oe_per_share")), _num(n.get("base_oe_per_share"))
    am = _iprd_amortized_ttm(n)
    if am is not None:
        # [v5.6 review] an iprd_amortized base on native_base ttm_json IS ttm.json's TTM base less the
        # amortization: the TTM legs it rests on are compared through the record's native base
        b = _num(am.get("native_base_per_share"))
    # [Codex review r25 of PR #47] a zero TTM base too — [Codex review r26] only an exact zero (figure_matches): a
    # numeric match against ttm.json is undeclared, so it carries no half-cent band
    if not (pinned and _engine.figure_matches(b, tv)):
        return {}
    if am is None and declared_fy_built_pin(_judgment_base_override(folder), inp.get("base_oe_ps_arg")):
        return {}       # [Codex review r24 of PR #47] a pin declared built on FY figures rests on no TTM leg
    out = {}
    for u in tt.get("overrides_used") or []:
        f = u.get("field") if isinstance(u, dict) else None
        if f not in ("capex", "sbc", "shares"):
            continue
        # Every override the pinned TTM base used must be the one judgment.json
        # declares now — applied fields included (a capex_override edited after
        # ttm.py ran leaves the pin on the old value; PR #31 verifier).
        o = j_over.get(f)
        if o is None:
            fail(f"ttm.json used a {f}_override to fill TTM legs but judgment.json no longer declares one — "
                 "rerun ttm.py (and the engine with --ttm) with the current judgment.json")
        uv = _num(u.get("value"))
        if u.get("kind") != o["kind"] or uv is None or abs(float(o["value"]) - uv) > max(1.0, abs(float(o["value"])) * 0.001):
            fail(f"judgment.json {f}_override (value {o['value']}, kind {o['kind']}) disagrees with the override "
                 f"ttm.json used (value {u.get('value')}, kind {u.get('kind')}) — rerun ttm.py with the current judgment.json")
        legs = u.get("legs_filled")
        if legs is None:
            legs = {}
        ok = isinstance(legs, dict) and all(
            isinstance(v, dict) and (v.get("period") is None
                                     or (isinstance(v["period"], list) and len(v["period"]) == 2
                                         and all(isinstance(x, str) for x in v["period"])))
            for v in legs.values())
        if not ok:
            fail(f"ttm.json overrides_used.{f}.legs_filled is malformed ({str(legs)[:80]}) — rerun ttm.py")
        # [v5.5 — Codex review 2, PR #31] ttm.py's legs are USD only: at a filer the engine converted from another
        # currency (or that files USD translations), a capex / SBC override that fills TTM legs must declare
        # currency "USD" — applied fields included (a stale ttm.json can carry a converted override's raw value).
        fx_filer = bool(n.get("fx_conversion")) or any(str(fl).startswith(("FX_CONVERTED", "USD_TRANSLATIONS_USED"))
                                                       for fl in n.get("fragility_flags") or [])
        filled_any = any(isinstance(v, dict) and v.get("amount") for v in legs.values())
        if (f in ("capex", "sbc") and fx_filer and filled_any
                and str(o.get("currency") or "").strip().upper() != "USD"):
            fail(f"ttm.json used a {f}_override in its USD legs at a filer reporting in another currency, and "
                 f"judgment.json does not declare currency \"USD\" on it — ttm.py cannot convert an override; declare "
                 "the filing's US-dollar figure with currency \"USD\" (kind filing) and rerun ttm.py, or drop the TTM pin")
        if f in applied:
            continue
        out[f] = {"field": f, "value": o["value"], "kind": o["kind"], "source": o["source"], "reason": o["reason"],
                  "scope": "ttm_legs", "legs_filled": legs,
                  "periods_filled": [f"{k}: {v['period'][0]}..{v['period'][1]}" if v.get("period")
                                     else f"{k}: share count (TTM denominator)" for k, v in legs.items()]}
    return out


def _ttm_base_without_overrides(ticker, n):
    """(zero-fill TTM OE/share, built_without). Primary: ttm.py with overrides
    disabled; built_without is True when that run computes a TTM base. When
    it decides it cannot (ttm.py exit 3) — the usual case, since the filing
    gap the override covers is exactly what breaks it — reconstruct zero-fill
    from the with-override run (any other failure refuses, _ttm_no_override_run):
    remove each filled leg's contribution with TTM signs (FY - prior YTD +
    current YTD) from the OE total, and built_without is False (no TTM base
    exists without the override)."""
    cik_args = ["--cik", str(n["cik"])] if n.get("cik") else []
    base0, built = _ttm_no_override_run(ticker, n)
    if built:
        return base0, True
    d = _run_json([sys.executable, TTM_PY, ticker] + cik_args, {"DCF_TTM_NO_WRITE": "1"})
    if d is None or d.get("ttm_oe_per_share") is None or d.get("ttm_oe_total") is None:
        fail("cannot compute the no-override TTM base for the override impact (ttm.py failed with and without overrides)")
    used = {u.get("field"): u for u in d.get("overrides_used") or []}
    if "shares" in used:
        # No zero-fill denominator exists for shares: without the override
        # there is no TTM base at all. Signal "no counterfactual" (None);
        # the caller records a null impact with unblocks_tier set.
        return None, False
    oe_total = d["ttm_oe_total"]
    for field in ("capex", "sbc"):
        legs = (used.get(field) or {}).get("legs_filled") or {}
        oe_total += (legs.get("fy") or {}).get("amount", 0.0) \
                  - (legs.get("ytd_prior") or {}).get("amount", 0.0) \
                  + (legs.get("ytd_current") or {}).get("amount", 0.0)
    shares = d.get("ttm_shares_diluted")
    if not shares:
        fail("ttm.py returned no TTM share count — cannot measure override impact")
    return oe_total / shares, False


def payable_pin_impact(ticker, n):
    """The payable override's own measured impact: the engine-native base
    (median of the last 3 FY, field overrides on) and its weighted IRR, versus
    the pinned payable base the score used. Replays the final configuration
    without the pin; a failed replay refuses the score like any other
    measurement failure."""
    args = _final_run_args(n)
    m = _run_json([sys.executable, ENGINE, ticker, "--measure"] + args)
    if m is None:
        fail("native-base replay failed — cannot measure the payable base override's impact")
    bw, iw = m.get("base_oe_per_share"), m.get("implied_irr_weighted")
    bp, ip = n.get("base_oe_per_share"), n.get("implied_irr_weighted")
    pct = round((bp - bw) / bw * 100, 3) if isinstance(bp, (int, float)) and isinstance(bw, (int, float)) and bw else None
    pp = round((ip - iw) * 100, 3) if isinstance(ip, (int, float)) and isinstance(iw, (int, float)) else None
    return {"base_used": "payable_5y",
            "base_oe_without_override": round(bw, 4) if isinstance(bw, (int, float)) else None,
            "base_oe_with_override": round(bp, 4) if isinstance(bp, (int, float)) else None,
            "base_oe_impact_pct": pct,
            "weighted_irr_without_override": round(iw, 4) if isinstance(iw, (int, float)) else None,
            "weighted_irr_with_override": round(ip, 4) if isinstance(ip, (int, float)) else None,
            "weighted_irr_impact_pp": pp,
            "tier_by_numbers_without_override": m.get("tier_by_numbers"),
            "tier_by_numbers_with_override": n.get("tier_by_numbers")}


def _iprd_amortized_record(n):
    """The engine's amortized record (iprd_adjustment.amortized) when the run carried an iprd_amortized base, else None."""
    blk = n.get("iprd_adjustment") if isinstance(n.get("iprd_adjustment"), dict) else None
    am = (blk or {}).get("amortized")
    return am if (blk and blk.get("treatment") == "amortized_in_base" and isinstance(am, dict)) else None


IPRD_AMORTIZED_IMPACT_KEYS = ("weighted_irr_without_override", "weighted_irr_impact_pp",
                              "tier_by_numbers_without_override", "tier_by_numbers_with_override",
                              "iprd_treatment_without_override", "iprd_charge_per_share_without_override")


def iprd_amortized_impact(ticker, n):
    """[Codex review r2 of PR #47] The iprd_amortized base_override's own measured impact (registry event): without
    the override the run scores its NATIVE base and takes the one-time value deduction, so the final run's inputs
    and field overrides are replayed without the pin — `--ttm` for native base ttm_json (make_score has already
    refused a ttm.json that changed after the run), no pin for the median — and its weighted IRR, tier, treatment
    and charge are recorded beside the run's own (payable_pin_impact's shape). The replay's base must be the
    record's native base (0.1%); a failed replay refuses the score like any other measurement failure."""
    am = _iprd_amortized_record(n)
    args = _final_run_args(n) + (["--ttm"] if am.get("native_base") == "ttm_json" else [])
    m = _run_json([sys.executable, ENGINE, ticker, "--measure"] + args)
    if m is None:
        fail("one-time-deduction replay failed — cannot measure the iprd_amortized base override's impact")
    bw, nb = _num(m.get("base_oe_per_share")), _num(am.get("native_base_per_share"))
    if not _engine.figure_matches(bw, nb):    # [Codex review r26 of PR #47] engine output against engine output
        fail(f"the one-time-deduction replay scored base {bw!r}, not the amortized record's native base {nb!r} — "
             "cannot measure the iprd_amortized base override's impact; re-run the engine")
    iw, ip = _num(m.get("implied_irr_weighted")), _num(n.get("implied_irr_weighted"))
    mb = m.get("iprd_adjustment") if isinstance(m.get("iprd_adjustment"), dict) else {}
    return {"weighted_irr_without_override": round(iw, 4) if iw is not None else None,
            "weighted_irr_impact_pp": round((ip - iw) * 100, 3) if (ip is not None and iw is not None) else None,
            "tier_by_numbers_without_override": m.get("tier_by_numbers"),
            "tier_by_numbers_with_override": n.get("tier_by_numbers"),
            "iprd_treatment_without_override": mb.get("treatment"),
            "iprd_charge_per_share_without_override": round(_engine.iprd_charge_per_share(m), 4)}


def iprd_amortized_not_measured(n, note):
    """The amortized event's counterfactual fields, null, with why they were not measured."""
    out = {k: None for k in IPRD_AMORTIZED_IMPACT_KEYS}
    out.update({"tier_by_numbers_with_override": n.get("tier_by_numbers"), "counterfactual_note": note})
    return out


def declared_fy_built_pin(bo, pin):
    """[Codex review r24 of PR #47] True when judgment.json base_override `bo` declares the pin `pin` (its value within
    0.1%) and says the pin was built on FY figures: basis iprd_amortized on native_base
    median_of_last_3_fy_oe_per_share, or no basis with basis_window {"window": "fy"}. Such a pin is never ttm.json's
    pin, even when it equals ttm_oe_per_share within 0.1% — the engine reads the IPR&D window and share denominator
    from the declaration (the FY window, the latest FY count), and so do the base-pin provenance check, the
    override-impact branch and the TTM-leg override rules here."""
    # [Codex review r25] zero too; [Codex review r26] at a half cent only for the iprd_amortized arithmetic
    if not _engine.declared_value_matches(bo, pin):
        return False
    if bo.get("basis") == IPRD_AMORTIZED_BASIS:
        return bo.get("native_base") == "median_of_last_3_fy_oe_per_share"
    bw = bo.get("basis_window")
    return bo.get("basis") is None and isinstance(bw, dict) and bw.get("window") == "fy"


def _judgment_base_override(folder):
    try:
        with open(f"{folder}/judgment.json", encoding="utf-8") as f:
            bo = (json.load(f) or {}).get("base_override")
    except Exception:
        return None
    return bo if isinstance(bo, dict) else None


def _declared_pin_not_ttm(ticker, n):
    """[v5.5] True when the final run's --base-oe-ps pin equals a declared
    base_override without `basis`, or (v5.6) of basis iprd_amortized on the
    median native base (within 0.1%), and does NOT equal ttm.json's
    ttm_oe_per_share (within 0.1%): a pin built from engine outputs (NTNX /
    TEM / VIV), whose override impact is measured with the pin held constant,
    not by re-running ttm.py. An iprd_amortized pin on native_base ttm_json is
    measured on the TTM branch instead (False). [Codex review r24 of PR #47] A
    pin its declaration says was built on FY figures (declared_fy_built_pin)
    is a declared pin even when it equals ttm.json's figure (True)."""
    inp = n.get("inputs") or {}
    pin = inp.get("base_oe_ps_arg")
    if inp.get("base_pin_source") != "base_oe_ps_arg" or not isinstance(pin, (int, float)) or isinstance(pin, bool):
        return False    # [Codex review r25 of PR #47] a zero pin (a $0.00 amortized base) is a pin like any other
    try:
        with open(f"{BASE}/{ticker}/judgment.json", encoding="utf-8") as f:
            bo = (json.load(f) or {}).get("base_override")
    except Exception:
        return False
    if (not isinstance(bo, dict) or bo.get("basis") not in (None, IPRD_AMORTIZED_BASIS)
            or not _engine.declared_value_matches(bo, pin)):    # [Codex review r26 of PR #47]
        return False
    if bo.get("basis") == IPRD_AMORTIZED_BASIS and _iprd_amortized_ttm(n) is not None:
        return False    # [v5.6 review] ttm.json's TTM base less the amortization: measured on the TTM branch
    if declared_fy_built_pin(bo, pin):
        return True     # [Codex review r24 of PR #47] built on FY figures: never the TTM branch, whatever ttm.json holds
    try:
        with open(f"{BASE}/{ticker}/ttm.json", encoding="utf-8") as f:
            tv = json.load(f).get("ttm_oe_per_share")
        if _engine.figure_matches(pin, tv):    # [Codex review r26 of PR #47] undeclared: a zero only exactly
            return False
    except Exception:
        pass
    return True


# ---------------------------------------------------------------------------
# v5.7 lane L4 (R2 foreign filers, Andrew 2026-10-19) — L0 placeholders, no-ops until L4 fills them
# ---------------------------------------------------------------------------
def annual_instance_check(folder, n):
    """v5.7 placeholder (L4, R2b; 07 §1.12 step 1, after the content-hash check): when the run read annual facts
    from the filing's own XBRL instance, <T>/annual_instance.json must be that instance's. None in L0."""
    return None


def interim_pin_state(folder, n, j, tt):
    """v5.7 placeholder (L4, R2a; step 3, after check_ttm_inputs_current): the declared 6-K interim bridge's state
    against ttm.json (tt) and the run's pin. None in L0."""
    return None


def check_interim_obligation(n, j, interim, plan=None):
    """v5.7 placeholder (L4, R2a): a 5.7 STALE_FY 20-F / 40-F run declares interim_bridge or interim_bridge_declined
    (plan: R7's ttm_rejection_state, a declared bridge may be rejected). No-op in L0."""
    return None


def interim_bridge_measurement(ticker, n, interim, release_mismatch, prior_score=None):
    """v5.7 placeholder (L4; step 4, after the override impact): the bridged vs annual-median measurement (R7 folds
    its figures into build_base_alternatives). None in L0."""
    return None


def score_interim_fields(score, n, j, interim, interim_meas):
    """v5.7 placeholder (L4): score.json interim_bridge / interim_bridge_declined and the TTM_DECLARED_INTERIM flag.
    No-op in L0."""
    return None


# ---------------------------------------------------------------------------
# v5.7 lane R7 (STALE_FY discretion made checkable, Andrew 2026-10-19) — L0 placeholders, no-ops until R7 fills them
# ---------------------------------------------------------------------------
def ttm_rejection_state(folder, n, j, j_sc=None, interim=None, j_over=None):
    """v5.7 placeholder (R7; step 3, after interim_pin_state): the plan — whether the run must carry a qualifying
    judgment.json ttm_rejection_reason (STALE_FY, a published base that is not the TTM, a TTM for this run), and
    the refusals when it does not. None on pre-5.7 output and in L0."""
    return None


def _alt_ttm_ok(ttm, j_sc):
    """v5.7 gate hook (L8 / R7, 08 §8.9): a ttm.json alternative is priced only when it is on the share_classes
    declaration (_sc.ttm_on_declaration). True in L0."""
    return True


def build_base_alternatives(ticker, folder, n, j, plan, impact=None, payable_impact=None, amortized_impact=None,
                            release_mismatch=False, prior_score=None, j_sc=None, interim_meas=None):
    """v5.7 placeholder (R7; step 4, after the amortized impact): score.json base_alternatives — the published base
    beside every other base computed for the run (annual median, TTM, declared-interim TTM: base OE/share, weighted
    IRR, tier, role, why), one record shared with L4's bridge measurement (interim_meas) and gated per ttm.json
    alternative by _alt_ttm_ok(ttm, j_sc). None on pre-5.7 output and in L0 (no key written)."""
    return None


def compute_override_impact(ticker, n, ttm_only=None):
    """The impact block, on Andrew's basis: the base the final run actually
    used, the final run's exact configuration, toggling only the overrides.
    Returns the block stored in score.json (override_impact) and the registry.
    [v5.5 — Codex, PR #31] ttm_only (ttm_leg_overrides): on a TTM pin whose
    legs an override fills, unblocks_tier is also true when ttm.py cannot
    build the TTM base without the override — the pinned base, and so the
    tier, exists only because of it (APA)."""
    base_with = n.get("base_oe_per_share")
    irr_with = n.get("implied_irr_weighted")
    gaps = list(n.get("data_gap") or [])
    unblocks = bool(gaps) and not (n.get("data_gap_uncovered") or [])
    base_src = (n.get("base_source") or "").lower()
    pin_src = (n.get("inputs") or {}).get("base_pin_source")
    pinned = (n.get("inputs") or {}).get("base_oe_ps_arg") is not None or "ttm" in base_src
    base_used = "payable_5y" if (pin_src == "judgment_base_override" or n.get("payable_base")) \
        else "declared_pin" if _declared_pin_not_ttm(ticker, n) \
        else "ttm" if pinned else "median_3y"
    args = _final_run_args(n)
    if base_used in ("payable_5y", "declared_pin"):
        # The base is pinned to a declared figure in both worlds (field
        # overrides fill OCF/capex/SBC/share history, never the pin), so the
        # base impact is zero by construction; the IRR counterfactual replays
        # the same pin with the field overrides off, since they can still move
        # the growth blend. A gate firing in the replay (the override covers
        # the only capex history, as at RNR; or a filing shares_override covers
        # a basic-only year, as at VIV) is an honest "no counterfactual" when
        # the override unblocks the tier. [v5.5] "declared_pin" is a
        # --base-oe-ps pin that equals a declared base_override (no basis) and
        # is NOT ttm.json's figure: before 5.5 it fell into the TTM branch,
        # which re-ran ttm.py, but a pin built from engine outputs is not a TTM
        # figure, and at an IFRS filer ttm.py cannot run at all (VIV).
        base_without = base_with
        m = _run_json([sys.executable, ENGINE, ticker, "--measure"] + args
                      + ["--base-oe-ps", repr(float(base_with))],
                      # [v5.6 review] a declared pin holds the final run's IPR&D treatment and charge (an
                      # iprd_amortized one stays amortized_in_base); [Codex review r1 of PR #47] so does the payable
                      # pin: a shares_override can move the FY share denominator, and the charge is mechanical
                      {"DCF_NO_OVERRIDES": "1", "DCF_IPRD_HOLD": _iprd_hold(n)})
        if m is None:
            fail("counterfactual engine --measure run failed — cannot measure override impact on the " + ("payable" if base_used == "payable_5y" else "declared pinned") + " base")
        if m.get("implied_irr_weighted") is None:
            if unblocks and (m.get("data_gap") or []):
                base_without = None      # gate fired: honestly no counterfactual
                irr_without = None
            elif irr_with is None and not (m.get("data_gap") or []):
                irr_without = None       # Tier F on the pin in both worlds: null IRR impact, zero base impact
            else:
                fail("counterfactual run produced no IRR and no data gap — cannot measure override impact on the " + ("payable" if base_used == "payable_5y" else "declared pinned") + " base")
        else:
            irr_without = m.get("implied_irr_weighted")
    elif base_used == "ttm":
        base_without, built_without = _ttm_base_without_overrides(ticker, n)
        if ttm_only and not built_without:
            unblocks = True
        am = _iprd_amortized_ttm(n)
        if am is not None and base_without is not None:
            # [v5.6 review] the amortized TTM base: the no-override TTM base less the same amortization per share
            base_without = base_without - (float(am["native_base_per_share"]) - float(am["pinned_per_share"]))
        if base_without is None:
            if not unblocks:
                fail("no no-override TTM base exists but the override covers no data gap — cannot measure override impact")
            irr_without = None
        else:
            # [v5.6 review] DCF_IPRD_HOLD: the --base-oe-ps replay would otherwise read the FY window and the
            # latest FY share count, not the --ttm run's current-YTD leg and ttm_shares_diluted
            m = _run_json([sys.executable, ENGINE, ticker, "--measure"] + args
                          + ["--base-oe-ps", repr(float(base_without))],
                          {"DCF_NO_OVERRIDES": "1", "DCF_IPRD_HOLD": _iprd_hold(n)})
            if m is None:
                fail("counterfactual engine --measure run failed — cannot measure override impact on the TTM base")
            irr_without = m.get("implied_irr_weighted")
    else:
        # [Codex review r1 of PR #47] DCF_IPRD_HOLD here too: a shares_override that fills the latest FY diluted
        # count moves the replay's IPR&D share denominator, so without the hold the measured impact mixed the
        # override's effect with a re-detected charge
        m = _run_json([sys.executable, ENGINE, ticker, "--measure"] + args,
                      {"DCF_NO_OVERRIDES": "1", "DCF_IPRD_HOLD": _iprd_hold(n)})
        if m is None:
            # v5.3.1 (Codex review of Stocks PR #1): a FAILED replay (timeout,
            # non-zero exit, malformed output) is not evidence that no
            # counterfactual exists — v5.3 recorded null impact and scored
            # anyway whenever the override unblocked a gap. Fail hard, like
            # the TTM branch above.
            fail("counterfactual engine --measure run failed — cannot measure override impact on the median base")
        if m.get("base_oe_per_share") is None:
            if not (unblocks and (m.get("data_gap") or [])):
                fail("counterfactual run produced no base and no data gap — cannot measure override impact on the median base")
            # The replay ran and the gate fired: without the override there
            # is no base at all, so the impact is honestly unmeasurable —
            # record nulls; unblocks_tier carries the information.
            base_without = None
            irr_without = None
        else:
            base_without = m["base_oe_per_share"]
            irr_without = m.get("implied_irr_weighted")
    base_pct = round((base_with - base_without) / base_without * 100, 3) \
        if isinstance(base_with, (int, float)) and base_without else None
    irr_pp = round((irr_with - irr_without) * 100, 3) \
        if isinstance(irr_with, (int, float)) and isinstance(irr_without, (int, float)) else None
    return {"base_used": base_used,
            "base_oe_without_override": round(base_without, 4) if isinstance(base_without, (int, float)) else None,
            "base_oe_with_override": round(base_with, 4) if isinstance(base_with, (int, float)) else None,
            "base_oe_impact_pct": base_pct,
            "weighted_irr_without_override": round(irr_without, 4) if isinstance(irr_without, (int, float)) else None,
            "weighted_irr_with_override": round(irr_with, 4) if isinstance(irr_with, (int, float)) else None,
            "weighted_irr_impact_pp": irr_pp,
            "unblocks_tier": unblocks}


def _default_cik(ticker):
    """The CIK the tickers-exchange mapping assigns (what the engine uses
    unless a --cik override or the CIK-fallback probe intervened)."""
    try:
        sec = json.load(open(f"{SYS_DIR}/sec_tickers_exchange.json", encoding="utf-8"))
        m = {}
        for rec in sec["data"]:
            m.setdefault(rec[2].upper(), rec[0])
        for cand in (ticker, ticker.replace("/", "-"), ticker.replace("/", ".")):
            if cand in m:
                return m[cand]
    except Exception:
        pass
    return None


def base_override_event_applies(j, n):
    """True when this run records a base_override registry event: judgment.json
    declares one and the final run was pinned (--base-oe-ps / --ttm /
    --base-judgment)."""
    return bool(j.get("base_override")) and ((n.get("inputs") or {}).get("base_oe_ps_arg") is not None
                                            or "ttm" in (n.get("base_source") or "").lower())


def pin_rescued(n):
    """[v5.5 — re-score audit] True when the final run's tier exists only
    because a declared base_override pin rescued a share-scale defect
    (dcf_numbers.json share_scale.rescued_by_pin): without the pin the engine
    gaps DATA_GAP:shares — SHARE_SCALE, so the tier rests on a judgment
    override exactly as when a field override covers a data gap. Both alert
    gates treat it as unblocks_tier (NTNX, TEM, VIV)."""
    ss = n.get("share_scale")
    return isinstance(ss, dict) and ss.get("rescued_by_pin") is True


def pin_rescue_impact(n):
    """[v5.5 — re-score audit] The base_override registry event's measured
    impact on a share-scale rescue, from the final run's own record (nothing
    is replayed): the engine's median on the defective share basis
    (base_oe_normalized_per_share) without the pin, the pin with it; no IRR
    exists without the pin (the run gaps), so unblocks_tier is true."""
    ss = n.get("share_scale") or {}
    native, pinned, irr = (_num(n.get("base_oe_normalized_per_share")), _num(n.get("base_oe_per_share")),
                           _num(n.get("implied_irr_weighted")))
    reasons = "; ".join(str(r) for r in (ss.get("reasons") or [])) or "share-scale defect"
    return {"base_used": "declared_pin",
            "base_oe_without_override": round(native, 4) if native is not None else None,
            "base_oe_with_override": round(pinned, 4) if pinned is not None else None,
            "base_oe_impact_pct": None,
            "weighted_irr_without_override": None,
            "weighted_irr_with_override": round(irr, 4) if irr is not None else None,
            "weighted_irr_impact_pp": None,
            "unblocks_tier": True,
            "impact_note": ("share-scale rescue: without the pin the run gaps (DATA_GAP:shares — SHARE_SCALE: "
                            + reasons + "), so no IRR exists without it; base_oe_without_override is the "
                            "engine's own median on the defective share basis")}


# The fields that identify one declaration per registry entry type: an entry
# whose declaration is unchanged keeps the date it was first recorded (the
# measured impact fields are re-derived every run). [Codex, PR #31] Every
# material field is part of the identity: a field override's `currency`
# (declared USD is used verbatim instead of FX-converted) and `scope`
# (annual run vs ttm.py legs only), and a base_override's `kind` and payable
# shape (`basis`, `figures`, `shares`). One legacy allowance: registry events
# written before 5.5 never recorded a base_override's `kind`, so a prior
# event WITHOUT the key is compared on the other fields only (its kind is
# unknown, not different); once an event records `kind`, a change re-dates.
# [Codex review r15 of PR #47] A plain base_override's `basis_window` (the
# window its pin was built on, which sets the acquired-IPR&D window) is part of
# the identity too, with the same legacy allowance: an event recorded before
# round 15 carries no `basis_window` key and is compared on the other fields.
# v5.7 (L0, 07 §1.11 — every key at once): the event types the 5.7 lanes write are declared before any run writes
# one, since _EVENT_DECLARATION is also the whitelist load_registry / registry_entry_problem apply to every entry
# (an unknown event refuses the WHOLE registry). The keys added to existing identities (tier_override / base_override
# `facts`, base_override `share_basis` / `share_period`, a field override's `software_included`) are carried by no
# recorded entry: json null on both sides of keep_first_dates, so nothing is re-dated. None of these events may use
# an IPRD_DEFERRED_EVENT_KEYS name.
_FIELD_DECLARATION = ("value", "kind", "source", "reason", "currency", "scope",
                      "software_included")                                          # L9 (R9)
_EVENT_DECLARATION = {"tier_override": ("tier_by_numbers", "tier_final", "reason",
                                        "facts"),                                   # L2 (R3): cited facts
                      "manual_price": ("value",),
                      "base_override": ("value", "kind", "source", "reason", "basis", "figures", "shares", "native_base",
                                        "basis_window",
                                        "share_basis", "share_period",              # L8 (R6)
                                        "facts"),                                   # L2 (R3): cited facts
                      "gterm": ("value",), "cik": ("value",), "ads_ratio": ("ratio", "source", "reason"),
                      "scope_correction": ("old_cap", "new_cap", "in_scope"),
                      "iprd_deferred_payment": ("deal", "first_charged_period", "contingent_total", "paid_to_date",
                                                "periods"),
                      # ---- v5.7 (2026-10-19 rulings): written by the lanes, declared here first ----
                      "misfit_notch": ("tier_by_numbers", "tier_final", "reason"),          # L1 (R1)
                      "declared_facts": ("facts_sha256",),                                  # L2 (R3)
                      "moat_divergence": ("moat_score", "reason"),                          # L3 (R4)
                      "moat_low_roic": ("moat_score", "reason"),                            # L3
                      "moat_high_return_low_moat": ("moat_score", "reason"),                # L3
                      "moat_erosion_rebuttal": ("moat_score", "reason"),                    # L3 / L3b
                      "moat_widening_declined": ("moat_score", "reason"),                   # L3b (M6)
                      "interim_bridge": ("declaration_hash",),                              # L4 (R2a)
                      "interim_bridge_declined": ("reason",),                               # L4
                      "share_classes": ("basis", "declaration_sha256"),                     # L8 (R6)
                      "up_c_suspect": ("reason",),                                          # L8
                      "capex_unlisted_ack": ("tag", "reason"),                              # L9 (R8)
                      "base_alternatives": ("chosen", "reason", "ttm_kind", "ttm_fy_end", "ttm_ytd_end")}   # R7


def _declaration(e, ignore=()):
    if e.get("field"):
        keys, head = _FIELD_DECLARATION, ("field", e.get("field"))
    else:
        keys, head = _EVENT_DECLARATION.get(e.get("event"), ()), ("event", e.get("event"))
    return head + tuple(json.dumps(e.get(k), sort_keys=True, default=str) for k in keys if k not in ignore)


# keys a base_override event recorded before they existed lacks (kind: before 5.5; basis_window: before round 15)
_LEGACY_BASE_OVERRIDE_KEYS = ("kind", "basis_window")


def keep_first_dates(new_entries, prior_entries):
    """[v5.5 — re-score audit] Set each new entry's `date` to the earliest
    date a prior entry of this ticker recorded for the SAME declaration
    (_declaration); a new or changed declaration keeps today's date. Before
    this, every make_score run re-dated every entry of the ticker (the
    wholesale replace stamped `today`), so a re-score rewrote when an override
    or an ads_ratio was first taken (NTNX's 2026-10-15 base_override and WF's
    2026-10-16 ads_ratio read 2026-10-19 after the engine 5.5 re-score)."""
    first, legacy = {}, {}
    for e in prior_entries:
        d = e.get("date")
        if isinstance(d, str) and d:
            k = _declaration(e)
            first[k] = min(first.get(k, d), d)
            ig = tuple(x for x in _LEGACY_BASE_OVERRIDE_KEYS if x not in e)
            if e.get("event") == "base_override" and ig:
                lk = (ig, _declaration(e, ignore=ig))
                legacy[lk] = min(legacy.get(lk, d), d)
            if e.get("event") == "tier_override":
                # v5.7 (L1, R1): a legacy one-notch tier_override is the same judgment as the misfit_notch event that
                # replaces it (same tiers, same reason) — that event keeps the date the notch was first taken. The old
                # event recorded the reason raw, misfit_notch records it stripped (misfit_notch), so the cross-index
                # strips it too: surrounding whitespace never re-dates a legacy notch (review of d9618aa)
                r = e.get("reason")
                nk = _declaration(dict(e, event="misfit_notch", reason=r.strip() if isinstance(r, str) else r))
                first[nk] = min(first.get(nk, d), d)
    for e in new_entries:
        d = first.get(_declaration(e))
        if d is None and e.get("event") == "base_override":
            hits = [legacy[(ig, _declaration(e, ignore=ig))] for ig in {k[0] for k in legacy}
                    if (ig, _declaration(e, ignore=ig)) in legacy]
            d = min(hits) if hits else None
        if d and (not isinstance(e.get("date"), str) or d < e["date"]):
            e["date"] = d


# v5.7 (L0, 07 §1.11): each lane's registry events, appended by update_registry in this fixed order after the
# deferred-payment events and before keep_first_dates. Pure — they run under the registry lock (lock_held), so no
# file read, no lock, no fail(). [] (or nothing) until the lane fills them.
def _notch_events(ticker, today, notch, n):
    """v5.7 (L1, R1): the misfit_notch event when the notch applies — {ticker, event, date, tier_by_numbers,
    tier_final (the notched tier), weighted_irr (4 dp), reason, reason_source, basis (the detection source)}; its
    declaration (_EVENT_DECLARATION) is tier_by_numbers / tier_final / reason. A block the notch could not be applied
    to (D / F / payable_base) records no event: score.json and key_numbers.md carry its reason. Pure."""
    if not isinstance(notch, dict) or not notch.get("applies"):
        return []
    irr = _num((n or {}).get("implied_irr_weighted"))
    return [{"ticker": ticker, "event": "misfit_notch", "date": today,
             "tier_by_numbers": notch.get("tier_by_numbers"), "tier_final": notch.get("tier_after_notch"),
             "weighted_irr": round(irr, 4) if irr is not None else None,
             "reason": notch.get("reason"), "reason_source": notch.get("reason_source"),
             "basis": (notch.get("basis") or {}).get("source")}]


def _moat_events(ticker, today, moat_ev):
    """v5.7 placeholder (L3 / L3b, R4 / M6): the moat_* events. [] in L0."""
    return []


def _interim_events(ticker, interim, declined, today):
    """v5.7 placeholder (L4, R2a): interim_bridge / interim_bridge_declined. [] in L0."""
    return []


def _facts_events(ticker, today, facts_check):
    """v5.7 (L2, R3; 02 §5): one declared_facts event per run with a facts.json — {ticker, event, date,
    facts_sha256, count, by_kind, influencing (the ids any influence field cites)}. Its identity
    (_EVENT_DECLARATION) is facts_sha256 alone, so an unchanged declaration keeps its first date. None of its keys
    is an iprd_deferred_payment field name (rebase I5)."""
    if facts_check is None:
        return []
    by_kind = {}
    for f in facts_check.facts:
        by_kind[f.get("kind")] = by_kind.get(f.get("kind"), 0) + 1
    influencing = sorted({i for rec in facts_check.influence.values() for i in rec.get("facts") or []},
                         key=lambda x: int(x[1:]) if x[1:].isdigit() else 0)
    return [{"ticker": ticker, "event": "declared_facts", "date": today, "facts_sha256": facts_check.sha,
             "count": len(facts_check.facts), "by_kind": by_kind, "influencing": influencing}]


def _share_classes_events(ticker, share_classes, up_c, n, j):
    """v5.7 placeholder (L8, R6): share_classes / up_c_suspect (the per-period map is `units_by_period`, never
    `periods`). [] in L0."""
    return []


def _base_alternatives_events(ticker, base_alts, today):
    """v5.7 placeholder (R7): the base_alternatives event (a rejected STALE_FY TTM, or a published 6-K bridge). []
    in L0."""
    return []


def _capex_events(ticker, today, unlisted_acks, n):
    """v5.7 placeholder (L9, R8): one capex_unlisted_ack event per acknowledged CAPEX_UNLISTED_COMPONENT tag. [] in
    L0."""
    return []


def _attach_fact_citations(entries, facts_check):
    """v5.7 (L2, R3; 02 §5, rebase A6): a post-pass over this run's new entries — `facts: [{id, kind, value, unit,
    period, source}]` on the tier_override / base_override event whose reason cites facts (the influence record
    check_influence kept on the facts check). Only then: an absent key and None compare equal in keep_first_dates,
    an empty list does not, so a legacy event is never re-dated. Touches no other event (the iprd_deferred_payment
    events sit in the same slice)."""
    if facts_check is None:
        return None
    field_of = {"tier_override": "tier_override_reason", "base_override": "base_override"}
    for e in entries:
        fld = field_of.get(e.get("event"))
        ids = ((facts_check.influence.get(fld) or {}).get("facts") or []) if fld else []
        if ids:
            e["facts"] = facts_check.cited_records(ids)
    return None


def update_registry(ticker, applied, j_over, impact, j, n, scope_event=None, payable_impact=None, amortized_impact=None,
                    deferred_events=None, lock_held=False, notch=None, override_in_force=None, facts_check=None,
                    moat_ev=None, interim=None, declined=None, share_classes=None, up_c=None, unlisted_acks=None,
                    base_alts=None):
    """Replace this ticker's registry entries wholesale on every score
    (round-2: the old upsert only replaced fields still applied, so a
    removed override's entry went stale and stayed forever). Records the
    applied field overrides (schema unchanged: value/kind/source/reason +
    final-base impact + unblocks_tier) AND every other judgment call the
    run embodies, each as its own entry with "event": tier_override (with
    reason), manual_price, base_override, gterm (non-default), cik
    (non-default / fallback), ads_ratio, and (v5.5) scope_correction
    {old_cap, new_cap, in_scope} when the pre-5.5 ADS market-cap correction
    decided the scope. A payable-earnings base_override event carries
    `payable_impact` — measured (payable_pin_impact) or carried / not measured
    (carried_payable_impact) by main() BEFORE any write (M3); nothing is
    spawned here. [v5.5 — re-score audit] The base_override event records the
    declaration's `kind` and, on a share-scale rescue (pin_rescued), the pin's
    impact (pin_rescue_impact); an entry whose declaration is unchanged keeps
    the date it was first recorded (keep_first_dates). [Codex review r2 of
    PR #47] An iprd_amortized base_override event carries `amortized_impact`
    (iprd_amortized_impact: the one-time-deduction replay's IRR, tier,
    treatment and charge, measured by main() before any write), or those
    fields null with counterfactual_note. [Codex review r8 of PR #47]
    deferred_events: one iprd_deferred_payment event per deal
    (iprd_deferred_lifetime, checked by main() against the carried prior
    events before any write) — the deal's every declared period and
    paid_to_date, so deleting a judgment.json entry never erases a paid
    milestone (and, Codex review r10, a recorded period's amount is never
    rewritten). make_score.py is the single writer; the write is atomic under
    an fcntl lock ([Codex review r21 of PR #47] tmp + _stable._replace; a
    failed replace is refused). [Codex review r19 of PR #47] lock_held: main() already holds
    it (registry_transaction, where deferred_events were validated against the
    registry read under that same lock); the lock is not re-entrant, so it is
    not taken again. v5.7 (L0): one keyword per lane after lock_held (notch,
    override_in_force: L1; facts_check: L2; moat_ev: L3 / L3b; interim,
    declined: L4; share_classes (the measured block, main()'s sc_impact),
    up_c: L8; unlisted_acks: L9; base_alts: R7), each lane's events
    appended in a fixed order (_notch_events …
    _capex_events, then _attach_fact_citations) before keep_first_dates —
    none yet."""
    today = datetime.datetime.now(ZoneInfo("America/New_York")).date().isoformat()
    with (contextlib.nullcontext() if lock_held else locked(REGISTRY + ".lock")):
        # [Codex review r26 of PR #47] a fresh registry only when the file does not exist: an unreadable or malformed
        # one is refused (load_registry), never rewritten from an empty default
        reg = load_registry()
        if reg is None:
            reg = {"entries": []}
        prior = [e for e in reg["entries"] if e.get("ticker") == ticker]
        entries = [e for e in reg["entries"] if e.get("ticker") != ticker]
        n_kept = len(entries)
        for field in ("capex", "sbc", "shares"):
            if field in applied:
                a = applied[field]
                ent = {"ticker": ticker, "field": field, "value": a["value"],
                       "kind": a["kind"], "source": a["source"],
                       "reason": j_over[field]["reason"], "date": today}
                if j_over[field].get("currency") is not None:
                    ent["currency"] = j_over[field]["currency"]
                if a.get("scope"):
                    ent["scope"] = a["scope"]
                entries.append(dict(ent, **{
                                "base_used": impact["base_used"],
                                "base_oe_without_override": impact["base_oe_without_override"],
                                "base_oe_with_override": impact["base_oe_with_override"],
                                "base_oe_impact_pct": impact["base_oe_impact_pct"],
                                "weighted_irr_without_override": impact["weighted_irr_without_override"],
                                "weighted_irr_with_override": impact["weighted_irr_with_override"],
                                "weighted_irr_impact_pp": impact["weighted_irr_impact_pp"],
                                "unblocks_tier": impact["unblocks_tier"]}))
        # v5.7 (L1, R1): only an override in force (override_in_force None = every pre-5.7 caller: as before); a
        # legacy one-notch override is recorded as the misfit_notch event (_notch_events) instead
        if j.get("tier_override") and (override_in_force is None or override_in_force):
            entries.append({"ticker": ticker, "event": "tier_override", "date": today,
                            "tier_by_numbers": n.get("tier_by_numbers"),
                            "tier_final": j["tier_override"],
                            "reason": j.get("tier_override_reason")})
        if n.get("price_source") == "manual":
            entries.append({"ticker": ticker, "event": "manual_price", "date": today,
                            "value": n.get("price")})
        bo = j.get("base_override")
        if base_override_event_applies(j, n):
            ev = {"ticker": ticker, "event": "base_override", "date": today,
                  "value": bo["value"], "source": bo["source"], "reason": bo["reason"]}
            if bo.get("kind") is not None:
                ev["kind"] = bo["kind"]
            if bo.get("basis_window") is not None:
                ev["basis_window"] = bo["basis_window"]   # [Codex review r15 of PR #47]
            if pin_rescued(n) and not n.get("payable_base"):
                ev.update(pin_rescue_impact(n))
            _am = (n.get("iprd_adjustment") or {}).get("amortized") if isinstance(n.get("iprd_adjustment"), dict) else None
            if bo.get("basis") == IPRD_AMORTIZED_BASIS and isinstance(_am, dict):
                # v5.6: the amortized acquired-IPR&D base — the declaration and the native -> pinned base from the
                # run's own record; [Codex review r2 of PR #47] the IRR / tier without it are the one-time path's,
                # replayed by main() (iprd_amortized_impact) before any write, or null with the reason
                nb, pb_ = _num(_am.get("native_base_per_share")), _num(_am.get("pinned_per_share"))
                ev.update({"basis": bo.get("basis"), "figures": bo.get("figures"), "shares": bo.get("shares"),
                           # [fixer review round] the branch compute_override_impact measures it on: "ttm" for a
                           # ttm_json native base (ttm.json's TTM base less the amortization), else "declared_pin"
                           "native_base": bo.get("native_base"),
                           "base_used": "ttm" if _iprd_amortized_ttm(n) is not None else "declared_pin",
                           "base_oe_without_override": round(nb, 4) if nb is not None else None,
                           "base_oe_with_override": round(pb_, 4) if pb_ is not None else None,
                           "base_oe_impact_pct": round((pb_ / nb - 1) * 100, 2) if (nb and pb_ is not None) else None,
                           "weighted_irr_with_override": round(n["implied_irr_weighted"], 4)
                           if isinstance(n.get("implied_irr_weighted"), (int, float)) else None,
                           "impact_note": "acquired IPR&D amortized in the base (iprd_amortized): native base -> the pin; "
                                          "without it the run takes the one-time value deduction instead"})
                ev.update(amortized_impact if amortized_impact is not None else iprd_amortized_not_measured(
                    n, "not measured: update_registry was given no one-time-deduction replay"))
            if n.get("payable_base"):
                pb = n["payable_base"]
                ev.update({"basis": pb.get("basis"), "figures": pb.get("figures"), "shares": pb.get("shares"),
                           "ads_ratio": pb.get("ads_ratio"), "pinned_per_share": pb.get("pinned_per_share"),
                           "sic": pb.get("sic")})
                if payable_impact:
                    ev.update(payable_impact)
            entries.append(ev)
        gterm = (n.get("inputs") or {}).get("g_terminal", n.get("g_terminal"))
        if isinstance(gterm, (int, float)) and abs(gterm - 0.025) > 1e-9:
            entries.append({"ticker": ticker, "event": "gterm", "date": today, "value": gterm})
        cik_used = n.get("cik")
        cik_default = _default_cik(ticker)
        cik_fallback = any(str(f).startswith("CIK_FALLBACK") for f in n.get("fragility_flags") or [])
        if cik_used is not None and (cik_fallback or (cik_default is not None and int(cik_used) != int(cik_default))):
            entries.append({"ticker": ticker, "event": "cik", "date": today, "value": cik_used,
                            "note": "engine ran under a non-default CIK (--cik override or CIK-fallback probe)"})
        if n.get("ads_ratio"):
            a = n["ads_ratio"]
            entries.append({"ticker": ticker, "event": "ads_ratio", "date": today,
                            "ratio": a["ratio"], "source": a["source"], "reason": a["reason"]})
        if scope_event:
            entries.append({"ticker": ticker, "event": "scope_correction", "date": today,
                            "old_cap": scope_event["old_cap"], "new_cap": scope_event["new_cap"],
                            "in_scope": scope_event["in_scope"]})
        for ev in deferred_events or []:
            # [Codex review r8 of PR #47] carried across runs: the merged record of every period ever declared
            entries.append(dict(ev, date=today))
        # v5.7 (07 §1.11): the lanes' events, in this fixed order ([] until each lane fills its function)
        entries += _notch_events(ticker, today, notch, n)                       # L1 (R1)
        entries += _moat_events(ticker, today, moat_ev)                         # L3 / L3b (R4, M6)
        entries += _interim_events(ticker, interim, declined, today)            # L4 (R2)
        entries += _facts_events(ticker, today, facts_check)                    # L2 (R3)
        entries += _share_classes_events(ticker, share_classes, up_c, n, j)     # L8 (R6)
        entries += _base_alternatives_events(ticker, base_alts, today)          # R7
        entries += _capex_events(ticker, today, unlisted_acks, n)               # L9 (R8)
        _attach_fact_citations(entries[n_kept:], facts_check)                   # L2: a post-pass, never a new entry
        keep_first_dates(entries[n_kept:], prior)
        reg["entries"] = entries
        try:
            # [Codex review r21 of PR #47] tmp + _stable._replace (retried on a Windows PermissionError); a failure is
            # a clean refusal — main() writes the registry first, so nothing else has been written yet
            _atomic_write(REGISTRY, json.dumps(reg, indent=1))
        except OSError as ex:
            fail(f"cannot replace the registry {REGISTRY} ({type(ex).__name__}: {ex}) — it is written before "
                 "score.json and key_numbers.md, so nothing was written; close whatever holds the file and rerun")


def alert_reasons(tier_final, tier_by_numbers, override, conf, model_fit, unblocks, irr_at_floor, stale_release=None,
                  share_classes_raise=None):
    """(entry_reasons, exit_reasons): why an alert for this score is
    suppressed. Entry reasons apply only to a final S/A tier (alert_eligible),
    exit reasons only to a final tier below A (exit_alert_eligible); both are
    empty when the score clears its gate. stale_release (v5.5): the
    release_mismatch_reason() text when the engine output is not from the
    current ENGINE_RELEASE — it closes BOTH gates ("... — re-run the engine
    before an entry / exit alert"); None leaves every gate as in 5.4.
    share_classes_raise (v5.7 keyword placed by L0 for lane L8, R6: the
    reason when a share-class declaration RAISES the tier) is not read yet;
    None, the default, leaves every gate exactly as before."""
    sa = ("S", "A")
    entry, exit_ = [], []
    if stale_release:
        # DESIGN §8.3 [ADDITION, policy-bearing]: a score rebuilt on engine
        # output from another release never alerts, either way.
        (entry if tier_final in sa else exit_).append(
            f"{stale_release} — re-run the engine before an {'entry' if tier_final in sa else 'exit'} alert")
    if tier_final in sa:
        # Andrew's decision (2026-10-15, applied at the 2026-10-16 live port):
        # Tier S/A alerts fire regardless of confidence — confidence alone never
        # suppresses an alert, so there is deliberately no conf check here.
        if model_fit == "misfit": entry.append("sector model misfit")
        if unblocks: entry.append("tier exists only because of a judgment override")
        # Codex review of PR #2: a tier_override that lifts a C/B numeric tier into
        # S/A rests entirely on judgment — the weighted IRR never crossed the line.
        if override and tier_by_numbers not in sa:
            entry.append(f"tier rests on a judgment tier override (numeric tier {tier_by_numbers})")
        if irr_at_floor: entry.append("IRR at solver floor")
    else:
        # Confidence never suppresses an exit alert either (same decision).
        if model_fit == "misfit": exit_.append("sector model misfit")
        if unblocks: exit_.append("tier exists only because of a judgment override")
        # No tier-override rule here: a judgment downgrade out of S/A is a valid
        # exit warning (the entry rule stops judgment-only upgrades).
    return entry, exit_


def _usd(v):
    if v is None:
        return "—"
    a = abs(v)
    if a >= 1e9:
        return f"${v / 1e9:,.3f}B"
    if a >= 1e6:
        return f"${v / 1e6:,.1f}M"
    if a >= 1e3:
        return f"${v:,.0f}"
    return f"${v:,.2f}"


def _usd_exact(v):
    """A dollar amount to the dollar ($284,887,000) — the IPR&D lines quote filed figures exactly."""
    return f"${v:,.0f}" if isinstance(v, (int, float)) and not isinstance(v, bool) else "—"


def _pct(x, digits=2):
    return "—" if x is None else f"{x * 100:.{digits}f}%"


def _money(v):
    return "—" if v is None else f"${v:,.2f}"


def _amount(v, unit=None):
    """A filed amount in its own unit: $ for USD (or no unit), else '<n> <unit>'."""
    v = _num(v)
    if v is None:
        return "—"
    return _usd(v) if unit in (None, "", "USD") else f"{v:,.0f} {unit}"


def _csv_rows(folder):
    """financials_history.csv rows (dicts of strings), oldest first; [] when absent / unreadable."""
    try:
        with open(f"{folder}/financials_history.csv", encoding="utf-8", newline="") as f:
            rows = [r for r in csv.DictReader(f) if r.get("period_end")]
    except (OSError, csv.Error, UnicodeDecodeError):
        return []
    return sorted(rows, key=lambda r: r["period_end"])


def _f(s):
    try:
        return float(s) if s not in (None, "") else None
    except (TypeError, ValueError):
        return None


def capex_basis_lines(folder, n):
    """One 'Capex basis' line per last-3 FY (DESIGN §8.6), only when the run
    recorded capex_provenance (engine 5.5): from financials_history.csv's
    capex / capex_source / capex_tag (+ capex_ppe / capex_intangibles), else
    from capex_provenance itself when the CSV lacks those columns."""
    prov = n.get("capex_provenance")
    if not isinstance(prov, dict) or not prov:
        return []
    out = []
    rows = [r for r in _csv_rows(folder) if "capex_source" in r][-3:]
    for r in rows:
        ppe, intang = _f(r.get("capex_ppe")), _f(r.get("capex_intangibles"))
        split = f" (PP&E {_usd(ppe)} + intangibles {_usd(intang or 0.0)})" if ppe is not None else ""
        out.append(f"- Capex basis FY{r.get('fy_label') or r['period_end'][:4]} ({r['period_end']}): "
                   f"{_usd(_f(r.get('capex')))} — {r.get('capex_source') or '—'}: {r.get('capex_tag') or '—'}{split}")
    if out:
        return out
    for pe in sorted(prov)[-3:]:
        p = prov[pe] if isinstance(prov[pe], dict) else {}
        ppe = p.get("ppe") if isinstance(p.get("ppe"), dict) else {}
        intang = p.get("intangibles") if isinstance(p.get("intangibles"), dict) else {}
        legs = [f"{t} {_amount(v, p.get('ppe_unit'))}" for t, v in ppe.items()] \
            + [f"{t} {_amount(v, p.get('intangibles_unit'))}" for t, v in intang.items()]
        note = f"; intangibles not added: {p['intangibles_not_added']}" if p.get("intangibles_not_added") else ""
        out.append(f"- Capex basis FY{pe[:4]} ({pe}): {p.get('ppe_source') or '—'}: {' + '.join(legs) or '—'}{note}")
    return out


def _scalars(d, skip=()):
    """'k=v, …' for the scalar entries of a record (lists of scalars joined by '; ')."""
    parts = []
    for k, v in (d or {}).items():
        if k in skip or isinstance(v, dict):
            continue
        if isinstance(v, list):
            if v and all(not isinstance(x, (dict, list)) for x in v):
                parts.append(f"{k}={'; '.join(str(x) for x in v)}")
            continue
        if isinstance(v, bool) or v is None or isinstance(v, str):
            if v is not None:
                parts.append(f"{k}={v}")
        elif isinstance(v, int):
            parts.append(f"{k}={v:,}")
        elif isinstance(v, float):
            parts.append(f"{k}={v:,.0f}" if v.is_integer() and abs(v) >= 1000 else f"{k}={v:.6g}")
        else:
            parts.append(f"{k}={v}")
    return ", ".join(parts)


def _split_fact(f):
    """(date, ratio text) of one split-fact record: {date, ratio_filed} (the
    engine's shape; event_date / ratio accepted too) or a [date, ratio] pair."""
    if isinstance(f, dict):
        d = f.get("date") or f.get("event_date")
        r = f.get("ratio_filed", f.get("ratio"))
    elif isinstance(f, (list, tuple)) and f:
        d, r = f[0], (f[1] if len(f) > 1 else None)
    else:
        d, r = f, None
    r = _num(r)
    return str(d) if d else "date n/a", (f"{r:g}" if r is not None else "n/a")


def share_basis_lines(n):
    """'Share basis' line(s) when the run recorded a split adjustment, a
    cover-page divergence or a share-scale defect (DESIGN §8.6); [ADDITION —
    M7] one line per unconfirmed post-FY split fact (no post-event cover-page
    count confirms it, so history and price may sit on different bases) and
    one compact line listing the in-history split facts."""
    out = []
    sb = n.get("share_basis") if isinstance(n.get("share_basis"), dict) else {}
    if isinstance(sb.get("split"), dict) and sb["split"]:
        out.append(f"- Share basis: split adjustment applied — {_scalars(sb['split'])}")
    if isinstance(sb.get("divergence"), dict) and sb["divergence"]:
        out.append(f"- Share basis: cover-page divergence — {_scalars(sb['divergence'])}")
    unconf = sb.get("unconfirmed_split_facts")
    for f in (unconf if isinstance(unconf, list) else []):
        d, r = _split_fact(f)
        out.append(f"- Share basis: unconfirmed split fact {d} ratio {r} (no post-event cover-page count confirms it) "
                   "— check the latest 10-Q")
    hist = sb.get("in_history_split_facts")
    facts = sorted(set(_split_fact(f) for f in (hist if isinstance(hist, list) else [])))
    if facts:
        out.append("- Share basis: in-history split facts (dated on or before the latest FY end; never applied by the "
                   "engine — informational): " + "; ".join(f"{d} ratio {r}" for d, r in facts))
    ss = n.get("share_scale") if isinstance(n.get("share_scale"), dict) else {}
    if ss.get("defect"):
        out.append(f"- Share basis: share-scale defect — {_scalars(ss, skip=('defect', 'tests'))}")
    return out


def sbc_reconciled_lines(n):
    """The periods where AllocatedShareBasedCompensationExpense replaced a
    smaller ShareBasedCompensation (decision 6), from sbc_provenance."""
    prov = n.get("sbc_provenance")
    if not isinstance(prov, dict):
        return []
    out = []
    for pe in sorted(prov):
        p = prov[pe] if isinstance(prov[pe], dict) else {}
        if not p.get("reconciled"):
            continue
        sh = p.get("share") if isinstance(p.get("share"), list) else [None, None]
        al = p.get("allocated") if isinstance(p.get("allocated"), list) else [None, None]
        sv, av = (_num(sh[0]) if sh else None), (_num(al[0]) if al else None)
        pct = f" (+{(av / sv - 1) * 100:.1f}%)" if sv and av else ""
        out.append(f"- SBC reconciled FY{pe[:4]} ({pe}): AllocatedShareBasedCompensationExpense "
                   f"{_amount(av, al[1] if len(al) > 1 else None)} used over ShareBasedCompensation "
                   f"{_amount(sv, sh[1] if len(sh) > 1 else None)}{pct}")
    return out


def quoted(text):
    """v5.7 (07 §1.10, the echo convention): worker-authored text make_score prints in key_numbers.md, wrapped in
    curly quotes — check_quotes never reads a number inside “…”. Curly quotes inside the text become straight ones,
    so the span closes where the text ends. Not used for any line yet (each lane wraps its own echoes)."""
    s = "" if text is None else str(text)
    return "“" + s.replace("“", '"').replace("”", '"') + "”"


# v5.7 (L0, 07 §1.9): one hook per lane in key_numbers.md's section order — each returns its lines ([] in L0, so
# the text is byte-identical); a lane fills only its own function.
def _kn_price_vs_iv(n):
    """v5.7 (L2, R3; 02 §7.2): Headline, after "Upside vs price" — the price against the weighted IV@15%, so an
    analysis quotes the premium / discount instead of computing it. Omitted without a positive IV@15%."""
    p, iv = _num(n.get("price")), _num(n.get("iv_at_15"))
    if p is None or iv is None or iv <= 0:
        return []
    d = p / iv - 1.0
    return [f"- Price vs weighted IV@15%: price {_money(p)} is {abs(d) * 100:.1f}% {'above' if d >= 0 else 'below'} it "
            f"(price ÷ IV@15% = {p / iv:.2f}x)"]


def _kn_base_extras(n):
    """v5.7 (L2, R3; 02 §7.2): Base owner's earnings, after "Base OE/share" — price ÷ base OE/share (omitted when
    the base is not positive)."""
    p, b = _num(n.get("price")), _num(n.get("base_oe_per_share"))
    if p is None or b is None or b <= 0:
        return []
    return [f"- Price ÷ base OE/share: {p / b:.2f}x"]


def _kn_shares_suffix(n):
    """v5.7 placeholder (L8, R6): appended to the "Shares diluted (latest)" line on a declared run (total economic
    units). "" in L0."""
    return ""


def _kn_share_classes(n, score):
    """v5.7 placeholder (L8, R6): the per-period share-class block, right after the capex / share / SBC basis lines.
    [] in L0."""
    return []


def _kn_base_interim(n, score, interim, instance):
    """v5.7 placeholder (L4, R2): the ANNUAL_FROM_INSTANCE line, the "Interim bridge declined" line and a bridge's
    base-source text, before the payable block. [] in L0."""
    return []


def _kn_base_alternatives(score):
    """v5.7 placeholder (R7): the "Base alternatives" section, right after the IPR&D section. [] in L0."""
    return []


def _kn_growth_extras(folder, n):
    """v5.7 (L2, R3; 02 §7.2 / §1.1, 07 §1.9 item 4): the Growth & moat block's return / margin series from
    fundamentals.json (last 6 FY, 1 dp): gross, operating and net margin, ROE, FCF and OCF margin, revenue growth,
    SBC and capex % of revenue. The ROIC proxy series is printed once, by the moat lane's Moat scorecard (07 §1.20,
    02 Q3)."""
    return [f"- {label} (fundamentals.json): " + " · ".join(f"{v * 100:.1f}% ({fy})" for fy, v in reversed(pts))
            for label, _field, pts in _quotes.return_series(folder)]


def _usd_full(v):
    """Full dollars with the sign in front: $3,971,094,000 · -$52,220,000."""
    return "—" if _num(v) is None else f"{'-' if v < 0 else ''}${abs(v):,.0f}"


def _kn_filed_history(folder, n):
    """v5.7 (L2, R3; 02 §7.2, rebase A1 / A9 / A10): the "Filed history" table — financials_history.csv's last 10
    FY in full dollars (USD: the engine's FX-converted figures), after the Growth & moat block and before Scenarios
    (A1: never between the capex basis lines and "## Growth"). Columns the CSV lacks print "—"; total debt is
    debt_total, else debt_current + debt_lt; OE/share is shown only when the latest row reproduces the engine's
    latest-FY OE/share (× the applied ADS ratio), else the column is withheld with a note — never a refusal. Then the
    revenue, OCF, net income and OE year-on-year changes, newest first (check_quotes.YOY_COLUMNS)."""
    fh = _quotes.filed_history(folder, n)
    rows = fh["rows"]
    if not rows:
        return []
    cols = _quotes.FILED_COLUMNS
    L = ["", f"## Filed history (financials_history.csv, last {len(rows)} FY; USD — FX-converted at period-end rates "
             "where the filer reports in another currency)",
         "| FY | Period end | " + " | ".join(name for _, name in cols) + " |",
         "|" + "---|" * (len(cols) + 2)]
    for r in reversed(rows):
        cells = [r["fy"], r["period_end"]]
        for col, _ in cols:
            v = r.get(col)
            cells.append("—" if v is None else f"{_money(v)}" if col == "oe_per_share"
                         else f"{v:,.0f}" if col == "shares_diluted" else _usd_full(v))
        L.append("| " + " | ".join(cells) + " |")
    if not fh["per_share"]:
        L.append("- OE/share column withheld: the CSV's OE ÷ diluted shares does not reproduce the engine's latest-FY "
                 "OE/share (a share-count adjustment)")
    if fh["yoy"]:
        L.append("- " + "; ".join(f"{name} YoY: " + " · ".join(f"{g * 100:+.2f}% ({fy})" for fy, g in reversed(pts))
                                  for name, pts in fh["yoy"]))
    return L


def _kn_scenario_extras(n):
    """v5.7 (L2, R3; 02 §7.2): after the scenario table — the probability weights an analysis quotes (bear-or-worse,
    base, bull-or-better)."""
    sc = n.get("scenarios") or {}
    pr = [_num((sc.get(lbl) or {}).get("prob")) for lbl in LABELS]
    if any(x is None for x in pr):
        return []
    return [f"- Probability weight: bear-or-worse {(pr[0] + pr[1]) * 100:.0f}% · base {pr[2] * 100:.0f}% · "
            f"bull-or-better {(pr[3] + pr[4]) * 100:.0f}%"]


def _kn_method_runs(method_runs, previous):
    """v5.7 (L2, R3; 02 §7.3, rebase A15): "Method runs (saved engine runs — not the scored run)" — one line per
    hash-verified dcf_numbers_<label>.json (a preliminary or exploratory run quoted as a method range is quoted from
    here), an acquired-IPR&D saved run marked as after its own deduction; then the score this run replaced, when it
    was another engine run's. Engine output, so it precedes the judgment-backed sections."""
    if not method_runs and not previous:
        return []
    L = ["", "## Method runs (saved engine runs — not the scored run)"]
    for r in method_runs or []:
        s, rn = r["summary"], r["n"]
        sc = rn.get("scenarios") or {}
        pr = [_num((sc.get(lbl) or {}).get("prob")) for lbl in LABELS]
        probs = "/".join(f"{p * 100:.0f}" for p in pr) if all(p is not None for p in pr) else "—"
        w = rn.get("weighted") or {}
        line = (f"- {s['label']} ({s['file']}, {s.get('as_of')}, release {s.get('engine_release') or 'pre-5.4'}): base "
                f"{_money(rn.get('base_oe_per_share'))}/share ({rn.get('base_source')}), moat {rn.get('moat_score')}, "
                f"probs {probs}, g_base {_pct(rn.get('g_base'))} → weighted IRR {_pct(rn.get('implied_irr_weighted'))}, "
                f"IV@15% {_money(w.get('iv_at_15', rn.get('iv_at_15')))} · @12% {_money(w.get('iv_at_12', rn.get('iv_at_12')))}, "
                f"tier {rn.get('tier_by_numbers')}"
                + (f" (bear {_pct(rn.get('irr_bear'), 1)} {rn.get('tier_bear')} → bull {_pct(rn.get('irr_bull'), 1)} "
                   f"{rn.get('tier_bull')})" if rn.get("irr_bear") is not None else ""))
        if s.get("iprd_treatment"):
            line += (f" · acquired IPR&D: {s['iprd_treatment']}, {_money(s['iprd_charge_per_share'])}/share off every IV "
                     "(this run's figures are after it)")
        L.append(line)
    if previous:
        L.append(f"- Previous score (replaced by this run): {previous.get('analysis_date')}, release "
                 f"{previous.get('engine_release') or 'pre-5.4'}, tier {previous.get('tier_final')} (numbers "
                 f"{previous.get('tier_by_numbers')}), weighted IRR {_pct(previous.get('implied_irr'))}, IV@15% "
                 f"{_money(previous.get('iv_at_15'))}, base {_money(previous.get('base_oe_per_share'))}/share")
    return L


def _kn_moat(score):
    """v5.7 placeholder (L3 / L3b, R4): the "Moat scorecard" section. [] in L0."""
    return []


def _kn_interim(score, interim):
    """v5.7 placeholder (L4, R2a): the "Interim bridge" section. [] in L0."""
    return []


def _kn_declared_facts(facts_check):
    """v5.7 (L2, R3; 02 §7.4, D7): "Declared facts (not engine output)", always the last section — every declared
    fact with its value as rendered (the figure analysis.md quotes), period, type, source and status (verified,
    DRIFTED, STALE, the folder figure beside an adjusted one); labels, snippets and other worker text in “…”."""
    return _facts.key_numbers_lines(facts_check, quoted)


def write_key_numbers_text(folder, text):
    """key_numbers.md, atomically ([Codex review r21 of PR #47] tmp + replace) — v5.7 (L0): the text
    build_key_numbers made before the write phase; main() writes it last inside registry_transaction."""
    _atomic_write(f"{folder}/key_numbers.md", text)


def build_key_numbers(folder, n, j, score, applied, impact=None, ads_corr=None, facts_check=None, method_runs=None,
                      previous=None, interim=None, instance=None):
    """key_numbers.md — every headline figure from the final dcf_numbers.json.
    The single source workers quote in analysis.md. ads_corr (v5.5): the
    pre-5.5 ADS market-cap correction, printed with its label instead of the
    engine's uncorrected cap (the net-debt line follows its own rule, M1).
    v5.7 (L0): returns the text (write_key_numbers_text writes it); the
    lanes' sections come from the _kn_* hooks in the 07 §1.9 order —
    Headline, base OE (+ share classes, interim / instance lines, payable,
    IPR&D, base alternatives), Growth & moat, Filed history, Scenarios,
    Diagnostics, Fragility flags, Overrides applied, then Method runs, Moat
    scorecard, Interim bridge and Declared facts last."""
    L = [f"# {n['ticker']} — key numbers",
         f"Generated by make_score.py from dcf_numbers.json (engine v{n.get('engine_version')}, as of {n.get('as_of')}).",
         "Quote these figures verbatim in analysis.md — never recompute or retype a derived figure.",
         "",
         "## Headline"]
    if n.get("price") is not None:
        L.append(f"- Price: ${n['price']:,.2f} (source: {n.get('price_source')})")
    # ---- the Headline tier block (v5.7, L1: the mechanical misfit notch, R1; every echoed reason through quoted(),
    # 07 §1.10 — the notch reason whatever its source, the judgment override's, the set-aside's) ----
    mn = score.get("misfit_notch") if isinstance(score.get("misfit_notch"), dict) else None
    tier_note = score["tier_final"]
    why = score.get("tier_override_reason")
    if mn and mn.get("applies"):
        tier_note += f" (sector-misfit notch: numbers tier {mn.get('tier_by_numbers')} → {mn.get('tier_after_notch')}"
        if why:
            where = ("below the notch" if score["tier_final"] != mn.get("tier_after_notch")
                     else "at the notched tier (acquired-IPR&D hand deduction)")
            tier_note += f"; agent override {where}: {quoted(why)}"
        tier_note += ")"
    elif why:
        tier_note += f" (agent override of {n['tier_by_numbers']}: {quoted(why)})"
    conf_note = score["confidence"]
    if score.get("confidence_capped"):
        conf_note += " (capped from high by make_score: WIDE_SCENARIO_SPREAD present)"
    L.append(f"- Tier: {tier_note} · confidence {conf_note}")
    if mn and mn.get("applies"):
        L.append(f"- Misfit notch ({mn.get('reason_source')}): {quoted(mn.get('reason'))}")
    elif mn:
        L.append(f"- Misfit notch: not applied — {quoted(mn.get('reason'))}")
    if isinstance(score.get("misfit_sector_set_aside"), dict):
        L.append(f"- Sector misfit set aside: {quoted(score['misfit_sector_set_aside'].get('reason'))}")
    # ---- end of the Headline tier block ----
    if n.get("implied_irr_weighted") is not None:
        w = n.get("weighted") or {}
        L.append(f"- Weighted IRR: {_pct(n['implied_irr_weighted'])} · base-case IRR: {_pct(n.get('implied_irr_base'))}")
        L.append(f"- Weighted IV: @15% {_money(w.get('iv_at_15'))} · @12% {_money(w.get('iv_at_12'))} · @10% {_money(w.get('iv_at_10'))}")
        L.append(f"- Upside vs price: @15% {_pct(n.get('upside_at_15'), 1)} · @12% {_pct(n.get('upside_at_12'), 1)}")
        L += _kn_price_vs_iv(n)                                     # v5.7 hook (L2)
        if n.get("irr_bear") is not None:
            L.append(f"- IRR band: bear {_pct(n.get('irr_bear'))} (tier {n.get('tier_bear')}) → bull {_pct(n.get('irr_bull'))} (tier {n.get('tier_bull')}); scenario range {_pct(n.get('irr_low'))} – {_pct(n.get('irr_high'))}")
        if n.get("hurdle_prices"):
            hp = n["hurdle_prices"]
            L.append(f"- Hurdle-clearing prices (weighted path): 15% at {_money(hp.get('15'))} · 20% at {_money(hp.get('20'))} · 25% at {_money(hp.get('25'))}")
        if (n.get("diagnostics") or {}).get("irr_at_floor"):
            L.append("- IRR AT FLOOR: the solver converged onto terminal growth — read the weighted IRR as '<= g_terminal', not as a solution")
    if n.get("f_subtype"):
        L.append(f"- Tier F sub-type: {n['f_subtype']}")
    if n.get("note"):
        L.append(f"- Note: {n['note']}")
    # v5.5: the market cap carries its basis; a pre-5.5 ADS cap is the
    # make_score-corrected figure, labelled, with the engine's old print.
    if ads_corr:
        cap_line = (f"- Market cap (est): {_usd(ads_corr['cap'])} (ADS-corrected by make_score: price × shares ÷ ratio; "
                    f"the pre-5.5 engine printed {_usd(ads_corr['old_cap'])})")
    else:
        mb = n.get("market_cap_basis") if isinstance(n.get("market_cap_basis"), dict) else {}
        basis = score.get("market_cap_basis")
        cap_line = f"- Market cap (est): {_usd(n.get('market_cap_est'))}" + (
            f" (basis: {basis}" + (f"; {mb['formula']}" if mb.get("formula") else "") + ")" if basis else "")
    scope = score.get("in_scope_under_40b")
    scope_line = ("- Scope: " + ("in scope (market cap under $40B)" if scope else "out of scope (market cap $40B or more)")
                  + (" — corrected by make_score from the ADS-corrected market cap (the pre-5.5 engine's cap said "
                     f"{'in' if not scope else 'out of'} scope)" if score.get("in_scope_corrected_by_make_score") else "")
                  ) if isinstance(scope, bool) else None
    L += ["", "## Base owner's earnings",
          f"- Base OE/share: {_money(n.get('base_oe_per_share'))} (source: {n.get('base_source')})"]
    L += _kn_base_extras(n)                                         # v5.7 hook (L2)
    L += [f"- Latest FY OE/share: {_money(n.get('base_oe_latest_per_share'))} · normalized (3-yr median) OE/share: {_money(n.get('base_oe_normalized_per_share'))}",
          f"- Latest FY OE total: {_usd(n.get('base_oe_total_latest_fy'))}",
          (f"- Shares diluted (latest): {n.get('shares_diluted_latest'):,.0f}" if n.get("shares_diluted_latest")
           else "- Shares diluted (latest): —") + _kn_shares_suffix(n),          # v5.7 hook (L8)
          f"{cap_line} · net debt (latest): {_usd(n.get('net_debt_latest'))}"]
    if scope_line:
        L.append(scope_line)
    L.append(f"- OE-positive years (last 5): {n.get('oe_positive_years_of_last_5')}")
    L += capex_basis_lines(folder, n) + share_basis_lines(n) + sbc_reconciled_lines(n)
    L += _kn_share_classes(n, score)                                # v5.7 hook (L8)
    L += _kn_base_interim(n, score, interim, instance)              # v5.7 hook (L4)
    pb = n.get("payable_base")
    if pb:
        figs = pb.get("figures") or []
        L += ["", "## Payable-earnings base (insurer rule, 2026-10-19)",
              "- Operating income available to common, last 5 FY (oldest first, exact): " + " / ".join(f"${x:,.0f}" for x in figs),
              f"- Average: ${pb.get('average'):,.1f} · shares diluted (latest): {pb.get('shares'):,.0f}" if pb.get("shares") else f"- Average: {_usd(pb.get('average'))}",
              f"- Per ordinary share: {_money(pb.get('per_ordinary_share'))} × ADS ratio {pb.get('ads_ratio')} = pinned base {_money(pb.get('pinned_per_share'))}",
              f"- Source: {quoted((j.get('base_override') or {}).get('source'))}"]   # v5.7 (L2): worker text in “…”
    L += iprd_lines(n)   # v5.6: acquired IPR&D (nothing for a record without the block)
    L += _kn_base_alternatives(score)                               # v5.7 hook (R7)
    gc = n.get("growth_components") or {}
    L += ["", "## Growth & moat",
          f"- Growth blend: {_pct(n.get('g_blend'))}" + (f" → g_base {_pct(n.get('g_base'))}" if n.get("g_base") is not None else ""),
          f"- Components: rev CAGR 5y {_pct(gc.get('rev_cagr_5y'))} · rev CAGR 3y {_pct(gc.get('rev_cagr_3y'))} · latest rev YoY {_pct(gc.get('rev_yoy_latest'))} · OE/share CAGR 2y {_pct(gc.get('oe_ps_cagr_2y'))}",
          f"- Share count CAGR: {_pct(n.get('share_cagr'))} (growth adj {_pct(n.get('share_count_adj'))})",
          f"- Moat: {j['moat_score']}/10 · CAP {n.get('cap_years')} yrs · terminal growth {_pct(n.get('g_terminal'))}"]
    L += _kn_growth_extras(folder, n)                               # v5.7 hook (L2)
    L += _kn_filed_history(folder, n)                               # v5.7 hook (L2)
    scn = n.get("scenarios") or {}
    if scn:
        L += ["", "## Scenarios",
              "| Scenario | Prob | Growth start | OE mult | IV@15 | IV@12 | IRR |",
              "|---|---|---|---|---|---|---|"]
        names = {"super_bear": "Super bear", "bear": "Bear", "base": "Base", "bull": "Bull", "super_bull": "Super bull"}
        for lbl in LABELS:
            r = scn.get(lbl) or {}
            L.append(f"| {names[lbl]} | {_pct(r.get('prob'), 0)} | {_pct(r.get('g_start'), 1)} | {r.get('oe_mult')} | "
                     f"{_money(r.get('iv_at_15'))} | {_money(r.get('iv_at_12'))} | {_pct(r.get('irr'))} |")
        L += _kn_scenario_extras(n)                                 # v5.7 hook (L2)
    d = n.get("diagnostics") or {}
    if d:
        # Round-2 fix: the old line was ONE conditional expression over a
        # concatenated f-string, so a blank scenario spread dropped the OE
        # yield and TV share lines with it. Each figure gets its own line.
        # v5.5 (decision 1, "anything downstream"; M1): a pre-5.5 ADS record's
        # ratio is printed on the ADS basis beside the engine's, whatever the
        # state of its market cap (net_debt_line / ads_net_debt_basis).
        nd_line = net_debt_line(n)
        L += ["", "## Diagnostics",
              f"- OE yield: {_pct(d.get('oe_yield'))}",
              f"- TV share @15%: {_pct(d.get('tv_share_at_15'), 1)}",
              f"- Scenario spread (IV@15 super-bull / super-bear): {d['scenario_spread_iv15']:.2f}x" if d.get("scenario_spread_iv15") is not None else "- Scenario spread: —",
              nd_line,
              f"- Months since FY end: {d.get('months_since_fy_end'):.1f}" if d.get("months_since_fy_end") is not None else "- Months since FY end: —"]
    flags = n.get("fragility_flags") or []
    L += ["", "## Fragility flags"]
    L += [f"- {f}" for f in flags] or ["- (none)"]
    if applied:
        L += ["", "## Overrides applied",
              f"Filing gaps found and covered by judgment overrides: {', '.join(n.get('data_gap') or []) or '—'}",
              "",
              "| Field | Value | Kind | Source | Periods filled |",
              "|---|---|---|---|---|"]
        for field in ("capex", "sbc", "shares"):
            if field in applied:
                a = applied[field]
                val = _usd(a["value"]) if field in ("capex", "sbc") else f"{a['value']:,.0f}"
                filled = ", ".join(a.get("periods_filled") or [])
                if a.get("scope") == "ttm_legs":
                    filled = "TTM legs only (ttm.json): " + filled
                L.append(f"| {field} | {val} | {a['kind']} | {quoted(a['source'])} | {filled} |")   # v5.7 (L2): “…”
        for field in ("capex", "sbc", "shares"):
            if field in applied:
                L.append(f"- {field} reason: {quoted(applied[field]['reason'])}")
        if impact:
            basis_lbl = {"ttm": "TTM base", "payable_5y": "payable-earnings base (5-yr avg operating income to common)",
                         "declared_pin": "declared base_override pin (held constant in both worlds)"}.get(
                impact.get("base_used"), "3-yr median base")
            pct = impact.get("base_oe_impact_pct")
            pp = impact.get("weighted_irr_impact_pp")
            if impact.get("note"):
                # v5.5: release mismatch and no prior measurement on this base
                L += ["", f"- Impact {impact['note']} (with override: base OE/share "
                          f"{_money(impact.get('base_oe_with_override'))}, weighted IRR {_pct(impact.get('weighted_irr_with_override'))})"]
            else:
                L += ["",
                      f"- Measured impact (on the {basis_lbl} actually used; same final configuration, overrides toggled off): "
                      f"base OE/share {_money(impact.get('base_oe_without_override'))} (no override) → "
                      f"{_money(impact.get('base_oe_with_override'))} (with override)"
                      + (f", {pct:+.2f}%" if isinstance(pct, (int, float)) else "")
                      + f" · weighted IRR {_pct(impact.get('weighted_irr_without_override'))} → {_pct(impact.get('weighted_irr_with_override'))}"
                      + (f" ({pp:+.2f}pp)" if isinstance(pp, (int, float)) else "")
                      + (f" — carried from the prior score.json, not re-measured (engine output release "
                         f"{impact.get('counterfactual_engine_release') or 'pre-5.4'} vs current {ENGINE_RELEASE})"
                         if impact.get("impact_carried_from_prior_score") else "")]
            if impact.get("unblocks_tier"):
                # [v5.5 — Codex, PR #31] a TTM-leg override (scope ttm_legs) with no
                # annual gap: without it there is no TTM base to pin, not no tier.
                if any(a.get("scope") == "ttm_legs" for a in applied.values()) and not (n.get("data_gap") or []):
                    L.append("- Unblocks tier: YES — ttm.py cannot build the TTM base without this override, so the "
                             "pinned base and this tier rest on it; without it the score falls back to the 3-yr median base.")
                else:
                    L.append("- Unblocks tier: YES — this override is the only reason this company has a tier; "
                             "without it the filing gap blocks scoring entirely.")
    # v5.7 (07 §1.9): the fixed tail — engine runs first, then the judgment-backed sections, declared facts last
    L += _kn_method_runs(method_runs, previous)                     # L2
    L += _kn_moat(score)                                            # L3 / L3b
    L += _kn_interim(score, interim)                                # L4
    L += _kn_declared_facts(facts_check)                            # L2
    return "\n".join(L) + "\n"


def main():
    ticker = sys.argv[1].upper()
    folder = f"{BASE}/{ticker}"
    npath, jpath, spath = f"{folder}/dcf_numbers.json", f"{folder}/judgment.json", f"{folder}/score.json"
    if not os.path.exists(npath):
        fail(f"no dcf_numbers.json in {folder} — run dcf_engine.py first")
    n = json.load(open(npath, encoding="utf-8"))
    # Round-2 audit (NOW item): never build a score from pre-v5, gate-less
    # engine output. Before this check, make_score happily rebuilt HIG's v4
    # Tier B score.json from a v4 dcf_numbers.json (SBC missing in every
    # year) — a complete bypass of the v5 data gate, live mid-re-run.
    ev = n.get("engine_version")
    if not isinstance(ev, (int, float)) or isinstance(ev, bool) or ev < 5 or "data_gap" not in n:
        fail(f"dcf_numbers.json is pre-v5 output (engine_version={ev!r}, "
             f"data_gap field {'present' if 'data_gap' in n else 'MISSING'}) — this folder holds "
             "pre-v5 output and the engine must be re-run under v5 before scoring; "
             "make_score.py never builds a score from gate-less engine output")
    # Provenance (round-2): the engine stamps dcf_numbers.json with a sha256
    # content hash over its canonical payload. A mismatch — or no hash at
    # all — means the numbers were touched after the engine run (the audit
    # hand-edited one to Tier S, 31% IRR, and it scored). Refuse both.
    ch = n.get("content_hash")
    if not ch:
        fail("dcf_numbers.json has no content_hash — it predates engine provenance stamping or was "
             "stripped; re-run dcf_engine.py so the engine stamps its own output before scoring")
    canon = json.dumps({k: v for k, v in n.items() if k != "content_hash"},
                       sort_keys=True, separators=(",", ":"), default=str)
    if hashlib.sha256(canon.encode()).hexdigest() != ch:
        fail("dcf_numbers.json content_hash MISMATCH — the engine output was modified after the run "
             "(hand-edited numbers); re-run dcf_engine.py and score only what the engine produces")
    # v5.7 step 1 (07 §1.12; lane L4, R2b): the filing's own XBRL instance the run read annual facts from must be the
    # committed <T>/annual_instance.json (None in L0)
    instance = annual_instance_check(folder, n)
    # v5.5 (DESIGN §2c): a share_class_mismatch declaration never scores. It is
    # checked ahead of the gap check so the refusal names the declaration (a
    # 5.5 run also carries it as the uncovered gap "share_class").
    if os.path.exists(jpath):
        try:
            with open(jpath, encoding="utf-8") as f:
                refuse_share_class_mismatch(json.load(f))
        except ValueError:
            pass  # an unreadable judgment.json is reported where it is loaded below
    # v5.5 (DESIGN §8.2): the score being replaced — its override_impact is
    # carried when the engine output is from another release.
    prior_score = None
    if os.path.exists(spath):
        try:
            with open(spath, encoding="utf-8") as f:
                prior_score = json.load(f)
        except (OSError, ValueError):
            prior_score = None
    release_mismatch = n.get("engine_release") != ENGINE_RELEASE
    applied = {}
    for o in n.get("overrides_applied") or []:
        if isinstance(o, dict) and o.get("field"):
            applied[o["field"]] = o
    gaps = list(n.get("data_gap") or [])
    uncovered = [f for f in gaps if f not in applied]
    for f in n.get("data_gap_uncovered") or []:
        if f not in applied and f not in uncovered:
            uncovered.append(f)
    if uncovered:
        fail(f"dcf_numbers.json has uncovered data_gap {uncovered} — no score may be written on an uncovered data gap (gaps fully covered by judgment overrides appear in overrides_applied)")
    if not n.get("tier_by_numbers"):
        fail("dcf_numbers.json has no tier_by_numbers — engine run did not produce a tier")

    if not os.path.exists(jpath):
        if os.path.exists(spath):
            seed_judgment(folder, json.load(open(spath, encoding="utf-8")))
        else:
            fail(f"no judgment.json in {folder} and no score.json to seed from")
    j = json.load(open(jpath, encoding="utf-8"))
    refuse_share_class_mismatch(j)

    for field in ("name", "sector", "moat_score", "moat_justification", "probs_used",
                  "one_liner", "confidence", "in_scope_under_40b"):
        if j.get(field) is None:
            fail(f"judgment.json: missing required field '{field}'")
    check_str_list(j, "moat_for")
    check_str_list(j, "moat_against")
    probs = j["probs_used"]
    if not (isinstance(probs, list) and len(probs) == 5 and all(isinstance(p, (int, float)) for p in probs)):
        fail("judgment.json: probs_used must be a list of 5 numbers")
    if abs(sum(probs) - 1.0) > 0.01:
        fail(f"judgment.json: probs_used sums to {sum(probs):.3f}, not 1.0")
    scn = n.get("scenarios") or {}
    if scn:
        for i, lbl in enumerate(LABELS):
            ep = (scn.get(lbl) or {}).get("prob")
            if ep is None or abs(ep - probs[i]) > 0.005:
                fail(f"judgment.json probs_used[{i}]={probs[i]} does not match engine scenario '{lbl}' prob {ep} — judgment.json is not the input set for this engine run")
    if n.get("moat_score") is not None and abs(float(j["moat_score"]) - float(n["moat_score"])) > 0.01:
        fail(f"judgment.json moat_score {j['moat_score']} does not match engine moat_score {n['moat_score']} — rerun the engine with this judgment or fix judgment.json")
    if j["confidence"] not in CONFIDENCE:
        fail(f"judgment.json: confidence must be one of {CONFIDENCE}")
    override = j.get("tier_override")
    if override is not None:
        if override not in TIERS:
            fail(f"judgment.json: tier_override must be one of {TIERS} or null")
        if not (j.get("tier_override_reason") or "").strip():
            fail("judgment.json: tier_override requires a tier_override_reason")
    j_over = validate_overrides(j)
    for field, o in j_over.items():
        if field in applied:
            a = applied[field]
            if a.get("kind") != o["kind"] or abs(float(a["value"]) - float(o["value"])) > max(1.0, abs(float(o["value"])) * 0.001):
                fail(f"judgment.json {field}_override (value {o['value']}, kind {o['kind']}) disagrees with dcf_numbers.json overrides_applied (value {a.get('value')}, kind {a.get('kind')}) — the judgment file and the engine run are out of sync; rerun the engine")
        elif field in gaps:
            fail(f"judgment.json declares {field}_override but dcf_numbers.json shows an uncovered {field} gap — rerun the engine so the override is applied before scoring")
    for field in applied:
        if field not in j_over:
            fail(f"dcf_numbers.json overrides_applied includes {field} but judgment.json declares no {field}_override")
    check_override_currency_sync(j_over, applied, n)
    refuse_last_filed_unit_usd_override(n, j_over, applied)   # [ADDITION — HTHT]
    # [Codex review r23 of PR #47] the current ttm.json, as check_ttm_inputs_current (below) compares it with what the
    # run read — v5.7 (L0): read here, before the capex refusals that need its TTM legs (lane L9); unchanged otherwise
    try:
        with open(f"{folder}/ttm.json", encoding="utf-8") as f:
            _tt_now = json.load(f)
    except Exception:
        _tt_now = None
    refuse_superseded_capex_override(n, j_over)               # [ADDITION — WY]
    refuse_capex_override_software(n, j_over, tt=_tt_now)     # v5.7 placeholder (L9, R9)
    refuse_unlisted_capex_component(n, j)                     # v5.7 placeholder (L9, R8)

    # Override sanity band (round-2): the engine measured each declared
    # override against the company's last FILED value for that field. A value
    # outside 0.1x-10x of it (or with no filed value at all) needs an explicit
    # ack_reason in judgment.json acknowledging the out-of-band value — the
    # harness typo (19 for 19,000,000) and the never-filed case both land here.
    checks = n.get("override_checks") or {}
    for field, o in j_over.items():
        chk = checks.get(field)
        if chk and chk.get("out_of_band") and not str(o.get("ack_reason") or "").strip():
            lf = chk.get("last_filed_value")
            lf_s = f"${lf:,.0f}" if isinstance(lf, (int, float)) else "no filed value at all"
            fail(f"judgment.json {field}_override value {o['value']:,.0f} is OUT OF BAND — outside 0.1x-10x of the "
                 f"last filed value ({lf_s}) — and judgment.json carries no ack_reason acknowledging it. "
                 "Correct the value, or add ack_reason explaining why an out-of-band figure is right")

    j_base_override = validate_base_override(j)
    if j_base_override and j_base_override.get("basis") == PAYABLE_BASIS:
        # A payable declaration is binding: the final run must have been pinned
        # through --base-judgment (engine record payable_base, pin source
        # judgment_base_override). A median run, or a --base-oe-ps run typed
        # with the per-ordinary value (wrong by the ADS ratio), is refused.
        _pin = (n.get("inputs") or {}).get("base_pin_source")
        if _pin != "judgment_base_override" or not n.get("payable_base"):
            fail(f"judgment.json declares a {PAYABLE_BASIS} base_override but the engine run was not pinned through "
                 f"--base-judgment (base_pin_source {_pin!r}, payable_base "
                 f"{'present' if n.get('payable_base') else 'absent'}) — rerun the final pass with --base-judgment "
                 "so the engine recomputes, scales and records the base")
        _sic = str((n.get("payable_base") or {}).get("sic") or "")
        if _sic not in PAYABLE_SIC:
            fail(f"payable-earnings base at a filer outside the rule's scope: engine recorded SIC {_sic or 'unknown'} "
                 f"({(n.get('payable_base') or {}).get('sic_description') or 'n/a'}); the rule covers P&C insurers and "
                 f"reinsurers only (SIC {sorted(PAYABLE_SIC)}) — drop the declaration and keep the OCF base + notch")
    check_iprd_amortized(n, j_base_override)   # v5.6
    check_iprd_amortized_ttm_current(folder, n)   # [fixer review round]
    check_iprd_cash_flow(n, validate_iprd_cash_flow_check(j))   # [fixer review round]
    _deferred = validate_iprd_deferred_payment(j)   # Andrew's 2026-10-20 ruling (delegated)
    check_iprd_deferred_payment(n, _deferred)
    # [Codex review r8 of PR #47] the lifetime cap against the registry's carried record, before any measurement: a
    # fast pre-check only — [Codex review r19 of PR #47] the binding check re-reads the registry under its lock in
    # registry_transaction below, with the writes
    iprd_deferred_lifetime(ticker, _deferred, registry_prior_entries(ticker))
    check_iprd_share_count_unverified(n, j)   # [Codex review r1 of PR #47]
    check_iprd_unconverted(n)   # [Codex review r3 of PR #47]
    # [Codex review r22 of PR #47] last of the IPR&D checks, so a specific refusal above names its own cause
    check_iprd_judgment_current(n, j)
    j_ads = validate_ads_ratio(j)
    j_second_pass = validate_second_pass(j)
    # v5.7 step 2 (07 §1.12, after the IPR&D checks so their refusals keep precedence): the declared share classes
    # (L8, R6) and the declared facts + saved method runs (L2, R3) — validation and folder verification only, no
    # influence yet. None / no-ops in L0.
    j_sc = validate_share_classes(j)                          # L8 (R-1)
    check_share_classes_sync(n, j_sc, folder)                 # L8 (R-2 … R-5)
    check_up_c_obligation(n, j)                               # L8 (R-8)
    fc = load_declared_facts(folder, n, j, prior_score)       # L2
    runs = load_method_runs(folder, n)                        # L2

    # ADS gate (round-2): a 20-F/40-F filer's per-share figures are per
    # ordinary share; the traded price is per ADS. Without an applied
    # ads_ratio the tier is meaningless — refuse with DATA_GAP:ads_ratio so
    # the worker blocks it like any other data gap.
    form = n.get("filer_annual_form")
    if form in ("20-F", "40-F"):
        n_ads = n.get("ads_ratio")
        if not n_ads:
            fail(f"DATA_GAP:ads_ratio — {ticker} files on {form} and no ads_ratio was applied by the engine, so its "
                 "per-share figures are per ordinary share while the price is per ADS. Block via queue.py with this "
                 "reason, or add ads_ratio {ratio, source, reason} to judgment.json (a main-agent decision) and rerun the engine")
        if not j_ads or abs(float(j_ads["ratio"]) - float(n_ads["ratio"])) > max(0.001, abs(float(n_ads["ratio"])) * 0.001):
            fail("judgment.json ads_ratio disagrees with the ratio the engine applied in dcf_numbers.json — "
                 "rerun the engine with the current judgment.json")

    # TTM pin provenance (round-2): a pinned base (--base-oe-ps / --ttm) must
    # trace to ttm.py's saved output (ttm.json) within 0.1%. Any other pin is
    # a free number (the harness's --base-oe-ps 9.99 made a Tier S) unless
    # judgment.json declares it as a base_override {value, source, reason}.
    inp = n.get("inputs") or {}
    pinned = inp.get("base_oe_ps_arg") is not None or "ttm" in (n.get("base_source") or "").lower()
    if pinned:
        score_base = n.get("base_oe_per_share")
        ttm_val = None
        try:
            with open(f"{folder}/ttm.json", encoding="utf-8") as f:
                ttm_val = json.load(f).get("ttm_oe_per_share")
        except Exception:
            ttm_val = None
        # [Codex review r25 of PR #47] a zero TTM base is ttm.json's pin for a --ttm or --base-oe-ps pin (a payable
        # pin keeps its own declaration check); [Codex review r26 of PR #47] an undeclared numeric match, so within
        # 0.1% and a zero only by an exact zero (dcf_engine.figure_matches): half a cent let --base-oe-ps 0.004 pass
        # as ttm.json's $0.00 base and publish Tier D where the TTM base is Tier F
        via_ttm = (_engine.figure_matches(score_base, ttm_val)
                   and ((ttm_val != 0 and score_base != 0)
                        or inp.get("base_pin_source") in ("ttm_json", "base_oe_ps_arg")))
        # [Codex review r24 of PR #47] a --base-oe-ps pin its declaration says was built on FY figures is checked as
        # the declared base (check_base_basis_window included) even when it equals ttm.json's figure
        if via_ttm and inp.get("base_oe_ps_arg") is not None and declared_fy_built_pin(j_base_override, score_base):
            via_ttm = False
        if not via_ttm:
            pb = n.get("payable_base") or {}
            if pb:
                # Payable-earnings pin: the score's base is the declared
                # per-ordinary value scaled by the ADS ratio, and the engine's
                # record must match the declaration figure for figure.
                # Zero is a valid five-year average (Tier F, payable_earnings_nonpositive):
                # compare recorded and declared values at a cent / one-share tolerance.
                declared = (j_base_override and j_base_override.get("basis") == PAYABLE_BASIS
                            and isinstance(score_base, (int, float))
                            and pb.get("pinned_per_share") is not None
                            and abs(float(pb["pinned_per_share"]) - score_base) <= 1e-6
                            and abs(float(pb.get("per_ordinary_share") if pb.get("per_ordinary_share") is not None else 1e9)
                                    - float(j_base_override["value"])) <= 0.005
                            and [float(x) for x in (pb.get("figures") or [])] == [float(x) for x in j_base_override["figures"]]
                            and abs(float(pb.get("shares") or 0) - float(j_base_override["shares"])) < 1.0)
            else:
                # [Codex review r25 of PR #47] a $0.00 base (an amortized base the mean charge exhausts) is
                # declared by a zero value; [Codex review r26] at half a cent only for the iprd_amortized arithmetic,
                # 0.1% (a zero only exactly) for a plain value (dcf_engine.declared_value_matches)
                declared = bool(j_base_override and _engine.declared_value_matches(j_base_override, score_base))
                if declared:
                    check_base_basis_window(folder, n, j_base_override)   # [Codex review r15 of PR #47]
            if not declared:
                fail(f"base pin provenance: the score's base OE/share {score_base} differs from ttm.json's "
                     f"ttm_oe_per_share {ttm_val} by >0.1% (a zero only exactly; or ttm.json is missing) and judgment.json declares no "
                     "matching base_override {value, source, reason} — a pinned base must come from ttm.py "
                     "(ttm.json, via --ttm) or be declared as a base_override; an arbitrary pin is not scoreable")
    # [Codex review r23 of PR #47] ...and the rest of what the run read from ttm.json must still be ttm.json's (the
    # document read above, before the capex refusals)
    check_ttm_inputs_current(n, _tt_now)
    refuse_pre57_ttm_json(n, _tt_now)                          # v5.7 placeholder (L9, R8 / R9 TTM provenance)
    check_ttm_on_declaration(n, j_sc, _tt_now)                 # v5.7 placeholder (L8, R-6)
    # v5.7 step 3 (07 §1.12): the declared 6-K interim bridge (L4), then R7's plan, then L4's obligation (a declared
    # bridge may be rejected through ttm_rejection_reason) — all None / no-ops in L0
    interim = interim_pin_state(folder, n, j, _tt_now)         # L4 (R2a)
    declined = None                                            # L4: judgment.json interim_bridge_declined, once read
    plan = ttm_rejection_state(folder, n, j, j_sc=j_sc, interim=interim, j_over=j_over)   # R7
    check_interim_obligation(n, j, interim, plan=plan)         # L4 (R2a)

    # [v5.5 — Codex, PR #31] Overrides ttm.py used to fill the legs of the
    # TTM base this score is pinned to, where the annual engine applied none
    # (APA's SBC estimate): reported, measured and gated with the applied ones.
    ttm_only = ttm_leg_overrides(folder, n, j_over, applied)
    reported = dict(applied)
    reported.update(ttm_only)

    # Impact on the base the final run actually used — computed before any
    # write, so a measurement failure refuses cleanly like any other refusal.
    # v5.5: engine output from another release is never replayed through the
    # current engine (a different capex / SBC basis) — carried or unmeasured.
    if not reported:
        impact = None
    elif release_mismatch:
        impact = carried_override_impact(n, prior_score)
        # [v5.5 — PR #31 verifier] the TTM-leg rule holds on stale output too:
        # the carried block's own measurement when it said so, else ttm.py's
        # no-override run (ttm.py, not an engine replay).
        if ttm_only and not impact.get("unblocks_tier"):
            prior_blk = (prior_score or {}).get("override_impact") if isinstance(prior_score, dict) else None
            if impact.get("impact_carried_from_prior_score") and isinstance(prior_blk, dict) \
                    and prior_blk.get("unblocks_tier") is True:
                impact["unblocks_tier"] = True
            elif not _ttm_no_override_run(ticker, n)[1]:
                impact["unblocks_tier"] = True
    else:
        impact = compute_override_impact(ticker, n, ttm_only=ttm_only)
    # v5.7 step 4 (07 §1.12): the lanes' measurements, every one before the first write — L4's bridged vs
    # annual-median measurement, L8's filed-class vs total-unit replay (None in L0)
    interim_meas = interim_bridge_measurement(ticker, n, interim, release_mismatch, prior_score)   # L4 (R2a)
    sc_impact = share_classes_impact(ticker, n, j_sc, prior_score)                                # L8 (R6)
    # [ADDITION — M3] The payable-earnings pin's own impact (registry
    # base_override event): measured through the current engine only on
    # current-release output, carried / not measured otherwise — and, like
    # every measurement, before the first write.
    payable_impact = None
    if base_override_event_applies(j, n) and n.get("payable_base"):
        payable_impact = (carried_payable_impact(n, prior_payable_event(ticker)) if release_mismatch
                          else payable_pin_impact(ticker, n))
    # [Codex review r2 of PR #47] the iprd_amortized base's own impact (the one-time-deduction path it replaces),
    # measured through the current engine on current-release output only, before the first write
    amortized_impact = None
    if (base_override_event_applies(j, n) and (j.get("base_override") or {}).get("basis") == IPRD_AMORTIZED_BASIS
            and _iprd_amortized_record(n) is not None):
        amortized_impact = (iprd_amortized_not_measured(n, _not_measured_note(n.get("engine_release"))) if release_mismatch
                            else iprd_amortized_impact(ticker, n))
    # v5.7 step 4 (R7): the one base_alternatives record — the published base beside every other base computed for
    # the run (absorbs L4's interim_meas; each ttm.json alternative gated on L8's declaration). None in L0.
    base_alts = build_base_alternatives(ticker, folder, n, j, plan, impact=impact, payable_impact=payable_impact,
                                        amortized_impact=amortized_impact, release_mismatch=release_mismatch,
                                        prior_score=prior_score, j_sc=j_sc, interim_meas=interim_meas)

    scenarios = {}
    for lbl in LABELS:
        r = scn.get(lbl)
        if r:
            scenarios[lbl] = {"prob": r.get("prob"),
                              "iv_at_15": round(r["iv_at_15"], 2) if r.get("iv_at_15") is not None else None,
                              "irr": round(r["irr"], 4) if r.get("irr") is not None else None}
    # Scope and confidence are COMPUTED here, never trusted from judgment
    # (round-2: in_scope_under_40b: true at a $93B market cap and confidence:
    # high under WIDE_SCENARIO_SPREAD were both accepted verbatim).
    # v5.5 (DESIGN §1): a pre-5.5 ADS run's cap is price × shares ÷ ratio, and
    # a scope the old (ratio-times-too-large) cap implied is rewritten.
    ads_corr = ads_cap_correction(n)
    mktcap = ads_corr["cap"] if ads_corr else n.get("market_cap_est")
    computed_scope, scope_rewrite, scope_corrected = scope_decision(j["in_scope_under_40b"], mktcap, ads_corr)
    j_scope = scope_rewrite if scope_rewrite is not None else j["in_scope_under_40b"]
    if computed_scope is not None and bool(j_scope) != computed_scope:
        if ads_corr:
            fail(f"judgment.json in_scope_under_40b={j['in_scope_under_40b']} contradicts the ADS-corrected market cap "
                 f"({_usd(mktcap)} = price × shares ÷ {ads_corr['ratio']:g}; the pre-5.5 engine printed "
                 f"{_usd(ads_corr['old_cap'])}, which does not explain it either) — fix judgment.json to match")
        fail(f"judgment.json in_scope_under_40b={j['in_scope_under_40b']} contradicts the engine's market cap "
             f"({_usd(mktcap)}) — scope is computed from market cap by make_score.py; fix judgment.json to match")
    scope_val = computed_scope if computed_scope is not None else j["in_scope_under_40b"]
    conf = j["confidence"]
    conf_capped = False
    if conf == "high" and any(str(f).startswith("WIDE_SCENARIO_SPREAD") for f in n.get("fragility_flags") or []):
        conf, conf_capped = "medium", True
    mktcap_b = round(mktcap / 1e9, 2) if _num(mktcap) else None
    mcap_basis = market_cap_basis(n, ads_corr)
    score = {"ticker": n["ticker"], "name": j["name"], "sector": j["sector"],
             "price": n.get("price"), "market_cap_b": mktcap_b, "market_cap_basis": mcap_basis,
             "engine_version": n.get("engine_version"),
             "base_oe_per_share": n.get("base_oe_per_share"),
             "base_year": (n.get("latest_period_end") or "")[:4] or None,
             "base_source": n.get("base_source"),
             "moat_score": j["moat_score"], "moat_justification": j["moat_justification"],
             "cap_years": n.get("cap_years"), "fragility_flags": n.get("fragility_flags", []),
             "scenarios": scenarios,
             "iv_at_15": round(n["iv_at_15"], 2) if n.get("iv_at_15") is not None else None,
             "iv_at_12": round(n["iv_at_12"], 2) if n.get("iv_at_12") is not None else None,
             "implied_irr": round(n["implied_irr_weighted"], 4) if n.get("implied_irr_weighted") is not None else None,
             "implied_irr_base_case": round(n["implied_irr_base"], 4) if n.get("implied_irr_base") is not None else None,
             "upside_at_15_pct": round(n["upside_at_15"] * 100, 1) if n.get("upside_at_15") is not None else None,
             "tier_by_numbers": n["tier_by_numbers"],
             "tier_final": None,   # v5.7 (L1): set below by misfit_notch (the notched tier, or an override in force)
             "confidence": conf, "one_liner": j["one_liner"],
             "analysis_date": n.get("as_of"), "in_scope_under_40b": scope_val}
    # v5.4 additions — every one copied from the engine or derived by rule here.
    flags_all = n.get("fragility_flags") or []
    diag = n.get("diagnostics") or {}
    # v5.7 (L1, R1): universe sector OR EDGAR SIC (dcf_engine.misfit_status), no longer the flag alone
    model_fit, fit_basis = misfit_detection(n, folder)
    _dbl = check_no_double_softening(n, j, model_fit)
    if _dbl:
        fail(_dbl)
    # v5.7 step 5 (07 §1.12; lane L1, R1): the mechanical misfit notch, before registry_transaction (its refusals
    # R-1 .. R-5 write nothing); the payable double-count refusal above keeps priority
    tier_final, notch, override_in_force = misfit_notch(n, j, model_fit, fit_basis, override, is_57_run(n))
    score["tier_final"] = tier_final
    set_aside = misfit_set_aside_record(model_fit, fit_basis)
    # v5.7 step 6 (lane L3 / L3b, R4 / M6): moat_ev = _moat.evaluate(folder, n, j, facts=..., is_57=is_57_run(n), ...)
    moat_ev = None
    # v5.7 step 7: every influence check together, on 5.7 runs only and before the first write — each lane calls
    # check_influence (L2) for its own reason fields here (tier_override_reason, base_override, misfit_notch_reason,
    # the moat reasons, the share-class reasons, ttm_rejection_reason)
    if is_57_run(n):
        if notch and notch.get("reason_source") == "judgment":   # L1 (R1): misfit_notch_reason (R-3 / R-4 ran above)
            check_influence("misfit_notch_reason", notch["reason"], _facts.parse_refs(notch["reason"]), fc, folder, n)
        if plan and plan.get("reason"):
            pass   # R7: check_influence(TTM_REJECTION_KEY, plan["reason"], _facts.parse_refs(plan["reason"]), fc, ...)
        # L2 (R3, Andrew 2026-10-19; 02 §5): the tier override's reason and a plain base_override pin's reason +
        # source (the payable and iprd_amortized shapes are checked figure for figure elsewhere; rebase I13) — a hand
        # pin never traces to itself alone (base_pin_trace_only, review r05). misfit_notch_reason is L1's call (its
        # field, INFLUENCE_TAGS), made above.
        if override and (IPRD_HAND_OVERRIDE_TRACED or not iprd_override_required(n)):   # Q2 switch
            check_influence("tier_override_reason", j.get("tier_override_reason"),
                            _facts.parse_refs(j.get("tier_override_reason")), fc, folder, n)
        if (base_override_event_applies(j, n) and j_base_override
                and j_base_override.get("basis") not in (PAYABLE_BASIS, IPRD_AMORTIZED_BASIS)):
            _bo_text = " ".join(str(j_base_override.get(k) or "") for k in ("reason", "source"))
            check_influence("base_override", _bo_text, _facts.parse_refs(_bo_text), fc, folder, n,
                            trace_only=base_pin_trace_only(n, j_base_override), require_anchor=True)
    score.update({
        "engine_release": n.get("engine_release"),
        # [Codex review r12 of PR #47] the run this score was built from (its verified content_hash): reprice.py and
        # build_site show live figures only beside the run whose hash this is
        "dcf_content_hash": ch,
        "irr_bear": round(n["irr_bear"], 4) if isinstance(n.get("irr_bear"), (int, float)) else None,
        "irr_bull": round(n["irr_bull"], 4) if isinstance(n.get("irr_bull"), (int, float)) else None,
        "tier_bear": n.get("tier_bear"), "tier_bull": n.get("tier_bull"),
        "iv_at_20": round(n["iv_at_20"], 2) if isinstance(n.get("iv_at_20"), (int, float)) else None,
        "iv_at_25": round(n["iv_at_25"], 2) if isinstance(n.get("iv_at_25"), (int, float)) else None,
        "f_subtype": n.get("f_subtype"),
        "irr_at_floor": bool(diag.get("irr_at_floor")),
        "net_debt_latest": n.get("net_debt_latest"),
        "shares_diluted_latest": n.get("shares_diluted_latest"),
        "model_fit": model_fit,
    })
    # Alert eligibility (audit round-1: "alert only at medium+ confidence with
    # no data-gap flags" — S/A alerts had been firing on misfits and gaps).
    # Entries and exits get separate gates (see the module docstring).
    # v5.7 (L1): tier_final is misfit_notch's; the gates see a tier_override only while it is in force (a legacy
    # one-notch override is the notch, not a judgment lift)
    reasons, exit_reasons = alert_reasons(
        tier_final, n.get("tier_by_numbers"), override if override_in_force else None, conf, model_fit,
        bool(reported and impact and impact.get("unblocks_tier")) or pin_rescued(n), bool(diag.get("irr_at_floor")),
        stale_release=release_mismatch_reason(n.get("engine_release")) if release_mismatch else None,
        share_classes_raise=share_classes_raise_reason(sc_impact))   # v5.7 (L8): None in L0
    score["alert_eligible"] = tier_final in ("S", "A") and not reasons
    if reasons:
        score["alert_suppressed_reason"] = "; ".join(reasons)
    score["exit_alert_eligible"] = tier_final not in ("S", "A") and not exit_reasons
    if exit_reasons:
        score["exit_alert_suppressed_reason"] = "; ".join(exit_reasons)
    if j_second_pass:
        score["second_pass"] = j_second_pass
    if conf_capped:
        score["confidence_capped"] = True
    if notch:   # v5.7 (L1, R1): on every sector misfit, applied or not
        score["misfit_notch"] = notch
    if set_aside:   # v5.7 (L1, R1, Q1 (b)): a misfit universe sector the filer's SIC sets aside
        score["misfit_sector_set_aside"] = set_aside
    if override and override_in_force:   # v5.7 (L1): a legacy one-notch override's text is misfit_notch.reason
        score["tier_override_reason"] = j["tier_override_reason"]
    if j.get("moat_for"):
        score["moat_for"] = j["moat_for"]
    if j.get("moat_against"):
        score["moat_against"] = j["moat_against"]
    if moat_ev is not None:   # v5.7 (L3): score.json moat_evidence — never written in L0
        score["moat_evidence"] = moat_ev
    if reported:
        score["overrides"] = [dict({"field": f, "value": reported[f]["value"], "kind": reported[f]["kind"],
                                    "source": reported[f]["source"]},
                                   **({"scope": reported[f]["scope"]} if reported[f].get("scope") else {}))
                              for f in ("capex", "sbc", "shares") if f in reported]
        score["override_impact"] = impact
    if scope_corrected:
        score["in_scope_corrected_by_make_score"] = True
    _iprd = iprd_score_block(n)   # v5.6: only when the engine recorded the block
    if _iprd is not None:
        score["iprd_adjustment"] = _iprd
    # v5.7 step 8 (07 §1.12): the lanes' score.json blocks — none written in L0
    score_interim_fields(score, n, j, interim, interim_meas)        # L4 (R2)
    score_share_classes_fields(score, n, j_sc, sc_impact)           # L8 (R6)
    if base_alts is not None:                                        # R7
        score["base_alternatives"] = base_alts
    nd_ads = ads_net_debt_basis(n)  # [ADDITION — M1] pre-5.5 ADS record: the ratio on the ADS basis
    if nd_ads is not None:
        score["net_debt_to_normalized_oe_ads_basis"] = round(nd_ads["ads_basis"], 4)
    # v5.7 step 8 (L2): the stamps that describe this score (declared_facts, method_runs, previous_score,
    # key_numbers_sha256) go here, then key_numbers.md is built as one text — before the write phase, so nothing
    # below can fail between the registry and the last write. (L0: the same text the old in-place writer produced.)
    previous = previous_score_summary(prior_score, n)               # L2
    if fc is not None:                                               # L2 (R3, 02 §8.3)
        score["declared_facts"] = fc.summary()
    if runs:
        score["method_runs"] = [r["summary"] for r in runs]
    if previous:
        score["previous_score"] = previous
    kn_text = build_key_numbers(folder, n, j, score, reported, impact, ads_corr=ads_corr, facts_check=fc,
                                method_runs=runs, previous=previous, interim=interim, instance=instance)
    # L2 (R3; rebase A5): what make_score writes as key_numbers.md (LF; check_quotes I2 normalizes a CRLF checkout)
    score["key_numbers_sha256"] = hashlib.sha256(kn_text.encode("utf-8")).hexdigest()
    # Every refusal and every measurement (override and payable impact) is
    # behind us. [Codex review r19 of PR #47] The write phase is ONE registry
    # transaction: under the registry lock the prior registry is re-read, the
    # deals' deferred-payment lifetime re-validated and merged against it (a
    # scorer that overlapped this one may have recorded a period since the
    # pre-check), and only then come the writes. [Codex review r21 of PR #47]
    # The registry FIRST, then the scope rewrite, score.json and key_numbers.md
    # (each tmp + replace): a crash after the registry leaves the deals'
    # periods recorded beside the previous, stale score.json (no live figures
    # for it, and a rerun deleting a declaration is refused); a crash before
    # it leaves nothing changed. score.json had come first, so a crash between
    # the two published a score whose deferred periods were never recorded.
    with registry_transaction():
        deferred_events = iprd_deferred_lifetime(ticker, _deferred, registry_prior_entries(ticker))
        # Every run: the ticker's registry entries are replaced wholesale and
        # re-derived from THIS run (applied overrides + judgment-call events).
        scope_event = ({"old_cap": ads_corr["old_cap"], "new_cap": ads_corr["cap"], "in_scope": bool(scope_val)}
                       if scope_corrected else None)
        update_registry(ticker, reported, j_over, impact, j, n, scope_event=scope_event, payable_impact=payable_impact,
                        amortized_impact=amortized_impact, deferred_events=deferred_events, lock_held=True,
                        # v5.7: the lanes' registry inputs (each None in L0: no event)
                        notch=notch, override_in_force=override_in_force, facts_check=fc, moat_ev=moat_ev,
                        interim=interim, declined=declined, share_classes=sc_impact, up_c=None, unlisted_acks=None,
                        base_alts=base_alts)
        if scope_rewrite is not None:
            rewrite_judgment_scope(jpath, scope_rewrite)
            print(f"make_score.py: {ticker} judgment.json in_scope_under_40b {j['in_scope_under_40b']} -> {scope_rewrite} "
                  f"(ADS-corrected market cap {_usd(mktcap)} = price × shares ÷ {ads_corr['ratio']:g}; "
                  f"the pre-5.5 engine printed {_usd(ads_corr['old_cap'])})")
            j["in_scope_under_40b"] = scope_rewrite
        write_score_json(spath, score)
        write_key_numbers_text(folder, kn_text)   # v5.7 (L0): built above, written last
    print(f"make_score.py: wrote {spath} — tier {score['tier_final']}, weighted IRR {score['implied_irr']}, IV@15 {score['iv_at_15']}")


if __name__ == "__main__":
    main()
